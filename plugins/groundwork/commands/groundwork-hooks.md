---
description: Install the contract gate and session-start hooks into this repo
---

Install groundwork's enforcement into **the current repository**, not globally.
Contract paths differ per project, so a gate that fired everywhere would block
edits in repos that never opted in.

Steps:

1. Read `references/contract-gate.md` and `references/host-adapters.md` from the
   `groundwork` skill. The second one decides step 4.
2. Confirm the repo has a contract list — a fenced block under
   `## Contract paths` in `docs/architecture/invariants.md`, or wherever this
   project keeps it. **If there is none, stop and derive it with the user
   first.** A gate with an empty list is a no-op that reads as protection.
3. Copy `assets/hooks/contract_gate.py` and `assets/hooks/session_start.py`
   into the repo. The defaults are usually right; adjust only what misses.
4. Wire whichever mechanism this host has:
   - **A pre-edit hook** (Claude Code `PreToolUse`, an OpenCode plugin) — merge
     the entry into the host's settings file. Do not overwrite it; other hooks
     may already be registered.
   - **No pre-edit hook** — `python install.py --git-gate`, which writes a
     `pre-commit` hook calling `contract_gate.py --staged`.
   - **Either way**, offer the git gate: it is the only firing point that also
     stops a teammate working in a different agent.
5. **Verify every path you wired before claiming it works:**

```
echo '{"tool_name":"Edit","tool_input":{"file_path":"<contract path>"}}' | python <hooks>/contract_gate.py; echo $?   # expect 2
echo '{"tool_name":"Edit","tool_input":{"file_path":"<ordinary path>"}}' | python <hooks>/contract_gate.py; echo $?   # expect 0
python <hooks>/contract_gate.py --staged; echo $?                                                                    # expect 2 with a contract path staged
```

Show the user the diff and the exit codes. A gate that never fires is worse
than no gate — it reads as protection while providing none.

Argument, if any: $ARGUMENTS
