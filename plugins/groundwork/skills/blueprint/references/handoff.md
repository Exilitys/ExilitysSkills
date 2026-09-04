# Handoff - blueprint to groundwork

The two skills meet at a **file on disk**, not a conversation. That is the
whole integration: blueprint writes the spec where groundwork's inventory
already looks, and groundwork finds it the way it finds anything else.

## What groundwork does with what you wrote

groundwork's bootstrap maps eleven concerns and asks, for each, *where does
this already live?* A blueprint-produced spec answers three of them outright:

| Concern | Without blueprint | With it |
|---|---|---|
| 1 - What we're building, and for whom | a placeholder, because nothing exists to describe | **pointer** to `docs/prd/prd.md` |
| 2 - How the system is structured | thin until code exists | **pointer** to the decisions and seams sections |
| 11 - Decision provenance | empty on a new project | **the decision records**, already in the required shape |

This is why the seam needs no code. groundwork's `bootstrap.md` already lists
`docs/prd/`, a spec, or a README as the typical home for concern 1 - writing
there means its inventory resolves the row to a pointer instead of generating a
duplicate. **Two documents describing one project is exactly the drift
groundwork exists to prevent**, so the correct outcome is that groundwork
writes *less* because blueprint ran.

## Where to write

| Artifact | Path | Owner after handoff |
|---|---|---|
| Product-level spec | `docs/prd/prd.md` | blueprint (re-run to amend) |
| First slice spec | `docs/specs/001-<slug>.md` | Lane 1 |
| Deferred items with conditions | inside the spec, then `docs/backlog.md` | groundwork's sync step |

Confirm the paths with the user rather than assuming - a repo with an existing
convention wins, and groundwork's placement rules ("no new top-level folders
unless the repo has nowhere for a concern to go") apply here too.

## What blueprint must never write

The root `AGENTS.md`/`CLAUDE.md`, the hooks, the integrity test, the lane
table, the contract list. Those are groundwork's, and a blueprint that writes
them produces the two-homes-for-one-truth failure on day one.

The line is clean: **blueprint decides what gets built; groundwork decides
where truth lives and how work moves.**

## The handoff message

When the spec is approved, say four things:

1. **What was decided** - the decision numbers, not a re-summary.
2. **What was deliberately deferred**, with each revisit condition.
3. **What blueprint did not decide**, explicitly. Silence reads as settled, and
   groundwork will treat an unspecified area as a resolved one.
4. **The next command** - groundwork Mode A, to bootstrap the context system
   around the spec.

```
Spec approved: docs/prd/prd.md (D-001..D-012, 4 deferred).
Not decided here: auth provider, deployment target.
Next: /groundwork - it will inventory this repo, find the spec, and set up the
context system, lanes and gate around it.
```

## Feeding the contract gate

One useful thing to hand over deliberately. groundwork's contract list wants
paths where breaking something is *cheap and silent*, plus **any deferred item
carrying a revisit condition.** A blueprint spec produces both:

- The seams from the interfaces section are the first contract paths, once code
  exists at them.
- Every Deferred row is a non-path contract trigger by definition.

Name them in the handoff so groundwork's step 6 starts from a real list rather
than the empty one a fresh project usually gets.

## Re-entry - when the spec turns out to be wrong

The build will contradict the spec. That is normal and is not a failure of
either skill; what matters is which one handles it:

| Situation | Goes to |
|---|---|
| A decision was wrong, or its revisit condition fired | **blueprint** - amend the record, add a superseding entry, keep the old one visible |
| The docs no longer describe the code | **groundwork Mode C** - drift audit |
| A new large subsystem needs specifying | **blueprint** again, scoped to that subsystem |
| A task needs routing into a lane | **groundwork Mode B** |

Never delete a superseded decision. The record of what was chosen *and later
overturned* is the most expensive knowledge the project owns, and it is the
thing a rewrite six months later will otherwise re-derive from scratch.
