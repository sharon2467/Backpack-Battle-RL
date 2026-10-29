"""One bounded, input-only phase443 interface-control batch; never a battle."""
from pathlib import Path
import copy
import hashlib
import importlib
import json
import signal
import sys
import time
import traceback
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
STAGED = ROOT / 'data/phase443-pure-candidate-source/staged'
FREEZE = 'data/phase443-pure-candidate-source/candidate-source-freeze.json'
FREEZE_SHA = 'b5a87cbaab96e859368fdc5a037889c5931908d429e3551a612c732af5e0d68a'
BUNDLE = 'data/phase441-fixed-A-input-first-001/input-bundle.json'
BUNDLE_SHA = 'c87525f35adf8fa3793cc5d1440dff420dc55f3a24c77e520766b01e8963ae2c'
OUTPUT = ROOT / 'data/phase444-independent-interfaces-first-001'
OWNER = ROOT / 'data/phase444-independent-interfaces-source/owned-files.json'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encoded(value):
    return (json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + '\n').encode()


def pin(path, expected=None, size=None):
    raw = path.read_bytes()
    record = dict(path=str(path.relative_to(ROOT)), size=len(raw), sha256=sha(raw))
    if expected is not None and record['sha256'] != expected:
        raise AssertionError('source/input drift: ' + str(path))
    if size is not None and len(raw) != size:
        raise AssertionError('size drift: ' + str(path))
    return raw, record


def state_digest(root):
    """Stored state only: no model getters; represent aliases/cycles explicitly."""
    seen = {}

    def walk(value):
        if value is None or type(value) in (bool, str, int):
            return [type(value).__name__, value]
        if type(value) is float:
            return ['float', value.hex()]
        if callable(value):
            return ['callable', id(value)]
        identity = id(value)
        if identity in seen:
            return ['ref', seen[identity]]
        seen[identity] = len(seen)
        if type(value) is dict:
            return ['dict', [[walk(k), walk(v)] for k, v in value.items()]]
        if type(value) in (list, tuple):
            return [type(value).__name__, [walk(v) for v in value]]
        if type(value) in (set, frozenset):
            return [type(value).__name__, [walk(v) for v in sorted(value, key=repr)]]
        if hasattr(value, '__dict__'):
            return [type(value).__module__, type(value).__name__, walk(vars(value))]
        return [type(value).__name__, repr(value)]

    return sha(encoded(walk(root)))


def main():
    if OUTPUT.exists():
        raise RuntimeError('unique output already exists; no retry')
    OUTPUT.mkdir()
    started = time.monotonic()
    reads, calls, cases = [], Counter(), []
    report = dict(schema='phase444-independent-interface-controls/1', status='RUNNING',
                  cases=cases, model_release=False, King_admitted=False,
                  scope='one actual INPUT-derived instance, then synthetic local mutations; no battle')
    allowed = {str(ROOT / FREEZE), str(ROOT / BUNDLE), str(OWNER), str(Path(__file__).resolve())}
    output_paths = {str(OUTPUT / 'result.json'), str(OUTPUT / 'owned-files.json')}
    auditing = False

    def audit(event, args):
        if event != 'open' or not args or not isinstance(args[0], (str, bytes)):
            return
        path = Path(args[0]).resolve()
        if not path.is_relative_to(ROOT):
            if path.is_relative_to('/workspace'):
                raise AssertionError('outside-repository workspace access forbidden: ' + str(path))
            return  # Standard-library/platform imports, not task data.
        mode = args[1]
        flags = args[2]
        writing = (isinstance(mode, str) and any(c in mode for c in 'wax+')) or flags & 3 != 0
        if writing:
            if str(path) not in output_paths:
                raise AssertionError('unapproved repository write: ' + str(path))
        elif str(path) not in allowed:
            raise AssertionError('unapproved repository read: ' + str(path))
        reads.append(dict(path=str(path.relative_to(ROOT)), operation='write' if writing else 'read'))

    def profile(frame, event, arg):
        if event != 'call':
            return
        local = frame.f_locals.get('self')
        generated_state = (frame.f_code.co_filename == '<string>' and local is not None
                           and type(local).__module__ == 'native_replay_v8.engine'
                           and type(local).__name__ in ('CharacterState', 'ItemState'))
        if not generated_state and not frame.f_code.co_filename.startswith(str(STAGED) + '/'):
            return
        cls = type(local).__name__ + '.' if local is not None else ''
        origin = 'generated_dataclass' if generated_state else str(Path(frame.f_code.co_filename).relative_to(STAGED))
        key = origin + ':' + cls + frame.f_code.co_name
        calls[key] += 1
        forbidden = {'run', 'run_input_bundle', 'run_observed', 'compare_expected', 'compare_capture',
                     'activate_from_checkpoint', 'activate', 'step', 'result', 'complete'}
        primitive = cls == 'TapeRandom.' and frame.f_code.co_name in ('_take', 'randf', 'randf_range', 'randi_range', 'global_u32')
        if frame.f_code.co_name in forbidden or primitive:
            raise AssertionError('forbidden model entry: ' + key)

    def passed(name, **facts):
        cases.append(dict(name=name, status='PASS', **facts))

    def reject(name, fn):
        try:
            fn()
        except ValueError as exc:
            passed(name, rejection=str(exc))
        else:
            raise AssertionError('negative accepted: ' + name)

    def check_snapshot(name, obj, getter):
        before = state_digest(obj)
        first, second = getter(), getter()
        assert first == second, name + ': unstable snapshot'
        assert state_digest(obj) == before, name + ': mutated stored state'
        passed(name, state_sha256=before)
        return first

    def deadline(signum, frame):
        raise TimeoutError('15-second control budget exceeded')

    try:
        raw, freeze_ref = pin(ROOT / FREEZE, FREEZE_SHA, 4466)
        freeze = json.loads(raw)
        allowed.update(str(ROOT / row['path']) for row in freeze['files'])
        # Imports may probe a missing pycache file before falling back to source.
        allowed.update(str(p.parent / '__pycache__' / (p.stem + '.cpython-' + str(sys.version_info.major) + str(sys.version_info.minor) + '.pyc'))
                       for p in (ROOT / row['path'] for row in freeze['files']))
        source_refs = [pin(ROOT / row['path'], row['sha256'], row['size'])[1] for row in freeze['files']]
        assert len(source_refs) == 15
        own = json.loads(OWNER.read_bytes())
        for row in own['files']:
            allowed.add(str(ROOT / row['path']))
            pin(ROOT / row['path'], row['sha256'], row['size'])
        report['source_pins'] = source_refs
        report['freeze'] = freeze_ref
        report['control_source_owner'] = pin(OWNER)[1]
        sys.addaudithook(audit)
        auditing = True
        sys.dont_write_bytecode = True
        sys.path.insert(0, str(STAGED))
        signal.signal(signal.SIGALRM, deadline)
        signal.setitimer(signal.ITIMER_REAL, 15)
        sys.setprofile(profile)
        E = importlib.import_module('native_replay_v8.engine')
        R = importlib.import_module('native_replay_v8.randomness')
        for name, module in list(sys.modules.items()):
            if name.startswith(('native_replay_v7', 'native_replay_v8')):
                assert Path(module.__file__).resolve().is_relative_to(STAGED), name
        raw, input_ref = pin(ROOT / BUNDLE, BUNDLE_SHA, 539534)
        bundle = json.loads(raw)
        report['input'] = input_ref
        fixture, runtime = bundle['fixture'], bundle['runtime']
        assert set(bundle) == {'schema', 'fixture', 'runtime', 'draws', 'synthetic_seed'}
        assert len(bundle['draws']) == 365 and bundle['synthetic_seed'] is None
        dto = E.validate_runtime_inputs(runtime, fixture)
        passed('actual14_DTO', runtime_keys=len(runtime), draws=len(bundle['draws']))

        def bad(name, change):
            altered = copy.deepcopy(runtime)
            change(altered)
            reject(name, lambda: E.validate_runtime_inputs(altered, fixture))

        bad('missing_key', lambda x: x.pop('timer_initial'))
        bad('extra_key', lambda x: x.update(display='excluded'))
        bad('fps_BOOL', lambda x: x['environment'].update(fps=True))
        bad('scale_INT', lambda x: x['environment'].update(scale=1))
        bad('limiter_BOOL', lambda x: next(iter(x['initial_items'].values())).update(activationsThisFrame=False))
        bad('character_invu_INT', lambda x: x['initial_characters']['P'].update(invulnerable=0))
        bad('duplicate_order', lambda x: x['prepare_order'].__setitem__(1, x['prepare_order'][0]))
        bad('native_alias', lambda x: x['processing_nodes'][1].update(native_id=x['processing_nodes'][0]['native_id']))
        bad('flag_INT', lambda x: x['processing_nodes'][0].update(internal_idle=0))
        bad('config_path', lambda x: x['nodes'][0].update(path='/root/wrong'))
        bad('mode_BOOL', lambda x: x['timer_initial']['invu:P'].update(process_mode=False))
        bad('private_zero', lambda x: x['timer_initial']['invu:P'].update(private_left_bits=E._float_bits(0.0)))
        bad('one_shot_INT', lambda x: x['timer_initial']['invu:P'].update(one_shot=1))
        def stale_p5(x):
            for row in x['nodes'] + x['processing_nodes']:
                if row['role'] == 'invu:P':
                    row['positions'][-1] = 5
        bad('stale_P5', stale_p5)
        reject('DTO_convenience', lambda: E.validate_runtime_inputs(E.RuntimeDTO(dto.data, dto.prepare_order, dto.util_time + 1.), fixture))

        state_calls = lambda: sum(v for k, v in calls.items() if k.endswith(('ItemState.__init__', 'CharacterState.__init__')))
        for name, rng in (('None', None), ('SeededRandom', R.SeededRandom(0))):
            before = state_calls()
            reject('no_seed_' + name, lambda rng=rng: E.CombatEngine(fixture, rng, dto))
            assert state_calls() == before
        tape = R.TapeRandom(bundle['draws'])
        engine = E.CombatEngine(fixture, tape, dto)
        report['same_instance'] = dict(engine=id(engine), tape=id(tape), timer_runtime=id(engine.timer_runtime), driver=id(engine.frame_driver))
        assert tape.position == 0 and tape.audit == []
        rt = engine.timer_runtime
        timers = {role: node for role, node in engine.runtime_roles.items() if isinstance(node, E.TimerRecord)}
        assert len(timers) == len({id(n) for n in timers.values()}) == 33
        assert set(timers) == set(runtime['timer_initial'])
        for role, node in timers.items():
            initial = runtime['timer_initial'][role]
            assert node.private_left == -1. and not node.processing and node.wait_time == 1.
            assert node.one_shot is initial['one_shot'] and node.process_mode == 0 and not node.paused and not node.autostart
        for row in runtime['processing_nodes']:
            node = rt.root if row['role'] == 'root_viewport' else engine.runtime_roles[row['role']]
            assert rt._path(node) == row['path'] and list(rt._positions(node)) == row['positions']
            for flag in ('ordinary_physics', 'internal_physics', 'ordinary_idle', 'internal_idle'):
                assert getattr(node, flag) is row[flag]
        for role in ('util', 'game'):
            node = engine.runtime_roles[role]
            for mode in (0, 1):
                assert sum(member is node for member in rt.groups[(mode, True)]['members']) == 1
                assert (node, mode) in rt.ordinary_callbacks
        assert len(rt.ordinary_callbacks) == len(set(rt.ordinary_callbacks))
        passed('real33_sparse78_Util_Game', timers=33, processing_nodes=78)
        snap = check_snapshot('constructed_read_only', engine, lambda: engine._pure_business_snapshot('constructed_off_clock'))
        assert snap['off_clock'] and snap['clock'] is None
        engine.prepare_only()
        assert engine.prepared and not engine.activated and tape.position == 0 and not tape.audit
        snap = check_snapshot('prepared_read_only', engine, lambda: engine._pure_business_snapshot('prepare_off_clock'))
        assert snap['off_clock'] and snap['clock'] is None
        assert [s['stage'] for s in engine.pure_snapshots] == ['constructed_off_clock', 'prepare_off_clock']
        tape.position = 1
        try:
            reject('prepared_Tape_guard', engine._validate_pure441_prepared)
        finally:
            tape.position = 0
        passed('construct_prepare_no_Tape', position=tape.position, audit=len(tape.audit))

        real_history = engine.histories.item_state
        history_calls = []
        def history_spy(item, state, next_event=False):
            history_calls.append([item.instance_id, state, next_event])
            return real_history(item, state, next_event=next_event)
        engine.histories.item_state = history_spy
        king_table = engine.king_states
        engine.king_states = {}  # A visual-tail access now fails; the real history still executes.
        try:
            for state, with_next in ((0, False), (1, True), (2, False)):
                engine.king_set_state(engine.items['P:12'], state, with_next)
        finally:
            engine.king_states = king_table
            del engine.histories.item_state
        assert history_calls == [['P:12', 0, False], ['P:12', 1, True], ['P:12', 2, False]]
        history = engine.histories.logger('P')['itemStateHistories']['P:12']
        assert history.values[-3:] == [0, 1, 2]
        assert history.event_numbers[-3:] == [engine.event_num, engine.event_num + 1, engine.event_num]
        passed('King_real_history_before_visual_return', calls=history_calls)

        timer_cases = [('tick:P', ()), ('fatigue:start', (14,)), ('fatigue:tick', (3,)),
                       ('fatigue:tick', (1,)), ('fatigue:start', (14.0,))]
        for role, args in timer_cases:
            engine._start_timer(role, *args)
            before, after = engine.pure_api_trace[-2:]
            expected = [] if not args else ([dict(type='int', decimal=str(args[0]))] if type(args[0]) is int else [dict(type='float', binary64_be=E._float_bits(args[0]))])
            assert before['edge'] == 'before' and after['edge'] == 'after'
            assert before['argc'] == after['argc'] == len(args) and before['args'] == after['args'] == expected
            assert after['helper_status'] == dict(ok=True, error=None)
            assert after['native_return_semantics'] == dict(typed={'type': 'null'}, basis='SOURCE_VOID_NOT_SAMPLED')
            assert timers[role].processing
            engine._stop_timer(role)
        reject('start_BOOL', lambda: engine._start_timer('tick:P', True))
        reject('start_argc2', lambda: engine._start_timer('tick:P', 1, 2))
        passed('Timer_wrapper_arity_and_Variant', starts=len(timer_cases))

        driver_snap = check_snapshot('FrameDriver_wrapper_read_only_unadvanced', engine, engine.frame_driver.snapshot)
        assert 'business' in driver_snap and 'full_fx' not in driver_snap
        assert driver_snap['passes_consumed'] == 0 and len(driver_snap['business']['timers']) == 33
        assert driver_snap['business']['clock']['phase'] == 'before_activation_idle_tail'
        passed('wrapper_label_disclosure', selected_stage=driver_snap['business']['stage'], actual_cut='unadvanced synthetic control, not cleanup')

        auxiliary = ['aux:' + side + ':' + name for side in ('P', 'O') for name in ('battleRageTimer', 'autoRageTimer')]
        for role in auxiliary:
            engine._start_timer(role, 1)
        stops = []
        real_stop = rt.stop
        def stop_spy(node):
            stops.append((node.role, id(node)))
            return real_stop(node)
        rt.stop = stop_spy
        engine.ended, engine.winner = True, 'P'
        try:
            engine.finish()
        finally:
            del rt.stop
        observed = [(role, identity) for role, identity in stops if role in auxiliary]
        assert observed == [(role, id(timers[role])) for role in auxiliary]
        assert all(timers[role].private_left == -1. and not timers[role].processing for role in auxiliary)
        assert not any(row.get('kind') == 'inactive_aux_stop' for row in engine.runtime_trace)
        assert engine.finalized and not engine.frame_driver.cleaned and not engine.frame_driver.finalized
        check_snapshot('synthetic_finished_read_only', engine, lambda: engine._pure_business_snapshot('synthetic_local_finish'))
        assert tape.position == 0 and not tape.audit and engine.frame_driver.pass_index == 0
        passed('four_real_aux_stops_synthetic_finish', auxiliary_calls=observed, all_component_stops=len(stops))
        assert calls['native_replay_v8/engine.py:CombatEngine.__init__'] == 3
        assert calls['native_replay_v8/engine.py:CombatEngine.prepare_only'] == 1
        assert calls['native_replay_v8/engine.py:CombatEngine.finish'] == 1
        report['source_readback'] = [pin(ROOT / row['path'], row['sha256'], row['size'])[1] for row in freeze['files']]
        report['summary'] = dict(constructor_attempts=3, successful_instances=1, prepare=1,
                                 synthetic_finish=1, real_timers=33, frame_passes=0, Tape_draws=0,
                                 full_battle=0, original12_reads=0, EXPECTED_reads=0, old_controls=0)
        report['status'] = 'PASS_INTERFACE_ONLY_NOT_RUNTIME_EQUIVALENCE'
    except BaseException as exc:
        report['status'] = 'FAIL_FIRST_ERROR_NO_RETRY'
        report['error'] = dict(type=type(exc).__name__, message=str(exc), traceback=traceback.format_exc())
    finally:
        sys.setprofile(None)
        signal.setitimer(signal.ITIMER_REAL, 0)
        report['elapsed_seconds'] = time.monotonic() - started
        report['profiled_model_component_calls'] = dict(sorted(calls.items()))
        report['readscope'] = dict(audit_installed=auditing, accesses=list(reads),
                                   bundle_reads=sum(x['path'] == BUNDLE and x['operation'] == 'read' for x in reads),
                                   pre_audit='freeze once,15 source pins,control-owner plus owned SPEC/script pins; no bundle read')
        report['remaining_blocks'] = ['B1 native constructor/cache/prepare equivalence', 'B2 separate finite Source acceptance', 'B5 required output method/site mapping']
        result_raw = encoded(report)
        (OUTPUT / 'result.json').write_bytes(result_raw)
        owner = dict(schema='phase444-independent-interface-result-owner/1', files=[dict(path=str((OUTPUT / 'result.json').relative_to(ROOT)), size=len(result_raw), sha256=sha(result_raw))])
        (OUTPUT / 'owned-files.json').write_bytes(encoded(owner))
    print(json.dumps(dict(status=report['status'], completed_cases=len(cases), elapsed_seconds=report['elapsed_seconds'], output=str(OUTPUT))))
    return 0 if report['status'].startswith('PASS') else 1


if __name__ == '__main__':
    raise SystemExit(main())
