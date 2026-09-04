<!--
  blueprint scaffold. Replace the content; keep the structure.

  Two things check_spec.py will fail you on, so do them as you write:
    - every decision record has a `Rejected.` line (write
      `Rejected. Default, not evaluated.` when it genuinely was one)
    - every Deferred row has a `Revisit when.` condition

  Omit a section the project has no answer for. An empty heading implies a
  ruling nobody made.
-->

# <Project> - specification

**Status.** Draft | Approved YYYY-MM-DD
**Owner.** <who signs off>
**Supersedes.** <earlier doc, or none>

---

## 1. Problem

<The situation somebody is in today. Not a missing feature - a person, mid-task,
hitting something. Two or three sentences.>

**What they do instead today.** <The workaround. This is the competitor and the
bar to clear. If the answer is "nothing", say so - it is a risk, not a gap.>

## 2. Users

| Who | What they do today | What changes for them |
|---|---|---|
| <specific role> | <workaround> | <the observable difference> |

<"Everyone" is not a user. If you cannot name one specifically enough to
disagree with, section 1 is not finished.>

## 3. The core assumption

> <The one thing that must be true for this to be worth building.>

**How we would know it is false.** <An observable outcome. An assumption that
cannot come back negative is not an assumption, it is a slogan.>

## 4. Scope

**In.** <what is being built now>

**Adjacent, later.** <real, wanted, explicitly not now - each becomes a
Deferred row in section 11>

**Not this product.** <three things a reader would reasonably assume are
included and are not. The cheapest section in the document.>

## 5. Decisions

<The spine. One record per decision, numbered. Cite them from everywhere else.>

### D-001 - <the decision, as a noun phrase>

- **Chosen.** <what>
- **Rejected.** <the real alternatives, named, with why each lost. If it was
  genuinely a default: `Default, not evaluated.`>
- **Because.** <the reason, tied to a constraint or requirement - not taste,
  not industry convention>
- **Revisit when.** <the condition that would overturn this>
- **Provenance.** <who, and the date. `Decided <date> with @user` when they
  chose from options; `Agent's call; @user delegated <date>` when they
  declined to; these are different facts and cost different amounts to
  overturn.>

<!-- Duplicate the D-001 block above for D-002, D-003, ... -->

## 6. Data model

### <Entity>

| Field | Type | Notes |
|---|---|---|
| id | uuid | |
| <field> | <type + unit> | |

- **Owned by.** <which principal; what happens to the row when it is deleted>
- **Lifetime.** <created by what, deleted by what, archived when>
- **Source of truth.** <when this fact lives in two places>
- **States.** <explicit list + legal transitions, or "none">

## 7. Interfaces and seams

<The shape, not a description of the shape. Signatures, schemas, or sample
payloads - something an engineer can disagree with precisely.>

```
POST /<path>  { <field>: <type> }
  -> 202 { <field>: <type> }
  -> 409 when <the concurrency rule>
```

**Seams.** <the boundaries this design commits to - these become groundwork's
first contract paths once code exists at them>

## 8. Failure behaviour

| When this fails | The system | Who finds out |
|---|---|---|
| <dependency> | <retries / rolls back / degrades / surfaces> | <user / alert / nobody> |

<The section most often missing and most often invented by whoever writes the
code at 2am.>

## 9. Non-functional targets

| Target | Number | Measured by |
|---|---|---|
| <e.g. import latency> | <p95 under 30s at 50k rows> | <the test or dashboard> |

<Numbers and their measurement. "Fast", "scalable" and "secure" are not
targets - each is a number, a test, or a decision not yet made.>

## 10. Risks

| Risk | Early signal | If it fires |
|---|---|---|
| <what could make this fail> | <what we would see first> | <the response> |

## 11. Deferred

<Consciously not decided. Each one needs a condition, or it is a decision
being avoided rather than deferred.>

- **<Item>.** Not decided. **Revisit when** <the condition>.

## 12. The first slice

<The smallest build that proves or disproves section 3.>

**It proves.** <which part of the core assumption>
**It does not include.** <the obvious things it leaves out>
**Done when.** <the observable, falsifiable outcome>

<Tests: could one Lane 1 pass build it? Does it prove the assumption rather
than just producing a working screen? Is it allowed to come back negative?>

## 13. Open questions

<Asked and not answered. Silence is not agreement, so it lives here rather than
becoming an assumption. A draft is expected to carry these; an approved spec
may not - check_spec.py fails on it.>

- **<Question>.** Asked <date>, not answered. Blocks <D-00N / which section>.
  **If unanswered at build time:** <what happens by default>.
