# Lesson 2: What counts as bought together?

A merchandising team asks you a question:

> Which product categories do customers buy together? We would like to explore
> cross-sell recommendations.

That sounds straightforward. But does “together” mean in one order, or across several
visits by the same customer? Those are different questions. In this lesson, you will
investigate categories bought in the **same order**.

The team could use this information to choose category combinations to investigate
for cross-selling. Before choosing any, they need to know which combinations occur
and how much evidence sits behind them. You will build that starting point—not an
automated recommendation service.

This is part of business intelligence: turning records into information that helps
someone decide what to do next. A report or dashboard could present the result, but
the analytical value comes from defining the question, producing new information,
and explaining how it can be used.

Allow about 60–90 minutes. Complete [Lesson 1](../lesson_1/README.md) first. Keep
DBeaver connected to your local database and run the queries below in order, in the same
SQL editor session.

By the end, you will have a category-pair summary and a clear explanation of what each
count represents. You will use SQL joins, common table expressions, and temporary views
along the way. Your output is a checked category-pair summary and an update to
the analytical note you started in Lesson 1. Keep that note as your investigation
record; later lessons will extend it rather than start a separate report each time.

Optional depth: [Grain, joins, and missing matches](joins_side_quest.md)
uses tiny examples to investigate row multiplication and population changes.
You can complete the main lesson without taking this side quest.

## 1. Define a basket before counting one

For this investigation, use these working definitions:

- A basket is one order whose status is `delivered`.
- Use all available order history. This is a historical exercise, not a current
  recommendation model.
- Investigate **categories**, rather than individual products.
- A category is present or absent in a basket. Three items from one category still count
  as one category occurrence.
- Exclude items without a usable category, but measure how many orders this leaves out.
- Keep single-category baskets in the population. They do not produce pairs, but they
  will matter when you calculate rates later.

Categories give you a manageable starting point. Individual products may have too few
shared purchases to support useful conclusions. You will still need to check how much
evidence the category analysis actually has.

**Write down:** what does “bought together” mean in this analysis? What business
question does this definition leave unanswered?

## 2. Connect orders to their items and products

You need three tables:

```text
orders --order_id--> order_items --product_id--> products
```

An order can have several item rows. Each item points to a product, which provides its
category.

Start with a preview:

```sql
SELECT
    o.order_id
  , i.order_item_id
  , i.product_id
  , p.category_name
FROM
    orders AS o
        INNER JOIN order_items AS i
            ON o.order_id = i.order_id
        LEFT JOIN products AS p
            ON
            i.product_id = p.product_id
WHERE
    o.status = 'delivered'
LIMIT 20
;
```

The short names `o`, `i`, and `p` are table aliases. They make it clear which table
supplies a column.

An `INNER JOIN` keeps matching records. A `LEFT JOIN` keeps every row on its left, even
when there is no matching product; the product columns are then `NULL`. That lets you
notice missing category information instead of silently losing those item rows.

The intended grain here is **one row per order item**, not one row per order. This
assumes the identifiers on the lookup side of each join are unique. Check that
assumption:

```sql
SELECT
    product_id
  , count(*) AS row_count
FROM
    products
GROUP BY
    product_id
HAVING
    count(*) > 1
;
```

You should get no rows. `HAVING` filters groups after aggregation.

> **Watch out — a lookup can multiply your rows**
>
> More than one product record per `product_id` can make an item appear several
> times after the join. If this check finds duplicates, investigate before continuing.
> Adding `DISTINCT` afterwards can hide the problem rather than resolve it.

## 3. Build one row per basket and category

You do not want repeated items from the same category to inflate a pair count. Prepare a
distinct set of order-category combinations:

```sql
CREATE OR REPLACE TEMP VIEW basket_categories AS
SELECT DISTINCT
    o.order_id
  , p.category_name
FROM
    orders AS o
        INNER JOIN order_items AS i
            ON o.order_id = i.order_id
        INNER JOIN products AS p
            ON i.product_id = p.product_id
WHERE
    o.status = 'delivered'
    AND p.category_name IS NOT NULL
    AND trim(p.category_name) <> ''
;
```

`DISTINCT` applies to the selected combination of columns. An order can still appear
several times, but each of its categories appears only once.

A **VIEW** names a query so you can reuse it. `TEMP` makes this view temporary: it
belongs to this database connection and disappears when the connection closes. You are
not changing the source tables. If DBeaver reconnects or reports that the view is
missing, rerun the view definitions in this lesson in the same editor session.

Check the new grain:

```sql
SELECT
    order_id
  , category_name
  , count(*) AS row_count
FROM
    basket_categories
GROUP BY
    order_id
  , category_name
HAVING
    count(*) > 1
;
```

This should return no rows. Now measure the population you kept:

```sql
SELECT
    (
        SELECT count(*)
        FROM
            orders
        WHERE
            status = 'delivered'
        )                          AS
                                      delivered_orders
  , count(DISTINCT order_id)       AS eligible_baskets
  , (
        SELECT count(*)
        FROM
            orders
        WHERE
            status = 'delivered'
        )
        - count(DISTINCT order_id) AS orders_without_usable_categories
FROM
    basket_categories
;
```

A subquery is a query inside another query. Here, each parenthesized query produces a
single count.

Your eligible basket population is now **delivered orders with at least one usable
category**.

> **Interpretation limit — retained baskets can still be incomplete**
>
> An order with some missing categories can remain in the population. The exclusion
> count measures completely unrepresented orders, not every order affected by missing
> information. Missing categories cannot contribute to observed pairs. Keep this
> distinction in your note when describing category coverage.

**Record:** the two population counts, the exclusion count, and how partially missing
categories could affect the result.

## 4. Check whether baskets can produce pairs

```sql
WITH
    basket_sizes AS (
        SELECT order_id, count(*) AS category_count
        FROM
            basket_categories
        GROUP BY
            order_id
        )
SELECT category_count, count(*) AS basket_count
FROM
    basket_sizes
GROUP BY
    category_count
ORDER BY
    category_count
;
```

`WITH` gives an intermediate query a name for this statement. This is a **common table
expression**, or CTE. Unlike a temporary view, it does not remain available for the next
statement.

An order with one category cannot produce a category pair, even if it contains many
items. Look at how many baskets have two or more categories before assuming this dataset
can support strong affinity conclusions.

**Checkpoint:** with the supplied data and these eligibility rules, expect 95,146
eligible baskets: 94,423 with one category, 708 with two, and 15 with three. Only
723 baskets—about 0.76%—can contribute category pairs. If your counts differ,
check the delivered-order filter and category deduplication before continuing.

You have already learned something useful for the team: under these definitions,
cross-category purchases within an order are uncommon. That helps set the scope of
the investigation before anyone treats the order count as evidence for cross-selling.

> **Interpretation limit — orders are not all evidence of category pairing**
>
> Only the 723 multi-category baskets can contribute pairs. Sparse pair counts are
> an expected feature of this exercise, not a sign that you failed to find the right
> query. Use the pair counts to decide which relationships merit further investigation;
> the size of the full order table alone cannot establish that.

**Your turn:** explain why counting items would give a different answer from counting
categories.

## 5. Make pairs without counting them twice

Imagine a basket containing categories A, B, and C. You want three pairs: A–B, A–C, and
B–C. You do not want A–A, and you do not want both A–B and B–A.

A **self-join** joins a dataset to itself. You give it two aliases, `a` and `b`, so
SQL can distinguish the row on the left from the row on the right. These are two
references to `basket_categories`, not two different source tables.

Imagine that `basket_categories` contains these rows for one order:

| order_id | category_name |
| --- | --- |
| order_1 | A |
| order_1 | B |
| order_1 | C |

If you join only on matching `order_id`, each of the three rows on the left matches
all three rows on the right. That produces nine combinations:

| Category from `a` | Matches from `b` |
| --- | --- |
| A | A, B, C |
| B | A, B, C |
| C | A, B, C |

You need a second condition to keep only one version of each useful pair. That is
what `a.category_name < b.category_name` does:

| Candidate pair | Keep it? | Why? |
| --- | --- | --- |
| A–A, B–B, C–C | No | A name is not less than itself. |
| A–B, A–C, B–C | Yes | The left name sorts before the right name. |
| B–A, C–A, C–B | No | These reverse pairs already kept in the previous row. |

Using `<>` (not equal) instead would remove self-pairs but keep both A–B and B–A.
Using `<` removes self-pairs **and** reversed duplicates. For actual category names,
DuckDB uses its text comparison rules; A, B, and C just make the example easy to see.

Now apply both conditions in the self-join:

```sql
CREATE OR REPLACE TEMP VIEW basket_pairs AS
SELECT
    a.order_id
  , a.category_name AS category_a
  , b.category_name AS category_b
FROM
    basket_categories AS a
        INNER JOIN basket_categories AS b
                ON a.order_id = b.order_id AND a.category_name < b.category_name
;
```

Read the `ON` conditions together:

- `a.order_id = b.order_id`: take both categories from the same basket, not from
  unrelated orders.
- `a.category_name < b.category_name`: keep one consistently ordered representation
  of each pair, with no category paired with itself.

> **Watch out — repeated items can inflate pair counts**
>
> The `<` condition removes self-pairs and reversed pairs; it does not remove repeated
> category occurrences in the input. The earlier deduplication makes repeated items
> contribute just one occurrence of each category per basket. Keep both steps.

The names `category_a` and `category_b` label the two output columns. They do **not**
mean that A was purchased before B, that A caused B, or that the pair has a direction.
We could have used `>` instead of `<` and kept the same relationships with their
column positions reversed.

The grain is now **one row per order and unordered category pair**. “Unordered” means
A–B represents the same relationship as B–A; we store only one version.

**Your turn:** a basket contains A, B, C, and D. List the pairs this join would keep.
Would buying a second item from category A add another pair? Explain using the grain
of `basket_categories`.

Check it:

```sql
SELECT
    order_id
  , category_a
  , category_b
  , count(*) AS row_count
FROM
    basket_pairs
GROUP BY
    order_id
  , category_a
  , category_b
HAVING
    count(*) > 1
;
```

You should get no rows. A basket with three categories contributes three different
pairs, so adding all pair counts together does not give the number of baskets.

## 6. Count shared baskets

```sql
CREATE OR REPLACE TEMP VIEW basket_pair_counts AS
SELECT
    category_a
  , category_b
  , count(*) AS pair_baskets
FROM
    basket_pairs
GROUP BY
    category_a
  , category_b
;
```

```sql
SELECT
    category_a
  , category_b
  , pair_baskets
FROM
    basket_pair_counts
ORDER BY
    pair_baskets DESC
  , category_a
  , category_b
LIMIT 20
;
```

The grain has changed again: **one row per category pair**. `pair_baskets` counts
eligible orders containing both categories.

Keep the original category names as analytical keys. If you want English display labels,
use `product_categories`, but first check whether it has one row per `category_name`.
Joining a non-unique translation table can multiply your results too. A missing
translation is not the same thing as a missing category.

Now calculate the individual category counts:

```sql
CREATE OR REPLACE TEMP VIEW basket_category_counts AS
SELECT
    category_name
  , count(*) AS category_baskets
FROM
    basket_categories
GROUP BY
    category_name
;
```

```sql
SELECT
    category_name
  , category_baskets
FROM
    basket_category_counts
ORDER BY
    category_baskets DESC
  , category_name
LIMIT 20
;
```

**Pause:** are categories in the top pairs also common individually? A common pair might
simply combine two popular categories. Shared-basket counts alone do not tell you
whether the relationship is unusual.

## 7. Turn your summary into a useful finding

You can now answer a question that individual order records did not answer directly:
which category combinations occur in the same delivered orders, and how often?
The checked summary is useful information even before it becomes a chart or workbook.

Extend your investigation record from Lesson 1. Choose one pair and record:

- Your definition of an eligible basket and the total eligible population.
- The number of baskets containing both categories.
- The number containing each category individually.
- The amount of missing category information you measured.
- What this pair suggests the team could investigate next, and why.
- One thing you would check before recommending the pair to customers.

> **Interpretation limit — observed purchases are not an intervention**
>
> These counts describe existing orders. They do not show that displaying one category
> will cause someone to purchase the other. If the team wants to try a cross-sell
> placement, its effect needs an evaluation suited to that use.

Write a short finding for the team, using your actual counts:

```text
Among [N] eligible baskets, [AB] contained both [A] and [B].
Individually, these categories appeared in [A count] and [B count] baskets.
This makes the pair worth investigating because [reason], or leaves too little
observed evidence to prioritise it because [reason].
Our next check is [specific check], which would help us decide [decision].
```

A common pair may simply combine popular categories. That gives you a concrete next
question: is the pair common because its categories are common, or do they occur
together unusually often?

You have completed the lesson when you can explain all three grains:

1. One row per order and category.
2. One row per order and category pair.
3. One row per category pair, summarized across orders.

**What you can do now:** turn item records into a checked basket-category dataset,
generate pairs without double-counting, and explain the population behind a finding.
These are reusable analytical skills, not just steps for this particular question.

Continue to [Lesson 3](../lesson_3/README.md) to distinguish common pairs from unusually
associated categories and give the team a better basis for prioritising investigation.
