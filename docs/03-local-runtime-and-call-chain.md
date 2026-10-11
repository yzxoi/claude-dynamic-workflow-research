# 本地调用链与实现细节

本页的接口与实现针对官方 Claude Code 2.1.296 的本地路径，不冒充 `multiagent_20261001` 私有 DSL。

## 可达链路

```text
Lead 模型生成 Workflow tool call
  → workflow-tool：选择 inline script / scriptPath / saved workflow
  → 验证 meta，编译程序，创建后台任务
  → workflow-runtime：建立执行环境与 globals
  → 执行脚本；agent() 创建 worker 请求并经过队列
  → worker configuration / subagent runner
  → 工具调用、最终文本或 StructuredOutput
  → 返回脚本调用方，记录 journal
  → 脚本最终 return
  → 后台 task 完成，向 lead 投递完成通知
```

入口源码：[workflow-tool.js](../evidence/formatted-js/workflow-tool.js)、[workflow-runtime.js](../evidence/formatted-js/workflow-runtime.js)、[subagent-runner.js](../evidence/formatted-js/subagent-runner.js)。早期报告保存了行号和符号定位；格式化文件仅便于阅读，原 minified JS 另在 bun-files 和 extracted-js 中保留。

## Workflow 输入与程序

输入包含 script、scriptPath、name、args 和 resumeFromRunId。Script 是 plain JavaScript，body 在 async 环境执行；meta 是纯字面量，包含名称和描述，可附阶段信息。名称、阶段的元数据本身不执行派发。

本地编排运行环境提供下列接口：

| 接口 | 含义 |
|---|---|
| agent(prompt, opts) | 启动 worker；返回最终字符串，或经过 schema 校验的对象 |
| parallel(thunks) | 并行启动函数，等待它们全部完成，按输入顺序收集 |
| pipeline(items, stages...) | 每项独立依次进入阶段；跨工作项没有阶段屏障 |
| phase(title) | 进度分组；不建立等待关系 |
| log(message) | 显示进度消息 |
| args | 传入程序的数据 |
| workflow(...) | 本地一层嵌套 workflow，共享本轮限制 |
| budget | 指南描述的 token target 接口；实际接线另见下文 |

Opts 可提供 label、phase、schema、model、effort、isolation、agentType。AgentType 指向本地 agent registry；这是本地自定义 agent 入口，不等于云端 define system prompt。

Parallel 接受函数数组，不能直接传 Promise 数组。已进入聚合的子任务失败可成为 null；输入验证和 cap 错误仍可能抛出。Pipeline 的某项返回 null 或抛错，会跳过该项后续步骤。这些细节通过五项 [原函数探针](../evidence/semantics-probe.json) 核对过。

## Worker context 和结果

该路径没有把完整 forkContextMessages 传给 runner。Worker 从自己的 history 开始，再加载任务、适用项目 context 和环境。另有受来源规则约束的 user-request relay，不可把实验中无 nonce 泛化成从不传任何用户请求。

默认 workflow worker 禁用 SendUserMessage、Agent 和 Workflow，主要把结果交回程序。自定义 agent 的 denies 与这些约束合并。

无 schema 时，最终文本逐字成为返回字符串。有 schema 时，运行器增加 StructuredOutput 工具，校验输入形状并消费 structured_output attachment。缺字段或格式不符可提示修正；这不是事实审计，也不是重新拆任务。

## 队列、工作区与确定性

2.1.296 的默认并发公式是 min(16, max(2, availableCPUs - 2))，可受环境覆盖；多余调用排队。累计 agent cap 为 1,000，聚合数组 cap 为 4,096。它们是本地版本实现，不用于推导云端限流。

默认共同 cwd；worktree 可隔离 Git 修改。Remote isolation 在本包明确不可用。同步 VM 保护时间为 30 秒，不是整个异步 run 的 lifetime。

使用 node:vm，限制动态 string code generation 与 Wasm，不向脚本提供普通 Node/文件系统 API。文件操作由 worker 工具执行。实时时钟和随机数被禁止；显式日期可用。Cloud 模板中出现 step.now()，说明不能照搬本地表面接口。

## Journal 与恢复

Journal 保存 launched、started、result、failed；另保存脚本和 worker transcript。恢复通过此前调用的缓存结果重放未改变的调用序列前缀；第一项变化和后续工作重新执行。

缓存 key 的组成是 previousKey、prompt 和稳定排序的 options。Schema、model、effort、isolation、agentType 等参与；label/phase 不参与。源码与探针验证了 key 行为，但没有完整实测“编辑 workflow 后通过 CLI 恢复”。未知项目实验恢复的是 lead session，并非编辑后重放同一 workflow。

缓存不是外部文件系统的快照。相同 prompt/opts 下源文件变化不会自动让缓存失效；这属于源码推导的限制。

## 两处需要保留的实现差异

**Budget 接线：**指南把用户 token target 描述为硬 ceiling，kernel 也有有限预算检查。但本包 launch 的可达路径传入 total:null，因此这条路径的 remaining 为 Infinity。本次没有运行 token-target 集成实验。CLI 美元预算与该 token target 不能混为一谈。

**Fact-rule 代码：**tool 文件中有 put/read/on/retract 等另一套运行器代码，但通常入口没有启用它，launch 走本地 v1 路径。Journal key 的 v2 前缀只是缓存格式版本，不证明切换了执行器。不能把发布包中的未启用代码认作云端实现。

## 完成通知

[通知生成器](../evidence/formatted-js/205220505.js) 接收脚本最终 return、失败列表、用量、输出文件和逐 agent 日志路径，然后进入 lead 的 task-notification 队列。2.1.296 对通知结果使用约 8,000 字符上限，完整值在 output 文件；各 worker 完整 return 在 journal。

进度更新走 UI/task registry/SDK 展示链，不等于逐个给 lead 注入完整 worker 回答。默认完成通知也不自动把脚本丢弃的结果补回。

## 内置研究 workflow

[deep-research-0.js](../evidence/builtins/deep-research-0.js) 是随包发布的完整工作流，包括 scope、搜索、去重、获取提取、claim 验证和综合。它展示了范围发现、按结果展开后续工作及多票验证怎样组合。没有执行它作为本次真实研究任务；不能把其理论 agent 数量或质量模式列为实测效果。
