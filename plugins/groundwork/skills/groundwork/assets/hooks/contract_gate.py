"""PreToolUse gate: contract files need an approved spec on the branch.

The rule is Lane 1 step 4 in CLAUDE.md. It is a hook rather than a sentence
because the sentence has a known failure mode -- a session in a hurry skims it.
`docs/architecture/design-system.md` has the receipts.

Membership is read from invariants.md's fenced block so there is exactly one
list, not one in prose and one in code that quietly disagree.

Escape hatch is deliberate and printed in the rejection: a gate with no
override becomes a gate people disable entirely.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

REPO = Path(__file__).resolve().parents[2]
INVARIANTS = REPO / "docs" / "architecture" / "invariants.md"
SPEC_DIR = "docs/superpowers/specs/"


def contract_paths() -> list[str]:
    """The fenced block under '## Contract paths' in invariants.md."""
    if not INVARIANTS.exists():
        return []
    text = INVARIANTS.read_text(encoding="utf-8")
    section = text.split("## Contract paths", 1)
    if len(section) < 2:
        return []
    fence = re.search(r"```\n(.*?)```", section[1], re.S)
    if not fence:
        return []
    return [ln.strip() for ln in fence.group(1).splitlines() if ln.strip()]


def rel(path: str) -> str:
    try:
        return Path(path).resolve().relative_to(REPO).as_posix()
    except (ValueError, OSError):
        return path.replace("\\", "/")


def git(*args: str) -> str:
    try:
        return subprocess.run(
            ["git", *args], cwd=REPO, capture_output=True, text=True, timeout=10
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def nearest_base() -> str | None:
    """The closest integration branch this one descends from.

    Picking the first that merely *exists* is wrong: a branch cut from
    `development` has an ancient merge-base with `main`, so diffing against it
    sweeps in every spec merged in between and the gate silently passes. Choose
    the candidate whose merge-base is most recent instead.
    """
    best: tuple[int, str] | None = None
    for base in ("development", "origin/development", "main", "origin/main"):
        if not git("rev-parse", "--verify", "--quiet", base):
            continue
        merge_base = git("merge-base", base, "HEAD")
        if not merge_base:
            continue
        when = git("show", "-s", "--format=%ct", merge_base)
        try:
            stamp = int(when)
        except ValueError:
            continue
        if best is None or stamp > best[0]:
            best = (stamp, merge_base)
    return best[1] if best else None


def spec_on_branch() -> str | None:
    """A spec added or touched on this branch, or sitting uncommitted."""
    candidates = []
    base = nearest_base()
    if base:
        candidates.append(git("diff", "--name-only", f"{base}...HEAD"))
    candidates.append(git("diff", "--name-only"))
    candidates.append(git("diff", "--name-only", "--cached"))
    candidates.append(git("ls-files", "--others", "--exclude-standard"))
    for blob in candidates:
        for line in blob.splitlines():
            if line.strip().startswith(SPEC_DIR):
                return line.strip()
    return None


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0  # never block on a malformed payload

    if payload.get("tool_name") not in ("Edit", "Write", "NotebookEdit"):
        return 0

    target = payload.get("tool_input", {}).get("file_path")
    if not target:
        return 0

    target_rel = rel(target)
    hits = [p for p in contract_paths() if target_rel.startswith(p.rstrip("/"))]
    if not hits:
        return 0

    if os.environ.get("LP_CONTRACT_OK"):
        return 0
    if (REPO / ".claude" / ".contract-override").exists():
        return 0

    spec = spec_on_branch()
    if spec:
        return 0

    print(
        f"CONTRACT PATH: {target_rel} matches `{hits[0]}` in "
        f"docs/architecture/invariants.md.\n"
        f"\n"
        f"Lane 1 step 4: this needs an approved design spec on the branch "
        f"before code. No file under {SPEC_DIR} was found on this branch.\n"
        f"\n"
        f"Write the spec first (cite provenance -- file and date -- for each "
        f"locked decision), get it approved, then build.\n"
        f"\n"
        f"If this really is exempt, set LP_CONTRACT_OK=1 for the command, or "
        f"touch .claude/.contract-override -- and say in the commit why.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
