"""Finite condition repair acceptance; no raw capture, battle, Expected or pool."""
import argparse
from collections import Counter
from copy import deepcopy
import hashlib
import importlib
import json
import math
import os
from pathlib import Path
import stat
import struct
import sys
import time
import traceback
import types
ROOT=Path('/workspace/python-original-engine/repo')
SOURCE=ROOT/'data/phase477-independent-harness-source'
STAGED=ROOT/'data/phase476-joint-condition-repair/staged'
OUTPUT=ROOT/'data/phase477-independent-interfaces-first-001'
DERIVED=ROOT/'data/phase476-derived-joint-input-first-001'
PREPARED={'P:6':['P:7','P:8','P:9','P:10','P:11'],'P:7':['P:6']}
FRESH={'P:6':['P:8','P:7','P:9','P:10','P:11'],'P:7':['P:6']}
LISTENERS={'P:6':['P:7'],'P:7':['P:6'],'P:8':['P:6'],'P:9':['P:6'],'P:10':['P:6'],'P:11':['P:6']}


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def path_of(value):
    p = Path(value)
    return p if p.is_absolute() else ROOT/p


def strict(raw):
    def pairs(rows):
        result = {}
        for k,v in rows:
            if k in result: raise ValueError('duplicate JSON key '+k)
            result[k] = v
        return result
    def invalid(x): raise ValueError('nonfinite JSON '+x)
    return json.loads(raw,object_pairs_hook=pairs,parse_constant=invalid)


def equal(a,b):
    assert json.dumps(a,sort_keys=True,separators=(',',':'),allow_nan=False) == json.dumps(b,sort_keys=True,separators=(',',':'),allow_nan=False)


def bits(value):
    assert type(value) is float and math.isfinite(value)
    return struct.pack('>d',value).hex()


def pin(path):
    raw = path.read_bytes()
    return {'path':str(path),'size':len(raw),'sha256':digest(raw)}


def checked(row):
    path = path_of(row['path']); before=path.lstat()
    assert stat.S_ISREG(before.st_mode) and before.st_nlink==1 and not any(p.is_symlink() for p in path.parents)
    fd = os.open(path,os.O_RDONLY|os.O_NOFOLLOW)
    identity = lambda x:(x.st_dev,x.st_ino,x.st_size,x.st_mode,x.st_mtime_ns,x.st_ctime_ns)
    try:
        assert identity(os.fstat(fd))==identity(before)
        chunks=[]
        while True:
            b=os.read(fd,65536)
            if not b:break
            chunks.append(b)
        assert identity(os.fstat(fd))==identity(before)
    finally:os.close(fd)
    assert identity(path.lstat())==identity(before)
    raw=b''.join(chunks)
    assert len(raw)==row['size'] and digest(raw)==row['sha256'],str(path)
    return raw


def write_new(path,value):
    raw=(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode()
    with path.open('xb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
    return {'path':str(path),'size':len(raw),'sha256':digest(raw)}


def load_module(name,path,expected):
    raw=path.read_bytes();assert digest(raw)==expected
    module=types.ModuleType(name);module.__file__=str(path);sys.modules[name]=module
    exec(compile(raw,str(path),'exec'),module.__dict__)
    return module


def validate_stage(engine,receipt,prepared):
    phase='pre_activate' if prepared else 'pre_prepare'
    assert engine.prepared is prepared and engine.activated is False
    assert engine.random.position==0 and engine.random.audit==[] and engine.frame_driver.pass_index==0
    current={key:[x.instance_id for x in values] for key,values in engine.affected_items_cache.items()}
    observations=receipt['prepare_observations'][phase]
    for role,obs in observations.items():
        actual_current={int(e['key']['decimal']):[v['key']['role'] for v in e['value']['entries']] for e in obs['currentAffectedItems']['entries']}
        assert set(actual_current)=={0,2,4,7} and all(not actual_current[k] for k in (2,4,7))
        assert actual_current[0]==PREPARED.get(role,[])
        if role in current:equal(current[role],actual_current[0])
        else:assert not actual_current[0]
        assert engine.items[role].cache_prepared is prepared
        if prepared:
            cache={int(e['key']['decimal']):[v['role'] for v in e['value']['values']] for e in obs['cachedAffectedItems']['entries']}
            equal(cache,actual_current)
        else:assert obs['cachedAffectedItems']=={'type':'dictionary','entries':[]}
    for role in ('P:6','P:7'):
        item=engine.items[role];fields=observations[role]['goobert_state']
        assert type(item.goobert_activations) is int and item.goobert_activations==int(fields['activations']['decimal'])
        assert type(item.definition['activations_to_trigger']) is int
        assert bits(float(item.definition['activations_to_trigger']))==fields['activationsToTrigger']['binary64_be']
        assert bits(item.iteration_cooldown)==fields['iterationCooldown']['binary64_be'] and bits(item.trigger_time)==fields['triggerTime']['binary64_be']
    assert type(engine.king_states['P:6']['invuCharges']) is int and engine.king_states['P:6']['invuCharges']==int(observations['P:6']['goobert_state']['invuCharges']['decimal'])
    for side in ('P','O'):
        assert engine.characters[side].invulnerable is False and engine.invu_origins[side] is None
        assert type(engine.characters[side].buff_protect_stacks) is int and engine.characters[side].buff_protect_stacks==0
    timers={role:node for role,node in engine.runtime_roles.items() if role in engine.runtime_inputs.data['timer_initial']}
    assert len(timers)==33
    for role,node in timers.items():
        initial=engine.runtime_inputs.data['timer_initial'][role]
        assert bits(node.private_left)==initial['private_left_bits'] and node.processing is False and node.paused is False
        assert type(node.process_mode) is int and node.process_mode==0 and bits(node.wait_time)==initial['wait_time_bits']
    if prepared:
        equal(engine.activation_listeners,LISTENERS)
        history=engine.histories.loggers[0]['itemStateHistories']['P:6']
        assert history.values==[0] and type(history.values[0]) is int
    return {'stage':phase,'current_caches':current,'native_prepared_primary':deepcopy(PREPARED),'listener_mapping':deepcopy(engine.activation_listeners),
            'Timer_count':33,'Tape_position':engine.random.position,'Tape_audit_length':len(engine.random.audit),'passes_consumed':engine.frame_driver.pass_index,
            'King':deepcopy(engine.king_states['P:6']),'Basic':deepcopy(observations['P:7']['goobert_state'])}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--pins-sha256',required=True);args=parser.parse_args()
    assert not OUTPUT.exists() and not DERIVED.exists();OUTPUT.mkdir(mode=0o700)
    start=time.monotonic();stage='preflight';engine=tape=None;calls=Counter();cases=[];io=Counter();forbidden=[];artifacts=[]
    result={'schema':'phase477-independent-interface-result/1','status':'RUNNING','cases':cases,'full_run':0,'step':0,
            'Expected_business_decode':0,'Oracle':0,'pool_operations':0,'raw_capture_INPUT_reads':0,'B2_raw_reextract':0}
    try:
        pins_raw=(SOURCE/'pins.json').read_bytes();assert digest(pins_raw)==args.pins_sha256
        config=strict(pins_raw);pins=config['files'];before=[]
        for row in pins:
            raw=checked(row);before.append({'path':str(path_of(row['path'])),'size':len(raw),'sha256':digest(raw)})
        self_pin=pin(Path(__file__).absolute());assert self_pin['sha256']==config['harness_sha256'];before.append(self_pin)
        allowed={p['path'] for p in before}|{str(SOURCE/'pins.json')};stdlib=Path(os.__file__).parent
        def audit(event,values):
            if event.startswith(('subprocess.','socket.')) or event in ('os.system','os.exec','os.spawn','os.fork','os.posix_spawn'):
                forbidden.append(event);raise RuntimeError('FORBIDDEN_OPERATION '+event)
            if event!='open' or isinstance(values[0],int):return
            path=Path(os.fsdecode(values[0])).absolute();flags=values[2] or 0
            writing=bool(flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND))
            own=path.is_relative_to(OUTPUT) or path.is_relative_to(DERIVED)
            if writing:
                if not own:forbidden.append(str(path));raise RuntimeError('FORBIDDEN_WRITE '+str(path))
            elif str(path) in allowed:io[str(path)]+=1
            elif not (own or path.is_relative_to(stdlib)):
                forbidden.append(str(path));raise RuntimeError('FORBIDDEN_READ '+str(path))
        sys.dont_write_bytecode=True;sys.pycache_prefix=str(OUTPUT/'unused-bytecode-cache');sys.addaudithook(audit)
        by_path={p['path']:p for p in pins}
        def read(relative):return strict(checked(by_path[relative]))
        def instrument(obj,name,label,deny=False):
            original=getattr(obj,name)
            def wrapped(*v,**kw):
                calls[label]+=1
                if deny:raise AssertionError('FORBIDDEN_MODEL_ENTRY '+label)
                return original(*v,**kw)
            setattr(obj,name,wrapped)
        def negative(name,fn):
            try:fn()
            except ValueError as error:cases.append({'name':name,'status':'PASS_REJECTED','reason':str(error)})
            else:raise AssertionError('ACCEPTED_NEGATIVE '+name)
        stage='derivation-controls'
        d=load_module('phase477_deriver_target',ROOT/config['deriver_path'],config['deriver_sha256'])
        instrument(d,'derive_from_bytes','deriver.derive_from_bytes');instrument(d,'build_from_files','deriver.build_from_files')
        instrument(d,'read_pinned','deriver.read_pinned')
        old_raw=checked(by_path['data/phase470-joint-input-first-001/input-bundle.json'])
        fact_raw=checked(by_path['data/phase475-cooldown-branch-input-evidence/receipt.json'])
        negative('01 changed old bundle byte identity',lambda:d.derive_from_bytes(old_raw+b' ',fact_raw))
        negative('02 changed fact byte identity',lambda:d.derive_from_bytes(old_raw,fact_raw+b' '))
        negative('03 missing fact identity',lambda:d.derive_from_bytes(old_raw,b''))
        stage='unique-actual-derivation'
        d.build_from_files(DERIVED)
        new_path=DERIVED/config['derived_bundle_filename'];new_raw=new_path.read_bytes();bundle=strict(new_raw);old_bundle=strict(old_raw)
        assert old_raw.count(b'"below_master": false')==1
        assert new_raw==old_raw.replace(b'"below_master": false',b'"below_master": true',1)
        wanted=deepcopy(old_bundle);assert wanted['fixture']['below_master'] is False;wanted['fixture']['below_master']=True
        equal(bundle,wanted);assert bundle['fixture']['below_master'] is True and len(bundle['draws'])==422
        assert calls['deriver.derive_from_bytes']==4 and calls['deriver.build_from_files']==1
        receipt=read('data/phase470-joint-input-first-001/initial-receipt.json')
        binding=read('data/phase474-root-external-identities/comparison-binding.json')
        binding['input_bundle']=dict(pin(new_path),path=str(new_path.relative_to(ROOT)))
        binding['input_canonical_sha256']=digest(json.dumps(bundle,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
        binding['candidate_freeze']=config['candidate_freeze']
        artifacts.append(write_new(OUTPUT/'actual-comparison-binding.json',binding))
        cases.append({'name':'04 one actual fixed input derivation','status':'PASS','new_bundle':binding['input_bundle'],
                      'changed_field':'/fixture/below_master','old_initial_receipt':by_path['data/phase470-joint-input-first-001/initial-receipt.json']})
        stage='imports'
        assert not any(n.startswith(('native_replay_v8','native_replay_v7','original_rng','godot_pcg_integer')) for n in sys.modules)
        sys.path.insert(0,str(STAGED));e=importlib.import_module('native_replay_v8.engine');randomness=sys.modules['native_replay_v8.randomness']
        a=load_module('phase477_adapter_target',ROOT/config['adapter_path'],config['adapter_sha256'])
        launcher=load_module('phase477_launcher_target',ROOT/config['launcher_path'],config['launcher_sha256'])
        imported={}
        for name,module in list(sys.modules.items()):
            if name.startswith(('native_replay_v8','native_replay_v7')) or name in ('original_rng','godot_pcg_integer'):
                path=Path(module.__file__).absolute();assert path.is_relative_to(STAGED) and str(path) in allowed;imported[name]=str(path)
        assert Path(e.__file__)==STAGED/'native_replay_v8/engine.py'
        result.update(loaded_modules=imported,adapter_path=a.__file__,launcher_path=launcher.__file__,deriver_path=d.__file__)
        for name in ('validate_runtime_inputs','_validate_joint_captured_runtime','build_runtime_scaffold'):
            instrument(e,name,'engine.'+name)
        for name in ('__init__','prepare_only','activate_from_checkpoint','_validate_joint_captured_state','_pure_business_snapshot','_fresh_goobert_targets','king_prepare','king_set_state'):
            instrument(e.CombatEngine,name,'CombatEngine.'+name)
        for name in ('run','step','result'):instrument(e.CombatEngine,name,'CombatEngine.'+name,True)
        instrument(e.EngineFrameDriver,'activate','EngineFrameDriver.activate');instrument(e.EngineFrameDriver,'step','EngineFrameDriver.step',True)
        instrument(randomness.TapeRandom,'__init__','TapeRandom.__init__');instrument(randomness.TapeRandom,'_take','TapeRandom._take')
        for name in ('bindings','_basic_fields','project_model_callbacks','_subject'):instrument(a,name,'adapter.'+name)
        instrument(launcher,'validate_request','launcher.validate_request');instrument(launcher,'read_descriptor','launcher.read_descriptor')
        runtime,fixture=bundle['runtime'],bundle['fixture']
        negative('05 old false fixture rejected by repaired gate',lambda:e.validate_runtime_inputs(runtime,old_bundle['fixture']))
        stage='one-actual-instance'
        tape=randomness.TapeRandom(bundle['draws']);engine=e.CombatEngine(fixture,tape,runtime)
        stages=[validate_stage(engine,receipt,False)]
        fresh={identity:[x.instance_id for x in engine._fresh_goobert_targets(engine.items[identity])] for identity in ('P:6','P:7')};equal(fresh,FRESH)
        engine.prepare_only();stages.append(validate_stage(engine,receipt,True))
        biases={}
        for side in ('P','O'):
            char=engine.characters[side];want=-0.2 if side=='P' else 0.2
            biases[side]={}
            for name in ('accuracy','critical'):
                rng=getattr(char,name);assert bits(rng.expected_wins)==bits(want) and type(rng.wins) is int and rng.wins==0 and rng.last_result is False
                biases[side][name]={'expected_wins_bits':bits(rng.expected_wins),'wins':rng.wins,'last_result':rng.last_result}
        prepared_snapshot=deepcopy(engine.pure_snapshots[-1]);engine.activate_from_checkpoint()
        assert engine.prepared and engine.activated and not engine.ended and not engine.finalized
        assert engine.frame_driver.pass_index==0 and engine.frame==0 and engine.elapsed==0.0
        assert tape.position==10 and tape.audit==bundle['draws'][:10]
        assert [x['label'] for x in tape.audit]==['cooldown:'+x for x in ['P:10','P:8','P:12','P:9','P:13','P:11','O:11','O:6','O:10','O:7']]
        for x in tape.audit:assert x['args']==['3fef333333333333' if x['label'].startswith('cooldown:O:') else '3fee666666666666','3ff0cccccccccccd']
        assert [x['stage'] for x in engine.pure_snapshots]==['constructed_off_clock','prepare_off_clock','pre_activate']
        for snap in engine.pure_snapshots[:2]:assert snap['clock'] is None and snap['off_clock'] is True and snap['tape_position']==0 and snap['tape_audit_length']==0
        before_api=[x for x in engine.pure_api_trace if x['edge']=='before']
        assert [(x['role'],x['operation'],x['argc'],x['args']) for x in before_api]==[
            ('fatigue:start','stop',0,[]),('fatigue:tick','stop',0,[]),('fatigue:start','start',1,[{'type':'int','decimal':'14'}]),('tick:P','start',0,[]),('tick:O','start',0,[])]
        assert len(engine.pure_api_trace)==10
        for row in engine.pure_api_trace:
            if row['edge']=='after':assert row['native_return_semantics']=={'typed':{'type':'null'},'basis':'SOURCE_VOID_NOT_SAMPLED'}
        assert calls['CombatEngine.__init__']==1 and calls['CombatEngine.prepare_only']==1 and calls['CombatEngine.activate_from_checkpoint']==2
        assert calls['CombatEngine.run']==calls['CombatEngine.step']==calls['CombatEngine.result']==calls['EngineFrameDriver.step']==0
        cases.append({'name':'06 one real construct/prepare/activate with shared biases and ten startup draws','status':'PASS'})
        artifacts.append(write_new(OUTPUT/'same-instance-stage-correspondence.json',{'status':'PASS','stages':stages,'fresh_targets':fresh,'prepared_biases':biases,
            'prepared_snapshot':prepared_snapshot,'activation_Tape_position':tape.position,'activation_Tape_audit':tape.audit,'startup_API':engine.pure_api_trace,'initial_snapshots':engine.pure_snapshots}))
        stage='adapter-controls'
        bound=a.bindings(bundle,binding)
        synthetic={'instance':'P:7','fields':{'activations':0,'activationsToTrigger':5.0,'iterationCooldown':5.0,'triggerTime':5.0}}
        a._basic_fields(synthetic,bound);cases.append({'name':'07 actual binding and synthetic Basic typed positive','status':'PASS'})
        bad=deepcopy(binding);bad['input_canonical_sha256']='0'*64
        negative('08 wrong canonical input',lambda:a.bindings(bundle,bad))
        b=deepcopy(bundle);b['runtime']['profile_id']='pure-combat-fixed-king-A-input441/1';bad=deepcopy(binding);bad['input_canonical_sha256']=digest(json.dumps(b,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
        negative('09 old profile with synthetic digest',lambda:a.bindings(b,bad))
        item=deepcopy(synthetic);del item['fields']['activationsToTrigger']
        negative('10 missing Basic REAL',lambda:a._basic_fields(item,bound))
        item=deepcopy(synthetic);item['fields']['activations']=False
        negative('11 BOOL Basic INT',lambda:a._basic_fields(item,bound))
        item=deepcopy(synthetic);item['fields']['activationsToTrigger']=5
        negative('12 INT Basic REAL',lambda:a._basic_fields(item,bound))
        item=deepcopy(synthetic);item['fields']['triggerTime']=float('nan')
        negative('13 nonfinite Basic REAL',lambda:a._basic_fields(item,bound))
        fake={'pure_combat_diagnostics':{'callbacks':[{'kind':'source_callback','role':'item:P:foreign','mode':1}]}}
        negative('14 foreign noop identity',lambda:a.project_model_callbacks(fake,bound))
        node=bound['nodes']['tick:P'];row={'subject':{'type':'native_ref','native_id':node['native_id'],'role':'tick:P','class':'Node2D'}}
        negative('15 retained native subject class',lambda:a._subject(row,bound))
        stage='launcher-control'
        closed=read('data/phase474-joint-output-source/launcher-request-contract.json')['closed_keys'];request={k:None for k in closed}
        request.update(schema='phase474-root-joint-model-request/1',case_id='NATIVE-028-KING-BASIC-A',root_model_authorized=False)
        negative('16 false launcher authority',lambda:launcher.validate_request(request))
        assert calls['launcher.read_descriptor']==0 and len(cases)==16
        stage='postflight';after=[pin(Path(p['path'])) for p in before];equal(before,after);assert not forbidden
        result.update(status='ACCEPTED_REPAIRED_JOINT_INPUT_AND_INTERFACES_NOT_FULL_RUN',source_before=before,source_after=after,
            input_binding=binding,successful_constructors=1,prepare_calls=1,logical_activate_calls=1,actual_activate_method_entries=2,
            passes_consumed=0,activation_Tape_position=tape.position,activation_Tape_audit=tape.audit,complete_model_run=False,
            complete_native_comparison=False,B2_reused=by_path['data/phase475-independent-interfaces-first-001/b2-applicability.json'],io=dict(io))
    except BaseException as error:
        result.update(status='FAILED_FIRST_ATTEMPT',stage=stage,error=type(error).__name__,reason=str(error),traceback=traceback.format_exc(),io=dict(io),forbidden_io=forbidden)
        if engine is not None:
            artifacts.append(write_new(OUTPUT/'same-instance-partial.json',{'prepared':engine.prepared,'activated':engine.activated,'ended':engine.ended,
                'frame':engine.frame,'elapsed':engine.elapsed,'passes_consumed':engine.frame_driver.pass_index,'events':engine.events,
                'listeners':engine.activation_listeners,'pure_snapshots':engine.pure_snapshots,'api':engine.pure_api_trace,'runtime_trace':engine.runtime_trace}))
        if tape is not None:result['Tape_partial']={'position':tape.position,'audit':tape.audit,'records':len(tape.records)}
    result['calls']=dict(calls);result['wall_seconds']=time.monotonic()-start
    artifacts.append(write_new(OUTPUT/'result.json',result));write_new(OUTPUT/'owned-files.json',{'schema':'phase477-independent-interface-owner/1','status':result['status'],'files':artifacts})
    print(json.dumps({'status':result['status'],'stage':result.get('stage'),'cases':len(cases),'wall_seconds':result['wall_seconds'],'calls':dict(calls)}))
    return 0 if result['status']=='ACCEPTED_REPAIRED_JOINT_INPUT_AND_INTERFACES_NOT_FULL_RUN' else 1


if __name__=='__main__':raise SystemExit(main())
