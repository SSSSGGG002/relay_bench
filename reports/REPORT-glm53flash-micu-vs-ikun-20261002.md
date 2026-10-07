# glm-5.3-flash：米醋 vs ikuncode（基线），2026-10-02 19:30–20:07 北京时间

- **被测**：`www.micuapi.ai`（分组 vip_4 ×0.5）；**基线**：`api.ikuncode.cc`（分组 glm ×0.7，key sk-W6y…）。
- **范围**：按用户要求只测智力、缓存、p50/p99，ikuncode 的智力不跑全量。
- **路线**：Mac + Clash TUN，两家同一时段交错测。延迟只做两家横向比较。
- **数据**：`results/glmsuite/glm1002/`，日志 `logs/glmsuite-glm1002/`，refcheck 结果 `results/refcheck/ikuncode-glm53flash-20261002-0733.json`。
- **新基线**：`suite/reference/ikuncode-glm53flash-20261002.json`。旧的 09-26 基线保留不动。
- **花费**：米醋 ¥0.18，ikuncode ¥0.46。

## 结论

1. **两家都是智谱 GLM-5.3-Flash**：米醋写入的缓存，ikuncode 读到了 10044/10145；分词增量两家与 09-26 冻结值逐位一致。
2. **智力**：米醋 27 题跑 1 遍，22/27。丢的 5 题里 3 题是思考跑满 32k 被截断（H4 H7 X8），2 题答错（H5 X12）。ikuncode 09-26 基线这 5 题 9/10 都对，今天抽测 9 题 7/9，refcheck 的 10 道漂移题 9/10 通过。所以米醋大约是 81% 对基线 94%，主要差在长思考被截断上。因为只跑了 1 遍，这个差距有一部分可能是抽样波动。
3. **缓存：两家都不稳**，原因不同。
   - **米醋**：和它的 DeepSeek 一样，后面有多台后端，各自有缓存。连发 6 次里 5 次命中，空闲 10–60 s 后还能命中，120 s 和 240 s 都没中；TTL 那一组的 60/180/300 s 探针全部没中。
   - **ikuncode**：接入层换成了 OpenRouter 风格的网关（`gen-<时间戳>-<20 位>` id，usage 带 `cost` / `is_byok` / `cache_write_tokens`），请求在多个供应商之间轮换，缓存不跨供应商共享。连发 6 次只中 3 次，空闲测试 1/5，同一前缀换个问题也常常不中。09-26 冻结时还是 3 分钟内 100% 命中。
4. **延迟：ikuncode 明显更好。**

   | | 顺序首 token p50 / p90 / p99 | 顺序成功 | 首字超过 10 s | 30 并发首 token p50 / p99 | 并发成功 |
   |---|---|---|---|---|---|
   | ikuncode | **1.83 / 3.75 / 8.21 s** | 60/60 | 0 | **3.60 / 8.17 s** | 30/30 |
   | 米醋 | 3.62 / 12.2 / **38.7 s** | 59/60（1 次读超时） | 10 | 6.80 / 14.5 s | 30/30 |

5. **价格**：米醋只有 ikuncode 的 36%。米醋每百万 token 输入 ¥0.20、输出 ¥0.70、缓存 ¥0.058；ikuncode 是 ¥0.56 / ¥1.96 / ¥0.161。两家都按账单逐条拟合，误差在几个额度单位以内。
6. **注入：米醋有。** 35 次请求的 total_tokens 都比 prompt + completion 多 59 个，和它的 DeepSeek 用的是同一个模板，这部分不计费；"Reply OK" 报 8 个 prompt token，官方和 ikuncode 都是 17，说明 usage 被改写过。ikuncode 没有注入。
7. **参数**：
   - 米醋的 `thinking: disabled` 不生效，照样思考。
   - ikuncode 的 `thinking: disabled` 和 `max_tokens=999999` 现在都返回 200（09-26 是 400），`temperature=5` 仍是 400。
   - 智谱官方 glm-5.3-flash 本来就关不掉思考，所以两家关不掉都不算作假的证据。

**怎么选**：图便宜、跑批量、不在乎尾延迟，选米醋，但要把超时设长一些，并接受那 59 token 的注入。要低延迟、稳定，选 ikuncode。如果用量里缓存占大头（比如 Agent），两家这次的命中率都不理想，最好用自己的真实工作量按账单比一次实际花费。

## ikuncode 基线变化（refcheck = DRIFT）

| 项 | 09-26 冻结 | 10-02 |
|---|---|---|
| id | uuid | `gen-<ts>-<20位>`（多数）/ uuid |
| usage | 标准 | 加 `cost`、`cost_details`、`is_byok`、`cache_write_tokens` |
| 工具 id | `call_-<int64>` 一类 | `chatcmpl-tool-<hex>` |
| OK prompt_tokens / 分词增量 | 17 / 1050·801·301 | 17 / 1050·801·301（不变） |
| thinking:disabled / max_tokens 999999 | 400 / 400 | 200 / 200 |
| 缓存 | 3 分钟内 100% | 约 4 成，跨供应商不共享 |
| 顺序首 token p50 / p99 | 2.09 / 3.53 s（北京直连） | 1.83 / 8.21 s（Mac + TUN） |
| 智力 | 51/54 | 漂移题 9/10、抽测 7/9（完整分沿用 51/54） |

新基线 `ikuncode-glm53flash-20261002.json` 用的是今天的指纹、缓存和延迟，智力漂移题和完整分数沿用 09-26。以后测 GLM 中转，先跑 `KEY_REF=<key> python3 glmsuite.py refcheck suite/reference/ikuncode-glm53flash-20261002.json`。
