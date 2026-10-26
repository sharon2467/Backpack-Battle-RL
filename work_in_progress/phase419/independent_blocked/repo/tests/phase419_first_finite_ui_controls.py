"""Single finite independent test of original418 UI parser, synthetic bytes only."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import struct
import sys
import time
import types

ROOT=Path('/workspace/python-original-engine/repo')
PREP=ROOT/'data/phase419-finite-ui-controls-preparation'
OUT=ROOT/'data/phase419-finite-ui-controls-first-001'
assert not OUT.exists()
OUT.mkdir()
manifest=json.loads((PREP/'execution-manifest.json').read_bytes())
expected=json.loads((PREP/'expected.json').read_bytes())
rows=[]


def identity(info):
    return[info.st_dev,info.st_ino,info.st_mode,info.st_nlink,info.st_size,info.st_mtime_ns,info.st_ctime_ns]


def read_pin(row):
    path=ROOT/row['path']
    assert path.resolve(strict=True)==path and not any(p.is_symlink()for p in(path,*path.parents))
    before=path.lstat()
    assert stat.S_ISREG(before.st_mode)and before.st_nlink==1 and before.st_size==row['size']
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
    try:
        assert identity(os.fstat(fd))==identity(before)
        chunks=[]
        while True:
            chunk=os.read(fd,65536)
            if not chunk:break
            chunks.append(chunk)
        raw=b''.join(chunks)
        assert identity(os.fstat(fd))==identity(before)
    finally:
        os.close(fd)
    assert identity(path.lstat())==identity(before)
    assert len(raw)==row['size']and hashlib.sha256(raw).hexdigest()==row['sha256']
    return raw


started=time.monotonic()
module=types.ModuleType('independent419_original418_finite_ui_controls')
module.__file__=str(ROOT/manifest['module']['path'])
module.__package__=''
raw=read_pin(manifest['module'])
exec(compile(raw,module.__file__,'exec'),module.__dict__)
result=dict(schema='independent419-first-finite-ui-controls/1',status='RUNNING',
    source_module=manifest['module'],new_module_instances=1,top_level_API_calls=0,
    successful_returns=0,observed_rejections=0,passing_controls=0,failed_controls=0,
    old_SUT_calls=0,schema_calls=0,audit_calls=0,actual_projection_calls=0,
    raw_carrier_reads=0,EXPECTED_reads=0,models=0,native=0,automatic_retry=False,
    trusted_stdlib_startup='before complete pinned418 load; no exhaustive startup-preload claim',
    private_verified_gate_constructed=False,whole_Root_positive_fabricated=False)
for test in manifest['controls']:
    record=dict(id=test['id'],API='project_ui',expected=expected[test['id']])
    raw=read_pin(test['input'])
    result['top_level_API_calls']+=1
    try:
        value=module.project_ui(raw)
        result['successful_returns']+=1
        record.update(outcome='RETURN',cut=value['cut'],
            per_role_gaps={role:value['per_role'][role]['gaps']for role in value['per_role']})
        if test['id']=='valid_prefix_opaque_suffix':
            passed=value['cut']['ui_sequence']==4 and all(not row['gaps']for row in value['per_role'].values())
        else:
            passed='UNSUPPORTED_INITIAL_UI_PATH'in value['per_role']['king_hide:P:12']['gaps']
    except module.Rejected as exc:
        result['observed_rejections']+=1
        record.update(outcome='REJECTED',exception=str(exc))
        passed=test['id']!='valid_prefix_opaque_suffix'
    except BaseException as exc:
        record.update(outcome='UNEXPECTED_EXCEPTION',exception_type=type(exc).__name__,exception=str(exc))
        passed=False
    record['passed']=passed
    rows.append(record)
    print(json.dumps(dict(control=record['id'],passed=passed,outcome=record['outcome'])),flush=True)
    if not passed:
        result.update(status='FIRST_FUNCTIONAL_COUNTEREXAMPLE_STOP',first_failure=record)
        result['failed_controls']+=1
        break
    result['passing_controls']+=1
else:
    result['status']='TWO_CRITICAL_UI_CONTROLS_PASS_NOT_WHOLE_FUNCTIONAL_ACCEPTANCE'
result.update(controls=rows,elapsed_seconds=time.monotonic()-started,
    remaining_controls_unexecuted='Role/counter/slot/lineage boundary/authority/filesystem controls pending behind first blocker; no actual run')
with(OUT/'result.json').open('x')as handle:
    json.dump(result,handle,indent=2,sort_keys=True);handle.write('\n');handle.flush();os.fsync(handle.fileno())
raise SystemExit(1 if result['failed_controls']else 0)
