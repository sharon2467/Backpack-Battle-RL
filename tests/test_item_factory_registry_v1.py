import unittest
from unittest.mock import Mock, call

from basic_backpack_v1 import ITEM_CATALOG
from battle_initializer_v1 import initialize_battle
from battle_module_v1 import (
    ATTACK_PHASE_ON_ATTACKED,
    ATTACK_PHASE_ON_ATTACK_MISSED,
    AttackEvent,
    AttackReactionContext,
    BattleContext,
    BattleState,
    PlayerState,
)
from item_factory_registry_v1 import (
    AttackMissTrigger,
    Banana,
    Broom,
    BuffRemovalEffect,
    CooldownTrigger,
    DEFAULT_ITEM_FACTORIES,
    FoodCooldownTrigger,
    FoodLinkedMeleeAttackEffect,
    GainBlockEffect,
    Garlic,
    HealEffect,
    InflictDebuffEffect,
    MeleeAttackEffect,
    OnAttackedTrigger,
    Pan,
    PreventAttackDamageEffect,
    RegenerateStaminaEffect,
    RemoveOpponentStaminaEffect,
    StaminaConsumptionEffect,
    WoodenBuckler,
    WoodenSword,
)


class ItemFactoryRegistryV1Test(unittest.TestCase):
    def make_context(
        self,
        frame_delta=0.1,
        health=10,
        max_health=10,
        stamina=0.0,
        max_stamina=0.0,
    ):
        owner = PlayerState(
            player_id=0,
            health=health,
            max_health=max_health,
            stamina=stamina,
            max_stamina=max_stamina,
        )
        opponent = PlayerState(player_id=1, health=10, max_health=10)
        battle_state = BattleState(
            players=[owner, opponent],
            frame_delta=frame_delta,
        )
        return BattleContext(battle_state, None, owner, opponent)

    def test_default_item_factories_is_a_registry_dict(self):
        self.assertIsInstance(DEFAULT_ITEM_FACTORIES, dict)

    def test_banana_is_registered_with_metadata_and_components(self):
        banana = DEFAULT_ITEM_FACTORIES["banana"](
            item_id="banana",
            item_key="banana1",
            player_id=0,
        )

        self.assertIsInstance(banana, Banana)
        self.assertEqual(banana.item_id, "banana")
        self.assertEqual(banana.item_key, "banana1")
        self.assertEqual(banana.player_id, 0)
        self.assertEqual(banana.display_name, "Banana")
        self.assertEqual(banana.item_classes, ("Neutral",))
        self.assertEqual(banana.rarity, "Common")
        self.assertEqual(banana.cost, 3)
        self.assertEqual(banana.item_types, ("Food",))
        self.assertEqual(banana.icon_types, ("nature",))
        self.assertTrue(banana.is_active_item)
        self.assertEqual(banana.socket_count, 0)
        self.assertEqual(len(banana.triggers), 1)
        self.assertIsInstance(banana.triggers[0], FoodCooldownTrigger)
        self.assertEqual(banana.triggers[0].cooldown_seconds, 5.0)
        self.assertIsNone(banana.triggers[0].qualifying_food_count)
        self.assertEqual(len(banana.effects), 2)
        self.assertIsInstance(banana.effects[0], HealEffect)
        self.assertEqual(banana.effects[0].amount, 4)
        self.assertIsInstance(banana.effects[1], RegenerateStaminaEffect)
        self.assertEqual(banana.effects[1].amount, 1.0)

    def test_bananas_own_independent_component_instances(self):
        first = Banana(item_key="banana1", player_id=0)
        second = Banana(item_key="banana2", player_id=0)

        self.assertIsNot(first.triggers[0], second.triggers[0])
        self.assertIsNot(first.effects[0], second.effects[0])
        self.assertIsNot(first.effects[1], second.effects[1])

        first.triggers[0].cooldown_progress = 0.5
        first.triggers[0].qualifying_food_count = 2

        self.assertEqual(second.triggers[0].cooldown_progress, 0.0)
        self.assertIsNone(second.triggers[0].qualifying_food_count)

    def test_initializer_builds_banana_as_active_item_with_deduplicated_star_link(
        self,
    ):
        battle = initialize_battle(
            [
                {
                    "player_id": 0,
                    "health": 10,
                    "max_health": 10,
                    "stamina": 5.0,
                    "max_stamina": 5.0,
                    "placements": [
                        {
                            "item_id": "banana",
                            "x": 2,
                            "y": 2,
                            "rotation": 0,
                        },
                        {
                            "item_id": "wooden_sword",
                            "x": 1,
                            "y": 2,
                            "rotation": 0,
                        },
                    ],
                },
                {
                    "player_id": 1,
                    "health": 10,
                    "max_health": 10,
                    "stamina": 5.0,
                    "max_stamina": 5.0,
                    "placements": [],
                },
            ],
            DEFAULT_ITEM_FACTORIES,
            item_catalog=ITEM_CATALOG,
        )

        banana = battle.players[0].items["banana1"]
        sword = battle.players[0].items["wooden_sword1"]

        self.assertIsInstance(banana, Banana)
        self.assertEqual(banana.linked_items, ["wooden_sword1"])
        self.assertEqual(battle.active_items, [banana, sword])

    def test_garlic_is_registered_with_metadata_and_components(self):
        garlic = DEFAULT_ITEM_FACTORIES["garlic"](
            item_id="garlic",
            item_key="garlic1",
            player_id=0,
        )

        self.assertIsInstance(garlic, Garlic)
        self.assertEqual(garlic.item_id, "garlic")
        self.assertEqual(garlic.item_key, "garlic1")
        self.assertEqual(garlic.player_id, 0)
        self.assertEqual(garlic.display_name, "Garlic")
        self.assertEqual(garlic.item_classes, ("Neutral",))
        self.assertEqual(garlic.rarity, "Common")
        self.assertEqual(garlic.cost, 2)
        self.assertEqual(garlic.item_types, ("Food",))
        self.assertEqual(garlic.icon_types, ("nature",))
        self.assertTrue(garlic.is_active_item)
        self.assertEqual(garlic.socket_count, 0)
        self.assertEqual(len(garlic.triggers), 1)
        self.assertIsInstance(garlic.triggers[0], FoodCooldownTrigger)
        self.assertEqual(garlic.triggers[0].cooldown_seconds, 4.0)
        self.assertIsNone(garlic.triggers[0].qualifying_food_count)
        self.assertEqual(len(garlic.effects), 2)
        self.assertIsInstance(garlic.effects[0], GainBlockEffect)
        self.assertEqual(garlic.effects[0].amount, 3)
        self.assertIsInstance(garlic.effects[1], BuffRemovalEffect)
        self.assertEqual(garlic.effects[1].buff_name, "Vampirism")
        self.assertEqual(garlic.effects[1].amount, 1)

    def test_garlics_own_independent_component_instances(self):
        first = Garlic(item_key="garlic1", player_id=0)
        second = Garlic(item_key="garlic2", player_id=0)

        self.assertIsNot(first.triggers[0], second.triggers[0])
        self.assertIsNot(first.effects[0], second.effects[0])
        self.assertIsNot(first.effects[1], second.effects[1])

        first.triggers[0].cooldown_progress = 0.5
        first.triggers[0].qualifying_food_count = 2

        self.assertEqual(second.triggers[0].cooldown_progress, 0.0)
        self.assertIsNone(second.triggers[0].qualifying_food_count)

    def test_initializer_builds_garlic_as_active_item_with_deduplicated_star_link(
        self,
    ):
        battle = initialize_battle(
            [
                {
                    "player_id": 0,
                    "health": 10,
                    "max_health": 10,
                    "stamina": 5.0,
                    "max_stamina": 5.0,
                    "placements": [
                        {
                            "item_id": "garlic",
                            "x": 2,
                            "y": 2,
                            "rotation": 0,
                        },
                        {
                            "item_id": "banana",
                            "x": 3,
                            "y": 2,
                            "rotation": 0,
                        },
                    ],
                },
                {
                    "player_id": 1,
                    "health": 10,
                    "max_health": 10,
                    "stamina": 5.0,
                    "max_stamina": 5.0,
                    "placements": [],
                },
            ],
            DEFAULT_ITEM_FACTORIES,
            item_catalog=ITEM_CATALOG,
        )

        garlic = battle.players[0].items["garlic1"]
        banana = battle.players[0].items["banana1"]

        self.assertIsInstance(garlic, Garlic)
        self.assertEqual(garlic.linked_items, ["banana1"])
        self.assertEqual(battle.active_items, [garlic, banana])

    def test_wooden_buckler_is_registered_with_metadata_and_components(self):
        buckler = DEFAULT_ITEM_FACTORIES["wooden_buckler"](
            item_id="wooden_buckler",
            item_key="wooden_buckler1",
            player_id=0,
        )

        self.assertIsInstance(buckler, WoodenBuckler)
        self.assertEqual(buckler.item_id, "wooden_buckler")
        self.assertEqual(buckler.item_key, "wooden_buckler1")
        self.assertEqual(buckler.player_id, 0)
        self.assertEqual(buckler.display_name, "Wooden Buckler")
        self.assertEqual(buckler.item_classes, ("Neutral",))
        self.assertEqual(buckler.rarity, "Common")
        self.assertEqual(buckler.cost, 4)
        self.assertEqual(buckler.item_types, ("Shield",))
        self.assertEqual(buckler.icon_types, ())
        self.assertFalse(buckler.is_active_item)
        self.assertEqual(buckler.socket_count, 1)
        self.assertEqual(len(buckler.triggers), 1)
        self.assertIsInstance(buckler.triggers[0], OnAttackedTrigger)
        self.assertEqual(buckler.triggers[0].attack_types, ("melee",))
        self.assertEqual(buckler.triggers[0].chance, 0.3)
        self.assertEqual(len(buckler.effects), 2)
        self.assertIsInstance(buckler.effects[0], PreventAttackDamageEffect)
        self.assertEqual(buckler.effects[0].amount, 7)
        self.assertIsInstance(buckler.effects[1], RemoveOpponentStaminaEffect)
        self.assertEqual(buckler.effects[1].amount, 0.3)

    def test_wooden_bucklers_own_independent_component_instances(self):
        first = WoodenBuckler(item_key="wooden_buckler1", player_id=0)
        second = WoodenBuckler(item_key="wooden_buckler2", player_id=0)

        self.assertIsNot(first.triggers[0], second.triggers[0])
        self.assertIsNot(first.effects[0], second.effects[0])
        self.assertIsNot(first.effects[1], second.effects[1])

    def test_initializer_builds_wooden_buckler_as_passive_reaction_item(self):
        battle = initialize_battle(
            [
                {
                    "player_id": 0,
                    "health": 10,
                    "max_health": 10,
                    "stamina": 5.0,
                    "max_stamina": 5.0,
                    "placements": [
                        {
                            "item_id": "wooden_sword",
                            "x": 0,
                            "y": 0,
                            "rotation": 0,
                        },
                    ],
                },
                {
                    "player_id": 1,
                    "health": 10,
                    "max_health": 10,
                    "stamina": 5.0,
                    "max_stamina": 5.0,
                    "placements": [
                        {
                            "item_id": "wooden_buckler",
                            "x": 0,
                            "y": 0,
                            "rotation": 0,
                        },
                    ],
                },
            ],
            DEFAULT_ITEM_FACTORIES,
            item_catalog=ITEM_CATALOG,
        )

        sword = battle.players[0].items["wooden_sword1"]
        buckler = battle.players[1].items["wooden_buckler1"]
        self.assertIsInstance(buckler, WoodenBuckler)
        self.assertEqual(battle.active_items, [sword])
        self.assertEqual(
            battle._get_attack_reaction_items(
                battle.players[1],
                ATTACK_PHASE_ON_ATTACKED,
            ),
            (buckler,),
        )

    def test_wooden_sword_is_registered_with_metadata_and_components(self):
        sword = DEFAULT_ITEM_FACTORIES["wooden_sword"](
            item_id="wooden_sword",
            item_key="wooden_sword1",
            player_id=0,
        )

        self.assertIsInstance(sword, WoodenSword)
        self.assertEqual(sword.item_id, "wooden_sword")
        self.assertEqual(sword.item_key, "wooden_sword1")
        self.assertEqual(sword.player_id, 0)
        self.assertEqual(sword.display_name, "Wooden Sword")
        self.assertEqual(sword.item_classes, ("Neutral",))
        self.assertEqual(sword.rarity, "Common")
        self.assertEqual(sword.cost, 3)
        self.assertEqual(sword.item_types, ("Weapon",))
        self.assertEqual(sword.icon_types, ("melee",))
        self.assertTrue(sword.is_active_item)
        self.assertEqual(sword.socket_count, 1)
        self.assertEqual(len(sword.triggers), 1)
        self.assertIsInstance(sword.triggers[0], CooldownTrigger)
        self.assertEqual(len(sword.effects), 2)
        self.assertIsInstance(sword.effects[0], StaminaConsumptionEffect)
        self.assertIsInstance(sword.effects[1], MeleeAttackEffect)

    def test_wooden_swords_own_independent_component_instances(self):
        first = WoodenSword(item_key="wooden_sword1", player_id=0)
        second = WoodenSword(item_key="wooden_sword2", player_id=0)

        self.assertIsNot(first.triggers[0], second.triggers[0])
        self.assertIsNot(first.effects[0], second.effects[0])
        self.assertIsNot(first.effects[1], second.effects[1])

        first.triggers[0].cooldown_progress = 0.5
        self.assertAlmostEqual(second.triggers[0].cooldown_progress, 0.0)

    def test_wooden_sword_does_not_attack_at_battle_start(self):
        rng = Mock()
        sword, context = self.make_wooden_sword_context(
            rng=rng,
            frame_delta=0.1,
            stamina=2.0,
        )

        sword.activate_item(context)

        self.assertAlmostEqual(sword.triggers[0].cooldown_progress, 0.1)
        self.assertAlmostEqual(context.owner.stamina, 2.0)
        self.assertEqual(context.opponent.health, 10)
        rng.random.assert_not_called()
        rng.randint.assert_not_called()

    def test_wooden_sword_pays_stamina_and_attacks_after_cooldown(self):
        rng = Mock()
        rng.random.return_value = 0.0
        rng.randint.return_value = 2
        sword, context = self.make_wooden_sword_context(
            rng=rng,
            frame_delta=1.4,
            stamina=2.0,
        )

        sword.activate_item(context)

        self.assertAlmostEqual(context.owner.stamina, 1.0)
        self.assertEqual(context.opponent.health, 8)
        self.assertAlmostEqual(sword.triggers[0].cooldown_progress, 0.0)
        rng.random.assert_called_once_with()
        rng.randint.assert_called_once_with(1, 3)

    def test_wooden_sword_pays_stamina_but_does_not_damage_on_miss(
        self,
    ):
        rng = Mock()
        rng.random.return_value = 0.95
        sword, context = self.make_wooden_sword_context(
            rng=rng,
            frame_delta=1.4,
            stamina=2.0,
        )

        sword.activate_item(context)

        self.assertAlmostEqual(context.owner.stamina, 1.0)
        self.assertEqual(context.opponent.health, 10)
        rng.random.assert_called_once_with()
        rng.randint.assert_not_called()

    def test_wooden_sword_skips_attack_and_restarts_cooldown_without_stamina(self):
        rng = Mock()
        sword, context = self.make_wooden_sword_context(
            rng=rng,
            frame_delta=1.4,
            stamina=0.5,
        )

        sword.activate_item(context)

        self.assertAlmostEqual(context.owner.stamina, 0.5)
        self.assertAlmostEqual(sword.triggers[0].cooldown_progress, 0.0)
        self.assertEqual(context.opponent.health, 10)
        rng.random.assert_not_called()
        rng.randint.assert_not_called()

        context.owner.stamina = 2.0
        context.battle_state.frame_delta = 0.1
        sword.activate_item(context)

        self.assertAlmostEqual(sword.triggers[0].cooldown_progress, 0.1)
        rng.random.assert_not_called()

    def test_initializer_builds_wooden_sword_as_an_active_item(self):
        battle = initialize_battle(
            [
                {
                    "player_id": 0,
                    "health": 10,
                    "max_health": 10,
                    "stamina": 5.0,
                    "max_stamina": 5.0,
                    "placements": [
                        {
                            "item_id": "wooden_sword",
                            "x": 0,
                            "y": 0,
                            "rotation": 0,
                        },
                    ],
                },
                {
                    "player_id": 1,
                    "health": 10,
                    "max_health": 10,
                    "stamina": 5.0,
                    "max_stamina": 5.0,
                    "placements": [],
                },
            ],
            DEFAULT_ITEM_FACTORIES,
            item_catalog=ITEM_CATALOG,
        )

        sword = battle.players[0].items["wooden_sword1"]
        self.assertIsInstance(sword, WoodenSword)
        self.assertEqual(battle.active_items, [sword])

    def test_cooldown_trigger_starts_empty_and_does_not_trigger_immediately(self):
        trigger = CooldownTrigger(cooldown_seconds=1.4)

        result = trigger.update(self.make_context(frame_delta=0.1))

        self.assertFalse(result)
        self.assertAlmostEqual(trigger.cooldown_progress, 0.1)

    def test_cooldown_trigger_fires_when_accumulated_progress_reaches_threshold(self):
        trigger = CooldownTrigger(cooldown_seconds=1.0)
        context = self.make_context(frame_delta=0.25)

        results = [trigger.update(context) for _ in range(4)]

        self.assertEqual(results, [False, False, False, True])
        self.assertAlmostEqual(trigger.cooldown_progress, 0.0)

    def test_cooldown_trigger_reads_current_frame_delta_on_every_update(self):
        trigger = CooldownTrigger(cooldown_seconds=1.0)
        context = self.make_context(frame_delta=0.25)

        first_result = trigger.update(context)
        context.battle_state.frame_delta = 0.75
        second_result = trigger.update(context)

        self.assertFalse(first_result)
        self.assertTrue(second_result)
        self.assertAlmostEqual(trigger.cooldown_progress, 0.0)

    def test_cooldown_trigger_cancels_heat_and_cold_stacks(self):
        cases = (
            (5, 5, 0.5),
            (8, 3, 0.55),
            (3, 8, 0.5 / 1.1),
        )

        for heat, cold, expected_progress in cases:
            with self.subTest(heat=heat, cold=cold):
                trigger = CooldownTrigger(cooldown_seconds=1.0)
                context = self.make_context(frame_delta=0.5)
                context.owner.buffs.Heat = heat
                context.owner.debuffs.Cold = cold

                self.assertFalse(trigger.update(context))
                self.assertAlmostEqual(
                    trigger.cooldown_progress,
                    expected_progress,
                )

    def test_cooldown_trigger_reads_current_heat_and_cold_each_frame(self):
        trigger = CooldownTrigger(cooldown_seconds=1.0)
        context = self.make_context(frame_delta=0.25)
        context.owner.buffs.Heat = 10

        self.assertFalse(trigger.update(context))
        self.assertAlmostEqual(trigger.cooldown_progress, 0.3)

        context.owner.buffs.Heat = 0
        context.owner.debuffs.Cold = 10

        self.assertFalse(trigger.update(context))
        self.assertAlmostEqual(trigger.cooldown_progress, 0.3 + 0.25 / 1.2)

    def test_cooldown_trigger_never_reverses_progress_from_high_cold(self):
        trigger = CooldownTrigger(cooldown_seconds=1.0)
        context = self.make_context(frame_delta=0.3)
        context.owner.debuffs.Cold = 100

        self.assertFalse(trigger.update(context))
        self.assertAlmostEqual(trigger.cooldown_progress, 0.1)

    def test_cooldown_trigger_preserves_overflow_progress(self):
        trigger = CooldownTrigger(cooldown_seconds=1.0)
        context = self.make_context(frame_delta=0.75)

        self.assertFalse(trigger.update(context))
        context.battle_state.frame_delta = 0.5

        self.assertTrue(trigger.update(context))
        self.assertAlmostEqual(trigger.cooldown_progress, 0.25)

    def test_cooldown_trigger_instances_have_independent_progress(self):
        first_trigger = CooldownTrigger(cooldown_seconds=1.0)
        second_trigger = CooldownTrigger(cooldown_seconds=1.0)

        first_trigger.update(self.make_context(frame_delta=0.25))

        self.assertAlmostEqual(first_trigger.cooldown_progress, 0.25)
        self.assertAlmostEqual(second_trigger.cooldown_progress, 0.0)

    def test_food_cooldown_counts_each_linked_other_food_instance(self):
        banana, context, _ = self.make_banana_context(
            linked_item_specs=(
                ("garlic1", "garlic", ("Food",)),
                ("garlic2", "garlic", ("Food",)),
            ),
        )

        self.assertFalse(banana.triggers[0].update(context))

        self.assertEqual(
            banana.triggers[0].qualifying_food_count,
            2,
        )
        self.assertAlmostEqual(
            banana.triggers[0].cooldown_progress,
            1.2,
        )

    def test_food_cooldown_ignores_linked_same_food_and_non_food(self):
        banana, context, _ = self.make_banana_context(
            linked_item_specs=(
                ("banana2", "banana", ("Food",)),
                ("wooden_sword1", "wooden_sword", ("Weapon",)),
            ),
        )

        self.assertFalse(banana.triggers[0].update(context))

        self.assertEqual(
            banana.triggers[0].qualifying_food_count,
            0,
        )
        self.assertAlmostEqual(
            banana.triggers[0].cooldown_progress,
            1.0,
        )

    def test_food_cooldown_ignores_unlinked_food(self):
        banana, context, _ = self.make_banana_context(
            unlinked_item_specs=(
                ("garlic1", "garlic", ("Food",)),
            ),
        )

        self.assertFalse(banana.triggers[0].update(context))

        self.assertEqual(
            banana.triggers[0].qualifying_food_count,
            0,
        )
        self.assertAlmostEqual(
            banana.triggers[0].cooldown_progress,
            1.0,
        )

    def test_food_cooldown_counts_one_linked_instance_once(self):
        banana, context, _ = self.make_banana_context(
            linked_item_specs=(
                ("garlic1", "garlic", ("Food",)),
            ),
        )
        banana.add_linked_item("garlic1")

        self.assertEqual(banana.linked_items, ["garlic1"])
        self.assertFalse(banana.triggers[0].update(context))
        self.assertEqual(
            banana.triggers[0].qualifying_food_count,
            1,
        )
        self.assertAlmostEqual(
            banana.triggers[0].cooldown_progress,
            1.1,
        )

    def test_food_cooldown_combines_food_faster_and_cold_additively(self):
        banana, context, _ = self.make_banana_context(
            linked_item_specs=(
                ("garlic1", "garlic", ("Food",)),
            ),
        )
        context.owner.debuffs.Cold = 5

        self.assertFalse(banana.triggers[0].update(context))

        self.assertAlmostEqual(
            banana.triggers[0].cooldown_progress,
            1.0,
        )

    def test_food_cooldown_caches_link_count_after_first_update(self):
        banana, context, linked_items = self.make_banana_context(
            linked_item_specs=(
                ("garlic1", "garlic", ("Food",)),
            ),
        )

        self.assertFalse(banana.triggers[0].update(context))
        self.assertEqual(
            banana.triggers[0].qualifying_food_count,
            1,
        )
        self.assertAlmostEqual(
            banana.triggers[0].cooldown_progress,
            1.1,
        )

        blueberries = Mock()
        blueberries.item_id = "blueberries"
        blueberries.item_types = ("Food",)
        linked_items["blueberries1"] = blueberries
        context.owner.items["blueberries1"] = blueberries
        banana.add_linked_item("blueberries1")
        context.owner.debuffs.Cold = 5

        self.assertFalse(banana.triggers[0].update(context))

        self.assertEqual(
            banana.triggers[0].qualifying_food_count,
            1,
        )
        self.assertAlmostEqual(
            banana.triggers[0].cooldown_progress,
            2.1,
        )

    def test_garlic_food_cooldown_counts_linked_banana(self):
        garlic, context, _, _ = self.make_garlic_context(
            linked_item_specs=(
                ("banana1", "banana", ("Food",)),
            ),
        )

        self.assertFalse(garlic.triggers[0].update(context))

        self.assertEqual(
            garlic.triggers[0].qualifying_food_count,
            1,
        )
        self.assertAlmostEqual(
            garlic.triggers[0].cooldown_progress,
            1.1,
        )

    def test_garlic_food_cooldown_ignores_linked_garlic(self):
        garlic, context, _, _ = self.make_garlic_context(
            linked_item_specs=(
                ("garlic2", "garlic", ("Food",)),
            ),
        )

        self.assertFalse(garlic.triggers[0].update(context))

        self.assertEqual(
            garlic.triggers[0].qualifying_food_count,
            0,
        )
        self.assertAlmostEqual(
            garlic.triggers[0].cooldown_progress,
            1.0,
        )

    def test_garlic_food_cooldown_keeps_first_cached_count(self):
        garlic, context, linked_items, _ = self.make_garlic_context(
            linked_item_specs=(
                ("banana1", "banana", ("Food",)),
            ),
        )

        self.assertFalse(garlic.triggers[0].update(context))
        self.assertEqual(
            garlic.triggers[0].qualifying_food_count,
            1,
        )

        blueberries = Mock()
        blueberries.item_id = "blueberries"
        blueberries.item_types = ("Food",)
        linked_items["blueberries1"] = blueberries
        context.owner.items["blueberries1"] = blueberries
        garlic.add_linked_item("blueberries1")
        context.owner.debuffs.Cold = 5

        self.assertFalse(garlic.triggers[0].update(context))

        self.assertEqual(
            garlic.triggers[0].qualifying_food_count,
            1,
        )
        self.assertAlmostEqual(
            garlic.triggers[0].cooldown_progress,
            2.1,
        )

    def test_gain_block_effect_adds_amount(self):
        effect = GainBlockEffect(amount=3)
        context = self.make_context()
        context.owner.block = 2

        result = effect.apply(context)

        self.assertTrue(result)
        self.assertEqual(context.owner.block, 5)

    def test_gain_block_effect_returns_false_for_zero_amount(self):
        effect = GainBlockEffect(amount=0)
        context = self.make_context()
        context.owner.block = 2

        result = effect.apply(context)

        self.assertFalse(result)
        self.assertEqual(context.owner.block, 2)

    def test_gain_block_effect_rejects_invalid_amount(self):
        for invalid_amount in (-1, 1.5, True, "3"):
            with self.subTest(invalid_amount=invalid_amount):
                with self.assertRaises(ValueError):
                    GainBlockEffect(invalid_amount)

    def test_buff_removal_effect_removes_named_buff(self):
        effect = BuffRemovalEffect(
            buff_name="Vampirism",
            amount=1,
        )
        context = self.make_context()
        context.opponent.buffs.Vampirism = 2
        context.battle_state.rng = Mock()

        result = effect.apply(context)

        self.assertTrue(result)
        self.assertEqual(context.opponent.buffs.Vampirism, 1)
        context.battle_state.rng.random.assert_not_called()

    def test_buff_removal_effect_can_remove_another_supported_buff(self):
        effect = BuffRemovalEffect(
            buff_name="Heat",
            amount=2,
        )
        context = self.make_context()
        context.opponent.buffs.Heat = 3

        result = effect.apply(context)

        self.assertTrue(result)
        self.assertEqual(context.opponent.buffs.Heat, 1)

    def test_buff_removal_effect_caps_at_available_stacks(self):
        effect = BuffRemovalEffect(
            buff_name="Vampirism",
            amount=3,
        )
        context = self.make_context()
        context.opponent.buffs.Vampirism = 1

        result = effect.apply(context)

        self.assertTrue(result)
        self.assertEqual(context.opponent.buffs.Vampirism, 0)

    def test_buff_removal_effect_returns_false_with_no_stacks(self):
        effect = BuffRemovalEffect(
            buff_name="Vampirism",
            amount=1,
        )
        context = self.make_context()

        result = effect.apply(context)

        self.assertFalse(result)
        self.assertEqual(context.opponent.buffs.Vampirism, 0)

    def test_buff_removal_effect_rejects_invalid_buff_name(self):
        for invalid_name in ("", "Unknown", True, 1):
            with self.subTest(invalid_name=invalid_name):
                with self.assertRaises(ValueError):
                    BuffRemovalEffect(
                        buff_name=invalid_name,
                        amount=1,
                    )

    def test_buff_removal_effect_rejects_invalid_amount(self):
        for invalid_amount in (-1, 1.5, True, "1"):
            with self.subTest(invalid_amount=invalid_amount):
                with self.assertRaises(ValueError):
                    BuffRemovalEffect(
                        buff_name="Vampirism",
                        amount=invalid_amount,
                    )

    def test_heal_effect_increases_health_by_amount(self):
        effect = HealEffect(amount=4)
        context = self.make_context(health=5, max_health=10)

        result = effect.apply(context)

        self.assertTrue(result)
        self.assertEqual(context.owner.health, 9)
        self.assertEqual(context.owner.max_health, 10)

    def test_heal_effect_caps_health_at_max_health(self):
        effect = HealEffect(amount=4)
        context = self.make_context(health=9, max_health=10)

        result = effect.apply(context)

        self.assertTrue(result)
        self.assertEqual(context.owner.health, 10)

    def test_heal_effect_returns_false_at_full_health(self):
        effect = HealEffect(amount=4)
        context = self.make_context(health=10, max_health=10)

        result = effect.apply(context)

        self.assertFalse(result)
        self.assertEqual(context.owner.health, 10)

    def test_heal_effect_rejects_invalid_amount(self):
        for invalid_amount in (-1, 1.5, True, "4"):
            with self.subTest(invalid_amount=invalid_amount):
                with self.assertRaises(ValueError):
                    HealEffect(invalid_amount)

    def test_regenerate_stamina_effect_increases_stamina_by_amount(self):
        effect = RegenerateStaminaEffect(amount=1)
        context = self.make_context(stamina=2.0, max_stamina=5.0)

        result = effect.apply(context)

        self.assertTrue(result)
        self.assertEqual(context.owner.stamina, 3.0)
        self.assertEqual(context.owner.max_stamina, 5.0)

    def test_regenerate_stamina_effect_caps_at_max_stamina(self):
        effect = RegenerateStaminaEffect(amount=1.0)
        context = self.make_context(stamina=4.5, max_stamina=5.0)

        result = effect.apply(context)

        self.assertTrue(result)
        self.assertEqual(context.owner.stamina, 5.0)

    def test_regenerate_stamina_effect_returns_false_at_full_stamina(self):
        effect = RegenerateStaminaEffect(amount=1.0)
        context = self.make_context(stamina=5.0, max_stamina=5.0)

        result = effect.apply(context)

        self.assertFalse(result)
        self.assertEqual(context.owner.stamina, 5.0)

    def test_regenerate_stamina_effect_rejects_invalid_amount(self):
        for invalid_amount in (-1, True, "1"):
            with self.subTest(invalid_amount=invalid_amount):
                with self.assertRaises(ValueError):
                    RegenerateStaminaEffect(invalid_amount)

    def test_stamina_consumption_effect_deducts_cost_when_stamina_is_sufficient(self):
        effect = StaminaConsumptionEffect(stamina_cost=0.7)
        context = self.make_context(stamina=2.0, max_stamina=5.0)

        result = effect.apply(context)

        self.assertTrue(result)
        self.assertAlmostEqual(context.owner.stamina, 1.3)
        self.assertAlmostEqual(context.owner.max_stamina, 5.0)

    def test_stamina_consumption_effect_accepts_exact_remaining_stamina(self):
        effect = StaminaConsumptionEffect(stamina_cost=1.0)
        context = self.make_context(stamina=1.0, max_stamina=5.0)

        result = effect.apply(context)

        self.assertTrue(result)
        self.assertAlmostEqual(context.owner.stamina, 0.0)

    def test_stamina_consumption_effect_does_not_deduct_when_stamina_is_insufficient(self):
        effect = StaminaConsumptionEffect(stamina_cost=1.0)
        context = self.make_context(stamina=0.5, max_stamina=5.0)

        result = effect.apply(context)

        self.assertFalse(result)
        self.assertAlmostEqual(context.owner.stamina, 0.5)
        self.assertAlmostEqual(context.owner.max_stamina, 5.0)

    def test_banana_does_not_activate_before_cooldown(self):
        banana, context, _ = self.make_banana_context(
            frame_delta=1.0,
            health=5,
            max_health=10,
            stamina=2.0,
            max_stamina=5.0,
        )

        banana.activate_item(context)

        self.assertAlmostEqual(
            banana.triggers[0].cooldown_progress,
            1.0,
        )
        self.assertEqual(context.owner.health, 5)
        self.assertEqual(context.owner.stamina, 2.0)

    def test_banana_heals_and_regenerates_stamina_after_cooldown(self):
        banana, context, _ = self.make_banana_context(
            frame_delta=5.0,
            health=5,
            max_health=10,
            stamina=2.0,
            max_stamina=5.0,
        )

        banana.activate_item(context)

        self.assertEqual(context.owner.health, 9)
        self.assertEqual(context.owner.stamina, 3.0)
        self.assertAlmostEqual(
            banana.triggers[0].cooldown_progress,
            0.0,
        )

    def test_banana_runs_stamina_effect_when_heal_has_no_effect(self):
        banana, context, _ = self.make_banana_context(
            frame_delta=5.0,
            health=10,
            max_health=10,
            stamina=2.0,
            max_stamina=5.0,
        )

        banana.activate_item(context)

        self.assertEqual(context.owner.health, 10)
        self.assertEqual(context.owner.stamina, 3.0)

    def test_banana_runs_heal_effect_when_stamina_has_no_effect(self):
        banana, context, _ = self.make_banana_context(
            frame_delta=5.0,
            health=5,
            max_health=10,
            stamina=5.0,
            max_stamina=5.0,
        )

        banana.activate_item(context)

        self.assertEqual(context.owner.health, 9)
        self.assertEqual(context.owner.stamina, 5.0)

    def test_banana_caps_both_resources(self):
        banana, context, _ = self.make_banana_context(
            frame_delta=5.0,
            health=9,
            max_health=10,
            stamina=4.5,
            max_stamina=5.0,
        )

        banana.activate_item(context)

        self.assertEqual(context.owner.health, 10)
        self.assertEqual(context.owner.stamina, 5.0)

    def test_banana_does_not_activate_star_linked_items(self):
        banana, context, linked_items = self.make_banana_context(
            frame_delta=5.0,
            health=5,
            max_health=10,
            stamina=2.0,
            max_stamina=5.0,
            linked_item_specs=(
                ("garlic1", "garlic", ("Food",)),
            ),
        )

        banana.activate_item(context)

        self.assertEqual(context.owner.health, 9)
        self.assertEqual(context.owner.stamina, 3.0)
        linked_items["garlic1"].activate_item.assert_not_called()

    def test_garlic_does_not_activate_before_cooldown(self):
        rng = Mock()
        rng.random.return_value = 0.0
        garlic, context, _, _ = self.make_garlic_context(
            frame_delta=1.0,
            block=2,
            opponent_vampirism=2,
            rng=rng,
        )

        garlic.activate_item(context)

        self.assertAlmostEqual(
            garlic.triggers[0].cooldown_progress,
            1.0,
        )
        self.assertEqual(context.owner.block, 2)
        self.assertEqual(context.opponent.buffs.Vampirism, 2)
        rng.random.assert_not_called()

    def test_garlic_gains_block_and_removes_vampirism_on_success(self):
        rng = Mock()
        rng.random.return_value = 0.29
        garlic, context, _, _ = self.make_garlic_context(
            frame_delta=4.0,
            block=2,
            opponent_vampirism=2,
            rng=rng,
        )

        garlic.activate_item(context)

        self.assertEqual(context.owner.block, 5)
        self.assertEqual(context.opponent.buffs.Vampirism, 1)
        self.assertAlmostEqual(
            garlic.triggers[0].cooldown_progress,
            0.0,
        )
        rng.random.assert_called_once_with()

    def test_garlic_still_gains_block_when_removal_roll_fails(self):
        rng = Mock()
        rng.random.return_value = 0.30
        garlic, context, _, _ = self.make_garlic_context(
            frame_delta=4.0,
            block=2,
            opponent_vampirism=2,
            rng=rng,
        )

        garlic.activate_item(context)

        self.assertEqual(context.owner.block, 5)
        self.assertEqual(context.opponent.buffs.Vampirism, 2)
        rng.random.assert_called_once_with()

    def test_garlic_still_gains_block_when_opponent_has_no_vampirism(self):
        rng = Mock()
        rng.random.return_value = 0.29
        garlic, context, _, _ = self.make_garlic_context(
            frame_delta=4.0,
            block=2,
            opponent_vampirism=0,
            rng=rng,
        )

        garlic.activate_item(context)

        self.assertEqual(context.owner.block, 5)
        self.assertEqual(context.opponent.buffs.Vampirism, 0)
        rng.random.assert_called_once_with()

    def test_garlic_does_not_activate_star_linked_items(self):
        rng = Mock()
        rng.random.return_value = 0.29
        garlic, context, linked_items, _ = self.make_garlic_context(
            frame_delta=4.0,
            block=2,
            opponent_vampirism=2,
            rng=rng,
            linked_item_specs=(
                ("wooden_sword1", "wooden_sword", ("Weapon",)),
            ),
        )

        garlic.activate_item(context)

        self.assertEqual(context.owner.block, 5)
        self.assertEqual(context.opponent.buffs.Vampirism, 1)
        linked_items["wooden_sword1"].activate_item.assert_not_called()

    def test_battle_step_runs_garlic_at_four_seconds(self):
        rng = Mock()
        rng.random.return_value = 0.29
        garlic, context, _, _ = self.make_garlic_context(
            frame_delta=1.0,
            block=0,
            opponent_vampirism=2,
            rng=rng,
        )

        for _ in range(4):
            context.battle_state.step()

        self.assertEqual(context.battle_state.frame, 4)
        self.assertEqual(context.owner.block, 3)
        self.assertEqual(context.opponent.buffs.Vampirism, 1)
        self.assertAlmostEqual(
            garlic.triggers[0].cooldown_progress,
            0.0,
        )
        rng.random.assert_called_once_with()

    def test_melee_attack_effect_starts_with_unprepared_zero_damage_modifier(
        self,
    ):
        effect = MeleeAttackEffect(1, 3, 90)
        context = self.make_context()
        context.battle_state.rng = Mock()
        context.battle_state.rng.random.return_value = 0.0
        context.battle_state.rng.randint.return_value = 1

        self.assertEqual(effect.damage_modifier, 0)
        self.assertFalse(effect.damage_modifier_prepared)

        result = effect.apply(context)

        self.assertTrue(result)
        self.assertTrue(effect.damage_modifier_prepared)
        self.assertEqual(effect.damage_modifier, 0)
        context.battle_state.rng.randint.assert_called_once_with(1, 3)

    def test_melee_attack_effect_stacks_persistent_damage_modifiers(self):
        effect = MeleeAttackEffect(1, 3, 90)
        effect.stack_damage_modifier(2)
        effect.stack_damage_modifier(3)
        context = self.make_context()
        context.owner.buffs.Empower = 1
        context.battle_state.rng = Mock()
        context.battle_state.rng.random.return_value = 0.0
        context.battle_state.rng.randint.return_value = 7

        effect.apply(context)

        self.assertEqual(effect.damage_modifier, 5)
        context.battle_state.rng.randint.assert_called_once_with(7, 9)

    def test_melee_attack_effect_prepares_intrinsic_modifier_once(self):
        class PreparingMeleeAttackEffect(MeleeAttackEffect):
            def __init__(self):
                super().__init__(1, 3, 90)
                self.prepare_calls = 0

            def prepare_damage_modifier(self, context):
                self.prepare_calls += 1
                self.stack_damage_modifier(2)

        effect = PreparingMeleeAttackEffect()
        context = self.make_context()
        context.battle_state.rng = Mock()
        context.battle_state.rng.random.return_value = 0.0
        context.battle_state.rng.randint.side_effect = [3, 3]

        effect.apply(context)
        effect.apply(context)

        self.assertEqual(effect.prepare_calls, 1)
        self.assertEqual(effect.damage_modifier, 2)
        self.assertEqual(effect.min_damage, 1)
        self.assertEqual(effect.max_damage, 3)
        self.assertEqual(
            context.battle_state.rng.randint.call_args_list,
            [call(3, 5), call(3, 5)],
        )

    def test_food_linked_melee_attack_effect_counts_all_linked_food_instances(
        self,
    ):
        rng = Mock()
        rng.random.return_value = 0.0
        rng.randint.return_value = 7
        pan, context, _, _ = self.make_pan_context(
            rng=rng,
            linked_item_specs=(
                ("banana1", "banana", ("Food",)),
                ("banana2", "banana", ("Food",)),
            ),
        )
        effect = pan.effects[1]

        effect.apply(context)

        self.assertEqual(effect.qualifying_food_count, 2)
        self.assertEqual(effect.damage_modifier, 2)
        self.assertTrue(effect.damage_modifier_prepared)
        rng.randint.assert_called_once_with(7, 8)

    def test_food_linked_melee_attack_effect_ignores_non_food_and_unlinked_food(
        self,
    ):
        rng = Mock()
        rng.random.return_value = 0.0
        rng.randint.return_value = 5
        pan, context, _, _ = self.make_pan_context(
            rng=rng,
            linked_item_specs=(
                ("wooden_sword1", "wooden_sword", ("Weapon",)),
            ),
            unlinked_item_specs=(
                ("banana1", "banana", ("Food",)),
            ),
        )
        effect = pan.effects[1]

        effect.apply(context)

        self.assertEqual(effect.qualifying_food_count, 0)
        self.assertEqual(effect.damage_modifier, 0)
        rng.randint.assert_called_once_with(5, 6)

    def test_food_linked_melee_attack_effect_uses_first_cached_count(self):
        rng = Mock()
        rng.random.return_value = 0.0
        rng.randint.side_effect = [6, 6]
        pan, context, linked_items, _ = self.make_pan_context(
            rng=rng,
            linked_item_specs=(
                ("banana1", "banana", ("Food",)),
            ),
        )
        effect = pan.effects[1]

        effect.apply(context)

        blueberries = Mock()
        blueberries.item_id = "blueberries"
        blueberries.item_types = ("Food",)
        linked_items["blueberries1"] = blueberries
        context.owner.items["blueberries1"] = blueberries
        pan.add_linked_item("blueberries1")
        effect.apply(context)

        self.assertEqual(effect.qualifying_food_count, 1)
        self.assertEqual(effect.damage_modifier, 1)
        self.assertEqual(
            rng.randint.call_args_list,
            [call(6, 7), call(6, 7)],
        )

    def test_food_linked_melee_attack_effect_rejects_invalid_damage_per_food(
        self,
    ):
        for invalid_amount in (-1, 1.5, True, "1"):
            with self.subTest(invalid_amount=invalid_amount):
                with self.assertRaises(ValueError):
                    FoodLinkedMeleeAttackEffect(
                        min_damage=5,
                        max_damage=6,
                        accuracy=85,
                        damage_per_food=invalid_amount,
                    )

    def test_food_linked_melee_attack_effect_preserves_external_modifier_and_base_damage(
        self,
    ):
        rng = Mock()
        rng.random.return_value = 0.0
        rng.randint.return_value = 11
        pan, context, _, _ = self.make_pan_context(
            rng=rng,
            linked_item_specs=(
                ("banana1", "banana", ("Food",)),
                ("banana2", "banana", ("Food",)),
            ),
        )
        effect = pan.effects[1]
        effect.stack_damage_modifier(4)

        effect.apply(context)

        self.assertEqual(effect.damage_modifier, 6)
        self.assertEqual(effect.min_damage, 5)
        self.assertEqual(effect.max_damage, 6)
        rng.randint.assert_called_once_with(11, 12)

    def test_pan_is_registered_with_metadata_and_components(self):
        pan = DEFAULT_ITEM_FACTORIES["pan"](
            item_id="pan",
            item_key="pan1",
            player_id=0,
        )

        self.assertIsInstance(pan, Pan)
        self.assertEqual(pan.item_id, "pan")
        self.assertEqual(pan.item_key, "pan1")
        self.assertEqual(pan.player_id, 0)
        self.assertEqual(pan.display_name, "Pan")
        self.assertEqual(pan.item_classes, ("Neutral",))
        self.assertEqual(pan.rarity, "Common")
        self.assertEqual(pan.cost, 4)
        self.assertEqual(pan.item_types, ("Weapon",))
        self.assertEqual(pan.icon_types, ("melee",))
        self.assertTrue(pan.is_active_item)
        self.assertEqual(pan.socket_count, 1)
        self.assertEqual(len(pan.triggers), 1)
        self.assertIsInstance(pan.triggers[0], CooldownTrigger)
        self.assertNotIsInstance(pan.triggers[0], FoodCooldownTrigger)
        self.assertEqual(pan.triggers[0].cooldown_seconds, 2.2)
        self.assertEqual(len(pan.effects), 2)
        self.assertIsInstance(
            pan.effects[0],
            StaminaConsumptionEffect,
        )
        self.assertEqual(pan.effects[0].stamina_cost, 2.0)
        self.assertIsInstance(
            pan.effects[1],
            FoodLinkedMeleeAttackEffect,
        )
        self.assertEqual(pan.effects[1].min_damage, 5)
        self.assertEqual(pan.effects[1].max_damage, 6)
        self.assertEqual(pan.effects[1].accuracy, 85)
        self.assertEqual(pan.effects[1].damage_per_food, 1)

    def test_pans_own_independent_component_instances(self):
        first = Pan(item_key="pan1", player_id=0)
        second = Pan(item_key="pan2", player_id=0)

        self.assertIsNot(first.triggers[0], second.triggers[0])
        self.assertIsNot(first.effects[0], second.effects[0])
        self.assertIsNot(first.effects[1], second.effects[1])

        first.triggers[0].cooldown_progress = 0.5
        first.triggers[0].stack_speed_modifier(0.2)
        first.triggers[0].speed_modifiers_prepared = True
        first.effects[1].stack_damage_modifier(3)
        first.effects[1].damage_modifier_prepared = True
        first.effects[1].qualifying_food_count = 2

        self.assertEqual(second.triggers[0].cooldown_progress, 0.0)
        self.assertEqual(second.triggers[0].speed_modifiers, 0.0)
        self.assertFalse(second.triggers[0].speed_modifiers_prepared)
        self.assertEqual(second.effects[1].damage_modifier, 0)
        self.assertFalse(second.effects[1].damage_modifier_prepared)
        self.assertIsNone(second.effects[1].qualifying_food_count)

    def test_initializer_builds_pan_as_active_item_with_deduplicated_food_link(
        self,
    ):
        battle = initialize_battle(
            [
                {
                    "player_id": 0,
                    "health": 20,
                    "max_health": 20,
                    "stamina": 10.0,
                    "max_stamina": 10.0,
                    "placements": [
                        {
                            "item_id": "pan",
                            "x": 2,
                            "y": 2,
                            "rotation": 0,
                        },
                        {
                            "item_id": "banana",
                            "x": 4,
                            "y": 2,
                            "rotation": 0,
                        },
                    ],
                },
                {
                    "player_id": 1,
                    "health": 20,
                    "max_health": 20,
                    "stamina": 10.0,
                    "max_stamina": 10.0,
                    "placements": [],
                },
            ],
            DEFAULT_ITEM_FACTORIES,
            item_catalog=ITEM_CATALOG,
        )

        pan = battle.players[0].items["pan1"]
        banana = battle.players[0].items["banana1"]
        self.assertIsInstance(pan, Pan)
        self.assertEqual(pan.linked_items, ["banana1"])
        self.assertEqual(battle.active_items, [pan, banana])

    def test_pan_does_not_activate_before_cooldown(self):
        rng = Mock()
        pan, context, _, _ = self.make_pan_context(
            frame_delta=1.0,
            stamina=5.0,
            rng=rng,
        )

        pan.activate_item(context)

        self.assertAlmostEqual(pan.triggers[0].cooldown_progress, 1.0)
        self.assertEqual(context.owner.stamina, 5.0)
        self.assertEqual(context.opponent.health, 100)
        self.assertFalse(pan.effects[1].damage_modifier_prepared)
        rng.random.assert_not_called()
        rng.randint.assert_not_called()

    def test_pan_pays_stamina_and_attacks_with_base_damage(self):
        rng = Mock()
        rng.random.return_value = 0.0
        rng.randint.return_value = 5
        pan, context, _, _ = self.make_pan_context(
            frame_delta=2.2,
            stamina=5.0,
            opponent_health=20,
            rng=rng,
        )

        pan.activate_item(context)

        self.assertEqual(context.owner.stamina, 3.0)
        self.assertEqual(context.opponent.health, 15)
        self.assertAlmostEqual(pan.triggers[0].cooldown_progress, 0.0)
        rng.random.assert_called_once_with()
        rng.randint.assert_called_once_with(5, 6)

    def test_pan_adds_one_damage_per_linked_food(self):
        rng = Mock()
        rng.random.return_value = 0.0
        rng.randint.return_value = 7
        pan, context, _, _ = self.make_pan_context(
            frame_delta=2.2,
            stamina=5.0,
            opponent_health=20,
            rng=rng,
            linked_item_specs=(
                ("banana1", "banana", ("Food",)),
                ("banana2", "banana", ("Food",)),
            ),
        )

        pan.activate_item(context)

        self.assertEqual(context.owner.stamina, 3.0)
        self.assertEqual(context.opponent.health, 13)
        self.assertEqual(pan.effects[1].qualifying_food_count, 2)
        self.assertEqual(pan.effects[1].damage_modifier, 2)
        rng.randint.assert_called_once_with(7, 8)

    def test_pan_combines_food_external_damage_modifier_and_empower(self):
        rng = Mock()
        rng.random.return_value = 0.0
        rng.randint.return_value = 14
        pan, context, _, _ = self.make_pan_context(
            frame_delta=2.2,
            stamina=5.0,
            empower=3,
            rng=rng,
            linked_item_specs=(
                ("banana1", "banana", ("Food",)),
                ("banana2", "banana", ("Food",)),
            ),
        )
        pan.effects[1].stack_damage_modifier(4)

        pan.activate_item(context)

        self.assertEqual(pan.effects[1].damage_modifier, 6)
        rng.randint.assert_called_once_with(14, 15)

    def test_pan_accepts_external_damage_modifier_after_preparation(self):
        rng = Mock()
        rng.random.return_value = 0.0
        rng.randint.side_effect = [6, 8]
        pan, context, _, _ = self.make_pan_context(
            frame_delta=2.2,
            stamina=10.0,
            rng=rng,
            linked_item_specs=(
                ("banana1", "banana", ("Food",)),
            ),
        )

        pan.activate_item(context)
        pan.effects[1].stack_damage_modifier(2)
        pan.activate_item(context)

        self.assertEqual(pan.effects[1].qualifying_food_count, 1)
        self.assertEqual(pan.effects[1].damage_modifier, 3)
        self.assertEqual(
            rng.randint.call_args_list,
            [call(6, 7), call(8, 9)],
        )

    def test_pan_food_links_do_not_speed_up_cooldown(self):
        pan, context, _, _ = self.make_pan_context(
            frame_delta=1.0,
            stamina=5.0,
            linked_item_specs=(
                ("banana1", "banana", ("Food",)),
            ),
        )

        pan.activate_item(context)

        self.assertAlmostEqual(pan.triggers[0].cooldown_progress, 1.0)
        self.assertEqual(pan.triggers[0].speed_modifiers, 0.0)

    def test_pan_accepts_external_speed_modifier(self):
        pan, context, _, _ = self.make_pan_context(
            frame_delta=1.0,
            stamina=5.0,
        )
        pan.triggers[0].stack_speed_modifier(0.20)

        pan.activate_item(context)

        self.assertAlmostEqual(pan.triggers[0].cooldown_progress, 1.2)
        self.assertAlmostEqual(pan.triggers[0].speed_modifiers, 0.20)
        self.assertTrue(pan.triggers[0].speed_modifiers_prepared)

    def test_pan_skips_attack_without_stamina(self):
        rng = Mock()
        pan, context, _, _ = self.make_pan_context(
            frame_delta=2.2,
            stamina=1.0,
            rng=rng,
            linked_item_specs=(
                ("banana1", "banana", ("Food",)),
            ),
        )

        pan.activate_item(context)

        self.assertEqual(context.owner.stamina, 1.0)
        self.assertAlmostEqual(pan.triggers[0].cooldown_progress, 0.0)
        self.assertFalse(pan.effects[1].damage_modifier_prepared)
        self.assertIsNone(pan.effects[1].qualifying_food_count)
        self.assertEqual(pan.effects[1].damage_modifier, 0)
        rng.random.assert_not_called()
        rng.randint.assert_not_called()

    def test_pan_does_not_activate_star_linked_food_on_hit(self):
        rng = Mock()
        rng.random.return_value = 0.0
        rng.randint.return_value = 6
        pan, context, linked_items, _ = self.make_pan_context(
            frame_delta=2.2,
            stamina=5.0,
            rng=rng,
            linked_item_specs=(
                ("banana1", "banana", ("Food",)),
            ),
        )

        pan.activate_item(context)

        self.assertEqual(context.owner.stamina, 3.0)
        linked_items["banana1"].activate_item.assert_not_called()

    def test_pan_repeated_attacks_do_not_stack_food_damage_again(self):
        rng = Mock()
        rng.random.return_value = 0.0
        rng.randint.side_effect = [7, 7]
        pan, context, _, _ = self.make_pan_context(
            frame_delta=2.2,
            stamina=10.0,
            rng=rng,
            linked_item_specs=(
                ("banana1", "banana", ("Food",)),
                ("banana2", "banana", ("Food",)),
            ),
        )

        pan.activate_item(context)
        pan.activate_item(context)

        self.assertEqual(pan.effects[1].qualifying_food_count, 2)
        self.assertEqual(pan.effects[1].damage_modifier, 2)
        self.assertTrue(pan.effects[1].damage_modifier_prepared)
        self.assertEqual(
            rng.randint.call_args_list,
            [call(7, 8), call(7, 8)],
        )

    def test_pan_miss_still_pays_stamina_without_activating_linked_food(
        self,
    ):
        rng = Mock()
        rng.random.return_value = 0.85
        pan, context, linked_items, _ = self.make_pan_context(
            frame_delta=2.2,
            stamina=5.0,
            opponent_health=20,
            rng=rng,
            linked_item_specs=(
                ("banana1", "banana", ("Food",)),
            ),
        )

        pan.activate_item(context)

        self.assertEqual(context.owner.stamina, 3.0)
        self.assertEqual(context.opponent.health, 20)
        self.assertTrue(pan.effects[1].damage_modifier_prepared)
        self.assertEqual(pan.effects[1].damage_modifier, 1)
        rng.random.assert_called_once_with()
        rng.randint.assert_not_called()
        linked_items["banana1"].activate_item.assert_not_called()

    def test_cooldown_trigger_ignores_attack_reaction_context(self):
        broom, context, _ = self.make_broom_context(
            frame_delta=1.0,
        )
        event = AttackEvent(
            attacker=context.opponent,
            defender=context.owner,
            source_item=Mock(),
            attack_types=("melee",),
            min_damage=1,
            max_damage=1,
            accuracy=0,
            hit=False,
        )
        reaction_context = AttackReactionContext(
            battle_state=context.battle_state,
            item=broom,
            owner=context.owner,
            opponent=context.opponent,
            attack_phase=ATTACK_PHASE_ON_ATTACK_MISSED,
            attack_event=event,
        )

        result = broom.triggers[0].update(reaction_context)

        self.assertFalse(result)
        self.assertEqual(broom.triggers[0].cooldown_progress, 0.0)
        self.assertFalse(
            broom.triggers[0].speed_modifiers_prepared
        )

    def test_inflict_debuff_effect_adds_stacks_to_opponent(self):
        context = self.make_context()
        context.owner.debuffs.Blind = 7
        context.opponent.debuffs.Blind = 2
        effect = InflictDebuffEffect("Blind", 1)

        result = effect.apply(context)

        self.assertTrue(result)
        self.assertEqual(context.opponent.debuffs.Blind, 3)
        self.assertEqual(context.owner.debuffs.Blind, 7)

    def test_inflict_debuff_effect_handles_zero_and_rejects_invalid_arguments(
        self,
    ):
        context = self.make_context()
        context.opponent.debuffs.Blind = 2
        effect = InflictDebuffEffect("Blind", 0)

        result = effect.apply(context)

        self.assertFalse(result)
        self.assertEqual(context.opponent.debuffs.Blind, 2)

        invalid_arguments = (
            ("missing", 1),
            (1, 1),
            ("Blind", -1),
            ("Blind", True),
            ("Blind", 1.5),
            ("Blind", "1"),
        )
        for debuff_name, amount in invalid_arguments:
            with self.subTest(
                debuff_name=debuff_name,
                amount=amount,
            ):
                with self.assertRaises(ValueError):
                    InflictDebuffEffect(debuff_name, amount)

    def test_broom_is_registered_with_metadata_and_components(self):
        broom = DEFAULT_ITEM_FACTORIES["broom"](
            item_id="broom",
            item_key="broom1",
            player_id=0,
        )

        self.assertIsInstance(broom, Broom)
        self.assertEqual(broom.item_id, "broom")
        self.assertEqual(broom.item_key, "broom1")
        self.assertEqual(broom.player_id, 0)
        self.assertEqual(broom.display_name, "Broom")
        self.assertEqual(broom.item_classes, ("Neutral",))
        self.assertEqual(broom.rarity, "Common")
        self.assertEqual(broom.cost, 4)
        self.assertEqual(broom.item_types, ("Weapon",))
        self.assertEqual(broom.icon_types, ("melee",))
        self.assertTrue(broom.is_active_item)
        self.assertEqual(broom.socket_count, 1)
        self.assertEqual(len(broom.triggers), 2)
        self.assertIsInstance(broom.triggers[0], CooldownTrigger)
        self.assertEqual(broom.triggers[0].cooldown_seconds, 1.7)
        self.assertIsInstance(broom.triggers[1], AttackMissTrigger)
        self.assertEqual(len(broom.effects), 3)
        self.assertIsInstance(
            broom.effects[0],
            StaminaConsumptionEffect,
        )
        self.assertEqual(broom.effects[0].stamina_cost, 1.2)
        self.assertIsInstance(broom.effects[1], MeleeAttackEffect)
        self.assertEqual(broom.effects[1].min_damage, 2)
        self.assertEqual(broom.effects[1].max_damage, 4)
        self.assertEqual(broom.effects[1].accuracy, 95)
        self.assertIsInstance(broom.effects[2], InflictDebuffEffect)
        self.assertEqual(broom.effects[2].debuff_name, "Blind")
        self.assertEqual(broom.effects[2].amount, 1)
        self.assertEqual(broom.miss_damage_bonus, 0)

    def test_brooms_own_independent_components_and_bonus_state(self):
        first = Broom(item_key="broom1", player_id=0)
        second = Broom(item_key="broom2", player_id=0)

        for first_trigger, second_trigger in zip(
            first.triggers,
            second.triggers,
        ):
            self.assertIsNot(first_trigger, second_trigger)
        for first_effect, second_effect in zip(
            first.effects,
            second.effects,
        ):
            self.assertIsNot(first_effect, second_effect)

        first.triggers[0].cooldown_progress = 0.5
        first.effects[1].stack_damage_modifier(2)
        first.miss_damage_bonus = 2

        self.assertEqual(second.triggers[0].cooldown_progress, 0.0)
        self.assertEqual(second.effects[1].damage_modifier, 0)
        self.assertEqual(second.miss_damage_bonus, 0)

    def test_initializer_builds_broom_as_active_and_attack_miss_responder(
        self,
    ):
        battle = initialize_battle(
            [
                {
                    "player_id": 0,
                    "health": 20,
                    "max_health": 20,
                    "stamina": 5.0,
                    "max_stamina": 5.0,
                    "placements": [
                        {
                            "item_id": "broom",
                            "x": 0,
                            "y": 0,
                            "rotation": 0,
                        },
                    ],
                },
                {
                    "player_id": 1,
                    "health": 20,
                    "max_health": 20,
                    "stamina": 5.0,
                    "max_stamina": 5.0,
                    "placements": [],
                },
            ],
            DEFAULT_ITEM_FACTORIES,
            item_catalog=ITEM_CATALOG,
        )

        broom = battle.players[0].items["broom1"]
        self.assertIsInstance(broom, Broom)
        self.assertIn(broom, battle.active_items)
        self.assertEqual(
            battle._get_attack_reaction_items(
                battle.players[0],
                ATTACK_PHASE_ON_ATTACK_MISSED,
            ),
            (broom,),
        )
        self.assertEqual(
            battle._get_attack_reaction_items(
                battle.players[0],
                ATTACK_PHASE_ON_ATTACKED,
            ),
            (),
        )

    def test_broom_waits_for_cooldown_without_rng(self):
        rng = Mock()
        broom, context, _ = self.make_broom_context(
            frame_delta=1.0,
            stamina=5.0,
            rng=rng,
        )

        broom.activate_item(context)

        self.assertAlmostEqual(
            broom.triggers[0].cooldown_progress,
            1.0,
        )
        self.assertEqual(context.owner.stamina, 5.0)
        self.assertEqual(context.opponent.health, 100)
        self.assertEqual(context.opponent.debuffs.Blind, 0)
        rng.random.assert_not_called()
        rng.randint.assert_not_called()

    def test_broom_gains_two_damage_when_opponent_melee_attack_misses(
        self,
    ):
        rng = Mock()
        rng.random.return_value = 0.5
        broom, context, _ = self.make_broom_context(rng=rng)

        self.resolve_opponent_attack(
            context,
            accuracy=0,
            attack_types=("melee",),
        )

        self.assertEqual(broom.miss_damage_bonus, 2)
        self.assertEqual(broom.effects[1].damage_modifier, 2)
        self.assertEqual(broom.triggers[0].cooldown_progress, 0.0)
        self.assertFalse(
            broom.triggers[0].speed_modifiers_prepared
        )
        self.assertEqual(context.owner.stamina, 5.0)
        rng.random.assert_called_once_with()
        rng.randint.assert_not_called()

    def test_broom_attack_miss_trigger_accepts_ranged_and_effect_attacks(
        self,
    ):
        rng = Mock()
        rng.random.side_effect = [0.5, 0.5]
        broom, context, _ = self.make_broom_context(rng=rng)

        for attack_type in ("ranged", "effect"):
            self.resolve_opponent_attack(
                context,
                accuracy=0,
                attack_types=(attack_type,),
            )

        self.assertEqual(broom.miss_damage_bonus, 4)
        self.assertEqual(broom.effects[1].damage_modifier, 4)
        self.assertEqual(rng.random.call_count, 2)
        rng.randint.assert_not_called()

    def test_broom_multiple_opponent_misses_stack(self):
        rng = Mock()
        rng.random.side_effect = [0.5, 0.5, 0.5]
        broom, context, _ = self.make_broom_context(rng=rng)

        for _ in range(3):
            self.resolve_opponent_attack(context, accuracy=0)

        self.assertEqual(broom.miss_damage_bonus, 6)
        self.assertEqual(broom.effects[1].damage_modifier, 6)
        self.assertEqual(broom.effects[1].min_damage, 2)
        self.assertEqual(broom.effects[1].max_damage, 4)

    def test_broom_ignores_opponent_hits(self):
        rng = Mock()
        rng.random.return_value = 0.0
        rng.randint.return_value = 2
        broom, context, _ = self.make_broom_context(rng=rng)

        self.resolve_opponent_attack(
            context,
            accuracy=100,
            min_damage=2,
            max_damage=2,
        )

        self.assertEqual(broom.miss_damage_bonus, 0)
        self.assertEqual(broom.effects[1].damage_modifier, 0)
        self.assertEqual(context.owner.health, 98)

    def test_broom_pays_stamina_and_attacks_with_base_damage(self):
        rng = Mock()
        rng.random.side_effect = [0.0, 0.5]
        rng.randint.return_value = 2
        broom, context, _ = self.make_broom_context(
            frame_delta=1.7,
            stamina=5.0,
            rng=rng,
        )

        broom.activate_item(context)

        self.assertAlmostEqual(context.owner.stamina, 3.8)
        self.assertEqual(context.opponent.health, 98)
        rng.randint.assert_called_once_with(2, 4)
        self.assertEqual(rng.random.call_count, 2)

    def test_broom_applies_accumulated_bonus_then_clears_it_on_hit(
        self,
    ):
        rng = Mock()
        rng.random.side_effect = [0.5, 0.5, 0.0, 0.5]
        rng.randint.return_value = 6
        broom, context, _ = self.make_broom_context(
            frame_delta=1.7,
            stamina=5.0,
            rng=rng,
        )
        self.resolve_opponent_attack(context, accuracy=0)
        self.resolve_opponent_attack(context, accuracy=0)

        broom.activate_item(context)

        rng.randint.assert_called_once_with(6, 8)
        self.assertEqual(broom.miss_damage_bonus, 0)
        self.assertEqual(broom.effects[1].damage_modifier, 0)
        self.assertEqual(broom.effects[1].min_damage, 2)
        self.assertEqual(broom.effects[1].max_damage, 4)

    def test_broom_miss_retains_accumulated_bonus_and_skips_blind_roll(
        self,
    ):
        rng = Mock()
        rng.random.side_effect = [0.5, 0.5, 0.99]
        broom, context, _ = self.make_broom_context(
            frame_delta=1.7,
            stamina=5.0,
            rng=rng,
        )
        self.resolve_opponent_attack(context, accuracy=0)
        self.resolve_opponent_attack(context, accuracy=0)

        broom.activate_item(context)

        self.assertAlmostEqual(context.owner.stamina, 3.8)
        self.assertEqual(broom.miss_damage_bonus, 4)
        self.assertEqual(broom.effects[1].damage_modifier, 4)
        self.assertEqual(context.opponent.debuffs.Blind, 0)
        self.assertEqual(rng.random.call_count, 3)
        rng.randint.assert_not_called()

    def test_broom_retained_bonus_is_used_on_later_hit(self):
        rng = Mock()
        rng.random.side_effect = [
            0.5,
            0.5,
            0.99,
            0.0,
            0.5,
        ]
        rng.randint.return_value = 6
        broom, context, _ = self.make_broom_context(
            frame_delta=1.7,
            stamina=10.0,
            rng=rng,
        )
        self.resolve_opponent_attack(context, accuracy=0)
        self.resolve_opponent_attack(context, accuracy=0)
        broom.activate_item(context)

        broom.activate_item(context)

        rng.randint.assert_called_once_with(6, 8)
        self.assertEqual(broom.miss_damage_bonus, 0)
        self.assertEqual(broom.effects[1].damage_modifier, 0)

    def test_broom_insufficient_stamina_retains_bonus_without_rng(self):
        rng = Mock()
        rng.random.side_effect = [0.5]
        broom, context, _ = self.make_broom_context(
            frame_delta=1.7,
            stamina=1.0,
            rng=rng,
        )
        self.resolve_opponent_attack(context, accuracy=0)

        broom.activate_item(context)

        self.assertEqual(context.owner.stamina, 1.0)
        self.assertEqual(broom.miss_damage_bonus, 2)
        self.assertEqual(broom.effects[1].damage_modifier, 2)
        self.assertAlmostEqual(
            broom.triggers[0].cooldown_progress,
            0.0,
        )
        rng.random.assert_called_once_with()
        rng.randint.assert_not_called()

    def test_broom_on_hit_inflicts_blind_when_chance_succeeds(self):
        rng = Mock()
        rng.random.side_effect = [0.0, 0.329]
        rng.randint.return_value = 2
        broom, context, _ = self.make_broom_context(
            frame_delta=1.7,
            stamina=5.0,
            opponent_blind=2,
            rng=rng,
        )

        broom.activate_item(context)

        self.assertEqual(context.opponent.debuffs.Blind, 3)
        self.assertEqual(
            rng.method_calls,
            [call.random(), call.randint(2, 4), call.random()],
        )

    def test_broom_on_hit_does_not_inflict_blind_when_chance_fails(
        self,
    ):
        rng = Mock()
        rng.random.side_effect = [0.0, 0.33]
        rng.randint.return_value = 2
        broom, context, _ = self.make_broom_context(
            frame_delta=1.7,
            stamina=5.0,
            opponent_blind=2,
            rng=rng,
        )

        broom.activate_item(context)

        self.assertEqual(context.opponent.debuffs.Blind, 2)
        self.assertEqual(rng.random.call_count, 2)
        rng.randint.assert_called_once_with(2, 4)

    def test_broom_clears_only_miss_bonus_and_preserves_external_modifier(
        self,
    ):
        rng = Mock()
        rng.random.side_effect = [
            0.5,
            0.5,
            0.0,
            0.5,
            0.0,
            0.5,
        ]
        rng.randint.side_effect = [11, 7]
        broom, context, _ = self.make_broom_context(
            frame_delta=1.7,
            stamina=10.0,
            rng=rng,
        )
        broom.effects[1].stack_damage_modifier(5)
        self.resolve_opponent_attack(context, accuracy=0)
        self.resolve_opponent_attack(context, accuracy=0)

        broom.activate_item(context)

        self.assertEqual(broom.miss_damage_bonus, 0)
        self.assertEqual(broom.effects[1].damage_modifier, 5)

        broom.activate_item(context)

        self.assertEqual(
            rng.randint.call_args_list,
            [call(11, 13), call(7, 9)],
        )
        self.assertEqual(broom.effects[1].damage_modifier, 5)

    def test_brooms_own_independent_miss_bonus_state(self):
        rng = Mock()
        rng.random.side_effect = [0.5, 0.0, 0.5]
        rng.randint.return_value = 4
        first = Broom(item_key="broom1", player_id=0)
        second = Broom(item_key="broom2", player_id=0)
        owner = PlayerState(
            player_id=0,
            health=100,
            max_health=100,
            stamina=10.0,
            max_stamina=10.0,
            items={"broom1": first, "broom2": second},
        )
        opponent = PlayerState(
            player_id=1,
            health=100,
            max_health=100,
            stamina=10.0,
            max_stamina=10.0,
        )
        battle = BattleState(
            players=[owner, opponent],
            active_items=[first, second],
            frame_delta=1.7,
            rng=rng,
        )
        context = BattleContext(battle, first, owner, opponent)

        self.resolve_opponent_attack(context, accuracy=0)

        self.assertEqual(first.miss_damage_bonus, 2)
        self.assertEqual(second.miss_damage_bonus, 2)

        first.activate_item(context)

        self.assertEqual(first.miss_damage_bonus, 0)
        self.assertEqual(first.effects[1].damage_modifier, 0)
        self.assertEqual(second.miss_damage_bonus, 2)
        self.assertEqual(second.effects[1].damage_modifier, 2)

    def test_battle_step_applies_natural_stamina_regen_before_banana(self):
        banana, context, _ = self.make_banana_context(
            frame_delta=1.0,
            health=5,
            max_health=10,
            stamina=3.0,
            max_stamina=5.0,
        )
        banana.triggers[0].cooldown_progress = 4.0

        context.battle_state.step()

        self.assertEqual(context.owner.health, 9)
        self.assertEqual(context.owner.stamina, 5.0)
        self.assertAlmostEqual(
            banana.triggers[0].cooldown_progress,
            0.0,
        )

    def make_banana_context(
        self,
        frame_delta=1.0,
        health=5,
        max_health=10,
        stamina=2.0,
        max_stamina=5.0,
        linked_item_specs=(),
        unlinked_item_specs=(),
    ):
        banana = Banana(item_key="banana1", player_id=0)
        linked_items = {}
        owner_items = {"banana1": banana}

        for item_key, item_id, item_types in (
            tuple(linked_item_specs) + tuple(unlinked_item_specs)
        ):
            item = Mock()
            item.item_id = item_id
            item.item_types = item_types
            linked_items[item_key] = item
            owner_items[item_key] = item

        for item_key, _, _ in linked_item_specs:
            banana.add_linked_item(item_key)

        owner = PlayerState(
            player_id=0,
            health=health,
            max_health=max_health,
            stamina=stamina,
            max_stamina=max_stamina,
            items=owner_items,
        )
        opponent = PlayerState(
            player_id=1,
            health=10,
            max_health=10,
            stamina=5.0,
            max_stamina=5.0,
        )
        battle_state = BattleState(
            players=[owner, opponent],
            active_items=[banana],
            frame_delta=frame_delta,
        )
        context = BattleContext(
            battle_state,
            banana,
            owner,
            opponent,
        )
        return banana, context, linked_items

    def make_garlic_context(
        self,
        frame_delta=1.0,
        block=0,
        opponent_vampirism=0,
        rng=None,
        linked_item_specs=(),
        unlinked_item_specs=(),
    ):
        garlic = Garlic(item_key="garlic1", player_id=0)
        linked_items = {}
        owner_items = {"garlic1": garlic}

        for item_key, item_id, item_types in (
            tuple(linked_item_specs) + tuple(unlinked_item_specs)
        ):
            item = Mock()
            item.item_id = item_id
            item.item_types = item_types
            linked_items[item_key] = item
            owner_items[item_key] = item

        for item_key, _, _ in linked_item_specs:
            garlic.add_linked_item(item_key)

        owner = PlayerState(
            player_id=0,
            health=10,
            max_health=10,
            block=block,
            stamina=5.0,
            max_stamina=5.0,
            items=owner_items,
        )
        opponent = PlayerState(
            player_id=1,
            health=10,
            max_health=10,
            stamina=5.0,
            max_stamina=5.0,
        )
        opponent.buffs.Vampirism = opponent_vampirism
        if rng is None:
            rng = Mock()
            rng.random.return_value = 0.5
        battle_state = BattleState(
            players=[owner, opponent],
            active_items=[garlic],
            frame_delta=frame_delta,
            rng=rng,
        )
        context = BattleContext(
            battle_state,
            garlic,
            owner,
            opponent,
        )
        return garlic, context, linked_items, rng

    def make_pan_context(
        self,
        frame_delta=1.0,
        stamina=5.0,
        opponent_health=100,
        empower=0,
        rng=None,
        linked_item_specs=(),
        unlinked_item_specs=(),
    ):
        pan = Pan(item_key="pan1", player_id=0)
        linked_items = {}
        owner_items = {"pan1": pan}

        for item_key, item_id, item_types in (
            tuple(linked_item_specs) + tuple(unlinked_item_specs)
        ):
            item = Mock()
            item.item_id = item_id
            item.item_types = item_types
            linked_items[item_key] = item
            owner_items[item_key] = item

        for item_key, _, _ in linked_item_specs:
            pan.add_linked_item(item_key)

        owner = PlayerState(
            player_id=0,
            health=100,
            max_health=100,
            stamina=stamina,
            max_stamina=10.0,
            items=owner_items,
        )
        owner.buffs.Empower = empower
        opponent = PlayerState(
            player_id=1,
            health=opponent_health,
            max_health=opponent_health,
            stamina=10.0,
            max_stamina=10.0,
        )
        if rng is None:
            rng = Mock()
        battle_state = BattleState(
            players=[owner, opponent],
            active_items=[pan],
            frame_delta=frame_delta,
            rng=rng,
        )
        context = BattleContext(
            battle_state,
            pan,
            owner,
            opponent,
        )
        return pan, context, linked_items, rng

    def make_broom_context(
        self,
        frame_delta=1.0,
        stamina=5.0,
        opponent_health=100,
        opponent_blind=0,
        rng=None,
    ):
        broom = Broom(item_key="broom1", player_id=0)
        owner = PlayerState(
            player_id=0,
            health=100,
            max_health=100,
            stamina=stamina,
            max_stamina=10.0,
            items={"broom1": broom},
        )
        opponent = PlayerState(
            player_id=1,
            health=opponent_health,
            max_health=opponent_health,
            stamina=10.0,
            max_stamina=10.0,
        )
        opponent.debuffs.Blind = opponent_blind
        if rng is None:
            rng = Mock()
        battle_state = BattleState(
            players=[owner, opponent],
            active_items=[broom],
            frame_delta=frame_delta,
            rng=rng,
        )
        context = BattleContext(
            battle_state,
            broom,
            owner,
            opponent,
        )
        return broom, context, rng

    def resolve_opponent_attack(
        self,
        context,
        *,
        accuracy,
        attack_types=("melee",),
        min_damage=1,
        max_damage=1,
    ):
        event = AttackEvent(
            attacker=context.opponent,
            defender=context.owner,
            source_item=Mock(),
            attack_types=attack_types,
            min_damage=min_damage,
            max_damage=max_damage,
            accuracy=accuracy,
        )
        return context.battle_state.resolve_attack(event)

    def make_wooden_sword_context(
        self,
        rng,
        frame_delta,
        stamina,
    ):
        sword = WoodenSword(item_key="wooden_sword1", player_id=0)
        owner = PlayerState(
            player_id=0,
            health=10,
            max_health=10,
            stamina=stamina,
            max_stamina=5.0,
            items={"wooden_sword1": sword},
        )
        opponent = PlayerState(
            player_id=1,
            health=10,
            max_health=10,
            stamina=5.0,
            max_stamina=5.0,
        )
        battle_state = BattleState(
            players=[owner, opponent],
            active_items=[sword],
            frame_delta=frame_delta,
            rng=rng,
        )
        context = BattleContext(battle_state, sword, owner, opponent)
        return sword, context


if __name__ == "__main__":
    unittest.main()
