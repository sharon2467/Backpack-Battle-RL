"""Saved-artifact KingBuff pair overlay. Author must never import/run this module."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat

REPO = Path('/workspace/python-original-engine/repo')
CONTEXT = REPO / 'data/phase426-king-buff-overlay-source/context.json'
RELEASE_PATH = REPO / 'data/phase426-root-saved-overlay-release/release.json'
OUTPUT_REL = 'data/phase426-king-buff-overlay-first-001'
OUTPUT = REPO / OUTPUT_REL
ROOT_SCHEMA = 'root426-saved-kingbuff-overlay/1'
REVIEW_SCHEMA = 'independent427-kingbuff-overlay-source-functional-review/1'
REVIEW_STATUS = 'INDEPENDENT427_KINGBUFF_OVERLAY_SOURCE_AND_FUNCTIONAL_ACCEPTED_ROOT_PENDING'
PHASES = ('pre_prepare', 'pre_activate')
ROLE, TIMER, KING = 'king_buff:P:12', '81717', '81679'
SCENE = 'res://Items/Exclusive/KingGoobert.tscn'
SCRIPT = 'res://Items/Exclusive/KingGoobert.gd'
RULE = 'SCENE_TIMER_CONFIGURED_NO_START/1'
PRIVATE_MINUS_ONE = {'type':'float','binary64_be':'bff0000000000000'}
A4_KEYS = {('Timer.private_left', p, r) for p in PHASES for r in ('king_hide:P:12','king_drag:P:12')}
PAIR_KEYS = {('Timer.private_left', p, ROLE) for p in PHASES}
_TOKEN = object()
PUBLIC_FIELDS = [('Timer.process_mode', 0), ('Timer.wait_time', {'type': 'float', 'binary64_be': '3ff0000000000000'}), ('Timer.time_left', {'type': 'float', 'binary64_be': '0000000000000000'}), ('Timer.one_shot', True), ('Timer.autostart', False), ('Timer.paused', False), ('Timer.stopped', True), ('Timer.node.native_id', '81717'), ('Timer.node.role', 'king_buff:P:12'), ('Timer.node.path', '/root/Main/Player/King Goobert/BuffTimer'), ('Timer.node.name', 'BuffTimer'), ('Timer.node.class', 'Timer'), ('Timer.node.positions', [-1, 18, 3, 14, 7]), ('Timer.node.priority', 0), ('Timer.node.inside_tree', True), ('Timer.node.ordinary_physics', False), ('Timer.node.internal_physics', False), ('Timer.node.ordinary_idle', False), ('Timer.node.internal_idle', False)]
BIRTH = {'autostart': False, 'node': {'class': 'Timer', 'inside_tree': False, 'internal_idle': False, 'internal_physics': False, 'name': 'BuffTimer', 'native_id': '81717', 'ordinary_idle': False, 'ordinary_physics': False, 'path': None, 'positions': [-1, 7], 'priority': 0, 'role': None}, 'one_shot': True, 'paused': False, 'process_mode': 0, 'stopped': True, 'time_left': {'binary64_be': '0000000000000000', 'type': 'float'}, 'wait_time': {'binary64_be': '3ff0000000000000', 'type': 'float'}}

class Rejected(ValueError):
    pass


def require(condition, reason):
    if not condition:
        raise Rejected(reason)

def integer(value, minimum=0):
    return type(value) is int and value >= minimum

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


def row_key(row):
    require(type(row) is dict and all(type(row.get(k)) is str for k in ('field_id', 'phase', 'side_or_role')), 'TARGET_KEY_TYPE')
    return row['field_id'], row['phase'], row['side_or_role']


def validate_a4(delta, index):
    require(type(delta) is dict and delta.get('schema') == 'phase420-initial-partial-delta/1', 'A4_SCHEMA')
    require(delta.get('status') == 'PARTIAL_SOURCE_DERIVATION_PENDING_INDEPENDENT_ACTUAL_REVIEW', 'A4_ORIGINAL_STATUS')
    for key, expected in [('source_derived', 4), ('remaining_missing', 84), ('unchanged_DIRECT_SUPPORTED', 1391)]:
        require(type(delta.get(key)) is int and delta[key] == expected, 'A4_COUNTS')
    require(delta.get('fullschema') == 'NOT_VALIDATED' and delta.get('King_admitted') is False and delta.get('genuine_bundle') is False, 'A4_ADMISSION_LIMITS')
    rows = delta.get('targets')
    require(type(rows) is list and len(rows) == 88, 'A4_TARGET_COUNT')
    seen, supported = set(), set()
    for row in rows:
        key = row_key(row)
        require(key not in seen and key in index and key in set(target_keys()), 'A4_KEY_DOMAIN')
        seen.add(key)
        require(type(row.get('original_index')) is int and row['original_index'] == index[key]['index'], 'A4_INDEX_JOIN')
        require(type(row.get('proof_complete')) is bool, 'A4_PROOF_TYPE')
        if key in A4_KEYS:
            require(row.get('classification') == 'SOURCE_DERIVED' and row.get('validation_result') == 'SUPPORTED' and row['proof_complete'] is True and same(row.get('actual_value'), PRIVATE_MINUS_ONE), 'A4_ACCEPTED_VALUE')
            require(row.get('rule') == 'AUTOHIDE_IMMEDIATE_CONSTRUCTOR_NO_START/1' and type(row.get('source_receipts')) is dict and type(row.get('input_evidence')) is list and len(row['input_evidence']) == 34, 'A4_EXISTING_PROOF')
            supported.add(key)
        else:
            require(row.get('classification') == 'MISSING' and row.get('validation_result') == 'UNPROVEN' and row['proof_complete'] is False and 'actual_value' not in row, 'A4_OTHER_MISSING')
    require(seen == set(target_keys()) and supported == A4_KEYS, 'A4_EXACT_UNION')
    return rows


def collect_kingbuff_initial(index, provenance):
    # Bounded saved evidence only. No private countdown value or admission here.
    gaps, evidence = [], []
    def get(field, phase, ordinal):
        found = index.get((field, phase, ROLE))
        if found is None:
            gaps.append('MISSING_' + phase + '_' + field); return None
        row = found['row']
        require(found['index'] == ordinal and row_key(row) == (field, phase, ROLE), 'SUPPORT_ORDINAL_KEY')
        if row.get('classification') == 'MISSING':
            require(row.get('validation_result') == 'UNPROVEN' and row.get('proof_complete') is False and 'actual_value' not in row, 'MISSING_SUPPORT_SHAPE')
            gaps.append('UNPROVEN_' + phase + '_' + field); return None
        require(row.get('classification') == 'DIRECT_OBSERVATION' and row.get('validation_result') == 'SUPPORTED' and row.get('proof_complete') is True and 'actual_value' in row, 'DIRECT_SUPPORT_REQUIRED')
        require(row['actual_value'] is not None, 'NULL_DIRECT_SUPPORT_VALUE')
        refs = row.get('input_refs')
        require(type(refs) is list and len(refs) == 1 and type(refs[0]) is dict, 'SUPPORT_REFERENCE_SHAPE')
        ref = refs[0]
        if field.startswith('Timer.lineage.'):
            require(ref.get('file') == 'king-input-facts.json' and ref.get('pointer') == '/timers/' + ROLE + '/lineage/' + field.rsplit('.', 1)[1], 'FACT_REFERENCE')
        else:
            require(ref.get('file') == 'observer7-input.jsonl' and type(ref.get('line')) is int and ref['line'] == {'pre_prepare': 1, 'pre_activate': 4}[phase] and type(ref.get('sequence')) is int and ref['sequence'] == {'pre_prepare': 138, 'pre_activate': 1231}[phase] and ref.get('native_owner') == TIMER and ref.get('pointer') == '/payload/nodes/57/timer/' + field.removeprefix('Timer.').replace('.', '/'), 'CHECKPOINT_REFERENCE')
        evidence.append({'index': ordinal, 'field': field, 'phase': phase, 'value': row['actual_value'], 'input_ref': ref})
        return row['actual_value']
    def compare(value, expected, label):
        require(type(value) is type(expected), 'VALUE_TYPE_' + label)
        if type(expected) is dict:
            if expected.get('type') == 'float':
                require(set(value) == {'type', 'binary64_be'} and value.get('type') == 'float' and type(value.get('binary64_be')) is str and re.fullmatch(r'[0-9a-f]{16}', value['binary64_be']), 'NATIVE_FLOAT_SHAPE_' + label)
            require(set(value) <= set(expected), 'VALUE_EXTRA_KEYS_' + label)
            for k, v in expected.items():
                if k not in value: gaps.append('MISSING_' + label + '_' + k)
                else: compare(value[k], v, label + '_' + k)
        elif type(expected) is list:
            require(len(value) == len(expected), 'VALUE_LIST_SHAPE_' + label)
            for i, (a, b) in enumerate(zip(value, expected)): compare(a, b, label + '_' + str(i))
        elif not same(value, expected):
            gaps.append('UNSUPPORTED_' + label)
    for phase, start in [('pre_prepare', 615), ('pre_activate', 1287)]:
        for offset, (field, expected) in enumerate(PUBLIC_FIELDS):
            value = get(field, phase, start + offset)
            if value is not None:
                if field in ('Timer.node.native_id', 'Timer.node.role', 'Timer.node.class', 'Timer.node.name', 'Timer.node.path'):
                    require(same(value, expected), 'CONFLICTING_TIMER_IDENTITY')
                compare(value, expected, phase + '_' + field)
    facts = {name: get('Timer.lineage.' + name, 'pre_activate', 1370 + i) for i, name in enumerate(('timer_id', 'owner_id', 'kind', 'starts', 'stops', 'birth'))}
    for name, ident in [('timer_id', TIMER), ('owner_id', KING)]:
        if facts[name] is not None: require(type(facts[name]) is str and facts[name] == ident, 'BIRTH_OWNER_TIMER_CONFLICT')
    if facts['kind'] is not None: compare(facts['kind'], 'King.scene.instance', 'SCENE_BIRTH_KIND')
    for name in ('starts', 'stops'):
        if facts[name] is not None:
            require(integer(facts[name]), 'LIFETIME_COUNTER_TYPE')
            if facts[name] != 0: gaps.append('NONZERO_LIFETIME_' + name)
    if facts['birth'] is not None:
        born = facts['birth']
        require(type(born) is dict, 'BIRTH_TYPE')
        if 'node' in born:
            require(type(born['node']) is dict, 'BIRTH_NODE_TYPE')
            for name, value in [('native_id', TIMER), ('name', 'BuffTimer'), ('class', 'Timer')]:
                if name in born['node']: require(same(born['node'][name], value), 'BIRTH_NODE_IDENTITY')
        compare(born, BIRTH, 'BIRTH')
    require(type(provenance) is dict, 'PROVENANCE_TYPE')
    slot = provenance.get('slots')
    if slot is None: gaps.append('SAVED_SLOT_MISSING')
    else:
        require(type(slot) is dict and type(slot.get('binding')) is dict, 'SLOT_SHAPE')
        binding = slot['binding']
        for k, v in {'instance_id':'P:12','native_id':KING,'descriptor_id':'12018','character_id':'47611','inventory_id':'48429','input_slot':12,'inventory_encounter_index':12,'item_index':{'type':'int','decimal':'262'}}.items():
            require(k in binding and same(binding[k], v), 'SELECTED_SLOT_CONFLICT')
        require(type(slot.get('row')) is int and slot['row'] == 12 and slot.get('pointer') == '/actual_bindings/12', 'SLOT_POINTER')
    lineage = provenance.get('lineage')
    if lineage is None: gaps.append('SAVED_LINEAGE_MISSING')
    else:
        require(type(lineage) is dict and type(lineage.get('selected')) is list and type(lineage.get('gaps')) is list, 'LINEAGE_SHAPE')
        if lineage['gaps']: gaps.append('SAVED_LINEAGE_GAPS')
        rows = lineage['selected']
        require(len(rows) <= 3, 'DUPLICATE_OR_FOREIGN_LINEAGE')
        if len(rows) != 3: gaps.append('SCENE_READY_PAIR_MISSING')
        else:
            for row, seq, line, site, edge in zip(rows, (36,37,38), (37,38,39), ('Items/ItemDescriptor.gd::instantiate','Items/Item.gd::_ready','Items/Item.gd::_ready'), ('scene_instance','enter','return_implicit')):
                require(type(row) is dict and type(row.get('sequence')) is int and row['sequence'] == seq and type(row.get('line')) is int and row['line'] == line and row.get('site') == site and row.get('edge') == edge, 'SCENE_READY_ORDER')
                require(type(row.get('subject')) is dict and row['subject'].get('type') == 'native_ref' and row['subject'].get('native_id') == KING and type(row.get('payload')) is dict, 'LINEAGE_KING_ID')
            scene = rows[0]['payload']
            require(scene.get('item_id') == KING and scene.get('descriptor_id') == '12018' and scene.get('scene_path') == SCENE and scene.get('pooled') is False and same(scene.get('item_index'), {'type':'int','decimal':'262'}), 'SCENE_FRESH_DOMAIN')
            require(same(rows[2]['payload'].get('return_value'), {'type':'null'}), 'READY_NORMAL_RETURN')
    ui = provenance.get('ui')
    if ui is None: gaps.append('SAVED_UI_MISSING')
    else:
        require(type(ui) is dict and type(ui.get('bind')) is list, 'UI_BIND_SHAPE')
        require(len(ui['bind']) <= 1, 'UI_DUPLICATE_BIND')
        if not ui['bind']: gaps.append('UI_BIND_MISSING')
        else:
            b = ui['bind'][0]
            require(type(b) is dict and type(b.get('payload')) is dict and b.get('kind') == 'bind' and b.get('site') == 'scene_instance' and type(b.get('sequence')) is int and b['sequence'] == 1029, 'UI_BIND_IDENTITY')
            p = b['payload']
            require(p.get('item_id') == KING and p.get('script') == SCRIPT and p.get('scene') == SCENE and p.get('pooled') is False and p.get('inside_tree') is False and type(p.get('generation')) is int and p['generation'] == 1, 'UI_FRESH_SCENE_DOMAIN')
        roles = ui.get('roles')
        if roles is None: gaps.append('UI_ROLES_MISSING')
        else:
            require(type(roles) is dict and roles.get('kind') == 'roles' and roles.get('site') == 'configure' and type(roles.get('sequence')) is int and roles['sequence'] == 1076 and type(roles.get('payload')) is dict, 'UI_FIRST_ROLES')
            require(same(roles['payload'].get('kings'), [{'item_id':KING,'role':'P:12'}]) and roles['payload'].get('using_controller') is False, 'UI_SELECTED_ROLE_CONFLICT')
    return {'role':ROLE,'gaps':sorted(set(gaps)),'support':evidence,'saved_provenance_used':True,'meaning':'Conditional input evidence only; no private value or target admission.'}


class _VerifiedGate:
    def __init__(self, token, receipts):
        require(token is _TOKEN, 'INTERNAL_GATE_ONLY')
        self.token, self.receipts = token, receipts


def verify_kingbuff_release(release_descriptor, io):
    require(canonical_path(release_descriptor['path']) == RELEASE_PATH, 'FRESH_ROOT_RELEASE_PATH')
    r = strict_json(read_regular(release_descriptor, 65536, io))
    require(type(r) is dict and r.get('schema') == ROOT_SCHEMA and r.get('action') == 'ONE_SAVED_KINGBUFF_PAIR_OVERLAY' and r.get('output') == OUTPUT_REL, 'ROOT_ACTION_SCHEMA')
    owner = strict_json(read_regular(r['source_owner'], 1048576, io))
    review = strict_json(read_regular(r['source_review'], 262144, io))
    review_owner = strict_json(read_regular(r['review_owner'], 1048576, io))
    require(review.get('schema') == REVIEW_SCHEMA and review.get('status') == REVIEW_STATUS and review.get('final_seal') is True and same(review.get('source_owner'), r['source_owner']), 'FINAL427_REVIEW_REQUIRED')
    require(type(review_owner.get('files')) is list and r['source_review'] in review_owner['files'], 'REVIEW_OWNER_JOIN')
    require(type(owner.get('files')) is list and r['context'] in owner['files'] and canonical_path(r['context']['path']) == CONTEXT, 'SOURCE_CONTEXT_JOIN')
    modules = [d for d in owner['files'] if canonical_path(d['path']) == Path(__file__).absolute()]
    require(len(modules) == 1, 'SOURCE_MODULE_JOIN'); read_regular(modules[0], 262144, io)
    c = strict_json(read_regular(r['context'], 262144, io))
    require(c.get('schema') == 'phase426-saved-overlay-context/1' and same(r.get('data'), c['data']) and set(c['data']) == {'index','provenance','a4'}, 'EXACT_SAVED_DATA_ONLY')
    require(same(review.get('context'), r['context']) and same(review.get('design_review'), c['controls']['design_review']) and same(review.get('root423'), c['controls']['root423']), 'FINAL427_RULE_CONTEXT_BINDINGS')
    for d in c['source_pins']: read_regular(d, 2097152, io)
    ctl = {k: strict_json(read_regular(d, 262144, io)) for k,d in c['controls'].items()}
    design = ctl['design_review']
    require(design.get('schema') == 'independent425-king-buff-scene-rule-design-review/1' and design.get('status') == 'INDEPENDENT425_KINGBUFF_TWO_TARGET_SCENE_RULE_DESIGN_ACCEPTED_ROOT_PENDING' and design.get('final_seal') is True, 'ACCEPTED425_RULE_REQUIRED')
    require(design.get('scope', {}).get('rule_family') == RULE and design['scope'].get('role') == ROLE and design['scope'].get('native_timer') == TIMER and design['scope'].get('owner') == KING and design.get('native_semantics_disposition', {}).get('accepted_for_this_bounded_design') is True, 'SCENE_NATIVE_RULE_DISPOSITION')
    require(c['controls']['design_review'] in ctl['design_owner']['files'], 'DESIGN_OWNER_JOIN')
    root, actual = ctl['root423'], ctl['actual423']
    require(root.get('schema') == 'root423-four-initial-target-chain-acceptance/1' and root.get('status') == 'ACCEPTED_FOUR_TARGET_CHAINS_ONE_AUTOHIDE_RULE_FAMILY' and same(root.get('review'), c['controls']['actual423']) and same(root.get('review_owner'), c['controls']['actual423_owner']), 'ROOT423_ACCEPTANCE')
    require(c['controls']['actual423'] in ctl['actual423_owner']['files'] and actual.get('status') == 'INDEPENDENT423_FOUR_AUTOHIDE_INITIAL_TARGET_CHAINS_ACCEPTED_ROOT_PENDING' and actual.get('final_seal') is True and same(actual.get('actual_projection_output_owner'), c['controls']['a4_owner']), 'ACTUAL423_OUTPUT_JOIN')
    for name in ('a4','provenance'):
        require(c['data'][name] in ctl['a4_owner']['files'], 'SAVED_OUTPUT_OWNER_JOIN')
    physical_path(OUTPUT.parent, False); require(not os.path.lexists(OUTPUT), 'OUTPUT_NOT_FRESH')
    return c, _VerifiedGate(_TOKEN, {'root':release_descriptor,'implementation_review':r['source_review'],'design_review':c['controls']['design_review'],'root423':c['controls']['root423']})


def derive_kingbuff_pair(index, a4, evidence, gate):
    require(type(gate) is _VerifiedGate and gate.token is _TOKEN, 'VERIFIED_GATE_REQUIRED')
    require(type(evidence) is dict and evidence.get('role') == ROLE and type(evidence.get('gaps')) is list and all(type(x) is str for x in evidence['gaps']) and type(evidence.get('support')) is list, 'EVIDENCE_SHAPE')
    rows = validate_a4(a4, index)
    # Evidence is recomputed from saved inputs by run, never a public proof Boolean.
    if not evidence['gaps']:
        require(len(evidence['support']) == 44 and len({(x['field'], x['phase']) for x in evidence['support']}) == 44, 'COMPLETE_PAIR_SUPPORT_REQUIRED')
    result = []
    for row in rows:
        key = row_key(row)
        if key not in PAIR_KEYS:
            result.append(row); continue
        new = dict(row)
        new['reasons'] = list(evidence['gaps'])
        if not evidence['gaps']:
            new.update(classification='SOURCE_DERIVED', validation_result='SUPPORTED', proof_complete=True, actual_value=dict(PRIVATE_MINUS_ONE), rule=RULE, source_receipts=gate.receipts, input_evidence=evidence['support'])
        result.append(new)
    require({row_key(x) for x in result} == set(target_keys()) and len(result) == 88, 'OVERLAY_EXACT_UNION')
    new_count = sum(x['classification'] == 'SOURCE_DERIVED' for x in result if row_key(x) in PAIR_KEYS)
    require(new_count in (0,2), 'PAIR_ATOMICITY')
    for before, after in zip(rows, result):
        if row_key(before) not in PAIR_KEYS: require(same(before, after), 'OLD_ROW_CHANGED')
    require(sum(x['classification'] == 'SOURCE_DERIVED' for x in result) == 4 + new_count, 'NO_DOUBLE_COUNT')
    return result, new_count


def run(release_descriptor):
    io = []
    context, gate = verify_kingbuff_release(release_descriptor, io)
    os.mkdir(OUTPUT, 0o700)
    try:
        d = context['data']
        index = load_initial_index(read_regular(d['index'], 2097152, io))
        provenance = strict_json(read_regular(d['provenance'], 262144, io))
        a4 = strict_json(read_regular(d['a4'], 262144, io))
        validate_a4(a4, index)
        evidence = collect_kingbuff_initial(index, provenance)
        rows, count = derive_kingbuff_pair(index, a4, evidence, gate)
        report = {'schema':'phase426-kingbuff-overlay/1','status':'KINGBUFF_PAIR_CANDIDATES_PENDING_INDEPENDENT_ACTUAL_REVIEW' if count else 'BLOCKED_KINGBUFF_SOURCE_GAPS','targets':rows,'new_kingbuff_candidates':count,'prior_accepted_source_derived':4,'source_derived_total':4+count,'remaining_missing':84-count,'unchanged_DIRECT_SUPPORTED':1391,'direct_index_reference':d['index'],'accepted_a4_reference':d['a4'],'provenance_reference':d['provenance'],'fullschema':'NOT_VALIDATED','genuine_bundle':False,'King_admitted':False,'actual_saved_overlay_calls':1,'old_parser_SUT_schema_model_native_calls':0,'io':io}
        files = [save_new(OUTPUT/'proof-evidence.json',evidence), save_new(OUTPUT/'overlay-report.json',report)]
        save_new(OUTPUT/'owned-files.json',{'schema':'phase426-saved-overlay-owned/1','files':files})
        return {'status':report['status'],'new_kingbuff_candidates':count,'remaining_missing':84-count}
    except Exception as error:
        save_new(OUTPUT/'first-error.json',{'schema':'phase426-first-overlay-error/1','error_type':type(error).__name__,'message':str(error),'io':io,'retry':False})
        raise


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--release',required=True)
    parser.add_argument('--release-size',required=True,type=int)
    parser.add_argument('--release-sha256',required=True)
    args = parser.parse_args()
    result = run({'path':args.release,'size':args.release_size,'sha256':args.release_sha256})
    print(json.dumps(result,sort_keys=True))


if __name__ == '__main__':
    main()
