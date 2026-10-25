"""Pure text/AST SOURCE derivation; no schema/runtime import or API calls."""
from pathlib import Path
import ast
import difflib
import hashlib
import json
import re

R = Path(__file__).resolve().parents[1]
D = R / 'data/phase360-schema-auxiliary-binding-source'
B = Path('/workspace/godotsteam-startup-20261013/baseline/Backpack Battles')
BASE_SCHEMA = R / 'tests/phase358_king_observer_schema.py'
MODULE = R / 'tests/phase360_king_observer_schema.py'


def identity(raw):
    return dict(size=len(raw), sha256=hashlib.sha256(raw).hexdigest())


def descriptor(path):
    assert path.is_relative_to(R) and not path.is_symlink()
    assert all(not parent.is_symlink() for parent in path.parents if parent.is_relative_to(R))
    return dict(path=str(path.relative_to(R)), **identity(path.read_bytes()))


def save(name, value):
    with (D / name).open('x') as stream:
        stream.write(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + '\n')


def main():
    D.mkdir(exist_ok=False)
    assert not MODULE.exists()
    old_files = {}
    for path, required in (
        (BASE_SCHEMA, dict(size=259033, sha256='d8dabd87ffe0352ceb886ad3f25c2548d1e4412d13538da813ba77f8115947a7')),
        (R / 'data/phase359-king-producer-source/producer-source-freeze.json', dict(size=43099, sha256='419a79c51f9a5c92c56edc4a2fd0ca7fd829f0471f747652015a39e26035204a')),
        (R / 'docs/phase360-schema-auxiliary-binding-spec.md', dict(size=13312, sha256='fe78aeb31feafebc1210d786500c39f7dfbd1bc518b6d1efc6523a4e13797528')),
    ):
        assert identity(path.read_bytes()) == required, path
        old_files[str(path.relative_to(R))] = descriptor(path)
    for name in ('data/phase358-king-schema-source-repair/source-owner.json', 'data/phase359-king-producer-source/source-owner.json'):
        owner = R / name
        old_files[name] = descriptor(owner)
        value = json.loads(owner.read_text())
        assert value['root'] == str(R)
        for row in value['files']:
            actual = descriptor(R / row['path'])
            assert actual == row, row['path']
            old_files[row['path']] = actual
    for freeze, staged in (
        ('data/phase324-rainbow75-source/candidate-source-freeze.json', '.'),
        ('data/phase349-king-fresh-source/candidate-source-freeze.json', 'data/phase349-king-fresh-source/staged'),
        ('data/phase356-king-admission-source-repair/candidate-source-freeze.json', 'data/phase356-king-admission-source-repair/staged'),
    ):
        fp = R / freeze
        old_files[freeze] = descriptor(fp)
        files = json.loads(fp.read_text())['files']
        assert len(files) == 15
        for name, expected in files.items():
            path = R / staged / name
            assert identity(path.read_bytes()) == expected, path
            old_files[str(path.relative_to(R))] = descriptor(path)
    source = BASE_SCHEMA.read_text()
    original_tree = ast.parse(source)
    assignments = {target.id: node for node in original_tree.body if isinstance(node, ast.Assign)
                   for target in node.targets if isinstance(target, ast.Name)}
    matrix_node = assignments['MATRIX']
    matrix = ast.literal_eval(matrix_node.value)
    previous_matrix = ast.literal_eval(matrix_node.value)
    inherited307 = json.loads((R / 'data/phase307-observer-chance-source/native-source-freeze.json').read_text())
    goobert = R / inherited307['source_locations']['Items/Goobert.gd']['before']
    raw = goobert.read_bytes()
    expected = inherited307['files']['Items/Goobert.gd']
    assert identity(raw) == dict(size=expected['before_size'], sha256=expected['before_sha256'])
    assert (B / 'Items/Goobert.gd').read_bytes() == raw
    gd_lines = raw.decode().splitlines(keepends=True)
    repairs = []
    for name, args in (('prepare', []), ('onItemActivated', ['event']), ('doCooldownEffect', [])):
        site = 'Items/Goobert.gd::' + name
        assert site not in matrix['sites']
        positions = [i for i, line in enumerate(gd_lines) if re.match(r'^func ' + name + r'\(', line)]
        assert len(positions) == 1
        start = positions[0]
        stop = start + 1
        while stop < len(gd_lines) and (not gd_lines[stop].strip() or gd_lines[stop].startswith(('\t', '#'))):
            stop += 1
        body = ''.join(gd_lines[start:stop])
        assert gd_lines[start].rstrip() == 'func ' + name + '(' + ', '.join(args) + '):'
        assert not re.search(r'^\t+return\b', body, re.M)
        spec = dict(channel='runtime', state_schema='goobert', arguments_exact=args, argument_types={}, explicit_returns=[])
        matrix['sites'][site] = spec
        repairs.append(dict(site=site, spec=spec, source=descriptor(goobert), line_start=start + 1, line_end=stop,
                            signature=gd_lines[start].rstrip(), function=identity(body.encode()),
                            event_type='Unannotated original GD Variant; actual typed event_ref preserved, no invented Node/Timer annotation',
                            partition='EXPECTED_RUNTIME_ONLY_NOT_NEW_INPUT_CHANNEL'))
    assert len(matrix['sites']) == 106 and len(previous_matrix['sites']) == 103
    unpatched = {key: value for key, value in matrix['sites'].items() if key in previous_matrix['sites']}
    assert unpatched == previous_matrix['sites']
    for key in previous_matrix:
        if key != 'sites':
            assert matrix[key] == previous_matrix[key]
    slot_path = R / 'data/phase359-king-producer-source/fixed-slot-map.json'
    fixed_plan = json.loads(slot_path.read_text())
    assert len(fixed_plan) == 39 and {row['instance_id'] for row in fixed_plan} == set(ast.literal_eval(assignments['SINGLE_KING_ROLES'].value.args[0]))
    source_contract = dict(schema='phase360-binding-source-contract/1',
        schema_origin=descriptor(BASE_SCHEMA), producer_source_origin=descriptor(R / 'data/phase359-king-producer-source/producer-source-freeze.json'),
        fixed_slot_map=descriptor(slot_path), fixed_fixture=descriptor(R / 'data/phase355-king-finite-source/fixed-A-v8-fixture.json'),
        evidence_policy='SOURCE_ORIGIN_ONLY_NOT_INDEPENDENT_ACCEPTANCE_OR_RUNTIME_ADMISSION')
    lines = source.splitlines(keepends=True)
    generated_base = ''.join(lines[:matrix_node.lineno - 1]) + 'MATRIX=' + repr(matrix) + '\n' + ''.join(lines[matrix_node.end_lineno:])
    prefix = ('\n\n# phase360 auxiliary SOURCE interface; no projection or admission.\n'
              'BINDING_MAX_BYTES = 2097152\nBINDING_FIXED_PLAN = ' + repr(fixed_plan)
              + '\nBINDING_SOURCE_CONTRACT = ' + repr(source_contract) + '\n\n')
    extension_path = R / 'tests/phase360_binding_schema_extension.py'
    extension = extension_path.read_text()
    published = ('\n\nschema.validate_binding_carrier = validate_binding_carrier\n'
                 'schema.join_binding_provenance = join_binding_provenance\n'
                 'schema.validate_sources_with_binding = validate_sources_with_binding\n')
    result = generated_base + prefix + extension + published
    with MODULE.open('x') as stream:
        stream.write(result)
    result_tree = ast.parse(result)
    originals = {node.name: ast.dump(node, include_attributes=False) for node in original_tree.body if isinstance(node, (ast.FunctionDef, ast.ClassDef))}
    derived = {node.name: ast.dump(node, include_attributes=False) for node in result_tree.body if isinstance(node, (ast.FunctionDef, ast.ClassDef))}
    assert all(derived[name] == node for name, node in originals.items())
    prefix_tree = ast.parse(generated_base)
    for old, new in zip(original_tree.body, prefix_tree.body):
        if old is matrix_node:
            continue
        assert ast.dump(old, include_attributes=False) == ast.dump(new, include_attributes=False)
    assert len(prefix_tree.body) == len(original_tree.body)
    # The exact inverse replaces only the declared assignment and removes the append.
    inverse = ''.join(lines[:matrix_node.lineno - 1]) + ''.join(lines[matrix_node.lineno - 1:matrix_node.end_lineno]) + ''.join(lines[matrix_node.end_lineno:])
    assert inverse == source
    for path in (BASE_SCHEMA, MODULE, extension_path, Path(__file__)):
        compile(path.read_bytes(), str(path), 'exec')
    patch = ''.join(difflib.unified_diff(source.splitlines(keepends=True), result.splitlines(keepends=True),
                                       fromfile='frozen358/schema.py', tofile='source360/schema.py'))
    with (D / 'schema-source.patch').open('x') as stream:
        stream.write(patch)
    save('goobert-three-site-source-map.json', dict(repairs=repairs, source_sites_are_not_coverage=True,
        delegate_paths=['_base_validate_record', 'validate_record', '_validate_call_pairs', 'validate_observation_records', 'schema.MATRIX'],
        argument_policy='Actual original unannotated event stays typed Variant; no new primitive ABI or domain added'))
    save('source-contract.json', source_contract)
    save('fixed-slot-map.json', fixed_plan)
    save('api-contract.json', dict(schema='phase360-binding-source-API/1', APIs={
        'validate_binding_carrier(binding_bytes,fixed_plan)': 'closed359 DTO/local identity+geometry+order proof only',
        'join_binding_provenance(decoded11,binding,source_contract)': 'fourchannel typed/order gates plus source relationships; not replacement for whole11 source/fresh/UI/clock validation',
        'validate_sources_with_binding(raw11,binding_bytes,source_contract)': 'whole11 inherited validators then auxiliary join; proof-only, no bundle/projection/admission'},
        input_names='Original eleven exact names unchanged; king-slot-bindings.json is a separate explicit raw argument',
        raw_conservation='No row/nativeID/NULLrole/stamp/sequence/ref order mutation; raw source SHA returned',
        actual_full12_carrier_positive=False, original_schema_functions_AST_conserved=len(originals),
        source_contract_is_acceptance=False, proposed_359_source_review='PENDING_NOT_ASSUMED'))
    save('remaining-obligations.json', dict(schema='phase360-pending-obligations/1',
        pending=['Independent new schema synthetic controls have not run', '359 producer SOURCE independent review pending',
                 'No complete actual12 source-carrier positive, no collector or input projection',
                 'No inventory-node second direct observation/binding stamp in359: SOURCE getter/control-flow relation only; no invented values',
                 'Projection/sealer/runtime profile-patch binding/host and native release are separate future blocks'],
        unchanged='356 shared unconditional admission remains closed; canonical75 and all old sources unchanged',
        no_more_SOURCE_work_after_handoff=True))
    for name, expected in old_files.items():
        assert descriptor(R / name) == expected, name
    save('old-source-readback.json', dict(status='ALL_OLD_REFERENCED_LEAVES_READ_BEFORE_AND_AFTER_NO_CHANGE', files=list(old_files.values()),
        scope='canonical15 from324;349staged15;356staged15;358/359 complete source owners and all leaves; frozen360design'))
    save('source-validation.json', dict(schema='phase360-source-only-static-validation/1', python_compile_without_import=True,
        original_functions_classes_AST_identical=len(originals), original_module_except_MATRIX_append_AST_identical=True,
        original103_site_entries_unchanged=True, all_other_MATRIX_keys_unchanged=True,
        new_sites=3, native_authorized=False, counts=dict(schema_imports=0, schema_API_calls=0, carrier_constructions=0,
            candidate_imports=0, RNG=0, Engine=0, models=0, Godot=0, native=0, capture_reads=0, expected_reads=0, pool_writes=0)))
    source_files = [R / name for name in ('tests/phase360_prepare_binding_schema_source.py', 'tests/phase360_binding_schema_extension.py',
        'tests/phase360_king_observer_schema.py', 'docs/phase360_schema_binding_implementation_spec.md')]
    save('schema-source-freeze.json', dict(schema='phase360-auxiliary-binding-source-freeze/1', status='SOURCE_ONLY_INDEPENDENT_TESTS_PENDING',
        files=[descriptor(path) for path in source_files], origin=source_contract,
        patch=descriptor(D / 'schema-source.patch'), runtime_or_native_admission=False))
    save('summary.json', dict(schema='phase360-source-handoff/1', status='AUTHOR_SOURCE_READY_FOR_INDEPENDENT_SCHEMA_REVIEW',
        schema_module=descriptor(MODULE), freeze=descriptor(D / 'schema-source-freeze.json'),
        old_functions_classes_AST_conserved=len(originals), old103_sites_conserved=True, added_sites=3,
        APIs=['validate_binding_carrier', 'join_binding_provenance', 'validate_sources_with_binding'],
        actual_full12_source_carrier_positive=False, producer359_independent_accepted=False,
        projection_implemented=False, runtime_admission_changed=False, canonical_writes=0, independent_FINAL=False,
        full_engine_RL='IN_PROGRESS', no_more_writes=True))
    own = source_files + sorted(path for path in D.rglob('*') if path.is_file())
    rows = [descriptor(path) for path in own]
    assert len({row['path'] for row in rows}) == len(rows)
    save('source-owner.json', dict(schema='phase360-source-owner/1', root=str(R), files=rows,
        scope='new SOURCE/schema interfaces only; not independent FINAL and no runtime/native admission'))
    for row in json.loads((D / 'source-owner.json').read_text())['files']:
        assert descriptor(R / row['path']) == row
    print(json.dumps(dict(status='SOURCE_ONLY_ALL_OWNER_LEAVES_READ_BACK', module=descriptor(MODULE),
        owner=descriptor(D / 'source-owner.json'), freeze=descriptor(D / 'schema-source-freeze.json'), leaves=len(rows), bytes=sum(row['size'] for row in rows))))


if __name__ == '__main__':
    main()
