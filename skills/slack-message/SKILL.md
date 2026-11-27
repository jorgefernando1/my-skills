---
name: slack-message
description: Slack message drafts that explain technical work from the current conversation to an engineering team, a product manager, or the whole organization. Use when the user wants to write, announce or explain something on Slack or to those readers, or wants an existing draft for another audience.
---

# Slack message

Draft only: the user pastes and sends the message themselves.

## 1. Pick the audience and topic

Read the file for the audience, which holds its sections, length and technical depth:

| Audience | File |
|---|---|
| Team: the user's teammates or any engineering group | [TEAM.md](TEAM.md) |
| PM: the product manager | [PM.md](PM.md) |
| Org-wide: readers across the organization | [ORG.md](ORG.md) |

Ask which audience when the request does not settle it. When the conversation covers several topics and the user named none, ask which one.

## 2. Gather the facts

Build the message from the current conversation. Check its claims against whatever the conversation points to (diff, commits, PR, files, command output). Done when every fact you intend to use is either verified or noted as unverified.

When something the message depends on is missing (a date, who is affected, the impact, the decision needed), ask a few short questions before drafting. Dates, impact and certainty come only from the sources or the user: "probably" stays "probably", and an unknown date is said to be unknown or left out.

## 3. Draft

- **Conclusion first.** The first two lines carry the point for a reader who stops there.
- **Under a minute.** Short paragraphs or bullets, plain words, jargon only where this audience uses it.
- **Filled sections only.** Keep the audience file's order and drop any section with nothing to say.
- **Thread reply** only when there is technical depth the reader may want that would break the length target: draft it as a second, separate message.
- **Voice:** the user's own, as "I" or "we", direct and friendly. Little or no emoji. Names and @mentions only when the user asks.
- **Language:** English unless the user asks for another, section labels included.
- **Slack markup:** `*bold*` section labels, `_italic_`, `•` bullets one level deep, backticks for code, and triple-backtick blocks with no language tag. Slack does not render `#` headings or tables.

## 4. Remove what should not spread

Leave out secrets, credentials, private URLs, customer names and data, and anything the user or project marked confidential. Describe failures by what happened to the system, so that no person is blamed. When the point needs a removed detail, generalize it ("a customer", `<redacted>`). When unsure, leave it out and say so in the notes.

## 5. Deliver

1. The message in a four-backtick fenced block, so snippets inside survive and it copies as is.
2. The thread reply, if any, in its own four-backtick block.
3. Outside the blocks, brief notes: what you assumed, left out or removed (and why), and what is unverified. Report a removed secret by its kind, without repeating its value.

## Revising

Apply feedback such as "shorter" or "less technical" and deliver again. For another audience, read that file and rebuild from the facts of step 2; the earlier draft was cut to fit different readers.
