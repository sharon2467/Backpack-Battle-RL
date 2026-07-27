from battle_module_v1 import (
    ATTACK_PHASE_ON_ATTACKED,
    ATTACK_PHASE_ON_ATTACK_MISSED,
    ITEM_ACTIVATION_PHASE_LINKED,
    ITEM_MARKER_TYPES,
    AttackReactionContext,
    BattleContext,
    BattleItem,
    ItemActivationContext,
    Trigger,
)
from item_effects_v1 import SUPPORTED_ATTACK_TYPES


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


class ActivationTrigger(Trigger):
    item_activation_phase = ITEM_ACTIVATION_PHASE_LINKED

    def __init__(self, marker_type: str = "star"):
        if marker_type not in ITEM_MARKER_TYPES:
            raise ValueError(f"unsupported marker type: {marker_type}")
        self.marker_type = marker_type

    def update(self, context: BattleContext) -> bool:
        if not isinstance(context, ItemActivationContext):
            return False
        if context.source_item.player_id != context.item.player_id:
            return False
        return (
            context.source_item.item_key
            in context.item.marker_items[self.marker_type]
        )


class SlimeActivationTrigger(ActivationTrigger):
    def __init__(self, required_activations: int):
        super().__init__(marker_type="star")
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
        if not super().update(context):
            return False

        self.activation_count += 1
        triggered = self.activation_count >= self.required_activations
        activation_count_delta = 1
        if triggered:
            self.activation_count -= self.required_activations
            activation_count_delta -= self.required_activations

        context.battle_state.record_log(
            context.item,
            {
                "action": "count_linked_item_activation",
                "source_item_key": getattr(
                    context.source_item,
                    "item_key",
                    None,
                ),
                "source_item_id": getattr(
                    context.source_item,
                    "item_id",
                    None,
                ),
                "required": self.required_activations,
                "triggered": triggered,
                "activation_count_delta": activation_count_delta,
            },
        )
        return triggered


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
        roll = context.battle_state.rng.random()
        success = roll < self.chance
        context.battle_state.record_log(
            context.item,
            {
                "action": "on_attacked_check",
                "chance": self.chance,
                "roll": roll,
                "success": success,
                "attacker_player_id": event.attacker.player_id,
                "defender_player_id": event.defender.player_id,
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
                "attack_types": list(event.attack_types),
            },
        )
        return success
