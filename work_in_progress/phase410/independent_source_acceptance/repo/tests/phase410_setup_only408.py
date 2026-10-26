"""One independent full408 module setup; no408 API is invoked."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import stat
import struct
import sys
import traceback
import types
import time

ROOT = Path('/workspace/python-original-engine/repo')
PREP = ROOT / 'data/phase410-setup-only408-preparation'
OUT = ROOT / 'data/phase410-setup-only408-first-001'
contract = json.loads((PREP / 'execution-manifest.json').read_bytes())
expected = json.loads((PREP / 'expected.json').read_bytes())
MODULE = ROOT / contract['module']['path']
assert not OUT.exists()
OUT.mkdir()


def identity(info):
    return [info.st_dev, info.st_ino, info.st_mode, info.st_nlink,
            info.st_size, info.st_mtime_ns, info.st_ctime_ns]


def progress(stage):
    print(json.dumps(dict(stage=stage, observation_active=active)), flush=True)


events = []
active = False


def observer(event, args):
    if not active:
        return
    if event == 'open':
        path, mode, flags = args
        events.append(dict(event=event, path=path, mode=mode, flags=flags))
    elif event == 'import':
        events.append(dict(event=event, module=args[0]))
    elif event in ('compile', 'exec'):
        events.append(dict(event=event))


started = time.monotonic()
result = dict(status='FIRST_SETUP_FAILURE_STOP', new_audit_module_instances=0,
              top_level_API_calls=0, module_API_calls=0, main_run_audit_calls=0,
              old_SUT_calls=0, old_SUT_imports=0, schema_calls=0, actual12_reads=0,
              models=0, native=0, inputbuild=0, automatic_retry=False,
              API_zero_basis='sealed top-level safety plus runner calls no408 functions',
              output_evidence_phase='after observation_active false')
module = types.ModuleType('independent410_setup_only_actual408')
module.__file__ = str(MODULE)
module.__package__ = ''
sys.dont_write_bytecode = True
sys.addaudithook(observer)
try:
    assert all(name in sys.modules for name in contract['preloaded_modules'])
    assert MODULE.is_absolute() and MODULE.resolve(strict=True) == MODULE
    assert not any(path.is_symlink() for path in (MODULE, *MODULE.parents))
    before = MODULE.lstat()
    pin = contract['module']
    assert stat.S_ISREG(before.st_mode) and before.st_nlink == 1
    assert before.st_size == pin['size']
    progress('preloaded_and_source_metadata_checked')
    active = True
    fd = os.open(str(MODULE), os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        assert identity(os.fstat(fd)) == identity(before)
        chunks = []
        remaining = pin['size'] + 1
        while remaining:
            chunk = os.read(fd, remaining)
            if chunk == b'':
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        raw = b''.join(chunks)
        after_fd = os.fstat(fd)
    finally:
        os.close(fd)
    assert identity(before) == identity(after_fd) == identity(MODULE.lstat())
    assert len(raw) == pin['size'] and hashlib.sha256(raw).hexdigest() == pin['sha256']
    progress('source_read_and_sha_verified')
    code = compile(raw, str(MODULE), 'exec')
    progress('complete_source_compiled')
    exec(code, module.__dict__)
    result['new_audit_module_instances'] = 1
    progress('complete_module_executed')
    assert module.__file__ == str(MODULE) and module.__name__ != '__main__'
    assert identity(MODULE.lstat()) == identity(before)
    result.update(module=pin, source_identity=identity(before))
except BaseException as exc:
    result['first_error'] = dict(type=type(exc).__name__, message=str(exc))
finally:
    active = False

snapshot = tuple(events)
progress('observation_closed_snapshot_frozen')
counts = {name: sum(row['event'] == name for row in snapshot)
          for name in ('open', 'import', 'compile', 'exec')}
result.update(events=snapshot, event_counts=counts, measurement_event_count=len(snapshot),
              observer_disabled_before_snapshot=True, used_profiler=False,
              observed_event_types=['open', 'import', 'compile', 'exec'],
              elapsed_seconds=time.monotonic() - started)
try:
    assert 'first_error' not in result
    assert counts == expected['event_counts'], counts
    opens = tuple(row for row in snapshot if row['event'] == 'open')
    assert opens[0]['path'] == str(MODULE) and opens[0]['mode'] is None
    assert not opens[0]['flags'] & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND)
    assert opens[0]['flags'] & os.O_NOFOLLOW and opens[0]['flags'] & os.O_NONBLOCK
    assert result['new_audit_module_instances'] == 1
    result.update(status='SETUP_ONLY_READ_SCOPE_PASS', measured_path_opens=1,
                  measured_pyc_path_opens=0, measured_data_path_opens=0,
                  measured_stdlib_path_opens=0, measured_import_events=0)
except BaseException as exc:
    result['scope_assertion_error'] = dict(type=type(exc).__name__, message=str(exc))

with (OUT / 'result.json').open('x') as handle:
    json.dump(result, handle, indent=2, sort_keys=True)
    handle.write('\n')
    handle.flush()
    os.fsync(handle.fileno())
progress(result['status'])
raise SystemExit(0 if result['status'] == 'SETUP_ONLY_READ_SCOPE_PASS' else 1)
