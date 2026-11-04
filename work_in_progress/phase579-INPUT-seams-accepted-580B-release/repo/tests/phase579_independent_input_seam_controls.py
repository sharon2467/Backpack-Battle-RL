#!/usr/bin/env python3
"""Frozen finite controls; no execution before exact Root release."""
import argparse, copy, hashlib, json, math, os, pathlib, re, signal, stat, struct, sys, time, traceback, types
from collections import Counter
ROOT=pathlib.Path('/workspace/python-original-engine/repo')
SOURCE=ROOT/'data/phase579-independent-source'
OUT=ROOT/'data/phase579-independent-controls-first-001'
INITIAL=ROOT/'tests/phase578_initial_receipt.py'
BRIDGE=ROOT/'tests/phase578_input_bridge.py'
UNUSED=ROOT/'data/phase578-independent-unbound-579-never-created'

def digest(raw):return hashlib.sha256(raw).hexdigest()
def canonical(obj):return json.dumps(obj,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def pin_file(path):
 raw=path.read_bytes();return {'path':str(path),'size':len(raw),'sha256':digest(raw)}
def verify(pins):
 answer=[]
 for row in pins:
  path=pathlib.Path(row['path']);path=path if path.is_absolute() else ROOT/path
  actual=pin_file(path)
  if (actual['size'],actual['sha256'])!=(row['size'],row['sha256']):raise AssertionError('PIN_DRIFT '+str(path))
  answer.append(actual)
 return answer

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--pins',required=True);parser.add_argument('--output-new',required=True);args=parser.parse_args()
 if pathlib.Path(args.output_new)!=OUT or OUT.exists() or UNUSED.exists():raise ValueError('FIXED_UNUSED_OUTPUTS_REQUIRED')
 OUT.mkdir();started=time.monotonic()
 result=dict(schema='phase579-independent-actual/1',status='STARTED',scope='SOURCE_SYNTHETIC_CHANGED_SEAMS_ONLY',cases=[],direct_entered=0,module_eval_attempts=0,module_imports_completed=0,schema_evals=0,full_receipt=0,raw12_decode=0,full_projection=0,models=0,Native=0,Expected=0,pool=0)
 pins=json.loads(pathlib.Path(args.pins).read_text())['files'];before=None;calls=Counter();reads=Counter();writes=Counter()
 def deadline(signum,frame):raise TimeoutError('15s finite seam deadline')
 signal.signal(signal.SIGALRM,deadline);signal.alarm(15)
 try:
  before=verify(pins);result['before']=before
  vectors=json.loads((SOURCE/'vectors.json').read_text());assert len(vectors['cases'])==9
  allowed={str(pathlib.Path(p['path']) if pathlib.Path(p['path']).is_absolute() else ROOT/p['path']) for p in pins}
  def audit(event,values):
   if event=='open' and values and isinstance(values[0],(str,bytes,os.PathLike)):
    path=str(pathlib.Path(os.fsdecode(values[0])).absolute());flags=values[2] if len(values)>2 and type(values[2]) is int else 0
    writing=bool(flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND))
    if writing:
     if not path.startswith(str(OUT)+os.sep):raise PermissionError('WRITE_SCOPE '+path)
     writes[path]+=1
    else:
     if path not in allowed and not path.startswith(str(OUT)+os.sep):raise PermissionError('READ_SCOPE '+path)
     reads[path]+=1
   elif event=='os.mkdir':
    path=str(pathlib.Path(os.fsdecode(values[0])).absolute())
    if not path.startswith(str(OUT)+os.sep):raise PermissionError('MKDIR_SCOPE '+path)
   elif event in ('subprocess.Popen','os.system','os.exec','os.posix_spawn','socket.connect','socket.bind'):raise PermissionError('NO_OPERATIONAL_CALL '+event)
  sys.addaudithook(audit)
  def profiler(frame,event,arg):
   filename=frame.f_code.co_filename
   if event=='call' and filename in (str(INITIAL),str(BRIDGE)):calls[filename+':'+frame.f_code.co_name]+=1
  sys.setprofile(profiler)
  modules=[]
  for name,path in [('phase578_initial_receipt',INITIAL),('phase579_tested_bridge',BRIDGE)]:
   if name in sys.modules:raise AssertionError('NO_CACHED_TEST_MODULE')
   module=types.ModuleType(name);module.__file__=str(path);sys.modules[name]=module;result['module_eval_attempts']+=1
   exec(compile(path.read_bytes(),str(path),'exec'),module.__dict__);result['module_imports_completed']+=1;modules.append(module)
  bridge=modules[1]
  for vector in vectors['cases']:
   arguments=copy.deepcopy(vector.get('args'));input_value=copy.deepcopy(vector);before_input=digest(canonical(input_value))
   row={'id':vector['id'],'api':vector['api'],'expected':vector['expected'],'reason':vector['reason'],'status':'ENTERED'};result['cases'].append(row)
   if vector['api']=='authenticate_request':
    request=copy.deepcopy(vector['request']);context_raw=canonical(vector['context']);request['source_context'].update(size=len(context_raw),sha256=digest(context_raw));request_raw=canonical(request)
    arguments=[request_raw,{'path':str(SOURCE/'synthetic-selected-request.json'),'size':len(request_raw),'sha256':digest(request_raw)},context_raw]
   args_digest=digest(canonical(arguments)) if vector['api']!='authenticate_request' else digest(canonical([arguments[0].hex(),arguments[1],arguments[2].hex()]))
   read_before=reads.copy();write_before=writes.copy();result['direct_entered']+=1
   try:
    returned=getattr(bridge,vector['api'])(*arguments)
   except bridge.Rejected as error:
    row['first_reject']=str(error)
    if vector['expected']!='REJECT' or str(error)!=vector['reason']:raise
   else:
    if vector['expected']!='ACCEPT':raise AssertionError('MISSING_EXPECTED_REJECTION')
    source_receipt=arguments[2];observations=source_receipt['prepare_observations']['pre_activate']
    assert set(returned['items'])==set(observations)
    for role,observation in observations.items():
     projected=returned['items'][role]
     for key,value in observation.items():assert canonical(projected[key])==canonical(value),(role,key)
     assert projected['native_id']==arguments[1]['role_to_native'][role]
    assert returned['items']['P:13']['ordered_cache_aliases']==[{'color':{'type':'int','decimal':'0'},'ordered_roles':['P:21','P:20'],'ordered_native_ids':[arguments[1]['role_to_native'][r] for r in ['P:21','P:20']]}]
    assert [x['role'] for x in returned['items']['P:13']['ordered_current_aliases'][0]['ordered_members']]==['P:21','P:20']
    assert canonical(returned['characters'])==canonical(source_receipt['resource_observations']['pre_activate'])
    assert canonical(returned['pre_prepare_characters'])==canonical(source_receipt['resource_observations']['pre_prepare'])
    assert returned['source_default_p1']==vector['source_rule_expected']
    assert returned['status']=='OBSERVED_INPUT_NOT_MODEL_EQUIVALENCE'
    row['returned']=copy.deepcopy(returned)
    returned['items']['P:13']['typed_fields']['numBuffs']['decimal']='999'
    returned['characters']['P']['baseStaminaRegen']['binary64_be']='0000000000000000'
   actual_args_digest=digest(canonical(arguments)) if vector['api']!='authenticate_request' else digest(canonical([arguments[0].hex(),arguments[1],arguments[2].hex()]))
   assert actual_args_digest==args_digest,'INPUT_MUTATION'
   assert digest(canonical(input_value))==before_input
   if vector['api']=='build_from_files':
    actual_reads=dict(reads-read_before);actual_writes=dict(writes-write_before)
    expected_reads={str(ROOT/'data/phase578-mixed-input-bridge-source/request-template.json'):1,str(ROOT/'data/phase578-mixed-input-bridge-source/source-context-template.json'):1}
    assert actual_reads==expected_reads,(actual_reads,expected_reads)
    assert not actual_writes and not UNUSED.exists()
    row.update(read_open_counts=actual_reads,write_open_counts=actual_writes,public_output_absent=True,raw12_reads=0,schema_reads=0)
   row.update(status='PASS',input_unchanged=True)
  sys.setprofile(None)
  assert result['direct_entered']==9
  assert calls[str(BRIDGE)+':authenticate_request']==5 and calls[str(BRIDGE)+':project_prepared_witnesses']==4 and calls[str(BRIDGE)+':build_from_files']==1
  for name in ('load_schema','project_from_bytes','decode_lawful12','verify_source_context','verify_raw_inputs','project_decoded'):
   assert calls[str(BRIDGE)+':'+name]==0,name
  assert not any(key.startswith(str(INITIAL)+':') and not key.split(':')[-1].startswith('<') for key in calls)
  result['status']='PASS_SOURCE_SYNTHETIC_SEAMS_ONLY'
 except BaseException as error:
  sys.setprofile(None);result.update(status='FAIL_FIRST_UNEXPECTED',error_type=type(error).__name__,error=str(error),traceback=traceback.format_exc())
 finally:
  sys.setprofile(None);signal.alarm(0)
  try:result['after']=verify(pins);assert result['after']==before;result['pins_unchanged']=True
  except BaseException as error:result['after_error']=repr(error);result['status']='FAIL_FIRST_UNEXPECTED'
  result.update(seconds=time.monotonic()-started,profile=dict(calls),audit_read_open_counts=dict(reads),audit_write_open_counts=dict(writes),public_output_absent=not UNUSED.exists(),python=sys.version)
  (OUT/'result.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
  if result['status']=='FAIL_FIRST_UNEXPECTED':(OUT/'first-error.json').write_text(json.dumps({k:result.get(k) for k in ('status','error_type','error','traceback','direct_entered','module_eval_attempts','module_imports_completed')},indent=2)+'\n')
  owned=[pin_file(p) for p in sorted(OUT.iterdir()) if p.is_file()]
  (OUT/'owned-files.json').write_text(json.dumps({'schema':'phase579-actual-owner/1','files':owned},indent=2)+'\n')
 return 0 if result['status']=='PASS_SOURCE_SYNTHETIC_SEAMS_ONLY' else 1
if __name__=='__main__':raise SystemExit(main())
