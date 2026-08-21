"""Print where the explanation file should be written.

Three rules, and each has a reason that is easy to forget at 2am:

  * **Outside the repository.** A generated artifact in the work tree gets
    committed by the next `git add -A`, and then it rots in version control
    where nobody reads it.
  * **Filename starts with `YYYY-MM-DD-`.** The files then sort by time in any
    listing, which is the only organisation a scratch directory ever gets.
  * **Not hardcoded `/tmp`.** It does not exist on Windows. This picks the
    platform's own scratch directory instead.

    python write_target.py --slug retry-backoff
    python write_target.py --slug retry-backoff --print-dir

`EXPLAIN_DIFF_OUT` overrides the directory when the user wants these kept
somewhere durable, which is a reasonable thing to want.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import tempfile
from datetime import date
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def output_dir() -> Path:
    override = os.environ.get("EXPLAIN_DIFF_OUT")
    if override:
        return Path(override).expanduser()
    # tempfile honours TMPDIR / TEMP / TMP and falls back per platform, so it
    # is right on Windows and on a Linux box with a non-standard TMPDIR alike.
    return Path(tempfile.gettempdir())


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return (slug or "change")[:60]


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--slug", default="change", help="short name for the change")
    ap.add_argument("--print-dir", action="store_true", help="print only the directory")
    ap.add_argument("--mkdir", action="store_true", help="create the directory if missing")
    args = ap.parse_args(argv)

    directory = output_dir()
    if args.mkdir:
        directory.mkdir(parents=True, exist_ok=True)

    if args.print_dir:
        print(directory)
        return 0

    name = f"{date.today():%Y-%m-%d}-explanation-{slugify(args.slug)}.html"
    print(directory / name)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
