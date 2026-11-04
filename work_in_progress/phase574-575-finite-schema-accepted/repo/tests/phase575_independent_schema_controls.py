#!/usr/bin/env python3
"""Frozen independent synthetic schema controls; execute only after Root release."""
import argparse, ast, copy, dataclasses, hashlib, json, math, os, pathlib, re, signal, stat, struct, sys, time, traceback, types
from collections import Counter
ROOT=pathlib.Path('/workspace/python-original-engine/repo')
SCHEMA=ROOT/'data/phase572-mixed-observer-source-v2/schema/phase572_mixed_observer_schema.py'
VECTORS=ROOT/'data/phase575-independent-schema-source/vectors.json'
EXPECTED_OUTPUT=ROOT/'data/phase575-independent-controls-first-001'

def digest(raw):return hashlib.sha256(raw).hexdigest()
def canonical(obj):return json.dumps(obj,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def pin_file(path):
 b=path.read_bytes();return dict(path=str(path),size=len(b),sha256=digest(b))
def verify(pins):
 rows=[]
 for row in pins:
  p=pathlib.Path(row['path']);p=p if p.is_absolute() else ROOT/p
  actual=pin_file(p)
  if (actual['size'],actual['sha256'])!=(row['size'],row['sha256']):raise ValueError('PIN_DRIFT '+str(p))
  rows.append(actual)
 return rows

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--pins',required=True);parser.add_argument('--output-new',required=True);args=parser.parse_args()
 out=pathlib.Path(args.output_new).resolve()
 if out!=EXPECTED_OUTPUT or out.exists():raise ValueError('fixed unused independent output required')
 out.mkdir();started=time.monotonic();result=dict(schema='phase575-independent-actual/1',status='STARTED',synthetic=True,actual_native_data=False,cases=[],direct_entered=0,schema_imports=0,full_capture_validations=0,models=0,Native=0,Expected=0,pool=0)
 pinrows=json.loads(pathlib.Path(args.pins).read_text())['files'];profile=Counter();reads=Counter();before=None
 def timeout(signum,frame):raise TimeoutError('15s independent schema batch deadline')
 signal.signal(signal.SIGALRM,timeout);signal.alarm(15)
 try:
  before=verify(pinrows);result['before']=before
  vectors=json.loads(VECTORS.read_text());assert len(vectors['cases'])==22
  allowed={str(pathlib.Path(x['path']) if pathlib.Path(x['path']).is_absolute() else ROOT/x['path']) for x in pinrows}
  def audit(event,arg):
   if event=='open' and arg and isinstance(arg[0],(str,bytes,os.PathLike)):
    path=str(pathlib.Path(os.fsdecode(arg[0])).absolute());flags=arg[2] if len(arg)>2 and type(arg[2])is int else 0
    writing=bool(flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND))
    if writing:
     if not path.startswith(str(out)+os.sep):raise PermissionError('WRITE_SCOPE '+path)
    else:
     if path not in allowed and not path.startswith(str(out)+os.sep):raise PermissionError('READ_SCOPE '+path)
     reads[path]+=1
   elif event in ('subprocess.Popen','os.system','os.exec','os.posix_spawn','socket.connect','socket.bind'):raise PermissionError('NO_OPERATIONAL_CALL '+event)
  sys.addaudithook(audit)
  module=types.ModuleType('phase575_frozen_schema');module.__file__=str(SCHEMA);sys.modules[module.__name__]=module
  def profiler(frame,event,arg):
   if event=='call' and frame.f_code.co_filename==str(SCHEMA):profile[frame.f_code.co_name]+=1
  sys.setprofile(profiler)
  result['schema_imports']+=1;exec(compile(SCHEMA.read_bytes(),str(SCHEMA),'exec'),module.__dict__)
  for row in vectors['cases']:
   arguments=copy.deepcopy(row['args']);before_args=digest(canonical(arguments));record=dict(id=row['id'],group=row['group'],api=row['api'],expected=row['expected'],input_sha256=before_args,status='ENTERED');result['cases'].append(record);result['direct_entered']+=1;t0=time.monotonic()
   try:
    returned=getattr(module,row['api'])(*arguments)
   except ValueError as exc:
    record['observed_exception']=str(exc)
    if row['expected']!='REJECT_VALUEERROR':raise
    record['first_reject']=str(exc)
   else:
    if row['expected']!='ACCEPT':raise AssertionError('EXPECTED_REJECTION_NOT_RAISED '+row['id'])
    record['return_sha256']=digest(canonical(returned))
   if digest(canonical(arguments))!=before_args:raise AssertionError('INPUT_MUTATION '+row['id'])
   record.update(status='PASS',seconds=time.monotonic()-t0,input_unchanged=True)
  sys.setprofile(None)
  result['status']='PASS_SOURCE_SYNTHETIC_HELPERS_ONLY'
 except BaseException as exc:
  sys.setprofile(None);result.update(status='FAIL_FIRST_UNEXPECTED',error_type=type(exc).__name__,error=str(exc),traceback=traceback.format_exc())
 finally:
  sys.setprofile(None);signal.alarm(0)
  try:result['after']=verify(pinrows);result['source_pins_unchanged']=result['after']==before
  except BaseException as exc:result['after_error']=repr(exc);result['status']='FAIL_FIRST_UNEXPECTED'
  result.update(seconds=time.monotonic()-started,schema_function_calls=dict(profile),read_open_counts=dict(reads),read_scope='pinned source/vector files and new output only after audit installation; preaudit pin verification separate',python=sys.version)
  (out/'result.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
  if result['status']=='FAIL_FIRST_UNEXPECTED':(out/'first-error.json').write_text(json.dumps({k:result.get(k) for k in ('status','error_type','error','traceback','direct_entered','schema_imports')},indent=2)+'\n')
  files=[pin_file(p) for p in sorted(out.iterdir()) if p.is_file()]
  (out/'owned-files.json').write_text(json.dumps(dict(schema='phase575-actual-owner/1',files=files),indent=2)+'\n')
 return 0 if result['status']=='PASS_SOURCE_SYNTHETIC_HELPERS_ONLY' else 1
if __name__=='__main__':raise SystemExit(main())
