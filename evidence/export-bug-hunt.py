import collections
import hashlib
import html
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent / 'bug-hunt-probe'
OUT = ROOT / 'export'
OUT.mkdir(exist_ok=True)
CAP = ROOT / 'capture'
RUN = 'wf_19ca15dc-a9c'

def rows(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]

def save_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

def content_items(row):
    value = row.get('message', {}).get('content', [])
    return [{'type': 'text', 'text': value}] if isinstance(value, str) else value or []

def export_thread(path, dest):
    dest.mkdir(exist_ok=True)
    data = rows(path)
    snapshots = [r['attachment'] for r in data if r.get('attachment', {}).get('type') == 'prompt_snapshot']
    save_json(dest / 'prompt-snapshots.json', snapshots)
    final_snapshot = snapshots[-1]
    save_json(dest / 'system-chunks.json', final_snapshot['systemPrompt'])
    (dest / 'system.txt').write_text('\n\n'.join(final_snapshot['systemPrompt']) + '\n')
    save_json(dest / 'tools.json', final_snapshot.get('tools', []))
    save_json(dest / 'messages.json', [r for r in data if r.get('type') in ('user', 'assistant')])
    save_json(dest / 'attachments.json', [r['attachment'] for r in data if r.get('attachment', {}).get('type') not in ('credential_org', 'session_context', 'prompt_snapshot') and r.get('type') == 'attachment'])
    incoming = next(c['text'] for r in data if r.get('type') == 'user' for c in content_items(r) if c.get('type') == 'text')
    (dest / 'incoming-task.txt').write_text(incoming + '\n')
    calls = []
    results = {}
    for r in data:
        for c in content_items(r):
            if c.get('type') == 'tool_use':
                calls.append({'timestamp': r.get('timestamp'), 'id': c.get('id'), 'name': c.get('name'), 'input': c.get('input')})
            elif c.get('type') == 'tool_result':
                results[c.get('tool_use_id')] = {'timestamp': r.get('timestamp'), 'content': c.get('content'), 'is_error': c.get('is_error', False)}
    for c in calls:
        c['response'] = results.get(c['id'])
    save_json(dest / 'tool-io.json', calls)
    return data, incoming, final_snapshot, calls

lead, lead_task, lead_snapshot, lead_calls = export_thread(CAP / 'lead.jsonl', OUT / 'lead')
queue = [r for r in lead if r.get('type') == 'queue-operation']
save_json(OUT / 'lead/queue-operations.json', queue)
notifications = [r for r in queue if r.get('operation') == 'enqueue' and str(r.get('content', '')).startswith('<task-notification>')]
for notification in notifications:
    text = notification['content']
    task_id = text.split('<task-id>', 1)[1].split('</task-id>', 1)[0]
    (OUT / ('notification-' + task_id + '.xml')).write_text(text + '\n')
authoring = next(c['text'] for r in lead if r.get('type') == 'user' for c in content_items(r) if c.get('type') == 'text' and c['text'].startswith('# Workflow authoring reference'))
(OUT / 'workflow-authoring-reference.txt').write_text(authoring + '\n')
workflow = json.loads((CAP / 'session/workflows' / (RUN + '.json')).read_text())
persisted = (CAP / 'session/workflows/scripts' / ('audit-utils-' + RUN + '.js')).read_text()
assert persisted == workflow['script']
sent = [c['input']['script'] for c in lead_calls if c['name'] == 'Workflow' and 'script' in c['input']]
assert persisted == sent[0]
(OUT / 'workflow.js').write_text(persisted)
(ROOT / 'generated-workflow-from-events.js').write_text(persisted)
save_json(OUT / 'workflow-metadata.json', workflow)
save_json(OUT / 'workflow-result.json', workflow['result'])
audit_notice = next(n['content'] for n in notifications if '<task-id>' + workflow['taskId'] + '</task-id>' in n['content'])
notice_result = json.loads(html.unescape(audit_notice.split('<result>', 1)[1].split('</result>', 1)[0]))
assert notice_result == workflow['result']
journal = rows(CAP / 'session/subagents/workflows' / RUN / 'journal.jsonl')
save_json(OUT / 'journal.json', journal)
started = [r for r in journal if r['type'] == 'started']
returned = {r['agentId']: r['result'] for r in journal if r['type'] == 'result'}
workers = []
systems = []
for n, start in enumerate(started, 1):
    module = start['label'].split(':', 1)[1]
    directory = OUT / module
    data, incoming, snapshot, calls = export_thread(CAP / 'session/subagents/workflows' / RUN / ('agent-' + start['agentId'] + '.jsonl'), directory)
    frame, task = incoming.split('\n', 1)
    task = '\n'.join(line[2:] if line.startswith('  ') else line for line in task.splitlines())
    (directory / 'task.txt').write_text(task + '\n')
    (OUT / 'harness-frame.txt').write_text(frame + '\n')
    save_json(directory / 'returned-result.json', returned[start['agentId']])
    structured = [c for c in calls if c['name'] == 'StructuredOutput']
    assert len(structured) == 1 and structured[0]['input'] == returned[start['agentId']]
    bash = [c for c in calls if c['name'] == 'Bash']
    assert len(bash) == 1
    (directory / 'original-stdout.txt').write_text(bash[0]['response']['content'] + '\n')
    progress = next(r for r in workflow['workflowProgress'] if r.get('agentId') == start['agentId'])
    workers.append({'module': module, 'agentId': start['agentId'], 'label': start['label'], 'durationMs': progress['durationMs'], 'startedAt': progress['startedAt'], 'attempt': progress['attempt'], 'tools': [c['name'] for c in calls], 'statuses': dict(collections.Counter(f['status'] for f in returned[start['agentId']]['findings'])), 'timestamps': [r['timestamp'] for r in data if r.get('timestamp')]})
    systems.append(snapshot['systemPrompt'])
assert all(s == systems[0] for s in systems)
(OUT / 'common-worker-system.txt').write_text('\n\n'.join(systems[0]) + '\n')
save_json(OUT / 'common-worker-system-chunks.json', systems[0])

events = rows(ROOT / 'events.jsonl')
final = [e for e in events if e.get('type') == 'result'][-1]
(OUT / 'lead-final.md').write_text(final['result'] + '\n')
save_json(OUT / 'completion.json', final)
before = json.loads((ROOT / 'source-manifest-before.json').read_text())
after = []
for entry in before:
    path = ROOT / 'workspace' / entry['path']
    after.append({**entry, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
save_json(ROOT / 'source-manifest-after.json', after)
assert before == after

proofs = []
env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
for path in sorted((ROOT / 'workspace/scratch').glob('*.py')):
    result = subprocess.run(['python3', '-I', str(path)], cwd=ROOT / 'workspace', env=env, capture_output=True, text=True, timeout=15)
    proofs.append({'script': str(path), 'returncode': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr})
assert all(p['returncode'] == 0 for p in proofs)
save_json(OUT / 'independent-proof-reruns.json', proofs)
status_counts = collections.Counter(f['status'] for result in workflow['result'] for f in result['findings'])
summary = {'auditRunId': RUN, 'sessionId': (ROOT / 'session-id.txt').read_text().strip(), 'workflowCalls': len(sent), 'workflowCallAgents': [json.loads(p.read_text())['agentCount'] for p in sorted((CAP / 'session/workflows').glob('*.json'))], 'leadAgents': 1, 'workerAgents': len(started), 'uniqueWorkerIds': len({s['agentId'] for s in started}), 'failedJournalEntries': sum(r['type'] == 'failed' for r in journal), 'sourcesUnchanged': before == after, 'originalScriptMatchesPayloadAndMetadata': True, 'workerSystemIdentical': True, 'workers': workers, 'workerFindingStatuses': dict(status_counts), 'auditDurationMs': workflow['durationMs'], 'auditTokensReported': workflow['totalTokens'], 'auditToolCalls': workflow['totalToolCalls'], 'totalCostUsdListEstimate': final['total_cost_usd'], 'modelUsage': final['modelUsage'], 'cliDurationApiMs': final['duration_api_ms'], 'leadPermissionDenials': final['permission_denials'], 'knownSeededBugs': 5, 'leadConfirmedSeededBugs': 5, 'extraRuntimePrecisionFinding': True, 'oneWorkflowInstructionSatisfied': False}
save_json(OUT / 'verification.json', summary)

sections = [
    '# Local autonomous bug-hunting experiment\n',
    'This is a local Claude Code Workflow observation, not a cloud multiagent_20261001 run. The benchmark is a 91-line artificial package with five known defects. The lead did not receive the defect count or locations. It chose the modules, phase, worker prompts, schema and verification method.\n',
    'Actual count: one lead plus four workers. Audit run: '+RUN+'. There was also an accidental zero-worker noop run; the one-Workflow instruction was violated, but the five-agent limit held.\n',
    '**Task given to the lead**\n\n```text\n'+lead_task+'\n```\n',
    '**Generated workflow (original bytes)**\n\n```javascript\n'+persisted+'\n```\n',
    '**Common worker system prompt (snapshot chunks joined by blank lines)**\n\n```text\n'+'\n\n'.join(systems[0])+'\n```\n',
    '**Harness framing**\n\n```text\n'+(OUT / 'harness-frame.txt').read_text()+'```\n',
]
for w in workers:
    d = OUT / w['module']
    sections += ['**Worker '+w['label']+' / '+w['agentId']+'**\n', 'Task sent to agent():\n\n```text\n'+(d / 'task.txt').read_text()+'```\n', 'Runtime stdout (original transcript):\n\n```text\n'+(d / 'original-stdout.txt').read_text()+'```\n', 'Returned value (validated StructuredOutput input; also exact journal result):\n\n```json\n'+(d / 'returned-result.json').read_text()+'```\n']
sections += ['**Lead final answer (verbatim)**\n\n'+final['result']+'\n', '**Post-run audit notes**\n\nAll five planted defects have runtime reproductions. All six proof scripts were independently re-run with exit code 0; the unchanged source hashes match the initial manifest. Worker confirmed status occurred six times, including the extra floating-point cancellation repro. The lead downgraded that extra finding, which is a lead judgment rather than a schema validation result. Zero-minimum pricing was executed but labeled unverified despite no observable contradiction; it is not an additional confirmed defect. Scheduling worker and lead claimed the empty merge case was tested, but no merge_overlaps([]) call exists in the recorded proof scripts. Percentile descriptions claiming all unclamped p are wrong overstate the result (p=0 works and repeated data can mask the off-by-one). No separate verifier worker or cross-module phase was run. There were no permission denials in the final result. The restrictions in task.txt were behavioral instructions; executed Bash commands also included mkdir, cat, wc, sleep, and own workflow-log reads.\n', '**Communication observed**\n\nEach worker got a fresh task plus common system/context attachments. All four environment snapshots point to the same workspace and are not worktrees. Each worker read its module and the entire SPEC.md and wrote a distinct proof file. No worker read another worker file or received another worker result. Each called StructuredOutput once. The validated object became the agent() resolved value and a journal result. parallel gathered objects in input module order, and return res became workflow metadata.result. The workflow completion was a task_notification to the lead; the lead also read the journal with Bash. The lead performed one proof before receiving worker results and a second proof after reading them, then summarized and changed the severity of one claim.\n', '**Verification metadata**\n\n```json\n'+json.dumps(summary, ensure_ascii=False, indent=2)+'\n```\n']
sections += ['**Notification payload verification**\n\nThe lead queue contains the complete task-notification XML, including an HTML-escaped JSON result array inline. Decoding its result reproduces workflow metadata.result exactly. See export/notification-wag1wflr2.xml and export/lead/queue-operations.json. The audited workflow notification was enqueued at 2026-10-11T05:09:41.603Z and absorbed at 2026-10-11T05:11:03.227Z after the lead Bash wait. Pricing input nonmutation claims also had no explicit before/after assertion in the proof script; they should be classified as code observations rather than executed mutation tests.\n']
(ROOT / 'EXPERIMENT.md').write_text('\n'.join(sections))
files = []
for path in sorted(ROOT.rglob('*')):
    if path.is_file() and path.name != 'artifact-manifest.json':
        files.append({'path': str(path.relative_to(ROOT)), 'bytes': path.stat().st_size, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
save_json(ROOT / 'artifact-manifest.json', files)
print(json.dumps({k:v for k,v in summary.items() if k not in ('workers','modelUsage')}, ensure_ascii=False, indent=2))
print('report bytes', (ROOT / 'EXPERIMENT.md').stat().st_size, 'artifacts',len(files))
