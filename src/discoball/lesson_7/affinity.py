import polars as pl

from discoball.const import OLIST_DIR


def load_basket_categories() -> pl.DataFrame:
    orders = pl.read_csv(
        OLIST_DIR / "orders.csv",
        columns=["order_id", "order_status"],
        infer_schema=False,
    ).rename({"order_status": "status"})
    items = pl.read_csv(
        OLIST_DIR / "order_items.csv",
        columns=["order_id", "product_id"],
        infer_schema=False,
    )
    products = pl.read_csv(
        OLIST_DIR / "products.csv",
        columns=["product_id", "product_category_name"],
        infer_schema=False,
    ).rename({"product_category_name": "category_name"})
    return (
        orders.filter(pl.col("status") == "delivered")
        .join(items, on="order_id", how="inner", validate="1:m")
        .join(products, on="product_id", how="inner", validate="m:1")
        .filter(
            pl.col("category_name").is_not_null()
            & (pl.col("category_name").str.strip_chars() != "")
        )
        .select("order_id", "category_name")
        .unique()
    )


def calculate_affinity(baskets: pl.DataFrame) -> pl.DataFrame:
    if baskets.is_empty():
        raise ValueError("No eligible baskets. Check inputs and eligibility rules.")
    if baskets.unique(subset=["order_id", "category_name"]).height != baskets.height:
        raise ValueError("Expected one row per order and category.")
    if baskets.select(pl.any_horizontal(pl.all().is_null()).any()).item():
        raise ValueError("Basket keys and categories must not be null.")

    population = baskets["order_id"].n_unique()
    counts = baskets.group_by("category_name").agg(pl.len().alias("category_baskets"))
    pairs = (
        baskets.rename({"category_name": "category_a"})
        .join(
            baskets.rename({"category_name": "category_b"}),
            on="order_id",
            how="inner",
        )
        .filter(pl.col("category_a") < pl.col("category_b"))
        .group_by("category_a", "category_b")
        .agg(pl.len().alias("pair_baskets"))
    )
    result = (
        pairs.join(
            counts.rename(
                {"category_name": "category_a", "category_baskets": "a_baskets"}
            ),
            on="category_a",
            validate="m:1",
        )
        .join(
            counts.rename(
                {"category_name": "category_b", "category_baskets": "b_baskets"}
            ),
            on="category_b",
            validate="m:1",
        )
        .with_columns(pl.lit(population).alias("eligible_baskets"))
        .with_columns(
            (pl.col("pair_baskets") / pl.col("eligible_baskets")).alias("support"),
            (pl.col("pair_baskets") / pl.col("a_baskets")).alias("confidence_a_to_b"),
            (pl.col("pair_baskets") / pl.col("b_baskets")).alias("confidence_b_to_a"),
        )
        .with_columns(
            (
                pl.col("confidence_a_to_b")
                / (pl.col("b_baskets") / pl.col("eligible_baskets"))
            ).alias("lift")
        )
        .sort(
            ["pair_baskets", "category_a", "category_b"],
            descending=[True, False, False],
        )
    )
    invalid = result.filter(
        (pl.col("pair_baskets") > pl.col("a_baskets"))
        | (pl.col("pair_baskets") > pl.col("b_baskets"))
        | (pl.col("a_baskets") > population)
        | (pl.col("b_baskets") > population)
    )
    if not invalid.is_empty():
        raise ValueError("Affinity counts violate population constraints.")
    return result


def main() -> None:
    baskets = load_basket_categories()
    print(f"Eligible baskets: {baskets['order_id'].n_unique():,}")
    print(calculate_affinity(baskets).head(10))


if __name__ == "__main__":
    main()
