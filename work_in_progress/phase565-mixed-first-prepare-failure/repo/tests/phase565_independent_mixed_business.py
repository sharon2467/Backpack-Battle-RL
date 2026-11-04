"""Independent564 Source-only controls. Frozen exact Root release required; no Native input."""
import argparse,copy,dataclasses,functools,hashlib,importlib,json,math,os,random,re,resource,signal,stat,struct,sys,time,traceback,types,typing
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'data/phase564-source-finite-mixed'
PLAN=ROOT/'data/phase565-exact-business-source'
OUT=ROOT/'data/phase565-independent-business-first-001'
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
  setter=name in('give_bowl_double_activation_chance','give_double_attack_effect_chance')
  row=None
  if setter:
   field='double_activation_chance'if name.startswith('give_bowl')else'double_attack_effect_chance'
   row=dict(mode=MODE,stage=STAGE,method=name,source=a[1].instance_id,target=a[2].instance_id,source_prepared=a[1].cache_prepared,target_prepared=a[2].cache_prepared,before=getattr(a[2],field),event_num=e.event_num,draws=len(e.random.audit))
  tracked=('trigger','adjust_cooldown','_pet_cooldown_effect','_bowl_cooldown_effect','activate','attack_effect_count','attack','weapon_attack','pre_item_damage','late_item_damage','on_item_dealt_damage','on_character_attacked','on_character_damaged','give_random_buffs','give_least_buffs','steal_random_buff','flush_logging_queue','add_speed','give_stamina_regeneration')
  if label.startswith('Engine.')and name in tracked and hasattr(e,'events'):
   row=dict(mode=MODE,stage=STAGE,method=name,item=getattr(a[1],'instance_id',a[1])if len(a)>1 else None,event_num=e.event_num,events=len(e.events),draws=len(e.random.audit),phase='enter')
   if name in('add_speed','give_stamina_regeneration'):row['amount']=a[2]
   if name=='add_speed':row['caller']=sys._getframe(1).f_code.co_name;row['source']=getattr(sys._getframe(1).f_locals.get('item'),'instance_id',None)
   if name=='activate':row['frame_before']=a[1].activations_this_frame
   HOOKS.append(row)
  if label=='Tape._take':HOOKS.append(dict(mode=MODE,stage=STAGE,method='draw',kind=a[1],label=a[2],args=copy.deepcopy(a[3]),event_num=ACTIVE.event_num))
  if label=='Histories.tooltip'and a[2]in(3,9):HOOKS.append(dict(mode=MODE,stage=STAGE,method='tooltip',item=a[1].instance_id,stat=a[2],global_event_num=e.event_num,effective_event=kw.get('event_num',e.event_num),speed=a[1].speed_scale))
  try:v=orig(*a,**kw)
  except BaseException:
   if row is not None:row['status']='RAISED'
   raise
  SUCCEEDED[key]=SUCCEEDED.get(key,0)+1
  if row is not None:row['status']='RETURNED'
  if setter:row.update(after=getattr(a[2],field),after_event_num=e.event_num,after_draws=len(e.random.audit));SETTERS.append(row)
  if name=='attack_effect_count':row['count']=v
  if label=='Engine.prepare_only':PREP.append(dict(mode=MODE,draws_before=before,draws_after=len(e.random.audit),activated=e.activated,order=list(e.preparation_order)))
  if label=='Engine.flush_logging_queue':HOOKS.append(dict(mode=MODE,stage=STAGE,method=name,phase='return',event_num=e.event_num,events=len(e.events),queue=len(e.signal_queue)))
  if label=='Engine.activate'and row is not None:row['frame_after']=a[1].activations_this_frame
  return v
 setattr(obj,name,wrapper)


def reset(e):
 assert not e.signal_queue
 e.ended=False;e.pending_terminal=False;e.util_time=20.0;e.logging_mode=1
 for c in e.characters.values():
  c.dead=False;c.hp=999.0;c.stamina=5.0;c.stamina_regen=1.0;c.invulnerable=False;c.buff_protect_stacks=0;c.debuff_reflect_stacks=0;c.debuff_resist_stacks=0;c.accuracy.reset(-1.0);c.critical.reset(-1.0)
  for k,f in c.buff_fields.items():
   name={100:'block',101:'lucky',102:'regeneration',103:'vampirism',104:'spikes',105:'mana',106:'empower',107:'heat',108:'poison',109:'blind',110:'cold'}[k]
   setattr(c,name,0);f['permanentStacks']=0;f['temporaryStacks']=[];f['resistStacks']=0
   for n in('reflectChancePercent','resistChancePercent','cleanseProtectionChancePercent'):f[n]=0.0
 for i,it in e.items.items():
  it.last_activation_time=-1.0;it.activations_this_frame=0;it.trigger_time=0.0;it.bowl_speed_bonus_given=0.0;it.bonus_damage=0;it.bonus_max_only=0;it.varying_damage=0;it.crit_chance=0.0;it.chance_rng.reset();it.damage_range.acc=0.0
  if i in PREP_SPEED:it.speed_scale=PREP_SPEED[i]
  for k in it.buff_powers:it.buff_powers[k]=1.0;it.buff_amplification_chances[k]=0.0


def view(e):
 return dict(event_num=e.event_num,events=len(e.events),ended=e.ended,logging_mode=e.logging_mode,queue=len(e.signal_queue),
  sides={s:dict(hp=c.hp,mana=c.mana,block=c.block,lucky=c.lucky,spikes=c.spikes,regen=c.stamina_regen)for s,c in e.characters.items()},
  items={i:dict(pet_chance=x.double_activation_chance,weapon_chance=x.double_attack_effect_chance,ledger=x.bowl_speed_bonus_given,speed=x.speed_scale,activations=x.activations,activation_frame=x.activations_this_frame,trigger_time=x.trigger_time,iteration_cooldown=x.iteration_cooldown,bonus=x.bonus_damage)for i,x in e.items.items()if not x.definition['bag']})


def segment(m,e,name,rows,fn):
 global STAGE
 STAGE=name;e.random=m.TapeRandom(rows);ev=len(e.events);hi=len(HOOKS);before=view(e);allocated=e.event_num
 result=fn();raw=dict(name=name,before=before,after=view(e),result=result,events=copy.deepcopy(e.events[ev:]),allocated=[copy.deepcopy(v)for k,v in e.allocated_events.items()if k>allocated],audit=copy.deepcopy(e.random.audit),hooks=copy.deepcopy(HOOKS[hi:]))
 save('segment-'+name+'.json',raw);e.random.assert_consumed();strict(raw['audit'],rows,'exact rows');return raw

def gates(h,unit):
 global MODE,STAGE
 MODE='gate';STAGE='gate';fixture=call('validate_component',h.validate_experimental_nonking_layout,copy.deepcopy(unit))
 # Geometrically valid O additions ensure rejection reaches mixed admission.
 for label,k,fragment in [('reject_duplicate_bowl',162,'at most one162'),('reject_duplicate_skill',385,'at most one385'),('reject_outside',201,'finite twelve-ID')]:
  bad=copy.deepcopy(unit);bad['sides'][1]['items'].append(dict(item_index=k,x=2,y=2,f=0,instance_id='O:extra'))
  # Duplicate source belongs to P, where its original lives; move the extra to free P cells.
  if k in(162,385):bad['sides'][1]['items'].pop();bad['sides'][0]['items'].append(dict(item_index=k,x=3,y=0,f=0,instance_id='P:extra'))
  reject(label,h.validate_experimental_nonking_layout,bad);assert fragment in REJECTS[-1]['error']
 bad=copy.deepcopy(unit);bad['sides'][0]['character_class']=2;reject('reject_class',h.validate_experimental_nonking_layout,bad);assert 'class0' in REJECTS[-1]['error']
 reject('reject_old_initialize',h.initialize,unit,56501);reject('reject_old_batch',h.run_batch,[dict(layout=unit,seed=56501)])
 check('01_complete_mixed_admission_both_multiplicities',copy.deepcopy(REJECTS));return fixture


def prestack(e,side,name,n):
 setattr(e.characters[side],name.lower(),n);e.characters[side].buff_fields[{'Mana':105,'Block':100}[name]]['permanentStacks']=n



def weapon_contract(raw,identity,late=True):
 hooks=[x for x in raw['hooks']if x.get('item')==identity]
 for method,n in [('attack_effect_count',1),('pre_item_damage',2),('late_item_damage',2 if late else 0),('on_item_dealt_damage',2),('attack',1),('activate',1)]:strict(sum(x['method']==method for x in hooks),n,identity+':'+method)
 strict([x['count']for x in hooks if x['method']=='attack_effect_count'],[2])
 for method in('on_character_attacked','on_character_damaged'):strict(sum(x['method']==method for x in raw['hooks']),1)



def components(h,m,hs,fixture,contract,vectors):
 global MODE,STAGE,ACTIVE,PREP_SPEED
 MODE='unit';STAGE='construct';runtime=call('runtime_inputs',h.runtime_inputs,fixture,contract['order']);e=call('component_ctor',m.CombatEngine,fixture,m.TapeRandom([]),runtime);ACTIVE=e;e.util_time=0.0
 bowl=e.items['P:bowl'];sq=e.items['P:sq'];skill=e.items['P:enchanted'];staff=e.items['P:staff'];spear=e.items['P:spear'];thorn=e.items['P:thorn'];lucky=e.items['P:luckybow']
 STAGE='prepare';call('prepare_only',e.prepare_only);strict((PREP[-1]['draws_before'],PREP[-1]['draws_after'],PREP[-1]['activated']),(0,0,False))
 strict(PREP[-1]['order'],contract['order']);strict(len(SETTERS),6)
 for x in SETTERS:
  pet=x['source']=='P:bowl';strict(x['source_prepared'],True);strict(x['target_prepared'],not pet);strict((x['before'],x['after']),(0.0,.2 if pet else .25));strict(x['draws'],x['after_draws']);strict(x['event_num'],x['after_event_num'])
 for key in('bowl_caches','skill_caches','pet_caches'):strict({i:[x.instance_id for x in e.affected_items_cache[i]]for i in contract[key]},contract[key])
 for i,x in e.items.items():strict(x.double_activation_chance,.2 if i in contract['global_Pets']else 0.0);strict(x.double_attack_effect_chance,.25 if i in contract['skill_receivers']else 0.0)
 for i in contract['spatial_false_skill']:assert e.items[i].cells & skill.stars;assert e.items[i]not in e.affected_items_cache[skill.instance_id]
 strict(spear.spear_block_removal,4);strict(sq.speed_scale,.15);strict(bowl.speed_scale,.2);strict(e.items['P:wolf'].speed_scale,0.0)
 PREP_SPEED={i:x.speed_scale for i,x in e.items.items()};save('component-prepared.json',dict(prepare=PREP[-1],setters=SETTERS,view=view(e),contract=contract));check('02_disjoint_global_spatial_fields_complete_prepare')
 sq.double_activation_chance=0.0
 try:reject('reject_missing_pet',e._validate_bowl_double_activation_chance,sq);strict(sq.double_activation_chance,0.0)
 finally:sq.double_activation_chance=.2
 staff.double_attack_effect_chance=0.0
 try:reject('reject_missing_weapon',e._validate_attack_effect_chance,staff);strict(staff.double_attack_effect_chance,0.0)
 finally:staff.double_attack_effect_chance=.25
 reject('reject_duplicate_pet_setter',e.give_bowl_double_activation_chance,bowl,sq);reject('reject_duplicate_weapon_setter',e.give_double_attack_effect_chance,skill,staff);check('03_missing_duplicate_contributions_not_repaired')
 reset(e);prestack(e,'P','Mana',1);start={i:e.items[i].activations for i in('P:bowl','P:enchanted','P:staff')}
 def chain1():
  call('chain_bowl',e.trigger,bowl);call('chain_skill',e.trigger,skill);return call('chain_staff',e.weapon_attack,staff)
 r=segment(m,e,'bowl_skill_staff',vectors['rows']['bowl_skill_staff'],chain1)
 strict([x['type']for x in r['events']],vectors['types']['bowl_skill_staff']);strict([x['params']['amount']for x in r['events']if x['type']==105],[2,-3]);strict(r['result']['params']['damage'],14);strict(staff.bonus_damage,2);strict(e.characters['P'].mana,0)
 assert all(x['parent']is None for x in r['events']);paid=next(x for x in r['events']if x['type']==105 and x['params']['amount']<0);strict(paid['params']['used'],True)
 expected=1.0
 for n in(2,1,-3):expected+=n*((.7*1.0)/100.0)
 strict(e.characters['P'].stamina_regen,expected);strict([x['amount']for x in r['hooks']if x['method']=='give_stamina_regeneration'],[n*((.7*1.0)/100.0)for n in(2,1,-3)])
 for i,n in start.items():strict(e.items[i].activations,n+1)
 weapon_contract(r,'P:staff');strict(bowl.bowl_speed_bonus_given,25.0);strict(bowl.trigger_time,4.0);strict(skill.trigger_time,5.2)
 speed=[x for x in r['hooks']if x['method']=='add_speed'];strict([x['item']for x in speed],contract['bowl_caches']['P:bowl']);strict([x['amount']for x in speed],[.25,.25])
 for i in contract['bowl_caches']['P:bowl']:strict(e.items[i].speed_scale,PREP_SPEED[i]+.25)
 tip=[x for x in r['hooks']if x['method']=='tooltip'and x['item']in contract['bowl_caches']['P:bowl']];strict([(x['item'],x['stat'])for x in tip],[(i,s)for i in contract['bowl_caches']['P:bowl']for s in(3,9)]);assert all(x['effective_event']==r['events'][0]['id']for x in tip)
 flush=next(j for j,x in enumerate(r['hooks'])if x['method']=='flush_logging_queue'and x.get('phase')=='return');firstspeed=next(j for j,x in enumerate(r['hooks'])if x['method']=='add_speed');assert flush<firstspeed
 check('04_shared_Tape_Bowl_least_Staff_pay_and_history')
 reset(e);prestack(e,'O','Mana',2);n=sq.activations;tn=thorn.activations
 def chain2():
  call('chain_squirrel',e.trigger,sq);return call('chain_thorn',e.weapon_attack,thorn)
 r=segment(m,e,'squirrel_thorn',vectors['rows']['squirrel_thorn'],chain2);strict([x['type']for x in r['events']],vectors['types']['squirrel_thorn']);strict(sq.activations,n+2);strict(thorn.activations,tn+1);strict(sq.activations_this_frame,2);strict(sq.trigger_time,4.0)
 strict(sum(x['method']=='_pet_cooldown_effect'for x in r['hooks']),2);strict(sum(x['method']=='adjust_cooldown'for x in r['hooks']),1);weapon_contract(r,'P:thorn')
 spike=next(x for x in r['events']if x['type']==104);strict(spike['parent'],r['result']['id']);assert all(x['parent']is None for x in r['events']if x['type']!=104)
 strict(e.characters['P'].mana,2);strict(e.characters['O'].mana,0);strict(e.characters['P'].spikes,1)
 expected=1.0
 for _ in range(3):expected+=(.7*1.0)/100.0
 strict(e.characters['P'].stamina_regen,expected);expected=1.0
 for _ in range(2):expected-=((.7*1.0)/100.0)
 strict(e.characters['O'].stamina_regen,expected);check('05_Squirrel_pitch_extra_then_Thorn_explicit_parent')
 reset(e);prestack(e,'O','Block',10);n=spear.activations;r=segment(m,e,'spear_block',vectors['rows']['spear_block'],lambda:call('spear_block',e.weapon_attack,spear))
 strict([x['type']for x in r['events']],vectors['types']['spear_block']);strict([x['params']['amount']for x in r['events']if x['type']==100],[-4,-4]);strict(e.characters['O'].block,0);strict(e.characters['O'].hp,998.0);strict(e.characters['O'].stamina_regen,1.0);strict(e.characters['P'].stamina_regen,1.0)
 strict([x for x in r['hooks']if x['method']=='give_stamina_regeneration'],[]);assert all(x['parent']is None for x in r['events']);strict(spear.activations,n+1);weapon_contract(r,'P:spear');check('06_Block_excluded_from_registered_Wolper_feedback')
 reset(e);n=lucky.activations;r=segment(m,e,'lucky_early',vectors['rows']['lucky_early'],lambda:call('lucky_early',e.weapon_attack,lucky));strict([x['type']for x in r['events']],vectors['types']['lucky_early']);strict(r['events'][0]['parent'],None);assert r['events'][0]['id']<r['result']['id'];strict(e.characters['P'].lucky,1);strict(e.characters['P'].stamina_regen,1.0+(.7*1.0)/100.0);strict(lucky.activations,n+1);weapon_contract(r,'P:luckybow');strict(sum(x['method']=='_pet_cooldown_effect'for x in r['hooks']),0);check('07_Lucky_own_rolls_separate_from_Bowl_activations')
 before=view(e);snapshot=call('final_snapshot',e.snapshot);strict(view(e),before)
 for i,x in snapshot['items'].items():strict(x['double_activation_chance'],e.items[i].double_activation_chance);strict(x['double_attack_effect_chance'],e.items[i].double_attack_effect_chance);strict(x['bowl_speed_bonus_given'],e.items[i].bowl_speed_bonus_given)
 save('component-final-snapshot.json',snapshot);save('component-events-histories.json',dict(events=e.events,allocated=e.allocated_events,histories=e.histories.snapshot()));strict(COUNTS.get('unit:Tape._take',0),26)
 for name in('activate_from_checkpoint','step','run'):strict(COUNTS.get('unit:Engine.'+name,0),0)
 check('08_same_instance_serialization_and_unit_budget')


def natural(h,job):
 global MODE,STAGE,ACTIVE
 MODE='natural';STAGE='natural_initialize';b=call('natural_initialize',h.initialize_experimental_nonking,copy.deepcopy(job['layout']),job['seed']);e=b._engine;ACTIVE=e
 save('natural-initialize.json',dict(initialization=b.initialization,prepare=PREP[-1],events=e.events,audit=e.random.audit,source_rng=e.random.snapshot()));strict((PREP[-1]['draws_before'],PREP[-1]['draws_after'],PREP[-1]['activated']),(0,0,False));strict(type(e.random),h.CombatRandom)
 STAGE='natural_run';result=call('natural_run',b.run,max_seconds=job['max_seconds']);output=save('natural-source-output.json',result);save('natural-measured-hooks.json',[x for x in HOOKS if x['mode']=='natural'])
 STAGE='natural_postcheck';strict(e.finalized,True);strict(b.done,True);strict(e.king_mode,False);strict(sum(n['kind']=='timer'for n in e.runtime_inputs.data['nodes']),26);strict(result['coverage']['formal_support'],75);strict(result['coverage']['catalog_registered'],84);strict(result['initialization']['root_seed'],56501);strict(result['random_inputs'],e.random.audit);strict(result['source_rng'],e.random.snapshot())
 ah=[x for x in HOOKS if x['mode']=='natural'];pets=('P:sq','P:wolf','O:wolf');effects=sum(x['method']=='_pet_cooldown_effect'for x in ah);triggers=sum(x['method']=='trigger'and x['item']in pets for x in ah)
 measures=dict(extra_Pet_effect=effects-triggers,double_weapon_effect=sum(x['method']=='attack_effect_count'and x.get('count')==2 for x in ah),Bowl_activation=sum(x['type']==0 and x['origin']=='P:bowl'for x in e.events),Skill_activation=sum(x['type']==0 and x['origin']=='P:enchanted'for x in e.events),Bowl_food_speed_calls=sum(x['method']=='add_speed'and x.get('caller')=='_bowl_cooldown_effect'for x in ah),Squirrel_pitch=sum(x['label'].startswith('squirrel_activation_pitch:')for x in e.random.audit),Squirrel_actual_loss=sum(x['origin']=='P:sq'and 101<=x['type']<=107 and x['params'].get('amount',0)<0 for x in e.events),Wolper_positive_feedback=sum(x['method']=='give_stamina_regeneration'and x['amount']>0 for x in ah),Wolper_negative_feedback=sum(x['method']=='give_stamina_regeneration'and x['amount']<0 for x in ah),Staff_Mana_pay=sum(x['origin']=='P:staff'and x['type']==105 and x['params'].get('used')is True for x in e.events),Thorn_parented_Spikes=sum(x['origin']=='P:thorn'and x['type']==104 and x['parent']is not None for x in e.events),Spear_Block_loss=sum(x['origin']=='P:spear'and x['type']==100 and x['params'].get('amount',0)<0 for x in e.events))
 summary=dict(status='EXPERIMENTAL_SOURCE_NOT_NATIVE',output=output,seed=56501,items=29,timers=26,events=len(e.events),draws=len(e.random.audit),winner=e.winner,simulated_seconds=e.elapsed,measures=measures,HIT={k:'HIT'if v else'NOT_HIT'for k,v in measures.items()},source_rng=e.random.snapshot(),limits='No guaranteed natural HIT, no retuned seed/layout; synthetic prestates and Source RNG are not Native observations.')
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
  for name in('__init__','prepare_only','activate_from_checkpoint','run','step','attack_effect_count','attack','weapon_attack','pre_item_damage','late_item_damage','on_item_dealt_damage','on_character_attacked','on_character_damaged','_validate_attack_effect_chance','give_double_attack_effect_chance','_validate_bowl_double_activation_chance','give_bowl_double_activation_chance','trigger','adjust_cooldown','_pet_cooldown_effect','_bowl_cooldown_effect','activate','give_random_buffs','give_least_buffs','steal_random_buff','flush_logging_queue','add_speed','give_stamina_regeneration'):observe(m.CombatEngine,name,'Engine.'+name)
  observe(hs.CombatHistories,'tooltip','Histories.tooltip')
  observe(hs.CombatHistories,'snapshot','Histories.snapshot')
  observe(m.TapeRandom,'_take','Tape._take')
  fixture=gates(h,unit);components(h,m,hs,fixture,contract,vectors);natural(h,job)
  strict([x['label']for x in DIRECT],ledger['direct_order']);strict(len(REJECTS),10);strict(len(PASSES),9)
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
 def deadline(sig,frame):raise TimeoutError('565 whole-process35s wall budget')
 signal.signal(signal.SIGALRM,deadline);signal.alarm(35);sys.exit(main())
