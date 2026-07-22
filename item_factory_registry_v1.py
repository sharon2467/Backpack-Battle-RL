from battle_module_v1 import (
    ATTACK_PHASE_ON_ATTACKED,
    AttackEvent,
    AttackReactionContext,
    BattleContext,
    BattleItem,
    Effect,
    Trigger,
)

SUPPORTED_ATTACK_TYPES = ("melee", "ranged", "effect")


class CooldownTrigger(Trigger):
    def __init__(self, cooldown_seconds: float):
        self.cooldown_seconds = cooldown_seconds
        self.cooldown_progress = 0.0

    def update(self, context: BattleContext) -> bool:
        net_heat_stacks = context.owner.buffs.Heat - context.owner.debuffs.Cold
        if net_heat_stacks >= 0:
            trigger_speed_multiplier = 1.0 + net_heat_stacks * 0.02
        else:
            trigger_speed_multiplier = 1.0 / (1.0 + -net_heat_stacks * 0.02)
        self.cooldown_progress += (
            context.battle_state.frame_delta * trigger_speed_multiplier
        )

        if self.cooldown_progress < self.cooldown_seconds:
            return False

        self.cooldown_progress -= self.cooldown_seconds
        return True


class StaminaConsumptionEffect(Effect):
    def __init__(self, stamina_cost: float):
        self.stamina_cost = stamina_cost

    def apply(self, context: BattleContext) -> bool:
        if context.owner.stamina < self.stamina_cost:
            return False

        context.owner.stamina -= self.stamina_cost
        return True


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

    def apply(self, context: BattleContext) -> bool:
        event = AttackEvent(
            attacker=context.owner,
            defender=context.opponent,
            source_item=context.item,
            attack_types=("melee",),
            min_damage=self.min_damage + context.owner.buffs.Empower,
            max_damage=self.max_damage + context.owner.buffs.Empower,
            accuracy=self.accuracy
            + (context.owner.buffs.Luck - context.owner.debuffs.Blind) * 5,
        )
        resolved_event = context.battle_state.resolve_attack(event)
        return resolved_event.hit is True


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

    def run_own_effect(
        self,
        trigger_results: list[bool],
        context: BattleContext,
    ) -> bool:
        if not trigger_results[0]:
            return False
        self.effects[0].apply(context)
        self.effects[1].apply(context)
        return True


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

    def run_own_effect(
        self,
        trigger_results: list[bool],
        context: BattleContext,
    ) -> bool:
        if not trigger_results[0]:
            return False
        if not self.effects[0].apply(context):
            return False
        return self.effects[1].apply(context)


DEFAULT_ITEM_FACTORIES = {
    "wooden_buckler": WoodenBuckler,
    "wooden_sword": WoodenSword,
}
