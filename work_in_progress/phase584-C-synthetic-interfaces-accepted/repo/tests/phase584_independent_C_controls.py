#!/usr/bin/env python3
"""Frozen finite synthetic C seams; requires separate Root execution release."""
import argparse, copy, dataclasses, datetime, hashlib, importlib, importlib.util, json, math, os, pathlib, random, re, signal, stat, struct, sys, time, traceback, types, typing
from collections import Counter
ROOT=pathlib.Path('/workspace/python-original-engine/repo')
SOURCE=ROOT/'data/phase584-independent-C-control-source'
STAGE=ROOT/'data/phase580-captured-mixed-source/staged'
OUT=ROOT/'data/phase584-independent-controls-first-001'
MODULES={'launcher':ROOT/'tests/phase583_mixed_tape_run.py','adapter':ROOT/'tests/phase583_mixed_business_output.py','B2':ROOT/'tests/phase583_shared_callback_guard.py'}

def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)
def sha(value):return hashlib.sha256(canonical(value).encode()).hexdigest()
def pin_file(path):
 raw=path.read_bytes();return dict(path=str(path),size=len(raw),sha256=hashlib.sha256(raw).hexdigest())
def verify(rows):
 out=[]
 for row in rows:
  p=pathlib.Path(row['path']);p=p if p.is_absolute() else ROOT/p;got=pin_file(p)
  assert (got['size'],got['sha256'])==(row['size'],row['sha256']),('PIN_DRIFT',str(p))
  out.append(got)
 return out

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--pins',required=True);parser.add_argument('--output-new',required=True);args=parser.parse_args()
 assert pathlib.Path(args.pins)==SOURCE/'pins.json' and pathlib.Path(args.output_new)==OUT and not OUT.exists(),'FIXED_FRESH_OUTPUT'
 OUT.mkdir();started=time.monotonic();before=None;engine=None;profile=Counter();reads=Counter();modules={}
 result=dict(schema='phase584-independent-synthetic-C-controls/1',status='STARTED',cases=[],C_direct_entered=0,C_positive=0,C_reject=0,C_module_import_attempts=0,C_module_import_completed=0,candidate_import_attempts=0,candidate_import_completed=0,ctor_entered=0,ctor_success=0,explicit_snapshots=0,empty_Tape_ctor=0,synthetic_final_assignments=[],prepare=0,activate=0,step=0,run=0,Native=0,Expected=0,actual_UI=0,actual_INPUT=0,full_comparison=0,actual_B1=0)
 pins=json.loads(pathlib.Path(args.pins).read_text())['files']
 def timeout(sig,frame):raise TimeoutError('20s finite C control deadline')
 signal.signal(signal.SIGALRM,timeout);signal.alarm(20)
 try:
  before=verify(pins);result['before']=before
  vectors=json.loads((SOURCE/'vectors.json').read_text());bundle=json.loads((SOURCE/'synthetic-bundle-pretty.json').read_text());rawUI=(SOURCE/'synthetic-king-ui-authority.jsonl').read_bytes()
  allowed={str(pathlib.Path(r['path']) if pathlib.Path(r['path']).is_absolute() else ROOT/r['path']) for r in pins}
  def audit(event,values):
   if event=='open' and values and isinstance(values[0],(str,bytes,os.PathLike)):
    path=str(pathlib.Path(os.fsdecode(values[0])).absolute());flags=values[2] if len(values)>2 and type(values[2]) is int else 0;writing=bool(flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND))
    if writing:
     if not path.startswith(str(OUT)+os.sep):raise PermissionError('WRITE_SCOPE '+path)
    else:
     if path not in allowed and not path.startswith(str(OUT)+os.sep):raise PermissionError('READ_SCOPE '+path)
     reads[path]+=1
   elif event in ('subprocess.Popen','os.system','os.exec','os.posix_spawn','socket.connect','socket.bind'):raise PermissionError('NO_OPERATIONAL_CALL '+event)
  sys.dont_write_bytecode=True;sys.pycache_prefix=str(OUT/'unused-bytecode-cache');sys.addaudithook(audit)
  watched={str(p) for p in MODULES.values()}
  def profiler(frame,event,arg):
   if event=='call':
    filename=frame.f_code.co_filename
    if filename in watched or filename.startswith(str(STAGE)+os.sep):profile[filename+':'+frame.f_code.co_qualname]+=1
  sys.setprofile(profiler)
  for name,path in MODULES.items():
   result['C_module_import_attempts']+=1;spec=importlib.util.spec_from_file_location('phase584_'+name,path);mod=importlib.util.module_from_spec(spec);sys.modules[spec.name]=mod;spec.loader.exec_module(mod);modules[name]=mod;result['C_module_import_completed']+=1
   assert pathlib.Path(mod.__file__).resolve()==path
  L,A,B=modules['launcher'],modules['adapter'],modules['B2']
  assert not any(n.startswith(('native_replay_v7','native_replay_v8')) for n in sys.modules),'FRESH_CANDIDATE'
  sys.path.insert(0,str(STAGE));result['candidate_import_attempts']+=1;E=importlib.import_module('native_replay_v8.engine');R=sys.modules['native_replay_v8.randomness'];result['candidate_import_completed']+=1
  origins={n:str(pathlib.Path(m.__file__).resolve()) for n,m in sys.modules.items() if n.startswith(('native_replay_v7','native_replay_v8')) and getattr(m,'__file__',None)}
  assert all(p in allowed and p.startswith(str(STAGE)+os.sep) for p in origins.values());result['import_origins']=origins;result['C_import_origins']={k:str(m.__file__) for k,m in modules.items()}
  result['empty_Tape_ctor']+=1;tape=R.TapeRandom([]);result['ctor_entered']+=1;engine=E.CombatEngine(copy.deepcopy(bundle['fixture']),tape,copy.deepcopy(bundle['runtime']));result['ctor_success']+=1
  assert not engine.prepared and not engine.activated and tape.position==0 and tape.audit==[] and engine.frame_driver.pass_index==0
  for obj,field,label in ((engine,'finalized','engine.finalized'),(engine.frame_driver,'finalized','engine.frame_driver.finalized')):
   assert getattr(obj,field) is False;setattr(obj,field,True);result['synthetic_final_assignments'].append(dict(field=label,before=False,after=True,authority='explicit synthetic prestate, not completed run'))
  result['explicit_snapshots']+=1;snapshot=engine.snapshot();model=dict(final=snapshot,random_inputs=[],captured_terminal={'final':{'passes_consumed':0}})
  result['synthetic_result_from_actual_snapshot']=model
  expected=vectors['expected_final_aux'];bound={'items':{i['instance_id']:i for s in bundle['fixture']['sides'] for i in s['items']},'nodes':{n['role']:n for n in bundle['runtime']['processing_nodes']},'inactive_timers':frozenset('invu:'+s for s in ('P','O'))|frozenset('aux:'+s+':'+n for s in ('P','O') for n in ('battleRageTimer','autoRageTimer'))}
  def call(name,fn,reason=None):
   row=dict(id=name,status='ENTERED',expected_reject=reason);result['cases'].append(row);result['C_direct_entered']+=1
   try:value=fn()
   except (ValueError,AssertionError) as exc:
    if reason is None:raise
    row.update(first_reject_type=type(exc).__name__,first_reject=str(exc),first_reject_traceback=traceback.format_exc())
    if reason!='ASSERTION' and reason not in str(exc):raise AssertionError('WRONG_FIRST_REJECT '+name+':'+str(exc))
    if reason=='ASSERTION' and type(exc) is not AssertionError:raise AssertionError('WRONG_ASSERTION_TYPE '+name)
    result['C_reject']+=1;value=None
   else:
    if reason is not None:raise AssertionError('NEGATIVE_ACCEPTED '+name)
    result['C_positive']+=1
   row['status']='PASS';return value
  actual_aux=call('01_actual_getter_synthetic_final',lambda:L.final_business_view(engine,model));result['raw_actual_getter']=actual_aux
  assert canonical(actual_aux)==canonical(expected),'PRESEALED_GETTER_EXPECTATION'
  engine.frame_driver.finalized=False
  try:call('02_actual_getter_wrong_stage',lambda:L.final_business_view(engine,model),'actual post-run finalized getter stage');assert engine.frame_driver.finalized is False
  finally:engine.frame_driver.finalized=True
  result['synthetic_final_assignments'].extend([dict(field='engine.frame_driver.finalized',before=True,after=False,authority='negative stage'),dict(field='engine.frame_driver.finalized',before=False,after=True,authority='restore unit prestate')])
  def origin_binding(aux):return {'model_output_canonical_sha256':sha(model),'final_aux_canonical_sha256':sha(aux)}
  projected=call('03_aux_origin_positive',lambda:A.validate_final_aux_origin(copy.deepcopy(expected),model,bound,origin_binding(expected)))
  assert canonical(projected)==canonical({i:{n:f['projected_value'] for n,f in item['properties'].items()} for i,item in expected['items'].items()})
  def aux_negative(name,change,reason,wrongcanonical=False):
   aux=copy.deepcopy(expected);change(aux);binding=origin_binding(aux)
   if wrongcanonical:binding['final_aux_canonical_sha256']='0'*64
   frozen=canonical(aux);call(name,lambda:A.validate_final_aux_origin(aux,model,bound,binding),reason);assert canonical(aux)==frozen
  aux_negative('04_aux_wrong_canonical',lambda x:None,'same externally authenticated sealed model/aux canonical bytes',True)
  aux_negative('05_aux_foreign_stage',lambda x:x.__setitem__('stage','PREPARE_OFF_CLOCK'),'actual final getter stage/Source')
  aux_negative('06_aux_foreign_owner',lambda x:x['items']['P:15'].__setitem__('instance_id','P:14'),'same final getter owner/subtype')
  aux_negative('07_aux_missing_property',lambda x:x['items']['P:15']['properties'].pop('manaCost'),'exact getter properties')
  aux_negative('08_aux_rawINT_not_projectedREAL',lambda x:x['items']['P:15']['properties']['manaCost'].__setitem__('projected_value',3),'Source float projection distinct from raw type')
  Bbinding=vectors['B2_root_binding'];assert Bbinding['input_bundle']['sha256']!=Bbinding['input_bundle_canonical_sha256'] and sha(bundle)==Bbinding['input_bundle_canonical_sha256']
  frozen=canonical([bundle,Bbinding]);guard=call('09_B2_pretty_physical_distinct_canonical',lambda:B.extract_shared_callback_guard(rawUI,bundle,vectors['B2_raw_pin'],Bbinding));assert canonical([bundle,Bbinding])==frozen
  assert guard['native_roles_verified']==29 and guard['model_noop_slots']==31 and guard['full_FX_UI_gate_called'] is False
  result['synthetic_B2_raw_return_not_actual_evidence']=guard;result['pretty_physical_SHA']=Bbinding['input_bundle']['sha256'];result['bundle_canonical_SHA']=sha(bundle)
  wrong=copy.deepcopy(Bbinding);wrong['input_bundle_canonical_sha256']=wrong['input_bundle']['sha256'];call('10_B2_physical_SHA_as_canonical',lambda:B.extract_shared_callback_guard(rawUI,bundle,vectors['B2_raw_pin'],wrong),'ASSERTION')
  missing=copy.deepcopy(Bbinding);missing.pop('input_bundle_canonical_sha256');call('11_B2_missing_fifth_key',lambda:B.extract_shared_callback_guard(rawUI,bundle,vectors['B2_raw_pin'],missing),'ASSERTION')
  call('12_unknown_callback_before_noop',lambda:A.project_model_callbacks({'pure_combat_diagnostics':{'callbacks':[{'kind':'source_callback','role':'item:FOREIGN','mode':1}]}},bound),'model callback bound identity')
  extra=copy.deepcopy(vectors['comparison_template']);extra['verified']=True;call('13_closed20_no_verified_shortcut',lambda:A.bindings({}, {},extra),'closed20 external comparison binding')
  request=copy.deepcopy(vectors['model_request_template']);call('14_closed17_false_Root_auth',lambda:L.validate_request(request),'closed17 Root model request')
  request=copy.deepcopy(request);request['root_model_authorized']=True;call('15_unbound_actual_descriptors',lambda:L.validate_request(request),'UNBOUND_ACTUAL_INPUT_OR_SOURCE_REQUEST')
  call('16_prepared_gate_foreign_stage',lambda:L.validate_prepared_business_view(vectors['prepared_wrong_stage'],{}, {},{}),'same-instance prepared zeroKing stage')
  assert result['C_direct_entered']==16 and result['C_positive']==3 and result['C_reject']==13
  assert result['ctor_success']==1 and result['explicit_snapshots']==1 and tape.position==0 and tape.audit==[] and engine.frame_driver.pass_index==0 and not engine.prepared and not engine.activated
  for key in ('prepare_only','activate_from_checkpoint','step','run','finish','death','_run_captured_clock'):
   assert profile[str(STAGE/'native_replay_v8/engine.py')+':CombatEngine.'+key]==0,key
  assert profile[str(MODULES['adapter'])+':compare_decoded']==0 and profile[str(MODULES['launcher'])+':main']==0
  result.update(status='PASS_SOURCE_AND_SYNTHETIC_C_SEAMS_ONLY',Tape_consumed=0,passes_consumed=0,actual_postrun=False,actual_B1=False,actual_B2=False,full_comparison=False)
 except BaseException as exc:
  sys.setprofile(None);result.update(status='FAIL_FIRST_UNEXPECTED',error_type=type(exc).__name__,error=str(exc),traceback=traceback.format_exc())
 finally:
  sys.setprofile(None);signal.alarm(0)
  if engine is not None:result['partial_engine']=dict(prepared=engine.prepared,activated=engine.activated,finalized=engine.finalized,driver_finalized=engine.frame_driver.finalized,Tape_position=engine.random.position,Tape_audit=engine.random.audit,passes=engine.frame_driver.pass_index,winner=engine.winner)
  try:result['after']=verify(pins);assert result['after']==before;result['pins_unchanged']=True
  except BaseException as exc:result['after_error']=repr(exc);result['status']='FAIL_FIRST_UNEXPECTED'
  result.update(seconds=time.monotonic()-started,profile=dict(profile),audit_read_open_counts=dict(reads),python=sys.version)
  (OUT/'result.json').write_text(json.dumps(result,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
  if result['status']=='FAIL_FIRST_UNEXPECTED':(OUT/'first-error.json').write_text(json.dumps({k:result.get(k) for k in ('status','error_type','error','traceback','C_direct_entered','ctor_entered','ctor_success','explicit_snapshots')},indent=2)+'\n')
  (OUT/'owned-files.json').write_text(json.dumps({'schema':'phase584-actual-owner/1','files':[pin_file(p) for p in sorted(OUT.iterdir()) if p.is_file()]},indent=2)+'\n')
 return 0 if result['status']=='PASS_SOURCE_AND_SYNTHETIC_C_SEAMS_ONLY' else 1
if __name__=='__main__':raise SystemExit(main())
