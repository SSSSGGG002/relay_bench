#!/usr/bin/env python3
"""Aggregate results/*/*.json into REPORT.md (comparison matrix + red flags + knowledge/IQ matrices)."""
import glob, json, os, re, sys, collections
HERE = os.path.dirname(os.path.abspath(__file__))
def load(root):
    rows = []
    for p in sorted(glob.glob(os.path.join(root, "*", "*.json"))):
        if re.search(r"\.[a-z]+(-[a-z]+)*\.json$", os.path.basename(p)) and not os.path.basename(p).count(".") == 1: pass
        try: d = json.load(open(p))
        except Exception: continue
        if "meta" not in d: continue
        d["_path"] = p; rows.append(d)
    # prefer the full-result file when partial files exist for the same model
    seen = {}
    for d in rows:
        k = (d["meta"]["label"], d["meta"]["model"])
        if k not in seen or len(d["findings"]) > len(seen[k]["findings"]): seen[k] = d
    return list(seen.values())
def g(m, k, d="-"):
    v = m.get(k); return d if v is None else v
def golden_compare(d):
    """Compare a relay's knowledge answers with the golden run of the same official model (suite/golden/<claimed>.json)."""
    key = d["meta"].get("expect_key"); m = d["metrics"]
    if not key: return None
    gp = os.path.join(HERE, "suite", "golden", key + ".json")
    if not os.path.exists(gp) or not d["extra"].get("knowledge"): return None
    g = json.load(open(gp))
    gold = {r["id"]: r["cls"] for r in g["ladder"]}; rel = {r["id"]: r["cls"] for r in d["extra"]["knowledge"]}
    ids = [i for i in gold if i in rel and not i.startswith("K00")]
    missing = [i for i in ids if gold[i] == "CORRECT" and rel[i] != "CORRECT"]
    extra = [i for i in ids if rel[i] == "CORRECT" and gold[i] != "CORRECT"]
    both = [i for i in ids if gold[i] == "CORRECT" and rel[i] == "CORRECT"]
    ge = {r["id"]: r["era"] for r in g.get("recency", []) if r["id"] != "C8"}; re_ = {r["id"]: r["era"] for r in d["extra"].get("recency", [])}   # C8 (latest Claude model) is contaminated by Claude Code's own model list in the golden run
    rec_older = [i for i in ge if i in re_ and ge[i] and re_[i] and re_[i] < ge[i]]
    rec_newer = [i for i in ge if i in re_ and ge[i] and re_[i] and re_[i] > ge[i]]
    if (len(missing) >= 3 and not extra) or (len(rec_older) >= 4 and not rec_newer): v = "older"
    elif len(extra) >= 2 or len(rec_newer) >= 2: v = "newer"
    elif missing or len(rec_older) >= 2: v = "borderline"
    else: v = "consistent"
    m["golden_verdict"] = v; m["golden_missing"] = missing; m["golden_extra"] = extra; m["golden_both"] = len(both); m["golden_rec_older"] = rec_older; m["golden_rec_newer"] = rec_newer
    return v

def verdict(d):
    m = d["metrics"]; flags = []
    gv = golden_compare(d)
    if gv is not None: m["knowledge_verdict"] = gv   # golden comparison overrides the nominal-cutoff heuristic
    if m.get("basic_ok") is False: return "UNREACHABLE", ["basic call failed"]
    kv = m.get("knowledge_verdict")
    if kv == "older": flags.append("知识明显少于官方同型号(假映射)" if m.get("golden_verdict") else "知识截止早于所声称型号(假映射)")
    if kv == "newer": flags.append("知道官方同型号不知道的事(映射到别的模型或注入)")
    if kv == "borderline": flags.append("知识前沿比声称截止早2-4个月(临界)")
    pm = m.get("pool_mix_eras")
    if pm and len({e for e in pm if e}) > 1: flags.append(f"同题4次答案年代不一致{pm}(混合池)")
    if (m.get("avg_tokens_per_chunk") or 0) > 40: flags.append(f"假流式(每chunk≈{m['avg_tokens_per_chunk']}tok)")
    if m.get("thinking_default") is False and d["meta"].get("expect_key") in ("claude-opus-5", "claude-sonnet-5", "claude-fable-5-1", "claude-fable-5"): flags.append("默认无thinking块(Claude 5系应默认思考)")
    if m.get("self_family") and d["meta"]["dialect"] == "anthropic":
        fam = re.search(r"(fable|opus|sonnet|haiku)", d["meta"]["model"])
        if fam and m["self_family"] in ("fable", "opus", "sonnet", "haiku") and m["self_family"] != fam.group(1): flags.append(f"自报家族={m['self_family']}(仅参考:真模型也会跟着提示自报)")
    v = (m.get("self_vendor") or "").lower(); want = "anthropic" if d["meta"]["dialect"] == "anthropic" else "openai"
    if v and want not in v: flags.append(f"自报厂商={v[:20]}(仅参考)")
    if m.get("thinking_signature") is False and m.get("thinking_visible"): flags.append("thinking无签名")
    ps = m.get("passthrough_score")
    if ps is not None and ps < 0.5: flags.append(f"参数校验一致率{ps:.0%}(请求被改写)")
    if m.get("tokenizer_o200k_match") is False: flags.append("token计数≠o200k")
    if m.get("cache_works") is False: flags.append("缓存不命中")
    if (m.get("injected_tokens_est") or 0) > 150: flags.append(f"注入~{m['injected_tokens_est']}tok隐藏提示")
    if m.get("stop_sequences_honored") is False: flags.append("stop序列被忽略")
    if m.get("max_tokens_honored") is False: flags.append("max_tokens未生效")
    if (m.get("seq_errors") or 0) > 0: flags.append(f"顺序调用错误{m['seq_errors']}")
    if (m.get("cache_isolation_read") or 0) >= 500: flags.append("缓存命中造假(新前缀也报命中)")
    if (m.get("soak_error_rate") or 0) > 0.05: flags.append(f"soak错误率{m['soak_error_rate']:.0%}")
    bs = m.get("burst_success")
    if bs and bs.split("/")[0] != bs.split("/")[1]: flags.append(f"并发失败{bs}")
    if (m.get("speed_errors") or 0) > 0: flags.append(f"吞吐采样失败{m['speed_errors']}次")
    for k, v in m.items():
        if k.startswith("ctx_") and k.count("_") == 1 and isinstance(v, str) and (v.startswith("ERR") or (v.endswith("/3") and not v.startswith("3/"))): flags.append(f"{k}={v}")
    iq = d["extra"].get("iq", [])
    ref = sum(1 for r in iq if r.get("refused")); emp = sum(1 for r in iq if r.get("empty"))
    if ref: flags.append(f"中转对良性推理任务拒答(refusal){ref}次")
    if emp >= 3: flags.append(f"空响应/截断{emp}次(可靠性差)")
    fails = [f for f in d["findings"] if f["status"] == "FAIL"]
    sev = "FAKE/ALTERED" if any(x in " ".join(flags) for x in ("假映射", "混合池", "无签名")) else ("SUSPICIOUS" if len(flags) >= 3 or len(fails) >= 3 else ("OK-ish" if flags else "CLEAN"))
    return sev, flags
def short(c):
    lab = c["meta"]["label"].replace("88wk-", "").replace("bitmiracle", "bit")
    return f"{lab}/{c['meta']['model'].replace('claude-', '').replace('-20251001', '')}"

def shape(d):
    m = d["metrics"]; e = d["extra"]; idp = (m.get("id_sample") or "")[:9]
    hp = (m.get("hidden_prompt_head") or "") + " " + (m.get("injected_instructions") or "")
    if m.get("thinking_signature") is True and d["meta"]["dialect"] == "anthropic":
        return f"真·Anthropic直连(thinking有效签名) id={idp or 'n/a'}"
    tag = "Kiro/Bedrock" if "kiro" in hp.lower() or "toolu_bdrk" in json.dumps(e.get("basic", {})) or "tooluse_" in json.dumps([f["detail"] for f in d["findings"] if f["name"].startswith("tool_call")]) else ("Codex池" if "codex" in hp.lower() or idp.startswith("resp_") else ("ClaudeCode池" if (m.get("cache_rows") or [{}])[0].get("write") and m.get("injected_tokens_est", 0) < 50 and d["meta"]["dialect"] == "anthropic" else "?"))
    return f"{tag} 注入≈{m.get('injected_tokens_est','-')} id={idp}"

def main():
    root = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "results")
    rows = load(root)
    if not rows: print("no results"); return
    out = []
    out.append("# relay-bench 报告\n")
    out.append(f"结果文件: {len(rows)} 个 (目录 {root})\n")
    # ---- IQ capability scoreboard (the gap the user cares about) ----
    keep_path = os.path.join(HERE, "suite", "iq_keep.json")
    keep = set(json.load(open(keep_path))) if os.path.exists(keep_path) else None
    if keep:  # score every model on the current curated bank only (older runs may carry retired items)
        for d in rows:
            if d["extra"].get("iq"):
                d["extra"]["iq"] = [r for r in d["extra"]["iq"] if r["id"] in keep or r["tier"] == "screen"]
                for t in ("iq_direct", "iq_screen", "iq_reason", "iq_reason_off", "iq_hard", "iq_hard_off", "iq_xhard", "iq_xhard_off"):
                    d["metrics"].pop(t, None)
                for tier in ("screen", "reason", "hard", "xhard"):
                    for mode in ("default", "off"):
                        sel = [r for r in d["extra"]["iq"] if r["tier"] == tier and r["mode"] == mode]
                        if not sel: continue
                        def _trunc(r): return (r["tier"] != "direct" and r.get("stop") in ("end_turn", "stop") and (r.get("out_tokens") or 0) < 40 and not r["correct"] and "answer" not in (r.get("got") or "").lower() and len(r.get("got") or "") < 30)
                        scored = [r for r in sel if not r.get("refused") and not r.get("empty") and r.get("status", 200) == 200 and not _trunc(r)]
                        key = f"iq_{tier}" + ("" if mode == "default" else "_off")
                        d["metrics"][key] = f"{sum(r['correct'] for r in scored)}/{len(scored)}"
                        d["metrics"][key + "_glitch"] = len(sel) - len(scored)
    iqrows = [d for d in sorted(rows, key=lambda x: (x["meta"]["label"], x["meta"]["model"])) if d["extra"].get("iq")]
    if iqrows:
        out.append("## 0. 智力分档对比（拉开差距的核心）\n")
        out.append("每格 = 答对数/总题数（思考默认开启；`_off` = 强制关闭思考）。只统计当前题库 `suite/iq_keep.json` 里的 26 题；中转拒答/空响应不计入分母（括号内为剔除次数）。难度递增：reason < hard < xhard。\n")
        tiers = ["iq_screen", "iq_reason", "iq_reason_off", "iq_hard", "iq_hard_off", "iq_xhard", "iq_xhard_off"]
        present = [t for t in tiers if any(t in d["metrics"] for d in iqrows)]
        out.append("| 站点/模型 | " + " | ".join(t.replace("iq_", "") for t in present) + " | 合计 |")
        out.append("|---|" + "---|" * (len(present) + 1))
        for d in iqrows:
            m = d["metrics"]; cells = []; tot_c = tot_n = 0
            for t in present:
                v = m.get(t, "")
                if isinstance(v, str) and "/" in v:
                    c, n = v.split("/"); tot_c += int(c); tot_n += int(n)
                cells.append(str(v) if v else "-")
            gl = sum(v for k, v in m.items() if k.startswith("iq_") and k.endswith("_glitch"))
            out.append(f"| {short(d)} | " + " | ".join(cells) + f" | **{tot_c}/{tot_n}**" + (f" (中转故障剔除{gl})" if gl else "") + " |")
        out.append("")
        out.append("### 各题耗时（reason+hard+xhard，思考开启，单位秒）\n")
        out.append("| 站点/模型 | reason均 | hard均 | xhard均 |")
        out.append("|---|---|---|---|")
        for d in iqrows:
            m = d["metrics"]
            out.append(f"| {short(d)} | {m.get('iq_reason_latency','-')} | {m.get('iq_hard_latency','-')} | {m.get('iq_xhard_latency','-')} |")
        out.append("")
    out.append("## 1. 总览矩阵\n")
    hdr = ["站点", "模型", "协议", "结论", "上游形态", "参数一致率", "知识前沿(阶梯/开放)", "自报", "tok比率EN", "注入tok", "缓存", "缓存隔离/过期", "TTFT中位", "tok/s中位", "p50", "并发成功", "soak错误率", "IQ直答", "IQ推理", "IQ困难", "IQ超难", "ctx20k", "ctx60k", "ctx130k", "ctx230k", "红旗"]
    out.append("| " + " | ".join(hdr) + " |"); out.append("|" + "---|" * len(hdr))
    for d in sorted(rows, key=lambda x: (x["meta"]["label"], x["meta"]["model"])):
        m = d["metrics"]; sev, flags = verdict(d)
        ps = m.get("passthrough_score"); ps = f"{ps:.0%}({m.get('passthrough_n')})" if ps is not None else "-"
        selfr = f"{g(m,'self_vendor')}/{g(m,'self_family')}{g(m,'self_version','')}"
        out.append("| " + " | ".join(str(x) for x in [d["meta"]["label"], d["meta"]["model"], d["meta"]["dialect"][:4], sev, shape(d), ps, f"{g(m, 'knowledge_frontier')}/{g(m, 'recency_frontier')}", selfr[:28], g(m, "tok_ratio_en"), g(m, "injected_tokens_est"), {True: "命中", False: "未命中"}.get(m.get("cache_works"), "-"), (f"iso={g(m,'cache_isolation_read')}/exp={g(m,'cache_expiry_read')}" if "cache_isolation_read" in m else "-"), g(m, "ttft_median", g(m, "ttft")), g(m, "tps_median", g(m, "tps")), g(m, "seq_p50"), g(m, "burst_success"), g(m, "soak_error_rate"), g(m, "iq_direct"), g(m, "iq_reason"), g(m, "iq_hard"), g(m, "iq_xhard"), g(m, "ctx_20k"), g(m, "ctx_60k"), g(m, "ctx_130k"), g(m, "ctx_230k"), len(flags)]) + " |")
    out.append("\n结论分级: CLEAN=无红旗; OK-ish=有轻微红旗; SUSPICIOUS=≥3个红旗; FAKE/ALTERED=知识截止/自报身份/签名证据表明不是所声称的模型。\n")
    out.append("## 2. 每个模型的红旗与关键证据\n")
    for d in sorted(rows, key=lambda x: (x["meta"]["label"], x["meta"]["model"])):
        sev, flags = verdict(d); m = d["metrics"]
        out.append(f"### {d['meta']['label']} / {d['meta']['model']}  → **{sev}**")
        out.append(f"- 红旗: {'; '.join(flags) if flags else '无'}")
        out.append(f"- 自报: `{(m.get('self_report') or '')[:160]}`")
        out.append(f"- 知识前沿: 阶梯={m.get('knowledge_frontier')} 开放式={m.get('recency_frontier')} 判定={m.get('knowledge_verdict')} (声称型号 {d['meta'].get('expect_key')})")
        if m.get("golden_verdict"): out.append(f"- 与官方同型号金标准逐题对比: 官方知道而它不知道={m.get('golden_missing')} ; 它知道而官方不知道={m.get('golden_extra')} ; 双方都知道={m.get('golden_both')} ; 开放式探针比官方更旧={m.get('golden_rec_older')} 更新={m.get('golden_rec_newer')}")
        if m.get("hidden_prompt_head"): out.append(f"- 泄露的隐藏系统提示: `{m['hidden_prompt_head'][:160]}`")
        if m.get("speed_runs"): out.append(f"- 吞吐采样: {m['speed_runs']}")
        if m.get("burst_statuses"): out.append(f"- 并发{m.get('burst_n')}: 状态={m['burst_statuses']} p50={m.get('burst_p50')}s p95={m.get('burst_p95')}s")
        if m.get("soak_calls"): out.append(f"- soak {m.get('soak_minutes')}min: {m['soak_calls']}次 错误率={m.get('soak_error_rate')} p50={m.get('soak_p50')}s p95={m.get('soak_p95')}s max={m.get('soak_max')}s 空响应={m.get('soak_empty')}")
        if "cache_isolation_read" in m: out.append(f"- 缓存TTL检查: 新前缀cache_read={m.get('cache_isolation_read')} 1h写入={m.get('cache_1h_write')} 5.5分钟后cache_read={m.get('cache_expiry_read')}")
        if m.get("injected_instructions"): out.append(f"- Responses API 回显的注入 instructions: `{m['injected_instructions'][:160]}`")
        if m.get("max_tokens_leak_msg"): out.append(f"- 上限探针错误信息: `{m['max_tokens_leak_msg'][:160]}`")
        for f in d["findings"]:
            if f["status"] in ("FAIL", "WARN"): out.append(f"- [{f['status']}] {f['group']}/{f['name']}: {f['detail'][:260]}")
        out.append("")
    out.append("## 3. 知识截止阶梯 (✓知道 ?不知道 ✗答错 !错误)\n")
    items = None
    for d in rows:
        if d["extra"].get("knowledge"): items = [(r["id"], r["date"]) for r in d["extra"]["knowledge"]]; break
    if items:
        cols = [d for d in sorted(rows, key=lambda x: (x["meta"]["label"], x["meta"]["model"])) if d["extra"].get("knowledge")]
        out.append("| 题 | 日期 | " + " | ".join(short(c) for c in cols) + " |"); out.append("|---|---|" + "---|" * len(cols))
        sym = {"CORRECT": "✓", "UNKNOWN": "?", "WRONG": "✗", "ERR": "!"}
        for kid, date in items:
            out.append(f"| {kid} | {date} | " + " | ".join(sym.get(next((r["cls"] for r in c["extra"]["knowledge"] if r["id"] == kid), ""), "") for c in cols) + " |")
        out.append("")
    out.append("## 3b. 开放式近期知识探针 (答案所属年代)\n")
    cols = [d for d in sorted(rows, key=lambda x: (x["meta"]["label"], x["meta"]["model"])) if d["extra"].get("recency")]
    if cols:
        ids = [r["id"] for r in cols[0]["extra"]["recency"]]
        out.append("| 题 | " + " | ".join(short(c) for c in cols) + " |"); out.append("|---|" + "---|" * len(cols))
        for kid in ids:
            cells = []
            for c in cols:
                r = next((x for x in c["extra"]["recency"] if x["id"] == kid), None)
                cells.append(f"{r['era']} `{r['answer'][:22]}`" if r else "")
            out.append(f"| {kid} | " + " | ".join(cells) + " |")
        out.append("")
    out.append("## 4. IQ 分题矩阵\n")
    cols = [d for d in sorted(rows, key=lambda x: (x["meta"]["label"], x["meta"]["model"])) if d["extra"].get("iq")]
    if cols:
        ids = []
        for c in cols:
            for r in c["extra"]["iq"]:
                k = (r["id"], r["mode"]);
                if k not in ids: ids.append(k)
        out.append("| 题 | 模式 | " + " | ".join(short(c) for c in cols) + " |"); out.append("|---|---|" + "---|" * len(cols))
        for kid, mode in ids:
            out.append(f"| {kid} | {mode} | " + " | ".join(next(("✓" if r["correct"] else "✗") for r in c["extra"]["iq"] if r["id"] == kid and r["mode"] == mode) if any(r["id"] == kid and r["mode"] == mode for r in c["extra"]["iq"]) else "" for c in cols) + " |")
        out.append("")
    out.append("## 5. 同站点跨模型聚类 (相同输出 = 很可能同一上游)\n")
    by = collections.defaultdict(list)
    for d in rows:
        if d["extra"].get("cluster"): by[d["meta"]["label"]].append(d)
    for label, ds in by.items():
        out.append(f"### {label}")
        for i in range(len(ds)):
            for j in range(i + 1, len(ds)):
                a, b = ds[i], ds[j]; same = [k for k in a["extra"]["cluster"] if a["extra"]["cluster"][k]["text"] and a["extra"]["cluster"][k]["text"] == b["extra"]["cluster"].get(k, {}).get("text")]
                ina = [a["extra"]["cluster"][k]["input"] for k in a["extra"]["cluster"]]; inb = [b["extra"]["cluster"].get(k, {}).get("input") for k in a["extra"]["cluster"]]
                out.append(f"- {a['meta']['model']} vs {b['meta']['model']}: 相同输出 {len(same)}/{len(a['extra']['cluster'])} {same} ; input_tokens {ina} vs {inb}")
        out.append("")
    txt = "\n".join(out)
    open(os.path.join(HERE, "REPORT.md"), "w").write(txt)
    print(txt)
if __name__ == "__main__":
    main()
