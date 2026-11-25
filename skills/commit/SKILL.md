---
name: commit
description: Turn working-tree changes into a clean series of meaningful commits, each telling the story of one logical step (why, what was found, why this approach), following the format in FORMAT.md. Use whenever you are about to create commits, including "commit everything", "commit these changes", "commit what we did", or committing after the user reviewed uncommitted work. Also use when committing as you go during autonomous work that the user will only review as a finished PR.
---

# Commit

Read [FORMAT.md](FORMAT.md) first. It defines the message format and what a good series looks like. This file is the procedure for producing that series.

Never push, never rewrite commits that are already pushed or that you did not create, and never commit unless the user asked for commits or asked for the work to be done end to end.

## 1. Survey

```bash
git status --short
git diff HEAD --stat
git log --oneline -15
```

The recent log shows the repo's own conventions. If the repo has `commitlint`, a `CONTRIBUTING.md` commit section, or a clearly different established style, follow it where it conflicts with FORMAT.md and keep the story-telling body.

Read the actual diff (`git diff HEAD`, plus untracked files) before deciding anything. Do not plan commits from file names.

## 2. Plan the series

Group the changes into logical steps, then order them so each commit is a coherent step and the series reads as the story of the change (see "The series as a whole" in FORMAT.md).

Write the plan as one line per commit (`type(scope): summary` plus the files or hunks it covers). If the grouping is genuinely ambiguous and a wrong guess would be costly, ask once. Otherwise proceed.

Work out what you know about the *why* for each group from the conversation so far: the problem, what was tried, what was decided. That is the raw material for the body. Do not invent what you do not know (see "Honesty" in FORMAT.md).

## 3. Commit each step

Stage exactly one step. Whole files with `git add <paths>`. When one file holds hunks for different steps, stage by hunk without the interactive UI: write the wanted hunks to a patch and `git apply --cached <patch>`.

Check `git diff --cached` shows only this step. Before committing, reread the message you wrote and strip anything sensitive (secrets, other people's names or contact details, customer or business data, anything not yours to share; see "Sensitive information" in FORMAT.md). The conversation and the diff often contain such details, so do not copy them into the message. Then commit with the message from a heredoc so formatting survives:

```bash
git commit -F - <<'EOF'
type(scope): summary

Body paragraphs...
EOF
```

Run any repo hooks normally. If a hook fails, fix the cause and make a new commit attempt; never bypass it with `--no-verify`.

## 4. Verify

- `git status` is clean, or only holds what you deliberately left out. Tell the user about anything left out.
- No commit message contains sensitive information. If one does, fix it now if the commit is yours and unpushed, otherwise tell the user.
- `git log --stat <base>..HEAD` reads like a story top to bottom: no vague subjects, no step that depends on a later one, no unrelated changes.

## During autonomous work

When you are doing a task end to end and the user will only see the PR, commit as you go. Commit after each logical step is done, not at the end, so the story is written while you still know it. Do not make one big commit at the finish, and do not leave uncommitted work behind. If tests or CI fail later, or review turns up a real problem, commit the fix as a new step that continues the story. Do not amend or fold it into earlier commits.

If the user said not to commit, or to leave changes uncommitted for review, do not commit. They will ask later, and then you run this procedure on the whole working tree.

## Report

End with the list of commits created (`git log --oneline <base>..HEAD`) and anything left uncommitted or skipped, and why.
