"""Independent whole-module inverse AST and source-only dataflow review."""
import ast
import copy
import hashlib
import json
from pathlib import Path

R = Path(__file__).resolve().parents[1]
D = R / 'data/phase355-independent-source-review'
A = R / 'data/phase355-king-finite-source'
B = R / 'data/phase349-king-fresh-source/staged'


def pin(p):
    b = p.read_bytes()
    return dict(size=len(b), sha256=hashlib.sha256(b).hexdigest())


def dump(node):
    return ast.dump(node, include_attributes=False)


class RemoveNewDispatch(ast.NodeTransformer):
    def visit_ImportFrom(self, n):
        n.names = [a for a in n.names if a.name != 'SINGLE_KING_GENUINE_PROFILE']
        return n

    def visit_If(self, n):
        if isinstance(n.test, ast.Call) and isinstance(n.test.func, ast.Name) and n.test.func.id == '_single_king_genuine_profile':
            return None
        if any(isinstance(x, ast.Name) and x.id == 'SINGLE_KING_GENUINE_PROFILE' for x in ast.walk(n.test)):
            # Only the new top-level profile/result/observer branches are removed;
            # the old runtime's inner King dispatch is retained and normalized.
            if isinstance(n.test, ast.Compare) and isinstance(n.test.left, ast.Call):
                return None
        return self.generic_visit(n)

    def visit_Tuple(self, n):
        n = self.generic_visit(n)
        n.elts = [x for x in n.elts if not (isinstance(x, ast.Name) and x.id == 'SINGLE_KING_GENUINE_PROFILE')]
        return n

    def visit_Compare(self, n):
        original = copy.deepcopy(n)
        n = self.generic_visit(n)
        if (len(original.comparators) == 1 and isinstance(original.comparators[0], ast.Tuple)
                and len(original.comparators[0].elts) == 2
                and [getattr(x, 'id', None) for x in original.comparators[0].elts] == ['KING_GENUINE_PROFILE', 'SINGLE_KING_GENUINE_PROFILE']):
            n.ops = [ast.Eq()]
            n.comparators = [ast.Name(id='KING_GENUINE_PROFILE', ctx=ast.Load())]
        return n

    def visit_BoolOp(self, n):
        n = self.generic_visit(n)
        n.values = [x for x in n.values if not (isinstance(x, ast.Call) and isinstance(x.func, ast.Name) and x.func.id == '_single_king_genuine_profile')]
        return n.values[0] if len(n.values) == 1 else n

    def visit_BinOp(self, n):
        n = self.generic_visit(n)
        if isinstance(n.op, ast.BitOr) and isinstance(n.right, ast.Set) and len(n.right.elts) == 1 and isinstance(n.right.elts[0], ast.Name) and n.right.elts[0].id == 'SINGLE_KING_GENUINE_PROFILE':
            return n.left
        return n


def main():
    owner = json.loads((A / 'source-owner.json').read_text())
    for row in owner['files']:
        assert pin(R / row['path']) == {k: row[k] for k in ('size', 'sha256')}
    freeze = json.loads((A / 'candidate-source-freeze.json').read_text())
    changed = []
    for name, identity in freeze['files'].items():
        new, old = A / 'staged' / name, B / name
        assert pin(new) == identity
        compile(new.read_bytes(), str(new), 'exec')
        if new.read_bytes() != old.read_bytes():
            changed.append(name)
    assert set(changed) == {'native_replay_v8/engine.py', 'native_replay_v8/genuine.py'}
    conservation = []
    for filename in changed:
        old = ast.parse((B / filename).read_text())
        new = ast.parse((A / 'staged' / filename).read_text())
        old_names = {n.name for n in old.body if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
        new_names = {n.name for n in new.body if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
        new.body = [n for n in new.body if not (
            isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name not in old_names
            or isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id.startswith('SINGLE_KING_') for t in n.targets))]
        inverse = RemoveNewDispatch().visit(new)
        assert dump(inverse) == dump(old), filename
        conservation.append(dict(path=filename, baseline_functions=sum(isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) for n in ast.walk(old)), added_definitions=sorted(new_names-old_names), whole_old_module_inverse_AST=True))
    fixture = json.loads((A / 'fixed-A-v8-fixture.json').read_text())
    source_a = json.loads((R / 'data/phase351-fixed-pure-input-plan/A.json').read_text())
    expected = copy.deepcopy(source_a)
    expected['schema'] = 'native-v8-fixture/1'
    for side in expected['sides']:
        side['hp'] = float(side['hp'])
        side['stamina'] = float(side['stamina'])
    assert fixture == expected
    assert json.dumps(fixture, sort_keys=True, separators=(',', ':'), allow_nan=False) == json.dumps(expected, sort_keys=True, separators=(',', ':'), allow_nan=False)
    assert [i['instance_id'] for s in fixture['sides'] for i in s['items'] if i['item_index'] == 262] == ['P:12']

    engine_source = (D / 'SOURCE/engine.py').read_text()
    et = ast.parse(engine_source)
    engine_class = next(n for n in et.body if isinstance(n, ast.ClassDef) and n.name == 'CombatEngine')
    init = next(n for n in engine_class.body if isinstance(n, ast.FunctionDef) and n.name == '__init__')
    positions = {}
    for node in ast.walk(init):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in ('validate_runtime_inputs', 'SeededRandom'):
            positions[node.func.id] = node.lineno
    assert positions['validate_runtime_inputs'] < positions['SeededRandom']
    gt = ast.parse((D / 'SOURCE/genuine.py').read_text())
    proof = next(n for n in gt.body if isinstance(n, ast.FunctionDef) and n.name == 'validate_single_king_input_provenance')
    rngproof = next(n for n in gt.body if isinstance(n, ast.FunctionDef) and n.name == '_single_king_rng_checkpoint')
    forbidden_calls = {'SeededRandom', 'CombatEngine', 'OriginalRNG', 'GodotPCGInteger', 'initialize', 'runInputBundle', 'build'}
    for node in (proof, rngproof):
        assert not {n.func.id for n in ast.walk(node) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)} & forbidden_calls
        assert not any(isinstance(n, (ast.Yield, ast.YieldFrom)) for n in ast.walk(node))
    # Existing clock/cleanup/effects/RNG algorithms are covered by the whole old
    # module inverse and thirteen byte-identical source files, not re-executed.
    result = dict(schema='phase355-independent-static-source-review/1',
                  status='STATIC_CONSERVATION_PASS_SOURCE_ADMISSION_BLOCKED_SEPARATELY',
                  author_owner_leaves=len(owner['files']), author_owner_bytes=sum(r['size'] for r in owner['files']),
                  candidate_modules=15, byte_conserved=13, changed=changed,
                  module_conservation=conservation, baseline_old_functions=sum(r['baseline_functions'] for r in conservation),
                  fixed_A=dict(source='data/phase351-fixed-pure-input-plan/A.json', identity=pin(R / 'data/phase351-fixed-pure-input-plan/A.json'), conversion='schema only; hp/stamina to float', exact=True, King='P:12'),
                  pre_rng_validation_source_lines=positions,
                  proof_helpers_construct_or_restore_rng=False,
                  deferred='complete typed observer/schema/patch/collector/runtime adapter/model tools/host and actual11 carrier evidence',
                  candidate_imports=0, RNG_constructions=0, Engine_constructions=0, models=0, native=0, expected_reads=0)
    with (D / 'static-review.json').open('x') as f:
        json.dump(result, f, indent=2, sort_keys=True)
        f.write('\n')
    print(json.dumps(dict(status=result['status'], old_functions=result['baseline_old_functions'], byte_conserved=13)))


if __name__ == '__main__':
    main()
