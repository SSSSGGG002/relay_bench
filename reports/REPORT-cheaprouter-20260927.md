# cheaprouter.cc 测试报告（2026-09-27）

数据：`results/cheaprouter/`（`claude-fable-5-1.iq.json` 第二轮逐题，`iq-pass1-hung.json` 挂站期间的第一轮，`probes/` 探针脚本、JSON、日志）。
站点：**sub2api**（Zeabur 托管、Cloudflare 前置），钱包 key，初始余额 $8.60，只有 10 个 Claude 名字。倍率 **×1.2**（usage 里 actual_cost / cost）。
本机直连。**这把 key 已烧完（余额 $0.09）**，所以缓存没测，速度只测了 fable-5-1，其他名字只做了知识/身份探针。

## 一句话结论

**fable-5-1 是被隐藏模板压制的 Fable 级模型（和 fluxion「Max-外接」、sudocode 同款模板），智力比 ooioo/ikuncode 低一档（区分题 9/12），而且站点稳定性很差：中途整站挂了约 2.5 小时，挂着的请求照样扣了 $2.8；恢复后思考不受 max_tokens 约束，11 道题烧掉 $5。** 个人使用不推荐：贵、慢、会挂、钱扣得不明不白。

## 1. 稳定性（这次最重要的发现）

| 时间（北京 UTC+8 换算前，本机 EDT） | 事件 |
|---|---|
| 07:03 | 首批 OK 调用正常（3–15 s） |
| 07:05 起 | IQ 12 题（并发 3）只有 R3、H2 两题返回，其余 10 题连续 3 次连接失败（transport error，2–4 s 内断）；知识探针 3 条返回后全部 300 s 读超时；指纹探针一条都没返回 |
| 07:05 → 09:31 | **整站约 2.5 小时无响应**。这段时间 usage 记了 23 个请求、46,289 输出 token、扣费 $2.80，绝大多数是没有返回的请求 |
| 09:31 | 恢复：OK 调用 40 s 超时 → 32 s → 4 s |
| 09:33–09:45 | 第二轮 IQ 11 题全部返回，但单题 32–220 s |
| 09:50 | 速度测试：20 次短请求 20/20，但 p99 60 s；流式作文 3 次里 1 次连接被重置、1 次因余额 403 |

短请求（"Reply with exactly: OK"，串行）：

| n | p50 | p90 | p99 | max |
|---|---|---|---|---|
| 20 | 4.0 s | 18.1 s | 59.9 s | 68.9 s |

流式 350 词作文（仅 1 次成功）：首字节 6.3 s，**首个正文字 53 s**（前面 1,000 个思考 token 被隐藏），正文 29.5 tok/s，每 chunk 3.4 字符（真流式），output 1,499 撞 max_tokens 上限。
对比 ooioo 同模型：p50 3.3 s / p99 6.7 s、44 tok/s。

## 2. fable-5-1 真假

| 探针 | 结果 | 解读 |
|---|---|---|
| 协议形状 | `msg_011C…`、`stop_details`、`inference_geo: global`、`output_tokens_details.thinking_tokens`，思考签名信封 `08 04 12 … 0a 10 08 11 18 02`（版本字段 17，与 09-23 fluxion 验证过的真 5.1 完全相同） | 官方 Anthropic 响应，Fable 族签名 |
| 分词 | "Reply with exactly: OK" = 18 token（新分词器）；opus-5/sonnet-5 同句 13 token（老分词器） | fable 名下是新一代模型，opus-5/sonnet-5 名下不是 |
| `tool_choice: any` | 返回 200 + tool_use（官方 5.1 应 400） | 网关改写，指纹失效（同 fluxion 后期） |
| `computer_20251124` | 接受 | 排除 Opus 5.5 顶名 |
| thinking 文本 | 每个 thinking 块正文为空，只有签名和 token 数 | 网关剥掉思考内容（无法读摘要泄漏） |
| 隐藏模板 | 自称「knowledge cutoff January 2025」、「I don't cover other companies' models」、问 system prompt 答 NO 或「I'm Claude Code…won't reproduce my setup text」 | **与 fluxion Max-外接 / sudocode 同款模板**，见 [[fluxion-max-fable]] |
| 2025 年底知识 | Leo XIV、高市早苗、Krasznahorkai、Mamdani 全对（第一轮一次答石破） | 知识至少到 2025-11 |
| 2026-02/03 强制猜答（2 次） | 奥斯卡《One Battle After Another》2/2、Mojtaba 2/2、Mamdani 就职 2/2、Opus 4.6（2 月）1/2；Super Bowl LX 0/2（猜海鹰–比尔 27–24、酋长–雄狮） | 模板声称 2025-01 截止，答案却泄漏到 2026-02 → 被压制的新模型；但比分答错，**分不清 Fable 5 还是 5.1**（ooioo 3/3 答对 29–13） |

结论：**Fable 级真模型 + 隐藏模板压制**；型号在 5 和 5.1 之间不能定，签名版本 17 与真 5.1 一致。

## 3. fable-5-1 智力（`suite/iq.ref-20260924.json` 12 道区分题，max_tokens 16000，默认思考）

| 题 | 结果 | 耗时 | 输出 token |
|---|---|---|---|
| R3 | ✓ | 12.7 s | 809 |
| R10 | ✗（漏了 Z） | 69.7 s | 5,515 |
| H2 | ✓（第一轮） | 48.6 s | 2,547 |
| H4 | ✗（答 108，应 924） | 180.7 s | **15,237** |
| H6 | ✓ | 160.8 s | 11,901 |
| H7 | ✓ | 219.8 s | **15,999（撞上限）** |
| X3 | ✓ | 130.9 s | 10,906 |
| X4 | ✓ | 86.4 s | 4,097 |
| X6 | ✓ | 36.4 s | 2,866 |
| X7 | ✓ | 189.3 s | **15,999（撞上限）** |
| X12 | ✓ | 32.5 s | 2,691 |
| X13 | ✗（顺序错） | 202.0 s | 364（正文极短，思考被隐藏） |
| **合计** | **9/12** | 平均 114 s | 合计 88k token ≈ $5.3 |

对比：ooioo fable-5-1 12/12（同题平均 20 s、最多 4.8k token）；ikuncode opus-5 12/12。
同一道 X4，ooioo 用 1.4k token 答对，这里 4.1k；H7 ooioo 4.1k，这里 16k 撞顶。**思考量是 ooioo 的 3–4 倍，答对率反而低**，符合「效率被压低 + 模板占注意力」的表现（fluxion 模板里也有 effort 25）。另一种解释是它是 Fable 5 而非 5.1，两者外部无法区分。
经济后果：这站的 fable 默认思考不受 max_tokens 之外的约束，写代码类长任务单次 $0.5 起。

## 4. 其他名字（只做探针，各 5 次）

| 名字 | 号池 | 发现 |
|---|---|---|
| opus-5 | U 池（实时 id、geo global），13 token 老分词器，**从不思考** | 第一次 OK 调用空回复 13.6 s；知识：Leo XIV / 高市 / Krasznahorkai 对，但 NYC 市长答 Eric Adams 4/4、「Khamenei 仍在任」、GPT-5.1 或 o3 → 知识止 2025-10/11 且弱于 Fable；`temperature`、`thinking:disabled` 都被吞 200 |
| sonnet-5 | 同上 | 与 opus-5 同一批答案（酋长 31–27 比尔、Eric Adams、GPT-5/5.1、「Claude 3.7 Opus」）→ 两个名字大概率同一个老模型；"OK" 只记 1 个 output token |
| opus-5-5 | **M 池**：id 时间戳比当前早（`msg_011CfM…`）、`inference_geo: not_available`、签名版本 18 | 答「教皇仍是方济各」2/2，却「知道」高市 10-21 上任和 Mamdani 1 月就职 → 隐藏 prompt 里塞了日期事实；强制 `tool_choice` 返回 400「does not support forced tool_choice; use auto or none」、`thinking:disabled` 返回 400「requires adaptive thinking…output_config.effort」——**都不是官方原文，是网关伪造的 Opus 5.5 报错**，与 [[fluxion-awsq-opus55]] 同款 |
| count_tokens | 全部 404「Upstream request failed」 | 没有 count_tokens |

## 5. 计费

- 倍率 ×1.2；$8.51 扣费 = 68 请求、12k 输入、144,662 输出 token。
- **$2.80 扣在整站挂死期间**（23 个请求，绝大多数没返回）：请求超时/连接失败也照扣。
- IQ 11 题 $5.3，全是思考 token。
- 余额扣到 $0.09 后返回 403，没有预警。

## 6. 对比参考站 ikuncode（冻结值，未跑 refcheck：本会话无 ikuncode key）

| | ikuncode opus-5 | ooioo fable-5-1（09-27） | cheaprouter fable-5-1 |
|---|---|---|---|
| 实际模型 | 真 Opus 4.6/5 档 | Fable 5.1 档 | Fable 5/5.1 级，被模板压制 |
| 12 道区分题 | 12/12 | 12/12 | **9/12**（平均 114 s/题） |
| 知识 | 到 2025-11 | 到 2026-03 | 模板称 2025-01，泄漏到 2026-02 |
| 短请求 p50 / p99 | 4.65 / 23.4 s（Mac/Clash） | 3.30 / 6.70 s | 4.0 / **59.9 s** |
| 流式 | 假流式 | 真流式 44 tok/s | 真流式 29.5 tok/s，首正文 53 s |
| 稳定性 | 41 次 0 错 | 限速内 0 错 | **整站挂 2.5 h**，恢复后仍有连接重置 |
| 隐藏 prompt | Kiro 6k 计缓存读 | A 池 18.8k 缓存读 | 同 fluxion 模板（截止造假、不谈他家模型、否认 system prompt），thinking 正文剥空 |
| 单价 | — | ×1.3，读缓存 4 倍 | ×1.2，挂死也扣钱 |

## 7. 给你的结论

- fable-5-1 后面是 Fable 级真模型，但被同一套「截止 2025-01 + 不谈其他公司 + 否认 system prompt」的模板压着，思考量暴涨、答对率反降，一道难题 $0.5–0.8。
- 站点这一天挂了 2.5 小时，挂着的请求照扣，恢复后 p99 一分钟。
- opus-5 / sonnet-5 是同一个不思考的老模型（NYC 市长还是 Eric Adams），opus-5-5 是网关伪造报错的另一个池。
- 不推荐充值。你要用 Fable，ooioo 这次的数据（12/12、p99 6.7 s）明显更好。
