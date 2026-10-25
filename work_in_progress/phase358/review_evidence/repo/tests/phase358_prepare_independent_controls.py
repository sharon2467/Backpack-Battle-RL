"""Static SOURCE review and synthetic fixture preseal; no schema import/call."""
import ast
import copy
import hashlib
import json
from pathlib import Path

R = Path(__file__).resolve().parents[1]
D = R / 'data/phase358-independent-schema-review'
A = R / 'data/phase358-king-schema-source-repair'
OLD = R / 'data/phase357-independent-schema-review'


def pin(p):
    b = p.read_bytes()
    return dict(size=len(b), sha256=hashlib.sha256(b).hexdigest())


def desc(p):
    return dict(path=str(p.relative_to(R)), **pin(p))


def write(name, obj):
    with (D / name).open('x') as f:
        json.dump(obj, f, indent=2, sort_keys=True)
        f.write('\n')


def main():
    D.mkdir(exist_ok=False)
    s = D / 'SOURCE'
    s.mkdir()
    assert pin(A / 'source-owner.json') == dict(size=2511, sha256='8107db40a93ad0326e6bcfb19237b69085527e7d8521e049630f445d5cd01364')
    owner = json.loads((A / 'source-owner.json').read_text())
    for row in owner['files']:
        assert pin(R / row['path']) == {k: row[k] for k in ('size', 'sha256')}
    originals = {
        'schema.py': R / 'tests/phase358_king_observer_schema.py',
        'mapper.py': R / 'tests/phase358_prepare_schema_source.py',
        'old357-schema.py': OLD / 'SOURCE/phase357_king_observer_schema.py',
        'schema-contract.json': OLD / 'SOURCE/schema-contract.json',
        'old8-fixtures.json': OLD / 'synthetic-probe-fixtures.json',
        'old4-fixtures.json': OLD / 'object-argument-fixtures.json',
        'old8-contract.json': OLD / 'probe-contract.json',
        'old4-contract.json': OLD / 'object-argument-contract.json',
        'source-signature-completeness.json': A / 'source-signature-completeness.json',
    }
    for name, p in originals.items():
        with (s / name).open('xb') as f:
            f.write(p.read_bytes())
    old = (s / 'old357-schema.py').read_text()
    new = (s / 'schema.py').read_text()
    ot, nt = ast.parse(old), ast.parse(new)
    get_matrix = lambda t: next(n for n in t.body if isinstance(n, ast.Assign) and any(isinstance(x, ast.Name) and x.id == 'MATRIX' for x in n.targets))
    om, nm = get_matrix(ot), get_matrix(nt)
    before, after = ast.literal_eval(om.value), ast.literal_eval(nm.value)
    pairs = [('Utility/EventBus.gd::connectEvent', 'emitter'), ('Utility/EventBus.gd::connectEvent', 'receiver'), ('Utility/EventBus.gd::emitAndLog', 'emitter'), ('Utility/Util.gd::changeTimer', 'timer')]
    inverse_matrix = copy.deepcopy(after)
    for site, key in pairs:
        assert key not in before['sites'][site]['argument_types']
        assert inverse_matrix['sites'][site]['argument_types'].pop(key) == 'native_ref|null'
    assert inverse_matrix == before
    inverse = new.replace(ast.get_source_segment(new, nm), ast.get_source_segment(old, om), 1)
    gate = "    if kind in ('item', 'goobert', 'king', 'potion', 'plain_item'):\n"
    assert inverse.count(gate) == 1
    inverse = inverse.replace(gate, "    if kind in ('item', 'goobert', 'king', 'potion'):\n", 1)
    term = " or kind == 'plain_item' and actual != 'plain_item'"
    assert inverse.count(term) == 1
    inverse = inverse.replace(term, '', 1)
    assert ast.dump(ast.parse(inverse), include_attributes=False) == ast.dump(ot, include_attributes=False)
    allowed = {'hashlib', 'json', 'math', 're', 'struct', 'copy', 'dataclasses', 'types'}
    for n in nt.body:
        if isinstance(n, ast.Import):
            assert {x.name.split('.')[0] for x in n.names} <= allowed
        elif isinstance(n, ast.ImportFrom):
            assert n.module.split('.')[0] in allowed
    mapper = ast.parse((s / 'mapper.py').read_text())
    args_fn = next(n for n in mapper.body if isinstance(n, ast.FunctionDef) and n.name == 'arguments')
    assert any(isinstance(n, ast.Raise) for n in ast.walk(args_fn))
    assert not any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in ('open', 'save', 'main', 'pin') for n in ast.walk(args_fn))
    freeze = R / 'data/phase356-king-admission-source-repair/candidate-source-freeze.json'
    frozen = json.loads(freeze.read_text())
    assert pin(freeze) == dict(size=2783, sha256='a135fc774658dab7f9b16d9e9955252f700c030fb0fb661d7db0c06ec3424afb')
    for rel, identity in frozen['files'].items():
        assert pin(freeze.parent / 'staged' / rel) == identity
    for p in (s / 'schema.py', s / 'mapper.py'):
        compile(p.read_bytes(), str(p), 'exec')
    write('static-review.json', dict(schema='phase358-independent-static-repair/1', status='PASS',
        author_leaves=len(owner['files']), author_bytes=sum(x['size'] for x in owner['files']),
        complete_module_inverse_AST_equal357=True, exact_changed_argument_leaves=pairs,
        old43clones_and103declarations_reused_by_whole_AST_conservation=True,
        actual356_runtime15_identities_unchanged=True, guard356_closed=True,
        mapper_pure_function_no_file_calls=True, schema_imports=0, models=0, native=0))

    c = json.loads((s / 'schema-contract.json').read_text())
    I = lambda n: dict(type='int', decimal=str(n))
    F = lambda bits='0000000000000000': dict(type='float', binary64_be=bits)
    B = lambda v=False: dict(type='bool', value=v)
    N = lambda: dict(type='null')
    ref = lambda n='9001', role='P:12', cls='Item': dict(type='native_ref', native_id=n, role=role, **{'class': cls})
    def cache():
        return dict(type='dictionary', entries=[dict(key=I(color), value=dict(type='dictionary', entries=[])) for color in (0, 2, 4, 7)])
    def state(kind):
        result = {}
        for key, typ in c['state_schemas'][kind].items():
            if typ == 'auto_hide':
                value = state('auto_hide')
            elif typ in ('timer', 'timer|null', 'node'):
                value = state('node' if typ == 'node' else 'timer')
            elif typ == 'id':
                value = '9200'
            elif kind == 'node':
                value = {'class': 'Timer', 'inside_tree': True, 'name': 'Timer', 'native_id': '9200', 'path': '/root/SYNTHETIC_SCHEMA_ONLY/Timer', 'positions': [-1, 0, 0], 'priority': 0, 'role': 'king_buff:P:12'}.get(key, False)
            elif kind == 'timer' and typ in ('bool', 'int'):
                value = True if key in ('one_shot', 'stopped') else 0 if typ == 'int' else False
            elif typ == 'int':
                value = I(262 if key == 'descriptorIndex' and kind == 'king' else 1 if key == 'descriptorIndex' else 0)
            elif typ == 'float':
                value = F('3ff0000000000000' if key in ('wait_time', 'speed_scale', 'speedScale') else '0000000000000000')
            elif typ == 'bool':
                value = B()
            elif typ in ('array', 'temporary_array'):
                value = dict(type='array', values=[])
            elif typ == 'dictionary':
                value = cache() if key == 'currentAffectedItems' else dict(type='dictionary', entries=[])
            elif '|null' in typ:
                value = N()
            elif typ == 'string':
                value = dict(type='string', value='SYNTHETIC_SCHEMA_ONLY')
            else:
                raise AssertionError((kind, key, typ))
            result[key] = value
        if kind == 'king':
            result.update(activationsToTrigger=F('4018000000000000'), protectedBuffs=F('4008000000000000'), manaCost=F('4010000000000000'))
        if kind == 'auto_hide':
            result['lifetime'] = F('3fe6666660000000')
        return result
    def arguments(rows):
        return dict(type='dictionary', entries=[dict(key=dict(type='string', value=k), value=v) for k, v in rows])
    def record(site, role, fields, values, channel='runtime', native='9100'):
        return dict(schema='observer7-record/1', sequence=0, channel=channel, site=site, edge='enter',
                    subject=ref(native, role, 'Node2D'), stamp=dict(physics_frame='0', idle_frame='0', util_time=F(), combat_time=N(), phase='SYNTHETIC_SCHEMA_ONLY'), payload=dict(arguments=arguments(values), state=fields))
    cases = []
    def add(label, operation, data=None, expected='accept', **options):
        cases.append(dict(id=len(cases) + 1, label=label, operation=operation, data=data, expected=expected, **options))
    old8 = json.loads((s / 'old8-fixtures.json').read_text())
    old4 = json.loads((s / 'old4-fixtures.json').read_text())
    for item in json.loads((s / 'old8-contract.json').read_text())['controls']:
        add(item['label'], item['operation'].upper(), old8.get(item.get('fixture')), item['expected'], **({'kind': item['kind']} if 'kind' in item else {}))
    for item in json.loads((s / 'old4-contract.json').read_text())['controls']:
        add(item['label'], 'RECORD', old4[item['fixture']], item['expected'])
    assert len(cases) == 12
    bus = state('event_bus')
    connect = record('Utility/EventBus.gd::connectEvent', 'event_bus', bus, [('emitter', ref('9300', 'P', 'Character')), ('signalName', dict(type='string', value='SYNTHETIC_SCHEMA_ONLY')), ('receiver', ref()), ('method', dict(type='string', value='onSchemaOnly'))])
    add('connectEvent-two-Node-ref-positive', 'RECORD', connect)
    for key in ('emitter', 'receiver'):
        bad = copy.deepcopy(connect)
        next(x for x in bad['payload']['arguments']['entries'] if x['key']['value'] == key)['value'] = I(0)
        add('connectEvent-' + key + '-INT-rejected', 'RECORD', bad, 'reject')
    nullable = copy.deepcopy(connect)
    for x in nullable['payload']['arguments']['entries']:
        if x['key']['value'] in ('emitter', 'receiver'):
            x['value'] = N()
    add('Node-nullable-entry', 'RECORD', nullable)
    nullable = copy.deepcopy(old4['util_Timer_ref'])
    nullable['payload']['arguments']['entries'][0]['value'] = N()
    add('Timer-nullable-entry', 'RECORD', nullable)
    bag = copy.deepcopy(old8['plain_one']); bag['descriptorIndex'] = I(11)
    add('Bag11-plain-positive', 'STATE', bag, kind='plain_item')
    for label, value in [('BOOL', B()), ('REAL', F('3ff0000000000000'))]:
        bad = copy.deepcopy(bag); bad['descriptorIndex'] = value
        add('descriptor-' + label + '-rejected', 'STATE', bad, 'reject', kind='plain_item')
    add('mapper-Node-Timer-declarations', 'MAPPER', 'func synthetic(n: Node, t: Timer):', returns=dict(names=['n', 't'], types={'n': 'native_ref|null', 't': 'native_ref|null'}))
    add('mapper-unknown-explicit-annotation', 'MAPPER', 'func synthetic(x: UnrecognizedExplicitType):', 'reject')
    add('typed-BOOL-positive', 'TYPED', B())
    add('typed-INT64max-positive', 'TYPED', I((1 << 63) - 1))
    add('typed-REAL-negativezero-positive', 'TYPED', F('8000000000000000'))
    add('typed-INT-BOOL-decimal-rejected', 'TYPED', dict(type='int', decimal=False), 'reject')
    add('typed-BOOL-numeric-value-rejected', 'TYPED', dict(type='bool', value=0), 'reject')
    add('typed-INT-noncanonical-rejected', 'TYPED', dict(type='int', decimal='01'), 'reject')
    add('typed-INT64overflow-rejected', 'TYPED', I(1 << 63), 'reject')
    add('REAL-width-rejected', 'TYPED', F('000000000000000'), 'reject')
    add('REAL-uppercase-rejected', 'TYPED', F('3FF0000000000000'), 'reject')
    add('REAL-NaN-rejected', 'TYPED', F('7ff8000000000000'), 'reject')
    add('native-id-zero-rejected', 'TYPED', ref('0'), 'reject')
    add('unknown-typed-kind-rejected', 'TYPED', dict(type='unknown'), 'reject')
    add('typed-extra-field-rejected', 'TYPED', dict(type='null', extra=0), 'reject')
    repeated = dict(key=I(0), value=N())
    add('duplicate-typed-dictionary-key-rejected', 'TYPED', dict(type='dictionary', entries=[repeated, copy.deepcopy(repeated)]), 'reject')
    deep = N()
    for _ in range(18): deep = dict(type='array', values=[deep])
    add('typed-depth-cap-rejected', 'TYPED', deep, 'reject')
    add('typed-array-cap-rejected', 'TYPED', dict(type='array', values=[N() for _ in range(8193)]), 'reject')
    add('typed-string-cap-rejected', 'TYPED', dict(type='string', value='x' * 4097), 'reject')
    add('typed-dictionary-cap-rejected', 'TYPED', dict(type='dictionary', entries=[dict(key=I(i), value=N()) for i in range(513)]), 'reject')
    king, character = state('king'), state('character')
    add('King-complete-private-state', 'STATE', king, kind='king')
    for key, value in [('protectedBuffs', I(3)), ('invuCharges', B())]:
        bad = copy.deepcopy(king); bad[key] = value
        add('King-' + key + '-wrong-raw-type', 'STATE', bad, 'reject', kind='king')
    add('Character-protection-INT-and-null-origin', 'STATE', character, kind='character')
    for key, value in [('buffProtectStacks', F()), ('invulnerabilityItem', I(0))]:
        bad = copy.deepcopy(character); bad[key] = value
        add('Character-' + key + '-wrong-type', 'STATE', bad, 'reject', kind='character')
    mana = record('Core/Character.gd::useMana', 'P', character, [('amount', I(4)), ('item', ref()), ('triggerEvent', N())])
    add('Character-useMana-INT-entry', 'RECORD', mana)
    bad = copy.deepcopy(mana); bad['payload']['arguments']['entries'][0]['value'] = F('4010000000000000')
    add('Character-useMana-REAL-entry-rejected', 'RECORD', bad, 'reject')
    mana = record('Items/Item.gd::useMana', 'P:12', king, [('amount', F('4010000000000000')), ('triggerEvent', N())])
    add('King-Item-useMana-REAL-callsite', 'RECORD', mana)
    bad = copy.deepcopy(mana); bad['payload']['arguments']['entries'][0]['value'] = I(4)
    add('King-Item-useMana-INT-callsite-rejected', 'RECORD', bad, 'reject')
    timer = state('timer')
    bad = copy.deepcopy(timer); bad['process_mode'] = False
    add('Timer-mode-BOOL-rejected', 'STATE', bad, 'reject', kind='timer')
    add('cache-four-actual-colors', 'CACHE', cache())
    bad = cache(); bad['entries'][0]['key'] = B()
    add('cache-BOOL-primary-rejected', 'CACHE', bad, 'reject')
    bad = cache(); bad['entries'].pop()
    add('cache-missing-color-rejected', 'CACHE', bad, 'reject')
    bad = cache(); pair = dict(key=ref('9400', 'P:13'), value=B(True)); bad['entries'][0]['value']['entries'] = [pair, copy.deepcopy(pair)]
    add('cache-duplicate-native-ref-rejected', 'CACHE', bad, 'reject')
    ready = record('Items/Item.gd::_ready', 'O:19', dict(native_id='9100'), [], channel='lineage')
    add('generic-ready-owner-only', 'RECORD', ready)
    bad = copy.deepcopy(ready); bad['payload']['state']['timer'] = timer
    add('fake-full-ready-rejected', 'RECORD', bad, 'reject')
    bad = copy.deepcopy(ready); bad['site'] = 'Unknown::method'
    add('unknown-record-site-rejected', 'RECORD', bad, 'reject')
    bad = copy.deepcopy(ready); bad['extra'] = 0
    add('extra-record-envelope-field-rejected', 'RECORD', bad, 'reject')
    bad = copy.deepcopy(ready); bad['edge'] = 'unknown_edge'
    add('unknown-record-edge-rejected', 'RECORD', bad, 'reject')
    bad = copy.deepcopy(ready); bad['payload']['state']['native_id'] = '9999'
    add('generic-ready-owner-mismatch-rejected', 'RECORD', bad, 'reject')
    context = dict.fromkeys(c['primitive_context_exact']); context['item'] = 'P:12'
    pitch = dict(kind='randf_range', label='invulnerability_pitch:P:12', args=[F('3feccccccccccccd'), F('3ff199999999999a')], value=F('3ff0000000000000'), context=context)
    add('King-pitch-typed-return-only', 'PRIMITIVE', pitch)
    bad = copy.deepcopy(pitch); bad['args'][0] = I(0)
    add('King-pitch-endpoint-type-rejected', 'PRIMITIVE', bad, 'reject')
    delta = '3f91111120000000'
    clock = dict(schema='phase105-exogenous-frame-clock/1', lineage='fresh_activate_idle_tail', environment=dict(physics_fps=60, scale_bits='3ff0000000000000', paused=False), checkpoint=dict(phase='activate_items_idle_tail', physics_frame=0, idle_frame=0, util_frame_counter=0, util_time_bits='0000000000000000', util_clock_time_bits='0000000000000000'), passes=[dict(kind='physics', delta_bits=delta, physics_frame=1, idle_frame=1), dict(kind='idle', delta_bits=delta, physics_frame=1, idle_frame=1), dict(kind='physics', delta_bits=delta, physics_frame=2, idle_frame=2), dict(kind='idle', delta_bits=delta, physics_frame=2, idle_frame=2)])
    add('clock-typed-schedule-only', 'CLOCK', clock)
    bad = copy.deepcopy(clock); bad['extra'] = 0
    add('clock-header-extra-rejected', 'CLOCK', bad, 'reject')
    bad = copy.deepcopy(clock); bad['environment']['physics_fps'] = True
    add('clock-BOOL-fps-rejected', 'CLOCK', bad, 'reject')
    bad = copy.deepcopy(clock); bad['passes'][0], bad['passes'][1] = bad['passes'][1], bad['passes'][0]
    add('clock-row-reversal-rejected', 'CLOCK', bad, 'reject')
    endpoint = dict(schema='phase111-fixed-endpoint/1', phase='idle_pre_internal_flush', physics_frame=2, idle_frame=2, passes=4, two_future_physics_signals=2, fx_exact_comparison='NOT_EVALUATED_REQUIRES_MODEL')
    cleanup = dict(physics_frame=0, idle_frame=0, is_in_physics_frame=False)
    add('expected-shape-two-future-cut', 'TERMINAL', dict(clock=clock, endpoint=endpoint, cleanup=cleanup))
    trailing = copy.deepcopy(clock); trailing['passes'].append(dict(kind='idle', delta_bits=delta, physics_frame=2, idle_frame=3)); ep = dict(endpoint, idle_frame=3, passes=5)
    add('expected-shape-trailing-idle-rejected', 'TERMINAL', dict(clock=trailing, endpoint=ep, cleanup=cleanup), 'reject')
    before = record('Items/Exclusive/KingGoobert.gd::doCooldownEffect', 'king_buff:P:12', {}, [], native='9200')
    before.update(sequence=10, edge='timer_before')
    before['subject']['class'] = 'Timer'
    before['payload'] = dict(role='king_buff:P:12', operation='start', argc=1, args=[F('3ff8000000000000')], public_before=timer, public_after=None)
    after = copy.deepcopy(before); after.update(sequence=11, edge='timer_after'); after_timer = copy.deepcopy(timer); after_timer.update(stopped=False, wait_time=F('3ff8000000000000'), time_left=F('3ff8000000000000')); after_timer['node']['internal_physics'] = True; after['payload'].update(public_before=None, public_after=after_timer)
    identity = dict(native_to_role={'9200': 'king_buff:P:12'}, role_to_native={'king_buff:P:12': '9200'})
    add('expected-shape-Timer-pair', 'OBSERVATIONS', dict(records=[before, after], identity=identity))
    add('expected-shape-Timer-EOF-rejected', 'OBSERVATIONS', dict(records=[before], identity=identity), 'reject')
    add('expected-shape-unknown-Timer-owner-rejected', 'OBSERVATIONS', dict(records=[before, after], identity=dict(native_to_role={}, role_to_native={})), 'reject')
    sites = ['Items/Item.gd::' + x for x in ('respondToHover', 'respondToHoverEnd', '_process:dragged', '_process:rigid', 'activateDragParticles', 'deactivateDragParticles', 'onAddedToGridStorage', 'deactivateParticles')] + ['Utility/AutoHideParticles.gd::' + x for x in ('activate', 'deactivate', 'startTimer', 'instantClear')]
    control = dict(root_id='1000', disable_input=True, physics_object_picking=False, ordinary_physics=False, ordinary_idle=False, internal_physics=True, internal_idle=True)
    ui = []
    def u(kind, site, payload):
        ui.append(dict(schema='phase355-king-ui-authority/1', sequence=len(ui), kind=kind, site=site, physics_frame=0, idle_frame=0, in_physics=False, payload=payload))
    u('open', 'sink._ready', dict(case='KING-K1-A-353', sites=sites, before=dict(control, disable_input=False, physics_object_picking=True), after=control, drop_mouse_setting=False, window='before_selected_birth_to_final_preinternal', limits=dict(bytes=8388608, rows=65536, record=16384)))
    u('bind', 'scene_instance', dict(item_id='1200', activation_id='1201', drag_id='1202', script='res://Items/Exclusive/KingGoobert.gd', scene='res://Items/Exclusive/KingGoobert.tscn', pooled=False, inside_tree=False, generation=1))
    for native in ('1201', '1202', '5000'):
        ancestry = ([dict(native_id='1200', king_source=True)] if native != '5000' else []) + [dict(native_id='1000', king_source=False)]
        u('ready', 'Utility/AutoHideParticles.gd::_ready', dict(receiver_id=native, ancestry=ancestry, script='res://Utility/AutoHideParticles.gd', viewport_id='1000'))
    fixture = json.loads((R / 'data/phase355-king-finite-source/fixed-A-v8-fixture.json').read_text())
    roles = [i['instance_id'] for side in fixture['sides'] for i in side['items']]
    guards = [dict(item_id='1200' if role == 'P:12' else str(2000 + j), role=role, focus=False, hovered=False, dragged=False, mode=1, viewport_id='1000') for j, role in enumerate(roles)]
    u('roles', 'configure', dict(kings=[dict(item_id='1200', role='P:12')], selected_guards=guards, using_controller=False))
    token = len(ui)
    u('entry', 'Utility/AutoHideParticles.gd::activate', dict(token=token, receiver_id='5000', king_source=False, arguments={}, classification='supported_nonking_auto', source_phase='SYNTHETIC_SCHEMA_ONLY'))
    u('exit', 'Utility/AutoHideParticles.gd::activate', dict(token=token, receiver_id='5000'))
    u('close', 'finish_capture', dict(phase='idle_pre_internal_flush', completed=True, failed=False, overflow=False, dropped=0, entries=1, unsupported=0, rows_before_close=len(ui), sites=sites, controls=control, king_clock_closed=True, active_buff_calls=0))
    add('UI-independent-sequence-foreign-source-shape', 'UI', ui)
    bad = copy.deepcopy(ui); bad[1]['sequence'] = 0
    add('UI-self-sequence-reversal-rejected', 'UI', bad, 'reject')
    add('UI-missing-close-rejected', 'UI', copy.deepcopy(ui[:-1]), 'reject')
    game = record('Core/Game.gd::prepareItems', 'game', state('game'), [('items', dict(type='array', values=[]))], channel='input')
    lineage = copy.deepcopy(ready); lineage['sequence'] = 1
    metadata = dict(schema='observer7-record/1', sequence=2, channel='metadata', site='Sheets/ItemBook.gd::detectMentionedStacks', edge='loaded_descriptors', subject=N(), stamp=copy.deepcopy(game['stamp']), payload={})
    descriptors = []
    for index in (1, 4, 11, 19, 22, 262):
        fields = dict(itemIndex=I(index), identifier=dict(type='string', value='SYNTHETIC_SCHEMA_ONLY'), types=dict(type='array', values=[]), tags=I(0), gainedStacks=I(0), removedStacks=I(0), usedStacks=I(0), hasBattleRageEffect=B(), descriptionKey=dict(type='string', value='SYNTHETIC_SCHEMA_ONLY'), scene_path=dict(type='string', value='res://SYNTHETIC_SCHEMA_ONLY'))
        descriptors.append(arguments(list(fields.items())))
    metadata['payload'] = dict(descriptors=dict(type='array', values=descriptors), locale='SYNTHETIC_SCHEMA_ONLY')
    primitive = dict(schema='observer7-record/1', sequence=3, channel='primitive', site='Utility/Util.gd::randPitch', edge='return_native_primitive', subject=N(), stamp=copy.deepcopy(game['stamp']), payload=pitch)
    def line(row): return json.dumps(row, separators=(',', ':')) + '\n'
    raw = {'fixture.json': '{}', 'player_fixture.json': '{}', 'observer7-input.jsonl': line(game), 'observer7-lineage.jsonl': line(lineage), 'observer7-metadata.jsonl': line(metadata), 'observer7-primitives.jsonl': line(primitive), 'king-clock-checkpoint.json': json.dumps({k: v for k, v in clock.items() if k != 'passes'}), 'king-clock-passes.jsonl': ''.join(line(x) for x in clock['passes']), 'king-input-facts.json': '{}', 'king-ui-authority.jsonl': ''.join(line(x) for x in ui), 'king-rng-checkpoint.json': '{}'}
    add('eleven-synthetic-transport-four-typed-rows-NOT-sourceproof', 'STREAM', raw)
    bad = copy.deepcopy(raw); bad['observer7-input.jsonl'] = bad['observer7-lineage.jsonl']
    add('four-stream-filename-channel-rejected', 'STREAM', bad, 'reject')
    bad = copy.deepcopy(raw); row = json.loads(bad['observer7-lineage.jsonl']); row['sequence'] = 0; bad['observer7-lineage.jsonl'] = line(row)
    add('four-stream-global-duplicate-rejected', 'STREAM', bad, 'reject')
    bad = copy.deepcopy(raw); bad['events.jsonl'] = '{}\n'
    add('expected-file-outside-eleven-rejected', 'STREAM', bad, 'reject')
    panels, nodes = [], []
    for side, native in (('P', '9501'), ('O', '9502')):
        ledgers = []
        for category in range(100, 111):
            ledger = state('buff')
            ledger.update(type=I(category), character=ref(native, side, 'Character'))
            if side == 'P' and category == 105:
                ledger['current'] = I(1)  # intentionally inconsistent synthetic Mana prefix
            ledgers.append(dict(stack=I(category), state=ledger))
        panels.append(dict(side=side, native_id=native, buffProtectStacks=I(0), debuffReflectStacks=I(0), buffs=ledgers))
        nodes.append(dict(role='character:' + side, node=dict(native_id=native)))
    add('source-Mana-ledger-current-without-permanent-rejected', 'RESOURCES', dict(panels=panels, nodes=nodes), 'reject')
    assert len(cases) == 80 and len({x['label'] for x in cases}) == 80, len(cases)
    write('cases.json', cases)
    write('scope.json', dict(schema='phase358-independent-case-scope/1', unique_cases=80, necessary_version_regressions=12, new_unique_cases=68,
        synthetic_only=True, fixtures_not_actual_inputs=True, eleven_positive='Transport/type layer only;empty fresh/RNG/fixture proof objects intentionally NOT complete SOURCE/carriers/bundle.',
        expected_shape_tests='Only synthetic endpoint/Timer records,no expected file reads.', schema_clock_containers='ClockSchedule/FramePass data only,never RuntimeDTO/Engine',
        reused_SOURCE='43clones/103GDdeclarations and old356transport/guard only by exact identities;no old batch rerun', remaining='Actual producer/patch/collector,11carriers,sourcecachegeometry+orderedbusinessproof,bundleprojection/poison,host remain future;356closed.'))
    files = [R / 'docs/phase358_independent_schema_repair_validation_spec.md', Path(__file__).resolve(), R / 'tests/phase358_independent_schema_controls.py', D / 'static-review.json', D / 'cases.json', D / 'scope.json', *sorted(s.iterdir())]
    for p in files:
        if p.suffix == '.py': compile(p.read_bytes(), str(p), 'exec')
    write('source-contract.json', dict(schema='phase358-independent-preexecution-contract/1', files=[desc(p) for p in files], unique_cases=80, regressions=12, new_cases=68, actual_module_imports=0, trusted_bootstrap='stdlib+manifested metadata read/pin beforehook;actual two SOURCE module imports only afterhook'))
    files.append(D / 'source-contract.json')
    write('source-owner.json', dict(schema='phase358-independent-preexecution-owner/1', files=[desc(p) for p in files]))
    for row in json.loads((D / 'source-owner.json').read_text())['files']:
        assert desc(R / row['path']) == row
    print(json.dumps(dict(owner=desc(D / 'source-owner.json'), cases=80)))


if __name__ == '__main__':
    main()
