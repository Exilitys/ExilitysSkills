# The HTML contract

Hard constraints on the produced file. Most are checkable, and
`assets/check_output.py` checks them — run it rather than trusting that you
followed this page.

## One self-contained file

CSS in a `<style>` tag, JS in a `<script>` tag, images inlined as data URIs or
drawn as inline SVG. **No external requests of any kind** — no CDN, no Google
Fonts, no remote images.

The reason is not purity: this file gets emailed, dropped in a chat, opened on
a plane, and read in three years. Every external reference is a way for it to
degrade quietly into a broken page. A system font stack costs nothing and
always works.

## The whitespace trap

The single most common defect in these pages:

> A code block in a styled `<div>` collapses every newline into one line,
> because HTML collapses whitespace by default. The page looks fine while you
> write it and arrives as one unreadable line.

**Use `<pre>`.** If a design genuinely needs a `div`, its CSS *must* carry
`white-space: pre` or `pre-wrap`.

Before saving, scan every code block in the source and confirm it. The checker
does this mechanically — a rule a tool can check should not be left to a
careful reading.

Inside `<pre>`, escape `<`, `>` and `&`. An unescaped generic type or JSX tag
becomes a real element: it vanishes from the render and can swallow everything
after it.

## Structure

- **One long page.** Section headers, a table of contents at the top that links
  to them. No tabs at the top level — hidden content is content the reader will
  not find.
- Anchor IDs on every section, stable and readable (`#intuition`), so the page
  can be linked into at a specific point.
- The TOC should be short enough to take in at a glance. Two levels at most.

## Responsive

It will be read on a phone. That costs one media query and three habits:

- `<meta name="viewport" content="width=device-width, initial-scale=1">`
- Body text capped around `70ch`, centred, with real padding at small widths.
- Anything that cannot shrink — a wide `<pre>`, a table, a side-by-side
  diagram — goes in a container with `overflow-x: auto`, so it scrolls itself
  instead of forcing the whole page sideways.
- Side-by-side comparisons stack vertically under about 640px. A two-column
  before/after is unreadable on a phone.

## Type and colour

Fonts are the system stacks, so there is nothing to load and nothing to fail:

```
-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif
ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace
```

Colours are custom properties defined once on `:root`, with a
`@media (prefers-color-scheme: dark)` block overriding the same names and
nothing else in the file naming a colour directly. Two failures follow from
breaking that, and both are checked: a token defined *only* in the dark block
is undefined in light mode, and a colour literal outside those two blocks
cannot be overridden by either.

The rest of it — the type scale, what each token means, the components that use
them, and how much emphasis a page can carry — is `design.md`. This page stops
at the constraints the file itself has to satisfy.

## Where the file goes

Outside the repository, filename beginning with today's date:

```
<tmp>/2026-01-12-explanation-retry-backoff.html
```

The date prefix keeps the files time-sorted; being outside the repo keeps them
out of version control, which is where a generated artifact does not belong.

**Do not hardcode `/tmp`** — it does not exist on Windows, where this repo's
tooling is primarily used. `assets/write_target.py` picks the right directory
per platform and prints the path; use it, or honour `EXPLAIN_DIFF_OUT` if the
user has set it.

## Before claiming it works

```bash
python assets/check_output.py <path>
```

It verifies the whitespace rule on every code block, that no external resource
is referenced, that the filename carries the date prefix, that the file is
outside a git repository, that the quiz wiring is complete, and the design
rules that are mechanically decidable — the colour tokens, uncaptioned
diagrams, classes with no CSS behind them, and how much of the page is shouting
(`design.md`). Paste the output. A page reported as finished on the strength
of intent is how the one-line code block ships.
