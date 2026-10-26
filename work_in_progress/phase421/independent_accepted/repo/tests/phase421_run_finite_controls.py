"""One presealed independent finite batch; never opens true carrier or Root release."""
import argparse
import copy
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
PREP=ROOT/'data/phase421-functional-preparation'
OUT=ROOT/'data/phase421-functional-first-001'
assert not OUT.exists()
OUT.mkdir()
manifest=json.loads((PREP/'execution-manifest.json').read_bytes())
cases=json.loads((PREP/'cases.json').read_bytes())
expectations=json.loads((PREP/'expected.json').read_bytes())
module_path=ROOT/manifest['module']['path']
info=module_path.lstat()
assert stat.S_ISREG(info.st_mode)and info.st_nlink==1 and module_path.resolve(strict=True)==module_path
assert not any(p.is_symlink()for p in(module_path,*module_path.parents))
fd=os.open(module_path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
try:
    assert os.fstat(fd).st_ino==info.st_ino
    chunks=[]
    while True:
        chunk=os.read(fd,65536)
        if not chunk:break
        chunks.append(chunk)
    raw=b''.join(chunks)
finally:
    os.close(fd)
assert len(raw)==manifest['module']['size']and hashlib.sha256(raw).hexdigest()==manifest['module']['sha256']
module=types.ModuleType('independent421_actual420_finite_controls')
module.__file__=str(module_path)
module.__package__=''
exec(compile(raw,str(module_path),'exec'),module.__dict__)
active=None
events=[]


def observer(event,args):
    if event=='open':
        value=args[0]
        if type(value)is str and '/output/capture/'in value:
            raise AssertionError('FORBIDDEN_REAL_CAPTURE_OPEN')
        if active is not None:
            events.append(dict(control=active,path=value,mode=args[1],flags=args[2]))


sys.addaudithook(observer)
api_counts={}


def call(name,*args):
    api_counts[name]=api_counts.get(name,0)+1
    return getattr(module,name)(*args)


def index_from_rows(rows):
    return{(row['field_id'],row['phase'],row['side_or_role']):dict(index=n,row=row)
           for n,row in enumerate(rows)}


def execute(case):
    kind=case['kind'];data=case['input']
    if kind=='ui':return call('project_ui',bytes.fromhex(data['raw_hex']))
    if kind=='sequence':return call('envelope_sequence',bytes.fromhex(data['raw_hex']))
    if kind=='lineage':return call('project_lineage',bytes.fromhex(data['raw_hex']),data['slot'])
    if kind=='slots':return call('project_slots',bytes.fromhex(data['raw_hex']),data['fixed_table'])
    if kind=='json':return call('strict_json',bytes.fromhex(data['raw_hex']))
    if kind=='role':
        return call('check_autohide_role',index_from_rows(data['rows']),data['provenance'],data['role'])
    if kind=='role_pair':
        index=index_from_rows(data['rows'])
        return{role:call('check_autohide_role',index,data['provenance'],role)
               for role in('king_hide:P:12','king_drag:P:12')}
    if kind=='gate':return call('derive_autohide_pair',{}, {},data['gate'])
    if kind=='spent_release':return call('verify_release',data['descriptor'],[])
    if kind=='read':
        io=[];raw=call('read_regular',data['descriptor'],2097152,io)
        return dict(size=len(raw),sha256=hashlib.sha256(raw).hexdigest(),io=io)
    if kind=='save':
        path=OUT/'ordinary-output.json'
        return call('save_new',path,data['value'])
    if kind=='canonical':return str(call('canonical_path',data['path']))
    raise AssertionError('UNKNOWN_INDEPENDENT_CASE_KIND')


def matches(value,expected,case):
    kind=expected['kind']
    if kind=='reject':return False
    if kind=='ui_clean':
        return not any(row['gaps']for row in value['per_role'].values())and value['cut']['ui_sequence']==expected['cut']
    if kind=='ui_gap':
        affected=expected['affected']
        return all('UNSUPPORTED_INITIAL_UI_PATH'in value['per_role'][role]['gaps']for role in affected)and all(not value['per_role'][role]['gaps']for role in value['per_role']if role not in affected)
    if kind=='ui_missing_role':return 'INITIAL_OWNER_READY_MISSING'in value['per_role'][expected['role']]['gaps']
    if kind=='integer':return type(value)is int and value==expected['value']
    if kind=='lineage':return not value['gaps']and value['cut']['kind']==expected['cut']and len(value['selected'])==3
    if kind=='slot':return value['binding']['native_id']=='81679'and value['binding']['instance_id']=='P:12'
    if kind=='role_clean':return value['conditional_input_match']is True and not value['gaps']and'actual_value'not in value
    if kind=='role_gap':return value['conditional_input_match']is False and expected['reason']in value['gaps']and'actual_value'not in value
    if kind=='role_pair':return value['king_hide:P:12']['conditional_input_match']is True and value['king_drag:P:12']['conditional_input_match']is False
    if kind=='read':return(value['size'],value['sha256'])==(expected['size'],expected['sha256'])
    if kind=='saved':return Path(value['path']).name=='ordinary-output.json'and value['size']>0
    raise AssertionError('UNKNOWN_INDEPENDENT_EXPECTATION')


started=time.monotonic()
records=[]
result=dict(schema='independent421-finite-functional-controls/1',status='RUNNING',
    module_instances=1,successful_returns=0,expected_rejections=0,passing_controls=0,
    failed_controls=0,automatic_retry=False,actual_projection_calls=0,old_SUT_calls=0,
    schema_calls=0,audit_calls=0,models=0,native=0,raw_actual_carrier_reads=0,
    EXPECTED_reads=0,private_gate_constructed=False,whole_Root_positive_fabricated=False,
    trusted_stdlib_startup='preloaded before full pinned420 load; outside case measurement')
for case in cases:
    expected=expectations[case['id']]
    record=dict(id=case['id'],kind=case['kind'],expected=expected)
    start_event=len(events);active=case['id']
    try:
        value=execute(case)
        active=None
        result['successful_returns']+=1
        record['outcome']='RETURN'
        if case['kind']=='ui':record['summary']=dict(cut=value['cut'],gaps={k:v['gaps']for k,v in value['per_role'].items()})
        elif case['kind']in('role','role_pair'):record['summary']=value
        else:record['summary']=value
        passed=matches(value,expected,case)
    except module.Rejected as exc:
        active=None
        record.update(outcome='REJECTED',exception=str(exc))
        passed=expected['kind']=='reject'and(expected.get('reason')is None or expected['reason']in str(exc))
        if passed:result['expected_rejections']+=1
    except BaseException as exc:
        active=None
        record.update(outcome='UNEXPECTED_EXCEPTION',exception_type=type(exc).__name__,exception=str(exc))
        passed=False
    snapshot=tuple(events[start_event:])
    record['open_events']=snapshot
    if 'expected_opens'in expected:
        passed=passed and len(snapshot)==expected['expected_opens']
    record['passed']=passed;records.append(record)
    print(json.dumps(dict(control=case['id'],passed=passed,outcome=record['outcome'])),flush=True)
    if not passed:
        result.update(status='FIRST_FUNCTIONAL_FAILURE_STOP',first_failure=record)
        result['failed_controls']+=1
        break
    result['passing_controls']+=1
else:
    result['status']='FINITE_FUNCTIONAL_CONTROLS_PASS'
result.update(controls=records,API_counts=api_counts,top_level_API_calls=sum(api_counts.values()),
    planned_controls=len(cases),unexecuted_controls=[x['id']for x in cases[len(records):]],
    elapsed_seconds=time.monotonic()-started,nested_utility_calls='not profiled')
with(OUT/'result.json').open('x')as handle:
    json.dump(result,handle,indent=2,sort_keys=True);handle.write('\n');handle.flush();os.fsync(handle.fileno())
raise SystemExit(0 if result['status']=='FINITE_FUNCTIONAL_CONTROLS_PASS'else 1)
