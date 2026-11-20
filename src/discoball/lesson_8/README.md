# Lesson 8: Choose where the work belongs

You now have two ways to calculate basket affinity. Should every future analysis use
Polars? Should everything stay in SQL?

Neither is a useful universal rule. You need to consider the data, the workload, the
supported platform, and who will maintain the result.

Allow about 60–90 minutes. Complete [Lesson 7](../lesson_7/README.md). You will run a
local comparison, then write a workload recommendation. You do not need MotherDuck
access.

## 1. Separate language from execution location

Python is a general-purpose language. Polars is a tabular processing library you can
call from Python. DuckDB executes SQL and can also be called from Python. MotherDuck
provides a platform built around DuckDB capabilities; actual execution and data movement
depend on the configuration and workload.

“Python versus SQL” and “local versus remote” are different decisions. A Python script
can send SQL to a database and retrieve only a small result. Writing Python does not
mean every source row must be loaded into a dataframe.

## 2. Reconcile the implementations

Open [affinity.sql](affinity.sql). It packages the earlier SQL transformations into one
statement using CTEs, so it does not depend on your DBeaver session.

Open [compare.py](compare.py), then run:

```powershell
uv run python -m discoball.lesson_8.compare
```

If the database is locked, disconnect DBeaver and close other processes using it, then
retry. The script opens the local database read-only. It never resets or reloads tables.

The script:

1. Reads saved SQL from a file.
2. Executes it through the DuckDB Python library.
3. Transfers only the category-pair summary to a Polars DataFrame.
4. Runs the CSV-based Polars workflow.
5. Aligns columns, sorts by the pair keys, and compares all rows.

Exact integer counts must agree; floating-point rates are compared with a small
tolerance. Count dtypes can differ between engines, so this exercise ignores dtype
differences while preserving column names and comparing values. A production output also
needs an explicit schema contract.

You should see a message confirming agreement across all observed category pairs. If the
comparison fails, investigate definitions, data versions, types, and coverage before
adjusting tolerances. The setup database does not automatically refresh when the CSVs
change.

This is a correctness comparison, not a benchmark. One run cannot establish which engine
is faster in general.

## 3. Notice the data movement

The SQL branch reads database tables and returns a small summary. The Polars branch
reads selected columns from CSV into the local Python process. Both are reasonable for
this local exercise.

The comparison uses `fetchall()` for the small summary to avoid adding an Arrow
dependency to the lesson. It would be a poor default for an unbounded raw-data extract:
it materializes Python rows before constructing the dataframe. At larger scale, discuss
supported transfers, batching, lazy execution, and whether the transfer is needed at
all.

**Your turn:** identify each place data crosses a boundary: file to engine, engine to
Python rows, and rows to dataframe. Which boundary would become a concern if the raw
input were hundreds of gigabytes?

## 4. Choose according to the work

| Need | Reasonable starting point | What to check |
| --- | --- | --- |
| Join and aggregate shared platform tables | SQL near the data | Supported execution path, permissions, resource implications |
| Explore a manageable local file | DuckDB or Polars | Team familiarity, types, memory, and reuse |
| Coordinate files, parameters, checks, and exports | Python | Clear errors, ownership, and reproducibility |
| Apply transformations already expressed clearly in SQL | Reuse the SQL | Avoid an unnecessary second implementation |
| Work with Python libraries or a specialized algorithm | Python with suitable libraries | Whether the necessary input can safely and efficiently be transferred |
| Publish a shared reusable definition | Approved platform asset | Grain, access, documentation, and lifecycle |

Polars is not only for small data, and SQL is not only for remote data. This table
suggests starting questions, not hard size cutoffs or performance guarantees.

Do not export a large shared table merely because a notebook is convenient. First ask
whether filtering and aggregation can happen where the data already lives. Equally, do
not force file handling or workbook presentation into an elaborate SQL-only solution.

## 5. Make a measured comparison, if performance matters

Before comparing runtimes, fix the question and population. Record input versions,
selected columns, output size, execution environment, and whether file reads or
transfers are included.

Repeat measurements and acknowledge caching. Avoid presenting the local CSV branch
versus the database branch as a controlled engine benchmark: the storage formats and
loading work differ.

A faster run that changes null handling or drops part of the population is not a
successful optimization.

## 6. Prepare for MotherDuck without inventing the platform

For a future shared-platform version, ask:

- Which databases and workspaces are approved for this task?
- Which data must remain remote, and what may be exported?
- Where does this query execute, and how can you verify that?
- How often will it run, and who else uses the same resources?
- Should the result remain a table/view, or be delivered as a file?
- Who owns shared definitions, recurring execution, and failures?

Use the platform team's documented access and execution patterns when available. This
lesson does not provide credentials, assume that all SQL runs remotely, or authorize
uploading local data.

Refer back to the [platform side quest](../lesson_4/platform_side_quest.md): an
evidence-based capability request is often more valuable than choosing a tool before
discussing the requirement.

## 7. Recommend an execution approach

Choose one scenario:

- A one-off analysis of three local CSVs.
- A weekly summary of large, access-controlled platform tables.
- A small Excel review pack generated from an approved summary.

Write a proposal identifying where data lives, where each transformation should run,
what crosses into Python, and who owns the output. Explain one alternative and why you
did not choose it. Mark unknown platform capabilities as questions, not assumptions.

You have completed this lesson when you can explain why a good analyst workflow may
combine SQL, Python, and Polars rather than select one winner.

Continue to [Lesson 9](../lesson_9/README.md) to deliver a workbook—and decide whether
it is the right deliverable.
