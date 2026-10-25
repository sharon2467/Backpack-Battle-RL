"""Static SOURCE seal only: text, AST and compile; never import a candidate."""
from pathlib import Path
import ast
import builtins
import difflib
import hashlib
import json

R = Path(__file__).resolve().parents[1]
D = R / 'data/phase355-king-finite-source'
S = D / 'staged'
B = R / 'data/phase349-king-fresh-source/staged'


def pin(path):
    raw = path.read_bytes()
    return dict(size=len(raw), sha256=hashlib.sha256(raw).hexdigest())


def write(name, value):
    with (D / name).open('x') as stream:
        stream.write(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + '\n')


def tree(text):
    return ast.dump(ast.parse(text), include_attributes=False)


def main():
    baseline = json.loads((B.parent / 'candidate-source-freeze.json').read_text())
    before = {}
    after = {}
    changed = []
    patches = []
    for name, identity in baseline['files'].items():
        assert pin(B / name) == identity, name
        old, new = (B / name).read_bytes(), (S / name).read_bytes()
        compile(new, str(S / name), 'exec')
        before[name], after[name] = identity, pin(S / name)
        if old != new:
            changed.append(name)
            patches.extend(difflib.unified_diff(old.decode().splitlines(True), new.decode().splitlines(True),
                                               fromfile='349/' + name, tofile='355/' + name))
    assert set(changed) == {'native_replay_v8/genuine.py', 'native_replay_v8/engine.py'}
    (D / 'candidate-source.patch').write_text(''.join(patches))
    old_g = (B / 'native_replay_v8/genuine.py').read_text()
    new_g = (S / 'native_replay_v8/genuine.py').read_text()
    inverse_g = new_g.split('#355 new finite source domain.', 1)[0]
    start = inverse_g.index('SINGLE_KING_GENUINE_PROFILE =')
    end = inverse_g.index('PROFILES =', start)
    inverse_g = inverse_g[:start] + inverse_g[end:]
    inverse_g = inverse_g.replace(' | {SINGLE_KING_GENUINE_PROFILE}', '', 1)
    for function, variable, field, error in (
        ('validate_profile(data, fixture)', 'data', 'profile_id', 'runtime'),
        ('validate_result_profile(runtime,fixture)', 'runtime', 'profile', 'result'),
    ):
        added = (
            '    if ' + variable + ".get('" + field + "') == SINGLE_KING_GENUINE_PROFILE:\n"
            '        if ' + variable + ".get('mode') != 'genuine' or " + variable + ".get('terminal_profile') != SINGLE_KING_TERMINAL:\n"
            "            raise ValueError('single King finite genuine " + error + "/terminal required')\n"
            '        validate_single_king_fixture(fixture)\n        return\n'
        )
        assert inverse_g.count(added) == 1
        inverse_g = inverse_g.replace(added, '', 1)
    added = "    if data.get('profile_id') == SINGLE_KING_GENUINE_PROFILE:return 'observer7-355-single-king-A'\n"
    assert inverse_g.count(added) == 1
    inverse_g = inverse_g.replace(added, '', 1)
    assert tree(inverse_g) == tree(old_g), 'all original genuine statements/functions restored'

    old_e = (B / 'native_replay_v8/engine.py').read_text()
    new_e = (S / 'native_replay_v8/engine.py').read_text()
    inverse_e = new_e.split('#355 actual finite runtime:', 1)[0]
    pairs = [
        ('observer_label, KING_GENUINE_PROFILE, SINGLE_KING_GENUINE_PROFILE\n', 'observer_label, KING_GENUINE_PROFILE\n'),
        ('(KING_INTEGRATION_PROFILE, KING_GENUINE_PROFILE, SINGLE_KING_GENUINE_PROFILE)', '(KING_INTEGRATION_PROFILE, KING_GENUINE_PROFILE)'),
        ("    if data.get('profile_id') == SINGLE_KING_GENUINE_PROFILE:\n        return _validate_single_king_processing_inputs(data, fixture)\n", ''),
        ("data['profile_id'] in (KING_GENUINE_PROFILE, SINGLE_KING_GENUINE_PROFILE)", "data['profile_id']==KING_GENUINE_PROFILE"),
        ('if _source_king_profile(runtime) or _single_king_genuine_profile(runtime) else None', 'if _source_king_profile(runtime) else None'),
        ("    if _single_king_genuine_profile(data):\n        from .genuine import validate_single_king_fixture\n        validate_single_king_fixture(fixture)\n", ''),
        ("    if _single_king_genuine_profile(data):\n        _validate_single_king_initials(data)\n", ''),
    ]
    for added, previous in pairs:
        assert inverse_e.count(added) == 1, added
        inverse_e = inverse_e.replace(added, previous, 1)
    assert tree(inverse_e) == tree(old_e), 'all original engine statements/functions restored'
    for path in (R / 'tests/phase355_input_source_contract.py', Path(__file__)):
        compile(path.read_bytes(), str(path), 'exec')
    # Conservative static missing-global check on new pure helpers, not execution.
    gtree = ast.parse(new_g)
    bound = set(dir(builtins))
    for node in ast.walk(gtree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            bound.add(node.id)
        elif isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            bound.add(node.name)
        elif isinstance(node, ast.arg):
            bound.add(node.arg)
        elif isinstance(node, ast.alias):
            bound.add(node.asname or node.name.split('.')[0])
    for fn in gtree.body:
        if isinstance(fn, ast.FunctionDef) and (fn.name.startswith('_single_king') or fn.name.startswith('validate_single_king')):
            missing = {n.id for n in ast.walk(fn) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)} - bound
            assert not missing, (fn.name, sorted(missing))
    counts = {}
    for name in changed:
        t = ast.parse((B / name).read_text())
        counts[name] = sum(isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) for n in ast.walk(t))
    write('source-validation.json', dict(
        schema='phase355-static-source-validation/1', compile='PASS_NO_IMPORT',
        changed=changed, byte_conserved=13, old_module_AST_restored=True,
        baseline_function_counts=counts, missing_new_helper_globals=[],
        old_profile_hash_patch_and_core_algorithms='UNCHANGED_AFTER_REMOVING_EXPLICIT_NEW_DISPATCH',
        semantic_helper_controls_executed=0, candidate_calls=0,
    ))
    write('candidate-source-freeze.json', dict(
        schema='phase355-candidate-source-freeze/1', files=after, changed=changed, conserved=13,
        baseline=dict(path=str((B.parent / 'candidate-source-freeze.json').relative_to(R)),
                      **pin(B.parent / 'candidate-source-freeze.json')),
        profile='observer7-355-native-single-king-A/1', status='SOURCE_ONLY_NOT_INDEPENDENTLY_ACCEPTED',
        native_patch_accepted=False, no_more_candidate_writes=True,
    ))
    print(json.dumps(dict(status='STATIC_SOURCE_COMPILE_INVERSE_PASS', candidate=pin(D / 'candidate-source-freeze.json'),
                          old_functions_checked=counts, candidate_imports=0)))


if __name__ == '__main__':
    main()
