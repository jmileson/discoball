# Lesson 4: Same customer, different question

The merchandising team has another idea:

> Could we recommend categories based on what a customer has bought across their
> purchase history, rather than just one basket?

You can reuse much of your basket-affinity approach. But changing the unit of
observation changes the meaning of the result. A customer with ten orders must not count
as ten customers.

Allow about 60–90 minutes. Complete [Lesson 3](../lesson_3/README.md) first. Use the
same SQL session with the temporary views from Lessons 2 and 3 available. If you have
reconnected, rerun those view definitions in lesson order before continuing.

## 1. Define a customer history

Use these working rules:

- Recognize a customer using `customer_unique_id`.
- Include delivered orders across all available history, as in the basket analysis.
- Include customers with at least one usable category in those orders.
- Count each category once per customer, regardless of item or order count.
- Keep customers with one category in the denominator.

Your question is now:

> Which categories occur in the same customer's observed purchase history?

This does **not** require the categories to occur in different orders. A customer who
buys A and B in one order qualifies. It also does not tell you which category was
purchased first.

“All available history” is a period choice, not a complete lifetime history. Customers
first observed near the end of the dataset have less opportunity to make another
recorded purchase. Purchases outside this dataset are invisible.

## 2. Link orders to a stable customer identifier

`orders.customer_id` joins to `customers.customer_id`. The customer record then supplies
`customer_unique_id`, which can connect different orders for the same customer.

First check the lookup key:

```sql
SELECT
    customer_id
  , count(*) AS row_count
FROM
    customers
GROUP BY
    customer_id
HAVING
    count(*) > 1
;
```

You should get no rows. If you do, investigate before relying on the join.

Build a mapping for the eligible baskets you prepared in Lesson 2:

```sql
CREATE OR REPLACE TEMP VIEW customer_order_categories AS
SELECT
    c.customer_unique_id
  , b.order_id
  , b.category_name
FROM
    basket_categories AS b
        INNER JOIN orders AS o
            ON b.order_id = o.order_id
        INNER JOIN customers AS c
            ON o.customer_id =
               c.customer_id
WHERE
    c.customer_unique_id IS NOT NULL
;
```

The grain remains one row per order and category, now with a customer identifier
attached.

Check whether any eligible baskets were lost because they could not be mapped:

```sql
SELECT
    (
        SELECT count(DISTINCT order_id)
        FROM
            basket_categories
        )                              AS eligible_baskets
  , count(DISTINCT order_id)           AS mapped_baskets
  , count(DISTINCT customer_unique_id) AS eligible_customers
FROM
    customer_order_categories
;
```

If the basket counts differ, document and investigate the missing mappings. Comparisons
with the basket analysis need to acknowledge this population difference.

## 3. Check how much repeat-purchase evidence you have

```sql
WITH
    customer_history AS (
        SELECT
            customer_unique_id
          , count(DISTINCT order_id)      AS order_count
          , count(DISTINCT category_name) AS category_count
        FROM
            customer_order_categories
        GROUP BY
            customer_unique_id
        )
SELECT
    order_count
  , count(*)                                    AS customer_count
  , count(*) FILTER (WHERE category_count >= 2) AS customers_with_multiple_categories
FROM
    customer_history
GROUP BY
    order_count
ORDER BY
    order_count
;
```

`FILTER` applies a condition to one aggregate without removing rows from the other
aggregates in the query. Here, it counts multi-category customers alongside all
customers in each order-count group.

These order counts cover eligible orders with usable categories, not every order a
customer may ever have placed.

**Record:** how many customers have more than one eligible order? Does this dataset
provide much evidence about buying across visits, or is most of the observed activity a
single order?

If repeat purchasing is sparse, that limits what you can learn. It is not a reason to
pretend that same-basket purchases are later purchases.

## 4. Change the grain to customer and category

```sql
CREATE OR REPLACE TEMP VIEW customer_categories AS
SELECT DISTINCT
    customer_unique_id
  , category_name
FROM
    customer_order_categories
;
```

The grain is now **one row per customer and category**. Buying a category repeatedly no
longer creates repeated rows.

```sql
SELECT
    customer_unique_id
  , category_name
  , count(*) AS row_count
FROM
    customer_categories
GROUP BY
    customer_unique_id
  , category_name
HAVING
    count(*) > 1
;
```

You should get no rows.

**Pause:** what information did you intentionally remove? Could this view tell you how
often someone purchased a category, or when they did so?

## 5. Build customer-level pairs and measures

Use the same pairing pattern, but match on the customer identifier rather than the order
identifier:

```sql
CREATE OR REPLACE TEMP VIEW customer_pair_counts AS
SELECT
    a.category_name AS category_a
  , b.category_name AS category_b
  , count(*)        AS pair_customers
FROM
    customer_categories AS a
        INNER JOIN customer_categories AS b
            ON a.customer_unique_id = b.customer_unique_id
               AND a.category_name < b.category_name
GROUP BY
    a.category_name
  , b.category_name
;
```

Because `customer_categories` contains one row per customer-category combination, each
customer contributes at most once to each pair.

```sql
CREATE OR REPLACE TEMP VIEW customer_affinity AS
WITH
    category_counts AS (
        SELECT
            category_name
          , count(*) AS category_customers
        FROM
            customer_categories
        GROUP BY
            category_name
        )
  , population AS (
        SELECT
            count(DISTINCT customer_unique_id) AS
                eligible_customers
        FROM
            customer_categories
        )
  , counts AS (
        SELECT
            p.category_a
          , p.category_b
          , p.pair_customers
          , a.category_customers AS a_customers
          , b.category_customers AS b_customers
          , n.eligible_customers
        FROM
            customer_pair_counts AS p
                INNER JOIN category_counts AS a
                    ON p.category_a = a.category_name
                INNER JOIN category_counts AS b
                    ON p.category_b = b.category_name
                CROSS JOIN population AS n
        )
SELECT
    *
  , 1.0 * pair_customers / nullif(eligible_customers, 0)               AS support
  , 1.0 * pair_customers / nullif(a_customers, 0)                      AS confidence_a_to_b
  , 1.0 * pair_customers / nullif(b_customers, 0)                      AS confidence_b_to_a
  , (1.0 * pair_customers / nullif(a_customers, 0))
        / nullif(1.0 * b_customers / nullif(eligible_customers, 0), 0) AS lift
FROM
    counts
;
```

The formulas are familiar, but every count now represents **customers**, not baskets.
Confidence A → B means the fraction of A-buying customers who also bought B somewhere in
their observed history.

Check the count invariants:

```sql
SELECT *
FROM
    customer_affinity
WHERE
     pair_customers > a_customers
  OR pair_customers > b_customers
  OR a_customers > eligible_customers
  OR b_customers > eligible_customers
;
```

This should return no rows.

## 6. Compare the two analyses

```sql
SELECT
    c.category_a
  , c.category_b
  , b.pair_baskets
  , c.pair_customers
  , round(b.lift, 2) AS basket_lift
  , round(c.lift, 2) AS customer_lift
FROM
    customer_affinity AS c
        LEFT JOIN basket_affinity AS b
            ON c.category_a = b.category_a AND
               c.category_b = b.category_b
WHERE
    c.pair_customers >= 10
ORDER BY
    c.pair_customers DESC
  , c.category_a
  , c.category_b
LIMIT 20
;
```

The minimum of ten customers is an illustrative filter, not proof of reliability. Try
other thresholds and report how sensitive the results are.

A `NULL` basket value here means the pair was absent from the observed basket-pair
summary. It does not mean a calculation returned zero lift.

Do not directly subtract pair counts and call the difference “cross-order customers.” A
customer may contribute several baskets, one customer history, and both same-order and
cross-order purchases. The populations and units differ.

If the two analyses look similar, use your repeat-order profile to help explain why.
Similar results are not a failed exercise; they can reflect limited additional customer
history.

## 7. Ask a genuinely cross-order question

To require evidence across different orders, return to the view that still contains
order identifiers:

```sql
SELECT
    category_a
  , category_b
  , count(*) AS customers_with_cross_order_evidence
FROM
    cross_order_customers
GROUP BY
    category_a
  , category_b
ORDER BY
    customers_with_cross_order_evidence DESC
  , category_a
  , category_b
LIMIT 20
;
```

`<>` means “not equal.” `DISTINCT` ensures that several qualifying order combinations
for the same customer do not multiply that customer's contribution to the pair count.

This requires A and B to occur in different orders, but it still does **not** establish
a direction. A customer could also have bought both in the same order on another
occasion.

Answering “what do customers buy next?” requires another analysis: purchase timestamps,
a definition of the next eligible order, treatment of ties, and a follow-up window.
Sorting category names cannot establish purchase sequence. You should not use these
unordered pairs to claim that buying A predicts a later purchase of B.

## 8. Recommend an analytical path

Write a short response to the merchandising team. Include:

1. Whether their proposed use needs same-basket, customer-history, or sequential
evidence.
2. Your eligible population, observation period, and unit of analysis.
3. One candidate pair with counts and measures, if the evidence supports one.
4. How much repeat-purchase evidence is available.
5. What this dataset cannot establish, and what you would investigate next.

It is acceptable to conclude that the available history does not support a strong
repeat-purchase recommendation. A useful analysis can prevent an unsupported decision as
well as suggest an opportunity.

You have completed the lesson when you can explain why these are three different
statements:

- Categories A and B appeared in the same order.
- The same customer purchased A and B during the observed period.
- A customer purchased B after purchasing A.

The SQL patterns overlap. The questions, grains, and evidence requirements do not.

Before moving on, take the [side quest: From your query to a shared
workflow](platform_side_quest.md) to explore how your analysis could become a dependable
shared deliverable, and how to collaborate with data engineering.

A useful next step is to run a chosen analysis from Python with explicit period and
eligibility parameters, save the results, and make the checks repeatable. Automating the
query should preserve these definitions—not hide them.
