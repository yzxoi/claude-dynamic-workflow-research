# 复核、取回材料与复现

## 离线检查归档

在仓库根目录执行标准库验证器：

```bash
python3 scripts/verify_archive.py
```

它检查 published manifest/hash、作者新增 Markdown 的相对文件链接、JSON/JSONL、研究脚本语法、REA gzip 结构及实验 ZIP 与发布目录的一致性。它不启动 Claude、不读取认证存储、不创建 API resource、不执行归档中的 vendor code。

三项内容按 [content-formats](../manifests/content-formats.json) 声明的原格式检查：models.json 是 CLI 连续输出的多个 JSON 值；bad.json 和 badenc.json 是 worker 故意生成的畸形 JSON/编码输入，用来触发错误路径。验证器核对负例的 hash 并确认它们仍不能解析，而不是修改原记录让所有 .json 假装有效。

查看 [validation-report](../manifests/validation-report.json) 和 [scan-summary](../manifests/scan-summary.json) 可了解发布时检查口径。完整 gitleaks 临时报告没有加入仓库，安全摘要保留规则、文件位置和人工判断。

## 原始、脱敏与重新提取

- 原始来源清单：[source-catalog](../manifests/source-catalog.json)，原 SHA-256 与 published SHA-256 分列。
- 发布全量清单：[published-files](../manifests/published-files.json)、[SHA256SUMS](../SHA256SUMS)。
- 脱敏规则及文件：[redactions](../manifests/redactions.json)。
- 官方分发来源与 hash：[distributions](../manifests/distributions.json)。

发布副本的原日志、原 stdout、原 generated script 字段保留采集的结构和因果关系，但可能替换路径或账号元数据。source-catalog 的 byte_identical_to_source 才表示字节相同；不能从文件名称中的 original/raw 推断。

旧 evidence manifest 表示采集时原字节。它们不是坏文件，也不能直接用于验证脱敏后的副本。需要恢复严格原字节的公开 package，可重新下载官方包后按版本提取。

## 取回官方二进制

私有 [Release](https://github.com/yzxoi/claude-dynamic-workflow-research/releases/tag/research-2026-10-11) 保存官方 native tar、wrapper tar、SDK tar、ant zip 和完整脱敏离线归档。Release assets 另有 SHA256SUMS；Git tree 不提交 100 MiB 以上文件。

使用 GitHub CLI 可下载附件；它使用读者自己的 GitHub 认证，不需要 Claude API key：

```bash
gh release download research-2026-10-11 \
  --repo yzxoi/claude-dynamic-workflow-research \
  --dir downloads
```

也可以按 distributions.json 中官方下载 URL 取回，并核对 SHA-256、npm SRI 或 ant 的 release digest。取回后用到源码提取时，无需先执行该 binary。

## 在副本中重新提取

extract-bun.py 会把 manifest 写到脚本同级目录，decode-assets.py 和 prompt/semantics 脚本也会写自己的产物。因此请在新复制的实验目录运行，避免覆盖这一归档。

```bash
mkdir -p downloads/reextract
cp evidence/extract-bun.py downloads/reextract/
tar -xzf downloads/claude-code-darwin-arm64-2.1.296.tgz \
  -C downloads/reextract
python3 downloads/reextract/extract-bun.py \
  downloads/reextract/package/claude \
  downloads/reextract/bun-files
cp evidence/decode-assets.py downloads/reextract/
python3 downloads/reextract/decode-assets.py
```

decode-assets.py 需要 zstd 可执行程序。该提取器针对本版本 little-endian Mach-O64 的 Bun graph 格式，不是适用于未来任意版本的通用 unpacker。

语义探针需要 Node 和原 bun-files 对应文件；在副本中运行 `node probe-semantics.cjs`。输出将重写 semantics-probe.json。读脚本即可核对 stubs 和边界，无需认证。

## 重新运行本地模型实验

保留的 runner 是当时实际使用的脚本，含该实验目录结构、已有 session ID 和导出路径；它们是证据，不是无需适配的一键产品。重新实验应：

1. 新建隔离目录和 session ID，复制 task、fixture 与 settings。
2. 取回固定版本 binary，明确指定模型、effort、工具、CLI 美元预算和 wall timeout。
3. 修改 runner 的工作目录和 capture/export 源位置，启用 system snapshots。
4. 保留 raw stream、stderr/debug、生成脚本、journal、worker transcript 和 source 前后 hash。
5. 把后来独立复现的结果与 lead 当时收到的结果区分开。

L2 runner 设置 medium effort、$2 上限；L3 是 high effort、$3 上限。这些数字限制是该次设置，不能对未来模型成本作保证。Prepare-bug-hunt 会写源码夹具，必须在新副本使用。

继续 lead session 与编辑 workflow/resumeFromRunId 是不同实验；不要用前者的成功替代后者的验证。

## 云端准备脚本

[cloud-probe/run-probe.py](../evidence/cloud-probe/run-probe.py) 会依次创建 agent、environment、session；首次请求失败就退出。在有余额的 workspace 执行会产生资源并可能调用付费模型。这次归档未再次执行它。

[capture-cloud-readonly.py](../evidence/capture-cloud-readonly.py) 是已有 session 的 GET-only collector。它支持显式环境 API key，或让官方 ant CLI 在内存提供 token，且不把 token 写到输出。曾检查其 help/语法；没有真实 cloud session 可供采集。

采集 thread 只能获得公开可见层。Inline system 是程序定义的 system，不代表服务端全部隐藏 harness；对 lead 导出的程序也需交叉验证。详见 [局限](07-limitations-and-open-questions.md)。

## 重建发布清单

修改研究文档或发布副本后：

```bash
python3 scripts/build_publication.py --refresh
python3 scripts/verify_archive.py
```

首次 build 才使用 --source；它复制并脱敏原目录，拒绝覆盖已有 evidence。Refresh 会重建 ZIP、更新发布 hash，不修改本机原始材料。验证报告文件更新后还需 refresh，避免 hash 过期。
