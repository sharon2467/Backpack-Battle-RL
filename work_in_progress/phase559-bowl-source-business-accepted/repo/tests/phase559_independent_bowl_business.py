"""Independent558 Source-only controls. Frozen exact Root release required; no Native input."""
import argparse,copy,dataclasses,functools,hashlib,importlib,json,math,os,random,re,resource,signal,stat,struct,sys,time,traceback,types,typing
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'data/phase558-source-bowl-treats'
PLAN=ROOT/'data/phase559-exact-business-source'
OUT=ROOT/'data/phase559-independent-business-first-001'
MODE='preflight';STAGE='preflight';ACTIVE=None
COUNTS={};SUCCEEDED={};DIRECT=[];PASSES=[];REJECTS=[];HOOKS=[];PREP=[];SETTERS=[];PREP_SPEED={}

def sha(b):return hashlib.sha256(b).hexdigest()


def pin(p):
 b=p.read_bytes();return dict(path=str(p.relative_to(ROOT)),size=len(b),sha256=sha(b))


def save(n,v):
 p=OUT/n;p.write_text(json.dumps(v,ensure_ascii=False,allow_nan=False,separators=(',',':'))+'\n');return pin(p)


def strict(a,b,w='$'):
 assert type(a)is type(b),(w,type(a).__name__,type(b).__name__)
 if isinstance(a,float):assert struct.pack('>d',a)==struct.pack('>d',b),(w,a,b)
 elif isinstance(a,dict):
  assert {(type(k),k)for k in a}=={(type(k),k)for k in b},(w,'keys')
  for k in a:strict(a[k],b[k],w+'.'+str(k))
 elif isinstance(a,(tuple,list)):
  assert len(a)==len(b),(w,len(a),len(b))
  for i,(x,y)in enumerate(zip(a,b)):strict(x,y,w+'['+str(i)+']')
 else:assert a==b,(w,a,b)


def call(label,fn,*a,**kw):
 row=dict(mode=MODE,stage=STAGE,label=label,status='ENTERED');DIRECT.append(row)
 try:v=fn(*a,**kw)
 except BaseException as ex:row.update(status='RAISED',type=type(ex).__name__,message=str(ex));raise
 row['status']='RETURNED';return v


def reject(label,fn,*a):
 draws=len(ACTIVE.random.audit)if ACTIVE is not None else None
 before={k:v for k,v in COUNTS.items()if any(z in k for z in('Engine.__init__','CombatRandom','derive_stream_seeds','PCG'))}
 try:call(label,fn,*a)
 except ValueError as ex:REJECTS.append(dict(label=label,error=str(ex)))
 else:raise AssertionError('expected rejection '+label)
 strict({k:v for k,v in COUNTS.items()if any(z in k for z in('Engine.__init__','CombatRandom','derive_stream_seeds','PCG'))},before)
 if draws is not None:strict(len(ACTIVE.random.audit),draws,'reject draws')


def check(name,details=None):
 row=dict(name=name,status='PASS',details=details);PASSES.append(row)
 with(OUT/'controls.jsonl').open('a')as f:f.write(json.dumps(row,allow_nan=False)+'\n')



def observe(obj,name,label):
 orig=getattr(obj,name)
 @functools.wraps(orig)
 def wrapper(*a,**kw):
  global ACTIVE
  key=MODE+':'+label;COUNTS[key]=COUNTS.get(key,0)+1
  e=a[0]if label.startswith('Engine.')else getattr(a[0],'engine',None)
  if label=='Engine.__init__':ACTIVE=e
  before=len(e.random.audit)if label=='Engine.prepare_only'else None
  row=None
  if label=='Tape._take':
   HOOKS.append(dict(mode=MODE,stage=STAGE,method='draw',kind=a[1],label=a[2],args=copy.deepcopy(a[3]),event_num=ACTIVE.event_num))
  if label=='Engine.give_bowl_double_activation_chance':
   row=dict(mode=MODE,stage=STAGE,source=a[1].instance_id,target=a[2].instance_id,source_prepared=a[1].cache_prepared,target_prepared=a[2].cache_prepared,before=a[2].double_activation_chance,event_num=e.event_num,draws=len(e.random.audit))
  tracked=('adjust_cooldown','trigger','_pet_cooldown_effect','_bowl_cooldown_effect','activate','give_random_buffs','give_least_buffs','steal_random_buff','flush_logging_queue','add_speed','give_stamina_regeneration')
  if label.startswith('Engine.')and name in tracked and hasattr(e,'events'):
   row=dict(mode=MODE,stage=STAGE,method=name,item=getattr(a[1],'instance_id',a[1])if len(a)>1 else None,event_num=e.event_num,events=len(e.events),draws=len(e.random.audit),phase='enter')
   if name in('add_speed','give_stamina_regeneration'):row['amount']=a[2]
   if name=='add_speed':row['caller']=sys._getframe(1).f_code.co_name;row['source']=getattr(sys._getframe(1).f_locals.get('item'),'instance_id',None)
   if name=='activate':row['frame_before']=a[1].activations_this_frame
   HOOKS.append(row)
  if label=='Histories.tooltip'and a[2]in(3,9):
   HOOKS.append(dict(mode=MODE,stage=STAGE,method='tooltip',item=a[1].instance_id,stat=a[2],global_event_num=e.event_num,effective_event=kw.get('event_num',e.event_num),speed=a[1].speed_scale))
  try:v=orig(*a,**kw)
  except BaseException:
   if row is not None:row['status']='RAISED'
   raise
  SUCCEEDED[key]=SUCCEEDED.get(key,0)+1
  if row is not None:row['status']='RETURNED'
  if label=='Engine.give_bowl_double_activation_chance':row.update(after=a[2].double_activation_chance,after_event_num=e.event_num,after_draws=len(e.random.audit));SETTERS.append(row)
  if label=='Engine.prepare_only':PREP.append(dict(mode=MODE,draws_before=before,draws_after=len(e.random.audit),activated=e.activated,order=list(e.preparation_order)))
  if label=='Engine.flush_logging_queue':HOOKS.append(dict(mode=MODE,stage=STAGE,method=name,phase='return',event_num=e.event_num,events=len(e.events),queue=len(e.signal_queue)))
  if label=='Engine.activate'and row is not None:row['frame_after']=a[1].activations_this_frame
  return v
 setattr(obj,name,wrapper)

def reset(e,all_beneficial=0):
 assert not e.signal_queue
 e.ended=False;e.pending_terminal=False;e.util_time=20.0;e.logging_mode=1
 for c in e.characters.values():
  c.dead=False;c.hp=999.0;c.stamina=5.0;c.stamina_regen=1.0;c.invulnerable=False;c.buff_protect_stacks=0;c.debuff_reflect_stacks=0;c.debuff_resist_stacks=0
  for k,f in c.buff_fields.items():
   name={100:'block',101:'lucky',102:'regeneration',103:'vampirism',104:'spikes',105:'mana',106:'empower',107:'heat',108:'poison',109:'blind',110:'cold'}[k]
   value=all_beneficial if 101<=k<=107 else 0
   setattr(c,name,value);f['permanentStacks']=value;f['temporaryStacks']=[];f['resistStacks']=0
   for n in('reflectChancePercent','resistChancePercent','cleanseProtectionChancePercent'):f[n]=0.0
 for i,it in e.items.items():
  it.last_activation_time=-1.0;it.activations_this_frame=0;it.trigger_time=0.0;it.bowl_speed_bonus_given=0.0
  if i in PREP_SPEED:it.speed_scale=PREP_SPEED[i]
  for k in it.buff_powers:it.buff_powers[k]=1.0;it.buff_amplification_chances[k]=0.0

def view(e):
 return dict(event_num=e.event_num,events=len(e.events),ended=e.ended,logging_mode=e.logging_mode,queue=len(e.signal_queue),
  sides={s:dict(mana=c.mana,lucky=c.lucky,regen=c.stamina_regen)for s,c in e.characters.items()},
  items={i:dict(chance=x.double_activation_chance,ledger=x.bowl_speed_bonus_given,speed=x.speed_scale,activations=x.activations,activation_frame=x.activations_this_frame,trigger_time=x.trigger_time,iteration_cooldown=x.iteration_cooldown)for i,x in e.items.items()if not x.definition['bag']})

def segment(m,e,name,rows,fn):
 global STAGE
 STAGE=name;e.random=m.TapeRandom(rows);ev=len(e.events);hi=len(HOOKS);before=view(e);allocated=e.event_num
 result=fn();raw=dict(name=name,before=before,after=view(e),result=result,events=copy.deepcopy(e.events[ev:]),allocated=[copy.deepcopy(v)for k,v in e.allocated_events.items()if k>allocated],audit=copy.deepcopy(e.random.audit),hooks=copy.deepcopy(HOOKS[hi:]))
 save('segment-'+name+'.json',raw);e.random.assert_consumed();strict(raw['audit'],rows,'exact rows');return raw

def gates(h,unit):
 global MODE,STAGE
 MODE='gate';STAGE='gate';fixture=call('validate_component',h.validate_experimental_nonking_layout,copy.deepcopy(unit))
 old=copy.deepcopy(unit)
 for s in old['sides']:s['items']=[x for x in s['items']if x['item_index']!=162]
 call('validate_without_bowl',h.validate_experimental_nonking_layout,old)
 bad=copy.deepcopy(unit);bad['sides'][0]['items'].append(dict(item_index=201,x=2,y=2,f=0,instance_id='P:outside'))
 reject('reject_outside',h.validate_experimental_nonking_layout,bad)
 bad=copy.deepcopy(unit);bad['sides'][0]['items'].append(dict(item_index=162,x=2,y=2,f=0,instance_id='P:duplicate'))
 reject('reject_duplicate_bowl',h.validate_experimental_nonking_layout,bad)
 reject('reject_old_initialize',h.initialize,unit,55901)
 reject('reject_old_batch',h.run_batch,[dict(layout=unit,seed=55901)])
 return fixture

def components(h,m,hs,fixture,contract,vectors):
 global MODE,STAGE,ACTIVE,PREP_SPEED
 MODE='unit';STAGE='construct';runtime=call('runtime_inputs',h.runtime_inputs,fixture,contract['order'])
 e=call('component_ctor',m.CombatEngine,fixture,m.TapeRandom([]),runtime);ACTIVE=e
 bowl=e.items['P:bowl'];sq=e.items['P:sq'];wolf=e.items['P:wolf'];other=e.items['O:bowl']
 call('initial_chance_guard',e._validate_bowl_double_activation_chance,sq)
 reject('reject_premature_setter',e.give_bowl_double_activation_chance,bowl,sq)
 reset(e);r=segment(m,e,'sq_zero',vectors['rows']['sq_zero'],lambda:call('sq_zero',e.trigger,sq))
 strict([x['type']for x in r['events']],[0]);strict(sq.double_activation_chance,0.0);strict(sq.trigger_time,4.0)
 strict([x['method']for x in r['hooks']].count('adjust_cooldown'),1);strict([x['method']for x in r['hooks']].count('_pet_cooldown_effect'),1)
 reset(e);e.util_time=0.0;STAGE='prepare';call('prepare_only',e.prepare_only)
 strict(PREP[-1]['draws_before'],2);strict(PREP[-1]['draws_after'],2);strict(PREP[-1]['activated'],False)
 strict(len(SETTERS),4)
 for x in SETTERS:
  strict(x['target_prepared'],contract['P_targets_prepared']if x['source']=='P:bowl'else contract['O_targets_prepared']);strict((x['before'],x['after']),(0.0,.2));strict(x['draws'],x['after_draws']);strict(x['event_num'],x['after_event_num'])
 cache={i:[x.instance_id for x in e.affected_items_cache[i]]for i in contract['bowl_caches']};strict(cache,contract['bowl_caches'])
 strict({i:[x.instance_id for x in e.affected_items_cache[i]]for i in contract['pet_caches']},contract['pet_caches'])
 strict([list(x)for x in bowl.definition['shape']],contract['bowl_shape']);strict([list(x)for x in bowl.definition['stars']],contract['bowl_stars'])
 for i,x in e.items.items():strict(x.double_activation_chance,.2 if i in contract['global_Pets']else 0.0)
 strict(bowl.speed_scale,.2);strict(other.speed_scale,0.0);strict(bowl.bowl_speed_bonus_given,0.0)
 PREP_SPEED={i:x.speed_scale for i,x in e.items.items()}
 save('component-prepared.json',dict(caches=cache,prepare=PREP[-1],setters=SETTERS,view=view(e)));check('01_geometry_global_spatial_domain',REJECTS.copy())
 for label,value in [('reject_missing',0.0),('reject_duplicate_value',.4),('reject_wrong_type',0)]:
  sq.double_activation_chance=value
  try:reject(label,e._validate_bowl_double_activation_chance,sq);strict(sq.double_activation_chance,value)
  finally:sq.double_activation_chance=.2
 reject('reject_unowned_target',e._validate_bowl_double_activation_chance,copy.copy(sq))
 reject('reject_duplicate_setter',e.give_bowl_double_activation_chance,bowl,sq)
 reject('reject_foreign_side',e.give_bowl_double_activation_chance,bowl,e.items['O:sq'])
 check('02_prepare_order_owned_contributions_no_repair')
 before=view(e);snap=call('prepared_snapshot',e.snapshot);strict(view(e),before)
 for i,x in snap['items'].items():strict(x['bowl_speed_bonus_given'],0.0);strict(x['double_activation_chance'],e.items[i].double_activation_chance)
 save('prepared-serialized-state.json',snap)
 cases=[('sq_fail',0,0,False,1,[0]),('sq_success',2,0,False,2,vectors['sq_success_types']),('sq_third',2,2,False,1,vectors['sq_third_types']),('sq_fourth',2,3,False,0,vectors['sq_fourth_types']),('sq_ended',0,0,True,0,[])]
 for name,mana,prior_frame,ended,activations,types_expected in cases:
  reset(e);e.characters['O'].mana=mana;e.characters['O'].buff_fields[105]['permanentStacks']=mana;e.ended=ended
  if prior_frame:sq.last_activation_time=20.0;sq.activations_this_frame=prior_frame
  start=sq.activations;r=segment(m,e,name,vectors['rows'][name],lambda name=name:call(name,e.trigger,sq))
  strict([x['type']for x in r['events']],types_expected);strict(sq.activations,start+activations);strict(sq.trigger_time,4.0);strict(sq.iteration_cooldown,4.0)
  methods=[x['method']for x in r['hooks']];strict(methods.count('adjust_cooldown'),1);strict(methods.count('_pet_cooldown_effect'),1 if name=='sq_fail'else 2)
  strict(sum(x['label']=='double_activation:P:sq'for x in r['audit']),1)
  assert all(x['parent']is None for x in r['events'])
  if mana:strict(e.characters['O'].mana,0);strict(e.characters['P'].mana,2)
  if prior_frame:strict(sq.activations_this_frame,prior_frame+2)
  if name=='sq_ended':strict(r['allocated'],[]);strict(e.characters['P'].stamina_regen,1.0)
 check('03_zero_positive_boundary_single_bookkeeping')
 check('04_Squirrel_full_effect_pitch_and_fourth_fifth_limiter')
 check('05_ended_no_new_trigger_cancellation')
 reset(e);r=segment(m,e,'wolf_success',vectors['rows']['wolf_success'],lambda:call('wolf_success',e.trigger,wolf))
 strict([x['type']for x in r['events']],vectors['wolf_types']);strict(wolf.trigger_time,5.0);assert all(x['parent']is None for x in r['events'])
 feedback=[x for x in r['hooks']if x['method']=='give_stamina_regeneration'];strict(len(feedback),6)
 expected=1.0
 for _ in range(6):expected+=(0.7*1.0)/100.0
 strict(e.characters['P'].stamina_regen,expected)
 for name,who,ledger,amount,after in [('bowl_normal',bowl,0.0,.25,25.0),('bowl_empty',other,0.0,None,25.0),('bowl_cap',bowl,100.0,None,100.0),('bowl_nearcap',bowl,90.0,.1,115.0)]:
  reset(e,10000 if name=='bowl_cap'else 0);who.bowl_speed_bonus_given=ledger
  targetids=contract['bowl_caches'][who.instance_id];speeds={i:e.items[i].speed_scale for i in targetids}
  r=segment(m,e,name,vectors['rows'][name],lambda name=name,who=who:call(name,e._bowl_cooldown_effect,who))
  strict(who.bowl_speed_bonus_given,after);strict([x['type']for x in r['events']],[0]if name=='bowl_cap'else[101,105,0]);strict(who.trigger_time,0.0)
  additions=[x for x in r['hooks']if x['method']=='add_speed']
  strict([x['item']for x in additions],targetids if amount is not None else[])
  if amount is not None:
   strict([x['amount']for x in additions],[amount]*len(targetids))
   for i in targetids:strict(e.items[i].speed_scale,speeds[i]+amount)
   stats=[x for x in r['hooks']if x['method']=='tooltip'and x['item']in targetids]
   strict([(x['item'],x['stat'])for x in stats],[(i,s)for i in targetids for s in(3,9)])
   bufflast=r['events'][-2]['id'];assert all(x['global_event_num']==bufflast and x['effective_event']==bufflast for x in stats)
   flush=max(i for i,x in enumerate(r['hooks'])if x['method']=='flush_logging_queue'and x.get('phase')=='return');firstspeed=min(i for i,x in enumerate(r['hooks'])if x['method']=='add_speed');assert flush<firstspeed
  strict(e.logging_mode,1);strict(e.signal_queue,[])
  if name=='bowl_cap':strict([x for x in r['hooks']if x['method']=='give_stamina_regeneration'],[])
 check('06_Bowl_speed_ledger_targets_empty_cap_nearcap')
 check('07_random_flush_current_event_speed_history_Wolper_feedback')
 for name,value in [('reject_ledger_int',0),('reject_ledger_negative',-1.0)]:
  prior_ledger=bowl.bowl_speed_bonus_given;bowl.bowl_speed_bonus_given=value
  try:reject(name,e._bowl_cooldown_effect,bowl);strict(bowl.bowl_speed_bonus_given,value)
  finally:bowl.bowl_speed_bonus_given=prior_ledger
 before=view(e);snap=call('final_snapshot',e.snapshot);strict(view(e),before);strict(snap['items']['P:bowl']['bowl_speed_bonus_given'],115.0);strict(snap['items']['P:sq']['double_activation_chance'],.2)
 save('component-final-snapshot.json',snap);save('component-events-histories.json',dict(events=e.events,allocated=e.allocated_events,histories=e.histories.snapshot()))
 strict(COUNTS.get('unit:Tape._take',0),vectors['unit_draws']);strict(COUNTS.get('unit:Engine.activate_from_checkpoint',0),0);strict(COUNTS.get('unit:Engine.step',0),0);strict(COUNTS.get('unit:Engine.run',0),0)
 check('08_real_serialized_fields_kernel_conservation')

def natural(h,job):
 global MODE,STAGE,ACTIVE
 MODE='natural';STAGE='natural_initialize';b=call('natural_initialize',h.initialize_experimental_nonking,copy.deepcopy(job['layout']),job['seed']);e=b._engine;ACTIVE=e
 save('natural-initialize.json',dict(initialization=b.initialization,prepare=PREP[-1],events=e.events,audit=e.random.audit,source_rng=e.random.snapshot()))
 strict(PREP[-1]['draws_before'],0);strict(PREP[-1]['draws_after'],0);strict(PREP[-1]['activated'],False);strict(type(e.random),h.CombatRandom)
 STAGE='natural_run';result=call('natural_run',b.run,max_seconds=job['max_seconds']);output=save('natural-source-output.json',result)
 save('natural-measured-hooks.json',[x for x in HOOKS if x['mode']=='natural'])
 STAGE='natural_postcheck';strict(e.finalized,True);strict(b.done,True);strict(e.king_mode,False);strict(sum(n['kind']=='timer'for n in e.runtime_inputs.data['nodes']),26)
 strict(result['coverage']['formal_support'],75);strict(result['coverage']['catalog_registered'],84);strict(result['initialization']['root_seed'],55901);strict(result['random_inputs'],e.random.audit);strict(result['source_rng'],e.random.snapshot())
 ah=[x for x in HOOKS if x['mode']=='natural'];effects=sum(x['method']=='_pet_cooldown_effect'for x in ah);triggers=sum(x['method']=='trigger'and x['item']in('P:sq','P:wolf','O:sq','O:wolf')for x in ah)
 measures=dict(extra_Pet_effect=effects-triggers,Bowl_activation=sum(x['type']==0 and x['origin']in('P:bowl','O:bowl')for x in e.events),Bowl_food_speed_calls=sum(x['method']=='add_speed'and x.get('caller')=='_bowl_cooldown_effect'for x in ah),
  Squirrel_pitch=sum(x['label'].startswith('squirrel_activation_pitch:')for x in e.random.audit),Squirrel_actual_loss=sum(x['origin']in('P:sq','O:sq')and 101<=x['type']<=107 and x['params'].get('amount',0)<0 for x in e.events),
  Wolper_positive_feedback=sum(x['method']=='give_stamina_regeneration'and x['amount']>0 for x in ah),Wolper_negative_feedback=sum(x['method']=='give_stamina_regeneration'and x['amount']<0 for x in ah),
  Bowl_cap=sum(e.items[i].bowl_speed_bonus_given>=100.0 for i in('P:bowl','O:bowl')))
 summary=dict(status='EXPERIMENTAL_SOURCE_NOT_NATIVE',output=output,seed=55901,items=23,timers=26,events=len(e.events),draws=len(e.random.audit),winner=e.winner,simulated_seconds=e.elapsed,measures=measures,HIT={k:'HIT'if v else'NOT_HIT'for k,v in measures.items()},Bowl_ledgers={i:e.items[i].bowl_speed_bonus_given for i in('P:bowl','O:bowl')},source_rng=e.random.snapshot(),limiter_ended_nearcap='Only directed synthetic coverage, not inferred natural HIT')
 save('natural-summary.json',summary);check('09_one_fixed_natural_Source_case',summary)

def frames(tb):
 while tb is not None:yield tb;tb=tb.tb_next


def main():
 global MODE,STAGE
 OUT.mkdir(exist_ok=False);start=time.monotonic();status='FAILED';refs=[]
 try:
  refs=json.loads((PLAN/'pins.json').read_bytes())['files']
  for row in refs:strict(pin(ROOT/row['path']),row,'source input before')
  save('source-input-before.json',refs)
  job=json.loads((PLAN/'natural-job.json').read_bytes());unit=json.loads((PLAN/'synthetic-layout.json').read_bytes());vectors=json.loads((PLAN/'vectors.json').read_bytes());contract=json.loads((PLAN/'preparation-contract.json').read_bytes());ledger=json.loads((PLAN/'call-ledger.json').read_bytes())
  sys.dont_write_bytecode=True;sys.pycache_prefix=str(OUT/'unused-bytecode-cache');sys.path.insert(0,str(SRC/'staged'))
  allowed={str((ROOT/x['path']).resolve())for x in refs}|{str((PLAN/'pins.json').resolve())}
  def audit(event,args):
   if event=='open':
    if isinstance(args[0],int):return
    p=str(Path(os.fsdecode(args[0])).resolve())
    if p.startswith(str(OUT)+os.sep):return
    mode,flags=args[1:3]
    if(isinstance(mode,str)and any(x in mode for x in'wa+'))or(isinstance(flags,int)and flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND)):raise PermissionError('outside-output write '+p)
    if p not in allowed:raise PermissionError('unlisted read '+p)
   if event in('subprocess.Popen','os.system','socket.connect'):raise PermissionError('external execution/network')
  sys.addaudithook(audit);STAGE='import';h=importlib.import_module('headless');m=importlib.import_module('native_replay_v8.engine');hs=importlib.import_module('native_replay_v8.histories')
  imports=[]
  for name,mod in list(sys.modules.items()):
   if name in('headless','original_rng','godot_pcg_integer')or name.startswith(('native_replay_v7','native_replay_v8')):
    p=Path(mod.__file__).resolve();assert str(p)in allowed;imports.append(dict(module=name,path=str(p),sha256=sha(p.read_bytes())))
  save('imports.json',imports)
  for obj,name,label in((h,'derive_stream_seeds','derive_stream_seeds'),(h.CombatRandom,'__init__','CombatRandom.__init__'),(h.GodotPCGInteger,'__init__','PCG.__init__')):observe(obj,name,label)
  for name in('__init__','prepare_only','activate_from_checkpoint','run','step','_validate_bowl_double_activation_chance','give_bowl_double_activation_chance','trigger','adjust_cooldown','_pet_cooldown_effect','_bowl_cooldown_effect','activate','give_random_buffs','give_least_buffs','steal_random_buff','flush_logging_queue','add_speed','give_stamina_regeneration'):observe(m.CombatEngine,name,'Engine.'+name)
  observe(hs.CombatHistories,'tooltip','Histories.tooltip')
  observe(hs.CombatHistories,'snapshot','Histories.snapshot')
  observe(m.TapeRandom,'_take','Tape._take')
  fixture=gates(h,unit);components(h,m,hs,fixture,contract,vectors);natural(h,job)
  strict([x['label']for x in DIRECT],ledger['direct_order']);strict(len(REJECTS),13);strict(len(PASSES),9)
  for mode in('unit','natural'):
   strict(COUNTS[mode+':Engine.__init__'],1);strict(COUNTS[mode+':Engine.prepare_only'],1)
  strict(COUNTS['natural:Engine.activate_from_checkpoint'],1);strict(COUNTS['natural:Engine.run'],1)
  status='PASS_EIGHT_SOURCE_FAMILIES_ONE_NATURAL_NOT_NATIVE'
 except BaseException as ex:
  save('first-error.json',dict(stage=STAGE,type=type(ex).__name__,error=str(ex),traceback=[dict(file=x.tb_frame.f_code.co_filename,line=x.tb_lineno,function=x.tb_frame.f_code.co_name)for x in frames(ex.__traceback__)],calls=COUNTS,direct=DIRECT))
  if ACTIVE is not None and hasattr(ACTIVE,'events'):save('same-instance-partial.json',dict(events=ACTIVE.events,audit=getattr(ACTIVE.random,'audit',None),view=view(ACTIVE)))
 finally:
  signal.alarm(0);after=[pin(ROOT/x['path'])for x in refs];save('source-input-after.json',after)
  if after!=refs:status='FAILED_SOURCE_INPUT_DRIFT'
  save('measured-hooks.json',dict(hooks=HOOKS,setters=SETTERS,prepare=PREP));save('actual-call-ledger.json',dict(direct=DIRECT,entered=COUNTS,succeeded=SUCCEEDED,expected_rejects=REJECTS))
  result=dict(status=status,stage=STAGE,passed=len(PASSES),direct_calls=len(DIRECT),expected_rejects=len(REJECTS),calls=COUNTS,succeeded=SUCCEEDED,wall_seconds=time.monotonic()-start,peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,source_input_pins=len(refs),source_input_unchanged=after==refs,Native=0,Expected=0,old_tests=0,auto_retry=False)
  save('result.json',result);save('owned-files.json',dict(files=[pin(p)for p in sorted(OUT.iterdir())if p.is_file()],sealed=True))
 print(json.dumps(result));return 0 if status.startswith('PASS')else 1


if __name__=='__main__':
 def deadline(sig,frame):raise TimeoutError('559 whole-process35s wall budget')
 signal.signal(signal.SIGALRM,deadline);signal.alarm(35);sys.exit(main())
