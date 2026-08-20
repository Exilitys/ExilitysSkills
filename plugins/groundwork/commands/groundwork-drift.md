---
description: Audit whether the project's context files are still true
---

Invoke the `groundwork` skill in **Mode C** and follow
`references/drift-audit.md`.

Run the mechanical passes first, from the skill's `assets/` directory:

```
python drift_report.py --root . --days 7
python lane_adoption.py --project . --last 20
```

Then run the project's context integrity test if it has one.

Report as a table: **file | claim | status (true / stale / now-enforced) |
action**. Fix what is false. Leave what is merely old — a doc unchanged for six
months because its subject has not changed is stability, not drift, and
refreshing it destroys the signal that it was accurate.

Scope, if given: $ARGUMENTS
