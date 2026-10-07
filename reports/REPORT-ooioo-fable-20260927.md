# ooioo.work claude-fable-5-1 测试报告（2026-09-27）

数据：`results/ooioo/`（`iq-merged.json` 逐题；`probes/` 全部探针脚本、原始 JSON 和日志；`logs/ooioo-iq*-0927.log` 五轮 IQ 日志）。
站点：new-api（前端 v1.0.0-rc.23），这把 key 在 **cc-max** 分组（站方描述「Claude Max / Enterprise 号池，后续可能会涨」，倍率 ×1.3）。
fable-5-1 定价 = 官价（输入 $10/M、输出 $50/M、写缓存 ×1.25）× 1.3；**读缓存按输入价的 10%（$1/M）计，是官方 $0.25/M 的 4 倍**。
key 限速 **30 请求/分钟，被拒的 429 也计数**，所以一旦超速会连锁 429 约一分钟。本机直连（不走 Clash）。
本次总花费 **$7.72**（站内 usage 统计）；其中 10:02 余额扣到 −$0.06，30 次速度测试作废，你充值后（约 10:20）补测完成。

## 一句话结论

**是真 Fable 5.1 档的模型，智力和知识都对得上官方基线，但 key 后面是两个池随机分配，其中一个池会丢掉你的 system prompt 和工具。**
- 智力：27 题参考题库 **27/27 全对**（默认思考），和 ikuncode opus-5 的 25/26 同档或更好；12 道区分题 12/12。
- 知识：2026 年 2–3 月的三件事（Super Bowl LX 海鹰 29–13、第 98 届奥斯卡《One Battle After Another》、Mojtaba 接任）**3/3 答对**，这是官方 Fable 5.1 基线（知识到 2026-03）独有的，Fable 5（到 2026-01）和 Opus 4.5/4.6 冒名池全部答不出。
- 速度：短请求 p50 3.3 s / p99 6.7 s；流式首字节 1.6–6 s，正文 42–54 tok/s，真流式。
- 缓存：B 池是真 Anthropic 缓存（36k 前缀写 2 次后读 2 次），A 池不缓存你的内容（因为根本没把它发给模型）。

## 1. 两个池（按响应头和 usage 形状可稳定区分）

| | A 池「Claude Code 桥接」（约 40%） | B 池「普通」（约 60%） |
|---|---|---|
| 响应头 | `server: nginx`、`x-request-id`、new-api rc.23 | `server: GoFrame HTTP Server`、再套一层 new-api rc.19 |
| usage | 多一个 `iterations` 数组；**每次都读 18,826–18,917 token 的 1h 缓存**（Claude Code 完整 system prompt + 工具定义）；"OK" 的 input_tokens = 4 | 普通形状；"OK" 的 input_tokens = 42（隐藏前缀约 24 token） |
| 隐藏 prompt | 完整 Claude Code 模板：工作目录 `/Users/user/project`、Darwin 25.0.0、「powered by Fable 5.1」、「knowledge cutoff June 2026」 | 只有一句 `You are Claude Code, Anthropic's official CLI for Claude.`，没有工具 |
| **你的 system prompt** | **被丢弃**：codeword 探针答 NONE（1/1）；12k 文档放 system 里问主题，答「你说的文本没有包含在内」，usage 里 input 只有 4 | 正常：codeword 2/2 答对，文档主题答对 |
| **你的 tools** | **被丢弃**：`tool_choice: any` 直接回文本「5」，没有 tool_use 块 | 正常：`computer_20251124` 工具被接受并描述 |
| 副作用 | 模型偶尔按 Claude Code 习惯去调 Bash 等工具，返回 `stop_reason: tool_use`，正文为空（IQ 里 H6/X4/X7 各出现一次）；R10/X14 各遇到 1 次 `stop_reason: refusal` 空回复 | 未见 |
| 计费底噪 | 18.8k 读缓存 × $1/M × 1.3 ≈ **每次请求固定 $0.024**，哪怕只回一个 OK | 几乎为零 |

对你的实际影响：用 Claude Code 客户端接这个站，两个池都能用（Claude Code 自己的 system prompt 在 A 池会被站方的那份替代，工具照常）；**用 API 自带 system prompt 或 tools 的场景，约 40% 的请求会静默丢掉它们**，回答看起来正常但没按你的指令走。

## 2. 真假：型号证据

| 探针 | 结果 | 说明 |
|---|---|---|
| 2026-02/03 知识（各 3 次，两池都覆盖） | Super Bowl LX 海鹰 29–13 ✓✓✓；奥斯卡最佳影片 ✓✓✓；Mojtaba Khamenei ✓✓✓ | 与 `suite/golden/claude-fable-5-1.json`（官方订阅基线）一致；twskyhope 的 Fable 5 冒名 21/21 UNKNOWN，Opus 4.5 池连 Mamdani 都不知道 |
| 2025 年底知识 | Leo XIV、高市早苗、Krasznahorkai、Mamdani、GPT-5.2（12 月）、TIME「The Architects of AI」全对 | 同官方基线 |
| 2026 年 4 月以后 | Eurovision/NBA/世界杯 2026 全部「不知道」，猜瑞典 | 官方基线也是 UNKNOWN/猜瑞典，没有隐藏联网搜索的迹象（回复都是单段 text） |
| 2026 澳网 | 答 Sinner（guess） | 官方基线答 Djokovic，两者都不确定，不作证据 |
| 协议字段 | `msg_011C…`、`stop_details`、`inference_geo`、`service_tier`、`output_tokens_details.thinking_tokens`、`context_management` | 官方 Anthropic 响应形状 |
| 思考签名 | `08 04 12 … 42 08 "thinking"` 信封，与 09-23 验证过的真 Fable 5.1 同格式，内层版本字段 18（09-23 是 17） | 同族格式；版本号变化可能是模型侧更新，不作反证 |
| 默认思考 | 智力题每题都有 thinking 块（400–4,800 token）；350 词作文 7/7 不思考 | adaptive 行为 |
| `computer_20251124` | B 池接受 | Opus 5.5 会 400，排除「Opus 5.5 顶名」 |
| `tool_choice any` 400 指纹 | 不可测：落在 A 池被剥掉工具；`temperature`、`thinking:disabled` 都 200 | 网关静默剥参数，官方式 400 指纹在这里失效 |

综合：知识前沿 2026-03 + 智力满分 + 官方协议形状 = **Fable 5.1 档**（无法在外部区分 5.1 和「同知识的更新版本」，但排除 Fable 5、Opus 4.x/5/5.5 冒名）。

## 3. 智力（`suite/iq.ref-20260924.json` 27 题，max_tokens 16000，默认思考，流式）

| 档 | 得分 | 逐题 |
|---|---|---|
| reason（6） | 6/6 | R2 R3 R4 R7 R9 R10 |
| hard（7） | 7/7 | H1–H7 |
| xhard（14） | 14/14 | X1–X14 |
| **合计** | **27/27** | 3 题（H6 X4 X7）首次因 A 池 tool_use 空回复、2 题（R10 X14）首次 refusal 空回复，补跑后全对 |
| 12 道区分题 | 12/12 | ikuncode opus-5 冻结值 12/12 |

耗时：reason 5.6–15.9 s，hard 3.4–54.8 s，xhard 7.3–54.8 s（最长的 H7/X7/X8 思考 4k+ token）。
一个反例：我在 B 池单独重问 X4 一次答 4293（正确 1391），即 X4 为 2 次里对 1 次；其余题没有复测。
故障率：5 轮共 30 次有效题目调用里 5 次（17%）空回复（3 次 tool_use、2 次 refusal），都能重试成功。此外限速造成的 429 不计。

## 4. 速度与稳定性（本机直连，串行或 2 并发，避开限速）

| 场景 | n | p50 | p90 | p99 | max |
|---|---|---|---|---|---|
| 短请求非流式（"Reply with exactly: OK"） | 41 | **3.30 s** | 4.79 s | **6.70 s** | 7.58 s |
| ↳ A 池 | 17 | 3.31 s | | | 7.58 s |
| ↳ B 池 | 24 | 2.92 s | | | 5.23 s |
| 350 词作文流式：首字节 | 7 | 3.15 s | | | 6.09 s |
| 350 词作文流式：首个正文字 | 7 | 3.8 s | | | 26.7 s（1 次） |
| 350 词作文流式：总耗时 | 7 | 16.7 s | | | 36.3 s |
| 正文速度 | 7 | **43.9 tok/s** | | | 42–54 |

真流式，每 chunk 约 12 字符。限速内 0 网络错误、0 5xx；超速时 429 连锁。
未做 30 并发 / 30 分钟 soak：30 req/min 的 key 限速本身就不允许这类负载，个人用也用不到。

## 5. 缓存（system 放 46k 字符自然文本，站方计 35,979 token，带 cache_control，间隔 5–6 s）

| 调用 | 池 | 结果 |
|---|---|---|
| 第 1、2 次 | B | 写 35,979 ×2（连续两次写 → B 池里至少两个账号轮换，或写入异步） |
| 第 3、4 次 | B | **读 35,979 ×2**，真命中 |
| 不带 cache_control | B | input 36,005，不缓存（官方语义） |
| 任意一次 | A | input 4、读 18.8k、写 ≈90：你的 system 根本没进模型，也谈不上缓存 |

计价：读缓存 $1/M × 1.3，比官方 $0.25/M 贵 4 倍；但 B 池 36k 命中后单次只要 $0.047，仍比不缓存（$0.47）省 10 倍。
分词：这段中文为主的文本 o200k 计 25.5k，站方计 36.0k（1.41×），在 Claude 分词器对中文的正常范围内，不算虚高。

## 6. 计费与限制

- 本次 $7.72：IQ 五轮约 $4.5（xhard 思考多）、探针和缓存约 $2.0、速度约 $1.2。A 池每请求固定 $0.024 的隐藏 prompt 缓存读是「个人轻用」的主要底噪：每天 200 次对话 ≈ $4.8/月只为它买单。
- 限速 30 req/min（含被拒请求），Claude Code 并行子 agent 或批量脚本很容易撞上。
- 余额到负数后返回 403「用户额度不足」，没有预警。

## 7. 对比参考站 ikuncode（Kiro 分组，`suite/reference/ikuncode-kiro.json` 冻结值）

**本次没有跑 `refcheck.py`**：这个会话里没有 ikuncode 的 key（规则要求先查漂移再复用冻结值）。下表 ikuncode 一列是 09-24/25 冻结值，延迟不是同日同路线，只作量级参考。

| | ikuncode opus-5 | ooioo fable-5-1 |
|---|---|---|
| 实际模型 | 真 Opus 4.6/5 档（知识到 2025-11） | **Fable 5.1 档**（知识到 2026-03） |
| 智力（27 题） | 25/26 | **27/27** |
| 12 道区分题 | 12/12 | 12/12 |
| 知识 | Leo XIV / 高市；2026 年事实不知道 | Leo XIV / 高市 / Mamdani / **Super Bowl LX / 奥斯卡 98 / Mojtaba** |
| 短请求 p50 / p99 | 4.65 / 23.4 s（09-24 Mac/Clash） | 3.30 / 6.70 s（09-27 Mac 直连） |
| 流式 | 假流式（憋 15–18 s 一次吐完） | 真流式 44 tok/s |
| 号池 | 单一 Kiro 池，隐藏 prompt 6.1–6.5k 计作 cache_read | 两池混：A 池隐藏 18.8k 计作 cache_read 并**丢 system/tools**，B 池干净 |
| 缓存 | 固定拆分假命中 | B 池真命中，读价 4 倍官方 |
| 空回复 | 偶发，被换成中文警告 | 17%（tool_use / refusal），重试可解 |
| 单价（输入/输出） | opus-5 ×? | $13 / $65 per M（×1.3） |

结论：智力和知识 ooioo 明显更强（这是 Fable 5.1 对 Opus 5 的代差，不是站点功劳）；延迟和流式体验也更好。短板是 A 池丢 system prompt/工具、17% 空回复要重试、30/min 限速，以及贵 5 倍的单价。

## 8. 给你的建议

- 个人用 Claude Code：可以用，智力是 Fable 5.1 档。注意每次请求 $0.024 底噪和 30/min 限速。
- 用 API 自己写 system prompt / tools：不推荐直接用，约 40% 请求会落到 A 池被静默丢弃。可以按响应头 `server: GoFrame` 或 usage 里没有 `iterations` 判断是否命中 B 池，不是就重发。
- 空回复（`stop_reason` 为 `tool_use` 或 `refusal` 且无正文）当成失败重试即可。
