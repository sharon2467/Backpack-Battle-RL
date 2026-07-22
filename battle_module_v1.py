from __future__ import annotations
import random
from dataclasses import dataclass, field
from typing import Sequence

ATTACK_PHASE_ON_ATTACKED = "on_attacked"
SUPPORTED_ATTACK_REACTION_PHASES = (ATTACK_PHASE_ON_ATTACKED,)

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

    def run_effects(self, context:BattleContext)->bool:
        trigger_results = self.update_triggers(context)
        will_run_linked_items = self.run_own_effect(trigger_results, context)
        if type(will_run_linked_items) is not bool:
            raise ValueError("run_own_effect must return a bool")

        if will_run_linked_items:
            self.run_linked_items(context)
        return will_run_linked_items

    def run_own_effect(self, trigger_results:list[bool], context:BattleContext)->bool:
        raise NotImplementedError("concrete items must run their own effect logic")

    def run_linked_items(self, context:BattleContext)->None:
        for linked_key in self.linked_items:
            linked_item = context.owner.items[linked_key]
            linked_context = context.for_item(linked_item)
            linked_item.run_effects(linked_context)

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
    block: int = 0
    stamina: float = 0.0
    max_stamina: float = 0.0
    buffs: BuffSlot = field(default_factory=BuffSlot)
    debuffs: DebuffSlot = field(default_factory=DebuffSlot)
    items: dict[str,BattleItem] = field(default_factory=dict)


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



@dataclass
class BattleState:
    frame: int = 0
    time: float = 0.0
    players: list[PlayerState] = field(default_factory=list)
    active_items: list[BattleItem] = field(default_factory=list)
    winner: object = None
    frame_delta: float = 1.0
    rng: random.Random = field(default_factory=random.Random)
    _responder_item_cache: dict[
        object,
        dict[str, tuple[BattleItem, ...]],
    ] = field(default_factory=dict, init=False, repr=False)

    def step(self):
        for player in self.players:
            player.stamina = min(
                player.max_stamina,
                player.stamina + self.frame_delta,
            )

        for active_item in list(self.active_items):
            context = self.build_context(active_item)
            active_item.run_effects(context)

        self.frame += 1
        self.time += self.frame_delta
        self.check_battle_end()
        return self.winner

    def run(self, max_frames: int, frame_delta: float = 1.0):
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
        self.commit_attack_damage(event)
        event.is_resolved = True
        return event

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
            item.run_effects(context)

    def commit_attack_damage(self, event: AttackEvent)->None:
        if event.is_resolved:
            raise ValueError("cannot commit a resolved attack event")
        if event.hit is not True:
            raise ValueError("cannot commit an attack that did not hit")
        if event.pending_damage < 0:
            raise ValueError("pending attack damage cannot be negative")

        blocked_damage = min(event.defender.block, event.pending_damage)
        health_damage = event.pending_damage - blocked_damage
        event.defender.block -= blocked_damage
        event.defender.health -= health_damage
        event.block_damage = blocked_damage
        event.health_damage = health_damage

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
