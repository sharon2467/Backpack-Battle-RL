"""Case029 lawful INPUT-only bridge. No schema load/default request at import."""
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
import sys
import types
from phase511_initial_receipt import build_initial_receipt,value_index

REPO=Path(__file__).resolve().parents[1]
STATUS='INPUT_ONLY_NOT_RUNTIME_VALIDATED'
CASE='NATIVE-029-WHELP-FAMILY-A'
RUN='original029-whelp-family-A-single-001'
PROFILE='pure-combat-whelp-family-A-captured/1'
RUNTIME_SCHEMA='native-v8-pure-combat-runtime-input/whelp-family-1'
RUNTIME_KEYS=('schema','mode','profile_id','checkpoint','environment','nodes','timer_initial','initial_items','initial_characters','prepare_order','activate_order','terminal_profile','frame_clock','processing_nodes')
STACK_NAMES={100:'Block',101:'Lucky',102:'Regeneration',103:'Vampirism',104:'Spikes',105:'Mana',106:'Empower',107:'Heat',108:'Poison',109:'Blind',110:'Cold'}
ZERO_BITS='0000000000000000'
DEFERRED=('actual same-instance business prepare equivalence','ordinary callbacks/transform/selected RNG noninterference','candidate interface and actual INPUT acceptance','one-model output/strict8 mapping')
LAWFUL=('fixture.json','player_fixture.json','observer7-input.jsonl','observer7-lineage.jsonl','observer7-metadata.jsonl','observer7-primitives.jsonl','king-clock-checkpoint.json','king-clock-passes.jsonl','king-input-facts.json','king-ui-authority.jsonl','king-rng-checkpoint.json','king-slot-bindings.json')
DEFAULT_REQUEST=None
SCHEMA_PIN = {'path': 'data/phase502-whelp-observer-source-v4/schema/phase502_whelp_observer_schema.py', 'size': 197522, 'sha256': 'd5531e3e9b119f0309140cb50dff2c7f545abb5ec3500d488bde29cacdb8f193'}
FIXED_SOURCE_BINDINGS = {'schema_module': {'path': 'data/phase502-whelp-observer-source-v4/schema/phase502_whelp_observer_schema.py', 'size': 197522, 'sha256': 'd5531e3e9b119f0309140cb50dff2c7f545abb5ec3500d488bde29cacdb8f193'}, 'observer_tuple': {'path': 'data/phase502-whelp-observer-source-v4/source-tuple.json', 'size': 2001, 'sha256': '026877626166fe632c08bd3cba28aec191561373b2167f3c6d15d1f1fac86658'}, 'observer_owner': {'path': 'data/phase502-whelp-observer-source-v4/source-owner.json', 'size': 27181, 'sha256': '48a578c6d8f9f2189e5241432d6e0b14fed8a5d4fda948ca73b0ab62dd6c8d8f'}, 'observer_acceptance': {'path': 'data/phase503-independent-final-acceptance/review.json', 'size': 7550, 'sha256': '468ec5cb36e2d11f0a1a7e8160eca4d806b5fe10bb92ce90ccf2733ea1cd3db4'}, 'candidate_freeze': {'path': 'data/phase505-captured-nonking-source-v3/candidate-source-freeze.json', 'size': 4729, 'sha256': 'e3f2a86713ef097cae77858f0868fdd70b7487cdeadeaa7fcf11ebb184d550ad'}, 'candidate_interface_acceptance': {'path': 'data/phase506-independent-final-acceptance/review.json', 'size': 8697, 'sha256': '7199a5dd9cbd52a99ff7a7ebf6d2e01bd88c7c92990799019093de688dbc03a0'}, 'native_timer_source_rule': {'path': 'data/phase438-native-timer-source-review/source-ledger.json', 'size': 2689, 'sha256': 'cb88ff66ce1151338f453b3f7f08811f87d80f1e96a7a5a9aa4e8ad656e860b0'}, 'character_source_rule': {'path': 'data/phase438-root-character8-acceptance/acceptance.json', 'size': 1482, 'sha256': 'c4fc10ff4196083eab5c3f1169bfa00bb080712ab49cb2947bcebbc0b60f28a5'}, 'timer_rule_acceptance': {'path': 'data/phase439-root-timer64-acceptance/acceptance.json', 'size': 2052, 'sha256': 'c32a013aa58598fd15a6658c220dba67073062a4e3f022f84c5b8b0408d25b78'}, 'receipt_source': {'path': 'tests/phase511_initial_receipt.py', 'size': 16790, 'sha256': 'b504aef3f5c60af9d95a03aa0e975334ac9caa7723a3622badba6aec4e7f7b68'}}
SOURCE_RULES = {'cooldown_predicate': {'descriptor': {'path': 'data/phase511-input-bridge-source/branch-source-rule.json', 'size': 2161, 'sha256': 'c735b7d516734fe241f2b6fea818c1c25764ffd23061a3d239e833cfe7bf4551'}, 'predicate': 'Game.isBelowLeague(Game.Leagues.Master) or Game.curMode == Game.Mode.Lobbies', 'basis': 'NEW_SITE_WITNESS_PLUS_FIXED_SOURCE_CLOSURE'}, 'initial': {'domain': 'accepted G02 and Character default/pre-ready-call closure applied to actual new32/2cut objects', 'native_rule': {'path': 'data/phase438-native-timer-source-review/source-ledger.json', 'size': 2689, 'sha256': 'cb88ff66ce1151338f453b3f7f08811f87d80f1e96a7a5a9aa4e8ad656e860b0'}, 'character_rule': {'path': 'data/phase438-root-character8-acceptance/acceptance.json', 'size': 1482, 'sha256': 'c4fc10ff4196083eab5c3f1169bfa00bb080712ab49cb2947bcebbc0b60f28a5'}, 'timer_acceptance': {'path': 'data/phase439-root-timer64-acceptance/acceptance.json', 'size': 2052, 'sha256': 'c32a013aa58598fd15a6658c220dba67073062a4e3f022f84c5b8b0408d25b78'}, 'limits': 'Historical domain/migration limits retained. No old row/native-ID/private value or all-fresh assumption. Actual birth/no-start ledger only for2invu, no fabricated ledger for30others.'}}

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

def source_value(index, field, phase, role):
    ident = (field, phase, role)
    require(ident in index, 'EMITTED_VALUE_SOURCE_MISSING_' + ':'.join(ident))
    ordinal, row = index[ident]
    return deepcopy(row['actual_value']), {'file': 'initial-receipt.json', 'pointer': f'/values/{ordinal}/actual_value',
        'classification': row['classification'], 'rule': row['rule'], 'key': list(ident), 'input_refs': deepcopy(row['input_refs'])}

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

def authenticate_request(request_raw,request_pin,context_raw):
    require(type(request_pin) is dict and set(request_pin)=={'path','size','sha256'},'EXPLICIT_ROOT_REQUEST_PIN')
    canonical(request_pin['path'])
    require(type(request_pin['size']) is int and type(request_pin['sha256']) is str and re.fullmatch('[0-9a-f]{64}',request_pin['sha256']) is not None,'ROOT_REQUEST_PIN_TYPES')
    require(type(request_raw) is bytes and len(request_raw)==request_pin['size'] and hashlib.sha256(request_raw).hexdigest()==request_pin['sha256'],'ROOT_SELECTED_REQUEST_BYTES')
    request=strict_json(request_raw)
    require(type(request) is dict and set(request)=={'schema','case_id','run_name','source_context','input_descriptors','models_allowed','expected_allowed'},'CLOSED_ROOT_REQUEST')
    require(request['schema']=='phase511-root-bound-input-request/1' and request['case_id']==CASE and request['run_name']==RUN,'FIXED_NEW_CASE_RUN')
    require(all(type(request[k]) is int and request[k]==0 for k in ('models_allowed','expected_allowed')),'REQUEST_STRICT_INT0')
    cp=request['source_context']
    require(type(cp) is dict and set(cp)=={'path','size','sha256'},'EXPLICIT_CONTEXT_PIN')
    canonical(cp['path'])
    require(type(cp['size']) is int and type(cp['sha256']) is str and type(context_raw) is bytes and len(context_raw)==cp['size']
            and hashlib.sha256(context_raw).hexdigest()==cp['sha256'],'ROOT_BOUND_CONTEXT_BYTES')
    pins=request['input_descriptors']
    require(type(pins) is dict and set(pins)==set(LAWFUL),'EXACT12_ROOT_INPUT_PINS_REQUIRED')
    parents=set()
    for name,p in pins.items():
        require(type(p) is dict and set(p)=={'path','size','sha256'},'INPUT_PIN_SHAPE')
        require(type(p['size']) is int and 0<p['size']<=4194304 and type(p['sha256']) is str and re.fullmatch('[0-9a-f]{64}',p['sha256']) is not None,'INPUT_PIN_TYPES')
        path=canonical(p['path']);require(path.name==name,'LAWFUL_LEAF_NAME');parents.add(str(path.parent))
    require(len(parents)==1,'ONE_EXPLICIT_LAWFUL_INPUT_ROOT')
    context=strict_json(context_raw)
    require(type(context) is dict and set(context)=={'schema','case_id','profile','runtime_schema','schema_module','fixed_source_bindings','source_pins','source_rules','prepared_gate'},'CLOSED_SOURCE_CONTEXT')
    require(context['schema']=='phase511-fixed-source-context/1' and context['case_id']==CASE and context['profile']==PROFILE
            and context['runtime_schema']==RUNTIME_SCHEMA and same(context['schema_module'],SCHEMA_PIN),'EXACT511_SOURCE_CONTEXT')
    require(same(context['fixed_source_bindings'],FIXED_SOURCE_BINDINGS) and same(context['source_rules'],SOURCE_RULES),'NO_CALLER_PROOF_FLAGS_OR_SOURCE_DRIFT')
    require(context['prepared_gate']=='EXTERNAL_SAME_INSTANCE_BUSINESS_PREPARE_GATE_REQUIRED_BEFORE_ACTIVATION','PREPARED_GATE_NOT_CERTIFIED_BY_BRIDGE')
    require(type(context['source_pins']) is list and context['source_pins'],'EXPLICIT_SOURCE_PINS')
    allowed={p['path'] for p in FIXED_SOURCE_BINDINGS.values()} | {'tests/phase511_input_bridge.py','data/phase511-input-bridge-source/branch-source-rule.json','data/phase511-input-bridge-source/abi.json'}
    require(len(context['source_pins'])==len(allowed) and {p['path'] for p in context['source_pins']}==allowed,'CLOSED_SOURCE_PIN_PATHS_NO_EXPECTED')
    actual={p['path']:p for p in context['source_pins']}
    for p in FIXED_SOURCE_BINDINGS.values():require(same(actual[p['path']],p),'FIXED_SOURCE_PIN_IDENTITY')
    return request,context


def verify_raw_inputs(raw12,request):
    require(type(raw12) is dict and set(raw12)==set(LAWFUL),'EXACT12_LAWFUL_BYTES')
    for name,p in request['input_descriptors'].items():
        require(type(raw12[name]) is bytes and len(raw12[name])==p['size']
                and hashlib.sha256(raw12[name]).hexdigest()==p['sha256'],'ROOT_PINNED_INPUT_'+name)
    return deepcopy(request['input_descriptors'])


def load_schema(schema_raw):
    require(type(schema_raw) is bytes and len(schema_raw)==SCHEMA_PIN['size'] and hashlib.sha256(schema_raw).hexdigest()==SCHEMA_PIN['sha256'],'EXACT_PINNED502_SCHEMA_BYTES')
    name='_phase511_exact502_schema';module=types.ModuleType(name);module.__file__=SCHEMA_PIN['path']
    require(name not in sys.modules,'NO_CACHED_SCHEMA_SHORTCUT')
    sys.modules[name]=module
    try:
        exec(compile(schema_raw,module.__file__,'exec'),module.__dict__)
        require(module.VERSION=='7-whelp-family-A-502' and module.PROFILE=='observer7-whelp-family-A-native-tape/1'
                and len(module.FIXED_ROLES)==29 and module.DESCRIPTOR_IDS==frozenset({1,11,22,23,64,164,197,199,201}),'EXACT_ZERO_KING_SCHEMA_DOMAIN')
        return module
    finally:
        del sys.modules[name]


def decode_lawful12(raw12,request,schema):
    pins=verify_raw_inputs(raw12,request)
    decoded=schema._transport_only_decode({name:raw12[name] for name in schema.INPUT_FILES})
    for name in schema.CHANNEL_FILES:
        for row in decoded[name]:schema.validate_record(row)
    binding=schema.validate_binding_carrier(raw12['king-slot-bindings.json'],schema.BINDING_FIXED_PLAN)
    aliases=schema.join_binding_provenance(decoded,binding,schema.BINDING_SOURCE_CONTRACT)
    return decoded,aliases,{'input_descriptors':pins,'binding_join':aliases,'scope':'ROOT_PINNED_BYTES_TRANSPORT_TYPED_RELATION_ONLY','full_FX_UI_gate_called':False}


def derive_branch_witness(decoded,aliases):
    selected=[];opponent=[]
    for line,row in enumerate(decoded['observer7-primitives.jsonl'],1):
        if not row['site'].startswith('Items/Item.gd::adjustCooldown:'):continue
        label=row['payload']['label'];require(label.startswith('cooldown:'),'COOLDOWN_SOURCE_LABEL')
        role=label[len('cooldown:'):]
        require(role in aliases['role_to_native'] and re.fullmatch('[PO]:[0-9]+',role) is not None,'COOLDOWN_SELECTED_ALIAS')
        site=row['site']
        require(site in ('Items/Item.gd::adjustCooldown:belowMasterOpponent','Items/Item.gd::adjustCooldown:other'),'EXACT_TWO_SOURCE_BRANCHES')
        if role.startswith('P:'):require(site.endswith(':other'),'PLAYER_COOLDOWN_BRANCH')
        witness={'file':'observer7-primitives.jsonl','line':line,'sequence':row['sequence'],'role':role,
                 'native_owner':aliases['role_to_native'][role],'site':site,'startup':same(row['stamp']['combat_time'],{'type':'float','binary64_be':ZERO_BITS})}
        selected.append(witness)
        if role.startswith('O:'):opponent.append(witness)
    require(opponent and any(row['startup'] for row in opponent),'NEW_OPPONENT_STARTUP_BRANCH_REQUIRED')
    sites={row['site'] for row in opponent};require(len(sites)==1,'NEW_PREDICATE_BRANCH_NOT_STABLE')
    value=next(iter(sites)).endswith(':belowMasterOpponent')
    return {'schema':'phase511-new-input-predicate-witness/1','field':'fixture.below_master','type':'BOOL','value':value,
            'witnesses':selected,'source_rule':deepcopy(SOURCE_RULES['cooldown_predicate']),
            'limits':'Execution-site classifier plus unique frozen literal call mapping; not direct rank/UI/league serialization. No random return or bound comparison chooses the predicate.'}


def project_order(entry,aliases,schema):
    args = schema.argument_fields(entry['payload']['arguments'])
    require('items' in args and args['items'].get('type') == 'array', 'GAME_ITEMS_ARGUMENT')
    order = []
    for ref in args['items']['values']:
        schema.validate_typed(ref)
        require(ref.get('type') == 'native_ref', 'GAME_ITEM_REFERENCE')
        role = aliases['native_to_role'].get(ref.get('native_id'))
        require(role in schema.FIXED_ROLES and ref.get('role') == role and aliases['role_to_native'].get(role) == ref['native_id'], 'GAME_ITEM_ALIAS')
        order.append(role)
    require(len(order) == len(set(order)) == 29 and set(order) == schema.FIXED_ROLES, 'GAME_ORDER29')
    return order

def project_fixture(decoded,branch,schema):
    fixture = deepcopy(schema.FIXED_FIXTURE)
    for side, name in (('P', 'player_fixture.json'), ('O', 'fixture.json')):
        raw = decoded[name]
        expected = fixture['sides'][0 if side == 'P' else 1]
        schema.exact(raw, ('schema_version', 'game_version', 'class', 'health', 'stamina', 'items'))
        require(type(raw['schema_version']) is int and raw['schema_version'] == 1 and raw['game_version'] == '1.1.8' and type(raw['class']) is int and raw['class'] == 0, 'FIXED_FIXTURE_CLASS_VERSION')
        for source, target in (('health', 'hp'), ('stamina', 'stamina')):
            value = raw[source]
            require(type(value) in (int, float) and math.isfinite(value) and value == expected[target], 'FIXED_FIXTURE_RESOURCE')
        items = [{k: v for k, v in row.items() if k != 'instance_id'} for row in expected['items']]
        require(same(raw['items'], items), 'FIXED_FIXTURE_GEOMETRY_ORDER')
    require(type(branch.get('value')) is bool,'ACTUAL_BRANCH_BOOL')
    fixture['below_master']=branch['value']
    return fixture

def project_runtime(decoded,aliases,index,schema):
    inputs = decoded['observer7-input.jsonl']
    pre = one(inputs, 'Core/Game.gd::prepareItems', 'checkpoint')
    act = one(inputs, 'Core/Game.gd::activateItems', 'checkpoint')
    pe = one(inputs, 'Core/Game.gd::prepareItems', 'enter')
    ae = one(inputs, 'Core/Game.gd::activateItems', 'enter')
    for checkpoint, entry in ((pre, pe), (act, ae)):
        require(checkpoint['sequence'] + 1 == entry['sequence'], 'CHECKPOINT_ENTRY_ADJACENCY')
        require(all(same(checkpoint['stamp'][k], entry['stamp'][k]) for k in ('physics_frame', 'idle_frame', 'util_time', 'combat_time')), 'CHECKPOINT_ENTRY_CLOCK')
    prepare, activate = project_order(pe,aliases,schema), project_order(ae,aliases,schema)
    require(prepare == activate, 'FIXED_JOINT_PREPARE_ACTIVATE_ORDER')
    header = deepcopy(decoded['king-clock-checkpoint.json'])
    frame_clock = dict(header, passes=deepcopy(decoded['king-clock-passes.jsonl']))
    clock = schema.decode_clock(frame_clock)
    require(ae['stamp']['phase'] == 'Core/Game.gd::activateItems:enter' and ae['stamp']['combat_time'] == {'type': 'float', 'binary64_be': ZERO_BITS}, 'ACTIVATION_PHASE_COMBAT_CLOCK')
    require(ae['stamp']['util_time']['binary64_be'] == header['checkpoint']['util_time_bits'] and schema.decimal(ae['stamp']['physics_frame']) == clock.physics_frame and schema.decimal(ae['stamp']['idle_frame']) == clock.idle_frame, 'ACTIVATION_HEADER_JOIN')
    env = act['payload']['environment']
    environment = {'fps': typed_scalar(env['fps'], 'int'), 'scale': typed_scalar(env['scale'], 'float'), 'paused': typed_scalar(env['paused'], 'bool')}
    require(type(environment['fps']) is int and environment['fps'] == 60 and environment['scale'] == 1.0 and environment['paused'] is False, 'FIXED_ACTIVATION_ENVIRONMENT')
    processing, nodes, timers, origins = [], [], {}, {}
    raw_nodes = {row['role']: row for row in act['payload']['nodes']}
    require(len(raw_nodes) == len(act['payload']['nodes']), 'RAW_NODE_ROLE_DUPLICATE')
    expected_timers = {role for field, phase, role in index if field == 'Timer.private_left' and phase == 'pre_activate'}
    expected_ordinary = {'root_viewport', 'game', 'util', 'combat_timer', 'character:P', 'character:O'} | {'item:' + role for role in schema.FIXED_ROLES}
    require(set(raw_nodes) == expected_timers | expected_ordinary, 'EXACT_EMITTED_BUSINESS_NODE_ROLES')
    emitted_native_ids = set()
    for raw_role, wrapper in raw_nodes.items():
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
        require(identity == wrapper['node']['native_id'], 'TIMER_NEW_RECEIPT_NATIVE_ID')
        origins['timer_initial.' + role + '.native_identity'] = identity_origin
        values = {}
        for raw_field, output_field in (('wait_time', 'wait_time_bits'), ('one_shot', 'one_shot'), ('process_mode', 'process_mode'), ('autostart', 'autostart'), ('paused', 'paused')):
            actual, origin = source_value(index, 'Timer.' + raw_field, 'pre_activate', raw_role)
            require(same(actual, timer[raw_field]), 'TIMER_ACTUAL_RECEIPT_JOIN_' + raw_role + ':' + raw_field)
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
    require(len(timers) == 32 and len(processing) == 67 and len(nodes) == 66 and len({n['role'] for n in processing}) == len(processing), 'BUSINESS_TIMER_OR_NODE_COUNT')
    prefixes={};path_positions={};positions=set();paths=set()
    for node in processing:
        names=node['path'].split('/')[1:];pos=node['positions']
        require(len(pos)==len(names) and pos and pos[0]==-1 and node['path'] not in paths and tuple(pos) not in positions,'PROCESSING_PATH_POSITION_UNIQUE')
        for end in range(1,len(names)+1):
            pp=tuple(pos[:end]);np=tuple(names[:end])
            require((pp not in prefixes or prefixes[pp]==np) and (np not in path_positions or path_positions[np]==pp),'PROCESSING_BIDIRECTIONAL_PREFIX')
            prefixes[pp]=np;path_positions[np]=pp
        paths.add(node['path']);positions.add(tuple(pos))
    characters = {}
    for side in ('P', 'O'):
        values = {}
        for name, kind in (('invulnerable', 'bool'), ('invulnerabilityItem', 'null'), ('buffProtectStacks', 'int')):
            actual, origin = source_value(index, 'Character.' + name, 'pre_activate', side)
            values[name] = typed_scalar(actual, kind)
            origins['initial_characters.' + side + '.' + name] = origin
        require(type(values['buffProtectStacks']) is int and values['buffProtectStacks']==0,'SUPPORTED_OBSERVED_CHARACTER_PROTECTION_INITIAL')
        characters[side] = values
    initial = {}
    for row in pre['payload']['items']:
        identity, fields = row['instance'], row['fields']
        require(identity in schema.FIXED_ROLES and identity not in initial, 'INITIAL_ITEM_IDENTITY')
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
    require(set(initial) == schema.FIXED_ROLES, 'INITIAL_ITEMS_COMPLETE29')
    runtime = dict(schema=RUNTIME_SCHEMA, mode='genuine', profile_id=PROFILE,
                   checkpoint={'util_time_bits': ae['stamp']['util_time']['binary64_be'], 'combat_time_bits': ae['stamp']['combat_time']['binary64_be'], 'source_phase': ae['stamp']['phase']},
                   environment=environment, nodes=nodes, timer_initial=timers, initial_items=initial,
                   initial_characters=characters, prepare_order=prepare, activate_order=activate,
                   terminal_profile='first-actual-idle-after-at-least-two-future-physics/1', frame_clock=frame_clock, processing_nodes=processing)
    require(set(runtime) == set(RUNTIME_KEYS), 'RUNTIME14_KEYS')
    for field in ('schema', 'mode', 'profile_id', 'terminal_profile'):
        origins['runtime.' + field] = {'source': 'data/phase511-input-bridge-source/abi.json', 'predicate': 'immutable input-only ABI declaration; not runtime acceptance'}
    for field in ('checkpoint', 'environment', 'nodes', 'processing_nodes'):
        origins['runtime.' + field] = {'file': 'observer7-input.jsonl', 'sequence': ae['sequence'] if field == 'checkpoint' else act['sequence'], 'predicate': 'actual activation field projection with role normalization and all raw32 Timer records; no exclusions'}
    origins['runtime.frame_clock'] = {'files': ['king-clock-checkpoint.json', 'king-clock-passes.jsonl'], 'predicate': 'complete original header/pass sequence; typed clock decode'}
    for field, entry in (('prepare_order', pe), ('activate_order', ae)):
        origins['runtime.' + field] = {'file': 'observer7-input.jsonl', 'sequence': entry['sequence'], 'pointer': '/payload/arguments', 'predicate': 'actual29 native/role relation'}
    for field in ('timer_initial', 'initial_characters'):
        origins['runtime.' + field] = {'file': 'initial-receipt.json', 'predicate': 'new-object Source-supported values joined to these actual INPUT bytes; individual field refs supplied'}
    origins['runtime.initial_items'] = {'file': 'observer7-input.jsonl', 'sequence': pre['sequence'], 'pointer': '/payload/items', 'predicate': 'only emitted pre-prepare limiter/cache predicates; not complete constructor proof'}
    return runtime, origins, ae['sequence']

def validate_auxiliary_joins(decoded,aliases,schema):
    inputs=decoded['observer7-input.jsonl']
    act=one(inputs,'Core/Game.gd::activateItems','checkpoint')
    nodes={row['role']:row['node'] for row in act['payload']['nodes']}
    facts=decoded['king-input-facts.json'];rng=decoded['king-rng-checkpoint.json']
    schema._single_king_rng_checkpoint(rng,inputs)
    require(rng['game_id']==aliases['role_to_native']['game'] and rng['util']['native_id']==aliases['role_to_native']['util'],'RNG_ACTUAL_GAME_UTIL_ALIAS')
    require(same(facts['root_viewport'],nodes['root_viewport']) and facts['delayed_activation']['target_id']==rng['game_id'],'FACTS_ROOT_DELAYED_OWNER_JOIN')
    for item in facts['items']:
        require(same(item['node'],nodes['item:'+item['instance']]),'FACTS_ACTUAL_ITEM_NODE_JOIN')
        for socket in item['sockets']:
            require(socket['node']['native_id'] not in aliases['native_to_role'],'SOCKET_NOT_SELECTED_NODE_ALIAS')
    return {'initial_rng':'ACTUAL_SOURCE_CHECKPOINT_ONLY_NOT_SEED_REPLAY','facts_root_and_item_aliases':'JOINED_TO_ACTUAL_ACTIVATION_CUT'}


def project_prepared_witnesses(decoded,aliases,receipt):
    observations=receipt['prepare_observations']['pre_activate']
    result={'schema':'phase511-lawful-prepared-witness/1','stage':'pre_activate','status':'OBSERVED_INPUT_NOT_MODEL_EQUIVALENCE',
            'gate':'EXTERNAL_SAME_INSTANCE_BUSINESS_PREPARE_GATE_REQUIRED_BEFORE_ACTIVATION','items':{},
            'comparison_scope':'Only actual business-consumed target/cache order via B1 mapping; full color/current dictionaries are provenance, not Python UI state.'}
    for role,observation in observations.items():
        cached,current=observation['cachedAffectedItems'],observation['currentAffectedItems']
        arrays=[];relations=[]
        for color in cached['entries']:
            arrays.append({'color':deepcopy(color['key']),'ordered_roles':[r['role'] for r in color['value']['values']],
                           'ordered_native_ids':[r['native_id'] for r in color['value']['values']]})
        for color in current['entries']:
            relations.append({'color':deepcopy(color['key']),'ordered_members':[{'role':r['key']['role'],'native_id':r['key']['native_id'],'value':deepcopy(r['value'])} for r in color['value']['entries']]})
        value=deepcopy(observation);value['native_id']=aliases['role_to_native'][role]
        value['ordered_cache_aliases']=arrays;value['ordered_current_aliases']=relations
        result['items'][role]=value
    require(len(result['items'])==29 and all(r in result['items'] for r in ('P:9','P:10','P:14')),'PREPARED29_SPECIAL_IDENTITIES')
    require('goobert_state' in result['items']['P:9'] and 'stackTypes' in result['items']['P:14'],'PREPARED_BASIC_SAPPHIRE_TYPED_WITNESSES')
    return result


def validate_initial_consumer_coverage(bundle,origins,receipt,witness):
    require(set(bundle)=={'schema','fixture','runtime','draws','synthetic_seed'} and bundle['schema']=='native-v8-input-only/1' and bundle['synthetic_seed'] is None,'INPUT_ONLY_ENVELOPE')
    data=bundle['runtime'];require(set(data)==set(RUNTIME_KEYS) and data['schema']==RUNTIME_SCHEMA and data['profile_id']==PROFILE,'RUNTIME14_ABI')
    require(len(data['timer_initial'])==32 and len(data['processing_nodes'])==67 and len(data['nodes'])==66 and len(data['initial_items'])==29,'RAW32_67_66_29')
    require(receipt['counts']['SOURCE_DERIVED']==72 and len(witness['items'])==29,'ALL64_PLUS8_AND_PREPARED_WITNESS')
    for field in bundle:require('bundle.'+field in origins,'BUNDLE_ORIGIN_'+field)
    for field in data:require('runtime.'+field in origins,'RUNTIME_ORIGIN_'+field)
    for role,fields in data['timer_initial'].items():
        for field in fields:require('timer_initial.'+role+'.'+field in origins,'TIMER_FIELD_ORIGIN')
    for side,fields in data['initial_characters'].items():
        for field in fields:require('initial_characters.'+side+'.'+field in origins,'CHARACTER_FIELD_ORIGIN')
    return {'status':STATUS,'runtime_validated':False,'model_release':False,'future_model_blockers':list(DEFERRED)}


def project_decoded(decoded,aliases,receipt,branch,schema):
    fixture=project_fixture(decoded,branch,schema)
    runtime,origins,activation=project_runtime(decoded,aliases,value_index(receipt),schema)
    draws,sequences=project_primitives(decoded,activation)
    witness=project_prepared_witnesses(decoded,aliases,receipt)
    bundle={'schema':'native-v8-input-only/1','fixture':fixture,'runtime':runtime,'draws':draws,'synthetic_seed':None}
    origins.update({'bundle.schema':{'source':'511 ABI'},'bundle.fixture':{'files':['fixture.json','player_fixture.json','king-slot-bindings.json'],'predicate':'actual fixed geometry/resources plus new executed branch witness'},
        'bundle.runtime':{'source':'511 runtime14 ABI'},'bundle.draws':{'file':'observer7-primitives.jsonl','sequences':sequences,'predicate':'full actual selected physical stream including ended-tail'},
        'bundle.synthetic_seed':{'source':'511 ABI NULL; no seed manufacture'}})
    coverage=validate_initial_consumer_coverage(bundle,origins,receipt,witness)
    proof={'schema':'phase511-input-only-projection-proof/1','status':STATUS,'field_origins':origins,
           'primitive_original_sequences':sequences,'branch_witness':branch,'coverage':coverage,
           'timer_origin':'Actual new G02/Character premises; not publiczero or all fresh configured',
           'prepared_equivalence':'External same-instance prepare_only business gate required; not proven by bridge',
           'model_release':False}
    return bundle,proof,witness


def project_from_bytes(raw12,request_raw,request_pin,context_raw,schema_raw):
    """Explicit Root-bound pure bytes interface; no filesystem I/O or import-time schema load."""
    request,context=authenticate_request(request_raw,request_pin,context_raw)
    verify_raw_inputs(raw12,request)  # identity before any data/schema decode
    schema=load_schema(schema_raw)
    decoded,aliases,validation=decode_lawful12(raw12,request,schema)
    receipt=build_initial_receipt(decoded,aliases,schema)
    auxiliary=validate_auxiliary_joins(decoded,aliases,schema)
    branch=derive_branch_witness(decoded,aliases)
    bundle,proof,witness=project_decoded(decoded,aliases,receipt,branch,schema)
    proof['fixed_input_validation']=validation;proof['auxiliary_source_joins']=auxiliary;proof['source_context']=deepcopy(request['source_context'])
    proof['initial_receipt']={'file':'initial-receipt.json','counts':deepcopy(receipt['counts'])}
    return bundle,proof,receipt,witness


def verify_source_context(context,io):
    # Source files only. This is called by the explicit future filesystem build, not by import.
    seen=set()
    for p in context['source_pins']:
        path=str(canonical(p['path']));require(path not in seen,'SOURCE_PIN_DUPLICATE');seen.add(path);read_pinned(p,io)
    required={str(canonical(p['path'])) for p in FIXED_SOURCE_BINDINGS.values()}
    require(required<=seen and str(Path(__file__).absolute()) in seen,'FIXED_SOURCE_AND_PROJECTOR_PINS_REQUIRED')
    return {'status':STATUS,'fixed_source_bindings':deepcopy(FIXED_SOURCE_BINDINGS),'source_rules':deepcopy(SOURCE_RULES),'model_release':False}


def build_from_files(output_new,request_pin):
    require(request_pin is not None,'NO_DEFAULT_REQUEST_OR_NATIVE_PINS')
    source_io=[];input_io=[];owned=[]
    request_raw=read_pinned(request_pin,source_io);request_head=strict_json(request_raw)
    require(type(request_head) is dict and request_head.get('schema')=='phase511-root-bound-input-request/1','EXPLICIT_ROOT_REQUEST_SCHEMA')
    context_raw=read_pinned(request_head['source_context'],source_io)
    request,context=authenticate_request(request_raw,request_pin,context_raw)
    authority=verify_source_context(context,source_io)
    schema_raw=read_pinned(SCHEMA_PIN,source_io)
    output=canonical(output_new);require(output.parent==REPO/'data' and output.name.startswith('phase511-'),'OUTPUT_DOMAIN')
    physical(output.parent,False);require(not os.path.lexists(output),'OUTPUT_EXISTS');output.mkdir(mode=0o700)
    try:
        raw12={name:read_pinned(p,input_io) for name,p in request['input_descriptors'].items()}
        bundle,proof,receipt,witness=project_from_bytes(raw12,request_raw,request_pin,context_raw,schema_raw)
        proof['source_authority']=authority
        source_after=[];input_after=[]
        for p in source_io:read_pinned(p,source_after)
        for p in input_io:read_pinned(p,input_after)
        require(same(source_io,source_after) and same(input_io,input_after),'SOURCE_INPUT_READBACK')
        for name,value in (('input-bundle.json',bundle),('initial-receipt.json',receipt),('input-proof.json',proof),('prepared-witness.json',witness),
                           ('inputs-before-interpretation.json',{'source':source_io,'input':input_io,'request':request_pin}),
                           ('input-readback.json',{'source_before':source_io,'source_after':source_after,'input_before':input_io,'input_after':input_after,'whole_files_read_and_hashed':True,'lawful_syntax_decoded':12,'Expected_reads':0})):
            owned.append(save_new(output/name,value))
        owned.append(save_new(output/'input-seal.json',{'schema':'phase511-input-only-seal/1','status':STATUS,'files':deepcopy(owned),'runtime_validated':False,'model_release':False,'external_same_instance_prepare_gate':'REQUIRED_NOT_EXECUTED','request':request_pin}))
        save_new(output/'owned-files.json',{'schema':'phase511-output-owner/1','files':owned,'independent_input_acceptance':'PENDING','status':STATUS})
    except Exception as error:
        if not os.path.lexists(output/'first-error.json'):save_new(output/'first-error.json',{'error':type(error).__name__,'reason':str(error)[:2000],'source_reads':source_io,'input_reads':input_io,'preserved_outputs':owned,'automatic_retry':False,'model_release':False})
        raise
    return {'status':STATUS,'input_bundle_created':True,'runtime_validated':False,'model_runs':0,'output':str(output)}


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--request',required=True);parser.add_argument('--request-size',type=int,required=True);parser.add_argument('--request-sha256',required=True)
    parser.add_argument('--output-new',required=True);args=parser.parse_args(argv)
    print(json.dumps(build_from_files(args.output_new,{'path':args.request,'size':args.request_size,'sha256':args.request_sha256}),sort_keys=True))


if __name__=='__main__':main()
