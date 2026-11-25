---
name: grill
description: Grill the user relentlessly about a plan, decision, or idea until shared understanding, one round of questions at a time. Use when the user wants to stress-test their thinking, says "grill me", "interview me", or "poke holes in this", or when another skill needs an interview. In a repo it also builds the domain model, writing GLOSSARY.md and ADRs as decisions land.
---

Interview the user relentlessly until you reach a shared understanding. Map this as a **design tree**: every decision branches into the decisions that hang off it.

## Rounds

The **frontier** is every decision whose prerequisites are already settled: the questions you can ask _now_ without guessing at answers you haven't heard yet. Ask the whole frontier in one round, then wait for the user's answers before the next round.

Format a round like so:

```
❓ **Q1** - **<question title>**: <question body, might be multiple paragraphs, including multiple choices>

➡️ <your recommended answer>

---

❓ **Q2** - **<question title>**: <question body>

➡️ <your recommended answer>
```

- Ask in plain chat text. Do not use `AskUserQuestion` or any picker UI: open questions answered in the user's own words are the point.
- Word each question so "yes" accepts your recommended answer. If your recommendation argues against the question as worded, reword the question.
- Answers reshape the tree. Recompute the frontier and ask the next round. A question that depends on another question still open in this round belongs to a _later_ round.
- If the user says an answer should have changed another question, reopen that branch in the next round.

## Facts vs. decisions

Finding _facts_ is your job, never the user's. When a frontier question needs a fact from the environment (filesystem, code, tools), dispatch a sub-agent with a fresh context to find it. Don't block on it: only the questions downstream of the fact wait; ask the rest of the frontier now.

The _decisions_ are the user's. Put each to them and wait. **Never answer your own questions**, even when another skill invoked you to "resolve" something.

## Domain model (when in a repo)

Skip this section outside a working directory. Inside one, build and sharpen the project's domain model as you go. Write things down the moment they crystallise, not at the end.

- **Challenge against the glossary.** If the user's term conflicts with `GLOSSARY.md`, say so immediately: "Your glossary defines 'cancellation' as X, but you seem to mean Y. Which is it?"
- **Sharpen fuzzy language.** For vague or overloaded terms, propose one canonical term: "do you mean the Customer or the User?"
- **Probe with scenarios.** Invent concrete edge cases that force the user to be precise about boundaries between concepts.
- **Cross-check the code.** When the user states how something works, check the code. Surface contradictions: "Your code cancels whole Orders, but you said partial cancellation is possible."
- **Update `GLOSSARY.md` inline** when a term resolves. Format in [GLOSSARY-FORMAT.md](./GLOSSARY-FORMAT.md). It is a glossary only: no implementation details, specs, or scratch notes.
- **Offer ADRs sparingly**, only when the decision is hard to reverse, surprising without context, AND a real trade-off. Format in [ADR-FORMAT.md](./ADR-FORMAT.md).

Files live at the repo root `GLOSSARY.md` and `docs/adr/`. If `GLOSSARY-MAP.md` exists the repo has multiple contexts; read it and infer which one applies (ask if unclear). Create files lazily, only when there is something to write.

## Finishing

The session is done when the frontier is empty: every branch visited, nothing silently assumed. Then summarise the shared understanding and **ask the user to confirm it. Do not implement, edit code, or start any follow-up work until they explicitly say so.** An empty frontier is not permission.
