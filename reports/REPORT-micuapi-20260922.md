# micuapi.ai Kiro Claude 分组测试：claude-opus-5 / claude-sonnet-5（2026-09-22）

数据：`results/micu/`（bench full 结果 + probes/ 探针日志 + pelican/），日志 `logs/micu-full-*.log`。key 额度 $50，本次用掉约 $20。
分组特征：Kiro/AWS Bedrock 号池——`toolu_bdrk_` 工具 id、`msg_<uuid>` 响应 id、每次请求带 ~7k token 的 Kiro 隐藏 system prompt 并计费、无 thinking 块、参数不校验（temperature/top_k/prefill/max_tokens=999999 全 200）、count_tokens 404。

## 结论
| 名称 | 实际模型 | 智力 | 主要问题 |
|---|---|---|---|
| claude-opus-5 | Opus 4.6/5 档（知识到 2025-11：知道高市、Mamdani、Opus 4.5；不知超级碗 LX；与官方 Opus 5 黄金基线一致，自报 Opus 4.6 来自 Kiro prompt；ModelTrace 指纹 opus-5 100%） | 24/26（7 题空回复重跑后计） | **约 10–50% 请求落到「空回复池」**（input ≈300–420 token、output 0）；长文本（≥20k）几乎必空；每次多付 7k 隐藏 prompt |
| claude-sonnet-5 | **Sonnet 4.5**（自报 claude-sonnet-4-5-20250929、教宗 Francis、日相石破、GPT-4o；「忽略截止」框架下 6/6 仍不知高市/Mamdani；官方 Sonnet 5 知道 Mamdani） | **31/33**（xhard 13/14，异常强） | 冒名；合成重复文本触发护栏返回空；20k 自然文本把 [NOTE] 当注入拒答 |

## 1. 注入 / 隐藏 prompt
- "Reply with exactly: OK" 计 input 6895（sonnet）/ 7178（opus）token，用户文本 1000 词时 7249/7434 → 隐藏前缀约 **6.9–7.2k token，按输入价计费**。
- 泄漏探针一律「I can't discuss that.」（Kiro 标准回复）。sonnet 直接承认："I'm running in Kiro, an AI-powered development environment… following file editing rules that require content to be split into chunks of 50 lines or fewer"。opus 说自己在 "Anthropic agentic coding CLI"，拒绝谈 Kiro/Amazon。
- **50 行分块规则真实影响输出**：Claude Code 里让 opus 画 SVG 鹈鹕，它在 thinking 里说「要按 ≤50 行分块写」，两次 Write 都只写了 51 行背景，鹈鹕根本没画就报告完成；sonnet 画出来了但把文件写到了自己编造的路径。
- 我们自己的 system prompt 能生效（TESTBOT 测试通过），说明 Kiro prompt 在前、用户 system 在后拼接。
- opus 另有一个「无隐藏 prompt」池：input ≈ 283–420 token，输出永远为空（identity 探针 4/20、决定性探针 3/6、顺序 60 次里 4 次、IQ 33 题里 7 题、自然文本 needle 3/3 全落此池）。

## 2. 智力（iq_full 33 题，默认参数）
| | reason | hard | xhard | 合计 |
|---|---|---|---|---|
| opus-5 | 9/9（3 题空回复） | 6/7（H7 答 22） | 9/10（X6 错；4 题空回复） | 24/26 答出题 ≈ 92% |
| sonnet-5 | 11/12（R2 错） | 7/7 | 13/14（X12 错） | 31/33 ≈ 94% |
sonnet 名下的 Sonnet 4.5 反而比 opus 名下更稳、更强（无空回复，hard 平均 89 s 说明在认真算）。

## 3. 速度与延迟（短问答流式，TTFT 秒）
| | 顺序 60 次 p50 / p90 / p95 / p99 | 空/错 | 30 并发 ×2 波 p50 / p95 / p99 | 成功 | 正文吞吐 |
|---|---|---|---|---|---|
| opus-5 | 3.85 / 5.46 / 6.46 / 9.56 | 4 空 + 1 SSL | 7.05 / 9.74 / 11.81 | 60/60 | 35–45 tok/s，≈8 tok/chunk（块状流） |
| sonnet-5 | 3.88 / 5.22 / 5.36 / 6.02 | 0 | 6.02 / 6.75 / 6.83 | 60/60 | 45–57 tok/s |
bench 自带 8 并发：opus p50 5.8 s / p95 10.9 s，sonnet p50 4.6 s / p95 5.9 s。30 并发无 429/5xx，只是首字翻倍。2500 token 长输出无截断。
注意 bench 的 stability/sequential 用极短请求测到 p50 1.6–1.8 s，上表用的是含「Reply」推理的问答，取后者更接近真实。

## 4. 缓存（8.5k 前缀 system + cache_control，3 s 间隔）
| 项 | opus-5 | sonnet-5 |
|---|---|---|
| 顺序 20 次 | 1 写 + 19 读，read 恒 16811 | 合成文本 20/20 空回复（护栏），换自然文本 1 写 + 7 读，read 17976 |
| 10 并发同前缀 | 10/10 读 | — |
| 多轮增长（8 轮） | 8/8 读，read 17.1k→19.1k 递增 | 8/8 读，但全部空回复（合成文本） |
| 无 cache_control | 不缓存，每次全额 19.8k–21.4k | 同 |
| OpenAI /chat/completions | cached_tokens 恒 0，每次 19.8k | 同 |
| TTL | 空闲 5.5 min 仍命中，空闲 12.5 min 失效 | — |
| 命中是否降 TTFT | 否（4–8 s 不变） | 否 |

**理论最高缓存比例 ≈ 85%。** 命中时 usage = read 16.8k + input 2.97k，input 这 ~3k 无论用户消息多短都不进缓存（Kiro 侧每轮的固定开销），所以能缓存的上限是 read/(read+input) ≈ 16.8/19.8 = 85%，多轮场景实测 84–85%。
read 数字 ≈ 8.5k 前缀 + 7k 隐藏 prompt + 约 1k，没有 aiearth 那种 5–10 倍虚报；但**大 prompt 的 input 计费有 1.3–2.2 倍放大**（20k 文档计 44k，60k 计 75k–118k，130k 计 219k）。
sonnet 在合成文本上第一次请求就报 read 16570（不可能命中的新前缀）→ 空回复时 usage 是估算出来的，不可信。

## 5. 长上下文
| | 20k | 60k | 130k |
|---|---|---|---|
| opus-5 合成 | 3/3 | 空 | 空 |
| opus-5 自然文本 | 空 | 空 | 空（3.4 s 秒回，落空回复池） |
| sonnet-5 合成 | 2/3 | 2/3 | 空 |
| sonnet-5 自然文本 | 拒答（把 [NOTE] 当注入） | **3/3** | 2/3（用中文回答） |
sonnet 长上下文可用；opus 名下长请求基本拿不到回复。

## 6. 协议与其他
- 两模型默认无 thinking，显式 enabled 也无 thinking 块 → 无法验签；`stop_sequences` 无效；`max_tokens` 不生效（visible 511 vs 限制）。
- 流式无 ping 事件、每 chunk ≈8 token（Bedrock 转换流）。
- 缓存 bench 三连发：opus input_tokens 在 [2405, 829, 829] 间跳 → 多账号轮换。

## 7. 给用户
- sonnet-5 = Sonnet 4.5 冒名，但这条渠道本身质量最好：无空回复、p99 6 s、30 并发稳、缓存 85%、xhard 13/14。按 Sonnet 5 价买 Sonnet 4.5 是亏的，按 Sonnet 4.5 价是好渠道。
- opus-5 = Opus 4.6/5 档（知识与官方 Opus 5 一致，无法区分），但空回复池比例高、长文本几乎必空、块状流；Claude Code 里会被 Kiro 的「50 行分块」规则拖累（鹈鹕案例）。
- 两者都每请求多付 ~7k 隐藏 prompt 的输入费；OpenAI 格式完全没有缓存，务必用 Anthropic 格式 + cache_control。
