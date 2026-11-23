# Lesson 4: Same customer, different question

The merchandising team has another idea:

> Could we recommend categories based on what a customer has bought across their
> purchase history, rather than just one basket?

You can reuse much of your basket-affinity approach. But changing the unit of
observation changes the meaning of the result. A customer with ten orders must not count
as ten customers.

The practical question is which evidence fits what the team wants to do. Exploring
categories to display together, targeting customers from their histories, and asking
what people buy next are related ideas, but they need different analyses. You will
compare those questions and extend your investigation record with a recommended
analytical path.

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

> **Interpretation limit — observed history is not a lifetime history**
>
> Customers first observed near the end of the dataset have less opportunity to
> make another recorded purchase. Purchases outside this dataset are invisible.
> Keep the observation period alongside customer-history findings; “all available
> history” does not give every customer an equal follow-up period.

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

**Checkpoint:** with the supplied data and these eligibility rules, you should have
92,098 eligible customers, of whom 2,742 have more than one eligible order—about 3%.
Sum `customer_count` across all rows for the population, then across rows where
`order_count > 1` for the repeat-order count. If your counts differ, check the
eligibility rules and customer mapping before interpreting the difference.

You can now tell the team how much observed history is available for their new idea.
Most customers have only one eligible order, so changing to customer history may
add relatively little evidence beyond basket affinity. That is useful when deciding
whether to pursue a cross-visit investigation with this snapshot.

> **Interpretation limit — one observed order does not mean no repeat purchasing**
>
> This profile describes eligible orders in this dataset. It does not establish that
> these customers never bought again or elsewhere. Use it to describe the evidence
> available here, not to label customers as people who never return.

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

As in Lesson 3, the minimum of ten customers is a screening choice: passing it means
retained for investigation, not validated. Try other cutoffs and record how the
candidate list changes.

A `NULL` basket value here means the pair was absent from the observed basket-pair
summary. It does not mean a calculation returned zero lift.

> **Watch out — subtracting different units does not isolate cross-order purchases**
>
> Do not subtract pair counts and call the difference “cross-order customers.” One
> customer may contribute several baskets, one customer history, and both same-order
> and cross-order purchases. To count cross-order evidence, keep the order identifiers
> and test for different orders explicitly, as in the next section.

If the two analyses look similar, use your repeat-order profile to help explain why.
Similar results are not a failed exercise; they can reflect limited additional customer
history.

## 7. Ask a genuinely cross-order question

To require evidence across different orders, return to the view that still contains
order identifiers:

```sql
WITH cross_order_customers AS (
    SELECT DISTINCT
        a.customer_unique_id
      , a.category_name AS category_a
      , b.category_name AS category_b
    FROM customer_order_categories AS a
    INNER JOIN customer_order_categories AS b
        ON a.customer_unique_id = b.customer_unique_id
       AND a.order_id <> b.order_id
       AND a.category_name < b.category_name
)
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

> **Interpretation limit — different orders do not establish a direction**
>
> Answering “what do customers buy next?” requires purchase timestamps, a definition
> of the next eligible order, treatment of ties, and a follow-up window. Sorting
> category names cannot establish purchase sequence. These unordered pairs do not
> show that buying A predicts a later purchase of B.

You have separated three questions that can otherwise sound interchangeable. That
lets you discuss the team's intended use before investing in a more complex analysis:

| Proposed use to investigate | Relevant starting evidence |
| --- | --- |
| Categories to display together in a basket context | Same-basket co-occurrence |
| Category suggestions informed by customer history | Customer-history relationships, with explicit checks for cross-order evidence if that is the intended basis |
| Suggestions about a later purchase | A sequential analysis with defined timing and follow-up |

These are starting points for investigation, not proof that a placement or suggestion
will work. Testing an action is a separate step from describing past purchases.

## 8. Recommend an analytical path

Use your evolving investigation record to write a short response to the merchandising
team. Include:

1. Whether their proposed use needs same-basket, customer-history, or sequential
evidence.
2. Your eligible population, observation period, and unit of analysis.
3. One candidate pair with counts and measures, if the evidence supports one.
4. How much repeat-purchase evidence is available.
5. What this dataset cannot establish.
6. A specific next check or action, what you would learn from it, and which decision
that would help the team make.

For example, you might recommend clarifying whether the intended suggestion is for
this basket or a later visit, checking a candidate across defined periods, or asking
whether more follow-up history is available. Choose the step that addresses the
uncertainty you actually found.

It is acceptable to conclude that the available history does not support prioritising
a repeat-purchase recommendation yet. Make that useful by identifying what evidence
would change the conclusion and how the team could obtain or evaluate it.

You have completed the lesson when you can explain why these are three different
statements:

- Categories A and B appeared in the same order.
- The same customer purchased A and B during the observed period.
- A customer purchased B after purchasing A.

The SQL patterns overlap. The questions, grains, and evidence requirements do not.

**What you can do now:** adapt an analysis to a different unit of observation,
measure how much evidence the change adds, and explain which question fits an
intended use. You are helping the team choose an analytical path, not simply
producing another version of the same report.

For optional discussion, take the [side quest: From your query to a shared
workflow](platform_side_quest.md). It explores how to describe a dependable shared
deliverable and collaborate with data engineering. It does not require or assume
that the future platform's capabilities and responsibilities have been settled.

Continue to [Lesson 5: Your first analyst workflow in Python](../lesson_5/README.md).
You will learn Python and Polars, reproduce the basket analysis, compare execution
approaches, and deliver an Excel review pack. Rebuilding is deliberate: with a familiar
question and known results, you can focus on learning another tool and check that it
preserves your definitions. You gain another option for exploration and prototyping,
not a requirement to replace SQL.
