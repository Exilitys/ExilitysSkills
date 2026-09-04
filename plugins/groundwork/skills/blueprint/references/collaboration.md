# Collaboration - the spec is written *with* the user, not *for* them

The failure this file exists to prevent is **approval theatre**: an agent works
alone through intake, interrogation and drafting, and presents a finished
twelve-section document for sign-off. Nobody can review that. They can skim it
and say "looks good", which is worse than no spec at all - it now carries a
signature, so every decision inside it reads as agreed when most were never
examined by anyone but the agent.

## The rule

> **Nothing enters the spec as settled unless the user settled it.**

Three ways that gets broken, all of them quiet:

| Failure | What it looks like | Why it survives review |
|---|---|---|
| **The big reveal** | one approval, at the end, on the whole document | too much to hold at once, so it gets skimmed |
| **The silent default** | the agent picks and reports; the user never saw that a choice existed | a decision nobody knew was being made cannot be argued with |
| **The wall of questions** | fifteen questions in one message | one answer covers three of them; the other twelve become assumptions |

## Checkpoints - where to stop, and where not to

Not everywhere. A user asked to approve every paragraph stops reading the
approvals, which returns you to theatre by a different route. The rule for
where to stop is groundwork's own gate logic: **stop where being wrong is
expensive to reverse.**

| # | Checkpoint | What is on the table | Comes before |
|---|---|---|---|
| 1 | **The restatement** | the problem, the user, the current workaround | any question - a misread premise makes every later answer wrong |
| 2 | **Assumption and scope** | the core assumption, in/adjacent/not | any technical decision |
| 3 | **Each decision cluster** | three to five related decisions, as they are made | the next cluster |
| 4 | **The first slice** | what gets built to prove the assumption | writing the final document |
| 5 | **The whole spec** | a re-read | sign-off |

Checkpoint 3 is the one that does the real work, and the one an agent working
at speed will skip. Decisions are agreed **in clusters as they are made**, not
in a batch at the end. Done properly, checkpoint 5 is a formality - the user
has already agreed to everything in the document. **If the final read produces
surprises, an earlier checkpoint was skipped**, and the correct response is to
go back to it rather than to defend the draft.

## Propose, do not announce

Every decision reaches the user as a choice they make, not a result they
receive.

> **Announcing.** "I've chosen Postgres for storage."
>
> **Proposing.** "Two realistic options. **Postgres** - the reporting
> requirement needs ad-hoc joins we cannot predict, and it is one fewer moving
> part; costs us the easy horizontal write path later. **DynamoDB** - scales
> writes without thinking, but the reporting requirement becomes a second
> system. I lean Postgres, because reporting is stated and the write volume is
> currently a guess. Which fits what you know about the load?"

What makes a proposal real rather than decorative:

- **The alternatives are genuine.** A recommendation flanked by two obviously
  worse options is an announcement in a costume - and it produces exactly the
  empty `Rejected.` row that `spec-format.md` exists to prevent.
- **You recommend.** "What would you prefer?" with no lean hands the work back
  to the person who asked for help. Have an opinion and show its reasoning.
- **Every option names what it costs**, the recommended one included. An option
  with no downside has not been thought about.
- **Say what would change your mind.** It tells the user which fact they hold
  is the one that matters, which is usually how the decision actually gets
  made.

## Silence is not agreement

An unanswered question stays **open**. It does not quietly become a decision, a
default, or an inference that graduates on its own.

This is enforced, not merely asked for: unanswered questions live in the spec's
`Open questions` section, and `check_spec.py` **fails an approved spec that
still has any.** Without that, "I'll assume X for now" becomes the product.

The same applies to a question the user answers partially. Answering "roughly
ten thousand" to "how many users, and how fast will that grow?" settles one
half; the other half stays open, and saying so is not pedantry - growth rate is
what decides the storage decision.

## One thing at a time

Small, related batches. Roughly **three to five questions per turn**, grouped
by subject, ordered so the one that blocks the most comes first.

A message containing fifteen questions gets one paragraph back that addresses
three of them, and the agent - having "asked" - treats the rest as covered.
That is the wall-of-questions failure, and it is the most common way a
collaborative process degrades into an extractive one.

## When the user delegates

"I don't care, you pick" is a legitimate and common answer. Record it as what
it is:

```markdown
- **Provenance.** Agent's call; @user delegated 2026-09-04.
```

That is **not** the same as a joint decision, and the difference matters later:
a delegated decision is cheap to overturn when its revisit condition fires, a
jointly-made one deserves the conversation again before it moves. Filing a
delegation as agreement erases that distinction and inflates how settled the
spec actually is.

## When you disagree

The user will overrule a recommendation. Two rules:

**Keep the losing argument.** Your reasoning goes into `Rejected.` with the
option you preferred. The argument that lost is precisely what a reader needs
in six months when the revisit condition fires - and if you were right, the
record is what makes that visible rather than embarrassing.

**Say it once, then build what they chose.** State the disagreement plainly,
with the specific cost you expect and what signal would show it arriving. Then
stop. Re-litigating a settled decision across turns is how a collaborator
becomes a cost, and it teaches the user to stop reading your objections - which
is expensive on the one that matters.

## Use their words

When the user says the sentence that settles something, put **their** sentence
in the spec, not a paraphrase in agent-voice. "It has to work for their
accountant, who has never used a terminal" is a better requirement than
anything a rewrite would produce, and citing it makes the provenance real
rather than administrative.

## Contribute, do not only extract

`interrogation.md` harvests what the user already knows. Collaboration also
owes them what they do not.

If you can see a failure mode they have not mentioned, a simpler shape, a
decision that will hurt in month three, or a thing that already exists and
would remove half the project - **say it unprompted**, at the checkpoint where
it is still cheap to act on. A skill that only asks questions is a form, and a
form is not a collaborator.

The strongest version of this is the uncomfortable one: **if the honest
conclusion is that the project should not be built, or should be bought instead
of built, say so.** That is the most valuable output this skill can produce,
and it is never reached by a process that treats the project as a given.
