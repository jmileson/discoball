# Side quest: Types, nulls, and messy inputs

Allow 25–35 minutes. Optional: these examples do not alter the Olist files.
Run the snippets in order in a scratch script.

## A failed conversion is evidence

```python
import polars as pl

raw = pl.DataFrame({"count_text": ["4", "", None, "unknown", "0"]})
print(raw.schema)
try:
    print(raw.with_columns(pl.col("count_text").cast(pl.Int64).alias("count")))
except pl.exceptions.InvalidOperationError as error:
    print(type(error).__name__)
```

The input is text. A blank string is not a null, and `unknown` is not an integer.
Strict casting refuses to silently invent counts. Catching this error here is a
teaching exercise, not a recommendation to suppress failures in a reporting script.

**Predict:** which values would become null if conversion failures were allowed?

```python
parsed = raw.with_columns(
    pl.col("count_text").cast(pl.Int64, strict=False).alias("count")
)
print(parsed)
print(parsed.filter(pl.col("count_text").is_not_null() & pl.col("count").is_null()))
```

The second output identifies two failed conversions, distinct from the original
missing value. Preserve the raw field so you can investigate the difference.
Non-strict casting is useful for diagnosis; it is not validation by itself.

## Missing does not mean zero

```python
print(
    parsed.select(
        pl.len().alias("rows"),
        pl.col("count").count().alias("known_counts"),
        pl.col("count").mean().alias("known_mean"),
        pl.col("count").fill_null(0).mean().alias("zero_filled_mean"),
    )
)
print(parsed.filter(pl.col("count") > 0))
```

Expect five rows, two known counts, a known-value mean of 2, and a zero-filled
mean of 0.8. Neither mean is automatically the correct business measure. Replacing
unknown values with zero asserts that nothing occurred. Filtering keeps only true
conditions, so rows with null comparisons do not survive.

## NaN is a different condition

```python
measurements = pl.DataFrame({"value": [1.0, None, float("nan")]})
print(
    measurements.with_columns(
        pl.col("value").is_null().alias("missing"),
        pl.col("value").is_nan().alias("not_a_number"),
    )
)
```

NaN is a floating-point value representing “not a number”; null represents missing
data. `fill_null` does not remove NaN. Investigate how each arose before using
`fill_nan` or excluding rows. The NaN test itself returns null for the missing value.

When reading real files, choose types intentionally using `schema_overrides` where
appropriate. Keep identifiers as strings when leading zeroes matter. A successful
cast does not prove a value is sensible: negative counts still need a domain check.

**Checkpoint:** document whether a missing count should fail a run, be excluded with
an explicit coverage note, or be resolved with the source owner. Why is silent zero
filling inappropriate for your chosen case?

Return to [Lesson 6](README.md).
