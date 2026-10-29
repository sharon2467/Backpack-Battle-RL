"""Fixed028 joint output-only business projection; no file, model, schema or launcher imports.

Call only from the independent output stage after its exact result/source/input
seal. This module has no I/O and cannot authorize a battle or manufacture inputs.
"""
from copy import deepcopy
import hashlib
import json
import math
import re
import struct

PROFILE = 'pure-combat-king-basic-A-captured/1'
NATIVE_PROFILE = 'observer7-king-basic-A-native-tape/1'
CONTRACT_SHA256 = '71c681047140d3bc13d91b24be590dcb598cb3454edac394288c64e01cb3ecef'
# Actual lawful joint INPUT checkpoint1149 immediately precedes activation enter1150.
# This is a pinned INPUT-origin cut, not an EXPECTED-dependent callback selector.
ACTIVATION_AFTER_SEQUENCE = 1150
STACKS = dict(enumerate(('Block','Lucky','Regeneration','Vampirism','Spikes','Mana','Empower','Heat','Poison','Blind','Cold'),100))
UI_TIMERS = frozenset(('king_hide:P:6','king_drag:P:6'))
EXPECTED_LEAVES = frozenset(('events.jsonl','event_references.json','histories.json','final_state.json',
    'observer7-runtime.jsonl','king-post-cleanup-source.json','king-final-source.json',
    'king-capture-endpoint.json','king-collector-cut.json'))
SECTIONS = ('events','event_references','histories','rng','final','callbacks','timer_api','cuts')
NODE_KEYS = ('native_id','role','path','name','class','positions','priority','inside_tree',
             'ordinary_physics','internal_physics','ordinary_idle','internal_idle')
FLAGS = ('inside_tree','ordinary_physics','internal_physics','ordinary_idle','internal_idle')
TIMER_KEYS = ('process_mode','wait_time','time_left','one_shot','autostart','paused','stopped')
RNG_KEYS = ('expectedWins','wins','balancedness','lastResult','extraLuck','lastTarget','accChance')
KING_KEYS = ('activations','activationsToTrigger','invuCharges','protectedBuffs','manaCost')
# Generated below from the accepted fixed bundle and the frozen391 SOURCE ABI.
NATIVE_SITES = frozenset(('Core/Buff.gd::TemporaryStacks._init', 'Core/Buff.gd::changeCleanseProtectionChance', 'Core/Buff.gd::changeCurrentLogShowLabel', 'Core/Buff.gd::changeReflectChance', 'Core/Buff.gd::changeResistChance', 'Core/Buff.gd::combatEnd', 'Core/Buff.gd::gainTemporary', 'Core/Buff.gd::init', 'Core/Buff.gd::loseStacks', 'Core/Buff.gd::onTimeout', 'Core/Character.gd::_physics_process', 'Core/Character.gd::_ready', 'Core/Character.gd::changeBuffProtectStacks', 'Core/Character.gd::changeDebuffReflectStacks', 'Core/Character.gd::changeMaxHealthTemporary', 'Core/Character.gd::cleanse', 'Core/Character.gd::combatEnd', 'Core/Character.gd::combatStart', 'Core/Character.gd::endBattleRage', 'Core/Character.gd::endStun', 'Core/Character.gd::gainMana', 'Core/Character.gd::gainStacks', 'Core/Character.gd::gainStacksTemporary', 'Core/Character.gd::invulnerabilityEnded', 'Core/Character.gd::loseHealth', 'Core/Character.gd::makeInvulnerable', 'Core/Character.gd::onTick', 'Core/Character.gd::prepare', 'Core/Character.gd::startBattleRage', 'Core/Character.gd::stun', 'Core/Character.gd::takeDamage', 'Core/Character.gd::useMana', 'Core/Character.gd::useStacks', 'Core/CombatLog.gd::createEvent', 'Core/CombatLog.gd::createEvent_BattleRageEnd', 'Core/CombatLog.gd::createEvent_BattleRageStart', 'Core/CombatLog.gd::createEvent_InvulnerableEnd', 'Core/CombatLog.gd::createEvent_InvulnerableStart', 'Core/CombatLog.gd::createEvent_Stack', 'Core/CombatLog.gd::createEvent_StackTemporary', 'Core/CombatLog.gd::createEvent_StackTimeout', 'Core/CombatLog.gd::logEvent', 'Core/CombatLog.gd::onCombatEnd', 'Core/CombatLog.gd::snapshotItemState', 'Core/Game.gd::activateItems', 'Core/Game.gd::combatEndDeferred', 'Core/Game.gd::endCombat', 'Core/Game.gd::prepareItems', 'Interface/CombatTimer/CombatTimer.gd::_physics_process', 'Interface/CombatTimer/CombatTimer.gd::combatEnd', 'Interface/CombatTimer/CombatTimer.gd::dealFatigueDamage', 'Interface/CombatTimer/CombatTimer.gd::start', 'Interface/CombatTimer/CombatTimer.gd::startFatigue', 'Items/Exclusive/KingGoobert.gd::buffEnded', 'Items/Exclusive/KingGoobert.gd::doCooldownEffect', 'Items/Exclusive/KingGoobert.gd::onCombatEnd', 'Items/Exclusive/KingGoobert.gd::onStateChanged', 'Items/Exclusive/KingGoobert.gd::prepare', 'Items/HealthPotion.gd::onDamaged', 'Items/HealthPotion.gd::onPrepare', 'Items/HealthPotion.gd::onTriggerPotion', 'Items/Item.gd::_physics_process', 'Items/Item.gd::_ready', 'Items/Item.gd::activate', 'Items/Item.gd::addBonusDamage', 'Items/Item.gd::cleanseRandomDebuffs', 'Items/Item.gd::combatEnd', 'Items/Item.gd::consume', 'Items/Item.gd::getMostStacks', 'Items/Item.gd::giveMana', 'Items/Item.gd::giveMana_capped', 'Items/Item.gd::giveMaxHealth', 'Items/Item.gd::giveMostBuffs', 'Items/Item.gd::healthToBlock', 'Items/Item.gd::miniActivate', 'Items/Item.gd::pickRandomStacks', 'Items/Item.gd::prepare', 'Items/Item.gd::rollChance', 'Items/Item.gd::stealLife', 'Items/Item.gd::tryUseMana', 'Items/Item.gd::useMana', 'Items/ItemDescriptor.gd::instantiate', 'Items/ItemDescriptor.gd::instantiate_pooled', 'Items/Potion.gd::activate', 'Items/Potion.gd::consumePotion', 'Items/Potion.gd::prepare', 'Items/Potion.gd::triggerPotion', 'Items/Weapon.gd::attack', 'Items/Weapon.gd::doCooldownEffect', 'Sheets/ItemBook.gd::detectMentionedStacks', 'Utility/AutoHideParticles.gd::_ready', 'Utility/AutoHideParticles.gd::activate', 'Utility/AutoHideParticles.gd::deactivate', 'Utility/AutoHideParticles.gd::instantClear', 'Utility/AutoHideParticles.gd::startTimer', 'Utility/AutoHideParticles.gd::timeout', 'Utility/EventBus.gd::connectEvent', 'Utility/EventBus.gd::disconnectAll', 'Utility/EventBus.gd::emitAndLog', 'Utility/EventBus.gd::flushLoggingQueue', 'Utility/Util.gd::_physics_process', 'Utility/Util.gd::_process', 'Utility/Util.gd::changeTimer', 'Items/Goobert.gd::prepare', 'Items/Goobert.gd::onItemActivated', 'Items/Goobert.gd::doCooldownEffect', 'Items/Food.gd::prepare'))
MODEL_SOURCE_HASHES = {'component:__init__.py': '82b496191ffa3ec2761b83bf4de9267089d077b777ee38e4b93ab0cb824c4612', 'component:frame_driver.py': '9d8e361144e353a8d944e4490502c5301e7a92451771d35f22ab48f6277f64fd', 'component:timer_runtime.py': '5b7c14ebb7c7511aa05a3411752c7f3341b925c00de31eedfacf4f9345f4a109', '__init__.py': '805cc7035f10e96bfc217ef52f6ac175323ea83c69fb6e678fcd97a5bbcc3d7b', '__main__.py': 'b808649da7470e72669ad7639ef01577187e9692e9ade3745e18b0f21eea647a', 'compare.py': '4af52ee400acf1460c9e28faf5a760d05753d1de7218a00d4a740712a40fdd22', 'engine.py': 'e06bf6493baf0d5d4250c73ea13f6388a0925556e1aafde4043ab9a21871a118', 'genuine.py': '1902f3ee476532abda53fe2cbf219be7c5004f4763ea8f81a17b32e37d0d38d6', 'histories.py': 'd9b3f270b53f328f5958647fdaba86532ff3d9db11b272d9a7d0d2aef1db0b05', 'observed.py': '0a04fb2b03e48cd1cd9a3e43425deddef56c7906105dadeaefafa81ac84a6fd1', 'randomness.py': '676d42a69937394dc1bd8ff23268a08dc41fe9604f7e56213bb968ab331b9139', 'state.py': '21478fecea4c888f701ff8991fb2cf75519670c602ed2bd9d17874e238c54bd1'}

CANDIDATE_FREEZE = {'path': 'data/phase471-captured-joint-source/candidate-source-freeze.json', 'size': 5113, 'sha256': 'd640e6cd25562692ae6bd4cc3b908d5c6e57e20754e0c60221644b87cb8e88b8'}
CONTRACT_DESCRIPTOR = {'path': 'data/phase466-captured-joint-bridge-design/comparison-contract.json', 'size': 4636, 'sha256': '71c681047140d3bc13d91b24be590dcb598cb3454edac394288c64e01cb3ecef'}
FIXTURE_CANONICAL_SHA256 = '20c259d7a7b99ef18f006b049c362fde21830cbb557d5879016282bf7451c0a2'


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def keys(value, names, reason):
    require(type(value) is dict and set(value) == set(names), reason)
    return value


def canonical_sha(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


def strict_json_loads(text):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, 'duplicate JSON key')
            result[key] = value
        return result
    def real(text):
        value = float(text)
        require(math.isfinite(value), 'nonfinite JSON float')
        return value
    def invalid(value):
        raise ValueError('nonfinite JSON constant: '+value)
    return json.loads(text,object_pairs_hook=pairs,parse_float=real,parse_constant=invalid)


def bits(value):
    require(type(value) is float and math.isfinite(value), 'finite REAL required')
    return struct.pack('>d',value).hex()


def decimal(value):
    require(type(value) is str and re.fullmatch(r'0|-?[1-9][0-9]*',value) is not None,'canonical decimal')
    return int(value)


def role(value):
    require(type(value) is str,'role string')
    if value.startswith('buff:'):
        parts = value.split(':')
        require(len(parts)==3 and parts[1] in ('P','O'),'Buff role')
        if parts[2] in STACKS.values():
            return value
        index = decimal(parts[2])
        require(index in STACKS,'Buff numeric type')
        return 'buff:'+parts[1]+':'+STACKS[index]
    for side in ('P','O'):
        remap = {side+':tickTimer':'tick:'+side,side+':invulnerabilityTimer':'invu:'+side,
                 side+':battleRageTimer':'aux:'+side+':battleRageTimer',side+':autoRageTimer':'aux:'+side+':autoRageTimer'}
        if value in remap:
            return remap[value]
    return value


def bindings(bundle,root_binding):
    keys(root_binding,('schema','input_bundle','input_canonical_sha256','candidate_freeze','contract'),'closed external comparison binding')
    require(root_binding['schema']=='phase474-fixed-comparison-binding/1','external binding schema')
    for name in ('input_bundle','candidate_freeze','contract'):
        row=root_binding[name];keys(row,('path','size','sha256'),'actual descriptor shape')
        require(type(row['path']) is str and row['path'] and type(row['size']) is int and row['size']>0
                and type(row['sha256']) is str and re.fullmatch('[0-9a-f]{64}',row['sha256']) is not None,'actual descriptor types')
    require(root_binding['candidate_freeze']==CANDIDATE_FREEZE and root_binding['contract']==CONTRACT_DESCRIPTOR,'exact candidate and pre-Expected contract')
    digest=root_binding['input_canonical_sha256']
    require(type(digest) is str and re.fullmatch('[0-9a-f]{64}',digest) is not None
            and type(bundle) is dict and canonical_sha(bundle)==digest,'authenticated actual INPUT canonical identity')
    require(set(bundle)=={'schema','fixture','runtime','draws','synthetic_seed'} and bundle['schema']=='native-v8-input-only/1'
            and bundle['synthetic_seed'] is None and canonical_sha(bundle['fixture'])==FIXTURE_CANONICAL_SHA256,'exact captured joint envelope/fixture')
    data=bundle['runtime']
    require(data['schema']=='native-v8-pure-combat-runtime-input/king-basic-1' and data['profile_id']==PROFILE
            and data['mode']=='genuine' and len(data['timer_initial'])==33,'joint profile/33Timer')
    table={n['role']:deepcopy(n) for n in data['processing_nodes']}
    require(len(data['processing_nodes'])==len(table)==65,'joint65 processing roles')
    native={n['native_id']:name for name,n in table.items()}
    require(len(native)==65,'native identity bijection')
    items={i['instance_id']:i for side in bundle['fixture']['sides'] for i in side['items']}
    require(len(items)==26 and items['P:6']['item_index']==262 and items['P:7']['item_index']==23
            and items['P:12']['item_index']==1 and items['O:9']['item_index']==19,'joint26 subtype bindings')
    expected={'root_viewport','game','util','combat_timer','character:P','character:O'}|set(data['timer_initial'])|{'item:'+i for i in items}
    require(set(table)==expected,'complete bound business graph')
    return dict(nodes=table,native=native,timers=frozenset(data['timer_initial']),items=items)


def decode_native(value, bound=None):
    if type(value) is list:
        return [decode_native(v,bound) for v in value]
    if type(value) is not dict:
        require(type(value) in (str,int,float,bool,type(None)),'JSON scalar')
        if type(value) is float:bits(value)
        return value
    kind = value.get('type')
    if type(kind) is not str:
        return {k:decode_native(v,bound) for k,v in value.items()}
    if kind=='null':
        keys(value,('type',),'null fields');return None
    if kind=='int':
        keys(value,('type','decimal'),'INT fields');return decimal(value['decimal'])
    if kind=='float':
        require(set(value) in ({'type','binary64_be'},{'type','binary64_le'},{'type','display','binary64_be'},{'type','display','binary64_le'}),'REAL fields')
        if 'display' in value:require(type(value['display']) is str,'collector REAL display metadata')
        endian = 'binary64_be' if 'binary64_be' in value else 'binary64_le'
        raw = value[endian]
        require(type(raw) is str and re.fullmatch('[0-9a-f]{16}',raw) is not None,'REAL bits')
        number = struct.unpack('>d' if endian.endswith('be') else '<d',bytes.fromhex(raw))[0]
        bits(number);return number
    if kind in ('bool','string'):
        keys(value,('type','value'),'BOOL/STRING fields')
        require(type(value['value']) is (bool if kind=='bool' else str),'BOOL/STRING value')
        return value['value']
    if kind=='array':
        require(set(value) in ({'type','values'},{'type','variant_type','values'}),'ARRAY fields')
        if 'variant_type' in value:
            require(type(value['variant_type']) is int and value['variant_type'] in (19,20,21,22,23,24),'collector ARRAY family tag')
        require(type(value['values']) is list,'ARRAY contents')
        return [decode_native(v,bound) for v in value['values']]
    if kind=='TemporaryStacks':
        keys(value,('type','native_id','amount','timeout','item'),'collector TemporaryStacks fields')
        require(decimal(value['native_id'])>0,'TemporaryStacks object identity')
        amount=decode_native(value['amount'],bound);timeout=decode_native(value['timeout'],bound)
        require(type(amount) is int and type(timeout) is float,'TemporaryStacks INT amount/REAL timeout')
        bits(timeout)
        require(type(value['item']) is dict and value['item'].get('type') in ('null','instance_reference'),'TemporaryStacks Item reference form')
        item=decode_native(value['item'],bound)
        require(item is None or bound is not None and type(item) is str and item in bound['items'],'TemporaryStacks bound Item owner')
        return dict(amount=amount,timeout=timeout,item=item)
    if kind=='dictionary':
        keys(value,('type','entries'),'DICTIONARY fields');require(type(value['entries']) is list,'DICTIONARY entries')
        result = {};identities=set()
        for entry in value['entries']:
            keys(entry,('key','value'),'DICTIONARY entry')
            key = decode_native(entry['key'],bound)
            require(type(key) in (str,int),'dictionary key type')
            identity=(type(key).__name__,key)
            require(identity not in identities and key not in result,'duplicate/alias dictionary key')
            identities.add(identity);result[key]=decode_native(entry['value'],bound)
        return result
    if kind=='StatHistory':
        keys(value,('type','event_numbers','values'),'HISTORY fields')
        return {k:decode_native(value[k],bound) for k in ('event_numbers','values')}
    if kind=='Vector2':
        keys(value,('type','x','y'),'VECTOR fields')
        return dict(x=decode_native(value['x'],bound),y=decode_native(value['y'],bound))
    if kind in ('instance_reference','event_reference'):
        keys(value,('type','id'),'collector REF fields')
        if kind=='event_reference':return decimal(value['id'])
        require(type(value['id']) is str and value['id'] in ({'P','O'} | set(bound['items']) if bound else {'P','O'}),'collector instance REF')
        return value['id']
    if kind=='native_ref':
        keys(value,('type','native_id','role','class'),'native REF fields')
        require(bound is not None and value['native_id'] in bound['native'],'native REF owner')
        expected=bound['native'][value['native_id']]
        actual=role(value['role']) if value['role'] is not None else None
        allowed={expected}
        if expected.startswith('character:'):allowed.add(expected[-1])
        if expected.startswith('item:'):allowed.add(expected[5:])
        require(actual in allowed and value['class']==bound['nodes'][expected]['class'],'native REF association')
        return expected[-1] if expected.startswith('character:') else expected[5:] if expected.startswith('item:') else expected
    if kind=='event_ref':
        keys(value,('type','native_id','event_id'),'event REF fields')
        require(decimal(value['native_id'])>0,'event object identity')
        return decimal(value['event_id'])
    raise ValueError('unknown typed Variant '+kind)


def first_difference(left, right, path='$'):
    if type(left) is not type(right):return dict(path=path,native=left,model=right,reason='type')
    if type(left) is dict:
        lk={(type(k).__name__,k) for k in left};rk={(type(k).__name__,k) for k in right}
        if lk!=rk:return dict(path=path,native_keys=sorted(map(repr,lk)),model_keys=sorted(map(repr,rk)),reason='dictionary_key_types_or_members')
        for key in left:
            difference=first_difference(left[key],right[key],path+'.'+str(key))
            if difference:return difference
    elif type(left) is list:
        for i,(a,b) in enumerate(zip(left,right)):
            difference=first_difference(a,b,path+'['+str(i)+']')
            if difference:return difference
        if len(left)!=len(right):return dict(path=path,native_length=len(left),model_length=len(right),reason='length')
    elif type(left) is float:
        if bits(left)!=bits(right):return dict(path=path,native=bits(left),model=bits(right),reason='float_bits')
    elif left!=right:return dict(path=path,native=left,model=right,reason='value')
    return None


def restore_integer_table(table):
    require(type(table) is dict,'integer table')
    result={}
    for key,value in table.items():
        integer=key if type(key) is int else decimal(key)
        require(type(integer) is int and integer not in result,'integer table alias')
        result[integer]=value
    return result


def restore_histories(value):
    value=deepcopy(value)
    for logger in value['stat_loggers']:
        for name in ('characterStatHistories','stackHistories'):
            logger[name]=restore_integer_table(logger[name])
        logger['metricHistories']=[restore_integer_table(table) for table in logger['metricHistories']]
    return value


def project_events(rows,bound,sequence=True):
    require(type(rows) is list,'events array')
    fields=('id','timestamp','parent','origin','target','type','params','snapshot')
    if sequence:fields=('sequence',)+fields
    result=[]
    for row in rows:
        require(type(row) is dict and set(fields)<=set(row),'complete event fields')
        event={k:decode_native(row[k],bound) for k in fields}
        event['timestamp_hex']=bits(event['timestamp'])
        if sequence:require(type(event['sequence']) is int and event['sequence']==len(result),'event sequence')
        require(type(event['id']) is int and (event['parent'] is None or type(event['parent']) is int),'event identity')
        result.append(event)
    return result


def project_references(rows,bound):
    require(type(rows) is dict,'parent-reference object')
    result={}
    for key,value in rows.items():
        require(decimal(key)>=0,'parent reference ID')
        projected=project_events([value],bound,False)[0]
        require(projected['id']==int(key),'parent reference key/value')
        result[key]=projected
    return result


def _basic_fields(item,bound):
    if item['instance']=='P:7':
        require(bound['items']['P:7']['item_index']==23,'bound Basic subtype')
        fields=item['fields']
        require('activations' in fields and type(fields['activations']) is int,'Basic INT counter required')
        for name in ('activationsToTrigger','iterationCooldown','triggerTime'):
            require(name in fields and type(fields[name]) is float,'Basic REAL field required: '+name)
            bits(fields[name])


def _rule_state(native,bound):
    chars=deepcopy(native['characters'])
    require(len(chars)==2 and [c['instance'] for c in chars]==['P','O'],'ordered characters')
    seen=set()
    for char in chars:
        for item in char['items']:
            identity=item['instance'];require(identity in bound['items'] and identity not in seen,'terminal item identity')
            require(identity.startswith(char['instance']+':'),'terminal item side')
            seen.add(identity)
            extra=item.pop('observer7_fields')
            require(type(extra) is dict and not (set(extra)&set(item['fields'])),'subtype fields disjoint')
            item['fields'].update(extra)
            require(item.pop('observer7_timers')=={},'joint seven-ID empty particle wrapper')
            _basic_fields(item,bound)
    require(seen==set(bound['items']),'all26 terminal items')
    return dict(characters=chars,rules=deepcopy(native['rules']))


def project_native_final(native,bound):
    value=decode_native(native,bound)
    for char in value['characters']:
        require(type(char['fields']) is dict,'decoded collector character fields')
        for name,kind in (('characterName',str),('chibi',bool),('invulBubbleVisible',bool)):
            require(name in char['fields'],'native presentation envelope field missing')
            require(type(char['fields'][name]) is kind,'native declared presentation field type')
            del char['fields'][name]
    rule=_rule_state(value,bound)
    code=value['game']['roundResults'][0]
    require(type(code) is int and code in (0,1),'terminal winner code')
    return dict(native_rule_state=rule,game=value['game'],event_bus=value['event_bus'],
        timer=value['timer'],winner='P' if code==0 else 'O')


def project_model_final(result,bound):
    final=result['final'];rule=deepcopy(final['native_rule_state'])
    require([c['instance'] for c in rule['characters']]==['P','O'],'model ordered characters')
    rule['rules']['values']=restore_integer_table(rule['rules']['values']);seen=set()
    for char in rule['characters']:
        char['stats']=restore_integer_table(char['stats'])
        char['fields']['typedDamageFactors']=restore_integer_table(char['fields']['typedDamageFactors'])
        require('invulBubbleVisible' in char['fields'],'model legacy bubble envelope')
        del char['fields']['invulBubbleVisible']
        for item in char['items']:
            identity=item['instance'];require(identity in bound['items'] and identity not in seen,'model26 identity')
            seen.add(identity)
            for name in ('buffPowers','buffAmplificationChances'):
                item['fields'][name]=restore_integer_table(item['fields'][name])
            if bound['items'][identity]['item_index']==19:
                actual=final['items'][identity]
                require(type(actual['item_index']) is int and actual['item_index']==19 and type(actual['potion_full']) is bool,'same-instance HealthPotion live bool')
                require('isFull' not in item['fields'],'unexpected preexisting pure isFull')
                item['fields']['isFull']=actual['potion_full']
            _basic_fields(item,bound)
    require(seen==set(bound['items']),'complete model26')
    return dict(native_rule_state=rule,game=deepcopy(final['game']),event_bus=deepcopy(final['event_bus']),
        timer=dict(combatTime=final['timestamp'],timeAdvance=final['time_advance'],fatigueCounter=final['fatigue_counter']),winner=final['winner'])


def _typed_rng(rule):
    chars={};items={}
    for char in rule['characters']:
        side=char['instance'];keys(char['balanced_rng'],('accuracyRng','critRng','critResistanceRng','stunResistanceRng'),'four Character RNGs')
        chars[side]=deepcopy(char['balanced_rng'])
        for rng in chars[side].values():keys(rng,RNG_KEYS,'seven RNG fields')
        for item in char['items']:
            keys(item['chance_rng'],RNG_KEYS,'Item chance RNG');keys(item['damage_rng'],('acc',),'Item range RNG')
            items[item['instance']]=dict(chance=deepcopy(item['chance_rng']),damage=deepcopy(item['damage_rng']))
    return dict(characters=chars,items=items)


def _node(native,name,bound):
    keys(native,NODE_KEYS,'native Node DTO')
    require(name in bound['nodes'],'known business node')
    expected=bound['nodes'][name]
    for field in ('native_id','path','name','class','positions','priority'):
        require(first_difference(native[field],expected[field]) is None,'node identity/topology '+field)
    allowed={name,None}
    if name.startswith('character:'):allowed.add(name[-1])
    if name.startswith('item:'):allowed.add(name[5:])
    require(native['role'] in allowed or role(native['role'])==name,'node role alias')
    for field in FLAGS:require(type(native[field]) is bool,'independent node bool')
    value=deepcopy(native);value['role']=name
    return value


def _native_timer(native,name,bound):
    keys(native,('node',)+TIMER_KEYS,'native Timer DTO')
    require(name in bound['timers'],'one of33 business Timers')
    value={k:decode_native(native[k],bound) for k in TIMER_KEYS}
    require(type(value['process_mode']) is int,'Timer mode INT')
    for field in ('wait_time','time_left'):bits(value[field])
    for field in ('one_shot','autostart','paused','stopped'):require(type(value[field]) is bool,'Timer BOOL')
    value['node']=_node(native['node'],name,bound)
    return value


def _model_timer(public,name,bound):
    value={k:decode_native(v,bound) for k,v in public.items()}
    keys(value,('path','index','ancestor_positions','process_priority','inside_tree',
        'internal_physics','ordinary_physics','internal_idle','ordinary_idle')+TIMER_KEYS,'model Timer component ABI')
    require(value['index']==value['ancestor_positions'][-1],'component node index')
    node=deepcopy(bound['nodes'][name])
    for target,source in (('path','path'),('positions','ancestor_positions'),('priority','process_priority')):
        node[target]=value[source]
    for field in FLAGS:node[field]=value[field]
    timer={k:value[k] for k in TIMER_KEYS};timer['node']=_node(node,name,bound)
    for field in ('wait_time','time_left'):bits(timer[field])
    return timer


def _runtime_rows(rows,bound):
    require(type(rows) is list,'runtime output rows')
    previous=-1
    for row in rows:
        keys(row,('schema','sequence','channel','site','edge','subject','stamp','payload'),'runtime envelope')
        require(row['schema']=='observer7-record/1' and row['channel']=='runtime' and row['site'] in NATIVE_SITES,'native390 runtime Source ABI')
        require(type(row['sequence']) is int and row['sequence']>previous,'runtime original sequence')
        previous=row['sequence']
        keys(row['stamp'],('physics_frame','idle_frame','util_time','combat_time','phase'),'runtime stamp')
        require(decimal(row['stamp']['physics_frame'])>=0 and decimal(row['stamp']['idle_frame'])>=0,'runtime frame counters')
        require(type(row['stamp']['phase']) is str,'runtime Source phase')
        require(type(row['payload']) is dict,'runtime payload')
    return rows


def _subject(row,bound):
    subject=row['subject'];require(type(subject) is dict and subject.get('type')=='native_ref','callback receiver ref')
    require(subject['native_id'] in bound['native'],'callback known receiver')
    decode_native(subject,bound)
    return bound['native'][subject['native_id']]


def _callback_role(row,bound):
    site=row['site']
    direct={'Utility/Util.gd::_physics_process':('util',0),'Utility/Util.gd::_process':('util',1),
        'Interface/CombatTimer/CombatTimer.gd::_physics_process':('combat_timer',0),
        'Interface/CombatTimer/CombatTimer.gd::startFatigue':('fatigue:start',0),
        'Interface/CombatTimer/CombatTimer.gd::dealFatigueDamage':('fatigue:tick',0)}
    if site in direct:
        expected,mode=direct[site]
        owner='combat_timer' if expected.startswith('fatigue:') else expected
        require(_subject(row,bound)==owner,'callback direct receiver')
        return expected,mode,site.endswith(('::_physics_process','::_process'))
    if site in ('Core/Character.gd::_physics_process','Items/Item.gd::_physics_process'):
        receiver=_subject(row,bound)
        require(receiver.startswith('character:' if site.startswith('Core/') else 'item:'),'ordinary receiver class')
        return receiver,0,True
    if site in ('Core/Character.gd::onTick','Core/Character.gd::invulnerabilityEnded'):
        owner=_subject(row,bound);require(owner in ('character:P','character:O'),'Character timeout owner')
        return ('tick:' if site.endswith('onTick') else 'invu:')+owner[-1],0,False
    if site=='Items/Exclusive/KingGoobert.gd::buffEnded':
        require(_subject(row,bound)=='item:P:6','King timeout owner');return 'king_buff:P:6',0,False
    if site=='Core/Buff.gd::onTimeout':
        state=row['payload']['state'];side=decode_native(state['character'],bound);category=decode_native(state['type'],bound)
        require(side in ('P','O') and type(category) is int and category in STACKS,'Buff timeout association')
        return 'buff:'+side+':'+STACKS[category],0,False
    return None


def project_native_callbacks(rows,bundle,bound):
    result=[];header=bundle['runtime']['frame_clock']['checkpoint']
    start=(header['physics_frame'],header['idle_frame'])
    for row in rows:
        if row['sequence']<=ACTIVATION_AFTER_SEQUENCE:continue
        if row['edge']!='enter':continue
        selected=_callback_role(row,bound)
        if selected is None:continue
        p,i=decimal(row['stamp']['physics_frame']),decimal(row['stamp']['idle_frame'])
        require(p>=start[0] and i>=start[1],'callback clock after activation cut')
        # No business callback is part of the activation idle tail. An unexpected
        # selected entry after the exact sequence cut is never silently skipped.
        require((p,i)!=start,'unmodeled same-activation-frame business callback')
        name,mode,ordinary=selected;delta=None
        if ordinary:
            args=decode_native(row['payload']['arguments'],bound);keys(args,('delta',),'callback delta argument')
            delta=bits(args['delta'])
        result.append(dict(role=name,mode=mode,physics_frame=p,idle_frame=i,delta_bits=delta,
            util_time_bits=bits(decode_native(row['stamp']['util_time'],bound)),
            combat_time_bits=bits(decode_native(row['stamp']['combat_time'],bound))))
    return result


def project_model_callbacks(result,bound):
    rows=[]
    noop_slots={('game',0),('game',1)} | {('item:'+identity,1) for identity in bound['items']}
    for row in result['pure_combat_diagnostics']['callbacks']:
        require(row['kind']=='source_callback','model callback kind')
        name=row['role'];mode=row['mode']
        require(type(name) is str and name in bound['nodes'],'model callback bound identity')
        require(type(mode) is int and mode in (0,1),'model callback mode INT0/1')
        if (name,mode) in noop_slots:
            continue  # Exact28-slot Source-only partition; new-case guard required externally, inherited444 rule; no native rows fabricated.
        require(name in bound['nodes'] and (name=='util' or name=='combat_timer' or name.startswith(('character:','item:')) or name in bound['timers']),'unknown model callback')
        rows.append({k:row[k] for k in ('role','mode','physics_frame','idle_frame','delta_bits','util_time_bits','combat_time_bits')})
    return rows


def _api_pairs(rows):
    require(len(rows)%2==0,'Timer paired API edge count')
    for first,second in zip(rows[::2],rows[1::2]):
        require(first['edge']=='before' and second['edge']=='after','Timer before/after edge pair')
        for field in ('role','operation','argc','args','physics_frame','idle_frame'):
            require(first_difference(first[field],second[field]) is None,'Timer API paired '+field)


def project_native_api(rows,bundle,bound):
    result=[];header=bundle['runtime']['frame_clock']['checkpoint']
    for row in rows:
        if row['sequence']<=ACTIVATION_AFTER_SEQUENCE:continue
        if row['edge'] not in ('timer_before','timer_after'):continue
        payload=row['payload'];name=role(payload['role'])
        if name in UI_TIMERS:continue
        require(name in bound['timers'],'unknown/foreign Timer role')
        p,i=decimal(row['stamp']['physics_frame']),decimal(row['stamp']['idle_frame'])
        require(p>=header['physics_frame'] and i>=header['idle_frame'],'Timer API clock after activation cut')
        require(type(payload['argc']) is int and payload['argc'] in (0,1) and type(payload['args']) is list and len(payload['args'])==payload['argc'],'Timer typed argc')
        require(payload['operation'] in ('start','stop') and (payload['operation']!='stop' or payload['argc']==0),'Timer operation')
        args=deepcopy(payload['args'])
        for arg in args:
            require(arg.get('type') in ('int','float'),'original Timer INT/REAL');decode_native(arg,bound)
        expected_int={'Interface/CombatTimer/CombatTimer.gd::start':14,'Interface/CombatTimer/CombatTimer.gd::startFatigue':3,'Interface/CombatTimer/CombatTimer.gd::dealFatigueDamage':1}
        if payload['operation']=='start' and args:
            if row['site'] in expected_int:require(args==[dict(type='int',decimal=str(expected_int[row['site']]))],'Timer native callsite INT')
            else:require(args[0]['type']=='float','Timer native REAL duration')
        edge='before' if row['edge']=='timer_before' else 'after'
        value=payload['public_before' if edge=='before' else 'public_after']
        require(value is not None,'Timer public API state')
        require(_subject(row,bound)==name,'Timer API receiver typed ID/role/class binding')
        result.append(dict(role=name,edge=edge,operation=payload['operation'],argc=payload['argc'],args=args,
            physics_frame=p,idle_frame=i,public=_native_timer(value,name,bound)))
    _api_pairs(result);return result


def project_model_api(result,bound):
    rows=[]
    for row in result['pure_combat_diagnostics']['api']:
        name=row['role'];require(name in bound['timers'],'model Timer33 role')
        require(type(row['argc']) is int and len(row['args'])==row['argc'],'model argc')
        for arg in row['args']:decode_native(arg,bound)
        if row['edge']=='after':
            require(row['native_return_semantics']==dict(typed={'type':'null'},basis='SOURCE_VOID_NOT_SAMPLED'),'Source void separation')
            if row['operation']=='start':
                require(row['helper_status']==dict(ok=True,error=None),'model Timer helper failure')
            else:require(row['helper_status'] is None,'stop helper status')
        rows.append(dict(role=name,edge=row['edge'],operation=row['operation'],argc=row['argc'],args=deepcopy(row['args']),
            physics_frame=row['physics_frame'],idle_frame=row['idle_frame'],public=_model_timer(row['state']['public'],name,bound)))
    _api_pairs(rows);return rows


def _snapshot_native(value,bound):
    timers={}
    for raw_name,timer in value['timers'].items():
        name=role(raw_name)
        if name in UI_TIMERS:continue
        require(name in bound['timers'] and name not in timers,'snapshot Timer identity')
        timers[name]=_native_timer(timer,name,bound)
    require(set(timers)==bound['timers'],'snapshot complete33 Timers')
    chars={}
    for side in ('P','O'):
        item=value['characters_invu'][side]
        chars[side]={k:decode_native(item[k],bound) for k in ('invulnerable','invulnerabilityItem','buffProtectStacks')}
    kings=value['king_source_state'];keys(kings,('P:6',),'one King snapshot')
    king={k:decode_native(kings['P:6']['fields'][k],bound) for k in KING_KEYS}
    root=value['nodes'];require(len(root)==1,'source snapshot root only')
    raw=root[0]['node'] if 'node' in root[0] else root[0]
    return dict(timers=timers,root=_node(raw,'root_viewport',bound),characters=chars,king=king,
        clock=dict(physics_frame=value['physics_frame'],idle_frame=value['idle_frame'],
            util_time_bits=bits(decode_native(value['util_time'],bound)),
            util_clock_time_bits=bits(decode_native(value['util_clockTime'],bound)),
            util_frame_counter=decode_native(value['util_frameCounter'],bound),in_physics=value['is_in_physics_frame']))


def _snapshot_model(driver,bound):
    value=driver['business'];timers={name:_model_timer(t['public'],name,bound) for name,t in value['timers'].items()}
    require(set(timers)==bound['timers'],'model snapshot33')
    chars={s:dict(invulnerable=value['characters'][s]['invulnerable'],invulnerabilityItem=value['invu_origins'][s],
        buffProtectStacks=value['characters'][s]['buff_protect_stacks']) for s in ('P','O')}
    king_rows=[item for c in driver['model']['native_rule_state']['characters'] for item in c['items'] if item['instance']=='P:6']
    require(len(king_rows)==1,'same-cut King state')
    king={k:deepcopy(king_rows[0]['fields'][k]) for k in KING_KEYS}
    node=[n for n in value['processing_nodes'] if n['role']=='root_viewport'];require(len(node)==1,'model root row')
    c=value['clock'];require(value['off_clock'] is False,'runtime cut is on actual clock')
    return dict(timers=timers,root=_node(node[0],'root_viewport',bound),characters=chars,king=king,
        clock=dict(physics_frame=c['physics_frame'],idle_frame=c['idle_frame'],util_time_bits=c['util_time_bits'],
            util_clock_time_bits=c['util_clock_time_bits'],util_frame_counter=c['util_frame_counter'],
            in_physics=c['phase'].startswith('physics_')))


def _terminal_native(native,bundle,cleanup,final,bound):
    endpoint=native['king-capture-endpoint.json'];cut=native['king-collector-cut.json'];receipt=cut['receipt'];terminal=receipt['terminal_cut']
    require(endpoint['schema']=='phase390-first-eligible-idle-endpoint/1' and endpoint['phase']=='idle_pre_internal_flush','native390 endpoint ABI')
    require(endpoint['terminal_policy']=='first-actual-idle-after-at-least-two-future-physics/1' and terminal['terminal_policy']==endpoint['terminal_policy'],'native terminal policy')
    anchor=terminal['cleanup_anchor_pass'];passes=bundle['runtime']['frame_clock']['passes']
    require(endpoint['cleanup_anchor_pass']==anchor and endpoint['minimum_future_physics_signals']==2,'native endpoint anchor and future minimum')
    require(type(anchor) is int and 0<=anchor<len(passes),'cleanup anchor')
    header=bundle['runtime']['frame_clock']['checkpoint'];at=header if anchor==0 else passes[anchor-1]
    require((at['physics_frame'],at['idle_frame'])==(cleanup['clock']['physics_frame'],cleanup['clock']['idle_frame']),'native cleanup clock association')
    future=[(i+1,p) for i,p in enumerate(passes) if i+1>anchor]
    count=0;eligible=None
    for index,row in future:
        if row['kind']=='physics':count+=1
        if row['kind']=='idle' and count>=2:eligible=(index,row,count);break
    require(eligible is not None,'first eligible idle exists')
    index,row,count=eligible
    require(index==len(passes)==endpoint['passes']==terminal['first_eligible_idle_pass']==endpoint['first_eligible_idle_pass'],'first idle exact full finite EOF')
    require(terminal['observed_future_physics_signals']==endpoint['observed_future_physics_signals']==count and terminal['minimum_future_physics_signals']==2,'at least two actual future physics')
    require((row['physics_frame'],row['idle_frame'])==(endpoint['physics_frame'],endpoint['idle_frame'])==(final['clock']['physics_frame'],final['clock']['idle_frame']),'native final counters')
    require(final['clock']['in_physics'] is False,'native idle preinternal final')
    require(first_difference(_snapshot_native(cut['actual_final'],bound),final) is None,'same collector final cut')
    return dict(cleanup_anchor_pass=anchor,passes_consumed=index,physics_frame=row['physics_frame'],idle_frame=row['idle_frame'],future_physics=count)


def _terminal_model(result,bundle):
    driver=result['king_terminal'];cleanup=driver['post_cleanup'];final=driver['final'];passes=bundle['runtime']['frame_clock']['passes'];trace=driver['passes']
    require(len(trace)==len(passes)==final['passes_consumed'],'full model clock exhaustion')
    for index,(record,source) in enumerate(zip(trace,passes)):
        expected=dict(index=index,kind=source['kind'],end_phase='idle_pre_internal_flush' if index==len(passes)-1 else source['kind']+'_tail',completed=index!=len(passes)-1)
        require(first_difference(record,expected) is None,'exact model pass '+str(index))
    require(final['finalized'] is True and final['cleaned'] is True and final['physics_signals_remaining']==0,'model terminal barrier')
    return dict(cleanup_anchor_pass=cleanup['passes_consumed'],passes_consumed=final['passes_consumed'],
        physics_frame=final['physics_frame'],idle_frame=final['idle_frame'],future_physics=final['physics_frame']-cleanup['physics_frame'])


def project_native(native,bundle,root_binding):
    keys(native,EXPECTED_LEAVES,'closed native output leaves')
    bound=bindings(bundle,root_binding);rows=_runtime_rows(native['observer7-runtime.jsonl'],bound)
    final=project_native_final(native['final_state.json'],bound)
    cleanup=_snapshot_native(native['king-post-cleanup-source.json'],bound);last=_snapshot_native(native['king-final-source.json'],bound)
    return dict(events=project_events(native['events.jsonl'],bound),event_references=project_references(native['event_references.json'],bound),
        histories=decode_native(native['histories.json'],bound),
        rng=dict(primitives=deepcopy(bundle['draws']),states=_typed_rng(final['native_rule_state'])),final=final,
        callbacks=project_native_callbacks(rows,bundle,bound),timer_api=project_native_api(rows,bundle,bound),
        cuts=dict(cleanup=cleanup,final=last,terminal=_terminal_native(native,bundle,cleanup,last,bound)))


def project_model(result,bundle,root_binding):
    bound=bindings(bundle,root_binding)
    require(result['observer_version']=='observer7-king-basic-A-captured-candidate471' and result['final']['runtime']['profile']==PROFILE,'joint471 model result')
    require(result['model_source_sha256']==MODEL_SOURCE_HASHES,'exact candidate+component Source hashes')
    require(first_difference(result['fixture'],bundle['fixture']) is None,'model fixture')
    diag=result['pure_combat_diagnostics']
    require(diag['tape_position']==diag['tape_records']==len(bundle['draws']),'complete selected primitive Tape')
    require(len(diag['snapshots'])==3 and [s['stage'] for s in diag['snapshots']]==['constructed_off_clock','prepare_off_clock','pre_activate'],'three initial same-instance stages')
    for snapshot in diag['snapshots'][:2]:require(snapshot['clock'] is None and snapshot['off_clock'] is True,'prepare/constructor off-clock')
    final=project_model_final(result,bound)
    return dict(events=deepcopy(result['events']),event_references=deepcopy(result['event_references']),histories=restore_histories(result['histories']),
        rng=dict(primitives=deepcopy(result['random_inputs']),states=_typed_rng(final['native_rule_state'])),final=final,
        callbacks=project_model_callbacks(result,bound),timer_api=project_model_api(result,bound),
        cuts=dict(cleanup=_snapshot_model(result['king_terminal']['post_cleanup'],bound),
            final=_snapshot_model(result['king_terminal']['final'],bound),terminal=_terminal_model(result,bundle)))


def compare_projected(native,model):
    keys(native,SECTIONS,'native business sections');keys(model,SECTIONS,'model business sections')
    differences={name:first_difference(native[name],model[name],'$.'+name) for name in SECTIONS}
    return dict(schema='phase445-strict-business-output-result/1',status='PASS' if not any(differences.values()) else 'FAIL',
        first_differences=differences,contract_sha256=CONTRACT_SHA256,
        scope='fixed joint26 conditional Tape business events/parents/histories/RNG/final/Timer/callback/clock',
        observation_limits=dict(observer_debug_sites=107,complete_method_enter_return_equality='NOT_CLAIMED',
            noop_slots='28 modeled, inherited finite444 rule requires new-case applicability; no native ordinary entry rows',
            later_private_Timer='MODEL_DIAGNOSTIC_ONLY_NOT_NATIVE_SAMPLED',same_seed_global_generator='NOT_CLAIMED'))


def compare_decoded(native_outputs,sealed_result,accepted_bundle,root_binding):
    """Pure output projection. Independent caller authenticates raw INPUT/output/EXPECTED seals first."""
    return compare_projected(project_native(native_outputs,accepted_bundle,root_binding),project_model(sealed_result,accepted_bundle,root_binding))
