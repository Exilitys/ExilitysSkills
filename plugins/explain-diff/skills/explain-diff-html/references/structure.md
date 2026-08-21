# The four sections

One long page, section headers, a table of contents at the top. **No tabs for
the top-level structure** — tabs hide content, and a reader who cannot see that
a background section exists will not go looking for it.

The sections are ordered by what the reader can absorb, not by what is easiest
to write. Each ends by raising the question the next one answers.

---

## 1. Background — the system before the change

The section that decides whether the page works, and the one most often skipped
because it is the only one that cannot be written from the diff.

**Two passes, and mark the first one skippable.** You do not know who is
reading. A beginner needs the domain and the shape of the system; a teammate
needs neither and will bounce off a page that makes them scroll through it.

### Pass 1 - deep background

For a reader who does not know the domain. The concepts, the vocabulary, the
shape of the system in the region of the change. Open it with an explicit
marker so the informed reader can skip:

> **New to this part of the system?** This section builds up from first
> principles. If you already know how <X> works here, skip to <Pass 2>.

Make that a real link to the next heading, not a sentence hoping for
cooperation.

### Pass 2 - narrow background

The specific mechanism this change touches, for a reader who knows the system
generally but not this corner. The function and its callers, the invariant that
holds today, the data as it is currently shaped.

End with the tension: what this design does not handle, what broke, what was
asked for. The reader should reach the next section already wanting the answer.

**Both passes describe the world *before*.** Nothing here is in the past tense
relative to the change — write it as the reader would have found it that
morning. Introducing the change here steals the intuition section's job and
leaves the reader with two half-explanations.

---

## 2. Intuition — the essence, on toy data

The core idea, small enough to hold in your head. If a reader stops after this
section they should be able to describe what the change does and why, without
having seen a line of the real code.

**Rules that keep it honest:**

- **Toy data, named and concrete.** Three users, two rows, one request. Not
  "the collection" — `[alice, bob, carol]`. Real values make an argument
  checkable; abstractions let a hand-wave pass.
- **One example, carried through.** The same toy case through the before, the
  problem, and the after. A new example per point makes the reader re-orient
  three times and hides whether the pieces fit together.
- **Diagrams liberally**, from a small reused family — `diagrams.md`.
- **No real code here.** Real identifiers, error handling and edge cases are
  the next section's job. Reaching for them here is the most common way this
  section fails: it becomes a code walkthrough with worse structure.

Show the before state, then the problem in that state, then the after. The
change is the difference between two pictures the reader has already seen —
which is what makes it feel inevitable rather than arbitrary.

State the trade-off. Every change costs something; a page where the new design
is better in every respect is a page the reader will not believe, correctly.

---

## 3. Code — the walkthrough

Now the real thing, at altitude.

**Group by idea, never by file.** File order is an artifact of the filesystem.
Lead with the change that carries the idea — usually one function — and let the
rest hang off it: what had to change to support it, what changed only because a
signature moved.

A structure that works, when it fits:

1. **The core change.** The one hunk that *is* the idea.
2. **What it required.** Call sites, types, schema, config.
3. **Mechanical fallout.** Renames, generated files, import churn — one line,
   grouped, not enumerated. "The rename touched 34 call sites; none of them
   interesting."
4. **Tests.** What they pin, which is the clearest statement of intended
   behaviour anywhere in the diff.

**Show excerpts, not the diff.** Pull the handful of lines that matter, in
`<pre>` blocks, and say what each is doing. A reader who wants every line has
the diff; what they cannot get from the diff is which lines matter.

Name files as `path/to/file.ts` so they can be found. Where a change looks
wrong until you know something — a guard for a case three layers up, an order
that matters — that is exactly where a callout goes.

---

## 4. Quiz — five questions

Interactive multiple choice, immediate feedback on click. Full guidance in
`quiz.md`.

Medium difficulty: answerable only by someone who understood the substance, not
gotchas. The point is a reader checking themselves, not a test they can fail.

Close the page after it. One short paragraph: what the change does, in one
sentence, now that the reader has everything needed to understand it — and
anything left genuinely unexplained, named plainly.

---

## Transitions

The sections are one argument, not four documents. Each should end pointing at
the next:

- Background -> Intuition: the tension. *"So a second reader arriving mid-write
  sees a row that no longer exists. The fix turns on one observation."*
- Intuition -> Code: from the picture to the machinery. *"That is the whole
  idea. The rest is where it lives."*
- Code -> Quiz: an invitation, not an exam. *"If that all landed, the questions
  below should be straightforward."*

Never open a section by announcing itself. "In this section, we will examine
the background" is a heading restated in a sentence — cut it and start with the
subject.
