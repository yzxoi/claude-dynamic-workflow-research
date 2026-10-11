import collections
import hashlib
import html
import json
from pathlib import Path
import re
import shutil

ROOT = Path(__file__).resolve().parent / 'unknown-content-probe'
OUT = ROOT / 'export'
CAP = ROOT / 'capture'
OUT.mkdir(exist_ok=True)
CAP.mkdir(exist_ok=True)
sid = (ROOT / 'session-id.txt').read_text().strip()
source = list(Path('/home/researcher/.claude/projects').glob('*/' + sid + '.jsonl'))
assert len(source) == 1
shutil.copy2(source[0], CAP / 'lead.jsonl')
shutil.copytree(source[0].parent / sid, CAP / 'session', dirs_exist_ok=True)

def rows(path):
    result = []
    for line in path.read_text().splitlines():
        if line.strip():
            try:
                result.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return result

def save_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

def items(row):
    value = row.get('message', {}).get('content', [])
    return [{'type': 'text', 'text': value}] if isinstance(value, str) else value or []

def export_thread(path, dest):
    dest.mkdir(exist_ok=True)
    data = rows(path)
    snapshots = [r['attachment'] for r in data if r.get('attachment', {}).get('type') == 'prompt_snapshot']
    save_json(dest / 'prompt-snapshots.json', snapshots)
    if snapshots:
        snapshot = snapshots[-1]
        save_json(dest / 'system-chunks.json', snapshot['systemPrompt'])
        (dest / 'system.txt').write_text('\n\n'.join(snapshot['systemPrompt']) + '\n')
        save_json(dest / 'tools.json', snapshot.get('tools', []))
    save_json(dest / 'messages.json', [r for r in data if r.get('type') in ('user', 'assistant')])
    save_json(dest / 'attachments.json', [r['attachment'] for r in data if r.get('type') == 'attachment' and r.get('attachment', {}).get('type') not in ('credential_org', 'session_context', 'prompt_snapshot')])
    incoming = next((c['text'] for r in data if r.get('type') == 'user' for c in items(r) if c.get('type') == 'text'), '')
    (dest / 'incoming-task.txt').write_text(incoming + '\n')
    if incoming.startswith('[Workflow harness'):
        frame, task = incoming.split('\n', 1)
        (dest / 'harness-frame.txt').write_text(frame + '\n')
        (dest / 'task.txt').write_text('\n'.join(l[2:] if l.startswith('  ') else l for l in task.splitlines()) + '\n')
    calls = []
    results = {}
    for r in data:
        for c in items(r):
            if c.get('type') == 'tool_use':
                calls.append({'timestamp': r.get('timestamp'), 'id': c.get('id'), 'name': c.get('name'), 'input': c.get('input')})
            if c.get('type') == 'tool_result':
                results[c.get('tool_use_id')] = {'timestamp': r.get('timestamp'), 'content': c.get('content'), 'is_error': c.get('is_error', False)}
    for call in calls:
        call['response'] = results.get(call['id'])
    save_json(dest / 'tool-io.json', calls)
    environment = [r['attachment']['snapshot'] for r in data if r.get('attachment', {}).get('type') == 'environment']
    save_json(dest / 'environment.json', environment)
    return data, calls

lead, lead_calls = export_thread(CAP / 'lead.jsonl', OUT / 'lead')
queue = [r for r in lead if r.get('type') == 'queue-operation']
save_json(OUT / 'lead/queue-operations.json', queue)
notifications = [r for r in queue if r.get('operation') == 'enqueue' and str(r.get('content', '')).startswith('<task-notification>')]
for notification in notifications:
    content = notification['content']
    task_id = content.split('<task-id>', 1)[1].split('</task-id>', 1)[0]
    (OUT / ('notification-' + task_id + '.xml')).write_text(content + '\n')
for r in lead:
    for c in items(r):
        if c.get('type') == 'text' and c['text'].startswith('# Workflow authoring reference'):
            (OUT / 'workflow-authoring-reference.txt').write_text(c['text'] + '\n')

all_workers = []
workflows = []
for path in sorted((CAP / 'session/workflows').glob('*.json')):
    workflow = json.loads(path.read_text())
    run_id = workflow['runId']
    dest = OUT / run_id
    dest.mkdir(exist_ok=True)
    save_json(dest / 'metadata.json', workflow)
    (dest / 'workflow.js').write_text(workflow['script'])
    script_name = Path(workflow['scriptPath']).name
    persisted = (CAP / 'session/workflows/scripts' / script_name).read_text()
    assert persisted == workflow['script']
    save_json(dest / 'result.json', workflow.get('result'))
    journal = rows(CAP / 'session/subagents/workflows' / run_id / 'journal.jsonl')
    save_json(dest / 'journal.json', journal)
    for start in [r for r in journal if r.get('type') == 'started']:
        aid = start['agentId']
        worker_dest = dest / aid
        data, calls = export_thread(CAP / 'session/subagents/workflows' / run_id / ('agent-' + aid + '.jsonl'), worker_dest)
        returned = [r for r in journal if r.get('agentId') == aid and r.get('type') in ('result', 'failed')]
        save_json(worker_dest / 'journal-terminal.json', returned)
        if returned and 'result' in returned[-1]:
            save_json(worker_dest / 'returned-result.json', returned[-1]['result'])
        progress = next((r for r in workflow.get('workflowProgress', []) if r.get('agentId') == aid), {})
        worker = {'runId': run_id, 'agentId': aid, 'label': start.get('label'), 'phase': start.get('phase'), 'startedAt': progress.get('startedAt'), 'durationMs': progress.get('durationMs'), 'attempt': progress.get('attempt'), 'state': progress.get('state'), 'toolCalls': len(calls), 'toolNames': [c['name'] for c in calls]}
        all_workers.append(worker)
    notice = next((n['content'] for n in notifications if '<task-id>' + workflow['taskId'] + '</task-id>' in n['content']), None)
    notification_matches = None
    if notice and '<result>' in notice:
        try:
            decoded = json.loads(html.unescape(notice.split('<result>', 1)[1].split('</result>', 1)[0]))
            notification_matches = decoded == workflow.get('result')
        except json.JSONDecodeError:
            notification_matches = False
    workflows.append({'runId': run_id, 'status': workflow.get('status'), 'agentCount': workflow.get('agentCount'), 'durationMs': workflow.get('durationMs'), 'notificationResultMatches': notification_matches, 'notificationTruncated': bool(notice and '... (truncated ' in notice)})

events = rows(ROOT / 'events.jsonl')
if (ROOT / 'continuation-events.jsonl').exists():
    events += rows(ROOT / 'continuation-events.jsonl')
completions = [r for r in events if r.get('type') == 'result']
save_json(OUT / 'completions.json', completions)
if completions:
    (OUT / 'lead-final.md').write_text(completions[-1].get('result', '') + '\n')
before = json.loads((ROOT / 'source-manifest-before.json').read_text())
after = []
for record in before:
    path = ROOT / 'workspace' / record['path']
    after.append({'path': record['path'], 'bytes': path.stat().st_size if path.exists() else None, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None})
save_json(ROOT / 'source-manifest-after.json', after)
summary = {'sessionId': sid, 'provenance': json.loads((ROOT / 'provenance.json').read_text()), 'workflowCalls': len([c for c in lead_calls if c['name'] == 'Workflow']), 'workflows': workflows, 'leadAgents': 1, 'workerAgents': len(all_workers), 'uniqueWorkerIds': len({w['agentId'] for w in all_workers}), 'withinFiveAgentLimit': len(all_workers) <= 4, 'workers': all_workers, 'upstreamSourcesUnchanged': before == after, 'extraWorkspaceFiles': sorted(str(f.relative_to(ROOT / 'workspace')) for f in (ROOT / 'workspace').rglob('*') if f.is_file() and str(f.relative_to(ROOT / 'workspace')) not in {r['path'] for r in before}), 'complete': bool(completions), 'totalCostUsdListEstimate': completions[-1].get('total_cost_usd') if completions else None}
save_json(OUT / 'verification.json', summary)
save_json(ROOT / 'artifact-manifest.json', [{'path': str(p.relative_to(ROOT)), 'bytes': p.stat().st_size, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(ROOT.rglob('*')) if p.is_file() and p.name != 'artifact-manifest.json'])
print(json.dumps({k:v for k,v in summary.items() if k not in ('workers','provenance','extraWorkspaceFiles')}, ensure_ascii=False, indent=2))
