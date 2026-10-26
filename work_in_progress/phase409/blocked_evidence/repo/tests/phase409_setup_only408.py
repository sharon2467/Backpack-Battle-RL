"""Root-authorized single setup-only408 full-module load, zero public API calls."""
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

ROOT=Path('/workspace/python-original-engine/repo')
PREP=ROOT/'data/phase409-setup-only-preparation'
OUT=ROOT/'data/phase409-setup-only-first-001'
MODULE=ROOT/'tests/phase408_initial_source_audit.py'
assert not OUT.exists()
OUT.mkdir()
contract=json.loads((PREP/'contract.json').read_bytes())
events=[];profiles={};phase='MEASUREMENT';started=time.monotonic()
module=types.ModuleType('independent409_setup_only_actual408')
module.__file__=str(MODULE)
module.__package__=''

def summary(value):
    if value is None or type(value)in(str,int,bool,float):return value
    if type(value)is bytes:return dict(type='bytes',size=len(value),sha256=hashlib.sha256(value).hexdigest())
    if isinstance(value,types.CodeType):return dict(type='code',filename=value.co_filename,name=value.co_name)
    if type(value)in(list,tuple):return [summary(x)for x in value]
    return dict(type=type(value).__name__)
def observer(event,args):events.append(dict(phase=phase,event=event,args=summary(args)))
def profiler(frame,event,arg):
    if event=='call' and frame.f_code.co_filename==str(MODULE):
        name=frame.f_code.co_name;profiles[name]=profiles.get(name,0)+1
def identity(info):return [info.st_dev,info.st_ino,info.st_mode,info.st_nlink,info.st_size,info.st_mtime_ns,info.st_ctime_ns]
def trace(exc):
    tb=exc.__traceback__;frames=[]
    while tb:
        frames.append(dict(file=tb.tb_frame.f_code.co_filename,line=tb.tb_lineno,function=tb.tb_frame.f_code.co_name));tb=tb.tb_next
    return dict(type=type(exc).__name__,message=str(exc),frames=frames)

result=dict(status='RUNNING',new_audit_module_instances=0,top_level_API_calls=0,old_SUT_calls=0,old_SUT_imports=0,schema_calls=0,actual12_reads=0,models=0,native=0,inputbuild=0,automatic_retry=False)
sys.setprofile(profiler)
sys.addaudithook(observer)
try:
    assert all(name in sys.modules for name in contract['preloaded_modules'])
    assert not any(p.is_symlink()for p in(MODULE,*MODULE.parents))
    before=MODULE.lstat();pin=contract['module']
    assert stat.S_ISREG(before.st_mode)and before.st_nlink==1 and before.st_size==pin['size']
    fd=os.open(MODULE,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
    try:
        opened=os.fstat(fd);assert identity(opened)==identity(before)
        chunks=[];remaining=pin['size']+1
        while remaining:
            chunk=os.read(fd,remaining)
            if not chunk:break
            chunks.append(chunk);remaining-=len(chunk)
        raw=b''.join(chunks);closed=os.fstat(fd)
    finally:os.close(fd)
    assert identity(before)==identity(closed)==identity(MODULE.lstat())
    assert len(raw)==pin['size'] and hashlib.sha256(raw).hexdigest()==pin['sha256']
    code=compile(raw,str(MODULE),'exec')
    exec(code,module.__dict__)
    result['new_audit_module_instances']=1
    assert module.__file__==str(MODULE)
    assert identity(MODULE.lstat())==identity(before)
    assert profiles=={'<module>':1,'SourceIntegrityError':1},profiles
    opens=[e for e in events if e['event']=='open']
    assert len(opens)==1 and opens[0]['args'][0]==str(MODULE),opens
    assert not any(e['event']=='import'for e in events)
    assert sum(e['event']=='compile'for e in events)==1 and sum(e['event']=='exec'for e in events)==1
    result.update(status='SETUP_ONLY_READ_SCOPE_PASS',module=pin,identity=identity(before),measured_path_opens=1,measured_pyc_path_opens=0,measured_data_path_opens=0,measured_import_events=0,module_API_calls=0,compile_events=1,exec_events=1)
except BaseException as exc:
    result.update(status='FIRST_SETUP_FAILURE_STOP',first_error=trace(exc))
finally:
    sys.setprofile(None)
    result['measurement_event_count']=len(events)
    phase='EVIDENCE_SEALING'
    result.update(events=events,profile_counts=profiles,elapsed_seconds=time.monotonic()-started)
    with (OUT/'result.json').open('x')as f:json.dump(result,f,indent=2,sort_keys=True);f.write('\n')
    print(json.dumps({k:result[k]for k in('status','new_audit_module_instances','top_level_API_calls','elapsed_seconds')}))
raise SystemExit(0 if result['status']=='SETUP_ONLY_READ_SCOPE_PASS'else 1)
