"""24 bounded SOURCE/text checks; never parse/run GD, schema or native objects."""
import ast
import copy
import difflib
import hashlib
import json
from pathlib import Path
import re
import sys
import types

R = Path(__file__).resolve().parents[1]
D = R / 'data/phase359-independent-producer-review'
A = R / 'data/phase359-king-producer-source'


def pin(p):
    b = p.read_bytes()
    return dict(size=len(b), sha256=hashlib.sha256(b).hexdigest())


def main():
    contract = json.loads((D / 'contract.json').read_text())
    for row in contract['source_files']:
        assert pin(R / row['path']) == {k: row[k] for k in ('size', 'sha256')}
    spec = types.ModuleType('__independent359_text_generator__')
    spec.__file__ = str(D / 'SOURCE/generator.py')
    sys.modules[spec.__name__] = spec
    exec(compile(Path(spec.__file__).read_bytes(), spec.__file__, 'exec'), spec.__dict__)
    owner = json.loads((A / 'source-owner.json').read_text())
    freeze = json.loads((A / 'producer-source-freeze.json').read_text())
    prior = json.loads((R / 'data/phase307-observer-chance-source/native-source-freeze.json').read_text())
    files = {name: (R / row['after']).read_bytes() for name, row in freeze['source_locations'].items()}
    sink = files['native_random_observer_sink_v7.gd'].decode()
    methods = {name: spec.fn_text(sink, name) for name in spec.functions(sink)[1]}
    ledger = json.loads((A / 'new-edits-inverse-ledger.json').read_text())
    getter = json.loads((A / 'field-getter-source-matrix.json').read_text())
    queries = json.loads((A / 'binding-query-source.json').read_text())
    slotmap = json.loads((A / 'fixed-slot-map.json').read_text())
    schema_text = (R / 'tests/phase358_king_observer_schema.py').read_text()
    st = ast.parse(schema_text)
    assignments = {t.id: n.value for n in st.body if isinstance(n, ast.Assign) for t in n.targets if isinstance(t, ast.Name)}
    schema_contract = ast.literal_eval(assignments['CONTRACT'])
    schema_sites = ast.literal_eval(assignments['MATRIX'])['sites']
    records = json.loads((A / 'record-hook-source-matrix.json').read_text())
    results = []
    facts = {}
    out = D / 'checks-first-001'
    out.mkdir(exist_ok=False)
    def check(label, fn):
        try:
            detail = fn()
        except Exception as exc:
            row = dict(label=label, pass_=False, error=dict(type=type(exc).__name__, message=str(exc)))
        else:
            row = dict(label=label, pass_=True, detail=detail)
        results.append(row)
        with (out / 'journal.jsonl').open('a') as f:
            f.write(json.dumps(row, sort_keys=True) + '\n')
    def must(value, message):
        if not value:
            raise AssertionError(message)
    def owner_check():
        must(pin(A / 'source-owner.json') == dict(size=20694, sha256='b711ccbbbc2495eaeef8559c1c4ce7ac11f25b4c3832a350131963282f59abc3'), 'author owner pin')
        for row in owner['files']:
            must(pin(R / row['path']) == {k: row[k] for k in ('size', 'sha256')}, row['path'])
        return dict(leaves=len(owner['files']), bytes=sum(r['size'] for r in owner['files']))
    check('01-author101-leaf-readback', owner_check)
    def file_check():
        must(len(files) == 75, 'exact generated closure')
        for name, raw in files.items():
            must(dict(size=len(raw), sha256=hashlib.sha256(raw).hexdigest()) == freeze['files'][name]['after'], name)
        for row in (freeze['final_patch'], freeze['report']):
            must(pin(R / row['path']) == {k: row[k] for k in ('size', 'sha256')}, 'final artifact')
        return dict(files=len(files), bytes=sum(map(len, files.values())), patch=freeze['final_patch'])
    check('02-generated75-and-finalpatch-identities', file_check)
    def inverse_check():
        inverse = dict(files)
        must(len(ledger['edits']) == 43, '43 exact edits')
        for edit in reversed(ledger['edits']):
            must(inverse[edit['path']] == edit['after'].encode(), edit['label'])
            inverse[edit['path']] = edit['before'].encode()
        for name, row in prior['files'].items():
            if name != 'native_random_observer_sink_v7.gd':
                must(hashlib.sha256(inverse[name]).hexdigest() == row['after_sha256'] and len(inverse[name]) == row['after_size'], name)
        for name in ('Items/Exclusive/KingGoobert.gd', 'Utility/AutoHideParticles.gd'):
            before = Path(freeze['source_locations'][name]['before']).read_bytes()
            must(inverse[name] == before, name)
        return dict(exact_edits=43, original307_after_recovered=True, added2_original_bodies_recovered=True, sink='separate observer source')
    check('03-exact43-inverse-to307-and-two-originals', inverse_check)
    def inherited_check():
        same = [name for name, row in prior['files'].items() if len(files[name]) == row['after_size'] and hashlib.sha256(files[name]).hexdigest() == row['after_sha256']]
        must(len(same) == 68 and set(same) == set(freeze['unmodified307_after_files']), 'unchanged68')
        return dict(unchanged=68)
    check('04-unchanged68-inherited-after-files', inherited_check)
    def patch_check():
        diff = []
        for name in sorted(files):
            p = freeze['source_locations'][name]['before']
            original = (R / p).read_bytes() if p else b''
            if p:
                must(dict(size=len(original), sha256=hashlib.sha256(original).hexdigest()) == freeze['files'][name]['before'], name)
            diff.extend(difflib.unified_diff(original.decode().splitlines(True), files[name].decode().splitlines(True), fromfile='original/' + name if p else '/dev/null', tofile='source359/' + name))
        must(''.join(diff).encode() == (R / freeze['final_patch']['path']).read_bytes(), 'whole exact diff')
        return dict(final_patch_reproduced_in_memory=True)
    check('05-fullpatch-reproduction-originalSHA', patch_check)
    def helper_check():
        old = (R / prior['source_locations']['native_random_observer_sink_v7.gd']['after']).read_text()
        must(methods['shortbow_debuff_label'] == spec.fn_text(old, 'shortbow_debuff_label'), 'exact307 label method')
        diagnostic = json.loads((A / 'first-generation/static-diagnostic.json').read_text())
        must(diagnostic['missing_method'] == 'shortbow_debuff_label', 'first diagnostic preserved')
        return dict(exact_helper307=True, first_diagnostic_preserved=True, no_new_draw=True)
    check('06-shortbow-pure307-helper-and-firstfailure', helper_check)
    def symbols_check():
        definitions = re.findall(r'^func (\w+)\(', sink, re.M)
        must(len(definitions) == len(set(definitions)), 'duplicate sink functions')
        fields = re.findall(r'^(?:var|const) (\w+)\b', sink, re.M)
        must(len(fields) == len(set(fields)), 'duplicate global fields')
        calls = {x for name, raw in files.items() if name != 'native_random_observer_sink_v7.gd' for x in re.findall(r'NativeRandomObserver\.(\w+)\(', raw.decode())}
        must(calls <= set(definitions), str(sorted(calls - set(definitions))))
        source_calls = set(re.findall(r'(?<![.\w])(source_\w+)\(', sink))
        must(source_calls <= set(definitions), 'new internal source helper unresolved')
        return dict(called_observer_methods=len(calls), no_duplicates=True, lexical_only_not_GD_parse=True)
    check('07-lexical-symbol-and-global-closure', symbols_check)
    def arguments_check():
        checked = []
        for row in records['sites']:
            site = row['site']; name, method = site.split('::', 1)
            block = spec.fn_text(files[name].decode(), method)
            match = re.search(r'NativeRandomObserver\.entry\(\s*' + re.escape(json.dumps(site)) + r'\s*,\s*self\s*,\s*(\{[^\n]*\})\s*\)', block)
            must(match is not None, site)
            pairs = re.findall(r'"(\w+)"\s*:\s*(\w+)', match[1])
            must([k for k, _ in pairs] == row['arguments_exact'] and all(k == v for k, v in pairs), site)
            checked.append(site)
        must(len(checked) == 106, 'declared106 not runtimeHIT')
        return dict(bound_argument_sites=106, observer_casts_not_used=True)
    check('08-callee-bound106-argument-symbols', arguments_check)
    def getter_check():
        for name, row in getter['source_files'].items():
            raw = (Path('/workspace/godotsteam-startup-20261013/baseline/Backpack Battles') / name).read_text()
            must('setget' not in raw and not re.search(r'^\s*func _get\(', raw, re.M), name)
        for row in queries['functions']:
            original = (Path('/workspace/godotsteam-startup-20261013/baseline/Backpack Battles') / row['path']).read_text()
            body = spec.fn_text(original, row['function'])
            must(body == row['body'], row['function'])
        must('return items' in next(x['body'] for x in queries['functions'] if x['function'] == 'getItems'), 'live inventory is read only')
        return dict(direct_field_rows=len(getter['properties']), binding_query_bodies=len(queries['functions']), native_getters='Inherited111/154 SOURCE authority,not VM executed')
    check('09-property-and-six-getter-source-closure', getter_check)
    def purity_check():
        extension = (D / 'SOURCE/extension.gd').read_text()
        must(not re.search(r'\.(?:prepare|reset|cacheAffectedItemsForCombat|getAffectedItems|getP|getP_m|gainStacks|useMana|emitEvent|connectEvent)\(', extension), 'observer business call')
        must(not re.search(r'\.(?:set_process|set_physics_process|set_process_internal|set_physics_process_internal|randomize|set_seed|set_state)\(', sink), 'observer flags/RNG mutation')
        must('get_tree().connect("physics_frame", self, "clock_physics_signal")' in methods['_ready'] and 'get_tree().connect("idle_frame", self, "clock_idle_signal")' in methods['_ready'], 'only declared frame observers')
        return dict(no_new_business_calls_or_flags=True, ui_picking_controls='Exact inherited137/154 authority;not process flags')
    check('10-observation-call-and-processflag-purity', purity_check)
    def retention_check():
        must('source_buffer.append(row)' in methods['write_record'] and '"subject": reference(subject)' in methods['write_record'], 'encoded early rows')
        must('source_crowns[str(object.get_instance_id())] = arguments._crownState' in methods['entry'], 'crown actual scalar arg')
        must('source_cleanup = {"physics_frame": Engine.get_physics_frames()' in methods['source_mark_cleanup'], 'cleanup scalars only')
        must('registry[object.get_instance_id()] = role' in methods['source_register'], 'registry primitive ID role')
        return dict(global_event_or_temporary_objects_retained=False, source_buffer='encoded DTOs', scope='SOURCE assignments inspected,not GC experiment')
    check('11-primitive-only-observer-retained-state', retention_check)
    def slot_check():
        fixture = ast.literal_eval(assignments['FIXED_FIXTURE'])
        wanted = [i['instance_id'] for side in fixture['sides'] for i in side['items']]
        must([x['instance_id'] for x in slotmap] == wanted and len(wanted) == 39 and 'O:12' not in wanted and 'O:19' in wanted, 'exact role hole')
        bind = methods['bind_fixed_inventory']
        for anchor in ('item.descriptor.itemIndex == spec.item_index', 'top_left == Vector2(spec.x, spec.y)', 'item.faceDirection == spec.f', 'item.inventory != inventory', 'SOURCE_OCCUPIED_MEMBERS', 'SOURCE_SLOT_GEOMETRY_AMBIGUOUS', 'SOURCE_SLOT_DUPLICATE_OR_GEMS'):
            must(anchor in bind, anchor)
        must('enumerate' not in bind and 'inventory_encounter_index' in bind, 'do not compact-renumber')
        return dict(selected_roles=39, geometry_descriptor_inventory_join=True, actual_binding_observed=False)
    check('12-fixedA-O-hole-and-actual-query-binding-source', slot_check)
    def early_check():
        bind = methods['bind_fixed_inventory']
        must(not re.search(r'row\.(?:subject|stamp|sequence)\s*=', bind), 'raw row rewritten')
        must('source_write_diagnostic(row)' in bind and 'source_write_row(row)' in bind, 'early selected/unselected retained')
        must('row = {"schema": "observer7-record/1", "sequence": sequence' in methods['write_record'], 'actual sequence')
        return dict(raw_roles_stamps_sequences_not_reassigned=True, auxiliary_binding='12th proof pending')
    check('13-early-row-immutability-and-retention', early_check)
    def birth_check():
        auto = files['Utility/AutoHideParticles.gd'].decode()
        must(auto.index('timer = Timer.new()') < auto.index('timer_birth(timer') < auto.index('timer.one_shot = true'), 'actual ctor cut')
        must('timer_birth(invulnerabilityTimer, self, "Character.scene.ready")' in files['Core/Character.gd'].decode(), 'actual scene timer')
        must('track_king_timer_api(timer, operation)' in methods['timer_before'], 'prebinding no-start tracking')
        must('"private_provenance": "source_constructor_minus_one_no_start_not_public_zero_inference"' in sink, 'private lemma not actual getter')
        return dict(constructor_scene_ready_source_order=True, private_countdown_directly_observed=False)
    check('14-fresh-birth-timing-and-private-lemma', birth_check)
    def state_check():
        state_table = json.loads(re.search(r'^const STATE_SCHEMAS = (.*)$', sink, re.M)[1])
        must(state_table == schema_contract['state_schemas'], 'exact358 state table')
        must('encode(character.buffProtectStacks)' in methods['source_resources'], 'direct storedINT')
        must('state(character.buffs[category], "buff")' in methods['source_resources'], 'full actual ledger')
        return dict(state_table_exact358=True, Character_stored='INT', King_callsite='REAL', onready_missing_values_not_synthesized=True)
    check('15-typed-field-and-source-resource-emission', state_check)
    def clock_check():
        code = methods['clock_idle_signal']
        for anchor in ('clock_pass("idle", get_process_delta_time())', 'source_cleanup.physics_frame + 2', 'SOURCE_MISSED_FIRST_IDLE_CUT', 'close_king_clock()', 'source_window_complete = not failed'):
            must(anchor in code, anchor)
        must('call_deferred' not in code, 'not deferred final close')
        must('get_physics_process_delta_time()' in methods['clock_physics_signal'] and 'KING_CLOCK_COUNTER_ORDER' in methods['clock_pass'], 'actual counters/delta')
        return dict(real_external_schedule_source=True, two_future_and_first_idle_preinternal=True, native_samples=0)
    check('16-real-clock-and-synchronous-source-close', clock_check)
    def rng_partition_check():
        code = methods['rng_initial_capture']
        must('rng148.get_seed()' in code and 'rng148.get_state()' in code and 'rng148.set_' not in code and 'randomize' not in code, 'readonly checkpoint')
        must('EXPECTED_ONLY_NOT_MODEL_INPUT' in methods['source_runtime_snapshot'] and 'native_capture_accepted' in methods['source_completion_receipt'], 'expected partition')
        must('"model_input_admitted": false' in methods['bind_fixed_inventory'], 'binding not runtime')
        return dict(rng_checkpoint_proof_only=True, no_runtime_projection=True, raw_RNG='Inherited307 actual calls plus one original randPitch expression,not executed')
    check('17-RNG-and-proof-expected-partition', rng_partition_check)
    def caps_check():
        for name, anchor in [('write_record', 'sequence >= CAPS.records'), ('source_write_row', 'CAPS.total_bytes'), ('source_write_diagnostic', 'CAPS.record_bytes'), ('clock_pass', 'king_clock_count >= 200000')]:
            must(anchor in methods[name], name)
        must('failed = true' in methods['fail'] and 'observer7_failure.json' in methods['fail'], 'durable failure')
        must('if failed or closed:' in methods['entry'], 'no observation after failure')
        return dict(bounded_failed_capture_not_silent=True, original_bodies='Recovered exact after removing43observer edits;no observer-success branch wraps gameplay')
    check('18-caps-and-firstfailure-source-policy', caps_check)
    def interface_check():
        sites = json.loads(re.search(r'^const SITES = (.*)$', sink, re.M)[1])
        extra = sorted(set(sites) - set(schema_sites))
        expected = sorted('Items/Goobert.gd::' + x for x in ('prepare', 'onItemActivated', 'doCooldownEffect'))
        must(extra == expected and len(sites) == 106, 'known exact3 schema gap')
        for site in schema_sites:
            must(sites[site] == {k: schema_sites[site][k] for k in ('channel', 'state_schema')}, site)
        delta = json.loads((A / 'required-schema-delta.json').read_text())
        must(delta['auxiliary_proof']['accepted_by_358'] is False, 'auxiliary not silently admitted')
        facts['pipeline_blockers'] = dict(unaccepted_sites=extra, unaccepted_auxiliary='king-slot-bindings.json', collector_adapter_host='not implemented', native_ready=False)
        return facts['pipeline_blockers']
    check('19-explicit-known-interface-blockers-not-filtered', interface_check)
    text_calls = 0
    def transformed(source):
        nonlocal text_calls
        text_calls += 1
        return spec.hook_function(source, 'Toy.gd::toy', dict(arguments_exact=[]))
    def toy_void():
        value = transformed('func toy():\n\tvar x = 1\n')
        must(value.count('"return_implicit"') == 1 and value.count('var x = 1') == 1, 'fallthrough')
        return dict(source_text_only=True)
    check('20-text-fallthrough-observer-once', toy_void)
    def toy_return():
        value = transformed('func toy():\n\treturn side_effect()\n')
        must(value.count('side_effect()') == 1 and 'return observer359_return_0' in value and value.count('"return_explicit"') == 1, 'return expr once')
        return dict(expression_not_executed=True)
    check('21-text-return-expression-single-evaluation', toy_return)
    def toy_inline():
        value = transformed('func toy():\n\tif flag: return side_effect()\n')
        must(value.count('side_effect()') == 1 and '\tif flag:\n' in value and '"return_implicit"' in value, 'inline branch')
        return dict(branch_not_executed=True)
    check('22-text-inline-branch-return-preservation', toy_inline)
    def toy_collision():
        try:
            transformed('func toy():\n\tvar observer359_existing = 1\n')
        except ValueError:
            return dict(collision_rejected=True)
        raise AssertionError('temporary collision accepted')
    check('23-text-temporary-name-collision-rejected', toy_collision)
    def toy_idempotent():
        one = transformed('func toy():\n\treturn null\n')
        must(transformed(one) == one, 'existing hook doubled')
        return dict(existing_hook_not_doubled=True)
    check('24-text-existing-hook-not-duplicated', toy_idempotent)
    must(len(results) == 24, 'exact presealed24')
    failures = [x for x in results if not x['pass_']]
    report = dict(schema='phase359-independent-source-checks/1', status='SOURCE_COMPONENT_CHECKS_PASS_PIPELINE_PENDING' if not failures else 'SOURCE_CHECK_FAILURE',
        checks=results, executed=24, failures=failures, facts=facts, text_generator_module_imports=1, pure_text_hook_calls=text_calls,
        schema_imports=0, schema_API_calls=0, GD_parse_or_run=0, FakeNative=0, candidate_imports=0, RNG=0, Engine=0, models=0,
        actual_input_builds=0, native=0, capture_reads=0, expected_reads=0, no_HIT_claim=True,
        scope='LexicalSOURCE/in-memorypatch reconstruction/text transforms only;not Godot parse/VM or runtime conformance')
    with (out / 'report.json').open('x') as f:
        json.dump(report, f, indent=2, sort_keys=True); f.write('\n')
    print(json.dumps(dict(status=report['status'], checks=24, failures=[x['label'] for x in failures], text_calls=text_calls)))


if __name__ == '__main__':
    main()
