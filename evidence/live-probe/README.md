# 本地 Workflow 实测：上下文、workspace 与返回值

2026-10-11，运行官方 Claude Code 2.1.296 的独立下载副本，使用 claude.ai Pro 登录。已安装的 2.1.123 保持不变。模型为 claude-sonnet-5-5、effort=low。只执行一个 local Workflow、三个 worker，未执行 Managed Agents run。

CLI 使用 safe-mode、restricted、空 MCP 配置、仅 Workflow/Skill/Read/Write/Edit 工具、1.50 美元 CLI 预算上限和 system prompt snapshots。任务目录与 session 都是本实验新建。safe-mode 排除项目 CLAUDE.md、用户插件与 MCP 等影响；结论适用于这个受限环境，不证明所有默认配置相同。

## 结果

| 观测 | 证据 |
|---|---|
| A/B 独立对话，读取同一 seed | 两个独立 transcript；各自只收到 computed task；均返回 workspace-shared-6295 |
| A/B 并行，C 在两者完成后启动 | journal 为 started A → started B → result A → result B → started C |
| 默认共享 workspace | A 的 Write 建立 artifact-a.txt；C 的 Read 返回 artifact-A-85192 |
| 显式传递数据 | 脚本将 A/B 对象 JSON.stringify 后编入 C 的 prompt；C 的 StructuredOutput 原样返回这两个对象 |
| 不自动继承完整 lead 对话 | 只在 lead 任务出现的 nonce 没有进入任何 worker incoming task；三个 worker 的 leadOnlyValue 均为 null |
| 结构化返回经过工具协议 | worker 最后调用 StructuredOutput，其 schema 在各自 tools.json 中；journal 保存相同对象 |
| worker 不负责继续编排 | 实际工具为 Edit、Read、Skill、Write、StructuredOutput；没有 Workflow/Agent |

上下文结论同时由源码支持：本地 worker spawn 未传 forkContextMessages。源码另有 trusted-human 请求 relay；本次 print-mode worker 没有该 relay。因此“完整 lead history 不被复制”与“某些路径会传真实用户请求片段”可以同时成立。nonce 探针不是对所有 interactive 模式的保证。

本次 CLI 报告的累计模型 list-cost 为 **$0.1408173**，不是 Pro 订阅实际扣款证明。累计 modelUsage：input=20、output=2,278、cache creation input=34,005、cache read input=61,618。普通 subagent_stats.spawned 为 0，但 workflow journal 实际有三个 worker，不能用普通 Agent 统计代替 Workflow 数量。

## 完整记录

- [输入任务](task.txt)
- [原始生成脚本](capture/session/workflows/scripts/context-probe-wf_a2116ab0-2a2.js)
- [journal](capture/session/subagents/workflows/wf_a2116ab0-2a2/journal.jsonl)
- [解析后的结果与用量](summary.json)
- [每文件 SHA-256 与来源](prompt-manifest.json)

| 角色 | system 原始 chunks / 阅读版 | tools schema | incoming task | 完整任务消息 |
|---|---|---|---|---|
| Lead | [JSON](prompts/lead-system.json) / [TXT](prompts/lead-system.txt) | [JSON](prompts/lead-tools.json) | [TXT](prompts/lead-incoming-task.txt) | [JSON](prompts/lead-messages.json) |
| A | [JSON](prompts/worker-A-system.json) / [TXT](prompts/worker-A-system.txt) | [JSON](prompts/worker-A-tools.json) | [TXT](prompts/worker-A-incoming-task.txt) | [JSON](prompts/worker-A-messages.json) |
| B | [JSON](prompts/worker-B-system.json) / [TXT](prompts/worker-B-system.txt) | [JSON](prompts/worker-B-tools.json) | [TXT](prompts/worker-B-incoming-task.txt) | [JSON](prompts/worker-B-messages.json) |
| C | [JSON](prompts/worker-C-system.json) / [TXT](prompts/worker-C-system.txt) | [JSON](prompts/worker-C-tools.json) | [TXT](prompts/worker-C-incoming-task.txt) | [JSON](prompts/worker-C-messages.json) |

每角色还提供 `<role>-snapshot.json`，含 cliPrefix、system chunk 数组、tools 与渲染标记。worker system 是四个 chunks；第一个 639 bytes 来自 StructuredOutput 专用 system，随后是通用 agent 通信/权限、环境提示及 token 状态。系统文本提到 agent message 不是用户批准，这是权限来源规则，不表示 workflow script 暴露 peer-message API。

snapshot 记录 base system 和工具定义；动态 attachment 渲染、请求头、cache block 布局未抓取为完整 HTTP 请求。capture 目录是这次新建 session 的原始记录，包含本机路径和账号组织元数据，适合在本机复核。导出的 messages.json 不携带无关 attachment；没有读取认证存储或复制其他聊天。
