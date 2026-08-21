# The quiz

Five multiple-choice questions, answered in the page, feedback on click.

Its job is **a reader checking themselves**, not a test they can fail. Nobody
is grading this; the value is the moment a reader discovers they had understood
something backwards, while the explanation is still on screen.

## What makes a good question

**Medium difficulty: unanswerable without the substance, obvious with it.**
Both failure directions are real:

- **Too easy** — answerable from the wording, or from general programming
  sense. If a reader who skipped straight to the quiz can get it, it tests
  nothing.
- **A gotcha** — turning on a detail nobody would retain, an off-by-one in a
  variable name, a fact stated once in passing. It teaches that the page was
  full of traps, and the reader stops trusting their own understanding, which
  is the opposite of the point.

**Test the model, not the text.** The best questions ask what would happen in a
situation the page never explicitly covered but fully equipped the reader for:

- *"If two clients call `sync` with the same revision, which one wins, and why?"*
- *"What breaks if the cache is populated before the migration runs?"*
- *"Why does the guard live in the caller rather than inside the function?"*

Each is answerable from a correct mental model, and not otherwise. That is the
target.

**Cover the change, not one corner.** Roughly: one on the background (did they
absorb the world before), two on the intuition (the core mechanism and its
trade-off), one on the code (where something lives and why), one on an
implication or edge case. Five questions on the same hunk measure one thing.

## Distractors

**Wrong answers must be plausible.** Three obviously-silly options make a
one-option question. The distractor to aim for is the thing a reader would
believe if they had the *almost* right model — the previous behaviour, the
approach that was considered and rejected, the plausible-but-wrong ordering.

That is what makes the feedback worth reading: it names a specific
misunderstanding and corrects it.

## Feedback

Every option gets feedback, not only the wrong ones.

- **Correct** — say briefly *why* it is right. Confirmation without a reason
  leaves the reader unsure whether they reasoned or guessed.
- **Wrong** — name the misunderstanding, then correct it, then point at the
  section that covers it. *"That was the behaviour before this change — the
  ordering flipped in the retry path; see Intuition."*

Never just "Incorrect." A wrong answer is the most valuable moment in the page
and dismissing it wastes the only leverage the quiz has.

## Mechanics

The template has this wired; keep its behaviour:

- Click an option to reveal feedback. No submit button, no score.
- Correct and chosen-wrong are distinguished by **more than colour** — an icon
  or a text label — or the page fails for colourblind readers.
- Answering one question does not affect the others; a reader may skip.
- Feedback appears inline, below the option list, and stays. Do not use
  `alert()`.
- Once answered, keep the options visible so the reader can compare.

Store the answer key in a JS object rendered into the page, not in `data-`
attributes on each option where a curious reader trips over it — though do not
pretend this is secure. It is a self-check; anyone who wants the answers can
read the source, and that is fine.
