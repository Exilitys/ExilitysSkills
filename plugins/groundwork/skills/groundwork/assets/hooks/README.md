# Hook templates

Working scripts, not pseudocode. Copy into `<repo>/.claude/hooks/` and adjust
the three project-specific bits.

## `contract_gate.py` — PreToolUse on Edit|Write

Blocks writes to contract paths unless a spec exists on the branch.

Adjust:
- `INVARIANTS` — the doc holding the fenced contract list
- `SPEC_DIR` — where specs live
- `nearest_base()` candidates — this repo's integration branch names

Reads the path list from the doc, so the list has one home. Do not hardcode it.

## `session_start.py` — SessionStart

Prints branch, uncommitted count, plans with open work, graph freshness, and the
lane/contract reminder. Everything computed; nothing hand-maintained -- the repo
name, the contract list and the plan directory are all derived, so it usually
runs unmodified.

Reads the contract list from the same fenced block the gate reads, so the
reminder and the enforcement cannot disagree.

Adjust only if the defaults miss: `INVARIANTS`, `PLAN_DIRS`, `GRAPH`. Sections
whose source is absent are omitted rather than printed empty.

## settings.json

```json
{
  "hooks": {
    "SessionStart": [{ "matcher": "startup|resume|clear|compact",
      "hooks": [{ "type": "command", "timeout": 10,
        "command": "python \"$CLAUDE_PROJECT_DIR/.claude/hooks/session_start.py\"" }] }],
    "PreToolUse": [{ "matcher": "Edit|Write|NotebookEdit",
      "hooks": [{ "type": "command", "timeout": 15,
        "command": "python \"$CLAUDE_PROJECT_DIR/.claude/hooks/contract_gate.py\"" }] }]
  }
}
```

## Verify all three paths before believing it works

```bash
echo '{"tool_name":"Edit","tool_input":{"file_path":"<contract path>"}}' | python contract_gate.py; echo $?  # 2
echo '{"tool_name":"Edit","tool_input":{"file_path":"<ordinary path>"}}' | python contract_gate.py; echo $?  # 0
echo '{"tool_name":"Edit","tool_input":{"file_path":"<contract path>"}}' | LP_CONTRACT_OK=1 python contract_gate.py; echo $?  # 0
```

A gate that never fires is worse than no gate — it reads as protection.
