"""Static independent evidence and preseal of the first8 schema controls."""
import ast
import copy
import hashlib
import json
from pathlib import Path

R = Path(__file__).resolve().parents[1]
D = R / 'data/phase357-independent-schema-review'
A = R / 'data/phase357-king-observer-schema-source'


def pin(p):
    b = p.read_bytes()
    return dict(size=len(b), sha256=hashlib.sha256(b).hexdigest())


def desc(p):
    return dict(path=str(p.relative_to(R)), **pin(p))


def write(name, value):
    with (D / name).open('x') as f:
        json.dump(value, f, indent=2, sort_keys=True)
        f.write('\n')


def main():
    D.mkdir(exist_ok=False)
    source = D / 'SOURCE'
    source.mkdir()
    assert pin(A / 'source-owner.json') == dict(size=3955, sha256='cee4404934446da8b90808c96b22b794bc78ec1e99e08ba3e1c19ef15a41b369')
    owner = json.loads((A / 'source-owner.json').read_text())
    for row in owner['files']:
        assert pin(R / row['path']) == {k: row[k] for k in ('size', 'sha256')}
    inputs = {'phase357_king_observer_schema.py': R / 'tests/phase357_king_observer_schema.py'}
    for name in ('schema-contract.json', 'record-hook-matrix.json', 'cloned-pure-source-functions.json', 'producer-requirements-and-remaining.json'):
        inputs[name] = A / name
    for name, path in inputs.items():
        with (source / name).open('xb') as f:
            f.write(path.read_bytes())
    module = (source / 'phase357_king_observer_schema.py').read_text()
    tree = ast.parse(module)
    compile(module, '<frozen-real-pure-schema>', 'exec')
    imports = []
    for node in tree.body:
        if isinstance(node, ast.Import):
            imports.extend(n.name.split('.')[0] for n in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module.split('.')[0])
    assert set(imports) == {'hashlib', 'json', 'math', 're', 'struct', 'copy', 'dataclasses', 'types'}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name):
            assert node.func.id not in {'open', 'exec', 'eval', '__import__', 'CombatEngine', 'SeededRandom', 'TapeRandom', 'OriginalRNG', 'RuntimeDTO', 'initialize', 'runInputBundle', 'build'}
        elif isinstance(node.func, ast.Attribute):
            assert node.func.attr not in {'read_bytes', 'read_text', 'write_bytes', 'write_text', 'mkdir', 'unlink', 'system', 'Popen', 'connect', 'run'}
    matrix = json.loads((A / 'record-hook-matrix.json').read_text())
    for row in matrix['original_files'].values():
        assert pin(Path(row['path'])) == {k: row[k] for k in ('size', 'sha256')}
    declarations = []
    for row in matrix['sites']:
        lines = Path(row['file']).read_text().splitlines(True)
        raw = ''.join(lines[row['line_start'] - 1:row['line_end']]).encode()
        actual = dict(size=len(raw), sha256=hashlib.sha256(raw).hexdigest())
        assert actual == {k: row[k] for k in ('size', 'sha256')}
        declarations.append(dict(site=row['site'], **actual, signature=row['signature'], arguments=row['arguments'], declared_types=row['declared_types']))
    assert len(declarations) == 103 and len(matrix['original_files']) == 15
    sources = {
        'tests/native_random_observer_patch_v7.py': R / 'tests/native_random_observer_patch_v7.py',
        '356 staged genuine.py': R / 'data/phase356-king-admission-source-repair/staged/native_replay_v8/genuine.py',
        '356 staged frame_driver.py': R / 'data/phase356-king-admission-source-repair/staged/native_replay_v7/frame_driver.py',
    }
    clones = []
    for row in json.loads((A / 'cloned-pure-source-functions.json').read_text())['functions']:
        original = sources[row['source']].read_text()
        name = row['function']
        node = [n for n in ast.parse(original).body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name == name][-1]
        text = ''.join(original.splitlines(True)[node.lineno - 1:node.end_lineno]) + '\n'
        assert hashlib.sha256(text.encode()).hexdigest() == row['sha256']
        destination = '_base_' + name if row['source'] == 'tests/native_random_observer_patch_v7.py' and name in ('validate_state', 'primitive_context', 'validate_primitive', 'validate_record') else name
        if destination != name:
            text = text.replace('def ' + name + '(', 'def ' + destination + '(', 1)
        if name == 'validate_record' and row['source'] == 'tests/native_random_observer_patch_v7.py':
            text = text.replace("'Utility/Util.gd::pickRandomElement':('random_stack:',),", "'Utility/Util.gd::pickRandomElement':('random_stack:',),\n            'Utility/Util.gd::randPitch':('invulnerability_pitch:',),")
        expected = ast.parse(text).body[0]
        if isinstance(expected, ast.ClassDef):
            expected.decorator_list = copy.deepcopy(node.decorator_list)
        actual = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name == destination][0]
        assert ast.dump(expected, include_attributes=False) == ast.dump(actual, include_attributes=False), (row['source'], name)
        clones.append(dict(source=row['source'], function=name, destination=destination, AST_equal=True))
    embedded = ast.literal_eval(next(n.value for n in tree.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'MATRIX' for t in n.targets)))
    assert set(embedded['sites']) == {x['site'] for x in declarations}
    for row in declarations:
        site = embedded['sites'][row['site']]
        assert site['arguments_exact'] == row['arguments'] and site['argument_types'] == row['declared_types']
    freeze = R / 'data/phase356-king-admission-source-repair/candidate-source-freeze.json'
    assert pin(freeze) == dict(size=2783, sha256='a135fc774658dab7f9b16d9e9955252f700c030fb0fb661d7db0c06ec3424afb')
    frozen = json.loads(freeze.read_text())
    for name in ('native_replay_v8/genuine.py', 'native_replay_v8/engine.py'):
        assert pin(freeze.parent / 'staged' / name) == frozen['files'][name]
    write('static-review.json', dict(schema='phase357-independent-static-schema-review/1', status='SOURCE_STATIC_PASS_SEMANTICS_PENDING',
        author_readback=dict(leaves=len(owner['files']), bytes=sum(x['size'] for x in owner['files'])), module=desc(source / 'phase357_king_observer_schema.py'),
        import_roots=sorted(set(imports)), no_file_network_process_candidate_calls=True,
        original_GD_files=15, declared_source_sites=103, site_declarations=declarations,
        pure_clones=clones, clone_count=len(clones), guard356_unchanged=True,
        scope='103 original-source declaration identities are not runtime coverage;no schema import/call yet'))
    contract = json.loads((source / 'schema-contract.json').read_text())
    def integer(n):
        return dict(type='int', decimal=str(n))
    plain = {}
    for key, kind in contract['state_schemas']['plain_item'].items():
        if kind == 'int':
            plain[key] = integer(1 if key == 'descriptorIndex' else 0)
        elif kind == 'float':
            plain[key] = dict(type='float', binary64_be='3ff0000000000000' if key == 'speedScale' else '0000000000000000')
        elif kind == 'bool':
            plain[key] = dict(type='bool', value=False)
        elif kind == 'dictionary':
            entries = [dict(key=integer(c), value=dict(type='dictionary', entries=[])) for c in (0, 2, 4, 7)] if key == 'currentAffectedItems' else []
            plain[key] = dict(type='dictionary', entries=entries)
        else:
            raise AssertionError((key, kind))
    fixtures = dict(plain_one=plain, plain_unknown=copy.deepcopy(plain), plain_King=copy.deepcopy(plain),
                    role_O19=dict(type='native_ref', native_id='9001', role='O:19', **{'class': 'Item'}),
                    role_O12=dict(type='native_ref', native_id='9001', role='O:12', **{'class': 'Item'}))
    fixtures['plain_unknown']['descriptorIndex'] = integer(999)
    fixtures['plain_King']['descriptorIndex'] = integer(262)
    write('synthetic-probe-fixtures.json', fixtures)
    controls = [
        dict(label='real-module-API-and-native-not-authorized', operation='API', expected='accept'),
        dict(label='plain-state-ID1-positive', operation='state', kind='plain_item', fixture='plain_one', expected='accept'),
        dict(label='public-plain-state-unknown-ID999-must-reject', operation='state', kind='plain_item', fixture='plain_unknown', expected='reject'),
        dict(label='public-plain-state-King-without-private-fields-must-reject', operation='state', kind='plain_item', fixture='plain_King', expected='reject'),
        dict(label='normal-item-ID1-positive', operation='state', kind='item', fixture='plain_one', expected='accept'),
        dict(label='normal-item-unknown-ID999-rejected', operation='state', kind='item', fixture='plain_unknown', expected='reject'),
        dict(label='fixed-O19-role-positive', operation='typed', fixture='role_O19', expected='accept'),
        dict(label='deleted-O12-role-rejected', operation='typed', fixture='role_O12', expected='reject'),
    ]
    write('preparation-first-syntax-error.json', dict(schema='phase357-independent-preparation-diagnostic/1',
        stage='inline metadata SOURCE preparation before any statement executed',
        error="SyntaxError: expected 'else' after 'if' expression;token else0", 
        correction='Write real helper SOURCE with explicit spaced conditional;compile before execution',
        schema_imports=0, schema_calls=0, files_created_by_failed_command=0))
    files = [R / 'docs/phase357_independent_schema_validation_spec.md', Path(__file__).resolve(),
             R / 'tests/phase357_independent_schema_probe.py', D / 'synthetic-probe-fixtures.json',
             D / 'static-review.json', D / 'preparation-first-syntax-error.json', *sorted(source.iterdir())]
    for p in files:
        if p.suffix == '.py':
            compile(p.read_bytes(), str(p), 'exec')
    write('probe-contract.json', dict(schema='phase357-independent-first-semantic-probe-contract/1', controls=controls,
        source_files=[desc(p) for p in files], cases=8, total_budget=80, synthetic_only=True,
        no_actual_native_values_claimed=True,
        priority='Public state validator must enforce fixed6 descriptor/subtype for every accepted Item state-kind, including plain_item;normal item dispatch is tested separately.'))
    files.append(D / 'probe-contract.json')
    write('source-owner.json', dict(schema='phase357-independent-probe-source-owner/1', files=[desc(p) for p in files]))
    for row in json.loads((D / 'source-owner.json').read_text())['files']:
        assert desc(R / row['path']) == row
    print(json.dumps(dict(source_owner=desc(D / 'source-owner.json'), declarations=103, clones=len(clones), presealed_cases=8)))


if __name__ == '__main__':
    main()
