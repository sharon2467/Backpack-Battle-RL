"""Finite new Squirrel controls; first error preserved, no native/old replay."""
import copy
import functools
import hashlib
import importlib
import json
from pathlib import Path
import signal
import struct
import sys
import time
import traceback
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'data/phase489-source-squirrel'
PLAN=ROOT/'data/phase490-independent-business-plan'
OWN=ROOT/'data/phase490-independent-harness-source/owned-files.json'
OUT=ROOT/'data/phase490-independent-business-first-001'
COUNTS={};PASSES=[];PREPARES=[];SPEED_WRITES=[];ACTIVE=None;STAGE='preflight'
SQ='P:squirrel';POS=('Lucky','Regeneration','Vampirism','Spikes','Mana','Empower','Heat')
CACHE_POS={SQ:['P:berry0','P:squirrelB','P:squirrelC'],'P:squirrelB':['P:berry0',SQ],'P:squirrelC':[SQ]}
CACHE_ZERO={SQ:[]}
CACHE_NAT={SQ:['P:berry0','P:goobert','P:berry1']}
EXPECTED_CACHE=None

def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
 b=p.read_bytes();return dict(path=str(p.relative_to(ROOT)),size=len(b),sha256=sha(b))
def save(name,v):
 p=OUT/name;p.write_text(json.dumps(v,ensure_ascii=False,allow_nan=False,separators=(',',':'))+'\n');return pin(p)
def strict(a,b,where='$'):
 assert type(a)is type(b),(where,type(a).__name__,type(b).__name__)
 if isinstance(a,float):assert struct.pack('>d',a)==struct.pack('>d',b),(where,a,b)
 elif isinstance(a,dict):
  assert {(type(k),k)for k in a}=={(type(k),k)for k in b},(where,'keys')
  for k in a:strict(a[k],b[k],where+'.'+str(k))
 elif isinstance(a,(list,tuple)):
  assert len(a)==len(b),(where,len(a),len(b))
  for i,(x,y)in enumerate(zip(a,b)):strict(x,y,where+'['+str(i)+']')
 else:assert a==b,(where,a,b)
def verify_owner(p,want=None):
 raw=p.read_bytes()
 if want:strict(sha(raw),want)
 rows=json.loads(raw)['files']
 for row in rows:strict(pin(ROOT/row['path']),row,'pin')
 return rows
def check(name,details=None):
 row=dict(name=name,status='PASS',details=details,calls=COUNTS.copy());PASSES.append(row)
 with(OUT/'controls.jsonl').open('a')as f:f.write(json.dumps(row,allow_nan=False)+'\n')
def counted(obj,name,label):
 original=getattr(obj,name)
 @functools.wraps(original)
 def call(*a,**kw):
  COUNTS[label]=COUNTS.get(label,0)+1
  if label=='Engine.prepare_only':
   e=a[0];strict(e.random.audit,[]);answer=original(*a,**kw);strict(e.random.audit,[])
   cache={i:[x.instance_id for x in e.affected_items(e.items[i])]for i in EXPECTED_CACHE}
   strict(cache,EXPECTED_CACHE,'real_prepared_cache')
   for i in EXPECTED_CACHE:strict(e.items[i].speed_scale,0.0,'before_real_combatStart_speed')
   PREPARES.append(dict(cache=cache,audit=copy.deepcopy(e.random.audit),source_rng=e.random.snapshot()))
   return answer
  if label=='Engine.add_speed' and a[1].item_index==164:
   e,item,amount=a
   SPEED_WRITES.append(dict(item=item.instance_id,amount=amount,all_cooldowns_active=all(x.cooldown_active for x in e.items.values()if x.has_cooldown),audit=copy.deepcopy(e.random.audit),before=item.speed_scale))
  return original(*a,**kw)
 setattr(obj,name,call)
def reject(name,fn):
 before=COUNTS.copy()
 try:fn()
 except ValueError as ex:strict(COUNTS,before,name+'.zero_rng');check(name,dict(error=str(ex),no_rng_or_engine=True))
 else:raise AssertionError(name+' accepted')

def ingress(h,mod,layout):
 d=mod.CATALOG[164]
 strict(d['shape'],((0,0),(0,1),(1,1)));strict(d['stars'],((0,-1),(-1,0),(1,0),(-1,1),(2,1),(0,2),(1,2)))
 strict((d['pet'],d['nature'],d['cooldown'],d['pet_speed_percent'],d['buff_steal'],d['socket_count'],d['default_gem']),(True,True,4.0,15.0,1,0,None))
 strict(len(mod.CATALOG),77);strict(len(h.ITEMS),75);assert164_not_in=164 not in h.ITEMS;assert assert164_not_in
 check('01_exact_descriptor_and_closed_formal75')
 h.validate_squirrel_layout(layout)
 opposite=copy.deepcopy(layout)
 for i,side in enumerate(reversed(copy.deepcopy(layout['sides']))):
  identity=('P','O')[i];side['side']=identity
  for x in side['items']:x['instance_id']=identity+':'+x['instance_id'].split(':',1)[1]
  opposite['sides'][i]=side
 h.validate_squirrel_layout(opposite);check('02_P_and_O_new_admission')
 reject('03_old_initialize_164',lambda:h.initialize(layout,49001))
 old=copy.deepcopy(layout);old['sides'][0]['items']=[x for x in old['sides'][0]['items']if x['item_index']!=164]
 reject('04_old_batch_bad_second_atomic',lambda:h.run_batch([dict(layout=old,seed=49001),dict(layout=layout,seed=49001)],keep_results=True))
 reject('05_new_requires164',lambda:h.initialize_squirrel(old,49001))
 king=copy.deepcopy(layout);next(x for x in king['sides'][0]['items']if x['item_index']==164)['item_index']=262
 reject('06_noKing',lambda:h.initialize_squirrel(king,49001))
 rage=copy.deepcopy(layout);rage['sides'][0]['items'][0]['item_index']=129
 reject('07_noRage',lambda:h.initialize_squirrel(rage,49001))
 cl=copy.deepcopy(layout);cl['sides'][0]['character_class']=2
 reject('08_class0',lambda:h.initialize_squirrel(cl,49001))
 extra=copy.deepcopy(layout);next(x for x in extra['sides'][0]['items']if x['item_index']==164)['power']=2
 reject('09_noModifier',lambda:h.initialize_squirrel(extra,49001))
 reject('10_boolSeed',lambda:h.initialize_squirrel(layout,True));strict(COUNTS,{})

def initialize(h,layout,cache,name):
 global ACTIVE,EXPECTED_CACHE
 EXPECTED_CACHE=cache;speed_at=len(SPEED_WRITES);b=h.initialize_squirrel(copy.deepcopy(layout),49001);e=b._engine;ACTIVE=e
 strict(b.initialization['source_extension'],'source-headless-squirrel-default/1');strict(b.initialization['formal_support'],75)
 strict(e.king_mode,False)
 strict(sum(x['kind']=='timer'for x in e.runtime_inputs.data['nodes']),26)
 labels=['cooldown:'+i for i in e.preparation_order if e.items[i].has_cooldown]
 strict([x['label']for x in e.random.audit],labels,'only_startup_cooldowns')
 for i,targets in cache.items():
  value=len(targets)*15.0/100.0
  strict(e.items[i].speed_scale,value,'original_speed_arithmetic')
  strict(e.items[i].activations,0);strict(e.histories.item_metrics[i][4],0)
  strict(e.histories.logger('P')['itemTooltipHistories'][i][3].values[-1],1.0+value)
  strict(e.histories.logger('P')['itemTooltipHistories'][i][9].values[-1],e.histories.item_stat(e.items[i],9))
 assert not any(x['origin']in cache and x['type']==0 for x in e.events)
 writes=SPEED_WRITES[speed_at:];strict(len(writes),sum(bool(v)for v in cache.values()))
 for x in writes:strict(x['all_cooldowns_active'],True);strict([r['label']for r in x['audit']],labels)
 save(name+'.initialize.json',dict(actual_prepare=PREPARES[-1],cache=cache,speed_writes=writes,original_audit=e.random.audit,original_rng=e.random.snapshot(),events=e.events,history=e.histories.snapshot(),calls=COUNTS.copy()))
 return b

def bits(v):return struct.pack('>d',float(v)).hex()
def fr(label,lo,hi,value):return dict(kind='randf_range',label=label,args=[bits(lo),bits(hi)],value_bits=bits(value))
def pitch():return fr('squirrel_activation_pitch:'+SQ,.9,1.1,1.0)
def cooldown():return fr('cooldown:'+SQ,.95,1.05,1.0)
def pick(high=0,value=0):return dict(kind='randi_range',label='random_stack:'+SQ+':O:take:0',args=[0,high],value=value)

class UnitTape:
 def __init__(self,rows,e,trail):self.rows=copy.deepcopy(rows);self.audit=[];self.position=0;self.e=e;self.trail=trail
 def take(self,kind,label,args):
  assert self.position<len(self.rows),('tape_exhausted',label)
  row=self.rows[self.position];key='value_bits'if kind=='randf_range'else'value'
  strict({k:v for k,v in row.items()if k!=key},dict(kind=kind,label=label,args=args))
  self.position+=1;self.audit.append(copy.deepcopy(row))
  if label.startswith('squirrel_activation_pitch:'):
   self.trail.append(dict(method='pitch',events=len(self.e.events),metric=self.e.histories.item_metrics[SQ][4],tooltip=self.e.histories.logger('P')['itemTooltipHistories'][SQ][9].snapshot()))
  return struct.unpack('>d',bytes.fromhex(row[key]))[0]if key=='value_bits'else row[key]
 def randf_range(self,label,lo,hi):return self.take('randf_range',label,[bits(lo),bits(hi)])
 def randi_range(self,label,lo,hi):return self.take('randi_range',label,[lo,hi])
 def assert_consumed(self):strict(self.position,len(self.rows))

def instrument_history(e,trail):
 for method in ('item_metric','tooltip'):
  original=getattr(e.histories,method)
  def call(*a,_m=method,_f=original,**kw):
   result=_f(*a,**kw)
   trail.append(dict(method=_m,identity=a[0].instance_id,stat=a[1],events=len(e.events)))
   return result
  setattr(e.histories,method,call)

def reset(e,timevalue,own=None,enemy=None,protect=0):
 e.util_time=float(timevalue)
 for side,values in (('P',own or {}),('O',enemy or {})):
  for kind in POS:
   value=values.get(kind,0);setattr(e.characters[side],kind.lower(),value)
   fields,_=e._buff_record(side,kind);fields['permanentStacks']=value;fields['temporaryStacks'].clear()
   e.histories.stack(side,{'Lucky':101,'Regeneration':102,'Vampirism':103,'Spikes':104,'Mana':105,'Empower':106,'Heat':107}[kind])
 e.characters['O'].buff_protect_stacks=protect

def segment(e,trail,name,rows,fn):
 global STAGE
 STAGE=name;start=len(e.events);trail.clear();e.random=UnitTape(rows,e,trail)
 save(name+'.prestate.json',dict(synthetic=True,util_time=e.util_time,ended=e.ended,protection=e.characters['O'].buff_protect_stacks,
  stacks={s:{k:getattr(e.characters[s],k.lower())for k in POS}for s in ('P','O')},metric=e.histories.item_metrics[SQ][4],lastActivationTime=e.items[SQ].last_activation_time,activationsThisFrame=e.items[SQ].activations_this_frame))
 answer=fn();events=copy.deepcopy(e.events[start:])
 save(name+'.actual.json',dict(synthetic=True,events=events,return_value=answer,audit=e.random.audit,position=e.random.position,trail=trail,snapshot=e.snapshot(),histories=e.histories.snapshot(),calls=COUNTS.copy()))
 e.random.assert_consumed();return answer,events

def tail(trail):
 last=trail[-3:];strict([x['method']for x in last],['item_metric','tooltip','pitch'])
 strict((last[0]['identity'],last[0]['stat'],last[1]['identity'],last[1]['stat']),(SQ,4,SQ,9))

def components(h,mod,pos,zero):
 global STAGE
 STAGE='11_positive_cache';b=initialize(h,pos,CACHE_POS,'positive-cache');check('11_rotated_samePet_order_dedup_exact_start_speed')
 STAGE='12_zero_cache';b=initialize(h,zero,CACHE_ZERO,'zero-cache');e=b._engine;check('12_zero_start_no_speed_or_activation')
 trail=[];instrument_history(e,trail);E=mod.EVENT_TYPES
 reset(e,1.0)
 _,ev=segment(e,trail,'13_empty_fulltrigger',[cooldown(),pitch()],lambda:e.trigger(e.items[SQ]))
 strict([x['type']for x in ev],[E['Activation']]);strict(ev[0]['origin'],SQ);tail(trail)
 strict((e.items[SQ].consumed,e.items[SQ].cooldown_active),(False,True));parent=ev[0]['id'];check('13_empty_pick_keeps_fullcaller',ev)
 reset(e,2.0,enemy={'Mana':2})
 _,ev=segment(e,trail,'14_unprotected_fulltrigger',[cooldown(),pick(),pitch()],lambda:e.trigger(e.items[SQ]))
 strict([x['type']for x in ev],[105,105,0]);strict([(x['target'],x['params']['amount'],x['parent'])for x in ev[:2]],[(1,-1,None),(0,1,None)])
 strict((e.characters['O'].mana,e.characters['P'].mana),(1,1));tail(trail)
 strict(e.histories.logger('O')['stackHistories'][105].values[-1],1);strict(e.histories.logger('P')['stackHistories'][105].values[-1],1)
 check('14_unprotected_loss_then_requested_gain_then_activation',ev)
 reset(e,3.0,enemy={'Mana':2},protect=1)
 _,ev=segment(e,trail,'15_protected_fulltrigger',[cooldown(),pick(),pitch()],lambda:e.trigger(e.items[SQ]))
 strict([x['type']for x in ev],[105,105,0]);strict(ev[0]['params'],dict(amount=1,used=False,reflected=False,protected=True))
 strict([(x['target'],x['params']['amount'],x['parent'])for x in ev[:2]],[(1,1,None),(0,1,None)])
 strict((e.characters['O'].mana,e.characters['P'].mana,e.characters['O'].buff_protect_stacks),(2,1,0));tail(trail)
 strict(e.histories.logger('O')['stackHistories'][105].values[-1],2);strict(e.histories.logger('P')['stackHistories'][105].values[-1],1)
 check('15_protected_actual_loss0_still_picked_gain1',ev)
 reset(e,3.5,enemy={'Lucky':1,'Mana':1})
 _,ev=segment(e,trail,'16_ordered_pick_explicit_parent',[pick(1,1)],lambda:e.steal_random_buff(e.items[SQ],1,parent))
 strict([x['type']for x in ev],[105,105]);strict([(x['target'],x['params']['amount'],x['parent'])for x in ev],[(1,-1,parent),(0,1,parent)])
 strict((e.characters['O'].lucky,e.characters['O'].mana,e.characters['P'].mana),(1,0,1))
 check('16_category_order_and_shared_actual_parent',ev)
 e.util_time=4.0;before=e.histories.item_metrics[SQ][4]
 def four():
  for _ in range(4):e.activate(e.items[SQ])
 _,ev=segment(e,trail,'17_three_pitch_fourth_limiter',[pitch(),pitch(),pitch()],four)
 strict([x['type']for x in ev],[0,0,0]);strict(e.histories.item_metrics[SQ][4],before+3)
 strict([x['method']for x in trail],['item_metric','tooltip','pitch']*3);strict(e.items[SQ].activations_this_frame,4)
 check('17_three_calls_pitch_then_fourth_suppressed',dict(events=ev,trail=trail))
 e.util_time=5.0;e.ended=True;before=e.histories.item_metrics[SQ][4]
 _,ev=segment(e,trail,'18_ended_allowed_pitch',[pitch()],lambda:e.activate(e.items[SQ]))
 strict(ev,[]);strict(e.histories.item_metrics[SQ][4],before);strict([x['method']for x in trail],['pitch']);strict(e.items[SQ].activations_this_frame,1)
 check('18_ended_allowed_numeric_tail_no_gameplay_event',trail)

def natural(h,mod,job):
 global STAGE,ACTIVE
 STAGE='19_one_natural_Source'
 b=initialize(h,job['layout'],CACHE_NAT,'natural');e=b._engine;ACTIVE=e;strict(type(e.random),h.CombatRandom)
 result=b.run(max_seconds=120.0);output=save('natural-source-output.json',result)
 strict(b.done,True);strict(e.finalized,True);strict(e.king_mode,False)
 strict(result['coverage']['formal_support'],75);strict(result['coverage']['catalog_registered'],77)
 strict(result['coverage']['status'],'EXPERIMENTAL_SOURCE_SQUIRREL_NOT_NATIVE_VALIDATED')
 strict(result['source_rng'],e.random.snapshot());strict(result['random_inputs'],e.random.audit)
 strict(result['fixture'],e.fixture);strict(result['initialization']['root_seed'],job['seed'])
 pitchrows=[x for x in e.random.audit if x['label']=='squirrel_activation_pitch:'+SQ]
 selection=[x for x in e.random.audit if x['label'].startswith('random_stack:'+SQ+':')]
 acts=[x for x in e.events if x['origin']==SQ and x['type']==0]
 losses=[x for x in e.events if x['origin']==SQ and 101<=x['type']<=107 and x['params'].get('amount',0)<0]
 gains=[x for x in e.events if x['origin']==SQ and 101<=x['type']<=107 and x['params'].get('amount',0)>0]
 summary=dict(status='FRESH_SOURCE_SQUIRREL_NOT_NATIVE',output=output,seed=job['seed'],items=sum(len(x['items'])for x in job['layout']['sides']),
  events=len(e.events),draws=len(e.random.audit),timers=26,winner=e.winner,simulated_seconds=result['final']['timestamp'],
  Squirrel_activations=len(acts),pitch_draws=len(pitchrows),selection_draws=len(selection),loss_events=len(losses),gain_events=len(gains),
  HIT=dict(repeated_steal='HIT'if len(losses)>1 else'NOT_HIT',activation_pitch='HIT'if pitchrows else'NOT_HIT',natural_protection_loss='NOT_CLAIMED_SYNTHETIC_CONTROL_ONLY'),
  source_rng=e.random.snapshot(),no_input_tuning=True)
 save('natural-summary.json',summary);check('19_fixed_natural_Source_terminal',summary)

def main():
 global STAGE
 started=time.monotonic();OUT.mkdir(exist_ok=False);status='FAILED';rows=[]
 try:
  verify_owner(OWN);verify_owner(PLAN/'owned-files.json','5bc9cb185707c492c09df71606dcec6f80a6c4e58ed59bf92bc37da07c3752ce')
  rows=verify_owner(SOURCE/'owned-files.json','c8fdff5b35ea530631e1ac6a07569b56f029b17d8ad8e2c4c8663766c7584130')
  pos=json.loads((PLAN/'cache-positive.json').read_bytes());zero=json.loads((PLAN/'cache-zero.json').read_bytes());job=json.loads((PLAN/'natural-job.json').read_bytes())
  sys.dont_write_bytecode=True;sys.pycache_prefix=str(OUT/'unused-bytecode-cache');sys.path.insert(0,str(SOURCE/'staged'));STAGE='import_frozen_candidate'
  h=importlib.import_module('headless');mod=importlib.import_module('native_replay_v8.engine')
  allowed={str((ROOT/r['path']).resolve())for r in rows if'/staged/'in r['path']};imports=[]
  for name,m in list(sys.modules.items()):
   if name in ('headless','original_rng','godot_pcg_integer')or name.startswith(('native_replay_v7','native_replay_v8')):
    path=str(Path(m.__file__).resolve());assert path in allowed,(name,path);imports.append(dict(name=name,path=path))
  save('imports.json',imports)
  for obj,name,label in [(h,'derive_stream_seeds','derive_stream_seeds'),(h.CombatRandom,'__init__','CombatRandom.__init__'),(h.GodotPCGInteger,'__init__','GodotPCGInteger.__init__'),
   (mod.CombatEngine,'__init__','Engine.__init__'),(mod.CombatEngine,'prepare_only','Engine.prepare_only'),(mod.CombatEngine,'activate_from_checkpoint','Engine.activate_from_checkpoint'),
   (mod.CombatEngine,'run','Engine.run'),(mod.CombatEngine,'add_speed','Engine.add_speed')]:counted(obj,name,label)
  for name in ('trigger','activate','steal_random_buff','pick_random_stacks','remove_stack','give_stack'):counted(mod.CombatEngine,name,'Engine.'+name)
  STAGE='ingress';ingress(h,mod,zero);components(h,mod,pos,zero);natural(h,mod,job)
  strict(len(PASSES),19);strict(COUNTS['Engine.__init__'],3);strict(COUNTS['Engine.prepare_only'],3);strict(COUNTS['Engine.run'],1)
  status='PASS_EXPERIMENTAL_SQUIRREL_SOURCE_COMPONENTS_AND_ONE_NATURAL_NOT_NATIVE'
 except BaseException as exc:
  save('first-error.json',dict(stage=STAGE,type=type(exc).__name__,message=str(exc),traceback=traceback.format_exc(),calls=COUNTS.copy()))
  if ACTIVE is not None:
   try:save('same-instance-failure.json',dict(events=ACTIVE.events,audit=ACTIVE.random.audit,snapshot=ACTIVE.snapshot(),histories=ACTIVE.histories.snapshot()))
   except BaseException as secondary:save('failure-diagnostic-error.json',dict(type=type(secondary).__name__,message=str(secondary)))
 finally:
  signal.alarm(0);after=[pin(ROOT/r['path'])for r in rows];strict(after,rows,'source_after');save('source-after.json',after)
  save('actual-prepare-boundaries.json',PREPARES);save('actual-start-speed-writes.json',SPEED_WRITES)
  result=dict(status=status,stage=STAGE,wall_seconds=time.monotonic()-started,passed_controls=len(PASSES),calls=COUNTS,source_refs_unchanged=len(after),native=0,Expected=0,old_tests=0,pool=0,auto_retry=False)
  save('result.json',result);save('owned-files.json',dict(files=[pin(p)for p in sorted(OUT.iterdir())if p.is_file()],no_more_writes=True))
 print(json.dumps(result));return 0 if status.startswith('PASS')else 1

if __name__=='__main__':
 def timeout(signum,frame):raise TimeoutError('phase490 whole harness35s wall deadline')
 signal.signal(signal.SIGALRM,timeout);signal.alarm(35);sys.exit(main())
