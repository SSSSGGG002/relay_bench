#!/usr/bin/env python3
"""Cross-channel prefix-cache probe: Zhipu's implicit cache appears to be GLOBAL (shared across accounts).
If a relay's FIRST call with a brand-new prefix reports cached_tokens>0 right after the same prefix was sent ONCE
through the official API, the relay's upstream is the same Zhipu backend (strong proof of an official upstream).
  python3 xcache.py --official URL:KEY --relay LABEL=URL:KEY [--relay ...] [--model glm-5.3-flash]
"""
import argparse, json, random, time, httpx
def prefix(seed, n=5200):
    rng = random.Random(seed); words = "river stone cloud bright silver window garden yellow purple forest castle meadow ocean quiet thunder velvet copper marble candle orbit".split()
    out = []
    while sum(len(x) for x in out) < n * 4: out.append(" ".join(rng.choice(words) for _ in range(12)) + f" [{rng.randint(1000,9999)}].")
    return " ".join(out)
NO_EFFORT = False
def call(base, key, model, sysm, i):
    base = base.rstrip("/"); path = "/chat/completions" if base.endswith("/v4") else "/v1/chat/completions"
    t0 = time.time()
    body = {"model": model, "max_tokens": 64, "messages": [{"role": "system", "content": sysm}, {"role": "user", "content": f"probe {i}. Reply with exactly: OK"}]}
    if not NO_EFFORT: body["reasoning_effort"] = "low"
    r = httpx.post(base + path, headers={"authorization": f"Bearer {key}"}, json=body, timeout=120)
    try: u = r.json().get("usage", {})
    except Exception: u = {}
    return dict(status=r.status_code, prompt=u.get("prompt_tokens"), cached=(u.get("prompt_tokens_details") or {}).get("cached_tokens"), t=round(time.time() - t0, 2))
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--official", required=True); ap.add_argument("--relay", action="append", default=[]); ap.add_argument("--model", default="glm-5.3-flash"); ap.add_argument("--no-effort", action="store_true", help="omit reasoning_effort (some relays 400 on it)")
    a = ap.parse_args(); ob, ok = a.official.rsplit(":", 1)
    global NO_EFFORT; NO_EFFORT = a.no_effort
    relays = []
    for r in a.relay:
        lab, rest = r.split("=", 1); b, k = rest.rsplit(":", 1); relays.append((lab, b, k))
    res = {}
    seed = int(time.time())
    print(f"seed={seed}")
    # A: official self-hit sanity
    p = prefix(seed); a1 = call(ob, ok, a.model, p, 1); time.sleep(2); a2 = call(ob, ok, a.model, p, 2)
    print(f"[A] official new prefix: call1 {a1} -> call2 {a2}  (expect cached 0 then >0)"); res["A_official_self"] = [a1, a2]
    # B: official first, then each relay ONCE with the same brand-new prefix
    for lab, b, k in relays:
        p = prefix(seed + hash(lab) % 100000); o = call(ob, ok, a.model, p, 1); time.sleep(2); r1 = call(b, k, a.model, p, 2)
        same = (r1.get("cached") or 0) > 1000
        print(f"[B] official->{lab}: official {o} -> relay first call {r1}  => {'SAME BACKEND (relay hit a cache only the official call could have written)' if same else 'no cross hit (different backend, or cache is per-account)'}")
        res[f"B_official_to_{lab}"] = [o, r1, same]
    # C: relay first, then official once (does the relay's upstream write into the same cache?)
    for lab, b, k in relays:
        p = prefix(seed + 7 * (hash(lab) % 100000) + 3); r1 = call(b, k, a.model, p, 1); time.sleep(2); o = call(ob, ok, a.model, p, 2)
        same = (o.get("cached") or 0) > 1000
        print(f"[C] {lab}->official: relay {r1} -> official first call {o}  => {'SAME BACKEND' if same else 'no cross hit'}")
        res[f"C_{lab}_to_official"] = [r1, o, same]
    # D: relay self-hit (its own second call)
    for lab, b, k in relays:
        p = prefix(seed + 11 * (hash(lab) % 100000) + 5); r1 = call(b, k, a.model, p, 1); time.sleep(2); r2 = call(b, k, a.model, p, 2)
        print(f"[D] {lab} self: {r1} -> {r2}  (expect 0 then >0 if the relay's upstream caches and does not rotate accounts)")
        res[f"D_{lab}_self"] = [r1, r2]
    import os; prev = json.load(open("results/xcache.json")) if os.path.exists("results/xcache.json") else {}; prev.update(res); json.dump(prev, open("results/xcache.json", "w"), indent=1)
main()
