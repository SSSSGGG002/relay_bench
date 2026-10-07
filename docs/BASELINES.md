# 测试基线与测试指标（整理于 2026-10-06）

这份文档把 relay-bench 里所有**基线**（拿来对照的标尺）和**指标**（每项测什么、怎么判）集中列出来。
怎么跑的细节见 [README](../README.md)，各站历史报告见 [reports/](../reports/README.md)，Fable 的题目原文见 [Fable测试题库-20260922.md](Fable测试题库-20260922.md)。

---

## 1. 基线分三层

| 层 | 位置 | 是什么 | 怎么用 |
|---|---|---|---|
| 官方金标准 | `suite/golden/<model>.json` | 订阅直连官方（`golden.py` → `claude -p`）跑出来的知识阶梯 + 开放式探针答案 | `report.py` 按**声称型号**自动逐题对比，判断知识是否比官方旧或新 |
| 冻结参考站 | `suite/reference/<name>.json` | 某个参考站一次完整测试的冻结结果：指纹、IQ 逐题、知识、上下文、缓存、带日期和路线的延迟 | 新站和它横向比；**复用前必须先跑 refcheck**，SAME 才能复用 |
| 固定题库 | `suite/iq*.json`、`suite/knowledge.json`、`suite/corpus/natural.txt` | 智力题（答案由代码生成）、知识阶梯、长上下文用的自然文本 | 题库换了，分数就不能和旧基线比，所以参考站都钉死题库 md5 |

### 1.1 选哪个基线（用户规定）

| 被测模型 | 必须对比的基线 | 用的脚本 | 规则来源 |
|---|---|---|---|
| Claude（只测 opus-5-5 / opus-5 / sonnet-5） | `suite/golden/` 官方 + `suite/reference/ikuncode-kiro.json`（opus-5 / sonnet-5）+ `ikuncode-opus55.json`（opus-5-5）；计费比 `ikuncode-ccrev-cost.json`；注入/缓存比 `ikuncode-ccrev-injcache.json` | `bench.py` + `report.py`，参考站漂移用 `refcheck.py`，计费用 `costcheck.py --ref`，注入/缓存用 `injcache.py` | 09-25：新站报告必须有 ikuncode 对比节 |
| GLM（glm-5.3-flash 等） | `zhipu-official-glm53flash.json` + `ikuncode-glm53flash*.json` | `glmsuite.py run/summarize/compare` | 09-25：GLM 一律对比官方 + ikuncode 冻结基线 |
| DeepSeek（deepseek-v4-flash） | `ikuncode-dsv4flash.json` | `glmsuite.py`（`--model deepseek-v4-flash`） | 10-02：ds v4-flash 对比冻结的 ikuncode 基线 |
| GPT（只测 gpt-5.6-sol / gpt-5.6-terra / gpt-6-astra） | `spatialai-gpt.json` | `gptcheck.py`（注入 / 参数 / 缓存 / TTL / 会话实扣 / 延迟 / soak，不测智力） | 10-07：GPT 基线用 spatialai，智力用户另有方法 |

三条共同规则：

1. **先 refcheck**：SAME → 复用冻结的智力 / 知识 / 分词 / 参数指纹；DRIFT → 先重测参考站。
2. **延迟、稳定性、缓存 TTL 不复用**：这些随路线和时段变化。要比 p50/p99，就在同一台机器、同一时段，给参考站也跑一遍 `lat` / `soak`。
3. 用北京服务器测之前先跟用户打招呼；key 放自己子目录，测完删掉。

---

## 2. 基线清单

### 2.1 官方金标准 `suite/golden/`

24 题知识阶梯（K00–K23，2024-11 → 2026-09 逐月事实）+ 10 题开放式探针（C1–C10）+ 3 次号池混合检查。

| 文件 | 采集日期 | 阶梯分类 | 阶梯前沿 | 开放式前沿 | 状态 |
|---|---|---|---|---|---|
| `claude-opus-5.json` | 2026-09-10 | 8 对 / 16 UNKNOWN | 2025-11 | 2026-09 | 可用 |
| `claude-sonnet-5.json` | 2026-09-10 | 8 对 / 16 UNKNOWN | 2025-11 | 2026-06 | 可用 |
| `claude-fable-5-1.json` | 2026-09-10 | 14 对 / 2 错 / 8 UNKNOWN | 2026-03 | 2026-09 | 可用 |
| `claude-opus-5-5.json` | 2026-09-25 | 24 题全空 | — | — | **无效，未入库**（采集时订阅 OAuth 已过期，答案全是空串）。重登订阅后用 `golden.py claude-opus-5-5` 重采 |

判读要点：

- 官方模型对标称截止前 4–6 个月的事大多答 UNKNOWN（官方 Opus 5 标称 2026-05，可靠记忆只到 2025-11），所以**不拿标称截止日期硬比**，只拿官方同型号的实测答案逐题比。
- 官方知道而中转不知道 = 疑似降级；中转知道而官方不知道 = 映射到别的模型或注入了信息。
- 决定性题目每题重复 3 次以上，官方稳定答对、中转稳定 UNKNOWN 才算定案。
- C8（"你知道的最新 Claude 型号"）被 Claude Code 自带的型号列表污染，`report.py` 对比时跳过。

### 2.2 冻结参考站 `suite/reference/`

| 文件 | 模型 | 冻结时间 | 路线 | 代表什么 |
|---|---|---|---|---|
| `ikuncode-kiro.json` | claude-opus-5 / claude-sonnet-5 | 09-24（IQ/知识/缓存/上下文）+ 09-25（北京延迟） | Mac + 北京直连 | Kiro 池里最好的档：opus-5 = 真 Opus 4.6/5 档；sonnet-5 = **Sonnet 4.5 冒名**，代表"Kiro 池最好的 Sonnet 档"，不代表真 Sonnet 5 |
| `zhipu-official-glm53flash.json` | glm-5.3-flash | 09-25 | 北京阿里云直连 | **官方标尺**（智谱开放平台 paas/v4 + anthropic） |
| `ikuncode-glm53flash.json` | glm-5.3-flash | 09-25 | 北京阿里云直连 | "好的 GLM 中转"的标尺：智谱后端，跨账号缓存双向命中 |
| `ikuncode-glm53flash-20261002.json` | glm-5.3-flash | 10-02 | Mac + Clash TUN | ikuncode **漂移后**的快照：接入层换成 OpenRouter 风格网关、多供应商轮换。智力只跑 9 题，完整分沿用 09-25 的 51/54 |
| `ikuncode-dsv4flash.json` | deepseek-v4-flash | 10-02 | Mac + Clash TUN | deepseek-official 分组，回显 deepseek-v4-flash-0731 |
| `ikuncode-opus55.json` | claude-opus-5-5 | 10-07（IQ/知识/上下文/协议/延迟）+ 09-26（北京延迟、soak） | Mac + Clash 代理；09-26 北京直连 | cc逆向分组 Kiro 通道上的 2026 前沿档：IQ 27/27、区分题 12/12、知识到 2026-03、55 万 token 3 针全中。refcheck 可直接用。10-07 起接入层漂移：自动缓存取消、token 计数约 ×1.35 |
| `ikuncode-ccrev-cost.json` | claude-opus-5-5 / opus-5 / sonnet-5 / sonnet-5-5 | 10-07 | Mac 直连 | **计费基线**：cc逆向分组固定负载的实扣金额（costcheck v1），按站点公式诚实计费 |
| `ikuncode-ccrev-injcache.json` | claude-sonnet-5-5 / opus-5-5 / sonnet-5 | 10-07 | Mac 直连（TTL 补测走代理） | **注入与缓存基线**：cc逆向分组其实也是 Kiro 池；隐藏提示词存在但不计费，缓存是中转模拟的、规则对用户公道（见 3.5.1） |
| `spatialai-gpt.json` | gpt-5.6-sol / gpt-5.6-terra / gpt-6-astra | 10-07 | Mac + Clash 代理 | **GPT 基线**：真 OpenAI Codex 号池；注入、缓存、TTL、会话实扣、p50/p99（gptcheck v1） |

所有参考站的 IQ 题库都是 `suite/iq.ref-20260924.json`，md5 `ad1f46e9f80233a7264d9f01196c9993`（和当前 `suite/iq.json` 一样）。

### 2.3 题库 `suite/`

| 文件 | 内容 | 备注 |
|---|---|---|
| `iq.json` | 当前智力题库，27 题：R2–R10（reason 6）、H1–H7（hard 7）、X1–X14（xhard 14），seed 20260909 | `bench.py` 默认题库 |
| `iq.ref-20260924.json` | `iq.json` 在 09-24 的钉死副本 | 参考站和 `glmsuite.py` 固定用它 |
| `iq_keep.json` | bench 保留的 26 题（去掉 H7） | 控制 `bench.py` 实际出哪些题 |
| `iq_screen.json` | screen 档 8 题：R7 R10 R3 R4 R9 H2 H3 X14 | 前沿接近全对、降级货明显失分、单题 30 s 内 |
| `iq_full.json` | 完整题库 41 题（含已删的 D 直答档和 R1/R5/R6/R8/R11/R12） | 只做存档和重新筛题 |
| `iq.v1/v2/v3.json` | 历史版本（26 / 26 / 33 题） | 旧报告的分数基于这些，不能和 v3 之后直接比 |
| `knowledge.json` | 24 题知识阶梯 + 10 题开放式探针 + 各型号官方截止表 | 事实 09-09 按维基/官方公告核过；每隔几个月要补新事实 |
| `corpus/natural.txt` | 约 70 万字符的自然文本（历史报告拼接） | `glmsuite.py ctx` 组的针测语料；合成文本在部分池会空回复，所以针测用自然文本 |
| `gpt_manual_probe.md` | GPT 渠道手工探针 | |

---

## 3. 测试指标

### 3.1 身份（定性结论，优先级最高）

| 指标 | 测法 | 判读 |
|---|---|---|
| 知识阶梯前沿 | 24 题逐月事实，答不上答 UNKNOWN；Claude 关思考、`max_tokens 500` | 和金标准逐题比，见 2.1。**唯一无法通过改写请求伪造的指纹** |
| 开放式年代探针 | 现任教宗、日本首相、纽约市长、最新 Claude/GPT/GLM 型号、诺贝尔文学奖 | 必须给答案，不受"不知道就答 UNKNOWN"压制。答方济各 / 石破 = 2025-05 以前的模型 |
| 自报厂商 / 型号 / 截止 | 直接问 | **只作参考，不作 FAKE 证据**：真 Fable 5.1 在 Kiro 风格提示下会自称 Sonnet 4.5 |
| 隐藏系统提示 | 让模型复述收到的系统提示；5-token 请求的 input_tokens | 抓出 "You are Kiro / Claude Code / Codex"；Kiro 池 6.1–6.5k token 隐藏提示计为 cache_read。GLM 官方自己也会复述 "You are an AI assistant accessed via an API."，这句不算注入 |
| 签名验证 | thinking 块 `signature` 篡改后重放 | 只有 Anthropic 后端能验签；无签名 = 不是官方 API 出来的 |
| 号池混合 | 按响应 id 分族统计（`msg_011C…` / `msg_pre_…` / `msg_<32hex>` / 随机 id） | 混池不要求平均，每族单独出结论 |
| ModelTrace 指纹 | 几百个 1–355 随机整数的分布比对 | 闭集 13 个模型，没有 fable / 3.7 Sonnet / Sonnet 4.5 / 国模；家族不符且 ≥90% 才判假映射 |
| 跨账号缓存（GLM） | 官方 key 写入隐式缓存，中转读；反过来再测 | **GLM 身份的决定性证据**：智谱隐式缓存全局共享，双向命中 = 同一后端；对照组用新文档必须 0 |

### 3.2 协议与参数透传

| 指标 | 官方行为（基线） | 异常含义 |
|---|---|---|
| 响应 id 格式 | Anthropic `msg_01`+22 位；OpenAI `chatcmpl-`；智谱 14 位时间戳+16 hex；DeepSeek uuid | 被重新生成 = 有适配层；`toolu_bdrk_` = Bedrock |
| usage 字段集合 | 见各参考站 `fingerprint.usage_keys` | 多出 `credit_usage` / `cost` / `is_byok` = 计费或网关层 |
| 参数严格性 | Claude 5 系列 temperature/top_k/budget_tokens/prefill 必 400；智谱关思考 / effort none / max_tokens 999999 → 400（1210），temperature 5 → 200 | 全部 200 = 请求被改写后转发 |
| `stop_sequences` / `max_tokens` 是否生效 | 生效 | 不生效直接影响账单和程序正确性（ikuncode Kiro 就不生效） |
| 默认思考 | Opus 5 / Sonnet 5 / Fable 默认思考；智谱默认完整思考（写代码题 14–20k 字符） | 某入口默认几乎不思考 = 被改成低 effort，难题会掉分 |
| 分词增量 | GLM 官方：zh 1050 / digits 801 / en 301 / code 595 / +system 7；DeepSeek（ikuncode）：zh 1020 / digits 801 / en 293 / code 601 / system 6；"Reply with exactly: OK" 官方 GLM 17、DeepSeek 88 | 逐位一致 = 没有额外 token；比率乱飞 = usage 是编的 |
| Anthropic 口转换 | 有 `ping` 事件、thinking 带签名 | new-api 转换常见：非流式丢 thinking、effort 参数被忽略、count_tokens 404 |

### 3.3 智力

| 指标 | 测法 | 判读 |
|---|---|---|
| IQ 总分 | `bench.py`：26 题单次；`glmsuite.py`：27 题 × 2 遍，max_tokens 32000，默认思考，流式 | 只当**地板检查**：前沿之间拉不开，前沿和降级货拉得开 |
| 分档 | reason / hard / xhard | xhard 负责前沿之间的顶端分辨 |
| 截断数（L） | 想满 max_tokens 被截断 | 官方 GLM 有 5 次截断；不认 max_tokens 的中转会多想，分数要连截断数看 |
| 关思考 IQ | `--iq-body '{"reasoning_effort":"none"}'` 等 | 先确认关思考真的生效（看 completion_tokens 和首正文时间，不只看 reasoning_content 是否为空） |
| 区分题（drift 集） | 冻结参考里每题都对、耗时 < 150 s 的 10–12 题 | refcheck 用；允许最多掉 2 题 |

历史分档参考（`suite/iq.json` 27 题题库，出处是本地报告，未入库）：

| 渠道 | 实际模型 | IQ | Kiro 区分题 12 题 |
|---|---|---|---|
| ikuncode opus-5 | Opus 4.6/5 档 | 25/26 | 12/12 |
| ikuncode sonnet-5 | Sonnet 4.5 | 23/27 | 11/12 |
| ikuncode opus-5-5（09-26、10-07 两次） | 2026 前沿档，与 Opus 5.5 相符 | 27/27 | 12/12 |
| rsiai opus-5 / opus-5-5 | Opus 4.6/5 档 / 2026 前沿档 | — | 11/12 / 12/12 |
| cheaprouter fable-5-1 | 模板压制的 Fable 级 | — | 9/12 |
| ahg opus-5（三池混） | 半数 2024 老模型 | — | 2/12 |
| buliangren / junliai | 3.7 Sonnet（Kiro / R24 池） | 14–15/27 | 0/12 |

真 Opus 5 / Sonnet 5 历史上约 95%。GLM：官方 47/54，ikuncode 51/54。DeepSeek ikuncode：开思考 49/54，关思考 30/54。

### 3.4 上下文

| 指标 | 测法 | 判读 |
|---|---|---|
| 三针召回 | 10% / 50% / 90% 深度三根针；bench 20k/60k/130k/230k，glmsuite 20k/60k/130k/190k + 可选极限 | 截断、丢中段、1M 是否真实（200K 模型 230k 必报错） |
| usage 线性 | input_tokens 是否随长度线性增长 | 不线性 = 截断后照原长计费，或 usage 是编的 |
| 自然文本 vs 合成文本 | 两种都测 | ikuncode sonnet-5 合成文本 ≥60k 空回复，自然文本 130k 正常 |
| 长上下文下规则遵守 / 多轮记忆 | 60k 处的 system 规则；20 轮历史 | 丢 system / 截历史 |
| 参考值 | 官方 glm-5.3-flash 接受 53 万 token 输入（478k 三针全中）；ikuncode Kiro opus-5 230k 3/3 | |

### 3.5 缓存

| 指标 | 测法 | 判读 |
|---|---|---|
| 命中率 | 同一前缀连打；**前缀至少 10k token**（3.5k 探针在 ikuncode opus-5-5 上误报 0 命中，门槛约 4096） | 账号池轮询不同账号 → 永远不命中，一直付全价 |
| 真假命中 | 命中数和 TTFT 一起看；换同样大小的新前缀必须不命中 | 新前缀也报命中 / 命中比例恒定（Kiro 池 ≈92%、rsiai 15/85 拆分）= 固定拆分的假命中 |
| TTL | 空闲 5 s – 600 s 后重打（`--gaps` / `--ttl`） | 官方 GLM 5–7 分钟内基本命中、10 分钟失效；ikuncode GLM 09-25 ≤3 分钟 100%，10-02 只剩约四成 |
| 计费核对 | 余额差分或 new-api `/api/log/token?key=` 逐条账单 | 缓存读不打折、token 虚高、截断照全额扣，都要用实扣金额核对，不能只看 usage |

### 3.5.1 注入与缓存探针 `injcache.py` —— 2026-10-07 新增

Kiro 类渠道上游不提供缓存，usage 里的缓存数字是中转站自己算的，所以不能只看「命中率」，要看中转定的规则对用户是否公道、计费是否和 usage 一致。

| 段 | 内容 | 看什么 |
|---|---|---|
| I-base / I-sys2k | OK ×3；再加一段 2k token system | OK 计费 input − 5 = 每请求注入计费量；几十是协议转换，几千是隐藏提示词被计费 |
| I-ask | 你是谁 / 复述上文 / 列工具 / 日期与知识截止 / 受何限制；再带 canary system 复述 | 号池身份、隐藏提示词是否存在、是否回显用户 system |
| C-size | 12k / 25k / 50k 新前缀带 cache_control，同问题 ×2 + 换问题 ×1 | 首次 read 必须为 0；read 应等于 write；换问题 read 不应变；TTFT 是否下降 |
| C-auto | 12k / 25k 不带 cache_control ×2 | 不带也报命中 = 自动缓存或拆分 |
| C-small | 3k / 5k | 最小可缓存长度 |
| C-turn | 12k system + 4 轮 | 历史是否进缓存 |
| C-ttl | 360 s 后重发 12k 前缀 | 是否还算命中 |
| 账单 | `/api/log/token` 按 request id 逐条对 | usage 与实扣 token 是否一致 |

```bash
RB_KEY=sk-... .venv/bin/python injcache.py --label <站>-<模型>-<日期> --base https://<站> --model <模型> [--direct]
.venv/bin/python injcache.py --summary results/injcache/<a>.json [<b>.json ...]      # 汇总表
# 某一步网络失败时只补 TTL 并重新挂账单：
.venv/bin/python injcache.py --label x --base https://<站> --model <模型> --skip I,C --merge-into results/injcache/<a>.json
```

**基线 ikuncode cc逆向（2026-10-07，`suite/reference/ikuncode-ccrev-injcache.json`）**：三个模型都自称「Kiro … made by AWS … connected through an ACP client」，拒谈上文、工具和规则（「I can't discuss that」），不回显用户 system。

| 模型 | OK 计费 input | 注入≈ | 2k system 计费/发送 | 不带 cache_control | 新前缀首次 read | 最小命中 | read=write | 多轮 read | 360 s 后 | 账单一致 |
|---|---|---|---|---|---|---|---|---|---|---|
| claude-sonnet-5-5 | 69 / 74 / 74 | 64 | 2130 / 2019 | 0 命中 | 0 | 3k | 否（15567→15306、6414→6700） | 12549 恒定 | 失效，重写 | 32/32 |
| claude-opus-5-5 | 77 ×3 | 72 | 2551 / 2022 | 0 命中 | 0 | 3k | 否（3148→3286、28589→29216） | 14496 恒定 | 失效，重写 | 34/34 |
| claude-sonnet-5 | 77 ×3 | 72 | 2824 / 2018 | 0 命中 | 0 | 3k | 否（28562→27902/27800） | 15599 / 16245 / 15685 | 失效，重写 | 34/34 |

结论：隐藏提示词存在但不计费；缓存是中转模拟的，但规则贴近官方（要 cache_control、5 分钟 TTL、只缓存断点前的部分），新前缀不报假命中，缓存读按 0.1（opus-5-5 0.05）计价，对用户有利。read 和 write 对不上、同一前缀总 token 逐次变、命中后首字不变快，说明数字不是上游真值。新站对照时重点看：新前缀首次是否就报 read、不带 cache_control 是否也报命中、6 分钟后是否仍算命中、注入是否计费。

### 3.6 延迟、稳定性、速度

| 指标 | 测法 | 判读 |
|---|---|---|
| 首 token / 首正文 / 总耗时 p50 p90 p99 | glmsuite `lat`：顺序 60 次 + 30 并发 × 2 波；北京服务器 `lat.py` | p99 至少要 60 个样本；Kiro 池 p99 8–23 s 算抖 |
| 错误率 / 空回复 / 挂起 | 同上，外加 soak | 区分站点错误和本机路线错误（Mac + Clash 下约 5% SSL EOF 是本机问题） |
| soak | 每 10 秒一次，30 分钟 ≈ 180 样本 | 单独跑，别和别的负载叠加 |
| 吞吐 tok/s | 约 600 词长回答 × 3 取中位 | 参考：官方 GLM 51、ikuncode GLM 43、ikuncode DeepSeek 84 |
| 假流式 | 每 chunk token 数、TTFT 后是否一次吐完 | 每 chunk 远大于 1，或 TTFT 15–18 s 后一次吐完（ikuncode Kiro）= 上游非流式 |
| 限流 | 并发时的 429 / 1302 | 官方智谱 key 30 并发触发 1302 账户限速，是账户档位，不算服务故障 |

### 3.7 实际花费（固定负载实扣对账）—— 2026-10-07 新增

倍率低不等于便宜：有的站每个请求注入几千 token 的隐藏提示，再把输入固定拆成 70–80%「缓存命中」，账面倍率很低，实际扣费却不低。所以各站之间比价格，要比**跑完同一套负载实际扣了多少钱**，不比倍率。

工具 `costcheck.py`：每个模型发同一套确定性负载，按响应头 `x-oneapi-request-id` 把每次调用和站点逐条账单（new-api `/api/log/token`）对上，汇总实扣金额。

| 段 | 内容 | 看什么 |
|---|---|---|
| `inject` | "Reply with exactly: OK" × 3 | 计费输入减去实际发送量 = 每个请求被注入多少 token |
| `fresh` | 约 3k 和 12k o200k token 的全新文档各 1 次，不带 cache_control | 全新文档不可能命中缓存：报了 cache_read = 缓存是拆分出来的。两点斜率 = 站点分词比（相对 o200k） |
| `session` | Claude Code 式：CC 身份 + 约 12k token 文档带 cache_control，5 轮对话，历史累积 | 真实 agent 场景下的缓存和计费 |
| `iq` | 8 道 screen 智力题，默认思考，max_tokens 16000 | 「跑这些题实际花多少钱」，顺带出智力分 |

输出指标：

- **实扣 $**：站内美元（quota ÷ 500000）。乘上你自己的充值价（元 / 站内美元）就是实际花费，报告表里留了填价格的列。
- **理想 $**：用站点自己公布的公式，算实际发送的内容应该扣多少（无注入；会话里系统文档写一次、之后都读缓存；输出 token 用站点报告的数）。
- **实扣/理想**：≈1 说明按标价诚实计费；明显大于 1 说明注入或缓存拆分在加价，倍率要乘上这个系数再比。
- **每请求注入 token**、**分词比**、**新文档的 cache_read**、**报告缓存命中率**、智力分、错误数。
- 站点总用量 `/v1/dashboard/billing/usage` 的前后差值（单位是站内美分，已换算成美元）做交叉核对；同一把 key 同时有别的使用时会偏大。

```bash
RB_KEY=sk-... python3 costcheck.py --label <站>-<分组>-<日期> --base https://<站> \
    --models claude-opus-5-5,claude-opus-5,claude-sonnet-5 --direct --route "<路线>"
python3 costcheck.py --report results/costcheck/<label>.json [--ref <参考>]           # 重出表格
python3 costcheck.py --report results/costcheck/<label>.json --freeze suite/reference/<名字>-cost.json   # 冻结成计费基线
```

分词比没法独立核实，因为没有官方计数做对照。负载内容在各站完全相同（只有开头一行 nonce 不同），所以同一模型在两个站的分词比可以直接比，高出很多（比如 1.2 对 2.0）的那家就是在虚报 token。

**计费基线 ikuncode cc逆向（2026-10-07，`suite/reference/ikuncode-ccrev-cost.json`）**：

| 模型 | 跑完一套实扣（站内 $） | 理想 $ | 实扣/理想 | 报告缓存命中 | 每请求注入 | 分词比 | 新文档 cache_read | IQ |
|---|---|---|---|---|---|---|---|---|
| claude-opus-5-5 | 0.1375 | 0.1322 | 1.04× | 63% | 68 | 1.19 | 0 / 0 | 8/8 |
| claude-opus-5 | 0.1908 | 0.1831 | 1.04× | 63% | 68 | 1.19 | 0 / 0 | 7/8 |
| claude-sonnet-5 | 0.0942 | 0.0911 | 1.03× | 63% | 68 | 1.19 | 0 / 0 | 7/8 |
| claude-sonnet-5-5（10-07 单独一轮） | 0.0688 | 0.0671 | 1.02× | 64% | 63 | 1.19 | 0 / 0 | 8/8 |

站点定价：扣费 = (输入 + 缓存读×0.1〔opus-5-5 是 0.05〕+ 缓存写×1.25 + 输出×5) × 模型倍率（opus-5-5 2 / opus-5 2.5 / sonnet-5 1）× 分组倍率 0.5，站内 $ = quota ÷ 500000。历史 448 条和本次 54 条账单逐条复算，0 条不符。新站和它比时，两边各乘自己的充值价再比「跑完一套实扣」。

```bash
RB_KEY=sk-... python3 costcheck.py --label <站>-<分组>-<日期> --base https://<站> \
    --models claude-opus-5-5,claude-opus-5,claude-sonnet-5 --ref suite/reference/ikuncode-ccrev-cost.json
```

### 3.8 GPT 渠道（gptcheck.py）—— 2026-10-07 新增

GPT 中转多数是 Codex 订阅号池：每个请求会被塞进 4k 多 token 的 Codex 提示词。有的站在 chat/completions 上把它藏起来、不计费，在 /v1/responses 上照收。所以两个接口都要测。

| 段 | 内容 | 看什么 |
|---|---|---|
| `inject` | OK × 3 走 chat，× 3 走 responses | chat 报告输入 vs responses 报告输入；responses 回显的 `instructions` 和 `usage.attribution.request_fields.instructions`；两个接口各自被扣了多少 |
| `params` | temperature 5、max_tokens / max_completion_tokens 16、非法 / none effort、stop、logprobs、n=2；responses 发 prompt_cache_key / temperature / max_output_tokens / store 看回显 | 参数是否原样到达模型 |
| `cache` | 约 12k token 文档连发 3 次 + 1 次新文档，chat 和 responses 各一轮 | OpenAI 前缀缓存是否真命中；新文档必须 0（注入部分除外） |
| `ttl` | 每个间隔一份文档，写入后空闲 30 / 120 / 300 / 600 s 再读 | 缓存寿命；忽中忽不中 = 多账号轮询 |
| `session` | chat 5 轮，system 是 12k 文档 | 真实使用下的缓存和实扣 |
| `lat` | 流式 OK：顺序 60 + 30 并发 × 2 | 首 token 和总耗时的 p50 / p90 / p99、错误、429 |
| `soak` | 每 10 秒一次，30 分钟 | 长窗口稳定性 |

计费：sub2api 风格网关的 `GET /v1/usage` 会实时给出每个模型的累计 token、cost、actual_cost。每段前后各取一次差值，就是这一段实扣多少。没有这个接口的站，计费列留空，改用余额差分。

**GPT 基线 spatialai.vip（2026-10-07，`suite/reference/spatialai-gpt.json`，Mac + Clash 代理）**：

| | gpt-5.6-sol | gpt-5.6-terra | gpt-6-astra |
|---|---|---|---|
| 后端 | 真 OpenAI，Codex 号池 | 同左 | 同左（GPT-6 版 Codex 提示词） |
| 每请求注入 | 4380 token | 4380 | 4114 |
| 注入计费 | chat 不计（按 11 token 扣）；responses 照扣，3840 记缓存读 | 同左 | chat 不计；responses 前两次全价 |
| chat 缓存（12k 文档 第 2/3 次） | 11008 / 11008（91%），新文档 0 | 同左 | 同左 |
| responses 缓存 | 只命中注入的 3840，用户文档不命中（prompt_cache_key 被换成随机） | 同左 | 同左 |
| TTL 30/120/300/600 s | 未中 / 中 / 未中 / 中 | 全中 | 全中 |
| 参数 | 全部被改写，只有非法 effort 返回 400 | 同左 | 同左 |
| 顺序首 token p50 / p99 | 1.47 / 28.8 s | 1.67 / 30.6 s | 1.99 / 9.3 s |
| 30 并发首 token p50 / p99 | 5.05 / 51.6 s（1 次 429） | 8.7 / 28.6 s | 5.9 / 11.7 s |
| soak 30 min（每 10 s 一次） | 179/180，首 token p50 3.25 / p99 5.6 s | 178/180，3.44 / 6.97 s | 178/180，3.91 / 9.49 s |
| 一套负载实扣（站内 $） | 0.2494 | 0.0886 | 0.4816 |

实扣统一是名义价格的 0.29 倍。余额差分 $0.8196 等于各段 actual_cost 合计（不含 soak）。soak 的失败是每个模型各 1 次 429 `gateway_queue_full`，terra/astra 另各有 1 次本机 Clash 的 SSL EOF；长窗口下 sol/terra 没有再出现 30 s 卡顿，p99 在 7 s 以内。soak 期间有别的客户端共用这把 key（astra 多出 154 次请求），astra soak 的计费作废，延迟数据仍可用。

```bash
RB_KEY=sk-... python3 gptcheck.py run --label <站>-<日期> --base https://<站> --sections inject,params,cache,ttl,session [--proxy]
for m in gpt-5.6-sol gpt-5.6-terra gpt-6-astra; do RB_KEY=sk-... python3 gptcheck.py run --label <站>-<日期> --base https://<站> --models $m --sections lat; done
RB_KEY=sk-... python3 gptcheck.py run --label <站>-<日期> --base https://<站> --sections soak --soak-min 30
python3 gptcheck.py report --label <站>-<日期>
```

### 3.9 参考站核心数值速查

延迟单位秒，均为冻结时那一次的路线，**只用于同路线横向参考，不当常量**。

| 参考 | IQ | 顺序首 token p50 / p99 | 30 并发首 token p50 / p99 | soak 30 min | tok/s | 缓存 burst |
|---|---|---|---|---|---|---|
| 智谱官方 glm-5.3-flash（北京） | 47/54 | 0.54 / 1.46 | 0.68 / 1.70（25/60 被 1302 限速） | 180/180，p99 2.17 | 51.0 | 7/8 |
| ikuncode glm-5.3-flash 09-25（北京） | 51/54 | 2.09 / 3.53 | 3.53 / 14.2 | 180/180，p99 5.0 | 42.7 | 14/14 |
| ikuncode glm-5.3-flash 10-02（Mac） | 7/9（沿用 51/54） | 1.83 / 8.21 | 3.60 / 8.17 | — | — | 3/5 |
| ikuncode deepseek-v4-flash 10-02（Mac） | 49/54（关思考 30/54） | 2.56 / 5.23 | 5.00 / 8.88 | 171/180，p99 8.03 | 83.9 | 13/14 |
| ikuncode Kiro opus-5 09-25（北京，lat.py 口径） | 25/26 | 2.87 / 5.65 | 3.36 / 6.46 | — | 假流式 | 固定拆分 |
| ikuncode opus-5-5 09-26（北京，lat.py 口径） | 27/27 | 1.94 / 4.80 | 2.77 / 6.08 | 180/180，p99 7.81 | 62–69 | 自动缓存 99.8% |
| ikuncode opus-5-5 10-07（Mac + Clash 代理，lat.py 口径） | 27/27 | 3.98 / 11.27 | 5.26 / 10.64 | — | 41–52 | 只认 cache_control，读 99.3–99.9% |
| ikuncode Kiro sonnet-5 09-25（北京，lat.py 口径） | 23/27 | 2.93 / 10.09 | 3.43 / 5.18 | 158/159，p99 26.06 | 假流式 | 固定拆分 |

---

## 4. 已知问题

- `suite/golden/claude-opus-5-5.json` 是空采集，已在 `.gitignore` 里排除。本机这份还在，`report.py` 会拿它对比声称 opus-5-5 的渠道，结果会被误判成"知道得比官方多"。重采前建议先挪开它。
- ikuncode GLM 已漂移：用 09-25 那份做 refcheck 会 DRIFT（关思考和 max_tokens 999999 现在都 200）。新站和 ikuncode GLM 比时，协议和缓存看 10-02 快照，完整智力分沿用 09-25。
- 2026-10-02 的两份参考是 Mac + Clash TUN 路线，延迟和 soak 数字带本机 SSL EOF 噪声。
- `lat.py` / `soak.py` 在北京服务器 `/root/bltest`，不在这个仓库里。
- GPT 没有官方金标准（没有官方 OpenAI key），`spatialai-gpt.json` 是中转参考，不是官方标尺。

## 5. 新增或更新基线

```bash
# 官方金标准（需要本机 Claude Code 登录订阅）
python3 golden.py claude-opus-5-5
# GLM / DeepSeek 参考站：先完整跑一轮 glmsuite，再冻结某个通道
python3 glmsuite.py freeze --run <run> --label <通道标签> --name <参考名> --note "<日期、路线、同窗口对照>" --annotate <手写说明.json>
```

冻结后检查三件事：`iq_bank.md5` 和当前题库一致；`source.route` 写清路线；`caveats` 写明哪些数不能复用。
