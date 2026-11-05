"""Frozen independent Source-only Wand controls; requires separate Root execution release."""
import __future__,argparse,ast,copy,dataclasses,functools,hashlib,importlib,json,math,os,random,re,resource,signal,stat,struct,sys,time,traceback,types,typing
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PLAN=ROOT/'data/phase664-wand-exact-harness'
SRC=ROOT/'data/phase662-wand422-source/staged'
JOB=ROOT/'data/phase662-wand422-source/source-job.json'
OUT=ROOT/'data/phase664-independent-wand-first-001'
MODE='preflight';STAGE='preflight';ACTIVE=None
COUNTS={};HOOKS=[];PENDING={};DIRECT=[];SETUP=[];CASES=[];REJECTS=[];READS={};WRITES=[];WRITTEN={};IMPORTS=[]
NAMES={100:'Block',101:'Lucky',102:'Regeneration',103:'Vampirism',104:'Spikes',105:'Mana',106:'Empower',107:'Heat',108:'Poison',109:'Blind',110:'Cold'}


def digest(b):return hashlib.sha256(b).hexdigest()


def descriptor(p,b=None):
 p=Path(p);b=p.read_bytes() if b is None else b
 return dict(path=str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p),size=len(b),sha256=digest(b))


def save(name,value):
 # Once serialized: audit list changes cannot alter the bytes hashed for owner.
 raw=(json.dumps(value,ensure_ascii=False,allow_nan=False,separators=(',',':'))+'\n').encode()
 p=OUT/name;p.write_bytes(raw);row=descriptor(p,raw);WRITTEN[name]=row;return row


def strict(a,b,where='value'):
 assert type(a)is type(b),(where,type(a).__name__,type(b).__name__)
 if isinstance(a,float):assert struct.pack('>d',a)==struct.pack('>d',b),(where,a,b)
 elif isinstance(a,dict):
  assert {(type(k),k)for k in a}=={(type(k),k)for k in b},(where,'keys')
  for k in a:strict(a[k],b[k],where+'.'+str(k))
 elif isinstance(a,(tuple,list)):
  assert len(a)==len(b),(where,'length',len(a),len(b))
  for j,(x,y)in enumerate(zip(a,b)):strict(x,y,where+'['+str(j)+']')
 else:assert a==b,(where,a,b)


def enter(label,fn,*args,setup=False,**kwargs):
 row=dict(mode=MODE,stage=STAGE,label=label,status='ENTERED');(SETUP if setup else DIRECT).append(row)
 try:answer=fn(*args,**kwargs)
 except BaseException as ex:
  row.update(status='RAISED',exception=type(ex).__name__,message=str(ex));raise
 row['status']='RETURNED';return answer


def count(mode,qualname):
 return sum(n for k,n in COUNTS.get(mode,{}).items() if k.endswith(':'+qualname))


def profile(frame,event,arg):
 global ACTIVE
 path=frame.f_code.co_filename
 if not path.startswith(str(SRC)+os.sep) or event not in ('call','return'):return
 qual=frame.f_code.co_qualname;loc=frame.f_locals;obj=loc.get('self')
 if event=='call':
  key=str(Path(path).relative_to(SRC))+':'+qual;table=COUNTS.setdefault(MODE,{});table[key]=table.get(key,0)+1
  if qual=='CombatEngine.__init__':ACTIVE=obj
  watched={'CombatEngine.trigger','CombatEngine.adjust_cooldown','CombatEngine.activate','CombatEngine.give_least_buffs','CombatEngine.remove_most_buffs','CombatEngine.give_stack','CombatEngine.use_stack','CombatEngine.remove_stack','CombatEngine.give_stamina_regeneration','CombatEngine.flush_logging_queue','CombatEngine.set_logging_mode','TapeRandom._take'}
  history=qual=='CombatHistories.character' and loc.get('stat')==20
  if qual not in watched and not history:return
  e=getattr(obj,'engine',None) if history else obj if qual.startswith('CombatEngine.') else ACTIVE
  if e is None or not hasattr(e,'event_num'):return
  row=dict(mode=MODE,stage=STAGE,method=qual,event='call',event_num=e.event_num,draws=len(e.random.audit),side=loc.get('side'),item=getattr(loc.get('item'),'instance_id',None))
  if qual=='CombatEngine.give_stamina_regeneration':row.update(amount=loc['amount'],before=e.characters[loc['side']].stamina_regen)
  if qual=='TapeRandom._take':row.update(kind=loc['kind'],label=loc['label'],args=copy.deepcopy(loc['args']))
  if qual=='CombatEngine.activate':row['limiter_before']=loc['item'].activations_this_frame
  if history:
   side=loc['side'];hist=e.histories.loggers[0 if side=='P' else 1]['characterStatHistories'][20]
   row.update(side=side,before_length=len(hist.values),before_last=copy.deepcopy(hist.values[-1]) if hist.values else None,expected_value=float((e.characters[side].stamina_regen-1)*100.0),effective_event=e.event_num+int(loc['next_event']) if loc['event_num'] is None else loc['event_num'])
  HOOKS.append(row);PENDING[id(frame)]=row
 else:
  row=PENDING.pop(id(frame),None)
  if row is None:return
  e=getattr(obj,'engine',None) if qual=='CombatHistories.character' else obj if qual.startswith('CombatEngine.') else ACTIVE
  row['returned']=True;row['return_event_id']=arg.get('id') if type(arg)is dict else None
  if qual=='CombatEngine.give_stamina_regeneration':row['after']=e.characters[loc['side']].stamina_regen
  if qual=='CombatEngine.activate':row['limiter_after']=loc['item'].activations_this_frame
  if qual=='CombatHistories.character':
   hist=e.histories.loggers[0 if loc['side']=='P' else 1]['characterStatHistories'][20]
   row.update(after_length=len(hist.values),after_last=copy.deepcopy(hist.values[-1]),after_last_event=hist.event_numbers[-1])


def view(e):
 return dict(event_num=e.event_num,event_count=len(e.events),prepared=e.prepared,activated=e.activated,ended=e.ended,logging_mode=e.logging_mode,queue=len(e.signal_queue),util_time=e.util_time,time=e.time,
  sides={s:dict(stacks={str(k):getattr(c,n.lower())for k,n in NAMES.items()},regen=c.stamina_regen,base_regen=c.base_stamina_regen,buff_protect=c.buff_protect_stacks)for s,c in e.characters.items()},
  wand=dict(trigger_time=e.items['P:wand'].trigger_time,iteration_cooldown=e.items['P:wand'].iteration_cooldown,activations=e.items['P:wand'].activations,limiter=e.items['P:wand'].activations_this_frame),
  wolves={i:dict(registered=x.wolpertinger_buff_listener_registered,coefficient=x.wolpertinger_stamina_regen_per_buff)for i,x in e.items.items()if x.item_index==231})


def passed(name,detail=None):
 CASES.append(dict(name=name,status='PASS',detail=detail));save('case-progress.json',CASES)


def reject(name,fn,error,*args,**kwargs):
 before=copy.deepcopy(args);draws=len(ACTIVE.random.audit) if ACTIVE is not None else 0;ctors=sum(count(m,'CombatEngine.__init__')for m in COUNTS)
 try:enter(name,fn,*args,**kwargs)
 except ValueError as ex:
  strict(str(ex),error,name+' first rejection');REJECTS.append(dict(name=name,error=str(ex)))
 else:raise AssertionError('expected rejection '+name)
 # Engine/Item args are not compared by deepcopy identity; callers verify their real state separately.
 if all(type(x)in(dict,list,str,int,float,bool,type(None))for x in args):strict(args,before,name+' arguments')
 strict(sum(count(m,'CombatEngine.__init__')for m in COUNTS),ctors,name+' ctor delta')
 if ACTIVE is not None:strict(len(ACTIVE.random.audit),draws,name+' draw delta')
 passed(name,dict(first_rejection=error))


def gates(h,vectors):
 global MODE,STAGE
 MODE='gates';STAGE='gates';fixture=None
 for g in vectors['gates']:
  arg=copy.deepcopy(g['layout']);before=copy.deepcopy(arg);fn=getattr(h,g['api'])
  if g['error']is not None:reject(g['name'],fn,g['error'],arg)
  else:
   value=enter(g['name'],fn,arg)
   if fixture is None:fixture=value
   passed(g['name'],dict(items=sum(len(s['items'])for s in value['sides'])))
  strict(arg,before,g['name']+' input immutable')
 return fixture


def reset(e,spec):
 # Explicit synthetic prestate; no manual listeners, events, history reset or flush.
 assert not e.signal_queue
 e.util_time=20.0;e.ended=False;e.pending_terminal=False;e.logging_mode=1
 for c in e.characters.values():
  c.dead=False;c.hp=180.0;c.stamina=5.0;c.stamina_regen=1.0;c.invulnerable=False;c.buff_protect_stacks=0;c.debuff_reflect_stacks=0;c.debuff_resist_stacks=0
  for k,n in NAMES.items():
   setattr(c,n.lower(),0);f=c.buff_fields[k];f['permanentStacks']=0;f['temporaryStacks']=[];f['resistStacks']=0
   for field in ('reflectChancePercent','resistChancePercent','cleanseProtectionChancePercent'):f[field]=0.0
 for item in e.items.values():
  item.last_activation_time=-1.0;item.activations_this_frame=0;item.trigger_time=0.0
  for k in item.buff_powers:item.buff_powers[k]=1.0;item.buff_amplification_chances[k]=0.0
 target=spec.get('target','P');c=e.characters[target]
 for k,n in zip((105,101,102),spec['counts']):setattr(c,NAMES[k].lower(),n);c.buff_fields[k]['permanentStacks']=n
 if spec.get('outside_empower'):
  c.empower=spec['outside_empower'];c.buff_fields[106]['permanentStacks']=spec['outside_empower']
 c.buff_protect_stacks=spec.get('protect',0)
 if spec.get('limiter'):
  e.items['P:wand'].last_activation_time=e.util_time;e.items['P:wand'].activations_this_frame=spec['limiter']


def feedback_check(raw,expected):
 rows=[x for x in raw['hooks']if x['method']=='CombatEngine.give_stamina_regeneration']
 strict([(x['side'],x['amount'])for x in rows],[(s,n*((0.7*1.0)/100.0))for s,n in expected],'synchronous delta sequence')
 running={'P':1.0,'O':1.0}
 for row,(side,n)in zip(rows,expected):
  strict(row['before'],running[side],'feedback before');running[side]+=n*((0.7*1.0)/100.0);strict(row['after'],running[side],'feedback after')
 histories=[x for x in raw['hooks']if x['method']=='CombatHistories.character']
 strict(len(histories),len(rows),'stat20 actual calls')
 for h,g in zip(histories,rows):
  strict(h['side'],g['side']);strict(h['effective_event'],g['event_num'],'stat20 event id')
  strict(h['expected_value'],float((g['after']-1)*100.0),'stat20 Source projection');strict(h['after_last'],h['expected_value'])
  changed=type(h['before_last'])is not type(h['expected_value'])or h['before_last']!=h['expected_value']
  strict(h['after_length'],h['before_length']+int(changed),'actual dedup')
  if changed:strict(h['after_last_event'],h['effective_event'])
 for side in running:strict(raw['after']['sides'][side]['regen'],running[side],side+' final regen')


def segment(e,spec,subset):
 global STAGE
 STAGE=spec['name'];reset(e,spec);w=e.items['P:wand'];before=view(e);event0=len(e.events);hook0=len(HOOKS);draw0=len(e.random.audit);ret=None;parent=e.events[-1]['id'] if spec.get('real_parent') else None
 if spec['kind']=='trigger':ret=enter(spec['name'],e.trigger,w)
 elif spec['kind']=='remove':ret=enter(spec['name'],e.remove_most_buffs,w,spec['amount'],parent,spec['use'],subset)
 else:
  null=enter('NULL_helper',e.remove_most_buffs,w,0,None,True,subset);strict(null,None)
  ret=enter('NULL_Empower',e.give_stack,w,'P','Empower',1,None)
  enter('NULL_activate',e.activate,w)
 raw=dict(name=STAGE,synthetic_prestate=True,before=before,after=view(e),result=copy.deepcopy(ret),input_parent=parent,events=copy.deepcopy(e.events[event0:]),hooks=copy.deepcopy(HOOKS[hook0:]),rows=copy.deepcopy(e.random.audit[draw0:]))
 save('segment-'+STAGE+'.json',raw)
 strict(raw['rows'],spec['rows'],'exact primitive rows');strict(tuple(subset),(105,101,102),'ordered subset unchanged')
 strict(raw['after']['logging_mode'],1);strict(raw['after']['queue'],0)
 strict(sum(x['method']=='CombatEngine.flush_logging_queue'for x in raw['hooks']),0)
 ev=raw['events'];expected_feedback=[]
 if spec['kind']=='trigger':
  converted=spec['conversion'];t=spec['selected'];limited=bool(spec.get('limiter'))
  strict([x['type']for x in ev],([t,t,106]if converted else[t])+([]if limited else[0]))
  strict(ev[0]['params']['amount'],1);strict(ev[0]['parent'],None)
  expected_feedback=[('P',1)]
  if converted:
   strict(ev[1]['params']['amount'],-1);strict(ev[1]['params']['used'],True);strict(ev[1]['parent'],None)
   strict(ev[2]['params']['amount'],1);strict(ev[2]['parent'],ev[1]['id']);expected_feedback.extend([('P',-1),('P',1)])
   strict(raw['after']['sides']['P']['stacks'][str(t)],9)
  else:strict(raw['after']['sides']['P']['stacks'][str(t)],1)
  expected_cd=3.3*1.0;strict(raw['after']['wand']['iteration_cooldown'],expected_cd);strict(raw['after']['wand']['trigger_time'],0.0+expected_cd)
  strict(raw['after']['wand']['activations'],before['wand']['activations']+int(not limited))
  strict(raw['after']['wand']['limiter'],4 if limited else 1)
  strict(sum(x['method']=='CombatEngine.adjust_cooldown'for x in raw['hooks']),1)
  strict(sum(x['method']=='CombatEngine.activate'for x in raw['hooks']),1)
  for x in ev:
   if x['type']==0:strict(x['parent'],None)
 elif spec['kind']=='remove':
  side=spec['target'];t=spec['selected'];loss=spec['loss'];protected=spec.get('protect',0)>0 and not spec['use']
  if loss:
   strict(len(ev),1);strict(ret,ev[0]);strict(ret['type'],t);strict(ret['params']['amount'],-loss);strict(ret['params']['used'],spec['use']);strict(ret['parent'],parent)
   expected_feedback=[(side,-loss)]
  else:
   strict(ret,None);strict(len(ev),int(protected))
   if protected:strict(ev[0]['params']['protected'],True);strict(ev[0]['params']['amount'],1);strict(ev[0]['parent'],parent)
  strict(raw['after']['sides'][side]['stacks'][str(t)],before['sides'][side]['stacks'][str(t)]-loss)
  other='O'if side=='P'else'P';strict(raw['after']['sides'][other],before['sides'][other],'unselected side')
  strict(raw['after']['sides'][side]['buff_protect'],0 if protected else spec.get('protect',0))
  strict(raw['after']['wand']['activations'],before['wand']['activations'])
  if spec.get('outside_empower'):strict(raw['after']['sides'][side]['stacks']['106'],99)
 else:
  strict([x['type']for x in ev],[106,0]);strict(ev[0]['params']['amount'],1);strict(ev[0]['parent'],None);strict(ev[1]['parent'],None)
  strict(ret,ev[0]);strict(raw['after']['wand']['activations'],before['wand']['activations']+1);expected_feedback=[('P',1)]
 feedback_check(raw,expected_feedback);passed(spec['name'],dict(events=len(ev),draws=len(raw['rows']),synthetic=True))


def components(h,m,fixture,vectors):
 global MODE,STAGE,ACTIVE
 MODE='component';STAGE='runtime'
 runtime=enter('runtime_inputs',h.runtime_inputs,fixture,vectors['preparation_order'],setup=True)
 tape=enter('TapeRandom',m.TapeRandom,copy.deepcopy(vectors['tape']),setup=True)
 e=enter('component_ctor',m.CombatEngine,fixture,tape,runtime,setup=True);ACTIVE=e;e.util_time=0.0
 enter('component_prepare_only',e.prepare_only,setup=True)
 strict(tape.position,0);strict(e.activated,False);strict(e.prepared,True)
 for side in ('P','O'):
  wolf=e.items[side+':wolper'];strict(wolf.wolpertinger_buff_listener_registered,True)
  strict(e.characters[side].base_stamina_regen,1.0);strict(wolf.wolpertinger_stamina_regen_per_buff,(0.7*1.0)/100.0)
 save('component-prepared.json',dict(view=view(e),preparation_order=e.preparation_order,synthetic_order=True))
 subset=tuple(vectors['subset'])
 for spec in vectors['segments']:segment(e,spec,subset)
 STAGE='type_guards'
 for v in vectors['guard_rejects']:
  before=view(e);reject(v['name'],e.remove_most_buffs,vectors['guard_error'],e.items['P:wand'],v['amount'],None,v['use'],subset);strict(view(e),before,'rejection no mutation')
 strict(tape.position,22);strict(tape.audit,vectors['tape']);strict(tape.records,vectors['tape'])
 strict(len(CASES),21);strict(len(DIRECT),23);strict(len(REJECTS),6);strict([x['label']for x in DIRECT],vectors['direct_order'],'exact direct ledger')
 for method in ('activate_from_checkpoint','step','run'):strict(count('component','CombatEngine.'+method),0)
 strict(count('component','CombatEngine.__init__'),1);strict(count('component','CombatEngine.prepare_only'),1)
 save('component-final.json',dict(view=view(e),events=e.events,audit=tape.audit,subcases=CASES,profile=COUNTS.get('component',{}),source_only=True))


def natural(h,job):
 global MODE,STAGE,ACTIVE
 MODE='natural';STAGE='initialize'
 b=enter('natural_initialize',h.initialize_experimental_nonking,copy.deepcopy(job['layout']),job['seed'],setup=True);e=b._engine;ACTIVE=e
 save('natural-initialization.json',b.initialization)
 STAGE='run';raw=enter('natural_run',b.run,max_seconds=job['max_seconds'],setup=True)
 output=save('natural-source-output.json',raw) # Seal raw bytes before any result assertion.
 STAGE='natural_assertions'
 strict(e.finalized,True);strict(b.done,True);strict(e.king_mode,False)
 strict(raw['initialization']['root_seed'],66301);strict(raw['coverage']['formal_support'],75);strict(raw['coverage']['catalog_registered'],85)
 strict(raw['random_inputs'],e.random.audit);strict(raw['source_rng'],e.random.snapshot())
 strict(len(e.items),15);strict(sum(n['kind']=='timer'for n in e.runtime_inputs.data['nodes']),26)
 for method in ('__init__','prepare_only','activate_from_checkpoint','run'):strict(count('natural','CombatEngine.'+method),1)
 events=e.events;byid={x['id']:x for x in events};wand=[x for x in events if x['origin']=='P:wand']
 used=[x for x in wand if x['type']in(105,101,102)and x['params'].get('used')is True and x['params'].get('amount',0)<0]
 empowered=[x for x in wand if x['type']==106 and x['params'].get('amount',0)>0]
 for x in empowered:
  p=byid[x['parent']];assert p in used;assert p['id']<x['id']
 measures=dict(Wand_least_grant=sum(x['type']in(105,101,102)and x['params'].get('amount',0)>0 for x in wand),Wand_conversion=len(used),Wand_Empower_actual_use_parent=len(empowered),Wand_activation=sum(x['type']==0 for x in wand),Wolper_positive_feedback=sum(x['mode']=='natural'and x['method']=='CombatEngine.give_stamina_regeneration'and x['amount']>0 for x in HOOKS),Wolper_negative_feedback=sum(x['mode']=='natural'and x['method']=='CombatEngine.give_stamina_regeneration'and x['amount']<0 for x in HOOKS),Wand_limited_activate=sum(x['mode']=='natural'and x['method']=='CombatEngine.activate'and x['item']=='P:wand'and x.get('limiter_after',0)>3 for x in HOOKS))
 save('natural-summary.json',dict(status='SOURCE_ONLY_NOT_NATIVE',output=output,seed=job['seed'],items=15,simulated_seconds=e.elapsed,winner=e.winner,steps=count('natural','CombatEngine.step'),events=len(events),draws=len(e.random.audit),measures=measures,HIT={k:'HIT'if v else'NOT_HIT'for k,v in measures.items()},limits=['One fixed seed/layout; no retuning.','Synthetic zero-request/protected-loss/helper cases are not natural Wand branch claims.','Formal75 and Native qualification unchanged.']))


def audit(event,args):
 if event=='open':
  if isinstance(args[0],int):return
  path=str(Path(os.fsdecode(args[0])).resolve());mode,flags=args[1:3]
  writing=(isinstance(mode,str)and any(x in mode for x in'wa+'))or(isinstance(flags,int)and flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND))
  if writing:
   if not path.startswith(str(OUT)+os.sep):raise PermissionError('OUTSIDE_OUTPUT_WRITE '+path)
   WRITES.append(path)
  else:
   if path not in ALLOWED and not path.startswith(str(OUT)+os.sep):raise PermissionError('UNPINNED_READ '+path)
   key=MODE+':'+path;READS[key]=READS.get(key,0)+1
 if event in ('subprocess.Popen','os.system','socket.connect'):raise PermissionError('EXTERNAL_EXECUTION_FORBIDDEN')


def main():
 global MODE,STAGE,ALLOWED
 ap=argparse.ArgumentParser();ap.add_argument('--pins-sha256',required=True);args=ap.parse_args()
 assert not OUT.exists(),'fixed output must be unused'
 OUT.mkdir();started=time.monotonic();status='FAILED';refs=[]
 try:
  pinsraw=(PLAN/'pins.json').read_bytes();strict(digest(pinsraw),args.pins_sha256,'Root pins binding');refs=json.loads(pinsraw)['files']
  for row in refs:strict(descriptor(ROOT/row['path']),row,'before pin')
  save('source-input-before.json',refs)
  vectors=json.loads((PLAN/'vectors.json').read_bytes());job=json.loads(JOB.read_bytes());original_vectors=copy.deepcopy(vectors);original_job=copy.deepcopy(job)
  ALLOWED={str((ROOT/x['path']).resolve())for x in refs}|{str((PLAN/'pins.json').resolve())}
  sys.dont_write_bytecode=True;sys.path.insert(0,str(SRC));sys.addaudithook(audit);sys.setprofile(profile)
  STAGE='candidate_import';MODE='import';h=importlib.import_module('headless');m=importlib.import_module('native_replay_v8.engine')
  for name,module in list(sys.modules.items()):
   if name in ('headless','original_rng','godot_pcg_integer')or name.startswith(('native_replay_v7','native_replay_v8')):
    p=Path(module.__file__).resolve();assert str(p).startswith(str(SRC)+os.sep);IMPORTS.append(dict(module=name,source=descriptor(p)))
  save('actual-imports.json',IMPORTS)
  fixture=gates(h,vectors);components(h,m,fixture,vectors)
  strict(vectors,original_vectors,'all vectors immutable');strict(job,original_job,'natural job immutable')
  natural(h,job)
  strict(vectors,original_vectors);strict(job,original_job);strict(len(DIRECT),23);strict(len(CASES),21);strict(len(REJECTS),6)
  status='PASS_8_FAMILIES_21_SUBCASES_ONE_SOURCE_NATURAL_NOT_NATIVE'
 except BaseException as ex:
  frames=[];tb=ex.__traceback__
  while tb is not None:frames.append(dict(file=tb.tb_frame.f_code.co_filename,function=tb.tb_frame.f_code.co_name,line=tb.tb_lineno));tb=tb.tb_next
  save('first-error.json',dict(stage=STAGE,mode=MODE,type=type(ex).__name__,message=str(ex),traceback=frames,direct=DIRECT,setup=SETUP,profile=COUNTS))
  if ACTIVE is not None and hasattr(ACTIVE,'events')and 'P:wand'in getattr(ACTIVE,'items',{}):save('partial-instance.json',dict(view=view(ACTIVE),events=ACTIVE.events,audit=ACTIVE.random.audit))
 finally:
  sys.setprofile(None);signal.alarm(0);MODE='report';STAGE='report'
  after=[descriptor(ROOT/x['path'])for x in refs];save('source-input-after.json',after)
  if after!=refs:status='FAILED_SOURCE_INPUT_DRIFT'
  save('actual-profile-hooks.json',dict(counts=COUNTS,hooks=HOOKS,pending_frames=len(PENDING)))
  save('actual-call-ledger.json',dict(direct=DIRECT,setup=SETUP,subcases=CASES,rejects=REJECTS))
  result=dict(status=status,direct_calls=len(DIRECT),subcases_passed=len(CASES),expected_rejects=len(REJECTS),source_input_pins=len(refs),pins_unchanged=after==refs,profile=COUNTS,imports=IMPORTS,reads=READS,writes_before_result_serialization=list(WRITES),wall_seconds=time.monotonic()-started,peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,Native=0,Expected=0,pool=0,old_battles=0,auto_retry=False)
  save('result.json',result);save('owned-files.json',dict(schema='phase664-actual-owner/1',files=list(WRITTEN.values())))
 return 0 if status.startswith('PASS_')else 1


if __name__=='__main__':
 def deadline(signum,frame):raise TimeoutError('phase664 whole-process35s wall cap')
 signal.signal(signal.SIGALRM,deadline);signal.alarm(35);sys.exit(main())
