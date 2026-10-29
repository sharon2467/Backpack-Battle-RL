"""Independent fixed470 controls then one INPUT-only build; no model imports."""
import argparse
from collections import Counter
from copy import deepcopy
import dataclasses
import hashlib
import json
import math
import os
from pathlib import Path
import re
import stat
import struct
import sys
import time
import traceback
import types

ROOT = Path('/workspace/python-original-engine/repo')
OWNER = ROOT / 'data/phase470-joint-input-source/source-owner.json'
OWNER_SHA = '73b0ac566b5f59748c6b46fb0af75f2b0a0af0b1083f171de011a586ba245ab7'
BRIDGE = ROOT / 'tests/phase470_joint_input_bridge.py'
BRIDGE_SHA = 'd70d31b13226da2f08627986c260f32aba6520cb745bbc5dbc6bf069a5936394'
RECEIPT = ROOT / 'tests/phase470_joint_initial_receipt.py'
RECEIPT_SHA = '67cede8069561f03113008b1797be22248b1d2f69751c970c91c11060c2a6f4e'
STACKS = dict(zip(range(100, 111), ('Block','Lucky','Regeneration','Vampirism','Spikes','Mana','Empower','Heat','Poison','Blind','Cold')))


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def path_of(value):
    p = Path(value)
    return p if p.is_absolute() else ROOT / p


def pin(path):
    raw = path.read_bytes()
    return {'path': str(path), 'size': len(raw), 'sha256': sha(raw)}


def equal(a, b):
    # JSON transport values only; preserves INT/REAL/BOOL distinctions and -0.0.
    assert json.dumps(a, sort_keys=True, separators=(',', ':'), allow_nan=False) == json.dumps(b, sort_keys=True, separators=(',', ':'), allow_nan=False)


def write_new(path, value):
    with path.open('x', encoding='utf-8') as f:
        json.dump(value, f, ensure_ascii=False, indent=2, allow_nan=False)
        f.write('\n')


def load_exact(name, path, expected):
    raw = path.read_bytes()
    assert sha(raw) == expected, str(path)
    module = types.ModuleType(name)
    module.__file__ = str(path)
    sys.modules[name] = module
    exec(compile(raw, str(path), 'exec'), module.__dict__)
    return module


def norm(role):
    if role.startswith('buff:'):
        _, side, n = role.split(':')
        return 'buff:' + side + ':' + STACKS[int(n)]
    return role


def pointer(value, path):
    assert path.startswith('/')
    for token in path.split('/')[1:]:
        token = token.replace('~1', '/').replace('~0', '~')
        value = value[int(token)] if isinstance(value, list) else value[token]
    return value


def validate_refs(receipt, decoded, aliases):
    checked = []
    def check(ref):
        name = ref['file']
        assert name in ('observer7-input.jsonl', 'king-input-facts.json')
        if name.endswith('.jsonl'):
            row = decoded[name][ref['line'] - 1]
            assert row['sequence'] == ref['sequence']
            assert (ref['line'], ref['sequence']) in ((1, 99), (4, 1149))
            value = pointer(row, ref['pointer'])
            parts = ref['pointer'].split('/')
            if parts[2] == 'nodes':
                owner = row['payload']['nodes'][int(parts[3])]['node']['native_id']
            elif parts[2] == 'items':
                owner = aliases['role_to_native'][row['payload']['items'][int(parts[3])]['instance']]
            else:
                assert parts[2] == 'source_resources'
                resource = row['payload']['source_resources'][int(parts[3])]
                owner = resource['buffs'][int(parts[5])]['state']['timer']['node']['native_id'] if parts[4] == 'buffs' else resource['native_id']
            assert ref['native_owner'] == owner
        else:
            value = pointer(decoded[name], ref['pointer'])
            assert ref['native_owner'] == value['timer_id']
        checked.append((name, ref['pointer']))
        return value
    for row in receipt['values']:
        resolved = [check(r) for r in row['input_refs']]
        if row['classification'] == 'DIRECT_OBSERVATION':
            assert len(resolved) == 1
            equal(resolved[0], row['actual_value'])
    for witness in receipt['timer_witnesses']:
        check(witness['owner_ref'])
        for ref in witness['timer_refs']:
            check(ref)
    for ref in receipt['lifetime_witnesses'].values():
        equal(check(ref), ref['lineage'])
    for phase in receipt['prepare_observations'].values():
        for obs in phase.values():
            actual = check(obs['input_ref'])
            for key in ('cachedAffectedItems', 'currentAffectedItems'):
                equal(actual[key], obs[key])
            for key, value in obs.get('goobert_state', {}).items():
                equal(actual['fields'][key], value)
    return len(checked)


def independent_actual(bundle, proof, receipt, decoded, aliases, baseline_runtime):
    runtime = bundle['runtime']
    equal(runtime, baseline_runtime)
    assert set(bundle) == {'schema','fixture','runtime','draws','synthetic_seed'} and bundle['synthetic_seed'] is None
    assert bundle['schema'] == 'native-v8-input-only/1' and len(runtime) == 14
    assert runtime['profile_id'] == 'pure-combat-king-basic-A-captured/1'
    pre, act = decoded['observer7-input.jsonl'][0], decoded['observer7-input.jsonl'][3]
    assert [pre['sequence'], act['sequence']] == [99, 1149]
    equal(runtime['frame_clock'], dict(decoded['king-clock-checkpoint.json'], passes=decoded['king-clock-passes.jsonl']))
    ordinary, configs, timers = [], [], {}
    for wrap in act['payload']['nodes']:
        raw_role = wrap['role']
        if raw_role in ('king_hide:P:6', 'king_drag:P:6'):
            continue
        role = norm(raw_role)
        node = deepcopy(wrap['node']); node['role'] = role; ordinary.append(node)
        if role != 'root_viewport':
            configs.append({k: node[k] for k in ('role','path','positions','priority')} | {'kind': 'timer' if wrap['timer'] is not None else 'ordinary'})
        if wrap['timer'] is not None:
            t = wrap['timer']
            timers[role] = {k: t[k] for k in ('one_shot','process_mode','autostart','paused')} | {'wait_time_bits': t['wait_time']['binary64_be'], 'private_left_bits': 'bff0000000000000'}
    equal(runtime['processing_nodes'], ordinary); equal(runtime['nodes'], configs); equal(runtime['timer_initial'], timers)
    assert (len(ordinary),len(configs),len(timers),len(runtime['initial_items'])) == (65,64,33,26)
    for resource in act['payload']['source_resources']:
        side = resource['side']
        equal(runtime['initial_characters'][side], {'invulnerable':False,'invulnerabilityItem':None,'buffProtectStacks':int(resource['buffProtectStacks']['decimal'])})
    for row in pre['payload']['items']:
        fields = row['fields']
        expected = {k: int(fields[k]['decimal']) for k in ('activationsThisFrame','triggersThisFrame')}
        expected.update({k: row[k]['value'] for k in ('dragged','moveback_running')})
        expected.update({k+'_bits':fields[k]['binary64_be'] for k in ('lastActivationTime','lastTriggerTime')})
        assert row['cachedAffectedItems'] == {'type':'dictionary','entries':[]}
        expected['cache_fresh'] = True
        equal(runtime['initial_items'][row['instance']], expected)
    for side, name in (('P','player_fixture.json'),('O','fixture.json')):
        projected = next(x for x in bundle['fixture']['sides'] if x['side'] == side)
        actual = decoded[name]
        assert projected['hp'] == actual['health'] and projected['stamina'] == actual['stamina']
        equal(actual['items'], [{k:v for k,v in item.items() if k != 'instance_id'} for item in projected['items']])
    for name, site in (('prepare_order','prepareItems'),('activate_order','activateItems')):
        row = next(r for r in decoded['observer7-input.jsonl'] if r['site'] == 'Core/Game.gd::'+site and r['edge'] == 'enter')
        args = {p['key']['value']:p['value'] for p in row['payload']['arguments']['entries']}
        refs = args['items']['values']
        assert all(aliases['role_to_native'][r['role']] == r['native_id'] for r in refs)
        equal(runtime[name], [r['role'] for r in refs])
    records = decoded['observer7-primitives.jsonl']
    assert len(bundle['draws']) == len(records)
    for original, draw in zip(records, bundle['draws']):
        value = original['payload']
        assert draw['kind'] == value['kind'] and draw['label'] == value['label']
        if value['kind'] == 'randi_range':
            equal(draw['args'], [int(v['decimal']) for v in value['args']]); assert draw['value'] == int(value['value']['decimal'])
        else:
            bits = []
            for v in value['args']:
                if v['type'] == 'float': bits.append(v['binary64_be'])
                else:
                    assert original['site'] == 'Utility/Util.gd::roll' and v == {'type':'int','decimal':'0'}
                    bits.append('0000000000000000')
            equal(draw['args'], bits); assert draw['value_bits'] == value['value']['binary64_be']
    equal(proof['primitive_original_sequences'], [r['sequence'] for r in records])
    origins = proof['field_origins']
    assert all('bundle.'+k in origins for k in bundle) and all('runtime.'+k in origins for k in runtime)
    for role, values in timers.items():
        for field in values: assert 'timer_initial.'+role+'.'+field in origins
    for side, values in runtime['initial_characters'].items():
        for field in values: assert 'initial_characters.'+side+'.'+field in origins
    for role in runtime['initial_items']: assert 'initial_items.'+role in origins
    for origin in origins.values():
        if origin.get('file') == 'initial-receipt.json' and 'pointer' in origin:
            row = receipt['values'][int(origin['pointer'].split('/')[2])]
            equal(row['key'], origin['key']); equal(row['input_refs'], origin['input_refs'])
            assert row['classification'] == origin['classification'] and row['rule'] == origin['rule']
            equal(pointer(receipt, origin['pointer']), row['actual_value'])
    refs_checked = validate_refs(receipt, decoded, aliases)
    return {'items':26,'business_timers':33,'processing_nodes':65,'node_configs':64,'derived':74,
            'clock_passes':len(runtime['frame_clock']['passes']),'primitives':len(records),'field_origins':len(origins),'receipt_input_refs_checked':refs_checked}


def run(output, build_output):
    assert output.parent == build_output.parent == ROOT/'data'
    assert output.name == 'phase470-independent-input-acceptance-first-001'
    assert build_output.name == 'phase470-joint-input-first-001'
    assert not output.exists() and not build_output.exists()
    output.mkdir(mode=0o700)
    started = time.monotonic(); stage = 'source-preflight'
    calls, io = Counter(), Counter(); cases = []; owner_payloads = []
    result = {'schema':'phase470-independent-input-acceptance/1','status':'RUNNING','cases':cases,'calls':calls,
              'model_runs':0,'Oracle':0,'EXPECTED_business_decodes':0,'pool_operations':0,'old_controls':0,'runtime_validated':False}
    try:
        assert pin(OWNER)['sha256'] == OWNER_SHA
        author = json.loads(OWNER.read_bytes())
        source_before = []
        for p in author['files']:
            d = pin(path_of(p['path'])); assert (d['size'],d['sha256']) == (p['size'],p['sha256']); source_before.append(d)
        source_before.extend([pin(OWNER),pin(Path(__file__).absolute())])
        assert pin(BRIDGE)['sha256'] == BRIDGE_SHA and pin(RECEIPT)['sha256'] == RECEIPT_SHA
        allowed_sources = {p['path'] for p in source_before}
        raw_pins = author['actual_input_descriptors']; raw_paths = {p['path'] for p in raw_pins.values()}
        source_counts = Counter(); forbidden = []
        stdlib = str(Path(os.__file__).parent) + '/'
        def audit(event, args):
            if event in ('subprocess.Popen','os.system','socket.connect'):
                forbidden.append(event); raise RuntimeError('FORBIDDEN_OPERATION '+event)
            if event != 'open' or isinstance(args[0], int): return
            p = os.path.abspath(os.fsdecode(args[0])); mode, flags = args[1], args[2]
            writing = bool(flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND)) if isinstance(flags,int) else bool(mode and any(x in mode for x in 'wax+'))
            in_output = p.startswith(str(output)+'/') or p.startswith(str(build_output)+'/')
            if writing:
                if not in_output: forbidden.append(p); raise RuntimeError('FORBIDDEN_WRITE '+p)
            elif p in raw_paths: io[p] += 1
            elif p in allowed_sources: source_counts[p] += 1
            elif not (in_output or p.startswith(stdlib)):
                forbidden.append(p); raise RuntimeError('FORBIDDEN_READ '+p)
        sys.dont_write_bytecode = True
        sys.pycache_prefix = str(output/'unused-bytecode-cache')
        sys.addaudithook(audit)
        stage = 'imports'
        r = load_exact('phase470_joint_initial_receipt', RECEIPT, RECEIPT_SHA)
        m = load_exact('phase470_independent_bridge_target', BRIDGE, BRIDGE_SHA)
        schema = m.native_schema
        assert Path(r.__file__) == RECEIPT and Path(m.__file__) == BRIDGE and Path(schema.__file__) == path_of(m.SCHEMA_PIN['path'])
        assert not any(n.startswith(('native_replay','phase471')) for n in sys.modules)
        result['loaded_paths'] = {'bridge':m.__file__,'receipt':r.__file__,'schema':schema.__file__}
        for module, names, prefix in ((m,('read_pinned','decode_lawful12','verify_raw_inputs','project_runtime','project_primitives','project_decoded','project_from_bytes','build_from_files','source_value','validate_initial_consumer_coverage'),'bridge'),
                                      (r,('build_initial_receipt','validate_timer','validate_ledger','validate_cache_alias','value_index'),'receipt'),
                                      (schema,('decode_clock',),'schema')):
            for name in names:
                original = getattr(module,name)
                def counted(*args,_original=original,_key=prefix+'.'+name,**kwargs):
                    calls[_key] += 1
                    return _original(*args,**kwargs)
                setattr(module,name,counted)
                if module is r and name in ('build_initial_receipt','value_index'): setattr(m,name,counted)
        def positive(label, action):
            value = action(); cases.append({'name':label,'status':'PASS'}); return value
        def negative(label, action, missing=None):
            try: action()
            except (ValueError,KeyError) as e:
                if isinstance(e,KeyError): assert missing is not None and e.args == (missing,), str(e)
                elif missing is not None: raise AssertionError('Expected missing field KeyError: '+str(e)) from e
                cases.append({'name':label,'status':'PASS_REJECTED','error':type(e).__name__,'reason':str(e)})
            else: raise AssertionError('ACCEPTED_NEGATIVE '+label)
        stage = 'controls'
        read_log = []
        raw12 = {n:m.read_pinned(p,read_log) for n,p in raw_pins.items()}
        decoded, aliases, validation = m.decode_lawful12(raw12)
        pristine = sha(json.dumps(decoded,sort_keys=True,separators=(',',':')).encode())
        receipt = positive('01 new74 receipt',lambda:r.build_initial_receipt(decoded,aliases,schema))
        derived = [x for x in receipt['values'] if x['classification'] == 'SOURCE_DERIVED']
        assert Counter(x['rule'] for x in derived) == {'INACTIVE_PROCESSING_INVARIANT':64,'FRESH_KING_NATIVE_SCENE_NO_START':2,'CHARACTER_DEFAULT_CALLER_CLOSURE_LIFETIME_ZERO_START':8}
        assert all(x['actual_value'] == {'type':'float','binary64_be':'bff0000000000000'} for x in derived if x['key'][0] == 'Timer.private_left')
        index = r.value_index(receipt)
        first = next(iter(raw12)); bad = dict(raw12); b = raw12[first]; bad[first] = bytes([b[0]^1])+b[1:]
        negative('02 raw byte identity',lambda:m.verify_raw_inputs(bad))
        bad = dict(raw12); del bad[first]
        negative('03 missing raw carrier',lambda:m.verify_raw_inputs(bad))
        def cut(d, phase=0):
            site = ('prepareItems','activateItems')[phase]
            return next(x for x in d['observer7-input.jsonl'] if x['site'] == 'Core/Game.gd::'+site and x['edge'] == 'checkpoint')
        def wrapper(d, role, phase=0): return next(x for x in cut(d,phase)['payload']['nodes'] if x['role'] == role)
        def basic(d, phase=0): return next(x for x in cut(d,phase)['payload']['items'] if x['instance'] == 'P:7')
        d = deepcopy(decoded); cut(d)['payload']['nodes'][1]['role'] = cut(d)['payload']['nodes'][0]['role']
        negative('04 duplicate role',lambda:r.build_initial_receipt(d,aliases,schema))
        d = deepcopy(decoded); wrapper(d,'tick:P',1)['node']['native_id'] = aliases['role_to_native']['O']
        negative('05 foreign crosscut alias',lambda:r.build_initial_receipt(d,aliases,schema))
        parent = wrapper(decoded,'character:P')['node']
        w = deepcopy(wrapper(decoded,'tick:P')); w['timer']['process_mode'] = False
        negative('06 BOOL mode',lambda:r.validate_timer(w,parent,'tick:P',schema))
        w = deepcopy(wrapper(decoded,'tick:P')); w['node']['internal_idle'] = 0; w['timer']['node'] = deepcopy(w['node'])
        negative('07 INT flag',lambda:r.validate_timer(w,parent,'tick:P',schema))
        w = deepcopy(wrapper(decoded,'tick:P')); w['timer']['paused'] = True
        negative('08 paused Timer',lambda:r.validate_timer(w,parent,'tick:P',schema))
        w = deepcopy(wrapper(decoded,'tick:P')); w['node']['positions'][-1] += 1; w['timer']['node'] = deepcopy(w['node'])
        negative('09 wrong child position',lambda:r.validate_timer(w,parent,'tick:P',schema))
        d = deepcopy(decoded); cut(d)['payload']['source_resources'][0]['buffs'][0]['state']['timer']['time_left']['binary64_be'] = '3ff0000000000000'
        negative('10 Buff dual',lambda:r.build_initial_receipt(d,aliases,schema))
        timer = wrapper(decoded,'invu:P',1)['timer']; owner = wrapper(decoded,'character:P',1)['node']
        f = deepcopy(decoded['king-input-facts.json']); f['timers']['invu:P']['lineage']['owner_id'] = aliases['role_to_native']['O']
        negative('11 ledger owner',lambda:r.validate_ledger(f,'invu:P',owner,timer,schema))
        f = deepcopy(decoded['king-input-facts.json']); f['timers']['invu:P']['lineage']['starts'] = 1
        negative('12 nonzero start',lambda:r.validate_ledger(f,'invu:P',owner,timer,schema))
        d = deepcopy(decoded); scene = next(x for x in d['observer7-lineage.jsonl'] if x['edge'] == 'scene_instance' and x['payload']['item_id'] == aliases['role_to_native']['P:6']); scene['payload']['pooled'] = True
        negative('13 pooled King',lambda:r.build_initial_receipt(d,aliases,schema))
        d = deepcopy(decoded); del basic(d)['fields']['activationsToTrigger']
        negative('14 missing Basic threshold',lambda:r.build_initial_receipt(d,aliases,schema),missing='activationsToTrigger')
        d = deepcopy(decoded); basic(d)['fields']['activationsToTrigger'] = {'type':'int','decimal':'5'}
        negative('15 INT Basic threshold',lambda:r.build_initial_receipt(d,aliases,schema))
        d = deepcopy(decoded); basic(d)['fields']['activations'] = {'type':'bool','value':False}
        negative('16 BOOL Basic counter',lambda:r.build_initial_receipt(d,aliases,schema))
        cache = deepcopy(basic(decoded,1)['cachedAffectedItems']); refs = [x for e in cache['entries'] for x in e['value']['values']]; assert refs
        refs[0]['native_id'] = aliases['role_to_native']['O']
        negative('17 cache foreign alias',lambda:r.validate_cache_alias(cache,aliases,schema,False))
        d = deepcopy(decoded); basic(d,1)['fields']['cachedAffectedItems'] = {'type':'dictionary','entries':[]}
        negative('18 cache dual',lambda:r.build_initial_receipt(d,aliases,schema))
        ix = dict(index); del ix[('Timer.private_left','pre_activate','tick:P')]
        negative('19 missing receipt key',lambda:m.source_value(ix,'Timer.private_left','pre_activate','tick:P'))
        ae = next(x for x in decoded['observer7-input.jsonl'] if x['site'] == 'Core/Game.gd::activateItems' and x['edge'] == 'enter')['sequence']
        d = {'observer7-primitives.jsonl':deepcopy(decoded['observer7-primitives.jsonl'])}; assert d['observer7-primitives.jsonl']; d['observer7-primitives.jsonl'][0]['sequence'] = ae
        negative('20 early primitive',lambda:m.project_primitives(d,ae))
        clock = deepcopy(dict(decoded['king-clock-checkpoint.json'],passes=decoded['king-clock-passes.jsonl'])); assert len(clock['passes']) >= 2; clock['passes'][1] = deepcopy(clock['passes'][0])
        negative('21 clock duplicate',lambda:schema.decode_clock(clock))
        runtime, origins, _ = positive('22 partial runtime',lambda:m.project_runtime(decoded,aliases,index))
        assert (len(runtime['timer_initial']),len(runtime['initial_items']),len(runtime['processing_nodes']),len(runtime['nodes'])) == (33,26,65,64)
        equal(runtime['frame_clock'],dict(decoded['king-clock-checkpoint.json'],passes=decoded['king-clock-passes.jsonl']))
        for side in ('P','O'):
            assert runtime['initial_characters'][side]['invulnerable'] is False and runtime['initial_characters'][side]['invulnerabilityItem'] is None
            assert type(runtime['initial_characters'][side]['buffProtectStacks']) is int
        d = deepcopy(decoded)
        for role in ('king_hide:P:6','king_drag:P:6'): wrapper(d,role,1)['node']['priority'] += 1
        runtime_display, _, _ = positive('23 display exclusion',lambda:m.project_runtime(d,aliases,index)); equal(runtime,runtime_display)
        fake = {'schema':'native-v8-input-only/1','fixture':{},'runtime':runtime,'draws':[],'synthetic_seed':None}
        bad_origins = deepcopy(origins); bad_origins.update({'bundle.'+k:{} for k in fake}); del bad_origins['timer_initial.tick:P.private_left_bits']
        negative('24 missing origin',lambda:m.validate_initial_consumer_coverage(fake,bad_origins))
        assert len(cases) == 24 and sha(json.dumps(decoded,sort_keys=True,separators=(',',':')).encode()) == pristine
        assert calls['bridge.project_decoded'] == calls['bridge.project_from_bytes'] == calls['bridge.build_from_files'] == 0
        result['controls_calls'] = dict(calls); result['controls_seconds'] = time.monotonic()-started
        result['controls_raw_reads'] = dict(io)
        write_new(output/'controls.json',{'status':'PASS24','cases':cases,'calls':dict(calls),'raw_reads':dict(io),'full_bundle_projections':0,'partial_runtime_projections':2})
        stage = 'actual-build'
        build_started = time.monotonic()
        result['build_return'] = m.build_from_files(str(build_output))
        result['build_seconds'] = time.monotonic()-build_started
        assert calls['bridge.build_from_files'] == calls['bridge.project_from_bytes'] == calls['bridge.project_decoded'] == 1
        assert calls['bridge.decode_lawful12'] == 2
        stage = 'output-acceptance'
        output_owner = json.loads((build_output/'owned-files.json').read_bytes())
        for p in output_owner['files']:
            d = pin(path_of(p['path'])); assert (d['size'],d['sha256']) == (p['size'],p['sha256']); owner_payloads.append(d)
        bundle = json.loads((build_output/'input-bundle.json').read_bytes()); proof = json.loads((build_output/'input-proof.json').read_bytes()); actual_receipt = json.loads((build_output/'initial-receipt.json').read_bytes())
        equal(actual_receipt,receipt)
        result['mapping'] = independent_actual(bundle,proof,actual_receipt,decoded,aliases,runtime)
        readback = json.loads((build_output/'input-readback.json').read_bytes())
        equal(readback['source_before'],readback['source_after']); equal(readback['input_before'],readback['input_after'])
        assert len(readback['input_before']) == len(readback['input_after']) == 12
        seal = json.loads((build_output/'input-joint-seal.json').read_bytes())
        assert seal['status'] == 'INPUT_ONLY_NOT_RUNTIME_VALIDATED' and seal['runtime_validated'] is False and seal['model_release'] is False and seal['King_admitted'] is False
        source_after = [pin(Path(p['path'])) for p in source_before]; equal(source_before,source_after)
        assert set(io) == raw_paths and set(io.values()) == {3} and sum(io.values()) == 36
        assert not forbidden and not any(n.startswith(('native_replay','phase471')) for n in sys.modules)
        result.update(status='ACCEPTED_ACTUAL_INPUT_ONLY_NOT_RUNTIME_VALIDATED',source_before=source_before,source_after=source_after,
                      physical_raw_reads=dict(io),physical_raw_reads_total=sum(io.values()),distinct_raw_inputs=len(io),
                      source_read_opens_after_audit=dict(source_counts),input_output_owner=pin(build_output/'owned-files.json'),output_payloads=owner_payloads,
                      full_bundle_projections=1,actual_builds=1,transport_decodes=2,controls_case_count=24,
                      loaded_candidate_modules=[],forbidden_io=forbidden)
    except BaseException as error:
        result.update(status='FAILED_FIRST_ATTEMPT',stage=stage,error=type(error).__name__,reason=str(error),traceback=traceback.format_exc(),physical_raw_reads=dict(io),physical_raw_reads_total=sum(io.values()))
    result['wall_seconds'] = time.monotonic()-started
    result['calls'] = dict(calls)
    write_new(output/'result.json',result)
    files = [pin(p) for p in sorted(output.iterdir()) if p.is_file()]
    write_new(output/'owned-files.json',{'schema':'phase470-independent-actual-owner/1','files':files,'status':result['status']})
    print(json.dumps({'status':result['status'],'stage':result.get('stage'),'cases':len(cases),'wall_seconds':result['wall_seconds'],'output':str(output)}))
    return 0 if result['status'] == 'ACCEPTED_ACTUAL_INPUT_ONLY_NOT_RUNTIME_VALIDATED' else 1


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--output-new',required=True); p.add_argument('--build-output-new',required=True)
    args = p.parse_args()
    raise SystemExit(run(Path(args.output_new).absolute(),Path(args.build_output_new).absolute()))
