# glmproxy —— 给 Claude Code / Anthropic 客户端用 v129 这类 OpenAI 格式中转的翻译代理

单文件、只依赖 `aiohttp` + `httpx`（可选 `tiktoken`）。Anthropic Messages 进，OpenAI chat.completions（智谱 GLM 方言）出。

```bash
PROXY_UPSTREAM=https://api.v129.site PROXY_UPSTREAM_KEY=sk-你的v129key python3 glmproxy.py --port 8790
# Claude Code：
ANTHROPIC_BASE_URL=http://127.0.0.1:8790 ANTHROPIC_AUTH_TOKEN=any ANTHROPIC_MODEL=glm-5.3-flash ANTHROPIC_SMALL_FAST_MODEL=glm-5.3-flash claude
```
上游也可以直接指官方 `PROXY_UPSTREAM=https://open.bigmodel.cn/api/paas/v4`（这时 count_tokens 走官方 /tokenizer，精确）。不设 `PROXY_UPSTREAM_KEY` 时把客户端的 x-api-key 原样转发，方便多分组共用一个代理。

## 修掉了 v129 自带 Anthropic 接口的哪些问题（2026-09-10 用 bench.py 以 Anthropic 协议实测）

| 项目 | 官方 Anthropic 接口 | v129 自带 /v1/messages | glmproxy → v129 |
|---|---|---|---|
| thinking 块 + signature | 有 | 无 | 有（reasoning_content → thinking_delta，24 hex signature） |
| effort / thinking 参数 | 生效 | 忽略，思考限不住 | `output_config.effort` → reasoning_effort；`budget_tokens` <2048→low、<16000→high、否则 max；`disabled` → low（`PROXY_STRICT_THINKING=1` 改为 400 同官方） |
| stop_sequences | 生效 | 不生效 | 代理里扫流截断，`stop_reason=stop_sequence` 并回填 `stop_sequence`，usage 仍完整 |
| count_tokens | 200 | 404 | 200（官方上游走 /tokenizer；否则 o200k×GLM 系数估算，误差约 1 token） |
| 流式 | 逐 token，有 ping | 整段生成后假流式 | 逐 token，15 s 无输出自动 ping |
| usage | 原生 | 多出 new-api 字段 | 只有 input/output/cache_read/cache_creation，cached_tokens 映射为 cache_read |
| 工具调用 同步/流式 | ✓ | ✓ | ✓（tool_result → role=tool；tool_choice any/tool → required，GLM 不能指定具体工具） |
| 短 max_tokens 请求 | 正常 | 5/5 空正文 | 正常（effort 生效后思考不再吃光预算） |
| 缓存 | 命中 | 命中 | 命中（多轮对话 cache_read 正常，Claude Code 端到端 57k 命中） |
| 参数校验一致率 | 10/10 | 8/10 | 8/10（差异只在 thinking disabled / effort xhigh 被映射而不是 400，可开 STRICT） |

Claude Code 端到端（`claude -p` 通过代理，读 2 个文件、新建 1 个文件、汇报）：4 轮、69 s、正确完成。

## 已知边界
- 不能指定必须调用某一个工具（GLM 只支持 auto/required）。
- 多轮里客户端回传的 thinking 块会被丢弃（GLM 本身也不接收历史思考）。
- `cache_control` 是空操作：智谱是隐式缓存，自动命中，TTL 约 2–3 分钟。
- temperature 会被截到 [0,1]，top_k 被忽略。
- 上游是 v129 时，v129 自己丢 `stop`，所以截断由代理完成，多生成的 token 仍会被上游计费。
