"""Generate self-contained pure schema from pinned SOURCE text; no imports of it."""
from pathlib import Path
import ast
from copy import deepcopy
import hashlib
import json
import pprint
import re

R = Path(__file__).resolve().parents[1]
D = R / 'data/phase357-king-observer-schema-source'
B = Path('/workspace/godotsteam-startup-20261013/baseline/Backpack Battles')
OUT = R / 'tests/phase357_king_observer_schema.py'


def pin(path):
    raw = path.read_bytes()
    return dict(size=len(raw), sha256=hashlib.sha256(raw).hexdigest())


def save(name, value):
    with (D / name).open('x') as stream:
        stream.write(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + '\n')


def extract(source, name):
    nodes = [n for n in ast.parse(source).body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name == name]
    node = nodes[-1]
    return ''.join(source.splitlines(keepends=True)[node.lineno - 1:node.end_lineno]) + '\n'


def blocks(source):
    lines = source.splitlines(keepends=True)
    result = {}
    for i, line in enumerate(lines):
        match = re.match(r'^(\t*)func (\w+)\(', line)
        if not match:
            continue
        level, name = len(match[1]), match[2]
        end = i + 1
        while end < len(lines):
            s = lines[end].lstrip()
            if s.strip() and not s.startswith('#') and len(lines[end]) - len(s) <= level:
                break
            end += 1
        if level:
            if name != '_init' or not any(re.match(r'^class TemporaryStacks extends Reference:', x) for x in lines[:i]):
                continue
            name = 'TemporaryStacks._init'
        result[name] = (i, end, level)
    return lines, result


def arguments(block):
    start = block.index('(') + 1
    chunks, current, level, quote, escaped = [], '', 0, None, False
    end = None
    for offset, char in enumerate(block[start:]):
        if quote:
            current += char
            if escaped:
                escaped = False
            elif char == '\\':
                escaped = True
            elif char == quote:
                quote = None
        elif char in ('"', "'"):
            quote = char
            current += char
        elif char in '([{':
            level += 1
            current += char
        elif char == ')' and level == 0:
            if current.strip():
                chunks.append(current.strip())
            end = start + offset + 1
            break
        elif char in ')]}':
            level -= 1
            current += char
        elif char == ',' and level == 0:
            chunks.append(current.strip())
            current = ''
        else:
            current += char
    names, types = [], {}
    for chunk in chunks:
        declaration = chunk.split('=', 1)[0].strip()
        pieces = declaration.split(':', 1)
        name = pieces[0].strip()
        if re.fullmatch(r'\w+', name) is None:
            raise ValueError('unparsed actual GD parameter ' + chunk)
        names.append(name)
        if len(pieces) == 2:
            kind = pieces[1].strip()
            if kind in ('int', 'float', 'bool', 'String', 'Array', 'Dictionary', 'Item', 'Character', 'CombatEvent', 'DamageSource', 'DamageResult'):
                types[name] = {'String': 'string', 'Array': 'array', 'Dictionary': 'dictionary',
                               'Item': 'native_ref|null', 'Character': 'native_ref|null',
                               'CombatEvent': 'event_ref|null', 'DamageSource': 'damage_source|null',
                               'DamageResult': 'damage_result|null'}.get(kind, kind)
    if end is None:
        raise ValueError('unterminated GD function signature')
    return names, types, block[:end]


def main():
    D.mkdir(exist_ok=False)
    contract = json.loads((R / 'data/phase040-observer7-implementation/prebody-contract.json').read_text())
    original_matrix = json.loads((R / 'data/phase040-observer7-implementation/body-site-matrix.json').read_text())
    additions = json.loads((R / 'data/phase095-goobert-native-preparation/source-additions.json').read_text())['matrix_additions']
    old_sites = {**original_matrix['sites'], **additions['sites']}
    sink = (R / 'tests/phase298_native_sink.gd').read_text()
    states = next(ast.literal_eval(line.split(' = ', 1)[1]) for line in sink.splitlines() if line.startswith('const STATE_SCHEMAS = '))
    sites = next(ast.literal_eval(line.split(' = ', 1)[1]) for line in sink.splitlines() if line.startswith('const SITES = '))
    keep = ('Core/', 'Utility/', 'Interface/CombatTimer/', 'Sheets/')
    item_sources = {'Items/Item.gd', 'Items/ItemDescriptor.gd', 'Items/Weapon.gd', 'Items/Potion.gd', 'Items/HealthPotion.gd'}
    sites = {site: value for site, value in sites.items() if site.split('::')[0].startswith(keep) or site.split('::')[0] in item_sources}
    extra = [('Items/Exclusive/KingGoobert.gd', name, 'king') for name in ('prepare', 'doCooldownEffect', 'buffEnded', 'onCombatEnd', 'onStateChanged')]
    extra += [('Core/Character.gd', name, 'character') for name in ('makeInvulnerable', 'invulnerabilityEnded', 'cleanse', 'changeBuffProtectStacks')]
    extra += [('Core/CombatLog.gd', name, 'combat_log') for name in ('createEvent_InvulnerableStart', 'createEvent_InvulnerableEnd')]
    extra += [('Utility/AutoHideParticles.gd', name, 'auto_hide') for name in ('_ready', 'activate', 'deactivate', 'startTimer', 'timeout', 'instantClear')]
    extra += [('Utility/Util.gd', name, 'util') for name in ('_process', 'changeTimer')]
    for file, method, kind in extra:
        sites[file + '::' + method] = dict(channel='runtime', state_schema=kind)
    matrix = dict(sites={}, Timer_API_statement_sites=[], extra_edges=original_matrix['extra_edges'])
    sources = {}
    signatures = []
    for site, meta in sorted(sites.items()):
        file, method = site.split('::', 1)
        raw = (B / file).read_text()
        lines, table = blocks(raw)
        begin, end, level = table[method]
        body = ''.join(lines[begin:end])
        args, types, signature = arguments(body)
        spec = deepcopy(old_sites.get(site, {}))
        spec.update(meta, arguments_exact=args, argument_types=types,
                    explicit_returns=[dict(line=i + 1) for i in range(begin, end) if re.match(r'^\t+return(?:\s|$)', lines[i]) or re.match(r'^\t+.*:\s*return(?:\s|$)', lines[i])])
        matrix['sites'][site] = spec
        sources[file] = pin(B / file)
        signatures.append(dict(site=site, file=str(B / file), line_start=begin + 1, line_end=end,
                               signature=signature, arguments=args, declared_types=types,
                               size=len(body.encode()), sha256=hashlib.sha256(body.encode()).hexdigest()))
        for i in range(begin, end):
            match = re.fullmatch(r'\t+(timer|tickTimer|invulnerabilityTimer|battleRageTimer|autoRageTimer|buffTimer|fatigueStartTimer|fatigueTickTimer)\.(start|stop)\((.*)\)\s*', lines[i].rstrip('\r\n'))
            if match:
                receiver, operation, value = match.groups()
                matrix['Timer_API_statement_sites'].append(dict(site=site, operation=operation, argc=0 if not value else 1,
                                                                receiver_local=receiver, original_args_source=value, line=i + 1))
    keep_states = ('buff', 'character', 'combat_log', 'combat_timer', 'event_bus', 'game', 'generic', 'goobert', 'item', 'node', 'potion', 'temporary_constructor', 'timer', 'util')
    states = {key: states[key] for key in keep_states}
    states['king'] = {**states['goobert'], 'invuCharges': 'int', 'protectedBuffs': 'float', 'manaCost': 'float', 'buffTimer': 'timer', 'activationParticles': 'auto_hide'}
    states['character'].update(buffProtectStacks='int', invulnerabilityItem='native_ref|null', invulBubbleVisible='bool', invulnerabilityTimer='timer')
    states['auto_hide'] = dict(emitting='bool', explosiveness='float', lifetime='float', one_shot='bool', speed_scale='float', timer='timer|null', visible='bool')
    states['plain_item'] = states['item']
    contract['state_schemas'] = states
    contract['caps']['descriptors'] = 6
    contract['primitive_sites']['Utility/Util.gd::randPitch'] = dict(kind='randf_range')
    contract['current_permissions'] = dict(native=False, model=False, input_build=False)
    contract['schema'] = 'phase357-king-typed-record-contract/1'
    contract['status'] = 'SOURCE_SCHEMA_IMPLEMENTED_ADMISSION_CLOSED'
    contract['genuine_extraction_enabled'] = False
    contract['input_leaf_whitelist'] = ['fixture.json', 'player_fixture.json', 'observer7-input.jsonl',
        'observer7-lineage.jsonl', 'observer7-metadata.jsonl', 'observer7-primitives.jsonl',
        'king-clock-checkpoint.json', 'king-clock-passes.jsonl', 'king-input-facts.json',
        'king-ui-authority.jsonl', 'king-rng-checkpoint.json']
    base = (R / 'tests/native_random_observer_patch_v7.py').read_text()
    pieces = ['"""Self-contained finite King typed schema SOURCE. No file/model/native operations."""\n',
              'import hashlib, json, math, re, struct\nfrom copy import deepcopy\nfrom dataclasses import dataclass\nfrom types import SimpleNamespace\n',
              "VERSION='7-king-single-A-355'\nPROFILE='observer7-355-native-single-king-A/1'\nCASE='KING-K1-A-353'\nNATIVE_AUTHORIZED=False\n",
              'DESCRIPTOR_IDS=frozenset({1,4,11,19,22,262})\n',
              'CONTRACT=' + pprint.pformat(contract, width=110, sort_dicts=True) + '\nCAPS=CONTRACT["caps"]\n',
              'MATRIX=' + pprint.pformat(matrix, width=110, sort_dicts=True) + '\n']
    cloned = []
    for name in ('strict_json_loads', 'exact', 'integer', 'decimal', 'text', 'validate_typed', 'validate_state', 'primitive_context', 'scalar_number', 'validate_primitive', 'validate_record'):
        text = extract(base, name)
        if name in ('validate_state', 'primitive_context', 'validate_primitive', 'validate_record'):
            text = text.replace('def ' + name + '(', 'def _base_' + name + '(', 1)
        if name == 'validate_record':
            text = text.replace("'Utility/Util.gd::pickRandomElement':('random_stack:',),", "'Utility/Util.gd::pickRandomElement':('random_stack:',),\n            'Utility/Util.gd::randPitch':('invulnerability_pitch:',),")
        pieces.append(text)
        cloned.append(dict(source='tests/native_random_observer_patch_v7.py', function=name, sha256=hashlib.sha256(extract(base, name).encode()).hexdigest()))
    genuine = (R / 'data/phase356-king-admission-source-repair/staged/native_replay_v8/genuine.py').read_text()
    gt = ast.parse(genuine)
    for node in gt.body:
        if isinstance(node, ast.Assign) and all(isinstance(t, ast.Name) for t in node.targets):
            names = [t.id for t in node.targets]
            if all(n.startswith(('_ui_', '_rng_', 'SINGLE_KING_')) for n in names):
                pieces.append(ast.unparse(node) + '\n')
    names = ['canonical_sha', '_ui_need', '_ui_exact', '_ui_ident', '_ui_integer', '_ui_controls', '_ui_require_admission',
             '_rng_keys', '_rng_decimal', '_rng_int64', '_rng_real', 'validate_single_king_fixture', '_single_king_keys',
             '_single_king_validate_ui', '_single_king_rng_checkpoint', '_single_king_typed', '_single_king_node',
             '_single_king_timer', '_single_king_particle', 'validate_single_king_fresh_facts', 'validate_single_king_ui_authority',
             '_single_king_counter', '_single_king_real', 'validate_single_king_source_defaults', 'validate_single_king_input_provenance']
    for name in names:
        pieces.append(extract(genuine, name))
        cloned.append(dict(source='356 staged genuine.py', function=name, sha256=hashlib.sha256(extract(genuine, name).encode()).hexdigest()))
    clock = (R / 'data/phase356-king-admission-source-repair/staged/native_replay_v7/frame_driver.py').read_text()
    pieces.append("SCHEMA='phase105-exogenous-frame-clock/1'\nMAX_PASSES=200000\nMAX_JSON_BYTES=67108864\nMAX_COUNTER=(1<<63)-1\nPHYSICS_DELTA=struct.unpack('<f',struct.pack('<f',1/60))[0]\n")
    pieces.append("def f32(value):\n    return struct.unpack('<f',struct.pack('<f',value))[0]\n")
    for name in ('_keys', '_counter', '_real', '_nonnegative_real', 'FramePass', 'ClockSchedule', 'decode_clock'):
        text = extract(clock, name)
        if name in ('FramePass', 'ClockSchedule'):
            text = '@dataclass(frozen=True)\n' + text
        pieces.append(text)
        cloned.append(dict(source='356 staged frame_driver.py', function=name, sha256=hashlib.sha256(extract(clock, name).encode()).hexdigest()))
    transport = (R / 'tests/phase355_input_source_contract.py').read_text()
    transport_tree = ast.parse(transport)
    wanted = {'INPUT_FILES', 'CHANNEL_FILES', 'TOTAL_BYTES', 'FILE_CAPS', 'LINE_CAPS', 'ROW_CAPS'}
    for node in transport_tree.body:
        if isinstance(node, ast.Assign) and all(isinstance(t, ast.Name) and t.id in wanted for t in node.targets):
            pieces.append(ast.unparse(node) + '\n')
        elif (isinstance(node, ast.Expr) and isinstance(node.value, ast.Call)
              and isinstance(node.value.func, ast.Attribute) and node.value.func.attr == 'update'
              and isinstance(node.value.func.value, ast.Name) and node.value.func.value.id in wanted):
            pieces.append(ast.unparse(node) + '\n')
    pieces.append("def strict_json(raw):\n    return strict_json_loads(raw.decode('utf-8'))\n")
    fixture = json.loads((R / 'data/phase355-king-finite-source/fixed-A-v8-fixture.json').read_text())
    pieces.append('FIXED_FIXTURE=' + pprint.pformat(fixture, width=110, sort_dicts=True) + '\n')
    extension = (R / 'tests/phase357_schema_extension_source.py').read_text()
    index = {item['instance_id']: item['item_index'] for side in fixture['sides'] for item in side['items']}
    extension = extension.replace('ITEM_INDEX_BY_ROLE = None  # replaced by SOURCE generator with the frozen A map',
                                  'ITEM_INDEX_BY_ROLE = ' + repr(index))
    placeholder = "def _transport_only_decode(raw_by_name):\n    raise AssertionError('SOURCE generator replaces this declaration')\n"
    assert extension.count(placeholder) == 1
    extension = extension.replace(placeholder, extract(transport, 'decode_sources').replace('def decode_sources(', 'def _transport_only_decode(', 1))
    pieces.append(extension)
    output = '\n\n'.join(pieces)
    compile(output, str(OUT), 'exec')
    with OUT.open('x') as stream:
        stream.write(output)
    save('record-hook-matrix.json', dict(schema='phase357-record-to-source-hook/1', sites=signatures,
                                        Timer_API_statement_sites=matrix['Timer_API_statement_sites'],
                                        original_files={name: dict(path=str(B / name), **value) for name, value in sources.items()},
                                        future_producer_implemented=False))
    save('schema-contract.json', contract)
    save('cloned-pure-source-functions.json', dict(functions=cloned, candidate_imports=0, schema_calls=0))
    print(json.dumps(dict(status='SOURCE_GENERATED_COMPILE_ONLY', module=pin(OUT), sites=len(sites), source_files=len(sources))))


if __name__ == '__main__':
    main()
