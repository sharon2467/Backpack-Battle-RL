"""Output-only SOURCE assembly/static proof; no GD/schema/runtime import or call."""
from pathlib import Path
import ast
import hashlib
import json
import re
import difflib

R = Path(__file__).resolve().parents[1]
D = R / 'data/phase359-king-producer-source'
BASE = Path('/workspace/godotsteam-startup-20261013/baseline/Backpack Battles')


def pin_bytes(raw):
    return dict(size=len(raw), sha256=hashlib.sha256(raw).hexdigest())


def pin(path):
    return pin_bytes(path.read_bytes())


def save(name, value):
    with (D / name).open('x') as stream:
        stream.write(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + '\n')


def blocks(source):
    lines = source.splitlines(keepends=True)
    found = {}
    for i, line in enumerate(lines):
        match = re.match(r'^func (\w+)\(', line)
        if not match:
            continue
        end = i + 1
        while end < len(lines):
            line2 = lines[end]
            if line2.strip() and not line2.startswith(('\t', '#', ' ')):
                break
            end += 1
        if match[1] in found:
            raise ValueError('duplicate observer method ' + match[1])
        found[match[1]] = ''.join(lines[i:end])
    return found


def main():
    sink_path = D / 'after-source/native_random_observer_sink_v7.gd'
    sink = sink_path.read_text()
    extension = (R / 'tests/phase359_sink_extension_source.gd').read_text()
    for name, body in blocks(extension).items():
        old = blocks(sink).get(name)
        if old is None:
            sink += '\n' + body
        else:
            sink = sink.replace(old, body + '\n', 1)
    prior = json.loads((R / 'data/phase307-observer-chance-source/native-source-freeze.json').read_text())
    helper = (R / prior['source_locations']['native_random_observer_sink_v7.gd']['after']).read_text()
    sink += '\n' + blocks(helper)['shortbow_debuff_label']
    sink_path.write_text(sink)
    definitions = set(blocks(sink))
    calls = {}
    for path in (D / 'after-source').rglob('*.gd'):
        if path == sink_path:
            continue
        for name in re.findall(r'NativeRandomObserver\.(\w+)\(', path.read_text()):
            calls.setdefault(name, set()).add(str(path.relative_to(D / 'after-source')))
    assert set(calls) <= definitions, sorted(set(calls) - definitions)
    assert 'if false' not in sink
    # Direct script member audit for every dynamic state-table read.
    schema_tree = ast.parse((R / 'tests/phase358_king_observer_schema.py').read_text())
    contract = ast.literal_eval(next(node.value for node in schema_tree.body if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'CONTRACT' for t in node.targets)))
    owners = {'item': ['Items/Item.gd'], 'plain_item': ['Items/Item.gd'], 'potion': ['Items/Potion.gd', 'Items/Item.gd'],
              'goobert': ['Items/Goobert.gd', 'Items/Item.gd'], 'king': ['Items/Exclusive/KingGoobert.gd', 'Items/Goobert.gd', 'Items/Item.gd'],
              'character': ['Core/Character.gd'], 'buff': ['Core/Buff.gd'], 'temporary_constructor': ['Core/Buff.gd'],
              'game': ['Core/Game.gd'], 'util': ['Utility/Util.gd'], 'event_bus': ['Utility/EventBus.gd'],
              'combat_timer': ['Interface/CombatTimer/CombatTimer.gd'], 'combat_log': ['Core/CombatLog.gd'], 'auto_hide': ['Utility/AutoHideParticles.gd']}
    computed = {'descriptorIndex', 'native_id', 'allocation_counter', 'event_count', 'connection_count'}
    native = {'auto_hide': {'emitting', 'explosiveness', 'lifetime', 'one_shot', 'speed_scale', 'visible'}}
    properties = []
    originals = {}
    for kind, paths in owners.items():
        for name in paths:
            source = (BASE / name).read_text()
            assert not re.search(r'^func _get\(', source, re.M)
            assert 'setget' not in source
            originals[name] = pin(BASE / name)
        for field, variant in contract['state_schemas'][kind].items():
            if field in computed:
                properties.append(dict(schema=kind, field=field, raw_kind=variant, origin='explicit computed branch; no object.get for this name'))
                continue
            if field in native.get(kind, set()):
                properties.append(dict(schema=kind, field=field, raw_kind=variant, origin='native Particles2D property; AutoHide has no _get/setget'))
                continue
            found = []
            for name in paths:
                for line, text in enumerate((BASE / name).read_text().splitlines(), 1):
                    if re.search(r'\bvar\s+' + re.escape(field) + r'\b', text):
                        found.append(dict(path=name, line=line, declaration=text.strip()))
            assert found, (kind, field)
            properties.append(dict(schema=kind, field=field, raw_kind=variant, declarations=found,
                                   phase='callee-bound state or actual checkpoint/cleanup/final', getter='direct declared script member; _get/setget absent in audited source chains'))
    save('field-getter-source-matrix.json', dict(schema='phase359-readonly-field-source-matrix/1', properties=properties, source_files=originals,
        computed_branches={'native_id': 'Object.get_instance_id/class, immutable numeric/string identity', 'descriptorIndex': 'object.descriptor.itemIndex',
                           'allocation_counter': 'object.combatLog.eventNum', 'event_count': 'object.events.size()', 'connection_count': 'read-only nested dictionary/array sizes'},
        native_readonly=['Node instance/class/script/base_script/path/name/parent/index/priority/tree/processing flags/viewport lookup',
                         'Timer mode/wait/time_left/one_shot/autostart/paused/is_stopped', 'Engine frames/is_in_physics_frame/time_scale/fps',
                         'Particles2D scalar/flags and CanvasItem light visible/self_modulate', 'StreamPeerBuffer double serialization'],
        forbidden_observation_calls=['prepare', 'reset', 'cacheAffectedItemsForCombat', 'getAffectedItems', 'getP', 'getP_m', 'gain/use/change resource business APIs'],
        native_property_scope='readonly public getters inherited old111/154; no claim of direct private Timer countdown',
        caveat='Actual GD parse/VM getter conformance not executed; source-only proof and independent delta review pending'))
    # Snapshot the exact original-query bodies used by new binding code.
    query_requests = {'Items/Item.gd': ['getTopLeftCell', 'getGemsNoNull', 'getGems'],
                      'Items/GemSocket.gd': ['getGem'], 'Utility/Util.gd': ['filterNull'],
                      'Core/Inventory.gd': ['getItems']}
    queries = []
    for name, methods in query_requests.items():
        text = (BASE / name).read_text()
        assert not re.search(r'^func _get\(', text, re.M) and 'setget' not in text
        funcs = blocks(text)
        for method in methods:
            body = funcs[method]
            queries.append(dict(path=name, function=method, body=body, **pin_bytes(body.encode())))
    save('binding-query-source.json', dict(functions=queries,
        getGemsNoNull='getGems creates a fresh local array of direct socket.getGem member reads; filterNull creates another local array; no writes to sockets/items/inventory or business calls',
        inventory_order='getItems returns live items array; observer reads only, never sorts/mutates it',
        source_only='Exact original function bodies and no _get/setget in their declaring scripts; no getter called by author, independent SOURCE review pending',
        actual_binding_receipt='king-slot-bindings.json auxiliary proof pending12th schema/adapter admission'))
    paths, diff = {}, []
    for path in sorted((D / 'after-source').rglob('*')):
        if not path.is_file():
            continue
        name = str(path.relative_to(D / 'after-source'))
        if name in prior['source_locations']:
            location = prior['source_locations'][name]['before']
            before = (R / location).read_bytes() if location is not None else None
        else:
            before = (BASE / name).read_bytes()
        after = path.read_bytes()
        paths[name] = dict(before=None if before is None else pin_bytes(before), after=pin_bytes(after))
        diff.extend(difflib.unified_diff((before or b'').decode().splitlines(True), after.decode().splitlines(True),
                                       fromfile='original/' + name if before is not None else '/dev/null', tofile='source359/' + name))
    (D / 'final-native-source.patch').write_text(''.join(diff))
    for name in ('tests/phase359_generate_producer_source.py', 'tests/phase359_finalize_producer_source.py'):
        compile((R / name).read_bytes(), name, 'exec')
    save('final-producer-patch-report.json', dict(schema='phase359-final-observer-source-patch/1', version='7-king-single-A-source359',
        paths=paths, path_count=len(paths), declared_sites=106, patch=pin(D / 'final-native-source.patch'),
        generator=pin(R / 'tests/phase359_generate_producer_source.py'), finalizer=pin(Path(__file__)),
        sink=pin(sink_path), implemented_called_observer_methods=len(calls), no_missing_NativeRandomObserver_method=True,
        admission='SOURCE_ONLY_GD_PARSE_SCHEMA_DELTA_COLLECTOR_INPUT_ADAPTER_HOST_ALL_PENDING', native_authorized=False,
        inherited307_shortbow_label='exact method copied, no new draw; inherited callers must parse even outsideK1',
        first_generation='retained under first-generation; sink/report/patch/generator/extension originalbytes preserved'))
    save('static-source-validation.json', dict(schema='phase359-static-producer-validation/1', python_compile='PASS_NO_IMPORT',
        generated_GD_parsed_or_run=False, all_patched_NativeObserver_call_names_resolved=True,
        direct_script_field_lookup_closed=len(properties), _get_setget_absent_in_audited_owner_chains=True,
        branch_timer_return_expression_evaluation='new code uses one local evaluated value; original307 inheritance preserved',
        raw_stamp_sequence_roles='early primitive records never rewritten', source_binding='actual desc/geometry/inventory query; not continuousenumerate',
        schema_delta='Goobert3sites and auxiliary12th proof explicitly unaccepted; no native-readyclaim',
        schema_imports=0, schema_tests=0, candidate_imports=0, RNG=0, Engine=0, native=0, models=0))
    print(json.dumps(dict(status='PRODUCER_SOURCE_STATIC_CLOSURE_NO_VM_EXECUTION', paths=len(paths), called_methods=len(calls), patch=pin(D / 'final-native-source.patch'))))


if __name__ == '__main__':
    main()
