# Lesson 8: Choose where the work belongs

You now have two ways to calculate basket affinity. Should every future analysis use
Polars? Should everything stay in SQL?

Neither is a useful universal rule. You need to consider the data, the workload, the
supported platform, and who will maintain the result.

This is the payoff of the rebuild: you can check that two implementations preserve
the same answer, then choose how to do the work for a particular need. You will also
see a third combination—Python running saved SQL and handling the returned summary.
The tools can work together; you do not have to choose one language for everything.

Allow about 60–90 minutes. Complete [Lesson 7](../lesson_7/README.md). You will run a
local comparison, then add its findings and a workload recommendation to your
investigation record. You do not need MotherDuck access.

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

You should see a message confirming agreement across all observed category pairs.
That is stronger than matching a few rows from the top of each ranking: the comparison
checks the complete observed pair output, including its counts and rates.

If the comparison fails, investigate definitions, data versions, types, and coverage
before adjusting tolerances. The setup database does not automatically refresh when
CSVs change. Exact count differences need an explanation, not a floating-point allowance.

> **Interpretation limit — agreement is not independent business validation**
>
> Both implementations can agree while sharing an unsuitable definition or source
> limitation. Agreement supports implementation consistency for these inputs; it does
> not add purchase evidence or establish that a recommendation will work.

This is a result comparison, not a benchmark. You have not measured which engine is
faster in general.

## 3. Notice the data movement

The SQL branch reads database tables and returns a small summary. The Polars branch
reads selected columns from CSV into the local Python process. Both are reasonable for
this local exercise.

The comparison uses `fetchall()` for the small summary to avoid adding an Arrow
dependency to the lesson. It would be a poor default for an unbounded raw-data extract:
it materializes Python rows before constructing the dataframe. At larger scale, discuss
supported transfers, batching, lazy execution, and whether the transfer is needed at
all.

**What this enables:** Python can coordinate a workflow while the database performs
the joins and calculations. You can reuse SQL you trust and bring just its summary
into another tool for checks, further analysis, or presentation.

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

The course rebuilt the analysis to teach an alternative and test preservation of its
meaning. Maintaining two implementations indefinitely is a separate choice. For a real
deliverable, choose a supported approach that meets the need; keep a second version
only when its value justifies the extra maintenance.

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

Use the platform team's documented access and execution patterns when available.
These are questions for a future agreement, not capabilities this lesson supplies.
The lesson does not provide credentials, assume that all SQL runs remotely, or
authorize exporting restricted data or uploading local data.

Refer back to the [platform side quest](../lesson_4/platform_side_quest.md): an
evidence-based capability request is often more valuable than choosing a tool before
discussing the requirement.

## 7. Recommend an execution approach

Choose one scenario:

- A one-off analysis of three local CSVs.
- A weekly summary of large, access-controlled platform tables.
- A small Excel review pack generated from an approved summary.

Add your recommendation to the investigation record. Identify:

- The local comparison result and what it establishes.
- Where the scenario's data lives and where each transformation should run.
- What crosses into Python, and why that movement is needed.
- Which implementation you would reuse and who would own the output.
- One alternative and why you did not choose it.
- What can be demonstrated now and what needs a platform agreement.

For the platform scenario, this is a proposal, not a deployment exercise. Mark unknown
capabilities and ownership as questions rather than filling them in with assumptions.

You have completed this lesson when you can explain why a good analyst workflow may
combine SQL, Python, and Polars rather than select one winner.

**What you can do now:** compare complete analytical results, distinguish language
from execution location, and explain a tool choice in terms of the workload. You can
prototype outside a database or use Python to coordinate SQL without treating either
as the only way to work.

Continue to [Lesson 9](../lesson_9/README.md) to deliver the information in a workbook,
connect it to a proposed next action, and decide whether the workbook is the right
deliverable.
