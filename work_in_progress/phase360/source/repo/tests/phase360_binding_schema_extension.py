"""Appended SOURCE template: auxiliary binding proof, never model admission.

The generator embeds the exact fixed plan and SOURCE-origin descriptors.  This
template deliberately has no imports, runtime calls, filesystem or entry point.
"""


def _binding_same_source(value, expected):
    if type(value) is not type(expected):
        raise ValueError('SOURCE value has a different primitive/container type')
    if type(expected) is dict:
        exact(value, expected)
        for key in expected:
            _binding_same_source(value[key], expected[key])
    elif type(expected) is list:
        if len(value) != len(expected):
            raise ValueError('SOURCE list length')
        for actual, planned in zip(value, expected):
            _binding_same_source(actual, planned)
    elif type(expected) not in (str, int, bool, type(None)) or value != expected:
        raise ValueError('exact frozen SOURCE literal required')


def _binding_id(value):
    decimal(value, True)
    return value


def _binding_integer_value(value):
    validate_typed(value)
    if value['type'] != 'int':
        raise ValueError('binding actual INT required')
    return decimal(value['decimal'])


def _binding_real_value(value):
    validate_typed(value)
    if value['type'] != 'float':
        raise ValueError('binding actual REAL required')
    return _single_king_real(value['binary64_be'])


def _binding_cells(cells, expected):
    if type(cells) is not list or len(cells) != len(expected):
        raise ValueError('binding occupied cell count')
    seen = set()
    wanted = {tuple(cell) for cell in expected}
    for cell in cells:
        if type(cell) is not list or len(cell) != 2:
            raise ValueError('binding occupied cell pair')
        point = tuple(integer(coordinate, 0, 127) for coordinate in cell)
        if point not in wanted or point in seen:
            raise ValueError('binding duplicate/foreign occupied cell')
        seen.add(point)
    if seen != wanted:
        raise ValueError('binding missing occupied cell')


def _binding_validate_value(value, fixed_plan):
    _binding_same_source(fixed_plan, BINDING_FIXED_PLAN)
    exact(value, ('schema', 'source_slot_table', 'actual_bindings',
                  'raw_early_rows_unchanged', 'model_input_admitted', 'remaining_interface'))
    if (value['schema'] != 'phase359-source-slot-bindings/1'
            or value['raw_early_rows_unchanged'] is not True
            or value['model_input_admitted'] is not False
            or value['remaining_interface'] != 'NOT_IN_358_ELEVEN_CARRIER_SCHEMA'):
        raise ValueError('exact359 auxiliary SOURCE format, not an admission flag')
    _binding_same_source(value['source_slot_table'], BINDING_FIXED_PLAN)
    rows = value['actual_bindings']
    if type(rows) is not list or len(rows) != len(BINDING_FIXED_PLAN):
        raise ValueError('exact39 actual slot bindings')
    planned = {row['instance_id']: row for row in BINDING_FIXED_PLAN}
    roles, natives, characters, inventories = set(), set(), {}, {}
    descriptor_by_index, index_by_descriptor = {}, {}
    encountered = {'P': [], 'O': []}
    sides = []
    for row in rows:
        exact(row, ('instance_id', 'input_slot', 'native_id', 'descriptor_id', 'item_index',
                    'top_left', 'orientation', 'occupiedCells', 'inventory_id', 'character_id',
                    'inventory_encounter_index'))
        role = row['instance_id']
        if type(role) is not str or role not in planned or role in roles:
            raise ValueError('unknown/duplicate fixed binding role; no O:12 renumbering')
        roles.add(role)
        spec = planned[role]
        side = spec['side']
        sides.append(side)
        if integer(row['input_slot'], 0, 19) != spec['input_slot']:
            raise ValueError('binding original fixture slot differs')
        if _binding_integer_value(row['item_index']) != spec['item_index']:
            raise ValueError('binding descriptor differs from SOURCE slot')
        if _binding_integer_value(row['orientation']) != spec['f']:
            raise ValueError('binding orientation differs from SOURCE slot')
        exact(row['top_left'], ('x', 'y'))
        for axis in ('x', 'y'):
            if _binding_real_value(row['top_left'][axis]) != spec[axis]:
                raise ValueError('binding actual top-left differs from SOURCE geometry')
        _binding_cells(row['occupiedCells'], spec['cells'])
        native, descriptor, inventory, character = [_binding_id(row[key]) for key in
            ('native_id', 'descriptor_id', 'inventory_id', 'character_id')]
        if native in natives:
            raise ValueError('actual item nativeID reused across slots')
        natives.add(native)
        if (side in characters and characters[side] != character
                or side in inventories and inventories[side] != inventory):
            raise ValueError('one actual character/inventory per side')
        characters[side], inventories[side] = character, inventory
        index = spec['item_index']
        if (index in descriptor_by_index and descriptor_by_index[index] != descriptor
                or descriptor in index_by_descriptor and index_by_descriptor[descriptor] != index):
            raise ValueError('actual descriptor/index association inconsistent')
        descriptor_by_index[index], index_by_descriptor[descriptor] = descriptor, index
        position = integer(row['inventory_encounter_index'], 0, 19)
        encountered[side].append(position)
    if roles != set(planned) or sides != [row['side'] for row in BINDING_FIXED_PLAN]:
        raise ValueError('exact fixed sides and source traversal groups')
    for side in ('P', 'O'):
        if encountered[side] != list(range(len(encountered[side]))):
            raise ValueError('actual inventory encounter order; never sorted into place')
    objects = list(characters.values()) + list(inventories.values())
    if (len(objects) != len(set(objects)) or set(objects) & natives
            or set(index_by_descriptor) & (natives | set(objects))):
        raise ValueError('item/character/inventory/descriptor native object aliases')
    return deepcopy(value)


def validate_binding_carrier(binding_bytes, fixed_plan):
    """Local closed DTO validation only, not a fullbundle/native positive."""
    if type(binding_bytes) is not bytes or not 0 < len(binding_bytes) <= BINDING_MAX_BYTES:
        raise ValueError('bounded auxiliary raw bytes required')
    if not binding_bytes.endswith(b'\n'):
        raise ValueError('auxiliary single JSON terminal newline')
    value = strict_json_loads(binding_bytes.decode('utf-8'))
    return _binding_validate_value(value, fixed_plan)


def _binding_check_channels(decoded11):
    exact(decoded11, INPUT_FILES)
    seen = set()
    for name in INPUT_FILES:
        value = decoded11[name]
        if name.endswith('.jsonl'):
            if type(value) is not list or not 1 <= len(value) <= ROW_CAPS[name]:
                raise ValueError('decoded SOURCE stream count')
        elif type(value) is not dict:
            raise ValueError('decoded SOURCE single object')
        if name not in CHANNEL_FILES:
            continue
        previous = -1
        for row in value:
            if type(row) is not dict or row.get('channel') != CHANNEL_FILES[name]:
                raise ValueError('physical filename/source channel mismatch')
            sequence = integer(row.get('sequence'), 0, CAPS['records'] - 1)
            if sequence <= previous or sequence in seen:
                raise ValueError('physical SOURCE order/global sequence uniqueness')
            previous = sequence
            seen.add(sequence)
            validate_record(row)


def _binding_one(rows, site, edge):
    found = [row for row in rows if row['site'] == site and row['edge'] == edge]
    if len(found) != 1:
        raise ValueError('unique binding SOURCE observation ' + site + ':' + edge)
    return found[0]


def _binding_checkpoint(row):
    nodes = {entry['role']: entry['node'] for entry in row['payload']['nodes']}
    wanted = ({'root_viewport', 'game', 'util', 'combat_timer', 'character:P', 'character:O'}
              | TIMER_ROLES | {'item:' + role for role in FIXED_ROLES})
    if set(nodes) != wanted:
        raise ValueError('exact frozen SOURCE checkpoint topology')
    native_to_role, role_to_native = {}, {}
    for envelope, node in nodes.items():
        role = envelope.split(':', 1)[1] if envelope.startswith(('item:', 'character:')) else envelope
        native = _binding_id(node['native_id'])
        if node['role'] != role or native in native_to_role or role in role_to_native:
            raise ValueError('actual checkpoint envelope/inner role/native identity')
        native_to_role[native], role_to_native[role] = role, native
    items = {entry['instance']: entry for entry in row['payload']['items']}
    if set(items) != FIXED_ROLES:
        raise ValueError('complete39 selected SOURCE checkpoint item states')
    return nodes, items, native_to_role, role_to_native


def join_binding_provenance(decoded11, binding, source_contract):
    """Relation-only SOURCE join. Complete11 validation is a separate caller step.

    No trusted 'verified' object shortcut, row mutation, role restamping, sorted
    primitive Tape, resource/default projection, runtime or patch admission.
    """
    _binding_same_source(source_contract, BINDING_SOURCE_CONTRACT)
    binding = _binding_validate_value(binding, BINDING_FIXED_PLAN)
    _binding_check_channels(decoded11)
    before = hashlib.sha256(json.dumps(decoded11, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()
    records = decoded11['observer7-input.jsonl']
    pre = _binding_one(records, 'Core/Game.gd::prepareItems', 'checkpoint')
    act = _binding_one(records, 'Core/Game.gd::activateItems', 'checkpoint')
    if pre['sequence'] >= act['sequence']:
        raise ValueError('binding preparation must precede activation')
    pre_nodes, pre_items, pre_natives, pre_roles = _binding_checkpoint(pre)
    act_nodes, act_items, act_natives, act_roles = _binding_checkpoint(act)
    if pre_natives != act_natives or pre_roles != act_roles:
        raise ValueError('actual pre/activate complete identity continuity')
    for role in pre_nodes:
        if pre_nodes[role]['class'] != act_nodes[role]['class']:
            raise ValueError('native class changed across source checkpoints')
    meta = _binding_one(decoded11['observer7-metadata.jsonl'], 'Sheets/ItemBook.gd::detectMentionedStacks', 'loaded_descriptors')
    descriptors = {}
    for encoded in meta['payload']['descriptors']['values']:
        fields = argument_fields(encoded)
        index = _binding_integer_value(fields['itemIndex'])
        descriptors[index] = fields['scene_path']['value']
    if set(descriptors) != DESCRIPTOR_IDS:
        raise ValueError('binding complete selected SOURCE descriptors')
    lineage = decoded11['observer7-lineage.jsonl']
    planned = {row['instance_id']: row for row in BINDING_FIXED_PLAN}
    evidence, inventory_order = {}, {'P': [], 'O': []}
    for actual in binding['actual_bindings']:
        role = actual['instance_id']
        spec, native = planned[role], actual['native_id']
        side = spec['side']
        if (act_roles.get(role) != native or actual['character_id'] != act_roles[side]):
            raise ValueError('binding actual item/Character differs from checkpoints')
        for nodes, items in ((pre_nodes, pre_items), (act_nodes, act_items)):
            fields = items[role]['fields']
            if (fields['descriptorIndex'] != actual['item_index']
                    or fields['faceDirection'] != actual['orientation']
                    or fields['placed'] != {'type': 'bool', 'value': True}
                    or fields['ownerType'] != {'type': 'int', 'decimal': '1' if side == 'P' else '3'}):
                raise ValueError('actual item descriptor/orientation/placed/Owner source join')
        scenes = [row for row in lineage if row['edge'] == 'scene_instance' and row['payload']['item_id'] == native]
        readies = [row for row in lineage if row['site'] == 'Items/Item.gd::_ready' and row['edge'] == 'enter'
                   and row['subject'].get('native_id') == native]
        if len(scenes) != 1 or len(readies) != 1:
            raise ValueError('one actual scene/ready per selected binding')
        scene, ready = scenes[0], readies[0]
        if (scene['subject']['type'] != 'native_ref' or scene['subject']['native_id'] != native
                or scene['subject']['role'] is not None or ready['subject']['role'] is not None
                or scene['subject']['class'] != act_nodes['item:' + role]['class']
                or ready['subject']['class'] != act_nodes['item:' + role]['class']
                or scene['payload']['descriptor_id'] != actual['descriptor_id']
                or scene['payload']['item_index'] != actual['item_index']
                or scene['payload']['scene_path'] != descriptors[spec['item_index']]
                or scene['payload']['pooled'] is not False
                or ready['payload']['state'] != {'native_id': native}
                or not scene['sequence'] < ready['sequence'] < pre['sequence']):
            raise ValueError('unchanged early NULL-role owner/descriptor/scene/ready chain')
        for counter in ('physics_frame', 'idle_frame'):
            values = [decimal(row['stamp'][counter]) for row in (scene, ready, pre, act)]
            if any(value < 0 for value in values) or values != sorted(values):
                raise ValueError('source birth/ready/checkpoint frame order')
        inventory_order[side].append(role)
        evidence[role] = dict(native_id=native, descriptor_id=actual['descriptor_id'], inventory_id=actual['inventory_id'],
                              character_id=actual['character_id'], scene_sequence=scene['sequence'], ready_sequence=ready['sequence'],
                              pre_sequence=pre['sequence'], activate_sequence=act['sequence'])
    after = hashlib.sha256(json.dumps(decoded11, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()
    if before != after:
        raise ValueError('binding join mutated decoded original observations')
    return dict(schema='phase360-auxiliary-binding-join/1', status='RELATION_PROOF_ONLY_NOT_FULL_ELEVEN_VALIDATION_OR_ADMISSION',
                native_to_role=deepcopy(act_natives), role_to_native=deepcopy(act_roles),
                input_order={side: [row['instance_id'] for row in BINDING_FIXED_PLAN if row['side'] == side] for side in ('P', 'O')},
                inventory_order=inventory_order, evidence_refs=evidence, decoded_observations_sha256=before,
                source_contract=deepcopy(BINDING_SOURCE_CONTRACT),
                source_limits=['359 inventory association derives from actual bind method getter/control-flow SOURCE; no second inventory-node direct sample',
                               '359 has no independent binding stamp; no timestamp was invented', '359 independent producer review is still pending'],
                input_bundle_created=False, native_admitted=False, model_calls=0)


def validate_sources_with_binding(raw11, binding_bytes, source_contract):
    """Full11 checks plus auxiliary relation proof; no projection or admission."""
    _binding_same_source(source_contract, BINDING_SOURCE_CONTRACT)
    if type(raw11) is not dict or set(raw11) != set(INPUT_FILES):
        raise ValueError('exact original eleven SOURCE names; auxiliary stays separate')
    if any(type(value) is not bytes for value in raw11.values()) or type(binding_bytes) is not bytes:
        raise ValueError('raw immutable SOURCE bytes required')
    if sum(map(len, raw11.values())) + len(binding_bytes) > TOTAL_BYTES:
        raise ValueError('combined eleven plus auxiliary total byte cap')
    binding = validate_binding_carrier(binding_bytes, BINDING_FIXED_PLAN)
    eleven = validate_source_carriers(raw11)
    decoded = decode_sources(raw11)
    joined = join_binding_provenance(decoded, binding, source_contract)
    pins = {name: dict(size=len(raw), sha256=hashlib.sha256(raw).hexdigest()) for name, raw in raw11.items()}
    pins['king-slot-bindings.json'] = dict(size=len(binding_bytes), sha256=hashlib.sha256(binding_bytes).hexdigest())
    return dict(schema='phase360-twelve-source-proof/1', status='SOURCE_PROOF_ONLY_NOT_INPUT_BUNDLE_OR_NATIVE_ACCEPTANCE',
                original_eleven_schema=eleven['schema'], binding_join=joined, raw_sources=pins,
                producer_independent_acceptance='PENDING_NOT_ASSERTED_BY_SCHEMA', input_bundle_created=False,
                native_admitted=False, model_calls=0, projection_implemented=False)
