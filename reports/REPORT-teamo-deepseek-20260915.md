# teamorouter.com DeepSeek 系列实测（2026-09-15，官方 key 同窗口对照）

站点：`https://api.teamorouter.com/v1`。对照：DeepSeek 官方 `https://api.deepseek.com`（官方当天只有两个模型 id：`deepseek-flash` = DeepSeek-V4.1-Flash，`deepseek-v4-pro` = DeepSeek-V4-Pro-0813；请求 `deepseek-v4-flash` 会被官方映射到 `deepseek-flash`）。官方 key 余额只有 ¥3.10，所以官方基准按预算裁剪：flash 跑 quick 全组 + hard/xhard 补测，v4-pro 只跑协议/身份/知识/分词/缓存/速度 + 8 道 screen 题，全程花了 ¥1.80。
原始数据：`results/ds-official-*`、`results/teamo-deepseek-*`、`results/ops/`、`logs/teamo-ds-*.log`、`logs/ops-ds-*.log`。

## 结论

teamorouter 上四个 deepseek 名字对应三个完全不同的上游：

| 中转模型名 | 上游 | 实际模型 | 判定 |
|---|---|---|---|
| `deepseek-flash` | **DeepSeek 官方 API 原样透传**（uuid id、`system_fingerprint`、`prompt_cache_hit/miss_tokens`、模板 35 token、报错原文一致） | DeepSeek-V4.1-Flash（与官方当前同款） | ✅ 真，速度接近官方 |
| `deepseek-v4-flash` | 第三方托管（火山方舟格式：id `02+时间戳`、model 回显 `deepseek-v4-flash-ga-260731`、`service_tier`；约 4 成请求再经一层 LiteLLM，回显 `deepseek-v4-flash-0731`、带 `provider_specific_fields`） | **DeepSeek-V4-Flash 0731 老版本**，不是官方现在 `deepseek-v4-flash` 名字对应的 V4.1-Flash | ⚠️ 名字对不上：思考模式智力持平，关思考明显更弱，知识更旧 |
| `deepseek-v4-pro` | 第三方托管（同上火山方舟格式，回显 `deepseek-v4-pro-ga-260813`） | DeepSeek-V4-Pro-0813，与官方同一版本 | 🟡 同版本、非官方直连；吞吐只有官方的 1/3 |
| `deepseek-v4-pro-260425` | 同上，回显 `deepseek-v4-pro-260425`（6/10）与 `-ga-260813`（4/10）混发 | 两个 Pro 版本混合 | ⚠️ 混池，未深测 |

## 1. 上游指纹（每个名字 10 次 "Reply with exactly: OK"）

| 项目 | 官方 flash | 官方 v4-pro | 中转 deepseek-flash | 中转 deepseek-v4-flash | 中转 deepseek-v4-pro |
|---|---|---|---|---|---|
| 响应 id | uuid | uuid | uuid（10/10） | `02+时间戳+hex`（6/10）/ `chatcmpl-uuid`（4/10） | `02+时间戳+hex`（10/10） |
| model 回显 | deepseek-flash | deepseek-v4-pro | deepseek-flash | `deepseek-v4-flash-ga-260731` / `deepseek-v4-flash-0731` | `deepseek-v4-pro-ga-260813` |
| `system_fingerprint` / `prompt_cache_hit_tokens` | 有 | 有 | 有（10/10） | 无 | 无 |
| `service_tier` / `provider_specific_fields` | 无 | 无 | 无 | 有 / 有（LiteLLM 那 4 次） | 有 / 无 |
| 该请求 prompt_tokens | 35 | 88 | 35 | 88 | 88 |
| 分词增量（英 +1261 o200k / 中 +2040 o200k） | 1647 / 1570 | 1647 / 1570 | 1647 / 1570 | 1647 / 1570 | 1647 / 1570 |
| `max_tokens=999999` | 400「[1, 393216]」 | 同 | 400（中转改写成「The request could not be completed」） | 200 | 200 |
| `max_completion_tokens` | 忽略（只认 `max_tokens`） | 同 | 忽略 | **生效**（截断到 3 token） | **生效** |
| `thinking: disabled` / `reasoning_effort: none` | 生效，模板变 9 token | 同 | 生效 | 生效（9 token） | 生效（9 token） |
| 缓存 | 账号内命中（`prompt_cache_hit_tokens`） | 同 | 账号内命中；**与官方 key 不互通**（DeepSeek 缓存按账号隔离，官方↔中转双向 0 命中，对判定不构成证据） | `cached_tokens` 2048 块命中（第 3 次起） | 同 |
| 自报厂商 | deepseek | deepseek | deepseek | deepseek | deepseek |

补充：中转 deepseek-flash 的 `thinking: enabled` / `reasoning_effort: high` 都原样生效，思考长度与官方同量级；官方与中转对 `stop` 序列都生效。

## 2. 智力（suite/iq_full.json，思考开=默认；关=reasoning_effort none）

| 档 | 官方 flash | 中转 deepseek-flash | 中转 deepseek-v4-flash | 中转 deepseek-v4-pro | 官方 v4-pro |
|---|---|---|---|---|---|
| reason 12 题（思考开） | 12/12 | 12/12 | 12/12 | 12/12 | screen 8 题 8/8 |
| hard 6 题（思考开） | 5/5 | 5/5 | 6/6 | 6/6 | – |
| xhard 14 题（思考开） | 13/13 | 11/11 | 14/14 | 14/14 | – |
| 全部（思考开，答出题） | 30/30，2 题超 16k 输出被截 | 28/28，4 题截断 | 32/32 | 32/32 | – |
| 全部（**关思考**，严格 / 宽松计分） | 未测（预算） | 28/32 | 16/32 / **21/32** | 18/32 / **22/32** | – |
| screen 8 题（R7 R10 R3 R4 R9 H2 H3 X14） | 8/8 | 8/8 | 8/8 | 8/8 | 8/8 |

宽松计分是把 `3**`、`\frac{a}{b}`、`3E9D` 对 `0x3E9D` 这类格式差异算对，剩下的才是真错。关思考时中转 deepseek-flash（V4.1-Flash）几乎不掉分，而 V4-Flash-0731 和 V4-Pro 都掉到七成左右，这是版本差异，不是中转做了手脚（同样的老模型在官方已经下线，没法直接对照）。

## 3. 知识

| 项目 | 官方 flash | 中转 deepseek-flash | 中转 deepseek-v4-flash | 中转 deepseek-v4-pro | 官方 v4-pro |
|---|---|---|---|---|---|
| 知识阶梯前沿 | 2025-11 | 2025-11 | **无**（阶梯题全 UNKNOWN） | 2025-05 | 2025-05 |
| 开放式近期前沿 | 2025-02 | 2024-10 | 2024-10 | 2025-02 | 2024-10 |
| 同题 4 次年代一致 | 混合（教宗题，官方自己就摇摆） | 混合 | – | – | – |

中转 deepseek-v4-pro 与官方 v4-pro 的知识墙同为 2025-05，支持"同一版本"的判断；deepseek-v4-flash 比 V4.1-Flash 旧。

## 4. 协议与长上下文

| 项目 | 官方 flash | 中转 deepseek-flash | 中转 deepseek-v4-flash | 中转 deepseek-v4-pro |
|---|---|---|---|---|
| 默认思考 | 是 | 是 | 是 | 是 |
| 流式 | 逐 token、reasoning 在前、无 obfuscation | 同 | 同 | 同 |
| 20k / 60k / 130k 三针 | 3/3（20k 1.1 s；quick 未测 60k+） | 3/3 / 3/3 / 3/3（2.4 / 2.8 / 4.5 s） | 3/3 / 3/3 / 3/3（3.0 / 4.4 / 9.1 s） | 3/3 / 3/3 / 3/3（3.5 / 4.6 / 5.8 s） |
| 20 轮记忆 / 60k 下 system 规则 | 通过 | 通过 | 通过 | 通过 |
| 5k 前缀缓存 | 第 2 次命中 | 第 2 次命中 | 命中 | 命中 |
| 顺序 8 次 / 8 并发 | 0 错 p50 0.63 s / – | 0 错 p50 1.18 s / 8/8 p50 3.0 s | 0 错 1.58 s / 8/8 3.61 s | 0 错 1.73 s / 8/8 4.45 s |
| model 回显漂移 | 无 | 无 | **有**（两个回显名混发） | 无 |
| 套件误报 | vendor_mismatch、tokenizer/differential 在官方上同样 FAIL（套件预期 o200k/openai），不算证据 | 同 | 同 | 同 |

## 5. 运营指标：deepseek-flash 官方 vs 中转（ops.py 同窗口交错，07:12–07:31）

| 指标 | 中转 deepseek-flash | 官方 flash |
|---|---|---|
| 短请求 30 轮：错误 / 空回复 | 0 / 0 | 0 / 0 |
| 短请求 p50 / p95 / max | 1.26 / 1.72 / 3.0 s | 1.02 / 1.46 / 2.73 s |
| 流式吞吐 p50 | 152 tok/s | 137 tok/s |
| 流式 TTFB p50 | 3.11 s | 2.45 s |
| 默认思考写代码：首个正文 / 总耗时 / 思考 token | 30.7 s / 32.4 s / 7730 | 26.6 s / 28.3 s / 7046 |
| 8 并发 p50 / 16 并发 p50 / req/s | 3.25 / 3.06 s / 4.52 | 3.23 / 2.15 s / 4.71 |
| 20k 缓存第 2 次命中 | 0.991 | 0.988 |
| 缓存 TTL +60/180/300/600 s | 全部命中 | +60 s 未命中，其余命中 |
| 多轮前缀缓存 | 覆盖 / 记忆正确 | 同 |

bench.py 单独测的速度：TTFT 1.43 s vs 0.52 s，吞吐 126 vs 130 tok/s。中转 deepseek-flash 比官方只多约 0.3–0.9 s 的转发延迟，吞吐持平。

## 6. 运营指标：中转 deepseek-v4-flash / deepseek-v4-pro（无官方同款可对照）

bench.py 数据：v4-flash TTFT 2.07 s、吞吐 139 tok/s（区间 89–156）；v4-pro TTFT 1.88 s、**吞吐 43.8 tok/s**（官方 v4-pro 未测吞吐，但官方 flash 137 tok/s、中转 flash 152 tok/s 可作参照）。ops.py 同类结果：

| 指标（ops.py，07:32–07:47，两条同时跑） | 中转 deepseek-v4-flash | 中转 deepseek-v4-pro | 参照：中转 deepseek-flash（官方透传） |
|---|---|---|---|
| 短请求 30 轮：错误 / 空回复 | 0 / 0 | 0 / 0 | 0 / 0 |
| 短请求 p50 / p95 / max | 1.67 / 2.06 / 3.08 s | 1.65 / 2.10 / 3.60 s | 1.26 / 1.72 / 3.0 s |
| 流式吞吐 p50（区间） | 86 tok/s（86–167） | **44 tok/s**（43–52） | 152 tok/s |
| 流式 TTFB p50 | 1.58 s | 1.68 s | 3.11 s |
| 默认思考写代码：首个正文 / 总耗时 / 思考 token | 39.2 s / 43.4 s / 5690 | **70.7 s / 77.2 s** / 5341 | 30.7 s / 32.4 s / 7730 |
| 20k 缓存命中（第几次） / 命中占比 | 第 3 次 / 0.992 | 第 2 次 / 0.992 | 第 2 次 / 0.991 |
| 缓存 TTL +60/180/300/600 s | 命中（+180 s 只命中 18432/20126） | 命中（+180/+300 s 18432/20130） | 全部命中 |

两条第三方池的转发延迟本身不高（TTFB 1.6 s，比官方透传的 3.1 s 还快），差在生成速度：v4-flash 86 tok/s 波动大（单次可到 167），v4-pro 只有 44 tok/s，同一道写代码题总耗时是 flash 的 2.4 倍。

## 7. 其他

- 官方 key 余额：开始 ¥3.10，结束 ¥1.30；其中 IQ 补测 ¥1.49、其余 ¥0.31。
- 官方计费（高峰价）：flash 输入 $0.30 / 输出 $1.20 每百万，v4-pro $1.32 / $3.96；低谷（UTC 16:30–00:30）半价。中转价格公开页未列，未核实。
- 中转 deepseek-flash 的 `/v1/responses` 允许篡改 `encrypted_content` 后仍 200（官方同样不校验，非中转问题）。
- 官方 v4-pro 被问"之前有什么指令"时会编造一段 Anthropic/Claude 系统提示，中转 v4-pro 同样，这是模型本身的幻觉。
- 本机到 teamorouter 必须走代理，经 Clash 偶发 SSL EOF，与站点无关。

## 8. 使用建议

- 要 DeepSeek 官方同款且便宜：用 `deepseek-flash`。
- `deepseek-v4-flash` 不是官方现在这个名字对应的模型，是下线前的 V4-Flash 0731；如果你的用法依赖关思考模式，它明显更弱。
- `deepseek-v4-pro` 版本与官方相同，但吞吐约 44 tok/s，长回复会慢 3 倍。
- 避免 `deepseek-v4-pro-260425`，两个版本混发。
