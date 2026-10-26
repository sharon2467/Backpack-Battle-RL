import hashlib,json,math,re,struct,copy,dataclasses,types,sys,os,time,traceback
from pathlib import Path
B=Path('/workspace/python-original-engine/repo/data/phase435-independent-python-controls-continuation-001')
REPO=B.parent.parent
start=time.monotonic()
def dump(name,obj):
 with (B/name).open('x') as f:json.dump(obj,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n');f.flush();os.fsync(f.fileno())
def check(d):
 p=Path(d['path']);p=p if p.is_absolute() else REPO/p;raw=p.read_bytes();assert len(raw)==d['size'] and hashlib.sha256(raw).hexdigest()==d['sha256'];return raw
prep=json.loads((B/'preparation-owner.json').read_text())
for d in prep['files']:check(d)
release=json.loads(check(prep['release']));plan=json.loads(check(release['plan']));assert len(plan['tests'])==27
bundle=json.loads((B/'frozen-fixtures-and-expecteds.json').read_text());cases=bundle['cases'];assert [x['id'] for x in cases]==[f'P{i:02}' for i in range(1,28)]
raw=check(plan['source_module'])
dump('started.json',{'source_module':plan['source_module'],'Root_release':prep['release'],'stdlib_startup':'Normal trusted stdlib and preparation/fixture/source pin reads occur before observed interval. Source full bytes compile/exec once; dataclass module registered in sys.modules.','controls':27})
active=True;events=[]
def audit(event,args):
 if active and event in ('open','import'):
  detail={'event':event,'arg0':str(args[0])};events.append(detail)
  if event=='import':raise RuntimeError('UNEXPECTED_IMPORT:'+str(args[0]))
  p=Path(os.fsdecode(args[0])) if not isinstance(args[0],int) else None
  if p is None or p!=B/'progress.jsonl':raise RuntimeError('OUT_OF_SCOPE_OPEN:'+str(args[0]))
sys.addaudithook(audit)
module=types.ModuleType('independent435_actual434_schema');module.__file__=str(REPO/plan['source_module']['path']);sys.modules[module.__name__]=module
exec(compile(raw,module.__file__,'exec'),module.__dict__)
results=[];calls=0;failure=None
canonical=lambda x:json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False)
for c in cases:
 t=time.monotonic();exception=None;tb=None;actual=None;detail={};fact=None;before=None
 try:
  if c['operation']=='identity':
   assert module.schema.validate_early_invu_fact is module.validate_early_invu_fact;actual='identity'
  elif c['operation']=='early_fact':
   fact=copy.deepcopy(c['input_fact']);before=canonical(fact);calls+=1;v=module.validate_early_invu_fact(fact,c['input_role']);assert v is fact and canonical(fact)==before;actual='return_same_unchanged';detail={'input_role':c['input_role'],'counters':dict(starts=v['lineage']['starts'],stops=v['lineage']['stops']),'private_provenance':v['private_provenance']}
  else:
   changes=c['changes'];contract=changes['source_contract'];inputs={};binding=b''
   if contract=='module.BINDING_SOURCE_CONTRACT':contract=copy.deepcopy(module.BINDING_SOURCE_CONTRACT)
   elif type(contract) is str and contract.startswith('copy(module.ACTIVE_SOURCE_CONTRACT)'):
    contract=copy.deepcopy(module.ACTIVE_SOURCE_CONTRACT);contract['sink']['sha256']='0'*64
   elif contract=='module.ACTIVE_SOURCE_CONTRACT':contract=copy.deepcopy(module.ACTIVE_SOURCE_CONTRACT)
   if changes['raw11']=='module.INPUT_FILES mapped to empty bytes':inputs={n:b'' for n in module.INPUT_FILES}
   if changes['binding_bytes']=='bytearray()':binding=bytearray()
   calls+=1;v=module.validate_sources_with_binding(inputs,binding,contract);actual='unexpected_return'
 except ValueError as e:actual='ValueError';exception=str(e)
 except Exception as e:
  actual='UNEXPECTED_EXCEPTION'
  exception=type(e).__name__+':'+str(e)
  tb=[]
  walk=e.__traceback__
  while walk is not None:
   tb.append({'file':walk.tb_frame.f_code.co_filename,'line':walk.tb_lineno,'function':walk.tb_frame.f_code.co_name})
   walk=walk.tb_next
 if fact is not None:detail['input_unchanged']=canonical(fact)==before
 expected='identity' if c['operation']=='identity' else ('ValueError' if c['expected'].startswith('ValueError') else 'return_same_unchanged')
 good=actual==expected and (fact is None or detail['input_unchanged'])
 r={'id':c['id'],'name':c['name'],'pass':good,'expected':expected,'actual':actual,'exception':exception,'traceback':tb,'detail':detail,'elapsed':time.monotonic()-t};results.append(r)
 with (B/'progress.jsonl').open('a') as f:f.write(json.dumps(r,allow_nan=False)+'\n');f.flush();os.fsync(f.fileno())
 if not good:failure={'result':r,'fixture':c};break
active=False;snapshot=tuple(events)
dump('result.json',{'schema':'independent435-Python27-result/1','status':'PASS' if failure is None else 'BLOCKED_FIRST_UNEXPECTED','planned':27,'executed':len(results),'passed':sum(x['pass'] for x in results),'unexecuted':[x['id'] for x in cases[len(results):]],'results':results,'first_failure':failure,'module_loads':1,'top_API_calls':calls,'events':snapshot,'elapsed':time.monotonic()-start,'stdlib_scope_is_not_global_OS_trace':True,'native':0,'models':0,'hostplan_execute_raw_EXPECTED':0,'new_recipes':0})
print(json.dumps({'status':'PASS' if failure is None else 'BLOCKED_FIRST_UNEXPECTED','executed':len(results),'passed':sum(x['pass'] for x in results),'module_loads':1,'top_API_calls':calls}))
sys.exit(0 if failure is None else 1)
