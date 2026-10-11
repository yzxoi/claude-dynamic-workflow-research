# 重规划要求与结果传递：证据核对

核对日期：2026-10-11。没有新启动 Claude 实验或云端 run。

## 结论与边界

在已恢复的本地 lead system chunks、Workflow 工具说明、workflow-authoring 指南、两种 worker 指令和四份官方云端任务模板中，未发现要求每次 workflow 必须加入“遇到任意意外就请求重新规划”的通用出口。云端完整私有 lead harness prompt 尚未取得，因此不能推断其绝无其他指令。

本地官方指南确实推荐结果驱动的继续探索：
- 第 14 行：大型任务分成若干轮，读完每轮结果再决定下一阶段。
- 第 123 行：可安排 completeness critic 找缺失的搜索方式、未验证结论、未读来源，其发现形成下一轮工作。
- 第 121 行：可循环发现，直到连续若干轮没有新项目。
- 第 114、128 行：这些是可按任务选择和组合的质量模式，可设计其他自修复循环。
- 第 130 行：编排控制流应由确定性程序表达。

这些是官方策略建议，不是运行时默认创建重规划 agent 的证据。Ultracode 段落强化编排和验证的倾向，也没有要求上述通用出口。

## 四份模板实际规定

| 模板 | 发现遗漏、被否定、质量不足时 | 技术失败或不足时 |
|---|---|---|
| Bug hunter | 每个切片都二次检查遗漏，包括首轮无发现或失败的切片；候选首次被 prover 否定后，交给 fresh prover，附否定理由并尝试另一输入，第二次结论为最终结论 | 单 agent 失败不应使整轮失败；报告失败者、完成工作和未验证候选；run 失败或返回不足时，不自行启动另一轮 |
| Watchlist scanner | 每个 ticker 都复核遗漏；不通过的内容重做再审；Quick 模式明确改为 reviewer 自己修正，代替额外 redo | 失败 ticker 记为未覆盖；run 失败或返回不足时报告已完成部分，不自行启动另一轮 |
| Performance tuner | checker 独立检查；失败、发现更好算法或提速落后触发 redo；最终测量失败回退到通过检查的版本或原版 | optimizer 失败进入 redo；checker 失败记为未检查，lead 随后自行检查；整轮失败、超时或返回不足时交付已通过检查的磁盘产物，不自行另开 run |
| Explainer video maker | 独立 reviewer 最多指出一个需修复场景，只为该场景派一个 fixer | 音乐不可用则交付无声视频并说明；报告未修复项；失败或结果不足时使用已完成部分，不自行另开 run |

这里的“不自行启动另一轮”是模板要求先询问用户，不是平台不能再运行。它们没有要求因任意未知问题改变切片、角色、阶段或整体策略。

模板来源：
- [Bug hunter](official-skill/bug-hunter.md)：59、61、63、70、74 行。
- [Watchlist scanner](official-skill/watchlist-scanner.md)：46、56、67、69 行。
- [Performance tuner](official-skill/performance-tuner.md)：72—86 行。
- [Explainer video maker](official-skill/explainer-video-maker.md)：58—70 行。

## 中间结果是否自动传给 lead

默认路径是：
worker 返回值 → workflow 程序 → 程序传给后续 worker 或纳入最终 return → 整轮完成通知 → lead。

本地证据：
- worker-text-system 指令说最终文本是 calling script 的逐字返回值，并禁止用 SendUserMessage 交付。
- worker-structured-system 指令说脚本只读取 StructuredOutput 返回；格式不符时修正格式。
- workflow-tool-with-skill 第 1 行规定后台执行并在整轮完成时发 task-notification。
- workflow-runtime 的 agent 包装将完整 worker return 写入 journal，然后返回给脚本调用方。
- 脚本最终 return 经运行器包装成 result；任务完成时 hXn 把该 result 放入 lead 的 task-notification 队列。
- 进度事件更新 UI/task registry 和 SDK 展示；它们不等于把完整 worker 返回逐个追加到 lead 的对话。
- 完成通知只携带脚本最终返回的数据，不自动补回脚本过滤掉的 worker 原始结果；完整逐 agent 返回仍可从 journal 主动读取。
- 本地 2.1.296 的完成通知对序列化结果应用 8,000 字符截断逻辑，附完整 output-file 和 journal 路径。不要把这个版本数值当成云端规则。

未知项目实测：
- 三个 worker 完成后只有一条整轮完成通知入队。
- 脚本最终 return 包含三份 worker 结果，所以 lead 最终可取到全部结果。
- 完整结果约 19,821 字符；通知只带截断前缀。
- lead 随后主动读取完整 output 文件，再复现 CLI worker 的发现。
- 没有后续 worker、没有运行中通用重规划循环。
- lead 在等待期间自行做过探针，不应误记为读取了 worker 中间输出。

实测记录：
[observations](unknown-content-probe/export/observations.json)、
[queue operations](unknown-content-probe/export/lead/queue-operations.json)、
[lead tool IO](unknown-content-probe/export/lead/tool-io.json)、
[实际 workflow](unknown-content-probe/export/wf_b793799a-8e3/workflow.js)。

源码定位：
[完成通知生成](formatted-js/205220505.js)：264、319、356、395 行。
[运行器与通知调用](formatted-js/workflow-runtime.js)：2045、3624、3880、4050、4070 行。

## 云端官方文档可确认的部分

[Workflow runs](https://platform.claude.com/docs/en/managed-agents/workflow-runs#how-dynamic-workflows-work)：
worker 结果先交给程序，程序决定后续工作；整轮结束后 lead 获得一轮读取结果的机会，可回答或启动下一轮。文档说明在预算、中断等情况下，这一轮可能延迟或不发生。

[Run threads](https://platform.claude.com/docs/en/managed-agents/workflow-runs#a-runs-threads)：
各 thread 的消息留在自身事件流；部分 thread 状态事件到主事件流。客户端可读取 thread，不代表 worker 完整消息自动成为 lead 的上下文。

[Multiagent orchestration](https://platform.claude.com/docs/en/managed-agents/multiagent-orchestration#hand-work-to-other-agents)：
普通 subagent 能接收 lead follow-up；workflow worker 不能通过这种通道追问。Lead 可检查运行进度。

仍未确认：云端私有 harness 是否附加其他重规划要求、lead 可用的完整运行中检查工具、最终结果私有注入格式和截断规则。没有云端实际 run。

