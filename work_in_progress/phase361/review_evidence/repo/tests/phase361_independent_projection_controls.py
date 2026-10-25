"""Bounded real projection/schema unit controls. No model or actual input source build."""
import ast
import copy
import dataclasses
import hashlib
import json
import math
import os
from pathlib import Path
import re
import struct
import sys
import sysconfig
import types

R=Path(__file__).resolve().parents[1];D=R/'data/phase361-independent-source-review'
def desc(p):
 b=p.read_bytes();return dict(path=str(p.relative_to(R)),size=len(b),sha256=hashlib.sha256(b).hexdigest())
def canonical(v):return json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def main():
 contract=json.loads((D/'execution-contract.json').read_text())
 for row in contract['files']:assert desc(R/row['path'])==row
 source_owner=desc(D/'source-owner.json');cases=json.loads((D/'cases.json').read_text());fixtures=json.loads((D/'fixtures.json').read_text());assert len(cases)==32
 out=D/'controls-first-001';out.mkdir(exist_ok=False)
 allowed={str((R/r['path']).resolve()) for r in contract['files']}|{str((D/'execution-contract.json').resolve()),str((D/'source-owner.json').resolve())}
 stdlib=Path(sysconfig.get_path('stdlib')).resolve();root=out.resolve();audit=dict(reads=[],writes=[],blocked=[])
 def below(p,r):return p==r or r in p.parents
 def hook(event,args):
  if event=='open':
   if isinstance(args[0],int):return
   p=Path(os.fsdecode(args[0])).absolute().resolve();mode,flags=args[1:3];writing=bool(flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND)) if isinstance(flags,int) else bool(mode and any(c in mode for c in 'wax+'))
   ok=below(p,root) if writing else str(p) in allowed or below(p,root) or (below(p,stdlib) and not {'site-packages','dist-packages'}&set(p.parts))
   if not ok:audit['blocked'].append(dict(event=event,path=str(p),writing=writing));raise PermissionError('phase361 file boundary')
   audit['writes' if writing else 'reads'].append(str(p))
  elif event.startswith('socket.') or event in ('subprocess.Popen','os.system','os.posix_spawn','os.posix_spawnp','os.fork','os.exec'):
   audit['blocked'].append(dict(event=event));raise PermissionError('phase361 network/process boundary')
 sys.addaudithook(hook)
 def module(name,p):
  m=types.ModuleType(name);m.__file__=str(p);sys.modules[name]=m;exec(compile(p.read_bytes(),str(p),'exec'),m.__dict__);return m
 schema=module('phase360_king_observer_schema',R/'tests/phase360_king_observer_schema.py')
 projector=module('__independent361_real_projector__',D/'SOURCE/projector.py')
 calls={};results=[]
 def invoke(name,*args):calls[name]=calls.get(name,0)+1;return getattr(projector,name)(*args)
 def codec():
  runtime=dict.fromkeys(projector.RUNTIME_KEYS);runtime.update(profile_id=schema.PROFILE,mode='genuine',terminal_profile=projector.TERMINAL_PROFILE)
  return dict(schema='native-v8-input-only/1',fixture=copy.deepcopy(schema.FIXED_FIXTURE),runtime=runtime,draws=[],synthetic_seed=None)
 # Deliberately invalid runtime values: this object is engineering codec data,
 # never a semantic model-input positive or passed to an Engine/runtime validator.
 proof=dict(schema='SYNTHETIC_ENGINEERING_CODEC_ONLY',valid_model_input=False,actual_native_sources=False)
 before=dict(schema='SYNTHETIC_IO_CONTROL_ONLY',input_build_authorized=False)
 empty=out/'missing-source-root';empty.mkdir();positive=out/'codec-only-positive'
 aliases=fixtures['aliases'];raw12={n:v.encode() for n,v in fixtures['incomplete_raw12'].items()}
 with (out/'journal.jsonl').open('x') as journal:
  for case in cases:
   op=case['operation'];data=copy.deepcopy(case['data']);data_before=canonical(data);aliases_before=canonical(aliases);raw_before=copy.deepcopy(raw12);detail={};expected=case['expected']
   try:
    if op=='VERIFY_SOURCE':value=invoke('_verify_source_controls',R)
    elif op=='READER':value=invoke('read_and_validate_sources',R,out/'CAPTURE_MUST_NOT_READ',dict(path='RELEASE_MUST_NOT_READ.json',size=1,sha256='0'*64))
    elif op=='BAD_SOURCE_READER':value=invoke('read_and_validate_sources',empty,out/'CAPTURE_MUST_NOT_READ',{})
    elif op=='ROLE':value=invoke('_role',data)
    elif op=='ORDER':value=invoke('_order',data,aliases)
    elif op=='PRIMITIVE':value=invoke('_primitive_projection',data)
    elif op=='TAPE':value=invoke('_check_tape_row',data)
    elif op=='PROJECT_RUNTIME':value=invoke('project_fixture_and_runtime',raw12,aliases)
    elif op=='PROJECT_DRAWS':value=invoke('project_primitives',raw12,aliases)
    elif op.startswith('SEAL_'):
     b=codec();pr=copy.deepcopy(proof);source_root=R;target=out/('codec-unit-'+str(case['id']));first_files=None
     if op=='SEAL_OK':target=positive
     elif op=='SEAL_EXISTING':
      target=positive;first_files={p.name:desc(p) for p in target.iterdir() if p.is_file()}
     elif op=='SEAL_SYMLINK':target.symlink_to(positive,target_is_directory=True)
     elif op=='SEAL_PARTIAL':pr['not_JSON_number']=float('nan')
     elif op=='SEAL_BAD_TOP':b['proof_leak']=True
     elif op=='SEAL_BAD_ROOT':source_root=empty
     elif op=='SEAL_BAD_SEED':b['synthetic_seed']=32103
     elif op=='SEAL_BAD_RUNTIME':b['runtime']['prepared_charges_leak']=3
     elif op=='SEAL_BAD_PROOF':pr=[]
     value=invoke('seal_once',b,pr,before,target,source_root)
     assert value['status']=='FILES_SEALED_NOT_RUNTIME_OR_NATIVE_ACCEPTANCE' and value['models']==0 and value['native']==0
     seal=json.loads((target/'input-joint-seal.json').read_text());assert seal['native_admitted'] is False and seal['model_permission'] is False
     for name,p in seal['files'].items():assert {k:desc(target/name)[k] for k in ('size','sha256')}==p
     observed=json.loads((target/'input-bundle.json').read_text());assert observed==b and observed['runtime']['nodes'] is None
     detail['codec_only_not_a_valid_model_bundle']=True
    elif op=='BAD_PATH':value=invoke('_file',R,'../NEVER_OPEN_OUTSIDE')
    else:raise AssertionError('unsealed operation')
    if case['expected_value'] is not None:assert value==case['expected_value'], 'presealed SOURCE result differs'
   except (ValueError,TypeError,KeyError) as exc:
    accepted=False;detail.update(type=type(exc).__name__,message=str(exc))
    if expected=='pending':
     assert isinstance(exc,ValueError) and str(exc).startswith('PENDING_COLLECTOR_HOST_SHARED_CANDIDATE_CLOSURE:')
     assert not any('CAPTURE_MUST_NOT_READ' in p or 'RELEASE_MUST_NOT_READ' in p for p in audit['reads'])
     detail['capture_release_open_calls']=0
    if op=='SEAL_EXISTING':assert first_files=={p.name:desc(p) for p in positive.iterdir() if p.is_file()}
    if op=='SEAL_PARTIAL':
     assert (target/'input-bundle.json').is_file() and not (target/'input-proof.json').exists() and not (target/'input-joint-seal.json').exists();detail['failed_partial_preserved']=True
   except Exception as exc:
    accepted=None;detail['checker_error']=dict(type=type(exc).__name__,message=str(exc))
   else:accepted=True;detail['return_type']=type(value).__name__
   unchanged=canonical(data)==data_before and canonical(aliases)==aliases_before and raw12==raw_before
   matched=accepted is (expected=='accept')
   row=dict(id=case['id'],label=case['label'],expected=expected,accepted=accepted,unchanged=unchanged,pass_=matched and unchanged,detail=detail);results.append(row);journal.write(json.dumps(row,sort_keys=True)+'\n');journal.flush()
 failures=[r for r in results if not r['pass_']]
 report=dict(schema='phase361-independent-unit-controls/1',status='BOUNDED_UNITS_PASS_FULL_PROJECTION_POSITIVE_NOT_TESTED' if not failures else 'BLOCKED_FIRST_SOURCE_OR_CONTROL_COUNTEREXAMPLE',unique_cases=32,executed=len(results),accepted=sum(r['accepted'] is True for r in results),rejected=sum(r['accepted'] is False for r in results),controls=results,failures=failures,top_level_projector_calls=calls,top_level_call_total=sum(calls.values()),internal_schema_calls='NOT_COUNTED',pure_schema_imports=1,pure_projector_imports=1,synthetic_only=True,engineering_codec_positive_not_a_valid_model_bundle=True,full_projection_API_positive=False,actual12_positive=False,reader_pending=True,candidate_imports=0,RNG=0,Engine=0,RuntimeDTO=0,models=0,native=0,capture_reads=0,expected_reads=0,actual_input_builds=0)
 with (out/'report.json').open('x') as f:json.dump(report,f,indent=2,sort_keys=True);f.write('\n')
 files=[desc(out/n) for n in ('journal.jsonl','report.json')]
 with (out/'open-audit.json').open('x') as f:
  json.dump(dict(schema='phase361-independent-file-audit/1',**audit,trusted_bootstrap='Script/stdlib and exact source/metadata descriptors pinned before hook; actual schema/projector source loaded after hook.',recording_cut='Opening audit; later only own outputs hash readback/jointseal/stdout under activehook.',no_explicit_third_party_or_attack_test_claim=True),f,indent=2,sort_keys=True);f.write('\n')
 files.append(desc(out/'open-audit.json'))
 with (out/'joint-seal.json').open('x') as f:json.dump(dict(schema='phase361-independent-output-jointseal/1',files=files,source_owner=source_owner),f,indent=2,sort_keys=True);f.write('\n')
 print(json.dumps(dict(status=report['status'],executed=len(results),failures=[r['label'] for r in failures],calls=sum(calls.values()),blocked=len(audit['blocked']))))
if __name__=='__main__':main()
