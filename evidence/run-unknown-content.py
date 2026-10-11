from pathlib import Path
import datetime
import json
import os
import signal
import subprocess
import time

ROOT = Path(__file__).resolve().parent
RUN = ROOT / 'unknown-content-probe'
WORK = RUN / 'workspace'
CLI = ROOT / 'native-latest/package/claude'
env = dict(os.environ)
overrides = {'DISABLE_AUTOUPDATER': '1', 'CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC': '1', 'CLAUDE_CODE_SUBAGENT_PROMPT_SNAPSHOT': '1', 'CLAUDE_CODE_WORKFLOW_MAX_CONCURRENT_AGENTS': '4', 'PYTHONDONTWRITEBYTECODE': '1'}
env.update(overrides)
sid = (RUN / 'session-id.txt').read_text().strip()
args = [str(CLI), '--print', '--verbose', '--output-format', 'stream-json', '--safe-mode', '--restricted', '--strict-mcp-config', '--mcp-config', '{"mcpServers":{}}', '--settings', str(RUN / 'settings.json'), '--tools', 'Workflow,Skill,Read,Glob,Grep,Write,Bash', '--allowedTools', 'Workflow,Skill,Read,Glob,Grep,Write,Bash', '--model', 'sonnet', '--effort', 'high', '--max-budget-usd', '3', '--session-id', sid, '--system-prompt-snapshot', 'on', '--debug-file', str(RUN / 'debug.log')]
started = datetime.datetime.now(datetime.timezone.utc).isoformat()
start_clock = time.monotonic()
(RUN / 'launch.json').write_text(json.dumps({'args': args, 'cwd': str(WORK), 'environment_overrides': overrides, 'wall_timeout_seconds': 420, 'started_at': started}, indent=2) + '\n')
with (RUN / 'task.txt').open() as source, (RUN / 'events.jsonl').open('w') as output, (RUN / 'stderr.log').open('w') as errors:
    process = subprocess.Popen(args, cwd=WORK, env=env, stdin=source, stdout=output, stderr=errors, start_new_session=True)
    try:
        return_code = process.wait(timeout=420)
        status = 'completed'
    except subprocess.TimeoutExpired:
        status = 'wall_timeout'
        os.killpg(process.pid, signal.SIGINT)
        try:
            return_code = process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGTERM)
            return_code = process.wait(timeout=10)
result = {'exit_code': return_code, 'status': status, 'session_id': sid, 'duration_seconds': time.monotonic() - start_clock, 'started_at': started, 'finished_at': datetime.datetime.now(datetime.timezone.utc).isoformat()}
(RUN / 'process-result.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result), flush=True)
