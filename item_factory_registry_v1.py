from battle_module_v1 import BattleContext, BattleItem, BuffSlot
from item_effects_v1 import (
    AttackEffect,
    BuffRemovalEffect,
    FoodLinkedMeleeAttackEffect,
    GainBlockEffect,
    GainBuffEffect,
    GainMaxHealthEffect,
    HealEffect,
    HolyLinkedHealEffect,
    InflictDebuffEffect,
    LinkedWeaponDamageEffect,
    PreventAttackDamageEffect,
    RegenerateStaminaEffect,
    RemoveOpponentBlockEffect,
    RemoveOpponentStaminaEffect,
    StaminaConsumptionEffect,
    UseBuffEffect,
)
from item_triggers_v1 import (
    ActivationTrigger,
    AfterTimeTrigger,
    AttackMissTrigger,
    CooldownTrigger,
    FoodCooldownTrigger,
    ItemAcceleratedCooldownTrigger,
    OnAttackedTrigger,
    SlimeActivationTrigger,
    StartOfBattleTrigger,
)


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

    def _least_resource_name(self, buffs: BuffSlot) -> str:
        return min(
            self.RESOURCE_NAMES,
            key=lambda resource_name: getattr(buffs, resource_name),
        )

    def _most_resource_name(self, buffs: BuffSlot) -> str:
        return max(
            self.RESOURCE_NAMES,
            key=lambda resource_name: getattr(buffs, resource_name),
        )

    def run_effect(
        self,
        trigger_results: list[bool],
        context: BattleContext,
    ) -> None:
        if not trigger_results[0]:
            return

        buffs = context.owner.buffs
        least_resource = self._least_resource_name(buffs)
        self._gain_effects_by_name[least_resource].apply(context)

        if max(
            getattr(buffs, resource_name)
            for resource_name in self.RESOURCE_NAMES
        ) >= 10:
            most_resource = self._most_resource_name(buffs)
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

    def run_effect(
        self,
        trigger_results: list[bool],
        context: BattleContext,
    ) -> None:
        if not trigger_results[0]:
            return
        if not self.effects[0].apply(context):
            return

        self._prepare_spell_weight(context)
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

    def run_effect(
        self,
        trigger_results: list[bool],
        context: BattleContext,
    ) -> None:
        if not trigger_results[0]:
            return

        self._prepare_neutral_item_count(context)
        chance = min(
            1.0,
            self.BASE_CHANCE
            + self.neutral_item_count * self.CHANCE_PER_NEUTRAL,
        )
        roll = context.battle_state.rng.random()
        success = roll < chance
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
        hit = self.effects[1].apply(context, "melee")
        if hit:
            if self.miss_damage_bonus > 0:
                consumed_bonus = self.miss_damage_bonus
                self.effects[1].stack_damage_modifier(
                    -self.miss_damage_bonus
                )
                self.miss_damage_bonus = 0
                context.battle_state.record_log(
                    self,
                    {
                        "action": "consume_miss_damage_bonus",
                        "miss_damage_bonus_delta": -consumed_bonus,
                        "damage_modifier_delta": -consumed_bonus,
                    },
                )
            blind_roll = context.battle_state.rng.random()
            blind_success = blind_roll < 0.33
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
        removal_roll = context.battle_state.rng.random()
        removal_success = removal_roll < 0.30
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
        poison_roll = context.battle_state.rng.random()
        poison_success = poison_roll < 0.75
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
        blind_roll = context.battle_state.rng.random()
        blind_success = blind_roll < 0.10
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
