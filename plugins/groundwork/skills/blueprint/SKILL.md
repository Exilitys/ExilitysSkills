---
name: blueprint
description: Turn a raw idea, PRD, feature request or pile of notes into an interrogated, decision-recorded technical specification a team can build from - then hand the project to groundwork to set up its context system. Use when starting a new project or a large new subsystem, when the user arrives with an idea, requirements doc, product brief or "I want to build X", when a spec needs stress-testing before anyone writes code, or when a request is too vague to plan from. Not for routing an already-specified task, and not for bootstrapping context in a repo that already has a spec.
---

# Blueprint

The stage before groundwork. **Blueprint decides what gets built and why;
groundwork decides where truth lives and how work moves.** Two skills because
they have opposite first instructions: groundwork reads a repo for evidence,
blueprint asks a human, because on a new project there is nothing to read.

## The one idea

> A spec is a record of decisions, not a description of a product.

A description tells you what the thing is. A decision tells you what was
chosen, what was rejected, and what would change the answer. Only the second
survives contact with the build, because when reality disagrees with the spec
the team needs to know whether they are breaking a considered decision or
correcting an assumption nobody made on purpose.

The working rule: **a statement that rules nothing out is description. Cut it,
or turn it into a decision.**

## What counts as enough detail

The user asking for this usually wants "extreme detail", and they are right to
- but detail spent on the wrong things is what makes specs go unread. The test:

> **Two competent engineers building from this spec, independently, produce
> systems that fit together.**

That earns extreme detail on the seams - data shapes, interfaces, ownership,
failure behaviour, the states a thing can be in - and forbids it on anything
their compilers would have agreed on anyway. Twelve pages enumerating CRUD
endpoints while the concurrency model goes unstated is a spec that fails the
test at full length.

## Preflight - before anything

Same posture as groundwork: this skill routes to other skills, so **check they
exist first.** Read the session's skill list against `references/skill-map.md`.

Report what is missing, name the fallback for each, and continue - none of
these are hard blockers, but a session that silently improvises `grill-me` and
reports the spec as stress-tested has produced the exact artifact this skill
exists to prevent.

## The flow

### 1. Intake - take the input in whatever shape it arrives

A PRD, three sentences in chat, a meeting transcript, a competitor's URL, a
screenshot, a half-built repo. Full handling in `references/intake.md`.

Two things happen here and nothing else:

**Restate it back**, in your words, structured. Cheapest correction point in
the whole process - a misread premise caught here costs one message and caught
at the spec review costs the spec.

**Split what was said from what you inferred.** Two explicit lists, labelled.

> **Stated.** Users upload a CSV; the system emails a summary.
> **Inferred (confirm or correct).** Files are under 10MB. One user per
> account. Email is transactional, not marketing. Failure is retried, not
> surfaced.

This is the single highest-value step in the skill. An agent handed a thin idea
will fill the gaps with plausible features and the user will approve them
because they look reasonable - and then the project is building someone else's
product. Inference is not the problem; **unlabelled** inference is.

### 2. Interrogate - grill only what changes the build

`references/interrogation.md` has the question taxonomy and the routing.

Route to `grill-me` for the adversarial pass and `brainstorming` for the
solution space where the shape is genuinely open. Ask about the load-bearing
unknowns - who the user is and what they do today instead, the one thing that
must work, who owns the data, what breaks at 10x, what is deliberately out of
scope, the constraint that is real (a date, a budget, a platform).

**The stopping rule:** stop when the remaining unknowns would not change the
first slice. Specs die of endless discovery more often than of thin
interrogation, and an unknown that only bites in month six is a deferral with
a revisit condition, not a blocker.

**Ask the project-scale rung 1.** Does this need to exist? Is there something
off the shelf that does it? A spec whose honest conclusion is "buy this
instead" is the most valuable output this skill can produce, and it is never
reached by a process that assumes the project is happening.

### 3. Decide the shape

Now the technical half: stack, architecture, data model, the seams, the
failure behaviour. `references/spec-format.md` carries the section list.

Every decision is recorded in the same shape, and it is the same provenance
discipline groundwork's gate already demands:

| Field | Why |
|---|---|
| **Chosen** | the decision |
| **Rejected** | the real alternatives, named |
| **Because** | the reason, tied to a constraint from step 2 - not taste |
| **Revisit when** | the condition that would overturn it |

A decision with an empty *rejected* row was not a decision, it was a default.
Say so - "default, not evaluated" is honest and tells the next reader how much
weight it carries.

Route to `codebase-design` for the module seams and interfaces, and to a
minimalism skill (`ponytail`) as the counterweight. **Spec time is when
over-engineering is cheapest to add and most expensive to remove** - every
speculative layer costs one line here and six months of maintenance later, so
the pass that deletes them belongs here more than anywhere downstream.

Where the stack is decided, pull in the craft skill for it if one is installed
- `matt-pocock` for TypeScript, `ui-styling` / `design-system.md` for frontend
component sourcing. Check availability; never name one you did not verify.

### 4. Write it

`assets/spec-template.md` is the scaffold; `references/spec-format.md` is what
each section must contain and how it fails. Product-level spec at
`docs/prd/prd.md`, the first slice at `docs/specs/`. Confirm the paths - they
are what groundwork's inventory will look for.

**End with the first slice.** A spec for a whole product is not buildable. Name
the smallest thing that proves the core assumption, and make it small enough to
be one Lane 1 pass.

### 5. Stress it, then check it

Run `grill-me` **on the spec**, not on the idea - different target, different
findings. Then the mechanical pass:

```bash
python assets/check_spec.py docs/prd/prd.md
```

It checks what a tool can decide: decisions missing their rejected
alternatives, requirements no one could falsify, deferrals with no revisit
condition, leftover `TBD`s, weasel words standing in for numbers. Paste its
output. The same rule the rest of this repo runs on - a rule a tool can check
should not be left to a careful reading at the end of a long session.

### 6. Approve, then hand off

Get explicit sign-off. Then `references/handoff.md`: the project goes to
**groundwork Mode A**, which inventories what you just wrote, resolves concerns
1, 2 and 11 to it rather than generating placeholders, and sets up the context
system, the lanes and the gate around it.

Say plainly what blueprint did **not** decide, so groundwork does not read
silence as settled.

## Ownership - the line between the two skills

| Owns | Skill |
|---|---|
| `docs/prd/`, `docs/specs/`, the decision records | **blueprint** |
| The root `AGENTS.md`/`CLAUDE.md`, hooks, integrity test, lanes, contract list | **groundwork** |

Blueprint never writes the root file. Groundwork never invents a requirement.
Two homes, one direction of travel - the same one-concern-one-home rule
groundwork applies to everything else, applied to the pair of skills.

## References

| File | Read when |
|---|---|
| `references/intake.md` | Step 1 - normalising any input shape, said vs. inferred |
| `references/interrogation.md` | Step 2 - the question taxonomy, routing, the stopping rule |
| `references/spec-format.md` | Steps 3-4 - the document's sections, caps, and how each fails |
| `references/handoff.md` | Step 6 - the seam to groundwork, and what it expects to find |
| `references/skill-map.md` | Preflight - which skills this routes to, and the fallbacks |
| `assets/spec-template.md` | Step 4 - start here rather than from an empty file |
| `assets/check_spec.py` | Step 5 - before claiming the spec is ready |
