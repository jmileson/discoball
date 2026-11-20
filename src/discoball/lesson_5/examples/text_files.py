import csv
import json
from pathlib import Path

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "outputs"


def write_example_files(output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "category_review.csv"
    json_path = output_dir / "category_review.json"
    # Synthetic rows: never overwrite or clean the source Olist files in place.
    rows = [
        {"category": " Health, beauty ", "basket_count": "4"},
        {"category": "Café", "basket_count": "2"},
    ]
    cleaned = [
        {
            "category": row["category"].strip(),
            "basket_count": int(row["basket_count"]),
        }
        for row in rows
    ]
    with csv_path.open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=["category", "basket_count"])
        writer.writeheader()
        writer.writerows(cleaned)
    with json_path.open("w", encoding="utf-8") as target:
        json.dump(cleaned, target, ensure_ascii=False, indent=2)
    return csv_path, json_path


def main() -> None:
    text = "Café"
    payload = text.encode("utf-8")
    print("Text characters:", len(text))
    print("UTF-8 bytes:", len(payload))
    print("Decoded:", payload.decode("utf-8"))
    csv_path, json_path = write_example_files(OUTPUT_DIR)
    with csv_path.open(encoding="utf-8", newline="") as source:
        for row in csv.DictReader(source):
            print("CSV record:", row, "count type:", type(row["basket_count"]).__name__)
    with json_path.open(encoding="utf-8") as source:
        records = json.load(source)
    print("JSON records:", records)
    print(f"Wrote {csv_path} and {json_path}; rerunning replaces these files.")


if __name__ == "__main__":
    main()
