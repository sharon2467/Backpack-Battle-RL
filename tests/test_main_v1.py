import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from battle_module_v1 import BattleItem, Effect, Trigger
from main_v1 import (
    DEFAULT_FRAME_DELTA,
    load_battle_run_file,
    main,
    normalize_player_specs,
    run_battle_from_config,
    run_battle_from_file,
)


class AlwaysTrigger(Trigger):
    def update(self, context):
        return True


class DamageEffect(Effect):
    def __init__(self, damage):
        self.damage = damage

    def apply(self, context):
        blocked_damage = min(context.opponent.block, self.damage)
        health_damage = self.damage - blocked_damage
        context.battle_state.commit_health_reduction(
            context.opponent,
            blocked_damage,
            health_damage,
        )
        return True


class DamageItem(BattleItem):
    def __init__(self, damage=100, **kwargs):
        super().__init__(
            triggers=[AlwaysTrigger()],
            effects=[DamageEffect(damage)],
            is_active_item=True,
            **kwargs,
        )

    def run_effect(self, trigger_results, context):
        if not trigger_results[0]:
            return
        self.effects[0].apply(context)


class StatusSetupEffect(Effect):
    def apply(self, context):
        context.owner.buffs.Regeneration = 2
        context.opponent.debuffs.Poison = 1
        return True


class StatusSetupItem(BattleItem):
    def __init__(self, **kwargs):
        super().__init__(
            triggers=[AlwaysTrigger()],
            effects=[StatusSetupEffect()],
            is_active_item=True,
            **kwargs,
        )

    def run_effect(self, trigger_results, context):
        if trigger_results[0]:
            self.effects[0].apply(context)


def make_damage_factory(damage=100):
    def factory(item_id, item_key, player_id):
        return DamageItem(
            item_id=item_id,
            item_key=item_key,
            player_id=player_id,
            damage=damage,
        )

    return factory


def make_status_setup_factory(item_id, item_key, player_id):
    return StatusSetupItem(
        item_id=item_id,
        item_key=item_key,
        player_id=player_id,
    )


def minimal_config(players=None, settings=None):
    if players is None:
        players = [
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
        ]
    if settings is None:
        settings = {"max_frames": 1, "frame_delta": 1.0}

    return {
        "schema_version": "battle_run_v1",
        "settings": settings,
        "players": players,
    }


class MainV1Test(unittest.TestCase):
    def test_main_default_frame_delta_is_one_thirtieth(self):
        result = run_battle_from_config(
            minimal_config(settings={"max_frames": 1}),
            item_factories={},
            item_catalog={},
        )

        self.assertEqual(DEFAULT_FRAME_DELTA, 1.0 / 30.0)
        self.assertEqual(result["time"], 1.0 / 30.0)

    def test_normalize_player_specs_keeps_class_id_as_metadata(self):
        player_specs, metadata = normalize_player_specs(minimal_config())

        self.assertEqual(
            player_specs,
            [
                {
                    "player_id": 0,
                    "health": 25,
                    "max_health": 25,
                    "stamina": 5.0,
                    "max_stamina": 5.0,
                    "placements": [],
                },
                {
                    "player_id": 1,
                    "health": 25,
                    "max_health": 25,
                    "stamina": 5.0,
                    "max_stamina": 5.0,
                    "placements": [],
                },
            ],
        )
        self.assertEqual(metadata["players"][0]["class_id"], "ranger")
        self.assertEqual(metadata["players"][1]["class_id"], "reaper")

    def test_run_battle_from_config_returns_max_frames_result(self):
        result = run_battle_from_config(
            minimal_config(settings={"max_frames": 2, "frame_delta": 0.5}),
            item_factories={},
            item_catalog={},
        )

        self.assertEqual(result["winner"], None)
        self.assertEqual(result["finish_reason"], "max_frames_reached")
        self.assertEqual(result["frame"], 2)
        self.assertEqual(result["time"], 1.0)
        self.assertEqual(result["players"][0]["class_id"], "ranger")
        self.assertEqual(result["players"][1]["class_id"], "reaper")
        self.assertEqual(result["players"][0]["health"], 25)
        self.assertEqual(result["players"][0]["max_health"], 25)
        self.assertEqual(result["players"][0]["stamina"], 5.0)
        self.assertEqual(result["players"][0]["max_stamina"], 5.0)
        self.assertEqual(
            result["players"][0]["buffs"],
            {
                "Empower": 0,
                "Heat": 0,
                "Luck": 0,
                "Mana": 0,
                "Regeneration": 0,
                "Spikes": 0,
                "Vampirism": 0,
            },
        )
        self.assertEqual(
            result["players"][0]["debuffs"],
            {"Poison": 0, "Blind": 0, "Cold": 0},
        )
        self.assertEqual(result["log"], [])

    def test_run_battle_from_config_returns_winner_result(self):
        item_catalog = {
            "stone": {"item_id": "stone", "shape_cells": [(0, 0)]},
        }
        config = minimal_config(
            players=[
                {
                    "player_id": 0,
                    "class_id": "ranger",
                    "health": 25,
                    "max_health": 25,
                    "stamina": 5.0,
                    "max_stamina": 5.0,
                    "placements": [
                        {"item_id": "stone", "x": 0, "y": 0, "rotation": 0},
                    ],
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
            settings={"max_frames": 5, "frame_delta": 1.0},
        )

        result = run_battle_from_config(
            config,
            item_factories={"stone": make_damage_factory()},
            item_catalog=item_catalog,
        )

        self.assertEqual(result["winner"], 0)
        self.assertEqual(result["finish_reason"], "winner")
        self.assertEqual(result["frame"], 0)
        self.assertEqual(result["time"], 0.0)
        self.assertEqual(result["players"][1]["health"], 0)
        self.assertEqual(
            result["active_items"],
            [{"player_id": 0, "item_key": "stone1", "item_id": "stone"}],
        )

    def test_run_battle_serializes_fatigue_damage(self):
        result = run_battle_from_config(
            minimal_config(
                settings={"max_frames": 17, "frame_delta": 1.0},
            ),
            item_factories={},
            item_catalog={},
        )

        self.assertEqual(result["players"][0]["fatigue_damage"], 1)
        self.assertEqual(result["players"][1]["fatigue_damage"], 1)

    def test_run_battle_serializes_regeneration_and_lethal_poison(self):
        config = minimal_config(
            players=[
                {
                    "player_id": 0,
                    "class_id": "ranger",
                    "health": 5,
                    "max_health": 10,
                    "stamina": 5.0,
                    "max_stamina": 5.0,
                    "placements": [
                        {
                            "item_id": "status_setup",
                            "x": 0,
                            "y": 0,
                            "rotation": 0,
                        },
                    ],
                },
                {
                    "player_id": 1,
                    "class_id": "reaper",
                    "health": 1,
                    "max_health": 1,
                    "stamina": 5.0,
                    "max_stamina": 5.0,
                    "placements": [],
                },
            ],
            settings={"max_frames": 2, "frame_delta": 1.0},
        )
        item_catalog = {
            "status_setup": {
                "item_id": "status_setup",
                "shape_cells": [(0, 0)],
            },
        }

        result = run_battle_from_config(
            config,
            item_factories={
                "status_setup": make_status_setup_factory,
            },
            item_catalog=item_catalog,
        )

        self.assertEqual(result["winner"], 0)
        self.assertEqual(result["finish_reason"], "winner")
        self.assertEqual(result["frame"], 2)
        self.assertEqual(result["time"], 2.0)
        self.assertEqual(result["players"][0]["health"], 7)
        self.assertEqual(result["players"][0]["buffs"]["Regeneration"], 2)
        self.assertEqual(result["players"][1]["health"], 0)
        self.assertEqual(result["players"][1]["debuffs"]["Poison"], 1)

    def test_lethal_fatigue_returns_player_win_without_draw(self):
        config = minimal_config(
            settings={"max_frames": 17, "frame_delta": 1.0},
        )
        config["players"][0]["health"] = 1
        config["players"][1]["health"] = 1

        result = run_battle_from_config(
            config,
            item_factories={},
            item_catalog={},
        )

        self.assertEqual(result["winner"], 0)
        self.assertEqual(result["finish_reason"], "winner")
        self.assertEqual(result["frame"], 17)
        self.assertEqual(result["time"], 17.0)
        self.assertEqual(result["players"][0]["health"], 1)
        self.assertEqual(result["players"][0]["fatigue_damage"], 0)
        self.assertEqual(result["players"][1]["health"], 0)
        self.assertEqual(result["players"][1]["fatigue_damage"], 1)

    def test_load_battle_run_file_reads_and_validates_json(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            input_path = Path(temp_dir) / "battle_run.json"
            input_path.write_text(json.dumps(minimal_config()), encoding="utf-8")

            result = load_battle_run_file(input_path)

        self.assertEqual(result["schema_version"], "battle_run_v1")

    def test_run_battle_from_file_loads_json_then_runs(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            input_path = Path(temp_dir) / "battle_run.json"
            input_path.write_text(json.dumps(minimal_config()), encoding="utf-8")

            result = run_battle_from_file(input_path, item_factories={}, item_catalog={})

        self.assertEqual(result["finish_reason"], "max_frames_reached")

    def test_unknown_schema_version_fails(self):
        config = minimal_config()
        config["schema_version"] = "other"

        with self.assertRaises(ValueError):
            run_battle_from_config(config, item_factories={}, item_catalog={})

    def test_requires_exactly_two_players(self):
        config = minimal_config(players=[])

        with self.assertRaises(ValueError):
            run_battle_from_config(config, item_factories={}, item_catalog={})

    def test_missing_required_player_field_fails(self):
        for field_name in ("health", "max_health"):
            with self.subTest(field_name=field_name):
                config = minimal_config()
                del config["players"][0][field_name]

                with self.assertRaises(ValueError):
                    run_battle_from_config(
                        config,
                        item_factories={},
                        item_catalog={},
                    )

    def test_health_and_max_health_must_be_positive_ints(self):
        for field_name in ("health", "max_health"):
            for invalid_value in (0, -1, 1.5, True, "25"):
                with self.subTest(
                    field_name=field_name,
                    invalid_value=invalid_value,
                ):
                    config = minimal_config()
                    config["players"][0][field_name] = invalid_value

                    with self.assertRaises(ValueError):
                        run_battle_from_config(
                            config,
                            item_factories={},
                            item_catalog={},
                        )

    def test_health_cannot_exceed_max_health(self):
        config = minimal_config()
        config["players"][0]["health"] = 26

        with self.assertRaisesRegex(
            ValueError,
            "player health cannot exceed max_health",
        ):
            run_battle_from_config(
                config,
                item_factories={},
                item_catalog={},
            )

    def test_missing_stamina_player_fields_fail(self):
        for field_name in ("stamina", "max_stamina"):
            with self.subTest(field_name=field_name):
                config = minimal_config()
                del config["players"][0][field_name]

                with self.assertRaises(ValueError):
                    run_battle_from_config(config, item_factories={}, item_catalog={})

    def test_stamina_player_fields_must_be_positive_numbers(self):
        for invalid_value in (0, True, "5"):
            with self.subTest(invalid_value=invalid_value):
                config = minimal_config()
                config["players"][0]["stamina"] = invalid_value
                config["players"][0]["max_stamina"] = invalid_value

                with self.assertRaises(ValueError):
                    run_battle_from_config(config, item_factories={}, item_catalog={})

    def test_battle_must_start_with_full_stamina(self):
        config = minimal_config()
        config["players"][0]["stamina"] = 4.0

        with self.assertRaises(ValueError):
            run_battle_from_config(config, item_factories={}, item_catalog={})

    def test_missing_item_factory_fails(self):
        item_catalog = {
            "stone": {"item_id": "stone", "shape_cells": [(0, 0)]},
        }
        config = minimal_config(
            players=[
                {
                    "player_id": 0,
                    "health": 25,
                    "max_health": 25,
                    "stamina": 5.0,
                    "max_stamina": 5.0,
                    "placements": [
                        {"item_id": "stone", "x": 0, "y": 0, "rotation": 0},
                    ],
                },
                {
                    "player_id": 1,
                    "health": 25,
                    "max_health": 25,
                    "stamina": 5.0,
                    "max_stamina": 5.0,
                    "placements": [],
                },
            ],
        )

        with self.assertRaises(ValueError):
            run_battle_from_config(config, item_factories={}, item_catalog=item_catalog)

    def test_main_prints_success_result_for_empty_battle(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            input_path = Path(temp_dir) / "battle_run.json"
            input_path.write_text(json.dumps(minimal_config()), encoding="utf-8")

            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                exit_code = main(["--input", str(input_path)])

        result = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0)
        self.assertEqual(result["finish_reason"], "max_frames_reached")

    def test_main_prints_error_result_for_missing_factory(self):
        config = minimal_config(
            players=[
                {
                    "player_id": 0,
                    "health": 25,
                    "max_health": 25,
                    "stamina": 5.0,
                    "max_stamina": 5.0,
                    "placements": [
                        {"item_id": "stone", "x": 0, "y": 0, "rotation": 0},
                    ],
                },
                {
                    "player_id": 1,
                    "health": 25,
                    "max_health": 25,
                    "stamina": 5.0,
                    "max_stamina": 5.0,
                    "placements": [],
                },
            ],
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            input_path = Path(temp_dir) / "battle_run.json"
            input_path.write_text(json.dumps(config), encoding="utf-8")

            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                exit_code = main(["--input", str(input_path)])

        result = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 1)
        self.assertEqual(result["finish_reason"], "error")
        self.assertEqual(result["error"]["type"], "ValueError")


if __name__ == "__main__":
    unittest.main()
