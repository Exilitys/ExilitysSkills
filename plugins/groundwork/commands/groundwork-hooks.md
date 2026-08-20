---
description: Install the contract gate and session-start hooks into this repo
---

Install groundwork's enforcement hooks into **the current repository**, not
globally. Contract paths differ per project, so a gate that fired everywhere
would block edits in repos that never opted in.

Steps:

1. Read `references/contract-gate.md` from the `groundwork` skill.
2. Confirm the repo has a contract list — a fenced block under
   `## Contract paths` in `docs/architecture/invariants.md`, or wherever this
   project keeps it. **If there is none, stop and derive it with the user
   first.** A gate with an empty list is a no-op that reads as protection.
3. Copy `assets/hooks/contract_gate.py` and `assets/hooks/session_start.py`
   into `.claude/hooks/`, and adjust the marked project-specific constants.
4. Merge the hook entries into `.claude/settings.json` — do not overwrite the
   file, other hooks may already be registered.
5. **Verify all three paths before claiming it works:**

```
echo '{"tool_name":"Edit","tool_input":{"file_path":"<contract path>"}}' | python .claude/hooks/contract_gate.py; echo $?   # expect 2
echo '{"tool_name":"Edit","tool_input":{"file_path":"<ordinary path>"}}' | python .claude/hooks/contract_gate.py; echo $?   # expect 0
```

Show the user the diff and the exit codes. A gate that never fires is worse
than no gate — it reads as protection while providing none.

Argument, if any: $ARGUMENTS
