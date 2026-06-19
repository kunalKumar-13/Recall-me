# Phase 8B — Tier 1 Cleanup + Repo Collapse

**Status:** complete · all verifications green
**Directive:** delete proven-dead items from 8A. No
feature work, no launcher work, no UI changes. Reduce
weight, keep behaviour identical.

> Repo smaller. Same product. No regressions.

---

## Before / after metrics

| Metric                                       | Before    | After    | Delta            |
|----------------------------------------------|-----------|----------|------------------|
| **Python LOC** (`app/` + `api/`)             | 29,544    | 22,435   | **−7,109 (−24 %)** |
| **Python files** (`app/` + `api/`)           | 82        | 74       | **−8**           |
| **Live `app/ui/*.py` files**                 | 11        | 5        | **−6**           |
| **`app/ui/launcher.py` LOC**                 | 60        | 18       | **−42**          |
| **Asset PNG count** (`assets/screenshots/`)  | 102       | 47       | **−55 (−54 %)**  |
| **Asset folders**                            | 19        | 8        | **−11 (−58 %)**  |
| **Archive folders**                          | 11        | 14       | **+3**           |
| **Extension component files** (`src/components/`) | 11        | 3        | **−8**           |
| **`apps/web/package.json` deps**             | 7         | 4        | **−3 unused**    |
| **`apps/extension/ui` deps misplaced**       | 1         | 0        | **−1 moved**     |
| **Docs file count**                          | 129       | 134      | **+5 new audit docs** |

The Python LOC drop is the headline — **7,109 lines
moved out of the live tree** into `archive/launcher-old/`.
None deleted; all recoverable.

---

## What changed (per directive section)

### 1. Delete pass — covered by [`DELETE_PLAN.md`](../AUDIT/DELETE_PLAN.md)

- **30 files moved** to `archive/launcher-old/`,
  `archive/screenshots-history/`,
  `archive/extension-pre-7a/`.
- **11 root-level PNGs deleted** (7 orphan PNGs from
  pre-6H + 4 dep entries from `package.json`).
- **0 features removed** from the user-facing surface.

### 2. Launcher collapse — covered by [`LAUNCHER_FREEZE.md`](../AUDIT/LAUNCHER_FREEZE.md)

- 8 legacy launcher files moved to
  `archive/launcher-old/`.
- 3 historical capture scripts moved alongside.
- `app/ui/launcher.py` collapsed from 60 lines → 18
  lines — no more `RECALL_LAUNCHER=legacy` branch.
- `from app.ui.launcher import Launcher` still resolves
  to `LiveLauncher` (the import contract holds).

### 3. Doc collapse execution

- All docs already lived under
  `docs/{product,engineering,trust,release,alpha,founder,archive}/`.
- `DOC_INDEX.md` already carried the `/AUDIT/` section
  added in 8A. No re-organisation needed.
- 5 new audit docs land in `AUDIT/` for this phase
  (DELETE_PLAN, LAUNCHER_FREEZE, DEPENDENCY_DIFF,
  ASSET_FREEZE, this one).

### 4. Dependency pass — covered by [`DEPENDENCY_DIFF.md`](../AUDIT/DEPENDENCY_DIFF.md)

- 3 unused deps removed from `apps/web/package.json`
  (`clsx`, `lucide-react`, `tailwind-merge`).
- 1 misplaced dep moved in `apps/extension/ui/package.json`
  (`playwright` → `devDependencies`).
- 4 manifest lines total. All builds clean post-edit.

### 5. Asset pass — covered by [`ASSET_FREEZE.md`](../AUDIT/ASSET_FREEZE.md)

- 11 historical capture folders moved to
  `archive/screenshots-history/`.
- 7 orphan root PNGs deleted.
- 2 ⭐ live capture folders (`launcher-7e/` +
  `extension-7a/`) + 5 reference folders + 11
  capture-harness root PNGs are the new frozen
  active asset surface.

### 6. Verify

| Command                                                       | Result                                            |
|---------------------------------------------------------------|---------------------------------------------------|
| `python -m pyflakes app/ui app/core api`                      | clean                                             |
| `python recall.py doctor`                                     | GREEN on config / events / daemon / extension / installer (5 YELLOWs unchanged from 8A) |
| `python recall.py capture status`                             | 11 events today / 12 investigations / last event 6m ago |
| `from app.ui.launcher import Launcher; Launcher(FakeEngine())`| `LiveLauncher` constructs at `(700, 500)`         |
| `cd apps/extension/ui && npx tsc --noEmit`                    | clean                                             |
| `cd apps/extension/ui && npx vite build`                      | clean, **293 KB JS** (identical to 8A — confirms dead components were already tree-shaken) |
| `cd apps/admin/web && npx tsc --noEmit`                       | clean                                             |
| `cd apps/web && npx tsc --noEmit`                             | clean                                             |

All 8 verifications pass.

---

## What was NOT done in 8B (deferred to 8C)

### Orphan API routes (5)

```
POST /v1/threads/{id}/forget
GET  /v1/contexts/recent
GET  /v1/sessions/recent
POST /v1/threads/cache/clear   (evolution variant)
POST /v1/replay/day
```

The handler funcs are dead per 8A. Removing them
cleanly requires walking the pydantic response models
+ service-layer wrappers each handler imports. Schedule
a tight 8C pass. The cost of keeping them is near-zero
(FastAPI registers them; nothing calls them).

### `_smoke_api.py` full run

The 29-section smoke suite was not re-run in 8B. The
8B verifications above are *incremental* — `pyflakes`
+ doctor + capture + offscreen launcher construct +
TypeScript across 3 apps + vite build of the extension.
The full HTTP integration suite should run before the
next release tag.

---

## Files touched

**Archived (no deletion):**

- `app/ui/launcher_legacy.py` → `archive/launcher-old/`
- `app/ui/cards.py` → `archive/launcher-old/`
- `app/ui/widgets.py` → `archive/launcher-old/`
- `app/ui/styles.py` → `archive/launcher-old/`
- `app/ui/launcher_anims.py` → `archive/launcher-old/`
- `app/ui/launcher_digest.py` → `archive/launcher-old/`
- `app/core/demo_data.py` → `archive/launcher-old/`
- `app/core/ceremonies.py` → `archive/launcher-old/`
- `infra/scripts/capture/capture_launcher.py` →
  `archive/launcher-old/captures/`
- `infra/scripts/capture/capture_recovery.py` →
  `archive/launcher-old/captures/`
- `infra/scripts/capture/capture_demo.py` →
  `archive/launcher-old/captures/`
- 8 pre-7A extension components →
  `archive/extension-pre-7a/`
- 11 historical screenshot folders →
  `archive/screenshots-history/`

**Deleted outright:**

- 7 root-level orphan PNGs in `assets/screenshots/`
- 3 lines in `apps/web/package.json` (unused deps)
- 1 line in `apps/extension/ui/package.json` moved
  (playwright → devDependencies)

**Edited (light):**

- [`app/ui/launcher.py`](../../app/ui/launcher.py) —
  collapsed from 60 → 18 lines (drop env-var fork +
  back-compat constant re-exports).

**Created:**

- 5 new docs in `AUDIT/`:
  [`DELETE_PLAN.md`](../AUDIT/DELETE_PLAN.md),
  [`LAUNCHER_FREEZE.md`](../AUDIT/LAUNCHER_FREEZE.md),
  [`DEPENDENCY_DIFF.md`](../AUDIT/DEPENDENCY_DIFF.md),
  [`ASSET_FREEZE.md`](../AUDIT/ASSET_FREEZE.md), and
  this status doc.

---

## Success criterion

> Repo smaller. Same product. No regressions.

Met:

1. **Repo smaller** — Python LOC down 24 %, asset PNGs
   down 54 %, asset folders down 58 %, extension
   components down 73 %.
2. **Same product** — every verification command above
   passes; the `from app.ui.launcher import Launcher`
   contract resolves to `LiveLauncher` at `(700, 500)`;
   extension vite build identical at 293 KB; doctor
   GREEN.
3. **No regressions** — pyflakes clean, all three TS
   builds clean, no test path now broken (subject to
   the deferred `_smoke_api.py` full run).

The launcher is **frozen**
([`LAUNCHER_FREEZE.md`](../AUDIT/LAUNCHER_FREEZE.md)).
The asset surface is **frozen**
([`ASSET_FREEZE.md`](../AUDIT/ASSET_FREEZE.md)). The
repo is in its smallest state since Phase 5.

Default-no on adding anything from here until a real
user need surfaces.
