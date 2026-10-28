"""Fixed-case64 Timer Source overlay. Author must not import or run this module."""
import argparse
from copy import deepcopy
import hashlib
import json
import math
import os
from pathlib import Path
import re
import stat

REPO = Path('/workspace/python-original-engine/repo')
BASE = Path('/workspace/godotsteam-startup-20261013/baseline/Backpack Battles')
CONTEXT = {'path': 'data/phase439-timer-overlay-source/context.json', 'size': 212241, 'sha256': '962aab0cd096fe0c43c6547690763ca7befeb786848be3e3e7687e669f8ada93'}
CONTEXT_CANONICAL_SHA256 = 'd8460942df09d733077786e0e76a737a46675d165a48fea21278479344ee6729'
AUDIT_CANONICAL_SHA256 = '370ca835fbc95ba5939d0a42f35b1c2d0c33e2e855b94efc0c1df6d3085f5078'
RECEIVERS_CANONICAL_SHA256 = '877bf8fe7fd7b2e092c9fe0b74103beb7fbf53f0f8400d283fb801567728c974'
RULE = 'NATIVE_TIMER_NONPAUSED_INACTIVE_FLAGS_STANDARD_DOMAIN/439'
PHASES = ('pre_prepare', 'pre_activate')
ROLES = (('tick:P', 'tick:O') + tuple(f'buff:{side}:{category}' for side in ('P', 'O') for category in range(100, 111)) + ('fatigue:start', 'fatigue:tick') + tuple(f'aux:{side}:{name}' for side in ('P', 'O') for name in ('battleRageTimer', 'autoRageTimer')) + ('invu:P', 'invu:O'))
TARGETS = frozenset(('Timer.private_left', phase, role) for phase in PHASES for role in ROLES)
PUBLIC_FIELDS = ('process_mode', 'wait_time', 'time_left', 'one_shot', 'autostart', 'paused', 'stopped', 'node.native_id', 'node.role', 'node.path', 'node.name', 'node.class', 'node.positions', 'node.priority', 'node.inside_tree', 'node.ordinary_physics', 'node.internal_physics', 'node.ordinary_idle', 'node.internal_idle')
PRIVATE_MINUS_ONE = {'type': 'float', 'binary64_be': 'bff0000000000000'}
PREMISES = (
    'Version-attributed Timer/Node/Object native semantics under accepted419/425 G02 ordinary registered builtin runtime domain; no custom binary reproduction claim.',
    'Plain native Timer.new or exact native Timer scene receivers; no target script/getter shadow or foreign native/editor registrar.',
    'Completed serialized native-operation cuts; ordinary timeout nesting is allowed, internal setter receptor reentry is outside the accepted domain.',
    'Pinned project and active observer/collector writer domain contains only valid Timer mode history0/1 and no external inherited internal-flag writes on these receivers.',
    'Actual same-cut paused/internal_idle/internal_physics are strictly bool false and current process_mode is strictly int0; IDs/roles/parents are bound to actual required INPUT.',
    'Kernel induction yields processing=false then private_left=-1. Public time_left0/stoppedtrue are consistency fields, not proof premises.',
)
LIMIT = 'Reuses the historical815-script public-redaction/migration Source domain; no new environment-ready, arbitrary native-hook safety, custom-binary equality, fullschema, input-build or King admission.'


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


def validate_source(context, io):
    require(fingerprint(context) == CONTEXT_CANONICAL_SHA256, 'FIXED_SOURCE_CONTEXT')
    require(context['schema'] == 'phase439-timer-source-context/1' and same(context['premises'], list(PREMISES)), 'SOURCE_SCHEMA_RULE')
    require(len(context['project_scripts']) == 815 and len(context['scene_dependencies']) == 19, 'SOURCE_DOMAIN_COUNTS')
    require(fingerprint(context['receivers']) == RECEIVERS_CANONICAL_SHA256, 'RECEIVER_SOURCE_DOMAIN')
    seen = set()
    for group in ('project_scripts', 'scene_dependencies', 'other_source'):
        for pin in context[group]:
            name = str(canonical(pin['path']))
            require(name not in seen, 'SOURCE_DUPLICATE')
            seen.add(name)
            read_pinned(pin, io)
    require({str(p) for p in BASE.rglob('*.gd')} == {str(canonical(p['path'])) for p in context['project_scripts']}, 'SOURCE_SCRIPT_SET_DRIFT')
    receipts = {name: strict_json(read_pinned(pin, io)) for name, pin in context['receipts'].items()}
    root = receipts['root438']
    require(root.get('schema') == 'phase438-root-character8-acceptance/1' and root.get('status') == 'ACCEPTED_ACTUAL8_NEW_SOURCE_DERIVED', 'ROOT438_ACCEPTANCE')
    require(same(root.get('actual_overlay'), context['inputs']['audit']) and same(root.get('after'), {'DIRECT': 1289, 'SOURCE_DERIVED': 10, 'MISSING': 64}), 'ROOT438_ACTUAL_INPUT')
    require(root.get('remaining64') == 'NativeTimerconditionalruleG02accepted;actualbinding/adapter/independentcontrols stillpending', 'ROOT438_NATIVE_DISPOSITION')
    require(same(root.get('independent_seal'), context['receipts']['independent438']), 'ROOT438_INDEPENDENT_SEAL')
    require(receipts['kernel']['conditional_conclusion'] == 'nonpaused && both_internal_flags_false => private_left == -1', 'KERNEL_CONCLUSION')
    # Concrete fixed source/receipt identities, not caller-supplied approval flags.
    return {'context_descriptor': deepcopy(CONTEXT), 'rule': RULE, 'premises': list(PREMISES),
            'native_source_and_receipt_descriptors': deepcopy(context['receipts']),
            'receiver_manifest': deepcopy(context['receivers']), 'source_domain': {'scripts': 815, 'inherited_scenes': 19, 'additional_source': deepcopy(context['other_source'])},
            'attribution_limit': LIMIT}


def validate_audit(audit):
    require(type(audit) is dict and audit.get('profile') == 'pure-combat-initial-fixed-king-A/437' and audit.get('schema') == 'phase438-character-combat-initial-overlay/1', 'AUDIT_IDENTITY')
    require(same(audit.get('counts'), {'DIRECT': 1289, 'SOURCE_DERIVED': 10, 'MISSING': 64}), 'AUDIT_COUNTS')
    rows, excluded = audit.get('required_rows'), audit.get('excluded_presentation')
    require(type(rows) is list and len(rows) == 1363 and type(excluded) is list and len(excluded) == 116, 'AUDIT_ARRAY_COUNTS')
    require(audit.get('King_admitted') is False and audit.get('fullschema') == 'NOT_VALIDATED', 'AUDIT_ADMISSION')
    found, missing, counts = {}, set(), {'DIRECT': 0, 'SOURCE_DERIVED': 0, 'MISSING': 0}
    for ordinal, row in enumerate(rows):
        ident = key(row)
        require(ident not in found, 'AUDIT_DUPLICATE')
        found[ident] = ordinal
        kind = row.get('classification')
        if kind == 'MISSING':
            require(row.get('proof_complete') is False and row.get('validation_result') == 'UNPROVEN' and 'actual_value' not in row, 'AUDIT_MISSING_SHAPE')
            missing.add(ident)
            counts['MISSING'] += 1
        else:
            require(kind in ('DIRECT_OBSERVATION', 'SOURCE_DERIVED') and row.get('proof_complete') is True and row.get('validation_result') == 'SUPPORTED' and 'actual_value' in row, 'AUDIT_SUPPORTED_SHAPE')
            counts['DIRECT' if kind == 'DIRECT_OBSERVATION' else 'SOURCE_DERIVED'] += 1
    require(missing == TARGETS and same(counts, audit['counts']), 'AUDIT_EXACT64_GAPS')
    require(fingerprint(audit) == AUDIT_CANONICAL_SHA256, 'AUDIT_FIXED_CANONICAL_FINGERPRINT')
    return found


def node_index(nodes):
    require(type(nodes) is list, 'CUT_NODES')
    roles, native_ids = {}, set()
    for i, wrapper in enumerate(nodes):
        require(type(wrapper) is dict and type(wrapper.get('node')) is dict, 'NODE_WRAPPER')
        require(set(wrapper) == {'role', 'node', 'timer'}, 'NODE_WRAPPER_FIELDS')
        role, native = wrapper.get('role'), wrapper['node'].get('native_id')
        require(type(role) is str and role not in roles and type(native) is str and re.fullmatch('[1-9][0-9]*', native) and native not in native_ids, 'NODE_ID_ROLE_BIJECTION')
        roles[role] = (i, wrapper)
        native_ids.add(native)
    return roles


def field_value(timer, name):
    value = timer
    for part in name.split('.'):
        require(type(value) is dict and part in value, 'MISSING_PUBLIC_FIELD_' + name)
        value = value[part]
    return value


def validate_cuts(records, audit, receivers, ordinals):
    require(type(records) is list and len(records) == 2, 'CUT_COUNT')
    require(type(receivers) is list and fingerprint(receivers) == RECEIVERS_CANONICAL_SHA256, 'FIXED_RECEIVER_MANIFEST')
    require(len(receivers) == 32 and {r['role'] for r in receivers} == set(ROLES), 'RECEIVER_ROLES')
    environment = {'fps': {'type': 'int', 'decimal': '60'}, 'scale': {'type': 'float', 'binary64_be': '3ff0000000000000'}, 'paused': {'type': 'bool', 'value': False}}
    witnesses, prior_ids = [], None
    for phase, record, line, sequence, site, frames, util_time in zip(PHASES, records, (1, 4), (138, 1231), ('prepareItems', 'activateItems'), (('302', '38'), ('446', '56')), ('4014222233c00000', '401dbbbbd5c00000')):
        require(type(record) is dict and record.get('schema') == 'observer7-record/1' and record.get('channel') == 'input' and record.get('edge') == 'checkpoint', 'CUT_RECORD')
        require(set(record) == {'schema', 'sequence', 'channel', 'site', 'edge', 'subject', 'stamp', 'payload'}, 'CUT_RECORD_FIELDS')
        require(type(record.get('sequence')) is int and record['sequence'] == sequence and record.get('site') == 'Core/Game.gd::' + site, 'CUT_SITE_SEQUENCE')
        require(same(record.get('subject'), {'type': 'native_ref', 'native_id': '4015', 'role': 'game', 'class': 'Node2D'}), 'CUT_GAME')
        stamp, payload = record.get('stamp'), record.get('payload')
        require(type(stamp) is dict and type(payload) is dict and stamp.get('phase') == 'Core/Game.gd::' + site + ':enter', 'CUT_PHASE')
        require(set(stamp) == {'physics_frame', 'idle_frame', 'util_time', 'combat_time', 'phase'} and set(payload) == {'environment', 'nodes', 'items', 'source_resources'}, 'CUT_STAMP_PAYLOAD_FIELDS')
        require(type(stamp.get('physics_frame')) is str and stamp['physics_frame'] == frames[0] and type(stamp.get('idle_frame')) is str and stamp['idle_frame'] == frames[1], 'CUT_FRAMES')
        require(same(stamp.get('util_time'), {'type': 'float', 'binary64_be': util_time}) and same(stamp.get('combat_time'), {'type': 'float', 'binary64_be': '0000000000000000'}) and same(payload.get('environment'), environment), 'CUT_STAMP_ENVIRONMENT')
        nodes = node_index(payload.get('nodes'))
        resources = payload.get('source_resources')
        require(type(resources) is list and len(resources) == 2 and all(type(r) is dict for r in resources) and {r.get('side') for r in resources} == {'P', 'O'}, 'CUT_RESOURCES')
        current_ids = {}
        for receiver in receivers:
            role, native = receiver['role'], receiver['native_id']
            require(role in nodes and receiver['parent_role'] in nodes, 'RECEIVER_OR_PARENT_MISSING')
            ni, wrapper = nodes[role]
            _, parent_wrapper = nodes[receiver['parent_role']]
            parent, node, timer = parent_wrapper['node'], wrapper['node'], wrapper.get('timer')
            require(type(timer) is dict and same(node, timer.get('node')), 'TIMER_NODE_DUPLICATE_REPRESENTATION')
            require(set(timer) == {'node', 'process_mode', 'wait_time', 'time_left', 'one_shot', 'autostart', 'paused', 'stopped'}, 'TIMER_NATIVE_FIELDS')
            require(set(node) == {'native_id', 'role', 'path', 'name', 'class', 'positions', 'priority', 'inside_tree', 'ordinary_physics', 'internal_physics', 'ordinary_idle', 'internal_idle'}, 'TIMER_NODE_NATIVE_FIELDS')
            require(node.get('native_id') == native and node.get('role') == role and node.get('class') == 'Timer' and node.get('name') == receiver['name'] and node.get('path') == receiver['path'], 'RECEIVER_IDENTITY')
            require(parent.get('native_id') == receiver['parent_id'] and parent.get('path') == receiver['parent_path'] and node['path'] == parent['path'] + '/' + node['name'], 'RECEIVER_PARENT_ID_PATH')
            parent_role = receiver['parent_role'].removeprefix('character:')
            require(parent.get('class') == 'Node2D' and parent.get('role') == parent_role and parent.get('name') == receiver['parent_path'].rsplit('/', 1)[1] and parent.get('inside_tree') is True, 'RECEIVER_PARENT_CLASS_ROLE')
            require(type(node.get('positions')) is list and type(parent.get('positions')) is list and node['positions'][:-1] == parent['positions'], 'RECEIVER_PARENT_POSITIONS')
            require(all(type(x) is int for x in parent['positions'] + node['positions']), 'RECEIVER_POSITION_INTEGER_TYPES')
            require(type(timer.get('process_mode')) is int and timer['process_mode'] == 0, 'STRICT_NATIVE_MODE0')
            require(type(timer.get('paused')) is bool and timer['paused'] is False, 'STRICT_NONPAUSED')
            for name in ('internal_idle', 'internal_physics'):
                require(type(node.get(name)) is bool and node[name] is False, 'STRICT_INACTIVE_' + name)
            require(type(node.get('inside_tree')) is bool and node['inside_tree'] is True, 'STRICT_INSIDE_TREE')
            # Every19 public row/ref must equal its lawful raw INPUT value, not a fabricated summary.
            support_ordinals = []
            for name in PUBLIC_FIELDS:
                ident = ('Timer.' + name, phase, role)
                require(ident in ordinals, 'PUBLIC_ROW_MISSING')
                ordinal = ordinals[ident]
                row = audit['required_rows'][ordinal]
                require(row.get('classification') == 'DIRECT_OBSERVATION' and row.get('proof_complete') is True and row.get('validation_result') == 'SUPPORTED', 'PUBLIC_DIRECT_REQUIRED')
                require(same(row.get('actual_value'), field_value(timer, name)), 'PUBLIC_ACTUAL_VALUE_DISAGREEMENT')
                ref = {'file': 'observer7-input.jsonl', 'line': line, 'sequence': sequence, 'native_owner': native, 'pointer': '/payload/nodes/' + str(ni) + '/timer/' + name.replace('.', '/')}
                require(same(row.get('input_refs'), [ref]), 'PUBLIC_ACTUAL_REFERENCE_DISAGREEMENT')
                support_ordinals.append(ordinal)
            input_refs = [{'file': 'observer7-input.jsonl', 'line': line, 'sequence': sequence, 'native_owner': native, 'pointer': '/payload/nodes/' + str(ni) + '/timer'}]
            if role.startswith('buff:'):
                _, side, category = role.split(':')
                matches = [(i, r) for i, r in enumerate(resources) if r['side'] == side]
                require(len(matches) == 1, 'BUFF_RESOURCE_SIDE')
                si, resource = matches[0]
                require(resource.get('native_id') == parent['native_id'], 'BUFF_RESOURCE_PARENT')
                buffs = resource.get('buffs')
                require(type(buffs) is list and len(buffs) == 11 and all(type(b) is dict for b in buffs), 'BUFF_RESOURCE_COUNT')
                expected_stacks = [{'type': 'int', 'decimal': str(c)} for c in range(100, 111)]
                require(same([b.get('stack') for b in buffs], expected_stacks), 'BUFF_STACK_TYPES_ORDER')
                bi, buff = next((i, b) for i, b in enumerate(buffs) if same(b['stack'], {'type': 'int', 'decimal': category}))
                state = buff.get('state')
                require(type(state) is dict and same(state.get('type'), buff['stack']) and same(state.get('character'), {'type': 'native_ref', 'native_id': parent['native_id'], 'role': side, 'class': 'Node2D'}), 'BUFF_TYPE_CHARACTER')
                require(same(state.get('timer'), timer), 'BUFF_TIMER_DUAL_REPRESENTATION')
                input_refs.append({'file': 'observer7-input.jsonl', 'line': line, 'sequence': sequence, 'native_owner': native, 'pointer': f'/payload/source_resources/{si}/buffs/{bi}/state/timer'})
            current_ids[role] = native
            witnesses.append({'key': ['Timer.private_left', phase, role], 'input_refs': input_refs,
                              'public_support_ordinals': support_ordinals,
                              'typed_witness': {'paused': timer['paused'], 'mode': timer['process_mode'], 'inside_tree': node['inside_tree'], 'internal_idle': node['internal_idle'], 'internal_physics': node['internal_physics']}})
        require(len(current_ids) == len(set(current_ids.values())) == 32, 'TARGET_TIMER_BIJECTION')
        require(prior_ids is None or current_ids == prior_ids, 'CROSS_CUT_IDENTITY_DRIFT')
        prior_ids = current_ids
    require(len(witnesses) == 64, 'WITNESS_COUNT')
    return witnesses


def project(audit, records, receivers):
    ordinals = validate_audit(audit)
    witnesses = validate_cuts(records, audit, receivers, ordinals)
    report, changes = deepcopy(audit), []
    for i, witness in enumerate(witnesses):
        ident = tuple(witness['key'])
        ordinal = ordinals[ident]
        row = report['required_rows'][ordinal]
        row.update(classification='SOURCE_DERIVED', validation_result='SUPPORTED', proof_complete=True,
                   actual_value=deepcopy(PRIVATE_MINUS_ONE), rule=RULE,
                   input_refs=deepcopy(witness['input_refs']),
                   source_derivation={'proof_file': 'proof-evidence.json', 'proof_index': i,
                                      'shared_source_context': '#/source_context',
                                      'typed_witness': deepcopy(witness['typed_witness'])})
        row.pop('reasons', None)
        changes.append(dict(required_ordinal=ordinal, **deepcopy(witness)))
    report.update(schema='phase439-timer-combat-initial-overlay/1', status='TIMER64_SOURCE_CANDIDATES_PENDING_INDEPENDENT_ACTUAL_ACCEPTANCE', counts={'DIRECT': 1289, 'SOURCE_DERIVED': 74, 'MISSING': 0}, phase439_rule=RULE, source_attribution_limit=LIMIT)
    require(same(report['excluded_presentation'], audit['excluded_presentation']) and same(report['full_reference_counts'], audit['full_reference_counts']), 'PRESENTATION_OR_HISTORICAL_REFERENCE_CHANGED')
    require([key(r) for r in report['required_rows']] == [key(r) for r in audit['required_rows']], 'ROW_ORDER_CHANGED')
    for before, after in zip(audit['required_rows'], report['required_rows']):
        if key(before) not in TARGETS:
            require(same(before, after), 'NON_TARGET_ROW_CHANGED')
    return report, {'schema': 'phase439-timer-proof/1', 'rule': RULE, 'changes': changes, 'candidate_count': 64,
                    'remaining_missing': 0, 'preserved_required_rows': 1299, 'preserved_prior_derived': 10,
                    'acceptance': 'INDEPENDENT_REVIEW_REQUIRED', 'King_admitted': False,
                    'fullschema': 'NOT_VALIDATED', 'input_builds': 0, 'models': 0, 'captures': 0}


def run(output_new):
    output = canonical(output_new)
    require(output.is_relative_to(REPO / 'data') and output != REPO / 'data', 'OUTPUT_DOMAIN')
    physical(output.parent, False)
    require(not os.path.lexists(output), 'OUTPUT_EXISTS')
    io = []
    context = strict_json(read_pinned(CONTEXT, io))
    shared = validate_source(context, io)
    inputs = {name: read_pinned(pin, io) for name, pin in context['inputs'].items()}
    lines = inputs['checkpoints'].splitlines()
    require(len(lines) == 6, 'INPUT_FILE_LINE_COUNT')
    records = [strict_json(lines[i]) for i in (0, 3)]
    report, proof = project(strict_json(inputs['audit']), records, context['receivers'])
    proof['source_context'] = shared
    proof['input_descriptors'] = deepcopy(context['inputs'])
    before, after = deepcopy(io), []
    for pin in before:
        read_pinned(pin, after)
    require(same(before, after), 'READBACK_ORDER_OR_PIN')
    output.mkdir(mode=0o700)
    owned = []
    try:
        owned.append(save_new(output / 'proof-evidence.json', proof))
        owned.append(save_new(output / 'overlay-report.json', report))
        owned.append(save_new(output / 'input-readback.json', {'before': before, 'after': after, 'unchanged': True,
                    'whole_files_hashed_before': len(before), 'whole_files_rehashed_after': len(after),
                    'whole_file_bytes_include_unparsed_records': True, 'parsed_checkpoint_lines': [1, 4],
                    'checkpoint_records_parsed': 2, 'postcleanup_records_parsed': 0, 'EXPECTED_file_reads': 0}))
        save_new(output / 'owned-files.json', {'schema': 'phase439-timer-overlay-owned/1', 'files': owned, 'independent_acceptance': 'PENDING'})
    except Exception as error:
        if not os.path.lexists(output / 'first-error.json'):
            save_new(output / 'first-error.json', {'error': type(error).__name__, 'reason': str(error)[:1000], 'preserved_outputs': owned})
        raise
    return {'output': str(output), 'new_candidates': 64, 'remaining_missing': 0, 'accepted': False, 'King_admitted': False}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-new', required=True)
    args = parser.parse_args(argv)
    print(json.dumps(run(args.output_new), sort_keys=True))


if __name__ == '__main__':
    main()
