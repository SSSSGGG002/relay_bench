# micuapi.ai claude-fable-5-1（"enterprise" 分组）测试报告 2026-09-22

数据目录 `results/micu-fable/`（gate*/knowledge*/hidden/signature/effort/cache*/speed*/iq_* 的 .json+.log，`cc_*.json` 为真实 Claude Code 客户端 `claude -p` 的 JSON 输出，`scripts/` 为探测脚本）。
站点要求只能在 Claude Code 里用：非 Claude Code 客户端的请求被拦（HTTP 400「客户端存在异常」，或 200 + `stop_reason: refusal` 空回复，`stop_details` 抄的是 Anthropic 官方 cyber refusal 文案）。协议/缓存/IQ 数据来自被放行的脚本请求；**身份结论以真实 `claude` 客户端（独立配置目录 `/tmp/ccmicu` 指向本站）的 9 次采样为准**。
站点计量：这把 key 的 `/v1/dashboard/billing/usage` 显示累计 $25.16（硬上限 $50），本次测试约花掉大半。

## 一句话结论
上游是**真 Anthropic API 直连**（官方 `msg_011C…` id、`service_tier`/`inference_geo`/`container`/`stop_details` 字段、`thinking.type=disabled` 返回官方 400「Use adaptive + output_config.effort」、prompt cache 语义与官方完全一致、真流式 ping），走的是 **Claude Code 订阅号池**（隐藏 system prompt = 整套 Claude Code 2.1 系统提示，含 Memory/Environment/Context management 段，用户轮带 `<reasoning_effort>25</reasoning_effort>`，usage 被改写成不含隐藏前缀）。
**模型知识止于 2026 年 1 月底–2 月初，不是 Fable 5.1 的 2026-03 画像**：9 次真实 Claude Code 采样里，Super Bowl LX / 2026 奥斯卡只有低置信度"faint memory"（6/9），Opus 4.6 仅 2/9 记得，Mojtaba 接任 0/9，最新 GPT 停在 5.1/5.2；官方 Fable 5.1（09-10 黄金基线）对这几项是 3/3 确信作答。画像与 twskyhope 的「Fable 5 顶 5.1 名」一致（见 REPORT-fable-compare-20260917.md）。智力是前沿档，缓存正常，速度中等。

## 1. 身份 / 知识
| 探针（真实 Claude Code 客户端，9 次） | 结果 | 官方 Fable 5.1 黄金基线 |
|---|---|---|
| Mamdani 任纽约市长（2026-01-01） | 9/9 高置信 | 知道 |
| GPT-5.2（2025-12） | 记得（部分只到 5.1） | 知道 |
| Opus 4.6（2026-02-05） | 2/9 记得，7/9 说最新是 Opus 4.5（2025-11） | 知道 |
| Super Bowl LX（2026-02-08） | 6/9 低置信 "Seahawks 29-13"，3/9 UNKNOWN | 3/3 确信 |
| 98 届奥斯卡最佳影片（2026-03-15） | 6/9 低置信 "One Battle After Another"，3/9 UNKNOWN | 3/3 确信 |
| Mojtaba Khamenei 接任 | 0/9（只说"有模糊印象的 2026 传闻"） | 知道 |
| 2026 澳网 | UNKNOWN / 乱猜 | 官方也答错（Djokovic），不计 |
| 自述 | "真实记忆到 2025 年底–2026 年初；Fable 5.1 / Opus 5 名字只来自本会话 system prompt" | — |

直接 API 探针（脚本，注入的隐藏 prompt 写着 "knowledge cutoff January 2026"）更保守：SB LX / 奥斯卡 / 澳网 / Eurovision 9/9 UNKNOWN，最新 Claude = Opus 4.5 6/6；明说"忽略配置的 cutoff"后 1/3 能挤出 Seahawks 29-13。
判定：训练数据在 2026-02 初变稀、2026-03 为零 → **Fable 5 档（cutoff 2026-01/02）冒 Fable 5.1 名**。同一天没能跑官方对照（本机 OAuth 过期），对照用的是 09-10 的 suite/golden 基线。

## 2. 隐藏 prompt / 协议
- 模型能复述隐藏 system prompt 的结构：以 "You are Claude Code, Anthropic's official CLI for Claude." 开头，含安全测试政策、Harness、Session-specific guidance、Memory、Environment、Context management 各段；`Assistant knowledge cutoff is January 2026`；用户轮附 `<reasoning_effort>25</reasoning_effort>`；没有任何工具定义。→ 站方用固定的 Claude Code 系统提示模板套订阅号池，模板里的 cutoff 写的是 January 2026（Claude Code 给 claude-fable-5 注入的正是这个日期，给 5.1 注入的是 June 2026）。
- usage 改写："Reply OK" 计 input 18（官方裸调约 18），隐藏前缀没计入。
- `thinking:{type:disabled}` → 400 官方原文 `"thinking.type.disabled" is not supported for this model. Use "thinking.type.adaptive" and "output_config.effort"`；第二次同样请求被站点本地拦下（"Request blocked locally because an identical request previously failed upstream"）。默认 adaptive 有 thinking（thinking_tokens 50–4400，随题难度），thinking 块带签名但正文为空（摘要被剥）。`output_config.effort` low/high ≈ 250 思考 token，max ≈ 1000。
- `thinking.enabled + budget_tokens` 被接受但行为同 adaptive。count_tokens 404。原生 ping、真流式。
- 拒绝行为：重复/无意义文本（7000 个随机希腊字母词、同一句重复 12 遍）稳定触发 200 + `stop_reason: refusal`（category cyber），且照常计费（cache_creation 17k）。这与 Bedrock/Kiro 池的"重复文本护栏"同款，对日志/CSV 类批处理是实际风险。

## 3. 智力（直接 API，adaptive thinking，max_tokens 16000）
| 题库 | 得分 | 备注 |
|---|---|---|
| screen 8 题 | **8/8** | 平均 12 s |
| iq_full 33 题（reason 12 / hard 7 / xhard 14） | **30/33** | 错：X4（答 966，应 1391）；R12 输出跑成工具调用格式烧满 16k token（格式故障）；X1 三次都 refusal（护栏） |
前沿档（twskyhope Fable 5 档 09-10 是 39/39，远桥云 Opus 4.5 档 8/8 screen）；IQ 分不开 Fable 5 与 5.1。

## 4. 缓存（自然文本 14.3k token 前缀，3 s 间隔）
| 写法 | 结果 |
|---|---|
| system + cache_control(ephemeral) | 第 1 次 write 14290，之后 3 次 + 换用户消息 2 次全部 read 14290（**5/5 命中**） |
| 无 cache_control | input 14306 全额，不缓存（官方语义） |
| ttl=1h | write 14294 → read；6 分钟后仍命中 |
| 5 分钟 TTL | 5.5 分钟后重新 write（正常过期） |
| Claude Code 端到端（3 回合） | 第 1 次 write 28.6k，后续 read 52.8k 累计，命中正常 |
命中不降延迟（4.9–9 s 波动）。缓存行为与官方完全一致。

## 5. 速度
- 短请求（"Reply OK"）3–7 s；知识问答 4–12 s。
- 流式 300 词作文：首字 3.3 s，1870 字符 / 11.8 s ≈ 38 tok/s，约 10 字符/chunk，真流式。
- 异常：同一作文 prompt 连续重发时 6/6 返回 200 + 空 SSE（21–31 s 后结束、无任何事件）；换措辞后正常。疑与站点"相同请求本地拦截"缓存有关，重复请求要小心。
- Claude Code 端到端编码任务（写 stats.py + 造数据 + 运行 + 独立校验）：3 回合 / 30 s / 一次通过、校验相符；CC 按 Fable 5.1 表价估 $0.48，单次知识问答 $0.37。

## 6. 给用户
- 通道真、协议真、缓存真、智力前沿档，Claude Code 里用是顺的。
- 但模型不是 Fable 5.1：知识止于 2026-02 初，和 twskyhope kk 分组一样是 Fable 5 档顶名；隐藏模板自己都写着 "knowledge cutoff January 2026"。按 Fable 5.1 价买亏一档。
- 站点公告说"问模型是谁/问截止日期不受理"，这份报告用的是可复现的知识探针、官方 400 原文、usage/缓存字段和真实客户端日志（`results/micu-fable/cc_*.json`），符合它自己列的"有效举证"。
- 实用坑：重复文本会被静默 refusal 且计费；相同请求重发可能得到空流；effort 被固定在 25（低）——真实 CC 会话里 thinking 只有几百 token。

---
# 修正（2026-09-22 下午，第二把 key sk-I7Eq…，数据 results/micu-fable-key2/）

## 结论改判：上游按 Fable 5.1 的规则运行，"Fable 5 顶名"不成立
| 探针（同一把 key，直接调用路径） | claude-fable-5-1 | claude-fable-5 | claude-opus-5 |
|---|---|---|---|
| `tool_choice: {type:"any"}` | **400** `tool_choice: type "tool" and "any" are not supported for this model.`（官方 5.1 原文） | 200，正常调工具 | 200，正常调工具 |
| `tool_choice: {type:"tool"}` | **400** 同上 | 200 | — |
| `tool_choice: auto` | 200 调工具 | 200 | — |
强制工具调用被拒是 Fable 5.1 / Mythos 5.1 独有的破坏性变更，Fable 5 和 Opus 5 都接受。三个名字在同一把 key 上行为按官方规则分叉，说明模型路由是真的（`toolchoice_*.json`）。

## 知识边界复测（effort=max，system 里明说"前面的 January 2026 是代理误注入"）
| 题 | 结果 |
|---|---|
| Super Bowl LX | **3/3 Seahawks 29-13、Levi's Stadium**（置信 50–70%，MVP 两次 Ernest Jones、一次 Walker） |
| 98 届奥斯卡 | 0/3，明说"在我可靠知识的边缘之外" |
| 2026 年发布的 Claude 模型 | 0/3，"训练里没有 2026 年的 Claude 模型"，最新记得 Opus 4.5 |
| Mojtaba 接任 | 0/3 |
把 effort 从 25 提到 max 后，2 月初的事实（SB LX）能召回，3 月的（奥斯卡、Mojtaba）和 2 月 5 日的 Opus 4.6 仍召不回。和 09-10 官方 5.1 黄金基线（三项 3/3 确信）仍有差距，但那份基线是 June 2026 cutoff 提示下跑的；这里模型看到的是站方前置的 "January 2026" 句子，即使被告知那句是错的，模型仍按它自我设限。**两个硬信号（协议指纹 = 5.1，知识召回 ≈ 5）的最合理解释：真 Fable 5.1，被站方前置的 Fable 5 环境模板 + 低 effort 压住了 2026 年 2–3 月的召回。** 没有同日官方对照，这一点不能钉死。

## effort 不是上限，是默认值
- `<reasoning_effort>N</reasoning_effort>` 这个标签是 **Claude Code 客户端自己生成的**：`CLAUDE_CODE_EFFORT_LEVEL=low` 时标签变成 10，默认 25。中转把它原样透传，模型也据此思考。
- 真实 Claude Code、同一道数论题、禁用工具：low 思考 2335 token / 37 s；默认 9088 token / 103 s；max 一次跑了 21 分钟没返回，被我手动终止（`cc_effort2_max.json` 空）。直接 API 里 `output_config.effort=max` 也被透传（思考 1000–1700 token vs 默认 250–500）。
- 所以"限制 effort"的说法不准确：站方前置模板带的 25 只是它自己号池客户端的默认，用户端设 `CLAUDE_CODE_EFFORT_LEVEL` 或 API 里的 `output_config.effort` 都能调高。代价是 max 档在这条通道上有超时/重试风险。

## 第二把 key 的其他观察
- 真实 Claude Code 4/4：SB LX / 奥斯卡 / Mojtaba UNKNOWN，最新模型 Opus 4.5；模型引用出 system prompt 里两句冲突的 cutoff（站方前置 "January 2026" + 客户端自带 "…Fable 5.1 … June 2026"）。
- 4 次里 2 次耗时 240 s（重试）；连续几个 400 后站点会短暂拒绝该会话（"Too many invalid requests from this session"），且相同请求失败后会被本地拦截。
- 对话中途 effort 消息（5.1 独有 beta）三个名字都被同一条格式校验挡下，无分辨力。

## 补充 3：站方前置模板的来源（真实 Claude Code 客户端 11 次采样，`cc_template_quote.json`、`cc_tplcorr_*.json`）
让模型逐句引用前后两个 Environment 块。第二块始终是本机客户端的（darwin / zsh / /tmp/…，Agent SDK 身份）；**第一块（站方的）每次都不一样**：
| 采样 | 站方块的平台 | 站方块的 cutoff 句 | 其他 |
|---|---|---|---|
| cc_k2_1–4 | — | `January 2026` | 与客户端的 June 2026 并存 |
| template_quote, tplcorr_3 | `linux` / bash | `June 2026`，模型名 Fable 5.1 | 工作目录被改写成 `/workspace/<本机目录名>` |
| tplcorr_1,2,4 | darwin | `June 2026` | |
| tplcorr_5,6 | `win32` / PowerShell / Windows 10 Pro 10.0.19045 | **没有 cutoff 句** | 附加目录 `C:\Users\user\project` |
结论：站方不是手写一段模板注入，而是把请求转发给一批**真实安装的 Claude Code 客户端**（Linux 容器、Windows 10 机器、macOS），由那些客户端各自生成系统提示再发往 Anthropic（上午 503 报错里的 "distributor" 就是这层）。"Assistant knowledge cutoff is …" 是 Claude Code 客户端按模型名查表填的字符串，不来自 API：旧版本查表给 5.1 填 January 2026 或干脆没有这一句，新版本填 June 2026。HTTP 里的 `model` 字段才决定路由，所以指纹是 5.1、模板日期却是 5 的，两者并不矛盾。

**知识召回随样本波动（6 次）**：Opus 4.6 知道 4/6；Super Bowl LX 1/6 确答（Seahawks 29-13）；奥斯卡 1/6（"One Battle After Another"）；Mojtaba 接任 1/6（低置信）。tplcorr_4 一次答齐四项，且与 09-10 官方 Fable 5.1 黄金基线逐字一致（K11/K12/K13/K14）。**3 月 2026 的事实 Fable 5 不可能知道，这一条加上 tool_choice 指纹，把"模型是 5.1"钉死**；其余 5 次的 UNKNOWN 是模型在两套互相矛盾的环境块下自我设限（它自己说"实际召回比声明的 cutoff 稀"），不是模型换了。
