---
name: groundwork
description: Set up or maintain a project's agentic context system and coding workflow - the AGENTS.md/CLAUDE.md layer, the invariants and contract gate, the enforcement hooks, and the lane discipline that routes features, bugs, chores and spikes through the right skills. Use when starting a fresh project, when an existing repo's AI context is missing or stale, when deciding how a team should work with Claude Code, or when asked to make a workflow repeatable across projects.
---

# Groundwork

Two things, and they are the same thing: **where truth lives**, and **how work
moves**. A workflow without a context system re-derives the project every
session; a context system without a workflow rots because nothing consumes it.

## The one idea

> A rule a tool can check should be tool config, not prose.

Everything below follows from it. Documents that restate what code already says
go stale and then lie, which is worse than silence. So: enforce what you can,
write down only the *why* that no check can hold, and make the writing itself
checkable.

## Preflight - before either mode

This skill does not do the work; it routes to other skills that do. So the
first action, every time, is **check they exist.**

1. Read the session's available-skills list against the tiers in
   `references/skill-map.md`.
2. **Tier 1 missing -> stop and ask.** Name the plugin, give the install
   command, and offer the one-line fallback for each affected step. The user
   chooses install or degrade; you do not choose silently. A lane that names a
   skill nobody has is a lane the agent improvises and reports as followed.
3. **Tier 2 missing -> report, name the fallback, continue.**
4. Whatever is missing at the end, the lane table you write says `manual` for
   that step. Never write a row for a skill the user does not have.

## Two modes

**Which mode?** No `AGENTS.md`/`CLAUDE.md` and no `docs/` structure -> bootstrap.
Has them, and the user is doing a task -> route. Has them, and the question is
whether they are still true -> drift audit. When ambiguous, ask.

### Mode A - Bootstrap

Establish (or repair) the context system. Read `references/bootstrap.md` and
follow it. Summary:

1. **Inventory before writing.** Nine concerns; find where each already lives.
2. **Present the gap table and confirm.** On a mature repo most rows resolve to
   something that exists - write pointers, not duplicates. On a fresh repo
   every row is a gap and you generate all nine.
3. **Write only the gaps**, plus the routing table into `CLAUDE.md`.
4. **Lay the tooling floor** - `references/tooling-floor.md`.
5. **Offer the hooks** - `references/contract-gate.md`. Opt-in, shown first.

Never overwrite curated prose. Add lines; rewrite only lines this skill owns.

### Mode C - Drift audit

The repo has a context system and the question is whether it is still true.
Read `references/drift-audit.md`. Summary: run `assets/drift_report.py` for the
mechanical pass, run the integrity test, then read what is left and ask the
three questions no script can - is this rule now enforced by a tool, was a
decision made and never written, did a deferral's revisit condition fire.

Report, never gate. Fix what is false; leave what is merely old.

### Mode B - Route

A task arrived. Pick the lane, then follow it. Full definitions with skill
chaining in `references/lanes.md`.

| Lane | Trigger | Shape |
|---|---|---|
| **1 Slice** | new feature, user-visible capability | brainstorm, **contract check**, spec, *(gate)*, plan, worktree, build, verify, review, PR, sync |
| **2 Bug** | wrong behavior, failing test | **reproduce first**, root cause, failing regression test, minimal fix, verify |
| **3 Chore** | refactor, rename, dep bump | no spec; plan only if >3 files; **existing tests pass unchanged** |
| **4 Spike** | "will this even work" | throwaway, no docs, not merged - deleted or promoted to Lane 1 |

## The gate

The one hard stop. Before editing, check the path against the project's
**contract list** (`docs/architecture/invariants.md`, or wherever bootstrap put
it).

- **Touches a contract path -> STOP.** Spec, approval, then build.
- **Touches none ->** proceed in one session.

It is membership in a list, not a judgment about importance. A contract path is
one where breaking it is *cheap and silent*: port signatures, migrations, a
shared runtime script, design tokens, prompts - plus any deferred item carrying
a revisit condition.

**Every locked decision in a spec cites its source - file and date.** A
decision without provenance is a guess wearing a spec's clothes. The most
valuable thing a spec does is discover that the thing being asked for was
already decided against, and why.

## Non-negotiables while building

**Climb the ladder before writing any file.** Does this need to exist? Does it
already exist here? Does the stdlib do it? A platform feature? An installed
dependency? Can it be one line? Only then write it.

Rung 2 is the expensive one to answer with grep. Use the graph
(`references/memory-graph.md`).

**Two-strikes promotion.** The second time a pattern appears, extract it - and
add its guard in the same commit. A primitive without its invariant is half the
work, because the third occurrence is still possible.

**Mark deliberate corner-cuts** with a greppable comment naming the ceiling and
the upgrade path. Those are deferrals; harvest them into the backlog at sync.

**Evidence before assertions.** Run the command, read the output, then claim.

## References

| File | Read when |
|---|---|
| `references/bootstrap.md` | Mode A - the nine concerns, gap analysis, templates |
| `references/drift-audit.md` | Mode C - periodic "is this still true" pass |
| `references/lanes.md` | Mode B - full lane definitions, skill chaining per phase |
| `references/contract-gate.md` | Designing the contract list and generating hooks |
| `references/tooling-floor.md` | Deciding what becomes config instead of prose |
| `references/skill-map.md` | **Preflight availability tiers**, which skill owns which phase, collisions |
| `references/memory-graph.md` | Graph-based code search and the three memory tiers |
| `assets/hooks/` | Hook scripts to adapt into a target repo |
