# 更正、实验干预与历史材料

研究应保留失败、偏差和修正。Evidence 中的报告是采集阶段的材料；本 docs 目录给出整理后的当前判断。两者时间和覆盖范围不同。

| 原判断或记录 | 当前更正 | 依据 |
|---|---|---|
| 初次只找到三份目标模板 | Performance tuner 在压缩资源中，完整目标模板为四份 | [decoded manifest](../evidence/decoded-assets-manifest.json)、[模板](../evidence/prompts/cloud-template-performance-tuner-6c866b59.md) |
| 模板在本机，可能是本地编排入口 | 四模板走 claude-api onboarding，不能证明本地执行器共用 | [call sites](../evidence/template-call-sites.json) |
| 发布包出现 fact-rule API，可解释默认派发 | 可达 launch 未启用该路径；v2 是 journal key 格式 | [runtime](../evidence/formatted-js/workflow-runtime.js)、[tool](../evidence/formatted-js/workflow-tool.js) |
| 编排有 budget 接口，因此 token ceiling 总是生效 | 可达本地 launch 传 total:null；有限 kernel 与入口接线需区分 | [实现说明](03-local-runtime-and-call-chain.md) |
| 可设计重规划，所以默认会重规划 | 指南是建议，模板是任务策略；没有通用出口必需性的证据 | [核对](05-replanning-and-result-delivery.md) |
| 普通 subagent_stats.spawned=0，所以没有 workers | Workflow journal 和独立 transcript 显示三 workers | [L1 summary](../evidence/live-probe/summary.json) |
| L2 完全遵守只调用一次 Workflow | 主 run 后多启动零 worker noop，agent 总上限仍满足 | [L2 verification](../evidence/bug-hunt-probe/export/verification.json) |
| L2 最终汇总说验证过 merge_overlaps([]) | tool IO 没有这一实际调用；是模型报告偏差 | [lead tool IO](../evidence/bug-hunt-probe/export/lead/tool-io.json) |
| L2 pricing 未修改输入已做 before/after 实验 | 当时只有代码观察，没有完整运行断言 | [lead tool IO](../evidence/bug-hunt-probe/export/lead/tool-io.json) |
| L2 第六个 confirmed 就是第六个植入 bug | 是额外浮点取消现象，ground truth 只有五个，规格层面不确定 | [truth](../evidence/bug-hunt-probe/ground-truth.json)、[reruns](../evidence/bug-hunt-probe/export/independent-proof-reruns.json) |
| L3 原约束能公平观察是否另开 run | runner 加了多余的一次 Workflow/no-resume；在同一 lead session 撤销，cap 未变 | [修正输入](../evidence/unknown-content-probe/continuation-task.txt) |
| L3 json.dumps 在 try 外 | 实际在 try 内，但 except 太窄，TypeError 逃逸 | [源码](../evidence/unknown-content-probe/workspace/bin/jsonpointer)、[observations](../evidence/unknown-content-probe/export/observations.json) |
| L3 上游测试无法运行，是项目本身问题 | python -I 忽略 PYTHONPATH；runner 显式 sys.path 后 52 tests 通过 | [独立验证](../evidence/unknown-content-probe/export/independent-verification.json) |
| 52 tests 通过属于 lead 的验证 | 由研究者随后运行，未发送给 lead | [observations](../evidence/unknown-content-probe/export/observations.json) |
| L3 有共享文件，故已有后序 agent handoff | 只有共享 cwd/目录列表，没有后序 worker，没有 peer 正文读取 | [observations](../evidence/unknown-content-probe/export/observations.json) |
| 长通知包含全部返回，lead 已直接收到全部 | 约 19,821 字符结果被截断，lead 主动读取 output 后才得到完整数据 | [queue](../evidence/unknown-content-probe/export/lead/queue-operations.json) |
| 整轮完成即所有发现正确 | 最终汇总也可能错述证据，独立审计是另一个策略 | 上述报告与源码/工具记录的差异 |
| Console 授权成功，云端已经可以实跑 | 首个 create-agent 因 credits 不足拒绝；没有 resources/run | [实际错误](../evidence/cloud-probe/agent-created.json) |

## 历史记录的阅读方式

[REPORT.md](../evidence/REPORT.md) 是最早综合报告，重点在源码和 L1；[REPLANNING-AND-RESULT-DELIVERY.md](../evidence/REPLANNING-AND-RESULT-DELIVERY.md) 是最后问答的证据核对。它们作为原研究成果保存，不被本次发布改写成伪造的同期报告。

L2/L3 EXPERIMENT 内嵌 model 原答复，有些段落属于模型自己的断言。读者应优先看对应 raw tool IO、脚本、文件和 independent verification。最终 lead response 的措辞不自动提升为已审计事实。

发布时仅按统一规则替换路径和身份元数据；保留 session/run/agent ID、时间、错误、重复调用和干预输入，以便按因果关系审计。
