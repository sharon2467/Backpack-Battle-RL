import unittest

from battle_module_v1 import BattleItem, BattleState, PlayerState, evaluate_layout


class RecordingItem(BattleItem):
    def __init__(self, name, log, should_trigger=True, **kwargs):
        super().__init__(
            item_id=name,
            triggers=["test_trigger"],
            effects=["test_effect"],
            **kwargs,
        )
        self.name = name
        self.log = log
        self.should_trigger = should_trigger

    def update_triggers(self, context):
        self.log.append(f"update:{self.item_key}")
        self.triggered = self.should_trigger

    def run_own_effects(self, context):
        self.log.append(f"effect:{self.item_key}")


class BattleModuleV1Test(unittest.TestCase):
    def test_battle_item_requires_at_least_one_trigger(self):
        with self.assertRaises(ValueError):
            BattleItem(item_id="empty", item_key="empty1", triggers=[], effects=["effect"])

    def test_battle_item_requires_at_least_one_effect(self):
        with self.assertRaises(ValueError):
            BattleItem(item_id="empty", item_key="empty1", triggers=["trigger"], effects=[])

    def test_battle_item_stores_player_id_and_item_key(self):
        item = BattleItem(
            item_id="owned_item",
            item_key="owned_item1",
            player_id=1,
            triggers=["trigger"],
            effects=["effect"],
        )

        self.assertEqual(item.player_id, 1)
        self.assertEqual(item.item_key, "owned_item1")

    def test_add_linked_item_stores_keys_once_in_first_seen_order(self):
        item = BattleItem(
            item_id="source",
            item_key="source1",
            triggers=["trigger"],
            effects=["effect"],
        )

        item.add_linked_item("target1")
        item.add_linked_item("target2")
        item.add_linked_item("target1")

        self.assertEqual(item.linked_items, ["target1", "target2"])

    def test_battle_state_step_updates_only_active_items_directly(self):
        log = []
        active_item = RecordingItem("active", log, item_key="active1", player_id=0, is_active_item=True)
        inactive_item = RecordingItem("inactive", log, item_key="inactive1", player_id=0, is_active_item=False)
        owner = PlayerState(player_id=0, health=10, items={
            "active1": active_item,
            "inactive1": inactive_item,
        })
        opponent = PlayerState(player_id=1, health=10)
        battle = BattleState(players=[owner, opponent], active_items=[active_item])

        battle.step()

        self.assertEqual(log, ["update:active1", "effect:active1"])
        self.assertEqual(battle.frame, 1)
        self.assertEqual(battle.time, 1.0)

    def test_run_effects_recursively_updates_linked_items_by_key(self):
        log = []
        active_item = RecordingItem("active", log, item_key="active1", player_id=0, is_active_item=True)
        linked_item = RecordingItem("linked", log, item_key="linked1", player_id=0)
        nested_item = RecordingItem("nested", log, item_key="nested1", player_id=0)
        active_item.add_linked_item("linked1")
        linked_item.add_linked_item("nested1")
        owner = PlayerState(player_id=0, health=10, items={
            "active1": active_item,
            "linked1": linked_item,
            "nested1": nested_item,
        })
        opponent = PlayerState(player_id=1, health=10)
        battle = BattleState(players=[owner, opponent], active_items=[active_item])

        battle.step()

        self.assertEqual(
            log,
            [
                "update:active1",
                "effect:active1",
                "update:linked1",
                "effect:linked1",
                "update:nested1",
                "effect:nested1",
            ],
        )

    def test_untriggered_linked_item_does_not_run_effects(self):
        log = []
        active_item = RecordingItem("active", log, item_key="active1", player_id=0, is_active_item=True)
        linked_item = RecordingItem("linked", log, item_key="linked1", player_id=0, should_trigger=False)
        active_item.add_linked_item("linked1")
        owner = PlayerState(player_id=0, health=10, items={
            "active1": active_item,
            "linked1": linked_item,
        })
        opponent = PlayerState(player_id=1, health=10)
        battle = BattleState(players=[owner, opponent], active_items=[active_item])

        battle.step()

        self.assertEqual(log, ["update:active1", "effect:active1", "update:linked1"])

    def test_player_state_uses_independent_mutable_defaults(self):
        first_player = PlayerState(player_id=0)
        second_player = PlayerState(player_id=1)

        first_player.buffs["heat"] = 1
        first_player.items["item1"] = "item"

        self.assertEqual(second_player.buffs, {})
        self.assertEqual(second_player.items, {})

    def test_battle_state_sets_winner_when_one_player_remains_alive(self):
        winner = PlayerState(player_id=0, health=10)
        loser = PlayerState(player_id=1, health=0)
        battle = BattleState(players=[winner, loser])

        battle.check_battle_end()

        self.assertEqual(battle.winner, 0)

    def test_evaluate_layout_is_declared_but_not_scored_yet(self):
        with self.assertRaises(NotImplementedError):
            evaluate_layout([], opponent=None)


if __name__ == "__main__":
    unittest.main()
