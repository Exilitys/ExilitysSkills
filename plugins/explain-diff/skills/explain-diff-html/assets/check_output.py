"""Verify a produced explanation page before anyone claims it works.

`html-contract.md` is a page of rules. Most of them a careful reading could
enforce, and a careful reading is exactly what stops happening at the end of a
long task -- which is when this file gets written. So they are checked here
instead.

    python check_output.py <path> [--scaffold]

`--scaffold` relaxes the two checks that only make sense on a finished page:
leftover REPLACE markers, and the five-question count. Use it when checking the
template itself.

Exit 0 = pass (warnings allowed), 1 = at least one failure, 2 = cannot read the
file. Warnings are things worth a look; failures are things a reader will hit.

The defect this exists for, above all others: a code block in a styled div
collapses every newline into one line. The page looks correct while it is being
written and arrives unreadable.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

FAILURES: list[str] = []
WARNINGS: list[str] = []

# Classes that name a code block. A div with one of these needs the
# white-space rule; a <pre> already has it from the browser default.
CODEISH = re.compile(r"\b(code|snippet|listing|highlight|codeblock|source)\b", re.I)
EXTERNAL = re.compile(r"""(?:src|href)\s*=\s*["']\s*(https?:)?//""", re.I)


def fail(msg: str) -> None:
    FAILURES.append(msg)


def warn(msg: str) -> None:
    WARNINGS.append(msg)


# --------------------------------------------------------------------------
# location and naming
# --------------------------------------------------------------------------

def check_location(path: Path) -> None:
    if path.suffix.lower() != ".html":
        fail(f"not an .html file: {path.name}")

    stem = path.name
    if not re.match(r"^\d{4}-\d{2}-\d{2}-", stem):
        fail(f"filename must start with YYYY-MM-DD-, got {stem!r}")
    else:
        try:
            datetime.strptime(stem[:10], "%Y-%m-%d")
        except ValueError:
            fail(f"filename date prefix is not a real date: {stem[:10]}")

    try:
        inside = subprocess.run(
            ["git", "-C", str(path.parent), "rev-parse", "--is-inside-work-tree"],
            capture_output=True, text=True, timeout=10,
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return
    if inside == "true":
        fail(
            f"{path} is inside a git work tree. Generated pages belong outside "
            f"the repo -- run write_target.py to get a path."
        )


# --------------------------------------------------------------------------
# the whitespace rule
# --------------------------------------------------------------------------

def css_rules_with_whitespace(text: str) -> set[str]:
    """Selectors whose block sets white-space to a newline-preserving value."""
    keeps: set[str] = set()
    for selectors, body in re.findall(r"([^{}]+)\{([^{}]*)\}", text, re.S):
        m = re.search(r"white-space\s*:\s*([a-z-]+)", body, re.I)
        if not m or m.group(1).lower() not in ("pre", "pre-wrap", "pre-line", "break-spaces"):
            continue
        for sel in selectors.split(","):
            keeps.add(sel.strip())
    return keeps


def check_whitespace(text: str) -> None:
    style = "\n".join(re.findall(r"<style[^>]*>(.*?)</style>", text, re.S | re.I))
    # Strip comments first, or a comment sitting above a rule is read as part
    # of its selector and lands in the failure message.
    style = re.sub(r"/\*.*?\*/", "", style, flags=re.S)
    keeps = css_rules_with_whitespace(style)

    # A <pre> that the page has explicitly un-preserved is the nastiest case,
    # because the markup looks right.
    for selectors, body in re.findall(r"([^{}]+)\{([^{}]*)\}", style, re.S):
        if not re.search(r"(^|[\s,>+~])pre\b", selectors):
            continue
        m = re.search(r"white-space\s*:\s*([a-z-]+)", body, re.I)
        if m and m.group(1).lower() in ("normal", "nowrap"):
            fail(
                f"CSS sets `white-space: {m.group(1)}` on a <pre> selector "
                f"({selectors.strip()}) -- newlines will collapse"
            )

    # Every element that looks like a code block but is not a <pre>.
    for tag in re.finditer(r"<(?!pre\b)(\w+)([^>]*\bclass\s*=\s*[\"']([^\"']+)[\"'][^>]*)>", text):
        name, attrs, classes = tag.group(1), tag.group(2), tag.group(3)
        if not CODEISH.search(classes):
            continue
        inline = re.search(r"style\s*=\s*[\"'][^\"']*white-space\s*:\s*([a-z-]+)", attrs, re.I)
        if inline and inline.group(1).lower().startswith("pre"):
            continue
        if any(
            f".{cls}" in keeps or cls in keeps or f"{name}.{cls}" in keeps
            for cls in classes.split()
        ):
            continue
        fail(
            f"<{name} class=\"{classes}\"> looks like a code block but no CSS "
            f"gives it `white-space: pre`/`pre-wrap` -- its newlines will "
            f"collapse into one line. Use <pre>."
        )

    if "<pre" not in text.lower():
        warn("no <pre> blocks at all -- a code walkthrough with no code excerpts?")


# --------------------------------------------------------------------------
# self-containment
# --------------------------------------------------------------------------

def check_self_contained(text: str) -> None:
    for m in EXTERNAL.finditer(text):
        snippet = text[m.start(): m.start() + 90].replace("\n", " ")
        fail(f"external resource -- the page must work offline: ...{snippet}...")

    if re.search(r"@import\s+(url\()?[\"']?(https?:)?//", text, re.I):
        fail("CSS @import of a remote stylesheet -- inline it instead")

    for pattern, what in (
        (r"\bfetch\s*\(", "fetch()"),
        (r"\bXMLHttpRequest\b", "XMLHttpRequest"),
        (r"\bnew\s+WebSocket\b", "WebSocket"),
        (r"\bimport\s*\(\s*[\"']https?:", "dynamic import from a URL"),
    ):
        if re.search(pattern, text):
            fail(f"{what} in the page -- it will fail when opened from disk")


# --------------------------------------------------------------------------
# structure and quiz wiring
# --------------------------------------------------------------------------

def top_level(body: str) -> dict[str, str]:
    """Keys of a JS object literal, mapped to their raw values.

    Regex cannot do this: `feedback: {` is nested one level down and a
    line-anchored pattern reads it as a sibling of `q1`. Track depth instead.
    """
    out: dict[str, str] = {}
    depth = 0
    key: str | None = None
    start = 0
    i = 0
    quote: str | None = None
    while i < len(body):
        ch = body[i]
        if quote:
            if ch == "\\":
                i += 2
                continue
            if ch == quote:
                quote = None
        elif ch in "\"'":
            quote = ch
        elif ch in "{[":
            depth += 1
        elif ch in "}]":
            depth -= 1
        elif depth == 0:
            if ch == ":" and key is None:
                back = body[:i].rstrip()
                m = re.search(r"([A-Za-z_$][\w$]*|\"[^\"]+\"|'[^']+')$", back)
                if m:
                    key = m.group(1).strip("\"'")
                    start = i + 1
            elif ch == "," and key is not None:
                out[key] = body[start:i].strip()
                key = None
        i += 1
    if key is not None:
        out[key] = body[start:].strip()
    return out


def check_structure(text: str, scaffold: bool) -> None:
    if not re.search(r'<meta[^>]+name=["\']viewport["\']', text, re.I):
        fail("no viewport meta tag -- the page will not be readable on a phone")

    title = re.search(r"<title[^>]*>(.*?)</title>", text, re.S | re.I)
    if not title or not title.group(1).strip():
        fail("no <title>")
    elif "REPLACE" in title.group(1) and not scaffold:
        fail("the <title> still contains a REPLACE placeholder")

    for anchor in ("background", "intuition", "code", "quiz"):
        if not re.search(rf'id=["\']{anchor}', text, re.I):
            fail(f"no section with id=\"{anchor}\" -- all four sections are required")

    if not re.search(r'href=["\']#', text):
        fail("no table of contents links -- the page needs a TOC at the top")

    if re.search(r"<(button|a)[^>]*\bdata-tab\b", text, re.I) or 'class="tabs"' in text:
        warn("looks like tabs at the top level -- hidden content is content the "
             "reader will not find; use one long page")

    if not scaffold and "REPLACE" in text:
        n = text.count("REPLACE")
        fail(f"{n} REPLACE placeholder(s) left in the page")


def check_quiz(text: str, scaffold: bool) -> None:
    blocks = re.findall(r'data-q\s*=\s*["\']([^"\']+)["\']', text)
    if not blocks:
        fail("no quiz blocks found (expected elements with data-q)")
        return

    if len(blocks) != len(set(blocks)):
        fail("duplicate data-q ids -- each question needs its own")

    if not scaffold and len(blocks) != 5:
        fail(f"the quiz has {len(blocks)} question(s); the format calls for 5")

    key_src = re.search(r"ANSWERS\s*=\s*\{(.*?)\n\s*\};", text, re.S)
    if not key_src:
        fail("no ANSWERS object found -- the quiz will not respond to clicks")
        return
    entries = top_level(key_src.group(1))
    keyed = set(entries)

    for qid in blocks:
        if qid not in keyed:
            fail(f"question {qid} has no entry in ANSWERS -- clicking it does nothing")
    for qid in keyed - set(blocks):
        warn(f"ANSWERS has an entry for {qid} with no matching question block")

    # Every option needs feedback: a wrong answer is the most valuable moment
    # in the page, and "Incorrect." wastes it.
    for block in re.finditer(
        r'data-q\s*=\s*["\']([^"\']+)["\'](.*?)(?=data-q\s*=|</main>)', text, re.S
    ):
        qid, body = block.group(1), block.group(2)
        opts = set(re.findall(r'data-opt\s*=\s*["\']([^"\']+)["\']', body))
        if not opts:
            fail(f"question {qid} has no options")
            continue
        raw = entries.get(qid)
        if raw is None:
            continue
        fields = top_level(raw.strip().lstrip("{").rstrip("}"))
        correct = (fields.get("correct") or "").strip().strip("\"'")
        if not correct:
            fail(f"question {qid} has no `correct` option in ANSWERS")
        elif correct not in opts:
            fail(f"question {qid}: correct answer {correct!r} is not one of its options")
        fb_raw = fields.get("feedback", "")
        fb = set(top_level(fb_raw.strip().lstrip("{").rstrip("}")))
        missing = opts - fb
        if missing:
            fail(f"question {qid}: no feedback for option(s) {', '.join(sorted(missing))}")

    if re.search(r"\balert\s*\(", text):
        fail("alert() in the quiz -- feedback belongs inline, below the options")


def check_accessibility(text: str) -> None:
    if not re.search(r"prefers-color-scheme", text):
        warn("no dark-mode block -- a long read at night will be a white page")

    for svg in re.finditer(r"<svg([^>]*)>", text, re.I):
        if "viewbox" not in svg.group(1).lower():
            warn("an inline <svg> has no viewBox -- it will overflow on a phone")
            break

    if re.search(r"<(table|pre)\b", text, re.I) and "overflow-x" not in text:
        warn("wide elements present but no overflow-x anywhere -- the page may "
             "scroll sideways on a phone")


# --------------------------------------------------------------------------

def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("path", help="the produced .html file")
    ap.add_argument("--scaffold", action="store_true",
                    help="checking the template: allow placeholders and <5 questions")
    args = ap.parse_args(argv)

    path = Path(args.path).expanduser()
    if not path.is_file():
        print(f"cannot read {path}", file=sys.stderr)
        return 2
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        print(f"cannot read {path}: {exc}", file=sys.stderr)
        return 2

    check_location(path)
    check_whitespace(text)
    check_self_contained(text)
    check_structure(text, args.scaffold)
    check_quiz(text, args.scaffold)
    check_accessibility(text)

    size = path.stat().st_size
    print(f"{path}  ({size / 1024:.0f} KB)")

    for msg in WARNINGS:
        print(f"  WARN  {msg}")
    for msg in FAILURES:
        print(f"  FAIL  {msg}")

    if FAILURES:
        print(f"\n{len(FAILURES)} failure(s). The page is not ready.")
        return 1
    print(f"\nPassed{f' with {len(WARNINGS)} warning(s)' if WARNINGS else ''}.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
