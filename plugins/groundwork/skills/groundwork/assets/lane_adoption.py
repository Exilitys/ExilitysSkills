"""Did the lane discipline actually get followed, or is it decorative?

The skill asserts a workflow. Nothing measures whether sessions use it, so the
honest answer has always been "no idea" -- and a workflow nobody follows is
worse than none, because it makes the repo look governed.

`lanes.md` says "announce which lane you are in." That is checkable. This reads
the Claude Code transcripts for a project and reports what fraction of working
sessions announced one.

    python lane_adoption.py [--project PATH] [--last N]

Sessions with no code edits are excluded: a question-answering session has no
lane and counting it as a miss makes the number meaningless.

Exit 0 always. This measures; it does not judge. Treat a low number as evidence
about the workflow's fit, not about the sessions.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

LANE_RE = re.compile(r"\bLane\s*([1-4])\b", re.I)
NAMED_RE = re.compile(r"\b(slice|bug|chore|spike)\b", re.I)
EDIT_TOOLS = {"Edit", "Write", "NotebookEdit", "MultiEdit"}
LANE_NAMES = {"1": "Slice", "2": "Bug", "3": "Chore", "4": "Spike"}


def transcript_dir(project: Path) -> Path:
    r"""Claude Code slugs the absolute path: every non-alphanumeric becomes '-'.

    One dash per character, not per run -- `D:\My Code\Widget` becomes
    `D--My-Code-Widget`, with the drive colon, the separator and the space each
    contributing their own dash.
    """
    slug = re.sub(r"[^A-Za-z0-9]", "-", str(project.resolve()))
    return Path.home() / ".claude" / "projects" / slug


def scan(path: Path) -> tuple[bool, str | None]:
    """(did this session edit code, which lane it announced)."""
    edited = False
    lane: str | None = None

    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return (False, None)

    for line in lines:
        if not line.strip():
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        if rec.get("type") != "assistant":
            continue

        for block in rec.get("message", {}).get("content", []) or []:
            if not isinstance(block, dict):
                continue
            kind = block.get("type")
            if kind == "tool_use" and block.get("name") in EDIT_TOOLS:
                edited = True
            elif kind == "text" and lane is None:
                text = block.get("text", "")
                m = LANE_RE.search(text)
                if m:
                    lane = m.group(1)
                elif NAMED_RE.search(text) and "lane" in text.lower():
                    lane = "?"
    return (edited, lane)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", default=".", help="repo whose sessions to read")
    ap.add_argument("--last", type=int, default=20, help="how many sessions")
    args = ap.parse_args()

    tdir = transcript_dir(Path(args.project))
    if not tdir.is_dir():
        print(f"No transcripts found at {tdir}")
        print("Either the project has no sessions yet, or it was opened by another path.")
        return 0

    files = sorted(tdir.glob("*.jsonl"), key=lambda p: p.stat().st_mtime)[-args.last :]
    if not files:
        print(f"No sessions in {tdir}")
        return 0

    working, announced = 0, 0
    lanes: Counter[str] = Counter()
    misses: list[str] = []

    for f in files:
        edited, lane = scan(f)
        if not edited:
            continue
        working += 1
        if lane:
            announced += 1
            lanes[lane] += 1
        else:
            misses.append(f.stem[:8])

    if not working:
        print(f"Read {len(files)} session(s); none edited code. Nothing to measure.")
        return 0

    pct = round(100 * announced / working)
    print(f"Lane adoption over the last {len(files)} session(s)\n")
    print(f"  sessions that edited code : {working}")
    print(f"  announced a lane          : {announced}  ({pct}%)")

    if lanes:
        print("\n  breakdown:")
        for key, n in sorted(lanes.items()):
            print(f"    Lane {key} {LANE_NAMES.get(key, 'unspecified'):<12} {n}")

    if misses:
        shown = ", ".join(misses[:8])
        more = f" (+{len(misses) - 8} more)" if len(misses) > 8 else ""
        print(f"\n  no lane announced: {shown}{more}")

    print("\n" + verdict(pct))
    return 0


def verdict(pct: int) -> str:
    if pct >= 70:
        return "The discipline is real. Keep the lane table where sessions see it."
    if pct >= 30:
        return (
            "Partial adoption. Usually the lane table is not in an always-loaded\n"
            "file, or the SessionStart hook is not printing it. Check both before\n"
            "concluding the workflow is wrong."
        )
    return (
        "Decorative. Either the lanes do not fit how work actually arrives here,\n"
        "or nothing surfaces them at the moment a task starts. Prefer fixing the\n"
        "surfacing first -- rewriting lanes nobody has read yet learns nothing."
    )


if __name__ == "__main__":
    sys.exit(main())
