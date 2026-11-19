# Lesson 3: Common together, or unusually associated?

In [Lesson 2](../lesson_2/README.md), you counted baskets containing pairs of
categories. Now the merchandising team asks:

> Are these categories meaningfully associated, or are they just popular?

You will use the same eligible basket population to calculate support, confidence, and
lift. Each measure answers a different question. None proves that a recommendation will
increase sales.

Allow about 60 minutes. Use the same DBeaver session as Lesson 2. If you have
disconnected, rerun its four temporary view definitions in order: `basket_categories`,
`basket_pairs`, `basket_pair_counts`, and `basket_category_counts`. Do not change the
eligibility rules between those views.

## 1. Keep the denominator visible

Your population is **delivered orders with at least one usable category**. It includes
single-category baskets, even though they produce no pairs.

```sql
SELECT
    count(DISTINCT order_id) AS eligible_baskets
FROM basket_categories;
```

Removing single-category baskets would answer a different question: association among
multi-category orders only. That changes the baseline and can change the apparent
strength of a relationship.

For a pair A–B, you need four counts from this same population:

- **N:** all eligible baskets.
- **A:** baskets containing category A.
- **B:** baskets containing category B.
- **AB:** baskets containing both.

## 2. Understand the measures with small numbers

Imagine 100 eligible baskets. Twenty contain A, ten contain B, and four contain both.

### Support: how widespread is the pair?

```text
support(A, B) = AB / N = 4 / 100 = 0.04
```

Four percent of eligible baskets contain both categories. Support is symmetric: A–B and
B–A have the same support.

### Confidence: how often does B appear when A appears?

```text
confidence(A → B) = AB / A = 4 / 20 = 0.20
confidence(B → A) = AB / B = 4 / 10 = 0.40
```

The direction matters. Twenty percent of A baskets contain B, while forty percent of B
baskets contain A.

The arrow describes a conditional calculation, **not** purchase order or causation.

### Lift: how does that compare with B's overall frequency?

```text
lift(A, B) = confidence(A → B) / (B / N) = 0.20 / 0.10 = 2.0
```

In this example, B occurs twice as often among A baskets as it does in the eligible
population overall.

- Lift above 1 indicates co-occurrence above the independence baseline.
- Lift near 1 indicates co-occurrence near that baseline.
- Lift below 1 indicates co-occurrence below that baseline.

For the same population, lift is symmetric even though confidence is directional. A high
lift based on very few observations is not automatically reliable.

## 3. Assemble counts before calculating rates

```sql
CREATE OR REPLACE TEMP VIEW basket_affinity_counts AS
WITH
    population AS (
        SELECT
            count(DISTINCT order_id) AS eligible_baskets
        FROM
            basket_categories
        )
SELECT
    p.category_a
  , p.category_b
  , p.pair_baskets
  , a.category_baskets AS a_baskets
  , b.category_baskets AS b_baskets
  , n.eligible_baskets
FROM
    basket_pair_counts AS p
        INNER JOIN basket_category_counts AS a
            ON p.category_a = a.category_name
        INNER JOIN basket_category_counts AS b
            ON p.category_b = b.category_name
        CROSS JOIN population AS n
;
```

A `CROSS JOIN` combines every row on one side with every row on the other. Here,
`population` has exactly one row, so it adds the same denominator to each pair without
multiplying the number of pair rows.

Check the counts before trusting any rates:

```sql
SELECT *
FROM
    basket_affinity_counts
WHERE
     pair_baskets > a_baskets
  OR pair_baskets > b_baskets
  OR a_baskets > eligible_baskets
  OR b_baskets > eligible_baskets
;
```

You should get no rows. A pair cannot appear in more baskets than either of its
component categories. This kind of invariant is a useful check when you change an
analytical pipeline.

## 4. Calculate the measures

```sql
CREATE OR REPLACE TEMP VIEW basket_affinity AS
SELECT
    *
  , 1.0 * pair_baskets / nullif(eligible_baskets, 0)              AS support
  , 1.0 * pair_baskets / nullif(a_baskets, 0)                     AS confidence_a_to_b
  , 1.0 * pair_baskets / nullif(b_baskets, 0)                     AS confidence_b_to_a
  , (1.0 * pair_baskets / nullif(a_baskets, 0))
     / nullif(1.0 * b_baskets / nullif(eligible_baskets, 0), 0)   AS lift
FROM
    basket_affinity_counts
;
```

`NULLIF(value, 0)` returns `NULL` when a denominator is zero, avoiding a misleading
division result. Multiplying by `1.0` makes the intention to calculate a fractional rate
explicit.

These are proportions, not percentages: support of `0.04` means 4%. Keep full precision
for calculation; round only when presenting results.

```sql
SELECT
    category_a
  , category_b
  , pair_baskets
  , a_baskets
  , b_baskets
  , round(100 * support, 3)           AS support_pct
  , round(100 * confidence_a_to_b, 2) AS confidence_a_to_b_pct
  , round(100 * confidence_b_to_a, 2) AS confidence_b_to_a_pct
  , round(lift, 2)                    AS lift
FROM
    basket_affinity
ORDER BY
    pair_baskets DESC
  , category_a
  , category_b
LIMIT 20
;
```

**Your turn:** choose one row and calculate:

    - Of the baskets containing category A, what percentage also contain B?
    - Of the baskets containing category B, what percentage also contain A?

Use `pair_baskets`, `a_baskets`, and `b_baskets`, then compare your answers with the
displayed confidence percentages. Small differences may come from rounding.

Identify the denominator in each calculation. Why can the percentages differ even
though they use the same shared-basket count? Do either of these calculations tell 
you which category was purchased first?

## 5. Look for fragile results

Sort by lift alone:

```sql
SELECT
    category_a
  , category_b
  , pair_baskets
  , a_baskets
  , b_baskets
  , lift
FROM
    basket_affinity
ORDER BY
    lift         DESC
  , pair_baskets DESC
  , category_a
  , category_b
LIMIT 20
;
```

How many shared baskets support the highest values? Would you present the same
recommendation if the pair occurred twice rather than two hundred times?

Now apply an illustrative evidence filter:

```sql
SELECT
    category_a
  , category_b
  , pair_baskets
  , support
  , confidence_a_to_b
  , confidence_b_to_a
  , lift
FROM
    basket_affinity
WHERE
      pair_baskets >= 10
  AND a_baskets >= 50
  AND b_baskets >= 50
ORDER BY
    lift         DESC
  , pair_baskets DESC
  , category_a
  , category_b
LIMIT 20
;
```

These thresholds are exercise choices, not statistical guarantees or universal business
rules. They screen out some very small counts; they do not establish significance,
stability, or commercial value.

**Your turn:** compare minimum pair counts of 5, 10, and 20. Record how the candidate
list changes. If a filter leaves few or no results, report that rather than quietly
weakening the rule until you get an appealing answer.

Your pair table contains only observed pairs. It does not list all possible category
combinations with zero shared baskets. Do not describe it as a complete survey of
categories that avoid one another.

## 6. Choose what to investigate next

Pick two candidates: one common pair and one higher-lift pair that passes your chosen
count filter. For each, record:

- Pair count and total eligible baskets.
- Support, both directional confidence values, and lift.
- Why it is worth investigating.
- What makes the evidence weak or incomplete.

Common categories can have substantial commercial reach without remarkable lift. A rare
pair can have remarkable lift without much reach. Neither ranking is automatically the
right answer.

You also combined all available history. Category popularity, availability, promotions,
and customer mix can change over time. A next check would be to recompute the analysis
for defined time periods and see whether the relationship persists. A recommendation
would ultimately need an evaluation suited to its intended use, not just an attractive
historical ratio.

You have completed this lesson when you can explain:

- Why every measure must use a consistent population.
- Why confidence has a direction but does not imply a sequence.
- Why pair count and lift should be read together.
- Why observed association is not proof of a successful intervention.

Continue to [Lesson 4](../lesson_4/README.md), where you will change the unit from an
order to a customer—and see why that changes the question.
