"""Finite King projection/sealer SOURCE; native reader remains closed."""

SCHEMA_ORIGIN = {'path': 'tests/phase360_king_observer_schema.py', 'size': 190693, 'sha256': 'd4229ce6d94525b5bc0b93f7ab80617b96041d65fb4cd4f425e0b07a50a4c5f6'}
SOURCE_CONTROL_PINS = [{'path': 'data/phase359-root-acceptance/accepted.json', 'size': 1257, 'sha256': '8fbcb7148ee12aa424cf101daf39ddc04606db5938c36099cb2d9e873e34a770'}, {'path': 'data/phase359-independent-producer-review/review.json', 'size': 3761, 'sha256': '1e8b9556beb6fd46cd67504b8c10f890da645ea6b26c89e3d67c4d4510e3c250'}, {'path': 'data/phase359-independent-producer-review/owned-files.json', 'size': 3038, 'sha256': '2a3b830d9a46902a8279017a6a47c70c4c735f842ee443595a4ff355acd37072'}, {'path': 'data/phase359-king-producer-source/source-owner.json', 'size': 20694, 'sha256': 'b711ccbbbc2495eaeef8559c1c4ce7ac11f25b4c3832a350131963282f59abc3'}, {'path': 'data/phase359-king-producer-source/producer-source-freeze.json', 'size': 43099, 'sha256': '419a79c51f9a5c92c56edc4a2fd0ca7fd829f0471f747652015a39e26035204a'}, {'path': 'data/phase360-root-acceptance/accepted.json', 'size': 1375, 'sha256': '23915057cc663ca2dc9f885159c2e62780787e48d576a6f98c6ba435a306dc5e'}, {'path': 'data/phase360-independent-schema-review/review.json', 'size': 3895, 'sha256': '7e0fad1907dbff5f488880d806e3d4ff63afe8a2d909c416c05189ee54669603'}, {'path': 'data/phase360-independent-schema-review/owned-files.json', 'size': 4836, 'sha256': 'a2cc615a3dfb72a070d40602fe15a7a8f0e4b3370bd5f4aef0779e462cf07747'}, {'path': 'data/phase360-schema-auxiliary-binding-source/source-owner.json', 'size': 2949, 'sha256': 'ed0ff1578733c306042e8195ae6a6f85fbab3033cb5ca9f4d37915207e372542'}, {'path': 'data/phase360-schema-auxiliary-binding-source/schema-source-freeze.json', 'size': 2080, 'sha256': '9d886addaaeac5fc631ec15ad8f689b4b892c6b877f2b4f5476a24a25d6b7312'}, {'path': 'tests/phase360_king_observer_schema.py', 'size': 190693, 'sha256': 'd4229ce6d94525b5bc0b93f7ab80617b96041d65fb4cd4f425e0b07a50a4c5f6'}, {'path': 'data/phase355-king-finite-source/fixed-A-v8-fixture.json', 'size': 5636, 'sha256': 'e969df30573a01e1ce7a0efa65a90b7f153d3e32636492cb6832ad705ee8c627'}, {'path': 'data/phase356-king-admission-source-repair/candidate-source-freeze.json', 'size': 2783, 'sha256': 'a135fc774658dab7f9b16d9e9955252f700c030fb0fb661d7db0c06ec3424afb'}]
ROOT_SOURCE_STATUSES = [({'path': 'data/phase359-root-acceptance/accepted.json', 'size': 1257, 'sha256': '8fbcb7148ee12aa424cf101daf39ddc04606db5938c36099cb2d9e873e34a770'}, 'ACCEPTED_SOURCE_COMPONENT_PIPELINE_BLOCKED'), ({'path': 'data/phase360-root-acceptance/accepted.json', 'size': 1375, 'sha256': '23915057cc663ca2dc9f885159c2e62780787e48d576a6f98c6ba435a306dc5e'}, 'ACCEPTED_SOURCE_AND_SYNTHETIC_CONTROLS_NATIVE_CLOSED')]
SOURCE_ORIGIN_CONTRACT = {'schema': 'phase361-reviewed-SOURCE-origins/1', 'controls': [{'path': 'data/phase359-root-acceptance/accepted.json', 'size': 1257, 'sha256': '8fbcb7148ee12aa424cf101daf39ddc04606db5938c36099cb2d9e873e34a770'}, {'path': 'data/phase359-independent-producer-review/review.json', 'size': 3761, 'sha256': '1e8b9556beb6fd46cd67504b8c10f890da645ea6b26c89e3d67c4d4510e3c250'}, {'path': 'data/phase359-independent-producer-review/owned-files.json', 'size': 3038, 'sha256': '2a3b830d9a46902a8279017a6a47c70c4c735f842ee443595a4ff355acd37072'}, {'path': 'data/phase359-king-producer-source/source-owner.json', 'size': 20694, 'sha256': 'b711ccbbbc2495eaeef8559c1c4ce7ac11f25b4c3832a350131963282f59abc3'}, {'path': 'data/phase359-king-producer-source/producer-source-freeze.json', 'size': 43099, 'sha256': '419a79c51f9a5c92c56edc4a2fd0ca7fd829f0471f747652015a39e26035204a'}, {'path': 'data/phase360-root-acceptance/accepted.json', 'size': 1375, 'sha256': '23915057cc663ca2dc9f885159c2e62780787e48d576a6f98c6ba435a306dc5e'}, {'path': 'data/phase360-independent-schema-review/review.json', 'size': 3895, 'sha256': '7e0fad1907dbff5f488880d806e3d4ff63afe8a2d909c416c05189ee54669603'}, {'path': 'data/phase360-independent-schema-review/owned-files.json', 'size': 4836, 'sha256': 'a2cc615a3dfb72a070d40602fe15a7a8f0e4b3370bd5f4aef0779e462cf07747'}, {'path': 'data/phase360-schema-auxiliary-binding-source/source-owner.json', 'size': 2949, 'sha256': 'ed0ff1578733c306042e8195ae6a6f85fbab3033cb5ca9f4d37915207e372542'}, {'path': 'data/phase360-schema-auxiliary-binding-source/schema-source-freeze.json', 'size': 2080, 'sha256': '9d886addaaeac5fc631ec15ad8f689b4b892c6b877f2b4f5476a24a25d6b7312'}, {'path': 'tests/phase360_king_observer_schema.py', 'size': 190693, 'sha256': 'd4229ce6d94525b5bc0b93f7ab80617b96041d65fb4cd4f425e0b07a50a4c5f6'}, {'path': 'data/phase355-king-finite-source/fixed-A-v8-fixture.json', 'size': 5636, 'sha256': 'e969df30573a01e1ce7a0efa65a90b7f153d3e32636492cb6832ad705ee8c627'}, {'path': 'data/phase356-king-admission-source-repair/candidate-source-freeze.json', 'size': 2783, 'sha256': 'a135fc774658dab7f9b16d9e9955252f700c030fb0fb661d7db0c06ec3424afb'}], 'scope': 'SOURCE_ACCEPTANCES_ONLY_NOT_CAPTURE_OR_MODEL_PERMISSION'}
SOURCE_NAMES = ('fixture.json', 'player_fixture.json', 'observer7-input.jsonl', 'observer7-lineage.jsonl', 'observer7-metadata.jsonl', 'observer7-primitives.jsonl', 'king-clock-checkpoint.json', 'king-clock-passes.jsonl', 'king-input-facts.json', 'king-ui-authority.jsonl', 'king-rng-checkpoint.json', 'king-slot-bindings.json')
RUNTIME_KEYS = ('schema', 'mode', 'profile_id', 'checkpoint', 'environment', 'nodes', 'timer_lineage', 'initial_items', 'prepare_order', 'activate_order', 'terminal_profile', 'frame_clock', 'king_particles', 'root_node', 'processing_nodes', 'inactive_auxiliaries', 'ui_authority')
STACK_NAMES = {101: 'Lucky', 102: 'Regeneration', 100: 'Block', 103: 'Vampirism', 104: 'Spikes', 105: 'Mana', 109: 'Blind', 106: 'Empower', 108: 'Poison', 107: 'Heat', 110: 'Cold'}
ZERO_BITS = '0000000000000000'
AUXILIARY_LEMMA = 'original1.1.8-Ranger-fixed-King-no-Rage-callers/1'
TERMINAL_PROFILE = 'source-two-physics-idle-pre-internal/1'

"""SOURCE template, appended after frozen constants. No CLI or battle imports."""
import hashlib
import json
import os
from copy import deepcopy
from pathlib import Path, PurePosixPath

import phase360_king_observer_schema as schema


def _same(actual, expected):
    if type(actual) is not type(expected):
        raise ValueError('exact SOURCE/projection type')
    if type(expected) is dict:
        schema.exact(actual, expected)
        for key in expected:
            _same(actual[key], expected[key])
    elif type(expected) is list:
        if len(actual) != len(expected):
            raise ValueError('exact SOURCE/projection sequence length')
        for left, right in zip(actual, expected):
            _same(left, right)
    elif actual != expected:
        raise ValueError('exact SOURCE/projection value')


def _pin(raw):
    return dict(size=len(raw), sha256=hashlib.sha256(raw).hexdigest())


def _safe_root(path):
    root = Path(path).absolute()
    if not root.is_dir() or any(parent.is_symlink() for parent in (root, *root.parents)):
        raise ValueError('existing directory with no symlink ancestors required')
    return root


def _file(root, relative):
    name = PurePosixPath(relative)
    if (type(relative) is not str or name.is_absolute() or str(name) != relative
            or not name.parts or any(part in ('.', '..') for part in name.parts)):
        raise ValueError('canonical relative SOURCE path')
    path = root.joinpath(*name.parts)
    if any(parent.is_symlink() for parent in (path, *path.parents)):
        raise ValueError('SOURCE symlink rejected')
    return path


def _read_pinned(root, row):
    schema.exact(row, ('path', 'size', 'sha256'))
    schema.integer(row['size'], 1, 268435456)
    path = _file(root, row['path'])
    if not path.is_file() or path.stat().st_size != row['size']:
        raise ValueError('missing/incorrect pinned SOURCE file')
    raw = path.read_bytes()
    if _pin(raw) != {key: row[key] for key in ('size', 'sha256')}:
        raise ValueError('SOURCE bytes identity mismatch')
    return raw


def _verify_source_controls(source_root):
    root = _safe_root(source_root)
    for row in SOURCE_CONTROL_PINS:
        _read_pinned(root, row)
    expected_schema = _file(root, SCHEMA_ORIGIN['path'])
    if Path(schema.__file__).resolve() != expected_schema.resolve():
        raise ValueError('imported schema is outside exact SOURCE root')
    for row, status in ROOT_SOURCE_STATUSES:
        value = schema.strict_json_loads(_read_pinned(root, row).decode('utf-8'))
        if value['status'] != status or value['King_production_admitted'] is not False:
            raise ValueError('actual bounded SOURCE root acceptance only')
    return root


def _require_future_capture_closure():
    # No flag, caller-provided checker, or old accepted patch can open this.
    # Future SOURCE must replace this pending gate by the actual joint identity
    # check only after collector/host/candidate exist and are independently read.
    raise ValueError('PENDING_COLLECTOR_HOST_SHARED_CANDIDATE_CLOSURE: no actual12 capture release admitted')


def _validate_sources(source_bytes, aliases=None):
    if _pin(Path(schema.__file__).read_bytes()) != {key: SCHEMA_ORIGIN[key] for key in ('size', 'sha256')}:
        raise ValueError('exact frozen schema SOURCE identity required')
    schema.exact(source_bytes, SOURCE_NAMES)
    raw11 = {name: source_bytes[name] for name in schema.INPUT_FILES}
    auxiliary = source_bytes['king-slot-bindings.json']
    proof = schema.validate_sources_with_binding(raw11, auxiliary, schema.BINDING_SOURCE_CONTRACT)
    joined = proof['binding_join']
    if aliases is not None:
        _same(aliases, joined)
    return schema.decode_sources(raw11), joined, proof['raw_sources']


def read_and_validate_sources(source_root, lawful_dir, release_descriptor):
    """Closed native reader; SOURCE validation precedes any release/capture read.

    The body defines a small future input-only release interface, not a release
    instance or authority. The pending host-code gate currently always rejects.
    """
    root = _verify_source_controls(source_root)
    _require_future_capture_closure()
    release = schema.strict_json_loads(_read_pinned(root, release_descriptor).decode('utf-8'))
    schema.exact(release, ('schema', 'status', 'input_files', 'permissions', 'source_origin'))
    if release['schema'] != 'king12-input-only-release/1' or release['status'] != 'INPUT_PREPARATION_ONLY_RELEASED_SINGLE_KING_A':
        raise ValueError('exact input-only release format')
    schema.exact(release['permissions'], ('models', 'expected_reads', 'new_native'))
    if any(type(value) is not int or value != 0 for value in release['permissions'].values()):
        raise ValueError('strictINT0 input-only permissions')
    _same(release['source_origin'], SOURCE_ORIGIN_CONTRACT)
    schema.exact(release['input_files'], SOURCE_NAMES)
    directory = _safe_root(lawful_dir)
    sources = {}
    for name in SOURCE_NAMES:
        identity = release['input_files'][name]
        schema.exact(identity, ('size', 'sha256'))
        sources[name] = _read_pinned(directory, dict(path=name, **identity))
    decoded, aliases, pins = _validate_sources(sources)
    return dict(source_bytes=sources, aliases=aliases, raw_sources=pins,
                source_origin=deepcopy(SOURCE_ORIGIN_CONTRACT), native_admitted=False,
                input_bundle_created=False, decoded_names=list(decoded))


def _one(rows, site, edge):
    found = [row for row in rows if row['site'] == site and row['edge'] == edge]
    if len(found) != 1:
        raise ValueError('unique projection SOURCE site/edge')
    return found[0]


def _role(raw):
    if raw.startswith('buff:'):
        parts = raw.split(':')
        if len(parts) != 3 or parts[1] not in ('P', 'O'):
            raise ValueError('actual buff role')
        category = schema.decimal(parts[2])
        if category not in STACK_NAMES:
            raise ValueError('SOURCE buff category')
        return 'buff:' + parts[1] + ':' + STACK_NAMES[category]
    return raw


def _order(entry, aliases):
    arguments = schema.argument_fields(entry['payload']['arguments'])
    refs = arguments['items']
    if refs['type'] != 'array':
        raise ValueError('actual Game items argument array')
    order = []
    for ref in refs['values']:
        schema.validate_typed(ref)
        role = aliases['native_to_role'].get(ref.get('native_id'))
        if (ref['type'] != 'native_ref' or role not in schema.FIXED_ROLES
                or ref['role'] != role or aliases['role_to_native'][role] != ref['native_id']):
            raise ValueError('Game items source alias identity')
        order.append(role)
    if len(order) != 39 or len(set(order)) != 39 or set(order) != schema.FIXED_ROLES:
        raise ValueError('complete39 source order')
    return order


def project_fixture_and_runtime(source_bytes, aliases):
    """Pure finite ABI projection, not runtime/admission validation or execution."""
    decoded, aliases, pins = _validate_sources(source_bytes, aliases)
    inputs = decoded['observer7-input.jsonl']
    pre = _one(inputs, 'Core/Game.gd::prepareItems', 'checkpoint')
    act = _one(inputs, 'Core/Game.gd::activateItems', 'checkpoint')
    pe = _one(inputs, 'Core/Game.gd::prepareItems', 'enter')
    ae = _one(inputs, 'Core/Game.gd::activateItems', 'enter')
    if pre['sequence'] + 1 != pe['sequence'] or act['sequence'] + 1 != ae['sequence']:
        raise ValueError('actual checkpoint immediately precedes entry')
    for checkpoint, entry in ((pre, pe), (act, ae)):
        for key in ('physics_frame', 'idle_frame', 'util_time', 'combat_time'):
            if checkpoint['stamp'][key] != entry['stamp'][key]:
                raise ValueError('checkpoint/entry exact source clock continuity')
    if ae['stamp']['combat_time'] != {'type': 'float', 'binary64_be': ZERO_BITS}:
        raise ValueError('actual activation combat clock REAL+0')
    if ae['stamp']['util_time'] != {'type': 'float', 'binary64_be': decoded['king-clock-checkpoint.json']['checkpoint']['util_time_bits']}:
        raise ValueError('actual activation/finite header Util clock bits')
    metadata = _one(decoded['observer7-metadata.jsonl'], 'Sheets/ItemBook.gd::detectMentionedStacks', 'loaded_descriptors')
    if metadata['sequence'] >= pre['sequence']:
        raise ValueError('SOURCE metadata before preparation')
    prepare, activate = _order(pe, aliases), _order(ae, aliases)
    if prepare != activate:
        raise ValueError('distinct preparation/activation order unsupported')
    initial = {}
    for checkpoint in (pre, act):
        for item in checkpoint['payload']['items']:
            fields = item['fields']
            for name in ('lastActivationTime', 'lastTriggerTime'):
                if fields[name] != {'type': 'float', 'binary64_be': ZERO_BITS}:
                    raise ValueError('fresh SOURCE limiter REAL+0 required')
            for name in ('activationsThisFrame', 'triggersThisFrame'):
                if fields[name] != {'type': 'int', 'decimal': '0'}:
                    raise ValueError('fresh SOURCE limiter INT0 required')
            if item['dragged'] != {'type': 'bool', 'value': False} or item['moveback_running'] != {'type': 'bool', 'value': False}:
                raise ValueError('no picking or moveback tween source')
            if fields['consumed'] != {'type': 'bool', 'value': False}:
                raise ValueError('fresh unconsumed source item')
            if checkpoint is pre:
                if item['cachedAffectedItems'] != {'type': 'dictionary', 'entries': []}:
                    raise ValueError('unprepared fresh cache must be empty')
                initial[item['instance']] = dict(lastActivationTime_bits=ZERO_BITS, lastTriggerTime_bits=ZERO_BITS,
                    activationsThisFrame=0, triggersThisFrame=0, dragged=False, moveback_running=False, cache_fresh=True)
    processing, nodes, lineage, auxiliaries = [], [], {}, {}
    for raw in act['payload']['nodes']:
        node = deepcopy(raw['node'])
        role = _role(raw['role'])
        node['role'] = role  # separate model copy; the source row remains intact
        processing.append(node)
        timer = raw['timer']
        if timer is not None:
            if (timer['stopped'] is not True or timer['autostart'] is not False or timer['paused'] is not False
                    or timer['time_left'] != {'type': 'float', 'binary64_be': ZERO_BITS}
                    or node['internal_physics'] is not False or node['internal_idle'] is not False):
                raise ValueError('fresh inactive Timer source; no public0 private inversion')
        if role.startswith('aux:'):
            if timer is None:
                raise ValueError('actual auxiliary Timer required')
            auxiliaries[role] = dict(source_lemma=AUXILIARY_LEMMA, lineage='fresh_configured',
                wait_time_bits=timer['wait_time']['binary64_be'], one_shot=timer['one_shot'], process_mode=timer['process_mode'])
            continue
        if role in ('root_viewport', 'game'):
            continue
        output = dict(role=role, path=node['path'], positions=deepcopy(node['positions']), priority=node['priority'],
                      kind='timer' if timer is not None else 'ordinary')
        if timer is not None:
            output.update(wait_time_bits=timer['wait_time']['binary64_be'], one_shot=timer['one_shot'], process_mode=timer['process_mode'])
            lineage[role] = 'fresh_configured'
        nodes.append(output)
    particles = {}
    for king in decoded['king-input-facts.json']['kings']:
        parts = {}
        for kind in ('activation', 'drag'):
            fact = king[kind]
            parts[kind] = dict(node=deepcopy(fact['node']), getters={
                **{key + '_bits': fact[key]['binary64_be'] for key in ('lifetime', 'explosiveness', 'speed_scale')},
                **{key: fact[key]['value'] for key in ('one_shot', 'visible', 'emitting')}})
        particles[king['instance']] = parts
    root = next(row for row in processing if row['role'] == 'root_viewport')
    runtime = dict(schema='native-v8-runtime-input/1', mode='genuine', profile_id=schema.PROFILE,
        checkpoint=dict(util_time_bits=ae['stamp']['util_time']['binary64_be'], combat_time_bits=ae['stamp']['combat_time']['binary64_be'],
                        source_phase='Core/Game.gd::activateItems:enter'),
        environment=dict(fps=60, scale=1.0, paused=False, no_pending_gameplay_transform=True),
        nodes=nodes, timer_lineage=lineage, initial_items=initial, prepare_order=prepare, activate_order=activate,
        terminal_profile=TERMINAL_PROFILE,
        frame_clock=dict(deepcopy(decoded['king-clock-checkpoint.json']), passes=deepcopy(decoded['king-clock-passes.jsonl'])),
        king_particles=particles, root_node=deepcopy(root), processing_nodes=processing,
        inactive_auxiliaries=auxiliaries, ui_authority=deepcopy(decoded['king-ui-authority.jsonl']))
    schema.exact(runtime, RUNTIME_KEYS)
    return deepcopy(schema.FIXED_FIXTURE), runtime, dict(schema='phase361-field-projection-proof/1', raw_sources=pins,
        aliases=deepcopy(aliases), dataflow='PROOF_ONLY_NOT_STATE_OR_ADMISSION',
        ui_authority='compatibility validation-only ABI, stored but never UI business commands or stop input',
        defaults='constructor constants only; observed private/resource/cache values validate then remain outside bundle',
        native_admitted=False, projection_does_not_open_runtime356=True)


def _primitive_projection(row):
    schema.validate_record(row)
    value = row['payload']
    kind = value['kind']
    result = dict(kind=kind, label=value['label'])
    if kind in ('randf', 'randf_range'):
        args = []
        for arg in value['args']:
            if arg['type'] == 'float':
                args.append(arg['binary64_be'])
            elif row['site'] == 'Utility/Util.gd::roll' and arg == {'type': 'int', 'decimal': '0'}:
                args.append(ZERO_BITS)
            else:
                raise ValueError('unknown primitive argument conversion')
        if value['value']['type'] != 'float':
            raise ValueError('actual primitive REAL return required')
        result.update(args=args, value_bits=value['value']['binary64_be'])
    elif kind == 'randi_range':
        args = []
        for arg in value['args']:
            if arg['type'] != 'int':
                raise ValueError('actual randi endpoint INT required')
            args.append(schema.integer(schema.decimal(arg['decimal']), -(1 << 31), (1 << 31) - 1))
        if value['value']['type'] != 'int':
            raise ValueError('actual randi return INT required')
        result.update(args=args, value=schema.decimal(value['value']['decimal']))
    else:
        raise ValueError('K1 forbids global_u32 and unknown primitive')
    _check_tape_row(result)
    return result


def _check_tape_row(row):
    kind = row['kind']
    if kind in ('randf', 'randf_range'):
        schema.exact(row, ('kind', 'label', 'args', 'value_bits'))
        if type(row['args']) is not list or len(row['args']) != (0 if kind == 'randf' else 2):
            raise ValueError('float Tape arity')
        args = [schema._single_king_real(bits) for bits in row['args']]
        value = schema._single_king_real(row['value_bits'])
        low, high = (0.0, 1.0) if not args else (min(args), max(args))
        if not low <= value <= high:
            raise ValueError('float Tape return bounds')
    elif kind == 'randi_range':
        schema.exact(row, ('kind', 'label', 'args', 'value'))
        if type(row['args']) is not list or len(row['args']) != 2:
            raise ValueError('integer Tape arity')
        args = [schema.integer(value, -(1 << 31), (1 << 31) - 1) for value in row['args']]
        if not min(args) <= schema.integer(row['value']) <= max(args):
            raise ValueError('integer Tape return bounds')
    else:
        raise ValueError('K1 Tape kind')
    if type(row['label']) is not str or not row['label']:
        raise ValueError('Tape label')


def project_primitives(source_bytes, aliases):
    decoded, aliases, pins = _validate_sources(source_bytes, aliases)
    activation = _one(decoded['observer7-input.jsonl'], 'Core/Game.gd::activateItems', 'enter')
    draws, origin = [], []
    for row in decoded['observer7-primitives.jsonl']:
        if row['sequence'] <= activation['sequence']:
            raise ValueError('selected battle primitive before actual activation')
        draws.append(_primitive_projection(row))
        origin.append(row['sequence'])
    return draws, dict(schema='phase361-primitive-projection-proof/1', original_sequences=origin,
                       raw_sources=pins, physical_order_preserved=True, native_admitted=False)


def _json_bytes(value):
    return (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n').encode('utf-8')


def _fsync_directory(path):
    descriptor = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def seal_once(bundle, proof, before, output_dir, source_root):
    """Engineering codec/seal only. It grants no release or model permission."""
    _verify_source_controls(source_root)
    schema.exact(bundle, ('schema', 'fixture', 'runtime', 'draws', 'synthetic_seed'))
    if bundle['schema'] != 'native-v8-input-only/1' or bundle['synthetic_seed'] is not None:
        raise ValueError('genuine five-key bundle, no synthetic seed')
    _same(bundle['fixture'], schema.FIXED_FIXTURE)
    schema.exact(bundle['runtime'], RUNTIME_KEYS)
    if (bundle['runtime']['profile_id'] != schema.PROFILE or bundle['runtime']['mode'] != 'genuine'
            or bundle['runtime']['terminal_profile'] != TERMINAL_PROFILE):
        raise ValueError('exact pending finite profile only')
    if type(bundle['draws']) is not list:
        raise ValueError('nonNULL actual Tape required')
    for row in bundle['draws']:
        _check_tape_row(row)
    if type(proof) is not dict or type(before) is not dict:
        raise ValueError('engineering proof/before objects')
    directory = Path(output_dir).absolute()
    _safe_root(directory.parent)
    if directory.exists() or directory.is_symlink():
        raise ValueError('new output directory only; no overwrite/retry')
    directory.mkdir()
    _fsync_directory(directory.parent)
    identities = {}
    for name, value in (('input-bundle.json', bundle), ('input-proof.json', proof), ('inputs-before-interpretation.json', before)):
        raw = _json_bytes(value)
        with (directory / name).open('xb') as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        for unused in range(2):
            if (directory / name).read_bytes() != raw:
                raise ValueError('sealed output double readback mismatch')
        identities[name] = _pin(raw)
    seal = dict(schema='phase361-joint-input-engineering-seal/1', files=identities,
                native_admitted=False, model_permission=False, runtime356='UNCHANGED_CLOSED')
    with (directory / 'input-joint-seal.json').open('xb') as stream:
        stream.write(_json_bytes(seal)); stream.flush(); os.fsync(stream.fileno())
    _fsync_directory(directory)
    if schema.strict_json_loads((directory / 'input-joint-seal.json').read_text()) != seal:
        raise ValueError('jointseal actual readback')
    receipt = dict(schema='phase361-engineering-seal-receipt/1', status='FILES_SEALED_NOT_RUNTIME_OR_NATIVE_ACCEPTANCE',
                   seal=_pin((directory / 'input-joint-seal.json').read_bytes()), models=0, native=0,
                   input_source_authorization='Reader remains pending until actual collector/host/shared candidate closure')
    with (directory / 'engineering-receipt.json').open('xb') as stream:
        stream.write(_json_bytes(receipt)); stream.flush(); os.fsync(stream.fileno())
    owner = dict(schema='phase361-engineering-output-owner/1', files={
        path.name: _pin(path.read_bytes()) for path in directory.iterdir() if path.is_file()})
    with (directory / 'owned-files.json').open('xb') as stream:
        stream.write(_json_bytes(owner)); stream.flush(); os.fsync(stream.fileno())
    _fsync_directory(directory)
    for name, identity in owner['files'].items():
        if _pin((directory / name).read_bytes()) != identity:
            raise ValueError('engineering owner readback')
    return receipt
