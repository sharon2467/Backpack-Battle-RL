import json
from pathlib import Path


WIDTH = 9
HEIGHT = 7
VALID_ROTATIONS = {0, 90, 180, 270}
MARKER_TYPES = ("star", "diamond", "triangle")


def _load_item_catalog():
    catalog_path = Path(__file__).with_name("data") / "item_catalog_v1.json"
    item_catalog = json.loads(catalog_path.read_text(encoding="utf-8"))

    for item_spec in item_catalog.values():
        for marker_type in MARKER_TYPES:
            key = f"{marker_type}_cells_by_rotation"
            if key in item_spec:
                item_spec[key] = {
                    int(rotation): cells
                    for rotation, cells in item_spec[key].items()
                }

    return item_catalog


ITEM_CATALOG = _load_item_catalog()


def rotate_cells(cells, rotation):
    if rotation not in VALID_ROTATIONS:
        raise ValueError(f"invalid rotation: {rotation}")

    rotated = []
    for x, y in cells:
        if rotation == 0:
            rotated.append((x, y))
        elif rotation == 90:
            rotated.append((-y, x))
        elif rotation == 180:
            rotated.append((-x, -y))
        elif rotation == 270:
            rotated.append((y, -x))
    return rotated


def place_item(item_spec, placement):
    rotation = placement["rotation"]
    if rotation not in VALID_ROTATIONS:
        raise ValueError(f"invalid rotation: {rotation}")

    occupied_cells = rotate_cells(item_spec["shape_cells"], rotation)

    marker_cells = {}
    for marker_type in MARKER_TYPES:
        by_rotation_key = f"{marker_type}_cells_by_rotation"
        cells_key = f"{marker_type}_cells"
        if by_rotation_key in item_spec:
            cells_by_rotation = item_spec[by_rotation_key]
            if set(cells_by_rotation) != VALID_ROTATIONS:
                raise ValueError(f"incomplete {by_rotation_key} for item: {item_spec['item_id']}")
            marker_cells[cells_key] = list(cells_by_rotation[rotation])
        else:
            marker_cells[cells_key] = rotate_cells(item_spec.get(cells_key, []), rotation)

    x_offset = placement["x"]
    y_offset = placement["y"]
    occupied_cells = [(x + x_offset, y + y_offset) for x, y in occupied_cells]
    for cells_key, cells in marker_cells.items():
        marker_cells[cells_key] = [(x + x_offset, y + y_offset) for x, y in cells]

    placed_item = {
        "item_key": placement.get("item_key"),
        "item_id": item_spec["item_id"],
        "x": x_offset,
        "y": y_offset,
        "rotation": rotation,
        "occupied_cells": occupied_cells,
    }
    placed_item.update(marker_cells)
    return placed_item


def build_occupancy_matrix(placements, item_catalog):
    occupancy_matrix = [[None for _ in range(WIDTH)] for _ in range(HEIGHT)]
    placed_items = []
    item_counts = {}

    for placement in placements:
        item_id = placement["item_id"]
        if item_id not in item_catalog:
            raise ValueError(f"unknown item_id: {item_id}")
        if placement["rotation"] not in VALID_ROTATIONS:
            raise ValueError(f"invalid rotation: {placement['rotation']}")

        item_counts[item_id] = item_counts.get(item_id, 0) + 1
        item_key = f"{item_id}{item_counts[item_id]}"

        placement_with_item_key = dict(placement)
        placement_with_item_key["item_key"] = item_key
        placed_item = place_item(item_catalog[item_id], placement_with_item_key)

        for x, y in placed_item["occupied_cells"]:
            if not (0 <= x < WIDTH and 0 <= y < HEIGHT):
                raise ValueError(f"occupied cell out of bounds: {(x, y)}")
            row_index = HEIGHT - 1 - y
            if occupancy_matrix[row_index][x] is not None:
                raise ValueError(f"occupied cell overlaps: {(x, y)}")
            occupancy_matrix[row_index][x] = item_key

        placed_items.append(placed_item)

    return occupancy_matrix, placed_items


def find_marker_links(placed_items, occupancy_matrix, marker_type):
    cells_key = f"{marker_type}_cells"
    cell_key = f"{marker_type}_cell"
    marker_links = []

    for placed_item in placed_items:
        source_item_key = placed_item["item_key"]
        for x, y in placed_item.get(cells_key, []):
            if not (0 <= x < WIDTH and 0 <= y < HEIGHT):
                continue

            target_item_key = occupancy_matrix[HEIGHT - 1 - y][x]
            if target_item_key is None:
                continue
            if target_item_key == source_item_key:
                continue

            marker_links.append(
                {
                    "source_item_key": source_item_key,
                    "target_item_key": target_item_key,
                    cell_key: (x, y),
                }
            )

    return marker_links


def find_star_links(placed_items, occupancy_matrix):
    return find_marker_links(placed_items, occupancy_matrix, "star")


def find_diamond_links(placed_items, occupancy_matrix):
    return find_marker_links(placed_items, occupancy_matrix, "diamond")


def find_triangle_links(placed_items, occupancy_matrix):
    return find_marker_links(placed_items, occupancy_matrix, "triangle")
