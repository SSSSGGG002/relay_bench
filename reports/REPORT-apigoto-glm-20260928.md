# apigoto.com：glm-5.3-flash 测试报告（2026-09-28，北京时间 21:53–23:54）

- **站点**：`https://www.apigoto.com`，网关 APISIX 3.10.0，144 个模型。
- **key**：`sk-routercode-…`，免费套餐「RouterCode Free / APIGOTO FREE」。每 7 天 2500 万额度（约 $3.72），**并发上限 2**。
- **路线**：北京阿里云直连，智谱官方和 ikuncode 在同一时段对照。开测前 refcheck 两份冻结基线都是 SAME，漂移题各 10/10。
- **数据**：
  - 结果：`results/glmsuite/ag0928`（探测、智力、缓存、长上下文、跨账号缓存）、`ag0928-lat`（顺序延迟、soak、吞吐）、`ag0928-price*`（额度差分）；
  - 日志：`logs/glmsuite-ag0928/`。
- **收尾**：key 测完已从服务器删除。本次用掉约 568 万额度（本周额度的 23%，约 $0.85）。

## 一句话结论

**apigoto 的 `glm-5.3-flash` 大部分不是 GLM**，是按请求在几个上游之间分配的混合池：

| 上游 | 30 分钟 soak 占比（179 次成功） | 特征 |
|---|---|---|
| **MiniMax-M3**（MiniMax 官方接口） | **133 次 = 74%** | 回显 `MiniMax-M3`；带 `base_resp`、`input_sensitive` 字段和 `x-mm-request-id` 头；自带 MiniMax 系统提示（"Your model version is MiniMax-M3, developed by MiniMax. Knowledge cutoff: January 2026…"）；问身份直接答 MiniMax-M3 |
| GLM-5.3-Flash @ 火山方舟 | 25 次 = 14% | 回显 `glm-5-3-flash-260828` |
| GLM-5.3-Flash（`zai-org/…`，id 是智谱格式） | 11 次 = 6% | 同步工具调用 id 是官方的 `call_-<int64>` 格式，疑似转发智谱官方 |
| GLM-5.3-Flash（`zai-org/…`，id 以 `rxq-` 开头） | 10 次 = 6% | 同上，另一家托管 |

- **长文档几乎只给 MiniMax**：约 1 万 token 的新文档首发 38/38 都落到 MiniMax；短请求才有约四分之一轮到 GLM。所以越重的任务越可能拿到 MiniMax。同站 `glm-5` 也回显 MiniMax-M3，`glm-5.3` 则是真 GLM（`zai-org/GLM-5.3`）。
- **智力**：27 题里 26 题由 MiniMax 作答，第一遍 17/27，另有 7 题想满 32k 没答完；作答正确率 85%。GLM 官方 96%，ikuncode 96%。
- **速度很快，但那是 MiniMax 的速度**：顺序首 token p50 0.66 s / p99 1.35 s，吞吐 150–180 tok/s；官方 GLM 是 0.54 / 1.96 s、45 tok/s。30 分钟 soak 179/180。
- **缓存计费是反的**：缓存命中的 token 比未命中贵 25%（约 1.68 对 1.34 额度/token），重复发长文档反而更费额度。
- **其他问题**：
  - 并发上限 2，第 3 个同时请求直接 429；
  - MiniMax 的思考以 `<think>` 标签混在正文里，客户端会把思考过程当回答显示出来；
  - Anthropic 口一旦分到 MiniMax，非流式响应的 Content-Length 不对，客户端报"连接被提前关闭"。

## 1. 身份

**最短请求 "Reply with exactly: OK"**：

| | 回显 | prompt_tokens | 响应特征 |
|---|---|---|---|
| apigoto 落到 MiniMax 时 | MiniMax-M3 | 181（多出来的是 MiniMax 自带的约 164 token 系统提示，计入输入） | `base_resp`、`input_sensitive`、`output_sensitive`、`total_characters`；id = trace-id（32 hex）；思考写在 content 的 `<think>…</think>` 里 |
| apigoto 落到 GLM 时 | `glm-5-3-flash-260828` 或 `zai-org/GLM-5.3-Flash` | 17 / 25（和官方一样） | 思考在 `reasoning_content` |
| 智谱官方 | glm-5.3-flash | 17 | — |

- **MiniMax 部分的自述**：模型复述出的系统提示原文是 "Your model version is MiniMax-M3, developed by MiniMax. Knowledge cutoff: January 2026. Founded in early 2022, MiniMax is a global AI foundation model company…" 和 "You are a helpful assistant."；问身份答 "I was developed by MiniMax… MiniMax-M3"。站方没有做任何伪装。
- **路由规律**：
  - 21:53–22:01 的请求 100% 是 MiniMax；22:01–22:15 的探测大多落到 GLM；之后又以 MiniMax 为主。
  - 同一篇文档连续发，大多数时候会留在同一个上游，但也见过中途换到火山方舟。
  - 1 万 token 左右的新文档首发 38/38 都是 MiniMax。
- **跨账号缓存**：这次测到的 apigoto 请求全部落在 MiniMax，所以没能验证 GLM 那部分能不能读到官方缓存。不过 `zai-org` + 智谱格式 id 那一路返回了官方独有的同步工具 id 格式（`call_-7226153970098495520`），像是转发智谱官方。

## 2. 按上游看参数和思考

写代码题的思考，以及参数测试，每条都标出了实际落到的上游：

| 测试 | apigoto（上游） | 智谱官方 |
|---|---|---|
| 默认思考 | GLM-rxq 12.0k / 11.6k 字符，GLM-智谱id 11.5k | 12.4k |
| effort low / high / max | 0（rxq）/ 76（智谱id）/ 18.9k（智谱id） | 0 / 72 / 13.4k |
| `thinking: disabled` | 200，落到火山方舟（照样思考）；另一次落到 MiniMax，思考写在正文里 | 400 |
| `reasoning_effort: none` | 400「请求模型不支持此内容」；另一次落到智谱id，思考 0 | 400 |
| `max_tokens=16` / `max_completion_tokens=16` | 都没生效（rxq，输出 138 / 207 token） | max_tokens 生效 |
| `max_tokens=999999` | 200（rxq） | 400 |
| `stop` | 正文为空（rxq，同官方） | 正文为空 |
| `n=2` | 400 "upstream error" | 只回 1 条 |
| 非法 effort | 400（MiniMax 原文 "allowed: low, medium, high, xhigh, max (2013)"） | 400 code 1210 |
| JSON 模式 / 工具调用 | 正常（rxq） | 正常 |

**Anthropic 口 `/v1/messages`**：
- 落到 MiniMax 时，非流式响应的 Content-Length 和实际内容对不上，客户端报 "peer closed connection"，这次 7 次里 6 次失败；流式能用。
- 落到火山方舟时正常，有 thinking 块。
- count_tokens 404。

## 3. 智力（`suite/iq.ref-20260924.json`，max_tokens 32000，流式；并发上限 2，只跑了第一遍加第二遍的前 7 题）

| | apigoto（26 题 MiniMax + 1 题 GLM） | 智谱官方（冻结） | ikuncode（冻结） | ooioo 默认（09-27） |
|---|---|---|---|---|
| 第一遍 27 题 | **17/27** | 22/27 | 25/27 | 15/27 |
| 基础推理 / 较难 / 很难（第一遍） | 5/6 · 4/7 · 8/14 | 6/6 · 6/7 · 10/14 | 6/6 · 6/7 · 13/14 | — |
| 想满 32k 没答完 | 7（H2 H4 H7 X3 X4 X7 X8） | 3 | 0 | — |
| 答完的题里答对 | 17/20 = 85%（加上第二遍 7 题：23/27 = 85%） | 96%（两遍 47/49） | 96%（两遍 51/53） | 65%（两遍 33/51） |
| 固定答错 | R10（两遍）、X12、X13 | — | — | — |

MiniMax-M3 在这套题上思考特别长，超过四分之一的难题在 32k 以内想不完，答完的题正确率 85%，比 GLM-5.3-Flash 官方低约 10 个百分点。

## 4. 延迟、稳定性、吞吐（北京直连，同一时段）

| | 成功 | 首 token p50 / p90 / p99 | 总耗时 p50 / p99 / max |
|---|---|---|---|
| **顺序 60 次（22:53–22:56）** | | | |
| apigoto（这段 60/60 都是 MiniMax） | 60/60 | 0.66 / 0.88 / 1.35 | 0.97 / 1.62 / 2.84 |
| 智谱官方 | 60/60 | 0.54 / 1.35 / 1.96 | 1.39 / 2.90 / 3.12 |
| ikuncode | 60/60 | 2.39 / 3.44 / 3.67 | 3.31 / 5.28 / 6.88 |
| **30 分钟 soak（22:56–23:26，每 10 秒一次）** | | | |
| apigoto | 179/180（1 次并发 429） | 0.86 / 1.99 / 4.65 | 1.20 / 5.37 / 8.96 |
| — 其中 MiniMax（133 次） | | 0.75 / — / 6.71 | 1.07 / 7.03 |
| — 其中 GLM 各家（46 次） | | 1.16–1.56 / — / 1.4–3.8 | 1.9–2.5 / 2.3–5.4 |
| 智谱官方 | 180/180 | 0.56 / 1.32 / 1.98 | 1.42 / 3.09 / 4.13 |
| ikuncode | 180/180 | 3.07 / 5.05 / 6.75 | 4.12 / 10.08 / 17.65 |

- **吞吐**（约 600 词长回答，3 次，都落到 MiniMax）：153 / 174 / 182 tok/s，每 chunk 约 2.7 token。思考写在正文里，首个字 0.8–1.1 s 就出来。官方 43–47 tok/s，ikuncode 42–44 tok/s，这两家要先思考 50–110 秒才出正文。
- **并发**：同时 2 个正常，同时 3 个全部 429（42901 "concurrency limit exceeded"）。计数释放有延迟：两个请求在跑时，第三个顺序请求也会被拒（leak 组 30 次全被拒）。所以 30 并发测不了。

## 5. 缓存、长上下文

- **缓存**：
  - MiniMax 部分几乎整段命中（9,465 / 9,466），多轮对话也覆盖，空闲 7 分钟（420 s）后仍命中。
  - 火山方舟部分有自己的缓存（10,240 / 10,254）。
  - 但计费上命中不打折，反而更贵（见 §6）。
- **长上下文**（自然文本三针，这批请求全部落到 MiniMax）：2 万 / 5.7 万 / 11.4 万 / 17.8 万 / 44.9 万 token 都是 3/3。17.8 万 token 首 token 4.1 s，官方 19.1 万 token 要 13.4 s。

## 6. 额度（计费）

套餐按 "rpm_credits" 计量：每 7 天 2500 万，约合 $3.72。用 `/v1/usage` 做前后差分，跑了两轮，结果一致：

| 请求 | 额度消耗（两轮） |
|---|---|
| 1.8 万 token 新文档 + 118–200 输出 | 24,905 / 25,346 |
| **同一文档再发一次（命中 18,027 token）+ 26–28 输出** | **30,435 / 30,424** |
| 193 输入 + 831–863 输出 | 4,769 / 4,942 |

- **反推单价**：未命中输入 ≈ 1.34 额度/token，**缓存命中 ≈ 1.68 额度/token（贵 25%）**，输出 ≈ 5.4 额度/token。
- **折合美元**：约 $0.20 / $0.25 / $0.80 每百万 token（输入 / 缓存命中 / 输出）。
- **一周额度大约够**：1,860 万输入 token，或 460 万输出 token。
- **注意**：落到 MiniMax 时，每个请求还会多计约 164 token 的 MiniMax 系统提示。

## 7. 对比参考站 ikuncode（GLM；冻结 09-25，refcheck 09-28 SAME；延迟为今天同一时段实测）

| | apigoto glm-5.3-flash | ikuncode glm-5.3-flash | 官方 |
|---|---|---|---|
| 实际模型 | **74% 是 MiniMax-M3**，其余为三家托管的 GLM-5.3-Flash | 智谱后端 GLM-5.3-Flash | — |
| 智力（答完的题里答对） | 85%（第一遍 17/27，7 题没想完） | 96%（第一遍 25/27） | 96%（第一遍 22/27） |
| 顺序首 token p50 / p99 | **0.66 / 1.35 s** | 2.39 / 3.67 s | 0.54 / 1.96 s |
| soak 首 token p99 | 4.65 s | 6.75 s | 1.98 s |
| 吞吐 | 150–180 tok/s（MiniMax） | 42–44 tok/s | 43–47 tok/s |
| 并发 | 上限 2 | 30 并发可用（09-25） | 30 并发可用 |
| 参数行为 | 取决于落到哪个上游，每次都可能不同 | 同官方 | — |
| 缓存 | 命中率高但计费更贵 | 按官方比例打折 | 打折 |
| Anthropic 口 | 落到 MiniMax 时非流式坏掉 | 可用 | 可用 |

**结论**：想要 GLM-5.3-Flash，apigoto 不合格，四次里有三次拿到的是 MiniMax-M3。它的优势只有 MiniMax 本身带来的速度，而且这是个免费套餐，只能 2 并发。

## 8. 方法学备注

- **判定混合池**：给每条响应按回显、id 格式、`base_resp` 字段打上游标签，再分上游统计。混在一起算的平均值没有意义。
- **跨账号缓存要分上游看**：这家同一篇文档连续发，大多会留在同一个上游。验证 GLM 部分时要每次换新文档，而且只看首发。这次 38 次长文档首发都落到 MiniMax，所以 GLM 部分的后端没有验证到。
- **并发上限 2 的站点**：只能串行测，并发测试不适用。智力题 1 路串行很慢，这次只跑了一遍半。
- **额度差分**：新文档 / 同文档命中 / 纯输出三步，两轮一致，排除了偶然误差。
