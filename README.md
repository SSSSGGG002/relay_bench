# relay-bench：中转站真假 / 协议 / 上下文 / 缓存 / 速度 / 智力 一体化测试方案

> 基线（官方金标准、冻结参考站、题库）和全部测试指标的汇总见 [docs/BASELINES.md](docs/BASELINES.md)。

## 0. 给协作者：从哪里开始

1. **测试标准**：[docs/BASELINES.md](docs/BASELINES.md)。写了每类模型（Claude / GLM / DeepSeek / GPT）该对照哪份基线、测哪些指标、各指标怎么判读、参考站的冻结数值。
2. **冻结基线**：`suite/golden/`（官方知识金标准）和 `suite/reference/`（参考站 ikuncode、智谱官方、spatialai 等）。新站拿同一脚本、同一参数跑完，直接和这些 JSON 比。
3. **历史报告**：[reports/](reports/README.md)，09-09 起各站的实测结论，按模型分类有索引。
4. **环境**：`python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`，之后都用 `.venv/bin/python` 跑。key 只通过 `RB_KEY` 环境变量或 `--key` 传，不要写进文件。
5. **对比流程**（以 Claude 为例）：先 `refcheck.py suite/reference/<参考>.json` 确认参考站没变（SAME 才能复用冻结值），再对新站跑 `bench.py` / `injcache.py` / `costcheck.py --ref ...`。延迟和稳定性只能同一天、同一条路线对比，不要拿别人机器上的延迟当常量。
6. 自己的测试输出在 `results/`、`logs/`，已被 `.gitignore` 排除；新报告脱敏后（key 只留前后几位、不写服务器 IP）放进 `reports/` 再提交。

目标：用**造假者改不了的证据**判断一个 API 中转站（new-api / one-api 之类）背后到底是什么模型、请求有没有被改写、上下文有没有被截、缓存有没有生效、速度和稳定性如何。
同时支持 Anthropic Messages 协议（`claude-*`）和 OpenAI Chat Completions 协议（`gpt-*` 等），一套命令跑完，`report.py` 出对比矩阵。

## 1. 为什么"智力题"拉不开差距

- 中等难度题（事件循环、缓存策略、组合计数）Sonnet 4.5 级别模型就能对 80% 以上，再往上只剩噪声；模型间 1 道题的差距在统计上没有意义。
- 开了 thinking 之后各档模型进一步收敛。要看"裸能力"必须 `thinking disabled`（本方案的 direct 档和 `--iq-nothink`）。
- 更根本的问题：智力只是间接证据。中转站可以把 opus-5 映射到一个同样能做对题的 Sonnet 4.5，你用智力题永远证明不了它是假的。

所以本方案把**身份证据**放在第一位，智力放在最后一位，只作为佐证。

## 2. 测试维度与检测原理（每一项都写明"造假者为什么改不了"）

| 组 | 测试 | 检测什么 | 为什么可信 |
|---|---|---|---|
| protocol | `message_id_format` | 响应 id 是否是官方格式（Anthropic `msg_01`+22 位 / OpenAI `chatcmpl-`） | 适配层重新生成 id 会露馅；`resp_` 前缀 = Responses API 转换；`toolu_bdrk_` = Bedrock；`tooluse_` = Bedrock Converse |
| protocol | `usage_shape` | usage 里有没有非官方字段（`credit_usage` 等）、缺不缺官方字段 | 计费适配层的痕迹 |
| protocol | `thinking_default` | 不传 thinking 时是否出现 thinking 块 | Opus 5 / Sonnet 5 / Fable 默认思考；4.8 及更早默认不思考。官方行为，改不了 |
| protocol | `prompt_injection_by_usage` | 5 个 token 的请求被计成几百上千 token | 上游注入了隐藏系统提示（Claude Code / Kiro / Codex 账号池的典型特征） |
| protocol | `stream_ping` / `stream_obfuscation` | Anthropic 原生流有 `ping` 事件；OpenAI 原生流每个 chunk 带 `obfuscation` 字段 | 协议转换层几乎不会伪造这些 |
| passthrough | `param_strictness` | 故意发非法参数，看是否按官方规则 400 | Claude 5 系列 temperature/top_k/budget_tokens/prefill 必 400；Fable 禁 thinking disabled；Opus 5 支持消息内 system 而 Sonnet 5 不支持；GPT 推理模型拒绝 temperature/max_tokens/logprobs/非法 effort。全部 200 = 请求被改写后转发 |
| protocol | `stop_sequences` / `max_tokens_honored` | 你传的参数有没有真的生效 | 直接影响你的账单和程序正确性 |
| protocol | `max_tokens_limit_leak` | `max_tokens=999999` 时官方 400 会说出真实上限和真实模型名 | 错误信息泄露真实模型 |
| protocol | `count_tokens_endpoint` / `responses_endpoint` / `models_endpoint` | 辅助端点是否存在、`/v1/responses` 是否回显注入的 `instructions` | 直接把隐藏提示词抓出来 |
| identity | `self_report` / `vendor_word` / `api_string` | 模型自报厂商、家族、版本、截止 | 单独不可靠，但和知识阶梯交叉验证很有力 |
| identity | `system_prompt_leak` / `date_awareness` | 让模型复述它收到的系统提示 | 直接读出 "You are Kiro / Claude Code / Codex" |
| identity | `thinking_artifacts` / `thinking_signature_tamper` | thinking 块有没有 `signature`；篡改后重放是否被 400 | 只有 Anthropic 后端能验签。无签名 = 不是官方 API 出来的 |
| identity | `reasoning_artifacts` / `encrypted_reasoning_tamper` | OpenAI Responses 的 `encrypted_content` 是否存在、篡改后是否 400 | 同上，只有 OpenAI 后端能解密 |
| knowledge | `ladder`（24 题，2024-11 → 2026-09 逐月事实） | 模型知道到哪个月 | **知识截止是唯一无法通过改写请求伪造的指纹**。每个型号的官方 reliable/training cutoff 已内置，前沿明显早于声称 = 假映射 |
| knowledge | `recency`（10 题开放式："现任教宗/日本首相/你知道的最新 Claude、GPT 型号"） | 同上，但模型必须给答案，不受"不确定就答 UNKNOWN"的压制 | 把"过度保守"和"真不知道"区分开 |
| tokenizer | `differential` | 同一段文本增量的 token 计数 | GPT 通道必须与 tiktoken o200k 完全一致；Claude 4.7+/Sonnet 5/Fable 的新分词器比旧的多 ~30%；比率乱飞 = usage 是编的 |
| context | `needle_20k/60k/130k/230k` | 三根针（10%/50%/90% 深度）召回 + usage 是否随长度线性 | 截断、丢中段、1M 上下文是否真实（200K 模型 230k 必报错） |
| context | `system_rule_at_60k` / `multiturn_memory` | 长上下文下系统提示是否还被遵守；20 轮历史是否被丢 | 中转站常见的"丢 system / 截历史" |
| cache | `prompt_cache` | 同一 5000 token 前缀连打 2-3 次，`cache_read` 是否命中 | 账号池轮询不同账号 → 永远不命中，你一直付全价 |
| cache | `response_replay` | 两次相同请求是否返回同一个 id | 有些站直接回放缓存的响应 |
| cache | `--cache-ttl`：`cache_isolation` / `cache_1h_ttl` / `cache_5m_expiry` | 换一个同样大小的新前缀必须不命中；1h TTL 写入应记在 `ephemeral_1h_input_tokens`；闲置 5.5 分钟后 5 分钟缓存应失效 | 新前缀也报命中 = usage 造假；过期后仍命中 = TTL 不对或造假 |
| stability | `sequential` / `burst N`（`--burst 12`，默认 full 档 8）/ `usage_drift` / `model_echo_drift` | 错误率、空正文、并发下的状态分布、p50/p95、`retry-after`、同样请求 usage 漂移 | 漂移 = 多账号多版本提示词轮询 |
| soak | `--soak 10`：每 10 秒一个小流式请求持续 N 分钟，按分钟分桶 | 长窗口错误率曲线、p50/p95/max、空响应、型号回显漂移 | 几分钟的抽样看不出的间歇性故障 |
| speed | `throughput`（`--speed-repeat 3`，取中位数并记录 min/max）/ `fake_streaming` / `long_output_2500tok` | TTFT、tok/s、chunk 粒度、长输出是否断流 | 33 秒后突然 150 tok/s = 上游非流式，中转站假装流式 |
| iq | reason 6 题 / hard 6 题 / xhard 14 题（共 26 题，按实测区分度筛选） | 前沿模型 vs 降级模型的地板检查；xhard 档负责前沿之间的顶端分辨 | 答案全部由代码生成并验证；`suite/iq_keep.json` 控制保留哪些题，`suite/iq_full.json` 是完整题库；`gen_iq.py --seed N` 随时换一套。direct（禁思考直答）档已删除：它被输出格式和"思考无法关闭"污染，没有区分度 |
| cluster | 4 个固定提示 | 同一站点不同型号输出是否逐字相同 | 相同 = 同一个上游模型套了多个名字 |

## 3. 使用

```bash
cd relay-bench
python3 gen_iq.py --seed 20260909          # 生成/更换题库（答案自动计算）
python3 bench.py --label 站点名 --base https://xxx --key sk-... \
    --models claude-opus-5,claude-sonnet-5,gpt-5.6-sol --profile quick      # 每个模型约 100 次调用、4-6 分钟
python3 bench.py ... --profile full --big-context --iq-nothink              # 加 60k/130k/230k 上下文、并发、长输出、验签篡改、hard 题
python3 bench.py ... --profile full --speed-repeat 3 --burst 12 --soak 10 --cache-ttl        # 更全面：吞吐 3 次取中位、12 并发、10 分钟 soak、缓存隔离/1h/过期检查（多 ~20 分钟）
python3 bench.py ... --profile screen --concurrency 8                                       # 快速筛选：身份自报 + 开放式知识探针 + 8 道高区分度智力题 + 1 次吞吐，约 2-3 分钟，先淘汰假货再跑 full
python3 bench.py ... --only knowledge,identity                              # 只跑某几组（结果会合并进已有文件）
python3 bench.py ... --only iq --iq-ids R9                                   # 只重跑某几道题
python3 report.py                                                            # 汇总为 REPORT.md
```

依赖：`python3 -m pip install httpx tiktoken`，Node 22（仅题库生成需要）。

## 3b. 两步法：先 screen 再 full

1. `--profile screen`：约 30 次调用、2-3 分钟。看三样东西：自报厂商/家族是否对得上、开放式知识探针的年代（现任教宗、日本首相、最新 Claude/GPT 型号）是否符合声称型号的截止、8 道 screen 题的得分。声称前沿模型却在 screen 题上低于 6/8，或知识年代明显偏早，直接淘汰。
2. 通过的再跑 `--profile full`（加 `--speed-repeat 3 --burst 12 --soak 10 --cache-ttl`），拿协议严格性、上下文、缓存、稳定性、完整 IQ。

screen 题目由 `suite/iq_screen.json` 指定（默认 R7 模幂、R10 事件循环、R3 字符串流水线、R4 约瑟夫、R9 Python 输出、H2 车放置计数、H3 队列模拟、X14 Fletcher-16），选取标准是实测中前沿模型接近全对、降级模型明显失分、单题 30 秒内可答。

## 4. 怎么读报告

1. 先看 **knowledge 前沿** 和 **recency**：这是定性结论。声称 Opus 5（截止 2026-05）却只知道 2025-08 以前的事 → 假。
2. 再看 **identity**：自报 "Sonnet 4.5" + 隐藏提示 "You are Kiro" + `toolu_bdrk_` id → 上游是 Kiro/Bedrock 账号池。
3. **passthrough 一致率**低（尤其"全部 200"）说明请求被适配层重写：你传的 temperature/stop/max_tokens 可能根本没到模型。
4. **tokenizer / usage** 异常说明账单数字不可信。
5. **cache / stability / speed** 决定实际使用体验和成本。
6. **iq** 只用来交叉验证：实测 Opus 5 / Sonnet 5 / Fable 5.1 在这类题上几乎打平（52/55 vs 52/57），它们之间排不出名次；但前沿与降级货差距明显（降级货约 12-24/32），所以把它当地板检查：声称 opus-5 却只有 20 分上下，配合知识前沿就能定性。


**自报截止/型号为什么不能信：** Claude Code 的系统提示里就写着当前配置型号和它的知识截止（例如 "Assistant knowledge cutoff is May 2026"），模型问到时只是复述这一行。实测同一 bitmiracle opus-5 通道：注入这句 → 答 "2026年5月"；不注入 → 答 "2024年10月"；而真实事实（现任教宗、日本首相、最新 Claude 型号）与注入与否无关。所以判断以 knowledge/recency 探针为准，自报只作参考。

**自报型号同样不能信（已用真 Fable 验证）：** twskyhope 上验过签名的真 Fable 5.1，在注入 Kiro 风格系统提示后同样自报 "Claude Sonnet 4.5、截止 2025-01"，注入 Opus 5 提示就自报 "Opus 5、2026-05"。所以 bitmiracle 通道"自曝 Sonnet 4.5"本身不是证据；报告里自报家族/厂商只标记为参考，FAKE 判定只由知识前沿、混合池、签名/协议证据触发。

**官方金标准（推荐）：** 只要本机 Claude Code 登录了订阅，`python3 golden.py claude-opus-5 claude-sonnet-5 claude-fable-5-1` 会通过 `claude -p` 直连 api.anthropic.com，用同一套知识阶梯 + 开放式探针给官方模型打基线，存到 `suite/golden/<model>.json`；之后 report.py 对声称同型号的中转做**逐题对比**（官方知道而它不知道 = 疑似降级；它知道而官方不知道 = 映射到别的模型或注入），不再拿标称截止日期硬比。原因是实测官方模型对截止前 4-6 个月的事件大多答 UNKNOWN：官方 Opus 5（标称截止 2026-05）不知道 2026 年 2 月的超级碗、Eurovision、NBA，可靠记忆只到 2025 年 11 月；官方 Sonnet 5（标称 2026-01）连 2025 年 10 月的高市早苗都答 UNKNOWN。用标称日期判"知识太旧"会把真模型误判成假货。

**官方模型的自报同样不可靠：** 官方 Opus 5 被要求"只凭训练回答"时自报 "Claude Opus 4、截止 2025-01"（无论有没有 Kiro 风格提示）；官方 Sonnet 5 / Fable 5.1 自报正确，但那可能是复述了 Claude Code 系统提示里的型号。

**用金标准定型号的实例：** twskyhope 的 "claude-fable-5-1" 对 2026 年 2-3 月的事实（超级碗 LX、奥斯卡、伊朗新领袖、2026 澳网）3 次重复全部 UNKNOWN，而官方 Fable 5.1 通过订阅直连 3 次全对；它只知道 2026 年 1 月及以前的事（Opus 4.6 发布）。知识止于 2026-01 正是 Fable 5（截止 2026-01）的特征，签名有效说明确是 Anthropic 的 Fable 系列，所以结论是**以 5.1 的名义提供 Fable 5**。方法要点：对声称截止前 2-4 个月的事实各重复 3 次，官方稳定答对而中转稳定 UNKNOWN，才算定案；单次结果会被采样噪声干扰。

## 5. 局限

- 没有官方 API 作为"金标准"对照；参数严格性预期来自官方文档（2026-09），`suite/knowledge.json` 里的 `model_cutoffs` 也来自官方模型页。
- 知识阶梯需要每隔几个月补充新事实（编辑 `suite/knowledge.json`，附来源）。
- 智力题的绝对分数不能跨题库比较；同一题库、同一 seed 下的相对差距才有意义。

## 6. GLM-5.3-flash（智谱）官方基准模式 —— 2026-09-10 新增

思路变化：之前没有官方 API 做金标准，只能靠官方文档推断。现在有智谱官方 key，所以**先把官方直连跑一遍存成基准，再让每个中转站与基准逐项比对**（`compare.py`）。

### 6.1 官方接口的指纹（2026-09-10 实测，用于识别中转站是否直连）

| 维度 | OpenAI 兼容 `https://open.bigmodel.cn/api/paas/v4` | Anthropic 兼容 `https://open.bigmodel.cn/api/anthropic` |
|---|---|---|
| 响应 id | 14 位时间戳 + 16 位 hex（`20260910141811 7b5325c9dfd944d8`），顶层还有 `request_id` | `msg_` + 同样 30 位；signature = 24 位 hex（不是真正的 Anthropic 签名，篡改后不校验） |
| usage 字段 | `prompt_tokens/completion_tokens/total_tokens/prompt_tokens_details.cached_tokens/completion_tokens_details.reasoning_tokens`，无 `system_fingerprint`/`service_tier` | `input_tokens/output_tokens/cache_read_input_tokens/server_tool_use/service_tier`，无 `cache_creation_input_tokens` |
| 思考 | **永远开启**，`thinking.type=disabled` / `reasoning_effort=none|minimal|medium|xhigh|ultra` 一律 400 code 1210；只接受 `low/high/max` | 同上；`output_config.effort=low/high/max` 可用，`thinking.disabled`/`effort xhigh` 400 |
| 参数校验 | `temperature=5` 照样 200（不校验范围）；`max_tokens=999999` 400 "[1,131072]"；**`max_completion_tokens` 被静默忽略**（只认 `max_tokens`）；`logprobs`/`n=2`/未知字段 全部 200 忽略；模型名错 400 code 1211 | `temperature/top_k/budget_tokens/prefill/system-in-messages/tool_choice any/未知 beta 头` 全 200 |
| 流式 | 逐 token chunk，`reasoning_content` 增量在前，usage 在最后一个 chunk；无 `obfuscation` 字段 | 有 `ping` 事件；`x-process-time` 头 |
| 工具调用 id | 同步 `call_` + 有符号 int64；流式 `call_` + 24 hex | `call_` + 24 hex（不是 `toolu_`） |
| 辅助端点 | `POST /tokenizer` 200（官方分词计数，中转站基本 404）；`GET /models/{id}` owned_by=z-ai；`/responses` 404 | `/v1/messages/count_tokens` 200 |
| 分词 | 英文 ≈ 1.01× o200k，中文 ≈ 0.79× o200k | 同 |
| 缓存 | 隐式缓存，`cached_tokens` 报告命中，命中价 0.23 元/M（原价 0.8 输入 / 2.8 输出） | `cache_read_input_tokens` |
| 限流 | 超限返回 code 1302（账户限速）/ 1305（模型过载） | 同 |

### 6.2 跑法

```bash
# 官方基准（两种协议都跑）
python3 bench.py --label zhipu-official --base https://open.bigmodel.cn/api/paas/v4 --key <官方key> --models glm-5.3-flash --profile full --iq-nothink --big-context
python3 bench.py --label zhipu-official-anthropic --base https://open.bigmodel.cn/api/anthropic --key <官方key> --models glm-5.3-flash --dialect anthropic --profile full --iq-nothink
# 中转站（同样参数）
python3 bench.py --label 站点-分组 --base https://xxx --key sk-... --models glm-5.3-flash --profile full --iq-nothink --big-context
# 出报告
python3 report.py            # 单站体检 REPORT.md
python3 compare.py --baseline zhipu-official   # 与官方逐项比对 COMPARE.md
```

`bench.py` 对 `glm*` 模型自动：走 `/chat/completions`（base 以 `/v4` 结尾时去掉 `/v1`）、用 `max_tokens` 而不是 `max_completion_tokens`、"关闭思考" 档改为 `reasoning_effort=low`、期望厂商=智谱、分词参照官方 `/tokenizer` 而不是 o200k。

### 6.3 compare.py 的判定

- ✅ 与官方一致：id/usage/字段/参数校验/分词/思考/知识/智力/缓存全部在官方误差内。
- 🟡 模型一致但经过协议改写层：模型层指标一致，但 id 被重生成、usage 多了 new-api 字段、`max_completion_tokens` 被改写成生效、参数校验结果与官方不同 —— 典型的 new-api 转发（不一定是假，但你发的参数不是原样到模型）。
- ⚠️/❌：知识前沿、自报厂商、默认思考、同题年代混合、智力分数与官方偏离 —— 不是官方 glm-5.3-flash。

### 6.4 配套脚本（2026-09-10）

| 脚本 | 作用 | 输出 |
|---|---|---|
| `ops.py --ch label=[anthropic@]base:key ...` | 运营指标专项：多站点同窗口交错 30 轮延迟、5 轮流式速度、默认思考写代码 TTFT、8/16 并发、20k 缓存命中 + TTL(60/180/300/600s) + 多轮前缀缓存 | `results/ops/*.json`、`OPS.md`（`--report-only` 可重建） |
| `xcache.py --official base:key --relay label=base:key` | 跨账号缓存互通：官方写入→中转首读命中 = 同一后端（智谱隐式缓存全局共享） | `results/xcache.json` |
| `greedy.py --official base:key --ch ...` | 量化/部署差异：do_sample=false 贪心分歧（与官方样本匹配前缀占比）、关思考精度题、200k 十针 | `results/greedy/*.json`、`GREEDY.md` |
| `compare.py --baseline zhipu-official` | 每个中转与同模型同协议官方基准逐项比对，按 身份/智力/协议/上下文/运营 分类给结论 | `COMPARE.md` |
| `final.py` / `build_page.py` | 汇总为 `FINAL.md` / 网页 `site/glm53flash-audit.html` | |
| `RELAY_IQ_BANK=suite/iq.v3.json python3 bench.py ...` | 固定智力题库（v3 = 原 33 题；`iq_full.json` = 40 题含 X8–X14） | |

注意：智谱官方本身的三个特性不能当造假证据——低强度思考偶发空正文、"现任教宗"答案摇摆（pool_mix 会 FAIL）、贪心解码非确定（自身一致性仅 ≈0.19）。

## 7. 版本管理与协作站「Pull & Reload」—— 2026-09-16 新增

协作站「设置」页上 relay-bench 的 **Pull & Reload** 执行的是
`git pull --ff-only`（见 relay-collab `src/app/api/engines/reload/route.ts`），
所以 `RELAY_BENCH_DIR` 必须是一个 git 工作副本。

远端用的是**同一台服务器上的裸仓库** `/opt/relay-bench.git`：服务器那次 pull 是本地
文件系统操作，不走网络、不需要凭据，也就不会卡在交互式认证上。

    Mac ~/cctest/relay-bench  --push over ssh-->  /opt/relay-bench.git (裸)
                                                        |
                                 /opt/relay-bench  <--- pull --ff-only（网页按钮）

当前实际配置（2026-09-16）：

    origin = ssh://root@<北京服务器>/opt/relay-bench.git
    服务器工作副本 = /opt/relay-bench（RELAY_BENCH_DIR）

一次性配置：在服务器上跑 `relay-collab/deploy/relay-bench-git-origin.sh`，
按提示从 Mac `git push -u origin main`，再跑一次同一个脚本即可。脚本可重复执行，
不会碰 `.venv/`、`results/`、`logs/` 这些未跟踪文件；如果服务器上**被跟踪**的文件
与仓库不一致，它会打印 diff 然后停下，不覆盖（要覆盖得显式加 `--force`，会先备份）。

日常改动流程：

```bash
cd ~/cctest/relay-bench
# 改 bench.py / suite/*.json …
git commit -am "..."
git push
# 然后在协作站「设置」页点 relay-bench 的 Pull & Reload
```

CLI 引擎是每次跑测试时新起子进程，所以拉完不用重启 Web 或 Worker。

**只跟踪引擎本身**：各 `*.py`、`suite/`（题库 / knowledge / golden 基线）、`proxy/`，
共 27 个文件约 436K。`results*/`、`logs/`、`site/`、各类备份，以及 report/compare/ops/
greedy/final 生成的 `REPORT*.md`、`COMPARE*.md`、`OPS*.md`、`GREEDY*.md`、`FINAL*.md`
都在 `.gitignore` 里——这些脚本会原地覆盖同名文件，跟着版本走只会天天冲突，而且
服务器并不需要另一台机器的跑测结果。要把报告也纳入版本管理，删掉 `.gitignore`
里对应几行即可。

**注意**：`git pull --ff-only` 要求服务器那份没有本地改动。以后不要直接编辑
`/opt/relay-bench` 下被跟踪的文件，否则按钮会报 pull 失败——改在 Mac 上、推上去。

## 8. 数字指纹归属（ModelTrace）—— 2026-09-17 新增

`bench.py` 新增 `fingerprint` 组，screen / quick / full 默认都跑，也可单独 `--only fingerprint`。
原理：让模型连续给出几百个 1–355 的「随机」整数，按取值分布和 ModelTrace 指纹库比对，
给出**最像哪个具体模型**及概率。它是和知识前沿、协议特征互相独立的一条证据，
能分开「知识都判 older」但背后模型不同的渠道（apizn Kiro opus-5 → opus-5 100%，dragonapi Kiro opus-5 → haiku-4-5 95%）。

```bash
python bench.py --label <站> --base <url> --key <key> --models claude-opus-5,claude-sonnet-5 --only fingerprint
```

- 每个模型 3 条有效回复（最多试 6 次），约 50–100 秒。runner 调用不计入 `meta.calls`，次数见 `metrics.fingerprint_calls`。
- 依赖协作站旁边装好的引擎，默认路径 `../relay-collab/engines/modeltrace`（`.venv` 里有 numpy）和
  `../relay-collab/engines/modeltrace-runner/run.py`；可用 `MODELTRACE_DIR` / `MODELTRACE_PYTHON` / `MODELTRACE_RUNNER` 覆盖。
  没装时这一组记 INFO 跳过，不影响其他组。relay-bench 自己的 venv 不需要 numpy。
- 只对 GPT / Claude 型号跑（按型号名 `claude*` / `gpt*` / `o<数字>` 判断）。GLM、DeepSeek、Kimi 等国模自动 INFO 跳过，不发请求：库里没有这些家族，闭集分类器照样会报出某个 GPT/Claude，白花 3–6 次调用还会误导。
- `RELAY_BENCH_NO_FINGERPRINT=1` 跳过这一组。协作站 worker 会设置它，因为站里把指纹作为独立引擎单独跑。
- 结果：`metrics.fingerprint_*`、`extra.fingerprint`（含每次请求解析出多少数字和回复开头），
  原始产物在 `results/<label>/<model>.modeltrace/`。

**REPORT.md**：总览表多了「指纹归属」列（`型号 概率·标签`），每个模型的详情里列出候选排名。红旗规则比较保守：

| 指纹判定 | finding | 红旗 |
|---|---|---|
| 指纹一致 | PASS | 无。和知识前沿结论冲突时另起一行提示「证据冲突」，**不会**撤销其他红旗 |
| 同家族·版本不符 | WARN | 概率 ≥80% 记一条普通红旗「(疑似降级)」，单独不判 FAKE |
| 家族不符（家族概率 ≥90%） | FAIL | 「(假映射)」→ FAKE/ALTERED |
| 家族不符（置信度低） | WARN | 普通红旗 |
| 库外型号 / 样本不足 | INFO / WARN | 无 |

**局限**：闭集，只能在库里 13 个模型中选（gpt-5.4/5.5/5.6-sol/terra/luna/6-astra，claude-haiku-4-5/sonnet-4-6/sonnet-5/opus-4-6/4-7/4-8/opus-5）；
**没有 fable、3.7 Sonnet、Sonnet 4.5 和国模**。所以某个名字被判「一致」，不能排除它其实是库里没有的相近型号
（例如 Sonnet 4.5 冒充 Sonnet 5）。库的参考数据也是作者经中转采集的。
同一渠道从不同出口测，可能打到不同后端（见鑫旺），报告里请注明出口。

`REPORT_OUT=/path/REPORT.md python report.py <results>` 可以把报告写到别处，不覆盖仓库根目录共享的 REPORT.md。
测试：`python test_fingerprint.py`（假 runner 覆盖全部判定 + 本地假中转端到端，不联网、不花钱）。

## 参考站（冻结基线）与 refcheck.py
中转站之间横向对比时，不必每次重跑参考站。`suite/reference/<name>.json` 冻结了参考站的全量结果：IQ 逐题、知识、上下文、缓存行为、号池指纹，以及带日期和路线的延迟。IQ 题库固定为 `suite/iq.ref-20260924.json`（md5 ad1f46e9…，与 `suite/iq.json` 在 09-24 时一致）。
复用前先跑漂移检查：

    RB_KEY=<参考站 key> python3 refcheck.py suite/reference/ikuncode-kiro.json --direct          # 约 5-15 分钟
    RB_KEY=<参考站 key> python3 refcheck.py suite/reference/ikuncode-kiro.json --direct --quick  # 只查指纹和知识，约 1 分钟

- 输出 SAME：直接复用冻结的 IQ / 知识 / 上下文。输出 DRIFT：参考站换了池或模型，先重测。结果存到 `results/refcheck/`。
- 延迟、稳定性、缓存不当作常量复用：它们随路线和时段变化。09-24 走 Mac/Clash 测 ikuncode，30 并发有一半 TLS 失败；09-25 从北京直连是 120/120。所以新站一律在北京服务器 `/root/bltest` 上用 `lat.py` / `soak.py` 测，需要时当天顺手给参考站也跑一遍（约 10 分钟）。
- ikuncode 的 sonnet-5 实际是 Sonnet 4.5。作为参考，它代表"Kiro 池里最好的 Sonnet 档"，不代表真 Sonnet 5；真模型的标尺仍然是 `suite/golden/`（官方）和历史真 Opus 5 / Sonnet 5 的约 95%。

## 9. GLM 中转横向基准 glmsuite.py —— 2026-09-25 新增
测 GLM（glm-5.3-flash 等）中转站用 `glmsuite.py`。它和 `bench.py` 的区别：一次运行把**新站、官方、参考站放在同一时段、同一台机器上交错测**，每一次调用都落盘（`results/glmsuite/<run>/<group>.jsonl`），最后 `summarize` 出 `summary.json` / `SUMMARY.md`。
官方和 ikuncode 两家已冻结成参考基线：`suite/reference/zhipu-official-glm53flash.json`、`suite/reference/ikuncode-glm53flash.json`。

```bash
# 在北京服务器上跑（/root/glmtest；key 只放在服务器的 glmenv.sh，测完删掉）
export KEY_OFFICIAL=<智谱官方 key> KEY_NEWSTA=sk-... KEY_IKUNCODE=sk-...   # --ch <label> 的 key 读环境变量 KEY_<LABEL>
CH="--ch official=https://open.bigmodel.cn/api/paas/v4 --anth official=https://open.bigmodel.cn/api/anthropic \
    --ch newsta=https://<新站>/v1 --anth newsta=https://<新站> \
    --ch ikuncode=https://api.ikuncode.cc/v1 --anth ikuncode=https://api.ikuncode.cc"
python3 glmsuite.py run --run <名字> $CH --groups fp,inject,leak,params,think,know,anth,billing   # ~15 分钟
python3 glmsuite.py run --run <名字> $CH --groups iq            # 27 题 × 2 遍，~50 分钟（和上面并行跑）
python3 glmsuite.py run --run <名字> $CH --groups xcache,cache,cachehit,ctx   # 跨账号缓存 / TTL / 长上下文
python3 glmsuite.py run --run <名字> $CH --groups lat           # 智力题跑完后再跑：顺序 60 + 30 并发 × 2
python3 glmsuite.py run --run <名字> $CH --groups speed,anthq
python3 glmsuite.py run --run <名字> $CH --groups soak --soak-min 30    # 单独跑，别和别的负载叠加
python3 glmsuite.py summarize --run <名字>
python3 glmsuite.py compare --run <名字> --label newsta --ref suite/reference/zhipu-official-glm53flash.json --ref suite/reference/ikuncode-glm53flash.json
```

2026-09-27 起新增的选项（测 ooioo 时加的）：

- `--chmodel 标签=模型`：同一次运行里各通道用不同模型，比如 GLM 和 DeepSeek 一起测延迟和 soak。
- `--lat-serial a,b,c --lat-gap 2`：共用一个账号限速的通道，顺序延迟一个接一个测，并且每次调用至少间隔 2 秒。ooioo 每用户 80 次/分钟，多个渠道同时测会被站点限流，数据作废。
- `--iq-body '{"reasoning_effort":"max"}' --iq-tag effmax [--iq-rep-offset 1]`：同一题库换参数再测一遍，结果按 tag 分开统计；`--iq-rep-offset` 用来补跑中断的轮次。
- `--price-body '{}'`：计费差分用的请求参数。共用一把 key 的通道必须分开跑，而且跑的时候不能有别的请求。
- `--xcache-relays 标签,标签`：只测指定中转的跨账号缓存。
- `--ctx-ratio-for 标签=比例`：给不同分词器的通道分别设置每字符 token 数。
- 新组 `logs`：读 new-api 的逐条账单 `/api/log/token?key=`（只返回最近 1000 条，按 request_id 去重），`summarize` 会核对计费公式并统计上游渠道。
- 新组 `vision`：三色条纹图片识别，检查多模态是否透传。
- `think` 组加了"关思考"的两个变体。判断关思考是否生效，要同时看 completion_tokens 和首个正文时间，不能只看 reasoning_content 是否为空。
- DeepSeek 格式的 usage（`prompt_cache_hit_tokens`）也会计入 cached。

只想省事、不重测参考站时：先 `KEY_REF=<key> python3 glmsuite.py refcheck suite/reference/<名字>.json` 查漂移（指纹、分词增量、参数状态码、智力漂移题），SAME 就复用冻结的智力/知识/协议结论。延迟、稳定性、缓存 TTL 依赖路线和时段，不当常量复用；要比 p50/p99，就在同一台机器上、同一时段，给官方也跑一遍 `lat` 和 `soak`（官方 key 30 并发会触发 1302 账户限速，这是账户档位，单独列出）。

各组测什么、怎么判：

| 组 | 看什么 | 判读要点 |
|---|---|---|
| `xcache` | 官方 key 写入的隐式缓存，中转能不能读到；中转写入的，官方能不能读到 | **身份的决定性证据**：智谱隐式缓存跨账号全局共享，双向命中 = 同一后端。对照组用新文档，必须是 0 |
| `inject` / `leak` | "Reply with exactly: OK" 的 prompt_tokens（官方 17）、中英数字代码四段文本的分词增量、原样回显、隐藏指令问答与复述 | 分词增量逐位等于官方 = 没有额外 token；官方自己也会复述 "You are an AI assistant accessed via an API."、约七成回答"有系统指令"，只有超出官方分布的内容才算注入 |
| `params` | 关思考、effort 各档、max_tokens 999999 / 16、max_completion_tokens、temperature 5 / 1.5、stop、JSON 模式、工具调用 id | 官方：关思考 / effort none / 999999 → 400（1210）；temperature 5 → 200；只认 max_tokens；stop 在计数题上返回空正文；同步工具 id `call_-<int64>` |
| `think` / `anthq` | 默认思考深度（写代码题官方 7–20k 字符）、effort 阶梯、Anthropic 口是否一样思考 | 某个入口默认几乎不思考 = 请求被改成低 effort，难题会掉分 |
| `cache` / `cachehit` | 同一 system 文档重复发、换问题、多轮、空闲 5–420 s 后是否还命中 | 智谱缓存按整条消息做前缀；命中不降首字延迟，只降价 |
| `ctx` | 2 万 / 6 万 / 13 万 / 20 万 token 自然文本三根针（每家加独立前缀，避免吃到别家写入的全局缓存），可选极限探针 | 官方 glm-5.3-flash 接受 53 万 token 输入 |
| `lat` / `soak` | 首 token（思考或正文）、首个正文 token、总耗时的 p50/p90/p99，错误、空回复、挂起，id 族 | p99 至少要 60 个样本；soak 30 分钟每 10 秒一次 ≈ 180 个样本 |
| `speed` | 约 600 词长回答的 tok/s（含思考 token）、每个 chunk 的 token 数 | 每 chunk 远大于 1 = 中转攒包或假流式 |
| `iq` | `suite/iq.ref-20260924.json` 27 题 × 2，max_tokens 32000，默认思考，流式 | 官方有几题会想满 32k 被截断（记 L）；不认 max_tokens 的中转会多想，分数要结合截断数看 |
