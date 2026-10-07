# buliangrenai.com：claude-sonnet-5 / claude-opus-5（2026-09-25，20:10–21:35 北京时间）

数据：`results/bl-cc/`（Mac 走 Clash 美国出口跑的 bench full）、`results/bl-cc-screen/`（opus-4-8 screen）、`results/bl-probes/`（探针，`server/` 子目录是北京阿里云服务器直连跑的，延迟/稳定性数字以它为准）。日志：`logs/bl-cc-*.log`。脚本：`results/bl-probes/scripts/`（key 从环境变量 `BL_KEY` 读）。
站点：new-api，Cloudflare。key 名 `cc`，不限额；分组 **`claude-0.25`**（从报错文本里看到）。

## 一句话结论
- **这把 key 调不了 claude-opus-5**：`/v1/models` 里没有它，调用返回 503 `分组 claude-0.25 下模型 claude-opus-5 无可用渠道`，两条出口都一样。能用的 Opus 名字只有 opus-4-6 / 4-7 / 4-8，下面用 **claude-opus-4-8 代替**测。
- **后端是几个号池混用，而且在测试过程中换了池**：
  - 20:55 以前：sonnet-5 约 90–100% 落在 **A 池**（`msg_011C` 模板池）。这是新一代会思考的模型，外面套了 Claude Code 模板。
  - 21:00 以后：A 池没了。sonnet-5 **100% 落到 Kiro 池**，模型是 **Claude 3.7 Sonnet**（2024 年的老模型），并有一段时间约 30–40% 请求 503 `No available accounts`。
  - 同一时间，opus-4-8 落在 **B 池**：默认不思考，27 题 14 对（52%），开 effort=max 也只到约 59%。
- **所以现在买到的 "sonnet-5" 实际是 3.7 Sonnet，"opus" 是一个推理约 60% 的老档模型**。只有 A 池在线的那段时间，sonnet-5 才接近真货的水平（带思考的题 11/13）。你拿到哪个池，自己控制不了。

| 名字 | 测试时落到的池 | 实际表现 | 智力（27 题） | 顺序首字 p50 / p99 | 30 并发 p50 / p99 |
|---|---|---|---|---|---|
| sonnet-5（20:55 前） | A 池 ~95% | 新一代思考模型；有隐藏 Claude Code 提示和隐藏 web_search 工具；知识到 2025-10 | bench 18/25；其中确定在 A 池、有思考的题 11/13（另 2 题 16k 思考没答完） | **2.73 / 5.10 s** | 4.18 / 7.71 s（60/60） |
| sonnet-5（21:00 后） | Kiro 池 100% | **Claude 3.7 Sonnet**：自报 3.7、教宗方济各、日相岸田、不知道任何 2025 年的事；思考参数被丢弃 | **10/23**（43%） | 3.75 / 8.56 s（30 分钟 soak，5.4% 失败） | — |
| opus-4-8（代 opus-5） | B 池 ~100% | 不思考；知识到 2025-10（Leo XIV、高市早苗） | 默认 **14/27**；effort=max 复测 11 道错题只救回 2 道，5 道思考 16k 仍没答完 | **2.36 / 3.82 s** | 3.17 / 5.48 s（60/60） |

## 1. 可用模型与分组
- `/v1/models`：claude-fable-5、haiku-4-5、opus-4-6、opus-4-7、opus-4-8、sonnet-4-6、sonnet-5。站点定价页显示还有 claude-0.07 / 0.09 / 0.25 / claude-kiro-0.10 等分组，本 key 在 claude-0.25。
- claude-opus-5 → 503 model_not_found（无渠道），不是临时故障，定价页里也没有这个模型。

## 2. 后端池（每条响应都按 id 格式和 usage 字段打标签）
| 池 | 响应 id | usage 形状 | 背后 | 同类站 |
|---|---|---|---|---|
| **A「011C 模板池」** | 流式和非流式都是 `msg_011C…` | 官方字段齐全：`service_tier`、`inference_geo`、`output_tokens_details.thinking_tokens`；数值是网关估算（"Reply with exactly: OK" 报 7） | 新一代思考模型 + Claude Code 模板 | 与 hyhawang P1、fluxion「AWSB逆」主池同款 |
| **B「msg_01 随机」** | 流式 `msg_01`+22 位随机，非流式 `msg_011C…` | 只有 input/output/cache 字段，没有 `service_tier` | 不思考的模型，同样有 Claude Code 模板 | 与 hyhawang 的 opus-5（~60%）同档 |
| **K「Kiro」** | `msg_`+32 位 hex | `kiro_actual/billable/excluded_input_tokens`、`kiro_credits` | Kiro/AWS 号池，**Claude 3.7 Sonnet** | 与 hyhawang P2 相同（隐藏 prompt 5255/5247 逐位一致） |
| 其它 | `msg_`+24 位随机 | 小请求就报 cache_creation 178 | 只见过 1 次 | — |

**时间线（北京时间，按池计数）**
- 20:15 首次探测：7 个名字全部 A 池（`msg_011C` + service_tier）。
- 20:45 抽样：sonnet-5 美国出口 20/20 A 池；北京直连 18/20 A 池、2/20 Kiro 池。
- 20:46 北京延迟测试：顺序 59/60 A 池；30 并发时 7/60 溢出到 Kiro 池、1/60 落到 B 池 → **负载高时往老模型溢出**。
- 20:50 缓存探针：A 池正常，20:52 起开始出现 520 / 502 / 600 秒挂起。
- 21:00 起：sonnet-5 100% Kiro 池，另有 30–40% 返回 503 `No available accounts: no available accounts`（两条出口都这样；是否带 thinking / effort、请求长短都不影响分流）。
- 21:08–21:31 每 3 分钟抽样（9 轮）：sonnet-5 每轮 6/6 Kiro（30 分钟 soak 129 次里只有 1 次回到 A 池），opus-4-8 基本全在 B 池（偶尔 1–3 次 Kiro），opus-4-7 全 Kiro，opus-4-6 全 B 池，fable-5 全 Kiro。

## 3. 注入（隐藏提示词 / 隐藏工具 / 参数改写）
**A 池（sonnet-5 前半段）**
- 隐藏 Claude Code 系统提示：问"有没有系统提示"，答 "I'm Claude Code, Anthropic's official CLI for Claude. I won't reproduce my setup text"；即使我们自己传了 system 也照样说。自报截止 2025-01、"没有可靠途径知道确切型号"。
- **隐藏 `web_search` 工具**：问"你有哪些工具"答 `web_search`；问最近一届世界杯，直接返回 `stop_reason=tool_use` 调用 web_search（我们从没传过工具）。**客户端会收到一个它不认识的工具调用**，Agent 类客户端要注意。
- 注入不计费：usage 只报我们自己那部分（"OK" 7 token），隐藏提示大小从 usage 看不出来；参照同款 fluxion 模板池约 5.6k token。
- thinking：显式 adaptive + effort high 会返回 thinking 块，但**签名为空字符串**，也没有思考正文；`thinking.enabled + budget_tokens`、`display: summarized` 都被接受但不产生思考。
- 参数：temperature / top_k / budget_tokens / prefill / system 放 messages 里，官方应 400，这里都 200（官方行为吻合度 3/8）；stop_sequences、max_tokens 生效；`max_tokens=999999` 200；count_tokens 404。

**Kiro 池（sonnet-5 后半段、opus-4-7、fable-5）**
- 模型自己说："I received a system prompt that defines my identity as **Kiro** … approximately 3000 words"。usage 里 `kiro_excluded_input_tokens` 5247–6321（即隐藏 prompt 5.2–6.3k token），标记为不计费。
- thinking 参数（enabled+budget、adaptive+max）**全部被静默丢弃**，从不思考。

**B 池（opus-4-8 / 4-6）**
- 同样自称 Claude Code、截止 2025-01；默认不思考；effort=max 时会输出可见的长思考（2–3.6 万字符），经常 16k 用完还没给答案。

## 4. 智力（suite/iq.json 27 题，max_tokens 16000，单次作答）
| | reason | hard | xhard | 合计 | 备注 |
|---|---|---|---|---|---|
| sonnet-5 · bench（20:30–20:50，A 池为主） | 5/6 | 4/6 | 9/13 | **18/25**（2 题 16k 思考没答完） | 有思考的 13 题 11 对（确定是 A 池）；不思考的 12 题 7 对（可能混了 Kiro） |
| sonnet-5 · Kiro 池（21:05–21:20 逐题打标签） | 4/6 | 2/6 | 4/11 | **10/23**（43%） | 从不思考，每题 0.3–1.5k token 直接作答 |
| sonnet-5 · 同轮落到 A 池的 4 题 | — | H5 ✓ | X9 ✓ X11 ✓ X8 ✗（16k 没答完） | 3/4 | 思考 0.6k–16k token |
| opus-4-8 · B 池 默认 | 4/6 | 3/7 | 7/14 | **14/27**（52%） | 一题都不思考 |
| opus-4-8 · B 池 effort=max 复测 11 道错题 | | | | 救回 2 道（R10、H6） | 5 道思考 16k 仍没答完 |
对照：relay-bench 历史上真 Opus 5 / Sonnet 5 ≈ 95%，ikuncode Kiro 池 Sonnet 4.5 23/27，hyhawang（同款 A/B 池）16/26。
- 一个直观的例子：R10（JS 事件循环顺序）不思考时，A 池 opus-4-8、B 池 opus-4-8、Kiro 池 sonnet-5 给出**同一个错误答案** `["H","Z","J","K","A",…]`；A 池 sonnet-5 加 effort=max 后思考 3.7k token 就答对了。A 池默认经常不思考直接答（bench 里 12/25 题没有思考块），**用 A 池时显式传 `thinking:{type:"adaptive"}` + `output_config.effort:"high"/"max"` 能明显变强**。Kiro 池传了也没用。
- 20:50 时 A 池上 sonnet-5 和 opus-4-8 在 temperature 0 下对 3 个短提示给出逐字相同的回答 → A 池里两个名字大概率是同一个模型。

## 5. 缓存（北京服务器，自然文本前缀约 25k token，system + cache_control，间隔 3 s）
| | A 池（20:50） | Kiro 池（21:02 后） | B 池（opus-4-8） |
|---|---|---|---|
| 行为 | 第 1 次写 25446 → 之后读 25446；7 次里有 1 次重新写（换账号），命中时 input 只剩 11 | 放在 **system 里的 25k 前缀只计 billable 8**（input 2 + cache_read 6）；**放在 user 消息里的内容按 cache_creation 全额计**（20k needle 报 write 30654） | 不带 cache_control 也自动按 cache_creation 计（20k needle write 35509、60k write 84668） |
| 单次命中率 | read ÷ 总输入 ≈ **99.96%** | 无意义（数字是 Kiro 的计费拆分） | 未测多次命中 |
| 命中是否降首字 | 否（2.7–5.0 s，无规律） | — | — |
- A 池的缓存语义像真的（先写后读、换账号会失效），与 fluxion 同款池一致；bench 用合成文本测时 write/read 全 0，自然文本才有缓存。
- **Kiro 池的计费怪现象**：同样的大段文本放 system 几乎不收钱、放 user 按 1.25 倍写入价收。
- 大前缀测试（~19 万 token 放 system）：3 次 500 `Upstream access forbidden, please contact administrator`、1 次挂 62 s 后空回复。

## 6. 速度 / 稳定性（北京阿里云直连；Mac 本地 Clash 链路当时对所有 Cloudflare 站点都有 20–40% TLS EOF，不计入站点）
**短问答流式首字（17×23，CC 系统提示，秒）**
| | 顺序 60 次 p50 / p90 / p95 / p99 / max | 30 并发 ×2 波 p50 / p95 / p99 / max | 成功 |
|---|---|---|---|
| sonnet-5（A 池时段 20:46） | 2.73 / 4.03 / 4.25 / **5.10** / 6.05 | 4.18 / 6.94 / **7.71** / 9.43；总耗时 p99 12–23 s | 120/120 |
| opus-4-8（B 池 21:17） | 2.36 / 2.87 / 3.02 / **3.82** / 6.09 | 3.17 / 5.32 / **5.48** / 13.9 | 120/120 |
| sonnet-5 soak 30 分钟（Kiro 时段 21:02–21:32，每 10 s 一次，129 次） | 3.75 / 5.56 / 5.85 / **8.56** / 10.2 | — | 122/129（5.4% 失败：503×4、流挂起 90 s+ ×2、500×1） |

**吞吐**：A 池 sonnet-5（Mac bench）首字 2.56 s、35.7 tok/s，2500 token 长输出完整；Kiro 池 sonnet-5 62–66 tok/s、B 池 opus-4-8 58–72 tok/s，都是真流式（每块 3–4 token）。

**故障类型**（这站主要的问题在这里，不在平均延迟）：
- **503 `No available accounts`**：21:00–21:05 路由探针两条出口各 40 次里 13–15 次；soak 开头 3 分钟 4 次。号池没账号了。
- **流挂起**：连接建立、只发 `: PING` 保活、不出内容。Mac bench soak 有 1 次挂满 **600 s** 后返回空 200；缓存探针 1 次 600.8 s 空 200；北京 30 分钟 soak 2 次首字出来后流卡住、90 s 仍不结束（被我们强制断开）；另有 1 次最后一个 token 后流 30 s 才关。没有总超时的客户端会被一直卡住。
- **Cloudflare 502 / 520 / 524**：跨模型对比那轮（7 个名字 × 7 题）49 次里 11 次，fable-5 最多，524 在 126–130 s。
- **500 `Upstream access forbidden`**：130k / 200k 自然文本 needle 各 2/2，大前缀缓存 3/3。
- 并发 30 时没有 429，看不到 RPM 限速。

## 7. 长上下文（自然文本 needle，3 个埋点）
| | 20k | 60k | 130k | 200k |
|---|---|---|---|---|
| sonnet-5（Kiro 池） | 3/3，5.5 s | 3/3，6.4 s | 500 Upstream access forbidden ×2 | 同左 |
| opus-4-8（B 池） | 3/3，6.2 s | 3/3，7.3 s | 未测 | 未测 |
| sonnet-5 bench 合成文本（A 池时段） | 20k–230k 全部 200 空回复（合成文本触发护栏，不作能力结论） | | | |
**实际可用上下文约 60k–120k**，再大就 500。

## 8. 给用户的建议
- 要 opus-5：这把 key 没有，得换分组/换站。
- 如果站方保证长期在 A 池，sonnet-5 可以用，但必须显式开 effort high/max，并在客户端过滤隐藏的 `web_search` 工具调用。**以 21:00 之后的状态**，sonnet-5 是 3.7 Sonnet 冒名，opus-4-8 是 60% 档老模型，不值 Sonnet 5 / Opus 5 的价。
- 稳定性上：一定要设总超时（比如 120 s）并重试 503，否则会被 600 秒挂起的流卡住。
- 想省钱可以把大段背景放 system（Kiro 池几乎不计费），但 Kiro 池本身是 3.7 Sonnet。

## 9. 花费与遗留
- 本轮请求以短请求和收到 message_start 就断开的抽样为主，花费大头是两轮 27 题智力测试和几次 20k–60k needle；站点后台没有逐条账单接口（`/api/usage/token/` 只显示 unlimited）。
- 没做到的：A 池消失后，sonnet-5 在 A 池的完整 27 题定向智力测试没能补完（只有 bench 那轮和 4 道定向题）。A 池上的长上下文也没测到自然文本版本。

## 10. 对比参考站 ikuncode（Kiro 分组，已冻结为 `suite/reference/ikuncode-kiro.json`）
ikuncode 的 IQ / 知识 / 上下文沿用 09-24 全量结果；09-25 21:45 用 `refcheck.py` 复核未漂移：号池指纹逐位一致，12 道区分题 opus-5 11/12、sonnet-5 9/12，冻结值为 12/12 和 11/12，都在容差内。延迟两站都在 09-25 从北京服务器同路线实测。

| | ikuncode opus-5 | buliangren opus-4-8（无 opus-5） | ikuncode sonnet-5 | buliangren sonnet-5（21:00 后） |
|---|---|---|---|---|
| 实际模型 | 真 Opus 4.6/5 档 | 不思考的老档模型（B 池） | Sonnet 4.5 冒名 | **Claude 3.7 Sonnet**（Kiro 池） |
| 智力（27 题） | **25/26** | 14/27 | **23/27** | 10/23 |
| 12 道区分题 | 12/12（今天 11/12） | **0/12** | 11/12（今天 9/12） | **0/12** |
| 知识 | Leo XIV / 高市 | Leo XIV / 高市 | 不稳定（方济各或 Leo） | 方济各 / 岸田，无 2025 年知识 |
| 顺序首字 p50 / p99（北京） | 2.87 / 5.65 s | 2.36 / 3.82 s | 2.93 / 10.09 s | soak 3.75 / 8.56 s |
| 30 并发 ×2 p50 / p99 | 3.36 / 6.46 s（60/60） | 3.17 / 5.48 s（60/60） | 3.43 / 5.18 s（60/60） | —（A 池时段 4.18 / 7.71 s，60/60） |
| 流式 | 假流式（先憋 15 s 再一次吐完） | 真流式 58–72 tok/s | 假流式 | 真流式 62–66 tok/s |
| 30 分钟 soak（北京，每 10 s） | — | — | 158/159（0.6%，1 次断连），首字 p50 3.82 / p99 **26.06** s，无挂起 | 122/129（5.4%：503、挂起、500），首字 p50 3.75 / p99 8.56 s |
| 故障 | 偶发空回复被换成中文警告正文 | 503 无账号、600 s 流挂起、CF 5xx | 同左；长尾偶尔 20–30 s | 同左 |
| 上下文（自然文本） | 130k 3/3 | 60k 3/3（更大未测） | 130k 3/3 | 60k 3/3，130k 起 500 |
| 缓存 | 固定拆分，≈92% 恒报命中（假） | 自动按写入计 | 同左 | 无意义（system 几乎不计费） |
| 注入 | Kiro prompt 6.1–6.5k 计作 cache_read | Claude Code 模板 | 同左 | Kiro prompt 5.2–6.3k 标不计费 |

**结论**：智力上 ikuncode 完胜，在 12 道区分题上 buliangren 两个名字都是 0 分。buliangren 只在短请求延迟、长尾和真流式上略好：soak p99 8.6 s，ikuncode 是 26 s。但 buliangren 的失败率高约 9 倍（5.4% 对 0.6%），还有号池断供（503）、流挂起和中途换池。按 09-25 的状态，ikuncode 两个名字都明显更值。
