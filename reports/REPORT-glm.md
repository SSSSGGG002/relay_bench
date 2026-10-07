# relay-bench 报告

结果文件: 9 个 (目录 results-glm)

## 0. 智力分档对比（拉开差距的核心）

每格 = 答对数/总题数（思考默认开启；`_off` = 强制关闭思考）。只统计当前题库 `suite/iq_keep.json` 里的 26 题；中转拒答/空响应不计入分母（括号内为剔除次数）。难度递增：reason < hard < xhard。

| 站点/模型 | reason | reason_off | hard | hard_off | xhard | xhard_off | 合计 |
|---|---|---|---|---|---|---|---|
| rtoc/glm-5.3-flash | 6/6 | 5/6 | 6/6 | 5/6 | 12/13 | 11/13 | **45/50** (中转故障剔除2) |
| rtoc-anthropic/glm-5.3-flash | 5/6 | 4/6 | 4/6 | 4/6 | 7/7 | 5/7 | **29/38** |
| v129-K1/glm-5.3-flash | 6/6 | 4/6 | 5/6 | 5/5 | 12/12 | 8/14 | **40/49** (中转故障剔除3) |
| v129-K1-anthropic/glm-5.3-flash | 6/6 | 5/6 | 6/6 | 5/6 | 6/7 | 5/5 | **33/36** (中转故障剔除2) |
| v129-K2/glm-5.3-flash | 6/6 | 2/6 | 5/6 | 3/6 | 9/12 | 5/13 | **30/49** (中转故障剔除3) |
| zhipu-official/glm-5.3-flash | 6/6 | 4/6 | 5/6 | 5/6 | 11/12 | 8/14 | **39/50** (中转故障剔除2) |
| zhipu-official-anthropic/glm-5.3-flash | 6/6 | 4/6 | 6/6 | 5/6 | 13/14 | 8/13 | **42/51** (中转故障剔除1) |

### 各题耗时（reason+hard+xhard，思考开启，单位秒）

| 站点/模型 | reason均 | hard均 | xhard均 |
|---|---|---|---|
| rtoc/glm-5.3-flash | 57.4 | 106.7 | 139.4 |
| rtoc-anthropic/glm-5.3-flash | 40.6 | 127.1 | 149.4 |
| v129-K1/glm-5.3-flash | 30.6 | 84.9 | 55.8 |
| v129-K1-anthropic/glm-5.3-flash | 27.7 | 63.9 | 58.9 |
| v129-K2/glm-5.3-flash | 34.9 | 44.6 | 46.0 |
| zhipu-official/glm-5.3-flash | 19.7 | 58.8 | 54.5 |
| zhipu-official-anthropic/glm-5.3-flash | 36.6 | 57.0 | 48.6 |

## 1. 总览矩阵

| 站点 | 模型 | 协议 | 结论 | 上游形态 | 参数一致率 | 知识前沿(阶梯/开放) | 自报 | tok比率EN | 注入tok | 缓存 | 缓存隔离/过期 | TTFT中位 | tok/s中位 | p50 | 并发成功 | soak错误率 | IQ直答 | IQ推理 | IQ困难 | IQ超难 | ctx20k | ctx60k | ctx130k | ctx230k | 红旗 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| rtoc | glm-5.3-flash | open | FAKE/ALTERED | ? 注入≈12 id=msg_20260 | 80%(10) | 2025-11/2026-01 | z.ai/- | 1.064 | 12 | 命中 | - | 84.63 | 187.6 | 2.17 | - | - | - | 6/6 | 6/6 | 12/13 | 3/3 | 3/3 | 3/3 | 3/3 | 3 |
| rtoc-anthropic | glm-5.3-flash | anth | FAKE/ALTERED | 真·Anthropic直连(thinking有效签名) id=msg_20260 | 80%(10) | 2025-11/2026-01 | z.ai/glm4.5 | 1.064 | 12 | 命中 | - | 2.49 | 32.0 | 2.55 | 8/8 | - | - | 5/6 | 4/6 | 7/7 | 3/3 | 3/3 | 3/3 | - | 1 |
| v129-K1 | glm-5.3-flash | open | FAKE/ALTERED | ? 注入≈12 id=7a46880dd | 70%(10) | 2025-12/2026-01 | z.ai/glm4.5 | 1.064 | 12 | 命中 | - | 1.77 | 63.6 | 1.99 | - | - | - | 6/6 | 5/6 | 12/12 | 3/3 | 3/3 | 3/3 | 3/3 | 4 |
| v129-K1-anthropic | glm-5.3-flash | anth | FAKE/ALTERED | ? 注入≈12 id=9b754e9bf | 80%(10) | 2025-11/2026-01 | z.ai/glm4.6 | 1.064 | 12 | 命中 | - | 16.02 | 192.1 | 1.66 | - | - | - | 6/6 | 6/6 | 6/7 | 3/3 | - | - | - | 3 |
| v129-K2 | glm-5.3-flash | open | FAKE/ALTERED | ? 注入≈12 id=74475ddef | 70%(10) | 2025-11/2026-01 | i was trained by z.ai. as a  | 1.064 | 12 | 命中 | - | 1.88 | 66.1 | 2.02 | - | - | - | 6/6 | 5/6 | 9/12 | 3/3 | 3/3 | 3/3 | 3/3 | 4 |
| v129-K3 | glm-5.3-flash | open | UNREACHABLE | ? 注入≈- id= | - | -/- | -/- | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | 1 |
| v129-K4 | glm-5.3-flash | open | UNREACHABLE | ? 注入≈- id= | - | -/- | -/- | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | 1 |
| zhipu-official | glm-5.3-flash | open | FAKE/ALTERED | ? 注入≈12 id=202609101 | 100%(10) | 2025-12/2026-01 | z.ai/glm4.5 | 1.064 | 12 | 命中 | - | 1.31 | 60.8 | 1.67 | - | - | - | 6/6 | 5/6 | 11/12 | 3/3 | 3/3 | 3/3 | 3/3 | 2 |
| zhipu-official-anthropic | glm-5.3-flash | anth | FAKE/ALTERED | 真·Anthropic直连(thinking有效签名) id=msg_20260 | 100%(10) | 2025-12/2026-01 | z.ai/glm4.5 | 1.064 | 12 | 命中 | - | 1.18 | 62.5 | 1.48 | - | - | - | 6/6 | 6/6 | 13/14 | 3/3 | 3/3 | 3/3 | - | 2 |

结论分级: CLEAN=无红旗; OK-ish=有轻微红旗; SUSPICIOUS=≥3个红旗; FAKE/ALTERED=知识截止/自报身份/签名证据表明不是所声称的模型。

## 2. 每个模型的红旗与关键证据

### rtoc / glm-5.3-flash  → **FAKE/ALTERED**
- 红旗: 同题4次答案年代不一致['2025-05', '2025-05', '2013-03', '2013-03'](混合池); 自报厂商=z.ai; 吞吐采样失败2次
- 自报: ``
- 知识前沿: 阶梯=2025-11 开放式=2026-01 判定=None (声称型号 glm-5.3-flash)
- 上限探针错误信息: `当前模型暂不可用 (request id: 202609100641514664340248268d9d6S5NrAbX7)`
- [WARN] protocol/message_id_format: id=msg_2026091014360855627beeb9934132 (NOT the Zhipu-native id format -> relay regenerates ids (new-api chatcmpl-… etc.))
- [WARN] protocol/zhipu_response_fields: top-level keys=['choices', 'created', 'id', 'model', 'object', 'usage'] system_fingerprint=None (official: has request_id, no system_fingerprint/service_tier)
- [WARN] passthrough/param_strictness: agreement with real-API behaviour for claimed 'glm-5.3-flash': 8/10 ; temperature:200✓ max_tokens_legacy:200✓ effort_invalid:400✓ logprobs:200✓ effort_none:200✗(exp 400) effort_max:200✓ n_2:200✓ max_out_100k:200✓ thinking_disabled:200✗(exp 400) temperature_out
- [WARN] protocol/max_tokens_limit_leak: max_completion_tokens=999999 -> HTTP 503 '当前模型暂不可用 (request id: 202609100641514664340248268d9d6S5NrAbX7)' (real API: 400 naming the true limit)
- [WARN] identity/effort_scaling: reasoning_tokens effort=low 0 vs effort=max 0 (effort has NO effect -> parameter stripped by relay or usage fabricated)
- [FAIL] knowledge/pool_mix: same question 4x gave different knowledge eras ['2025-05', '2025-05', '2013-03', '2013-03'] -> requests are routed to DIFFERENT underlying models (mixed account pool)
- [FAIL] context/system_rule_at_60k: ends with ZEBRA-42: False reply='tences that combine random word pairs with arbitrary numbers' status=200
- [FAIL] stability/sequential: 8 calls: errors=0 empty=8 p50=2.17s max=3.09s statuses=[200, 200, 200, 200, 200, 200, 200, 200] input_tokens=[17]
- [WARN] speed/throughput_empty_at_1200: empty visible text with max_tokens=1200 (variant=glm:effort=low, reasoning_tokens=1198, stop=length) -> thinking cannot be limited on this channel; retrying with max_tokens=8000
- [FAIL] speed/throughput: stream failed 200 {'type': 'http', 'code': None, 'message': ': PING\n\n: PING\n\n: PING\n\n: PING\n'} text_len=0 thinking_len=0 stop=None
- [FAIL] speed/throughput: stream failed 200 {'type': 'http', 'code': None, 'message': ': PING\n\n: PING\n\n: PING\n\n: PING\n'} text_len=0 thinking_len=0 stop=None
- [FAIL] speed/long_output_2500tok: status=200 stop=None numbers=0 last=None latency=50.0s chunks=0

### rtoc-anthropic / glm-5.3-flash  → **FAKE/ALTERED**
- 红旗: 自报厂商=z.ai
- 自报: ````json
{
  "vendor": "Z.ai",
  "model_family": "GLM",
  "model_version": "GLM-4.5",
  "knowledge_cutoff": "2024-10"
}
````
- 知识前沿: 阶梯=2025-11 开放式=2026-01 判定=consistent (声称型号 glm-5.3-flash)
- 并发8: 状态={'200': 8} p50=7.1s p95=17.48s
- 上限探针错误信息: `status_code=400, request_failed (request id: 202609100732292217740568268d9d641uF7ttM)`
- [WARN] passthrough/param_strictness: agreement with real-API behaviour for claimed 'glm-5.3-flash': 8/10 ; temperature:200✓ top_k:200✓ budget_tokens:200✓ prefill:200✓ disabled_xhigh:200✗(exp 400) effort_xhigh:200✗(exp 400) tool_choice_any:200✓ system_in_messages:200✓ unknown_beta_header:200✓ max_
- [WARN] protocol/count_tokens_endpoint: HTTP 301 
- [WARN] protocol/max_tokens_limit_leak: max_tokens=999999 -> HTTP 400 'status_code=400, request_failed (request id: 202609100732292217740568268d9d641uF7ttM)' (real API: 400 naming the true limit and model)
- [WARN] cache/input_tokens_unstable: identical prefix but input_tokens vary [5094, 38, 38] -> different upstream accounts/system prompts per call
- [WARN] stability/sequential: 8 calls: errors=0 empty=1 p50=2.55s max=10.29s statuses=[200, 200, 200, 200, 200, 200, 200, 200] input_tokens=[17]

### v129-K1 / glm-5.3-flash  → **FAKE/ALTERED**
- 红旗: 同题4次答案年代不一致['2025-05', '2013-03', '2025-05', '2013-03'](混合池); 自报厂商=z.ai; stop序列被忽略; 空响应/截断3次(可靠性差)
- 自报: ````json
{
  "vendor": "Z.ai",
  "model_family": "GLM",
  "model_version": "GLM-4.5",
  "knowledge_cutoff": "2024-10"
}
````
- 知识前沿: 阶梯=2025-12 开放式=2026-01 判定=None (声称型号 glm-5.3-flash)
- 泄露的隐藏系统提示: `I can't share the verbatim text of my system prompt or instructions, as those are confidential. If you're curious about how I work or what I can help with, I'm `
- [WARN] protocol/message_id_format: id=7a46880dd9ba13849e8008ee368c6d00 (NOT the Zhipu-native id format -> relay regenerates ids (new-api chatcmpl-… etc.))
- [WARN] protocol/zhipu_response_fields: top-level keys=['choices', 'created', 'id', 'model', 'object', 'usage'] system_fingerprint=None (official: has request_id, no system_fingerprint/service_tier)
- [WARN] passthrough/param_strictness: agreement with real-API behaviour for claimed 'glm-5.3-flash': 7/10 ; temperature:200✓ max_tokens_legacy:200✓ effort_invalid:200✗(exp 400) logprobs:200✓ effort_none:200✗(exp 400) effort_max:200✓ n_2:200✓ max_out_100k:200✓ thinking_disabled:200✗(exp 400) temper
- [FAIL] protocol/stop_sequences: stop=stop stop_sequence=None text='1, 2, 3, 4, 5, 6, 7, 8, 9, 10'
- [WARN] protocol/max_tokens_limit_leak: max_completion_tokens=999999 -> HTTP 200 'OK' (real API: 400 naming the true limit)
- [WARN] identity/hidden_system_prompt_exposed: model quoted instructions you never sent: "I can't share the verbatim text of my system prompt or instructions, as those are confidential. If you're curious about how I work or what I can help with, I'm happy to answer general questions about "
- [FAIL] knowledge/pool_mix: same question 4x gave different knowledge eras ['2025-05', '2013-03', '2025-05', '2013-03'] -> requests are routed to DIFFERENT underlying models (mixed account pool)
- [WARN] stability/sequential: 8 calls: errors=0 empty=1 p50=1.99s max=2.39s statuses=[200, 200, 200, 200, 200, 200, 200, 200] input_tokens=[17]

### v129-K1-anthropic / glm-5.3-flash  → **FAKE/ALTERED**
- 红旗: 同题4次答案年代不一致['2013-03', '2025-05', '2025-05', '2025-05'](混合池); 自报厂商=z.ai; stop序列被忽略
- 自报: ````json
{
  "vendor": "Z.ai",
  "model_family": "GLM",
  "model_version": "GLM-4.6",
  "knowledge_cutoff": "2024-10"
}
````
- 知识前沿: 阶梯=2025-11 开放式=2026-01 判定=consistent (声称型号 glm-5.3-flash)
- [WARN] protocol/message_id_format: id=9b754e9bfe92c69e121636cf6dffc36d (NOT the Zhipu-native id format -> id generated by relay/adapter)
- [WARN] protocol/usage_shape: usage keys=['billing_usage', 'cache_creation_input_tokens', 'cache_read_input_tokens', 'claude_cache_creation_1_h_tokens', 'claude_cache_creation_5_m_tokens', 'input_tokens', 'output_tokens'] ; NON-NATIVE keys ['billing_usage', 'claude_cache_creation_1_h_token
- [FAIL] protocol/thinking_default: default request has thinking block=False ; real glm-5.3-flash -> True
- [WARN] protocol/stream_ping: ping events=0 (native Anthropic streams send periodic pings; converted streams usually don't)
- [WARN] passthrough/param_strictness: agreement with real-API behaviour for claimed 'glm-5.3-flash': 8/10 ; temperature:200✓ top_k:200✓ budget_tokens:200✓ prefill:200✓ disabled_xhigh:200✗(exp 400) effort_xhigh:200✗(exp 400) tool_choice_any:200✓ system_in_messages:200✓ unknown_beta_header:200✓ max_
- [WARN] protocol/stop_sequences: stop=None stop_sequence=None text=''
- [WARN] protocol/count_tokens_endpoint: HTTP 404 {"error": {"message": "Invalid URL (POST /v1/messages/count_tokens)", "type": "invalid_request_error", "param": "", "code": ""}}
- [WARN] protocol/max_tokens_limit_leak: max_tokens=999999 -> HTTP 200 'OK' (real API: 400 naming the true limit and model)
- [WARN] identity/signature_shape: signature='' shape=None (official Zhipu: 24 hex chars, not a real Anthropic signature)
- [FAIL] knowledge/pool_mix: same question 4x gave different knowledge eras ['2013-03', '2025-05', '2025-05', '2025-05'] -> requests are routed to DIFFERENT underlying models (mixed account pool)
- [FAIL] stability/sequential: 5 calls: errors=0 empty=5 p50=1.66s max=2.14s statuses=[200, 200, 200, 200, 200] input_tokens=[17]
- [WARN] speed/throughput_empty_at_1200: empty visible text with max_tokens=1200 (variant=glm:effort=low, reasoning_tokens=None, stop=max_tokens) -> thinking cannot be limited on this channel; retrying with max_tokens=8000

### v129-K2 / glm-5.3-flash  → **FAKE/ALTERED**
- 红旗: 同题4次答案年代不一致['2013-03', '2025-05', '2025-05', '2013-03'](混合池); 自报厂商=i was trained by z.a; stop序列被忽略; 空响应/截断3次(可靠性差)
- 自报: ````json
{
  "vendor": "Z.ai",
  "model_family": "GLM",
  "model_version": "GLM-4.6",
  "knowledge_cutoff": "2024-06"
}
````
- 知识前沿: 阶梯=2025-11 开放式=2026-01 判定=consistent (声称型号 glm-5.3-flash)
- 泄露的隐藏系统提示: `I can't reproduce my instructions verbatim. My system prompt contains operational guidance that isn't meant to be quoted back in full, as doing so could help pe`
- [WARN] protocol/message_id_format: id=74475ddef9e20ba3e6cf1e1fbd41dceb (NOT the Zhipu-native id format -> relay regenerates ids (new-api chatcmpl-… etc.))
- [WARN] protocol/zhipu_response_fields: top-level keys=['choices', 'created', 'id', 'model', 'object', 'usage'] system_fingerprint=None (official: has request_id, no system_fingerprint/service_tier)
- [WARN] passthrough/param_strictness: agreement with real-API behaviour for claimed 'glm-5.3-flash': 7/10 ; temperature:200✓ max_tokens_legacy:200✓ effort_invalid:200✗(exp 400) logprobs:200✓ effort_none:200✗(exp 400) effort_max:200✓ n_2:200✓ max_out_100k:200✓ thinking_disabled:200✗(exp 400) temper
- [FAIL] protocol/stop_sequences: stop=stop stop_sequence=None text='1, 2, 3, 4, 5, 6, 7, 8, 9, 10'
- [WARN] protocol/max_tokens_limit_leak: max_completion_tokens=999999 -> HTTP 200 'OK' (real API: 400 naming the true limit)
- [WARN] identity/hidden_system_prompt_exposed: model quoted instructions you never sent: "I can't reproduce my instructions verbatim. My system prompt contains operational guidance that isn't meant to be quoted back in full, as doing so could help people craft ways to bypass my guidelines."
- [FAIL] knowledge/pool_mix: same question 4x gave different knowledge eras ['2013-03', '2025-05', '2025-05', '2013-03'] -> requests are routed to DIFFERENT underlying models (mixed account pool)

### v129-K3 / glm-5.3-flash  → **UNREACHABLE**
- 红旗: basic call failed
- 自报: ``
- 知识前沿: 阶梯=None 开放式=None 判定=None (声称型号 glm-5.3-flash)
- [WARN] protocol/basic_retries: all 3 attempts failed: [503, 503, 503]
- [FAIL] protocol/basic: HTTP 503 {'type': 'new_api_error', 'code': 'model_not_found', 'message': '分组 国产混合2 下模型 glm-5.3-flash 无可用渠道（distributor） (request id: 202609100729117823498868268d9d6C7uTiQEe)'}

### v129-K4 / glm-5.3-flash  → **UNREACHABLE**
- 红旗: basic call failed
- 自报: ``
- 知识前沿: 阶梯=None 开放式=None 判定=None (声称型号 glm-5.3-flash)
- [WARN] protocol/basic_retries: all 3 attempts failed: [503, 503, 503]
- [FAIL] protocol/basic: HTTP 503 {'type': 'new_api_error', 'code': 'model_not_found', 'message': '分组 国产混合特惠 下模型 glm-5.3-flash 无可用渠道（distributor） (request id: 202609100729452641273188268d9d6P9K0J9Vj)'}

### zhipu-official / glm-5.3-flash  → **FAKE/ALTERED**
- 红旗: 同题4次答案年代不一致['2013-03', '2013-03', '2025-05', '2025-05'](混合池); 自报厂商=z.ai
- 自报: ````json
{
  "vendor": "Z.ai",
  "model_family": "GLM",
  "model_version": "GLM-4.5",
  "knowledge_cutoff": "2024-10"
}
````
- 知识前沿: 阶梯=2025-12 开放式=2026-01 判定=None (声称型号 glm-5.3-flash)
- 泄露的隐藏系统提示: `I can't share my system prompt or internal instructions verbatim, so I can't fulfill that request as written. If you said "NONE," that also wouldn't be accurate`
- 上限探针错误信息: `max_tokens参数非法：限制数值范围[1,131072]`
- [WARN] protocol/responses_endpoint: HTTP 404 status=404 injected_instructions_len=0 head=''
- [WARN] identity/hidden_system_prompt_exposed: model quoted instructions you never sent: 'I can\'t share my system prompt or internal instructions verbatim, so I can\'t fulfill that request as written. If you said "NONE," that also wouldn\'t be accurate — I do have instructions guiding this c'
- [FAIL] knowledge/pool_mix: same question 4x gave different knowledge eras ['2013-03', '2013-03', '2025-05', '2025-05'] -> requests are routed to DIFFERENT underlying models (mixed account pool)
- [WARN] stability/sequential: 8 calls: errors=0 empty=1 p50=1.67s max=2.26s statuses=[200, 200, 200, 200, 200, 200, 200, 200] input_tokens=[17]

### zhipu-official-anthropic / glm-5.3-flash  → **FAKE/ALTERED**
- 红旗: 同题4次答案年代不一致['2025-05', '2013-03', '2025-05', '2025-05'](混合池); 自报厂商=z.ai
- 自报: ````json
{
  "vendor": "Z.ai",
  "model_family": "GLM",
  "model_version": "GLM-4.5",
  "knowledge_cutoff": "2024-10"
}
````
- 知识前沿: 阶梯=2025-12 开放式=2026-01 判定=consistent (声称型号 glm-5.3-flash)
- 泄露的隐藏系统提示: `I appreciate your interest in transparency. I do have developer instructions, but I'm not able to provide them verbatim on request, as doing so could enable mis`
- 上限探针错误信息: `[1210][max_tokens参数非法：限制数值范围[1,131072]][202609101501586469a3b733964cbc]`
- [WARN] identity/hidden_system_prompt_exposed: model quoted instructions you never sent: "I appreciate your interest in transparency. I do have developer instructions, but I'm not able to provide them verbatim on request, as doing so could enable misuse (e.g., crafting prompts designed to "
- [FAIL] knowledge/pool_mix: same question 4x gave different knowledge eras ['2025-05', '2013-03', '2025-05', '2025-05'] -> requests are routed to DIFFERENT underlying models (mixed account pool)
- [WARN] cache/input_tokens_unstable: identical prefix but input_tokens vary [5094, 38, 38] -> different upstream accounts/system prompts per call
- [FAIL] stability/sequential: 8 calls: errors=0 empty=2 p50=1.48s max=2.31s statuses=[200, 200, 200, 200, 200, 200, 200, 200] input_tokens=[17]

## 3. 知识截止阶梯 (✓知道 ?不知道 ✗答错 !错误)

| 题 | 日期 | rtoc/glm-5.3-flash | rtoc-anthropic/glm-5.3-flash | v129-K1/glm-5.3-flash | v129-K1-anthropic/glm-5.3-flash | v129-K2/glm-5.3-flash | zhipu-official/glm-5.3-flash | zhipu-official-anthropic/glm-5.3-flash |
|---|---|---|---|---|---|---|---|---|
| K00 | 2024-11 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| K01 | 2025-05 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| K02 | 2025-06 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| K03 | 2025-08 | ✓ | ✓ | ✓ | ? | ✓ | ✓ | ✓ |
| K04 | 2025-10 | ? | ✓ | ? | ✓ | ✓ | ? | ✓ |
| K05 | 2025-10 | ? | ? | ? | ? | ? | ? | ✓ |
| K06 | 2025-11 | ? | ✓ | ? | ? | ? | ✓ | ? |
| K07 | 2025-11 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| K08 | 2025-12 | ? | ? | ? | ? | ? | ? | ? |
| K09 | 2025-12 | ? | ? | ✓ | ? | ? | ✓ | ✓ |
| K10 | 2026-01 | ? | ? | ? | ? | ? | ? | ? |
| K11 | 2026-02 | ? | ? | ? | ? | ? | ? | ? |
| K12 | 2026-02 | ? | ? | ? | ? | ? | ? | ? |
| K13 | 2026-03 | ? | ? | ? | ? | ? | ? | ? |
| K14 | 2026-03 | ? | ? | ? | ? | ? | ? | ? |
| K15 | 2026-04 | ? | ? | ? | ? | ? | ? | ? |
| K16 | 2026-05 | ? | ? | ? | ? | ? | ? | ? |
| K17 | 2026-05 | ? | ? | ? | ? | ? | ? | ? |
| K18 | 2026-06 | ? | ? | ? | ? | ? | ? | ? |
| K19 | 2026-06 | ? | ? | ? | ? | ? | ? | ? |
| K20 | 2026-07 | ? | ? | ? | ? | ? | ? | ? |
| K21 | 2026-07 | ? | ? | ? | ? | ? | ? | ? |
| K22 | 2026-07 | ? | ? | ? | ? | ? | ? | ? |
| K23 | 2026-09 | ? | ? | ? | ? | ? | ? | ? |

## 3b. 开放式近期知识探针 (答案所属年代)

| 题 | rtoc/glm-5.3-flash | rtoc-anthropic/glm-5.3-flash | v129-K1/glm-5.3-flash | v129-K1-anthropic/glm-5.3-flash | v129-K2/glm-5.3-flash | zhipu-official/glm-5.3-flash | zhipu-official-anthropic/glm-5.3-flash |
|---|---|---|---|---|---|---|---|
| C1 | 2013-03 `Pope Francis, born Jor` | 2013-03 `As of my knowledge cut` | 2025-05 `Pope Francis is the po` | 2025-05 `Pope Leo XIV (Robert P` | 2025-05 `Pope Leo XIV (Robert P` | 2025-05 `Pope Francis is the cu` | 2025-05 `Pope Leo XIV (Robert P` |
| C2 | 2024-10 `Shigeru Ishiba, who to` | 2025-10 `Shigeru Ishiba (as of ` | 2024-10 `Shigeru Ishiba, who be` | 2025-10 `Sanae Takaichi, who be` | 2024-10 `Shigeru Ishiba is the ` | 2025-10 `Sanae Takaichi became ` | 2024-10 `Shigeru Ishiba, who be` |
| C3 | 2026-01 `Zohran Mamdani, a Demo` | 2026-01 `Zohran Mamdani, who wo` | 2026-01 `As of my knowledge cut` | 2026-01 `As of my knowledge cut` | 2026-01 `Eric Adams (though he ` | 2026-01 `Zohran Mamdani, who to` | 2026-01 `Zohran Mamdani, who to` |
| C4 | 1989-06 `Ali Khamenei` | 1989-06 `Ali Khamenei.` | 1989-06 `Ali Khamenei` | 1989-06 `Ali Khamenei, Supreme ` | 1989-06 `Ali Khamenei.` | 1989-06 `Ali Khamenei has been ` | 1989-06 `Ali Khamenei has been ` |
| C5 | 2025-02 `Philadelphia Eagles wo` | 2024-02 `Kansas City Chiefs won` | 2024-02 `Kansas City Chiefs, Su` | 2025-02 `The Philadelphia Eagle` | 2024-02 `The Kansas City Chiefs` | 2024-02 `The Kansas City Chiefs` | 2024-02 `The Kansas City Chiefs` |
| C6 | 2022-12 `Argentina won the most` | 2022-12 `Argentina won the 2022` | 2022-12 `Argentina won the 2022` | 2022-12 `Argentina won the 2022` | 2022-12 `Argentina, in 2022, de` | 2022-12 `Argentina won the 2022` | 2022-12 `Argentina won the 2022` |
| C7 | 2024-10 `Han Kang of South Kore` | 2024-10 `Han Kang, awarded the ` | 2023-10 `Jon Fosse, the Norwegi` | 2024-10 `Han Kang of South Kore` | 2024-10 `Han Kang of South Kore` | 2023-10 `The 2023 Nobel Prize i` | 2025-10 `László Krasznahorkai, ` |
| C8 | 2025-05 `Claude Opus 4 and Clau` | 2025-11 `Claude Opus 4.5 (API n` | 2000-01 `I apologize, but I do ` | 2024-10 `Claude 3.5 Sonnet (cla` | 2025-05 `Claude Opus 4 (alongsi` | 2025-11 `Claude Opus 4.5 (Annou` | 2024-10 `Claude 3.5 Sonnet, rel` |
| C9 | 2024-05 `GPT-4o (specifically t` | 2025-04 `GPT-4.1 (released Apri` | 2024-05 `GPT-4o (GPT-4 "omni"),` | 2025-02 `GPT-4.5 ("GPT-4.5"), r` | 2024-05 `GPT-4o (Omni), announc` | 2024-05 `GPT-4o (with variants ` | 2024-05 `The most recent I know` |
| C10 | 2025-01 `Donald Trump, who took` | 2025-01 `Donald Trump (as of my` | 2025-01 `As of my knowledge cut` | 2025-01 `Donald Trump, inaugura` | 2025-01 `Donald Trump, who bega` | 2025-01 `Donald Trump.` | 2025-01 `Donald Trump, as of my` |

## 4. IQ 分题矩阵

| 题 | 模式 | rtoc/glm-5.3-flash | rtoc-anthropic/glm-5.3-flash | v129-K1/glm-5.3-flash | v129-K1-anthropic/glm-5.3-flash | v129-K2/glm-5.3-flash | zhipu-official/glm-5.3-flash | zhipu-official-anthropic/glm-5.3-flash |
|---|---|---|---|---|---|---|---|---|
| R2 | default | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| R2 | off | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ |
| R3 | default | ✓ | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ |
| R3 | off | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ |
| R4 | default | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| R4 | off | ✓ | ✗ | ✗ | ✓ | ✗ | ✗ | ✓ |
| R7 | default | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| R7 | off | ✓ | ✗ | ✗ | ✓ | ✓ | ✓ | ✓ |
| R9 | default | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| R9 | off | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ |
| R10 | default | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| R10 | off | ✗ | ✓ | ✓ | ✗ | ✗ | ✓ | ✓ |
| H1 | default | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| H1 | off | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ |
| H2 | default | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| H2 | off | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| H3 | default | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| H3 | off | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ |
| H4 | default | ✓ | ✗ | ✓ | ✓ | ✗ | ✗ | ✓ |
| H4 | off | ✗ | ✗ | ✓ | ✗ | ✓ | ✗ | ✓ |
| H5 | default | ✓ | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ |
| H5 | off | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| H6 | default | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | ✓ |
| H6 | off | ✓ | ✗ | ✗ | ✓ | ✗ | ✓ | ✗ |
| X1 | default | ✓ | ✓ | ✓ | ✗ | ✗ | ✓ | ✓ |
| X1 | off | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ |
| X2 | default | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| X2 | off | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | ✓ |
| X3 | default | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ |
| X3 | off | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| X4 | default | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| X4 | off | ✓ | ✗ | ✓ | ✓ | ✗ | ✗ | ✗ |
| X5 | default | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| X5 | off | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| X6 | default | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| X6 | off | ✓ | ✓ | ✗ | ✓ | ✗ | ✓ | ✗ |
| X7 | default | ✗ | ✓ | ✗ | ✓ | ✗ | ✗ | ✓ |
| X7 | off | ✗ | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ |
| X8 | default | ✓ |  | ✗ |  | ✗ | ✗ | ✓ |
| X8 | off | ✗ |  | ✗ |  | ✓ | ✓ | ✗ |
| X9 | default | ✓ |  | ✓ |  | ✓ | ✓ | ✗ |
| X9 | off | ✓ |  | ✓ |  | ✓ | ✓ | ✓ |
| X10 | default | ✓ |  | ✓ |  | ✓ | ✓ | ✓ |
| X10 | off | ✓ |  | ✓ |  | ✓ | ✓ | ✓ |
| X11 | default | ✓ |  | ✓ |  | ✓ | ✓ | ✓ |
| X11 | off | ✓ |  | ✓ |  | ✗ | ✓ | ✓ |
| X12 | default | ✓ |  | ✓ |  | ✗ | ✓ | ✓ |
| X12 | off | ✗ |  | ✗ |  | ✗ | ✗ | ✓ |
| X13 | default | ✓ |  | ✓ |  | ✓ | ✗ | ✓ |
| X13 | off | ✓ |  | ✗ |  | ✗ | ✗ | ✗ |
| X14 | default | ✓ |  | ✓ |  | ✓ | ✓ | ✓ |
| X14 | off | ✓ |  | ✓ |  | ✗ | ✗ | ✓ |

## 5. 同站点跨模型聚类 (相同输出 = 很可能同一上游)

### rtoc-anthropic

### rtoc

### v129-K1-anthropic

### v129-K1

### v129-K2

### zhipu-official-anthropic

### zhipu-official
