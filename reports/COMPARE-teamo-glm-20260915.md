# 中转站 vs 官方基准 对比报告

基准: ['zhipu-official-0915', 'zhipu-official-anthropic-0915']  (官方直连结果；每一行 = 中转站的数值 / 官方的数值 / 判定)

## 总表

| 中转站 | 模型 | 协议 | 结论 | 偏离项(身份/智力/协议/上下文/运营) |
|---|---|---|---|---|
| rtoc | glm-5.3-flash | openai | ⚠️ 模型层有偏离，需人工复核 | 身份1/智力0/协议5/上下文1/运营8 |
| rtoc-anthropic | glm-5.3-flash | anthropic | ⚠️ 模型层有偏离，需人工复核 | 身份1/智力0/协议2/上下文0/运营5 |
| teamo-glm | glm-5.3-flash | openai | ❌ 模型身份与官方不一致（知识/自报/思考/分词证据） | 身份2/智力0/协议6/上下文0/运营6 |
| teamo-glm-anthropic | glm-5.3-flash | anthropic | ❌ 模型身份与官方不一致（知识/自报/思考/分词证据） | 身份2/智力0/协议2/上下文0/运营3 |
| v129-K1 | glm-5.3-flash | openai | ⚠️ 模型层有偏离，需人工复核 | 身份1/智力0/协议4/上下文0/运营4 |
| v129-K1-anthropic | glm-5.3-flash | anthropic | ⚠️ 模型层有偏离，需人工复核 | 身份1/智力0/协议4/上下文0/运营4 |
| v129-K1-proxy | glm-5.3-flash | anthropic | ❌ 模型身份与官方不一致（知识/自报/思考/分词证据） | 身份2/智力0/协议4/上下文0/运营0 |
| v129-K2 | glm-5.3-flash | openai | ⚠️ 模型层有偏离，需人工复核 | 身份1/智力1/协议4/上下文0/运营3 |
| v129-K3 | glm-5.3-flash | openai | ⛔ 不可用（该分组没有此模型渠道 / 全部失败） | 身份0/智力0/协议3/上下文0/运营1 |
| v129-K4 | glm-5.3-flash | openai | ⛔ 不可用（该分组没有此模型渠道 / 全部失败） | 身份0/智力0/协议3/上下文0/运营1 |
| yjapi-glm | glm-5.3-flash | openai | ⚠️ 模型层有偏离，需人工复核 | 身份1/智力0/协议3/上下文6/运营3 |
| yjapi-glm-anthropic | glm-5.3-flash | anthropic | ❌ 模型身份与官方不一致（知识/自报/思考/分词证据） | 身份1/智力2/协议5/上下文1/运营1 |
| yjapi-glm-r2 | glm-5.3-flash | openai | 🟡 模型一致，但经过协议改写层（new-api 转换；参数/流式/计费字段与官方不同）；运营指标偏离 2 项 | 身份0/智力2/协议3/上下文0/运营2 |
| zhipu-0913 | glm-5.3-flash | openai | ❌ 模型身份与官方不一致（知识/自报/思考/分词证据） | 身份2/智力1/协议0/上下文0/运营5 |
| zhipu-official | glm-5.3-flash | openai | ⚠️ 模型层有偏离，需人工复核 | 身份1/智力0/协议2/上下文0/运营2 |
| zhipu-official-0913 | glm-5.3-flash | openai | ⚠️ 模型层有偏离，需人工复核 | 身份1/智力0/协议1/上下文0/运营2 |
| zhipu-official-anthropic | glm-5.3-flash | anthropic | ⚠️ 模型层有偏离，需人工复核 | 身份1/智力0/协议2/上下文0/运营4 |
| zhipu-official-anthropic-0913 | glm-5.3-flash | anthropic | ⚠️ 模型层有偏离，需人工复核 | 身份1/智力0/协议0/上下文0/运营0 |

## 0. 官方基准指纹速览

| 基准 | 模型 | 协议 | id样例 | usage字段 | 默认思考 | 注入tok | 知识前沿(阶梯/开放) | IQ direct/reason/hard/xhard | TTFT | tok/s | p50 | 缓存 | ctx |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| zhipu-official-0915 | glm-5.3-flash | openai | `20260915162609f1523f2bb6bb4858` | completion_tokens,completion_tokens_details,prompt_tokens,prompt_tokens_details,total_tokens | True | 12 | 2025-12/2025-05 | None/12/12/5/6/6/6 | 0.73 | 61.0 | 1.14 | [0, 5056, 5056] | 3/3/3/3/3/3/3/3 |
| zhipu-official-anthropic-0915 | glm-5.3-flash | anthropic | `msg_20260915162609446452a7f2b04362` | cache_read_input_tokens,input_tokens,output_tokens,server_tool_use,service_tier | True | 12 | 2025-11/2026-01 | None/12/12/5/6/3/3 | 2.68 | 80.0 | 1.43 | [5056, 5056, 5056] | 3/3/3/3/3/3/None |

## rtoc / glm-5.3-flash (openai) → ⚠️ 模型层有偏离，需人工复核

偏离项 16（身份 1｜智力 0｜协议 5｜上下文 1｜运营 8）: usage 字段集合, 响应顶层字段, 参数校验与官方逐项一致率, stop 序列生效, 60k 下 system 规则仍遵守, reasoning_effort 生效(low→max 思考token增长), 开放式近期知识前沿,   ↳ reason 平均耗时(s),   ↳ xhard 平均耗时(s),   ↳ xhard_off 平均耗时(s), 顺序调用错误/空回复, 2500 token 长输出不断流, 首字节 TTFB(s), 首个正文 token TTFT(s), 短请求 p50 延迟(s), 8并发 p50 延迟(s)

| 维度 | 中转站 | 官方 | 判定 | 说明 |
|---|---|---|---|---|
| 响应 id 格式 | msg_2026091014360855627beeb9934132 | 20260915162609f1523f2bb6bb4858 | 一致 | 官方=14位时间戳+18位hex；chatcmpl-/自造id=中转层重新生成 |
| usage 字段集合 | billing_usage,claude_cache_creation_1_h_tokens,claude_cache_creation_5 | completion_tokens,completion_tokens_details,prompt_tokens,prompt_token | 偏离 |  |
| 响应顶层字段 | choices,created,id,model,object,usage | choices,created,id,model,object,request_id,usage | 偏离 | 官方带 request_id、无 system_fingerprint/service_tier |
| 模型名回显 | glm-5.3-flash | glm-5.3-flash | 一致 |  |
| 默认返回 reasoning_content | True | True | 一致 | GLM-5.3 永远思考；没有=思考被剥离或换了模型 |
| 流式 obfuscation 字段 | False | False | 一致 | 官方无此字段；有=经过 OpenAI 原生/new-api 改写 |
| 工具调用 id 格式(e_sync) | True | True | 一致 | 官方 openai=call_+有符号整数 / anthropic=call_+24hex |
| 工具调用 id 格式(stream) | True | True | 一致 | 官方 openai=call_+有符号整数 / anthropic=call_+24hex |
| 隐藏提示注入(多算的input tokens) | 12 | 12 | 一致 | 差值>8 = 上游加了系统提示或 usage 被改 |
| 自报厂商 | z.ai | z.ai | 一致 |  |
| 参数校验与官方逐项一致率 | 8/12 | - | 偏离 | effort_none:200(官方400) thinking_disabled:200(官方400) effort_low:400(官方200) bad_model:503(官方400) |
| stop 序列生效 | True | False | 偏离 |  |
| max_tokens 生效 | True | True | 一致 |  |
| 20轮历史记忆 | True | True | 一致 |  |
| 60k 下 system 规则仍遵守 | False | True | 偏离 |  |
| 英文 +1261 o200k tok 的 usage 增量 | 1720 | 1720 | 一致 | 偏差>2% = usage 不是 GLM 分词器算的(估算/伪造) |
| 中文 +2040 o200k tok 的 usage 增量 | 1610 | 1610 | 一致 | 偏差>2% = usage 不是 GLM 分词器算的(估算/伪造) |
| reasoning_effort 生效(low→max 思考token增长) | 0→0 | 7→23 | 偏离 |  |
| 知识阶梯前沿 | 2025-11 | 2025-12 | 一致 | 相差≥2个月才算偏离（temperature=1 抽样本身有±1个月噪声）；早于官方 = 更老的模型 |
| 开放式近期知识前沿 | 2026-01 | 2025-05 | 偏离 |  |
| 知识阶梯逐题分类一致 | 23/24 | - | 一致 | K09:UNKNOWN(官方CORRECT) |
| 同题4次年代一致(无混合池) | ['2025-05', '2025-05', '2013-03', '2013-03'] | ['2025-05', '2013-03', '2025-05', '2025-05'] | 一致 | 官方 GLM 本身对'现任教宗'就答不稳(方济各/良十四世各半)，所以只有官方稳定而中转不稳才算偏离 |
| 智力 reason | 12/12 | 12/12 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ reason 平均耗时(s) | 57.4 | 21.0 | 偏离 | 慢于官方2.5倍以上 |
| 智力 reason_off | 11/12 | 9/12 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ reason_off 平均耗时(s) | 62.8 | 25.6 | 一致 | 慢于官方2.5倍以上 |
| 智力 hard | 6/6 | 5/6 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ hard 平均耗时(s) | 106.7 | 65.3 | 一致 | 慢于官方2.5倍以上 |
| 智力 hard_off | 5/6 | 6/6 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ hard_off 平均耗时(s) | 134.6 | 81.9 | 一致 | 慢于官方2.5倍以上 |
| 智力 xhard | 12/13 | 6/6 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ xhard 平均耗时(s) | 139.4 | 22.6 | 偏离 | 慢于官方2.5倍以上 |
| 智力 xhard_off | 11/13 | 3/8 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ xhard_off 平均耗时(s) | 144.0 | 42.3 | 偏离 | 慢于官方2.5倍以上 |
| 长上下文 20k 三针召回 | 3/3 | 3/3 | 一致 | 耗时 7.4s vs 官方 1.5s ; usage比 1.063 vs 1.063 |
| 长上下文 60k 三针召回 | 3/3 | 3/3 | 一致 | 耗时 10.6s vs 官方 3.5s ; usage比 1.069 vs 1.069 |
| 长上下文 130k 三针召回 | 3/3 | 3/3 | 一致 | 耗时 21.8s vs 官方 4.4s ; usage比 1.069 vs 1.069 |
| 长上下文 230k 三针召回 | 3/3 | 3/3 | 一致 | 耗时 30.4s vs 官方 6.0s ; usage比 1.066 vs 1.066 |
| 前缀缓存命中(cached_tokens 序列) | [0, 5056, 5056] | [0, 5056, 5056] | 一致 | 官方隐式缓存第2次即命中；不命中 = 账号池轮询/缓存层被剥离(你付全价) |
| 顺序调用错误/空回复 | 0/8 of 8 | 0/2 of 8 | 偏离 |  |
| 8 并发错误数 | 0 | 0 | 一致 |  |
| 2500 token 长输出不断流 | False | True | 偏离 |  |
| 首字节 TTFB(s) | 9.48 | 0.73 | 偏离 | 慢1199% |
| 首个正文 token TTFT(s) | 84.63 | 0.73 | 偏离 | 慢11493% |
| 短请求 p50 延迟(s) | 2.17 | 1.14 | 偏离 | 慢90% |
| 8并发 p50 延迟(s) | 6.77 | 1.4 | 偏离 | 慢384% |
| 生成速度 tok/s | 187.6 (187.6-187.6) | 61.0 (58.9-62.7) | 一致 | 快208% |
| 流式粒度 tok/chunk | 0.1 | 1.0 | 一致 | >3倍官方 = 中转缓冲后再切块(假流式) |

## rtoc-anthropic / glm-5.3-flash (anthropic) → ⚠️ 模型层有偏离，需人工复核

偏离项 8（身份 1｜智力 0｜协议 2｜上下文 0｜运营 5）: 参数校验与官方逐项一致率, stop 序列生效, 英文 +1261 o200k tok 的 usage 增量,   ↳ xhard 平均耗时(s),   ↳ xhard_off 平均耗时(s), 顺序调用错误/空回复, 8并发 p50 延迟(s), 生成速度 tok/s

| 维度 | 中转站 | 官方 | 判定 | 说明 |
|---|---|---|---|---|
| 响应 id 格式 | msg_2026091015310283b4e7b0c2f74752 | msg_20260915162609446452a7f2b04362 | 一致 | 官方=14位时间戳+18位hex；chatcmpl-/自造id=中转层重新生成 |
| usage 字段集合 | cache_read_input_tokens,input_tokens,output_tokens,server_tool_use,ser | cache_read_input_tokens,input_tokens,output_tokens,server_tool_use,ser | 一致 |  |
| 响应顶层字段 | content,id,model,role,stop_reason,stop_sequence,type,usage | content,id,model,role,stop_reason,stop_sequence,type,usage | 一致 | 官方带 request_id、无 system_fingerprint/service_tier |
| 模型名回显 | glm-5.3-flash | glm-5.3-flash | 一致 |  |
| thinking signature 形态 | 24hex | 24hex | 一致 | 官方=24位hex |
| 流式 ping 事件 | 1 | 1 | 一致 |  |
| 工具调用 id 格式(e_sync) | True | True | 一致 | 官方 openai=call_+有符号整数 / anthropic=call_+24hex |
| 工具调用 id 格式(stream) | True | True | 一致 | 官方 openai=call_+有符号整数 / anthropic=call_+24hex |
| 隐藏提示注入(多算的input tokens) | 12 | 12 | 一致 | 差值>8 = 上游加了系统提示或 usage 被改 |
| 自报厂商 | z.ai | z.ai | 一致 |  |
| 参数校验与官方逐项一致率 | 8/10 | - | 偏离 | disabled_xhigh:200(官方400) effort_xhigh:200(官方400) |
| stop 序列生效 | True | False | 偏离 |  |
| max_tokens 生效 | True | True | 一致 |  |
| 20轮历史记忆 | True | True | 一致 |  |
| 60k 下 system 规则仍遵守 | True | True | 一致 |  |
| 英文 +1261 o200k tok 的 usage 增量 | 1720 | -8 | 偏离 | 偏差>2% = usage 不是 GLM 分词器算的(估算/伪造) |
| 中文 +2040 o200k tok 的 usage 增量 | 1610 | 1610 | 一致 | 偏差>2% = usage 不是 GLM 分词器算的(估算/伪造) |
| 知识阶梯前沿 | 2025-11 | 2025-11 | 一致 | 相差≥2个月才算偏离（temperature=1 抽样本身有±1个月噪声）；早于官方 = 更老的模型 |
| 开放式近期知识前沿 | 2026-01 | 2026-01 | 一致 |  |
| 知识阶梯逐题分类一致 | 22/24 | - | 一致 | K06:CORRECT(官方UNKNOWN) K14:UNKNOWN(官方WRONG) |
| 同题4次年代一致(无混合池) | ['2013-03', '2013-03', '2013-03', '2013-03'] | ['2013-03', '2025-05', '2025-05', '2025-05'] | 一致 | 官方 GLM 本身对'现任教宗'就答不稳(方济各/良十四世各半)，所以只有官方稳定而中转不稳才算偏离 |
| 智力 reason | 11/12 | 12/12 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ reason 平均耗时(s) | 40.6 | 38.6 | 一致 | 慢于官方2.5倍以上 |
| 智力 reason_off | 7/12 | 8/12 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ reason_off 平均耗时(s) | 46.4 | 29.9 | 一致 | 慢于官方2.5倍以上 |
| 智力 hard | 4/6 | 5/6 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ hard 平均耗时(s) | 127.1 | 95.4 | 一致 | 慢于官方2.5倍以上 |
| 智力 hard_off | 4/6 | 4/6 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ hard_off 平均耗时(s) | 106.1 | 51.1 | 一致 | 慢于官方2.5倍以上 |
| 智力 xhard | 7/7 | 3/3 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ xhard 平均耗时(s) | 149.4 | 12.6 | 偏离 | 慢于官方2.5倍以上 |
| 智力 xhard_off | 5/7 | 2/4 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ xhard_off 平均耗时(s) | 90.0 | 7.1 | 偏离 | 慢于官方2.5倍以上 |
| 长上下文 20k 三针召回 | 3/3 | 3/3 | 一致 | 耗时 25.3s vs 官方 13.7s ; usage比 1.063 vs 0.002 |
| 长上下文 60k 三针召回 | 3/3 | 3/3 | 一致 | 耗时 28.5s vs 官方 2.2s ; usage比 1.069 vs 0.001 |
| 长上下文 130k 三针召回 | 3/3 | 3/3 | 一致 | 耗时 23.8s vs 官方 2.2s ; usage比 1.069 vs 0.0 |
| 前缀缓存命中(cached_tokens 序列) | [0, 5056, 5056] | [5056, 5056, 5056] | 一致 | 官方隐式缓存第2次即命中；不命中 = 账号池轮询/缓存层被剥离(你付全价) |
| 顺序调用错误/空回复 | 0/1 of 8 | 0/0 of 8 | 偏离 |  |
| 8 并发错误数 | 0 | 0 | 一致 |  |
| 2500 token 长输出不断流 | True | True | 一致 |  |
| 首字节 TTFB(s) | 2.27 | 2.68 | 一致 | 快15% |
| 首个正文 token TTFT(s) | 2.49 | 2.68 | 一致 | 快7% |
| 短请求 p50 延迟(s) | 2.55 | 1.43 | 一致 | 慢78% |
| 8并发 p50 延迟(s) | 7.1 | 1.38 | 偏离 | 慢414% |
| 生成速度 tok/s | 32.0 (29.7-32.8) | 80.0 (76.3-84.4) | 偏离 | 慢60% |
| 流式粒度 tok/chunk | 1.0 | 1.0 | 一致 | >3倍官方 = 中转缓冲后再切块(假流式) |

## teamo-glm / glm-5.3-flash (openai) → ❌ 模型身份与官方不一致（知识/自报/思考/分词证据）

偏离项 15（身份 2｜智力 0｜协议 6｜上下文 0｜运营 6）: usage 字段集合, 响应顶层字段, 默认返回 reasoning_content, 隐藏提示注入(多算的input tokens), 泄露的隐藏系统提示, 参数校验与官方逐项一致率, reasoning_effort 生效(low→max 思考token增长), 开放式近期知识前沿,   ↳ xhard 平均耗时(s), 顺序调用错误/空回复, 相同请求 input_tokens 漂移, 首字节 TTFB(s), 首个正文 token TTFT(s), 短请求 p50 延迟(s), 8并发 p50 延迟(s)

| 维度 | 中转站 | 官方 | 判定 | 说明 |
|---|---|---|---|---|
| 响应 id 格式 | 0e0e76ff1f4444b59cbdfd35c935e7a4 | 20260915162609f1523f2bb6bb4858 | 一致 | 官方=14位时间戳+18位hex；chatcmpl-/自造id=中转层重新生成 |
| usage 字段集合 | claude_cache_creation_1_h_tokens,claude_cache_creation_5_m_tokens,comp | completion_tokens,completion_tokens_details,prompt_tokens,prompt_token | 偏离 |  |
| 响应顶层字段 | choices,created,id,model,object,usage | choices,created,id,model,object,request_id,usage | 偏离 | 官方带 request_id、无 system_fingerprint/service_tier |
| 模型名回显 | glm-5.3-flash | glm-5.3-flash | 一致 |  |
| 默认返回 reasoning_content | False | True | 偏离 | GLM-5.3 永远思考；没有=思考被剥离或换了模型 |
| 流式 obfuscation 字段 | False | False | 一致 | 官方无此字段；有=经过 OpenAI 原生/new-api 改写 |
| 工具调用 id 格式(e_sync) | True | True | 一致 | 官方 openai=call_+有符号整数 / anthropic=call_+24hex |
| 工具调用 id 格式(stream) | True | True | 一致 | 官方 openai=call_+有符号整数 / anthropic=call_+24hex |
| 隐藏提示注入(多算的input tokens) | 3 | 12 | 偏离 | 差值>8 = 上游加了系统提示或 usage 被改 |
| 泄露的隐藏系统提示 | I don't have access to a system prompt in this conversation, so there  | I can't quote my system prompt or developer instructions verbatim, as  | 偏离 |  |
| 自报厂商 | z.ai | z.ai | 一致 |  |
| 参数校验与官方逐项一致率 | 9/12 | - | 偏离 | effort_invalid:200(官方400) effort_none:200(官方400) thinking_disabled:200(官方400) |
| stop 序列生效 | False | False | 一致 |  |
| max_tokens 生效 | True | True | 一致 |  |
| 20轮历史记忆 | True | True | 一致 |  |
| 60k 下 system 规则仍遵守 | True | True | 一致 |  |
| 英文 +1261 o200k tok 的 usage 增量 | 1720 | 1720 | 一致 | 偏差>2% = usage 不是 GLM 分词器算的(估算/伪造) |
| 中文 +2040 o200k tok 的 usage 增量 | 1601 | 1610 | 一致 | 偏差>2% = usage 不是 GLM 分词器算的(估算/伪造) |
| reasoning_effort 生效(low→max 思考token增长) | 0→0 | 7→23 | 偏离 |  |
| 知识阶梯前沿 | 2025-12 | 2025-12 | 一致 | 相差≥2个月才算偏离（temperature=1 抽样本身有±1个月噪声）；早于官方 = 更老的模型 |
| 开放式近期知识前沿 | 2025-10 | 2025-05 | 偏离 |  |
| 知识阶梯逐题分类一致 | 22/24 | - | 一致 | K04:CORRECT(官方UNKNOWN) K10:WRONG(官方UNKNOWN) |
| 同题4次年代一致(无混合池) | ['2013-03', '2013-03', '2025-05', '2013-03'] | ['2025-05', '2013-03', '2025-05', '2025-05'] | 一致 | 官方 GLM 本身对'现任教宗'就答不稳(方济各/良十四世各半)，所以只有官方稳定而中转不稳才算偏离 |
| 智力 reason | 10/12 | 12/12 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ reason 平均耗时(s) | 29.8 | 21.0 | 一致 | 慢于官方2.5倍以上 |
| 智力 reason_off | 7/12 | 9/12 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ reason_off 平均耗时(s) | 21.4 | 25.6 | 一致 | 慢于官方2.5倍以上 |
| 智力 hard | 4/6 | 5/6 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ hard 平均耗时(s) | 34.9 | 65.3 | 一致 | 慢于官方2.5倍以上 |
| 智力 hard_off | 4/5 | 6/6 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ hard_off 平均耗时(s) | 76.8 | 81.9 | 一致 | 慢于官方2.5倍以上 |
| 智力 xhard | 12/13 | 6/6 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ xhard 平均耗时(s) | 57.1 | 22.6 | 偏离 | 慢于官方2.5倍以上 |
| 智力 xhard_off | 8/12 | 3/8 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ xhard_off 平均耗时(s) | 52.1 | 42.3 | 一致 | 慢于官方2.5倍以上 |
| 长上下文 20k 三针召回 | 3/3 | 3/3 | 一致 | 耗时 5.7s vs 官方 1.5s ; usage比 1.063 vs 1.063 |
| 长上下文 60k 三针召回 | 3/3 | 3/3 | 一致 | 耗时 17.4s vs 官方 3.5s ; usage比 1.069 vs 1.069 |
| 长上下文 130k 三针召回 | 3/3 | 3/3 | 一致 | 耗时 9.1s vs 官方 4.4s ; usage比 1.069 vs 1.069 |
| 长上下文 230k 三针召回 | 3/3 | 3/3 | 一致 | 耗时 20.0s vs 官方 6.0s ; usage比 1.066 vs 1.066 |
| 前缀缓存命中(cached_tokens 序列) | [5056, 5056, 5056] | [0, 5056, 5056] | 一致 | 官方隐式缓存第2次即命中；不命中 = 账号池轮询/缓存层被剥离(你付全价) |
| 顺序调用错误/空回复 | 0/1 of 8 | 0/2 of 8 | 偏离 |  |
| 8 并发错误数 | 0 | 0 | 一致 |  |
| 相同请求 input_tokens 漂移 | [8, 17] | [17] | 偏离 | 多账号/多版本提示词轮询 |
| 2500 token 长输出不断流 | True | True | 一致 |  |
| 首字节 TTFB(s) | 3.19 | 0.73 | 偏离 | 慢337% |
| 首个正文 token TTFT(s) | 3.19 | 0.73 | 偏离 | 慢337% |
| 短请求 p50 延迟(s) | 2.81 | 1.14 | 偏离 | 慢146% |
| 8并发 p50 延迟(s) | 5.3 | 1.4 | 偏离 | 慢279% |
| 生成速度 tok/s | 59.8 (56.8-59.9) | 61.0 (58.9-62.7) | 一致 | 慢2% |
| 流式粒度 tok/chunk | 1.0 | 1.0 | 一致 | >3倍官方 = 中转缓冲后再切块(假流式) |

## teamo-glm-anthropic / glm-5.3-flash (anthropic) → ❌ 模型身份与官方不一致（知识/自报/思考/分词证据）

偏离项 8（身份 2｜智力 0｜协议 2｜上下文 0｜运营 3）: 泄露的隐藏系统提示, 参数校验与官方逐项一致率, 英文 +1261 o200k tok 的 usage 增量, 中文 +2040 o200k tok 的 usage 增量, 知识阶梯逐题分类一致,   ↳ xhard 平均耗时(s),   ↳ xhard_off 平均耗时(s), 8并发 p50 延迟(s)

| 维度 | 中转站 | 官方 | 判定 | 说明 |
|---|---|---|---|---|
| 响应 id 格式 | msg_202609151626127c6c4e004924481e | msg_20260915162609446452a7f2b04362 | 一致 | 官方=14位时间戳+18位hex；chatcmpl-/自造id=中转层重新生成 |
| usage 字段集合 | cache_read_input_tokens,input_tokens,output_tokens,server_tool_use,ser | cache_read_input_tokens,input_tokens,output_tokens,server_tool_use,ser | 一致 |  |
| 响应顶层字段 | content,id,model,role,stop_reason,stop_sequence,type,usage | content,id,model,role,stop_reason,stop_sequence,type,usage | 一致 | 官方带 request_id、无 system_fingerprint/service_tier |
| 模型名回显 | glm-5.3-flash | glm-5.3-flash | 一致 |  |
| thinking signature 形态 | 24hex | 24hex | 一致 | 官方=24位hex |
| 流式 ping 事件 | 1 | 1 | 一致 |  |
| 工具调用 id 格式(e_sync) | True | True | 一致 | 官方 openai=call_+有符号整数 / anthropic=call_+24hex |
| 工具调用 id 格式(stream) | True | True | 一致 | 官方 openai=call_+有符号整数 / anthropic=call_+24hex |
| 隐藏提示注入(多算的input tokens) | 12 | 12 | 一致 | 差值>8 = 上游加了系统提示或 usage 被改 |
| 泄露的隐藏系统提示 | I can't share the contents of my system prompt or instructions. I'm ha |  | 偏离 |  |
| 自报厂商 | z.ai | z.ai | 一致 |  |
| 参数校验与官方逐项一致率 | 8/10 | - | 偏离 | disabled_xhigh:200(官方400) effort_xhigh:200(官方400) |
| stop 序列生效 | False | False | 一致 |  |
| max_tokens 生效 | True | True | 一致 |  |
| 20轮历史记忆 | True | True | 一致 |  |
| 60k 下 system 规则仍遵守 | True | True | 一致 |  |
| 英文 +1261 o200k tok 的 usage 增量 | 1 | -8 | 偏离 | 偏差>2% = usage 不是 GLM 分词器算的(估算/伪造) |
| 中文 +2040 o200k tok 的 usage 增量 | 19 | 1610 | 偏离 | 偏差>2% = usage 不是 GLM 分词器算的(估算/伪造) |
| 知识阶梯前沿 | 2025-12 | 2025-11 | 一致 | 相差≥2个月才算偏离（temperature=1 抽样本身有±1个月噪声）；早于官方 = 更老的模型 |
| 开放式近期知识前沿 | 2026-01 | 2026-01 | 一致 |  |
| 知识阶梯逐题分类一致 | 19/24 | - | 偏离 | K00:UNKNOWN(官方CORRECT) K05:CORRECT(官方UNKNOWN) K06:CORRECT(官方UNKNOWN) K09:CORRECT(官方UNKNOWN) K14:UNKNOWN(官方WRONG) |
| 同题4次年代一致(无混合池) | ['2025-05', '2013-03', '2025-05', '2013-03'] | ['2013-03', '2025-05', '2025-05', '2025-05'] | 一致 | 官方 GLM 本身对'现任教宗'就答不稳(方济各/良十四世各半)，所以只有官方稳定而中转不稳才算偏离 |
| 智力 reason | 11/12 | 12/12 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ reason 平均耗时(s) | 27.9 | 38.6 | 一致 | 慢于官方2.5倍以上 |
| 智力 reason_off | 11/12 | 8/12 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ reason_off 平均耗时(s) | 34.4 | 29.9 | 一致 | 慢于官方2.5倍以上 |
| 智力 hard | 5/6 | 5/6 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ hard 平均耗时(s) | 60.4 | 95.4 | 一致 | 慢于官方2.5倍以上 |
| 智力 hard_off | 5/6 | 4/6 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ hard_off 平均耗时(s) | 40.6 | 51.1 | 一致 | 慢于官方2.5倍以上 |
| 智力 xhard | 14/14 | 3/3 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ xhard 平均耗时(s) | 57.2 | 12.6 | 偏离 | 慢于官方2.5倍以上 |
| 智力 xhard_off | 7/13 | 2/4 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ xhard_off 平均耗时(s) | 40.4 | 7.1 | 偏离 | 慢于官方2.5倍以上 |
| 长上下文 20k 三针召回 | 3/3 | 3/3 | 一致 | 耗时 5.4s vs 官方 13.7s ; usage比 1.063 vs 0.002 |
| 长上下文 60k 三针召回 | 3/3 | 3/3 | 一致 | 耗时 4.2s vs 官方 2.2s ; usage比 0.001 vs 0.001 |
| 长上下文 130k 三针召回 | 3/3 | 3/3 | 一致 | 耗时 10.2s vs 官方 2.2s ; usage比 0.0 vs 0.0 |
| 前缀缓存命中(cached_tokens 序列) | [0, 5056, 5056] | [5056, 5056, 5056] | 一致 | 官方隐式缓存第2次即命中；不命中 = 账号池轮询/缓存层被剥离(你付全价) |
| 顺序调用错误/空回复 | 0/0 of 8 | 0/0 of 8 | 一致 |  |
| 8 并发错误数 | 0 | 0 | 一致 |  |
| 2500 token 长输出不断流 | True | True | 一致 |  |
| 首字节 TTFB(s) | 2.9 | 2.68 | 一致 | 慢8% |
| 首个正文 token TTFT(s) | 2.94 | 2.68 | 一致 | 慢10% |
| 短请求 p50 延迟(s) | 2.48 | 1.43 | 一致 | 慢73% |
| 8并发 p50 延迟(s) | 4.44 | 1.38 | 偏离 | 慢222% |
| 生成速度 tok/s | 56.8 (55.1-63.8) | 80.0 (76.3-84.4) | 一致 | 慢29% |
| 流式粒度 tok/chunk | 1.0 | 1.0 | 一致 | >3倍官方 = 中转缓冲后再切块(假流式) |

## v129-K1 / glm-5.3-flash (openai) → ⚠️ 模型层有偏离，需人工复核

偏离项 9（身份 1｜智力 0｜协议 4｜上下文 0｜运营 4）: usage 字段集合, 响应顶层字段, 泄露的隐藏系统提示, 参数校验与官方逐项一致率, 开放式近期知识前沿, 顺序调用错误/空回复, 首字节 TTFB(s), 首个正文 token TTFT(s), 8并发 p50 延迟(s)

| 维度 | 中转站 | 官方 | 判定 | 说明 |
|---|---|---|---|---|
| 响应 id 格式 | 7a46880dd9ba13849e8008ee368c6d00 | 20260915162609f1523f2bb6bb4858 | 一致 | 官方=14位时间戳+18位hex；chatcmpl-/自造id=中转层重新生成 |
| usage 字段集合 | cached_tokens,completion_tokens,completion_tokens_details,prompt_token | completion_tokens,completion_tokens_details,prompt_tokens,prompt_token | 偏离 |  |
| 响应顶层字段 | choices,created,id,model,object,usage | choices,created,id,model,object,request_id,usage | 偏离 | 官方带 request_id、无 system_fingerprint/service_tier |
| 模型名回显 | glm-5.3-flash | glm-5.3-flash | 一致 |  |
| 默认返回 reasoning_content | True | True | 一致 | GLM-5.3 永远思考；没有=思考被剥离或换了模型 |
| 流式 obfuscation 字段 | False | False | 一致 | 官方无此字段；有=经过 OpenAI 原生/new-api 改写 |
| 工具调用 id 格式(e_sync) | True | True | 一致 | 官方 openai=call_+有符号整数 / anthropic=call_+24hex |
| 工具调用 id 格式(stream) | True | True | 一致 | 官方 openai=call_+有符号整数 / anthropic=call_+24hex |
| 隐藏提示注入(多算的input tokens) | 12 | 12 | 一致 | 差值>8 = 上游加了系统提示或 usage 被改 |
| 泄露的隐藏系统提示 | I can't share the verbatim text of my system prompt or instructions, a | I can't quote my system prompt or developer instructions verbatim, as  | 偏离 |  |
| 自报厂商 | z.ai | z.ai | 一致 |  |
| 参数校验与官方逐项一致率 | 8/12 | - | 偏离 | effort_invalid:200(官方400) effort_none:200(官方400) thinking_disabled:200(官方400) bad_model:503(官方400) |
| stop 序列生效 | False | False | 一致 |  |
| max_tokens 生效 | True | True | 一致 |  |
| 20轮历史记忆 | True | True | 一致 |  |
| 60k 下 system 规则仍遵守 | True | True | 一致 |  |
| 英文 +1261 o200k tok 的 usage 增量 | 1720 | 1720 | 一致 | 偏差>2% = usage 不是 GLM 分词器算的(估算/伪造) |
| 中文 +2040 o200k tok 的 usage 增量 | 1610 | 1610 | 一致 | 偏差>2% = usage 不是 GLM 分词器算的(估算/伪造) |
| reasoning_effort 生效(low→max 思考token增长) | 2→64 | 7→23 | 一致 |  |
| 知识阶梯前沿 | 2025-12 | 2025-12 | 一致 | 相差≥2个月才算偏离（temperature=1 抽样本身有±1个月噪声）；早于官方 = 更老的模型 |
| 开放式近期知识前沿 | 2026-01 | 2025-05 | 偏离 |  |
| 知识阶梯逐题分类一致 | 24/24 | - | 一致 |  |
| 同题4次年代一致(无混合池) | ['2025-05', '2013-03', '2025-05', '2013-03'] | ['2025-05', '2013-03', '2025-05', '2025-05'] | 一致 | 官方 GLM 本身对'现任教宗'就答不稳(方济各/良十四世各半)，所以只有官方稳定而中转不稳才算偏离 |
| 智力 reason | 12/12 | 12/12 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ reason 平均耗时(s) | 30.6 | 21.0 | 一致 | 慢于官方2.5倍以上 |
| 智力 reason_off | 8/12 | 9/12 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ reason_off 平均耗时(s) | 21.6 | 25.6 | 一致 | 慢于官方2.5倍以上 |
| 智力 hard | 5/6 | 5/6 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ hard 平均耗时(s) | 84.9 | 65.3 | 一致 | 慢于官方2.5倍以上 |
| 智力 hard_off | 5/5 | 6/6 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ hard_off 平均耗时(s) | 68.6 | 81.9 | 一致 | 慢于官方2.5倍以上 |
| 智力 xhard | 12/12 | 6/6 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ xhard 平均耗时(s) | 55.8 | 22.6 | 一致 | 慢于官方2.5倍以上 |
| 智力 xhard_off | 8/14 | 3/8 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ xhard_off 平均耗时(s) | 38.3 | 42.3 | 一致 | 慢于官方2.5倍以上 |
| 长上下文 20k 三针召回 | 3/3 | 3/3 | 一致 | 耗时 3.0s vs 官方 1.5s ; usage比 1.063 vs 1.063 |
| 长上下文 60k 三针召回 | 3/3 | 3/3 | 一致 | 耗时 4.0s vs 官方 3.5s ; usage比 1.069 vs 1.069 |
| 长上下文 130k 三针召回 | 3/3 | 3/3 | 一致 | 耗时 4.5s vs 官方 4.4s ; usage比 1.069 vs 1.069 |
| 长上下文 230k 三针召回 | 3/3 | 3/3 | 一致 | 耗时 6.4s vs 官方 6.0s ; usage比 1.066 vs 1.066 |
| 前缀缓存命中(cached_tokens 序列) | [5056, 5056, 5056] | [0, 5056, 5056] | 一致 | 官方隐式缓存第2次即命中；不命中 = 账号池轮询/缓存层被剥离(你付全价) |
| 顺序调用错误/空回复 | 0/1 of 8 | 0/2 of 8 | 偏离 |  |
| 8 并发错误数 | 0 | 0 | 一致 |  |
| 2500 token 长输出不断流 | True | True | 一致 |  |
| 首字节 TTFB(s) | 1.77 | 0.73 | 偏离 | 慢142% |
| 首个正文 token TTFT(s) | 1.77 | 0.73 | 偏离 | 慢142% |
| 短请求 p50 延迟(s) | 1.99 | 1.14 | 一致 | 慢75% |
| 8并发 p50 延迟(s) | 3.97 | 1.4 | 偏离 | 慢184% |
| 生成速度 tok/s | 63.6 (62.7-77.1) | 61.0 (58.9-62.7) | 一致 | 快4% |
| 流式粒度 tok/chunk | 1.0 | 1.0 | 一致 | >3倍官方 = 中转缓冲后再切块(假流式) |

## v129-K1-anthropic / glm-5.3-flash (anthropic) → ⚠️ 模型层有偏离，需人工复核

偏离项 9（身份 1｜智力 0｜协议 4｜上下文 0｜运营 4）: usage 字段集合, 响应顶层字段, 流式 ping 事件, 参数校验与官方逐项一致率, 英文 +1261 o200k tok 的 usage 增量,   ↳ xhard 平均耗时(s),   ↳ xhard_off 平均耗时(s), 顺序调用错误/空回复, 首个正文 token TTFT(s)

| 维度 | 中转站 | 官方 | 判定 | 说明 |
|---|---|---|---|---|
| 响应 id 格式 | 9b754e9bfe92c69e121636cf6dffc36d | msg_20260915162609446452a7f2b04362 | 一致 | 官方=14位时间戳+18位hex；chatcmpl-/自造id=中转层重新生成 |
| usage 字段集合 | billing_usage,cache_creation_input_tokens,cache_read_input_tokens,clau | cache_read_input_tokens,input_tokens,output_tokens,server_tool_use,ser | 偏离 |  |
| 响应顶层字段 | content,id,model,role,stop_reason,type,usage | content,id,model,role,stop_reason,stop_sequence,type,usage | 偏离 | 官方带 request_id、无 system_fingerprint/service_tier |
| 模型名回显 | glm-5.3-flash | glm-5.3-flash | 一致 |  |
| thinking signature 形态 | 未测 | 24hex | — | 该轮未覆盖此项 |
| 流式 ping 事件 | 0 | 1 | 偏离 |  |
| 工具调用 id 格式(e_sync) | True | True | 一致 | 官方 openai=call_+有符号整数 / anthropic=call_+24hex |
| 工具调用 id 格式(stream) | True | True | 一致 | 官方 openai=call_+有符号整数 / anthropic=call_+24hex |
| 隐藏提示注入(多算的input tokens) | 12 | 12 | 一致 | 差值>8 = 上游加了系统提示或 usage 被改 |
| 自报厂商 | z.ai | z.ai | 一致 |  |
| 参数校验与官方逐项一致率 | 8/10 | - | 偏离 | disabled_xhigh:200(官方400) effort_xhigh:200(官方400) |
| stop 序列生效 | False | False | 一致 |  |
| max_tokens 生效 | True | True | 一致 |  |
| 20轮历史记忆 | True | True | 一致 |  |
| 60k 下 system 规则仍遵守 | 未测 | True | — | 该轮未覆盖此项 |
| 英文 +1261 o200k tok 的 usage 增量 | 1720 | -8 | 偏离 | 偏差>2% = usage 不是 GLM 分词器算的(估算/伪造) |
| 中文 +2040 o200k tok 的 usage 增量 | 1610 | 1610 | 一致 | 偏差>2% = usage 不是 GLM 分词器算的(估算/伪造) |
| 知识阶梯前沿 | 2025-11 | 2025-11 | 一致 | 相差≥2个月才算偏离（temperature=1 抽样本身有±1个月噪声）；早于官方 = 更老的模型 |
| 开放式近期知识前沿 | 2026-01 | 2026-01 | 一致 |  |
| 知识阶梯逐题分类一致 | 22/24 | - | 一致 | K03:UNKNOWN(官方CORRECT) K14:UNKNOWN(官方WRONG) |
| 同题4次年代一致(无混合池) | ['2013-03', '2025-05', '2025-05', '2025-05'] | ['2013-03', '2025-05', '2025-05', '2025-05'] | 一致 | 官方 GLM 本身对'现任教宗'就答不稳(方济各/良十四世各半)，所以只有官方稳定而中转不稳才算偏离 |
| 智力 reason | 10/12 | 12/12 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ reason 平均耗时(s) | 27.7 | 38.6 | 一致 | 慢于官方2.5倍以上 |
| 智力 reason_off | 11/12 | 8/12 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ reason_off 平均耗时(s) | 27.7 | 29.9 | 一致 | 慢于官方2.5倍以上 |
| 智力 hard | 6/6 | 5/6 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ hard 平均耗时(s) | 63.9 | 95.4 | 一致 | 慢于官方2.5倍以上 |
| 智力 hard_off | 5/6 | 4/6 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ hard_off 平均耗时(s) | 45.3 | 51.1 | 一致 | 慢于官方2.5倍以上 |
| 智力 xhard | 6/7 | 3/3 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ xhard 平均耗时(s) | 58.9 | 12.6 | 偏离 | 慢于官方2.5倍以上 |
| 智力 xhard_off | 5/5 | 2/4 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ xhard_off 平均耗时(s) | 79.6 | 7.1 | 偏离 | 慢于官方2.5倍以上 |
| 长上下文 20k 三针召回 | 3/3 | 3/3 | 一致 | 耗时 4.0s vs 官方 13.7s ; usage比 1.063 vs 0.002 |
| 长上下文 60k 三针召回 | 未测 | 3/3 | — | 该轮未覆盖此项 |
| 长上下文 130k 三针召回 | 未测 | 3/3 | — | 该轮未覆盖此项 |
| 前缀缓存命中(cached_tokens 序列) | [0, 5056] | [5056, 5056, 5056] | 一致 | 官方隐式缓存第2次即命中；不命中 = 账号池轮询/缓存层被剥离(你付全价) |
| 顺序调用错误/空回复 | 0/5 of 5 | 0/0 of 8 | 偏离 |  |
| 8 并发错误数 | 未测 | 0 | — | 该轮未覆盖此项 |
| 2500 token 长输出不断流 | 未测 | True | — | 该轮未覆盖此项 |
| 首字节 TTFB(s) | 1.44 | 2.68 | 一致 | 快46% |
| 首个正文 token TTFT(s) | 16.02 | 2.68 | 偏离 | 慢498% |
| 短请求 p50 延迟(s) | 1.66 | 1.43 | 一致 | 慢16% |
| 生成速度 tok/s | 192.1 (192.1-192.1) | 80.0 (76.3-84.4) | 一致 | 快140% |
| 流式粒度 tok/chunk | 0.3 | 1.0 | 一致 | >3倍官方 = 中转缓冲后再切块(假流式) |

## v129-K1-proxy / glm-5.3-flash (anthropic) → ❌ 模型身份与官方不一致（知识/自报/思考/分词证据）

偏离项 7（身份 2｜智力 0｜协议 4｜上下文 0｜运营 0）: usage 字段集合, 泄露的隐藏系统提示, 参数校验与官方逐项一致率, stop 序列生效, 英文 +1261 o200k tok 的 usage 增量, 开放式近期知识前沿, 短请求 p50 延迟(s)

| 维度 | 中转站 | 官方 | 判定 | 说明 |
|---|---|---|---|---|
| 响应 id 格式 | msg_20260910085956961491de8fff0ed7 | msg_20260915162609446452a7f2b04362 | 一致 | 官方=14位时间戳+18位hex；chatcmpl-/自造id=中转层重新生成 |
| usage 字段集合 | cache_creation_input_tokens,cache_read_input_tokens,input_tokens,outpu | cache_read_input_tokens,input_tokens,output_tokens,server_tool_use,ser | 偏离 |  |
| 响应顶层字段 | content,id,model,role,stop_reason,stop_sequence,type,usage | content,id,model,role,stop_reason,stop_sequence,type,usage | 一致 | 官方带 request_id、无 system_fingerprint/service_tier |
| 模型名回显 | glm-5.3-flash | glm-5.3-flash | 一致 |  |
| thinking signature 形态 | 24hex | 24hex | 一致 | 官方=24位hex |
| 流式 ping 事件 | 1 | 1 | 一致 |  |
| 工具调用 id 格式(e_sync) | True | True | 一致 | 官方 openai=call_+有符号整数 / anthropic=call_+24hex |
| 工具调用 id 格式(stream) | True | True | 一致 | 官方 openai=call_+有符号整数 / anthropic=call_+24hex |
| 隐藏提示注入(多算的input tokens) | 12 | 12 | 一致 | 差值>8 = 上游加了系统提示或 usage 被改 |
| 泄露的隐藏系统提示 | I can't quote my system prompt or developer instructions verbatim, so  |  | 偏离 |  |
| 自报厂商 | z.ai | z.ai | 一致 |  |
| 参数校验与官方逐项一致率 | 8/10 | - | 偏离 | disabled_xhigh:200(官方400) effort_xhigh:200(官方400) |
| stop 序列生效 | True | False | 偏离 |  |
| max_tokens 生效 | True | True | 一致 |  |
| 20轮历史记忆 | True | True | 一致 |  |
| 60k 下 system 规则仍遵守 | 未测 | True | — | 该轮未覆盖此项 |
| 英文 +1261 o200k tok 的 usage 增量 | 1720 | -8 | 偏离 | 偏差>2% = usage 不是 GLM 分词器算的(估算/伪造) |
| 中文 +2040 o200k tok 的 usage 增量 | 1610 | 1610 | 一致 | 偏差>2% = usage 不是 GLM 分词器算的(估算/伪造) |
| 知识阶梯前沿 | 2025-12 | 2025-11 | 一致 | 相差≥2个月才算偏离（temperature=1 抽样本身有±1个月噪声）；早于官方 = 更老的模型 |
| 开放式近期知识前沿 | 2025-09 | 2026-01 | 偏离 |  |
| 知识阶梯逐题分类一致 | 21/24 | - | 一致 | K06:CORRECT(官方UNKNOWN) K09:CORRECT(官方UNKNOWN) K14:UNKNOWN(官方WRONG) |
| 同题4次年代一致(无混合池) | ['2013-03', '2025-05', '2013-03', '2013-03'] | ['2013-03', '2025-05', '2025-05', '2025-05'] | 一致 | 官方 GLM 本身对'现任教宗'就答不稳(方济各/良十四世各半)，所以只有官方稳定而中转不稳才算偏离 |
| 智力 reason | 12/12 | 12/12 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ reason 平均耗时(s) | 28.8 | 38.6 | 一致 | 慢于官方2.5倍以上 |
| 长上下文 20k 三针召回 | 3/3 | 3/3 | 一致 | 耗时 9.2s vs 官方 13.7s ; usage比 1.063 vs 0.002 |
| 长上下文 60k 三针召回 | 未测 | 3/3 | — | 该轮未覆盖此项 |
| 长上下文 130k 三针召回 | 未测 | 3/3 | — | 该轮未覆盖此项 |
| 前缀缓存命中(cached_tokens 序列) | [0, 5056] | [5056, 5056, 5056] | 一致 | 官方隐式缓存第2次即命中；不命中 = 账号池轮询/缓存层被剥离(你付全价) |
| 顺序调用错误/空回复 | 0/0 of 5 | 0/0 of 8 | 一致 |  |
| 8 并发错误数 | 未测 | 0 | — | 该轮未覆盖此项 |
| 2500 token 长输出不断流 | 未测 | True | — | 该轮未覆盖此项 |
| 首字节 TTFB(s) | 0.01 | 2.68 | 一致 | 快100% |
| 首个正文 token TTFT(s) | 4.12 | 2.68 | 一致 | 慢54% |
| 短请求 p50 延迟(s) | 3.96 | 1.43 | 偏离 | 慢177% |
| 生成速度 tok/s | 63.1 (63.1-63.1) | 80.0 (76.3-84.4) | 一致 | 慢21% |
| 流式粒度 tok/chunk | 1.0 | 1.0 | 一致 | >3倍官方 = 中转缓冲后再切块(假流式) |

## v129-K2 / glm-5.3-flash (openai) → ⚠️ 模型层有偏离，需人工复核

偏离项 9（身份 1｜智力 1｜协议 4｜上下文 0｜运营 3）: usage 字段集合, 响应顶层字段, 泄露的隐藏系统提示, 参数校验与官方逐项一致率, 开放式近期知识前沿, 智力 hard_off, 首字节 TTFB(s), 首个正文 token TTFT(s), 8并发 p50 延迟(s)

| 维度 | 中转站 | 官方 | 判定 | 说明 |
|---|---|---|---|---|
| 响应 id 格式 | 74475ddef9e20ba3e6cf1e1fbd41dceb | 20260915162609f1523f2bb6bb4858 | 一致 | 官方=14位时间戳+18位hex；chatcmpl-/自造id=中转层重新生成 |
| usage 字段集合 | cached_tokens,completion_tokens,completion_tokens_details,prompt_token | completion_tokens,completion_tokens_details,prompt_tokens,prompt_token | 偏离 |  |
| 响应顶层字段 | choices,created,id,model,object,usage | choices,created,id,model,object,request_id,usage | 偏离 | 官方带 request_id、无 system_fingerprint/service_tier |
| 模型名回显 | glm-5.3-flash | glm-5.3-flash | 一致 |  |
| 默认返回 reasoning_content | True | True | 一致 | GLM-5.3 永远思考；没有=思考被剥离或换了模型 |
| 流式 obfuscation 字段 | False | False | 一致 | 官方无此字段；有=经过 OpenAI 原生/new-api 改写 |
| 工具调用 id 格式(e_sync) | True | True | 一致 | 官方 openai=call_+有符号整数 / anthropic=call_+24hex |
| 工具调用 id 格式(stream) | True | True | 一致 | 官方 openai=call_+有符号整数 / anthropic=call_+24hex |
| 隐藏提示注入(多算的input tokens) | 12 | 12 | 一致 | 差值>8 = 上游加了系统提示或 usage 被改 |
| 泄露的隐藏系统提示 | I can't reproduce my instructions verbatim. My system prompt contains  | I can't quote my system prompt or developer instructions verbatim, as  | 偏离 |  |
| 自报厂商 | i was trained by z.ai. as a glm large la | z.ai | 一致 |  |
| 参数校验与官方逐项一致率 | 8/12 | - | 偏离 | effort_invalid:200(官方400) effort_none:200(官方400) thinking_disabled:200(官方400) bad_model:503(官方400) |
| stop 序列生效 | False | False | 一致 |  |
| max_tokens 生效 | True | True | 一致 |  |
| 20轮历史记忆 | True | True | 一致 |  |
| 60k 下 system 规则仍遵守 | True | True | 一致 |  |
| 英文 +1261 o200k tok 的 usage 增量 | 1720 | 1720 | 一致 | 偏差>2% = usage 不是 GLM 分词器算的(估算/伪造) |
| 中文 +2040 o200k tok 的 usage 增量 | 1610 | 1610 | 一致 | 偏差>2% = usage 不是 GLM 分词器算的(估算/伪造) |
| reasoning_effort 生效(low→max 思考token增长) | 21→33 | 7→23 | 一致 |  |
| 知识阶梯前沿 | 2025-11 | 2025-12 | 一致 | 相差≥2个月才算偏离（temperature=1 抽样本身有±1个月噪声）；早于官方 = 更老的模型 |
| 开放式近期知识前沿 | 2026-01 | 2025-05 | 偏离 |  |
| 知识阶梯逐题分类一致 | 22/24 | - | 一致 | K04:CORRECT(官方UNKNOWN) K09:UNKNOWN(官方CORRECT) |
| 同题4次年代一致(无混合池) | ['2013-03', '2025-05', '2025-05', '2013-03'] | ['2025-05', '2013-03', '2025-05', '2025-05'] | 一致 | 官方 GLM 本身对'现任教宗'就答不稳(方济各/良十四世各半)，所以只有官方稳定而中转不稳才算偏离 |
| 智力 reason | 12/12 | 12/12 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ reason 平均耗时(s) | 34.9 | 21.0 | 一致 | 慢于官方2.5倍以上 |
| 智力 reason_off | 8/12 | 9/12 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ reason_off 平均耗时(s) | 20.6 | 25.6 | 一致 | 慢于官方2.5倍以上 |
| 智力 hard | 5/6 | 5/6 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ hard 平均耗时(s) | 44.6 | 65.3 | 一致 | 慢于官方2.5倍以上 |
| 智力 hard_off | 3/6 | 6/6 | 偏离 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ hard_off 平均耗时(s) | 58.2 | 81.9 | 一致 | 慢于官方2.5倍以上 |
| 智力 xhard | 9/12 | 6/6 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ xhard 平均耗时(s) | 46.0 | 22.6 | 一致 | 慢于官方2.5倍以上 |
| 智力 xhard_off | 5/13 | 3/8 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ xhard_off 平均耗时(s) | 49.8 | 42.3 | 一致 | 慢于官方2.5倍以上 |
| 长上下文 20k 三针召回 | 3/3 | 3/3 | 一致 | 耗时 3.1s vs 官方 1.5s ; usage比 1.063 vs 1.063 |
| 长上下文 60k 三针召回 | 3/3 | 3/3 | 一致 | 耗时 5.0s vs 官方 3.5s ; usage比 1.069 vs 1.069 |
| 长上下文 130k 三针召回 | 3/3 | 3/3 | 一致 | 耗时 5.4s vs 官方 4.4s ; usage比 1.069 vs 1.069 |
| 长上下文 230k 三针召回 | 3/3 | 3/3 | 一致 | 耗时 12.0s vs 官方 6.0s ; usage比 1.066 vs 1.066 |
| 前缀缓存命中(cached_tokens 序列) | [5056, 5056, 5056] | [0, 5056, 5056] | 一致 | 官方隐式缓存第2次即命中；不命中 = 账号池轮询/缓存层被剥离(你付全价) |
| 顺序调用错误/空回复 | 0/0 of 8 | 0/2 of 8 | 一致 |  |
| 8 并发错误数 | 0 | 0 | 一致 |  |
| 2500 token 长输出不断流 | True | True | 一致 |  |
| 首字节 TTFB(s) | 1.88 | 0.73 | 偏离 | 慢158% |
| 首个正文 token TTFT(s) | 1.88 | 0.73 | 偏离 | 慢158% |
| 短请求 p50 延迟(s) | 2.02 | 1.14 | 一致 | 慢77% |
| 8并发 p50 延迟(s) | 4.09 | 1.4 | 偏离 | 慢192% |
| 生成速度 tok/s | 66.1 (38.8-69.8) | 61.0 (58.9-62.7) | 一致 | 快8% |
| 流式粒度 tok/chunk | 1.0 | 1.0 | 一致 | >3倍官方 = 中转缓冲后再切块(假流式) |

## v129-K3 / glm-5.3-flash (openai) → ⛔ 不可用（该分组没有此模型渠道 / 全部失败）

偏离项 4（身份 0｜智力 0｜协议 3｜上下文 0｜运营 1）: usage 字段集合, 响应顶层字段, reasoning_effort 生效(low→max 思考token增长), 前缀缓存命中(cached_tokens 序列)

| 维度 | 中转站 | 官方 | 判定 | 说明 |
|---|---|---|---|---|
| 响应 id 格式 |  | 20260915162609f1523f2bb6bb4858 | 一致 | 官方=14位时间戳+18位hex；chatcmpl-/自造id=中转层重新生成 |
| usage 字段集合 |  | completion_tokens,completion_tokens_details,prompt_tokens,prompt_token | 偏离 |  |
| 响应顶层字段 |  | choices,created,id,model,object,request_id,usage | 偏离 | 官方带 request_id、无 system_fingerprint/service_tier |
| 模型名回显 | 未测 | glm-5.3-flash | — | 该轮未覆盖此项 |
| 默认返回 reasoning_content | 未测 | True | — | 该轮未覆盖此项 |
| 流式 obfuscation 字段 | 未测 | False | — | 该轮未覆盖此项 |
| 工具调用 id 格式(e_sync) | 未测 | True | — | 该轮未覆盖此项 |
| 工具调用 id 格式(stream) | 未测 | True | — | 该轮未覆盖此项 |
| 隐藏提示注入(多算的input tokens) | 未测 | 12 | — | 该轮未覆盖此项 |
| 自报厂商 | 未测 | z.ai | — | 该轮未覆盖此项 |
| stop 序列生效 | 未测 | False | — | 该轮未覆盖此项 |
| max_tokens 生效 | 未测 | True | — | 该轮未覆盖此项 |
| 20轮历史记忆 | 未测 | True | — | 该轮未覆盖此项 |
| 60k 下 system 规则仍遵守 | 未测 | True | — | 该轮未覆盖此项 |
| reasoning_effort 生效(low→max 思考token增长) | None→None | 7→23 | 偏离 |  |
| 知识阶梯前沿 | 未测 | 2025-12 | — | 该轮未覆盖此项 |
| 开放式近期知识前沿 | 未测 | 2025-05 | — | 该轮未覆盖此项 |
| 同题4次年代一致(无混合池) | 未测 | ['2025-05', '2013-03', '2025-05', '2025-05'] | — | 该轮未覆盖此项 |
| 长上下文 20k 三针召回 | 未测 | 3/3 | — | 该轮未覆盖此项 |
| 长上下文 60k 三针召回 | 未测 | 3/3 | — | 该轮未覆盖此项 |
| 长上下文 130k 三针召回 | 未测 | 3/3 | — | 该轮未覆盖此项 |
| 长上下文 230k 三针召回 | 未测 | 3/3 | — | 该轮未覆盖此项 |
| 前缀缓存命中(cached_tokens 序列) | [] | [0, 5056, 5056] | 偏离 | 官方隐式缓存第2次即命中；不命中 = 账号池轮询/缓存层被剥离(你付全价) |
| 顺序调用错误/空回复 | None/None of None | 0/2 of 8 | 一致 |  |
| 8 并发错误数 | 未测 | 0 | — | 该轮未覆盖此项 |
| 2500 token 长输出不断流 | 未测 | True | — | 该轮未覆盖此项 |
| 流式粒度 tok/chunk | 未测 | 1.0 | — | 该轮未覆盖此项 |

## v129-K4 / glm-5.3-flash (openai) → ⛔ 不可用（该分组没有此模型渠道 / 全部失败）

偏离项 4（身份 0｜智力 0｜协议 3｜上下文 0｜运营 1）: usage 字段集合, 响应顶层字段, reasoning_effort 生效(low→max 思考token增长), 前缀缓存命中(cached_tokens 序列)

| 维度 | 中转站 | 官方 | 判定 | 说明 |
|---|---|---|---|---|
| 响应 id 格式 |  | 20260915162609f1523f2bb6bb4858 | 一致 | 官方=14位时间戳+18位hex；chatcmpl-/自造id=中转层重新生成 |
| usage 字段集合 |  | completion_tokens,completion_tokens_details,prompt_tokens,prompt_token | 偏离 |  |
| 响应顶层字段 |  | choices,created,id,model,object,request_id,usage | 偏离 | 官方带 request_id、无 system_fingerprint/service_tier |
| 模型名回显 | 未测 | glm-5.3-flash | — | 该轮未覆盖此项 |
| 默认返回 reasoning_content | 未测 | True | — | 该轮未覆盖此项 |
| 流式 obfuscation 字段 | 未测 | False | — | 该轮未覆盖此项 |
| 工具调用 id 格式(e_sync) | 未测 | True | — | 该轮未覆盖此项 |
| 工具调用 id 格式(stream) | 未测 | True | — | 该轮未覆盖此项 |
| 隐藏提示注入(多算的input tokens) | 未测 | 12 | — | 该轮未覆盖此项 |
| 自报厂商 | 未测 | z.ai | — | 该轮未覆盖此项 |
| stop 序列生效 | 未测 | False | — | 该轮未覆盖此项 |
| max_tokens 生效 | 未测 | True | — | 该轮未覆盖此项 |
| 20轮历史记忆 | 未测 | True | — | 该轮未覆盖此项 |
| 60k 下 system 规则仍遵守 | 未测 | True | — | 该轮未覆盖此项 |
| reasoning_effort 生效(low→max 思考token增长) | None→None | 7→23 | 偏离 |  |
| 知识阶梯前沿 | 未测 | 2025-12 | — | 该轮未覆盖此项 |
| 开放式近期知识前沿 | 未测 | 2025-05 | — | 该轮未覆盖此项 |
| 同题4次年代一致(无混合池) | 未测 | ['2025-05', '2013-03', '2025-05', '2025-05'] | — | 该轮未覆盖此项 |
| 长上下文 20k 三针召回 | 未测 | 3/3 | — | 该轮未覆盖此项 |
| 长上下文 60k 三针召回 | 未测 | 3/3 | — | 该轮未覆盖此项 |
| 长上下文 130k 三针召回 | 未测 | 3/3 | — | 该轮未覆盖此项 |
| 长上下文 230k 三针召回 | 未测 | 3/3 | — | 该轮未覆盖此项 |
| 前缀缓存命中(cached_tokens 序列) | [] | [0, 5056, 5056] | 偏离 | 官方隐式缓存第2次即命中；不命中 = 账号池轮询/缓存层被剥离(你付全价) |
| 顺序调用错误/空回复 | None/None of None | 0/2 of 8 | 一致 |  |
| 8 并发错误数 | 未测 | 0 | — | 该轮未覆盖此项 |
| 2500 token 长输出不断流 | 未测 | True | — | 该轮未覆盖此项 |
| 流式粒度 tok/chunk | 未测 | 1.0 | — | 该轮未覆盖此项 |

## yjapi-glm / glm-5.3-flash (openai) → ⚠️ 模型层有偏离，需人工复核

偏离项 13（身份 1｜智力 0｜协议 3｜上下文 6｜运营 3）: 响应顶层字段, 泄露的隐藏系统提示, 参数校验与官方逐项一致率, 20轮历史记忆, 60k 下 system 规则仍遵守, 开放式近期知识前沿, 长上下文 20k 三针召回, 长上下文 60k 三针召回, 长上下文 130k 三针召回, 长上下文 230k 三针召回, 前缀缓存命中(cached_tokens 序列), 顺序调用错误/空回复, 8 并发错误数

| 维度 | 中转站 | 官方 | 判定 | 说明 |
|---|---|---|---|---|
| 响应 id 格式 | 4a56a0c0-ef39-4459-81f1-03455a0aa2 | 20260915162609f1523f2bb6bb4858 | 一致 | 官方=14位时间戳+18位hex；chatcmpl-/自造id=中转层重新生成 |
| usage 字段集合 | completion_tokens,completion_tokens_details,prompt_tokens,prompt_token | completion_tokens,completion_tokens_details,prompt_tokens,prompt_token | 一致 |  |
| 响应顶层字段 | choices,created,id,model,object,usage | choices,created,id,model,object,request_id,usage | 偏离 | 官方带 request_id、无 system_fingerprint/service_tier |
| 模型名回显 | glm-5.3-flash | glm-5.3-flash | 一致 |  |
| 默认返回 reasoning_content | True | True | 一致 | GLM-5.3 永远思考；没有=思考被剥离或换了模型 |
| 流式 obfuscation 字段 | False | False | 一致 | 官方无此字段；有=经过 OpenAI 原生/new-api 改写 |
| 工具调用 id 格式(e_sync) | True | True | 一致 | 官方 openai=call_+有符号整数 / anthropic=call_+24hex |
| 工具调用 id 格式(stream) | True | True | 一致 | 官方 openai=call_+有符号整数 / anthropic=call_+24hex |
| 隐藏提示注入(多算的input tokens) | 12 | 12 | 一致 | 差值>8 = 上游加了系统提示或 usage 被改 |
| 泄露的隐藏系统提示 | I can't share my system prompt or developer instructions verbatim. 

I | I can't quote my system prompt or developer instructions verbatim, as  | 偏离 |  |
| 自报厂商 | z.ai | z.ai | 一致 |  |
| 参数校验与官方逐项一致率 | 10/12 | - | 偏离 | temperature_out_of_range:400(官方200) bad_model:503(官方400) |
| stop 序列生效 | False | False | 一致 |  |
| max_tokens 生效 | True | True | 一致 |  |
| 20轮历史记忆 | False | True | 偏离 |  |
| 60k 下 system 规则仍遵守 | False | True | 偏离 |  |
| 英文 +1261 o200k tok 的 usage 增量 | 1720 | 1720 | 一致 | 偏差>2% = usage 不是 GLM 分词器算的(估算/伪造) |
| 中文 +2040 o200k tok 的 usage 增量 | 1610 | 1610 | 一致 | 偏差>2% = usage 不是 GLM 分词器算的(估算/伪造) |
| reasoning_effort 生效(low→max 思考token增长) | 2→54 | 7→23 | 一致 |  |
| 知识阶梯前沿 | 2025-11 | 2025-12 | 一致 | 相差≥2个月才算偏离（temperature=1 抽样本身有±1个月噪声）；早于官方 = 更老的模型 |
| 开放式近期知识前沿 | 2026-01 | 2025-05 | 偏离 |  |
| 知识阶梯逐题分类一致 | 21/24 | - | 一致 | K06:CORRECT(官方UNKNOWN) K09:UNKNOWN(官方CORRECT) K20:WRONG(官方UNKNOWN) |
| 同题4次年代一致(无混合池) | ['2025-05', '2025-05', '2025-05', '2013-03'] | ['2025-05', '2013-03', '2025-05', '2025-05'] | 一致 | 官方 GLM 本身对'现任教宗'就答不稳(方济各/良十四世各半)，所以只有官方稳定而中转不稳才算偏离 |
| 长上下文 20k 三针召回 | ERR400 | 3/3 | 偏离 | 耗时 Nones vs 官方 1.5s ; usage比 None vs 1.063 |
| 长上下文 60k 三针召回 | ERR400 | 3/3 | 偏离 | 耗时 Nones vs 官方 3.5s ; usage比 None vs 1.069 |
| 长上下文 130k 三针召回 | ERR400 | 3/3 | 偏离 | 耗时 Nones vs 官方 4.4s ; usage比 None vs 1.069 |
| 长上下文 230k 三针召回 | ERR400 | 3/3 | 偏离 | 耗时 Nones vs 官方 6.0s ; usage比 None vs 1.066 |
| 前缀缓存命中(cached_tokens 序列) | [0, 0, 0] | [0, 5056, 5056] | 偏离 | 官方隐式缓存第2次即命中；不命中 = 账号池轮询/缓存层被剥离(你付全价) |
| 顺序调用错误/空回复 | 8/0 of 8 | 0/2 of 8 | 偏离 |  |
| 8 并发错误数 | 8 | 0 | 偏离 |  |
| 2500 token 长输出不断流 | 未测 | True | — | 该轮未覆盖此项 |
| 流式粒度 tok/chunk | 未测 | 1.0 | — | 该轮未覆盖此项 |

## yjapi-glm-anthropic / glm-5.3-flash (anthropic) → ❌ 模型身份与官方不一致（知识/自报/思考/分词证据）

偏离项 10（身份 1｜智力 2｜协议 5｜上下文 1｜运营 1）: usage 字段集合, 响应顶层字段, 流式 ping 事件, 工具调用 id 格式(e_sync), 参数校验与官方逐项一致率, 英文 +1261 o200k tok 的 usage 增量, 智力 reason, 智力 reason_off, 长上下文 20k 三针召回, 顺序调用错误/空回复

| 维度 | 中转站 | 官方 | 判定 | 说明 |
|---|---|---|---|---|
| 响应 id 格式 | 8cff0a7a-cb91-4c95-9767-72807946c3 | msg_20260915162609446452a7f2b04362 | 一致 | 官方=14位时间戳+18位hex；chatcmpl-/自造id=中转层重新生成 |
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
| 60k 下 system 规则仍遵守 | 未测 | True | — | 该轮未覆盖此项 |
| 英文 +1261 o200k tok 的 usage 增量 | 1720 | -8 | 偏离 | 偏差>2% = usage 不是 GLM 分词器算的(估算/伪造) |
| 中文 +2040 o200k tok 的 usage 增量 | 1610 | 1610 | 一致 | 偏差>2% = usage 不是 GLM 分词器算的(估算/伪造) |
| 知识阶梯前沿 | 2025-11 | 2025-11 | 一致 | 相差≥2个月才算偏离（temperature=1 抽样本身有±1个月噪声）；早于官方 = 更老的模型 |
| 开放式近期知识前沿 | 2026-01 | 2026-01 | 一致 |  |
| 知识阶梯逐题分类一致 | 22/24 | - | 一致 | K01:UNKNOWN(官方CORRECT) K14:UNKNOWN(官方WRONG) |
| 同题4次年代一致(无混合池) | ['2013-03', '2013-03', '2013-03', '2013-03'] | ['2013-03', '2025-05', '2025-05', '2025-05'] | 一致 | 官方 GLM 本身对'现任教宗'就答不稳(方济各/良十四世各半)，所以只有官方稳定而中转不稳才算偏离 |
| 智力 reason | 2/2 | 12/12 | 偏离 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ reason 平均耗时(s) | 3.0 | 38.6 | 一致 | 慢于官方2.5倍以上 |
| 智力 reason_off | 1/1 | 8/12 | 偏离 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ reason_off 平均耗时(s) | 1.9 | 29.9 | 一致 | 慢于官方2.5倍以上 |
| 长上下文 20k 三针召回 | ERR400 | 3/3 | 偏离 | 耗时 Nones vs 官方 13.7s ; usage比 None vs 0.002 |
| 长上下文 60k 三针召回 | 未测 | 3/3 | — | 该轮未覆盖此项 |
| 长上下文 130k 三针召回 | 未测 | 3/3 | — | 该轮未覆盖此项 |
| 前缀缓存命中(cached_tokens 序列) | [0, 5056] | [5056, 5056, 5056] | 一致 | 官方隐式缓存第2次即命中；不命中 = 账号池轮询/缓存层被剥离(你付全价) |
| 顺序调用错误/空回复 | 0/5 of 5 | 0/0 of 8 | 偏离 |  |
| 8 并发错误数 | 未测 | 0 | — | 该轮未覆盖此项 |
| 2500 token 长输出不断流 | 未测 | True | — | 该轮未覆盖此项 |
| 首字节 TTFB(s) | 2.03 | 2.68 | 一致 | 快24% |
| 首个正文 token TTFT(s) | 5.13 | 2.68 | 一致 | 慢91% |
| 短请求 p50 延迟(s) | 1.95 | 1.43 | 一致 | 慢36% |
| 生成速度 tok/s | 66.5 (66.5-66.5) | 80.0 (76.3-84.4) | 一致 | 慢17% |
| 流式粒度 tok/chunk | 0.7 | 1.0 | 一致 | >3倍官方 = 中转缓冲后再切块(假流式) |

## yjapi-glm-r2 / glm-5.3-flash (openai) → 🟡 模型一致，但经过协议改写层（new-api 转换；参数/流式/计费字段与官方不同）；运营指标偏离 2 项

偏离项 7（身份 0｜智力 2｜协议 3｜上下文 0｜运营 2）: usage 字段集合, 响应顶层字段, reasoning_effort 生效(low→max 思考token增长), 智力 reason, 智力 hard_off,   ↳ xhard 平均耗时(s), 前缀缓存命中(cached_tokens 序列)

| 维度 | 中转站 | 官方 | 判定 | 说明 |
|---|---|---|---|---|
| 响应 id 格式 |  | 20260915162609f1523f2bb6bb4858 | 一致 | 官方=14位时间戳+18位hex；chatcmpl-/自造id=中转层重新生成 |
| usage 字段集合 |  | completion_tokens,completion_tokens_details,prompt_tokens,prompt_token | 偏离 |  |
| 响应顶层字段 |  | choices,created,id,model,object,request_id,usage | 偏离 | 官方带 request_id、无 system_fingerprint/service_tier |
| 模型名回显 | 未测 | glm-5.3-flash | — | 该轮未覆盖此项 |
| 默认返回 reasoning_content | 未测 | True | — | 该轮未覆盖此项 |
| 流式 obfuscation 字段 | 未测 | False | — | 该轮未覆盖此项 |
| 工具调用 id 格式(e_sync) | 未测 | True | — | 该轮未覆盖此项 |
| 工具调用 id 格式(stream) | 未测 | True | — | 该轮未覆盖此项 |
| 隐藏提示注入(多算的input tokens) | 未测 | 12 | — | 该轮未覆盖此项 |
| 自报厂商 | 未测 | z.ai | — | 该轮未覆盖此项 |
| stop 序列生效 | 未测 | False | — | 该轮未覆盖此项 |
| max_tokens 生效 | 未测 | True | — | 该轮未覆盖此项 |
| 20轮历史记忆 | 未测 | True | — | 该轮未覆盖此项 |
| 60k 下 system 规则仍遵守 | 未测 | True | — | 该轮未覆盖此项 |
| reasoning_effort 生效(low→max 思考token增长) | None→None | 7→23 | 偏离 |  |
| 知识阶梯前沿 | 未测 | 2025-12 | — | 该轮未覆盖此项 |
| 开放式近期知识前沿 | 未测 | 2025-05 | — | 该轮未覆盖此项 |
| 同题4次年代一致(无混合池) | 未测 | ['2025-05', '2013-03', '2025-05', '2025-05'] | — | 该轮未覆盖此项 |
| 智力 reason | 9/12 | 12/12 | 偏离 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ reason 平均耗时(s) | 35.8 | 21.0 | 一致 | 慢于官方2.5倍以上 |
| 智力 reason_off | 7/7 | 9/12 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ reason_off 平均耗时(s) | 42.8 | 25.6 | 一致 | 慢于官方2.5倍以上 |
| 智力 hard | 5/6 | 5/6 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ hard 平均耗时(s) | 85.8 | 65.3 | 一致 | 慢于官方2.5倍以上 |
| 智力 hard_off | 3/3 | 6/6 | 偏离 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ hard_off 平均耗时(s) | 41.5 | 81.9 | 一致 | 慢于官方2.5倍以上 |
| 智力 xhard | 10/14 | 6/6 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ xhard 平均耗时(s) | 58.5 | 22.6 | 偏离 | 慢于官方2.5倍以上 |
| 智力 xhard_off | 7/8 | 3/8 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ xhard_off 平均耗时(s) | 46.2 | 42.3 | 一致 | 慢于官方2.5倍以上 |
| 长上下文 20k 三针召回 | 未测 | 3/3 | — | 该轮未覆盖此项 |
| 长上下文 60k 三针召回 | 未测 | 3/3 | — | 该轮未覆盖此项 |
| 长上下文 130k 三针召回 | 未测 | 3/3 | — | 该轮未覆盖此项 |
| 长上下文 230k 三针召回 | 未测 | 3/3 | — | 该轮未覆盖此项 |
| 前缀缓存命中(cached_tokens 序列) | [] | [0, 5056, 5056] | 偏离 | 官方隐式缓存第2次即命中；不命中 = 账号池轮询/缓存层被剥离(你付全价) |
| 顺序调用错误/空回复 | None/None of None | 0/2 of 8 | 一致 |  |
| 8 并发错误数 | 未测 | 0 | — | 该轮未覆盖此项 |
| 2500 token 长输出不断流 | 未测 | True | — | 该轮未覆盖此项 |
| 流式粒度 tok/chunk | 未测 | 1.0 | — | 该轮未覆盖此项 |

## zhipu-0913 / glm-5.3-flash (openai) → ❌ 模型身份与官方不一致（知识/自报/思考/分词证据）

偏离项 8（身份 2｜智力 1｜协议 0｜上下文 0｜运营 5）: 自报厂商, 开放式近期知识前沿, 智力 hard_off,   ↳ xhard 平均耗时(s), 顺序调用错误/空回复, 首字节 TTFB(s), 首个正文 token TTFT(s), 8并发 p50 延迟(s)

| 维度 | 中转站 | 官方 | 判定 | 说明 |
|---|---|---|---|---|
| 响应 id 格式 | 2026091322155198ef0239647d497b | 20260915162609f1523f2bb6bb4858 | 一致 | 官方=14位时间戳+18位hex；chatcmpl-/自造id=中转层重新生成 |
| usage 字段集合 | completion_tokens,completion_tokens_details,prompt_tokens,prompt_token | completion_tokens,completion_tokens_details,prompt_tokens,prompt_token | 一致 |  |
| 响应顶层字段 | choices,created,id,model,object,request_id,usage | choices,created,id,model,object,request_id,usage | 一致 | 官方带 request_id、无 system_fingerprint/service_tier |
| 模型名回显 | glm-5.3-flash | glm-5.3-flash | 一致 |  |
| 默认返回 reasoning_content | True | True | 一致 | GLM-5.3 永远思考；没有=思考被剥离或换了模型 |
| 流式 obfuscation 字段 | False | False | 一致 | 官方无此字段；有=经过 OpenAI 原生/new-api 改写 |
| 工具调用 id 格式(e_sync) | True | True | 一致 | 官方 openai=call_+有符号整数 / anthropic=call_+24hex |
| 工具调用 id 格式(stream) | True | True | 一致 | 官方 openai=call_+有符号整数 / anthropic=call_+24hex |
| 隐藏提示注入(多算的input tokens) | 12 | 12 | 一致 | 差值>8 = 上游加了系统提示或 usage 被改 |
| 自报厂商 | i am a glm language model developed and  | z.ai | 偏离 |  |
| 参数校验与官方逐项一致率 | 12/12 | - | 一致 | 全部一致 |
| stop 序列生效 | False | False | 一致 |  |
| max_tokens 生效 | True | True | 一致 |  |
| 20轮历史记忆 | True | True | 一致 |  |
| 60k 下 system 规则仍遵守 | True | True | 一致 |  |
| 英文 +1261 o200k tok 的 usage 增量 | 1720 | 1720 | 一致 | 偏差>2% = usage 不是 GLM 分词器算的(估算/伪造) |
| 中文 +2040 o200k tok 的 usage 增量 | 1610 | 1610 | 一致 | 偏差>2% = usage 不是 GLM 分词器算的(估算/伪造) |
| usage 与官方 /tokenizer 一致 | True | True | 一致 |  |
| reasoning_effort 生效(low→max 思考token增长) | 7→26 | 7→23 | 一致 |  |
| 知识阶梯前沿 | 2025-11 | 2025-12 | 一致 | 相差≥2个月才算偏离（temperature=1 抽样本身有±1个月噪声）；早于官方 = 更老的模型 |
| 开放式近期知识前沿 | 2026-01 | 2025-05 | 偏离 |  |
| 知识阶梯逐题分类一致 | 21/24 | - | 一致 | K04:CORRECT(官方UNKNOWN) K05:CORRECT(官方UNKNOWN) K09:UNKNOWN(官方CORRECT) |
| 同题4次年代一致(无混合池) | ['2013-03', '2013-03', '2025-05', '2013-03'] | ['2025-05', '2013-03', '2025-05', '2025-05'] | 一致 | 官方 GLM 本身对'现任教宗'就答不稳(方济各/良十四世各半)，所以只有官方稳定而中转不稳才算偏离 |
| 智力 reason | 12/12 | 12/12 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ reason 平均耗时(s) | 28.7 | 21.0 | 一致 | 慢于官方2.5倍以上 |
| 智力 reason_off | 8/12 | 9/12 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ reason_off 平均耗时(s) | 27.3 | 25.6 | 一致 | 慢于官方2.5倍以上 |
| 智力 hard | 5/6 | 5/6 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ hard 平均耗时(s) | 48.7 | 65.3 | 一致 | 慢于官方2.5倍以上 |
| 智力 hard_off | 3/6 | 6/6 | 偏离 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ hard_off 平均耗时(s) | 50.8 | 81.9 | 一致 | 慢于官方2.5倍以上 |
| 智力 xhard | 10/13 | 6/6 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ xhard 平均耗时(s) | 59.5 | 22.6 | 偏离 | 慢于官方2.5倍以上 |
| 智力 xhard_off | 9/14 | 3/8 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ xhard_off 平均耗时(s) | 49.6 | 42.3 | 一致 | 慢于官方2.5倍以上 |
| 长上下文 20k 三针召回 | 3/3 | 3/3 | 一致 | 耗时 1.9s vs 官方 1.5s ; usage比 1.063 vs 1.063 |
| 长上下文 60k 三针召回 | 3/3 | 3/3 | 一致 | 耗时 8.9s vs 官方 3.5s ; usage比 1.069 vs 1.069 |
| 长上下文 130k 三针召回 | 3/3 | 3/3 | 一致 | 耗时 4.7s vs 官方 4.4s ; usage比 1.069 vs 1.069 |
| 长上下文 230k 三针召回 | 未测 | 3/3 | — | 该轮未覆盖此项 |
| 前缀缓存命中(cached_tokens 序列) | [0, 5056, 5056] | [0, 5056, 5056] | 一致 | 官方隐式缓存第2次即命中；不命中 = 账号池轮询/缓存层被剥离(你付全价) |
| 顺序调用错误/空回复 | 0/2 of 8 | 0/2 of 8 | 偏离 |  |
| 8 并发错误数 | 0 | 0 | 一致 |  |
| 2500 token 长输出不断流 | True | True | 一致 |  |
| 首字节 TTFB(s) | 2.87 | 0.73 | 偏离 | 慢293% |
| 首个正文 token TTFT(s) | 2.87 | 0.73 | 偏离 | 慢293% |
| 短请求 p50 延迟(s) | 1.83 | 1.14 | 一致 | 慢61% |
| 8并发 p50 延迟(s) | 3.81 | 1.4 | 偏离 | 慢172% |
| 生成速度 tok/s | 65.9 (64.6-66.8) | 61.0 (58.9-62.7) | 一致 | 快8% |
| 流式粒度 tok/chunk | 1.0 | 1.0 | 一致 | >3倍官方 = 中转缓冲后再切块(假流式) |

## zhipu-official / glm-5.3-flash (openai) → ⚠️ 模型层有偏离，需人工复核

偏离项 5（身份 1｜智力 0｜协议 2｜上下文 0｜运营 2）: 泄露的隐藏系统提示, stop 序列生效, 开放式近期知识前沿, 顺序调用错误/空回复, 8并发 p50 延迟(s)

| 维度 | 中转站 | 官方 | 判定 | 说明 |
|---|---|---|---|---|
| 响应 id 格式 | 20260910143435d77c664001b34e71 | 20260915162609f1523f2bb6bb4858 | 一致 | 官方=14位时间戳+18位hex；chatcmpl-/自造id=中转层重新生成 |
| usage 字段集合 | completion_tokens,completion_tokens_details,prompt_tokens,prompt_token | completion_tokens,completion_tokens_details,prompt_tokens,prompt_token | 一致 |  |
| 响应顶层字段 | choices,created,id,model,object,request_id,usage | choices,created,id,model,object,request_id,usage | 一致 | 官方带 request_id、无 system_fingerprint/service_tier |
| 模型名回显 | glm-5.3-flash | glm-5.3-flash | 一致 |  |
| 默认返回 reasoning_content | True | True | 一致 | GLM-5.3 永远思考；没有=思考被剥离或换了模型 |
| 流式 obfuscation 字段 | False | False | 一致 | 官方无此字段；有=经过 OpenAI 原生/new-api 改写 |
| 工具调用 id 格式(e_sync) | True | True | 一致 | 官方 openai=call_+有符号整数 / anthropic=call_+24hex |
| 工具调用 id 格式(stream) | True | True | 一致 | 官方 openai=call_+有符号整数 / anthropic=call_+24hex |
| 隐藏提示注入(多算的input tokens) | 12 | 12 | 一致 | 差值>8 = 上游加了系统提示或 usage 被改 |
| 泄露的隐藏系统提示 | I can't share my system prompt or internal instructions verbatim, so I | I can't quote my system prompt or developer instructions verbatim, as  | 偏离 |  |
| 自报厂商 | z.ai | z.ai | 一致 |  |
| 参数校验与官方逐项一致率 | 12/12 | - | 一致 | 全部一致 |
| stop 序列生效 | True | False | 偏离 |  |
| max_tokens 生效 | True | True | 一致 |  |
| 20轮历史记忆 | True | True | 一致 |  |
| 60k 下 system 规则仍遵守 | True | True | 一致 |  |
| 英文 +1261 o200k tok 的 usage 增量 | 1720 | 1720 | 一致 | 偏差>2% = usage 不是 GLM 分词器算的(估算/伪造) |
| 中文 +2040 o200k tok 的 usage 增量 | 1610 | 1610 | 一致 | 偏差>2% = usage 不是 GLM 分词器算的(估算/伪造) |
| usage 与官方 /tokenizer 一致 | True | True | 一致 |  |
| reasoning_effort 生效(low→max 思考token增长) | 11→26 | 7→23 | 一致 |  |
| 知识阶梯前沿 | 2025-12 | 2025-12 | 一致 | 相差≥2个月才算偏离（temperature=1 抽样本身有±1个月噪声）；早于官方 = 更老的模型 |
| 开放式近期知识前沿 | 2026-01 | 2025-05 | 偏离 |  |
| 知识阶梯逐题分类一致 | 23/24 | - | 一致 | K06:CORRECT(官方UNKNOWN) |
| 同题4次年代一致(无混合池) | ['2013-03', '2013-03', '2025-05', '2025-05'] | ['2025-05', '2013-03', '2025-05', '2025-05'] | 一致 | 官方 GLM 本身对'现任教宗'就答不稳(方济各/良十四世各半)，所以只有官方稳定而中转不稳才算偏离 |
| 智力 reason | 12/12 | 12/12 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ reason 平均耗时(s) | 19.7 | 21.0 | 一致 | 慢于官方2.5倍以上 |
| 智力 reason_off | 10/12 | 9/12 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ reason_off 平均耗时(s) | 17.9 | 25.6 | 一致 | 慢于官方2.5倍以上 |
| 智力 hard | 5/6 | 5/6 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ hard 平均耗时(s) | 58.8 | 65.3 | 一致 | 慢于官方2.5倍以上 |
| 智力 hard_off | 5/6 | 6/6 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ hard_off 平均耗时(s) | 65.6 | 81.9 | 一致 | 慢于官方2.5倍以上 |
| 智力 xhard | 11/12 | 6/6 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ xhard 平均耗时(s) | 54.5 | 22.6 | 一致 | 慢于官方2.5倍以上 |
| 智力 xhard_off | 8/14 | 3/8 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ xhard_off 平均耗时(s) | 30.0 | 42.3 | 一致 | 慢于官方2.5倍以上 |
| 长上下文 20k 三针召回 | 3/3 | 3/3 | 一致 | 耗时 3.3s vs 官方 1.5s ; usage比 1.063 vs 1.063 |
| 长上下文 60k 三针召回 | 3/3 | 3/3 | 一致 | 耗时 4.3s vs 官方 3.5s ; usage比 1.069 vs 1.069 |
| 长上下文 130k 三针召回 | 3/3 | 3/3 | 一致 | 耗时 13.2s vs 官方 4.4s ; usage比 1.069 vs 1.069 |
| 长上下文 230k 三针召回 | 3/3 | 3/3 | 一致 | 耗时 26.7s vs 官方 6.0s ; usage比 1.066 vs 1.066 |
| 前缀缓存命中(cached_tokens 序列) | [0, 5056, 5056] | [0, 5056, 5056] | 一致 | 官方隐式缓存第2次即命中；不命中 = 账号池轮询/缓存层被剥离(你付全价) |
| 顺序调用错误/空回复 | 0/1 of 8 | 0/2 of 8 | 偏离 |  |
| 8 并发错误数 | 0 | 0 | 一致 |  |
| 2500 token 长输出不断流 | True | True | 一致 |  |
| 首字节 TTFB(s) | 1.31 | 0.73 | 一致 | 慢79% |
| 首个正文 token TTFT(s) | 1.31 | 0.73 | 一致 | 慢79% |
| 短请求 p50 延迟(s) | 1.67 | 1.14 | 一致 | 慢46% |
| 8并发 p50 延迟(s) | 4.54 | 1.4 | 偏离 | 慢224% |
| 生成速度 tok/s | 60.8 (52.5-64.4) | 61.0 (58.9-62.7) | 一致 | 慢0% |
| 流式粒度 tok/chunk | 1.0 | 1.0 | 一致 | >3倍官方 = 中转缓冲后再切块(假流式) |

## zhipu-official-0913 / glm-5.3-flash (openai) → ⚠️ 模型层有偏离，需人工复核

偏离项 4（身份 1｜智力 0｜协议 1｜上下文 0｜运营 2）: 泄露的隐藏系统提示, 开放式近期知识前沿,   ↳ xhard 平均耗时(s), 8并发 p50 延迟(s)

| 维度 | 中转站 | 官方 | 判定 | 说明 |
|---|---|---|---|---|
| 响应 id 格式 | 20260913225235ae030e348d8f4f56 | 20260915162609f1523f2bb6bb4858 | 一致 | 官方=14位时间戳+18位hex；chatcmpl-/自造id=中转层重新生成 |
| usage 字段集合 | completion_tokens,completion_tokens_details,prompt_tokens,prompt_token | completion_tokens,completion_tokens_details,prompt_tokens,prompt_token | 一致 |  |
| 响应顶层字段 | choices,created,id,model,object,request_id,usage | choices,created,id,model,object,request_id,usage | 一致 | 官方带 request_id、无 system_fingerprint/service_tier |
| 模型名回显 | glm-5.3-flash | glm-5.3-flash | 一致 |  |
| 默认返回 reasoning_content | True | True | 一致 | GLM-5.3 永远思考；没有=思考被剥离或换了模型 |
| 流式 obfuscation 字段 | False | False | 一致 | 官方无此字段；有=经过 OpenAI 原生/new-api 改写 |
| 工具调用 id 格式(e_sync) | True | True | 一致 | 官方 openai=call_+有符号整数 / anthropic=call_+24hex |
| 工具调用 id 格式(stream) | True | True | 一致 | 官方 openai=call_+有符号整数 / anthropic=call_+24hex |
| 隐藏提示注入(多算的input tokens) | 12 | 12 | 一致 | 差值>8 = 上游加了系统提示或 usage 被改 |
| 泄露的隐藏系统提示 | I can't quote my system prompt or instructions verbatim, even in part  | I can't quote my system prompt or developer instructions verbatim, as  | 偏离 |  |
| 自报厂商 | z.ai | z.ai | 一致 |  |
| 参数校验与官方逐项一致率 | 12/12 | - | 一致 | 全部一致 |
| stop 序列生效 | False | False | 一致 |  |
| max_tokens 生效 | True | True | 一致 |  |
| 20轮历史记忆 | True | True | 一致 |  |
| 60k 下 system 规则仍遵守 | True | True | 一致 |  |
| 英文 +1261 o200k tok 的 usage 增量 | 1720 | 1720 | 一致 | 偏差>2% = usage 不是 GLM 分词器算的(估算/伪造) |
| 中文 +2040 o200k tok 的 usage 增量 | 1610 | 1610 | 一致 | 偏差>2% = usage 不是 GLM 分词器算的(估算/伪造) |
| usage 与官方 /tokenizer 一致 | True | True | 一致 |  |
| reasoning_effort 生效(low→max 思考token增长) | 8→26 | 7→23 | 一致 |  |
| 知识阶梯前沿 | 2025-11 | 2025-12 | 一致 | 相差≥2个月才算偏离（temperature=1 抽样本身有±1个月噪声）；早于官方 = 更老的模型 |
| 开放式近期知识前沿 | 2025-09 | 2025-05 | 偏离 |  |
| 知识阶梯逐题分类一致 | 22/24 | - | 一致 | K04:CORRECT(官方UNKNOWN) K09:UNKNOWN(官方CORRECT) |
| 同题4次年代一致(无混合池) | ['2025-05', '2025-05', '2013-03', '2025-05'] | ['2025-05', '2013-03', '2025-05', '2025-05'] | 一致 | 官方 GLM 本身对'现任教宗'就答不稳(方济各/良十四世各半)，所以只有官方稳定而中转不稳才算偏离 |
| 智力 reason | 12/12 | 12/12 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ reason 平均耗时(s) | 23.1 | 21.0 | 一致 | 慢于官方2.5倍以上 |
| 智力 reason_off | 8/12 | 9/12 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ reason_off 平均耗时(s) | 24.1 | 25.6 | 一致 | 慢于官方2.5倍以上 |
| 智力 hard | 5/6 | 5/6 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ hard 平均耗时(s) | 67.6 | 65.3 | 一致 | 慢于官方2.5倍以上 |
| 智力 hard_off | 4/6 | 6/6 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ hard_off 平均耗时(s) | 47.1 | 81.9 | 一致 | 慢于官方2.5倍以上 |
| 智力 xhard | 12/13 | 6/6 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ xhard 平均耗时(s) | 58.6 | 22.6 | 偏离 | 慢于官方2.5倍以上 |
| 智力 xhard_off | 7/12 | 3/8 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ xhard_off 平均耗时(s) | 49.4 | 42.3 | 一致 | 慢于官方2.5倍以上 |
| 长上下文 20k 三针召回 | 3/3 | 3/3 | 一致 | 耗时 2.0s vs 官方 1.5s ; usage比 1.063 vs 1.063 |
| 长上下文 60k 三针召回 | 3/3 | 3/3 | 一致 | 耗时 2.5s vs 官方 3.5s ; usage比 1.069 vs 1.069 |
| 长上下文 130k 三针召回 | 3/3 | 3/3 | 一致 | 耗时 4.8s vs 官方 4.4s ; usage比 1.069 vs 1.069 |
| 长上下文 230k 三针召回 | 未测 | 3/3 | — | 该轮未覆盖此项 |
| 前缀缓存命中(cached_tokens 序列) | [5056, 5056, 5056] | [0, 5056, 5056] | 一致 | 官方隐式缓存第2次即命中；不命中 = 账号池轮询/缓存层被剥离(你付全价) |
| 顺序调用错误/空回复 | 0/0 of 8 | 0/2 of 8 | 一致 |  |
| 8 并发错误数 | 0 | 0 | 一致 |  |
| 2500 token 长输出不断流 | True | True | 一致 |  |
| 首字节 TTFB(s) | 1.24 | 0.73 | 一致 | 慢70% |
| 首个正文 token TTFT(s) | 1.24 | 0.73 | 一致 | 慢70% |
| 短请求 p50 延迟(s) | 1.29 | 1.14 | 一致 | 慢13% |
| 8并发 p50 延迟(s) | 3.12 | 1.4 | 偏离 | 慢123% |
| 生成速度 tok/s | 68.9 (64.3-74.3) | 61.0 (58.9-62.7) | 一致 | 快13% |
| 流式粒度 tok/chunk | 1.0 | 1.0 | 一致 | >3倍官方 = 中转缓冲后再切块(假流式) |

## zhipu-official-anthropic / glm-5.3-flash (anthropic) → ⚠️ 模型层有偏离，需人工复核

偏离项 7（身份 1｜智力 0｜协议 2｜上下文 0｜运营 4）: 泄露的隐藏系统提示, stop 序列生效, 英文 +1261 o200k tok 的 usage 增量,   ↳ xhard 平均耗时(s),   ↳ xhard_off 平均耗时(s), 顺序调用错误/空回复, 8并发 p50 延迟(s)

| 维度 | 中转站 | 官方 | 判定 | 说明 |
|---|---|---|---|---|
| 响应 id 格式 | msg_20260910150116738226bfb8a64ca4 | msg_20260915162609446452a7f2b04362 | 一致 | 官方=14位时间戳+18位hex；chatcmpl-/自造id=中转层重新生成 |
| usage 字段集合 | cache_read_input_tokens,input_tokens,output_tokens,server_tool_use,ser | cache_read_input_tokens,input_tokens,output_tokens,server_tool_use,ser | 一致 |  |
| 响应顶层字段 | content,id,model,role,stop_reason,stop_sequence,type,usage | content,id,model,role,stop_reason,stop_sequence,type,usage | 一致 | 官方带 request_id、无 system_fingerprint/service_tier |
| 模型名回显 | glm-5.3-flash | glm-5.3-flash | 一致 |  |
| thinking signature 形态 | 24hex | 24hex | 一致 | 官方=24位hex |
| 流式 ping 事件 | 1 | 1 | 一致 |  |
| 工具调用 id 格式(e_sync) | True | True | 一致 | 官方 openai=call_+有符号整数 / anthropic=call_+24hex |
| 工具调用 id 格式(stream) | True | True | 一致 | 官方 openai=call_+有符号整数 / anthropic=call_+24hex |
| 隐藏提示注入(多算的input tokens) | 12 | 12 | 一致 | 差值>8 = 上游加了系统提示或 usage 被改 |
| 泄露的隐藏系统提示 | I appreciate your interest in transparency. I do have developer instru |  | 偏离 |  |
| 自报厂商 | z.ai | z.ai | 一致 |  |
| 参数校验与官方逐项一致率 | 10/10 | - | 一致 | 全部一致 |
| stop 序列生效 | True | False | 偏离 |  |
| max_tokens 生效 | True | True | 一致 |  |
| 20轮历史记忆 | True | True | 一致 |  |
| 60k 下 system 规则仍遵守 | True | True | 一致 |  |
| 英文 +1261 o200k tok 的 usage 增量 | 1720 | -8 | 偏离 | 偏差>2% = usage 不是 GLM 分词器算的(估算/伪造) |
| 中文 +2040 o200k tok 的 usage 增量 | 1610 | 1610 | 一致 | 偏差>2% = usage 不是 GLM 分词器算的(估算/伪造) |
| 知识阶梯前沿 | 2025-12 | 2025-11 | 一致 | 相差≥2个月才算偏离（temperature=1 抽样本身有±1个月噪声）；早于官方 = 更老的模型 |
| 开放式近期知识前沿 | 2026-01 | 2026-01 | 一致 |  |
| 知识阶梯逐题分类一致 | 21/24 | - | 一致 | K05:CORRECT(官方UNKNOWN) K09:CORRECT(官方UNKNOWN) K14:UNKNOWN(官方WRONG) |
| 同题4次年代一致(无混合池) | ['2025-05', '2013-03', '2025-05', '2025-05'] | ['2013-03', '2025-05', '2025-05', '2025-05'] | 一致 | 官方 GLM 本身对'现任教宗'就答不稳(方济各/良十四世各半)，所以只有官方稳定而中转不稳才算偏离 |
| 智力 reason | 12/12 | 12/12 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ reason 平均耗时(s) | 36.6 | 38.6 | 一致 | 慢于官方2.5倍以上 |
| 智力 reason_off | 9/12 | 8/12 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ reason_off 平均耗时(s) | 24.6 | 29.9 | 一致 | 慢于官方2.5倍以上 |
| 智力 hard | 6/6 | 5/6 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ hard 平均耗时(s) | 57.0 | 95.4 | 一致 | 慢于官方2.5倍以上 |
| 智力 hard_off | 5/6 | 4/6 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ hard_off 平均耗时(s) | 48.0 | 51.1 | 一致 | 慢于官方2.5倍以上 |
| 智力 xhard | 13/14 | 3/3 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ xhard 平均耗时(s) | 48.6 | 12.6 | 偏离 | 慢于官方2.5倍以上 |
| 智力 xhard_off | 8/13 | 2/4 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ xhard_off 平均耗时(s) | 44.9 | 7.1 | 偏离 | 慢于官方2.5倍以上 |
| 长上下文 20k 三针召回 | 3/3 | 3/3 | 一致 | 耗时 3.1s vs 官方 13.7s ; usage比 1.063 vs 0.002 |
| 长上下文 60k 三针召回 | 3/3 | 3/3 | 一致 | 耗时 4.4s vs 官方 2.2s ; usage比 1.069 vs 0.001 |
| 长上下文 130k 三针召回 | 3/3 | 3/3 | 一致 | 耗时 5.9s vs 官方 2.2s ; usage比 1.069 vs 0.0 |
| 前缀缓存命中(cached_tokens 序列) | [0, 5056, 5056] | [5056, 5056, 5056] | 一致 | 官方隐式缓存第2次即命中；不命中 = 账号池轮询/缓存层被剥离(你付全价) |
| 顺序调用错误/空回复 | 0/2 of 8 | 0/0 of 8 | 偏离 |  |
| 8 并发错误数 | 0 | 0 | 一致 |  |
| 2500 token 长输出不断流 | True | True | 一致 |  |
| 首字节 TTFB(s) | 1.18 | 2.68 | 一致 | 快56% |
| 首个正文 token TTFT(s) | 1.18 | 2.68 | 一致 | 快56% |
| 短请求 p50 延迟(s) | 1.48 | 1.43 | 一致 | 慢3% |
| 8并发 p50 延迟(s) | 3.25 | 1.38 | 偏离 | 慢136% |
| 生成速度 tok/s | 62.5 (62.3-62.6) | 80.0 (76.3-84.4) | 一致 | 慢22% |
| 流式粒度 tok/chunk | 1.0 | 1.0 | 一致 | >3倍官方 = 中转缓冲后再切块(假流式) |

## zhipu-official-anthropic-0913 / glm-5.3-flash (anthropic) → ⚠️ 模型层有偏离，需人工复核

偏离项 1（身份 1｜智力 0｜协议 0｜上下文 0｜运营 0）: 英文 +1261 o200k tok 的 usage 增量

| 维度 | 中转站 | 官方 | 判定 | 说明 |
|---|---|---|---|---|
| 响应 id 格式 | msg_202609132252351edadaf92ff04b77 | msg_20260915162609446452a7f2b04362 | 一致 | 官方=14位时间戳+18位hex；chatcmpl-/自造id=中转层重新生成 |
| usage 字段集合 | cache_read_input_tokens,input_tokens,output_tokens,server_tool_use,ser | cache_read_input_tokens,input_tokens,output_tokens,server_tool_use,ser | 一致 |  |
| 响应顶层字段 | content,id,model,role,stop_reason,stop_sequence,type,usage | content,id,model,role,stop_reason,stop_sequence,type,usage | 一致 | 官方带 request_id、无 system_fingerprint/service_tier |
| 模型名回显 | glm-5.3-flash | glm-5.3-flash | 一致 |  |
| thinking signature 形态 | 24hex | 24hex | 一致 | 官方=24位hex |
| 流式 ping 事件 | 1 | 1 | 一致 |  |
| 工具调用 id 格式(e_sync) | True | True | 一致 | 官方 openai=call_+有符号整数 / anthropic=call_+24hex |
| 工具调用 id 格式(stream) | True | True | 一致 | 官方 openai=call_+有符号整数 / anthropic=call_+24hex |
| 隐藏提示注入(多算的input tokens) | 12 | 12 | 一致 | 差值>8 = 上游加了系统提示或 usage 被改 |
| 自报厂商 | z.ai | z.ai | 一致 |  |
| 参数校验与官方逐项一致率 | 10/10 | - | 一致 | 全部一致 |
| stop 序列生效 | False | False | 一致 |  |
| max_tokens 生效 | True | True | 一致 |  |
| 20轮历史记忆 | True | True | 一致 |  |
| 60k 下 system 规则仍遵守 | 未测 | True | — | 该轮未覆盖此项 |
| 英文 +1261 o200k tok 的 usage 增量 | 1720 | -8 | 偏离 | 偏差>2% = usage 不是 GLM 分词器算的(估算/伪造) |
| 中文 +2040 o200k tok 的 usage 增量 | 1610 | 1610 | 一致 | 偏差>2% = usage 不是 GLM 分词器算的(估算/伪造) |
| 知识阶梯前沿 | 2025-12 | 2025-11 | 一致 | 相差≥2个月才算偏离（temperature=1 抽样本身有±1个月噪声）；早于官方 = 更老的模型 |
| 开放式近期知识前沿 | 2026-01 | 2026-01 | 一致 |  |
| 知识阶梯逐题分类一致 | 21/24 | - | 一致 | K04:UNKNOWN(官方CORRECT) K09:CORRECT(官方UNKNOWN) K14:UNKNOWN(官方WRONG) |
| 同题4次年代一致(无混合池) | ['2013-03', '2025-05', '2025-05', '2025-05'] | ['2013-03', '2025-05', '2025-05', '2025-05'] | 一致 | 官方 GLM 本身对'现任教宗'就答不稳(方济各/良十四世各半)，所以只有官方稳定而中转不稳才算偏离 |
| 智力 reason | 11/12 | 12/12 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ reason 平均耗时(s) | 20.3 | 38.6 | 一致 | 慢于官方2.5倍以上 |
| 智力 reason_off | 11/12 | 8/12 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ reason_off 平均耗时(s) | 12.1 | 29.9 | 一致 | 慢于官方2.5倍以上 |
| 长上下文 20k 三针召回 | 3/3 | 3/3 | 一致 | 耗时 2.0s vs 官方 13.7s ; usage比 1.063 vs 0.002 |
| 长上下文 60k 三针召回 | 未测 | 3/3 | — | 该轮未覆盖此项 |
| 长上下文 130k 三针召回 | 未测 | 3/3 | — | 该轮未覆盖此项 |
| 前缀缓存命中(cached_tokens 序列) | [0, 5056] | [5056, 5056, 5056] | 一致 | 官方隐式缓存第2次即命中；不命中 = 账号池轮询/缓存层被剥离(你付全价) |
| 顺序调用错误/空回复 | 0/0 of 5 | 0/0 of 8 | 一致 |  |
| 8 并发错误数 | 未测 | 0 | — | 该轮未覆盖此项 |
| 2500 token 长输出不断流 | 未测 | True | — | 该轮未覆盖此项 |
| 首字节 TTFB(s) | 1.16 | 2.68 | 一致 | 快57% |
| 首个正文 token TTFT(s) | 1.16 | 2.68 | 一致 | 快57% |
| 短请求 p50 延迟(s) | 1.23 | 1.43 | 一致 | 快14% |
| 生成速度 tok/s | 63.4 (63.4-63.4) | 80.0 (76.3-84.4) | 一致 | 慢21% |
| 流式粒度 tok/chunk | 1.0 | 1.0 | 一致 | >3倍官方 = 中转缓冲后再切块(假流式) |
