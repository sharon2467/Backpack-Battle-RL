from __future__ import annotations

from battle_module_v1 import (
    ITEM_MARKER_TYPES,
    BattleContext,
    BalancedRngState,
    BuffSlot,
    ItemActivationContext,
)
from item_effects_v1 import *
from item_triggers_v1 import *
from typing import Sequence



class BattleItem:
    item_id = None
    display_name = None
    item_classes = ()
    rarity = None
    cost = None
    item_types = ()
    icon_types = ()
    is_active_item = False
    is_crafted = False
    socket_count = 0
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
        self.marker_items = {
            marker_type: []
            for marker_type in ITEM_MARKER_TYPES
        }
        self.gemsocket = [None for _ in range(self.socket_count)]
        self.belongs_to: str | None = None
        self.gem_type: tuple[str, ...] = ()
        self.has_prepared = False
        self.consumed = False
        self.last_activation_frame: int | None = None
        self.activations_this_frame = 0
        self.damage_multiplier = 1.0
        self.crit_tokens = 0
        self.damage_range_acc = 0.0
        self.chance_rng = BalancedRngState()
        if not self.effects:
            raise ValueError("battle item must have at least one effect")
        self.trigger_results = [False for _ in self.triggers]
        for idx, trigger in enumerate(self.triggers):
            trigger.item = self
            trigger.idx = idx
        for effect in self.effects:
            effect.item = self
    def roll_chance(self, chance: float, rng) -> bool:
        return self.chance_rng.roll_percent(chance * 100.0, rng)

    def roll_damage(self, min_damage: int, max_damage: int, rng) -> int:
        damage = rng.randint(min_damage, max_damage)
        difference = damage - 0.5 * (min_damage + max_damage)
        if self.damage_range_acc >= 1:
            malus = min(damage - min_damage, int(self.damage_range_acc))
            self.damage_range_acc -= malus
            damage -= malus
        elif self.damage_range_acc <= -1:
            bonus = min(max_damage - damage, int(abs(self.damage_range_acc)))
            self.damage_range_acc += bonus
            damage += bonus
        self.damage_range_acc += difference
        return damage

    def update_triggers(self, context:BattleContext,trigger_index:int|None=None)->list[bool]:
        results = [False for _ in self.triggers]
        if trigger_index is not None:
            if trigger_index < 0 or trigger_index >= len(self.triggers):
                raise ValueError("trigger index out of range")
            trigger = self.triggers[trigger_index]
            result = trigger.update(context)
            if type(result) is not bool:
                raise ValueError("trigger update must return a bool")
            results[trigger_index]=result
        else:
            for idx,trigger in enumerate(self.triggers):
                result = trigger.update(context)
                if type(result) is not bool:
                    raise ValueError("trigger update must return a bool")
                results[idx]=result
        for i in range(len(self.triggers)):
            self.trigger_results[i] = results[i]
        return results

    def activate_item(self, context:BattleContext , trigger_index:int|None=None)->None:
        if not self.triggers and trigger_index is None:
            return
        trigger_results = self.update_triggers(context, trigger_index)
        self.run_effect(trigger_results, context)

    def emit_activation(self, context: BattleContext) -> None:
        if context.item is not self:
            raise ValueError("activation context item mismatch")
        if context.battle_state.winner is not None:
            return
        if self.last_activation_frame != context.battle_state.frame:
            self.last_activation_frame = context.battle_state.frame
            self.activations_this_frame = 0
        self.activations_this_frame += 1
        if self.activations_this_frame > 3:
            return
        context.battle_state.record_log(
            self,
            {"action": "item_activation"},
        )
        activation_context = ItemActivationContext(
            battle_state=context.battle_state,
            item=self,
            owner=context.owner,
            opponent=context.opponent,
            source_item=self,
        )
        context.battle_state.emit_signal(
            self,
            "item_activation",
            activation_context,
        )

    def run_effect(self, trigger_results:list[bool], context:BattleContext)->None:
        raise NotImplementedError("concrete items must run their effect logic")

    def add_linked_item(self, linked_key:str):
        if linked_key not in self.linked_items:
            self.linked_items.append(linked_key)

    def add_marker_item(
        self,
        marker_type: str,
        linked_key: str,
    ) -> None:
        if marker_type not in ITEM_MARKER_TYPES:
            raise ValueError(f"unsupported marker type: {marker_type}")
        if linked_key not in self.marker_items[marker_type]:
            self.marker_items[marker_type].append(linked_key)
        self.add_linked_item(linked_key)
    def add_gems(self, gem: BattleItem) -> None:
        if self.has_prepared or gem.has_prepared:
            raise ValueError("cannot socket gems after preparation")
        if self is gem or "Gem" in self.item_types:
            raise ValueError("a gem cannot host another gem")
        if not self.item_key or not gem.item_key or self.item_key == gem.item_key:
            raise ValueError("host and gem require distinct nonempty item keys")
        if self.player_id != gem.player_id:
            raise ValueError("host and gem must belong to the same player")
        if "Gem" not in gem.item_types or gem.socket_count != 0 or gem.gemsocket:
            raise ValueError("socketed item must be a gem without sockets")
        if gem.belongs_to is not None:
            raise ValueError("gem is already socketed")
        for i in range(len(self.gemsocket)):
            if self.gemsocket[i] is None:
                self.gemsocket[i] = gem.item_key
                gem.belongs_to = self.item_key
                gem.gem_type = self.item_types
                return
        raise ValueError("no available gem sockets")

    def get_gems(self, context: BattleContext) -> list[BattleItem]:
        return [context.owner.items[key] for key in self.gemsocket if key is not None]

    def getTriggerPriority(self) -> int:
        return 0

    def prepare(self, context: BattleContext) -> None:
        if self.has_prepared:
            raise ValueError("item has already been prepared")
        self.damage_range_acc = 0.0
        self.chance_rng.reset()
        for gem in self.get_gems(context):
            gem.prepare(context.for_item(gem))
        for trigger in self.triggers:
            trigger.connect_bus(context)
        self.onPrepare(context)
        self.has_prepared = True

    def onPrepare(self, context: BattleContext) -> None:
        pass

    def preCombatStart(self, context: BattleContext) -> None:
        for gem in self.get_gems(context):
            gem.preCombatStart(context.for_item(gem))
            context.battle_state.check_battle_end()
            if context.battle_state.winner is not None:
                return
        if self.belongs_to is None:
            for trigger in self.triggers:
                if isinstance(trigger, CooldownTrigger):
                    trigger.initialize_for_combat(context)
        self.onPreCombatStart(context)

    def onPreCombatStart(self, context: BattleContext) -> None:
        pass

    def combatStart(self, context: BattleContext) -> None:
        for gem in self.get_gems(context):
            gem.combatStart(context.for_item(gem))
            context.battle_state.check_battle_end()
            if context.battle_state.winner is not None:
                return
        self.onCombatStart(context)

    def onCombatStart(self, context: BattleContext) -> None:
        pass

    def postCombatStart(self, context: BattleContext) -> None:
        for gem in self.get_gems(context):
            gem.postCombatStart(context.for_item(gem))
            context.battle_state.check_battle_end()
            if context.battle_state.winner is not None:
                return
        self.onPostCombatStart(context)

    def onPostCombatStart(self, context: BattleContext) -> None:
        pass

    def consume(self, context: BattleContext) -> None:
        self.emit_activation(context)
        self.consumed = True

class Weapon(BattleItem):
    def __init__(self,item_id: str | None = None, item_key: str | None = None, player_id: int | None = None,is_active_item: bool = True,
                    cooldown: float = 0.0,min_damage: int = 1,max_damage: int = 1,accuracy: float = 100.0,stamina_cost: float = 0.0,attack_types: tuple[str, ...] = ("melee",),
                    triggers: Sequence[Trigger] | None = None,effects: Sequence[Effect] | None = None,is_trigger_append=True, is_effect_append=True

                ):
        self.cooldown = cooldown
        self.min_damage = min_damage
        self.max_damage = max_damage
        self.accuracy = accuracy
        self.stamina_cost = stamina_cost
        self.attack_types = attack_types
        triggers_temp=[CooldownTrigger(cooldown_seconds=cooldown)]
        effects_temp=[StaminaConsumptionEffect(stamina_cost=stamina_cost),AttackEffect(min_damage=min_damage,max_damage=max_damage,accuracy=accuracy)]
        if triggers is not None:
            if is_trigger_append:
                triggers_temp.extend(triggers)
            else:
                triggers_temp=triggers
        if effects is not None:
            if is_effect_append:
                effects_temp.extend(effects)
            else:
                effects_temp=effects
        super().__init__(
            item_id=item_id,
            item_key=item_key,
            player_id=player_id,
            is_active_item=is_active_item,
            triggers=triggers_temp,
            effects=effects_temp,
        )
        if not 'Weapon' in self.item_types:
            raise ValueError("Weapon must have 'Weapon' in item_types")
    def onPreDealDamage_early(self, context: BattleContext) -> None:
        pass
    def onPreDealDamage_late(self, context: BattleContext) -> None:
        pass
    def onDealtDamage(self, context: BattleContext) -> None:
        pass
    def run_effect(
        self,
        trigger_results: list[bool],
        context: BattleContext,
    ) -> None:
        if not trigger_results[0]:
            return
        if not self.effects[0].apply(context):
            return
        self.effects[1].apply(context, attack_type=self.attack_types)
        self.emit_activation(context)

class PocketSand(BattleItem):
    item_id = "pocket_sand"
    display_name = "Pocket Sand"
    item_classes = ("Neutral",)
    rarity = "Common"
    cost = 2
    item_types = ("Accessory",)
    icon_types = ("nature",)
    is_active_item = False
    socket_count = 0

    def __init__(
        self,
        item_id: str | None = None,
        item_key: str | None = None,
        player_id: int | None = None,
    ):
        super().__init__(
            item_id=item_id,
            item_key=item_key,
            player_id=player_id,
            is_active_item=False,
            triggers=[],
            effects=[InflictDebuffEffect("Blind", 1)],
        )

    def onCombatStart(self, context: BattleContext) -> None:
        self.effects[0].apply(context)
        self.consume(context)


class HealingHerbs(BattleItem):
    item_id = "healing_herbs"
    display_name = "Healing Herbs"
    item_classes = ("Neutral",)
    rarity = "Common"
    cost = 4
    item_types = ("Accessory",)
    icon_types = ("nature",)
    is_active_item = False
    socket_count = 0

    def __init__(
        self,
        item_id: str | None = None,
        item_key: str | None = None,
        player_id: int | None = None,
    ):
        super().__init__(
            item_id=item_id,
            item_key=item_key,
            player_id=player_id,
            is_active_item=False,
            triggers=[],
            effects=[GainBuffEffect("Regeneration", 2)],
        )

    def onCombatStart(self, context: BattleContext) -> None:
        self.effects[0].apply(context)
        self.consume(context)


class Flame(BattleItem):
    item_id = "flame"
    display_name = "Flame"
    item_classes = ("Pyromancer",)
    rarity = "Common"
    cost = 1
    item_types = ("Accessory",)
    icon_types = ("fire",)
    is_active_item = False
    socket_count = 0

    def __init__(
        self,
        item_id: str | None = None,
        item_key: str | None = None,
        player_id: int | None = None,
    ):
        super().__init__(
            item_id=item_id,
            item_key=item_key,
            player_id=player_id,
            is_active_item=False,
            triggers=[],
            effects=[GainBuffEffect("Heat", 1)],
        )

    def onCombatStart(self, context: BattleContext) -> None:
        self.effects[0].apply(context)
        self.consume(context)


class WalrusTusk(BattleItem):
    item_id = "walrus_tusk"
    display_name = "Walrus Tusk"
    item_classes = ("Neutral",)
    rarity = "Common"
    cost = 4
    item_types = ("Accessory",)
    icon_types = ("nature",)
    is_active_item = False
    socket_count = 0

    def __init__(
        self,
        item_id: str | None = None,
        item_key: str | None = None,
        player_id: int | None = None,
    ):
        super().__init__(
            item_id=item_id,
            item_key=item_key,
            player_id=player_id,
            is_active_item=False,
            triggers=[],
            effects=[GainBuffEffect("Spikes", 1)],
        )

    def onCombatStart(self, context: BattleContext) -> None:
        self.effects[0].apply(context)
        self.consume(context)


class ShinyShell(BattleItem):
    item_id = "shiny_shell"
    display_name = "Shiny Shell"
    item_classes = ("Neutral",)
    rarity = "Common"
    cost = 2
    item_types = ("Accessory",)
    icon_types = ("nature", "holy")
    is_active_item = True
    socket_count = 0

    def __init__(
        self,
        item_id: str | None = None,
        item_key: str | None = None,
        player_id: int | None = None,
    ):
        super().__init__(
            item_id=item_id,
            item_key=item_key,
            player_id=player_id,
            is_active_item=True,
            triggers=[AfterTimeTrigger(delay_seconds=5.0)],
            effects=[
                HolyLinkedHealEffect(
                    base_amount=5,
                    amount_per_holy=3,
                )
            ],
        )

    def run_effect(
        self,
        trigger_results: list[bool],
        context: BattleContext,
    ) -> None:
        if not trigger_results[0]:
            return
        self.effects[0].apply(context)
        self.emit_activation(context)


class WandOfEquilibrium(BattleItem):
    item_id = "wand_of_equilibrium"
    display_name = "Wand of Equilibrium"
    item_classes = ("Mage",)
    rarity = "Common"
    cost = 4
    item_types = ("Accessory",)
    icon_types = ()
    is_active_item = True
    socket_count = 0
    RESOURCE_NAMES = ("Mana", "Luck", "Regeneration")

    def __init__(
        self,
        item_id: str | None = None,
        item_key: str | None = None,
        player_id: int | None = None,
    ) -> None:
        gain_effects = [
            GainBuffEffect(resource_name, 1)
            for resource_name in self.RESOURCE_NAMES
        ]
        use_effects = [
            UseBuffEffect(resource_name, 1)
            for resource_name in self.RESOURCE_NAMES
        ]
        empower_effect = GainBuffEffect("Empower", 1)
        super().__init__(
            item_id=item_id,
            item_key=item_key,
            player_id=player_id,
            is_active_item=True,
            triggers=[CooldownTrigger(cooldown_seconds=3.3)],
            effects=[*gain_effects, *use_effects, empower_effect],
        )
        self._gain_effects_by_name = dict(
            zip(self.RESOURCE_NAMES, gain_effects)
        )
        self._use_effects_by_name = dict(
            zip(self.RESOURCE_NAMES, use_effects)
        )
        self._empower_effect = empower_effect

    def _least_resource_name(self, buffs: BuffSlot, rng) -> str:
        minimum = min(getattr(buffs, name) for name in self.RESOURCE_NAMES)
        return rng.choice([name for name in self.RESOURCE_NAMES
                           if getattr(buffs, name) == minimum])

    def _most_resource_name(self, buffs: BuffSlot, rng) -> str:
        maximum = max(getattr(buffs, name) for name in self.RESOURCE_NAMES)
        return rng.choice([name for name in self.RESOURCE_NAMES
                           if getattr(buffs, name) == maximum])

    def run_effect(
        self,
        trigger_results: list[bool],
        context: BattleContext,
    ) -> None:
        if not trigger_results[0]:
            return

        buffs = context.owner.buffs
        least_resource = self._least_resource_name(buffs, context.battle_state.rng)
        self._gain_effects_by_name[least_resource].apply(context)

        if max(
            getattr(buffs, resource_name)
            for resource_name in self.RESOURCE_NAMES
        ) >= 10:
            most_resource = self._most_resource_name(buffs, context.battle_state.rng)
            self._use_effects_by_name[most_resource].apply(context)
            self._empower_effect.apply(context)

        self.emit_activation(context)


class MagicForDummies(BattleItem):
    item_id = "magic_for_dummies"
    display_name = "Magic For Dummies"
    item_classes = ("Mage",)
    rarity = "Common"
    cost = 4
    item_types = ("Book",)
    icon_types = ("magic",)
    is_active_item = True
    is_crafted = False
    socket_count = 0
    BASE_MAX_HEALTH = 8
    MAX_HEALTH_PER_SPELL_WEIGHT = 3

    def __init__(
        self,
        item_id: str | None = None,
        item_key: str | None = None,
        player_id: int | None = None,
    ) -> None:
        super().__init__(
            item_id=item_id,
            item_key=item_key,
            player_id=player_id,
            is_active_item=True,
            triggers=[CooldownTrigger(cooldown_seconds=5.0)],
            effects=[
                UseBuffEffect("Mana", 1),
                GainMaxHealthEffect(self.BASE_MAX_HEALTH),
            ],
        )
        self.spell_weight: int | None = None

    def _prepare_spell_weight(
        self,
        context: BattleContext,
    ) -> None:
        if self.spell_weight is not None:
            return

        self.spell_weight = sum(
            2 if context.owner.items[linked_key].is_crafted else 1
            for linked_key in self.marker_items["star"]
            if "Spell" in context.owner.items[linked_key].item_types
        )
        self.effects[1].amount = (
            self.BASE_MAX_HEALTH
            + self.spell_weight * self.MAX_HEALTH_PER_SPELL_WEIGHT
        )

    def onPrepare(self, context: BattleContext) -> None:
        self._prepare_spell_weight(context)

    def run_effect(
        self,
        trigger_results: list[bool],
        context: BattleContext,
    ) -> None:
        if not trigger_results[0]:
            return
        if self.effects[0].apply(context):
            self.effects[1].apply(context)
        self.emit_activation(context)


class Whetstone(BattleItem):
    item_id = "whetstone"
    display_name = "Whetstone"
    item_classes = ("Neutral",)
    rarity = "Common"
    cost = 4
    item_types = ("Accessory",)
    icon_types = ()
    is_active_item = False
    socket_count = 0

    def __init__(
        self,
        item_id: str | None = None,
        item_key: str | None = None,
        player_id: int | None = None,
    ):
        super().__init__(
            item_id=item_id,
            item_key=item_key,
            player_id=player_id,
            is_active_item=False,
            triggers=[],
            effects=[LinkedWeaponDamageEffect(amount=1)],
        )

    def onCombatStart(self, context: BattleContext) -> None:
        self.effects[0].apply(context)
        self.emit_activation(context)


class Twine(BattleItem):
    item_id = "twine"
    display_name = "Twine"
    item_classes = ("Adventurer",)
    rarity = "Common"
    cost = 2
    item_types = ("Accessory",)
    icon_types = ()
    is_active_item = False
    socket_count = 0
    BASE_CHANCE = 0.20
    CHANCE_PER_NEUTRAL = 0.20

    def __init__(
        self,
        item_id: str | None = None,
        item_key: str | None = None,
        player_id: int | None = None,
    ):
        super().__init__(
            item_id=item_id,
            item_key=item_key,
            player_id=player_id,
            is_active_item=False,
            triggers=[ActivationTrigger(marker_type="star")],
            effects=[GainMaxHealthEffect(amount=2)],
        )
        self.neutral_item_count: int | None = None

    def _prepare_neutral_item_count(
        self,
        context: BattleContext,
    ) -> None:
        if self.neutral_item_count is not None:
            return

        self.neutral_item_count = sum(
            1
            for linked_key in self.marker_items["diamond"]
            if "Neutral" in context.owner.items[linked_key].item_classes
        )

    def onPrepare(self, context: BattleContext) -> None:
        self._prepare_neutral_item_count(context)

    def run_effect(
        self,
        trigger_results: list[bool],
        context: BattleContext,
    ) -> None:
        if not trigger_results[0]:
            return

        chance = min(
            1.0,
            self.BASE_CHANCE
            + self.neutral_item_count * self.CHANCE_PER_NEUTRAL,
        )
        success = self.roll_chance(chance, context.battle_state.rng)
        roll = self.chance_rng.last_roll
        source_item = getattr(context, "source_item", None)
        context.battle_state.record_log(
            self,
            {
                "action": "gain_max_health_check",
                "chance": chance,
                "roll": roll,
                "success": success,
                "neutral_item_count": self.neutral_item_count,
                "source_item_key": getattr(
                    source_item,
                    "item_key",
                    None,
                ),
                "source_item_id": getattr(
                    source_item,
                    "item_id",
                    None,
                ),
            },
        )
        if not success:
            return

        self.effects[0].apply(context)
        self.emit_activation(context)


class Goobling(BattleItem):
    item_id = "goobling"
    display_name = "Goobling"
    item_classes = ("Neutral",)
    rarity = "Common"
    cost = 2
    item_types = ("Pet",)
    icon_types = ()
    is_active_item = False
    socket_count = 0

    def __init__(
        self,
        item_id: str | None = None,
        item_key: str | None = None,
        player_id: int | None = None,
    ):
        super().__init__(
            item_id=item_id,
            item_key=item_key,
            player_id=player_id,
            is_active_item=False,
            triggers=[
                SlimeActivationTrigger(
                    required_activations=3,
                )
            ],
            effects=[HealEffect(amount=4)],
        )

    def run_effect(
        self,
        trigger_results: list[bool],
        context: BattleContext,
    ) -> None:
        if not trigger_results[0]:
            return
        self.effects[0].apply(context)
        self.emit_activation(context)


class WoodenBuckler(BattleItem):
    item_id = "wooden_buckler"
    display_name = "Wooden Buckler"
    item_classes = ("Neutral",)
    rarity = "Common"
    cost = 4
    item_types = ("Shield",)
    icon_types = ()
    is_active_item = False
    socket_count = 1

    def __init__(
        self,
        item_id: str | None = None,
        item_key: str | None = None,
        player_id: int | None = None,
    ):
        super().__init__(
            item_id=item_id,
            item_key=item_key,
            player_id=player_id,
            is_active_item=False,
            triggers=[
                OnAttackedTrigger(
                    attack_types=("melee",),
                    chance=0.3,
                ),
                ShieldBlockedTrigger(),
            ],
            effects=[
                PreventAttackDamageEffect(amount=7),
                RemoveOpponentStaminaEffect(amount=0.3),
            ],
        )
        self.blocked_attack_event = None

    def run_effect(
        self,
        trigger_results: list[bool],
        context: BattleContext,
    ) -> None:
        if trigger_results[0]:
            self.blocked_attack_event = context.attack_event
            self.effects[0].apply(context)
        if trigger_results[1]:
            self.effects[1].apply(context)
            self.emit_activation(context)
            context.battle_state.emit_signal(self, "blocked", context)
            self.blocked_attack_event = None


class Broom(Weapon):
    item_id = "broom"
    display_name = "Broom"
    item_classes = ("Neutral",)
    rarity = "Common"
    cost = 4
    item_types = ("Weapon",)
    icon_types = ("melee",)
    is_active_item = True
    socket_count = 1

    def __init__(
        self,
        item_id: str | None = None,
        item_key: str | None = None,
        player_id: int | None = None,
    ):
        super().__init__(
            item_id=item_id,
            item_key=item_key,
            player_id=player_id,
            is_active_item=True,
            cooldown=1.7,
            min_damage=2,
            max_damage=4,
            accuracy=95,
            stamina_cost=1.2,
            attack_types=("melee",),
            triggers=[AttackMissTrigger()],
            effects=[InflictDebuffEffect(debuff_name="Blind", amount=1)]
        )
        self.miss_damage_bonus = 0

    def run_effect(
        self,
        trigger_results: list[bool],
        context: BattleContext,
    ) -> None:
        if trigger_results[1]:
            self.miss_damage_bonus += 2
            self.effects[1].stack_damage_modifier(2)
            attack_event = context.attack_event
            context.battle_state.record_log(
                self,
                {
                    "action": "gain_miss_damage_bonus",
                    "miss_damage_bonus_delta": 2,
                    "damage_modifier_delta": 2,
                    "attack_source_item_key": (
                        getattr(
                            attack_event.source_item,
                            "item_key",
                            None,
                        )
                    ),
                    "attack_source_item_id": (
                        getattr(
                            attack_event.source_item,
                            "item_id",
                            None,
                        )
                    ),
                    "attacker_player_id": attack_event.attacker.player_id,
                },
            )
        if not trigger_results[0]:
            return
        if not self.effects[0].apply(context):
            return
        self.effects[1].apply(context, self.attack_types)
        self.emit_activation(context)
        if self.miss_damage_bonus > 0:
            consumed_bonus = self.miss_damage_bonus
            self.effects[1].stack_damage_modifier(-consumed_bonus)
            self.miss_damage_bonus = 0
            context.battle_state.record_log(
                self,
                {
                    "action": "consume_miss_damage_bonus",
                    "miss_damage_bonus_delta": -consumed_bonus,
                    "damage_modifier_delta": -consumed_bonus,
                },
            )

    def onDealtDamage(self, context: BattleContext) -> None:
        if context.attack_event.hit is True:
            blind_success = self.roll_chance(0.33, context.battle_state.rng)
            blind_roll = self.chance_rng.last_roll
            context.battle_state.record_log(
                self,
                {
                    "action": "inflict_blind_check",
                    "chance": 0.33,
                    "roll": blind_roll,
                    "success": blind_success,
                },
            )
            if blind_success:
                self.effects[2].apply(context)


class WoodenSword(Weapon):
    item_id = "wooden_sword"
    display_name = "Wooden Sword"
    item_classes = ("Neutral",)
    rarity = "Common"
    cost = 3
    item_types = ("Weapon",)
    icon_types = ("melee",)
    is_active_item = True
    socket_count = 1

    def __init__(
        self,
        item_id: str | None = None,
        item_key: str | None = None,
        player_id: int | None = None,
    ):
        super().__init__(
            item_id=item_id,
            item_key=item_key,
            player_id=player_id,
            is_active_item=True,
            cooldown=1.4,
            min_damage=1,
            max_damage=3,
            accuracy=90,
            stamina_cost=1.0,
            attack_types=("melee",),
        )

class Shortbow(Weapon):
    item_id = "shortbow"
    display_name = "Shortbow"
    item_classes = ("Ranger",)
    rarity = "Common"
    cost = 4
    item_types = ("Weapon",)
    icon_types = ("ranged",)
    is_active_item = True
    socket_count = 1

    def __init__(
        self,
        item_id: str | None = None,
        item_key: str | None = None,
        player_id: int | None = None,
    ):
        super().__init__(
            item_id=item_id,
            item_key=item_key,
            player_id=player_id,
            is_active_item=True,
            cooldown=1.7,
            min_damage=2,
            max_damage=3,
            accuracy=85,
            stamina_cost=0.7,
            attack_types=("ranged",),
        )



class Stone(Weapon):
    item_id = "stone"
    display_name = "Stone"
    item_classes = ("Neutral",)
    rarity = "Common"
    cost = 1
    item_types = ("Weapon",)
    icon_types = ("ranged", "nature")
    is_active_item = True
    socket_count = 0

    def __init__(
        self,
        item_id: str | None = None,
        item_key: str | None = None,
        player_id: int | None = None,
    ):
        super().__init__(
            item_id=item_id,
            item_key=item_key,
            player_id=player_id,
            is_active_item=True,
            min_damage=2,
            max_damage=4,
            accuracy=70,
            attack_types=("ranged",),
            triggers=[AfterTimeTrigger(delay_seconds=2.5)],
            effects=[RemoveOpponentBlockEffect(amount=4)],
            is_trigger_append=False,
        )

    def onPreDealDamage_late(self, context: BattleContext) -> None:
        self.effects[2].apply(context)


class Banana(BattleItem):
    item_id = "banana"
    display_name = "Banana"
    item_classes = ("Neutral",)
    rarity = "Common"
    cost = 3
    item_types = ("Food",)
    icon_types = ("nature",)
    is_active_item = True
    socket_count = 0

    def __init__(
        self,
        item_id: str | None = None,
        item_key: str | None = None,
        player_id: int | None = None,
    ):
        super().__init__(
            item_id=item_id,
            item_key=item_key,
            player_id=player_id,
            is_active_item=True,
            triggers=[FoodCooldownTrigger(cooldown_seconds=5.0)],
            effects=[
                HealEffect(amount=4),
                RegenerateStaminaEffect(amount=1.0),
            ],
        )

    def onPrepare(self, context: BattleContext) -> None:
        self.triggers[0].prepare_speed_modifiers(context)
        self.triggers[0].speed_modifiers_prepared = True

    def run_effect(
        self,
        trigger_results: list[bool],
        context: BattleContext,
    ) -> None:
        if not trigger_results[0]:
            return
        self.effects[0].apply(context)
        self.effects[1].apply(context)
        self.emit_activation(context)


class Garlic(BattleItem):
    item_id = "garlic"
    display_name = "Garlic"
    item_classes = ("Neutral",)
    rarity = "Common"
    cost = 2
    item_types = ("Food",)
    icon_types = ("nature",)
    is_active_item = True
    socket_count = 0

    def __init__(
        self,
        item_id: str | None = None,
        item_key: str | None = None,
        player_id: int | None = None,
    ):
        super().__init__(
            item_id=item_id,
            item_key=item_key,
            player_id=player_id,
            is_active_item=True,
            triggers=[FoodCooldownTrigger(cooldown_seconds=4.0)],
            effects=[
                GainBlockEffect(amount=3),
                BuffRemovalEffect(
                    buff_name="Vampirism",
                    amount=1,
                ),
            ],
        )

    def onPrepare(self, context: BattleContext) -> None:
        self.triggers[0].prepare_speed_modifiers(context)
        self.triggers[0].speed_modifiers_prepared = True

    def run_effect(
        self,
        trigger_results: list[bool],
        context: BattleContext,
    ) -> None:
        if not trigger_results[0]:
            return
        self.effects[0].apply(context)
        removal_success = self.roll_chance(0.30, context.battle_state.rng)
        removal_roll = self.chance_rng.last_roll
        context.battle_state.record_log(
            self,
            {
                "action": "remove_vampirism_check",
                "chance": 0.30,
                "roll": removal_roll,
                "success": removal_success,
            },
        )
        if removal_success:
            self.effects[1].apply(context)
        self.emit_activation(context)


class Pan(Weapon):
    item_id = "pan"
    display_name = "Pan"
    item_classes = ("Neutral",)
    rarity = "Common"
    cost = 4
    item_types = ("Weapon",)
    icon_types = ("melee",)
    is_active_item = True
    socket_count = 1

    def __init__(
        self,
        item_id: str | None = None,
        item_key: str | None = None,
        player_id: int | None = None,
    ):
        super().__init__(
            item_id=item_id,
            item_key=item_key,
            player_id=player_id,
            is_active_item=True,
            cooldown=2.2,
            attack_types=("melee",),
            effects=[
            StaminaConsumptionEffect(stamina_cost=2.0),
            FoodLinkedMeleeAttackEffect(
                min_damage=5,
                max_damage=6,
                accuracy=85,
                damage_per_food=1,
            ),
            ],
            is_effect_append=False
        )

    def onPreCombatStart(self, context: BattleContext) -> None:
        self.effects[1].prepare_damage_modifier(context)
        self.effects[1].damage_modifier_prepared = True


class Rat(BattleItem):
    item_id = "rat"
    display_name = "Rat"
    item_classes = ("Ranger",)
    rarity = "Common"
    cost = 4
    item_types = ("Pet",)
    icon_types = ("nature",)
    is_active_item = True
    socket_count = 0

    def __init__(
        self,
        item_id: str | None = None,
        item_key: str | None = None,
        player_id: int | None = None,
    ):
        super().__init__(
            item_id=item_id,
            item_key=item_key,
            player_id=player_id,
            is_active_item=True,
            triggers=[CooldownTrigger(cooldown_seconds=3.3)],
            effects=[
                AttackEffect(
                    min_damage=5,
                    max_damage=5,
                    accuracy=100,
                ),
                InflictDebuffEffect("Poison", 1),
                InflictDebuffEffect("Blind", 1),
            ],
        )

    def onCombatStart(self, context: BattleContext) -> None:
        count = sum(
            1 for key in self.marker_items["star"]
            if "Pet" in context.owner.items[key].item_types
            or "Food" in context.owner.items[key].item_types
        )
        self.triggers[0].stack_speed_modifier(count * 0.15)

    def run_effect(
        self,
        trigger_results: list[bool],
        context: BattleContext,
    ) -> None:
        if not trigger_results[0]:
            return
        if not self.effects[0].apply(context, ("effect",)):
            self.emit_activation(context)
            return
        poison_success = self.roll_chance(0.75, context.battle_state.rng)
        poison_roll = self.chance_rng.last_roll
        context.battle_state.record_log(
            self,
            {
                "action": "inflict_poison_check",
                "chance": 0.75,
                "roll": poison_roll,
                "success": poison_success,
            },
        )
        if poison_success:
            self.effects[1].apply(context)
        blind_success = self.roll_chance(0.10, context.battle_state.rng)
        blind_roll = self.chance_rng.last_roll
        context.battle_state.record_log(
            self,
            {
                "action": "inflict_blind_check",
                "chance": 0.10,
                "roll": blind_roll,
                "success": blind_success,
            },
        )
        if blind_success:
            self.effects[2].apply(context)
        self.emit_activation(context)


DEFAULT_ITEM_FACTORIES = {
    "banana": Banana,
    "broom": Broom,
    "flame": Flame,
    "garlic": Garlic,
    "goobling": Goobling,
    "healing_herbs": HealingHerbs,
    "magic_for_dummies": MagicForDummies,
    "pan": Pan,
    "pocket_sand": PocketSand,
    "rat": Rat,
    "shiny_shell": ShinyShell,
    "shortbow": Shortbow,
    "stone": Stone,
    "twine": Twine,
    "walrus_tusk": WalrusTusk,
    "wand_of_equilibrium": WandOfEquilibrium,
    "whetstone": Whetstone,
    "wooden_buckler": WoodenBuckler,
    "wooden_sword": WoodenSword,
}
