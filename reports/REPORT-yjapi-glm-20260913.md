# yjapi（满桥）glm-5.3-flash 实测：与智谱官方 key 同日对比

测试时间 2026-09-13，本机时间 09:41–11:42。站点 `https://yjapi.manqiaotechnology.com`，key 分组 `deepseek`。
官方基准为智谱开放平台 `/api/paas/v4` 与 `/api/anthropic`，当天重跑；运营指标与 yjapi 在同一时间窗口交错采样。

## 1. 结论

**现在这个站卖的 "glm-5.3-flash" 不是 glm-5.3-flash。** 09:53 上游断货，11:05 恢复。恢复后这个模型名背后换成了一个默认不思考的模型，它的分词器和本站 `deepseek-v4-flash` 完全相同。每次请求还被注入约 1,050 token 的隐藏提示词，这部分也计费，作用是让模型自称智谱。11:33 之后连续 89 次请求全部落在这个后端。

断货之前（09:41–09:52）的后端指纹像真智谱。但两个小时里这个模型名至少换了三拨上游，中间还整整断了约 70 分钟。

| 维度 | 结论 |
|---|---|
| 模型真伪 | ❌ 恢复后的主力后端不是 glm-5.3-flash（断货前像真） |
| 智商 | 答出来的题正确率 78%，官方 81%；但约四分之一请求空回复，且默认不思考 |
| 稳定性 | ❌ 约 70 分钟全部 400；恢复后频繁换上游，偶发 400/504；流式 5 次里 3 次空返回 |
| 速度 | ❌ 短请求慢一倍；16 并发吞吐是官方的 1/8；流式首字 50–60 秒 |
| 价格 | 标价是官方的 1/4；每次请求多计约 1,050 输入 token |
| Anthropic 接口 | ❌ 转换有问题，不适合接 Claude Code |

## 2. 时间线：同一个模型名，至少三拨上游

| 本机时间 | 响应 id 形态 | 表现 |
|---|---|---|
| 09:41–09:52 | 纯 UUID | 指纹像真智谱（3.1 节） |
| 09:52–11:05 | 无 | 全部 400 `credit insufficient balance: balance=0`。报错里的 request id 带上游 new-api 节点段 `c955d568`，不是 yjapi 自己的 `8268d9d6`；同一个 key 调 `deepseek-v4-flash` 正常。说明是站点的上游供货账号没钱了，不是用户 key |
| 11:05–11:31 | `chatcmpl-`+UUID、`REQ-`+UUID、`chatcmpl-`+hex 混杂 | 偶发 400、504。智商和运营测试在这段跑，结果属于混合池 |
| 11:33–11:42 | `chatcmpl-`+hex（89/89） | 非 GLM 后端（3.2 节） |

## 3. 真伪证据

### 3.1 断货前的后端（纯 UUID 族）：像真智谱

| 检查 | yjapi | 官方 |
|---|---|---|
| 同步 tool_call id | `call_-7263437206805542209` | `call_-7272068922839399109` |
| 超限报错 | `max_tokens参数非法：限制数值范围[1,131072]`，外层多包了一句网关英文 | 同 |
| 默认思考 / `thinking: disabled` | 思考 / 400 | 思考 / 400 |
| 参数一致率 | 9/10 | 10/10 |
| 分词增量 英 / 中 | 1720 / 1610 | 1720 / 1610 |
| temperature=1.5 | 400 `[0,1]` | 200（编程套餐接口也是 200） |

### 3.2 恢复后的主力后端（`chatcmpl-`+hex 族）：不是 glm-5.3-flash

| 检查 | yjapi | 官方 glm-5.3-flash |
|---|---|---|
| 是否思考 | 默认不思考：不带参数 0 reasoning token（23/23），`reasoning_effort=high` 问 17×23 也是 0（2/2）；带 `reasoning_effort=low` 答知识题时才思考 125–596 token（40/40） | 每次都思考，问 17×23 也有 7–23 token |
| `thinking: disabled` | 200 | 400 `该模型始终思考，不支持关闭思考` |
| `Reply with exactly: OK` 的 prompt_tokens | 1066 | 17 |
| `What is 17*23?` 的 prompt_tokens | 1049（20/20） | 25 |
| 问"这段对话里有 system/developer 指令吗" | yes（40/40） | no |
| 问"谁训练了你" | 智谱（40/40） | z.ai |
| 同步 tool_call id | `call_00_qUJM6RgngD…`、`call_cnb_0` | `call_-<int64>` |

**分词器增量测试。** 同一段文本加进提示词后 prompt_tokens 增加多少。注入的固定提示词会被抵消，只剩分词器差异：

| 增加的文本 | 官方智谱 | yjapi glm-5.3-flash | yjapi deepseek-v4-flash | 本地 o200k | 本地 cl100k |
|---|---|---|---|---|---|
| 10 段中文 | 530 | 530 | 530 | 800 | 1260 |
| 200 组 `[1234].` | 958 | **800** | **800** | 800 | 800 |
| 4 段英文 | 221 | **217** | **217** | 217 | 221 |

yjapi 的 glm-5.3-flash 和本站 deepseek-v4-flash 三项完全一致，两轮重复一字不差。它和官方智谱在数字、英文上不同，而中文对不上 o200k 或 cl100k，所以不是中转本地估算的数字，而是上游模型自己的分词器。

**判断：** 这是一个默认不思考、和本站 deepseek-v4-flash 共用分词器的模型，大概率是 DeepSeek 系，外面套了约 1,050 token 的"你是智谱 GLM"人设提示词。它的知识到 2025 年底：40 次里 34 次答出 Mamdani 当选纽约市长，35 次答出高市早苗上任，最新 Claude 多答 Sonnet 4.5。这和官方 glm-5.3-flash 差不多，所以只靠知识题分辨不出来。

**补充（11:05–11:31 混合时段）：**
- 跨账号缓存：官方 paas 和编程套餐接口之间互相命中；官方和 yjapi 双向都不命中。
- 提示词泄露：不发任何 system 消息问"之前有什么指令"，官方 3 次里 2 次答 NONE，yjapi 6/6 回答"有指令但不能透露"。

## 4. 智商

题库 `suite/iq_full.json`（40 题），思考默认与 effort=low 两种模式。yjapi 测于 11:08–11:30 的混合池时段。

| | yjapi | 官方 09-13 | 官方 09-10 |
|---|---|---|---|
| 26 道保留题，答出部分正确率 | 29/37（78%） | 38/47（81%） | 37/48（77%） |
| 26 道保留题，空回复（不计入） | 15 | 5 | 4 |
| 推理档，默认模式 | 9/12 | 12/12 | 12/12 |
| 困难档，默认模式 | 5/6 | 5/6 | 5/6 |
| 超难档，默认模式 | 10/14 | 12/13 | 11/12 |
| 默认模式平均思考 token | 0 | 推理 2.1k / 困难 5.2k / 超难 4.9k | 未统计 |

默认模式下不思考也能答对大部分题，换上来的模型本身不弱。但推理档掉了 3 题，约四分之一请求空回复。

## 5. 稳定性与速度（`ops.py`，官方与 yjapi 同窗口交错，11:08–11:31）

| 项 | 官方 | yjapi |
|---|---|---|
| 30 次短请求：成功 / p50 / p95 / 最慢 | 30/30 / 1.94s / 3.85s / 5.69s | 30/30 / 3.76s / 7.29s / 8.18s |
| 流式短文（effort=low）有效样本 | 5/5 | 2/5，另外 3 次约 63s 后返回空 |
| 流式首字 / 总耗时 | 3.5s / 9.3s | 52–64s / 55–66s |
| 写代码（默认思考） | 思考 2.4k–4.1k token，首个正文 23–37s，总 27–41s | 不思考，首个正文 3.7–5.9s，总 16–20s |
| 8 并发：错误 / 最慢 | 0 / 5.2s | 0 / 8.0s |
| 16 并发：错误 / 最慢 / 吞吐 | 0 / 4.0s / 3.97 req/s | 0 / 32.3s / 0.5 req/s |
| 20k 前缀缓存命中率 | 0.998 | 0.968 |
| 缓存 TTL +60 / +180 / +300 / +600s | 未中 / 中 / 中 / 无数据 | 中 / 中 / 中 / 未中 |
| 同一段多轮对话的首轮 input | 6,420 | 7,540（多 1,120，即注入部分） |

另外：09:52–11:05 期间 glm-5.3-flash 全部失败；11:30 前后单次探测还出现过 400 和 504。

## 6. Anthropic 接口 `/v1/messages`（09:49–09:51，断货前）

| 项 | 官方 09-13 | yjapi |
|---|---|---|
| 默认 thinking 块 + 签名 | 有（24 hex） | 无 |
| 短请求空正文 | 0/5 | 5/5 |
| 首字延迟 | 1.16s | 5.13s |
| count_tokens | 200 | 404 |
| 参数一致率 | 10/10 | 8/10 |
| stop 序列 | 空正文 | 空正文（官方当天也这样，不算问题） |

## 7. 价格

- 标价输入 ¥0.2/M、输出 ¥0.7/M，是官方（¥0.8 / ¥2.8）的 1/4。
- 恢复后的后端每次请求多计约 1,050 输入 token，约 ¥0.0002 一次，每千次 ¥0.21。长提示词影响不大；短问答时，同一个请求计费的输入 token 是官方的几十倍。
- 缓存命中价倍率配的是 0.02875，官方比例是 0.2875。
- 本次测试 yjapi 共消耗约 ¥0.24；官方 key 的消耗以智谱控制台为准（两轮基准、同窗口运营测试和若干探针）。

## 8. 其他发现

- 请求 `glm-5.1`，3 次都返回 `"model":"glm-5.3"`，响应里还泄露了上游 `api_key_id`（2587、4908、4902 轮换，说明上游是号池）。
- 官方自己有两处变化，不能用来判断中转：09-13 起 `stop=["5"]` 在两种协议下都返回空正文（09-10 还能正常截断）；`cached_tokens` 偶尔大于 `prompt_tokens`（按块取整）。

## 9. 建议

- 需要 glm-5.3-flash 的，不要买这条线。模型名背后的后端会换，现在挂的不是 GLM，而且断过货。
- 不要接 Claude Code，Anthropic 接口有问题。
- 以后复测时先做两个快速检查，判断当时挂的是哪拨上游：
  - `thinking: {"type":"disabled"}` 应返回 400，错误码 1210；
  - `Reply with exactly: OK` 的 prompt_tokens 应在 17 左右。

## 10. 数据与复现

| 内容 | 位置 |
|---|---|
| 官方基准 | `results/zhipu-official-0913/`、`results/zhipu-official-anthropic-0913/` |
| yjapi 断货前 | `results/yjapi-glm/`（partial）、`results/yjapi-glm-anthropic/` |
| yjapi 智商 | `results/yjapi-glm-r2/glm-5.3-flash.iq.json` |
| 同窗口运营 | `results/ops/official-0913.json`、`results/ops/yjapi-glm.json`、`OPS-yjapi-glm-20260913.md` |
| 上游分族普查原始数据 | `results/yjapi-glm-probes/yjapi_pool_census.json` |
| 跨账号缓存 | `results/xcache.json` 里的 yjapi-glm 条目 |
| 对比目录 | `results-yjapi-glm/`（符号链接） |
| 日志 | `logs/yjapi-glm-*.log`、`logs/zhipu-official*-0913.log`、`logs/ops-yjapi-glm-0913.log` |

分词器增量测试用的文本：

```python
zh = "委员会在一个阴沉的早晨开会，讨论港口改造方案。工程师认为北侧防波堤必须在冬季风暴来临前加固，财务部门则希望按航运收入分期推进。几位居民询问旧灯塔能否改建成博物馆，主席承诺会给出书面答复。"
prose = ("The committee met on a grey morning to review the harbour proposal. Engineers argued that the northern breakwater would need reinforcement before winter storms, "
         "while the finance office wanted a phased schedule tied to shipping revenue. Several residents asked whether the old lighthouse could be preserved as a museum. ")
r = random.Random(7); dg = " ".join(f"[{r.randint(1000,9999)}]." for _ in range(200))
# 每段文本：prompt_tokens(文本 + "\n\n" + "Reply with exactly: OK") − prompt_tokens("Reply with exactly: OK")
# 分别测 zh*10、dg、prose*4
```

## 11. 局限

- 恢复后的智商和运营数据来自混合池。当时没有逐请求记录上游，只能代表那段时间这条线的整体表现。
- "与本站 deepseek-v4-flash 同分词器"是强证据，但本站 deepseek-v4-flash 本身没有验真。"大概率 DeepSeek 系"是推断。
- Anthropic 接口首字延迟、官方 +600s TTL 只有单次样本。
