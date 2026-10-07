# 远桥云 yuanqiaoyun.com Claude 通道实测（2026-09-16 10:10–10:50，Mac 经 Clash 出海）

站点：远桥云 API（new-api `v1.0.0-rc.24`）。key 所在分组名就叫 **`kiro`**（倍率 0.12），站内分组表还有 `正价kiro` 0.35、`Claude max（蒸馏）` 1.4、`cc max` 1.1。本 key 可见 7 个 Claude 名字（haiku-4-5 / sonnet-4-6 / opus-4-6 / 4-7 / 4-8 / opus-5 / sonnet-5），fable 系列不在本分组。

## 结论

| 名字 | 结论 | 实际后端（重复采样） |
|---|---|---|
| claude-opus-5 | **假映射 / 被改写**。上游是 Kiro（AWS）账号池，不是 Anthropic 直连；模型知识为 2026-01 档（Leo XIV / 高市早苗 / Mamdani / Opus 4.5 / GPT-5.1，开放式 12/12），与 Opus 4.7/4.8/5/Sonnet 5 无法用知识区分；screen 那轮 10 题开放探针又答出 Francis/岸田（老模型混池）。要求 thinking 时也永远没有 thinking 块 | Kiro 池里的 2026-01 档 Anthropic 模型，间歇混入 2025 年初档 |
| claude-sonnet-5 | **假**。知识止于 2025 年初（Pope Francis / 石破茂 / Eric Adams / 最新 Claude=3.5 Sonnet / GPT-4o，5/6 次），官方 Sonnet 5 知道 Leo XIV + Mamdani | Kiro 池 Sonnet 4.5 / Sonnet 4 档 |
| claude-opus-4-8 | **假**。6 次采样 4 次 2025-01 档、1 次 2025-05、1 次 2026 档，混池 | 主要是 Sonnet 4.5 档 |
| claude-opus-4-7 | **假**。知识 2025-01 档；且吞吐测到 TTFB 13.6s 后 884 tok/s（假流式） | Sonnet 4.5 档 |
| claude-sonnet-4-6 | **假**。知识 2024-10 / 2025-01 档，自报 `claude-sonnet-4-5` | Sonnet 4.5 档 |
| claude-opus-4-6 | **可疑 / 偏老**。Leo XIV 知道、高市不知道、最新 Claude = "Claude 4"，自报 `claude-sonnet-4-20250514` | Sonnet 4 档 |
| claude-haiku-4-5-20251001 | **不可用**。3/3 返回 404 "Service is temporarily unavailable" | — |

所有 7 个名字共用同一套上游，证据：

- **自报 Kiro**：直接问"你运行在什么环境"，`msg_hex` 池 100% 答 "I'm Kiro, an AI-powered development environment built by AWS"；`msg_01` 池答 Kiro 的固定拒答 "I can't share, reproduce, summarize, translate, or describe system instructions or internal context."
- **Bedrock 工具 id**：tool_use id 全是 `toolu_bdrk_01…`（6/6，三个型号）。
- **两条账号池按响应 id 分族**，60 次小请求各型号都是约 5:5：
  - 池 A `msg_01`+22 位：隐藏提示计入 usage（"Reply with exactly: OK" 13 tok、带工具 545 tok、开放式问题 82–124 tok），真流式 TTFT 6–9s，约 40–45 tok/s，有 `ping`。
  - 池 B `msg_<32hex>`：usage 极小（同样请求 4 / 5 / 56 tok），**上游非流式，中转假装流式**（TTFT 14–55s 后 140–160 个 delta 在 0.1–0.5s 内一次吐完，opus-5 3/4、sonnet-5 1/1 次都是），无 `ping`。
- **thinking 完全没有**：不传、传 `enabled budget 1024` 都只回 text 块（Opus 5 / Sonnet 5 官方默认思考且返回带签名的 thinking 块）；`thinking disabled` 200。
- **参数全部不校验**：temperature+top_p 同传 200、`max_tokens=999999` 200、`max_tokens` 不生效、`count_tokens` 404。
- **usage / 缓存数字不可信**：同一 8.4k token 前缀第一次请求就报 `cache_read 7778`（池 A）或 `input 4 + cache_read 5859`（池 B），是适配层编的数字，不能当省钱依据。
- 一处更严重的坑：sonnet-5 名字在 144k token 输入时，池 A 把输入**截到 16,430 token**再回答（usage 也只报 16430），池 B 全量接收但以"这像提示注入测试"为由拒答；opus-5 名字 53k / 144k / 207k token 三针召回 3/3（自然文本）。

## 速度 / 稳定 / 价格

- opus-5 小请求 p50 6.8s；池 A TTFT 6–9s、40 tok/s；池 B TTFT 14–55s 假流式。opus-4-7 p50 22.5s。
- 12 并发：12/12 成功，但时延 7.6–54.5s 两级分化（池 B 慢）。
- screen 8 题智力：opus-4-7 / 4-8 8/8，opus-5 7/7（1 次中转空回）、sonnet-5 7/7、opus-4-6 与 sonnet-4-6 7/8 —— 全部是 Sonnet 4.5 档水平，拉不开差距，也说明各名字后端同质。
- 价格（分组 kiro 0.12 × new-api 基价 $2/M）：opus-5 / 4-x ≈ $0.6/M 入、$3/M 出；sonnet-5 ≈ $0.24/$1.2；haiku ≈ $0.12/$0.6。既然所有名字都是同一个池、同一档模型，**买这个分组只该调 sonnet-5 这个最便宜的名字**，调 opus-5 多付 2.5 倍拿不到更好的模型。
- 本轮约 320 次调用（含 3 次 140–210k 长文）合计消耗约 $1.7。

原始数据：`results/yuanqiao/*.json`（screen 档）、`results/yuanqiao/probes/`（手工探针脚本与输出）。下面是 report.py 自动汇总。

---

# relay-bench 报告

结果文件: 7 个 (目录 <本地临时目录>)

## 0. 智力分档对比（拉开差距的核心）

每格 = 答对数/总题数（思考默认开启；`_off` = 强制关闭思考）。只统计当前题库 `suite/iq_keep.json` 里的 26 题；中转拒答/空响应不计入分母（括号内为剔除次数）。难度递增：reason < hard < xhard。

| 站点/模型 | screen | 合计 |
|---|---|---|
| yuanqiao/opus-4-6 | 7/8 | **7/8** |
| yuanqiao/opus-4-7 | 8/8 | **8/8** |
| yuanqiao/opus-4-8 | 8/8 | **8/8** |
| yuanqiao/opus-5 | 7/7 | **7/7** (中转故障剔除1) |
| yuanqiao/sonnet-4-6 | 7/8 | **7/8** |
| yuanqiao/sonnet-5 | 7/7 | **7/7** (中转故障剔除1) |

### 各题耗时（reason+hard+xhard，思考开启，单位秒）

| 站点/模型 | reason均 | hard均 | xhard均 |
|---|---|---|---|
| yuanqiao/opus-4-6 | - | - | - |
| yuanqiao/opus-4-7 | - | - | - |
| yuanqiao/opus-4-8 | - | - | - |
| yuanqiao/opus-5 | - | - | - |
| yuanqiao/sonnet-4-6 | - | - | - |
| yuanqiao/sonnet-5 | - | - | - |

## 1. 总览矩阵

| 站点 | 模型 | 协议 | 结论 | 上游形态 | 参数一致率 | 知识前沿(阶梯/开放) | 自报 | tok比率EN | 注入tok | 缓存 | 缓存隔离/过期 | TTFT中位 | tok/s中位 | p50 | 并发成功 | soak错误率 | IQ直答 | IQ推理 | IQ困难 | IQ超难 | ctx20k | ctx60k | ctx130k | ctx230k | 红旗 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| yuanqiao | claude-haiku-4-5-20251001 | anth | UNREACHABLE | ? 注入≈- id= | - | -/- | -/- | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | - | 1 |
| yuanqiao | claude-opus-4-6 | anth | OK-ish | ? 注入≈-1 id=msg_3c9c5 | - | -/2025-05 | amazon/sonnet4 | - | -1 | - | - | 2.5 | 31.2 | - | - | - | - | - | - | - | - | - | - | - | 2 |
| yuanqiao | claude-opus-4-7 | anth | FAKE/ALTERED | ? 注入≈8 id=msg_01L2S | - | -/2025-01 | i can't discuss that./- | - | 8 | - | - | 13.63 | 884.2 | - | - | - | - | - | - | - | - | - | - | - | 2 |
| yuanqiao | claude-opus-4-8 | anth | FAKE/ALTERED | ? 注入≈8 id=msg_01J6g | - | -/2025-05 | i can't discuss that./- | - | 8 | - | - | 4.43 | 39.9 | - | - | - | - | - | - | - | - | - | - | - | 3 |
| yuanqiao | claude-opus-5 | anth | FAKE/ALTERED | ? 注入≈8 id=msg_01Qem | - | -/2025-09 | amazon/- | - | 8 | - | - | 4.12 | 39.5 | - | - | - | - | - | - | - | - | - | - | - | 3 |
| yuanqiao | claude-sonnet-4-6 | anth | FAKE/ALTERED | ? 注入≈8 id=msg_01pxU | - | -/2024-10 | anthropic/sonnet4 | - | 8 | - | - | 13.16 | 709.6 | - | - | - | - | - | - | - | - | - | - | - | 1 |
| yuanqiao | claude-sonnet-5 | anth | FAKE/ALTERED | ? 注入≈-1 id=msg_31d11 | - | -/2024-10 | i can't discuss that./- | - | -1 | - | - | 3.38 | 45.0 | - | - | - | - | - | - | - | - | - | - | - | 3 |

结论分级: CLEAN=无红旗; OK-ish=有轻微红旗; SUSPICIOUS=≥3个红旗; FAKE/ALTERED=知识截止/自报身份/签名证据表明不是所声称的模型。

## 2. 每个模型的红旗与关键证据

### yuanqiao / claude-haiku-4-5-20251001  → **UNREACHABLE**
- 红旗: basic call failed
- 自报: ``
- 知识前沿: 阶梯=None 开放式=None 判定=None (声称型号 claude-haiku-4-5)
- [WARN] protocol/basic_retries: all 3 attempts failed: [404, 404, 404]
- [FAIL] protocol/basic: HTTP 404 {'type': '<nil>', 'code': None, 'message': 'Service is temporarily unavailable, please retry later (request id: 202609161011463039678798268d9d6aUi4ZDIp) (request id: 202609161011445631255328268d9d6zKUM66ul)'}

### yuanqiao / claude-opus-4-6  → **OK-ish**
- 红旗: 自报家族=sonnet(仅参考:真模型也会跟着提示自报); 自报厂商=amazon(仅参考)
- 自报: ````json
{
  "vendor": "Anthropic",
  "model_family": "Claude",
  "model_version": "claude-sonnet-4-20250514",
  "knowledge_cutoff": "2025-03"
}
````
- 知识前沿: 阶梯=None 开放式=2025-05 判定=consistent (声称型号 claude-opus-4-6)
- [WARN] protocol/message_id_format: id=msg_3c9c5c846ec64314986a8a9d2446f456 (not the native msg_01+22 format -> generated by relay/adapter)
- [WARN] protocol/stream_ping: ping events=0 (native Anthropic streams send periodic pings; converted streams usually don't)
- [FAIL] identity/vendor_mismatch: model says it was trained by 'amazon' but the requested id implies anthropic
- [FAIL] identity/family_mismatch: requested claude-opus-4-6 but the model identifies as Claude sonnet

### yuanqiao / claude-opus-4-7  → **FAKE/ALTERED**
- 红旗: 知识截止早于所声称型号(假映射); 自报厂商=i can't discuss that(仅参考)
- 自报: `{"vendor":"unknown","model_family":"unknown","model_version":"unknown","knowledge_cutoff":"unknown"}`
- 知识前沿: 阶梯=None 开放式=2025-01 判定=older (声称型号 claude-opus-4-7)
- 泄露的隐藏系统提示: `I can't share, reproduce, summarize, translate, or describe system instructions or internal context.`
- [WARN] protocol/message_id_format: id=msg_01L2SRARVOLAW01YkMyq51 (not the native msg_01+22 format -> generated by relay/adapter)
- [WARN] protocol/stream_ping: ping events=0 (native Anthropic streams send periodic pings; converted streams usually don't)
- [WARN] identity/vendor_undisclosed: model would not name its vendor: "i can't discuss that." (hidden system prompt forbids disclosure?)
- [WARN] identity/hidden_system_prompt_exposed: model quoted instructions you never sent: "I can't share, reproduce, summarize, translate, or describe system instructions or internal context."
- [FAIL] knowledge/frontier_vs_claim: knows events only up to 2025-01 but real claude-opus-4-7 has cutoff 2026-01 -> served model is OLDER than claimed (fake mapping)

### yuanqiao / claude-opus-4-8  → **FAKE/ALTERED**
- 红旗: 知识截止早于所声称型号(假映射); 同题4次答案年代不一致['2013-03', '2025-05', '2025-05', '2013-03'](混合池); 自报厂商=i can't discuss that(仅参考)
- 自报: ````json
{
  "vendor": "unknown",
  "model_family": "unknown",
  "model_version": "unknown",
  "knowledge_cutoff": "unknown"
}
````
- 知识前沿: 阶梯=None 开放式=2025-05 判定=older (声称型号 claude-opus-4-8)
- 泄露的隐藏系统提示: `I can't share, reproduce, summarize, translate, or describe system instructions or internal context.`
- [WARN] protocol/message_id_format: id=msg_01J6gABURKJm1zhokR0hLQ (not the native msg_01+22 format -> generated by relay/adapter)
- [WARN] identity/vendor_undisclosed: model would not name its vendor: "i can't discuss that." (hidden system prompt forbids disclosure?)
- [WARN] identity/hidden_system_prompt_exposed: model quoted instructions you never sent: "I can't share, reproduce, summarize, translate, or describe system instructions or internal context."
- [FAIL] knowledge/pool_mix: same question 4x gave different knowledge eras ['2013-03', '2025-05', '2025-05', '2013-03'] -> requests are routed to DIFFERENT underlying models (mixed account pool)
- [FAIL] knowledge/frontier_vs_claim: knows events only up to 2025-05 but real claude-opus-4-8 has cutoff 2026-01 -> served model is OLDER than claimed (fake mapping)

### yuanqiao / claude-opus-5  → **FAKE/ALTERED**
- 红旗: 知识明显少于官方同型号(假映射); 默认无thinking块(Claude 5系应默认思考); 自报厂商=amazon(仅参考)
- 自报: ````json
{
  "vendor": "unknown",
  "model_family": "unknown",
  "model_version": "unknown",
  "knowledge_cutoff": "unknown"
}
````
- 知识前沿: 阶梯=None 开放式=2025-09 判定=older (声称型号 claude-opus-5)
- 与官方同型号金标准逐题对比: 官方知道而它不知道=[] ; 它知道而官方不知道=[] ; 双方都知道=0 ; 开放式探针比官方更旧=['C1', 'C2', 'C3', 'C5', 'C7', 'C9'] 更新=[]
- 泄露的隐藏系统提示: `I can't share, reproduce, summarize, translate, or describe system instructions or internal context.`
- [WARN] protocol/message_id_format: id=msg_01QemTO0SDRlNeeBTjSd1j (not the native msg_01+22 format -> generated by relay/adapter)
- [FAIL] protocol/thinking_default: default request has thinking block=False ; real claude-opus-5 -> True
- [WARN] protocol/stream_ping: ping events=0 (native Anthropic streams send periodic pings; converted streams usually don't)
- [FAIL] identity/vendor_mismatch: model says it was trained by 'amazon' but the requested id implies anthropic
- [WARN] identity/hidden_system_prompt_exposed: model quoted instructions you never sent: "I can't share, reproduce, summarize, translate, or describe system instructions or internal context."
- [FAIL] knowledge/frontier_vs_claim: knows events only up to 2025-09 but real claude-opus-5 has cutoff 2026-05 -> served model is OLDER than claimed (fake mapping)

### yuanqiao / claude-sonnet-4-6  → **FAKE/ALTERED**
- 红旗: 知识截止早于所声称型号(假映射)
- 自报: ````json
{
  "vendor": "Anthropic",
  "model_family": "Claude",
  "model_version": "claude-sonnet-4-5",
  "knowledge_cutoff": "2025-02"
}
````
- 知识前沿: 阶梯=None 开放式=2024-10 判定=older (声称型号 claude-sonnet-4-6)
- [WARN] protocol/message_id_format: id=msg_01pxUy8VxU7xG3LKq6a6x0 (not the native msg_01+22 format -> generated by relay/adapter)
- [FAIL] knowledge/frontier_vs_claim: knows events only up to 2024-10 but real claude-sonnet-4-6 has cutoff 2025-08 -> served model is OLDER than claimed (fake mapping)

### yuanqiao / claude-sonnet-5  → **FAKE/ALTERED**
- 红旗: 知识明显少于官方同型号(假映射); 默认无thinking块(Claude 5系应默认思考); 自报厂商=i can't discuss that(仅参考)
- 自报: `{"vendor": "Anthropic", "model_family": "Claude", "model_version": "unknown", "knowledge_cutoff": "unknown"}`
- 知识前沿: 阶梯=None 开放式=2024-10 判定=older (声称型号 claude-sonnet-5)
- 与官方同型号金标准逐题对比: 官方知道而它不知道=[] ; 它知道而官方不知道=[] ; 双方都知道=0 ; 开放式探针比官方更旧=['C1', 'C2', 'C3', 'C5', 'C7', 'C9', 'C10'] 更新=[]
- [WARN] protocol/message_id_format: id=msg_31d113f4b54e43c2839fc157a1f92677 (not the native msg_01+22 format -> generated by relay/adapter)
- [FAIL] protocol/thinking_default: default request has thinking block=False ; real claude-sonnet-5 -> True
- [WARN] identity/vendor_undisclosed: model would not name its vendor: "i can't discuss that." (hidden system prompt forbids disclosure?)
- [FAIL] knowledge/frontier_vs_claim: knows events only up to 2024-10 but real claude-sonnet-5 has cutoff 2026-01 -> served model is OLDER than claimed (fake mapping)

## 3. 知识截止阶梯 (✓知道 ?不知道 ✗答错 !错误)

| 题 | 日期 | yuanqiao/opus-4-6 | yuanqiao/opus-4-7 | yuanqiao/opus-4-8 | yuanqiao/opus-5 | yuanqiao/sonnet-4-6 | yuanqiao/sonnet-5 |
|---|---|---|---|---|---|---|---|
| K00 | 2024-11 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

## 3b. 开放式近期知识探针 (答案所属年代)

| 题 | yuanqiao/opus-4-6 | yuanqiao/opus-4-7 | yuanqiao/opus-4-8 | yuanqiao/opus-5 | yuanqiao/sonnet-4-6 | yuanqiao/sonnet-5 |
|---|---|---|---|---|---|---|
| C1 | 2025-05 `Pope Leo XIV (Robert F` | 2013-03 `Pope Francis, elected ` | 2025-05 `Pope Leo XIV, elected ` | 2013-03 `Pope Francis, elected ` | 2013-03 `Pope Francis, elected ` | 2013-03 `Pope Francis (Jorge Ma` |
| C2 | 2024-10 `Shigeru Ishiba.` | 2021-10 `As of my knowledge cut` | 2021-10 `As of my knowledge cut` | 2021-10 `Fumio Kishida is Japan` | 2024-10 `Fumio Kishida. (Though` | 2021-10 `Fumio Kishida.` |
| C3 | 2022-01 `Eric Adams.` | 2022-01 `Eric Adams, who took o` | 2022-01 `Eric Adams is the mayo` | 2022-01 `Eric Adams is the mayo` | 2022-01 `Eric Adams is the mayo` | 2022-01 `Eric Adams` |
| C4 | 1989-06 `Ayatollah Ali Khamenei` | 1989-06 `Ali Khamenei has been ` | 1989-06 `Ali Khamenei is the cu` | 1989-06 `Ali Khamenei has been ` | 1989-06 `Ali Khamenei, who has ` | 1989-06 `Ali Khamenei.` |
| C5 | 2024-02 `The Kansas City Chiefs` | 2024-02 `Kansas City Chiefs won` | 2024-02 `The Kansas City Chiefs` | 2024-02 `The Kansas City Chiefs` | 2024-02 `The Kansas City Chiefs` | 2024-02 `Kansas City Chiefs won` |
| C6 | 2022-12 `Argentina won the 2022` | 2022-12 `Argentina won the most` | 2022-12 `Argentina won the most` | 2022-12 `Argentina won the 2022` | 2022-12 `Argentina won the most` | 2022-12 `Argentina won the 2022` |
| C7 | 2024-10 `Han Kang, 2024.` | 2023-10 `Jon Fosse, Norwegian a` | 2000-01 `Annie Ernaux, 2022 Nob` | 2024-10 `Han Kang, South Korean` | 2024-10 `Han Kang, 2024 Nobel P` | 2023-10 `Jon Fosse, 2023 Nobel ` |
| C8 | 2024-10 `Claude 3.5 Sonnet (cla` | 2024-10 `Claude 3.5 Sonnet (Oct` | 2024-10 `Claude 3.5 Sonnet (the` | 2025-09 `Claude Sonnet 4.5 (cla` | 2024-10 `Claude 3.5 Sonnet (cla` | 2024-10 `Claude 3.5 Sonnet (Jun` |
| C9 | 2024-05 `GPT-4o (GPT-4 Omni), r` | 2024-05 `GPT-4o (GPT-4 Omni), r` | 2024-05 `GPT-4o (GPT-4 Omni), r` | 2024-05 `GPT-4o (including GPT-` | 2024-05 `GPT-4o` | 2024-05 `GPT-4o` |
| C10 | 2021-01 `Joe Biden.` | 2025-01 `As of my knowledge cut` | 2025-01 `As of my knowledge cut` | 2025-01 `Donald Trump, inaugura` | 2021-01 `Joe Biden.` | 2021-01 `Joe Biden.` |

## 4. IQ 分题矩阵

| 题 | 模式 | yuanqiao/opus-4-6 | yuanqiao/opus-4-7 | yuanqiao/opus-4-8 | yuanqiao/opus-5 | yuanqiao/sonnet-4-6 | yuanqiao/sonnet-5 |
|---|---|---|---|---|---|---|---|
| R3 | default | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| R4 | default | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| R7 | default | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| R9 | default | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| R10 | default | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| H2 | default | ✗ | ✓ | ✓ | ✓ | ✗ | ✓ |
| H3 | default | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ |
| X14 | default | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ |

## 5. 同站点跨模型聚类 (相同输出 = 很可能同一上游)
