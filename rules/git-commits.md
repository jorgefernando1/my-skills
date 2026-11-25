# Git commits

Whenever you create a git commit, use the `commit` skill and follow its `FORMAT.md`: a Conventional Commits subject and a body that tells the story (why, what was found, why this approach).

- When working a task end to end for a PR the user will only review at the end, commit after each logical step instead of once at the end. Every commit should hold one concise piece of work, and together they should read as the solution the PR brings.
- When the user asks you to leave changes uncommitted, do not commit. When they later ask you to commit them, run the `commit` skill's procedure to split the changes into a meaningful series.
- Never write vague messages (`fix bug`, `wip`, `update`) and never invent history you did not witness.
