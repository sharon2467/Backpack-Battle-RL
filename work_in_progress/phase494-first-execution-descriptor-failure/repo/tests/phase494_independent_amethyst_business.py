"""Sealed finite201 caller controls; synthetic prestates are not native facts."""
import copy,functools,hashlib,importlib,json,signal,struct,sys,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'data/phase493-source-amethyst-whelp'
PLAN=ROOT/'data/phase494-independent-business-plan'
HARNESS=ROOT/'data/phase494-independent-harness-source'
OUT=ROOT/'data/phase494-independent-business-first-001'
W='P:whelp';SQ='P:squirrel';COUNTS={};PASSES=[];REJECTS=[];PREPARES=[];TRAIL=[];ACTIVE=None;MODE=None;STAGE='preflight';R=None

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
def counted(obj,name,label):
 orig=getattr(obj,name)
 @functools.wraps(orig)
 def call(*a,**kw):
  global ACTIVE
  COUNTS[label]=COUNTS.get(label,0)+1
  if label=='Engine.prepare_only':
   e=a[0];ACTIVE=e;strict(e.random.audit,[]);v=orig(*a,**kw);strict(e.random.audit,[])
   record=dict(mode=MODE,audit=copy.deepcopy(e.random.audit),source_rng=e.random.snapshot(),order=e.preparation_order,
    caches={i:[x.instance_id for x in e.affected_items(e.items[i])]for i in (SQ,'P:whetstone')if i in e.items})
   PREPARES.append(record)
   if MODE=='unit':
    rows=[rr('cooldown:'+i,.975 if e.items[i].side=='O' else .95,1.05,1.0)for i in e.preparation_order if e.items[i].has_cooldown]
    rows += [ri(f'random_stack:{W}:O:give:{i}',0,2,n)for i,n in enumerate((0,2,0,1))]
    rows += [rr(f'reflect:O:{W}:'+kind,0.0,100.0,50.0)for kind in ('Poison','Poison','Cold','Blind')]
    e.random=UnitTape(rows,e)
   return v
  if label in ('Engine.pre_item_damage','Engine.emit','Engine.give_stack','Engine.remove_random_buffs')and MODE=='unit':
   e=a[0];TRAIL.append(dict(method=name,position=getattr(e.random,'position',None),events=len(e.events),origin=getattr(a[1],'instance_id',a[1]) if len(a)>1 else None))
  return orig(*a,**kw)
 setattr(obj,name,call)
def reject(name,fn):
 before=COUNTS.copy()
 try:fn()
 except ValueError as exc:strict(COUNTS,before,'reject_preRNG');REJECTS.append(dict(name=name,error=str(exc)))
 else:raise AssertionError('accepted '+name)
def ingress(h,m,layout):
 d=m.CATALOG[201]
 strict(d['shape'],((0,0),(1,0),(0,1),(1,1)));strict(d.get('stars',()),());strict((d['socket_count'],d['default_gem']),(1,None))
 strict([d[x]for x in ('ranged','pet','dark','effect')],[True]*4)
 strict([d[x]for x in ('cooldown','stamina','accuracy','min_damage','max_damage','start_debuffs','remove_buffs')],[2.1,0.0,90.0,5,10,4,1])
 strict((len(m.CATALOG),len(h.ITEMS),m.GAINED_STACK_FLAGS[201]),(78,75,1792));assert 201 in m.EMPOWERABLE_WEAPON_IDS and 201 not in m.CACHED_AFFECTED_IDS
 check('01_descriptor_and_bounded_dualtype_Source')
 for keep in ({201},{164},{164,201}):
  x=copy.deepcopy(layout)
  for s in x['sides']:s['items']=[i for i in s['items']if i['item_index']not in {164,201}-keep]
  h.validate_experimental_nonking_layout(x)
 check('02_new_three_closed_admissions')
 reject('old_initialize',lambda:h.initialize(layout,49401));reject('old_Squirrel',lambda:h.initialize_squirrel(layout,49401))
 old=copy.deepcopy(layout)
 for s in old['sides']:s['items']=[i for i in s['items']if i['item_index']not in(164,201)]
 reject('old_batch_bad_second',lambda:h.run_batch([dict(layout=old,seed=49401),dict(layout=layout,seed=49401)],keep_results=True))
 check('03_old_admission_atomic',REJECTS.copy())
 reject('noextra',lambda:h.initialize_experimental_nonking(old,49401))
 for item_id in (262,129,999):
  x=copy.deepcopy(layout);next(i for i in x['sides'][0]['items']if i['item_index']==201)['item_index']=item_id
  reject('badID'+str(item_id),lambda x=x:h.initialize_experimental_nonking(x,49401))
 x=copy.deepcopy(layout);x['sides'][0]['character_class']=2;reject('class',lambda:h.initialize_experimental_nonking(x,49401))
 x=copy.deepcopy(layout);next(i for i in x['sides'][0]['items']if i['item_index']==201)['power']=2;reject('modifier',lambda:h.initialize_experimental_nonking(x,49401))
 reject('bool_seed',lambda:h.initialize_experimental_nonking(layout,True));check('04_new_rejections',REJECTS[3:]);strict(COUNTS,{})
def reset(e,t,mana=2,block=0,protect=0,invu=False):
 e.util_time=float(t);e.ended=False;e.winner=None;e.pending_terminal=False
 for side in ('P','O'):
  c=e.characters[side];c.dead=False;c.hp=c.max_hp;c.invulnerable=False;c.buff_protect_stacks=0
  for kind in range(100,111):
   name=R.STACK_NAMES_BY_TYPE[kind];value=mana if side=='O'and kind==105 else block if side=='O'and kind==100 else 0
   setattr(c,name.lower(),value);f,_=e._buff_record(side,name);f['permanentStacks']=value;f['temporaryStacks'].clear();e.histories.stack(side,kind)
 c=e.characters['O'];c.buff_protect_stacks=protect;c.invulnerable=invu;c.accuracy.reset();c.accuracy.last_result=True
 e.items[W].damage_range.acc=0.0;e.items[W].crit_chance=0.0

def attack_rows(hit=True,picks=1,double=False,damage=True):
 rows=[rf('double_attack_effect:'+W,0.0 if double else .5),rf('accuracy:O:'+W,.5 if hit else 1.0)]
 rows += [ri('random_stack:'+W+':O:take:0',0,0,0)for _ in range(picks)]
 if hit and damage:rows.append(ri('damage:'+W,6,11,6))
 return rows

def segment(e,name,rows,fn):
 global STAGE
 STAGE=name;start=len(e.events);before=COUNTS.copy();TRAIL.clear();e.random=UnitTape(rows,e)
 save(name+'.prestate.json',dict(synthetic=True,util_time=e.util_time,ended=e.ended,characters=e.snapshot()['characters'],before_calls=before))
 answer=fn();events=copy.deepcopy(e.events[start:]);saved=save(name+'.actual.json',dict(synthetic=True,events=events,answer=answer,audit=e.random.audit,trail=TRAIL,snapshot=e.snapshot(),history=e.histories.snapshot(),calls=COUNTS.copy()))
 e.random.assert_consumed();return answer,events,before,saved

def components(h,m,layout):
 global MODE,ACTIVE,STAGE
 MODE='unit';STAGE='05_unit_initialize';TRAIL.clear();b=h.initialize_experimental_nonking(layout,49401);e=b._engine;ACTIVE=e;e.random.assert_consumed()
 save('unit-initialize.json',dict(prepared=PREPARES[-1],events=e.events,audit=e.random.audit,trail=TRAIL,snapshot=e.snapshot(),history=e.histories.snapshot(),initialization=b.initialization))
 strict(PREPARES[-1]['caches'],{'P:whetstone':[W]});strict(sum(x['kind']=='timer'for x in e.runtime_inputs.data['nodes']),26)
 strict(e.items[W].bonus_damage,1);strict(e.damage_bounds(e.items[W]),(6,11))
 strict(b.initialization['source_extension'],'source-headless-experimental-nonking-defaults/1');strict(b.initialization['experimental_items'],[201]);strict(b.initialization['catalog_registered'],78)
 check('05_real_prepare_and_cooldown_before_start',PREPARES[-1])
 ev=[x for x in e.events if x['origin']==W];strict([x['type']for x in ev],[108,110,109,0]);strict([x['params']['amount']for x in ev[:3]],[2,1,1]);strict([x['parent']for x in ev],[None]*4)
 gains=[x for x in TRAIL if x['method']=='give_stack'];strict(len(gains),3);strict([x['position']for x in gains],[5,7,8])
 strict([x['label']for x in e.random.audit],[f'cooldown:{W}']+[f'random_stack:{W}:O:give:{i}'for i in range(4)]+[f'reflect:O:{W}:'+k for k in ('Poison','Poison','Cold','Blind')])
 strict(e.histories.item_metrics[W][4],1);check('06_four_draws_grouping_order_then_Activation',ev)
 for name,hit,block,invu,mana,protect,double in [
  ('07_miss',False,0,False,2,0,False),('08_positive_hit',True,0,False,2,0,False),
  ('09_block_zero',True,20,False,2,0,False),('10_invu_zero',True,0,True,2,0,False),
  ('11_empty_pool',True,0,False,0,0,False),('12_protected_loss',True,0,False,2,1,False),
  ('13_double_own',True,0,False,2,0,True)]:
  reset(e,int(name[:2]),mana,block,protect,invu);num=(2 if double else 1)if hit and mana else 0;hp=e.characters['O'].hp;metric=e.histories.item_metrics[W][4]
  answer,ev,before,saved=segment(e,name,attack_rows(hit,num,double),lambda:e.weapon_attack(e.items[W]))
  nloss=(0 if protect else num);strict(e.characters['O'].mana,mana-nloss);strict(e.characters['P'].mana,0)
  loss=[x for x in ev if x['type']==105];strict(len(loss),num)
  for x in loss:strict((x['origin'],x['target'],x['parent']),(W,1,None));strict(x['params']['amount'],1 if protect else -1)
  if protect:strict(loss[0]['params']['protected'],True);strict(e.characters['O'].buff_protect_stacks,0)
  strict(e.histories.logger('O')['stackHistories'][105].values[-1],mana-nloss)
  attack=[x for x in ev if x['type']in(1,2,3)];strict(len(attack),1);strict(len([x for x in ev if x['type']==0 and x['origin']==W]),1)
  strict(e.histories.item_metrics[W][4],metric+1);strict(COUNTS['Engine.attack']-before.get('Engine.attack',0),1)
  strict(COUNTS['Engine.on_character_attacked']-before.get('Engine.on_character_attacked',0),1)
  strict(COUNTS['Engine.pre_item_damage']-before.get('Engine.pre_item_damage',0),2 if double else 1)
  if loss:assert all(x['id']<attack[0]['id']for x in loss)
  if not hit:strict(attack[0]['type'],3)
  else:strict(attack[0]['params']['damage'],0 if invu else 6)
  strict(e.characters['O'].hp,hp-(6 if hit and not block and not invu else 0))
  if hit and mana:
   methods=[x['method']for x in TRAIL];damage_pos=next(i for i,x in enumerate(TRAIL)if x.get('label')=='damage:'+W)
   assert all(i<damage_pos for i,x in enumerate(TRAIL)if x['method']=='remove_random_buffs')
  strict(e.logging_mode,1);strict(e.signal_queue,[]);check(name,dict(events=ev,artifact=saved))
 reset(e,14);e.characters['O'].dead=True
 _,ev,before,_=segment(e,'14_dead_defender',[],lambda:e.attack(e.items[W]));strict(ev,[]);strict(COUNTS.get('Engine.pre_item_damage'),before.get('Engine.pre_item_damage'));check('14_dead_defender_no_hook_or_draw')
 reset(e,15);c=e.characters['P'];c.empower=2;c.buff_fields[106]['permanentStacks']=2
 strict(e.damage_bounds(e.items[W]),(8,13));c.empower=0;c.buff_fields[106]['permanentStacks']=0
 for side in ('P','O'):
  ch=e.characters[side];strict((ch.ranged_spikes_limit,ch.effect_spikes_limit,ch.ranged_vampirism_limit),(0.0,0.0,0.0));assert all(v==0.0 for v in ch.typed_damage_factors.values())
 c.vampirism=3;c.buff_fields[103]['permanentStacks']=3;c.hp=100.0;e.characters['O'].spikes=3;e.characters['O'].buff_fields[104]['permanentStacks']=3
 # Picker list is Spikes then Mana; choose Mana, leaving positive Spikes to discriminate ranged default path.
 rows=attack_rows();rows[2]=ri('random_stack:'+W+':O:take:0',0,1,1)
 _,ev,_,_=segment(e,'15_default_dualtype_empower',rows,lambda:e.weapon_attack(e.items[W]));strict(c.hp,100.0);assert not any(x['type']==12 or x['origin']==104 for x in ev);strict(m.GAINED_STACK_FLAGS[201]&254,0)
 check('15_Whetstone_empower_and_default_ranged_no_spikes_vamp',ev)
 reset(e,16);_,ev,_,_=segment(e,'16_no_Squirrel_pitch',[],lambda:e.activate(e.items[W]));strict([x['type']for x in ev],[0]);check('16_Whelp_has_no_Squirrel_pitch',ev)

def natural(h,job):
 global STAGE,MODE,ACTIVE
 MODE='natural';STAGE='17_natural_initialize';b=h.initialize_experimental_nonking(copy.deepcopy(job['layout']),job['seed']);e=b._engine;ACTIVE=e
 save('natural-initialize.json',dict(initialization=b.initialization,prepare=PREPARES[-1],events=e.events,audit=e.random.audit,snapshot=e.snapshot()))
 strict(PREPARES[-1]['caches'][SQ],['P:berry0','P:goobert','P:berry1',W]);strict(e.items[SQ].speed_scale,4*15.0/100.0);strict(type(e.random),h.CombatRandom)
 STAGE='17_natural_run';result=b.run(max_seconds=120.0);output=save('natural-source-output.json',result)
 strict(e.finalized,True);strict(b.done,True);strict(e.king_mode,False);strict(sum(x['kind']=='timer'for x in e.runtime_inputs.data['nodes']),26)
 strict(result['coverage']['formal_support'],75);strict(result['coverage']['catalog_registered'],78);strict(result['coverage']['experimental_items'],[164,201]);strict(result['coverage']['status'],'EXPERIMENTAL_NONKING_SOURCE_NOT_NATIVE_VALIDATED')
 strict(result['source_rng'],e.random.snapshot());strict(result['random_inputs'],e.random.audit);strict(result['initialization']['root_seed'],49401)
 startup=[x for x in e.random.audit if x['label'].startswith('random_stack:'+W+':O:give:')];strict(len(startup),4)
 losses={i:[x for x in e.events if x['origin']==i and 101<=x['type']<=107 and x['params'].get('amount',0)<0]for i in (W,SQ)}
 acts={i:[x for x in e.events if x['origin']==i and x['type']==0]for i in (W,SQ)}
 summary=dict(status='EXPERIMENTAL_SOURCE_NOT_NATIVE',output=output,seed=49401,items=22,events=len(e.events),draws=len(e.random.audit),timers=26,winner=e.winner,simulated_seconds=result['final']['timestamp'],
  activations={i:len(v)for i,v in acts.items()},losses={i:len(v)for i,v in losses.items()},startup_draws=4,source_rng=e.random.snapshot(),
  HIT=dict(Whelp_removal='HIT'if losses[W]else'NOT_HIT',Squirrel_steal='HIT'if losses[SQ]else'NOT_HIT',same_category_pool='HIT'if {x['type']for x in losses[W]}&{x['type']for x in losses[SQ]}else'NOT_HIT',Pet_speed='HIT',natural_protection='NOT_CLAIMED',natural_double='NOT_CLAIMED'),no_input_tuning=True)
 save('natural-summary.json',summary);check('17_one_fixed_natural_Source',summary)

def main():
 global MODE,STAGE,R
 OUT.mkdir(exist_ok=False);start=time.monotonic();status='FAILED';source_rows=[]
 try:
  verify(HARNESS/'owned-files.json');verify(PLAN/'owned-files.json','450f7f82f8ab2b71d0150e084ebf72913715e572f91be9f7a213f8e76cc35b0e')
  source_rows=verify(SOURCE/'owned-files.json','6b10e35d7487ab7834ae30ee4e3f51241c70d0c09067fe4c8f83860c4349c0c4')
  job=json.loads((PLAN/'natural-job.json').read_bytes());unit=json.loads((HARNESS/'synthetic-layout.json').read_bytes())
  sys.dont_write_bytecode=True;sys.pycache_prefix=str(OUT/'unused-bytecode-cache');sys.path.insert(0,str(SOURCE/'staged'));STAGE='import_frozen'
  h=importlib.import_module('headless');R=importlib.import_module('native_replay_v8.engine');allowed={str((ROOT/x['path']).resolve())for x in source_rows if '/staged/'in x['path']};imports=[]
  for name,module in list(sys.modules.items()):
   if name in('headless','original_rng','godot_pcg_integer')or name.startswith(('native_replay_v7','native_replay_v8')):
    path=str(Path(module.__file__).resolve());assert path in allowed,(name,path);imports.append(dict(name=name,path=path))
  save('imports.json',imports)
  for obj,name,label in [(h,'derive_stream_seeds','derive_stream_seeds'),(h.CombatRandom,'__init__','CombatRandom.__init__'),(h.GodotPCGInteger,'__init__','PCG.__init__')]:counted(obj,name,label)
  for name in('__init__','prepare_only','activate_from_checkpoint','run','attack','weapon_attack','pre_item_damage','on_character_attacked','inflict_random_debuffs','remove_random_buffs','steal_random_buff','give_stack','emit','activate'):
   counted(R.CombatEngine,name,'Engine.'+name)
  STAGE='ingress';ingress(h,R,job['layout']);components(h,R,unit);natural(h,job)
  strict(len(PASSES),17);strict(COUNTS['Engine.__init__'],2);strict(COUNTS['Engine.prepare_only'],2);strict(COUNTS['Engine.run'],1)
  status='PASS_EXPERIMENTAL_AMETHYST_SOURCE_COMPONENTS_AND_ONE_MIXED_NATURAL_NOT_NATIVE'
 except BaseException as exc:
  save('first-error.json',dict(stage=STAGE,type=type(exc).__name__,message=str(exc),traceback=traceback.format_exc(),calls=COUNTS.copy()))
  if ACTIVE is not None:
   try:save('same-instance-failure.json',dict(events=ACTIVE.events,audit=ACTIVE.random.audit,snapshot=ACTIVE.snapshot(),history=ACTIVE.histories.snapshot()))
   except BaseException as second:save('failure-diagnostic-error.json',dict(type=type(second).__name__,message=str(second)))
 finally:
  signal.alarm(0);after=[pin(ROOT/x['path'])for x in source_rows];strict(after,source_rows,'source_after');save('source-after.json',after);save('actual-prepare-boundaries.json',PREPARES);save('input-harness-after.json',dict(plan=verify(PLAN/'owned-files.json'),harness=verify(HARNESS/'owned-files.json')))
  result=dict(status=status,stage=STAGE,passed_groups=len(PASSES),rejection_calls=len(REJECTS),calls=COUNTS,wall_seconds=time.monotonic()-start,source_refs_unchanged=len(after),Native=0,Expected=0,old_tests=0,pool=0,auto_retry=False)
  save('result.json',result);save('owned-files.json',dict(files=[pin(p)for p in sorted(OUT.iterdir())if p.is_file()],no_more_writes=True))
 print(json.dumps(result));return 0 if status.startswith('PASS')else 1
if __name__=='__main__':
 def timeout(signum,frame):raise TimeoutError('phase494 whole harness35s wall deadline')
 signal.signal(signal.SIGALRM,timeout);signal.alarm(35);sys.exit(main())
