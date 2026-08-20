# Drift audit - is any of this still true?

Bootstrap finds gaps on a cold repo. Nothing finds rot on a warm one, and rot
is the failure this skill exists to prevent: a stale doc does not go quiet, it
starts lying, and it lies with the authority of something that was once
checked.

Run this periodically - after a merge-heavy week, before onboarding someone,
whenever a session says "the docs told me X and X was wrong."

It is a **report, never a gate.** The heuristic is coarse on purpose; a gate on
it would be disabled within a week and take the honest signal with it.

## Step 1 - Mechanical pass

```bash
python assets/drift_report.py --root . --days 7
```

For every living context file, it compares the doc's last commit against the
last commit of each path the doc points at. Newer code means the claim has not
been reviewed since the thing it describes moved.

Two exclusions matter, and both were learned by running it:

- **Point-in-time records are excluded** - plans, specs, reports, ADRs. They
  are snapshots, stale by design. Including them produced 247 rows on a real
  repo and buried the ~20 that mattered.
- **Bare top-level directories are excluded** as targets. `backend` commits
  daily; a row saying so never tells you which claim to re-read.

A row is a question, not a verdict.

## Step 2 - The three questions a mechanical pass cannot ask

Run the integrity test first (`assets/tests/`) - it answers "does this name
exist" so you do not spend judgment on it. What is left needs reading:

1. **Is a documented rule now enforced by a tool?** Then the prose is a second
   home for a rule that has config. Cut it to naming the command. This is the
   skill's one idea, applied in reverse.
2. **Did a decision get made in a session and never written down?** Look for
   choices in the diff that no spec explains. An undocumented decision gets
   re-litigated at full cost every few weeks.
3. **Did a deferral's revisit condition fire?** Every backlog item carrying a
   condition is a scheduled question. Check the conditions, not the dates.

## Step 3 - Report, then fix only what is false

Present: **file | claim | status (true / stale / now-enforced) | action.**

Fix the false ones. Leave the merely-old ones alone - a doc that has not
changed in six months because the thing it describes has not changed is not
drift, it is stability, and rewriting it to look fresh destroys the signal that
it was accurate.

Confirming a claim is still true is a real outcome. Touch the file so the next
audit starts from the confirmation.

## Step 3b - Measure whether the workflow is followed at all

```bash
python assets/lane_adoption.py --project . --last 20
```

`lanes.md` says "announce which lane you are in", which makes adoption
measurable. The script reads the project's session transcripts and reports what
fraction of **code-editing** sessions announced one; sessions that only answered
questions are excluded, because they have no lane.

A low number is evidence about the workflow, not about the sessions. Measured
on the repo this skill was built in: **13%**, with a `SessionStart` hook
printing the lane table every single session. Being visible is not the same as
being used - which is the finding, and it points at the lanes needing to fit how
work actually arrives, not at more prose.

Fix surfacing before rewriting lanes. Rewriting something nobody has read yet
learns nothing.

## Step 4 - Feed what you learned back

Drift is evidence about the context system, not just about one file.

- The same file stale three audits running? Its subject moves faster than prose
  can track. Replace it with a check, or delete it and let the code speak.
- A rule broken repeatedly despite being written down? It is a hook, not a
  sentence. `contract-gate.md`.
- A concern with two homes again? Bootstrap step 2 got the ruling wrong. Re-rule
  it once, in `CLAUDE.md`.
