import csv
import json
import tempfile
import unittest
from pathlib import Path

from discoball.lesson_5.examples.functions import add_note, passes_threshold
from discoball.lesson_5.examples.numbers import support
from discoball.lesson_5.examples.objects import CategoryReview, parse_review
from discoball.lesson_5.examples.text_files import write_example_files


class FoundationTests(unittest.TestCase):
    def test_default_notes_are_independent(self):
        first = add_note("First")
        second = add_note("Second")
        self.assertEqual(first, ["First"])
        self.assertEqual(second, ["Second"])
        self.assertIsNot(first, second)

    def test_explicit_notes_are_mutated(self):
        notes = []
        self.assertIs(add_note("Check", notes), notes)
        self.assertEqual(notes, ["Check"])

    def test_threshold_keyword_and_bounds(self):
        self.assertTrue(passes_threshold(10))
        self.assertFalse(passes_threshold(10, minimum=20))
        with self.assertRaises(ValueError):
            passes_threshold(-1)
        with self.assertRaises(TypeError):
            # Deliberately violate the signature to check the runtime failure.
            passes_threshold(10, 20)  # ty: ignore[too-many-positional-arguments]

    def test_support_denominator_and_count_bounds(self):
        self.assertEqual(support(0, 100), 0)
        self.assertAlmostEqual(support(4, 100), 0.04)
        for args in [(4, 0), (-1, 100), (101, 100)]:
            with self.subTest(args=args), self.assertRaises(ValueError):
                support(*args)

    def test_csv_json_round_trip_and_replacement(self):
        with tempfile.TemporaryDirectory() as folder:
            csv_path, json_path = write_example_files(Path(folder))
            with open(csv_path, newline="") as source:
                csv_rows = list(csv.DictReader(source))
            with open(json_path) as source:
                json_rows = json.load(source)
            self.assertEqual(csv_rows[0]["category"], "Health, beauty")
            self.assertIsInstance(csv_rows[0]["basket_count"], str)
            self.assertIsInstance(json_rows[0]["basket_count"], int)
            self.assertEqual(json_rows[1]["category"], "Café")
            self.assertEqual(
                [parse_review(row) for row in csv_rows],
                [parse_review(row) for row in json_rows],
            )
            before = json_path.read_bytes()
            write_example_files(Path(folder))
            self.assertEqual(json_path.read_bytes(), before)

    def test_validated_record(self):
        review = parse_review({"category": " A ", "basket_count": "4"})
        self.assertEqual(review, CategoryReview("A", 4))
        self.assertEqual(review.describe(), "A: 4 baskets")

    def test_invalid_records_are_rejected(self):
        invalid = [
            None,
            [],
            {},
            {"category": " ", "basket_count": 4},
            {"category": "A", "basket_count": -1},
            {"category": "A", "basket_count": True},
            {"category": "A", "basket_count": 1.5},
            {"category": "A", "basket_count": "unknown"},
        ]
        for value in invalid:
            with self.subTest(value=value), self.assertRaises((TypeError, ValueError)):
                parse_review(value)


if __name__ == "__main__":
    unittest.main()
