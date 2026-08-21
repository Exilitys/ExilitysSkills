#!/usr/bin/env python3
"""Install this repo's skills into any coding agent that reads SKILL.md.

The skills were already portable -- a `SKILL.md` with YAML frontmatter, plus
references and scripts in the same folder, which is the Agent Skills format
every major agent now loads. What was not portable was *delivery*: they shipped
as Claude Code plugins, so only Claude Code could find them.

This script is the delivery layer. It puts each skill folder where each host
looks, writes the host's own flavour of that plugin's commands, and drops an
`AGENTS.md` pointer for harnesses that have no skill loader at all.

    python install.py                      # detect hosts, install every skill here
    python install.py --list               # skills, hosts, and where things go
    python install.py --skill groundwork   # just one
    python install.py --host codex opencode
    python install.py --scope user         # into the home-directory config
    python install.py --dry-run            # print the plan, touch nothing
    python install.py --link               # symlink hosts at the shared copy
    python install.py --git-gate           # + a pre-commit contract gate
    python install.py --uninstall          # remove what a previous run wrote

Nothing is written without being recorded in `.groundwork/install.json`, so
`--uninstall` removes exactly what was added and never guesses.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import sys
from dataclasses import dataclass, field
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = Path(__file__).resolve().parent
PLUGINS = HERE / "plugins"
MANIFEST = ".groundwork/install.json"
# The gate ships with groundwork; --git-gate looks for it by this path.
GATE_REL = "assets/hooks/contract_gate.py"

BEGIN = "<!-- groundwork:begin -->"
END = "<!-- groundwork:end -->"


@dataclass(frozen=True)
class Skill:
    name: str            # the skill's own directory name, which is its id
    plugin: str          # the plugin that ships it
    path: Path           # the skill folder itself
    commands: Path       # that plugin's commands dir; may not exist
    description: str     # the frontmatter description, for the AGENTS.md pointer


def frontmatter_description(skill_md: Path) -> str:
    """The `description:` line, folded to one line.

    It is what tells a host *when* to load the skill, so it is also what an
    AGENTS.md pointer has to carry on a host with no skill loader -- there,
    nothing else advertises the trigger.
    """
    try:
        text = skill_md.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""
    if not text.startswith("---"):
        return ""
    parts = text.split("---", 2)
    if len(parts) < 3:
        return ""
    out: list[str] = []
    capturing = False
    for line in parts[1].splitlines():
        if line.startswith("description:"):
            capturing = True
            out.append(line.partition(":")[2].strip())
        elif capturing:
            # YAML folds a continuation line only when it is indented.
            if line[:1].isspace() and line.strip():
                out.append(line.strip())
            else:
                break
    return " ".join(out)


def discover_skills() -> list[Skill]:
    """Every skill this repo ships, found rather than listed.

    A hardcoded list is one more place to forget when a plugin is added, and
    the failure is silent -- the skill simply never installs anywhere.
    """
    found: list[Skill] = []
    for skill_md in sorted(PLUGINS.glob("*/skills/*/SKILL.md")):
        folder = skill_md.parent
        found.append(Skill(
            name=folder.name,
            plugin=folder.parent.parent.name,
            path=folder,
            commands=folder.parent.parent / "commands",
            description=frontmatter_description(skill_md),
        ))
    return found


@dataclass(frozen=True)
class Host:
    key: str
    label: str
    # Where the skill folder goes, relative to the repo / to home.
    project_skills: str
    user_skills: str
    # Where command files go, and in which dialect. Empty means the host has
    # no command mechanism and reaches the skill by description alone.
    project_commands: str = ""
    user_commands: str = ""
    dialect: str = "none"
    # Args placeholder in this host's command files.
    args_token: str = "$ARGUMENTS"
    # Paths whose presence means the user actually uses this host.
    markers: tuple[str, ...] = ()
    note: str = ""


# Ordered most-specific first; `.agents/` is last because it is the fallback
# every host can read rather than any one host's home.
HOSTS: tuple[Host, ...] = (
    Host(
        key="claude",
        label="Claude Code",
        project_skills=".claude/skills",
        user_skills=".claude/skills",
        project_commands=".claude/commands",
        user_commands=".claude/commands",
        dialect="md_frontmatter",
        markers=(".claude", "CLAUDE.md"),
        note="Also installable as a plugin: /plugin marketplace add Exilitys/ExilitysSkills",
    ),
    Host(
        key="codex",
        label="OpenAI Codex CLI",
        project_skills=".codex/skills",
        user_skills=".codex/skills",
        user_commands=".codex/prompts",
        dialect="md_plain",
        markers=(".codex", "AGENTS.md"),
        note="Prompts are global only; project scope installs the skill alone.",
    ),
    Host(
        key="opencode",
        label="OpenCode",
        project_skills=".opencode/skills",
        user_skills=".config/opencode/skills",
        project_commands=".opencode/command",
        user_commands=".config/opencode/command",
        dialect="md_frontmatter",
        markers=(".opencode", "opencode.json", "opencode.jsonc"),
        note="Also reads .claude/skills and .agents/skills, so one copy may already do.",
    ),
    Host(
        key="cursor",
        label="Cursor",
        project_skills=".cursor/skills",
        user_skills=".cursor/skills",
        project_commands=".cursor/commands",
        user_commands=".cursor/commands",
        dialect="md_plain",
        markers=(".cursor",),
    ),
    Host(
        key="gemini",
        label="Gemini CLI",
        project_skills=".gemini/skills",
        user_skills=".gemini/skills",
        project_commands=".gemini/commands",
        user_commands=".gemini/commands",
        dialect="toml",
        args_token="{{args}}",
        markers=(".gemini", "GEMINI.md"),
    ),
    Host(
        key="agents",
        label="Vendor-neutral (.agents)",
        project_skills=".agents/skills",
        user_skills=".agents/skills",
        dialect="none",
        markers=(".agents",),
        note="The cross-client convention. Read by OpenCode and others; the "
             "AGENTS.md pointer aims here, so harnesses with no skill loader "
             "still find the file.",
    ),
)

BY_KEY = {h.key: h for h in HOSTS}


# --------------------------------------------------------------------------
# command translation
# --------------------------------------------------------------------------

def split_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---"):
        return ({}, text)
    parts = text.split("---", 2)
    if len(parts) < 3:
        return ({}, text)
    meta: dict[str, str] = {}
    for line in parts[1].splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            meta[key.strip()] = value.strip()
    return (meta, parts[2].lstrip("\n"))


def render_command(source: Path, host: Host, skill_path: str) -> tuple[str, str]:
    """(filename, contents) for this host's flavour of one command file."""
    meta, body = split_frontmatter(source.read_text(encoding="utf-8"))
    description = meta.get("description", f"groundwork: {source.stem}")
    name = source.stem

    # Hosts other than Claude Code have no plugin-relative skill root, so the
    # command has to say where the skill actually landed. Without this the
    # command names references/ files the agent cannot find.
    body = f"Read `{skill_path}/SKILL.md` first, then follow it.\n\n{body}"
    body = body.replace("$ARGUMENTS", host.args_token)
    body = body.replace("references/", f"{skill_path}/references/")
    body = body.replace("assets/", f"{skill_path}/assets/")

    if host.dialect == "md_frontmatter":
        return (f"{name}.md", f"---\ndescription: {description}\n---\n\n{body}")
    if host.dialect == "md_plain":
        return (f"{name}.md", f"# {description}\n\n{body}")
    if host.dialect == "toml":
        escaped = body.replace('\\', '\\\\').replace('"""', '\\"\\"\\"')
        return (
            f"{name}.toml",
            f'description = {json.dumps(description)}\nprompt = """\n{escaped}\n"""\n',
        )
    raise ValueError(host.dialect)


# --------------------------------------------------------------------------
# AGENTS.md pointer
# --------------------------------------------------------------------------

def pointer_block(entries: list[tuple[str, str, str]]) -> str:
    """entries: (skill name, path relative to the repo, description).

    This block is the whole story on a harness with no skill loader: it names
    the file, and it carries the description, which is the part that says
    *when* to read it. A pointer without the trigger gets read once, on the
    session where someone happened to open AGENTS.md.
    """
    lines = [BEGIN, "## Agent skills in this repository", ""]
    lines.append(
        "These are [Agent Skills](https://github.com/agentskills/agentskills): a "
        "`SKILL.md` plus its references and scripts. **Read the relevant one "
        "before starting work it covers**, not only when asked for it by name. "
        "Each `SKILL.md` says which of its `references/` to load for a given "
        "case, so read it first and follow its routing rather than loading "
        "everything."
    )
    lines.append("")
    for name, rel, description in entries:
        lines.append(f"### `{name}`")
        lines.append("")
        lines.append(f"`{rel}/SKILL.md`")
        lines.append("")
        if description:
            lines.append(description)
            lines.append("")

    gate = next((rel for name, rel, _ in entries if name == "groundwork"), None)
    if gate:
        lines.append(
            "Before editing any file, check it against `## Contract paths` in "
            "the invariants doc that `groundwork/SKILL.md` names. A contract "
            "path needs an approved spec on the branch first. "
            f"`{gate}/{GATE_REL} <path>` answers that question mechanically; "
            "exit 2 means stop."
        )
        lines.append("")
    lines.append(END)
    return "\n".join(lines)


def upsert_pointer(agents_md: Path, entries: list[tuple[str, str, str]], dry: bool) -> str:
    block = pointer_block(entries)
    if agents_md.exists():
        text = agents_md.read_text(encoding="utf-8")
        if BEGIN in text and END in text:
            new = re.sub(
                re.escape(BEGIN) + r".*?" + re.escape(END), block, text, flags=re.S
            )
            action = "unchanged" if new == text else "updated"
        else:
            new = text.rstrip("\n") + "\n\n" + block + "\n"
            action = "appended to"
    else:
        new = f"# AGENTS.md\n\nInstructions for coding agents working in this repository.\n\n{block}\n"
        action = "created"
    if not dry and action != "unchanged":
        agents_md.parent.mkdir(parents=True, exist_ok=True)
        agents_md.write_text(new, encoding="utf-8")
    return action


# --------------------------------------------------------------------------
# copying
# --------------------------------------------------------------------------

def copy_skill(source: Path, dest: Path, link_to: Path | None, dry: bool) -> str:
    if dry:
        return "would link" if link_to else "would copy"
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.is_symlink() or dest.exists():
        remove(dest)
    if link_to is not None:
        try:
            dest.symlink_to(os.path.relpath(link_to, dest.parent), target_is_directory=True)
            return "linked"
        except (OSError, NotImplementedError):
            # Windows without developer mode. A copy is worse but it works,
            # and a hard failure here would strand the whole install.
            pass
    shutil.copytree(source, dest)
    return "copied"


def prune_empty(path: Path, stop: Path) -> None:
    """Walk up removing directories this install created and emptied.

    Stops at the repo root, and stops the moment a directory still holds
    something -- an uninstall that deleted a user's own `.claude/` would be a
    far worse bug than a leftover empty folder.
    """
    try:
        stop = stop.resolve()
        current = path.resolve()
    except OSError:
        return
    while current != stop and stop in current.parents:
        try:
            if any(current.iterdir()):
                return
            current.rmdir()
        except OSError:
            return
        current = current.parent


def remove(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)


def fingerprint(source: Path) -> str:
    """Hash of a source skill, so a stale install is detectable."""
    digest = hashlib.sha256()
    for f in sorted(source.rglob("*")):
        if f.is_file():
            digest.update(f.relative_to(source).as_posix().encode())
            digest.update(f.read_bytes())
    return digest.hexdigest()[:16]


# --------------------------------------------------------------------------
# git gate
# --------------------------------------------------------------------------

PRECOMMIT = """#!/bin/sh
# groundwork contract gate -- installed by install.py --git-gate
# Blocks a commit that stages a contract path with no spec on the branch.
# Bypass deliberately with `git commit --no-verify` or GROUNDWORK_CONTRACT_OK=1.
exec {python} "{gate}" --staged
"""


def install_git_gate(root: Path, gate: Path, dry: bool) -> tuple[str, Path | None]:
    hooks = root / ".git" / "hooks"
    if not hooks.parent.is_dir():
        return ("skipped - not a git repository", None)
    target = hooks / "pre-commit"
    if target.exists():
        body = target.read_text(encoding="utf-8", errors="replace")
        if "groundwork contract gate" not in body:
            return (f"skipped - {target} exists and is not ours", None)
    if dry:
        return ("would install", target)
    hooks.mkdir(parents=True, exist_ok=True)
    rel = os.path.relpath(gate, root)
    target.write_text(
        PRECOMMIT.format(python=sys.executable or "python3", gate=rel), encoding="utf-8"
    )
    target.chmod(target.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return ("installed", target)


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------

def detect(root: Path, home: Path) -> list[str]:
    found = []
    for host in HOSTS:
        if host.key == "agents":
            continue
        if any((root / m).exists() or (home / m).exists() for m in host.markers):
            found.append(host.key)
    return found


def base_for(scope: str, root: Path, home: Path) -> Path:
    return root if scope == "project" else home


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__.splitlines()[0],
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="\n".join(
            f"  {h.key:<9} {h.label:<22} {h.project_skills}/<skill>" for h in HOSTS
        ),
    )
    ap.add_argument("--skill", nargs="+", metavar="NAME",
                    help="skills to install (default: all of them)")
    ap.add_argument("--host", nargs="+", metavar="KEY",
                    help="hosts to install for (default: detected + agents). "
                         f"One or more of: {', '.join(BY_KEY)}, all")
    ap.add_argument("--scope", choices=["project", "user"], default="project",
                    help="install into this repo (default) or the home config")
    ap.add_argument("--root", default=".", help="repo to install into")
    ap.add_argument("--link", action="store_true",
                    help="symlink each host at one shared copy instead of copying")
    ap.add_argument("--no-agents-md", action="store_true",
                    help="skip the AGENTS.md pointer block")
    ap.add_argument("--git-gate", action="store_true",
                    help="also install a pre-commit contract gate")
    ap.add_argument("--list", action="store_true", help="show hosts and paths, install nothing")
    ap.add_argument("--dry-run", action="store_true", help="print the plan, write nothing")
    ap.add_argument("--uninstall", action="store_true", help="remove a previous install")
    args = ap.parse_args(argv)

    root = Path(args.root).resolve()
    home = Path.home()

    available = discover_skills()
    if not available:
        print(f"No skills found under {PLUGINS}/*/skills/*/SKILL.md", file=sys.stderr)
        return 1
    by_name = {s.name: s for s in available}

    if args.skill:
        unknown = [n for n in args.skill if n not in by_name]
        if unknown:
            print(f"Unknown skill(s): {', '.join(unknown)}. "
                  f"Known: {', '.join(by_name)}", file=sys.stderr)
            return 1
        skills = [by_name[n] for n in dict.fromkeys(args.skill)]
    else:
        skills = available

    detected = detect(root, home)

    if args.list:
        print(f"source: {PLUGINS}\n")
        print(f"{'skill':<20} {'plugin':<16} {'commands':<10} fingerprint")
        for skill in available:
            n = len(list(skill.commands.glob("*.md"))) if skill.commands.is_dir() else 0
            print(f"{skill.name:<20} {skill.plugin:<16} {n:<10} {fingerprint(skill.path)}")
        print()
        print(f"{'host':<9} {'detected':<9} {'project':<28} {'user'}")
        for host in HOSTS:
            mark = "yes" if host.key in detected else "-"
            print(f"{host.key:<9} {mark:<9} {host.project_skills+'/<skill>':<28} "
                  f"~/{host.user_skills}/<skill>")
        print()
        for host in HOSTS:
            if host.note:
                print(f"  {host.key}: {host.note}")
        return 0

    manifest_path = root / MANIFEST

    if args.uninstall:
        if not manifest_path.is_file():
            print(f"No install manifest at {manifest_path}; nothing to remove.")
            return 0
        record = json.loads(manifest_path.read_text(encoding="utf-8"))
        for entry in record.get("paths", []):
            path = Path(entry)
            if path.exists() or path.is_symlink():
                if not args.dry_run:
                    remove(path)
                print(f"  removed  {entry}")
            if not args.dry_run:
                prune_empty(path.parent, root)
        agents_md = root / "AGENTS.md"
        if agents_md.is_file():
            text = agents_md.read_text(encoding="utf-8")
            if BEGIN in text:
                cleaned = re.sub(
                    r"\n*" + re.escape(BEGIN) + r".*?" + re.escape(END) + r"\n*",
                    "\n", text, flags=re.S,
                )
                if not args.dry_run:
                    agents_md.write_text(cleaned, encoding="utf-8")
                print("  removed  AGENTS.md pointer block")
        if not args.dry_run:
            manifest_path.unlink()
            prune_empty(manifest_path.parent, root)
        print("Uninstalled.")
        return 0

    if args.host and "all" in args.host:
        keys = [h.key for h in HOSTS]
    elif args.host:
        unknown = [k for k in args.host if k not in BY_KEY]
        if unknown:
            print(f"Unknown host(s): {', '.join(unknown)}. "
                  f"Known: {', '.join(BY_KEY)}", file=sys.stderr)
            return 1
        keys = list(dict.fromkeys(args.host))
    else:
        # `agents` always, because it is what a harness with no skill loader
        # reads, and that is the whole point of installing outside Claude Code.
        keys = detected + ["agents"]
        if not detected:
            print("No agent config detected; installing the vendor-neutral copy only.")
            print("Name hosts explicitly with --host, or see --list.\n")

    base = base_for(args.scope, root, home)
    written: list[str] = []
    installed: dict[str, dict[str, Path]] = {}   # skill -> host -> dest
    dry = args.dry_run

    print(f"source : {PLUGINS}")
    print(f"target : {base}  [{args.scope} scope]")
    print(f"skills : {', '.join(s.name for s in skills)}")
    print(f"hosts  : {', '.join(keys)}\n")

    for skill in skills:
        shared: Path | None = None
        installed[skill.name] = {}
        for key in keys:
            host = BY_KEY[key]
            skills_rel = host.project_skills if args.scope == "project" else host.user_skills
            dest = base / skills_rel / skill.name

            link_to = shared if (args.link and shared is not None and shared != dest) else None
            action = copy_skill(skill.path, dest, link_to, dry)
            if not args.link or shared is None:
                shared = dest
            written.append(str(dest))
            installed[skill.name][key] = dest
            print(f"  {action:<12} {skill.name:<18} {host.label:<24} {dest}")

            cmd_rel = host.project_commands if args.scope == "project" else host.user_commands
            if not cmd_rel or host.dialect == "none" or not skill.commands.is_dir():
                continue
            cmd_dir = base / cmd_rel
            skill_path = os.path.relpath(dest, root if args.scope == "project" else home)
            skill_path = skill_path.replace(os.sep, "/")
            if args.scope == "user":
                skill_path = "~/" + skill_path
            for src in sorted(skill.commands.glob("*.md")):
                name, body = render_command(src, host, skill_path)
                out = cmd_dir / name
                if not dry:
                    cmd_dir.mkdir(parents=True, exist_ok=True)
                    out.write_text(body, encoding="utf-8")
                written.append(str(out))
                print(f"  {'command':<12} {skill.name:<18} {host.label:<24} {out}")

    def preferred(skill_name: str) -> Path | None:
        """Where a repo-level reference should point for this skill.

        The vendor-neutral copy when there is one: an AGENTS.md line and a git
        hook belong to the repository, not to whichever agent happened to be
        installed first and might be uninstalled next.
        """
        places = installed.get(skill_name)
        if not places:
            return None
        return places.get("agents") or next(iter(places.values()))

    if not args.no_agents_md and args.scope == "project":
        entries = []
        for skill in skills:
            target = preferred(skill.name)
            if target is None:
                continue
            entries.append((
                skill.name,
                os.path.relpath(target, root).replace(os.sep, "/"),
                skill.description,
            ))
        if entries:
            action = upsert_pointer(root / "AGENTS.md", entries, dry)
            listed = ", ".join(name for name, _, _ in entries)
            print(f"\n  AGENTS.md pointer {action} -> {listed}")

    if args.git_gate:
        source = preferred("groundwork")
        if source is None:
            print("  pre-commit gate skipped - the gate ships with the "
                  "groundwork skill, which was not installed")
        else:
            gate = source / GATE_REL
            action, target = install_git_gate(root, gate, dry)
            if target is not None and action == "installed":
                written.append(str(target))
            print(f"  pre-commit gate {action}" + (f" -> {target}" if target else ""))

    if not dry:
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(
            json.dumps(
                {"source": str(PLUGINS), "scope": args.scope, "hosts": keys,
                 "skills": {s.name: fingerprint(s.path) for s in skills},
                 "paths": written},
                indent=2,
            ) + "\n",
            encoding="utf-8",
        )
        print(f"\nRecorded in {manifest_path} -- `--uninstall` reverses exactly this.")
    else:
        print("\nDry run; nothing written.")

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
