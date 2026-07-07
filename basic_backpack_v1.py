WIDTH = 9
HEIGHT = 7
VALID_ROTATIONS = {0, 90, 180, 270}

ITEM_CATALOG = {
    "stone": {
        "item_id": "stone",
        "shape_cells": [(0, 0)],
        "star_cells": [],
    },
    "banana": {
        "item_id": "banana",
        "shape_cells": [(0, 1), (0, 0), (1, 0)],
        "star_cells": [(0, 2), (-1, 1), (1, 1), (-1, 0), (2, 0), (0, -1), (1, -1)],
    },
    "blood_harvester": {
        "item_id": "blood_harvester",
        "shape_cells": [(0, 1), (1, 1), (2, 1), (0, 0), (0, -1), (0, -2)],
        "star_cells": [(1, 0), (2, 0), (1, -1), (2, -1), (1, -2), (2, -2)],
    },
    "bag_of_stones": {
        "item_id": "bag_of_stones",
        "shape_cells": [(0, 0), (1, 0)],
        "star_cells_by_rotation": {
            0: [(0, 1), (1, 1)],
            90: [(0, 2)],
            180: [(0, 1), (-1, 1)],
            270: [(0, 1)],
        },
    },
    "health_potion": {
        "item_id": "health_potion",
        "shape_cells": [(0, 0), (0, 1)],
        "star_cells_by_rotation": {
            0: [(0, 2)],
            90: [(-1, 1)],
            180: [(0, 1)],
            270: [(1, 1)],
        },
    },
}


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

    if "star_cells_by_rotation" in item_spec:
        star_cells_by_rotation = item_spec["star_cells_by_rotation"]
        if set(star_cells_by_rotation) != VALID_ROTATIONS:
            raise ValueError(f"incomplete star_cells_by_rotation for item: {item_spec['item_id']}")
        star_cells = list(star_cells_by_rotation[rotation])
    else:
        star_cells = rotate_cells(item_spec.get("star_cells", []), rotation)

    x_offset = placement["x"]
    y_offset = placement["y"]
    occupied_cells = [(x + x_offset, y + y_offset) for x, y in occupied_cells]
    star_cells = [(x + x_offset, y + y_offset) for x, y in star_cells]

    return {
        "instance_id": placement.get("instance_id"),
        "item_id": item_spec["item_id"],
        "x": x_offset,
        "y": y_offset,
        "rotation": rotation,
        "occupied_cells": occupied_cells,
        "star_cells": star_cells,
    }


def build_occupancy_matrix(placements, item_catalog):
    occupancy_matrix = [[None for _ in range(WIDTH)] for _ in range(HEIGHT)]
    placed_items = []

    for instance_id, placement in enumerate(placements):
        item_id = placement["item_id"]
        if item_id not in item_catalog:
            raise ValueError(f"unknown item_id: {item_id}")
        if placement["rotation"] not in VALID_ROTATIONS:
            raise ValueError(f"invalid rotation: {placement['rotation']}")

        placement_with_instance_id = dict(placement)
        placement_with_instance_id["instance_id"] = instance_id
        placed_item = place_item(item_catalog[item_id], placement_with_instance_id)

        for x, y in placed_item["occupied_cells"]:
            if not (0 <= x < WIDTH and 0 <= y < HEIGHT):
                raise ValueError(f"occupied cell out of bounds: {(x, y)}")
            row_index = HEIGHT - 1 - y
            if occupancy_matrix[row_index][x] is not None:
                raise ValueError(f"occupied cell overlaps: {(x, y)}")
            occupancy_matrix[row_index][x] = instance_id

        placed_items.append(placed_item)

    return occupancy_matrix, placed_items


def find_star_links(placed_items, occupancy_matrix):
    star_links = []

    for placed_item in placed_items:
        source_instance_id = placed_item["instance_id"]
        for x, y in placed_item["star_cells"]:
            if not (0 <= x < WIDTH and 0 <= y < HEIGHT):
                continue

            target_instance_id = occupancy_matrix[HEIGHT - 1 - y][x]
            if target_instance_id is None:
                continue
            if target_instance_id == source_instance_id:
                continue

            star_links.append(
                {
                    "source_instance_id": source_instance_id,
                    "target_instance_id": target_instance_id,
                    "star_cell": (x, y),
                }
            )

    return star_links
