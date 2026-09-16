#!/usr/bin/env python3
"""final.py — 把 bench(results/<label>/glm-5.3-flash.json) + ops + greedy + xcache 汇总成 FINAL.md（商用渠道分析总表）。"""
import glob, json, os, re, statistics
HERE = os.path.dirname(os.path.abspath(__file__))
def J(p):
    try: return json.load(open(p))
    except Exception: return None
def frac(s):
    if isinstance(s, str) and "/" in s: a, b = s.split("/"); return int(a), int(b)
    return None
labels = ["zhipu-official", "zhipu-official-anthropic", "v129-K1", "v129-K2", "v129-K3", "v129-K4", "rtoc", "rtoc-anthropic", "v129-K1-anthropic"]
B = {l: J(os.path.join(HERE, "results", l, "glm-5.3-flash.json")) for l in labels}
O = {os.path.basename(p)[:-5]: J(p) for p in glob.glob(os.path.join(HERE, "results", "ops", "*.json"))}
G = {os.path.basename(p)[:-5]: J(p) for p in glob.glob(os.path.join(HERE, "results", "greedy", "*.json"))}
X = J(os.path.join(HERE, "results", "xcache.json")) or {}
out = ["# GLM-5.3-flash 商用渠道分析总表（官方基准 vs 中转站）\n"]
def iqsum(m, tiers):
    c = n = 0
    for t in tiers:
        f = frac(m.get(t))
        if f: c += f[0]; n += f[1]
    return f"{c}/{n}" if n else "-"
out.append("## 1. 一页总览\n")
hdr = ["通道", "协议", "可用", "上游判定", "id原生", "参数校验一致", "stop生效", "注入tok", "知识前沿", "IQ思考开(直答+推理+困难+超难)", "IQ关思考(推理+困难+超难)", "推理题均耗时", "230k三针", "缓存", "顺序8次错/空", "8并发错", "TTFT", "tok/s"]
out.append("| " + " | ".join(hdr) + " |"); out.append("|" + "---|" * len(hdr))
for l in labels:
    d = B.get(l)
    if not d: continue
    m = d["metrics"]
    if m.get("basic_ok") is False:
        err = next((f["detail"] for f in d["findings"] if f["name"] == "basic"), "")
        out.append(f"| {l} | {d['meta']['dialect']} | ❌ | {re.sub(r'.*message.: .', '', err)[:60]} |" + " - |" * (len(hdr) - 4)); continue
    idn = "✓" if any(f["name"] == "message_id_format" and f["status"] == "PASS" for f in d["findings"]) else "✗"
    ps = m.get("passthrough_score"); ps = f"{ps:.0%}" if ps is not None else "-"
    out.append("| " + " | ".join(str(x) for x in [l, d["meta"]["dialect"], "✓", "", idn, ps, "✓" if m.get("stop_sequences_honored") else "✗", m.get("injected_tokens_est"), f"{m.get('knowledge_frontier')}/{m.get('recency_frontier')}", iqsum(m, ["iq_direct", "iq_reason", "iq_hard", "iq_xhard"]), iqsum(m, ["iq_reason_off", "iq_hard_off", "iq_xhard_off"]), f"{m.get('iq_reason_latency')}s", m.get("ctx_230k", m.get("ctx_130k")), "命中" if m.get("cache_works") else "未命中", f"{m.get('seq_errors')}/{m.get('seq_empty')}", m.get("burst_errors"), m.get("ttft"), m.get("tps")]) + " |")
out.append("\n上游判定列见第 3 节（由跨账号缓存互通、id/usage 形态、参数改写行为综合得出）。\n")
# 2. official fingerprint
out.append("## 2. 官方基准数据（两种协议）\n")
for l in ("zhipu-official", "zhipu-official-anthropic"):
    d = B.get(l); m = d["metrics"] if d else {}
    if not d: continue
    out.append(f"### {l}\n")
    out.append(f"- 调用 {d['meta']['calls']} 次，耗时 {d['meta']['seconds']}s；id 样例 `{m.get('id_sample')}`；usage 字段 `{m.get('usage_keys')}`；注入 {m.get('injected_tokens_est')} tok")
    out.append(f"- 参数校验 {m.get('passthrough_score')}；stop 生效 {m.get('stop_sequences_honored')}；max_tokens 生效 {m.get('max_tokens_honored')}；max_completion_tokens 生效 {m.get('max_completion_tokens_honored')}")
    out.append(f"- 自报 `{(m.get('self_report') or '')[:120]}`；知识阶梯前沿 {m.get('knowledge_frontier')}，开放式 {m.get('recency_frontier')}；同题 4 次年代 {m.get('pool_mix_eras')}")
    out.append(f"- 分词 EN Δ{m.get('tok_delta_en')} / ZH Δ{m.get('tok_delta_zh')}（官方 /tokenizer Δ{m.get('tok_official_delta_en')}/{m.get('tok_official_delta_zh')}）")
    out.append(f"- 上下文 20k/60k/130k/230k = {m.get('ctx_20k')}/{m.get('ctx_60k')}/{m.get('ctx_130k')}/{m.get('ctx_230k')}，耗时 {m.get('ctx_20k_latency')}/{m.get('ctx_60k_latency')}/{m.get('ctx_130k_latency')}/{m.get('ctx_230k_latency')}s；60k 下 system 规则 {m.get('sys_rule_60k')}")
    out.append(f"- 缓存 {m.get('cache_rows')}")
    out.append(f"- 顺序 8 次 p50 {m.get('seq_p50')}s 错 {m.get('seq_errors')} 空 {m.get('seq_empty')}；8 并发错 {m.get('burst_errors')} p50 {m.get('burst_p50')}s；TTFT {m.get('ttft')}s，{m.get('tps')} tok/s（{m.get('tps_min')}-{m.get('tps_max')}），2500tok 长输出 {m.get('long_output_ok')}")
    out.append(f"- IQ 直答 {m.get('iq_direct')} 推理 {m.get('iq_reason')}({m.get('iq_reason_latency')}s) 困难 {m.get('iq_hard')}({m.get('iq_hard_latency')}s) 超难 {m.get('iq_xhard')}({m.get('iq_xhard_latency')}s)；关思考 推理 {m.get('iq_reason_off')} 困难 {m.get('iq_hard_off')} 超难 {m.get('iq_xhard_off')}\n")
# 3. cross cache
out.append("## 3. 跨账号缓存互通（上游是否就是智谱开放平台）\n")
out.append("| 探针 | 第一步 | 第二步 | 结论 |"); out.append("|---|---|---|---|")
for k, v in X.items():
    a, b = v[0], v[1]; same = v[2] if len(v) > 2 else None
    f = lambda r: f"{r.get('st')} in={r.get('prompt', r.get('input'))} cached={r.get('cached', r.get('cache_read'))} t={r.get('t')}s"
    out.append(f"| {k} | {f(a)} | {f(b)} | {'同一后端' if same else ('无互通' if same is False else '')} |")
out.append("")
# 4. per-relay findings
out.append("## 4. 各中转通道红旗与关键证据\n")
for l in labels:
    d = B.get(l)
    if not d or l.startswith("zhipu-official"): continue
    m = d["metrics"]; out.append(f"### {l} ({d['meta']['dialect']})\n")
    for f in d["findings"]:
        if f["status"] in ("FAIL", "WARN"): out.append(f"- [{f['status']}] {f['group']}/{f['name']}: {f['detail'][:240]}")
    out.append(f"- IQ 直答 {m.get('iq_direct')} 推理 {m.get('iq_reason')}({m.get('iq_reason_latency')}s) 困难 {m.get('iq_hard')} 超难 {m.get('iq_xhard')}；关思考 推理 {m.get('iq_reason_off')} 困难 {m.get('iq_hard_off')} 超难 {m.get('iq_xhard_off')}")
    out.append(f"- 上下文 {m.get('ctx_20k')}/{m.get('ctx_60k')}/{m.get('ctx_130k')}/{m.get('ctx_230k')}（{m.get('ctx_20k_latency')}/{m.get('ctx_60k_latency')}/{m.get('ctx_130k_latency')}/{m.get('ctx_230k_latency')}s）；缓存 {m.get('cache_rows')}；速度 TTFT {m.get('ttft')} {m.get('tps')} tok/s\n")
# 5. ops & greedy embedded
for name, fn in (("5. 运营指标专项（缓存 / 速度 / 稳定性，同窗口交错采样）", "OPS.md"), ("6. 量化 / 部署差异探测", "GREEDY.md"), ("7. 与官方逐项比对", "COMPARE.md")):
    p = os.path.join(HERE, fn)
    if os.path.exists(p):
        body = open(p).read(); body = re.sub(r"^# .*\n", "", body); body = re.sub(r"^## ", "### ", body, flags=re.M)
        out.append(f"## {name}\n"); out.append(body); out.append("")
txt = "\n".join(out); open(os.path.join(HERE, "FINAL.md"), "w").write(txt); print(f"FINAL.md written, {len(txt)} chars")
