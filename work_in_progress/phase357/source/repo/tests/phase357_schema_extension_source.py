# SOURCE template appended by phase357_prepare_schema_source.py; no imports/calls.

FIXED_ROLES = SINGLE_KING_ROLES
ITEM_INDEX_BY_ROLE = None  # replaced by SOURCE generator with the frozen A map
TIMER_ROLES = frozenset(
    ['tick:P', 'tick:O', 'fatigue:start', 'fatigue:tick', 'invu:P', 'invu:O',
     'king_buff:P:12', 'king_hide:P:12', 'king_drag:P:12']
    + ['buff:' + side + ':' + str(category) for side in ('P', 'O') for category in range(100, 111)]
    + ['aux:' + side + ':' + name for side in ('P', 'O') for name in ('battleRageTimer', 'autoRageTimer')]
)
KNOWN_REF_ROLES = FIXED_ROLES | TIMER_ROLES | {
    'P', 'O', 'root_viewport', 'game', 'util', 'combat_timer', 'combat_log', 'event_bus',
}

_base_validate_typed = validate_typed


def validate_typed(value, depth=0):
    _base_validate_typed(value, depth)
    if value['type'] == 'native_ref' and value['role'] is not None and value['role'] not in KNOWN_REF_ROLES:
        raise ValueError('unknown fixed A native reference role')
    return value


def validate_cache(value, current=False):
    validate_typed(value)
    if value['type'] != 'dictionary':
        raise ValueError('typed cache dictionary')
    if not value['entries'] and not current:
        return value  # genuine pre-prepare cache is not yet the four prepared arrays
    colors = set()
    for entry in value['entries']:
        key, content = entry['key'], entry['value']
        if key['type'] != 'int':
            raise ValueError('cache color must be actual INT, never BOOL/REAL alias')
        color = decimal(key['decimal'])
        if color not in (0, 2, 4, 7) or color in colors:
            raise ValueError('cache exact distinct SOURCE color')
        colors.add(color)
        if content['type'] != ('dictionary' if current else 'array'):
            raise ValueError('current ordered refs/bools versus prepared array cache')
        refs = content['entries'] if current else content['values']
        seen = set()
        for row in refs:
            ref = row['key'] if current else row
            if current and row['value'] != {'type': 'bool', 'value': True}:
                raise ValueError('current affected SOURCE BOOLtrue membership')
            if ref['type'] != 'native_ref' or ref['role'] not in FIXED_ROLES or ref['native_id'] in seen:
                raise ValueError('known unique ordered affected native refs')
            seen.add(ref['native_id'])
    if colors != {0, 2, 4, 7}:
        raise ValueError('missing SOURCE affected color')
    return value


def validate_state(value, kind, constructor=False):
    if kind not in CONTRACT['state_schemas']:
        raise ValueError('unknown K1 state schema')
    if kind in ('item', 'goobert', 'king', 'potion'):
        if type(value) is not dict or 'descriptorIndex' not in value:
            raise ValueError('item descriptor raw identity required')
        validate_typed(value['descriptorIndex'])
        if value['descriptorIndex']['type'] != 'int':
            raise ValueError('item descriptor INT')
        index = decimal(value['descriptorIndex']['decimal'])
        if index not in DESCRIPTOR_IDS:
            raise ValueError('item descriptor outside fixed six IDs')
        actual = 'king' if index == 262 else 'potion' if index == 19 else 'plain_item'
        if kind == 'king' and actual != 'king' or kind == 'potion' and actual != 'potion' or kind == 'goobert' and actual != 'king':
            raise ValueError('closed source Item subtype')
        kind = actual
    # Reuse the old field loop, bypass its ambiguous legacy item-shape dispatcher.
    fields = CONTRACT['state_schemas'][kind]
    exact(value, fields)
    for key, expected in fields.items():
        field = value[key]
        if expected == 'auto_hide':
            validate_state(field, 'auto_hide', constructor)
        elif expected in ('timer', 'timer|null', 'node'):
            if field is None and (expected.endswith('|null') or constructor):
                continue
            validate_state(field, 'node' if expected == 'node' else 'timer', constructor)
        elif expected == 'id':
            decimal(field, True)
        elif kind == 'node' and key in ('role', 'path'):
            if field is not None:
                text(field)
            if key == 'role' and field is not None and field not in KNOWN_REF_ROLES:
                raise ValueError('unknown actual node role')
        elif kind == 'node' and key in ('name', 'class'):
            text(field)
        elif expected == 'int_array':
            if type(field) is not list or len(field) > CAPS['depth']:
                raise ValueError('ancestor path cap/type')
            for position in field:
                integer(position, -1, (1 << 31) - 1)
        elif kind in ('node', 'timer') and expected in ('bool', 'int'):
            if expected == 'bool' and type(field) is not bool:
                raise ValueError('raw node/Timer BOOL')
            if expected == 'int':
                integer(field, 0 if kind == 'timer' else -(1 << 31), 1 if kind == 'timer' else (1 << 31) - 1)
        else:
            validate_typed(field)
            if expected == 'temporary_array':
                if field['type'] != 'array' or any(row['type'] != 'temporary' or row['ordinal'] != i for i, row in enumerate(field['values'])):
                    raise ValueError('ordered temporary ledger projection')
            elif field['type'] not in expected.split('|'):
                raise ValueError('exact raw property type ' + kind + '.' + key)
    for key in ('currentAffectedItems', 'cachedAffectedItems'):
        if key in value:
            validate_cache(value[key], key == 'currentAffectedItems')
    if kind == 'timer':
        if value['node']['class'] != 'Timer':
            raise ValueError('actual Timer class')
        if scalar_number(value['wait_time']) <= 0 or scalar_number(value['time_left']) < 0:
            raise ValueError('Timer public getter range')
    return value


def primitive_context(label, kind):
    if label.startswith('invulnerability_pitch:'):
        if label != 'invulnerability_pitch:P:12' or kind != 'randf_range':
            raise ValueError('fixed selected King pitch context')
        return dict.fromkeys(CONTRACT['primitive_context_exact']) | {'item': 'P:12'}
    result = _base_primitive_context(label, kind)
    if result['item'] not in (None, 'null') and result['item'] not in FIXED_ROLES:
        raise ValueError('primitive unknown selected item role')
    return result


def validate_primitive(payload):
    if payload.get('label') == 'invulnerability_pitch:P:12':
        if payload.get('args') != [{'type': 'float', 'binary64_be': '3feccccccccccccd'}, {'type': 'float', 'binary64_be': '3ff199999999999a'}]:
            raise ValueError('original randPitch0.1 exact REAL endpoints')
    return _base_validate_primitive(payload)


def argument_fields(value):
    validate_typed(value)
    if value['type'] != 'dictionary':
        raise ValueError('typed argument dictionary')
    result = {}
    for row in value['entries']:
        if row['key']['type'] != 'string' or row['key']['value'] in result:
            raise ValueError('unique actual argument names')
        result[row['key']['value']] = row['value']
    return result


def validate_resources(rows, nodes):
    if type(rows) is not list or len(rows) != 2:
        raise ValueError('two source resource panels')
    for row, side in zip(rows, ('P', 'O')):
        exact(row, ('side', 'native_id', 'buffProtectStacks', 'debuffReflectStacks', 'buffs'))
        owners = [n['node'] for n in nodes if n['role'] == 'character:' + side]
        if len(owners) != 1 or row['side'] != side or row['native_id'] != owners[0]['native_id']:
            raise ValueError('source resource actual Character owner')
        for name in ('buffProtectStacks', 'debuffReflectStacks'):
            validate_typed(row[name])
            if row[name]['type'] != 'int':
                raise ValueError('Character stored INT source property ' + name)
        if type(row['buffs']) is not list or len(row['buffs']) != 11:
            raise ValueError('complete eleven source buff ledgers')
        for ledger, category in zip(row['buffs'], range(100, 111)):
            exact(ledger, ('stack', 'state'))
            if ledger['stack'] != {'type': 'int', 'decimal': str(category)}:
                raise ValueError('source stack order/type')
            validate_state(ledger['state'], 'buff')
            state = ledger['state']
            if state['type'] != ledger['stack'] or state['character']['type'] != 'native_ref' or state['character']['native_id'] != row['native_id']:
                raise ValueError('source Buff owner/type join')
            current = decimal(state['current']['decimal'])
            permanent = decimal(state['permanentStacks']['decimal'])
            temporary = sum(decimal(entry['amount']['decimal']) for entry in state['temporaryStacks']['values'])
            if current != permanent + temporary:
                raise ValueError('checkpoint SOURCE current/permanent/temporary ledger invariant')
    return rows


def validate_record(row):
    # Full row validation is independent of physical-file sequence validation.
    if type(row) is dict and row.get('edge') == 'checkpoint':
        payload = row.get('payload')
        exact(payload, ('environment', 'nodes', 'items', 'source_resources'))
        shadow = deepcopy(row)
        del shadow['payload']['source_resources']
        _base_validate_record(shadow)
        validate_resources(payload['source_resources'], payload['nodes'])
        if payload['environment'] != {
            'fps': {'type': 'int', 'decimal': '60'},
            'scale': {'type': 'float', 'binary64_be': '3ff0000000000000'},
            'paused': {'type': 'bool', 'value': False},
        }:
            raise ValueError('fixed60 scale1 unpaused source environment')
    else:
        _base_validate_record(row)
    site, edge, payload = row['site'], row['edge'], row['payload']
    if site in MATRIX['sites'] and edge == 'enter':
        fields = argument_fields(payload['arguments'])
        spec = MATRIX['sites'][site]
        exact(fields, spec['arguments_exact'])
        for key, kind in spec['argument_types'].items():
            if fields[key]['type'] not in kind.split('|'):
                raise ValueError('actual GD entry declared type ' + site + ':' + key)
        expected = {
            'Items/Exclusive/KingGoobert.gd::onStateChanged': {'_crownState': ('int',)},
            'Core/Character.gd::makeInvulnerable': {'invuDur': ('float',), 'item': ('native_ref',), 'triggerEvent': ('null', 'event_ref')},
            'Core/Character.gd::changeBuffProtectStacks': {'amount': ('float',)},
            'Core/CombatLog.gd::createEvent_InvulnerableStart': {'item': ('native_ref',), 'duration': ('float',), 'playerId': ('int',), 'triggerEvent': ('null', 'event_ref')},
            'Core/CombatLog.gd::createEvent_InvulnerableEnd': {'item': ('native_ref',), 'playerId': ('int',), 'triggerEvent': ('null', 'event_ref')},
            'Core/Buff.gd::loseStacks': {'amount': ('int',), 'item': ('null', 'native_ref'), 'triggerEvent': ('null', 'event_ref'), 'used': ('bool',)},
        }.get(site, {})
        for key, kinds in expected.items():
            if fields[key]['type'] not in kinds:
                raise ValueError('specific SOURCE callsite Variant ' + site + ':' + key)
        if site == 'Items/Item.gd::useMana' and row['subject'].get('role') == 'P:12' and fields['amount'] != {'type': 'float', 'binary64_be': '4010000000000000'}:
            raise ValueError('King Item.useMana keeps REAL4 before Character INT coercion')
    if site in MATRIX['sites'] and edge in ('enter', 'return_explicit', 'return_implicit'):
        if row['subject']['type'] != 'native_ref':
            raise ValueError('method receiver actual native ref required')
        if edge == 'return_implicit' and payload['return_value'] != {'type': 'null'}:
            raise ValueError('original observer implicit return is NULL')
        state = payload['state']
        if MATRIX['sites'][site]['state_schema'] == 'character' and row['subject']['role'] is not None:
            side = row['subject']['role']
            if side not in ('P', 'O') or state['playerId'] != {'type': 'int', 'decimal': '0' if side == 'P' else '1'}:
                raise ValueError('actual Character receiver owner/playerId')
        if MATRIX['sites'][site]['state_schema'] == 'generic' and state['native_id'] != row['subject']['native_id']:
            raise ValueError('generic ready/receiver owner identity')
        if 'descriptorIndex' in state and row['subject']['role'] is not None:
            if row['subject']['role'] not in ITEM_INDEX_BY_ROLE or decimal(state['descriptorIndex']['decimal']) != ITEM_INDEX_BY_ROLE[row['subject']['role']]:
                raise ValueError('actual receiver role/source descriptor join')
    if edge in ('timer_before', 'timer_after'):
        if row['subject']['type'] != 'native_ref':
            raise ValueError('Timer API actual receiver')
        native = row['subject']['native_id']
        if payload['role'] not in TIMER_ROLES and payload['role'] != 'native:' + native:
            raise ValueError('unknown Timer API role/receiver')
        state = payload['public_before' if edge == 'timer_before' else 'public_after']
        if state is None or state['node']['native_id'] != native:
            raise ValueError('Timer API direct receiver state identity')
    if edge == 'scene_instance':
        if decimal(payload['item_index']['decimal']) not in DESCRIPTOR_IDS or payload['pooled'] is not False or payload['particle'] is not None:
            raise ValueError('K1 unpooled six-ID scene provenance; no53/168 Timer')
    if len((json.dumps(row, ensure_ascii=False, separators=(',', ':'), allow_nan=False) + '\n').encode()) > CAPS['record_bytes']:
        raise ValueError('complete record cap including source proof')
    return row


def _validate_call_pairs(records):
    stack = []
    pending = []
    for row in records:
        site, edge = row['site'], row['edge']
        subject = row['subject']
        native = subject.get('native_id')
        if site in MATRIX['sites'] and edge == 'enter':
            stack.append((site, native))
        elif site in MATRIX['sites'] and edge in ('return_implicit', 'return_explicit'):
            if not stack or stack.pop() != (site, native):
                raise ValueError('source call return/order without matching enter')
        if edge == 'timer_before':
            pending.append((site, native, row['payload']['operation'], row['payload']['args']))
        elif edge == 'timer_after':
            if not pending or pending.pop() != (site, native, row['payload']['operation'], row['payload']['args']):
                raise ValueError('Timer API paired source order')
    if stack or pending:
        raise ValueError('source stream EOF inside method/API call')


# Source transport implementation is copied mechanically from the sealed355
# framing interface; the public decoder additionally invokes the actual schema.
def _transport_only_decode(raw_by_name):
    raise AssertionError('SOURCE generator replaces this declaration')


def decode_sources(raw_by_name):
    decoded = _transport_only_decode(raw_by_name)
    for name in CHANNEL_FILES:
        for row in decoded[name]:
            validate_record(row)
    return decoded


def validate_source_carriers(raw_by_name):
    decoded = decode_sources(raw_by_name)
    fixture = deepcopy(FIXED_FIXTURE)
    validate_single_king_fixture(fixture)
    for side, name in (('P', 'player_fixture.json'), ('O', 'fixture.json')):
        raw = decoded[name]
        exact(raw, ('schema_version', 'game_version', 'class', 'health', 'stamina', 'items'))
        expected = fixture['sides'][0 if side == 'P' else 1]
        if type(raw['schema_version']) is not int or raw['schema_version'] != 1 or raw['game_version'] != '1.1.8' or type(raw['class']) is not int or raw['class'] != 0:
            raise ValueError('closed fixed A native fixture schema/class')
        if any(type(raw[key]) not in (int, float) or not math.isfinite(raw[key]) or raw[key] != expected[target] for key, target in (('health', 'hp'), ('stamina', 'stamina'))):
            raise ValueError('fixed A lawful resource initial values')
        expected_items = [{key: value for key, value in item.items() if key != 'instance_id'} for item in expected['items']]
        if canonical_sha(raw['items']) != canonical_sha(expected_items):
            raise ValueError('fixed inventory/geometry/order, no slot renumbering')
    header = decoded['king-clock-checkpoint.json']
    exact(header, ('schema', 'lineage', 'environment', 'checkpoint'))
    clock = decode_clock(dict(header, passes=decoded['king-clock-passes.jsonl']))
    proof = validate_single_king_input_provenance(
        decoded['king-ui-authority.jsonl'], decoded['king-rng-checkpoint.json'],
        decoded['observer7-input.jsonl'], decoded['observer7-lineage.jsonl'],
        decoded['king-input-facts.json'], clock,
    )
    combined = sorted((row for name in CHANNEL_FILES for row in decoded[name]), key=lambda row: row['sequence'])
    _validate_call_pairs(combined)  # only after all physical order/unique gates pass
    metadata = [row for row in decoded['observer7-metadata.jsonl'] if row['edge'] == 'loaded_descriptors']
    if len(metadata) != 1:
        raise ValueError('one complete metadata close observation')
    act = next(row for row in decoded['observer7-input.jsonl'] if row['site'] == 'Core/Game.gd::activateItems' and row['edge'] == 'checkpoint')
    if (decimal(act['stamp']['physics_frame']) != clock.physics_frame
            or decimal(act['stamp']['idle_frame']) != clock.idle_frame
            or act['stamp']['util_time'] != {'type': 'float', 'binary64_be': struct.pack('>d', clock.util_time).hex()}):
        raise ValueError('actual activation checkpoint/external clock source cut join')
    identities = {}
    roles = {}
    for record in act['payload']['nodes']:
        node = record['node']
        if node['native_id'] in identities or record['role'] in roles:
            raise ValueError('actual node identity aliases')
        identities[node['native_id']] = record['role']
        roles[record['role']] = node['native_id']
    return dict(schema='phase357-eleven-carrier-source-proof/1', proof=proof,
                source_identity=dict(native_to_role=identities, role_to_native=roles),
                clocks=dict(passes=len(clock.passes), checkpoint=deepcopy(header)),
                dataflow='PROOF_ONLY_NOT_MODEL_RUNTIME_OR_SEED', input_bundle_created=False,
                native_capture_accepted=False, model_calls=0)


def validate_observation_records(records, source_identity):
    """Expected-only API; never called by decode_sources, no output-to-input path."""
    if type(records) is not list or len(records) > CAPS['records']:
        raise ValueError('bounded observation records')
    exact(source_identity, ('native_to_role', 'role_to_native'))
    previous = -1
    for row in records:
        validate_record(row)
        if row['channel'] not in ('runtime', 'allocation', 'registration') or row['sequence'] <= previous:
            raise ValueError('ordered expected channels only')
        previous = row['sequence']
        if row['edge'] in ('timer_before', 'timer_after'):
            native = row['subject']['native_id']
            role = source_identity['native_to_role'].get(native)
            if role not in TIMER_ROLES or source_identity['role_to_native'].get(role) != native:
                raise ValueError('unknown/unproven observed Timer owner')
            if row['payload']['role'] not in (role, 'native:' + native):
                raise ValueError('observed Timer role disguised by caller')
    _validate_call_pairs(records)
    return dict(status='TYPED_EXPECTED_OBSERVATIONS_ONLY', records=len(records), no_input_projection=True)


def validate_terminal_evidence(endpoint, clock, cleanup):
    """Expected-only finite-cut proof. Never a model termination input."""
    exact(endpoint, ('schema', 'phase', 'physics_frame', 'idle_frame', 'passes', 'two_future_physics_signals', 'fx_exact_comparison'))
    if endpoint['schema'] != 'phase111-fixed-endpoint/1' or endpoint['phase'] != 'idle_pre_internal_flush' or type(endpoint['two_future_physics_signals']) is not int or endpoint['two_future_physics_signals'] != 2 or endpoint['fx_exact_comparison'] != 'NOT_EVALUATED_REQUIRES_MODEL':
        raise ValueError('finite terminal source-cut schema')
    for name in ('physics_frame', 'idle_frame', 'passes'):
        _counter(endpoint[name])
    final = clock.passes[-1]
    if final.kind != 'idle' or (endpoint['physics_frame'], endpoint['idle_frame'], endpoint['passes']) != (final.physics_frame, final.idle_frame, len(clock.passes)):
        raise ValueError('terminal last actual idle cut/trailing')
    exact(cleanup, ('physics_frame', 'idle_frame', 'is_in_physics_frame'))
    _counter(cleanup['physics_frame']); _counter(cleanup['idle_frame'])
    if type(cleanup['is_in_physics_frame']) is not bool:
        raise ValueError('actual cleanup phase BOOL')
    kind = 'physics' if cleanup['is_in_physics_frame'] else 'idle'
    positions = [i for i, p in enumerate(clock.passes) if (p.kind, p.physics_frame, p.idle_frame) == (kind, cleanup['physics_frame'], cleanup['idle_frame'])]
    if len(positions) == 1:
        tail = clock.passes[positions[0] + 1:]
    elif not positions and kind == 'idle' and (cleanup['physics_frame'], cleanup['idle_frame']) == (clock.physics_frame, clock.idle_frame):
        tail = clock.passes
    else:
        raise ValueError('cleanup actual clock association')
    if sum(p.kind == 'physics' for p in tail) != 2:
        raise ValueError('exactly two future physics signals')
    second = max(i for i, p in enumerate(tail) if p.kind == 'physics')
    if len(tail) != second + 2 or tail[-1].kind != 'idle':
        raise ValueError('first eligible idle-preinternal only; EOF/trailing rejected')
    return dict(status='EXPECTED_ONLY_TWO_FUTURE_PHYSICS_IDLE_PREINTERNAL', no_model_stop_command=True)


schema = SimpleNamespace(
    validate_record=validate_record, validate_state=validate_state, validate_typed=validate_typed,
    validate_primitive=validate_primitive, primitive_context=primitive_context,
    strict_json_loads=strict_json_loads, exact=exact, integer=integer, decimal=decimal,
    text=text, CAPS=CAPS, CONTRACT=CONTRACT, MATRIX=MATRIX,
)
