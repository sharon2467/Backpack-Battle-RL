"""New actual-object application of accepted438/439 initial Source lemmas."""
from copy import deepcopy
import json
import re

PHASES = ('pre_prepare', 'pre_activate')
COMMON = (('tick:P', 'tick:O') + tuple(f'buff:{s}:{n}' for s in ('P', 'O') for n in range(100, 111))
          + ('fatigue:start', 'fatigue:tick') + tuple(f'aux:{s}:{n}' for s in ('P', 'O') for n in ('battleRageTimer', 'autoRageTimer'))
          + ('invu:P', 'invu:O'))
ZERO = {'type': 'float', 'binary64_be': '0000000000000000'}
MINUS_ONE = {'type': 'float', 'binary64_be': 'bff0000000000000'}
SOURCE_PREMISES = ('Accepted G02 ordinary legitimate native Timer processing invariant, closed modes/no escaped inherited flag writers/reentry; not publiczero proof.', 'Accepted438 Character pre-ready caller/default domain plus actual two invu birth/owner/monotonic lifetime zero-start ledgers; no resets assumed.', '502v4/503 fixed nine-ID zeroKing producer domain and accepted shared native rule origins are Source premises; no old instance audit or Native seed law.', '32 actual new Timer identities at two uniquely located cuts: pausedfalse/internalflagsfalse supports private-1; no fresh-history assertion for every native object.')


def require(value, message):
    if not value:
        raise ValueError(message)


def same(a, b):
    return json.dumps(a, sort_keys=True, separators=(',', ':'), allow_nan=False) == json.dumps(b, sort_keys=True, separators=(',', ':'), allow_nan=False)


def ref(record, pointer, owner, line):
    return {'file': 'observer7-input.jsonl', 'line': line, 'sequence': record['sequence'],
            'native_owner': owner, 'pointer': pointer}


def integer(value, expected):
    require(same(value, {'type': 'int', 'decimal': str(expected)}), 'INITIAL_TYPED_INT_' + str(expected))


def validate_cache_alias(value, aliases, schema, current):
    schema.validate_cache(value, current=current)
    for color in value['entries']:
        content = color['value']
        refs = [entry['key'] for entry in content['entries']] if current else content['values']
        for item in refs:
            require(item['class'] == 'RigidBody2D' and aliases['role_to_native'].get(item['role']) == item['native_id']
                    and aliases['native_to_role'].get(item['native_id']) == item['role'], 'CACHE_NATIVE_ROLE_ASSOCIATION')


def parent_spec(role):
    if role.startswith('fatigue:'):
        return 'combat_timer','FatigueStartTimer' if role.endswith('start') else 'FatigueTickTimer',None
    parts=role.split(':');side=parts[1]
    if parts[0]=='buff':return 'character:'+side,None,None
    if parts[0]=='tick':return 'character:'+side,'TickTimer',None
    if parts[0]=='invu':return 'character:'+side,'InvulnerabilityTimer',None
    return 'character:'+side,'BattleRageTimer' if parts[2]=='battleRageTimer' else 'AutoRageTimer',None


def validate_timer(wrapper, parent, role, schema):
    require(type(wrapper) is dict and set(wrapper) == {'role', 'node', 'timer'} and wrapper['role'] == role, 'TIMER_WRAPPER')
    node, timer = wrapper['node'], wrapper['timer']
    schema.validate_state(timer, 'timer')
    require(same(timer['node'], node), 'TIMER_NODE_DUAL')
    require(node['role'] == role and node['class'] == 'Timer' and node['inside_tree'] is True, 'TIMER_NATIVE_IDENTITY')
    _, name, child = parent_spec(role)
    require(node['path'] == parent['path'] + '/' + node['name'] and node['positions'][:-1] == parent['positions'], 'TIMER_PARENT_PATH_POSITION')
    if name is None:
        require(re.fullmatch(r'@@[0-9]+', node['name']) is not None, 'NATIVE_BUFF_TIMER_NAME')
    else:
        require(node['name'] == name, 'SOURCE_SCENE_TIMER_NAME')
    require(parent['inside_tree'] is True and parent['class'] == 'Node2D', 'TIMER_PARENT_CLASS_TREE')
    require(type(timer['process_mode']) is int and timer['process_mode'] == 0, 'STRICT_MODE_INT0')
    for field in ('paused', 'autostart'):
        require(type(timer[field]) is bool and timer[field] is False, 'STRICT_TIMER_FALSE_' + field)
    for field in ('internal_idle', 'internal_physics', 'ordinary_idle', 'ordinary_physics'):
        require(type(node[field]) is bool and node[field] is False, 'STRICT_TIMER_NODE_FALSE_' + field)
    require(type(timer['stopped']) is bool and timer['stopped'] is True and same(timer['time_left'], ZERO), 'PUBLIC_TIMER_CONSISTENCY')
    require(type(timer['one_shot']) is bool and timer['one_shot'] is (not role.startswith('tick:')), 'SOURCE_TIMER_ONE_SHOT')
    require(same(timer['wait_time'], {'type': 'float', 'binary64_be': '3ff0000000000000'}), 'SOURCE_TIMER_WAIT1')
    return timer


def validate_ledger(facts,role,owner,timer,schema):
    require(type(facts) is dict and facts.get('schema')=='phase502-zero-king-input-facts/1' and facts.get('kings')==[],'INITIAL_ZERO_KING_FACTS')
    fact=facts['timers'].get(role)
    require(type(fact) is dict and set(fact)=={'lineage','current','private_provenance'},'INITIAL_FACT_SHAPE')
    ledger=fact['lineage']
    require(type(ledger) is dict and set(ledger)=={'timer_id','owner_id','kind','starts','stops','birth'},'INITIAL_LEDGER_SHAPE')
    require(ledger['timer_id']==timer['node']['native_id'] and ledger['owner_id']==owner['native_id']
            and ledger['kind']=='Character.scene.ready','INITIAL_LEDGER_OWNER_KIND')
    require(type(ledger['starts']) is int and ledger['starts']==0 and type(ledger['stops']) is int and ledger['stops']>=0,'LIFETIME_NO_START_NONNEGATIVE_STOPS')
    birth=ledger['birth'];schema.validate_state(birth,'timer',constructor=True);bn=birth['node']
    require(bn['native_id']==timer['node']['native_id'] and bn['role'] is None and bn['class']=='Timer'
            and bn['name']==timer['node']['name'],'INITIAL_BIRTH_ID_CLASS_NAME')
    for field in ('process_mode','wait_time','one_shot','autostart','paused','stopped','time_left'):
        require(same(birth[field],timer[field]),'INITIAL_BIRTH_CONFIG_'+field)
    require(type(birth['process_mode']) is int and type(birth['paused']) is bool and type(birth['autostart']) is bool,'BIRTH_STRICT_TYPES')
    for field in ('ordinary_physics','internal_physics','ordinary_idle','internal_idle'):
        require(type(bn[field]) is bool and bn[field] is False,'BIRTH_INACTIVE_FLAGS')
    require(bn['inside_tree'] is True and bn['path']==timer['node']['path']
            and bn['path']==owner['path']+'/'+bn['name'] and bn['positions'][:-1]==owner['positions'],'CHARACTER_BIRTH_ACTUAL_PARENT')
    require(same(fact['current'],timer),'FACTS_CURRENT_CUT_JOIN')
    return {'file':'king-input-facts.json','pointer':'/timers/'+role+'/lineage',
            'native_owner':timer['node']['native_id'],'lineage':deepcopy(ledger)}


def build_initial_receipt(decoded, aliases, schema):
    rows = decoded['observer7-input.jsonl']; cuts = []
    for site in ('prepareItems', 'activateItems'):
        matches = [x for x in rows if x['site'] == 'Core/Game.gd::' + site and x['edge'] == 'checkpoint']
        require(len(matches) == 1, 'UNIQUE_INITIAL_CUT')
        cuts.append(matches[0])
    require(cuts[0]['sequence'] < cuts[1]['sequence'],'ACTUAL_INITIAL_CUT_ORDER')
    schema.validate_single_king_fresh_facts(decoded['king-input-facts.json'])
    result = {'schema': 'phase511-actual-object-initial-receipt/1', 'profile': 'pure-combat-whelp-family-A-captured/1',
              'status': 'SOURCE_SUPPORTED_INITIAL_INPUT_ONLY', 'source_premises': list(SOURCE_PREMISES),
              'values': [], 'timer_witnesses': [], 'lifetime_witnesses': {}, 'prepare_observations': {},
              'model_release': False, 'publiczero_is_proof': False}
    def put(field, phase, role, value, refs, rule=None):
        result['values'].append({'key': [field, phase, role], 'actual_value': deepcopy(value), 'input_refs': deepcopy(refs),
                                 'classification': 'SOURCE_DERIVED' if rule else 'DIRECT_OBSERVATION', 'rule': rule})
    maps, ids = [], None
    for phase, record in zip(PHASES,cuts):
        line=next(i for i,row in enumerate(rows,1) if row is record)
        require(record['schema'] == 'observer7-record/1' and record['channel'] == 'input' and record['edge'] == 'checkpoint'
                and record['stamp']['phase'] == record['site'] + ':enter', 'INITIAL_CUT_PHASE')
        require(same(record['stamp']['combat_time'], ZERO), 'INITIAL_COMBAT_CLOCK0')
        payload = record['payload']
        require(same(payload['environment'], {'fps': {'type': 'int', 'decimal': '60'},
                'scale': {'type': 'float', 'binary64_be': '3ff0000000000000'}, 'paused': {'type': 'bool', 'value': False}}), 'INITIAL_ENVIRONMENT')
        nodes, current_ids = {}, {}
        for i, wrapper in enumerate(payload['nodes']):
            require(wrapper['role'] not in nodes, 'INITIAL_DUPLICATE_ROLE')
            schema.validate_state(wrapper['node'], 'node')
            node = wrapper['node']; raw_role = wrapper['role']
            inner = raw_role.split(':', 1)[1] if raw_role.startswith(('character:', 'item:')) else raw_role
            require(node['role'] == inner and aliases['role_to_native'].get(inner) == node['native_id']
                    and aliases['native_to_role'].get(node['native_id']) == inner, 'INITIAL_NODE_ALIAS')
            nodes[raw_role] = (i, wrapper); current_ids[raw_role] = node['native_id']
        require(len(nodes) == len(set(current_ids.values())) == 67 and (ids is None or current_ids == ids), 'INITIAL_COMPLETE_CROSSCUT_BIJECTION')
        ids = current_ids
        require(record['subject'] == {'type': 'native_ref', 'native_id': current_ids['game'], 'role': 'game', 'class': 'Node2D'}, 'CUT_GAME_OWNER')
        resources = payload['source_resources']
        require(type(resources) is list and len(resources) == 2 and {r['side'] for r in resources} == {'P', 'O'}, 'INITIAL_RESOURCES')
        timer_roles = {name for name, (_, wrapper) in nodes.items() if wrapper['timer'] is not None}
        require(timer_roles == set(COMMON), 'EXACT32_RAW_TIMERS')
        for role in COMMON:
            ni, wrapper = nodes[role]; parent_role, _, _ = parent_spec(role)
            pi, pw = nodes[parent_role]; parent = pw['node']
            timer = validate_timer(wrapper, parent, role, schema)
            refs = [ref(record, f'/payload/nodes/{ni}/timer', wrapper['node']['native_id'], line)]
            if role.startswith('buff:'):
                _, side, category = role.split(':'); si, resource = next((i, r) for i, r in enumerate(resources) if r['side'] == side)
                require(resource['native_id'] == parent['native_id'], 'BUFF_RESOURCE_OWNER')
                require(same([b['stack'] for b in resource['buffs']], [{'type': 'int', 'decimal': str(n)} for n in range(100, 111)]), 'BUFF11_ORDER')
                bi = int(category) - 100; state = resource['buffs'][bi]['state']
                require(same(state['type'], {'type': 'int', 'decimal': category}) and same(state['character'],
                        {'type': 'native_ref', 'native_id': parent['native_id'], 'role': side, 'class': 'Node2D'}), 'BUFF_TYPE_CHARACTER')
                require(same(state['timer'], timer), 'BUFF_RESOURCE_TIMER_DUAL')
                refs.append(ref(record, f'/payload/source_resources/{si}/buffs/{bi}/state/timer', timer['node']['native_id'], line))
            for field in ('wait_time', 'one_shot', 'process_mode', 'autostart', 'paused'):
                put('Timer.' + field, phase, role, timer[field], [dict(refs[0], pointer=refs[0]['pointer'] + '/' + field)])
            put('Timer.node.native_id', phase, role, timer['node']['native_id'], [dict(refs[0], pointer=refs[0]['pointer'] + '/node/native_id')])
            put('Timer.private_left', phase, role, MINUS_ONE, refs,
                'INACTIVE_PROCESSING_INVARIANT')
            result['timer_witnesses'].append({'phase': phase, 'role': role, 'owner_ref': ref(record, f'/payload/nodes/{pi}/node', parent['native_id'], line),
                   'timer_refs': refs, 'native_id': timer['node']['native_id'], 'parent_id': parent['native_id'],
                   'native_node': deepcopy(timer['node']), 'typed_witness': {k: deepcopy(timer[k]) for k in ('paused', 'process_mode', 'autostart', 'time_left', 'stopped')}})
        for si, resource in enumerate(resources):
            side = resource['side']; owner = nodes['character:' + side][1]['node']
            require(resource['native_id'] == owner['native_id'] and owner['class'] == 'Node2D' and owner['name'] == 'Character', 'CHARACTER_RESOURCE_ALIAS')
            schema.validate_typed(resource['buffProtectStacks']); require(resource['buffProtectStacks']['type'] == 'int', 'CHARACTER_PROTECT_TYPED')
            put('Character.buffProtectStacks', phase, side, resource['buffProtectStacks'],
                [ref(record, f'/payload/source_resources/{si}/buffProtectStacks', owner['native_id'], line)])
            for field, value in (('invulnerable', {'type': 'bool', 'value': False}), ('invulnerabilityItem', {'type': 'null'})):
                put('Character.' + field, phase, side, value,
                    [ref(record, f'/payload/nodes/{nodes["invu:" + side][0]}/timer', nodes['invu:' + side][1]['node']['native_id'], line),
                     {'file': 'king-input-facts.json', 'pointer': '/timers/invu:' + side + '/lineage', 'native_owner': nodes['invu:' + side][1]['node']['native_id']}],
                    'CHARACTER_DEFAULT_CALLER_CLOSURE_LIFETIME_ZERO_START')
        observations = {}
        require(len(payload['items']) == 29 and {x['instance'] for x in payload['items']} == schema.FIXED_ROLES, 'INITIAL29_ITEMS')
        for ii, item in enumerate(payload['items']):
            role = item['instance']; fields = item['fields']
            if phase == 'pre_activate':
                validate_cache_alias(item['cachedAffectedItems'], aliases, schema, current=False)
            else:
                require(same(item['cachedAffectedItems'], {'type': 'dictionary', 'entries': []}), 'INITIAL_EMPTY_CACHE')
            validate_cache_alias(item['currentAffectedItems'], aliases, schema, current=True)
            require(same(fields['cachedAffectedItems'], item['cachedAffectedItems']) and same(fields['currentAffectedItems'], item['currentAffectedItems']), 'ITEM_CACHE_DUAL')
            observations[role] = {'input_ref': ref(record, f'/payload/items/{ii}', aliases['role_to_native'][role], line),
                'cachedAffectedItems': deepcopy(item['cachedAffectedItems']), 'currentAffectedItems': deepcopy(item['currentAffectedItems'])}
            if role == 'P:9':
                threshold='4014000000000000';integer(fields['activations'],0)
                require(same(fields['activationsToTrigger'],{'type':'float','binary64_be':threshold}),'BASIC_TYPED_THRESHOLD5')
                for field in ('iterationCooldown','triggerTime'):
                    require(same(fields[field],ZERO if phase=='pre_prepare' else {'type':'float','binary64_be':threshold}),'BASIC_PREPARE_STAGE_'+field)
                observations[role]['goobert_state']={k:deepcopy(fields[k]) for k in ('activations','activationsToTrigger','iterationCooldown','triggerTime')}
            if role == 'P:14':
                expected={'type':'array','values':[{'type':'int','decimal':str(i)} for i in (101,102,103,104,106,107)]}
                require(same(fields['stackTypes'],expected),'SAPPHIRE_ORDERED_SIX_INT')
                observations[role]['stackTypes']=deepcopy(fields['stackTypes'])
        result['prepare_observations'][phase] = observations
        maps.append(nodes)
    facts = decoded['king-input-facts.json']
    for role in ('invu:P','invu:O'):
        parent_role, _, _ = parent_spec(role)
        result['lifetime_witnesses'][role] = validate_ledger(facts, role, maps[1][parent_role][1]['node'], maps[1][role][1]['timer'], schema)
        require(maps[0][role][1]['node']['native_id'] == facts['timers'][role]['lineage']['timer_id'], 'BIRTH_BOTH_CUTS_TIMER')
    derived = [r for r in result['values'] if r['classification'] == 'SOURCE_DERIVED']
    require(len(derived) == 72, 'NEW64_TIMER_PLUS8_CHARACTER_FACTS')
    result['counts'] = {'SOURCE_DERIVED': len(derived), 'DIRECT_OBSERVATION': len(result['values']) - len(derived)}
    result['limits'] = ['New emitted-field receipt only; not old1363audit or fullschema.',
                        'Historical Source domain/G02 bounded premises retained; no fresh environment/native seed law.',
                        'Prepared cache arrays retain actual physical order; constructor/prepare equivalence remains external model gate.']
    return result


def value_index(receipt):
    result = {}
    for ordinal, row in enumerate(receipt['values']):
        key = tuple(row['key'])
        require(key not in result, 'DUPLICATE_INITIAL_RECEIPT_KEY')
        result[key] = (ordinal, row)
    return result
