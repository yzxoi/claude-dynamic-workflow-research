# 完整 prompt、模板与来源

## “完整 prompt”必须说明是哪一层

| 层级 | 本仓库保存的内容 | 不能据此声称的内容 |
|---|---|---|
| 静态本地指令 | 工具描述、authoring、worker 专用指令、动态源表达式 | 某次 HTTP 请求的全部 system stack |
| 本地 recorded snapshots | System chunks、tools、输入消息和 attachments | 完整 wire/cache/header 布局 |
| 官方 Managed Agents 模板 | 完整 agent.md 自定义 system、配置和 session 示例 | 云端隐藏 lead harness prompt |
| 本地生成 worker task | 每次 agent 调用的完整任务输入 | 云端具体 run 的 reader/prover system |
| 云端 inline worker system | 本次没有产生真实 run | 不能从模板猜写后充当实测 prompt |

## 本地 lead/worker 静态原文

- [完整 workflow-authoring](../evidence/prompts/workflow-authoring.txt)
- [强制模型变体](../evidence/prompts/workflow-authoring-model-forced.txt)
- [带 Skill 的组合工具描述](../evidence/prompts/workflow-tool-complete-with-skill-medium.txt)
- [无 Skill 的完整内联描述](../evidence/prompts/workflow-tool-complete-inline-medium.txt)
- [文本 worker 专用 system](../evidence/prompts/worker-text-system.txt)
- [结构化 worker 专用 system](../evidence/prompts/worker-structured-system.txt)
- [自定义文本 worker 后缀](../evidence/prompts/custom-worker-text-suffix.txt)
- [自定义结构化 worker 后缀](../evidence/prompts/custom-worker-structured-suffix.txt)
- [全部静态提取项索引](../evidence/PROMPTS.md)

一些静态条目仅是选择纯字符串函数后的 rendered 版本；另有动态插值表达式原文，不能把未实例化表达式当成运行中完整 prompt。

## 实验中的完整 prompt

受控实验的 [prompt 表](../evidence/live-probe/README.md) 直接链接 lead 与 A/B/C 的 system JSON、TXT、tools、incoming task 和 snapshots。

自主 bug-hunt 的 [完整实验报告](../evidence/bug-hunt-probe/EXPERIMENT.md) 内嵌 lead 任务、生成程序、四位 workers 的 prompt 和返回值；其 export 目录保留逐角色拆分版本及完整 tool IO。

未知项目的 [完整实验报告](../evidence/unknown-content-probe/EXPERIMENT.md) 内嵌初始任务和约束调整消息，链接 lead、三个 workers、首轮备份、完整 schema 和 transcript。第一轮与继续轮分别保留，避免把实验干预擦掉。

## 四份目标类型模板

| 模板 | 分发包提取版 | 公共 upstream 版 |
|---|---|---|
| Bug hunter | [提取](../evidence/prompts/cloud-template-bug-hunter-t77r14b6.md) | [原文](../evidence/official-skill/bug-hunter.md) |
| Watchlist scanner | [提取](../evidence/prompts/cloud-template-watchlist-scanner-kfkrzjrr.md) | [原文](../evidence/official-skill/watchlist-scanner.md) |
| Explainer video maker | [提取](../evidence/prompts/cloud-template-explainer-video-maker-sm29032a.md) | [原文](../evidence/official-skill/explainer-video-maker.md) |
| Performance tuner | [解压提取](../evidence/prompts/cloud-template-performance-tuner-6c866b59.md) | [原文](../evidence/official-skill/performance-tuner.md) |

这些模板与 `anthropics/skills` 固定 commit dbd4588f9e1033efb41dad4bef2f7947c8993d44 在精确替换模型变量后逐字相同。比较结果和 upstream URL 保存在 [comparison.json](../evidence/official-skill/comparison.json)。它们是正式 onboarding 资料，不是服务端私有 prompt 泄露。

模板中的 reader、reviewer、prover 等 prompt 由 lead 为具体工作在生成的程序中定义；模板本身主要给 lead 策略和约束。只恢复模板不能获得某次云端 worker 的完整输入。

## 模板调用位置

```text
初始化 bundled skills
  → 注册 claude-api skill
  → 动态读取文件表，解压资源并替换模型变量
  → managed-agents-onboard quickstart
  → 生成 agent.md / environment.yaml / session.yaml
  → ant apply 创建或更新 API resources
```

对应 [文件表](../evidence/formatted-js/chunk-p6hmrjkc.js)、[注册与选模板](../evidence/formatted-js/chunk-k9bc38yt.js)、[初始化取证](../evidence/template-call-sites.json)。

这条入口和本地 Workflow tool 入口不同。文件存在本机、ant 命令从本机运行，都不能证明 Managed Agents 编排在本机执行。Self-hosted sandbox 允许工具与文件在自有机器执行，也不等于编排器本地化。

## 云端接口能恢复到什么程度

模板直接出现 step.agent、define 和 step.now，要求 inline agent 定义 name/system；省略 model/tools，由 engine 继承或下发。完整函数签名、工具描述和程序校验器尚未取得。

SDK 0.133.0 可以核对 multiagent 类型、workflows/subagents/predefined/inline 配置、threads 和 events。它不包含私有 executor 源码。完整来源路径及字段定位见 [早期报告](../evidence/REPORT.md)。

## 重规划与拒绝机制

四模板有明确的任务内复核和条件返工；它们没有共同要求遇到任意意外就重新划分阶段和角色。默认 Quick watchlist 尤其不是不断追加 reviewer/redo。具体区别见 [重规划核对](05-replanning-and-result-delivery.md)。
