"""Independent phase454 harness; candidate binding follows frozen453 Source review.

Preparation only until SOURCE_BINDING is sealed. Never runs at import.
"""
import copy
import hashlib
import importlib
import json
import math
import os
from pathlib import Path
import signal
import struct
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]
REQUESTS = ROOT / 'data/phase454-independent-headless-requests/requests.json'
REQUESTS_SHA = 'b5d0e3d4a9fc85ffaf007aecb662c7a41b3c508baacea1a036bb08d108862bea'
SOURCE_BINDING = dict(directory='data/phase453-source-pure-headless', owner_sha='80280bf96635d6ccfd7aaf00a48a3d14f9f7102139f14c59c52e65cff2d65670', freeze_sha='4643a0d6b501945bd2ef7303f42c9a9fdd8617e7b9e219e8c8ee21fcbe288606')
OUTPUT = ROOT / 'data/phase454-independent-source-headless-first-001'
HARNESS_OWNER = ROOT / 'data/phase454-independent-harness-source/owned-files.json'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def pinned(path, expected_sha=None, expected_size=None):
    raw = path.read_bytes()
    if expected_sha is not None and sha(raw) != expected_sha:
        raise AssertionError('SHA drift: ' + str(path))
    if expected_size is not None and len(raw) != expected_size:
        raise AssertionError('size drift: ' + str(path))
    return raw, dict(path=str(path), size=len(raw), sha256=sha(raw))


def save_json(path, value):
    raw = (json.dumps(value, ensure_ascii=False, allow_nan=False,
                      separators=(',', ':')) + '\n').encode()
    path.write_bytes(raw)
    return dict(path=str(path), size=len(raw), sha256=sha(raw))


def strict_difference(a, b, path='$'):
    """Full in-memory comparison; no JSON key coercion or FLOAT/INT aliases."""
    if type(a) is not type(b):
        return dict(path=path, reason='type', left=type(a).__name__, right=type(b).__name__)
    if type(a) is float:
        if struct.pack('>d', a) != struct.pack('>d', b):
            return dict(path=path, reason='float_bits', left=a.hex(), right=b.hex())
    elif type(a) is dict:
        ak = {(type(k), k) for k in a}
        bk = {(type(k), k) for k in b}
        if ak != bk:
            return dict(path=path, reason='typed_keys', left=repr(ak), right=repr(bk))
        for key in a:
            difference = strict_difference(a[key], b[key], path + '[' + repr(key) + ']')
            if difference is not None:
                return difference
    elif type(a) in (list, tuple):
        if len(a) != len(b):
            return dict(path=path, reason='length', left=len(a), right=len(b))
        for index, (av, bv) in enumerate(zip(a, b)):
            difference = strict_difference(av, bv, path + '[' + str(index) + ']')
            if difference is not None:
                return difference
    elif a != b:
        return dict(path=path, reason='value', left=repr(a), right=repr(b))
    return None


def stored_state_digest(root):
    """Stored model graph only, including explicit RNG slots; no global/module walk.

    Based on accepted444v3's bounded fingerprint approach. Pause profiling during
    traversal and compact JSON encoding, retaining alias/cycle information.
    """
    profile = sys.getprofile()
    sys.setprofile(None)
    try:
        seen = {}
        def walk(value):
            if value is None or type(value) in (bool, int, str):
                return [type(value).__name__, value]
            if type(value) is float:
                return ['float64', struct.pack('>d', value).hex()]
            if callable(value):
                return ['callable_identity', id(value)]
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
            module = type(value).__module__
            if module.startswith(('native_replay_v7', 'native_replay_v8')) or module in ('headless', 'original_rng', 'godot_pcg_integer'):
                fields = dict(vars(value)) if hasattr(value, '__dict__') else {}
                for cls in type(value).__mro__:
                    slots = cls.__dict__.get('__slots__', ())
                    if type(slots) is str:
                        slots = (slots,)
                    for slot in slots:
                        if slot not in ('__dict__', '__weakref__') and hasattr(value, slot):
                            fields['slot:' + slot] = getattr(value, slot)
                return [module, type(value).__name__, [[key, walk(field)] for key, field in fields.items()]]
            return ['external_identity', module, type(value).__name__, identity]
        started = time.monotonic()
        raw = json.dumps(walk(root), ensure_ascii=False, allow_nan=False,
                         separators=(',', ':')).encode()
        return dict(sha256=sha(raw), nodes=len(seen), bytes=len(raw),
                    seconds=time.monotonic() - started)
    finally:
        sys.setprofile(profile)


class InvocationCounter:
    """Cache exact code objects once; no per-call Path work or broad graph reads."""
    def __init__(self, functions):
        self.names = {function.__code__: name for name, function in functions.items()}
        self.counts = {name: 0 for name in functions}
        self.return_hooks = {}

    def __call__(self, frame, event, arg):
        name = self.names.get(frame.f_code)
        if name is None:
            return
        if event == 'call':
            self.counts[name] += 1
        elif event == 'return' and name in self.return_hooks:
            self.return_hooks[name](frame, arg)

    def snapshot(self):
        return self.counts.copy()

    def delta(self, before):
        return {key: self.counts[key] - before[key] for key in self.counts}


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def rejection(label, operation, counter, forbidden, records):
    before = counter.snapshot()
    try:
        operation()
    except ValueError as exc:
        delta = counter.delta(before)
        require(all(delta[key] == 0 for key in forbidden), label + ': non-atomic rejection')
        records.append(dict(case=label, status='PASS', error=str(exc), calls=delta))
    else:
        raise AssertionError(label + ': expected ValueError')


def main():
    require(not OUTPUT.exists(), 'unique first output already exists')
    OUTPUT.mkdir()
    began = time.monotonic()
    report = dict(schema='phase454-independent-Source-acceptance/1', status='STARTED',
                  controls=[], completed_battles=0, calls={}, artifacts=[], reads=[],
                  expected_reads=0, native_captures=0, prior_battle_reexecutions=0)
    counter = None
    engines = []
    startup = []
    failure = None
    source_files = []
    stage = 'preflight'
    read_events = {}
    def alarm(signum, frame):
        raise RuntimeError('Independent harness 45-second bound exceeded')
    signal.signal(signal.SIGALRM, alarm)
    signal.alarm(45)
    try:
        raw, rec = pinned(HARNESS_OWNER)
        report['reads'].append(rec)
        harness_owner = json.loads(raw)
        for entry in harness_owner['payloads']:
            _, rec = pinned(ROOT / entry['path'], entry['sha256'], entry['size'])
            report['reads'].append(rec)
        directory = ROOT / SOURCE_BINDING['directory']
        raw, rec = pinned(directory / 'owned-files.json', SOURCE_BINDING['owner_sha'])
        report['reads'].append(rec)
        owner = json.loads(raw)
        for entry in owner['payloads']:
            _, rec = pinned(ROOT / entry['path'], entry['sha256'], entry['size'])
            report['reads'].append(rec)
        raw, rec = pinned(directory / 'candidate-source-freeze.json', SOURCE_BINDING['freeze_sha'])
        report['reads'].append(rec)
        freeze = json.loads(raw)
        source_files = freeze['files']
        require(len(source_files) == 15, 'exact15 candidate files')
        raw, rec = pinned(REQUESTS, REQUESTS_SHA)
        report['reads'].append(rec)
        jobs = json.loads(raw)
        require(len(jobs) == 2, 'exact two presealed requests')
        before = dict(candidate=source_files, requests=rec, harness=harness_owner)
        report['artifacts'].append(save_json(OUTPUT / 'before.json', before))
        staged = directory / 'staged'
        allowed = {str((ROOT / row['path']).resolve()) for row in source_files}
        allowed.add(str(Path(__file__).resolve()))
        output_root = str(OUTPUT.resolve()) + os.sep
        stdlib_root = str(Path(sys.base_prefix).resolve()) + os.sep
        def audit(event, args):
            if event == 'open' and isinstance(args[0], (str, bytes, os.PathLike)):
                path = os.path.realpath(os.fsdecode(args[0]))
                mode, flags = args[1], args[2]
                writing = (isinstance(mode, str) and any(x in mode for x in 'wax+')) or (isinstance(flags, int) and flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC))
                if writing:
                    if not path.startswith(output_root):
                        raise PermissionError('candidate/harness write outside unique output: ' + path)
                elif path in allowed or path.startswith(stdlib_root) or path.startswith(output_root):
                    read_events[path] = read_events.get(path, 0) + 1
                else:
                    raise PermissionError('undeclared read blocked: ' + path)
            elif event in ('subprocess.Popen', 'os.system', 'socket.connect', 'socket.bind'):
                raise PermissionError('external execution/network forbidden: ' + event)
        sys.dont_write_bytecode = True
        sys.pycache_prefix = str(OUTPUT / 'unused-bytecode-cache')
        sys.path.insert(0, str(staged))
        sys.addaudithook(audit)
        stage = 'candidate_import'
        h = importlib.import_module('headless')
        e = importlib.import_module('native_replay_v8.engine')
        tr = importlib.import_module('native_replay_v7.timer_runtime')
        pcg = importlib.import_module('godot_pcg_integer')
        original_rng = importlib.import_module('original_rng')
        modules = {}
        for name, module in list(sys.modules.items()):
            if name in ('headless', 'godot_pcg_integer', 'original_rng') or name.startswith(('native_replay_v7', 'native_replay_v8')):
                path = str(Path(module.__file__).resolve())
                require(path in allowed, 'candidate module from wrong capsule: ' + name)
                modules[name] = path
        report['loaded_candidate_modules'] = modules
        counter = InvocationCounter({
            'initialize': h.initialize, 'run_batch': h.run_batch,
            'CombatRandom.__init__': h.CombatRandom.__init__,
            'GodotPCGInteger.__init__': pcg.GodotPCGInteger.__init__,
            'CombatEngine.__init__': e.CombatEngine.__init__,
            'prepare_only': e.CombatEngine.prepare_only,
            'activate_from_checkpoint': e.CombatEngine.activate_from_checkpoint,
            'Engine.run': e.CombatEngine.run, 'Engine.step': e.CombatEngine.step,
            'Engine.finish': e.CombatEngine.finish,
            'Battle.run': h.HeadlessBattle.run, 'Battle.step': h.HeadlessBattle.step,
            'Battle.result': h.HeadlessBattle.result, 'Battle.snapshot': h.HeadlessBattle.snapshot,
            'source_state_assert': e.CombatEngine._validate_source_pure_state,
        })
        def capture_constructor(frame, returned):
            model = frame.f_locals['self']
            if not getattr(model, 'source_pure_mode', False):
                return
            timers = {role: node for role, node in model.runtime_roles.items() if isinstance(node, tr.TimerRecord)}
            require(len(timers) == 33, 'actual33 Timers at constructor cut')
            require(not model.pure_combat_mode and not model.integration_mode, 'profile separation')
            require(type(model.random) is h.CombatRandom and type(model.random._generator) is original_rng.OriginalRNG and type(model.random._global_generator) is pcg.GodotPCGInteger, 'actual twoSource generators')
            require(not model.random.audit, 'constructor combat RNG audit empty')
            king_ids = [item.instance_id for item in model.items.values() if item.item_index == 262]
            require(len(king_ids) == 1 and set(model.king_states) == set(king_ids), 'dynamic King identity')
            require(model.king_states[king_ids[0]]['invuCharges'] == 0, 'constructor charges0')
            timer_rows = {}
            for role, node in timers.items():
                require(type(node.private_left) is float and node.private_left == -1.0 and not node.processing, 'real constructor Timer private state')
                require(node.wait_time == 1.0 and node.process_mode == 0 and node.one_shot is (not role.startswith('tick:')), 'real constructor Timer config')
                require(not any((node.paused, node.autostart, node.internal_idle, node.internal_physics, node.ordinary_idle, node.ordinary_physics)), 'real constructor Timer flags')
                timer_rows[role] = dict(parent=node.parent.role, name=node.name, private_left=node.private_left)
            require(set(model.runtime_inputs.data) == {'schema','mode','profile_id','checkpoint','environment','nodes','timer_initial','initial_items','initial_characters','prepare_order','activate_order','terminal_profile','clock_policy'}, '13key carrier')
            require(all('native_id' not in row for row in model.runtime_inputs.data['nodes']), 'no native identity')
            require(not any(role.startswith(('king_hide:', 'king_drag:')) for role in model.runtime_roles), 'no King presentation Timers')
            engines.append(model)
            startup.append(dict(stage='constructed', king=king_ids[0], timers=timer_rows,
                                item_count=len(model.items), audit=0, invu_charges=0))
        def capture_prepare(frame, returned):
            model = frame.f_locals['self']
            if getattr(model, 'source_pure_mode', False) and model.prepared:
                require(all(v['invuCharges'] == 3 for v in model.king_states.values()), 'real prepare charges3')
                require(not model.random.audit, 'prepare consumes no combat provider')
                require(all(item.cache_prepared for item in model.items.values()), 'real prepared caches')
                identity = next(iter(model.king_states)); item = model.items[identity]
                values = model.histories.logger(item.side)['itemStateHistories'][identity].values
                require(values == [0], 'history-first state0 at prepare')
                startup.append(dict(stage='prepared', king=identity, invu_charges=3, audit=0, state_history=list(values)))
        def capture_initialize(frame, returned):
            if returned is not None:
                local_global = frame.f_locals['global_rng']
                model_global = returned._engine.random._global_generator
                require(local_global.get_state() == model_global.get_state(), 'continuous postshuffle globalstate')
                require(local_global is not model_global, 'private runtime generator object')
        counter.return_hooks.update({'CombatEngine.__init__': capture_constructor, 'prepare_only': capture_prepare, 'initialize': capture_initialize})
        sys.setprofile(counter)
        stage = 'finite_controls'
        forbidden = ['CombatRandom.__init__', 'GodotPCGInteger.__init__', 'CombatEngine.__init__', 'prepare_only']
        for seed in (True, -1, 1 << 64):
            rejection('seed_' + repr(seed), lambda seed=seed: h.initialize(copy.deepcopy(jobs[0]['layout']), seed), counter, forbidden, report['controls'])
        def invalid_layout(label, change):
            layout = copy.deepcopy(jobs[0]['layout']); change(layout)
            rejection(label, lambda: h.initialize(layout, jobs[0]['seed']), counter, forbidden, report['controls'])
        invalid_layout('layout_extra_capture_clock', lambda x: x.update(frame_clock={}))
        invalid_layout('item_gem_extra', lambda x: x['sides'][0]['items'][-1].update(gems=[]))
        invalid_layout('collision', lambda x: x['sides'][0]['items'][-1].update(x=1,y=0,f=0))
        invalid_layout('uncovered_cell', lambda x: x['sides'][0]['items'][-1].update(x=6,y=4,f=0))
        invalid_layout('duplicate_identity', lambda x: x['sides'][0]['items'][-1].update(instance_id=x['sides'][0]['items'][0]['instance_id']))
        invalid_layout('class2_withKing', lambda x: x['sides'][1].update(character_class=2))
        def two_kings(x):
            side = x['sides'][1]
            side['items'] = [v for v in side['items'] if v['item_index'] == 11] + [dict(item_index=262,x=1,y=0,f=0,instance_id='O:secondKing')]
        invalid_layout('twoKing_legal_geometry', two_kings)
        invalid_layout('other75_clover_withKing', lambda x: next(v for v in x['sides'][0]['items'] if v['item_index']==22).update(item_index=24))
        for item_index in (53,168,129):
            def add_outside(x, item_index=item_index):
                side=x['sides'][0]; bags=[v for v in side['items'] if v['item_index']==11]; others=[v for v in side['items'] if v['item_index']!=11]
                if item_index==129:
                    side['items']=bags+[dict(item_index=129,x=4,y=0,f=0,instance_id='P:rageBag')]+others
                else:
                    side['items']=bags+[dict(item_index=11,x=4,y=0,f=0,instance_id='P:extraBag')]+others+[dict(item_index=item_index,x=4,y=0,f=0,instance_id='P:outsideKingDomain')]
            invalid_layout('outsideKing_domain_' + str(item_index), add_outside)
        badjobs=copy.deepcopy(jobs);badjobs[1]['seed']=True
        rejection('wholebatch_bad_later_job', lambda: h.run_batch(badjobs,keep_results=True), counter, forbidden, report['controls'])
        for name, kwargs in [('bool_budget',dict(max_seconds=True)),('zero_budget',dict(max_seconds=0)),('oversized_budget',dict(max_seconds=121)),('retention_not_BOOL',dict(keep_results=1))]:
            rejection('batch_' + name, lambda kwargs=kwargs: h.run_batch(copy.deepcopy(jobs),**kwargs), counter, forbidden, report['controls'])
        original_initialize=h.initialize
        sentinel=ValueError('phase454 intentional batch ValueError')
        class FailingBattle:
            def run(self, max_seconds):
                raise sentinel
        try:
            h.initialize=lambda layout,seed: FailingBattle()
            before_calls=counter.snapshot()
            try:h.run_batch(copy.deepcopy(jobs),keep_results=True)
            except ValueError as exc:require(exc is sentinel, 'original ValueError identity propagated')
            else:raise AssertionError('batch swallowed ValueError')
            delta=counter.delta(before_calls)
            require(all(delta[k]==0 for k in forbidden), 'sentinel control unexpectedly constructed model')
            report['controls'].append(dict(case='batch_ValueError_propagates',status='PASS',synthetic_fault=True,calls=delta))
        finally:h.initialize=original_initialize
        tiny=h.run_batch([copy.deepcopy(jobs[0])],max_seconds=1e-12,keep_results=True)
        row=tiny['jobs'][0]
        require(row['status']=='TIME_BUDGET' and 'result' not in row and 'winner' not in row, 'actual tinybudget no manufactured result/winner')
        require(len(engines)==1 and not engines[0].ended and not engines[0].finalized and engines[0].winner is None, 'tinybudget did not finish a battle')
        report['controls'].append(dict(case='actual_tinybudget',status='PASS',record=row))
        tiny_engine=engines[0]
        tiny_battle=h.HeadlessBattle(tiny_engine, {})
        before_digest=stored_state_digest(tiny_engine)
        snap=tiny_battle.snapshot();done=tiny_battle.done
        after_digest=stored_state_digest(tiny_engine)
        require(before_digest['sha256']==after_digest['sha256'] and done is False,'readonly live snapshot/done')
        report['controls'].append(dict(case='readonly_snapshot_and_provider_slots',status='PASS',before=before_digest,after=after_digest))
        rejection('result_before_done',tiny_battle.result,counter,forbidden,report['controls'])
        fixture=tiny_engine.fixture
        for name, mutate in [('carrier_extra_native_id',lambda x:x['nodes'][0].update(native_id='123')),('carrier_BOOL_INT_alias',lambda x:x['timer_initial']['tick:P'].update(paused=0)),('carrier_external_passes',lambda x:x.update(frame_clock={}))]:
            carrier=copy.deepcopy(tiny_engine.runtime_inputs.data);mutate(carrier)
            rejection(name,lambda carrier=carrier:e.validate_runtime_inputs(carrier,fixture),counter,forbidden,report['controls'])
        require(counter.counts['Engine.finish']==0, 'no battle completion during controls')
        report['artifacts'].append(save_json(OUTPUT/'controls.json',dict(controls=report['controls'],calls=counter.snapshot(),startup=startup)))
        stage='batch_reference_two_battles'
        batch=h.run_batch(copy.deepcopy(jobs),keep_results=True)
        require(len(batch['jobs'])==2 and all(row['status']=='COMPLETED' for row in batch['jobs']), 'both reference jobs naturally complete')
        require(counter.counts['Engine.finish']==2, 'exact2 reference completions')
        report['completed_battles']=2
        references=[row['result'] for row in batch['jobs']]
        report['artifacts'].append(save_json(OUTPUT/'batch-reference.json',batch))
        stage='two_interleaved_battles'
        battles=[h.initialize(copy.deepcopy(job['layout']),job['seed']) for job in jobs]
        require(battles[0]._engine is not battles[1]._engine and battles[0]._engine.random is not battles[1]._engine.random, 'fresh independent engines/providers')
        step_calls=[0,0]
        while not all(battle.done for battle in battles):
            for index,battle in enumerate(battles):
                if not battle.done:
                    battle.step();step_calls[index]+=1
            require(max(step_calls)<=7202,'production quantum bound')
        require(counter.counts['Engine.finish']==4,'exact4 natural completions')
        report['completed_battles']=4
        stage='strict_results_and_terminal_checks'
        comparisons=[]
        for index,(battle,reference) in enumerate(zip(battles,references)):
            before_state=stored_state_digest(battle._engine)
            before_calls=counter.snapshot()
            require(battle.step() is False and battle.done is True,'postfinal step zero advancement')
            result=battle.result()
            after_state=stored_state_digest(battle._engine)
            delta=counter.delta(before_calls)
            require(before_state['sha256']==after_state['sha256'],'postfinal step/result readonly')
            require(delta['Engine.step']==0 and delta['Engine.run']==0,'postfinal result has no driver/run calls')
            artifact=save_json(OUTPUT/('interleaved-' + str(index) + '.json'),result)
            report['artifacts'].append(artifact)
            difference=strict_difference(reference,result)
            require(difference is None,'strict full result mismatch: '+repr(difference))
            require(strict_difference(reference['source_rng'],result['source_rng']) is None,'two-stream final states mismatch')
            require(result['coverage']['formal_support']==75 and 'PENDING' in result['coverage']['native_seed_parity'],'honest scope labels')
            require(result['source_terminal']['final']['physics_frame']>=result['source_terminal']['post_cleanup']['physics_frame']+2,'strict futurephysics terminal barrier')
            require(result['source_terminal']['final']['phase']=='idle_pre_internal_flush','final preinternalidle phase')
            rows=[v for v in result['source_timer_api'] if v['edge']=='before']
            tick=[v for v in rows if v['operation']=='start' and v['role'].startswith('tick:')]
            require(len(tick)==2 and all(v['argc']==0 and v['args']==[] for v in tick),'actual Tick argc0')
            fatigue=[v for v in rows if v['operation']=='start' and v['role'].startswith('fatigue:')]
            require(all(v['argc']==1 and v['args'][0]['type']=='int' and v['args'][0]['decimal'] in ('14','3','1') for v in fatigue),'actual fatigue INT forms')
            aux=[v['role'] for v in rows if v['operation']=='stop' and v['role'].startswith('aux:')]
            require(aux==['aux:P:battleRageTimer','aux:P:autoRageTimer','aux:O:battleRageTimer','aux:O:autoRageTimer'],'actual4auxstop sequence')
            king=next(item for side in result['fixture']['sides'] for item in side['items'] if item['item_index']==262)['instance_id']
            history=next(logger['itemStateHistories'][king] for logger in result['histories']['stat_loggers'] if king in logger['itemStateHistories'])
            comparisons.append(dict(index=index,status='PASS_FULL_TYPED_RESULT_AND_TWO_STREAM_STATES',steps=step_calls[index],winner=result['final']['winner'],terminal_time=result['final']['timestamp'],king=king,king_state_values=history['values'],event_count=len(result['events']),draw_count=len(result['random_inputs']),fatigue_arg_forms=sorted({v['args'][0]['decimal'] for v in fatigue}),actual_auxstops=aux,readonly_before=before_state,readonly_after=after_state))
        report['comparisons']=comparisons
        report['startup_cuts']=startup
        require(len(engines)==5,'1unfinished tinybudget plus4 completed models')
        report['status']='PASS_NEW_SOURCE_ONLY_FOUR_BATTLES_NOT_NATIVE_LAYOUT_OR_SEED_VALIDATION'
    except BaseException as exc:
        failure=exc
        report['status']='FAIL_FIRST_STOPPED_NO_RETRY'
        report['failure']=dict(stage=stage,type=type(exc).__name__,message=str(exc),traceback=traceback.format_exc())
    finally:
        sys.setprofile(None)
        signal.alarm(0)
        report['elapsed_seconds']=time.monotonic()-began
        if counter is not None:report['calls']=counter.snapshot()
        report['actual_captured_engines']=len(engines)
        report['completed_battles_observed']=sum(bool(getattr(model,'finalized',False)) for model in engines)
        report['startup_cuts']=startup
        report['runtime_open_read_counts']=read_events
        if failure is not None:
            report['partial_models']=[dict(king=list(model.king_states),prepared=model.prepared,activated=model.activated,ended=model.ended,finalized=model.finalized,winner=model.winner,frame=model.frame,elapsed=model.elapsed,provider_audit_length=len(model.random.audit),pass_index=model.frame_driver.pass_index) for model in engines]
        after=[]
        for row in source_files:
            try:
                _, rec=pinned(ROOT/row['path'],row['sha256'],row['size']);after.append(rec)
            except BaseException as exc:
                report.setdefault('after_source_errors',[]).append(str(exc));report['status']='FAIL_SOURCE_DRIFT'
        report['after_source_actual_reads']=after
        save_json(OUTPUT/'result.json',report)
        payloads=[]
        for path in sorted(OUTPUT.glob('*.json')):
            _, record=pinned(path);payloads.append(record)
        save_json(OUTPUT/'owned-files.json',dict(schema='phase454-independent-execution-owner/1',payloads=payloads))
    print(json.dumps(dict(status=report['status'],completed_battles=report['completed_battles_observed'],elapsed_seconds=report['elapsed_seconds'],output=str(OUTPUT))))
    if failure is not None:raise SystemExit(1)
    if report['status'].startswith('FAIL'):raise SystemExit(1)


if __name__ == '__main__':
    main()
