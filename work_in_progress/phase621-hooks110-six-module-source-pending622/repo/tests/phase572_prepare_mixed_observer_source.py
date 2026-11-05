"""Phase572 isolated Source generator. No schema imports, helper tests or native execution."""
import ast
import difflib
import hashlib
import json
from pathlib import Path
import re
import stat
import traceback

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data/phase572-mixed-observer-source'
SPEC = 'docs/phase572_mixed_observer_source_implementation_spec.md'
BASELINE = Path('/workspace/godotsteam-startup-20261013/baseline/Backpack Battles')
PROFILE = 'observer7-mixed-modifiers-A-native-tape/1'
VERSION = '7-mixed-modifiers-A-572'
SOURCE_CASE = 'MIXED-MODIFIERS-A-572'
CASE = 'NATIVE-030-MIXED-MODIFIERS-A'
IDS = [1,5,11,14,22,32,162,164,231,233,234,385]

PINS = {'collector': {'path': 'data/phase502-whelp-observer-source-v4/collector.gd', 'sha256': '640bdb9b1a62e57827faed1775054d7450a411ca3b647f70f286b851436f1dfd', 'size': 64612}, 'item': {'path': 'data/phase359-king-producer-source/after-source/Items/Item.gd', 'sha256': '2fc1d658db352a7ecae8c2bfb60640a019284992a9c5f9a14c87baea50721631', 'size': 178363}, 'schema': {'path': 'data/phase502-whelp-observer-source-v4/schema/phase502_whelp_observer_schema.py', 'sha256': 'd5531e3e9b119f0309140cb50dff2c7f545abb5ec3500d488bde29cacdb8f193', 'size': 197522}, 'sink': {'path': 'data/phase502-whelp-observer-source-v4/after-source/native_random_observer_sink_v7.gd', 'sha256': '41d500e34557cf731baea0c3e150e3d0d0815d26b5bea87c21ab3a81cd2b7162', 'size': 102916}, 'util_unchanged': {'path': 'data/phase359-king-producer-source/after-source/Utility/Util.gd', 'sha256': 'd437e9338c8c4587c0cddd29e848bef54e8b621169dd364ceaa341fbc7a1e507', 'size': 46276}, 'patch': {'path': 'data/phase502-whelp-observer-source-v4/native-patch-source.json', 'size': 31034, 'sha256': '3425d9aff911e076c57b7dc89e48e67003e95a42df99ffff732f002b132e77fc'}, 'freeze': {'path': 'data/phase502-whelp-observer-source-v4/combined-source-freeze.json', 'size': 58760, 'sha256': '04e152576b706f66da05d33fe493670604eca14110cbe98e73ee5f3703afb44a'}, 'base_owner': {'path': 'data/phase502-whelp-observer-source-v4/source-owner.json', 'size': 27181, 'sha256': '48a578c6d8f9f2189e5241432d6e0b14fed8a5d4fda948ca73b0ab62dd6c8d8f'}, 'base_tuple': {'path': 'data/phase502-whelp-observer-source-v4/source-tuple.json', 'size': 2001, 'sha256': '026877626166fe632c08bd3cba28aec191561373b2167f3c6d15d1f1fac86658'}, 'squirrel': {'path': 'data/phase502-whelp-observer-source-v4/after-source/Items/Exclusive/Squirrel.gd', 'size': 547, 'sha256': 'afbba6556077e0f30f6cd5d6abced0949cd64c5979e2554326ef1303076dd1e5'}, 'job': {'path': 'data/phase565-exact-business-source/natural-job.json', 'size': 4818, 'sha256': '7b7fcb86a0fe82640f024488c15472ab31b2d56143c526e9ed67c8c32638d51e'}, 'sdk': {'path': 'data/phase564-source-finite-mixed/staged/native_replay_v8/engine.py', 'size': 259634, 'sha256': '2a29367a60d55937bfd139ad16cc4b228c3616acf28f6d37f826c15284f9feff'}, 'aliases': {'path': 'data/phase569-mixed-producer-schema-design/fixed-source-alias-map.json', 'size': 5915, 'sha256': 'da6c362b9bcfc45a7b2e94461562a49533292c8cf248b791d8d3e7738255b91a'}, 'preimages': {'path': 'data/phase569-mixed-producer-schema-design/source-preimages-and-boundaries.json', 'size': 10723, 'sha256': '7a3b64b7bf0c9cd6c692244dc78686c84d19e72b4fed509f90cb962ee1db2a3e'}, 'conditions': {'path': 'data/phase571-mixed-producer-conditions-addendum/conditions-and-authorities.json', 'size': 7312, 'sha256': '91bda709b856028774002c81dae0a3a34892010ba915f549b6915fd2e649c92f'}, 'release': {'path': 'data/phase572-root-source-implementation-release/release.json', 'size': 1966, 'sha256': '5a287112857848d5b1e9a7b4e1f521fdc24e4759fdc140c1d2ac1343156f3b09'}, 'root_draft': {'path': 'data/phase571-root-future030-source-binding/source-binding.json', 'size': 1265, 'sha256': '09c8e95ba808339412e2259fa4577e32332f9399e23b44995eba313b8614816b'}, 'food_supplement': {'path': 'docs/phase572_food_receiver_binding_addendum_spec.md', 'size': 1184, 'sha256': '886fed4a5fa8db1aa541f7a82e96551abc1ed26ebde22f729f732abff8a54693'}, 'authority_0': {'path': '/workspace/godotsteam-startup-20261013/baseline/Backpack Battles/Sheets/CSV/ItemData.csv', 'sha256': '26f5433cf37cd33c066dd505672fcb292e7570ede8c823c5a10f9bc21208a473', 'size': 80933}, 'authority_1': {'path': '/workspace/godotsteam-startup-20261013/baseline/Backpack Battles/Sheets/ItemBook.gd', 'sha256': '6b0f0b78c0ee1a0529e7740b424b157837b614cbd74c3e8f22886f9509cb9d84', 'size': 48708}, 'authority_2': {'path': '/workspace/godotsteam-startup-20261013/baseline/Backpack Battles/Items/Item.gd', 'sha256': '7d2bf930d1a0d2ccdf57ccbbc4bbd4c9a3b985a210c42ec8cfa6291e8aae780f', 'size': 170717}, 'authority_3': {'path': '/workspace/godotsteam-startup-20261013/baseline/Backpack Battles/Items/Wolpertinger.gd', 'sha256': '5607b4eea0e69fa4f1f46f2a646e1c3a4c12668be75c45269cf0a2ce6b258ea2', 'size': 522}, 'authority_4': {'path': '/workspace/godotsteam-startup-20261013/baseline/Backpack Battles/Items/Wolpertinger.tscn', 'sha256': '69c0834d5d21b5adb9e6484c71261b0a305ccc192d651cf6ddd14be138ebe462', 'size': 1402}, 'authority_5': {'path': 'data/phase570-independent-mixed-producer-design-review/review.json', 'sha256': 'c5aee2755561feeb2cb6db07f47c8feb238efc39ee4248941daf181e907caa98', 'size': 10914}, 'authority_6': {'path': 'data/phase570-independent-mixed-producer-design-review/owned-files.json', 'sha256': 'f414e138ed4e43115123925ba0330f2c07306545eb68aff29928408c03fe9f79', 'size': 272}, 'authority_7': {'path': 'data/phase569-mixed-producer-schema-design/owned-files.json', 'sha256': 'dd26b088be8ae594f4a0dc5c4b3cc2c42c68bd46026971109a2e2e8ed326ed6e', 'size': 731}, 'authority_8': {'path': 'data/phase543-next-shared-combat-family-plan/actual-source-candidates.json', 'sha256': '3fdd4eb3476ca880dc3a4a8ed7302dc408ba28259067a2c69a9b8fc2ce6bbc45', 'size': 2936}, 'authority_9': {'path': 'data/phase543-next-shared-combat-family-plan/source-pins.json', 'sha256': '4b1046882c6c46680d2c2f321490e6781016496a7547b2cad303df3019682138', 'size': 5984}, 'authority_10': {'path': 'data/phase544-independent-wolpertinger-design-review/review.json', 'sha256': '1ed358c4b5dadc84d2f5826aaa581ad3956f41b8f15661faf0fccc343c0952a6', 'size': 10601}, 'authority_11': {'path': 'data/phase545-source-wolpertinger/source-context.json', 'sha256': '4900d657df442793bac0db0493e8d30fad41ac45f710418d95ff8cf37e9e6459', 'size': 7040}, 'authority_12': {'path': 'data/phase571-root-future030-source-binding/source-binding.json', 'sha256': '09c8e95ba808339412e2259fa4577e32332f9399e23b44995eba313b8614816b', 'size': 1265}, 'authority_13': {'path': 'data/phase571-root-future030-source-binding/owned-files.json', 'sha256': 'ddcad30477274d30e0307195a1e8f2de75cad4c183daed9ee50ba4a6c732dcf2', 'size': 454}, 'authority_14': {'path': 'data/phase502-whelp-observer-source-v4/source-tuple.json', 'sha256': '026877626166fe632c08bd3cba28aec191561373b2167f3c6d15d1f1fac86658', 'size': 2001}, 'authority_15': {'path': 'data/phase502-whelp-observer-source-v4/combined-source-freeze.json', 'sha256': '04e152576b706f66da05d33fe493670604eca14110cbe98e73ee5f3703afb44a', 'size': 58760}, 'authority_16': {'path': 'data/phase502-whelp-observer-source-v4/native-patch-source.json', 'sha256': '3425d9aff911e076c57b7dc89e48e67003e95a42df99ffff732f002b132e77fc', 'size': 31034}, 'authority_17': {'path': 'data/phase528-input-birth-guard-repair-source/source-context.json', 'sha256': 'cbd0862d9ce5d0a7d57db71612bf4945c672f4c9963d77648e72605c06f99d95', 'size': 7440}, 'authority_18': {'path': 'tests/phase528_initial_receipt.py', 'sha256': '95173bc927049e101c7a3d696ebad050eabf744adb5ddec00ba3db9e3650963a', 'size': 16745}, 'authority_19': {'path': 'data/phase566-independent-final-acceptance/review.json', 'sha256': '37609aabbdfd5cfce50f02a7c4677f499282328903be0136d540e62747476c49', 'size': 24506}, 'authority_20': {'path': 'docs/phase564_joint_native_followup_plan_spec.md', 'sha256': '87e5ae43ad5af37f034c5d33bad6417befe4a99360d5a6f40010398144329ff4', 'size': 13385}, 'food_release': {'path': 'data/phase572-root-food-binding-addendum/release.json', 'size': 697, 'sha256': '48e5abc63f07364973d5c7e0d5d572c6951563ae2f56297b1aef9b86d3d461aa'}}

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
        self.replace('\n' + ast.get_source_segment(self.text, nodes[0]) + '\n', '\n' + name + ' = ' + expression + '\n')

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

def assignment(text, name):
    nodes = [n for n in ast.parse(text).body if isinstance(n, ast.Assign)
             and any(isinstance(t, ast.Name) and t.id == name for t in n.targets)]
    require(len(nodes) == 1, 'one assignment: ' + name)
    return ast.literal_eval(nodes[0].value)


def verify_preimages():
    sources = {}
    for name, pin in PINS.items():
        path = ROOT / pin['path']
        require(descriptor(path) == pin, 'pinned Source drift: ' + name)
        sources[name] = path
    patch = json.loads(read_source(sources['patch']))
    require(len(patch['paths']) == 76, 'accepted502 patch target count')
    inherited = []
    for target, row in patch['paths'].items():
        pin = descriptor(ROOT / row['after_path'])
        require({k:pin[k] for k in ('size','sha256')} == row['after'], 'inherited Source drift: ' + target)
        inherited.append(dict(target=target,source=pin,before=row['before']))
    draft = json.loads(read_source(sources['root_draft']))
    require(draft['case_id'] == CASE and draft['global_seed'] == 57101 and draft['util_seed'] == 57102
            and draft['status'] == 'SOURCE_DRAFT_NOT_EXECUTION_AUTHORITY', 'Root Source draft')
    require(draft['authority'] == dict(Source_preparation_only=True,install=False,parse=False,capture=False,
                                     cleanup=False,host_execution=False), 'no operational authority')
    return sources, patch, inherited


def build_plan(sources):
    job = json.loads(read_source(sources['job']))
    aliases = json.loads(read_source(sources['aliases']))['slots']
    layout = job['layout']
    require([len(s['items']) for s in layout['sides']] == [23,6], 'presealed P23/O6')
    require(sorted({i['item_index'] for s in layout['sides'] for i in s['items']}) == IDS, 'twelve fixed descriptors')
    catalog = next(n.value for n in ast.parse(read_source(sources['sdk'])).body if isinstance(n,ast.Assign)
        and any(isinstance(t,ast.Name) and t.id == 'CATALOG' for t in n.targets))
    shapes = {ast.literal_eval(k):ast.literal_eval(next(w.value for w in v.keywords if w.arg=='shape'))
              for k,v in zip(catalog.keys,catalog.values) if ast.literal_eval(k) in IDS}
    slots, fixtures = [], {}
    for side in layout['sides']:
        require(side['character_class'] == 0 and side['stamina'] == 5, 'class0/default stamina')
        fixtures[side['side']] = dict(schema_version=1,game_version='1.1.8',**{'class':0},
            health=side['hp'],stamina=side['stamina'],items=[])
        for ordinal,item in enumerate(side['items']):
            require(type(item['f']) is int and item['f'] == 0, 'fixed presealed orientation0')
            spec = dict(side=side['side'],input_slot=ordinal,instance_id=side['side']+':'+str(ordinal),
                item_index=item['item_index'],x=item['x'],y=item['y'],f=item['f'],
                cells=[[item['x']+dx,item['y']+dy] for dx,dy in shapes[item['item_index']]])
            slots.append(spec)
            fixtures[side['side']]['items'].append({k:item[k] for k in ('item_index','x','y','f')})
    require(len(slots) == len(aliases) == 29, '29 slots')
    for actual, sealed in zip(slots,aliases):
        require(all(actual[k] == sealed[k] for k in ('side','input_slot','item_index','x','y','f'))
                and actual['instance_id'] == sealed['native_alias'], 'presealed slot bijection')
    fixture = dict(schema=1,game_version='1.1.8',mode='Unranked',round=1,rules='default',below_master=None,
        sides=[dict(side=s['side'],character_class=0,hp=float(s['hp']),stamina=float(s['stamina']),
          items=[{k:row[k] for k in ('instance_id','item_index','x','y','f')}
                 for row in slots if row['side']==s['side']]) for s in layout['sides']])
    config = dict(schema='native-combat-capture/1',case_id=CASE,global_seed=57101,util_seed=57102,
        player_fixture_enabled=True,timeouts=dict(battle_seconds=120,total_seconds=295))
    business = ['tick:P','tick:O','fatigue:start','fatigue:tick'] + ['buff:'+s+':'+str(i) for s in ('P','O') for i in range(100,111)]
    inactive = ['invu:'+s for s in ('P','O')] + ['aux:'+s+':'+n for s in ('P','O') for n in ('battleRageTimer','autoRageTimer')]
    return dict(schema='phase572-fixed-source-plan/1',profile=PROFILE,version=VERSION,source_case=SOURCE_CASE,
        native_case=CASE,proposed_run='original030-mixed-modifiers-A-single-001',slots=slots,fixture=fixture,
        native_fixtures=fixtures,config=config,source_bijection=aliases,
        timers=dict(raw=business+inactive,business=business,inactive_diagnostics=inactive),
        proposed_counts=dict(items=29,raw_timers=32,business_timers=26,inactive_diagnostics=6,processing_nodes=67,configs=66),
        native_facts=None,native_below_master=None,status='SOURCE_ONLY_NOT_OPERATIONAL')


def derive_item(path):
    d = Delta(path,'gd')
    d.function('trigger', [('Util.flip(doubleActivationChance)',
        'Util.flip(doubleActivationChance, "double_activation:" + NativeRandomObserver.item_id(self))')])
    d.function('getLeastStacks', [('while numStacks > 0:', 'var observer_least_ordinal = 0\n\twhile numStacks > 0:'),
        ('Util.pickRandomElement(leastStacks)', 'Util.pickRandomElement(leastStacks, "least_buff:" + NativeRandomObserver.item_id(self) + ":" + NativeRandomObserver.side(target) + ":" + str(observer_least_ordinal))'),
        ('numStacks -= 1', 'numStacks -= 1\n\t\tobserver_least_ordinal += 1')])
    return d


MIXED_FACTS = '''func selected_king_facts(items, characters):
	begin_encoding()
	var result = {"schema": "phase572-zero-king-input-facts/1", "root_viewport": node_state(get_tree().get_root()), "timers": {}, "kings": [], "delayed_activation": king_delayed, "items": []}
	if items.size() != SOURCE_SLOT_TABLE.size() or characters.size() != 2:
		fail("MIXED_FACT_COUNT", "selected_king_facts")
		return null
	for character in characters:
		var label = ids.get(character.get_instance_id(), "UNREGISTERED")
		if not label in ["P", "O"]:
			fail("MIXED_CHARACTER_ROLE", "selected_king_facts")
			return null
		result.timers["invu:" + label] = king_timer_fact(character.invulnerabilityTimer, character, "Character.scene.ready", 0)
	var enchantment = []
	for item in items:
		if ids.get(item.get_instance_id(), "UNREGISTERED") == "P:19":
			if item.descriptor.itemIndex != 385 or not item.cachedAffectedItems.has(0):
				fail("MIXED_ENCHANT_CACHE", "selected_king_facts")
				return null
			for target in item.cachedAffectedItems[0]:
				if not target in items or not ids.get(target.get_instance_id(), "UNREGISTERED") in ["P:15", "P:16", "P:17", "P:18"] or target.character() != item.character() or target in enchantment:
					fail("MIXED_ENCHANT_TARGET", "selected_king_facts")
					return null
				enchantment.append(target)
	for item in items:
		var label = ids.get(item.get_instance_id(), "UNREGISTERED")
		var index = item.descriptor.itemIndex
		if not index in [1, 5, 11, 14, 22, 32, 162, 164, 231, 233, 234, 385] or not source_is(item, "res://Items/Item.gd") or item.has_method("getDataPersistent") or not item.getGemsNoNull().empty() or not item.paramMult.empty() or not item.paramAdd.empty():
			fail("MIXED_UNSUPPORTED_ITEM_MODIFIER", "selected_king_facts")
			return null
		var activation_chance = 0.2 if label in ["P:13", "P:14"] else 0.0
		var attack_chance = 0.25 if item in enchantment else 0.0
		if item.doubleActivationChance != activation_chance or item.doubleAttackEffectChance != attack_chance:
			fail("MIXED_PREPARED_CHANCES", "selected_king_facts")
			return null
		if index in [162, 164, 231, 385] and item.sockets.size() != 0:
			fail("MIXED_SOCKET_COUNT", "selected_king_facts")
			return null
		var sockets = []
		for socket in item.sockets:
			sockets.append({"node": node_state(socket), "gem": encode(socket.getGem())})
		result.items.append({"instance": label, "node": node_state(item), "descriptorIndex": encode(index), "sockets": sockets, "gem_count": item.getGemsNoNull().size(), "persistent": item.has_method("getDataPersistent"), "paramMult": encode(item.paramMult), "paramAdd": encode(item.paramAdd), "doubleActivationChance": encode(item.doubleActivationChance), "doubleAttackEffectChance": encode(item.doubleAttackEffectChance)})
	return result'''


def derive_sink(path, plan):
    d = Delta(path,'gd')
    caps = json.loads(re.search(r'^const CAPS = (.+)$',d.text,re.M).group(1));caps['descriptors']=12
    states = json.loads(re.search(r'^const STATE_SCHEMAS = (.+)$',d.text,re.M).group(1))
    common = dict(states['item'],doubleActivationChance='float',doubleAttackEffectChance='float')
    states['item'] = common
    states['bowl'] = dict(common,speedBonusGiven='float')
    states['wolper'] = dict(common,staminaRegenPerBuff='null|float',numBuffs='int')
    states['enchanted'] = dict(common,buffs='int')
    for name,value in [('CAPS',caps),('STATE_SCHEMAS',states),('SOURCE_SLOT_TABLE',plan['slots']),('RNG_INITIAL_PROFILE',VERSION)]:
        d.gd_constant(name,value)
    d.function('state',[('[1, 11, 22, 23, 64, 164, 197, 199, 201]',repr(IDS)),
        ('"goobert" if index == 23 else ("sapphire" if index == 199 else "item")',
         '"bowl" if index == 162 else ("wolper" if index == 231 else ("enchanted" if index == 385 else "item"))')])
    d.function('context', [('elif label.begins_with("squirrel_activation_pitch:"):',
        'elif label.begins_with("least_buff:"):\n\t\tresult.item = parts[1] + ":" + parts[2]\n\t\tresult.target = parts[3]\n\t\tresult.operation = "least"\n\t\tresult.ordinal = int(parts[4])\n\telif label.begins_with("double_activation:"):\n\t\tresult.item = parts[1] + ":" + parts[2]\n\telif label.begins_with("squirrel_activation_pitch:"):')])
    d.function('source_resources',[('"buffs": rows}',
        '"buffs": rows, "baseStaminaRegen": encode(character.baseStaminaRegen), "staminaRegen": encode(character.staminaRegen)}')])
    d.replace(gd_functions(d.text)['selected_king_facts'],MIXED_FACTS)
    d.function('bind_fixed_inventory',[('return metadata([1, 11, 22, 23, 64, 164, 197, 199, 201])', 'return metadata('+repr(IDS)+')')])
    for name in ('ui_open','rng_initial_capture'):
        d.function(name,[('WHELP-FAMILY-A-502',SOURCE_CASE)])
    return d


def derive_collector(path,plan):
    d = Delta(path,'gd')
    for name,value in [('SOURCE_P',plan['native_fixtures']['P']),('SOURCE_O',plan['native_fixtures']['O']),
                       ('SOURCE_CONFIG',plan['config']),('PLAYER_ITEM_WHITELIST',IDS)]:
        d.gd_constant(name,value)
    d.function('state_snapshot',[('\t\t\tvar observer7_timers = {}',
        '\t\t\tif item.descriptor.itemIndex == 162:\n\t\t\t\tobserver7_fields = fields(item, ["speedBonusGiven"])\n\t\t\telif item.descriptor.itemIndex == 231:\n\t\t\t\tobserver7_fields = fields(item, ["staminaRegenPerBuff", "numBuffs"])\n\t\t\telif item.descriptor.itemIndex == 385:\n\t\t\t\tobserver7_fields = fields(item, ["buffs"])\n\t\t\tvar observer7_timers = {}')])
    d.function('on_idle_source_cut',[('phase502-zero-King-whelp-oracle-only','phase572-zero-King-mixed-oracle-only')])
    return d
MIXED_DEFAULTS = '''def validate_single_king_source_defaults(pre, act):
    """Read observed new-profile stages; Source0.7 is not a metadata getter."""
    for record in (pre, act):
        nodes, items, natives, roles = _binding_checkpoint(record)
        validate_resources(record['payload']['source_resources'], record['payload']['nodes'])
        for role, item in items.items():
            fields = item['fields']
            validate_state(fields, 'item')
            index = ITEM_INDEX_BY_ROLE[role]
            if fields['descriptorIndex'] != {'type':'int','decimal':str(index)}:
                raise ValueError('mixed observed descriptor identity')
            if index == 231:
                if fields['numBuffs'] != {'type':'int','decimal':'3'}:
                    raise ValueError('Wolper selected post-ready INT3')
                coefficient = fields['staminaRegenPerBuff']
                if record is act:
                    _single_king_typed(coefficient, 'float')
                if coefficient['type'] == 'float':
                    scalar_number(coefficient)
            elif index == 385 and fields['buffs'] != {'type':'int','decimal':'1'}:
                raise ValueError('Enchanted selected post-ready INT1')
            elif index == 162:
                _single_king_typed(fields['speedBonusGiven'], 'float', '0000000000000000')
            if record is pre:
                for key in ('doubleActivationChance','doubleAttackEffectChance'):
                    _single_king_typed(fields[key], 'float', '0000000000000000')
    return dict(kind='SOURCE_DEFAULTS_PROOF_ONLY_NOT_RUNTIME', phases=['pre_prepare','pre_activate'],
                p1='SOURCE_DERIVED_DEFAULT_P1_NOT_OBSERVED_METADATA', pooled_admitted=False)'''

MIXED_JOIN = '''def _validate_mixed_prepared_facts(facts, pre, act, meta):
    """Four-argument read-only production join; called after all29 lineage joins."""
    validate_single_king_fresh_facts(facts)
    validate_single_king_source_defaults(pre, act)
    nodes, items, natives, roles = _binding_checkpoint(act)
    meta_by_index = {}
    for encoded in meta['payload']['descriptors']['values']:
        fields = argument_fields(encoded)
        index = _binding_integer_value(fields['itemIndex'])
        if index in meta_by_index:
            raise ValueError('mixed duplicate metadata descriptor')
        meta_by_index[index] = fields
    if set(meta_by_index) != DESCRIPTOR_IDS or meta_by_index[231]['scene_path'] != {'type':'string','value':'res://Items/Wolpertinger.tscn'}:
        raise ValueError('fixed default Wolper descriptor/scene Source premise')
    # The Source-bound default loading/getP1 premise is separate from empty maps.
    # Metadata has no p1 property; do not infer it or accept a caller certificate.
    if SOURCE_DERIVED_DEFAULT_P1 != 0.7 or struct.pack('>d',SOURCE_DERIVED_DEFAULT_P1).hex() != '3fe6666666666666':
        raise ValueError('Source-only default p1 rule drift')
    enchanted = items['P:19']['fields']
    cache = enchanted['cachedAffectedItems']
    validate_cache(cache, False)
    primary = [entry['value'] for entry in cache['entries'] if entry['key'] == {'type':'int','decimal':'0'}]
    if len(primary) != 1 or primary[0]['type'] != 'array':
        raise ValueError('actual prepared Enchanted primary cache')
    affected = set()
    for ref in primary[0]['values']:
        validate_typed(ref)
        role = ref.get('role')
        if (ref['type'] != 'native_ref' or role not in ('P:15','P:16','P:17','P:18')
                or role in affected or ref['native_id'] != roles[role]
                or ref['class'] != nodes['item:' + role]['class']):
            raise ValueError('prepared cache receiver/UID/class/same-side association')
        affected.add(role)
    fact_items = {row['instance']:row for row in facts['items']}
    if set(fact_items) != FIXED_ROLES:
        raise ValueError('all29 prepared facts')
    resources = {row['side']:row for row in act['payload']['source_resources']}
    for role, item in items.items():
        fields, fact = item['fields'], fact_items[role]
        if fact['node'] != nodes['item:' + role] or fact['descriptorIndex'] != fields['descriptorIndex']:
            raise ValueError('prepared fact/checkpoint actual object join')
        for key, number in (('doubleActivationChance', .2 if role in ('P:13','P:14') else 0.0),
                            ('doubleAttackEffectChance', .25 if role in affected else 0.0)):
            expected = {'type':'float','binary64_be':struct.pack('>d',number).hex()}
            if fields[key] != expected or fact[key] != fields[key]:
                raise ValueError('prepared actual modifier/cache/fact agreement: ' + role + ':' + key)
        if ITEM_INDEX_BY_ROLE[role] == 231:
            side = role[0]
            resource = resources[side]
            if resource['native_id'] != roles[side]:
                raise ValueError('Wolper actual same-cut Character')
            _single_king_typed(resource['baseStaminaRegen'], 'float')
            _single_king_typed(resource['staminaRegen'], 'float')
            base = scalar_number(resource['baseStaminaRegen'])
            coefficient = (SOURCE_DERIVED_DEFAULT_P1 * base) / 100.0
            expected = {'type':'float','binary64_be':struct.pack('>d',coefficient).hex()}
            if fields['staminaRegenPerBuff'] != expected:
                raise ValueError('Wolper observed REAL coefficient/source-default/actual base relationship')
    return None'''

PRIMITIVE_CONTEXT = '''def primitive_context(label, kind):
    if label.startswith('double_activation:'):
        if label not in ('double_activation:P:13','double_activation:P:14') or kind != 'randf':
            raise ValueError('fixed Pet positive-only extra-activation primitive')
        return dict.fromkeys(CONTRACT['primitive_context_exact']) | {'item':label.split(':',1)[1]}
    if label.startswith('least_buff:'):
        match = re.fullmatch(r'least_buff:(P:13|O:4|P:19):([PO]):([0-9]+)',label)
        if match is None or kind != 'randi_range':
            raise ValueError('fixed least-buff primitive context')
        item, target, ordinal = match.groups()
        ordinal = int(ordinal)
        if target != item[0] or ordinal not in (range(1) if item == 'P:19' else range(3)):
            raise ValueError('least-buff actual target/call ordinal')
        return dict.fromkeys(CONTRACT['primitive_context_exact']) | dict(item=item,target=target,operation='least',ordinal=ordinal)
    if label.startswith('squirrel_activation_pitch:'):
        if label != 'squirrel_activation_pitch:P:14' or kind != 'randf_range':
            raise ValueError('fixed selected Squirrel pitch context')
        return dict.fromkeys(CONTRACT['primitive_context_exact']) | {'item':'P:14'}
    result = _base_primitive_context(label,kind)
    if result['item'] not in (None,'null') and result['item'] not in FIXED_ROLES:
        raise ValueError('primitive unknown selected item role')
    return result'''


def derive_schema(path, plan, binding_contract):
    d = Delta(path,'py')
    contract = assignment(d.text,'CONTRACT')
    contract['caps']['descriptors'] = 12
    common = dict(contract['state_schemas']['item'],doubleActivationChance='float',doubleAttackEffectChance='float')
    contract['state_schemas']['item'] = common
    contract['state_schemas']['plain_item'] = dict(common)
    contract['state_schemas']['bowl'] = dict(common,speedBonusGiven='float')
    contract['state_schemas']['wolper'] = dict(common,staminaRegenPerBuff='null|float',numBuffs='int')
    contract['state_schemas']['enchanted'] = dict(common,buffs='int')
    values = dict(VERSION=repr(VERSION),PROFILE=repr(PROFILE),DESCRIPTOR_IDS='frozenset('+repr(IDS)+')',
        CONTRACT=repr(contract),SINGLE_KING_GENUINE_PROFILE=repr(PROFILE),SINGLE_KING_OBSERVER_VERSION=repr(VERSION),
        SINGLE_KING_CASE=repr(SOURCE_CASE),SINGLE_KING_ITEMS='frozenset('+repr(IDS)+')',
        SINGLE_KING_FIXTURE_SHA256=repr(canonical(plan['fixture'])),
        SINGLE_KING_ROLES='frozenset('+repr([s['instance_id'] for s in plan['slots']])+')',
        FIXED_FIXTURE=repr(plan['fixture']),ITEM_INDEX_BY_ROLE=repr({s['instance_id']:s['item_index'] for s in plan['slots']}),
        TIMER_ROLES='frozenset('+repr(plan['timers']['raw'])+')',BINDING_FIXED_PLAN=repr(plan['slots']),
        BINDING_SOURCE_CONTRACT=repr(binding_contract))
    for name,value in values.items():d.py_constant(name,value)
    d.replace('import ast\n', 'import ast\n') if False else None
    # A literal Source-derived constant, not an added observation or caller proof flag.
    old = next(ast.get_source_segment(d.text,n) for n in ast.parse(d.text).body if isinstance(n,ast.Assign)
               and any(isinstance(t,ast.Name) and t.id=='VERSION' for t in n.targets))
    d.replace('\n'+old+'\n','\n'+old+'\nSOURCE_DERIVED_DEFAULT_P1 = 0.7\n')
    d.function('validate_single_king_fresh_facts',[
        ('phase502-zero-king-input-facts/1','phase572-zero-king-input-facts/1'),
        ("            _single_king_typed(item[key],'float','0000000000000000')",
         "            _single_king_typed(item[key],'float')\n            number = scalar_number(item[key])\n            allowed = (0.0,0.2) if key == 'doubleActivationChance' else (0.0,0.25)\n            if number not in allowed:\n                raise ValueError('bounded observed prepared modifier')"),
        ("if index in (64,197,199,201) and len(sockets) != 1 or index == 164 and len(sockets) != 0:",
         "if index in (162,164,231,385) and len(sockets) != 0:"),
        ('Whelp/Squirrel actual socket count','mixed no-socket subtype count')])
    d.replace(py_functions(d.text)['validate_single_king_source_defaults'],MIXED_DEFAULTS)
    d.function('validate_state',[
        ("('item', 'goobert', 'king', 'potion', 'plain_item', 'sapphire')", "('item', 'goobert', 'king', 'potion', 'plain_item', 'sapphire', 'bowl', 'wolper', 'enchanted')"),
        ("actual = 'goobert' if index == 23 else 'sapphire' if index == 199 else 'plain_item'",
         "actual = 'bowl' if index == 162 else 'wolper' if index == 231 else 'enchanted' if index == 385 else 'plain_item'"),
        ("or kind == 'sapphire' and actual != 'sapphire':",
         "or kind == 'sapphire' and actual != 'sapphire' or kind in ('bowl','wolper','enchanted') and actual != kind:"),
        ('fixed nine IDs','fixed twelve IDs'),
        ("    if kind == 'sapphire':\n", "    if kind == 'wolper' and value['numBuffs'] != {'type':'int','decimal':'3'}:\n        raise ValueError('post-ready Wolper INT3')\n    if kind == 'enchanted' and value['buffs'] != {'type':'int','decimal':'1'}:\n        raise ValueError('post-ready Enchanted INT1')\n    if kind == 'bowl' and scalar_number(value['speedBonusGiven']) < 0:\n        raise ValueError('Bowl actual nonnegative REAL ledger')\n    if kind == 'sapphire':\n")])
    d.function('validate_resources',[
        ("('side', 'native_id', 'buffProtectStacks', 'debuffReflectStacks', 'buffs')",
         "('side', 'native_id', 'buffProtectStacks', 'debuffReflectStacks', 'buffs', 'baseStaminaRegen', 'staminaRegen')"),
        ("        if type(row['buffs']) is not list", "        for name in ('baseStaminaRegen','staminaRegen'):\n            _single_king_typed(row[name], 'float')\n            scalar_number(row[name])\n        if type(row['buffs']) is not list")])
    d.replace(py_functions(d.text)['primitive_context'],PRIMITIVE_CONTEXT)
    d.function('validate_primitive',[("'squirrel_activation_pitch:P:10'","'squirrel_activation_pitch:P:14'"),
        ("    return _base_validate_primitive(payload)",
         "    if payload.get('label','').startswith('least_buff:'):\n        args = payload.get('args')\n        if type(args) is not list or len(args) != 2 or args[0] != {'type':'int','decimal':'0'}:\n            raise ValueError('least-buff INT0 lower endpoint')\n        validate_typed(args[1])\n        if args[1]['type'] != 'int' or not 0 <= decimal(args[1]['decimal']) <= 6:\n            raise ValueError('least-buff bounded actual INT upper endpoint')\n    return _base_validate_primitive(payload)")])
    d.function('_base_validate_record',[("('accuracy:','critical:','item_chance:','double_attack_effect:')",
        "('accuracy:','critical:','item_chance:','double_attack_effect:','double_activation:')"),
        ("('random_stack:',)","('random_stack:','least_buff:')")])
    d.function('validate_record',[
        ("if site == 'Items/Food.gd::prepare' and state['descriptorIndex'] != {'type': 'int', 'decimal': '22'}:",
         "if site == 'Items/Food.gd::prepare' and state['descriptorIndex'] not in [{'type':'int','decimal':str(i)} for i in (5,22,162)]:"),
        ('Food.prepare receiver must be original thin-domain Food descriptor INT22','Food.prepare receiver must be fixed-profile Food descriptor INT5/22/162')])
    old = py_functions(d.text)['join_binding_provenance']
    needle = "    after = hashlib.sha256(json.dumps(decoded11, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()"
    require(old.count(needle)==1,'full join exact before-mutation-check splice')
    d.replace(old,old.replace(needle,"    _validate_mixed_prepared_facts(decoded11['king-input-facts.json'], pre, act, meta)\n"+needle))
    # Keep final schema exports untouched; insert at the exact complete caller boundary.
    caller = py_functions(d.text)['join_binding_provenance']
    d.replace(caller,MIXED_JOIN+'\n\n\n'+caller)
    return d

def freeze_source(sources,plan,old_patch,inherited,artifacts,reports):
    paths = json.loads(json.dumps(old_patch['paths']))
    for target,name in [('Items/Item.gd','item'),('native_random_observer_sink_v7.gd','sink')]:
        paths[target]['after_path'] = artifacts[name]['path']
        paths[target]['after'] = {k:artifacts[name][k] for k in ('size','sha256')}
    untouched = []
    for row in inherited:
        if row['target'] not in ('Items/Item.gd','native_random_observer_sink_v7.gd'):
            require(paths[row['target']] == old_patch['paths'][row['target']], 'inherited target descriptor exact')
            untouched.append(row)
    require(len(untouched)==74,'74 inherited targets unchanged')
    gd_const = lambda text,name:re.search(r'^const '+name+r' = [^\n]+',text,re.M).group()
    old_sink,new_sink = read_source(sources['sink']).decode(),read_source(ROOT/artifacts['sink']['path']).decode()
    require(gd_const(old_sink,'SITES')==gd_const(new_sink,'SITES'),'107 method SITES byte exact')
    require(len(json.loads(gd_const(new_sink,'SITES').split(' = ',1)[1]))==107,'107 sites')
    old_schema,new_schema = read_source(sources['schema']).decode(),read_source(ROOT/artifacts['schema']['path']).decode()
    matrix = lambda text:next(ast.get_source_segment(text,n) for n in ast.parse(text).body if isinstance(n,ast.Assign)
        and any(isinstance(t,ast.Name) and t.id=='MATRIX' for t in n.targets))
    require(matrix(old_schema)==matrix(new_schema),'MATRIX/Timer API statement bytes exact')
    for name in ('squirrel_pitch','primitive','clock_pass','begin_king_clock','source_tail_begin',
                 'source_tail_note_pass','source_terminal_current','scene_instance','source_observable','entry'):
        require(gd_functions(old_sink)[name]==gd_functions(new_sink)[name],'shared sink body exact: '+name)
    # Original accepted one-call wrappers are not regenerated or modified.
    wrapper = descriptor(sources['squirrel'])
    require(paths['Items/Exclusive/Squirrel.gd']['after_path']==wrapper['path']
            and paths['Items/Exclusive/Squirrel.gd']['after']=={k:wrapper[k] for k in ('size','sha256')},'Squirrel wrapper exact')
    require(paths['Utility/Util.gd']['after_path']==PINS['util_unchanged']['path'],'Utility optional-label wrappers exact')
    require(py_functions(old_schema)['validate_sources_with_binding']==py_functions(new_schema)['validate_sources_with_binding'],
            'complete public caller byte exact')
    patch = dict(schema='phase572-native-patch-source/1',paths=paths,producer=descriptor(Path(__file__)),
        sink=artifacts['sink'],profile=PROFILE,observer_version=VERSION,terminal_policy=old_patch['terminal_policy'],
        status='SOURCE_ONLY_NOT_OPERATIONAL')
    save(OUT/'native-patch-source.json',patch)
    marker = json.loads(read_source(sources['freeze']))['artifacts']['.native-random-observer-disposable']
    require(descriptor(ROOT/marker['path'])==marker,'inherited marker exact')
    install_artifacts = {'native_combat_capture.gd':artifacts['collector'],
        'native_capture_config.json':descriptor(OUT/'case-inputs/native_capture_config.json'),
        '.native-random-observer-disposable':marker}
    targets = [dict(namespace='project',target=name,before=row['before'],source=dict(path=row['after_path'],**row['after']))
        for name,row in paths.items()]
    targets += [dict(namespace='project',target=name,before=None,
        before_policy='Actual predecessor unknown: locked preflight/journal required; not asserted absent',source=pin)
        for name,pin in install_artifacts.items()]
    total = sum(row['source']['size'] for row in targets)
    require(len({row['target'] for row in targets})==len(targets),'unique install target map')
    save(OUT/'install-targets.json',dict(schema='phase572-install-source-inventory/1',project=targets,
        project_install_count=len(targets),project_install_source_bytes=total,
        case_inputs=[dict(target=p.name,source=descriptor(p)) for p in sorted((OUT/'case-inputs').glob('*.json'))],
        actual_pool_preimages_verified=False,host_ready=False,install_or_execute_authorized=False,
        operational_preflight='Fresh physical/resource/space/Source gates remain required; no install attempt here'))
    save(OUT/'source-tuple.json',dict(schema='phase572-zero-king-mixed-observer-source-tuple/1',profile=PROFILE,
        observer_version=VERSION,case=CASE,proposed_run=plan['proposed_run'],global_seed=57101,util_seed=57102,
        terminal_policy=old_patch['terminal_policy'],producer=descriptor(Path(__file__)),sink=artifacts['sink'],
        collector=artifacts['collector'],schema_module=artifacts['schema'],
        direct_primitive_wrapper=wrapper,transparent_callsite_labels=['double_activation','least_buff'],
        fixed_plan=descriptor(OUT/'fixed-plan.json'),fixed_fixture=descriptor(OUT/'fixed-v8-fixture.json'),
        native_patch=descriptor(OUT/'native-patch-source.json'),default_p1_rule=descriptor(OUT/'source-default-p1-rule.json'),
        source_case_draft=descriptor(sources['root_draft']),project_install_count=len(targets),
        project_install_source_bytes=total,status='SOURCE_ONLY_NOT_OPERATIONAL',
        model_input_or_runtime_admitted=False,host_execution_ready=False,operational_authority=False,
        actual_Native_UID_cut_cache_clock_setup='UNOBSERVED',actual_Native_below_master=None))
    save(OUT/'conservation.json',dict(schema='phase572-source-conservation/1',
        changed_functions={k:v['changed_functions'] for k,v in reports.items()},
        new_functions={k:v['new_functions'] for k,v in reports.items()},
        unchanged_inherited_targets=untouched,unchanged_inherited_count=74,method_sites=107,new_method_hooks=0,
        MATRIX_Timer_API_statement_bytes_exact=True,Utility_and_Squirrel_wrappers_byte_exact=True,
        inverse='ALL_FOUR_COMPLETE_PREIMAGE_BYTES',
        callsite_observation=dict(trigger='Existing positive-only single Util.flip, same args0/return branch, optional label only',
          least='Existing one pickRandomElement per selection; same array/index/return, added local label ordinal only',
          Util_native_rng_call_count_unchanged=True,ended_or_limiter_filter_added=False,not_native_execution_proof=True),
        pooled_false_full_join_retained=True,complete_public_caller_body_exact=True,
        mixed_helper_splice="_validate_mixed_prepared_facts(decoded11['king-input-facts.json'], pre, act, meta)",
        helper_position='After complete29 identity/lineage/evidence loop, before afterSHA',
        new_food_binding=dict(strict_INT_ids=[5,22,162],other_receiver_join_retained=True),
        native_or_runtime_admission=False))
    compile(read_source(Path(__file__)),str(Path(__file__)),'exec',dont_inherit=True)
    save(OUT/'compile-only.json',dict(schema='phase572-compile-only/1',discarded_compile_objects=2,
        producer_compiled=True,schema_compiled=True,GD_parse=0,generated_schema_imports=0,schema_calls=0,
        controls=0,models=0,Expected_reads=0,Native=0,pool=0,host=0))
    save(OUT/'first-generation-result.json',dict(schema='phase572-source-generation-result/1',
        status='SOURCE_ONLY_NOT_OPERATIONAL_PENDING_INDEPENDENT573',source_generation_invocations=1,
        descriptors=12,slots=29,Kings=0,raw_timers_predicted=32,business_timers_predicted=26,
        project_install_count=len(targets),project_install_source_bytes=total,source_case_draft=descriptor(sources['root_draft']),
        generated_schema_imports=0,schema_helper_calls=0,controls=0,models=0,Godot=0,Native=0,
        Expected_reads=0,pool_operations=0,actual_native_canAdd='UNOBSERVED',actual_native_below_master=None))
    external = list(PINS.values()) + [row['source'] for row in inherited] + [marker]
    files = [descriptor(p) for p in sorted(OUT.rglob('*')) if p.is_file()]
    unique = {}
    for pin in files+external+[descriptor(Path(__file__)),descriptor(ROOT/SPEC)]:
        require(pin['path'] not in unique or unique[pin['path']]==pin,'conflicting Source descriptor')
        unique[pin['path']]=pin
    save(OUT/'combined-source-freeze.json',dict(schema='phase572-source-freeze/1',files=list(unique.values()),
        paths=paths,artifacts=install_artifacts,collector=artifacts['collector'],schema_module=artifacts['schema'],
        active_source_tuple=descriptor(OUT/'source-tuple.json'),profile=PROFILE,observer_version=VERSION,
        terminal_policy=old_patch['terminal_policy'],project_install_count=len(targets),project_install_source_bytes=total,
        status='SOURCE_ONLY_NOT_OPERATIONAL',host_ready=False,model_runtime_admitted=False,
        Godot_parse=0,Native=0,models=0,schema_helper_calls=0))
    unique[str((OUT/'combined-source-freeze.json').relative_to(ROOT))] = descriptor(OUT/'combined-source-freeze.json')
    save(OUT/'source-owner.json',dict(schema='phase572-source-owner/1',files=list(unique.values()),
        no_more_writes=True,status='SOURCE_ONLY_PENDING_INDEPENDENT573_NO_OPERATIONAL_RELEASE'))
    return descriptor(OUT/'source-owner.json')


def main():
    require(not OUT.exists(),'unique Source output already exists')
    OUT.mkdir()
    save(OUT/'generation-started.json',dict(schema='phase572-generation-started/1',attempt=1,
        producer=descriptor(Path(__file__)),spec=descriptor(ROOT/SPEC),Native=0,models=0))
    try:
        sources,patch,inherited = verify_preimages()
        save(OUT/'source-before.json',dict(files=list(PINS.values()),inherited_targets=inherited))
        plan = build_plan(sources)
        save(OUT/'fixed-plan.json',plan)
        save(OUT/'fixed-v8-fixture.json',plan['fixture'])
        for name,value in [('custom_player.json',plan['native_fixtures']['P']),('custom_opponent.json',plan['native_fixtures']['O']),
                           ('native_capture_config.json',plan['config'])]:save(OUT/'case-inputs'/name,value)
        conditions = json.loads(read_source(sources['conditions']))
        save(OUT/'source-default-p1-rule.json',dict(schema='phase572-source-default-p1-rule/1',
            rule=conditions['p1_rule'],Original_default_authority=conditions['Original_default_authority'],
            getP1_chain=conditions['getP1_chain'],conditions=descriptor(sources['conditions']),
            observation=False,new_getter=False,alternate_descriptor_params_or_pooled_admitted=False))
        save(OUT/'source-authority.json',dict(schema='phase572-source-authority/1',producer=descriptor(Path(__file__)),
            spec=descriptor(ROOT/SPEC),origin={k:descriptor(p) for k,p in sources.items()},
            default_p1_rule=descriptor(OUT/'source-default-p1-rule.json'),
            scope='SOURCE_ONLY_NOT_OPERATIONAL_NO_NATIVE_INPUT_OR_RUNTIME_ADMISSION'))
        contract = dict(schema='phase360-binding-source-contract/1',schema_origin=descriptor(sources['schema']),
            producer_source_origin=descriptor(OUT/'source-authority.json'),fixed_slot_map=descriptor(OUT/'fixed-plan.json'),
            fixed_fixture=descriptor(OUT/'fixed-v8-fixture.json'),evidence_policy='SOURCE_ORIGIN_ONLY_NO_NATIVE_ID_OR_ADMISSION')
        save(OUT/'binding-source-contract.json',contract)
        derived = [('item',derive_item(sources['item']),OUT/'after-source/Items/Item.gd',['trigger','getLeastStacks'],[]),
            ('sink',derive_sink(sources['sink'],plan),OUT/'after-source/native_random_observer_sink_v7.gd',
              ['state','context','source_resources','selected_king_facts','bind_fixed_inventory','ui_open','rng_initial_capture'],[]),
            ('collector',derive_collector(sources['collector'],plan),OUT/'collector.gd',['state_snapshot','on_idle_source_cut'],[]),
            ('schema',derive_schema(sources['schema'],plan,contract),OUT/'schema/phase572_mixed_observer_schema.py',
              ['validate_single_king_fresh_facts','validate_single_king_source_defaults','validate_state','validate_resources',
               'primitive_context','validate_primitive','_base_validate_record','validate_record','join_binding_provenance'],
              ['_validate_mixed_prepared_facts'])]
        artifacts,reports = {},{}
        for name,delta,path,changed,added in derived:
            artifacts[name],reports[name] = delta.finish(path,changed,added)
        owner = freeze_source(sources,plan,patch,inherited,artifacts,reports)
        print(json.dumps(dict(status='SOURCE_FROZEN_NO_RUNTIME_EXECUTION',owner=owner),sort_keys=True))
        return 0
    except Exception as error:
        save(OUT/'first-generation-error.json',dict(schema='phase572-generation-first-error/1',
            error_type=type(error).__name__,message=str(error),traceback=traceback.format_exc(),automatic_retry=False,
            generated_schema_imports=0,schema_helper_calls=0,models=0,Godot=0,Expected=0,pool_operations=0))
        partial = [descriptor(p) for p in sorted(OUT.rglob('*')) if p.is_file()]
        save(OUT/'partial-source-owner.json',dict(schema='phase572-partial-source-owner/1',files=partial+
            [descriptor(Path(__file__)),descriptor(ROOT/SPEC)],status='FIRST_GENERATION_ERROR_PRESERVED_NO_RETRY'))
        raise


if __name__ == '__main__':
    raise SystemExit(main())
