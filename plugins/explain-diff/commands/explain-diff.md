---
description: Explain a code change as a self-contained interactive HTML page
---

Invoke the `explain-diff-html` skill.

Resolve the target from the argument, or infer it and say what you chose:

- nothing → uncommitted work; if the tree is clean, this branch vs. its merge-base
- a branch name → that branch vs. `git merge-base` with the integration branch
- a PR number or URL → that PR's head vs. base
- a commit or range → exactly that

**Read the surrounding code before writing anything.** The background section
is what makes the page worth reading and it cannot be written from the diff —
read the touched files, their callers, their tests, and `git log -p` for why
the current design exists. Evidence before assertions: if you claim the old
code did something, you have read the old code.

Then follow the skill: four sections (background, intuition, code, quiz),
starting from `assets/template.html`.

Finish with both scripts, and **paste the checker's output**:

```
python assets/write_target.py --slug <short-slug>
python assets/check_output.py <path>
```

A page reported as done on the strength of intent is how the one-line code
block ships.

Target, if given: $ARGUMENTS
