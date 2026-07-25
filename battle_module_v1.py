from __future__ import annotations
import random
from dataclasses import dataclass, field
from typing import Sequence

ATTACK_PHASE_ON_ATTACKED = "on_attacked"
ATTACK_PHASE_ON_ATTACK_MISSED = "on_attack_missed"
ITEM_ACTIVATION_PHASE_LINKED = "linked_item_activated"
SUPPORTED_ATTACK_REACTION_PHASES = (
    ATTACK_PHASE_ON_ATTACKED,
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

class Trigger:
    def update(self, context:BattleContext)->bool:
        raise NotImplementedError("concrete triggers must implement update")
class Effect:
    def apply(self, context:BattleContext)->bool:
        raise NotImplementedError("concrete effects must implement apply")
class BattleItem:
    item_id = None
    display_name = None
    item_classes = ()
    rarity = None
    cost = None
    item_types = ()
    icon_types = ()
    is_active_item = False

    def __init__(
        self,
        item_id:str|None=None,
        item_key:str|None=None,
        player_id:int|None=None,
        is_active_item:bool=False,
        triggers:Sequence[Trigger]|None=None,
        effects:Sequence[Effect]|None=None,
        linked_items:Sequence[str]|None=None,
        display_name:str|None=None,
        item_classes:tuple[str, ...]|None=None,
        rarity:str|None=None,
        cost:int|None=None,
        item_types:tuple[str, ...]|None=None,
        icon_types:tuple[str, ...]|None=None,
    ):
        self.item_id = type(self).item_id if item_id is None else item_id
        self.item_key = item_key
        self.player_id = player_id
        self.display_name = type(self).display_name if display_name is None else display_name
        self.item_classes = type(self).item_classes if item_classes is None else item_classes
        self.rarity = type(self).rarity if rarity is None else rarity
        self.cost = type(self).cost if cost is None else cost
        self.item_types = type(self).item_types if item_types is None else item_types
        self.icon_types = type(self).icon_types if icon_types is None else icon_types
        self.is_active_item = type(self).is_active_item if is_active_item is None else is_active_item
        self.triggers = list(triggers) if triggers is not None else []
        self.effects = list(effects) if effects is not None else []
        self.linked_items = list(linked_items) if linked_items is not None else []

        if not self.triggers:
            raise ValueError("battle item must have at least one trigger")
        if not self.effects:
            raise ValueError("battle item must have at least one effect")
        self.trigger_results = [False for _ in self.triggers]

    def update_triggers(self, context:BattleContext)->list[bool]:
        results = []
        for trigger in self.triggers:
            result = trigger.update(context)
            if type(result) is not bool:
                raise ValueError("trigger update must return a bool")
            results.append(result)

        self.trigger_results = results
        return results

    def activate_item(self, context:BattleContext)->None:
        trigger_results = self.update_triggers(context)
        self.run_effect(trigger_results, context)

    def emit_activation(self, context: BattleContext) -> None:
        if context.item is not self:
            raise ValueError("activation context item mismatch")
        context.battle_state.dispatch_item_activation(self)

    def run_effect(self, trigger_results:list[bool], context:BattleContext)->None:
        raise NotImplementedError("concrete items must run their effect logic")

    def add_linked_item(self, linked_key:str):
        if linked_key not in self.linked_items:
            self.linked_items.append(linked_key)

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
    player_id: object = None
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
    rolled_damage: int = 0
    pending_damage: int = 0
    prevented_damage: int = 0
    block_damage: int = 0
    health_damage: int = 0
    is_resolved: bool = False


class _BattleFinishedSignal(Exception):
    pass


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
    _responder_item_cache: dict[
        object,
        dict[str, tuple[BattleItem, ...]],
    ] = field(default_factory=dict, init=False, repr=False)
    _item_activation_listener_cache: dict[
        object,
        dict[str, tuple[BattleItem, ...]],
    ] = field(default_factory=dict, init=False, repr=False)

    def regenerate_stamina(self):
        for player in self.players:
            player.stamina = min(
                player.max_stamina,
                player.stamina + self.frame_delta,
            )

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
            return self.winner

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

        next_damage = calculate_next_fatigue_damage(
            target.fatigue_damage,
            nightfall=nightfall,
        )
        target.fatigue_damage = next_damage
        blocked_damage = min(target.block, next_damage)
        health_damage = next_damage - blocked_damage
        self.commit_health_reduction(
            target,
            blocked_damage,
            health_damage,
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
        return self.heal(target, target.buffs.Regeneration)

    def _apply_poison_tick(self, target: PlayerState)->int:
        damage = target.debuffs.Poison
        if damage == 0:
            return 0

        blocked_damage = min(target.block, damage)
        health_damage = damage - blocked_damage
        return self.commit_health_reduction(
            target,
            blocked_damage,
            health_damage,
        )

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

    def build_item_activation_context(
        self,
        listener: BattleItem,
        source_item: BattleItem,
    ) -> ItemActivationContext:
        listener_context = self.build_context(listener)
        if source_item.player_id != listener.player_id:
            raise ValueError(
                "activation source and listener must have the same owner"
            )
        if (
            listener_context.owner.items.get(source_item.item_key)
            is not source_item
        ):
            raise ValueError(
                "activation source is not owned by the listener owner"
            )
        return ItemActivationContext(
            battle_state=self,
            item=listener,
            owner=listener_context.owner,
            opponent=listener_context.opponent,
            source_item=source_item,
        )

    def _get_item_activation_listeners(
        self,
        source_item: BattleItem,
    ) -> tuple[BattleItem, ...]:
        owner = self.get_player(source_item.player_id)
        if owner.items.get(source_item.item_key) is not source_item:
            raise ValueError("activation source is not part of this battle")

        player_cache = self._item_activation_listener_cache.setdefault(
            owner.player_id,
            {},
        )
        if source_item.item_key in player_cache:
            return player_cache[source_item.item_key]

        matching_items = tuple(
            item
            for item in owner.items.values()
            if source_item.item_key in item.linked_items
            and any(
                getattr(trigger, "item_activation_phase", None)
                == ITEM_ACTIVATION_PHASE_LINKED
                for trigger in item.triggers
            )
        )
        player_cache[source_item.item_key] = matching_items
        return matching_items

    def dispatch_item_activation(
        self,
        source_item: BattleItem,
    ) -> None:
        for listener in self._get_item_activation_listeners(source_item):
            context = self.build_item_activation_context(
                listener,
                source_item,
            )
            listener.activate_item(context)

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

    def _get_attack_reaction_items(
        self,
        responder: PlayerState,
        attack_phase: str,
    )->tuple[BattleItem, ...]:
        if attack_phase not in SUPPORTED_ATTACK_REACTION_PHASES:
            raise ValueError(f"unsupported attack reaction phase: {attack_phase}")
        if self.get_player(responder.player_id) is not responder:
            raise ValueError("attack responder is not part of this battle")

        phase_cache = self._responder_item_cache.setdefault(
            responder.player_id,
            {},
        )
        if attack_phase in phase_cache:
            return phase_cache[attack_phase]

        matching_items = tuple(
            item
            for item in responder.items.values()
            if any(
                getattr(trigger, "attack_phase", None) == attack_phase
                for trigger in item.triggers
            )
        )
        phase_cache[attack_phase] = matching_items
        return matching_items

    def resolve_attack(self, event: AttackEvent)->AttackEvent:
        if event.is_resolved:
            raise ValueError("attack event is already resolved")
        if event.attacker is event.defender:
            raise ValueError("attack requires different players")
        if self.get_player(event.attacker.player_id) is not event.attacker:
            raise ValueError("attack attacker is not part of this battle")
        if self.get_player(event.defender.player_id) is not event.defender:
            raise ValueError("attack defender is not part of this battle")

        event.hit = self.rng.random()*100 < event.accuracy
        if not event.hit:
            self.dispatch_attack_reactions(
                ATTACK_PHASE_ON_ATTACK_MISSED,
                event.defender,
                event,
            )
            if event.is_resolved:
                raise ValueError("cannot resolve an already resolved attack event")
            if event.hit is not False:
                raise ValueError("cannot resolve an attack whose hit result changed")
            event.is_resolved = True
            return event

        event.rolled_damage = self.rng.randint(
            event.min_damage,
            event.max_damage,
        )
        event.pending_damage = event.rolled_damage
        self.dispatch_attack_reactions(
            ATTACK_PHASE_ON_ATTACKED,
            event.defender,
            event,
        )
        if event.is_resolved:
            raise ValueError("cannot commit a resolved attack event")
        if event.hit is not True:
            raise ValueError("cannot commit an attack that did not hit")
        if event.pending_damage < 0:
            raise ValueError("pending attack damage cannot be negative")
        event.block_damage = min(event.defender.block, event.pending_damage)
        event.health_damage = event.pending_damage - event.block_damage
        event.is_resolved = True
        # Battle log may be added here in the future to record the attack event details.
        final_damage = self.commit_health_reduction(
            event.defender,
            event.block_damage,
            event.health_damage,
        )
        # Spike and Vampirism effects can be applied here
        self._apply_melee_hit_statuses(event, final_damage)
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
            self.commit_health_reduction(
                event.attacker,
                blocked_damage,
                health_damage,
            )

        vampirism_healing = min(
            event.attacker.buffs.Vampirism,
            final_damage,
        )
        if vampirism_healing > 0:
            self.heal(event.attacker, vampirism_healing)

    def dispatch_attack_reactions(
        self,
        phase: str,
        responder: PlayerState,
        event: AttackEvent,
    )->None:
        if phase not in SUPPORTED_ATTACK_REACTION_PHASES:
            raise ValueError(f"unsupported attack reaction phase: {phase}")
        if event.is_resolved:
            raise ValueError("cannot dispatch a resolved attack event")

        for item in self._get_attack_reaction_items(responder, phase):
            context = self.build_attack_reaction_context(
                item,
                phase,
                event,
            )
            item.activate_item(context)

    def commit_health_reduction(
        self,
        player: PlayerState,
        blocked_damage: int,
        health_damage: int,
    )->int:
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
        final_blocked_damage = blocked_damage
        final_health_damage = health_damage
        #future damage resistance or mitigation effects can be applied here
        final_health_damage = min(player.health, final_health_damage)
        player.block -= final_blocked_damage
        object.__setattr__(
            player,
            "health",
            player.health - final_health_damage,
        )
        final_damage = final_blocked_damage + final_health_damage
        self.stop_if_battle_ended()
        return final_damage

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
            return BattleContext(self.battle_state, item, self.owner, self.opponent)
        if item.player_id == self.opponent.player_id:
            return BattleContext(self.battle_state, item, self.opponent, self.owner)
        raise ValueError(f"item has unknown player_id: {item.player_id}")


@dataclass
class ItemActivationContext(BattleContext):
    source_item: BattleItem


@dataclass
class AttackReactionContext(BattleContext):
    attack_phase: str
    attack_event: AttackEvent

    def for_item(self, item: BattleItem)->AttackReactionContext:
        base_context = super().for_item(item)
        return AttackReactionContext(
            battle_state=base_context.battle_state,
            item=base_context.item,
            owner=base_context.owner,
            opponent=base_context.opponent,
            attack_phase=self.attack_phase,
            attack_event=self.attack_event,
        )

def evaluate_layout(placements, opponent:PlayerState):
    raise NotImplementedError(
        "layout scoring requires a backpack analyzer, concrete battle items, and score rules"
    )
