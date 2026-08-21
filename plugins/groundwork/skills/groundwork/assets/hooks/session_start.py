"""Session orientation: facts, not prose the session might skim.

Prints branch, uncommitted state, the contract list, any plan with unchecked
boxes, and graph freshness. All of it is computed, so none of it can go out of
date the way a written status line does -- which is precisely why a
hand-maintained progress tracker is not worth adopting.

Everything is derived from the repo, so this runs unmodified in most projects.
The constants below are the only tuning points.

Hosts differ in how they run it, and it needs nothing from any of them:

  * Claude Code -- a `SessionStart` hook; stdout is injected as context.
  * OpenCode    -- a plugin on the session-start event, same idea.
  * Anything else, including harnesses with no event model at all --
    `python session_start.py` and paste, or wire it into the shell prompt or a
    `make context` target. It reads stdin from nobody and writes markdown to
    stdout, so every host is just a different way of calling it.

    python session_start.py [--root PATH]
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

# Windows consoles default to cp1252; hook stdout must never die on a glyph.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Tuning points.
INVARIANTS_CANDIDATES = [
    "docs/architecture/invariants.md",
    "docs/invariants.md",
    "AGENTS.md",
    "CLAUDE.md",
]
PLAN_DIRS = ["docs/superpowers/plans", "docs/plans", "docs/specs"]
GRAPH_REL = "graphify-out/graph.json"


def repo_root(explicit: str | None = None) -> Path:
    """Git decides, so this runs from any install location on any host.

    The old `parents[2]` walk assumed the script sat at `.claude/hooks/`, true
    on exactly one host. It stays as the last fallback.
    """
    if explicit and Path(explicit).is_dir():
        return Path(explicit).resolve()
    env = os.environ.get("GROUNDWORK_REPO") or os.environ.get("CLAUDE_PROJECT_DIR")
    if env and Path(env).is_dir():
        return Path(env).resolve()
    for cwd in (Path.cwd(), Path(__file__).resolve().parent):
        try:
            out = subprocess.run(
                ["git", "-C", str(cwd), "rev-parse", "--show-toplevel"],
                capture_output=True, text=True, timeout=10,
            ).stdout.strip()
        except (OSError, subprocess.SubprocessError):
            continue
        if out:
            return Path(out).resolve()
    return Path(__file__).resolve().parents[2]


REPO = repo_root()
GRAPH = REPO / GRAPH_REL


def git(*args: str) -> str:
    try:
        return subprocess.run(
            ["git", *args], cwd=REPO, capture_output=True, text=True, timeout=10
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def invariants_file() -> Path | None:
    """First candidate that actually carries the section, not the first that exists."""
    override = os.environ.get("GROUNDWORK_INVARIANTS")
    for rel in ([override] if override else INVARIANTS_CANDIDATES):
        path = REPO / rel
        if not path.is_file():
            continue
        try:
            if "## Contract paths" in path.read_text(encoding="utf-8", errors="replace"):
                return path
        except OSError:
            continue
    return None


def contract_paths() -> tuple[list[str], Path | None]:
    """The fenced block under '## Contract paths' in the invariants doc.

    Same source and same parse the gate reads, so the reminder and the
    enforcement can never disagree -- one list, not one in prose and one in
    code.
    """
    doc = invariants_file()
    if doc is None:
        return ([], None)
    try:
        text = doc.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ([], doc)
    section = text.split("## Contract paths", 1)
    if len(section) < 2:
        return ([], doc)
    fence = re.search(r"```[^\n]*\n(.*?)```", section[1], re.S)
    if not fence:
        return ([], doc)
    paths = []
    for line in fence.group(1).splitlines():
        line = re.sub(r"^[-*]\s+", "", line.strip())
        if not line or line.startswith("#"):
            continue
        paths.append(line.split()[0])
    return (paths, doc)


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
    global REPO, GRAPH
    ap = argparse.ArgumentParser(description="Print session orientation as markdown.")
    ap.add_argument("--root", help="repo to describe (default: git toplevel)")
    args, _ = ap.parse_known_args()
    if args.root:
        REPO = repo_root(args.root)
        GRAPH = REPO / GRAPH_REL

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

    contracts, doc = contract_paths()
    if contracts and doc is not None:
        joined = ", ".join(f"`{p}`" for p in contracts)
        rel = doc.relative_to(REPO).as_posix()
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
