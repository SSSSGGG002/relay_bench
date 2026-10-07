#!/usr/bin/env python3
"""costcheck: run one fixed workload per Claude model and reconcile what the relay actually charged.

A low price multiplier says little when the relay injects a hidden prompt and reports a fixed 70-80 %
"cache hit" split: every request is billed for tokens you never sent. This script sends the same
deterministic workload to every relay, matches each call to the relay's own bill (new-api
/api/log/token, by x-oneapi-request-id) and reports what the workload cost in station dollars.
Multiply by your own top-up price (CNY per station dollar) to compare relays.

  RB_KEY=sk-... python3 costcheck.py --label ikun-ccrev --base https://api.ikuncode.cc \\
      --models claude-sonnet-5,claude-opus-5-5 [--sections inject,fresh,session,iq] [--direct]
  python3 costcheck.py --report results/costcheck/<label>.json      # rebuild the markdown table

Sections (content is identical on every relay for a given WORKLOAD version; a per-run nonce header keeps it out of earlier caches)
  inject   "Reply with exactly: OK" x3                       -> billed input for a ~10-token prompt
  fresh    brand-new documents of ~3k and ~12k o200k tokens, no cache_control, x1 each
           -> a fresh document cannot be cached: any cache_read on it beyond the injected
              overhead is a fabricated split; the slope of billed input vs o200k size gives the
              relay's tokens-per-o200k ratio, the intercept the per-request injection
  session  Claude Code style: system = CC identity + ~12k-token document with cache_control,
           5 user turns, history carried over                -> the realistic agent workload
  iq       the 8 screen IQ items (suite/iq_screen.json), default thinking, max_tokens 16000

"Ideal" cost = the station's own published formula applied to what was actually sent (relay ratio
x o200k size, no injection, perfect prompt caching in the session, reported output tokens).
actual / ideal is how much injection and the cache split inflate the bill over the nominal ratio.
"""
import argparse, concurrent.futures as cf, datetime, json, os, random, sys, threading, time
import httpx

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from bench import final_answer, match_answer  # noqa: E402

try:
    import tiktoken
    ENC = tiktoken.get_encoding("o200k_base")
except Exception:
    ENC = None
CORPUS = os.path.join(HERE, "suite", "corpus", "natural.txt")
CC_IDENT = "You are Claude Code, Anthropic's official CLI for Claude."
OK_PROMPT = "Reply with exactly: OK"
IQ_SUFFIX = "\n\nThink it through carefully. Your final line must be exactly:\nANSWER: <your final answer>"
SESSION_Q = ["Read the document above. In one sentence, what is it mainly about?",
             "Name three specific relay stations or products the document mentions.",
             "Quote one number that appears in the document and say what it measures.",
             "In two sentences, what is the most serious problem the document reports?",
             "Give a one-line title for the document."]
LOCK = threading.Lock()
WORKLOAD = "costcheck-v1"   # document content is fixed per workload version so every relay gets identical text; only the nonce header differs


def o200k(s): return len(ENC.encode(s)) if ENC else max(1, len(s) // 4)


def doc(seed, n_tok):
    """Deterministic slice of the natural-text corpus, cut to ~n_tok o200k tokens."""
    c = open(CORPUS, encoding="utf-8").read()
    off = random.Random(seed).randrange(len(c) // 2)
    s = c[off:off + n_tok * 3]
    while o200k(s) < n_tok: s += c[:n_tok]
    ids = ENC.encode(s)[:n_tok] if ENC else None
    return ENC.decode(ids) if ids else s[:n_tok * 4]


class Relay:
    def __init__(self, a):
        self.base = a.base.rstrip("/"); self.key = a.key; self.direct = a.direct
        self.c = httpx.Client(base_url=self.base, timeout=httpx.Timeout(900, connect=30), trust_env=not a.direct,
                              headers={"x-api-key": a.key, "authorization": "Bearer " + a.key, "anthropic-version": "2023-06-01",
                                       "content-type": "application/json", "user-agent": a.ua})

    def call(self, body, tag, model):
        """Streamed /v1/messages call; returns usage, text, request id and timings."""
        t0 = time.time(); rec = dict(tag=tag, model=model, t0=t0, status=0, text="", usage={}, rid=None, msg_id=None, ttft=None, err="")
        for attempt in range(3):
            try:
                with self.c.stream("POST", "/v1/messages", json={**body, "model": model, "stream": True}) as r:
                    rec["status"] = r.status_code; rec["rid"] = r.headers.get("x-oneapi-request-id") or r.headers.get("request-id")
                    if r.status_code != 200:
                        rec["err"] = r.read().decode(errors="replace")[:300]
                    else:
                        for line in r.iter_lines():
                            if not line.startswith("data:"): continue
                            try: ev = json.loads(line[5:].strip())
                            except Exception: continue
                            t = ev.get("type")
                            if t == "message_start":
                                m = ev.get("message") or {}; rec["msg_id"] = m.get("id"); rec["usage"].update(m.get("usage") or {})
                            elif t == "content_block_delta":
                                d = ev.get("delta") or {}
                                if rec["ttft"] is None: rec["ttft"] = round(time.time() - t0, 2)
                                if d.get("type") == "text_delta": rec["text"] += d.get("text", "")
                            elif t == "message_delta":
                                rec["usage"].update({k: v for k, v in (ev.get("usage") or {}).items() if v is not None})
            except Exception as e:
                rec["err"] = f"{type(e).__name__}: {str(e)[:200]}"
            if rec["status"] == 200 and not rec["err"]: break
            if rec["status"] in (400, 401, 403, 404): break
            time.sleep(5)
        rec["el"] = round(time.time() - t0, 2)
        return rec

    def logs(self):
        try:
            j = self.c.get("/api/log/token").json()
            return {x["request_id"]: x for x in j.get("data") or []}
        except Exception as e:
            print("log fetch failed:", e); return {}

    def total_usage(self):
        try: return self.c.get("/v1/dashboard/billing/usage").json().get("total_usage")
        except Exception: return None


def run_model(R, model, sections, nonce, out):
    recs = []
    def keep(r, **kw):
        r.update(kw); recs.append(r)
        with LOCK:
            u = r["usage"]
            print(f"  {model:28s} {r['tag']:10s} {r['status']} in={u.get('input_tokens')} cr={u.get('cache_read_input_tokens')} "
                  f"cw={u.get('cache_creation_input_tokens')} out={u.get('output_tokens')} {r['el']}s {r['err'][:80]}", flush=True)
    if "inject" in sections:
        for i in range(3):
            keep(R.call({"max_tokens": 64, "messages": [{"role": "user", "content": OK_PROMPT}]}, "inject", model), sent=o200k(OK_PROMPT))
    if "fresh" in sections:
        for n in (3000, 12000):
            d = f"[doc {nonce}-{model}-fresh{n}]\n" + doc(f"{WORKLOAD}-fresh{n}", n)
            q = d + "\n\nIn one sentence, what is the document above about?"
            keep(R.call({"max_tokens": 300, "messages": [{"role": "user", "content": q}]}, f"fresh{n // 1000}k", model), sent=o200k(q))
    if "session" in sections:
        d = f"[doc {nonce}-{model}-session]\n" + doc(f"{WORKLOAD}-session", 12000)
        system = [{"type": "text", "text": CC_IDENT}, {"type": "text", "text": d, "cache_control": {"type": "ephemeral"}}]
        sys_tok = o200k(CC_IDENT) + o200k(d); msgs = []; hist_tok = 0
        for i, q in enumerate(SESSION_Q):
            msgs.append({"role": "user", "content": q}); hist_tok += o200k(q)
            r = R.call({"max_tokens": 1000, "system": system, "messages": msgs}, f"session{i + 1}", model)
            keep(r, sent=sys_tok + hist_tok, sys_tok=sys_tok, turn=i + 1)
            a = r["text"] or "(no answer)"
            msgs.append({"role": "assistant", "content": a}); hist_tok += o200k(a)
            time.sleep(2)
    if "iq" in sections:
        bank = {it["id"]: it for it in json.load(open(os.path.join(HERE, "suite", "iq.json")))["items"]}
        ids = json.load(open(os.path.join(HERE, "suite", "iq_screen.json")))
        def one(i):
            p = bank[i]["q"] + IQ_SUFFIX
            r = R.call({"max_tokens": 16000, "messages": [{"role": "user", "content": p}]}, f"iq:{i}", model)
            got = final_answer(r["text"]) if r["text"].strip() else None
            r["correct"] = bool(got) and match_answer(got, bank[i]["ans"], bank[i].get("kind")); r["answer"] = got
            return r, o200k(p)
        with cf.ThreadPoolExecutor(4) as ex:
            for r, s in ex.map(one, ids): keep(r, sent=s)
    out[model] = recs


def attach_bills(R, data, wait=20):
    """Match every call to the relay's bill by request id (logs can lag a few seconds)."""
    want = {r["rid"] for recs in data["models"].values() for r in recs if r.get("rid")}
    bills = {}
    for _ in range(6):
        time.sleep(wait if not bills else 10)
        bills = R.logs()
        if want <= set(bills): break
    for recs in data["models"].values():
        for r in recs:
            b = bills.get(r.get("rid"))
            if not b: r["bill"] = None; continue
            o = json.loads(b.get("other") or "{}")
            r["bill"] = dict(quota=b["quota"], prompt=b["prompt_tokens"], completion=b["completion_tokens"], cache_read=o.get("cache_tokens", 0),
                             cache_write=o.get("cache_creation_tokens", 0), model_ratio=o.get("model_ratio"), completion_ratio=o.get("completion_ratio"),
                             cache_ratio=o.get("cache_ratio"), cache_creation_ratio=o.get("cache_creation_ratio", 1.25), group_ratio=o.get("group_ratio"),
                             group=b.get("group"), channel=b.get("channel"), use_time=b.get("use_time"))


def billed_in(b): return b["prompt"] + b["cache_read"] + b["cache_write"]


def analyse(data, qpd):
    rows = []
    for model, recs in data["models"].items():
        billed = [r for r in recs if r.get("bill")]
        if not billed: rows.append(dict(model=model, n=len(recs), billed=0)); continue
        b0 = billed[0]["bill"]; ratio = dict(m=b0["model_ratio"], c=b0["completion_ratio"], cr=b0["cache_ratio"], cw=b0["cache_creation_ratio"], g=b0["group_ratio"])
        # relay tokens per o200k token and per-request injection, from the inject + fresh calls (sizes ~10 / 3k / 12k)
        pts = [(r["sent"], billed_in(r["bill"])) for r in billed if r["tag"] in ("inject", "fresh3k", "fresh12k")]
        slope = icpt = None
        big = [p for p in pts if p[0] > 1000]
        if len(big) >= 2:
            (x1, y1), (x2, y2) = big[0], big[-1]
            slope = (y2 - y1) / (x2 - x1) if x2 != x1 else None
        inj = [billed_in(r["bill"]) - r["sent"] * (slope or 1) for r in billed if r["tag"] == "inject"]
        icpt = sorted(inj)[len(inj) // 2] if inj else None
        tr = slope or 1.0
        def q_of(p, cr, cw, c): return (p + cr * ratio["cr"] + cw * ratio["cw"] + c * ratio["c"]) * ratio["m"] * ratio["g"]
        sec = {}
        prev_prefix = 0
        for r in sorted(billed, key=lambda r: r["t0"]):
            b = r["bill"]; s = r["tag"].split(":")[0].rstrip("0123456789k") or r["tag"]
            s = {"fresh": "fresh", "session": "session", "inject": "inject", "iq": "iq"}.get(s, s)
            sent = r["sent"] * tr
            if r["tag"].startswith("session"):   # ideal: system written once, then read; each turn writes only its increment
                if r["turn"] == 1: ideal = q_of(0, 0, sent, b["completion"]); prev_prefix = sent
                else: ideal = q_of(0, prev_prefix, sent - prev_prefix, b["completion"]); prev_prefix = sent
            else:
                ideal = q_of(sent, 0, 0, b["completion"])
            a = sec.setdefault(s, dict(n=0, quota=0, ideal=0, sent=0, p=0, cr=0, cw=0, c=0))
            a["n"] += 1; a["quota"] += b["quota"]; a["ideal"] += ideal; a["sent"] += sent
            a["p"] += b["prompt"]; a["cr"] += b["cache_read"]; a["cw"] += b["cache_write"]; a["c"] += b["completion"]
        fresh_cr = [r["bill"]["cache_read"] for r in billed if r["tag"].startswith("fresh")]
        iq = [r for r in recs if r["tag"].startswith("iq:")]
        tot_q = sum(v["quota"] for v in sec.values()); tot_i = sum(v["ideal"] for v in sec.values())
        tot_in = sum(v["p"] + v["cr"] + v["cw"] for v in sec.values())
        rows.append(dict(model=model, n=len(recs), billed=len(billed), ratio=ratio, slope=slope, inject=icpt, fresh_cache_read=fresh_cr,
                         sections=sec, quota=tot_q, usd=tot_q / qpd, ideal_usd=tot_i / qpd, inflation=(tot_q / tot_i if tot_i else None),
                         hit=(sum(v["cr"] for v in sec.values()) / tot_in if tot_in else None),
                         iq=f"{sum(r.get('correct', False) for r in iq)}/{len(iq)}" if iq else "",
                         errors=sum(1 for r in recs if r["status"] != 200 or r["err"]),
                         groups=sorted({r["bill"]["group"] for r in billed}), channels=sorted({r["bill"]["channel"] for r in billed})))
    return rows


def md(data, rows, ref=None):
    m = data["meta"]
    refm = {r["model"]: r for r in (ref or {}).get("models", [])}
    L = [f"# costcheck · {m['label']}（{m['started']}）", "",
         f"base `{m['base']}` · 路线 {m['route']} · 负载 {', '.join(m['sections'])} · nonce `{m['nonce']}`", "",
         f"站内总用量变化 $（/v1/dashboard/billing/usage ÷ 100，同一把 key 的其他使用也会算进来）：{m.get('usage_delta')}", "",
         "金额单位是**站内美元**（quota ÷ 500000）。乘上你的充值价（元 / 站内美元）就是实际花费。", "",
         "| 模型 | 分组·渠道 | 实扣 $ | 理想 $ | 实扣/理想 | 报告缓存命中 | 每请求注入 token | 分词比（相对 o200k） | 新文档的 cache_read | IQ | 错误 | 你的价格 元/$ | 实际花费 元 |"
         + (f" 参考 {ref['name']} 实扣 $ | 参考的价格 元/$ | 参考实际花费 元 |" if ref else ""),
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|" + ("---|---|---|" if ref else "")]
    for r in rows:
        if not r.get("billed"): L.append(f"| {r['model']} | 无账单 | | | | | | | | | | | |"); continue
        L.append(f"| {r['model']} | {'/'.join(r['groups'])}·{'/'.join(map(str, r['channels']))} | {r['usd']:.4f} | {r['ideal_usd']:.4f} | "
                 f"{r['inflation']:.2f}× | {r['hit'] * 100:.0f}% | {r['inject']:.0f} | {r['slope'] or 0:.2f} | {r['fresh_cache_read']} | {r['iq']} | {r['errors']} | | |"
                 + (f" {refm[r['model']]['usd']:.4f} | | |" if r["model"] in refm else (" — | | |" if ref else "")))
    L += ["", "## 分段明细（站内美元；token 是站点账单里的数）", "",
          "| 模型 | 段 | 次数 | 实扣 $ | 理想 $ | 发送 token（换算后） | 计费 input | cache_read | cache_write | output |", "|---|---|---|---|---|---|---|---|---|---|"]
    qpd = data["meta"]["quota_per_usd"]
    for r in rows:
        for s, v in (r.get("sections") or {}).items():
            L.append(f"| {r['model']} | {s} | {v['n']} | {v['quota'] / qpd:.4f} | {v['ideal'] / qpd:.4f} | {v['sent']:.0f} | {v['p']} | {v['cr']} | {v['cw']} | {v['c']} |")
    L += ["", "读法：",
          "- **实扣/理想** ≈ 1：按站点标价诚实计费。明显大于 1：注入和缓存拆分在加价，倍率再低也要按这个系数折算。",
          "- **新文档的 cache_read** 应为 0（或只等于注入部分）。新文档也报大比例命中 = 缓存数字是拆出来的，不是真命中。",
          "- **每请求注入** = 一句 OK 的计费输入减去实际发送量。几十 token 是协议转换；几千 token 是号池的隐藏系统提示。",
          "- 理想值按站点自己的公式算：系统文档写入一次、后续轮次读取，输出 token 用站点报告的数（输出无法独立核实）。"]
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--label"); ap.add_argument("--base"); ap.add_argument("--key", default=os.environ.get("RB_KEY"))
    ap.add_argument("--models", default="claude-sonnet-5"); ap.add_argument("--sections", default="inject,fresh,session,iq")
    ap.add_argument("--direct", action="store_true", help="ignore HTTPS_PROXY"); ap.add_argument("--route", default=os.environ.get("RB_ROUTE", "unspecified"))
    ap.add_argument("--ua", default="claude-cli/2.1.278 (external, cli)"); ap.add_argument("--quota-per-usd", type=float, default=500000)
    ap.add_argument("--parallel", type=int, default=3, help="models run in parallel")
    ap.add_argument("--report", help="rebuild markdown from an existing results json")
    ap.add_argument("--ref", help="frozen cost reference (suite/reference/*-cost.json) to show side by side")
    ap.add_argument("--freeze", help="with --report: write the run as a frozen cost reference to this path")
    a = ap.parse_args()
    if a.report:
        data = json.load(open(a.report)); rows = analyse(data, data["meta"]["quota_per_usd"])
        if a.freeze:
            keep = ("model", "usd", "ideal_usd", "inflation", "hit", "inject", "slope", "fresh_cache_read", "iq", "errors", "groups", "channels", "ratio", "sections")
            ref = dict(name=os.path.basename(a.freeze).replace(".json", ""), kind="claude-cost", workload=data["meta"].get("workload"), base=data["meta"]["base"],
                       key_hint=data["meta"].get("key_hint"), measured_at=data["meta"]["started"], route=data["meta"]["route"], source=os.path.relpath(a.report, HERE),
                       quota_per_usd=data["meta"]["quota_per_usd"], usage_delta=data["meta"].get("usage_delta"),
                       models=[{k: r.get(k) for k in keep} for r in rows])
            json.dump(ref, open(a.freeze, "w"), ensure_ascii=False, indent=1); print("frozen ->", a.freeze); return
        text = md(data, rows, json.load(open(a.ref)) if a.ref else None)
        open(a.report.replace(".json", ".md"), "w").write(text + "\n"); print(text); return
    if not (a.label and a.base and a.key): ap.error("--label, --base and RB_KEY/--key are required")
    R = Relay(a); nonce = f"{random.randrange(16**8):08x}"; sections = a.sections.split(",")
    data = dict(meta=dict(workload=WORKLOAD, label=a.label, base=a.base, route=a.route, sections=sections, nonce=nonce, quota_per_usd=a.quota_per_usd,
                          started=datetime.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %z"), key_hint=a.key[:6] + "…" + a.key[-4:]), models={})
    u0 = R.total_usage()
    with cf.ThreadPoolExecutor(a.parallel) as ex:
        list(ex.map(lambda m: run_model(R, m, sections, nonce, data["models"]), a.models.split(",")))
    attach_bills(R, data)
    u1 = R.total_usage(); data["meta"]["usage_delta"] = round((u1 - u0) / 100, 4) if (u0 is not None and u1 is not None) else None
    os.makedirs(os.path.join(HERE, "results", "costcheck"), exist_ok=True)
    fn = os.path.join(HERE, "results", "costcheck", f"{a.label}.json")
    json.dump(data, open(fn, "w"), ensure_ascii=False, indent=1)
    rows = analyse(data, a.quota_per_usd); text = md(data, rows, json.load(open(a.ref)) if a.ref else None)
    open(fn.replace(".json", ".md"), "w").write(text + "\n"); print(text); print("->", fn)


if __name__ == "__main__":
    main()
