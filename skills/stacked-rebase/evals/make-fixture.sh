#!/usr/bin/env bash
# Builds a realistic "morning after" repo under $1 (must not exist or be empty).
#   $1/remote.git  bare origin
#   $1/work        main clone (checked out: feat-two, with dirty tracked + untracked + staged files)
#   $1/work-wt     linked worktree for feat-three (dirty tracked file)
# Branches: main, feat-one <- feat-two (stack), feat-three (independent, in worktree, will conflict),
#           old-merged (merged via merge commit), old-squashed (squash-merged)
# Origin's main has 2 new commits not yet pulled locally; one touches the same line as feat-three.
# Variant "conflicts": feat-three also edits binary data.bin (upstream does too -> unfixable), feat-four is stacked on feat-three,
#   and the uncommitted edit in work/ touches app.txt line2 which upstream also changed (stash pop conflicts).
set -eu
VARIANT="${2:-default}"   # default | conflicts
R="$1"; mkdir -p "$R"; cd "$R"
export GIT_AUTHOR_NAME=T GIT_AUTHOR_EMAIL=t@t GIT_COMMITTER_NAME=T GIT_COMMITTER_EMAIL=t@t
git init -q --bare -b main remote.git
git clone -q remote.git work 2>/dev/null; cd work

# Update the bare remote's main from another repo by fetching into it.
sync_remote() { git -C "$R/remote.git" fetch -q "$1" "+main:main"; git fetch -q origin; }

printf 'line1\nline2\nline3\nline4\nline5\n' > app.txt
printf 'a\n' > one.txt; printf 'b\n' > two.txt; printf 'c\n' > three.txt
printf '\x00\x01\x02\x03' > data.bin
git add .; git commit -qm "initial"; sync_remote "$R/work"

git checkout -q -b old-merged;   echo m > merged.txt;  git add .; git commit -qm "old merged work"
git checkout -q main; git merge -q --no-ff old-merged -m "Merge old-merged"
git checkout -q -b old-squashed; echo s > squashed.txt; git add .; git commit -qm "old squashed work"
git checkout -q main; git merge -q --squash old-squashed; git commit -qm "old squashed work (#12)"
sync_remote "$R/work"
git branch -q --set-upstream-to=origin/main main

git checkout -q -b feat-one;   echo "one-change" >> one.txt;  git add .; git commit -qm "feat-one: change"
git checkout -q -b feat-two;   echo "two-change" >> two.txt;  git add .; git commit -qm "feat-two: change"
git checkout -q main
git checkout -q -b feat-three; sed -i 's/line3/line3-from-feat-three/' app.txt; git add .; if [ "$VARIANT" = conflicts ]; then printf '\x00\xAA\xAA\xAA' > data.bin; fi
git add .; git commit -qm "feat-three: edit line3"
if [ "$VARIANT" = conflicts ]; then
  git checkout -q -b feat-four; echo four >> three.txt; git add .; git commit -qm "feat-four: stacked on feat-three"
fi
git checkout -q main

# origin moves on (made through a second clone)
cd "$R"; git clone -q remote.git other 2>/dev/null; cd other
echo "upstream-one" > upstream1.txt; git add .; git commit -qm "upstream: add file"
sed -i 's/line3/line3-from-upstream/' app.txt; if [ "$VARIANT" = conflicts ]; then printf '\x00\xBB\xBB\xBB' > data.bin; sed -i 's/line2/line2-from-upstream/' app.txt; fi
git add .; git commit -qm "upstream: edit line3"
sync_remote "$R/other" 2>/dev/null || git -C "$R/remote.git" fetch -q "$R/other" "+main:main"
cd "$R"; rm -rf other

cd "$R/work"
git worktree add -q ../work-wt feat-three
echo "wip" >> "$R/work-wt/three.txt"                 # dirty tracked file in the worktree
git checkout -q feat-two
if [ "$VARIANT" = conflicts ]; then sed -i 's/line2/line2-my-wip/' app.txt; fi
echo "wip-two" >> two.txt                            # dirty tracked file in main checkout
echo "scratch" > notes-untracked.txt                 # untracked file in main checkout
echo "staged" > staged.txt; git add staged.txt       # staged new file
echo "fixture ready at $R/work (current branch: feat-two)"
