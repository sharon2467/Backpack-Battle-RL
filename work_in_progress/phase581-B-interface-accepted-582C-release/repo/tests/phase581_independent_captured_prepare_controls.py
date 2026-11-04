#!/usr/bin/env python3
"""Exact finite synthetic captured constructor/prepare; release required."""
import argparse, copy, dataclasses, hashlib, importlib, json, math, os, pathlib, random, re, signal, stat, struct, sys, time, traceback, types, typing
from collections import Counter
ROOT=pathlib.Path('/workspace/python-original-engine/repo')
SOURCE=ROOT/'data/phase581-independent-interface-source'
STAGE=ROOT/'data/phase580-captured-mixed-source/staged'
OUT=ROOT/'data/phase581-independent-interface-first-001'

def digest(raw):return hashlib.sha256(raw).hexdigest()
def canonical(obj):return json.dumps(obj,sort_keys=True,separators=(',',':'),allow_nan=False)
def pin_file(path):
 raw=path.read_bytes();return dict(path=str(path),size=len(raw),sha256=digest(raw))
def verify(rows):
 result=[]
 for row in rows:
  p=pathlib.Path(row['path']);p=p if p.is_absolute() else ROOT/p;actual=pin_file(p)
  if (actual['size'],actual['sha256'])!=(row['size'],row['sha256']):raise ValueError('PIN_DRIFT '+str(p))
  result.append(actual)
 return result

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--pins',required=True);parser.add_argument('--output-new',required=True);args=parser.parse_args()
 if pathlib.Path(args.output_new)!=OUT or OUT.exists():raise ValueError('FIXED_NEW_OUTPUT')
 OUT.mkdir();started=time.monotonic();before=None;engine=None;profile=Counter();reads=Counter()
 result=dict(schema='phase581-finite-synthetic-interface/1',status='STARTED',cases=[],top_entered=0,ctor_entered=0,ctor_success=0,ctor_rejected=0,prepare_entered=0,package_import_attempts=0,package_imports_completed=0,explicit_snapshot_reads=0,activation=0,step=0,run=0,Native=0,Expected=0,pool=0)
 pins=json.loads(pathlib.Path(args.pins).read_text())['files']
 def timeout(signum,frame):raise TimeoutError('15s finite interface deadline')
 signal.signal(signal.SIGALRM,timeout);signal.alarm(15)
 try:
  before=verify(pins);result['before']=before;data=json.loads((SOURCE/'inputs.json').read_text());fixture=data['fixture'];runtime=data['runtime'];expected=data['expected']
  allowed={str(pathlib.Path(p['path']) if pathlib.Path(p['path']).is_absolute() else ROOT/p['path']) for p in pins}
  def audit(event,values):
   if event=='open' and values and isinstance(values[0],(str,bytes,os.PathLike)):
    path=str(pathlib.Path(os.fsdecode(values[0])).absolute());flags=values[2] if len(values)>2 and type(values[2]) is int else 0;writing=bool(flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND))
    if writing:
     if not path.startswith(str(OUT)+os.sep):raise PermissionError('WRITE_SCOPE '+path)
    else:
     if path not in allowed and not path.startswith(str(OUT)+os.sep):raise PermissionError('READ_SCOPE '+path)
     reads[path]+=1
   elif event in ('subprocess.Popen','os.system','os.exec','os.posix_spawn','socket.connect','socket.bind'):raise PermissionError('NO_OPERATIONAL_CALL '+event)
  sys.addaudithook(audit);sys.dont_write_bytecode=True;sys.pycache_prefix=str(OUT/'unused-bytecode-cache');sys.path.insert(0,str(STAGE))
  if any(n.startswith(('native_replay_v7','native_replay_v8')) for n in sys.modules):raise AssertionError('FRESH_PACKAGE_REQUIRED')
  def profiler(frame,event,arg):
   if event=='call' and frame.f_code.co_filename.startswith(str(STAGE)+os.sep):profile[frame.f_code.co_filename[len(str(STAGE))+1:]+':'+frame.f_code.co_qualname]+=1
  sys.setprofile(profiler);result['package_import_attempts']+=1
  E=importlib.import_module('native_replay_v8.engine');G=sys.modules['native_replay_v8.genuine'];R=sys.modules['native_replay_v8.randomness'];result['package_imports_completed']+=1
  origins={name:str(pathlib.Path(module.__file__).resolve()) for name,module in sys.modules.items() if name.startswith(('native_replay_v7','native_replay_v8')) and getattr(module,'__file__',None)}
  assert all(path in allowed and path.startswith(str(STAGE)+os.sep) for path in origins.values());result['import_origins']=origins
  def rejected(name,fn,reason):
   row=dict(id=name,status='ENTERED',expected_reject=reason);result['cases'].append(row);result['top_entered']+=1
   try:fn()
   except ValueError as error:
    row['first_reject']=str(error)
    if reason not in str(error):raise AssertionError('WRONG_FIRST_REJECT '+name+':'+str(error))
   else:raise AssertionError('NEGATIVE_ACCEPTED '+name)
   row['status']='PASS'
  def negative_fixture(name,edit,reason):
   f=copy.deepcopy(fixture);edit(f);frozen=canonical(f);rejected(name,lambda:G.validate_captured_mixed_fixture(f),reason);assert canonical(f)==frozen
  def negative_runtime(name,edit,reason):
   x=copy.deepcopy(runtime);edit(x);frozen=canonical(x);rejected(name,lambda:E.validate_runtime_inputs(x,fixture),reason);assert canonical(x)==frozen
  negative_fixture('01_BOOL_type',lambda f:f.__setitem__('below_master',0),'explicit actual belowMaster BOOL')
  negative_fixture('02_geometry',lambda f:f['sides'][0]['items'][0].__setitem__('x',1),'exact29 geometry')
  negative_runtime('03_missing_aux_private',lambda x:x['timer_initial']['aux:P:battleRageTimer'].pop('private_left_bits'),'pure timer fields')
  negative_runtime('04_character_BOOL_alias',lambda x:x['initial_characters']['P'].__setitem__('invulnerable',0),'character initial values')
  def ghost(x):
   for role,name,pos in [('buff:P:Block','A',9),('buff:P:Lucky','B',10)]:
    node=next(n for n in x['processing_nodes'] if n['role']==role);node.update(path='/root/Ghost/'+name,name=name,positions=[-1,pos,0])
    config=next(n for n in x['nodes'] if n['role']==role);config.update(path=node['path'],positions=node['positions'][:])
  negative_runtime('05_reverse_ancestor',ghost,'reverse sparse prefix conflict')
  def bad_provider():
   result['ctor_entered']+=1
   try:return E.CombatEngine(fixture,None,runtime)
   except ValueError:result['ctor_rejected']+=1;raise
  rejected('06_no_provider',bad_provider,'exact TapeRandom')
  result['top_entered']+=1;row=dict(id='07_construct',status='ENTERED');result['cases'].append(row);result['ctor_entered']+=1
  tape=R.TapeRandom(data['tape']);engine=E.CombatEngine(fixture,tape,runtime);result['ctor_success']+=1
  assert engine.captured_clock_mode and engine.pure_combat_mode and not engine.king_mode and not engine.source_pure_mode and not engine.source_king_mode and engine.king_states=={}
  assert len(engine.runtime_roles)==66 and sum(isinstance(n,E.TimerRecord) for n in engine.runtime_roles.values())==32
  assert engine.captured_noop_slots==frozenset({('game',0),('game',1)}|{('item:'+i,1) for i in engine.items}) and len(engine.captured_noop_slots)==31
  assert all(isinstance(engine.runtime_roles[role],E.TimerRecord) and len(engine.runtime_roles[role].timeout_handlers)==1 for role in expected['inactive'])
  assert tape.position==0 and tape.audit==[] and engine.frame_driver.pass_index==0 and not engine.timer_runtime.started_timers and not engine.prepared
  assert not any(i.cache_prepared or i.double_activation_chance!=0.0 or i.double_attack_effect_chance!=0.0 for i in engine.items.values())
  assert all(engine.items[i].wolpertinger_stamina_regen_per_buff is None and not engine.items[i].wolpertinger_buff_listener_registered for i in ('P:13','O:4'))
  assert engine.items['P:6'].item_index==11 and engine.items['P:14'].item_index==164
  row['status']='PASS'
  result['top_entered']+=1;row=dict(id='08_prepare',status='ENTERED');result['cases'].append(row);result['prepare_entered']+=1;engine.prepare_only()
  assert engine.prepared and not engine.activated and all(i.cache_prepared for i in engine.items.values())
  for identity,value in expected['pet_chance'].items():assert type(engine.items[identity].double_activation_chance) is float and engine.items[identity].double_activation_chance==value
  for identity,value in expected['attack_chance'].items():assert type(engine.items[identity].double_attack_effect_chance) is float and engine.items[identity].double_attack_effect_chance==value
  for identity in ('P:13','O:4'):
   item=engine.items[identity];assert item.wolpertinger_buff_listener_registered is True and type(item.wolpertinger_stamina_regen_per_buff) is float and struct.pack('>d',item.wolpertinger_stamina_regen_per_buff).hex()==expected['wolf_coefficient_bits']
  assert engine.items['P:12'].bowl_speed_bonus_given==0.0 and type(engine.items['P:12'].bowl_speed_bonus_given) is float
  assert tape.position==0 and tape.audit==[] and engine.frame_driver.pass_index==0 and not engine.timer_runtime.started_timers
  result['explicit_snapshot_reads']+=1;prepared_snapshot=engine.snapshot();result['prepared_snapshot']=prepared_snapshot;row['status']='PASS'
  def state_negative(name,identity,field,bad,reason):
   item=engine.items[identity];old=getattr(item,field);setattr(item,field,bad)
   try:
    rejected(name,lambda:engine._validate_captured_mixed_state(True),reason)
    assert type(getattr(item,field)) is type(bad) and getattr(item,field)==bad,'CHECKER_REPAIRED_STATE'
   finally:setattr(item,field,old)
  state_negative('09_missing_Bowl','P:13','double_activation_chance',0.0,'double activation differs from actual prepared global Bowl contributions')
  state_negative('10_missing_385','P:15','double_attack_effect_chance',0.0,'double attack effect chance differs from actual prepared385 contributions')
  state_negative('11_wrong_coefficient','P:13','wolpertinger_stamina_regen_per_buff',.008,'captured mixed actual prepared Wolper coefficient')
  rejected('12_foreign_idle',lambda:engine._source_noninterfering_callback('item:FOREIGN',1,.01),'unknown captured no-op callback role/mode')
  timer=engine.runtime_roles['aux:P:battleRageTimer'];rejected('13_inactive_timeout',lambda:timer.timeout_handlers[0](timer),'inactive captured Timer timeout: aux:P:battleRageTimer')
  result['explicit_snapshot_reads']+=1;after_snapshot=engine.snapshot();assert canonical(prepared_snapshot)==canonical(after_snapshot)
  assert tape.position==0 and tape.audit==[] and engine.frame_driver.pass_index==0 and not engine.activated and not engine.timer_runtime.started_timers
  assert result['top_entered']==13 and result['ctor_entered']==2 and result['ctor_success']==1 and result['ctor_rejected']==1 and result['prepare_entered']==1
  for key in ('CombatEngine.activate_from_checkpoint','CombatEngine.step','CombatEngine.run','CombatEngine.finish','CombatEngine.death','CombatEngine._run_captured_clock'):assert profile['native_replay_v8/engine.py:'+key]==0,key
  result.update(status='PASS_SYNTHETIC_CAPTURED_CONSTRUCT_PREPARE_ONLY',Tape_consumed=0,passes_consumed=0,returned_state_unchanged_after_negative_controls=True)
 except BaseException as error:
  sys.setprofile(None);result.update(status='FAIL_FIRST_UNEXPECTED',error_type=type(error).__name__,error=str(error),traceback=traceback.format_exc())
 finally:
  sys.setprofile(None);signal.alarm(0)
  if engine is not None:result['partial_scalars']=dict(prepared=engine.prepared,activated=engine.activated,Tape_position=engine.random.position,Tape_audit=engine.random.audit,pass_index=engine.frame_driver.pass_index,king_states=engine.king_states)
  try:result['after']=verify(pins);assert result['after']==before;result['pins_unchanged']=True
  except BaseException as error:result['after_error']=repr(error);result['status']='FAIL_FIRST_UNEXPECTED'
  result.update(seconds=time.monotonic()-started,profile=dict(profile),audit_read_open_counts=dict(reads),python=sys.version)
  (OUT/'result.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
  if result['status']=='FAIL_FIRST_UNEXPECTED':(OUT/'first-error.json').write_text(json.dumps({k:result.get(k) for k in ('status','error_type','error','traceback','top_entered','ctor_entered','ctor_success','prepare_entered')},indent=2)+'\n')
  (OUT/'owned-files.json').write_text(json.dumps({'schema':'phase581-actual-owner/1','files':[pin_file(p) for p in sorted(OUT.iterdir()) if p.is_file()]},indent=2)+'\n')
 return 0 if result['status']=='PASS_SYNTHETIC_CAPTURED_CONSTRUCT_PREPARE_ONLY' else 1
if __name__=='__main__':raise SystemExit(main())
