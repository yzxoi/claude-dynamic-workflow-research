# 研究请求与记录覆盖

这份归档尽量保存用户要求的全过程材料，但不把可见片段补写成完整聊天。下表从此次可见用户消息整理研究方向；实验中的完整 task 与实际 worker 输入另在 evidence 中。

| 顺序 | 用户原始要求的核心内容 | 对应交付 |
|---|---|---|
| 1 | 用 morluto/rea 或其他工具逆向 Claude Code，找 multiagent_20261001 的逻辑、完整 prompt、通信 | [方法](01-scope-and-methodology.md)、[调用链](03-local-runtime-and-call-chain.md)、REA evidence |
| 2 | 官方 orchestration 文档也有这个类型，是否本地就有 | 区分本地分发的模板/API 配置与本地执行器 |
| 3 | 追踪模板使用处；允许小任务探测；解释 context/workspace/分工通信 | [模板](04-prompts-and-templates.md)、L1/C3 |
| 4 | Claude Code 已登录 | 后续本地实跑；没有归档凭据 |
| 5 | Console 已授权 | 模型读取成功，创建 agent 仍额度拒绝 |
| 6 | 先交付现有证据 | 停止继续云端付费实验，保留拒绝原响应 |
| 7 | 贴本地 lead/worker 全 prompt，结合程序解释，云端未知单列 | [prompt 索引](../evidence/PROMPTS.md)、[L1 完整记录](../evidence/live-probe/README.md) |
| 8 | 不预设角色/阶段，最多五 agents 自主 bug-hunt | [L2](../evidence/bug-hunt-probe/EXPERIMENT.md) |
| 9 | 未知内容实验，观察追加验证/重派与后序成果共享 | [L3](../evidence/unknown-content-probe/EXPERIMENT.md)，包括约束修正与无重派事实 |
| 10 | 先系统解释整体模式，不需要实现细节 | [行为模型](02-workflow-behavior.md) |
| 11 | 返回值怎样执行条件/循环/派发/合并，是否一开始写死 | 区分初始规则与运行时工作清单 |
| 12 | Workflow 包含什么，是 JSON 吗 | 本地 executable JS；JSON 是工具输入和数据 |
| 13 | Worker 发现预设规则未覆盖的问题，谁重新拆解 | [重规划边界](05-replanning-and-result-delivery.md) |
| 14 | 官方 prompt 是否要求通用出口，中间结果是否直接给 lead | 全 prompt/模板核对，加完成通知源码与 L3 队列实证 |
| 15 | 在 yzxoi 的新 private repo 尽可能完整归档 | 本仓库、逐文件清单、脱敏记录、私有 Release |

原始请求还引用了官方 116k 行代码/70 植入 bugs、单 agent 三次 14/15/27 与 workflow 三次 66 的对比，以及最多 1,000 agents、成本较高的说明。它们是研究动机；本次没有取得或复现该基准，不作为本地实验结论。

## 可用原始记录

实际生成的 workflow、worker prompts、schema、系统 chunks、tool IO、messages、transcripts、journal、完成通知、CLI events/debug、fixture/文件产物都按原结构保留在脱敏镜像。实验者脚本和独立复现也保留。

REA 完整 evidence 保存了静态分析内容；并未取得完整所有研究 shell 命令的 terminal recording，或此前助手每轮答复的完整原文。已有旧报告可以追踪结论演变，不能替代缺失的聊天/终端记录。认证 UI 全过程也没有录制。归档不伪造这些缺失内容。

发布检查与复核报告是本次整理新产生的材料；它们与原实验目录分开。原始源目录没有改动。
