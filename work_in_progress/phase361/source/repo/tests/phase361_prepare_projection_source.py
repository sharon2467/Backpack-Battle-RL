"""Generate/freeze projection SOURCE without importing schema or constructing input."""
from pathlib import Path
import ast
import hashlib
import json

R = Path(__file__).resolve().parents[1]
D = R / 'data/phase361-projection-sealer-source'
MODULE = R / 'tests/phase361_king_projection_sealer.py'


def identity(raw):
    return dict(size=len(raw), sha256=hashlib.sha256(raw).hexdigest())


def descriptor(path):
    assert path.is_relative_to(R) and not path.is_symlink()
    assert all(not parent.is_symlink() for parent in path.parents if parent.is_relative_to(R))
    return dict(path=str(path.relative_to(R)), **identity(path.read_bytes()))


def save(name, value):
    with (D / name).open('x') as stream:
        stream.write(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + '\n')


def assignments(path):
    return {target.id: node.value for node in ast.parse(path.read_text()).body if isinstance(node, ast.Assign)
            for target in node.targets if isinstance(target, ast.Name)}


def main():
    D.mkdir(exist_ok=False)
    assert not MODULE.exists()
    old = {}
    source_metadata = {}
    root_statuses = []
    for name, size, digest, status in (
        ('data/phase359-root-acceptance/accepted.json', 1257, '8fbcb7148ee12aa424cf101daf39ddc04606db5938c36099cb2d9e873e34a770', 'ACCEPTED_SOURCE_COMPONENT_PIPELINE_BLOCKED'),
        ('data/phase360-root-acceptance/accepted.json', 1375, '23915057cc663ca2dc9f885159c2e62780787e48d576a6f98c6ba435a306dc5e', 'ACCEPTED_SOURCE_AND_SYNTHETIC_CONTROLS_NATIVE_CLOSED'),
    ):
        path = R / name
        assert identity(path.read_bytes()) == dict(size=size, sha256=digest)
        root = json.loads(path.read_text())
        assert root['status'] == status and root['King_production_admitted'] is False
        source_metadata[name] = descriptor(path)
        root_statuses.append((descriptor(path), status))
        for key in ('review', 'owner', 'source_owner', 'freeze'):
            row = root[key]
            assert descriptor(R / row['path']) == row
            source_metadata[row['path']] = row
        source_owner = json.loads((R / root['source_owner']['path']).read_text())
        assert source_owner['root'] == str(R)
        for row in source_owner['files']:
            assert descriptor(R / row['path']) == row
            old[row['path']] = row
    for freeze_name, staged in (
        ('data/phase324-rainbow75-source/candidate-source-freeze.json', '.'),
        ('data/phase349-king-fresh-source/candidate-source-freeze.json', 'data/phase349-king-fresh-source/staged'),
        ('data/phase356-king-admission-source-repair/candidate-source-freeze.json', 'data/phase356-king-admission-source-repair/staged'),
    ):
        path = R / freeze_name
        old[freeze_name] = descriptor(path)
        files = json.loads(path.read_text())['files']
        assert len(files) == 15
        for name, expected in files.items():
            path = R / staged / name
            assert identity(path.read_bytes()) == expected
            old[str(path.relative_to(R))] = descriptor(path)
    design = R / 'docs/phase361_king_projection_sealer_source_spec.md'
    assert identity(design.read_bytes()) == dict(size=13317, sha256='ec63db9b284e0ead47979d9cefb4fce858ff3c495ef4d8270777235b2f633da0')
    old[str(design.relative_to(R))] = descriptor(design)
    source_metadata.update({name: descriptor(R / name) for name in (
        'tests/phase360_king_observer_schema.py',
        'data/phase355-king-finite-source/fixed-A-v8-fixture.json',
        'data/phase356-king-admission-source-repair/candidate-source-freeze.json')})
    schema_path = R / 'tests/phase360_king_observer_schema.py'
    assert identity(schema_path.read_bytes()) == dict(size=190693, sha256='d4229ce6d94525b5bc0b93f7ab80617b96041d65fb4cd4f425e0b07a50a4c5f6')
    engine_path = R / 'data/phase356-king-admission-source-repair/staged/native_replay_v8/engine.py'
    engine = assignments(engine_path)
    events = ast.literal_eval(engine['EVENT_TYPES'])
    stack_names = {value: name for name, value in events.items() if 100 <= value <= 110}
    assert len(stack_names) == 11 and stack_names[105] == 'Mana' and stack_names[103] == 'Vampirism'
    input_contract = R / 'tests/phase355_input_source_contract.py'
    runtime_keys = ast.literal_eval(assignments(input_contract)['RUNTIME_KEYS'].args[0])
    assert len(runtime_keys) == 17
    schema_assign = assignments(schema_path)
    source_names = ast.literal_eval(schema_assign['INPUT_FILES']) + ('king-slot-bindings.json',)
    assert len(source_names) == 12
    constants = dict(SCHEMA_ORIGIN=descriptor(schema_path), SOURCE_CONTROL_PINS=list(source_metadata.values()),
        ROOT_SOURCE_STATUSES=root_statuses, SOURCE_ORIGIN_CONTRACT=dict(schema='phase361-reviewed-SOURCE-origins/1',
            controls=list(source_metadata.values()), scope='SOURCE_ACCEPTANCES_ONLY_NOT_CAPTURE_OR_MODEL_PERMISSION'),
        SOURCE_NAMES=source_names, RUNTIME_KEYS=runtime_keys, STACK_NAMES=stack_names, ZERO_BITS='0000000000000000',
        AUXILIARY_LEMMA=ast.literal_eval(engine['AUX_LEMMA']), TERMINAL_PROFILE='source-two-physics-idle-pre-internal/1')
    prefix = '"""Finite King projection/sealer SOURCE; native reader remains closed."""\n\n'
    prefix += ''.join(name + ' = ' + repr(value) + '\n' for name, value in constants.items())
    template_path = R / 'tests/phase361_projection_sealer_template.py'
    generated = prefix + '\n' + template_path.read_text()
    with MODULE.open('x') as stream:
        stream.write(generated)
    for path in (MODULE, template_path, Path(__file__)):
        compile(path.read_bytes(), str(path), 'exec')
    template_tree, generated_tree = [ast.parse(path.read_text()) for path in (template_path, MODULE)]
    funcs = {node.name: ast.dump(node, include_attributes=False) for node in template_tree.body if isinstance(node, ast.FunctionDef)}
    actual = {node.name: ast.dump(node, include_attributes=False) for node in generated_tree.body if isinstance(node, ast.FunctionDef)}
    assert funcs == actual
    # Inspect calls/import names as SOURCE only, never load these modules.
    calls = sorted({ast.unparse(node.func) for node in ast.walk(generated_tree) if isinstance(node, ast.Call)})
    assert not any('CombatEngine' in call or 'TapeRandom' in call or 'SeededRandom' in call or call.endswith(('.initialize', '.step', '.run')) for call in calls)
    assert 'NativeRandomObserver' not in generated and '/workspace/' not in generated
    fields = {
        'schema/mode/profile_id': ('frozen code-approved discriminants', 'genuine.validate_profile / validate_runtime_inputs'),
        'checkpoint': ('actual activate enter clocks / joined external header', 'activate_from_checkpoint util_time'),
        'environment': ('full fixed60 unpaused fresh/UI guard', 'validate_runtime_inputs / scaffold'),
        'nodes': ('actual continuous fresh paths/positions/priority/config only', 'build_runtime_scaffold'),
        'timer_lineage': ('full actual fresh provenance then code semantic fresh_configured', '_validate_runtime_nodes; constructor private state'),
        'initial_items': ('source constructor zero limiters; pre/act gate, never prepared state', 'activate_from_checkpoint four limiters'),
        'prepare_order/activate_order': ('actual Game entry refs + proven native aliases, original order', 'prepare / activate iteration'),
        'terminal_profile': ('frozen SOURCE algorithm name, no endpoint', 'finite FrameDriver cleanup barrier'),
        'frame_clock': ('actual header and unchanged physical physics/idle passes', 'finite FrameDriver; strict exhaustion'),
        'king_particles': ('full validated fresh native topology/default configuration', 'constructor particle_facts and actual effects'),
        'root_node/processing_nodes': ('actual fresh processing/ancestry flags and nodes', 'scaffold / ordinary membership / snapshots'),
        'inactive_auxiliaries': ('actual fresh config plus source noRage lemma', 'validator and inactive Timer snapshots'),
        'ui_authority': ('raw complete UI carrier, no simulated UI input', 'validation-only _validate_single_king_processing_inputs; retained in RuntimeDTO'),
        'draws': ('actual primitive returns/args/bits, original physical order', 'Tape ABI only; no production seed derivation'),
        'synthetic_seed': ('NULL constant for genuine', 'observed.run_input_bundle validates before constructing RNG'),
    }
    save('field-dataflow-matrix.json', dict(schema='phase361-field-writer-reader-matrix/1', fields={
        key: dict(writer=pair[0], reader=pair[1]) for key, pair in fields.items()}, runtime_keys=list(runtime_keys),
        engine_SOURCE=descriptor(engine_path), observed_SOURCE=descriptor(engine_path.parent / 'observed.py'),
        forbidden_state_inputs=['prepared source_resources/cache/private defaults', 'RNGcheckpoint seed/state', 'terminal endpoint/final/history/events'],
        ui='Kept only for old validation ABI and storage; no UI command replay or footer-driven termination',
        source_proof_only=True))
    save('source-input-pins.json', dict(source_controls=list(source_metadata.values()), code_derivation=[
        descriptor(engine_path), descriptor(engine_path.parent / 'observed.py'), descriptor(engine_path.parent / 'randomness.py'), descriptor(input_contract)],
        frozen_design=descriptor(design), imported_runtime_or_schema=False))
    save('pending-interfaces.json', dict(schema='phase361-source-pending/1',
        native_reader='UNCONDITIONAL_HOST_CODE_PENDING_BEFORE_RELEASE_OR_CAPTURE_READ',
        actual_release_instances=0, actual12_positive=False,
        missing=['actual collector and fixedA placement/writer/archive SOURCE', 'actual host/lease/config SOURCE',
                 'new candidate shared profile-patch-schema-collector-projection identity binding', 'root native and actual input-only releases'],
        pure_projection='Synthetic SOURCE testing only after independent gate; no runtime admission',
        seal='Engineering pack/readback only; no model/native permission',
        future_opening='New SOURCE and actual joint identity verification, never caller bool or old307 patch'))
    for name, expected in old.items():
        assert descriptor(R / name) == expected, name
    for row in source_metadata.values():
        assert descriptor(R / row['path']) == row
    save('old-source-readback.json', dict(status='ALL_REFERENCED_OLD_SOURCE_LEAVES_IDENTICAL_BEFORE_AFTER', files=list(old.values()),
        scope='canonical15 +34915 +35615 +359/360 complete source owners + frozen361design'))
    save('static-source-validation.json', dict(schema='phase361-static-SOURCE-validation/1', compile_without_import=True,
        template_functions_AST_identical=len(funcs), candidate_or_RNG_calls_absent=True,
        source_paths='explicit source_root/lawful_dir/output_dir; module contains no /workspace literal',
        actual_source_acceptances_only=[row[0] for row in root_statuses],
        counts=dict(schema_imports=0, schema_API_calls=0, projections=0, bundles_constructed=0, seal_calls=0,
                    RNG=0, Engine=0, models=0, native=0, Godot=0, capture_reads=0, expected_reads=0, pool_writes=0)))
    files = [Path(__file__), template_path, MODULE, R / 'docs/phase361_projection_sealer_implementation_spec.md']
    save('projection-source-freeze.json', dict(schema='phase361-projection-sealer-source-freeze/1',
        status='SOURCE_READY_INDEPENDENT_REVIEW_PENDING_NO_ACTUAL_INPUT_OR_ADMISSION', files=[descriptor(path) for path in files],
        source_origins=constants['SOURCE_ORIGIN_CONTRACT'], runtime356='UNCHANGED_CLOSED', pipeline_admitted=False))
    save('summary.json', dict(schema='phase361-author-SOURCE-handoff/1', status='SOURCE_READY_PENDING_INDEPENDENT_REVIEW',
        module=descriptor(MODULE), freeze=descriptor(D / 'projection-source-freeze.json'),
        public_APIs=['read_and_validate_sources', 'project_fixture_and_runtime', 'project_primitives', 'seal_once'],
        native_reader_closed=True, pure_projection_executed=False, actual_input_bundle_created=False,
        seal_executed=False, runtime_or_canonical_modified=False, independent_FINAL=False,
        formal_items=75, King_production_admitted=False, full_engine_RL='IN_PROGRESS', no_more_writes=True))
    own = files + sorted(path for path in D.rglob('*') if path.is_file())
    rows = [descriptor(path) for path in own]
    assert len({row['path'] for row in rows}) == len(rows)
    save('source-owner.json', dict(schema='phase361-source-owner/1', root=str(R), files=rows,
                                 scope='new SOURCE only; not independent FINAL or runtime/native authority'))
    for row in json.loads((D / 'source-owner.json').read_text())['files']:
        assert descriptor(R / row['path']) == row
    print(json.dumps(dict(status='SOURCE_FROZEN_ALL_LEAVES_READ_BACK', module=descriptor(MODULE),
        freeze=descriptor(D / 'projection-source-freeze.json'), owner=descriptor(D / 'source-owner.json'),
        leaves=len(rows), bytes=sum(row['size'] for row in rows))))


if __name__ == '__main__':
    main()
