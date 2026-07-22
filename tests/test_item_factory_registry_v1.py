import unittest
from unittest.mock import Mock

from basic_backpack_v1 import ITEM_CATALOG
from battle_initializer_v1 import initialize_battle
from battle_module_v1 import (
    ATTACK_PHASE_ON_ATTACKED,
    BattleContext,
    BattleState,
    PlayerState,
)
from item_factory_registry_v1 import (
    CooldownTrigger,
    DEFAULT_ITEM_FACTORIES,
    MeleeAttackEffect,
    OnAttackedTrigger,
    PreventAttackDamageEffect,
    RemoveOpponentStaminaEffect,
    StaminaConsumptionEffect,
    WoodenBuckler,
    WoodenSword,
)


class ItemFactoryRegistryV1Test(unittest.TestCase):
    def make_context(
        self,
        frame_delta=0.1,
        stamina=0.0,
        max_stamina=0.0,
    ):
        owner = PlayerState(
            player_id=0,
            health=10,
            stamina=stamina,
            max_stamina=max_stamina,
        )
        opponent = PlayerState(player_id=1, health=10)
        battle_state = BattleState(
            players=[owner, opponent],
            frame_delta=frame_delta,
        )
        return BattleContext(battle_state, None, owner, opponent)

    def test_default_item_factories_is_a_registry_dict(self):
        self.assertIsInstance(DEFAULT_ITEM_FACTORIES, dict)

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

        result = sword.run_effects(context)

        self.assertFalse(result)
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

        result = sword.run_effects(context)

        self.assertTrue(result)
        self.assertAlmostEqual(context.owner.stamina, 1.0)
        self.assertEqual(context.opponent.health, 8)
        self.assertAlmostEqual(sword.triggers[0].cooldown_progress, 0.0)
        rng.random.assert_called_once_with()
        rng.randint.assert_called_once_with(1, 3)

    def test_wooden_sword_pays_stamina_but_returns_false_on_miss(self):
        rng = Mock()
        rng.random.return_value = 0.95
        sword, context = self.make_wooden_sword_context(
            rng=rng,
            frame_delta=1.4,
            stamina=2.0,
        )

        result = sword.run_effects(context)

        self.assertFalse(result)
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

        first_result = sword.run_effects(context)

        self.assertFalse(first_result)
        self.assertAlmostEqual(context.owner.stamina, 0.5)
        self.assertAlmostEqual(sword.triggers[0].cooldown_progress, 0.0)
        self.assertEqual(context.opponent.health, 10)
        rng.random.assert_not_called()
        rng.randint.assert_not_called()

        context.owner.stamina = 2.0
        context.battle_state.frame_delta = 0.1
        second_result = sword.run_effects(context)

        self.assertFalse(second_result)
        self.assertAlmostEqual(sword.triggers[0].cooldown_progress, 0.1)
        rng.random.assert_not_called()

    def test_initializer_builds_wooden_sword_as_an_active_item(self):
        battle = initialize_battle(
            [
                {
                    "player_id": 0,
                    "health": 10,
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
            stamina=stamina,
            max_stamina=5.0,
            items={"wooden_sword1": sword},
        )
        opponent = PlayerState(
            player_id=1,
            health=10,
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
