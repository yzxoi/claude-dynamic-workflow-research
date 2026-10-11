# 提示词与脚本原文索引

静态文件来自 Claude Code 2.1.296 官方分发包。不是 Managed Agents 私有系统提示词的副本。rendered 静态文件仅运行了 extract-prompts.cjs 明确选择的纯字符串函数；另附一次真实本地 Workflow 运行的 prompt snapshots、工具定义和任务消息。组合工具描述包含 size guideline 默认变体。模板表达式保留动态插值，不能当作某次真实模型请求的完整 system。SHA-256 与来源见 [prompt-manifest.json](prompt-manifest.json)。

## 优先阅读

| 内容 | 原文 |
|---|---|
| 云端 multiagent_20261001 的 Bug hunter 完整配置及任务 system | [Bug hunter](prompts/cloud-template-bug-hunter-t77r14b6.md) |
| Lead 的组合 Workflow 工具描述（有 Skill） | [small](prompts/workflow-tool-complete-with-skill-small.txt)、[medium](prompts/workflow-tool-complete-with-skill-medium.txt) |
| Lead 的完整内联工具描述（无 Skill） | [small](prompts/workflow-tool-complete-inline-small.txt)、[medium](prompts/workflow-tool-complete-inline-medium.txt) |
| 完整 workflow-authoring | [常规](prompts/workflow-authoring.txt)、[强制模型](prompts/workflow-authoring-model-forced.txt) |
| Worker 专用指令，仍需通用 base system / 环境组合 | [文本](prompts/worker-text-system.txt)、[结构化](prompts/worker-structured-system.txt) |
| 自定义 Worker 后缀 | [文本](prompts/custom-worker-text-suffix.txt)、[结构化](prompts/custom-worker-structured-suffix.txt) |
| 所有角色 prompt、schemas 与控制流 | [本地内置 deep-research](builtins/deep-research-0.js) |
| 本次本地实测的 recorded system、工具与 incoming task | [实测记录](live-probe/README.md)、[lead system](live-probe/prompts/lead-system.txt)、[Worker A system](live-probe/prompts/worker-A-system.txt)、[完整工具定义](live-probe/prompts/worker-A-tools.json) |
| 第四份目标类型模板（zstd 解压恢复） | [Performance tuner](prompts/cloud-template-performance-tuner-6c866b59.md) |
| 其他云端目标类型模板 | [Watchlist scanner](prompts/cloud-template-watchlist-scanner-kfkrzjrr.md)、[Explainer video maker](prompts/cloud-template-explainer-video-maker-sm29032a.md) |

## 全部已提取项

共 47 项、267,289 bytes。补充模板字符串包含通用、Ultracode 和其他动态 prompt 片段，不是 47 个独立 agent。

| 文件 | 表示 | 字节 | 来源 |
|---|---|---:|---|
| [prompts/workflow-tool-with-skill.txt](prompts/workflow-tool-with-skill.txt) | rendered-pure-prompt-function | 3225 | `bun-files/chunk-62rej6c1.js` |
| [prompts/workflow-tool-inline-reference.txt](prompts/workflow-tool-inline-reference.txt) | rendered-pure-prompt-function | 20174 | `bun-files/chunk-62rej6c1.js` |
| [prompts/workflow-authoring.txt](prompts/workflow-authoring.txt) | rendered-pure-prompt-function | 17141 | `bun-files/chunk-62rej6c1.js` |
| [prompts/size-guideline-small-configured.txt](prompts/size-guideline-small-configured.txt) | rendered-pure-size-guideline-function | 204 | `bun-files/chunk-c5zwk83v.js` |
| [prompts/size-guideline-small-default.txt](prompts/size-guideline-small-default.txt) | rendered-pure-size-guideline-function | 273 | `bun-files/chunk-c5zwk83v.js` |
| [prompts/workflow-tool-complete-inline-small.txt](prompts/workflow-tool-complete-inline-small.txt) | rendered-composite-tool-prompt-variant | 20449 | `bun-files/chunk-62rej6c1.js + chunk-c5zwk83v.js + NQr from chunk-04v7vxqn.js` |
| [prompts/workflow-tool-complete-with-skill-small.txt](prompts/workflow-tool-complete-with-skill-small.txt) | rendered-composite-tool-prompt-variant | 3500 | `bun-files/chunk-62rej6c1.js + chunk-c5zwk83v.js + NQr from chunk-04v7vxqn.js` |
| [prompts/size-guideline-medium-configured.txt](prompts/size-guideline-medium-configured.txt) | rendered-pure-size-guideline-function | 206 | `bun-files/chunk-c5zwk83v.js` |
| [prompts/size-guideline-medium-default.txt](prompts/size-guideline-medium-default.txt) | rendered-pure-size-guideline-function | 275 | `bun-files/chunk-c5zwk83v.js` |
| [prompts/workflow-tool-complete-inline-medium.txt](prompts/workflow-tool-complete-inline-medium.txt) | rendered-composite-tool-prompt-variant | 20451 | `bun-files/chunk-62rej6c1.js + chunk-c5zwk83v.js + NQr from chunk-04v7vxqn.js` |
| [prompts/workflow-tool-complete-with-skill-medium.txt](prompts/workflow-tool-complete-with-skill-medium.txt) | rendered-composite-tool-prompt-variant | 3502 | `bun-files/chunk-62rej6c1.js + chunk-c5zwk83v.js + NQr from chunk-04v7vxqn.js` |
| [prompts/size-guideline-large-configured.txt](prompts/size-guideline-large-configured.txt) | rendered-pure-size-guideline-function | 205 | `bun-files/chunk-c5zwk83v.js` |
| [prompts/size-guideline-large-default.txt](prompts/size-guideline-large-default.txt) | rendered-pure-size-guideline-function | 274 | `bun-files/chunk-c5zwk83v.js` |
| [prompts/workflow-authoring-model-forced.txt](prompts/workflow-authoring-model-forced.txt) | rendered-pure-prompt-function | 16776 | `bun-files/chunk-62rej6c1.js` |
| [prompts/worker-text-system.txt](prompts/worker-text-system.txt) | rendered-literal | 594 | `bun-files/chunk-hedqf2m1.js:45` |
| [prompts/custom-worker-text-suffix.txt](prompts/custom-worker-text-suffix.txt) | rendered-literal | 307 | `bun-files/chunk-hedqf2m1.js:51` |
| [prompts/custom-worker-structured-suffix.txt](prompts/custom-worker-structured-suffix.txt) | rendered-literal | 409 | `bun-files/chunk-hedqf2m1.js:55` |
| [prompts/worker-structured-system.txt](prompts/worker-structured-system.txt) | rendered-literal | 639 | `bun-files/chunk-hedqf2m1.js:59` |
| [prompts/provenance-computed-task.txt](prompts/provenance-computed-task.txt) | literal-concatenation | 422 | `bun-files/chunk-6f3cp7aa.js` |
| [prompts/provenance-user-request.txt](prompts/provenance-user-request.txt) | literal-concatenation | 369 | `bun-files/chunk-6f3cp7aa.js` |
| [prompts/provenance-assistant-context.txt](prompts/provenance-assistant-context.txt) | literal-concatenation | 206 | `bun-files/chunk-6f3cp7aa.js` |
| [prompts/provenance-automated-trigger.txt](prompts/provenance-automated-trigger.txt) | literal-concatenation | 255 | `bun-files/chunk-6f3cp7aa.js` |
| [builtins/deep-research-0.js](builtins/deep-research-0.js) | rendered-bundled-workflow | 24693 | `bun-files/chunk-qajs04tk.js` |
| [prompts/template-chunk-sfn1dbxq-1011699-1.js.txt](prompts/template-chunk-sfn1dbxq-1011699-1.js.txt) | exact-source-expression-unrendered | 44052 | `bun-files/chunk-sfn1dbxq.js:utf16:1011699-1055751` |
| [prompts/template-chunk-sfn1dbxq-1081817-2.js.txt](prompts/template-chunk-sfn1dbxq-1081817-2.js.txt) | exact-source-expression-unrendered | 308 | `bun-files/chunk-sfn1dbxq.js:utf16:1081817-1082125` |
| [prompts/template-chunk-sfn1dbxq-1139787-3.js.txt](prompts/template-chunk-sfn1dbxq-1139787-3.js.txt) | exact-source-expression-unrendered | 21889 | `bun-files/chunk-sfn1dbxq.js:utf16:1139787-1161676` |
| [prompts/template-chunk-sfn1dbxq-Cpo-4.js.txt](prompts/template-chunk-sfn1dbxq-Cpo-4.js.txt) | exact-source-expression-unrendered | 1786 | `bun-files/chunk-sfn1dbxq.js:utf16:1172200-1173986` |
| [prompts/template-chunk-sfn1dbxq-jpo-5.js.txt](prompts/template-chunk-sfn1dbxq-jpo-5.js.txt) | exact-source-expression-unrendered | 10775 | `bun-files/chunk-sfn1dbxq.js:utf16:1190071-1200846` |
| [prompts/template-chunk-sfn1dbxq-m5t-6.js.txt](prompts/template-chunk-sfn1dbxq-m5t-6.js.txt) | exact-source-expression-unrendered | 1448 | `bun-files/chunk-sfn1dbxq.js:utf16:2032076-2033524` |
| [prompts/template-chunk-sfn1dbxq-b5t-7.js.txt](prompts/template-chunk-sfn1dbxq-b5t-7.js.txt) | exact-source-expression-unrendered | 5194 | `bun-files/chunk-sfn1dbxq.js:utf16:2036535-2041729` |
| [prompts/template-chunk-sfn1dbxq-2054251-8.js.txt](prompts/template-chunk-sfn1dbxq-2054251-8.js.txt) | exact-source-expression-unrendered | 7861 | `bun-files/chunk-sfn1dbxq.js:utf16:2054251-2062112` |
| [prompts/template-chunk-sfn1dbxq-4052588-9.js.txt](prompts/template-chunk-sfn1dbxq-4052588-9.js.txt) | exact-source-expression-unrendered | 314 | `bun-files/chunk-sfn1dbxq.js:utf16:4052588-4052902` |
| [prompts/template-chunk-sfn1dbxq-Mzr-10.js.txt](prompts/template-chunk-sfn1dbxq-Mzr-10.js.txt) | exact-source-expression-unrendered | 1275 | `bun-files/chunk-sfn1dbxq.js:utf16:4353783-4355058` |
| [prompts/template-chunk-sfn1dbxq-M-11.js.txt](prompts/template-chunk-sfn1dbxq-M-11.js.txt) | exact-source-expression-unrendered | 327 | `bun-files/chunk-sfn1dbxq.js:utf16:4448715-4449042` |
| [prompts/template-chunk-sfn1dbxq-4449136-12.js.txt](prompts/template-chunk-sfn1dbxq-4449136-12.js.txt) | exact-source-expression-unrendered | 1953 | `bun-files/chunk-sfn1dbxq.js:utf16:4449136-4451089` |
| [prompts/template-chunk-sfn1dbxq-w-13.js.txt](prompts/template-chunk-sfn1dbxq-w-13.js.txt) | exact-source-expression-unrendered | 711 | `bun-files/chunk-sfn1dbxq.js:utf16:4452274-4452985` |
| [prompts/template-chunk-sfn1dbxq-4468903-14.js.txt](prompts/template-chunk-sfn1dbxq-4468903-14.js.txt) | exact-source-expression-unrendered | 315 | `bun-files/chunk-sfn1dbxq.js:utf16:4468903-4469218` |
| [prompts/template-chunk-hedqf2m1-25746-1.js.txt](prompts/template-chunk-hedqf2m1-25746-1.js.txt) | exact-source-expression-unrendered | 220 | `bun-files/chunk-hedqf2m1.js:utf16:25746-25966` |
| [prompts/template-chunk-hedqf2m1-ks-2.js.txt](prompts/template-chunk-hedqf2m1-ks-2.js.txt) | exact-source-expression-unrendered | 602 | `bun-files/chunk-hedqf2m1.js:utf16:38181-38783` |
| [prompts/template-chunk-hedqf2m1-ys-3.js.txt](prompts/template-chunk-hedqf2m1-ys-3.js.txt) | exact-source-expression-unrendered | 315 | `bun-files/chunk-hedqf2m1.js:utf16:38787-39102` |
| [prompts/template-chunk-hedqf2m1-bs-4.js.txt](prompts/template-chunk-hedqf2m1-bs-4.js.txt) | exact-source-expression-unrendered | 381 | `bun-files/chunk-hedqf2m1.js:utf16:39106-39487` |
| [prompts/template-chunk-hedqf2m1-Ss-5.js.txt](prompts/template-chunk-hedqf2m1-Ss-5.js.txt) | exact-source-expression-unrendered | 586 | `bun-files/chunk-hedqf2m1.js:utf16:39491-40077` |
| [prompts/cloud-template-bug-hunter-t77r14b6.md](prompts/cloud-template-bug-hunter-t77r14b6.md) | shipped-console-agent-template-not-server-internal-prompt | 8092 | `bun-files/bug-hunter-t77r14b6.md` |
| [prompts/cloud-template-deep-researcher-kr59y5yh.md](prompts/cloud-template-deep-researcher-kr59y5yh.md) | shipped-console-agent-template-not-server-internal-prompt | 2426 | `bun-files/deep-researcher-kr59y5yh.md` |
| [prompts/cloud-template-watchlist-scanner-kfkrzjrr.md](prompts/cloud-template-watchlist-scanner-kfkrzjrr.md) | shipped-console-agent-template-not-server-internal-prompt | 5638 | `bun-files/watchlist-scanner-kfkrzjrr.md` |
| [prompts/cloud-template-explainer-video-maker-sm29032a.md](prompts/cloud-template-explainer-video-maker-sm29032a.md) | shipped-console-agent-template-not-server-internal-prompt | 4882 | `bun-files/explainer-video-maker-sm29032a.md` |
| [prompts/cloud-template-performance-tuner-6c866b59.md](prompts/cloud-template-performance-tuner-6c866b59.md) | shipped-console-agent-template-not-server-internal-prompt | 11390 | `bun-files/performance-tuner-6c866b59.md.zst decoded with zstd; see decoded-assets-manifest.json` |

本地实测另导出 24 个文件、184,686 bytes，哈希与来源见 [实测 prompt manifest](live-probe/prompt-manifest.json)。JSON system 数组保留 chunk 边界，TXT 是供阅读的拼接；snapshot 含 cliPrefix 与 rendering 标记。完整原始 transcript 另保存在 capture 中。这些是本地 harness 记录，不等同云端 harness 或完整 HTTP wire 请求。
