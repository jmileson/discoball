# Lesson 9: Deliver an analysis—not just a spreadsheet

A merchandising colleague wants to review category pairs in Excel, filter the list, and
discuss candidates in a meeting.

You can build that workbook. But before you do, ask what decision it supports and
whether a file is the right delivery method. Automating an output does not automatically
make it useful.

You have produced information that was not explicit in individual order records:
which categories occur together, how common those combinations are, and how their
co-occurrence compares with a popularity baseline. Now help the team use it. The
workbook supports the discussion; your recommendation connects the evidence to a
next action and explains what the team would need to learn from it.

**Excel is a delivery mechanism here, not the analytical product itself.** The
maintained product is the analysis: its definitions, reusable calculations, checks,
and interpretation. The workbook is a generated snapshot of that work. It should be
possible to reproduce the analytical result without opening a particular workbook.

As a working estimate, allow about 60–90 minutes for generating and inspecting the
workbook, then a separate session to synthesise your final recommendation. Complete
[Lesson 8](../lesson_8/README.md). You will generate
a local review pack, inspect it, and use your investigation record to recommend a
next analytical or business action as well as a delivery approach.
You need Excel or a compatible workbook viewer for the inspection step; rendering can
vary between applications.

## 1. Define the deliverable

For this exercise, the audience needs a **historical candidate review**, not a live
sales dashboard or an automated recommendation service.

Use your investigation record to write down:

- Who will use it and what decision they are considering.
- What the analysis has added to their understanding.
- What next check or action you recommend, and why.
- Whether they need a snapshot or current data.
- What definitions and limitations must travel with the numbers.
- Whether the data may be exported to the intended location.

> **Interpretation limit — affinity is not expected return**
>
> The Olist inputs do not provide margins, recommendation exposure, implementation
> costs, or experimental effects. Affinity measures cannot be labelled expected profit
> or additional sales. If the team needs that decision, identify what further evidence
> would help evaluate it.

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
directory.

> **Watch out — rerunning replaces the review file**
>
> Each run replaces the named workbook. Close it in Excel before rerunning; an open
> workbook can prevent replacement, especially on Windows. Preserve any review
> annotations separately before regenerating. This exercise is not a versioned,
> concurrent, or failure-safe publishing service.

## 3. Inspect the workbook as a reader

The workbook contains:

| Sheet | Purpose |
| --- | --- |
| Read me | Audience, population, grain, count cutoffs, limitations, delivery role, and ownership status |
| Run summary | Generation time, counts, and checks performed |
| Candidate pairs | Pairs retained by the illustrative count cutoffs, for investigation |
| Category summary | Individual category frequencies |

The script uses Excel tables with filters, readable widths, frozen headers, and number
formats. Confidence and support remain numeric proportions, displayed as percentages.
Converting `0.04` to the string `"4%"` would make later numerical use less reliable.

If no pairs pass the count cutoffs, the candidate sheet explicitly says so. That is
different from a failed run. The script raises errors for invalid input assumptions
rather than disguising them as an empty report.

The candidate list uses original category keys. They are stable analytical identifiers,
but not necessarily the best reader-facing labels. If you add English translations,
check translation-key uniqueness and retain a fallback for missing labels. A
presentation join must not change the pair counts.

**Your turn:** choose one candidate and check its counts and percentages against the
Python result. If none pass the cutoffs, verify that the workbook explicitly reports
that result and that it agrees with the Python output. Try filtering any populated
Excel table. Can you still find the definitions without the lesson open? What question
would you ask the team about a retained pair before proposing an action?

## 4. Understand presentation versus calculation

Analytical calculations remain in the reusable Polars workflow. The workbook presents
the result; it does not recreate the analysis in another set of formulas.

### Keep the repeatable analysis outside the workbook

A long-lived workbook with an ODBC connection, embedded SQL, and manual adjustments
can become a substitute for a repeatable analytical workflow. That is an understandable
workaround when no supported path exists, but it is not the pattern this course is
teaching.

When the analytical logic lives inside circulating workbooks, copies can acquire
different queries, definitions, connection settings, and edits. It becomes difficult to
review changes, establish which version produced a number, validate results consistently,
control access across copies, or assign responsibility for refresh failures. A workbook
that still opens is not evidence that its analysis is current or correct.

Keep the maintained definitions, SQL or Python, and checks in a reviewable, reproducible
workflow. Generate Excel from its approved outputs. Corrections to the analysis belong
in that workflow, followed by regeneration—not as an undocumented patch to a cell.
Review annotations can remain useful, but preserve them separately from regenerated
outputs and agree how they feed into decisions.

An existing connected workbook may need a supported transition rather than an abrupt
shutdown. Identify its users, logic, dependencies, and owner, then agree a repeatable
replacement before people depend on it. The goal is to govern the analytical work,
not simply move hidden logic into a different file type.

The export disables automatic interpretation of strings as formulas or URLs. This is a
useful safeguard when displaying source text; file delivery should not unexpectedly turn
data into executable spreadsheet content.

Comments or annotations entered by your colleague do not flow back into the database or
Python code. Decide explicitly how review decisions will be recorded and reconciled if
the workflow becomes ongoing.

> **Interpretation limit — generation time is not data freshness**
>
> A generation timestamp says when the file was written. This workbook uses all
> available historical data, not today's customer behavior. Check the source coverage
> before describing how current a finding is; rerunning does not create new observations.

## 5. Validate the artifact, not just the script

Before sharing a workbook, check:

- The exported candidate count agrees with the run summary and Python result.
- The population, count cutoffs, and their screening role are visible.
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
find out which tools your organization actually supports. Do not turn the generated
review pack into a permanent refreshable workbook by embedding connections and SQL.
Bring the recurring analytical need to the supported workflow discussion instead.

| Need | Possible delivery method | Questions to ask |
| --- | --- | --- |
| One-off review and annotations | Excel | How will versions and feedback be managed? |
| Recurring interactive monitoring | Supported dashboard or reporting tool | Who owns refresh, metrics, and access? |
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

Changing the format does not by itself create more intelligence. Ask what new
information the recurring version would provide, who could act on it, and what they
would do differently. A dashboard, a written brief, and a workbook can each support
BI when they help people make an informed decision and follow through.

## 7. Decide whether to build, reuse, change, or stop

An analyst-built export can fit a bounded request with a clear audience, manageable
data, and proportionate maintenance. Reconsider it when it becomes business-critical,
duplicates governed definitions, distributes restricted data, or has no owner for
recurring failures.

Do not assume that moving this script to MotherDuck solves delivery, permissions, or
operational ownership. Those need explicit design and agreement.

Bring your investigation record together into a short recommendation for the team.
You do not need to reproduce every query or exercise in this brief; keep the saved
work available as supporting evidence. Distinguish two decisions: what the team should
do next, and how the supporting information should be delivered.

```text
Audience and decision:
Information gained from the analysis:
Key evidence: population, counts, measures, and limitations:
Recommended next check or action, and why:
What outcome or observation we would evaluate:
What comparison or further evidence would help us judge it:
Who needs to agree to or own the next step:
Open questions:
Why this output format fits—or does not:
Snapshot versus recurring need:
Available alternatives to investigate:
Data-handling and access considerations:
Validation performed and limitations:
Where the maintained analytical logic and checks live:
How the workbook is generated without becoming the source of analytical truth:
Who would own updates and failures:
Recommendation: keep, reuse another tool, redesign, or stop:
```

The next step does not have to be launching a cross-sell offer. It might be domain
review of a candidate, checking whether a relationship persists across periods, or
obtaining enough follow-up history to investigate later purchases. State what that
step would resolve and what finding would change your recommendation.

If you propose a trial of an offer, identify an outcome the team wants to improve and
a comparison that would help evaluate it. For example, comparing eligible customers
randomly assigned to receive or not receive an offer could help distinguish its effect
from purchases that would have happened anyway. Agree the design and success criteria
with the appropriate people before running it; the historical affinity result does
not supply an expected improvement or a ready-made evaluation plan.

Submit the workbook and recommendation, with your investigation record and saved
implementation available for reproduction. It is acceptable to recommend that the
workbook remain a one-off prototype or that a recurring report is not justified.
Be specific about the useful next step rather than ending at “more analysis needed.”

You have completed the lesson when you can:

- Reconcile the workbook with the calculated result and inspect it as a reader.
- Explain what new information the analysis produced and its limits.
- Recommend a next step tied to a decision and describe how it could be evaluated.
- Choose a proportionate delivery method without treating a dashboard as the goal.
- Separate what you can deliver now from responsibilities and capabilities that
  require agreement.

**What you can do now:** take a business question through defined populations,
checked transformations, alternative implementations, and delivery—and explain what
someone can do with the resulting information.

You have now taken one analytical question through exploration, SQL, Python, Polars,
execution choices, and delivery. The next step is not necessarily another tool. It is
the smallest justified action that helps the intended user make a better decision.
