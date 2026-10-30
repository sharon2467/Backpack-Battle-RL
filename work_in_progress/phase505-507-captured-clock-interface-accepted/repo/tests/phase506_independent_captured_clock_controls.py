"""Finite506 synthetic integration; never a native input or fullbattle runner."""
import sys
sys.dont_write_bytecode=True
import argparse,copy,hashlib,importlib,json,math,struct,time,traceback
from pathlib import Path
from collections import Counter
from dataclasses import replace
ROOT=Path('/workspace/python-original-engine/repo')
SRC=ROOT/'data/phase506-independent-interface-source'
STAGE=ROOT/'data/phase505-captured-nonking-source-v3/staged'
def descriptor(path):
    b=path.read_bytes();return dict(path=str(path.relative_to(ROOT)),size=len(b),sha256=hashlib.sha256(b).hexdigest())
def write(path,value):
    path.write_text(json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
def same(a,b):
    if type(a) is not type(b):return False
    if type(a) is float:return struct.pack('>d',a)==struct.pack('>d',b)
    if type(a) in (list,tuple):return len(a)==len(b) and all(same(x,y) for x,y in zip(a,b))
    if type(a) is dict:return list(a)==list(b) and all(same(k,j) and same(a[k],b[j]) for k,j in zip(a,b))
    return a==b

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output-new',required=True);a=ap.parse_args()
    out=Path(a.output_new).resolve()
    if out.parent!=ROOT/'data' or out.name!='phase506-independent-interface-first-001':raise ValueError('fixed output')
    out.mkdir(exist_ok=False);started=time.monotonic();counts=Counter();codes={};primary=None;secondary=None
    result=dict(schema='phase506-actual-synthetic-interface/1',status='STARTED',negative_calls=0,negatives=[],checks=[],ctor_entered=0,ctor_success=0,ctor_rejected=0,prepare_calls=0,logical_activate_calls=0,step_attempts=0,positive_result_calls=0,fullbattle_runs=0,Godot=0,Expected=0,host=0,pool=0,native=0)
    pins=json.loads((SRC/'pins.json').read_text())
    def checkpoint(label,condition):
        if not condition:raise AssertionError(label)
        result['checks'].append(label);write(out/'progress.json',result)
    def rejected(label,fn,fragment,kind=ValueError):
        result['negative_calls']+=1;row=dict(name=label,status='STARTED');result['negatives'].append(row)
        try:fn()
        except kind as exc:
            row['error_type']=type(exc).__name__;row['error']=str(exc)
            if fragment not in str(exc):raise AssertionError('wrong rejection for '+label+': '+str(exc))
            row['status']='PASS'
        else:raise AssertionError('accepted negative '+label)
        write(out/'progress.json',result)
    def profile(frame,event,arg):
        if event=='call' and frame.f_code in codes:counts[codes[frame.f_code]]+=1
    def ctor(fixture,provider,dto,expect_reject=False):
        result['ctor_entered']+=1
        try:e=E.CombatEngine(fixture,provider,dto)
        except Exception:
            if expect_reject:result['ctor_rejected']+=1
            raise
        result['ctor_success']+=1;return e
    def prepare(e):result['prepare_calls']+=1;e.prepare_only()
    def activate(e):result['logical_activate_calls']+=1;e.activate_from_checkpoint()
    def step(e):result['step_attempts']+=1;return e.step()
    def readstate(e):return copy.deepcopy((e.snapshot(),e.frame_driver.snapshot(),e.random.position,e.random.audit,e.runtime_trace,e.pure_api_trace,e.pure_snapshots))
    try:
        for x in pins['files']:assert descriptor(ROOT/x['path'])==x,x['path']
        write(out/'before.json',pins);data=json.loads((SRC/'inputs.json').read_text());fixture=data['fixture'];runtime=data['runtime'];expected=data['expected']
        sys.pycache_prefix=str(out/'unused-bytecode-cache');sys.path.insert(0,str(STAGE))
        E=importlib.import_module('native_replay_v8.engine');R=importlib.import_module('native_replay_v8.randomness');FD=importlib.import_module('native_replay_v7.frame_driver')
        result['candidate_package_imports']=1
        loaded={name:descriptor(Path(mod.__file__).resolve()) for name,mod in sys.modules.items() if name.startswith(('native_replay_v7','native_replay_v8')) and getattr(mod,'__file__',None)}
        allowed={x['path'] for x in pins['candidate_files']};assert all(x['path'] in allowed for x in loaded.values());result['loaded_modules']=loaded
        for name in ['__init__','prepare_only','activate_from_checkpoint','activate','death','finish','step','run','result','snapshot','_source_noninterfering_callback','_timer_timeout','_start_timer','_stop_timer']:
            codes[getattr(E.CombatEngine,name).__code__]='CombatEngine.'+name
        codes[E.validate_runtime_inputs.__code__]='validate_runtime_inputs';sys.setprofile(profile)
        def mutate(label,operation,fragment,fixture_override=None):
            x=copy.deepcopy(runtime);operation(x);rejected(label,lambda:E.validate_runtime_inputs(x,fixture if fixture_override is None else fixture_override),fragment)
        mutate('01 missing diagnostic private value',lambda x:x['timer_initial']['aux:P:battleRageTimer'].pop('private_left_bits'),'pure timer fields')
        mutate('02 Character BOOL alias',lambda x:x['initial_characters']['P'].__setitem__('invulnerable',0),'character initial values')
        mutate('03 Timer mode BOOL alias',lambda x:x['timer_initial']['tick:P'].__setitem__('process_mode',False),'typed Timer state/config')
        mutate('04 duplicate native identity',lambda x:x['processing_nodes'][0].__setitem__('native_id',x['processing_nodes'][1]['native_id']),'native identity')
        def ghost(x):
            for role,name,pos in [('buff:P:Block','X',9),('buff:P:Lucky','Y',10)]:
                row=next(n for n in x['processing_nodes'] if n['role']==role);row.update(path='/root/Ghost/'+name,name=name,positions=[-1,pos,0])
                cfg=next(n for n in x['nodes'] if n['role']==role);cfg.update(path=row['path'],positions=row['positions'][:])
        mutate('05 reverse ancestor alias',ghost,'reverse sparse prefix conflict')
        mutate('06 old441 profile cannot admit new fixture',lambda x:x.__setitem__('profile_id',E.PURE441_PROFILE),'single King outside predeclared')
        mutate('07 unknown diagnostic initial field',lambda x:x['timer_initial']['invu:O'].__setitem__('verified',True),'pure timer fields')
        mutate('08 prepare/activation order mismatch',lambda x:x['activate_order'].__setitem__(slice(0,2),list(reversed(x['activate_order'][:2]))),'different prepare/activate order')
        badfixture=copy.deepcopy(fixture);badfixture['sides'][0]['items'][6]['item_index']=262
        mutate('09 fabricated King fixture',lambda x:None,'exact29 geometry',badfixture)
        rejected('10 None provider',lambda:ctor(fixture,None,runtime,True),'exact TapeRandom')
        rejected('11 object provider',lambda:ctor(fixture,object(),runtime,True),'exact TapeRandom')
        primary=ctor(fixture,R.TapeRandom(data['primary_tape']),runtime)
        checkpoint('constructed emptyKing exact32 records/31noops/Tape0',not primary.king_mode and primary.king_states=={} and primary.captured_clock_mode and len(primary._timer_snapshot())==32 and len(primary.captured_noop_slots)==31 and primary.random.position==0 and not primary.timer_runtime.started_timers)
        checkpoint('not legacyP6King',primary.items['P:6'].item_index==11 and primary.items['P:14'].item_index==199)
        checkpoint('tree order independent of reversed input rows',primary.ordinary_roles==[n['role'] for n in sorted(runtime['nodes'],key=lambda n:(n['priority'],tuple(n['positions']))) if n['kind']=='ordinary'])
        prepare(primary)
        checkpoint('prepare offclock/Tape0 Basic/cache/Sapphire',primary.random.position==0 and primary.frame_driver.pass_index==0 and primary.items['P:9'].iteration_cooldown==5.0 and primary.items['P:9'].goobert_activations==0 and [x.instance_id for x in primary.affected_items_cache['P:10']]==expected['squirrel_prepared_cache'] and primary.items['P:14'].definition['random_buff_types']==(101,102,103,104,106,107))
        rejected('12 foreign idle',lambda:primary._source_noninterfering_callback('item:FOREIGN',1,0.01),'unknown captured no-op')
        rejected('13 BOOL Game mode',lambda:primary._source_noninterfering_callback('game',True,0.01),'unknown captured no-op')
        timer=primary.runtime_roles['aux:P:battleRageTimer']
        rejected('14 inactive timeout',lambda:timer.timeout_handlers[0](timer),'inactive captured Timer timeout')
        activate(primary)
        checkpoint('activation consumed exact20 startup draws',primary.random.position==20 and primary.frame_driver.activated and primary.frame_driver.pass_index==0)
        callback_key=(primary.runtime_roles['game'],0);original_callback=primary.timer_runtime.ordinary_callbacks[callback_key];injection=[]
        def synthetic_after_real_game(node,delta):
            original_callback(node,delta)
            if not injection:
                before=copy.deepcopy(primary.histories.snapshot());position=primary.random.position
                primary.characters['O'].hp=0.0;primary.death(primary.characters['O']);primary.activate(primary.items['P:10'])
                injection.append(dict(kind='SYNTHETIC_AFTER_REAL_GAME_BOUNDARY',phase=primary.frame_driver.phase,physics=primary.frame_driver.physics_frame,tape_before=position,tape_after=primary.random.position,history_unchanged=same(before,primary.histories.snapshot())))
        primary.timer_runtime.ordinary_callbacks[callback_key]=synthetic_after_real_game
        for unused in range(7):step(primary)
        primary.timer_runtime.ordinary_callbacks[callback_key]=original_callback
        result['positive_result_calls']+=1;computed=primary.result()
        write(out/'primary-output.json',computed);write(out/'primary-injection.json',injection)
        primary.random.assert_consumed()
        checkpoint('primary computed barrier all7passes/noKing/dualterminal',primary.finalized and primary.frame_driver.finalized and primary.frame_driver.pass_index==7 and 'captured_terminal' in computed and 'king_terminal' not in computed and computed['captured_terminal']['post_cleanup']['passes_consumed']==3 and computed['captured_terminal']['final']['passes_consumed']==7 and computed['captured_terminal']['passes'][-1]['completed'] is False)
        checkpoint('ended Squirrel pitch preserved after real callback',len(injection)==1 and injection[0]['phase']=='ordinary_physics' and injection[0]['tape_before']==20 and injection[0]['tape_after']==21 and injection[0]['history_unchanged'])
        diag=computed['pure_combat_diagnostics'];beforeops=[x for x in diag['api'] if x['edge']=='before']
        stoproles=[x['role'] for x in beforeops if x['operation']=='stop' and x['role'] in E.CAPTURED_WHELP_INACTIVE]
        checkpoint('six inactive real API stops ordered',stoproles==expected['six_stop_order'] and all(x['argc']==0 and x['args']==[] for x in beforeops if x['operation']=='stop'))
        checkpoint('inactive never started or timed out',all(primary.runtime_roles[x] not in primary.timer_runtime.started_timers for x in E.CAPTURED_WHELP_INACTIVE) and not any(x.get('kind')=='timeout_enter' and x.get('role') in E.CAPTURED_WHELP_INACTIVE for x in primary.runtime_trace))
        starts=[x for x in beforeops if x['operation']=='start'];checkpoint('native argument Variants INT14/tickargc0',starts[0]['role']=='fatigue:start' and starts[0]['args']==[{'type':'int','decimal':'14'}] and [(x['role'],x['argc'],x['args']) for x in starts[1:]]==[('tick:P',0,[]),('tick:O',0,[])])
        cutoff_callbacks=[x for x in diag['callbacks'] if x['idle_frame']==204 and x['mode']==1]
        checkpoint('no finalidle callbacks; retained all32diagnostics',not cutoff_callbacks and len(diag['post_cleanup']['timers'])==32 and len(diag['final']['timers'])==32 and len(diag['final']['processing_nodes'])==67 and diag['post_cleanup']['king']=={} and diag['final']['king']=={})
        ut=10.0
        for x in runtime['frame_clock']['passes']:
            if x['kind']=='physics':ut+=struct.unpack('>d',bytes.fromhex(x['delta_bits']))[0]
        ct=10.0
        for x in runtime['frame_clock']['passes'][:6]:
            if x['kind']=='idle':ct+=struct.unpack('>d',bytes.fromhex(x['delta_bits']))[0]
        checkpoint('actual supplied Util clocks and counters',same(primary.frame_driver.util_time,ut) and same(primary.frame_driver.util_clock_time,ct) and primary.frame_driver.util_frame_counter==603)
        frozen=readstate(primary);result['positive_result_calls']+=1;again=primary.result();snapshot=primary.snapshot()
        checkpoint('readonly sameinstance snapshots/result',same(frozen,readstate(primary)) and same(computed,again) and same(snapshot,computed['final']))
        clock=primary.frame_driver.clock;last=clock.passes[-1];extra=replace(last,idle_frame=last.idle_frame+1)
        primary.frame_driver.clock=replace(clock,passes=clock.passes+(extra,))
        try:rejected('15 trailing clock through result',primary.result,'trailing frame records')
        finally:primary.frame_driver.clock=clock
        checkpoint('trailing rejection no advance',same(frozen,readstate(primary)))
        short=copy.deepcopy(runtime);short['frame_clock']['passes']=short['frame_clock']['passes'][:1]
        secondary=ctor(fixture,R.TapeRandom(data['eof_tape']),short);prepare(secondary);activate(secondary);step(secondary)
        rejected('16 premature EOF via engine.step',lambda:step(secondary),'EOF is not a rule-derived terminal barrier',FD.IncompleteFrameStream)
        write(out/'eof-partial.json',dict(snapshot=secondary.snapshot(),driver=secondary.frame_driver.snapshot(),tape=secondary.random.audit))
        checkpoint('EOF no phantom terminal or winner',not secondary.ended and not secondary.finalized and not secondary.frame_driver.finalized and secondary.winner is None and secondary.random.position==20)
        checkpoint('exact released operation bounds',result['negative_calls']==16 and result['ctor_entered']==4 and result['ctor_success']==2 and result['ctor_rejected']==2 and result['prepare_calls']==2 and result['logical_activate_calls']==2 and result['step_attempts']==9 and counts['CombatEngine.run']==0)
        result['draws_consumed']=primary.random.position+secondary.random.position;result['status']='PASS_SYNTHETIC_CAPTURED_CLOCK_INTERFACE_NOT_NATIVE'
    except BaseException as exc:
        result['status']='FIRST_ERROR_STOPPED';result['error']=dict(type=type(exc).__name__,message=str(exc),traceback=traceback.format_exc())
        if primary is not None:
            try:write(out/'primary-partial.json',dict(snapshot=primary.snapshot(),driver=primary.frame_driver.snapshot(),tape=primary.random.audit))
            except Exception as err:result['partial_save_error']=str(err)
    finally:
        sys.setprofile(None);result['engine_method_entries']=dict(sorted(counts.items()));result['wall_seconds']=time.monotonic()-started
        after=[descriptor(ROOT/x['path']) for x in pins['files']];result['source_input_after_unchanged']=after==pins['files']
        if not result['source_input_after_unchanged']:result['status']='SOURCE_DRIFT_STOPPED'
        write(out/'after.json',dict(files=after));write(out/'result.json',result)
        write(out/'owned-files.json',dict(schema='phase506-actual-owner/1',files=[descriptor(p) for p in sorted(out.iterdir()) if p.is_file()]))
    print(json.dumps({k:result.get(k) for k in ['status','negative_calls','ctor_entered','ctor_success','ctor_rejected','step_attempts','draws_consumed','wall_seconds']}))
    return 0 if result['status'].startswith('PASS_') else 1
if __name__=='__main__':raise SystemExit(main())
