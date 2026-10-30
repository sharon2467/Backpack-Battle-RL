"""Finite three-Whelp Source controls, no native or legacy-case replay."""
import copy,functools,hashlib,importlib,json,signal,struct,sys,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'data/phase497-source-three-whelps'
PLAN=ROOT/'data/phase498-independent-business-plan'
HARNESS=ROOT/'data/phase498-independent-harness-source'
OUT=ROOT/'data/phase498-independent-business-first-001'
A='P:amethyst';E='P:emerald';S='P:sapphire';RUBY='O:ruby';SQ='P:squirrel'
COUNTS={};PASSES=[];REJECTS=[];PREPARES=[];TRAIL=[];REFLECTIONS=[];NATURAL_HOOKS=[];START_GAINS=[]
ACTIVE=None;MODE=None;STAGE='preflight';R=None
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

def verify(p,want=None):
 if want:strict(sha(p.read_bytes()),want)
 rows=json.loads(p.read_bytes())['files']
 for row in rows:strict(pin(ROOT/row['path']),row,'pin')
 return rows

def check(name,details=None):
 row=dict(name=name,status='PASS',details=details,calls=COUNTS.copy());PASSES.append(row)
 with(OUT/'controls.jsonl').open('a')as f:f.write(json.dumps(row,allow_nan=False)+'\n')

def bits(v):return struct.pack('>d',float(v)).hex()

def rf(label,value):return dict(kind='randf',label=label,args=[],value_bits=bits(value))

def rr(label,lo,hi,value):return dict(kind='randf_range',label=label,args=[bits(lo),bits(hi)],value_bits=bits(value))

def ri(label,lo,hi,value):return dict(kind='randi_range',label=label,args=[lo,hi],value=value)

class UnitTape:
 alignment='SOURCE_SYNTHETIC_TEST_OWNED_EXACT_ROWS'
 def __init__(self,rows,e):self.records=copy.deepcopy(rows);self.audit=[];self.position=0;self.e=e
 def take(self,kind,label,args):
  assert self.position<len(self.records),('tape exhausted',label)
  row=self.records[self.position];value='value_bits'if kind!='randi_range'else'value'
  strict({k:v for k,v in row.items()if k!=value},dict(kind=kind,label=label,args=args),'unitrow')
  self.position+=1;self.audit.append(copy.deepcopy(row));TRAIL.append(dict(method='draw',label=label,position=self.position,events=len(self.e.events)))
  return struct.unpack('>d',bytes.fromhex(row[value]))[0]if value=='value_bits'else row[value]
 def randf(self,label):return self.take('randf',label,[])
 def randf_range(self,label,lo,hi):return self.take('randf_range',label,[bits(lo),bits(hi)])
 def randi_range(self,label,lo,hi):return self.take('randi_range',label,[lo,hi])
 def assert_consumed(self):strict(self.position,len(self.records))

def reject(name,fn):
 before=COUNTS.copy()
 try:fn()
 except ValueError as exc:strict(COUNTS,before,'reject_preRNG');REJECTS.append(dict(name=name,error=str(exc)))
 else:raise AssertionError('accepted '+name)

def counted(obj,name,label):
 orig=getattr(obj,name)
 @functools.wraps(orig)
 def call(*a,**kw):
  global ACTIVE
  COUNTS[label]=COUNTS.get(label,0)+1
  if label=='Engine.prepare_only':
   e=a[0];ACTIVE=e;strict(e.random.audit,[]);v=orig(*a,**kw);strict(e.random.audit,[])
   PREPARES.append(dict(mode=MODE,audit=copy.deepcopy(e.random.audit),source_rng=e.random.snapshot(),order=list(e.preparation_order),
    caches={SQ:[x.instance_id for x in e.affected_items(e.items[SQ])]}if SQ in e.items else{},
    initial_buffs={s:dict(heat=c.heat,lucky=c.lucky,mana=c.mana,reflect=c.debuff_reflect_stacks)for s,c in e.characters.items()}))
   if MODE=='unit':
    rows=[rr('cooldown:'+i,.975 if e.items[i].side=='O' else .95,1.05,1.0)for i in e.preparation_order if e.items[i].has_cooldown]
    rows += [ri(f'random_stack:{A}:O:give:{i}',0,2,v)for i,v in enumerate((0,2,0,1))]
    rows += [rr(f'reflect:O:{A}:'+k,0.,100.,50.)for k in('Poison','Poison','Cold','Blind')]
    e.random=UnitTape(rows,e)
   return v
  if label=='Engine.change_debuff_reflection':
   e,side,amount=a;before=e.characters[side].debuff_reflect_stacks;heat=e.characters[side].heat
   v=orig(*a,**kw);REFLECTIONS.append(dict(mode=MODE,side=side,amount=amount,before=before,after=e.characters[side].debuff_reflect_stacks,heat=heat,draws=len(e.random.audit),events=len(e.events),labels=[x['label']for x in e.random.audit]));return v
  if label=='Engine.give_stack'and STAGE in('04_unit_initialize','16_natural_initialize'):
   e,item,side,kind,amount=a[:5];START_GAINS.append(dict(mode=MODE,origin=item.instance_id,side=side,kind=kind,amount=amount,
    draws=len(e.random.audit),events=len(e.events),Oreflect=e.characters['O'].debuff_reflect_stacks,
    all_cooldowns_active=all(x.cooldown_active for x in e.items.values()if x.has_cooldown)))
  if label=='Engine.pre_item_damage'and MODE=='natural'and a[1].item_index in(197,199):
   e,item,hit=a;start=len(e.events);mana=e.characters[item.side].mana;v=orig(*a,**kw)
   NATURAL_HOOKS.append(dict(item=item.instance_id,item_index=item.item_index,hit=hit,mana_before=mana,mana_after=e.characters[item.side].mana,events=[x['id']for x in e.events[start:]]));return v
  if MODE=='unit'and label in('Engine.pre_item_damage','Engine.give_stack','Engine.try_use_mana','Engine.give_random_buffs','Engine.emit'):
   e=a[0];TRAIL.append(dict(method=name,position=getattr(e.random,'position',None),events=len(e.events),origin=getattr(a[1],'instance_id',a[1])if len(a)>1 else None))
  return orig(*a,**kw)
 setattr(obj,name,call)

def ingress(h,m,layout):
 for identity,flag in((64,128),(197,258),(199,254)):
  d=m.CATALOG[identity];strict(d['shape'],((0,0),(1,0),(0,1),(1,1)));strict(d.get('stars',()),());strict((d['socket_count'],d['default_gem']),(1,None))
  strict([d[k]for k in('ranged','pet','effect')],[True]*3);strict([d[k]for k in('cooldown','stamina','accuracy','min_damage','max_damage')],[2.1,0.0,90.0,5,10]);strict(m.GAINED_STACK_FLAGS[identity],flag);assert identity in m.EMPOWERABLE_WEAPON_IDS
 strict(m.CATALOG[199]['random_buff_types'],(101,102,103,104,106,107));strict((len(m.CATALOG),len(h.ITEMS)),(81,75));check('01_three_exact_descriptors')
 stripped=copy.deepcopy(layout)
 for side in stripped['sides']:side['items']=[x for x in side['items']if x['item_index']not in(64,164,197,199,201)]
 variants=[]
 for identity in(64,197,199):
  x=copy.deepcopy(layout)
  for side in x['sides']:side['items']=[v for v in side['items']if v['item_index']not in{64,164,197,199,201}-{identity}]
  h.validate_experimental_nonking_layout(x);variants.append(x)
 h.validate_experimental_nonking_layout(layout)
 reject('noextras',lambda:h.initialize_experimental_nonking(stripped,49801))
 for identity in(262,129,999):
  x=copy.deepcopy(layout);next(v for v in x['sides'][0]['items']if v['item_index']==199)['item_index']=identity
  reject('newbad'+str(identity),lambda x=x:h.initialize_experimental_nonking(x,49801))
 check('02_new_domain_and_atomic_refusals',REJECTS.copy())
 for identity,x in zip((64,197,199),variants):reject('old'+str(identity),lambda x=x:h.initialize(x,49801))
 reject('oldSquirrel',lambda:h.initialize_squirrel(layout,49801))
 reject('oldbatch',lambda:h.run_batch([dict(layout=stripped,seed=49801),dict(layout=variants[-1],seed=49801)],keep_results=True))
 check('03_old_closed_routes',REJECTS[4:]);strict(COUNTS,{})

def reset(e,t,mana=0,block=0,protect=0,invu=False):
 e.util_time=float(t);e.ended=False;e.winner=None;e.pending_terminal=False
 for side in('P','O'):
  c=e.characters[side];c.dead=False;c.hp=c.max_hp;c.invulnerable=False;c.buff_protect_stacks=0;c.debuff_reflect_stacks=0;c.debuff_resist_stacks=0
  for category in range(100,111):
   name=R.STACK_NAMES_BY_TYPE[category];value=mana if side=='P'and category==105 else block if side=='P'and category==100 else 0
   setattr(c,name.lower(),value);f,_=e._buff_record(side,name);f['permanentStacks']=value;f['temporaryStacks'].clear();e.histories.stack(side,category)
  c.accuracy.reset();c.accuracy.last_result=True
 e.characters['P'].buff_protect_stacks=protect;e.characters['O'].invulnerable=invu
 for name in(E,S):e.items[name].damage_range.acc=0.0;e.items[name].crit_chance=0.0

def segment(e,name,rows,fn):
 global STAGE
 STAGE=name;start=len(e.events);before=COUNTS.copy();TRAIL.clear();e.random=UnitTape(rows,e)
 save(name+'.prestate.json',dict(synthetic=True,characters=e.snapshot()['characters'],util_time=e.util_time,counts=before))
 answer=fn();events=copy.deepcopy(e.events[start:]);p=save(name+'.actual.json',dict(synthetic=True,events=events,answer=answer,audit=e.random.audit,trail=TRAIL,snapshot=e.snapshot(),history=e.histories.snapshot(),counts=COUNTS.copy()))
 e.random.assert_consumed();return answer,events,before,p

def attack_prefix(identity,hit=True,double=False):return [rf('double_attack_effect:'+identity,0.0 if double else .5),rf('accuracy:O:'+identity,.5 if hit else 1.0)]
def damage(identity):return ri('damage:'+identity,5,10,5)
def selector(value):return ri(f'random_stack:{S}:P:give:0',0,5,value)
def paid_events(events):return [x for x in events if x['origin']==S and x['type']==105 and x['params'].get('used')is True]
def prove_paid(events,expected_types,cap=False):
 paid=paid_events(events);strict(len(paid),len(expected_types));rewards=[x for x in events if x['origin']==S and 100<=x['type']<=107 and x['type']!=105]
 for p,kind in zip(paid,expected_types):
  strict((p['params']['amount'],p['target'],p['parent']),(-1,0,None))
  own=[x for x in rewards if x['parent']==p['id']];strict([x['type']for x in own],[kind]if cap else[100,kind]);strict([x['params']['amount']for x in own],[1]if cap else[10,1]);assert all(x['id']>p['id']for x in own)
 assert all(x['parent']in{p['id']for p in paid}for x in rewards)
 return paid

def components(h,m,layout):
 global MODE,ACTIVE,STAGE
 MODE='unit';STAGE='04_unit_initialize';TRAIL.clear();b=h.initialize_experimental_nonking(copy.deepcopy(layout),49801);e=b._engine;ACTIVE=e;e.random.assert_consumed()
 save('unit-initialize.json',dict(initialization=b.initialization,prepared=PREPARES[-1],events=e.events,audit=e.random.audit,reflections=REFLECTIONS,start_gains=START_GAINS,trail=TRAIL,snapshot=e.snapshot(),history=e.histories.snapshot()))
 strict(PREPARES[-1]['initial_buffs'],{s:dict(heat=0,lucky=0,mana=0,reflect=0)for s in('P','O')})
 provision=[x for x in REFLECTIONS if x['amount']>0];strict(len(provision),1);q=provision[0];strict((q['side'],q['amount'],q['before'],q['after'],q['heat'],q['events']),('O',3,0,3,0,0))
 assert 'cooldown:'+RUBY in q['labels'];assert all(x.startswith('cooldown:')for x in q['labels']);assert all(x['all_cooldowns_active']for x in START_GAINS);strict(START_GAINS[0]['Oreflect'],3)
 check('04_Ruby_pre_stage_before_all_starts',dict(provision=q,start_gains=START_GAINS))
 for identity,kind,amount in((RUBY,107,5),(E,101,3),(S,105,6)):
  ev=[x for x in e.events if x['origin']==identity];strict([x['type']for x in ev],[kind,0]);strict(ev[0]['params']['amount'],amount);strict([x['parent']for x in ev],[None,None])
 strict((e.characters['P'].poison,e.characters['P'].cold,e.characters['O'].blind,e.characters['O'].debuff_reflect_stacks),(2,1,1,0))
 strict((e.characters['P'].lucky,e.characters['P'].mana,e.characters['O'].heat),(3,6,5));check('05_real_start_effects_and_Ruby_reflection',e.events)
 reset(e,6);_,ev,_,_=segment(e,'06_Emerald_miss',attack_prefix(E,False),lambda:e.weapon_attack(e.items[E]));strict([x['type']for x in ev],[3,0]);check('06_Emerald_miss_no_poison')
 reset(e,7,invu=True);rows=attack_prefix(E)+[rr(f'reflect:O:{E}:Poison',0.,100.,50.)for _ in range(3)]+[damage(E)]
 _,ev,_,_=segment(e,'07_Emerald_zero_hit',rows,lambda:e.weapon_attack(e.items[E]));strict([x['type']for x in ev],[108,1,0]);strict(ev[0]['params']['amount'],3);strict(ev[0]['parent'],None);strict(ev[1]['params']['damage'],0);strict(e.characters['O'].poison,3);check('07_Emerald_zero_damage_hit_keeps_poison',ev)
 reset(e,8);rows=attack_prefix(E,double=True)+[rr(f'reflect:O:{E}:Poison',0.,100.,50.)for _ in range(6)]+[damage(E)]
 _,ev,before,_=segment(e,'08_Emerald_double',rows,lambda:e.weapon_attack(e.items[E]));strict([x['type']for x in ev],[108,108,1,0]);strict([x['params']['amount']for x in ev[:2]],[3,3]);strict([x['parent']for x in ev[:2]],[None,None]);strict(COUNTS['Engine.pre_item_damage']-before['Engine.pre_item_damage'],2);strict(COUNTS['Engine.on_character_attacked']-before['Engine.on_character_attacked'],1);check('08_Emerald_double_own_only',ev)
 reset(e,9,mana=1);_,miss,before,_=segment(e,'09a_Sapphire_miss',attack_prefix(S,False),lambda:e.weapon_attack(e.items[S]));strict(e.characters['P'].mana,1);strict(COUNTS.get('Engine.try_use_mana',0),before.get('Engine.try_use_mana',0));strict([x['type']for x in miss],[3,0])
 reset(e,9.1);_,fail,_,_=segment(e,'09b_Sapphire_no_Mana',attack_prefix(S)+[damage(S)],lambda:e.weapon_attack(e.items[S]));strict([x['type']for x in fail],[1,0]);strict(e.characters['P'].block,0);check('09_Sapphire_miss_and_failed_pay',dict(miss=miss,failed=fail))
 reset(e,10,mana=1,protect=1);_,ev,_,_=segment(e,'10_Sapphire_paid_protected',attack_prefix(S)+[selector(0),damage(S)],lambda:e.weapon_attack(e.items[S]));prove_paid(ev,[101]);strict([x['type']for x in ev],[105,100,101,1,0]);strict((e.characters['P'].mana,e.characters['P'].block,e.characters['P'].lucky,e.characters['P'].buff_protect_stacks),(0,10,1,1));check('10_actual_paid_parent_and_used_bypass',ev)
 mappings=[]
 for raw,kind in enumerate((101,102,103,104,106,107)):
  if raw==0:continue
  reset(e,11+raw/10,mana=1);_,ev,_,_=segment(e,'11_mapping_'+str(raw),[selector(raw)],lambda:e.pre_item_damage(e.items[S],True));prove_paid(ev,[kind]);strict([x['type']for x in ev],[105,100,kind]);mappings.append(dict(raw=raw,kind=kind,events=ev))
 check('11_remaining_six_category_mapping_no_Mana',mappings)
 reset(e,12,mana=1,block=100000);_,ev,_,_=segment(e,'12_Block_cap',attack_prefix(S)+[selector(5),damage(S)],lambda:e.weapon_attack(e.items[S]));prove_paid(ev,[107],cap=True);strict([x['type']for x in ev],[105,107,1,0]);strict((e.characters['P'].block,e.characters['P'].heat),(100000,1));check('12_capped_Block_does_not_cancel_reward',ev)
 reset(e,13,mana=1);_,ev,before,_=segment(e,'13_double_one_Mana',attack_prefix(S,double=True)+[selector(0),damage(S)],lambda:e.weapon_attack(e.items[S]));prove_paid(ev,[101]);strict([x['type']for x in ev],[105,100,101,1,0]);strict(COUNTS['Engine.try_use_mana']-before['Engine.try_use_mana'],2);strict(COUNTS['Engine.on_character_attacked']-before['Engine.on_character_attacked'],1);strict(e.characters['P'].mana,0);check('13_double_one_Mana_second_fails',ev)
 reset(e,14,mana=2);_,ev,before,_=segment(e,'14_double_two_Mana',attack_prefix(S,double=True)+[selector(1),selector(5),damage(S)],lambda:e.weapon_attack(e.items[S]));paid=prove_paid(ev,[102,107]);strict([x['type']for x in ev],[105,100,102,105,100,107,1,0]);assert paid[0]['id']!=paid[1]['id'];strict(e.characters['P'].block,20);strict(COUNTS['Engine.on_character_attacked']-before['Engine.on_character_attacked'],1);check('14_double_two_paid_event_chains',ev)
 strict(b.initialization['experimental_items'],[64,197,199,201]);strict(b.initialization['domain']['experimental_kinds'],[64,164,197,199,201]);strict(b.initialization['catalog_registered'],81)
 copied=b.initialization;copied['source_extension']='false';strict(b.initialization['source_extension'],h.EXPERIMENTAL_NONKING_EXTENSION)
 assert all(not x['label'].startswith('squirrel_activation_pitch:')for x in e.random.audit)
 check('15_persisted_identity_defensive_getter_no_invented_pitch')

def natural(h,job):
 global MODE,STAGE,ACTIVE
 MODE='natural';STAGE='16_natural_initialize';b=h.initialize_experimental_nonking(copy.deepcopy(job['layout']),job['seed']);e=b._engine;ACTIVE=e
 save('natural-initialize.json',dict(initialization=b.initialization,prepare=PREPARES[-1],events=e.events,audit=e.random.audit,start_gains=[x for x in START_GAINS if x['mode']=='natural'],reflection=[x for x in REFLECTIONS if x['mode']=='natural'],snapshot=e.snapshot()))
 strict(PREPARES[-1]['caches'][SQ],['P:berry0','P:goobert','P:berry1',A]);strict(e.items[SQ].speed_scale,.6);strict(type(e.random),h.CombatRandom)
 STAGE='16_natural_run';result=b.run(max_seconds=120.0);raw=save('natural-source-output.json',result);trace=save('natural-measured-hooks.json',NATURAL_HOOKS)
 strict(e.finalized,True);strict(b.done,True);strict(e.king_mode,False);strict(sum(x['kind']=='timer'for x in e.runtime_inputs.data['nodes']),26)
 strict(result['coverage']['formal_support'],75);strict(result['coverage']['catalog_registered'],81);strict(result['coverage']['experimental_items'],[64,164,197,199,201]);strict(result['coverage']['experimental_kinds'],[64,164,197,199,201]);strict(result['coverage']['source_extension'],h.EXPERIMENTAL_NONKING_EXTENSION)
 strict(result['random_inputs'],e.random.audit);strict(result['source_rng'],e.random.snapshot());strict(result['initialization']['root_seed'],49801)
 ev=e.events;payments=[x for x in ev if x['origin']==S and x['type']==105 and x['params'].get('used')is True];paidids={x['id']for x in payments}
 selected=[x for x in ev if x['origin']==S and x['parent']in paidids and 101<=x['type']<=107];assert all(x['type']!=105 for x in selected)
 failed=[x for x in NATURAL_HOOKS if x['item_index']==199 and x['hit']and x['mana_before']==0]
 summary=dict(status='EXPERIMENTAL_SOURCE_NOT_NATIVE',output=raw,hook_trace=trace,seed=49801,items=29,events=len(ev),draws=len(e.random.audit),timers=26,winner=e.winner,simulated_seconds=result['final']['timestamp'],
  Sapphire_payments=len(payments),Sapphire_failed_zeroMana_hooks=len(failed),Sapphire_rewards=len(selected),
  Emerald_poison_events=sum(x['origin']==E and x['type']==108 for x in ev),Ruby_heat_events=sum(x['origin']==RUBY and x['type']==107 for x in ev),
  Amethyst_losses=sum(x['origin']==A and 101<=x['type']<=107 and x['params'].get('amount',0)<0 for x in ev),Squirrel_losses=sum(x['origin']==SQ and 101<=x['type']<=107 and x['params'].get('amount',0)<0 for x in ev),
  reflected_Amethyst_events=sum(x['origin']==A and x['params'].get('reflected')is True for x in ev),
  HIT=dict(Sapphire_paid='HIT'if payments else'NOT_HIT',Sapphire_zeroMana='HIT'if failed else'NOT_HIT',Ruby_pre_reflection='HIT'if any(x['mode']=='natural'and x['amount']==3 for x in REFLECTIONS)else'NOT_HIT',
   protection_cap_double='SYNTHETIC_ONLY_UNLESS_SEALED_TRACE_SHOWS_HIT'),no_seed_or_layout_tuning=True,source_rng=e.random.snapshot())
 save('natural-summary.json',summary);check('16_one_fixed_mixed_natural',summary)

def main():
 global STAGE,R
 OUT.mkdir(exist_ok=False);t=time.monotonic();status='FAILED';refs=[]
 try:
  verify(HARNESS/'owned-files.json');verify(PLAN/'owned-files.json','9d5cfdfa1204e1bf64eafb76d4222087dc32ffe87f95373036bb7cd8df96b923');refs=verify(SOURCE/'owned-files.json','9d60cd3d5165b8810eb145a02ae9cb78614112936ca526bc613a2135f482302f')
  job=json.loads((PLAN/'natural-job.json').read_bytes());unit=json.loads((PLAN/'synthetic-layout.json').read_bytes());sys.dont_write_bytecode=True;sys.pycache_prefix=str(OUT/'unused-bytecode-cache');sys.path.insert(0,str(SOURCE/'staged'));STAGE='import_frozen'
  h=importlib.import_module('headless');R=importlib.import_module('native_replay_v8.engine');allowed={str((ROOT/x['path']).resolve())for x in refs if '/staged/'in x['path']};imports=[]
  for name,module in list(sys.modules.items()):
   if name in('headless','original_rng','godot_pcg_integer')or name.startswith(('native_replay_v7','native_replay_v8')):
    path=str(Path(module.__file__).resolve());assert path in allowed,(name,path);imports.append(dict(name=name,path=path))
  save('imports.json',imports)
  for obj,name,label in((h,'derive_stream_seeds','derive_stream_seeds'),(h.CombatRandom,'__init__','CombatRandom.__init__'),(h.GodotPCGInteger,'__init__','PCG.__init__')):counted(obj,name,label)
  for name in('__init__','prepare_only','activate_from_checkpoint','run','change_debuff_reflection','give_stack','try_use_mana','give_random_buffs','pre_item_damage','weapon_attack','attack','on_character_attacked','emit','activate'):
   counted(R.CombatEngine,name,'Engine.'+name)
  STAGE='ingress';ingress(h,R,job['layout']);components(h,R,unit);natural(h,job)
  strict(len(PASSES),16);strict(COUNTS['Engine.__init__'],2);strict(COUNTS['Engine.prepare_only'],2);strict(COUNTS['Engine.run'],1);status='PASS_THREE_WHELP_SOURCE_FINITE_COMPONENTS_ONE_MIXED_NATURAL_NOT_NATIVE'
 except BaseException as exc:
  save('first-error.json',dict(stage=STAGE,type=type(exc).__name__,message=str(exc),traceback=traceback.format_exc(),calls=COUNTS.copy()))
  if ACTIVE is not None:
   try:save('same-instance-failure.json',dict(events=ACTIVE.events,audit=ACTIVE.random.audit,snapshot=ACTIVE.snapshot(),history=ACTIVE.histories.snapshot()))
   except BaseException as exc2:save('failure-diagnostic-error.json',dict(type=type(exc2).__name__,message=str(exc2)))
 finally:
  signal.alarm(0);after=[pin(ROOT/x['path'])for x in refs];strict(after,refs);save('source-after.json',after);save('input-harness-after.json',dict(plan=verify(PLAN/'owned-files.json'),harness=verify(HARNESS/'owned-files.json')))
  save('measured-prepare-and-reflection.json',dict(prepare=PREPARES,reflection=REFLECTIONS,start_gains=START_GAINS))
  result=dict(status=status,stage=STAGE,passed_groups=len(PASSES),reject_calls=len(REJECTS),calls=COUNTS,wall_seconds=time.monotonic()-t,source_refs_unchanged=len(after),Native=0,Expected=0,pool=0,old_tests=0,auto_retry=False)
  save('result.json',result);save('owned-files.json',dict(files=[pin(p)for p in sorted(OUT.iterdir())if p.is_file()],no_more_writes=True))
 print(json.dumps(result));return 0 if status.startswith('PASS')else 1
if __name__=='__main__':
 def timeout(signum,frame):raise TimeoutError('phase49835second wholeharness wall deadline')
 signal.signal(signal.SIGALRM,timeout);signal.alarm(35);sys.exit(main())
