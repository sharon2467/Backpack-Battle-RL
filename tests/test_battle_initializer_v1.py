import unittest

from battle_initializer_v1 import initialize_battle
from battle_module_v1 import BattleItem


class TestBattleItem(BattleItem):
    def __init__(self, **kwargs):
        super().__init__(
            triggers=["test_trigger"],
            effects=["test_effect"],
            **kwargs,
        )

    def update_triggers(self, context):
        self.triggered = True

    def run_own_effects(self, context):
        pass


def make_factory(is_active_item=False, **overrides):
    def factory(item_id, item_key, player_id):
        if "return_value" in overrides:
            return overrides["return_value"]
        return TestBattleItem(
            item_id=overrides.get("item_id", item_id),
            item_key=overrides.get("item_key", item_key),
            player_id=overrides.get("player_id", player_id),
            is_active_item=is_active_item,
        )

    return factory


class BattleInitializerV1Test(unittest.TestCase):
    def test_requires_exactly_two_players(self):
        with self.assertRaises(ValueError):
            initialize_battle([], {}, item_catalog={})

        with self.assertRaises(ValueError):
            initialize_battle(
                [
                    {"player_id": 0, "health": 25, "placements": []},
                    {"player_id": 1, "health": 25, "placements": []},
                    {"player_id": 2, "health": 25, "placements": []},
                ],
                {},
                item_catalog={},
            )

    def test_requires_unique_player_ids(self):
        with self.assertRaises(ValueError):
            initialize_battle(
                [
                    {"player_id": 0, "health": 25, "placements": []},
                    {"player_id": 0, "health": 25, "placements": []},
                ],
                {},
                item_catalog={},
            )

    def test_builds_player_state_items_as_keyed_dict(self):
        item_catalog = {
            "stone": {"item_id": "stone", "shape_cells": [(0, 0)]},
        }
        battle = initialize_battle(
            [
                {
                    "player_id": 0,
                    "health": 25,
                    "placements": [
                        {"item_id": "stone", "x": 0, "y": 0, "rotation": 0},
                        {"item_id": "stone", "x": 1, "y": 0, "rotation": 0},
                    ],
                },
                {"player_id": 1, "health": 25, "placements": []},
            ],
            {"stone": make_factory()},
            item_catalog=item_catalog,
        )

        player = battle.players[0]
        self.assertEqual(player.player_id, 0)
        self.assertEqual(player.health, 25)
        self.assertEqual(list(player.items), ["stone1", "stone2"])
        self.assertEqual(player.items["stone1"].item_id, "stone")
        self.assertEqual(player.items["stone1"].item_key, "stone1")
        self.assertEqual(player.items["stone1"].player_id, 0)

    def test_marker_links_are_attached_as_target_keys(self):
        item_catalog = {
            "source": {
                "item_id": "source",
                "shape_cells": [(0, 0)],
                "star_cells": [(1, 0)],
                "diamond_cells": [(2, 0)],
                "triangle_cells": [(3, 0)],
            },
            "target": {"item_id": "target", "shape_cells": [(0, 0)]},
        }
        battle = initialize_battle(
            [
                {
                    "player_id": 0,
                    "health": 25,
                    "placements": [
                        {"item_id": "source", "x": 0, "y": 0, "rotation": 0},
                        {"item_id": "target", "x": 1, "y": 0, "rotation": 0},
                        {"item_id": "target", "x": 2, "y": 0, "rotation": 0},
                        {"item_id": "target", "x": 3, "y": 0, "rotation": 0},
                    ],
                },
                {"player_id": 1, "health": 25, "placements": []},
            ],
            {
                "source": make_factory(),
                "target": make_factory(),
            },
            item_catalog=item_catalog,
        )

        source = battle.players[0].items["source1"]
        self.assertEqual(source.linked_items, ["target1", "target2", "target3"])

    def test_duplicate_marker_links_are_deduplicated_by_battle_item_method(self):
        item_catalog = {
            "source": {
                "item_id": "source",
                "shape_cells": [(0, 0)],
                "star_cells": [(1, 0)],
                "diamond_cells": [(1, 0)],
            },
            "target": {"item_id": "target", "shape_cells": [(0, 0)]},
        }
        battle = initialize_battle(
            [
                {
                    "player_id": 0,
                    "health": 25,
                    "placements": [
                        {"item_id": "source", "x": 0, "y": 0, "rotation": 0},
                        {"item_id": "target", "x": 1, "y": 0, "rotation": 0},
                    ],
                },
                {"player_id": 1, "health": 25, "placements": []},
            ],
            {
                "source": make_factory(),
                "target": make_factory(),
            },
            item_catalog=item_catalog,
        )

        source = battle.players[0].items["source1"]
        self.assertEqual(source.linked_items, ["target1"])

    def test_active_items_are_ordered_by_player_and_item_insertion_order(self):
        item_catalog = {
            "active": {"item_id": "active", "shape_cells": [(0, 0)]},
            "inactive": {"item_id": "inactive", "shape_cells": [(0, 0)]},
        }
        battle = initialize_battle(
            [
                {
                    "player_id": 0,
                    "health": 25,
                    "placements": [
                        {"item_id": "inactive", "x": 0, "y": 0, "rotation": 0},
                        {"item_id": "active", "x": 1, "y": 0, "rotation": 0},
                    ],
                },
                {
                    "player_id": 1,
                    "health": 25,
                    "placements": [
                        {"item_id": "active", "x": 0, "y": 0, "rotation": 0},
                    ],
                },
            ],
            {
                "active": make_factory(is_active_item=True),
                "inactive": make_factory(is_active_item=False),
            },
            item_catalog=item_catalog,
        )

        self.assertEqual(
            [(item.player_id, item.item_key) for item in battle.active_items],
            [(0, "active1"), (1, "active1")],
        )

    def test_missing_factory_fails(self):
        item_catalog = {
            "stone": {"item_id": "stone", "shape_cells": [(0, 0)]},
        }

        with self.assertRaises(ValueError):
            initialize_battle(
                [
                    {"player_id": 0, "health": 25, "placements": [
                        {"item_id": "stone", "x": 0, "y": 0, "rotation": 0},
                    ]},
                    {"player_id": 1, "health": 25, "placements": []},
                ],
                {},
                item_catalog=item_catalog,
            )

    def test_factory_returning_non_battle_item_fails(self):
        item_catalog = {
            "stone": {"item_id": "stone", "shape_cells": [(0, 0)]},
        }

        with self.assertRaises(ValueError):
            initialize_battle(
                [
                    {"player_id": 0, "health": 25, "placements": [
                        {"item_id": "stone", "x": 0, "y": 0, "rotation": 0},
                    ]},
                    {"player_id": 1, "health": 25, "placements": []},
                ],
                {"stone": make_factory(return_value=object())},
                item_catalog=item_catalog,
            )

    def test_factory_returning_wrong_item_identity_fails(self):
        item_catalog = {
            "stone": {"item_id": "stone", "shape_cells": [(0, 0)]},
        }

        with self.assertRaises(ValueError):
            initialize_battle(
                [
                    {"player_id": 0, "health": 25, "placements": [
                        {"item_id": "stone", "x": 0, "y": 0, "rotation": 0},
                    ]},
                    {"player_id": 1, "health": 25, "placements": []},
                ],
                {"stone": make_factory(item_key="wrong1")},
                item_catalog=item_catalog,
            )


if __name__ == "__main__":
    unittest.main()
