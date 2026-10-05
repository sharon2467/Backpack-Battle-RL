from __future__ import annotations
import math
import random
from dataclasses import asdict, dataclass, field, replace
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from item_factory_registry_v1 import BattleItem

ATTACK_PHASE_PRE_DEAL_DAMAGE_EARLY = "pre_deal_damage_early"
ATTACK_PHASE_PRE_TAKE_DAMAGE = "pre_take_damage"
ATTACK_PHASE_PRE_DEAL_DAMAGE_LATE = "pre_deal_damage_late"
ATTACK_PHASE_PRE_TAKE_DAMAGE_LATE = "pre_take_damage_late"
ATTACK_PHASE_CHARACTER_ATTACKED = "character_attacked"
ATTACK_PHASE_CHARACTER_DAMAGED = "character_damaged"
ATTACK_PHASE_ATTACKED = "attacked"
ATTACK_PHASE_ON_ATTACK_MISSED = "on_attack_missed"
ITEM_MARKER_TYPES = ("star", "diamond", "triangle")
SUPPORTED_ATTACK_REACTION_PHASES = (
    ATTACK_PHASE_PRE_DEAL_DAMAGE_EARLY,
    ATTACK_PHASE_PRE_TAKE_DAMAGE,
    ATTACK_PHASE_PRE_DEAL_DAMAGE_LATE,
    ATTACK_PHASE_PRE_TAKE_DAMAGE_LATE,
    ATTACK_PHASE_CHARACTER_ATTACKED,
    ATTACK_PHASE_CHARACTER_DAMAGED,
    ATTACK_PHASE_ATTACKED,
    ATTACK_PHASE_ON_ATTACK_MISSED,
)
NIGHTFALL_FATIGUE_START_TIME = 17.0
NIGHTFALL_FATIGUE_INTERVAL = 1.0
STATUS_TICK_INTERVAL = 2.0
FIRST_REGENERATION_TIME = 1.0
FIRST_POISON_TIME = 2.0


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
    source_item: BattleItem
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
    final_blocked_damage: int = 0
    final_health_damage: int = 0

    log_handle: LogHandle | None = None
    trigger_log_handle: LogHandle | None = None
class _BattleFinishedSignal(Exception):
    pass


@dataclass(frozen=True, eq=False)
class LogHandle:
    battle_state: BattleState = field(repr=False)
    sequence: int


@dataclass
class BattleState:
    frame: int = 0
    time: float = 0.0
    players: list[PlayerState] = field(default_factory=list)
    active_items: list[BattleItem] = field(default_factory=list)
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
    def prepareItems(self):
        for player in self.players:
            for item in player.items.values():
                context = self.build_context(item)
                item.onPrepare(context)
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

    def _get_pending_damage_log_data(
        self,
        log_handle: LogHandle,
        target: PlayerState,
    ) -> dict[str, object]:
        if not isinstance(log_handle, LogHandle):
            raise ValueError("damage log handle must be a LogHandle")
        if log_handle.battle_state is not self:
            raise ValueError("damage log handle belongs to another battle")
        if not 0 <= log_handle.sequence < len(self.log):
            raise ValueError("damage log handle is stale")

        entry = self.log[log_handle.sequence]
        if entry.get("sequence") != log_handle.sequence:
            raise ValueError("damage log handle is stale")
        data = entry.get("data")
        if not isinstance(data, dict):
            raise ValueError("damage log data must be a dict")
        if (
            "block_damage" not in data
            or "health_damage" not in data
        ):
            raise ValueError("damage log is missing raw damage fields")
        if data.get("target_player_id") != target.player_id:
            raise ValueError("damage log target does not match damage target")
        if (
            "final_block_damage" in data
            or "final_health_damage" in data
        ):
            raise ValueError("damage log is already complete")
        return data

    def _complete_damage_log(
        self,
        data: dict[str, object],
        final_block_damage: int,
        final_health_damage: int,
    ) -> None:
        data["final_block_damage"] = final_block_damage
        data["final_health_damage"] = final_health_damage

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
        self.regenerate_stamina()
        try:
            for active_item in list(self.active_items):
                context = self.build_context(active_item)
                active_item.activate_item(context)

            self.frame += 1
            self.time += self.frame_delta
            self._apply_system_triggers()
        except _BattleFinishedSignal:
            self.record_player_state_snapshot()
            return self.winner

        self.record_player_state_snapshot()
        return self.winner

    def run(self, max_frames: int, frame_delta: float = 1.0 / 30.0):
        self.frame_delta = frame_delta
        for _ in range(max_frames):
            if self.winner is not None:
                break
            self.step()
        return self.winner

    def check_battle_end(self):
        if len(self.players) < 2:
            return

        alive_players = [player for player in self.players if player.health > 0]
        if len(alive_players) == 1:
            self.winner = alive_players[0].player_id

    def stop_if_battle_ended(self):
        self.check_battle_end()
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
        blocked_damage = min(target.block, next_damage)
        health_damage = next_damage - blocked_damage
        log_handle = self.record_log(
            "Fatigue",
            {
                "action": "fatigue_damage",
                "target_player_id": target.player_id,
                "fatigue_damage_delta": (
                    next_damage - previous_fatigue_damage
                ),
                "block_damage": blocked_damage,
                "health_damage": health_damage,
            },
        )
        self.commit_health_reduction(
            target,
            blocked_damage,
            health_damage,
            log_handle=log_handle,
        )
        return next_damage

    def heal(self, target: PlayerState, amount: int)->int:
        if self.get_player(target.player_id) is not target:
            raise ValueError("healing target is not part of this battle")
        if type(amount) is not int or amount < 0:
            raise ValueError("healing amount must be a non-negative int")

        old_health = target.health
        if amount == 0 or old_health >= target.max_health:
            return 0
        target.health = min(target.max_health, old_health + amount)
        return target.health - old_health

    def _apply_regeneration_tick(self, target: PlayerState)->int:
        requested_healing = target.buffs.Regeneration
        actual_healing = self.heal(target, requested_healing)
        if requested_healing > 0:
            self.record_log(
                "Regeneration",
                {
                    "action": "heal",
                    "target_player_id": target.player_id,
                    "healing": requested_healing,
                    "final_healing": actual_healing,
                },
            )
        return actual_healing

    def _apply_poison_tick(self, target: PlayerState)->int:
        damage = target.debuffs.Poison
        if damage == 0:
            return 0

        blocked_damage = min(target.block, damage)
        health_damage = damage - blocked_damage
        log_handle = self.record_log(
            "Poison",
            {
                "action": "poison_damage",
                "target_player_id": target.player_id,
                "block_damage": blocked_damage,
                "health_damage": health_damage,
            },
        )
        final_block_damage, final_health_damage = (
            self.commit_health_reduction(
                target,
                blocked_damage,
                health_damage,
                log_handle=log_handle,
            )
        )
        return final_block_damage + final_health_damage

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
        if poison_due:
            self._apply_poison_tick(enemy)
        if fatigue_due:
            self.inflict_fatigue(enemy, nightfall=True)
            self.inflict_fatigue(player, nightfall=True)
        if poison_due:
            self._apply_poison_tick(player)
        if regeneration_due:
            self._apply_regeneration_tick(player)

    def build_context(self, item: BattleItem)->BattleContext:
        owner = self.get_player(item.player_id)
        opponent = self.get_opponent(item.player_id)
        return BattleContext(self, item, owner, opponent)

    def build_attack_reaction_context(
        self,
        item: BattleItem,
        attack_phase: str,
        attack_event: AttackEvent,
    )->AttackReactionContext:
        if attack_phase not in SUPPORTED_ATTACK_REACTION_PHASES:
            raise ValueError(f"unsupported attack reaction phase: {attack_phase}")
        if attack_event is None:
            raise ValueError("attack reaction context requires an attack event")

        base_context = self.build_context(item)
        return AttackReactionContext(
            battle_state=base_context.battle_state,
            item=base_context.item,
            owner=base_context.owner,
            opponent=base_context.opponent,
            attack_phase=attack_phase,
            attack_event=attack_event,
        )

    def resolve_attack(self, event: AttackEvent)->AttackEvent:
        item = event.source_item
        if event.is_resolved:
            raise ValueError("attack event is already resolved")
        if event.attacker is event.defender:
            raise ValueError("attack requires different players")
        if self.get_player(event.attacker.player_id) is not event.attacker:
            raise ValueError("attack attacker is not part of this battle")
        if self.get_player(event.defender.player_id) is not event.defender:
            raise ValueError("attack defender is not part of this battle")

        is_attack = any(
            attack_type in event.attack_types
            for attack_type in ("melee", "ranged")
        )
        final_damage = 0
        hit_roll = self.rng.random() * 100
        event.hit = hit_roll < event.accuracy
        if is_attack:
            context = self.build_attack_reaction_context(
                item, ATTACK_PHASE_PRE_DEAL_DAMAGE_EARLY, event,
            )
            self.emit_signal(item, ATTACK_PHASE_PRE_DEAL_DAMAGE_EARLY, context)
            early_hook = getattr(item, "onPreDealDamage_early", None)
            if early_hook is not None:
                early_hook(context)

        if not event.hit:
            event.log_handle=self.record_log(
                event.source_item,
                {
                    "action": "attack",
                    "target_player_id": event.defender.player_id,
                    "attack_types": list(event.attack_types),
                    "hit": False,
                },
            )
            context = self.build_attack_reaction_context(item, ATTACK_PHASE_ON_ATTACK_MISSED, event)

            self.emit_signal(event.attacker,ATTACK_PHASE_ON_ATTACK_MISSED,context)
            if event.is_resolved:
                raise ValueError("cannot resolve an already resolved attack event")
            if event.hit is not False:
                raise ValueError("cannot resolve an attack whose hit result changed")
            event.is_resolved = True
        else:
            event.rolled_damage = self.rng.randint(
                event.min_damage,
                event.max_damage,
            )
            event.pending_damage += event.rolled_damage
            context = self.build_attack_reaction_context(
                item, ATTACK_PHASE_PRE_TAKE_DAMAGE, event,
            )
            self.emit_signal(event.defender, ATTACK_PHASE_PRE_TAKE_DAMAGE, context)
            event.pending_damage = max(0, event.pending_damage-event.prevented_damage)
            if is_attack:
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
            if event.is_resolved:
                raise ValueError("cannot commit a resolved attack event")
            if event.hit is not True:
                raise ValueError("cannot commit an attack that did not hit")
            if event.pending_damage < 0:
                raise ValueError("pending attack damage cannot be negative")
            event.block_damage = min(event.defender.block, event.pending_damage)
            event.health_damage = event.pending_damage - event.block_damage
            event.is_resolved = True
            log_handle = self.record_log(
                item,
                {
                    "action": "attack",
                    "target_player_id": event.defender.player_id,
                    "attack_types": list(event.attack_types),
                    "hit": True,
                    "block_damage": event.block_damage,
                    "health_damage": event.health_damage,
                },
            )
            event.log_handle = log_handle
            committed_blocked_damage, committed_health_damage = (
                self.commit_health_reduction(
                    event.defender,
                    event.block_damage,
                    event.health_damage,
                    log_handle=log_handle,
                )
            )
            event.final_blocked_damage = committed_blocked_damage
            event.final_health_damage = committed_health_damage
            final_damage = committed_blocked_damage + committed_health_damage

        post_context = self.build_attack_reaction_context(
            item, ATTACK_PHASE_CHARACTER_ATTACKED, event,
        )
        self.emit_signal(event.defender, ATTACK_PHASE_CHARACTER_ATTACKED, post_context)
        damage_context = self.build_attack_reaction_context(
            item, ATTACK_PHASE_CHARACTER_DAMAGED, event,
        )
        self.emit_signal(event.defender, ATTACK_PHASE_CHARACTER_DAMAGED, damage_context)
        if is_attack:
            dealt_hook = getattr(item, "onDealtDamage", None)
            if dealt_hook is not None:
                dealt_hook(post_context)
        self._apply_melee_hit_statuses(event, final_damage)
        if is_attack:
            context = self.build_attack_reaction_context(
                item, ATTACK_PHASE_ATTACKED, event,
            )
            self.emit_signal(item, ATTACK_PHASE_ATTACKED, context)
        return event

    def _apply_melee_hit_statuses(
        self,
        event: AttackEvent,
        final_damage: int,
    )->None:
        if (
            event.hit is not True
            or "melee" not in event.attack_types
            or final_damage <= 0
        ):
            return

        spikes_damage = min(
            event.defender.buffs.Spikes,
            final_damage,
        )
        if spikes_damage > 0:
            blocked_damage = min(event.attacker.block, spikes_damage)
            health_damage = spikes_damage - blocked_damage
            log_handle = self.record_log(
                "Spikes",
                {
                    "action": "spikes_damage",
                    "owner_player_id": event.defender.player_id,
                    "target_player_id": event.attacker.player_id,
                    "attack_source_item_key": getattr(
                        event.source_item,
                        "item_key",
                        None,
                    ),
                    "attack_source_item_id": getattr(
                        event.source_item,
                        "item_id",
                        None,
                    ),
                    "block_damage": blocked_damage,
                    "health_damage": health_damage,
                },
            )
            self.commit_health_reduction(
                event.attacker,
                blocked_damage,
                health_damage,
                log_handle=log_handle,
            )

        vampirism_healing = min(
            event.attacker.buffs.Vampirism,
            final_damage,
        )
        if vampirism_healing > 0:
            actual_healing = self.heal(
                event.attacker,
                vampirism_healing,
            )
            self.record_log(
                "Vampirism",
                {
                    "action": "heal",
                    "target_player_id": event.attacker.player_id,
                    "attack_source_item_key": getattr(
                        event.source_item,
                        "item_key",
                        None,
                    ),
                    "attack_source_item_id": getattr(
                        event.source_item,
                        "item_id",
                        None,
                    ),
                    "healing": vampirism_healing,
                    "final_healing": actual_healing,
                },
            )

    def commit_health_reduction(
        self,
        player: PlayerState,
        blocked_damage: int,
        health_damage: int,
        *,
        log_handle: LogHandle | None = None,
    )->tuple[int, int]:
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
        log_data = (
            None
            if log_handle is None
            else self._get_pending_damage_log_data(
                log_handle,
                player,
            )
        )
        final_blocked_damage = blocked_damage
        final_health_damage = health_damage
        #future damage resistance mitigation,and invincible effects can be applied here
        final_health_damage = min(player.health, final_health_damage)
        player.block -= final_blocked_damage
        object.__setattr__(
            player,
            "health",
            player.health - final_health_damage,
        )
        if log_data is not None:
            self._complete_damage_log(
                log_data,
                final_blocked_damage,
                final_health_damage,
            )
        self.stop_if_battle_ended()
        return final_blocked_damage, final_health_damage

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
    item: BattleItem
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
class ItemActivationContext(BattleContext):
    source_item: BattleItem


@dataclass
class AttackReactionContext(BattleContext):
    attack_phase: str
    attack_event: AttackEvent

def evaluate_layout(placements, opponent:PlayerState):
    raise NotImplementedError(
        "layout scoring requires a backpack analyzer, concrete battle items, and score rules"
    )
