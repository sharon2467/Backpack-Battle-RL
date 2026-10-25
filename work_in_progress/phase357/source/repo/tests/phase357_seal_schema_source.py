"""Compile/AST/identity SOURCE seal; never import the generated schema or runtime."""
from pathlib import Path
import ast
import builtins
import hashlib
import json

R = Path(__file__).resolve().parents[1]
D = R / 'data/phase357-king-observer-schema-source'
MODULE = R / 'tests/phase357_king_observer_schema.py'


def pin(path):
    raw = path.read_bytes()
    return dict(size=len(raw), sha256=hashlib.sha256(raw).hexdigest())


def save(name, value):
    with (D / name).open('x') as stream:
        stream.write(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + '\n')


def main():
    text = MODULE.read_text()
    tree = ast.parse(text)
    compile(text, str(MODULE), 'exec')
    nodes = {node.name: node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.ClassDef))}
    assignments = {}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    assignments[target.id] = node.value
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.add(node.module)
    assert imports <= {'hashlib', 'json', 'math', 're', 'struct', 'copy', 'dataclasses', 'types'}, imports
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            assert node.func.id not in {'open', 'eval', 'exec', 'compile', '__import__', 'CombatEngine', 'CombatRandom', 'TapeRandom', 'SeededRandom'}
    bound = set(dir(builtins))
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            bound.add(node.id)
        elif isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            bound.add(node.name)
        elif isinstance(node, ast.arg):
            bound.add(node.arg)
        elif isinstance(node, ast.alias):
            bound.add(node.asname or node.name.split('.')[0])
    missing = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load)} - bound
    assert not missing, missing
    apis = ['strict_json_loads', 'validate_typed', 'validate_state', 'validate_record',
            'primitive_context', 'validate_primitive', 'decode_clock', 'decode_sources',
            'validate_source_carriers', 'validate_observation_records', 'validate_terminal_evidence']
    assert all(name in nodes for name in apis)
    assert all('native_profile' not in {arg.arg for arg in nodes[name].args.args} for name in apis)
    index = ast.literal_eval(assignments['ITEM_INDEX_BY_ROLE'])
    fixture = ast.literal_eval(assignments['FIXED_FIXTURE'])
    expected = {item['instance_id']: item['item_index'] for side in fixture['sides'] for item in side['items']}
    assert index == expected and len(index) == 39 and 'O:12' not in index and 'O:19' in index
    contract = ast.literal_eval(assignments['CONTRACT'])
    matrix = ast.literal_eval(assignments['MATRIX'])
    assert contract['state_schemas']['character']['buffProtectStacks'] == 'int'
    assert contract['state_schemas']['king']['protectedBuffs'] == 'float'
    assert contract['state_schemas']['king']['manaCost'] == 'float'
    assert matrix['sites']['Core/Character.gd::useMana']['argument_types']['amount'] == 'int'
    assert 'amount' not in matrix['sites']['Items/Item.gd::useMana']['argument_types']
    for site, spec in matrix['sites'].items():
        assert spec['state_schema'] in contract['state_schemas'], site
        assert len(spec['arguments_exact']) == len(set(spec['arguments_exact']))
        assert set(spec['argument_types']) <= set(spec['arguments_exact'])
    source = R / 'data/phase356-king-admission-source-repair'
    freeze = json.loads((source / 'candidate-source-freeze.json').read_text())
    for name, identity in freeze['files'].items():
        assert pin(source / 'staged' / name) == identity
    host_genuine = ast.parse((source / 'staged/native_replay_v8/genuine.py').read_text())
    gate = next(node for node in host_genuine.body if isinstance(node, ast.FunctionDef) and node.name == 'require_single_king_admission')
    assert len(gate.body) == 2 and isinstance(gate.body[-1], ast.Raise)
    assert gate.args.args == [] and gate.args.kwonlyargs == []
    helper_sources = ['tests/phase357_prepare_schema_source.py', 'tests/phase357_schema_extension_source.py', 'tests/phase357_seal_schema_source.py']
    for name in helper_sources:
        compile((R / name).read_bytes(), name, 'exec')
    source_files = [
        'tests/native_random_observer_patch_v7.py', 'tests/phase298_native_sink.gd',
        'data/phase040-observer7-implementation/prebody-contract.json',
        'data/phase040-observer7-implementation/body-site-matrix.json',
        'data/phase095-goobert-native-preparation/source-additions.json',
        'tests/native_observer7_profile_095.py', 'tests/phase307_native_profile.py',
        'tests/native_observer7_profile_111.py', 'tests/native_observer7_profile_154.py',
        'tests/native_random_observer_sink_v7_154.gd', 'tests/phase355_input_source_contract.py',
        'data/phase355-king-finite-source/fixed-A-v8-fixture.json',
        'data/phase356-king-admission-source-repair/staged/native_replay_v8/genuine.py',
        'data/phase356-king-admission-source-repair/staged/native_replay_v7/frame_driver.py',
        'data/phase356-king-admission-source-repair/candidate-source-freeze.json',
        'data/phase356-root-acceptance/accepted.json',
        'data/phase357-independent-schema-preparation/owned-files.json',
        'data/phase357-independent-schema-preparation/typed-partition-matrix.json',
        'data/phase357-independent-schema-preparation/controls-contract.json',
    ]
    save('source-input-pins.json', dict(schema='phase357-source-input-pins/1', files=[dict(path=name, **pin(R / name)) for name in source_files],
                                      inputs='STATIC_SOURCE_ONLY_NO_ACTUAL_OR_EXPECTED', runtime_356_15_unchanged=True))
    save('source-validation.json', dict(schema='phase357-static-source-validation/1', module=pin(MODULE),
        compile='PASS_NO_IMPORT', actual_schema_functions_called=0, pure_semantic_controls_executed=0,
        candidate_imports=0, RNG_constructions=0, Engine_constructions=0, input_builds=0, models=0, native=0,
        import_closure=sorted(imports), no_file_network_process_candidate_calls=True,
        conservative_static_missing_globals=[], public_implemented_APIs=apis,
        site_count=len(matrix['sites']), roles='exact39 from frozen A includingO19 excludingO12',
        stored_protection_INT_and_Mana_entry_coercion_STATIC=True, shared356_gate='UNCHANGED_UNCONDITIONAL_CLOSED'))
    save('schema-source-freeze.json', dict(schema='phase357-typed-schema-source-freeze/1',
        module=dict(path=str(MODULE.relative_to(R)), **pin(MODULE)),
        helpers=[dict(path=name, **pin(R / name)) for name in helper_sources],
        observer_version='7-king-single-A-355', profile='observer7-355-native-single-king-A/1',
        admission='356_GATE_REMAINS_CLOSED', schema_controls='NOT_EXECUTED_AUTHOR_SOURCE_ONLY',
        no_more_module_writes=True))
    print(json.dumps(dict(status='SCHEMA_SOURCE_COMPILE_AST_FROZEN', module=pin(MODULE), freeze=pin(D / 'schema-source-freeze.json'), schema_calls=0)))


if __name__ == '__main__':
    main()
