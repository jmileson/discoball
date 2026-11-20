import csv
import json
from dataclasses import asdict, dataclass
from typing import NamedTuple, TypedDict

from discoball.lesson_5.examples.text_files import OUTPUT_DIR, write_example_files


class ReviewPayload(TypedDict):
    category: str
    basket_count: int


class CategoryPair(NamedTuple):
    category_a: str
    category_b: str


@dataclass
class CategoryReview:
    category: str
    basket_count: int

    def describe(self) -> str:
        return f"{self.category}: {self.basket_count:,} baskets"


def parse_review(raw: object) -> CategoryReview:
    if not isinstance(raw, dict):
        raise TypeError("Expected a record mapping.")
    category = raw.get("category")
    count = raw.get("basket_count")
    if not isinstance(category, str) or not category.strip():
        raise ValueError("Category must be non-blank text.")
    # CSV gives strings; JSON gives integers for these example counts.
    if isinstance(count, str):
        try:
            count = int(count)
        except ValueError as error:
            raise ValueError("Basket count must be a non-negative integer.") from error
    # bool is an int subclass, but True is not an appropriate count here.
    if type(count) is not int or count < 0:
        raise ValueError("Basket count must be a non-negative integer.")
    return CategoryReview(category.strip(), count)


def main() -> None:
    csv_path, json_path = write_example_files(OUTPUT_DIR)
    with csv_path.open(encoding="utf-8", newline="") as source:
        reviews = [parse_review(row) for row in csv.DictReader(source)]
    with json_path.open(encoding="utf-8") as source:
        raw = json.load(source)
    if not isinstance(raw, list):
        raise TypeError("Expected a JSON array of review records.")
    json_reviews = [parse_review(row) for row in raw]
    if reviews != json_reviews:
        raise ValueError("CSV and JSON records disagree.")
    for review in reviews:
        print(review.describe())
    payload: ReviewPayload = {
        "category": reviews[0].category,
        "basket_count": reviews[0].basket_count,
    }
    print("TypedDict value is still a dict:", type(payload).__name__)
    print("Dataclass as JSON:", json.dumps(asdict(reviews[0]), ensure_ascii=False))
    pair = CategoryPair("A", "B")
    print("Named tuple:", pair.category_a, pair.category_b)


if __name__ == "__main__":
    main()
