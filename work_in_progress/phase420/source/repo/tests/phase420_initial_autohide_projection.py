"""Initial-only, stdlib projection. No SUT/model imports; never execute without a new Root release."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import struct

REPO = Path('/workspace/python-original-engine/repo')
BASE = REPO / 'data/phase420-initial-partial-recipe-source'
CONTEXT = BASE / 'context.json'
RELEASE_PATH = REPO / 'data/phase420-root-initial-partial-projection-release/release.json'
OUTPUT = REPO / 'data/phase420-initial-partial-projection-first-001'
ROOT_SCHEMA = 'root420-initial-autohide-projection/1'
REVIEW_SCHEMA = 'independent421-autohide-partial-recipe-final-review/1'
REVIEW_STATUS = 'INDEPENDENT421_AUTOHIDE_PARTIAL_RECIPE_SOURCE_AND_FUNCTIONAL_ACCEPTED_ROOT_PENDING'
G01 = 'ACCEPTED_FOR_EXACT_FIXED_AUTOHIDE_SOURCE_DOMAIN'
G02 = 'ACCEPTED_BOUNDED_VERSION_ATTRIBUTED_NATIVE_SEMANTICS_FOR_RULE_A'
PHASES = ('pre_prepare', 'pre_activate')
AUTO = {'king_hide:P:12': ('81740', '81718'), 'king_drag:P:12': ('81732', '81714')}
KING, CHARACTER = '81679', '47611'
FLOAT_ZERO = {'type': 'float', 'binary64_be': '0000000000000000'}
FLOAT_ONE = {'type': 'float', 'binary64_be': '3ff0000000000000'}
PRIVATE_MINUS_ONE = {'type': 'float', 'binary64_be': 'bff0000000000000'}
UI_SITES = ('Items/Item.gd::respondToHover', 'Items/Item.gd::respondToHoverEnd', 'Items/Item.gd::_process:dragged', 'Items/Item.gd::_process:rigid', 'Items/Item.gd::activateDragParticles', 'Items/Item.gd::deactivateDragParticles', 'Items/Item.gd::onAddedToGridStorage', 'Items/Item.gd::deactivateParticles', 'Utility/AutoHideParticles.gd::activate', 'Utility/AutoHideParticles.gd::deactivate', 'Utility/AutoHideParticles.gd::startTimer', 'Utility/AutoHideParticles.gd::instantClear')
AUTO_UI_SITES = UI_SITES[-4:]
_TOKEN = object()


class Rejected(ValueError):
    pass


def require(condition, reason):
    if not condition:
        raise Rejected(reason)


def integer(value, minimum=0):
    return type(value) is int and value >= minimum


def native_id(value):
    return type(value) is str and re.fullmatch(r'[1-9][0-9]*', value) is not None


def same(left, right):
    return json.dumps(left, sort_keys=True, separators=(',', ':'), allow_nan=False) == json.dumps(right, sort_keys=True, separators=(',', ':'), allow_nan=False)


def strict_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, 'DUPLICATE_JSON_KEY')
            result[key] = value
        return result
    def bad_constant(value):
        raise Rejected('NONFINITE_JSON_CONSTANT')
    def finite_float(value):
        number = float(value)
        require(number not in (float('inf'), float('-inf')), 'NONFINITE_JSON_NUMBER')
        return number
    try:
        return json.loads(raw.decode('utf-8', 'strict'), object_pairs_hook=pairs, parse_constant=bad_constant, parse_float=finite_float)
    except (ValueError, UnicodeError) as error:
        raise Rejected('STRICT_JSON: ' + str(error)) from error


def canonical_path(value):
    require(type(value) is str and bool(value), 'PATH_TYPE')
    path = Path(value)
    require('..' not in path.parts and '.' not in path.parts, 'PATH_COMPONENT')
    require(str(path) == value, 'NONCANONICAL_PATH')
    return path if path.is_absolute() else REPO / path


def physical_path(path, leaf_regular=True):
    # lstat all ancestors before any content access; never resolve through a link.
    for part in reversed((path,) + tuple(path.parents)):
        info = part.lstat()
        require(not stat.S_ISLNK(info.st_mode), 'SYMLINK_PATH')
        if part != path or not leaf_regular:
            require(stat.S_ISDIR(info.st_mode), 'PARENT_NOT_DIRECTORY')
        else:
            require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1, 'NONORDINARY_FILE')
    return path.lstat()


def descriptor(value):
    require(type(value) is dict and set(value) == {'path', 'size', 'sha256'}, 'DESCRIPTOR_SHAPE')
    canonical_path(value['path'])
    require(integer(value['size']) and type(value['sha256']) is str and re.fullmatch(r'[0-9a-f]{64}', value['sha256']), 'DESCRIPTOR_TYPE')
    return value


def read_regular(value, cap=2097152, io=None):
    d = descriptor(value)
    require(d['size'] <= cap, 'READ_CAP')
    path = canonical_path(d['path'])
    before = physical_path(path)
    require(before.st_size == d['size'], 'SIZE_BEFORE_READ')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        now = os.fstat(fd)
        require((now.st_dev, now.st_ino) == (before.st_dev, before.st_ino) and stat.S_ISREG(now.st_mode) and now.st_nlink == 1, 'OPEN_IDENTITY')
        chunks, count = [], 0
        while True:
            chunk = os.read(fd, 65536)
            if not chunk:
                break
            count += len(chunk)
            require(count <= d['size'], 'READ_GROWTH')
            chunks.append(chunk)
        after = os.fstat(fd)
        require((now.st_size, now.st_mtime_ns, now.st_ctime_ns) == (after.st_size, after.st_mtime_ns, after.st_ctime_ns), 'READ_METADATA_CHANGE')
    finally:
        os.close(fd)
    last = physical_path(path)
    require((last.st_dev, last.st_ino, last.st_size, last.st_mtime_ns, last.st_ctime_ns) == (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns), 'PATH_CHANGED')
    raw = b''.join(chunks)
    require(len(raw) == d['size'] and hashlib.sha256(raw).hexdigest() == d['sha256'], 'READBACK_PIN')
    if io is not None:
        io.append({'descriptor': d, 'bytes_hashed': len(raw), 'ordinary_nlink1': True})
    return raw


def target_keys():
    roles = ['tick:P', 'tick:O'] + [f'buff:{side}:{i}' for side in ('P', 'O') for i in range(100, 111)]
    roles += ['fatigue:start', 'fatigue:tick'] + [f'aux:{side}:{name}' for side in ('P', 'O') for name in ('battleRageTimer', 'autoRageTimer')]
    roles += ['invu:P', 'invu:O', 'king_buff:P:12', 'king_hide:P:12', 'king_drag:P:12']
    return [(field, phase, role) for phase in PHASES for field, role in
            ([(f'Character.{name}', side) for side in ('P', 'O') for name in ('invulnerable', 'invulnerabilityItem', 'invulBubbleVisible')] +
             [(f'King.{name}', 'P:12') for name in ('crown', 'light_visible', 'light_modulate')] + [('Timer.private_left', role) for role in roles])]


def load_initial_index(raw):
    rows = strict_json(raw)
    require(type(rows) is list and len(rows) == 1479, 'INDEX_COUNT')
    result = {}
    missing, direct = set(), 0
    for ordinal, row in enumerate(rows):
        require(type(row) is dict and all(type(row.get(k)) is str for k in ('field_id', 'phase', 'side_or_role')), 'INDEX_KEY_TYPE')
        key = (row['field_id'], row['phase'], row['side_or_role'])
        require(key not in result, 'INDEX_DUPLICATE_TARGET')
        require(type(row.get('proof_complete')) is bool and type(row.get('input_refs')) is list, 'INDEX_PROOF_OR_REFS_TYPE')
        if row.get('classification') == 'MISSING':
            require(row.get('validation_result') == 'UNPROVEN' and row['proof_complete'] is False and 'actual_value' not in row, 'INDEX_MISSING_SHAPE')
            missing.add(key)
        else:
            require(row.get('classification') == 'DIRECT_OBSERVATION' and row.get('validation_result') == 'SUPPORTED' and row['proof_complete'] is True and 'actual_value' in row, 'INDEX_DIRECT_SHAPE')
            direct += 1
        result[key] = {'index': ordinal, 'row': row}
    require(missing == set(target_keys()) and direct == 1391, 'INDEX_FIXED_TARGET_SET')
    return result


def observed(index, field, phase, role):
    found = index.get((field, phase, role))
    if found is None:
        return None
    row = found['row']
    require(row.get('classification') == 'DIRECT_OBSERVATION', 'NOT_DIRECT_SUPPORT')
    return {'index': found['index'], 'value': row['actual_value'], 'input_refs': row['input_refs']}


def project_slots(raw, fixed_table):
    obj = strict_json(raw)
    require(type(obj) is dict and obj.get('schema') == 'phase359-source-slot-bindings/1', 'SLOT_SCHEMA')
    require(same(obj.get('source_slot_table'), fixed_table) and obj.get('raw_early_rows_unchanged') is True and obj.get('model_input_admitted') is False, 'FIXED_SLOT_DOMAIN')
    rows = obj.get('actual_bindings')
    require(type(rows) is list and len(rows) == len(fixed_table), 'SLOT_COUNT')
    seen, ids, selected = set(), set(), None
    inventories, encounters = {}, {}
    expected = {x['instance_id']: x for x in fixed_table}
    for n, row in enumerate(rows):
        require(type(row) is dict and row.get('instance_id') in expected, 'SLOT_ROLE')
        role = row['instance_id']
        require(role not in seen and native_id(row.get('native_id')) and row['native_id'] not in ids, 'SLOT_DUPLICATE_ID')
        seen.add(role); ids.add(row['native_id'])
        spec = expected[role]
        require(type(row.get('input_slot')) is int and row['input_slot'] == spec['input_slot'], 'SLOT_ORDINAL')
        require(same(row.get('item_index'), {'type': 'int', 'decimal': str(spec['item_index'])}), 'SLOT_ITEM_TYPE')
        require(native_id(row.get('character_id')) and native_id(row.get('inventory_id')) and native_id(row.get('descriptor_id')), 'SLOT_OWNER_ID')
        side = spec['side']
        require(row['character_id'] == {'P': CHARACTER, 'O': '84805'}[side], 'SLOT_CHARACTER_JOIN')
        inventories.setdefault(side, row['inventory_id'])
        require(inventories[side] == row['inventory_id'], 'SLOT_INVENTORY_JOIN')
        encounter = row.get('inventory_encounter_index')
        require(integer(encounter) and encounter < sum(x['side'] == side for x in fixed_table) and encounter not in encounters.setdefault(side, set()), 'SLOT_ENCOUNTER')
        encounters[side].add(encounter)
        expected_xy = {k: {'type': 'float', 'binary64_be': struct.pack('>d', float(spec[k])).hex()} for k in ('x', 'y')}
        require(same(row.get('top_left'), expected_xy) and same(row.get('orientation'), {'type': 'int', 'decimal': str(spec['f'])}), 'SLOT_GEOMETRY_TYPE')
        cells = row.get('occupiedCells')
        require(type(cells) is list and all(type(c) is list and len(c) == 2 and all(type(n) is int for n in c) for c in cells), 'SLOT_CELLS_TYPE')
        require(len(cells) == len({tuple(c) for c in cells}) and {tuple(c) for c in cells} == {tuple(c) for c in spec['cells']}, 'SLOT_CELLS')
        if role == 'P:12':
            require(row['native_id'] == KING and row['character_id'] == CHARACTER, 'KING_SLOT_ID')
            selected = {'row': n, 'pointer': '/actual_bindings/' + str(n), 'binding': row}
    require(selected is not None, 'KING_SLOT_MISSING')
    return selected


def _skip_string(raw, pos):
    require(raw[pos:pos+1] == b'"', 'ENVELOPE_STRING')
    pos += 1
    while pos < len(raw):
        if raw[pos] == 92:
            pos += 2
        elif raw[pos] == 34:
            return pos + 1
        else:
            pos += 1
    raise Rejected('UNTERMINATED_ENVELOPE_STRING')


def _skip_value(raw, pos):
    if raw[pos:pos+1] == b'"':
        return _skip_string(raw, pos)
    if raw[pos:pos+1] in (b'{', b'['):
        depth = 0
        while pos < len(raw):
            char = raw[pos:pos+1]
            if char == b'"':
                pos = _skip_string(raw, pos); continue
            if char in (b'{', b'['): depth += 1
            if char in (b'}', b']'):
                depth -= 1
                if depth == 0: return pos + 1
            pos += 1
        raise Rejected('UNTERMINATED_ENVELOPE_CONTAINER')
    while pos < len(raw) and raw[pos:pos+1] not in b',} \t\r\n': pos += 1
    return pos


def envelope_sequence(raw):
    # Scan all top-level keys; payload values remain opaque bytes, never decoded.
    pos = 0
    def ws(i):
        while i < len(raw) and raw[i:i+1] in b' \r\n\t': i += 1
        return i
    pos = ws(pos); require(raw[pos:pos+1] == b'{', 'ENVELOPE_OBJECT'); pos += 1
    keys, sequence = set(), None
    while pos < len(raw):
        pos = ws(pos); end = _skip_string(raw, pos); key = strict_json(raw[pos:end]); pos = ws(end)
        require(key not in keys, 'DUPLICATE_ENVELOPE_KEY'); keys.add(key)
        require(raw[pos:pos+1] == b':', 'ENVELOPE_COLON'); pos = ws(pos + 1)
        if key == 'sequence':
            match = re.match(rb'(0|[1-9][0-9]*)(?=[,}\s])', raw[pos:])
            require(match is not None, 'ENVELOPE_SEQUENCE_TYPE')
            sequence = int(match.group(1)); pos += len(match.group(1))
        else:
            end = _skip_value(raw, pos)
            require(end > pos, 'ENVELOPE_VALUE_MISSING'); pos = end
        pos = ws(pos)
        if raw[pos:pos+1] == b'}':
            pos = ws(pos + 1)
            require(pos == len(raw), 'ENVELOPE_TRAILING_BYTES')
            require(sequence is not None, 'ENVELOPE_SEQUENCE_ABSENT')
            return sequence
        require(raw[pos:pos+1] == b',', 'ENVELOPE_SEPARATOR'); pos += 1
    raise Rejected('UNTERMINATED_ENVELOPE_OBJECT')


def project_lineage(raw, slot, cutoff=138):
    require(type(cutoff) is int and cutoff == 138, 'LINEAGE_FIXED_CUT')
    position, line, previous = 0, 0, -1
    selected = []
    cut = {'kind': 'EOF', 'byte_offset': len(raw)}
    while position < len(raw):
        end = raw.find(b'\n', position)
        finish = len(raw) if end < 0 else end + 1
        record = raw[position:finish]; line += 1
        seq = envelope_sequence(record)
        require(seq > previous, 'LINEAGE_SEQUENCE_ORDER')
        if seq >= cutoff:
            cut = {'kind': 'FIRST_SEQUENCE_AT_OR_AFTER_CUT', 'line': line, 'sequence': seq, 'byte_offset': position}
            break
        require(end >= 0 and len(record) <= 1048576, 'LINEAGE_INITIAL_LINE_BOUND')
        row = strict_json(record)
        require(row.get('schema') == 'observer7-record/1' and row.get('channel') == 'lineage' and type(row.get('sequence')) is int and row['sequence'] == seq, 'LINEAGE_ENVELOPE')
        require(type(row.get('site')) is str and type(row.get('edge')) is str and type(row.get('subject')) is dict and type(row.get('payload')) is dict, 'LINEAGE_ENVELOPE_TYPE')
        if row['subject'].get('native_id') == KING:
            require(row['subject'].get('type') == 'native_ref', 'KING_LINEAGE_REF')
            require((row['site'], row['edge']) in {('Items/ItemDescriptor.gd::instantiate', 'scene_instance'), ('Items/Item.gd::_ready', 'enter'), ('Items/Item.gd::_ready', 'return_implicit'), ('Items/Item.gd::_ready', 'return_explicit')}, 'UNEXPECTED_SELECTED_INITIAL_LINEAGE')
            selected.append({'line': line, 'sequence': seq, 'site': row['site'], 'edge': row['edge'], 'subject': row['subject'], 'payload': row['payload']})
        previous = seq; position = finish
    scene = [x for x in selected if x['edge'] == 'scene_instance']
    ready = [x for x in selected if x['site'] == 'Items/Item.gd::_ready']
    require(len(scene) <= 1 and len([x for x in ready if x['edge'] == 'enter']) <= 1 and len([x for x in ready if x['edge'].startswith('return_')]) <= 1, 'DUPLICATE_KING_LINEAGE')
    gaps = []
    if not scene: gaps.append('INITIAL_SCENE_ROW_MISSING')
    else:
        row = scene[0]; val = row['payload']
        require(row['site'] == 'Items/ItemDescriptor.gd::instantiate' and val.get('item_id') == KING and val.get('pooled') is False and val.get('scene_path') == 'res://Items/Exclusive/KingGoobert.tscn', 'KING_SCENE_DOMAIN')
        require(val.get('descriptor_id') == slot['binding']['descriptor_id'] and same(val.get('item_index'), {'type': 'int', 'decimal': '262'}), 'KING_DESCRIPTOR_JOIN')
    enters = [x for x in ready if x['edge'] == 'enter']; leaves = [x for x in ready if x['edge'].startswith('return_')]
    if not enters or not leaves: gaps.append('INITIAL_ITEM_READY_PAIR_MISSING')
    elif scene:
        require(scene[0]['sequence'] < enters[0]['sequence'] < leaves[0]['sequence'] and same(leaves[0]['payload'].get('return_value'), {'type': 'null'}), 'KING_READY_ORDER_RETURN')
    return {'selected': selected, 'cut': cut, 'suffix_semantics': 'NOT_DECODED_OR_VALIDATED', 'gaps': gaps}


def project_ui(raw):
    position, line, rows = 0, 0, []
    while position < len(raw):
        end = raw.find(b'\n', position)
        require(end >= 0 and end + 1 - position <= 16384 and line < 65536, 'UI_INITIAL_LINE_BOUND')
        row = strict_json(raw[position:end+1]); line += 1
        require(type(row) is dict and row.get('schema') == 'phase355-king-ui-authority/1' and type(row.get('sequence')) is int and row['sequence'] == line - 1, 'UI_SEQUENCE_SCHEMA')
        require(type(row.get('kind')) is str and type(row.get('site')) is str and type(row.get('payload')) is dict and integer(row.get('physics_frame')) and integer(row.get('idle_frame')) and type(row.get('in_physics')) is bool, 'UI_ENVELOPE')
        rows.append({'line': line, **row}); position = end + 1
        if row['kind'] == 'roles':
            require(row['site'] == 'configure', 'FIRST_UI_ROLES_SITE')
            break
    require(rows and rows[0]['kind'] == 'open' and rows[0]['site'] == 'sink._ready' and rows[-1]['kind'] == 'roles', 'UI_OPEN_OR_FIRST_ROLES_MISSING')
    require(sum(r['kind'] == 'open' for r in rows) == 1, 'UI_DUPLICATE_OPEN')
    payload = rows[0]['payload']; after = payload.get('after')
    require(type(after) is dict and native_id(after.get('root_id')) and after.get('disable_input') is True and after.get('physics_object_picking') is False, 'UI_INITIAL_CONTROL')
    require(payload.get('case') == 'KING-K1-A-353', 'UI_CASE')
    root = after['root_id']; roles = rows[-1]['payload']
    require(roles.get('using_controller') is False and same(roles.get('kings'), [{'item_id': KING, 'role': 'P:12'}]), 'FIRST_UI_ROLES_BINDING')
    guards = roles.get('selected_guards'); require(type(guards) is list, 'UI_GUARDS_TYPE')
    selected_guard = [g for g in guards if type(g) is dict and (g.get('item_id') == KING or g.get('role') == 'P:12')]
    require(len(selected_guard) == 1, 'UI_KING_GUARD_DUPLICATE_OR_MISSING')
    guard = selected_guard[0]
    require(guard.get('item_id') == KING and guard.get('role') == 'P:12' and guard.get('viewport_id') == root and all(guard.get(k) is False for k in ('focus', 'hovered', 'dragged')) and type(guard.get('mode')) is int and guard['mode'] == 1, 'UI_KING_GUARD_DOMAIN')
    binds = [r for r in rows if r['kind'] == 'bind' and r['payload'].get('item_id') == KING]
    require(len(binds) <= 1, 'UI_DUPLICATE_KING_BIND')
    shared = []
    if not binds: shared.append('INITIAL_UI_BIND_MISSING')
    else:
        bind = binds[0]; p = bind['payload']
        require(bind['site'] == 'scene_instance' and p.get('script') == 'res://Items/Exclusive/KingGoobert.gd' and p.get('scene') == 'res://Items/Exclusive/KingGoobert.tscn' and p.get('pooled') is False and p.get('inside_tree') is False and type(p.get('generation')) is int and p['generation'] == 1, 'UI_KING_BIND_DOMAIN')
        require(p.get('activation_id') == AUTO['king_hide:P:12'][1] and p.get('drag_id') == AUTO['king_drag:P:12'][1] and len({root, KING, p['activation_id'], p['drag_id']}) == 4, 'UI_OWNER_COLLISION')
    per_role = {}
    for role, (_, owner) in AUTO.items():
        rr = [r for r in rows if r['kind'] == 'ready' and r['payload'].get('receiver_id') == owner]
        require(len(rr) <= 1, 'UI_DUPLICATE_READY_OWNER')
        gaps = list(shared)
        for event in rows:
            if event['kind'] == 'entry' and event['payload'].get('receiver_id') in (owner, KING):
                classification = event['payload'].get('classification')
                require(type(classification) is str and type(event['payload'].get('king_source')) is bool, 'UI_ENTRY_CLASSIFICATION_TYPE')
                supported = (event['site'] in AUTO_UI_SITES and
                             event['payload']['receiver_id'] == AUTO['king_hide:P:12'][1] and
                             classification == 'supported_activation' and
                             event['payload']['king_source'] is False and
                             len(rr) == 1 and rr[0]['sequence'] < event['sequence'])
                if not supported:
                    gaps.append('UNSUPPORTED_INITIAL_UI_PATH')
        if not rr: gaps.append('INITIAL_OWNER_READY_MISSING')
        else:
            r = rr[0]; p = r['payload']; ancestry = p.get('ancestry')
            require(r['site'] == 'Utility/AutoHideParticles.gd::_ready' and p.get('script') == 'res://Utility/AutoHideParticles.gd' and p.get('viewport_id') == root and type(ancestry) is list and 1 <= len(ancestry) <= 32, 'UI_READY_DOMAIN')
            require(all(type(a) is dict and native_id(a.get('native_id')) and type(a.get('king_source')) is bool for a in ancestry), 'UI_ANCESTRY_TYPE')
            ids = [a['native_id'] for a in ancestry]
            require(len(ids) == len(set(ids)) and owner not in ids and ids[-1] == root and sum(a['native_id'] == KING and a['king_source'] is True for a in ancestry) == 1, 'UI_ANCESTRY_JOIN')
            if binds: require(binds[0]['sequence'] < r['sequence'] < rows[-1]['sequence'], 'UI_BIRTH_READY_ORDER')
        per_role[role] = {'ready': rr, 'gaps': gaps}
    return {'open': rows[0], 'bind': binds, 'roles': rows[-1], 'per_role': per_role, 'cut': {'line': line, 'ui_sequence': rows[-1]['sequence'], 'byte_offset_after': position}, 'suffix_semantics': 'NOT_DECODED_OR_VALIDATED'}


def check_autohide_role(index, provenance, role):
    require(role in AUTO, 'AUTOHIDE_ROLE_ONLY')
    timer, owner = AUTO[role]
    gaps = list(provenance['lineage']['gaps']) + list(provenance['ui']['per_role'][role]['gaps'])
    evidence = []
    def get(field, phase):
        v = observed(index, field, phase, role)
        if v is None: gaps.append('MISSING_' + phase + '_' + field); return None
        require(v['value'] is not None and type(v['input_refs']) is list and len(v['input_refs']) == 1, 'DIRECT_VALUE_OR_REFERENCE_MISSING')
        ref = v['input_refs'][0]
        require(type(ref) is dict and type(ref.get('pointer')) is str, 'SUPPORT_REFERENCE_TYPE')
        if field.startswith('Timer.lineage.'):
            require(ref.get('file') == 'king-input-facts.json' and ref['pointer'] == '/timers/' + role + '/lineage/' + field.rsplit('.', 1)[1], 'FACT_REFERENCE_JOIN')
        else:
            require(ref.get('file') == 'observer7-input.jsonl' and type(ref.get('sequence')) is int and ref['sequence'] == {'pre_prepare': 138, 'pre_activate': 1231}[phase] and type(ref.get('line')) is int and ref['line'] == {'pre_prepare': 1, 'pre_activate': 4}[phase] and ref.get('native_owner') == timer and ref['pointer'].startswith('/payload/nodes/'), 'CHECKPOINT_SUPPORT_ID')
        evidence.append(v)
        return v['value']
    for phase, sequence in zip(PHASES, (138, 1231)):
        ident = get('Timer.node.native_id', phase)
        if ident is not None: require(ident == timer, 'CROSS_PHASE_TIMER_ID')
        checks = {'Timer.process_mode': 1, 'Timer.wait_time': FLOAT_ONE, 'Timer.time_left': FLOAT_ZERO, 'Timer.one_shot': True, 'Timer.autostart': False, 'Timer.paused': False, 'Timer.stopped': True, 'Timer.node.class': 'Timer', 'Timer.node.inside_tree': True, 'Timer.node.internal_idle': False, 'Timer.node.internal_physics': False, 'Timer.node.ordinary_idle': False, 'Timer.node.ordinary_physics': False}
        for field, expected in checks.items():
            value = get(field, phase)
            if value is not None:
                require(type(value) is type(expected), 'PUBLIC_VALUE_TYPE')
                if type(expected) is dict:
                    require(set(value) == set(expected) and value.get('type') == 'float' and type(value.get('binary64_be')) is str and re.fullmatch(r'[0-9a-f]{16}', value['binary64_be']), 'TYPED_REAL_SHAPE')
                if not same(value, expected): gaps.append('UNSUPPORTED_' + phase + '_' + field)
    facts = {key: get('Timer.lineage.' + key, 'pre_activate') for key in ('timer_id', 'owner_id', 'kind', 'starts', 'stops', 'birth')}
    if facts['timer_id'] is not None: require(facts['timer_id'] == timer, 'FACT_TIMER_ID')
    if facts['owner_id'] is not None: require(facts['owner_id'] == owner, 'FACT_OWNER_ID')
    if facts['kind'] is not None:
        require(type(facts['kind']) is str, 'BIRTH_KIND_TYPE')
        if facts['kind'] != 'AutoHide.Timer.new': gaps.append('BIRTH_KIND_UNSUPPORTED')
    for key in ('starts', 'stops'):
        if facts[key] is not None:
            require(integer(facts[key]), 'COUNTER_TYPE')
            if facts[key] != 0: gaps.append('NONZERO_LIFETIME_' + key.upper())
    born = facts['birth']
    if born is not None:
        require(type(born) is dict and type(born.get('node')) is dict and born['node'].get('native_id') == timer, 'BIRTH_IDENTITY')
        expected = {'process_mode': 1, 'wait_time': FLOAT_ONE, 'time_left': FLOAT_ZERO, 'one_shot': False, 'autostart': False, 'paused': False, 'stopped': True}
        require(all(type(born.get(k)) is type(v) for k, v in expected.items()), 'BIRTH_CONFIGURATION_TYPE')
        if any(not same(born.get(k), v) for k, v in expected.items()): gaps.append('BIRTH_CONSTRUCTOR_CONFIGURATION')
        node = born['node']
        require(type(node.get('class')) is str and (node.get('path') is None or type(node['path']) is str) and all(type(node.get(k)) is bool for k in ('inside_tree', 'internal_idle', 'internal_physics', 'ordinary_idle', 'ordinary_physics')), 'BIRTH_NODE_TYPE')
        for field in ('wait_time', 'time_left'):
            value = born[field]
            require(set(value) == {'type', 'binary64_be'} and value.get('type') == 'float' and type(value.get('binary64_be')) is str and re.fullmatch(r'[0-9a-f]{16}', value['binary64_be']), 'BIRTH_TYPED_REAL_SHAPE')
        if node.get('inside_tree') is not False or node.get('path') is not None or node.get('class') != 'Timer' or any(node.get(k) is not False for k in ('internal_idle', 'internal_physics', 'ordinary_idle', 'ordinary_physics')): gaps.append('BIRTH_NOT_IMMEDIATE_OUTSIDE_TREE')
    return {'role': role, 'conditional_input_match': not gaps, 'gaps': sorted(set(gaps)), 'evidence': evidence, 'meaning': 'Local input premises only; not a SOURCE_DERIVED admission or real Root release.'}


class _VerifiedGate:
    def __init__(self, token, reasons, receipts):
        require(token is _TOKEN, 'INTERNAL_GATE_ONLY')
        self.reasons = tuple(reasons)
        self.receipts = receipts
        self.token = token


def verify_release(release_descriptor, io):
    require(canonical_path(release_descriptor['path']) == RELEASE_PATH, 'FRESH_ROOT_RELEASE_PATH')
    release = strict_json(read_regular(release_descriptor, 65536, io))
    require(release.get('schema') == ROOT_SCHEMA and release.get('action') == 'ONE_INITIAL_AUTOHIDE_PROJECTION' and release.get('output') == str(OUTPUT), 'ROOT_ACTION_SCHEMA')
    require(type(release.get('source_owner')) is dict and type(release.get('source_review')) is dict and type(release.get('review_owner')) is dict, 'REAL_REVIEW_DESCRIPTORS_REQUIRED')
    owner = strict_json(read_regular(release['source_owner'], 1048576, io))
    review = strict_json(read_regular(release['source_review'], 262144, io))
    ro = strict_json(read_regular(release['review_owner'], 1048576, io))
    require(review.get('schema') == REVIEW_SCHEMA and review.get('status') == REVIEW_STATUS and review.get('final_seal') is True and same(review.get('source_owner'), release['source_owner']), 'FINAL_SOURCE_AND_FUNCTIONAL_REVIEW_REQUIRED')
    require(type(ro.get('files')) is list and release['source_review'] in ro['files'], 'REVIEW_OWNER_JOIN')
    require(type(owner.get('files')) is list and release.get('context') in owner['files'], 'SOURCE_OWNER_CONTEXT_JOIN')
    module = [x for x in owner['files'] if canonical_path(x['path']) == Path(__file__).absolute()]
    require(len(module) == 1, 'SOURCE_OWNER_MODULE'); read_regular(module[0], 262144, io)
    require(canonical_path(release['context']['path']) == CONTEXT, 'CONTEXT_PATH')
    context = strict_json(read_regular(release['context'], 262144, io))
    require(context.get('schema') == 'phase420-fixed-source-context/1', 'CONTEXT_SCHEMA')
    for d in context['source_pins']: read_regular(d, 2097152, io)
    require(same(release.get('data'), context['data']), 'EXACT_FOUR_DATA_PATHS_AND_PINS')
    require(type(release['data']) is dict and set(release['data']) == {'index', 'slots', 'lineage', 'ui'}, 'FOUR_DATA_ONLY')
    require(same(review.get('owner_domain_rule'), context['owner_domain_rule']) and same(review.get('native_attribution_proposal'), context['native_attribution_proposal']), 'RULE_DISPOSITION_BINDING')
    reasons = []
    require(type(review.get('G01', {})) is dict and type(review.get('G02', {})) is dict, 'RULE_STATUS_TYPE')
    if review.get('G01', {}).get('status') != G01: reasons.append('OWNER_DOMAIN_CLOSURE_PENDING')
    if review.get('G02', {}).get('status') != G02: reasons.append('SOURCE_RUNTIME_ATTRIBUTION_PENDING')
    physical_path(OUTPUT.parent, False)
    require(not os.path.lexists(OUTPUT), 'OUTPUT_NOT_FRESH')
    return context, _VerifiedGate(_TOKEN, reasons, {'root': release_descriptor, 'review': release['source_review']}), release


def derive_autohide_pair(index, provenance, gate):
    require(type(gate) is _VerifiedGate and gate.token is _TOKEN, 'VERIFIED_RULE_GATE_REQUIRED')
    local = {role: check_autohide_role(index, provenance, role) for role in AUTO}
    results = []
    for field, phase, role in target_keys():
        reasons = ['RULE_DISABLED_OTHER_84']
        if field == 'Timer.private_left' and role in AUTO: reasons = list(gate.reasons) + local[role]['gaps']
        row = {'field_id': field, 'phase': phase, 'side_or_role': role, 'classification': 'MISSING', 'validation_result': 'UNPROVEN', 'proof_complete': False, 'reasons': reasons, 'original_index': index[(field, phase, role)]['index']}
        if not reasons:
            row.update(classification='SOURCE_DERIVED', validation_result='SUPPORTED', proof_complete=True, actual_value=dict(PRIVATE_MINUS_ONE), rule='AUTOHIDE_IMMEDIATE_CONSTRUCTOR_NO_START/1', source_receipts=gate.receipts, input_evidence=local[role]['evidence'])
        results.append(row)
    return results


def save_new(path, value):
    physical_path(path.parent, False)
    require(not os.path.lexists(path), 'OUTPUT_EXISTS')
    raw = (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode()
    require(len(raw) <= 2097152, 'OUTPUT_CAP')
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    try:
        offset = 0
        while offset < len(raw):
            written = os.write(fd, raw[offset:]); require(written > 0, 'SHORT_OUTPUT_WRITE'); offset += written
        os.fsync(fd)
    finally:
        os.close(fd)
    d = {'path': str(path), 'size': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}
    require(read_regular(d) == raw, 'OUTPUT_READBACK')
    return d


def run(release_descriptor):
    io = []
    context, gate, release = verify_release(release_descriptor, io)
    os.mkdir(OUTPUT, 0o700)  # Reserve once; failures remain. Never retry or repair.
    try:
        data = context['data']
        index = load_initial_index(read_regular(data['index'], 2097152, io))
        slot = project_slots(read_regular(data['slots'], 1048576, io), context['slot_table'])
        provenance = {'slots': slot, 'lineage': project_lineage(read_regular(data['lineage'], 67108864, io), slot), 'ui': project_ui(read_regular(data['ui'], 8388608, io))}
        results = derive_autohide_pair(index, provenance, gate)
        count = sum(x['classification'] == 'SOURCE_DERIVED' for x in results)
        report = {'schema': 'phase420-initial-partial-delta/1', 'status': 'PARTIAL_SOURCE_DERIVATION_PENDING_INDEPENDENT_ACTUAL_REVIEW' if count else 'BLOCKED_INITIAL_SOURCE_GAPS', 'targets': results, 'source_derived': count, 'remaining_missing': 88-count, 'unchanged_DIRECT_SUPPORTED': 1391, 'documentary_support_subset': 1371, 'fullschema': 'NOT_VALIDATED', 'genuine_bundle': False, 'King_admitted': False, 'actual_new_projection_calls': 1, 'old_SUT_schema_model_native_calls': 0, 'io': io}
        owned = [save_new(OUTPUT/'initial-provenance.json', provenance), save_new(OUTPUT/'delta-report.json', report)]
        save_new(OUTPUT/'owned-files.json', {'schema': 'phase420-actual-initial-projection-owned/1', 'files': owned})
        return {'status': report['status'], 'source_derived': count, 'remaining_missing': 88-count}
    except Exception as error:
        # Preserve first error and partial output. No automatic retry.
        save_new(OUTPUT/'first-error.json', {'schema': 'phase420-first-projection-error/1', 'error_type': type(error).__name__, 'message': str(error), 'io': io, 'retry': False})
        raise


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--release', required=True)
    parser.add_argument('--release-size', required=True, type=int)
    parser.add_argument('--release-sha256', required=True)
    args = parser.parse_args()
    result = run({'path': args.release, 'size': args.release_size, 'sha256': args.release_sha256})
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
