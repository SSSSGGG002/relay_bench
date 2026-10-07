# teamorouter.com glm-5.3-flash 实测（2026-09-15，官方 key 同窗口对照）

站点：`https://api.teamorouter.com/v1`（与 `https://teamorouter.com/v1` 同一网关：同 nginx、同 `x-trace-id`、同两个后端池，只是 EdgeOne 解析到不同节点）。
对照：智谱官方 `https://open.bigmodel.cn/api/paas/v4` 与 `/api/anthropic`，同一天同一窗口用官方 key 重跑了全量基准（`results/zhipu-official-0915`、`results/zhipu-official-anthropic-0915`）。
原始数据：`results/teamo-glm`、`results/teamo-glm-anthropic`、`results/ops/teamo-glm.json`、`results/greedy/`、`logs/teamo-*.log`。

## 结论

1. **模型是真的智谱 glm-5.3-flash。** 决定性证据是跨账号缓存互通：用官方 key 写入的 6.4k token 文档，中转两个池的请求都命中了（`cached_tokens` 6336 / 6400）；反过来中转写入的文档，官方 key 第一次读就命中 4352。智谱隐式缓存全局共享，只有同一后端才会互相命中。分词增量、知识前沿、贪心自洽度、精度题、200k 十针也都和官方一致。
2. **但它是双池混合，约 30% 的请求默认不思考。** 一个池是官方 OpenAI 口原样透传；另一个池（响应 id 是 32 位 hex）走的是另一条智谱接入面，默认思考几乎为零，`reasoning_effort` 被忽略，必须显式传 `thinking: {"type": "enabled"}` 才会思考。写代码这类默认靠思考的任务，落到这个池时质量会掉。
3. **速度全面慢于官方，稳定性正常。** 首字 3–6 s（官方 0.7–3 s），短请求 p50 慢 0.7–1.7 s，长上下文慢 2–5 倍，吞吐持平（59 tok/s）。同窗口 30 轮无错误，8/16 并发无错误，缓存命中和 TTL 与官方一致。
4. **Anthropic 口（`/v1/messages`）也是官方透传**，签名、usage、缓存与官方一致，只是 count_tokens 404、关思考/xhigh 不报错。

## 1. 两个后端池

| 项目 | 池 A：`2026091516…`（14 位时间戳+16 hex） | 池 B：32 位 hex id | 官方 paas |
|---|---|---|---|
| 占比（80 分钟每 20 s 采样） | 61/83（root 域名）、59/86（api 域名） | 22/83、26/86 | – |
| 顶层字段 | 含 `request_id`，与官方逐字段相同 | 无 `request_id`；usage 多出 `cost`、`input_tokens`、`claude_cache_creation_5_m_tokens` 等 | 含 `request_id` |
| "Reply with exactly: OK" 的 prompt_tokens | 17 | 8（比官方少 9 个模板 token，所有文本的增量与官方逐位相同） | 17 |
| reasoning_tokens | 正常上报 | 永远 0，`total_tokens ≠ prompt+completion` | 正常 |
| 默认思考（写代码题，思考字符数中位） | 3,749 | **74** | 5,232 |
| `reasoning_effort=max` | 思考 4.6k–6.8k 字符（同官方） | 17–30 字符（被忽略） | 5k–6.7k |
| `thinking: {"type":"enabled"}` | 5.8k–6.4k | **2.6k–6.3k（恢复正常思考）** | – |
| `thinking: {"type":"disabled"}` / `effort=none` / `max_tokens=999999` | 从未落到此池 | 全部 200（13/13） | 400 code 1210 |
| 同步 tool_call id | `call_-7262549282446638499`（官方 OpenAI 口格式） | `call_679076b3e06043fd94ce6f55`（官方 Anthropic 口 / 流式格式） | `call_-<int64>` |
| 跨账号缓存（官方写→此池读） | 命中 6336 | 命中 6400（3/4 次样本） | – |
| 按池 IQ（iq_full 26 题 × 2 轮，默认模式） | 38/45 | 16/19 | 当天官方 23/24 |
| 单次 OK 请求耗时均值（采样期） | 6.0 s | 9.4–13.3 s | 官方 p50 2.2 s |

判断：池 B 同样是智谱官方后端（缓存互通、分词一致、知识与精度一致），大概率是中转把请求转成 Anthropic 格式打到智谱的 Anthropic 接入面再转回 OpenAI 格式：工具 id 格式、`thinking` 参数生效而 `reasoning_effort` 失效、缺 9 个模板 token、reasoning_tokens 填 0，都符合这个转换层的特征。官方会拒绝的参数（关思考、effort=none、max_tokens 超限）100% 从池 B 返回 200，像是「先打官方、被 400 后回退到池 B」的策略。

**对使用者的实际影响：** 不带参数直接调用时，约三成请求拿到的是几乎不思考的 glm-5.3-flash（相当于官方 `reasoning_effort=high/low` 的输出量）。需要思考质量时，在请求里加 `"thinking": {"type": "enabled"}`，两个池都会正常思考；或者改走 `/v1/messages` Anthropic 口（透传官方）。

补充说明：官方 glm-5.3-flash 本身 `reasoning_effort=high` 只思考 17–38 字符，`low` 为 0，默认才是完整思考（当天实测），所以中转上 `effort=high` 不思考不是中转的问题。

## 2. 协议指纹（bench.py protocol / passthrough 组）

| 项目 | 中转 OpenAI 口 | 官方 paas | 中转 Anthropic 口 | 官方 anthropic |
|---|---|---|---|---|
| 响应 id | 池 A 官方格式 / 池 B 32 hex | 14 位时间戳+16 hex | `msg_` + 官方格式 | 同 |
| 模型名回显 | glm-5.3-flash | 同 | 同 | 同 |
| 参数校验一致率 | 9/12（关思考、effort none/invalid 不报错） | – | 8/10（disabled_xhigh、effort_xhigh 不报错） | – |
| `max_tokens=999999` | 200（官方 400「[1,131072]」） | 400 | 200 | 400 |
| `stop` 序列 | 不生效（官方当天同样不生效，不算差异） | 不生效 | 同 | 同 |
| `/tokenizer` | 404 | 200 | – | – |
| `count_tokens` | – | – | 404 | 200 |
| 分词增量（英 +1261 o200k / 中 +2040 o200k） | 1720 / 1601 | 1720 / 1610 | 一致 | – |
| thinking 签名 | – | – | 24 hex（同官方，官方本身不校验） | 24 hex |
| 流式 | 真流式，1 tok/chunk，reasoning 在前、usage 在末块，无 obfuscation | 同 | 有 ping 事件 | 同 |
| 隐藏提示注入 | 无（trivial 请求 8–17 token） | 17 | 无 | – |
| 自报厂商 | Z.ai | Z.ai | Z.ai | Z.ai |
| 请求不存在的模型名 | 400 `model_not_available: temporarily unavailable. Please retry`（中转自己的错误） | 400 code 1211 | – | – |

## 3. 智力与知识

| 项目 | 中转 OpenAI 口 | 官方 paas（当天） | 中转 Anthropic 口 | 官方 anthropic（当天） |
|---|---|---|---|---|
| reason（12 题，思考开） | 10/12 | 12/12 | 11/12 | 12/12 |
| hard（6 题） | 4/6 | 5/6 | 5/6 | 5/6 |
| xhard | 12/13 | 6/6 | 14/14 | 3/3 |
| reason / hard / xhard（关思考） | 7/12、4/5、8/12 | 9/12、6/6、3/8 | 11/12、5/6、7/13 | 8/12、4/6、2/4 |
| 知识阶梯前沿 | 2025-12 | 2025-12 | 2025-12 | 2025-11 |
| 逐题分类一致 | 22/24 | – | 19/24 | – |
| 同题 4 次年代一致 | 混合（教宗题） | 官方自己也混合 | 混合 | 官方自己也混合 |
| 贪心自洽度（greedy.py） | 0.205 | 0.21 | – | – |
| 精度题 | 12/20 | 13/20 | – | – |
| 200k 十针 | 10/10（48 s） | 10/10（10 s） | – | – |

差异都在抽样噪声内（官方 glm-5.3-flash 即使 do_sample=false 也不确定，自洽度只有 0.21）。xhard 分母不同是因为空回复/故障题不计入。

## 4. 运营指标（ops.py，同窗口交错采样 05:05–05:25）

| 指标 | teamorouter | 官方 paas |
|---|---|---|
| 短请求 30 轮：错误 / 空回复 | 0 / 1 | 0 / 1 |
| 短请求 p50 / p90 / p95 / max | 2.96 / 7.86 / 9.92 / 10.28 s | 2.21 / 6.2 / 7.59 / 11.25 s |
| 流式吞吐 p50（区间） | 58.9 tok/s（54.6–64.9） | 59.1 tok/s（44.8–63.9） |
| 流式 TTFB p50 | 6.42 s | 3.27 s |
| 默认思考写代码：首个正文 token / 总耗时 / 思考 token | 6.3 s / 14.5 s / 无（这 3 次落在池 B） | 33.7 s / 38.2 s / 3342 |
| 8 并发：错误 / p50 / max | 0 / 4.25 / 5.56 s | 0 / 3.47 / 10.06 s |
| 16 并发：错误 / p50 / max / req/s | 0 / 4.58 / 6.94 s / 2.3 | 0 / 3.89 / 8.32 s / 1.92 |
| 20k 前缀缓存：第 2 次命中占比 | 0.997 | 0.997 |
| 缓存 TTL +60/180/300/600 s | 全部命中 | +60 s 未命中，其余命中 |
| 多轮前缀缓存覆盖 / 记忆 | 是 / 正确 | 是 / 正确 |

bench.py 里的同类数据（不同时段）：TTFT 3.19 s vs 0.73 s；顺序 8 次 p50 2.81 s vs 1.14 s；8 并发 p50 5.3 s vs 1.4 s；长上下文 20k/60k/130k/230k 三针全部 3/3，但耗时 5.7/17.4/9.1/20.0 s 对官方 1.5/3.5/4.4/6.0 s。

## 5. 缓存互通（决定性证据）

| 探针 | 结果 |
|---|---|
| 官方写 6.4k 文档 ×2（第 2 次命中 6336）→ 中转读 ×12 | 池 A 8/9 命中 6336；池 B 2/3 命中 6400 |
| 中转写 4.4k 文档（首次 0）→ 后续中转 5 次 | 池 A 2/4 命中、池 B 1/1 命中 |
| 同一文档官方首次读 | 命中 4352（官方读到了中转写入的缓存） |
| xcache.py（4.1k 前缀） | 官方→中转：未命中（1 次样本，落池 B）；中转→官方：命中 4096；中转自身：第 2 次命中 4096 |

未命中的个别样本与智谱缓存的异步写入延迟一致（官方 xcache [A] 自己第 2 次也偶发 0）。

## 6. 其他

- **网络**：域名走腾讯 EdgeOne（43.159.x.x），本机直连被 reset，必须经代理；经本机 Clash 出现约 3–10% 的 `SSL: UNEXPECTED_EOF`，同一代理打 bigmodel.cn 也有 1/24，直连 0/24，属于本机代理路径的问题，不计入站点稳定性。
- **`glm-5.3-flash-free`**：当天额度已用尽（402，太平洋时间 9:00 重置），未测。
- **计费**：公开页面只列了 glm-5.2（$1.40 / $4.40 每百万），glm-5.3-flash 未列出；池 B 响应里的 `usage.cost`（约 1e-5 美元/次）与 token 数对不上任何单价，没有可用的账单接口（/api/user/self 403），本次无法核实实际扣费。
- **停用的旧 key**：`sk-teamo-5aa2…` 在所有域名和两种鉴权头上都返回 401「此 API Key 已被停用」。

## 7. 方法学备注

- 判定不依赖自报身份和知识题：官方 glm-5.3-flash 自身 pool_mix、stop 序列、隐藏提示泄露这三项在当天官方基准上同样 FAIL/WARN，compare.py 自动给出的「❌ 模型身份不一致」是误报，主要由池 B 的默认不思考、reasoning_tokens=0、usage 字段差异触发。
- `ops.py` / `xcache.py` 的 `--ch` base 不能带 `/v1`（脚本自己拼 `/v1/chat/completions`），带了会 404。
- 每个响应先按 id 格式分池再统计，混合池的平均值没有意义。
