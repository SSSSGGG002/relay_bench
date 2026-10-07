# claude-fable-5-1 两站对比：远桥云 `sgg` vs twskyhope us-tob2 `kk`（2026-09-17）

> **2026-09-23 更正提示**：文中远桥云 sgg「Opus 4.5 档冒名」的判断改为存疑，原因见 REPORT-yuanqiao-sgg-20260917.md 顶部的更正提示。

结论：**两站都不是 Fable 5.1，但差距明显。** twskyhope 服务的是 Fable 5 档（知识到 2026-01/02，比 5.1 老约 2 个月），
远桥云服务的是 Opus 4.5 档（知识到 2025-10，老约 5 个月）。要在两者里选，twskyhope 更接近声称的模型；
但 twskyhope 现在把 thinking 全部剥掉、并带一个不可见的 GitLab Duo 风格 system prompt。

数据：`results/yuanqiao-sgg/`、`results/twskyhope-kk/`，日志 `logs/yuanqiao-sgg-*.log`、`logs/twskyhope-kk-*.log`。
远桥云单站详细报告：`REPORT-yuanqiao-sgg-20260917.md`。

## 1. 一览
| 项 | 远桥云 sgg | twskyhope kk |
|---|---|---|
| 分组 / 额度 | sgg，无限 | kk，无限（已用 846 万 quota） |
| 模型回显 | claude-fable-5-1 | claude-fable-5.1（点号） |
| 响应 id | msg_011C…（官方） | msg_01…（官方） |
| 透传上游头 | 无 | anthropic-organization-id、anthropic-ratelimit-*、request-id（真 Anthropic API 直出） |
| 默认 thinking | 有（adaptive，签名有效） | **无**；enabled/adaptive/disabled 四种写法全无 thinking 块，thinking_tokens 恒 0 |
| 篡改签名重放 | 400（真验签） | 无法测（拿不到 thinking 块） |
| 隐藏 system prompt | 无（模型自述无、leak 为空、OK=18 token） | **有**：模型承认有指令但拒绝引用；泄漏片段「issues, merge requests, or epics in your namespace」= GitLab Duo 词汇；usage 未计入（OK=21 token，usage 被改写） |
| count_tokens | 404 | 200 |
| 流式 | 真流式，TTFT 2.65 s，30.3 tok/s，0.7 tok/chunk | 真流式，TTFB 0.33 s / 首字 7.8 s，34.3 tok/s，6.1 tok/chunk |
| IQ screen | 8/8，平均 47 s | 7/7 + X14 空回复（中转故障），平均 19 s |
| ModelTrace 指纹 | gpt-6-astra 65%（库无 fable/Opus 4.5，无意义） | gpt-5.5 74% / opus-4-6 25%（同样无意义） |

## 2. 知识前沿（决定性，无 system prompt 时每题 3 次）
| 探针 | 远桥云 sgg | twskyhope kk | 官方 Fable 5.1 黄金基线 |
|---|---|---|---|
| K07 Mamdani 纽约市长（2025-11） | UNKNOWN 6/6（答 Adams） | **Mamdani 3/3**，含 2026-01 就职 | 知道 |
| 最新 Claude | Sonnet/Haiku 4.5，明说不认识 Opus 4.5 | Opus 4.5 3/3 | — |
| K12 Opus 4.6（2026-02-05） | UNKNOWN 3/3 | **Opus 4.6 3/3** | 知道 |
| 最新 GPT | GPT-5 / 5 Pro | GPT-5.1 / 5.2 | — |
| K11 Super Bowl LX（2026-02-08） | UNKNOWN 3/3 | UNKNOWN 3/3 | 知道 |
| K13 Oscars 2026（2026-03） | UNKNOWN | UNKNOWN 3/3 | 知道 |
| K14 Mojtaba（2026-03） | UNKNOWN 3/3 | UNKNOWN 3/3 | 知道 |
| K15–K17（2026-04/05） | UNKNOWN 9/9 | UNKNOWN 9/9 | 不知道 |
| 最晚确认事件 | 2025-10-30 釜山特习会 | 自述 2025-01（自述不采信） | — |
| 推断前沿 | **2025-10 底** | **2026-01 ~ 2026-02 初** | 2026-03 |
| 对应档位 | Opus 4.5 | Fable 5（与 09-10 twskyhope 结论相同） | Fable 5.1 |

twskyhope 认识 2 月 5 日的 Opus 4.6 却不认识 2 月 8 日的 Super Bowl LX，切口在 2026-02 初，正是 Fable 5（cutoff 2026-01）的画像；
官方 Fable 5.1 三项 Feb–Mar 事实 3/3 全知道（09-10 订阅直连实测）。

## 3. twskyhope 与 09-10 相比的变化
- 09-10：默认有 thinking 块且签名有效，可做验签实验；今天四种 thinking 写法全部不返回 thinking，thinking_tokens=0。
- 09-10 未记录隐藏 prompt；今天模型明确承认有系统指令并拒绝透露，自报「Claude Sonnet 4 / 2025-01」，泄漏片段指向 GitLab Duo Chat（issues / merge requests / epics）。
- 透传了 anthropic-organization-id 与 ratelimit 头，说明上游就是 Anthropic API 本体（GitLab Duo 走 Anthropic），中转只改了 usage 和模型名。
- 能力仍是前沿档：screen 7/7、X14 一次空回复属中转故障（09-10 也观察到约 25% 难题假拒答/空回复）。

## 4. 给用户的一句话
两把 key 的 fable-5-1 都是拿老一代冒名：远桥云是 Opus 4.5（2025-10 知识），twskyhope 是 Fable 5（2026-01 知识）。
twskyhope 模型更新、更快，但 thinking 被剥、带 GitLab 风格隐藏提示、难题偶发空回复；远桥云 thinking 和验签是真的，但模型老半年。
两站都用不到 Fable 5.1 的 2026-03 知识，按 Fable 5.1 价格买都是亏的。
