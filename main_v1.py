import argparse
import json
import math
import sys
from copy import deepcopy
from dataclasses import asdict
from pathlib import Path

from basic_backpack_v1 import ITEM_CATALOG
from battle_initializer_v1 import initialize_battle
from item_factory_registry_v1 import DEFAULT_ITEM_FACTORIES


BATTLE_RUN_SCHEMA_VERSION = "battle_run_v1"
BATTLE_RESULT_SCHEMA_VERSION = "battle_result_v1"
DEFAULT_MAX_FRAMES = 1000
DEFAULT_FRAME_DELTA = 1.0 / 30.0
STAMINA_COMPRESSION_ABS_TOLERANCE = 1e-9


def load_battle_run_file(input_path):
    path = Path(input_path)
    run_config = json.loads(path.read_text(encoding="utf-8"))
    _validate_run_config(run_config)
    return run_config


def normalize_player_specs(run_config):
    _validate_run_config(run_config)

    player_specs = []
    player_metadata = {}
    for player in run_config["players"]:
        player_spec = {
            "player_id": player["player_id"],
            "health": player["health"],
            "max_health": player["max_health"],
            "stamina": player["stamina"],
            "max_stamina": player["max_stamina"],
            "placements": player["placements"],
        }
        player_specs.append(player_spec)
        player_metadata[player["player_id"]] = {
            "class_id": player.get("class_id"),
        }

    return player_specs, {"players": player_metadata}


def run_battle_from_config(run_config, item_factories, item_catalog=ITEM_CATALOG):
    _validate_run_config(run_config)

    settings = run_config.get("settings", {})
    max_frames = settings.get("max_frames", DEFAULT_MAX_FRAMES)
    frame_delta = settings.get("frame_delta", DEFAULT_FRAME_DELTA)

    player_specs, run_metadata = normalize_player_specs(run_config)
    battle_state = initialize_battle(
        player_specs=player_specs,
        item_factories=item_factories,
        item_catalog=item_catalog,
    )
    battle_state.collect_player_state_history = settings.get(
        "collect_player_state_history",
        False,
    )
    battle_state.run(max_frames=max_frames, frame_delta=frame_delta)

    finish_reason = "winner" if battle_state.winner is not None else "max_frames_reached"
    return _build_success_result(battle_state, run_metadata, finish_reason)


def run_battle_from_file(input_path, item_factories, item_catalog=ITEM_CATALOG):
    run_config = load_battle_run_file(input_path)
    return run_battle_from_config(run_config, item_factories, item_catalog)


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output")
    parser.add_argument("--max-frames", type=int)
    parser.add_argument("--frame-delta", type=float)
    args = parser.parse_args(argv)

    try:
        run_config = load_battle_run_file(args.input)
        _apply_cli_overrides(run_config, args)
        result = run_battle_from_config(run_config, DEFAULT_ITEM_FACTORIES)
        exit_code = 0
    except Exception as exc:
        result = _build_error_result(exc)
        exit_code = 1

    result_text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(result_text + "\n", encoding="utf-8")
    else:
        print(result_text)

    return exit_code


def _validate_run_config(run_config):
    if not isinstance(run_config, dict):
        raise ValueError("battle run config must be a dict")

    schema_version = run_config.get("schema_version")
    if schema_version != BATTLE_RUN_SCHEMA_VERSION:
        raise ValueError(f"unsupported schema_version: {schema_version}")

    settings = run_config.get("settings", {})
    if not isinstance(settings, dict):
        raise ValueError("settings must be a dict")

    max_frames = settings.get("max_frames", DEFAULT_MAX_FRAMES)
    frame_delta = settings.get("frame_delta", DEFAULT_FRAME_DELTA)
    _validate_positive_int("settings.max_frames", max_frames)
    _validate_positive_number("settings.frame_delta", frame_delta)

    if "collect_log" in settings and not isinstance(settings["collect_log"], bool):
        raise ValueError("settings.collect_log must be a bool")
    if (
        "collect_player_state_history" in settings
        and not isinstance(settings["collect_player_state_history"], bool)
    ):
        raise ValueError(
            "settings.collect_player_state_history must be a bool"
        )

    if "players" not in run_config:
        raise ValueError("missing required field: players")
    players = run_config["players"]
    if not isinstance(players, list):
        raise ValueError("players must be a list")
    if len(players) != 2:
        raise ValueError("battle run config requires exactly two players")

    for player in players:
        if not isinstance(player, dict):
            raise ValueError("player spec must be a dict")
        for key in (
            "player_id",
            "health",
            "max_health",
            "stamina",
            "max_stamina",
            "placements",
        ):
            if key not in player:
                raise ValueError(f"missing required player field: {key}")

        _validate_positive_int("player.health", player["health"])
        _validate_positive_int("player.max_health", player["max_health"])
        if player["health"] > player["max_health"]:
            raise ValueError("player health cannot exceed max_health")
        _validate_positive_number("player.stamina", player["stamina"])
        _validate_positive_number("player.max_stamina", player["max_stamina"])
        if player["stamina"] != player["max_stamina"]:
            raise ValueError("player stamina must equal max_stamina at battle start")


def _validate_positive_int(name, value):
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{name} must be a positive int")


def _validate_positive_number(name, value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
        raise ValueError(f"{name} must be a positive number")


def _apply_cli_overrides(run_config, args):
    if args.max_frames is None and args.frame_delta is None:
        return

    settings = dict(run_config.get("settings", {}))
    if args.max_frames is not None:
        settings["max_frames"] = args.max_frames
    if args.frame_delta is not None:
        settings["frame_delta"] = args.frame_delta
    run_config["settings"] = settings


def _players_match_for_history_compression(
    previous_players: list[dict[str, object]],
    current_players: list[dict[str, object]],
    frame_delta: float,
) -> bool:
    if len(previous_players) != len(current_players):
        return False

    for previous_player, current_player in zip(
        previous_players,
        current_players,
    ):
        previous_without_stamina = {
            key: value
            for key, value in previous_player.items()
            if key != "stamina"
        }
        current_without_stamina = {
            key: value
            for key, value in current_player.items()
            if key != "stamina"
        }
        if previous_without_stamina != current_without_stamina:
            return False

        stamina_delta = (
            current_player["stamina"]
            - previous_player["stamina"]
        )
        if math.isclose(
            stamina_delta,
            0.0,
            rel_tol=0.0,
            abs_tol=STAMINA_COMPRESSION_ABS_TOLERANCE,
        ):
            continue
        if math.isclose(
            stamina_delta,
            frame_delta,
            rel_tol=0.0,
            abs_tol=STAMINA_COMPRESSION_ABS_TOLERANCE,
        ):
            continue

        reached_max_stamina = math.isclose(
            current_player["stamina"],
            current_player["max_stamina"],
            rel_tol=0.0,
            abs_tol=STAMINA_COMPRESSION_ABS_TOLERANCE,
        )
        if (
            reached_max_stamina
            and 0.0 < stamina_delta < frame_delta
        ):
            continue
        return False

    return True


def compress_player_state_history(
    player_state_history: list[dict[str, object]],
    frame_delta: float,
) -> list[dict[str, object]]:
    compressed_history = []
    previous_record = None

    for record in player_state_history:
        if (
            previous_record is not None
            and _players_match_for_history_compression(
                previous_record["players"],
                record["players"],
                frame_delta,
            )
        ):
            current = compressed_history[-1]
            current["sequence"] = (
                current["sequence"][0],
                record["sequence"],
            )
            current["frame"] = (
                current["frame"][0],
                record["frame"],
            )
            current["time"] = (
                current["time"][0],
                record["time"],
            )
            for compressed_player, record_player in zip(
                current["players"],
                record["players"],
            ):
                compressed_player["stamina"] = (
                    round(compressed_player["stamina"][0], 2),
                    round(record_player["stamina"], 2),
                )
            previous_record = record
            continue

        compressed_players = deepcopy(record["players"])
        for player in compressed_players:
            stamina = player["stamina"]
            player["stamina"] = (round(stamina, 2), round(stamina, 2))

        compressed_history.append(
            {
                "sequence": (record["sequence"], record["sequence"]),
                "frame": (record["frame"], record["frame"]),
                "time": (record["time"], record["time"]),
                "players": compressed_players,
            }
        )
        previous_record = record

    return compressed_history


def _build_success_result(battle_state, run_metadata, finish_reason):
    player_metadata = run_metadata.get("players", {})
    compressed_player_state_history = compress_player_state_history(
        battle_state.player_state_history,
        battle_state.frame_delta,
    )
    return {
        "schema_version": BATTLE_RESULT_SCHEMA_VERSION,
        "winner": battle_state.winner,
        "finish_reason": finish_reason,
        "frame": battle_state.frame,
        "time": battle_state.time,
        "players": [
            _serialize_player(player, player_metadata.get(player.player_id, {}))
            for player in battle_state.players
        ],
        "active_items": [
            {
                "player_id": item.player_id,
                "item_key": item.item_key,
                "item_id": item.item_id,
            }
            for item in battle_state.active_items
        ],
        "player_state_history": compressed_player_state_history,
        "log": list(battle_state.log),
    }


def _serialize_player(player, metadata):
    return {
        "player_id": player.player_id,
        "class_id": metadata.get("class_id"),
        "health": player.health,
        "max_health": player.max_health,
        "block": player.block,
        "fatigue_damage": player.fatigue_damage,
        "stamina": player.stamina,
        "max_stamina": player.max_stamina,
        "buffs": asdict(player.buffs),
        "debuffs": asdict(player.debuffs),
        "items": list(player.items),
    }


def _build_error_result(exc):
    return {
        "schema_version": BATTLE_RESULT_SCHEMA_VERSION,
        "winner": None,
        "finish_reason": "error",
        "error": {
            "type": type(exc).__name__,
            "message": str(exc),
        },
    }


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
