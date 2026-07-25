from battle_module_v1 import (
    ATTACK_PHASE_ON_ATTACKED,
    ATTACK_PHASE_ON_ATTACK_MISSED,
    ITEM_ACTIVATION_PHASE_LINKED,
    AttackEvent,
    AttackReactionContext,
    BattleContext,
    BattleItem,
    BuffSlot,
    DebuffSlot,
    Effect,
    ItemActivationContext,
    Trigger,
)

SUPPORTED_ATTACK_TYPES = ("melee", "ranged", "effect")


class StartOfBattleTrigger(Trigger):
    def __init__(self):
        self.has_triggered = False

    def update(self, context: BattleContext) -> bool:
        if isinstance(context, AttackReactionContext):
            return False
        if self.has_triggered or context.battle_state.frame != 0:
            return False

        self.has_triggered = True
        return True


class LinkedItemActivationCountTrigger(Trigger):
    item_activation_phase = ITEM_ACTIVATION_PHASE_LINKED

    def __init__(self, required_activations: int):
        if (
            type(required_activations) is not int
            or required_activations <= 0
        ):
            raise ValueError(
                "required activations must be a positive int"
            )
        self.required_activations = required_activations
        self.activation_count = 0

    def update(self, context: BattleContext) -> bool:
        if not isinstance(context, ItemActivationContext):
            return False
        if context.source_item.player_id != context.item.player_id:
            return False
        if context.source_item.item_key not in context.item.linked_items:
            return False

        self.activation_count += 1
        if self.activation_count < self.required_activations:
            return False

        self.activation_count -= self.required_activations
        return True


class CooldownTrigger(Trigger):
    def __init__(self, cooldown_seconds: float):
        self.cooldown_seconds = cooldown_seconds
        self.cooldown_progress = 0.0
        self.speed_modifiers: float = 0.0
        self.speed_modifiers_prepared: bool = False

    def stack_speed_modifier(self, amount: float) -> None:
        self.speed_modifiers += amount
    def prepare_speed_modifiers(self,context:BattleContext) -> None:
        pass
    def update(self, context: BattleContext) -> bool:
        if isinstance(context, AttackReactionContext):
            return False
        if not self.speed_modifiers_prepared:
            self.prepare_speed_modifiers(context)
            self.speed_modifiers_prepared = True
        status_faster = min(
            10.0,
            max(
                -10.0,
                (
                    context.owner.buffs.Heat
                    - context.owner.debuffs.Cold
                )
                * 0.02,
            ),
        )
        net_faster = status_faster + self.speed_modifiers
        if net_faster >= 0:
            trigger_speed_multiplier = 1.0 + net_faster
        else:
            trigger_speed_multiplier = 1.0 / (1.0 + -net_faster)
        self.cooldown_progress += (
            context.battle_state.frame_delta * trigger_speed_multiplier
        )

        if self.cooldown_progress < self.cooldown_seconds:
            return False

        self.cooldown_progress -= self.cooldown_seconds
        return True


class AfterTimeTrigger(CooldownTrigger):
    def __init__(self, delay_seconds: float):
        super().__init__(cooldown_seconds=delay_seconds)
        self.has_triggered = False
        self.has_triggered_locked_false = False

    def lock_has_triggered_false(self) -> None:
        self.has_triggered = False
        self.has_triggered_locked_false = True

    def update(self, context: BattleContext) -> bool:
        if self.has_triggered:
            return False
        if not super().update(context):
            return False

        if not self.has_triggered_locked_false:
            self.has_triggered = True
        return True


class FoodCooldownTrigger(CooldownTrigger):
    def __init__(self, cooldown_seconds: float):
        super().__init__(cooldown_seconds)
        self.qualifying_food_count: int | None = None

    def prepare_speed_modifiers(self, context: BattleContext) -> None:
        if self.qualifying_food_count is None:
            qualifying_food_count = 0
            for linked_key in context.item.linked_items:
                linked_item = context.owner.items[linked_key]
                if "Food" not in linked_item.item_types:
                    continue
                if linked_item.item_id == context.item.item_id:
                    continue
                qualifying_food_count += 1
            self.qualifying_food_count = qualifying_food_count
        self.stack_speed_modifier(self.qualifying_food_count * 0.10)
        return


class ItemAcceleratedCooldownTrigger(CooldownTrigger):
    FILTER_KEYS = ("class", "rarity", "item_type", "icon_type")
    ALLOWED_KEYS = frozenset((*FILTER_KEYS, "accelerate"))

    def __init__(
        self,
        cooldown_seconds: float,
        acceleration_conditions: list[dict[str, object]],
    ):
        super().__init__(cooldown_seconds)
        if type(acceleration_conditions) is not list:
            raise ValueError("acceleration conditions must be a list")

        validated_conditions: list[dict[str, object]] = []
        for condition in acceleration_conditions:
            if type(condition) is not dict:
                raise ValueError(
                    "each acceleration condition must be a dict"
                )
            if not set(condition).issubset(self.ALLOWED_KEYS):
                raise ValueError(
                    "acceleration condition contains an unknown field"
                )
            for key in self.FILTER_KEYS:
                if key in condition and (
                    type(condition[key]) is not str or not condition[key]
                ):
                    raise ValueError(
                        "acceleration filter values must be non-empty strings"
                    )

            accelerate = condition.get("accelerate")
            if (
                isinstance(accelerate, bool)
                or not isinstance(accelerate, (int, float))
                or accelerate < 0
            ):
                raise ValueError(
                    "acceleration must be a non-negative number"
                )

            copied_condition = dict(condition)
            copied_condition["accelerate"] = float(accelerate)
            validated_conditions.append(copied_condition)

        self.acceleration_conditions = validated_conditions
        self.item_acceleration: float | None = None

    def _matches_condition(
        self,
        linked_item: BattleItem,
        condition: dict[str, object],
    ) -> bool:
        if (
            "class" in condition
            and condition["class"] not in linked_item.item_classes
        ):
            return False
        if (
            "rarity" in condition
            and condition["rarity"] != linked_item.rarity
        ):
            return False
        if (
            "item_type" in condition
            and condition["item_type"] not in linked_item.item_types
        ):
            return False
        if (
            "icon_type" in condition
            and condition["icon_type"] not in linked_item.icon_types
        ):
            return False
        return True

    def prepare_speed_modifiers(self, context: BattleContext) -> None:
        if self.item_acceleration is None:
            item_acceleration = 0.0
            for linked_key in context.item.linked_items:
                linked_item = context.owner.items[linked_key]
                for condition in self.acceleration_conditions:
                    if self._matches_condition(linked_item, condition):
                        item_acceleration += condition["accelerate"]
            self.item_acceleration = item_acceleration

        self.stack_speed_modifier(self.item_acceleration)


class StaminaConsumptionEffect(Effect):
    def __init__(self, stamina_cost: float):
        self.stamina_cost = stamina_cost

    def apply(self, context: BattleContext) -> bool:
        if context.owner.stamina < self.stamina_cost:
            return False

        context.owner.stamina -= self.stamina_cost
        return True


class HealEffect(Effect):
    def __init__(self, amount: int):
        if type(amount) is not int or amount < 0:
            raise ValueError("healing amount must be a non-negative int")
        self.amount = amount

    def apply(self, context: BattleContext) -> bool:
        actual_healing = context.battle_state.heal(
            context.owner,
            self.amount,
        )
        return actual_healing > 0


class HolyLinkedHealEffect(HealEffect):
    def __init__(self, base_amount: int, amount_per_holy: int):
        super().__init__(base_amount)
        if type(amount_per_holy) is not int or amount_per_holy < 0:
            raise ValueError(
                "healing amount per holy item must be a non-negative int"
            )

        self.base_amount = base_amount
        self.amount_per_holy = amount_per_holy
        self.qualifying_holy_count: int | None = None
        self.amount_prepared = False

    def prepare_amount(self, context: BattleContext) -> None:
        if self.qualifying_holy_count is None:
            self.qualifying_holy_count = sum(
                1
                for linked_key in context.item.linked_items
                if context.owner.items[linked_key] is not context.item
                and "holy" in context.owner.items[linked_key].icon_types
            )

        self.amount = (
            self.base_amount
            + self.qualifying_holy_count * self.amount_per_holy
        )

    def apply(self, context: BattleContext) -> bool:
        if not self.amount_prepared:
            self.prepare_amount(context)
            self.amount_prepared = True
        return super().apply(context)


class RegenerateStaminaEffect(Effect):
    def __init__(self, amount: float):
        if (
            isinstance(amount, bool)
            or not isinstance(amount, (int, float))
            or amount < 0
        ):
            raise ValueError(
                "regenerated stamina must be a non-negative number"
            )
        self.amount = float(amount)

    def apply(self, context: BattleContext) -> bool:
        old_stamina = context.owner.stamina
        context.owner.stamina = min(
            context.owner.max_stamina,
            old_stamina + self.amount,
        )
        return context.owner.stamina > old_stamina


class GainBlockEffect(Effect):
    def __init__(self, amount: int):
        if type(amount) is not int or amount < 0:
            raise ValueError("block amount must be a non-negative int")
        self.amount = amount

    def apply(self, context: BattleContext) -> bool:
        old_block = context.owner.block
        context.owner.block = old_block + self.amount
        return context.owner.block > old_block


class RemoveOpponentBlockEffect(Effect):
    def __init__(self, amount: int):
        if type(amount) is not int or amount < 0:
            raise ValueError(
                "removed block amount must be a non-negative int"
            )
        self.amount = amount

    def apply(self, context: BattleContext) -> bool:
        actual_removal = min(context.opponent.block, self.amount)
        context.opponent.block -= actual_removal
        return actual_removal > 0


class GainBuffEffect(Effect):
    def __init__(self, buff_name: str, amount: int):
        if (
            type(buff_name) is not str
            or buff_name not in BuffSlot.__annotations__
        ):
            raise ValueError("unsupported buff name")
        if type(amount) is not int or amount < 0:
            raise ValueError(
                "gained buff amount must be a non-negative int"
            )
        self.buff_name = buff_name
        self.amount = amount

    def apply(self, context: BattleContext) -> bool:
        old_stacks = getattr(context.owner.buffs, self.buff_name)
        application = self.amount
        setattr(
            context.owner.buffs,
            self.buff_name,
            old_stacks + application,
        )
        return application > 0


class UseBuffEffect(Effect):
    def __init__(self, buff_name: str, amount: int):
        if (
            type(buff_name) is not str
            or buff_name not in BuffSlot.__annotations__
        ):
            raise ValueError("unsupported buff name")
        if type(amount) is not int or amount < 0:
            raise ValueError(
                "used buff amount must be a non-negative int"
            )
        self.buff_name = buff_name
        self.amount = amount

    def apply(self, context: BattleContext) -> bool:
        available = getattr(context.owner.buffs, self.buff_name)
        if available < self.amount:
            return False

        setattr(
            context.owner.buffs,
            self.buff_name,
            available - self.amount,
        )
        return True


class BuffRemovalEffect(Effect):
    def __init__(self, buff_name: str, amount: int):
        if (
            type(buff_name) is not str
            or buff_name not in BuffSlot.__annotations__
        ):
            raise ValueError("unsupported buff name")
        if type(amount) is not int or amount < 0:
            raise ValueError(
                "removed buff amount must be a non-negative int"
            )
        self.buff_name = buff_name
        self.amount = amount

    def apply(self, context: BattleContext) -> bool:
        old_stacks = getattr(
            context.opponent.buffs,
            self.buff_name,
        )
        removal = self.amount
        # Future modifiers and removal protection can adjust removal here.
        actual_removal = min(old_stacks, removal)
        setattr(
            context.opponent.buffs,
            self.buff_name,
            old_stacks - actual_removal,
        )
        return actual_removal > 0


class InflictDebuffEffect(Effect):
    def __init__(self, debuff_name: str, amount: int):
        if (
            type(debuff_name) is not str
            or debuff_name not in DebuffSlot.__annotations__
        ):
            raise ValueError("unsupported debuff name")
        if type(amount) is not int or amount < 0:
            raise ValueError(
                "inflicted debuff amount must be a non-negative int"
            )
        self.debuff_name = debuff_name
        self.amount = amount

    def apply(self, context: BattleContext) -> bool:
        old_stacks = getattr(
            context.opponent.debuffs,
            self.debuff_name,
        )
        application = self.amount
        # Future duplicate, resist, and reflect modifiers can adjust this.
        setattr(
            context.opponent.debuffs,
            self.debuff_name,
            old_stacks + application,
        )
        return application > 0


class CleanseDebuffEffect(Effect):
    def __init__(self, debuff_name: str, amount: int):
        if (
            type(debuff_name) is not str
            or debuff_name not in DebuffSlot.__annotations__
        ):
            raise ValueError("unsupported debuff name")
        if type(amount) is not int or amount < 0:
            raise ValueError(
                "cleansed debuff amount must be a non-negative int"
            )
        self.debuff_name = debuff_name
        self.amount = amount

    def apply(self, context: BattleContext) -> bool:
        old_stacks = getattr(
            context.owner.debuffs,
            self.debuff_name,
        )
        cleansing = self.amount
        actual_cleansing = min(old_stacks, cleansing)
        setattr(
            context.owner.debuffs,
            self.debuff_name,
            old_stacks - actual_cleansing,
        )
        return actual_cleansing > 0


class AttackEffect(Effect):
    def __init__(
        self,
        min_damage: int,
        max_damage: int,
        accuracy: float,
    ):
        if min_damage < 0:
            raise ValueError("minimum damage cannot be negative")
        if max_damage < min_damage:
            raise ValueError("maximum damage cannot be below minimum damage")
        # Some items can have more than 100% accuracy.
        self.min_damage = min_damage
        self.max_damage = max_damage
        self.accuracy = accuracy
        self.damage_modifier: int = 0
        self.damage_modifier_prepared: bool = False

    def apply(
        self,
        context: BattleContext,
        attack_type: str,
    ) -> bool:
        if attack_type not in SUPPORTED_ATTACK_TYPES:
            raise ValueError(f"unsupported attack type: {attack_type}")
        if not self.damage_modifier_prepared:
            self.prepare_damage_modifier(context)
            self.damage_modifier_prepared = True

        damage = self.damage_modifier
        accuracy = self.accuracy
        if "Weapon" in context.item.item_types:
            damage += context.owner.buffs.Empower
            accuracy += (
                context.owner.buffs.Luck - context.owner.debuffs.Blind
            ) * 5

        event = AttackEvent(
            attacker=context.owner,
            defender=context.opponent,
            source_item=context.item,
            attack_types=(attack_type,),
            min_damage=self.min_damage + damage,
            max_damage=self.max_damage + damage,
            accuracy=accuracy,
        )
        resolved_event = context.battle_state.resolve_attack(event)
        return resolved_event.hit is True

    def stack_damage_modifier(self, amount: int) -> None:
        self.damage_modifier += amount

    def prepare_damage_modifier(self, context: BattleContext) -> None:
        pass


class LinkedWeaponDamageEffect(Effect):
    def __init__(self, amount: int):
        if type(amount) is not int or amount < 0:
            raise ValueError(
                "linked weapon damage must be a non-negative int"
            )
        self.amount = amount

    def apply(self, context: BattleContext) -> bool:
        modified_attack = False
        for linked_key in context.item.linked_items:
            linked_item = context.owner.items[linked_key]
            if "Weapon" not in linked_item.item_types:
                continue

            for effect in linked_item.effects:
                if not isinstance(effect, AttackEffect):
                    continue
                effect.stack_damage_modifier(self.amount)
                modified_attack = True

        return modified_attack


class FoodLinkedMeleeAttackEffect(AttackEffect):
    def __init__(
        self,
        min_damage: int,
        max_damage: int,
        accuracy: float,
        damage_per_food: int,
    ):
        super().__init__(
            min_damage=min_damage,
            max_damage=max_damage,
            accuracy=accuracy,
        )
        if type(damage_per_food) is not int or damage_per_food < 0:
            raise ValueError(
                "damage per food must be a non-negative int"
            )
        self.damage_per_food = damage_per_food
        self.qualifying_food_count: int | None = None

    def prepare_damage_modifier(self, context: BattleContext) -> None:
        if self.qualifying_food_count is None:
            qualifying_food_count = 0
            for linked_key in context.item.linked_items:
                linked_item = context.owner.items[linked_key]
                if "Food" in linked_item.item_types:
                    qualifying_food_count += 1
            self.qualifying_food_count = qualifying_food_count

        damage = self.qualifying_food_count * self.damage_per_food
        self.stack_damage_modifier(damage)


class AttackMissTrigger(Trigger):
    attack_phase = ATTACK_PHASE_ON_ATTACK_MISSED

    def update(self, context: BattleContext) -> bool:
        if not isinstance(context, AttackReactionContext):
            return False
        if context.attack_phase != self.attack_phase:
            return False
        return context.attack_event.hit is False


class OnAttackedTrigger(Trigger):
    attack_phase = ATTACK_PHASE_ON_ATTACKED

    def __init__(
        self,
        attack_types: tuple[str, ...],
        chance: float = 1.0,
    ):
        if not attack_types:
            raise ValueError("on-attacked trigger requires an attack type")
        if any(
            attack_type not in SUPPORTED_ATTACK_TYPES
            for attack_type in attack_types
        ):
            raise ValueError("unsupported attack type")
        if not 0 <= chance <= 1:
            raise ValueError("chance must be between 0 and 1")

        self.attack_types = tuple(attack_types)
        self.chance = chance

    def update(self, context: BattleContext) -> bool:
        if not isinstance(context, AttackReactionContext):
            return False
        if context.attack_phase != self.attack_phase:
            return False

        event = context.attack_event
        if event.hit is not True:
            return False
        if not any(
            attack_type in event.attack_types
            for attack_type in self.attack_types
        ):
            return False
        return context.battle_state.rng.random() < self.chance


class PreventAttackDamageEffect(Effect):
    def __init__(self, amount: int):
        if amount < 0:
            raise ValueError("prevented damage cannot be negative")
        self.amount = amount

    def apply(self, context: BattleContext) -> bool:
        if not isinstance(context, AttackReactionContext):
            raise ValueError("prevent attack damage requires an attack context")
        if context.attack_phase != ATTACK_PHASE_ON_ATTACKED:
            raise ValueError("prevent attack damage requires on-attacked phase")

        event = context.attack_event
        if event.is_resolved:
            raise ValueError("cannot change a resolved attack event")
        if event.pending_damage < 0:
            raise ValueError("pending attack damage cannot be negative")

        prevented_damage = min(self.amount, event.pending_damage)
        event.pending_damage -= prevented_damage
        event.prevented_damage += prevented_damage
        return prevented_damage > 0


class RemoveOpponentStaminaEffect(Effect):
    def __init__(self, amount: float):
        if amount < 0:
            raise ValueError("removed stamina cannot be negative")
        self.amount = amount

    def apply(self, context: BattleContext) -> bool:
        old_stamina = context.opponent.stamina
        context.opponent.stamina = max(0.0, old_stamina - self.amount)
        return context.opponent.stamina != old_stamina


class PocketSand(BattleItem):
    item_id = "pocket_sand"
    display_name = "Pocket Sand"
    item_classes = ("Neutral",)
    rarity = "Common"
    cost = 2
    item_types = ("Accessory",)
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
            triggers=[StartOfBattleTrigger()],
            effects=[InflictDebuffEffect("Blind", 1)],
        )

    def run_effect(
        self,
        trigger_results: list[bool],
        context: BattleContext,
    ) -> None:
        if trigger_results[0]:
            self.effects[0].apply(context)


class HealingHerbs(BattleItem):
    item_id = "healing_herbs"
    display_name = "Healing Herbs"
    item_classes = ("Neutral",)
    rarity = "Common"
    cost = 4
    item_types = ("Accessory",)
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
            triggers=[StartOfBattleTrigger()],
            effects=[GainBuffEffect("Regeneration", 2)],
        )

    def run_effect(
        self,
        trigger_results: list[bool],
        context: BattleContext,
    ) -> None:
        if trigger_results[0]:
            self.effects[0].apply(context)


class Flame(BattleItem):
    item_id = "flame"
    display_name = "Flame"
    item_classes = ("Pyromancer",)
    rarity = "Common"
    cost = 1
    item_types = ("Accessory",)
    icon_types = ("fire",)
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
            triggers=[StartOfBattleTrigger()],
            effects=[GainBuffEffect("Heat", 1)],
        )

    def run_effect(
        self,
        trigger_results: list[bool],
        context: BattleContext,
    ) -> None:
        if trigger_results[0]:
            self.effects[0].apply(context)


class WalrusTusk(BattleItem):
    item_id = "walrus_tusk"
    display_name = "Walrus Tusk"
    item_classes = ("Neutral",)
    rarity = "Common"
    cost = 4
    item_types = ("Accessory",)
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
            triggers=[StartOfBattleTrigger()],
            effects=[GainBuffEffect("Spikes", 1)],
        )

    def run_effect(
        self,
        trigger_results: list[bool],
        context: BattleContext,
    ) -> None:
        if trigger_results[0]:
            self.effects[0].apply(context)


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


class Whetstone(BattleItem):
    item_id = "whetstone"
    display_name = "Whetstone"
    item_classes = ("Neutral",)
    rarity = "Common"
    cost = 4
    item_types = ("Accessory",)
    icon_types = ()
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
            triggers=[StartOfBattleTrigger()],
            effects=[LinkedWeaponDamageEffect(amount=1)],
        )

    def run_effect(
        self,
        trigger_results: list[bool],
        context: BattleContext,
    ) -> None:
        if trigger_results[0]:
            self.effects[0].apply(context)


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
                LinkedItemActivationCountTrigger(
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
            ],
            effects=[
                PreventAttackDamageEffect(amount=7),
                RemoveOpponentStaminaEffect(amount=0.3),
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
        self.effects[1].apply(context)
        self.emit_activation(context)


class Broom(BattleItem):
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
            triggers=[
                CooldownTrigger(cooldown_seconds=1.7),
                AttackMissTrigger(),
            ],
            effects=[
                StaminaConsumptionEffect(stamina_cost=1.2),
                AttackEffect(
                    min_damage=2,
                    max_damage=4,
                    accuracy=95,
                ),
                InflictDebuffEffect(
                    debuff_name="Blind",
                    amount=1,
                ),
            ],
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
        if not trigger_results[0]:
            return
        if not self.effects[0].apply(context):
            return
        hit = self.effects[1].apply(context, "melee")
        if hit:
            if self.miss_damage_bonus > 0:
                self.effects[1].stack_damage_modifier(
                    -self.miss_damage_bonus
                )
                self.miss_damage_bonus = 0
            if context.battle_state.rng.random() < 0.33:
                self.effects[2].apply(context)
        self.emit_activation(context)


class WoodenSword(BattleItem):
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
            triggers=[CooldownTrigger(cooldown_seconds=1.4)],
            effects=[
                StaminaConsumptionEffect(stamina_cost=1.0),
                AttackEffect(
                    min_damage=1,
                    max_damage=3,
                    accuracy=90,
                ),
            ],
        )

    def run_effect(
        self,
        trigger_results: list[bool],
        context: BattleContext,
    ) -> None:
        if not trigger_results[0]:
            return
        if not self.effects[0].apply(context):
            return
        self.effects[1].apply(context, "melee")
        self.emit_activation(context)


class Shortbow(BattleItem):
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
            triggers=[CooldownTrigger(cooldown_seconds=1.7)],
            effects=[
                StaminaConsumptionEffect(stamina_cost=0.7),
                AttackEffect(
                    min_damage=2,
                    max_damage=3,
                    accuracy=85,
                ),
            ],
        )

    def run_effect(
        self,
        trigger_results: list[bool],
        context: BattleContext,
    ) -> None:
        if not trigger_results[0]:
            return
        if not self.effects[0].apply(context):
            return
        self.effects[1].apply(context, "ranged")
        self.emit_activation(context)


class Stone(BattleItem):
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
            triggers=[AfterTimeTrigger(delay_seconds=2.5)],
            effects=[
                AttackEffect(
                    min_damage=2,
                    max_damage=4,
                    accuracy=70,
                ),
                RemoveOpponentBlockEffect(amount=4),
            ],
        )

    def run_effect(
        self,
        trigger_results: list[bool],
        context: BattleContext,
    ) -> None:
        if not trigger_results[0]:
            return
        hit = self.effects[0].apply(context, "ranged")
        if hit:
            self.effects[1].apply(context)
        self.emit_activation(context)


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

    def run_effect(
        self,
        trigger_results: list[bool],
        context: BattleContext,
    ) -> None:
        if not trigger_results[0]:
            return
        self.effects[0].apply(context)
        if context.battle_state.rng.random() < 0.30:
            self.effects[1].apply(context)
        self.emit_activation(context)


class Pan(BattleItem):
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
            triggers=[CooldownTrigger(cooldown_seconds=2.2)],
            effects=[
                StaminaConsumptionEffect(stamina_cost=2.0),
                FoodLinkedMeleeAttackEffect(
                    min_damage=5,
                    max_damage=6,
                    accuracy=85,
                    damage_per_food=1,
                ),
            ],
        )

    def run_effect(
        self,
        trigger_results: list[bool],
        context: BattleContext,
    ) -> None:
        if not trigger_results[0]:
            return
        if not self.effects[0].apply(context):
            return
        self.effects[1].apply(context, "melee")
        self.emit_activation(context)


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
            triggers=[
                ItemAcceleratedCooldownTrigger(
                    cooldown_seconds=3.3,
                    acceleration_conditions=[
                        {
                            "item_type": "Pet",
                            "accelerate": 0.15,
                        },
                        {
                            "item_type": "Food",
                            "accelerate": 0.15,
                        },
                    ],
                )
            ],
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

    def run_effect(
        self,
        trigger_results: list[bool],
        context: BattleContext,
    ) -> None:
        if not trigger_results[0]:
            return
        if not self.effects[0].apply(context, "effect"):
            self.emit_activation(context)
            return
        if context.battle_state.rng.random() < 0.75:
            self.effects[1].apply(context)
        if context.battle_state.rng.random() < 0.10:
            self.effects[2].apply(context)
        self.emit_activation(context)


DEFAULT_ITEM_FACTORIES = {
    "banana": Banana,
    "broom": Broom,
    "flame": Flame,
    "garlic": Garlic,
    "goobling": Goobling,
    "healing_herbs": HealingHerbs,
    "pan": Pan,
    "pocket_sand": PocketSand,
    "rat": Rat,
    "shiny_shell": ShinyShell,
    "shortbow": Shortbow,
    "stone": Stone,
    "walrus_tusk": WalrusTusk,
    "whetstone": Whetstone,
    "wooden_buckler": WoodenBuckler,
    "wooden_sword": WoodenSword,
}
