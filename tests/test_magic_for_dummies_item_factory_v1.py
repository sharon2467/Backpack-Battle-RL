import unittest
from unittest.mock import Mock

from basic_backpack_v1 import ITEM_CATALOG, place_item
from battle_initializer_v1 import initialize_battle
from battle_module_v1 import (
    BattleContext,
    BattleItem,
    BattleState,
    PlayerState,
)
from item_effects_v1 import GainMaxHealthEffect, UseBuffEffect
from item_factory_registry_v1 import (
    DEFAULT_ITEM_FACTORIES,
    MagicForDummies,
    Stone,
)
from item_triggers_v1 import CooldownTrigger


class MagicForDummiesItemFactoryV1Test(unittest.TestCase):
    def make_state(
        self,
        *,
        mana=1,
        health=10,
        max_health=20,
    ):
        guide = MagicForDummies(
            item_key="magic_for_dummies1",
            player_id=0,
        )
        owner = PlayerState(
            player_id=0,
            health=health,
            max_health=max_health,
            items={guide.item_key: guide},
        )
        owner.buffs.Mana = mana
        opponent = PlayerState(
            player_id=1,
            health=20,
            max_health=20,
        )
        battle = BattleState(
            players=[owner, opponent],
            active_items=[guide],
        )
        context = BattleContext(
            battle_state=battle,
            item=guide,
            owner=owner,
            opponent=opponent,
        )
        return guide, battle, owner, opponent, context

    def add_item(
        self,
        guide,
        owner,
        *,
        item_key,
        item_types,
        is_crafted=False,
        starred=True,
    ):
        item = Stone(item_key=item_key, player_id=owner.player_id)
        item.item_types = item_types
        item.is_crafted = is_crafted
        owner.items[item.item_key] = item
        if starred:
            guide.add_marker_item("star", item.item_key)
        return item

    def test_battle_item_defaults_to_not_crafted(self):
        self.assertFalse(BattleItem.is_crafted)
        self.assertFalse(Stone(item_key="stone1", player_id=0).is_crafted)

    def test_metadata_components_and_instance_isolation(self):
        guide = DEFAULT_ITEM_FACTORIES["magic_for_dummies"](
            item_id="magic_for_dummies",
            item_key="magic_for_dummies1",
            player_id=0,
        )
        second = MagicForDummies(
            item_key="magic_for_dummies2",
            player_id=0,
        )

        self.assertIsInstance(guide, MagicForDummies)
        self.assertEqual(guide.item_id, "magic_for_dummies")
        self.assertEqual(guide.display_name, "Magic For Dummies")
        self.assertEqual(guide.item_classes, ("Mage",))
        self.assertEqual(guide.rarity, "Common")
        self.assertEqual(guide.cost, 4)
        self.assertEqual(guide.item_types, ("Book",))
        self.assertEqual(guide.icon_types, ("magic",))
        self.assertTrue(guide.is_active_item)
        self.assertFalse(guide.is_crafted)
        self.assertEqual(guide.socket_count, 0)
        self.assertIsInstance(guide.triggers[0], CooldownTrigger)
        self.assertEqual(guide.triggers[0].cooldown_seconds, 5.0)
        self.assertIsInstance(guide.effects[0], UseBuffEffect)
        self.assertEqual(guide.effects[0].buff_name, "Mana")
        self.assertEqual(guide.effects[0].amount, 1)
        self.assertIsInstance(guide.effects[1], GainMaxHealthEffect)
        self.assertEqual(guide.effects[1].amount, 8)
        self.assertIsNone(guide.spell_weight)
        self.assertIsNot(guide.triggers[0], second.triggers[0])
        self.assertIsNot(guide.effects[0], second.effects[0])
        self.assertIsNot(guide.effects[1], second.effects[1])

    def test_cooldown_does_nothing_before_five_seconds(self):
        guide, battle, owner, _, context = self.make_state()
        battle.frame_delta = 4.9
        battle.dispatch_item_activation = Mock(
            wraps=battle.dispatch_item_activation
        )

        guide.activate_item(context)

        self.assertEqual(owner.buffs.Mana, 1)
        self.assertEqual(owner.health, 10)
        self.assertEqual(owner.max_health, 20)
        self.assertIsNone(guide.spell_weight)
        battle.dispatch_item_activation.assert_not_called()

    def test_success_uses_mana_and_gains_base_max_health(self):
        guide, battle, owner, _, context = self.make_state()
        battle.frame_delta = 5.0
        battle.dispatch_item_activation = Mock(
            wraps=battle.dispatch_item_activation
        )

        guide.activate_item(context)

        self.assertEqual(owner.buffs.Mana, 0)
        self.assertEqual(owner.health, 18)
        self.assertEqual(owner.max_health, 28)
        self.assertEqual(guide.spell_weight, 0)
        battle.dispatch_item_activation.assert_called_once_with(guide)

    def test_insufficient_mana_skips_effect_and_activation(self):
        guide, battle, owner, _, context = self.make_state(mana=0)
        battle.frame_delta = 5.0
        battle.dispatch_item_activation = Mock(
            wraps=battle.dispatch_item_activation
        )

        guide.activate_item(context)

        self.assertEqual(owner.health, 10)
        self.assertEqual(owner.max_health, 20)
        self.assertIsNone(guide.spell_weight)
        battle.dispatch_item_activation.assert_not_called()

        owner.buffs.Mana = 1
        guide.activate_item(context)

        self.assertEqual(owner.buffs.Mana, 0)
        self.assertEqual(owner.health, 18)
        self.assertEqual(owner.max_health, 28)
        battle.dispatch_item_activation.assert_called_once_with(guide)

    def test_counts_only_starred_spell_instances(self):
        guide, battle, owner, _, context = self.make_state()
        self.add_item(
            guide,
            owner,
            item_key="spell1",
            item_types=("Spell",),
        )
        self.add_item(
            guide,
            owner,
            item_key="book1",
            item_types=("Book",),
            is_crafted=True,
        )
        self.add_item(
            guide,
            owner,
            item_key="accessory1",
            item_types=("Accessory",),
        )
        self.add_item(
            guide,
            owner,
            item_key="spell2",
            item_types=("Spell",),
            starred=False,
        )
        battle.frame_delta = 5.0

        guide.activate_item(context)

        self.assertEqual(guide.spell_weight, 1)
        self.assertEqual(guide.effects[1].amount, 11)
        self.assertEqual(owner.health, 21)
        self.assertEqual(owner.max_health, 31)

    def test_crafted_spell_counts_twice(self):
        guide, battle, owner, _, context = self.make_state()
        self.add_item(
            guide,
            owner,
            item_key="crafted_spell1",
            item_types=("Spell",),
            is_crafted=True,
        )
        battle.frame_delta = 5.0

        guide.activate_item(context)

        self.assertEqual(guide.spell_weight, 2)
        self.assertEqual(owner.health, 24)
        self.assertEqual(owner.max_health, 34)

    def test_same_spell_covering_multiple_stars_counts_once(self):
        guide, battle, owner, _, context = self.make_state()
        spell = self.add_item(
            guide,
            owner,
            item_key="spell1",
            item_types=("Spell",),
        )
        guide.add_marker_item("star", spell.item_key)
        battle.frame_delta = 5.0

        guide.activate_item(context)

        self.assertEqual(guide.marker_items["star"], [spell.item_key])
        self.assertEqual(guide.spell_weight, 1)
        self.assertEqual(owner.max_health, 31)

    def test_spell_weight_is_cached_per_item_instance(self):
        guide, battle, owner, _, context = self.make_state(mana=2)
        self.add_item(
            guide,
            owner,
            item_key="spell1",
            item_types=("Spell",),
        )
        battle.frame_delta = 5.0

        guide.activate_item(context)
        self.add_item(
            guide,
            owner,
            item_key="crafted_spell1",
            item_types=("Spell",),
            is_crafted=True,
        )
        guide.activate_item(context)

        second = MagicForDummies(
            item_key="magic_for_dummies2",
            player_id=0,
        )
        self.assertEqual(guide.spell_weight, 1)
        self.assertEqual(owner.health, 32)
        self.assertEqual(owner.max_health, 42)
        self.assertIsNone(second.spell_weight)

    def test_initializer_builds_active_item_and_star_links(self):
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
                            "item_id": "magic_for_dummies",
                            "x": 3,
                            "y": 3,
                            "rotation": 0,
                        },
                        {
                            "item_id": "stone",
                            "x": 3,
                            "y": 5,
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

        guide = battle.players[0].items["magic_for_dummies1"]
        self.assertIsInstance(guide, MagicForDummies)
        self.assertIn(guide, battle.active_items)
        self.assertEqual(guide.marker_items["star"], ["stone1"])
        self.assertEqual(guide.linked_items, ["stone1"])

    def test_catalog_rotates_two_cell_shape_and_six_stars(self):
        expected = {
            0: (
                [(3, 4), (3, 3)],
                [(3, 5), (2, 4), (4, 4), (2, 3), (4, 3), (3, 2)],
            ),
            90: (
                [(2, 3), (3, 3)],
                [(1, 3), (2, 2), (2, 4), (3, 2), (3, 4), (4, 3)],
            ),
            180: (
                [(3, 2), (3, 3)],
                [(3, 1), (4, 2), (2, 2), (4, 3), (2, 3), (3, 4)],
            ),
            270: (
                [(4, 3), (3, 3)],
                [(5, 3), (4, 4), (4, 2), (3, 4), (3, 2), (2, 3)],
            ),
        }

        for rotation, cells in expected.items():
            with self.subTest(rotation=rotation):
                placed = place_item(
                    ITEM_CATALOG["magic_for_dummies"],
                    {
                        "item_key": "magic_for_dummies1",
                        "x": 3,
                        "y": 3,
                        "rotation": rotation,
                    },
                )

                self.assertEqual(placed["occupied_cells"], cells[0])
                self.assertEqual(placed["star_cells"], cells[1])
                self.assertEqual(placed["diamond_cells"], [])
                self.assertEqual(placed["triangle_cells"], [])


if __name__ == "__main__":
    unittest.main()
