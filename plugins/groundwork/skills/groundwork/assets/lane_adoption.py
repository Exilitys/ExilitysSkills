"""Did the lane discipline actually get followed, or is it decorative?

The skill asserts a workflow. Nothing measures whether sessions use it, so the
honest answer has always been "no idea" -- and a workflow nobody follows is
worse than none, because it makes the repo look governed.

`lanes.md` says "announce which lane you are in." That is checkable. This reads
a coding agent's session transcripts for a project and reports what fraction of
working sessions announced one.

    python lane_adoption.py [--project PATH] [--last N]
                            [--host claude|codex|opencode|auto]
                            [--transcripts DIR]

Transcript formats are per-host and undocumented, so honesty about the reading
matters more than coverage:

  * **claude** -- exact. The record shape is known, so an edit is an edit and a
    lane announcement is one the assistant actually made.
  * **anything else** -- heuristic, and labelled as such in the output. Any
    JSONL is scanned for edit-tool names and lane announcements without knowing
    which field is whose, so it can over-count. Use it for a trend, not a KPI.

`--transcripts DIR` points at any directory of `.jsonl` session logs, which is
the escape hatch for a host this file has never heard of.

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
# Lowercased, and wider: other hosts name their editors differently.
EDIT_TOOLS_ANY = {t.lower() for t in EDIT_TOOLS} | {
    "apply_patch", "str_replace_editor", "str_replace_based_edit_tool",
    "create_file", "edit_file", "write_file", "patch", "editor", "shell_edit",
}
LANE_NAMES = {"1": "Slice", "2": "Bug", "3": "Chore", "4": "Spike"}


def claude_dir(project: Path) -> Path:
    r"""Claude Code slugs the absolute path: every non-alphanumeric becomes '-'.

    One dash per character, not per run -- `D:\My Code\Widget` becomes
    `D--My-Code-Widget`, with the drive colon, the separator and the space each
    contributing their own dash.
    """
    slug = re.sub(r"[^A-Za-z0-9]", "-", str(project.resolve()))
    return Path.home() / ".claude" / "projects" / slug


def codex_dir() -> Path:
    """Codex keeps rollouts in date-nested dirs, not per-project ones.

    So the project filter has to come from inside each file rather than from
    the path -- see `mentions_project`.
    """
    return Path.home() / ".codex" / "sessions"


def opencode_dir() -> Path:
    base = Path.home() / ".local" / "share" / "opencode" / "storage"
    return base / "session"


def discover(project: Path, host: str) -> tuple[list[Path], str, Path | None]:
    """(session files, host actually used, directory searched)."""
    hosts = [host] if host != "auto" else ["claude", "codex", "opencode"]
    for name in hosts:
        directory = {
            "claude": claude_dir(project),
            "codex": codex_dir(),
            "opencode": opencode_dir(),
        }[name]
        if not directory.is_dir():
            continue
        files = sorted(directory.rglob("*.jsonl"), key=lambda p: p.stat().st_mtime)
        if name != "claude":
            files = [f for f in files if mentions_project(f, project)]
        if files:
            return (files, name, directory)
    searched = None
    if host != "auto":
        searched = {
            "claude": claude_dir(project),
            "codex": codex_dir(),
            "opencode": opencode_dir(),
        }[host]
    return ([], host, searched)


def mentions_project(path: Path, project: Path) -> bool:
    """Cheap cwd filter for hosts that do not shard transcripts per project.

    Reads the head of the file only: every format this matters for records the
    working directory in its first few records.
    """
    needle = str(project.resolve())
    alt = needle.replace("\\", "/")
    try:
        with path.open("r", encoding="utf-8", errors="replace") as fh:
            head = fh.read(65536)
    except OSError:
        return False
    return needle in head or alt in head


def scan_claude(path: Path) -> tuple[bool, str | None]:
    """Exact read of the Claude Code record shape."""
    edited = False
    lane: str | None = None

    for rec in records(path):
        if rec.get("type") != "assistant":
            continue
        for block in rec.get("message", {}).get("content", []) or []:
            if not isinstance(block, dict):
                continue
            kind = block.get("type")
            if kind == "tool_use" and block.get("name") in EDIT_TOOLS:
                edited = True
            elif kind == "text" and lane is None:
                lane = lane_in(block.get("text", ""))
    return (edited, lane)


def scan_generic(path: Path) -> tuple[bool, str | None]:
    """Format-blind read, for hosts whose record shape is not known here.

    Walks every record for a tool name that looks like an editor and every
    string for a lane announcement. It cannot tell an assistant's claim from a
    user's quotation of one, which is exactly why the output says heuristic.
    """
    edited = False
    lane: str | None = None

    for rec in records(path):
        stack: list[object] = [rec]
        while stack:
            node = stack.pop()
            if isinstance(node, dict):
                for key, value in node.items():
                    lower = key.lower()
                    if lower in ("name", "tool", "tool_name", "toolname") and isinstance(value, str):
                        if value.lower() in EDIT_TOOLS_ANY:
                            edited = True
                    elif isinstance(value, str):
                        if lane is None and len(value) < 20000:
                            lane = lane_in(value)
                    else:
                        stack.append(value)
            elif isinstance(node, list):
                stack.extend(node)
    return (edited, lane)


def lane_in(text: str) -> str | None:
    m = LANE_RE.search(text)
    if m:
        return m.group(1)
    if NAMED_RE.search(text) and "lane" in text.lower():
        return "?"
    return None


def records(path: Path):
    """Yield parsed records from a JSONL file, tolerating a JSON array too."""
    try:
        raw = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return
    stripped = raw.lstrip()
    if stripped.startswith("["):
        try:
            payload = json.loads(stripped)
        except json.JSONDecodeError:
            return
        if isinstance(payload, list):
            for item in payload:
                if isinstance(item, dict):
                    yield item
        return
    for line in raw.splitlines():
        if not line.strip():
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(rec, dict):
            yield rec


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--project", default=".", help="repo whose sessions to read")
    ap.add_argument("--last", type=int, default=20, help="how many sessions")
    ap.add_argument(
        "--host", default="auto", choices=["auto", "claude", "codex", "opencode"],
        help="which agent's transcripts to read (default: first one with sessions)",
    )
    ap.add_argument(
        "--transcripts", help="read this directory of .jsonl sessions instead",
    )
    args = ap.parse_args()

    project = Path(args.project)

    if args.transcripts:
        tdir = Path(args.transcripts)
        if not tdir.is_dir():
            print(f"No such directory: {tdir}")
            return 0
        files = sorted(tdir.rglob("*.jsonl"), key=lambda p: p.stat().st_mtime)
        host = args.host if args.host != "auto" else "custom"
    else:
        files, host, searched = discover(project, args.host)
        if not files:
            where = searched or "any known transcript directory"
            print(f"No transcripts found for {project.resolve()} in {where}.")
            print(
                "Either this project has no sessions yet, it was opened by another\n"
                "path, or this host stores transcripts somewhere unknown here --\n"
                "point --transcripts at the directory if you know where it is."
            )
            return 0

    files = files[-args.last :]
    exact = host == "claude"
    scan = scan_claude if exact else scan_generic

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
    reading = "exact" if exact else "heuristic - see the module docstring"
    print(f"Lane adoption over the last {len(files)} session(s)")
    print(f"  host: {host}  |  reading: {reading}\n")
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
            "Partial adoption. Usually the lane table is not in the host's\n"
            "always-loaded file (AGENTS.md / CLAUDE.md), or nothing prints it at\n"
            "session start. Check both before concluding the workflow is wrong."
        )
    return (
        "Decorative. Either the lanes do not fit how work actually arrives here,\n"
        "or nothing surfaces them at the moment a task starts. Prefer fixing the\n"
        "surfacing first -- rewriting lanes nobody has read yet learns nothing."
    )


if __name__ == "__main__":
    sys.exit(main())
