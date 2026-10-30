"""Finite phase502 SOURCE generation. No generated schema/runtime imports."""
import ast
import difflib
import hashlib
import json
from pathlib import Path
import re
import stat
import traceback

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data/phase502-whelp-observer-source-v2'
SPEC = 'docs/phase502_whelp_observer_source_v2_compile_repair_spec.md'
BASE = 'data/phase462-joint-observer-source-v3'
PROFILE = 'observer7-whelp-family-A-native-tape/1'
VERSION = '7-whelp-family-A-502'
SOURCE_CASE = 'WHELP-FAMILY-A-502'
CASE = 'NATIVE-029-WHELP-FAMILY-A'
IDS = [1,11,22,23,64,164,197,199,201]

PINS = {'sink': {'path': 'data/phase462-joint-observer-source-v3/after-source/native_random_observer_sink_v7.gd', 'size': 102572, 'sha256': '3d3d0cefe90c0e4bd3590d01800b1a05b0ff3398f7e4d245935a122e526a190a'}, 'collector': {'path': 'data/phase462-joint-observer-source-v3/collector.gd', 'size': 64365, 'sha256': 'feb22de0f4427b0412d136d9f56ee0ab17ab8d8044fc225244a69d9cc8ccf273'}, 'schema': {'path': 'data/phase462-joint-observer-source-v3/schema/phase462_king_basic_observer_schema.py', 'size': 196289, 'sha256': 'b2cafda5409b048f655f2f2668f915e3e69339ea801569d0420c775776aabd91'}, 'patch': {'path': 'data/phase462-joint-observer-source-v3/native-patch-source.json', 'size': 30619, 'sha256': '9f8289d4ae7b80d4f3be2ed090c183416538cf776a7aca2f94ff88e3879b4889'}, 'freeze': {'path': 'data/phase462-joint-observer-source-v3/combined-source-freeze.json', 'size': 51863, 'sha256': 'b073e49f98f43d6b77ac8bc8d31e2f387de0122e43860557b243bb64640d7faa'}, 'request': {'path': 'data/phase501-whelp-native-plan-v2/candidate-request-boundary.json', 'size': 7330, 'sha256': '252c8ba4980101c13bb0592fb1986893acf22fcf029f4a1c0f5fe6e0cd0ad235'}, 'request_owner': {'path': 'data/phase501-whelp-native-plan-v2/owned-files.json', 'size': 1075, 'sha256': '91a90b17206accd69429d8135e745bf8d00525c72dfbfd2f79d1390ccede3e39'}, 'job': {'path': 'data/phase498-independent-business-plan/natural-job.json', 'size': 4805, 'sha256': 'e747cddff1646c63bffbe2c3c156dc4c1bfb5c23abc60ca34bce006e6b948e0a'}, 'accepted': {'path': 'data/phase498-independent-final-acceptance/review.json', 'size': 4915, 'sha256': '2f2dadfd5a472ace680aad1604ea11d090a7946ff7a069cef49fc48f3993c0cd'}, 'sdk': {'path': 'data/phase497-source-three-whelps/staged/native_replay_v8/engine.py', 'size': 244417, 'sha256': '3111f334e05a3ce900f78d3ebcbe54da7e3a78935e23fa29bfe00352fd1bb40b'}, 'sdk_owner': {'path': 'data/phase497-source-three-whelps/owned-files.json', 'size': 4445, 'sha256': '9d60cd3d5165b8810eb145a02ae9cb78614112936ca526bc613a2135f482302f'}, 'squirrel': {'path': '/workspace/godotsteam-startup-20261013/baseline/Backpack Battles/Items/Exclusive/Squirrel.gd', 'size': 508, 'sha256': 'c23b8aec966449cc60761007879b99c3528c4cbe94309914789954cea34de949'}, 'sapphire': {'path': '/workspace/godotsteam-startup-20261013/baseline/Backpack Battles/Items/Exclusive/SapphireWhelp.gd', 'size': 384, 'sha256': '583fdfee8bffcdcf56c795aba2ef1f7bbd29f9c16e906d2ffd48dfde150afc17'}}

BASELINE = Path('/workspace/godotsteam-startup-20261013/baseline/Backpack Battles')

def relative_source(path):
    return str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)

def require(ok, message):
    if not ok:
        raise ValueError(message)

def digest(data):
    return hashlib.sha256(data).hexdigest()

def read_source(path):
    path = Path(path)
    require(path.is_relative_to(ROOT) or path.is_relative_to(BASELINE), 'source outside authorized roots')
    require(not any(p.is_symlink() for p in (path, *path.parents)), 'linked source ancestor')
    info = path.lstat()
    require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1, 'ordinary single-link Source required')
    return path.read_bytes()

def descriptor(path):
    path = Path(path)
    raw = read_source(path)
    return dict(path=relative_source(path), size=len(raw), sha256=digest(raw))

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
    # Only header and indented body; intervening top-level declarations are not methods.
    lines = text.splitlines(keepends=True)
    result = {}
    for index, line in enumerate(lines):
        match = re.match(r'^func (\w+)\(', line)
        if match is None:
            continue
        name = match.group(1)
        if name in result:
            raise ValueError('duplicate GD function: ' + name)
        end = index + 1
        while end < len(lines):
            following = lines[end]
            if not following.strip() or following.startswith((' ', '\t')) or following.lstrip().startswith('#'):
                end += 1
            else:
                break
        result[name] = ''.join(lines[index:end]).rstrip()
    return result

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

    def finish(self, path, allowed, added=()):
        inverse = self.text
        for row in reversed(self.edits):
            for pos in reversed(row['after_positions']):
                require(inverse[pos:pos + len(row['after'])] == row['after'], 'inverse preimage mismatch')
                inverse = inverse[:pos] + row['before'] + inverse[pos + len(row['after']):]
        require(inverse.encode() == self.original, 'whole-byte inverse')
        parse = py_functions if self.language == 'py' else gd_functions
        before, after = parse(self.before), parse(self.text)
        require(set(after) - set(before) == set(added) and not set(before) - set(after), 'method inventory changed')
        changed = sorted(name for name in before if before[name] != after[name])
        require(set(changed) == set(allowed), 'unexpected changed functions: ' + repr(changed))
        if self.language == 'py':
            compile(self.text, str(path), 'exec', dont_inherit=True)
        write_bytes(path, self.text.encode())
        stem = path.stem
        report = dict(before=descriptor(self.path), after=descriptor(path), edits=self.edits,
                      inverse='EXACT_COMPLETE_BYTES', changed_functions=changed,
                      conserved_functions=sorted(set(before) - set(changed)),
                      new_functions=sorted(added), language=self.language)
        save(OUT / 'inverse' / (stem + '.json'), report)
        write_bytes(OUT / 'inverse' / (stem + '.patch'), ''.join(difflib.unified_diff(
            self.before.splitlines(True), self.text.splitlines(True),
            fromfile=relative_source(self.path), tofile=relative_source(path))).encode())
        return descriptor(path), report


def verify_preimages():
    sources = {}
    for name, pin in PINS.items():
        path = ROOT / pin['path']
        require(descriptor(path) == pin, 'Source drift: ' + name)
        sources[name] = path
    selected = ROOT / 'data/phase502-root-native-seed-selection/selection.json'
    require(descriptor(selected)['sha256'] == 'a9a6f49df7e2faf64d64a4f37316a659ab25462d3f1fd1e1157420c4de164fd2', 'Root seed selection drift')
    sources['seeds'] = selected
    patch = json.loads(read_source(sources['patch']))
    require(len(patch['paths']) == 75, '75 inherited targets')
    inherited = []
    for target, row in patch['paths'].items():
        if target == 'native_random_observer_sink_v7.gd':
            continue
        pin = descriptor(ROOT / row['after_path'])
        require({k: pin[k] for k in ('size', 'sha256')} == row['after'], 'inherited target drift: ' + target)
        inherited.append(dict(target=target, source=pin, before=row['before']))
    require(len(inherited) == 74, '74 inherited non-sink targets')
    return sources, patch, inherited


def build_plan(sources):
    request = json.loads(read_source(sources['request']))
    job = json.loads(read_source(sources['job']))
    seeds = json.loads(read_source(sources['seeds']))
    require(seeds['case_id'] == CASE and seeds['global_seed'] == 50201 and seeds['util_seed'] == 50202
            and seeds['execute_install_or_capture_authorized'] is False, 'exact preselected seeds; no execution release')
    layout = job['layout']
    require([len(s['items']) for s in layout['sides']] == [16, 13], 'P16/O13')
    require(sorted({i['item_index'] for s in layout['sides'] for i in s['items']}) == IDS, 'exact nine IDs')
    catalog = next(n.value for n in ast.parse(read_source(sources['sdk'])).body if isinstance(n, ast.Assign)
                   and any(isinstance(t, ast.Name) and t.id == 'CATALOG' for t in n.targets))
    shapes = {ast.literal_eval(k): ast.literal_eval(next(kw.value for kw in v.keywords if kw.arg == 'shape'))
              for k, v in zip(catalog.keys, catalog.values) if ast.literal_eval(k) in IDS}
    slots, fixtures = [], {}
    for side in layout['sides']:
        require(side['character_class'] == 0 and side['stamina'] == 5, 'class0/stamina5')
        fixtures[side['side']] = dict(schema_version=1, game_version='1.1.8', **{'class': 0},
                                     health=side['hp'], stamina=side['stamina'], items=[])
        for ordinal, item in enumerate(side['items']):
            require(type(item['f']) is int and item['f'] == 0, 'fixed orientation0')
            spec = dict(side=side['side'], input_slot=ordinal, instance_id=side['side'] + ':' + str(ordinal),
                        item_index=item['item_index'], x=item['x'], y=item['y'], f=item['f'],
                        cells=[[item['x'] + dx, item['y'] + dy] for dx, dy in shapes[item['item_index']]])
            slots.append(spec)
            fixtures[side['side']]['items'].append({key: item[key] for key in ('item_index', 'x', 'y', 'f')})
    expected = request['source_to_native_slot_map']
    require(len(slots) == len(expected) == 29, '29 fixed slots')
    for spec, source in zip(slots, expected):
        require(all(spec[k] == source[k] for k in ('side', 'input_slot', 'item_index', 'x', 'y', 'f'))
                and spec['instance_id'] == source['native_slot_alias'], 'presealed map mismatch')
    fixture = dict(schema=1, game_version='1.1.8', mode='Unranked', round=1, rules='default',
                   below_master=None, sides=[dict(side=s['side'], character_class=0, hp=float(s['hp']),
                   stamina=float(s['stamina']), items=[{k: row[k] for k in ('instance_id','item_index','x','y','f')}
                   for row in slots if row['side'] == s['side']]) for s in layout['sides']])
    config = dict(schema='native-combat-capture/1', case_id=CASE, global_seed=50201, util_seed=50202,
                  player_fixture_enabled=True, timeouts=dict(battle_seconds=120,total_seconds=295))
    business = ['tick:P','tick:O','fatigue:start','fatigue:tick'] + ['buff:'+s+':'+str(i) for s in ('P','O') for i in range(100,111)]
    inactive = ['invu:'+s for s in ('P','O')] + ['aux:'+s+':'+n for s in ('P','O') for n in ('battleRageTimer','autoRageTimer')]
    return dict(schema='phase502-fixed-source-plan/1', profile=PROFILE, version=VERSION, source_case=SOURCE_CASE,
                native_case=CASE, slots=slots, fixture=fixture, native_fixtures=fixtures, config=config,
                timers=dict(raw=business+inactive,business=business,inactive_diagnostics=inactive),
                proposed_counts=dict(raw_timers=32,business_timers=26,processing_nodes=67,business_processing=61,business_configs=60),
                source_bijection=expected, native_facts=None, native_below_master=None,
                status='SOURCE_PLAN_NOT_CAPTURE_OR_RUNTIME_ADMISSION')


ZERO_FACTS = '''func selected_king_facts(items, characters):
	begin_encoding()
	var result = {"schema": "phase502-zero-king-input-facts/1", "root_viewport": node_state(get_tree().get_root()), "timers": {}, "kings": [], "delayed_activation": king_delayed, "items": []}
	if items.size() != SOURCE_SLOT_TABLE.size() or characters.size() != 2:
		fail("WHELP_FACT_COUNT", "selected_king_facts")
		return null
	for character in characters:
		var label = ids.get(character.get_instance_id(), "UNREGISTERED")
		if not label in ["P", "O"]:
			fail("WHELP_CHARACTER_ROLE", "selected_king_facts")
			return null
		result.timers["invu:" + label] = king_timer_fact(character.invulnerabilityTimer, character, "Character.scene.ready", 0)
	for item in items:
		var label = ids.get(item.get_instance_id(), "UNREGISTERED")
		var index = item.descriptor.itemIndex
		if not index in [1, 11, 22, 23, 64, 164, 197, 199, 201] or not source_is(item, "res://Items/Item.gd") or item.has_method("getDataPersistent") or not item.getGemsNoNull().empty() or not item.paramMult.empty() or not item.paramAdd.empty() or item.doubleActivationChance != 0.0 or item.doubleAttackEffectChance != 0.0:
			fail("WHELP_UNSUPPORTED_ITEM_MODIFIER", "selected_king_facts")
			return null
		if (index in [64, 197, 199, 201] and item.sockets.size() != 1) or (index == 164 and item.sockets.size() != 0):
			fail("WHELP_SOCKET_COUNT", "selected_king_facts")
			return null
		var sockets = []
		for socket in item.sockets:
			sockets.append({"node": node_state(socket), "gem": encode(socket.getGem())})
		result.items.append({"instance": label, "node": node_state(item), "descriptorIndex": encode(index), "sockets": sockets, "gem_count": item.getGemsNoNull().size(), "persistent": item.has_method("getDataPersistent"), "paramMult": encode(item.paramMult), "paramAdd": encode(item.paramAdd), "doubleActivationChance": encode(item.doubleActivationChance), "doubleAttackEffectChance": encode(item.doubleAttackEffectChance)})
	return result'''

PITCH_WRAPPER = '''func squirrel_pitch(item, low, high):
	var value = get_node("/root/Util").rng.randf_range(low, high)
	# Preserve original call even outside the selected capture window or after end.
	if source_fixture_bound and ids.has(item.get_instance_id()) and item.descriptor.itemIndex == 164:
		primitive("Items/Exclusive/Squirrel.gd::playDropSound", "randf_range", "squirrel_activation_pitch:" + item_id(item), [low, high], value)
	return value'''


def derive_sink(path, plan):
    delta = Delta(path, 'gd')
    caps = json.loads(re.search(r'^const CAPS = (.+)$', delta.text, re.M).group(1)); caps['descriptors'] = 9
    states = json.loads(re.search(r'^const STATE_SCHEMAS = (.+)$', delta.text, re.M).group(1))
    states['sapphire'] = dict(states['item'], stackTypes='array')
    for name, value in (('CAPS',caps),('STATE_SCHEMAS',states),('SOURCE_SLOT_TABLE',plan['slots']),('RNG_INITIAL_PROFILE',VERSION)):
        delta.gd_constant(name,value)
    delta.function('state', [('[1, 4, 11, 19, 22, 23, 262]',repr(IDS)),
        ('"king" if index == 262 else ("goobert" if index == 23 else ("potion" if index == 19 else "item"))',
         '"goobert" if index == 23 else ("sapphire" if index == 199 else "item")')])
    delta.function('context', [('elif label.begins_with("invulnerability_pitch:"):',
                               'elif label.begins_with("squirrel_activation_pitch:"):')])
    old = gd_functions(delta.text)['selected_king_facts']; delta.replace(old,ZERO_FACTS)
    old = gd_functions(delta.text)['bind_fixed_inventory']
    new = old.replace('return metadata([1, 4, 11, 19, 22, 23, 262])','return metadata('+repr(IDS)+')')
    start = new.index('\tfor item in game.PLAYER.INVENTORY.getItems():')
    end = new.index('\tif not configure(registry):',start)
    new = new[:start] + new[end:]
    delta.replace(old,new)
    delta.function('source_selected_auto', [('ui_kings.has(owner) and ui_kings[owner].pooled == false and ids.get(int(owner), "") == "P:6"', 'false')])
    for name in ('ui_open','rng_initial_capture'):
        delta.function(name,[('KING-BASIC-A-460',SOURCE_CASE)])
    delta.replace(delta.text[-1:], delta.text[-1:] + '\n\n' + PITCH_WRAPPER + '\n') if False else None
    # Append via an exact unique complete trailing method anchor, keeping inverse positional.
    last = list(gd_functions(delta.text))[-1]
    tail = gd_functions(delta.text)[last]
    delta.replace(tail, tail + '\n\n' + PITCH_WRAPPER)
    return delta


def derive_squirrel(path):
    delta = Delta(path, 'gd')
    delta.function('playDropSound', [('Util.rng.randf_range(0.9, 1.1)',
        'get_node("/root/NativeRandomObserver").squirrel_pitch(self, 0.9, 1.1)')])
    return delta


def derive_collector(path, plan):
    delta = Delta(path, 'gd')
    for name, value in (('SOURCE_P',plan['native_fixtures']['P']),('SOURCE_O',plan['native_fixtures']['O']),
                        ('SOURCE_CONFIG',plan['config']),('PLAYER_ITEM_WHITELIST',IDS)):
        delta.gd_constant(name,value)
    delta.function('state_snapshot', [('\t\t\tvar observer7_timers = {}',
        '\t\t\tif item.descriptor.itemIndex == 199:\n\t\t\t\tobserver7_fields = fields(item, ["stackTypes"])\n\t\t\tvar observer7_timers = {}')])
    delta.function('on_idle_source_cut', [('phase391-single-King-oracle-only','phase502-zero-King-whelp-oracle-only')])
    return delta

ZERO_FACTS_VALIDATOR = '''def validate_single_king_fresh_facts(facts):
    exact(facts, ('schema','root_viewport','timers','kings','delayed_activation','items'))
    if facts['schema'] != 'phase502-zero-king-input-facts/1' or facts['kings'] != []:
        raise ValueError('fixed zero-King facts/profile')
    root = _single_king_node(facts['root_viewport'])
    if root['path'] != '/root' or not root['inside_tree']:
        raise ValueError('actual root identity')
    exact(facts['timers'], ('invu:P','invu:O'))
    timer_ids = set()
    for role, fact in facts['timers'].items():
        exact(fact, ('lineage','current','private_provenance'))
        lineage = fact['lineage']
        exact(lineage, ('timer_id','owner_id','kind','starts','stops','birth'))
        decimal(lineage['owner_id'], True)
        if (lineage['kind'] != 'Character.scene.ready' or type(lineage['starts']) is not int
                or lineage['starts'] != 0 or type(lineage['stops']) is not int or lineage['stops'] < 0):
            raise ValueError('Character actual lifetime no-start ledger')
        birth, current = _single_king_timer(lineage['birth']), _single_king_timer(fact['current'])
        node = current['node']
        if (lineage['timer_id'] != node['native_id'] or birth['node']['native_id'] != node['native_id']
                or node['native_id'] in timer_ids or node['role'] != role):
            raise ValueError('Character stable distinct Timer identity')
        timer_ids.add(node['native_id'])
        if fact['private_provenance'] != 'source_constructor_minus_one_no_start_not_public_zero_inference':
            raise ValueError('source lineage is not private observation')
        for timer in (birth,current):
            if (type(timer['process_mode']) is not int or timer['process_mode'] != 0
                    or timer['autostart'] is not False or timer['paused'] is not False or timer['stopped'] is not True):
                raise ValueError('Character source Timer state')
            _single_king_typed(timer['wait_time'],'float','3ff0000000000000')
            _single_king_typed(timer['time_left'],'float','0000000000000000')
            if any(timer['node'][flag] is not False for flag in ('ordinary_physics','internal_physics','ordinary_idle','internal_idle')):
                raise ValueError('Character inactive source Timer flags')
        if current['one_shot'] is not True or birth['one_shot'] is not True or node['inside_tree'] is not True:
            raise ValueError('Character configured in-tree Timer')
    items = facts['items']
    if type(items) is not list or len(items) != len(FIXED_ROLES):
        raise ValueError('complete29 selected item facts')
    seen, natives, socket_ids = set(), set(), set()
    for item in items:
        exact(item, ('instance','node','descriptorIndex','sockets','gem_count','persistent','paramMult','paramAdd','doubleActivationChance','doubleAttackEffectChance'))
        role = item['instance']
        if type(role) is not str or role not in FIXED_ROLES or role in seen:
            raise ValueError('unknown/duplicate zero-King item role')
        seen.add(role)
        node = _single_king_node(item['node'])
        if node['role'] != role or node['native_id'] in natives or node['native_id'] in timer_ids:
            raise ValueError('actual item identity association')
        natives.add(node['native_id'])
        if item['descriptorIndex'] != {'type':'int','decimal':str(ITEM_INDEX_BY_ROLE[role])}:
            raise ValueError('actual item descriptor association')
        if type(item['gem_count']) is not int or item['gem_count'] != 0 or item['persistent'] is not False:
            raise ValueError('empty/nonpersistent fixed domain')
        for key in ('paramMult','paramAdd'):
            if _single_king_typed(item[key],'dictionary')['entries'] != []:
                raise ValueError('no custom item modifiers')
        for key in ('doubleActivationChance','doubleAttackEffectChance'):
            _single_king_typed(item[key],'float','0000000000000000')
        sockets = item['sockets']
        if type(sockets) is not list or len(sockets) > 16:
            raise ValueError('bounded actual sockets')
        index = ITEM_INDEX_BY_ROLE[role]
        if index in (64,197,199,201) and len(sockets) != 1 or index == 164 and len(sockets) != 0:
            raise ValueError('Whelp/Squirrel actual socket count')
        for socket in sockets:
            exact(socket, ('node','gem'))
            child = _single_king_node(socket['node'])
            _single_king_typed(socket['gem'],'null')
            if child['native_id'] in socket_ids or not child['path'].startswith(node['path']+'/Icon/Sockets/'):
                raise ValueError('distinct owned socket')
            socket_ids.add(child['native_id'])
    if natives & socket_ids or timer_ids & socket_ids:
        raise ValueError('item/socket/Timer identity aliases')
    delayed = facts['delayed_activation']
    exact(delayed, ('target_id','method','delay','tree_timer_id','source','physics_frame','idle_frame'))
    decimal(delayed['target_id'],True); decimal(delayed['tree_timer_id'],True)
    if delayed['method'] != 'activateItems' or delayed['source'] != 'Utility/Util.gd::callDelayed':
        raise ValueError('actual delayed activation source')
    _single_king_typed(delayed['delay'],'float','4004000000000000')
    _single_king_counter(delayed['physics_frame']); _single_king_counter(delayed['idle_frame'])
    return facts'''


def derive_schema(path, plan, binding_contract):
    delta = Delta(path,'py')
    contract = next(ast.literal_eval(n.value) for n in ast.parse(delta.text).body if isinstance(n,ast.Assign)
                    and any(isinstance(t,ast.Name) and t.id == 'CONTRACT' for t in n.targets))
    contract['caps']['descriptors'] = 9
    contract['state_schemas']['sapphire'] = dict(contract['state_schemas']['item'], stackTypes='array')
    contract['primitive_sites']['Items/Exclusive/Squirrel.gd::playDropSound'] = dict(kind='randf_range',args=['REAL0.9','REAL1.1'])
    constants = dict(VERSION=repr(VERSION),PROFILE=repr(PROFILE),DESCRIPTOR_IDS='frozenset('+repr(IDS)+')',
        CONTRACT=repr(contract),SINGLE_KING_GENUINE_PROFILE=repr(PROFILE),SINGLE_KING_OBSERVER_VERSION=repr(VERSION),
        SINGLE_KING_CASE=repr(SOURCE_CASE),SINGLE_KING_ITEMS='frozenset('+repr(IDS)+')',
        SINGLE_KING_FIXTURE_SHA256=repr(canonical(plan['fixture'])),SINGLE_KING_ROLES='frozenset('+repr([s['instance_id'] for s in plan['slots']])+')',
        FIXED_FIXTURE=repr(plan['fixture']),ITEM_INDEX_BY_ROLE=repr({s['instance_id']:s['item_index'] for s in plan['slots']}),
        TIMER_ROLES='frozenset('+repr(plan['timers']['raw'])+')', BINDING_FIXED_PLAN=repr(plan['slots']),
        BINDING_SOURCE_CONTRACT=repr(binding_contract))
    for name, expression in constants.items(): delta.py_constant(name,expression)
    delta.function('validate_single_king_fixture',[("kings != ['P:6']",'kings != []'),
        ('single King outside predeclared fixed A fixture','zero-King outside predeclared Whelp fixture'),
        ('single unsocketed P King/six item source domain','zero-King nine-ID source domain')])
    delta.function('_single_king_validate_ui', [
        ("if kind=='bind':", "if kind=='bind':\n   raise ValueError('zero-King profile rejects King particle binding')"),
        ("len(v['kings'])==1,'one selected King'", "len(v['kings'])==0,'zero selected Kings'"),
        ("closed and len(rolemap)==1", "closed and len(rolemap)==0")])
    delta.replace(py_functions(delta.text)['validate_single_king_fresh_facts'],ZERO_FACTS_VALIDATOR)
    old = py_functions(delta.text)['validate_single_king_source_defaults']
    start = old.index('    for record, cooldown in ')
    new = 'def validate_single_king_source_defaults(pre, act):\n    """Observed Basic defaults only; never model state or fixture predicate."""\n' + old[start:]
    new = new.replace("'P:7'","'P:9'")
    delta.replace(old,new)
    old = py_functions(delta.text)['validate_single_king_input_provenance']
    start = old.index("    king = facts['kings'][0]")
    end = old.index('    for native, role in selected.items():',start)
    new = old[:start] + '''    if ui['king_roles'] != {}:
        raise ValueError('zero selected King role mapping')
    fact_items = {item['instance']: item for item in facts['items']}
    if set(fact_items) != set(SINGLE_KING_ROLES):
        raise ValueError('all selected item facts join')
    for role, item in fact_items.items():
        if item['node'] != byrole['item:' + role]['node']:
            raise ValueError('actual selected item facts/checkpoint node join')
''' + old[end:]
    delta.replace(old,new)
    delta.function('validate_state', [
        ("('item', 'goobert', 'king', 'potion', 'plain_item')", "('item', 'goobert', 'king', 'potion', 'plain_item', 'sapphire')"),
        ("actual = 'king' if index == 262 else 'goobert' if index == 23 else 'potion' if index == 19 else 'plain_item'",
         "actual = 'goobert' if index == 23 else 'sapphire' if index == 199 else 'plain_item'"),
        ("or kind == 'plain_item' and actual != 'plain_item':", "or kind == 'plain_item' and actual != 'plain_item' or kind == 'sapphire' and actual != 'sapphire':"),
        ("item descriptor outside fixed seven IDs", "item descriptor outside fixed nine IDs"),
        ("    for key in ('currentAffectedItems', 'cachedAffectedItems'):",
         "    if kind == 'sapphire':\n        wanted = {'type': 'array', 'values': [{'type': 'int', 'decimal': str(i)} for i in (101,102,103,104,106,107)]}\n        if value['stackTypes'] != wanted:\n            raise ValueError('Sapphire actual ordered six INT nonMana stackTypes')\n    for key in ('currentAffectedItems', 'cachedAffectedItems'):")])
    delta.function('primitive_context', [
        ("label.startswith('invulnerability_pitch:')", "label.startswith('squirrel_activation_pitch:')"),
        ("label != 'invulnerability_pitch:P:6'", "label != 'squirrel_activation_pitch:P:10'"),
        ("{'item': 'P:6'}", "{'item': 'P:10'}"),
        ('fixed selected King pitch context','fixed selected Squirrel pitch context')])
    delta.function('validate_primitive',[("'invulnerability_pitch:P:6'","'squirrel_activation_pitch:P:10'"),
        ('original randPitch0.1 exact REAL endpoints','original direct Squirrel exact REAL endpoints')])
    delta.function('_base_validate_record',[("'Utility/Util.gd::randPitch':('invulnerability_pitch:',),",
        "'Utility/Util.gd::randPitch':('invulnerability_pitch:',),\n            'Items/Exclusive/Squirrel.gd::playDropSound':('squirrel_activation_pitch:',),")])
    # Remove a King-only REAL4 assertion, which would misclassify new P6 LeatherBag.
    old = py_functions(delta.text)['validate_record']
    start = old.index("        if site == 'Items/Item.gd::useMana'")
    end = old.index("    if site in MATRIX['sites'] and edge in",start)
    delta.replace(old,old[:start]+old[end:])
    delta.function('_binding_validate_value',[('exact26 actual slot bindings','exact29 actual slot bindings')])
    return delta


def freeze_source(sources, plan, old_patch, inherited, artifacts, reports):
    paths = json.loads(json.dumps(old_patch['paths']))
    paths['native_random_observer_sink_v7.gd']['after_path'] = artifacts['sink']['path']
    paths['native_random_observer_sink_v7.gd']['after'] = {k:artifacts['sink'][k] for k in ('size','sha256')}
    require('Items/Exclusive/Squirrel.gd' not in paths, 'Squirrel is one genuinely new target')
    paths['Items/Exclusive/Squirrel.gd'] = dict(before={k:descriptor(sources['squirrel'])[k] for k in ('size','sha256')},
        after={k:artifacts['squirrel'][k] for k in ('size','sha256')}, after_path=artifacts['squirrel']['path'])
    for row in inherited:
        require(paths[row['target']] == old_patch['paths'][row['target']], 'inherited descriptor mutation')
    original_sink, actual_sink = read_source(sources['sink']).decode(), read_source(ROOT/artifacts['sink']['path']).decode()
    gd_const = lambda source,name: re.search(r'^const '+name+r' = [^\n]+',source,re.M).group()
    require(gd_const(original_sink,'SITES') == gd_const(actual_sink,'SITES'), '107 SITES exact')
    require(len(json.loads(gd_const(actual_sink,'SITES').split(' = ',1)[1])) == 107, '107 sites')
    get_matrix = lambda source: next(ast.get_source_segment(source,n) for n in ast.parse(source).body
        if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id == 'MATRIX' for t in n.targets))
    original_schema = read_source(sources['schema']).decode()
    actual_schema = read_source(ROOT/artifacts['schema']['path']).decode()
    require(get_matrix(original_schema) == get_matrix(actual_schema), 'MATRIX and Timer API exact')
    old_squirrel = gd_functions(read_source(sources['squirrel']).decode())
    new_squirrel = gd_functions(read_source(ROOT/artifacts['squirrel']['path']).decode())
    require(old_squirrel['playPickupSound'] == new_squirrel['playPickupSound'], 'pickup unchanged')
    require(old_squirrel['doCooldownEffect'] == new_squirrel['doCooldownEffect'], 'effect unchanged')
    require(new_squirrel['playDropSound'].replace('get_node("/root/NativeRandomObserver").squirrel_pitch(self, 0.9, 1.1)',
        'Util.rng.randf_range(0.9, 1.1)') == old_squirrel['playDropSound'], 'exact one-expression inverse')
    require(PITCH_WRAPPER.count('.rng.randf_range(low, high)') == 1 and 'fightEnded' not in PITCH_WRAPPER
        and PITCH_WRAPPER.rstrip().endswith('return value'), 'one original RNG/actual result, no ended filter')
    require(gd_functions(original_sink)['primitive'] == gd_functions(actual_sink)['primitive'], 'raw primitive encoder unchanged')
    for name in ('stack_pick_label','fraction_context','buff_label','reflect_label','clock_pass','begin_king_clock',
                 'source_tail_begin','source_tail_note_pass','source_terminal_current'):
        require(gd_functions(original_sink)[name] == gd_functions(actual_sink)[name], 'shared method drift: '+name)
    patch = dict(schema='phase502-native-patch-source/1',paths=paths,producer=descriptor(Path(__file__)),
        sink=artifacts['sink'],profile=PROFILE,observer_version=VERSION,terminal_policy=old_patch['terminal_policy'])
    save(OUT/'native-patch-source.json',patch)
    marker = json.loads(read_source(sources['freeze']))['artifacts']['.native-random-observer-disposable']
    require(descriptor(ROOT/marker['path']) == marker, 'exact disposable marker')
    install_artifacts = {'native_combat_capture.gd':artifacts['collector'],
        'native_capture_config.json':descriptor(OUT/'case-inputs/native_capture_config.json'),
        '.native-random-observer-disposable':marker}
    targets = [dict(namespace='project',target=name,before=row['before'],source=dict(path=row['after_path'],**row['after']))
        for name,row in paths.items()]
    targets += [dict(namespace='project',target=name,before=None,before_policy='Unknown actual predecessor; future locked journal required',source=pin)
                for name,pin in install_artifacts.items()]
    total = sum(row['source']['size'] for row in targets)
    save(OUT/'install-targets.json',dict(schema='phase502-install-source-inventory/1',project=targets,
        project_install_count=len(targets),project_install_source_bytes=total,
        case_inputs=[dict(target=p.name,source=descriptor(p)) for p in sorted((OUT/'case-inputs').glob('*.json'))],
        actual_pool_preimages_verified=False,host_ready=False,install_or_execute_authorized=False,
        old_reference=dict(count=78,bytes=812880,applicable=False),
        restore_requirement='Actual predecessor union, new Squirrel preimage and touched-directory metadata; no hardcoded old80 restore count'))
    save(OUT/'source-tuple.json',dict(schema='phase502-zero-king-observer-source-tuple/1',profile=PROFILE,
        observer_version=VERSION,case=CASE,terminal_policy=old_patch['terminal_policy'],producer=descriptor(Path(__file__)),
        sink=artifacts['sink'],collector=artifacts['collector'],schema_module=artifacts['schema'],
        direct_primitive_wrapper=artifacts['squirrel'],fixed_plan=descriptor(OUT/'fixed-plan.json'),
        fixed_fixture=descriptor(OUT/'fixed-v8-fixture.json'),native_patch=descriptor(OUT/'native-patch-source.json'),
        model_input_or_runtime_admitted=False,host_execution_ready=False))
    sdk_freeze = json.loads(read_source(ROOT/'data/phase497-source-three-whelps/candidate-source-freeze.json'))
    sdk_files = []
    for row in sdk_freeze['files']:
        pin = {k:row[k] for k in ('path','size','sha256')}
        require(descriptor(ROOT/pin['path']) == pin, '497 SDK drift')
        sdk_files.append(pin)
    require(len(sdk_files) == 15, 'exact15 SDK unchanged')
    save(OUT/'conservation.json',dict(schema='phase502-source-conservation/1',changed_functions={k:v['changed_functions'] for k,v in reports.items()},
        added_functions={k:v['new_functions'] for k,v in reports.items()}, unchanged_inherited_targets=inherited,
        inherited_non_sink_count=74,method_sites=107,new_method_hooks=0,new_direct_primitive_sites=1,
        MATRIX_Timer_API_statement_bytes_exact=True,inverse='ALL_FOUR_COMPLETE_PREIMAGE_BYTES',
        direct_wrapper=dict(original_call='Util.rng.randf_range(0.9, 1.1)',same_native_call_count=1,
            actual_return_forwarded=True,playPickupSound_exact=True,doCooldownEffect_exact=True,
            ended_or_limiter_prefilter=False,not_a_native_execution_test=True),sdk497_unchanged=sdk_files))
    external = [descriptor(p) for p in sources.values()] + [row['source'] for row in inherited] + [marker]
    external += sdk_files + [descriptor(ROOT/'data/phase497-source-three-whelps/candidate-source-freeze.json')]
    generated = [descriptor(p) for p in sorted(OUT.rglob('*')) if p.is_file()]
    save(OUT/'combined-source-freeze.json',dict(schema='phase502-source-freeze/1',files=generated+external+
        [descriptor(Path(__file__)),descriptor(ROOT/SPEC)],paths=paths,artifacts=install_artifacts,
        collector=artifacts['collector'],schema_module=artifacts['schema'],active_source_tuple=descriptor(OUT/'source-tuple.json'),
        profile=PROFILE,observer_version=VERSION,terminal_policy=old_patch['terminal_policy'],
        project_install_count=len(targets),project_install_source_bytes=total,
        host_ready=False,model_runtime_admitted=False,Godot_parse=0,native=0,model=0))
    compile(read_source(Path(__file__)),str(Path(__file__)),'exec',dont_inherit=True)
    save(OUT/'compile-only.json',dict(schema='phase502-compile-only/1',discarded_compile_objects=2,producer=True,
        schema_compiled=True,GD_parser_or_parse=0,generated_module_imports=0,schema_calls=0,models=0,
        Expected_reads=0,host_plan_or_execute=0,pool_operations=0,cleanup=0))
    save(OUT/'first-generation-result.json',dict(schema='phase502-source-generation-result/1',
        status='SOURCE_GENERATED_COMPILED_PENDING_INDEPENDENT503',source_generation_invocations=1,
        descriptors=9,slots=29,Kings=0,raw_timers=32,business_timers=26,inactive_diagnostics=6,
        project_install_count=len(targets),project_install_source_bytes=total,
        imports=0,schema_calls=0,models=0,Godot=0,Expected_reads=0,pool_operations=0,
        actual_native_canAdd='UNOBSERVED',actual_native_below_master=None,
        later='Independent Source and limited Python synthetic controls only; no automatic parse/install/capture; nonKing realclock consumer phase504')))
    owned = [descriptor(ROOT/SPEC),descriptor(Path(__file__))] + [descriptor(p) for p in sorted(OUT.rglob('*')) if p.is_file()] + external
    # Keep one exact physical Source identity per path, including complete external closure.
    unique = {}
    for pin in owned:
        require(pin['path'] not in unique or unique[pin['path']] == pin, 'conflicting Source owner descriptor')
        unique[pin['path']] = pin
    save(OUT/'source-owner.json',dict(schema='phase502-source-owner/1',files=list(unique.values()),no_more_writes=True,
        status='SOURCE_ONLY_PENDING_INDEPENDENT503_NO_HOST_NATIVE_OR_RUNTIME_RELEASE'))
    return descriptor(OUT/'source-owner.json')


def main():
    require(not OUT.exists(),'unique Source directory already exists')
    OUT.mkdir()
    save(OUT/'generation-started.json',dict(schema='phase502-generation-started/1',attempt=1,
        producer=descriptor(Path(__file__)),spec=descriptor(ROOT/SPEC),native=0,models=0))
    try:
        sources, patch, inherited = verify_preimages()
        save(OUT/'source-before.json',dict(files=[descriptor(p) for p in sources.values()],inherited_targets=inherited))
        plan = build_plan(sources)
        save(OUT/'fixed-plan.json',plan)
        save(OUT/'fixed-v8-fixture.json',plan['fixture'])
        for name,value in (('custom_player.json',plan['native_fixtures']['P']),('custom_opponent.json',plan['native_fixtures']['O']),
                           ('native_capture_config.json',plan['config'])):
            save(OUT/'case-inputs'/name,value)
        save(OUT/'source-authority.json',dict(schema='phase502-source-authority/1',producer=descriptor(Path(__file__)),spec=descriptor(ROOT/SPEC),
            origin={k:descriptor(p) for k,p in sources.items()},scope='SOURCE_ONLY_NOT_HOST_NATIVE_INPUT_OR_RUNTIME_ADMISSION'))
        binding_contract = dict(schema='phase360-binding-source-contract/1',schema_origin=descriptor(sources['schema']),
            producer_source_origin=descriptor(OUT/'source-authority.json'),fixed_slot_map=descriptor(OUT/'fixed-plan.json'),
            fixed_fixture=descriptor(OUT/'fixed-v8-fixture.json'),evidence_policy='SOURCE_ORIGIN_ONLY_NO_NATIVE_ID_OR_ADMISSION')
        derived = [('sink',derive_sink(sources['sink'],plan),OUT/'after-source/native_random_observer_sink_v7.gd',
            ['state','context','selected_king_facts','bind_fixed_inventory','source_selected_auto','ui_open','rng_initial_capture'],['squirrel_pitch']),
            ('collector',derive_collector(sources['collector'],plan),OUT/'collector.gd',['state_snapshot','on_idle_source_cut'],[]),
            ('schema',derive_schema(sources['schema'],plan,binding_contract),OUT/'schema/phase502_whelp_observer_schema.py',
            ['validate_single_king_fixture','_single_king_validate_ui','validate_single_king_fresh_facts',
             'validate_single_king_source_defaults','validate_single_king_input_provenance','validate_state',
             'primitive_context','validate_primitive','_base_validate_record','validate_record','_binding_validate_value'],[]),
            ('squirrel',derive_squirrel(sources['squirrel']),OUT/'after-source/Items/Exclusive/Squirrel.gd',['playDropSound'],[])]
        artifacts,reports = {},{}
        for name,delta,path,changed,added in derived:
            artifacts[name],reports[name] = delta.finish(path,changed,added)
        owner = freeze_source(sources,plan,patch,inherited,artifacts,reports)
        print(json.dumps(dict(status='SOURCE_FROZEN_NO_RUNTIME_EXECUTION',owner=owner),sort_keys=True))
        return 0
    except Exception as error:
        save(OUT/'first-generation-error.json',dict(schema='phase502-generation-first-error/1',error_type=type(error).__name__,
            message=str(error),traceback=traceback.format_exc(),automatic_retry=False,Godot=0,models=0,Expected=0,pool_operations=0))
        raise


if __name__ == '__main__':
    raise SystemExit(main())
