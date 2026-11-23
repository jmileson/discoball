# Lesson 7: Rebuild basket affinity with Polars

Can you change tools without changing the answer?

You will rebuild the category-affinity workflow from Lessons 2 and 3 using Polars. The
goal is not to prove that one language is better. It is to preserve definitions,
understand the transformations, and check that the implementation answers the same
question.

Rebuilding gives you a second practical route from inputs to analytical information.
When a platform does not yet provide a needed analysis, you can prototype with
approved local data and still carry forward explicit definitions and checks. The
point is to gain an option, not to declare that every SQL query should be rewritten.

Your output is a checked Polars implementation and an explanation of how its steps
preserve the SQL analysis. In Lesson 8, you will compare every observed pair rather
than relying on a few matching preview rows.

Allow about 90 minutes. Complete [Lesson 6](../lesson_6/README.md), and keep Lessons 2
and 3 nearby. The complete implementation is in [affinity.py](affinity.py).

## 1. Write down the contract

Before running anything, restate the rules:

- One basket is one delivered order across all available history.
- Exclude items without a usable category; partial baskets may remain.
- Count each category only once per order.
- Keep single-category baskets in the population denominator.
- Store each unordered category pair once per basket.
- Calculate support, both confidences, and lift from the same population.

Use the definitions in your investigation record as the contract for the rebuild.
Keep them fixed so that differences reveal something about the implementation,
rather than silently becoming a different analysis.

Run:

```powershell
uv run python -m discoball.lesson_7.affinity
```

Expect 95,146 eligible baskets and a preview of category-pair measures. The workflow
does not depend on temporary views from your DBeaver session.

## 2. Load and normalize the inputs

Read `load_basket_categories()`. It selects only the identifiers, status, and category
needed from the three CSV files. It explicitly renames source columns to match the
lesson vocabulary.

The identifiers remain strings. You are comparing categories and counting combinations,
not doing UUID arithmetic. The next lesson will compare the results with the database
implementation, rather than assuming these input differences are harmless.

Read the join contracts:

```python
.join(items, on="order_id", how="inner", validate="1:m")
.join(products, on="product_id", how="inner", validate="m:1")
```

`1:m` requires unique order keys on the left. `m:1` requires unique product keys on the
right. These options turn lookup-key assumptions into explicit checks.

> **Watch out — join validation checks multiplicity, not coverage**
>
> A validated inner join can still discard unmatched records. Check retained
> populations as well as key relationships; `validate="m:1"` is not a promise that
> every item found a product. This distinction is the same as in SQL.

The filter removes null and blank categories. It checks stripped text for emptiness but
does not otherwise rename or merge category keys. Finally, `select(...).unique()`
creates one row per order-category combination.

**Your turn:** identify the line that prevents three items from the same category from
contributing three category occurrences. Explain why a join-validation option alone
cannot do this.

## 3. Generate the unordered pairs

In `calculate_affinity()`, the basket dataset is joined to itself on `order_id`, then
filtered:

```python
.filter(pl.col("category_a") < pl.col("category_b"))
```

This is the same canonical ordering used in SQL. It excludes self-pairs and reversed
duplicates. It does not establish purchase sequence.

> **Watch out — pair generation can expand the work substantially**
>
> The join creates candidate combinations before filtering them. Large baskets can
> create many combinations, even if the final summary is small. Profile basket sizes
> and execution behavior before reusing this pattern on a substantially larger workload.

After grouping, the output grain is one category pair, with `pair_baskets` counting
baskets containing both.

**Your turn:** trace a basket containing A, B, and C through the deduplication,
self-join, filter, and grouping. Where would duplication occur if the input grain were
wrong?

## 4. Attach denominators and calculate measures

The function counts baskets per category, attaches A and B counts using validated joins,
and adds the total eligible population as a literal column.

The first `with_columns` calculation step defines support and confidence. A later step
defines lift using the new confidence column. Splitting these steps makes the dependency
explicit.

> **Watch out — sibling expressions are not sequential assignments**
>
> Do not define a confidence column and then reference that new column in a sibling
> expression within the same `with_columns` call. Use a later call for the dependent
> calculation. A chain of calls makes the dependency explicit.

The denominators are positive for observed pairs from a non-empty valid basket
population. The function rejects an empty population and checks the resulting count
bounds. Unlike the defensive SQL formula, it does not introduce `NULLIF` into every
division because its input contract establishes those conditions.

**Your turn:** use one result row to calculate support, both confidence values, and lift
by hand. Compare with the unrounded result. The interpretation remains the one from
Lesson 3: these are measures of observed association, not effects of an intervention.

## 5. Test a small example you can understand completely

In a Python scratch script or interactive session, run:

```python
import polars as pl

from discoball.lesson_7.affinity import calculate_affinity

example = pl.DataFrame(
    {
        "order_id": ["1", "1", "2", "3"],
        "category_name": ["A", "B", "A", "B"],
    }
)
print(calculate_affinity(example))
```

There are three baskets, two containing A, two containing B, and one containing both.
Expect support of 1/3, both confidences of 1/2, and lift of 0.75.

Now deliberately supply a duplicate order-category row. The function should fail its
grain check. Remove the duplicate and try a population containing only single-category
baskets with no shared categories. An empty pair result is valid; an empty basket
population is rejected. Those are different conditions.

Small examples help you reason about correctness. They complement checks on real data;
they do not establish that all possible inputs work.

## 6. Reconcile before interpreting

Repeat Lesson 2's basket-size summary in Polars. Expect 94,423 baskets with one
category, 708 with two, and 15 with three. If that does not match, stop before comparing
affinity rankings.

Update the implementation section of your investigation record with:

- The three grains and the transformations that create them.
- Which assumptions each function checks.
- The result of the basket-size reconciliation and the small-example tests.
- Any differences from the SQL implementation that you still need to investigate.

The business interpretation has not changed: this remains a candidate list for
investigation. A second implementation gives you another way to produce it, not
additional purchase evidence.

**What you can do now:** rebuild a relational analysis with dataframe operations,
turn join and grain assumptions into checks, and test calculations against an example
you can reason through completely. Next you will test agreement across the full
observed pair result.

Continue to [Lesson 8](../lesson_8/README.md) to reconcile every pair with SQL and
choose where different parts of the workload belong.
