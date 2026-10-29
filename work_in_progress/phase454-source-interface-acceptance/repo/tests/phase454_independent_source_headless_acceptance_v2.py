"""Independent phase454 v2 remaining interleaving harness; no old controls/batch rerun.

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
OUTPUT = ROOT / 'data/phase454-independent-source-headless-v2-first-001'
HARNESS_OWNER = ROOT / 'data/phase454-independent-harness-source-v2/owned-files.json'


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


REFERENCE = ROOT / 'data/phase454-independent-source-headless-first-001/batch-reference.json'
REFERENCE_SHA = '23ce28b2f3a1eb3c0b86dec8e63fb86d0ca9096c17ffa0a6cc2a7c171f8ab422'


def restore_reference_result(raw, state, compare, counts):
    """Only Source-defined paths; never consult the new candidate result."""
    value = copy.deepcopy(raw)
    value['histories'] = compare.restore_history_json_keys(value['histories'])
    counts['restore_history_json_keys'] += 1
    for snapshot in (value['final'], value['source_terminal']['post_cleanup']['model'], value['source_terminal']['final']['model']):
        snapshot['native_rule_state'] = state.restore_state_json_keys(snapshot['native_rule_state'])
        counts['restore_state_json_keys'] += 1
        for character in snapshot['characters'].values():
            for field in ('typed_damage_factors', 'buff_fields'):
                character[field] = state.restore_integer_table(character[field])
                counts['direct_dataclass_integer_tables'] += 1
        for item in snapshot['items'].values():
            for field in ('buff_powers', 'buff_amplification_chances'):
                item[field] = state.restore_integer_table(item[field])
                counts['direct_dataclass_integer_tables'] += 1
            def coordinate(row):
                require(type(row) is list and len(row) == 2 and all(type(x) is int for x in row), 'Source coordinate tuple schema')
                counts['coordinate_tuples'] += 1
                return tuple(row)
            item['top_left'] = coordinate(item['top_left'])
            for field in ('cells', 'stars', 'ordered_cells'):
                require(type(item[field]) is list, 'Source outer coordinate list schema')
                item[field] = [coordinate(row) for row in item[field]]
    roundtrip = state.strict_json_loads(json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(',', ':')))
    require(strict_difference(raw, roundtrip) is None, 'restoration changed JSON business values/float bits')
    counts['strict_json_roundtrip'] += 1
    return value


def main():
    require(not OUTPUT.exists(), 'unique v2 output already exists')
    OUTPUT.mkdir()
    began = time.monotonic()
    report = dict(schema='phase454-independent-remaining-interleaving/2', status='STARTED',
                  source_model='UNCHANGED_PHASE453', old_controls_rerun=0, batch_calls=0,
                  previous_natural_completions=4, completed_battles=0,
                  explicit_public_calls=dict(initialize=0, step=[0,0], done=0, result=0, run=0),
                  timings={}, artifacts=[], reads=[], expected_reads=0, native_captures=0)
    counter = None
    battles = []
    source_files = []
    read_events = {}
    failure = None
    stage = 'preflight'
    def alarm(signum, frame):
        raise RuntimeError('Independent v2 harness 45-second bound exceeded')
    signal.signal(signal.SIGALRM, alarm)
    signal.alarm(45)
    try:
        raw, rec=pinned(HARNESS_OWNER);report['reads'].append(rec)
        harness_owner=json.loads(raw)
        for row in harness_owner['payloads']:
            _, rec=pinned(ROOT/row['path'],row['sha256'],row['size']);report['reads'].append(rec)
        directory=ROOT/SOURCE_BINDING['directory']
        raw,rec=pinned(directory/'owned-files.json',SOURCE_BINDING['owner_sha']);report['reads'].append(rec)
        for row in json.loads(raw)['payloads']:
            _,rec=pinned(ROOT/row['path'],row['sha256'],row['size']);report['reads'].append(rec)
        raw,rec=pinned(directory/'candidate-source-freeze.json',SOURCE_BINDING['freeze_sha']);report['reads'].append(rec)
        source_files=json.loads(raw)['files'];require(len(source_files)==15,'exact15 candidate')
        raw,rec=pinned(REQUESTS,REQUESTS_SHA);report['reads'].append(rec);jobs=json.loads(raw)
        reference_raw,rec=pinned(REFERENCE,REFERENCE_SHA);report['reads'].append(rec)
        require(len(jobs)==2,'exact original2requests')
        report['artifacts'].append(save_json(OUTPUT/'before.json',dict(candidate=source_files,requests_sha=REQUESTS_SHA,reference=rec,harness=harness_owner)))
        allowed={str((ROOT/row['path']).resolve()) for row in source_files}
        allowed.add(str(Path(__file__).resolve()))
        output_root=str(OUTPUT.resolve())+os.sep
        stdlib_root=str(Path(sys.base_prefix).resolve())+os.sep
        def audit(event,args):
            if event=='open' and isinstance(args[0],(str,bytes,os.PathLike)):
                path=os.path.realpath(os.fsdecode(args[0]));mode,flags=args[1],args[2]
                writing=(isinstance(mode,str) and any(x in mode for x in 'wax+')) or (isinstance(flags,int) and flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC))
                if writing:
                    if not path.startswith(output_root):raise PermissionError('write outside v2output: '+path)
                elif path in allowed or path.startswith(stdlib_root) or path.startswith(output_root):
                    read_events[path]=read_events.get(path,0)+1
                else:raise PermissionError('undeclared read blocked: '+path)
            elif event in ('subprocess.Popen','os.system','socket.connect','socket.bind'):
                raise PermissionError('external execution/network blocked: '+event)
        sys.dont_write_bytecode=True
        sys.pycache_prefix=str(OUTPUT/'unused-bytecode-cache')
        sys.path.insert(0,str(directory/'staged'))
        sys.addaudithook(audit)
        stage='import_and_Source_schema_reference_restoration'
        h=importlib.import_module('headless')
        e=importlib.import_module('native_replay_v8.engine')
        state=importlib.import_module('native_replay_v8.state')
        compare=importlib.import_module('native_replay_v8.compare')
        pcg=importlib.import_module('godot_pcg_integer')
        modules={}
        for name,module in list(sys.modules.items()):
            if name in ('headless','godot_pcg_integer','original_rng') or name.startswith(('native_replay_v7','native_replay_v8')):
                path=str(Path(module.__file__).resolve());require(path in allowed,'wrong capsule module: '+name);modules[name]=path
        report['loaded_candidate_modules']=modules
        reference_batch=state.strict_json_loads(reference_raw.decode())
        require(len(reference_batch['jobs'])==2 and all(row['status']=='COMPLETED' for row in reference_batch['jobs']),'frozen completed batch pair')
        restoration_counts=dict(restore_history_json_keys=0,restore_state_json_keys=0,direct_dataclass_integer_tables=0,coordinate_tuples=0,strict_json_roundtrip=0)
        references=[restore_reference_result(row['result'],state,compare,restoration_counts) for row in reference_batch['jobs']]
        report['reference_restoration_direct_helper_calls']=restoration_counts
        report['reference_restoration_basis']='Conserved Source-specific dictionary paths and ItemState coordinate tuple fields; no candidate output consulted.'
        report['timings']['preflight_import_restore_seconds']=time.monotonic()-began
        report['artifacts'].append(save_json(OUTPUT/'restoration.json',dict(counts=restoration_counts,basis=report['reference_restoration_basis'],reference_sha=REFERENCE_SHA)))
        stage='initialize_two_instances'
        t=time.monotonic()
        counter=InvocationCounter({'initialize':h.initialize,'CombatRandom.__init__':h.CombatRandom.__init__,'GodotPCGInteger.__init__':pcg.GodotPCGInteger.__init__,'CombatEngine.__init__':e.CombatEngine.__init__,'prepare_only':e.CombatEngine.prepare_only,'activate_from_checkpoint':e.CombatEngine.activate_from_checkpoint,'source_state_assert':e.CombatEngine._validate_source_pure_state})
        sys.setprofile(counter)
        try:
            for job in jobs:
                report['explicit_public_calls']['initialize']+=1
                battles.append(h.initialize(copy.deepcopy(job['layout']),job['seed']))
        finally:sys.setprofile(None)
        report['initialization_profile_counts']=counter.snapshot()
        require(counter.counts['CombatEngine.__init__']==2 and counter.counts['prepare_only']==2,'two actual constructors/prepares')
        require(battles[0]._engine is not battles[1]._engine and battles[0]._engine.random is not battles[1]._engine.random,'independent actual model/provider identity')
        report['timings']['initialize_seconds']=time.monotonic()-t
        stage='interleave_two_natural_battles'
        t=time.monotonic()
        def done(battle):
            report['explicit_public_calls']['done']+=1
            value=battle.done;require(type(value) is bool,'strict done BOOL');return value
        while not all(done(battle) for battle in battles):
            for index,battle in enumerate(battles):
                if not done(battle):
                    battle.step();report['explicit_public_calls']['step'][index]+=1
            require(max(report['explicit_public_calls']['step'])<=7202,'bounded production quanta')
        require(all(battle._engine.finalized and battle._engine.frame_driver.finalized for battle in battles),'both computed final barriers')
        report['completed_battles']=2
        report['timings']['interleaving_seconds']=time.monotonic()-t
        report['artifacts'].append(save_json(OUTPUT/'completed-pair.json',dict(completed=2,public_steps=report['explicit_public_calls']['step'],actual_passes=[battle._engine.frame_driver.pass_index for battle in battles],actual_rng_states=[battle._engine.random.snapshot() for battle in battles])))
        stage='extract_seal_and_strict_compare'
        comparisons=[];report['comparisons']=comparisons
        for index,(battle,reference) in enumerate(zip(battles,references)):
            per={};t=time.monotonic()
            before_state=stored_state_digest(battle._engine);per['digest_before_seconds']=time.monotonic()-t
            t=time.monotonic()
            require(battle.step() is False and done(battle),'postfinal noadvance')
            report['explicit_public_calls']['step'][index]+=1
            report['explicit_public_calls']['result']+=1
            result=battle.result()
            per['postfinal_result_seconds']=time.monotonic()-t
            t=time.monotonic()
            report['artifacts'].append(save_json(OUTPUT/('interleaved-'+str(index)+'.json'),result))
            per['seal_seconds']=time.monotonic()-t
            t=time.monotonic()
            after_state=stored_state_digest(battle._engine);per['digest_after_seconds']=time.monotonic()-t
            require(before_state['sha256']==after_state['sha256'],'same-instance postfinal/result readonly')
            t=time.monotonic()
            difference=strict_difference(reference,result)
            if difference is not None:
                report['first_difference']=difference
                raise AssertionError('strict complete business comparison difference: '+repr(difference))
            require(strict_difference(reference['source_rng'],result['source_rng']) is None,'strict dualstream final state')
            per['strict_comparison_seconds']=time.monotonic()-t
            terminal=result['source_terminal'];require(terminal['final']['physics_frame']>=terminal['post_cleanup']['physics_frame']+2,'two strictly futurephysics')
            require(terminal['final']['phase']=='idle_pre_internal_flush','final preinternalidle')
            rows=[row for row in result['source_timer_api'] if row['edge']=='before']
            ticks=[row for row in rows if row['operation']=='start' and row['role'].startswith('tick:')]
            require(len(ticks)==2 and all(row['argc']==0 and row['args']==[] for row in ticks),'actual Tick argc0')
            fatigue=[row for row in rows if row['operation']=='start' and row['role'].startswith('fatigue:')]
            require(all(row['argc']==1 and row['args'][0]['type']=='int' and row['args'][0]['decimal'] in ('14','3','1') for row in fatigue),'actual fatigue INT')
            aux=[row['role'] for row in rows if row['operation']=='stop' and row['role'].startswith('aux:')]
            require(aux==['aux:P:battleRageTimer','aux:P:autoRageTimer','aux:O:battleRageTimer','aux:O:autoRageTimer'],'actual4aux sequence')
            require(result['coverage']['formal_support']==75 and 'PENDING' in result['coverage']['native_seed_parity'],'scope honest')
            king=next(item['instance_id'] for side in result['fixture']['sides'] for item in side['items'] if item['item_index']==262)
            history=next(logger['itemStateHistories'][king] for logger in result['histories']['stat_loggers'] if king in logger['itemStateHistories'])
            comparisons.append(dict(index=index,status='PASS_FULL_TYPED_RESULT_AND_DUAL_STREAM_STATE',winner=result['final']['winner'],king=king,king_state_values=history['values'],event_count=len(result['events']),draw_count=len(result['random_inputs']),physics_frames=result['scheduling']['frames'],passes=battle._engine.frame_driver.pass_index,terminal_time=result['final']['timestamp'],actual_auxstops=aux,fatigue_arg_forms=sorted({row['args'][0]['decimal'] for row in fatigue}),readonly_before=before_state,readonly_after=after_state,timings=per))
        report['status']='PASS_REMAINING_PAIR_STRICT_SOURCE_INTERLEAVING_NOT_NATIVE_SEED_VALIDATION'
    except BaseException as exc:
        failure=exc;report['status']='FAIL_FIRST_STOPPED_NO_RETRY'
        report['failure']=dict(stage=stage,type=type(exc).__name__,message=str(exc),traceback=traceback.format_exc())
    finally:
        sys.setprofile(None);signal.alarm(0)
        report['elapsed_seconds']=time.monotonic()-began
        report['actual_models']=len(battles)
        report['completed_battles_observed']=sum(bool(battle._engine.finalized) for battle in battles)
        report['cumulative_natural_completions']=4+report['completed_battles_observed']
        report['runtime_open_read_counts']=read_events
        if counter is not None:report['initialization_only_profile_counts']=counter.snapshot()
        report['profile_scope']='Only initialize2; no profile during stepping/result/deepcopy/digest/serialization. Unprofiled internalcalls are not reported as measuredzero.'
        if failure is not None:
            report['partial_models']=[dict(prepared=b._engine.prepared,activated=b._engine.activated,ended=b._engine.ended,finalized=b._engine.finalized,winner=b._engine.winner,frame=b._engine.frame,elapsed=b._engine.elapsed,pass_index=b._engine.frame_driver.pass_index,rng=b._engine.random.snapshot()) for b in battles]
        after=[]
        for row in source_files:
            try:
                _,rec=pinned(ROOT/row['path'],row['sha256'],row['size']);after.append(rec)
            except BaseException as exc:report.setdefault('source_after_errors',[]).append(str(exc));report['status']='FAIL_SOURCE_DRIFT'
        report['source_after_actual_reads']=after
        save_json(OUTPUT/'result.json',report)
        payloads=[]
        for path in sorted(OUTPUT.glob('*.json')):
            _,rec=pinned(path);payloads.append(rec)
        save_json(OUTPUT/'owned-files.json',dict(schema='phase454-independent-remaining-execution-owner/2',payloads=payloads))
    print(json.dumps(dict(status=report['status'],completed_battles=report['completed_battles_observed'],elapsed_seconds=report['elapsed_seconds'],output=str(OUTPUT))))
    if failure is not None or report['status'].startswith('FAIL'):raise SystemExit(1)


if __name__ == '__main__':
    main()
