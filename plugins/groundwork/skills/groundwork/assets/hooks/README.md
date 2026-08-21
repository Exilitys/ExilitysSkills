# Hook templates

Working scripts, not pseudocode. Both run standalone on any host — they take
their input from argv, stdin or the repo itself, never from a host-specific
API. Copy them into the target repo (`install.py` does this) and wire whichever
mechanism the host offers.

Which mechanism that is, per agent, is in `references/host-adapters.md`.

## `contract_gate.py`

Blocks writes to contract paths unless a spec exists on the branch. Three input
shapes, one list:

```bash
# pre-edit hook: JSON envelope on stdin (Claude Code PreToolUse, and others)
echo '{"tool_name":"Edit","tool_input":{"file_path":"<path>"}}' | python contract_gate.py

# explicit paths: harnesses that pass argv, and manual checks
python contract_gate.py <path>...

# git pre-commit: the fallback that works on every host
python contract_gate.py --staged
```

Exit **2** means blocked. That code is chosen to serve both callers: Claude
Code reads 2 as "block and show the model this text", git reads any non-zero as
"reject the commit".

The envelope parser walks for path-ish keys rather than matching one known
shape, so a host this file has never heard of usually works anyway.

Tuning, all optional — the defaults cover most repos:

| Constant / env | Default |
|---|---|
| `INVARIANTS_CANDIDATES` / `GROUNDWORK_INVARIANTS` | first of `docs/architecture/invariants.md`, `docs/invariants.md`, `AGENTS.md`, `CLAUDE.md` that actually contains a `## Contract paths` section |
| `SPEC_DIRS` / `GROUNDWORK_SPEC_DIR` | `docs/superpowers/specs/`, `docs/specs/`, `docs/design/` |
| `GROUNDWORK_BASE_BRANCHES` | `development`, `main`, `master`, and their `origin/` forms |
| `GROUNDWORK_REPO` | git toplevel |

Overrides: `GROUNDWORK_CONTRACT_OK=1`, or a `.groundwork/.contract-override`
file. Both are printed in the rejection, deliberately.

Reads the path list from the doc, so the list has one home. Do not hardcode it.

## `session_start.py`

Prints branch, uncommitted count, plans with open work, graph freshness, and the
lane/contract reminder. Everything computed; nothing hand-maintained — the repo
name, the contract list and the plan directory are all derived, so it usually
runs unmodified.

```bash
python session_start.py [--root PATH]
```

It takes no input and writes markdown to stdout, so the host only decides when
it runs: a `SessionStart` hook, a session-start plugin event, a `make context`
target, or a human running it. Where none of those exist, put the lane table in
`AGENTS.md` instead — a static table that is always loaded beats a computed one
that is never run.

Reads the contract list from the same fenced block and with the same parser the
gate uses, so the reminder and the enforcement cannot disagree.

Adjust only if the defaults miss: `INVARIANTS_CANDIDATES`, `PLAN_DIRS`,
`GRAPH_REL`. Sections whose source is absent are omitted rather than printed
empty.

## Wiring

### Any host, via git

```bash
python install.py --git-gate
```

Writes `.git/hooks/pre-commit`. Later than a pre-edit gate, but it is the only
one that also stops a teammate working in a different agent.

### Claude Code

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

### Hosts with no hook mechanism

The git gate above, plus a line in `AGENTS.md` telling the agent to run
`contract_gate.py <path>` before editing. The line is not enforcement — it is a
prompt, and it will be skimmed sometimes. That is exactly why the git gate goes
in as well rather than instead.

## Verify before believing it works

```bash
echo '{"tool_name":"Edit","tool_input":{"file_path":"<contract path>"}}' | python contract_gate.py; echo $?  # 2
echo '{"tool_name":"Edit","tool_input":{"file_path":"<ordinary path>"}}' | python contract_gate.py; echo $?  # 0
GROUNDWORK_CONTRACT_OK=1 python contract_gate.py "<contract path>"; echo $?                                  # 0
python contract_gate.py --staged; echo $?                       # 2 with a contract path staged
```

A gate that never fires is worse than no gate — it reads as protection.
