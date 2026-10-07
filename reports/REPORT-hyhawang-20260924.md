# api.hyhawang.com：claude-opus-5 / claude-sonnet-5（2026-09-24）

数据：`results/hyha-k2-ovs/`（海外出口 bench full）、`results/hyha-k2-kiro/`（国内出口 + claude-cli UA bench full）、`results/hyha-probes/`（延迟 / 缓存 / 自然文本 needle / RPM 探针）、日志 `logs/hyha-k2-*.log`。
两把 key：`sk-199a…`（k1）分组列 6 个模型，opus-5/sonnet-5 两条出口 16/16 次全是 Cloudflare 502，渠道整体挂了，按用户要求不再管；`sk-c742…`（k2）分组列 21 个模型，本报告全部基于 k2。key 在 09:50 左右耗尽（`insufficient balance`），Kiro 路由的自然文本 needle 与 IQ 补测没跑成。

## 结论
| 名称 | 实际情况 | 智力（26 题） | 主要问题 |
|---|---|---|---|
| claude-opus-5 | 知识前沿 2025-10、自报截止 2025-01（真 Opus 5 截止 2026-05）→ **老模型冒名**；两池答案逐题一致 | 16/21（5 题被限速/空回复）· 16/26 | 一把 key 后面 3 个池随机混用；合成文本必空回复；usage 是估算值 |
| claude-sonnet-5 | 同上（Sonnet 5 截止 2026-01，差 2-4 月，边界）；Kiro 池上知识更老（首相石破、市长 Adams、"最新 Claude 3.7 Sonnet"） | 15/25 · 16/27 | 同上 |

两名字在同一池里的输出逐字相同（cluster 4 提示全同）、IQ 错题也相同（R10 / X12 / X13 / X4 / H2 / H4 四组全错），基本是**同一个模型挂两个名字**。IQ ≈ 60%，低于 micuapi 上的 Sonnet 4.5（31/33）和 relay-bench 历史上真 Opus 5 / Sonnet 5（≈95%），属于降级货档位。ModelTrace 指纹报 opus-5 / sonnet-5 100%，但指纹库是闭集，不能作为反证。

## 1. 三个后端池（同一把 key、同一分组）
| 池 | 响应 id | usage | 特征 |
|---|---|---|---|
| P1「011C」 | `msg_011C…` 官方格式 | 官方字段齐全（`inference_geo: global`、`service_tier`、`cache_creation{}`），但数值是估算：130k prompt 报 `input_tokens=2`，8.5k 前缀报 write 16k（1.67-2×） | 隐藏 Claude Code 系统提示（模型自称 "I'm Claude Code"）；不传 cache_control 也报缓存命中；两条出口共享同一缓存；**随机词合成文本一律空回复**（out=1、0 chunk）；部分请求流中途 `upstream_error`（缓存探针 B 段 1/6，F 段 2/2） |
| P2「Kiro」 | `msg_<32hex>` | `kiro_actual_input_tokens` 5255 / `kiro_billable` 8 / `kiro_excluded` 5247、`kiro_credits` | Kiro 号池，5.2k 隐藏 prompt 标为不计费；15k 实际只计 89 billable；cache_read 只有 6-71 |
| P3「hex 无字段」 | `msg_<32hex>` | 只有 `{input_tokens, output_tokens}`；5 token 提示报 17，8.5k 前缀报 2345（严重少报） | 无任何缓存字段，同前缀 12 次 0 命中 |

路由规律：开始 15/15、6/6 看起来按「出口 + User-Agent」固定（海外→P1；国内直连 + claude-cli/python UA→P2；国内 + `relay-bench/1.0` UA→P1），半小时后同样请求变成 P1/P3 随机混、偶尔 P2；bench「kiro」组结果里 id 池计数 hex 3 / 011C 4。**用户无法控制落到哪个池**。

## 2. 身份与协议（四组一致）
- 默认无 thinking；显式 adaptive/low 返回 43 字符的 thinking 块且**无 signature**（无法验签，adapter 伪造或剥离）。
- 参数校验 3-4/9：temperature / top_k / budget_tokens / prefill / thinking disabled+xhigh 全部 200；`max_tokens=999999` 200；count_tokens 在 P1 404、在 P2 200。stop_sequences / max_tokens 生效。
- 流有 ping、每 chunk ≈1.7-2 token；`/v1/models` 只回 4 个字段。
- 分词差分：+1617 o200k 英文 token 报 2711（1.68×），中文 +2052 token 报 0/-5 → usage 不是真分词结果。

## 3. 智力（suite/iq.json 26 题，默认 thinking，max_tokens 16000）
| | reason | hard | xhard | 有效合计 |
|---|---|---|---|---|
| ovs opus-5 | 3/3（3 题 429） | 4/6（1 空） | 9/12（2 空） | 16/21 |
| ovs sonnet-5 | 3/6 | 4/6（1 glitch） | 8/13（1 glitch） | 15/25 |
| kiro opus-5 | 3/6 | 5/7 | 8/13（1 glitch） | 16/26 |
| kiro sonnet-5 | 4/6 | 4/7 | 8/14 | 16/27 |
答案键已独立复核（X12 手算、R10/X13 用 Node 22 跑）无误。空回复多为 stop=max_tokens、out=16000（思考 16k 仍没答完）。4 组并行时撞了站点 100 RPM 限速，部分 429 计为 glitch 已剔除；余额耗尽无法补测。

## 4. 延迟 / 稳定性（短问答流式 TTFT，秒；探针全部落在 P1）
| | 顺序 60 次 p50 / p90 / p99 / max | 30 并发 ×2 波 p50 / p95 / p99 / max | 成功 |
|---|---|---|---|
| opus-5（海外） | 2.40 / 2.91 / 4.94 / 6.54 | 5.73 / 7.00 / 7.14 / 7.16 | 120/120 |
| sonnet-5（海外） | 2.33 / 3.35 / 4.50 / 6.70 | 5.49 / 6.20 / 6.46 / 7.58 | 120/120 |
| opus-5（国内直连） | 2.02 / 2.41 / 3.22 / 4.15 | 3.18 / 3.66 / 4.05 / 4.92 | 120/120 |
| sonnet-5（国内直连） | 1.93 / 2.38 / 3.41 / 5.46 | 2.86 / 4.05 / 4.23 / 4.67 | 120/120 |
- bench soak 10 分钟 ×4：0 错误、0 空回复，p50 3.0-3.9 s、p95 5.2-5.5 s、max 6-26 s。
- P2 池顺序 8 次 p50 2.1-2.3 s、12 并发 12/12 p50 2.7-3.0 s（bench kiro 组，落 P2 时）。
- 吞吐 32-38 tok/s（≈493 token 中位数），2500 token 长输出无截断。
- **每用户 100 请求/分钟硬限速**：2 req/s 打到第 101 个开始 429（retry-after 7 s）。
- 海外出口偶发 TLS `UNEXPECTED_EOF`（代理链路），直连偶发 ConnectError。

## 5. 缓存（8.5k 前缀 system + cache_control，3 s 间隔）
| 项 | P1（两模型一致） | P2 | P3 |
|---|---|---|---|
| 顺序 12 次 | 1 写 + 11 读，read 恒 16047/15940 | 15k 实际 → billable 89、read 0-71 | 12/12 read=0 |
| 多轮 6 轮 | 5/5 命中，read 16047→16149 递增；1 轮 upstream_error | — | — |
| 不带 cache_control | **照样命中**（read 16047） | — | — |
| 新前缀 | 先写后读，正常 | — | — |
| 1h TTL | opus 报 input 1114/无缓存，sonnet 当 5m 处理；`ephemeral_1h` 恒 0 | — | — |
| 空闲 5.5 min | bench：read=0（过期） | — | — |
| OpenAI 格式 | opus 回 `msg_011C` id、cached 16062；sonnet 回 `chatcmpl-` 无 usage | — | — |
| 命中降 TTFT | 否（3-4 s 不变） | — | — |
**理论缓存上限（P1 报出的数）≈ 99.9%**：命中时 read 16047 + input 14，只有用户末条消息不进缓存。但这个 usage 是模板估算（130k prompt 报 input 2），只能说明「站点账单按什么算」，不能证明上游真的命中；余额在测 130k/230k 后迅速耗尽，实际扣费比例请在后台账单核对（`/api/log/token` 404，拉不到逐条账单）。P3 池完全无缓存。

## 6. 长上下文
| | 20k | 60k | 130k | 230k |
|---|---|---|---|---|
| 合成随机词（bench，P1） | 空 | 空 | 空 | 200 但空 |
| 自然文本（探针，P1）opus-5 | 3/3，7.1 s | 3/3，6.2 s | 2/3，7.9 s | — |
| 自然文本 sonnet-5 | 3/3，5.6 s | 3/3，5.9 s | 2/3，6.8 s | — |
| P2 / P3 | 余额耗尽未测（bench 时被自己的 429 打掉） | | | |
自然文本 130k 能召回 2/3，上下文基本真实到 130k；两模型三档答案逐字相同。230k 接受但没有正文，无法证明 1M。60k 系统提示遵守测试因合成文本空回复无结果。20 轮多轮记忆通过（P1）。

## 7. 其他
- 隐藏提示：P1 计 "Reply with exactly: OK" 为 7 token（不含隐藏部分），模型自称 Claude Code；P2 用 `kiro_excluded` 明示 5.2k。
- k1 分组（`sk-199a…`）：模型列表含 fable-5 / opus-4-6~4-8 / opus-5 / sonnet-5，测试期间 opus-5 / sonnet-5 全程 502。
