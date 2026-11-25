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

Symlink it into Claude Code's skills directory:

```bash
ln -s "$PWD/skills/stacked-rebase" ~/.claude/skills/stacked-rebase
```
