# 尝试、实验与原始记录

本页是全部尝试的导航。完整 prompt 和生成代码已在 evidence 中保存；阅读版报告与逐字段原始记录并存。

## 尝试清单

| 编号 | 尝试 | 成果与状态 |
|---|---|---|
| S1 | 查目标类型与公开 API | SDK 中定位 multiagent_20261001 与 workflows 配置 |
| S2 | Native 发布包取证 | 恢复 Bun 嵌入源和压缩资源，无 source map |
| S3 | REA slice/kernel 分析 | 获得完整 evidence；保留图容量和语义 unknown 限制 |
| S4 | 模板使用位置追踪 | 四模板属于 claude-api/onboarding；公共 upstream 对照吻合 |
| P1 | 原函数语义探针 | 五项通过；有明确 host stubs，无模型调用 |
| L1 | 受控交接 | 一位 lead、三位 workers，显式结果和文件 handoff 成功 |
| L2 | 植入缺陷、lead 自主拆解 | 四 workers，五个已知缺陷全部确认；出现额外 noop run |
| L3 | 未知真实项目、lead 自主拆解 | 三 workers，发现一个 CLI bug；lead 自行验证，无追加 worker |
| L3b | 同一 lead session 继续 | 撤销多余单 run 限制；保持 agent cap，无新增 workflow |
| C1 | Claude Code 认证 | 用户完成登录，随后能跑本地实验；未归档凭据 |
| C2 | Console/ant OAuth | 用户授权；模型读取成功 |
| C3 | 创建云端诊断 agent | 首个 create-agent 请求额度拒绝；未创建任何资源或启动 run |
| S5 | 重规划和结果交付核对 | 区分指南建议、模板策略、运行器与真实 lead 接收路径 |

认证过程的概要来自此次对话和后续请求状态，仓库不包含 OAuth code/token。精确认证 UI/终端全过程没有被记录为可重放 transcript。

## P1：原函数语义探针

[probe-semantics.cjs](../evidence/probe-semantics.cjs) 读取提取的原函数，在显式 host 边界 stubs 下执行；输出 [semantics-probe.json](../evidence/semantics-probe.json)。检查：

1. Pipeline 跨项无屏障，回调收到前项结果、原始输入与 index。
2. 返回 null/抛错的项目跳过后续阶段。
3. Parallel 等待全部 thunk、保序，子项失败变 null，Promise 输入被拒绝。
4. Journal key 前序链及 model 变更影响后续 key；label/phase 不影响。
5. 确定性 shim 拒绝实时钟和随机数，允许显式日期。

日志中的 intentional failure 是为验证失败语义主动制造的，并非实验失控。该探针不证明 CLI 接线、模型行为或云端执行。

## L1：受控 context/workspace handoff

任务明确预设 A/B 并行、C 汇总，用于分离数据传递和 context 继承：

```text
Lead-only nonce 保留在 lead 输入
写入 seed
  → A 读 seed、写 artifact、返回对象
  → B 读 seed、返回对象
等待 A/B
  → C 的 prompt 带 A/B 原返回对象，读取 artifact
  → 程序返回 A/B/C
```

实际 A/B 读取 workspace-shared-6295；C 读取 artifact-A-85192。三位 workers 输入都没有 lead-only nonce，输出 leadOnlyValue:null。

配置为 Claude Code 2.1.296、Sonnet 5.5、low effort、safe-mode/restricted、空 MCP，只开放 Workflow/Skill/Read/Write/Edit；CLI 美元上限 $1.50。没有 Bash、普通 Agent 或嵌套 worker 编排。

| 材料 | 入口 |
|---|---|
| 完整报告与逐角色 prompt 表 | [README](../evidence/live-probe/README.md) |
| 实际初始输入 | [task](../evidence/live-probe/task.txt) |
| 生成 workflow 原文 | [script](../evidence/live-probe/capture/session/workflows/scripts/context-probe-wf_a2116ab0-2a2.js) |
| 逐 agent started/result 通信 | [journal](../evidence/live-probe/capture/session/subagents/workflows/wf_a2116ab0-2a2/journal.jsonl) |
| 系统、tool schema 与 messages | [prompts](../evidence/live-probe/prompts/) |
| 本地 harness 原记录 | [capture](../evidence/live-probe/capture/) |
| 汇总用量与结果 | [summary](../evidence/live-probe/summary.json) |

累计 list-cost $0.1408173。普通 subagent_stats 的 0 不计这三位 workflow workers。这项正交实验可以证明受控 handoff，不能证明 lead 自发选择该拓扑。

## L2：小型植入缺陷 bug-hunt

实验者创建 inventory、pricing、scheduling、metrics 四模块，共约 91 行、五个已知缺陷。Ground truth 放在 worker workspace 外，任务没有给 lead 预先规定角色和阶段。总上限五 agents，包括 lead。

Lead 自行选择一轮 Audit，四个模块分别派一位 worker。每位 worker 可读源码、写自己的 scratch、用 Python 复现，然后以同一 schema 返回 confirmed/rejected/unverified。没有独立 verifier worker；lead 收齐后自行补查和汇总。

| 材料 | 入口 |
|---|---|
| 全文：输入、程序、各 worker prompt/return、lead 汇总 | [EXPERIMENT](../evidence/bug-hunt-probe/EXPERIMENT.md) |
| 任务输入 | [task](../evidence/bug-hunt-probe/task.txt) |
| 生成程序 | [workflow.js](../evidence/bug-hunt-probe/export/workflow.js) |
| 四 workers 逐角色导出 | [inventory](../evidence/bug-hunt-probe/export/inventory/)、[pricing](../evidence/bug-hunt-probe/export/pricing/)、[scheduling](../evidence/bug-hunt-probe/export/scheduling/)、[metrics](../evidence/bug-hunt-probe/export/metrics/) |
| 结构化 journal 与程序返回 | [journal](../evidence/bug-hunt-probe/export/journal.json)、[result](../evidence/bug-hunt-probe/export/workflow-result.json) |
| lead 完整输入/工具/队列 | [lead](../evidence/bug-hunt-probe/export/lead/) |
| 最终答复 | [lead-final](../evidence/bug-hunt-probe/export/lead-final.md) |
| 捕获、事件、调试日志 | [capture](../evidence/bug-hunt-probe/capture/)、[events](../evidence/bug-hunt-probe/events.jsonl)、[debug](../evidence/bug-hunt-probe/debug.log) |
| ground truth 与独立验证 | [truth](../evidence/bug-hunt-probe/ground-truth.json)、[baseline](../evidence/bug-hunt-probe/independent-baseline.json)、[proof reruns](../evidence/bug-hunt-probe/export/independent-proof-reruns.json) |
| 统计与限制审计 | [verification](../evidence/bug-hunt-probe/export/verification.json) |

Sonnet 5.5，medium effort，CLI $2 上限。主 run 19.202 秒、记录的 worker tokens 45,503、16 tool calls；完整 lead session 更长。四 worker 最初共提出六项 confirmed，其中一个额外浮点精度问题被 lead 降为 marginal，另有六项 rejected、一项 unverified。最终确认五个植入缺陷。

记录含两次 Workflow call：主 run 四 workers，意外 noop run 零 workers。五 agents 总上限满足，但实验者添加的“一次 Workflow”约束没有满足。没有失败重试、没有后序 agent handoff，源码前后 hash 相同。累计 list-cost $0.32556。

此实验展示自主拆分与验证，但规模很小、函数很短、已知缺陷人工植入，不能作为官方 116k 行/70 bugs 的复现或统计基准。

## L3：未知内容的真实项目

选取 [python-json-pointer](https://github.com/stefankoegl/python-json-pointer) 固定 commit f2641f09b20dfde10f068e492531f4d914427110，版本 3.2.1。原始源码、文档、测试和 RFC6901 参考一起放进实验 workspace，没有插入缺陷、提供缺陷数量或 correctness oracle。[provenance](../evidence/unknown-content-probe/provenance.json)

Lead 自行拆成 resolve-set、class-api、cli 三位 workers，使用一轮 Audit，保留第四个 worker 名额。实际共四 agents；未追加 worker。Worker 输入不含前序 worker 结果，也没有后序 worker 获取前序结果这一事件。

| 材料 | 入口 |
|---|---|
| 完整中文实验报告，含首轮与继续 | [EXPERIMENT](../evidence/unknown-content-probe/EXPERIMENT.md) |
| 原任务与修正消息 | [task](../evidence/unknown-content-probe/task.txt)、[continuation-task](../evidence/unknown-content-probe/continuation-task.txt) |
| 生成原程序 | [workflow.js](../evidence/unknown-content-probe/export/wf_b793799a-8e3/workflow.js) |
| worker 1 | [a2055a73c0ac276c7](../evidence/unknown-content-probe/export/wf_b793799a-8e3/a2055a73c0ac276c7/) |
| worker 2 | [a7467c40d37269c39](../evidence/unknown-content-probe/export/wf_b793799a-8e3/a7467c40d37269c39/) |
| worker 3 | [ac41b96f3fc87d5b9](../evidence/unknown-content-probe/export/wf_b793799a-8e3/ac41b96f3fc87d5b9/) |
| 最终程序返回与 journal | [result](../evidence/unknown-content-probe/export/wf_b793799a-8e3/result.json)、[journal](../evidence/unknown-content-probe/export/wf_b793799a-8e3/journal.json) |
| lead 的所有 prompt/tool IO/队列 | [lead](../evidence/unknown-content-probe/export/lead/) |
| 首轮不可变备份 | [first-turn-export](../evidence/unknown-content-probe/first-turn-export/)、[first-turn-capture](../evidence/unknown-content-probe/first-turn-capture/) |
| 原始事件与继续事件 | [events](../evidence/unknown-content-probe/events.jsonl)、[continuation-events](../evidence/unknown-content-probe/continuation-events.jsonl) |
| lead 最終汇总 | [lead-final](../evidence/unknown-content-probe/export/lead-final.md) |
| 观察与独立验证 | [observations](../evidence/unknown-content-probe/export/observations.json)、[independent-verification](../evidence/unknown-content-probe/export/independent-verification.json) |
| 上游与 scratch/验证产物 | [workspace](../evidence/unknown-content-probe/workspace/) |

Sonnet 5.5，high effort，CLI $3 上限。Workflow 71.371 秒、记录 worker tokens 98,700、21 tool calls。Workers 共返回一项 bug、九项 ambiguity、十三项 rejected。

CLI 问题是：对数组末端 /a/- 得到 EndOfList sentinel，json.dumps 引发 TypeError。代码虽然在 try 中，但 except 只接 JsonPointerException，导致 CLI 提前退出，后续输入文件未处理，违反文档中错误后继续处理的行为。研究者用“后一个文件单独运行成功、放在失败文件后被跳过”的独立探针增强了证据。

Lead 读到完整程序结果后自行复现，并在同一 session 的继续轮补查 pointer-file 等路径，决定不再派 worker。累计 list-cost $0.878151，包含继续轮。52 项上游测试由研究者随后用正确模块路径跑通，结果没有发送给 lead。

这里有一次必须保留的干预：runner 初始添加了“一次 Workflow、不得 resume”的多余限制；首轮后撤销该限制，保持五 agents 总上限，不指定角色、阶段或追加任务。仍没有新 workflow/worker，说明这个样本中 lead 自行验证已满足其判断；不能因此断言默认机制绝不会重派。

共享文件有直接观察：class-api 列出了 scratch/cli 和 scratch/lead。没有观察到它读取 peer 文件正文。**共享 cwd 证据不等于这轮已经实现跨 worker 的成果交接。**正向成果 handoff 由 L1 单独验证。

## C3：没有启动的云端尝试

准备了最多三位 inline workers、两分钟 lifetime、关闭普通 subagents/advisor、限制工具与网络的诊断。Session 预算拟设 amount:"150"，USD 最小单位，即 $1.50；这是准备值，没有创建成功也没有费用发生。

[run-probe.py](../evidence/cloud-probe/run-probe.py) 第一个 create-agent 请求返回 [agent-created.json](../evidence/cloud-probe/agent-created.json)：Your credit balance is too low to access the Anthropic API。脚本立即退出，environment/session/run 没有产生。

保留 [拟用 lead system](../evidence/cloud-probe/lead-system.txt)、[拟用 task](../evidence/cloud-probe/task.txt)、[读取的 models](../evidence/cloud-probe/models.json)、[ant help](../evidence/ant-agent-create-help.txt)、[GET-only collector](../evidence/capture-cloud-readonly.py)。它们不是实际云端 lead/worker 输入与通信记录。
