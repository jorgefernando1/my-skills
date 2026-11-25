---
name: stacked-rebase
description: Daily "update all my branches" routine for a git repo - pulls the latest main/master, then rebases the user's local feature branches onto it while preserving stacks (master <- feature_one <- feature_two), stashing and restoring uncommitted work in every worktree, resolving conflicts, and flagging local branches that are already merged. Use this whenever the user mentions stacked rebases, stacked branches or PRs, rebasing all/several/my active branches, "sync my branches", "update my branches after pulling main", "start of day git cleanup", or rebasing branches that live in git worktrees - even if they never say "stacked".
---

# Stacked rebase

The user does this every morning: pull the base branch, then bring their active local branches up to date, keeping stacks intact and leaving each working directory exactly as they left it (tracked changes, staged changes, untracked files). Run the whole routine, then report what happened - including what failed. Rebasing rewrites history and stashing touches uncommitted work, so the guiding rule is: **never lose work**. The only time you ask the user anything is the one question in step 1; after that, run to the end without stopping and put anything that went wrong in the final report.

This skill never deletes branches or worktrees and never pushes. Merged branches are only *flagged*.

## 0. Survey (read-only)

Run these as two separate commands (a combined command can be blocked by permission checks, and then the survey would silently use stale remote data):

```bash
git fetch origin --prune
python <skill-dir>/scripts/discover.py     # add --no-gh to skip GitHub PR lookups
```

Fetching only updates remote-tracking refs (never the user's branches or files), so do it even when the user asked for a read-only look such as "which branches are merged" - otherwise the verdict is judged against stale data.

The script prints JSON: the base branch (`main`/`master`, auto-detected), every worktree (dirty? untracked files? rebase already in progress?), and every local branch with its worktree, merged signals, and guessed `stack_parent`. Use it rather than re-deriving this by hand - it handles the fiddly cases (squash merges, parents that were already rebased).

Stop and tell the user if any worktree has `rebase_in_progress: true`; finishing or aborting that is their call.

## 1. Ask which branches to update

Show a compact tree so the user can see the stacks at a glance, marking merged branches:

```
main
├─ feat-one            (checked out in ~/proj)
│  └─ feat-two         (worktree ~/proj-wt)   dirty: 2 tracked, 1 untracked
├─ feat-three
└─ old-squashed        ✔ merged (squash, PR #12)   - nothing to rebase
```

Then ask one question (AskUserQuestion, multiSelect): which branches to update. **Include an "All active branches" option** (everything not merged, and not the base), plus one option per branch. If the user's message already says which branches (e.g. "all of them", or names), skip the question and use that.

Rules for the selection:
- If a selected branch's stack parent isn't selected, include the parent too - a child can't follow a parent that doesn't move. Tell the user you did.
- If a parent is selected, its children are not implied; only rebase them if selected (but "All" includes them).
- A merged branch has nothing to rebase; skip it even under "All", and just report it as merged.
- If a stack guess looks wrong (`stack_parent_how` is `reflog_fork_point`, or a branch plausibly has two parents), say what you assumed in the report.

### Reading the "merged" signals
- `ancestor_of_base` / `all_commits_patch_equivalent_in_base` (merge commit, rebase-merge, squash) and `github_pr_merged`: strong evidence - say "merged".
- `upstream_branch_deleted` alone: only a hint - say "upstream deleted, maybe merged".

If a *selected* branch has a merged parent, treat that parent as gone and rebase the child onto the base: `git rebase --onto <base> <merged-parent-old-tip> <child>`.

## 2. Stash uncommitted work

For every worktree you'll touch (each selected branch's worktree, the worktree that has the base checked out, and the main checkout if you'll switch branches in it) that has changes:

```bash
git -C <worktree> stash push --include-untracked -m "stacked-rebase:<branch>:<YYYYMMDD-HHMM>"
```

`--include-untracked` is what makes the working directory restorable - without it untracked files stay behind and can block checkouts. Stashes live in one list shared by all worktrees, so the message tag is how you tell them apart later. Write down `branch -> worktree path -> tag`. Leave worktrees you won't touch alone, dirty or not.

Before stashing each worktree, save its `git status --porcelain` output - it's the reference for verifying (and, after a conflicted pop, repairing) the staged/unstaged split later. Also record the starting state: which branch each worktree has checked out (the user expects to land back there), and each branch's tip SHA. Put old SHAs in the final report - they're the user's escape hatch.

## 3. Update the base branch

If the base is checked out in a worktree: `git -C <that-worktree> pull --ff-only origin <base>`. Otherwise: `git fetch origin <base>:<base>`. Fast-forward only. If local base has diverged from origin (commits made directly on it), don't merge: record "base not updated: diverged", skip all rebases that depend on it, restore stashes (step 5), and report.

## 4. Rebase, parents before children

Process branches in topological order. Capture every selected branch's old tip SHA **before** you rebase anything.

- Branch directly on base: `git rebase <base>`
- Stacked branch: `git rebase --onto <parent> <old-parent-tip> <child>`

The second form is `git rebase <parent>` done properly: after the parent was rebased, its old commits still sit under the child, and a plain `git rebase <parent>` would try to replay those old duplicates and can invent conflicts. `--onto` with the parent's *pre-rebase* tip replays only the child's own commits.

Where to run each rebase:
- Branch checked out in a worktree: `git -C <worktree> ...`.
- Branch not checked out anywhere: `git worktree add <tmpdir> <branch>`, rebase there, then `git worktree remove <tmpdir>`. This never disturbs the user's checkouts.

### Conflicts

Fix them yourself - that's part of the job:
1. List conflicted files (`git diff --name-only --diff-filter=U`) and read each conflict with enough surrounding context to understand what *both* sides were trying to do. `git log` on both sides helps when intent isn't obvious.
2. Combine both intents when they're compatible (neighbouring-line edits, entries added to the same list, imports). When the two sides edit the same line/value to different things but keeping both is a harmless, reasonable outcome, keep both and *flag it in the report* as a judgment call so the user can double check.
3. Generated files (lockfiles, snapshots): regenerate with the project's tool when it's obvious which one.
4. Remove every conflict marker, `git add`, `git rebase --continue`. A multi-commit branch may conflict again at the next commit.

**If a conflict can't be fixed with confidence** (binary files changed on both sides, logic changed in incompatible ways, a function deleted upstream but edited here, you'd be guessing), do not guess and do not ask: run `git rebase --abort` for that branch (it returns to its exact pre-rebase state), mark it **failed** with the file(s) and a one-line reason, and **also mark every branch stacked on top of it as failed ("not attempted: parent failed")** - a child can't be rebased correctly onto a parent that didn't move. Carry on with unrelated branches.

After a conflicted-but-resolved rebase, run the project's quick check only if one is obvious and cheap; otherwise just flag in the report that conflicts were resolved.

## 5. Restore the original state

For every worktree, whatever happened in step 4 (including failures - the user's uncommitted work comes back no matter what):

- Make sure it's on the branch it started on.
- Pop its stash **with `--index`** so staged vs. unstaged changes come back as they were: `git -C <worktree> stash pop --index <ref>`. Look the ref up by message tag at pop time (`git stash list | grep <tag>`) - positions shift as stashes are popped.
- **If the pop conflicts, carry on anyway.** Git still restores the working tree - including untracked files and non-conflicting edits - writes conflict markers into the conflicted files, and keeps the stash entry ("Index was not unstashed": the staged/unstaged split is not restored for those paths). Leave it that way: nothing committed, no attempt to resolve the user's own uncommitted work. Run `git reset -q -- <conflicted files>` (only those paths) so they appear as ordinary modified files with markers rather than unmerged index entries. Git also skips restoring the index for the *other* files, so compare `git status --porcelain` with the snapshot from step 2 and repair the non-conflicted paths: `git add <path>` where it was staged before and isn't now, `git restore --staged <path>` where it was only modified before and is staged now. Then **keep the stash entry** as a safety copy. Flag it in the report: worktree, conflicted files, and the stash ref/tag, so the user can resolve the markers or re-apply the stash.
- If the pop was clean, the stash is gone. Verify `git status --short` per worktree looks like the start (same tracked, staged and untracked entries). Clean up any temporary worktrees you made.

## 6. Final report

Keep it scannable, in this order:

1. **Failed / needs attention** (first, if any): each failed branch with the conflicting files, why it couldn't be fixed, and which stacked branches were skipped because of it; stash pops that conflicted (worktree, files, stash tag, still saved); base not fast-forwarded.
2. **Updated**: per branch, old tip -> new tip. Mark which ones had conflicts you resolved (file + one line on how, especially judgment calls like "kept both lines").
3. **Merged branches** you noticed (and the signal), as a heads-up; you did not delete anything.
4. Restored state: stashes popped cleanly, anything left over.
5. A reminder that rebased branches which exist on a remote need `git push --force-with-lease`. Don't push yourself.
