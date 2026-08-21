# Diagrams

A diagram earns its place when it shows something prose makes the reader hold
in their head: a shape, a flow, a before/after. It does not earn its place by
restating a sentence in boxes.

## Pick two or three families and reuse them

The instinct is to invent a fresh visual per point. Resist it: every new visual
grammar costs the reader a re-orientation, and by the fourth one they have
stopped reading the diagrams. **A small family, reused, becomes legible** —
the second time a reader sees the same shape they read it in a glance, and the
third time they can predict what the change did before you say it.

Three families cover most changes:

### 1. Simplified UI

A stripped-down version of what the user sees — boxes, a label, a button. For
explaining a UI change without a screenshot that dates immediately.

Keep it obviously schematic. A diagram that nearly looks like the real product
invites the reader to check it against the product, and it will be wrong within
a release.

### 2. System / data flow

Components as boxes, arrows for calls or messages. The one thing that makes
these useful rather than decorative:

> **Put example data on the arrows.** `POST /sync {rev: 4}` teaches; a bare
> arrow labelled "request" does not. The data is the part a reader cannot infer.

Use the same toy values the intuition section already introduced. That is the
whole payoff of carrying one example through: by the third diagram, `alice` and
`rev: 4` are load-bearing and the reader is tracking a story rather than
decoding a new picture.

### 3. Before / after, side by side

Two instances of the *same* family, laid out together, with the difference
marked. This is the workhorse — most changes are best explained as a delta
between two pictures the reader has already learned to read.

Do not switch families between the before and the after. If the before is a
flow diagram, the after is a flow diagram; changing the grammar hides the
change inside the re-orientation.

## Never ASCII art

It breaks on every viewport, it cannot be styled, it is unreadable on a phone,
and it will not survive a copy-paste. **Use HTML.** Boxes are divs with a
border; arrows are a `::after` glyph or a styled span; a grid is
`display: grid`. Lists of things are `<ul>`, not lines of dashes.

The template's `.diagram`, `.node`, `.arrow` and `.compare` classes cover all
three families — extend them rather than starting over, so the page stays one
visual system.

## SVG

Fine, and inline only — the page must stay self-contained. Worth it for
anything genuinely geometric: a tree, a timeline, an overlap. Not worth it for
boxes and arrows, which are less code and more responsive as HTML.

Give every SVG a `viewBox` and no fixed pixel width, or it will overflow on a
phone. Use `currentColor` for strokes so it survives a theme change instead of
becoming an invisible black line.

## Captions

Every diagram gets one line underneath saying what to notice. Not what it is —
the reader can see that — but where to look: *"Note that the second write never
reads the row it overwrites."* A diagram with no caption is a diagram the
reader skims past.

## The check

Before keeping a diagram, ask what the reader would lose if you deleted it. If
the answer is nothing, delete it. Three diagrams that each carry an idea beat
nine that decorate paragraphs.
