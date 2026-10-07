#!/usr/bin/env python3
"""gptcheck: GPT relay baseline — injection, cache, billing reconciliation, latency p50/p99, soak. No IQ.

Speaks both OpenAI dialects (/v1/chat/completions and /v1/responses), because Codex-pool relays
often hide the injected instructions on one path and bill them on the other.

  RB_KEY=sk-... python3 gptcheck.py run --label spatial-20261007 --base https://spatialai.vip \\
      --models gpt-5.6-sol,gpt-5.6-terra,gpt-6-astra --sections inject,params,cache,ttl,session,lat [--proxy]
  RB_KEY=sk-... python3 gptcheck.py run --label spatial-20261007 ... --sections soak --soak-min 30
  python3 gptcheck.py report --label spatial-20261007            # -> results/gptcheck/<label>/REPORT.md
  python3 gptcheck.py freeze --label spatial-20261007 --name <ref-name>   # -> suite/reference/<ref-name>.json

Billing: on sub2api-style gateways GET /v1/usage returns per-model running totals (requests, input,
cache_read, cache_write, output, cost, actual_cost). Each section of one model runs sequentially and
is bracketed by two snapshots, so the delta is exactly what that section was billed (models run in
parallel; their stats are separate). Gateways without it: billing columns stay empty.

Sections (documents are identical on every relay for one WORKLOAD version; a nonce header line keeps
them out of earlier caches)
  inject   "Reply with exactly: OK" x3 on chat and x3 on responses: reported vs billed input; the
           responses path echoes `instructions` and per-field token attribution
  params   temperature 5, max_completion_tokens 16, max_tokens 16, invalid reasoning_effort, stop,
           prompt_cache_key echo                     -> are client parameters passed through?
  cache    ~12k-token document x3 (same) then a fresh one, on chat and on responses
  ttl      one document per gap (30/120/300/600 s): write, idle, re-read  -> cache lifetime
  session  agent-style 5 turns on chat, system = ~12k-token document, history carried over
  lat      streamed "OK" calls: N sequential + W waves x C concurrent  -> TTFT / total p50 p90 p99
  soak     one streamed call every I s for M minutes
"""
import argparse, concurrent.futures as cf, datetime, json, os, random, statistics, sys, threading, time
import httpx

HERE = os.path.dirname(os.path.abspath(__file__))
try:
    import tiktoken
    ENC = tiktoken.get_encoding("o200k_base")
except Exception:
    ENC = None
CORPUS = os.path.join(HERE, "suite", "corpus", "natural.txt")
WORKLOAD = "gptcheck-v1"
OK_PROMPT = "Reply with exactly: OK"
SESSION_Q = ["Read the document above. In one sentence, what is it mainly about?",
             "Name three specific relay stations or products the document mentions.",
             "Quote one number that appears in the document and say what it measures.",
             "In two sentences, what is the most serious problem the document reports?",
             "Give a one-line title for the document."]
LOCK = threading.Lock()


def o200k(s): return len(ENC.encode(s)) if ENC else max(1, len(s) // 4)


def doc(seed, n_tok):
    c = open(CORPUS, encoding="utf-8").read()
    off = random.Random(seed).randrange(len(c) // 2)
    s = c[off:off + n_tok * 3]
    return ENC.decode(ENC.encode(s)[:n_tok]) if ENC else s[:n_tok * 4]


def pct(v, p):
    v = sorted(x for x in v if x is not None)
    return v[max(0, round(p / 100 * len(v)) - 1)] if v else None   # nearest rank, same as glmsuite / lat.py


def say(*a):
    with LOCK: print(*a, flush=True)


class Relay:
    def __init__(self, a):
        self.base = a.base.rstrip("/"); self.key = a.key; self.proxy = a.proxy
        self.hdr = {"authorization": "Bearer " + a.key, "content-type": "application/json", "user-agent": a.ua}

    def client(self, timeout=600):
        return httpx.Client(base_url=self.base, timeout=httpx.Timeout(timeout, connect=30), trust_env=self.proxy, headers=self.hdr)

    def stats(self):
        """Per-model billed totals from GET /v1/usage (sub2api style); {} when unsupported."""
        try:
            with self.client(60) as c: j = c.get("/v1/usage").json()
            return {m["model"]: m for m in j.get("model_stats") or []}, j
        except Exception:
            return {}, {}

    def chat(self, body, c, stream=False):
        r = dict(api="chat", status=0, text="", usage={}, id=None, ttft=None, err="", t0=time.time())
        try:
            if not stream:
                resp = c.post("/v1/chat/completions", json=body); r["status"] = resp.status_code
                j = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {}
                if resp.status_code != 200: r["err"] = resp.text[:300]
                else:
                    r["id"] = j.get("id"); r["usage"] = j.get("usage") or {}; r["model_echo"] = j.get("model")
                    r["text"] = ((j.get("choices") or [{}])[0].get("message") or {}).get("content") or ""
                    r["top_keys"] = sorted(j.keys())
            else:
                with c.stream("POST", "/v1/chat/completions", json={**body, "stream": True, "stream_options": {"include_usage": True}}) as resp:
                    r["status"] = resp.status_code
                    if resp.status_code != 200: r["err"] = resp.read().decode(errors="replace")[:300]
                    else:
                        n_chunks = 0
                        for line in resp.iter_lines():
                            if not line.startswith("data:"): continue
                            d = line[5:].strip()
                            if not d or d == "[DONE]": continue
                            try: ev = json.loads(d)
                            except Exception: continue
                            r["id"] = r["id"] or ev.get("id")
                            if ev.get("usage"): r["usage"] = ev["usage"]
                            for ch in ev.get("choices") or []:
                                t = (ch.get("delta") or {}).get("content")
                                if t:
                                    n_chunks += 1
                                    if r["ttft"] is None: r["ttft"] = round(time.time() - r["t0"], 3)
                                    r["text"] += t
                        r["chunks"] = n_chunks
        except Exception as e:
            r["err"] = f"{type(e).__name__}: {str(e)[:200]}"
        r["el"] = round(time.time() - r["t0"], 3)
        return r

    def responses(self, body, c):
        r = dict(api="responses", status=0, text="", usage={}, id=None, err="", t0=time.time())
        try:
            resp = c.post("/v1/responses", json=body); r["status"] = resp.status_code
            j = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {}
            if resp.status_code != 200: r["err"] = resp.text[:300]
            else:
                r["id"] = j.get("id"); r["usage"] = j.get("usage") or {}; r["model_echo"] = j.get("model")
                ins = j.get("instructions")
                r["instructions_len"] = len(ins) if isinstance(ins, str) else None
                r["instructions_head"] = ins[:160] if isinstance(ins, str) else ins
                r["echo"] = {k: j.get(k) for k in ("temperature", "top_p", "max_output_tokens", "prompt_cache_key", "store", "reasoning", "service_tier")}
                for it in j.get("output") or []:
                    for cc in it.get("content") or []:
                        if cc.get("type") == "output_text": r["text"] += cc.get("text", "")
        except Exception as e:
            r["err"] = f"{type(e).__name__}: {str(e)[:200]}"
        r["el"] = round(time.time() - r["t0"], 3)
        return r


def cached_of(u):
    return (u.get("prompt_tokens_details") or u.get("input_tokens_details") or {}).get("cached_tokens") or 0


def in_of(u): return u.get("prompt_tokens", u.get("input_tokens"))


class Model:
    def __init__(self, R, model, nonce, out):
        self.R = R; self.m = model; self.nonce = nonce; self.out = out; self.out.setdefault(model, {})

    def section(self, name, fn, n_expected):
        s0, _ = self.R.stats(); b0 = s0.get(self.m)
        calls = fn()
        delta = None
        if b0 is not None or s0:
            for _ in range(20):          # wait until the gateway has booked every call of this section
                time.sleep(3)
                s1, _ = self.R.stats(); b1 = s1.get(self.m) or {}
                done = (b1.get("requests", 0) - (b0 or {}).get("requests", 0))
                if done >= n_expected: break
            delta = {k: round((b1.get(k) or 0) - ((b0 or {}).get(k) or 0), 8) for k in
                     ("requests", "input_tokens", "cache_read_tokens", "cache_creation_tokens", "output_tokens", "cost", "actual_cost")}
        self.out[self.m][name] = dict(calls=calls, billed=delta)
        say(f"  {self.m:16s} {name:8s} calls={len(calls)} ok={sum(c['status'] == 200 for c in calls)} billed={delta}")

    def inject(self):
        def fn():
            out = []
            with self.R.client() as c:
                for _ in range(3): out.append(self.R.chat({"model": self.m, "messages": [{"role": "user", "content": OK_PROMPT}]}, c))
                for _ in range(3): out.append(self.R.responses({"model": self.m, "input": OK_PROMPT}, c))
            return out
        self.section("inject", fn, 6)

    def params(self):
        q = "What is 17 * 23? Reply with only the number."
        variants = [("baseline", {}), ("temperature_5", {"temperature": 5}), ("max_completion_tokens_16", {"max_completion_tokens": 16}),
                    ("max_tokens_16", {"max_tokens": 16}), ("effort_invalid", {"reasoning_effort": "bogus"}), ("effort_none", {"reasoning_effort": "none"}),
                    ("stop_9", {"stop": ["9"]}), ("logprobs", {"logprobs": True}), ("n_2", {"n": 2})]
        def fn():
            out = []
            with self.R.client() as c:
                for name, kw in variants:
                    r = self.R.chat({"model": self.m, "messages": [{"role": "user", "content": q}], **kw}, c); r["variant"] = name; out.append(r)
                key = f"gptcheck-{self.nonce}"
                r = self.R.responses({"model": self.m, "input": q, "prompt_cache_key": key, "temperature": 0.3, "max_output_tokens": 999999, "store": True}, c)
                r["variant"] = "responses_echo"; r["sent"] = dict(prompt_cache_key=key, temperature=0.3, max_output_tokens=999999, store=True); out.append(r)
            return out
        self.section("params", fn, len(variants) + 1)

    def cache(self):
        def fn():
            out = []
            with self.R.client() as c:
                for api in ("chat", "responses"):
                    d = f"[doc {self.nonce}-{self.m}-cache-{api}]\n" + doc(f"{WORKLOAD}-cache", 12000)
                    fresh = f"[doc {self.nonce}-{self.m}-fresh-{api}]\n" + doc(f"{WORKLOAD}-fresh", 12000)
                    for i, text in enumerate([d, d, d, fresh]):
                        q = text + "\n\nIn one sentence, what is the document above about?"
                        r = (self.R.chat({"model": self.m, "messages": [{"role": "user", "content": q}]}, c) if api == "chat"
                             else self.R.responses({"model": self.m, "input": q}, c))
                        r["tag"] = f"{api}-{'fresh' if i == 3 else 'rep' + str(i + 1)}"; r["sent"] = o200k(q); out.append(r)
                        time.sleep(3)
            return out
        self.section("cache", fn, 8)

    def ttl(self, gaps):
        def one(g):
            d = f"[doc {self.nonce}-{self.m}-ttl{g}]\n" + doc(f"{WORKLOAD}-ttl", 8000)
            q = d + "\n\nReply with exactly: OK"
            with self.R.client() as c:
                w = self.R.chat({"model": self.m, "messages": [{"role": "user", "content": q}]}, c)
                time.sleep(g)
                r = self.R.chat({"model": self.m, "messages": [{"role": "user", "content": q}]}, c)
            w["tag"] = f"ttl{g}-write"; r["tag"] = f"ttl{g}-read"; r["gap"] = g; w["sent"] = r["sent"] = o200k(q)
            return [w, r]
        def fn():
            with cf.ThreadPoolExecutor(len(gaps)) as ex: return [x for pair in ex.map(one, gaps) for x in pair]
        self.section("ttl", fn, 2 * len(gaps))

    def session(self):
        def fn():
            d = f"[doc {self.nonce}-{self.m}-session]\n" + doc(f"{WORKLOAD}-session", 12000)
            msgs = [{"role": "system", "content": d}]; out = []
            with self.R.client() as c:
                for i, q in enumerate(SESSION_Q):
                    msgs.append({"role": "user", "content": q})
                    r = self.R.chat({"model": self.m, "messages": msgs}, c); r["tag"] = f"turn{i + 1}"
                    r["sent"] = sum(o200k(m["content"]) for m in msgs); out.append(r)
                    msgs.append({"role": "assistant", "content": r["text"] or "(no answer)"}); time.sleep(2)
            return out
        self.section("session", fn, 5)

    def lat(self, n_seq, waves, conc):
        body = {"model": self.m, "messages": [{"role": "user", "content": OK_PROMPT}]}
        def fn():
            out = []
            with self.R.client(300) as c:
                for i in range(n_seq):
                    r = self.R.chat(body, c, stream=True); r["tag"] = "seq"; out.append(r)
            for w in range(waves):
                def one(_):
                    with self.R.client(300) as c2:
                        r = self.R.chat(body, c2, stream=True); r["tag"] = f"conc{w + 1}"; return r
                with cf.ThreadPoolExecutor(conc) as ex: out += list(ex.map(one, range(conc)))
                time.sleep(20)
            return out
        self.section("lat", fn, n_seq + waves * conc)

    def soak(self, minutes, every):
        body = {"model": self.m, "messages": [{"role": "user", "content": OK_PROMPT}]}
        def fn():
            out = []; end = time.time() + minutes * 60
            with cf.ThreadPoolExecutor(8) as ex:
                futs = []
                while time.time() < end:
                    def one():
                        with self.R.client(300) as c:
                            r = self.R.chat(body, c, stream=True); r["tag"] = "soak"; return r
                    futs.append(ex.submit(one)); time.sleep(every)
                out = [f.result() for f in futs]
            return out
        n = int(minutes * 60 / every)
        self.section("soak", fn, n)


def lat_stats(calls):
    ok = [c for c in calls if c["status"] == 200 and not c["err"]]
    empty = [c for c in ok if not (c.get("text") or "").strip()]
    errs = {}
    for c in calls:
        if c["status"] != 200 or c["err"]:
            k = f"{c['status']}:{(c['err'] or '')[:60]}"; errs[k] = errs.get(k, 0) + 1
    t = [c["ttft"] for c in ok]; e = [c["el"] for c in ok]
    return dict(n=len(calls), ok=len(ok), err_rate=round(1 - len(ok) / len(calls), 3) if calls else None, empty=len(empty), errs=errs,
                ttft_p50=pct(t, 50), ttft_p90=pct(t, 90), ttft_p99=pct(t, 99), el_p50=pct(e, 50), el_p90=pct(e, 90), el_p99=pct(e, 99),
                el_max=max(e) if e else None, chunks_p50=pct([c.get("chunks") for c in ok], 50))


def summarize(data):
    S = {}
    for m, secs in data["models"].items():
        s = S[m] = {}
        if "inject" in secs:
            cs = secs["inject"]["calls"]; ch = [c for c in cs if c["api"] == "chat"]; rs = [c for c in cs if c["api"] == "responses"]
            att = [((c["usage"].get("attribution") or {}).get("request_fields") or {}).get("instructions") for c in rs]
            s["inject"] = dict(chat_prompt_tokens=[in_of(c["usage"]) for c in ch], responses_input_tokens=[in_of(c["usage"]) for c in rs],
                               responses_cached=[cached_of(c["usage"]) for c in rs], instructions_tokens=[(a or {}).get("input_tokens") for a in att],
                               instructions_len=[c.get("instructions_len") for c in rs], instructions_head=(rs[0].get("instructions_head") if rs else None),
                               sent_o200k=o200k(OK_PROMPT), id_chat=[(c["id"] or "")[:12] for c in ch], id_resp=[(c["id"] or "")[:12] for c in rs],
                               billed=secs["inject"]["billed"])
        if "params" in secs:
            s["params"] = {c["variant"]: dict(status=c["status"], text=(c["text"] or "")[:40], ct=(c["usage"] or {}).get("completion_tokens"),
                                              err=(c["err"] or "")[:120], echo=c.get("echo"), sent=c.get("sent")) for c in secs["params"]["calls"]}
        if "cache" in secs:
            s["cache"] = {c["tag"]: dict(status=c["status"], input=in_of(c["usage"]), cached=cached_of(c["usage"]), sent=c["sent"], el=c["el"])
                          for c in secs["cache"]["calls"]}
            s["cache"]["_billed"] = secs["cache"]["billed"]
        if "ttl" in secs:
            s["ttl"] = {c["gap"]: dict(input=in_of(c["usage"]), cached=cached_of(c["usage"]), status=c["status"]) for c in secs["ttl"]["calls"] if c.get("gap")}
        if "session" in secs:
            cs = secs["session"]["calls"]
            s["session"] = dict(turns=[dict(input=in_of(c["usage"]), cached=cached_of(c["usage"]), out=(c["usage"] or {}).get("completion_tokens"), sent=c["sent"], el=c["el"]) for c in cs],
                                billed=secs["session"]["billed"])
        for k in ("lat", "soak"):
            if k in secs:
                cs = secs[k]["calls"]
                s[k] = {t: lat_stats([c for c in cs if c["tag"].startswith(t)]) for t in sorted({c["tag"].rstrip("0123456789") for c in cs})}
                s[k]["_billed"] = secs[k]["billed"]
    return S


def md(data, S):
    m = data["meta"]
    L = [f"# gptcheck · {m['label']}", "", f"base `{m['base']}` · 路线 {m['route']} · 负载 {WORKLOAD} · nonce `{m['nonce']}` · 开始 {m['started']}", ""]
    L += ["## 注入", "", "| 模型 | chat 报告输入 | responses 报告输入（其中缓存） | 注入 instructions token | instructions 开头 | inject 段计费（输入 / 缓存读 / 输出，$ 实扣） |", "|---|---|---|---|---|---|"]
    for mod, s in S.items():
        i = s.get("inject")
        if not i: continue
        b = i["billed"] or {}
        L.append(f"| {mod} | {i['chat_prompt_tokens']} | {i['responses_input_tokens']}（{i['responses_cached']}） | {i['instructions_tokens']} | {str(i['instructions_head'])[:70]!r} | "
                 f"{b.get('input_tokens')} / {b.get('cache_read_tokens')} / {b.get('output_tokens')}，${b.get('actual_cost')} |")
    L += ["", "## 缓存（约 12k token 文档，连发 3 次 + 1 次新文档）", "", "| 模型 | 接口 | rep1 输入/缓存 | rep2 | rep3 | 新文档 | 段计费 $ 实扣 / 名义 |", "|---|---|---|---|---|---|---|"]
    for mod, s in S.items():
        cc = s.get("cache")
        if not cc: continue
        b = cc.get("_billed") or {}
        for api in ("chat", "responses"):
            cell = lambda t: f"{cc.get(f'{api}-{t}', {}).get('input')}/{cc.get(f'{api}-{t}', {}).get('cached')}"
            L.append(f"| {mod} | {api} | {cell('rep1')} | {cell('rep2')} | {cell('rep3')} | {cell('fresh')} | " + (f"${b.get('actual_cost')} / ${b.get('cost')}" if api == "chat" else "（两接口合计）") + " |")
    if any("ttl" in s for s in S.values()):
        L += ["", "## 缓存 TTL（写入后空闲 N 秒再读同一文档，chat）", "", "| 模型 | " + " | ".join(f"{g}s" for g in data["meta"]["gaps"]) + " |", "|---|" + "---|" * len(data["meta"]["gaps"])]
        for mod, s in S.items():
            t = s.get("ttl")
            if t: L.append(f"| {mod} | " + " | ".join(f"{(t.get(g) or t.get(str(g)) or {}).get('cached')}/{(t.get(g) or t.get(str(g)) or {}).get('input')}" for g in data["meta"]["gaps"]) + " |")
    if any("session" in s for s in S.values()):
        L += ["", "## 5 轮会话（chat，system = 12k 文档）", "", "| 模型 | 每轮 输入/缓存 | 计费 输入 / 缓存读 / 输出 | 实扣 $ | 名义 $ | 实扣/名义 |", "|---|---|---|---|---|---|"]
        for mod, s in S.items():
            se = s.get("session")
            if not se: continue
            b = se["billed"] or {}
            L.append(f"| {mod} | {' · '.join(f'{t['input']}/{t['cached']}' for t in se['turns'])} | {b.get('input_tokens')} / {b.get('cache_read_tokens')} / {b.get('output_tokens')} | "
                     f"{b.get('actual_cost')} | {b.get('cost')} | {(b['actual_cost'] / b['cost']) if b.get('cost') else '—'} |")
    for k, title in (("lat", "延迟（流式短请求，秒）"), ("soak", "soak")):
        if not any(k in s for s in S.values()): continue
        L += ["", f"## {title}", "", "| 模型 | 段 | 成功/总数 | 空 | 首 token p50 / p90 / p99 | 总耗时 p50 / p90 / p99 / max | 错误 |", "|---|---|---|---|---|---|---|"]
        for mod, s in S.items():
            for t, v in (s.get(k) or {}).items():
                if t.startswith("_"): continue
                L.append(f"| {mod} | {t} | {v['ok']}/{v['n']} | {v['empty']} | {v['ttft_p50']} / {v['ttft_p90']} / {v['ttft_p99']} | {v['el_p50']} / {v['el_p90']} / {v['el_p99']} / {v['el_max']} | {v['errs'] or ''} |")
    if any("params" in s for s in S.values()):
        L += ["", "## 参数透传（chat，状态码 · 正文）", ""]
        for mod, s in S.items():
            p = s.get("params")
            if not p: continue
            L.append(f"- **{mod}**：" + "；".join(f"{k} {v['status']}·{v['text']!r}" + (f"·ct={v['ct']}" if v.get('ct') is not None else "") for k, v in p.items() if k != "responses_echo"))
            e = p.get("responses_echo") or {}
            if e.get("echo"): L.append(f"  - responses 回显：发送 {e.get('sent')} → 回显 {e.get('echo')}")
    return "\n".join(L)


def rdir(label): return os.path.join(HERE, "results", "gptcheck", label)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    r = sp.add_parser("run")
    r.add_argument("--label", required=True); r.add_argument("--base", required=True); r.add_argument("--key", default=os.environ.get("RB_KEY"))
    r.add_argument("--models", default="gpt-5.6-sol,gpt-5.6-terra,gpt-6-astra"); r.add_argument("--sections", default="inject,params,cache,ttl,session,lat")
    r.add_argument("--proxy", action="store_true", help="honour HTTPS_PROXY"); r.add_argument("--route", default=os.environ.get("RB_ROUTE", "unspecified"))
    r.add_argument("--ua", default="relay-bench/gptcheck"); r.add_argument("--gaps", default="30,120,300,600")
    r.add_argument("--lat-n", type=int, default=60); r.add_argument("--waves", type=int, default=2); r.add_argument("--conc", type=int, default=30)
    r.add_argument("--soak-min", type=float, default=30); r.add_argument("--soak-every", type=float, default=10)
    p = sp.add_parser("report"); p.add_argument("--label", required=True)
    f = sp.add_parser("freeze"); f.add_argument("--label", required=True); f.add_argument("--name", required=True)
    a = ap.parse_args()
    if a.cmd == "run":
        if not a.key: ap.error("RB_KEY or --key required")
        R = Relay(a); d = rdir(a.label); os.makedirs(d, exist_ok=True)
        fn = os.path.join(d, "data.json")
        data = json.load(open(fn)) if os.path.exists(fn) else dict(meta=dict(label=a.label, base=a.base, route=a.route, workload=WORKLOAD,
                    nonce=f"{random.randrange(16**8):08x}", started=datetime.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %z"),
                    key_hint=a.key[:6] + "…" + a.key[-4:]), models={})
        data["meta"]["gaps"] = [int(x) for x in a.gaps.split(",")]
        _, u0 = R.stats(); data["meta"].setdefault("balance_log", []).append([time.strftime("%H:%M:%S"), u0.get("balance"), a.sections])
        secs = a.sections.split(",")
        def per_model(m):
            M = Model(R, m, data["meta"]["nonce"], data["models"])
            for s in secs:
                if s == "ttl": M.ttl(data["meta"]["gaps"])
                elif s == "lat": M.lat(a.lat_n, a.waves, a.conc)
                elif s == "soak": M.soak(a.soak_min, a.soak_every)
                else: getattr(M, s)()
                with LOCK: json.dump(data, open(fn, "w"), ensure_ascii=False, indent=1)
        with cf.ThreadPoolExecutor(len(a.models.split(","))) as ex: list(ex.map(per_model, a.models.split(",")))
        _, u1 = R.stats(); data["meta"]["balance_log"].append([time.strftime("%H:%M:%S"), u1.get("balance"), "end"])
        json.dump(data, open(fn, "w"), ensure_ascii=False, indent=1)
    data = json.load(open(os.path.join(rdir(a.label), "data.json")))
    S = summarize(data)
    if a.cmd == "freeze":
        ref = dict(name=a.name, kind="gpt-relay", workload=WORKLOAD, base=data["meta"]["base"], key_hint=data["meta"]["key_hint"],
                   measured_at=data["meta"]["started"], route=data["meta"]["route"], source=os.path.relpath(rdir(a.label), HERE), summary=S)
        out = os.path.join(HERE, "suite", "reference", a.name + ".json"); json.dump(ref, open(out, "w"), ensure_ascii=False, indent=1, default=str)
        print("frozen ->", out); return
    text = md(data, S); open(os.path.join(rdir(a.label), "REPORT.md"), "w").write(text + "\n"); print(text)


if __name__ == "__main__":
    main()
