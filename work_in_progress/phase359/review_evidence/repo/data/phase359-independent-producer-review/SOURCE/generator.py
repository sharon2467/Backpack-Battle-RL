"""Generate observation-only GD SOURCE in a new directory. No apply/native API."""
from pathlib import Path
import ast
from copy import deepcopy
import difflib
import hashlib
import json
import re

R = Path(__file__).resolve().parents[1]
D = R / 'data/phase359-king-producer-source'
BASE = Path('/workspace/godotsteam-startup-20261013/baseline/Backpack Battles')


def pin_bytes(raw):
    return dict(size=len(raw), sha256=hashlib.sha256(raw).hexdigest())


def pin(path):
    return pin_bytes(path.read_bytes())


def save(name, value):
    with (D / name).open('x') as stream:
        stream.write(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + '\n')


def functions(source):
    lines = source.splitlines(keepends=True)
    found = {}
    for i, line in enumerate(lines):
        match = re.match(r'^(\t*)func (\w+)\(', line)
        if not match:
            continue
        indent, name = len(match[1]), match[2]
        end = i + 1
        while end < len(lines):
            stripped = lines[end].lstrip()
            if stripped.strip() and not stripped.startswith('#') and len(lines[end]) - len(stripped) <= indent:
                break
            end += 1
        if indent:
            if name != '_init' or not any(x.startswith('class TemporaryStacks extends Reference:') for x in lines[:i]):
                continue
            name = 'TemporaryStacks._init'
        found[name] = (i, end, indent)
    return lines, found


def fn_text(source, name):
    lines, table = functions(source)
    a, z, _ = table[name]
    return ''.join(lines[a:z])


def hook_function(source, site, spec):
    name = site.split('::', 1)[1]
    lines, table = functions(source)
    a, z, level = table[name]
    block = lines[a:z]
    if 'NativeRandomObserver.entry(' + json.dumps(site) in ''.join(block):
        return source
    if 'observer359_' in ''.join(block):
        raise ValueError('new temporary name collision ' + site)
    head = next(i for i, line in enumerate(block) if re.search(r'\)\s*(?:->[^:]+)?\s*:\s*$', line))
    indent = '\t' * (level + 1)
    args = '{' + ', '.join(json.dumps(arg) + ': ' + arg for arg in spec['arguments_exact']) + '}'
    result = block[:head + 1] + [indent + 'NativeRandomObserver.entry(' + json.dumps(site) + ', self, ' + args + ')\n']
    serial = 0
    for line in block[head + 1:]:
        raw = line.rstrip('\r\n')
        match = re.match(r'^(\t*)(.*?)(?:\breturn)(?:\s+(.*))?$', raw)
        if not match or raw.lstrip().startswith('#'):
            result.append(line)
            continue
        tabs, prefix, expression = match.groups()
        if prefix.strip():
            if not prefix.rstrip().endswith(':'):
                raise ValueError('unsupported inline return ' + site)
            result.append(tabs + prefix.rstrip() + '\n')
            tabs += '\t'
        if expression is None:
            result.extend([tabs + 'NativeRandomObserver.leave(' + json.dumps(site) + ', self, null, "return_explicit")\n', tabs + 'return\n'])
        else:
            variable = 'observer359_return_' + str(serial)
            serial += 1
            result.extend([tabs + 'var ' + variable + ' = ' + expression + '\n',
                           tabs + 'NativeRandomObserver.leave(' + json.dumps(site) + ', self, ' + variable + ', "return_explicit")\n',
                           tabs + 'return ' + variable + '\n'])
    significant = [line.rstrip('\r\n') for line in block[head + 1:] if line.strip() and not line.lstrip().startswith('#')]
    final_unconditional_return = bool(significant and len(significant[-1]) - len(significant[-1].lstrip('\t')) == level + 1 and significant[-1].lstrip().startswith('return'))
    if not final_unconditional_return:
        while result and not result[-1].strip():
            result.pop()
        result.append(indent + 'NativeRandomObserver.leave(' + json.dumps(site) + ', self, null, "return_implicit")\n\n')
    return ''.join(lines[:a] + result + lines[z:])


def main():
    D.mkdir(exist_ok=False)
    schema = R / 'tests/phase358_king_observer_schema.py'
    assert pin(schema) == dict(size=259033, sha256='d8dabd87ffe0352ceb886ad3f25c2548d1e4412d13538da813ba77f8115947a7')
    assignments = {target.id: node.value for node in ast.parse(schema.read_text()).body if isinstance(node, ast.Assign)
                   for target in node.targets if isinstance(target, ast.Name)}
    contract = ast.literal_eval(assignments['CONTRACT'])
    matrix = ast.literal_eval(assignments['MATRIX'])
    fixture = ast.literal_eval(assignments['FIXED_FIXTURE'])
    catalog = json.loads((R / 'data/phase321-rainbow-king-source-plan/catalog-literal-for-layout-geometry.json').read_text())['catalog']
    slots = []
    for side in fixture['sides']:
        for slot, item in enumerate(side['items']):
            assert item['f'] == 0, 'current fixed A SOURCE has no rotations; do not guess a new rotation policy'
            cells = [[item['x'] + x, item['y'] + y] for x, y in catalog[str(item['item_index'])]['shape']]
            slots.append(dict(item, input_slot=slot, side=side['side'], cells=cells))
    assert len(slots) == 39 and 'O:12' not in {s['instance_id'] for s in slots} and 'O:19' in {s['instance_id'] for s in slots}
    save('fixed-slot-map.json', slots)
    baseline = json.loads((R / 'data/phase307-observer-chance-source/native-source-freeze.json').read_text())
    original, after = {}, {}
    for name, identity in baseline['files'].items():
        location = baseline['source_locations'][name]
        raw = (R / location['after']).read_bytes()
        assert pin_bytes(raw) == dict(size=identity['after_size'], sha256=identity['after_sha256']), name
        after[name] = raw
        if location['before'] is None:
            original[name] = None
        else:
            before = (R / location['before']).read_bytes()
            assert pin_bytes(before) == dict(size=identity['before_size'], sha256=identity['before_sha256']), name
            assert (BASE / name).read_bytes() == before
            original[name] = before
    for name in ('Items/Exclusive/KingGoobert.gd', 'Utility/AutoHideParticles.gd'):
        assert name not in after
        original[name] = (BASE / name).read_bytes()
        after[name] = original[name]
    # Preserve these real inherited source observations, despite the358 roster gap.
    schema_delta = []
    for name in ('prepare', 'onItemActivated', 'doCooldownEffect'):
        site = 'Items/Goobert.gd::' + name
        assert site not in matrix['sites']
        matrix['sites'][site] = dict(channel='runtime', state_schema='goobert', arguments_exact=['event'] if name == 'onItemActivated' else [])
        schema_delta.append(dict(site=site, arguments=matrix['sites'][site]['arguments_exact'], declaration=fn_text(original['Items/Goobert.gd'].decode(), name).split(':\n', 1)[0], reason='INHERITED307_REAL_SOURCE_NOT_IN358103_ROSTER'))
    save('required-schema-delta.json', dict(inherited_sites=schema_delta,
        auxiliary_proof=dict(name='king-slot-bindings.json', schema='phase359-source-slot-bindings/1', accepted_by_358=False),
        admission='BLOCKED_PENDING_SCHEMA_AND_ADAPTER_DELTA_NOT_A_NEW_READY_BOOL'))
    edits = []
    def change(name, label, transform):
        before = after[name]
        modified = transform(before.decode()).encode()
        if modified != before:
            edits.append(dict(path=name, label=label, before=before.decode(), after=modified.decode(),
                              before_identity=pin_bytes(before), after_identity=pin_bytes(modified)))
            after[name] = modified
    for site, spec in matrix['sites'].items():
        name = site.split('::', 1)[0]
        if name not in after:
            raise ValueError('SOURCE file outside declared base closure ' + name)
        change(name, 'callee-bound-site:' + site, lambda source, site=site, spec=spec: hook_function(source, site, spec))
    # New Timer statements only; inherited307 API wrappers stay exact.
    for site in matrix['sites']:
        name, method = site.split('::', 1)
        def timer_wrappers(source, site=site, method=method):
            block = fn_text(source, method)
            lines = block.splitlines(keepends=True)
            out = []
            for i, line in enumerate(lines):
                match = re.fullmatch(r'(\t+)(timer|tickTimer|invulnerabilityTimer|battleRageTimer|autoRageTimer|buffTimer|fatigueStartTimer|fatigueTickTimer)\.(start|stop)\((.*)\)\s*\n?', line)
                if not match or i and 'NativeRandomObserver.timer_before(' in lines[i - 1]:
                    out.append(line)
                    continue
                tabs, receiver, operation, expression = match.groups()
                args = []
                if expression:
                    variable = 'observer359_timer_arg_' + str(i)
                    if variable in block:
                        raise ValueError('Timer temporary collision ' + site)
                    out.append(tabs + 'var ' + variable + ' = ' + expression + '\n')
                    args = [variable]
                rendered = '[' + ', '.join(args) + ']'
                out.extend([tabs + 'NativeRandomObserver.timer_before(' + receiver + ', ' + json.dumps(operation) + ', ' + rendered + ', ' + json.dumps(site) + ')\n',
                            tabs + receiver + '.' + operation + '(' + ', '.join(args) + ')\n',
                            tabs + 'NativeRandomObserver.timer_after(' + receiver + ', ' + json.dumps(operation) + ', ' + rendered + ', ' + json.dumps(site) + ')\n'])
            replacement = ''.join(out)
            assert source.count(block) == 1
            return source.replace(block, replacement, 1)
        change(name, 'new-selected-Timer-API:' + site, timer_wrappers)
    def once(source, old, new):
        if source.count(old) != 1:
            raise ValueError('unique passive SOURCE anchor ' + old[:90])
        return source.replace(old, new, 1)
    change('Core/Character.gd', 'invu-scene-ready-birth', lambda s: once(s,
        '\tNativeRandomObserver.entry("Core/Character.gd::_ready", self, {})',
        '\tNativeRandomObserver.timer_birth(invulnerabilityTimer, self, "Character.scene.ready")\n\tNativeRandomObserver.entry("Core/Character.gd::_ready", self, {})'))
    change('Utility/AutoHideParticles.gd', 'auto-ready-owner-only-and-constructor-birth', lambda s: once(once(s,
        'func _ready() -> void :\n', 'func _ready() -> void :\n\tNativeRandomObserver.ui_ready(self)\n'),
        '\ttimer = Timer.new()\n', '\ttimer = Timer.new()\n\tNativeRandomObserver.timer_birth(timer, self, "AutoHide.Timer.new")\n'))
    change('Core/Character.gd', 'King-pitch-passive-label', lambda s: once(s,
        'Util.randPitch(0.1)', 'Util.randPitch(0.1, "invulnerability_pitch:" + NativeRandomObserver.item_id(item))'))
    change('Utility/Util.gd', 'one-real-pitch-return', lambda s: once(s,
        'func randPitch(variation = 0.05) -> float:\n\treturn rng.randf_range(1 - variation, 1 + variation)',
        'func randPitch(variation = 0.05, observer359_label = "") -> float:\n\tvar observer359_low = 1 - variation\n\tvar observer359_high = 1 + variation\n\tvar observer359_value = rng.randf_range(observer359_low, observer359_high)\n\tNativeRandomObserver.primitive("Utility/Util.gd::randPitch", "randf_range", observer359_label, [observer359_low, observer359_high], observer359_value)\n\treturn observer359_value'))
    def delayed(source):
        block = fn_text(source, 'callDelayed')
        old = '\ttimer.connect("timeout", target, methodName, binds, CONNECT_ONESHOT)'
        return source.replace(block, once(block, old, old + '\n\tNativeRandomObserver.capture_delayed(target, methodName, delay, timer)'), 1)
    change('Utility/Util.gd', 'actual-delayed-activation-fact', delayed)
    # Complete UI authority observers are inherited source transformations.
    ui_methods = ('respondToHover', 'respondToHoverEnd', 'activateDragParticles', 'deactivateDragParticles', 'onAddedToGridStorage', 'deactivateParticles')
    def ui_hook(source, method, site):
        block = fn_text(source, method)
        if 'observer359_ui_' in block:
            raise ValueError('UI token collision ' + site)
        lines = block.splitlines(keepends=True)
        head = next(i for i, l in enumerate(lines) if re.search(r'\)\s*(?:->[^:]+)?\s*:\s*$', l))
        out = lines[:head + 1] + ['\tvar observer359_ui_token = NativeRandomObserver.ui_entry(' + json.dumps(site) + ', self, {})\n']
        for line in lines[head + 1:]:
            if re.fullmatch(r'\t+return\s*\n', line):
                out.append(line[:len(line) - len(line.lstrip())] + 'NativeRandomObserver.ui_leave(observer359_ui_token, ' + json.dumps(site) + ', self)\n')
            elif re.match(r'\t+return\b', line):
                raise ValueError('value return in narrow UI source ' + site)
            out.append(line)
        while out and not out[-1].strip():
            out.pop()
        out.append('\tNativeRandomObserver.ui_leave(observer359_ui_token, ' + json.dumps(site) + ', self)\n\n')
        return source.replace(block, ''.join(out), 1)
    for method in ui_methods:
        change('Items/Item.gd', 'UI-source-entry:' + method, lambda s, m=method: ui_hook(s, m, 'Items/Item.gd::' + m))
    for method in ('activate', 'deactivate', 'startTimer', 'instantClear'):
        change('Utility/AutoHideParticles.gd', 'UI-auto-entry:' + method, lambda s, m=method: ui_hook(s, m, 'Utility/AutoHideParticles.gd::' + m))
    for guard, label in [('\tif dragged:', 'dragged'), ('\tif mode == RigidBody2D.MODE_RIGID and visible:', 'rigid')]:
        def branch(source, guard=guard, label=label):
            block = fn_text(source, '_process')
            lines = block.splitlines(keepends=True)
            a = next(i for i, line in enumerate(lines) if line.rstrip('\r\n') == guard)
            z = a + 1
            while z < len(lines) and (not lines[z].strip() or lines[z].startswith('\t\t')):
                z += 1
            if any(re.match(r'\t+return\b', line) for line in lines[a + 1:z]):
                raise ValueError('UI branch early return')
            token = 'observer359_ui_' + label
            site = 'Items/Item.gd::_process:' + label
            added = lines[:a + 1] + ['\t\tvar ' + token + ' = NativeRandomObserver.ui_entry(' + json.dumps(site) + ', self, {"delta_bits": NativeRandomObserver.float_bits(delta)})\n'] + lines[a + 1:z] + ['\t\tNativeRandomObserver.ui_leave(' + token + ', ' + json.dumps(site) + ', self)\n'] + lines[z:]
            return source.replace(block, ''.join(added), 1)
        change('Items/Item.gd', 'UI-process-branch:' + label, branch)
    # Sink composition: actual methods, not runtime monkeypatching or placeholders.
    sink = (R / 'tests/native_random_observer_sink_v7_154.gd').read_text()
    replacements = {'CAPS': contract['caps'], 'STATE_SCHEMAS': contract['state_schemas'],
                    'SITES': {site: {key: spec[key] for key in ('channel', 'state_schema')} for site, spec in matrix['sites'].items()}}
    for key, value in replacements.items():
        pattern = r'^const ' + key + r' = .*\n'
        sink, count = re.subn(pattern, 'const ' + key + ' = ' + json.dumps(value, sort_keys=True) + '\n', sink, count=1, flags=re.M)
        assert count == 1
    sink = sink.replace('"phase137-ui-authority/1"', '"phase355-king-ui-authority/1"').replace('"NATIVE-V7-008-KING-UI-GUARDED-127"', '"KING-K1-A-353"').replace('"7-king-rng-initial-148-family63"', '"7-king-single-A-355"').replace('"phase148-util-rng-checkpoint/1"', '"phase355-util-rng-checkpoint/1"').replace('"phase111-king-input-facts/1"', '"phase355-king-input-facts/1"')
    sink = sink.replace('const OUT = "user://native-capture"\n', 'const OUT = "user://native-capture"\nconst SOURCE_SLOT_TABLE = ' + json.dumps(slots, sort_keys=True) + '\n')
    extension = (R / 'tests/phase359_sink_extension_source.gd').read_text()
    prefix = extension[:extension.index('func ')]
    sink = sink.replace('func begin_encoding():', prefix + '\nfunc begin_encoding():', 1)
    for method in functions(extension)[1]:
        replacement = fn_text(extension, method)
        if method in functions(sink)[1]:
            sink = sink.replace(fn_text(sink, method), replacement + '\n', 1)
        else:
            sink += '\n' + replacement
    # Preserve the exact307 auxiliary observer API referenced by inherited GD.
    # The thin K1 domain does not call this method, but its callers must parse.
    helper307 = (R / baseline['source_locations']['native_random_observer_sink_v7.gd']['after']).read_text()
    if 'shortbow_debuff_label' not in functions(sink)[1]:
        sink += '\n' + fn_text(helper307, 'shortbow_debuff_label')
    # New proof panels do not mutate the original checkpoint fields/order.
    checkpoint = fn_text(sink, 'checkpoint')
    checkpoint = once(checkpoint, '"nodes": nodes, "items": rows}', '"nodes": nodes, "items": rows, "source_resources": source_resources(game)}')
    sink = sink.replace(fn_text(sink, 'checkpoint'), checkpoint, 1)
    after['native_random_observer_sink_v7.gd'] = sink.encode()
    # Exactly reverse every declared new edit; then require the unchanged307 transition.
    inverse = deepcopy(after)
    for edit in reversed(edits):
        assert inverse[edit['path']] == edit['after'].encode(), edit['label']
        inverse[edit['path']] = edit['before'].encode()
    for name, identity in baseline['files'].items():
        if name == 'native_random_observer_sink_v7.gd':
            continue
        assert pin_bytes(inverse[name]) == dict(size=identity['after_size'], sha256=identity['after_sha256'])
    generated = D / 'after-source'
    paths = {}
    diff = []
    for name in sorted(after):
        p = generated / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(after[name])
        before = original[name]
        paths[name] = dict(before=None if before is None else pin_bytes(before), after=pin_bytes(after[name]))
        diff.extend(difflib.unified_diff((before or b'').decode().splitlines(True), after[name].decode().splitlines(True), fromfile='original/' + name if before is not None else '/dev/null', tofile='source359/' + name))
    (D / 'native-source.patch').write_text(''.join(diff))
    save('new-edits-inverse-ledger.json', dict(edits=edits, reverse_to307_after='PASS', original307_before_transition='EXACT_FROZEN_IDENTITY', sink='separately generated observer-only new source', no_business_execution=True))
    save('producer-patch-report.json', dict(schema='phase359-observer-source-patch/1', version='7-king-single-A-source359', paths=paths,
        patch=pin(D / 'native-source.patch'), generator=pin(Path(__file__)), path_count=len(paths),
        declared_sites=len(matrix['sites']), new_schema_delta_sites=len(schema_delta),
        independent_accepted=False, native_authorized=False, runtime_PATCHES_updated=False,
        flags='SOURCE_ONLY_NO_GODOT_PARSE_OR_RUN'))
    compile(Path(__file__).read_bytes(), str(Path(__file__)), 'exec')
    print(json.dumps(dict(status='ACTUAL_SOURCE_TEXT_GENERATED_NO_EXECUTION', paths=len(paths), sites=len(matrix['sites']), patch=pin(D / 'native-source.patch'))))


if __name__ == '__main__':
    main()
