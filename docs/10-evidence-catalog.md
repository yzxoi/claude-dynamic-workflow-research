# 材料目录、来源与完整性

## 全量 inventory

[source-catalog](../manifests/source-catalog.json) 给每个源文件记录路径、bytes、SHA-256、发布/省略/附件决定；发布文件同时记录脱敏后的 hash 和 byte-identical 标记。[published-files](../manifests/published-files.json) 是当前 Git tree 的发布 inventory，不含自身和 SHA256SUMS，避免循环 hash。

[claims](../manifests/claims.json) 将关键结论映射到证据类别与文件；[distributions](../manifests/distributions.json) 记录大包、官方下载 URL、固定版本和 hash；[redactions](../manifests/redactions.json) 记录发生替换的文件及规则次数。

## 分类导航

| 类别 | 内容与入口 |
|---|---|
| 原综合成果 | [REPORT](../evidence/REPORT.md)、[PROMPTS](../evidence/PROMPTS.md)、[重规划核对](../evidence/REPLANNING-AND-RESULT-DELIVERY.md) |
| 官方包 metadata | [native](../evidence/native-latest-metadata.json)、[wrapper](../evidence/wrapper-latest-metadata.json)、[SDK](../evidence/anthropic-sdk-metadata.json)、[ant release](../evidence/ant-release.json) |
| 原始嵌入文件 | [bun-files](../evidence/bun-files/)，包括 JS、压缩 markdown、native extensions 与保留的 notices |
| JS source | [extracted-js](../evidence/extracted-js/)，按原二进制 offset 命名，保留重复映射 |
| 可读源码 | [formatted-js](../evidence/formatted-js/)，包括 tool/runtime/prompts/subagent-runner 和 skill 注册 |
| REA 工作范围 | [workflow-slice](../evidence/workflow-slice/)、[workflow-kernel](../evidence/workflow-kernel/)、[summary](../evidence/rea-summaries.json)、[evidence gzip](../evidence/rea-evidence.json.gz) |
| 提取辅助 | [extract-bun](../evidence/extract-bun.py)、[decode-assets](../evidence/decode-assets.py)、[extract-prompts](../evidence/extract-prompts.cjs)、[Bun extraction](../evidence/bun-extraction.json) |
| Prompt 原文 | [prompts](../evidence/prompts/)，文本、动态插值表达式、组合描述和五份 cloud-template（其中 deep-researcher 不是目标四模板之一） |
| 内置 JS workflow | [deep-research](../evidence/builtins/deep-research-0.js)，未执行 |
| 公共模板对照 | [official-skill](../evidence/official-skill/)，四模板、commit 与比较结果 |
| SDK 公开边界 | [agents.ts](../evidence/cloud-sdk/package/src/resources/beta/agents/agents.ts)、[sessions](../evidence/cloud-sdk/package/src/resources/beta/sessions/)、threads/events 编译产物 |
| Text 搜索材料 | [strings](../evidence/strings/)、[string-manifest](../evidence/string-manifest.json)，不是独立反编译源码 |
| 受控交接 L1 | [live-probe](../evidence/live-probe/)，role prompts、capture、summary |
| 自主植入实验 L2 | [bug-hunt-probe](../evidence/bug-hunt-probe/)，fixture、ground truth、capture/export、tool IO、独立 reruns |
| 未知项目 L3 | [unknown-content-probe](../evidence/unknown-content-probe/)，上游快照、workspace、首轮备份、继续轮、capture/export、独立验证 |
| 云端失败 C3 | [cloud-probe](../evidence/cloud-probe/)，模型列表、拟用 system/task、runner 和真实 create 拒绝 |
| CLI 取证 | [Claude help](../evidence/claude-2.1.296-help.txt)、[ant agent help](../evidence/ant-agent-create-help.txt) 及根目录其他 ant help |

## 数量口径

- 2,609 是嵌入文件记录数量；不都是 agent prompt。
- 2,365 是 JS source 文件数量；formatted 与 extracted/bun-files 可能是同一 source 的不同表示。
- 141 是本次恢复的 zstd 资源数量。
- Prompt manifest 的 47 项包含内置 workflow；prompts 目录的 46 文件不是 46 agents。
- 三次 model 实验分别有 3、4、3 workers；均有一位 lead，不能按普通 subagent_stats 相加。
- L2 第二个 run 为 noop，不能因 run 数量为二而推断八 workers。
- 第一轮 unknown export/capture 备份与最终 export 可能重复，保留它们是为了证明干预前后状态。

最终文件数和 bytes 用 published-files 的机器可读结果为准；文档不硬编码随着验证报告增加而改变的总数。

## 省略和附件

省略 .DS_Store、Python bytecode/cache、重复 symlink、VCS 元数据。真实底层文件已保留；source-catalog 逐项写理由。未省略失败 stderr/debug 或无结果尝试，因为它们属于用户要求的原始记录。

Native 主 executable 和 tar、ant executable 与下载 zip 不直接写入 Git tree。私有 Release 保存官方 tar/zip，包含 executable；取回关系、原始 hash 和来源见 distributions。其他较小官方包与完整提取内容均在 tree 内。

unknown-content-probe-records.zip 用发布目录重建，避免未脱敏旧归档绕过文本替换。REA gzip 在解压后替换本机路径，再重新压缩；原 hash 仍保存在来源清单，发布 hash 则单独核对。

## 人工可读与机器可读相互校验

从某一结论出发，先看 claims 指向的原证据，再按 source-catalog 判断它是否脱敏，最后按 published-files 核对当前 bytes。旧原始 hash 不匹配发布文件属于预期替换，不是实验记录遗失。

第三方权利与许可边界见 [notices](../THIRD_PARTY_NOTICES.md)。这个仓库是私有研究归档；没有把提取的专有内容重新授权为开源。
