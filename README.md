# Claude Dynamic Workflow Research

对 Claude Code 本地 Workflow 与 Claude Managed Agents `multiagent_20261001` 的一次完整取证记录。调查日期为 **2026-10-11**。仓库收录研究文档、完整提取的提示词与源码、原函数探针、三次本地模型实验及通信记录，以及未能启动的云端实验记录。

**已恢复和验证的是本地实现、官方分发模板及公开 API 契约。没有取得云端私有执行器、完整隐藏 lead harness prompt，也没有实际运行 Managed Agents workflow。**

## 已得到的关键结论

1. 本地 Workflow 是 lead 编写的 **JavaScript 编排程序**。JSON 用于工具参数、schema 和结果；程序负责条件、循环、派发与合并。
2. 动态派发来自程序读取 worker 返回值，构造后续任务。控制策略通常在 run 开始前生成，任务内容和数量可在执行时确定。
3. Worker 有独立对话；不会默认复制 lead 的完整 history。交接通过显式结果传递、prompt 组装与共同文件完成。共享 workspace 不等于共享聊天记忆。
4. Worker 结果默认先交给程序。Lead 默认通过整轮完成通知接收脚本的最终返回值，必要时主动读取完整文件或逐 agent 日志。运行进度不等于完整中间结果自动进入 lead context。
5. 官方编写指南推荐补漏检查、独立反驳和分轮继续，但已恢复 prompt 中没有要求每个 run 必须加入“任意意外触发通用重规划”的出口。四份任务模板有各自明确的复核、返工和降级规则。
6. 运行完成、返回格式通过与任务正确是不同结论。审计和打回必须由具体协作策略安排。
7. 四份目标类型模板走 Claude API onboarding 入口；本地 Workflow 走本地运行器。没有证据证明两者共用编排实现。

## 阅读入口

| 想了解什么 | 文档 |
|---|---|
| 材料范围、取证步骤、证据强弱 | [范围与方法](docs/01-scope-and-methodology.md) |
| Lead 如何生成计划、动态派发和 handoff | [行为模型](docs/02-workflow-behavior.md) |
| 本地调用链、接口、缓存恢复和预算差异 | [本地实现](docs/03-local-runtime-and-call-chain.md) |
| Lead/worker 完整 prompt，四份模板的实际策略 | [Prompt 与模板](docs/04-prompts-and-templates.md) |
| 是否有通用重规划出口，中间结果是否直接给 lead | [重规划与结果交付](docs/05-replanning-and-result-delivery.md) |
| 每次实验做了什么、原始记录在哪 | [实验总览](docs/06-experiments.md) |
| 目前不能下的结论、后续最短验证路径 | [局限与待验证项](docs/07-limitations-and-open-questions.md) |
| 离线复核、取回二进制、重新实验 | [复核与复现](docs/08-reproduction-and-verification.md) |
| 研究中发现的错误、干预与修正 | [修正记录](docs/09-corrections-and-history.md) |
| 全部文件分类、来源与完整性 | [材料目录](docs/10-evidence-catalog.md) |
| 用户研究方向与未捕获的记录范围 | [请求与覆盖](docs/11-research-requests-and-coverage.md) |

## 实验结果

| 尝试 | 设置与结果 | 直接记录 |
|---|---|---|
| 原函数语义探针 | 五项检查通过；显式 host stubs，未调用模型 | [结果 JSON](evidence/semantics-probe.json) |
| 受控 context/workspace 交接 | Lead + 3 workers；A/B 并行，C 收到两者返回并读取 A 的产物 | [完整记录](evidence/live-probe/README.md) |
| 自主拆解的植入缺陷实验 | Lead + 4 workers；lead 自选按模块审计，确认全部 5 个植入缺陷；另有一个零 worker 的意外 noop run | [完整记录](evidence/bug-hunt-probe/EXPERIMENT.md) |
| 未知真实项目实验 | 未植入缺陷；Lead + 3 workers；得到一个可复现 CLI 问题，lead 自行验证，没有再派 worker | [完整记录](evidence/unknown-content-probe/EXPERIMENT.md) |
| 云端 bounded probe | 首个 create-agent 请求因 API credits 不足拒绝；没有云端资源、run 或 workers | [实际响应](evidence/cloud-probe/agent-created.json) |

三次本地实验的 CLI 模型 list-cost 估计分别为 $0.1408173、$0.32556、$0.878151；第三项含同一 lead session 的后续继续。这些不是订阅实际扣款证明，也不是云端费用。

## 文件布局

```text
docs/                         当前综合文档与修正说明
evidence/                     原研究目录的发布镜像
  REPORT.md                   早期源码报告，作为历史记录保留
  PROMPTS.md                  静态提示词与脚本完整索引
  prompts/                    Lead/worker 指令及模板原文
  bun-files/                  2,609 个 Bun 嵌入文件
  extracted-js/               2,365 个提取的 JS 源码文件
  decoded-assets/             141 个解压资源
  formatted-js/               阅读用格式化调用链源码
  builtins/                   内置 deep-research workflow
  live-probe/                 三 worker 受控交接实验
  bug-hunt-probe/             五个植入缺陷的实验
  unknown-content-probe/      未修改上游项目的实验与继续记录
  cloud-probe/                云端失败尝试及准备脚本
  rea-evidence.json.gz        REA 完整分析 evidence，发布版已脱敏
manifests/                    来源、脱敏、完整性和验证清单
scripts/                      发布构建与离线验证工具
SHA256SUMS                    发布文件 SHA-256 清单
```

## 原始记录与发布版的区别

原始本机材料保持不变。GitHub 中的是**脱敏发布镜像**：统一替换研究目录、个人 home 和临时用户路径；稳定替换账号邮件、组织身份等元数据。保留任务内容、agent/run/session 关联 ID、因果时间线、工具调用、stdout、prompt、返回值和生成 workflow。

每个源文件的原始 hash 与发布 hash 在 [source-catalog](manifests/source-catalog.json) 中分开记录。原材料里的旧 manifest 仍表示原始字节；验证发布版应使用 [published-files](manifests/published-files.json) 或 `SHA256SUMS`。不能把脱敏日志称为逐字不变的 wire capture。

大体积官方分发包通过本私有仓库的 [研究归档 Release](https://github.com/yzxoi/claude-dynamic-workflow-research/releases/tag/research-2026-10-11) 保存，并保留官方下载来源和 hash。源码、prompt 和实验记录在 Git 中可直接浏览。缓存与重复 symlink 的省略理由见 source catalog。

```bash
python3 scripts/verify_archive.py
```

第三方内容保持原权利归属，详见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。没有为整库第三方源码声明新的统一许可证。
