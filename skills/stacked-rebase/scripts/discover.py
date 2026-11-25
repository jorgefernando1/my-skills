#!/usr/bin/env python3
"""Read-only survey of a git repo for the stacked-rebase skill.

Prints JSON describing: the base branch, every worktree (and whether it is
dirty / mid-rebase), every local branch (tip, worktree, upstream state,
merged-into-base signals, guessed stack parent) so the skill can plan a
rebase without re-deriving all of this by hand. Never modifies the repo.

Usage: discover.py [--base BRANCH] [--no-gh]
"""
import argparse, json, os, shutil, subprocess, sys


def git(*args, cwd=None, check=False):
    p = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    if check and p.returncode:
        sys.exit(f"git {' '.join(args)} failed: {p.stderr.strip()}")
    return p.returncode, p.stdout.strip()


def detect_base(forced):
    if forced:
        return forced
    rc, out = git("symbolic-ref", "--short", "refs/remotes/origin/HEAD")
    if rc == 0 and out.startswith("origin/"):
        return out[len("origin/"):]
    for cand in ("main", "master"):
        if git("rev-parse", "--verify", "-q", f"refs/heads/{cand}")[0] == 0:
            return cand
    sys.exit("Could not detect base branch; pass --base")


def worktrees():
    _, out = git("worktree", "list", "--porcelain")
    items, cur = [], {}
    for line in out.splitlines() + [""]:
        if not line:
            if cur:
                items.append(cur)
            cur = {}
            continue
        k, _, v = line.partition(" ")
        cur[k] = v
    res = []
    for w in items:
        path = w["worktree"]
        branch = w.get("branch", "").replace("refs/heads/", "") or None
        _, status = git("status", "--porcelain", cwd=path)
        lines = status.splitlines()
        gdir = git("rev-parse", "--git-dir", cwd=path)[1]
        gdir = gdir if os.path.isabs(gdir) else os.path.join(path, gdir)
        res.append({
            "path": path,
            "branch": branch,
            "detached": "detached" in w,
            "bare": "bare" in w,
            "tracked_changes": sum(1 for l in lines if not l.startswith("??")),
            "untracked": sum(1 for l in lines if l.startswith("??")),
            "dirty": bool(lines),
            "rebase_in_progress": any(os.path.isdir(os.path.join(gdir, d)) for d in ("rebase-merge", "rebase-apply")),
        })
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base")
    ap.add_argument("--no-gh", action="store_true")
    a = ap.parse_args()

    if git("rev-parse", "--git-dir")[0]:
        sys.exit("Not inside a git repository")

    base = detect_base(a.base)
    remote_base = f"origin/{base}" if git("rev-parse", "--verify", "-q", f"refs/remotes/origin/{base}")[0] == 0 else base
    wts = worktrees()
    wt_by_branch = {w["branch"]: w["path"] for w in wts if w["branch"]}

    _, fmt = git("for-each-ref", "refs/heads", "--format=%(refname:short)\t%(objectname)\t%(upstream:short)\t%(upstream:track)")
    branches = {}
    for line in fmt.splitlines():
        name, sha, up, track = (line.split("\t") + ["", "", ""])[:4]
        branches[name] = {"name": name, "sha": sha, "upstream": up or None, "upstream_gone": track == "[gone]"}

    gh = None if a.no_gh else shutil.which("gh")

    for name, b in branches.items():
        b["worktree"] = wt_by_branch.get(name)
        b["is_base"] = name == base
        if name == base:
            continue
        b["commits_ahead_of_remote_base"] = int(git("rev-list", "--count", f"{remote_base}..{name}")[1] or 0)
        anc = git("merge-base", "--is-ancestor", name, remote_base)[0] == 0
        _, cherry = git("cherry", remote_base, name)
        cl = cherry.splitlines()
        patch_equiv = bool(cl) and all(l.startswith("-") for l in cl)
        pr = None
        if gh and not anc and not patch_equiv:
            p = subprocess.run(["gh", "pr", "list", "--head", name, "--state", "merged", "--json", "number,mergedAt", "--limit", "1"],
                               capture_output=True, text=True)
            if p.returncode == 0:
                try:
                    data = json.loads(p.stdout or "[]")
                    pr = data[0] if data else None
                except json.JSONDecodeError:
                    pass
        signals = []
        if anc: signals.append("ancestor_of_base")
        if patch_equiv: signals.append("all_commits_patch_equivalent_in_base")
        if pr: signals.append(f"github_pr_merged(#{pr['number']})")
        if b["upstream_gone"]: signals.append("upstream_branch_deleted")
        b["merged_signals"] = signals
        # ancestor / patch-equivalent / merged PR = strong; only 'upstream gone' = weak hint
        b["likely_merged"] = bool(set(signals) - {"upstream_branch_deleted"})

    live = [n for n, b in branches.items() if not b["is_base"] and not b.get("likely_merged")]
    # Stack parent guess: the closest other live branch that is an ancestor of this
    # branch (directly, or via the reflog fork-point if the parent was rebased since).
    for n in live:
        best, best_dist = None, None
        for p in live:
            if p == n or branches[p]["sha"] == branches[n]["sha"]:
                continue
            # a branch that descends from n can never be n's parent
            if git("merge-base", "--is-ancestor", n, p)[0] == 0:
                continue
            is_anc = git("merge-base", "--is-ancestor", p, n)[0] == 0
            how = "ancestor"
            if not is_anc:
                rc, fp = git("merge-base", "--fork-point", p, n)
                if rc != 0 or not fp:
                    continue
                # fork-point of p..n only meaningful if it is beyond the base
                if git("merge-base", "--is-ancestor", fp, remote_base)[0] == 0:
                    continue
                how = "reflog_fork_point"
            dist = int(git("rev-list", "--count", f"{p}..{n}")[1] or 0) if is_anc else 10**6
            # parent must carry commits of its own beyond base
            if branches[p]["commits_ahead_of_remote_base"] == 0:
                continue
            if best is None or dist < best_dist:
                best, best_dist, best_how = p, dist, how
        branches[n]["stack_parent"] = best
        branches[n]["stack_parent_how"] = best_how if best else None

    _, cur = git("branch", "--show-current")
    _, ahead = git("rev-list", "--left-right", "--count", f"{base}...{remote_base}") if remote_base != base else (0, "0\t0")
    out = {
        "base": base,
        "remote_base": remote_base,
        "current_branch": cur or None,
        "base_checked_out_in": wt_by_branch.get(base),
        "main_worktree": wts[0]["path"] if wts else None,
        "worktrees": wts,
        "branches": sorted(branches.values(), key=lambda b: b["name"]),
        "gh_available": bool(gh),
        "note": "Run `git fetch origin` first so merged detection compares against the latest remote base.",
    }
    json.dump(out, sys.stdout, indent=2)
    print()


if __name__ == "__main__":
    main()
