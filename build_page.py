#!/usr/bin/env python3
"""build_page.py — render the GLM-5.3-flash channel audit as a single HTML page (Artifact)."""
import glob, json, os, re, html, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
def J(p):
    try: return json.load(open(p))
    except Exception: return None
LAB = {"zhipu-official": "官方 OpenAI 协议", "zhipu-official-anthropic": "官方 Anthropic 协议", "v129-K1": "v129 K1", "v129-K2": "v129 K2", "v129-K3": "v129 K3", "v129-K4": "v129 K4", "v129-K1-anthropic": "v129 K1 · Anthropic 协议", "rtoc": "rtoc · OpenAI 协议", "rtoc-anthropic": "rtoc · Anthropic 协议"}
ORDER = ["zhipu-official", "zhipu-official-anthropic", "v129-K1", "v129-K2", "v129-K1-anthropic", "rtoc", "rtoc-anthropic", "v129-K3", "v129-K4"]
B = {l: J(os.path.join(HERE, "results", l, "glm-5.3-flash.json")) for l in ORDER}
O = {os.path.basename(p)[:-5]: J(p) for p in glob.glob(os.path.join(HERE, "results", "ops", "*.json"))}
G = {os.path.basename(p)[:-5]: J(p) for p in glob.glob(os.path.join(HERE, "results", "greedy", "*.json"))}
X = J(os.path.join(HERE, "results", "xcache.json")) or {}
E = html.escape
def v(x, dash="—"): return dash if x is None else str(x)
def frac(s):
    if isinstance(s, str) and "/" in s: a, b = s.split("/"); return int(a), int(b)
    return None
def iqsum(m, tiers):
    c = n = 0
    for t in tiers:
        f = frac(m.get(t))
        if f: c += f[0]; n += f[1]
    return f"{c}/{n}" if n else "—"
VERDICT = {
 "zhipu-official": ("base", "基准", "官方直连，所有指标的参照系"),
 "zhipu-official-anthropic": ("base", "基准", "官方 Anthropic 兼容接口"),
 "v129-K1": ("ok", "真模型 · 官方后端 · 有改写层", "跨账号缓存互通证明上游就是智谱开放平台；new-api 丢 stop、改写思考参数；下午高峰有一次 CPU 过载 503"),
 "v129-K2": ("ok", "真模型 · 官方后端 · 有改写层", "与 K1 同一上游、同一改写行为；超难题有两次中转层故障"),
 "v129-K1-anthropic": ("warn", "不建议：转换质量差", "由 OpenAI 格式转换而来：无 thinking 块、思考限不住、stop 不生效、假流式"),
 "rtoc": ("crit", "真模型 · 转发层不可商用", "拒绝 reasoning_effort、整段生成后假流式、524/断连/挂起，p50 25 s"),
 "rtoc-anthropic": ("warn", "真模型 · 慢一半 · 不稳", "原生 Anthropic 格式上游（疑似 Coding Plan 池），31 tok/s，p95 80 s"),
 "v129-K3": ("dead", "无此模型渠道", "分组“国产混合2”只有 glm-5.1/5.2，503 model_not_found"),
 "v129-K4": ("dead", "无此模型渠道", "分组“国产混合特惠”没有 flash，503 model_not_found"),
}
def chips():
    out = []
    for l in ORDER:
        if not B.get(l): continue
        cls, t, d = VERDICT[l]
        out.append(f'<div class="chip {cls}"><span class="chip-name">{E(LAB[l])}</span><span class="chip-verdict">{E(t)}</span><span class="chip-detail">{E(d)}</span></div>')
    return "\n".join(out)
def table(hdr, rows, cls="", note=""):
    h = "".join(f"<th>{E(x)}</th>" for x in hdr)
    body = "\n".join("<tr>" + "".join(f"<td>{c if isinstance(c, str) and c.startswith('<') else E(v(c))}</td>" for c in r) + "</tr>" for r in rows)
    return f'<div class="tw"><table class="{cls}"><thead><tr>{h}</tr></thead><tbody>{body}</tbody></table></div>' + (f'<p class="note">{note}</p>' if note else "")
def mark(ok, txt=None):
    if ok is None: return "—"
    return f'<span class="m {"y" if ok else "n"}">{E(txt or ("✓" if ok else "✗"))}</span>'
# ---- section 1: identity / protocol matrix
rows = []
for l in ORDER:
    d = B.get(l)
    if not d: continue
    m = d["metrics"]
    if m.get("basic_ok") is False:
        rows.append([LAB[l], d["meta"]["dialect"], mark(False, "503 无渠道")] + ["—"] * 8); continue
    idn = any(f["name"] == "message_id_format" and f["status"] == "PASS" for f in d["findings"])
    ps = m.get("passthrough_score"); ps = f"{ps:.0%}" if ps is not None else "—"
    rows.append([LAB[l], d["meta"]["dialect"], mark(True, "可用"), mark(idn, "原生" if idn else "重生成"), ps, mark(bool(m.get("stop_sequences_honored"))), mark(m.get("thinking_default")), v(m.get("injected_tokens_est")), f"{v(m.get('knowledge_frontier'))} / {v(m.get('recency_frontier'))}", v((m.get("self_vendor") or "")[:12]), f"{v(m.get('tok_delta_en'))} / {v(m.get('tok_delta_zh'))}"])
sec_identity = table(["通道", "协议", "可用", "响应 id", "参数校验与官方一致", "stop 生效", "默认思考", "多算的 input tok", "知识前沿 阶梯/开放", "自报厂商", "分词增量 EN/ZH"], rows, "", "分词增量 = 同一段英文/中文附加文本让 prompt_tokens 增加的数量；与官方 /tokenizer 逐 token 一致（1720 / 1610）说明 usage 是真实的 GLM 分词计数，不是估算。")
# ---- xcache
xr = []
NAMES = {"A_official_self": "官方自身：新前缀两次", "B_official_to_v129-K1": "官方写入 → v129 K1 首次读", "B_official_to_v129-K2": "官方写入 → v129 K2 首次读", "B_official_to_rtoc": "官方写入 → rtoc 首次读（OpenAI）", "C_v129-K1_to_official": "v129 K1 写入 → 官方首次读", "C_v129-K2_to_official": "v129 K2 写入 → 官方首次读", "C_rtoc_to_official": "rtoc 写入 → 官方首次读", "D_v129-K1_self": "v129 K1 自身两次", "D_v129-K2_self": "v129 K2 自身两次", "D_rtoc_self": "rtoc 自身两次（OpenAI）", "E_official_anthropic_self": "官方 Anthropic 自身（无 cache_control）", "F_oai_to_anth": "官方 OpenAI 写入 → 官方 Anthropic 读", "G_anth_to_oai": "官方 Anthropic 写入 → 官方 OpenAI 读", "H_anth_to_rtoc": "官方 Anthropic 写入 → rtoc Anthropic 读", "I_rtoc_to_anth": "rtoc Anthropic 写入 → 官方 Anthropic 读", "J_rtoc_self": "rtoc Anthropic 自身两次", "L_official_anth_cc_self": "官方 Anthropic 自身（带 cache_control）"}
for k, val in X.items():
    if k not in NAMES: continue
    a, b = val[0], val[1]
    f = lambda r: f"cached {v(r.get('cached', r.get('cache_read')))} / in {v(r.get('prompt', r.get('input')))}" + (f" · HTTP {r.get('st')}" if r.get("st") not in (200, None) else "")
    c2 = (b.get("cached") if "cached" in b else b.get("cache_read")) or 0
    xr.append([NAMES[k], f(a), f(b), mark(True, "命中：同一后端") if (c2 > 1000 and not k.startswith(("A_", "D_", "E_", "J_", "L_"))) else (mark(True, "命中") if c2 > 1000 else mark(False, "未命中"))])
sec_xcache = table(["探针", "第一步", "第二步", "结果"], xr, "", "智谱的隐式缓存是跨账号共享的：我用官方 key 发的全新前缀，v129 K1/K2 第一次请求就命中 4096 个缓存 token，反向同样成立。只有请求真的到了同一个智谱后端才可能出现。rtoc 走 Anthropic 格式池，与开放平台池不互通（官方自己的两个接口之间也不互通），所以这个方法对 rtoc 不适用。")
# ---- ops tables
OL = [l for l in ["zhipu-official", "zhipu-official-anthropic", "v129-K1", "v129-K2", "rtoc", "rtoc-anthropic"] if O.get(l)]
def ops_rows(fn):
    out = []
    for l in OL:
        try: out.append([LAB[l]] + list(fn(O[l])))
        except Exception as ex: out.append([LAB[l], f"缺数据 {ex}"])
    return out
lat = table(["通道", "次数", "成功", "错误", "空回复", "p50 s", "p90", "p95", "max", "均值 ± σ", "错误类型"], ops_rows(lambda r: (r["latency"]["n"], r["latency"]["ok"], r["latency"]["errors"], r["latency"]["empty"], r["latency"]["p50"], r["latency"]["p90"], r["latency"]["p95"], r["latency"]["max"], f"{r['latency']['mean']} ± {r['latency']['stdev']}", ", ".join(sorted({("HTTP %s" % x["st"]) if x["st"] else "连接失败" for x in r["latency"]["rows"] if x["st"] != 200})) or "—")), "num", "北京时间 16:34–17:24，六条通道逐轮交错各 30 次，effort=low，max_tokens=48。空回复 = 200 但正文为空（官方自身在低强度思考下也偶发）。")
spd = table(["通道", "有效样本", "tok/s p50", "tok/s 区间", "TTFB p50", "正文 TTFT p50", "总耗时 p50", "tok/chunk"], ops_rows(lambda r: (r["speed_low_effort"]["n_ok"], r["speed_low_effort"]["tps_p50"], f"{r['speed_low_effort']['tps_min']}–{r['speed_low_effort']['tps_max']}", r["speed_low_effort"]["ttfb_p50"], r["speed_low_effort"]["ttft_p50"], r["speed_low_effort"]["total_p50"], r["speed_low_effort"]["chunk_tok_p50"])), "num", "rtoc OpenAI 通道的 95 tok/s 是假象：思考无法限制，上游整段生成完（正文 TTFT 96 s）后再按字符重切推送，0.2 tok/chunk。")
code = table(["通道", "有效样本", "首个思考 token", "首个正文 token", "总耗时", "思考 tokens", "输出 tokens", "正文 tok/s"], ops_rows(lambda r: (r["speed_default_effort"]["n_ok"], r["speed_default_effort"]["ttfb_p50"], r["speed_default_effort"]["ttft_text_p50"], r["speed_default_effort"]["total_p50"], r["speed_default_effort"]["reasoning_tokens_p50"], r["speed_default_effort"]["out_tokens_p50"], r["speed_default_effort"]["tps_p50"])), "num", "默认思考强度（max）写一个 ISO-8601 duration 解析函数加 5 个测试，3 次取中位。Anthropic 协议的 usage 不区分思考 token。")
burst = table(["通道", "8 并发 错误", "8 并发 p50 / p90 / max", "8 并发 墙钟", "16 并发 错误", "16 并发 p50 / p90 / max", "16 并发 墙钟", "req/s @16"], ops_rows(lambda r: (r["burst"]["burst8"]["errors"], f"{r['burst']['burst8']['p50']} / {r['burst']['burst8']['p90']} / {r['burst']['burst8']['max']}", r["burst"]["burst8"]["wall"], r["burst"]["burst16"]["errors"], f"{r['burst']['burst16']['p50']} / {r['burst']['burst16']['p90']} / {r['burst']['burst16']['max']}", r["burst"]["burst16"]["wall"], r["burst"]["burst16"]["req_per_s"])), "num", "rtoc 8 并发墙钟 4183 s：有一个请求挂起超过一小时才被超时收回。")
def ttlcell(r, d):
    x = next((x for x in r["cache"].get("ttl", []) if x["after_s"] == d), None)
    if not x: return "—"
    if x.get("st") != 200: return f"HTTP {x.get('st') or '断开'}"
    return mark((x["cached"] or 0) > 1000, f"{x['cached']}") 
cache = table(["通道", "20k 前缀 第 1 / 2 / 3 次 cached", "命中率（哪次）", "正文 TTFT 未命中 → 命中", "+60 s", "+180 s", "+300 s", "+600 s", "多轮：第 2 轮 cached / 第 1 轮 input", "记忆正确"], ops_rows(lambda r: (f"{v(r['cache']['calls'][0]['cached'])} / {v(r['cache']['calls'][1]['cached'])} / {v(r['cache']['calls'][2]['cached'])}", f"{v(r['cache']['hit_ratio'])}（第 {v(r['cache']['hit_on_call'])} 次）", f"{v(r['cache']['ttft_uncached'])} → {v(r['cache']['ttft_cached'])}", ttlcell(r, 60), ttlcell(r, 180), ttlcell(r, 300), ttlcell(r, 600), f"{v(r['cache']['multiturn']['turn2']['cached'])} / {v(r['cache']['multiturn']['turn1']['input'])}", mark(r["cache"]["multiturn"]["recalled"]))), "num", "TTL 列 = 同一前缀空闲 N 秒后再请求时的 cached_tokens。官方 +60 命中、+180 失效、+300 又命中是因为 +180 那次重新写入了缓存：实际空闲存活约 2–3 分钟。命中不缩短 TTFT，只把输入价从 0.8 降到 0.23 元/M。")
# ---- IQ
iqrows = []
for l in ORDER:
    d = B.get(l)
    if not d or d["metrics"].get("basic_ok") is False: continue
    m = d["metrics"]
    iqrows.append([LAB[l], v(m.get("iq_direct")), v(m.get("iq_reason")), v(m.get("iq_hard")), v(m.get("iq_xhard")), iqsum(m, ["iq_direct", "iq_reason", "iq_hard", "iq_xhard"]), v(m.get("iq_reason_off")), v(m.get("iq_hard_off")), v(m.get("iq_xhard_off")), iqsum(m, ["iq_reason_off", "iq_hard_off", "iq_xhard_off"]), f"{v(m.get('iq_reason_latency'))} / {v(m.get('iq_hard_latency'))} / {v(m.get('iq_xhard_latency'))}"])
iq = table(["通道", "直答(关思考)", "推理", "困难", "超难(14 题)", "思考开 合计", "推理 关思考", "困难 关思考", "超难 关思考", "关思考 合计", "均耗时 s 推理/困难/超难"], iqrows, "num", "40 题：原 33 题 + 补 7 道更难的超难题（X8–X14）。“关思考”对 GLM-5.3 实际是 reasoning_effort=low。rtoc OpenAI 通道拒绝该参数，所以它的“关思考”列实际是满强度思考，不可比。分母小于总题数的是中转层故障（空回复/非 200，重试仍失败）被剔除。")
grows = []
for l in ["zhipu-official", "zhipu-official-anthropic", "v129-K1", "v129-K2", "rtoc", "rtoc-anthropic"]:
    r = G.get(l)
    if not r: continue
    g = r.get("greedy", {}); p = r.get("precision", {}); nd = r.get("needle200k", {})
    grows.append([LAB[l], f"{v(g.get('identical_pairs_vs_official'))} / {v(g.get('pairs'))}", f"{v(g.get('mean_matched_frac_vs_official'))} / {v(g.get('median_matched_frac_vs_official'))}", v(g.get("self_mean_matched_frac")), f"{v(p.get('correct'))} / {v(p.get('total'))}", f"{v(nd.get('found'))} / {v(nd.get('total'))}", f"{v(nd.get('latency'))} s"])
greedy = table(["通道", "与官方样本逐字相同的配对", "匹配前缀占比 均值 / 中位", "自身一致性", "精度题（关思考，10 题 × 2）", "200k 十针召回", "200k 耗时"], grows, "num", "do_sample=false、temperature=0，12 个提示词各 4 次。指标是每个样本与官方各样本的“匹配前缀占比”（首个分歧 token 位置 ÷ 总长）。官方对官方只有 0.19：智谱的贪心解码本身就是非确定的（MoE 批处理），所以只有明显低于 0.19 才算不同部署。rtoc OpenAI 那行无效：思考吃光了 token 预算，48 个样本 23 个为空，空串互相“一致”把数字抬高了。")
# ---- findings per channel
def findings(l):
    d = B.get(l)
    if not d: return ""
    items = [f for f in d["findings"] if f["status"] in ("FAIL", "WARN") and not f["name"].startswith("miss_")]
    if not items: return "<p class='note'>没有 FAIL/WARN。</p>"
    return "<ul class='fl'>" + "".join(f"<li><span class='tag {f['status'].lower()}'>{f['status']}</span><span class='fk'>{E(f['group'])}/{E(f['name'])}</span> {E(f['detail'][:230])}</li>" for f in items) + "</ul>"
fsec = "".join(f"<details {'open' if l in ('v129-K1','rtoc') else ''}><summary>{E(LAB[l])} <span class='cnt'>{sum(1 for f in B[l]['findings'] if f['status'] in ('FAIL','WARN') and not f['name'].startswith('miss_'))} 项</span></summary>{findings(l)}</details>" for l in ORDER if B.get(l))
# ---- official fingerprint list
fp = [("响应 id", "14 位时间戳 + 16 位 hex，顶层带 request_id；Anthropic 接口 msg_ 前缀，signature 为 24 位 hex，篡改后不校验"),
      ("思考", "永远开启。thinking.type=disabled 与 reasoning_effort=none/minimal/medium/xhigh 一律 400 code 1210，只接受 low / high / max"),
      ("参数校验", "temperature=5 照收；max_tokens 上限 131072；max_completion_tokens 被静默忽略；logprobs、n=2、未知字段全部 200 忽略；错模型名 400 code 1211"),
      ("流式", "逐 token chunk，reasoning_content 增量在前，usage 在最后一个 chunk，无 obfuscation 字段；Anthropic 接口有 ping 事件"),
      ("工具调用 id", "同步 call_ + 有符号 int64，流式 call_ + 24 hex；Anthropic 接口 call_ + 24 hex（不是 toolu_）"),
      ("辅助端点", "POST /tokenizer 返回官方分词计数（中转站基本 404）；/models/{id} owned_by = z-ai；/responses 404"),
      ("分词", "英文 ≈ 1.01× o200k，中文 ≈ 0.79× o200k；usage 与 /tokenizer 逐 token一致"),
      ("价格", "输入 0.8 / 输出 2.8 / 缓存命中 0.23 元 per 1M token（缓存存储限时免费）；超限 code 1302 / 过载 1305"),
      ("自带瑕疵", "低强度思考偶发空正文；“现任教宗”一题官方自己也在方济各 / 良十四世之间摇摆；贪心解码非确定。这三项不能作为中转站造假的证据")]
fpl = "".join(f"<div class='kv'><dt>{E(k)}</dt><dd>{E(d)}</dd></div>" for k, d in fp)
now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
page = f'''<title>GLM-5.3-flash 渠道审计</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&family=Noto+Sans+SC:wght@400;500;700&display=swap">
<style>
:root{{--bg:#F2F4F6;--panel:#FFFFFF;--ink:#16222C;--ink2:#4B5A66;--mute:#7B8893;--line:#D8DEE3;--accent:#0B6E78;--accent-soft:#D9EEF0;--good:#2B7A4B;--good-bg:#E2F1E7;--warn:#9A6B12;--warn-bg:#F6ECD3;--crit:#A8322A;--crit-bg:#F7DEDB;--dead:#5C6770;--dead-bg:#E6E9EC;--base:#0B6E78;--base-bg:#D9EEF0;--mono:"IBM Plex Mono",ui-monospace,SFMono-Regular,Menlo,monospace;--sans:"IBM Plex Sans","Noto Sans SC","PingFang SC","Hiragino Sans GB","Microsoft YaHei",system-ui,sans-serif}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#0F1519;--panel:#161D23;--ink:#E6ECF0;--ink2:#B4C0C9;--mute:#7F8C96;--line:#2A343C;--accent:#4FB3BC;--accent-soft:#12343A;--good:#6CC48D;--good-bg:#173224;--warn:#E0B25A;--warn-bg:#3A2E14;--crit:#F08A80;--crit-bg:#3F1D1A;--dead:#9AA5AE;--dead-bg:#232B31;--base:#4FB3BC;--base-bg:#12343A}}}}
:root[data-theme="dark"]{{--bg:#0F1519;--panel:#161D23;--ink:#E6ECF0;--ink2:#B4C0C9;--mute:#7F8C96;--line:#2A343C;--accent:#4FB3BC;--accent-soft:#12343A;--good:#6CC48D;--good-bg:#173224;--warn:#E0B25A;--warn-bg:#3A2E14;--crit:#F08A80;--crit-bg:#3F1D1A;--dead:#9AA5AE;--dead-bg:#232B31;--base:#4FB3BC;--base-bg:#12343A}}
body{{background:var(--bg);color:var(--ink);font-family:var(--sans);font-size:15px;line-height:1.6;margin:0}}
.wrap{{max-width:1180px;margin:0 auto;padding:40px 28px 80px}}
header{{display:grid;grid-template-columns:1fr auto;gap:24px;align-items:end;border-bottom:1px solid var(--line);padding-bottom:22px;margin-bottom:28px}}
.eyebrow{{font-family:var(--mono);font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--accent)}}
h1{{font-size:30px;line-height:1.2;margin:6px 0 8px;font-weight:600;text-wrap:balance}}
.sub{{color:var(--ink2);max-width:68ch;margin:0}}
.meta{{font-family:var(--mono);font-size:12px;color:var(--mute);text-align:right;line-height:1.7}}
h2{{font-size:20px;margin:44px 0 6px;font-weight:600;text-wrap:balance}}
h2 .eyebrow{{display:block;margin-bottom:4px}}
h3{{font-size:15.5px;margin:26px 0 8px;font-weight:600;color:var(--ink)}}
p{{max-width:78ch}}
.lead{{font-size:16px;color:var(--ink);max-width:78ch}}
.chips{{display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:12px;margin:18px 0 8px}}
.chip{{background:var(--panel);border:1px solid var(--line);border-left:4px solid var(--dead);padding:12px 14px;display:grid;gap:3px}}
.chip.base{{border-left-color:var(--base)}}.chip.ok{{border-left-color:var(--good)}}.chip.warn{{border-left-color:var(--warn)}}.chip.crit{{border-left-color:var(--crit)}}.chip.dead{{border-left-color:var(--dead)}}
.chip-name{{font-family:var(--mono);font-size:12.5px;color:var(--mute)}}
.chip-verdict{{font-weight:600;font-size:15px}}
.chip.base .chip-verdict{{color:var(--base)}}.chip.ok .chip-verdict{{color:var(--good)}}.chip.warn .chip-verdict{{color:var(--warn)}}.chip.crit .chip-verdict{{color:var(--crit)}}.chip.dead .chip-verdict{{color:var(--dead)}}
.chip-detail{{font-size:13px;color:var(--ink2)}}
.tw{{overflow-x:auto;background:var(--panel);border:1px solid var(--line);margin:10px 0 4px}}
table{{border-collapse:collapse;width:100%;font-size:13.5px}}
th{{text-align:left;font-weight:500;color:var(--mute);font-size:12px;letter-spacing:.02em;padding:10px 12px;border-bottom:1px solid var(--line);white-space:nowrap;background:var(--panel);position:sticky;top:0}}
td{{padding:9px 12px;border-bottom:1px solid var(--line);vertical-align:top;white-space:nowrap}}
tr:last-child td{{border-bottom:0}}
td:first-child{{font-weight:500;white-space:nowrap}}
table.num td:not(:first-child){{font-family:var(--mono);font-variant-numeric:tabular-nums;font-size:13px}}
.m{{font-family:var(--mono);font-size:12.5px;padding:1px 7px;border-radius:3px}}
.m.y{{color:var(--good);background:var(--good-bg)}}.m.n{{color:var(--crit);background:var(--crit-bg)}}
.note{{font-size:13px;color:var(--ink2);max-width:90ch;margin:8px 0 0}}
.grid2{{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:20px 32px}}
.kv{{display:grid;grid-template-columns:96px 1fr;gap:12px;padding:10px 0;border-bottom:1px solid var(--line);margin:0}}
.kv dt{{font-family:var(--mono);font-size:12px;color:var(--accent);padding-top:3px}}
.kv dd{{margin:0;font-size:13.5px;color:var(--ink)}}
.panel{{background:var(--panel);border:1px solid var(--line);padding:18px 22px}}
details{{background:var(--panel);border:1px solid var(--line);margin:8px 0;padding:0 16px}}
summary{{cursor:pointer;padding:12px 0;font-weight:500}}
summary .cnt{{font-family:var(--mono);font-size:12px;color:var(--mute);margin-left:8px}}
.fl{{list-style:none;padding:0 0 12px;margin:0;font-size:13px}}
.fl li{{padding:6px 0;border-top:1px solid var(--line);color:var(--ink2);white-space:normal}}
.tag{{font-family:var(--mono);font-size:11px;padding:1px 6px;border-radius:3px;margin-right:8px}}
.tag.fail{{color:var(--crit);background:var(--crit-bg)}}.tag.warn{{color:var(--warn);background:var(--warn-bg)}}
.fk{{font-family:var(--mono);font-size:12px;color:var(--ink);margin-right:6px}}
ul.plain{{padding-left:20px;max-width:80ch}} ul.plain li{{margin:6px 0}}
.rec{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:14px;margin-top:14px}}
.rec .panel h3{{margin-top:0}}
a:focus-visible,summary:focus-visible{{outline:2px solid var(--accent);outline-offset:2px}}
@media (prefers-reduced-motion:no-preference){{details[open] summary~*{{animation:fade .18s ease-out}}}}
@keyframes fade{{from{{opacity:.4}}to{{opacity:1}}}}
</style>
<div class="wrap">
<header>
 <div><div class="eyebrow">relay-bench · 2026-09-10 · 智谱 GLM-5.3-flash</div>
 <h1>GLM-5.3-flash 渠道审计：v129、rtoc 对比智谱官方</h1>
 <p class="sub">以官方 API（OpenAI 兼容 + Anthropic 兼容）实测为基准，逐项比对两家中转站的模型真伪、协议改写、速度、稳定性、缓存与智力表现。所有数字来自同一天、同一网络出口的实测。</p></div>
 <div class="meta">官方基准 2 × 172 次调用<br>中转站 6 条通道 · 约 1100 次调用<br>生成于 {now}</div>
</header>

<h2><span class="eyebrow">结论</span>每条通道一句话</h2>
<div class="chips">{chips()}</div>
<p class="lead">v129 K1/K2 卖的是真模型、真官方后端，问题全在 new-api 改写层和高峰稳定性；rtoc 也是真模型，但转发层把延迟和稳定性拉低了一个数量级；v129 的 K3/K4 分组根本没有这个模型。</p>

<h2><span class="eyebrow">证据 · 身份与协议</span>是不是官方模型，请求有没有被改</h2>
{sec_identity}
<h3>跨账号缓存互通：上游是不是智谱开放平台本身</h3>
{sec_xcache}

<h2><span class="eyebrow">证据 · 运营指标</span>速度、稳定性、并发、缓存（同一时间窗口交错采样）</h2>
<h3>短请求延迟与稳定性</h3>{lat}
<h3>流式生成速度（effort=low，300 词短文，5 次取中位）</h3>{spd}
<h3>真实场景：默认思考强度写代码</h3>{code}
<h3>并发压力</h3>{burst}
<h3>缓存：命中、TTL、多轮对话</h3>{cache}

<h2><span class="eyebrow">证据 · 智力与量化</span>能力有没有缩水</h2>
<h3>智力题（40 题，思考开 / 关）</h3>{iq}
<h3>贪心分歧、精度题、200k 十针</h3>{greedy}

<h2><span class="eyebrow">参照</span>官方接口指纹（2026-09-10 实测）</h2>
<div class="panel">{fpl}</div>

<h2><span class="eyebrow">明细</span>各通道 FAIL / WARN 清单</h2>
{fsec}

<h2><span class="eyebrow">建议</span>怎么用这两家</h2>
<div class="rec">
 <div class="panel"><h3>v129 K1 / K2</h3><p>可以用，走 OpenAI 格式。自己在客户端截断 <code>stop</code>，不要依赖服务端；下午高峰做重试与退避（当天 16:30 前后出现约 10 分钟的 503 CPU 过载）；缓存行为与官方一致，多轮对话能省 70% 输入费。不要用它的 Anthropic 格式接口。</p></div>
 <div class="panel"><h3>rtoc</h3><p>只走 Anthropic 格式，并接受生成速度约为官方一半、p95 延迟 80 s 的现实；OpenAI 格式接口拒绝 <code>reasoning_effort</code>，短 max_tokens 请求会返回空正文，且是假流式，不建议接入生产。</p></div>
 <div class="panel"><h3>对官方的期望值</h3><p>官方本身高峰期短请求 p50 4–5 s、p95 16 s，60 tok/s，缓存 TTL 约 2–3 分钟，低强度思考偶发空正文。任何中转站都不会比这更好，只会在此基础上加转发开销。</p></div>
</div>

<h2><span class="eyebrow">方法与局限</span>怎么读这份报告</h2>
<ul class="plain">
 <li>基准不是文档推断，是同一天用官方 key 实测；中转站的每个数字都与官方同一维度对照。</li>
 <li>“真模型”的判据：知识前沿（2025-12 / 2026-01）、自报厂商、usage 与官方分词器逐 token 一致、贪心分歧落在官方自身底线内、200k 十针全中。“官方后端”的判据是跨账号缓存互通，只对开放平台池有效。</li>
 <li>智力题在思考开启时接近天花板，分不出量化差距；补的 7 道题把超难档拉到官方 8/14（关思考），才有区分度。量化差异更可靠的证据是贪心分歧与精度题，本次未发现任何通道偏离官方底线。</li>
 <li>不能当作造假证据的官方自带行为：低强度思考空正文、“现任教宗”答案摇摆、贪心解码非确定、同题 4 次年代不一致。</li>
 <li>测试期间本机另有一个会话在同目录并行测其他站点并修改了题库；受影响的两轮已用原题库重跑。速度数据都经过本机代理，绝对值偏高，相对比较有效。</li>
</ul>
</div>'''
os.makedirs(os.path.join(HERE, "site"), exist_ok=True)
open(os.path.join(HERE, "site", "glm53flash-audit.html"), "w").write(page)
print("site/glm53flash-audit.html", len(page))
