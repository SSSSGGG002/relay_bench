#!/usr/bin/env python3
"""ops.py — 运营指标专项：缓存 / 速度 / 稳定性，多站点同一时间窗口交错采样。

  python3 ops.py --ch official=https://open.bigmodel.cn/api/paas/v4:KEY --ch v129-K1=https://api.v129.site:KEY \
                 --ch rtoc-anth=anthropic@https://api.rtoc.cc:KEY [--model glm-5.3-flash] [--rounds 30] [--ttl 60,180,300,600]
输出 results/ops/<label>.json 与 OPS.md
"""
import argparse, concurrent.futures as cf, json, os, random, statistics, threading, time, datetime
import bench
from bench import Channel, msg, text_of, tok, filler
HERE = os.path.dirname(os.path.abspath(__file__))

def pct(xs, p):
    if not xs: return None
    xs = sorted(xs); k = (len(xs) - 1) * p; f = int(k); c = min(f + 1, len(xs) - 1)
    return round(xs[f] + (xs[c] - xs[f]) * (k - f), 2)

class Ops:
    def __init__(self, chans, model, rounds, ttl):
        self.chans = chans; self.model = model; self.rounds = rounds; self.ttl = ttl
        self.res = {c.label: dict(label=c.label, base=c.base, dialect=c.dialect, model=model) for c in chans}
        self.lock = threading.Lock(); self.threads = []
    def log(self, s): print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {s}", flush=True)

    # ---- A: interleaved short-call latency & stability
    def a_latency(self):
        rows = {c.label: [] for c in self.chans}
        for r in range(self.rounds):
            for c in self.chans:
                x = msg(c, "Reply with exactly: OK", max_tokens=48, think="off")
                rows[c.label].append(dict(t=round(x["latency"], 2), st=x["status"], empty=bool(x["ok"] and not text_of(x)), err=((x["error"] or {}).get("code") or (x["error"] or {}).get("message", "")[:60]) if x["error"] else None, variant=x["variant"], ts=round(x["t0"], 1)))
            if r % 5 == 4: self.log(f"A round {r+1}/{self.rounds}: " + " | ".join(f"{l}: p50={pct([y['t'] for y in v if y['st']==200],0.5)} err={sum(1 for y in v if y['st']!=200)}" for l, v in rows.items()))
        for l, v in rows.items():
            ok = [y["t"] for y in v if y["st"] == 200]
            self.res[l]["latency"] = dict(n=len(v), ok=len(ok), errors=len(v) - len(ok), empty=sum(1 for y in v if y["empty"]), p50=pct(ok, .5), p90=pct(ok, .9), p95=pct(ok, .95), max=max(ok) if ok else None, min=min(ok) if ok else None, mean=round(statistics.mean(ok), 2) if ok else None, stdev=round(statistics.pstdev(ok), 2) if len(ok) > 1 else None, error_codes=sorted({str(y["err"]) for y in v if y["err"]}), rows=v)

    # ---- B: interleaved streaming throughput (effort low) + C: real-world default-effort TTFT
    def b_speed(self, n=5):
        rows = {c.label: [] for c in self.chans}; rows_c = {c.label: [] for c in self.chans}
        prompts = ["Write a 300-word story about a lighthouse keeper. Plain prose.", "Write a 300-word story about a desert caravan. Plain prose.", "Write a 300-word story about a night train. Plain prose.", "Write a 300-word story about a mountain village. Plain prose.", "Write a 300-word story about a fishing boat. Plain prose."]
        code_q = "Write a Python function that parses an ISO-8601 duration string (e.g. P3DT4H5M) into total seconds, with 5 unit tests. Code only."
        for i in range(n):
            for c in self.chans:
                x = msg(c, prompts[i % len(prompts)], max_tokens=8000, think="off", stream=True, timeout=600)
                rows[c.label].append(self._speed_row(x))
                if i < 3:
                    y = msg(c, code_q, max_tokens=12000, think="default", stream=True, timeout=900)
                    rows_c[c.label].append(self._speed_row(y))
            self.log(f"B/C sample {i+1}/{n}: " + " | ".join(f"{l}: {v[-1]['tps']}tok/s ttft={v[-1]['ttft']}" for l, v in rows.items()))
        for l in rows:
            v = [r for r in rows[l] if r["tps"]]; w = [r for r in rows_c[l] if r["ok"]]
            self.res[l]["speed_low_effort"] = dict(samples=rows[l], n_ok=len(v), tps_p50=pct([r["tps"] for r in v], .5), tps_min=min((r["tps"] for r in v), default=None), tps_max=max((r["tps"] for r in v), default=None), ttft_p50=pct([r["ttft"] for r in v if r["ttft"]], .5), ttfb_p50=pct([r["ttfb"] for r in v if r["ttfb"]], .5), total_p50=pct([r["total"] for r in v], .5), chunk_tok_p50=pct([r["tok_per_chunk"] for r in v if r["tok_per_chunk"]], .5))
            self.res[l]["speed_default_effort"] = dict(samples=rows_c[l], n_ok=len(w), ttfb_p50=pct([r["ttfb"] for r in w if r["ttfb"]], .5), ttft_text_p50=pct([r["ttft"] for r in w if r["ttft"]], .5), total_p50=pct([r["total"] for r in w], .5), reasoning_tokens_p50=pct([r["reasoning"] for r in w if r["reasoning"] is not None], .5), out_tokens_p50=pct([r["out"] for r in w if r["out"]], .5), tps_p50=pct([r["tps"] for r in w if r["tps"]], .5))
    def _speed_row(self, x):
        t = text_of(x); est = tok(t); gen = (x["t_last"] - x["t_first_text"]) if (x["t_last"] and x["t_first_text"]) else None
        return dict(ok=bool(x["ok"] and t), st=x["status"], ttfb=round(x["ttfb"], 2) if x["ttfb"] else None, ttft=round(x["t_first_text"] - x["t0"], 2) if (x["t_first_text"] and x["t0"]) else None, total=round(x["latency"], 1), est=est, out=x["usage"]["output"], reasoning=x["usage"]["reasoning"], tps=round(est / gen, 1) if (gen and gen > 0.2 and est > 30) else None, chunks=x["chunks"], tok_per_chunk=round(est / x["chunks"], 1) if x["chunks"] else None, stop=x["stop"], variant=x["variant"], err=(x["error"] or {}).get("message", "")[:80] if x["error"] else None)

    # ---- D: concurrency bursts
    def d_burst(self, sizes=(8, 16)):
        for c in self.chans:
            out = {}
            for n in sizes:
                def one(_):
                    x = msg(c, "Reply with exactly: OK", max_tokens=48, think="off"); return dict(st=x["status"], t=round(x["latency"], 2), err=((x["error"] or {}).get("code") or (x["error"] or {}).get("message", "")[:60]) if x["error"] else None, empty=bool(x["ok"] and not text_of(x)))
                t0 = time.time()
                with cf.ThreadPoolExecutor(max_workers=n) as ex: rows = list(ex.map(one, range(n)))
                wall = round(time.time() - t0, 2); ok = [r["t"] for r in rows if r["st"] == 200]
                out[f"burst{n}"] = dict(n=n, errors=n - len(ok), empty=sum(1 for r in rows if r["empty"]), p50=pct(ok, .5), p90=pct(ok, .9), max=max(ok) if ok else None, wall=wall, req_per_s=round(len(ok) / wall, 2) if wall else None, error_codes=sorted({str(r["err"]) for r in rows if r["err"]}), rows=rows)
                self.log(f"D {c.label} burst{n}: errors={out[f'burst{n}']['errors']} p50={out[f'burst{n}']['p50']} max={out[f'burst{n}']['max']} wall={wall}s codes={out[f'burst{n}']['error_codes']}")
                time.sleep(3)
            self.res[c.label]["burst"] = out

    # ---- E: cache — hit on repeat (20k prefix), TTFT benefit, TTL, multi-turn prefix growth
    def e_cache(self):
        for c in self.chans:
            seed = int(time.time() * 1000) % 10**9 + hash(c.label) % 1000
            big = " ".join(filler(20000, seed=seed)); small = " ".join(filler(6000, seed=seed + 1))
            def probe(sysm, i, stream=True, hist=None, user=None):
                x = msg(c, user or f"Probe {i}. Reply with exactly: OK", system=sysm, history=hist, max_tokens=48, think="off", stream=stream, timeout=600)
                return dict(st=x["status"], input=x["usage"]["input"], cached=x["usage"]["cache_read"], write=x["usage"]["cache_write"], ttft=round(x["t_first_text"] - x["t0"], 2) if (x["t_first_text"] and x["t0"]) else None, ttfb=round(x["ttfb"], 2) if x["ttfb"] else None, total=round(x["latency"], 2), at=round(time.time(), 1), text=text_of(x)[:20])
            r1 = probe(big, 1); time.sleep(8); r2 = probe(big, 2); time.sleep(8); r3 = probe(big, 3)
            hitrow = r2 if (r2["cached"] or 0) > 1000 else r3; hit = (hitrow["cached"] or 0) > 1000
            cache = dict(prefix_tokens=tok(big), calls=[r1, r2, r3], hit_on_repeat=hit, hit_on_call=(2 if hitrow is r2 else 3) if hit else None, hit_ratio=(round((hitrow["cached"] or 0) / ((hitrow["input"] or 0) + (hitrow["cached"] or 0) if c.dialect == "anthropic" else (hitrow["input"] or 1)), 3) if (hitrow["input"] or hitrow["cached"]) else None), ttft_uncached=r1["ttft"], ttft_cached=hitrow["ttft"], ttft_gain_pct=round((1 - hitrow["ttft"] / r1["ttft"]) * 100) if (r1["ttft"] and hitrow["ttft"]) else None, total_uncached=r1["total"], total_cached=hitrow["total"])
            self.log(f"E {c.label} 20k prefix: miss {r1['cached']}/{r1['input']} ttft={r1['ttft']} -> hit {r2['cached']}/{r2['input']} ttft={r2['ttft']} -> {r3['cached']} ; TTFT gain {cache['ttft_gain_pct']}%")
            # multi-turn growth: prefix + turn1 -> prefix + turn1 + reply + turn2 ; cached should cover the whole earlier conversation
            h1 = probe(small, 1, user="Turn 1: remember the word ORCHID. Reply OK."); time.sleep(6)
            hist = [{"role": "user", "content": "Turn 1: remember the word ORCHID. Reply OK."}, {"role": "assistant", "content": h1["text"] or "OK"}]
            time.sleep(2); h2 = probe(small, 2, hist=hist, user="Turn 2: what word did I ask you to remember? One word.")
            cache["multiturn"] = dict(turn1=h1, turn2=h2, turn2_cached_covers_turn1=bool(h2["cached"] and h1["input"] and h2["cached"] >= h1["input"] - 200), recalled=("ORCHID" in (h2["text"] or "").upper()))
            self.log(f"E {c.label} multi-turn: turn1 input={h1['input']} cached={h1['cached']} -> turn2 input={h2['input']} cached={h2['cached']} recalled={cache['multiturn']['recalled']}")
            self.res[c.label]["cache"] = cache
            # TTL probes in background
            def ttl_worker(c=c, big=big, base_at=r3["at"], probe=probe, cache=cache):
                cache["ttl"] = []
                for d in self.ttl:
                    wait = base_at + d - time.time()
                    if wait > 0: time.sleep(wait)
                    x = probe(big, 100 + d, stream=False)
                    with self.lock: cache["ttl"].append(dict(after_s=d, cached=x["cached"], input=x["input"], st=x["st"], total=x["total"]))
                    self.log(f"E {c.label} TTL +{d}s: cached={x['cached']}/{x['input']}")
            t = threading.Thread(target=ttl_worker, daemon=True); t.start(); self.threads.append(t)

    def run(self, groups):
        for g, fn in (("latency", self.a_latency), ("speed", self.b_speed), ("cache", self.e_cache), ("burst", self.d_burst)):
            if g in groups: self.log(f"=== {g}"); fn()
        for t in self.threads: t.join()
        os.makedirs(os.path.join(HERE, "results", "ops"), exist_ok=True)
        for l, r in self.res.items(): json.dump(r, open(os.path.join(HERE, "results", "ops", l + ".json"), "w"), indent=1, ensure_ascii=False)
        self.report()

    def report(self):
        R = self.res; L = list(R); out = [f"# 运营指标专项报告（缓存 / 速度 / 稳定性）\n\n采样时间 {datetime.datetime.now().isoformat(timespec='minutes')}；模型 {self.model}；所有站点在同一时间窗口交错采样。\n"]
        def T(title, hdr, rowsfn):
            out.append(f"## {title}\n"); out.append("| 站点 | " + " | ".join(hdr) + " |"); out.append("|---|" + "---|" * len(hdr))
            for l in L:
                try: out.append(f"| {l} | " + " | ".join(str(x) for x in rowsfn(R[l])) + " |")
                except Exception as e: out.append(f"| {l} | (缺数据 {e}) |")
            out.append("")
        T("1. 短请求延迟与稳定性（交错顺序调用，effort=low，max_tokens=48）", ["次数", "成功", "错误", "空回复", "p50(s)", "p90", "p95", "max", "均值±σ", "错误"], lambda r: (r["latency"]["n"], r["latency"]["ok"], r["latency"]["errors"], r["latency"]["empty"], r["latency"]["p50"], r["latency"]["p90"], r["latency"]["p95"], r["latency"]["max"], f"{r['latency']['mean']}±{r['latency']['stdev']}", ",".join(sorted({("HTTP%s" % x["st"]) if x["st"] else "连接失败" for x in r["latency"]["rows"] if x["st"] != 200})) or "-"))
        T("2. 流式生成速度（effort=low，300 词短文，5 次取中位）", ["有效样本", "tok/s p50", "tok/s 区间", "TTFB p50", "TTFT(正文) p50", "总耗时 p50", "tok/chunk"], lambda r: (r["speed_low_effort"]["n_ok"], r["speed_low_effort"]["tps_p50"], f"{r['speed_low_effort']['tps_min']}-{r['speed_low_effort']['tps_max']}", r["speed_low_effort"]["ttfb_p50"], r["speed_low_effort"]["ttft_p50"], r["speed_low_effort"]["total_p50"], r["speed_low_effort"]["chunk_tok_p50"]))
        T("3. 真实场景：默认思考强度写代码（3 次取中位）", ["有效样本", "TTFB(首个思考token)", "首个正文token", "总耗时", "思考 tokens", "输出 tokens", "正文 tok/s"], lambda r: (r["speed_default_effort"]["n_ok"], r["speed_default_effort"]["ttfb_p50"], r["speed_default_effort"]["ttft_text_p50"], r["speed_default_effort"]["total_p50"], r["speed_default_effort"]["reasoning_tokens_p50"], r["speed_default_effort"]["out_tokens_p50"], r["speed_default_effort"]["tps_p50"]))
        T("4. 并发压力", ["8并发 错误", "8并发 p50/p90/max", "8并发 墙钟", "16并发 错误", "16并发 p50/p90/max", "16并发 墙钟", "req/s@16", "错误码"], lambda r: (r["burst"]["burst8"]["errors"], f"{r['burst']['burst8']['p50']}/{r['burst']['burst8']['p90']}/{r['burst']['burst8']['max']}", r["burst"]["burst8"]["wall"], r["burst"]["burst16"]["errors"], f"{r['burst']['burst16']['p50']}/{r['burst']['burst16']['p90']}/{r['burst']['burst16']['max']}", r["burst"]["burst16"]["wall"], r["burst"]["burst16"]["req_per_s"], ",".join(r["burst"]["burst16"]["error_codes"] + r["burst"]["burst8"]["error_codes"]) or "-"))
        T("5. 缓存：20k 前缀重复命中 + TTFT 收益", ["前缀 tok", "第1次 cached", "第2次 cached", "第3次 cached", "命中占比(哪次)", "TTFT 未命中→命中", "TTFT 收益", "总耗时 未命中→命中"], lambda r: (r["cache"]["prefix_tokens"], r["cache"]["calls"][0]["cached"], r["cache"]["calls"][1]["cached"], r["cache"]["calls"][2]["cached"], f"{r['cache']['hit_ratio']}(第{r['cache']['hit_on_call']}次)", f"{r['cache']['ttft_uncached']}→{r['cache']['ttft_cached']}", f"{r['cache']['ttft_gain_pct']}%", f"{r['cache']['total_uncached']}→{r['cache']['total_cached']}"))
        T("6. 缓存 TTL（同一前缀在 N 秒后是否仍命中）", [f"+{d}s" for d in self.ttl], lambda r: tuple(next(((f"{x['cached']}/{x['input']}" if x.get("st") == 200 else f"HTTP{x.get('st')}") for x in r["cache"].get("ttl", []) if x["after_s"] == d), "?") for d in self.ttl))
        T("7. 多轮对话前缀缓存（第2轮 cached 是否覆盖第1轮全部输入）", ["轮1 input/cached", "轮2 input/cached", "轮2缓存覆盖轮1", "记忆正确"], lambda r: (f"{r['cache']['multiturn']['turn1']['input']}/{r['cache']['multiturn']['turn1']['cached']}", f"{r['cache']['multiturn']['turn2']['input']}/{r['cache']['multiturn']['turn2']['cached']}", r["cache"]["multiturn"]["turn2_cached_covers_turn1"], r["cache"]["multiturn"]["recalled"]))
        txt = "\n".join(out); open(os.path.join(HERE, "OPS.md"), "w").write(txt); print(txt)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--ch", action="append", required=True, help="label=[anthropic@]base:key"); ap.add_argument("--model", default="glm-5.3-flash")
    ap.add_argument("--report-only", action="store_true", help="rebuild OPS.md from results/ops/*.json"); ap.add_argument("--rounds", type=int, default=30); ap.add_argument("--ttl", default="60,180,300,600"); ap.add_argument("--only", default="latency,speed,cache,burst"); ap.add_argument("--speed-n", type=int, default=5)
    a = ap.parse_args(); chans = []
    for s in a.ch:
        label, rest = s.split("=", 1); dialect = "openai"
        if rest.startswith("anthropic@"): dialect = "anthropic"; rest = rest[len("anthropic@"):]
        base, key = rest.rsplit(":", 1); c = Channel(base, key, dialect, a.model); c.label = label; chans.append(c)
    o = Ops(chans, a.model, a.rounds, [int(x) for x in a.ttl.split(",") if x]); o.b_speed.__func__.__defaults__ = (a.speed_n,)
    if a.report_only:
        import glob
        o.res = {}
        for c in chans:
            p = os.path.join(HERE, "results", "ops", c.label + ".json")
            if os.path.exists(p):
                r = json.load(open(p)); ca = r.get("cache", {}); calls = ca.get("calls") or []
                if calls:  # recompute hit ratio with anthropic-style accounting
                    hr = calls[1] if (calls[1].get("cached") or 0) > 1000 else calls[2]; inp = hr.get("input") or 0; cd = hr.get("cached") or 0
                    ca["hit_ratio"] = round(cd / (inp + cd), 3) if c.dialect == "anthropic" and (inp + cd) else (round(cd / inp, 3) if inp else None)
                o.res[c.label] = r
        o.report(); return
    o.run([g for g in a.only.split(",") if g])
if __name__ == "__main__": main()
