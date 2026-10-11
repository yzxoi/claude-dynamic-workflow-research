# 证据局限与待验证问题

## 已验证范围

本调查取得本地公开分发包、完整嵌入源、解压模板、selected prompt snapshots、三个本地 model runs 和原函数探针。恢复内容足以解释本地 Workflow 的调用链、独立 context、共同 cwd、程序返回、完成通知和默认可达接口。

没有取得服务端私有源码，未实际运行 Managed Agents dynamic workflow。官方模板和 SDK 的同名概念不能证明云端 scheduler/harness 与本地代码共用。

## 不应作出的结论

| 不能声称 | 缺失证据 |
|---|---|
| 拿到 multiagent_20261001 全部隐藏 prompt | 只有公开模板、SDK 和本地专用 system |
| step.agent/define 的全部 schema 与执行器已恢复 | 没有云端私有 tool definitions/校验器 |
| 本地 Workflow 就是该 API 的本地后端 | 未建立源码或运行级关联 |
| 默认遇意外自动重新拆解 | 检查范围未发现强制通用出口，实验也没出现 |
| Worker 消息都直接注入 lead | 实测是整轮最终结果通知；进度与 thread 流不等于 context |
| Shared workspace 就是 shared memory | 对话 history 独立；成果需要明确传递或读取 |
| completed 等于正确或审计通过 | 只是执行终态；质量由具体任务策略实现 |
| 编辑后 resume 已实测成功 | 只有源码、key 探针；继续的是 lead session |
| 两次自主实验出现独立 verifier 阶段 | 验证由 workers 自查及 lead 补查，无 verifier worker |
| 五 agent cap 是 cloud engine 的 per-run 可配置硬限制 | 云端准备实验没启动；公开累计上限是另一概念 |
| 复现官方 70 bugs 基准 | 本地植入实验只有五个缺陷，未获取基准及三次原始运行 |
| List-cost 数字是实际订阅扣款 | CLI 报告估算口径，非财务账单 |

## 取证与实验限制

- JS 有 minification、动态模块和闭包。REA inventory 无解析失败，不代表语义图无缺失。
- 解压文件和 dead path 都被保留，只有可达路径可用于默认行为结论。
- Snapshot 记录 harness 数据，不是完整 HTTP wire capture。缓存、瞬时包装和服务端追加内容未全量观测。
- Safe/restricted、空 MCP、选定工具、模型和 agent cap 限制了行为。不能推广到所有 interactive/plugins/config。
- 两次自主实验都是单样本；角色选择可能受源码自然边界和成本约束影响。
- 未知项目实验发生约束修正。首轮与继续轮分开保留，不能称作完全无干预实验。
- 原报告可能含模型误述；必须与源码、tool IO、独立复现交叉对照。
- 发布副本脱敏后 hash 会改变。原 manifest 和 published manifest 各有用途，不能混用。

## 下一步最短验证路径

### 云端有 credits 后

先跑已准备的小型交接任务，取得真实 inline agent.system、thread events、共享文件操作和 worker 工具 IO，再请求 lead 原样输出它实际提交的程序。不要先用大 repo 做耗费巨大的 benchmark。

公开 API 隐藏启动/管理 run 的工具调用、程序正文和每 thread 向程序返回的数据。客户端采集不能直接绕过这层可见性；模型打印程序是一次追加的导出，完整性仍需比对 thread 数、实际输入、阶段与文件证据。[Workflow runs：visibility](https://platform.claude.com/docs/en/managed-agents/workflow-runs#a-runs-threads)

### 让意外确实挑战初始计划

需要一个已有合理初始分工、随后才暴露跨领域依赖或冲突的任务，并预留足够 agent 名额。观察程序内是否安排 planner，还是 run 完成后 lead 再生成新计划。任务不能强制“必须重派”，否则只能证明服从要求。

### 编辑与缓存恢复

先记录可重复的小 run，然后只改一处 prompt/option，检查缓存前缀与首次变化后的重执行；再只改 workspace 文件，检验缓存 key 是否检测。需记录 journal、实际工具调用和文件 hash，不能只看 UI。

### 失败、拒绝与审计

用可控且无破坏的任务分别触发 schema 失败、worker tool failure、候选被否定、全局假设被反驳，检查它们是否走不同路径。对最终汇总做独立审计，单独评估事实质量、覆盖与归纳准确性。

这些都是**后续实验建议，尚未执行**。本次整理和发布没有追加付费 Claude/cloud run。
