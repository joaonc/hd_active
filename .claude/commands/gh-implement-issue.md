---
description: Implement a GitHub issue end-to-end. branch → code → PR → review → merge
argument-hint: <issue-number>
allowed-tools: mcp__github__get_issue, mcp__github__create_pull_request, mcp__github__merge_pull_request, mcp__github__add_issue_comment, Bash, Read, Write, Grep, Glob, TodoWrite
---

# Implement GitHub Issue

Implements GitHub issue #$ARGUMENTS end-to-end: implementation → PR → automated review → fix-up → merge.

## Instructions

**Run steps 1–6 strictly one after another.** Each step depends on the previous step's output (the issue details, the branch, the PR number, the review text) — do not start a step until the previous one has fully finished, and do not fire off multiple steps' tool calls together just because parallel tool calls are normally encouraged. Every Agent call below is a single foreground call; wait for it to return before doing anything else.

1. **Fetch the issue**
   - Use `mcp__github__get_issue` to fetch issue #$ARGUMENTS's title, body, and labels for this repo (owner/repo from `git remote get-url origin` if needed). If the MCP tool errors or is unavailable, fall back to `gh issue view $ARGUMENTS --json title,body,labels,url`.
   - If #$ARGUMENTS doesn't exist or isn't open, stop and ask the user rather than guessing which issue was meant.

2. **Implement the issue — Sonnet 5, high effort**
   - Use the Agent tool, foreground (`run_in_background: false`), `model: "sonnet"`, `subagent_type: "general-purpose"`.
   - In the prompt: tell it to reason at high effort/thoroughness. Give it the full issue title/body, and instruct it to:
     - Read `CLAUDE.md` and the relevant `docs/` files first, and follow the layering/tenancy/i18n/testing conventions described there.
     - Create a new branch off `main` (e.g. `issue-$ARGUMENTS-<short-slug>`), implement the change, and run the relevant checks for whatever it touched: backend `uv run ruff check . && uv run ty check . && uv run pytest`, frontend `npm run lint && npm run typecheck && npm run test`, or `make lint && make test` if both stacks changed.
     - Regenerate the API client (`make generate-api`) if it touched anything under `services/api/src/pfo_api/routes/` or `schemas/`, per CLAUDE.md.
     - Commit the work (but not push).
   - Don't just trust the agent's summary — check `git status`/`git diff` yourself before moving on.

3. **Push and open the PR**
   - Push the branch.
   - Use `mcp__github__create_pull_request` to open a PR against `main`: title derived from the issue, body including "Closes #$ARGUMENTS" and a short summary of the change. Fall back to `gh pr create` if the MCP tool fails.
   - Record the PR number — every step below depends on it.

4. **Automated review — Opus 4.8, medium effort**
   - Use the Agent tool, foreground, `model: "opus"`, `subagent_type: "general-purpose"`.
   - Prompt it to reason at medium effort and to invoke the `gh-code-review` skill with the PR number from step 3 as its argument (that skill fetches the diff, reviews it, and posts a comment on the PR itself).
   - Have it report back the full text of the findings it posted so you can act on them in the next step.

5. **Fix review findings — Sonnet 5, high effort**
   - If the review posted no Critical/Warning/Suggestion items, skip to step 6.
   - Use the Agent tool, foreground, `model: "sonnet"`, `subagent_type: "general-purpose"`, instructed to reason at high effort.
   - Give it the full review text and the branch name. Instruct it to address each item it agrees with, re-run the same lint/typecheck/test commands from step 2, commit, and push to the same branch.
   - If a finding raises a genuine open question only the user can answer (a product/design decision, an ambiguous requirement — not something decidable from the code or docs), stop here and ask the user via AskUserQuestion instead of guessing. Do not proceed to step 6 until that's resolved.

6. **Merge**
   - Unless the user said otherwise earlier in the conversation, or step 5 raised an unresolved question, merge the PR now: `mcp__github__merge_pull_request`, falling back to `gh pr merge --squash` if the MCP tool fails.
   - Report the merged PR URL and a one-line summary of what changed.
   - If the user said not to merge, or a question is still open, stop after step 5 and report the PR link instead.
