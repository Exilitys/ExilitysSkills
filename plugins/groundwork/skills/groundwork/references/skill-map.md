# Skill map - who owns which phase

Several skill families claim overlapping territory. Installed together and
unruled, they produce two spec directories, three debugging loops, and two
opposed test philosophies. Rule the collisions once, write the rulings into
`CLAUDE.md`, and the ambiguity stops costing anything.

## Preflight - check availability before promising a workflow

**Run this before Mode A writes a lane table and before Mode B enters a lane.**
A lane that names a skill the user does not have is worse than no lane: the
agent silently improvises the step and reports it as followed.

Check the session's own skill list first - it is already in context. Fall back
to the filesystem when unsure; which directories to look in depends on the host
(`host-adapters.md` has the full table):

```bash
ls ~/.claude/skills/ ~/.claude/plugins/*/skills/ 2>/dev/null   # Claude Code
ls ~/.codex/skills/ .codex/skills/ 2>/dev/null                 # Codex CLI
ls ~/.config/opencode/skills/ .opencode/skills/ 2>/dev/null     # OpenCode
ls .agents/skills/ 2>/dev/null                                  # any host
```

**On a host that advertises no skill list and has none of these directories,
the honest answer is "nothing is installed."** Say that, use the fallbacks, and
write `manual` in every row. Do not infer availability from the fact that a
capability *sounds* standard.

### Tier 1 - required. Missing one degrades a lane.

Every one of these ships in a single Claude Code plugin, which makes that
plugin a single point of failure - and makes the whole tier unavailable on
Codex, Cursor, Gemini CLI, and any host that does not load Claude Code plugins.
**So Tier 1 does not fail shut.** Report the gap, offer the
install, and if the user says continue, run the fallback - each is one line,
because the skill's value is the discipline, not the prose.

| Skill | Lane step | Inline fallback |
|---|---|---|
| `superpowers:brainstorming` | 1.1 explore intent | Ask what problem this solves, who hits it, and what it replaces - before any design |
| `superpowers:writing-plans` | 1.5 plan | Write checkbox tasks to a file, smallest shippable first, constraints at the top |
| `superpowers:executing-plans` | 1.7 build | Work the checkboxes in order; tick only after the check for that task passes |
| `superpowers:test-driven-development` | 1.7b logic tests | Write the failing test, watch it fail, then make it pass. Watching it fail is the part that gets skipped |
| `superpowers:systematic-debugging` | 2.1 reproduce | Reproduce first, in a test. No hypothesis before a repro |
| `superpowers:verification-before-completion` | 1.8, 2.6 verify | Run the command, paste the output, then claim. Never the other order |
| `superpowers:requesting-code-review` + `receiving-code-review` | 1.10 review | Review on a fresh context that did not write the code; verify each point before acting on it |
| `superpowers:using-git-worktrees` | 1.6 isolate | `git worktree add` a branch dir, or just a branch if the workspace is clean |

Say "superpowers is not installed" once, with the install command, rather than
listing eight rows. Then name which fallbacks you will use.

On a host that cannot install it at all, skip the offer -- an install command
the user cannot run reads as a blocker where there is only a substitution. Name
the fallbacks and continue.

### Tier 2 - recommended. Missing one degrades a step to manual.

| Skill | Step, and what happens without it |
|---|---|
| `superpowers:subagent-driven-development` | 1.7 alternative build path - fall back to executing-plans |
| a scope skill (`/scope`) | "what's next" has no home - use the backlog file |
| an audit skill (`/audit`) | Mode A does more of the work by hand |
| a check skill (`/check verify`, `/check review`) | 1.9 becomes manual verification |
| a document skill (`/document pr`) | 1.11 PR prose written ad hoc |
| a sync skill (`/sync`) | 1.12, 2.7 - context never folds back; this is the one that rots the system |
| `grill-me` / `grill-with-docs` | 1.3 spec goes unstressed |
| `diagnose` | Lane 2 hard/perf bugs lose minimise + instrument |
| `prototype` | Lane 4 has no shape |
| `handoff` | context exhaustion becomes a lost session |
| `explain-diff-html` | 1.10b, and onboarding - fall back to a written walkthrough in the PR thread, which nobody reads twice |

**`explain-diff-html` is the one Tier 2 row you may already have.** It ships in
this same marketplace, so unlike the rest of the tier it is one command away
rather than a dependency on someone else's plugin:

```bash
/plugin install explain-diff@exilitys-skills     # Claude Code
python install.py --skill explain-diff-html      # any other host
```

### Tier 3 - craft. Called from inside a step; absence is not a blocker.

`ui-ux-pro-max`, `shadcn`, `ui-styling`, a test-writing skill (`/test`), a
minimalism skill (`ponytail`), `zoom-out`, a graph skill (`graphify`).

### Reporting the gaps

State missing Tier 1 skills and **stop to ask**: name the plugin, give the
install command, and offer the degraded path explicitly. Do not silently
substitute - a fallback the user did not agree to is indistinguishable from
improvising, which is the thing this preflight exists to prevent.

State missing Tier 2 skills, name the fallback each lane will use, and
**continue** - the workflow still holds, it just does more by hand.

Do not mention Tier 3 gaps unless the project is in that domain.

Never invent a skill name to fill a row. If nothing installed owns a phase, the
row reads `manual` and the lane table says so.

## The shape: spine and ring

**Spine — the build loop.** Whichever family the project already has working
history with. Continuity beats theoretical fit: if the repo has a dozen
completed cycles under one convention, that convention wins.

**Ring — the phases the spine lacks.** Roadmap, context bootstrap, post-merge
context maintenance, PR prose. These are usually a different family's strength.

**Craft skills** — design, framework-specific, library-specific — are called
*from inside* a lane step, never as a lane of their own.

## Phase ownership

| Phase | Owner |
|---|---|
| What's next / roadmap | a scope skill |
| Bootstrap context on a cold repo | an audit skill, plus this one |
| Explore intent | `superpowers:brainstorming` |
| Stress-test a design | `grill-me`, or `grill-with-docs` where a domain doc exists |
| Spec | project convention |
| Plan | `superpowers:writing-plans` |
| Isolate | `superpowers:using-git-worktrees` |
| Execute | `superpowers:executing-plans` / `subagent-driven-development` |
| Test-first (logic) | `superpowers:test-driven-development` |
| Test-after (UI) | a test-writing skill |
| Debug | `superpowers:systematic-debugging`; `diagnose` for hard/perf |
| Verify | `superpowers:verification-before-completion`, then a check/verify skill |
| Review | `requesting-` → `receiving-code-review` |
| PR prose | a document skill |
| Explain a change to a reader | `explain-diff-html` |
| Fold context back | a sync skill |
| Out of context | `handoff` |
| Unfamiliar area | `zoom-out` |

## The five collisions, and how to rule them

### 1. Two spec/artifact homes

Two families want different directories (`docs/specs/` vs. a nested SDD folder;
`docs/reviews/`, `docs/scope/`). **Pick the one with history** and redirect the
other. Renaming an existing artifact folder to drop a vendor's name is
tempting — weigh it against the link churn; usually not worth it.

### 2. Competing always-read substrates

`CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, a `context/` folder, `CONTEXT.md`. Pick
**one root** file. `AGENTS.md` stays legitimate as *directory-local* rules; the
root variant becomes a one-line pointer to whichever is canonical.

This collision gets worse, not easier, when a team uses several agents: each
host has a preferred filename and the instinct is to give each one its own
copy. Resist it. One canonical file, the rest one-line pointers -- see
`host-adapters.md`. Per-host copies are the same drift this skill exists to
prevent, multiplied by the number of agents in the team.

A domain-glossary `CONTEXT.md` is the one worthwhile addition, because several
skills read one and run degraded without it — but cap it at a glossary. The
moment it explains mechanism it is a second architecture doc.

### 3. Opposed test philosophies

Test-first vs. test-after are both defensible and cannot both be default. The
split that holds: **test-first for pure logic, test-after for UI.** A component
nobody has looked at yet cannot be specified in a test honestly; a pure policy
function can.

### 4. PR prose vs. an explanation page

`/document pr` and `explain-diff-html` both read a diff and produce prose, so
they read as rivals. They are not, and the split is by **audience**:

| | Reader | Length | Lives |
|---|---|---|---|
| **PR description** | someone deciding whether to look | paragraphs | in the PR, read once |
| **Explanation page** | someone who has decided and must understand | a long page | outside the repo, read by whoever needs it next |

The ruling: **the PR body always, the page only when step 10b's conditions
hold.** Neither substitutes for the other, and an explanation page is never a
reason to skip the PR description — the reviewer still needs the paragraph that
says what they are looking at.

### 5. Duplicated verbs

Two or three skills for debugging, executing, planning. Name the default and
name the exception. "systematic-debugging always; `diagnose` when it's hard or a
performance regression" is a complete ruling and takes one line.

## A lazy-coding discipline alongside all this

A minimalism skill (YAGNI, reuse first, shortest working diff) reads as an
objection to specs, plans, and tooling. Resolve it by scope:

**It governs the diff, not the process.** Its authority stops at the file being
edited. The ceremony is a deliberate choice about *which* code gets written; the
ladder is about how much code that is.

They are complements, not rivals — its "does this already exist here?" rung is
precisely the question the context system exists to make answerable. Without the
context system, that rung is answered by guessing.

Two carve-outs worth writing down:

- Its "one check, no frameworks, no fixtures" rule targets repos with no test
  infrastructure. Where a suite exists, using it *is* the lazier path — its own
  "use an installed dependency" rung says so.
- Its corner-cut comments are deferrals. Harvest them into the backlog rather
  than letting them accumulate as private notes in the source.

## Ordering rule

When several apply: **process skills first** — they set the approach — then
implementation skills carry it out. "Build X" starts with brainstorming. "Fix X"
starts with reproduction. Never the domain skill first.
