# Side quest: Joins preserve—or change—your population

Allow 25–35 minutes. Run these synthetic examples in order in a scratch script.
This optional exercise prepares you for Lesson 7's join checks.

## Start with a population

```python
import polars as pl

orders = pl.DataFrame({"order_id": [1, 2, 3], "product_id": ["A", "B", "X"]})
products = pl.DataFrame({"product_id": ["A", "B"], "category": ["beauty", None]})
joined = orders.join(products, on="product_id", how="left", validate="m:1")
print(joined.sort("order_id"))
```

The grain is one order here only because this deliberately tiny example has one
product per order. Real Olist orders can have multiple items.

**Predict:** how many rows survive? Expect three. A left join preserves the orders,
including product X without a lookup match. `m:1` checks uniqueness of lookup keys;
it does not require every order to match.

## Missing category or missing product?

```python
print(orders.join(products, on="product_id", how="anti"))
print(orders.join(products, on="product_id", how="semi"))
print(joined.filter(pl.col("category").is_not_null()))
```

The anti join returns order 3: its key has no match. The semi join returns orders 1
and 2, keeping only left-side columns and not multiplying rows for multiple matches.
The category filter returns only order 1. Order 2 matched a product but that product
has no category. These are different data-quality conditions.

Filtering right-side fields after a left join can remove the unmatched population.
That may be intentional, but write down the eligibility change.

## Duplicate lookups multiply rows

```python
duplicated = pl.concat([products, products.filter(pl.col("product_id") == "A")])
print(orders.join(duplicated, on="product_id", how="left").sort("order_id"))
try:
    orders.join(duplicated, on="product_id", how="left", validate="m:1")
except pl.exceptions.ComputeError as error:
    print(type(error).__name__)
```

The unchecked join produces four rows; the validated join fails. Even identical
lookup rows multiply matching facts. Do not add `unique()` to the final output just
to hide the symptom: first establish the lookup's intended grain and a defensible
resolution rule.

These examples use non-null keys. Polars does not match null join keys by default;
missing keys need a deliberate policy, not an assumption that they identify the
same entity.

**Checkpoint:** explain which check answers each question: “Is my lookup unique?”,
“Did every key match?”, and “Does every matched product have a category?” No single
join option establishes all three.

Return to [Lesson 6](README.md).
