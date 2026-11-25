# my-skills

Central repo for my AI tooling: skills I write, skills I vendor, and reusable rules / `CLAUDE.md` material.

## Layout

| Path | Purpose |
|---|---|
| `skills/` | Skills I author. One folder per skill, each with a `SKILL.md` (plus `scripts/`, `evals/`). |
| `vendor/` | Third-party skills copied in, with provenance tracked in `UPSTREAM.md`. |
| `claude-md/` | Example / reusable `CLAUDE.md` and `AGENTS.md` fragments. |
| `rules/` | Modular rule files (e.g. for `.claude/rules/`). |
| `test-artifacts/` | **Gitignored.** Eval runs, benchmarks and logs from testing skills. |

## Using a skill

Claude Code only, for now. Skills are loaded by symlinking each skill folder (any folder containing a `SKILL.md`) into `~/.claude/skills/`. Run from the repo root.

Load a single skill:

```bash
mkdir -p ~/.claude/skills
ln -sfn "$PWD/skills/stacked-rebase" ~/.claude/skills/stacked-rebase
```

Load **all** my skills (`vendor/` is reference only and is not loaded):

```bash
mkdir -p ~/.claude/skills
for f in skills/*/SKILL.md; do
  dir="$(dirname "$PWD/$f")"
  ln -sfn "$dir" ~/.claude/skills/"$(basename "$dir")"
done
```

Because they are symlinks, `git pull` updates the skills in place. Re-run the loop after adding a new skill. Restart Claude Code (or start a new session) to pick up new skills.
