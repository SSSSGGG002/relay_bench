# relay-bench 报告

结果文件: 35 个 (目录 results)

## 0. 智力分档对比（拉开差距的核心）

每格 = 答对数/总题数（思考默认开启；`_off` = 强制关闭思考）。只统计当前题库 `suite/iq_keep.json` 里的 26 题；中转拒答/空响应不计入分母（括号内为剔除次数）。难度递增：reason < hard < xhard。

| 站点/模型 | screen | reason | reason_off | hard | hard_off | xhard | xhard_off | 合计 |
|---|---|---|---|---|---|---|---|---|
| bit/haiku-4-5 | - | 0/5 | 0/5 | - | - | - | - | **0/10** (中转故障剔除2) |
| bit/opus-4-6 | - | 3/6 | 5/6 | - | - | - | - | **8/12** |
| bit/opus-4-7 | - | 5/6 | 3/6 | - | - | - | - | **8/12** |
| bit/opus-4-8 | - | 3/6 | 3/6 | - | - | - | - | **6/12** |
| bit/opus-5 | - | 6/6 | 6/6 | 6/6 | 6/6 | 12/12 | 12/12 | **48/48** (中转故障剔除4) |
| bit/sonnet-5 | - | 6/6 | 6/6 | 6/6 | 6/6 | 12/12 | 12/12 | **48/48** (中转故障剔除4) |
| bit-screen/haiku-4-5 | 2/8 | - | - | - | - | - | - | **2/8** |
| bit-screen/opus-4-6 | 5/8 | - | - | - | - | - | - | **5/8** |
| bit-screen/opus-5 | 7/7 | - | - | - | - | - | - | **7/7** (中转故障剔除1) |
| bit-screen/sonnet-5 | 8/8 | - | - | - | - | - | - | **8/8** |
| codex666-screen/opus-5 | 6/8 | - | - | - | - | - | - | **6/8** |
| codex666-screen/sonnet-5 | 6/8 | - | - | - | - | - | - | **6/8** |
| dragon3/fable-5 | 6/8 | - | - | - | - | - | - | **6/8** |
| dragon3/opus-5 | - | 4/6 | 5/6 | 2/6 | 4/6 | 7/14 | 8/14 | **30/52** |
| dragon3/sonnet-5 | 6/8 | - | - | - | - | - | - | **6/8** |
| rtoc/glm-5.3-flash | - | 6/6 | 5/6 | 6/6 | 5/6 | 12/13 | 11/13 | **45/50** (中转故障剔除2) |
| rtoc-anthropic/glm-5.3-flash | - | 5/6 | 4/6 | 4/6 | 4/6 | 7/7 | 5/7 | **29/38** |
| tokenking/fable-5-1 | - | 6/6 | - | 5/5 | - | 6/6 | - | **17/17** (中转故障剔除9) |
| twskyhope/fable-5-1 | - | 4/4 | 3/3 | 6/6 | 6/6 | 10/10 | 10/10 | **39/39** (中转故障剔除13) |
| v129-K1/glm-5.3-flash | - | 6/6 | 4/6 | 5/6 | 5/5 | 12/12 | 8/14 | **40/49** (中转故障剔除3) |
| v129-K1-anthropic/glm-5.3-flash | - | 6/6 | 5/6 | 6/6 | 5/6 | 6/7 | 5/5 | **33/36** (中转故障剔除2) |
| v129-K1-proxy/glm-5.3-flash | - | 6/6 | - | - | - | - | - | **6/6** |
| v129-K2/glm-5.3-flash | - | 6/6 | 2/6 | 5/6 | 3/6 | 9/12 | 5/13 | **30/49** (中转故障剔除3) |
| wawapii/opus-5 | - | 4/4 | 4/4 | 6/6 | 6/6 | 9/9 | 8/9 | **37/38** (中转故障剔除14) |
| wawapii/sonnet-5 | - | 6/6 | 5/6 | 6/6 | 5/6 | 12/12 | 11/14 | **45/50** (中转故障剔除2) |
| wawapii-cursor/opus-5 | - | 3/5 | 5/5 | 4/6 | 4/6 | 6/12 | 7/12 | **29/46** (中转故障剔除6) |
| wawapii-cursor/sonnet-5 | - | 4/6 | 3/6 | 2/5 | 3/6 | 3/3 | 2/2 | **17/28** (中转故障剔除24) |
| zhipu-official/glm-5.3-flash | - | 6/6 | 4/6 | 5/6 | 5/6 | 11/12 | 8/14 | **39/50** (中转故障剔除2) |
| zhipu-official-anthropic/glm-5.3-flash | - | 6/6 | 4/6 | 6/6 | 5/6 | 13/14 | 8/13 | **42/51** (中转故障剔除1) |

### 各题耗时（reason+hard+xhard，思考开启，单位秒）

| 站点/模型 | reason均 | hard均 | xhard均 |
|---|---|---|---|
| bit/haiku-4-5 | 9.7 | - | - |
| bit/opus-4-6 | 13.6 | - | - |
| bit/opus-4-7 | 13.0 | - | - |
| bit/opus-4-8 | 13.1 | - | - |
| bit/opus-5 | 26.1 | 29.9 | 33.0 |
| bit/sonnet-5 | 37.0 | 53.3 | 108.6 |
| bit-screen/haiku-4-5 | - | - | - |
| bit-screen/opus-4-6 | - | - | - |
| bit-screen/opus-5 | - | - | - |
| bit-screen/sonnet-5 | - | - | - |
| codex666-screen/opus-5 | - | - | - |
| codex666-screen/sonnet-5 | - | - | - |
| dragon3/fable-5 | - | - | - |
| dragon3/opus-5 | 15.1 | 19.9 | 15.9 |
| dragon3/sonnet-5 | - | - | - |
| rtoc/glm-5.3-flash | 57.4 | 106.7 | 139.4 |
| rtoc-anthropic/glm-5.3-flash | 40.6 | 127.1 | 149.4 |
| tokenking/fable-5-1 | 20.0 | 27.2 | 12.0 |
| twskyhope/fable-5-1 | 29.3 | 69.8 | 27.4 |
| v129-K1/glm-5.3-flash | 30.6 | 84.9 | 55.8 |
| v129-K1-anthropic/glm-5.3-flash | 27.7 | 63.9 | 58.9 |
| v129-K1-proxy/glm-5.3-flash | 28.8 | - | - |
| v129-K2/glm-5.3-flash | 34.9 | 44.6 | 46.0 |
| wawapii/opus-5 | 91.2 | 138.9 | 99.1 |
| wawapii/sonnet-5 | 56.6 | 55.0 | 64.5 |
| wawapii-cursor/opus-5 | 15.6 | 20.5 | 26.3 |
| wawapii-cursor/sonnet-5 | 27.4 | 15.3 | 9.3 |
| zhipu-official/glm-5.3-flash | 19.7 | 58.8 | 54.5 |
| zhipu-official-anthropic/glm-5.3-flash | 36.6 | 57.0 | 48.6 |

## 1. 总览矩阵

| 站点 | 模型 | 协议 | 结论 | 上游形态 | 参数一致率 | 知识前沿(阶梯/开放) | 自报 | tok比率EN | 注入tok | 缓存 | 缓存隔离/过期 | TTFT中位 | tok/s中位 | p50 | 并发成功 | soak错误率 | IQ直答 | IQ推理 | IQ困难 | IQ超难 | ctx20k | ctx60k | ctx130k | ctx230k | 红旗 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| bitmiracle | claude-haiku-4-5-20251001 | anth | FAKE/ALTERED | Kiro/Bedrock 注入≈4 id=msg_6ce8c | 62%(8) | -/2024-10 | i can't discuss that./-3.5 | 0.121 | 4 | 命中 | - | 1.86 | 81.4 | 1.75 | - | - | - | 0/5 | - | - | 3/3 | - | - | - | 5 |
| bitmiracle | claude-opus-4-6 | anth | SUSPICIOUS | 真·Anthropic直连(thinking有效签名) id=msg_U5nxw | 71%(7) | -/2025-02 | i can't discuss that./sonnet | 1.113 | 4 | 未命中 | - | 2.36 | 33.4 | 2.71 | - | - | - | 3/6 | - | - | 0/3 | - | - | - | 6 |
| bitmiracle | claude-opus-4-7 | anth | FAKE/ALTERED | 真·Anthropic直连(thinking有效签名) id=msg_Zq53L | 50%(8) | -/2025-02 | i cannot discuss that./sonne | 1.113 | 4 | 未命中 | - | 2.39 | 33.6 | 2.61 | - | - | - | 5/6 | - | - | 0/3 | - | - | - | 6 |
| bitmiracle | claude-opus-4-8 | anth | FAKE/ALTERED | 真·Anthropic直连(thinking有效签名) id=msg_rUCkZ | 56%(9) | -/2025-01 | i cannot discuss that./sonne | 1.113 | 4 | 未命中 | - | 2.3 | 35.5 | 2.62 | - | - | - | 3/6 | - | - | 0/3 | - | - | - | 6 |
| bitmiracle | claude-opus-5 | anth | FAKE/ALTERED | ClaudeCode池 注入≈8 id=msg_1acfa | 44%(9) | 2025-11/2025-09 | amazon/- | 1.886 | 8 | 命中 | iso=0/exp=0 | 20.78 | 99.6 | 2.55 | 12/12 | 0.017 | - | 6/6 | 6/6 | 12/12 | 3/3 | 3/3 | 3/3 | - | 8 |
| bitmiracle | claude-sonnet-5 | anth | FAKE/ALTERED | ClaudeCode池 注入≈8 id=msg_08f2d | 38%(8) | 2025-11/2024-10 | i can't discuss that./-2025 | 0.182 | 8 | 命中 | iso=0/exp=0 | 3.8 | 42.9 | 3.55 | 12/12 | 1.0 | - | 6/6 | 6/6 | 12/12 | 3/3 | 0/3 | 0/3 | - | 10 |
| bitmiracle-screen | claude-haiku-4-5-20251001 | anth | FAKE/ALTERED | Kiro/Bedrock 注入≈4 id=msg_6a19e | - | -/2024-10 | i can't discuss that./-3.5 | - | 4 | - | - | 2.17 | 64.4 | - | - | - | - | - | - | - | - | - | - | - | 3 |
| bitmiracle-screen | claude-opus-4-6 | anth | SUSPICIOUS | 真·Anthropic直连(thinking有效签名) id=msg_kjkpm | - | -/2025-02 | i cannot discuss that./sonne | - | 4 | - | - | 2.48 | 36.9 | - | - | - | - | - | - | - | - | - | - | - | 3 |
| bitmiracle-screen | claude-opus-5 | anth | FAKE/ALTERED | Kiro/Bedrock 注入≈8 id=msg_c9b02 | - | -/2025-09 | amazon/sonnet4.5 | - | 8 | - | - | 101.43 | 61.5 | - | - | - | - | - | - | - | - | - | - | - | 4 |
| bitmiracle-screen | claude-sonnet-5 | anth | FAKE/ALTERED | ? 注入≈8 id=msg_91fe5 | - | -/2025-01 | i can't discuss that./sonnet | - | 8 | - | - | 91.55 | 46.5 | - | - | - | - | - | - | - | - | - | - | - | 3 |
| codex666-screen | claude-opus-5 | anth | FAKE/ALTERED | 真·Anthropic直连(thinking有效签名) id=msg_mdyxs | - | -/2025-02 | anthropic/sonnet3.7 | - | 4 | - | - | 2.2 | 32.7 | - | - | - | - | - | - | - | - | - | - | - | 3 |
| codex666-screen | claude-sonnet-5 | anth | FAKE/ALTERED | 真·Anthropic直连(thinking有效签名) id=msg_aWBsT | - | -/2025-02 | anthropic/sonnet3.7 | - | 4 | - | - | 2.05 | 35.0 | - | - | - | - | - | - | - | - | - | - | - | 2 |
| dragon3 | claude-fable-5 | anth | FAKE/ALTERED | 真·Anthropic直连(thinking有效签名) id=msg_YGd1s | - | -/2024-10 | anthropic/sonnet3.7 | - | 4 | - | - | 2.19 | 37.3 | - | - | - | - | - | - | - | - | - | - | - | 3 |
| dragon3 | claude-haiku-4-5-20251001 | anth | CLEAN | ? 注入≈- id= | - | -/- | -/- | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | 0 |
| dragon3 | claude-opus-4-6 | anth | CLEAN | ? 注入≈- id= | - | -/- | -/- | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | 0 |
| dragon3 | claude-opus-4-8 | anth | CLEAN | ? 注入≈- id= | - | -/- | -/- | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | 0 |
| dragon3 | claude-opus-5 | anth | FAKE/ALTERED | ClaudeCode池 注入≈4 id=msg_4pJ7n | 33%(9) | -/2024-10 | /sonnet3.7 | - | 4 | 未命中 | - | 2.02 | 36.4 | - | - | - | - | 4/6 | 2/6 | 7/14 | ERR500 | 0/3 | 0/3 | 0/3 | 10 |
| dragon3 | claude-sonnet-4-6 | anth | CLEAN | ? 注入≈- id= | - | -/- | -/- | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | 0 |
| dragon3 | claude-sonnet-5 | anth | FAKE/ALTERED | 真·Anthropic直连(thinking有效签名) id=msg_DKxX0 | - | -/2024-10 | amazon/sonnet3.7 | - | 4 | - | - | 2.1 | 31.8 | - | - | - | - | - | - | - | - | - | - | - | 3 |
| rtoc | glm-5.3-flash | open | FAKE/ALTERED | ? 注入≈12 id=msg_20260 | 80%(10) | 2025-11/2026-01 | z.ai/- | 1.064 | 12 | 命中 | - | 84.63 | 187.6 | 2.17 | - | - | - | 6/6 | 6/6 | 12/13 | 3/3 | 3/3 | 3/3 | 3/3 | 3 |
| rtoc-anthropic | glm-5.3-flash | anth | OK-ish | 真·Anthropic直连(thinking有效签名) id=msg_20260 | 80%(10) | 2025-11/2026-01 | z.ai/glm4.5 | 1.064 | 12 | 命中 | - | 2.49 | 32.0 | 2.55 | 8/8 | - | - | 5/6 | 4/6 | 7/7 | 3/3 | 3/3 | 3/3 | - | 1 |
| tokenking | claude-fable-5-1 | anth | FAKE/ALTERED | ClaudeCode池 注入≈-1 id=chatcmpl- | 0%(9) | 2025-12/2026-09 | anthropic/- | -0.001 | -1 | 命中 | - | - | - | 5.74 | - | - | - | 6/6 | 5/5 | 6/6 | 2/3 | - | - | - | 6 |
| twskyhope | claude-fable-5-1 | anth | FAKE/ALTERED | 真·Anthropic直连(thinking有效签名) id=msg_01yoj | 22%(9) | 2026-02/2026-01 | anthropic/-2025 | - | 13 | 命中 | iso=0/exp=0 | 6.7 | 32.7 | 8.5 | 12/12 | 0.02 | - | 4/4 | 6/6 | 10/10 | 3/3 | 3/3 | 3/3 | - | 6 |
| v129-K1 | glm-5.3-flash | open | FAKE/ALTERED | ? 注入≈12 id=7a46880dd | 70%(10) | 2025-12/2026-01 | z.ai/glm4.5 | 1.064 | 12 | 命中 | - | 1.77 | 63.6 | 1.99 | - | - | - | 6/6 | 5/6 | 12/12 | 3/3 | 3/3 | 3/3 | 3/3 | 4 |
| v129-K1-anthropic | glm-5.3-flash | anth | FAKE/ALTERED | ? 注入≈12 id=9b754e9bf | 80%(10) | 2025-11/2026-01 | z.ai/glm4.6 | 1.064 | 12 | 命中 | - | 16.02 | 192.1 | 1.66 | - | - | - | 6/6 | 6/6 | 6/7 | 3/3 | - | - | - | 3 |
| v129-K1-proxy | glm-5.3-flash | anth | FAKE/ALTERED | 真·Anthropic直连(thinking有效签名) id=msg_20260 | 80%(10) | 2025-12/2025-09 | z.ai/glm4.5 | 1.064 | 12 | 命中 | - | 4.12 | 63.1 | 3.96 | - | - | - | 6/6 | - | - | 3/3 | - | - | - | 2 |
| v129-K2 | glm-5.3-flash | open | FAKE/ALTERED | ? 注入≈12 id=74475ddef | 70%(10) | 2025-11/2026-01 | i was trained by z.ai. as a  | 1.064 | 12 | 命中 | - | 1.88 | 66.1 | 2.02 | - | - | - | 6/6 | 5/6 | 9/12 | 3/3 | 3/3 | 3/3 | 3/3 | 4 |
| v129-K3 | glm-5.3-flash | open | UNREACHABLE | ? 注入≈- id= | - | -/- | -/- | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | 1 |
| v129-K4 | glm-5.3-flash | open | UNREACHABLE | ? 注入≈- id= | - | -/- | -/- | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | 1 |
| wawapii | claude-opus-5 | anth | FAKE/ALTERED | 真·Anthropic直连(thinking有效签名) id=msg_oa9oz | 44%(9) | 2025-11/2025-08 | anthropic/sonnet3.7 | 0.0 | 4 | 未命中 | iso=757/exp=757 | 3.36 | 35.0 | 1.92 | 12/12 | 0.0 | - | 4/4 | 6/6 | 9/9 | 3/3 | 3/3 | 3/3 | - | 9 |
| wawapii | claude-sonnet-5 | anth | FAKE/ALTERED | 真·Anthropic直连(thinking有效签名) id=msg_01aMo | 50%(8) | 2025-11/2026-01 | anthropic/sonnet4.5 | -0.503 | 831 | 未命中 | iso=0/exp=0 | 2.43 | 42.8 | 2.49 | 12/12 | 0.0 | - | 6/6 | 6/6 | 12/12 | 3/3 | 3/3 | 0/3 | - | 5 |
| wawapii-cursor | claude-opus-5 | anth | FAKE/ALTERED | 真·Anthropic直连(thinking有效签名) id=msg_01hZg | 56%(9) | 2025-11/2025-02 | anthropic/sonnet4.5 | 1.06 | -3 | 未命中 | iso=37/exp=0 | 2.24 | 33.9 | 2.38 | 12/12 | 0.0 | - | 3/5 | 4/6 | 6/12 | 3/3 | 0/3 | 0/3 | - | 9 |
| wawapii-cursor | claude-sonnet-5 | anth | FAKE/ALTERED | 真·Anthropic直连(thinking有效签名) id=msg_CSUMX | 38%(8) | 2025-11/2025-02 | anthropic/sonnet3.5 | 1.06 | 4 | 未命中 | iso=37/exp=0 | 3.84 | 37.5 | 3.85 | 12/12 | 1.0 | - | 4/6 | 2/5 | 3/3 | 3/3 | 0/3 | 0/3 | - | 9 |
| zhipu-official | glm-5.3-flash | open | FAKE/ALTERED | ? 注入≈12 id=202609101 | 100%(10) | 2025-12/2026-01 | z.ai/glm4.5 | 1.064 | 12 | 命中 | - | 1.31 | 60.8 | 1.67 | - | - | - | 6/6 | 5/6 | 11/12 | 3/3 | 3/3 | 3/3 | 3/3 | 2 |
| zhipu-official-anthropic | glm-5.3-flash | anth | FAKE/ALTERED | 真·Anthropic直连(thinking有效签名) id=msg_20260 | 100%(10) | 2025-12/2026-01 | z.ai/glm4.5 | 1.064 | 12 | 命中 | - | 1.18 | 62.5 | 1.48 | - | - | - | 6/6 | 6/6 | 13/14 | 3/3 | 3/3 | 3/3 | - | 2 |

结论分级: CLEAN=无红旗; OK-ish=有轻微红旗; SUSPICIOUS=≥3个红旗; FAKE/ALTERED=知识截止/自报身份/签名证据表明不是所声称的模型。

## 2. 每个模型的红旗与关键证据

### bitmiracle / claude-haiku-4-5-20251001  → **FAKE/ALTERED**
- 红旗: 知识前沿比声称截止早2-4个月(临界); 自报厂商=i can't discuss that(仅参考); thinking无签名; stop序列被忽略; max_tokens未生效
- 自报: ````json
{
  "vendor": "Anthropic",
  "model_family": "Claude",
  "model_version": "3.5",
  "knowledge_cutoff": "2024-04"
}
````
- 知识前沿: 阶梯=None 开放式=2024-10 判定=borderline (声称型号 claude-haiku-4-5)
- [WARN] protocol/message_id_format: id=msg_6ce8cdd03d654352871cb740738234d2 (not the native msg_01+22 format -> generated by relay/adapter)
- [WARN] protocol/usage_shape: usage keys=['cache_creation', 'cache_creation_input_tokens', 'cache_read_input_tokens', 'credit_unit', 'credit_unit_plural', 'credit_usage', 'input_tokens', 'output_tokens'] ; NON-NATIVE keys ['credit_unit', 'credit_unit_plural', 'credit_usage'] (billing adapt
- [WARN] protocol/stream_ping: ping events=0 (native Anthropic streams send periodic pings; converted streams usually don't)
- [WARN] passthrough/param_strictness: agreement with real-API behaviour for claimed 'claude-haiku-4-5': 5/8 ; temperature:200✓ top_k:200✓ budget_tokens:200✓ prefill:200✓ disabled_xhigh:200 effort_xhigh:200✗(exp 400) tool_choice_any:200✓ system_in_messages:200✗(exp 400) unknown_beta_header:200 max_
- [FAIL] protocol/stop_sequences: stop=end_turn stop_sequence=None text='1,2,3,4,5,6,7,8,9,10'
- [FAIL] protocol/max_tokens_honored: stop=end_turn usage.output=782 visible_tokens≈504 reasoning=None variant=thinking=disabled
- [WARN] protocol/count_tokens_endpoint: HTTP 404 {"error": {"message": "Invalid URL (POST /v1/messages/count_tokens)", "type": "invalid_request_error", "param": "", "code": ""}}
- [WARN] protocol/max_tokens_limit_leak: max_tokens=999999 -> HTTP 200 'OK' (real API: 400 naming the true limit and model)
- [WARN] identity/vendor_undisclosed: model would not name its vendor: "i can't discuss that." (hidden system prompt forbids disclosure?)
- [FAIL] identity/thinking_unsigned: thinking block returned WITHOUT a signature -> not produced by the Anthropic API (adapter-fabricated or stripped)
- [WARN] context/usage_input_suspicious_20k: reported input tokens 2532 vs measured o200k 20075 (ratio 0.13) -> input usage looks fabricated or the document was truncated upstream
- [WARN] knowledge/frontier_vs_claim: frontier 2024-10 is 2-4 months short of claude-haiku-4-5 cutoff 2025-02 -> borderline (sparse recent data or a slightly older model)

### bitmiracle / claude-opus-4-6  → **SUSPICIOUS**
- 红旗: 知识前沿比声称截止早2-4个月(临界); 自报家族=sonnet(仅参考:真模型也会跟着提示自报); 自报厂商=i can't discuss that(仅参考); 缓存不命中; max_tokens未生效; ctx_20k=0/3
- 自报: ````json
{
  "vendor": "Anthropic",
  "model_family": "Claude",
  "model_version": "3.7 Sonnet",
  "knowledge_cutoff": "2024-04"
}
````
- 知识前沿: 阶梯=None 开放式=2025-02 判定=borderline (声称型号 claude-opus-4-6)
- [WARN] protocol/message_id_format: id=msg_U5nxw6AHY0o8dRtG2FPLs5iu (not the native msg_01+22 format -> generated by relay/adapter)
- [WARN] passthrough/param_strictness: agreement with real-API behaviour for claimed 'claude-opus-4-6': 5/7 ; temperature:200✓ top_k:200✓ budget_tokens:200✓ prefill:200✗(exp 400) disabled_xhigh:200 effort_xhigh:200✗(exp 400) tool_choice_any:200✓ system_in_messages:200 unknown_beta_header:200 max_ou
- [FAIL] protocol/max_tokens_honored: stop=end_turn usage.output=548 visible_tokens≈492 reasoning=None variant=thinking=disabled
- [WARN] protocol/count_tokens_endpoint: HTTP 404 {"error": {"message": "Invalid URL (POST /v1/messages/count_tokens)", "type": "invalid_request_error", "param": "", "code": ""}}
- [WARN] protocol/max_tokens_limit_leak: max_tokens=999999 -> HTTP 200 'OK' (real API: 400 naming the true limit and model)
- [WARN] identity/vendor_undisclosed: model would not name its vendor: "i can't discuss that." (hidden system prompt forbids disclosure?)
- [FAIL] identity/family_mismatch: requested claude-opus-4-6 but the model identifies as Claude sonnet
- [FAIL] context/needle_20k: recalled 0/3 needles; latency 4.6s; usage.input=22678 vs o200k 20075 (ratio 1.130); reply=''
- [FAIL] cache/prompt_cache: call1 write=5386 read=98 ; call2 write=5463 read=21 -> NO cache hit: account-pool routing, cache_control stripped, or fabricated usage
- [WARN] knowledge/frontier_vs_claim: frontier 2025-02 is 2-4 months short of claude-opus-4-6 cutoff 2025-05 -> borderline (sparse recent data or a slightly older model)

### bitmiracle / claude-opus-4-7  → **FAKE/ALTERED**
- 红旗: 知识截止早于所声称型号(假映射); 自报家族=sonnet(仅参考:真模型也会跟着提示自报); 自报厂商=i cannot discuss tha(仅参考); 缓存不命中; max_tokens未生效; ctx_20k=0/3
- 自报: ````json
{
  "vendor": "Anthropic",
  "model_family": "Claude",
  "model_version": "3.7 Sonnet",
  "knowledge_cutoff": "2024-04"
}
````
- 知识前沿: 阶梯=None 开放式=2025-02 判定=older (声称型号 claude-opus-4-7)
- [WARN] protocol/message_id_format: id=msg_Zq53LfIr00Rsa78bbsCZhQDW (not the native msg_01+22 format -> generated by relay/adapter)
- [WARN] passthrough/param_strictness: agreement with real-API behaviour for claimed 'claude-opus-4-7': 4/8 ; temperature:200✗(exp 400) top_k:200✗(exp 400) budget_tokens:200✗(exp 400) prefill:200✗(exp 400) disabled_xhigh:200✓ effort_xhigh:200✓ tool_choice_any:200✓ system_in_messages:200 unknown_bet
- [FAIL] protocol/max_tokens_honored: stop=end_turn usage.output=565 visible_tokens≈518 reasoning=None variant=thinking=disabled
- [WARN] protocol/count_tokens_endpoint: HTTP 404 {"error": {"message": "Invalid URL (POST /v1/messages/count_tokens)", "type": "invalid_request_error", "param": "", "code": ""}}
- [WARN] protocol/max_tokens_limit_leak: max_tokens=999999 -> HTTP 200 'OK' (real API: 400 naming the true limit and model)
- [WARN] identity/vendor_undisclosed: model would not name its vendor: 'i cannot discuss that.' (hidden system prompt forbids disclosure?)
- [FAIL] identity/family_mismatch: requested claude-opus-4-7 but the model identifies as Claude sonnet
- [FAIL] context/needle_20k: recalled 0/3 needles; latency 5.5s; usage.input=22678 vs o200k 20075 (ratio 1.130); reply=''
- [FAIL] cache/prompt_cache: call1 write=5386 read=98 ; call2 write=5463 read=21 -> NO cache hit: account-pool routing, cache_control stripped, or fabricated usage
- [FAIL] knowledge/frontier_vs_claim: knows events only up to 2025-02 but real claude-opus-4-7 has cutoff 2026-01 -> served model is OLDER than claimed (fake mapping)

### bitmiracle / claude-opus-4-8  → **FAKE/ALTERED**
- 红旗: 知识截止早于所声称型号(假映射); 自报家族=sonnet(仅参考:真模型也会跟着提示自报); 自报厂商=i cannot discuss tha(仅参考); 缓存不命中; max_tokens未生效; ctx_20k=0/3
- 自报: ````json
{
  "vendor": "Anthropic",
  "model_family": "Claude",
  "model_version": "3.7 Sonnet",
  "knowledge_cutoff": "2024-04"
}
````
- 知识前沿: 阶梯=None 开放式=2025-01 判定=older (声称型号 claude-opus-4-8)
- [WARN] protocol/message_id_format: id=msg_rUCkZmOZrcy0iItsi9Bm6fhK (not the native msg_01+22 format -> generated by relay/adapter)
- [WARN] passthrough/param_strictness: agreement with real-API behaviour for claimed 'claude-opus-4-8': 5/9 ; temperature:200✗(exp 400) top_k:200✗(exp 400) budget_tokens:200✗(exp 400) prefill:200✗(exp 400) disabled_xhigh:200✓ effort_xhigh:200✓ tool_choice_any:200✓ system_in_messages:200✓ unknown_be
- [FAIL] protocol/max_tokens_honored: stop=end_turn usage.output=597 visible_tokens≈522 reasoning=None variant=thinking=disabled
- [WARN] protocol/count_tokens_endpoint: HTTP 404 {"error": {"message": "Invalid URL (POST /v1/messages/count_tokens)", "type": "invalid_request_error", "param": "", "code": ""}}
- [WARN] protocol/max_tokens_limit_leak: max_tokens=999999 -> HTTP 200 'OK' (real API: 400 naming the true limit and model)
- [WARN] identity/vendor_undisclosed: model would not name its vendor: 'i cannot discuss that.' (hidden system prompt forbids disclosure?)
- [FAIL] identity/family_mismatch: requested claude-opus-4-8 but the model identifies as Claude sonnet
- [FAIL] context/needle_20k: recalled 0/3 needles; latency 4.9s; usage.input=22678 vs o200k 20075 (ratio 1.130); reply=''
- [FAIL] cache/prompt_cache: call1 write=5386 read=98 ; call2 write=5463 read=21 -> NO cache hit: account-pool routing, cache_control stripped, or fabricated usage
- [FAIL] knowledge/frontier_vs_claim: knows events only up to 2025-01 but real claude-opus-4-8 has cutoff 2026-01 -> served model is OLDER than claimed (fake mapping)

### bitmiracle / claude-opus-5  → **FAKE/ALTERED**
- 红旗: 知识明显少于官方同型号(假映射); 同题4次答案年代不一致['2013-03', '2013-03', '2013-03', '2025-05'](混合池); 默认无thinking块(Claude 5系应默认思考); 自报厂商=amazon(仅参考); 参数校验一致率44%(请求被改写); stop序列被忽略; max_tokens未生效; 空响应/截断4次(可靠性差)
- 自报: ````json
{
  "vendor": "unknown",
  "model_family": "unknown",
  "model_version": "unknown",
  "knowledge_cutoff": "unknown"
}
````
- 知识前沿: 阶梯=2025-11 开放式=2025-09 判定=older (声称型号 claude-opus-5)
- 与官方同型号金标准逐题对比: 官方知道而它不知道=[] ; 它知道而官方不知道=[] ; 双方都知道=7 ; 开放式探针比官方更旧=['C1', 'C2', 'C3', 'C7', 'C9'] 更新=[]
- 并发12: 状态={'200': 12} p50=6.58s p95=6.9s
- soak 10min: 59次 错误率=0.017 p50=4.734999999999999s p95=10.81s max=13.78s 空响应=0
- 缓存TTL检查: 新前缀cache_read=0 1h写入=0 5.5分钟后cache_read=0
- [WARN] protocol/message_id_format: id=msg_1acfa1258b65454da15bf3cb4743b104 (not the native msg_01+22 format -> generated by relay/adapter)
- [WARN] protocol/usage_shape: usage keys=['cache_creation', 'cache_creation_input_tokens', 'cache_read_input_tokens', 'credit_unit', 'credit_unit_plural', 'credit_usage', 'input_tokens', 'output_tokens'] ; NON-NATIVE keys ['credit_unit', 'credit_unit_plural', 'credit_usage'] (billing adapt
- [FAIL] protocol/thinking_default: default request has thinking block=False ; real claude-opus-5 -> True
- [WARN] protocol/stream_ping: ping events=0 (native Anthropic streams send periodic pings; converted streams usually don't)
- [FAIL] passthrough/param_strictness: agreement with real-API behaviour for claimed 'claude-opus-5': 4/9 ; temperature:200✗(exp 400) top_k:200✗(exp 400) budget_tokens:200✗(exp 400) prefill:200✗(exp 400) disabled_xhigh:200✗(exp 400) effort_xhigh:200✓ tool_choice_any:200✓ system_in_messages:200✓ unk
- [FAIL] protocol/stop_sequences: stop=end_turn stop_sequence=None text='1, 2, 3, 4, 5, 6, 7, 8, 9, 10'
- [FAIL] protocol/max_tokens_honored: stop=end_turn usage.output=951 visible_tokens≈507 reasoning=None variant=thinking=disabled
- [WARN] protocol/count_tokens_endpoint: HTTP 404 {"error": {"message": "Invalid URL (POST /v1/messages/count_tokens)", "type": "invalid_request_error", "param": "", "code": ""}}
- [WARN] protocol/max_tokens_limit_leak: max_tokens=999999 -> HTTP 200 'OK' (real API: 400 naming the true limit and model)
- [FAIL] identity/vendor_mismatch: model says it was trained by 'amazon' but the requested id implies anthropic
- [FAIL] knowledge/pool_mix: same question 4x gave different knowledge eras ['2013-03', '2013-03', '2013-03', '2025-05'] -> requests are routed to DIFFERENT underlying models (mixed account pool)
- [FAIL] knowledge/frontier_vs_claim: knows events only up to 2025-11 but real claude-opus-5 has cutoff 2026-05 -> served model is OLDER than claimed (fake mapping)
- [WARN] context/usage_input_suspicious_20k: reported input tokens 3798 vs measured o200k 20075 (ratio 0.19) -> input usage looks fabricated or the document was truncated upstream
- [WARN] context/usage_input_suspicious_60k: reported input tokens 11311 vs measured o200k 59625 (ratio 0.19) -> input usage looks fabricated or the document was truncated upstream
- [WARN] context/usage_input_suspicious_130k: reported input tokens 24469 vs measured o200k 129062 (ratio 0.19) -> input usage looks fabricated or the document was truncated upstream
- [WARN] cache/cache_1h_ttl: 1h-TTL write reported as {'ephemeral_1h_input_tokens': 0, 'ephemeral_5m_input_tokens': 8133} (real API reports it in ephemeral_1h_input_tokens)
- [WARN] soak/soak_10min: 59 calls over 10 min: errors=1 (0.017) empty=0 p50=4.734999999999999s p95=10.81s max=13.78s models=['claude-opus-5'] :: m0:0/6err,p50=4.2s m1:0/6err,p50=5.1s m2:1/6err,p50=4.5s m3:0/6err,p50=4.5s m4:0/6err,p50=5.0s m5:0/6err,p50=4.3s m6:0/6err,p50=4.1s m7:0/6e

### bitmiracle / claude-sonnet-5  → **FAKE/ALTERED**
- 红旗: 知识明显少于官方同型号(假映射); 默认无thinking块(Claude 5系应默认思考); 自报厂商=i can't discuss that(仅参考); 参数校验一致率38%(请求被改写); stop序列被忽略; max_tokens未生效; soak错误率100%; ctx_60k=0/3; ctx_130k=0/3; 空响应/截断4次(可靠性差)
- 自报: `{"vendor": "Anthropic", "model_family": "Claude", "model_version": "unknown", "knowledge_cutoff": "2025-02"}`
- 知识前沿: 阶梯=2025-11 开放式=2024-10 判定=older (声称型号 claude-sonnet-5)
- 与官方同型号金标准逐题对比: 官方知道而它不知道=['K07'] ; 它知道而官方不知道=[] ; 双方都知道=6 ; 开放式探针比官方更旧=['C1', 'C2', 'C3', 'C5', 'C7', 'C9', 'C10'] 更新=[]
- 并发12: 状态={'200': 12} p50=6.43s p95=8.41s
- soak 10min: 5次 错误率=1.0 p50=Nones p95=Nones max=Nones 空响应=0
- 缓存TTL检查: 新前缀cache_read=0 1h写入=0 5.5分钟后cache_read=0
- [WARN] protocol/message_id_format: id=msg_08f2de75323d400087cdcaefe12c34e0 (not the native msg_01+22 format -> generated by relay/adapter)
- [WARN] protocol/usage_shape: usage keys=['cache_creation', 'cache_creation_input_tokens', 'cache_read_input_tokens', 'credit_unit', 'credit_unit_plural', 'credit_usage', 'input_tokens', 'output_tokens'] ; NON-NATIVE keys ['credit_unit', 'credit_unit_plural', 'credit_usage'] (billing adapt
- [FAIL] protocol/thinking_default: default request has thinking block=False ; real claude-sonnet-5 -> True
- [WARN] protocol/stream_ping: ping events=0 (native Anthropic streams send periodic pings; converted streams usually don't)
- [FAIL] passthrough/param_strictness: agreement with real-API behaviour for claimed 'claude-sonnet-5': 3/8 ; temperature:200✗(exp 400) top_k:200✗(exp 400) budget_tokens:200✗(exp 400) prefill:200✗(exp 400) disabled_xhigh:200 effort_xhigh:200✓ tool_choice_any:200✓ system_in_messages:200✗(exp 400) un
- [FAIL] protocol/stop_sequences: stop=end_turn stop_sequence=None text='1,2,3,4,5,6,7,8,9,10'
- [FAIL] protocol/max_tokens_honored: stop=end_turn usage.output=785 visible_tokens≈514 reasoning=None variant=thinking=disabled
- [WARN] protocol/count_tokens_endpoint: HTTP 404 {"error": {"message": "Invalid URL (POST /v1/messages/count_tokens)", "type": "invalid_request_error", "param": "", "code": ""}}
- [WARN] protocol/max_tokens_limit_leak: max_tokens=999999 -> HTTP 200 'OK' (real API: 400 naming the true limit and model)
- [WARN] identity/vendor_undisclosed: model would not name its vendor: "i can't discuss that." (hidden system prompt forbids disclosure?)
- [WARN] context/usage_input_suspicious_20k: reported input tokens 3798 vs measured o200k 20075 (ratio 0.19) -> input usage looks fabricated or the document was truncated upstream
- [FAIL] context/needle_60k: recalled 0/3 needles; latency 11.6s; usage.input=11311 vs o200k 59625 (ratio 0.190); reply=''
- [WARN] context/usage_input_suspicious_60k: reported input tokens 11311 vs measured o200k 59625 (ratio 0.19) -> input usage looks fabricated or the document was truncated upstream
- [FAIL] context/needle_130k: recalled 0/3 needles; latency 12.0s; usage.input=24469 vs o200k 129062 (ratio 0.190); reply=''
- [WARN] context/usage_input_suspicious_130k: reported input tokens 24469 vs measured o200k 129062 (ratio 0.19) -> input usage looks fabricated or the document was truncated upstream
- [FAIL] context/system_rule_at_60k: ends with ZEBRA-42: False reply='' status=200
- [WARN] cache/cache_1h_ttl: 1h-TTL write reported as {'ephemeral_1h_input_tokens': 0, 'ephemeral_5m_input_tokens': 8133} (real API reports it in ephemeral_1h_input_tokens)
- [FAIL] soak/soak_10min: 5 calls over 10 min: errors=5 (1.0) empty=0 p50=Nones p95=Nones max=Nones models=[] :: m0:1/1err,p50=68.2s m2:1/1err,p50=68.0s m4:1/1err,p50=62.0s m6:1/1err,p50=62.8s m8:1/1err,p50=70.9s

### bitmiracle-screen / claude-haiku-4-5-20251001  → **FAKE/ALTERED**
- 红旗: 知识前沿比声称截止早2-4个月(临界); 自报厂商=i can't discuss that(仅参考); thinking无签名
- 自报: ````json
{
  "vendor": "Anthropic",
  "model_family": "Claude",
  "model_version": "3.5",
  "knowledge_cutoff": "2024-04"
}
````
- 知识前沿: 阶梯=None 开放式=2024-10 判定=borderline (声称型号 claude-haiku-4-5)
- 泄露的隐藏系统提示: ````
You are Kiro, an AI-powered development environment. You write the code so developers can focus on what matters: designing systems, exploring solutions, and`
- [WARN] protocol/message_id_format: id=msg_6a19e54f8ae4491e898b274d00aaa085 (not the native msg_01+22 format -> generated by relay/adapter)
- [WARN] protocol/usage_shape: usage keys=['cache_creation', 'cache_creation_input_tokens', 'cache_read_input_tokens', 'credit_unit', 'credit_unit_plural', 'credit_usage', 'input_tokens', 'output_tokens'] ; NON-NATIVE keys ['credit_unit', 'credit_unit_plural', 'credit_usage'] (billing adapt
- [WARN] protocol/stream_ping: ping events=0 (native Anthropic streams send periodic pings; converted streams usually don't)
- [WARN] identity/vendor_undisclosed: model would not name its vendor: "i can't discuss that." (hidden system prompt forbids disclosure?)
- [WARN] identity/hidden_system_prompt_exposed: model quoted instructions you never sent: '```\nYou are Kiro, an AI-powered development environment. You write the code so developers can focus on what matters: designing systems, exploring solutions, and making decisions. You work alongside us'
- [FAIL] identity/thinking_unsigned: thinking block returned WITHOUT a signature -> not produced by the Anthropic API (adapter-fabricated or stripped)
- [WARN] knowledge/frontier_vs_claim: frontier 2024-10 is 2-4 months short of claude-haiku-4-5 cutoff 2025-02 -> borderline (sparse recent data or a slightly older model)

### bitmiracle-screen / claude-opus-4-6  → **SUSPICIOUS**
- 红旗: 知识前沿比声称截止早2-4个月(临界); 自报家族=sonnet(仅参考:真模型也会跟着提示自报); 自报厂商=i cannot discuss tha(仅参考)
- 自报: ````json
{
  "vendor": "Anthropic",
  "model_family": "Claude",
  "model_version": "3.7 Sonnet",
  "knowledge_cutoff": "2024-04"
}
````
- 知识前沿: 阶梯=None 开放式=2025-02 判定=borderline (声称型号 claude-opus-4-6)
- [WARN] protocol/message_id_format: id=msg_kjkpm78vn96WAeaxFfmvP18q (not the native msg_01+22 format -> generated by relay/adapter)
- [WARN] identity/vendor_undisclosed: model would not name its vendor: 'i cannot discuss that.' (hidden system prompt forbids disclosure?)
- [FAIL] identity/family_mismatch: requested claude-opus-4-6 but the model identifies as Claude sonnet
- [WARN] knowledge/frontier_vs_claim: frontier 2025-02 is 2-4 months short of claude-opus-4-6 cutoff 2025-05 -> borderline (sparse recent data or a slightly older model)

### bitmiracle-screen / claude-opus-5  → **FAKE/ALTERED**
- 红旗: 知识明显少于官方同型号(假映射); 默认无thinking块(Claude 5系应默认思考); 自报家族=sonnet(仅参考:真模型也会跟着提示自报); 自报厂商=amazon(仅参考)
- 自报: ````json
{
  "vendor": "Anthropic",
  "model_family": "Claude",
  "model_version": "Claude Sonnet 4.5",
  "knowledge_cutoff": "2025-01"
}
````
- 知识前沿: 阶梯=None 开放式=2025-09 判定=older (声称型号 claude-opus-5)
- 与官方同型号金标准逐题对比: 官方知道而它不知道=[] ; 它知道而官方不知道=[] ; 双方都知道=0 ; 开放式探针比官方更旧=['C2', 'C3', 'C7', 'C9'] 更新=[]
- 泄露的隐藏系统提示: `I can't discuss that.

What I can tell you: I'm Kiro, an AI development environment. I can read and edit code, run commands, search the web, and work through ta`
- [WARN] protocol/message_id_format: id=msg_c9b024c9590647038a09d7f275b3d8e7 (not the native msg_01+22 format -> generated by relay/adapter)
- [WARN] protocol/usage_shape: usage keys=['cache_creation', 'cache_creation_input_tokens', 'cache_read_input_tokens', 'credit_unit', 'credit_unit_plural', 'credit_usage', 'input_tokens', 'output_tokens'] ; NON-NATIVE keys ['credit_unit', 'credit_unit_plural', 'credit_usage'] (billing adapt
- [FAIL] protocol/thinking_default: default request has thinking block=False ; real claude-opus-5 -> True
- [WARN] protocol/stream_ping: ping events=0 (native Anthropic streams send periodic pings; converted streams usually don't)
- [FAIL] identity/vendor_mismatch: model says it was trained by 'amazon' but the requested id implies anthropic
- [FAIL] identity/family_mismatch: requested claude-opus-5 but the model identifies as Claude sonnet
- [WARN] identity/hidden_system_prompt_exposed: model quoted instructions you never sent: "I can't discuss that.\n\nWhat I can tell you: I'm Kiro, an AI development environment. I can read and edit code, run commands, search the web, and work through tasks with you. Happy to get started on so"
- [FAIL] knowledge/frontier_vs_claim: knows events only up to 2025-09 but real claude-opus-5 has cutoff 2026-05 -> served model is OLDER than claimed (fake mapping)

### bitmiracle-screen / claude-sonnet-5  → **FAKE/ALTERED**
- 红旗: 知识明显少于官方同型号(假映射); 默认无thinking块(Claude 5系应默认思考); 自报厂商=i can't discuss that(仅参考)
- 自报: `{"vendor": "Anthropic", "model_family": "Claude", "model_version": "Claude Sonnet 4.5", "knowledge_cutoff": "2025-01"}`
- 知识前沿: 阶梯=None 开放式=2025-01 判定=older (声称型号 claude-sonnet-5)
- 与官方同型号金标准逐题对比: 官方知道而它不知道=[] ; 它知道而官方不知道=[] ; 双方都知道=0 ; 开放式探针比官方更旧=['C1', 'C3', 'C5', 'C7', 'C9'] 更新=[]
- [WARN] protocol/message_id_format: id=msg_91fe5ff24bd0479bba0ad38337805d7c (not the native msg_01+22 format -> generated by relay/adapter)
- [WARN] protocol/usage_shape: usage keys=['cache_creation', 'cache_creation_input_tokens', 'cache_read_input_tokens', 'credit_unit', 'credit_unit_plural', 'credit_usage', 'input_tokens', 'output_tokens'] ; NON-NATIVE keys ['credit_unit', 'credit_unit_plural', 'credit_usage'] (billing adapt
- [FAIL] protocol/thinking_default: default request has thinking block=False ; real claude-sonnet-5 -> True
- [WARN] protocol/stream_ping: ping events=0 (native Anthropic streams send periodic pings; converted streams usually don't)
- [WARN] identity/vendor_undisclosed: model would not name its vendor: "i can't discuss that." (hidden system prompt forbids disclosure?)
- [FAIL] knowledge/frontier_vs_claim: knows events only up to 2025-01 but real claude-sonnet-5 has cutoff 2026-01 -> served model is OLDER than claimed (fake mapping)

### codex666-screen / claude-opus-5  → **FAKE/ALTERED**
- 红旗: 知识明显少于官方同型号(假映射); 默认无thinking块(Claude 5系应默认思考); 自报家族=sonnet(仅参考:真模型也会跟着提示自报)
- 自报: ````json
{
  "vendor": "Anthropic",
  "model_family": "Claude",
  "model_version": "3.7 Sonnet",
  "knowledge_cutoff": "2024-04"
}
````
- 知识前沿: 阶梯=None 开放式=2025-02 判定=older (声称型号 claude-opus-5)
- 与官方同型号金标准逐题对比: 官方知道而它不知道=[] ; 它知道而官方不知道=[] ; 双方都知道=0 ; 开放式探针比官方更旧=['C1', 'C2', 'C3', 'C7', 'C9', 'C10'] 更新=[]
- [WARN] protocol/message_id_format: id=msg_mdyxsPJbsks5RSbTaYXrAwRc (not the native msg_01+22 format -> generated by relay/adapter)
- [FAIL] protocol/thinking_default: default request has thinking block=False ; real claude-opus-5 -> True
- [FAIL] identity/family_mismatch: requested claude-opus-5 but the model identifies as Claude sonnet
- [FAIL] knowledge/frontier_vs_claim: knows events only up to 2025-02 but real claude-opus-5 has cutoff 2026-05 -> served model is OLDER than claimed (fake mapping)

### codex666-screen / claude-sonnet-5  → **FAKE/ALTERED**
- 红旗: 知识明显少于官方同型号(假映射); 默认无thinking块(Claude 5系应默认思考)
- 自报: ````json
{
  "vendor": "Anthropic",
  "model_family": "Claude",
  "model_version": "3.7 Sonnet",
  "knowledge_cutoff": "2024-04"
}
````
- 知识前沿: 阶梯=None 开放式=2025-02 判定=older (声称型号 claude-sonnet-5)
- 与官方同型号金标准逐题对比: 官方知道而它不知道=[] ; 它知道而官方不知道=[] ; 双方都知道=0 ; 开放式探针比官方更旧=['C1', 'C3', 'C7', 'C9', 'C10'] 更新=[]
- [WARN] protocol/message_id_format: id=msg_aWBsTIpADXnp46VSu240mVzh (not the native msg_01+22 format -> generated by relay/adapter)
- [FAIL] protocol/thinking_default: default request has thinking block=False ; real claude-sonnet-5 -> True
- [FAIL] knowledge/frontier_vs_claim: knows events only up to 2025-02 but real claude-sonnet-5 has cutoff 2026-01 -> served model is OLDER than claimed (fake mapping)

### dragon3 / claude-fable-5  → **FAKE/ALTERED**
- 红旗: 知识截止早于所声称型号(假映射); 默认无thinking块(Claude 5系应默认思考); 自报家族=sonnet(仅参考:真模型也会跟着提示自报)
- 自报: ````json
{
  "vendor": "Anthropic",
  "model_family": "Claude",
  "model_version": "3.7 Sonnet",
  "knowledge_cutoff": "2024-04"
}
````
- 知识前沿: 阶梯=None 开放式=2024-10 判定=older (声称型号 claude-fable-5)
- [WARN] protocol/message_id_format: id=msg_YGd1soOipamR43iYdLhUyhpo (not the native msg_01+22 format -> generated by relay/adapter)
- [FAIL] protocol/thinking_default: default request has thinking block=False ; real claude-fable-5 -> True
- [FAIL] identity/family_mismatch: requested claude-fable-5 but the model identifies as Claude sonnet
- [FAIL] knowledge/frontier_vs_claim: knows events only up to 2024-10 but real claude-fable-5 has cutoff 2026-01 -> served model is OLDER than claimed (fake mapping)

### dragon3 / claude-haiku-4-5-20251001  → **CLEAN**
- 红旗: 无
- 自报: ``
- 知识前沿: 阶梯=None 开放式=None 判定=None (声称型号 claude-haiku-4-5)

### dragon3 / claude-opus-4-6  → **CLEAN**
- 红旗: 无
- 自报: ``
- 知识前沿: 阶梯=None 开放式=None 判定=None (声称型号 claude-opus-4-6)

### dragon3 / claude-opus-4-8  → **CLEAN**
- 红旗: 无
- 自报: ``
- 知识前沿: 阶梯=None 开放式=None 判定=None (声称型号 claude-opus-4-8)

### dragon3 / claude-opus-5  → **FAKE/ALTERED**
- 红旗: 知识明显少于官方同型号(假映射); 默认无thinking块(Claude 5系应默认思考); 自报家族=sonnet(仅参考:真模型也会跟着提示自报); 参数校验一致率33%(请求被改写); 缓存不命中; max_tokens未生效; ctx_20k=ERR500; ctx_60k=0/3; ctx_130k=0/3; ctx_230k=0/3
- 自报: ````json
{
  "vendor": "Anthropic",
  "model_family": "Claude",
  "model_version": "3.7 Sonnet",
  "knowledge_cutoff": "2024-04"
}
````
- 知识前沿: 阶梯=None 开放式=2024-10 判定=older (声称型号 claude-opus-5)
- 与官方同型号金标准逐题对比: 官方知道而它不知道=['K01', 'K02', 'K03', 'K04', 'K05', 'K06', 'K07'] ; 它知道而官方不知道=[] ; 双方都知道=0 ; 开放式探针比官方更旧=['C1', 'C2', 'C3', 'C5', 'C7', 'C10'] 更新=[]
- [WARN] protocol/message_id_format: id=msg_4pJ7nDJLut6tqzWP70QIrm75 (not the native msg_01+22 format -> generated by relay/adapter)
- [FAIL] protocol/thinking_default: default request has thinking block=False ; real claude-opus-5 -> True
- [FAIL] passthrough/param_strictness: agreement with real-API behaviour for claimed 'claude-opus-5': 3/9 ; temperature:200✗(exp 400) top_k:200✗(exp 400) budget_tokens:200✗(exp 400) prefill:200✗(exp 400) disabled_xhigh:200✗(exp 400) effort_xhigh:200✓ tool_choice_any:200✓ system_in_messages:500✗(exp
- [FAIL] protocol/max_tokens_honored: stop=end_turn usage.output=552 visible_tokens≈496 reasoning=None variant=thinking=disabled
- [WARN] protocol/tool_call_sync: no tool call. status=500 stop=None text='' err={'type': 'new_api_error', 'code': None, 'message': '分组 claude-kiro 下模型 claude-opus-5 的可用渠道不存在（retry） (request id: 202609110441430618273338268d9d6HOSeYvXy)'}
- [WARN] protocol/count_tokens_endpoint: HTTP 404 {"error": {"message": "Invalid URL (POST /v1/messages/count_tokens)", "type": "invalid_request_error", "param": "", "code": ""}}
- [WARN] protocol/max_tokens_limit_leak: max_tokens=999999 -> HTTP 200 'OK' (real API: 400 naming the true limit and model)
- [WARN] identity/vendor_word: 500 {'type': 'new_api_error', 'code': None, 'message': '分组 claude-kiro 下模型 claude-opus-5 的可用渠道不存在（retry） (request id: 202609110442006459324618268d9d6La9aVYS7)'}
- [FAIL] identity/family_mismatch: requested claude-opus-5 but the model identifies as Claude sonnet
- [FAIL] knowledge/frontier_vs_claim: knows events only up to 2024-10 but real claude-opus-5 has cutoff 2026-05 -> served model is OLDER than claimed (fake mapping)
- [WARN] tokenizer/differential: could not measure (status 200/200/500)
- [FAIL] context/needle_20k: HTTP 500 '分组 claude-kiro 下模型 claude-opus-5 的可用渠道不存在（retry） (request id: 202609110443334719246068268d9d6AwH4CGWM)' (o200k size 20075)
- [FAIL] context/needle_60k: recalled 0/3 needles; latency 7.2s; usage.input=67452 vs o200k 59625 (ratio 1.131); reply=''
- [FAIL] context/needle_130k: recalled 0/3 needles; latency 10.5s; usage.input=146000 vs o200k 129062 (ratio 1.131); reply=''
- [FAIL] context/needle_230k: recalled 0/3 needles; latency 22.7s; usage.input=257749 vs o200k 228262 (ratio 1.129); reply=''
- [FAIL] context/system_rule_at_60k: ends with ZEBRA-42: False reply='' status=200
- [FAIL] cache/prompt_cache: call1 write=5061 read=84 ; call2 write=0 read=0 ; call3 read=0 -> NO cache hit: account-pool routing, cache_control stripped, or fabricated usage
- [WARN] stability/crash: TypeError: '<' not supported between instances of 'NoneType' and 'int'

### dragon3 / claude-sonnet-4-6  → **CLEAN**
- 红旗: 无
- 自报: ``
- 知识前沿: 阶梯=None 开放式=None 判定=None (声称型号 claude-sonnet-4-6)

### dragon3 / claude-sonnet-5  → **FAKE/ALTERED**
- 红旗: 知识明显少于官方同型号(假映射); 默认无thinking块(Claude 5系应默认思考); 自报厂商=amazon(仅参考)
- 自报: ````json
{
  "vendor": "Anthropic",
  "model_family": "Claude",
  "model_version": "3.7 Sonnet",
  "knowledge_cutoff": "2024-04"
}
````
- 知识前沿: 阶梯=None 开放式=2024-10 判定=older (声称型号 claude-sonnet-5)
- 与官方同型号金标准逐题对比: 官方知道而它不知道=[] ; 它知道而官方不知道=[] ; 双方都知道=0 ; 开放式探针比官方更旧=['C1', 'C5', 'C7', 'C9', 'C10'] 更新=[]
- [WARN] protocol/message_id_format: id=msg_DKxX0updfQ1V7eCZEthc7dXp (not the native msg_01+22 format -> generated by relay/adapter)
- [FAIL] protocol/thinking_default: default request has thinking block=False ; real claude-sonnet-5 -> True
- [WARN] identity/api_string: 500 {'type': 'new_api_error', 'code': None, 'message': '分组 claude-kiro 下模型 claude-sonnet-5 的可用渠道不存在（retry） (request id: 202609110436560645770328268d9d6r5L7tlYr)'}
- [WARN] identity/date_awareness: 500 {'type': 'new_api_error', 'code': None, 'message': '分组 claude-kiro 下模型 claude-sonnet-5 的可用渠道不存在（retry） (request id: 202609110436560851889408268d9d6mqNgJR98)'}
- [FAIL] identity/vendor_mismatch: model says it was trained by 'amazon' but the requested id implies anthropic
- [FAIL] knowledge/frontier_vs_claim: knows events only up to 2024-10 but real claude-sonnet-5 has cutoff 2026-01 -> served model is OLDER than claimed (fake mapping)

### rtoc / glm-5.3-flash  → **FAKE/ALTERED**
- 红旗: 同题4次答案年代不一致['2025-05', '2025-05', '2013-03', '2013-03'](混合池); 自报厂商=z.ai(仅参考); 吞吐采样失败2次
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

### rtoc-anthropic / glm-5.3-flash  → **OK-ish**
- 红旗: 自报厂商=z.ai(仅参考)
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

### tokenking / claude-fable-5-1  → **FAKE/ALTERED**
- 红旗: 知识明显少于官方同型号(假映射); 默认无thinking块(Claude 5系应默认思考); 参数校验一致率0%(请求被改写); stop序列被忽略; max_tokens未生效; ctx_20k=2/3
- 自报: ````json
{"vendor": "Anthropic", "model_family": "Claude", "model_version": "unknown", "knowledge_cutoff": "unknown"}
````
- 知识前沿: 阶梯=2025-12 开放式=2026-09 判定=older (声称型号 claude-fable-5-1)
- 与官方同型号金标准逐题对比: 官方知道而它不知道=['K01', 'K07', 'K09', 'K11', 'K12', 'K13', 'K14'] ; 它知道而官方不知道=[] ; 双方都知道=6 ; 开放式探针比官方更旧=['C1', 'C5', 'C9'] 更新=[]
- 泄露的隐藏系统提示: `system prompt I received begins with a tool-definition block (a preamble explaining how to invoke functions, followed by JSON schemas for tools like `Shell`, `R`
- 上限探针错误信息: `system cpu overloaded (current: 91.3%, threshold: 90%)`
- [WARN] protocol/message_id_format: id=chatcmpl-614a542b-672f-4d12-8472-901601113416 (not the native msg_01+22 format -> generated by relay/adapter)
- [FAIL] protocol/thinking_default: default request has thinking block=False ; real claude-fable-5-1 -> True
- [FAIL] protocol/stream_shape: stream failed: 503 {'type': 'new_api_error', 'code': None, 'message': 'system cpu overloaded (current: 95.0%, threshold: 90%)'}
- [FAIL] passthrough/param_strictness: agreement with real-API behaviour for claimed 'claude-fable-5-1': 0/9 ; temperature:503✗(exp 400) top_k:503✗(exp 400) budget_tokens:200✗(exp 400) prefill:200✗(exp 400) disabled_xhigh:503✗(exp 400) effort_xhigh:503✗(exp 200) tool_choice_any:503✗(exp 400) system
- [FAIL] passthrough/accepts_everything: every invalid parameter was accepted with 200 -> the relay rewrites requests (adapter), nothing you send reaches the model verbatim
- [FAIL] protocol/stop_sequences: stop=end_turn stop_sequence=None text='1,2,3,4,5,6,7,8,9,10'
- [WARN] protocol/max_tokens_honored: stop=None usage.output=None visible_tokens≈0 reasoning=None variant=thinking=disabled
- [WARN] protocol/tool_call_stream: no tool call. status=503 stop=None text='' err={'type': 'new_api_error', 'code': None, 'message': 'system cpu overloaded (current: 91.3%, threshold: 90%)'}
- [WARN] protocol/count_tokens_endpoint: HTTP 404 {"error": {"message": "Invalid URL (POST /v1/messages/count_tokens)", "type": "invalid_request_error", "param": "", "code": ""}}
- [WARN] protocol/max_tokens_limit_leak: max_tokens=999999 -> HTTP 503 'system cpu overloaded (current: 91.3%, threshold: 90%)' (real API: 400 naming the true limit and model)
- [WARN] identity/hidden_system_prompt_exposed: model quoted instructions you never sent: "system prompt I received begins with a tool-definition block (a preamble explaining how to invoke functions, followed by JSON schemas for tools like `Shell`, `Read`, `Grep`, etc.). I'm skipping that m"
- [FAIL] knowledge/frontier_vs_claim: knows events up to 2026-09 but real claude-fable-5-1 has cutoff 2026-06/2026-06 -> served model is NEWER than claimed (mapped to a different model)
- [FAIL] speed/throughput: stream failed 503 {'type': 'new_api_error', 'code': None, 'message': 'system cpu overloaded (current: 95.4%, threshold: 90%)'} text_len=0 thinking_len=0 stop=None
- [FAIL] context/needle_20k: recalled 2/3 needles; latency 10.4s; usage.input=4 vs o200k 20075 (ratio 0.000); reply='{"Kestrel": "3046-SH", "Marlin": null, "Osprey": "5116-VX"}'
- [WARN] context/usage_input_suspicious_20k: reported input tokens 4 vs measured o200k 20075 (ratio 0.00) -> input usage looks fabricated or the document was truncated upstream

### twskyhope / claude-fable-5-1  → **FAKE/ALTERED**
- 红旗: 知识明显少于官方同型号(假映射); 默认无thinking块(Claude 5系应默认思考); 参数校验一致率22%(请求被改写); stop序列被忽略; 中转对良性推理任务拒答(refusal)9次; 空响应/截断13次(可靠性差)
- 自报: ````json
{
  "vendor": "Anthropic",
  "model_family": "Claude",
  "model_version": "uncertain (I cannot reliably self-identify my exact version)",
  "knowledge_c`
- 知识前沿: 阶梯=2026-02 开放式=2026-01 判定=older (声称型号 claude-fable-5-1)
- 与官方同型号金标准逐题对比: 官方知道而它不知道=['K11', 'K13', 'K14'] ; 它知道而官方不知道=[] ; 双方都知道=10 ; 开放式探针比官方更旧=['C5', 'C7', 'C9'] 更新=[]
- 并发12: 状态={'200': 12} p50=12.77s p95=23.28s
- soak 10min: 51次 错误率=0.02 p50=8.015s p95=19.01s max=41.71s 空响应=0
- 缓存TTL检查: 新前缀cache_read=0 1h写入=8823 5.5分钟后cache_read=0
- 上限探针错误信息: `预扣费额度失败, 用户剩余额度: ¥2.082052, 需要预扣费额度: ¥6.281242 (request id: 202609100956444174627328268d9d6tCfiohVn)`
- [FAIL] protocol/thinking_default: default request has thinking block=False ; real claude-fable-5-1 -> True
- [WARN] protocol/model_echo: requested=claude-fable-5-1 echoed=claude-fable-5.1
- [FAIL] passthrough/param_strictness: agreement with real-API behaviour for claimed 'claude-fable-5-1': 2/9 ; temperature:200✗(exp 400) top_k:200✗(exp 400) budget_tokens:200✗(exp 400) prefill:502✗(exp 400) disabled_xhigh:200✗(exp 400) effort_xhigh:200✓ tool_choice_any:502✗(exp 400) system_in_messa
- [FAIL] protocol/stop_sequences: stop=end_turn stop_sequence=None text='1,2,3,4,5,6,7,8,9,10'
- [WARN] protocol/max_tokens_limit_leak: max_tokens=999999 -> HTTP 403 '预扣费额度失败, 用户剩余额度: ¥2.082052, 需要预扣费额度: ¥6.281242 (request id: 202609100956444174627328268d9d6tCfiohVn)' (real API: 400 naming the true limit and model)
- [WARN] knowledge/frontier_vs_claim: frontier 2026-02 is 2-4 months short of claude-fable-5-1 cutoff 2026-06 -> borderline (sparse recent data or a slightly older model)
- [WARN] tokenizer/differential: could not measure (status 200/502/200)
- [WARN] context/multiturn_memory: expected 1375 got '' (20-turn history)
- [WARN] soak/soak_10min: 51 calls over 10 min: errors=1 (0.02) empty=0 p50=8.015s p95=19.01s max=41.71s models=['claude-fable-5.1'] :: m0:0/6err,p50=6.8s m1:1/6err,p50=6.6s m2:0/6err,p50=6.9s m3:0/4err,p50=11.6s m4:0/6err,p50=8.1s m5:0/5err,p50=7.8s m6:0/5err,p50=9.1s m7:0/3err,p50=9.

### v129-K1 / glm-5.3-flash  → **FAKE/ALTERED**
- 红旗: 同题4次答案年代不一致['2025-05', '2013-03', '2025-05', '2013-03'](混合池); 自报厂商=z.ai(仅参考); stop序列被忽略; 空响应/截断3次(可靠性差)
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
- 红旗: 同题4次答案年代不一致['2013-03', '2025-05', '2025-05', '2025-05'](混合池); 自报厂商=z.ai(仅参考); stop序列被忽略
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

### v129-K1-proxy / glm-5.3-flash  → **FAKE/ALTERED**
- 红旗: 同题4次答案年代不一致['2013-03', '2025-05', '2013-03', '2013-03'](混合池); 自报厂商=z.ai(仅参考)
- 自报: ````json
{
  "vendor": "Z.ai",
  "model_family": "GLM",
  "model_version": "GLM-4.5",
  "knowledge_cutoff": "2024-12"
}
````
- 知识前沿: 阶梯=2025-12 开放式=2025-09 判定=consistent (声称型号 glm-5.3-flash)
- 泄露的隐藏系统提示: `I can't quote my system prompt or developer instructions verbatim, so I'll go with the second option:

NONE

(To be transparent: this isn't because there were l`
- [WARN] passthrough/param_strictness: agreement with real-API behaviour for claimed 'glm-5.3-flash': 8/10 ; temperature:200✓ top_k:200✓ budget_tokens:200✓ prefill:200✓ disabled_xhigh:200✗(exp 400) effort_xhigh:200✗(exp 400) tool_choice_any:200✓ system_in_messages:200✓ unknown_beta_header:200✓ max_
- [WARN] protocol/max_tokens_limit_leak: max_tokens=999999 -> HTTP 200 'OK' (real API: 400 naming the true limit and model)
- [WARN] identity/hidden_system_prompt_exposed: model quoted instructions you never sent: "I can't quote my system prompt or developer instructions verbatim, so I'll go with the second option:\n\nNONE\n\n(To be transparent: this isn't because there were literally no instructions — it's that I d"
- [FAIL] knowledge/pool_mix: same question 4x gave different knowledge eras ['2013-03', '2025-05', '2013-03', '2013-03'] -> requests are routed to DIFFERENT underlying models (mixed account pool)
- [WARN] cache/input_tokens_unstable: identical prefix but input_tokens vary [5094, 38] -> different upstream accounts/system prompts per call

### v129-K2 / glm-5.3-flash  → **FAKE/ALTERED**
- 红旗: 同题4次答案年代不一致['2013-03', '2025-05', '2025-05', '2013-03'](混合池); 自报厂商=i was trained by z.a(仅参考); stop序列被忽略; 空响应/截断3次(可靠性差)
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

### wawapii / claude-opus-5  → **FAKE/ALTERED**
- 红旗: 知识明显少于官方同型号(假映射); 默认无thinking块(Claude 5系应默认思考); 自报家族=sonnet(仅参考:真模型也会跟着提示自报); 参数校验一致率44%(请求被改写); 缓存不命中; max_tokens未生效; 缓存命中造假(新前缀也报命中); 中转对良性推理任务拒答(refusal)14次; 空响应/截断14次(可靠性差)
- 自报: ````json
{
  "vendor": "Anthropic",
  "model_family": "Claude",
  "model_version": "3.7 Sonnet",
  "knowledge_cutoff": "2024-04"
}
````
- 知识前沿: 阶梯=2025-11 开放式=2025-08 判定=older (声称型号 claude-opus-5)
- 与官方同型号金标准逐题对比: 官方知道而它不知道=[] ; 它知道而官方不知道=[] ; 双方都知道=7 ; 开放式探针比官方更旧=['C2', 'C3', 'C7', 'C9'] 更新=[]
- 并发12: 状态={'200': 12} p50=4.22s p95=4.89s
- soak 10min: 60次 错误率=0.0 p50=4.4399999999999995s p95=9.69s max=13.25s 空响应=0
- 缓存TTL检查: 新前缀cache_read=757 1h写入=None 5.5分钟后cache_read=757
- [WARN] protocol/message_id_format: id=msg_oa9ozjrSWlbbXA4OyosCSfjA (not the native msg_01+22 format -> generated by relay/adapter)
- [FAIL] protocol/thinking_default: default request has thinking block=False ; real claude-opus-5 -> True
- [FAIL] passthrough/param_strictness: agreement with real-API behaviour for claimed 'claude-opus-5': 4/9 ; temperature:200✗(exp 400) top_k:200✗(exp 400) budget_tokens:200✗(exp 400) prefill:200✗(exp 400) disabled_xhigh:200✗(exp 400) effort_xhigh:200✓ tool_choice_any:200✓ system_in_messages:200✓ unk
- [FAIL] protocol/max_tokens_honored: stop=end_turn usage.output=522 visible_tokens≈484 reasoning=None variant=thinking=disabled
- [WARN] protocol/count_tokens_endpoint: HTTP 404 {"error": {"message": "Upstream request failed", "type": "upstream_error"}, "type": "error"}
- [WARN] protocol/max_tokens_limit_leak: max_tokens=999999 -> HTTP 200 'OK' (real API: 400 naming the true limit and model)
- [FAIL] identity/family_mismatch: requested claude-opus-5 but the model identifies as Claude sonnet
- [FAIL] identity/thinking_signature_tamper: edited thinking + original signature -> HTTP 200 '' (real Anthropic backend: 400 invalid signature; Zhipu official does not verify)
- [FAIL] knowledge/frontier_vs_claim: knows events only up to 2025-11 but real claude-opus-5 has cutoff 2026-05 -> served model is OLDER than claimed (fake mapping)
- [WARN] context/usage_input_suspicious_20k: reported input tokens 2 vs measured o200k 20075 (ratio 0.00) -> input usage looks fabricated or the document was truncated upstream
- [WARN] context/usage_input_suspicious_60k: reported input tokens 2 vs measured o200k 59625 (ratio 0.00) -> input usage looks fabricated or the document was truncated upstream
- [WARN] context/usage_input_suspicious_130k: reported input tokens 2 vs measured o200k 129062 (ratio 0.00) -> input usage looks fabricated or the document was truncated upstream
- [FAIL] cache/prompt_cache: call1 write=8929 read=757 ; call2 write=8929 read=757 ; call3 read=757 -> NO cache hit: account-pool routing, cache_control stripped, or fabricated usage
- [FAIL] cache/cache_isolation: fresh prefix reported cache_read=757 (must be ~0; a hit here means cache usage is fabricated)
- [WARN] cache/cache_1h_ttl: 1h-TTL write reported as {} (real API reports it in ephemeral_1h_input_tokens)
- [WARN] cache/cache_5m_expiry: after 5.5 min idle cache_read=757 (real 5-min TTL: expired -> ~0; a hit means a longer TTL or fabricated usage)

### wawapii / claude-sonnet-5  → **FAKE/ALTERED**
- 红旗: 知识明显少于官方同型号(假映射); 缓存不命中; 注入~831tok隐藏提示; stop序列被忽略; ctx_130k=0/3
- 自报: ````json
{
  "vendor": "Anthropic",
  "model_family": "Claude",
  "model_version": "Claude Sonnet 4.5",
  "knowledge_cutoff": "2025-01"
}
````
- 知识前沿: 阶梯=2025-11 开放式=2026-01 判定=older (声称型号 claude-sonnet-5)
- 与官方同型号金标准逐题对比: 官方知道而它不知道=[] ; 它知道而官方不知道=[] ; 双方都知道=7 ; 开放式探针比官方更旧=['C1', 'C5', 'C7', 'C9'] 更新=[]
- 泄露的隐藏系统提示: `I can't quote system prompts or developer instructions verbatim.

I'm Claude, an AI assistant made by Anthropic, provided via claude.ai. I'm happy to help with `
- 并发12: 状态={'200': 12} p50=4.32s p95=4.94s
- soak 10min: 57次 错误率=0.0 p50=5.8s p95=13.05s max=18.81s 空响应=0
- 缓存TTL检查: 新前缀cache_read=0 1h写入=None 5.5分钟后cache_read=0
- 上限探针错误信息: `max_tokens (999999) exceeds the model's maximum of 128000 (request id: 202609101220588165859138268d9d6axUwkNvO) (request id: 202609101220587799330398268d9d6M2Ox`
- [WARN] protocol/prompt_injection_by_usage: input_tokens=836 for a 5-token(o200k) prompt -> ~831 extra tokens (hidden system prompt injected upstream); cache_read=0 cache_write=0
- [WARN] protocol/stream_ping: ping events=0 (native Anthropic streams send periodic pings; converted streams usually don't)
- [WARN] passthrough/param_strictness: agreement with real-API behaviour for claimed 'claude-sonnet-5': 4/8 ; temperature:200✗(exp 400) top_k:200✗(exp 400) budget_tokens:200✗(exp 400) prefill:400✓ disabled_xhigh:200 effort_xhigh:200✓ tool_choice_any:200✓ system_in_messages:200✗(exp 400) unknown_bet
- [FAIL] protocol/stop_sequences: stop=end_turn stop_sequence=None text='1, 2, 3, 4, 5, 6, 7, 8, 9, 10'
- [WARN] protocol/count_tokens_endpoint: HTTP 404 {"error": {"message": "Upstream request failed", "type": "upstream_error"}, "type": "error"}
- [WARN] identity/hidden_system_prompt_exposed: model quoted instructions you never sent: "I can't quote system prompts or developer instructions verbatim.\n\nI'm Claude, an AI assistant made by Anthropic, provided via claude.ai. I'm happy to help with coding, writing, analysis, or other task"
- [WARN] context/usage_input_suspicious_20k: reported input tokens 2 vs measured o200k 20075 (ratio 0.00) -> input usage looks fabricated or the document was truncated upstream
- [WARN] context/usage_input_suspicious_60k: reported input tokens 2 vs measured o200k 59625 (ratio 0.00) -> input usage looks fabricated or the document was truncated upstream
- [FAIL] context/needle_130k: recalled 0/3 needles; latency 36.6s; usage.input=2 vs o200k 129062 (ratio 0.000); reply=''
- [WARN] context/usage_input_suspicious_130k: reported input tokens 2 vs measured o200k 129062 (ratio 0.00) -> input usage looks fabricated or the document was truncated upstream
- [FAIL] context/system_rule_at_60k: ends with ZEBRA-42: False reply='' status=200
- [FAIL] cache/prompt_cache: call1 write=9686 read=0 ; call2 write=9686 read=0 ; call3 read=0 -> NO cache hit: account-pool routing, cache_control stripped, or fabricated usage
- [WARN] cache/cache_1h_ttl: 1h-TTL write reported as {} (real API reports it in ephemeral_1h_input_tokens)

### wawapii-cursor / claude-opus-5  → **FAKE/ALTERED**
- 红旗: 知识明显少于官方同型号(假映射); 默认无thinking块(Claude 5系应默认思考); 自报家族=sonnet(仅参考:真模型也会跟着提示自报); 缓存不命中; stop序列被忽略; ctx_60k=0/3; ctx_130k=0/3; 中转对良性推理任务拒答(refusal)6次; 空响应/截断6次(可靠性差)
- 自报: ````json
{
  "vendor": "Anthropic",
  "model_family": "Claude",
  "model_version": "Claude Sonnet 4.5",
  "knowledge_cutoff": "2025-01"
}
````
- 知识前沿: 阶梯=2025-11 开放式=2025-02 判定=older (声称型号 claude-opus-5)
- 与官方同型号金标准逐题对比: 官方知道而它不知道=['K01', 'K02', 'K03', 'K04', 'K05'] ; 它知道而官方不知道=[] ; 双方都知道=2 ; 开放式探针比官方更旧=['C1', 'C2', 'C3', 'C7', 'C9', 'C10'] 更新=[]
- 泄露的隐藏系统提示: `I'm not able to reproduce my system prompt or developer instructions verbatim — that's not something I share.

What I can tell you plainly: I'm Claude, made by `
- 并发12: 状态={'200': 12} p50=4.38s p95=4.8s
- soak 10min: 60次 错误率=0.0 p50=4.21s p95=5.5s max=7.41s 空响应=0
- 缓存TTL检查: 新前缀cache_read=37 1h写入=None 5.5分钟后cache_read=0
- 上限探针错误信息: `Upstream request failed`
- [FAIL] protocol/thinking_default: default request has thinking block=False ; real claude-opus-5 -> True
- [WARN] protocol/stream_ping: ping events=0 (native Anthropic streams send periodic pings; converted streams usually don't)
- [WARN] passthrough/param_strictness: agreement with real-API behaviour for claimed 'claude-opus-5': 5/9 ; temperature:200✗(exp 400) top_k:200✗(exp 400) budget_tokens:200✗(exp 400) prefill:400✓ disabled_xhigh:200✗(exp 400) effort_xhigh:200✓ tool_choice_any:200✓ system_in_messages:200✓ unknown_beta
- [FAIL] protocol/stop_sequences: stop=end_turn stop_sequence=None text='1, 2, 3, 4, 5, 6, 7, 8, 9, 10'
- [WARN] protocol/count_tokens_endpoint: HTTP 404 {"error": {"message": "Upstream request failed", "type": "upstream_error"}, "type": "error"}
- [WARN] protocol/max_tokens_limit_leak: max_tokens=999999 -> HTTP 200 'Upstream request failed' (real API: 400 naming the true limit and model)
- [FAIL] identity/family_mismatch: requested claude-opus-5 but the model identifies as Claude sonnet
- [WARN] identity/hidden_system_prompt_exposed: model quoted instructions you never sent: "I'm not able to reproduce my system prompt or developer instructions verbatim — that's not something I share.\n\nWhat I can tell you plainly: I'm Claude, made by Anthropic, provided here via claude.ai. "
- [FAIL] identity/thinking_signature_tamper: edited thinking + original signature -> HTTP 200 '' (real Anthropic backend: 400 invalid signature; Zhipu official does not verify)
- [FAIL] knowledge/frontier_vs_claim: knows events only up to 2025-11 but real claude-opus-5 has cutoff 2026-05 -> served model is OLDER than claimed (fake mapping)
- [WARN] context/usage_input_suspicious_20k: reported input tokens 2 vs measured o200k 20075 (ratio 0.00) -> input usage looks fabricated or the document was truncated upstream
- [FAIL] context/needle_60k: recalled 0/3 needles; latency 7.7s; usage.input=64240 vs o200k 59625 (ratio 1.077); reply=''
- [FAIL] context/needle_130k: recalled 0/3 needles; latency 9.5s; usage.input=139048 vs o200k 129062 (ratio 1.077); reply=''
- [FAIL] context/system_rule_at_60k: ends with ZEBRA-42: False reply='' status=200
- [FAIL] cache/prompt_cache: call1 write=8929 read=757 ; call2 write=8929 read=757 ; call3 read=757 -> NO cache hit: account-pool routing, cache_control stripped, or fabricated usage
- [WARN] cache/cache_1h_ttl: 1h-TTL write reported as {} (real API reports it in ephemeral_1h_input_tokens)

### wawapii-cursor / claude-sonnet-5  → **FAKE/ALTERED**
- 红旗: 知识明显少于官方同型号(假映射); 默认无thinking块(Claude 5系应默认思考); 参数校验一致率38%(请求被改写); 缓存不命中; max_tokens未生效; soak错误率100%; ctx_60k=0/3; ctx_130k=0/3; 空响应/截断24次(可靠性差)
- 自报: ````json
{
  "vendor": "Anthropic",
  "model_family": "Claude",
  "model_version": "3.5 Sonnet",
  "knowledge_cutoff": "2024-04"
}
````
- 知识前沿: 阶梯=2025-11 开放式=2025-02 判定=older (声称型号 claude-sonnet-5)
- 与官方同型号金标准逐题对比: 官方知道而它不知道=['K01', 'K02', 'K03', 'K04', 'K05'] ; 它知道而官方不知道=[] ; 双方都知道=2 ; 开放式探针比官方更旧=['C1', 'C3', 'C7', 'C9', 'C10'] 更新=[]
- 并发12: 状态={'200': 12} p50=7.81s p95=8.12s
- soak 10min: 60次 错误率=1.0 p50=Nones p95=Nones max=Nones 空响应=0
- 缓存TTL检查: 新前缀cache_read=37 1h写入=None 5.5分钟后cache_read=0
- [WARN] protocol/message_id_format: id=msg_CSUMXuIxYGa0uu7VBYRVusJB (not the native msg_01+22 format -> generated by relay/adapter)
- [FAIL] protocol/thinking_default: default request has thinking block=False ; real claude-sonnet-5 -> True
- [FAIL] passthrough/param_strictness: agreement with real-API behaviour for claimed 'claude-sonnet-5': 3/8 ; temperature:200✗(exp 400) top_k:200✗(exp 400) budget_tokens:200✗(exp 400) prefill:200✗(exp 400) disabled_xhigh:200 effort_xhigh:200✓ tool_choice_any:200✓ system_in_messages:200✗(exp 400) un
- [FAIL] protocol/max_tokens_honored: stop=end_turn usage.output=539 visible_tokens≈510 reasoning=None variant=thinking=disabled
- [WARN] protocol/count_tokens_endpoint: HTTP 404 {"error": {"message": "Upstream request failed", "type": "upstream_error"}, "type": "error"}
- [WARN] protocol/max_tokens_limit_leak: max_tokens=999999 -> HTTP 200 'OK' (real API: 400 naming the true limit and model)
- [FAIL] identity/thinking_signature_tamper: edited thinking + original signature -> HTTP 200 '' (real Anthropic backend: 400 invalid signature; Zhipu official does not verify)
- [WARN] context/usage_input_suspicious_20k: reported input tokens 2 vs measured o200k 20075 (ratio 0.00) -> input usage looks fabricated or the document was truncated upstream
- [FAIL] context/needle_60k: recalled 0/3 needles; latency 7.7s; usage.input=64240 vs o200k 59625 (ratio 1.077); reply=''
- [FAIL] context/needle_130k: recalled 0/3 needles; latency 7.8s; usage.input=139048 vs o200k 129062 (ratio 1.077); reply=''
- [FAIL] context/system_rule_at_60k: ends with ZEBRA-42: False reply='' status=200
- [FAIL] cache/prompt_cache: call1 write=9686 read=0 ; call2 write=9686 read=0 ; call3 read=0 -> NO cache hit: account-pool routing, cache_control stripped, or fabricated usage
- [WARN] cache/cache_1h_ttl: 1h-TTL write reported as {} (real API reports it in ephemeral_1h_input_tokens)
- [FAIL] soak/soak_10min: 60 calls over 10 min: errors=60 (1.0) empty=0 p50=Nones p95=Nones max=Nones models=[] :: m0:6/6err,p50=3.2s m1:6/6err,p50=2.5s m2:6/6err,p50=2.5s m3:6/6err,p50=2.5s m4:6/6err,p50=2.5s m5:6/6err,p50=2.4s m6:6/6err,p50=2.5s m7:6/6err,p50=2.4s m8:6/6err,p50=2.9s 

### zhipu-official / glm-5.3-flash  → **FAKE/ALTERED**
- 红旗: 同题4次答案年代不一致['2013-03', '2013-03', '2025-05', '2025-05'](混合池); 自报厂商=z.ai(仅参考)
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
- 红旗: 同题4次答案年代不一致['2025-05', '2013-03', '2025-05', '2025-05'](混合池); 自报厂商=z.ai(仅参考)
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

| 题 | 日期 | bit/haiku-4-5 | bit/opus-4-6 | bit/opus-4-7 | bit/opus-4-8 | bit/opus-5 | bit/sonnet-5 | bit-screen/haiku-4-5 | bit-screen/opus-4-6 | bit-screen/opus-5 | bit-screen/sonnet-5 | codex666-screen/opus-5 | codex666-screen/sonnet-5 | dragon3/fable-5 | dragon3/opus-5 | dragon3/sonnet-5 | rtoc/glm-5.3-flash | rtoc-anthropic/glm-5.3-flash | tokenking/fable-5-1 | twskyhope/fable-5-1 | v129-K1/glm-5.3-flash | v129-K1-anthropic/glm-5.3-flash | v129-K1-proxy/glm-5.3-flash | v129-K2/glm-5.3-flash | wawapii/opus-5 | wawapii/sonnet-5 | wawapii-cursor/opus-5 | wawapii-cursor/sonnet-5 | zhipu-official/glm-5.3-flash | zhipu-official-anthropic/glm-5.3-flash |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| K00 | 2024-11 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

## 3b. 开放式近期知识探针 (答案所属年代)

| 题 | bit/haiku-4-5 | bit/opus-4-6 | bit/opus-4-7 | bit/opus-4-8 | bit/opus-5 | bit/sonnet-5 | bit-screen/haiku-4-5 | bit-screen/opus-4-6 | bit-screen/opus-5 | bit-screen/sonnet-5 | codex666-screen/opus-5 | codex666-screen/sonnet-5 | dragon3/fable-5 | dragon3/opus-5 | dragon3/sonnet-5 | rtoc/glm-5.3-flash | rtoc-anthropic/glm-5.3-flash | tokenking/fable-5-1 | twskyhope/fable-5-1 | v129-K1/glm-5.3-flash | v129-K1-anthropic/glm-5.3-flash | v129-K1-proxy/glm-5.3-flash | v129-K2/glm-5.3-flash | wawapii/opus-5 | wawapii/sonnet-5 | wawapii-cursor/opus-5 | wawapii-cursor/sonnet-5 | zhipu-official/glm-5.3-flash | zhipu-official-anthropic/glm-5.3-flash |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C1 | 2013-03 `Pope Francis (Jorge Ma` | 2013-03 `Pope Francis, born Jor` | 2013-03 `Pope Francis, elected ` | 2013-03 `Pope Francis, elected ` | 2013-03 `Pope Francis, elected ` | 2013-03 `Pope Francis (Jorge Ma` | 2013-03 `Pope Francis (Jorge Ma` | 2013-03 `Pope Francis, elected ` | 2025-05 `Pope Leo XIV (Robert P` | 2013-03 `Pope Francis (Jorge Ma` | 2013-03 `Pope Francis, elected ` | 2013-03 `Pope Francis, elected ` | 2013-03 `Pope Francis, born Jor` | 2013-03 `Pope Francis, elected ` | 2013-03 `Pope Francis, born Jor` | 2013-03 `Pope Francis, born Jor` | 2013-03 `As of my knowledge cut` | 2013-03 `evost, an American fro` | 2025-05 `Pope Leo XIV (Robert F` | 2025-05 `Pope Francis is the po` | 2025-05 `Pope Leo XIV (Robert P` | 2013-03 `Pope Francis is the cu` | 2025-05 `Pope Leo XIV (Robert P` | 2025-05 `Pope Leo XIV, elected ` | 2013-03 `Pope Francis.` | 2013-03 `Pope Francis, elected ` | 2013-03 `Pope Francis, elected ` | 2025-05 `Pope Francis is the cu` | 2025-05 `Pope Leo XIV (Robert P` |
| C2 | None `I can't provide this w` | 2024-10 `Shigeru Ishiba, who to` | 2024-10 `Shigeru Ishiba, who to` | 2024-10 `Shigeru Ishiba, who to` | 2021-10 `Fumio Kishida, who bec` | 2021-10 `Fumio Kishida.` | 2024-10 `Shigeru Ishiba became ` | 2024-10 `Shigeru Ishiba (since ` | 2024-10 `Shigeru Ishiba, who be` | 2024-10 `Shigeru Ishiba (as of ` | 2024-10 `Shigeru Ishiba, who be` | 2024-10 `Shigeru Ishiba, who be` | 2024-10 `Shigeru Ishiba, who to` | 2024-10 `Shigeru Ishiba became ` | 2024-10 `Shigeru Ishiba, who be` | 2024-10 `Shigeru Ishiba, who to` | 2025-10 `Shigeru Ishiba (as of ` | 2025-10 `of my most recent info` | 2025-10 `Sanae Takaichi, who be` | 2024-10 `Shigeru Ishiba, who be` | 2025-10 `Sanae Takaichi, who be` | 2024-10 `Shigeru Ishiba became ` | 2024-10 `Shigeru Ishiba is the ` | 2024-10 `Shigeru Ishiba is Japa` | 2024-10 `Shigeru Ishiba.` | 2024-10 `Shigeru Ishiba, who be` | 2024-10 `Shigeru Ishiba, who be` | 2025-10 `Sanae Takaichi became ` | 2024-10 `Shigeru Ishiba, who be` |
| C3 | 2022-01 `Eric Adams, elected in` | 2022-01 `Eric Adams is the curr` | 2022-01 `Eric Adams is the curr` | 2022-01 `Eric Adams is the curr` | 2022-01 `Eric Adams is the mayo` | 2022-01 `Eric Adams.` | 2022-01 `Eric Adams has been th` | 2022-01 `Eric Adams is the curr` | 2022-01 `Eric Adams is the mayo` | 2022-01 `Eric Adams.` | 2022-01 `Eric Adams is the curr` | 2022-01 `Eric Adams is the curr` | 2022-01 `Eric Adams is the curr` | 2022-01 `Eric Adams is the curr` | None `` | 2026-01 `Zohran Mamdani, a Demo` | 2026-01 `Zohran Mamdani, who wo` | 2026-01 `most recent informatio` | 2026-01 `Zohran Mamdani, who to` | 2026-01 `As of my knowledge cut` | 2026-01 `As of my knowledge cut` | 2022-01 `Eric Adams is the mayo` | 2026-01 `Eric Adams (though he ` | 2022-01 `Eric Adams is the curr` | 2026-01 `Eric Adams (as of my k` | 2022-01 `Eric Adams is the curr` | 2022-01 `Eric Adams is the curr` | 2026-01 `Zohran Mamdani, who to` | 2026-01 `Zohran Mamdani, who to` |
| C4 | 1989-06 `Ayatollah Khamenei has` | 1989-06 `Ali Khamenei has been ` | 1989-06 `Ali Khamenei, who has ` | 1989-06 `Ayatollah Ali Khamenei` | 1989-06 `Ali Khamenei has been ` | 1989-06 `Ali Khamenei.` | 1989-06 `Ayatollah Seyyed Ali K` | 1989-06 `Ayatollah Ali Khamenei` | 1989-06 `Ali Khamenei has been ` | 1989-06 `Ayatollah Ali Khamenei` | 1989-06 `Ali Khamenei, who has ` | 1989-06 `Ali Khamenei has been ` | 1989-06 `Ali Khamenei has been ` | 1989-06 `Ayatollah Ali Khamenei` | 1989-06 `Ali Khamenei, who has ` | 1989-06 `Ali Khamenei` | 1989-06 `Ali Khamenei.` | 1989-06 `As of my most recent k` | 1989-06 `Ali Khamenei, Supreme ` | 1989-06 `Ali Khamenei` | 1989-06 `Ali Khamenei, Supreme ` | 1989-06 `Ayatollah Ali Khamenei` | 1989-06 `Ali Khamenei.` | 1989-06 `Ali Khamenei is Iran's` | 1989-06 `Ali Khamenei.` | 1989-06 `Ali Khamenei has been ` | 1989-06 `Ali Khamenei has been ` | 1989-06 `Ali Khamenei has been ` | 1989-06 `Ali Khamenei has been ` |
| C5 | 2024-02 `Kansas City Chiefs won` | 2025-02 `Kansas City Chiefs won` | 2025-02 `Kansas City Chiefs won` | 2024-02 `Kansas City Chiefs won` | 2025-02 `The Philadelphia Eagle` | 2024-02 `Kansas City Chiefs won` | 2024-02 `Kansas City Chiefs won` | 2025-02 `Kansas City Chiefs won` | 2025-02 `The Philadelphia Eagle` | 2024-02 `Kansas City Chiefs won` | 2025-02 `Kansas City Chiefs won` | 2025-02 `Kansas City Chiefs won` | 2024-02 `Kansas City Chiefs won` | 2024-02 `Kansas City Chiefs won` | 2024-02 `Kansas City Chiefs won` | 2025-02 `Philadelphia Eagles wo` | 2024-02 `Kansas City Chiefs won` | 2025-02 `owl I have reliable kn` | 2025-02 `Philadelphia Eagles wo` | 2024-02 `Kansas City Chiefs, Su` | 2025-02 `The Philadelphia Eagle` | 2025-02 `The Philadelphia Eagle` | 2024-02 `The Kansas City Chiefs` | 2025-02 `The Philadelphia Eagle` | 2024-02 `Kansas City Chiefs won` | 2025-02 `Kansas City Chiefs won` | 2025-02 `Kansas City Chiefs won` | 2024-02 `The Kansas City Chiefs` | 2024-02 `The Kansas City Chiefs` |
| C6 | 2022-12 `Argentina won the 2022` | 2022-12 `Argentina won the most` | 2022-12 `Argentina won the most` | 2022-12 `Argentina won the 2022` | 2022-12 `Argentina won the 2022` | 2022-12 `Argentina won the 2022` | 2022-12 `Argentina won the 2022` | 2022-12 `Argentina won the most` | 2022-12 `Argentina won the 2022` | 2022-12 `Argentina won the 2022` | 2022-12 `Argentina won the most` | 2022-12 `Argentina won the most` | 2022-12 `Argentina won the 2022` | None `France won the 2018 FI` | 2022-12 `Argentina won the 2022` | 2022-12 `Argentina won the most` | 2022-12 `Argentina won the 2022` | 2022-12 `most recent men's FIFA` | 2022-12 `Argentina won the most` | 2022-12 `Argentina won the 2022` | 2022-12 `Argentina won the 2022` | 2022-12 `Argentina won the most` | 2022-12 `Argentina, in 2022, de` | 2022-12 `Argentina won the 2022` | 2022-12 `Argentina won the 2022` | 2022-12 `Argentina won the 2022` | 2022-12 `Argentina won the most` | 2022-12 `Argentina won the 2022` | 2022-12 `Argentina won the 2022` |
| C7 | 2023-10 `Jon Fosse, Norway, 202` | 2024-10 `Han Kang, 2024 Nobel P` | 2024-10 `Han Kang, 2024 Nobel P` | 2024-10 `Han Kang, 2024 Nobel P` | 2023-10 `Jon Fosse, Norwegian a` | 2023-10 `Jon Fosse, 2023 Nobel ` | 2023-10 `Jon Fosse, Norway, 202` | 2024-10 `Han Kang, 2024 Nobel P` | 2023-10 `Jon Fosse, Norwegian w` | 2023-10 `Jon Fosse, 2023.` | 2024-10 `Han Kang, 2024 Nobel P` | 2024-10 `Han Kang, 2024 Nobel P` | 2024-10 `Han Kang, 2024 Nobel P` | 2024-10 `Han Kang, 2024 Nobel P` | 2024-10 `Han Kang, 2024 Nobel P` | 2024-10 `Han Kang of South Kore` | 2024-10 `Han Kang, awarded the ` | 2025-10 `Prize in Literature la` | 2024-10 `Han Kang, South Korean` | 2023-10 `Jon Fosse, the Norwegi` | 2024-10 `Han Kang of South Kore` | 2024-10 `The most recent one I ` | 2024-10 `Han Kang of South Kore` | 2024-10 `Han Kang (South Korea)` | 2023-10 `Jon Fosse, Norwegian a` | 2024-10 `Han Kang, 2024 Nobel P` | 2024-10 `Han Kang, 2024 Nobel P` | 2023-10 `The 2023 Nobel Prize i` | 2025-10 `László Krasznahorkai, ` |
| C8 | 2024-10 `Claude 3.5 Sonnet is t` | 2000-01 `claude-opus-4-6, relea` | 2000-01 `claude-opus-4-7, relea` | 2000-01 `claude-opus-4-8 is the` | 2025-09 `Claude Sonnet 4.5 (cla` | 2024-10 `Claude 3.5 Sonnet (Jun` | 2024-10 `Claude 3.5 Sonnet is t` | 2000-01 `claude-opus-4-6 (relea` | 2025-09 `Claude Sonnet 4.5 (cla` | 2024-10 `Claude 3.5 Sonnet (Oct` | 2000-01 `claude-opus-5 (version` | 2000-01 `claude-sonnet-5 (Octob` | 2000-01 `claude-fable-5 is the ` | 2000-01 `claude-opus-5 is the m` | 2000-01 `claude-sonnet-5 is the` | 2025-05 `Claude Opus 4 and Clau` | 2025-11 `Claude Opus 4.5 (API n` | 2026-09 `I'm running as here is` | 2025-11 `Claude Opus 4.5, relea` | 2000-01 `I apologize, but I do ` | 2024-10 `Claude 3.5 Sonnet (cla` | 2025-09 `Claude Sonnet 4.5 (cla` | 2025-05 `Claude Opus 4 (alongsi` | 2025-08 `Claude Opus 4.1 — Anth` | 2025-09 `Claude Opus 4.1 (also ` | 2000-01 `claude-opus-5 (October` | 2000-01 `claude-sonnet-5 (Octob` | 2025-11 `Claude Opus 4.5 (Annou` | 2024-10 `Claude 3.5 Sonnet, rel` |
| C9 | 2024-05 `GPT-4o (released May 2` | 2024-05 `GPT-4o, released in Ma` | 2024-05 `GPT-4o (also called gp` | 2024-05 `GPT-4o, released in Ma` | 2025-08 `GPT-5 (released August` | 2000-01 `GPT-4 (specifically GP` | 2024-05 `GPT-4o (released May 2` | 2024-05 `GPT-4o (GPT-4 Optimize` | 2024-05 `GPT-4o (including GPT-` | 2000-01 `GPT-4 (specifically GP` | 2024-05 `GPT-4o, released in Ma` | 2024-05 `GPT-4o, released in Ma` | 2000-01 `GPT-4 Turbo is the mos` | None `` | 2000-01 `GPT-4 Turbo, with the ` | 2024-05 `GPT-4o (specifically t` | 2025-04 `GPT-4.1 (released Apri` | 2025-11 `GPT-5.1 Thinking, with` | 2025-11 `GPT-5.1 (released Nove` | 2024-05 `GPT-4o (GPT-4 "omni"),` | 2025-02 `GPT-4.5 ("GPT-4.5"), r` | 2024-05 `GPT-4o — OpenAI's flag` | 2024-05 `GPT-4o (Omni), announc` | 2025-08 `GPT-5, OpenAI's model ` | 2024-05 `GPT-4o.` | 2024-05 `GPT-4o, released in Ma` | 2024-05 `GPT-4o, released in Ma` | 2024-05 `GPT-4o (with variants ` | 2024-05 `The most recent I know` |
| C10 | 2021-01 `Joe Biden is the curre` | 2025-01 `Donald Trump is the cu` | 2025-01 `Donald Trump is the cu` | 2025-01 `Donald Trump is the cu` | 2025-01 `Donald Trump, inaugura` | 2021-01 `Joe Biden.` | 2021-01 `Joe Biden is the curre` | 2025-01 `Donald Trump is the cu` | 2025-01 `Donald Trump, inaugura` | 2025-01 `Donald Trump.` | 2021-01 `Joe Biden is the curre` | 2021-01 `Joe Biden is the curre` | 2021-01 `Joe Biden is the curre` | 2021-01 `Joe Biden is the curre` | 2021-01 `Joe Biden is the curre` | 2025-01 `Donald Trump, who took` | 2025-01 `Donald Trump (as of my` | 2025-01 `of my knowledge, the P` | 2025-01 `Donald Trump, inaugura` | 2025-01 `As of my knowledge cut` | 2025-01 `Donald Trump, inaugura` | 2025-01 `Donald Trump, who bega` | 2025-01 `Donald Trump, who bega` | 2025-01 `Donald Trump is the cu` | 2025-01 `Donald Trump.` | 2021-01 `Joe Biden is the curre` | 2021-01 `Joe Biden is the curre` | 2025-01 `Donald Trump.` | 2025-01 `Donald Trump, as of my` |

## 4. IQ 分题矩阵

| 题 | 模式 | bit/haiku-4-5 | bit/opus-4-6 | bit/opus-4-7 | bit/opus-4-8 | bit/opus-5 | bit/sonnet-5 | bit-screen/haiku-4-5 | bit-screen/opus-4-6 | bit-screen/opus-5 | bit-screen/sonnet-5 | codex666-screen/opus-5 | codex666-screen/sonnet-5 | dragon3/fable-5 | dragon3/opus-5 | dragon3/sonnet-5 | rtoc/glm-5.3-flash | rtoc-anthropic/glm-5.3-flash | tokenking/fable-5-1 | twskyhope/fable-5-1 | v129-K1/glm-5.3-flash | v129-K1-anthropic/glm-5.3-flash | v129-K1-proxy/glm-5.3-flash | v129-K2/glm-5.3-flash | wawapii/opus-5 | wawapii/sonnet-5 | wawapii-cursor/opus-5 | wawapii-cursor/sonnet-5 | zhipu-official/glm-5.3-flash | zhipu-official-anthropic/glm-5.3-flash |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| R2 | default | ✗ | ✗ | ✓ | ✗ | ✓ | ✓ |  |  |  |  |  |  |  | ✗ |  | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| R2 | off | ✗ | ✗ | ✗ | ✗ | ✓ | ✓ |  |  |  |  |  |  |  | ✗ |  | ✓ | ✓ |  | ✓ | ✓ | ✓ |  | ✗ | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ |
| R3 | default | ✗ | ✗ | ✓ | ✗ | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ |
| R3 | off | ✗ | ✓ | ✗ | ✗ | ✓ | ✓ |  |  |  |  |  |  |  | ✓ |  | ✓ | ✓ |  | ✗ | ✓ | ✓ |  | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| R4 | default | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| R4 | off | ✗ | ✓ | ✓ | ✗ | ✓ | ✓ |  |  |  |  |  |  |  | ✓ |  | ✓ | ✗ |  | ✓ | ✗ | ✓ |  | ✗ | ✓ | ✗ | ✓ | ✓ | ✗ | ✓ |
| R7 | default | ✗ | ✗ | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ |
| R7 | off | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ |  |  |  |  |  |  |  | ✓ |  | ✓ | ✗ |  | ✓ | ✗ | ✓ |  | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ |
| R10 | default | ✗ | ✓ | ✗ | ✗ | ✓ | ✓ | ✗ | ✗ | ✓ | ✓ | ✗ | ✗ | ✗ | ✓ | ✗ | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ | ✗ | ✗ | ✓ | ✓ |
| R10 | off | ✗ | ✓ | ✗ | ✓ | ✓ | ✓ |  |  |  |  |  |  |  | ✓ |  | ✗ | ✓ |  | ✗ | ✓ | ✗ |  | ✗ | ✗ | ✓ | ✓ | ✗ | ✓ | ✓ |
| R9 | default | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ | ✗ | ✓ | ✓ | ✓ |
| R9 | off | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ |  |  |  |  |  |  |  | ✓ |  | ✓ | ✓ |  | ✗ | ✓ | ✓ |  | ✓ | ✗ | ✓ | ✗ | ✓ | ✓ | ✗ |
| H1 | default |  |  |  |  | ✓ | ✓ |  |  |  |  |  |  |  | ✓ |  | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| H1 | off |  |  |  |  | ✓ | ✓ |  |  |  |  |  |  |  | ✓ |  | ✓ | ✓ |  | ✓ | ✓ | ✓ |  | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| H2 | default |  |  |  |  | ✓ | ✓ | ✗ | ✗ | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✗ | ✗ | ✓ | ✓ |
| H2 | off |  |  |  |  | ✓ | ✓ |  |  |  |  |  |  |  | ✗ |  | ✓ | ✓ |  | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✗ | ✗ | ✓ | ✓ |
| H3 | default |  |  |  |  | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| H3 | off |  |  |  |  | ✓ | ✓ |  |  |  |  |  |  |  | ✓ |  | ✓ | ✓ |  | ✓ | ✓ | ✓ |  | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| H4 | default |  |  |  |  | ✓ | ✓ |  |  |  |  |  |  |  | ✗ |  | ✓ | ✗ | ✓ | ✓ | ✓ | ✓ |  | ✗ | ✓ | ✓ | ✗ | ✗ | ✗ | ✓ |
| H4 | off |  |  |  |  | ✓ | ✓ |  |  |  |  |  |  |  | ✗ |  | ✗ | ✗ |  | ✓ | ✓ | ✗ |  | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ | ✓ |
| H5 | default |  |  |  |  | ✓ | ✓ |  |  |  |  |  |  |  | ✗ |  | ✓ | ✗ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ |
| H5 | off |  |  |  |  | ✓ | ✓ |  |  |  |  |  |  |  | ✓ |  | ✓ | ✓ |  | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ |
| H6 | default |  |  |  |  | ✓ | ✓ |  |  |  |  |  |  |  | ✗ |  | ✓ | ✓ | ✗ | ✓ | ✗ | ✓ |  | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ |
| H6 | off |  |  |  |  | ✓ | ✓ |  |  |  |  |  |  |  | ✓ |  | ✓ | ✗ |  | ✓ | ✗ | ✓ |  | ✗ | ✓ | ✗ | ✓ | ✓ | ✓ | ✗ |
| X1 | default |  |  |  |  | ✗ | ✓ |  |  |  |  |  |  |  | ✗ |  | ✓ | ✓ | ✓ | ✗ | ✓ | ✗ |  | ✗ | ✗ | ✓ | ✗ | ✓ | ✓ | ✓ |
| X1 | off |  |  |  |  | ✗ | ✓ |  |  |  |  |  |  |  | ✓ |  | ✓ | ✓ |  | ✗ | ✓ | ✓ |  | ✗ | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ |
| X2 | default |  |  |  |  | ✓ | ✓ |  |  |  |  |  |  |  | ✓ |  | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✗ | ✓ | ✗ | ✓ | ✓ | ✓ |
| X2 | off |  |  |  |  | ✓ | ✓ |  |  |  |  |  |  |  | ✓ |  | ✓ | ✓ |  | ✓ | ✗ | ✓ |  | ✓ | ✗ | ✓ | ✗ | ✓ | ✓ | ✓ |
| X3 | default |  |  |  |  | ✓ | ✓ |  |  |  |  |  |  |  | ✗ |  | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| X3 | off |  |  |  |  | ✓ | ✓ |  |  |  |  |  |  |  | ✗ |  | ✓ | ✗ |  | ✓ | ✗ | ✗ |  | ✗ | ✗ | ✓ | ✓ | ✗ | ✗ | ✗ |
| X4 | default |  |  |  |  | ✓ | ✓ |  |  |  |  |  |  |  | ✗ |  | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✗ | ✗ | ✓ | ✓ |
| X4 | off |  |  |  |  | ✓ | ✓ |  |  |  |  |  |  |  | ✗ |  | ✓ | ✗ |  | ✓ | ✓ | ✓ |  | ✗ | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ |
| X5 | default |  |  |  |  | ✓ | ✓ |  |  |  |  |  |  |  | ✓ |  | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ |
| X5 | off |  |  |  |  | ✓ | ✓ |  |  |  |  |  |  |  | ✓ |  | ✓ | ✓ |  | ✓ | ✓ | ✓ |  | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ |
| X6 | default |  |  |  |  | ✓ | ✓ |  |  |  |  |  |  |  | ✓ |  | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ |  | ✓ | ✗ | ✓ | ✗ | ✗ | ✓ | ✓ |
| X6 | off |  |  |  |  | ✓ | ✓ |  |  |  |  |  |  |  | ✗ |  | ✓ | ✓ |  | ✗ | ✗ | ✓ |  | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ |
| X7 | default |  |  |  |  | ✓ | ✗ |  |  |  |  |  |  |  | ✗ |  | ✗ | ✓ | ✗ | ✓ | ✗ | ✓ |  | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ | ✓ |
| X7 | off |  |  |  |  | ✓ | ✗ |  |  |  |  |  |  |  | ✗ |  | ✗ | ✓ |  | ✓ | ✓ | ✗ |  | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| X8 | default |  |  |  |  | ✓ | ✗ |  |  |  |  |  |  |  | ✗ |  | ✓ |  | ✗ | ✓ | ✗ |  |  | ✗ | ✓ | ✗ | ✓ | ✗ | ✗ | ✓ |
| X8 | off |  |  |  |  | ✓ | ✗ |  |  |  |  |  |  |  | ✗ |  | ✗ |  |  | ✓ | ✗ |  |  | ✓ | ✓ | ✗ | ✓ | ✗ | ✓ | ✗ |
| X9 | default |  |  |  |  | ✓ | ✓ |  |  |  |  |  |  |  | ✓ |  | ✓ |  | ✗ | ✓ | ✓ |  |  | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ | ✗ |
| X9 | off |  |  |  |  | ✓ | ✓ |  |  |  |  |  |  |  | ✓ |  | ✓ |  |  | ✓ | ✓ |  |  | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ |
| X10 | default |  |  |  |  | ✓ | ✓ |  |  |  |  |  |  |  | ✓ |  | ✓ |  | ✗ | ✓ | ✓ |  |  | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ |
| X10 | off |  |  |  |  | ✓ | ✓ |  |  |  |  |  |  |  | ✓ |  | ✓ |  |  | ✓ | ✓ |  |  | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ |
| X11 | default |  |  |  |  | ✓ | ✓ |  |  |  |  |  |  |  | ✓ |  | ✓ |  | ✗ | ✓ | ✓ |  |  | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ |
| X11 | off |  |  |  |  | ✓ | ✓ |  |  |  |  |  |  |  | ✓ |  | ✓ |  |  | ✓ | ✓ |  |  | ✗ | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ |
| X12 | default |  |  |  |  | ✓ | ✓ |  |  |  |  |  |  |  | ✗ |  | ✓ |  | ✗ | ✗ | ✓ |  |  | ✗ | ✓ | ✓ | ✗ | ✗ | ✓ | ✓ |
| X12 | off |  |  |  |  | ✓ | ✓ |  |  |  |  |  |  |  | ✓ |  | ✗ |  |  | ✗ | ✗ |  |  | ✗ | ✓ | ✓ | ✗ | ✗ | ✗ | ✓ |
| X13 | default |  |  |  |  | ✓ | ✓ |  |  |  |  |  |  |  | ✗ |  | ✓ |  | ✗ | ✓ | ✓ |  |  | ✓ | ✗ | ✓ | ✗ | ✗ | ✗ | ✓ |
| X13 | off |  |  |  |  | ✓ | ✓ |  |  |  |  |  |  |  | ✗ |  | ✓ |  |  | ✓ | ✗ |  |  | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ |
| X14 | default |  |  |  |  | ✗ | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |  | ✗ | ✗ | ✓ |  |  | ✓ | ✗ | ✓ | ✗ | ✗ | ✓ | ✓ |
| X14 | off |  |  |  |  | ✗ | ✓ |  |  |  |  |  |  |  | ✓ |  | ✓ |  |  | ✗ | ✓ |  |  | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ | ✓ |

## 5. 同站点跨模型聚类 (相同输出 = 很可能同一上游)

### bitmiracle
- claude-haiku-4-5-20251001 vs claude-opus-4-6: 相同输出 1/4 ['c1'] ; input_tokens [20, 19, 23, 29] vs [19, 20, 22, 25]
- claude-haiku-4-5-20251001 vs claude-opus-4-7: 相同输出 1/4 ['c1'] ; input_tokens [20, 19, 23, 29] vs [19, 20, 22, 25]
- claude-haiku-4-5-20251001 vs claude-opus-4-8: 相同输出 1/4 ['c1'] ; input_tokens [20, 19, 23, 29] vs [19, 20, 22, 25]
- claude-haiku-4-5-20251001 vs claude-opus-5: 相同输出 1/4 ['c1'] ; input_tokens [20, 19, 23, 29] vs [30, 28, 34, 43]
- claude-haiku-4-5-20251001 vs claude-sonnet-5: 相同输出 1/4 ['c1'] ; input_tokens [20, 19, 23, 29] vs [30, 28, 34, 43]
- claude-opus-4-6 vs claude-opus-4-7: 相同输出 2/4 ['c1', 'c3'] ; input_tokens [19, 20, 22, 25] vs [19, 20, 22, 25]
- claude-opus-4-6 vs claude-opus-4-8: 相同输出 2/4 ['c1', 'c3'] ; input_tokens [19, 20, 22, 25] vs [19, 20, 22, 25]
- claude-opus-4-6 vs claude-opus-5: 相同输出 1/4 ['c1'] ; input_tokens [19, 20, 22, 25] vs [30, 28, 34, 43]
- claude-opus-4-6 vs claude-sonnet-5: 相同输出 1/4 ['c1'] ; input_tokens [19, 20, 22, 25] vs [30, 28, 34, 43]
- claude-opus-4-7 vs claude-opus-4-8: 相同输出 2/4 ['c1', 'c3'] ; input_tokens [19, 20, 22, 25] vs [19, 20, 22, 25]
- claude-opus-4-7 vs claude-opus-5: 相同输出 1/4 ['c1'] ; input_tokens [19, 20, 22, 25] vs [30, 28, 34, 43]
- claude-opus-4-7 vs claude-sonnet-5: 相同输出 1/4 ['c1'] ; input_tokens [19, 20, 22, 25] vs [30, 28, 34, 43]
- claude-opus-4-8 vs claude-opus-5: 相同输出 1/4 ['c1'] ; input_tokens [19, 20, 22, 25] vs [30, 28, 34, 43]
- claude-opus-4-8 vs claude-sonnet-5: 相同输出 1/4 ['c1'] ; input_tokens [19, 20, 22, 25] vs [30, 28, 34, 43]
- claude-opus-5 vs claude-sonnet-5: 相同输出 1/4 ['c1'] ; input_tokens [30, 28, 34, 43] vs [30, 28, 34, 43]

### dragon3
- claude-fable-5 vs claude-haiku-4-5-20251001: 相同输出 0/4 [] ; input_tokens [19, 20, 22, 25] vs [None, 20, 22, 25]
- claude-fable-5 vs claude-opus-4-6: 相同输出 1/4 ['c1'] ; input_tokens [19, 20, 22, 25] vs [19, 20, 22, 25]
- claude-fable-5 vs claude-opus-4-8: 相同输出 1/4 ['c1'] ; input_tokens [19, 20, 22, 25] vs [19, 20, 22, 25]
- claude-fable-5 vs claude-opus-5: 相同输出 1/4 ['c1'] ; input_tokens [19, 20, 22, 25] vs [19, 20, 22, 25]
- claude-fable-5 vs claude-sonnet-4-6: 相同输出 2/4 ['c1', 'c3'] ; input_tokens [19, 20, 22, 25] vs [19, 20, 22, None]
- claude-fable-5 vs claude-sonnet-5: 相同输出 1/4 ['c1'] ; input_tokens [19, 20, 22, 25] vs [19, 20, None, None]
- claude-haiku-4-5-20251001 vs claude-opus-4-6: 相同输出 0/4 [] ; input_tokens [None, 20, 22, 25] vs [19, 20, 22, 25]
- claude-haiku-4-5-20251001 vs claude-opus-4-8: 相同输出 0/4 [] ; input_tokens [None, 20, 22, 25] vs [19, 20, 22, 25]
- claude-haiku-4-5-20251001 vs claude-opus-5: 相同输出 0/4 [] ; input_tokens [None, 20, 22, 25] vs [19, 20, 22, 25]
- claude-haiku-4-5-20251001 vs claude-sonnet-4-6: 相同输出 0/4 [] ; input_tokens [None, 20, 22, 25] vs [19, 20, 22, None]
- claude-haiku-4-5-20251001 vs claude-sonnet-5: 相同输出 0/4 [] ; input_tokens [None, 20, 22, 25] vs [19, 20, None, None]
- claude-opus-4-6 vs claude-opus-4-8: 相同输出 1/4 ['c1'] ; input_tokens [19, 20, 22, 25] vs [19, 20, 22, 25]
- claude-opus-4-6 vs claude-opus-5: 相同输出 2/4 ['c1', 'c3'] ; input_tokens [19, 20, 22, 25] vs [19, 20, 22, 25]
- claude-opus-4-6 vs claude-sonnet-4-6: 相同输出 1/4 ['c1'] ; input_tokens [19, 20, 22, 25] vs [19, 20, 22, None]
- claude-opus-4-6 vs claude-sonnet-5: 相同输出 1/4 ['c1'] ; input_tokens [19, 20, 22, 25] vs [19, 20, None, None]
- claude-opus-4-8 vs claude-opus-5: 相同输出 2/4 ['c1', 'c4'] ; input_tokens [19, 20, 22, 25] vs [19, 20, 22, 25]
- claude-opus-4-8 vs claude-sonnet-4-6: 相同输出 1/4 ['c1'] ; input_tokens [19, 20, 22, 25] vs [19, 20, 22, None]
- claude-opus-4-8 vs claude-sonnet-5: 相同输出 1/4 ['c1'] ; input_tokens [19, 20, 22, 25] vs [19, 20, None, None]
- claude-opus-5 vs claude-sonnet-4-6: 相同输出 1/4 ['c1'] ; input_tokens [19, 20, 22, 25] vs [19, 20, 22, None]
- claude-opus-5 vs claude-sonnet-5: 相同输出 1/4 ['c1'] ; input_tokens [19, 20, 22, 25] vs [19, 20, None, None]
- claude-sonnet-4-6 vs claude-sonnet-5: 相同输出 2/4 ['c1', 'c2'] ; input_tokens [19, 20, 22, None] vs [19, 20, None, None]

### rtoc-anthropic

### rtoc

### tokenking

### twskyhope

### v129-K1-anthropic

### v129-K1-proxy

### v129-K1

### v129-K2

### wawapii-cursor
- claude-opus-5 vs claude-sonnet-5: 相同输出 0/4 [] ; input_tokens [18, 19, 21, 24] vs [None, None, None, None]

### wawapii
- claude-opus-5 vs claude-sonnet-5: 相同输出 1/4 ['c1'] ; input_tokens [2, 2, 2, 2] vs [828, 829, 832, 834]

### zhipu-official-anthropic

### zhipu-official
