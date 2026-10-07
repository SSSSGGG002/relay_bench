# 远桥云 yuanqiaoyun.com GLM / DeepSeek 分组实测（2026-09-16）

两把 key：GLM 分组（`glm`，无限额度）与 DeepSeek 分组（`ds`，无限额度）。

## 0. 先说没测到的

- **`glm-5.3-flash` 这把 key 调不到。** 分组 GLM 下只有 `glm-5.2`、`glm-5.3` 两个渠道，请求 `glm-5.3-flash`（含各种大小写/别名）一律 `分组 GLM 下模型 glm-5.3-flash 无可用渠道`。站内目录（`/api/pricing`）显示 `glm-5.3-flash` 只挂在「国模」分组（倍率 0.4，补全 3.5）。
- **DeepSeek V4.1（`DeepSeek-V4.1-Flash`）同样只在「国模」分组**（倍率 37.5？目录如此标注），DeepSeek 分组只有一个渠道 `deepseek-v4-flash-0731`。`deepseek-flash` / `deepseek-v4-flash` / `deepseek-v4.1-flash` 等名字全部无渠道。
- 因此本轮只完整测了 **`deepseek-v4-flash-0731`**；glm-5.3 / glm-5.2 按要求中止（中止前拿到的指纹放在附录，供参考）。要测 glm-5.3-flash 与 V4.1 需要「国模」分组的 key。

## 1. `deepseek-v4-flash-0731`（DeepSeek 分组）

对照：teamorouter 的 `deepseek-v4-flash`（同一个 0731 版本，火山方舟/LiteLLM 池，09-15 实测）和 DeepSeek 官方 `deepseek-flash`（V4.1-Flash，09-15 基准）。官方已不再提供 0731 版本，无法直连对照。

### 1.1 指纹

| 项目 | 远桥云 0731 | teamorouter v4-flash（0731） | 官方 V4.1 flash |
|---|---|---|---|
| 响应 id | `chatcmpl-<uuid>`（20/20） | `02+时间戳`（6/10）/ `chatcmpl-uuid`（4/10） | uuid |
| model 回显 | `deepseek-v4-flash-0731` | `-ga-260731` / `-0731` | deepseek-flash |
| `system_fingerprint` / `prompt_cache_hit_tokens` | 无 | 无 | 有 |
| "Reply with exactly: OK" prompt_tokens | 88 | 88 | 35 |
| 分词增量（英 / 中，bench） | 1647 / 1570 | 1647 / 1570 | 1647 / 1570 |
| 默认思考 | 是 | 是 | 是 |
| `thinking: disabled` / `effort: none` | 生效，模板 9 token | 同 | 同 |
| `max_tokens=999999` | 200（官方 400） | 200 | 400 |
| `temperature=5` | 400「[0.0, 2.0]」（官方接受到 2） | – | – |
| 工具 id | `call_` + 24 hex | 同 | – |
| 自报厂商（4 次） | Anthropic / DeepSeek / OpenAI / DeepSeek（模型幻觉） | – | deepseek |
| 隐藏提示注入 | 无（3/3 NONE，4/4 答 No） | 无 | – |
| 缓存 | `cached_tokens` 命中（第 2 次 0.965） | 命中 | 账号内命中 |

远桥云这条与 teamorouter 那 4 成走 LiteLLM 的子池同一形态（`chatcmpl-` id、`-0731` 回显、tokenizer 相同），大概率是同一家第三方托管的 DeepSeek-V4-Flash 0731。

### 1.2 智力（suite/iq_full.json）

| | 远桥云 0731 | teamorouter 0731 | teamorouter deepseek-flash（V4.1 官方透传） | 官方 V4.1 |
|---|---|---|---|---|
| 思考开（答出题） | 30/31，2 题空回复（X8、X13） | 32/32 | 28/28，4 题截断 | 30/30 |
| 关思考（严格 / 宽松） | 19/33 / 19/33 | 16/32 / 21/32 | 28/32 | 未测 |
| 知识阶梯 / 开放式前沿 | 无 / 2024-10 | 无 / 2024-10 | 2025-11 / 2024-10 | 2025-11 / 2025-02 |

同 teamorouter 的 0731 一致：思考开时与 V4.1 持平，关思考掉到六成，知识比 V4.1 旧。这是版本差异，不是站点动手脚。

### 1.3 速度与稳定性（ops.py，11:05–11:30；bench 另一时段）

| 指标 | 远桥云 0731 | teamorouter 0731 | 官方 V4.1（09-15） |
|---|---|---|---|
| 短请求 30 轮：错误 / 空回复 | 0 / 0 | 0 / 0 | 0 / 0 |
| 短请求 p50 / p95 / max | 1.82 / 2.20 / 3.37 s | 1.67 / 2.06 / 3.08 s | 1.02 / 1.46 / 2.73 s |
| 流式吞吐 p50（区间） | 73 tok/s（67–77） | 86 tok/s（86–167） | 137 tok/s |
| 流式 TTFB | 1.76 s | 1.58 s | 2.45 s |
| 流式粒度 | **4.3 tok/chunk**（缓冲后切块） | 1.0 | 1.0 |
| 默认思考写代码：首个正文 / 总耗时 | 28.3 / 33.4 s（3 次只 1 次有效） | 39.2 / 43.4 s | 26.6 / 28.3 s |
| 8 并发（bench） | 8/8，p50 3.8 s | 8/8，3.61 s | – |
| 20k / 60k / 130k 三针 | 3/3 全过，耗时 7.3 / 15.3 / 14.1 s | 3/3，3.0 / 4.4 / 9.1 s | 20k 1.1 s |
| 20k 缓存第 2 次命中 / TTL | 0.965 / +60 s 命中，之后渠道故障无法测 | 0.992 / 全命中 | 0.988 / +60 s 未命中，其余命中 |
| 多轮前缀缓存 | 轮 2 只命中 5120/6116（部分） | 覆盖 | 覆盖 |

### 1.4 渠道故障（本地 11:10 起）

ops 跑到缓存 TTL 阶段时（站点时间约 11:10），DeepSeek 分组开始**每次 HTTP 500**：`upstream error: do request failed (code do_request_failed)`，是 new-api 打上游失败，不是 key 问题（同站 GLM 分组同时 200，key 额度仍为无限）。11:19 复查 5/5 仍 500，之后每 30 s 监测一次，恢复时间见文末补记。此前 bench 171 次 + ops 30 轮 + 8/16 并发全部 0 错误，故障是突然整体断掉，不是零星错误。

结论：模型真是 DeepSeek V4-Flash 0731；正常时段 0 错误，但吞吐只有官方 V4.1 的一半，流式是 4 token 一块的缓冲流，长上下文慢 2–5 倍，关思考模式明显弱于 V4.1，而且测试当天上游整体断了一次（持续时间见补记）。

## 附录：中止前的 glm-5.3 / glm-5.2 指纹（GLM 分组，未按要求继续）

- `glm-5.3`：20/20 智谱官方格式 id + `request_id`，`thinking disabled` / `effort none` 返回智谱原文 400 code 1210，`max_tokens=999999` 400「[1,131072]」，工具 id `call_-int64`，分词增量与官方逐位一致；**与官方 key 缓存互通**（官方写入→中转 6/8 命中 3712）；单次请求耗时 5–6 s，官方 1.5–2 s。Anthropic 口是 new-api 转换：无 thinking 块、无签名、count_tokens 404、顺序 5 次全空回复。
- `glm-5.2`：火山方舟托管（id `02+时间戳`，回显 `glm-5-2-260617`，`service_tier`），无缓存命中，39 tok/s，`temperature=5` 被方舟 400。


## 补记：DeepSeek 分组故障时间线（站点时间）

- 11:10 起全部 500 `do_request_failed`（ops TTL +180 s 探针首次撞上）。
- 11:19 复查 5/5 仍 500；11:20 500 → 11:21 变 400 → 11:22 变 404（像是在换渠道）→ **11:27 恢复 200**，中断约 17 分钟。
- 恢复后 6 次复查：6/6 200，`chatcmpl-` id、回显 `deepseek-v4-flash-0731`、prompt_tokens 88、耗时 3.6–4.0 s，与故障前同一上游。
