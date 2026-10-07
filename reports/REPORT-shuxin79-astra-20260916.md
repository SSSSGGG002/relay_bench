# shuxin79.top · gpt-6-astra · reasoning_effort low vs high（2026-09-16，Mac/Clash 出口）

问题：用户感觉 low 严重降智、high 正常，像两个模型。

## 结论
1. **low 和 high 打的是同一个上游、同一个模型。**
   - `/v1/responses` 回显：两档都注入同一份 Codex 系统提示（21429 字符，sha256 前缀 52811f43eb，"You are Codex, an agent based on GPT-6"），`safety_identifier` 全程同一个值 `user-kIp6Vk…`，`reasoning.effort` 原样回显 low/high（20/20 次）。
   - ModelTrace 指纹（unified_bank）：low → gpt-6-astra 99.3%，high → gpt-6-astra 81.4%（次选 gpt-5.5 8.9%）。
   - 知识探针 6×4 档：新旧答案（Opus 4.5/GPT-5.2 vs Sonnet 4.6/GPT-5.4/超级碗 LX）在 none/low/medium/high 四档都随机出现，与 effort 无关，是同一模型对临近截止日期事实的抖动。
2. **非流式下 low 并不比 high 笨。** reason+hard 全量题：low 16/17（只错 H2），high 14/16（错 H2、R12）；screen 8 题 low 6/8、high 7/8（R9/R10 抖动，重测都对）。
3. **effort 对推理长度影响很弱**（chat 路径 H2：low 481 / medium 516 / high 950 / xhigh 1938 reasoning tokens；responses 路径 H2：low 203 / medium 209 / high 190 / xhigh 357-516）。R9 这种简单题四档都 50-290。也就是说这条渠道的 astra 基本是"自适应短思考"，low/high 的答案质量差异被抖动淹没。
4. **真正可复现的差异在流式 chat/completions：`reasoning_effort:"low"` + `stream:true` 100% 立刻失败（22/22），** 返回 role chunk 后紧跟上游原文错误 `An error occurred while processing your request… help.openai.com… request ID …`，1-3 秒内返回。同一时刻 none 6/6、high 5/6、medium 3/6 正常（stream_rate.json），`/v1/responses` 流式 low 3/3 正常，非标准嵌套写法 `reasoning:{effort:"low"}` 流式 3/5 正常（与其它档同水平）。→ 站点的 chat→responses 转换在 stream+flat low 这个组合上送了上游不接受的请求，是中转 bug，不是模型差异。
5. 站点稳定性差：11:00 后并发 3 就大量 502（Cloudflare HTML，IQ 33 题里 11 个 502），流式各档随后出现上游原文 `Our servers are currently overloaded`（Codex 账号池被限流）。指纹/IQ 数据用重试补齐。
6. 计费：`/v1/responses` 报 input_tokens 4127（其中 instructions 4116，cached 3968）；chat/completions 只报 prompt_tokens 11，隐藏注入。每次 prompt_cache_key 随机，不吃前缀缓存。`minimal` 被上游 400 拒绝（真实 OpenAI 错误体）。

## 给用户的解释
- 不是两个模型。low 的"降智"体验最可能来自：客户端走 chat/completions 流式 + reasoning_effort=low 时每次都被上游打回，客户端/网关重试或降级后的结果；或者是对同一模型抖动的主观感受（本次 low 在推理题上并不输 high）。
- 规避：用 `/v1/responses`；或 chat 里用 medium/high；或先别用流式 low。让站长查 chat/completions 流式对 low 的参数转换。

## 数据
results/shuxin79-astra/：probe_lh.json（协议+screen IQ）、resp_tag.json（20 次 responses 回显）、know_rep.json（知识 6×4 档）、fp_low.json / fp_high.json（指纹）、effort_scale.json / resp_scale.json（推理 token 缩放）、iq_tiers.json + iq_redo.json（全量 IQ）、stream_rate.json / stream_variants / stream_clean（流式失败率）。

## 补充：Codex CLI 形态的 /v1/responses（用户实际环境）
请求带自己的 instructions、shell tool、`reasoning:{effort,summary:auto}`、`include:[reasoning.encrypted_content]`、`stream:true`、originator=codex_cli_rs 头。
- 中转不再注入 21k Codex 提示，原样保留客户端 instructions（marker 回显 26/26），tools 回显，encrypted_content 有，summary 被改成 detailed。流式 low 26/26 没有 chat 路径那种秒退错误。
- 指纹（responses 路径）：low → gpt-6-astra 99.9%，high → gpt-6-astra 82.9%。
- 账号池：safety_identifier 出现 3 个账号。eJR19M 占 ~85%，dvwHBX ~10%，od1K9I ~3%（60 多次里 2 次，low/high 各 1 次）。od1K9I 明显更旧更弱：日本首相 UNKNOWN、最新 Claude=Opus 4.1、GPT=GPT-5，R4 只想了 24 个 reasoning token 答错。dvwHBX 也有一次答 Ishiba。主账号 eJR19M 知识与前面一致。**账号分配与 effort 无关。**
- screen IQ：low 6/8（R4 错来自 od1K9I 账号，H2 两档都被 Cloudflare 30 s 断流），high 7/8。
- 推理 token：同一提示 low 约 50-190，high 约 90-440，xhigh 更高；low 确实想得很少，但没有跨模型。
- 结论不变：Codex 环境下 low 和 high 是同一个 gpt-6-astra、同一账号池。"low 降智"=（1）low 本身只给几十到一百多 reasoning token；（2）约 3-10% 的请求落到旧/弱账号，随机出现在任何档位。要证明 low 的短思考是否官方常态，需要一把官方或其它可信 astra 渠道做同提示对照。
