#!/usr/bin/env python3
"""Build golden knowledge baselines for OFFICIAL models through the Claude subscription (`claude -p`, api.anthropic.com).
Usage: python3 golden.py claude-opus-5 [claude-sonnet-5 ...]   -> suite/golden/<model>.json
Runs the same ladder + recency + pool-mix questions as bench.py's knowledge group and classifies with the same rules,
so report.py can compare a relay's answers item-by-item against the genuine model instead of against a nominal cutoff date."""
import json, os, re, subprocess, sys, concurrent.futures as cf
HERE = os.path.dirname(os.path.abspath(__file__)); SUITE = os.path.join(HERE, "suite")
sys.path.insert(0, HERE); from bench import UNKNOWN_RE  # same classifier
K = json.load(open(os.path.join(SUITE, "knowledge.json")))
SYS_LADDER = "You are a factual assistant answering from your own training knowledge. If you have knowledge of the event, answer it directly in at most 15 words (a best recollection is fine). Only if you have no knowledge of the event at all, reply exactly UNKNOWN."
SYS_RECENT = "Answer from your own training knowledge as of your knowledge cutoff. Give your single best answer in at most 20 words. Do not answer UNKNOWN; if unsure, give the most recent one you know."
def ask(model, system, q):
    env = {k: v for k, v in os.environ.items() if k not in ("ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_API_KEY")}
    env["ANTHROPIC_BASE_URL"] = "https://api.anthropic.com"
    cmd = ["claude", "-p", "--model", model, "--output-format", "json", "--settings", '{"env":{"ANTHROPIC_BASE_URL":"https://api.anthropic.com","ANTHROPIC_AUTH_TOKEN":""}}', "--append-system-prompt", system, q]
    for attempt in range(3):
        try:
            out = subprocess.run(cmd, capture_output=True, text=True, timeout=300, env=env, stdin=subprocess.DEVNULL, cwd="/tmp").stdout
            j = json.loads(out[out.index("{"):])
            if not j.get("is_error"): return str(j.get("result") or "")
        except Exception as e:
            err = str(e)
    return ""
def run(model):
    rows = []
    for it in K["items"]:
        t = ask(model, SYS_LADDER, it["q"])
        cls = "CORRECT" if any(re.search(p, t, re.I) for p in it["accept"]) else ("UNKNOWN" if (UNKNOWN_RE.search(t) or t.strip().upper() == "UNKNOWN" or not t) else "WRONG")
        rows.append(dict(id=it["id"], date=it["date"], control=it.get("control", False), cls=cls, answer=t[:120])); print(f"  {model} {it['id']} {cls:8s} {t[:60]!r}", flush=True)
    rec = []
    for it in K.get("recency", []):
        t = ask(model, SYS_RECENT, it["q"]); era = None
        for d, pat in it["eras"]:
            if re.search(pat, t, re.I): era = d; break
        rec.append(dict(id=it["id"], answer=t[:120], era=era)); print(f"  {model} {it['id']} era={era} {t[:60]!r}", flush=True)
    pope = next((it for it in K.get("recency", []) if it["id"] == "C1"), None); mix = []
    if pope:
        for _ in range(3):
            t = ask(model, SYS_RECENT, pope["q"]); era = next((d for d, pat in pope["eras"] if re.search(pat, t, re.I)), None); mix.append(era)
    correct = [r["date"] for r in rows if r["cls"] == "CORRECT" and not r["control"]]
    eras = [r["era"] for r in rec if r["era"]]
    res = dict(model=model, source="official api via claude -p (subscription); Claude Code base system prompt present", ladder=rows, recency=rec, pool_mix=mix,
               ladder_frontier=max(correct) if correct else None, recency_frontier=max(eras) if eras else None)
    json.dump(res, open(os.path.join(SUITE, "golden", model + ".json"), "w"), indent=1, ensure_ascii=False)
    print(f"== {model}: ladder_frontier={res['ladder_frontier']} recency_frontier={res['recency_frontier']} pool_mix={mix} correct={len(correct)}", flush=True)
if __name__ == "__main__":
    models = sys.argv[1:] or ["claude-opus-5", "claude-sonnet-5", "claude-fable-5-1"]
    with cf.ThreadPoolExecutor(len(models)) as ex: list(ex.map(run, models))
