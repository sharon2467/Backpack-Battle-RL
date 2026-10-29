"""Source-initialized75 plus thin single-King combat; no oracle/tape ingress."""
from copy import deepcopy
import argparse
import hashlib
import json
import math
from pathlib import Path

from godot_pcg_integer import GodotPCGInteger, MASK64
from original_rng import OriginalRNG
from native_replay_v8.engine import (
    CATALOG, CombatEngine, NATIVE_PHYSICS_DELTA, STACK_NAMES_BY_TYPE,
    SYNTHETIC_PROFILE, SYNTHETIC_TERMINAL, _float_bits, _required_roles,
    SOURCE_KING_PROFILE, SOURCE_KING_ITEMS, _has_king, validate_source_king_domain,
    source_king_runtime_inputs, source_king_fresh_defaults, source_king_policy,
    source_king_topology, _source_king_equal,
    SOURCE_PURE_PROFILE, source_pure_runtime_inputs, source_pure_business_defaults,
    source_pure_policy, _source_pure_roles,
    validate_fixture, validate_runtime_inputs, _validate_runtime_nodes,
)
from native_replay_v8.randomness import _bits
from native_replay_v8.state import strict_json_loads

ITEMS = frozenset({0, 1, 2, 4, 5, 6, 10, 11, 14, 15, 16, 19, 21, 22, 24, 26, 30, 67, 117, 129, 208, 405, 182, 233, 234, 235, 29, 82, 83, 84, 17, 18, 34, 50, 35, 36, 37, 46, 3, 12, 27, 28, 7, 8, 20, 39, 48, 124, 209, 32, 172, 23, 38, 205, 296, 52, 54, 400, 468, 53, 168, 204, 340, 62, 179, 332, 351, 374, 74, 169, 219, 220, 401, 416, 469})
# Original Bag.getBagLayerPriority: Unique first, then resource Icon/Border.
# Static facts for admitted default resources; no visual object is constructed.
BAG_LAYERS = {11: 0, 26: 1, 67: 2, 129: 2, 405: 1}
ORIGIN = 'source-headless-fresh-prepare-domain-separated-pcg/2'
SEED_POLICY = 'headless-sha256-domains/1'
SEED_PREFIX = b'backpack-battles/headless-sha256-domains/1\0'


def derive_stream_seeds(root_seed):
    """Authorized production seed policy; not native randomize/session reconstruction."""
    if type(root_seed) is not int or not 0 <= root_seed <= MASK64:
        raise ValueError('uint64 headless root seed required')
    encoded = root_seed.to_bytes(8, 'big')
    return tuple(int.from_bytes(hashlib.sha256(SEED_PREFIX + label + encoded).digest()[:8], 'big')
                 for label in (b'global\0', b'util\0'))


def validate_layout(layout):
    """Resolve source defaults and validate the entire closed ingress before RNGs."""
    if type(layout) is not dict or set(layout) != {'schema', 'below_master', 'sides'}:
        raise ValueError('closed headless layout fields required')
    if layout['schema'] != 'headless-layout/1' or type(layout['below_master']) is not bool:
        raise ValueError('headless layout schema and boolean below_master required')
    if type(layout['sides']) is not list or len(layout['sides']) != 2:
        raise ValueError('exactly P and O sides required')
    sides = []
    for side, expected in zip(layout['sides'], ('P', 'O')):
        if type(side) is not dict or not {'side', 'character_class', 'items'} <= set(side) <= {'side', 'character_class', 'items', 'hp', 'stamina'}:
            raise ValueError('closed headless side fields required')
        if side['side'] != expected or type(side['character_class']) is not int or side['character_class'] not in (0, 2):
            raise ValueError('ordered P/O Ranger0 or Berserker2 required')
        if type(side['items']) is not list or not 1 <= len(side['items']) <= 64:
            raise ValueError('one to64 item instances required per side')
        ordinary_seen = False
        bag_seen = False
        for item in side['items']:
            if type(item) is not dict or type(item.get('item_index')) is not int or item['item_index'] not in ITEMS | {262}:
                raise ValueError('item outside75 default headless family')
            if CATALOG[item['item_index']]['bag']:
                if ordinary_seen:
                    raise ValueError('fresh insertion requires bags before ordinary items')
                bag_seen = True
            else:
                ordinary_seen = True
        if not bag_seen:
            raise ValueError('at least one bag required per side')
        sides.append(dict(side=expected, character_class=side['character_class'],
                          hp=side.get('hp', 25), stamina=side.get('stamina', 5),
                          items=deepcopy(side['items'])))
    fixture = dict(schema=1, game_version='1.1.8', mode='Unranked', round=1,
                   below_master=layout['below_master'], rules='default', sides=sides)
    validate_fixture(fixture)
    _validate_king_fresh_domain(fixture)
    return fixture


def _validate_king_fresh_domain(fixture):
    if _has_king(fixture):
        validate_source_king_domain(fixture)


def _fresh_king_facts(fixture):
    return source_king_fresh_defaults(fixture)


def source_sort(items, before):
    """Godot SortArray, reusing the accepted bag-order algorithm with a comparator."""
    result = list(items)

    def adjust_heap(first, hole, length, value):
        top = hole
        child = 2 * hole + 2
        while child < length:
            if before(result[first + child], result[first + child - 1]):
                child -= 1
            result[first + hole] = result[first + child]
            hole = child
            child = 2 * (child + 1)
        if child == length:
            result[first + hole] = result[first + child - 1]
            hole = child - 1
        while hole > top:
            parent = (hole - 1) // 2
            if not before(result[first + parent], value):
                break
            result[first + hole] = result[first + parent]
            hole = parent
        result[first + hole] = value

    def heap_sort(first, last):
        length = last - first
        for parent in range((length - 2) // 2, -1, -1):
            adjust_heap(first, parent, length, result[first + parent])
        while last - first > 1:
            value = result[last - 1]
            result[last - 1] = result[first]
            last -= 1
            adjust_heap(first, 0, last - first, value)

    def intro(first, last, depth):
        while last - first > 16:
            if depth == 0:
                heap_sort(first, last)
                return
            depth -= 1
            a, b, c = result[first], result[first + (last - first) // 2], result[last - 1]
            if before(a, b):
                pivot = b if before(b, c) else (c if before(a, c) else a)
            else:
                pivot = a if before(a, c) else (c if before(b, c) else b)
            left, right = first, last
            while True:
                while before(result[left], pivot):
                    left += 1
                right -= 1
                while before(pivot, result[right]):
                    right -= 1
                if left >= right:
                    break
                result[left], result[right] = result[right], result[left]
                left += 1
            intro(left, last, depth)
            last = left

    if result:
        intro(0, len(result), 2 * (len(result).bit_length() - 1))
        for index in range(1, len(result)):
            value, hole = result[index], index
            while hole > 0 and before(value, result[hole - 1]):
                result[hole] = result[hole - 1]
                hole -= 1
            result[hole] = value
    return result


def _inventory_items(fixture, side):
    entries = fixture['sides'][0 if side == 'P' else 1]['items']
    if side == 'P':
        return list(entries)
    # Same comparator/algorithm as accepted opponent_inventory_order; no ItemState needed.
    return source_sort(entries, lambda a, b: int(CATALOG[a['item_index']]['bag']) > int(CATALOG[b['item_index']]['bag']))


def preparation_order(fixture, global_rng):
    order = []
    for side in ('P', 'O'):
        entries = _inventory_items(fixture, side)
        for index in range(len(entries) - 1, 0, -1):
            other = global_rng.randi() % (index + 1)
            entries[index], entries[other] = entries[other], entries[index]
        entries = source_sort(entries, lambda a, b: CATALOG[a['item_index']].get('priority', 0) > CATALOG[b['item_index']].get('priority', 0))
        order.extend(item['instance_id'] for item in entries)
    return order


def _item_siblings(entries):
    """Bag.addToInventory first-greater-layer move after each fresh item insertion."""
    siblings = []
    for item in entries:
        siblings.append(item)
        if not CATALOG[item['item_index']]['bag']:
            continue
        layer = BAG_LAYERS[item['item_index']]
        insertion = next((i for i, existing in enumerate(siblings)
                          if CATALOG[existing['item_index']]['bag']
                          and BAG_LAYERS[existing['item_index']] > layer), len(siblings))
        old = len(siblings) - 1
        if old < insertion:
            insertion -= 1
        siblings.insert(insertion, siblings.pop(old))
    return siblings


def source_runtime_topology(fixture):
    """Generate fresh combat-relative topology, never accepting captured private phase."""
    _validate_king_fresh_domain(fixture)
    king = _has_king(fixture)
    if king:return source_pure_runtime_topology(fixture)
    roles = _required_roles(fixture)
    nodes = []

    def node(role, path, positions):
        value = dict(role=role, path=path, positions=positions, priority=0, kind=roles[role])
        if roles[role] == 'timer':
            value.update(wait_time_bits=_float_bits(1.0), one_shot=not role.startswith('tick:'))
            if king:value['process_mode'] = 1 if role.startswith(('king_hide:', 'king_drag:')) else 0
        nodes.append(value)

    node('util', '/root/Util', [-1, 0])
    for side in ('O', 'P'):
        parent = '/root/Main/Combat/Opponent' if side == 'O' else '/root/Main/Player'
        pos = [-1, 1, 0, 0] if side == 'O' else [-1, 1, 1]
        node('character:' + side, parent + '/Character', pos + [0])
        node('tick:' + side, parent + '/Character/TickTimer', pos + [0, 3 if king else 5])
        if king:node('invu:' + side, parent + '/Character/InvulnerabilityTimer', pos + [0, 5])
        if 'rage:' + side in roles:
            node('rage:' + side, parent + '/Character/BattleRageTimer', pos + [0, 6])
        for index, category in enumerate(range(100, 111)):
            name = STACK_NAMES_BY_TYPE[category]
            node('buff:' + side + ':' + name, parent + '/Character/Buff' + str(index), pos + [0, 100 + index])
        for index, item in enumerate(_item_siblings(_inventory_items(fixture, side))):
            item_path=parent+'/Item'+str(index)
            item_pos=pos+[index+2]
            node('item:'+item['instance_id'],item_path,item_pos)
            if king and item['item_index'] == 262:
                identity = item['instance_id']
                node('king_buff:' + identity, item_path + '/BuffTimer', item_pos + [7])
                node('king_hide:' + identity, item_path + '/ActivationParticles/Timer', item_pos + [8, 0])
                node('king_drag:' + identity, item_path + '/Icon/SpecificDragParticles/Timer', item_pos + [1, 2, 0])
            if item['item_index'] in (53,168):
                node('particle:'+item['instance_id'],item_path+'/ParticleTimer',item_pos+[9])
                nodes[-1]['process_mode']=0
    timer_path = '/root/Main/Combat/UI/CombatTimer'
    timer_pos = [-1, 1, 0, 1, 0]
    node('combat_timer', timer_path, timer_pos)
    node('fatigue:start', timer_path + '/FatigueStartTimer', timer_pos + [1])
    node('fatigue:tick', timer_path + '/FatigueTickTimer', timer_pos + [2])
    timer_roles = [name for name, kind in roles.items() if kind == 'timer']
    topology=dict(nodes=nodes,timer_lineage={r:'fresh_configured' for r in timer_roles})
    _validate_runtime_nodes(topology,fixture,king)
    if king and not _source_king_equal(topology, source_king_topology(fixture)):
        raise ValueError('independent SOURCE King topology mismatch before RNG')
    return topology


def runtime_inputs(fixture, order, topology=None):
    topology=source_runtime_topology(fixture) if topology is None else deepcopy(topology)
    if _has_king(fixture):
        _validate_king_fresh_domain(fixture)
        return source_pure_runtime_inputs(fixture, order, topology)
    _validate_runtime_nodes(topology,fixture)
    initial_items = {item['instance_id']: dict(lastActivationTime_bits=_float_bits(0.0),
                     activationsThisFrame=0, lastTriggerTime_bits=_float_bits(0.0), triggersThisFrame=0,
                     dragged=False, moveback_running=False, cache_fresh=True)
                     for side in fixture['sides'] for item in side['items']}
    # Legacy DTO discriminants are an internal carrier, not public origin evidence.
    carrier = dict(schema='native-v8-runtime-input/1', mode='synthetic', profile_id=SYNTHETIC_PROFILE,
                   checkpoint=dict(util_time_bits=_float_bits(0.0), combat_time_bits=_float_bits(0.0),
                                   source_phase='synthetic-before-activate'),
                   environment=dict(fps=60, scale=1.0, paused=False, no_pending_gameplay_transform=True),
                   nodes=topology['nodes'], timer_lineage=topology['timer_lineage'],
                   initial_items=initial_items, prepare_order=list(order), activate_order=list(order),
                   terminal_profile=SYNTHETIC_TERMINAL)
    return validate_runtime_inputs(carrier, fixture)


class CombatRandom:
    alignment = ORIGIN

    def __init__(self, seed, *, global_state=None, global_contexts=()):
        global_seed, combat_seed = derive_stream_seeds(seed)
        if global_state is not None and (type(global_state) is not int or not 0 <= global_state <= MASK64):
            raise ValueError('uint64 private global state required')
        if (type(global_contexts) is not tuple or any(type(c) is not str or not c.startswith('fraction_shuffle:') or not c.endswith(':multiply') for c in global_contexts)
                or len(set(global_contexts)) != len(global_contexts)):
            raise ValueError('unique SOURCE Mirror contexts required')
        self._generator = OriginalRNG(combat_seed)
        self._global_generator = GodotPCGInteger(global_seed)
        if global_state is not None:
            self._global_generator.set_state(global_state)
        self._global_contexts = frozenset(global_contexts)
        self.audit = []

    @staticmethod
    def _label(label):
        if type(label) is not str or not label:
            raise ValueError('nonempty combat primitive label required')

    def randf(self, label):
        self._label(label)
        value = self._generator.randf()
        self.audit.append(dict(kind='randf', label=label, args=[], value_bits=_bits(value)))
        return value

    def randf_range(self, label, low, high):
        self._label(label)
        value = self._generator.randf_range(low, high)
        self.audit.append(dict(kind='randf_range', label=label, args=[_bits(low), _bits(high)], value_bits=_bits(value)))
        return value

    def randi_range(self, label, low, high):
        self._label(label)
        value = self._generator.randi_range(low, high)
        self.audit.append(dict(kind='randi_range', label=label, args=[low, high], value=value))
        return value

    def global_u32(self, label, context, ordinal, width):
        if (type(label) is not str or type(context) is not str or context not in self._global_contexts
                or type(ordinal) is not int or not 0 <= ordinal <= 5
                or type(width) is not int or width != 7 - ordinal
                or label != f'{context}:{ordinal}:{width}'):
            raise ValueError('exact SOURCE Mirror global primitive required')
        value = self._global_generator.randi()
        self.audit.append(dict(kind='global_u32', label=label, args=[], value=value,
                               context=context, ordinal=ordinal, width=width))
        return value

    def snapshot(self):
        return dict(schema='source-headless-two-stream-state/1',util=self._generator.snapshot(),
            global_rng=dict(state=self._global_generator.get_state(),current_seed=self._global_generator.get_seed(),
                            increment=self._global_generator._increment),audit_length=len(self.audit),
            seed_policy=SEED_POLICY,native_seed_parity='PENDING_CUSTOM_BINARY_NUMERIC_AND_SESSION_CONSUMPTION')


class HeadlessBattle:
    def __init__(self, engine, descriptor):
        self._engine = engine
        self._initialization = deepcopy(descriptor)

    @property
    def initialization(self):
        return deepcopy(self._initialization)

    @property
    def done(self):
        return self._engine.frame_driver.finalized if self._engine.king_mode else self._engine.finalized

    def step(self):
        if self._engine.source_king_mode:
            return self._engine._source_king_quantum()
        self._engine.step()

    def snapshot(self):
        value = self._engine.snapshot()
        # Public metadata describes the source-generated origin, not the legacy DTO.
        value['runtime'].update(mode='source_headless', profile=SOURCE_PURE_PROFILE if self._engine.source_pure_mode else SOURCE_KING_PROFILE if self._engine.source_king_mode else ORIGIN)
        if self._engine.source_pure_mode:
            value=_source_pure_snapshot_view(value)
            value['source_rng']=self._engine.random.snapshot()
        return value

    def run(self, max_seconds=120.0):
        if type(max_seconds) not in (float, int) or not math.isfinite(max_seconds) or max_seconds <= 0:
            raise ValueError('positive finite battle budget required')
        result = self._engine.run(float(max_seconds))
        return self._result_view(result)

    def result(self):
        if not self.done:raise ValueError('result requires completed battle; use step or run')
        return self._result_view(self._engine.result())

    def _result_view(self,result):
        value = dict(schema='headless-battle-result/1', initialization=self.initialization,
                    fixture=result['fixture'], events=result['events'], event_references=result['event_references'],
                    histories=result['histories'], final=self.snapshot(), random_inputs=result['random_inputs'],
                    scheduling=dict(preparation_order=result['scheduling']['preparation_order'],
                                    ordinary_order=list(self._engine.ordinary_roles), frames=self._engine.frame,
                                    elapsed=self._engine.elapsed, delta_bits=_float_bits(NATIVE_PHYSICS_DELTA)),
                    coverage=dict(items=sorted(ITEMS), classes=[0, 2],
                                  status='source_initialized_not_per_layout_native_validation',
                                  remaining=['other_items_classes', 'modifiers_gems_custom_rules',
                                             'Game_session_reconstruction', 'whole_engine_RL']))
        if self._engine.source_king_mode:
            value['coverage'].update(items=sorted(SOURCE_KING_ITEMS), classes=[0],
                status='source_single_King_six_ID_domain_not_native_validated',
                domains=dict(non_King_default75=sorted(ITEMS),
                             King=dict(items=sorted(SOURCE_KING_ITEMS), classes=[0], global_max_King=1)),
                remaining=['two_King', 'King_plus75_mixed', 'King_rage', 'gems', 'native_King', 'whole_engine_RL'])
            value['scheduling']['source_clock'] = dict(policy=source_king_policy(),
                passes_consumed=self._engine.frame_driver.pass_index,
                physics_frame=self._engine.frame_driver.physics_frame,
                idle_frame=self._engine.frame_driver.idle_frame)
        if self._engine.source_pure_mode:
            value['coverage'].update(status='SOURCE_PURE_SIX_ID_SINGLE_KING_NOT_NATIVE_SEED_VALIDATED',formal_support=75,
                native_seed_parity='PENDING_CUSTOM_BINARY_NUMERIC_AND_SESSION_CONSUMPTION',
                evidence='Fixed441 conditionalTape equality only; this layout and seed have no native comparison',
                remaining=['King_plus75','two_King','King_rage','gems','custom_native_seed_parity','full_engine_RL_action_environment'])
            value['scheduling']['source_clock']['policy']=source_pure_policy()
            value['source_rng']=self._engine.random.snapshot()
            terminal=deepcopy(result['king_terminal'])
            for stage in ('post_cleanup','final'):terminal[stage]['model']=_source_pure_snapshot_view(terminal[stage]['model'])
            value['source_terminal']=terminal
            value['source_timer_api']=deepcopy(self._engine.pure_api_trace)
        return value


def initialize(layout, seed):
    if type(seed) is not int or not 0 <= seed <= MASK64:
        raise ValueError('uint64 headless seed required')
    fixture = validate_layout(layout)
    topology = source_runtime_topology(fixture)
    if _has_king(fixture):source_pure_business_defaults(fixture)
    else:_validate_runtime_nodes(topology,fixture)
    global_contexts = tuple(f"fraction_shuffle:{item['instance_id']}:{side['side']}:multiply"
                            for side in fixture['sides'] for item in side['items'] if item['item_index'] == 332)
    global_seed, combat_seed = derive_stream_seeds(seed)
    global_rng = GodotPCGInteger(global_seed)
    order = preparation_order(fixture, global_rng)
    runtime = runtime_inputs(fixture, order, topology)
    engine = CombatEngine(fixture, CombatRandom(seed, global_state=global_rng.get_state(), global_contexts=global_contexts), runtime)
    engine.prepare_only()
    engine.activate_from_checkpoint()
    descriptor = dict(origin=ORIGIN, seed=seed, root_seed=seed, seed_policy=SEED_POLICY,
                      global_seed=global_seed, combat_seed=combat_seed,
                      util_time_origin=0.0, combat_time_origin=0.0,
                      preparation_order=order, ordinary_order=list(engine.ordinary_roles))
    if engine.source_king_mode:
        descriptor.update(source_clock=source_pure_policy() if engine.source_pure_mode else source_king_policy(),
            domain=dict(items=sorted(SOURCE_KING_ITEMS), classes=[0], global_max_King=1),
            clock_time_origin=0.0, physics_frame_origin=0, idle_frame_origin=0, util_frame_counter_origin=0)
    if engine.source_pure_mode:
        descriptor.update(profile=SOURCE_PURE_PROFILE,initialization_origin='FRESH_MODEL_OBJECTS_SOURCE_FACTORY',
            native_seed_parity='PENDING_CUSTOM_BINARY_NUMERIC_AND_SESSION_CONSUMPTION',formal_support=75)
    return HeadlessBattle(engine, descriptor)


def source_pure_runtime_topology(fixture):
    _validate_king_fresh_domain(fixture)
    roles=_source_pure_roles(fixture);nodes=[]
    def add(name,path,positions):nodes.append(dict(role=name,path=path,positions=positions,priority=0,kind=roles[name]))
    add('util','/root/Util',[-1,0])
    for side in ('O','P'):
        parent='/root/Main/Combat/Opponent' if side=='O' else '/root/Main/Player'
        pos=[-1,1,0,0] if side=='O' else [-1,1,1]
        add('character:'+side,parent+'/Character',pos+[0])
        add('tick:'+side,parent+'/Character/TickTimer',pos+[0,3])
        add('invu:'+side,parent+'/Character/InvulnerabilityTimer',pos+[0,7 if side=='P' else 5])
        for name,child in [('battleRageTimer',6 if side=='P' else 4),('autoRageTimer',8 if side=='P' else 6)]:
            add('aux:'+side+':'+name,parent+'/Character/'+name,pos+[0,child])
        for index,category in enumerate(range(100,111)):
            add('buff:'+side+':'+STACK_NAMES_BY_TYPE[category],parent+'/Character/Buff'+str(index),pos+[0,100+index])
        for index,item in enumerate(_item_siblings(_inventory_items(fixture,side))):
            path=parent+'/Item'+str(index);position=pos+[index+2]
            add('item:'+item['instance_id'],path,position)
            if item['item_index']==262:add('king_buff:'+item['instance_id'],path+'/BuffTimer',position+[7])
    path='/root/Main/Combat/UI/CombatTimer';position=[-1,1,0,1,0]
    add('combat_timer',path,position)
    add('fatigue:start',path+'/FatigueStartTimer',position+[1])
    add('fatigue:tick',path+'/FatigueTickTimer',position+[2])
    timers={name:dict(wait_time_bits=_float_bits(1.0),one_shot=not name.startswith('tick:'),process_mode=0,
                autostart=False,paused=False,private_left_bits=_float_bits(-1.0)) for name,kind in roles.items() if kind=='timer'}
    return dict(nodes=nodes,timer_initial=timers)


def _source_pure_snapshot_view(snapshot):
    value=deepcopy(snapshot)
    value['runtime'].pop('invu_bubbles',None)
    for char in value['native_rule_state']['characters']:char['fields'].pop('invulBubbleVisible',None)
    return value


def run_batch(jobs,max_seconds=120.0,keep_results=False):
    if type(jobs) is not list or not 1<=len(jobs)<=64:raise ValueError('one to64 ordered batch jobs required')
    if type(max_seconds) not in (int,float) or not math.isfinite(max_seconds) or not 0<max_seconds<=120:
        raise ValueError('batch positive finite budget <=120 required')
    if type(keep_results) is not bool:raise ValueError('batch keep_results BOOL required')
    # Complete cheap validation of every job before any RNG/Engine is constructed.
    for job in jobs:
        if type(job) is not dict or set(job)!={'layout','seed'}:raise ValueError('closed batch job fields')
        if type(job['seed']) is not int or not 0<=job['seed']<=MASK64:raise ValueError('batch uint64 seed required')
        fixture=validate_layout(job['layout'])
        source_runtime_topology(fixture)
    records=[]
    for index,job in enumerate(jobs):
        battle=initialize(job['layout'],job['seed'])
        try:
            result=battle.run(float(max_seconds))
        except TimeoutError as error:
            records.append(dict(index=index,seed=job['seed'],status='TIME_BUDGET',message=str(error),
                elapsed=battle._engine.elapsed,frames=battle._engine.frame,scope=battle.initialization))
        else:
            record=dict(index=index,seed=job['seed'],status='COMPLETED',summary=dict(winner=result['final']['winner'],
                terminal_time=result['final']['timestamp'],frames=result['scheduling']['frames'],coverage=deepcopy(result['coverage'])))
            if keep_results:record['result']=result
            records.append(record)
        del battle
    return dict(schema='headless-batch-result/1',jobs=records,seed_policy=SEED_POLICY,formal_support=75,
        source_king_domain='experimental sixID singleKing class0; native numeric/seed parity pending')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--layout', type=Path)
    parser.add_argument('--seed', type=int)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--max-seconds', type=float, default=120.0)
    parser.add_argument('--batch', type=Path)
    parser.add_argument('--keep-results', action='store_true')
    args = parser.parse_args()
    if args.batch is not None:
        if args.layout is not None or args.seed is not None:parser.error('--batch excludes --layout/--seed')
        result=run_batch(strict_json_loads(args.batch.read_text()),args.max_seconds,args.keep_results)
    else:
        if args.layout is None or args.seed is None:parser.error('--layout and --seed required without --batch')
        result = initialize(strict_json_loads(args.layout.read_text()), args.seed).run(args.max_seconds)
    args.output.write_text(json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + '\n')


if __name__ == '__main__':
    main()
