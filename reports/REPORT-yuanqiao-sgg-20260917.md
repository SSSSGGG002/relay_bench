# 远桥云 yuanqiaoyun.com — `sgg` 分组 claude-fable-5-1 真伪测试（2026-09-17）

> **2026-09-23 更正提示**：本报告把 sgg 分组的 claude-fable-5-1 判为「Opus 4.5 档冒名」，现改为存疑。当时的依据是知识止于 2025 年 10 月底；9 月 23 日在 fluxionai.space 确认，一套隐藏模板（含「不得陈述 2025 年 10 月之后的事实」）会让真 Fable 5.1 在知识题上正好表现成这样，同时改写 usage、让模型否认有 system prompt，所以本报告「无隐藏提示」的判断也不可靠。本站当时的思考签名格式与那边确认的 Fable 5.1 相同。更可能是真 Fable 级模型被同类模板压制。详见 REPORT-fluxion-fable-20260923.md。

结论：**假映射。** 上游是真 Anthropic 协议（thinking 签名有效、篡改签名被 400 拒、msg_011C… id、官方 usage 字段含 inference_geo），
但被服务的模型知识止于 2025-10 下旬，比官方 Fable 5.1（黄金基线前沿 2026-03）老约 5 个月，
特征对应 **Claude Opus 4.5 档**（认识 Sonnet 4.5 / Haiku 4.5，不认识 Opus 4.5 本身、不知道 Mamdani 当选）。
同 key 的 claude-opus-5 名字与之同池；claude-fable-5 名字更差，是 Claude 4 / 3.5 混池。

数据：`results/yuanqiao-sgg/`（bench screen json + probe-*.json），日志 `logs/yuanqiao-sgg-*.log`。

## 1. key 信息
- 分组名 `sgg`，无限额度；站内 fable 名字公开只挂在 `Claude max（蒸馏）`1.4 / `cc max`1.1 两组，`sgg` 不在公开 group_ratio 里。
- 可用名字：claude-fable-5-1, claude-fable-5, claude-opus-5, claude-opus-4-6/4-7/4-8, claude-sonnet-5, claude-sonnet-4-6。

## 2. 协议（fable-5-1）
| 项 | 结果 |
|---|---|
| 响应 id | `msg_011C…`（官方格式，与 opus-5/fable-5 名字同族） |
| usage | 官方字段 + `output_tokens_details.thinking_tokens` + `inference_geo:global` |
| 默认 thinking | 有（adaptive，空 thinking + 签名） |
| 篡改 signature 重放 | **400 Invalid signature**（真验签） |
| 篡改 thinking 文本 / 删签名重放 | 200（官方对上一轮非工具调用的 thinking 块本就忽略，不作为证据） |
| 隐藏提示 | 无：`Reply with exactly: OK` 计 18 input tokens；模型自述无 system prompt；prompt-leak 为空 |
| count_tokens | 404（new-api 未代理，非证据） |
| 流式 | 真流式，有 ping，TTFT 2.65 s，30.3 tok/s，0.7 tok/chunk |

## 3. 知识前沿（决定性证据，无 system prompt，每题 3 次）
| 探针 | fable-5-1 | 官方 Fable 5.1 黄金基线 |
|---|---|---|
| K11 Super Bowl LX (2026-02) | UNKNOWN 3/3 | 知道 |
| K12 Opus 4.6 (2026-02) | UNKNOWN 3/3 | 知道 |
| K13 Oscars 2026 (2026-03) | UNKNOWN 2/3 + 1 空回复 | 知道 |
| K14 Mojtaba (2026-03) | UNKNOWN 3/3 | 知道 |
| K15–K17 (2026-04/05) | UNKNOWN 9/9 | 不知道 |
| K07 Mamdani 纽约市长 (2025-11) | UNKNOWN 6/6，一律答 Eric Adams | 官方 Opus 5 / Sonnet 5 都知道 |
| 最新 Claude | Sonnet 4.5 / Haiku 4.5（2025-10），明确说不认识 Opus 4.5 | — |
| 最新 GPT | GPT-5 / GPT-5 Pro | — |
| 现任 | Leo XIV、高市早苗（2025-10-21）、Eric Adams | — |
| 最晚能确认的事件 | 2025-10-30 特朗普–习近平釜山会晤 | — |

→ 知识止于 2025-10 底、2025-11 初之前。认识 Haiku 4.5（10-15）却不认识 Opus 4.5（11-24）、不知 Mamdani（11-04），
是 **Opus 4.5 档模型**的典型画像；不是 Fable 5.1（2026-03 前沿），也不是 Fable 5（2026-01 前沿，见 twskyhope 记录）。

bench screen 的 `recency frontier=2026-07 PASS` 是打分器误判（把「My knowledge cutoff is January…」等自述当年代），
且一次回答「Claude Opus 4.6 released November 2025」是把 Opus 4.5 的时间张冠李戴，实际 Opus 4.6 是 2026-02。自述 cutoff 三个值（2025-01 / 2025-08 / 2026-01）互相矛盾，按惯例不采信。

## 4. 智力 / 指纹
- IQ screen **8/8**（R3 R4 R7 R9 R10 H2 H3 X14），平均 47 s —— 是前沿旗舰级的能力，与 Opus 4.5 档一致，不能靠 IQ 区分 4.5 与 5.1。
- ModelTrace 指纹：gpt-6-astra 65.5% / GPT 家族 98.3%。**库里没有 fable 也没有 Opus 4.5**，闭集结果无归属意义，只说明它不像库里任何一个 Claude（sonnet-5 1.5%）。

## 5. 同 key 其他名字对照（同一 probe 脚本）
| 名字 | 现任日相 | 最新 Claude | 最晚事件 | 判断 |
|---|---|---|---|---|
| claude-fable-5-1 | 高市 3/3 | Sonnet/Haiku 4.5 | 2025-10-30 | Opus 4.5 档 |
| claude-opus-5 | 高市 2/3、石破 1/3 | Haiku 4.5 ×2、Sonnet 4.5 ×1 | 2024-12 ~ 2025-01 | 与 fable-5-1 同池（Opus 4.5 档，略混） |
| claude-fable-5 | 石破 3/3；一次教宗答 Francis | Opus 4 / Sonnet 4 ×2、Claude 3.5 ×1 | 2025-01 | 更老的混池：Claude 4/4.1 档 + 3.x 档 |

三个名字全部 Feb–May 2026 探针 UNKNOWN 21/21；三个名字签名验证行为一致（篡改签名 400）。

## 6. 给用户的一句话
这把 key 的 fable-5-1 是**用 Opus 4.5 档模型冒名**：接的是真 Anthropic 通道（不是 Kiro/Bedrock 假流式那种），推理能力不差，但绝不是 Fable 5.1；
同 key 调 opus-5 得到的是同样的东西，fable-5 名字反而更烂。要验证可任选 Feb–Mar 2026 事实各问 3 次，官方 Fable 5.1 全知道，这里全 UNKNOWN。
