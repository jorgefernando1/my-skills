# Commit format

A commit message tells the story of one piece of work. A reviewer who only sees the finished PR reads the history instead of the live session, so the message must carry what the session knew: why the change exists, what was found, and why this approach was chosen.

## Message

```
<type>(<scope>): <imperative summary>

<why: the problem or motivation, in terms the reviewer can follow cold>

<what happened: what was tried, what was found, what was decided and why>

<optional: how to verify, commands that mattered>

<optional footers>
```

### Subject

- Conventional Commits shape: `type(scope): summary`. Scope is optional and is a noun for the area touched.
- Types: `feat`, `fix`, `refactor`, `perf`, `test`, `docs`, `build`, `ci`, `chore`, `revert`. If a change fits two types, it is two commits.
- Imperative mood ("Add", "Convert", "Reject"), no trailing period, 50 characters ideal, 72 max.
- Specific enough to stand alone in `git log --oneline`. "fix bug", "update code", "wip" and "address review" say nothing.
- `!` before the colon marks a breaking change.

### Body

Separate from the subject by a blank line. Wrap at 72 characters. Write prose, not a list of touched files; the diff already shows what changed, the message explains what the diff cannot.

1. **Why.** The problem, symptom or goal. Include the exact error text or failing command when there is one, so `git log --grep` finds this commit later, after removing anything sensitive (see "Sensitive information").
2. **What happened.** The investigation and the decision: what was tried, what ruled options out, why the chosen approach beat the alternatives, and any trade-off a reviewer would otherwise ask about. Dead ends that explain the final shape belong here.
3. **How to verify.** Only when non-obvious: the command, test, or manual check that shows it works. Record a command if it taught something reusable.

### Footers

`Refs: #123`, `Co-Authored-By: ...`, and `BREAKING CHANGE: <what breaks and what to do>` where applicable. Follow the repo's own conventions and trailers where they differ.

### Scale to the change

Length follows what the change needs, not a quota. A typo fix is a subject line alone. A non-obvious fix after an hour of debugging deserves the whole story. Never pad.

### Sensitive information

Commit history is permanent, widely copied and often readable by people who never saw the session. Keep anything that should not be shared out of the message, whatever its form. The following are examples, not a complete list; judge by the principle: **if the information is not yours to publish, or could cause harm or embarrassment if it spread, leave it out.**

- Secrets and access: passwords, tokens, API keys, private keys, connection strings, session cookies, internal URLs or hostnames that are not public.
- People: names, emails, phone numbers, handles, or any detail that identifies someone other than the user, including colleagues, customers and reporters.
- Customer or business data: customer names and details, account or order IDs, records, support tickets quoted verbatim, contract or pricing details, unreleased plans.
- Anything the user or the project marked confidential, or that you would not paste into a public issue.

When the story needs the detail, describe it generically or redact it: "a customer reported", `<redacted>`, `<token>`, `user@example.com`. Apply this to quoted error text and commands too: keep the useful, searchable part and replace the sensitive values. If a detail cannot be removed without losing the point, leave it out and keep the rest. When unsure whether something is sensitive, treat it as sensitive.

Public attribution of sources (a published article or a library author) is fine. Credit for people in a private context is not.

### Honesty

Only write what actually happened or what you verified. If the investigation is not known (for example, committing someone else's uncommitted work with no session context), state the why and the what the diff supports and stop there. Never invent a debugging story, test results, or motivation.

## Example

```
fix(search): stop crashing on queries with non-ASCII characters

Searching for "café" returned a 500. The logs showed:

    UnicodeEncodeError: 'ascii' codec can't encode character '\xe9'

The query string was being logged through a handler that opened its
file without an explicit encoding, so it fell back to the container's
POSIX locale (ASCII). The search itself was fine; only the audit log
write failed, and the exception propagated to the request.

Opening the audit log as UTF-8 fixes it at the source. Catching and
swallowing the logging error would have hidden the same problem for
any other handler, so I left error propagation alone.

Verify: `pytest tests/search/test_audit_log.py -k non_ascii`
```

## The series as a whole

The commits on a branch together tell the story of the PR, and each one carries a piece of the solution.

- **One logical step per commit.** Small enough to review in one sitting, whole enough to make sense alone.
- **Reads in order.** Preparation (refactors, renames, new seams) comes before the change that uses it. A reader going top to bottom should never meet something unexplained.
- **Each commit is a coherent step, ideally one that works.** Aim to leave the tree in a sensible state, but it is not a hard rule and nothing needs to be run to prove it. If tests or CI fail later, the fix becomes its own commit that continues the story (what failed, why, what the fix does), not an amend that hides it.
- **Tests travel with the code they cover.** Not in a trailing "add tests" commit.
- **No noise.** No `wip`, `fix typo in previous commit`, or bare `address review` commits. A follow-up commit is welcome when it has its own story: a failing test, a CI difference, or a review finding, with the cause and the fix explained.
- **No drive-bys.** Unrelated cleanups go in their own commit or their own PR.
