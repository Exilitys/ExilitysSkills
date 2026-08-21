# Host adapters — running this skill outside Claude Code

The skill is host-neutral by construction: `SKILL.md` plus `references/` plus
`assets/` is the Agent Skills layout, and every major agent loads it. What is
*not* neutral is everything around it — where the folder goes, how a command is
declared, whether a pre-edit hook exists at all, and which file the host loads
unprompted.

This file is the translation table. Read it when the session is not Claude
Code, or when bootstrapping a repo whose team uses more than one agent.

## The three things a host has to supply

| Need | Why the skill needs it | If the host cannot |
|---|---|---|
| **Skill discovery** | Load `SKILL.md` on description match | Point at it from the always-loaded file; the skill then loads by instruction rather than by match |
| **An always-loaded file** | The lane table has to be visible when a task *arrives*, not when someone remembers to ask | No fallback. A workflow nobody sees is decorative — this is the one that decides whether adoption is real |
| **Enforcement** | The gate has to fire without being remembered | Git `pre-commit` — later than a pre-edit hook, but universal |

Everything else — slash commands, session-start banners — is convenience.

## Where things go

`install.py` at the repo root writes all of this; the table is here so the
placement can be checked, undone, or done by hand.

| Host | Skill folder | Always-loaded file | Commands | Pre-edit hook |
|---|---|---|---|---|
| **Claude Code** | `.claude/skills/` | `CLAUDE.md` | `.claude/commands/*.md` (frontmatter) | `PreToolUse`, JSON on stdin |
| **Codex CLI** | `.codex/skills/` | `AGENTS.md` | `~/.codex/prompts/*.md`, global only | none — use the git gate |
| **OpenCode** | `.opencode/skills/`, and it also reads `.claude/skills/` and `.agents/skills/` | `AGENTS.md` | `.opencode/command/*.md` | plugin on a tool event |
| **Cursor** | `.cursor/skills/` | `AGENTS.md` | `.cursor/commands/*.md` | none — use the git gate |
| **Gemini CLI** | `.gemini/skills/` | `GEMINI.md` / `AGENTS.md` | `.gemini/commands/*.toml` | none — use the git gate |
| **Anything else** | `.agents/skills/` | `AGENTS.md` | — | git gate |

`.agents/skills/` is the cross-client convention and the safest single place to
put one copy. `AGENTS.md` is the cross-tool always-loaded file; where a host
has its own (`CLAUDE.md`, `GEMINI.md`), make that one a pointer rather than a
second copy — **collision 2 in `skill-map.md` applies across hosts exactly as
it applies within one.** Two always-loaded files that disagree is the failure
mode, and having two agents is not a reason to accept it.

## What changes in the skill's own behaviour

**Preflight.** `skill-map.md` says to read the session's available-skills list.
Only some hosts advertise one. Where none exists, ask the user which of the
Tier 1 phases they have tooling for, or assume none and say so — then every
lane step reads `manual` and uses the inline fallback. Do not name a skill you
have not seen; that is the failure preflight exists to prevent, and it gets
easier to commit on a host where nothing can contradict you.

**Tier 1 is a Claude Code plugin.** `superpowers` does not install on Codex or
Gemini. On those hosts the fallback column in `skill-map.md` is not a
degradation, it is the plan — each is one line, because the value was always
the discipline rather than the prose. Report it once and continue; do not stop
to ask for an install that cannot happen.

**Mode A, bootstrap.** Write `AGENTS.md` as the root file unless the repo
already has a `CLAUDE.md` with history. When the team uses several agents, one
root file plus per-host pointers — never per-host copies, which is the same
drift the whole skill exists to prevent, multiplied by the number of agents.

**Mode C, drift.** `assets/lane_adoption.py` reads Claude Code transcripts
exactly and other hosts heuristically; it labels which reading it used. Treat a
heuristic number as a trend, not a measurement.

## Enforcement without a hook mechanism

`assets/hooks/contract_gate.py` runs three ways against one list:

```bash
# 1. Pre-edit hook — Claude Code PreToolUse, or any harness with a JSON envelope
echo '{"tool_name":"Edit","tool_input":{"file_path":"<path>"}}' | python contract_gate.py

# 2. Explicit paths — harnesses that hand argv to a hook, and manual checks
python contract_gate.py <path>...

# 3. Git pre-commit — every host, including those with no hook mechanism
python contract_gate.py --staged
```

Exit 2 means blocked either way: Claude Code reads 2 as "block and show the
model this", git reads any non-zero as "reject the commit".

Install the git gate with `python install.py --git-gate`. It is strictly later
than a pre-edit gate — the work is already written when it fires — so on a host
that *has* a pre-edit hook, use that, and keep the git gate as the backstop for
teammates on other agents.

**A pre-edit gate is not portable; a commit gate is.** That asymmetry is worth
stating to a team before they pick their enforcement, because the instinct is
to configure the best gate their own agent supports and then discover it
protects nobody else.

## Session orientation

`assets/hooks/session_start.py` takes no input and writes markdown to stdout,
so the host only decides *when* it runs: a `SessionStart` hook on Claude Code,
a session-start plugin event on OpenCode, and on everything else a manual
`python session_start.py`, a `make context` target, or a shell alias.

Where it cannot be automatic, do not pretend it is. Put the lane table in
`AGENTS.md` instead — a static table that is always loaded beats a computed one
that is never run.
