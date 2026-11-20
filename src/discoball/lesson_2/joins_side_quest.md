# Side quest: Grain, joins, and missing matches

Allow 25–35 minutes. This is optional; return to the main lesson whenever you are
ready. Run each query in DuckDB through DBeaver. Each query defines its own tiny
input using `VALUES`; it does not change your database tables.

## Predict the output before executing

```sql
WITH example_orders(order_id, product_id) AS (
    VALUES (1, 'A'), (2, 'B'), (3, 'X')
), example_products(product_id, category_name) AS (
    VALUES ('A', 'beauty'), ('B', NULL)
)
SELECT
    o.order_id
  , o.product_id
  , p.product_id AS matched_product_id
  , p.category_name
FROM example_orders AS o
LEFT JOIN example_products AS p ON o.product_id = p.product_id
ORDER BY o.order_id;
```

The left population contains three orders. Expect three output rows. Order 2 matches
product B, which has a missing category. Order 3 does not match a product at all.
Testing only `category_name IS NULL` would mix those two conditions.

Here an order has just one product. That is a synthetic simplification, not the grain
of Olist's order-items table.

**Your turn:** insert `WHERE p.category_name IS NOT NULL` before `ORDER BY`.
Predict which orders remain. Expect only order 1: the later filter removes unmatched
rows despite the left join. Filtering is a population decision, not just tidying.

## Matching is not the same as attaching columns

```sql
WITH example_orders(order_id, product_id) AS (
    VALUES (1, 'A'), (2, 'B'), (3, 'X')
), example_products(product_id) AS (
    VALUES ('A'), ('A'), ('B')
)
SELECT o.*
FROM example_orders AS o
ANTI JOIN example_products AS p ON o.product_id = p.product_id;
```

Expect order 3. DuckDB's `ANTI JOIN` finds left rows without a match. Change it to
`SEMI JOIN`: expect orders 1 and 2, each once. These joins answer existence questions
without attaching right-side columns. Duplicate A keys do not duplicate order 1 in
a semi join.

Change it to `LEFT JOIN` while keeping `SELECT o.*`. Expect four rows. Selecting
only left columns does not prevent multiplication by duplicate matches.

## Investigate the lookup before using it

```sql
WITH example_products(product_id, category_name) AS (
    VALUES ('A', 'beauty'), ('A', 'beauty'), ('B', NULL)
)
SELECT
    product_id
  , count(*) AS lookup_rows
FROM example_products
GROUP BY product_id
HAVING count(*) > 1;
```

Expect A with two rows. Ask what one lookup row should represent, whether duplicates
are identical or conflicting, and who owns the correction. `DISTINCT` is not a
universal repair: it can hide repeated records without resolving conflicting labels.

**Checkpoint:** describe separately the preserved population, join relationship,
missing-match check, and post-join eligibility filter in Lesson 2's analysis. Why
would counting joined rows without checking grain overstate some results?

See the [SQL reference](../sql_reference.md) for syntax, then return to
[Lesson 2](README.md).
