"""Independent finite Source-only Wolpertinger controls; no execution without Root release."""
import argparse,copy,dataclasses,functools,hashlib,importlib,json,math,os,random,re,signal,stat,struct,sys,time,traceback,types,typing
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'data/phase545-source-wolpertinger'
PLAN=ROOT/'data/phase546-exact-business-source'
OUT=ROOT/'data/phase546-independent-business-first-001'
W='P:wolf';W2='P:wolf2';W0='O:wolf0'
MODE='none';STAGE='preflight';ACTIVE=None
COUNTS={};SUCCEEDED={};DIRECT=[];PASSES=[];TRAIL=[];REGEN=[];STAT20=[];SPEED=[];PREP=[];SWORDS=[];REJECTS=[]

def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
 b=p.read_bytes();return dict(path=str(p.relative_to(ROOT)),size=len(b),sha256=sha(b))
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
def save(name,value):
 p=OUT/name;p.write_text(json.dumps(value,ensure_ascii=False,allow_nan=False,separators=(',',':'))+'\n');return pin(p)
def check(name,details=None):
 row=dict(name=name,status='PASS',details=details,calls=COUNTS.copy());PASSES.append(row)
 with(OUT/'controls.jsonl').open('a')as f:f.write(json.dumps(row,allow_nan=False)+'\n')
def call(label,fn,*args,**kwargs):
 row=dict(mode=MODE,stage=STAGE,label=label,status='ENTERED');DIRECT.append(row)
 try:v=fn(*args,**kwargs)
 except BaseException as exc:row.update(status='RAISED',type=type(exc).__name__,error=str(exc));raise
 row['status']='RETURNED';return v

def bits(v):return struct.pack('>d',v).hex()
class UnitTape:
 alignment='SOURCE_SYNTHETIC_TEST_OWNED_EXACT_ROWS'
 def __init__(self,rows,e):self.records=copy.deepcopy(rows);self.audit=[];self.position=0;self.e=e
 def take(self,kind,label,args):
  assert self.position<len(self.records),('unit tape exhausted',kind,label,args)
  row=self.records[self.position];valuekey='value'if kind=='randi_range'else'value_bits'
  strict({k:v for k,v in row.items()if k!=valuekey},dict(kind=kind,label=label,args=args),'exact unit row')
  v=row[valuekey]if kind=='randi_range'else struct.unpack('>d',bytes.fromhex(row[valuekey]))[0]
  if kind=='randi_range':assert type(v)is int and args[0]<=v<=args[1]
  else:assert math.isfinite(v) and struct.unpack('>d',bytes.fromhex(args[0]))[0]<=v<=struct.unpack('>d',bytes.fromhex(args[1]))[0]
  self.position+=1;self.audit.append(copy.deepcopy(row));TRAIL.append(dict(mode=MODE,stage=STAGE,method='draw',label=label,event_num=self.e.event_num,events=len(self.e.events)))
  return v
 def randi_range(self,label,lo,hi):return self.take('randi_range',label,[lo,hi])
 def randf_range(self,label,lo,hi):return self.take('randf_range',label,[bits(lo),bits(hi)])
 def randf(self,label):raise AssertionError('unplanned randf '+label)
 def assert_consumed(self):strict(self.position,len(self.records),'unit rows consumed')

def hist(e,s):return e.histories.logger(s)['characterStatHistories'][20].snapshot()
def view(e):
 return dict(event_num=e.event_num,event_count=len(e.events),logging_mode=e.logging_mode,queue_length=len(e.signal_queue),ended=e.ended,
  sides={s:dict(regen=c.stamina_regen,stamina=c.stamina,protect=c.buff_protect_stacks,
    stacks={n:getattr(c,n)for n in('block','lucky','regeneration','vampirism','spikes','mana','empower','heat','poison','blind','cold')},stat20=hist(e,s))for s,c in e.characters.items()},
  regen_calls=len(REGEN),stat20_calls=len(STAT20),draws=getattr(e.random,'position',len(e.random.audit)))
def instrument(obj,name,label):
 orig=getattr(obj,name)
 @functools.wraps(orig)
 def wrapped(*a,**kw):
  global ACTIVE
  key=MODE+':'+label;COUNTS[key]=COUNTS.get(key,0)+1
  e=a[0]if label.startswith('Engine.')else getattr(a[0],'engine',None)
  before=None
  if label=='Engine.__init__':ACTIVE=e
  if label=='Engine.prepare_only':before=len(e.random.audit)
  if label=='Engine.give_stamina_regeneration':
   side,amount=a[1:3];caller=sys._getframe(1);item=caller.f_locals.get('item')if caller.f_code.co_name=='on_stack_changed'else None
   before=dict(mode=MODE,stage=STAGE,side=side,amount=amount,receiver=getattr(item,'instance_id',None),event_num=e.event_num,before=e.characters[side].stamina_regen,history_before=hist(e,side))
  if label=='Histories.character'and a[2]==20:
   before=dict(mode=MODE,stage=STAGE,side=a[1],global_event_num=e.event_num,history_before=hist(e,a[1]))
  if label=='Engine.add_speed'and a[1].item_index==231:
   before=dict(mode=MODE,item=a[1].instance_id,amount=a[2],registered_before=a[1].wolpertinger_buff_listener_registered,coefficient_before=a[1].wolpertinger_stamina_regen_per_buff)
  if MODE=='unit'and label in('Engine.give_stack','Engine.get_least_stacks','Engine.give_least_buffs','Engine.emit','Engine.activate','Engine.flush_logging_queue'):
   TRAIL.append(dict(mode=MODE,stage=STAGE,method=name,event_num=e.event_num,events=len(e.events),origin=getattr(a[1],'instance_id',a[1])if len(a)>1 else None))
  if MODE=='natural'and label=='Engine.trigger'and a[1].instance_id=='P:sword':before=dict(stamina=e.characters['P'].stamina,regen=e.characters['P'].stamina_regen,event_index=len(e.events),time=e.time)
  v=orig(*a,**kw);SUCCEEDED[key]=SUCCEEDED.get(key,0)+1
  if label=='Engine.prepare_only':PREP.append(dict(mode=MODE,draws_before=before,draws_after=len(e.random.audit),activated=e.activated,order=list(e.preparation_order)))
  elif label=='Engine.give_stamina_regeneration':before.update(after=e.characters[a[1]].stamina_regen,history_after=hist(e,a[1]));REGEN.append(before)
  elif label=='Histories.character'and a[2]==20:before.update(history_after=hist(e,a[1]));STAT20.append(before)
  elif label=='Engine.add_speed'and a[1].item_index==231:before.update(speed_scale_after=a[1].speed_scale);SPEED.append(before)
  elif MODE=='natural'and label=='Engine.trigger'and a[1].instance_id=='P:sword':before.update(stamina_after=e.characters['P'].stamina,event_ids=[x['id']for x in e.events[before['event_index']:]]);SWORDS.append(before)
  return v
 setattr(obj,name,wrapped)

def reset_unit(e,amount=0):
 assert not e.signal_queue,'cannot reset pending real signals'
 e.ended=False;e.util_time=20.0;e.logging_mode=1
 for s,c in e.characters.items():
  c.stamina_regen=1.0;c.buff_protect_stacks=0;c.debuff_reflect_stacks=0;c.debuff_resist_stacks=0
  for category,fields in c.buff_fields.items():
   n={100:'block',101:'lucky',102:'regeneration',103:'vampirism',104:'spikes',105:'mana',106:'empower',107:'heat',108:'poison',109:'blind',110:'cold'}[category]
   value=amount if 101<=category<=107 else 0
   setattr(c,n,value);fields['permanentStacks']=value;fields['temporaryStacks']=[];fields['resistStacks']=0
   for k in('reflectChancePercent','resistChancePercent','cleanseProtectionChancePercent'):fields[k]=0.0
 for item in e.items.values():
  for k in item.buff_powers:item.buff_powers[k]=1.0;item.buff_amplification_chances[k]=0.0

def segment(e,name,rows,fn):
 global STAGE
 STAGE=name;e.random=UnitTape(rows,e);before=view(e);ev=len(e.events);trail=len(TRAIL);reg=len(REGEN);stats=len(STAT20)
 result=fn();raw=dict(name=name,before=before,after=view(e),result=result,events=copy.deepcopy(e.events[ev:]),audit=copy.deepcopy(e.random.audit),
  trail=copy.deepcopy(TRAIL[trail:]),regen=copy.deepcopy(REGEN[reg:]),stat20=copy.deepcopy(STAT20[stats:]),queue=copy.deepcopy(e.signal_queue))
 save('segment-'+name+'.json',raw);e.random.assert_consumed();return raw

def gate(h,layout,unit):
 global STAGE
 STAGE='gate';fixture=call('validate_experimental_nonking_layout',h.validate_experimental_nonking_layout,copy.deepcopy(unit))
 old=copy.deepcopy(layout)
 for side in old['sides']:side['items']=[x for x in side['items']if x['item_index']not in(164,199,201)]
 for label,fn in [('old_initialize',lambda:h.initialize(old,54601)),('old_squirrel',lambda:h.initialize_squirrel(old,54601)),('old_batch',lambda:h.run_batch([dict(layout=old,seed=54601)],keep_results=True))]:
  before=COUNTS.copy()
  try:call(label,fn)
  except ValueError as exc:strict(COUNTS,before,'before constructor/RNG gate');REJECTS.append(dict(label=label,error=str(exc)))
  else:raise AssertionError('old API admitted231: '+label)
 check('08_closed_gate',REJECTS.copy());return fixture

def components(h,m,fixture,v):
 global MODE,STAGE,ACTIVE
 MODE='unit';STAGE='component_construct';order=[x['instance_id']for s in fixture['sides']for x in s['items']]
 runtime=call('runtime_inputs',h.runtime_inputs,fixture,order)
 e=call('CombatEngine',m.CombatEngine,fixture,m.TapeRandom([]),runtime);ACTIVE=e;w=e.items[W]
 strict(sum(n['kind']=='timer'for n in e.runtime_inputs.data['nodes']),26)
 for name in(W,W2,W0):strict((e.items[name].wolpertinger_buff_listener_registered,e.items[name].wolpertinger_stamina_regen_per_buff),(False,None))
 e.util_time=0.0;e.characters['P'].base_stamina_regen=v['P_base_stamina_regen']
 pre=len(REGEN);call('pre_registration_gain',e.give_stack,w,'P','Lucky',1);strict(len(REGEN),pre)
 reset_unit(e);call('prepare_only',e.prepare_only);strict(PREP[-1]['draws_before'],0);strict(PREP[-1]['draws_after'],0);strict(e.activated,False)
 coef=(0.7*0.1)/100.0;assert bits(coef)!=bits((0.7/100.0)*0.1)
 caches={n:[x.instance_id for x in e.affected_items(e.items[n])]for n in(W,W2,W0)}
 strict(caches,v['caches']);speed=[x for x in SPEED if x['mode']=='unit'];strict([x['item']for x in speed],[W,W2,W0])
 for x in speed:
  strict(x['amount'],v['speed_additions'][x['item']]);strict((x['registered_before'],x['coefficient_before']),(False,None));strict(x['speed_scale_after'],x['amount'])
 for n in(W,W2):strict(e.items[n].wolpertinger_stamina_regen_per_buff,coef)
 strict(e.items[W0].wolpertinger_stamina_regen_per_buff,(0.7*1.0)/100.0)
 save('component-prepared.json',dict(caches=caches,speeds=speed,prepare=PREP[-1],view=view(e)));check('06_prepare_cache_order_zero_and_coefficient')
 reset_unit(e);r=segment(e,'01_ordered',v['draws']['ordered'],lambda:call('get_least_ordered',e.get_least_stacks,w,3))
 strict(list(r['result'].items()),[tuple(x)for x in v['ordered_picks']]);strict(r['events'],[]);strict(r['regen'],[]);check('01_ordered_ties_virtual_prior',r['result'])
 reset_unit(e);parent=call('emit_parent',e.emit,W,'Activation')['id']
 r=segment(e,'02_aggregate',v['draws']['aggregate'],lambda:call('give_least_aggregate',e.give_least_buffs,w,3,parent,[101,105]))
 strict(r['result'],None);strict([(x['type'],x['params']['amount'],x['parent'])for x in r['events']],[(101,1,parent),(105,2,parent)])
 drawindices=[i for i,x in enumerate(r['trail'])if x['method']=='draw'];grantindices=[i for i,x in enumerate(r['trail'])if x['method']=='give_stack'];assert max(drawindices)<min(grantindices)
 strict([x['receiver']for x in r['regen']],[W,W2,W,W2]);expected=1.0
 for amount in(1,1,2,2):expected+=amount*coef
 strict(e.characters['P'].stamina_regen,expected);check('02_preselect_then_aggregate_parent_order')
 reset_unit(e);r=segment(e,'03_singleton',v['draws']['singleton'],lambda:call('get_least_singleton',e.get_least_stacks,w,1,None,[105]));strict(r['result'],{105:1})
 for label,count,grant in [('03_zero',0,False),('03_negative',-1,False),('03_zero_grant',0,True)]:
  fn=(lambda:call('give_least_zero',e.give_least_buffs,w,0,None,[]))if grant else(lambda count=count:call('get_least_count_'+str(count),e.get_least_stacks,w,count,None,[]))
  r=segment(e,label,[],fn);strict(r['result'],None if grant else{});strict(r['events'],[]);strict(r['regen'],[])
 reset_unit(e,10001);STAGE='03_sentinel';e.random=UnitTape([],e)
 try:call('get_least_sentinel_reject',e.get_least_stacks,w,1)
 except ValueError as exc:assert '10000 sentinel' in str(exc);save('sentinel-rejection.json',dict(error=str(exc),view=view(e)))
 else:raise AssertionError('positive empty sentinel admitted')
 e.random.assert_consumed();check('03_singleton_zero_negative_sentinel')
 reset_unit(e,10000);r=segment(e,'04_full_cap_trigger',v['draws']['cap_trigger'],lambda:call('trigger_cap',e.trigger,w))
 strict([x['type']for x in r['events']],[0]);strict(r['regen'],[]);strict(w.activations,1);strict([x['params']for x in r['events']],[{}])
 reset_unit(e);w.buff_amplification_chances[101]=100.0;call('set_logging_delayed',e.set_logging_mode,2)
 r=segment(e,'04_amplified_queued',v['draws']['amplified_delayed'],lambda:call('give_least_amplified',e.give_least_buffs,w,3,None,[101,105]))
 strict(r['events'],[]);strict(r['regen'],[]);strict(e.logging_mode,2);strict(e.characters['P'].lucky,2);strict(e.characters['P'].mana,2);strict(e.characters['P'].stamina_regen,1.0)
 strict([(x[0]['type'],x[0]['params']['amount'])for x in e.signal_queue],[(101,2),(105,2)])
 marker=call('emit_later_marker',e.emit,W,'Activation')['id'];r=segment(e,'04_explicit_flush',[],lambda:call('flush_logging_queue',e.flush_logging_queue))
 strict([x['type']for x in r['events']],[101,105,0]);strict([x['receiver']for x in r['regen']],[W,W2,W,W2]);strict([x['global_event_num']for x in r['stat20']],[marker]*4)
 expected=1.0
 for _ in range(4):expected+=2*coef
 strict(e.characters['P'].stamina_regen,expected);strict([x['history_after']['event_numbers'][-1]for x in r['stat20']],[marker]*4);strict(e.logging_mode,1);check('04_cap_fullcaller_amplification_and_real_delayed_history')
 reset_unit(e)
 operations=[('gain',[],lambda:call('gain_mana',e.give_stack,w,'P','Mana',4),[4*coef,4*coef]),
  ('loss',[],lambda:call('lose_mana',e.remove_stack,w,'P','Mana',1),[-coef,-coef]),
  ('use',[],lambda:call('use_mana',e.try_use_mana,w,1),[-coef,-coef]),
  ('protected',[],lambda:call('protected_loss',e.remove_stack,w,'P','Mana',1),[]),
  ('block',[],lambda:call('give_block',e.give_stack,w,'P','Block',1),[]),
  ('poison',v['draws']['excluded_debuff'],lambda:call('give_poison',e.give_stack,w,'P','Poison',1),[]),
  ('opponent',[],lambda:call('give_opponent',e.give_stack,w,'O','Lucky',1),[(0.7*1.0)/100.0]),
  ('capped',[],lambda:call('capped_gain',e.give_stack,w,'P','Lucky',1),[]),
  ('zero_dispatch',[],lambda:call('explicit_zero_dispatch',e._emit_and_log,None,('P','Mana',0)),[0.0,0.0]),
  ('ended',[],lambda:call('ended_dispatch',e._emit_and_log,None,('P','Mana',1)),[])]
 for label,rows,fn,expected in operations:
  if label=='protected':e.characters['P'].buff_protect_stacks=1
  if label=='capped':e.characters['P'].lucky=10000;e.characters['P'].buff_fields[101]['permanentStacks']=10000
  if label=='ended':e.ended=True
  r=segment(e,'05_'+label,rows,fn);strict([x['amount']for x in r['regen']],expected)
  if label in('loss','use'):strict(r['events'][-1]['params']['amount'],-1)
  if label=='use':strict(r['events'][-1]['params']['used'],True)
  if label=='protected':strict(e.characters['P'].mana,2);strict(e.characters['P'].buff_protect_stacks,0);strict(r['events'][-1]['params']['protected'],True)
  if label=='opponent':strict([x['receiver']for x in r['regen']],[W0])
  if label=='zero_dispatch':strict(len(r['stat20']),2);strict(r['before']['sides']['P']['stat20'],r['after']['sides']['P']['stat20'])
 e.ended=False;check('05_actual_feedback_exclusions_zero_dispatch_ended')
 r=segment(e,'07_direct_zero_regen',[],lambda:call('give_stamina_regeneration_zero',e.give_stamina_regeneration,'P',0.0))
 strict(len(r['stat20']),1);strict(r['before']['sides']['P']['stat20'],r['after']['sides']['P']['stat20']);strict(len([x for x in TRAIL if x['method']=='draw']),v['unit_expected_draws'])
 check('07_binary64_coefficient_order_current_global_history_zero_dedup')
 save('component-events-history.json',dict(events=e.events,allocated=e.allocated_events,histories=e.histories.snapshot(),view=view(e)))
 strict(COUNTS.get('unit:Engine.activate_from_checkpoint',0),0);strict(COUNTS.get('unit:Engine.step',0),0);strict(COUNTS.get('unit:Engine.run',0),0)

def natural(h,job):
 global MODE,STAGE,ACTIVE
 MODE='natural';STAGE='natural_initialize';b=call('initialize_experimental_nonking',h.initialize_experimental_nonking,copy.deepcopy(job['layout']),job['seed']);e=b._engine;ACTIVE=e
 save('natural-initialize.json',dict(initialization=b.initialization,prepare=PREP[-1],events=e.events,audit=e.random.audit,
  wolf_cache=[x.instance_id for x in e.affected_items(e.items[W])],source_rng=e.random.snapshot()))
 strict(PREP[-1]['draws_before'],0);strict(PREP[-1]['draws_after'],0);strict(PREP[-1]['activated'],False)
 strict(type(e.random),h.CombatRandom);strict(b.initialization['source_extension'],h.EXPERIMENTAL_NONKING_EXTENSION)
 STAGE='natural_run';result=call('HeadlessBattle.run',b.run,max_seconds=job['max_seconds']);output=save('natural-source-output.json',result)
 save('natural-measured-hooks.json',dict(regen=[x for x in REGEN if x['mode']=='natural'],sword_triggers=SWORDS,speeds=[x for x in SPEED if x['mode']=='natural']))
 STAGE='natural_postcheck';strict(e.finalized,True);strict(b.done,True);strict(e.king_mode,False);strict(sum(n['kind']=='timer'for n in e.runtime_inputs.data['nodes']),26)
 strict(result['coverage']['formal_support'],75);strict(result['coverage']['catalog_registered'],82);strict(result['coverage']['experimental_items'],[164,199,201,231]);strict(result['coverage']['experimental_kinds'],[64,164,197,199,201,231])
 strict(result['initialization']['root_seed'],54601);strict(result['random_inputs'],e.random.audit);strict(result['source_rng'],e.random.snapshot())
 ev=e.events;measures=dict(Wolf_activation=sum(x['origin']==W and x['type']==0 for x in ev),Wolf_gain=sum(x['origin']==W and 101<=x['type']<=107 and x['params'].get('amount',0)>0 for x in ev),
  Wolf_least_draws=sum(x['label'].startswith('least_buff:'+W+':')for x in e.random.audit),
  positive_feedback=sum(x['mode']=='natural'and x['side']=='P'and x['amount']>0 for x in REGEN),negative_feedback=sum(x['mode']=='natural'and x['side']=='P'and x['amount']<0 for x in REGEN),
  Squirrel_loss=sum(x['origin']=='P:squirrel'and 101<=x['type']<=107 and x['params'].get('amount',0)<0 for x in ev),Sapphire_used=sum(x['origin']=='P:sapphire'and x['type']==105 and x['params'].get('used')is True for x in ev),
  Amethyst_loss=sum(x['origin']=='O:amethyst'and 101<=x['type']<=107 and x['params'].get('amount',0)<0 for x in ev),Sword_stamina_payment=sum(x['stamina_after']<x['stamina']for x in SWORDS),Sword_regen_above_base=sum(x['regen']>1.0 for x in SWORDS))
 summary=dict(status='EXPERIMENTAL_SOURCE_NOT_NATIVE',output=output,seed=54601,items=22,timers=26,events=len(ev),draws=len(e.random.audit),winner=e.winner,simulated_seconds=e.elapsed,
  measures=measures,HIT={k:'HIT'if v else'NOT_HIT'for k,v in measures.items()},source_rng=e.random.snapshot(),zero_cap_protection='DIRECTED_SYNTHETIC_ONLY; not inferred natural HIT',counterfactual_stamina_effect='NOT_CLAIMED')
 save('natural-summary.json',summary);check('09_one_fixed_natural_integration',summary)

def trace_frames(tb):
 while tb is not None:
  yield tb;tb=tb.tb_next

def main():
 global MODE,STAGE,ACTIVE
 OUT.mkdir(exist_ok=False);started=time.monotonic();status='FAILED';refs=[]
 try:
  meta=json.loads((PLAN/'pins.json').read_bytes());refs=meta['files']
  for row in refs:strict(pin(ROOT/row['path']),row,'before pin')
  save('source-input-before.json',refs);job=json.loads((PLAN/'natural-job.json').read_bytes());unit=json.loads((PLAN/'synthetic-layout.json').read_bytes());vectors=json.loads((PLAN/'vectors.json').read_bytes())
  sys.dont_write_bytecode=True;sys.pycache_prefix=str(OUT/'unused-bytecode-cache');sys.path.insert(0,str(SRC/'staged'))
  allowed={str((ROOT/x['path']).resolve())for x in refs}|{str((PLAN/'pins.json').resolve())}
  def audit(event,args):
   if event=='open':
    path=args[0]
    if isinstance(path,int):return
    p=str(Path(os.fsdecode(path)).resolve())
    if p.startswith(str(OUT)+os.sep):return
    mode=args[1];flags=args[2]
    if (isinstance(mode,str)and any(c in mode for c in'wa+'))or(isinstance(flags,int)and flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND)):raise PermissionError('outside-output write denied: '+p)
    if p not in allowed:raise PermissionError('unlisted read denied: '+p)
   if event in('subprocess.Popen','os.system','socket.connect'):raise PermissionError('external execution/network denied')
  sys.addaudithook(audit);STAGE='import_frozen';h=importlib.import_module('headless');m=importlib.import_module('native_replay_v8.engine');hs=importlib.import_module('native_replay_v8.histories')
  imports=[]
  for name,mod in list(sys.modules.items()):
   if name in('headless','original_rng','godot_pcg_integer')or name.startswith(('native_replay_v7','native_replay_v8')):
    p=Path(mod.__file__).resolve();assert str(p)in allowed;imports.append(dict(module=name,path=str(p),sha256=sha(p.read_bytes())))
  save('imports.json',imports)
  for obj,name,label in((h,'derive_stream_seeds','derive_stream_seeds'),(h.CombatRandom,'__init__','CombatRandom.__init__'),(h.GodotPCGInteger,'__init__','PCG.__init__')):instrument(obj,name,label)
  for name in('__init__','prepare_only','activate_from_checkpoint','run','step','give_stamina_regeneration','get_least_stacks','give_least_buffs','give_stack','remove_stack','try_use_mana','on_stack_changed','emit','activate','trigger','add_speed','flush_logging_queue'):
   instrument(m.CombatEngine,name,'Engine.'+name)
  instrument(hs.CombatHistories,'character','Histories.character')
  MODE='gate';fixture=gate(h,job['layout'],unit);components(h,m,fixture,vectors);natural(h,job)
  strict(len(PASSES),9);strict(COUNTS['unit:Engine.__init__'],1);strict(COUNTS['natural:Engine.__init__'],1);strict(COUNTS['unit:Engine.prepare_only'],1);strict(COUNTS['natural:Engine.prepare_only'],1);strict(COUNTS['natural:Engine.activate_from_checkpoint'],1);strict(COUNTS['natural:Engine.run'],1)
  expected=json.loads((PLAN/'call-ledger.json').read_bytes())['direct_order'];strict([x['label']for x in DIRECT],expected,'exact direct invocation sequence')
  status='PASS_EIGHT_SOURCE_FAMILIES_ONE_NATURAL_NOT_NATIVE'
 except BaseException as exc:
  save('first-error.json',dict(stage=STAGE,type=type(exc).__name__,message=str(exc),traceback=[dict(filename=fr.tb_frame.f_code.co_filename,line=fr.tb_lineno,function=fr.tb_frame.f_code.co_name)for fr in trace_frames(exc.__traceback__)],calls=COUNTS.copy(),direct=copy.deepcopy(DIRECT)))
  if ACTIVE is not None and hasattr(ACTIVE,'events'):
   save('same-instance-failure.json',dict(events=ACTIVE.events,audit=getattr(ACTIVE.random,'audit',None),view=view(ACTIVE)))
 finally:
  signal.alarm(0)
  after=[pin(ROOT/x['path'])for x in refs];save('source-input-after.json',after)
  if after!=refs:status='FAILED_SOURCE_OR_INPUT_DRIFT'
  save('all-measured-hooks.json',dict(regen=REGEN,stat20=STAT20,speed=SPEED,prepare=PREP,trail=TRAIL,sword=SWORDS))
  save('actual-call-ledger.json',dict(direct=DIRECT,entered=COUNTS,succeeded=SUCCEEDED))
  result=dict(status=status,stage=STAGE,passed=len(PASSES),expected_groups=9,gate_rejects=len(REJECTS),calls=COUNTS,succeeded=SUCCEEDED,direct_calls=len(DIRECT),wall_seconds=time.monotonic()-started,source_input_pins=len(refs),source_input_unchanged=after==refs,Native=0,Expected=0,pool=0,old_tests=0,auto_retry=False)
  save('result.json',result);save('owned-files.json',dict(files=[pin(p)for p in sorted(OUT.iterdir())if p.is_file()],sealed=True))
 print(json.dumps(result));return 0 if status.startswith('PASS')else 1
if __name__=='__main__':
 def timeout(signum,frame):raise TimeoutError('phase54635second whole-process wall deadline')
 signal.signal(signal.SIGALRM,timeout);signal.alarm(35);sys.exit(main())
