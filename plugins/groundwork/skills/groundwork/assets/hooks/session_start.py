"""SessionStart: orient the session in facts, not in prose it might skim.

Prints branch, uncommitted state, the contract list, any plan with unchecked
boxes, and graph freshness. All of it is computed, so none of it can go out of
date the way a written status line does -- which is precisely why a
hand-maintained progress tracker is not worth adopting.

Everything is derived from the repo, so this runs unmodified in most projects.
The three constants below are the only tuning points.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

# Windows consoles default to cp1252; hook stdout must never die on a glyph.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO = Path(__file__).resolve().parents[2]

# Tuning points.
INVARIANTS = REPO / "docs" / "architecture" / "invariants.md"
PLAN_DIRS = ["docs/superpowers/plans", "docs/plans", "docs/specs"]
GRAPH = REPO / "graphify-out" / "graph.json"


def git(*args: str) -> str:
    try:
        return subprocess.run(
            ["git", *args], cwd=REPO, capture_output=True, text=True, timeout=10
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def contract_paths() -> list[str]:
    """The fenced block under '## Contract paths' in the invariants doc.

    Same source the gate hook reads, so the reminder and the enforcement can
    never disagree -- one list, not one in prose and one in code.
    """
    if not INVARIANTS.exists():
        return []
    try:
        text = INVARIANTS.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    section = text.split("## Contract paths", 1)
    if len(section) < 2:
        return []
    fence = re.search(r"```\n(.*?)```", section[1], re.S)
    if not fence:
        return []
    return [ln.strip() for ln in fence.group(1).splitlines() if ln.strip()]


def open_plans() -> list[tuple[str, int]]:
    for rel in PLAN_DIRS:
        plans = REPO / rel
        if not plans.is_dir():
            continue
        out = []
        for f in sorted(plans.glob("*.md")):
            try:
                text = f.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            # Checkbox counts alone lie: shipped plans keep their unchecked
            # boxes and record completion in a status header instead. The
            # header is the truth, so it wins.
            head = "\n".join(text.splitlines()[:40]).lower()
            if "status: complete" in head or "status:** complete" in head:
                continue
            todo = text.count("- [ ]")
            if todo:
                out.append((f.name, todo))
        if out:
            return out[-3:]
    return []


def graph_state() -> str | None:
    """None when the project does not use a code graph -- stay silent then."""
    if not GRAPH.parent.is_dir():
        return None
    if not GRAPH.exists():
        return "absent - run `graphify .` to build (AST pass is free)"
    last_commit = git("log", "-1", "--format=%ct")
    try:
        if last_commit and GRAPH.stat().st_mtime < int(last_commit):
            return "STALE (older than HEAD) - run `graphify update .` first"
    except (ValueError, OSError):
        pass
    return "current"


def main() -> int:
    branch = git("rev-parse", "--abbrev-ref", "HEAD") or "?"
    dirty = [ln for ln in git("status", "--short").splitlines() if ln.strip()]

    status = f"**Branch:** `{branch}` | **Uncommitted:** {len(dirty)} file(s)"
    graph = graph_state()
    if graph:
        status += f" | **Graph:** {graph}"

    lines = [
        f"## {REPO.name} session context",
        "",
        status,
        "",
        "**Lanes:** 1 Slice (spec, plan, build) | 2 Bug (reproduce first) | "
        "3 Chore (tests pass unchanged) | 4 Spike (throwaway). "
        "**Announce which lane you are in.**",
    ]

    contracts = contract_paths()
    if contracts:
        joined = ", ".join(f"`{p}`" for p in contracts)
        rel = INVARIANTS.relative_to(REPO).as_posix()
        lines += [
            "",
            f"**Contract paths need a spec before code:** {joined} — plus any "
            f"backlog item with a revisit condition. Full list: `{rel}`.",
        ]

    plans = open_plans()
    if plans:
        lines += ["", "**Plans with unchecked tasks:**"]
        lines += [f"- `{name}`: {n} open" for name, n in plans]

    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
