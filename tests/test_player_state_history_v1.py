import json
import unittest
from copy import deepcopy

from battle_module_v1 import (
    BattleItem,
    BattleState,
    BuffSlot,
    DebuffSlot,
    Effect,
    PlayerState,
    Trigger,
    serialize_player_state,
)
from main_v1 import (
    compress_player_state_history,
    run_battle_from_config,
)


class AlwaysTrigger(Trigger):
    def update(self, context):
        return True


class NoopEffect(Effect):
    def apply(self, context):
        return True


class LethalItem(BattleItem):
    def __init__(self, item_key="lethal1", player_id=0):
        super().__init__(
            item_id="lethal",
            item_key=item_key,
            player_id=player_id,
            is_active_item=True,
            triggers=[AlwaysTrigger()],
            effects=[NoopEffect()],
        )

    def run_effect(self, trigger_results, context):
        context.battle_state.commit_health_reduction(
            context.opponent,
            blocked_damage=0,
            health_damage=context.opponent.health,
        )


class ErrorItem(BattleItem):
    def __init__(self, item_key="error1", player_id=0):
        super().__init__(
            item_id="error",
            item_key=item_key,
            player_id=player_id,
            is_active_item=True,
            triggers=[AlwaysTrigger()],
            effects=[NoopEffect()],
        )

    def run_effect(self, trigger_results, context):
        raise RuntimeError("unexpected item failure")


def minimal_config(settings=None):
    return {
        "schema_version": "battle_run_v1",
        "settings": settings or {},
        "players": [
            {
                "player_id": 0,
                "class_id": "ranger",
                "health": 25,
                "max_health": 25,
                "stamina": 5.0,
                "max_stamina": 5.0,
                "placements": [],
            },
            {
                "player_id": 1,
                "class_id": "reaper",
                "health": 25,
                "max_health": 25,
                "stamina": 5.0,
                "max_stamina": 5.0,
                "placements": [],
            },
        ],
    }


def history_record(sequence, frame, time, players):
    return {
        "sequence": sequence,
        "frame": frame,
        "time": time,
        "players": deepcopy(players),
    }


def history_player(
    player_id=0,
    *,
    health=10,
    max_health=10,
    block=0,
    fatigue_damage=0,
    stamina=5.0,
    max_stamina=5.0,
    buffs=None,
    debuffs=None,
):
    return {
        "player_id": player_id,
        "health": health,
        "max_health": max_health,
        "block": block,
        "fatigue_damage": fatigue_damage,
        "stamina": stamina,
        "max_stamina": max_stamina,
        "buffs": {} if buffs is None else dict(buffs),
        "debuffs": {} if debuffs is None else dict(debuffs),
    }


class PlayerStateHistoryV1Test(unittest.TestCase):
    def test_new_battle_states_have_independent_empty_player_state_histories(
        self,
    ):
        first = BattleState()
        second = BattleState()

        first.player_state_history.append({"sequence": 0})

        self.assertEqual(second.player_state_history, [])

    def test_serialize_player_state_copies_supported_combat_fields_without_backpack_state(
        self,
    ):
        player = PlayerState(
            player_id="player-a",
            health=17,
            max_health=25,
            block=3,
            fatigue_damage=2,
            stamina=4.5,
            max_stamina=5.0,
            buffs=BuffSlot(Heat=2, Mana=3),
            debuffs=DebuffSlot(Poison=1, Blind=2),
            items={"must_not_be_read": object()},
        )

        snapshot = serialize_player_state(player)

        self.assertEqual(
            snapshot,
            {
                "player_id": "player-a",
                "health": 17,
                "max_health": 25,
                "block": 3,
                "fatigue_damage": 2,
                "stamina": 4.5,
                "max_stamina": 5.0,
                "buffs": {
                    "Empower": 0,
                    "Heat": 2,
                    "Luck": 0,
                    "Mana": 3,
                    "Regeneration": 0,
                    "Spikes": 0,
                    "Vampirism": 0,
                },
                "debuffs": {
                    "Poison": 1,
                    "Blind": 2,
                    "Cold": 0,
                },
            },
        )
        self.assertNotIn("items", snapshot)

    def test_serialized_player_state_is_detached_and_json_serializable(self):
        player = PlayerState(
            player_id=0,
            health=10,
            max_health=10,
            buffs=BuffSlot(Heat=1),
            debuffs=DebuffSlot(Poison=2),
        )
        snapshot = serialize_player_state(player)

        player.buffs.Heat = 9
        player.debuffs.Poison = 8
        player.health = 11

        self.assertEqual(snapshot["health"], 10)
        self.assertEqual(snapshot["buffs"]["Heat"], 1)
        self.assertEqual(snapshot["debuffs"]["Poison"], 2)
        json.dumps(snapshot)

    def test_step_does_not_record_history_when_collection_is_disabled(self):
        battle = BattleState(
            players=[
                PlayerState(player_id=0, health=10),
                PlayerState(player_id=1, health=10),
            ],
        )

        battle.step()

        self.assertEqual(battle.player_state_history, [])

    def test_step_records_state_after_frame_and_system_resolution(self):
        first = PlayerState(
            player_id=0,
            health=5,
            max_health=10,
            stamina=0.0,
            max_stamina=2.0,
            buffs=BuffSlot(Regeneration=2),
        )
        second = PlayerState(
            player_id=1,
            health=10,
            max_health=10,
            stamina=2.0,
            max_stamina=2.0,
        )
        battle = BattleState(
            players=[first, second],
            frame_delta=1.0,
            collect_player_state_history=True,
        )

        battle.step()

        self.assertEqual(len(battle.player_state_history), 1)
        snapshot = battle.player_state_history[0]
        self.assertEqual(snapshot["sequence"], 0)
        self.assertEqual(snapshot["frame"], 1)
        self.assertEqual(snapshot["time"], 1.0)
        self.assertEqual(snapshot["players"][0]["health"], 7)
        self.assertEqual(snapshot["players"][0]["stamina"], 1.0)

    def test_multiple_steps_record_one_independent_snapshot_each(self):
        first = PlayerState(player_id=0, health=10, max_health=10)
        second = PlayerState(player_id=1, health=10, max_health=10)
        battle = BattleState(
            players=[first, second],
            collect_player_state_history=True,
        )

        battle.step()
        first.buffs.Heat = 1
        battle.step()
        first.buffs.Heat = 2
        battle.step()

        self.assertEqual(len(battle.player_state_history), 3)
        self.assertEqual(
            [record["sequence"] for record in battle.player_state_history],
            [0, 1, 2],
        )
        self.assertEqual(
            [
                record["players"][0]["buffs"]["Heat"]
                for record in battle.player_state_history
            ],
            [0, 1, 2],
        )

    def test_item_lethal_step_records_terminal_state_without_advancing_time(
        self,
    ):
        item = LethalItem()
        first = PlayerState(
            player_id=0,
            health=10,
            max_health=10,
            items={item.item_key: item},
        )
        second = PlayerState(player_id=1, health=10, max_health=10)
        battle = BattleState(
            players=[first, second],
            active_items=[item],
            collect_player_state_history=True,
        )

        battle.step()

        self.assertEqual(battle.winner, 0)
        self.assertEqual(len(battle.player_state_history), 1)
        snapshot = battle.player_state_history[0]
        self.assertEqual(snapshot["frame"], 0)
        self.assertEqual(snapshot["time"], 0.0)
        self.assertEqual(snapshot["players"][1]["health"], 0)

    def test_system_lethal_step_records_terminal_state_after_time_advances(
        self,
    ):
        first = PlayerState(player_id=0, health=10, max_health=10)
        second = PlayerState(
            player_id=1,
            health=1,
            max_health=1,
            debuffs=DebuffSlot(Poison=1),
        )
        battle = BattleState(
            frame=1,
            time=1.0,
            players=[first, second],
            frame_delta=1.0,
            collect_player_state_history=True,
        )

        battle.step()

        self.assertEqual(battle.winner, 0)
        snapshot = battle.player_state_history[0]
        self.assertEqual(snapshot["frame"], 2)
        self.assertEqual(snapshot["time"], 2.0)
        self.assertEqual(snapshot["players"][1]["health"], 0)

    def test_unexpected_step_exception_does_not_record_partial_snapshot(self):
        item = ErrorItem()
        first = PlayerState(
            player_id=0,
            health=10,
            items={item.item_key: item},
        )
        second = PlayerState(player_id=1, health=10)
        battle = BattleState(
            players=[first, second],
            active_items=[item],
            collect_player_state_history=True,
        )

        with self.assertRaisesRegex(RuntimeError, "unexpected item failure"):
            battle.step()

        self.assertEqual(battle.player_state_history, [])

    def test_compress_player_state_history_handles_empty_and_single_record(
        self,
    ):
        self.assertEqual(compress_player_state_history([], 0.1), [])

        players = [history_player(stamina=3.2)]
        compressed = compress_player_state_history(
            [history_record(4, 5, 0.5, players)],
            0.1,
        )
        expected_players = deepcopy(players)
        expected_players[0]["stamina"] = (3.2, 3.2)

        self.assertEqual(
            compressed,
            [
                {
                    "sequence": (4, 4),
                    "frame": (5, 5),
                    "time": (0.5, 0.5),
                    "players": expected_players,
                }
            ],
        )

    def test_compression_merges_exact_frame_delta_stamina_recovery(
        self,
    ):
        history = [
            history_record(
                0,
                1,
                0.1,
                [
                    history_player(0, stamina=1.0),
                    history_player(1, stamina=5.0),
                ],
            ),
            history_record(
                1,
                2,
                0.2,
                [
                    history_player(0, stamina=1.1),
                    history_player(1, stamina=5.0),
                ],
            ),
            history_record(
                2,
                3,
                0.3,
                [
                    history_player(0, stamina=1.2),
                    history_player(1, stamina=5.0),
                ],
            ),
        ]

        compressed = compress_player_state_history(history, 0.1)

        self.assertEqual(len(compressed), 1)
        self.assertEqual(compressed[0]["sequence"], (0, 2))
        self.assertEqual(compressed[0]["frame"], (1, 3))
        self.assertEqual(compressed[0]["time"], (0.1, 0.3))
        self.assertEqual(
            compressed[0]["players"][0]["stamina"],
            (1.0, 1.2),
        )
        self.assertEqual(
            compressed[0]["players"][1]["stamina"],
            (5.0, 5.0),
        )

    def test_compression_accepts_stamina_floating_point_error(self):
        history = [
            history_record(
                0,
                1,
                0.1,
                [history_player(stamina=1.0)],
            ),
            history_record(
                1,
                2,
                0.2,
                [history_player(stamina=1.1000000000000001)],
            ),
        ]

        compressed = compress_player_state_history(history, 0.1)

        self.assertEqual(len(compressed), 1)
        self.assertEqual(
            compressed[0]["players"][0]["stamina"],
            (1.0, 1.1000000000000001),
        )

    def test_compression_accepts_final_partial_recovery_at_max_stamina(
        self,
    ):
        history = [
            history_record(
                0,
                1,
                0.1,
                [history_player(stamina=4.95)],
            ),
            history_record(
                1,
                2,
                0.2,
                [history_player(stamina=5.0)],
            ),
        ]

        compressed = compress_player_state_history(history, 0.1)

        self.assertEqual(len(compressed), 1)
        self.assertEqual(
            compressed[0]["players"][0]["stamina"],
            (4.95, 5.0),
        )

    def test_compression_rejects_stamina_spending_and_non_natural_gain(
        self,
    ):
        cases = (
            ("spending", 3.0, 2.1, 5.0),
            ("large gain", 3.0, 3.2, 5.0),
            ("partial gain below max", 3.0, 3.05, 5.0),
        )

        for label, previous_stamina, current_stamina, max_stamina in cases:
            with self.subTest(label=label):
                history = [
                    history_record(
                        0,
                        1,
                        0.1,
                        [
                            history_player(
                                stamina=previous_stamina,
                                max_stamina=max_stamina,
                            )
                        ],
                    ),
                    history_record(
                        1,
                        2,
                        0.2,
                        [
                            history_player(
                                stamina=current_stamina,
                                max_stamina=max_stamina,
                            )
                        ],
                    ),
                ]

                compressed = compress_player_state_history(history, 0.1)

                self.assertEqual(len(compressed), 2)

    def test_compression_rejects_non_stamina_state_change(self):
        changes = (
            {"health": 9},
            {"block": 1},
            {"fatigue_damage": 1},
            {"max_stamina": 6.0},
            {"buffs": {"Heat": 1}},
            {"debuffs": {"Poison": 1}},
        )

        for change in changes:
            with self.subTest(change=change):
                previous = history_player(stamina=1.0)
                current = history_player(stamina=1.1, **change)
                history = [
                    history_record(0, 1, 0.1, [previous]),
                    history_record(1, 2, 0.2, [current]),
                ]

                compressed = compress_player_state_history(history, 0.1)

                self.assertEqual(len(compressed), 2)

    def test_compress_player_state_history_does_not_merge_equal_states_across_change(
        self,
    ):
        state_a = [history_player(health=10, stamina=1.0)]
        state_b = [history_player(health=9, stamina=1.1)]
        history = [
            history_record(0, 1, 0.1, state_a),
            history_record(1, 2, 0.2, state_b),
            history_record(2, 3, 0.3, state_a),
        ]

        compressed = compress_player_state_history(history, 0.1)

        self.assertEqual(len(compressed), 3)
        self.assertEqual(
            [record["sequence"] for record in compressed],
            [(0, 0), (1, 1), (2, 2)],
        )

    def test_compress_player_state_history_does_not_mutate_or_alias_input(
        self,
    ):
        players = [history_player(stamina=1.0)]
        history = [
            history_record(0, 1, 0.1, players),
            history_record(
                1,
                2,
                0.2,
                [history_player(stamina=1.1)],
            ),
        ]
        original = deepcopy(history)

        compressed = compress_player_state_history(history, 0.1)
        compressed[0]["players"][0]["health"] = 1
        compressed[0]["players"][0]["stamina"] = (0.0, 0.0)

        self.assertEqual(history, original)

    def test_run_config_validates_applies_and_compresses_player_state_history(
        self,
    ):
        with self.assertRaisesRegex(
            ValueError,
            "settings.collect_player_state_history must be a bool",
        ):
            run_battle_from_config(
                minimal_config(
                    {
                        "max_frames": 1,
                        "collect_player_state_history": "yes",
                    }
                ),
                item_factories={},
                item_catalog={},
            )

        disabled_result = run_battle_from_config(
            minimal_config({"max_frames": 2, "frame_delta": 1.0}),
            item_factories={},
            item_catalog={},
        )
        self.assertEqual(disabled_result["player_state_history"], [])

        enabled_result = run_battle_from_config(
            minimal_config(
                {
                    "max_frames": 3,
                    "frame_delta": 1.0,
                    "collect_player_state_history": True,
                }
            ),
            item_factories={},
            item_catalog={},
        )
        self.assertEqual(len(enabled_result["player_state_history"]), 1)
        compressed = enabled_result["player_state_history"][0]
        self.assertEqual(compressed["sequence"], (0, 2))
        self.assertEqual(compressed["frame"], (1, 3))
        self.assertEqual(compressed["time"], (1.0, 3.0))
        self.assertEqual(
            compressed["players"][0]["stamina"],
            (5.0, 5.0),
        )

    def test_success_result_player_state_history_is_json_serializable(self):
        result = run_battle_from_config(
            minimal_config(
                {
                    "max_frames": 2,
                    "frame_delta": 1.0,
                    "collect_player_state_history": True,
                }
            ),
            item_factories={},
            item_catalog={},
        )

        json.dumps(result)
        final_snapshot = result["player_state_history"][-1]["players"][0]
        final_player = result["players"][0]
        for key in (
            "player_id",
            "health",
            "max_health",
            "block",
            "fatigue_damage",
            "max_stamina",
            "buffs",
            "debuffs",
        ):
            self.assertEqual(final_snapshot[key], final_player[key])
        self.assertEqual(
            final_snapshot["stamina"][-1],
            final_player["stamina"],
        )
        self.assertNotIn("items", final_snapshot)


if __name__ == "__main__":
    unittest.main()
