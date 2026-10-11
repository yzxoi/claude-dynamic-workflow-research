from pathlib import Path
import json
import hashlib

ROOT = Path(__file__).resolve().parent
LIVE = ROOT / 'live-probe'
OUT = LIVE / 'prompts'
OUT.mkdir(exist_ok=True)
manifest = []

def save(name, value, source, representation):
    body = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, indent=2) + '\n'
    path = OUT / name
    path.write_text(body)
    manifest.append({'path': str(path.relative_to(ROOT)), 'source': str(source.relative_to(ROOT)), 'representation': representation, 'bytes': len(body.encode()), 'sha256': hashlib.sha256(body.encode()).hexdigest()})

journal_path = next((LIVE / 'capture' / 'session').rglob('journal.jsonl'))
journal = [json.loads(line) for line in journal_path.read_text().splitlines()]
labels = {row['agentId']: row['label'] for row in journal if row['type'] == 'started'}
paths = [LIVE / 'capture' / 'lead.jsonl', *sorted((LIVE / 'capture' / 'session').rglob('agent-*.jsonl'))]
agents = []
for path in paths:
    name = 'lead' if path.name == 'lead.jsonl' else labels[path.stem.removeprefix('agent-')]
    rows = [json.loads(line) for line in path.read_text().splitlines()]
    snapshots = [row['attachment'] for row in rows if row.get('type') == 'attachment' and row.get('attachment', {}).get('type') == 'prompt_snapshot']
    snapshot = snapshots[-1]
    save(name + '-system.json', snapshot['systemPrompt'], path, 'exact-recorded-system-chunk-array')
    save(name + '-system.txt', '\n\n'.join(snapshot['systemPrompt']) + '\n', path, 'recorded-system-chunks-joined-for-reading')
    save(name + '-tools.json', snapshot['tools'], path, 'exact-recorded-tool-definitions')
    save(name + '-snapshot.json', snapshot, path, 'exact-last-recorded-prompt-snapshot')
    messages = [{k: row.get(k) for k in ('type', 'timestamp', 'message')} for row in rows if row.get('type') in ('user', 'assistant')]
    save(name + '-messages.json', messages, path, 'recorded-task-messages-without-unrelated-attachments')
    first = next(row['message']['content'] for row in messages if row['type'] == 'user')
    task = first if isinstance(first, str) else '\n\n'.join(block['text'] for block in first if block.get('type') == 'text')
    save(name + '-incoming-task.txt', task + '\n', path, 'exact-first-user-message-text')
    agents.append({'role': name, 'system_chunk_lengths': [len(x.encode()) for x in snapshot['systemPrompt']], 'tools': [tool['name'] for tool in snapshot['tools']], 'incoming_task_has_lead_nonce': 'lead-context-probe-927463' in task, 'incoming_task_has_artifact_value': 'artifact-A-85192' in task, 'messages': len(messages)})

events = [json.loads(line) for line in (LIVE / 'events.jsonl').read_text().splitlines()]
result = [event for event in events if event.get('type') == 'result'][-1]
summary = {'scope': 'Claude Code local Workflow, not Managed Agents', 'cli_version': '2.1.296', 'model': list(result['modelUsage']), 'result': {key: result.get(key) for key in ('subtype', 'is_error', 'total_cost_usd', 'usage', 'modelUsage', 'subagent_stats')}, 'agents': agents, 'journal': journal, 'limitations': ['Snapshots record system chunks and tool definitions; message rendering, transient headers and exact wire/cache layout are not asserted.', 'Print-mode incoming worker tasks lack the lead-only nonce; interactive trusted-human request relay is a separate source path.', 'List-price cost estimate is not proof of a cash charge on a subscription.', 'These worker systems are local harness captures, not private Managed Agents systems.']}
(LIVE / 'prompt-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
(LIVE / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'exported_files': len(manifest), 'bytes': sum(x['bytes'] for x in manifest), 'agents': agents, 'total_cost_usd': result.get('total_cost_usd')}, ensure_ascii=False))
