"""Contract gate: contract paths need an approved spec on the branch.

The rule is Lane 1 step 4. It is a check rather than a sentence because the
sentence has a known failure mode -- a session in a hurry skims it.

Membership is read from the invariants doc's fenced block so there is exactly
one list, not one in prose and one in code that quietly disagree.

Every coding agent has a different hook mechanism, and some have none, so this
runs in three shapes against the same list:

  1. **Pre-edit hook, JSON on stdin** -- Claude Code `PreToolUse`, and any
     harness that emits a similar {tool, path} envelope. Several envelope
     shapes are understood; see `extract_targets`.
  2. **Explicit paths on argv** -- `python contract_gate.py <path>...`, for
     harnesses that hand a hook argv instead of stdin, and for manual checks.
  3. **Git pre-commit** -- `python contract_gate.py --staged`, the fallback for
     harnesses with no hook mechanism at all. Later than a pre-edit gate, but
     it is the one gate that works everywhere and cannot be talked out of.

Exit 2 means blocked, with the reason on stderr. 2 is deliberate: Claude Code
reads it as "block and show the model this text", and git reads any non-zero as
"reject the commit", so one code serves both.

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

# Where the contract list may live. First file that actually carries a
# '## Contract paths' section wins, so a project that keeps its invariants in
# AGENTS.md needs no edit here.
INVARIANTS_CANDIDATES = [
    "docs/architecture/invariants.md",
    "docs/invariants.md",
    "docs/architecture/INVARIANTS.md",
    "AGENTS.md",
    "CLAUDE.md",
]

# Where an approved spec may live. Any of these satisfies the gate.
SPEC_DIRS = [
    "docs/superpowers/specs/",
    "docs/specs/",
    "docs/design/",
]

EDIT_TOOLS = {
    # Claude Code
    "edit", "write", "notebookedit", "multiedit",
    # common elsewhere
    "apply_patch", "str_replace_editor", "str_replace_based_edit_tool",
    "create_file", "edit_file", "write_file", "patch", "editor",
}


def repo_root() -> Path:
    """Git decides, so the script works from any install location.

    The old `parents[2]` walk assumed the script sat at `.claude/hooks/`, which
    is true on exactly one host. Falling back to it keeps that case working
    when git is unavailable.
    """
    env = os.environ.get("GROUNDWORK_REPO") or os.environ.get("CLAUDE_PROJECT_DIR")
    if env and Path(env).is_dir():
        return Path(env).resolve()
    here = Path(__file__).resolve().parent
    for cwd in (Path.cwd(), here):
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


def invariants_file() -> Path | None:
    override = os.environ.get("GROUNDWORK_INVARIANTS")
    candidates = [override] if override else INVARIANTS_CANDIDATES
    for rel in candidates:
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
    """The fenced block under '## Contract paths', and the doc it came from."""
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
        line = line.strip()
        # Tolerate list markers and trailing prose in the fence.
        line = re.sub(r"^[-*]\s+", "", line)
        if not line or line.startswith("#"):
            continue
        paths.append(line.split()[0])
    return (paths, doc)


def spec_dirs() -> list[str]:
    override = os.environ.get("GROUNDWORK_SPEC_DIR")
    if override:
        return [override.rstrip("/") + "/"]
    return SPEC_DIRS


def rel(path: str) -> str:
    try:
        return Path(path).resolve().relative_to(REPO).as_posix()
    except (ValueError, OSError):
        return path.replace("\\", "/").lstrip("./")


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
    extra = os.environ.get("GROUNDWORK_BASE_BRANCHES", "")
    candidates = [b.strip() for b in extra.split(",") if b.strip()] or [
        "development", "origin/development", "main", "origin/main",
        "master", "origin/master",
    ]
    best: tuple[int, str] | None = None
    for base in candidates:
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
    dirs = spec_dirs()
    for blob in candidates:
        for line in blob.splitlines():
            line = line.strip()
            if any(line.startswith(d) for d in dirs):
                return line
    return None


def extract_targets(payload: object) -> list[str]:
    """Pull edited paths out of whatever envelope the harness handed us.

    Harnesses disagree about key names and nesting, and new ones appear faster
    than this file can be updated, so walk the structure for path-ish keys
    rather than matching one known shape.
    """
    found: list[str] = []
    path_keys = {"file_path", "filepath", "path", "file", "target_file", "notebook_path"}
    list_keys = {"paths", "files", "file_paths"}

    def walk(node: object, depth: int = 0) -> None:
        if depth > 6:
            return
        if isinstance(node, dict):
            for key, value in node.items():
                lower = key.lower()
                if lower in path_keys and isinstance(value, str) and value.strip():
                    found.append(value)
                elif lower in list_keys and isinstance(value, list):
                    found.extend(v for v in value if isinstance(v, str) and v.strip())
                else:
                    walk(value, depth + 1)
        elif isinstance(node, list):
            for item in node:
                walk(item, depth + 1)

    walk(payload)
    # Preserve order, drop repeats.
    seen: set[str] = set()
    return [p for p in found if not (p in seen or seen.add(p))]


def tool_name(payload: object) -> str | None:
    if not isinstance(payload, dict):
        return None
    for key in ("tool_name", "toolName", "tool", "name"):
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def staged_paths() -> list[str]:
    blob = git("diff", "--name-only", "--cached", "--diff-filter=ACMR")
    return [ln.strip() for ln in blob.splitlines() if ln.strip()]


def overridden() -> bool:
    if os.environ.get("GROUNDWORK_CONTRACT_OK") or os.environ.get("LP_CONTRACT_OK"):
        return True
    for marker in (".groundwork/.contract-override", ".claude/.contract-override"):
        if (REPO / marker).exists():
            return True
    return False


def report(hits: list[tuple[str, str]], doc: Path | None, mode: str) -> None:
    doc_rel = doc.relative_to(REPO).as_posix() if doc else "the invariants doc"
    listed = "\n".join(f"  {target}  matches `{pattern}`" for target, pattern in hits)
    where = {
        "staged": "These staged files are contract paths",
        "hook": "CONTRACT PATH",
        "argv": "CONTRACT PATH",
    }[mode]
    print(
        f"{where}:\n{listed}\n"
        f"\n"
        f"Listed under `## Contract paths` in {doc_rel}.\n"
        f"\n"
        f"Lane 1 step 4: this needs an approved design spec on the branch "
        f"before code. No file under {' or '.join(spec_dirs())} was found on "
        f"this branch.\n"
        f"\n"
        f"Write the spec first (cite provenance -- file and date -- for each "
        f"locked decision), get it approved, then build.\n"
        f"\n"
        f"If this really is exempt, set GROUNDWORK_CONTRACT_OK=1 for the "
        f"command, or create .groundwork/.contract-override -- and say in the "
        f"commit why.",
        file=sys.stderr,
    )


def check(targets: list[str], mode: str) -> int:
    if not targets:
        return 0

    paths, doc = contract_paths()
    if not paths:
        # No list means no gate. Say so on an explicit run so the silence is
        # not mistaken for protection; stay quiet in a hook, where it would be
        # noise on every edit.
        if mode != "hook":
            print(
                "groundwork: no `## Contract paths` block found in "
                f"{', '.join(INVARIANTS_CANDIDATES)} -- gate is a no-op.",
                file=sys.stderr,
            )
        return 0

    hits: list[tuple[str, str]] = []
    for target in targets:
        target_rel = rel(target)
        for pattern in paths:
            if target_rel.startswith(pattern.rstrip("/")):
                hits.append((target_rel, pattern))
                break
    if not hits:
        return 0

    if overridden():
        return 0
    if spec_on_branch():
        return 0

    report(hits, doc, mode)
    return 2


def main(argv: list[str]) -> int:
    args = list(argv)

    if "--help" in args or "-h" in args:
        print(__doc__)
        return 0

    if "--staged" in args:
        return check(staged_paths(), "staged")

    explicit = [a for a in args if not a.startswith("-")]
    if explicit:
        return check(explicit, "argv")

    if sys.stdin is None or sys.stdin.isatty():
        print(
            "usage: contract_gate.py <path>... | --staged | <hook JSON on stdin>",
            file=sys.stderr,
        )
        return 0

    try:
        payload = json.loads(sys.stdin.read() or "null")
    except (json.JSONDecodeError, ValueError):
        return 0  # never block on a malformed payload

    name = tool_name(payload)
    if name and name.lower() not in EDIT_TOOLS:
        return 0

    return check(extract_targets(payload), "hook")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
