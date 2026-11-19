import json
from dataclasses import dataclass

import duckdb

from .const import DB, OLIST_DIR


@dataclass
class Table:
    name: str
    column_types: dict[str, str]
    column_names: list[str]


TABLES: list[Table] = [
    Table(
        name="customers",
        column_types={
            "customer_id": "UUID",
            "customer_unique_id": "UUID",
            "zip_code_prefix": "VARCHAR",
        },
        column_names=[
            "customer_id",
            "customer_unique_id",
            "zip_code_prefix",
            "city",
            "state",
        ],
    ),
    Table(
        name="orders",
        column_types={
            "order_id": "UUID",
            "customer_id": "UUID",
            "ordered_at": "TIMESTAMPTZ",
            "approved_at": "TIMESTAMPTZ",
            "carrier_delivered_at": "TIMESTAMPTZ",
            "customer_delivered_at": "TIMESTAMPTZ",
            "estimated_delivered_at": "TIMESTAMPTZ",
        },
        column_names=[
            "order_id",
            "customer_id",
            "status",
            "ordered_at",
            "approved_at",
            "carrier_delivered_at",
            "customer_delivered_at",
            "estimated_delivered_at",
        ],
    ),
    Table(
        "order_items",
        column_types={
            "order_id": "UUID",
            "order_item_id": "INT",
            "product_id": "UUID",
            "seller_id": "UUID",
            "shipping_limit_at": "TIMESTAMPTZ",
            "price": "DECIMAL(18, 2)",
            "freight_price": "DECIMAL(18, 2)",
        },
        column_names=[
            "order_id",
            "order_item_id",
            "product_id",
            "seller_id",
            "shipping_limit_at",
            "price",
            "freight_price",
        ],
    ),
    Table(
        name="geolocation",
        column_types={
            "zip_code_prefix": "VARCHAR",
            "latitude": "DOUBLE",
            "longitude": "DOUBLE",
            "city": "VARCHAR",
            "state": "VARCHAR",
        },
        column_names=[
            "zip_code_prefix",
            "latitude",
            "longitude",
            "city",
            "state",
        ],
    ),
    Table(
        name="order_payments",
        column_types={
            "order_id": "UUID",
            "payment_sequential": "INT",
            "payment_type": "VARCHAR",
            "payment_installments": "INT",
            "payment_value": "DECIMAL(18, 2)",
        },
        column_names=[
            "order_id",
            "payment_sequential",
            "payment_type",
            "payment_installments",
            "payment_value",
        ],
    ),
    Table(
        name="order_reviews",
        column_types={
            "review_id": "UUID",
            "order_id": "UUID",
            "score": "INT",
            "created_at": "TIMESTAMPTZ",
            "answered_at": "TIMESTAMPTZ",
        },
        column_names=[
            "review_id",
            "order_id",
            "score",
            "comment_title",
            "comment_message",
            "created_at",
            "answered_at",
        ],
    ),
    Table(
        name="product_categories",
        column_types={},
        column_names=[
            "category_name",
            "category_name_english",
        ],
    ),
    Table(
        name="products",
        column_types={
            "product_id": "UUID",
            "name_length": "INT",
            "description_length": "INT",
            "photos_qty": "INT",
            "weight_g": "INT",
            "length_cm": "INT",
            "height_cm": "INT",
            "width_cm": "INT",
        },
        column_names=[
            "product_id",
            "category_name",
            "name_length",
            "description_length",
            "photos_qty",
            "weight_g",
            "length_cm",
            "height_cm",
            "width_cm",
        ],
    ),
    Table(
        name="sellers",
        column_types={
            "seller_id": "UUID",
            "zip_code_prefix": "VARCHAR",
        },
        column_names=[
            "seller_id",
            "zip_code_prefix",
            "city",
            "state",
        ],
    ),
]


def main():
    DB.parent.mkdir(exist_ok=True)
    conn = duckdb.connect(DB, config={"storage_compatibility_version": "v1.5.0"})

    for table in TABLES:
        file_name = OLIST_DIR / f"{table.name}.csv"
        conn.execute(f"""--sql
            CREATE TABLE IF NOT EXISTS {table.name} AS 
            SELECT *
            FROM read_csv(
                '{file_name}',
                header=true,
                column_types={json.dumps(table.column_types)},
                column_names={json.dumps(table.column_names)},
            )
        """)

    for table in TABLES:
        result = conn.sql(f"""--sql
            SELECT count(*) AS cnt
            FROM {table.name}
        """).fetchall()

        count = result[0][0]
        print(f"{table.name}: {count} rows")
