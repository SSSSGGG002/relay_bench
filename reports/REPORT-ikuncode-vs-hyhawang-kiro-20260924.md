# ikuncode Kiro 分组 vs hyhawang：claude-opus-5 / claude-sonnet-5（2026-09-24，重点智力与稳定性）

数据：ikuncode `results/ikun-kiro/`（bench：protocol/identity/knowledge/tokenizer/stability/speed/iq/fingerprint/cluster + 单独 soak）、`results/ikun-probes/`（延迟探针）、日志 `logs/ikun-kiro-*.log`；hyhawang 见 `REPORT-hyhawang-20260924.md`。
ikuncode key `sk-SqQx…`，分组 8 个模型（haiku-4-5、opus-4-5/4-6/4-7/4-8、opus-5、sonnet-4-6、sonnet-5）。海外/国内两条出口落同一后端，本机直连可达。

## 一句话结论
| | ikuncode Kiro 分组 | hyhawang k2 |
|---|---|---|
| 后端 | 单一 Kiro/Bedrock 号池（`msg_<32hex>`，Kiro prompt 6.1–6.5k 计为 cache_read，thinking **带真签名**） | 三个池随机混（011C 模板 / Kiro / 裸 hex），usage 估算 |
| opus-5 真身 | 知识到 2025-11（教宗 Leo XIV ✓、首相石破 ✗），自报 Sonnet 4.5，官方黄金基线对齐 Opus 4.6/5 档；**智力 25/26** | 老模型冒名，知识 2025-10；**智力 16/26** |
| sonnet-5 真身 | 知识 2025-11 阶梯 / 2024-10 开放式（教宗 Francis、日相石破、诺奖 Fosse），自报 Sonnet 4.5 → **Sonnet 4.5 冒名**；**智力 23/27** | 与 opus-5 同一老模型；**16/27** |
| 稳定性 | 无 RPM 限速（120/min 无 429），但**慢且抖**：顺序 p99 8–23 s、单次最长 53 s；30 并发新建连接约半数 TLS 失败、opus 读超时 130 s；soak p95 19–23 s、max 38–57 s | 100 RPM 硬限速；顺序 p99 3–5 s；30 并发 120/120；soak p95 5.5 s |

**智力上 ikuncode 完胜**（25/26、23/27 vs 16/26、16/27），已到 relay-bench 里真 Opus 5 / Sonnet 5 的档位；**稳定性上 hyhawang 明显更稳更快**，但它的模型是降级货。ikuncode 的 sonnet-5 名下仍是 Sonnet 4.5（和 micuapi 一样，Kiro 池的通病），只是 Sonnet 4.5 本身在这套题上就很强。

## 1. 身份（ikuncode）
- 两模型自报 `Claude Sonnet 4.5`、截止 2025-01；系统提示原文泄漏 "You are Kiro, an AI agent…"；opus 自称 Amazon 训练。
- opus-5：知识阶梯 6/6 到 2025-11（知道 Leo XIV、Krasznahorkai 诺奖等），与 hyhawang 老模型的 2025-10 边界不同，符合 Kiro 侧 Opus 4.6/5 档；sonnet-5：阶梯 7/7 到 2025-11 但开放式全是 2024 年答案（Francis / 石破 / Jon Fosse / GPT-4o）→ 4.5 档。
- **thinking 块有 signature**（opus adaptive+low 31 字符签名），篡改后重放却 200 不报错 → Bedrock 侧不验签，但至少不是伪造占位；hyhawang 两池都是无签名 43 字符占位。
- 参数校验 3–4/9 全 200；`stop_sequences` **不生效**（hyhawang 生效）；`max_tokens` **不生效**（限 40 输出 509 可见 token）；count_tokens 404；`max_tokens=999999` 200。
- 分词差分 1.32×/1.19×（Claude 新分词器比例），hyhawang 是 1.68×/0。
- ModelTrace 指纹：opus-5 → opus-5 100%、sonnet-5 → sonnet-5 100%（闭集，仅参考）。

## 2. 智力（suite/iq.json 26 题，默认 thinking，max_tokens 16000）
| | reason | hard | xhard | 合计 | hard 平均耗时 |
|---|---|---|---|---|---|
| ikuncode opus-5 | 6/6 | 7/7 | 12/13（X1 glitch：36 token 就 end_turn） | **25/26** | 46 s |
| ikuncode sonnet-5 | 5/6（R2） | 7/7 | 11/14（X1 X7 X8） | **23/27** | 195 s |
| hyhawang opus-5（两池） | 3/3 · 3/6 | 4/6 · 5/7 | 9/12 · 8/13 | 16/21 · 16/26 | 60–66 s |
| hyhawang sonnet-5（两池） | 3/6 · 4/6 | 4/6 · 4/7 | 8/13 · 8/14 | 15/25 · 16/27 | 70–94 s |
ikuncode 的错题都是"算错"而不是"没算完"；hyhawang 大量 stop=max_tokens、思考 16k 仍没答完。ikuncode sonnet-5 的 hard/xhard 单题平均 2–3 分钟，X8 直接空回复（out=1）。两站 X14（Fletcher-16）都错。

## 3. 稳定性 / 延迟（短问答流式 TTFT，秒）
| | 顺序 60 次 p50 / p90 / p99 / max | 错误 | 30 并发 ×2 波 p50 / p95 / p99 | 成功 |
|---|---|---|---|---|
| ikuncode opus-5 | 4.65 / 9.04 / **23.4** / 52.9 | 2 读超时(130 s)、1 断连、1 首字后挂住 | 9.9 / 38.1 / 38.3 | **34/60**（TLS 握手超时 / 连接重置 / 读超时） |
| ikuncode opus-5（走代理复测 10+60） | 2.31 / 5.43 / 8.86 / 8.86 | 0 | 6.0 / 10.2 / 18.0 | **32/60**（SSL EOF） |
| ikuncode sonnet-5 | 3.49 / 5.65 / 8.15 / 13.8 | 0 | 4.6 / 15.8 / 18.9（max 73.5） | 59/60 |
| hyhawang opus-5（011C 池） | 2.02–2.40 / 2.4–2.9 / 3.2–4.9 / 4.2–6.5 | 0 | 3.2–5.7 / 3.7–7.0 / 4.1–7.1 | 120/120 |
| hyhawang sonnet-5 | 1.93–2.33 / 2.4–3.4 / 3.4–4.5 / 5.5–6.7 | 0 | 2.9–5.5 / 4.1–6.2 / 4.2–6.5 | 120/120 |
- ikuncode 30 并发新建 TLS 连接两条出口都有约一半失败（hyhawang 同代理链路 60/60），是站点边缘的问题；bench 自带 12 并发（复用连接）12/12 成功但 p95 26–39 s、max 38–40 s（hyhawang 12 并发 p95 3.6–5.7 s）。
- soak 10 分钟（每 10 s 一次）：ikuncode opus 41 次 0 错，p50 6.0 s、p95 22.9 s、max 57.4 s（有一分钟只完成 1 次）；sonnet 51 次 0 错，p50 6.3 s、p95 18.9 s、max 38.1 s。hyhawang 四组 56–60 次 0 错，p50 3.0–3.9 s、p95 5.2–5.5 s。
- 吞吐：ikuncode 表现为**假流式**——TTFT 15–18 s 后 200–600 tok/s 一次性吐完（上游非流式，中转站攒够再发）；hyhawang 32–38 tok/s 真流式。2500 token 长输出两站都完整。
- ikuncode 无每分钟限速（2 req/s × 60 s 无 429）；hyhawang 100 RPM。
- ikuncode 同一请求 cache_creation 在 336/389/391/541 之间跳 → 至少 2–3 个 Kiro 账号/提示词版本轮询。

## 4. 计费侧（ikuncode，仅协议层观察）
"Reply with exactly: OK" 计 input 10 + cache_read 6083–6377 + cache_creation 336–541：Kiro 隐藏 prompt 约 6.5k 按缓存读计费（同 micuapi 模式，hyhawang 的 Kiro 池标为 excluded 不计费）。缓存/上下文本轮未测。

## 5. 缓存（12:05 补测；8.5k 前缀 system + cache_control，3 s 间隔；数据 `results/ikun-probes/cache-kiro-*.json`、`logs/ikun-kiro-ctxcache-*.log`）
| 项 | opus-5 | sonnet-5 |
|---|---|---|
| 顺序 12 次 | 12/12 都报 read 20134–20611 + write 1316–1751 + input 10，**第 1 次（不可能命中的新前缀）就报 read 20134** | 同：第 1 次 read 20338 |
| 换全新同长前缀（F） | 第 1 次 read 20760 | 第 1 次 read 20158 |
| 不带 cache_control（C） | 照样 read 20134–20611 | 照样 read 20371 |
| 多轮 6 轮（B） | read 20138–20601 恒定，不随历史增长 | 同 |
| 1h TTL（E） | 与 5m 无差别，`ephemeral_1h` 无此字段 | 同 |
| bench：空闲 5.5 min 后 | read 14792（不过期） | read 14718 |
| bench：新前缀隔离 | read 14827（FAIL） | read 14444（FAIL） |
| OpenAI /chat/completions | prompt 6723–6765、cached 6214–6377 → **8.5k 语料根本没被计入** | prompt 6482–6517、cached 6083–6116 |
| 命中降 TTFT | 否：首次 5.1 s，后续 3–6 s 抖动，无规律 | 否 |
**结论：ikuncode 的 cache_read 不是真实缓存计数，而是固定拆分规则**——不管前缀是否见过、有没有 cache_control、隔了多久，都把总量的一部分记成 read（小 prompt 时 read/(read+write+input) ≈ 92–94%；20k 自然文本首次请求 input 15402 + read 18461，read 占 54%）。write 在 1093/1316/1751 之间按账号跳。如果站点按这些数字计费，等于**永远以缓存价收约 92% 的输入**，实际是否命中无从验证（TTFT 不降）。对比：hyhawang 011C 池报 99.9%，但同样是模板估算；micuapi Kiro 池是真实先写后读、上限 85%。

## 6. 长上下文（合成随机词 needle = bench；自然文本 = 探针，`results/ikun-probes/needle_nat-kiro-*.json`）
| | 20k | 60k | 130k | 230k | 60k 系统规则 | 20 轮记忆 |
|---|---|---|---|---|---|---|
| opus-5 合成 | 3/3，6.7 s | 3/3，13.7 s | 3/3，16.0 s | **3/3，19.5 s**（usage.input 302437） | ✓ | ✗（上游空回复） |
| opus-5 自然文本 | 3/3，8.0 s | 3/3，7.0 s | 3/3，9.0 s | — | | |
| sonnet-5 合成 | 1/3 | 空 | 空 | 空 | 空 | ✓ |
| sonnet-5 自然文本 | 3/3，5.5 s | 3/3，6.0 s | 3/3，8.1 s | — | | |
- opus-5 名下 230k 合成文本 3/3 召回、input 按 1.325× 线性计数，**上下文真实到 230k**，是 1M 档模型（Opus 4.6/5 档一致）；hyhawang 230k 只回 200 空正文。
- sonnet-5 名下 ≥60k 合成随机词一律空回复（同 micuapi 的 Sonnet 4.5 护栏行为），自然文本 130k 3/3 正常，实际可用；230k 因合成空回复无法判断。
- **中转站会把上游空回复替换成一段中文文本** "⚠️ 上游模型未返回任何内容。可能原因：触发了安全策略、上游限流…" 作为 assistant 正文返回（status 200、end_turn）。程序会把它当成模型答案，写代理/Agent 时必须过滤。opus-5 的 20 轮多轮记忆测试就是这样"答错"的。
- 130k 自然文本 TTFT 7–8 s（Kiro 池吞吐正常）；hyhawang 011C 池 130k 只召回 2/3。
