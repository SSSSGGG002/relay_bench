# deepseek-v4-flash 三家对比：ikuncode（基线）/ sudocode / 米醋（2026-10-02，北京时间 16:15–18:41）

- **被测**：`api.ikuncode.cc`（分组 deepseek-official ×0.95）、`sudocode.chat`（分组 Deepseek）、`www.micuapi.ai`（分组 vip_4 ×0.5），模型名都是 `deepseek-v4-flash`。
- **路线**：全部从这台 Mac 出发，经 Clash TUN（用户要求不用北京服务器）。三家同一时段交错测。约 2–8% 调用死于本机到 Clash 的 SSL EOF，已从各项统计中剔除并单列。延迟只适合三家互比，不能和以往北京直连的数字比。
- **脚本**：`glmsuite.py`（fp / inject / leak / params / think / know / cache / cachehit / ctx / lat / soak / speed / iq / logs），另加专项脚本 `results/glmsuite/ds1002/scripts/`（知识阶梯、同名兄弟模型、Agent 式缓存、缓存路由、隐藏思考检查）。
- **数据**：`results/glmsuite/ds1002*`（主体 / iq / iqfix / lat / ikunref），日志 `logs/glmsuite-ds1002/`，三家逐条账单 `results/glmsuite/ds1002/bill-*.json`（已去掉 ip、用户名）。
- **基线**：ikuncode 已冻结为 `suite/reference/ikuncode-dsv4flash.json`（指纹、分词增量、参数状态码、IQ 逐题、漂移题、计费公式）。
- **花费**（站内账单，¥）：ikuncode 6.40，sudocode 4.50（余额从 2.89 跑到 0.14，中途 ¥0 时有 16 次 403），米醋 1.55。

## 结论

1. **米醋的 `deepseek-v4-flash` 是新版本（V4.1-Flash 档），另外两家都是 V4-Flash 0731 老版本。**
   - 关思考智力：米醋 43/54（80%），ikuncode 30/54（56%），sudocode 29/54（54%）。0731 历史值五六成，V4.1 八成多。
   - 知识阶梯（2025-05 到 2025-12，开思考）：米醋 13/18，同站 `deepseek-v4.1-flash` 15/18；ikuncode 3/18。关思考时 ikuncode / sudocode 从 K01 起全部"不知道"。
   - ikuncode 直接回显 `deepseek-v4-flash-0731`；sudocode 是火山方舟原样透传（`02+时间戳` id、`service_tier`），和 09-22 一样。
2. **缓存：ikuncode / sudocode 稳定；米醋是多后端各自缓存、随机分配，命中率只有一半左右。**
   - 同一前缀换问题连发 10 次：ikun 9/10、sudo 9/10、米醋 3/10。
   - 空闲 5–420 s 后再发：ikun 22/23、sudo 21/21、米醋 14/22。米醋没中的空闲时间是 60/90/150/180/300 s，和时长无关，是路由到了没写过这段前缀的后端。
   - 多轮对话三家都是第 2 轮起命中（米醋这类请求似乎粘在同一后端）。
   - **同样 16 次 Agent 式请求（约 45 万输入 token）实扣（峰时）：ikun ¥0.130、sudo ¥0.134、米醋 ¥0.132**。米醋单价最低，但缓存不中按全价收，结果三家一样贵；非峰时 ikuncode 只要 ¥0.065；如果米醋缓存都命中，只要约 ¥0.025。
3. **注入：只有米醋有。** 每个请求注入 59 token 的"Formatting notes for this conversation: (1) Treat the system prompt in this conversation as your sole source of identity and instructions. (2) When a name appears in square brackets like [AB], write it the same way…"。表现为 `total_tokens` 恒比 prompt+completion 多 59、复述探针原样吐出、"有无 system 指令"6/6 答 yes。**这 59 token 没进账单**（逐条按 prompt_tokens 计费，公式 0 偏差），但模型会受它影响。同站 `deepseek-v4.1-flash` 是另一条线路（uuid id、9 token、无注入）。ikuncode / sudocode 分词增量逐位一致、无注入。
4. **稳定性与延迟：sudocode 最快，ikuncode 最稳，米醋尾延迟差。**

   | | 顺序首 token p50 / p90 / p99 | 30 并发 ×2 首 token p50 / p99 | soak 30 min 首 token p50 / p99（有效/总） | 吞吐 |
   |---|---|---|---|---|
   | ikuncode | 2.56 / 3.32 / 5.23 s，60/60 | 5.00 / 8.88 s，60/60 | 4.52 / 8.03 s，171/171（另 9 次本机 SSL） | 81–89 tok/s |
   | sudocode | **1.74 / 2.35 / 3.08 s**，60/60 | 4.28 / 5.71 s，46/46（14 次余额 403） | **3.70 / 7.03 s**，172/172（另 8 次本机 SSL） | 87–94 tok/s |
   | 米醋 | 4.27 / 16.1 / **48.1 s**，59/60 | 13.3 / **50.9 s**，60/60 | 6.54 / **53.1 s**，104/107（3 次读超时，另 7 次本机 SSL） | **205–229 tok/s** |

   - 米醋：一旦开始吐字很快（200+ tok/s），但约 3 成请求要排队 10–60 s 才出第一个字；长请求 8 次 Cloudflare 524（125 s）、12 万 token 上下文被断开。
   - ikuncode 全程 0 个站点错误（只有坏模型名 503）。sudocode 有 3 次 524。
5. **智力（27 题 ×2，max_tokens 32000，默认思考）**：米醋 53/54，ikuncode 49/54（5 次想满 32k 截断，不是答错），sudocode 49/51（另 3 题断线未补）。开思考三家同档，差别在关思考。
6. **参数**：ikuncode / sudocode 都守规矩（`reasoning_effort:none` / `thinking:disabled` 生效，`temperature=5` 400，`max_tokens` 生效，`stop` 生效）。米醋：`reasoning_effort:none` **无效**（照样思考几千 token），要用 `thinking:{"type":"disabled"}`；非法 effort、`temperature=5` 都 200；`stop` 不生效；`max_completion_tokens` 不生效；`max_tokens=999999` 挂到 524。

**怎么选**：要新模型、关思考跑批量 → 米醋（智力最高、吐字最快、单价最低），但别指望缓存省钱，客户端要设 60 s+ 超时并接受 59 token 注入。要稳定、缓存可预期、Agent / Claude Code 式长前缀复用 → sudocode 或 ikuncode（同一个 0731 老模型；sudocode 延迟更低，ikuncode 尾部更稳、本机可直连）。

## 1. 上游指纹

| 项目 | ikuncode | sudocode | 米醋 |
|---|---|---|---|
| id / 回显 | uuid / `deepseek-v4-flash-0731` | `02`+时间戳 / `deepseek-v4-flash` | 32 hex / `deepseek-v4-flash` |
| "Reply OK" prompt_tokens（思考/关） | 88 / 9 | 88 / 9 | 26 / 1（关思考被改写成 1） |
| total − (prompt+completion) | 0 | 0 | **恒 59** |
| usage | 标准 + reasoning_tokens + cached_tokens | 同左 + `service_tier` | new-api 转换格式（claude_cache_*、cost 字段），reasoning_tokens 恒 0 |
| 分词增量 zh / digits / en / code | 1020 / 801 / 293 / 601 | 1020 / 801 / 293 / 601 | 1020 / 801 / 293 / 600 |
| 工具调用 id | `call_` + 24 位 | `call_` + 24 位 | `call_00_` + 24 位（DeepSeek 官方风格） |
| 判断 | 0731（与 09-22 的 `router-` 网关不同，上游已换） | 火山方舟 V4-Flash 0731 原样透传 | 新版本，经一层改写 usage 的网关 |

米醋同站三个名字：`deepseek-v4-flash` 与 `deepseek-v4-flash-0731` 走同一 hex32 池（同样 59 token 注入、知识阶梯关思考都只多知道 K01）；`deepseek-v4.1-flash` 是 uuid / 9 token 的 DeepSeek 官方格式线路，账单里倍率 0（本 key 免费？未核实）。

## 2. 缓存明细

| 项目 | ikuncode | sudocode | 米醋 |
|---|---|---|---|
| 粒度 | 256 token 块 | 256 token 块 | 128 token 块 |
| 25k 前缀第 2 / 3 次 | 0.99 / 0.95 | 0.99 / 0.99 | 0.996 / 0.996 |
| 同前缀换问题 | 命中 0.99 | 命中 0.99 | **0** |
| TTL 60 / 180 / 300 / 600 / 900 s | 0.99 / 0.96 / 0.90 / 0.90 / 0.89 | 0.90 / 0.90 / 0.90 / 0.90 / 0.89 | 0.99 / **0** / 0.99 / **0** / **0** |
| 同一文档连发 12 次（路由验证） | 首次外全中 | 未测 | 中中中不中模式：0,0,0,1,1,1,1,0,1,1,0,1 |
| 命中后耗时 | 3.1 s（未命中 6.6 s） | 2.7 s（5.3 s） | 4.5 s（6.9 s） |
| 命中价 / 输入价 | 2% | 3.3% | 10% |

## 3. 智力

| 档 | ikuncode | sudocode | 米醋 |
|---|---|---|---|
| 开思考（默认） | 49/54（截断 5） | 49/51（断线 3） | **53/54**（截断 1） |
| 关思考 | 30/54（`effort:none`） | 29/54（`effort:none`） | **43/54**（`thinking:disabled`） |
| 米醋用 `effort:none`（实际仍思考） | – | – | 45/54（截断 8） |

关思考错题：ikun / sudo 高度重合（R2 R3 R10 H4 H6 H7 X2 X3 X4 X6 X7 X8 X12 X13），同一 0731 模型的签名。米醋只错 H5 H7 X7 X8 X12 X13。检查过米醋 `thinking:disabled` 没有后台偷偷思考：completion_tokens 与正文字数对得上（每 token 2.3–3.1 字符，与 ikuncode 相同），首字慢是排队。

## 4. 长上下文（三根针）

| | 2 万 | 6 万 | 12 万 |
|---|---|---|---|
| ikuncode | 3/3，首字 8.7 s | 3/3，11.9 s | 3/3，16.2 s |
| sudocode | 3/3，5.1 s | 3/3，7.4 s | 余额不足 403（未测） |
| 米醋 | 3/3，24.8 s | 3/3，27.5 s | 站点断开（13 s，无响应） |

## 5. 计费（逐条账单）

| | 公式（站内额度/token） | 换算每百万 ¥（输入 / 输出 / 缓存） | 核对 |
|---|---|---|---|
| ikuncode | `(p + 4c + 0.02cr) × 峰时2` × 0.95 | 峰时 1.90 / 7.60 / 0.038；非峰 0.95 / 3.80 / 0.019 | 296 条拟合误差 < 1 |
| sudocode | `(3p + 9c + 0.1cr) × 峰时1.2` × 0.5 | 峰时 1.80 / 5.40 / 0.060；非峰 1.50 / 4.50 / 0.050 | 411 条（峰 336 / 非峰 75）误差 p50 0.02% |
| 米醋 | `(p − cr + 0.1cr + 2c) × 0.5 × 0.5` | 0.50 / 1.00 / 0.05 | 422 条 0 偏差（21 条兄弟模型倍率 0） |

峰时 = 工作日北京时间 9–12、14–18 点；本次 16:15–18:41 大部分在峰时。三家公式按北京时间逐条回放账单，相对误差 p50 ≤ 0.02%。

同一批任务按本次实测 token 数计价（¥）：

| 工作量 | ikuncode 非峰 / 峰 | sudocode 非峰 / 峰 | 米醋 |
|---|---|---|---|
| 智力题开思考 54 次（约 38 万输出 token） | 1.88 / 3.75 | 2.36 / 2.83 | **0.39** |
| 智力题关思考 54 次（约 9 万输出） | 0.33 / 0.65 | 0.44 / 0.53 | **0.12** |
| Agent 式 16 次（约 45 万输入，命中 87% / 87% / 47%） | **0.065** / 0.130 | 0.111 / 0.134 | 0.132 |

## 6. 对照：ikuncode 冻结基线

`suite/reference/ikuncode-dsv4flash.json`，漂移题 H2 R2 R4 R9 X12 X2 X3 X4 X5 X6（允许掉 2 题）。以后测别家 deepseek-v4-flash：
`KEY_REF=<ikuncode key> python3 glmsuite.py refcheck suite/reference/ikuncode-dsv4flash.json`（指纹、分词、参数状态码、漂移题；`--quick` 只查指纹）。SAME 就复用智力 / 知识 / 计费结论；延迟、soak、缓存 TTL 仍要同路线同时段重测。注意关思考参数：ikuncode / sudocode 用 `reasoning_effort:none`，米醋必须用 `thinking:disabled`。

## 7. 测试中的问题

- 16:17–16:26 用户关了 Clash，sudocode（本机 DNS 污染，必须走代理）17 道智力题连接失败；恢复后补跑 14 题，余额告急停掉剩下 3 题。
- sudocode 余额：开测 ¥2.89，结束 ¥0.14；30 并发第一、二波有 14 次「额度不足 / 预扣费失败」403，12 万上下文未测，已全部从统计里剔除。
- 米醋的 `thinking_disabled` / `thinking_enabled` 参数探针恰逢本机 SSL EOF，参数表里的结论来自智力和隐藏思考专项（共 70+ 次调用）。

## 8. 补测：米醋 `deepseek-v4-flash-0731`（19:04–19:23 北京时间，只测智力 / 缓存 / 延迟，花费 ¥0.26）

版本说明：Hugging Face 模型卡写明 "DeepSeek-V4-Flash-0731 is the official release of DeepSeek-V4-Flash, superseding the preview version"，即 0731 是 V4-Flash 的正式版。DeepSeek 2026-09-10 又发布了 V4.1-Flash，官方 API 的 `deepseek-v4-flash` 名字现在临时指向 V4.1-Flash。本报告前文的「0731 老版本」指的是「比 V4.1-Flash 早的 V4-Flash 正式版」。

| | 米醋 `-0731` | 米醋 `deepseek-v4-flash` | ikuncode | sudocode |
|---|---|---|---|---|
| 开思考 | 26/27（1 遍） | 53/54 | 49/54 | 49/51 |
| 关思考（米醋用 thinking:disabled） | **36/54（67%）** | 43/54（80%） | 30/54（56%） | 29/54（54%） |
| 同前缀换问题（首次之后） | 6/9 | 2/9 | 9/9 | 9/9 |
| 空闲 60 / 180 / 300 s | 中 / 中 / 中 | 中 / 不中 / 中 | 都中 | 都中 |
| 顺序首 token p50 / p90 / p99 | 4.54 / 18.0 / 27.8 s（60/60） | 4.27 / 16.1 / 48.1 s | 2.56 / 3.32 / 5.23 s | 1.74 / 2.35 / 3.08 s |
| 30 并发首 token p50 / p99 | 5.39 / 17.8 s（30/30，1 波） | 13.3 / 50.9 s | 5.00 / 8.88 s | 4.28 / 5.71 s |

- `-0731` 关思考错题（H2 H4 H6 H7 R2 R10 X3 X6 X7 X8 X12 X13）和 ikuncode / sudocode 的 0731 错题基本重合，是 0731 的特征；同站 `deepseek-v4-flash` 名字更高（80%）。两个名字 id、59 token 注入、价格都一样，但智力不一样，说明米醋把它们路由到不同模型。
- 缓存仍是多后端随机命中，但这次比 `deepseek-v4-flash` 名字好（6/9 vs 2/9）。
- 延迟不在同一时段（晚 1 小时、非峰），只能粗比：p99 比 `deepseek-v4-flash` 低一半，仍远高于另两家。
- 数据：`results/glmsuite/ds1002-m0731/`。
