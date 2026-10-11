import collections
import hashlib
import html
import json
from pathlib import Path
import re
import zipfile

ROOT = Path(__file__).resolve().parent / 'unknown-content-probe'
OUT = ROOT / 'export'
verification = json.loads((OUT / 'verification.json').read_text())
provenance = json.loads((ROOT / 'provenance.json').read_text())
run = verification['workflows'][0]['runId']
workflow = json.loads((OUT / run / 'metadata.json').read_text())
lead_calls = json.loads((OUT / 'lead/tool-io.json').read_text())
completions = json.loads((OUT / 'completions.json').read_text())
independent = json.loads((OUT / 'independent-verification.json').read_text())
notification = next(OUT.glob('notification-*.xml')).read_text()
inline = html.unescape(notification.split('<result>', 1)[1].split('</result>', 1)[0])
prefix = inline.split('\n... (truncated ', 1)[0]
full = json.dumps(workflow['result'], ensure_ascii=False, separators=(',', ':'))
assert full.startswith(prefix)
systems = [json.loads((OUT / w['runId'] / w['agentId'] / 'system-chunks.json').read_text()) for w in verification['workers']]
same_system = all(s == systems[0] for s in systems)
if same_system:
    (OUT / 'common-worker-system.txt').write_text('\n\n'.join(systems[0]) + '\n')
    (OUT / 'common-worker-system-chunks.json').write_text(json.dumps(systems[0], ensure_ascii=False, indent=2) + '\n')
statuses = collections.Counter(item['classification'] for area in workflow['result'] for item in area['result']['items'])
observations = {
    'experiment': 'unmodified upstream project; no planted defects and no correctness oracle',
    'constraintCorrection': 'After the first turn, removed the runner-added one-Workflow/no-resume limit in the same lead session. The cumulative four-worker limit was unchanged. No roles, phases, expected findings, or follow-up worker were prescribed.',
    'leadSessionId': verification['sessionId'],
    'workflowRunId': run,
    'agents': {'lead': 1, 'workers': verification['workerAgents'], 'total': 1 + verification['workerAgents'], 'cap': 5},
    'additionalWorkerDispatch': False,
    'resultDrivenLocalVerification': True,
    'continuationLocalVerification': True,
    'workerSystemIdentical': same_system,
    'workflowDurationMs': workflow['durationMs'],
    'workflowReportedTokens': workflow.get('totalTokens'),
    'workflowToolCalls': workflow.get('totalToolCalls'),
    'workerItemCounts': dict(statuses),
    'notification': {'fullResultCompactChars': len(full), 'decodedPrefixChars': len(prefix), 'reportedOmittedChars': int(re.search(r'truncated (\d+) chars', inline).group(1)), 'prefixMatchesFullResult': True, 'completeResultIsInOutputFile': True},
    'workspaceSharing': {'sameWorkingDirectory': True, 'separateWorktrees': False, 'peerResultInjectedIntoWorkerPrompt': False, 'observedCrossDirectoryListing': 'class-api listed scratch/cli (empty at that moment) and scratch/lead containing d.json, e.txt, p.txt', 'observedPeerFileContentRead': False, 'laterWorkerFileHandoff': 'not observed; no later worker was dispatched'},
    'upstreamTests': {'testsRun': independent['upstreamTests']['testsRun'], 'successful': independent['upstreamTests']['successful'], 'receivedByLead': False},
    'independentBugConfirmation': True,
    'sourceCorrection': 'json.dumps is inside the try block, but except only handles JsonPointerException; the emitted TypeError escapes it. Worker and lead said outside the try, which is inaccurate.',
    'bootstrapCorrection': 'python -I ignores PYTHONPATH; the runner selected the local module explicitly via sys.path.insert and ran all 52 upstream tests successfully. The lead inability to run tests was an invocation issue.',
    'costUsdListEstimateCumulative': completions[-1]['total_cost_usd'],
    'upstreamSourcesUnchanged': verification['upstreamSourcesUnchanged'],
}
(OUT / 'observations.json').write_text(json.dumps(observations, ensure_ascii=False, indent=2) + '\n')

def fence(text, language='text'):
    return '\n```' + language + '\n' + text.rstrip('\n') + '\n```\n'

sections = [
    '# 未知缺陷的本地 Workflow 实验\n',
    '本次使用真实 python-json-pointer 上游快照，commit `'+provenance['commit']+'`，源码版本 3.2.1。未植入缺陷、未提供缺陷数量或位置、没有隐藏正确性 oracle。提供原有源码、README、doc、tests.py 和 RFC 6901。jsonpointer.py 364 行、CLI 105 行、tests.py 616 行。上游文件前后哈希一致。\n',
    '结果：1 个 lead + 3 个 worker，共 4 个 Claude agents，上限 5。Lead 自己选择 3 个领域并行审计，之后根据 CLI worker 的结果做本地复现，没有再派 worker。首次结束后撤掉 runner 额外加入的单次 Workflow 限制，在同一个 lead session 继续；它仍选择自己验证，没有另一个 Workflow。该约束调整属于实验干预，不能把第二轮选择称为完全无干预的自发行为。\n',
    '**Lead 初始完整任务**\n'+fence((ROOT / 'task.txt').read_text()),
    '**约束调整的完整消息**\n'+fence((ROOT / 'continuation-task.txt').read_text()),
    '**Lead 完整 system / tool / attachment 记录**\n\n见 [system](export/lead/system.txt)、[全部 snapshots](export/lead/prompt-snapshots.json)、[工具定义](export/lead/tools.json)、[工具调用和结果](export/lead/tool-io.json)、[原始 lead transcript](capture/lead.jsonl)。首轮不可变备份位于 first-turn-capture/ 和 first-turn-export/。\n',
    '**Lead 生成的完整 Workflow**\n'+fence(workflow['script'], 'javascript'),
    '**Worker 公共 system chunks**\n'+fence('\n\n'.join(systems[0])) if same_system else '**各 worker system 不同，分别保存于对应 agent 目录。**\n',
]
for worker in verification['workers']:
    directory = OUT / worker['runId'] / worker['agentId']
    terminal = json.loads((directory / 'journal-terminal.json').read_text())
    tool_io = json.loads((directory / 'tool-io.json').read_text())
    structured = [c for c in tool_io if c['name'] == 'StructuredOutput']
    assert len(structured) == 1
    assert structured[0]['input'] == terminal[-1]['result']
    sections += [
        '**'+worker['label']+' / '+worker['agentId']+'**\n',
        '真实收到的完整任务（包含 harness framing）：\n'+fence((directory / 'incoming-task.txt').read_text()),
        '完整返回对象（等于 StructuredOutput input 和 journal result）：\n'+fence((directory / 'returned-result.json').read_text(), 'json'),
        '工具、环境和完整往返：['+worker['label']+' tool-io](export/'+worker['runId']+'/'+worker['agentId']+'/tool-io.json)、[工具 schema](export/'+worker['runId']+'/'+worker['agentId']+'/tools.json)、[全部 prompt snapshots](export/'+worker['runId']+'/'+worker['agentId']+'/prompt-snapshots.json)、[environment](export/'+worker['runId']+'/'+worker['agentId']+'/environment.json)。\n',
    ]

sections += [
    '**实际通信与共享**\n\nWorkflow 工具先返回 task ID / runId / scriptPath，VM 里的 parallel 等待三次 agent()。worker 各调用一次 StructuredOutput，结构化 input 与 journal.result 完全一致；parallel 按 AREAS 输入顺序收集，return 把结果包装成 {area,result} 数组。worker 完成次序为 class-api、cli、resolve-set；返回数组次序为 resolve-set、class-api、cli。\n\n完整 compact JSON 长 '+str(len(full))+' 字符，完成通知含截断标记并给出完整 .output 文件路径，不能将通知里的 result 直接当作完整 JSON。Lead 发现截断，尝试读取 .output：第一次按字符串切片解析失败，然后改用 json.load(file)[\'result\'] 成功取得全部领域的返回值。原始通知在 export/notification-wbgtfsaya.xml，完整输出在 capture/task-outputs/wbgtfsaya.output，队列记录在 export/lead/queue-operations.json。\n\nworker 环境快照 cwd 相同，isWorktree=false。共同读上游文件，各写独立 scratch 子目录。class-api 的 Bash 在 05:24:12.780 UTC 列出 scratch/cli（当时为空）和 scratch/lead 中的 d.json、e.txt、p.txt，这证明共享文件系统的可见性；没有记录到它读取这些文件内容。没有前序结果注入其他 worker prompt，没有后续 worker 的任务或文件交接。Lead 收到证据路径，但其复现使用自己新建的 scratch/lead 输入；续轮又写 scratch/lead2。\n',
    '**由 worker 结果触发的 lead 本地验证**\n',
]
for call in lead_calls:
    if call['name'] == 'Bash' and ('/a/- c.json' in str(call['input']) or 'scratch/lead2' in str(call['input'])):
        sections += ['时间：'+str(call['timestamp'])+'\n', fence(call['input']['command'], 'bash'), '原始工具输出：\n'+fence(str(call['response']['content']))]
sections += ['**首轮 lead 汇总原文**\n\n'+completions[0]['result']+'\n', '**同会话续轮 lead 汇总原文**\n\n'+completions[-1]['result']+'\n',
    '**独立核验及需要修正的表述**\n\nrunner 在 lead 两轮结束后独立运行，未把该结果反馈给 lead。显式选择 workspace/jsonpointer.py 后，上游 52 项测试全部通过；lead 无法运行 tests.py 是 -I / PYTHONPATH 引导方式的问题。CLI EndOfList 崩溃独立复现，且混合用例的第二个文件本来能成功解析，但在第一个文件报错后被跳过。Worker/lead 所称 json.dumps 位于 try 外不准确：该行在 try 内，except 仅处理 JsonPointerException，TypeError 未被捕获。其他 ambiguity/rejected 项并未全部独立复跑，保留为 worker 报告。\n\nLead 说“约 12 手工 probes”概括不足：class-api 还按六字符字母表枚举长度 0..5 的 9,331 个字符串，CLI worker 报告约 45 次调用。不是随机 fuzz。工作流记录 21 次 worker 工具调用、98,700 tokens、71.371 秒；两轮累计 CLI 标价估算 $0.878151，继承同一 cost state，不能把两轮 total_cost_usd 相加。\n',
    '**独立核验的完整记录**\n'+fence(json.dumps(independent, ensure_ascii=False, indent=2), 'json'),
    '**观测元数据**\n'+fence(json.dumps(observations, ensure_ascii=False, indent=2), 'json'),
    '**保留文件说明**\n\n原始 events/debug/stderr、lead 和三个 worker 的原生 transcripts、journal、Workflow 元数据及脚本、任务和约束调整消息、每个 agent 的 system chunks / prompt snapshots / tool schemas / messages / attachments / tool-io、完整 output、两轮结果、源码快照与来源、前后源文件哈希和 artifact-manifest 都在同一目录。全部记录也打包到上一级 unknown-content-probe-records.zip。所有路径是实验目录，Synergy 主 checkout 和 runtime 未改动。\n',
]
(ROOT / 'EXPERIMENT.md').write_text('\n'.join(sections))
manifest = [{'path': str(p.relative_to(ROOT)), 'bytes': p.stat().st_size, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(ROOT.rglob('*')) if p.is_file() and p.name != 'artifact-manifest.json']
(ROOT / 'artifact-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
archive = ROOT.parent / 'unknown-content-probe-records.zip'
with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
    for path in sorted(ROOT.rglob('*')):
        if path.is_file():
            z.write(path, str(path.relative_to(ROOT.parent)))
print(json.dumps({'reportBytes': (ROOT / 'EXPERIMENT.md').stat().st_size, 'artifactCount': len(manifest), 'zipBytes': archive.stat().st_size, 'statuses': dict(statuses), 'totalClaudeAgents': 1 + verification['workerAgents'], 'upstreamSourcesUnchanged': verification['upstreamSourcesUnchanged']}, ensure_ascii=False))
