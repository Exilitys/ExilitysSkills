# The tooling floor

Every candidate rule gets one question: **can a tool check this?** If yes it
becomes config. Prose keeps only the residue.

This is not a style preference. Projects that wrote the rule down three times
still drifted; the check is what held.

## Triage

| Rule shape | Goes to |
|---|---|
| Layering / dependency direction | an import linter contract |
| "Never import X in Y" | import linter, or a banned-import lint rule |
| Type discipline | a type checker |
| Formatting, import order, modern idioms | the formatter/linter |
| "Always use component Z instead of hand-rolling" | a duplication test |
| Closed scales (radii, spacing, type sizes) | a test that fails on arbitrary values |
| Contrast / a11y floors | a test reading the theme file |
| "The docs must describe things that exist" | an integrity test |
| When to add an abstraction | **prose** |
| Why a rule exists | **prose** |
| Error taxonomy, wiring policy | **prose** |

## The four that pay for themselves

### 1. Layer enforcement

If the architecture has a dependency direction, nothing else checks it. A single
inward-pointing violation passes linting, tests, and type checking. This is
usually the single highest-value addition to a mature codebase, and it often
passes on the first run — the discipline was real, it just had no guard.

Use a *forbidden* contract alongside the layers one to keep the inner layer
framework-free. Allow the data-modelling library if the domain genuinely uses it;
ban the web, ORM, and model-provider packages.

### 2. Type checking, scoped

Do not turn strict mode on everywhere at once. Strict on the **pure core**
(domain, use-cases) where there are no third-party typing pathologies; basic at
the edges where the ORM and model SDK live.

Its unique value is finding what layer linting structurally cannot: right
module, **wrong shape** — a concrete class not satisfying the interface it is
wired into, a call passing a parameter that does not exist, an optional accessed
without a guard. A first run on an unchecked codebase surfaces things nobody has
looked at in months.

### 3. Duplication / closed-scale tests

Walk the source, fail on the patterns a primitive already owns and on arbitrary
values outside a named scale. Keep it **narrow** — each rule should encode a
duplication that was actually measured, not taste. A test encoding taste is
noise, and noise gets suppressed.

### 4. The integrity test

The context files must describe things that exist. Extract identifiers and paths
from them; assert each resolves. Costs ~80 lines and catches the exact rot that
makes a context system worse than none.

## Landing a checker that starts red

You will add a checker and get 50 errors. Do not leave it blocking.

**A permanently-red check teaches everyone to ignore the suite**, which costs
more than the check gains. Instead:

1. Land it **advisory** — configured, running, not gating.
2. Record the current count and the finding classes.
3. File the cleanup as work **with an explicit condition**: *"becomes a gate when
   the count reaches 0."*

That is the same deferral-with-condition discipline used for product decisions,
applied to tooling. It is honest about the state, and it makes the promotion
automatic rather than a judgment call later.

The same applies to closing a scale that is currently open — document the
intended scale, count the drift, and gate the test on the count reaching zero.

## Reporting

When a new checker finds probable **defects** (not just annotation gaps),
separate them out and name them individually. A type checker's first run is the
one time those get looked at. Do not fix them inline — they need reproduction,
which is Lane 2, not a drive-by in a tooling change.
