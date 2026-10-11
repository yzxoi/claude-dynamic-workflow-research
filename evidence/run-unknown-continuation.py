from pathlib import Path
import datetime
import json
import os
import signal
import subprocess
import time

ROOT = Path(__file__).resolve().parent
RUN = ROOT / 'unknown-content-probe'
first = json.loads((RUN / 'process-result.json').read_text())
assert first['status'] == 'completed' and first['exit_code'] == 0
original = json.loads((RUN / 'launch.json').read_text())
args = original['args'][:]
i = args.index('--session-id')
args[i:i+2] = ['--resume', (RUN / 'session-id.txt').read_text().strip()]
i = args.index('--debug-file')
args[i+1] = str(RUN / 'continuation-debug.log')
env = dict(os.environ)
env.update(original['environment_overrides'])
start = time.monotonic()
started = datetime.datetime.now(datetime.timezone.utc).isoformat()
(RUN / 'continuation-launch.json').write_text(json.dumps({'args': args, 'cwd': original['cwd'], 'environment_overrides': original['environment_overrides'], 'started_at': started, 'wall_timeout_seconds': 240, 'reason': 'Remove runner-added one-Workflow constraint; same lead session, one remaining worker'}, indent=2) + '\n')
with (RUN / 'continuation-task.txt').open() as source, (RUN / 'continuation-events.jsonl').open('w') as output, (RUN / 'continuation-stderr.log').open('w') as errors:
    process = subprocess.Popen(args, cwd=original['cwd'], env=env, stdin=source, stdout=output, stderr=errors, start_new_session=True)
    try:
        code = process.wait(timeout=240)
        status = 'completed'
    except subprocess.TimeoutExpired:
        status = 'wall_timeout'
        os.killpg(process.pid, signal.SIGINT)
        try:
            code = process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGTERM)
            code = process.wait(timeout=10)
result = {'status': status, 'exit_code': code, 'started_at': started, 'finished_at': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'duration_seconds': time.monotonic() - start}
(RUN / 'continuation-process-result.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result), flush=True)
