#!/usr/bin/env python3
"""Drift check for a frozen reference relay (suite/reference/<name>.json).

A reference relay is a station whose full results were measured once and frozen, so
new stations can be compared against it without re-running the whole suite on it.
Before reusing the frozen numbers, run this (~5-15 min, a few dozen calls):

    RB_KEY=sk-... python3 refcheck.py suite/reference/ikuncode-kiro.json [--direct] [--models claude-opus-5]

It checks, per model:
  1. fingerprint: "Reply with exactly: OK" x3 -> id format + usage shape/ranges must match
  2. knowledge:   one pope/PM probe must contain the frozen marker words
  3. drift IQ:    the frozen discriminating items (suite/iq.json) re-answered once each;
                  score may drop by at most `drift.max_drop` vs the frozen per-item results
and that suite/iq.json still has the md5 the reference was scored with.
Verdict SAME -> reuse frozen numbers; DRIFT -> re-baseline the reference before comparing.
Latency / stability / cache are NOT frozen as absolute truth: they depend on route and time,
so the reference stores them with route+date and new stations must be measured the same way.
"""
import argparse, concurrent.futures as cf, hashlib, json, os, re, sys, time
import httpx

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from bench import final_answer, match_answer  # noqa: E402

UA = "claude-cli/2.1.278 (external, cli)"
QUICK = False
GLITCH_MARKERS = ["上游模型未返回任何内容"]   # ikuncode replaces empty upstream replies with this assistant text


def client(base, key, direct, timeout=600):
    return httpx.Client(base_url=base, timeout=httpx.Timeout(timeout, connect=30), trust_env=not direct,
                        headers={"user-agent": UA, "x-api-key": key, "authorization": "Bearer " + key,
                                 "anthropic-version": "2023-06-01", "content-type": "application/json"})


def call(c, body, tries=3):
    for t in range(tries):
        try:
            r = c.post("/v1/messages", json=body)
            j = r.json() if r.headers.get("content-type", "").startswith("application/json") else None
            if r.status_code == 200 and j:
                if any(mk in text_of(j) for mk in GLITCH_MARKERS):   # relay swapped an empty upstream reply for a warning text
                    err = "relay glitch text"; time.sleep(3); continue
                return j
            err = f"HTTP {r.status_code} {r.text[:120]}"
        except Exception as e:
            err = f"{type(e).__name__}: {str(e)[:120]}"
        time.sleep(3)
    return {"_error": err}


def text_of(j): return "".join(b.get("text", "") for b in (j.get("content") or []) if b.get("type") == "text")


def check_model(c, model, ref, bank):
    out = {"model": model, "checks": [], "ok": True}
    def add(name, ok, detail):
        out["checks"].append(dict(name=name, ok=ok, detail=detail)); out["ok"] &= ok
        print(f"  [{'OK ' if ok else 'DRIFT'}] {model} {name}: {detail}", flush=True)
    fp = ref["fingerprint"]
    rows = [call(c, {"model": model, "max_tokens": 20, "messages": [{"role": "user", "content": "Reply with exactly: OK"}]}) for _ in range(3)]
    good = [j for j in rows if "_error" not in j]
    add("reachable", len(good) >= 2, f"{len(good)}/3 ok" + ("" if good else f" last={rows[-1].get('_error')}"))
    if good:
        ids_ok = all(re.fullmatch(fp["id_regex"], j.get("id") or "") for j in good)
        add("id_format", ids_ok, f"{[j.get('id') for j in good]} vs /{fp['id_regex']}/")
        keys = sorted((good[0].get("usage") or {}).keys())
        add("usage_keys", keys == sorted(fp["usage_keys"]), f"{keys}")
        for f, (lo, hi) in fp.get("usage_ranges", {}).items():
            vals = [(j.get("usage") or {}).get(f) for j in good]
            add(f"usage.{f}", all(isinstance(v, int) and lo <= v <= hi for v in vals), f"{vals} in [{lo},{hi}]")
    kn = ref["models"][model].get("knowledge_probe")
    if kn:
        # 3 best-guess answers: an older model names the old fact (must_not); a hedge is not evidence either way
        ts = []
        for _ in range(3):
            j = call(c, {"model": model, "max_tokens": 200, "messages": [{"role": "user", "content": kn["q"]}]})
            ts.append(text_of(j) if "_error" not in j else "")
        old = [t for t in ts if any(w.lower() in t.lower() for w in kn.get("must_not", []))]
        new = [t for t in ts if all(w.lower() in t.lower() for w in kn["must_contain"])]
        state = "older" if old else ("match" if new else "inconclusive")
        add("knowledge", not old, f"{state}: {len(new)}/3 contain {kn['must_contain']}, {len(old)}/3 contain {kn.get('must_not', [])} ; e.g. {(old or new or ts)[0][:110]!r}")
    if QUICK: return out
    frozen = ref["models"][model]["iq"]["per_item"]
    ids = [i for i in ref["drift"]["items"] if i in frozen]
    def one(iid):
        it = bank[iid]
        body = {"model": model, "max_tokens": 16000, "messages": [{"role": "user", "content": it["q"] + "\n\nThink it through carefully. Your final line must be exactly:\nANSWER: <your final answer>"}]}
        j = call(c, body)
        got = final_answer(text_of(j)) if "_error" not in j else None
        return iid, (got is not None and match_answer(got, it["ans"], it.get("kind"))), (got or j.get("_error", ""))[:40]
    with cf.ThreadPoolExecutor(3) as ex: res = list(ex.map(one, ids))
    now = sum(ok for _, ok, _ in res); then = sum(bool(frozen[i]) for i in ids)
    flips = [f"{i}:{'✓' if frozen[i] else '✗'}→{'✓' if ok else '✗'}({g})" for i, ok, g in res if ok != bool(frozen[i])]
    add("drift_iq", then - now <= ref["drift"]["max_drop"], f"now {now}/{len(ids)} vs frozen {then}/{len(ids)} ; flips {flips}")
    out["iq_now"] = {i: ok for i, ok, _ in res}
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ref"); ap.add_argument("--models", default=""); ap.add_argument("--direct", action="store_true", help="ignore HTTPS_PROXY")
    ap.add_argument("--quick", action="store_true", help="fingerprint + knowledge only (~1 min), skip the drift IQ items")
    a = ap.parse_args()
    global QUICK; QUICK = a.quick
    ref = json.load(open(a.ref))
    key = os.environ.get("RB_KEY") or sys.exit("set RB_KEY to the reference station's key")
    bank_path = os.path.join(HERE, ref["iq_bank"]["path"])
    md5 = hashlib.md5(open(bank_path, "rb").read()).hexdigest()
    if md5 != ref["iq_bank"]["md5"]:
        print(f"WARNING: {ref['iq_bank']['path']} md5 {md5} != frozen {ref['iq_bank']['md5']} -> IQ numbers are not comparable; use {ref['iq_bank'].get('pinned_copy')}")
        bank_path = os.path.join(HERE, ref["iq_bank"]["pinned_copy"])
    bank = {it["id"]: it for it in json.load(open(bank_path))["items"]}
    models = a.models.split(",") if a.models else list(ref["models"])
    print(f"refcheck {ref['name']} ({ref['base']}) frozen {ref['frozen_at']} models={models}")
    with client(ref["base"], key, a.direct) as c:
        results = [check_model(c, m, ref, bank) for m in models]
    verdict = ("SAME" if all(r["ok"] for r in results) else "DRIFT") + (" (quick: IQ not checked)" if QUICK else "")
    print(f"VERDICT {verdict}: " + ("reuse the frozen numbers" if verdict.startswith("SAME") else "re-baseline the reference before using it"))
    os.makedirs(os.path.join(HERE, "results", "refcheck"), exist_ok=True)
    fn = os.path.join(HERE, "results", "refcheck", f"{ref['name']}-{time.strftime('%Y%m%d-%H%M')}.json")
    json.dump(dict(ref=a.ref, at=time.strftime("%Y-%m-%d %H:%M:%S"), verdict=verdict, results=results), open(fn, "w"), ensure_ascii=False, indent=1)
    print("saved", fn)


if __name__ == "__main__":
    main()
