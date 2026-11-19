---
name: commit
description: Draft a copy-ready Conventional Commit message for staged changes, with a body explaining the motivation and relevant trade-offs. Use when asked to prepare a commit message without creating a commit.
---

# Draft a commit message

Inspect the staged changes and draft a commit message. Do not stage, unstage, modify files, or run git commit.

## Gather evidence

- Run `git status --short`, `git diff --cached --stat`, and `git diff --cached`.
- Base the message only on staged changes. When a file has both staged and unstaged edits, describe only its staged version.
- Read relevant surrounding code or recent commit history when needed to understand intent or repository conventions.
- Use the conversation and any supplied context to understand why the changes were made. Treat supplied context as guidance, not permission to describe changes absent from the index.
- Do not expose secrets found in diffs.
- If nothing is staged, say so briefly and stop. Do not silently use unstaged changes.
- If the motivation is materially ambiguous, ask a focused question rather than inventing it. Otherwise explain only motivations supported by the evidence.

## Compose the message

- Use a Conventional Commits header: `type(scope): imperative summary`. Omit the scope if it adds no useful information.
- Choose the type that best describes the staged change, such as `feat`, `fix`, `docs`, `refactor`, `perf`, `test`, `build`, `ci`, or `chore`.
- Keep the header concise, preferably at most 72 characters, without a trailing period.
- Include a blank line, then a useful body explaining why the change is needed, the problem it addresses, and important design choices or trade-offs. Explain outcomes rather than merely listing modified files.
- Keep the body proportional to the change; short paragraphs or bullets are appropriate. Wrap body lines at about 72 characters.
- Do not invent motivations, test results, issue references, or compatibility guarantees.
- Use `!` and a `BREAKING CHANGE:` footer only when a genuine breaking change is supported by the staged diff and context. Include other trailers only when supported or explicitly requested.

## Copy-ready output

Return exactly one proposed commit message as plain text. Do not use Markdown fences, a heading, quotation marks, a git command, introductory commentary, or a closing explanation. The entire final assistant message must be suitable for copying with Ctrl+X and pasting into a commit-message editor.
