# The spec - sections, depth, and how each one fails

`assets/spec-template.md` is the scaffold. This file is what goes in it and
what a bad version of each section looks like.

## The depth test, applied per section

> Two competent engineers building this independently produce systems that fit
> together.

Run it per section rather than over the whole document. It sorts detail into
earned and padded faster than any word count:

- **Earned.** Data shapes, interfaces, ownership, states, failure behaviour,
  units, boundaries. Two engineers disagree here unless it is written.
- **Padded.** Restating a chosen framework's defaults, enumerating symmetric
  CRUD, describing a screen that a wireframe already shows.

A spec that is thin on the first list and thick on the second is the common
failure, and it is worse than a short spec because its length reads as rigour.

## Section order

Problem first, decisions second, surface third. Anyone who reads only the first
two sections should be able to argue with the project.

| # | Section | Job | Fails when |
|---|---|---|---|
| 1 | **Problem** | the situation somebody is in today, and what they do instead | it describes a missing feature rather than a person's problem |
| 2 | **Users and the alternative** | who, specifically, and the workaround being replaced | "everyone" - a spec that cannot name a user cannot rule anything out |
| 3 | **The core assumption** | the one thing that must be true for this to be worth building | it is unfalsifiable, so nothing can prove it wrong |
| 4 | **Scope** | in / adjacent-later / explicitly not | the third list is missing, which is the one that prevents arguments |
| 5 | **Decisions** | the decision records - the spine of the document | entries with no *rejected* row |
| 6 | **Data model** | entities, ownership, lifetime, source of truth | fields listed without ownership or lifetime |
| 7 | **Interfaces and seams** | the boundaries, in signatures or schemas | prose descriptions of an API instead of its shape |
| 8 | **Failure behaviour** | what happens when each dependency fails | absent - the most common missing section in any spec |
| 9 | **Non-functional targets** | numbers, with how each is measured | adjectives: fast, scalable, robust, seamless |
| 10 | **Risks** | what could make this fail, and the early signal for each | a list of generic project risks |
| 11 | **Deferred** | what was consciously not decided, each with a revisit condition | a decision hidden here to avoid making it |
| 12 | **The first slice** | the smallest build that proves section 3 | it is the whole product with a smaller font |

Sections a project genuinely has no answer for are **omitted, not stubbed** -
an empty heading implies a ruling that was never made.

## The decision record

The unit the whole spec is built from. Four fields, and the second is the one
that makes it a decision:

```markdown
### D-004 - Postgres for primary storage

- **Chosen.** Postgres, single primary, managed.
- **Rejected.** DynamoDB - the access pattern is relational and reporting is a
  stated requirement. SQLite - loses the concurrent write path in section 8.
- **Because.** The reporting requirement (R-7) needs ad-hoc joins the team
  cannot predict at design time.
- **Revisit when.** Write throughput exceeds ~2k/s sustained, or a
  multi-region requirement lands.
- **Provenance.** Decided 2026-09-04 with @user; supersedes the "any SQL db"
  line in the original PRD.
```

Rules:

- **An empty *rejected* row means it was a default, not a decision.** Say so
  explicitly - `Default, not evaluated` - so the next reader knows how much
  weight it carries. Silently presenting a default as a decision is the lie
  this format exists to prevent.
- **The *because* ties to a constraint from interrogation**, ideally by
  reference (`R-7`, or a dated answer). "It is the industry standard" is not a
  reason, it is an appeal to a crowd that does not know this project.
- **Every locked decision carries provenance - who and when.** Same rule
  groundwork's gate enforces on specs, for the same reason: a decision without
  provenance is a guess wearing a spec's clothes.
- **Number them.** `D-001`. The numbers get cited by the build, by later
  specs, and by the backlog rows that revisit them.

## Requirements that can be falsified

Every requirement in the spec answers: **how would we know this is not met?**

| Not falsifiable | Falsifiable |
|---|---|
| The import should be fast | A 50k-row import completes in under 30s at p95 |
| The UI must be intuitive | A first-time user completes an import without opening docs, in 3 of 4 tests |
| Data must be secure | Rows are readable only by members of the owning org; verified by an access test |
| The system should scale | 500 concurrent imports with no queue growth over 5 minutes |

The left column cannot be built against, cannot be tested, and cannot be
argued with - which means it will be quietly interpreted by whoever writes the
code, and their interpretation becomes the product.

**Weasel words to hunt before saving:** fast, scalable, robust, secure,
intuitive, seamless, simple, flexible, modern, best-practice, real-time. Each
is a number, a test, or a decision that has not been made yet.
`assets/check_spec.py` flags them.

## Data model depth

The section engineers most often have to invent when it is missing. Per entity:

- **Fields with types and units.** `retention_days: int` beats `retention`.
- **Owner.** Which principal a row belongs to, and what happens to it when that
  principal is deleted.
- **Lifetime.** Created by what, deleted by what, archived when.
- **Source of truth**, when the same fact lives in two places.
- **States**, if it has any, as an explicit list with legal transitions. An
  entity with implicit states is where the concurrency bugs live.

## Interfaces

Write the shape, not a description of the shape. A signature, a schema, or a
sample payload - anything an engineer could disagree with precisely:

```
POST /imports  { file_id: str, mode: "replace" | "append" }
  -> 202 { import_id: str }
  -> 409 when an import is already running for this org
```

Prose - "an endpoint to start an import, which returns an id" - leaves the
error cases, the modes, and the concurrency rule to be invented later, and each
of those is a real decision.

## The first slice

The last section, and the one that makes the spec actionable. It names the
smallest build that would prove or disprove the core assumption in section 3.

Tests it must pass:

- **It could be built in one Lane 1 pass.** If it needs three, it is a
  roadmap, not a slice.
- **It proves the assumption**, rather than merely producing a working screen.
- **It is honestly allowed to fail.** A first slice that cannot come back
  negative was not testing anything.

Everything not in it is not "later" by vibe - it is a Deferred row with a
revisit condition, or it is out of scope.
