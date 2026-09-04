# Intake - reading whatever arrives

The input to this skill is not a format. It is whatever the person had when
they decided to start: a written PRD, a paragraph in chat, a voice-note
transcript, a competitor's landing page, a Figma link, a repo someone abandoned
in March.

Treat all of them the same way: **extract, restate, split, confirm.** The shape
of the input changes what you can extract, not what you owe back.

## What each input shape is hiding

Every source is unreliable in its own direction, and knowing which way saves an
interrogation round.

| Input | What it usually has | What it is usually missing |
|---|---|---|
| **A written PRD** | features, screens, user stories | the failure behaviour, the data owner, why alternatives were rejected |
| **A one-line idea** | the motivating pain, honestly stated | everything else - and that is fine, it is the cheapest input to work from |
| **A transcript / meeting notes** | real constraints, said in passing | the decisions - people talk around them and never land one |
| **A competitor or reference product** | a concrete target to point at | which parts matter; "like X" usually means one feature of X |
| **A design file** | the surface, in detail | the state model behind the surface |
| **An abandoned repo** | what was already tried | why it stopped, which is the most useful fact available |

A PRD is the most dangerous of these, because it *looks* complete. A document
with forty numbered requirements and no rejected alternatives is a description
wearing a spec's clothes - it will pass a skim and fail the first hard
question. Treat its features as **stated requirements** and its architecture as
**unverified inference** unless it records why.

## The restate

Before any question, hand back what you understood, structured. Not a summary
of their words - a restatement in the spec's own vocabulary:

- **The problem**, as a situation somebody is in today, not a missing feature.
- **Who has it**, specifically enough to argue with.
- **What they do instead right now.** If the answer is "nothing", the problem
  may not be real; if the answer is "a spreadsheet", the spreadsheet is the
  competitor and the bar to clear.
- **What "working" looks like**, in an observable event.

Getting one of these wrong is common and cheap here. The same error found at
spec review costs the spec.

## Said vs. inferred

The core mechanic of this file, and the one that keeps the whole skill honest.

Write two labelled lists. Everything you know goes in exactly one of them.

```markdown
### Stated
- Users upload a CSV of transactions.
- The system emails them a monthly summary.
- It must work for their accountant, who is not technical.

### Inferred - confirm or correct
- Files are single-user, under ~10MB. (from "their accountant", not stated)
- One organisation per account; no sharing model yet.
- The summary is transactional email, not a marketing send.
- A failed import is retried silently rather than surfaced to the user.
```

Rules that make it work:

- **Every inference is confirmable in one word.** If the reader has to research
  their own product to answer, it was a question, not an inference.
- **Say where an inference came from** when it is not obvious. "(from 'their
  accountant')" is what lets the user see the reasoning was real rather than
  decorative.
- **Inferences that would change the architecture go first.** The retry
  behaviour above outranks the file size.
- **Never let an inference graduate silently.** It moves to *Stated* when the
  user confirms it, and the spec cites that. An unconfirmed inference that ends
  up in the spec as a requirement is how a team ships a product nobody asked
  for while everyone believes it was specified.

## Scope of the ask

One more split, done at intake and revisited at the end:

- **This project** - what is being specified now.
- **Adjacent, later** - real, wanted, explicitly not now. These become backlog
  rows with revisit conditions, which is groundwork's concern 11.
- **Not this product** - things a reader might assume are included. Naming
  three of these is worth more than ten more requirements, because it stops the
  scope argument that would otherwise happen in month two.

## When the input is a repo

If something already exists, read it before asking anything - here the
groundwork instinct applies and the code is evidence. Look for what was tried,
what was abandoned mid-way, and what the tests claim. Then ask the one question
the code cannot answer: **why did it stop?** The answer is usually the most
important constraint in the whole spec, and it is never written down.
