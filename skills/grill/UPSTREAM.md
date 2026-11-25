# Adapted from mattpocock/skills

Merges `grilling`, `grill-me`, `grill-with-docs` and `domain-modeling` (see `vendor/mattpocock-skills/`, plugin 1.3.2) into one skill.

Changes from upstream:
- No wrapper skills and no skill-calls-skill chain (upstream documents that nested loads are unreliable).
- Domain-modeling is an inline section, active only inside a repo.
- Explicit rule: never implement before the user confirms shared understanding.
- Explicit rule: no `AskUserQuestion`.
- `GLOSSARY-FORMAT.md` and `ADR-FORMAT.md` copied unchanged.
