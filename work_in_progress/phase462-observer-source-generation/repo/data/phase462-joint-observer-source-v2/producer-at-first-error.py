"""One finite Source derivation only; never import generated schema or run Godot."""
import ast
import difflib
import hashlib
import json
from pathlib import Path
import re
import stat
import traceback


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data/phase462-joint-observer-source-v2'
SPEC = 'docs/phase462_joint_observer_source_v2_repair_spec.md'
REQUEST = 'data/phase460-joint-native-observation-design/request.json'
REVIEW = 'data/phase460-independent-design-review/review.json'
PREIMAGES = {
    'sink': ('data/phase391-terminal-source/after-source/native_random_observer_sink_v7.gd', '999e0043a653067a962819cf81340b0dad745fa2148bbfab7724d7948a6a21ea'),
    'collector': ('data/phase391-terminal-source/collector.gd', 'f05bbf6b0e7277b5a342553d3a8d3c842f3efa6526f0b85948bd003837ac74ce'),
    'schema': ('tests/phase391_king_observer_schema.py', 'ffcddfd2cbe58307f7258c1aefad5586a9179c6c452dc59c3342f9047f31457c'),
    'patch': ('data/phase391-terminal-source/native-patch-source.json', 'e889a9faf1669706732ceb72937011d5867f3094ca503b7997ff311b7c1002de'),
    'origin_freeze': ('data/phase391-terminal-source/combined-source-freeze.json', 'e55a602c9d7087a71a2fe6b78a3a143663fc8f0f659c0fe3fb690019ba8173c9'),
    'request': (REQUEST, '88d6f6e0b583eaeab540abbb105aa1549cee3891168b6f137f56ee43b84d9434'),
    'review': (REVIEW, '496a40c88f9f9bc5400b49e1f5a90e7b2e566c94a265c898ebdb16e8dfb42060'),
}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read_source(path):
    path = Path(path)
    require(path.is_relative_to(ROOT), 'source outside repository')
    require(not any(p.is_symlink() for p in (path, *path.parents)), 'linked source ancestor')
    info = path.lstat()
    require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1, 'ordinary single-link Source required')
    return path.read_bytes()


def descriptor(path):
    path = Path(path)
    raw = read_source(path)
    return dict(path=str(path.relative_to(ROOT)), size=len(raw), sha256=digest(raw))


def write_bytes(path, raw):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as stream:
        stream.write(raw)


def save(path, value):
    write_bytes(path, (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + '\n').encode())


def canonical(value):
    return digest(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode())


def py_functions(text):
    # Last definition is the active Source override in the inherited schema.
    return {n.name: ast.get_source_segment(text, n) for n in ast.parse(text).body
            if isinstance(n, (ast.FunctionDef, ast.ClassDef))}


def gd_functions(text):
    starts = list(re.finditer(r'^func (\w+)\(', text, re.M))
    return {match.group(1): text[match.start(): starts[i + 1].start() if i + 1 < len(starts) else len(text)].rstrip()
            for i, match in enumerate(starts)}


class Delta:
    def __init__(self, path, language):
        self.path = path
        self.original = read_source(path)
        self.before = self.original.decode('utf-8')
        self.text = self.before
        self.language = language
        self.edits = []

    def replace(self, before, after, count=1):
        require(before != after and self.text.count(before) == count, 'exact delta match: ' + before[:100])
        starts = [m.start() for m in re.finditer(re.escape(before), self.text)]
        after_positions = [pos + i * (len(after) - len(before)) for i, pos in enumerate(starts)]
        self.text = self.text.replace(before, after)
        self.edits.append(dict(before=before, after=after, occurrences=count, after_positions=after_positions))

    def gd_constant(self, name, value):
        match = re.search(r'^const ' + re.escape(name) + r' = [^\n]+', self.text, re.M)
        require(match is not None, 'GD constant ' + name)
        self.replace(match.group(), 'const ' + name + ' = ' + json.dumps(value, sort_keys=True))

    def py_constant(self, name, expression):
        nodes = [n for n in ast.parse(self.text).body if isinstance(n, ast.Assign)
                 and any(isinstance(t, ast.Name) and t.id == name for t in n.targets)]
        require(len(nodes) == 1, 'unique Python constant ' + name)
        self.replace(ast.get_source_segment(self.text, nodes[0]), name + ' = ' + expression)

    def function(self, name, replacements):
        functions = py_functions(self.text) if self.language == 'py' else gd_functions(self.text)
        old = functions[name]
        new = old
        for before, after in replacements:
            require(new.count(before) > 0, 'function delta absent ' + name + ': ' + before[:70])
            new = new.replace(before, after)
        self.replace(old, new)

    def finish(self, path, allowed):
        inverse = self.text
        for row in reversed(self.edits):
            for pos in reversed(row['after_positions']):
                require(inverse[pos:pos + len(row['after'])] == row['after'], 'inverse preimage mismatch')
                inverse = inverse[:pos] + row['before'] + inverse[pos + len(row['after']):]
        require(inverse.encode() == self.original, 'whole-byte inverse')
        parse = py_functions if self.language == 'py' else gd_functions
        before, after = parse(self.before), parse(self.text)
        require(set(before) == set(after), 'method inventory changed')
        changed = sorted(name for name in before if before[name] != after[name])
        require(set(changed) == set(allowed), 'unexpected changed functions: ' + repr(changed))
        if self.language == 'py':
            compile(self.text, str(path), 'exec', dont_inherit=True)
        write_bytes(path, self.text.encode())
        stem = path.stem
        report = dict(before=descriptor(self.path), after=descriptor(path), edits=self.edits,
                      inverse='EXACT_COMPLETE_BYTES', changed_functions=changed,
                      conserved_functions=sorted(set(before) - set(changed)),
                      new_functions=0, language=self.language)
        save(OUT / 'inverse' / (stem + '.json'), report)
        write_bytes(OUT / 'inverse' / (stem + '.patch'), ''.join(difflib.unified_diff(
            self.before.splitlines(True), self.text.splitlines(True),
            fromfile=str(self.path.relative_to(ROOT)), tofile=str(path.relative_to(ROOT)))).encode())
        return descriptor(path), report


def verify_preimages():
    sources = {}
    for name, (relative, expected) in PREIMAGES.items():
        path = ROOT / relative
        require(descriptor(path)['sha256'] == expected, 'Source descriptor drift: ' + name)
        sources[name] = path
    patch = json.loads(read_source(sources['patch']))
    require(len(patch['paths']) == 75, 'exact inherited75 transformed targets')
    inherited = []
    for target, row in patch['paths'].items():
        if target == 'native_random_observer_sink_v7.gd':
            continue
        actual = descriptor(ROOT / row['after_path'])
        require({k: actual[k] for k in ('size', 'sha256')} == row['after'], 'inherited transformed target drift: ' + target)
        inherited.append(dict(target=target, source=actual, before=row['before']))
    require(len(inherited) == 74, 'exact74 non-sink targets')
    return sources, patch, inherited


def build_fixed_plan(request):
    fixture = request['model_fixture_shape_proposal']
    require([len(s['items']) for s in fixture['sides']] == [14, 12], 'fixed P14/O12')
    require(sorted({i['item_index'] for s in fixture['sides'] for i in s['items']}) == [1, 4, 11, 19, 22, 23, 262], 'seven exact IDs')
    geometry = json.loads(read_source(ROOT / 'data/phase457-king-basic-business-design/static-layout-map.json'))
    by_source = {row['identity']: row['cells'] for side in geometry['sides'] for row in side['identity_cells_and_stars']}
    slots = []
    for row in request['Source459_to_native_slot_bijection']:
        slots.append(dict(side=row['side'], input_slot=row['input_slot'], instance_id=row['planned_native_role'],
                          item_index=row['item_index'], x=row['x'], y=row['y'], f=row['f'],
                          cells=by_source[row['Source459_instance_id']]))
    require(len(slots) == 26 and len({s['instance_id'] for s in slots}) == 26, '26 unique slots')
    require([s['instance_id'] for s in slots if s['item_index'] == 262] == ['P:6'], 'KingP6')
    require([s['instance_id'] for s in slots if s['item_index'] == 23] == ['P:7'], 'BasicP7')
    require(next(s for s in slots if s['instance_id'] == 'P:12')['item_index'] == 1, 'P12 ordinary sword')
    return dict(schema='phase462-fixed-source-plan/1', slots=slots, fixture=fixture,
                native_fixtures=request['native_fixture_proposal'], config=request['native_config_proposal'],
                profile=request['proposed_native_profile'], version=request['proposed_observer_version'],
                source_case=request['source_case'], native_case=request['case_id'],
                source_job_bijection=request['Source459_to_native_slot_bijection'],
                native_facts=None, status='SOURCE_PLAN_NOT_CAPTURE_OR_MODEL_INPUT')


def derive_sink(path, plan):
    delta = Delta(path, 'gd')
    caps = json.loads(re.search(r'^const CAPS = (.+)$', delta.text, re.M).group(1))
    caps['descriptors'] = 7
    delta.gd_constant('CAPS', caps)
    delta.gd_constant('SOURCE_SLOT_TABLE', plan['slots'])
    delta.gd_constant('RNG_INITIAL_PROFILE', plan['version'])
    delta.function('state', [('[1, 4, 11, 19, 22, 262]', '[1, 4, 11, 19, 22, 23, 262]'),
        ('schema = "king" if index == 262 else ("potion" if index == 19 else "item")',
         'schema = "king" if index == 262 else ("goobert" if index == 23 else ("potion" if index == 19 else "item"))')])
    delta.function('bind_fixed_inventory', [('P:12', 'P:6'), ('[1, 4, 11, 19, 22, 262]', '[1, 4, 11, 19, 22, 23, 262]')])
    delta.function('source_selected_auto', [('P:12', 'P:6')])
    for name in ('ui_open', 'rng_initial_capture'):
        delta.function(name, [('KING-K1-A-353', plan['source_case'])])
    return delta


def derive_collector(path, plan):
    delta = Delta(path, 'gd')
    delta.gd_constant('SOURCE_P', plan['native_fixtures']['P'])
    delta.gd_constant('SOURCE_O', plan['native_fixtures']['O'])
    delta.gd_constant('SOURCE_CONFIG', plan['config'])
    delta.gd_constant('PLAYER_ITEM_WHITELIST', [1, 4, 11, 19, 22, 23, 262])
    return delta


def derive_schema(path, plan, binding_contract):
    delta = Delta(path, 'py')
    tree = ast.parse(delta.text)
    contract = next(ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign)
                    and any(isinstance(t, ast.Name) and t.id == 'CONTRACT' for t in n.targets))
    contract['caps']['descriptors'] = 7
    constants = {
        'VERSION': repr(plan['version']), 'PROFILE': repr(plan['profile']),
        'DESCRIPTOR_IDS': 'frozenset({1,4,11,19,22,23,262})', 'CONTRACT': repr(contract),
        'SINGLE_KING_GENUINE_PROFILE': repr(plan['profile']),
        'SINGLE_KING_OBSERVER_VERSION': repr(plan['version']), 'SINGLE_KING_CASE': repr(plan['source_case']),
        'SINGLE_KING_ITEMS': 'frozenset({1,4,11,19,22,23,262})',
        'SINGLE_KING_FIXTURE_SHA256': repr(canonical(plan['fixture'])),
        'SINGLE_KING_ROLES': repr(None), 'FIXED_FIXTURE': repr(plan['fixture']),
        'ITEM_INDEX_BY_ROLE': repr({s['instance_id']: s['item_index'] for s in plan['slots']}),
        'TIMER_ROLES': "frozenset(['tick:P','tick:O','fatigue:start','fatigue:tick','invu:P','invu:O','king_buff:P:6','king_hide:P:6','king_drag:P:6'] + ['buff:'+side+':'+str(category) for side in ('P','O') for category in range(100,111)] + ['aux:'+side+':'+name for side in ('P','O') for name in ('battleRageTimer','autoRageTimer')])",
        'BINDING_FIXED_PLAN': repr(plan['slots']), 'BINDING_SOURCE_CONTRACT': repr(binding_contract),
    }
    constants['SINGLE_KING_ROLES'] = 'frozenset(' + repr([s['instance_id'] for s in plan['slots']]) + ')'
    for name, expression in constants.items():
        delta.py_constant(name, expression)
    for name in ('validate_single_king_fixture', 'validate_single_king_fresh_facts',
                 'validate_single_king_source_defaults', 'validate_single_king_input_provenance',
                 'primitive_context', 'validate_primitive', 'validate_record'):
        delta.function(name, [('P:12', 'P:6')])
    delta.function('validate_single_king_source_defaults', [
        ("    return dict(kind='SOURCE_DEFAULTS_PROOF_ONLY_NOT_RUNTIME'",
         "    for record, cooldown in ((pre, 0.0), (act, 5.0)):\n"
         "        matches = [row for row in record['payload']['items'] if row.get('instance') == 'P:7']\n"
         "        if len(matches) != 1:\n"
         "            raise ValueError('one selected Basic source item state')\n"
         "        fields = matches[0]['fields']\n"
         "        for key, expected in (('descriptorIndex', 23), ('activations', 0)):\n"
         "            if fields.get(key) != dict(type='int', decimal=str(expected)):\n"
         "                raise ValueError('Basic source INT ' + key)\n"
         "        for key, expected in (('activationsToTrigger', 5.0), ('iterationCooldown', cooldown), ('triggerTime', cooldown)):\n"
         "            if fields.get(key) != dict(type='float', binary64_be=struct.pack('>d', expected).hex()):\n"
         "                raise ValueError('Basic source REAL ' + key)\n"
         "    return dict(kind='SOURCE_DEFAULTS_PROOF_ONLY_NOT_RUNTIME'")])
    delta.function('validate_state', [
        ("actual = 'king' if index == 262 else 'potion' if index == 19 else 'plain_item'",
         "actual = 'king' if index == 262 else 'goobert' if index == 23 else 'potion' if index == 19 else 'plain_item'"),
        ("kind == 'goobert' and actual != 'king'", "kind == 'goobert' and actual not in ('king', 'goobert')"),
        ('item descriptor outside fixed six IDs', 'item descriptor outside fixed seven IDs')])
    # These loops were already fixed-plan based; only obsolete exact39 wording changes.
    delta.function('_binding_validate_value', [('exact39 actual slot bindings', 'exact26 actual slot bindings')])
    return delta


def freeze_source(plan, patch, inherited, artifacts, reports):
    paths = json.loads(json.dumps(patch['paths']))
    paths['native_random_observer_sink_v7.gd']['after_path'] = artifacts['sink']['path']
    paths['native_random_observer_sink_v7.gd']['after'] = {k: artifacts['sink'][k] for k in ('size', 'sha256')}
    require(all(paths[row['target']] == patch['paths'][row['target']] for row in inherited), 'non-sink descriptor mutation')
    original_sink = read_source(ROOT / PREIMAGES['sink'][0]).decode()
    actual_sink = read_source(ROOT / artifacts['sink']['path']).decode()
    for name in ('SITES', 'STATE_SCHEMAS'):
        get = lambda text: re.search(r'^const ' + name + r' = [^\n]+', text, re.M).group()
        require(get(original_sink) == get(actual_sink), 'conserved sink declaration ' + name)
    original_schema = read_source(ROOT / PREIMAGES['schema'][0]).decode()
    actual_schema = read_source(ROOT / artifacts['schema']['path']).decode()
    get_matrix = lambda text: next(ast.get_source_segment(text, n) for n in ast.parse(text).body if isinstance(n, ast.Assign)
                                  and any(isinstance(t, ast.Name) and t.id == 'MATRIX' for t in n.targets))
    require(get_matrix(original_schema) == get_matrix(actual_schema), 'MATRIX/API statement bytes conserved')
    slots = descriptor(OUT / 'fixed-plan.json')
    source_tuple = dict(schema='phase462-joint-observer-source-tuple/1', profile=plan['profile'],
                        observer_version=plan['version'], terminal_policy=patch['terminal_policy'],
                        fixed_fixture=descriptor(OUT / 'fixed-v8-fixture.json'), fixed_plan=slots,
                        producer=descriptor(Path(__file__)), sink=artifacts['sink'], collector=artifacts['collector'],
                        schema_module=artifacts['schema'], native_patch=str((OUT / 'native-patch-source.json').relative_to(ROOT)),
                        model_input_or_runtime_admitted=False, host_execution_ready=False)
    save(OUT / 'native-patch-source.json', dict(schema='phase462-native-patch-source/1', paths=paths,
        producer=descriptor(Path(__file__)), sink=artifacts['sink'], profile=plan['profile'],
        observer_version=plan['version'], terminal_policy=patch['terminal_policy']))
    source_tuple['native_patch'] = descriptor(OUT / 'native-patch-source.json')
    save(OUT / 'source-tuple.json', source_tuple)
    origin = json.loads(read_source(ROOT / PREIMAGES['origin_freeze'][0]))
    marker = origin['artifacts']['.native-random-observer-disposable']
    require(descriptor(ROOT / marker['path']) == marker, 'inherited disposable marker Source')
    install_artifacts = {'native_combat_capture.gd': artifacts['collector'],
                         'native_capture_config.json': descriptor(OUT / 'case-inputs/native_capture_config.json'),
                         '.native-random-observer-disposable': marker}
    targets = [dict(namespace='project', target=name, before=row['before'], source=dict(path=row['after_path'], **row['after']))
               for name, row in paths.items()]
    for name, payload in install_artifacts.items():
        targets.append(dict(namespace='project', target=name, before=None,
                            before_policy='Existing reset/installer validates actual predecessor/absence; no pool state read here.', source=payload))
    data_targets = [dict(namespace='case-input', target=p.name, source=descriptor(p),
                         future_destination='Unique run/data; custom fixtures staged in pool/data only by separately released existing host policy.')
                    for p in sorted((OUT / 'case-inputs').glob('*.json'))]
    total = sum(t['source']['size'] for t in targets)
    count = len(targets)
    save(OUT / 'install-targets.json', dict(schema='phase462-declared-install-payloads/1', project=targets,
        case_inputs=data_targets, project_install_count=count, project_install_source_bytes=total,
        case_staging_count=len(data_targets), case_staging_source_bytes=sum(t['source']['size'] for t in data_targets),
        old_reference=dict(max_count=78, max_bytes=815198),
        within_old_project_install_reference=count <= 78 and total <= 815198,
        actual_pool_preimages_verified=False, executable_installer_or_host=False,
        note='The old78/815198 limit applies only to project patch+artifact preload. Three run/data staging copies are separate; config is explicitly also a project artifact.'))
    save(OUT / 'conservation.json', dict(schema='phase462-source-conservation/1', original_target_count=75,
        unchanged_non_sink_targets=inherited, unchanged_non_sink_count=74,
        unchanged_non_sink_GD_count=sum(t['target'].endswith('.gd') for t in inherited),
        SITES=107, new_hook_sites=0, MATRIX_API_bytes_exact=True, collector_function_changes=0,
        changed_functions={key: report['changed_functions'] for key, report in reports.items()},
        inverse='ALL_THREE_COMPLETE_BYTE_STREAMS_RECONSTRUCTED', generated_schema_imports=0))
    freeze_files = [descriptor(p) for p in sorted(OUT.rglob('*')) if p.is_file()]
    freeze_files += [row['source'] for row in inherited] + [marker, descriptor(Path(__file__)), descriptor(ROOT / SPEC)]
    save(OUT / 'combined-source-freeze.json', dict(schema='phase462-source-freeze/1', files=freeze_files,
        paths=paths, artifacts=install_artifacts, collector=artifacts['collector'], schema_module=artifacts['schema'],
        active_source_tuple=descriptor(OUT / 'source-tuple.json'), profile=plan['profile'],
        observer_version=plan['version'], terminal_policy=patch['terminal_policy'],
        native_source_origin=descriptor(OUT / 'source-authority.json'), schema_case=plan['source_case'],
        accepted_source_controls=[], host_ready=False, native=0, model=0))
    compile(read_source(Path(__file__)), __file__, 'exec', dont_inherit=True)
    save(OUT / 'compile-only.json', dict(schema='phase462-compile-only/1', discarded_compile_objects=2,
        producer=True, schema_compiled=True, GD_lexical_conservation_only=True, Godot_parse=0,
        generated_module_imports=0, candidate_imports=0, schema_calls=0, models=0, Expected_reads=0, pool_operations=0))
    save(OUT / 'first-generation-result.json', dict(schema='phase462-first-generation/1',
        status='SOURCE_GENERATED_COMPILED_NOT_INDEPENDENTLY_ACCEPTED_OR_HOST_READY', source_generation_invocations=1,
        profile=plan['profile'], slots=26, descriptors=7, King='P:6', basic='P:7', P12='Wooden Sword',
        source_tuple=descriptor(OUT / 'source-tuple.json'), install_count=count, install_source_bytes=total,
        old_reference_exceeded=not (count <= 78 and total <= 815198),
        if_reference_exceeded='No installation permitted; Root must select the exact new payload budget before any later host integration.',
        imports=0, schema_calls=0, models=0, Godot=0, Expected_reads=0, pool_inventory_or_writes=0,
        independent_controls='PENDING; no final self-acceptance', next='Independent Source/typed/binding/inverse controls only.'))
    owned = [descriptor(ROOT / SPEC), descriptor(Path(__file__))]
    owned += [descriptor(p) for p in sorted(OUT.rglob('*')) if p.is_file()]
    owned += [row['source'] for row in inherited] + [marker]
    save(OUT / 'source-owner.json', dict(schema='phase462-source-owner/1', files=owned, no_more_writes=True,
        status='SOURCE_ONLY_PENDING_INDEPENDENT_TARGETED_CONTROLS_NO_HOST_OR_NATIVE_RELEASE'))
    return descriptor(OUT / 'source-owner.json')


def main():
    require(not OUT.exists(), 'unique Source generation directory already exists')
    OUT.mkdir()
    save(OUT / 'generation-started.json', dict(schema='phase462-generation-started/1', attempt=1,
        producer=descriptor(Path(__file__)), spec=descriptor(ROOT / SPEC), imports=0, native=0, models=0))
    try:
        sources, patch, inherited = verify_preimages()
        save(OUT / 'source-before.json', dict(files=[descriptor(p) for p in sources.values()], inherited_targets=inherited))
        request = json.loads(read_source(sources['request']))
        plan = build_fixed_plan(request)
        save(OUT / 'fixed-plan.json', plan)
        save(OUT / 'fixed-v8-fixture.json', plan['fixture'])
        for name, value in (('custom_player.json', plan['native_fixtures']['P']),
                            ('custom_opponent.json', plan['native_fixtures']['O']),
                            ('native_capture_config.json', plan['config'])):
            save(OUT / 'case-inputs' / name, value)
        save(OUT / 'source-authority.json', dict(schema='phase462-source-authority/1', producer=descriptor(Path(__file__)),
             spec=descriptor(ROOT / SPEC), request=descriptor(sources['request']), review=descriptor(sources['review']),
             inherited_patch=descriptor(sources['patch']), scope='SOURCE_ONLY_NOT_RUNTIME_OR_NATIVE_ADMISSION'))
        binding_contract = dict(schema='phase360-binding-source-contract/1', schema_origin=descriptor(sources['schema']),
            producer_source_origin=descriptor(OUT / 'source-authority.json'), fixed_slot_map=descriptor(OUT / 'fixed-plan.json'),
            fixed_fixture=descriptor(OUT / 'fixed-v8-fixture.json'),
            evidence_policy='SOURCE_ORIGIN_ONLY_NOT_INDEPENDENT_ACCEPTANCE_OR_RUNTIME_ADMISSION')
        sink = derive_sink(sources['sink'], plan)
        collector = derive_collector(sources['collector'], plan)
        schema = derive_schema(sources['schema'], plan, binding_contract)
        artifacts, reports = {}, {}
        for name, delta, path, changed in [
            ('sink', sink, OUT / 'after-source/native_random_observer_sink_v7.gd',
             ['state', 'bind_fixed_inventory', 'source_selected_auto', 'ui_open', 'rng_initial_capture']),
            ('collector', collector, OUT / 'collector.gd', []),
            ('schema', schema, OUT / 'schema/phase462_king_basic_observer_schema.py',
             ['validate_state', 'validate_single_king_fixture', 'validate_single_king_fresh_facts',
              'validate_single_king_source_defaults', 'validate_single_king_input_provenance',
              'primitive_context', 'validate_primitive', 'validate_record', '_binding_validate_value'])]:
            artifacts[name], reports[name] = delta.finish(path, changed)
        result = freeze_source(plan, patch, inherited, artifacts, reports)
        print(json.dumps(dict(status='SOURCE_FROZEN_NOT_EXECUTED', owner=result), sort_keys=True))
        return 0
    except Exception as error:
        save(OUT / 'first-generation-error.json', dict(schema='phase462-generation-error/1',
            error_type=type(error).__name__, message=str(error), traceback=traceback.format_exc(),
            retry_authorized=False, generated_schema_imports=0, Godot=0, models=0, pool_operations=0))
        raise


if __name__ == '__main__':
    raise SystemExit(main())
