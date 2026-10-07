# runapi.host glm-5.3-flash vs 智谱官方基准（0915）逐项对比（2026-09-21）


## runapi-glm / glm-5.3-flash (openai) → ❌ 模型身份与官方不一致（知识/自报/思考/分词证据）

偏离项 17（身份 2｜智力 0｜协议 5｜上下文 0｜运营 8）: usage 字段集合, 响应顶层字段, 泄露的隐藏系统提示, 自报厂商, 参数校验与官方逐项一致率, stop 序列生效, 开放式近期知识前沿, 知识阶梯逐题分类一致,   ↳ reason 平均耗时(s),   ↳ hard 平均耗时(s),   ↳ xhard 平均耗时(s), 顺序调用错误/空回复, 首字节 TTFB(s), 首个正文 token TTFT(s), 短请求 p50 延迟(s), 8并发 p50 延迟(s), 生成速度 tok/s

| 维度 | 中转站 | 官方 | 判定 | 说明 |
|---|---|---|---|---|
| 响应 id 格式 | b817de70-5694-4f58-8a02-b35041c81c | 20260915162609f1523f2bb6bb4858 | 一致 | 官方=14位时间戳+18位hex；chatcmpl-/自造id=中转层重新生成 |
| usage 字段集合 | claude_cache_creation_1_h_tokens,claude_cache_creation_5_m_tokens,comp | completion_tokens,completion_tokens_details,prompt_tokens,prompt_token | 偏离 |  |
| 响应顶层字段 | choices,created,id,model,object,usage | choices,created,id,model,object,request_id,usage | 偏离 | 官方带 request_id、无 system_fingerprint/service_tier |
| 模型名回显 | glm-5.3-flash | glm-5.3-flash | 一致 |  |
| 默认返回 reasoning_content | True | True | 一致 | GLM-5.3 永远思考；没有=思考被剥离或换了模型 |
| 流式 obfuscation 字段 | False | False | 一致 | 官方无此字段；有=经过 OpenAI 原生/new-api 改写 |
| 工具调用 id 格式(e_sync) | True | True | 一致 | 官方 openai=call_+有符号整数 / anthropic=call_+24hex |
| 工具调用 id 格式(stream) | True | True | 一致 | 官方 openai=call_+有符号整数 / anthropic=call_+24hex |
| 隐藏提示注入(多算的input tokens) | 12 | 12 | 一致 | 差值>8 = 上游加了系统提示或 usage 被改 |
| 泄露的隐藏系统提示 | I can't quote system prompt or developer instructions verbatim, even p | I can't quote my system prompt or developer instructions verbatim, as  | 偏离 |  |
| 自报厂商 | i am a glm large language model develope | z.ai | 偏离 |  |
| 参数校验与官方逐项一致率 | 7/12 | - | 偏离 | effort_invalid:200(官方400) effort_none:200(官方400) thinking_disabled:200(官方400) temperature_out_of_range:503(官方200) bad_mo |
| stop 序列生效 | True | False | 偏离 |  |
| max_tokens 生效 | True | True | 一致 |  |
| 20轮历史记忆 | True | True | 一致 |  |
| 60k 下 system 规则仍遵守 | True | True | 一致 |  |
| 英文 +1261 o200k tok 的 usage 增量 | 1720 | 1720 | 一致 | 偏差>2% = usage 不是 GLM 分词器算的(估算/伪造) |
| 中文 +2040 o200k tok 的 usage 增量 | 1610 | 1610 | 一致 | 偏差>2% = usage 不是 GLM 分词器算的(估算/伪造) |
| reasoning_effort 生效(low→max 思考token增长) | 0→24 | 7→23 | 一致 |  |
| 知识阶梯前沿 | 2025-11 | 2025-12 | 一致 | 相差≥2个月才算偏离（temperature=1 抽样本身有±1个月噪声）；早于官方 = 更老的模型 |
| 开放式近期知识前沿 | 2026-01 | 2025-05 | 偏离 |  |
| 知识阶梯逐题分类一致 | 20/24 | - | 偏离 | K04:CORRECT(官方UNKNOWN) K05:CORRECT(官方UNKNOWN) K06:CORRECT(官方UNKNOWN) K09:UNKNOWN(官方CORRECT) |
| 同题4次年代一致(无混合池) | ['2025-05', '2025-05', '2025-05', '2025-05'] | ['2025-05', '2013-03', '2025-05', '2025-05'] | 一致 | 官方 GLM 本身对'现任教宗'就答不稳(方济各/良十四世各半)，所以只有官方稳定而中转不稳才算偏离 |
| 智力 reason | 12/12 | 12/12 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ reason 平均耗时(s) | 71.4 | 21.0 | 偏离 | 慢于官方2.5倍以上 |
| 智力 reason_off | 10/12 | 9/12 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ reason_off 平均耗时(s) | 48.1 | 25.6 | 一致 | 慢于官方2.5倍以上 |
| 智力 hard | 4/5 | 5/6 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ hard 平均耗时(s) | 190.0 | 65.3 | 偏离 | 慢于官方2.5倍以上 |
| 智力 hard_off | 4/6 | 6/6 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ hard_off 平均耗时(s) | 176.5 | 81.9 | 一致 | 慢于官方2.5倍以上 |
| 智力 xhard | 12/13 | 6/6 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ xhard 平均耗时(s) | 156.1 | 22.6 | 偏离 | 慢于官方2.5倍以上 |
| 智力 xhard_off | 9/12 | 3/8 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ xhard_off 平均耗时(s) | 77.5 | 42.3 | 一致 | 慢于官方2.5倍以上 |
| 长上下文 20k 三针召回 | 3/3 | 3/3 | 一致 | 耗时 6.1s vs 官方 1.5s ; usage比 1.063 vs 1.063 |
| 长上下文 60k 三针召回 | 3/3 | 3/3 | 一致 | 耗时 10.8s vs 官方 3.5s ; usage比 1.069 vs 1.069 |
| 长上下文 130k 三针召回 | 3/3 | 3/3 | 一致 | 耗时 16.5s vs 官方 4.4s ; usage比 1.069 vs 1.069 |
| 长上下文 230k 三针召回 | 未测 | 3/3 | — | 该轮未覆盖此项 |
| 前缀缓存命中(cached_tokens 序列) | [0, 5056, 5056] | [0, 5056, 5056] | 一致 | 官方隐式缓存第2次即命中；不命中 = 账号池轮询/缓存层被剥离(你付全价) |
| 顺序调用错误/空回复 | 0/2 of 8 | 0/2 of 8 | 偏离 |  |
| 8 并发错误数 | 0 | 0 | 一致 |  |
| 2500 token 长输出不断流 | True | True | 一致 |  |
| 首字节 TTFB(s) | 2.94 | 0.73 | 偏离 | 慢303% |
| 首个正文 token TTFT(s) | 2.94 | 0.73 | 偏离 | 慢303% |
| 短请求 p50 延迟(s) | 3.18 | 1.14 | 偏离 | 慢179% |
| 8并发 p50 延迟(s) | 4.24 | 1.4 | 偏离 | 慢203% |
| 生成速度 tok/s | 27.6 (25.0-31.8) | 61.0 (58.9-62.7) | 偏离 | 慢55% |
| 流式粒度 tok/chunk | 1.0 | 1.0 | 一致 | >3倍官方 = 中转缓冲后再切块(假流式) |


## runapi-glm-anthropic / glm-5.3-flash (anthropic) → ⚠️ 模型层有偏离，需人工复核

偏离项 14（身份 1｜智力 0｜协议 5｜上下文 0｜运营 7）: usage 字段集合, 响应顶层字段, 流式 ping 事件, 工具调用 id 格式(e_sync), 参数校验与官方逐项一致率, 英文 +1261 o200k tok 的 usage 增量,   ↳ reason_off 平均耗时(s),   ↳ hard_off 平均耗时(s),   ↳ xhard 平均耗时(s),   ↳ xhard_off 平均耗时(s), 顺序调用错误/空回复, 首个正文 token TTFT(s), 短请求 p50 延迟(s), 8并发 p50 延迟(s)

| 维度 | 中转站 | 官方 | 判定 | 说明 |
|---|---|---|---|---|
| 响应 id 格式 | 8def5f8e-8a3d-437c-b995-520a689b2a | msg_20260915162609446452a7f2b04362 | 一致 | 官方=14位时间戳+18位hex；chatcmpl-/自造id=中转层重新生成 |
| usage 字段集合 | billing_usage,cache_creation_input_tokens,cache_read_input_tokens,clau | cache_read_input_tokens,input_tokens,output_tokens,server_tool_use,ser | 偏离 |  |
| 响应顶层字段 | content,id,model,role,stop_reason,type,usage | content,id,model,role,stop_reason,stop_sequence,type,usage | 偏离 | 官方带 request_id、无 system_fingerprint/service_tier |
| 模型名回显 | glm-5.3-flash | glm-5.3-flash | 一致 |  |
| thinking signature 形态 | 未测 | 24hex | — | 该轮未覆盖此项 |
| 流式 ping 事件 | 0 | 1 | 偏离 |  |
| 工具调用 id 格式(e_sync) | False | True | 偏离 | 官方 openai=call_+有符号整数 / anthropic=call_+24hex |
| 工具调用 id 格式(stream) | True | True | 一致 | 官方 openai=call_+有符号整数 / anthropic=call_+24hex |
| 隐藏提示注入(多算的input tokens) | 12 | 12 | 一致 | 差值>8 = 上游加了系统提示或 usage 被改 |
| 自报厂商 | z.ai | z.ai | 一致 |  |
| 参数校验与官方逐项一致率 | 8/10 | - | 偏离 | disabled_xhigh:200(官方400) effort_xhigh:200(官方400) |
| stop 序列生效 | False | False | 一致 |  |
| max_tokens 生效 | True | True | 一致 |  |
| 20轮历史记忆 | True | True | 一致 |  |
| 60k 下 system 规则仍遵守 | True | True | 一致 |  |
| 英文 +1261 o200k tok 的 usage 增量 | 1720 | -8 | 偏离 | 偏差>2% = usage 不是 GLM 分词器算的(估算/伪造) |
| 中文 +2040 o200k tok 的 usage 增量 | 1610 | 1610 | 一致 | 偏差>2% = usage 不是 GLM 分词器算的(估算/伪造) |
| 知识阶梯前沿 | 2025-11 | 2025-11 | 一致 | 相差≥2个月才算偏离（temperature=1 抽样本身有±1个月噪声）；早于官方 = 更老的模型 |
| 开放式近期知识前沿 | 2026-01 | 2026-01 | 一致 |  |
| 知识阶梯逐题分类一致 | 23/24 | - | 一致 | K14:UNKNOWN(官方WRONG) |
| 同题4次年代一致(无混合池) | ['2025-05', '2025-05', '2025-05', '2025-05'] | ['2013-03', '2025-05', '2025-05', '2025-05'] | 一致 | 官方 GLM 本身对'现任教宗'就答不稳(方济各/良十四世各半)，所以只有官方稳定而中转不稳才算偏离 |
| 智力 reason | 11/12 | 12/12 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ reason 平均耗时(s) | 89.8 | 38.6 | 一致 | 慢于官方2.5倍以上 |
| 智力 reason_off | 12/12 | 8/12 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ reason_off 平均耗时(s) | 93.2 | 29.9 | 偏离 | 慢于官方2.5倍以上 |
| 智力 hard | 6/6 | 5/6 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ hard 平均耗时(s) | 211.5 | 95.4 | 一致 | 慢于官方2.5倍以上 |
| 智力 hard_off | 5/6 | 4/6 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ hard_off 平均耗时(s) | 214.5 | 51.1 | 偏离 | 慢于官方2.5倍以上 |
| 智力 xhard | 10/11 | 3/3 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ xhard 平均耗时(s) | 129.1 | 12.6 | 偏离 | 慢于官方2.5倍以上 |
| 智力 xhard_off | 12/13 | 2/4 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ xhard_off 平均耗时(s) | 75.8 | 7.1 | 偏离 | 慢于官方2.5倍以上 |
| 长上下文 20k 三针召回 | 3/3 | 3/3 | 一致 | 耗时 7.8s vs 官方 13.7s ; usage比 1.063 vs 0.002 |
| 长上下文 60k 三针召回 | 3/3 | 3/3 | 一致 | 耗时 11.4s vs 官方 2.2s ; usage比 1.069 vs 0.001 |
| 长上下文 130k 三针召回 | 3/3 | 3/3 | 一致 | 耗时 15.5s vs 官方 2.2s ; usage比 1.069 vs 0.0 |
| 前缀缓存命中(cached_tokens 序列) | [0, 5056, 5056] | [5056, 5056, 5056] | 一致 | 官方隐式缓存第2次即命中；不命中 = 账号池轮询/缓存层被剥离(你付全价) |
| 顺序调用错误/空回复 | 0/8 of 8 | 0/0 of 8 | 偏离 |  |
| 8 并发错误数 | 0 | 0 | 一致 |  |
| 2500 token 长输出不断流 | True | True | 一致 |  |
| 首字节 TTFB(s) | 2.13 | 2.68 | 一致 | 快21% |
| 首个正文 token TTFT(s) | 91.15 | 2.68 | 偏离 | 慢3301% |
| 短请求 p50 延迟(s) | 2.68 | 1.43 | 偏离 | 慢87% |
| 8并发 p50 延迟(s) | 4.61 | 1.38 | 偏离 | 慢234% |
| 生成速度 tok/s | 108.6 (40.2-554.7) | 80.0 (76.3-84.4) | 一致 | 快36% |
| 流式粒度 tok/chunk | 0.1 | 1.0 | 一致 | >3倍官方 = 中转缓冲后再切块(假流式) |
