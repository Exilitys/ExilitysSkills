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

Long-form reading. `line-height` around 1.6, generous section spacing, a system
font stack for prose and a monospace stack for code:

```
-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif
ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace
```

Define colours once as custom properties on `:root`, then use the variables.
A dark-mode block via `@media (prefers-color-scheme: dark)` that overrides only
those variables is a few lines and prevents the page burning out someone's
eyes at night. Never give a colour its only definition inside the dark-mode
block.

**Never encode meaning in colour alone** — added/removed lines, correct/wrong
quiz answers. A symbol or a label alongside it.

## Callouts

For a definition, a key concept, an edge case, or something that would
otherwise read as a mistake. A left border, a tinted background, a bold lead-in
word. The template has `.callout`, `.callout.warn` and `.callout.key`.

Use them sparingly. On a page where every third paragraph is a callout,
nothing is emphasised.

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
outside a git repository, and that the quiz wiring is complete. Paste the
output. A page reported as finished on the strength of intent is how the
one-line code block ships.
