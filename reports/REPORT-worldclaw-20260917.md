# WorldClawPro worldclawpro.ai Claude 通道实测（2026-09-17 02:08–02:50，Mac 经 Clash 出海）

站点：WorldClawPro（new-api `v1.0.0-rc.36`，宣传 "1% of official price / 100+ models"）。key 所在分组 **「kiro 高缓」**（倍率 0.2，站内分组描述就是「测试」）。分组里 5 个 Claude 名字：opus-4-6 / 4-7 / 4-8、sonnet-4-6、sonnet-5，没有 opus-5 / fable。标价：opus-4-x 与 sonnet-4-6 倍率 37.5、sonnet-5 倍率 1.5（补全倍率都是 5）。测试期间管理员在实时改配置：sonnet-5 02:08 在列表里、02:15 被摘掉、02:21 又回来。

按用户要求重点测 **sonnet-5 和 opus-4-6**（screen 档 + 12/24 并发），opus-4-7 / 4-8 只各做了 1 次探针。

## 结论

| 名字 | 结论 | 实际后端 |
|---|---|---|
| claude-sonnet-5 | **假映射**。知识止于 2024-10（Francis / 石破茂 / Eric Adams / 最新 Claude = 3.5 Sonnet / GPT-4o，4 次一致），自报 "Claude Sonnet 4.5、截止 2025-01"。能力：screen 8/8，完整题库 **22/24**（reason 5/6、hard 5/6、xhard 12/12；H7/X7/X8 因 524 剔除），接近真前沿参照（bit/opus-5、sonnet-5 48/48）。指纹归属 sonnet-5 100%，但指纹库是闭集、没有 Sonnet 4.5 | Kiro 池里的 Sonnet 4.5 档 |
| claude-opus-4-6 | **映射到别的模型 + 混池**。bench 那轮开放式探针答到 2026-01（Leo XIV / Mamdani / Opus 4 / Claude Opus 4.5），比 Opus 4.6 官方截止（2025-05/08）还新；手工 3 次采样 1 次 2026-01 档（自报 Opus 4.5，知道高市/Mamdani/GPT-5.1）、2 次 2025-05 档（Leo XIV 但 Ishiba / Adams / 3.5–3.7 Sonnet / GPT-4o）。能力：screen 8/8，完整题库 **21/26**（reason 6/6、hard 5/7、xhard 10/14），介于真前沿（48/48）和 Kiro 降级货（dragon3 opus-5 30/52）之间；指纹归属 opus-4-6 100% | Kiro 池 Opus 4.5 与 Sonnet 4 档轮询 |
| claude-opus-4-7 | 假（1 次探针）。知识 2024 年档，自报 "Claude 3.5 Sonnet, training cutoff April 2024" | Sonnet 3.5/4 档 |
| claude-opus-4-8 | 假（1 次探针）。Pope Francis / 岸田 / Adams / 3.5 Sonnet / GPT-4o，自报 "Claude 3.x, cutoff early-to-mid 2024" | Sonnet 3.5/4 档 |
| claude-sonnet-4-6 | 未测（只在停机期间打过 3 次 503） | — |

上游形态（所有名字共用）：

- **两条账号池**，按响应 id 分族。`msg_01…+22 位` 池 = Kiro/Bedrock：tool_use id `toolu_bdrk_01…`（sonnet-5、opus-4-7、4-8）和 `tooluse_02…`（opus-4-6，Bedrock Converse），问"你在什么环境 / 系统提示第一行"答 Kiro 固定拒答 "I can't discuss that."，usage 只计用户文本（input 1 + cache_creation 3）。`chatcmpl-<19 位数字>` 池 = Claude Code 账号池：自报 "I'm Claude, running in Claude Code"，一个 "hi" 计 `cache_creation 3710 + cache_read 18493 ≈ 22k token`（整套 Claude Code 系统提示），`billing_usage.source = oai_chat`。传了 temperature/top_p 或 max_tokens=999999 的请求基本落在 chatcmpl 池；同一名字连续请求两边都会打到。
- **thinking 全假**：sonnet-5 / opus-4-6 要求 `thinking enabled budget 1024` 时 0 个 thinking 块；不要求时 chatcmpl 池偶尔回一个 **没有 signature** 的 thinking 块（bench `identity/thinking_unsigned` FAIL）。
- **协议痕迹**：usage 多出 `billing_usage`、`claude_cache_creation_5_m_tokens`、`claude_cache_creation_1_h_tokens` 等非官方字段；流式没有 `ping`；`temperature+top_p` 同传 200、`max_tokens=999999` 不是 400 而是被站内预扣费拦下（403）；**max_tokens 不生效**（opus-4-6 设 220 实际输出 834 / 421 token）；识别系统提示的探针里模型复述了一段用户没发过的指令（"I don't quote or reproduce my system instructions verbatim… running here in Claude Code"）。
- new-api 自己的校验还在（thinking budget < max_tokens / ≥ 1024 会 400），说明请求先过 new-api 再进适配层。

## 稳定 / 并发 / 速度

- **02:08–02:21 整个分组停机 13 分钟**：所有名字 100% 503 "No available channel for model … under group kiro 高缓 (distributor)"，每分钟轮询到 02:21:56 自行恢复。`(distributor)` 说明这站本身是分销层，上游是另一套 new-api。
- 恢复后 **12 并发 12/12、24 并发 24/24**，两名字都无 429 / retry-after：

| 名字 | 串行 5 次 p50 | 12 并发 p50 / p95 | 24 并发 p50 / p95 / max |
|---|---|---|---|
| sonnet-5 | 2.19s | 4.14s / 4.81s | 4.12s / 6.67s / 12.12s |
| opus-4-6 | 4.1s | 4.89s / 5.29s | 4.88s / 5.92s / 7.12s |

- 吞吐（1 次流式 ~500 token）：sonnet-5 TTFT 4.4s、35 tok/s；opus-4-6 TTFT 4.3s、33 tok/s。screen IQ 8 题平均每题 24–27s。真流式（约 2 token/chunk）。

### 1000 个小探针（200 路并发，"Reply with exactly: OK"，max_tokens 5）

| 名字 | 成功 | 耗时 | 吞吐 | p50 / p90 / p99 / max | 池分布 | 实扣 |
|---|---|---|---|---|---|---|
| sonnet-5 | 999/1000（1 次 120s 读超时） | 133s | 7.5 req/s | 4.5s / 26.2s / 42.2s / 100.7s | Claude Code 池 761、Kiro 池 238 | $0.35 |
| opus-4-6 | 1000/1000 | 113s | 8.9 req/s | 4.0s / 6.4s / 11.7s / 94.0s | Claude Code 池 623、Kiro 池 377 | $0.65 |

- 没有 429、没有 retry-after，model 回显 1000/1000 一致，999/1000 正文就是 "OK"（1 次答 "I should flag this rather…"）。
- **sonnet-5 的路由是 Claude Code 池优先、打满后溢出到 Kiro 池**：前 600 个请求几乎全在 chatcmpl 池（p50 4.0s），第 800–999 个几乎全落 Kiro 池，而 sonnet-5 的 Kiro 池 p50 25s、p90 33s。所以 p90 26s 全部来自溢出段。opus-4-6 两池混着走，Kiro 池反而快（p50 3.7s）。
- 同期 sonnet-5 的 IQ 跑在后台（每题 40–60s 长输出），洪流没让它报错，只是拖慢。

### 长思考请求 100% 被 Cloudflare 掐断（HTTP 524）

sonnet-5 对 H7 / X7 / X8 三道需要长思考的题，非流式和 `stream=true` 各试 3 次，**全部在 ~127s 收到 Cloudflare 524，流式模式下 0 个事件、0 字节**。原因：这条池把 thinking 藏起来、文本开始前不向客户端吐任何数据，上游思考超过 Cloudflare 100 秒源站超时就被掐。opus-4-6 同题 34s 内答完（答错）没触发。**任何需要模型思考超过 100 秒的请求在这站上无法完成，流式也救不了。**

### 能力差距的来源：同在 Kiro 池，sonnet-5 通道开了隐藏思考，opus-4-6 通道没开

补跑 X3/X4/X5/X13/H4/X7 各一次（流式，记录 message_start id）：两个名字 11/11 次成功请求全落 **Kiro 池（`msg_01`）**，几百字的推理题不走 Claude Code 池（小探针才走）。流里都没有 thinking 事件、可见输出量相近，差别全在首字时间：sonnet-5 每题先沉默 53–114s 再答（服务端隐藏的扩展思考），5/5 对；opus-4-6 5–9s 就开始输出、没有思考阶段，X3/X5/H4/X7 错。X7 sonnet-5 思考超过 100s 即 524。结论：不是模型档次之差，而是站方给 sonnet-5 名字的 Kiro 通道开了 thinking、给 opus-4-6 的没开（再加 opus-4-6 混着 Sonnet 4 档的号）。原始记录 `results/worldclaw/probes/iqpool-1.txt`。

## 计费

- **站内 dashboard 的 total_usage 不能当花费**：这轮从 0.13 涨到 15.17，但 `max_tokens=999999` 触发的 403 报错里「用户剩余额度」从 $4.9957（02:24）降到 $3.075356（03:40），即两名字各一轮 screen（32 次）+ 完整 IQ（28–43 次）+ 12/24 并发 + 各 1000 个小探针 + 几十次手工探针，合计约 2,300 次调用**实扣约 $1.92**。usage 计数里混着预扣费 / 多次内部重试。要查真余额，发一个 `max_tokens=999999` 的请求读 403 里的数字，免费。
- 22k 隐藏提示在 chatcmpl 池是否计费无法从站内数据判定（余额变化太小，且 usage 端不可信）。1000 个小探针 sonnet-5 $0.35、opus-4-6 $0.65，即每次不到 0.1 分钱，比标价 (opus $15/M 入) 还低得多，这一点与"站内标价"自相矛盾，实际计费规则不透明。

## 怎么用（如果非要用）

- 这个分组里所有名字都是 Kiro/Claude Code 账号池的 Sonnet 4.5 / Opus 4.5 / Sonnet 4 档，**不存在 Opus 4.6/4.7/4.8 或 Sonnet 5**。要用就调 sonnet-5（倍率最低、后端不比 opus-4-x 差）。
- 不要依赖 thinking、max_tokens、temperature：都不会到模型。
- 能力上 sonnet-5（22/24）好于 opus-4-6（21/26），且 opus 名字贵 25 倍，更没理由调 opus-4-6。
- 需要长思考（>100s）的任务在 sonnet-5 上 100% 524，得拆小或换站。
- 分组随时会整段 503 十几分钟，且管理员在线改模型列表；接入前先探活。

原始数据：`results/worldclaw/`（screen + IQ + stability JSON、`REPORT-auto.md`、`probes/` 手工脚本与输出）、`results/worldclaw-burst24/`（24 并发）、`results/worldclaw/probes/flood-*.json`（1000 探针逐条记录）、`logs/worldclaw-*.log`。下面是 report.py 自动汇总（opus-4-7 / 4-8 / sonnet-4-6 的 UNREACHABLE 是停机期间的记录）。

---

# relay-bench 报告

结果文件: 5 个 (目录 <本地临时目录>)

## 0. 智力分档对比（拉开差距的核心）

每格 = 答对数/总题数（思考默认开启；`_off` = 强制关闭思考）。只统计当前题库 `suite/iq_keep.json` 里的 26 题；中转拒答/空响应不计入分母（括号内为剔除次数）。难度递增：reason < hard < xhard。

| 站点/模型 | reason | hard | xhard | 合计 |
|---|---|---|---|---|
| worldclaw/opus-4-6 | 6/6 | 5/6 | 10/14 | **21/26** |
| worldclaw/sonnet-5 | 5/6 | 5/6 | 12/12 | **22/24** (中转故障剔除2) |

### 各题耗时（reason+hard+xhard，思考开启，单位秒）

| 站点/模型 | reason均 | hard均 | xhard均 |
|---|---|---|---|
| worldclaw/opus-4-6 | 37.1 | 34.2 | 17.7 |
| worldclaw/sonnet-5 | 43.5 | 56.4 | 52.2 |

## 1. 总览矩阵

| 站点 | 模型 | 协议 | 结论 | 上游形态 | 参数一致率 | 知识前沿(阶梯/开放) | 指纹归属 | 自报 | tok比率EN | 注入tok | 缓存 | 缓存隔离/过期 | TTFT中位 | tok/s中位 | p50 | 并发成功 | soak错误率 | IQ直答 | IQ推理 | IQ困难 | IQ超难 | ctx20k | ctx60k | ctx130k | ctx230k | 红旗 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| worldclaw | claude-opus-4-6 | anth | FAKE/ALTERED | ? 注入≈-4 id=chatcmpl- | - | -/2026-01 | claude-opus-4-6 100% | anthropic/sonnet4 | - | -4 | - | - | 4.28 | 33.0 | 4.1 | 12/12 | - | - | 6/6 | 5/6 | 10/14 | - | - | - | - | 3 |
| worldclaw | claude-opus-4-7 | anth | UNREACHABLE | ? 注入≈- id= | - | -/- | - | -/- | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | 1 |
| worldclaw | claude-opus-4-8 | anth | UNREACHABLE | ? 注入≈- id= | - | -/- | - | -/- | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | 1 |
| worldclaw | claude-sonnet-4-6 | anth | UNREACHABLE | ? 注入≈- id= | - | -/- | - | -/- | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | 1 |
| worldclaw | claude-sonnet-5 | anth | FAKE/ALTERED | ? 注入≈-4 id=msg_01bDM | - | -/2024-10 | claude-sonnet-5 100% | anthropic/sonnet4.5 | - | -4 | - | - | 4.43 | 35.3 | 2.19 | 12/12 | - | - | 5/6 | 5/6 | 12/12 | - | - | - | - | 3 |

结论分级: CLEAN=无红旗; OK-ish=有轻微红旗; SUSPICIOUS=≥3个红旗; FAKE/ALTERED=知识截止/自报身份/签名证据表明不是所声称的模型。

## 2. 每个模型的红旗与关键证据

### worldclaw / claude-opus-4-6  → **FAKE/ALTERED**
- 红旗: 知道官方同型号不知道的事(映射到别的模型或注入); 自报家族=sonnet(仅参考:真模型也会跟着提示自报); thinking无签名
- 自报: ````json
{
  "vendor": "Anthropic",
  "model_family": "Claude",
  "model_version": "Claude 4 (Sonnet)",
  "knowledge_cutoff": "2025-03"
}
````
- 知识前沿: 阶梯=None 开放式=2026-01 判定=newer (声称型号 claude-opus-4-6)
- 数字指纹(ModelTrace, 闭集13模型): 指纹一致 ; 最像 claude-opus-4-6 100.0% ; 家族 claude 100% ; 候选 claude-opus-4-6 100%，gpt-5.4 0%，claude-opus-5 0% ; 有效回复 3/3 (3 次调用)
  - ⚠ 证据冲突: 指纹与声称型号一致，但知识前沿判 newer。两者互相独立，建议对截止前后事实做重复探针复核后再下结论。
- 泄露的隐藏系统提示: `I'm not going to quote my system prompt verbatim. Sharing the exact contents of system-level instructions isn't something I should do, as those instructions are`
- 并发12: 状态={'200': 12} p50=4.89s p95=5.29s
- [WARN] protocol/message_id_format: id=chatcmpl-1789626970884592171 (not the native msg_01+22 format -> generated by relay/adapter)
- [WARN] protocol/usage_shape: usage keys=['billing_usage', 'cache_creation', 'cache_creation_input_tokens', 'cache_read_input_tokens', 'claude_cache_creation_1_h_tokens', 'claude_cache_creation_5_m_tokens', 'input_tokens', 'output_tokens'] ; NON-NATIVE keys ['billing_usage', 'claude_cache_
- [WARN] protocol/model_echo: requested=claude-opus-4-6 echoed=claude-opus-4.6
- [WARN] protocol/stream_ping: ping events=0 (native Anthropic streams send periodic pings; converted streams usually don't)
- [FAIL] identity/family_mismatch: requested claude-opus-4-6 but the model identifies as Claude sonnet
- [WARN] identity/hidden_system_prompt_exposed: model quoted instructions you never sent: "I'm not going to quote my system prompt verbatim. Sharing the exact contents of system-level instructions isn't something I should do, as those instructions are meant to guide my behavior rather than "
- [FAIL] identity/thinking_unsigned: thinking block returned WITHOUT a signature -> not produced by the Anthropic API (adapter-fabricated or stripped)
- [FAIL] knowledge/frontier_vs_claim: knows events up to 2026-01 but real claude-opus-4-6 has cutoff 2025-05/2025-08 -> served model is NEWER than claimed (mapped to a different model)

### worldclaw / claude-opus-4-7  → **UNREACHABLE**
- 红旗: basic call failed
- 自报: ``
- 知识前沿: 阶梯=None 开放式=None 判定=None (声称型号 claude-opus-4-7)
- [WARN] protocol/basic_retries: all 3 attempts failed: [503, 503, 503]
- [FAIL] protocol/basic: HTTP 503 {'type': '<nil>', 'code': None, 'message': 'No available channel for model claude-opus-4-7 under group kiro (distributor) (request id: 202609170612172540899748268d9d6kFXQishT) (request id: 202609170612154270162718268d9d6MUDR1Ggq) (request id: 20260917

### worldclaw / claude-opus-4-8  → **UNREACHABLE**
- 红旗: basic call failed
- 自报: ``
- 知识前沿: 阶梯=None 开放式=None 判定=None (声称型号 claude-opus-4-8)
- [WARN] protocol/basic_retries: all 3 attempts failed: [503, 503, 503]
- [FAIL] protocol/basic: HTTP 503 {'type': '<nil>', 'code': None, 'message': 'No available channel for model claude-opus-4-8 under group kiro (distributor) (request id: 202609170611054965001168268d9d62xf9RDMY) (request id: 202609170611048828047208268d9d6dCsmYlaY) (request id: 20260917

### worldclaw / claude-sonnet-4-6  → **UNREACHABLE**
- 红旗: basic call failed
- 自报: ``
- 知识前沿: 阶梯=None 开放式=None 判定=None (声称型号 claude-sonnet-4-6)
- [WARN] protocol/basic_retries: all 3 attempts failed: [503, 503, 503]
- [FAIL] protocol/basic: HTTP 503 {'type': '<nil>', 'code': None, 'message': 'No available channel for model claude-sonnet-4-6 under group kiro (distributor) (request id: 202609170613508703251318268d9d6dGjcGYkk) (request id: 202609170613502547634888268d9d66PUyiyJ1) (request id: 202609

### worldclaw / claude-sonnet-5  → **FAKE/ALTERED**
- 红旗: 知识明显少于官方同型号(假映射); 默认无thinking块(Claude 5系应默认思考); thinking无签名
- 自报: `{"vendor": "Anthropic", "model_family": "Claude", "model_version": "Claude Sonnet 4.5", "knowledge_cutoff": "2025-01"}`
- 知识前沿: 阶梯=None 开放式=2024-10 判定=older (声称型号 claude-sonnet-5)
- 数字指纹(ModelTrace, 闭集13模型): 指纹一致 ; 最像 claude-sonnet-5 100.0% ; 家族 claude 100% ; 候选 claude-sonnet-5 100%，claude-opus-4-8 0%，claude-opus-5 0% ; 有效回复 3/3 (3 次调用)
  - ⚠ 证据冲突: 指纹与声称型号一致，但知识前沿判 older。两者互相独立，建议对截止前后事实做重复探针复核后再下结论。
- 与官方同型号金标准逐题对比: 官方知道而它不知道=[] ; 它知道而官方不知道=[] ; 双方都知道=0 ; 开放式探针比官方更旧=['C1', 'C3', 'C5', 'C7', 'C9', 'C10'] 更新=[]
- 泄露的隐藏系统提示: `I can't do that. I don't quote or reproduce my system instructions verbatim.

I'm Claude, an AI assistant made by Anthropic, running here in Claude Code (Anthro`
- 并发12: 状态={'200': 12} p50=4.14s p95=4.81s
- [WARN] protocol/message_id_format: id=msg_01bDMGgr5E6K6fpmkdX3FC (not the native msg_01+22 format -> generated by relay/adapter)
- [WARN] protocol/usage_shape: usage keys=['billing_usage', 'cache_creation', 'cache_creation_input_tokens', 'cache_read_input_tokens', 'claude_cache_creation_1_h_tokens', 'claude_cache_creation_5_m_tokens', 'input_tokens', 'output_tokens'] ; NON-NATIVE keys ['billing_usage', 'claude_cache_
- [FAIL] protocol/thinking_default: default request has thinking block=False ; real claude-sonnet-5 -> True
- [WARN] protocol/stream_ping: ping events=0 (native Anthropic streams send periodic pings; converted streams usually don't)
- [WARN] identity/hidden_system_prompt_exposed: model quoted instructions you never sent: "I can't do that. I don't quote or reproduce my system instructions verbatim.\n\nI'm Claude, an AI assistant made by Anthropic, running here in Claude Code (Anthropic's terminal-based CLI tool). I'm happ"
- [FAIL] identity/thinking_unsigned: thinking block returned WITHOUT a signature -> not produced by the Anthropic API (adapter-fabricated or stripped)
- [FAIL] knowledge/frontier_vs_claim: knows events only up to 2024-10 but real claude-sonnet-5 has cutoff 2026-01 -> served model is OLDER than claimed (fake mapping)

## 3. 知识截止阶梯 (✓知道 ?不知道 ✗答错 !错误)

| 题 | 日期 | worldclaw/opus-4-6 | worldclaw/sonnet-5 |
|---|---|---|---|
| K00 | 2024-11 | ✓ | ✓ |

## 3b. 开放式近期知识探针 (答案所属年代)

| 题 | worldclaw/opus-4-6 | worldclaw/sonnet-5 |
|---|---|---|
| C1 | 2025-05 `Pope Leo XIV (Robert F` | 2013-03 `Pope Francis (Jorge Ma` |
| C2 | 2024-10 `Shigeru Ishiba is the ` | 2024-10 `Shigeru Ishiba is the ` |
| C3 | 2026-01 `Zohran Mamdani, who wo` | 2022-01 `Eric Adams` |
| C4 | 1989-06 `Ayatollah Ali Khamenei` | 1989-06 `Ali Khamenei is Iran's` |
| C5 | 2024-02 `The Kansas City Chiefs` | 2024-02 `Kansas City Chiefs won` |
| C6 | 2022-12 `Argentina won the 2022` | 2022-12 `Argentina won the 2022` |
| C7 | 2024-10 `Han Kang, awarded the ` | 2023-10 `Jon Fosse, awarded the` |
| C8 | 2025-05 `Claude Opus 4, with mo` | 2024-10 `Claude 3.5 Sonnet (the` |
| C9 | 2025-02 `GPT-4.5 (research prev` | 2000-01 `GPT-4 (specifically GP` |
| C10 | 2021-01 `Joe Biden.` | 2021-01 `Joe Biden.` |

## 4. IQ 分题矩阵

| 题 | 模式 | worldclaw/opus-4-6 | worldclaw/sonnet-5 |
|---|---|---|---|
| R2 | default | ✓ | ✓ |
| R3 | default | ✓ | ✓ |
| R4 | default | ✓ | ✓ |
| R7 | default | ✓ | ✓ |
| R9 | default | ✓ | ✓ |
| R10 | default | ✓ | ✗ |
| H1 | default | ✓ | ✓ |
| H2 | default | ✓ | ✓ |
| H3 | default | ✓ | ✓ |
| H4 | default | ✓ | ✓ |
| H5 | default | ✓ | ✓ |
| H6 | default | ✗ | ✗ |
| X1 | default | ✓ | ✓ |
| X2 | default | ✓ | ✓ |
| X3 | default | ✗ | ✓ |
| X4 | default | ✗ | ✓ |
| X5 | default | ✓ | ✓ |
| X6 | default | ✓ | ✓ |
| X7 | default | ✗ | ✗ |
| X8 | default | ✗ | ✗ |
| X9 | default | ✓ | ✓ |
| X10 | default | ✓ | ✓ |
| X11 | default | ✓ | ✓ |
| X12 | default | ✓ | ✓ |
| X13 | default | ✓ | ✓ |
| X14 | default | ✓ | ✓ |

## 5. 同站点跨模型聚类 (相同输出 = 很可能同一上游)
