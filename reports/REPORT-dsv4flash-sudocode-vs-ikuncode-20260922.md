# sudocode.chat vs api.ikuncode.cc：`deepseek-v4-flash` 对比（2026-09-22）

范围按要求只做三项：速度、缓存、智力，不做并发压测。两站各跑：指纹/协议探针（scratchpad）、`ops.py --only latency,speed,cache`（20 轮短请求、5 次流式、3 次默认思考写代码、20k 前缀缓存 + TTL + 多轮）、`bench.py --profile quick --iq-nothink`（协议/身份/知识/分词/20k 上下文/5k 缓存/顺序稳定性/吞吐 + reason 12 题）、再补 hard 7 + xhard 14 题两种模式。原始数据：`results/ikun-dsv4f*`、`results/sudo-dsv4f*`、`results/ops/{ikun,sudo}-dsv4f.json`、`OPS-{ikun,sudo}-dsv4f-0922.md`、`logs/*ikun-dsv4f*`、`logs/*sudo-dsv4f*`。

测试环境说明：sudocode 从这台 Mac 必须走 Clash 代理（直连不通），ikuncode 直连可达；两边脚本都复用长连接，握手开销不计入；但 sudocode 的每次请求仍多一跳代理，短请求延迟对它略不利。sudocode 这把 key 开测时余额为 ¥0（三个 deepseek 名字全部 `insufficient_user_quota`），约 11:26 恢复后才开跑；跑完主测试、复测到第 2 轮 X4 时又归零（¥-0.02，站点 usage 计 237.6），第 3 轮复测作废。另一会话同一天上午在这把 key 上测 fable-5-1 花掉约 $9.6，是第一次归零的原因。

## 结论

1. **两家卖的是同一个东西**：火山方舟托管的 **DeepSeek-V4-Flash 0731 老版本**（sudocode 直接回显 `deepseek-v4-flash-ga-260731`，与 09-15 在 teamorouter 测到的第三方池同款），都不是 DeepSeek 官方现在 `deepseek-v4-flash` 对应的 V4.1-Flash。同源证据：模板 token 都是思考 88 / 关思考 9（官方 35 / 9）；分词增量英 1647 / 中 1570 完全一致；知识阶梯从 K01 起全 UNKNOWN、开放式前沿 2024-10~2025-02；`max_completion_tokens` 都生效、`max_tokens=999999` 都 200（官方 400）；关思考时错的题高度重合（R2、X3 格式、H4、H7、X7、X8、X12、X13）。
2. **速度 sudocode 明显快**：流式吞吐 83 vs 38 tok/s，默认思考写代码出正文 29 s vs 184 s，33 道 IQ 题平均耗时 50 s vs 116 s（思考开）。ikuncode 的 `router-` 网关这一层慢了一倍多。短请求延迟两家持平（p50 2.0 vs 1.8 s）。
3. **缓存两家都有、都不省时间**：20k 前缀第 2 次即命中 99%，多轮对话第 2 轮覆盖第 1 轮全部输入；TTL 上 ikuncode 到 600 s 仍全量命中，sudocode 180 s 后掉到 91%（18432/20184）仍算命中。命中后 TTFT 反而慢 30% 左右（火山方舟本身如此）。两站都没公开价格页，缓存折扣比例无法核实，`cached_tokens` 字段两家都正常回传。
4. **智力：带思考完全同一水平，关思考 ikuncode 略高**。思考开第 1 轮 32/33 vs 30/33，复测后两轮取最好两家都 33/33，差异是抽样波动。关思考两轮合计 ikuncode 61% vs sudocode 49%，R3/H2 等题 ikun 两轮都对、sudo 两轮都错，疑似网关采样参数不同（未能验证，sudocode key 耗尽）。关思考掉到五六成本身是 V4-Flash-0731 这个版本的特性（09-15 teamorouter 同款 21/32），不是中转做手脚。另外 sudocode 思考模式不受 max_tokens 约束（单题输出到 71k token），长思考题更烧钱。
5. **协议差别**：sudocode 是火山方舟原样透传（`02+时间戳` id、`service_tier`、usage 带 `reasoning_tokens`、方舟原文报错）；ikuncode 套了一层 `router-` 网关：重写 id、抹掉 `-ga-260731` 回显、usage 丢掉 `completion_tokens_details`（拿不到思考 token 数）、`temperature=5` 上游挂死到 524（sudocode 立即 400）、约 2% 请求落到一个 DeepSeek 官方格式的备用渠道（uuid id、`prompt_cache_hit_tokens`）。

选哪家：同模型、同缓存，**sudocode 快一倍**；ikuncode 的优势只剩本地直连不用代理和缓存 TTL 更长。sudocode 另有 `deepseek-v4-1-flash` 名字（本次未测），如果那是 V4.1-Flash 就比这两个 0731 都新。

## 1. 上游指纹

| 项目 | sudocode | ikuncode | 官方 DeepSeek（09-15 记录） |
|---|---|---|---|
| 响应 id | `02` + 时间戳 + hex（30/30 + 24/24） | `router-` + 32 hex（30/30 + 24/24；全程约 2% uuid 备用池） | uuid |
| model 回显 | `deepseek-v4-flash-ga-260731` | `deepseek-v4-flash` | `deepseek-flash` |
| 顶层字段 | `service_tier=default`，无 `system_fingerprint` | 无 `service_tier`，无 `system_fingerprint` | 有 `system_fingerprint` |
| usage | `prompt_tokens_details.cached_tokens` + `completion_tokens_details.reasoning_tokens` | `prompt_tokens_details: {}`，无 reasoning_tokens | `prompt_cache_hit/miss_tokens` |
| "Reply with exactly: OK" prompt_tokens（思考 / 关思考） | 88 / 9 | 88 / 9 | 35 / 9 |
| 分词增量 英 / 中 | 1647 / 1570 | 1647 / 1570 | 1647 / 1570 |
| `max_tokens=999999` | 200 | 200 | 400「[1, 393216]」 |
| `max_completion_tokens=3` | 生效（截到 3 token） | 生效 | 忽略 |
| `thinking:disabled` / `reasoning_effort:none` | 都生效，模板 9 token | 都生效 | 生效 |
| `stop=["5"]` | 生效「1, 2, 3, 4,」 | 生效 | 生效 |
| `temperature=1.5` / `5` | 200 / 400「请求参数无效」（方舟原文） | 200 / **524 挂死 126 s** | – / 400 |
| `logprobs` | 200 | 400 | – |
| 非法 effort 报错文本 | 「当前模型或接口不支持本次请求中的部分参数」（方舟） | 「Upstream request failed: [4…」 | – |
| 工具调用（同步 / 流式） | 正常，`call_` + 24 位 | 正常，`call_` + 24 hex | – |
| 注入检查（"是否有 system 指令"） | No | No | No |
| 自报身份（关思考，仅供参考） | DeepSeek-V3 / gpt-4-0613 | Qwen 2.5 / gpt-4o | – |
| 知识阶梯 | K00 ✓，K01–K23 全 UNKNOWN | 同 | V4.1-Flash 前沿 2025-11 |
| 开放式近期前沿 | 2025-02（Pope Francis、Ishiba、Adams、Chiefs、Han Kang） | 2024-10（同一组答案） | 2025-02 |
| 20k 三针 / 20 轮记忆 | 3/3（4.2 s）/ 通过 | 3/3（3.9 s）/ 通过 | – |

## 2. 速度

| 指标 | sudocode | ikuncode |
|---|---|---|
| 短请求 20 轮（关思考，48 token）p50 / p90 / p95 / max | 2.02 / 2.42 / 3.08 / 9.38 s，0 错 | 1.81 / 2.87 / 3.06 / 3.5 s，0 错 |
| 顺序 5 次（bench）p50 / max | 1.96 / 2.10 s | 1.42 / 3.89 s |
| 流式吞吐 p50（5 次区间） | **83.4 tok/s**（79.9–88.0） | **38.2 tok/s**（31.1–62.0） |
| 流式 TTFB p50 | 2.12 s | 4.43 s |
| 300 词短文总耗时 p50 | 6.7 s | 15.0 s |
| bench 吞吐样本 | 83.5 tok/s，TTFB 2.47 s，1.0 tok/chunk | 45.4 tok/s，TTFB 1.78 s，2.1 tok/chunk |
| 默认思考写代码（3 次中位）：首个思考 token / 首个正文 / 总耗时 | 1.9 / **28.8** / 32.8 s（思考 3963，输出 4622 token，正文 157 tok/s） | 2.3 / **184.2** / 193.4 s（输出 8406 token，正文 75 tok/s；思考数被网关抹掉） |
| IQ 33 题平均耗时 思考开 / 关 | 50 s / 11 s | 116 s / 24 s |
| 20k 上下文三针 | 4.2 s | 3.9 s |

思考开时两家每题输出长度相近（均值 7.2k vs 6.6k token，中位 2.4k vs 2.9k），所以耗时差来自吞吐，不是思考长短。

## 3. 缓存

| 项目 | sudocode | ikuncode |
|---|---|---|
| 5k 前缀（bench）第 1 / 2 次 cached | 0 / 4096 | 0 / 4608 |
| 20k 前缀（ops）第 1 / 2 / 3 次 cached | 0 / 19968 / 19968（命中 98.9%） | 0 / 19968 / 19968（98.9%） |
| 命中后 TTFT | 4.22 → 5.62 s（-33%） | 4.35 → 5.64 s（-30%） |
| TTL +60 / +180 / +300 / +600 s | 19968 / 18432 / 18432 / 18432（/20184） | 19968 / 19968 / 19968 / 19968（/20188） |
| 多轮：轮 2 cached 覆盖轮 1 输入 | 6109 / 5888，覆盖，记忆正确 | 6108 / 5888，覆盖，记忆正确 |
| 块粒度 | 未单测 | 512 token（2k→512、8k→2560、20k→5632、40k→11520 逐级命中） |
| 计费折扣 | 站点无公开价格页，未核实 | 同 |

## 4. 智力（suite/iq_full.json 33 题：reason 12 + hard 7 + xhard 14；思考开 = 默认，关 = `reasoning_effort:none`；16k 输出上限）

| 档 | sudocode 思考开 | ikuncode 思考开 | sudocode 关 | ikuncode 关 |
|---|---|---|---|---|
| reason 12 | 12/12 | 12/12 | 10/12（R2 R3） | 10/12（R2 R10） |
| hard 7 | 6/7（H4） | 7/7 | 3/7（H2 H4 H6 H7） | 5/7（H4 H7） |
| xhard 14 | 12/14（X1 X12） | 13/14（X13） | 5/14 | 7/14 |
| 合计 | **30/33** | **32/33** | **18/33**（宽松 19，X3 只是 LaTeX 分数格式） | **22/33**（宽松 23） |
| 触到 16k 上限的题 | 5 | 3 | 0 | 0 |

### 4.1 复测（两家各再跑一轮第 1 轮里有分歧的 13 题，两种模式；sudocode 第 2 轮跑到 X4 时 key 再次耗尽 → 403，第 3 轮全部 403 作废）

思考开：

| 题 | ikun 第1轮 | ikun 第2轮 | sudo 第1轮 | sudo 第2轮 |
|---|---|---|---|---|
| H4 | ✓ | ✓ | ✗ | ✓ |
| R3 | ✓ | ✗ | ✓ | ✓ |
| R10 | ✓（重试后） | ✓ | ✓ | ✓ |
| X1 | ✓ | ✓ | ✗ | ✓ |
| X4 / X5 | ✓ / ✓ | ✓ / ✓ | ✓ / ✓ | 403 / 403 |
| X6 | ✓ | ✓ | ✓ | ✗ |
| X12 | ✓ | ✓ | ✗ | ✓ |
| X13 | ✗ | ✓ | ✓ | ✗ |
| 其余 H2 H6 X2 X14 | 全对 | 全对 | 全对 | 全对 |

两轮合计答出即正确：ikuncode 43/45，sudocode 39/44；两轮取最好，33 题两家都 **33/33**。思考开时是同一水平，第 1 轮的 30 vs 32 是抽样波动。

关思考：

| 题 | ikun 第1轮 | ikun 第2轮 | sudo 第1轮 | sudo 第2轮 |
|---|---|---|---|---|
| R3 | ✓ | ✓ | ✗ | ✗ |
| R10 | ✗ | ✗ | ✓ | ✗ |
| H2 | ✓ | ✓ | ✗ | ✗ |
| H4 | ✗ | ✗ | ✗ | ✗ |
| H6 | ✓ | ✗ | ✗ | ✗ |
| X1 | ✓ | ✓ | ✗ | ✓ |
| X2 | ✓ | ✓ | ✗ | ✓ |
| X4 | ✓ | ✗ | ✗ | 403 |
| X5 | ✗ | ✓ | ✓ | ✓ |
| X6 | ✓ | ✗ | ✗ | ✗ |
| X12 / X13 | ✗ / ✗ | ✗ / ✗ | ✗ / ✗ | ✗ / ✗ |
| X14 | ✗ | ✓ | ✓ | ✓ |

两轮合计：ikuncode **28/46（61%）**，sudocode **22/45（49%）**；两轮取最好 24/33 vs 20/33。关思考时 ikuncode 稳定高出约 10 个百分点（R3、H2 两轮都是 ikun 对、sudo 错）。同一个 0731 模型出现这种差距，最可能是网关层采样参数不同（例如 ikuncode 的 `router-` 层改写了 temperature/top_p），想验证要做贪心自洽对比，但 sudocode 的 key 已经是负数，没法再测。日常带思考用两家没区别；只有关思考跑批量任务时 ikuncode 略占优。

补充观察：sudocode 思考模式不受 `max_tokens=16000` 约束（R10 一次输出 71k token、X13 52k token，`finish=stop`），思考长的题会比 ikuncode 更贵；ikuncode 触顶 16k 就截断。

## 5. 稳定性（本次只做顺序调用）

两家 20 + 5 次顺序短请求都 0 错误 0 空回复；sudocode 出现一次 9.38 s 的长尾；ikuncode 有约 2% 请求落到备用渠道（uuid id）。ikuncode 的 `temperature=5` 会让上游挂到 Cloudflare 524，参数越界时不报错而是超时，客户端要自己设超时。
