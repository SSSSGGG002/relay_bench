# 中转站 vs 官方基准 对比报告

基准: ['zhipu-official', 'zhipu-official-anthropic']  (官方直连结果；每一行 = 中转站的数值 / 官方的数值 / 判定)

## 总表

| 中转站 | 模型 | 协议 | 结论 | 偏离项(身份/智力/协议/上下文/运营) |
|---|---|---|---|---|
| rtoc | glm-5.3-flash | openai | 🟡 模型一致，但经过协议改写层（new-api 转换；参数/流式/计费字段与官方不同）；运营指标偏离 9 项 | 身份0/智力0/协议4/上下文1/运营9 |
| rtoc-anthropic | glm-5.3-flash | anthropic | 🟡 模型一致，但经过协议改写层（new-api 转换；参数/流式/计费字段与官方不同）；运营指标偏离 5 项 | 身份0/智力2/协议1/上下文0/运营5 |
| v129-K1 | glm-5.3-flash | openai | 🟡 模型一致，但经过协议改写层（new-api 转换；参数/流式/计费字段与官方不同）；运营指标偏离 1 项 | 身份0/智力0/协议5/上下文0/运营1 |
| v129-K1-anthropic | glm-5.3-flash | anthropic | 🟡 模型一致，但经过协议改写层（new-api 转换；参数/流式/计费字段与官方不同）；运营指标偏离 2 项 | 身份0/智力2/协议5/上下文0/运营2 |
| v129-K1-proxy | glm-5.3-flash | anthropic | ⚠️ 模型层有偏离，需人工复核 | 身份1/智力0/协议3/上下文0/运营1 |
| v129-K2 | glm-5.3-flash | openai | 🟡 模型一致，但经过协议改写层（new-api 转换；参数/流式/计费字段与官方不同） | 身份0/智力1/协议5/上下文0/运营0 |
| v129-K3 | glm-5.3-flash | openai | ⛔ 不可用（该分组没有此模型渠道 / 全部失败） | 身份0/智力0/协议3/上下文0/运营1 |
| v129-K4 | glm-5.3-flash | openai | ⛔ 不可用（该分组没有此模型渠道 / 全部失败） | 身份0/智力0/协议3/上下文0/运营1 |

## 0. 官方基准指纹速览

| 基准 | 模型 | 协议 | id样例 | usage字段 | 默认思考 | 注入tok | 知识前沿(阶梯/开放) | IQ direct/reason/hard/xhard | TTFT | tok/s | p50 | 缓存 | ctx |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| zhipu-official | glm-5.3-flash | openai | `20260910143435d77c664001b34e71` | completion_tokens,completion_tokens_details,prompt_tokens,prompt_tokens_details,total_tokens | True | 12 | 2025-12/2026-01 | 8/8/12/12/5/6/11/12 | 1.31 | 60.8 | 1.67 | [0, 5056, 5056] | 3/3/3/3/3/3/3/3 |
| zhipu-official-anthropic | glm-5.3-flash | anthropic | `msg_20260910150116738226bfb8a64ca4` | cache_read_input_tokens,input_tokens,output_tokens,server_tool_use,service_tier | True | 12 | 2025-12/2026-01 | 7/8/12/12/6/6/13/14 | 1.18 | 62.5 | 1.48 | [0, 5056, 5056] | 3/3/3/3/3/3/None |

## rtoc / glm-5.3-flash (openai) → 🟡 模型一致，但经过协议改写层（new-api 转换；参数/流式/计费字段与官方不同）；运营指标偏离 9 项

偏离项 14（身份 0｜智力 0｜协议 4｜上下文 1｜运营 9）: usage 字段集合, 响应顶层字段, 参数校验与官方逐项一致率, 60k 下 system 规则仍遵守, reasoning_effort 生效(low→max 思考token增长),   ↳ direct 平均耗时(s),   ↳ reason 平均耗时(s),   ↳ reason_off 平均耗时(s),   ↳ xhard 平均耗时(s),   ↳ xhard_off 平均耗时(s), 顺序调用错误/空回复, 2500 token 长输出不断流, 首字节 TTFB(s), 首个正文 token TTFT(s)

| 维度 | 中转站 | 官方 | 判定 | 说明 |
|---|---|---|---|---|
| 响应 id 格式 | msg_2026091014360855627beeb9934132 | 20260910143435d77c664001b34e71 | 一致 | 官方=14位时间戳+18位hex；chatcmpl-/自造id=中转层重新生成 |
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
| stop 序列生效 | True | True | 一致 |  |
| max_tokens 生效 | True | True | 一致 |  |
| 20轮历史记忆 | True | True | 一致 |  |
| 60k 下 system 规则仍遵守 | False | True | 偏离 |  |
| 英文 +1261 o200k tok 的 usage 增量 | 1720 | 1720 | 一致 | 偏差>2% = usage 不是 GLM 分词器算的(估算/伪造) |
| 中文 +2040 o200k tok 的 usage 增量 | 1610 | 1610 | 一致 | 偏差>2% = usage 不是 GLM 分词器算的(估算/伪造) |
| reasoning_effort 生效(low→max 思考token增长) | 0→0 | 11→26 | 偏离 |  |
| 知识阶梯前沿 | 2025-11 | 2025-12 | 一致 | 相差≥2个月才算偏离（temperature=1 抽样本身有±1个月噪声）；早于官方 = 更老的模型 |
| 开放式近期知识前沿 | 2026-01 | 2026-01 | 一致 |  |
| 知识阶梯逐题分类一致 | 22/24 | - | 一致 | K06:UNKNOWN(官方CORRECT) K09:UNKNOWN(官方CORRECT) |
| 同题4次年代一致(无混合池) | ['2025-05', '2025-05', '2013-03', '2013-03'] | ['2013-03', '2013-03', '2025-05', '2025-05'] | 一致 | 官方 GLM 本身对'现任教宗'就答不稳(方济各/良十四世各半)，所以只有官方稳定而中转不稳才算偏离 |
| 智力 direct | 8/8 | 8/8 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ direct 平均耗时(s) | 13.3 | 3.4 | 偏离 | 慢于官方2.5倍以上 |
| 智力 reason | 12/12 | 12/12 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ reason 平均耗时(s) | 57.4 | 19.7 | 偏离 | 慢于官方2.5倍以上 |
| 智力 reason_off | 11/12 | 10/12 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ reason_off 平均耗时(s) | 62.8 | 17.9 | 偏离 | 慢于官方2.5倍以上 |
| 智力 hard | 6/6 | 5/6 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ hard 平均耗时(s) | 106.7 | 58.8 | 一致 | 慢于官方2.5倍以上 |
| 智力 hard_off | 5/6 | 5/6 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ hard_off 平均耗时(s) | 134.6 | 65.6 | 一致 | 慢于官方2.5倍以上 |
| 智力 xhard | 12/13 | 11/12 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ xhard 平均耗时(s) | 139.4 | 54.5 | 偏离 | 慢于官方2.5倍以上 |
| 智力 xhard_off | 11/13 | 8/14 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ xhard_off 平均耗时(s) | 144.0 | 30.0 | 偏离 | 慢于官方2.5倍以上 |
| 长上下文 20k 三针召回 | 3/3 | 3/3 | 一致 | 耗时 7.4s vs 官方 3.3s ; usage比 1.063 vs 1.063 |
| 长上下文 60k 三针召回 | 3/3 | 3/3 | 一致 | 耗时 10.6s vs 官方 4.3s ; usage比 1.069 vs 1.069 |
| 长上下文 130k 三针召回 | 3/3 | 3/3 | 一致 | 耗时 21.8s vs 官方 13.2s ; usage比 1.069 vs 1.069 |
| 长上下文 230k 三针召回 | 3/3 | 3/3 | 一致 | 耗时 30.4s vs 官方 26.7s ; usage比 1.066 vs 1.066 |
| 前缀缓存命中(cached_tokens 序列) | [0, 5056, 5056] | [0, 5056, 5056] | 一致 | 官方隐式缓存第2次即命中；不命中 = 账号池轮询/缓存层被剥离(你付全价) |
| 顺序调用错误/空回复 | 0/8 of 8 | 0/1 of 8 | 偏离 |  |
| 8 并发错误数 | 0 | 0 | 一致 |  |
| 2500 token 长输出不断流 | False | True | 偏离 |  |
| 首字节 TTFB(s) | 9.48 | 1.31 | 偏离 | 慢624% |
| 首个正文 token TTFT(s) | 84.63 | 1.31 | 偏离 | 慢6360% |
| 短请求 p50 延迟(s) | 2.17 | 1.67 | 一致 | 慢30% |
| 8并发 p50 延迟(s) | 6.77 | 4.54 | 一致 | 慢49% |
| 生成速度 tok/s | 187.6 (187.6-187.6) | 60.8 (52.5-64.4) | 一致 | 快209% |
| 流式粒度 tok/chunk | 0.1 | 1.0 | 一致 | >3倍官方 = 中转缓冲后再切块(假流式) |

## rtoc-anthropic / glm-5.3-flash (anthropic) → 🟡 模型一致，但经过协议改写层（new-api 转换；参数/流式/计费字段与官方不同）；运营指标偏离 5 项

偏离项 8（身份 0｜智力 2｜协议 1｜上下文 0｜运营 5）: 参数校验与官方逐项一致率, 智力 xhard,   ↳ xhard 平均耗时(s), 智力 xhard_off, 顺序调用错误/空回复, 首个正文 token TTFT(s), 8并发 p50 延迟(s), 生成速度 tok/s

| 维度 | 中转站 | 官方 | 判定 | 说明 |
|---|---|---|---|---|
| 响应 id 格式 | msg_2026091015310283b4e7b0c2f74752 | msg_20260910150116738226bfb8a64ca4 | 一致 | 官方=14位时间戳+18位hex；chatcmpl-/自造id=中转层重新生成 |
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
| stop 序列生效 | True | True | 一致 |  |
| max_tokens 生效 | True | True | 一致 |  |
| 20轮历史记忆 | True | True | 一致 |  |
| 60k 下 system 规则仍遵守 | True | True | 一致 |  |
| 英文 +1261 o200k tok 的 usage 增量 | 1720 | 1720 | 一致 | 偏差>2% = usage 不是 GLM 分词器算的(估算/伪造) |
| 中文 +2040 o200k tok 的 usage 增量 | 1610 | 1610 | 一致 | 偏差>2% = usage 不是 GLM 分词器算的(估算/伪造) |
| 知识阶梯前沿 | 2025-11 | 2025-12 | 一致 | 相差≥2个月才算偏离（temperature=1 抽样本身有±1个月噪声）；早于官方 = 更老的模型 |
| 开放式近期知识前沿 | 2026-01 | 2026-01 | 一致 |  |
| 知识阶梯逐题分类一致 | 21/24 | - | 一致 | K05:UNKNOWN(官方CORRECT) K06:CORRECT(官方UNKNOWN) K09:UNKNOWN(官方CORRECT) |
| 同题4次年代一致(无混合池) | ['2013-03', '2013-03', '2013-03', '2013-03'] | ['2025-05', '2013-03', '2025-05', '2025-05'] | 一致 | 官方 GLM 本身对'现任教宗'就答不稳(方济各/良十四世各半)，所以只有官方稳定而中转不稳才算偏离 |
| 智力 reason | 11/12 | 12/12 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ reason 平均耗时(s) | 40.6 | 36.6 | 一致 | 慢于官方2.5倍以上 |
| 智力 reason_off | 7/12 | 9/12 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ reason_off 平均耗时(s) | 46.4 | 24.6 | 一致 | 慢于官方2.5倍以上 |
| 智力 hard | 4/6 | 6/6 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ hard 平均耗时(s) | 127.1 | 57.0 | 一致 | 慢于官方2.5倍以上 |
| 智力 hard_off | 4/6 | 5/6 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ hard_off 平均耗时(s) | 106.1 | 48.0 | 一致 | 慢于官方2.5倍以上 |
| 智力 xhard | 7/7 | 13/14 | 偏离 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ xhard 平均耗时(s) | 149.4 | 48.6 | 偏离 | 慢于官方2.5倍以上 |
| 智力 xhard_off | 5/7 | 8/13 | 偏离 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ xhard_off 平均耗时(s) | 90.0 | 44.9 | 一致 | 慢于官方2.5倍以上 |
| 长上下文 20k 三针召回 | 3/3 | 3/3 | 一致 | 耗时 25.3s vs 官方 3.1s ; usage比 1.063 vs 1.063 |
| 长上下文 60k 三针召回 | 3/3 | 3/3 | 一致 | 耗时 28.5s vs 官方 4.4s ; usage比 1.069 vs 1.069 |
| 长上下文 130k 三针召回 | 3/3 | 3/3 | 一致 | 耗时 23.8s vs 官方 5.9s ; usage比 1.069 vs 1.069 |
| 前缀缓存命中(cached_tokens 序列) | [0, 5056, 5056] | [0, 5056, 5056] | 一致 | 官方隐式缓存第2次即命中；不命中 = 账号池轮询/缓存层被剥离(你付全价) |
| 顺序调用错误/空回复 | 0/1 of 8 | 0/2 of 8 | 偏离 |  |
| 8 并发错误数 | 0 | 0 | 一致 |  |
| 2500 token 长输出不断流 | True | True | 一致 |  |
| 首字节 TTFB(s) | 2.27 | 1.18 | 一致 | 慢92% |
| 首个正文 token TTFT(s) | 2.49 | 1.18 | 偏离 | 慢111% |
| 短请求 p50 延迟(s) | 2.55 | 1.48 | 一致 | 慢72% |
| 8并发 p50 延迟(s) | 7.1 | 3.25 | 偏离 | 慢118% |
| 生成速度 tok/s | 32.0 (29.7-32.8) | 62.5 (62.3-62.6) | 偏离 | 慢49% |
| 流式粒度 tok/chunk | 1.0 | 1.0 | 一致 | >3倍官方 = 中转缓冲后再切块(假流式) |

## v129-K1 / glm-5.3-flash (openai) → 🟡 模型一致，但经过协议改写层（new-api 转换；参数/流式/计费字段与官方不同）；运营指标偏离 1 项

偏离项 6（身份 0｜智力 0｜协议 5｜上下文 0｜运营 1）: usage 字段集合, 响应顶层字段, 泄露的隐藏系统提示, 参数校验与官方逐项一致率, stop 序列生效, 顺序调用错误/空回复

| 维度 | 中转站 | 官方 | 判定 | 说明 |
|---|---|---|---|---|
| 响应 id 格式 | 7a46880dd9ba13849e8008ee368c6d00 | 20260910143435d77c664001b34e71 | 一致 | 官方=14位时间戳+18位hex；chatcmpl-/自造id=中转层重新生成 |
| usage 字段集合 | cached_tokens,completion_tokens,completion_tokens_details,prompt_token | completion_tokens,completion_tokens_details,prompt_tokens,prompt_token | 偏离 |  |
| 响应顶层字段 | choices,created,id,model,object,usage | choices,created,id,model,object,request_id,usage | 偏离 | 官方带 request_id、无 system_fingerprint/service_tier |
| 模型名回显 | glm-5.3-flash | glm-5.3-flash | 一致 |  |
| 默认返回 reasoning_content | True | True | 一致 | GLM-5.3 永远思考；没有=思考被剥离或换了模型 |
| 流式 obfuscation 字段 | False | False | 一致 | 官方无此字段；有=经过 OpenAI 原生/new-api 改写 |
| 工具调用 id 格式(e_sync) | True | True | 一致 | 官方 openai=call_+有符号整数 / anthropic=call_+24hex |
| 工具调用 id 格式(stream) | True | True | 一致 | 官方 openai=call_+有符号整数 / anthropic=call_+24hex |
| 隐藏提示注入(多算的input tokens) | 12 | 12 | 一致 | 差值>8 = 上游加了系统提示或 usage 被改 |
| 泄露的隐藏系统提示 | I can't share the verbatim text of my system prompt or instructions, a | I can't share my system prompt or internal instructions verbatim, so I | 偏离 |  |
| 自报厂商 | z.ai | z.ai | 一致 |  |
| 参数校验与官方逐项一致率 | 8/12 | - | 偏离 | effort_invalid:200(官方400) effort_none:200(官方400) thinking_disabled:200(官方400) bad_model:503(官方400) |
| stop 序列生效 | False | True | 偏离 |  |
| max_tokens 生效 | True | True | 一致 |  |
| 20轮历史记忆 | True | True | 一致 |  |
| 60k 下 system 规则仍遵守 | True | True | 一致 |  |
| 英文 +1261 o200k tok 的 usage 增量 | 1720 | 1720 | 一致 | 偏差>2% = usage 不是 GLM 分词器算的(估算/伪造) |
| 中文 +2040 o200k tok 的 usage 增量 | 1610 | 1610 | 一致 | 偏差>2% = usage 不是 GLM 分词器算的(估算/伪造) |
| reasoning_effort 生效(low→max 思考token增长) | 2→64 | 11→26 | 一致 |  |
| 知识阶梯前沿 | 2025-12 | 2025-12 | 一致 | 相差≥2个月才算偏离（temperature=1 抽样本身有±1个月噪声）；早于官方 = 更老的模型 |
| 开放式近期知识前沿 | 2026-01 | 2026-01 | 一致 |  |
| 知识阶梯逐题分类一致 | 23/24 | - | 一致 | K06:UNKNOWN(官方CORRECT) |
| 同题4次年代一致(无混合池) | ['2025-05', '2013-03', '2025-05', '2013-03'] | ['2013-03', '2013-03', '2025-05', '2025-05'] | 一致 | 官方 GLM 本身对'现任教宗'就答不稳(方济各/良十四世各半)，所以只有官方稳定而中转不稳才算偏离 |
| 智力 direct | 6/8 | 8/8 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ direct 平均耗时(s) | 4.0 | 3.4 | 一致 | 慢于官方2.5倍以上 |
| 智力 reason | 12/12 | 12/12 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ reason 平均耗时(s) | 30.6 | 19.7 | 一致 | 慢于官方2.5倍以上 |
| 智力 reason_off | 8/12 | 10/12 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ reason_off 平均耗时(s) | 21.6 | 17.9 | 一致 | 慢于官方2.5倍以上 |
| 智力 hard | 5/6 | 5/6 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ hard 平均耗时(s) | 84.9 | 58.8 | 一致 | 慢于官方2.5倍以上 |
| 智力 hard_off | 5/5 | 5/6 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ hard_off 平均耗时(s) | 68.6 | 65.6 | 一致 | 慢于官方2.5倍以上 |
| 智力 xhard | 12/12 | 11/12 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ xhard 平均耗时(s) | 55.8 | 54.5 | 一致 | 慢于官方2.5倍以上 |
| 智力 xhard_off | 8/14 | 8/14 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ xhard_off 平均耗时(s) | 38.3 | 30.0 | 一致 | 慢于官方2.5倍以上 |
| 长上下文 20k 三针召回 | 3/3 | 3/3 | 一致 | 耗时 3.0s vs 官方 3.3s ; usage比 1.063 vs 1.063 |
| 长上下文 60k 三针召回 | 3/3 | 3/3 | 一致 | 耗时 4.0s vs 官方 4.3s ; usage比 1.069 vs 1.069 |
| 长上下文 130k 三针召回 | 3/3 | 3/3 | 一致 | 耗时 4.5s vs 官方 13.2s ; usage比 1.069 vs 1.069 |
| 长上下文 230k 三针召回 | 3/3 | 3/3 | 一致 | 耗时 6.4s vs 官方 26.7s ; usage比 1.066 vs 1.066 |
| 前缀缓存命中(cached_tokens 序列) | [5056, 5056, 5056] | [0, 5056, 5056] | 一致 | 官方隐式缓存第2次即命中；不命中 = 账号池轮询/缓存层被剥离(你付全价) |
| 顺序调用错误/空回复 | 0/1 of 8 | 0/1 of 8 | 偏离 |  |
| 8 并发错误数 | 0 | 0 | 一致 |  |
| 2500 token 长输出不断流 | True | True | 一致 |  |
| 首字节 TTFB(s) | 1.77 | 1.31 | 一致 | 慢35% |
| 首个正文 token TTFT(s) | 1.77 | 1.31 | 一致 | 慢35% |
| 短请求 p50 延迟(s) | 1.99 | 1.67 | 一致 | 慢19% |
| 8并发 p50 延迟(s) | 3.97 | 4.54 | 一致 | 快13% |
| 生成速度 tok/s | 63.6 (62.7-77.1) | 60.8 (52.5-64.4) | 一致 | 快5% |
| 流式粒度 tok/chunk | 1.0 | 1.0 | 一致 | >3倍官方 = 中转缓冲后再切块(假流式) |

## v129-K1-anthropic / glm-5.3-flash (anthropic) → 🟡 模型一致，但经过协议改写层（new-api 转换；参数/流式/计费字段与官方不同）；运营指标偏离 2 项

偏离项 9（身份 0｜智力 2｜协议 5｜上下文 0｜运营 2）: usage 字段集合, 响应顶层字段, 流式 ping 事件, 参数校验与官方逐项一致率, stop 序列生效, 智力 xhard, 智力 xhard_off, 顺序调用错误/空回复, 首个正文 token TTFT(s)

| 维度 | 中转站 | 官方 | 判定 | 说明 |
|---|---|---|---|---|
| 响应 id 格式 | 9b754e9bfe92c69e121636cf6dffc36d | msg_20260910150116738226bfb8a64ca4 | 一致 | 官方=14位时间戳+18位hex；chatcmpl-/自造id=中转层重新生成 |
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
| stop 序列生效 | False | True | 偏离 |  |
| max_tokens 生效 | True | True | 一致 |  |
| 20轮历史记忆 | True | True | 一致 |  |
| 60k 下 system 规则仍遵守 | 未测 | True | — | 该轮未覆盖此项 |
| 英文 +1261 o200k tok 的 usage 增量 | 1720 | 1720 | 一致 | 偏差>2% = usage 不是 GLM 分词器算的(估算/伪造) |
| 中文 +2040 o200k tok 的 usage 增量 | 1610 | 1610 | 一致 | 偏差>2% = usage 不是 GLM 分词器算的(估算/伪造) |
| 知识阶梯前沿 | 2025-11 | 2025-12 | 一致 | 相差≥2个月才算偏离（temperature=1 抽样本身有±1个月噪声）；早于官方 = 更老的模型 |
| 开放式近期知识前沿 | 2026-01 | 2026-01 | 一致 |  |
| 知识阶梯逐题分类一致 | 21/24 | - | 一致 | K03:UNKNOWN(官方CORRECT) K05:UNKNOWN(官方CORRECT) K09:UNKNOWN(官方CORRECT) |
| 同题4次年代一致(无混合池) | ['2013-03', '2025-05', '2025-05', '2025-05'] | ['2025-05', '2013-03', '2025-05', '2025-05'] | 一致 | 官方 GLM 本身对'现任教宗'就答不稳(方济各/良十四世各半)，所以只有官方稳定而中转不稳才算偏离 |
| 智力 reason | 10/12 | 12/12 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ reason 平均耗时(s) | 27.7 | 36.6 | 一致 | 慢于官方2.5倍以上 |
| 智力 reason_off | 11/12 | 9/12 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ reason_off 平均耗时(s) | 27.7 | 24.6 | 一致 | 慢于官方2.5倍以上 |
| 智力 hard | 6/6 | 6/6 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ hard 平均耗时(s) | 63.9 | 57.0 | 一致 | 慢于官方2.5倍以上 |
| 智力 hard_off | 5/6 | 5/6 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ hard_off 平均耗时(s) | 45.3 | 48.0 | 一致 | 慢于官方2.5倍以上 |
| 智力 xhard | 6/7 | 13/14 | 偏离 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ xhard 平均耗时(s) | 58.9 | 48.6 | 一致 | 慢于官方2.5倍以上 |
| 智力 xhard_off | 5/5 | 8/13 | 偏离 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ xhard_off 平均耗时(s) | 79.6 | 44.9 | 一致 | 慢于官方2.5倍以上 |
| 长上下文 20k 三针召回 | 3/3 | 3/3 | 一致 | 耗时 4.0s vs 官方 3.1s ; usage比 1.063 vs 1.063 |
| 长上下文 60k 三针召回 | 未测 | 3/3 | — | 该轮未覆盖此项 |
| 长上下文 130k 三针召回 | 未测 | 3/3 | — | 该轮未覆盖此项 |
| 前缀缓存命中(cached_tokens 序列) | [0, 5056] | [0, 5056, 5056] | 一致 | 官方隐式缓存第2次即命中；不命中 = 账号池轮询/缓存层被剥离(你付全价) |
| 顺序调用错误/空回复 | 0/5 of 5 | 0/2 of 8 | 偏离 |  |
| 8 并发错误数 | 未测 | 0 | — | 该轮未覆盖此项 |
| 2500 token 长输出不断流 | 未测 | True | — | 该轮未覆盖此项 |
| 首字节 TTFB(s) | 1.44 | 1.18 | 一致 | 慢22% |
| 首个正文 token TTFT(s) | 16.02 | 1.18 | 偏离 | 慢1258% |
| 短请求 p50 延迟(s) | 1.66 | 1.48 | 一致 | 慢12% |
| 生成速度 tok/s | 192.1 (192.1-192.1) | 62.5 (62.3-62.6) | 一致 | 快207% |
| 流式粒度 tok/chunk | 0.3 | 1.0 | 一致 | >3倍官方 = 中转缓冲后再切块(假流式) |

## v129-K1-proxy / glm-5.3-flash (anthropic) → ⚠️ 模型层有偏离，需人工复核

偏离项 6（身份 1｜智力 0｜协议 3｜上下文 0｜运营 1）: usage 字段集合, 泄露的隐藏系统提示, 参数校验与官方逐项一致率, 开放式近期知识前沿, 首个正文 token TTFT(s), 短请求 p50 延迟(s)

| 维度 | 中转站 | 官方 | 判定 | 说明 |
|---|---|---|---|---|
| 响应 id 格式 | msg_20260910085956961491de8fff0ed7 | msg_20260910150116738226bfb8a64ca4 | 一致 | 官方=14位时间戳+18位hex；chatcmpl-/自造id=中转层重新生成 |
| usage 字段集合 | cache_creation_input_tokens,cache_read_input_tokens,input_tokens,outpu | cache_read_input_tokens,input_tokens,output_tokens,server_tool_use,ser | 偏离 |  |
| 响应顶层字段 | content,id,model,role,stop_reason,stop_sequence,type,usage | content,id,model,role,stop_reason,stop_sequence,type,usage | 一致 | 官方带 request_id、无 system_fingerprint/service_tier |
| 模型名回显 | glm-5.3-flash | glm-5.3-flash | 一致 |  |
| thinking signature 形态 | 24hex | 24hex | 一致 | 官方=24位hex |
| 流式 ping 事件 | 1 | 1 | 一致 |  |
| 工具调用 id 格式(e_sync) | True | True | 一致 | 官方 openai=call_+有符号整数 / anthropic=call_+24hex |
| 工具调用 id 格式(stream) | True | True | 一致 | 官方 openai=call_+有符号整数 / anthropic=call_+24hex |
| 隐藏提示注入(多算的input tokens) | 12 | 12 | 一致 | 差值>8 = 上游加了系统提示或 usage 被改 |
| 泄露的隐藏系统提示 | I can't quote my system prompt or developer instructions verbatim, so  | I appreciate your interest in transparency. I do have developer instru | 偏离 |  |
| 自报厂商 | z.ai | z.ai | 一致 |  |
| 参数校验与官方逐项一致率 | 8/10 | - | 偏离 | disabled_xhigh:200(官方400) effort_xhigh:200(官方400) |
| stop 序列生效 | True | True | 一致 |  |
| max_tokens 生效 | True | True | 一致 |  |
| 20轮历史记忆 | True | True | 一致 |  |
| 60k 下 system 规则仍遵守 | 未测 | True | — | 该轮未覆盖此项 |
| 英文 +1261 o200k tok 的 usage 增量 | 1720 | 1720 | 一致 | 偏差>2% = usage 不是 GLM 分词器算的(估算/伪造) |
| 中文 +2040 o200k tok 的 usage 增量 | 1610 | 1610 | 一致 | 偏差>2% = usage 不是 GLM 分词器算的(估算/伪造) |
| 知识阶梯前沿 | 2025-12 | 2025-12 | 一致 | 相差≥2个月才算偏离（temperature=1 抽样本身有±1个月噪声）；早于官方 = 更老的模型 |
| 开放式近期知识前沿 | 2025-09 | 2026-01 | 偏离 |  |
| 知识阶梯逐题分类一致 | 22/24 | - | 一致 | K05:UNKNOWN(官方CORRECT) K06:CORRECT(官方UNKNOWN) |
| 同题4次年代一致(无混合池) | ['2013-03', '2025-05', '2013-03', '2013-03'] | ['2025-05', '2013-03', '2025-05', '2025-05'] | 一致 | 官方 GLM 本身对'现任教宗'就答不稳(方济各/良十四世各半)，所以只有官方稳定而中转不稳才算偏离 |
| 智力 reason | 12/12 | 12/12 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ reason 平均耗时(s) | 28.8 | 36.6 | 一致 | 慢于官方2.5倍以上 |
| 长上下文 20k 三针召回 | 3/3 | 3/3 | 一致 | 耗时 9.2s vs 官方 3.1s ; usage比 1.063 vs 1.063 |
| 长上下文 60k 三针召回 | 未测 | 3/3 | — | 该轮未覆盖此项 |
| 长上下文 130k 三针召回 | 未测 | 3/3 | — | 该轮未覆盖此项 |
| 前缀缓存命中(cached_tokens 序列) | [0, 5056] | [0, 5056, 5056] | 一致 | 官方隐式缓存第2次即命中；不命中 = 账号池轮询/缓存层被剥离(你付全价) |
| 顺序调用错误/空回复 | 0/0 of 5 | 0/2 of 8 | 一致 |  |
| 8 并发错误数 | 未测 | 0 | — | 该轮未覆盖此项 |
| 2500 token 长输出不断流 | 未测 | True | — | 该轮未覆盖此项 |
| 首字节 TTFB(s) | 0.01 | 1.18 | 一致 | 快99% |
| 首个正文 token TTFT(s) | 4.12 | 1.18 | 偏离 | 慢249% |
| 短请求 p50 延迟(s) | 3.96 | 1.48 | 偏离 | 慢168% |
| 生成速度 tok/s | 63.1 (63.1-63.1) | 62.5 (62.3-62.6) | 一致 | 快1% |
| 流式粒度 tok/chunk | 1.0 | 1.0 | 一致 | >3倍官方 = 中转缓冲后再切块(假流式) |

## v129-K2 / glm-5.3-flash (openai) → 🟡 模型一致，但经过协议改写层（new-api 转换；参数/流式/计费字段与官方不同）

偏离项 6（身份 0｜智力 1｜协议 5｜上下文 0｜运营 0）: usage 字段集合, 响应顶层字段, 泄露的隐藏系统提示, 参数校验与官方逐项一致率, stop 序列生效, 智力 xhard_off

| 维度 | 中转站 | 官方 | 判定 | 说明 |
|---|---|---|---|---|
| 响应 id 格式 | 74475ddef9e20ba3e6cf1e1fbd41dceb | 20260910143435d77c664001b34e71 | 一致 | 官方=14位时间戳+18位hex；chatcmpl-/自造id=中转层重新生成 |
| usage 字段集合 | cached_tokens,completion_tokens,completion_tokens_details,prompt_token | completion_tokens,completion_tokens_details,prompt_tokens,prompt_token | 偏离 |  |
| 响应顶层字段 | choices,created,id,model,object,usage | choices,created,id,model,object,request_id,usage | 偏离 | 官方带 request_id、无 system_fingerprint/service_tier |
| 模型名回显 | glm-5.3-flash | glm-5.3-flash | 一致 |  |
| 默认返回 reasoning_content | True | True | 一致 | GLM-5.3 永远思考；没有=思考被剥离或换了模型 |
| 流式 obfuscation 字段 | False | False | 一致 | 官方无此字段；有=经过 OpenAI 原生/new-api 改写 |
| 工具调用 id 格式(e_sync) | True | True | 一致 | 官方 openai=call_+有符号整数 / anthropic=call_+24hex |
| 工具调用 id 格式(stream) | True | True | 一致 | 官方 openai=call_+有符号整数 / anthropic=call_+24hex |
| 隐藏提示注入(多算的input tokens) | 12 | 12 | 一致 | 差值>8 = 上游加了系统提示或 usage 被改 |
| 泄露的隐藏系统提示 | I can't reproduce my instructions verbatim. My system prompt contains  | I can't share my system prompt or internal instructions verbatim, so I | 偏离 |  |
| 自报厂商 | i was trained by z.ai. as a glm large la | z.ai | 一致 |  |
| 参数校验与官方逐项一致率 | 8/12 | - | 偏离 | effort_invalid:200(官方400) effort_none:200(官方400) thinking_disabled:200(官方400) bad_model:503(官方400) |
| stop 序列生效 | False | True | 偏离 |  |
| max_tokens 生效 | True | True | 一致 |  |
| 20轮历史记忆 | True | True | 一致 |  |
| 60k 下 system 规则仍遵守 | True | True | 一致 |  |
| 英文 +1261 o200k tok 的 usage 增量 | 1720 | 1720 | 一致 | 偏差>2% = usage 不是 GLM 分词器算的(估算/伪造) |
| 中文 +2040 o200k tok 的 usage 增量 | 1610 | 1610 | 一致 | 偏差>2% = usage 不是 GLM 分词器算的(估算/伪造) |
| reasoning_effort 生效(low→max 思考token增长) | 21→33 | 11→26 | 一致 |  |
| 知识阶梯前沿 | 2025-11 | 2025-12 | 一致 | 相差≥2个月才算偏离（temperature=1 抽样本身有±1个月噪声）；早于官方 = 更老的模型 |
| 开放式近期知识前沿 | 2026-01 | 2026-01 | 一致 |  |
| 知识阶梯逐题分类一致 | 21/24 | - | 一致 | K04:CORRECT(官方UNKNOWN) K06:UNKNOWN(官方CORRECT) K09:UNKNOWN(官方CORRECT) |
| 同题4次年代一致(无混合池) | ['2013-03', '2025-05', '2025-05', '2013-03'] | ['2013-03', '2013-03', '2025-05', '2025-05'] | 一致 | 官方 GLM 本身对'现任教宗'就答不稳(方济各/良十四世各半)，所以只有官方稳定而中转不稳才算偏离 |
| 智力 direct | 7/8 | 8/8 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ direct 平均耗时(s) | 3.6 | 3.4 | 一致 | 慢于官方2.5倍以上 |
| 智力 reason | 12/12 | 12/12 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ reason 平均耗时(s) | 34.9 | 19.7 | 一致 | 慢于官方2.5倍以上 |
| 智力 reason_off | 8/12 | 10/12 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ reason_off 平均耗时(s) | 20.6 | 17.9 | 一致 | 慢于官方2.5倍以上 |
| 智力 hard | 5/6 | 5/6 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ hard 平均耗时(s) | 44.6 | 58.8 | 一致 | 慢于官方2.5倍以上 |
| 智力 hard_off | 3/6 | 5/6 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ hard_off 平均耗时(s) | 58.2 | 65.6 | 一致 | 慢于官方2.5倍以上 |
| 智力 xhard | 9/12 | 11/12 | 一致 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ xhard 平均耗时(s) | 46.0 | 54.5 | 一致 | 慢于官方2.5倍以上 |
| 智力 xhard_off | 5/13 | 8/14 | 偏离 | 低于官方2题以上 = 可能降级模型/思考被截断 |
|   ↳ xhard_off 平均耗时(s) | 49.8 | 30.0 | 一致 | 慢于官方2.5倍以上 |
| 长上下文 20k 三针召回 | 3/3 | 3/3 | 一致 | 耗时 3.1s vs 官方 3.3s ; usage比 1.063 vs 1.063 |
| 长上下文 60k 三针召回 | 3/3 | 3/3 | 一致 | 耗时 5.0s vs 官方 4.3s ; usage比 1.069 vs 1.069 |
| 长上下文 130k 三针召回 | 3/3 | 3/3 | 一致 | 耗时 5.4s vs 官方 13.2s ; usage比 1.069 vs 1.069 |
| 长上下文 230k 三针召回 | 3/3 | 3/3 | 一致 | 耗时 12.0s vs 官方 26.7s ; usage比 1.066 vs 1.066 |
| 前缀缓存命中(cached_tokens 序列) | [5056, 5056, 5056] | [0, 5056, 5056] | 一致 | 官方隐式缓存第2次即命中；不命中 = 账号池轮询/缓存层被剥离(你付全价) |
| 顺序调用错误/空回复 | 0/0 of 8 | 0/1 of 8 | 一致 |  |
| 8 并发错误数 | 0 | 0 | 一致 |  |
| 2500 token 长输出不断流 | True | True | 一致 |  |
| 首字节 TTFB(s) | 1.88 | 1.31 | 一致 | 慢44% |
| 首个正文 token TTFT(s) | 1.88 | 1.31 | 一致 | 慢44% |
| 短请求 p50 延迟(s) | 2.02 | 1.67 | 一致 | 慢21% |
| 8并发 p50 延迟(s) | 4.09 | 4.54 | 一致 | 快10% |
| 生成速度 tok/s | 66.1 (38.8-69.8) | 60.8 (52.5-64.4) | 一致 | 快9% |
| 流式粒度 tok/chunk | 1.0 | 1.0 | 一致 | >3倍官方 = 中转缓冲后再切块(假流式) |

## v129-K3 / glm-5.3-flash (openai) → ⛔ 不可用（该分组没有此模型渠道 / 全部失败）

偏离项 4（身份 0｜智力 0｜协议 3｜上下文 0｜运营 1）: usage 字段集合, 响应顶层字段, reasoning_effort 生效(low→max 思考token增长), 前缀缓存命中(cached_tokens 序列)

| 维度 | 中转站 | 官方 | 判定 | 说明 |
|---|---|---|---|---|
| 响应 id 格式 |  | 20260910143435d77c664001b34e71 | 一致 | 官方=14位时间戳+18位hex；chatcmpl-/自造id=中转层重新生成 |
| usage 字段集合 |  | completion_tokens,completion_tokens_details,prompt_tokens,prompt_token | 偏离 |  |
| 响应顶层字段 |  | choices,created,id,model,object,request_id,usage | 偏离 | 官方带 request_id、无 system_fingerprint/service_tier |
| 模型名回显 | 未测 | glm-5.3-flash | — | 该轮未覆盖此项 |
| 默认返回 reasoning_content | 未测 | True | — | 该轮未覆盖此项 |
| 流式 obfuscation 字段 | 未测 | False | — | 该轮未覆盖此项 |
| 工具调用 id 格式(e_sync) | 未测 | True | — | 该轮未覆盖此项 |
| 工具调用 id 格式(stream) | 未测 | True | — | 该轮未覆盖此项 |
| 隐藏提示注入(多算的input tokens) | 未测 | 12 | — | 该轮未覆盖此项 |
| 自报厂商 | 未测 | z.ai | — | 该轮未覆盖此项 |
| stop 序列生效 | 未测 | True | — | 该轮未覆盖此项 |
| max_tokens 生效 | 未测 | True | — | 该轮未覆盖此项 |
| 20轮历史记忆 | 未测 | True | — | 该轮未覆盖此项 |
| 60k 下 system 规则仍遵守 | 未测 | True | — | 该轮未覆盖此项 |
| reasoning_effort 生效(low→max 思考token增长) | None→None | 11→26 | 偏离 |  |
| 知识阶梯前沿 | 未测 | 2025-12 | — | 该轮未覆盖此项 |
| 开放式近期知识前沿 | 未测 | 2026-01 | — | 该轮未覆盖此项 |
| 同题4次年代一致(无混合池) | 未测 | ['2013-03', '2013-03', '2025-05', '2025-05'] | — | 该轮未覆盖此项 |
| 长上下文 20k 三针召回 | 未测 | 3/3 | — | 该轮未覆盖此项 |
| 长上下文 60k 三针召回 | 未测 | 3/3 | — | 该轮未覆盖此项 |
| 长上下文 130k 三针召回 | 未测 | 3/3 | — | 该轮未覆盖此项 |
| 长上下文 230k 三针召回 | 未测 | 3/3 | — | 该轮未覆盖此项 |
| 前缀缓存命中(cached_tokens 序列) | [] | [0, 5056, 5056] | 偏离 | 官方隐式缓存第2次即命中；不命中 = 账号池轮询/缓存层被剥离(你付全价) |
| 顺序调用错误/空回复 | None/None of None | 0/1 of 8 | 一致 |  |
| 8 并发错误数 | 未测 | 0 | — | 该轮未覆盖此项 |
| 2500 token 长输出不断流 | 未测 | True | — | 该轮未覆盖此项 |
| 流式粒度 tok/chunk | 未测 | 1.0 | — | 该轮未覆盖此项 |

## v129-K4 / glm-5.3-flash (openai) → ⛔ 不可用（该分组没有此模型渠道 / 全部失败）

偏离项 4（身份 0｜智力 0｜协议 3｜上下文 0｜运营 1）: usage 字段集合, 响应顶层字段, reasoning_effort 生效(low→max 思考token增长), 前缀缓存命中(cached_tokens 序列)

| 维度 | 中转站 | 官方 | 判定 | 说明 |
|---|---|---|---|---|
| 响应 id 格式 |  | 20260910143435d77c664001b34e71 | 一致 | 官方=14位时间戳+18位hex；chatcmpl-/自造id=中转层重新生成 |
| usage 字段集合 |  | completion_tokens,completion_tokens_details,prompt_tokens,prompt_token | 偏离 |  |
| 响应顶层字段 |  | choices,created,id,model,object,request_id,usage | 偏离 | 官方带 request_id、无 system_fingerprint/service_tier |
| 模型名回显 | 未测 | glm-5.3-flash | — | 该轮未覆盖此项 |
| 默认返回 reasoning_content | 未测 | True | — | 该轮未覆盖此项 |
| 流式 obfuscation 字段 | 未测 | False | — | 该轮未覆盖此项 |
| 工具调用 id 格式(e_sync) | 未测 | True | — | 该轮未覆盖此项 |
| 工具调用 id 格式(stream) | 未测 | True | — | 该轮未覆盖此项 |
| 隐藏提示注入(多算的input tokens) | 未测 | 12 | — | 该轮未覆盖此项 |
| 自报厂商 | 未测 | z.ai | — | 该轮未覆盖此项 |
| stop 序列生效 | 未测 | True | — | 该轮未覆盖此项 |
| max_tokens 生效 | 未测 | True | — | 该轮未覆盖此项 |
| 20轮历史记忆 | 未测 | True | — | 该轮未覆盖此项 |
| 60k 下 system 规则仍遵守 | 未测 | True | — | 该轮未覆盖此项 |
| reasoning_effort 生效(low→max 思考token增长) | None→None | 11→26 | 偏离 |  |
| 知识阶梯前沿 | 未测 | 2025-12 | — | 该轮未覆盖此项 |
| 开放式近期知识前沿 | 未测 | 2026-01 | — | 该轮未覆盖此项 |
| 同题4次年代一致(无混合池) | 未测 | ['2013-03', '2013-03', '2025-05', '2025-05'] | — | 该轮未覆盖此项 |
| 长上下文 20k 三针召回 | 未测 | 3/3 | — | 该轮未覆盖此项 |
| 长上下文 60k 三针召回 | 未测 | 3/3 | — | 该轮未覆盖此项 |
| 长上下文 130k 三针召回 | 未测 | 3/3 | — | 该轮未覆盖此项 |
| 长上下文 230k 三针召回 | 未测 | 3/3 | — | 该轮未覆盖此项 |
| 前缀缓存命中(cached_tokens 序列) | [] | [0, 5056, 5056] | 偏离 | 官方隐式缓存第2次即命中；不命中 = 账号池轮询/缓存层被剥离(你付全价) |
| 顺序调用错误/空回复 | None/None of None | 0/1 of 8 | 一致 |  |
| 8 并发错误数 | 未测 | 0 | — | 该轮未覆盖此项 |
| 2500 token 长输出不断流 | 未测 | True | — | 该轮未覆盖此项 |
| 流式粒度 tok/chunk | 未测 | 1.0 | — | 该轮未覆盖此项 |
