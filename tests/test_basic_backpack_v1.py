import unittest

from basic_backpack_v1 import (
    ITEM_CATALOG,
    build_occupancy_matrix,
    find_diamond_links,
    find_star_links,
    find_triangle_links,
    place_item,
    rotate_cells,
)


class BasicBackpackV1Test(unittest.TestCase):
    def test_wooden_buckler_occupies_two_by_two_cells_without_markers(self):
        occupancy_matrix, placed_items = build_occupancy_matrix(
            [{"item_id": "wooden_buckler", "x": 0, "y": 0, "rotation": 0}],
            ITEM_CATALOG,
        )

        self.assertEqual(
            ITEM_CATALOG["wooden_buckler"]["shape_cells"],
            [[0, 0], [1, 0], [0, 1], [1, 1]],
        )
        self.assertEqual(ITEM_CATALOG["wooden_buckler"]["star_cells"], [])
        self.assertEqual(
            placed_items[0]["occupied_cells"],
            [(0, 0), (1, 0), (0, 1), (1, 1)],
        )
        self.assertEqual(occupancy_matrix[6][0], "wooden_buckler1")
        self.assertEqual(occupancy_matrix[6][1], "wooden_buckler1")
        self.assertEqual(occupancy_matrix[5][0], "wooden_buckler1")
        self.assertEqual(occupancy_matrix[5][1], "wooden_buckler1")

    def test_wooden_sword_occupies_two_vertical_cells_without_markers(self):
        occupancy_matrix, placed_items = build_occupancy_matrix(
            [{"item_id": "wooden_sword", "x": 0, "y": 0, "rotation": 0}],
            ITEM_CATALOG,
        )

        self.assertEqual(
            ITEM_CATALOG["wooden_sword"]["shape_cells"],
            [[0, 0], [0, 1]],
        )
        self.assertEqual(ITEM_CATALOG["wooden_sword"]["star_cells"], [])
        self.assertEqual(
            placed_items[0]["occupied_cells"],
            [(0, 0), (0, 1)],
        )
        self.assertEqual(occupancy_matrix[6][0], "wooden_sword1")
        self.assertEqual(occupancy_matrix[5][0], "wooden_sword1")

    def test_banana_catalog_matches_wiki_grid(self):
        _, placed_items = build_occupancy_matrix(
            [{"item_id": "banana", "x": 2, "y": 2, "rotation": 0}],
            ITEM_CATALOG,
        )

        self.assertEqual(
            ITEM_CATALOG["banana"]["shape_cells"],
            [[0, 1], [0, 0], [1, 0]],
        )
        self.assertEqual(
            ITEM_CATALOG["banana"]["star_cells"],
            [
                [0, 2],
                [-1, 1],
                [1, 1],
                [-1, 0],
                [2, 0],
                [0, -1],
                [1, -1],
            ],
        )
        self.assertCountEqual(
            placed_items[0]["occupied_cells"],
            [(2, 3), (2, 2), (3, 2)],
        )
        self.assertCountEqual(
            placed_items[0]["star_cells"],
            [
                (2, 4),
                (1, 3),
                (3, 3),
                (1, 2),
                (4, 2),
                (2, 1),
                (3, 1),
            ],
        )
        self.assertEqual(placed_items[0]["diamond_cells"], [])
        self.assertEqual(placed_items[0]["triangle_cells"], [])

    def test_garlic_catalog_matches_wiki_grid(self):
        _, placed_items = build_occupancy_matrix(
            [{"item_id": "garlic", "x": 2, "y": 2, "rotation": 0}],
            ITEM_CATALOG,
        )

        self.assertEqual(
            ITEM_CATALOG["garlic"]["shape_cells"],
            [[0, 1], [0, 0]],
        )
        self.assertEqual(
            ITEM_CATALOG["garlic"]["star_cells"],
            [
                [0, 2],
                [-1, 1],
                [1, 1],
                [-1, 0],
                [1, 0],
                [0, -1],
            ],
        )
        self.assertCountEqual(
            placed_items[0]["occupied_cells"],
            [(2, 3), (2, 2)],
        )
        self.assertCountEqual(
            placed_items[0]["star_cells"],
            [
                (2, 4),
                (1, 3),
                (3, 3),
                (1, 2),
                (3, 2),
                (2, 1),
            ],
        )
        self.assertEqual(placed_items[0]["diamond_cells"], [])
        self.assertEqual(placed_items[0]["triangle_cells"], [])

    def test_garlic_catalog_rotates_shape_and_stars(self):
        placed_item = place_item(
            ITEM_CATALOG["garlic"],
            {
                "item_id": "garlic",
                "item_key": "garlic1",
                "x": 3,
                "y": 3,
                "rotation": 90,
            },
        )

        self.assertCountEqual(
            placed_item["occupied_cells"],
            [(2, 3), (3, 3)],
        )
        self.assertCountEqual(
            placed_item["star_cells"],
            [
                (1, 3),
                (2, 2),
                (2, 4),
                (3, 2),
                (3, 4),
                (4, 3),
            ],
        )

    def test_pan_catalog_matches_wiki_grid(self):
        _, placed_items = build_occupancy_matrix(
            [{"item_id": "pan", "x": 2, "y": 2, "rotation": 0}],
            ITEM_CATALOG,
        )

        self.assertEqual(
            ITEM_CATALOG["pan"]["shape_cells"],
            [[1, 1], [0, 0], [1, 0]],
        )
        self.assertEqual(
            ITEM_CATALOG["pan"]["star_cells"],
            [
                [1, 2],
                [0, 1],
                [2, 1],
                [-1, 0],
                [2, 0],
                [0, -1],
                [1, -1],
            ],
        )
        self.assertCountEqual(
            placed_items[0]["occupied_cells"],
            [(3, 3), (2, 2), (3, 2)],
        )
        self.assertCountEqual(
            placed_items[0]["star_cells"],
            [
                (3, 4),
                (2, 3),
                (4, 3),
                (1, 2),
                (4, 2),
                (2, 1),
                (3, 1),
            ],
        )
        self.assertEqual(placed_items[0]["diamond_cells"], [])
        self.assertEqual(placed_items[0]["triangle_cells"], [])

    def test_pan_catalog_rotates_shape_and_stars(self):
        placed_item = place_item(
            ITEM_CATALOG["pan"],
            {
                "item_id": "pan",
                "item_key": "pan1",
                "x": 3,
                "y": 3,
                "rotation": 90,
            },
        )

        self.assertCountEqual(
            placed_item["occupied_cells"],
            [(2, 4), (3, 3), (3, 4)],
        )
        self.assertCountEqual(
            placed_item["star_cells"],
            [
                (1, 4),
                (2, 3),
                (2, 5),
                (3, 2),
                (3, 5),
                (4, 3),
                (4, 4),
            ],
        )
        self.assertNotIn("star_cells_by_rotation", ITEM_CATALOG["pan"])

    def test_broom_catalog_matches_wiki_vertical_grid(self):
        _, placed_items = build_occupancy_matrix(
            [{"item_id": "broom", "x": 4, "y": 3, "rotation": 0}],
            ITEM_CATALOG,
        )

        self.assertEqual(
            ITEM_CATALOG["broom"]["shape_cells"],
            [[0, 0], [0, 1], [0, 2], [0, 3]],
        )
        self.assertEqual(ITEM_CATALOG["broom"]["star_cells"], [])
        self.assertEqual(
            placed_items[0]["occupied_cells"],
            [(4, 3), (4, 4), (4, 5), (4, 6)],
        )
        self.assertEqual(placed_items[0]["star_cells"], [])
        self.assertEqual(placed_items[0]["diamond_cells"], [])
        self.assertEqual(placed_items[0]["triangle_cells"], [])

    def test_broom_catalog_rotates_four_cell_line(self):
        expected_cells = {
            0: [(4, 3), (4, 4), (4, 5), (4, 6)],
            90: [(4, 3), (3, 3), (2, 3), (1, 3)],
            180: [(4, 3), (4, 2), (4, 1), (4, 0)],
            270: [(4, 3), (5, 3), (6, 3), (7, 3)],
        }

        for rotation, expected in expected_cells.items():
            with self.subTest(rotation=rotation):
                placed_item = place_item(
                    ITEM_CATALOG["broom"],
                    {
                        "item_id": "broom",
                        "item_key": "broom1",
                        "x": 4,
                        "y": 3,
                        "rotation": rotation,
                    },
                )

                self.assertEqual(
                    placed_item["occupied_cells"],
                    expected,
                )
                self.assertEqual(
                    len(set(placed_item["occupied_cells"])),
                    4,
                )
                self.assertEqual(placed_item["star_cells"], [])
                self.assertEqual(placed_item["diamond_cells"], [])
                self.assertEqual(placed_item["triangle_cells"], [])

    def test_single_one_by_one_item_writes_to_bottom_left_matrix_cell(self):
        occupancy_matrix, placed_items = build_occupancy_matrix(
            [{"item_id": "stone", "x": 0, "y": 0, "rotation": 0}],
            ITEM_CATALOG,
        )

        self.assertEqual(placed_items[0]["item_key"], "stone1")
        self.assertEqual(placed_items[0]["occupied_cells"], [(0, 0)])
        self.assertEqual(occupancy_matrix[6][0], "stone1")

    def test_two_non_overlapping_items_write_item_keys(self):
        occupancy_matrix, placed_items = build_occupancy_matrix(
            [
                {"item_id": "stone", "x": 0, "y": 0, "rotation": 0},
                {"item_id": "stone", "x": 2, "y": 3, "rotation": 0},
            ],
            ITEM_CATALOG,
        )

        self.assertEqual(len(placed_items), 2)
        self.assertEqual(occupancy_matrix[6][0], "stone1")
        self.assertEqual(occupancy_matrix[3][2], "stone2")

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
        self.assertEqual(occupancy_matrix[4][2], "l_shape1")
        self.assertEqual(occupancy_matrix[3][2], "l_shape1")
        self.assertEqual(occupancy_matrix[4][1], "l_shape1")

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
        self.assertEqual(occupancy_matrix[6][1], "offset_item1")

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
            {"item_key": "star_source1", "item_id": "star_source", "x": 3, "y": 3, "rotation": 90},
        )

        self.assertEqual(placed_item["star_cells"], [(3, 4)])

    def test_special_star_cells_by_rotation_are_read_directly(self):
        placed_item = place_item(
            ITEM_CATALOG["bag_of_stones"],
            {"item_key": "bag_of_stones1", "item_id": "bag_of_stones", "x": 3, "y": 3, "rotation": 90},
        )

        self.assertEqual(placed_item["occupied_cells"], [(3, 3), (3, 4)])
        self.assertEqual(placed_item["star_cells"], [(3, 5)])

    def test_bag_of_stones_special_star_cells_are_defined_for_all_rotations(self):
        expected_by_rotation = {
            0: ([(3, 3), (4, 3)], [(3, 4), (4, 4)]),
            90: ([(3, 3), (3, 4)], [(3, 5)]),
            180: ([(3, 3), (2, 3)], [(3, 4), (2, 4)]),
            270: ([(3, 3), (3, 2)], [(3, 4)]),
        }

        for rotation, expected in expected_by_rotation.items():
            with self.subTest(rotation=rotation):
                placed_item = place_item(
                    ITEM_CATALOG["bag_of_stones"],
                    {"item_key": "bag_of_stones1", "item_id": "bag_of_stones", "x": 3, "y": 3, "rotation": rotation},
                )

                expected_occupied_cells, expected_star_cells = expected
                self.assertEqual(placed_item["occupied_cells"], expected_occupied_cells)
                self.assertEqual(placed_item["star_cells"], expected_star_cells)

    def test_health_potion_special_star_cells_are_defined_for_all_rotations(self):
        expected_by_rotation = {
            0: ([(3, 3), (3, 4)], [(3, 5)]),
            90: ([(3, 3), (2, 3)], [(2, 4)]),
            180: ([(3, 3), (3, 2)], [(3, 4)]),
            270: ([(3, 3), (4, 3)], [(4, 4)]),
        }

        for rotation, expected in expected_by_rotation.items():
            with self.subTest(rotation=rotation):
                placed_item = place_item(
                    ITEM_CATALOG["health_potion"],
                    {"item_key": "health_potion1", "item_id": "health_potion", "x": 3, "y": 3, "rotation": rotation},
                )

                expected_occupied_cells, expected_star_cells = expected
                self.assertEqual(placed_item["occupied_cells"], expected_occupied_cells)
                self.assertEqual(placed_item["star_cells"], expected_star_cells)

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

    def test_mage_hat_loads_star_diamond_and_triangle_cells(self):
        placed_item = place_item(
            ITEM_CATALOG["mage_hat"],
            {"item_key": "mage_hat1", "item_id": "mage_hat", "x": 3, "y": 3, "rotation": 0},
        )

        self.assertCountEqual(placed_item["occupied_cells"], [(3, 4), (2, 3), (3, 3), (4, 3)])
        self.assertEqual(placed_item["star_cells"], [(2, 4), (1, 3), (2, 2), (2, 1)])
        self.assertEqual(placed_item["diamond_cells"], [(4, 4), (5, 3), (4, 2), (4, 1)])
        self.assertEqual(placed_item["triangle_cells"], [(3, 6), (3, 5), (3, 2), (3, 1)])

    def test_mage_hat_marker_cells_rotate_like_ordinary_cells(self):
        placed_item = place_item(
            ITEM_CATALOG["mage_hat"],
            {"item_key": "mage_hat1", "item_id": "mage_hat", "x": 4, "y": 3, "rotation": 90},
        )

        self.assertCountEqual(placed_item["occupied_cells"], [(3, 3), (4, 2), (4, 3), (4, 4)])
        self.assertEqual(placed_item["star_cells"], [(3, 2), (4, 1), (5, 2), (6, 2)])
        self.assertEqual(placed_item["diamond_cells"], [(3, 4), (4, 5), (5, 4), (6, 4)])
        self.assertEqual(placed_item["triangle_cells"], [(1, 3), (2, 3), (5, 3), (6, 3)])

    def test_mage_hat_star_diamond_and_triangle_links_are_found(self):
        occupancy_matrix, placed_items = build_occupancy_matrix(
            [
                {"item_id": "mage_hat", "x": 3, "y": 3, "rotation": 0},
                {"item_id": "stone", "x": 2, "y": 4, "rotation": 0},
                {"item_id": "stone", "x": 4, "y": 4, "rotation": 0},
                {"item_id": "stone", "x": 3, "y": 6, "rotation": 0},
            ],
            ITEM_CATALOG,
        )

        self.assertEqual(
            find_star_links(placed_items, occupancy_matrix),
            [{"source_item_key": "mage_hat1", "target_item_key": "stone1", "star_cell": (2, 4)}],
        )
        self.assertEqual(
            find_diamond_links(placed_items, occupancy_matrix),
            [{"source_item_key": "mage_hat1", "target_item_key": "stone2", "diamond_cell": (4, 4)}],
        )
        self.assertEqual(
            find_triangle_links(placed_items, occupancy_matrix),
            [{"source_item_key": "mage_hat1", "target_item_key": "stone3", "triangle_cell": (3, 6)}],
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
            [{"source_item_key": "source1", "target_item_key": "target1", "star_cell": (1, 0)}],
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

    def test_mixed_backpack_scenario_builds_matrix_and_star_links(self):
        item_catalog = {
            "ordinary_source": {
                "item_id": "ordinary_source",
                "shape_cells": [(0, 0)],
                "star_cells": [(1, 0)],
            },
            "special_source": {
                "item_id": "special_source",
                "shape_cells": [(0, 0), (0, 1)],
                "star_cells_by_rotation": {
                    0: [(0, 2)],
                    90: [(-1, 1)],
                    180: [(0, 1)],
                    270: [(1, 1)],
                },
            },
            "empty_source": {
                "item_id": "empty_source",
                "shape_cells": [(0, 0)],
                "star_cells": [(1, 0)],
            },
            "out_of_bounds_source": {
                "item_id": "out_of_bounds_source",
                "shape_cells": [(0, 0)],
                "star_cells": [(0, 1)],
            },
            "target": {
                "item_id": "target",
                "shape_cells": [(0, 0)],
                "star_cells": [],
            },
        }
        occupancy_matrix, placed_items = build_occupancy_matrix(
            [
                {"item_id": "ordinary_source", "x": 0, "y": 0, "rotation": 0},
                {"item_id": "target", "x": 1, "y": 0, "rotation": 0},
                {"item_id": "special_source", "x": 5, "y": 2, "rotation": 90},
                {"item_id": "target", "x": 4, "y": 3, "rotation": 0},
                {"item_id": "empty_source", "x": 2, "y": 2, "rotation": 0},
                {"item_id": "out_of_bounds_source", "x": 8, "y": 6, "rotation": 0},
            ],
            item_catalog,
        )

        self.assertEqual(occupancy_matrix[6][0], "ordinary_source1")
        self.assertEqual(occupancy_matrix[6][1], "target1")
        self.assertEqual(occupancy_matrix[4][5], "special_source1")
        self.assertEqual(occupancy_matrix[4][4], "special_source1")
        self.assertEqual(occupancy_matrix[3][4], "target2")
        self.assertEqual(occupancy_matrix[4][2], "empty_source1")
        self.assertEqual(occupancy_matrix[0][8], "out_of_bounds_source1")
        self.assertEqual(
            find_star_links(placed_items, occupancy_matrix),
            [
                {"source_item_key": "ordinary_source1", "target_item_key": "target1", "star_cell": (1, 0)},
                {"source_item_key": "special_source1", "target_item_key": "target2", "star_cell": (4, 3)},
            ],
        )

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
