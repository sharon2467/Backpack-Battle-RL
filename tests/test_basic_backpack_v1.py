import unittest

from basic_backpack_v1 import (
    ITEM_CATALOG,
    build_occupancy_matrix,
    find_star_links,
    place_item,
    rotate_cells,
)


class BasicBackpackV1Test(unittest.TestCase):
    def test_single_one_by_one_item_writes_to_bottom_left_matrix_cell(self):
        occupancy_matrix, placed_items = build_occupancy_matrix(
            [{"item_id": "stone", "x": 0, "y": 0, "rotation": 0}],
            ITEM_CATALOG,
        )

        self.assertEqual(placed_items[0]["instance_id"], 0)
        self.assertEqual(placed_items[0]["occupied_cells"], [(0, 0)])
        self.assertEqual(occupancy_matrix[6][0], 0)

    def test_two_non_overlapping_items_write_instance_ids(self):
        occupancy_matrix, placed_items = build_occupancy_matrix(
            [
                {"item_id": "stone", "x": 0, "y": 0, "rotation": 0},
                {"item_id": "stone", "x": 2, "y": 3, "rotation": 0},
            ],
            ITEM_CATALOG,
        )

        self.assertEqual(len(placed_items), 2)
        self.assertEqual(occupancy_matrix[6][0], 0)
        self.assertEqual(occupancy_matrix[3][2], 1)

    def test_overlapping_items_fail(self):
        with self.assertRaises(ValueError):
            build_occupancy_matrix(
                [
                    {"item_id": "stone", "x": 1, "y": 1, "rotation": 0},
                    {"item_id": "stone", "x": 1, "y": 1, "rotation": 0},
                ],
                ITEM_CATALOG,
            )

    def test_out_of_bounds_item_fails(self):
        with self.assertRaises(ValueError):
            build_occupancy_matrix(
                [{"item_id": "stone", "x": 9, "y": 0, "rotation": 0}],
                ITEM_CATALOG,
            )

    def test_unknown_item_id_fails(self):
        with self.assertRaises(ValueError):
            build_occupancy_matrix(
                [{"item_id": "missing", "x": 0, "y": 0, "rotation": 0}],
                ITEM_CATALOG,
            )

    def test_invalid_rotation_fails(self):
        with self.assertRaises(ValueError):
            build_occupancy_matrix(
                [{"item_id": "stone", "x": 0, "y": 0, "rotation": 45}],
                ITEM_CATALOG,
            )

    def test_rotate_cells_uses_y_up_counterclockwise_rotation(self):
        self.assertEqual(rotate_cells([(1, 0), (0, 1)], 90), [(0, 1), (-1, 0)])
        self.assertEqual(rotate_cells([(1, 0), (0, 1)], 270), [(0, -1), (1, 0)])

    def test_l_shape_rotation_is_correct(self):
        item_catalog = {
            "l_shape": {
                "item_id": "l_shape",
                "shape_cells": [(0, 0), (1, 0), (0, 1)],
                "star_cells": [],
            }
        }

        occupancy_matrix, placed_items = build_occupancy_matrix(
            [{"item_id": "l_shape", "x": 2, "y": 2, "rotation": 90}],
            item_catalog,
        )

        self.assertCountEqual(placed_items[0]["occupied_cells"], [(2, 2), (2, 3), (1, 2)])
        self.assertEqual(occupancy_matrix[4][2], 0)
        self.assertEqual(occupancy_matrix[3][2], 0)
        self.assertEqual(occupancy_matrix[4][1], 0)

    def test_reference_point_does_not_need_to_be_in_shape_cells(self):
        item_catalog = {
            "offset_item": {
                "item_id": "offset_item",
                "shape_cells": [(1, 0)],
                "star_cells": [],
            }
        }

        occupancy_matrix, placed_items = build_occupancy_matrix(
            [{"item_id": "offset_item", "x": 0, "y": 0, "rotation": 0}],
            item_catalog,
        )

        self.assertEqual(placed_items[0]["occupied_cells"], [(1, 0)])
        self.assertEqual(occupancy_matrix[6][1], 0)

    def test_ordinary_star_cells_rotate_with_item(self):
        item_catalog = {
            "star_source": {
                "item_id": "star_source",
                "shape_cells": [(0, 0)],
                "star_cells": [(1, 0)],
            }
        }

        placed_item = place_item(
            item_catalog["star_source"],
            {"instance_id": 0, "item_id": "star_source", "x": 3, "y": 3, "rotation": 90},
        )

        self.assertEqual(placed_item["star_cells"], [(3, 4)])

    def test_special_star_cells_by_rotation_are_read_directly(self):
        placed_item = place_item(
            ITEM_CATALOG["bag_of_stones"],
            {"instance_id": 0, "item_id": "bag_of_stones", "x": 3, "y": 3, "rotation": 90},
        )

        self.assertEqual(placed_item["occupied_cells"], [(3, 3), (3, 4)])
        self.assertEqual(placed_item["star_cells"], [(3, 5)])

    def test_incomplete_star_cells_by_rotation_fails(self):
        item_catalog = {
            "special": {
                "item_id": "special",
                "shape_cells": [(0, 0)],
                "star_cells_by_rotation": {0: [(0, 1)]},
            }
        }

        with self.assertRaises(ValueError):
            build_occupancy_matrix(
                [{"item_id": "special", "x": 0, "y": 0, "rotation": 0}],
                item_catalog,
            )

    def test_star_link_is_created_when_star_points_to_other_item(self):
        item_catalog = {
            "source": {
                "item_id": "source",
                "shape_cells": [(0, 0)],
                "star_cells": [(1, 0)],
            },
            "target": {
                "item_id": "target",
                "shape_cells": [(0, 0)],
                "star_cells": [],
            },
        }
        occupancy_matrix, placed_items = build_occupancy_matrix(
            [
                {"item_id": "source", "x": 0, "y": 0, "rotation": 0},
                {"item_id": "target", "x": 1, "y": 0, "rotation": 0},
            ],
            item_catalog,
        )

        self.assertEqual(
            find_star_links(placed_items, occupancy_matrix),
            [{"source_instance_id": 0, "target_instance_id": 1, "star_cell": (1, 0)}],
        )

    def test_empty_star_cell_creates_no_link(self):
        item_catalog = {
            "source": {
                "item_id": "source",
                "shape_cells": [(0, 0)],
                "star_cells": [(1, 0)],
            }
        }
        occupancy_matrix, placed_items = build_occupancy_matrix(
            [{"item_id": "source", "x": 0, "y": 0, "rotation": 0}],
            item_catalog,
        )

        self.assertEqual(find_star_links(placed_items, occupancy_matrix), [])

    def test_out_of_bounds_star_cell_creates_no_link(self):
        item_catalog = {
            "source": {
                "item_id": "source",
                "shape_cells": [(0, 0)],
                "star_cells": [(-1, 0)],
            }
        }
        occupancy_matrix, placed_items = build_occupancy_matrix(
            [{"item_id": "source", "x": 0, "y": 0, "rotation": 0}],
            item_catalog,
        )

        self.assertEqual(find_star_links(placed_items, occupancy_matrix), [])

    def test_self_targeting_star_cell_creates_no_link(self):
        item_catalog = {
            "source": {
                "item_id": "source",
                "shape_cells": [(0, 0)],
                "star_cells": [(0, 0)],
            }
        }
        occupancy_matrix, placed_items = build_occupancy_matrix(
            [{"item_id": "source", "x": 0, "y": 0, "rotation": 0}],
            item_catalog,
        )

        self.assertEqual(find_star_links(placed_items, occupancy_matrix), [])


if __name__ == "__main__":
    unittest.main()
