import unittest
from unittest.mock import Mock, call

from basic_backpack_v1 import ITEM_CATALOG, place_item
from battle_initializer_v1 import initialize_battle
from battle_module_v1 import (
    BattleContext,
    BattleState,
    ItemActivationContext,
    PlayerState,
)
from item_factory_registry_v1 import (
    ActivationTrigger,
    DEFAULT_ITEM_FACTORIES,
    GainMaxHealthEffect,
    SlimeActivationTrigger,
    Stone,
    Twine,
    WoodenSword,
)


def spy_on_activation_dispatch(battle_state):
    original_dispatch = battle_state.dispatch_item_activation
    dispatch_spy = Mock(wraps=original_dispatch)
    battle_state.dispatch_item_activation = dispatch_spy
    return dispatch_spy


class TwineItemFactoryV1Test(unittest.TestCase):
    def make_twine_state(
        self,
        *,
        health=10,
        max_health=20,
        neutral_count=0,
        include_non_neutral=False,
    ):
        source = WoodenSword(
            item_key="wooden_sword1",
            player_id=0,
        )
        twine = Twine(
            item_key="twine1",
            player_id=0,
        )
        twine.add_marker_item("star", source.item_key)
        items = {
            source.item_key: source,
            twine.item_key: twine,
        }
        for index in range(neutral_count):
            neutral = Stone(
                item_key=f"stone{index + 1}",
                player_id=0,
            )
            items[neutral.item_key] = neutral
            twine.add_marker_item("diamond", neutral.item_key)

        if include_non_neutral:
            non_neutral = Twine(
                item_key="twine2",
                player_id=0,
            )
            items[non_neutral.item_key] = non_neutral
            twine.add_marker_item("diamond", non_neutral.item_key)

        owner = PlayerState(
            player_id=0,
            health=health,
            max_health=max_health,
            items=items,
        )
        opponent = PlayerState(
            player_id=1,
            health=20,
            max_health=20,
        )
        battle = BattleState(players=[owner, opponent])
        context = ItemActivationContext(
            battle_state=battle,
            item=twine,
            owner=owner,
            opponent=opponent,
            source_item=source,
        )
        return source, twine, battle, owner, opponent, context

    def test_gain_max_health_effect_rejects_invalid_amounts(self):
        for invalid in (0, -1, 1.0, True, None):
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    GainMaxHealthEffect(invalid)

    def test_gain_max_health_increases_current_and_max_health(self):
        _, twine, battle, owner, opponent, _ = (
            self.make_twine_state(health=5, max_health=10)
        )
        effect = GainMaxHealthEffect(2)
        battle.heal = Mock(wraps=battle.heal)

        result = effect.apply(
            BattleContext(
                battle_state=battle,
                item=twine,
                owner=owner,
                opponent=opponent,
            )
        )

        self.assertTrue(result)
        self.assertEqual(owner.health, 7)
        self.assertEqual(owner.max_health, 12)
        battle.heal.assert_not_called()

    def test_twine_metadata_components_and_factory_registration(self):
        twine = DEFAULT_ITEM_FACTORIES["twine"](
            item_id="twine",
            item_key="twine1",
            player_id=0,
        )

        self.assertIsInstance(twine, Twine)
        self.assertEqual(twine.item_id, "twine")
        self.assertEqual(twine.display_name, "Twine")
        self.assertEqual(twine.item_classes, ("Adventurer",))
        self.assertEqual(twine.rarity, "Common")
        self.assertEqual(twine.cost, 2)
        self.assertEqual(twine.item_types, ("Accessory",))
        self.assertEqual(twine.icon_types, ())
        self.assertFalse(twine.is_active_item)
        self.assertEqual(twine.socket_count, 0)
        self.assertIsInstance(twine.triggers[0], ActivationTrigger)
        self.assertNotIsInstance(
            twine.triggers[0],
            SlimeActivationTrigger,
        )
        self.assertEqual(twine.triggers[0].marker_type, "star")
        self.assertIsInstance(twine.effects[0], GainMaxHealthEffect)
        self.assertEqual(twine.effects[0].amount, 2)
        self.assertIsNone(twine.neutral_item_count)

    def test_twine_instances_own_independent_components_and_caches(self):
        first = Twine(item_key="twine1", player_id=0)
        second = Twine(item_key="twine2", player_id=0)

        first.neutral_item_count = 2

        self.assertIsNot(first.triggers[0], second.triggers[0])
        self.assertIsNot(first.effects[0], second.effects[0])
        self.assertEqual(first.neutral_item_count, 2)
        self.assertIsNone(second.neutral_item_count)

    def test_twine_prepares_only_diamond_neutral_item_count(self):
        _, twine, battle, _, _, context = self.make_twine_state(
            neutral_count=2,
            include_non_neutral=True,
        )
        battle.rng = Mock()
        battle.rng.random.return_value = 0.99

        twine.activate_item(context)

        self.assertEqual(twine.neutral_item_count, 2)
        battle.rng.random.assert_called_once_with()

    def test_twine_keeps_first_cached_neutral_item_count(self):
        _, twine, battle, owner, _, context = self.make_twine_state(
            neutral_count=1,
        )
        battle.rng = Mock()
        battle.rng.random.side_effect = [0.99, 0.40]

        twine.activate_item(context)
        second_neutral = Stone(
            item_key="stone2",
            player_id=0,
        )
        owner.items[second_neutral.item_key] = second_neutral
        twine.add_marker_item("diamond", second_neutral.item_key)
        twine.activate_item(context)

        self.assertEqual(twine.neutral_item_count, 1)
        self.assertEqual(owner.health, 10)
        self.assertEqual(owner.max_health, 20)

    def test_twine_invalid_activation_does_not_prepare_count(self):
        _, twine, battle, owner, opponent, _ = self.make_twine_state(
            neutral_count=1,
        )
        battle.rng = Mock()

        twine.run_effect(
            [False],
            BattleContext(
                battle_state=battle,
                item=twine,
                owner=owner,
                opponent=opponent,
            ),
        )

        self.assertIsNone(twine.neutral_item_count)
        battle.rng.random.assert_not_called()

    def test_twine_diamond_only_activation_does_not_roll(self):
        source, twine, battle, owner, _, _ = self.make_twine_state()
        twine.marker_items["star"].clear()
        twine.add_marker_item("diamond", source.item_key)
        battle.rng = Mock()

        battle.dispatch_item_activation(source)

        self.assertIsNone(twine.neutral_item_count)
        self.assertEqual(owner.health, 10)
        self.assertEqual(owner.max_health, 20)
        battle.rng.random.assert_not_called()

    def test_twine_run_effect_uses_strict_random_boundary(self):
        _, twine, battle, owner, opponent, _ = self.make_twine_state()
        context = BattleContext(
            battle_state=battle,
            item=twine,
            owner=owner,
            opponent=opponent,
        )
        battle.rng = Mock()
        battle.rng.random.side_effect = [0.199, 0.20]

        twine.run_effect([True], context)
        twine.run_effect([True], context)

        self.assertEqual(owner.health, 12)
        self.assertEqual(owner.max_health, 22)

    def test_twine_run_effect_caps_chance_at_one(self):
        _, twine, battle, owner, opponent, _ = self.make_twine_state()
        twine.neutral_item_count = 10
        battle.rng = Mock()
        battle.rng.random.return_value = 0.999

        twine.run_effect(
            [True],
            BattleContext(
                battle_state=battle,
                item=twine,
                owner=owner,
                opponent=opponent,
            ),
        )

        self.assertEqual(owner.health, 12)
        self.assertEqual(owner.max_health, 22)

    def test_twine_catalog_rotates_one_star_and_three_diamonds(self):
        expected = {
            0: (
                [(3, 3)],
                [(4, 3)],
                [(0, 3), (1, 3), (2, 3)],
            ),
            90: (
                [(3, 3)],
                [(3, 4)],
                [(3, 0), (3, 1), (3, 2)],
            ),
            180: (
                [(3, 3)],
                [(2, 3)],
                [(6, 3), (5, 3), (4, 3)],
            ),
            270: (
                [(3, 3)],
                [(3, 2)],
                [(3, 6), (3, 5), (3, 4)],
            ),
        }

        for rotation, cells in expected.items():
            with self.subTest(rotation=rotation):
                placed = place_item(
                    ITEM_CATALOG["twine"],
                    {
                        "item_key": "twine1",
                        "x": 3,
                        "y": 3,
                        "rotation": rotation,
                    },
                )

                self.assertEqual(placed["occupied_cells"], cells[0])
                self.assertEqual(placed["star_cells"], cells[1])
                self.assertEqual(placed["diamond_cells"], cells[2])
                self.assertEqual(placed["triangle_cells"], [])

    def test_twine_star_activation_success_gains_health_and_emits_once(
        self,
    ):
        source, twine, battle, owner, _, _ = self.make_twine_state()
        battle.rng = Mock()
        battle.rng.random.return_value = 0.0
        dispatch_spy = spy_on_activation_dispatch(battle)

        battle.dispatch_item_activation(source)

        self.assertEqual(owner.health, 12)
        self.assertEqual(owner.max_health, 22)
        self.assertEqual(
            dispatch_spy.call_args_list,
            [call(source), call(twine)],
        )

    def test_twine_failed_roll_changes_nothing_and_does_not_emit(self):
        source, twine, battle, owner, _, _ = self.make_twine_state()
        battle.rng = Mock()
        battle.rng.random.return_value = 0.20
        dispatch_spy = spy_on_activation_dispatch(battle)

        battle.dispatch_item_activation(source)

        self.assertEqual(owner.health, 10)
        self.assertEqual(owner.max_health, 20)
        self.assertEqual(dispatch_spy.call_args_list, [call(source)])
        self.assertEqual(twine.neutral_item_count, 0)

    def test_twine_is_passive_and_not_added_to_active_items(self):
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
                            "item_id": "twine",
                            "x": 3,
                            "y": 3,
                            "rotation": 0,
                        }
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

        twine = battle.players[0].items["twine1"]
        self.assertIsInstance(twine, Twine)
        self.assertNotIn(twine, battle.active_items)


if __name__ == "__main__":
    unittest.main()
