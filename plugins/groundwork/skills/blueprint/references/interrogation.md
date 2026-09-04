# Interrogation - asking only what changes the build

The purpose of this phase is not to understand the product completely. It is to
**remove the ambiguity that would otherwise be resolved by an implementer
guessing.** Those are different targets, and the second one terminates.

## The filter

Before asking anything, run the question through one test:

> **Would a different answer produce a different build?**

If both answers lead to the same code, it is trivia - it belongs in the product
doc later, not in this conversation. If one answer changes a data shape, a
seam, an ownership boundary, or what happens when something fails, ask it now,
because that is exactly what an implementer will otherwise decide alone at
2am.

## The taxonomy - what is actually load-bearing

Most specs fail on the same handful of unknowns. Work these before anything
else.

### 1. The person and the alternative

- Who has this problem, specifically enough to disagree with?
- **What do they do today instead?** The current workaround is the real
  competitor and the bar the build has to clear. "Nothing" is a warning sign;
  "a spreadsheet" is a specification.
- What would make them go back to doing it the old way?

### 2. The one thing

- If everything else worked and this one thing did not, would the project be
  worthless? That is the core assumption, and the first slice exists to prove
  it.
- Conversely: what could be cut entirely and still leave something worth
  shipping?

### 3. Data - shape, owner, lifetime

The questions implementers most often answer by guessing:

- What is the unit of data, and who owns a given row - a user, an org, a team?
- Who can see it, and does that change over time?
- What is the source of truth when two things disagree?
- What must never be lost, and what is disposable?
- Is anything regulated, personal, or exportable on request?

### 4. Failure behaviour

Almost never in a PRD, almost always decided by whoever writes the code:

- What happens when the third party is down?
- Is a half-finished operation retried, rolled back, or surfaced?
- Who finds out when something breaks - the user, an inbox, nobody?
- What is allowed to be eventually consistent, and what is not?

### 5. Scale and shape of load

- How many users, rows, requests - **today**, not in the pitch deck.
- What breaks first at 10x? Ask for the number, not the adjective. "Fast" is
  not an answer; "a report in under 5s for 100k rows" is.
- Is the load steady, bursty, or scheduled?

### 6. The real constraint

- A date that is real (a demo, a contract, a season) versus one that is hoped.
- Budget, in money or in people.
- A platform, language, or vendor that is non-negotiable, and **why** - an
  existing team skill is a different constraint from a signed contract.

### 7. Out of scope, stated out loud

Three things a reader would reasonably assume are included and are not. This
is the cheapest section in any spec and prevents the most argument.

## Routing

| Skill | Use it for | If missing |
|---|---|---|
| `grill-me` | the adversarial pass - hunting the assumption that has not been examined | ask the taxonomy above yourself, and say the pass was manual |
| `brainstorming` | the solution space, when the shape is genuinely open | list three approaches and their trade-offs before picking |
| `zoom-out` | when the ask is a feature but the problem smells structural | ask what else in the system this touches |

Run `brainstorming` **before** converging on a shape, never after. Its value is
the alternatives; asked after a decision it produces retroactive justification
for the thing already chosen.

Run `grill-me` twice in the overall flow: once here on **the idea**, and again
in step 5 on **the written spec**. They find different things - the first finds
missing constraints, the second finds internal contradictions.

## The stopping rule

> Stop when the remaining unknowns would not change the first slice.

Everything past that line is a **deferral with a revisit condition**, not a
blocker - the same discipline groundwork applies to deferred decisions:

```markdown
- **Multi-region storage.** Not decided. Revisit when a customer outside the
  current region signs, or when p95 read latency exceeds 400ms.
```

Written that way it stops being an open question and becomes a tracked one.

Two failure directions, both real:

- **Under-interrogated.** The spec reads smoothly and every hard question was
  left to the build. Symptom: no section on failure behaviour, no numbers.
- **Over-interrogated.** Round four of questions, the user has lost interest,
  and nothing has been written down yet. Symptom: questions whose answers would
  not change any code that ships this quarter.

If a round of questions produces no change to the shape of the build, that
round was the last one.

## Recording the answers

Answers do not live in the chat log; they die there. Every answer that settles
something becomes either a **stated requirement** or the *because* line of a
decision record in `spec-format.md`. An answer that is neither was trivia -
which means the filter at the top of this file should have caught it.
