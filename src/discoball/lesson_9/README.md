# Lesson 9: Deliver an analysis—not just a spreadsheet

A merchandising colleague wants to review category pairs in Excel, filter the list, and
discuss candidates in a meeting.

You can build that workbook. But before you do, ask what decision it supports and
whether a file is the right delivery method. Automating an output does not automatically
make it useful.

Allow about 60–90 minutes. Complete [Lesson 8](../lesson_8/README.md). You will generate
a local review pack, inspect it, and recommend whether to keep this delivery approach.
You need Excel or a compatible workbook viewer for the inspection step; rendering can
vary between applications.

## 1. Define the deliverable

For this exercise, the audience needs a **historical candidate review**, not a live
sales dashboard or an automated recommendation service.

Write down:

- Who will use it and what decision they are considering.
- Whether they need a snapshot or current data.
- What definitions and limitations must travel with the numbers.
- Whether the data may be exported to the intended location.

The Olist inputs do not provide margins, recommendation exposure, implementation costs,
or experimental effects. Do not label affinity measures as expected profit.

## 2. Install the recorded dependency and run

The project now records `xlsxwriter`, used by Polars for Excel output. Sync the project
environment rather than installing an unrecorded package with pip:

```powershell
uv sync
uv run python -m discoball.lesson_9.report
```

Open [report.py](report.py) to inspect the workflow. It reuses Lesson 7's functions
rather than implementing the calculations again.

The output is `.data/lesson_9/affinity_review.xlsx`, under the ignored local data
directory. Each run replaces that file. Close it in Excel before rerunning; an open
workbook can prevent replacement, especially on Windows. This simple exercise is not a
concurrent, versioned, or failure-safe publishing service.

## 3. Inspect the workbook as a reader

The workbook contains:

| Sheet | Purpose |
| --- | --- |
| Read me | Audience context, population, grain, thresholds, limitations, and ownership status |
| Run summary | Generation time, counts, and checks performed |
| Candidate pairs | Pairs passing the illustrative evidence thresholds |
| Category summary | Individual category frequencies |

The script uses Excel tables with filters, readable widths, frozen headers, and number
formats. Confidence and support remain numeric proportions, displayed as percentages.
Converting `0.04` to the string `"4%"` would make later numerical use less reliable.

If no pairs pass the thresholds, the candidate sheet explicitly says so. That is
different from a failed run. The script raises errors for invalid input assumptions
rather than disguising them as an empty report.

The candidate list uses original category keys. They are stable analytical identifiers,
but not necessarily the best reader-facing labels. If you add English translations,
check translation-key uniqueness and retain a fallback for missing labels. A
presentation join must not change the pair counts.

**Your turn:** choose one candidate and check its counts and percentages against the
Python result. Try filtering the Excel table. Can you still find the definitions without
the lesson open?

## 4. Understand presentation versus calculation

Analytical calculations remain in the reusable Polars workflow. The workbook presents
the result; it does not recreate the analysis in another set of formulas.

The export disables automatic interpretation of strings as formulas or URLs. This is a
useful safeguard when displaying source text; file delivery should not unexpectedly turn
data into executable spreadsheet content.

Comments or annotations entered by your colleague do not flow back into the database or
Python code. Decide explicitly how review decisions will be recorded and reconciled if
the workflow becomes ongoing.

A generation timestamp says when the file was written, not when the underlying data
became fresh. This workbook uses all available historical data. It should never be
presented as “today's customer behavior.”

## 5. Validate the artifact, not just the script

Before sharing a workbook, check:

- The exported candidate count agrees with the run summary and Python result.
- The population and thresholds are visible.
- Percentages and counts have appropriate formats.
- Category identifiers remain intact.
- Filters and headers are usable in the reader's application.
- There are no unexpected formulas, links, or unnecessary sensitive records.
- The limitations and ownership status are clear.

Do not treat “the file exists” as a complete validation. This exercise's checks are
intentionally modest. A recurring business deliverable needs agreed acceptance checks
and a dependable publishing process.

Excel also has worksheet size limits: 1,048,576 rows including headers and 16,384
columns. Practical usability can deteriorate well before those limits. Exporting every
raw item is neither necessary for this review nor automatically a good idea.

## 6. Change the request and reconsider the tool

Your colleague now asks:

> Could this update every morning, show trends, and be available to several teams?

Do not immediately add a scheduler to the workbook script. Revisit the requirement and
find out which tools your organization actually supports.

| Need | Possible delivery method | Questions to ask |
| --- | --- | --- |
| One-off review and annotations | Excel | How will versions and feedback be managed? |
| Recurring interactive monitoring | Supported BI/dashboard tool | Who owns refresh, metrics, and access? |
| Reusable analytical input | Governed table or view | What is its grain, owner, and change policy? |
| Machine-readable handoff | Parquet or CSV | Does the recipient need types and metadata preserved? |
| A decision with a few supporting numbers | Written brief or presentation | Is a large table distracting from the conclusion? |
| Reproduction by another analyst | Saved SQL and a workflow | Are dependencies and execution instructions clear? |

These are options to investigate, not guarantees that each is provided on the platform.
An existing approved report may already answer the request. Ask before creating another
copy of the same metric.

Excel is not inherently wrong, and a dashboard is not inherently better. A dashboard can
be excessive for a one-off decision; emailed workbooks can be a poor substitute for
access-controlled operational monitoring.

## 7. Decide whether to build, reuse, change, or stop

An analyst-built export can fit a bounded request with a clear audience, manageable
data, and proportionate maintenance. Reconsider it when it becomes business-critical,
duplicates governed definitions, distributes restricted data, or has no owner for
recurring failures.

Do not assume that moving this script to MotherDuck solves delivery, permissions, or
operational ownership. Those need explicit design and agreement.

Write a short delivery recommendation:

```text
Audience and decision:
Why this output format fits—or does not:
Snapshot versus recurring need:
Available alternatives to investigate:
Data-handling and access considerations:
Validation performed and limitations:
Who would own updates and failures:
Recommendation: keep, reuse another tool, redesign, or stop:
```

Submit the workbook and this note. It is acceptable to recommend that the workbook
remain a one-off prototype or that there is insufficient evidence to justify a recurring
report.

You have now taken one analytical question through exploration, SQL, Python, Polars,
execution choices, and delivery. The next step is not necessarily another tool. It is
the smallest justified action that helps the intended user make a better decision.
