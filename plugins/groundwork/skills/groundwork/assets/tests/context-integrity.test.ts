/**
 * The context files must describe things that exist.
 *
 * A pointer to something real saves a session; a pointer to something renamed
 * or never built costs one. This is not hypothetical -- the case that produced
 * this template: a root CLAUDE.md listed a port class that had never existed
 * anywhere in the backend, while omitting one that had shipped four days
 * earlier. A 900-test suite could not see it, because no test reads prose.
 *
 * Adjust CONFIG below and delete rules that do not apply. Every rule should
 * encode a drift that actually happened here; a rule guarding a hypothetical
 * is a rule someone will disable the first time it is inconvenient.
 *
 * Identifier lookups go through token sets rather than word-boundary regexes:
 * one pass over the source instead of one per name, and no escaping to get
 * wrong.
 */
import { existsSync, readFileSync, readdirSync, statSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";

// --------------------------------------------------------------------------
// CONFIG -- the only part that is project-specific.
// --------------------------------------------------------------------------
const CONFIG = {
  /** Repo root, relative to this test's working directory. */
  root: join(process.cwd(), ".."),

  /** Directories scanned for identifiers, and which extensions count. */
  sourceDirs: ["backend", "frontend/src"],
  sourceExts: [".py", ".ts", ".tsx"],
  skipDirs: ["node_modules", "__pycache__", ".venv", "dist", ".next"],

  /** Context files checked. Missing ones are skipped, not failed. */
  contextFiles: ["CLAUDE.md", "AGENTS.md", "CONTEXT.md"],

  /**
   * Path references inside backticks are checked for existence when they start
   * with one of these. Keeps `npm run foo` and prose out of the check.
   */
  pathPrefixes: ["backend", "frontend", "docs", "src", "app"],

  /**
   * Suffixes that mark a name as a real code identifier rather than prose.
   * A word in a context file ending in one of these must exist in source.
   */
  identifierSuffixes: [
    "Policy", "Strategy", "Repo", "Repository", "Service", "Client",
    "Renderer", "Extractor", "Generator", "Verifier", "Pipeline", "Adapter",
    "Provider", "Handler", "Store", "Context",
  ],

  /** Heading under which a glossary lists names that must NOT exist. */
  notTermsHeading: "## Not domain terms",
};
// --------------------------------------------------------------------------

const read = (rel: string) => readFileSync(join(CONFIG.root, rel), "utf8");
const has = (rel: string) => existsSync(join(CONFIG.root, rel));

function sourceText(): string {
  const walk = (dir: string): string[] => {
    if (!existsSync(dir)) return [];
    return readdirSync(dir).flatMap((entry) => {
      if (CONFIG.skipDirs.includes(entry)) return [];
      const path = join(dir, entry);
      if (statSync(path).isDirectory()) return walk(path);
      return CONFIG.sourceExts.some((e) => path.endsWith(e))
        ? [readFileSync(path, "utf8")]
        : [];
    });
  };
  return CONFIG.sourceDirs.flatMap((d) => walk(join(CONFIG.root, d))).join("\n");
}

const SOURCE = sourceText();

/** Every identifier that appears anywhere in the scanned source. */
const TOKENS = new Set(SOURCE.match(/[A-Za-z_][A-Za-z0-9_]*/g) ?? []);

/** Every name actually declared as a class. */
const CLASSES = new Set(
  [...SOURCE.matchAll(/class\s+([A-Za-z_][A-Za-z0-9_]*)/g)].map((m) => m[1]),
);

const present = CONFIG.contextFiles.filter(has);

it("finds source to check against", () => {
  // Guards the config itself: a wrong sourceDirs makes every rule below pass
  // vacuously, which is the worst outcome -- a green suite guarding nothing.
  expect(TOKENS.size).toBeGreaterThan(100);
  expect(present.length).toBeGreaterThan(0);
});

/**
 * The part of a context file that asserts things exist. Everything under the
 * not-a-term heading asserts the opposite -- it names what is deliberately
 * absent. Scanning it for identifiers flags every entry as missing, which is
 * the section working as designed.
 */
const claims = (file: string) => read(file).split(CONFIG.notTermsHeading)[0];

describe.each(present)("%s", (file) => {
  const text = claims(file);

  it("points only at paths that exist", () => {
    const prefixes = CONFIG.pathPrefixes.join("|");
    const paths = [
      ...text.matchAll(
        new RegExp("`((?:" + prefixes + ")/[A-Za-z0-9_./-]+)`", "g"),
      ),
    ].map((m) => m[1].replace(/\/$/, ""));

    expect([...new Set(paths)].filter((p) => !has(p))).toEqual([]);
  });

  it("names only identifiers that exist in the source", () => {
    const suffixes = CONFIG.identifierSuffixes.join("|");
    const named = [
      ...text.matchAll(
        new RegExp("\b([A-Z][A-Za-z0-9]*(?:" + suffixes + "))\b", "g"),
      ),
    ].map((m) => m[1]);

    expect([...new Set(named)].filter((n) => !TOKENS.has(n))).toEqual([]);
  });
});

// A glossary that lists "names that are NOT domain terms" is making a claim in
// the other direction. If one becomes real, the entry should be promoted --
// leaving it reads as a warning against something that now ships.
const glossary = CONFIG.contextFiles.find(
  (f) => has(f) && read(f).includes(CONFIG.notTermsHeading),
);

describe.runIf(glossary)("glossary", () => {
  it("keeps the not-a-term list honest -- those names must stay absent", () => {
    const notTerms = read(glossary!).split(CONFIG.notTermsHeading)[1] ?? "";
    const revived = [...notTerms.matchAll(/\*\*`?([A-Z][A-Za-z0-9]+)`?\*\*/g)]
      .map((m) => m[1])
      .filter((name) => CLASSES.has(name));

    expect(revived).toEqual([]);
  });
});
