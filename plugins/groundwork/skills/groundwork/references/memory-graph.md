# Memory - the graph and the three tiers

## Why a graph

The most token-expensive question in a coding loop is the ladder's rung 2:
*"does this already exist here?"* Answered with grep it costs many reads and
still misses things named differently. Answered with a code graph it is one hop.

A graph tool that does AST extraction gives you that for **zero model tokens**,
because parsing is deterministic. That is the half worth wiring into every lane.

## The cost split — and the whole design

| Layer | Built by | Cost | Answers |
|---|---|---|---|
| **Code graph** | AST parsing | **free** | does it exist · who calls it · what breaks if I rename it |
| **Docs / decision graph** | model-driven extraction | tokens, rebuilt rarely | why was this decided · what connects this decision to that one |

Build the free layer first and always. Treat the paid layer as opt-in, rebuilt
only when documents change — which is rare compared to code.

**Never spend the paid layer's tokens without asking.** It needs subagents and
real budget; the free layer needs neither.

## Wiring it into the lanes

| Lane step | Instead of | Do |
|---|---|---|
| Orient | — | check graph freshness; stale is worse than absent |
| Explore intent | broad grep sweeps | query the graph |
| **Ladder rung 2** | grep and hope | explain the symbol — one hop |
| Bug: find every caller | grep the name | neighbour query on the node |
| Chore: rename | guess the blast radius | impact query first |
| Sync | — | rebuild (AST only, free) |

Automate the rebuild with a post-commit hook so the code layer cannot drift.
The `SessionStart` hook reports staleness rather than assuming freshness.

## Excluding noise

Vendored and minified assets will dominate a graph and mean nothing. A single
bundled library can produce two of your largest "communities" and no insight.
Exclude vendored directories and minified files before the first real build.

## The three memory tiers

A graph alone is not memory. Memory is three kinds of durable knowledge, and
most repos already have two of them without calling them that:

1. **Structural** — the graph. *What connects to what, right now.* Rebuilt
   mechanically; never hand-maintained.
2. **Episodic** — specs, plans, and verification reports. *What we did, when,
   and what the evidence actually showed* — including negative results, which
   are the ones nobody re-derives.
3. **Decision** — deferred items with explicit revisit conditions, plus
   corner-cut comments naming their ceiling and upgrade path. *What we chose not
   to do, and what would reopen it.*

Tier 3 is the one that prevents the expensive failure: rebuilding something that
was deliberately not built. A backlog entry that says "deferred, revisit only
if X" is worth more than a page of architecture, because it can *refuse* a
proposal on evidence.

Where a graph tool supports saving query answers back as nodes, use it — that is
what turns tier 1 from an index into accumulating memory.

## The failure mode

**A stale graph misleads exactly like a stale document**, and more confidently,
because it looks computed. Every guarantee here rests on the rebuild being
automatic and the freshness check being visible. If you cannot automate the
rebuild, report staleness loudly and prefer grep.
