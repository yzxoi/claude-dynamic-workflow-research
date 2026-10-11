import argparse
import json
import os
import subprocess
import urllib.parse
import urllib.request
from pathlib import Path

parser = argparse.ArgumentParser(description='Read an existing Managed Agents workflow; Managed Agents calls use GET only and do not start any agent. Authentication is explicit API key or delegated to the official ant CLI.')
parser.add_argument('session_id')
parser.add_argument('--workflow-run-id')
parser.add_argument('--thread-limit', type=int, default=8)
parser.add_argument('--max-pages', type=int, default=100)
parser.add_argument('--output', type=Path, required=True)
parser.add_argument('--ant-cli', type=Path, help='Use this official ant binary to obtain a bearer token in memory; never prints or saves the token.')
parser.add_argument('--profile', default='workflow-research')
args = parser.parse_args()
if args.thread_limit < 1 or args.max_pages < 1:
    parser.error('limits must be positive')
headers = {'anthropic-version': '2023-06-01', 'anthropic-beta': 'managed-agents-2026-04-01'}
if args.ant_cli:
    process = subprocess.run([str(args.ant_cli.resolve()), '--profile', args.profile, 'auth', 'print-credentials', '--access-token'], capture_output=True, text=True, timeout=60)
    if process.returncode:
        parser.error('Official ant CLI could not supply an access token; use ant auth login to repair authentication. Credential output is intentionally omitted.')
    token = process.stdout.strip()
    if not token or any(character.isspace() for character in token):
        parser.error('Official ant CLI returned an unexpected token format. Output is intentionally omitted.')
    headers['authorization'] = 'Bearer ' + token
else:
    key = os.environ.get('ANTHROPIC_API_KEY')
    if not key:
        parser.error('Set ANTHROPIC_API_KEY explicitly or pass --ant-cli. This script does not read credential stores itself.')
    headers['x-api-key'] = key

def get(path, query=None):
    url = 'https://api.anthropic.com' + path + '?' + urllib.parse.urlencode({'beta': 'true', **(query or {})})
    request = urllib.request.Request(url, headers=headers, method='GET')
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)

def pages(path):
    data = []
    cursor = None
    for _ in range(args.max_pages):
        result = get(path, {'page': cursor} if cursor else {})
        data.extend(result.get('data', []))
        cursor = result.get('next_page')
        if not cursor:
            return {'data': data, 'complete': True}
    return {'data': data, 'complete': False, 'next_page': cursor}

session = urllib.parse.quote(args.session_id, safe='')
base = '/v1/sessions/' + session
threads = pages(base + '/threads')
selected = [t for t in threads['data'] if t.get('workflow_run_id') and (not args.workflow_run_id or t['workflow_run_id'] == args.workflow_run_id)]
events = pages(base + '/events')
captured = []
for thread in selected[:args.thread_limit]:
    thread_id = urllib.parse.quote(thread['id'], safe='')
    metadata = get(base + '/threads/' + thread_id)
    history = pages(base + '/threads/' + thread_id + '/events')
    captured.append({'thread': metadata, 'events': history})
output = {'method': 'GET-only Managed Agents capture of an existing session; no workflow creation or model invocation; authentication is explicit API key or official ant CLI, never included in output', 'threads_inventory': threads, 'workflow_events': [e for e in events['data'] if e.get('type', '').startswith('workflow_run.') and (not args.workflow_run_id or e.get('workflow_run_id') == args.workflow_run_id)], 'session_event_inventory_complete': events['complete'], 'selected_thread_count': len(selected), 'captured_threads': captured, 'coverage': 'selected thread sample; inline agent.system is the program-defined prompt, not proof of the complete private server harness prompt'}
args.output.parent.mkdir(parents=True, exist_ok=True)
args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2))
print(json.dumps({'output': str(args.output), 'selected_threads': len(selected), 'captured_threads': len(captured)}))
