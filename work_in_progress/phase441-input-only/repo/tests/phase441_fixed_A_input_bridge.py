"""Fixed401-A INPUT-only projection. Author must not import or run this module."""
import argparse
from copy import deepcopy
import hashlib
import json
import math
import os
from pathlib import Path
import re
import stat
import struct
import phase391_king_observer_schema as native_schema

REPO = Path('/workspace/python-original-engine/repo')
CONTEXT = {'path': 'data/phase441-fixed-A-input-source/context.json', 'size': 7919, 'sha256': '4cb8efbb24c78727de9dd3028499524561466e188302f944cd4abe5e4eba88df'}
STATUS = 'INPUT_ONLY_NOT_RUNTIME_VALIDATED'
RUNTIME_SCHEMA = 'native-v8-pure-combat-runtime-input/441'
PROFILE = 'pure-combat-fixed-king-A-input441/1'
RUNTIME_KEYS = ('schema','mode','profile_id','checkpoint','environment','nodes','timer_initial','initial_items','initial_characters','prepare_order','activate_order','terminal_profile','frame_clock','processing_nodes')
EXCLUDED_TIMERS = frozenset(('king_hide:P:12','king_drag:P:12'))
STACK_NAMES = {100:'Block',101:'Lucky',102:'Regeneration',103:'Vampirism',104:'Spikes',105:'Mana',106:'Empower',107:'Heat',108:'Poison',109:'Blind',110:'Cold'}
ZERO_BITS = '0000000000000000'
DEFERRED = ('constructor/prepare equivalence','ordinary callbacks/transform/RNG noninterference','King setState/log behavior','candidate runtime acceptance and same-instance diagnostics','strict output/comparator mapping')
INPUT_PINS = {'fixture.json': {'path': '/workspace/native-combat-20261013/runs/original027-king-single-A-20261026-attempt06/output/capture/fixture.json', 'size': 771, 'sha256': '98ae29e5cbe3ae60504cee9d994ce76a27bd10d8d372d5281e6d681e500869b1'}, 'player_fixture.json': {'path': '/workspace/native-combat-20261013/runs/original027-king-single-A-20261026-attempt06/output/capture/player_fixture.json', 'size': 1676, 'sha256': 'a42675c3fedb0651e4309754403d5658edcce869f85edb07963e7a2f87391c56'}, 'observer7-input.jsonl': {'path': '/workspace/native-combat-20261013/runs/original027-king-single-A-20261026-attempt06/output/capture/observer7-input.jsonl', 'size': 306081, 'sha256': '00158549c266456a1b2a29ac14c395a47acb13eb441fc6a4be7056b21bfa6616'}, 'observer7-lineage.jsonl': {'path': '/workspace/native-combat-20261013/runs/original027-king-single-A-20261026-attempt06/output/capture/observer7-lineage.jsonl', 'size': 75657, 'sha256': '5c57025f62e96d05e80dad16f77b1fd2d3ea4688ed717b3708cb4747c01262e0'}, 'observer7-metadata.jsonl': {'path': '/workspace/native-combat-20261013/runs/original027-king-single-A-20261026-attempt06/output/capture/observer7-metadata.jsonl', 'size': 6457, 'sha256': '2e11a7eb3996d9fd0f9edd1146a1b190e9be95e92258683fbfc992033d8674f2'}, 'observer7-primitives.jsonl': {'path': '/workspace/native-combat-20261013/runs/original027-king-single-A-20261026-attempt06/output/capture/observer7-primitives.jsonl', 'size': 265642, 'sha256': '924d7be78bbdde6f655a9bd62318592b3a905ab88db4b9550324ece6a238f78d'}, 'king-clock-checkpoint.json': {'path': '/workspace/native-combat-20261013/runs/original027-king-single-A-20261026-attempt06/output/capture/king-clock-checkpoint.json', 'size': 352, 'sha256': '21ce432a668fb4406b27bbb4f4ff623a4cbb54f0c0695fb4c2bdf53a28629c73'}, 'king-clock-passes.jsonl': {'path': '/workspace/native-combat-20261013/runs/original027-king-single-A-20261026-attempt06/output/capture/king-clock-passes.jsonl', 'size': 227219, 'sha256': '660cff32026b6cd0b5942081e6c279fc0076ff6c95fee4ce1e8f7cf2d5a86526'}, 'king-input-facts.json': {'path': '/workspace/native-combat-20261013/runs/original027-king-single-A-20261026-attempt06/output/capture/king-input-facts.json', 'size': 10082, 'sha256': 'e3b2e6267a6132a53f95fd0f0322ba14fbc22115a1f5ba8dc9411a67ac3f5880'}, 'king-ui-authority.jsonl': {'path': '/workspace/native-combat-20261013/runs/original027-king-single-A-20261026-attempt06/output/capture/king-ui-authority.jsonl', 'size': 596454, 'sha256': 'bd3ddda8379be45bd13a40342b90951fa2a1e4b41a8334f7c996ab6aa0480429'}, 'king-rng-checkpoint.json': {'path': '/workspace/native-combat-20261013/runs/original027-king-single-A-20261026-attempt06/output/capture/king-rng-checkpoint.json', 'size': 772, 'sha256': '5a844bfb47cbb4491ab3ec647be315a3e7b2aa73b0373900ea7fd3d0769e51bc'}, 'king-slot-bindings.json': {'path': '/workspace/native-combat-20261013/runs/original027-king-single-A-20261026-attempt06/output/capture/king-slot-bindings.json', 'size': 20254, 'sha256': 'e326643b93a87f48864895dbfda136b3aa6feb2d03681cf943e81b3da550eefc'}}
AUDIT_PIN = {'path': 'data/phase439-timer-overlay-first-001/overlay-report.json', 'size': 1148063, 'sha256': '523974fd3e18522618bc678bc9062e83effb77d8a73f5d0d1bfdee51ad813e88'}
SCHEMA_PIN = {'path': 'tests/phase391_king_observer_schema.py', 'size': 208243, 'sha256': 'ffcddfd2cbe58307f7258c1aefad5586a9179c6c452dc59c3342f9047f31457c'}


class Rejected(ValueError):
    pass


def require(condition, reason):
    if not condition:
        raise Rejected(reason)


def same(left, right):
    return json.dumps(left, sort_keys=True, separators=(',', ':'), allow_nan=False) == json.dumps(right, sort_keys=True, separators=(',', ':'), allow_nan=False)


def strict_json(raw):
    def pairs(items):
        value = {}
        for name, item in items:
            require(name not in value, 'DUPLICATE_JSON_KEY')
            value[name] = item
        return value
    def finite(value):
        result = float(value)
        require(math.isfinite(result), 'NONFINITE_JSON_NUMBER')
        return result
    def invalid(value):
        raise Rejected('NONFINITE_JSON_CONSTANT')
    try:
        return json.loads(raw.decode('utf-8', 'strict'), object_pairs_hook=pairs,
                          parse_float=finite, parse_constant=invalid)
    except (UnicodeError, ValueError) as error:
        raise Rejected('STRICT_JSON: ' + str(error)) from error


def key(row):
    require(type(row) is dict, 'ROW_OBJECT')
    result = tuple(row.get(name) for name in ('field_id', 'phase', 'side_or_role'))
    require(all(type(x) is str for x in result), 'ROW_KEY_TYPE')
    return result


def canonical(value):
    require(type(value) is str and value, 'PATH_TYPE')
    path = Path(value)
    require(str(path) == value and '..' not in path.parts and '.' not in path.parts, 'PATH_CANONICAL')
    return path if path.is_absolute() else REPO / path


def physical(path, regular=True):
    for part in reversed((path,) + tuple(path.parents)):
        info = part.lstat()
        require(not stat.S_ISLNK(info.st_mode), 'PATH_SYMLINK')
        if part == path and regular:
            require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1, 'NONORDINARY_FILE')
        else:
            require(stat.S_ISDIR(info.st_mode), 'PATH_DIRECTORY')
    return path.lstat()


def read_pinned(descriptor, io):
    require(type(descriptor) is dict and set(descriptor) == {'path', 'size', 'sha256'}, 'PIN_SHAPE')
    require(type(descriptor['size']) is int and 0 <= descriptor['size'] <= 4194304, 'PIN_SIZE')
    require(type(descriptor['sha256']) is str and re.fullmatch('[0-9a-f]{64}', descriptor['sha256']), 'PIN_SHA')
    path = canonical(descriptor['path'])
    before = physical(path)
    require(before.st_size == descriptor['size'], 'PIN_SIZE_CHANGED')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    identity = lambda x: (x.st_dev, x.st_ino, x.st_size, x.st_mtime_ns, x.st_ctime_ns)
    try:
        opened = os.fstat(fd)
        require(identity(before) == identity(opened) and opened.st_nlink == 1, 'PIN_OPEN_IDENTITY')
        chunks, count = [], 0
        while True:
            block = os.read(fd, 65536)
            if not block:
                break
            count += len(block)
            require(count <= descriptor['size'], 'PIN_GROWTH')
            chunks.append(block)
        after = os.fstat(fd)
    finally:
        os.close(fd)
    require(identity(before) == identity(after) == identity(physical(path)), 'PIN_READ_IDENTITY')
    raw = b''.join(chunks)
    require(len(raw) == descriptor['size'] and hashlib.sha256(raw).hexdigest() == descriptor['sha256'], 'PIN_HASH')
    io.append(deepcopy(descriptor))
    return raw


def save_new(path, value):
    raw = (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode()
    require(len(raw) <= 4194304, 'OUTPUT_CAP')
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    try:
        offset = 0
        while offset < len(raw):
            count = os.write(fd, raw[offset:])
            require(count > 0, 'SHORT_WRITE')
            offset += count
        os.fsync(fd)
    finally:
        os.close(fd)
    pin = {'path': str(path), 'size': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}
    require(read_pinned(pin, []) == raw, 'OUTPUT_READBACK')
    return pin


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def verify_raw_inputs(raw12):
    require(type(raw12) is dict and set(raw12) == set(INPUT_PINS), 'EXACT_FIXED12_NAMES')
    for name, pin in INPUT_PINS.items():
        raw = raw12[name]
        require(type(raw) is bytes and len(raw) == pin['size'] and hashlib.sha256(raw).hexdigest() == pin['sha256'], 'FIXED_INPUT_IDENTITY_' + name)
    return deepcopy(INPUT_PINS)


def decode_lawful12(raw12):
    pins = verify_raw_inputs(raw12)
    raw11 = {name: raw12[name] for name in native_schema.INPUT_FILES}
    decoded = native_schema._transport_only_decode(raw11)
    for name in native_schema.CHANNEL_FILES:
        for row in decoded[name]:
            native_schema.validate_record(row)
    binding = native_schema.validate_binding_carrier(raw12['king-slot-bindings.json'], native_schema.BINDING_FIXED_PLAN)
    aliases = native_schema.join_binding_provenance(decoded, binding, native_schema.BINDING_SOURCE_CONTRACT)
    # Intentionally no full-FX source-carrier/fresh-facts/UI authority admission call.
    return decoded, aliases, {'input_descriptors': pins, 'binding_join': aliases,
                             'validation_scope': 'FIXED_BYTES_TRANSPORT_TYPED_RELATION_ONLY',
                             'full391_source_gate_called': False}


def load_accepted_initial(audit_raw):
    require(type(audit_raw) is bytes and len(audit_raw) == AUDIT_PIN['size'] and hashlib.sha256(audit_raw).hexdigest() == AUDIT_PIN['sha256'], 'ACCEPTED439_AUDIT_IDENTITY')
    audit = strict_json(audit_raw)
    require(audit.get('schema') == 'phase439-timer-combat-initial-overlay/1' and audit.get('profile') == 'pure-combat-initial-fixed-king-A/437', 'ACCEPTED439_PROFILE')
    require(same(audit.get('counts'), {'DIRECT': 1289, 'SOURCE_DERIVED': 74, 'MISSING': 0}) and len(audit.get('required_rows', [])) == 1363 and len(audit.get('excluded_presentation', [])) == 116, 'ACCEPTED439_COUNTS')
    result = {}
    for ordinal, row in enumerate(audit['required_rows']):
        ident = key(row)
        require(ident not in result and row.get('classification') in ('DIRECT_OBSERVATION', 'SOURCE_DERIVED') and row.get('proof_complete') is True and row.get('validation_result') == 'SUPPORTED' and 'actual_value' in row, 'ACCEPTED439_SUPPORTED_UNIQUE')
        result[ident] = (ordinal, row)
    return result


def source_value(index, field, phase, role):
    ident = (field, phase, role)
    require(ident in index, 'EMITTED_VALUE_SOURCE_MISSING_' + ':'.join(ident))
    ordinal, row = index[ident]
    return deepcopy(row['actual_value']), {'file': AUDIT_PIN['path'], 'pointer': f'/required_rows/{ordinal}/actual_value', 'classification': row['classification'], 'key': list(ident)}


def typed_scalar(value, kind):
    require(type(value) is dict and value.get('type') == kind, 'TYPED_' + kind)
    if kind == 'null':
        require(set(value) == {'type'}, 'TYPED_NULL_FIELDS')
        return None
    if kind == 'float':
        require(set(value) == {'type', 'binary64_be'} and type(value['binary64_be']) is str and re.fullmatch('[0-9a-f]{16}', value['binary64_be']), 'TYPED_FLOAT_BITS')
        result = struct.unpack('>d', bytes.fromhex(value['binary64_be']))[0]
        require(math.isfinite(result), 'TYPED_FLOAT_FINITE')
        return result
    if kind == 'int':
        require(set(value) == {'type', 'decimal'} and type(value['decimal']) is str and re.fullmatch('-?(0|[1-9][0-9]*)', value['decimal']), 'TYPED_INTEGER')
        result = int(value['decimal'])
        require(str(result) == value['decimal'], 'TYPED_INTEGER_CANONICAL')
        return result
    require(kind == 'bool' and set(value) == {'type', 'value'} and type(value['value']) is bool, 'TYPED_BOOL')
    return value['value']


def one(rows, site, edge):
    found = [r for r in rows if r.get('site') == site and r.get('edge') == edge]
    require(len(found) == 1, 'UNIQUE_SOURCE_' + site + ':' + edge)
    return found[0]


def model_role(role):
    require(type(role) is str, 'MODEL_ROLE_TYPE')
    if role.startswith('buff:'):
        parts = role.split(':')
        require(len(parts) == 3 and parts[1] in ('P', 'O') and parts[2] in {str(n) for n in STACK_NAMES}, 'MODEL_BUFF_ROLE')
        return 'buff:' + parts[1] + ':' + STACK_NAMES[int(parts[2])]
    return role


def project_order(entry, aliases):
    args = native_schema.argument_fields(entry['payload']['arguments'])
    require('items' in args and args['items'].get('type') == 'array', 'GAME_ITEMS_ARGUMENT')
    order = []
    for ref in args['items']['values']:
        native_schema.validate_typed(ref)
        require(ref.get('type') == 'native_ref', 'GAME_ITEM_REFERENCE')
        role = aliases['native_to_role'].get(ref.get('native_id'))
        require(role in native_schema.FIXED_ROLES and ref.get('role') == role and aliases['role_to_native'].get(role) == ref['native_id'], 'GAME_ITEM_ALIAS')
        order.append(role)
    require(len(order) == len(set(order)) == 39 and set(order) == native_schema.FIXED_ROLES, 'GAME_ORDER39')
    return order


def project_fixture(decoded):
    fixture = deepcopy(native_schema.FIXED_FIXTURE)
    for side, name in (('P', 'player_fixture.json'), ('O', 'fixture.json')):
        raw = decoded[name]
        expected = fixture['sides'][0 if side == 'P' else 1]
        native_schema.exact(raw, ('schema_version', 'game_version', 'class', 'health', 'stamina', 'items'))
        require(type(raw['schema_version']) is int and raw['schema_version'] == 1 and raw['game_version'] == '1.1.8' and type(raw['class']) is int and raw['class'] == 0, 'FIXED_FIXTURE_CLASS_VERSION')
        for source, target in (('health', 'hp'), ('stamina', 'stamina')):
            value = raw[source]
            require(type(value) in (int, float) and math.isfinite(value) and value == expected[target], 'FIXED_FIXTURE_RESOURCE')
        items = [{k: v for k, v in row.items() if k != 'instance_id'} for row in expected['items']]
        require(same(raw['items'], items), 'FIXED_FIXTURE_GEOMETRY_ORDER')
    return fixture


def project_runtime(decoded, aliases, index):
    inputs = decoded['observer7-input.jsonl']
    pre = one(inputs, 'Core/Game.gd::prepareItems', 'checkpoint')
    act = one(inputs, 'Core/Game.gd::activateItems', 'checkpoint')
    pe = one(inputs, 'Core/Game.gd::prepareItems', 'enter')
    ae = one(inputs, 'Core/Game.gd::activateItems', 'enter')
    for checkpoint, entry in ((pre, pe), (act, ae)):
        require(checkpoint['sequence'] + 1 == entry['sequence'], 'CHECKPOINT_ENTRY_ADJACENCY')
        require(all(same(checkpoint['stamp'][k], entry['stamp'][k]) for k in ('physics_frame', 'idle_frame', 'util_time', 'combat_time')), 'CHECKPOINT_ENTRY_CLOCK')
    prepare, activate = project_order(pe, aliases), project_order(ae, aliases)
    require(prepare == activate, 'FIXED_A_PREPARE_ACTIVATE_ORDER')
    header = deepcopy(decoded['king-clock-checkpoint.json'])
    frame_clock = dict(header, passes=deepcopy(decoded['king-clock-passes.jsonl']))
    clock = native_schema.decode_clock(frame_clock)
    require(ae['stamp']['phase'] == 'Core/Game.gd::activateItems:enter' and ae['stamp']['combat_time'] == {'type': 'float', 'binary64_be': ZERO_BITS}, 'ACTIVATION_PHASE_COMBAT_CLOCK')
    require(ae['stamp']['util_time']['binary64_be'] == header['checkpoint']['util_time_bits'] and native_schema.decimal(ae['stamp']['physics_frame']) == clock.physics_frame and native_schema.decimal(ae['stamp']['idle_frame']) == clock.idle_frame, 'ACTIVATION_HEADER_JOIN')
    env = act['payload']['environment']
    environment = {'fps': typed_scalar(env['fps'], 'int'), 'scale': typed_scalar(env['scale'], 'float'), 'paused': typed_scalar(env['paused'], 'bool')}
    require(type(environment['fps']) is int and environment['fps'] == 60 and environment['scale'] == 1.0 and environment['paused'] is False, 'FIXED_ACTIVATION_ENVIRONMENT')
    processing, nodes, timers, origins = [], [], {}, {}
    raw_nodes = {row['role']: row for row in act['payload']['nodes']}
    require(len(raw_nodes) == len(act['payload']['nodes']), 'RAW_NODE_ROLE_DUPLICATE')
    expected_timers = {role for field, phase, role in index if field == 'Timer.private_left' and phase == 'pre_activate'}
    expected_ordinary = {'root_viewport', 'game', 'util', 'combat_timer', 'character:P', 'character:O'} | {'item:' + role for role in native_schema.FIXED_ROLES}
    require(set(raw_nodes) - EXCLUDED_TIMERS == expected_timers | expected_ordinary, 'EXACT_EMITTED_BUSINESS_NODE_ROLES')
    emitted_native_ids = set()
    for raw_role, wrapper in raw_nodes.items():
        if raw_role in EXCLUDED_TIMERS:
            continue
        role = model_role(raw_role)
        node = deepcopy(wrapper['node'])
        inner_role = raw_role.split(':', 1)[1] if raw_role.startswith(('item:', 'character:')) else raw_role
        require(node.get('role') == inner_role and aliases['role_to_native'].get(inner_role) == node.get('native_id') and aliases['native_to_role'].get(node.get('native_id')) == inner_role, 'EMITTED_NODE_NATIVE_ALIAS')
        require(type(node.get('native_id')) is str and node['native_id'] not in emitted_native_ids, 'EMITTED_NODE_NATIVE_BIJECTION')
        emitted_native_ids.add(node['native_id'])
        require(type(node.get('path')) is str and type(node.get('priority')) is int and type(node.get('positions')) is list and all(type(x) is int for x in node['positions']), 'EMITTED_NODE_SCALARS')
        for flag in ('ordinary_physics', 'internal_physics', 'ordinary_idle', 'internal_idle', 'inside_tree'):
            require(type(node.get(flag)) is bool, 'EMITTED_NODE_BOOL_' + flag)
        node['role'] = role
        processing.append(node)
        origins['processing_nodes.' + role] = {'file': 'observer7-input.jsonl', 'sequence': act['sequence'], 'raw_role': raw_role}
        timer = wrapper['timer']
        if role != 'root_viewport':
            nodes.append({k: deepcopy(node[k]) for k in ('role', 'path', 'positions', 'priority')} | {'kind': 'timer' if timer is not None else 'ordinary'})
        if timer is None:
            continue
        require(same(timer['node'], wrapper['node']), 'TIMER_NODE_ALIAS')
        identity, identity_origin = source_value(index, 'Timer.node.native_id', 'pre_activate', raw_role)
        require(identity == wrapper['node']['native_id'], 'TIMER_ACCEPTED_AUDIT_NATIVE_ID')
        origins['timer_initial.' + role + '.native_identity'] = identity_origin
        values = {}
        for raw_field, output_field in (('wait_time', 'wait_time_bits'), ('one_shot', 'one_shot'), ('process_mode', 'process_mode'), ('autostart', 'autostart'), ('paused', 'paused')):
            actual, origin = source_value(index, 'Timer.' + raw_field, 'pre_activate', raw_role)
            require(same(actual, timer[raw_field]), 'TIMER_ACTUAL_AUDIT_JOIN_' + raw_role + ':' + raw_field)
            if raw_field == 'wait_time':
                require(typed_scalar(actual, 'float') > 0, 'TIMER_WAIT_POSITIVE')
                values[output_field] = actual['binary64_be']
            else:
                require(type(actual) is (int if raw_field == 'process_mode' else bool), 'TIMER_SCALAR_TYPE')
                values[output_field] = actual
            origins['timer_initial.' + role + '.' + output_field] = origin
        private, origin = source_value(index, 'Timer.private_left', 'pre_activate', raw_role)
        require(typed_scalar(private, 'float') == -1.0, 'SUPPORTED_PRIVATE_INITIAL_MINUS_ONE')
        values['private_left_bits'] = private['binary64_be']
        origins['timer_initial.' + role + '.private_left_bits'] = origin
        timers[role] = values
    require(len(timers) == 33 and len({n['role'] for n in processing}) == len(processing), 'BUSINESS_TIMER_OR_NODE_COUNT')
    for side, child in (('P', 7), ('O', 5)):
        invu, parent = raw_nodes['invu:' + side]['node'], raw_nodes['character:' + side]['node']
        require(invu['positions'] == parent['positions'] + [child] and invu['path'] == parent['path'] + '/InvulnerabilityTimer', 'ACTUAL_P7_O5_TOPOLOGY')
    characters = {}
    for side in ('P', 'O'):
        values = {}
        for name, kind in (('invulnerable', 'bool'), ('invulnerabilityItem', 'null'), ('buffProtectStacks', 'int')):
            actual, origin = source_value(index, 'Character.' + name, 'pre_activate', side)
            values[name] = typed_scalar(actual, kind)
            origins['initial_characters.' + side + '.' + name] = origin
        characters[side] = values
    initial = {}
    for row in pre['payload']['items']:
        identity, fields = row['instance'], row['fields']
        require(identity in native_schema.FIXED_ROLES and identity not in initial, 'INITIAL_ITEM_IDENTITY')
        value = {}
        for raw_field, output in (('lastActivationTime', 'lastActivationTime_bits'), ('lastTriggerTime', 'lastTriggerTime_bits')):
            require(typed_scalar(fields[raw_field], 'float') == 0.0 and fields[raw_field]['binary64_be'] == ZERO_BITS, 'EMITTED_INITIAL_LIMITER_ZERO')
            value[output] = fields[raw_field]['binary64_be']
        for name in ('activationsThisFrame', 'triggersThisFrame'):
            value[name] = typed_scalar(fields[name], 'int')
            require(value[name] == 0, 'EMITTED_INITIAL_COUNTER_ZERO')
        for name in ('dragged', 'moveback_running'):
            value[name] = typed_scalar(row[name], 'bool')
            require(value[name] is False, 'EMITTED_INITIAL_DRAG_TWEEN')
        require(same(row['cachedAffectedItems'], {'type': 'dictionary', 'entries': []}), 'EMITTED_UNPREPARED_EMPTY_CACHE')
        value['cache_fresh'] = True  # Exactly the observed empty-pre-cache predicate, not all constructor equivalence.
        initial[identity] = value
        origins['initial_items.' + identity] = {'file': 'observer7-input.jsonl', 'sequence': pre['sequence'], 'instance': identity, 'predicate': 'emitted limiter scalars and actual empty pre-cache only'}
    require(set(initial) == native_schema.FIXED_ROLES, 'INITIAL_ITEMS_COMPLETE39')
    runtime = dict(schema=RUNTIME_SCHEMA, mode='genuine', profile_id=PROFILE,
                   checkpoint={'util_time_bits': ae['stamp']['util_time']['binary64_be'], 'combat_time_bits': ae['stamp']['combat_time']['binary64_be'], 'source_phase': ae['stamp']['phase']},
                   environment=environment, nodes=nodes, timer_initial=timers, initial_items=initial,
                   initial_characters=characters, prepare_order=prepare, activate_order=activate,
                   terminal_profile='source-two-physics-idle-pre-internal/1', frame_clock=frame_clock, processing_nodes=processing)
    require(set(runtime) == set(RUNTIME_KEYS), 'RUNTIME14_KEYS')
    for field in ('schema', 'mode', 'profile_id', 'terminal_profile'):
        origins['runtime.' + field] = {'source': 'data/phase441-fixed-A-input-source/abi.json', 'predicate': 'immutable input-only ABI declaration; not runtime acceptance'}
    for field in ('checkpoint', 'environment', 'nodes', 'processing_nodes'):
        origins['runtime.' + field] = {'file': 'observer7-input.jsonl', 'sequence': ae['sequence'] if field == 'checkpoint' else act['sequence'], 'predicate': 'actual activation field projection with role normalization and two UI Timer exclusions'}
    origins['runtime.frame_clock'] = {'files': ['king-clock-checkpoint.json', 'king-clock-passes.jsonl'], 'predicate': 'complete original header/pass sequence; typed clock decode'}
    for field, entry in (('prepare_order', pe), ('activate_order', ae)):
        origins['runtime.' + field] = {'file': 'observer7-input.jsonl', 'sequence': entry['sequence'], 'pointer': '/payload/arguments', 'predicate': 'actual39 native/role relation'}
    for field in ('timer_initial', 'initial_characters'):
        origins['runtime.' + field] = {'file': AUDIT_PIN['path'], 'predicate': 'accepted actual values joined to the same fixed INPUT bytes; individual field refs supplied'}
    origins['runtime.initial_items'] = {'file': 'observer7-input.jsonl', 'sequence': pre['sequence'], 'pointer': '/payload/items', 'predicate': 'only emitted pre-prepare limiter/cache predicates; not complete constructor proof'}
    return runtime, origins, ae['sequence']


def project_primitives(decoded, activation_sequence):
    draws, sequences = [], []
    for row in decoded['observer7-primitives.jsonl']:
        require(type(row.get('sequence')) is int and row['sequence'] > activation_sequence, 'SELECTED_PRIMITIVE_NOT_AFTER_ACTIVATION')
        value = row['payload']
        kind = value['kind']
        projected = {'kind': kind, 'label': value['label']}
        require(type(projected['label']) is str and projected['label'], 'PRIMITIVE_LABEL')
        if kind in ('randf', 'randf_range'):
            args = []
            for arg in value['args']:
                if arg.get('type') == 'float':
                    typed_scalar(arg, 'float')
                    args.append(arg['binary64_be'])
                elif row['site'] == 'Utility/Util.gd::roll' and same(arg, {'type': 'int', 'decimal': '0'}):
                    args.append(ZERO_BITS)
                else:
                    raise Rejected('UNSUPPORTED_PRIMITIVE_ARGUMENT_COERCION')
            require(len(args) == (0 if kind == 'randf' else 2), 'PRIMITIVE_FLOAT_ARITY')
            result = typed_scalar(value['value'], 'float')
            floats = [struct.unpack('>d', bytes.fromhex(b))[0] for b in args]
            low, high = (0.0, 1.0) if not floats else (min(floats), max(floats))
            require(low <= result <= high, 'PRIMITIVE_FLOAT_BOUNDS')
            projected.update(args=args, value_bits=value['value']['binary64_be'])
        elif kind == 'randi_range':
            args = [typed_scalar(a, 'int') for a in value['args']]
            result = typed_scalar(value['value'], 'int')
            require(len(args) == 2 and all(-(1 << 31) <= a < (1 << 31) for a in args) and min(args) <= result <= max(args), 'PRIMITIVE_INTEGER_BOUNDS')
            projected.update(args=args, value=result)
        else:
            raise Rejected('UNKNOWN_OR_GLOBAL_PRIMITIVE')
        draws.append(projected)
        sequences.append(row['sequence'])
    require(sequences == sorted(sequences) and len(sequences) == len(set(sequences)), 'PRIMITIVE_PHYSICAL_ORDER')
    return draws, sequences


def validate_initial_consumer_coverage(bundle, origins):
    require(set(bundle) == {'schema', 'fixture', 'runtime', 'draws', 'synthetic_seed'} and bundle['schema'] == 'native-v8-input-only/1' and bundle['synthetic_seed'] is None, 'INPUT_ONLY_ENVELOPE')
    runtime = bundle['runtime']
    require(set(runtime) == set(RUNTIME_KEYS) and runtime['schema'] == RUNTIME_SCHEMA and runtime['profile_id'] == PROFILE, 'INPUT_ONLY_RUNTIME_ABI')
    require(len(runtime['timer_initial']) == 33 and len(runtime['initial_items']) == 39 and set(runtime['initial_characters']) == {'P', 'O'}, 'EMITTED_MEMBERSHIP')
    for field in bundle:
        require('bundle.' + field in origins, 'MISSING_BUNDLE_FIELD_ORIGIN_' + field)
    for field in runtime:
        require('runtime.' + field in origins, 'MISSING_RUNTIME_FIELD_ORIGIN_' + field)
    require(not any(n['role'] in EXCLUDED_TIMERS for n in runtime['processing_nodes']), 'EXCLUDED_UI_TIMER_EMITTED')
    for role in runtime['timer_initial']:
        for field in runtime['timer_initial'][role]:
            require('timer_initial.' + role + '.' + field in origins, 'MISSING_TIMER_FIELD_ORIGIN')
    for side in ('P', 'O'):
        for field in runtime['initial_characters'][side]:
            require('initial_characters.' + side + '.' + field in origins, 'MISSING_CHARACTER_FIELD_ORIGIN')
    return {'status': STATUS, 'emitted_fields_have_declared_sources': True,
            'future_model_blockers': list(DEFERRED), 'runtime_validated': False,
            'candidate_or_comparator_bound': False, 'model_release': False}


def project_decoded(decoded, aliases, index):
    """Pure business-field projection; no raw identity gate or runtime admission."""
    fixture = project_fixture(decoded)
    runtime, origins, activation_sequence = project_runtime(decoded, aliases, index)
    draws, sequences = project_primitives(decoded, activation_sequence)
    bundle = {'schema': 'native-v8-input-only/1', 'fixture': fixture, 'runtime': runtime, 'draws': draws, 'synthetic_seed': None}
    origins.update({'bundle.schema': {'source': 'data/phase441-fixed-A-input-source/abi.json', 'predicate': 'fixed five-key input envelope'},
                    'bundle.fixture': {'files': ['fixture.json', 'player_fixture.json', 'king-slot-bindings.json'], 'predicate': 'fixed Source fixture plus actual resources/geometry/order relation'},
                    'bundle.runtime': {'source': 'data/phase441-fixed-A-input-source/abi.json', 'predicate': 'exact14 declared INPUT-only fields; individual field refs supplied'},
                    'bundle.draws': {'file': 'observer7-primitives.jsonl', 'sequences': sequences, 'predicate': 'all selected actual records, strict activation boundary and physical order'},
                    'bundle.synthetic_seed': {'source': 'data/phase441-fixed-A-input-source/abi.json', 'predicate': 'null for conditional direct-native primitive Tape; no seed restoration'}})
    coverage = validate_initial_consumer_coverage(bundle, origins)
    return bundle, {'schema': 'phase441-input-only-projection-proof/1', 'status': STATUS,
                    'field_origins': origins, 'primitive_original_sequences': sequences,
                    'coverage': coverage, 'presentation_semantics': '116 excluded fields are not runtime/initial acceptance predicates',
                    'clock_and_tape': 'complete original physical selected streams; no posthoc terminal filtering',
                    'timer_origin': 'accepted SOURCE-supported initial values; never fresh_configured or public-zero inference'}


def project_from_bytes(raw12, audit_raw):
    """Pure fixed-byte entry; all physical filesystem/receipt controls are separate."""
    decoded, aliases, validation = decode_lawful12(raw12)
    index = load_accepted_initial(audit_raw)
    bundle, proof = project_decoded(decoded, aliases, index)
    proof['fixed_input_validation'] = validation
    proof['accepted_initial_audit'] = deepcopy(AUDIT_PIN)
    return bundle, proof


def verify_source_context(context, io):
    require(type(context) is dict and context.get('schema') == 'phase441-fixed-source-context/1', 'SOURCE_CONTEXT_SCHEMA')
    require(same(context.get('input_descriptors'), INPUT_PINS) and same(context.get('audit'), AUDIT_PIN), 'SOURCE_FIXED_INPUT_BINDING')
    require(same(context.get('schema_module'), SCHEMA_PIN), 'SOURCE_SCHEMA_BINDING')
    require(Path(native_schema.__file__).absolute() == canonical(SCHEMA_PIN['path']), 'IMPORTED_SCHEMA_PATH')
    seen = set()
    for pin in context['source_pins']:
        path = str(canonical(pin['path']))
        require(path not in seen, 'SOURCE_PIN_DUPLICATE')
        seen.add(path)
        read_pinned(pin, io)
    abi = strict_json(read_pinned(context['abi'], io))
    require(abi.get('status') == STATUS and abi.get('runtime_schema') == RUNTIME_SCHEMA and abi.get('projection_profile') == PROFILE and same(abi.get('runtime_keys'), list(RUNTIME_KEYS)) and abi.get('business_timer_count') == 33, 'IMMUTABLE441_ABI')
    receipts = {name: strict_json(read_pinned(pin, io)) for name, pin in context['receipts'].items()}
    accepted = receipts['root439']
    require(accepted.get('status') == 'ACCEPTED_ACTUAL64_SOURCE_DERIVED_FIXED_INPUT_DOMAIN' and same(accepted.get('actual_overlay'), AUDIT_PIN) and same(accepted.get('after'), {'DIRECT': 1289, 'SOURCE_DERIVED': 74, 'MISSING': 0}), 'ACTUAL439_ACCEPTANCE')
    require(same(accepted.get('independent_seal'), context['receipts']['independent439']), '439_INDEPENDENT_SEAL_BINDING')
    require(receipts['root440'].get('status') == 'ACCEPTED_INPUT_ONLY_IMPLEMENTATION_DIRECTION' and receipts['root440'].get('model_release') is False, '440_ROOT_INPUT_ONLY_DIRECTION')
    require(receipts['independent440'].get('status') == 'DESIGN_ACCEPTED_FOR_MINIMAL441_INPUT_ONLY_IMPLEMENTATION', '440_INDEPENDENT_DIRECTION')
    require(receipts['root402'].get('status') == 'ROOT_ACCEPTS_FIXED06_BOUNDED_TERMINAL_SOURCE_PROCESS_CONTROLS', 'FIXED401_402_CONTROL_ACCEPTANCE')
    return {'source_context': deepcopy(CONTEXT), 'abi': deepcopy(context['abi']),
            'receipts': deepcopy(context['receipts']), 'model_release': False,
            'native_profile': 'observer7-390-native-single-king-A/1',
            'projection_profile': PROFILE, 'status': STATUS}


def build_from_files(output_new):
    """One explicit file build; Source/controls must be accepted externally first."""
    output = canonical(output_new)
    require(output.is_relative_to(REPO / 'data') and output != REPO / 'data', 'OUTPUT_DOMAIN')
    physical(output.parent, False)
    require(not os.path.lexists(output), 'OUTPUT_EXISTS')
    source_io, input_io, owned = [], [], []
    context = strict_json(read_pinned(CONTEXT, source_io))
    source = verify_source_context(context, source_io)
    output.mkdir(mode=0o700)
    try:
        raw12 = {name: read_pinned(pin, input_io) for name, pin in INPUT_PINS.items()}
        audit_raw = read_pinned(AUDIT_PIN, input_io)
        bundle, proof = project_from_bytes(raw12, audit_raw)
        proof['source_authority'] = source
        source_after, input_after = [], []
        for pin in source_io:
            read_pinned(pin, source_after)
        for pin in input_io:
            read_pinned(pin, input_after)
        require(same(source_io, source_after) and same(input_io, input_after), 'BUILD_SOURCE_INPUT_READBACK')
        owned.append(save_new(output / 'input-bundle.json', bundle))
        owned.append(save_new(output / 'input-proof.json', proof))
        owned.append(save_new(output / 'inputs-before-interpretation.json', {'source_files': source_io, 'input_payload_files': input_io, 'raw_inputs': deepcopy(INPUT_PINS), 'accepted_initial_audit': deepcopy(AUDIT_PIN)}))
        owned.append(save_new(output / 'input-readback.json', {'source_before': source_io, 'source_after': source_after, 'input_before': input_io, 'input_after': input_after, 'unchanged': True, 'whole_files_read_and_hashed': True, 'lawful_carriers_syntax_decoded': 12, 'EXPECTED_file_reads': 0, 'postcleanup_records_used_as_input': 0}))
        seal = {'schema': 'phase441-joint-input-only-seal/1', 'status': STATUS, 'files': deepcopy(owned),
                'source_context': deepcopy(CONTEXT), 'abi': deepcopy(context['abi']),
                'runtime_validated': False, 'model_release': False, 'King_admitted': False,
                'future_model_blockers': list(DEFERRED)}
        owned.append(save_new(output / 'input-joint-seal.json', seal))
        save_new(output / 'owned-files.json', {'schema': 'phase441-input-only-output-owner/1', 'files': owned, 'status': STATUS, 'independent_input_acceptance': 'PENDING'})
    except Exception as error:
        if not os.path.lexists(output / 'first-error.json'):
            save_new(output / 'first-error.json', {'error': type(error).__name__, 'reason': str(error)[:2000], 'source_reads_completed': source_io, 'input_reads_completed': input_io, 'preserved_outputs': owned, 'automatic_retry': False, 'runtime_validated': False})
        raise
    return {'output': str(output), 'status': STATUS, 'input_bundle_created': True, 'runtime_validated': False, 'model_runs': 0}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-new', required=True)
    args = parser.parse_args(argv)
    print(json.dumps(build_from_files(args.output_new), sort_keys=True))


if __name__ == '__main__':
    main()
