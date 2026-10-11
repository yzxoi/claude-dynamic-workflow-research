from pathlib import Path
import subprocess
import json
import sys

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'cloud-probe'
ANT = ROOT / 'tools/ant-1.40.0/ant'

def call(name, args):
    process = subprocess.run([str(ANT), '--profile', 'workflow-research', '--format', 'json', '--format-error', 'json', *args], capture_output=True, text=True, timeout=60)
    output = process.stdout or process.stderr
    (OUT / (name + '.json')).write_text(output)
    try:
        value = json.loads(output)
    except json.JSONDecodeError:
        print(json.dumps({'step': name, 'exit_code': process.returncode, 'error': output[:1000]}))
        sys.exit(1)
    if process.returncode:
        print(json.dumps({'step': name, 'exit_code': process.returncode, 'error': value.get('error', value)}))
        sys.exit(1)
    print(json.dumps({'step': name, 'type': value.get('type'), 'id': value.get('id'), 'status': value.get('status')}))
    return value

def flag(value):
    return json.dumps(value, separators=(',', ':'))

system = 'You carry out tiny orchestration diagnostics. For the requested experiment use one dynamic workflow and at most three inline worker invocations. Preserve the exact program for inspection. Read and write only the experiment files under /mnt/session/work and /mnt/session/outputs. No network, installations, shell commands, or additional workflows. Never invent missing return values or runtime details.'
task = '''Run one tiny dynamic workflow as an orchestration diagnostic. Use exactly three step.agent calls, inline define agents, and no subagent calls, advisor, nested run, retries, or fourth agent. Set a two-minute lifetime for the run. Omit model and tools from every define so they inherit according to the workflow engine. Every worker's system must tell it to work only on this diagnostic and return concise JSON.
LEAD_ONLY value: lead-context-probe-cloud-638741. Do not include that value in any worker system, task, program, files, or returned A/B objects. Workers should report leadOnlyValue null unless the actual value is independently already visible in their incoming context; do not ask a worker to retrieve lead history.
First write /mnt/session/work/seed.txt containing exactly workspace-shared-cloud-2147.
Phase Observe: start A and B concurrently. A reads seed.txt and writes /mnt/session/work/artifact-a.txt containing exactly artifact-cloud-A-93317. A returns {worker:"A",seed:<contents>,leadOnlyValue:<value or null>}. B reads seed.txt and returns {worker:"B",seed:<contents>,leadOnlyValue:<value or null>}.
Phase Merge: after both complete, C receives the exact A/B return objects explicitly in its task, reads artifact-a.txt, and returns {receivedA:<object>,receivedB:<object>,artifactContents:<contents>,leadOnlyValue:<value or null>}.
The program should return A/B/C results. Keep every worker answer below 150 words. Worker failure should be recorded, never silently replaced with invented data. Open phases only at top level. Before launching, write the exact original executable workflow program you will submit (unmodified, not a prose approximation) to /mnt/session/outputs/workflow-program.js. Include all inline systems and any schemas in that program. End the turn once launched. If workflow functionality is unavailable, report the precise error and stop; do not substitute a roster experiment.'''
(OUT / 'lead-system.txt').write_text(system)
(OUT / 'task.txt').write_text(task)
multiagent = {'type': 'multiagent_20261001', 'workflows': {'type': 'enabled'}, 'subagents': {'type': 'disabled'}, 'advisor': {'type': 'disabled'}}
tool = {'type': 'agent_toolset_20260401', 'default_config': {'enabled': False}, 'configs': [{'name': 'read', 'enabled': True}, {'name': 'write', 'enabled': True}]}
agent = call('agent-created', ['beta:agents', 'create', '--name', 'Workflow research three-worker probe', '--model', flag({'id': 'claude-sonnet-5-5', 'effort': 'low'}), '--system', system, '--multiagent', flag(multiagent), '--tool', flag(tool), '--metadata', flag({'purpose': 'bounded-workflow-diagnostic'})])
environment = call('environment-created', ['beta:environments', 'create', '--name', 'Workflow research isolated sandbox', '--config', flag({'type': 'cloud', 'networking': {'type': 'limited', 'allow_mcp_servers': False, 'allow_package_managers': False, 'allowed_hosts': []}})])
session = call('session-created', ['beta:sessions', 'create', '--agent', agent['id'], '--environment-id', environment['id'], '--title', 'Bounded three-worker workflow diagnostic', '--budget', flag({'type': 'limit', 'max_list_cost': {'amount': '150', 'currency': 'USD'}}), '--initial-event', flag({'type': 'user.message', 'content': [{'type': 'text', 'text': task}]})])
(OUT / 'ids.json').write_text(json.dumps({'agent_id': agent['id'], 'environment_id': environment['id'], 'session_id': session['id']}, indent=2))
