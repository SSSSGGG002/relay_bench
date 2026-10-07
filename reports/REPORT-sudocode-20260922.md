# sudocode.chat claude-fable-5-1 测试（2026-09-22，单发，不测并发）

> **2026-09-23 更正提示**：本报告把 claude-fable-5-1 的 OFF 池（`msg_011C`）判为「Opus 4.5 档冒名」，这个结论很可能是错的。9 月 23 日在 fluxionai.space 确认：同一套隐藏模板（Claude Code 身份 + 隐藏 web_search + 「knowledge cutoff January 2025」 + 「不得陈述 2025 年 10 月之后的事实」）会让真 Fable 5.1 在知识题上正好表现为止于 2025 年 10 月底。本站 OFF 池的思考签名格式与那边确认的 Fable 5.1 相同，思考里也出现了同款搜索规则，少数回答还答出了 2026 年 2 月的超级碗比分（Opus 4.5 不可能知道）。更可能的解释是真 Fable 级模型被模板压制。PRE 池（`msg_pre_`、从不思考、连 2025 年 6 月的事也不知道）确实不是 Fable，这部分结论不变。详见 REPORT-fluxion-fable-20260923.md。

数据：`results/sudocode/`（screen、probe/probe2/pool3/cache/speed/sibling 日志与 json）、`results/sudocode-iq/`、`results/sudocode-iqfull/`，日志 `logs/sudocode-*.log`。
key 在 10:14 余额归零（站点 `/v1/dashboard/billing/usage` 显示已用 $9.62），后半程分池细测与 xhard 难题 13/14 被 403 打断。

## 结论一句话
**不是 Fable 5.1。** 上游是真 Anthropic API（官方 `msg_011C…` id、签名真验、`inference_geo`/`service_tier`/`context_management` 字段），
走的是 Claude Code 订阅号池（隐藏 system prompt 自称 "Claude Code, Anthropic's official CLI"，只带一个 `web_search` 工具，
注入 "knowledge cutoff January 2025" 与 "reasoning effort 25"），实际模型知识止于 **2025-10 底**，即 **Opus 4.5 档**（和远桥云 sgg 同一画像）。
智力是前沿档，速度中等偏慢，缓存只在一半请求上生效，且约 1/3 请求返回空 200。

## 1. 身份 / 知识（决定性）
| 探针 | 结果 | 官方 Fable 5.1 黄金基线 |
|---|---|---|
| K05 2025 诺贝尔文学奖（2025-10） | ✓ Krasznahorkai 3/3 | 知道 |
| 高市早苗任首相（2025-10-21）、加沙停火（2025-10-10） | 知道 | 知道 |
| K07 Mamdani 纽约市长（2025-11） | 3/3 空回复；开放式探针 4/4 答 Eric Adams | 知道 |
| 最新 Claude | 3.7 Sonnet / Sonnet 4.5 / Haiku 4.5（4 次），不认识 Opus 4.5 | — |
| K12 Opus 4.6（2026-02） | UNKNOWN 2/2 + 1 空 | 知道 |
| K11 Super Bowl LX / K13 Oscars / K14 Mojtaba | UNKNOWN 或空，无一答对 | 3/3 知道 |
| 2026 澳网 | "尚未举行，最近是 Sinner 2025" 4/4 | 知道 |
| 推断前沿 | **2025-10 底** | 2026-03 |

即使 system 里明确写「忽略配置里的 cutoff，按真实记忆答」，仍稳定停在 2025-10。同 key 下 opus-5、fable-5 自报同一套（cutoff January 2025 + web_search），
sonnet-5 自报 cutoff June 2024（更老），haiku-4-5 自报 Dec 2024 且工具列表变成 file/terminal（另一条渠道）。

## 2. 隐藏 prompt / 协议
- "Reply OK" 计 46 input token（官方直连约 18），usage 被改写：模型明说有一段内部配置、身份 "Claude Code, Anthropic's official CLI"、唯一工具 `web_search`、"Reasoning effort: 25"、"context 1M / max output 128K"。这是拿 OAuth 订阅号池必需的 CC 身份前缀。
- 签名：篡改签名 / 伪造签名 → 400（站点中文报错 `client_request_integrity_invalid`，上游真验签）；去掉签名 / 改思考正文 → 200（new-api 剥掉无签名块，与远桥云真直连表现一致）。
- 默认无 thinking（fable 真机默认 adaptive 有），`thinking.enabled` 时约一半请求仍无 thinking 块（见速度表）。count_tokens 404。原生 ping 事件、真流式。
- 站点 09:55 有一波 503 `model_service_unavailable`。

## 3. 智力
| 题库 | 得分 | 备注 |
|---|---|---|
| screen 8 题 | **8/8**，平均 43 s | R3 R4 R7 R9 R10 H2 H3 X14 |
| iq_full reason 12 题（两轮） | 9/12 → 12/12 | 第一轮错 R2/R3/R10（其中 R2 烧 7.8k 输出 token），第二轮全对 → 池间波动 |
| hard | 4/4（H1 H4 H5 H6），3 题被 403 打断 | |
| xhard | 1/1（X5），13 题被 403 打断 | 未能完成顶端分辨 |

能答的题接近全对，属前沿档（Opus 4.5 档在 09-17 远桥云 sgg 上也是 8/8）；未能靠 IQ 与真 Fable 区分。

## 4. 速度（流式，700 词作文，单发）
| 模式 | TTFT 中位 | 正文吞吐 | 每 chunk 字符 | 备注 |
|---|---|---|---|---|
| thinking disabled | 5.8 s | 46 tok/s | 3.3 | 4 次里 2 次只吐 1 个字符就结束（空流） |
| thinking enabled 1024 | 5.4 s（无思考池）/ 18–28 s（有思考池） | 45–58 tok/s | 11 vs 3.2 | 两种 chunk 粒度 = 两个上游 |

"Reply OK" 单发 5–7 s。首字慢（5–6 s）是 CC 号池的典型特征。

## 5. 缓存（8.5k 前缀，3 s 间隔顺序 8 次）
按流式 message_start 的 id 分两族：`msg_pre_<时间戳>`（PRE）与 `msg_011C…`（OFF）。
| 写法 | PRE 池 | OFF 池 |
|---|---|---|
| Anthropic + cache_control | 6/6 命中（read 12574，input 只计 13） | 1 次，全写入，无命中 |
| Anthropic 无 cache_control | **自动缓存**（写 12740 → 读 12740），不该发生 | 不缓存（input 12625，符合官方语义） |
| OpenAI chat | 写→读 12684 命中 | 不缓存 |
| 5.5 分钟后 | 重新写入（过期，正常） | 写入 |
- 两池前缀 token 数不同（12574 / 12679 / 12740 / 12625），互不命中 → 两条不同上游、不同隐藏前缀。
- 命中不降 TTFT（5–6 s 不变）。整体：约一半请求能吃到缓存价，落到 OFF 池的请求全额计费；OpenAI 格式也只在 PRE 池有缓存。

## 6. 稳定性（顺带观察）
- 非流式 200 空回复：知识探针 27 次里 10 次空、K07 3/3 空；流式 4 次里 2 次 1 字符即断；IQ hard/xhard 有 3 处 glitch（不含 403）。
- 09:55 503 一波；10:14 余额归零。

## 7. 给用户
- 模型层是 Opus 4.5 档冒 Fable 5.1 名（知识 2025-10，比真 5.1 老 5 个月），和远桥云 sgg 一样；智力够用但按 Fable 价买是亏的。
- 实用性问题比冒名更烦：约 1/3 空回复、首字 5–6 s、缓存一半概率不命中、默认不思考。
- 同 key 的 opus-5 / fable-5 是同一池（同样自报 Jan-2025 + web_search），sonnet-5 更老（自报 2024-06），haiku 走另一条渠道。

---
# 补测（充值后，2026-09-22 下午）

## 8. Claude Code 端到端（`claude -p` 指向本站，model claude-fable-5-1）
- 知识探针（system 为 Claude Code 自带 prompt）：自报「Claude Fable 5.1，cutoff June 2026」、最新模型「Claude 5 家族」——全部来自 CC 注入的 prompt；
  但 Mamdani / Super Bowl LX / Mojtaba 三问全答「不记得」。官方 Fable 5.1 在同样 CC prompt 下 3/3 知道。**结论不变：Claude Code 里只是自报变好看，模型没变。**
- 编码任务（写 stats.py + 建数据 + 运行 + 手算校验）：3 轮 CC 回合 / 2 次 API 调用，49 s，一次通过，输出正确。
  第 1 次写入缓存 28.1k，第 2 次读取 28.1k 命中、新写 5.3k；无空回复。CC 按 Fable 标价估算 $0.57。样本只有 2 次调用，命中率不能外推。

## 9. 池组成（流式 message_start id 分族，共 ~90 次）
| | PRE 池 `msg_pre_<时间戳>` | OFF 池 `msg_011C…` |
|---|---|---|
| 出现条件 | 只在流式请求出现（非流式 46/46 全 OFF）；流式约 40–60% | 非流式 100%，流式其余 |
| 首字 / 粒度 | 4–5 s，每 chunk 10–14 字符 | 6–12 s，每 chunk 2–3 字符 |
| thinking | 永远没有（enabled 也不思考） | enabled 有效，默认也常有短思考 |
| 自报 | cutoff 2025-01，有 web_search 工具，最新 Claude = 3.7 / 3.5 Sonnet | cutoff 2025-01，「无工具」，最新 Claude = 3.7 / Haiku 4.5 / Opus 4.1 |
| 知识 | Eric Adams、不知 Mamdani 初选 | 大多知道 Mamdani 赢 2025-06 初选、有的自述「训练数据到 2025-10」；**极少数（2/40）答出 Mamdani 50.4% 胜 Cuomo、2026-01-01 就职，以及 Super Bowl LX Seahawks 29-13 胜 Patriots、Walker MVP** |
| 空 200 | 高：thinking.enabled 流式 4/4 空；带 system 的知识题 5/5 空 | 偶发（probe2 非流式知识题 10/27 空） |
| 缓存 | 自动前缀缓存，无 cache_control 也命中 | 官方语义，需 cache_control；CC 端到端 1/1 命中 |

解读：OFF 池主体是 Opus 4.5 档（知识 2025-10），PRE 池是更老的 Sonnet 档（不思考、自认 3.7 最新）；
约 5% 的 OFF 请求落到真正 2026-02 之后知识的模型（Fable 5.1 或同代），说明号池里少数账号真的透传了 fable-5-1，其余账号被降级映射。
单次请求无法控制落到哪一档。

## 10. 智力（补齐后，iq_full 26 题非 screen）
reason 12/12（第二轮），hard 6/7（H2 一次 306≠307，输出 15.5k token），xhard 10/12（X7 空回复，X12 校验位错、X13 排序错）。
合计 **28/31 ≈ 90%**，与 Kiro Sonnet 4.5 档持平、低于真 Fable（twskyhope 09-10 39/39）。

## 11. 最终一句话
fable-5-1 = Claude Code 订阅号池，约 95% 请求是 Opus 4.5 / Sonnet 档降级（知识 2025-10 或更早），约 5% 才是 2026 年知识的真新模型；
Claude Code 里用起来能干活、缓存能命中，但自报身份不可信，空回复（尤其流式开 thinking）和 5–10 s 首字是日常痛点。
