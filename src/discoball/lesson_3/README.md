# Lesson 3: Common together, or unusually associated?

In [Lesson 2](../lesson_2/README.md), you counted baskets containing pairs of
categories. Now the merchandising team asks:

> Are these categories meaningfully associated, or are they just popular?

The team needs a way to prioritise investigation. A frequently observed pair may
have reach; an unusually associated pair may reveal a relationship that raw popularity
hides. Those are different reasons to look more closely.

You will use the same eligible basket population to calculate support, confidence, and
lift. Your output is an evidence-based comparison of candidate pairs, added to the
investigation record from Lessons 1 and 2. You will explain what each measure helps
the team decide—not just produce another ranking.

As a working estimate, allow about 60–90 minutes, with a break after calculating
and checking the measures in section 4 if useful. Use the same DBeaver session as
Lesson 2. If you have
disconnected, rerun its four temporary view definitions in order: `basket_categories`,
`basket_pairs`, `basket_pair_counts`, and `basket_category_counts`. Do not change the
eligibility rules between those views.

Optional depth: [Nulls, denominators, and conditional aggregation](denominators_side_quest.md)
explores how missing values and filtering change a measure. It is not required
for progress through the main lesson.

## 1. Keep the denominator visible

Your population is **delivered orders with at least one usable category**. It includes
single-category baskets, even though they produce no pairs.

```sql
SELECT
    count(DISTINCT order_id) AS eligible_baskets
FROM basket_categories;
```

> **Watch out — the pair table is not the population**
>
> Calculate the denominator from `basket_categories`, not just baskets in
> `basket_pairs`. Dropping single-category baskets changes the question to association
> among multi-category orders only. It changes the baseline and can change the
> apparent strength of a relationship.

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

For the same population, lift is symmetric even though confidence is directional.

These measures let you ask three useful questions about the same pair:

| Measure | What it helps you understand |
| --- | --- |
| Support | How much of the eligible basket population contains this combination? |
| Confidence A → B | Among baskets containing A, how often is B also present? |
| Lift | Is that co-occurrence above or below the baseline from B's overall frequency? |

Support describes observed reach, not additional sales you could generate. Confidence
and lift describe relationships in the records, not the effect of a cross-sell offer.
Read all three alongside the underlying counts.

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
analytical pipeline. You have made part of your reasoning executable: the query can
now flag a result that contradicts the meaning of its counts.

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

> **Interpretation limit — a striking ratio can rest on little evidence**
>
> A very high lift based on two shared baskets is still only two observed shared
> baskets. Read `pair_baskets` alongside lift before prioritising a pair. Neither
> lift nor counts alone establish stability or commercial value.

In Lesson 2, only 723 eligible baskets contained multiple categories. You can now use
both the amount of evidence and the relative association to distinguish candidates,
rather than choosing whichever row tops a single ranking.

**Your turn:** compare two high-lift pairs with different shared-basket counts.
Which would you investigate first, and why? What would you still need to know
before recommending either pair?

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

> **Interpretation limit — a count cutoff is a screening choice**
>
> These cutoffs keep very small counts out of the candidate list. There is no
> universal minimum count that makes a pair dependable or useful for cross-selling.
> Record the cutoffs you use and compare the results at different values. Passing
> the filter means “retained for investigation,” not “validated recommendation.”

**Your turn:** compare minimum pair counts of 5, 10, and 20. Record how the candidate
list changes. If a filter leaves few or no results, report that rather than quietly
weakening the rule until you get an appealing answer.

> **Interpretation limit — absent pairs are not evaluated pairs**
>
> This table contains only observed pairs, not all possible combinations with zero
> shared baskets. It cannot serve as a complete survey of categories that avoid one
> another. Investigating those combinations would require explicitly including them.

## 6. Turn the comparison into a next step

Update the investigation record you used in Lesson 2. Keep the basket definition,
population, and coverage alongside these new measures so the comparison remains
understandable without the lesson open.

If the evidence permits, pick two candidates: one common pair and one higher-lift
pair that passes your chosen count filter. If too few qualify, report that limitation
rather than weakening the rule just to complete the exercise. For each candidate, record:

- Pair count and total eligible baskets.
- Support, both directional confidence values, and lift.
- Why it is worth investigating.
- What makes the evidence weak or incomplete.

Common categories can appear across many baskets without remarkable lift. A rare
pair can have remarkable lift without much observed reach. Choosing between them
requires knowing what the team wants to do, not just which measure is larger.

For each candidate—or for your conclusion that none merits prioritising yet—add:

```text
Information gained beyond the pair count:
Proposed next check and why it matters:
What result would change our view:
Decision the check would help the team make:
```

For example, a period-by-period check could reveal whether a candidate's shared
purchases recur or are concentrated in one short period. That would help decide
whether to take it forward for domain review or gather more observations first.
If the next step is a trial of a cross-sell offer, identify what outcome the team
wants to improve and what comparison would help evaluate the trial. You do not
need to design the experiment in this lesson.

This is the link to action: not declaring that a high-lift pair will increase sales,
but explaining which uncertainty to resolve next and what decision that enables.

You combined all available history. Category popularity, availability, promotions,
and customer mix can change over time. Recomputing for defined periods is one useful
next check; smaller periods will also have fewer observations. Choose a check that
addresses a specific uncertainty rather than adding analysis for its own sake.

You have completed this lesson when you can explain:

- Why every measure must use a consistent population.
- Why confidence has a direction but does not imply a sequence.
- Why pair count and lift should be read together.
- Why observed association is not proof of a successful intervention.

**What you can do now:** distinguish a frequently observed combination from an
unusually associated one, inspect the evidence behind either, and propose a next
check tied to a decision. You can explain why a candidate merits investigation
and which uncertainty the team should resolve next.

Continue to [Lesson 4](../lesson_4/README.md), where you will change the unit from an
order to a customer—and decide whether that evidence better fits what the team
wants to do.
