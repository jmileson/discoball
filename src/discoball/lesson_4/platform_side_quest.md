# Lesson 4 side quest: From your query to a shared workflow

Your affinity analysis works in DBeaver. You have defined a population, prepared intermediate views, and checked your results.

Now a colleague asks:

> Can we use this every Monday? Other analysts would like to build on it too.

You are no longer being asked only for a query. You are being asked for something other people can rely on.

In this side quest, you will work out what that means, what you can manage yourself, and where to collaborate with data engineering. You do not need a MotherDuck account or any new software. Keep using the local database from the earlier lessons.

Allow about 45–60 minutes. Complete [Lesson 4](README.md) first. Your output will be a short workflow proposal, not a deployed pipeline.

## 1. Understand why you started locally

Local DuckDB gives you a realistic, low-risk place to practice. You can explore actual tables, test joins, and make analytical mistakes without modifying a shared production dataset.

The longer-term direction of this project is an analyst platform using MotherDuck, supported by data engineering practices. Moving there will not make your analytical definitions less important. It will make their consequences more widely shared.

A platform is more than a place to execute SQL. It includes shared data, access boundaries, supported ways to publish work, and people responsible for keeping those capabilities dependable.

Your role is not to become the engineer responsible for all of that. Your role is to understand what your analysis needs, use the supported capabilities deliberately, and communicate enough evidence for others to help.

**Pause:** if a colleague ran your affinity analysis without speaking to you, which assumptions might they miss?

## 2. Separate exploration from a dependable deliverable

Temporary views were a sensible choice for your investigation. They let you name intermediate steps without publishing permanent tables. There is no need to turn every experiment into a shared dataset.

But those views disappear when the connection closes. A colleague cannot depend on the state of your open DBeaver session.

Consider three stages:

| Stage | What you need | What you do not necessarily need yet |
| --- | --- | --- |
| Exploration | Queries, notes, checks, and freedom to revise definitions | Scheduling or a published dataset |
| Repeatable analysis | Saved definitions, explicit inputs and parameters, a known execution order | A centrally managed pipeline |
| Shared recurring deliverable | Reproducibility, access, ownership, freshness expectations, and a failure response | A new permanent table for every intermediate step |

These are not automatic promotion steps. A one-off investigation can remain one-off. A recurring report may be best served by a supported analyst workflow rather than a new engineering-owned pipeline.

**Your turn:** choose either basket affinity or customer affinity. Write down which stage it is in today and what would justify moving it to the next stage.

## 3. Make your dependencies visible

Start with the analysis you actually built. Do not describe an ideal workflow you have not implemented.

Record:

- The source tables and columns you use.
- The grain of each intermediate result and final output.
- The identifiers that must be unique for your joins to behave as intended.
- The order statuses, date coverage, and missing-value rules you chose.
- The checks that would reveal an unexpected change.
- The temporary views that must exist before later statements run.

For example:

> The basket analysis expects one product record per `product_id`. Duplicate product records could multiply item rows during the join. The prepared basket-category view must contain at most one row per order and category.

That is more useful than saying “the query needs clean data.” It identifies an expectation and its analytical consequence.

Now imagine the source data were updated every day. Ask:

- How recent would it need to be for a Monday report?
- Could recent orders still change status or receive late-arriving information?
- Should you recompute past periods when records change?
- How would you distinguish “no qualifying pairs” from “the input did not arrive”?

The supplied Olist database is a historical snapshot, not a daily feed. These questions prepare you to discuss a future workload; do not claim that the local setup provides freshness monitoring or scheduled updates.

## 4. Report an observation before diagnosing a cause

Suppose category coverage limits your analysis. “The products table is broken” is not yet a useful diagnosis. A missing category might be an accepted source limitation, a mapping gap, a delayed update, or a mistake in your own query.

You can gather evidence without changing the source tables:

```sql
SELECT
    COUNT(*) AS delivered_item_rows,
    COUNT(*) FILTER (WHERE p.product_id IS NULL)
        AS item_rows_without_product_match,
    COUNT(*) FILTER (
        WHERE p.product_id IS NOT NULL
          AND (p.category_name IS NULL OR TRIM(p.category_name) = '')
    ) AS matched_item_rows_without_category
FROM orders AS o
INNER JOIN order_items AS i
    ON o.order_id = i.order_id
LEFT JOIN products AS p
    ON i.product_id = p.product_id
WHERE o.status = 'delivered';
```

This query needs only the source tables, not your temporary views. As in Lesson 2, it assumes the product lookup key is unique; verify that assumption before interpreting the counts.

The denominator here is **delivered-order item rows**, not orders or customers. A missing product match and a matched product without a category are different observations. The query deliberately reports them separately.

Record the values you actually find. A zero count is a valid result. Do not manufacture a defect to complete the exercise.

Prepare a short report:

```text
Question or deliverable affected:

Observation date and database/dataset used:

Expected behavior, or the expectation we need to clarify:

Observed behavior:

Reproduction query and counts, including the denominator:

Analytical impact:

Current workaround and its limitations:

Question for the data owner or platform team:
```

For this analysis, an impact might be that excluded items cannot contribute to category pairs, leaving some observed baskets incomplete. That does not establish why the category is missing or whether its absence biases a particular pair.

Share queries, aggregate evidence, and only the example identifiers needed through approved channels. On a real platform, do not paste customer records or export sensitive data into a ticket just because it is convenient.

**Your turn:** write an evidence-based report using your result. If you find no missing categories, describe what the check supports and what it does not test.

## 5. Request a capability, not just a table

A defect report asks whether something is behaving as intended. A capability request asks for a better way to do useful work. Keep the two distinct.

Imagine three analysts have independently defined eligible baskets. Their reports disagree because one includes canceled orders and another drops all single-category orders.

A useful request starts with the problem:

> We need a consistent basis for category-affinity analysis. Several analysts maintain separate basket definitions, which makes results difficult to compare.

Bring a proposed definition, but leave room to agree on the solution. A shared view, an existing curated dataset, documentation, or a supported reusable query might solve the need. A new physical table is not automatically the answer.

Describe:

- **Use case:** the decision or deliverable this supports.
- **Consumers:** who will use it and how often.
- **Grain:** what one output row should represent.
- **Definitions:** eligibility, dates, missing values, and category identity.
- **Inputs and history:** the fields and coverage needed.
- **Service expectations:** how fresh it must be and when it must be available.
- **Workload:** approximate data size, execution frequency, runtime observed, and any known bottleneck.
- **Access:** who should read or publish the result.
- **Acceptance checks:** how you would confirm that the solution works.
- **Ownership:** who answers definition questions and who operates any recurring execution.

If you do not know a requirement, mark it as an open question. Do not invent a freshness target or runtime measurement to make the request look complete.

Business definitions may need agreement from a domain owner. Engineering should not have to choose the meaning of “customer” or “sales” merely because those definitions appear in SQL.

## 6. Agree on responsibilities

Responsibilities vary between teams. Use this as a starting point for a conversation, not a universal organizational chart:

| Area | A useful starting responsibility |
| --- | --- |
| Analytical question and interpretation | Analyst, with the relevant business owner |
| Business definitions | Agreed with domain owners and documented by the people using them |
| Exploratory queries and local checks | Analyst |
| Reliable ingestion and shared infrastructure | Data engineering or platform team |
| Supported access and publishing mechanisms | Platform team, with security and governance requirements |
| Validation for the intended analytical use | Analyst, collaborating with the data owner and engineering |
| Recurring execution and failure response | Explicitly assigned before anyone depends on the output |
| Changes to shared definitions | Coordinated among owners and consumers |

You do not stop owning the meaning of an analysis when someone else implements its shared inputs. Equally, a platform team should provide understandable supported paths rather than expect you to reverse-engineer infrastructure.

For the Monday report, ask directly:

> If the inputs are late or a check fails, who notices, who investigates, and what do readers see?

An empty output should not silently become a business conclusion when the workflow actually failed.

## 7. Prepare for shared-platform usage

You will learn the actual MotherDuck connection and workspace conventions when they are provided. Do not guess database names, permissions, or publication paths from this local exercise.

Some habits transfer now:

| In your local project | In a shared analyst platform |
| --- | --- |
| Check which database file you opened | Check the database, schema, and execution context |
| Know that temporary views belong to a session | Distinguish session-local objects from published assets |
| Keep experiments separate from source data | Use the approved personal or team workspace |
| Understand the joins before running them | Consider workload size, execution location, and resource implications |
| Keep data and credentials out of Git | Use approved access mechanisms and data-handling practices |
| Save the query that produced a finding | Make shared outputs reproducible, discoverable, and owned |

With local DuckDB and MotherDuck, you will also need to understand which data is local or remote, where computation runs, and whether a workflow moves data between environments. Do not assume that every query runs entirely on your laptop or entirely in the cloud. Follow the platform's documented configuration and verify the execution behavior using its supported tools.

Before turning an exploration into a scheduled workload, discuss expected frequency, scale, output size, and concurrency. Repeatedly rebuilding an expensive intermediate result may justify a shared materialization. It may also have a simpler solution. Bring measurements and the intended use rather than treating either a long query or a new table as inherently wrong.

## 8. Validate the solution together

Suppose engineering provides a shared basket-category dataset. Your work is not finished when the dataset appears.

Compare it with your exploratory result for the same fixed period and eligibility rules. Check:

- There is at most one row per eligible order and category.
- Population counts reconcile, or differences are explained.
- Missing-category treatment matches the agreed definition.
- Pair counts agree where the inputs and rules are the same.
- Documentation describes the actual behavior.
- The intended users can access it through the approved path.

Do not expect identical numbers if the shared dataset intentionally corrects a limitation in your prototype. Explain the difference and update the definition or tests accordingly.

A useful acceptance criterion is:

> The dataset contains at most one row per eligible order and category, and its documentation identifies the eligibility rules, missing-category treatment, coverage, and owner.

For a recurring deliverable, add agreed freshness and failure-handling criteria. “The numbers look right” is not enough to establish that it will remain dependable.

## 9. Write a workflow proposal

Use your chosen affinity analysis to prepare a short note:

```text
Decision or deliverable supported:

Current stage: exploratory, repeatable, or shared recurring work:

Users and expected frequency:

Population, observation period, and output grain:

Inputs and execution dependencies:

Checks and known limitations:

What can remain analyst-managed:

Platform support requested and why:

Proposed owners and open responsibility questions:

How we would validate the solution:

What should happen if inputs are late or checks fail:
```

Keep the proposal proportional to the work. You are making the need understandable, not designing an entire platform or promising an operational service by yourself.

You have completed this side quest when you can:

- Explain why a working session is not the same as a shared deliverable.
- Distinguish a data observation, a suspected cause, and a capability request.
- Give engineering a reproducible example and its analytical impact.
- Identify what you own and what needs an explicit agreement.
- Describe how you would validate a shared solution.

You are not handing your analysis away. You are making its needs explicit so it can work reliably within a larger system.
