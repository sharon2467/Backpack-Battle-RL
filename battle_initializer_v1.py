from basic_backpack_v1 import (
    ITEM_CATALOG,
    build_occupancy_matrix,
    find_diamond_links,
    find_star_links,
    find_triangle_links,
)
from battle_module_v1 import BattleItem, BattleState, PlayerState


def initialize_battle(player_specs, item_factories, item_catalog=ITEM_CATALOG):
    if len(player_specs) != 2:
        raise ValueError("battle initializer requires exactly two players")

    player_ids = [_required_field(player_spec, "player_id") for player_spec in player_specs]
    if len(set(player_ids)) != len(player_ids):
        raise ValueError("player_id values must be unique")

    player_states = []
    active_items = []

    for player_spec in player_specs:
        player_id = player_spec["player_id"]
        health = _required_field(player_spec, "health")
        placements = _required_field(player_spec, "placements")

        occupancy_matrix, placed_items = build_occupancy_matrix(placements, item_catalog)
        marker_links = (
            find_star_links(placed_items, occupancy_matrix)
            + find_diamond_links(placed_items, occupancy_matrix)
            + find_triangle_links(placed_items, occupancy_matrix)
        )

        items_by_key = _create_battle_items(
            placed_items,
            player_id,
            item_factories,
        )
        _attach_marker_links(marker_links, items_by_key)

        player_state = PlayerState(
            player_id=player_id,
            health=health,
            items=items_by_key,
        )
        player_states.append(player_state)

        for battle_item in items_by_key.values():
            if battle_item.is_active_item:
                active_items.append(battle_item)

    return BattleState(players=player_states, active_items=active_items)


def _required_field(source, key):
    if key not in source:
        raise ValueError(f"missing required field: {key}")
    return source[key]


def _create_battle_items(placed_items, player_id, item_factories):
    items_by_key = {}

    for placed_item in placed_items:
        item_id = placed_item["item_id"]
        item_key = placed_item["item_key"]
        if item_id not in item_factories:
            raise ValueError(f"missing item factory for item_id: {item_id}")

        if item_key in items_by_key:
            raise ValueError(f"duplicate item_key generated: {item_key}")

        battle_item = item_factories[item_id](
            item_id=item_id,
            item_key=item_key,
            player_id=player_id,
        )
        _validate_battle_item(battle_item, item_id, item_key, player_id)

        items_by_key[item_key] = battle_item

    return items_by_key


def _validate_battle_item(battle_item, item_id, item_key, player_id):
    if not isinstance(battle_item, BattleItem):
        raise ValueError("item factory must return a BattleItem")
    if battle_item.item_id != item_id:
        raise ValueError(f"battle item item_id mismatch: {battle_item.item_id} != {item_id}")
    if battle_item.item_key != item_key:
        raise ValueError(f"battle item item_key mismatch: {battle_item.item_key} != {item_key}")
    if battle_item.player_id != player_id:
        raise ValueError(f"battle item player_id mismatch: {battle_item.player_id} != {player_id}")


def _attach_marker_links(marker_links, items_by_key):
    for marker_link in marker_links:
        source_key = marker_link["source_item_key"]
        target_key = marker_link["target_item_key"]

        if source_key not in items_by_key:
            raise ValueError(f"unknown source_item_key: {source_key}")
        if target_key not in items_by_key:
            raise ValueError(f"unknown target_item_key: {target_key}")

        items_by_key[source_key].add_linked_item(target_key)
