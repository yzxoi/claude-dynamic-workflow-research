from pathlib import Path
import os
import json
import subprocess
import time
import signal
import threading

ROOT = Path(__file__).resolve().parent
RUN = ROOT / 'bug-hunt-probe'
WORK = RUN / 'workspace'
CLI = ROOT / 'native-latest/package/claude'
env = dict(os.environ)
env.update({'DISABLE_AUTOUPDATER': '1', 'CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC': '1', 'CLAUDE_CODE_SUBAGENT_PROMPT_SNAPSHOT': '1', 'CLAUDE_CODE_WORKFLOW_MAX_CONCURRENT_AGENTS': '4', 'PYTHONDONTWRITEBYTECODE': '1'})
args = [str(CLI), '--print', '--verbose', '--output-format', 'stream-json', '--safe-mode', '--restricted', '--strict-mcp-config', '--mcp-config', '{"mcpServers":{}}', '--settings', str(RUN / 'settings.json'), '--tools', 'Workflow,Skill,Read,Glob,Grep,Write,Bash', '--allowedTools', 'Workflow,Skill,Read,Glob,Grep,Write,Bash(python3 *)', '--model', 'sonnet', '--effort', 'medium', '--max-budget-usd', '2', '--session-id', (RUN / 'session-id.txt').read_text(), '--system-prompt-snapshot', 'on', '--debug-file', str(RUN / 'debug.log')]
(RUN / 'launch.json').write_text(json.dumps({'args': args, 'cwd': str(WORK), 'environment_overrides': {k: env[k] for k in ('DISABLE_AUTOUPDATER', 'CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC', 'CLAUDE_CODE_SUBAGENT_PROMPT_SNAPSHOT', 'CLAUDE_CODE_WORKFLOW_MAX_CONCURRENT_AGENTS', 'PYTHONDONTWRITEBYTECODE')}, 'wall_timeout_seconds': 300}, indent=2))
with (RUN / 'task.txt').open() as source, (RUN / 'events.jsonl').open('w') as output, (RUN / 'stderr.log').open('w') as errors:
    process = subprocess.Popen(args, cwd=WORK, env=env, stdin=source, stdout=output, stderr=errors, start_new_session=True)
    try:
        return_code = process.wait(timeout=300)
        status = 'completed'
    except subprocess.TimeoutExpired:
        status = 'wall_timeout'
        os.killpg(process.pid, signal.SIGINT)
        try:
            return_code = process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGTERM)
            return_code = process.wait(timeout=10)
(RUN / 'process-result.json').write_text(json.dumps({'exit_code': return_code, 'status': status}, indent=2))
print(json.dumps({'exit_code': return_code, 'status': status, 'session_id': (RUN / 'session-id.txt').read_text()}), flush=True)
