# Lanes - how work moves

Four lanes. The lane sets the ceremony. One workflow for everything either
over-plans a typo fix or under-plans a migration.

Announce which lane you are in. If you cannot tell, it is usually Lane 1 with a
small scope, or Lane 2 pretending to be Lane 3.

---

## Lane 1 - Slice

A new feature or user-visible capability.

| # | Step | Skill / action |
|---|---|---|
| 0 | Orient | branch, uncommitted state, open plans, graph freshness (the `SessionStart` hook prints these) |
| 1 | **Explore intent before designing** | `superpowers:brainstorming` — before plan mode, always |
| 2 | **Contract check** | path vs. the contract list |
| 3 | Spec | write to the project's spec directory. **Cite provenance — file and date — for every locked decision.** Stress-test with `grill-me` |
| 4 | **GATE** | contract path → stop, get approval. Otherwise continue |
| 5 | Plan | `superpowers:writing-plans` — checkbox tasks, global constraints |
| 6 | Isolate | `superpowers:using-git-worktrees` |
| 7 | Build | `superpowers:executing-plans` or `subagent-driven-development` |
| 7a | *before every file* | **climb the ladder** — need it? exists here? stdlib? platform? installed dep? one line? |
| 7b | Backend / pure logic | `superpowers:test-driven-development` — red, green, refactor |
| 7c | UI | build visually first with mock data, then write tests. Test-first on a component nobody has seen is theatre |
| 7d | UI craft | `ui-ux-pro-max` **fed the project's design brief as constraints** — see below |
| 7e | Primitives | shadcn's and Magic UI's registries, over MCP — `references/design-system.md`; `ui-styling` for Tailwind/a11y mechanics |
| 8 | Verify | `superpowers:verification-before-completion` — run the real commands, read the output |
| 9 | Prove | `/check verify` in the real app; `/check review` on a fresh model |
| 10 | Review | `superpowers:requesting-code-review` → `receiving-code-review` |
| 10b | **Explain it, if it is large or unfamiliar** | `explain-diff-html` — only when a reviewer would otherwise read it cold. See below |
| 11 | Write the prose | `/document pr` |
| 12 | Fold back | `/sync`, `finishing-a-development-branch`, rebuild the graph |
| 13 | If it needed proving | write a verification report — **including negative results** |

### When step 10b earns its place

An explanation page is a real cost — it means reading the surrounding code
properly, not just the diff — so it is opt-in, not routine. It pays when:

- the change is large enough that a reviewer will otherwise skim it;
- it lands in an area the reviewers do not know;
- it encodes a decision worth preserving past the review, which a PR thread
  will bury within a month;
- someone is being onboarded, and this change is a good way in.

It does **not** pay on a two-file change to code the reviewer wrote. There, the
diff is the explanation, and a document restating it is noise with a quiz
attached.

**It is not the PR description.** Different audience, different length: the PR
body is for someone deciding whether to look, the page is for someone who has
decided and now has to understand. Step 11 still happens.

### Design skills and a decided direction

A style database is a menu of alternatives. If the project has already approved
a direction, most of that menu is wrong answers.

**The direction is the brief, not the rival.** Never ask a design skill "which
style" once that is settled — ask "given these constraints, how do I lay this
out with real hierarchy and accessible charts." That is the half such skills are
genuinely good at and that a short design doc never covers.

If the project has **no** direction yet, the selection half is exactly right and
should run first. It stops being right the moment a direction is approved.

---

## Lane 2 - Bug

1. **Reproduce before hypothesizing.** `superpowers:systematic-debugging`. For
   hard or performance bugs, `diagnose` adds minimise and instrument phases.
2. **Root cause, not symptom.** Find every caller and fix the shared function
   once. One guard in the shared place is a smaller diff than one per call site,
   and patching only the reported path leaves a sibling broken.
3. **Contract check.** If the fix touches a contract path, it becomes Lane 1
   from step 3.
4. **Failing regression test first** — the bug is the spec, so this is test-first
   on any surface.
5. Minimal fix.
6. Verify: full suite.
7. `/sync` **only if** a doc is now false. The integrity test answers this.
8. If it revealed a design flaw, file a backlog row **with a revisit condition**.
9. If the root cause was genuinely subtle — the kind the team will hit again —
   `explain-diff-html`. A bug whose explanation is "the ordering flipped in the
   retry path" is worth one page and no more; one that took a day to find is
   worth the page precisely because the next person should not spend the day.

---

## Lane 3 - Chore

Refactor, rename, dependency bump.

1. Climb the ladder — often stops at rung 1: does this need doing at all?
2. No spec. Plan only if it spans more than ~3 files.
3. **Existing tests must pass unchanged.** That is the definition: if a test had
   to change, behavior changed, and it is not a chore.
4. `/simplify` or a review-oriented skill fits here.
5. `/sync` if it renamed something the docs name.

---

## Lane 4 - Spike

"Will this even work."

1. `prototype` — throwaway.
2. No docs, no tests, not merged.
3. Outcome: deleted, or **promoted to Lane 1** with what was learned written into
   the spec. A spike that quietly becomes production code is the worst case.

---

## Cross-cutting

| Situation | Reach for |
|---|---|
| Unfamiliar area of the codebase | `zoom-out`, then the graph |
| Someone has to understand a change they did not write | `explain-diff-html` |
| Running out of context | `handoff` |
| Codebase question | the graph before grep |
| Claiming something works | `verification-before-completion` |

## Failure modes

- **Skipping step 1 because the task seems clear.** Brainstorming is where you
  find out it was already decided against.
- **Fixing before reproducing.** The most common and most expensive.
- **Letting a Lane 3 grow.** If tests had to change, stop and re-lane it.
- **Claiming green without running it.** Evidence before assertions.
- **Treating the gate as advice.** It is membership in a list.
- **Writing an explanation page instead of a review.** Step 10b comes after
  step 10, never instead of it. A page explaining a change nobody reviewed
  explains it very clearly and catches nothing.
