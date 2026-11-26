---
description: Implement multiple GitHub issues in sequence (space or comma-separated)
argument-hint: <issue-number> [issue-number ...]
---

# Implement GitHub Issues (batch)

Runs `/gh-implement-issue` for each issue number in $ARGUMENTS, one at a time.

$ARGUMENTS is one or more issue numbers separated by spaces and/or commas (e.g. `12 14 21` or
`12,14,21`).

## Instructions

1. **Parse the argument list**
   - Split $ARGUMENTS on commas and/or whitespace, discard empty tokens, and parse each remaining
     token as an integer issue number.
   - If any token isn't a valid integer, or the list is empty, stop and ask the user rather than
     guessing.

2. **Run `/gh-implement-issue` for each issue number, strictly in sequence**
   - For each issue number, in the order given: invoke the `gh-implement-issue` skill with that
     issue number as its argument, and wait for it to fully finish (implementation → PR →
     automated review → fix-up → merge, per its own instructions) before starting the next one.
   - Do not fire off multiple issues' work in parallel — each one must complete before the next
     begins, even though nothing about the issues is technically dependent on each other.
   - If a run for one issue number stops early (e.g. it raises a question for the user, or the
     issue doesn't exist), report that clearly and ask the user whether to continue with the
     remaining issue numbers or stop the batch.

3. **Summarize**
   - After the batch finishes (or is stopped), report a short per-issue summary: issue number →
     outcome (merged PR link, stopped with open question, or skipped) for every number in the
     original list.
