"""Verify sealed preparation, then launch exactly one25s setup child."""
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import time

ROOT = Path('/workspace/python-original-engine/repo')
PREP = ROOT / 'data/phase410-setup-only408-preparation'
OUT = ROOT / 'data/phase410-setup-only408-launcher'
assert not OUT.exists()
owner = json.loads((PREP / 'owned-files.json').read_bytes())
for row in owner['files']:
    path = ROOT / row['path']
    assert path.resolve(strict=True) == path
    assert not any(p.is_symlink() for p in (path, *path.parents))
    info = path.lstat()
    assert stat.S_ISREG(info.st_mode) and info.st_nlink == 1 and info.st_size == row['size']
    raw = path.read_bytes()
    assert len(raw) == row['size'] and hashlib.sha256(raw).hexdigest() == row['sha256']
contract = json.loads((PREP / 'execution-manifest.json').read_bytes())
args = [sys.executable, '-B', str(ROOT / 'tests/phase410_setup_only408.py')]
OUT.mkdir()


def save(name, value):
    with (OUT / name).open('x') as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write('\n')


save('args.json', dict(args=args, cwd=str(ROOT), timeout_seconds=25,
                       environment_override={'PYTHONDONTWRITEBYTECODE': '1'},
                       invocations=1, automatic_retry=False,
                       preparation_owner_sha256=hashlib.sha256((PREP / 'owned-files.json').read_bytes()).hexdigest()))
started = time.monotonic()
env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
try:
    completed = subprocess.run(args, cwd=ROOT, env=env, capture_output=True, timeout=25)
    stdout, stderr = completed.stdout, completed.stderr
    receipt = dict(status='CHILD_EXITED', child_exit_code=completed.returncode, timed_out=False)
except subprocess.TimeoutExpired as exc:
    stdout, stderr = exc.stdout or b'', exc.stderr or b''
    receipt = dict(status='FIRST_SETUP_TIMEOUT_STOP', child_exit_code=None, timed_out=True)
for name, raw in (('stdout.txt', stdout), ('stderr.txt', stderr)):
    with (OUT / name).open('xb') as handle:
        handle.write(raw)
receipt.update(elapsed_seconds=time.monotonic()-started, invocations=1,
               automatic_retry=False, timeout_seconds=25)
save('exit.json', receipt)
print(json.dumps(receipt), flush=True)
raise SystemExit(0 if receipt['child_exit_code'] == 0 else 1)
