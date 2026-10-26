"""One independent, sealed20-call408 component batch. No actual audit authority."""
import argparse
import copy
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import stat
import struct
import sys
import time

ROOT=Path('/workspace/python-original-engine/repo')
PREP=ROOT/'data/phase409-independent408-component-preparation'
OUTPUT=ROOT/'data/phase409-independent408-component-first-001'
MODULE=ROOT/'tests/phase408_initial_source_audit.py'
events=[]
calls=[]
profile_counts={}
violations=[]
active=None
imports=0

def physical_pin(row):
    p=ROOT/row['path'];a=p.lstat()
    assert stat.S_ISREG(a.st_mode) and a.st_nlink==1 and a.st_size==row['size']
    assert not any(x.is_symlink() for x in (p,*p.parents))
    raw=p.read_bytes();b=p.lstat()
    for k in ('st_dev','st_ino','st_mode','st_nlink','st_size','st_mtime_ns','st_ctime_ns'):assert getattr(a,k)==getattr(b,k)
    assert len(raw)==row['size'] and hashlib.sha256(raw).hexdigest()==row['sha256']
    return raw

def observe(event,args):
    if event=='open':
        path,mode,flags=args
        events.append(dict(event='open',path=path if type(path)is int else os.fsdecode(path),mode=mode,flags=flags,active=active))
    elif event=='import':events.append(dict(event=event,module=str(args[0]),active=active))

def profile(frame,event,arg):
    if event=='call' and frame.f_code.co_filename==str(MODULE):
        name=frame.f_code.co_name
        profile_counts[name]=profile_counts.get(name,0)+1

def call(case,fn,*args):
    global active
    active=case['id'];entry=dict(id=active,API=fn.__name__,expected=case['expected'],open_start=len(events),profile_before=dict(profile_counts))
    calls.append(entry)
    try:
        value=fn(*args)
    except Exception as exc:
        entry.update(exception_type=type(exc).__name__,exception_message=str(exc))
        assert case['expected'].get('exception_type')==type(exc).__name__,entry
        assert case['expected'].get('message_contains','') in str(exc),entry
        entry['outcome']='EXPECTED_REJECTION'
        return None
    else:
        assert 'exception_type' not in case['expected'],entry
        entry['outcome']='RETURNED'
        return value
    finally:
        entry['open_end']=len(events);entry['profile_after']=dict(profile_counts);active=None

def failtrace(exc):
    rows=[];tb=exc.__traceback__
    while tb:
        rows.append(dict(file=tb.tb_frame.f_code.co_filename,line=tb.tb_lineno,function=tb.tb_frame.f_code.co_name));tb=tb.tb_next
    return dict(type=type(exc).__name__,message=str(exc),frames=rows)

def main():
    global imports,active
    assert not OUTPUT.exists()
    OUTPUT.mkdir()
    started=time.monotonic();result=dict(status='RUNNING',new_audit_imports=0,old_SUT_imports=0,old_SUT_calls=0,schema_calls=0,actual12_reads=0,models=0,native=0,inputbuild=0)
    try:
        manifest=json.loads((PREP/'execution-manifest.json').read_bytes())
        raw={r['path']:physical_pin(r) for r in manifest['read_pins']}
        inputs=json.loads(raw[manifest['inputs']]);expected=json.loads(raw[manifest['expected']]);cases=expected['calls']
        assert len(cases)==20
        owners=[json.loads(raw[p]) for p in inputs['real_owner_paths']]
        base=inputs['base_assessment_rows'];targets=inputs['required_targets']
        assert len(base)==len(targets)==1479
        sys.addaudithook(observe)
        sys.setprofile(profile)
        spec=importlib.util.spec_from_file_location('independent409_actual408',MODULE)
        audit=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(audit);imports+=1
        # Actual immutable402/405 path maps and408 list; no payload following or authority claim.
        for i,owner in enumerate(owners):
            value=call(cases[i],audit.owned_index,owner)
            expected_owner={r['path']:r for r in owner['files']} if type(owner['files'])is list else {name:dict(path=name,**r)for name,r in owner['files'].items()}
            assert value==expected_owner and len(value)==cases[i]['expected']['count']
        call(cases[3],audit.owned_index,inputs['bad_owner_path_override'])
        call(cases[4],audit.owned_index,inputs['bad_owner_duplicate'])
        value=call(cases[5],audit.required_initial_targets)
        assert value=={(r['field_id'],r['phase'],r['side_or_role']):r['route']for r in targets}
        for offset,variant in enumerate(inputs['assessment_variants']):
            rows=copy.deepcopy(base)
            if variant['operation']=='remove_last':rows.pop()
            elif variant['operation']=='duplicate_last':rows.append(copy.deepcopy(rows[-1]))
            elif variant['operation']=='patch':rows[variant['index']].update(variant['patch'])
            else:assert variant['operation']=='identity'
            value=call(cases[6+offset],audit.assess_initial_feasibility,rows,[])
            if value is not None:
                assert value['status']==cases[6+offset]['expected']['status'] and value['field_count']==1479
                assert value['fullschema']=='NOT_VALIDATED' and value['genuine_input_accepted']is False
                result['conservative_assessment']=value
        # The real guard runs after every module/fixture read. No replacement validator or constants.
        call(cases[14],audit.install_io_guard,set(),OUTPUT,violations)
        value=call(cases[15],audit.save_new,OUTPUT/'ordinary-output.json',inputs['output_value'])
        assert value==expected['ordinary_output_descriptor']
        entry=calls[-1]
        assert entry['profile_after'].get('read_regular',0)-entry['profile_before'].get('read_regular',0)==1
        writes=[e for e in events[entry['open_start']:entry['open_end']]if e['event']=='open' and type(e['path'])is str]
        assert len(writes)==2 and all(e['path']==str(OUTPUT/'ordinary-output.json')for e in writes),writes
        assert writes[0]['flags']&os.O_EXCL and writes[1]['flags']&os.O_NOFOLLOW and writes[1]['flags']&os.O_NONBLOCK
        call(cases[16],audit.save_new,OUTPUT/'ordinary-output.json',{'must_not_replace':True})
        for n,fixture in enumerate(inputs['physical_negatives']):
            observed=[]
            call(cases[17+n],audit.read_regular,ROOT/fixture['path'],fixture['descriptor'],1024,observed)
            entry=calls[-1]
            assert entry['open_end']==entry['open_start'] and observed==[],entry
        # Harmless standard-library read attempt of an owned leaf outside allowed output.
        active='guard-denied-owned-outside-read';start=len(events)
        try:
            with open(ROOT/inputs['outside_owned_leaf'],'rb') as f:f.read()
        except PermissionError as exc:
            assert str(exc)=='audit file outside exact permission set'
            result['outside_read_control']=dict(status='EXPECTED_PERMISSION_REJECTION',open_attempts=len(events)-start,content_read=False)
        else:raise AssertionError('real guard permitted outside read')
        finally:active=None
        assert len(violations)==1 and violations[0]['path']==str(ROOT/inputs['outside_owned_leaf'])
        assert len(calls)==20
        assert not any(k in profile_counts for k in ('main','run_audit','verify_audit_release','read_lawful12_once','seal_audit_once','audit_direct_fields','audit_source_chain'))
        # Ordinary output is rechecked independently; no extra SUT invocation.
        out=(OUTPUT/'ordinary-output.json').read_bytes()
        assert hashlib.sha256(out).hexdigest()==expected['ordinary_output_descriptor']['sha256']
        result['status']='FINITE_COMPONENTS_PASS'
    except BaseException as exc:
        result.update(status='FIRST_COMPONENT_FAILURE_STOP',first_error=failtrace(exc))
    finally:
        sys.setprofile(None)
        result.update(new_audit_imports=imports,top_level_API_calls=len(calls),calls=calls,profile_counts=profile_counts,io_events=events,guard_violations=violations,elapsed_seconds=time.monotonic()-started,automatic_retry=False)
        with (OUTPUT/'result.json').open('x')as f:json.dump(result,f,indent=2,sort_keys=True);f.write('\n')
        print(json.dumps({k:result[k]for k in ('status','new_audit_imports','top_level_API_calls','elapsed_seconds')}))
    return 0 if result['status']=='FINITE_COMPONENTS_PASS'else 1

if __name__=='__main__':raise SystemExit(main())
