---
description: Turn an idea, PRD or pile of requirements into an interrogated, decision-recorded spec
---

Invoke the `blueprint` skill.

**This is a conversation, not a task you go away and complete.** The spec is
written *with* the user: propose decisions as choices with real alternatives
and a recommendation, agree them in clusters of three to five as you go, and
never let an unanswered question become a settled one. A finished document
presented for one approval at the end cannot be reviewed — only skimmed and
waved through, which is how unexamined decisions end up carrying a signature.

Take the input in whatever shape it arrived — a PRD, a paragraph, a transcript,
a reference product, an abandoned repo — and work the flow, stopping at each
**checkpoint**:

1. **Restate it back**, structured, and **split what was stated from what you
   inferred.** Two labelled lists. Unlabelled inference is how a team ships a
   product nobody asked for while everyone believes it was specified.
   *Checkpoint 1 — confirmed before any question gets asked.*
2. **Interrogate what changes the build** — `grill-me` for the adversarial
   pass, `brainstorming` where the shape is genuinely open. Ask the
   load-bearing unknowns: the user and their current workaround, the one thing
   that must work, who owns the data, failure behaviour, real numbers, what is
   out of scope. Stop when the remaining unknowns would not change the first
   slice. Ask three to five at a time, not fifteen — a wall of questions gets
   one answer covering three of them and twelve silent assumptions. Contribute
   what they have not raised, rather than only extracting what they know.
   *Checkpoint 2 — the core assumption and scope, before anything rests on
   them.*
3. **Decide the shape.** Put each decision to the user as two or three genuine
   options with their costs and your recommendation, *then* record it as
   chosen / rejected / because / revisit-when / provenance. A record with no
   rejected alternatives was a default — say so rather than dressing it as a
   decision, and note whether the user chose it or delegated it.
   *Checkpoint 3 — each cluster of three to five decisions, as they are made.
   This is the one that does the real work and the first one to get skipped.*
4. **Write it** from `assets/spec-template.md` into `docs/prd/prd.md`, ending
   with the first slice: the smallest build that could prove the core
   assumption wrong. Anything still unanswered goes in `Open questions`, not
   into a decision made on the user's behalf.
   *Checkpoint 4 — the first slice, before the document is finalised.*
5. **Stress it** — `grill-me` on the written spec this time — then run the
   checker and **paste its output**:

```
python assets/check_spec.py docs/prd/prd.md
```

6. **Draw it** — `archify` on the spec, system design and architecture, into
   `docs/architecture/`. Before the gate, not after: the diagram is a review
   instrument, and a reviewer finds a wrong boundary in a picture in seconds
   and misses it in twelve sections of prose. If `archify` is not installed,
   draw it by hand in Mermaid and say so — do not skip it. A design you cannot
   draw is not finished.
7. **A human reviews and accepts.** Hand over the review packet — the spec, the
   diagram, what changed since the last round, the open questions, and the two
   or three places you want them to look hardest — then **stop and wait.**
   Nothing downstream starts. *Checkpoint 5 — a re-read rather than a first
   read; surprises here mean an earlier checkpoint was skipped.*
   - Changes requested is the gate working. Change what was asked and only
     that, re-present the *diff*, come back here. No round limit.
   - **Never record your own approval.** When they accept, write
     `Status. Accepted <date> by @who` and the version they saw. An accepted
     spec may not carry open questions; the checker enforces both.
8. **Hand off** to `/groundwork`, naming what was deferred and what blueprint
   did *not* decide. Silence reads as settled.

Do not write the root `AGENTS.md`/`CLAUDE.md`, the hooks or the lane table —
those are groundwork's, and writing them here creates two homes for one truth
on day one.

If interrogation reveals this is a one-afternoon change to an existing system,
say so and route it to `/groundwork` as a lane instead. A spec for a two-file
change teaches everyone the process is theatre.

Input, if given: $ARGUMENTS
