# Lesson 10: Make a change another analyst can trust

Two analysts want to improve the affinity review. One is clarifying the interpretation;
the other is changing the workbook presentation. How can they work independently without
losing each other's work—or quietly giving the same measure two different meanings?

Git helps you record and combine changes to files. Review helps you decide whether those
changes make analytical sense. You need both: applying changes without a conflict is
not proof of a correct analysis.

Allow about 60–90 minutes, plus time for a colleague to review. Complete
[Lesson 9](../lesson_9/README.md) first. You will make one small change on a feature
branch, ask for review, and bring the agreed change into the shared version. You do not
need to learn Git internals or a complicated branching strategy. We use one workflow:
**rebase your feature branch when it needs updating, then squash-merge the approved PR**.
This keeps `main` linear, with one meaningful commit for each accepted change.

## 1. Agree where it is safe to practise

Use an organization-approved training repository where you have permission to push a
branch and open a pull request. Ask the facilitator to provide one if this course's
repository is read-only. Do not push practice changes to a production project, make a
public copy of work data, or change repository permissions to complete the exercise.
Authentication and hosting access follow your organization's approved process; never
paste a password or access token into a project file.

The commands below run in **PowerShell in the repository root**. They assume the shared
remote is called `origin` and its main branch is `main`. Check with the maintainer if
your training repository uses different names. This lesson calls the review proposal a
**pull request (PR)**; your hosting service may use a different name.

Without hosting access, you can still create a local branch and commit, then ask a
partner to review the diff beside you. Record their feedback in your investigation
record. That practises change and review, but not publishing a branch, opening a PR,
or accepting it through the hosting service; return to those steps when access is available.

### The small mental model

| Term | What it means for your analysis |
| --- | --- |
| Repository | The project files and their recorded history. Your clone is a local copy. |
| Working changes | Edits on your computer that are not yet recorded in a commit. |
| Staging | Choosing the exact changes to include in your next commit. |
| Commit | A recorded snapshot of those changes, with a message explaining them. It is local until pushed. |
| Feature branch | A named line of work for one bounded change, separate from the team's accepted version. |
| Push / pull | Send committed work to the remote / bring remote work into your local branch. |
| Pull request | A proposal to accept a branch's changes, with a diff, discussion, and checks. It is not the same as `git pull`. |
| Rebase | Replay your branch's commits on top of the latest shared version, updating their starting point. |
| Squash-merge | Accept a PR's combined changes as one new commit on `main`, rather than preserving every work-in-progress commit. |

A branch is not a separate folder or a private backup of every file. Switching branches
changes tracked files in the same project folder. Uncommitted edits can follow you
between branches or block a switch: check your status before switching.

## 2. Structure the work so people can share it

A shared analysis needs a clear question, definitions, reproducible steps, and a place
for review decisions—not a large software architecture.

For a future analytical project, a modest structure might be:

```text
README.md                 # question, owner, inputs, and how to run
analysis/
  definitions.md          # population, grain, measures, exclusions
  decisions.md            # agreed choices, reasons, and remaining uncertainty
  sql/                    # saved queries in an explicit execution order
src/<project>/            # reusable calculations and a small delivery script
tests/                    # checks for assumptions and expected behaviour
.data/                    # ignored local inputs, databases, and generated outputs
pyproject.toml
uv.lock
```

This is a design example, not a request to rearrange this teaching repository. Here,
Lesson 7 holds reusable calculations, Lesson 9 presents them, and `.data/` holds local
outputs. Start with a few files; split them when there is a meaningful boundary, not
just to create more folders.

Agree these working rules:

- **One maintained definition.** Reuse the basket calculation rather than copying it
  into each report. Document population and grain where colleagues can find them.
- **Split by responsibility.** Keep input preparation, calculation, and presentation
  distinguishable. A workbook-label change should not require rewriting pair counting.
- **Make a handoff explicit.** If a result has one row per unordered pair with specific
  column names and numeric proportions, say so. A colleague can build presentation
  against that agreement without editing the calculation at the same time.
- **Keep personal exploration out of the shared path.** Use a clearly named scratch
  location and promote only useful, explained work. Do not use `final_v2_alex.py` as
  a substitute for shared history.
- **Commit code, definitions, and checks together.** Record intentional dependency
  changes in both `pyproject.toml` and `uv.lock`. Do not commit `.venv`, local databases,
  generated workbooks, credentials, or unapproved extracts. `.data/` is ignored here;
  `olist/` is an existing, deliberate Git LFS teaching-data exception, not a general
  instruction to put business data in Git.

Git shares files, not your running environment. Each analyst still has their own
`.venv`, local DuckDB database, and temporary SQL views. A shared branch does not share
an open DBeaver session, and accepting code does not deploy or refresh a shared service.

**Your turn:** sketch how two analysts could divide a new request: add English category
labels while keeping original category keys and counts unchanged. What does the label
lookup promise about key uniqueness and missing labels? Which file or interface needs
agreement before either person starts?

## 3. Agree one small change before editing

For your first PR, improve the **explanation**, not the affinity calculation.

In your training copy, create `analysis/review_notes.md`. Use a short description of
how the Lesson 9 candidate list should be interpreted, with these headings:

```text
Audience and decision:
Population and grain:
What the candidate cutoffs mean:
What this result cannot establish:
Next check and who should discuss it:
How to reproduce the workbook:
```

Use what you learned in Lesson 9. In particular, distinguish screening cutoffs from
validated recommendations. Do not include customer records or workbook exports.

Tell your partner the scope before editing: “I will add review notes; I am not changing
the calculation, cutoffs, or report.” Your partner can work on a separate, agreed task,
such as clarifying the workbook instructions. Avoid both editing the same paragraph
for this first pass. Take turns being author and reviewer.

Small branches should answer one reviewable question. Do not combine an interpretation
change, a project-wide reformat, and a new dependency in the same PR.

## 4. Start from the shared version and make a branch

First inspect your local state:

```powershell
git status
```

If it reports edits you did not expect, stop and identify them. Do not discard them to
make the exercise work. Finish and commit your own current work on its appropriate
branch, or ask the facilitator how to preserve it before proceeding. Start the following
sequence with a clean working tree:

```powershell
git switch main
git pull --ff-only
git switch -c notes/affinity-review-alex
```

Replace `alex` with your name or another agreed identifier. `--ff-only` updates your
local `main` only if Git can do so without combining diverged histories. If it refuses,
ask for help rather than adding force options. Feature branches are usually short-lived:
one small change, review, squash-merge, then a new branch for the next change.

Create `analysis/review_notes.md` in VS Code and write your explanation. Save it, then
inspect what you are about to record:

```powershell
git status
git diff
```

`git diff` shows changes to tracked files; it will not show the contents of a new,
untracked file. Open the new file in VS Code, then stage that specific path and inspect
the staged diff:

```powershell
git add analysis/review_notes.md
git diff --staged
git commit -m "docs: explain how to review affinity candidates"
```

Staging is your chance to exclude unrelated edits. Avoid `git add .` until you are
confident about every file it would include. Read the diff for accidental data or
credentials as well as typos. If Git asks for your name and email, use your approved
work identity following the maintainer's instructions, then retry the commit.

### Use Conventional Commits to make history readable

We recommend [Conventional Commits](https://www.conventionalcommits.org/): a simple
structure for commit messages that tells readers what kind of change was made and why.
For an analyst returning to a project, `fix: prevent duplicate category pairs` is more
useful than `updates` or `final version`. Consistent messages make history easier to
scan, help colleagues find relevant changes, and can support automated change summaries
or release tooling if a team later needs them. No extra tooling is needed here.

Use this structure:

```text
type(optional-scope): short description

Optional body explaining why the change was needed, important analytical effects,
and any limitations or trade-offs.
```

The type is required; the scope and body are optional. A scope names the part of the
analysis, such as `affinity` or `report`. Keep the description specific and action-led:
“clarify”, “add”, or “correct”, rather than “misc changes”. Use a body when the reason
or consequences are not obvious from the title.

Start with a few useful types:

| Type | When to use it | Example |
| --- | --- | --- |
| `docs` | Explanations or instructions | `docs: clarify candidate review limitations` |
| `feat` | A new analytical or delivery capability | `feat(report): add English category labels` |
| `fix` | Correct behaviour that was wrong | `fix(affinity): prevent duplicate category pairs` |
| `refactor` | Restructure code without intentionally changing results | `refactor(report): extract workbook formatting` |
| `test` | Add or improve checks | `test(affinity): check unordered pair uniqueness` |
| `chore` | Project upkeep, such as tool configuration | `chore: update editor recommendations` |

Choose the type by the purpose of the change, not the file extension. Correcting a
wrong denominator in SQL is a `fix`, not merely a code tidy-up. Calling a change
`refactor` does not establish that results stayed the same; checks still need to show
that. If a change breaks an agreed interface—for example, it renames a column another
report uses—Conventional Commits supports a `!`, such as
`feat(affinity)!: rename pair count column`. Explain what consumers need to change in
the body and agree the handoff before accepting it; punctuation is not notification.
You do not need to learn the full specification for this exercise.

Use this structure for your working commits and PR title, and **especially for the
final squash commit**: that is the message colleagues will see on `main`. A good message
summarises the agreed change, not every correction made during review. It complements
the PR's evidence and discussion; it does not replace them.

For this documentation-only change, check the explanation against Lesson 9 and verify
the reproduction command. If a later change affects Python, use the repository's Ruff,
type, and relevant analytical checks as well. Passing style checks alone does not verify
populations, joins, or measures.

## 5. Open a PR someone can review

If training hosting access is available, publish your branch:

```powershell
git push -u origin notes/affinity-review-alex
```

On the hosting site, open a PR **from your feature branch into `main`**. Check both
branch names and the **Files changed** view: you should see only your intended notes.
Request your partner's review. Use a description like this:

```text
Why: Help a colleague interpret the candidate review without implying proven uplift.
Changed: Added review notes; no code or cutoff changes.
Analytical effect: No change to population, grain, measures, or candidate selection.
Validation: Compared wording with Lesson 9; checked the reproduction instructions.
Review request: Are the limitations and proposed next check clear and justified?
```

For a change that *does* affect results, describe the old and new definition, the reason,
and the expected effect. Include a small, non-sensitive before/after summary and checks
performed. Never write “no analytical effect” just because the code change is short.

## 6. Review to share context and understanding

The main purpose of review is to **share context**: why this change matters, how the
analysis works, what choices were made, and what colleagues will need to know when
they use or maintain it. The author explains their reasoning; the reviewer brings
another perspective and learns enough to help carry the work forward. This reduces
dependence on one person's memory and helps the team make consistent decisions.

Finding bugs is valuable, but it is not the admission price for submitting a review.
A review that confirms your understanding, connects the change to another piece of
work, or records why the approach makes sense is useful even when nothing needs fixing.
Do not invent a criticism or request a cosmetic edit just to show that you reviewed.

Read the PR's purpose and diff. For this first exercise, submit a short review that
summarises your understanding of the change and its analytical effect. Add genuine
questions, relevant context, or suggestions where you have them. If you spot a bug or
unsupported claim, call it out clearly; distinguish a blocking correctness issue from
an optional preference. For example:

> **Needs change:** “best recommendations” sounds validated. Could we call these
> candidates for domain review and say that lift does not establish incremental sales?

> **Suggestion:** Put the reproduction command beside the output path so readers can
> find both without opening another document.

A review with no requested changes is equally legitimate:

> **Reviewed, no changes requested:** I understand that these notes help merchandising
> interpret the existing candidate list; they do not change the population or cutoffs.
> Keeping screening separate from evidence of uplift makes sense for this handoff.
> I checked the explanation against Lesson 9 and can follow the reproduction steps.

Use this short checklist for future code or SQL reviews too:

- Can I explain why this change is being made and how it fits the wider analysis?
- What context have I learned, and what relevant context can I share with the author?
- Is the question clear, and is this change within the agreed scope?
- Are population, grain, exclusions, and denominator still what the team intended?
- Could a join duplicate records, or a label change alter the category keys?
- What evidence supports the result? What check would expose a plausible mistake?
- Can another analyst reproduce it from saved files rather than an open session?
- Are definitions, limitations, instructions, and data-handling choices consistent?

A reviewer need not be the team's strongest programmer. Understanding a definition,
sharing relevant business context, or making a handoff clearer are important contributions,
as is spotting a changed denominator or unsupported business claim. Ask for help with
unfamiliar code rather than approving something you cannot assess. Say what you reviewed
and where your confidence ends. Review is shared reasoning, not an exam, a bug quota,
or a search for someone to blame. **Submit your review even if you found no bugs**;
if you understand and support the change within your review scope, approval is appropriate.

If feedback calls for edits, the author updates the same file on the same branch, then runs:

```powershell
git add analysis/review_notes.md
git diff --staged
git commit -m "docs: clarify candidate review limitations"
git push
```

The existing PR updates; do not open a new PR for each correction. Explain how you
addressed the comment, or why you suggest a different approach. The reviewer checks the
revision before approving. Once required reviews and checks are satisfied, use the
hosting site's **Squash and merge** option (or its equivalent). A maintainer may need
to perform that step; ask them to configure the training repository for this workflow.
Approval alone does not accept a PR.

Give the resulting commit a Conventional Commit title, such as
`docs: explain how to review affinity candidates`, and a short body explaining why the
change was made. Check the hosting site's suggested message rather than accepting a
list of drafting messages. Your local drafting and correction commits become one commit on `main`.
The PR retains the review discussion. If `main` has moved and your branch needs updating
before acceptance, follow the rebase steps below, then have the updated result checked.

## 7. Avoid collisions—and know which kind you have

Feature branches keep unfinished commits off `main`; they do not reserve files or stop
other people editing them. Most collision prevention happens before a PR is accepted:

| Situation | Better working habit |
| --- | --- |
| Two people plan to change the same calculation | Agree the definition and let one make that focused change; the other reviews or tackles a separate part. |
| Everyone edits one giant script | Separate reusable calculation from presentation at a useful boundary; avoid a full restructure during an urgent small change. |
| A branch lives for weeks | Keep changes small, review promptly, and communicate when shared definitions change. |
| Formatting obscures a meaningful change | Keep unrelated mass formatting out of the PR. |
| Two reports need the same measure | Reuse the maintained calculation and agree its output, rather than maintain two copies. |
| A shared table or workbook is being overwritten | Agree ownership, locations, and publishing rules; a Git branch does not isolate database writes or output paths. |

There are two different hazards:

### Update your branch with a rebase

When `main` has advanced and your PR needs updating, start on **your own feature branch**
with a clean working tree. Coordinate with your partner first: this workflow assumes
one author per branch, with colleagues contributing through review rather than pushing
commits to each other's branches.

```powershell
git status
git fetch origin
git rebase origin/main
```

Git replays your commits after the latest `main`. It changes their commit IDs, but
preserves their intended changes. Do not rebase `main` or a branch other people are
using as their own starting point. You do not need interactive rebasing or manual
squashing for this lesson; the hosting site handles the final squash.

**Text conflict:** Git cannot apply an edit cleanly to the same region of a file. This
is normal, not evidence someone broke the project. During a rebase, `git status` lists
the affected files. With the author of the other change, inspect both versions in
VS Code and agree the intended final content. Do not blindly select “ours” or “theirs”:
those labels can be confusing during a rebase. Remove conflict markers (`<<<<<<<`,
`=======`, `>>>>>>>`), inspect the result, then stage each resolved file by its path:

```powershell
# Example path: use the actual file reported by git status.
git add analysis/review_notes.md
git rebase --continue
```

Repeat if Git pauses at another commit. If Git opens a commit-message editor, save the
message and close the editor to continue. Do not make a separate `git commit` for the
resolution. If you are unsure while the rebase is still in progress,
`git rebase --abort` returns to the pre-rebase state; ask for help. Do not skip a commit
or discard changes just to clear the warning.

After the rebase finishes, inspect the updated diff and rerun appropriate checks.
If you already published this branch, an ordinary push will usually be refused because
the commit IDs changed. Update **only your own feature branch** using:

```powershell
git push --force-with-lease origin notes/affinity-review-alex
```

Use your actual branch name. `--force-with-lease` checks that the remote branch still
matches your last fetched view before replacing its history. If it refuses, stop and
check with your partner; do not retry with plain `--force`. This is a specific step for
a rebased personal branch, never a way to push over `main` or someone else's work.
If the branch has never been published, use the normal `git push -u origin <branch>`
command instead. Ask for another review of the updated result, especially any conflict
resolution; the hosting site may also require fresh approval and checks.

**Meaning conflict:** Git applies every edit cleanly, but one person changes the
population to all orders while another writes notes assuming delivered orders only.
Different files can now disagree without any conflict warning. Definition review and
analytical checks, not Git's ability to apply text changes, catch this.

**Your turn:** discuss that population example with your partner. Which code, notes,
workbook labels, and checks would need to change together? Who else should know? If
there is time, have the facilitator demonstrate a same-line text conflict in a disposable
training file; there is no need to manufacture one in the calculation.

## 8. Close the loop

After the PR has been squash-merged, return to the shared version with a clean working tree:

```powershell
git switch main
git pull --ff-only origin main
uv sync
```

Open the accepted notes and confirm your partner can find the reproduction instructions.
For a code change, rerun the relevant workflow and checks against the agreed local inputs.
Check the hosting site's history: this PR should have added one meaningful commit on
`main`, not all your drafting commits or an extra branch-joining commit.
Delete the completed remote feature branch through the hosting site according to the
team's practice. Always start the next task on a new branch from updated `main`;
do not reuse the old branch after its changes have been squashed.

Keep a short record of the PR link (or local-review substitute), feedback, changes made,
and any unresolved questions. An accepted PR records an agreed code or documentation
change—not permission to publish data or a guarantee of a successful business outcome.

You have completed the lesson when you can:

- Explain the difference between a local edit, a commit, a push, and a PR.
- Make one bounded change on a feature branch and inspect exactly what it includes.
- Explain how rebasing updates that branch and squash-merging keeps `main` linear.
- Write a Conventional Commit message that makes the purpose of the accepted change clear.
- Submit a review that shares understanding and context, whether or not you find a bug,
  and respond to colleagues' feedback.
- Propose a simple project structure and division of work that reduces overlap.
- Distinguish a text conflict from a disagreement in analytical meaning.
- State which shared-work steps you practised and which still require hosting access.

The aim is not to master every Git command. It is to make a small change that another
analyst can understand, question, reproduce, and safely build on.

### Optional: Graphite can simplify the mechanics

[Graphite](https://graphite.dev/) provides a CLI and a review interface that can make
many of these operations easier: creating branches, submitting and updating PRs,
syncing with `main`, and rebasing related work. It is particularly useful for
**stacked PRs**—a sequence of small changes where one builds on another—because it
helps manage their dependencies and keep them up to date. You do not need stacked PRs
or Graphite to complete this lesson.

The plain Git workflow above gives you the mental model; Graphite can reduce the
commands and bookkeeping around it. It does not remove the need to resolve conflicts
thoughtfully, check analytical meaning, or share context through review. If your team
uses a supported hosting service and approves Graphite's installation and repository
access, ask for a demonstration using the same small-change, rebase, and squash-merge
workflow. Treat it as an optional convenience, not another prerequisite.
