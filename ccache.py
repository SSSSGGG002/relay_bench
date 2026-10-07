#!/usr/bin/env python3
"""Cache-trigger ablation: which part of a Claude Code request makes a relay's GLM channel report cache hits?
Each variant gets its own brand-new ~6k-token prefix and is called N times (same body), streaming, so we see
both the usage cache fields and TTFT (numbers can be faked, TTFT cannot).
  RELAY_BASE=https://host RELAY_KEY=sk-... python3 ccache.py [--model glm-5.3-flash] [--n 3] [--gap 4] [--only A0,A5]
"""
import argparse, json, os, random, time, uuid, httpx
BASE = os.environ["RELAY_BASE"].rstrip("/"); KEY = os.environ["RELAY_KEY"]
CC_HEADERS = {"user-agent": "claude-cli/2.1.12 (external, cli)", "x-app": "cli", "anthropic-dangerous-direct-browser-access": "true",
              "anthropic-beta": "claude-code-20250219,interleaved-thinking-2025-05-14,fine-grained-tool-streaming-2025-05-14",
              "x-stainless-lang": "js", "x-stainless-package-version": "0.60.0", "x-stainless-runtime": "node", "x-stainless-os": "MacOS", "x-stainless-arch": "arm64"}
CC_IDENT = "You are Claude Code, Anthropic's official CLI for Claude."
TOOL = {"name": "Bash", "description": "Executes a bash command and returns its output.", "input_schema": {"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]}}
def prefix(seed, n=6000):
    rng = random.Random(seed); words = "river stone cloud bright silver window garden yellow purple forest castle meadow ocean quiet thunder velvet copper marble candle orbit".split()
    out = []
    while sum(len(x) for x in out) < n * 4: out.append(" ".join(rng.choice(words) for _ in range(12)) + f" [{rng.randint(1000,9999)}].")
    return " ".join(out)
def sse(r):
    for line in r.iter_lines():
        if line.startswith("data:"):
            d = line[5:].strip()
            if d and d != "[DONE]":
                try: yield json.loads(d)
                except Exception: pass
def anthropic(model, p, cc=False, meta=None, headers=False, ident=False, tool=False):
    sysb = ([{"type": "text", "text": CC_IDENT}] if ident else []) + [{"type": "text", "text": p}]
    if cc: sysb[-1]["cache_control"] = {"type": "ephemeral"}
    body = {"model": model, "max_tokens": 64, "stream": True, "system": sysb if (cc or ident) else p, "messages": [{"role": "user", "content": "Reply with exactly: OK"}]}
    if meta: body["metadata"] = {"user_id": meta}
    if tool: body["tools"] = [TOOL]
    h = {"x-api-key": KEY, "anthropic-version": "2023-06-01", "content-type": "application/json"}
    if headers: h.update(CC_HEADERS)
    t0 = time.time(); ttft = None; u = {}; rid = None; err = None
    with httpx.stream("POST", BASE + "/v1/messages", headers=h, json=body, timeout=180) as r:
        if r.status_code != 200: return dict(status=r.status_code, err=r.read().decode()[:200])
        for ev in sse(r):
            if ev.get("type") == "message_start": rid = ev["message"].get("id"); us = ev["message"].get("usage") or {}
            elif ev.get("type") == "message_delta": us = ev.get("usage") or {}
            elif ev.get("type") == "content_block_delta":
                if ttft is None: ttft = round(time.time() - t0, 2)
                continue
            elif ev.get("type") == "error": err = json.dumps(ev)[:200]; continue
            else: continue
            for k, v in us.items():
                if isinstance(v, (int, float)): u[k] = max(u.get(k, 0), v)
    return dict(status=200, id=(rid or "")[:18], inp=u.get("input_tokens"), c_read=u.get("cache_read_input_tokens"), c_write=u.get("cache_creation_input_tokens"), ttft=ttft, t=round(time.time() - t0, 2), err=err)
def openai(model, p, user=None):
    body = {"model": model, "max_tokens": 64, "stream": True, "stream_options": {"include_usage": True}, "messages": [{"role": "system", "content": p}, {"role": "user", "content": "Reply with exactly: OK"}]}
    if user: body["user"] = user
    t0 = time.time(); ttft = None; u = {}; rid = None
    with httpx.stream("POST", BASE + "/v1/chat/completions", headers={"authorization": f"Bearer {KEY}"}, json=body, timeout=180) as r:
        if r.status_code != 200: return dict(status=r.status_code, err=r.read().decode()[:200])
        for ev in sse(r):
            rid = rid or ev.get("id")
            if ev.get("usage"): u = ev["usage"]
            for c in ev.get("choices") or []:
                d = c.get("delta") or {}
                if ttft is None and (d.get("content") or d.get("reasoning_content")): ttft = round(time.time() - t0, 2)
    return dict(status=200, id=(rid or "")[:18], inp=u.get("prompt_tokens"), c_read=(u.get("prompt_tokens_details") or {}).get("cached_tokens"), ttft=ttft, t=round(time.time() - t0, 2))
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--model", default="glm-5.3-flash"); ap.add_argument("--n", type=int, default=3); ap.add_argument("--gap", type=float, default=4); ap.add_argument("--only", default=""); ap.add_argument("--out", default="results/ccache.json")
    a = ap.parse_args(); sid = f"user_{uuid.uuid4().hex}{uuid.uuid4().hex}_account__session_{uuid.uuid4()}"
    V = {"O0 openai bare": lambda p: openai(a.model, p),
         "O1 openai +user": lambda p: openai(a.model, p, user=sid),
         "A0 anthropic bare": lambda p: anthropic(a.model, p),
         "A1 +cache_control": lambda p: anthropic(a.model, p, cc=True),
         "A2 +metadata.user_id": lambda p: anthropic(a.model, p, meta=sid),
         "A3 +CC headers": lambda p: anthropic(a.model, p, headers=True),
         "A4 +cc +metadata": lambda p: anthropic(a.model, p, cc=True, meta=sid),
         "A5 full CC-like": lambda p: anthropic(a.model, p, cc=True, meta=sid, headers=True, ident=True, tool=True)}
    only = [x for x in a.only.split(",") if x]; seed = int(time.time()); res = {}
    print(f"base={BASE} model={a.model} seed={seed}")
    for i, (name, fn) in enumerate(V.items()):
        if only and name.split()[0] not in only: continue
        p = prefix(seed + i * 977); rows = []
        for j in range(a.n):
            try: row = fn(p)
            except Exception as e: row = dict(status="exc", err=repr(e)[:200])
            rows.append(row); print(f"[{name}] #{j+1} {row}", flush=True); time.sleep(a.gap)
        res[name] = rows
    prev = json.load(open(a.out)) if os.path.exists(a.out) else {}; prev[f"{BASE}|{a.model}|{seed}"] = res; json.dump(prev, open(a.out, "w"), indent=1)
main()
