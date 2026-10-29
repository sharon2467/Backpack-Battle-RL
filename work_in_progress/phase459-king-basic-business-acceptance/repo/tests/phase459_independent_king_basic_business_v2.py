"""Frozen independent Source-only business controls; executable only as __main__."""
import copy
import functools
import hashlib
import importlib
import json
from pathlib import Path
import signal
import struct
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'data/phase458-source-king-basic'
PLAN = ROOT / 'data/phase459-independent-business-plan'
OUT = ROOT / 'data/phase459-independent-business-v2-first-001'
OWNER = ROOT / 'data/phase459-independent-business-harness-source-v2/owned-files.json'
COUNTS = {}
PASSES = []
PREPARE_BOUNDARIES = []
ACTIVE = None
STAGE = 'preflight'
B, K, R = 'P:basic', 'P:king', 'P:berry0'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def pin(path):
    raw = path.read_bytes()
    return {'path': str(path.relative_to(ROOT)), 'size': len(raw), 'sha256': sha(raw)}


def save(name, value):
    p = OUT / name
    p.write_text(json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(',', ':')) + '\n')
    return pin(p)


def strict(actual, expected, where='$'):
    if type(actual) is not type(expected):
        raise AssertionError((where, 'types', type(actual).__name__, type(expected).__name__))
    if isinstance(actual, float):
        if struct.pack('>d', actual) != struct.pack('>d', expected):
            raise AssertionError((where, actual.hex(), expected.hex()))
    elif isinstance(actual, dict):
        if {(type(k), k) for k in actual} != {(type(k), k) for k in expected}:
            raise AssertionError((where, 'keys', list(actual), list(expected)))
        for k in actual:
            strict(actual[k], expected[k], where + '.' + str(k))
    elif isinstance(actual, (list, tuple)):
        if len(actual) != len(expected):
            raise AssertionError((where, 'length', len(actual), len(expected)))
        for i, (a, b) in enumerate(zip(actual, expected)):
            strict(a, b, where + '[' + str(i) + ']')
    elif actual != expected:
        raise AssertionError((where, actual, expected))


def check(name, details=None):
    row = {'name': name, 'status': 'PASS', 'details': details, 'calls': COUNTS.copy()}
    PASSES.append(row)
    with (OUT / 'controls.jsonl').open('a') as f:
        f.write(json.dumps(row, allow_nan=False) + '\n')


def verify_owner(path, expected=None):
    raw = path.read_bytes()
    if expected is not None:
        assert sha(raw) == expected, str(path)
    owner = json.loads(raw)
    rows = owner.get('payloads', owner.get('files'))
    for row in rows:
        p = ROOT / row['path']
        assert p.is_file() and not p.is_symlink() and p.stat().st_nlink == 1
        strict(pin(p), row, 'pin')
    return rows


def counted(cls, name, label):
    original = getattr(cls, name)

    @functools.wraps(original)
    def call(*args, **kwargs):
        COUNTS[label] = COUNTS.get(label, 0) + 1
        if label == 'Engine.prepare_only':
            engine = args[0]
            before = copy.deepcopy(engine.random.audit)
            answer = original(*args, **kwargs)
            after = copy.deepcopy(engine.random.audit)
            strict(before, [], 'actual_prepare_entry_audit')
            strict(after, [], 'actual_prepare_return_audit')
            PREPARE_BOUNDARIES.append({'before_audit': before, 'after_audit': after,
                'event_num': engine.event_num, 'basic_count': engine.items[B].goobert_activations,
                'basic_trigger': engine.items[B].trigger_time, 'prepared': engine.prepared})
            return answer
        return original(*args, **kwargs)

    setattr(cls, name, call)


def delta(a, b):
    return {k: b.get(k, 0) - a.get(k, 0) for k in a.keys() | b.keys() if b.get(k, 0) != a.get(k, 0)}


def rejects(name, fn):
    before = COUNTS.copy()
    try:
        fn()
    except ValueError as exc:
        strict(delta(before, COUNTS), {}, name + '.zero_compute')
        check(name, {'exception': str(exc), 'zero_rng_engine': True})
    else:
        raise AssertionError(name + ' accepted')


def ingress(h, mod, layout):
    good = copy.deepcopy(layout)
    fixture = h.validate_layout(good)
    strict(mod.validate_source_pure_business_domain(fixture), mod.SOURCE_KING_BASIC_PROFILE)
    topology = h.source_runtime_topology(fixture)
    strict(len(topology['timer_initial']), 33)
    legacy = copy.deepcopy(layout)
    legacy['sides'][0]['items'] = [i for i in legacy['sides'][0]['items'] if i['instance_id'] != B]
    strict(mod.validate_source_pure_business_domain(h.validate_layout(legacy)), mod.SOURCE_PURE_PROFILE)
    opposite = copy.deepcopy(layout)
    for i, old in enumerate(reversed(copy.deepcopy(layout['sides']))):
        side = ('P', 'O')[i]
        old['side'] = side
        for item in old['items']:
            item['instance_id'] = side + ':' + item['instance_id'].split(':', 1)[1]
        opposite['sides'][i] = old
    strict(mod.validate_source_pure_business_domain(h.validate_layout(opposite)), mod.SOURCE_KING_BASIC_PROFILE)
    strict(COUNTS, {}, 'validator_no_compute')
    check('P_and_O_domain_33Timers_old_six_profile_no_compute')
    bads = {}
    v = copy.deepcopy(layout)
    moved = next(i for i in v['sides'][0]['items'] if i['instance_id'] == B)
    v['sides'][0]['items'].remove(moved)
    moved.update(instance_id='O:basic', x=4, y=2)
    v['sides'][1]['items'].append(moved)
    bads['enemy_basic'] = v
    v = copy.deepcopy(layout)
    next(i for i in v['sides'][0]['items'] if i['instance_id'] == 'P:berry3').update(item_index=23, instance_id='P:basic2', x=4, y=2)
    bads['second_basic'] = v
    v = copy.deepcopy(layout)
    v['sides'][0]['items'] = [i for i in v['sides'][0]['items'] if i['instance_id'] != 'P:berry3']
    next(i for i in v['sides'][0]['items'] if i['instance_id'] == B).update(item_index=262)
    bads['second_king'] = v
    for name, change in (
        ('other_goobert38', lambda v: next(i for i in v['sides'][0]['items'] if i['instance_id'] == B).update(item_index=38)),
        ('class2', lambda v: v['sides'][0].update(character_class=2)),
        ('rage129', lambda v: v['sides'][0]['items'][0].update(item_index=129)),
        ('bool_item_index', lambda v: next(i for i in v['sides'][0]['items'] if i['instance_id'] == B).update(item_index=True)),
        ('duplicate_identity', lambda v: next(i for i in v['sides'][0]['items'] if i['instance_id'] == B).update(instance_id=K)),
        ('overlap', lambda v: next(i for i in v['sides'][0]['items'] if i['instance_id'] == B).update(x=2)),
        ('nondefault_power', lambda v: next(i for i in v['sides'][0]['items'] if i['instance_id'] == B).update(power=2)),
    ):
        v = copy.deepcopy(layout)
        change(v)
        bads[name] = v
    for name, bad in bads.items():
        rejects('ingress_' + name, lambda bad=bad: h.initialize(bad, 45701))
    rejects('batch_bad_second_zero_partial', lambda: h.run_batch([
        {'layout': layout, 'seed': 45701}, {'layout': bads['enemy_basic'], 'seed': 45701}], keep_results=True))


def history(e, identity):
    return e.histories.logger('P')['itemTooltipHistories'][identity][9]


def point(e):
    return {'events': len(e.events), 'allocated': e.event_num, 'api': len(e.pure_api_trace),
            'hist': {i: len(history(e, i).values) for i in (B, K)},
            'metrics': {i: e.histories.item_metrics[i][4] for i in (B, K, R)}}


def unit(h, mod, Tape, layout, name, pitch=False, basic=4, king=5, mana=4, charges=3, invulnerable=False):
    global ACTIVE
    battle = h.initialize(layout, 45701)
    e = battle._engine
    ACTIVE = e
    # Public initialize includes real activation cooldown draws. Preserve, never clear.
    activation_audit = copy.deepcopy(e.random.audit)
    labels = ['cooldown:' + identity for identity in e.preparation_order if e.items[identity].has_cooldown]
    strict([row['label'] for row in activation_audit], labels, 'activation_labels')
    strict(len(activation_audit), 10, 'fixed_unit_initialization_draw_count')
    for row in activation_audit:
        strict(set(row), {'kind', 'label', 'args', 'value_bits'})
        strict(row['kind'], 'randf_range')
        strict(row['args'], [struct.pack('>d', x).hex() for x in (0.95, 1.05)])
        value = struct.unpack('>d', bytes.fromhex(row['value_bits']))[0]
        assert 0.95 <= value <= 1.05
    save(name + '.initialize.json', {'synthetic_cut_not_native': True,
         'actual_prepare_boundary': copy.deepcopy(PREPARE_BOUNDARIES[-1]),
         'activation_audit': activation_audit, 'source_rng_before_test_provider': e.random.snapshot(),
         'preparation_order': e.preparation_order.copy(), 'calls': COUNTS.copy()})
    strict(battle.initialization['profile'], mod.SOURCE_KING_BASIC_PROFILE)
    strict(e.items[B].goobert_activations, 0)
    strict(e.items[B].iteration_cooldown, 5.0)
    strict(e.items[B].trigger_time, 5.0)
    strict(e.activation_listeners[K], [B])
    strict(e.activation_listeners[B], [K])
    strict(e.activation_listeners[R], [K])
    for emitter, receivers in e.activation_listeners.items():
        assert len(receivers) == len(set(receivers)), emitter
    strict(len(e.runtime_inputs.data), 13)
    e.util_time = 1.0
    c = e.characters['P']
    c.hp = 100.0
    c.mana = mana
    c.buff_protect_stacks = 0
    c.invulnerable = invulnerable
    fields, _ = e._buff_record('P', 'Mana')
    fields['permanentStacks'] = mana
    fields['temporaryStacks'].clear()
    e.histories.character('P', 0)
    e.histories.stack('P', mod.EVENT_TYPES['Mana'])
    e.king_states[K]['invuCharges'] = charges
    for identity, count, threshold in ((B, basic, 5.0), (K, king, 6.0)):
        item = e.items[identity]
        item.goobert_activations = count
        item.trigger_time = threshold - count
        item.iteration_cooldown = threshold
        item.cooldown_active = False
        item.activations_this_frame = 0
        item.last_activation_time = 0.0
        e.histories.tooltip(item, 9)
    records = ([{'kind': 'randf_range', 'label': 'invulnerability_pitch:' + K,
                 'args': [struct.pack('>d', x).hex() for x in (0.9, 1.1)],
                 'value_bits': struct.pack('>d', 1.0).hex()}] if pitch else [])
    e.random = Tape(records)
    trail = []
    pitch_call = e.random.randf_range
    def observe_pitch(label, low, high):
        trail.append({'edge': 'enter', 'method': 'randf_range', 'subject': label, 'event_num': e.event_num})
        return pitch_call(label, low, high)
    e.random.randf_range = observe_pitch
    for method in ('on_goobert_item_activated', 'activate', 'king_effect', 'heal', 'change_buff_protect_stacks',
                   'make_invulnerable', 'use_stack', '_start_timer'):
        original = getattr(e, method)
        def wrap(*args, _m=method, _f=original, **kwargs):
            identity = getattr(args[0], 'instance_id', args[0]) if args else None
            trail.append({'edge': 'enter', 'method': _m, 'subject': identity, 'event_num': e.event_num})
            result = _f(*args, **kwargs)
            trail.append({'edge': 'return', 'method': _m, 'subject': identity, 'event_num': e.event_num})
            return result
        setattr(e, method, wrap)
    return battle, e, trail


def projected_events(e, baseline, event_id, mod):
    names = {v: k for k, v in mod.EVENT_TYPES.items()}
    return [{'offset': x['id'] - event_id, 'origin': x['origin'], 'type': names[x['type']],
             'params': x['params'], 'parent_offset': None if x['parent'] is None else x['parent'] - event_id,
             'target': x['target']} for x in e.events[baseline['events']:]]


def business(e):
    return {'basic_count': e.items[B].goobert_activations, 'king_count': e.items[K].goobert_activations,
            'basic_trigger': e.items[B].trigger_time, 'king_trigger': e.items[K].trigger_time,
            'hp': e.characters['P'].hp, 'mana': e.characters['P'].mana,
            'protection': e.characters['P'].buff_protect_stacks, 'charges': e.king_states[K]['invuCharges'],
            'invulnerable': e.characters['P'].invulnerable,
            'histories': {i: history(e, i).snapshot() for i in (B, K)},
            'metrics': {i: copy.deepcopy(e.histories.item_metrics[i]) for i in (B, K, R)},
            'provider_audit': copy.deepcopy(e.random.audit)}


def save_unit(name, e, trail, start, mod):
    save(name + '.json', {'status': 'ACTION_RETURNED_PENDING_ASSERTIONS', 'synthetic_unit': True,
        'baseline': start, 'business': business(e), 'events': copy.deepcopy(e.events[start['events']:]),
        'event_references': e.event_references(), 'api': copy.deepcopy(e.pure_api_trace[start['api']:]),
        'calls': trail, 'counts': COUNTS.copy()})


def positive(h, mod, Tape, layout, expected, which):
    _, e, trail = unit(h, mod, Tape, layout, which, pitch=True)
    start = point(e)
    if which == 'basic_first':
        event = e.emit(K, 'Activation')
        e.on_goobert_item_activated(e.items[B], event)
    else:
        e.activate(e.items[R])
    event_id = start['allocated'] + 1
    save_unit(which, e, trail, start, mod)
    spec = expected[which]
    strict(projected_events(e, start, event_id, mod), spec['events'], which + '.events')
    strict(e.event_num - start['allocated'], 7)
    for i in (B, K):
        strict(e.items[i].goobert_activations, spec['final_counters'][i])
        strict(e.items[i].trigger_time, spec['final_triggers'][i])
        hist = history(e, i)
        rows = [{'event_offset': n - event_id, 'value': value} for n, value in
                zip(hist.event_numbers[start['hist'][i]:], hist.values[start['hist'][i]:])]
        strict(rows, spec['cooldown_history_appends'][i], which + '.history.' + i)
        strict(e.histories.item_metrics[i][4] - start['metrics'][i], 1)
        strict(e.histories.logger('P')['itemMetricHistories'][i][4].event_numbers[-1], event_id + 6)
    strict(e.characters['P'].hp, 144.0)
    strict(e.characters['P'].mana, 0)
    strict(e.characters['P'].buff_protect_stacks, 3)
    strict(e.characters['P'].invulnerable, True)
    strict(e.king_states[K]['invuCharges'], 2)
    strict(e.items[B].healing, 9.0)
    strict(e.items[K].healing, 35.0)
    strict(e.items[B].overheal, 0.0)
    strict(e.items[K].overheal, 0.0)
    strict(e._buff_record('P', 'Mana')[0]['permanentStacks'], 0)
    strict(e.random.position, 1)
    strict(e.random.audit, e.random.records)
    before = [x for x in e.pure_api_trace[start['api']:] if x['edge'] == 'before']
    strict([x['role'] for x in before], ['invu:P', 'king_buff:' + K])
    for row in before:
        strict(row['argc'], 1)
        strict(row['operation'], 'start')
        strict(row['args'], [{'type': 'float', 'binary64_be': struct.pack('>d', 1.5).hex()}])
    for role in ('invu:P', 'king_buff:' + K):
        strict(e.runtime_roles[role].private_left, 1.5)
        strict(e.runtime_roles[role].processing, True)
    # Actual Mana reference only; synchronous Health/Activation are not fabricated parents.
    invu = next(x['id'] for x in e.events[start['events']:] if x['type'] == mod.EVENT_TYPES['InvulnerableStart'])
    mana = next(x['id'] for x in e.events[start['events']:] if x['type'] == mod.EVENT_TYPES['Mana'])
    strict(e.allocated_events[mana]['parent'], invu)
    enters = [(x['method'], x['subject']) for x in trail if x['edge'] == 'enter']
    expected_chain = ([("on_goobert_item_activated", B), ("on_goobert_item_activated", K), ("on_goobert_item_activated", B)]
                      if which == 'basic_first' else
                      [("on_goobert_item_activated", K), ("on_goobert_item_activated", B), ("on_goobert_item_activated", K)])
    strict([x for x in enters if x[0] == 'on_goobert_item_activated'], expected_chain)
    king_effect_start = enters.index(('king_effect', K))
    expected_effect_order = [('king_effect', K), ('change_buff_protect_stacks', 'P'), ('heal', 'P'),
        ('make_invulnerable', K), ('_start_timer', 'invu:P'),
        ('randf_range', 'invulnerability_pitch:' + K), ('_start_timer', 'king_buff:' + K), ('use_stack', K)]
    strict(enters[king_effect_start:king_effect_start + len(expected_effect_order)], expected_effect_order)
    check(which + '_actual_reentry_events_history_mana_rng', {'trigger': spec['final_triggers'], 'pitch': 1, 'events': 7})


def short_circuits(h, mod, Tape, layout):
    for name, options in [('zero_charges', {'charges': 0}), ('insufficient_mana', {'mana': 3}),
                          ('already_invulnerable', {'invulnerable': True})]:
        _, e, trail = unit(h, mod, Tape, layout, name, basic=0, **options)
        start = point(e)
        e.activate(e.items[R])
        save_unit(name, e, trail, start, mod)
        strict([x['type'] for x in e.events[start['events']:]],
               [mod.EVENT_TYPES[x] for x in ('Activation', 'Health', 'Activation')])
        strict(e.characters['P'].hp, 135.0)
        strict(e.characters['P'].buff_protect_stacks, 3)
        strict(e.characters['P'].mana, options.get('mana', 4))
        strict(e.characters['P'].invulnerable, options.get('invulnerable', False))
        strict(e.king_states[K]['invuCharges'], options.get('charges', 3))
        strict(e.items[B].goobert_activations, 1)
        strict(e.items[K].goobert_activations, 0)
        strict(e.random.position, 0)
        strict(len(e.pure_api_trace), start['api'])
        check(name + '_protect_heal_activate_without_invu_rng')


def nontrigger_limiter_end(h, mod, Tape, layout):
    _, e, trail = unit(h, mod, Tape, layout, 'nontrigger', basic=0, king=0)
    start = point(e)
    event = e.emit(K, 'Activation')
    e.on_goobert_item_activated(e.items[B], event)
    save_unit('nontrigger', e, trail, start, mod)
    strict(e.items[B].goobert_activations, 1)
    strict(e.items[B].trigger_time, 4.0)
    strict(len(e.events) - start['events'], 1)
    strict(e.characters['P'].hp, 100.0)
    strict(e.random.position, 0)
    check('nonthreshold_no_effect_or_rng')
    _, e, trail = unit(h, mod, Tape, layout, 'limiter', king=0)
    start = point(e)
    for _ in range(4):
        e.items[B].goobert_activations = 4
        e.items[B].trigger_time = 1.0
        event = e.emit(K, 'Activation')  # four separately identified input carriers
        e.on_goobert_item_activated(e.items[B], event)
    save_unit('limiter', e, trail, start, mod)
    generated = [x for x in e.events[start['events']:] if x['origin'] == B]
    strict([x['type'] for x in generated], [mod.EVENT_TYPES[x] for x in
        ('Health', 'Activation', 'Health', 'Activation', 'Health', 'Activation', 'Health')])
    strict(e.items[K].goobert_activations, 3)
    strict(e.items[B].activations_this_frame, 4)
    strict(e.histories.item_metrics[B][4] - start['metrics'][B], 3)
    strict(e.characters['P'].hp, 136.0)
    strict(e.random.position, 0)
    check('fourth_effect_survives_activation_limiter')
    _, e, trail = unit(h, mod, Tape, layout, 'ended_boundary', basic=0, king=0)
    start = point(e)
    e.activation_listeners[R] = [K, B]  # explicit synthetic scheduler boundary, not layout membership
    delegate = e.on_goobert_item_activated
    def terminate_after_first(item, event):
        answer = delegate(item, event)
        e.ended = True
        return answer
    e.on_goobert_item_activated = terminate_after_first
    e.activate(e.items[R])
    save_unit('ended_boundary', e, trail, start, mod)
    strict(e.items[K].goobert_activations, 1)
    strict(e.items[B].goobert_activations, 0)
    strict(e.histories.item_metrics[R][4] - start['metrics'][R], 1)
    strict(len(e.events) - start['events'], 1)
    check('synthetic_ended_breaks_next_listener_but_outer_metric_survives', {'native_death_hit': False})
    before = (len(e.events), e.event_num, copy.deepcopy(e.histories.item_metrics[R]), len(trail))
    old_counter = e.items[R].activations_this_frame
    e.activate(e.items[R])
    strict((len(e.events), e.event_num, e.histories.item_metrics[R]), before[:3])
    strict(e.items[R].activations_this_frame, old_counter + 1)
    check('already_ended_no_event_metric_receiver')


def integration(h, mod, layout, seed):
    global ACTIVE
    before = COUNTS.copy()
    battle = h.initialize(layout, seed)
    e = battle._engine
    ACTIVE = e
    branches = []
    depth = 0
    original = e.on_goobert_item_activated
    def watch(item, event):
        nonlocal depth
        depth += 1
        prior = item.goobert_activations
        try:
            answer = original(item, event)
            if item.instance_id in (B, K):
                branches.append({'item': item.instance_id, 'depth': depth, 'before': prior,
                    'after': item.goobert_activations, 'trigger': item.trigger_time,
                    'event': event['id'], 'return_event': e.event_num})
            return answer
        finally:
            depth -= 1
    e.on_goobert_item_activated = watch
    result = battle.run(max_seconds=120.0)
    output_pin = save('source-model-output.json', result)
    save('natural-branch-ledger.json', branches)
    strict(battle.done, True)
    strict(len(e.runtime_inputs.data['timer_initial']), 33)
    strict(result['coverage']['status'], 'SOURCE_PURE_KING_BASIC_GOOBERT_NOT_JOINT_NATIVE_VALIDATED')
    strict(result['initialization']['profile'], mod.SOURCE_KING_BASIC_PROFILE)
    strict(result['source_rng'], e.random.snapshot())
    strict(result['random_inputs'], e.random.audit)
    assert e.frame_driver.finalized
    save('integration-summary.json', {'status': 'SOURCE_INTEGRATION_COMPLETED_NOT_NATIVE_JOINT_VALIDATED',
        'output': output_pin, 'calls': delta(before, COUNTS), 'events': len(e.events),
        'rng_draws': len(e.random.audit), 'branches': len(branches),
        'nested_handler_returns': sum(x['depth'] > 1 for x in branches),
        'timers': 33, 'source_rng': e.random.snapshot(), 'root_seed': seed,
        'fixed_layout_unchanged': True, 'winner_not_preselected': True})
    check('one_fixed_26item_Source_battle_complete', {'events': len(e.events), 'rng': len(e.random.audit), 'nested': sum(x['depth'] > 1 for x in branches)})


def main():
    global STAGE
    started = time.monotonic()
    OUT.mkdir(exist_ok=False)
    status = 'FAILED'
    source_rows = []
    try:
        verify_owner(OWNER)
        verify_owner(PLAN / 'owned-files.json', '8b58ee8f508880c673229c573b294431b080b61b2b0e1743b2e719d72e9b76a5')
        source_rows = verify_owner(SOURCE / 'owned-files.json', '772ba31a3f7b9bb39ccfca59543aca19ea833ac7fc7b529931766bf7342bada4')
        fixture = json.loads((PLAN / 'source-job.json').read_text())
        expected = json.loads((PLAN / 'expectations.json').read_text())
        sys.dont_write_bytecode = True
        sys.pycache_prefix = str(OUT / 'unused-bytecode-cache')
        sys.path.insert(0, str(SOURCE / 'staged'))
        STAGE = 'import_frozen_candidate'
        h = importlib.import_module('headless')
        mod = importlib.import_module('native_replay_v8.engine')
        Tape = importlib.import_module('native_replay_v8.randomness').TapeRandom
        imports = []
        allowed = {str((ROOT / r['path']).resolve()) for r in source_rows if '/staged/' in r['path']}
        for name, module in list(sys.modules.items()):
            if name in ('headless', 'original_rng', 'godot_pcg_integer') or name.startswith(('native_replay_v7', 'native_replay_v8')):
                path = str(Path(module.__file__).resolve())
                assert path in allowed, (name, path)
                imports.append({'name': name, 'path': path})
        save('imports.json', imports)
        for cls, method, label in [(h.CombatRandom, '__init__', 'CombatRandom.__init__'),
                (h.GodotPCGInteger, '__init__', 'GodotPCGInteger.__init__'),
                (mod.CombatEngine, '__init__', 'Engine.__init__'),
                (mod.CombatEngine, 'prepare_only', 'Engine.prepare_only'),
                (mod.CombatEngine, 'activate_from_checkpoint', 'Engine.activate_from_checkpoint'),
                (mod.CombatEngine, 'activate', 'Engine.activate'),
                (mod.CombatEngine, 'on_goobert_item_activated', 'Engine.on_goobert_item_activated'),
                (mod.CombatEngine, 'king_effect', 'Engine.king_effect'),
                (mod.CombatEngine, 'heal', 'Engine.heal'),
                (mod.CombatEngine, 'run', 'Engine.run'),
                (mod.CombatEngine, 'step', 'Engine.step')]:
            counted(cls, method, label)
        STAGE = 'reuse_sealed_twelve_passed_ingress_controls'
        old = ROOT / 'data/phase459-independent-business-first-001'
        old_owner_sha = json.loads((OWNER.parent / 'contract.json').read_text())['passed_prefix_owner']['sha256']
        verify_owner(old / 'owned-files.json', old_owner_sha)
        old_result = json.loads((old / 'result.json').read_text())
        strict(old_result['passed_controls'], 12)
        strict(old_result['stage'], 'basic_first')
        save('reused-prefix.json', {'actual_owner': pin(old / 'owned-files.json'),
             'passed_controls': 12, 'rerun': False, 'prior_ctor': 1, 'prior_prepare': 1,
             'prior_activate_entries': 2, 'prior_activation_draws': 10})
        STAGE = 'basic_first'
        positive(h, mod, Tape, fixture['layout'], expected, STAGE)
        STAGE = 'king_first'
        positive(h, mod, Tape, fixture['layout'], expected, STAGE)
        STAGE = 'King_short_circuits'
        short_circuits(h, mod, Tape, fixture['layout'])
        STAGE = 'nontrigger_limiter_ended'
        nontrigger_limiter_end(h, mod, Tape, fixture['layout'])
        STAGE = 'one_fixed_integration'
        integration(h, mod, fixture['layout'], fixture['source_root_seed'])
        status = 'PASS_SOURCE_BUSINESS_COMPONENTS_AND_ONE_FIXED_INTEGRATION_NOT_NATIVE_JOINT'
    except BaseException as exc:
        save('first-error.json', {'stage': STAGE, 'type': type(exc).__name__, 'message': str(exc),
            'traceback': traceback.format_exc(), 'calls': COUNTS.copy()})
        if ACTIVE is not None:
            try:
                save('same-instance-failure-state.json', {'business': business(ACTIVE),
                     'events': ACTIVE.events, 'allocated_event_num': ACTIVE.event_num,
                     'api': ACTIVE.pure_api_trace, 'source_frames': getattr(ACTIVE, 'frame', None)})
            except BaseException as secondary:
                save('failure-diagnostic-error.json', {'type': type(secondary).__name__, 'message': str(secondary)})
    finally:
        signal.alarm(0)
        after = []
        for row in source_rows:
            actual = pin(ROOT / row['path'])
            strict(actual, row, 'after_source')
            after.append(actual)
        save('source-after.json', after)
        save('actual-prepare-boundaries.json', PREPARE_BOUNDARIES)
        save('result.json', {'status': status, 'stage': STAGE, 'wall_seconds': time.monotonic() - started,
            'passed_controls': len(PASSES), 'reused_prefix_controls': 12, 'calls': COUNTS, 'native_runs': 0, 'Expected_reads': 0,
            'old_tests': 0, 'source_payloads_unchanged': len(after), 'no_auto_retry': True})
        files = [pin(p) for p in sorted(OUT.iterdir()) if p.is_file()]
        save('owned-files.json', {'schema': 'phase459-independent-actual-owner/1', 'files': files, 'no_more_writes': True})
    print(json.dumps({'status': status, 'stage': STAGE, 'passed_controls': len(PASSES), 'calls': COUNTS}))
    return 0 if status.startswith('PASS') else 1


if __name__ == '__main__':
    def timed_out(signum, frame):
        raise TimeoutError('independent harness wall limit40s')
    signal.signal(signal.SIGALRM, timed_out)
    signal.alarm(40)
    sys.exit(main())
