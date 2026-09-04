---
description: Turn an idea, PRD or pile of requirements into an interrogated, decision-recorded spec
---

Invoke the `blueprint` skill.

Take the input in whatever shape it arrived — a PRD, a paragraph, a transcript,
a reference product, an abandoned repo — and work the flow:

1. **Restate it back**, structured, and **split what was stated from what you
   inferred.** Two labelled lists. Unlabelled inference is how a team ships a
   product nobody asked for while everyone believes it was specified.
2. **Interrogate what changes the build** — `grill-me` for the adversarial
   pass, `brainstorming` where the shape is genuinely open. Ask the
   load-bearing unknowns: the user and their current workaround, the one thing
   that must work, who owns the data, failure behaviour, real numbers, what is
   out of scope. Stop when the remaining unknowns would not change the first
   slice.
3. **Decide the shape**, recording each decision as chosen / rejected /
   because / revisit-when / provenance. A record with no rejected alternatives
   was a default — say so rather than dressing it as a decision.
4. **Write it** from `assets/spec-template.md` into `docs/prd/prd.md`, ending
   with the first slice: the smallest build that could prove the core
   assumption wrong.
5. **Stress it** — `grill-me` on the written spec this time — then run the
   checker and **paste its output**:

```
python assets/check_spec.py docs/prd/prd.md
```

6. **Get explicit sign-off**, then hand off to `/groundwork`, naming what was
   deferred and what blueprint did *not* decide. Silence reads as settled.

Do not write the root `AGENTS.md`/`CLAUDE.md`, the hooks or the lane table —
those are groundwork's, and writing them here creates two homes for one truth
on day one.

If interrogation reveals this is a one-afternoon change to an existing system,
say so and route it to `/groundwork` as a lane instead. A spec for a two-file
change teaches everyone the process is theatre.

Input, if given: $ARGUMENTS
