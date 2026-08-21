# Bootstrap - establishing the context system

The output is **not nine files. It is nine concerns, each resolving to exactly
one location.** On an empty repo that means nine new files. On a mature repo it
usually means one or two files and seven pointers — and writing the other seven
anyway is how you get two homes for one truth, which is the failure this whole
skill exists to prevent.

## Step 1 - Inventory

Do not ask the user what exists. Look.

```
git remote -v
ls AGENTS.md CLAUDE.md GEMINI.md CONTEXT.md README.md
find docs -type f 2>/dev/null | head -50
find . -name "AGENTS.md" -not -path "*/node_modules/*"
ls -d .claude .codex .opencode .cursor .gemini .agents 2>/dev/null
```

That last line also tells you **which agents this team actually uses**, which
decides the root filename in step 4 and the enforcement mechanism in step 5.
More than one means the placement rules below matter more, not less.

Then read enough of what you find to know whether it is *current* or
aspirational. A doc that names a class is a claim; check the class exists.

## Step 2 - Map the nine concerns

| # | Concern | Typical home if it exists | Generate if missing |
|---|---|---|---|
| 1 | What we're building, and for whom | `docs/prd/`, a spec, README | `project-overview.md` |
| 2 | How the system is structured | `docs/architecture/` | `architecture.md` |
| 3 | **How code is written** | *usually nothing* | per-directory `AGENTS.md` §1 |
| 4 | **How libraries are used** | *usually nothing* | per-directory `AGENTS.md` §2 |
| 5 | Visual tokens | a CSS/theme file + its tests | `ui-tokens.md` |
| 6 | Design direction and rules | a design doc | `ui-rules.md` |
| 7 | Component gallery | the component directory itself | `ui-registry.md` |
| 8 | What's next | backlog, roadmap, issues | `build-plan.md` |
| 9 | Where we are | git + status headers + a hook | `progress-tracker.md` |

Concerns **3 and 4 are the reliable gaps.** Most projects document what they
are building and almost none document how it is written or which library
version's docs to trust. Expect those two to be real work and the rest to be
pointers.

Two more concerns exist that no starter kit includes, and they are the ones the
workflow actually runs on:

| # | Concern | Home |
|---|---|---|
| 10 | **How we work** — lanes, gate, contract list | root file tables + whatever the host enforces with (`host-adapters.md`) |
| 11 | **Decision provenance** — what we chose not to do, and when to revisit | spec files + backlog entries carrying explicit conditions |

## Step 3 - Present the gap table, then confirm

Show a table with a row per concern: **concern | resolves to | action
(pointer / write / skip)**. Say plainly which are gaps and which already have a
home. Then wait.

This is the step where the user catches your mistakes. On a repo with a strong
existing philosophy you *will* propose something that contradicts it — for
instance proposing a hand-maintained component registry to a project whose
design doc argues the code is the gallery and documentation was already tried
and failed. Take the correction; it is information about the project.

## Step 4 - Write

### Placement rules

- **One always-loaded root file.** Exactly one holds content; every other
  candidate becomes a one-line pointer to it. Prefer `AGENTS.md` — it is the
  cross-tool name, read by the most agents, and the only choice that does not
  need re-deciding when someone joins on a different tool. Keep `CLAUDE.md` as
  the content file only when it already has history; then `AGENTS.md` points at
  it. Never two files with content, and never one file per agent: that is the
  same drift this skill exists to prevent, multiplied by the number of tools.
- **Standards and library docs go directory-local**, next to the code they
  govern: `backend/AGENTS.md`, `frontend/AGENTS.md`. A Python session should
  never load React conventions. Split by stack, not by topic.
- **No new top-level folders** unless the repo has nowhere for a concern to go.
- Domain vocabulary — a glossary and nothing more — earns a root `CONTEXT.md`
  if any skill in use reads one. Cap it hard: the moment it explains *how*
  something works it has become a second architecture doc.

### The root file becomes a router

**Section order, caps, the trim test and a worked skeleton are in
`claude-md-template.md`.** Read it before drafting; this is the file every
session pays for, and the one people fill with a condensed architecture summary
that goes stale without anyone touching it.

Its job is the concern→location table, the lane table, the contract list, and
the framing no file carries. Not a second copy of the architecture — where a
longer document owns a subject, name it and stop. The rule that decides every
section: **it is a pointer or a rule, never a summary.**

**Plus one short section naming the skills the lane table depends on**, so a
future session in a different environment — or a different agent, where those
skills may not exist at all — finds out before it improvises a
step. Write only the skills that were actually installed when you wrote the
table — the list is a manifest of what the lanes assume, not a wishlist:

```markdown
## Skills this workflow assumes

Check these are available before following a lane. Missing one means that
step is manual — say so rather than improvising it.

| Step | Skill | If missing |
|---|---|---|
| explore intent | `superpowers:brainstorming` | **stop** — install superpowers |
| plan / build / test / debug / verify / review | `superpowers:*` | **stop** — same plugin |
| spec stress-test | `grill-me` | write the spec, skip the interview |
| verify in app | `/check verify` | run it by hand, record the output |
| fold context back | `/sync` | update docs manually at merge |

Install: `/plugin install <name>`
```

Keep it to steps the lane table actually names. A row per installed skill is a
second skill list that will drift from the first.

### Content rules for concerns 3 and 4

**§1 Standards.** Triage every candidate rule: can a tool check it? If yes it
becomes config (see `tooling-floor.md`) and the file merely names the command.
Prose keeps only the residue — when to add an abstraction, where wiring is
allowed, the error taxonomy, what *not* to persist, comment policy.

Encode the project's **actual** conventions, not the ones a template asserts.
Check the filenames before writing a filename rule; a kit that mandates
PascalCase files will invalidate an entire kebab-case tree.

**§2 Libraries.** Lead with the authority ladder:

```
MCP server (live docs) -> installed skill -> local package docs -> this file -> training knowledge
```

Then name the real resources for *this* repo — which skills are installed and
relevant, whether the framework ships docs inside `node_modules`, which MCP
servers are authenticated. Then per-library sections covering **how this project
uses it**, especially version-critical gotchas where training data is likely
describing an older major.

## Step 5 - Make the writing checkable

Write an integrity test. This is short and it is the highest-leverage artifact
in the whole bootstrap.

**Start from `assets/tests/`** - `context-integrity.test.ts` (Vitest) and
`test_context_integrity.py` (pytest) are working templates with the
project-specific parts hoisted into one CONFIG block. Adjust that block, delete
the rules that do not apply, keep the one that guards the config itself: a
wrong source directory makes every other rule pass vacuously, and a green suite
guarding nothing is the worst available outcome.

What it asserts:

- every identifier the context files name must exist in the source
- every path they point at must exist
- if the glossary lists "not domain terms", none may exist as real classes

Run it. It will fail on the first run — that failure is the point. A real
example: a root always-loaded file listing a port class that had never existed, while
omitting one that shipped four days earlier, with nothing in a 900-test suite
able to see it.

Prefer token-set lookups over per-name regexes: one pass over the source, and no
escaping to get wrong.

## Step 6 - Offer hooks

See `contract-gate.md`. Show the generated config and the derived contract list
before writing anything. On a fresh project the list is usually empty and the
hooks are a no-op — that is fine, they grow with the project.

## Anti-patterns

- **Generating all nine on a repo that has seven.** Vandalism with good manners.
- **A status file a human updates.** It is stale by the second session. Compute
  it in a `SessionStart` hook from git and plan headers instead.
- **A hand-maintained component registry** when the component directory exists.
  The code cannot go stale; the registry can.
- **Restating architecture in the root file.** Two summaries diverge; the always-
  loaded one wins by default and is usually the more out of date.
- **Writing a rule you could have enforced.** Ask what would fail if it were
  broken. If nothing, write the check instead — or as well.
