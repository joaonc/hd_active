---
description: Clean up local branches and worktrees that have already been merged into main
---

# Git Clean (branches + worktrees)

Clean up local branches and worktrees whose changes have already made it to `main`, and are
therefore safe to delete. This command is destructive (branch deletion, worktree removal), so
never skip the confirmation step.

## Definition of "no longer needed"

A branch/worktree is **still needed** (must NOT be deleted) if ANY of these is true:

- It has uncommitted or untracked changes (dirty working tree).
- It has commits that are not yet in `main`, **and** there is no merged PR for it (no PR at all,
  or a PR that's open, or a PR that was closed without merging).
- It has an open PR that is not yet merged.

In short: **everything not yet merged into `main` is needed.** Only delete a branch/worktree once
its changes are confirmed to be in `main` (either the branch has no commits ahead of `main`, or
its PR shows as merged) and its working tree is clean.

Never touch:
- `main` (or `master`) itself.
- The branch/worktree you are currently running this command from (git will refuse to delete a
  checked-out branch anyway — skip it up front instead of erroring).
- The primary/main worktree (the repo root itself), even if its branch turns out to be stale —
  only remove *linked* worktrees (the ones under `.claude/worktrees/` or wherever `git worktree
  add` put them). Just leave the primary worktree's branch checked out; report it as skipped if
  it's stale, don't try to force it onto another branch.

## Steps

1. **Inventory.**
   - `git worktree list --porcelain` — capture every worktree's path and branch.
   - `git for-each-ref --format='%(refname:short)' refs/heads/` — capture every local branch.
   - `git branch --show-current` — identify the branch active in *this* working directory, so it
     can be excluded.
   - `git fetch --prune` first, so merged-PR/gone-branch detection below reflects the remote's
     current state.

2. **Classify each branch.** For every local branch except `main`/`master` and the current one:
   - Determine if it has a linked worktree (from step 1). If so, run
     `git -C <worktree-path> status --porcelain` — any output means dirty, so mark it **needed**
     and move on.
   - Count commits ahead of main: `git rev-list --count main..<branch>`.
     - If `0`, the branch has nothing `main` doesn't already have → candidate for deletion
       (subject to the dirty check above).
     - If `>0`, check its PR status: `gh pr list --head <branch> --state all --json number,state,mergedAt --limit 1`.
       - No PR found, PR `OPEN`, or PR `CLOSED` (unmerged) → **needed**, keep it.
       - PR `MERGED` → candidate for deletion (subject to the dirty check above).

3. **Build the deletion plan.** Produce a clear list split into:
   - Branches/worktrees that will be deleted (with the reason: "no unique commits" or
     "PR #NNN merged").
   - Branches/worktrees that are being kept (with the reason: "uncommitted changes", "PR #NNN
     open", "PR #NNN closed unmerged", or "no PR, unmerged commits").

4. **Confirm before deleting.** Show the plan from step 3 to the user and ask for explicit
   confirmation before deleting anything. Do not proceed on an ambiguous or missing answer.

5. **Delete, once confirmed.** For each branch approved for deletion:
   - If it has a linked worktree: `git worktree remove <path>` (it's already confirmed clean, so
     no `--force` should be needed; if git still refuses, report the error rather than forcing).
   - Delete the branch:
     - `git branch -d <branch>` if it had zero commits ahead of main (git can verify this itself).
     - `git branch -D <branch>` if deletion is based on a confirmed merged PR (git's own
       fast-forward check will fail for squash/rebase merges even though the PR is merged, so the
       force flag is expected and safe here — the merge status was already verified in step 2).

6. **Report results.** List exactly what was deleted (branch name, worktree path if any, and the
   reason), and what was kept and why. If any deletion failed, show the error instead of silently
   skipping it.
