"""Character8 saved overlay v2. Author must not import or run this module."""
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
CONTEXT = {'path': 'data/phase438-character-overlay-source-v2/context.json',
           'size': 193067, 'sha256': '0098e19041a88317466c87d69a19044f018f7362334b325bf71cafe8cbc3ec73'}
AUDIT_CANONICAL_SHA256 = '7a176e2a17353305dff5932e09902a4b2757dc867ac48d2d7ceead6c21bb5a72'
RULE = 'CHARACTER_CTOR_PRE_READY_WRITER_CLOSURE_ACTUAL_NO_START/438'
PHASES = ('pre_prepare', 'pre_activate')
IDENTITIES = {'P': ('47611', '47767'), 'O': ('84805', '84961')}
TARGETS = frozenset((field, phase, side) for phase in PHASES
                    for side in IDENTITIES for field in
                    ('Character.invulnerable', 'Character.invulnerabilityItem'))
PREMISES = (
    'Original declarations initialize false/null; only cleanse, makeInvulnerable and invulnerabilityEnded write these fields.',
    'Pinned seven caller receivers and Character/Player/Opponent initialization closure exclude constructor-to-first-parent-ready makeInvulnerable.',
    'Character has no generic setter; Table.fill targets descriptor properties; scene tracks do not assign the target fields.',
    'Timer birth is the first parent-ready statement, unique per timer ID; owner and timer identities persist through both required cuts.',
    'Observer timer_before increments the birth ledger before the selected-fixture gate; no counter reset or duplicate birth is allowed.',
    'The earliest possible later makeInvulnerable sees false and reaches the counted direct start before native start or true assignment.',
    'No yield or gameplay callback intervenes between item assignment and counted start; required cuts are outside an incomplete writer.',
    'Actual saved pre_activate lineage has integer starts=0; monotonicity also covers pre_prepare. Public zero/stopped and provenance labels are not proof.',
)


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


def validate_source(context, io):
    require(type(context) is dict and set(context) == {'schema', 'inputs', 'project_scripts', 'scene_dependencies', 'other_source', 'premises'}, 'CONTEXT_SHAPE')
    require(context['schema'] == 'phase438-character-source-context/1' and same(context['premises'], list(PREMISES)), 'CONTEXT_RULE')
    require(type(context['inputs']) is dict and set(context['inputs']) == {'audit', 'checkpoints', 'facts'}, 'INPUT_DOMAIN')
    require(len(context['project_scripts']) == 815 and len(context['scene_dependencies']) == 19, 'SOURCE_DOMAIN_COUNTS')
    seen = set()
    for name in ('project_scripts', 'scene_dependencies', 'other_source'):
        require(type(context[name]) is list, 'SOURCE_LIST')
        for pin in context[name]:
            path = canonical(pin['path'])
            require(str(path) not in seen, 'SOURCE_DUPLICATE')
            seen.add(str(path))
            read_pinned(pin, io)
    actual_scripts = {str(path) for path in BASE.rglob('*.gd')}
    require(actual_scripts == {str(canonical(x['path'])) for x in context['project_scripts']}, 'SCRIPT_DOMAIN_DRIFT')
    return {'rule': RULE, 'premises': list(PREMISES), 'context': deepcopy(CONTEXT),
            'project_scripts': deepcopy(context['project_scripts']),
            'scene_dependencies': deepcopy(context['scene_dependencies']),
            'other_source': deepcopy(context['other_source']),
            'public_zero_is_not_proof': True}


def validate_audit(audit):
    require(type(audit) is dict and audit.get('profile') == 'pure-combat-initial-fixed-king-A/437', 'AUDIT_PROFILE')
    require(audit.get('schema') == 'combat-initial-feasibility/437', 'AUDIT_SCHEMA')
    rows, excluded = audit.get('required_rows'), audit.get('excluded_presentation')
    require(type(rows) is list and len(rows) == 1363 and type(excluded) is list and len(excluded) == 116, 'AUDIT_ARRAY_COUNTS')
    require(type(audit.get('required_count')) is int and audit['required_count'] == 1363 and type(audit.get('excluded_present_count')) is int and audit['excluded_present_count'] == 116, 'AUDIT_COUNT_TYPES')
    require(same(audit.get('counts'), {'DIRECT': 1289, 'SOURCE_DERIVED': 2, 'MISSING': 72}), 'AUDIT_COUNTS')
    require(audit.get('King_admitted') is False and audit.get('fullschema') == 'NOT_VALIDATED', 'AUDIT_ADMISSION')
    found, counts, missing = {}, {'DIRECT': 0, 'SOURCE_DERIVED': 0, 'MISSING': 0}, set()
    for ordinal, row in enumerate(rows):
        ident = key(row)
        require(ident not in found, 'AUDIT_DUPLICATE')
        found[ident] = ordinal
        kind = row.get('classification')
        if kind == 'MISSING':
            require(row.get('validation_result') == 'UNPROVEN' and row.get('proof_complete') is False and 'actual_value' not in row, 'AUDIT_MISSING_SHAPE')
            counts['MISSING'] += 1
            missing.add(ident)
        else:
            require(kind in ('DIRECT_OBSERVATION', 'SOURCE_DERIVED') and row.get('validation_result') == 'SUPPORTED' and row.get('proof_complete') is True and 'actual_value' in row, 'AUDIT_SUPPORTED_SHAPE')
            counts['DIRECT' if kind == 'DIRECT_OBSERVATION' else 'SOURCE_DERIVED'] += 1
    require(same(counts, audit['counts']) and TARGETS <= missing, 'AUDIT_TARGETS')
    require(len(missing - TARGETS) == 64 and all(x[0] == 'Timer.private_left' for x in missing - TARGETS), 'AUDIT_OTHER_GAPS')
    excluded_keys = set()
    for row in excluded:
        require(type(row) is dict and set(row) == {'reason', 'original_row'} and type(row['reason']) is str, 'AUDIT_EXCLUDED')
        ident = key(row['original_row'])
        require(ident not in found and ident not in excluded_keys, 'AUDIT_EXCLUDED_ID')
        excluded_keys.add(ident)
    fingerprint = hashlib.sha256(json.dumps(audit, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()
    require(fingerprint == AUDIT_CANONICAL_SHA256, 'AUDIT_FIXED_CANONICAL_FINGERPRINT')
    return found


def unique_node(nodes, role):
    require(type(nodes) is list, 'CUT_NODES')
    roles, ids = set(), set()
    for wrapper in nodes:
        require(type(wrapper) is dict and type(wrapper.get('node')) is dict, 'CUT_NODE_WRAPPER')
        name, native = wrapper.get('role'), wrapper['node'].get('native_id')
        require(type(name) is str and name not in roles and type(native) is str and re.fullmatch('[1-9][0-9]*', native) and native not in ids, 'CUT_NODE_BIJECTION')
        roles.add(name)
        ids.add(native)
    matches = [(i, x) for i, x in enumerate(nodes) if x['role'] == role]
    require(len(matches) == 1, 'CUT_ROLE_MISSING')
    return matches[0]


def validate_cuts(records):
    require(type(records) is list and len(records) == 2, 'CUT_COUNT')
    result, previous = {}, None
    expected_environment = {'fps': {'type': 'int', 'decimal': '60'}, 'scale': {'type': 'float', 'binary64_be': '3ff0000000000000'}, 'paused': {'type': 'bool', 'value': False}}
    for phase, record, sequence, line, site in zip(PHASES, records, (138, 1231), (1, 4), ('prepareItems', 'activateItems')):
        require(type(record) is dict and record.get('schema') == 'observer7-record/1' and record.get('channel') == 'input' and record.get('edge') == 'checkpoint', 'CUT_RECORD')
        require(type(record.get('sequence')) is int and record['sequence'] == sequence and record.get('site') == 'Core/Game.gd::' + site, 'CUT_SITE_SEQUENCE')
        require(same(record.get('subject'), {'type': 'native_ref', 'native_id': '4015', 'role': 'game', 'class': 'Node2D'}), 'CUT_GAME')
        stamp, payload = record.get('stamp'), record.get('payload')
        require(type(stamp) is dict and type(payload) is dict and stamp.get('phase') == 'Core/Game.gd::' + site + ':enter', 'CUT_PHASE')
        frames = []
        for name in ('physics_frame', 'idle_frame'):
            value = stamp.get(name)
            require(type(value) is str and re.fullmatch('[0-9]+', value), 'CUT_FRAME_TYPE')
            require(str(int(value)) == value, 'CUT_FRAME_CANONICAL')
            frames.append(int(value))
        require(frames == ([302, 38] if phase == 'pre_prepare' else [446, 56]), 'CUT_FIXED_FRAME_STAMP')
        require(previous is None or all(a >= b for a, b in zip(frames, previous)), 'CUT_FRAME_ORDER')
        previous = frames
        require(same(stamp.get('combat_time'), {'type': 'float', 'binary64_be': '0000000000000000'}) and same(payload.get('environment'), expected_environment), 'CUT_ENVIRONMENT')
        expected_util = '4014222233c00000' if phase == 'pre_prepare' else '401dbbbbd5c00000'
        require(same(stamp.get('util_time'), {'type': 'float', 'binary64_be': expected_util}), 'CUT_UTIL_STAMP')
        resources = payload.get('source_resources')
        require(type(resources) is list and len(resources) == 2 and {r.get('side') for r in resources if type(r) is dict} == set(IDENTITIES), 'CUT_RESOURCES')
        result[phase] = {}
        for side, (owner, timer_id) in IDENTITIES.items():
            si, resource = next((i, r) for i, r in enumerate(resources) if r['side'] == side)
            require(type(resource.get('native_id')) is str and resource['native_id'] == owner, 'CUT_RESOURCE_OWNER')
            ci, character = unique_node(payload.get('nodes'), 'character:' + side)
            char = character['node']
            require(char.get('native_id') == owner and char.get('role') == side and char.get('class') == 'Node2D' and char.get('inside_tree') is True, 'CUT_CHARACTER_ID')
            ti, wrapper = unique_node(payload['nodes'], 'invu:' + side)
            timer = wrapper.get('timer')
            require(type(timer) is dict and same(wrapper['node'], timer.get('node')), 'CUT_TIMER_NODE_ALIAS')
            node = timer['node']
            require(node.get('native_id') == timer_id and node.get('role') == 'invu:' + side and node.get('class') == 'Timer' and node.get('name') == 'InvulnerabilityTimer' and node.get('path') == char.get('path') + '/InvulnerabilityTimer', 'CUT_TIMER_ID')
            require(type(timer.get('process_mode')) is int and timer['process_mode'] == 0, 'CUT_MODE')
            result[phase][side] = {'owner_id': owner, 'timer_id': timer_id, 'timer': deepcopy(timer), 'input_refs': [
                {'file': 'observer7-input.jsonl', 'line': line, 'sequence': sequence, 'native_owner': owner, 'pointer': f'/payload/source_resources/{si}/native_id'},
                {'file': 'observer7-input.jsonl', 'line': line, 'sequence': sequence, 'native_owner': owner, 'pointer': f'/payload/nodes/{ci}/node'},
                {'file': 'observer7-input.jsonl', 'line': line, 'sequence': sequence, 'native_owner': timer_id, 'pointer': f'/payload/nodes/{ti}/timer'}]}
    return result


def validate_ledger(facts, bindings):
    require(type(facts) is dict and facts.get('schema') == 'phase355-king-input-facts/1' and type(facts.get('timers')) is dict, 'FACTS_SCHEMA')
    result = {}
    for side, (owner, timer_id) in IDENTITIES.items():
        fact = facts['timers'].get('invu:' + side)
        require(type(fact) is dict and set(fact) == {'lineage', 'current', 'private_provenance'}, 'FACT_TIMER_SHAPE')
        lineage = fact['lineage']
        require(type(lineage) is dict and set(lineage) == {'timer_id', 'owner_id', 'kind', 'starts', 'stops', 'birth'}, 'LINEAGE_SHAPE')
        require(type(lineage['timer_id']) is str and lineage['timer_id'] == timer_id and type(lineage['owner_id']) is str and lineage['owner_id'] == owner and lineage['kind'] == 'Character.scene.ready', 'LINEAGE_ID_KIND')
        for name in ('starts', 'stops'):
            require(type(lineage[name]) is int and lineage[name] == 0, 'LINEAGE_ZERO_INTEGER_' + name)
        birth = lineage['birth']
        require(type(birth) is dict and type(birth.get('node')) is dict, 'BIRTH_SHAPE')
        node = birth['node']
        require(node.get('native_id') == timer_id and node.get('role') is None and node.get('class') == 'Timer' and node.get('name') == 'InvulnerabilityTimer' and node.get('inside_tree') is True, 'BIRTH_ID')
        require(type(birth.get('process_mode')) is int and birth['process_mode'] == 0 and birth.get('autostart') is False and birth.get('one_shot') is True and birth.get('paused') is False, 'BIRTH_CONFIG')
        for phase in PHASES:
            binding = bindings[phase][side]
            require(binding['owner_id'] == owner and binding['timer_id'] == timer_id, 'LINEAGE_BINDING')
            require(node.get('path') == binding['timer']['node']['path'], 'BIRTH_PATH')
        require(same(fact['current'], bindings['pre_activate'][side]['timer']), 'FACT_CURRENT_IDENTITY')
        result[side] = {'lineage': deepcopy(lineage), 'input_ref': {'file': 'king-input-facts.json', 'pointer': '/timers/invu:' + side + '/lineage', 'native_owner': timer_id}, 'counter_cut': 'Core/Game.gd::activateItems:enter.before_original_body'}
    return result


def project(audit, records, facts):
    ordinals = validate_audit(audit)
    bindings = validate_cuts(records)
    ledger = validate_ledger(facts, bindings)
    report, changes = deepcopy(audit), []
    for ident in sorted(TARGETS, key=ordinals.get):
        field, phase, side = ident
        ordinal = ordinals[ident]
        row = report['required_rows'][ordinal]
        old = deepcopy(row)
        value = {'type': 'bool', 'value': False} if field == 'Character.invulnerable' else {'type': 'null'}
        proof = {'rule': RULE, 'premises': list(PREMISES), 'binding': deepcopy(bindings[phase][side]), 'no_start_ledger': deepcopy(ledger[side]), 'source_context': deepcopy(CONTEXT), 'original_row': old}
        row.update(classification='SOURCE_DERIVED', validation_result='SUPPORTED', proof_complete=True, actual_value=value, rule=RULE, input_refs=deepcopy(bindings[phase][side]['input_refs']) + [deepcopy(ledger[side]['input_ref'])], source_derivation=proof)
        row.pop('reasons', None)
        changes.append({'key': list(ident), 'required_ordinal': ordinal, 'actual_value': value, 'proof': proof})
    report.update(schema='phase438-character-combat-initial-overlay/1', status='CHARACTER8_SOURCE_CANDIDATES_PENDING_INDEPENDENT_ACTUAL_ACCEPTANCE', counts={'DIRECT': 1289, 'SOURCE_DERIVED': 10, 'MISSING': 64}, phase438_rule=RULE)
    require(same(report['excluded_presentation'], audit['excluded_presentation']), 'EXCLUDED_CHANGED')
    require([key(x) for x in report['required_rows']] == [key(x) for x in audit['required_rows']], 'ROW_ORDER_CHANGED')
    for before, after in zip(audit['required_rows'], report['required_rows']):
        if key(before) not in TARGETS:
            require(same(before, after), 'NONTARGET_CHANGED')
    return report, {'schema': 'phase438-character-proof/1', 'rule': RULE, 'changes': changes,
                    'candidate_count': 8, 'remaining_missing': 64, 'Buff44_promotions': 0,
                    'acceptance': 'INDEPENDENT_REVIEW_REQUIRED', 'King_admitted': False}


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


def run(output_new):
    output = canonical(output_new)
    require(output.is_relative_to(REPO / 'data') and output != REPO / 'data', 'OUTPUT_DOMAIN')
    physical(output.parent, False)
    require(not os.path.lexists(output), 'OUTPUT_EXISTS')
    io = []
    context = strict_json(read_pinned(CONTEXT, io))
    source = validate_source(context, io)
    inputs = {name: read_pinned(pin, io) for name, pin in context['inputs'].items()}
    lines = inputs['checkpoints'].splitlines()
    require(len(lines) == 6, 'INPUT_FILE_LINE_COUNT')
    records = [strict_json(lines[i]) for i in (0, 3)]
    report, proof = project(strict_json(inputs['audit']), records, strict_json(inputs['facts']))
    proof['source'] = source
    proof['input_descriptors'] = deepcopy(context['inputs'])
    before = deepcopy(io)
    after = []
    for pin in before:
        read_pinned(pin, after)
    require(same(before, after), 'READBACK_ORDER_OR_PIN')
    output.mkdir(mode=0o700)
    owned = []
    try:
        owned.append(save_new(output / 'proof-evidence.json', proof))
        owned.append(save_new(output / 'overlay-report.json', report))
        owned.append(save_new(output / 'input-readback.json', {'before': before, 'after': after, 'unchanged': True, 'whole_files_hashed_before': len(before), 'whole_files_rehashed_after': len(after), 'whole_file_bytes_include_unparsed_records': True, 'parsed_checkpoint_lines': [1, 4], 'checkpoint_records_parsed': 2, 'facts_json_syntax_decode': 'whole JSON object', 'facts_business_decode_pointers': ['/timers/invu:P', '/timers/invu:O'], 'EXPECTED_file_reads': 0, 'postcleanup_records_parsed': 0}))
        save_new(output / 'owned-files.json', {'schema': 'phase438-character-overlay-owned/1', 'files': owned, 'independent_acceptance': 'PENDING'})
    except Exception as error:
        if not os.path.lexists(output / 'first-error.json'):
            save_new(output / 'first-error.json', {'error': type(error).__name__, 'reason': str(error)[:1000], 'preserved_outputs': owned})
        raise
    return {'output': str(output), 'new_candidates': 8, 'remaining_missing': 64, 'accepted': False}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-new', required=True)
    args = parser.parse_args(argv)
    print(json.dumps(run(args.output_new), sort_keys=True))


if __name__ == '__main__':
    main()
