---
name: explain-diff-html
description: Produce a rich, interactive HTML explanation of a code change - a diff, a branch, a commit range, a PR, or the working tree - with deep background, the core intuition, a code walkthrough, diagrams, and a quiz that checks the reader actually understood it. Use when asked to explain, walk through, teach, document or onboard someone onto a change, when a PR is too large to review cold, or when a reviewer asks "what is this actually doing". Not for writing the PR description itself.
---

# Explain Diff

A diff shows *what* changed. It is silent on the two things a reader actually
needs: what the world looked like before, and why this shape was the right one.
This skill produces the missing half, as one self-contained HTML page.

## What this is for, and what it is not

**For** a reader who has to understand a change: a reviewer facing something
large, a teammate onboarding onto unfamiliar code, your future self at six
months, a reader learning the system through one of its changes.

**Not** for the PR description. That is a different artifact with a different
audience — short, aimed at someone deciding whether to look — and a document
with a quiz in it is the wrong shape for it. If the ask is a PR body, say so
and write that instead.

**Not** a summary of the diff. A reader can already read the diff. If the page
would be the diff rearranged, it is not worth producing, and the honest move is
to say the change is small enough to read directly.

## The one thing that makes it good or useless

> **Explain the system, not the patch.**

The failure mode is a page that walks the hunks in file order, restates each
one in prose, and teaches nothing — because it never establishes what the code
was doing before, so every change reads as arbitrary. A reader who finishes it
can recite the diff and still cannot predict what breaks if they revert it.

Everything below is in service of avoiding that.

## The flow

### 1. Resolve the target

Ask only if genuinely ambiguous; otherwise infer and say what you chose.

| The user said | Target |
|---|---|
| nothing | uncommitted work; if the tree is clean, the current branch vs. its merge-base |
| a branch name | that branch vs. its merge-base with the integration branch |
| a PR number/URL | that PR's head vs. base |
| a commit / range | exactly that |
| "this change" mid-session | what this session actually edited |

Get the base right. `git merge-base <base> HEAD` — diffing against a branch
tip sweeps in everything merged in between, and you will explain twenty other
people's changes as if they were this one.

### 2. Read the surrounding code — this is the expensive step, do not skip it

The background section is the one that decides whether the page works, and it
cannot be written from the diff alone. For each changed region, read the file
it lives in, its callers, and its tests. Look for the previous shape of the
thing being changed: `git log -p` on the touched files usually shows why the
current design exists.

**Evidence before assertions.** If you claim the old code did X, you have read
the old code. A confidently wrong background is worse than none — it teaches a
false model that survives long after the page is closed.

Where you genuinely cannot tell why something is the way it is, say so in the
page. "This predates the current tests and the reason is not recorded" is
useful; an invented rationale is not.

### 3. Write the four sections

Full definitions in `references/structure.md`. In short:

| Section | Job | Fails when |
|---|---|---|
| **Background** | The system before the change. Deep pass for beginners, marked skippable; then the narrow slice this change touches | It starts at the diff |
| **Intuition** | The essence, on toy data, with diagrams. One worked example carried end to end | It reaches for the real code |
| **Code** | High-level walkthrough, grouped by idea rather than by file | It becomes an annotated diff in file order |
| **Quiz** | Five interactive multiple-choice questions that require the substance | The answers are guessable from wording alone |

Order matters and the transitions carry weight: each section should end by
raising the question the next one answers.

### 4. Build the page

Start from `assets/template.html` — a working scaffold with the table of
contents, section shells, callout and diagram styles, and the quiz interaction
already wired. Replace its content; keep its structure, and build every visual
element out of the components it already defines rather than inventing new ones
(see **Design and components** below).

The hard constraints are in `references/html-contract.md`. The one that bites
most often: **a code block styled with a custom `div` collapses every newline
into one line unless its CSS says `white-space: pre-wrap`.** Use `<pre>`.

Write it in classic style — plain declarative prose that points at the subject
rather than at itself. Kleppmann is the target: concrete, unhurried, never
performing rigour.

### 5. Save it outside the repo, then check it

```bash
python assets/write_target.py --slug <short-slug>      # prints the path to write
python assets/check_output.py <path>                   # verify before you claim it works
```

The filename starts with today's date in `YYYY-MM-DD-` so the files sort by
time, and it lands outside the repository so it never reaches version control.
`write_target.py` picks the right directory per platform rather than assuming
`/tmp`, which does not exist on Windows.

**Run the checker and paste its output.** It catches the newline collapse, an
external `<script src>` that will not load offline, a missing date prefix, a
file accidentally written inside the repo, and the design rules that are
mechanically decidable — a colour token missing from one theme, a class with no
CSS behind it, a page overspending its emphasis budget. Do not report the page
as done on the strength of having intended those things.

### 6. Hand it over

Give the absolute path and one line on what the page covers. If anything in the
change is still unexplained — a hunk you could not account for, a decision with
no recoverable rationale — say which, rather than letting a confident-looking
document imply full coverage.

## Design and components

> **The template's components are the vocabulary. Extend them; never invent
> alongside them.**

These pages do not fail by being ugly. They fail by emphasising everything, so
the reader cannot tell which parts carry the idea — and by growing a new visual
grammar per point, which costs a re-orientation every time it appears. Three
rules carry most of it:

- **Every visual element comes from the template's set** — `.callout` and its
  `.warn` / `.key` variants, `<pre>`, tables inside `.scroll-x`, `.diagram`
  with `.node` and `.arrow`, `.compare`, `.caption`, `.q`. If nothing fits,
  extend the nearest one so it inherits the tokens, the dark mode and the phone
  layout. A class you invent and do not style renders as bare text.
- **Colour only through the tokens.** Both palettes live on `:root`; every
  other rule says `var(--x)`. A hex literal elsewhere is a light-mode
  assumption dark mode cannot override, and a token defined only in the
  dark-mode block is invisible in light mode. Never encode meaning in colour
  alone — the `+`/`-` and `✓`/`✗` glyphs are what carry it.
- **Spend the emphasis budget deliberately.** One `.callout.key` — the change
  turns on one idea. A callout no more often than every sixth paragraph. Three
  to six diagrams, drawn from two or three reused families. Past that, a box
  stops meaning "look here" and starts meaning nothing.

Which component for which job, what each colour token means, and the type scale
are in `references/design.md`. `check_output.py` enforces the parts of it a
tool can decide.

## References

| File | Read when |
|---|---|
| `references/structure.md` | Writing the sections — what each must contain, and the transitions |
| `references/diagrams.md` | Choosing diagram families; the HTML patterns; why never ASCII |
| `references/quiz.md` | Writing questions that test understanding rather than reading |
| `references/design.md` | Choosing a component, the colour tokens, how much emphasis a page can carry |
| `references/html-contract.md` | The file's hard constraints: self-contained, responsive, whitespace |
| `assets/template.html` | Always — start here rather than from an empty file |
| `assets/check_output.py` | Before claiming the page is finished |
