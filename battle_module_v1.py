from __future__ import annotations
import math
import random
import struct
from dataclasses import asdict, dataclass, field, replace
from typing import TYPE_CHECKING, Sequence

if TYPE_CHECKING:
    from item_factory_registry_v1 import BattleItem

ATTACK_PHASE_PRE_DEAL_DAMAGE_EARLY = "pre_deal_damage_early"
ATTACK_PHASE_PRE_TAKE_DAMAGE = "pre_take_damage"
ATTACK_PHASE_PRE_DEAL_DAMAGE_LATE = "pre_deal_damage_late"
ATTACK_PHASE_PRE_TAKE_DAMAGE_LATE = "pre_take_damage_late"
ATTACK_PHASE_CHARACTER_ATTACKED = "character_attacked"
ATTACK_PHASE_CHARACTER_DAMAGED = "character_damaged"
ATTACK_PHASE_ATTACKED = "attacked"
ITEM_MARKER_TYPES = ("star", "diamond", "triangle")
SUPPORTED_ATTACK_REACTION_PHASES = (
    ATTACK_PHASE_PRE_DEAL_DAMAGE_EARLY,
    ATTACK_PHASE_PRE_TAKE_DAMAGE,
    ATTACK_PHASE_PRE_DEAL_DAMAGE_LATE,
    ATTACK_PHASE_PRE_TAKE_DAMAGE_LATE,
    ATTACK_PHASE_CHARACTER_ATTACKED,
    ATTACK_PHASE_CHARACTER_DAMAGED,
    ATTACK_PHASE_ATTACKED,
)
NIGHTFALL_FATIGUE_START_TIME = 17.0
NIGHTFALL_FATIGUE_INTERVAL = 1.0
_STACK_TIMER_ORDER = (
    "Block", "Luck", "Regeneration", "Vampirism", "Spikes", "Mana",
    "Empower", "Heat", "Poison", "Blind", "Cold",
)
DEFAULT_ATTACK_FLAGS = {
    name: dict(zip(
        ("can_be_blocked", "can_be_spiked", "can_be_vampiric",
         "can_activate_item", "can_miss", "can_crit"), values,
    ))
    for name, values in {
        "melee": (True, True, True, True, True, True),
        "ranged": (True, True, True, True, True, True),
        "effect": (True, False, False, True, False, True),
        "self_damage": (True, False, False, True, False, False),
        "unhealing": (True, False, False, True, False, False),
        "spikes": (True, False, False, False, False, True),
        "poison": (True, False, False, False, False, True),
        "fatigue": (True, False, False, False, False, False),
    }.items()
}


def godot_round(value: float) -> int:
    return math.floor(value + 0.5) if value >= 0 else math.ceil(value - 0.5)

def calculate_next_fatigue_damage(
    previous: int,
    *,
    nightfall: bool,
)->int:
    if type(previous) is not int or previous < 0:
        raise ValueError("previous fatigue damage must be a non-negative int")
    if type(nightfall) is not bool:
        raise ValueError("nightfall must be a bool")
    if nightfall:
        return previous + previous // 10 + 1
    return previous + 1




@dataclass
class BuffSlot:
    Empower: int = 0
    Heat: int = 0
    Luck: int = 0
    Mana: int = 0
    Regeneration: int = 0
    Spikes: int = 0
    Vampirism: int = 0
@dataclass
class DebuffSlot:
    Poison: int = 0
    Blind: int = 0
    Cold: int = 0


@dataclass
class PhysicsTimerState:
    wait_time: float = 1.0
    time_left: float = -1.0
    processing: bool = False


def _godot_float32(value: float) -> float:
    return struct.unpack("<f", struct.pack("<f", float(value)))[0]


def _start_timer(timer: PhysicsTimerState, duration: float) -> None:
    duration = _godot_float32(duration)
    if duration > 0:
        timer.wait_time = duration
    timer.time_left = timer.wait_time
    timer.processing = True


def _stop_timer(timer: PhysicsTimerState) -> None:
    timer.time_left = -1.0
    timer.processing = False


def _timer_time_left(timer: PhysicsTimerState) -> float:
    return _godot_float32(max(timer.time_left, 0.0))


def _advance_timer(
    timer: PhysicsTimerState, delta: float, *, one_shot: bool,
) -> bool:
    if not timer.processing:
        return False
    timer.time_left -= _godot_float32(delta)
    if timer.time_left < 0:
        if one_shot:
            _stop_timer(timer)
        else:
            timer.time_left += timer.wait_time
        return True
    return False


@dataclass(eq=False)
class TemporaryStackBatch:
    amount: int
    expires_at: float
    source_item: BattleItem | None = None


@dataclass
class StackState:
    resist_chance_percent: float = 0.0
    resist_stacks: int = 0
    reflect_chance_percent: float = 0.0
    cleanse_protection_chance_percent: float = 0.0
    permanent_stacks: int = field(default=0, init=False)
    temporary_stacks: list[TemporaryStackBatch] = field(
        default_factory=list, init=False,
    )
    next_temporary_index: int = field(default=0, init=False)
    timer: PhysicsTimerState = field(
        default_factory=PhysicsTimerState, init=False,
    )


@dataclass
class BalancedRngState:
    expected_wins: float = 0.0
    wins: int = 0
    last_result: bool = False
    last_roll: float | None = None

    def reset(self) -> None:
        self.expected_wins = 0.0
        self.wins = 0
        self.last_result = False
        self.last_roll = None

    def roll_percent(self, percent: float, rng) -> bool:
        self.last_roll = None
        target = percent / 100.0
        if target <= 0:
            return False
        if target >= 1:
            return True
        chance = target
        difference = self.expected_wins - self.wins
        if difference > 0.3:
            chance *= 3.0 * min(1.0, difference)
        elif difference < -0.3:
            chance /= 3.0 * min(1.0, -difference)
        self.expected_wins += target
        if self.last_result and target < 0.4:
            chance *= 0.5
        elif not self.last_result and target > 0.6:
            chance *= 2.0
        self.last_roll = rng.random()
        self.last_result = self.last_roll <= chance
        if self.last_result:
            self.wins += 1
        return self.last_result


@dataclass
class PlayerState:
    player_id: str|None = None
    health: int = 0
    max_health: int = 0
    block: int = 0
    fatigue_damage: int = 0
    stamina: float = 0.0
    max_stamina: float = 0.0
    buffs: BuffSlot = field(default_factory=BuffSlot)
    debuffs: DebuffSlot = field(default_factory=DebuffSlot)
    items: dict[str,BattleItem] = field(default_factory=dict)

    is_dead: bool = False
    damage_resistance: float = 0.0
    damage_reduction: int = 0
    invulnerable: bool = False
    dodge_stacks: int = 0
    crit_tokens: int = 0
    crit_resistance: float = 0.0
    crit_resist_stacks: int = 0
    bonus_fatigue_damage: int = 0
    healing_efficiency: float = 1.0
    unhealing_amount: float = 0.0
    empower_damage: float = 1.0
    typed_damage_factors: dict[str, float] = field(default_factory=lambda: {
        "melee": 0.0,
        "ranged": 0.0,
        "effect": 0.0,
        "self_damage": 0.0,
        "unhealing": 0.0,
        "spikes": 0.0,
        "poison": 0.0,
        "fatigue": 0.0,
    })
    melee_spikes_limit: float = 1.0
    ranged_spikes_limit: float = 0.0
    effect_spikes_limit: float = 0.0
    melee_vampirism_limit: float = 1.0
    ranged_vampirism_limit: float = 0.0
    accuracy_rng: BalancedRngState = field(default_factory=BalancedRngState)
    crit_rng: BalancedRngState = field(default_factory=BalancedRngState)
    crit_resistance_rng: BalancedRngState = field(default_factory=BalancedRngState)
    stack_states: dict[str, StackState] = field(default_factory=dict)
    debuff_resist_stacks: int = 0
    debuff_reflect_stacks: int = 0
    buff_protect_stacks: int = 0
    status_tick_timer: PhysicsTimerState = field(
        default_factory=PhysicsTimerState, init=False,
    )
    status_tick_counter: int = field(default=0, init=False)

    def __post_init__(self) -> None:
        for name in _STACK_TIMER_ORDER:
            if name not in self.stack_states:
                self.stack_states[name] = StackState()
            if name == "Block":
                current = self.block
            elif name in BuffSlot.__annotations__:
                current = getattr(self.buffs, name)
            else:
                current = getattr(self.debuffs, name)
            self.stack_states[name].permanent_stacks = current

    def __setattr__(self, name, value):
        if (
            name == "health"
            and "health" in self.__dict__
            and value < self.__dict__["health"]
        ):
            raise ValueError(
                "health reductions must use "
                "BattleState.commit_health_reduction"
            )
        super().__setattr__(name, value)


def serialize_player_state(player: PlayerState) -> dict[str, object]:
    return {
        "player_id": player.player_id,
        "health": player.health,
        "max_health": player.max_health,
        "block": player.block,
        "fatigue_damage": player.fatigue_damage,
        "stamina": player.stamina,
        "max_stamina": player.max_stamina,
        "buffs": asdict(player.buffs),
        "debuffs": asdict(player.debuffs),
    }


@dataclass
class AttackEvent:
    attacker: PlayerState
    defender: PlayerState
    source_item: BattleItem|None
    attack_types: tuple[str, ...]

    min_damage: int
    max_damage: int

    accuracy: float
    hit: bool | None = None

    can_be_blocked: bool = True
    can_be_spiked: bool = True
    can_be_vampiric: bool = True
    can_activate_item:bool = True
    can_miss: bool = True

    can_crit: bool = True
    crit_chance: float = 0.0
    crit_multiplier: float = 2.0
    crit: bool=False

    rolled_damage: int = 0
    pending_damage: int = 0
    prevented_damage: int = 0
    block_damage: int = 0
    health_damage: int = 0
    is_resolved: bool = False

    log_handle: LogHandle | None = None
    trigger_log_handle: LogHandle | None = None


def make_attack_event(
    *, attacker, defender, source_item, attack_types, min_damage, max_damage,
    accuracy=100.0, flag_overrides=None, trigger_log_handle=None,
) -> AttackEvent:
    if not attack_types or any(t not in DEFAULT_ATTACK_FLAGS for t in attack_types):
        raise ValueError("unsupported attack types")
    # Match DamageSource.setItem's precedence for combined types.
    primary = next((t for t in ("melee", "ranged", "self_damage")
                    if t in attack_types), attack_types[0])
    flags = DEFAULT_ATTACK_FLAGS[primary].copy()
    if flag_overrides:
        if any(k not in flags or type(v) is not bool for k, v in flag_overrides.items()):
            raise ValueError("invalid attack flag override")
        flags.update(flag_overrides)
    return AttackEvent(
        attacker=attacker, defender=defender, source_item=source_item,
        attack_types=tuple(attack_types), min_damage=min_damage,
        max_damage=max_damage, accuracy=accuracy,
        trigger_log_handle=trigger_log_handle, **flags,
    )


def validate_gem_sockets(players: Sequence[PlayerState]) -> None:
    """Check socket relationships without changing items or battle state."""
    for player in players:
        seen_instances = set()
        socketed_keys = set()
        for key, item in player.items.items():
            if not key or key != item.item_key or item.player_id != player.player_id:
                raise ValueError("item key or player does not match its registration")
            if id(item) in seen_instances:
                raise ValueError("item instance is registered more than once")
            seen_instances.add(id(item))
            if len(item.gemsocket) != item.socket_count:
                raise ValueError("gem socket count does not match slot storage")
            if "Gem" in item.item_types and item.socket_count != 0:
                raise ValueError("gems cannot have sockets")
            for gem_key in item.gemsocket:
                if gem_key is None:
                    continue
                if "Gem" in item.item_types:
                    raise ValueError("a gem cannot host another gem")
                if gem_key not in player.items:
                    raise ValueError("socketed gem is missing from player items")
                gem = player.items[gem_key]
                if "Gem" not in gem.item_types:
                    raise ValueError("socketed item must be a gem")
                if gem.belongs_to != key or gem.gem_type != item.item_types:
                    raise ValueError("gem binding does not match its host")
                if gem_key in socketed_keys:
                    raise ValueError("gem is referenced by more than one socket")
                socketed_keys.add(gem_key)
        for key, item in player.items.items():
            if item.belongs_to is not None:
                if "Gem" not in item.item_types or key not in socketed_keys:
                    raise ValueError("item binding has no matching gem socket")


class _BattleFinishedSignal(Exception):
    pass


@dataclass(frozen=True, eq=False)
class LogHandle:
    battle_state: BattleState = field(repr=False)
    sequence: int


@dataclass
class StackResult:
    delta: int
    event: StackChangeContext | None


@dataclass
class BattleState:
    frame: int = 0
    time: float = 0.0
    players: list[PlayerState] = field(default_factory=list)
    active_items: list[BattleItem] = field(default_factory=list)
    battle_items: list[BattleItem] = field(default_factory=list, init=False)
    winner: object = None
    frame_delta: float = 1.0 / 60.0
    rng: random.Random = field(default_factory=random.Random)
    log: list[dict[str, object]] = field(default_factory=list)
    collect_player_state_history: bool = False
    player_state_history: list[dict[str, object]] = field(
        default_factory=list,
    )
    _bus_cache: dict[tuple[object, str], list[tuple[BattleItem,int]]] = field(default_factory=dict, init=False, repr=False)
    has_prepared: bool = field(default=False, init=False)
    combat_started: bool = field(default=False, init=False)
    signals_delayed: bool = field(default=False, init=False)
    _pending_signals: list[tuple] = field(
        default_factory=list, init=False, repr=False,
    )
    fatigue_start_timer: PhysicsTimerState = field(
        default_factory=PhysicsTimerState, init=False,
    )
    fatigue_tick_timer: PhysicsTimerState = field(
        default_factory=PhysicsTimerState, init=False,
    )

    def prepareItems(self) -> None:
        if self.has_prepared or self.combat_started:
            raise ValueError("battle has already been prepared or started")
        if self.time != 0.0 or self.frame != 0 or self.winner is not None:
            raise ValueError("battle time and frame must be zero before preparation")
        if len(self.players) != 2 or self.players[0].player_id == self.players[1].player_id:
            raise ValueError("battle preparation requires two distinct players")
        items = [item for player in self.players for item in player.items.values()]
        if any(item.has_prepared for item in items):
            raise ValueError("item has already been prepared")
        for player in self.players:
            player_items = [item for item in player.items.values() if item.belongs_to is None]
            self.rng.shuffle(player_items)
            player_items.sort(key=lambda item: item.getTriggerPriority(), reverse=True)
            self.battle_items.extend(player_items)
            player.accuracy_rng.reset()
            player.crit_rng.reset()
            player.crit_resistance_rng.reset()
        self.active_items = [item for item in self.active_items if item.belongs_to is None]
        for item in self.battle_items:
            item.prepare(self.build_context(item))
        self.has_prepared = True

    def start_combat(self) -> None:
        if self.combat_started:
            return
        if not self.has_prepared:
            raise ValueError("battle must be prepared before starting combat")
        self.combat_started = True
        self.emit_signal(None, "combat_start")
        if self.winner is not None:
            return
        _start_timer(self.fatigue_start_timer, NIGHTFALL_FATIGUE_START_TIME - 3.0)
        _stop_timer(self.fatigue_tick_timer)
        for player in self.players:
            player.status_tick_counter = 0
            _start_timer(player.status_tick_timer, 1.0)
        for phase in ("preCombatStart", "combatStart", "postCombatStart"):
            for item in self.battle_items:
                getattr(item, phase)(self.build_context(item))
                if self.winner is not None:
                    return

    def emit_signal(
        self,
        emitter: BattleItem | PlayerState | None,
        signalName: str,
        event_context: BattleContext | None = None,
    ) -> None:
        if event_context is not None and event_context.battle_state is not self:
            raise ValueError("event context belongs to another battle")
        if self.winner is not None:
            return
        if self.signals_delayed:
            self._pending_signals.append((emitter, signalName, event_context))
            return
        self._emit_signal_now(emitter, signalName, event_context)

    def _emit_signal_now(
        self,
        emitter: BattleItem | PlayerState | None,
        signalName: str,
        event_context: BattleContext | None = None,
    ) -> None:
        if event_context is not None and event_context.battle_state is not self:
            raise ValueError("event context belongs to another battle")
        if hasattr(emitter, "item_key"):
            emitter_key = ("item",emitter.player_id,emitter.item_key)
        elif hasattr(emitter, "player_id"):
            emitter_key = ("player",emitter.player_id)
        elif emitter is None:
            emitter_key = "environment"
        if (emitter_key, signalName) in self._bus_cache:
            for listener in self._bus_cache[(emitter_key, signalName)]:
                if self.winner is not None:
                    return
                listener_item,listener_idx = listener
                context = (
                    event_context.for_item(listener_item)
                    if event_context is not None
                    else self.build_context(listener_item)
                )
                listener_item.activate_item(context,listener_idx)

    def set_signals_delayed(self, delayed: bool) -> None:
        if type(delayed) is not bool:
            raise ValueError("signals_delayed must be a bool")
        self.signals_delayed = delayed

    def flush_signals(self) -> None:
        self.signals_delayed = False
        pending = self._pending_signals.copy()
        self._pending_signals.clear()
        try:
            for emitter, signal_name, context in pending:
                if self.winner is not None:
                    self._pending_signals.clear()
                    return
                self._emit_signal_now(emitter, signal_name, context)
        except _BattleFinishedSignal:
            self._pending_signals.clear()
            raise
        if self.winner is not None:
            self._pending_signals.clear()

    def connect(self, emitter, signalName, listener:tuple[BattleItem,int]):
        if hasattr(emitter, "item_key"):
            emitter_key = ("item",emitter.player_id,emitter.item_key)
        elif hasattr(emitter, "player_id"):
            emitter_key = ("player",emitter.player_id)
        elif emitter is None:
            emitter_key = "environment"
        if (emitter_key, signalName) not in self._bus_cache:
            self._bus_cache[(emitter_key, signalName)] = []
        self._bus_cache[(emitter_key, signalName)].append(listener)

    def record_log(
        self,
        source: object,
        data: dict[str, object],
    ) -> LogHandle:
        if type(source) is str:
            serialized_source = {
                "type": "system",
                "name": source,
            }
        else:
            serialized_source = {
                "type": "item",
                "player_id": getattr(source, "player_id", None),
                "item_key": getattr(source, "item_key", None),
                "item_id": getattr(source, "item_id", None),
            }

        sequence = len(self.log)
        self.log.append(
            {
                "sequence": sequence,
                "frame": self.frame,
                "time": round(self.time, 3),
                "source": serialized_source,
                "data": dict(data),
            }
        )
        return LogHandle(self, sequence)

    def _stack_slot(
        self, target: PlayerState, stack_name: str,
    ) -> tuple[BuffSlot | DebuffSlot | PlayerState, str]:
        if (
            not isinstance(target, PlayerState)
            or self.get_player(target.player_id) is not target
        ):
            raise ValueError("stack target is not part of this battle")
        if type(stack_name) is not str:
            raise ValueError("unsupported stack name")
        if stack_name in BuffSlot.__annotations__:
            return target.buffs, stack_name
        if stack_name in DebuffSlot.__annotations__:
            return target.debuffs, stack_name
        if stack_name == "Block":
            return target, "block"
        raise ValueError("unsupported stack name")

    def _stack_state(self, target: PlayerState, stack_name: str) -> StackState:
        slot, attribute = self._stack_slot(target, stack_name)
        if stack_name not in target.stack_states:
            state = StackState()
            state.permanent_stacks = getattr(slot, attribute)
            target.stack_states[stack_name] = state
        return target.stack_states[stack_name]

    def _commit_stack_delta(
        self, target: PlayerState, stack_name: str, delta: int, *,
        source_item: BattleItem | None = None,
        used: bool = False, reflected: bool = False,
        trigger_log_handle: LogHandle | None = None,
        timeout: bool = False,
        duration: float = -1.0,
    ) -> StackResult:
        slot, attribute = self._stack_slot(target, stack_name)
        current = getattr(slot, attribute)
        if delta < 0:
            delta = -min(current, -delta)
        result = StackResult(delta, None)
        if delta == 0:
            return result
        setattr(slot, attribute, current + delta)
        if source_item is None:
            return result

        log_data = {
            "action": "stack_change", "stack_name": stack_name,
            "amount": delta, "actual": delta,
            "target_player_id": target.player_id,
            "used": used, "reflected": reflected, "timeout": timeout,
            "trigger_log_sequence": (
                trigger_log_handle.sequence if trigger_log_handle else None
            ),
        }
        if delta > 0 and duration > 0:
            log_data["duration"] = duration
        log_handle = self.record_log(source_item, log_data)
        event = StackChangeContext(
            battle_state=self, item=source_item, owner=target,
            opponent=self.get_opponent(target.player_id),
            target=target, stack_name=stack_name, amount=delta,
            source_item=source_item, used=used, reflected=reflected,
            timeout=timeout, trigger_log_handle=trigger_log_handle,
            log_handle=log_handle, duration=duration,
        )
        result.event = event
        signal_stack = "lucky" if stack_name == "Luck" else stack_name.lower()
        self.emit_signal(target, f"character_{signal_stack}_changed", event)
        return result

    def gain_stacks(
        self, target: PlayerState, stack_name: str, amount: int, *,
        source_item: BattleItem | None = None,
        trigger_log_handle: LogHandle | None = None,
        reflected: bool = False,
        duration: float = -1.0,
    ) -> StackResult:
        slot, attribute = self._stack_slot(target, stack_name)
        if type(amount) is not int or amount < 0:
            raise ValueError("gained stack amount must be a non-negative int")
        if type(duration) not in (int, float) or not math.isfinite(duration):
            raise ValueError("stack duration must be a finite real number")
        duration = float(duration)
        if duration >= 0:
            try:
                timer_duration = _godot_float32(duration)
            except OverflowError:
                raise ValueError("stack duration must fit a finite float32") from None
            if not math.isfinite(timer_duration):
                raise ValueError("stack duration must fit a finite float32")
        result = StackResult(0, None)
        if amount == 0:
            return result

        state = self._stack_state(target, stack_name)
        resisted = 0
        resist_chance = state.resist_chance_percent
        if source_item is not None and not reflected:
            resist_chance -= source_item.stack_amplification_chances.get(stack_name, 0.0)
        if resist_chance > 0:
            for _ in range(amount):
                if self.rng.random() <= resist_chance / 100.0:
                    resisted += 1
        elif resist_chance < 0:
            for _ in range(amount):
                if self.rng.random() <= -resist_chance / 100.0:
                    amount += 1

        left = amount - resisted
        reflected_amount = 0
        if stack_name in DebuffSlot.__annotations__:
            if not reflected:
                # Even 0% consumes a roll and can match an exact zero draw.
                for _ in range(amount):
                    if self.rng.random() <= state.reflect_chance_percent / 100.0:
                        reflected_amount += 1
                left -= reflected_amount
                if left > 0:
                    reflected_by_stacks = min(left, target.debuff_reflect_stacks)
                    if reflected_by_stacks > 0:
                        reflected_amount += reflected_by_stacks
                        left -= reflected_by_stacks
                        target.debuff_reflect_stacks -= reflected_by_stacks
                if reflected_amount > 0:
                    amount -= reflected_amount

            # Original overlap can make left negative and increase resist_stacks.
            own_stacks_used = min(left, state.resist_stacks)
            resisted += own_stacks_used
            left -= own_stacks_used
            state.resist_stacks -= own_stacks_used
            if left > 0:
                character_stacks_used = min(left, target.debuff_resist_stacks)
                resisted += character_stacks_used
                target.debuff_resist_stacks -= character_stacks_used

        if resisted > 0:
            amount -= resisted
            self.record_log(source_item, {
                "action": "stack_resisted", "stack_name": stack_name,
                "amount": resisted, "actual": resisted,
                "target_player_id": target.player_id, "reflected": reflected,
                "trigger_log_sequence": (
                    trigger_log_handle.sequence if trigger_log_handle else None
                ),
            })
        if amount > 0:
            maximum = 100000 if stack_name == "Block" else 10000
            amount = min(amount, maximum - getattr(slot, attribute))
            # Original cap-zero return also discards pending partial reflection.
            if amount == 0:
                return result
            if duration < 0:
                state.permanent_stacks += amount
            else:
                state.temporary_stacks.append(TemporaryStackBatch(
                    amount, self.time + duration, source_item,
                ))
                if _timer_time_left(state.timer) <= 0:
                    _start_timer(state.timer, duration)
                    state.next_temporary_index = 0
                elif duration < _timer_time_left(state.timer):
                    _stop_timer(state.timer)
                    _start_timer(state.timer, duration)
                    state.next_temporary_index = len(state.temporary_stacks) - 1
            result = self._commit_stack_delta(
                target, stack_name, amount, source_item=source_item,
                reflected=reflected, trigger_log_handle=trigger_log_handle,
                duration=duration,
            )
        if reflected_amount > 0:
            self.gain_stacks(
                self.get_opponent(target.player_id), stack_name, reflected_amount,
                source_item=source_item, trigger_log_handle=trigger_log_handle,
                reflected=True, duration=duration,
            )
        return result

    def lose_stacks(
        self, target: PlayerState, stack_name: str, amount: int, *,
        source_item: BattleItem | None = None,
        trigger_log_handle: LogHandle | None = None,
        used: bool = False,
    ) -> StackResult:
        slot, attribute = self._stack_slot(target, stack_name)
        if type(amount) is not int or amount < 0:
            raise ValueError("removed stack amount must be a non-negative int")
        if amount == 0:
            return StackResult(0, None)

        current = getattr(slot, attribute)
        amount = min(current, amount)
        state = self._stack_state(target, stack_name)
        if not used:
            protected = 0
            protection_chance = state.cleanse_protection_chance_percent
            if protection_chance > 0:
                for _ in range(amount):
                    if self.rng.random() <= protection_chance / 100.0:
                        protected += 1
            elif protection_chance < 0:
                for _ in range(amount):
                    if self.rng.random() <= -protection_chance / 100.0:
                        protected -= 1
            amount = max(0, min(current, amount - protected))
            # 原版此处未限制 isBuff，疑似漏判，会连自身减益净化也阻挡；为复现原版保留。
            if amount > 0 and state.resist_stacks > 0:
                protected_by_stacks = min(amount, state.resist_stacks)
                protected += protected_by_stacks
                amount -= protected_by_stacks
                state.resist_stacks -= protected_by_stacks
            if (
                stack_name in BuffSlot.__annotations__
                and amount > 0 and target.buff_protect_stacks > 0
            ):
                protected_by_stacks = min(amount, target.buff_protect_stacks)
                protected += protected_by_stacks
                amount -= protected_by_stacks
                target.buff_protect_stacks -= protected_by_stacks
            if protected > 0:
                self.record_log(source_item, {
                    "action": "stack_protected", "stack_name": stack_name,
                    "amount": protected, "actual": protected,
                    "target_player_id": target.player_id,
                    "trigger_log_sequence": (
                        trigger_log_handle.sequence if trigger_log_handle else None
                    ),
                })

        if state.permanent_stacks >= amount:
            state.permanent_stacks -= amount
        else:
            temporary_to_remove = amount - state.permanent_stacks
            state.permanent_stacks = 0
            while temporary_to_remove > 0:
                if not state.temporary_stacks:
                    self.record_log("Stacks", {
                        "action": "stack_diagnostic",
                        "reason": "private_amount_missing",
                        "event_kind": "diagnostic",
                        "contributes_to_stack_totals": False,
                        "stack_name": stack_name,
                        "target_player_id": target.player_id,
                        "remaining": temporary_to_remove,
                    })
                    break
                farthest_index = 0
                for index in range(1, len(state.temporary_stacks)):
                    if (
                        state.temporary_stacks[index].expires_at
                        > state.temporary_stacks[farthest_index].expires_at
                    ):
                        farthest_index = index
                farthest = state.temporary_stacks[farthest_index]
                if farthest.amount > temporary_to_remove:
                    farthest.amount -= temporary_to_remove
                    temporary_to_remove = 0
                else:
                    temporary_to_remove -= farthest.amount
                    del state.temporary_stacks[farthest_index]
                    if not state.temporary_stacks:
                        _stop_timer(state.timer)
        return self._commit_stack_delta(
            target, stack_name, -amount, source_item=source_item, used=used,
            trigger_log_handle=trigger_log_handle,
        )

    def try_use_stacks(
        self, target: PlayerState, stack_name: str, amount: int, *,
        source_item: BattleItem | None = None,
        trigger_log_handle: LogHandle | None = None,
    ) -> StackResult:
        slot, attribute = self._stack_slot(target, stack_name)
        if type(amount) is not int or amount < 0:
            raise ValueError("used stack amount must be a non-negative int")
        if getattr(slot, attribute) < amount:
            return StackResult(0, None)
        return self.lose_stacks(
            target, stack_name, amount, source_item=source_item,
            trigger_log_handle=trigger_log_handle, used=True,
        )

    def _on_stack_timeout(self, target: PlayerState, stack_name: str) -> None:
        state = self._stack_state(target, stack_name)
        slot, attribute = self._stack_slot(target, stack_name)
        while True:
            index = state.next_temporary_index
            if not 0 <= index < len(state.temporary_stacks):
                self.record_log("Stacks", {
                    "action": "stack_diagnostic",
                    "reason": "invalid_timeout_index",
                    "event_kind": "diagnostic",
                    "contributes_to_stack_totals": False,
                    "stack_name": stack_name,
                    "target_player_id": target.player_id,
                    "index": index,
                    "batch_count": len(state.temporary_stacks),
                })
                return
            selected = state.temporary_stacks[index]
            self._commit_stack_delta(
                target, stack_name,
                -min(getattr(slot, attribute), selected.amount),
                source_item=selected.source_item, timeout=True,
                trigger_log_handle=None,
            )

            # The callback may change this shared index. Preserve Array.remove's
            # behavior rather than removing the previously selected object.
            index = state.next_temporary_index
            if 0 <= index < len(state.temporary_stacks):
                del state.temporary_stacks[index]
            else:
                self.record_log("Stacks", {
                    "action": "stack_diagnostic",
                    "reason": "invalid_remove_index",
                    "event_kind": "diagnostic",
                    "contributes_to_stack_totals": False,
                    "stack_name": stack_name,
                    "target_player_id": target.player_id,
                    "index": index,
                    "batch_count": len(state.temporary_stacks),
                })
            if not state.temporary_stacks:
                # A callback may have restarted the timer; an empty tail does
                # not cancel that restart in the original implementation.
                return

            earliest_index = 0
            for index in range(1, len(state.temporary_stacks)):
                if (
                    state.temporary_stacks[index].expires_at
                    < state.temporary_stacks[earliest_index].expires_at
                ):
                    earliest_index = index
            state.next_temporary_index = earliest_index
            delay = state.temporary_stacks[earliest_index].expires_at - self.time
            if delay <= 0.01:
                continue
            _start_timer(state.timer, delay)
            return

    def _tick_internal_timers(self) -> None:
        if len(self.players) != 2:
            return
        player, opponent = self.players
        timers = [("status", opponent, None, opponent.status_tick_timer)]
        timers.extend(
            ("stack", opponent, name, self._stack_state(opponent, name).timer)
            for name in _STACK_TIMER_ORDER
        )
        timers.extend((
            ("fatigue_start", None, None, self.fatigue_start_timer),
            ("fatigue_tick", None, None, self.fatigue_tick_timer),
            ("status", player, None, player.status_tick_timer),
        ))
        timers.extend(
            ("stack", player, name, self._stack_state(player, name).timer)
            for name in _STACK_TIMER_ORDER
        )
        # Freeze only active references, then inspect their live fields when
        # visited. A previously inactive timer started below waits one step.
        timers = [entry for entry in timers if entry[3].processing]
        for kind, target, stack_name, timer in timers:
            if not _advance_timer(
                timer, self.frame_delta, one_shot=kind != "status",
            ):
                continue
            if kind == "status":
                if target.status_tick_counter % 2 == 0:
                    self._apply_regeneration_tick(target)
                else:
                    self._apply_poison_tick(target)
                target.status_tick_counter += 1
            elif kind == "stack":
                self._on_stack_timeout(target, stack_name)
            elif kind == "fatigue_start":
                _start_timer(self.fatigue_tick_timer, 3.0)
            else:
                self.inflict_fatigue(opponent, nightfall=True)
                self.stop_if_battle_ended()
                self.inflict_fatigue(player, nightfall=True)
                self.stop_if_battle_ended()
                _start_timer(self.fatigue_tick_timer, NIGHTFALL_FATIGUE_INTERVAL)
            self.stop_if_battle_ended()

    def record_player_state_snapshot(self) -> None:
        if not self.collect_player_state_history:
            return

        self.player_state_history.append(
            {
                "sequence": len(self.player_state_history),
                "frame": self.frame,
                "time": round(self.time, 3),
                "players": [
                    serialize_player_state(player)
                    for player in self.players
                ],
            }
        )

    def regenerate_stamina(self):
        for player in self.players:
            player.stamina = round(min(
                player.max_stamina,
                player.stamina + self.frame_delta,
            ),4)

    def step(self) -> object | None:
        if not self.has_prepared:
            raise ValueError("battle must be prepared before stepping")
        if (
            type(self.frame_delta) not in (int, float)
            or not math.isfinite(self.frame_delta) or self.frame_delta <= 0
        ):
            raise ValueError("frame_delta must be a positive finite number")
        try:
            delta = _godot_float32(self.frame_delta)
        except OverflowError:
            raise ValueError("frame_delta must fit a positive finite float32") from None
        if not math.isfinite(delta) or delta <= 0:
            raise ValueError("frame_delta must fit a positive finite float32")
        self.frame_delta = delta
        try:
            self.start_combat()
            self.stop_if_battle_ended()
            self._tick_internal_timers()
            self.frame += 1
            self.time += delta
            self.regenerate_stamina()
            for active_item in list(self.active_items):
                context = self.build_context(active_item)
                active_item.activate_item(context)
                self.stop_if_battle_ended()
        except _BattleFinishedSignal:
            self.record_player_state_snapshot()
            return self.winner

        self.record_player_state_snapshot()
        return self.winner

    def run(
        self, max_frames: int, frame_delta: float = 1.0 / 60.0,
    ) -> object | None:
        if not self.has_prepared:
            raise ValueError("battle must be prepared before running")
        if (
            type(frame_delta) not in (int, float)
            or not math.isfinite(frame_delta) or frame_delta <= 0
        ):
            raise ValueError("frame_delta must be a positive finite number")
        try:
            delta = _godot_float32(frame_delta)
        except OverflowError:
            raise ValueError("frame_delta must fit a positive finite float32") from None
        if not math.isfinite(delta) or delta <= 0:
            raise ValueError("frame_delta must fit a positive finite float32")
        self.frame_delta = delta
        for _ in range(max_frames):
            if self.winner is not None:
                break
            self.step()
        return self.winner

    def check_battle_end(self) -> None:
        if len(self.players) != 2:
            return
        if self.winner is None:
            if not any(player.is_dead for player in self.players):
                return
            player, opponent = self.players
            self.winner = (player if opponent.health <= 0 else opponent).player_id
        if self.winner is None:
            return
        for player in self.players:
            _stop_timer(player.status_tick_timer)
            for state in player.stack_states.values():
                _stop_timer(state.timer)
                state.temporary_stacks.clear()
        _stop_timer(self.fatigue_start_timer)
        _stop_timer(self.fatigue_tick_timer)
        self._pending_signals.clear()

    def stop_if_battle_ended(self) -> None:
        if self.winner is not None:
            self.check_battle_end()
            raise _BattleFinishedSignal()

    def inflict_fatigue(
        self,
        target: PlayerState,
        *,
        nightfall: bool,
    )->int:
        if self.get_player(target.player_id) is not target:
            raise ValueError("fatigue target is not part of this battle")

        previous_fatigue_damage = target.fatigue_damage
        next_damage = calculate_next_fatigue_damage(
            previous_fatigue_damage,
            nightfall=nightfall,
        )
        target.fatigue_damage = next_damage
        event = make_attack_event(
            attacker=self.get_opponent(target.player_id), defender=target,
            source_item=None, attack_types=("fatigue",),
            min_damage=next_damage, max_damage=next_damage,
        )
        self.resolve_attack(event)
        if event.log_handle is not None:
            self.log[event.log_handle.sequence]["data"]["fatigue_damage_delta"] = (
                next_damage - previous_fatigue_damage
            )
        return next_damage

    def heal(
        self, target: PlayerState, amount: float | int, *,
        source: object = "Healing", trigger_log_handle: LogHandle | None = None,
    ) -> int:
        if self.get_player(target.player_id) is not target:
            raise ValueError("healing target is not part of this battle")
        if (isinstance(amount, bool) or not isinstance(amount, (float, int))
                or not math.isfinite(amount) or amount < 0):
            raise ValueError("healing amount must be non-negative")

        old_health = target.health
        amount = godot_round(float(amount) * max(0.0, target.healing_efficiency))
        target.health = min(target.max_health, old_health + amount)
        actual = target.health - old_health
        overheal = max(0, amount - (target.max_health - old_health))
        log_handle = self.record_log(source, {
            "action": "heal", "target_player_id": target.player_id,
            "healing": amount, "final_healing": actual, "overheal": overheal,
            "trigger_log_sequence": (
                trigger_log_handle.sequence if trigger_log_handle else None
            ),
        })
        context = HealingContext(
            self, source if hasattr(source, "item_key") else None,
            target, self.get_opponent(target.player_id), amount, overheal, log_handle,
        )
        self.emit_signal(target, "character_healed", context)
        if overheal > 0:
            self.emit_signal(target, "character_overhealed", context)
        unhealing = math.ceil(amount * target.unhealing_amount * (
            1.0 + target.typed_damage_factors.get("unhealing", 0.0)
        ))
        if unhealing > 0:
            self.resolve_attack(make_attack_event(
                attacker=target, defender=self.get_opponent(target.player_id),
                source_item=None, attack_types=("unhealing",),
                min_damage=unhealing, max_damage=unhealing,
                trigger_log_handle=log_handle,
            ))
        return actual

    def _apply_regeneration_tick(self, target: PlayerState)->int:
        requested_healing = target.buffs.Regeneration
        if requested_healing <= 0:
            return 0
        return self.heal(target, requested_healing, source="Regeneration")

    def _apply_poison_tick(self, target: PlayerState)->int:
        damage = target.debuffs.Poison
        if damage == 0:
            return 0

        event = make_attack_event(
            attacker=self.get_opponent(target.player_id), defender=target,
            source_item=None, attack_types=("poison",),
            min_damage=damage, max_damage=damage,
        )
        self.resolve_attack(event)
        return event.block_damage + event.health_damage

    def build_context(self, item: BattleItem)->BattleContext:
        owner = self.get_player(item.player_id)
        opponent = self.get_opponent(item.player_id)
        return BattleContext(self, item, owner, opponent)

    def build_attack_reaction_context(
        self,
        item: BattleItem | None,
        attack_phase: str,
        attack_event: AttackEvent,
    )->AttackReactionContext:
        if attack_phase not in SUPPORTED_ATTACK_REACTION_PHASES:
            raise ValueError(f"unsupported attack reaction phase: {attack_phase}")
        if attack_event is None:
            raise ValueError("attack reaction context requires an attack event")

        return AttackReactionContext(
            battle_state=self,
            item=item,
            owner=attack_event.attacker,
            opponent=attack_event.defender,
            attack_phase=attack_phase,
            attack_event=attack_event,
        )

    def canBeEmpowered(self, event: AttackEvent) -> bool:
        return (
            event.source_item is not None
            and "Weapon" in event.source_item.item_types
            and any(t in event.attack_types for t in ("melee", "ranged"))
            and any(getattr(effect, "min_damage", 0) > 0
                    for effect in event.source_item.effects)
        )

    def resolve_attack(self, event: AttackEvent)->AttackEvent:
        item = event.source_item
        if event.is_resolved:
            raise ValueError("attack event is already resolved")
        if self.get_player(event.attacker.player_id) is not event.attacker:
            raise ValueError("attack attacker is not part of this battle")
        if self.get_player(event.defender.player_id) is not event.defender:
            raise ValueError("attack defender is not part of this battle")
        if event.defender.is_dead:
            event.hit = False
            event.rolled_damage = event.pending_damage = 0
            event.block_damage = event.health_damage = 0
            event.crit = False
            event.is_resolved = True
            return event

        is_attack = any(
            attack_type in event.attack_types
            for attack_type in ("melee", "ranged")
        )
        self._determine_attack_hit(event, item, is_attack)
        if not event.hit:
            self._record_attack_miss(event)
        else:
            self._roll_attack_damage(event, item, is_attack)
            self._apply_attack_crit(event, item)
            self._apply_attack_mitigation(event, item, is_attack)
            self._commit_attack_hit(event, item)
        self._finish_attack(event, item, is_attack)
        return event

    def _determine_attack_hit(self, event: AttackEvent, item: BattleItem | None, is_attack: bool) -> None:
        if event.can_miss:
            event.hit = event.defender.accuracy_rng.roll_percent(event.accuracy, self.rng)
            if event.hit and event.defender.dodge_stacks > 0:
                event.hit = False
                event.defender.dodge_stacks -= 1
        else :
            event.hit = True

        if is_attack and item is not None:
            context = self.build_attack_reaction_context(
                item, ATTACK_PHASE_PRE_DEAL_DAMAGE_EARLY, event,
            )
            self.emit_signal(item, ATTACK_PHASE_PRE_DEAL_DAMAGE_EARLY, context)
            early_hook = getattr(item, "onPreDealDamage_early", None)
            if early_hook is not None:
                early_hook(context)

    def _record_attack_miss(self, event: AttackEvent) -> None:
        event.log_handle=self.record_log(
            event.source_item,
            {
                "action": "attack",
                "target_player_id": event.defender.player_id,
                "attack_types": list(event.attack_types),
                "hit": False,
                "trigger_log_sequence": (
                    event.trigger_log_handle.sequence if event.trigger_log_handle else None
                ),
            },
        )
        if event.is_resolved:
            raise ValueError("cannot resolve an already resolved attack event")
        if event.hit is not False:
            raise ValueError("cannot resolve an attack whose hit result changed")
        event.is_resolved = True

    def _roll_attack_damage(self, event: AttackEvent, item: BattleItem | None, is_attack: bool) -> None:
        min_damage = float(event.min_damage)
        max_damage = float(event.max_damage)
        if item is not None:
            if is_attack:
                min_damage, max_damage = math.ceil(min_damage), math.ceil(max_damage)
                if self.canBeEmpowered(event):
                    empower = event.attacker.empower_damage * event.attacker.buffs.Empower
                    min_damage += empower
                    max_damage += empower
                factor = 1.0 + sum(event.attacker.typed_damage_factors.get(t, 0.0)
                                   for t in event.attack_types)
                event.min_damage = max(0, godot_round(min_damage * factor * item.damage_multiplier))
                event.max_damage = max(0, godot_round(max_damage * factor * item.damage_multiplier))
            else:
                # updateEffect assigns the modified float to integer endpoints.
                factor = 1.0 + event.attacker.typed_damage_factors.get("effect", 0.0)
                event.min_damage = max(0, int(min_damage * factor * item.damage_multiplier))
                event.max_damage = max(0, int(max_damage * factor * item.damage_multiplier))
            event.rolled_damage = item.roll_damage(event.min_damage, event.max_damage, self.rng)
        else:
            event.rolled_damage = self.rng.randint(event.min_damage, event.max_damage)
        event.pending_damage += event.rolled_damage
        if "fatigue" in event.attack_types:
            event.pending_damage += event.defender.bonus_fatigue_damage

    def _apply_attack_crit(self, event: AttackEvent, item: BattleItem | None) -> None:
        if event.can_crit:
            crit = event.defender.crit_rng.roll_percent(event.crit_chance, self.rng)
            if not event.crit and item is not None and item.crit_tokens > 0:
                item.crit_tokens-=1
                crit=True
            if event.crit==False and event.attacker.crit_tokens>0:
                event.attacker.crit_tokens-=1
                crit=True
            if crit:
                crit_resisted = event.defender.crit_resistance_rng.roll_percent(
                    event.defender.crit_resistance, self.rng,
                )
                if crit_resisted:
                    crit=False
                elif event.defender.crit_resist_stacks>0:
                    event.defender.crit_resist_stacks-=1
                    crit=False
            event.crit=crit
            if event.crit:
                event.pending_damage = int(
                    event.pending_damage * event.crit_multiplier
                )
        else:
            event.crit = False

    def _apply_attack_mitigation(self, event: AttackEvent, item: BattleItem | None, is_attack: bool) -> None:
        r=max(min(event.defender.damage_resistance/100,1.0),-10.0)
        event.pending_damage = godot_round(float(event.pending_damage) * (1-r))
        if is_attack:
            event.pending_damage = event.pending_damage - event.defender.damage_reduction

        event.pending_damage =0 if event.defender.invulnerable else event.pending_damage

        context = self.build_attack_reaction_context(
            item, ATTACK_PHASE_PRE_TAKE_DAMAGE, event,
        )
        self.emit_signal(event.defender, ATTACK_PHASE_PRE_TAKE_DAMAGE, context)
        event.pending_damage = max(0, event.pending_damage-event.prevented_damage)

        if is_attack and item is not None:
            context = self.build_attack_reaction_context(
                item, ATTACK_PHASE_PRE_DEAL_DAMAGE_LATE, event,
            )
            self.emit_signal(item, ATTACK_PHASE_PRE_DEAL_DAMAGE_LATE, context)
            late_hook = getattr(item, "onPreDealDamage_late", None)
            if late_hook is not None:
                late_hook(context)

        context = self.build_attack_reaction_context(
            item, ATTACK_PHASE_PRE_TAKE_DAMAGE_LATE, event,
        )
        self.emit_signal(event.defender, ATTACK_PHASE_PRE_TAKE_DAMAGE_LATE, context)

    def _commit_attack_hit(self, event: AttackEvent, item: BattleItem | None) -> None:
        if event.is_resolved:
            raise ValueError("cannot commit a resolved attack event")
        if event.hit is not True:
            raise ValueError("cannot commit an attack that did not hit")
        if event.pending_damage < 0:
            raise ValueError("pending attack damage cannot be negative")

        if event.can_be_blocked:
            event.block_damage = min(event.defender.block, event.pending_damage)
            event.health_damage = event.pending_damage - event.block_damage
        else:
            event.block_damage = 0
            event.health_damage = event.pending_damage
        event.is_resolved = True
        self.commit_health_reduction(
            event.defender,
            event.block_damage,
            event.health_damage,
        )
        log_handle = self.record_log(
            item if item is not None else event.attack_types[0].title(),
            {
                "action": "attack" if item is not None else event.attack_types[0] + "_damage",
                "target_player_id": event.defender.player_id,
                "attack_types": list(event.attack_types),
                "hit": True,
                "block_damage": event.block_damage,
                "health_damage": event.health_damage,
                "final_block_damage": event.block_damage,
                "final_health_damage": event.health_damage,
                "critical": event.crit,
                "trigger_log_sequence": (
                    event.trigger_log_handle.sequence if event.trigger_log_handle else None
                ),
            },
        )
        event.log_handle = log_handle

    def _finish_attack(self, event: AttackEvent, item: BattleItem | None, is_attack: bool) -> None:
        post_context = self.build_attack_reaction_context(
            item, ATTACK_PHASE_CHARACTER_ATTACKED, event,
        )
        self.emit_signal(event.defender, ATTACK_PHASE_CHARACTER_ATTACKED, post_context)
        damage_context = self.build_attack_reaction_context(
            item, ATTACK_PHASE_CHARACTER_DAMAGED, event,
        )
        self.emit_signal(event.defender, ATTACK_PHASE_CHARACTER_DAMAGED, damage_context)
        if is_attack and item is not None:
            dealt_hook = getattr(item, "onDealtDamage", None)
            if dealt_hook is not None:
                dealt_hook(post_context)
        if event.defender.health <= 0:
            event.defender.is_dead = True
            self.check_battle_end()
        self.apply_spikes(event)
        if is_attack and item is not None:
            self.apply_vampirism(event)
            context = self.build_attack_reaction_context(
                item, ATTACK_PHASE_ATTACKED, event,
            )
            self.emit_signal(item, ATTACK_PHASE_ATTACKED, context)

    def apply_spikes(self, event: AttackEvent) -> None:
        if (
            event.hit is not True
            or event.pending_damage <= 0
            or not event.can_be_spiked
            or event.defender.buffs.Spikes <= 0
        ):
            return

        if "ranged" in event.attack_types:
            spikes_limit = event.defender.ranged_spikes_limit
        else:
            spikes_limit = event.defender.melee_spikes_limit
        if "effect" in event.attack_types:
            spikes_limit = max(spikes_limit, event.defender.effect_spikes_limit)


        spikes_damage = min(
            event.defender.buffs.Spikes,
            godot_round(event.pending_damage * spikes_limit),
        )
        if spikes_damage > 0:
            attack_event = make_attack_event(
                attacker=event.defender,
                defender=event.attacker,
                source_item=None,
                attack_types=("spikes",),
                min_damage=spikes_damage,
                max_damage=spikes_damage,
                accuracy=100.0,
                trigger_log_handle=event.log_handle
            )
            self.resolve_attack(attack_event)

    def apply_vampirism(self, event: AttackEvent) -> None:
        if (event.hit is not True or event.pending_damage <= 0
                or not event.can_be_vampiric or event.attacker.buffs.Vampirism <= 0):
            return
        vampirism_limit = (event.attacker.ranged_vampirism_limit
                          if "ranged" in event.attack_types
                          else event.attacker.melee_vampirism_limit)
        vampirism_healing = min(
            event.attacker.buffs.Vampirism,
            godot_round(event.pending_damage * vampirism_limit),
        )
        if vampirism_healing > 0 and event.can_be_vampiric:
            self.heal(
                event.attacker,
                vampirism_healing,
                source="Vampirism", trigger_log_handle=event.log_handle,
            )

    def commit_health_reduction(
        self,
        player: PlayerState,
        blocked_damage: int,
        health_damage: int,
    ) -> None:
        if self.get_player(player.player_id) is not player:
            raise ValueError("health reduction target is not part of this battle")
        if (
            type(blocked_damage) is not int
            or type(health_damage) is not int
            or blocked_damage < 0
            or health_damage < 0
        ):
            raise ValueError("health reduction values must be non-negative ints")
        if blocked_damage > player.block:
            raise ValueError("blocked damage cannot exceed current block")

        self.lose_stacks(
            player, "Block", blocked_damage, source_item=None, used=False,
        )
        object.__setattr__(
            player,
            "health",
            player.health - health_damage,
        )
        return

    def get_player(self, player_id):
        for player in self.players:
            if player.player_id == player_id:
                return player
        raise ValueError(f"unknown player_id: {player_id}")

    def get_opponent(self, player_id):
        opponents = [player for player in self.players if player.player_id != player_id]
        if len(opponents) != 1:
            raise ValueError("battle context requires exactly one opponent")
        return opponents[0]
@dataclass
class BattleContext:
    battle_state: BattleState
    item: BattleItem | None
    owner: PlayerState
    opponent: PlayerState

    def for_item(self, item: BattleItem)->BattleContext:
        if item.player_id == self.owner.player_id:
            owner, opponent = self.owner, self.opponent
        elif item.player_id == self.opponent.player_id:
            owner, opponent = self.opponent, self.owner
        else:
            raise ValueError(f"item has unknown player_id: {item.player_id}")
        return replace(self, item=item, owner=owner, opponent=opponent)


@dataclass
class StackChangeContext(BattleContext):
    target: PlayerState
    stack_name: str
    amount: int
    source_item: BattleItem | None
    used: bool
    reflected: bool
    timeout: bool
    trigger_log_handle: LogHandle | None
    log_handle: LogHandle
    duration: float = -1.0


@dataclass
class ItemActivationContext(BattleContext):
    source_item: BattleItem


@dataclass
class AttackReactionContext(BattleContext):
    attack_phase: str
    attack_event: AttackEvent


@dataclass
class HealingContext(BattleContext):
    amount: int
    overheal: int
    log_handle: LogHandle

def evaluate_layout(placements, opponent:PlayerState):
    raise NotImplementedError(
        "layout scoring requires a backpack analyzer, concrete battle items, and score rules"
    )
