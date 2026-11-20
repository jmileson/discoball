import polars as pl

from discoball.const import OLIST_DIR


def main() -> None:
    orders = pl.read_csv(
        OLIST_DIR / "orders.csv",
        columns=["order_id", "order_status"],
        infer_schema=False,
    ).rename({"order_status": "status"})
    print(orders.head(5))
    print(orders.schema)
    print(
        orders.group_by("status")
        .agg(pl.len().alias("order_count"))
        .sort(["order_count", "status"], descending=[True, False])
    )
    delivered = orders.filter(pl.col("status") == "delivered")
    print(f"Delivered orders: {delivered.height:,}")
    if orders["order_id"].n_unique() != orders.height:
        raise ValueError("Expected one row per order_id.")


if __name__ == "__main__":
    main()
