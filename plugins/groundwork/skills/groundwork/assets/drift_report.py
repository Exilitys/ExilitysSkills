"""Drift audit: which context files fell behind the code they describe.

Bootstrap detects gaps on a cold repo. Nothing detects rot on a warm one --
and rot is the failure this whole skill exists to prevent, because a doc that
went stale does not go quiet, it starts lying.

The heuristic is deliberately dumb and therefore trustworthy: a context file
that points at `backend/domain/ports/` is making a claim about that directory.
If the directory has commits newer than the file's last commit, the claim is
unreviewed. That is not proof of staleness -- it is a list worth reading, which
is all a periodic audit needs to be.

    python drift_report.py [--days N] [--root PATH]

Exit 0 always. This reports; it does not gate. A gate on a heuristic this
coarse would be disabled within a week.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Living documents only. A doc that makes a standing claim about the code can
# drift; a point-in-time record cannot, because it was never claiming to still
# be true. Auditing plans and reports buries the real signal under snapshots
# that are stale by design -- measured on a real repo: 247 rows, of which the
# handful that mattered were invisible.
CONTEXT_GLOBS = [
    "CLAUDE.md", "AGENTS.md", "CONTEXT.md", "README.md",
    "*/AGENTS.md", "*/CLAUDE.md",
    "docs/architecture/*.md",
]
SKIP_DOC_PARTS = {"plans", "specs", "reports", "superpowers", "security", "adr"}

PATH_RE = re.compile(r"`([a-zA-Z0-9_.-]+/[A-Za-z0-9_./-]*)`")
SKIP = {"node_modules", ".venv", "__pycache__", ".git", "dist", ".next"}


def git(root: Path, *args: str) -> str:
    try:
        return subprocess.run(
            ["git", *args], cwd=root, capture_output=True, text=True, timeout=15
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def last_commit(root: Path, path: str) -> tuple[int, str]:
    """(unix timestamp, short sha) of the newest commit touching path."""
    out = git(root, "log", "-1", "--format=%ct %h", "--", path)
    if not out:
        return (0, "")
    ts, _, sha = out.partition(" ")
    try:
        return (int(ts), sha)
    except ValueError:
        return (0, "")


def context_files(root: Path) -> list[Path]:
    seen: list[Path] = []
    for pattern in CONTEXT_GLOBS:
        for p in root.glob(pattern):
            if not p.is_file():
                continue
            parts = set(p.parts)
            if parts & SKIP or parts & SKIP_DOC_PARTS:
                continue
            if p not in seen:
                seen.append(p)
    return seen


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".", help="repo root")
    ap.add_argument(
        "--days",
        type=int,
        default=0,
        help="only report drift where the gap exceeds N days",
    )
    args = ap.parse_args()

    root = Path(args.root).resolve()
    if not (root / ".git").exists():
        print(f"not a git repo: {root}")
        return 0

    rows: list[tuple[int, str, str, str]] = []
    unreadable: list[str] = []

    for doc in context_files(root):
        rel = doc.relative_to(root).as_posix()
        doc_ts, _ = last_commit(root, rel)
        if not doc_ts:
            continue  # never committed -- nothing to compare against

        try:
            text = doc.read_text(encoding="utf-8", errors="replace")
        except OSError:
            unreadable.append(rel)
            continue

        # A bare top-level directory (`backend`, `frontend`) is always newer
        # than any doc -- something in it commits daily. The row is noise: it
        # never tells you which claim to re-read. Require depth.
        targets = {
            t
            for t in (m.rstrip("/") for m in PATH_RE.findall(text))
            if t.count("/") >= 1 and t != rel and (root / t).exists()
        }

        for target in sorted(targets):
            code_ts, sha = last_commit(root, target)
            if code_ts <= doc_ts:
                continue
            gap_days = (code_ts - doc_ts) // 86400
            if gap_days < args.days:
                continue
            rows.append((gap_days, rel, target, sha))

    if not rows:
        print("No drift found: every referenced path is older than the doc citing it.")
        return 0

    rows.sort(reverse=True)
    width = max(len(r[1]) for r in rows)

    print(f"{len(rows)} claim(s) unreviewed since the code moved, oldest first.\n")
    print(f"{'days':>5}  {'context file'.ljust(width)}  code that moved after it")
    print(f"{'-' * 5}  {'-' * width}  {'-' * 30}")
    for gap, doc, target, sha in rows:
        print(f"{gap:>5}  {doc.ljust(width)}  {target} ({sha})")

    if unreadable:
        print(f"\nCould not read: {', '.join(unreadable)}")

    print(
        "\nA row is a question, not a verdict: does that file still describe "
        "that code?\nConfirm it and touch the doc; correct it and commit the fix."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
