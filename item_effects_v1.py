from __future__ import annotations

import math
from typing import TYPE_CHECKING

from battle_module_v1 import (
    ATTACK_PHASE_PRE_TAKE_DAMAGE,
    AttackEvent,
    make_attack_event,
    AttackReactionContext,
    BattleContext,
    BuffSlot,
    DebuffSlot,
    LogHandle,
    StackResult,
    godot_round,
)

if TYPE_CHECKING:
    from item_factory_registry_v1 import BattleItem

SUPPORTED_ATTACK_TYPES = ("melee", "ranged", "effect" ,"self_damage","unhealing","spikes","poison","fatigue")

class Effect:
    def apply(self, context:BattleContext)->bool:
        raise NotImplementedError("concrete effects must implement apply")
    def __init__(self):
        self.item:BattleItem|None = None


class StaminaConsumptionEffect(Effect):
    def __init__(self, stamina_cost: float):
        super().__init__()
        self.stamina_cost = stamina_cost

    def apply(self, context: BattleContext) -> bool:
        stamina_before = context.owner.stamina
        success = stamina_before >= self.stamina_cost
        if not success:
            context.battle_state.record_log(
                context.item,
                {
                    "action": "spend_stamina",
                    "target_player_id": context.owner.player_id,
                    "stamina_spent": 0.0,
                    "success": False,
                },
            )
            return False

        context.owner.stamina -= self.stamina_cost
        context.battle_state.record_log(
            context.item,
            {
                "action": "spend_stamina",
                "target_player_id": context.owner.player_id,
                "stamina_spent": self.stamina_cost,
                "success": True,
            },
        )
        return True


class HealEffect(Effect):
    def __init__(self, amount: int):
        super().__init__()
        if type(amount) is not int or amount < 0:
            raise ValueError("healing amount must be a non-negative int")
        self.amount = amount

    def apply(self, context: BattleContext) -> bool:
        actual_healing = context.battle_state.heal(
            context.owner,
            self.amount,
            source=context.item,
        )
        return actual_healing > 0


class GainMaxHealthEffect(Effect):
    def __init__(self, amount: int):
        super().__init__()
        if type(amount) is not int or amount <= 0:
            raise ValueError(
                "maximum health gain must be a positive int"
            )
        self.amount = amount

    def apply(
        self,
        context: BattleContext,
        *,
        trigger_log_handle: LogHandle | None = None,
    ) -> bool:
        context.owner.max_health += self.amount
        context.owner.health += self.amount
        context.battle_state.record_log(
            context.item,
            {
                "action": "gain_max_health",
                "target_player_id": context.owner.player_id,
                "max_health_gained": self.amount,
                "trigger_log_sequence": (
                    trigger_log_handle.sequence if trigger_log_handle else None
                ),
            },
        )
        return True


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
        super().__init__()
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
        actual_restoration = context.owner.stamina - old_stamina
        context.battle_state.record_log(
            context.item,
            {
                "action": "restore_stamina",
                "target_player_id": context.owner.player_id,
                "stamina_generated": self.amount,
                "final_stamina_generated": actual_restoration,
            },
        )
        return actual_restoration > 0


class GainBlockEffect(Effect):
    def __init__(self, amount: int, *, duration: float = -1.0) -> None:
        super().__init__()
        if type(amount) is not int or amount < 0:
            raise ValueError("block amount must be a non-negative int")
        self.amount = amount
        if type(duration) not in (int, float) or not math.isfinite(duration):
            raise ValueError("stack duration must be a finite int or float")
        self.duration = float(duration)

    def apply(
        self,
        context: BattleContext,
        *,
        trigger_log_handle: LogHandle | None = None,
    ) -> bool:
        power = (
            context.item.stack_powers.get("Block", 1.0)
            if context.item is not None else 1.0
        )
        scaled = godot_round(self.amount * power)
        result = StackResult(0, None)
        if scaled > 0:
            result = context.battle_state.gain_stacks(
                context.owner,
                "Block",
                scaled,
                source_item=context.item,
                trigger_log_handle=trigger_log_handle,
                duration=self.duration,
            )
        actual_gain = result.delta
        if result.event is not None:
            context.battle_state.emit_signal(
                context.item, "gave_block", result.event
            )
        context.battle_state.record_log(
            context.item,
            {
                "action": "gain_block",
                "event_kind": "effect_attempt",
                "contributes_to_stack_totals": False,
                "target_player_id": context.owner.player_id,
                "block_gained": self.amount,
                "final_block_gained": actual_gain,
                "success": actual_gain > 0,
                "trigger_log_sequence": (
                    trigger_log_handle.sequence if trigger_log_handle else None
                ),
            },
        )
        return actual_gain > 0


class RemoveOpponentBlockEffect(Effect):
    def __init__(self, amount: int):
        super().__init__()
        if type(amount) is not int or amount < 0:
            raise ValueError(
                "removed block amount must be a non-negative int"
            )
        self.amount = amount

    def apply(
        self,
        context: BattleContext,
        *,
        trigger_log_handle: LogHandle | None = None,
    ) -> bool:
        result = context.battle_state.lose_stacks(
            context.opponent,
            "Block",
            self.amount,
            source_item=context.item,
            trigger_log_handle=trigger_log_handle,
            used=False,
        )
        actual_removal = -result.delta
        context.battle_state.record_log(
            context.item,
            {
                "action": "remove_block",
                "event_kind": "effect_attempt",
                "contributes_to_stack_totals": False,
                "target_player_id": context.opponent.player_id,
                "block_removed": self.amount,
                "final_block_removed": actual_removal,
                "success": actual_removal > 0,
                "trigger_log_sequence": (
                    trigger_log_handle.sequence if trigger_log_handle else None
                ),
            },
        )
        return actual_removal > 0


class GainBuffEffect(Effect):
    def __init__(
        self, buff_name: str, amount: int, *, duration: float = -1.0
    ) -> None:
        super().__init__()
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
        if type(duration) not in (int, float) or not math.isfinite(duration):
            raise ValueError("stack duration must be a finite int or float")
        self.duration = float(duration)

    def apply(
        self,
        context: BattleContext,
        *,
        trigger_log_handle: LogHandle | None = None,
    ) -> bool:
        power = (
            context.item.stack_powers.get(self.buff_name, 1.0)
            if context.item is not None else 1.0
        )
        scaled = godot_round(self.amount * power)
        application = 0
        if scaled > 0:
            application = context.battle_state.gain_stacks(
                context.owner,
                self.buff_name,
                scaled,
                source_item=context.item,
                trigger_log_handle=trigger_log_handle,
                duration=self.duration,
            ).delta
        context.battle_state.record_log(
            context.item,
            {
                "action": "gain_buff",
                "event_kind": "effect_attempt",
                "contributes_to_stack_totals": False,
                "target_player_id": context.owner.player_id,
                "buff": self.buff_name,
                "stack_gained": self.amount,
                "final_stack_gained": application,
                "success": application > 0,
                "trigger_log_sequence": (
                    trigger_log_handle.sequence if trigger_log_handle else None
                ),
            },
        )
        return application > 0


class UseBuffEffect(Effect):
    def __init__(self, buff_name: str, amount: int):
        super().__init__()
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

    def apply(
        self,
        context: BattleContext,
        *,
        trigger_log_handle: LogHandle | None = None,
    ) -> bool:
        result = self.apply_result(context, trigger_log_handle=trigger_log_handle)
        return self.amount == 0 or result.delta == -self.amount

    def apply_result(
        self,
        context: BattleContext,
        *,
        trigger_log_handle: LogHandle | None = None,
    ) -> StackResult:
        result = context.battle_state.try_use_stacks(
            context.owner,
            self.buff_name,
            self.amount,
            source_item=context.item,
            trigger_log_handle=trigger_log_handle,
        )
        actual_used = -result.delta
        success = self.amount == 0 or result.delta == -self.amount
        context.battle_state.record_log(
            context.item,
            {
                "action": "use_buff",
                "event_kind": "effect_attempt",
                "contributes_to_stack_totals": False,
                "target_player_id": context.owner.player_id,
                "buff": self.buff_name,
                "stack_used": self.amount,
                "final_stack_used": actual_used,
                "success": success,
                "trigger_log_sequence": (
                    trigger_log_handle.sequence if trigger_log_handle else None
                ),
            },
        )
        return result


class BuffRemovalEffect(Effect):
    def __init__(self, buff_name: str, amount: int):
        super().__init__()
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

    def apply(
        self,
        context: BattleContext,
        *,
        trigger_log_handle: LogHandle | None = None,
    ) -> bool:
        result = context.battle_state.lose_stacks(
            context.opponent,
            self.buff_name,
            self.amount,
            source_item=context.item,
            trigger_log_handle=trigger_log_handle,
            used=False,
        )
        actual_removal = -result.delta
        context.battle_state.record_log(
            context.item,
            {
                "action": "remove_buff",
                "event_kind": "effect_attempt",
                "contributes_to_stack_totals": False,
                "target_player_id": context.opponent.player_id,
                "buff": self.buff_name,
                "stack_removed": self.amount,
                "final_stack_removed": actual_removal,
                "success": actual_removal > 0,
                "trigger_log_sequence": (
                    trigger_log_handle.sequence if trigger_log_handle else None
                ),
            },
        )
        return actual_removal > 0


class InflictDebuffEffect(Effect):
    def __init__(
        self, debuff_name: str, amount: int, *, duration: float = -1.0
    ) -> None:
        super().__init__()
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
        if type(duration) not in (int, float) or not math.isfinite(duration):
            raise ValueError("stack duration must be a finite int or float")
        self.duration = float(duration)

    def apply(
        self,
        context: BattleContext,
        *,
        trigger_log_handle: LogHandle | None = None,
    ) -> bool:
        power = (
            context.item.stack_powers.get(self.debuff_name, 1.0)
            if context.item is not None else 1.0
        )
        scaled = godot_round(self.amount * power)
        application = 0
        if scaled > 0:
            application = context.battle_state.gain_stacks(
                context.opponent,
                self.debuff_name,
                scaled,
                source_item=context.item,
                trigger_log_handle=trigger_log_handle,
                duration=self.duration,
            ).delta
        context.battle_state.record_log(
            context.item,
            {
                "action": "inflict_debuff",
                "event_kind": "effect_attempt",
                "contributes_to_stack_totals": False,
                "target_player_id": context.opponent.player_id,
                "debuff": self.debuff_name,
                "stack_gained": self.amount,
                "final_stack_gained": application,
                "success": application > 0,
                "trigger_log_sequence": (
                    trigger_log_handle.sequence if trigger_log_handle else None
                ),
            },
        )
        return application > 0


class CleanseDebuffEffect(Effect):
    def __init__(self, debuff_name: str, amount: int):
        super().__init__()
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

    def apply(
        self,
        context: BattleContext,
        *,
        trigger_log_handle: LogHandle | None = None,
    ) -> bool:
        result = context.battle_state.lose_stacks(
            context.owner,
            self.debuff_name,
            self.amount,
            source_item=context.item,
            trigger_log_handle=trigger_log_handle,
            used=False,
        )
        actual_cleansing = -result.delta
        context.battle_state.record_log(
            context.item,
            {
                "action": "cleanse_debuff",
                "event_kind": "effect_attempt",
                "contributes_to_stack_totals": False,
                "target_player_id": context.owner.player_id,
                "debuff": self.debuff_name,
                "stack_removed": self.amount,
                "final_stack_removed": actual_cleansing,
                "success": actual_cleansing > 0,
                "trigger_log_sequence": (
                    trigger_log_handle.sequence if trigger_log_handle else None
                ),
            },
        )
        return actual_cleansing > 0


class AttackEffect(Effect):
    def __init__(
        self,
        min_damage: int,
        max_damage: int,
        accuracy: float,
    ):
        super().__init__()
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
        attack_type: tuple[str, ...],
        *,
        trigger_log_handle: LogHandle | None = None,
    ) -> bool:
        result = self.apply_result(
            context, attack_type, trigger_log_handle=trigger_log_handle
        )
        return result.hit is True

    def apply_result(
        self,
        context: BattleContext,
        attack_type: tuple[str, ...],
        *,
        trigger_log_handle: LogHandle | None = None,
    ) -> AttackEvent:
        if (
            not isinstance(attack_type, tuple)
            or not attack_type
            or any(kind not in SUPPORTED_ATTACK_TYPES for kind in attack_type)
        ):
            raise ValueError(f"unsupported attack type: {attack_type}")
        if not self.damage_modifier_prepared:
            self.prepare_damage_modifier(context)
            self.damage_modifier_prepared = True

        damage = self.damage_modifier
        accuracy = self.accuracy
        if "Weapon" in context.item.item_types:
            accuracy += (
                context.owner.buffs.Luck - context.owner.debuffs.Blind
            ) * 5

        event = make_attack_event(
            attacker=context.owner,
            defender=context.opponent,
            source_item=context.item,
            attack_types=attack_type,
            min_damage=self.min_damage + damage,
            max_damage=self.max_damage + damage,
            accuracy=accuracy,
            trigger_log_handle=trigger_log_handle,
        )
        resolved_event = context.battle_state.resolve_attack(event)
        return resolved_event

    def stack_damage_modifier(self, amount: int) -> None:
        self.damage_modifier += amount

    def prepare_damage_modifier(self, context: BattleContext) -> None:
        pass


class LinkedWeaponDamageEffect(Effect):
    def __init__(self, amount: int):
        super().__init__()
        if type(amount) is not int or amount < 0:
            raise ValueError(
                "linked weapon damage must be a non-negative int"
            )
        self.amount = amount

    def apply(self, context: BattleContext) -> bool:
        modified_attack = False
        targets = []
        for linked_key in context.item.linked_items:
            linked_item = context.owner.items[linked_key]
            if "Weapon" not in linked_item.item_types:
                continue

            for effect_index, effect in enumerate(linked_item.effects):
                if not isinstance(effect, AttackEffect):
                    continue
                effect.stack_damage_modifier(self.amount)
                targets.append(
                    {
                        "player_id": getattr(
                            linked_item,
                            "player_id",
                            None,
                        ),
                        "item_key": getattr(
                            linked_item,
                            "item_key",
                            linked_key,
                        ),
                        "item_id": getattr(
                            linked_item,
                            "item_id",
                            None,
                        ),
                        "effect_index": effect_index,
                        "damage_modifier_delta": self.amount,
                    }
                )
                modified_attack = True

        context.battle_state.record_log(
            context.item,
            {
                "action": "modify_linked_weapon_damage",
                "targets": targets,
                "success": modified_attack,
            },
        )
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
            for linked_key in context.item.marker_items["star"]:
                linked_item = context.owner.items[linked_key]
                if "Food" in linked_item.item_types:
                    qualifying_food_count += 1
            self.qualifying_food_count = qualifying_food_count

        damage = self.qualifying_food_count * self.damage_per_food
        self.stack_damage_modifier(damage)


class PreventAttackDamageEffect(Effect):
    def __init__(self, amount: int):
        super().__init__()
        if amount < 0:
            raise ValueError("prevented damage cannot be negative")
        self.amount = amount

    def apply(self, context: BattleContext) -> bool:
        if not isinstance(context, AttackReactionContext):
            raise ValueError("prevent attack damage requires an attack context")
        if context.attack_phase != ATTACK_PHASE_PRE_TAKE_DAMAGE:
            raise ValueError("prevent attack damage requires pre-take-damage phase")

        event = context.attack_event
        if event.is_resolved:
            raise ValueError("cannot change a resolved attack event")
        if event.pending_damage < 0:
            raise ValueError("pending attack damage cannot be negative")

        prevented_damage = min(self.amount, max(0, event.pending_damage-event.prevented_damage))
        event.prevented_damage += prevented_damage
        context.battle_state.record_log(
            context.item,
            {
                "action": "prevent_attack_damage",
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
                "pending_damage": self.amount,
                "final_pending_damage": prevented_damage,
                "success": prevented_damage > 0,
            },
        )
        return prevented_damage > 0


class RemoveOpponentStaminaEffect(Effect):
    def __init__(self, amount: float):
        super().__init__()
        if amount < 0:
            raise ValueError("removed stamina cannot be negative")
        self.amount = amount

    def apply(self, context: BattleContext) -> bool:
        old_stamina = context.opponent.stamina
        context.opponent.stamina = max(0.0, old_stamina - self.amount)
        actual_removal = old_stamina - context.opponent.stamina
        context.battle_state.record_log(
            context.item,
            {
                "action": "remove_stamina",
                "target_player_id": context.opponent.player_id,
                "stamina_removed": self.amount,
                "final_stamina_removed": actual_removal,
                "success": actual_removal > 0,
            },
        )
        return actual_removal > 0
