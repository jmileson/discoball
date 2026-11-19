# Lesson 2: What counts as bought together?

A merchandising team asks you a question:

> Which product categories do customers buy together? We would like to explore
> cross-sell recommendations.

That sounds straightforward. But does “together” mean in one order, or across several
visits by the same customer? Those are different questions. In this lesson, you will
investigate categories bought in the **same order**.

Allow about 60–90 minutes. Complete [Lesson 1](../lesson_1/README.md) first. Keep
DBeaver connected to your local database and run the queries below in order, in the same
SQL editor session.

By the end, you will have a category-pair summary and a clear explanation of what each
count represents. You will use SQL joins, common table expressions, and temporary views
along the way.

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

You should get no rows. `HAVING` filters groups after aggregation. If duplicates appear,
stop and investigate rather than adding `DISTINCT` to hide a join problem.

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
category**. An order with some missing categories can remain in the population, but its
observed basket is incomplete. The exclusion count above measures completely
unrepresented orders, not every order affected by missing information.

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

A large order table does not automatically give you a large amount of evidence
about categories bought together. Sparse pair counts are an expected feature of
this exercise, not a sign that you failed to find the right query. You may conclude
that a pairing needs more evidence rather than recommending it.

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

The earlier deduplication matters too. Because `basket_categories` has only one row
per order and category, repeated items cannot create extra copies of the same pair.

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

## 7. Write a finding, not a sales promise

Choose one pair and record:

- Your definition of an eligible basket and the total eligible population.
- The number of baskets containing both categories.
- The number containing each category individually.
- The amount of missing category information you measured.
- One thing you would check before recommending the pair to customers.

Do not claim that displaying one category will cause someone to purchase the other. This
analysis describes observed orders; it is not an experiment.

You have completed the lesson when you can explain all three grains:

1. One row per order and category.
2. One row per order and category pair.
3. One row per category pair, summarized across orders.

Continue to [Lesson 3](../lesson_3/README.md) to distinguish common pairs from unusually
associated categories.
