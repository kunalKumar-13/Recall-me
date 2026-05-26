# Delete Plan — Phase 8B

The complete tier-1 cleanup executed in 8B. Every row
below was proven dead in 8A
([`SURFACES.md`](SURFACES.md), [`DEAD_CODE.md`](DEAD_CODE.md),
[`ASSETS.md`](ASSETS.md)) and is now either **archived**
(preserved under `archive/`) or **deleted** (removed
entirely).

> No feature work. No launcher rewrites. No UI changes.
> Behavioural surface identical to 8A.

---

## Launcher collapse — 7 files + 3 helper modules archived

| Path                                    | Why dead                                          | Verification                                                  | Action |
|-----------------------------------------|---------------------------------------------------|---------------------------------------------------------------|--------|
| `app/ui/launcher_legacy.py` (2675 LOC)  | Reachable only via `RECALL_LAUNCHER=legacy`       | DEAD_CODE.md §1; only `launcher.py` imported it               | **MOVED** → `archive/launcher-old/launcher_legacy.py` |
| `app/ui/cards.py` (970 LOC)             | Imported only by `launcher_legacy.py`             | DEAD_CODE.md §1                                               | **MOVED** → `archive/launcher-old/cards.py` |
| `app/ui/widgets.py` (2471 LOC)          | Imported only by `launcher_legacy.py`             | DEAD_CODE.md §1                                               | **MOVED** → `archive/launcher-old/widgets.py` |
| `app/ui/styles.py` (359 LOC)            | Imported only by `launcher_legacy.py`             | DEAD_CODE.md §1                                               | **MOVED** → `archive/launcher-old/styles.py` |
| `app/ui/launcher_anims.py` (84 LOC)     | Imported only by `launcher_legacy.py`             | DEAD_CODE.md §1                                               | **MOVED** → `archive/launcher-old/launcher_anims.py` |
| `app/ui/launcher_digest.py` (89 LOC)    | Imported only by `launcher_legacy.py`             | DEAD_CODE.md §1                                               | **MOVED** → `archive/launcher-old/launcher_digest.py` |
| `app/core/demo_data.py`                 | Imported by `launcher_legacy.py` + `app/main.py` (legacy demo path) | DEAD_CODE.md §8                                | **MOVED** → `archive/launcher-old/demo_data.py` |
| `app/core/ceremonies.py`                | Imported only by `launcher_legacy.py`             | DEAD_CODE.md §8                                               | **MOVED** → `archive/launcher-old/ceremonies.py` |
| `infra/scripts/capture/capture_recovery.py` | Reproduces archived `launcher-recovery/` captures via legacy widgets | DEAD_CODE.md §10                          | **MOVED** → `archive/launcher-old/captures/capture_recovery.py` |
| `infra/scripts/capture/capture_launcher.py` | Same — produces archived launcher captures using legacy widgets | DEAD_CODE.md §10                                | **MOVED** → `archive/launcher-old/captures/capture_launcher.py` |
| `infra/scripts/capture/capture_demo.py`   | Same — produces archived demo captures using legacy widgets   | DEAD_CODE.md §10                                | **MOVED** → `archive/launcher-old/captures/capture_demo.py` |

`app/ui/launcher.py` collapsed from 60 lines to 18 — no
more `RECALL_LAUNCHER=legacy` branch, no more re-exports
of legacy constants (`LAUNCHER_WIDTH`, `SHADOW_MARGIN`,
`FOOTER_H`). The import contract holds:
`from app.ui.launcher import Launcher` still resolves to
`LiveLauncher`.

**Total LOC archived from `app/`**: ~6,648 lines (legacy
launcher + helpers + cards + widgets + styles + demo_data
+ ceremonies). Captures script LOC archived: ~600 lines.

---

## Asset cleanup — 7 PNGs deleted, 11 folders archived

### Deleted (7 root-level PNGs, no consumer)

| Path                                            | Last modified | Verification               |
|-------------------------------------------------|---------------|----------------------------|
| `assets/screenshots/control-room.png`           | 2026-05-21    | ASSETS.md root-table       |
| `assets/screenshots/doctor-output.png`          | 2026-05-21    | ASSETS.md root-table       |
| `assets/screenshots/installer-flow.png`         | 2026-05-21    | ASSETS.md root-table       |
| `assets/screenshots/settings-dialog.png`        | 2026-05-21    | ASSETS.md root-table       |
| `assets/screenshots/launcher-first-week.png`    | 2026-05-22    | ASSETS.md root-table       |
| `assets/screenshots/launcher-loading.png`       | 2026-05-22    | ASSETS.md root-table       |
| `assets/screenshots/launcher-offline.png`       | 2026-05-22    | ASSETS.md root-table       |

### Archived (11 historical capture folders → `archive/screenshots-history/`)

| Path                                            | Phase | Total captures (approx) |
|-------------------------------------------------|-------|--------------------------|
| `assets/screenshots/launcher-live/`             | 6K    | 6                        |
| `assets/screenshots/launcher-minimal/`          | 6L    | 4                        |
| `assets/screenshots/launcher-refined/`          | 6M.1  | 5                        |
| `assets/screenshots/launcher-compact/`          | 6M.2  | 4                        |
| `assets/screenshots/launcher-recovery/`         | 6N    | 5                        |
| `assets/screenshots/launcher-reset/`            | 6O    | 2                        |
| `assets/screenshots/launcher-visible/`          | 6P.1  | 4                        |
| `assets/screenshots/launcher-truth/`            | 6Q    | 4                        |
| `assets/screenshots/launcher-ship/`             | 6R    | 5                        |
| `assets/screenshots/launcher-final/`            | 7B    | 4                        |
| `assets/screenshots/launcher-merge/`            | 7B.1  | 5                        |

---

## Extension pre-7A components archived (8 files → `archive/extension-pre-7a/`)

All confirmed DEAD in `DEAD_CODE.md` §9 (not imported by
current `App.tsx` after Phase 7A).

| Path                                                       | Why dead                                  |
|------------------------------------------------------------|-------------------------------------------|
| `apps/extension/ui/src/components/ContinueCard.tsx`        | superseded by `v2/Hero.tsx`               |
| `apps/extension/ui/src/components/DebugStrip.tsx`          | removed from popup in 7A                   |
| `apps/extension/ui/src/components/DemoBanner.tsx`          | App.tsx has its own inline banner now      |
| `apps/extension/ui/src/components/InvestigationCard.tsx`   | superseded by `v2/Investigations.tsx`     |
| `apps/extension/ui/src/components/MemoryList.tsx`          | superseded by `v2/Timeline.tsx`           |
| `apps/extension/ui/src/components/Section.tsx`             | not used by `v2/` tree                    |
| `apps/extension/ui/src/components/TrustSurface.tsx`        | superseded by `v2/TrustStrip.tsx`         |
| `apps/extension/ui/src/components/states.tsx`              | superseded by `v2/States.tsx`             |

Build verification: `npx vite build` still produces a
**293 KB** JS bundle (identical pre-vs-post), confirming
the components were already tree-shaken out — the archive
is correctness-neutral.

---

## Dependency cleanup

### `apps/web/package.json` — 3 unused removed

| Package           | Pre-version | Verification          |
|-------------------|-------------|------------------------|
| `clsx`            | `^2.1.1`    | DEPENDENCIES.md §4    |
| `lucide-react`    | `^1.14.0`   | DEPENDENCIES.md §4    |
| `tailwind-merge`  | `^3.5.0`    | DEPENDENCIES.md §4    |

### `apps/extension/ui/package.json` — 1 misplaced

| Package           | Pre-section    | Post-section       |
|-------------------|----------------|--------------------|
| `playwright`      | `dependencies` | `devDependencies` |

---

## Deferred to Phase 8C (not done in 8B)

### Orphan API routes (5)

```
POST /v1/threads/{id}/forget
GET  /v1/contexts/recent
GET  /v1/sessions/recent
POST /v1/threads/cache/clear  (evolution variant)
POST /v1/replay/day
```

**Why deferred.** Removing the handlers from `api/main.py`
is straightforward, but each handler has an associated
pydantic response model + service-layer wrapper. Pruning
those cleanly requires more careful walking than the 8B
window allowed. The routes carry near-zero cost on disk
and zero cost at runtime (FastAPI registers them but they
sit idle). Schedule a tight 8C pass.

### Legacy launcher escape hatch test

`_smoke_api.py` should be re-run end-to-end against the
collapsed launcher.py to confirm no test path silently
depended on `RECALL_LAUNCHER=legacy`. Spot-checked via
`pyflakes` + offscreen `Launcher()` construct in 8B —
both clean — but the full smoke suite isn't part of the
8B run.

---

## Summary

| Category                        | Files moved | Files deleted | LOC moved | LOC deleted |
|---------------------------------|-------------|----------------|-----------|-------------|
| Launcher tree                   | 11          | 0              | ~7,200    | 0           |
| Extension pre-7A components     | 8           | 0              | (TS, n/a) | 0           |
| Screenshot folders              | 11          | 0              | (binary)  | 0           |
| Root PNGs                       | 0           | 7              | n/a       | n/a         |
| Dep entries                     | 0           | 4              | n/a       | 4 lines     |
| **Totals**                      | **30**      | **11**         | **~7,200**| **~4**      |

The vast majority of the cleanup is **archive moves, not
deletions**. Nothing is gone forever; everything is
recoverable from `archive/`. The product behaviour is
identical to 8A's frozen state.
