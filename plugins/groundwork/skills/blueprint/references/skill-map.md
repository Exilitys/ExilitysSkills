# Skill map - what blueprint routes to

Same preflight rule as groundwork: **check availability before promising a
step.** A phase that names a skill nobody has is a phase the agent improvises
and then reports as done, which is worse than doing it manually on purpose.

Check the session's own skill list first - it is already in context. Never
infer that a skill exists because its capability sounds standard, and **never
invent a name to fill a row.** A row with nothing behind it reads `manual`.

## The routing table

None of these are hard blockers. Blueprint's discipline is the question
taxonomy and the decision-record format, both of which are prose and survive
every skill being absent.

| Phase | Skill | What it adds | Fallback if missing |
|---|---|---|---|
| Step 2 - interrogate | `grill-me` | the adversarial pass; finds the assumption nobody examined | work `interrogation.md`'s taxonomy by hand, and say the pass was manual |
| Step 2 - open shape | `brainstorming` | the solution space, before converging | list three approaches with trade-offs, then choose |
| Step 2 - structural smell | `zoom-out` | when the ask is a feature but the problem is systemic | ask what else in the system this touches |
| Step 3 - seams | `codebase-design` | deep-module vocabulary for the interface boundaries | write signatures and ask what each hides |
| Step 3 - counterweight | `ponytail` (minimalism) | deletes the speculative layer while it is still one line | ask of each component: what breaks if we cut it |
| Step 3 - stack craft | `matt-pocock` (TypeScript), `ui-styling`, others | idiom for the chosen stack | note the stack decision and leave idiom to the build |
| Step 5 - stress | `grill-me` again, on the spec | internal contradictions, not missing constraints | re-read the spec against the falsifiability table |
| Step 6 - visualise | `archify` | the spec, system design and architecture drawn, as the review instrument | draw it by hand in Mermaid - `visualise.md`. Do not skip it; the diagram is doing review work |
| Step 6 - handoff | `groundwork` | the context system around the approved spec | write the root file by hand; slower and it drifts |

## Ordering that matters

**`brainstorming` before converging, never after.** Its output is
alternatives; run after a decision it produces justification for the choice
already made, which is worse than not running it - it launders a default into a
decision.

**`ponytail` after the shape exists, before the spec is written.** Too early it
has nothing to cut; too late the layer is in the document and deleting it feels
like losing work.

**`archify` after the spec is stressed, before it is reviewed.** A diagram
drawn after acceptance documents a decision nobody could see when they made it.
And never report a drawing as produced by `archify` when it is not installed -
say it was drawn by hand.

**`grill-me` twice, on two different targets.** The idea, then the written
spec. Running it once on the idea and calling the spec stress-tested is the
most common way this flow degrades.

## What blueprint does not route to

The build-loop skills - planning, executing, TDD, review. Those belong to
groundwork's lanes, after the handoff. A blueprint session that starts writing
implementation plans has skipped the approval gate, and the plan is built on a
spec the user never signed off.

The one exception worth naming: if interrogation reveals the whole thing is a
one-afternoon change to an existing system, **stop and say so.** Route it to
groundwork Lane 1 or Lane 3 directly. A spec for a two-file change is ceremony
that teaches everyone the process is theatre.
