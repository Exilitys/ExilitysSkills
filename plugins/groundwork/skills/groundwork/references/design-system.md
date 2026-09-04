# Design system — concerns 5-7, sourced live instead of written down

Applies only to a repo with a component-based UI. If there is no frontend, or
concerns 5-7 already resolve to something real, skip this file — bootstrap's
gap table already lets a row resolve to `skip`.

## Why the old default was wrong

Bootstrap's nine concerns include three UI ones:

| # | Concern | Old "generate if missing" |
|---|---|---|
| 5 | Visual tokens | `ui-tokens.md` |
| 6 | Design direction and rules | `ui-rules.md` |
| 7 | Component gallery | `ui-registry.md` |

Concern 7 already has a named anti-pattern in `bootstrap.md`: **"A hand-
maintained component registry when the component directory exists. The code
cannot go stale; the registry can."** Writing `ui-registry.md` as a catalog of
components is exactly that anti-pattern with extra steps — a list of names and
descriptions that is accurate on the day it is written and wrong the first time
someone adds, renames, or deletes a component without also editing the doc.

The fix is the same one this whole skill applies everywhere else: **a rule a
tool can check should be tool config, not prose.** A component gallery is not
a fact you write down — it is a query. `shadcn` and Magic UI both publish their
catalog as a live, queryable registry, and MCP is the tool that queries it. Once
that is wired up, concern 7 stops being a doc at all.

## Setup — two MCP servers, and how they relate

Both are real, official, and separately maintained. They solve slightly
different problems, so know which one you are reaching for.

### shadcn — the general mechanism

The primitive layer (button, dialog, form, table, ...) and the mechanism for
everything else, including Magic UI. Ships with the `shadcn` CLI itself — no
separate package.

```bash
npx shadcn@latest mcp init --client <host>   # writes the host's own config format
```

`--client claude` writes `.mcp.json` (Claude Code); `cursor` writes
`.cursor/mcp.json`; `vscode` writes `.vscode/mcp.json`. Where a host has no
`init` support, or the project prefers to review the config before it lands, the
manual form is the same everywhere — a generic `mcpServers` block:

```json
{
  "mcpServers": {
    "shadcn": { "command": "npx", "args": ["shadcn@latest", "mcp"] }
  }
}
```

Tools it exposes: `get_project_registries`, `list_items_in_registries`,
`search_items_in_registries`, `view_items_in_registries`,
`get_item_examples_from_registries`, `get_add_command_for_items`. The last one
is the load-bearing detail — it returns the CLI command, it does not run it.
The agent still runs `npx shadcn@latest add <item>` itself, which is what
**vendors the component's source into the repo** rather than installing it as
an opaque dependency. After that line runs, the component is owned code: it
lives in `components/ui/`, reads like anything else the project wrote, and
concern 3/4's per-directory `AGENTS.md` rules govern it same as any file there.

A port exists for React (the default), Vue (`shadcn-vue`) and Svelte
(`shadcn-svelte`); the MCP mechanics are the same across all three.

### Magic UI — a registry, reachable two ways

Magic UI (animated / marketing components: `marquee`, `dock`, `animated-beam`,
`bento-grid`, particle and text effects) publishes a shadcn-compatible
registry. That gives two legitimate ways to reach it, and they are not
equivalent:

**Option A — register it as a namespace inside shadcn's own mechanism.**
One entry in `components.json`:

```json
{
  "registries": {
    "@magicui": "https://magicui.design/r/{name}.json"
  }
}
```

After that, `@magicui/dock` is just another item to the same six shadcn tools
above — `search_items_in_registries` finds it, `get_add_command_for_items`
returns `npx shadcn@latest add @magicui/dock`. One MCP server, one install
path, one place a future session looks. This is the default — it is the same
"one canonical mechanism, not two" instinct `skill-map.md` applies to spec
directories and root context files, applied here to component sourcing.

**Option B — Magic UI's own MCP server**, `@magicuidesign/mcp`, in addition:

```bash
npx @magicuidesign/cli@latest install <host>   # cursor, windsurf, claude, cline, roo-cline
```

or manually:

```json
{
  "mcpServers": {
    "magicuidesign-mcp": { "command": "npx", "args": ["-y", "@magicuidesign/mcp@latest"] }
  }
}
```

Tools: `listRegistryItems`, `searchRegistryItems`, `getRegistryItem` — Magic
UI's own catalog, with richer per-item descriptions and demo source than a
generic registry item carries. Installing still ends the same way: a `shadcn
add` command against Magic UI's registry.

**Default to Option A.** Add Option B only when the project leans hard on Magic
UI specifically — a marketing site, a landing-page-heavy product — and the
richer discovery earns the second server. A second MCP server for a catalog the
first one can already reach is the same failure lanes.md rules against for spec
folders: two homes for one thing, and the newer one drifts out of habit rather
than by decision.

Both servers only *discover and vendor*. Neither one styles, themes, or
customizes what it fetches — that is still concern 6's job, below.

## The ladder, with one UI-specific rung

`SKILL.md`'s ladder: need it? exists here? stdlib? platform? installed
dependency? one line? For a UI component, one rung goes between "exists here"
and "write it":

1. Does this need to exist?
2. **Does it already exist in this project's `components/ui/` (or
   `components/magicui/`)?** Grep, not memory.
3. **Is it in shadcn's registry or Magic UI's?** `search_items_in_registries`,
   then `view_items_in_registries` to read the real source before vendoring it
   — same "evidence before assertions" rule the rest of this skill runs on.
   `get_item_examples_from_registries` first if the usage shape is unclear.
4. Only then write it — matching the project's existing token and variant
   conventions, not a fresh pattern.

Step 3 is not optional politeness. A hand-rolled dialog with its own focus trap
and its own escape-key handling is the component-layer version of the string
utility groundwork's ladder already forbids reinventing — except the failure
mode here is worse, because the bugs are accessibility bugs, and the registry
version has already had them found.

## Concern 5 — tokens

Unchanged by any of the above: a real CSS/theme file (or Tailwind config),
governed by whatever closed-scale test `tooling-floor.md` already recommends
for spacing, radii, and type sizes. shadcn and Magic UI both consume the
project's existing tokens rather than shipping their own — that is the whole
reason a vendored component reads as the project's code and not a vendor's.

## Concern 6 — direction, now including *which registry supplies what*

`lanes.md` already has the framing: **the direction is the brief, not the
rival** — a design skill gets handed the approved direction as constraints, not
asked to re-litigate it. Extend that brief with one more line, decided once at
bootstrap and not re-decided per component:

> Primitives — `shadcn`. Motion and marketing flourishes — Magic UI, used
> sparingly. [Any locked exceptions.]

State it in the design doc (the same file `lanes.md` calls a design brief) so a
session reaches for the plain primitive by default and treats an animated one
as a deliberate choice, not a habit. A settings screen and a landing page do
not carry the same amount of motion, and a repo with no ruling here re-decides
it component by component, which is how a product page ends up with a
particle-effect toggle switch.

## Concern 7 — the gallery is the directory

If concern 7 gets a file at all, it is one pointer, not a catalog:

```markdown
## Components

Primitives live in `components/ui/` (shadcn), motion/marketing pieces in
`components/magicui/` (Magic UI). Both are vendored, not npm dependencies —
read and edit them like any other file in this repo.

Browse or add more via the shadcn MCP tools (`search_items_in_registries`,
`get_add_command_for_items`) rather than listing them here — this file would
go stale the first time a component changed and nobody remembered to edit it.
```

That is the whole file. If the project has no `ui-registry.md`, do not write
one — the directory plus the MCP tools already answer the question the file
would have.

## Offering this at bootstrap

Same posture as the contract-gate hooks in `contract-gate.md`: **opt-in, shown
before written.** During Step 1 (inventory), check for signals this already
applies — `components.json`, a `components/ui/` directory, `shadcn` or
`@magicuidesign/mcp` in `package.json`, an existing `.mcp.json`. If the project
has a component-based frontend and none of that exists yet, offer the setup:
show the MCP config you would write and the `components.json` registries block,
and wait for confirmation before writing either. Never assume Option B; default
to Option A and name it as the default rather than silently picking it.

If the signals show this is already wired up, treat concern 7 as resolved —
write the one-line pointer above if it does not exist, and move on. Re-running
this setup on a project that already has it is the "generating all nine on a
repo that has seven" anti-pattern, once per UI concern instead of once per file.

## A caution, not a rule

These tools vendor code fast, which makes it easy to reach for a registry
component before checking whether the project actually needs the thing it
adds. The ladder's rung 1 — *does this need to exist* — still runs first.
`get_item_examples_from_registries` before installing is the guard: if the
example does not match what the task actually needs, that is a signal to look
further, not to install anyway and cut it down.

Commands and package names above are current as of when this was written;
verify against `ui.shadcn.com/docs/mcp` and `magicui.design` if they read as
stale — both projects move fast enough that an exact flag can drift.
