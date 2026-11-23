from pathlib import Path

from discoball.const import OLIST_DIR


def describe_file(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(f"Missing input: {path}. Check the project setup.")
    with open(path) as source:
        header = source.readline().strip()
    if header.startswith("version https://git-lfs.github.com/spec/v1"):
        raise ValueError(f"{path.name} is a Git LFS placeholder. Run git lfs pull.")
    return f"{path.name}: {path.stat().st_size:,} bytes\nHeader: {header}"


def main() -> None:
    required_files = ["orders.csv", "order_items.csv", "products.csv"]
    for name in required_files:
        print(describe_file(OLIST_DIR / name))


if __name__ == "__main__":
    main()
