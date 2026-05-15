# Repository structure

Recall is organised as a **pseudo-monorepo**: one git repo, four
runnable apps, three internal packages, structured infrastructure
directories. The structure is set up to be *split-ready* — every
top-level directory has a clean future-extraction path — but the
project is **not split today**, and that is deliberate.

```
recall/
├── apps/
│   ├── desktop/         the PyQt6 launcher + FastAPI service
│   │                    (Python tree currently at the repo root;
│   │                    see apps/desktop/README.md for the
│   │                    migration plan)
│   ├── web/             the marketing site (Next.js)
│   ├── docs/            the documentation site (Mintlify)
│   └── extension/       the Chrome / Edge MV3 browser extension
│
├── packages/            shared internal libraries
│   ├── shared/          constants, terminology, small helpers
│   ├── design-system/   design tokens + UI primitives
│   └── contracts/       wire schemas + API contracts
│
├── infra/               build + release infrastructure
│   ├── installers/      installer specs, code-signing notes
│   ├── release/         release pipeline assets
│   └── scripts/         dev bootstrap + maintenance scripts
│
├── assets/              non-code artefacts
│   ├── screenshots/     product captures (light + dark)
│   ├── branding/        logos, icon sources, brand notes
│   └── demos/           demo scripts, recording cues
│
├── archive/             deprecated work kept for context
│
├── CLAUDE.md            engineering charter
├── ROOT_ARCHITECTURE.md system boundaries + dependency graph
├── REPO_STRUCTURE.md    (this file)
├── README.md, etc.
└── (Python tree at root for now — see apps/desktop/README.md)
```

## Why pseudo-monorepo first

A pseudo-monorepo gives Recall four properties that a true
monorepo with build orchestration (Turborepo, Nx, Bazel) does
not need to give us yet:

1. **A single PR can change the engine + the docs + the
   marketing surface together.** This is the dominant change
   shape for a product that's still maturing. The cost of
   coordinating four PRs across four repos before that's worth
   it is real.
2. **Discoverability for new contributors.** Everything that
   touches the product is two clicks away. The
   `ROOT_ARCHITECTURE.md` map gives them the mental model.
3. **No build-orchestration tax.** No `nx graph`, no
   `turbo run`, no remote-cache infrastructure. Each app builds
   with its own native tooling (`pyinstaller`, `next build`,
   Mintlify, web-ext) and the dev scripts know how to call each.
4. **Reversible.** Every top-level directory has a clean future
   extraction path documented below. The day a directory needs
   its own repo, `git filter-repo` + the documented boundary is
   enough.

The decision matrix:

| Concern | Pseudo-monorepo (today) | Multi-repo (future) |
|---|---|---|
| PR scope crosses two apps | One PR | Two co-ordinated PRs |
| Discoverability | All in one tree | Four repos to find |
| Build orchestration | Native per app | Per-repo workflows |
| Release coupling | Implicit (shared tag) | Independent (separate cadences) |
| Contribution friction | Low | Higher per-repo onboarding |

Today the left column is the right tradeoff. When it stops
being, we'll split.

## Future split criteria

Each top-level directory under `apps/` and `packages/` carries
a documented gate condition for being extracted to its own
repo. The shortest form lives in
[`RELEASE.md`](RELEASE.md) § *Repo split plan*. The fuller
treatment per directory:

### `apps/desktop`

**Stays in-repo until:** the launcher and the extension start
shipping on independent cycles (i.e. an extension-only release
becomes routine), OR external embedders start consuming the
`api/` HTTP surface as a library and need versioned releases
independent of the launcher binary.

**Extraction shape:** `recall-core` repo holds `apps/desktop/` +
the `infra/installers/` Python-relevant pieces. Re-exposes the
`/v1/*` API surface as its public contract.

### `apps/web`

**Stays in-repo until:** the marketing team becomes a separate
contributor pool with a different review cadence, OR the web
build starts conflicting with engine PRs more often than helping.

**Extraction shape:** `recall-web` repo on Vercel-style CD. Pulls
shared tokens from `packages/design-system/` (which would be
extracted alongside it as a published npm package).

### `apps/docs`

**Stays in-repo until:** docs PRs start outnumbering engine PRs
by a wide margin and the cadence drift starts dragging engine
reviews.

**Extraction shape:** `recall-docs` Mintlify-hosted from a
separate repo. Pulls shared vocabulary references via
`packages/shared/`.

### `apps/extension`

**Stays in-repo until:** Firefox / Safari ports start shipping
with their own review cycles, OR the extension's reviewable
release artefact needs its own changelog.

**Extraction shape:** `recall-extension` repo per browser, each
publishing to its store. The `host_permissions` lockstep with
the desktop API stays a versioned contract in
`packages/contracts/`.

### `packages/*`

**Stay in-repo until:** an external consumer (a partner, a third-
party plugin, a community fork) needs to take a versioned
dependency on the package. At that point the package is
extracted and published to the relevant ecosystem registry
(`pypi` for shared/contracts when they go Python, `npm` for
design-system).

## Package boundaries

The three packages are **opt-in shared zones**. Most code does
not need them. The rules:

### `packages/shared/`

- **For:** constants, canonical vocabulary mappings, small
  utility helpers that two apps both need (e.g. the date
  formatter that the launcher and the marketing site both use to
  print "2d ago").
- **Not for:** business logic. If it does something the engine
  cares about, it lives in `apps/desktop/app/core/`.
- **Allowed dependencies:** none beyond the Python / TypeScript
  standard library.
- **Owned by:** everyone. Anyone can add to it; anyone can ask
  for additions to be removed.

### `packages/design-system/`

- **For:** colour tokens, typography scale, spacing scale, motion
  ramp, elevation ladder, and the small set of UI primitives
  that get reused (e.g. the kbd-chip pattern, the row hairline).
  Same content the
  [visual system doc](apps/docs/architecture/visual-system.mdx)
  describes — codified into reusable units.
- **Not for:** entire components. Pages and feature components
  live in `apps/web/` or `apps/desktop/app/ui/`.
- **Allowed dependencies:** Tailwind config (for web) and the
  Python style constants (for desktop). No app-specific code.
- **Owned by:** the visual-system steward (whoever is currently
  responsible for keeping the spacing scale honest).

### `packages/contracts/`

- **For:** the wire formats that cross app boundaries — event
  schemas (browser_visit, browser_search, chat_session, open),
  the `/v1/*` API request and response shapes, the
  thread/evolution/recovery JSON shapes the launcher and the
  extension both encode.
- **Not for:** in-app types. A dataclass that only the engine
  needs is not a contract.
- **Allowed dependencies:** none. Contracts are pure data
  declarations; importing engine code would invert the
  dependency direction.
- **Owned by:** whoever is currently the API maintainer.

Today these packages are empty by design — the canonical
material exists in `apps/desktop/api/schemas.py` (contracts),
`apps/web/tailwind.config.ts` + `apps/docs/architecture/
visual-system.mdx` (design-system), and the vocabulary table in
[`CLAUDE.md`](CLAUDE.md) § *"Naming and terminology"* (shared).
Each `packages/*/README.md` records the extraction plan and the
gate condition for actually populating the directory.

## Why the Python tree is still at the root

When the pseudo-monorepo refactor was performed, the
non-Python trees (`web/`, `docs/`, `extension/`, `scripts/`)
moved into their new homes immediately because each is a
self-contained tree with no path-sensitive build artefacts.

The Python tree (`app/`, `api/`, `recall.py`, `_smoke_api.py`,
`recall.spec`, `requirements.txt`) is currently still at the
repository root. Two reasons:

1. **PyInstaller specs reference relative paths.** `recall.spec`
   contains `os.path.join("app", "assets", "icon.ico")` and
   `collect_data_files("chromadb")`-style hooks. Moving the
   tree without updating the spec's spec-relative path
   resolution risks an installer build that succeeds locally
   but ships a broken executable.
2. **Cross-platform verification is the gate.** The unit smoke
   test passes regardless of file location (it uses Python
   package paths, not disk paths), but the *PyInstaller build*
   needs verification on Windows + macOS + Linux to know the
   move is safe. That verification is not safe to perform in a
   single landing pass alongside the rest of the restructure.

The migration plan is documented in
[`apps/desktop/README.md`](apps/desktop/README.md). When the
move runs, every reference to `app/` / `api/` / `recall.py` /
`_smoke_api.py` / `recall.spec` in the repo's docs is updated
in the same PR.

## Contributor guidance

A contributor opening the repo for the first time:

1. Read [`CLAUDE.md`](CLAUDE.md) for the engineering charter.
2. Read [`ROOT_ARCHITECTURE.md`](ROOT_ARCHITECTURE.md) for the
   system boundaries and dependency graph.
3. Find their target directory in the tree above.
4. Read that directory's `README.md` (every top-level
   subdirectory has one).
5. Follow the bootstrap instructions in
   [`CONTRIBUTING.md`](CONTRIBUTING.md).

If a contribution touches more than one app or package, it
goes through the **cross-cutting review path** — the PR
description names every directory it touches and a
maintainer for each. That's a soft process today; if it
becomes load-bearing it codifies into CODEOWNERS.

## What the structure does *not* do

- It does not install per-package build tooling. The shared
  Tailwind config lives in `apps/web/` until enough other
  consumers (a Storybook, a second front-end) need it.
- It does not create a cross-app type-checking pipeline. The
  contracts package is documented as a future extraction; for
  now the Pydantic models in `apps/desktop/api/schemas.py` are
  the canonical contract.
- It does not enforce import directionality through tooling.
  The convention is that nothing under `apps/` may import from
  another `apps/` sibling, only from `packages/`. Today no
  cross-app Python imports exist; if they appear, the lint
  rule comes with the offending PR.
