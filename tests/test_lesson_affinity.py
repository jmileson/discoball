import unittest

import polars as pl

from discoball.lesson_7.affinity import calculate_affinity


class AffinityTests(unittest.TestCase):
    def test_hand_calculated_example(self):
        baskets = pl.DataFrame(
            {
                "order_id": ["1", "1", "2", "3"],
                "category_name": ["A", "B", "A", "B"],
            }
        )
        result = calculate_affinity(baskets)
        self.assertEqual(result.height, 1)
        row = result.row(0, named=True)
        self.assertEqual((row["category_a"], row["category_b"]), ("A", "B"))
        self.assertEqual(row["pair_baskets"], 1)
        self.assertEqual(row["eligible_baskets"], 3)
        self.assertAlmostEqual(row["support"], 1 / 3)
        self.assertAlmostEqual(row["confidence_a_to_b"], 0.5)
        self.assertAlmostEqual(row["confidence_b_to_a"], 0.5)
        self.assertAlmostEqual(row["lift"], 0.75)

    def test_duplicate_grain_is_rejected(self):
        baskets = pl.DataFrame({"order_id": ["1", "1"], "category_name": ["A", "A"]})
        with self.assertRaisesRegex(ValueError, "one row per order"):
            calculate_affinity(baskets)

    def test_no_pairs_is_valid(self):
        baskets = pl.DataFrame({"order_id": ["1", "2"], "category_name": ["A", "B"]})
        self.assertTrue(calculate_affinity(baskets).is_empty())

    def test_empty_population_is_rejected(self):
        baskets = pl.DataFrame(
            schema={"order_id": pl.String, "category_name": pl.String}
        )
        with self.assertRaisesRegex(ValueError, "No eligible baskets"):
            calculate_affinity(baskets)

    def test_null_keys_are_rejected(self):
        baskets = pl.DataFrame({"order_id": ["1", None], "category_name": ["A", "B"]})
        with self.assertRaisesRegex(ValueError, "must not be null"):
            calculate_affinity(baskets)


if __name__ == "__main__":
    unittest.main()
