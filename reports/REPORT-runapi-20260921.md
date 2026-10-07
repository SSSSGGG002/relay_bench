# runapi.host Claude 渠道测试（2026-09-21，分组 `claude_lite` ×0.194）

站点：new-api v1.0.0-rc.39。key 所在分组 `claude_lite`（站方描述「Claude特惠，稳定性稍差于ccmax」）。
数据：`results/runapi/`（screen + 账单日志）、`results/runapi-iq/`、`results/runapi-cache/`、`results/runapi-load/`，日志 `logs/runapi-*`。
累计花费约 $9（`/api/log/token?key=` 逐条账单可拉）。

## 结论
| 名称 | 实际上游 | 判定 |
|---|---|---|
| claude-fable-5-1 / fable-5（渠道 153） | 单一上游，隐藏提示词写死身份；响应 id 时钟与真 Anthropic 不同步；伪造签名照收；缓存语义非 Anthropic 原生；知识答方济各/GPT-4o/Chiefs LVIII；IQ 23–26/33 | **冒名，不是 Fable 档** |
| claude-opus-5 / sonnet-5（渠道 255） | **两个池各约一半**：A 池 = 真 Anthropic 的 Claude Code 订阅号池（注入 3.6k CC 提示词、剥签名）；B 池 = 随机 id 的适配器池，老模型、不思考、usage 伪造 | **混池，约 45–50% 请求是降级模型** |
| opus-4-8 / haiku-4-5 | 同渠道 255 | 同上（haiku 顺序探针 0/20 命中用户前缀） |

## 1. 智力（iq_full 33 题，默认思考）
fable-5-1 23/33 · fable-5 26/33 · opus-5 23/31 · sonnet-5 22/30 · opus-4-8 22/33 · haiku-4-5 15/33。
真 Fable（09-10 twskyhope）在 R2/R3/H2/H4/X3/X4/X8 全对，本站 fable 全错，且每题烧 3k–16k 输出 token。
opus-5 / sonnet-5 的分数是 A、B 两池的平均，单看 B 池：带陷阱的蜗牛爬井题 9/9 答错（秒回 "15"，输出 1 token），A 池 7/7 答对（23）。

## 2. 分池证据（opus-5 / sonnet-5，按响应 id 分族）
| | A 池 `msg_011C…` | B 池 `msg_<随机>` |
|---|---|---|
| 占比（顺序 20 次 / 100 并发×2） | 50% / 52% | 50% / 48% |
| 响应 | 带 `context_management`，注入 Claude Code 提示词 3.66k token | 无；自称 "claude-opus-5 (October 2024 version)" |
| 思考 | 有（被剥掉但计费：120 词回答计 640 输出 token） | 无（同样回答 208 token） |
| 知识 | Leo XIV、Eagles LIX、GPT-5（≈2025-10） | 「Pope Francis … as of January 2026」、Chiefs 赢 LIX（幻觉）→ 2024 年档模型 + 提示词注入的假 cutoff |
| usage | 真实（8.55k 前缀） | 伪造：read 为 11–97 的随机数，write = 总数 − read；token 数 7.3k（按字符估算，重复数字串 1400 字符只计 422） |
| 100 并发 TTFT p50 | 12.0 s | 5.1 s |

## 3. 缓存
| 模型 | 顺序 20 次（3 s 间隔，8.5k 前缀） | 100 并发 ×2 波 | 计费 |
|---|---|---|---|
| fable-5-1 / fable-5 | 18/20 命中（2 次重写） | 200/200 命中 | 命中按 0.025×（fable-5 按 0.1×）；$0.0091/次 vs 全写 $0.026 |
| opus-5 | 9/20 完整命中（A 池）；B 池 10/20 永远「全额写入」 | 104/199 命中 | 命中 $0.0047 vs B 池 $0.0061/次 |
| sonnet-5 | 9/20；B 池 11/20 全写 | 52/79（第 1 轮） | 命中 $0.0019 vs $0.0035 |
| haiku-4-5 | **0/20**（只命中注入的 CC 提示词） | 未测 | — |

- A 池每次命中仍要重写 2.1k token（注入提示词尾部每请求变化），所以命中时也有 1.25× 的固定写入成本。
- bench 的 3 连发缓存测试全 FAIL 是因为连发落在不同池/不同号；A 池内部缓存是真的（5.5 分钟后 CC 提示词部分仍命中 = 号池其他用户在续命，不是造假）。
- fable 渠道 read 数每次不同（11478–11877，剩余部分记入 input），不是 Anthropic 断点式缓存的固定值 → 上游是自动前缀缓存类后端或 usage 被改写。
- 计费公式与 `/api/log/token` 一致（851 行里偏差只出现在几十 token 的小请求取整上）。B 池因为 usage 伪造成「全写入」，每次按 1.25× 计费，永远吃不到缓存价。

## 4. 100 并发（max_tokens 1500，流式，2 波）
| 模型 | 成功 | TTFT p50 / p90 | 总耗时 p50 / max | 单流文本吞吐 | 备注 |
|---|---|---|---|---|---|
| fable-5-1 | 200/200 | 14.6 s / 19 s | 19.6 s / 50 s | 45 tok/s | 每次输出都顶到 1500 token（878 字符正文 ≈ 220 token，其余是不可见思考，全按输出价计费） |
| opus-5 | 199/200（1 次 ConnectError） | A 12.0 s · B 5.1 s | 15 s / 35 s | 41 tok/s | 两池各半 |
| sonnet-5（第 1 轮，max_tokens 400） | 100/100 HTTP 200，21 条空文本 | 11.7 s / 13.6 s | 17 s / 120 s | 31–43 tok/s | 空文本 = 思考吃光 400 token |

站点在 100 并发下没有限流/5xx，稳定性本身合格；慢的是首字（单发 2.3 s → 并发 8–15 s）。

## 5. 签名
fable 渠道：原样回传 / 改 1 字符 / 置空 / 改思考文本 / 完全伪造签名，5 种全部 HTTP 200（真 Anthropic 后 4 种应 400）。其中 2 次回复变成 "I'm Claude Code, Anthropic's official CLI…" → fable 名下偶尔也落到 Claude Code 池。
opus-5 / sonnet-5：显式 `thinking.enabled` 也拿不到 thinking 块，签名无从验证；多轮工具调用场景下思考无法回传。

## 6. 使用建议
- fable-5-1 不值得买：不是 Fable，且每次调用强制烧 600–1500 个不可见思考 token（"Reply OK" 也计 403–1500 输出 token）。
- opus-5 / sonnet-5 只有一半请求是真 Claude Code 池，另一半是不思考的老模型，单次请求无法控制落哪个池；要用的话在客户端检查响应 id 是否 `msg_01` 开头，不是就重试。
- 该站更贵的 `coding` / `claude_normal` / `Plus` 分组未测（本 key 只在 `claude_lite`）。
