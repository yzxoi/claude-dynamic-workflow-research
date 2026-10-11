import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent / 'unknown-content-probe'
WORK = ROOT / 'workspace'
PROOFS = WORK / 'scratch/post-run-independent'
PROOFS.mkdir(exist_ok=True)
sys.path.insert(0, str(WORK))
import jsonpointer
import tests

assert Path(jsonpointer.__file__).resolve() == (WORK / 'jsonpointer.py').resolve()
tempfile.tempdir = str(PROOFS)
test_output = io.StringIO()
test_stdout = io.StringIO()
suite = unittest.defaultTestLoader.loadTestsFromModule(tests)
with contextlib.redirect_stdout(test_stdout):
    result = unittest.TextTestRunner(stream=test_output, verbosity=1).run(suite)

env = dict(os.environ, PYTHONPATH=str(WORK), PYTHONDONTWRITEBYTECODE='1')
with tempfile.TemporaryDirectory(dir=PROOFS) as directory:
    cwd = Path(directory)
    (cwd / 'first.json').write_text('{"a":[1]}')
    (cwd / 'second.json').write_text('{"a":{"-":"second-file-marker"}}')
    cases = []
    for label, args in [('mixed', ['/a/-', 'first.json', 'second.json']), ('second-only', ['/a/-', 'second.json']), ('control', ['/a/9', 'first.json', 'second.json'])]:
        command = ['python3', str(WORK / 'bin/jsonpointer'), *args]
        completed = subprocess.run(command, cwd=cwd, env=env, text=True, capture_output=True, timeout=15)
        cases.append({'label': label, 'command': command, 'returncode': completed.returncode, 'stdout': completed.stdout, 'stderr': completed.stderr})

assert result.wasSuccessful()
mixed, second, control = cases
assert mixed['returncode'] == 1 and mixed['stdout'] == '' and 'TypeError: Object of type EndOfList is not JSON serializable' in mixed['stderr']
assert second['returncode'] == 0 and second['stdout'].strip() == '"second-file-marker"'
assert control['returncode'] == 1 and control['stderr'].count('Could not resolve pointer:') == 2
record = {'kind': 'post-run independent verification by the experiment runner', 'receivedByLead': False, 'moduleOrigin': jsonpointer.__file__, 'upstreamVersion': jsonpointer.__version__, 'upstreamTests': {'testsRun': result.testsRun, 'failures': len(result.failures), 'errors': len(result.errors), 'skipped': len(result.skipped), 'successful': result.wasSuccessful(), 'stderr': test_output.getvalue(), 'stdout': test_stdout.getvalue()}, 'cliCases': cases, 'conclusion': 'The EndOfList CLI serialization error is reproduced. A second valid file is skipped after the first-file error; it succeeds when run alone. Existing upstream tests pass with the workspace module explicitly selected.'}
(ROOT / 'export/independent-verification.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'tests': record['upstreamTests']['testsRun'], 'upstreamTestsPass': result.wasSuccessful(), 'bugReproduced': True, 'secondFileSkipConfirmed': True, 'moduleOriginVerified': True}))
