# ikuncode cc逆向 注入与缓存探针（injcache.py，2026-10-07）

三个模型：claude-sonnet-5-5 / claude-opus-5-5 / claude-sonnet-5。冻结数据见 `suite/reference/ikuncode-ccrev-injcache.json`，判读见 `docs/BASELINES.md` 3.5.1。

| 模型 | OK 计费 input（发 5） | 注入≈ | 2k system 计费/发送 | 不带 cache_control | 新前缀首次 read | 命中档位 | read=write | 多轮 read | TTL 后 | TTFT 未命中→命中（50k） | 账单一致 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| claude-sonnet-5-5 | [69, 74, 74] | 64 | 2130/2019 | {'12k': [0, 0], '25k': [0, 0]} | [0, 0, 0, 0, 0] | 3k,5k,12k,25k,50k | 否 | [0, 12549, 12549, 12549] | C-ttl360s: r0/w14764 | [12.5, 10.0, 9.19] | 32/32 条账单与 usage 一致（共 32 次调用） |
| claude-opus-5-5 | [77, 77, 77] | 72 | 2551/2022 | {'12k': [0, 0], '25k': [0, 0]} | [0, 0, 0, 0, 0] | 3k,5k,12k,25k,50k | 否 | [0, 14496, 14496, 14496] | C-ttl360s: r0/w12501 | [8.14, 8.34, 18.39] | 34/34 条账单与 usage 一致（共 34 次调用） |
| claude-sonnet-5 | [77, 77, 77] | 72 | 2824/2018 | {'12k': [0, 0], '25k': [0, 0]} | [0, 0, 0, 0, 0] | 3k,5k,12k,25k,50k | 否 | [0, 15599, 16245, 15685] | C-ttl360s: r0/w12499 | [5.01, 15.16, 8.74] | 34/34 条账单与 usage 一致（共 34 次调用） |

| 模型 | 档位 | write | 后续 read | 每次总 token（in+read+write） |
|---|---|---|---|---|
| claude-sonnet-5-5 | 3k | 3303 | [3303] | [3382, 3382] |
| claude-sonnet-5-5 | 5k | 6414 | [6700] | [6493, 6782] |
| claude-sonnet-5-5 | 12k | 15567 | [15306, 15306] | [15648, 15386, 15386] |
| claude-sonnet-5-5 | 25k | 28145 | [28145, 29989] | [28225, 28225, 30074] |
| claude-sonnet-5-5 | 50k | 63438 | [63438, 63438] | [63523, 63523, 63523] |
| claude-opus-5-5 | 3k | 3148 | [3286] | [3223, 3364] |
| claude-opus-5-5 | 5k | 5707 | [5707] | [5785, 5785] |
| claude-opus-5-5 | 12k | 13584 | [13534, 13534] | [13665, 13615, 13615] |
| claude-opus-5-5 | 25k | 28589 | [28589, 29216] | [28670, 28670, 29298] |
| claude-opus-5-5 | 50k | 65172 | [65172, 65172] | [65254, 65254, 65254] |
| claude-sonnet-5 | 3k | 3977 | [3977] | [4059, 4059] |
| claude-sonnet-5 | 5k | 6686 | [6686] | [6768, 6768] |
| claude-sonnet-5 | 12k | 15873 | [15873, 15873] | [15956, 15956, 15956] |
| claude-sonnet-5 | 25k | 28562 | [27902, 27800] | [28645, 27983, 27881] |
| claude-sonnet-5 | 50k | 64860 | [64860, 64860] | [64941, 64941, 64941] |

**claude-sonnet-5-5 自述**（节选）
- who：I'm Kiro, an AI-powered development environment that helps you design, write, and debug code. / Kiro is made by AWS. I don't have details on which underlying model powers me. / I'm running inside Kiro itself, connected throu
- above：I can't discuss that.
- tools：I can't discuss that.
- date：Today's date: I don't have it in my context, but I can check the system clock if you'd like. / Knowledge cutoff: I don't have a confirmed cutoff date for the model I'm running on.
- rules：I can't discuss that. I won't claim I have no instructions, but I can't describe or summarize them. /  / If you have a question about a specific date, event, or something time-sensitive, ask it directly and I'll do my best t
- above-sys：I can't discuss that.

**claude-opus-5-5 自述**（节选）
- who：I'm Kiro, an AI assistant for software development and related work. / Kiro is built by Amazon Web Services (AWS). / I'm running inside the Kiro development environment, connected here through an ACP client.
- above：I can't discuss that. /  / If there's something you're working on, a project, a bug, or a question about how I can help, I'm glad to dig in.
- tools：I can't discuss that.
- date：Today's date: I don't have access to it, since my context doesn't include the current date or a clock. / Knowledge cutoff: My training data runs to roughly early 2025, but I can't confirm the exact date, so treat anything 
- rules：I can't discuss the specifics of my instructions, but I can be honest about the shape of things: /  / - I do have a system prompt with instructions that guide how I behave. / - One of those instructions asks me not to share or
- above-sys：I can't discuss that.

**claude-sonnet-5 自述**（节选）
- who：I'm Kiro, an AI-powered development environment. /  / I'm made by AWS (Amazon Web Services). /  / I'm running inside Kiro right now.
- above：I can't share that. My system prompt and instructions aren't something I can quote verbatim or output in full. /  / I'm Kiro — I can help with coding tasks, debugging, planning, infrastructure work, and more. What would you 
- tools：I can't discuss that.
- date：I don't have access to today's actual date in this conversation (no system clock or search was provided), so I can't state it reliably — if you tell me, I'll use it. My knowledge cutoff is early 2025.
- rules：Here's what applies, honestly summarized: /  / - System prompt: I can't discuss its contents, structure, or hidden instructions. If asked directly about it, I say "I can't discuss that" rather than describing or paraphrasing
- above-sys：I can't discuss that.
