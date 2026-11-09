from __future__ import annotations
import math
import random
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
STATUS_TICK_INTERVAL = 2.0
FIRST_REGENERATION_TIME = 1.0
FIRST_POISON_TIME = 2.0
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
class StackState:
    resist_chance_percent: float = 0.0
    resist_stacks: int = 0
    reflect_chance_percent: float = 0.0
    cleanse_protection_chance_percent: float = 0.0


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
    frame_delta: float = 1.0 / 30.0
    next_regeneration_time: float = FIRST_REGENERATION_TIME
    next_poison_time: float = FIRST_POISON_TIME
    next_nightfall_fatigue_time: float = NIGHTFALL_FATIGUE_START_TIME
    rng: random.Random = field(default_factory=random.Random)
    log: list[dict[str, object]] = field(default_factory=list)
    collect_player_state_history: bool = False
    player_state_history: list[dict[str, object]] = field(
        default_factory=list,
    )
    _bus_cache: dict[tuple[object, str], list[tuple[BattleItem,int]]] = field(default_factory=dict, init=False, repr=False)
    has_prepared: bool = field(default=False, init=False)
    combat_started: bool = field(default=False, init=False)

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
    ) -> BuffSlot | DebuffSlot:
        if (
            not isinstance(target, PlayerState)
            or self.get_player(target.player_id) is not target
        ):
            raise ValueError("stack target is not part of this battle")
        if type(stack_name) is not str:
            raise ValueError("unsupported stack name")
        if stack_name in BuffSlot.__annotations__:
            return target.buffs
        if stack_name in DebuffSlot.__annotations__:
            return target.debuffs
        raise ValueError("unsupported stack name")

    def _stack_state(self, target: PlayerState, stack_name: str) -> StackState:
        self._stack_slot(target, stack_name)
        if stack_name not in target.stack_states:
            target.stack_states[stack_name] = StackState()
        return target.stack_states[stack_name]

    def _commit_stack_delta(
        self, target: PlayerState, stack_name: str, delta: int, *,
        source_item: BattleItem | None = None,
        used: bool = False, reflected: bool = False,
        trigger_log_handle: LogHandle | None = None,
    ) -> StackResult:
        slot = self._stack_slot(target, stack_name)
        result = StackResult(delta, None)
        if delta == 0:
            return result
        setattr(slot, stack_name, getattr(slot, stack_name) + delta)
        if source_item is None:
            return result

        log_handle = self.record_log(source_item, {
            "action": "stack_change", "stack_name": stack_name,
            "amount": delta, "actual": delta,
            "target_player_id": target.player_id,
            "used": used, "reflected": reflected, "timeout": False,
            "trigger_log_sequence": (
                trigger_log_handle.sequence if trigger_log_handle else None
            ),
        })
        event = StackChangeContext(
            battle_state=self, item=source_item, owner=target,
            opponent=self.get_opponent(target.player_id),
            target=target, stack_name=stack_name, amount=delta,
            source_item=source_item, used=used, reflected=reflected,
            timeout=False, trigger_log_handle=trigger_log_handle,
            log_handle=log_handle,
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
    ) -> StackResult:
        slot = self._stack_slot(target, stack_name)
        if type(amount) is not int or amount < 0:
            raise ValueError("gained stack amount must be a non-negative int")
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
            amount = min(amount, 10000 - getattr(slot, stack_name))
            # Original cap-zero return also discards pending partial reflection.
            if amount == 0:
                return result
            result = self._commit_stack_delta(
                target, stack_name, amount, source_item=source_item,
                reflected=reflected, trigger_log_handle=trigger_log_handle,
            )
        if reflected_amount > 0:
            self.gain_stacks(
                self.get_opponent(target.player_id), stack_name, reflected_amount,
                source_item=source_item, trigger_log_handle=trigger_log_handle,
                reflected=True,
            )
        return result

    def lose_stacks(
        self, target: PlayerState, stack_name: str, amount: int, *,
        source_item: BattleItem | None = None,
        trigger_log_handle: LogHandle | None = None,
        used: bool = False,
    ) -> StackResult:
        slot = self._stack_slot(target, stack_name)
        if type(amount) is not int or amount < 0:
            raise ValueError("removed stack amount must be a non-negative int")
        if amount == 0:
            return StackResult(0, None)

        current = getattr(slot, stack_name)
        amount = min(current, amount)
        if not used:
            state = self._stack_state(target, stack_name)
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

        actual = min(getattr(slot, stack_name), amount)
        return self._commit_stack_delta(
            target, stack_name, -actual, source_item=source_item, used=used,
            trigger_log_handle=trigger_log_handle,
        )

    def try_use_stacks(
        self, target: PlayerState, stack_name: str, amount: int, *,
        source_item: BattleItem | None = None,
        trigger_log_handle: LogHandle | None = None,
    ) -> StackResult:
        slot = self._stack_slot(target, stack_name)
        if type(amount) is not int or amount < 0:
            raise ValueError("used stack amount must be a non-negative int")
        if getattr(slot, stack_name) < amount:
            return StackResult(0, None)
        return self.lose_stacks(
            target, stack_name, amount, source_item=source_item,
            trigger_log_handle=trigger_log_handle, used=True,
        )

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

    def step(self):
        if not self.has_prepared:
            raise ValueError("battle must be prepared before stepping")
        try:
            self.start_combat()
            self.stop_if_battle_ended()
            self.regenerate_stamina()
            for active_item in list(self.active_items):
                context = self.build_context(active_item)
                active_item.activate_item(context)
                self.stop_if_battle_ended()

            self.frame += 1
            self.time += self.frame_delta
            self._apply_system_triggers()
        except _BattleFinishedSignal:
            self.record_player_state_snapshot()
            return self.winner

        self.record_player_state_snapshot()
        return self.winner

    def run(self, max_frames: int, frame_delta: float = 1.0 / 30.0):
        if not self.has_prepared:
            raise ValueError("battle must be prepared before running")
        self.frame_delta = frame_delta
        for _ in range(max_frames):
            if self.winner is not None:
                break
            self.step()
        return self.winner

    def check_battle_end(self):
        if self.winner is not None or len(self.players) != 2:
            return
        if not any(player.is_dead for player in self.players):
            return
        player, opponent = self.players
        self.winner = (player if opponent.health <= 0 else opponent).player_id

    def stop_if_battle_ended(self):
        if self.winner is not None:
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

    def _apply_system_triggers(self)->None:
        if len(self.players) != 2:
            return

        regeneration_due = self.time >= self.next_regeneration_time
        poison_due = self.time >= self.next_poison_time
        fatigue_due = self.time >= self.next_nightfall_fatigue_time

        if regeneration_due:
            self.next_regeneration_time += STATUS_TICK_INTERVAL
        if poison_due:
            self.next_poison_time += STATUS_TICK_INTERVAL
        if fatigue_due:
            self.next_nightfall_fatigue_time += NIGHTFALL_FATIGUE_INTERVAL

        enemy = self.players[1]
        player = self.players[0]

        if regeneration_due:
            self._apply_regeneration_tick(enemy)
            self.stop_if_battle_ended()
        if poison_due:
            self._apply_poison_tick(enemy)
            self.stop_if_battle_ended()
        if fatigue_due:
            self.inflict_fatigue(enemy, nightfall=True)
            self.stop_if_battle_ended()
            self.inflict_fatigue(player, nightfall=True)
            self.stop_if_battle_ended()
        if poison_due:
            self._apply_poison_tick(player)
            self.stop_if_battle_ended()
        if regeneration_due:
            self._apply_regeneration_tick(player)
            self.stop_if_battle_ended()

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
        self.commit_health_reduction(
                event.defender,
                event.block_damage,
                event.health_damage,
        )

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
    ):
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

        player.block -= blocked_damage
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
