from battle_module_v1 import (
    ATTACK_PHASE_ON_ATTACKED,
    ATTACK_PHASE_ON_ATTACK_MISSED,
    AttackEvent,
    AttackReactionContext,
    BattleContext,
    BattleItem,
    BuffSlot,
    DebuffSlot,
    Effect,
    Trigger,
)

SUPPORTED_ATTACK_TYPES = ("melee", "ranged", "effect")


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
        faster = context.owner.buffs.Heat * 0.02
        slower = context.owner.debuffs.Cold * 0.02
        net_faster = faster - slower + self.speed_modifiers
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
        old_health = context.owner.health
        context.owner.health = min(
            context.owner.max_health,
            old_health + self.amount,
        )
        return context.owner.health > old_health


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


class MeleeAttackEffect(Effect):
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

    def apply(self, context: BattleContext) -> bool:
        if not self.damage_modifier_prepared:
            self.prepare_damage_modifier(context)
            self.damage_modifier_prepared = True

        damage = self.damage_modifier
        damage += context.owner.buffs.Empower
        event = AttackEvent(
            attacker=context.owner,
            defender=context.opponent,
            source_item=context.item,
            attack_types=("melee",),
            min_damage=self.min_damage + damage,
            max_damage=self.max_damage + damage,
            accuracy=self.accuracy
            + (context.owner.buffs.Luck - context.owner.debuffs.Blind) * 5,
        )
        resolved_event = context.battle_state.resolve_attack(event)
        return resolved_event.hit is True

    def stack_damage_modifier(self, amount: int) -> None:
        self.damage_modifier += amount

    def prepare_damage_modifier(self, context: BattleContext) -> None:
        pass


class FoodLinkedMeleeAttackEffect(MeleeAttackEffect):
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
                MeleeAttackEffect(
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
            return
        if not trigger_results[0]:
            return
        if not self.effects[0].apply(context):
            return
        if not self.effects[1].apply(context):
            return

        if self.miss_damage_bonus > 0:
            self.effects[1].stack_damage_modifier(
                -self.miss_damage_bonus
            )
            self.miss_damage_bonus = 0
        if context.battle_state.rng.random() < 0.33:
            self.effects[2].apply(context)


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
                MeleeAttackEffect(
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
        self.effects[1].apply(context)


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
        self.effects[1].apply(context)


DEFAULT_ITEM_FACTORIES = {
    "banana": Banana,
    "broom": Broom,
    "garlic": Garlic,
    "pan": Pan,
    "wooden_buckler": WoodenBuckler,
    "wooden_sword": WoodenSword,
}
