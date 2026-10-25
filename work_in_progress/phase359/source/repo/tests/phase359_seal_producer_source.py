"""Seal generated observer SOURCE and its provenance; never import a runtime."""
from pathlib import Path
import ast
import hashlib
import json
import re

R = Path(__file__).resolve().parents[1]
D = R / 'data/phase359-king-producer-source'
B = Path('/workspace/godotsteam-startup-20261013/baseline/Backpack Battles')


def identity(raw):
    return dict(size=len(raw), sha256=hashlib.sha256(raw).hexdigest())


def descriptor(path):
    return dict(path=str(path.relative_to(R)) if path.is_relative_to(R) else str(path), **identity(path.read_bytes()))


def save(name, value):
    with (D / name).open('x') as stream:
        stream.write(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + '\n')


def method(source, name):
    lines = source.splitlines(keepends=True)
    found = [i for i, line in enumerate(lines) if re.match(r'^\t*func ' + re.escape(name) + r'\(', line)]
    assert len(found) == 1, name
    start = found[0]
    indent = len(lines[start]) - len(lines[start].lstrip('\t'))
    end = start + 1
    while end < len(lines):
        text = lines[end].lstrip()
        if text.strip() and not text.startswith('#') and len(lines[end]) - len(text) <= indent:
            break
        end += 1
    body = ''.join(lines[start:end])
    return dict(line=start + 1, body=body, **identity(body.encode()))


def main():
    source = R / 'tests/phase358_king_observer_schema.py'
    tree = ast.parse(source.read_text())
    assigned = {target.id: node.value for node in tree.body if isinstance(node, ast.Assign)
                for target in node.targets if isinstance(target, ast.Name)}
    contract, matrix = [ast.literal_eval(assigned[key]) for key in ('CONTRACT', 'MATRIX')]
    delta = json.loads((D / 'required-schema-delta.json').read_text())
    for row in delta['inherited_sites']:
        matrix['sites'][row['site']] = dict(channel='runtime', state_schema='goobert', arguments_exact=row['arguments'])
    previous = json.loads((R / 'data/phase307-observer-chance-source/native-source-freeze.json').read_text())
    final = json.loads((D / 'final-producer-patch-report.json').read_text())
    ledger = json.loads((D / 'new-edits-inverse-ledger.json').read_text())
    # Exact full-file inverse, not a permissive observer-line stripping algorithm.
    reverted = {name: (D / 'after-source' / name).read_bytes() for name in final['paths']}
    for edit in reversed(ledger['edits']):
        assert reverted[edit['path']] == edit['after'].encode(), edit['label']
        reverted[edit['path']] = edit['before'].encode()
    originals = {}
    inherited = []
    for name, pins in final['paths'].items():
        assert identity((D / 'after-source' / name).read_bytes()) == pins['after'], name
        if name in previous['files']:
            old = previous['files'][name]
            before_path = previous['source_locations'][name]['before']
            if name != 'native_random_observer_sink_v7.gd':
                assert identity(reverted[name]) == dict(size=old['after_size'], sha256=old['after_sha256']), name
            if before_path is not None:
                assert identity((R / before_path).read_bytes()) == pins['before'], name
                assert (B / name).read_bytes() == (R / before_path).read_bytes(), name
                originals[name] = descriptor(R / before_path)
            if pins['after'] == dict(size=old['after_size'], sha256=old['after_sha256']):
                inherited.append(name)
        else:
            assert (B / name).read_bytes() == reverted[name], name
            originals[name] = descriptor(B / name)
    sites = []
    for site, spec in matrix['sites'].items():
        path, name = site.split('::')
        raw = (B / path).read_text()
        block = method(raw, '_init' if name == 'TemporaryStacks._init' else name)
        signature = block['body'].split(':\n', 1)[0]
        sites.append(dict(site=site, state_schema=spec['state_schema'], fields=contract['state_schemas'][spec['state_schema']],
                          channel=spec['channel'], arguments_exact=spec['arguments_exact'], original_signature=signature,
                          original_function=block, original_file=originals[path],
                          observation='callee entry after actual GD argument binding; paired explicit/implicit return on original path',
                          partition='INPUT_SOURCE_PROOF' if spec['channel'] in ('input', 'lineage', 'metadata') else 'EXPECTED_OBSERVATION_ONLY',
                          schema358_supported=site not in {row['site'] for row in delta['inherited_sites']}))
    save('record-hook-source-matrix.json', dict(schema='phase359-record-hook-source-matrix/1', sites=sites,
        count_is='DECLARED_SOURCE_SITES_NOT_RUNTIME_COVERAGE', original_sources=originals,
        computed_and_direct_field_matrix=descriptor(D / 'field-getter-source-matrix.json'),
        bindings_query_closure=descriptor(D / 'binding-query-source.json'),
        primitives=contract['primitive_sites'], return_semantics=contract['return_semantics'],
        scene_ready='scene_instance and generic ready preserve actual nativeID/stamp/sequence and NULL prebinding role; no fake fullready Timer state'))
    sources = [
        'tests/phase358_king_observer_schema.py', 'tests/native_random_observer_sink_v7_154.gd',
        'data/phase307-observer-chance-source/native-source-freeze.json',
        'data/phase353-king-native-source-plan/owned-files.json',
        'data/phase356-king-admission-source-repair/candidate-source-freeze.json',
        'data/phase358-king-schema-source-repair/schema-source-freeze.json',
        'data/phase351-fixed-pure-input-plan/A.json',
        'data/phase355-king-finite-source/fixed-A-v8-fixture.json',
        'data/phase321-rainbow-king-source-plan/catalog-literal-for-layout-geometry.json',
        'data/phase359-independent-producer-preparation/contract.json',
    ]
    queries = ['Core/Inventory.gd', 'Items/GemSocket.gd', 'Utility/DamageResult.gd', 'Utility/DamageSource.gd', 'Core/CombatEvent.gd', 'Items/ItemDescriptor.gd']
    for name in queries:
        text = (B / name).read_text()
        assert not re.search(r'^func _get\(', text, re.M) and 'setget' not in text
    save('source-input-pins.json', dict(sources=[descriptor(R / path) for path in sources],
        extra_readonly_originals=[descriptor(B / path) for path in queries],
        original_GD_before=originals, source_getter_matrix=descriptor(D / 'field-getter-source-matrix.json')))
    save('remaining-interfaces.json', dict(schema='phase359-unaccepted-source-interfaces/1', status='SOURCE_ONLY_NOT_NATIVE_READY',
        current_runtime_admission='356_UNCONDITIONAL_PENDING_GUARD_UNCHANGED',
        required=[
            dict(layer='schema', delta='Add three actual inherited Goobert sites; preserve all original SOURCE typed signatures and no silent filtering', source=descriptor(D / 'required-schema-delta.json')),
            dict(layer='schema/adapter', delta='Define and verify king-slot-bindings.json auxiliary twelfth proof; join unchanged early NULL-role rows by nativeID with actual geometry/inventory/birth proof; never rewrite raw roles/stamps/sequence or trust a verified bool'),
            dict(layer='collector', delta='Call begin_fixture_window with frozen fixed-slot-map before selected births, place exact39 slots, call bind_fixed_inventory before prepare; retain proof and unselected diagnostic rows without making either model input'),
            dict(layer='collector', delta='Poll actual source_completion_receipt; no deferred finish; export remaining actual full events/history/final and preserve first observer failure; this producer does not implement collector, fixture JSON writers, process launch or archive'),
            dict(layer='SOURCE conformance', delta='Independent changed-source review, schema conformance and GD parse/VM still required; no Godot parser or schema API called by author'),
            dict(layer='input adapter', delta='Validate new raw proof/fresh/clock/UI and strip all prepared resources, RNG checkpoint, alias proof and expected snapshots; only lawful initial fixture/topology/exogenous clock/primitive returns may reach model'),
            dict(layer='patch/profile/host', delta='Create actual new producer+collector/schema identity binding under future SOURCE gate. Must not open356 by boolean or accept旧307 patch; host/unique attempt/native release remains absent'),
        ],
        model_input_forbidden=['king-slot-bindings.json as user state', 'king-rng-checkpoint seed/state', 'source_resources prepared values', 'king-post-cleanup-source.json', 'king-final-source.json', 'king-capture-endpoint.json', 'runtime/allocation/event/history/final channels'],
        current_evidence='No actual native IDs, sampled clocks, source carrier positives, clean-exit claim, capture or battle outputs were created'))
    tools = [R / name for name in ('tests/phase359_generate_producer_source.py', 'tests/phase359_finalize_producer_source.py',
                                   'tests/phase359_seal_producer_source.py', 'tests/phase359_sink_extension_source.gd')]
    for path in tools:
        if path.suffix == '.py':
            compile(path.read_bytes(), str(path), 'exec')
    freeze = dict(schema='phase359-native-producer-source-freeze/1', schema_version='7-king-single-A-355',
                  status='AUTHOR_SOURCE_GENERATED_INDEPENDENT_REVIEW_PENDING_NOT_ADMITTED',
                  producer_tools=[descriptor(path) for path in tools], files=final['paths'],
                  source_locations={name: dict(before=originals.get(name, {}).get('path'), after=str((D / 'after-source' / name).relative_to(R))) for name in final['paths']},
                  final_patch=descriptor(D / 'final-native-source.patch'), report=descriptor(D / 'final-producer-patch-report.json'),
                  declared_sites=len(sites), generated_small_scripts=len(final['paths']), unmodified307_after_files=inherited,
                  new_edit_fullfile_inverse_to307_after='PASS_ALL_43_DECLARED_EDITS', schema358_delta=descriptor(D / 'required-schema-delta.json'),
                  runtime_guard='356_CLOSED_NOT_MODIFIED', independent_accepted=False, native_authorized=False)
    save('producer-source-freeze.json', freeze)
    save('summary.json', dict(schema='phase359-author-source-handoff/1', status='AUTHOR_SOURCE_HANDOFF_PENDING_INDEPENDENT_REVIEW',
        freeze=descriptor(D / 'producer-source-freeze.json'), generated_paths=len(final['paths']), generated_bytes=sum(row['after']['size'] for row in final['paths'].values()),
        inherited307_after_byte_identical=len(inherited), changed_original_business_files_from307_after=sorted({e['path'] for e in ledger['edits']}),
        new_declared_source_edits=len(ledger['edits']), declared_sites=len(sites), declared_sites_are_coverage=False,
        static_checks=['Python compile without import', '26 patched NativeRandomObserver call names resolve', '43 precise edits reverse to exact frozen307 after; before matches original SOURCE', '135 dynamic state fields source-declared or explicit computed/native property branch', 'actual-binding getter transitive SOURCE closure saved'],
        first_generation='Preserved first generated sink/generator/template/patch/report and shortbow label static diagnostic before final SOURCE correction',
        remaining=descriptor(D / 'remaining-interfaces.json'), counts=dict(candidate_imports=0, schema_API_calls=0, schema_semantic_tests=0, RNG_constructions=0, Engine_constructions=0,
            input_builds=0, native_launches=0, Godot_parses=0, capture_reads=0, expected_reads=0, pool_writes=0, Game_copies=0, models=0),
        King_production_admitted=False, formal_items=75, full_engine_RL='IN_PROGRESS', no_more_writes=True, independent_FINAL=False))
    own = [R / 'docs/phase359_king_observer_producer_source_spec.md'] + tools
    own += sorted(path for path in D.rglob('*') if path.is_file())
    assert len(own) == len(set(own))
    rows = []
    for path in own:
        assert path.is_relative_to(R) and not path.is_symlink()
        assert all(not parent.is_symlink() for parent in path.parents if parent.is_relative_to(R))
        rows.append(descriptor(path))
    save('source-owner.json', dict(schema='phase359-source-owner/1', root=str(R), files=rows,
        scope='new producer SOURCE only; not an independent FINAL; no native/runtime admission'))
    readback = json.loads((D / 'source-owner.json').read_text())
    for row in readback['files']:
        assert descriptor(R / row['path']) == row
    print(json.dumps(dict(status='SOURCE_OWNER_ALL_ACTUAL_LEAVES_READ_BACK', owner=descriptor(D / 'source-owner.json'), freeze=descriptor(D / 'producer-source-freeze.json'),
                          leaves=len(rows), bytes=sum(row['size'] for row in rows))))


if __name__ == '__main__':
    main()
