# Side quest: Think in expressions

Allow 20–30 minutes. This is optional; you can continue to Lesson 7 without it.
Run the snippets in order in a scratch script or an optional IPython session.

## A value now, or instructions for a column?

Python can calculate `4 / 100` immediately. A Polars expression describes a
calculation to apply to a table. Constructing an expression alone does not choose
which table supplies its values.

```python
import polars as pl

pairs = pl.DataFrame({"category": ["A", "B", "C"], "baskets": [4, 10, 0]})
share = pl.col("baskets") / 100
print(share)
print(pairs.select(share.alias("support")))
```

Here 100 is an explicitly assumed population, not a denominator Polars discovered.
`alias` names an output; it does not change the source column.

**Predict:** how many rows and columns will the `select` result contain?
Expect three rows and one column. The original `pairs` still has its two columns.

## Context decides how an expression is used

```python
annotated = pairs.with_columns(share.alias("support"))
selected = annotated.filter(pl.col("support") >= 0.04)
print(annotated)
print(selected)
print(pairs.select(pl.col("baskets").sum().alias("total_occurrences")))
```

`with_columns` retains existing columns and adds or replaces named columns.
`filter` retains rows where its condition is true. `select` chooses expressions;
an aggregation such as `sum` can reduce the result to one row.

The sum is 14 category occurrences. It is not necessarily 14 distinct baskets:
categories can overlap. An expression can be syntactically correct and still answer
the wrong analytical question.

## Dependencies need separate steps

```python
result = pairs.with_columns(share.alias("support")).with_columns(
    (pl.col("support") * 100).alias("support_percent")
)
print(result)
```

Do not assume sibling expressions in one `with_columns` call run as sequential
Python assignments. The second step explicitly uses the column created by the first.

For multiple conditions use `&` or `|`, with parentheses around each comparison:

```python
print(pairs.filter((pl.col("baskets") > 0) & (pl.col("category") != "B")))
```

Python's scalar `and` and `or` are not substitutes for these column operators.

**Checkpoint:** change the population to 200. Predict which rows still pass the
support threshold before rerunning. Explain why a new denominator changes the answer
without changing the category counts.

Return to [Lesson 6](README.md).
