# Design

The page has one job: a reader gets through a long explanation and comes out
with a working model. Every design decision is therefore a legibility decision,
and the way these pages fail visually is never ugliness — it is a reader who
cannot tell which parts matter, because everything on the page is shouting.

## The one rule

> **The template's components are the whole vocabulary. Extend them; never
> invent alongside them.**

This is `diagrams.md`'s argument applied to the page. Every new visual grammar
costs the reader a re-orientation — they stop reading and start decoding. A
page built from one small set reads as one document, and the second time a
reader meets a shape they take it in at a glance.

Four ways it breaks, in the order they actually happen:

| Failure | What it looks like | What it costs |
|---|---|---|
| **Invented** | a fresh `.tip` div, styled from scratch | a class with no CSS renders as bare text; the checker warns |
| **Repurposed** | a callout holding a code excerpt | the signal stops meaning one thing, so it means nothing |
| **Inflated** | every third paragraph is a callout | the emphasis budget is spent and nothing reads as emphasised |
| **Restyled inline** | `style="background:#eef"` on one node | dark mode cannot override it; it burns out at night |

If a component genuinely does not exist for what you are showing, extend the
nearest one — a modifier class beside `.callout.warn`, a variant of `.node` —
so it inherits the tokens, the dark mode and the responsive behaviour.

## The catalogue

Everything the template already gives you, and what each one is *for*. The
right-hand column is the part that matters: a component used for the wrong job
is worse than no component, because it teaches the reader a false signal.

| Component | Class / tag | Use it for | Not for |
|---|---|---|---|
| Body prose | `<p>` in `<main>` | the argument itself | anything you want noticed |
| Aside | `.callout` | a definition, a piece of context, a thing that reads as a mistake until explained | a paragraph you liked |
| Key idea | `.callout.key` | the single sentence the change turns on | any other emphasis |
| Trade-off | `.callout.warn` | what this costs, a trap, an edge case | ordinary caveats |
| Code | `<pre>` | code, output, data — **always**, see `html-contract.md` | prose you want in monospace |
| Inline code | `<code>` | an identifier, a path, a literal value | emphasis |
| Table | `<table>` in `.scroll-x` | three or more things compared across the same columns | two things (use `.compare`) |
| Flow | `.diagram` > `.row` > `.node` + `.arrow` | a sequence of calls or messages, with example data on the arrows | decoration between paragraphs |
| Before / after | `.compare` | the same diagram family twice, with the delta marked | two unrelated pictures |
| Caption | `.caption` | one line under every diagram saying where to look | naming what the diagram is |
| Contents | `nav.toc` | the four sections, two levels at most | a full outline |
| Skip marker | `.skip-note` | the one link past deep background | any other aside |
| Question | `.q` + `ANSWERS` | the five quiz questions — see `quiz.md` | mid-page rhetorical questions |
| Changed lines | `.add` / `.del` in a `<pre>` | added and removed lines, always with a `+` / `-` glyph | colouring prose |
| Subtitle | `.subtitle` | the one line naming the change and its target | a second title |

## Choosing one

Most of the work is a single decision made repeatedly: *what am I actually
showing?* Answer that literally and the component follows.

| What you are showing | Reach for | Instead of |
|---|---|---|
| A sequence of calls or messages | `.diagram` with data on the arrows | a paragraph narrating the sequence |
| The same shape before and after | `.compare`, same family both sides | two paragraphs the reader must hold at once |
| Three or more options across the same criteria | a table in `.scroll-x` | a bulleted list of prose |
| One rule the reader must carry forward | `.callout.key` | bold text mid-paragraph |
| A cost, a trap, a surprising constraint | `.callout.warn` | a parenthetical |
| The lines that carry the idea | a `<pre>` excerpt | the whole hunk, or an image of code |
| Something geometric — a tree, a timeline, an overlap | inline `<svg>` with a `viewBox` | ASCII art, ever |

When two components would both work, take the quieter one. Prose that reads
well is not improved by being put in a box.

## Colour is a token, never a literal

`:root` defines the palette twice — the base block for light, the
`prefers-color-scheme: dark` block overriding the same names for dark. Every
other rule in the stylesheet says `var(--x)` and nothing else. Two rules follow,
and the checker enforces both:

- **Every token gets its light value in the base `:root`.** A token defined only
  inside the dark block is undefined in light mode, so `var(--it)` resolves to
  nothing: invisible text, transparent panels. The page looks perfect to whoever
  wrote it in dark mode and is broken for everyone else.
- **No colour literal outside those two blocks.** A hardcoded `#fff` is a
  light-mode assumption that dark mode has no way to override. If you need a
  colour that does not exist, add the token *pair* — light value and dark value —
  and use the variable. The one reasonable exception is a translucent overlay
  (`rgba(0,0,0,.05)` for a shadow), which works over either background.

The palette is semantic, not decorative. Each token already means something, so
using it for anything else quietly lies to the reader:

| Token | Means | Where it already appears |
|---|---|---|
| `--accent` | interactive, or the reader's own path through the page | links, focus and hover borders |
| `--ok-*` | correct, or the state after the change | `.callout.key`, `.add`, a right quiz answer |
| `--no-*` | wrong, or the state removed | `.del`, a wrong quiz answer |
| `--warn-*` | the cost, the trap | `.callout.warn` |
| `--surface` | anything raised off the page | `pre`, `nav.toc`, `.diagram` |
| `--muted` | secondary text that must not compete | captions, labels, `.node .meta` |

**Never encode meaning in colour alone.** Roughly one man in twelve cannot
separate your green from your red, and nobody at all can separate them in a
printed handout. Every coloured state on the page already carries a second
signal — `+` and `-` on diff lines, `✓` and `✗` on quiz options, the uppercase
label on a callout — so when you add a state, give it one too.

## Type, space, and the shape of a long read

Prose in the system font stack, code in the monospace stack, both defined once
as `--sans` and `--mono`. Around 17px at a 1.65 line-height, with the measure
capped at 70ch: a line longer than that loses the reader on the return sweep,
which is why the constraint is in the template rather than left to taste.

Space does the sectioning, so nothing else has to. An `<h2>` already carries a
rule above it and a wide margin; adding coloured bars, boxed sections or
horizontal dividers between them is three signals for one boundary. Never
centre body text and never justify it — browsers do not hyphenate well, and
justification opens rivers of white space down the column.

`html-contract.md` carries the responsive rules, and they are design decisions
rather than compliance: the `.compare` grid collapsing to one column under
640px and the arrow glyph flipping from `→` to `↓` are what keep a diagram
readable on a phone, which is where a surprising share of this reading happens.

## The emphasis budget

A page has a fixed amount of *look here*, and callouts, diagrams and bold text
all spend from the same pot. Overspending does not produce a more emphatic
page; it produces a flat one, because the reader stops trusting that the boxes
mean anything.

Working ceilings for a page of the usual length:

- **One `.callout.key`.** The change turns on one idea. If you have two, one of
  them is background.
- **A callout roughly every six paragraphs, at most.** The checker warns past
  that.
- **Three to six diagrams**, from two or three reused families. Zero is also a
  failure — the intuition section is where a picture does the work prose cannot.
- **Bold for a term being defined**, not for a sentence you want read twice.
  A sentence that needs that is a callout, or is in the wrong place.

The test, from `diagrams.md`, applies to every visual element on the page: ask
what the reader loses if you delete it. If the answer is nothing, delete it.

## What the checker enforces

`check_output.py` covers the design rules that are mechanically decidable, for
the same reason the rest of this plugin does — a careful reading is exactly
what stops happening at the end of a long task:

| Check | Level |
|---|---|
| A custom property defined only in the dark-mode block | fail |
| A colour literal outside `:root` and the dark block | warn |
| A `.diagram` with no `.caption` | warn |
| A class used in the markup that no CSS rule defines | warn |
| More than one `.callout.key`, or callouts denser than one per six paragraphs | warn |
| No diagram or inline SVG anywhere on the page | warn |

Everything above this table is still yours to get right. The checker can prove
the page is one visual system; it cannot tell you the system was the right one.
