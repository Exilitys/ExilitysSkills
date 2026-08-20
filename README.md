# ExilitysSkills

A Claude Code plugin marketplace. One plugin so far.

```bash
/plugin marketplace add Exilitys/ExilitysSkills
/plugin install groundwork@exilitys-skills
```

---

## groundwork

**Where truth lives, and how work moves** — and they are the same problem. A
workflow without a context system re-derives the project every session; a
context system without a workflow rots, because nothing consumes it.

Most "AI context" advice produces a pile of markdown that is accurate for a
week. groundwork is built on one idea instead:

> A rule a tool can check should be tool config, not prose.

Everything follows from that. Enforce what you can, write down only the *why*
that no check can hold, and make the writing itself checkable.

### What you get

| Piece | What it does |
|---|---|
| **Three modes** | Bootstrap a context system, route a task into a lane, or audit whether the docs are still true |
| **Four lanes** | Slice / Bug / Chore / Spike — the lane sets the ceremony, so a typo fix is not over-planned and a migration is not under-planned |
| **The contract gate** | A short list of paths where breaking things is *cheap and silent*. Touch one → spec first. Enforced by a hook, not by hoping |
| **Integrity tests** | Working Vitest and pytest templates that fail when your docs name something that does not exist |
| **Drift report** | Finds context files whose subject moved after they were last touched |
| **Adoption report** | Measures whether the workflow is actually followed, or just documented |

### Commands

| Command | Use |
|---|---|
| `/groundwork` | Bootstrap, or route the task you are starting. Infers the mode from the repo |
| `/groundwork-drift` | "Is any of this still true?" — run after a merge-heavy stretch |
| `/groundwork-hooks` | Install the contract gate + session-start hooks into *this* repo |

The skill also loads on its own when you ask to set up project context, make a
workflow repeatable, or fix a repo whose AI docs have gone stale.

---

## How to use it

### On a fresh repo

```
/groundwork
```

It inventories what exists before writing anything, then shows you a gap table
— **concern | resolves to | action** — and waits. On an empty repo every row is
a gap and it generates all of them. On a mature repo most rows resolve to
something you already have, and it writes pointers instead of duplicates.

That confirmation step is where you catch its mistakes. Take the argument
seriously; a proposal that contradicts the project philosophy is a proposal
worth rejecting, and the correction is information.

### On an existing repo, starting a task

```
/groundwork
```

It picks a lane and announces it. The lane decides the ceremony:

- **Lane 1 · Slice** — brainstorm → contract check → spec → *gate* → plan →
  worktree → build → verify → review → PR → sync
- **Lane 2 · Bug** — reproduce **first** → root cause → failing regression test
  → minimal fix → verify
- **Lane 3 · Chore** — no spec; plan only if >3 files; **existing tests must
  pass unchanged** (if a test had to change, behavior changed, and it is not a
  chore)
- **Lane 4 · Spike** — throwaway, not merged; deleted or promoted to Lane 1

### Every so often

```
/groundwork-drift
```

Stale docs do not go quiet — they start lying, with the authority of something
that was once checked. This finds the lying ones.

---

## The gate

The one hard stop. Before editing, the path is checked against the contract
list:

```
backend/domain/ports/     backend/alembic/     backend/static/bridge.js
frontend/src/app/globals.css                   docs/prompts/
```

*(example — yours will differ)*

- **Touches one → STOP.** Spec, approval, then build.
- **Touches none →** proceed in one session.

It is membership in a list, not a judgment about importance. A contract path is
one where breaking it is **cheap and silent**: port signatures, migrations, a
shared runtime script, design tokens, prompts — plus any deferred decision
carrying a revisit condition.

`/groundwork-hooks` makes this a real `PreToolUse` hook rather than a sentence,
because the sentence has a known failure mode: a session in a hurry skims it.
The hook reads the path list *from your invariants doc*, so there is exactly one
list — never one in prose and one in code that quietly disagree.

Hooks install **per repo, not globally**. Contract paths differ per project, and
a gate firing in repos that never opted in is the first thing anyone uninstalls.

---

## Dependencies

groundwork routes to other skills rather than reimplementing them, so it checks
availability **before** promising a workflow. A lane that names a skill you do
not have is a lane the agent quietly improvises and then reports as followed.

- **Tier 1 — [superpowers](https://github.com/obra/superpowers)** owns
  brainstorming, planning, execution, TDD, debugging, verification, review, and
  worktrees. Missing it does not fail shut: groundwork reports the gap, offers
  the install, and falls back to a one-line version of each step if you say
  continue.
- **Tier 2 — recommended.** Scope, audit, check, document, sync, `grill-me`,
  `diagnose`, `prototype`, `handoff`. Each degrades to a named manual fallback.
  The one that matters most is **sync** — without it, context never folds back,
  which is what rots the system.
- **Tier 3 — craft.** UI, styling, testing, minimalism skills. Absence is never
  a blocker.

Install superpowers:

```bash
/plugin marketplace add obra/superpowers
/plugin install superpowers
```

---

## The parts that carry more than their length suggests

**Climb the ladder before writing any file.** Does this need to exist? Does it
already exist here? Stdlib? Platform feature? Installed dependency? One line?
Only then write it. Rung two is the expensive one to answer with grep — that is
what the context system is *for*.

**Two-strikes promotion.** The second time a pattern appears, extract it — and
add its guard in the same commit. A primitive without its invariant is half the
work, because the third occurrence is still possible.

**Every locked decision cites its source — file and date.** A decision without
provenance is a guess wearing a spec's clothes. The most valuable thing a spec
does is discover that the thing being asked for was already decided against,
and why.

**Evidence before assertions.** Run the command, read the output, then claim.

---

## Honest limitations

- **Adoption is the hard part, not authoring.** Measured on the repo groundwork
  was built in: **13% of code-editing sessions announced a lane**, with a
  SessionStart hook printing the lane table *every session*. Being visible is
  not being used. `/groundwork-drift` reports this number so you can see it
  rather than assume it.
- **The drift report is a coarse heuristic.** It compares commit recency; it
  cannot read meaning. It reports and never gates, because a gate on a signal
  this rough gets disabled within a week and takes the honest signal with it.
- **The integrity test only checks names and paths.** It catches a doc naming a
  class that never existed. It cannot catch a doc that describes real classes
  doing the wrong thing.
- **Windows-first.** Written and tested on Windows with Python 3.11+; the
  scripts avoid shell assumptions but have had less exercise elsewhere.

---

## Repo layout

```
.claude-plugin/marketplace.json     marketplace manifest
plugins/groundwork/
  .claude-plugin/plugin.json
  commands/                         /groundwork, -drift, -hooks
  skills/groundwork/
    SKILL.md                        preflight, modes, the one idea
    references/
      bootstrap.md                  Mode A: nine concerns, gap analysis
      claude-md-template.md         drafting the root file: sections, trim test
      lanes.md                      Mode B: full lane definitions
      drift-audit.md                Mode C: "is this still true"
      contract-gate.md              designing the list, generating hooks
      tooling-floor.md              what becomes config instead of prose
      skill-map.md                  preflight tiers, phase ownership
      memory-graph.md               graph search, memory tiers
    assets/
      hooks/                        contract_gate.py, session_start.py
      tests/                        integrity templates (Vitest + pytest)
      drift_report.py               Mode C mechanical pass
      lane_adoption.py              does anyone follow the workflow
```

## License

MIT — see [LICENSE](LICENSE).
