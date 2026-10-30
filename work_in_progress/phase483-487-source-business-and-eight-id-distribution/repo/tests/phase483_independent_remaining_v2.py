"""Remaining-only fixed Source integration; no prior control execution."""
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
OWN = ROOT / 'data/phase483-independent-remaining-harness-v2/owned-files.json'
OUT = ROOT / 'data/phase483-independent-remaining-v2-first-001'
COUNTS, PASSES, PREPARES = {}, [], []
ACTIVE = None
STAGE = 'preflight'
K, M, F = 'P:king', 'P:mirror', 'O:fly'


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
    result=b.run(max_seconds=120.0)
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
        prior=ROOT/'data/phase483-independent-business-first-001'
        contract=json.loads((OWN.parent/'contract.json').read_bytes())
        verify_owner(prior/'owned-files.json',contract['reused_actual_owner']['sha256'])
        prior_result=json.loads((prior/'result.json').read_bytes())
        strict(prior_result['passed_controls'],17);strict(prior_result['status'],'FAILED')
        save('reused-prefix.json',dict(owner=pin(prior/'owned-files.json'),result=pin(prior/'result.json'),passed_controls=17,rerun=False,
            first_natural_attempt_completed=False,first_natural_attempts=1))
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
        integration(h,mod,job)
        strict(len(PASSES),1);strict(COUNTS['Engine.__init__'],1);strict(COUNTS['Engine.prepare_only'],1);strict(COUNTS['Engine.run'],1)
        status='PASS_REMAINING_FIXED_SOURCE_INTEGRATION_NOT_NATIVE'
    except BaseException as exc:
        save('first-error.json',dict(stage=STAGE,type=type(exc).__name__,message=str(exc),traceback=traceback.format_exc(),calls=COUNTS.copy()))
        if ACTIVE is not None:
            try:save('same-instance-failure.json',dict(events=ACTIVE.events,audit=ACTIVE.random.audit,snapshot=ACTIVE.snapshot(),calls=COUNTS.copy()))
            except BaseException as secondary:save('failure-diagnostic-error.json',dict(type=type(secondary).__name__,message=str(secondary)))
    finally:
        signal.alarm(0)
        after=[pin(ROOT/r['path']) for r in rows];strict(after,rows,'source_after')
        save('source-after.json',after);save('prepare-boundaries.json',PREPARES)
        result=dict(status=status,stage=STAGE,wall_seconds=time.monotonic()-start,passed_remaining_controls=len(PASSES),reused_controls=17,calls=COUNTS,
            candidate_source_refs_unchanged=len(after),native_runs=0,Expected_reads=0,old_tests=0,pool_operations=0,auto_retry=False,
            this_attempt_natural_runs=COUNTS.get('Engine.run',0),cumulative_natural_attempts=1+COUNTS.get('Engine.run',0),
            cumulative_completed_natural_battles=int(status.startswith('PASS')),simulated_seconds_ceiling=120,wall_seconds_cap=35)
        save('result.json',result)
        save('owned-files.json',dict(schema='phase483-remaining-v2-actual-owner/1',files=[pin(p) for p in sorted(OUT.iterdir()) if p.is_file()],no_more_writes=True))
    print(json.dumps(result));return 0 if status.startswith('PASS') else 1

if __name__=='__main__':
    def timeout(signum,frame):raise TimeoutError('phase483 remaining harness35s wall limit')
    signal.signal(signal.SIGALRM,timeout);signal.alarm(35)
    sys.exit(main())
