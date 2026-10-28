"""One Root-released actual441 build; never reruns helper controls or a model."""
import argparse
from collections import Counter
from copy import deepcopy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import time

ROOT = Path('/workspace/python-original-engine/repo')
MODULE = ROOT / 'tests/phase441_fixed_A_input_bridge.py'
AUTHOR_OWNER = ROOT / 'data/phase441-fixed-A-input-source/source-owner.json'
CONTEXT = ROOT / 'data/phase441-fixed-A-input-source/context.json'
CONTROLS = ROOT / 'data/phase441-independent-controls-first-001/result.json'
MODULE_SHA = 'e6c3336c5d91e51988d9629eaa779c3a229af5c1cc08d423609062831032f4f9'
AUTHOR_OWNER_SHA = '7184b737c00ca53ac497463c4f038164cdee39875efa5eea13707939b68882ea'
CONTEXT_SHA = '4cb8efbb24c78727de9dd3028499524561466e188302f944cd4abe5e4eba88df'
CONTROLS_SHA = '894bd9b46477a5a1f95595f465b9820abc0e483539d0e08475b9e2923e0f3321'
STACKS = {100:'Block',101:'Lucky',102:'Regeneration',103:'Vampirism',104:'Spikes',105:'Mana',106:'Empower',107:'Heat',108:'Poison',109:'Blind',110:'Cold'}
UI = {'king_hide:P:12', 'king_drag:P:12'}
OUTPUT_NAMES = ('input-bundle.json','input-proof.json','inputs-before-interpretation.json','input-readback.json','input-joint-seal.json','owned-files.json')


def equal(a, b):
    assert json.dumps(a, sort_keys=True, separators=(',', ':'), allow_nan=False) == json.dumps(b, sort_keys=True, separators=(',', ':'), allow_nan=False)


def path_of(value):
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def descriptor(path, raw=None):
    if raw is None:
        raw = path.read_bytes()
    return {'path': str(path), 'size': len(raw), 'sha256': digest(raw)}


def checked(path, expected_sha):
    raw = path.read_bytes()
    assert digest(raw) == expected_sha, str(path)
    return raw


def write_once(path, value):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write('\n')


def normalized(role):
    if role.startswith('buff:'):
        _, side, number = role.split(':')
        return 'buff:' + side + ':' + STACKS[int(number)]
    return role


def independent_mapping(bundle, proof, context, first_bytes):
    parsed_names = []
    def parse(name):
        raw = first_bytes[str(path_of(context['input_descriptors'][name]['path']))]
        parsed_names.append(name)
        return [json.loads(line) for line in raw.splitlines()] if name.endswith('.jsonl') else json.loads(raw)
    records = parse('observer7-input.jsonl')
    def one(site, edge):
        rows = [r for r in records if r['site'] == site and r['edge'] == edge]
        assert len(rows) == 1
        return rows[0]
    pre = one('Core/Game.gd::prepareItems', 'checkpoint')
    act = one('Core/Game.gd::activateItems', 'checkpoint')
    pe = one('Core/Game.gd::prepareItems', 'enter')
    ae = one('Core/Game.gd::activateItems', 'enter')
    bindings = parse('king-slot-bindings.json')['actual_bindings']
    natives = {x['instance_id']: x['native_id'] for x in bindings}
    assert len(natives) == 39 and 'O:12' not in natives
    fixed_pin = next(p for p in context['source_pins'] if p['path'].endswith('fixed-A-v8-fixture.json'))
    equal(bundle['fixture'], json.loads(first_bytes[str(path_of(fixed_pin['path']))]))
    for side, name in [('P', 'player_fixture.json'), ('O', 'fixture.json')]:
        original = parse(name)
        projected = next(s for s in bundle['fixture']['sides'] if s['side'] == side)
        assert original['health'] == projected['hp'] and original['stamina'] == projected['stamina']
        equal(original['items'], [{k:v for k,v in i.items() if k != 'instance_id'} for i in projected['items']])
    runtime = bundle['runtime']
    for name, entry in [('prepare_order', pe), ('activate_order', ae)]:
        args = {x['key']['value']: x['value'] for x in entry['payload']['arguments']['entries']}
        refs = args['items']['values']
        assert all(natives.get(x['role']) == x['native_id'] for x in refs)
        equal(runtime[name], [x['role'] for x in refs])
        assert len(set(runtime[name])) == 39
    audit = json.loads(first_bytes[str(path_of(context['audit']['path']))])
    index = {(x['field_id'],x['phase'],x['side_or_role']):x for x in audit['required_rows']}
    assert len(index) == 1363
    raw_nodes = {n['role']:n for n in act['payload']['nodes']}
    expected_processing, expected_nodes, expected_timers = [], [], {}
    for role, row in raw_nodes.items():
        if role in UI:
            continue
        name = normalized(role)
        node = deepcopy(row['node']); node['role'] = name
        expected_processing.append(node)
        if name != 'root_viewport':
            expected_nodes.append({k:deepcopy(node[k]) for k in ('role','path','positions','priority')} | {'kind':'timer' if row['timer'] is not None else 'ordinary'})
        timer = row['timer']
        if timer is not None:
            expected_timers[name] = {'wait_time_bits':timer['wait_time']['binary64_be'], **{k:timer[k] for k in ('one_shot','process_mode','autostart','paused')},
                                    'private_left_bits':index[('Timer.private_left','pre_activate',role)]['actual_value']['binary64_be']}
            assert expected_timers[name]['private_left_bits'] == 'bff0000000000000'
    equal(runtime['processing_nodes'], expected_processing)
    equal(runtime['nodes'], expected_nodes)
    equal(runtime['timer_initial'], expected_timers)
    assert len(expected_timers) == 33
    for side, child in [('P',7),('O',5)]:
        assert raw_nodes['invu:'+side]['node']['positions'] == raw_nodes['character:'+side]['node']['positions'] + [child]
        expected = {}
        for name in ('invulnerable','invulnerabilityItem','buffProtectStacks'):
            value = index[('Character.'+name,'pre_activate',side)]['actual_value']
            expected[name] = None if value['type'] == 'null' else value['value'] if value['type'] == 'bool' else int(value['decimal'])
        equal(runtime['initial_characters'][side], expected)
    initial = {}
    for item in pre['payload']['items']:
        f = item['fields']
        initial[item['instance']] = {'lastActivationTime_bits':f['lastActivationTime']['binary64_be'], 'lastTriggerTime_bits':f['lastTriggerTime']['binary64_be'],
          'activationsThisFrame':int(f['activationsThisFrame']['decimal']), 'triggersThisFrame':int(f['triggersThisFrame']['decimal']),
          'dragged':item['dragged']['value'], 'moveback_running':item['moveback_running']['value'],
          'cache_fresh':item['cachedAffectedItems'] == {'type':'dictionary','entries':[]}}
    equal(runtime['initial_items'], initial)
    equal(runtime['checkpoint'], {'util_time_bits':ae['stamp']['util_time']['binary64_be'], 'combat_time_bits':ae['stamp']['combat_time']['binary64_be'], 'source_phase':ae['stamp']['phase']})
    equal(runtime['environment'], {'fps':60,'scale':1.0,'paused':False})
    header, passes = parse('king-clock-checkpoint.json'), parse('king-clock-passes.jsonl')
    equal(runtime['frame_clock'], dict(header, passes=passes))
    primitives = parse('observer7-primitives.jsonl')
    expected_draws = []
    for row in primitives:
        assert row['sequence'] > ae['sequence']
        p = row['payload']; item = {'kind':p['kind'],'label':p['label']}
        if p['kind'] == 'randi_range':
            item.update(args=[int(a['decimal']) for a in p['args']], value=int(p['value']['decimal']))
        else:
            args = []
            for a in p['args']:
                if a['type'] == 'float': args.append(a['binary64_be'])
                else:
                    equal(a, {'type':'int','decimal':'0'})
                    assert row['site'] == 'Utility/Util.gd::roll'
                    args.append('0000000000000000')
            item.update(args=args, value_bits=p['value']['binary64_be'])
        expected_draws.append(item)
    equal(bundle['draws'], expected_draws)
    equal(proof['primitive_original_sequences'], [r['sequence'] for r in primitives])
    equal(proof['coverage']['future_model_blockers'], context['deferred_model_blockers'])
    assert proof['coverage']['runtime_validated'] is False and proof['coverage']['model_release'] is False
    assert bundle['synthetic_seed'] is None
    return {'items':39,'timers':33,'processing_nodes':len(expected_processing),'clock_passes':len(passes),'primitive_records':len(primitives),
            'independent_retained_INPUT_JSON_parses':parsed_names,'independent_retained_audit_JSON_parses':1,
            'original_INPUT_files_reopened_for_independent_mapping':0}


def run(release_path):
    started = time.monotonic()
    own_pin = descriptor(Path(__file__).absolute())
    release_raw = Path(release_path).read_bytes(); release = json.loads(release_raw)
    assert release['schema'] == 'phase441-root-input-build-release/1'
    assert release['wrapper_sha256'] == own_pin['sha256'] and release['module_sha256'] == MODULE_SHA
    assert release['controls_result_sha256'] == CONTROLS_SHA
    assert type(release['max_builds']) is int and release['max_builds'] == 1
    assert release['model_release'] is False and type(release['EXPECTED_reads']) is int and release['EXPECTED_reads'] == 0
    output, review = Path(release['output_new']), Path(release['review_output_new'])
    for path in (output, review):
        assert path.is_absolute() and str(path) == str(path.absolute()) and '..' not in path.parts
        assert path.is_relative_to(ROOT / 'data') and path != ROOT / 'data' and not os.path.lexists(path)
    assert output != review
    checked(MODULE, MODULE_SHA); owner = json.loads(checked(AUTHOR_OWNER, AUTHOR_OWNER_SHA))
    for p in owner['files']:
        raw = checked(ROOT / p['path'], p['sha256']); assert len(raw) == p['size']
    controls = json.loads(checked(CONTROLS, CONTROLS_SHA))
    assert controls['status'] == 'PASS_HELPERS_ONLY_NO_FULL_BUNDLE' and controls['actual_builds'] == controls['full_bundle_projections'] == 0
    context = json.loads(checked(CONTEXT, CONTEXT_SHA))
    checked(path_of(context['schema_module']['path']), context['schema_module']['sha256'])
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location('phase441_actual_target', MODULE)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    assert Path(module.native_schema.__file__).absolute() == path_of(context['schema_module']['path'])
    assert not any(n.startswith(('native_replay_v7','native_replay_v8')) for n in sys.modules)
    module.physical(review.parent, False); review.mkdir(mode=0o700)
    calls, reads, first_bytes, opens = {}, [], {}, []
    result = {'schema':'phase441-independent-actual-input/1','status':'RUNNING','call_counts':calls,'read_pinned_trace':reads,'build_open_trace':opens,
              'source_module':descriptor(MODULE),'source_owner':descriptor(AUTHOR_OWNER),'wrapper':own_pin,'controls_result':descriptor(CONTROLS),
              'release':descriptor(Path(release_path),release_raw),'model_runs':0,'EXPECTED_reads':0,'native_operations':0,'controls_replayed':0}
    result['instrumentation_scope'] = 'Counters/read_pinned/audit opens cover the actual build invocation. Wrapper preflight/postflight engineering metadata and independent output reads are separate; original12 are opened only inside build.'
    for name in ('build_from_files','project_from_bytes','project_decoded','decode_lawful12','load_accepted_initial','project_runtime','project_fixture','project_primitives','project_order','validate_initial_consumer_coverage'):
        original = getattr(module, name)
        def counted(*args, _name=name, _original=original, **kwargs):
            calls[_name] = calls.get(_name,0)+1
            return _original(*args, **kwargs)
        setattr(module, name, counted)
    original_read = module.read_pinned
    def observed_read(pin, io):
        raw = original_read(pin, io)
        reads.append(deepcopy(pin)); name = str(path_of(pin['path']))
        if name in first_bytes: assert first_bytes[name] == raw
        else: first_bytes[name] = raw
        return raw
    module.read_pinned = observed_read
    source_sequence = [dict(path=str(CONTEXT.relative_to(ROOT)),size=7919,sha256=CONTEXT_SHA)] + context['source_pins'] + [context['abi']] + list(context['receipts'].values())
    input_sequence = list(context['input_descriptors'].values()) + [context['audit']]
    input_allowed = {str(path_of(p['path'])) for p in source_sequence + input_sequence}
    output_allowed = {str(output / n) for n in OUTPUT_NAMES + ('first-error.json',)}
    active = [False]
    def guard(event, args):
        if not active[0]: return
        if event in ('subprocess.Popen','os.system','socket.connect'):
            raise RuntimeError('forbidden build side path: '+event)
        if event != 'open': return
        target, mode, flags = args
        if type(target) is int: raise RuntimeError('unattributed build fd open')
        name = str(Path(os.fsdecode(target)).absolute())
        writing = bool(flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND))
        allowed = name in output_allowed if writing else name in input_allowed | output_allowed
        opens.append({'path':name,'write':writing,'allowed':allowed})
        if not allowed: raise RuntimeError('unapproved build open: '+name)
    sys.addaudithook(guard)
    try:
        active[0] = True
        try: returned = module.build_from_files(str(output))
        finally: active[0] = False
        expected_calls = {n:1 for n in ('build_from_files','project_from_bytes','project_decoded','decode_lawful12','load_accepted_initial','project_runtime','project_fixture','project_primitives','validate_initial_consumer_coverage')}
        expected_calls['project_order'] = 2
        equal(calls, expected_calls)
        prefix = source_sequence + input_sequence + source_sequence + input_sequence
        equal(reads[:len(prefix)], prefix)
        assert [Path(x['path']).name for x in reads[len(prefix):]] == list(OUTPUT_NAMES)
        assert Counter(x['path'] for x in opens if not x['write']) == Counter(str(path_of(x['path'])) for x in reads)
        assert Counter(x['path'] for x in opens if x['write']) == Counter(str(output/n) for n in OUTPUT_NAMES)
        actual_files = {n:(output/n).read_bytes() for n in OUTPUT_NAMES}
        documents = {n:json.loads(raw) for n,raw in actual_files.items()}
        for saved in documents['owned-files.json']['files']:
            raw = actual_files[Path(saved['path']).name]
            assert len(raw) == saved['size'] and digest(raw) == saved['sha256']
        before, readback = documents['inputs-before-interpretation.json'], documents['input-readback.json']
        equal(before['source_files'], source_sequence); equal(before['input_payload_files'], input_sequence)
        for key in ('source_before','source_after'): equal(readback[key], source_sequence)
        for key in ('input_before','input_after'): equal(readback[key], input_sequence)
        seal = documents['input-joint-seal.json']
        assert seal['status'] == 'INPUT_ONLY_NOT_RUNTIME_VALIDATED' and seal['runtime_validated'] is False and seal['model_release'] is False and seal['King_admitted'] is False
        equal(seal['files'], documents['owned-files.json']['files'][:-1])
        bundle, proof = documents['input-bundle.json'], documents['input-proof.json']
        abi = json.loads(first_bytes[str(path_of(context['abi']['path']))])
        assert set(bundle) == set(abi['bundle_keys']) and set(bundle['runtime']) == set(abi['runtime_keys'])
        assert bundle['schema'] == abi['bundle_schema'] and bundle['runtime']['schema'] == abi['runtime_schema'] and bundle['runtime']['profile_id'] == abi['projection_profile']
        mapping = independent_mapping(bundle, proof, context, first_bytes)
        post_source = []
        for path, expected_sha in ((MODULE,MODULE_SHA),(AUTHOR_OWNER,AUTHOR_OWNER_SHA),(CONTEXT,CONTEXT_SHA),(CONTROLS,CONTROLS_SHA),
                                   (path_of(context['schema_module']['path']),context['schema_module']['sha256'])):
            post_source.append(descriptor(path,checked(path,expected_sha)))
        result.update(status='ACCEPTED_ACTUAL_INPUT_ONLY_NOT_RUNTIME_VALIDATED',returned=returned,mapping=mapping,
          build_source_read_count=2*len(source_sequence),lawful_carrier_read_count=24,accepted_audit_read_count=2,bridge_output_readbacks=6,
          independent_output_reads=6,bridge_syntax_decode_calls=1,full_actual_builds=1,runtime_validated=False,model_release=False,King_admitted=False,
          future_model_blockers=context['deferred_model_blockers'],elapsed_seconds=time.monotonic()-started,
          postbuild_engineering_readback=post_source,
          output_files=[descriptor(output/n,actual_files[n]) for n in OUTPUT_NAMES])
        write_once(review/'result.json',result)
        write_once(review/'owned-files.json',{'schema':'phase441-independent-actual-owned/1','files':[descriptor(review/'result.json'),own_pin,descriptor(MODULE),descriptor(AUTHOR_OWNER),descriptor(CONTROLS),result['release']]+result['output_files'],'status':result['status']})
        return result
    except Exception as error:
        active[0] = False
        result.update(status='FIRST_ERROR_STOP_NO_RETRY',error_type=type(error).__name__,error=str(error),elapsed_seconds=time.monotonic()-started)
        write_once(review/'first-error.json',result)
        raise


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--release',required=True)
    args=parser.parse_args(); result=run(args.release)
    print(json.dumps({'status':result['status'],'calls':result['call_counts'],'reads':len(result['read_pinned_trace']),'mapping':result['mapping'],'elapsed_seconds':result['elapsed_seconds']}))
