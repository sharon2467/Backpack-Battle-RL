"""Independent finite Source component controls. No native, Expected or prior test runs."""
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
SOURCE = ROOT / 'data/phase482-source-king-mirror-poison-v2'
PLAN = ROOT / 'data/phase483-independent-business-plan'
OWN = ROOT / 'data/phase483-independent-harness-source/owned-files.json'
OUT = ROOT / 'data/phase483-independent-business-first-001'
COUNTS, PASSES, PREPARES = {}, [], []
ACTIVE = None
STAGE = 'preflight'
K, M, F = 'P:king', 'P:mirror', 'O:fly'
POSITIVE = ('Lucky', 'Regeneration', 'Vampirism', 'Spikes', 'Mana', 'Empower', 'Heat')

def sha(b):
    return hashlib.sha256(b).hexdigest()

def pin(p):
    b = p.read_bytes()
    return dict(path=str(p.relative_to(ROOT)), size=len(b), sha256=sha(b))

def save(name, value):
    p = OUT / name
    p.write_text(json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(',', ':')) + '\n')
    return pin(p)

def strict(a, b, where='$'):
    assert type(a) is type(b), (where, type(a).__name__, type(b).__name__)
    if isinstance(a, float):
        assert struct.pack('>d', a) == struct.pack('>d', b), (where, a, b)
    elif isinstance(a, dict):
        assert {(type(k), k) for k in a} == {(type(k), k) for k in b}, (where, list(a), list(b))
        for k in a: strict(a[k], b[k], where + '.' + str(k))
    elif isinstance(a, (list, tuple)):
        assert len(a) == len(b), (where, len(a), len(b))
        for i, (x, y) in enumerate(zip(a, b)): strict(x, y, where + '[' + str(i) + ']')
    else: assert a == b, (where, a, b)

def verify_owner(path, expected=None):
    raw = path.read_bytes()
    if expected: strict(sha(raw), expected)
    rows = json.loads(raw)['files']
    for row in rows:
        p = ROOT / row['path']
        assert p.is_file() and not p.is_symlink() and p.stat().st_nlink == 1
        strict(pin(p), row, 'pin')
    return rows

def check(name, details=None):
    row = dict(name=name, status='PASS', details=details, calls=COUNTS.copy())
    PASSES.append(row)
    with (OUT / 'controls.jsonl').open('a') as f: f.write(json.dumps(row, allow_nan=False) + '\n')

def counted(obj, name, label):
    original = getattr(obj, name)
    @functools.wraps(original)
    def invoke(*a, **kw):
        COUNTS[label] = COUNTS.get(label, 0) + 1
        if label == 'Engine.prepare_only':
            e = a[0]
            strict(e.random.audit, [], 'prepare_entry_combat_audit')
            result = original(*a, **kw)
            strict(e.random.audit, [], 'prepare_return_combat_audit')
            strict([x.instance_id for x in e.affected_items(e.items[M])], [K], 'one_Holy_target')
            strict(e.activation_listeners[M], [K], 'one_King_listener')
            for kind in ('Blind', 'Poison', 'Cold'):
                strict(e._buff_record('P', kind)[0]['reflectChancePercent'], 22.0, 'prepared_reflection')
            strict(len(e.runtime_inputs.data), 13)
            strict(len(e.runtime_inputs.data['timer_initial']), 33)
            PREPARES.append(dict(audit=copy.deepcopy(e.random.audit), rng=e.random.snapshot(),
                profile=e.runtime_inputs.data['profile_id'], reflection=22.0, Holy=[K], timers=33))
            return result
        return original(*a, **kw)
    setattr(obj, name, invoke)

def reject(name, fn):
    before = COUNTS.copy()
    try: fn()
    except ValueError as exc:
        strict(COUNTS, before, name + '.zero_compute')
        check(name, dict(exception=str(exc), no_rng_or_engine=True))
    else: raise AssertionError(name + ' accepted')

def ingress(h, mod, layout):
    fixture = h.validate_layout(copy.deepcopy(layout))
    strict(mod.validate_source_pure_business_domain(fixture), mod.SOURCE_KING_MIRROR_POISON_PROFILE)
    strict(len(h.source_runtime_topology(fixture)['timer_initial']), 33)
    check('01_valid_P_domain')
    opposite = copy.deepcopy(layout)
    for i, side in enumerate(reversed(copy.deepcopy(layout['sides']))):
        identity = ('P', 'O')[i]; side['side'] = identity
        for item in side['items']: item['instance_id'] = identity + ':' + item['instance_id'].split(':', 1)[1]
        opposite['sides'][i] = side
    strict(mod.validate_source_pure_business_domain(h.validate_layout(opposite)), mod.SOURCE_KING_MIRROR_POISON_PROFILE)
    check('02_valid_O_domain')
    legacy = copy.deepcopy(layout)
    legacy['sides'][0]['items'] = [x for x in legacy['sides'][0]['items'] if x['instance_id'] != K]
    assert not mod._has_king(h.validate_layout(legacy))
    check('03_nonKing_21_332_formal_route')
    def removed(identity):
        value = copy.deepcopy(layout)
        for side in value['sides']: side['items'] = [x for x in side['items'] if x['instance_id'] != identity]
        return value
    bad_mirror, bad_fly = removed(M), removed(F)
    reject('04_missing_Mirror', lambda: h.validate_layout(bad_mirror))
    reject('05_missing_Fly', lambda: h.validate_layout(bad_fly))
    wrong_mirror = copy.deepcopy(layout)
    x = next(x for x in wrong_mirror['sides'][0]['items'] if x['instance_id'] == M)
    wrong_mirror['sides'][0]['items'].remove(x); x.update(instance_id='O:mirror', x=5, y=2)
    wrong_mirror['sides'][1]['items'].append(x)
    reject('06_wrong_Mirror_side', lambda: h.validate_layout(wrong_mirror))
    wrong_fly = copy.deepcopy(layout)
    x = next(x for x in wrong_fly['sides'][1]['items'] if x['instance_id'] == F)
    wrong_fly['sides'][1]['items'].remove(x); x.update(instance_id='P:fly', x=5, y=2)
    wrong_fly['sides'][0]['items'].append(x)
    reject('07_wrong_Fly_side', lambda: h.validate_layout(wrong_fly))
    duplicate = copy.deepcopy(layout)
    duplicate['sides'][0]['items'].append(dict(item_index=332, x=5, y=0, f=0, instance_id='P:mirror2'))
    reject('08_second_Mirror', lambda: h.validate_layout(duplicate))
    basic = removed('P:berry3')
    basic['sides'][0]['items'].append(dict(item_index=23, x=4, y=2, f=0, instance_id='P:basic'))
    reject('09_additional_Basic', lambda: h.validate_layout(basic))
    reject('10_bad_second_batch_atomic', lambda: h.run_batch([
        dict(layout=layout, seed=48301), dict(layout=bad_mirror, seed=48301)], keep_results=True))
    strict(COUNTS, {}, 'all_ingress_zero_compute')

# Test-owned exact-row provider, never supplied through a public Source API.
def bits(v): return struct.pack('>d', float(v)).hex()
def fl(label, lo, hi, value):
    return dict(kind='randf_range', label=label, args=[bits(lo), bits(hi)], value_bits=bits(value))
def cooldown(identity): return fl('cooldown:' + identity, .975 if identity.startswith('O:') else .95, 1.05, 1.0)
def reflection(value): return fl('reflect:P:O:fly:Poison', 0.0, 100.0, value)
def shuffle():
    context = 'fraction_shuffle:P:mirror:P:multiply'
    return [dict(kind='global_u32', label=f'{context}:{i}:{7-i}', args=[], value=0,
                 context=context, ordinal=i, width=7-i) for i in range(6)]
def poison(): return dict(kind='randi_range', label='poison:P', args=[1, 1], value=1)

class UnitTape:
    """Finite rows fixed before action; exact types/float bits, no random fallback."""
    def __init__(self, rows): self.rows, self.audit, self.position = copy.deepcopy(rows), [], 0
    def take(self, kind, label, args, **extra):
        assert self.position < len(self.rows), ('unit_tape_exhausted', label)
        row = self.rows[self.position]
        output_key = 'value_bits' if kind.startswith('randf') else 'value'
        strict({k: v for k, v in row.items() if k != output_key}, dict(kind=kind, label=label, args=args, **extra))
        self.position += 1; self.audit.append(copy.deepcopy(row))
        return struct.unpack('>d', bytes.fromhex(row[output_key]))[0] if output_key == 'value_bits' else row[output_key]
    def randf_range(self, label, low, high): return self.take('randf_range', label, [bits(low), bits(high)])
    def randf(self, label): return self.take('randf', label, [])
    def randi_range(self, label, low, high): return self.take('randi_range', label, [low, high])
    def global_u32(self, label, context, ordinal, width):
        strict(context, 'fraction_shuffle:P:mirror:P:multiply')
        strict(width, 7 - ordinal); assert type(ordinal) is int and 0 <= ordinal <= 5
        return self.take('global_u32', label, [], context=context, ordinal=ordinal, width=width)
    def assert_consumed(self): strict(self.position, len(self.rows), 'unit_all_rows_consumed')

def unit(h, layout, name):
    global ACTIVE
    b = h.initialize(layout, 48301); e = b._engine; ACTIVE = e
    strict(b.initialization['profile'], 'source-headless-king-mirror-poison-fixed60/1')
    labels = ['cooldown:' + i for i in e.preparation_order if e.items[i].has_cooldown]
    strict([r['label'] for r in e.random.audit], labels)
    for row in e.random.audit:
        identity = row['label'].removeprefix('cooldown:')
        strict(row['kind'], 'randf_range')
        strict(row['args'], cooldown(identity)['args'])
    save(name + '.initialize.json', dict(synthetic_cut_not_native=True, actual_prepare=PREPARES[-1],
        initialization_audit=e.random.audit, original_source_rng=e.random.snapshot(), order=e.preparation_order))
    e.util_time = 1.0
    return e

def stacks(e, side, values):
    for kind, value in values.items():
        assert type(value) is int
        setattr(e.characters[side], kind.lower(), value)
        fields, _ = e._buff_record(side, kind)
        fields['permanentStacks'] = value; fields['temporaryStacks'].clear()

def prestate(e, name, values):
    save(name + '.prestate.json', dict(synthetic=True, assignments=values, hp=e.characters['P'].hp,
        stacks={s: {k: getattr(e.characters[s], k.lower()) for k in POSITIVE + ('Poison',)} for s in ('P','O')},
        protection=e.characters['P'].buff_protect_stacks, event_num=e.event_num))

def segment(e, name, rows, action):
    global STAGE
    STAGE = name
    start = len(e.events); api = len(e.pure_api_trace)
    e.random = UnitTape(rows)
    value = action()
    events = copy.deepcopy(e.events[start:])
    save(name + '.actual.json', dict(synthetic=True, events=events, audit=e.random.audit,
        tape_position=e.random.position, return_value=value, snapshot=e.snapshot(), histories=e.histories.snapshot(),
        api=e.pure_api_trace[api:], calls=COUNTS.copy()))
    e.random.assert_consumed()
    return value, events

def types(events): return [x['type'] for x in events]

def components(h, mod, layout):
    global STAGE
    E = mod.EVENT_TYPES
    STAGE = 'A_initialize'
    e = unit(h, layout, 'A')
    stacks(e, 'P', {k: 0 for k in POSITIVE}); e.characters['P'].buff_protect_stacks = 3
    strict(e.items[K].goobert_activations, 0)
    prestate(e, 'A_zero', {'seven_positive_stacks': 0, 'protection': 3, 'util_time': 1.0})
    _, ev = segment(e, '11_Mirror_zero_full_caller', [cooldown(M)], lambda: e.trigger(e.items[M]))
    strict(types(ev), [E['Activation']]); strict(ev[0]['origin'], M)
    strict(e.items[K].goobert_activations, 1); strict(e.characters['P'].buff_protect_stacks, 3)
    strict(e.items[M].consumed, True); strict(e.items[M].cooldown_active, False)
    check('11_zero_helper_retains_full_caller', dict(activation=ev, shuffle_calls=0))

    STAGE = 'B_initialize'
    e = unit(h, layout, 'B')
    stacks(e, 'P', {k: 100 for k in POSITIVE}); e.characters['P'].buff_protect_stacks = 3
    prestate(e, 'B_cap', {'seven_positive_stacks': 100, 'protection': 3, 'Vampirism_synthetic_only': True})
    allocation, ev = segment(e, '12_Mirror_cap_helper', shuffle(), lambda: e.get_stack_fraction(e.items[M], 'P', .2, 20, 'multiply'))
    strict(allocation, {101: 2, 102: 3, 103: 3, 104: 3, 105: 3, 106: 3, 107: 3})
    strict(ev, []); strict([getattr(e.characters['P'], k.lower()) for k in POSITIVE], [100]*7)
    strict(e.characters['P'].buff_protect_stacks, 3)
    check('12_cap20_six_exact_draws_no_mutation', allocation)
    stacks(e, 'P', {k: 1 for k in POSITIVE})
    prestate(e, 'B_tie', {'seven_positive_stacks': 1, 'protection': 3})
    _, ev = segment(e, '13_Mirror_tie_full_caller', [cooldown(M)] + shuffle(), lambda: e.trigger(e.items[M]))
    strict(types(ev), [E['Regeneration'], E['Activation']])
    strict(ev[0]['params']['amount'], 1); strict(ev[0]['origin'], M)
    strict([getattr(e.characters['P'], k.lower()) for k in POSITIVE], [1,2,1,1,1,1,1])
    strict(e.items[K].goobert_activations, 1); strict(e.characters['P'].buff_protect_stacks, 3)
    strict(e.items[M].consumed, True); strict(e.items[M].cooldown_active, False)
    check('13_equal_overflow_Regeneration_before_Activation', ev)

    STAGE = 'C_initialize'
    e = unit(h, layout, 'C'); c = e.characters['P']
    c.hp = 100.0; c.buff_protect_stacks = 0; stacks(e, 'P', {'Mana': 4})
    strict(e.king_states[K]['invuCharges'], 3)
    prestate(e, 'C_King_Fly', {'hp': 100.0, 'Mana': 4, 'protection': 0, 'util_time': 1.0})
    def king_fly():
        e.king_effect(e.items[K]); e.trigger(e.items[F]); e.trigger(e.items[F])
    rows = [fl('invulnerability_pitch:' + K, .9, 1.1, 1.0), cooldown(F), reflection(0), cooldown(F), reflection(100)]
    _, ev = segment(e, '14_King_then_Fly_reflection', rows, king_fly)
    inv = next(x for x in ev if x['type'] == E['InvulnerableStart'])
    mana = next(x for x in ev if x['type'] == E['Mana'])
    strict(mana['parent'], inv['id']); strict(mana['params']['amount'], -4)
    strict((c.hp, c.mana, c.buff_protect_stacks, c.invulnerable, e.king_states[K]['invuCharges']), (135.0,0,3,True,2))
    flyev = [x for x in ev if x['origin'] == F]
    strict(types(flyev), [E['Poison'],E['Activation'],E['Poison'],E['Activation']])
    strict([(x['target'], x['params']['amount'], x['params']['reflected']) for x in flyev if x['type']==E['Poison']], [(1,1,True),(0,1,False)])
    strict((c.poison,e.characters['O'].poison),(1,1))
    check('14_real_King_Fly_protect_and_explicit_Mana_parent', ev)
    def ticks():
        e.tick_counter['P'] = 1; e._timer_timeout('tick:P')
        strict((c.hp,c.block),(135.0,0))
        e._timer_timeout('invu:P')
        e.tick_counter['P'] = 3; e._timer_timeout('tick:P')
    prestate(e, 'C_ticks', {'direct_callback_bodies': True, 'synthetic_odd_tick_counters': [1,3], 'TimerRuntime_elapsed_claim': False})
    _, ev = segment(e, '15_Poison_invu_then_end_callbacks', [poison(),poison()], ticks)
    strict(types(ev), [E['DealDamage'],E['InvulnerableEnd'],E['DealDamage']])
    strict([x['params']['damage'] for x in ev if x['type']==E['DealDamage']], [0,1])
    strict((c.hp,c.block,c.invulnerable,c.buff_protect_stacks),(134.0,0,False,3))
    parent = next(x['id'] for x in ev if x['type']==E['InvulnerableEnd'])
    check('15_direct_tick_bodies_invu_and_end_draws', ev)
    for s in ('P','O'): stacks(e,s,{'Poison':0})
    prestate(e,'C_parent_reflection',{'both_Poison':0,'explicit_real_parent':parent})
    _, ev = segment(e,'16_explicit_parent_reflected_gain',[reflection(0),reflection(100)],
        lambda:e._gain_stacks(e.items[F],'P','Poison',2,parent=parent,reflect=False))
    strict(types(ev),[E['Poison'],E['Poison']])
    strict([(x['target'],x['params']['amount'],x['params']['reflected'],x['parent']) for x in ev],[(0,1,False,parent),(1,1,True,parent)])
    strict((c.poison,e.characters['O'].poison,c.buff_protect_stacks),(1,1,3))
    check('16_reflection_parent_and_no_recursive_roll',ev)
    stacks(e,'P',{'Poison':10000});stacks(e,'O',{'Poison':0})
    prestate(e,'C_cap_early_return',{'P_Poison':10000,'O_Poison':0})
    value,ev=segment(e,'17_Poison_cap_before_reflected_recursion',[reflection(0),reflection(100)],
        lambda:e._gain_stacks(e.items[F],'P','Poison',2,parent=parent,reflect=False))
    strict(value,None);strict(ev,[]);strict((c.poison,e.characters['O'].poison,c.buff_protect_stacks),(10000,0,3))
    check('17_cap_return_skips_reflected_recursion',dict(rolls=2,no_events=True))

def integration(h, mod, job):
    global ACTIVE, STAGE
    STAGE = '18_fixed_Source_integration'
    b = h.initialize(copy.deepcopy(job['layout']), job['seed']); e=b._engine;ACTIVE=e
    strict(type(e.random),h.CombatRandom)
    ledger=[]
    def wrap(name):
        original=getattr(e,name)
        def invoke(*a,**kw):
            before=dict(event_num=e.event_num, protection={s:e.characters[s].buff_protect_stacks for s in ('P','O')})
            out=original(*a,**kw)
            subject=getattr(a[0],'instance_id',a[0]) if a else None
            if name!='trigger' or subject in (M,F):
                ledger.append(dict(method=name,subject=subject,before=before,after_event_num=e.event_num,
                    protection={s:e.characters[s].buff_protect_stacks for s in ('P','O')}))
            return out
        setattr(e,name,invoke)
    for name in ('trigger','king_effect','invu_timeout','damage_nonitem','remove_stack'):wrap(name)
    result=b.run(max_seconds=10.0)
    output=save('natural-source-output.json',result);save('natural-business-ledger.json',ledger)
    strict(b.done,True);assert e.frame_driver.finalized
    strict(result['source_rng'],e.random.snapshot());strict(result['random_inputs'],e.random.audit)
    strict(result['coverage']['status'],'SOURCE_PURE_KING_MIRROR_POISON_NOT_PER_LAYOUT_NATIVE_VALIDATED')
    E=mod.EVENT_TYPES
    poison_events=[x for x in e.events if x['type']==E['Poison']]
    poison_damage=[x for x in e.events if x['origin']==108 and x['type']==E['DealDamage']]
    hit=dict(Mirror_activation=any(x['type']==E['Activation'] and x['origin']==M for x in e.events),
        Mirror_allocation=any(x['origin']==M and 101<=x['type']<=107 for x in e.events),
        Fly_poison=bool(poison_events),Poison_reflection=any(x['params'].get('reflected') for x in poison_events),
        invulnerability=any(x['type']==E['InvulnerableStart'] for x in e.events),
        zero_Poison_tick=any(x['params']['damage']==0 for x in poison_damage),
        nonzero_Poison_tick=any(x['params']['damage']>0 for x in poison_damage),
        protection_accumulation=any(x['method']=='king_effect' and x['protection']['P']>x['before']['protection']['P'] for x in ledger))
    decreases=[x for x in ledger if x['method']=='remove_stack' and any(x['protection'][s]<x['before']['protection'][s] for s in ('P','O'))]
    strict(decreases,[],'no_natural_positive_buff_remover')
    summary=dict(status='SOURCE_ONLY_NOT_NATIVE_OR_SEED_EQUIVALENCE',output=output,seed=job['seed'],items=27,
        events=len(e.events),draws=len(e.random.audit),timers=33,winner=e.winner,
        HIT={k:('HIT' if v else 'NOT_HIT') for k,v in hit.items()},
        natural_positive_buff_protection_loss='NOT_HIT_NO_SELECTED_REMOVER',no_input_tuning=True,
        source_rng=e.random.snapshot(),calls=COUNTS.copy())
    save('natural-summary.json',summary);check('18_one_fixed_Source_complete',summary)

def main():
    global STAGE
    start=time.monotonic();OUT.mkdir(exist_ok=False);status='FAILED';rows=[]
    try:
        verify_owner(OWN)
        verify_owner(PLAN/'owned-files.json','8c561ceae86bc875eb462fd161f1e90f78735177bf7d395dd773fb3b633c392d')
        rows=verify_owner(SOURCE/'owned-files.json','310896af1da03567a5dcd98b578567228ed0ec4b9eefffd798568eef9a0366d6')
        job=json.loads((PLAN/'source-job.json').read_bytes())
        sys.dont_write_bytecode=True;sys.pycache_prefix=str(OUT/'unused-bytecode-cache')
        sys.path.insert(0,str(SOURCE/'staged'));STAGE='import_frozen_source'
        h=importlib.import_module('headless');mod=importlib.import_module('native_replay_v8.engine')
        allowed={str((ROOT/r['path']).resolve()) for r in rows if '/staged/' in r['path']}
        imports=[]
        for name,m in list(sys.modules.items()):
            if name in ('headless','original_rng','godot_pcg_integer') or name.startswith(('native_replay_v7','native_replay_v8')):
                path=str(Path(m.__file__).resolve());assert path in allowed,(name,path);imports.append(dict(name=name,path=path))
        save('imports.json',imports)
        for obj,name,label in [(h,'derive_stream_seeds','derive_stream_seeds'),(h.CombatRandom,'__init__','CombatRandom.__init__'),
            (h.GodotPCGInteger,'__init__','GodotPCGInteger.__init__'),(mod.CombatEngine,'__init__','Engine.__init__'),
            (mod.CombatEngine,'prepare_only','Engine.prepare_only'),(mod.CombatEngine,'activate_from_checkpoint','Engine.activate_from_checkpoint'),
            (mod.CombatEngine,'run','Engine.run'),(mod.CombatEngine,'step','Engine.step')]: counted(obj,name,label)
        for name in ('trigger','king_effect','heal','activate','on_goobert_item_activated','_gain_stacks','remove_stack','get_stack_fraction','_timer_timeout'):
            counted(mod.CombatEngine,name,'Engine.'+name)
        STAGE='ingress';ingress(h,mod,job['layout'])
        components(h,mod,job['layout']);integration(h,mod,job)
        strict(len(PASSES),18);strict(COUNTS['Engine.__init__'],4);strict(COUNTS['Engine.prepare_only'],4);strict(COUNTS['Engine.run'],1)
        status='PASS_EIGHT_ID_SOURCE_COMPONENTS_AND_ONE_FIXED_INTEGRATION_NOT_NATIVE'
    except BaseException as exc:
        save('first-error.json',dict(stage=STAGE,type=type(exc).__name__,message=str(exc),traceback=traceback.format_exc(),calls=COUNTS.copy()))
        if ACTIVE is not None:
            try:save('same-instance-failure.json',dict(events=ACTIVE.events,audit=ACTIVE.random.audit,snapshot=ACTIVE.snapshot(),calls=COUNTS.copy()))
            except BaseException as secondary:save('failure-diagnostic-error.json',dict(type=type(secondary).__name__,message=str(secondary)))
    finally:
        signal.alarm(0)
        after=[pin(ROOT/r['path']) for r in rows];strict(after,rows,'source_after')
        save('source-after.json',after);save('prepare-boundaries.json',PREPARES)
        result=dict(status=status,stage=STAGE,wall_seconds=time.monotonic()-start,passed_controls=len(PASSES),calls=COUNTS,
            candidate_source_refs_unchanged=len(after),native_runs=0,Expected_reads=0,old_tests=0,pool_operations=0,auto_retry=False)
        save('result.json',result)
        save('owned-files.json',dict(schema='phase483-actual-owner/1',files=[pin(p) for p in sorted(OUT.iterdir()) if p.is_file()],no_more_writes=True))
    print(json.dumps(result));return 0 if status.startswith('PASS') else 1

if __name__=='__main__':
    def timeout(signum,frame):raise TimeoutError('phase483 harness 35s limit')
    signal.signal(signal.SIGALRM,timeout);signal.alarm(35)
    sys.exit(main())
