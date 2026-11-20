# Side quest: Nulls, denominators, and conditional aggregation

Allow 20–30 minutes. This optional exercise uses synthetic DuckDB queries, not
changes to your Olist tables. Predict each result before running it in DBeaver.

## Counting rows is not counting known values

```sql
WITH example_reviews(order_id, score) AS (
    VALUES (1, 5), (2, NULL), (3, 1), (4, 0)
)
SELECT
    count(*) AS all_orders
  , count(score) AS known_scores
  , count(*) FILTER (WHERE score >= 4) AS positive_orders
  , avg(score) AS known_score_mean
  , avg(coalesce(score, 0)) AS zero_filled_mean
FROM example_reviews;
```

Expect four orders, three known scores, one positive order, a known-score mean of 2,
and a zero-filled mean of 1.5. Zero is an observed value in this invented scale; null
means unknown. This is not the Olist review-score domain.

`count(column)` and `avg(column)` exclude null values. `count(*)` counts rows.
`coalesce` substitutes a value, but substituting zero changes the meaning of a mean.
Whether that substitution is justified is an analytical question.

## The same numerator can answer different questions

```sql
WITH example_reviews(order_id, score) AS (
    VALUES (1, 5), (2, NULL), (3, 1), (4, 0)
)
SELECT
    count(*) FILTER (WHERE score >= 4) / nullif(count(*), 0)
        AS positive_share_all_orders
  , count(*) FILTER (WHERE score >= 4) / nullif(count(score), 0)
        AS positive_share_known_scores
  , sum(CASE WHEN score >= 4 THEN 1 ELSE 0 END) AS positive_orders
FROM example_reviews;
```

Expect 0.25, approximately 0.3333, and 1. The first share counts unknown scores in
the population without claiming they were positive. The second describes only known
scores. Neither automatically estimates what the unknown customers thought.

`FILTER` limits rows for one aggregate without removing them from every other
aggregate. A query-level `WHERE score >= 4` would change all the denominators.
The `CASE` expression gives an alternative conditional count for this nonempty input.

DuckDB's `/` performs ordinary division here. Do not assume every SQL engine handles
integer operands identically; check your target engine.

## Undefined is not zero

```sql
WITH example_reviews(order_id, score) AS (
    VALUES (1, 5), (2, NULL), (3, 1), (4, 0)
)
SELECT
    count(*) AS rows_remaining
  , sum(CASE WHEN score >= 4 THEN 1 ELSE 0 END) AS positive_sum
  , count(*) FILTER (WHERE score >= 4) / nullif(count(score), 0)
        AS positive_share
FROM example_reviews
WHERE order_id > 100;
```

Expect one aggregate output row containing 0, null, and null. With no input rows,
`count` returns zero but `sum` returns null. `nullif(denominator, 0)` makes a zero
denominator null, so the resulting rate is undefined rather than a claimed zero rate.
Do not automatically replace an undefined rate with zero for presentation.

**Checkpoint:** explain why single-category baskets belong in the affinity population
although they contribute no category pairs. What question would support answer if you
silently restricted its denominator to multi-category baskets?

Return to [Lesson 3](README.md), or consult the
[SQL reference](../sql_reference.md) for syntax details.
