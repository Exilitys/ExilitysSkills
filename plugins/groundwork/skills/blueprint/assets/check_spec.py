"""Verify a spec before anyone signs off on it.

`spec-format.md` is a page of rules. Most of them a careful reading could
enforce -- and a careful reading is exactly what stops happening at the end of
a long specification session, which is when the document gets saved and sent
for approval. So they are checked here instead.

    python check_spec.py <path> [--scaffold]

`--scaffold` relaxes the checks that only make sense on a finished document:
leftover <placeholders> and TBD markers. Use it when checking the template.

Exit 0 = pass (warnings allowed), 1 = at least one failure, 2 = cannot read the
file. Warnings are worth a look; failures are things a builder will hit.

The defect this exists for, above all others: a decision record with no
`Rejected.` line. It reads exactly like a decision, it is filed as a decision,
and it was a default nobody examined -- which the team discovers only when the
constraint it silently assumed turns out to be false.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

FAILURES: list[str] = []
WARNINGS: list[str] = []

# Each is a number, a test, or a decision that has not been made yet.
WEASEL = re.compile(
    r"\b(fast|scalable|robust|secure|intuitive|seamless|simple|flexible|"
    r"modern|best[- ]practice|real[- ]time|user[- ]friendly|performant)\b",
    re.I,
)
UNRESOLVED = re.compile(r"\b(TBD|TODO|FIXME|\?\?\?)\b")
# <like this>, including the two-line kind a template uses for guidance.
PLACEHOLDER = re.compile(r"<[^<>]{2,400}>", re.S)

# Sections the format requires. A project with no answer omits a section --
# but not one of these, because omitting one of these means the interrogation
# did not finish.
REQUIRED = {
    "problem": r"^##\s*\d*\.?\s*Problem",
    "users": r"^##\s*\d*\.?\s*Users",
    "core assumption": r"^##\s*\d*\.?\s*The core assumption",
    "scope": r"^##\s*\d*\.?\s*Scope",
    "decisions": r"^##\s*\d*\.?\s*Decisions",
    "first slice": r"^##\s*\d*\.?\s*The first slice",
}


def fail(msg: str) -> None:
    FAILURES.append(msg)


def warn(msg: str) -> None:
    WARNINGS.append(msg)


# --------------------------------------------------------------------------
# reading the document
# --------------------------------------------------------------------------

def strip_comments(text: str) -> str:
    return re.sub(r"<!--.*?-->", "", text, flags=re.S)


def strip_code(text: str) -> str:
    """Fenced blocks hold payloads and signatures, not prose.

    A `<type>` in a sample payload is the spec doing its job; the same string
    in a paragraph is a placeholder nobody replaced.
    """
    return re.sub(r"```.*?```", "", text, flags=re.S)


def numbered_lines(text: str) -> list[tuple[int, str]]:
    return list(enumerate(text.splitlines(), start=1))


def decision_blocks(text: str) -> list[tuple[str, str]]:
    """Every `### D-NNN` heading mapped to its body.

    Split on the heading rather than parsing the whole document: a spec that
    reorders or renames its other sections should still have its decisions
    checked.
    """
    out: list[tuple[str, str]] = []
    marks = list(re.finditer(r"^###\s*(D-\d+)\b([^\n]*)", text, re.M))
    for i, m in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(text)
        nxt = re.search(r"^##\s", text[m.end():end], re.M)
        stop = m.end() + nxt.start() if nxt else end
        out.append((m.group(1), text[m.end():stop]))
    return out


def section_body(text: str, pattern: str) -> str:
    """The body of the first `##` section whose heading matches."""
    m = re.search(pattern, text, re.M | re.I)
    if not m:
        return ""
    nxt = re.search(r"^##\s", text[m.end():], re.M)
    return text[m.end(): m.end() + nxt.start()] if nxt else text[m.end():]


def is_approved(text: str) -> bool:
    return bool(re.search(r"Approved\s+\d{4}-\d{2}-\d{2}", text))


# --------------------------------------------------------------------------
# the checks
# --------------------------------------------------------------------------

def check_structure(text: str) -> None:
    for name, pattern in REQUIRED.items():
        if not re.search(pattern, text, re.M | re.I):
            fail(f"no `{name}` section -- the format requires it")

    if not re.search(r"^#\s+\S", text, re.M):
        fail("no title")

    # Optional, but it is the section spec-format.md names as the one most
    # often missing -- and the one whoever writes the code invents at 2am.
    if not re.search(r"^##\s*\d*\.?\s*Failure behaviour", text, re.M | re.I):
        warn("no `failure behaviour` section -- what happens when a dependency "
             "fails is otherwise decided by whoever writes the code")


def check_decisions(text: str, approved: bool) -> None:
    blocks = decision_blocks(text)
    if not blocks:
        fail("no decision records (### D-001 ...) -- a spec with no decisions "
             "is a description; see spec-format.md")
        return

    seen: set[str] = set()
    for did, body in blocks:
        if did in seen:
            fail(f"duplicate decision id {did} -- each record needs its own, "
                 f"because the build cites them")
        seen.add(did)

        if not re.search(r"\*\*Chosen\.?\*\*", body, re.I):
            fail(f"{did}: no `Chosen.` -- the record does not say what was decided")

        if not re.search(r"\*\*Rejected\.?\*\*", body, re.I):
            fail(f"{did}: no `Rejected.` -- an alternative-free record is a "
                 f"default wearing a decision's clothes. Name the alternatives, "
                 f"or write `Rejected. Default, not evaluated.`")

        if not re.search(r"\*\*Because\.?\*\*", body, re.I):
            fail(f"{did}: no `Because.` -- a decision with no reason cannot be "
                 f"revisited, only re-argued")

        if not re.search(r"\*\*Revisit when\.?\*\*", body, re.I):
            warn(f"{did}: no `Revisit when.` -- nothing will ever reopen this")

        if not re.search(r"\*\*Provenance\.?\*\*", body, re.I):
            msg = (f"{did}: no `Provenance.` -- a locked decision cites who and "
                   f"when, or it is a guess wearing a spec's clothes")
            fail(msg) if approved else warn(msg)

    print(f"  ..  {len(blocks)} decision record(s)")


def check_deferred(text: str) -> None:
    """A deferral with no condition is a decision being avoided."""
    body = section_body(text, r"^##\s*\d*\.?\s*Deferred")
    if not body.strip():
        warn("no Deferred section -- a spec that deferred nothing either "
             "decided everything or hid the open questions")
        return

    for line in body.splitlines():
        if not line.strip().startswith(("-", "*")):
            continue
        if not re.search(r"revisit\s+when", line, re.I):
            fail(f"deferred item with no revisit condition: {line.strip()[:70]}")


def check_falsifiable(text: str, written: str, scaffold: bool) -> None:
    body = section_body(text, r"^##\s*\d*\.?\s*Non-functional")
    if body.strip() and not re.search(r"\d", body):
        warn("the non-functional targets section has no numbers in it -- "
             "a target without a number cannot be met or missed")

    for n, line in numbered_lines(written):
        for m in WEASEL.finditer(line):
            # A weasel word next to a number is usually naming the metric.
            if re.search(r"\d", line):
                continue
            warn(f"line {n}: `{m.group(0)}` is not a requirement -- it is a "
                 f"number, a test, or a decision not yet made")
            break

    if scaffold:
        return
    for n, line in numbered_lines(written):
        m = UNRESOLVED.search(line)
        if m:
            fail(f"line {n}: unresolved `{m.group(0)}` -- the spec is not ready "
                 f"for sign-off")


def check_placeholders(text: str, scaffold: bool) -> None:
    if scaffold:
        return
    left = [" ".join(m.group(0).split())[:40] for m in PLACEHOLDER.finditer(text)]
    if left:
        shown = ", ".join(left[:4]) + (" ..." if len(left) > 4 else "")
        fail(f"{len(left)} unreplaced placeholder(s) ({shown})")


def check_first_slice(text: str) -> None:
    body = section_body(text, r"^##\s*\d*\.?\s*The first slice")
    if not body.strip():
        return
    if not re.search(r"done when|proves", body, re.I):
        warn("the first slice has no `Done when.` -- a slice with no "
             "observable finish cannot come back negative, which is what it "
             "exists to do")


# --------------------------------------------------------------------------

def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("path", help="the spec markdown file")
    ap.add_argument("--scaffold", action="store_true",
                    help="checking the template: allow placeholders and TBDs")
    args = ap.parse_args(argv)

    path = Path(args.path).expanduser()
    if not path.is_file():
        print(f"cannot read {path}", file=sys.stderr)
        return 2
    try:
        raw = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        print(f"cannot read {path}: {exc}", file=sys.stderr)
        return 2

    text = strip_comments(raw)
    prose = strip_code(text)
    # A weasel word inside a <placeholder> is guidance; the placeholder itself
    # is already a failure, so scanning its prose twice only adds noise.
    prose_written = PLACEHOLDER.sub("", prose)
    approved = is_approved(text)

    print(f"{path}  ({len(raw) / 1024:.0f} KB, "
          f"{'approved' if approved else 'draft'})")

    check_structure(text)
    check_decisions(text, approved)
    check_deferred(text)
    check_falsifiable(prose, prose_written, args.scaffold)
    check_placeholders(prose, args.scaffold)
    check_first_slice(text)

    for msg in WARNINGS:
        print(f"  WARN  {msg}")
    for msg in FAILURES:
        print(f"  FAIL  {msg}")

    if FAILURES:
        print(f"\n{len(FAILURES)} failure(s). The spec is not ready for sign-off.")
        return 1
    print(f"\nPassed{f' with {len(WARNINGS)} warning(s)' if WARNINGS else ''}.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
