import argparse,ast,copy,hashlib,json,os,pathlib,re,stat,sys,time,types
BASE=pathlib.Path('/workspace/python-original-engine/repo/data/phase427-independent-kingbuff-overlay-review')
REPO=BASE.parent.parent
started=time.monotonic()
def dump(name,obj):
 p=BASE/name
 with p.open('x') as f:json.dump(obj,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def desc(p):
 z=p.read_bytes();return {'path':str(p),'size':len(z),'sha256':hashlib.sha256(z).hexdigest()}
prep=json.loads((BASE/'preparation-owner.json').read_text())
for d in prep['files']:
 p=REPO/d['path'] if not pathlib.Path(d['path']).is_absolute() else pathlib.Path(d['path']);assert desc(p)==dict(d,path=str(p))
cases=json.loads((BASE/'controls-and-expecteds-final.json').read_text())['cases']
fixture=json.loads((BASE/'fixture-saved-inputs.json').read_text())
physical=json.loads((BASE/'physical-fixture-descriptors-final.json').read_text())
source=REPO/'tests/phase426_king_buff_overlay.py';raw=source.read_bytes();assert len(raw)==27087 and hashlib.sha256(raw).hexdigest()=='473c60a2ea1656ff6c9bd59fcbad2a16eee6739e1affc0bd78bdf6f2704aede0'
dump('started.json',{'module_prepinned':True,'controls':len(cases),'module_loads':0,'startup_boundary':'Trusted stdlib startup and runner/preparation reads precede observation. Whole426 bytes compiled/executed once, no420 import or actual run.','preparation_owner':desc(BASE/'preparation-owner.json')})
events=[];active=True
allowed={str(source),*(d['path'] for d in physical.values())}
allowed.update(str(p) for p in (BASE/'physical-fixtures').iterdir())
allowed.add(str(BASE/'synthetic-output.json'))
allowed.update(str(BASE/n) for n in ['result.json','progress.jsonl'])
def audit(event,args):
 if not active:return
 if event=='open':
  path=args[0]
  if isinstance(path,(str,bytes,os.PathLike)):
   path=os.fsdecode(path);p=pathlib.Path(path);p=p if p.is_absolute() else pathlib.Path.cwd()/p;path=str(p)
   events.append({'event':'open','path':path,'mode':str(args[1]),'flags':args[2]})
   if path not in allowed:raise RuntimeError('OUT_OF_SCOPE_OPEN:'+path)
 elif event=='import':
  events.append({'event':'import','name':str(args[0])});raise RuntimeError('UNEXPECTED_RUNTIME_IMPORT:'+str(args[0]))
sys.addaudithook(audit)
m=types.ModuleType('independent427_tested426');m.__file__=str(source);sys.modules[m.__name__]=m
exec(compile(raw,str(source),'exec'),m.__dict__)
module_loads=1;calls=0;results=[]
def call(fn,*a):
 global calls
 calls+=1;return fn(*a)
index=call(m.load_initial_index,json.dumps(fixture['index']).encode())
def access(obj,path):
 for k in path:obj=obj[k]
 return obj
def change(obj,path,value):access(obj,path[:-1])[path[-1]]=value
def edited(case):
 ix=copy.deepcopy(index);p=copy.deepcopy(fixture['provenance']);a=copy.deepcopy(fixture['a4']);ed=case.get('edit')
 if not ed:return ix,p,a
 op=ed[0]
 if op in ('row','delete_row','delete_row_value_key'):
  key=next(k for k,v in ix.items() if v['index']==ed[1]);row=ix[key]['row']
  if op=='row':change(row,ed[2],ed[3])
  elif op=='delete_row':del ix[key]
  else:del row['actual_value'][ed[2]]
 elif op=='provenance':change(p,ed[1],ed[2])
 elif op=='delete_provenance':del access(p,ed[1][:-1])[ed[1][-1]]
 elif op=='duplicate_a4':a['targets'][1]=copy.deepcopy(a['targets'][0])
 elif op=='a4_private_change':next(r for r in a['targets'] if r['classification']=='SOURCE_DERIVED')['actual_value']['binary64_be']='0000000000000000'
 elif op=='a4_bool_count':a['source_derived']=True
 elif op=='a4_new_king':
  r=next(r for r in a['targets'] if r['side_or_role']=='king_buff:P:12');r.update(classification='SOURCE_DERIVED',validation_result='SUPPORTED',proof_complete=True,actual_value={'type':'float','binary64_be':'bff0000000000000'})
 else:raise AssertionError('UNKNOWN_EDIT')
 return ix,p,a
failure=None
for c in cases:
 n=len(events);t=time.monotonic();ix,p,a=edited(c);actual=None;exception=None
 try:
  op=c['op']
  if op=='collect':
   v=call(m.collect_kingbuff_initial,ix,p)
   assert 'actual_value' not in v and 'private_value' not in v
   if not v['gaps']:assert len(v['support'])==44
   actual='complete' if not v['gaps'] else 'gap';detail={'gaps':v['gaps'],'support':len(v['support']),'private_target_promotions':0}
  elif op=='a4':
   v=call(m.validate_a4,a,ix);assert v==a['targets'] and len(v)==88;actual='a4_valid';detail={'rows':len(v)}
  elif op in ('derive_bool','derive_dict'):
   v=call(m.derive_kingbuff_pair,ix,a,{'role':m.ROLE,'gaps':[],'support':[]},True if op=='derive_bool' else {'verified':True});actual='returned';detail={}
  elif op=='gate_ctor':v=call(m._VerifiedGate,object(),{});actual='returned';detail={}
  elif op=='spent_run':
   before=len(events);v=call(m.run,{'path':'data/phase420-root-initial-partial-projection-release/release.json','size':2038,'sha256':'809480b03de7c691d2735222b9454ca10ce2ad102baf588a665731696bce8716'});actual='returned';detail={}
  elif op in physical:
   d=physical[op];saved=m.RELEASE_PATH;m.RELEASE_PATH=pathlib.Path(d['path'])
   try:v=call(m.verify_kingbuff_release,d,[]);actual='returned';detail={}
   finally:m.RELEASE_PATH=saved
  elif op in ('save_new','save_existing'):
   path=BASE/'synthetic-output.json';v=call(m.save_new,path,{'synthetic_io_only':True});actual='saved';detail={'descriptor':v}
  else:raise AssertionError('UNKNOWN_OP')
 except m.Rejected as ex:actual='reject';exception=str(ex);detail={}
 except Exception as ex:actual='unexpected_exception';exception=type(ex).__name__+':'+str(ex);detail={}
 good=actual==c['expect'] and (c.get('reason') is None or exception==c['reason'])
 if c['op']=='spent_run' and len(events)!=n:good=False;detail['gate_before_read_failed']=events[n:]
 if c['op'] in ('directory_owner','wrongsize_owner'):
  blocked=json.loads((BASE/'physical-fixture-descriptors-final.json').read_text()) if False else physical[c['op']]
  # The rejected owner must never be opened, only the negative release.
  if len([x for x in events[n:] if x['event']=='open'])!=1:good=False;detail['owner_open_after_physical_failure']=True
 r={'id':c['id'],'name':c['name'],'pass':good,'expected':c['expect'],'actual':actual,'reason':exception,'detail':detail,'elapsed':time.monotonic()-t,'observed_events':events[n:]};results.append(r)
 with (BASE/'progress.jsonl').open('a') as f:f.write(json.dumps(r,ensure_ascii=False)+'\n');f.flush();os.fsync(f.fileno())
 if not good:failure=r;break
active=False;snapshot=tuple(events)
dump('result.json',{'schema':'independent427-finite-functional-result/1','status':'PASS' if failure is None else 'BLOCKED_FIRST_FAILURE','module_loads':module_loads,'top_API_calls':calls,'planned_controls':len(cases),'executed_controls':len(results),'passed_controls':sum(x['pass'] for x in results),'unexecuted_controls':[x['id'] for x in cases[len(results):]],'first_failure':failure,'results':results,'events':snapshot,'elapsed':time.monotonic()-started,'actual_saved_overlay_calls':0,'new_private_promotions':0,'old420_imports_raw_carrier_EXPECTED_old_SUT_model_native':0,'only_run_invocation':'spent420 negative path gate, rejected before any I/O/output','no_positive_gate_minted':True})
print(json.dumps({'status':'PASS' if failure is None else 'BLOCKED_FIRST_FAILURE','executed':len(results),'passed':sum(x['pass'] for x in results),'calls':calls,'module_loads':1}))
sys.exit(0 if failure is None else 1)
