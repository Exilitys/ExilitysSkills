# The contract gate

## Why a gate at all

The expensive failure in a mature repo is not bad code. It is code built on a
decision that was already made and quietly overturned — a mockup reintroducing a
feature that was deferred with a condition, a migration for state that was
deliberately derived, a signature change that compiles and breaks a seam.

So the gate is about **decision provenance**, not process ceremony.

## Sizing it

Three options; the middle one is almost always right.

- **Hard** — every feature stops after the spec. Two sessions minimum, forever.
- **Sized** — stop only when the change touches a *contract*. This is the one.
- **Soft** — proceed unless something contradicts a doc. You discover bad
  premises at the end.

Sized only works if "is this a contract" is **not a judgment call.** Write the
list down literally. The agent checks membership; it does not assess importance.

## Deriving the contract list

A path belongs on it when breaking it is **cheap and silent** — no test fails,
nothing throws, and the damage surfaces later or elsewhere. Typical members:

| Kind | Why |
|---|---|
| Port / interface definitions | Change compiles; the seam fails at runtime. Layer linting sees the module, not the shape |
| Migrations | The one change reverting the commit does not revert |
| A shared runtime script every generated/embedded artifact loads | Breaks everything at once, invisibly |
| Design tokens / theme root | Every contrast and invariant test, plus a permanent two-place edit if mapping is skipped |
| Prompts | Correctness of everything generated from here on. Prompt regressions do not throw |
| Public API schemas / wire shapes | Consumers you cannot see |

**Plus one non-path trigger:** any deferred item carrying an explicit revisit
condition. Reviving it overturns a considered decision.

Keep the list short. A long list is a hard gate wearing a costume, and it will
be disabled within a week.

## Storing it

Put the list in a fenced block inside the project's invariants document, and
have the hook *read that block*. One source of truth, in prose the humans read
and the machine parses. Do not hardcode paths into the hook.

## The hooks

Two, and they do different jobs.

### `SessionStart` — orient, don't lecture

Print computed facts: branch, uncommitted count, plans with open work, whether
the code graph is stale, and a one-line lane + contract reminder.

**Compute everything.** This is why a hand-updated progress file is not worth
adopting — it is stale by the second session, while this cannot be.

Two traps, both found by running it:
- **Encoding.** Windows consoles are cp1252; arrows and middots crash the hook.
  Reconfigure stdout to UTF-8 *and* prefer ASCII.
- **Checkbox counts lie** if the project marks plans complete in a status header
  while leaving boxes unticked. Read the header first; it wins.

### `PreToolUse` on edit/write — block, with an exit

Read the contract list, match the target path, and allow when any of:

1. an override env var is set, or an override file exists
2. a spec exists on this branch

Otherwise exit non-zero with a message naming the matched path, the rule, and
**the override instruction**. A gate with no escape hatch gets deleted; a gate
that prints its own escape hatch gets used.

### Detecting "a spec exists on this branch" — get the base right

The subtle bug: picking the first integration branch that *exists*. A branch cut
from `development` has an ancient merge-base with `main`, so diffing against
`main` sweeps in every spec merged in between and **the gate silently passes**.

Compute the merge-base against each candidate and take the **most recent** one.
Then check that diff, plus unstaged, staged, and untracked files.

Verify all three paths before believing it works: contract path blocks, ordinary
path passes, override passes.

## What not to hook

Only the contract gate earns one. Lane selection does not — a hook that
misroutes a chore into Lane 1 is pure friction, and lane choice is cheap to get
wrong and expensive to over-enforce. Lanes live in prose; the gate lives in code.

## Portability

Hooks are the one part that does not travel cleanly — the path list is
repo-specific. So the skill **generates** them per project from the derived
contract list rather than shipping a fixed config. On a fresh project the list
is empty and the hooks are a no-op that grows with the repo.
