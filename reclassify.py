#!/usr/bin/env python3
"""Re-classify stored knowledge answers (results/*/*.json and suite/golden/*.json) with the current suite/knowledge.json patterns."""
import glob, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from bench import UNKNOWN_RE
K = json.load(open(os.path.join(HERE, "suite", "knowledge.json")))
items = {it["id"]: it for it in K["items"]}; rec = {it["id"]: it for it in K.get("recency", [])}
def cls_of(it, t):
    if any(re.search(p, t, re.I) for p in it["accept"]): return "CORRECT"
    if UNKNOWN_RE.search(t) or t.strip().upper() == "UNKNOWN" or not t: return "UNKNOWN"
    return "WRONG"
def era_of(it, t):
    for d, pat in it["eras"]:
        if re.search(pat, t, re.I): return d
    return None
changed = 0
for p in glob.glob(os.path.join(HERE, "results", "*", "*.json")) + glob.glob(os.path.join(HERE, "suite", "golden", "*.json")):
    d = json.load(open(p)); dirty = False
    ladder = d.get("ladder") if "ladder" in d else d.get("extra", {}).get("knowledge")
    if ladder:
        for r in ladder:
            if r["id"] in items and r.get("answer") is not None:
                c = cls_of(items[r["id"]], r["answer"]); 
                if c != r["cls"]: r["cls"] = c; dirty = True; changed += 1
        correct = [r["date"] for r in ladder if r["cls"] == "CORRECT" and not r.get("control")]
        if "ladder" in d: d["ladder_frontier"] = max(correct) if correct else None
        else: d["metrics"]["knowledge_frontier"] = max(correct) if correct else None
    recency = d.get("recency") if "ladder" in d else d.get("extra", {}).get("recency")
    if recency:
        for r in recency:
            if r["id"] in rec and r.get("answer") is not None:
                e = era_of(rec[r["id"]], r["answer"])
                if e != r.get("era"): r["era"] = e; dirty = True; changed += 1
        eras = [r["era"] for r in recency if r.get("era")]
        if "ladder" in d: d["recency_frontier"] = max(eras) if eras else None
        else: d["metrics"]["recency_frontier"] = max(eras) if eras else None
    if dirty: json.dump(d, open(p, "w"), indent=1, ensure_ascii=False)
print("reclassified rows changed:", changed)
