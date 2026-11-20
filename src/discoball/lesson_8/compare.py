from pathlib import Path

import duckdb
import polars as pl
from polars.testing import assert_frame_equal

from discoball.const import DB
from discoball.lesson_7.affinity import calculate_affinity, load_basket_categories


def main() -> None:
    query = Path(__file__).with_name("affinity.sql").read_text(encoding="utf-8")
    with duckdb.connect(str(DB), read_only=True) as connection:
        result = connection.execute(query)
        names = [column[0] for column in result.description]
        # Only the small category-pair summary crosses into Python, not raw items.
        sql_result = pl.DataFrame(result.fetchall(), schema=names, orient="row")

    polars_result = calculate_affinity(load_basket_categories())
    keys = ["category_a", "category_b"]
    assert_frame_equal(
        polars_result.select(sql_result.columns).sort(keys),
        sql_result.sort(keys),
        check_dtypes=False,
        check_exact=False,
        rel_tol=1e-10,
        abs_tol=1e-12,
    )
    print(f"SQL and Polars agree on all {sql_result.height} observed category pairs.")


if __name__ == "__main__":
    main()
