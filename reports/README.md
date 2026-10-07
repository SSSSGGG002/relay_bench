# 历史测试报告索引

2026-09-09 起各中转站的实测报告。每份报告写明测试时间、路线（Mac + Clash 出海 / 北京服务器直连）、用了什么基线对照。

- 报告里的 key 只保留前后几位（如 `sk-SqQx…`），服务器地址写成 `<北京服务器>`。
- 原始数据（逐次请求、账单、延迟明细）不入库，报告里出现的 `results/...` 路径在仓库里找不到。
- 中转站随时换上游。报告只代表当天、当条路线的状态，引用前先看日期；对比新站请按 [docs/BASELINES.md](../docs/BASELINES.md) 先跑 `refcheck.py` 确认参考站没变。
- 单行结论是从报告里摘出来的要点，细节和证据以报告正文为准。

## 参考站 ikuncode（基线来源）

| 报告 | 模型 | 一句话 |
|---|---|---|
| [REPORT-ikuncode-vs-hyhawang-kiro-20260924](REPORT-ikuncode-vs-hyhawang-kiro-20260924.md) | opus-5 / sonnet-5 | Kiro 池；opus-5 真 Opus 4.6/5 档（IQ 25/26），sonnet-5 是 Sonnet 4.5 冒名；缓存是固定拆分；慢且抖（Mac 路线） |
| [REPORT-ikuncode-o55-20260926](REPORT-ikuncode-o55-20260926.md) | opus-5-5 | 两渠道同上游，2026 前沿档（知识到 2026-03、IQ 27/27、52.7 万 token 三针全中），北京延迟稳 |
| [COST-ikuncode-ccrev-20261007](COST-ikuncode-ccrev-20261007.md) / [sonnet-5-5](COST-ikuncode-ccrev-sonnet55-20261007.md) | 4 个 Claude 模型 | 固定负载实扣：按站点公式诚实计费（1.02–1.04×） |
| [INJCACHE-ikuncode-ccrev-20261007](INJCACHE-ikuncode-ccrev-20261007.md) | sonnet-5-5 / opus-5-5 / sonnet-5 | cc逆向分组也是 Kiro；隐藏提示词不计费；缓存是中转模拟的但规则公道 |
| [REPORT-dsv4flash-sudocode-vs-ikuncode-20260922](REPORT-dsv4flash-sudocode-vs-ikuncode-20260922.md) | deepseek-v4-flash | 两家同为火山方舟 0731 池；ikuncode 套了 router- 网关、慢一倍 |
| [OPS-ikun-dsv4f-0922](OPS-ikun-dsv4f-0922.md) / [OPS-sudo-dsv4f-0922](OPS-sudo-dsv4f-0922.md) | deepseek-v4-flash | 上面那次对比的缓存 / 速度 / 稳定性明细 |

## Claude（opus-5 / opus-5-5 / sonnet-5 / fable-5-1）

| 报告 | 站点 | 一句话 |
|---|---|---|
| [REPORT-claude-gpt-20260909](REPORT-claude-gpt-20260909.md) | 多站（自动矩阵） | 第一轮 Claude + GPT 横测，bench.py 自动生成 |
| [REPORT-yjapi-20260911](REPORT-yjapi-20260911.md) | yjapi 满桥 | opus-5 / fable-5-1 假映射（Bedrock） |
| [REPORT-aiearth-billing-20260914](REPORT-aiearth-billing-20260914.md) | aiearth | 计费公式诚实，但 Kiro 积分池报 5–10 倍假缓存 token |
| [REPORT-yuanqiao-20260916](REPORT-yuanqiao-20260916.md) | 远桥云 | Claude 全是 Kiro 池 |
| [REPORT-yuanqiao-sgg-20260917](REPORT-yuanqiao-sgg-20260917.md) | 远桥云 sgg | fable-5-1 真伪（09-23 复核改判存疑） |
| [REPORT-fable-compare-20260917](REPORT-fable-compare-20260917.md) | 远桥云 vs twskyhope | fable-5-1 两站对比；twskyhope 是 Fable 5 顶名 |
| [REPORT-worldclaw-20260917](REPORT-worldclaw-20260917.md) | WorldClawPro | Kiro / Claude Code 池；sonnet-5 = Sonnet 4.5 档 |
| [REPORT-runapi-20260921](REPORT-runapi-20260921.md) | runapi | fable 冒名；opus/sonnet 真号池与假 usage 老模型池各半 |
| [REPORT-micuapi-20260922](REPORT-micuapi-20260922.md) | 米醋 | sonnet-5 = Sonnet 4.5 但渠道最稳；opus-5 有空回复池；Kiro 7k 隐藏 prompt 计费 |
| [REPORT-micu-fable-20260922](REPORT-micu-fable-20260922.md) | 米醋 enterprise | fable-5-1 测试 |
| [REPORT-sudocode-20260922](REPORT-sudocode-20260922.md) | sudocode | fable-5-1 = Claude Code 号池，疑为被模板压制的真 Fable |
| [REPORT-fluxion-20260923](REPORT-fluxion-20260923.md) | fluxion | 同一把 key 两个分组：Vertex 逆 / AWSB 逆，后者是模板池 + 老 Kiro 池 |
| [REPORT-fluxion-fable-20260923](REPORT-fluxion-fable-20260923.md) | fluxion | 真 Fable 5.1，但每请求隐藏注入约 5.6k token |
| [REPORT-hyhawang-20260924](REPORT-hyhawang-20260924.md) | hyhawang | 三池随机混；opus-5 = sonnet-5 同一老模型 |
| [REPORT-buliangren-20260925](REPORT-buliangren-20260925.md) | 不良人 | 三池；A 池中途消失后全落 3.7 Sonnet（含 ikuncode 对比节范例） |
| [REPORT-junliai-20260925](REPORT-junliai-20260925.md) | 君黎 | opus-5 = sonnet-5 = 3.7 Sonnet，稳但智力 14–15/27 |
| [REPORT-fluxion-o55-20260925](REPORT-fluxion-o55-20260925.md) | fluxion AWSQ | opus-5-5 假：Kiro 3.7 Sonnet 档 + 伪造 Opus 5.5 报错 |
| [REPORT-ahg-opus5-20260926](REPORT-ahg-opus5-20260926.md) | ahg.codes | opus-5 三池轮换、区分题 2/12、token 虚高 3 倍 |
| [REPORT-bitmiracle-o5-stability-20260926](REPORT-bitmiracle-o5-stability-20260926.md) | bitmiracle | opus-5 稳定性（对比 ikuncode opus-5-5） |
| [REPORT-cheaprouter-20260927](REPORT-cheaprouter-20260927.md) | cheaprouter | fable 级但模板压制、整站挂 2.5 h 照扣费；不推荐 |
| [REPORT-ooioo-fable-20260927](REPORT-ooioo-fable-20260927.md) | ooioo | fable-5-1 真 5.1 档但两池，其一丢 system/tools |
| [REPORT-rsiai-20260929](REPORT-rsiai-20260929.md) | rsiai | 0.05 倍；opus-5-5 2026 前沿档 12/12，与 ikuncode 同档便宜 10 倍；缓存假拆分 |

## GLM（glm-5.3-flash）

| 报告 | 站点 | 一句话 |
|---|---|---|
| [REPORT-glm](REPORT-glm.md) | 多站（自动矩阵） | 第一轮 GLM 横测 |
| [GREEDY-glm-20260910](GREEDY-glm-20260910.md) | 多站 | 贪心解码分歧 / 精度题 / 200k 十针：判断是否量化或换部署 |
| [OPS-glm-20260913](OPS-glm-20260913.md) | 多站 | 缓存 / 速度 / 稳定性同窗口交错采样 |
| [REPORT-yjapi-glm-20260913](REPORT-yjapi-glm-20260913.md) / [OPS](OPS-yjapi-glm-20260913.md) | yjapi | 断货后换成非 GLM 后端 |
| [FINAL-glm-20260915](FINAL-glm-20260915.md) | 多站 | GLM 商用渠道分析总表（官方基准 vs 中转） |
| [REPORT-teamo-glm-20260915](REPORT-teamo-glm-20260915.md) / [COMPARE](COMPARE-teamo-glm-20260915.md) / [GREEDY](GREEDY-teamo-glm-20260915.md) / [OPS](OPS-teamo-glm-20260915.md) | teamorouter | 真智谱后端但双池混合 |
| [REPORT-yuanqiao-glm-ds-20260916](REPORT-yuanqiao-glm-ds-20260916.md) | 远桥云 | GLM / DeepSeek 分组 |
| [COMPARE-glm-multi-20260921](COMPARE-glm-multi-20260921.md) | 多站 | 中转 vs 官方逐项对比（自动生成） |
| [COMPARE-runapi-glm-20260921](COMPARE-runapi-glm-20260921.md) | runapi | 隐式缓存属实，Anthropic 口丢 thinking |
| [REPORT-junliai-glm-20260925](REPORT-junliai-glm-20260925.md) | 君黎 | 真智谱，但缓存价/输出价配反、参数被改 |
| [REPORT-ooioo-glm-ds-20260927](REPORT-ooioo-glm-ds-20260927.md) | ooioo | glm-5.3-flash 是自建开源权重（非智谱）；ds 两个版本 |
| [REPORT-apigoto-glm-20260928](REPORT-apigoto-glm-20260928.md) | apigoto | 混合池约 74% 是 MiniMax-M3 |
| [REPORT-glm53flash-micu-vs-ikun-20261002](REPORT-glm53flash-micu-vs-ikun-20261002.md) | 米醋 vs ikuncode | glm-5.3-flash 对比基线 |

## DeepSeek

| 报告 | 站点 | 一句话 |
|---|---|---|
| [REPORT-teamo-deepseek-20260915](REPORT-teamo-deepseek-20260915.md) / [OPS flash](OPS-deepseek-flash-20260915.md) / [OPS v4](OPS-deepseek-v4-20260915.md) | teamorouter | deepseek-flash 官方透传；v4-flash / v4-pro 是方舟第三方池（老版 0731） |
| [OPS-yuanqiao-ds0731-20260916](OPS-yuanqiao-ds0731-20260916.md) | 远桥云 | 第三方托管真 0731 |
| [REPORT-dsv4flash-3way-20261002](REPORT-dsv4flash-3way-20261002.md) | ikuncode / sudocode / 米醋 | 三家对比，ikuncode 为基线 |

## GPT

| 报告 | 站点 | 一句话 |
|---|---|---|
| [REPORT-shuxin79-astra-20260916](REPORT-shuxin79-astra-20260916.md) | shuxin79 | gpt-6-astra low / high 同池同模型 |

GPT 的基线（spatialai）见 `suite/reference/spatialai-gpt.json` 和 BASELINES.md 3.8。

## 自动矩阵

[REPORT-auto-matrix-20260922](REPORT-auto-matrix-20260922.md)：`report.py` 对当时全部结果文件生成的总矩阵（智力分档、红旗、知识阶梯、IQ 分题、同站跨模型聚类）。
