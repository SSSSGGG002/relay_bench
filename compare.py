#!/usr/bin/env python3
"""Compare every relay result against the OFFICIAL baseline run of the same model.

  python3 compare.py --baseline zhipu-official [--baseline-anthropic zhipu-official-anthropic] [results_dir]

For each (label, model, dialect) that is not a baseline, find the baseline row with the same model+dialect and diff:
identity fingerprints (id format, response fields, usage keys, signature shape, tool-id format), parameter validation
(per-probe HTTP status vs the official status), tokenizer/usage numbers, thinking behaviour, knowledge frontier, IQ,
context recall, cache, stability and speed. Writes COMPARE.md.
"""
import argparse, glob, json, os, re, statistics
HERE = os.path.dirname(os.path.abspath(__file__))

def load(root):
    rows = {}
    for p in sorted(glob.glob(os.path.join(root, "*", "*.json"))):
        try: d = json.load(open(p))
        except Exception: continue
        if "meta" not in d: continue
        k = (d["meta"]["label"], d["meta"]["model"], d["meta"]["dialect"])
        if k not in rows or len(d["findings"]) > len(rows[k]["findings"]): rows[k] = d
    return rows

def num(x):
    try: return float(x)
    except Exception: return None

def frac(s):
    if isinstance(s, str) and "/" in s:
        a, b = s.split("/"); return int(a), int(b)
    return None

def cmp_row(rel, base):
    m, b = rel["metrics"], base["metrics"]; e, eb = rel["extra"], base["extra"]
    out = []; devs = []   # (dimension, relay, official, verdict)
    def row(dim, rv, bv, ok, note=""):
        if rv is None and bv is not None and not dim.startswith(("泄露", "相同请求")):
            out.append((dim, "未测", bv, "—", "该轮未覆盖此项")); return
        out.append((dim, rv, bv, "一致" if ok else "偏离", note))
        if not ok: devs.append(dim)
    # ---- identity fingerprints
    idr = m.get("id_sample") or ""; idb = b.get("id_sample") or ""
    pat = r"(msg_)?\d{14}[0-9a-f]{18}"
    row("响应 id 格式", idr[:34], idb[:34], bool(re.fullmatch(pat, idr)) == bool(re.fullmatch(pat, idb)), "官方=14位时间戳+18位hex；chatcmpl-/自造id=中转层重新生成")
    row("usage 字段集合", ",".join(m.get("usage_keys") or []), ",".join(b.get("usage_keys") or []), (m.get("usage_keys") or []) == (b.get("usage_keys") or []))
    tk = (e.get("basic") or {}).get("extra", {}).get("top_keys"); tkb = (eb.get("basic") or {}).get("extra", {}).get("top_keys")
    if tk or tkb: row("响应顶层字段", ",".join(tk or []), ",".join(tkb or []), tk == tkb, "官方带 request_id、无 system_fingerprint/service_tier")
    row("模型名回显", m.get("model_echo"), b.get("model_echo"), m.get("model_echo") == b.get("model_echo"))
    if rel["meta"]["dialect"] == "anthropic":
        row("thinking signature 形态", m.get("signature_shape"), b.get("signature_shape"), m.get("signature_shape") == b.get("signature_shape"), "官方=24位hex")
        row("流式 ping 事件", m.get("stream_pings"), b.get("stream_pings"), bool(m.get("stream_pings")) == bool(b.get("stream_pings")))
    else:
        row("默认返回 reasoning_content", m.get("thinking_default"), b.get("thinking_default"), m.get("thinking_default") == b.get("thinking_default"), "GLM-5.3 永远思考；没有=思考被剥离或换了模型")
        row("流式 obfuscation 字段", m.get("stream_obfuscation"), b.get("stream_obfuscation"), m.get("stream_obfuscation") == b.get("stream_obfuscation"), "官方无此字段；有=经过 OpenAI 原生/new-api 改写")
    for k in ("tool_id_native_sync", "tool_id_native_stream"):
        if k in m or k in b: row(f"工具调用 id 格式({k[-6:]})", m.get(k), b.get(k), m.get(k) == b.get(k), "官方 openai=call_+有符号整数 / anthropic=call_+24hex")
    row("隐藏提示注入(多算的input tokens)", m.get("injected_tokens_est"), b.get("injected_tokens_est"), abs((m.get("injected_tokens_est") or 0) - (b.get("injected_tokens_est") or 0)) <= 8, "差值>8 = 上游加了系统提示或 usage 被改")
    if m.get("hidden_prompt_head"): row("泄露的隐藏系统提示", m["hidden_prompt_head"][:80], (b.get("hidden_prompt_head") or "")[:80], not m.get("hidden_prompt_head"))
    row("自报厂商", m.get("self_vendor"), b.get("self_vendor"), bool(re.search(r"zhipu|z\.ai|智谱", (m.get("self_vendor") or "").lower())))
    # ---- parameter validation vs official statuses
    pr = e.get("passthrough") or {}; pb = eb.get("passthrough") or {}
    common = [k for k in pb if k in pr]
    agree = [k for k in common if pr[k]["status"] == pb[k]["status"]]
    diff = [f"{k}:{pr[k]['status']}(官方{pb[k]['status']})" for k in common if pr[k]["status"] != pb[k]["status"]]
    if common: row("参数校验与官方逐项一致率", f"{len(agree)}/{len(common)}", "-", len(agree) >= len(common) - 1, " ".join(diff) if diff else "全部一致")
    for k in ("stop_sequences_honored", "max_tokens_honored", "multiturn_ok", "sys_rule_60k"):
        if k in m or k in b: row({"stop_sequences_honored": "stop 序列生效", "max_tokens_honored": "max_tokens 生效", "multiturn_ok": "20轮历史记忆", "sys_rule_60k": "60k 下 system 规则仍遵守"}[k], m.get(k), b.get(k), m.get(k) == b.get(k))
    # ---- tokenizer / usage
    for k, nm in (("tok_delta_en", "英文 +1261 o200k tok 的 usage 增量"), ("tok_delta_zh", "中文 +2040 o200k tok 的 usage 增量")):
        rv, bv = m.get(k), b.get(k)
        if rv is not None and bv is not None: row(nm, rv, bv, abs(rv - bv) <= max(6, 0.02 * bv), "偏差>2% = usage 不是 GLM 分词器算的(估算/伪造)")
    if "tokenizer_official_match" in m: row("usage 与官方 /tokenizer 一致", m.get("tokenizer_official_match"), b.get("tokenizer_official_match"), bool(m.get("tokenizer_official_match")))
    if "effort_max_reasoning_tokens" in m or "effort_max_reasoning_tokens" in b:
        row("reasoning_effort 生效(low→max 思考token增长)", f"{m.get('effort_low_reasoning_tokens')}→{m.get('effort_max_reasoning_tokens')}", f"{b.get('effort_low_reasoning_tokens')}→{b.get('effort_max_reasoning_tokens')}", (m.get("effort_max_reasoning_tokens") or 0) > (m.get("effort_low_reasoning_tokens") or 0))
    # ---- knowledge
    def months(a, b):
        try: ya, ma = map(int, a.split("-")); yb, mb = map(int, b.split("-")); return abs((ya - yb) * 12 + ma - mb)
        except Exception: return 99 if (a or b) else 0
    row("知识阶梯前沿", m.get("knowledge_frontier"), b.get("knowledge_frontier"), months(m.get("knowledge_frontier"), b.get("knowledge_frontier")) <= 1, "相差≥2个月才算偏离（temperature=1 抽样本身有±1个月噪声）；早于官方 = 更老的模型")
    row("开放式近期知识前沿", m.get("recency_frontier"), b.get("recency_frontier"), months(m.get("recency_frontier"), b.get("recency_frontier")) <= 1)
    kr = {r["id"]: r["cls"] for r in e.get("knowledge") or []}; kb = {r["id"]: r["cls"] for r in eb.get("knowledge") or []}
    if kr and kb:
        same = sum(1 for k in kb if kr.get(k) == kb[k]); row("知识阶梯逐题分类一致", f"{same}/{len(kb)}", "-", same >= len(kb) - 3, " ".join(f"{k}:{kr.get(k)}(官方{kb[k]})" for k in kb if kr.get(k) != kb[k]))
    pm = m.get("pool_mix_eras"); pmb = b.get("pool_mix_eras")
    mixed = lambda v: bool(v) and len({x for x in v if x}) > 1
    row("同题4次年代一致(无混合池)", pm, pmb, (not mixed(pm)) or mixed(pmb), "官方 GLM 本身对'现任教宗'就答不稳(方济各/良十四世各半)，所以只有官方稳定而中转不稳才算偏离")
    # ---- IQ
    for t in ("iq_direct", "iq_reason", "iq_reason_off", "iq_hard", "iq_hard_off", "iq_xhard", "iq_xhard_off"):
        fr, fb = frac(m.get(t)), frac(b.get(t))
        if fr and fb:
            row(f"智力 {t[3:]}", m[t], b[t], fr[0] >= fb[0] - 2, "低于官方2题以上 = 可能降级模型/思考被截断")
            lr, lb = m.get(t + "_latency"), b.get(t + "_latency")
            if lr and lb: row(f"  ↳ {t[3:]} 平均耗时(s)", lr, lb, lr <= lb * 2.5, "慢于官方2.5倍以上")
    # ---- context
    for k in ("ctx_20k", "ctx_60k", "ctx_130k", "ctx_230k"):
        if k in m or k in b: row(f"长上下文 {k[4:]} 三针召回", m.get(k), b.get(k), (m.get(k) == b.get(k)) or (str(m.get(k)).startswith("3/")), f"耗时 {m.get(k+'_latency')}s vs 官方 {b.get(k+'_latency')}s ; usage比 {m.get(k+'_usage_ratio')} vs {b.get(k+'_usage_ratio')}")
    # ---- cache
    cr = [x.get("read") or 0 for x in (m.get("cache_rows") or [])]; cb = [x.get("read") or 0 for x in (b.get("cache_rows") or [])]
    row("前缀缓存命中(cached_tokens 序列)", cr, cb, bool(m.get("cache_works")) == bool(b.get("cache_works")), "官方隐式缓存第2次即命中；不命中 = 账号池轮询/缓存层被剥离(你付全价)")
    # ---- stability
    row("顺序调用错误/空回复", f"{m.get('seq_errors')}/{m.get('seq_empty')} of {m.get('seq_n')}", f"{b.get('seq_errors')}/{b.get('seq_empty')} of {b.get('seq_n')}", (m.get("seq_errors") or 0) + (m.get("seq_empty") or 0) == 0)
    if "burst_errors" in m or "burst_errors" in b: row("8 并发错误数", m.get("burst_errors"), b.get("burst_errors"), (m.get("burst_errors") or 0) <= (b.get("burst_errors") or 0))
    if m.get("seq_inputs") and len(m["seq_inputs"]) > 1: row("相同请求 input_tokens 漂移", m["seq_inputs"], b.get("seq_inputs"), False, "多账号/多版本提示词轮询")
    if "long_output_ok" in m or "long_output_ok" in b: row("2500 token 长输出不断流", m.get("long_output_ok"), b.get("long_output_ok"), bool(m.get("long_output_ok")))
    # ---- speed
    for k, nm, worse in (("ttfb", "首字节 TTFB(s)", 2.0), ("ttft", "首个正文 token TTFT(s)", 2.0), ("seq_p50", "短请求 p50 延迟(s)", 1.8), ("burst_p50", "8并发 p50 延迟(s)", 2.0)):
        rv, bv = num(m.get(k)), num(b.get(k))
        if rv is not None and bv is not None: row(nm, rv, bv, rv <= bv * worse, f"{'快' if rv < bv else '慢'}{abs(rv/bv-1)*100:.0f}%")
    rv, bv = num(m.get("tps")), num(b.get("tps"))
    if rv is not None and bv is not None: row("生成速度 tok/s", f"{rv} ({m.get('tps_min')}-{m.get('tps_max')})", f"{bv} ({b.get('tps_min')}-{b.get('tps_max')})", rv >= bv * 0.6, f"{'快' if rv > bv else '慢'}{abs(rv/bv-1)*100:.0f}%")
    row("流式粒度 tok/chunk", m.get("avg_tokens_per_chunk"), b.get("avg_tokens_per_chunk"), (m.get("avg_tokens_per_chunk") or 0) <= max(8, 3 * (b.get("avg_tokens_per_chunk") or 1)), ">3倍官方 = 中转缓冲后再切块(假流式)")
    return out, devs

def categorize(devs):
    ident = [d for d in devs if any(x in d for x in ("知识阶梯前沿", "开放式近期知识", "自报厂商", "默认返回 reasoning", "混合池", "usage 增量", "tokenizer"))]
    iq = [d for d in devs if d.startswith("智力")]
    proto = [d for d in devs if any(x in d for x in ("id 格式", "usage 字段", "顶层字段", "signature", "obfuscation", "工具调用 id", "参数校验", "注入", "stop 序列", "max_tokens 生效", "reasoning_effort", "ping", "隐藏系统提示"))]
    ops = [d for d in devs if any(x in d for x in ("耗时", "TTFB", "TTFT", "tok/s", "并发", "顺序调用", "缓存", "长输出", "漂移", "chunk"))]
    ctx = [d for d in devs if any(x in d for x in ("上下文", "历史记忆", "system 规则"))]
    return ident, iq, proto, ops, ctx
def verdict(devs, rel=None):
    if rel and rel["metrics"].get("basic_ok") is False: return "⛔ 不可用（该分组没有此模型渠道 / 全部失败）"
    ident, iq, proto, ops, ctx = categorize(devs)
    if len(ident) >= 2 or (ident and len(iq) >= 2): return "❌ 模型身份与官方不一致（知识/自报/思考/分词证据）"
    if ident or len(iq) >= 3 or len(ctx) >= 2: return "⚠️ 模型层有偏离，需人工复核"
    if proto: return "🟡 模型一致，但经过协议改写层（new-api 转换；参数/流式/计费字段与官方不同）" + ("；运营指标偏离 %d 项" % len(ops) if ops else "")
    if ops: return "✅ 模型与协议一致；运营指标偏离 %d 项" % len(ops)
    return "✅ 与官方基准一致"

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--baseline", default="zhipu-official"); ap.add_argument("--baseline-anthropic", default=None); ap.add_argument("root", nargs="?", default=os.path.join(HERE, "results"))
    a = ap.parse_args(); rows = load(a.root)
    bases = {a.baseline}
    if a.baseline_anthropic: bases.add(a.baseline_anthropic)
    else:
        for (lab, mod, dia) in rows:
            if lab.startswith(a.baseline): bases.add(lab)
    out = ["# 中转站 vs 官方基准 对比报告\n", f"基准: {sorted(bases)}  (官方直连结果；每一行 = 中转站的数值 / 官方的数值 / 判定)\n"]
    # baseline summary
    out.append("## 0. 官方基准指纹速览\n")
    out.append("| 基准 | 模型 | 协议 | id样例 | usage字段 | 默认思考 | 注入tok | 知识前沿(阶梯/开放) | IQ direct/reason/hard/xhard | TTFT | tok/s | p50 | 缓存 | ctx |")
    out.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for (lab, mod, dia), d in sorted(rows.items()):
        if lab not in bases: continue
        m = d["metrics"]
        out.append(f"| {lab} | {mod} | {dia} | `{(m.get('id_sample') or '')[:34]}` | {','.join(m.get('usage_keys') or [])} | {m.get('thinking_default')} | {m.get('injected_tokens_est')} | {m.get('knowledge_frontier')}/{m.get('recency_frontier')} | {m.get('iq_direct')}/{m.get('iq_reason')}/{m.get('iq_hard')}/{m.get('iq_xhard')} | {m.get('ttft')} | {m.get('tps')} | {m.get('seq_p50')} | {[x.get('read') for x in (m.get('cache_rows') or [])]} | {m.get('ctx_20k')}/{m.get('ctx_60k')}/{m.get('ctx_130k')}/{m.get('ctx_230k')} |")
    out.append("")
    summary = []
    for (lab, mod, dia), d in sorted(rows.items()):
        if lab in bases: continue
        base = next((v for (l2, m2, d2), v in rows.items() if l2 in bases and m2 == mod and d2 == dia), None)
        if base is None: continue
        table, devs = cmp_row(d, base); v = verdict(devs, d); ident, iq, proto, ops, ctx = categorize(devs)
        summary.append((lab, mod, dia, v, f"身份{len(ident)}/智力{len(iq)}/协议{len(proto)}/上下文{len(ctx)}/运营{len(ops)}"))
        out.append(f"## {lab} / {mod} ({dia}) → {v}\n")
        out.append(f"偏离项 {len(devs)}（身份 {len(ident)}｜智力 {len(iq)}｜协议 {len(proto)}｜上下文 {len(ctx)}｜运营 {len(ops)}）: {', '.join(devs) if devs else '无'}\n")
        out.append("| 维度 | 中转站 | 官方 | 判定 | 说明 |"); out.append("|---|---|---|---|---|")
        for dim, rv, bv, ok, note in table:
            out.append(f"| {dim} | {str(rv).replace('|', '/')[:70]} | {str(bv).replace('|', '/')[:70]} | {ok} | {note[:120]} |")
        out.append("")
    out.insert(2, "## 总表\n\n| 中转站 | 模型 | 协议 | 结论 | 偏离项(身份/智力/协议/上下文/运营) |\n|---|---|---|---|---|\n" + "\n".join(f"| {l} | {m} | {d} | {v} | {n} |" for l, m, d, v, n in summary) + "\n")
    txt = "\n".join(out); open(os.path.join(HERE, "COMPARE.md"), "w").write(txt); print(txt)
if __name__ == "__main__": main()
