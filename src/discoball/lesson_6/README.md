# Lesson 6: Explore familiar data with Polars

You know how to summarize order statuses in SQL. Now you will answer that familiar
question with Polars, a Python library for working with tables.

Keep the question simple while learning the tool. Changing the language should not
silently change the population or the meaning of a row. Because you already know
what the SQL result means, you can concentrate on how dataframe expressions work.

Your output is a status summary checked against Lesson 1, plus a small executable
check of your own. This is a stepping stone to rebuilding basket affinity: you are
learning how to ask familiar questions of files directly, without first loading them
into database tables.

Allow about 60–90 minutes. Complete [Lesson 5](../lesson_5/README.md), then open [explore.py](explore.py).

## Optional side quests

Take these when you want more practice; none is required before Lesson 7.
Each uses small synthetic tables rather than modifying the source files.

1. [Think in expressions](expressions.md): column instructions, contexts, and dependencies.
2. [Types, nulls, and messy inputs](types_nulls.md): conversions, missing values, and NaN.
3. [Joins and analytical grain](joins.md): coverage, duplicate keys, and validation.

## 1. Run a dataframe workflow

From the project terminal:

```powershell
uv run python -m discoball.lesson_6.explore
```

You should see a five-row preview, a schema, status counts, and the delivered-order
count. With the supplied data, there are 99,441 orders and 96,478 delivered orders.

A **DataFrame** is a table held by Polars, with named columns and data types. It is not
an Excel sheet and does not automatically belong to DuckDB. In this script, its rows
live in your Python process.

## 2. Read only what you need

The script begins by reading two CSV columns:

```python
orders = pl.read_csv(
    OLIST_DIR / "orders.csv",
    columns=["order_id", "order_status"],
    infer_schema=False,
).rename({"order_status": "status"})
```

`import polars as pl` supplies the short library name `pl`. `read_csv` returns a
DataFrame. The following `.rename(...)` calls a method on that result.

The source CSV uses `order_status`; the DuckDB setup renamed it to `status`. This script
explicitly makes the same change. Original CSV identifiers are unhyphenated strings,
while the setup imported some identifiers as UUIDs. Do not assume reading a CSV
reproduces every database type conversion.

`infer_schema=False` reads the selected values as strings. That is deliberate for this
example: both selected columns are identifiers or labels. It is not a sensible default
for every numerical analysis. Prices and dates need intentional types before
calculations.

A dictionary such as `{"order_status": "status"}` maps keys to values. Here it maps old
names to new names.

**Your turn:** use `orders.schema`, `orders.height`, and `orders.head(5)` to explain the
table's types, size, and grain. A preview is not a random sample.

## 3. Build expressions, not loops over rows

```python
delivered = orders.filter(pl.col("status") == "delivered")
```

`pl.col("status")` constructs an expression referring to a column. The comparison
creates a boolean expression, and `filter` keeps rows where it is true. Like SQL
filtering, a null condition does not retain a row.

You normally express operations on whole columns rather than looping through rows in
Python. This lets Polars execute the tabular operation efficiently.

> **Watch out — column expressions are not scalar booleans**
>
> Combine Polars expressions with `&` for AND and `|` for OR, with each comparison
> in parentheses. Python's scalar `and` and `or` do not combine column expressions.
> Keep this distinction from Lesson 5 when translating a condition.

```python
selected = orders.filter(
    (pl.col("status") == "delivered") | (pl.col("status") == "shipped")
)
```

**Your turn:** count this selected population. Explain why it differs from delivered orders alone.

## 4. Summarize groups

```python
summary = (
    orders.group_by("status")
    .agg(pl.len().alias("order_count"))
    .sort(["order_count", "status"], descending=[True, False])
)
```

Read the chain as a pipeline: group the input, aggregate each group, then sort the result.

| SQL concept | Polars example |
| --- | --- |
| Select columns | `orders.select("order_id", "status")` |
| Filter rows | `orders.filter(pl.col("status") == "delivered")` |
| Group rows | `orders.group_by("status")` |
| Count all rows | `pl.len()` inside an aggregation |
| Count non-null column values | `pl.col("status").count()` |
| Name an expression | `.alias("order_count")` |
| Distinct combinations | `.select(...).unique()` |
| Sort | `.sort(...)` |

The output grain is one status, not one order. Compare every status count with Lesson
1's SQL result. If they differ, investigate input, eligibility, and null handling before
blaming a library.

## 5. Make an assumption executable

The script checks that the number of unique order identifiers equals the number of rows.
If it does not, it raises an exception.

You are moving an assumption out of your notes and into the workflow: it can now
stop when the expected grain is violated.

> **Interpretation limit — one passing check does not validate every property**
>
> Uniqueness alone does not establish valid or non-null keys. Match each check to
> the property you require. Later, you will also validate join relationships.

**Your turn:** add a check that the sum of the grouped counts equals `orders.height`.
Explain what kind of mistake this would detect and what it would not detect.

## 6. Know what is being executed

These examples use **eager** operations: `read_csv` loads selected columns and each
operation produces its result immediately. That keeps early experiments straightforward.

Polars also supports **lazy** query plans, often beginning with `scan_csv`, with
execution triggered by `collect()`. Lazy execution can allow projection and filter
optimizations, but it is not a guarantee that arbitrary datasets fit in memory. Do not
replace every call with a lazy equivalent without understanding the workflow.

For this small local dataset, eager execution is a teaching choice. The next lessons
will ask whether data should be loaded into Python at all.

Save your script and update the implementation section of your investigation record:

- Do all status counts agree with Lesson 1? Record any differences and their cause.
- Which Polars expressions perform the filtering, grouping, and counting?
- What does your added check establish, and what does it leave untested?

**What you can do now:** read selected file columns into a dataframe, express filters
and summaries without Python row loops, and compare the result with a known SQL
answer. You have another practical way to explore tabular inputs.

Continue to [Lesson 7](../lesson_7/README.md) to rebuild basket affinity using these
expressions.
