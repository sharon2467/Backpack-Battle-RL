"""Root-released finite471/474 interfaces and one lawful B2 UI read; no battle."""
import argparse
from collections import Counter
from copy import deepcopy
import dataclasses
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

ROOT = Path('/workspace/python-original-engine/repo')
SOURCE = ROOT/'data/phase475-independent-harness-source'
STAGED = ROOT/'data/phase471-captured-joint-source/staged'
OUTPUT = ROOT/'data/phase475-independent-interfaces-first-001'
PREPARED = {'P:6':['P:7','P:8','P:9','P:10','P:11'],'P:7':['P:6']}
FRESH = {'P:6':['P:8','P:7','P:9','P:10','P:11'],'P:7':['P:6']}
LISTENERS = {'P:6':['P:7'],'P:7':['P:6'],'P:8':['P:6'],'P:9':['P:6'],'P:10':['P:6'],'P:11':['P:6']}
UI_SITES = ['Items/Item.gd::respondToHover','Items/Item.gd::respondToHoverEnd','Items/Item.gd::_process:dragged','Items/Item.gd::_process:rigid','Items/Item.gd::activateDragParticles','Items/Item.gd::deactivateDragParticles','Items/Item.gd::onAddedToGridStorage','Items/Item.gd::deactivateParticles','Utility/AutoHideParticles.gd::activate','Utility/AutoHideParticles.gd::deactivate','Utility/AutoHideParticles.gd::startTimer','Utility/AutoHideParticles.gd::instantClear']


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


def b2_extract(raw,bundle,pin_value):
    assert raw.endswith(b'\n') and len(raw)<=8388608
    lines=raw.splitlines();assert 1<=len(lines)<=65536
    rows=[]
    for index,line in enumerate(lines):
        assert line and len(line)<=16384
        row=strict(line)
        assert set(row)=={'schema','sequence','kind','site','physics_frame','idle_frame','in_physics','payload'}
        assert row['schema']=='phase355-king-ui-authority/1' and type(row['sequence']) is int and row['sequence']==index
        assert type(row['physics_frame']) is int and type(row['idle_frame']) is int and type(row['in_physics']) is bool
        assert row['physics_frame']>=0 and row['idle_frame']>=0 and type(row['payload']) is dict
        if rows:assert row['physics_frame']>=rows[-1]['physics_frame'] and row['idle_frame']>=rows[-1]['idle_frame']
        rows.append(row)
    def one(kind):
        found=[r for r in rows if r['kind']==kind];assert len(found)==1;return found[0]
    opened,roles,closed=one('open'),one('roles'),one('close')
    assert opened is rows[0] and closed is rows[-1] and opened['sequence']<roles['sequence']<closed['sequence']
    o,c,r=opened['payload'],closed['payload'],roles['payload']
    assert o['case']=='KING-BASIC-A-460' and o['window']=='before_selected_birth_to_final_preinternal'
    equal(o['sites'],UI_SITES);equal(c['sites'],UI_SITES)
    assert o['drop_mouse_setting'] is True and c['completed'] is True and c['failed'] is False and c['overflow'] is False
    assert type(c['dropped']) is int and c['dropped']==0 and c['phase']=='idle_pre_internal_flush'
    assert c['king_clock_closed'] is True and type(c['active_buff_calls']) is int and c['active_buff_calls']==0
    assert type(c['rows_before_close']) is int and c['rows_before_close']==len(rows)-1
    nodes={n['role']:n for n in bundle['runtime']['processing_nodes']}
    root_id=nodes['root_viewport']['native_id']
    for controls in (o['after'],c['controls']):
        assert controls['root_id']==root_id and controls['disable_input'] is True and controls['physics_object_picking'] is False
    assert o['before']['root_id']==root_id and r['using_controller'] is False
    expected={i['instance_id']:nodes['item:'+i['instance_id']]['native_id'] for side in bundle['fixture']['sides'] for i in side['items']}
    guards=r['selected_guards'];assert type(guards) is list and len(guards)==26 and len({g['role'] for g in guards})==26
    assert {g['role']:g['item_id'] for g in guards}==expected
    for g in guards:
        assert all(g[k] is False for k in ('focus','hovered','dragged'))
        assert type(g['mode']) is int and g['mode']==1 and g['viewport_id']==root_id
    equal(r['kings'],[{'item_id':expected['P:6'],'role':'P:6'}])
    stack=[];entries=[];by_site=Counter();critical=[];selected_item=[]
    for row in rows:
        if row['kind']=='entry':
            p=row['payload'];assert row['site'] in UI_SITES and type(p['token']) is int and p['token']==row['sequence']
            assert type(p['receiver_id']) is str
            stack.append((p['token'],row['site'],p['receiver_id']));entries.append(row);by_site[row['site']]+=1
            if row['site'] in UI_SITES[:4]:critical.append({'sequence':row['sequence'],'site':row['site'],'receiver_id':p['receiver_id']})
            if row['site'].startswith('Items/Item.gd::') and p['receiver_id'] in expected.values():selected_item.append({'sequence':row['sequence'],'site':row['site'],'receiver_id':p['receiver_id']})
        elif row['kind']=='exit':
            p=row['payload'];assert stack and stack.pop()==(p['token'],row['site'],p['receiver_id'])
    assert not stack and type(c['entries']) is int and c['entries']==len(entries)
    assert not critical,('RELEVANT_HOVER_DRAG_RIGID_ENTRY',critical)
    assert not selected_item,('SELECTED_ITEM_UI_ENTRY_REQUIRES_SOURCE_CLASSIFICATION',selected_item)
    return {'schema':'phase475-actual-joint-B2-applicability/1','status':'ACCEPTED_FIXED26_CONDITIONAL_TAPE_SHARED_CALLBACK_DOMAIN',
            'raw_descriptor':pin_value,'raw_UI_reads':1,'other_original_INPUT_reads':0,'rows':len(rows),'role_bind_sequence':roles['sequence'],
            'selected_guards':guards,'open':o,'close':c,'entries_by_site':dict(by_site),'relevant_critical_entries':critical,
            'selected_item_entries':selected_item,'native_roles_verified':26,'model_noop_slots':28,
            'argument':'Joined accepted444 branch-first Game/Item hooks and read-only residual callees with462/463 preserved hooks and this exact complete window. Per-clock/write ui_check_controls plus bounded original input-writer closure; initialfalse alone is not proof. Basic scene binds Goobert whose canAffect→Item.canActivate is already read-only.',
            'limits':['Conditional selected primitive Tape/business semantics only; no global/same-seed RNG or GUI equivalence.','No full-FX admission helper or107methods equality claim. Footer is coverage evidence only.','Ordinary G02 writer/dispatch, historical Source redaction and reconstructed-analysis limitations retained.']}


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
    assert not OUTPUT.exists();OUTPUT.mkdir(mode=0o700)
    start=time.monotonic();stage='preflight';engine=tape=None;calls=Counter();cases=[];io=Counter();forbidden=[];artifacts=[]
    result={'schema':'phase475-independent-interface-result/1','status':'RUNNING','cases':cases,'full_run':0,'step':0,'Expected_business_decode':0,'Oracle':0,'pool_operations':0}
    try:
        pins_raw=(SOURCE/'pins.json').read_bytes();assert digest(pins_raw)==args.pins_sha256
        config=strict(pins_raw);pins=config['files'];before=[]
        for row in pins:
            raw=checked(row);before.append({'path':str(path_of(row['path'])),'size':len(raw),'sha256':digest(raw)})
        self_pin=pin(Path(__file__).absolute());assert self_pin['sha256']==config['harness_sha256'];before.append(self_pin)
        allowed={p['path'] for p in before}|{str(SOURCE/'pins.json')};ui_path=config['UI']['path']
        stdlib=Path(os.__file__).parent
        def audit(event,values):
            if event.startswith(('subprocess.','socket.')) or event in ('os.system','os.exec','os.spawn','os.fork','os.posix_spawn'):
                forbidden.append(event);raise RuntimeError('FORBIDDEN_OPERATION '+event)
            if event!='open' or isinstance(values[0],int):return
            path=Path(os.fsdecode(values[0])).absolute();flags=values[2] or 0
            writing=bool(flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND))
            if writing:
                if not path.is_relative_to(OUTPUT):forbidden.append(str(path));raise RuntimeError('FORBIDDEN_WRITE '+str(path))
            elif str(path)==ui_path:io['original_UI_opens']+=1
            elif str(path) in allowed:io[str(path)]+=1
            elif not (path.is_relative_to(OUTPUT) or path.is_relative_to(stdlib)):
                forbidden.append(str(path));raise RuntimeError('FORBIDDEN_READ '+str(path))
        sys.dont_write_bytecode=True;sys.pycache_prefix=str(OUTPUT/'unused-bytecode-cache');sys.addaudithook(audit)
        by_path={p['path']:p for p in pins}
        def read(relative):return strict(checked(by_path[relative]))
        bundle=read('data/phase470-joint-input-first-001/input-bundle.json')
        receipt=read('data/phase470-joint-input-first-001/initial-receipt.json')
        binding=read('data/phase474-root-external-identities/comparison-binding.json')
        stage='B2-one-UI-read'
        b2=b2_extract(checked(config['UI']),bundle,config['UI'])
        artifacts.append(write_new(OUTPUT/'b2-applicability.json',b2))
        stage='imports'
        assert not any(n.startswith(('native_replay_v8','native_replay_v7','original_rng','godot_pcg_integer')) for n in sys.modules)
        sys.path.insert(0,str(STAGED))
        e=importlib.import_module('native_replay_v8.engine');randomness=sys.modules['native_replay_v8.randomness']
        a=load_module('phase475_adapter_target',ROOT/'tests/phase474_joint_business_output.py',config['adapter_sha256'])
        launcher=load_module('phase475_launcher_target',ROOT/'tests/phase474_joint_tape_run.py',config['launcher_sha256'])
        imported={}
        for name,module in list(sys.modules.items()):
            if name.startswith(('native_replay_v8','native_replay_v7')) or name in ('original_rng','godot_pcg_integer'):
                path=Path(module.__file__).absolute();assert path.is_relative_to(STAGED) and str(path) in allowed;imported[name]=str(path)
        assert Path(e.__file__)==STAGED/'native_replay_v8/engine.py' and Path(a.__file__)==ROOT/'tests/phase474_joint_business_output.py'
        result['loaded_modules']=imported;result['adapter_path']=a.__file__;result['launcher_path']=launcher.__file__
        def instrument(obj,name,label,deny=False):
            original=getattr(obj,name)
            def wrapped(*v,**kw):
                calls[label]+=1
                if deny:raise AssertionError('FORBIDDEN_MODEL_ENTRY '+label)
                return original(*v,**kw)
            setattr(obj,name,wrapped)
        for name in ('validate_runtime_inputs','_validate_joint_captured_runtime','build_runtime_scaffold'):
            instrument(e,name,'engine.'+name)
        for name in ('__init__','prepare_only','activate_from_checkpoint','_validate_joint_captured_state','_pure_business_snapshot','_fresh_goobert_targets','king_prepare','king_set_state'):
            instrument(e.CombatEngine,name,'CombatEngine.'+name)
        for name in ('run','step','result'):
            instrument(e.CombatEngine,name,'CombatEngine.'+name,True)
        instrument(e.EngineFrameDriver,'activate','EngineFrameDriver.activate')
        instrument(e.EngineFrameDriver,'step','EngineFrameDriver.step',True)
        instrument(randomness.TapeRandom,'__init__','TapeRandom.__init__')
        instrument(randomness.TapeRandom,'_take','TapeRandom._take')
        for name in ('bindings','_basic_fields','project_model_callbacks','_subject'):
            instrument(a,name,'adapter.'+name)
        instrument(launcher,'validate_request','launcher.validate_request')
        instrument(launcher,'read_descriptor','launcher.read_descriptor')
        def positive(name,fn):
            value=fn();cases.append({'name':name,'status':'PASS'});return value
        def negative(name,fn):
            try:fn()
            except ValueError as error:cases.append({'name':name,'status':'PASS_REJECTED','reason':str(error)})
            else:raise AssertionError('ACCEPTED_NEGATIVE '+name)
        stage='runtime-controls'
        runtime,fixture=bundle['runtime'],bundle['fixture']
        dto=positive('01 exact captured RuntimeDTO',lambda:e.validate_runtime_inputs(runtime,fixture))
        equal(dto.data,runtime);assert dto.prepare_order==tuple(runtime['prepare_order'])
        d=deepcopy(runtime);d['profile_id']='pure-combat-fixed-king-A-input441/1'
        negative('02 old profile',lambda:e.validate_runtime_inputs(d,fixture))
        f=deepcopy(fixture);f['sides'][0]['items'][0]['x']+=1
        negative('03 altered fixture',lambda:e.validate_runtime_inputs(runtime,f))
        d=deepcopy(runtime);d['timer_initial']['tick:P']['process_mode']=False
        negative('04 BOOL mode',lambda:e.validate_runtime_inputs(d,fixture))
        d=deepcopy(runtime);d['processing_nodes'][1]['native_id']=d['processing_nodes'][0]['native_id']
        negative('05 duplicate nativeID',lambda:e.validate_runtime_inputs(d,fixture))
        d=deepcopy(runtime);d['processing_nodes'].pop()
        negative('06 missing node',lambda:e.validate_runtime_inputs(d,fixture))
        d=deepcopy(runtime)
        for collection in ('processing_nodes','nodes'):
            row=next(x for x in d[collection] if x['role']=='invu:P');row['positions'][-1]=99
        negative('07 actual P7 topology',lambda:e.validate_runtime_inputs(d,fixture))
        wrong=e.RuntimeDTO(deepcopy(runtime),tuple(reversed(runtime['prepare_order'])),dto.util_time)
        negative('08 DTO convenience drift',lambda:e.validate_runtime_inputs(wrong,fixture))
        negative('09 None provider',lambda:e.CombatEngine(fixture,None,runtime))
        class SubTape(randomness.TapeRandom):pass
        rejected=SubTape(bundle['draws'])
        negative('10 subclass provider',lambda:e.CombatEngine(fixture,rejected,runtime))
        assert rejected.position==0 and rejected.audit==[] and calls['engine.build_runtime_scaffold']==0
        stage='one-actual-instance'
        tape=randomness.TapeRandom(bundle['draws'])
        engine=e.CombatEngine(fixture,tape,runtime)
        stages=[validate_stage(engine,receipt,False)]
        fresh={identity:[x.instance_id for x in engine._fresh_goobert_targets(engine.items[identity])] for identity in ('P:6','P:7')}
        equal(fresh,FRESH)
        engine.prepare_only();stages.append(validate_stage(engine,receipt,True))
        prepared_snapshot=deepcopy(engine.pure_snapshots[-1])
        engine.activate_from_checkpoint()
        assert engine.prepared is True and engine.activated is True and engine.ended is False and engine.finalized is False
        assert engine.frame_driver.pass_index==0 and engine.frame==0 and engine.elapsed==0.0
        assert tape.position>0 and tape.position<len(tape.records) and tape.audit==bundle['draws'][:tape.position]
        assert [x['stage'] for x in engine.pure_snapshots]==['constructed_off_clock','prepare_off_clock','pre_activate']
        for snap in engine.pure_snapshots[:2]:assert snap['clock'] is None and snap['off_clock'] is True and snap['tape_position']==0 and snap['tape_audit_length']==0
        before_api=[x for x in engine.pure_api_trace if x['edge']=='before']
        assert [(x['role'],x['operation'],x['argc'],x['args']) for x in before_api]==[
            ('fatigue:start','stop',0,[]),('fatigue:tick','stop',0,[]),('fatigue:start','start',1,[{'type':'int','decimal':'14'}]),('tick:P','start',0,[]),('tick:O','start',0,[])]
        assert len(engine.pure_api_trace)==10
        for row in engine.pure_api_trace:
            if row['edge']=='after':assert row['native_return_semantics']=={'typed':{'type':'null'},'basis':'SOURCE_VOID_NOT_SAMPLED'}
        assert calls['CombatEngine.__init__']==3 and calls['CombatEngine.prepare_only']==1 and calls['CombatEngine.activate_from_checkpoint']==2
        assert calls['CombatEngine.run']==calls['CombatEngine.step']==calls['CombatEngine.result']==calls['EngineFrameDriver.step']==0
        cases.append({'name':'11 one real construct/prepare/activate','status':'PASS'})
        artifacts.append(write_new(OUTPUT/'b1-stage-correspondence.json',{'schema':'phase475-B1-stage-correspondence/1','status':'PASS','stages':stages,'fresh_targets':fresh,'prepared_snapshot':prepared_snapshot,'logical_activation_calls':1,'actual_activation_method_entries':2,'passes_consumed':0,'activation_Tape_position':tape.position,'activation_Tape_audit':tape.audit,'startup_API':engine.pure_api_trace,'initial_snapshots':engine.pure_snapshots}))
        stage='adapter-controls'
        bound=a.bindings(bundle,binding)
        synthetic={'instance':'P:7','fields':{'activations':0,'activationsToTrigger':5.0,'iterationCooldown':5.0,'triggerTime':5.0}}
        a._basic_fields(synthetic,bound);cases.append({'name':'12 actual binding and synthetic Basic typed positive','status':'PASS'})
        bad=deepcopy(binding);bad['input_canonical_sha256']='0'*64
        negative('13 wrong canonical input',lambda:a.bindings(bundle,bad))
        b=deepcopy(bundle);b['runtime']['profile_id']='pure-combat-fixed-king-A-input441/1';bad=deepcopy(binding);bad['input_canonical_sha256']=digest(json.dumps(b,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
        negative('14 old profile with synthetic digest',lambda:a.bindings(b,bad))
        item=deepcopy(synthetic);del item['fields']['activationsToTrigger']
        negative('15 missing Basic REAL',lambda:a._basic_fields(item,bound))
        item=deepcopy(synthetic);item['fields']['activations']=False
        negative('16 BOOL Basic INT',lambda:a._basic_fields(item,bound))
        item=deepcopy(synthetic);item['fields']['activationsToTrigger']=5
        negative('17 INT Basic REAL',lambda:a._basic_fields(item,bound))
        item=deepcopy(synthetic);item['fields']['triggerTime']=float('nan')
        negative('18 nonfinite Basic REAL',lambda:a._basic_fields(item,bound))
        fake={'pure_combat_diagnostics':{'callbacks':[{'kind':'source_callback','role':'item:P:foreign','mode':1}]}}
        negative('19 foreign noop identity',lambda:a.project_model_callbacks(fake,bound))
        node=bound['nodes']['tick:P'];row={'subject':{'type':'native_ref','native_id':node['native_id'],'role':'tick:P','class':'Node2D'}}
        negative('20 retained native subject class',lambda:a._subject(row,bound))
        stage='launcher-control'
        closed=read('data/phase474-joint-output-source/launcher-request-contract.json')['closed_keys'];request={k:None for k in closed}
        request.update(schema='phase474-root-joint-model-request/1',case_id='NATIVE-028-KING-BASIC-A',root_model_authorized=False)
        negative('21 false launcher authority',lambda:launcher.validate_request(request))
        assert calls['launcher.read_descriptor']==0 and len(cases)==21
        stage='postflight'
        after=[pin(Path(p['path'])) for p in before];equal(before,after)
        assert io['original_UI_opens']==1 and not forbidden
        result.update(status='ACCEPTED_FIXED_JOINT_INTERFACES_B1_B2_B5_SOURCE_NOT_FULL_RUN',source_before=before,source_after=after,
                      actual_UI_reads=1,other_original_INPUT_reads=0,loaded_candidate_paths_verified=True,source_body_edits=0,
                      constructor_attempts=3,constructor_rejections=2,successful_constructors=1,prepare_calls=1,logical_activate_calls=1,
                      actual_activate_method_entries=2,frame_passes_consumed=0,activation_Tape_position=tape.position,activation_Tape_audit=tape.audit,
                      runtime_validated_through='construct/prepare/activation only; full clock and terminal not executed',
                      complete_model_run=False,complete_native_comparison=False,forbidden_io=forbidden,io=dict(io),B2_status=b2['status'])
    except BaseException as error:
        result.update(status='FAILED_FIRST_ATTEMPT',stage=stage,error=type(error).__name__,reason=str(error),traceback=traceback.format_exc(),io=dict(io),forbidden_io=forbidden)
        if engine is not None:
            partial={'prepared':engine.prepared,'activated':engine.activated,'ended':engine.ended,'frame':engine.frame,'elapsed':engine.elapsed,
                     'passes_consumed':engine.frame_driver.pass_index,'events':engine.events,'listeners':engine.activation_listeners,
                     'pure_snapshots':engine.pure_snapshots,'api':engine.pure_api_trace,'runtime_trace':engine.runtime_trace}
            artifacts.append(write_new(OUTPUT/'same-instance-partial.json',partial))
        if tape is not None:result['Tape_partial']={'position':tape.position,'audit':tape.audit,'records':len(tape.records)}
    result['calls']=dict(calls);result['wall_seconds']=time.monotonic()-start
    artifacts.append(write_new(OUTPUT/'result.json',result))
    write_new(OUTPUT/'owned-files.json',{'schema':'phase475-independent-interface-owner/1','status':result['status'],'files':artifacts})
    print(json.dumps({'status':result['status'],'stage':result.get('stage'),'cases':len(cases),'wall_seconds':result['wall_seconds'],'calls':dict(calls)}))
    return 0 if result['status']=='ACCEPTED_FIXED_JOINT_INTERFACES_B1_B2_B5_SOURCE_NOT_FULL_RUN' else 1


if __name__=='__main__':raise SystemExit(main())
