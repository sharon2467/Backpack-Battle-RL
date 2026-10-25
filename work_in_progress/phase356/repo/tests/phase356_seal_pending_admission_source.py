"""Static repair seal; never import or call a candidate."""
from pathlib import Path
import ast
import difflib
import hashlib
import json

R = Path(__file__).resolve().parents[1]
D = R / 'data/phase356-king-admission-source-repair'
S = D / 'staged'
B = R / 'data/phase355-king-finite-source/staged'


def pin(path):
    raw = path.read_bytes()
    return dict(size=len(raw), sha256=hashlib.sha256(raw).hexdigest())


def write(name, value):
    with (D / name).open('x') as stream:
        stream.write(json.dumps(value, indent=2, sort_keys=True) + '\n')


def shape(text):
    return ast.dump(ast.parse(text), include_attributes=False)


def main():
    baseline = json.loads((B.parent / 'candidate-source-freeze.json').read_text())
    after = {}
    changed = []
    patches = []
    for name, identity in baseline['files'].items():
        assert pin(B / name) == identity, name
        old, new = (B / name).read_bytes(), (S / name).read_bytes()
        compile(new, str(S / name), 'exec')
        after[name] = pin(S / name)
        if old != new:
            changed.append(name)
            patches.extend(difflib.unified_diff(old.decode().splitlines(True), new.decode().splitlines(True),
                                               fromfile='355/' + name, tofile='356/' + name))
    assert set(changed) == {'native_replay_v8/engine.py', 'native_replay_v8/genuine.py'}
    g = (S / 'native_replay_v8/genuine.py').read_text()
    gt = ast.parse(g)
    gate = next(n for n in gt.body if isinstance(n, ast.FunctionDef) and n.name == 'require_single_king_admission')
    assert not gate.args.posonlyargs and not gate.args.args and not gate.args.kwonlyargs
    assert gate.args.vararg is None and gate.args.kwarg is None
    assert len(gate.body) == 2 and isinstance(gate.body[0], ast.Expr) and isinstance(gate.body[1], ast.Raise)
    raised = gate.body[1].exc
    assert isinstance(raised, ast.Call) and isinstance(raised.func, ast.Name) and raised.func.id == 'ValueError'
    assert len(raised.args) == 1 and isinstance(raised.args[0], ast.Constant)
    assert raised.args[0].value.startswith('PENDING_SINGLE_KING_OBSERVER_PATCH_BINDING:')
    inverse_g = ''.join(g.splitlines(keepends=True)[:gate.lineno - 1])
    assert inverse_g.count('        require_single_king_admission()\n') == 2
    inverse_g = inverse_g.replace('        require_single_king_admission()\n', '')
    assert shape(inverse_g) == shape((B / 'native_replay_v8/genuine.py').read_text())
    # Input/result first new-profile branch invokes exactly the same closed gate.
    for name in ('validate_profile', 'validate_result_profile'):
        fn = next(n for n in gt.body if isinstance(n, ast.FunctionDef) and n.name == name)
        first = fn.body[0]
        assert isinstance(first, ast.If) and isinstance(first.test, ast.Compare)
        assert isinstance(first.test.comparators[0], ast.Name) and first.test.comparators[0].id == 'SINGLE_KING_GENUINE_PROFILE'
        call = first.body[0]
        assert isinstance(call, ast.Expr) and isinstance(call.value, ast.Call)
        assert isinstance(call.value.func, ast.Name) and call.value.func.id == 'require_single_king_admission'
        assert call.value.args == [] and call.value.keywords == []
    e = (S / 'native_replay_v8/engine.py').read_text()
    added = ('        from .genuine import validate_single_king_fixture, require_single_king_admission\n'
             '        require_single_king_admission()\n')
    old = '        from .genuine import validate_single_king_fixture\n'
    assert e.count(added) == 1
    assert shape(e.replace(added, old, 1)) == shape((B / 'native_replay_v8/engine.py').read_text())
    # Source call ordering only; no constructors/functions invoked.
    assert e.index(added) < e.index("    king = _has_king(fixture)", e.index('def validate_runtime_inputs('))
    ctor = e[e.index('class CombatEngine:'):e.index('    def _set_source_processing(')]
    assert ctor.index('source_runtime = validate_runtime_inputs(') < ctor.index('self.random =')
    assert 'or _single_king_genuine_profile(runtime) else None' in ctor
    observed = (S / 'native_replay_v8/observed.py').read_text()
    assert observed.index('runtime=validate_runtime_inputs(') < observed.index('rng=SeededRandom(')
    assert observed.index('runtime=validate_runtime_inputs(') < observed.index('rng=TapeRandom(')
    assert observed.index('runtime=validate_runtime_inputs(') < observed.index('engine=CombatEngine(')
    compile(Path(__file__).read_bytes(), str(Path(__file__)), 'exec')
    (D / 'candidate-source.patch').write_text(''.join(patches))
    write('source-validation.json', dict(
        schema='phase356-static-repair-validation/1', compile='PASS_NO_IMPORT',
        changed=changed, byte_conserved=13, inverse_old_modules_AST_equal_355=True,
        shared_gate='require_single_king_admission', no_args_no_flags_unconditional_raise=True,
        three_admission_sites=['genuine.validate_profile', 'genuine.validate_result_profile', 'engine.validate_runtime_inputs'],
        preRNG_call_order='STATIC_SOURCE_PASS_OBSERVED_AND_DIRECT_ENGINE_PATHS',
        unchanged=['validate_patch', 'compare.py', 'all pure SOURCE helpers', 'all existing profile branches',
                   'headless', 'effects', 'PCG', 'TimerRuntime', 'FrameDriver'],
        candidate_imports=0, helper_calls=0, Engine_constructions=0, RNG_constructions=0,
        semantic_controls_executed=0, models=0, native=0,
    ))
    write('candidate-source-freeze.json', dict(
        schema='phase356-candidate-source-freeze/1', files=after, changed=changed, conserved=13,
        baseline=dict(path=str((B.parent / 'candidate-source-freeze.json').relative_to(R)), **pin(B.parent / 'candidate-source-freeze.json')),
        profile='observer7-355-native-single-king-A/1', admission='CLOSED_UNCONDITIONAL_HOST_CODE_PENDING_BINDING',
        status='SOURCE_ONLY_INDEPENDENT_REPAIR_REVIEW_PENDING', no_more_candidate_writes=True,
    ))
    print(json.dumps(dict(status='STATIC_REPAIR_SOURCE_FROZEN_NO_CANDIDATE_CALL', candidate=pin(D / 'candidate-source-freeze.json'))))


if __name__ == '__main__':
    main()
