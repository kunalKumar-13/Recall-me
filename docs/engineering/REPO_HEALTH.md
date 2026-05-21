# REPO_HEALTH.md — the size and shape, measured

Real numbers from a `wc -l` pass at the close of Phase 5D. Tracked
so a new engineer can see, in one page, how big the codebase is
and how it has been kept honest.

Pairs with [`COMPLEXITY.md`](COMPLEXITY.md) (where size lives) and
[`DEAD_CODE_AUDIT.md`](DEAD_CODE_AUDIT.md) (what was removed).

---

## Headline metrics — Phase 5D close

| Metric | Value |
|---|---|
| Python LOC (`app/` + `api/`) | **20,152** |
| Archived LOC (`archive/`) | **3,735** |
| Largest Python file | `app/ui/launcher.py` (2,536 LOC) |
| Files > 1,000 LOC | 4 (`launcher.py`, `widgets.py`, `api/main.py`, `recovery.py`) |
| Files 500–1,000 LOC | 7 (`evolution`, `threads`, `settings`, `resurfacing`, `episodic`, `events`, `cards`) |
| Median file | `app/core/api_client.py` (~250 LOC) |
| TODO / FIXME / HACK comments | **0** across `app/` + `api/` |
| Web components on disk | **15** (down from 20 — Phase 5D archived 5 orphans) |
| Web components imported by `page.tsx` | **11** |
| Extension popup gzipped bundle | ~90 KB |
| Engine smoke sections | 35 |
| Test count | 35 smoke sections (one `_smoke_api.py` runner) |
| `requirements.txt` runtime packages | 9 |
| `requirements.txt` build-only (PyInstaller) | commented (uncomment to build) |

## What changed this cycle

| Phase 5D action | Delta |
|---|---|
| Archived 5 orphan web components | −5 components in `apps/web/` |
| Audit docs added | `DEAD_CODE_AUDIT.md`, `COMPLEXITY.md`, `DEPENDENCIES.md`, this file |
| Net source-tree LOC | unchanged (archive moves are file-moves, not deletes) |
| Behaviour | **unchanged** (web build verified clean after archive) |

## Tracked over time

Each future hygiene pass appends a row.

| Date | Python LOC | Archived LOC | Largest file (LOC) | Files > 1,000 | Notes |
|---|---|---|---|---|---|
| 2026-05-20 | 20,152 | 3,735 | launcher.py (2,536) | 4 | Phase 5D — 5 web orphans archived |

Update by running:

```bash
find app api -name "*.py" -not -path "*/__pycache__/*" -exec wc -l {} + | tail -1
find archive -name "*.tsx" -o -name "*.py" | xargs wc -l | tail -1
```

## The safe-delete policy

A piece of code or asset is removed only when **all three** are
true:

1. **Unused.** Grep the import graph; nothing references it.
2. **Verified.** The relevant test runs after removal —
   `_smoke_api.py` for engine; `npx next build` for web;
   `npm run build` for the extension; launcher import-check for UI.
3. **Documented.** The removal goes in `CHANGELOG.md` and the row
   gets a paragraph in [`DEAD_CODE_AUDIT.md`](DEAD_CODE_AUDIT.md)
   citing the verification.

Anything that fails one of those three is **archived** under
`archive/`, never deleted. `archive/` carries history; it does not
ship.

## What a new engineer should know in one read

- **One process.** The desktop tree (`app/` + `api/`) is the
  product — a single Python process embedding FastAPI + a PyQt6
  launcher. `app/main.py` is the wiring file.
- **Seven layers.** Events → sessions → contexts → resurfacing →
  threads → evolution → recovery. They compose strictly upward;
  each is its own file under `app/core/`.
- **One UI surface.** `app/ui/launcher.py` is the launcher window;
  `app/ui/widgets.py` is its widget zoo; `app/ui/cards.py` is the
  Phase 4K card set; `app/ui/settings.py` is the settings dialog.
- **Two web surfaces.** `apps/web/` is the marketing site;
  `apps/docs/` is the Mintlify docs site; `apps/extension/` is the
  browser companion (popup built from `apps/extension/ui/`).
- **One source of truth.** [`CLAUDE.md`](../../CLAUDE.md) is the
  engineering charter; everything else is consistent with it.

A first read of those five paragraphs + [`CLAUDE.md`](../../CLAUDE.md) +
[`SURFACE_MAP.md`](../product/SURFACE_MAP.md) is the one-hour onboarding the
directive's success criterion (*"new engineer joins, understands
repo in 1 hour"*) asks for.
