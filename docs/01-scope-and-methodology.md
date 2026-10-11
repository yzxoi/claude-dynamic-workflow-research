# 范围、方法与证据等级

## 原始研究问题

目标是弄清 `multiagent_20261001` 的 dynamic workflow 如何产生，lead 如何分工，workers 怎样协作、共享 context/workspace、传递结果，是否有独立审计、返工、重规划与恢复。随后增加了不预设角色和阶段的小实验，检查实际行为是否符合静态材料。

研究对象必须拆开：

| 层面 | 材料 | 能说明什么 |
|---|---|---|
| Claude Code 本地 Workflow | 官方 2.1.296 分发包、提取源码、真实本地运行 | 本地编排与 worker harness 的可达实现和受限环境行为 |
| Managed Agents 配置与契约 | SDK 0.133.0、官方 onboarding 模板、公开文档 | 类型、公开配置、模板策略和对外状态语义 |
| Managed Agents 私有执行器 | 本次未取得 | 完整 DSL、隐藏工具说明、内部 scheduler/harness 无法由本地材料代替 |

机器原有 Claude Code 2.1.123 未替换。实验使用独立下载的 2.1.296。任务源码及运行记录在独立实验目录产生，没有改动承载调查的 Synergy checkout 或 runtime。

## 证据标签

| 标签 | 含义 | 限制 |
|---|---|---|
| LOCAL-SOURCE | 已追踪的本地发布源码 | 仍需区分可达路径和未启用代码 |
| LOCAL-LIVE | 实际本地 CLI/model/tool/文件记录 | 只覆盖实验约束和观察到的行为 |
| HOST-PROBE | 提取原函数在明确 stubs 下运行 | 不证明完整 CLI 接线或云端行为 |
| TEMPLATE | 正式分发的任务 prompt | 是策略要求，不证明生成程序实际正确实现 |
| PUBLIC-CONTRACT | 官方 SDK/公开文档 | 不是服务端私有源码或本次实跑 |
| INFERENCE | 根据上述材料作出的推导 | 明确标注，不与观测混写 |
| UNVERIFIED | 缺失证据或未运行 | 保留问题，不补造实现 |

## 二进制与提取

主要对象是 `@anthropic-ai/claude-code-darwin-arm64@2.1.296`，arm64 Mach-O。主二进制为 240,664,432 bytes，SHA-256：

```text
c9b5341637becbd423ddffc5b254afb645682a3868cb708bbc6cc0e7bb419937
```

三个 npm 包对照 registry metadata 核对过 SHA-512 SRI。这不是 npm registry 签名验证。[Native metadata](../evidence/native-latest-metadata.json)、[Wrapper metadata](../evidence/wrapper-latest-metadata.json)、[SDK metadata](../evidence/anthropic-sdk-metadata.json)。

直接解析 `__BUN/__bun` 中的 standalone module graph，比把 strings 输出或反汇编结果当源码更直接。依据 Bun 尾部标记、Offsets 与文件记录恢复文件边界；它保留 JS 源文，即使带有 bytecode。

| 提取项 | 数量与体积 |
|---|---|
| 嵌入文件 | 2,609；contents 52,986,680 bytes |
| JS source 段 | 2,365；45,036,083 bytes |
| zstd 解压资源 | 141；10,264,450 bytes |
| Source map | 未找到 |

保存了 [提取器](../evidence/extract-bun.py)、[提取摘要](../evidence/bun-extraction.json)、[嵌入文件 manifest](../evidence/bun-files-manifest.json)、[JS manifest](../evidence/extracted-js-manifest.json)、[解压器](../evidence/decode-assets.py)、[解压 manifest](../evidence/decoded-assets-manifest.json)。格式参考代码也保存为 `evidence/Bun-src_*.rs`，来源在早期报告中说明。

## REA 的作用与限制

实际使用 rea-agents 6.3.0 检查提取出的 JavaScript。没有配置 Ghidra/Hopper/IDA 原生 provider。

第一轮 slice 的 13 个 JS 文件解析无失败，但语义图达到 100,000 节点限制，保留材料仍有 33,612 个 unknown。缩小到三个文件 kernel 后没有图截断，解析 23,949 个 AST 节点，但仍有 5,078 个 semantic unknown。Inventory 完整不代表调用语义完整，因此结论同时依靠人工调用链追踪、原函数探针和真实 CLI 实验。

[REA 摘要](../evidence/rea-summaries.json)、[完整 evidence](../evidence/rea-evidence.json.gz)、[原始完整性说明](../evidence/rea-evidence-integrity.json)。发布版 evidence 的本机路径已脱敏，原 hash 和发布 hash 分开保存。

## 源码到实测的步骤

1. 定位目标类型、模板资源、工具描述、authoring 指南和 worker runner。
2. 解压先前文本检索没有覆盖的资源，补齐第四份 Performance tuner 模板。
3. 追踪 skill 文件表和 onboarding 入口，确认它们不是本地 Workflow 的执行入口。
4. 排除常规 launch 未启用的 fact-rule runtime。
5. 用五项原函数探针检查 pipeline、parallel、缓存 key 和确定性约束。
6. 实跑受控数据/文件 handoff；导出 recorded system chunks、tool schema、输入和结果。
7. 实跑由 lead 自己拆解的植入缺陷任务。
8. 实跑无植入缺陷的真实项目，并在同一 lead session 撤销多余的单 run 限制。
9. 准备并尝试 Managed Agents bounded probe；首个资源请求被额度拒绝，未进入云端编排。
10. 再核对通用重规划要求和结果通知链，修正把“可设计策略”当成默认机制的风险。

## 记录完整性

保存的是本地 harness 记录和 prompt snapshots。它们能证明工具定义、任务输入、工具调用和最终返回，却不等于完整 HTTP wire request、缓存 block 布局或云端 system stack。

研究没有读取认证存储。认证由用户完成的官方 CLI 流程处理。发布排除凭据，账号元数据脱敏；原始材料留在本机。所有省略、替换和发布 hash 都有单独清单。
