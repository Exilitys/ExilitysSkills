# Acceptance - a human accepts, or it is not accepted

groundwork's contract gate says *"spec, approval, then build"*. This file is
what **approval** means, for every artifact produced before code is written: a
spec, a plan, a generated context document, an architecture diagram.

## The rule

> **An agent never records its own approval.**

Everything a planning phase produces arrives as a **draft**. It stays a draft
until a human says otherwise, and the agent's only job at that moment is to
record *who* said it and *when*. An agent that can write `Status. Approved` on
its own work has not passed a gate - it has written one on a sign it holds up
in front of itself.

`check_spec.py` enforces this: a spec marked approved with no named human
approver fails.

## What is gated

Everything downstream depends on these, and every one of them is cheap to wave
through and expensive to have been wrong about:

| Artifact | Produced by | Gated before |
|---|---|---|
| The spec | blueprint step 4 | handoff to groundwork |
| The architecture diagram | blueprint step 6 (`archify`) | the same gate - it is part of the packet |
| The build plan | groundwork Lane 1 step 5 | any file is edited |
| Generated context docs | groundwork bootstrap step 4 | they become the project's truth |
| A spec for a contract path | Lane 1 step 3 | the gate at step 4 releases |

**A plan is not a lesser artifact than a spec.** It decides sequence,
what gets built first, and what is deferred - and it is the document most often
generated, skimmed and executed, because it looks like a checklist rather than
a decision. Gate it the same way.

## The review packet

A human reviewing well needs more than the document. Hand over five things:

1. **The artifact itself**, at its path.
2. **The diagram** (see below). A reviewer sees a wrong boundary in a picture
   in seconds and misses it in twelve sections of prose.
3. **What changed since they last looked**, if this is not the first round.
   A re-read of an unchanged document finds nothing; a diff finds everything.
4. **The open questions**, named, with what each blocks.
5. **Where you want them to look hardest** - the two or three places you are
   least confident, and why. An agent that presents everything as equally solid
   has made the reviewer do the triage you were better placed to do.

Then **stop and wait.** Not "let me know if you'd like changes" while
continuing - the next step does not start.

## The acceptance record

When they accept, record it in the artifact:

```markdown
**Status.** Accepted 2026-09-04 by @user
**Reviewed.** v3 (after the storage decision changed); diagram in
`docs/architecture/system.md`
```

Three facts, each load-bearing:

- **Who.** A name, not "the user". If two people review, both.
- **When.** The date the human said yes, not the date the agent wrote it.
- **What.** Which version they saw. An artifact edited after acceptance is no
  longer the artifact that was accepted - see below.

## Change requests are the normal path

A reviewer asking for changes is the gate **working**, not a failure of the
draft. Treat it as a continuation of `collaboration.md`:

- **Change what they asked**, and only that. A revision that also quietly
  improves three other sections forces a full re-read and burns the trust that
  made the review quick.
- **Push back once when you disagree**, with the specific cost and the signal
  that would show it arriving. Then do what they decided, and keep your
  argument in the decision's `Rejected.` row.
- **Re-present the diff**, not the whole document. Round two should be
  reviewable in a minute.
- **A change that overturns a decision** gets a new decision record superseding
  the old one, not an edit in place. The overturned record stays visible.

There is no round limit. A spec that took four rounds is a spec four rounds
better, and the rounds are cheap compared to building the wrong thing.

## After acceptance

An accepted artifact is frozen in the sense that matters: **the agent does not
edit it silently.** Later changes go one of two ways:

| Change | Path |
|---|---|
| Corrects a typo, a broken link, a formatting slip | edit freely; acceptance survives |
| Changes what gets built, a decision, a sequence, a number | new round: amend, re-present the diff, re-record acceptance |

When the build contradicts an accepted spec - which it will - that is a
**re-entry**, per `handoff.md`. The decision record gets a superseding entry
and the status returns to draft until the human accepts the amendment. A spec
quietly edited to match what was built is no longer a spec; it is a
transcript, and it can never again be used to notice that something went wrong.

## What acceptance is not

- **Not silence.** A user who did not reply has not accepted. Same rule as
  `collaboration.md`: silence is not agreement, and it is not approval either.
- **Not "looks good" to a wall of text.** If the packet was too large to
  review, an approval against it is theatre with a signature. Split it and
  re-present.
- **Not transferable.** Acceptance of the spec is not acceptance of the plan.
  Each artifact is gated on its own, because each contains decisions the other
  does not.
- **Not the agent's to infer.** "They didn't object to the diagram" is not
  acceptance of the diagram.
