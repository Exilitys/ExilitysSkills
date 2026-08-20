---
description: Set up or route work through the project's context system and lanes
---

Invoke the `groundwork` skill.

Run its preflight first — check skill availability against the tiers in
`references/skill-map.md`, and report gaps before promising a workflow that
names skills the user does not have.

Then pick the mode:

- No `AGENTS.md`/`CLAUDE.md` and no `docs/` structure → **Mode A, bootstrap**.
- Has them, and a task just arrived → **Mode B, route** into a lane.
- Has them, and the question is whether they are still true → **Mode C, drift**.

Argument, if any: $ARGUMENTS

If the argument names a mode (`bootstrap`, `route`, `drift`), use it and skip
the inference. Otherwise infer from the repo, and ask when genuinely ambiguous.
