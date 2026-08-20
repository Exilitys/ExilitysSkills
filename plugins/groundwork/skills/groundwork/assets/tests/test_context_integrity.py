"""The context files must describe things that exist.

A pointer to something real saves a session; a pointer to something renamed or
never built costs one. This is not hypothetical -- the case that produced this
template: a root CLAUDE.md listed a port class that had never existed anywhere
in the backend, while omitting one that had shipped four days earlier. A
900-test suite could not see it, because no test reads prose.

Adjust CONFIG below and delete rules that do not apply. Every rule should
encode a drift that actually happened here; a rule guarding a hypothetical is a
rule someone will disable the first time it is inconvenient.

Identifier lookups go through a token set rather than per-name regexes: one
pass over the source instead of one per name, and no escaping to get wrong.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# CONFIG -- the only part that is project-specific.
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[2]

SOURCE_DIRS = ["backend", "frontend/src"]
SOURCE_EXTS = {".py", ".ts", ".tsx"}
SKIP_DIRS = {"node_modules", "__pycache__", ".venv", "dist", ".next", ".git"}

# Missing files are skipped, not failed.
CONTEXT_FILES = ["CLAUDE.md", "AGENTS.md", "CONTEXT.md"]

# Backticked references starting with one of these are checked for existence.
PATH_PREFIXES = ["backend", "frontend", "docs", "src", "app"]

# A word in a context file ending in one of these must exist in the source.
IDENTIFIER_SUFFIXES = [
    "Policy", "Strategy", "Repo", "Repository", "Service", "Client",
    "Renderer", "Extractor", "Generator", "Verifier", "Pipeline", "Adapter",
    "Provider", "Handler", "Store", "Context",
]

NOT_TERMS_HEADING = "## Not domain terms"
# ---------------------------------------------------------------------------


def _source_text() -> str:
    chunks = []
    for rel in SOURCE_DIRS:
        base = ROOT / rel
        if not base.is_dir():
            continue
        for path in base.rglob("*"):
            if any(part in SKIP_DIRS for part in path.parts):
                continue
            if path.suffix in SOURCE_EXTS and path.is_file():
                chunks.append(path.read_text(encoding="utf-8", errors="replace"))
    return "\n".join(chunks)


SOURCE = _source_text()
TOKENS = set(re.findall(r"[A-Za-z_][A-Za-z0-9_]*", SOURCE))
CLASSES = set(re.findall(r"class\s+([A-Za-z_][A-Za-z0-9_]*)", SOURCE))
PRESENT = [f for f in CONTEXT_FILES if (ROOT / f).exists()]

PATH_RE = re.compile(r"`((?:%s)/[A-Za-z0-9_./-]+)`" % "|".join(PATH_PREFIXES))
IDENT_RE = re.compile(r"\b([A-Z][A-Za-z0-9]*(?:%s))\b" % "|".join(IDENTIFIER_SUFFIXES))


def test_finds_source_to_check_against():
    """Guards the config itself.

    A wrong SOURCE_DIRS makes every rule below pass vacuously, which is the
    worst outcome -- a green suite guarding nothing.
    """
    assert len(TOKENS) > 100, f"scanned {SOURCE_DIRS} and found almost nothing"
    assert PRESENT, f"none of {CONTEXT_FILES} exist at {ROOT}"


def _claims(name: str) -> str:
    """The part of a context file that asserts things exist.

    Everything under NOT_TERMS_HEADING asserts the opposite -- it names what is
    deliberately absent. Scanning it for identifiers flags every entry as
    missing, which is the section working as designed.
    """
    text = (ROOT / name).read_text(encoding="utf-8", errors="replace")
    return text.split(NOT_TERMS_HEADING, 1)[0]


@pytest.mark.parametrize("name", PRESENT)
def test_points_only_at_paths_that_exist(name):
    text = _claims(name)
    refs = {m.rstrip("/") for m in PATH_RE.findall(text)}
    missing = sorted(r for r in refs if not (ROOT / r).exists())
    assert not missing, f"{name} points at paths that do not exist: {missing}"


@pytest.mark.parametrize("name", PRESENT)
def test_names_only_identifiers_that_exist(name):
    text = _claims(name)
    named = set(IDENT_RE.findall(text))
    missing = sorted(n for n in named if n not in TOKENS)
    assert not missing, f"{name} names identifiers that do not exist: {missing}"


def test_not_a_term_list_stays_honest():
    """A glossary listing names that are NOT domain terms claims the other way.

    If one becomes real, the entry should be promoted -- leaving it reads as a
    warning against something that now ships.
    """
    for name in PRESENT:
        text = (ROOT / name).read_text(encoding="utf-8", errors="replace")
        if NOT_TERMS_HEADING not in text:
            continue
        tail = text.split(NOT_TERMS_HEADING, 1)[1]
        revived = sorted(
            n for n in re.findall(r"\*\*`?([A-Z][A-Za-z0-9]+)`?\*\*", tail)
            if n in CLASSES
        )
        assert not revived, f"{name} calls these non-terms, but they are classes: {revived}"
