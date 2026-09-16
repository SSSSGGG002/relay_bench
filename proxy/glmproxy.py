#!/usr/bin/env python3
"""glmproxy — Anthropic Messages API in, OpenAI chat.completions out (Zhipu GLM dialect).

Fixes every defect measured on relay-side conversions (2026-09-10): real thinking blocks with signature, effort mapping,
stop_sequences enforced in-proxy, count_tokens, true token streaming, clean Anthropic usage, keep-alive pings.

  PROXY_UPSTREAM=https://api.v129.site PROXY_UPSTREAM_KEY=sk-... python3 glmproxy.py --port 8790
  # then: ANTHROPIC_BASE_URL=http://127.0.0.1:8790 ANTHROPIC_API_KEY=anything ANTHROPIC_MODEL=glm-5.3-flash claude

Env / flags:
  PROXY_UPSTREAM        upstream base (default https://api.v129.site ; official: https://open.bigmodel.cn/api/paas/v4)
  PROXY_UPSTREAM_KEY    upstream key; if unset the client's x-api-key / Bearer is forwarded
  PROXY_DEFAULT_MODEL   model used for any non-glm model name the client asks for (default glm-5.3-flash)
  PROXY_STRICT_THINKING 1 -> thinking.type=disabled returns 400 like the official API (default: map to effort=low)
"""
import argparse, asyncio, json, os, re, secrets, time, uuid
from aiohttp import web
import httpx
try:
    import tiktoken; ENC = tiktoken.get_encoding("o200k_base")
except Exception: ENC = None

UPSTREAM = os.environ.get("PROXY_UPSTREAM", "https://api.v129.site").rstrip("/")
UPSTREAM_KEY = os.environ.get("PROXY_UPSTREAM_KEY")
DEFAULT_MODEL = os.environ.get("PROXY_DEFAULT_MODEL", "glm-5.3-flash")
STRICT_THINKING = os.environ.get("PROXY_STRICT_THINKING") == "1"
CHAT_PATH = "/chat/completions" if UPSTREAM.endswith("/v4") else "/v1/chat/completions"
TOK_PATH = "/tokenizer" if UPSTREAM.endswith("/v4") else "/v1/tokenizer"
EFFORT = {"low": "low", "medium": "high", "high": "high", "xhigh": "max", "max": "max"}
STOP_MAP = {"stop": "end_turn", "length": "max_tokens", "tool_calls": "tool_use", "sensitive": "end_turn", "network_error": "end_turn", "model_context_window_exceeded": "max_tokens"}

def err(status, typ, msg):
    return web.json_response({"type": "error", "error": {"type": typ, "message": msg}}, status=status)
def new_id(prefix="msg"): return f"{prefix}_{time.strftime('%Y%m%d%H%M%S')}{secrets.token_hex(8)}"
def sig(): return secrets.token_hex(12)  # Zhipu's own Anthropic endpoint uses a 24-hex placeholder signature; nothing verifies it

# ---------------------------------------------------------------- request translation
def blocks_text(c):
    if isinstance(c, str): return c
    return "".join(b.get("text", "") for b in (c or []) if b.get("type") == "text")

def to_openai(req):
    model = req.get("model") or DEFAULT_MODEL
    if not model.lower().startswith("glm"): model = DEFAULT_MODEL
    msgs = []
    sysm = req.get("system")
    if sysm: msgs.append({"role": "system", "content": blocks_text(sysm)})
    for m in req.get("messages") or []:
        role, c = m.get("role"), m.get("content")
        if isinstance(c, str):
            msgs.append({"role": role, "content": c}); continue
        if role == "assistant":
            text = ""; tcs = []
            for b in c or []:
                t = b.get("type")
                if t == "text": text += b.get("text", "")
                elif t == "tool_use": tcs.append({"id": b.get("id") or f"call_{secrets.token_hex(12)}", "type": "function", "function": {"name": b.get("name"), "arguments": json.dumps(b.get("input") or {}, ensure_ascii=False)}})
                # thinking / redacted_thinking blocks are dropped: GLM (clear_thinking) does not take prior reasoning back
            am = {"role": "assistant", "content": text or ("" if not tcs else None)}
            if tcs: am["tool_calls"] = tcs
            if am["content"] is None: am["content"] = ""
            msgs.append(am)
        else:  # user: tool_result blocks become tool messages, everything else a user message
            parts = []; tools = []
            for b in c or []:
                t = b.get("type")
                if t == "tool_result":
                    inner = b.get("content")
                    txt = inner if isinstance(inner, str) else "".join(x.get("text", "") for x in (inner or []) if x.get("type") == "text")
                    tools.append({"role": "tool", "tool_call_id": b.get("tool_use_id"), "content": txt or ("error" if b.get("is_error") else "")})
                elif t == "text": parts.append({"type": "text", "text": b.get("text", "")})
                elif t == "image":
                    s = b.get("source") or {}
                    url = s.get("url") if s.get("type") == "url" else f"data:{s.get('media_type','image/png')};base64,{s.get('data','')}"
                    parts.append({"type": "image_url", "image_url": {"url": url}})
            msgs.extend(tools)
            if parts:
                if all(p["type"] == "text" for p in parts): msgs.append({"role": "user", "content": "".join(p["text"] for p in parts)})
                else: msgs.append({"role": "user", "content": parts})
    body = {"model": model, "messages": msgs, "stream": True, "stream_options": {"include_usage": True}, "max_tokens": max(1, min(int(req.get("max_tokens") or 4096), 131072))}
    if "temperature" in req: body["temperature"] = max(0.0, min(float(req["temperature"]), 1.0))
    if "top_p" in req: body["top_p"] = max(0.01, min(float(req["top_p"]), 1.0))
    stops = [s for s in (req.get("stop_sequences") or []) if s]
    if stops: body["stop"] = stops[:4]
    th = req.get("thinking") or {}; eff = None
    if th.get("type") == "disabled":
        if STRICT_THINKING: raise ValueError("该模型始终思考，不支持关闭思考；请使用 output_config.effort low/high/max")
        eff = "low"
    elif th.get("type") == "enabled" and th.get("budget_tokens"):
        b = int(th["budget_tokens"]); eff = "low" if b < 2048 else ("high" if b < 16000 else "max")
    oc = (req.get("output_config") or {}).get("effort")
    if oc: eff = EFFORT.get(oc, "high")
    if eff: body["reasoning_effort"] = eff
    tools = req.get("tools") or []
    ft = [{"type": "function", "function": {"name": t["name"], "description": t.get("description", ""), "parameters": t.get("input_schema") or {"type": "object", "properties": {}}}} for t in tools if t.get("name") and not t.get("type", "custom").startswith(("web_search", "computer", "bash", "text_editor"))]
    if ft:
        body["tools"] = ft
        tc = req.get("tool_choice") or {}
        body["tool_choice"] = "required" if tc.get("type") in ("any", "tool") else "auto"  # GLM cannot force one specific tool
    return body, stops

# ---------------------------------------------------------------- streaming translation
class Emitter:
    """Turns upstream OpenAI SSE chunks into Anthropic SSE events, enforcing stop sequences on visible text."""
    def __init__(self, model, stops):
        self.model = model; self.stops = stops; self.idx = -1; self.cur = None  # cur: thinking|text|tool
        self.text = ""; self.thinking = ""; self.tools = []; self.stop_reason = None; self.stop_seq = None; self.usage = {}
        self.events = []; self.id = new_id(); self.done = False; self.pending = ""  # pending = text held back for stop matching
    def ev(self, typ, **d): self.events.append((typ, dict(type=typ, **d)))
    def start(self):
        self.ev("message_start", message={"id": self.id, "type": "message", "role": "assistant", "model": self.model, "content": [], "stop_reason": None, "stop_sequence": None, "usage": {"input_tokens": 0, "output_tokens": 0, "cache_read_input_tokens": 0}})
        self.ev("ping")
    def close_block(self):
        if self.cur is None: return
        if self.cur == "thinking": self.ev("content_block_delta", index=self.idx, delta={"type": "signature_delta", "signature": sig()})
        self.ev("content_block_stop", index=self.idx); self.cur = None
    def open_block(self, kind, **extra):
        self.close_block(); self.idx += 1; self.cur = kind
        cb = {"thinking": {"type": "thinking", "thinking": "", "signature": ""}, "text": {"type": "text", "text": ""}, "tool": {"type": "tool_use", **extra}}[kind]
        self.ev("content_block_start", index=self.idx, content_block=cb)
    def on_reasoning(self, s):
        if not s or self.done: return
        if self.cur != "thinking": self.open_block("thinking")
        self.thinking += s; self.ev("content_block_delta", index=self.idx, delta={"type": "thinking_delta", "thinking": s})
    def on_text(self, s):
        if not s or self.done: return
        if self.cur != "text": self.flush_pending(); self.open_block("text")
        self.pending += s
        # stop-sequence enforcement: emit everything that cannot be a prefix of a stop sequence
        if self.stops:
            for st in self.stops:
                k = self.pending.find(st)
                if k >= 0:
                    out = self.pending[:k]; self.pending = ""; self._emit_text(out); self.done = True; self.stop_reason = "stop_sequence"; self.stop_seq = st; return
            hold = max((len(st) - 1 for st in self.stops if any(self.pending.endswith(st[:i]) for i in range(1, len(st)))), default=0)
            if hold: out = self.pending[:-hold] if hold < len(self.pending) else ""; self.pending = self.pending[len(out):]
            else: out = self.pending; self.pending = ""
            self._emit_text(out)
        else:
            out = self.pending; self.pending = ""; self._emit_text(out)
    def _emit_text(self, s):
        if s: self.text += s; self.ev("content_block_delta", index=self.idx, delta={"type": "text_delta", "text": s})
    def flush_pending(self):
        if self.pending: out = self.pending; self.pending = ""; self._emit_text(out)
    def on_tool(self, tc):
        if self.done: return
        i = tc.get("index", 0); f = tc.get("function") or {}
        while len(self.tools) <= i: self.tools.append({"id": None, "name": None, "args": "", "opened": False})
        t = self.tools[i]
        if tc.get("id"): t["id"] = tc["id"]
        if f.get("name"): t["name"] = f["name"]
        if not t["opened"] and t["name"]:
            t["opened"] = True; self.flush_pending(); self.open_block("tool", id=t["id"] or f"toolu_{secrets.token_hex(12)}", name=t["name"], input={}); t["blk"] = self.idx
        if f.get("arguments"):
            t["args"] += f["arguments"]
            if t["opened"]: self.ev("content_block_delta", index=t["blk"], delta={"type": "input_json_delta", "partial_json": f["arguments"]})
    def finish(self, finish_reason, usage):
        self.flush_pending(); self.close_block()
        if usage: self.usage = usage
        if not self.stop_reason: self.stop_reason = STOP_MAP.get(finish_reason or "stop", "end_turn")
        if self.tools and self.stop_reason == "end_turn": self.stop_reason = "tool_use"
        self.ev("message_delta", delta={"stop_reason": self.stop_reason, "stop_sequence": self.stop_seq}, usage=self.anthropic_usage())
        self.ev("message_stop")
    def anthropic_usage(self):
        u = self.usage or {}; cached = ((u.get("prompt_tokens_details") or {}).get("cached_tokens")) or u.get("cached_tokens") or 0
        pt = u.get("prompt_tokens") or 0
        return {"input_tokens": max(pt - cached, 0), "output_tokens": u.get("completion_tokens") or 0, "cache_read_input_tokens": cached, "cache_creation_input_tokens": 0}
    def message_json(self):
        content = []
        if self.thinking: content.append({"type": "thinking", "thinking": self.thinking, "signature": sig()})
        if self.text: content.append({"type": "text", "text": self.text})
        for t in self.tools:
            try: inp = json.loads(t["args"]) if t["args"] else {}
            except Exception: inp = {"_raw": t["args"]}
            content.append({"type": "tool_use", "id": t["id"] or f"toolu_{secrets.token_hex(12)}", "name": t["name"], "input": inp})
        return {"id": self.id, "type": "message", "role": "assistant", "model": self.model, "content": content, "stop_reason": self.stop_reason, "stop_sequence": self.stop_seq, "usage": self.anthropic_usage()}

def upstream_headers(request):
    key = UPSTREAM_KEY or request.headers.get("x-api-key") or (request.headers.get("authorization") or "").replace("Bearer ", "")
    return {"authorization": f"Bearer {key}", "content-type": "application/json"}

CLIENT = None
async def client():
    global CLIENT
    if CLIENT is None: CLIENT = httpx.AsyncClient(timeout=httpx.Timeout(900, connect=30))
    return CLIENT

async def handle_messages(request):
    try: req = await request.json()
    except Exception: return err(400, "invalid_request_error", "body is not JSON")
    if not req.get("messages"): return err(400, "invalid_request_error", "messages: field required")
    if not req.get("max_tokens"): return err(400, "invalid_request_error", "max_tokens: field required")
    if int(req["max_tokens"]) > 131072: return err(400, "invalid_request_error", f"max_tokens: {req['max_tokens']} > 131072, the maximum for {DEFAULT_MODEL}")
    try: body, stops = to_openai(req)
    except ValueError as e: return err(400, "invalid_request_error", str(e))
    em = Emitter(req.get("model") or body["model"], stops); em.start()
    stream = bool(req.get("stream")); resp = None; t0 = time.time()
    if stream:
        resp = web.StreamResponse(status=200, headers={"content-type": "text/event-stream; charset=utf-8", "cache-control": "no-cache", "x-glmproxy-upstream": UPSTREAM})
        await resp.prepare(request)
    sent = 0
    async def flush():
        nonlocal sent
        if not stream: return
        while sent < len(em.events):
            typ, d = em.events[sent]; sent += 1
            await resp.write(f"event: {typ}\ndata: {json.dumps(d, ensure_ascii=False)}\n\n".encode())
    await flush()
    finish = None; usage = None; last_ping = time.time(); upstream_status = 200
    try:
        c = await client()
        async with c.stream("POST", UPSTREAM + CHAT_PATH, headers=upstream_headers(request), json=body) as r:
            upstream_status = r.status_code
            if r.status_code != 200:
                raw = (await r.aread()).decode(errors="replace")
                try: j = json.loads(raw); msg = (j.get("error") or {}).get("message") or raw[:300]
                except Exception: msg = raw[:300]
                if stream:
                    await resp.write(f"event: error\ndata: {json.dumps({'type': 'error', 'error': {'type': 'api_error' if r.status_code >= 500 else 'invalid_request_error', 'message': f'upstream {r.status_code}: {msg}'}})}\n\n".encode()); await resp.write_eof(); return resp
                return err(r.status_code if r.status_code in (400, 401, 403, 404, 429) else 502, "api_error" if r.status_code >= 500 else "invalid_request_error", f"upstream {r.status_code}: {msg}")
            async for line in r.aiter_lines():
                if stream and time.time() - last_ping > 15:
                    await resp.write(b"event: ping\ndata: {\"type\": \"ping\"}\n\n"); last_ping = time.time()
                if not line.startswith("data:"): continue
                d = line[5:].strip()
                if d == "[DONE]": break
                try: ch = json.loads(d)
                except Exception: continue
                if ch.get("usage"): usage = ch["usage"]
                for choice in ch.get("choices") or []:
                    delta = choice.get("delta") or {}
                    if delta.get("reasoning_content"): em.on_reasoning(delta["reasoning_content"])
                    if delta.get("content"): em.on_text(delta["content"])
                    for tc in delta.get("tool_calls") or []: em.on_tool(tc)
                    if choice.get("finish_reason"): finish = choice["finish_reason"]
                await flush()
    except httpx.HTTPError as e:
        if stream:
            await resp.write(f"event: error\ndata: {json.dumps({'type': 'error', 'error': {'type': 'api_error', 'message': f'upstream transport error: {e}'}})}\n\n".encode()); await resp.write_eof(); return resp
        return err(502, "api_error", f"upstream transport error: {e}")
    em.finish(finish, usage)
    request.app["stats"].append(dict(t=round(time.time() - t0, 2), model=body["model"], st=upstream_status, out=em.anthropic_usage()["output_tokens"], stop=em.stop_reason))
    if stream:
        await flush(); await resp.write_eof(); return resp
    return web.json_response(em.message_json(), headers={"x-glmproxy-upstream": UPSTREAM})

async def handle_count(request):
    try: req = await request.json()
    except Exception: return err(400, "invalid_request_error", "body is not JSON")
    try: body, _ = to_openai(req)
    except ValueError as e: return err(400, "invalid_request_error", str(e))
    c = await client()
    try:
        r = await c.post(UPSTREAM + TOK_PATH, headers=upstream_headers(request), json={"model": body["model"], "messages": [m for m in body["messages"] if isinstance(m.get("content"), str)], **({"tools": body["tools"]} if body.get("tools") else {})}, timeout=30)
        if r.status_code == 200: return web.json_response({"input_tokens": (r.json().get("usage") or {}).get("prompt_tokens")})
    except Exception: pass
    # fallback: o200k estimate x GLM ratio (EN ~1.01, ZH ~0.79) + chat template overhead
    txt = "\n".join((m["content"] if isinstance(m.get("content"), str) else json.dumps(m.get("content"), ensure_ascii=False)) + json.dumps(m.get("tool_calls", ""), ensure_ascii=False) for m in body["messages"]) + json.dumps(body.get("tools", ""), ensure_ascii=False)
    n = len(ENC.encode(txt)) if ENC else len(txt) // 4
    zh = sum(1 for ch in txt if "一" <= ch <= "鿿") / max(len(txt), 1)
    return web.json_response({"input_tokens": int(n * (1.01 * (1 - zh) + 0.79 * zh)) + 12 + 3 * (len(body["messages"]) - 1)})

async def handle_models(request):
    return web.json_response({"data": [{"id": DEFAULT_MODEL, "type": "model", "display_name": DEFAULT_MODEL, "created_at": "2026-06-17T00:00:00Z"}], "has_more": False})
async def handle_health(request):
    s = request.app["stats"][-200:]
    return web.json_response({"ok": True, "upstream": UPSTREAM, "default_model": DEFAULT_MODEL, "recent": len(s), "errors": sum(1 for x in s if x["st"] != 200), "p50_s": sorted(x["t"] for x in s)[len(s) // 2] if s else None})

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--host", default="127.0.0.1"); ap.add_argument("--port", type=int, default=8790); a = ap.parse_args()
    app = web.Application(client_max_size=64 * 1024 * 1024); app["stats"] = []
    app.router.add_post("/v1/messages", handle_messages); app.router.add_post("/v1/messages/count_tokens", handle_count)
    app.router.add_get("/v1/models", handle_models); app.router.add_get("/health", handle_health)
    print(f"glmproxy: Anthropic in -> {UPSTREAM}{CHAT_PATH} out ; default model {DEFAULT_MODEL} ; strict_thinking={STRICT_THINKING}", flush=True)
    web.run_app(app, host=a.host, port=a.port, print=None)
if __name__ == "__main__": main()
