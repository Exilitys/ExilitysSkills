# ExilitysSkills

Three agent skills. They are plain [Agent Skills](https://github.com/agentskills/agentskills)
— a `SKILL.md` with frontmatter plus its references and scripts — so they run
on any coding agent that loads that format, not only Claude Code.

| Plugin | Skill | For |
|---|---|---|
| **groundwork** | `blueprint` | Turning an idea or PRD into an interrogated, decision-recorded spec — before any repo exists |
| **groundwork** | `groundwork` | Where truth lives and how work moves: the context system, the lanes, the contract gate |
| **explain-diff** | `explain-diff-html` | Explaining a change to whoever has to understand it, as an interactive HTML page |

`blueprint` and `groundwork` ship in one plugin and run in sequence — the first
decides *what* gets built, the second decides where truth lives and how work
moves. `explain-diff` is independent, but meets them at Lane 1 step 10b, where
a change large enough to be reviewed cold is a change worth explaining.

**Claude Code**, as plugins:

```bash
/plugin marketplace add Exilitys/ExilitysSkills
/plugin install groundwork@exilitys-skills
/plugin install explain-diff@exilitys-skills
```

**Codex, OpenCode, Cursor, Gemini CLI, or anything else** — clone and run the
installer, which puts the skill where your agent looks:

```bash
git clone https://github.com/Exilitys/ExilitysSkills
python ExilitysSkills/install.py --root /path/to/your/repo
```

It detects which agents the repo is configured for and installs all three skills
for those. `--skill groundwork` narrows it. See [Any coding agent](#any-coding-agent)
below.

---

## groundwork

**Where truth lives, and how work moves** — and they are the same problem. A
workflow without a context system re-derives the project every session; a
context system without a workflow rots, because nothing consumes it.

Most "AI context" advice produces a pile of markdown that is accurate for a
week. groundwork is built on one idea instead:

> A rule a tool can check should be tool config, not prose.

Everything follows from that. Enforce what you can, write down only the *why*
that no check can hold, and make the writing itself checkable.

### What you get

| Piece | What it does |
|---|---|
| **Three modes** | Bootstrap a context system, route a task into a lane, or audit whether the docs are still true |
| **Four lanes** | Slice / Bug / Chore / Spike — the lane sets the ceremony, so a typo fix is not over-planned and a migration is not under-planned |
| **The contract gate** | A short list of paths where breaking things is *cheap and silent*. Touch one → spec first. Enforced by a hook, not by hoping |
| **Integrity tests** | Working Vitest and pytest templates that fail when your docs name something that does not exist |
| **Drift report** | Finds context files whose subject moved after they were last touched |
| **Adoption report** | Measures whether the workflow is actually followed, or just documented |
| **Design system** | On a component-based UI, sources primitives live from shadcn's and Magic UI's registries over MCP instead of a hand-written component catalog |

### Commands

| Command | Use |
|---|---|
| `/groundwork` | Bootstrap, or route the task you are starting. Infers the mode from the repo |
| `/groundwork-drift` | "Is any of this still true?" — run after a merge-heavy stretch |
| `/groundwork-hooks` | Install the contract gate + session-start hooks into *this* repo |
| `/blueprint` | You have an idea or a PRD and no spec yet — interrogate it first |

The installer writes commands in each host's own dialect, so these are real
slash commands on Claude Code, OpenCode, Cursor and Gemini CLI, and prompts on
Codex. On a host with no command mechanism, ask for the skill by name instead.

The skill also loads on its own when you ask to set up project context, make a
workflow repeatable, or fix a repo whose AI docs have gone stale.

---

## blueprint

The stage before groundwork, and the answer to a question groundwork cannot
answer on its own: **what are we building, and what did we decide against?**

```
/blueprint                              # an idea, in conversation
/blueprint docs/product-brief.md        # a PRD, notes, a transcript
```

It takes the input in whatever shape it arrived, restates it back, interrogates
what is missing, and writes a spec whose spine is decision records rather than
descriptions.

### The one idea

> A spec is a record of decisions, not a description of a product.

A description tells you what the thing is. A decision tells you what was
chosen, what was **rejected**, and what would change the answer — and only the
second survives contact with the build, because when reality disagrees with the
spec the team needs to know whether they are breaking a considered decision or
correcting an assumption nobody made on purpose.

So every record carries five fields, and the second one is what makes it a
decision at all:

```markdown
### D-004 - Postgres for primary storage
- **Chosen.** Postgres, single primary, managed.
- **Rejected.** DynamoDB — the access pattern is relational and reporting is a
  stated requirement. SQLite — loses the concurrent write path in section 8.
- **Because.** The reporting requirement (R-7) needs ad-hoc joins.
- **Revisit when.** Write throughput exceeds ~2k/s sustained.
- **Provenance.** Decided 2026-09-04 with @user.
```

An empty `Rejected.` row means it was a default, not a decision — and the
format makes you write `Default, not evaluated` rather than letting a default
wear a decision's clothes.

### Said versus inferred

The step that keeps the whole thing honest. An agent handed a thin idea will
fill the gaps with plausible features, and the user approves them because they
look reasonable — and now the project is building somebody else's product.
Inference is not the problem; **unlabelled** inference is. So intake produces
two lists, and every inference is confirmable in one word before it can
graduate into a requirement.

### What "enough detail" means

> Two competent engineers building from this spec independently produce systems
> that fit together.

That earns extreme detail on seams, data shapes, ownership, states and failure
behaviour — and forbids it on anything their compilers would have agreed on
anyway. Twelve pages of CRUD endpoints with no concurrency model is a spec that
fails the test at full length.

### The rule a tool checks

Same move as everywhere else in this repo:

```bash
python assets/check_spec.py docs/prd/prd.md
```

It fails a decision record with no rejected alternatives, a deferred item with
no revisit condition, a leftover `TBD`, an unreplaced placeholder, a duplicate
decision id, and — on a spec marked approved — a locked decision with no
provenance. It warns on weasel words standing in for numbers ("fast",
"scalable", "secure"), a non-functional section with no digits in it, a first
slice with no observable finish, and a missing failure-behaviour section.

### The handoff

Blueprint writes `docs/prd/` and `docs/specs/`. It never writes the root
`AGENTS.md`, the hooks or the lane table — those are groundwork's. The two meet
at a **file on disk**, not a conversation: groundwork's inventory already looks
in `docs/prd/`, so a spec there resolves concerns 1, 2 and 11 to pointers
instead of generated placeholders. groundwork writes *less* because blueprint
ran, which is the point — two documents describing one project is the drift the
whole repo exists to prevent.

---

## How to use it

### Starting from an idea

```
/blueprint
```

Interrogate first, then bootstrap. Running `/groundwork` on a repo where
nothing has been decided produces placeholders for the concerns that matter
most — what you are building, and how it is shaped — because there is nothing
yet to describe. `/blueprint` is what fills them; when it hands off,
`/groundwork` finds a real spec and writes pointers instead.

### On a fresh repo

```
/groundwork
```

It inventories what exists before writing anything, then shows you a gap table
— **concern | resolves to | action** — and waits. On an empty repo every row is
a gap and it generates all of them. On a mature repo most rows resolve to
something you already have, and it writes pointers instead of duplicates.

That confirmation step is where you catch its mistakes. Take the argument
seriously; a proposal that contradicts the project philosophy is a proposal
worth rejecting, and the correction is information.

### On an existing repo, starting a task

```
/groundwork
```

It picks a lane and announces it. The lane decides the ceremony:

- **Lane 1 · Slice** — brainstorm → contract check → spec → *gate* → plan →
  worktree → build → verify → review → PR → sync
- **Lane 2 · Bug** — reproduce **first** → root cause → failing regression test
  → minimal fix → verify
- **Lane 3 · Chore** — no spec; plan only if >3 files; **existing tests must
  pass unchanged** (if a test had to change, behavior changed, and it is not a
  chore)
- **Lane 4 · Spike** — throwaway, not merged; deleted or promoted to Lane 1

### Every so often

```
/groundwork-drift
```

Stale docs do not go quiet — they start lying, with the authority of something
that was once checked. This finds the lying ones.

---

## The gate

The one hard stop. Before editing, the path is checked against the contract
list:

```
backend/domain/ports/     backend/alembic/     backend/static/bridge.js
frontend/src/app/globals.css                   docs/prompts/
```

*(example — yours will differ)*

- **Touches one → STOP.** Spec, approval, then build.
- **Touches none →** proceed in one session.

It is membership in a list, not a judgment about importance. A contract path is
one where breaking it is **cheap and silent**: port signatures, migrations, a
shared runtime script, design tokens, prompts — plus any deferred decision
carrying a revisit condition.

`/groundwork-hooks` makes this a real hook rather than a sentence, because the
sentence has a known failure mode: a session in a hurry skims it. The hook reads
the path list *from your invariants doc*, so there is exactly one list — never
one in prose and one in code that quietly disagree.

The same script fires three ways, so the list is enforced whatever your agent
supports:

```bash
echo '{"tool_name":"Edit","tool_input":{"file_path":"<path>"}}' | python contract_gate.py   # pre-edit hook
python contract_gate.py <path>...                                                            # explicit / argv hooks
python contract_gate.py --staged                                                             # git pre-commit
```

Exit 2 means blocked either way — Claude Code reads 2 as "block and tell the
model why", git reads non-zero as "reject the commit".

**A pre-edit gate is not portable; a commit gate is.** So install both:
`python install.py --git-gate` writes the `pre-commit` one, and it is the only
firing point that also stops a teammate working in a different agent. Without
it, the first person on another tool walks straight through a list that still
reads as enforced.

Hooks install **per repo, not globally**. Contract paths differ per project, and
a gate firing in repos that never opted in is the first thing anyone uninstalls.

---

## explain-diff

A diff shows *what* changed. It is silent on the two things a reader actually
needs: what the world looked like before, and why this shape was the right one.
`explain-diff-html` produces the missing half as one self-contained HTML page.

```
/explain-diff                      # uncommitted work, or this branch vs. its merge-base
/explain-diff feature/retry        # a branch
/explain-diff 1284                 # a PR
/explain-diff abc123..def456       # a range
```

Four sections, in the order a reader can absorb them:

| Section | Job |
|---|---|
| **Background** | The system *before* the change. A deep pass for beginners, explicitly skippable; then the narrow slice this change touches |
| **Intuition** | The core idea on toy data, with diagrams. If you stop here you can still say what the change does and why |
| **Code** | The walkthrough, grouped by idea rather than by file |
| **Quiz** | Five interactive questions that require the substance, with feedback on every option — including the right one |

### What makes it work, and what makes it useless

> **Explain the system, not the patch.**

The failure mode is a page that walks the hunks in file order and teaches
nothing, because it never establishes what the code did before — so every
change reads as arbitrary. A reader who finishes it can recite the diff and
still cannot predict what breaks if they revert it.

That is why the expensive step is reading the *surrounding* code, not the diff.
Everything in the skill is arranged around not skipping it.

It is also deliberately **not** the PR description — different audience,
different length — and not worth producing for a two-file change to code the
reviewer wrote. There the diff is the explanation.

### The rule a tool checks

groundwork's one idea applies to this plugin too:

> A rule a tool can check should be tool config, not prose.

The original instruction said *"before saving the file, scan each code block
and confirm its CSS includes `white-space: pre-wrap`"* — because a code block
in a styled `div` silently collapses every newline into one line. That is a
rule a tool can check, so a tool checks it:

```bash
python assets/write_target.py --slug retry-backoff   # a dated path outside the repo
python assets/check_output.py <path>                 # exit 1 on failure
```

`check_output.py` catches the newline collapse, an external `<script src>` that
will not load offline, a missing date prefix, a file written inside the repo,
a quiz option with no feedback, a correct answer that is not one of the
options, leftover `REPLACE` placeholders, and a missing viewport tag — plus the
design rules that are mechanically decidable: a colour token defined only for
dark mode, a class used in the markup with no CSS behind it, and a page
spending its emphasis budget on too many callouts. Every one of those has
shipped in a page someone believed was finished.

---

## Any coding agent

The skill is the Agent Skills format, which Claude Code, Codex CLI, OpenCode,
Cursor and Gemini CLI all load. What differs per agent is everything *around*
it — where the folder goes, how a command is declared, and whether a pre-edit
hook exists at all. `install.py` is that translation layer.

```bash
python install.py --list                    # skills, hosts, and where things would go
python install.py                           # every skill, detected hosts + the neutral copy
python install.py --skill groundwork        # just one skill
python install.py --host codex opencode     # name the hosts explicitly
python install.py --scope user              # into your home config instead of the repo
python install.py --link                    # one real copy, the rest symlinked at it
python install.py --git-gate                # + the pre-commit contract gate
python install.py --dry-run                 # print the plan, write nothing
python install.py --uninstall               # reverse exactly what a run wrote
```

| Host | Skill folder | Commands |
|---|---|---|
| Claude Code | `.claude/skills/` | `.claude/commands/*.md` |
| Codex CLI | `.codex/skills/` | `~/.codex/prompts/*.md` (global only) |
| OpenCode | `.opencode/skills/` — also reads `.claude/skills/` and `.agents/skills/` | `.opencode/command/*.md` |
| Cursor | `.cursor/skills/` | `.cursor/commands/*.md` |
| Gemini CLI | `.gemini/skills/` | `.gemini/commands/*.toml` |
| Anything else | `.agents/skills/` | — |

Every run also writes a marked block into `AGENTS.md` naming each installed
skill **and carrying its description** — the part that says *when* to read it.
That block is what makes this work on a harness with **no skill loader at
all** — a DeepSeek-backed agent, an in-house wrapper, whatever your team runs —
because `AGENTS.md` is the one file essentially every coding agent loads. It is
not as good as real skill discovery: the skill loads because the root file told
the agent to read it, not because the description matched. It is enough.

Everything is recorded in `.groundwork/install.json`, so `--uninstall` removes
exactly what was added and never guesses.

The skill knows about all this too — `references/host-adapters.md` is what it
reads when the session is not Claude Code, so it stops offering plugin installs
that cannot happen and picks the enforcement your host actually has.

### The honest part

Skill *discovery* is portable; the ecosystem around it is not.
[superpowers](https://github.com/obra/superpowers) — Tier 1 below — is a Claude
Code plugin, so on Codex or Gemini those eight rows are unavailable and the
one-line fallbacks are the plan rather than a degradation. groundwork's own
discipline (lanes, the gate, provenance, the ladder) carries over intact,
because it was always prose and a path list rather than a tool.

---

## Dependencies

groundwork routes to other skills rather than reimplementing them, so it checks
availability **before** promising a workflow. A lane that names a skill you do
not have is a lane the agent quietly improvises and then reports as followed.

- **Tier 1 — [superpowers](https://github.com/obra/superpowers)** owns
  brainstorming, planning, execution, TDD, debugging, verification, review, and
  worktrees. Missing it does not fail shut: groundwork reports the gap, offers
  the install, and falls back to a one-line version of each step if you say
  continue.
- **Tier 2 — recommended.** Scope, audit, check, document, sync, `grill-me`,
  `diagnose`, `prototype`, `handoff`. Each degrades to a named manual fallback.
  The one that matters most is **sync** — without it, context never folds back,
  which is what rots the system.
- **Tier 3 — craft.** UI, styling, testing, minimalism skills. Absence is never
  a blocker.

Install superpowers (Claude Code only):

```bash
/plugin marketplace add obra/superpowers
/plugin install superpowers
```

On other hosts groundwork skips the offer rather than naming an install command
you cannot run, and reports which fallbacks it will use instead.

---

## The parts that carry more than their length suggests

**Climb the ladder before writing any file.** Does this need to exist? Does it
already exist here? Stdlib? Platform feature? Installed dependency? One line?
Only then write it. Rung two is the expensive one to answer with grep — that is
what the context system is *for*.

**Two-strikes promotion.** The second time a pattern appears, extract it — and
add its guard in the same commit. A primitive without its invariant is half the
work, because the third occurrence is still possible.

**Every locked decision cites its source — file and date.** A decision without
provenance is a guess wearing a spec's clothes. The most valuable thing a spec
does is discover that the thing being asked for was already decided against,
and why.

**Evidence before assertions.** Run the command, read the output, then claim.

---

## Honest limitations

- **Adoption is the hard part, not authoring.** Measured on the repo groundwork
  was built in: **13% of code-editing sessions announced a lane**, with a
  SessionStart hook printing the lane table *every session*. Being visible is
  not being used. `/groundwork-drift` reports this number so you can see it
  rather than assume it.
- **The drift report is a coarse heuristic.** It compares commit recency; it
  cannot read meaning. It reports and never gates, because a gate on a signal
  this rough gets disabled within a week and takes the honest signal with it.
- **The integrity test only checks names and paths.** It catches a doc naming a
  class that never existed. It cannot catch a doc that describes real classes
  doing the wrong thing.
- **An explanation page is a real cost.** Producing a good one means reading
  the surrounding code properly, not just the diff. `explain-diff-html` is
  opt-in for exactly that reason, and on a two-file change to code the reviewer
  wrote it is not worth running — the diff is already the explanation.
- **`check_output.py` checks form, not truth.** It proves the page is
  well-formed, offline-safe and correctly wired. It cannot tell you the
  background section is wrong, which is the failure that matters most. That one
  is still on the reader.
- **Windows-first.** Written and tested on Windows with Python 3.11+; the
  scripts avoid shell assumptions but have had less exercise elsewhere.
  `--link` falls back to copying where symlinks are unavailable.
- **Adoption measurement is exact on Claude Code only.** `lane_adoption.py`
  knows Claude Code's transcript shape; on other hosts it scans JSONL
  heuristically and says so in its output. Read a heuristic number as a trend.
- **Host paths move.** Agents rename their config directories more often than a
  README gets updated. `install.py --list` prints where it *would* write before
  it writes anything, and `--host` overrides the guess.

---

## Repo layout

```
install.py                          cross-agent installer (finds every skill below)
.claude-plugin/marketplace.json     Claude Code marketplace manifest
plugins/groundwork/
  .claude-plugin/plugin.json
  commands/                         /groundwork, -drift, -hooks, /blueprint
  skills/blueprint/
    SKILL.md                        idea -> interrogation -> spec -> handoff
    references/
      intake.md                     any input shape; said vs. inferred
      interrogation.md              the question taxonomy, and when to stop
      spec-format.md                sections, the decision record, falsifiability
      handoff.md                    the seam to groundwork; re-entry paths
      skill-map.md                  what it routes to, and the fallbacks
    assets/
      spec-template.md              the scaffold
      check_spec.py                 verifies the spec before sign-off
  skills/groundwork/
    SKILL.md                        preflight, modes, the one idea
    references/
      bootstrap.md                  Mode A: nine concerns, gap analysis
      claude-md-template.md         drafting the root file: sections, trim test
      lanes.md                      Mode B: full lane definitions
      drift-audit.md                Mode C: "is this still true"
      contract-gate.md              designing the list, generating hooks
      tooling-floor.md              what becomes config instead of prose
      design-system.md              shadcn + Magic UI over MCP, instead of a hand-written component catalog
      skill-map.md                  preflight tiers, phase ownership
      host-adapters.md              running on Codex / OpenCode / Cursor / Gemini / anything
      memory-graph.md               graph search, memory tiers
    assets/
      hooks/                        contract_gate.py (3 input modes), session_start.py
      tests/                        integrity templates (Vitest + pytest)
      drift_report.py               Mode C mechanical pass
      lane_adoption.py              does anyone follow the workflow
plugins/explain-diff/
  .claude-plugin/plugin.json
  commands/                         /explain-diff
  skills/explain-diff-html/
    SKILL.md                        the flow: resolve, read around, write, check
    references/
      structure.md                  the four sections and the transitions
      diagrams.md                   diagram families, HTML patterns, never ASCII
      quiz.md                       questions that test the model, not the text
      html-contract.md              self-contained, responsive, the whitespace trap
      design.md                     the template's components, colour tokens, emphasis budget
    assets/
      template.html                 working scaffold: TOC, callouts, diagrams, quiz JS
      write_target.py               a dated path outside the repo, cross-platform
      check_output.py               verifies the page before you claim it works
```

## License

MIT — see [LICENSE](LICENSE).
