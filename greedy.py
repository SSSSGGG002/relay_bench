#!/usr/bin/env python3
"""greedy.py — 量化/部署差异探测：贪心解码分歧点 + 精度敏感题 + 200k 多针召回。
  python3 greedy.py --official URL:KEY --ch label=[anthropic@]URL:KEY ... [--n 12] [--reps 3]
所有通道用 do_sample=false / temperature 0 跑同一组提示词；以官方 3 次输出中的"众数"为参照，
记录每个通道每次输出与官方参照的首个分歧 token 位置（tiktoken o200k 切分）与整体一致率。
输出 results/greedy/<label>.json 与 GREEDY.md
"""
import argparse, json, os, random, statistics, time, datetime, concurrent.futures as cf
import bench
from bench import Channel, msg, text_of, tok, filler, _extract_json
try:
    import tiktoken; ENC = tiktoken.get_encoding("o200k_base")
except Exception: ENC = None
HERE = os.path.dirname(os.path.abspath(__file__))
PROMPTS = [
 "Continue this text for about 150 words, no commentary: 'It was the best of times, it was the worst of times, it was the age of wisdom, it was the age of foolishness,'",
 "Write a 150-word plain-prose description of how a refrigerator works.",
 "Explain in about 150 words why the sky is blue.",
 "List the first 40 prime numbers separated by commas, nothing else.",
 "Write a Python function that returns the n-th Fibonacci number iteratively, with a docstring. Code only.",
 "Translate into Chinese: 'The committee postponed the decision until further evidence could be gathered from the regional offices.'",
 "Summarize the plot of Romeo and Juliet in exactly five sentences.",
 "Give step-by-step instructions (about 120 words) for making a cup of pour-over coffee.",
 "Write a haiku sequence of four haiku about autumn.",
 "Describe the water cycle in about 120 words for a ten-year-old.",
 "Write a SQL query that returns the top 3 customers by total order amount from tables customers(id,name) and orders(id,customer_id,amount), then explain it in two sentences.",
 "Write 120 words about the history of the bicycle.",
]
PRECISION = [  # (prompt, answer) — computed here, exact numeric answers, thinking OFF
 ("Compute 8734921 × 6091837. Reply with only the number.", str(8734921 * 6091837)),
 ("Compute 99887766 × 55443322. Reply with only the number.", str(99887766 * 55443322)),
 ("Compute 123456789 × 987654321. Reply with only the number.", str(123456789 * 987654321)),
 ("Compute 7919 × 7907 × 7901. Reply with only the number.", str(7919 * 7907 * 7901)),
 ("What is 2 to the power of 61? Reply with only the number.", str(2 ** 61)),
 ("What is 3 to the power of 40? Reply with only the number.", str(3 ** 40)),
 ("Compute the sum of the squares of the integers from 1 to 250. Reply with only the number.", str(sum(i * i for i in range(1, 251)))),
 ("Compute 1234567 squared. Reply with only the number.", str(1234567 ** 2)),
 ("What is 1/7 to 40 decimal places? Reply with only the decimal.", "0." + str(10**40 // 7).zfill(40)),
 ("Compute 4567891234 divided by 7 (integer division) and the remainder. Reply as 'quotient remainder'.", f"{4567891234 // 7} {4567891234 % 7}"),
]
def toks(s): return ENC.encode(s) if ENC else list(s)
def first_div(a, b):
    ta, tb = toks(a), toks(b); n = min(len(ta), len(tb))
    for i in range(n):
        if ta[i] != tb[i]: return i, max(len(ta), len(tb))
    return (n if len(ta) != len(tb) else -1), max(len(ta), len(tb))  # -1 = identical
def greedy_extra(c):
    return {"temperature": 0, "top_p": 1} if c.dialect == "anthropic" else {"do_sample": False, "temperature": 0, "top_p": 1}
def run_prompt(c, p, reps, max_tokens=700):
    outs = []
    for _ in range(reps):
        r = msg(c, p, max_tokens=max_tokens, think="off", extra=greedy_extra(c), timeout=300)
        outs.append(text_of(r) if r["ok"] else f"<ERR {r['status']}>"); time.sleep(0.5)
    return outs
def mode(xs):
    return max(set(xs), key=lambda x: (xs.count(x), -len(x)))
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--official", required=True); ap.add_argument("--ch", action="append", default=[]); ap.add_argument("--model", default="glm-5.3-flash")
    ap.add_argument("--n", type=int, default=12); ap.add_argument("--reps", type=int, default=4); ap.add_argument("--only", default="greedy,precision,needle")
    a = ap.parse_args(); ob, ok = a.official.rsplit(":", 1)
    off = Channel(ob, ok, "openai", a.model); off.label = "zhipu-official"
    chans = []
    for s in a.ch:
        label, rest = s.split("=", 1); d = "openai"
        if rest.startswith("anthropic@"): d = "anthropic"; rest = rest[len("anthropic@"):]
        b, k = rest.rsplit(":", 1); c = Channel(b, k, d, a.model); c.label = label; chans.append(c)
    allc = [off] + chans; groups = a.only.split(","); res = {c.label: dict(label=c.label, dialect=c.dialect) for c in allc}
    log = lambda s: print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {s}", flush=True)
    if "greedy" in groups:
        P = PROMPTS[:a.n]
        with cf.ThreadPoolExecutor(max_workers=4) as ex:
            outs = {c.label: list(ex.map(lambda p, c=c: run_prompt(c, p, a.reps), P)) for c in allc}
        # pairwise matched-prefix fraction: every sample of a channel vs every OFFICIAL sample (same prompt); official vs itself = natural nondeterminism floor
        def mpf(a, b):
            d, L = first_div(a, b); return 1.0 if d == -1 else d / max(L, 1)
        for c in allc:
            rows = []; cross = []; within = []
            for i, p in enumerate(P):
                mine = outs[c.label][i]; theirs = outs[off.label][i]
                for j, o in enumerate(mine):
                    vs = [mpf(o, t) for k, t in enumerate(theirs) if not (c is off and k == j)]
                    rows.append(dict(prompt=i, rep=j, matched_frac_vs_official=round(statistics.mean(vs), 3) if vs else None, max_matched=round(max(vs), 3) if vs else None, head=o[:80]))
                    cross += vs
                for x in range(len(mine)):
                    for y in range(x + 1, len(mine)): within.append(mpf(mine[x], mine[y]))
            res[c.label]["greedy"] = dict(rows=rows, n=len(rows), mean_matched_frac_vs_official=round(statistics.mean(cross), 3), median_matched_frac_vs_official=round(statistics.median(cross), 3), self_mean_matched_frac=round(statistics.mean(within), 3) if within else None, identical_pairs_vs_official=sum(1 for v in cross if v == 1.0), pairs=len(cross))
            g = res[c.label]["greedy"]; log(f"greedy {c.label}: matched-prefix vs official mean={g['mean_matched_frac_vs_official']} median={g['median_matched_frac_vs_official']} identical pairs {g['identical_pairs_vs_official']}/{g['pairs']} ; self-consistency {g['self_mean_matched_frac']}")
    if "precision" in groups:
        for c in allc:
            rows = []
            for p, ans in PRECISION:
                got = [text_of(msg(c, p, max_tokens=200, think="off", extra=greedy_extra(c), timeout=200)) for _ in range(2)]
                okc = sum(1 for g in got if bench.match_answer(g, ans)); rows.append(dict(q=p[:50], expected=ans, got=[g[:60] for g in got], correct=okc))
            tot = sum(r["correct"] for r in rows); res[c.label]["precision"] = dict(rows=rows, correct=tot, total=2 * len(PRECISION))
            log(f"precision {c.label}: {tot}/{2*len(PRECISION)} :: " + " ".join(f"{r['correct']}" for r in rows))
    if "needle" in groups:
        names = ["Kestrel", "Marlin", "Osprey", "Falcon", "Heron", "Ibis", "Jay", "Kite", "Lark", "Merlin"]
        rng = random.Random(4242); codes = [f"{rng.randint(1000,9999)}-{''.join(rng.choice('ABCDEFGHJKLMNPQRSTUVWXYZ') for _ in range(2))}" for _ in names]
        paras = filler(200000, seed=200200); L = len(paras)
        for k, (nm, code) in enumerate(zip(names, codes)): paras.insert(int(L * (0.05 + 0.1 * k)), f"NOTE: the access code for project {nm} is {code}.")
        doc = "\n\n".join(paras); q = f"<document>\n{doc}\n</document>\n\nExtract the access codes for projects {', '.join(names)}. Reply with only JSON mapping project name to code (null if absent)."
        for c in allc:
            r = msg(c, q, max_tokens=600, think="off", timeout=900); t = text_of(r)
            try: j = json.loads(_extract_json(t)); found = sum(1 for nm, cd in zip(names, codes) if str(j.get(nm, "")).strip() == cd)
            except Exception: found = sum(1 for cd in codes if cd in t)
            res[c.label]["needle200k"] = dict(found=found, total=len(names), latency=round(r["latency"], 1), input=r["usage"]["input"], status=r["status"], reply=t[:200])
            log(f"needle200k {c.label}: {found}/{len(names)} in {r['latency']:.1f}s input={r['usage']['input']} status={r['status']}")
    os.makedirs(os.path.join(HERE, "results", "greedy"), exist_ok=True)
    for l, r in res.items(): json.dump(r, open(os.path.join(HERE, "results", "greedy", l + ".json"), "w"), indent=1, ensure_ascii=False)
    out = ["# 量化/部署差异探测（贪心分歧 / 精度题 / 200k 十针）\n", f"{datetime.datetime.now().isoformat(timespec='minutes')}；do_sample=false/temperature=0。指标 = 每个样本与官方各样本的'匹配前缀占比'(首个分歧 token 位置 / 总长)。官方 vs 官方那一行是同一部署的自然非确定性下限（智谱官方贪心解码本身 3 次输出也在十几个 token 内分岔，MoE 批处理所致）；某通道明显低于该下限才算不同部署/量化。\n",
           "| 通道 | 协议 | 与官方样本逐字相同的配对 | 匹配前缀占比 均值/中位 | 自身一致性 | 精度题(关思考) | 200k 十针 | 200k 耗时 |", "|---|---|---|---|---|---|---|---|"]
    for l, r in res.items():
        g = r.get("greedy", {}); p = r.get("precision", {}); nd = r.get("needle200k", {})
        out.append(f"| {l} | {r['dialect']} | {g.get('identical_pairs_vs_official','-')}/{g.get('pairs','-')} | {g.get('mean_matched_frac_vs_official','-')}/{g.get('median_matched_frac_vs_official','-')} | {g.get('self_mean_matched_frac','-')} | {p.get('correct','-')}/{p.get('total','-')} | {nd.get('found','-')}/{nd.get('total','-')} | {nd.get('latency','-')}s |")
    out.append("\n读法：官方自己的行给出'同一部署的自然波动'（MoE 批处理会带来少量非确定性）。某通道的相同率/匹配前缀占比明显低于官方自身、且精度题错误更多，才是量化/不同部署的证据；只是略低属于噪声。\n")
    txt = "\n".join(out); open(os.path.join(HERE, "GREEDY.md"), "w").write(txt); print(txt)
if __name__ == "__main__": main()
