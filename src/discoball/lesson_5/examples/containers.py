from itertools import chain, islice, pairwise


def main() -> None:
    files = ["orders.csv", "products.csv"]
    files.append("customers.csv")
    for position, filename in enumerate(files, start=1):
        print(f"{position}. {filename}")

    basket_sizes = [3, 1, 2]
    sizes_by_file = dict(zip(files, basket_sizes, strict=True))
    print("Illustrative counts, not actual source counts:", sizes_by_file)
    shortlist = [filename for filename, size in sizes_by_file.items() if size >= 2]
    print("Shortlist:", shortlist)

    shared = files
    shared.append("order_items.csv")
    print("Assignment shares the list:", files)
    independent = files.copy()
    independent.append("sellers.csv")
    print("A shallow copy has its own outer list:", independent)
    print("Original list is unchanged by that last append:", files)

    pair = ("A", "B")
    category_a, category_b = pair
    pair_counts = {pair: 4}
    print(f"Pair {category_a}–{category_b}: {pair_counts[pair]} baskets")
    print("First two filenames:", list(islice(iter(files), 2)))
    print("Combined lists:", list(chain(["orders.csv"], ["products.csv"])))
    print("Adjacent observations:", list(pairwise([10, 12, 9])))


if __name__ == "__main__":
    main()
