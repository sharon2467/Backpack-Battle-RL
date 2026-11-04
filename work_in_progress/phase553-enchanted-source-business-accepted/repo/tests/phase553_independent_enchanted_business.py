"""Finite independent551 Source controls. Root exact release required before execution."""
import argparse,copy,dataclasses,functools,hashlib,importlib,json,math,os,random,re,resource,signal,stat,struct,sys,time,traceback,types,typing
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'data/phase551-source-enchanted-weapons'
PLAN=ROOT/'data/phase553-exact-business-source'
OUT=ROOT/'data/phase553-independent-business-first-001'
MODE='preflight';STAGE='preflight';ACTIVE=None
COUNTS={};SUCCEEDED={};DIRECT=[];PASSES=[];REJECTS=[];HOOKS=[];PREP=[];SETTERS=[]

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
  e=a[0]if label.startswith('Engine.')else None
  if label=='Engine.__init__':ACTIVE=e
  before=None;row=None
  if label=='Engine.prepare_only':before=len(e.random.audit)
  if label=='Engine.give_double_attack_effect_chance':
   row=dict(mode=MODE,stage=STAGE,source=getattr(a[1],'instance_id',None),target=getattr(a[2],'instance_id',None),source_prepared=a[1].cache_prepared,target_prepared=a[2].cache_prepared,before=a[2].double_attack_effect_chance,event_num=e.event_num,draws=len(e.random.audit))
  if label in('Engine.attack_effect_count','Engine.pre_item_damage','Engine.late_item_damage','Engine.on_item_dealt_damage','Engine.on_character_attacked','Engine.on_character_damaged','Engine.weapon_attack','Engine.attack','Engine.activate','Engine.give_least_buffs','Engine.give_stamina_regeneration'):
   item=getattr(a[1],'instance_id',a[1])if len(a)>1 else None
   row=dict(mode=MODE,stage=STAGE,method=name,item=item,event_num=e.event_num,draws=len(e.random.audit),events=len(e.events))
   if name=='give_stamina_regeneration':row['amount']=a[2]
   HOOKS.append(row)
  if label=='Tape._take':HOOKS.append(dict(mode=MODE,stage=STAGE,method='draw',kind=a[1],label=a[2],args=copy.deepcopy(a[3])))
  try:v=orig(*a,**kw)
  except BaseException:
   if row is not None:row['status']='RAISED'
   raise
  SUCCEEDED[key]=SUCCEEDED.get(key,0)+1
  if row is not None:row['status']='RETURNED'
  if label=='Engine.give_double_attack_effect_chance':
   row.update(after=a[2].double_attack_effect_chance,after_event_num=e.event_num,after_draws=len(e.random.audit));SETTERS.append(row)
  if label=='Engine.attack_effect_count':row['count']=v
  if label=='Engine.prepare_only':PREP.append(dict(mode=MODE,draws_before=before,draws_after=len(e.random.audit),activated=e.activated,order=list(e.preparation_order)))
  return v
 setattr(obj,name,wrapper)
def reset(e):
 assert not e.signal_queue
 e.ended=False;e.pending_terminal=False;e.util_time=20.0;e.logging_mode=1
 for c in e.characters.values():
  c.dead=False;c.hp=999.0;c.stamina=5.0;c.stamina_regen=1.0;c.invulnerable=False;c.buff_protect_stacks=0;c.debuff_reflect_stacks=0;c.debuff_resist_stacks=0
  c.accuracy.reset(-1.0);c.critical.reset(-1.0)
  for k,fields in c.buff_fields.items():
   name={100:'block',101:'lucky',102:'regeneration',103:'vampirism',104:'spikes',105:'mana',106:'empower',107:'heat',108:'poison',109:'blind',110:'cold'}[k]
   setattr(c,name,0);fields['permanentStacks']=0;fields['temporaryStacks']=[];fields['resistStacks']=0
   for n in('reflectChancePercent','resistChancePercent','cleanseProtectionChancePercent'):fields[n]=0.0
 for it in e.items.values():
  it.bonus_damage=0;it.bonus_max_only=0;it.varying_damage=0;it.crit_chance=0.0;it.chance_rng.reset();it.damage_range.acc=0.0;it.last_activation_time=-1.0;it.activations_this_frame=0;it.trigger_time=0.0
  for k in it.buff_powers:it.buff_powers[k]=1.0;it.buff_amplification_chances[k]=0.0
 def count(c):return dict(hp=c.hp,mana=c.mana,block=c.block,lucky=c.lucky,spikes=c.spikes,regen=c.stamina_regen)
 return {s:count(c)for s,c in e.characters.items()}
def prestack(e,side,name,n):
 setattr(e.characters[side],name.lower(),n);e.characters[side].buff_fields[{'Mana':105,'Block':100}[name]]['permanentStacks']=n
def view(e):
 return dict(event_num=e.event_num,events=len(e.events),ended=e.ended,logging_mode=e.logging_mode,queue=len(e.signal_queue),
  sides={s:dict(hp=c.hp,mana=c.mana,block=c.block,lucky=c.lucky,spikes=c.spikes,regen=c.stamina_regen)for s,c in e.characters.items()},
  items={i:dict(chance=x.double_attack_effect_chance,bonus=x.bonus_damage,activations=x.activations,activation_frame=x.activations_this_frame,trigger_time=x.trigger_time)for i,x in e.items.items()if not x.definition['bag']})
def segment(m,e,name,rows,fn):
 global STAGE
 STAGE=name;e.random=m.TapeRandom(rows);ev=len(e.events);hi=len(HOOKS);before=view(e);allocated=e.event_num
 result=fn();raw=dict(name=name,before=before,after=view(e),result=result,events=copy.deepcopy(e.events[ev:]),allocated=[copy.deepcopy(v)for k,v in e.allocated_events.items()if k>allocated],audit=copy.deepcopy(e.random.audit),hooks=copy.deepcopy(HOOKS[hi:]))
 save('segment-'+name+'.json',raw);e.random.assert_consumed();strict(raw['audit'],rows,'exact rows');return raw

def gates(h,unit):
 global MODE,STAGE
 MODE='gate';STAGE='gate';fixture=call('validate_component',h.validate_experimental_nonking_layout,copy.deepcopy(unit))
 old=copy.deepcopy(unit)
 for s in old['sides']:s['items']=[x for x in s['items']if x['item_index']!=385]
 call('validate_without385',h.validate_experimental_nonking_layout,old)
 bad=copy.deepcopy(unit);bad['sides'][0]['items'].append(dict(item_index=201,x=2,y=4,f=0,instance_id='P:outside'))
 reject('reject_whelp',h.validate_experimental_nonking_layout,bad)
 bad=copy.deepcopy(unit);bad['sides'][0]['items'].append(dict(item_index=385,x=2,y=4,f=0,instance_id='P:duplicate'))
 reject('reject_duplicate385',h.validate_experimental_nonking_layout,bad)
 reject('reject_old_initialize',h.initialize,unit,55201)
 reject('reject_old_batch',h.run_batch,[dict(layout=unit,seed=55201)])
 return fixture

def components(h,m,fixture,contract,vectors):
 global MODE,STAGE,ACTIVE
 MODE='unit';STAGE='construct'
 runtime=call('runtime_inputs',h.runtime_inputs,fixture,contract['order'])
 e=call('component_ctor',m.CombatEngine,fixture,m.TapeRandom([]),runtime);ACTIVE=e;e.util_time=0.0
 skill=e.items['P:enchanted'];staff=e.items['P:staff'];sword=e.items['P:sword']
 call('initial_chance_guard',e._validate_attack_effect_chance,staff)
 reject('reject_premature_setter',e.give_double_attack_effect_chance,skill,staff)
 STAGE='prepare';call('prepare_only',e.prepare_only)
 strict(PREP[-1]['draws_before'],0);strict(PREP[-1]['draws_after'],0);strict(PREP[-1]['activated'],False)
 strict(len(SETTERS),8);strict([x['target_prepared']for x in SETTERS[:4]],contract['P_setter_target_cache_prepared']);strict([x['target_prepared']for x in SETTERS[4:]],contract['O_setter_target_cache_prepared'])
 for row in SETTERS:strict((row['before'],row['after']),(0.0,.25));strict(row['draws'],row['after_draws']);strict(row['event_num'],row['after_event_num'])
 caches={s+':enchanted':[x.instance_id for x in e.affected_items(e.items[s+':enchanted'])]for s in('P','O')}
 strict(caches,contract['caches']);strict(tuple(skill.definition['shape']),((0,0),));strict([list(x)for x in skill.definition['stars']],contract['skill_stars'])
 for s in('P','O'):strict(e.items[s+':spear'].spear_block_removal,contract['spear_block_removal'])
 for it in e.items.values():strict(it.double_attack_effect_chance,.25 if it.item_index in(14,32,233,234)else 0.0)
 save('component-prepared.json',dict(caches=caches,prepare=PREP[-1],setters=SETTERS,view=view(e)));check('01_geometry_cache_closed_admission',REJECTS.copy())
 for label,value in [('reject_missing',0.0),('reject_duplicate_value',.5),('reject_wrong_type',0)]:
  staff.double_attack_effect_chance=value
  try:reject(label,e._validate_attack_effect_chance,staff);strict(staff.double_attack_effect_chance,value)
  finally:staff.double_attack_effect_chance=.25
 reject('reject_unowned_target',e._validate_attack_effect_chance,copy.copy(staff))
 reject('reject_duplicate_setter',e.give_double_attack_effect_chance,skill,staff)
 reject('reject_non_skill_source',e.give_double_attack_effect_chance,e.items['P:wolf'],staff)
 reject('reject_foreign_side',e.give_double_attack_effect_chance,skill,e.items['O:staff'])
 strict(staff.double_attack_effect_chance,.25);check('02_prepare_before_after_and_reject_no_repair')
 before=view(e);snapshot=call('prepared_snapshot',e.snapshot);strict(view(e),before)
 for side in snapshot['native_rule_state']['characters']:
  for row in side['items']:
   identity=row['instance'];strict(row['fields']['doubleAttackEffectChance'],e.items[identity].double_attack_effect_chance);strict(snapshot['items'][identity]['double_attack_effect_chance'],e.items[identity].double_attack_effect_chance)
 save('prepared-serialized-state.json',snapshot);check('08_serialization_and_body_conservation')
 for name,it,expected in [('count_zero',sword,2),('count_above_zero',sword,1),('count_quarter',staff,2),('count_above_quarter',staff,1)]:
  r=segment(m,e,name,vectors['rows'][name],lambda name=name,it=it:call(name,e.attack_effect_count,it));strict(r['result'],expected);strict(r['events'],[])
 check('03_effect_flip_zero_quarter_nextafter')
 specs=[('staff_hit','staff',6,0,False,True,22,4,[105,105,1,0]),('staff_miss_partial','staff',3,0,False,False,0,2,[105,3,0]),('staff_hit_empty','staff',0,0,False,True,6,0,[1,0]),
 ('spear_hit','spear',0,10,False,True,3,0,[100,100,1,0]),('spear_invu','spear',0,3,True,True,0,0,[100,1,0]),('spear_miss','spear',0,10,False,False,0,0,[3,0]),
 ('thorn_hit','thorn',0,0,False,True,2,0,[1,104,0]),('lucky_hit','luckybow',0,0,False,True,3,0,[101,1,0])]
 attack_raw={}
 for name,item_name,mana,block,invu,hit,damage,bonus,types_expected in specs:
  reset(e);prestack(e,'P','Mana',mana);prestack(e,'O','Block',block);e.characters['O'].invulnerable=invu
  item=e.items['P:'+item_name];n=item.activations
  r=segment(m,e,name,vectors['rows'][name],lambda name=name,item=item:call(name,e.weapon_attack,item));attack_raw[name]=r
  strict([x['type']for x in r['events']],types_expected);strict(item.activations,n+1);strict(item.bonus_damage,bonus)
  if hit:strict(r['result']['params']['damage'],damage)
  methods=[x['method']for x in r['hooks']]
  for method,count in [('attack_effect_count',1),('pre_item_damage',2),('late_item_damage',2 if hit else 0),('on_item_dealt_damage',2),('on_character_attacked',1),('on_character_damaged',1),('attack',1),('activate',1)]:strict(methods.count(method),count,name+':'+method)
  flips=[x for x in r['hooks']if x['method']=='attack_effect_count'];strict(flips[0]['count'],2)
  if 'staff' in name:
   paid=[x for x in r['events']if x['type']==105];strict([x['params']['amount']for x in paid],[-3]*(2 if name=='staff_hit'else 1 if name=='staff_miss_partial'else 0));assert all(x['params']['used']is True and x['parent']is None for x in paid)
  if name=='spear_hit':strict([x['params']['amount']for x in r['events']if x['type']==100],[-8,-2]);strict(e.characters['O'].block,0)
  if name=='spear_invu':strict(e.characters['O'].hp,999.0);strict(e.characters['O'].block,0)
  if name=='spear_miss':strict(e.characters['O'].block,10)
  if name=='thorn_hit':strict(r['events'][1]['parent'],r['result']['id']);strict(e.characters['P'].spikes,1)
  if name=='lucky_hit':strict(r['events'][0]['parent'],None);strict(e.characters['P'].lucky,1);assert r['events'][0]['id']<r['result']['id']
 check('04_staff_early_hit_miss_independent_mana')
 check('05_spear_late_hit_miss_zero_damage_block_exhaustion')
 check('06_shortbow_independent_chances_and_parents')
 for name in('skill_normal','skill_ended','skill_limiter'):
  reset(e);n=skill.activations
  if name=='skill_ended':e.ended=True
  if name=='skill_limiter':skill.last_activation_time=20.0;skill.activations_this_frame=3
  r=segment(m,e,name,vectors['rows'][name],lambda name=name:call(name,e.trigger,skill))
  strict(e.characters['P'].lucky,1);strict(skill.trigger_time,5.2);strict(e.logging_mode,1);strict(len(e.signal_queue),0)
  strict([x['type']for x in r['events']],[]if name=='skill_ended'else[101]if name=='skill_limiter'else[101,0])
  strict(skill.activations,n+int(name=='skill_normal'))
  if name=='skill_ended':strict(len(r['allocated']),1);strict(e.characters['P'].stamina_regen,1.0)
  else:strict(e.characters['P'].stamina_regen,1.0+(0.7*1.0)/100.0)
  if name=='skill_limiter':strict(skill.activations_this_frame,4)
 check('07_skill_cooldown_least_then_activation_ended_limiter')
 save('component-history.json',dict(events=e.events,allocated=e.allocated_events,histories=e.histories.snapshot(),view=view(e)))
 strict(sum(len(v)for v in vectors['rows'].values()),35);strict(sum(x.get('method')=='draw' and x.get('mode')=='unit'for x in HOOKS),35)
 for method in('activate_from_checkpoint','step','run'):strict(COUNTS.get('unit:Engine.'+method,0),0)

def natural(h,job):
 global MODE,STAGE,ACTIVE
 MODE='natural';STAGE='natural_initialize';b=call('natural_initialize',h.initialize_experimental_nonking,copy.deepcopy(job['layout']),job['seed']);e=b._engine;ACTIVE=e
 save('natural-initialize.json',dict(initialization=b.initialization,prepare=PREP[-1],audit=e.random.audit,events=e.events))
 strict(PREP[-1]['draws_before'],0);strict(PREP[-1]['draws_after'],0);strict(type(e.random),h.CombatRandom)
 STAGE='natural_run';result=call('natural_run',b.run,max_seconds=job['max_seconds']);raw=save('natural-source-output.json',result)
 save('natural-hooks.json',[x for x in HOOKS if x['mode']=='natural'])
 STAGE='natural_postcheck';strict(e.finalized,True);strict(b.done,True);strict(e.king_mode,False);strict(sum(n['kind']=='timer'for n in e.runtime_inputs.data['nodes']),26)
 strict(result['coverage']['formal_support'],75);strict(result['coverage']['catalog_registered'],83);strict(result['coverage']['experimental_items'],[231,385]);strict(result['coverage']['experimental_kinds'],[64,164,197,199,201,231,385])
 strict(result['initialization']['root_seed'],55201);strict(result['random_inputs'],e.random.audit);strict(result['source_rng'],e.random.snapshot())
 ev=e.events;hooks=[x for x in HOOKS if x['mode']=='natural'];measures={}
 for name in('staff','spear','thorn','luckybow'):
  identity='P:'+name;measures[name+'_double']=sum(x['method']=='attack_effect_count'and x['item']==identity and x.get('count')==2 for x in hooks)
  measures[name+'_attack']=sum(x['origin']==identity and x['type']in(1,2,3)for x in ev)
 measures.update(skill_activation=sum(x['origin']=='P:enchanted'and x['type']==0 for x in ev),skill_gain=sum(x['origin']=='P:enchanted'and 101<=x['type']<=107 and x['params'].get('amount',0)>0 for x in ev),wolf_regen=sum(x['method']=='give_stamina_regeneration'and x.get('amount',0)!=0 for x in hooks),spear_positive_loss=sum(x['origin']=='P:spear'and x['type']==100 and x['params'].get('amount',0)<0 for x in ev))
 summary=dict(status='SOURCE_ONLY_NOT_NATIVE',raw=raw,seed=55201,items=24,events=len(ev),draws=len(e.random.audit),sim_seconds=e.elapsed,winner=e.winner,measures=measures,HIT={k:'HIT'if v else'NOT_HIT'for k,v in measures.items()},natural_spear_positive_loss_required=False)
 save('natural-summary.json',summary);check('09_single_presealed_natural',summary)
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
  sys.addaudithook(audit);STAGE='import';h=importlib.import_module('headless');m=importlib.import_module('native_replay_v8.engine')
  imports=[]
  for name,mod in list(sys.modules.items()):
   if name in('headless','original_rng','godot_pcg_integer')or name.startswith(('native_replay_v7','native_replay_v8')):
    p=Path(mod.__file__).resolve();assert str(p)in allowed;imports.append(dict(module=name,path=str(p),sha256=sha(p.read_bytes())))
  save('imports.json',imports)
  for obj,name,label in((h,'derive_stream_seeds','derive_stream_seeds'),(h.CombatRandom,'__init__','CombatRandom.__init__'),(h.GodotPCGInteger,'__init__','PCG.__init__')):observe(obj,name,label)
  for name in('__init__','prepare_only','activate_from_checkpoint','run','step','_validate_attack_effect_chance','give_double_attack_effect_chance','attack_effect_count','pre_item_damage','late_item_damage','on_item_dealt_damage','on_character_attacked','on_character_damaged','weapon_attack','attack','activate','give_least_buffs','give_stamina_regeneration'):observe(m.CombatEngine,name,'Engine.'+name)
  observe(m.TapeRandom,'_take','Tape._take')
  fixture=gates(h,unit);components(h,m,fixture,contract,vectors);natural(h,job)
  strict([x['label']for x in DIRECT],ledger['direct_order']);strict(len(REJECTS),12);strict(len(PASSES),9)
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
 def deadline(sig,frame):raise TimeoutError('553 whole-process35s wall budget')
 signal.signal(signal.SIGALRM,deadline);signal.alarm(35);sys.exit(main())
