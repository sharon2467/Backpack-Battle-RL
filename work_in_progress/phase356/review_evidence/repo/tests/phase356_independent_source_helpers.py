"""Exact-AST/static supplement for the bounded356 SOURCE regression."""
import ast
import builtins
import copy
import dataclasses
import hashlib
import json
from pathlib import Path
import types


def ast_dump(n):
    return ast.dump(n, include_attributes=False)


def static_review(root, d):
    a = root / 'data/phase356-king-admission-source-repair'
    def pin(p):
        b = p.read_bytes()
        return dict(size=len(b), sha256=hashlib.sha256(b).hexdigest())
    assert pin(a / 'source-owner.json') == dict(size=4879, sha256='b3a07058a564cfd07dde627d2c27f96c4ff384b38366157a35a8c999bbd04831')
    owner = json.loads((a / 'source-owner.json').read_text())
    for row in owner['files']:
        assert pin(root / row['path']) == {k: row[k] for k in ('size', 'sha256')}
    before = json.loads((root / 'data/phase355-king-finite-source/candidate-source-freeze.json').read_text())
    after = json.loads((a / 'candidate-source-freeze.json').read_text())
    changed = []
    for name, identity in after['files'].items():
        new = a / 'staged' / name
        old = root / 'data/phase355-king-finite-source/staged' / name
        assert pin(new) == identity and pin(old) == before['files'][name]
        compile(new.read_bytes(), str(new), 'exec')
        if new.read_bytes() != old.read_bytes():
            changed.append(name)
    assert set(changed) == {'native_replay_v8/genuine.py', 'native_replay_v8/engine.py'}
    genuine = ast.parse((d / 'SOURCE/genuine.py').read_text())
    guard = next(n for n in genuine.body if isinstance(n, ast.FunctionDef) and n.name == 'require_single_king_admission')
    args = guard.args
    assert not args.posonlyargs and not args.args and not args.kwonlyargs and args.vararg is None and args.kwarg is None and not args.defaults and not args.kw_defaults
    body = guard.body[1:] if isinstance(guard.body[0], ast.Expr) and isinstance(guard.body[0].value, ast.Constant) and isinstance(guard.body[0].value.value, str) else guard.body
    assert len(body) == 1 and isinstance(body[0], ast.Raise)
    assert isinstance(body[0].exc, ast.Call) and isinstance(body[0].exc.func, ast.Name) and body[0].exc.func.id == 'ValueError'
    assert len(body[0].exc.args) == 1 and isinstance(body[0].exc.args[0], ast.Constant)
    assert body[0].exc.args[0].value.startswith('PENDING_SINGLE_KING_OBSERVER_PATCH_BINDING:')
    sites = []
    for name in ('validate_profile', 'validate_result_profile'):
        fn = next(n for n in genuine.body if isinstance(n, ast.FunctionDef) and n.name == name)
        first = fn.body[0]
        assert isinstance(first, ast.If) and any(isinstance(n, ast.Name) and n.id == 'SINGLE_KING_GENUINE_PROFILE' for n in ast.walk(first.test))
        assert isinstance(first.body[0], ast.Expr) and ast_dump(first.body[0].value) == ast_dump(ast.parse('require_single_king_admission()', mode='eval').body)
        sites.append(dict(function=name, line=first.body[0].lineno, first_new_branch_action='shared unconditional guard'))
    engine = ast.parse((d / 'SOURCE/engine.py').read_text())
    runtime = next(n for n in engine.body if isinstance(n, ast.FunctionDef) and n.name == 'validate_runtime_inputs')
    branch = next(n for n in runtime.body if isinstance(n, ast.If) and isinstance(n.test, ast.Call) and n.test.func.id == '_single_king_genuine_profile')
    assert isinstance(branch.body[0], ast.ImportFrom) and branch.body[0].module == 'genuine' and branch.body[0].level == 1
    assert {n.name for n in branch.body[0].names} == {'validate_single_king_fixture', 'require_single_king_admission'}
    assert isinstance(branch.body[1], ast.Expr) and ast_dump(branch.body[1].value) == ast_dump(ast.parse('require_single_king_admission()', mode='eval').body)
    assert branch.body[2].value.func.id == 'validate_single_king_fixture'
    sites.append(dict(function='validate_runtime_inputs', line=branch.body[1].lineno, first_new_branch_action='import shared function then unconditional guard before fixture/remaining runtime'))

    class Inverse(ast.NodeTransformer):
        def visit_FunctionDef(self, node):
            return None if node.name == 'require_single_king_admission' else self.generic_visit(node)
        def visit_Expr(self, node):
            if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name) and node.value.func.id == 'require_single_king_admission':
                return None
            return self.generic_visit(node)
        def visit_ImportFrom(self, node):
            node.names = [n for n in node.names if n.name != 'require_single_king_admission']
            return node
    for name, tree in [('genuine.py', genuine), ('engine.py', engine)]:
        inverse = Inverse().visit(copy.deepcopy(tree))
        old = ast.parse((d / 'SOURCE' / ('old355-' + name)).read_text())
        assert ast_dump(inverse) == ast_dump(old), name
    cls = next(n for n in engine.body if isinstance(n, ast.ClassDef) and n.name == 'CombatEngine')
    init = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == '__init__')
    call_lines = {key: sorted(n.lineno for n in ast.walk(init) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == key)
                  for key in ('validate_runtime_inputs', 'SeededRandom')}
    early = next(n for n in init.body if isinstance(n, ast.Assign) and isinstance(n.value, ast.IfExp) and isinstance(n.value.body, ast.Call) and n.value.body.func.id == 'validate_runtime_inputs')
    assert '_single_king_genuine_profile' in {n.id for n in ast.walk(early.value.test) if isinstance(n, ast.Name)}
    assert early.value.body.lineno == call_lines['validate_runtime_inputs'][0] < call_lines['SeededRandom'][0]
    observed = ast.parse((d / 'SOURCE/observed.py').read_text())
    run = next(n for n in observed.body if isinstance(n, ast.FunctionDef) and n.name == 'run_input_bundle')
    observed_calls = {key: sorted(n.lineno for n in ast.walk(run) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == key)
                      for key in ('validate_runtime_inputs', 'SeededRandom', 'TapeRandom', 'CombatEngine')}
    assert all(observed_calls['validate_runtime_inputs'][0] < observed_calls[k][0] for k in ('SeededRandom', 'TapeRandom', 'CombatEngine'))
    compare = ast.parse((d / 'SOURCE/compare.py').read_text())
    compare_fn = next(n for n in compare.body if isinstance(n, ast.FunctionDef) and n.name == 'compare_capture')
    result_line = next(n.lineno for n in ast.walk(compare_fn) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'validate_result_profile')
    path_line = next(n.lineno for n in ast.walk(compare_fn) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'Path')
    assert result_line < path_line
    result = dict(schema='phase356-independent-static-regression/1', status='PASS',
                  author_readback=dict(leaves=len(owner['files']), bytes=sum(x['size'] for x in owner['files'])),
                  compiled_candidate_modules=15, byte_conserved=13, changed=changed,
                  inverse_complete_modules_equal_355=True, old_profile_patch_helpers_unchanged=True,
                  unconditional_no_argument_no_caller_flag_guard=True, shared_sites=sites,
                  direct_engine_source_call_lines=call_lines, observed_source_call_lines=observed_calls,
                  comparator_guard_before_Path=True, pending_profile_not_native_ready=True,
                  candidate_imports=0, Engine_constructions=0, RNG_constructions=0, models=0, native=0)
    with (d / 'static-review.json').open('x') as f:
        json.dump(result, f, indent=2, sort_keys=True)
        f.write('\n')
    return result


def supplement(ns, fixture, profile, result_profile, check, results, d):
    def pending(label, action):
        check(label, 'reject', action)
        row = results[-1]
        row['pending_reason_matched'] = row['detail'].get('type') == 'ValueError' and row['detail'].get('message', '').startswith('PENDING_SINGLE_KING_OBSERVER_PATCH_BINDING:')
        row['pass_'] = row['pass_'] and row['pending_reason_matched']
    pending('shared-guard-no-opening-condition', ns['require_single_king_admission'])
    check('shared-guard-no-positional-opening-flag', 'reject', lambda: ns['require_single_king_admission'](True))
    check('shared-guard-no-keyword-opening-flag', 'reject', lambda: ns['require_single_king_admission'](ready=True))
    flags = dict(ready=True, native_schema_ready=True, observer_accepted=True,
                 patch_version=ns['SUPPORT68_PATCH']['version'], pending=False)
    pending('input-caller-flags-and-old-patch-cannot-open', lambda: ns['validate_profile'](dict(profile, **flags), fixture))
    pending('result-caller-flags-and-old-patch-cannot-open', lambda: ns['validate_result_profile'](dict(result_profile, **flags), fixture))
    pending('input-guard-precedes-fixture-fields', lambda: ns['validate_profile'](profile, None))
    pending('result-guard-precedes-fixture-fields', lambda: ns['validate_result_profile'](result_profile, None))
    et = ast.parse((d / 'SOURCE/engine.py').read_text())
    genuine = types.ModuleType('__exact_source_genuine__')
    genuine.require_single_king_admission = ns['require_single_king_admission']
    genuine.validate_single_king_fixture = ns['validate_single_king_fixture']
    import_log = []
    def source_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == 'genuine' and level == 1 and set(fromlist) == {'validate_single_king_fixture', 'require_single_king_admission'}:
            import_log.append(dict(name=name, level=level, resolution='in-memory exact AST functions, no staged module import'))
            return genuine
        raise AssertionError('unexpected import in selected runtime validator')
    engine_ns = dict(__name__='__phase356_exact_source_runtime__',
                     __builtins__=dict(vars(builtins), __import__=source_import),
                     deepcopy=copy.deepcopy, dataclass=dataclasses.dataclass,
                     SINGLE_KING_GENUINE_PROFILE=ns['SINGLE_KING_GENUINE_PROFILE'])
    for node in et.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name) and node.targets[0].id == 'SOURCE_KING_PROFILE':
            engine_ns['SOURCE_KING_PROFILE'] = ast.literal_eval(node.value)
    selected_names = {'RuntimeDTO', '_source_king_profile', '_single_king_genuine_profile', 'validate_runtime_inputs'}
    selected = [n for n in et.body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name in selected_names]
    assert {n.name for n in selected} == selected_names
    exec(compile(ast.Module(body=selected, type_ignores=[]), '<exact-pure-runtime-SOURCE>', 'exec'), engine_ns)
    assert genuine.require_single_king_admission is ns['require_single_king_admission']
    runtime = engine_ns['validate_runtime_inputs']
    pending('runtime-minimal-new-profile-failclosed', lambda: runtime(dict(profile), fixture))
    pending('runtime-caller-flags-and-old-patch-cannot-open', lambda: runtime(dict(profile, **flags), fixture))
    pending('runtime-guard-precedes-fixture-fields', lambda: runtime(dict(profile), None))
    pending('runtime-mode-flag-cannot-bypass', lambda: runtime(dict(profile, mode='synthetic'), fixture))
    old_fixture = copy.deepcopy(fixture)
    old_fixture['sides'][0]['items'] = [x for x in old_fixture['sides'][0]['items'] if x['item_index'] != 262]
    old_input = dict(profile_id=ns['HEADLESS_PROFILE'], mode='genuine', terminal_profile=ns['TERMINAL'])
    old_result = dict(profile=ns['HEADLESS_PROFILE'], mode='genuine', terminal_profile=ns['TERMINAL'])
    check('existing-headless-input-domain-preserved', 'accept', lambda: ns['validate_profile'](old_input, old_fixture))
    check('existing-headless-result-domain-preserved', 'accept', lambda: ns['validate_result_profile'](old_result, old_fixture))
    check('existing-headless-wrong-mode-still-rejected', 'reject', lambda: ns['validate_profile'](dict(old_input, mode='synthetic'), old_fixture))
    check('unknown-input-profile-still-rejected', 'reject', lambda: ns['validate_profile'](dict(old_input, profile_id='unknown-future-profile'), old_fixture))
    check('unknown-result-profile-still-rejected', 'reject', lambda: ns['validate_result_profile'](dict(old_result, profile='unknown-future-profile'), old_fixture))
    return dict(runtime_relative_import_resolutions=import_log, staged_imports=0,
                RuntimeDTO_class_defined=1, RuntimeDTO_instances_constructed=0,
                Engine_constructions=0, RNG_constructions=0)
