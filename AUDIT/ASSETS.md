# Asset Audit — Phase 8A

Catalogue of every PNG under
[`assets/screenshots/`](../assets/screenshots/) with its
phase, status, and a real consumer reference (or
explicit ORPHAN flag).

> Status legend: **ACTIVE** = consumed by a live surface
> (web gallery, admin dashboard, capture rerun) ·
> **HISTORICAL** = referenced from a phase status doc
> only (kept for audit-trail traceability) · **ORPHAN**
> = no reference anywhere in the repo.

---

## Launcher capture folders (chronological)

| Folder                            | PNGs | Phase | Status        | Reference                                                  |
|-----------------------------------|------|-------|---------------|------------------------------------------------------------|
| `launcher-v2/`                    | 7    | 6B    | **ACTIVE**    | `apps/admin/web/app/launcher/page.tsx` + `apps/web/app/components/Screens.tsx` |
| `launcher-v3/`                    | 5    | 6I    | **ACTIVE**    | `apps/admin/web/app/launcher/page.tsx` (v2↔v3 diff strip) |
| `launcher-live/`                  | 6    | 6K    | **HISTORICAL**| Phase doc only                                             |
| `launcher-minimal/`               | 4    | 6L    | **HISTORICAL**| Phase doc only                                             |
| `launcher-refined/`               | 5    | 6M.1  | **HISTORICAL**| `docs/product/LAUNCHER_REVIEW.md`                          |
| `launcher-compact/`               | 4    | 6M.2  | **HISTORICAL**| `docs/engineering/PHASE_6M.2_STATUS.md`                    |
| `launcher-recovery/`              | 5    | 6N    | **HISTORICAL**| `docs/product/RECOVERY_VISUAL_AUDIT.md`                    |
| `launcher-reset/`                 | 2    | 6O    | **HISTORICAL**| `docs/product/LAUNCHER_RESET.md`                           |
| `launcher-visible/`               | 4    | 6P.1  | **HISTORICAL**| `docs/product/LAUNCHER_VISIBILITY.md`                      |
| `launcher-truth/`                 | 4    | 6Q    | **HISTORICAL**| `docs/product/SHOWCASE_TRUTH.md`                           |
| `launcher-ship/`                  | 5    | 6R    | **HISTORICAL**| `docs/product/LAUNCHER_SHIP_AUDIT.md`                      |
| `launcher-final/`                 | 4    | 7B    | **HISTORICAL**| `docs/product/LAUNCHER_FINAL_AUDIT.md` (note: name collision with 7E's `LAUNCHER_FINAL.md` — see DEAD_CODE.md §10) |
| `launcher-merge/`                 | 5    | 7B.1  | **HISTORICAL**| `docs/product/LAUNCHER_VISUAL_MERGE.md`                    |
| `launcher-7e/`                    | 5    | 7E    | **ACTIVE** ⭐ | `infra/scripts/capture/capture_launcher_7e.py` + `docs/product/LAUNCHER_FINAL.md` (the **live** launcher contract) |

⭐ = canonical launcher captures the live surface
references.

---

## Extension capture folders

| Folder           | PNGs | Phase | Status        | Reference                                                  |
|------------------|------|-------|---------------|------------------------------------------------------------|
| `extension-v2/`  | 5    | 6C    | **ACTIVE**    | `apps/admin/web/app/extension/page.tsx` (popup gallery)    |
| `extension-7a/`  | 7    | 7A    | **ACTIVE** ⭐ | `apps/extension/ui/capture_extension.mjs` + `docs/engineering/PHASE_7A_STATUS.md` |

---

## Demo + alpha folders

| Folder      | PNGs | Phase | Status        | Reference                                                       |
|-------------|------|-------|---------------|-----------------------------------------------------------------|
| `demo/`     | 4    | 6D    | **ACTIVE**    | `apps/web/app/components/Screens.tsx` + `docs/product/FIRST_MAGIC.md` |
| `alpha/`    | 3    | —     | **ACTIVE**    | `infra/scripts/capture/capture_alpha.py` + `docs/founder/PUBLIC_ALPHA.md` |

---

## Root-level flat PNGs

These predate the subfolder pattern (Phase 6B introduced
per-phase folders). Some are still consumed by the
public web gallery; others are orphans from earlier
experiments.

| File                              | Status        | Reference                                                       |
|-----------------------------------|---------------|-----------------------------------------------------------------|
| `extension-connected.png`         | **ACTIVE**    | `apps/extension/ui/capture_extension.mjs` (rerun output)        |
| `extension-empty.png`             | **ACTIVE**    | Capture harness + `apps/admin/web/app/screenshots/page.tsx`     |
| `extension-capturing.png`         | **ACTIVE**    | Capture harness                                                 |
| `extension-missing.png`           | **ACTIVE**    | Capture harness                                                 |
| `extension-disconnected.png`      | **ACTIVE**    | Capture harness                                                 |
| `extension-offline.png`           | **ACTIVE**    | Capture harness                                                 |
| `extension-loading.png`           | **ACTIVE**    | Capture harness                                                 |
| `launcher-digest.png`             | **ACTIVE**    | `apps/web/app/components/Screens.tsx` (web gallery hero)        |
| `launcher-empty.png`              | **ACTIVE**    | `apps/web/app/components/Screens.tsx`                           |
| `launcher-first-week.png`         | **ORPHAN**    | None found (stale 2026-05-22)                                   |
| `launcher-loading.png`            | **ORPHAN**    | None found (stale 2026-05-22)                                   |
| `launcher-offline.png`            | **ORPHAN**    | None found (stale 2026-05-22)                                   |
| `recovery-card.png`               | **ACTIVE**    | Part of launcher-v2 bucket expectations                          |
| `recovery-card-focused.png`       | **ACTIVE**    | Part of launcher-v2 bucket expectations                          |
| `control-room.png`                | **ORPHAN**    | None found (stale 2026-05-21)                                   |
| `doctor-output.png`               | **ORPHAN**    | None found (stale 2026-05-21)                                   |
| `installer-flow.png`              | **ORPHAN**    | None found (stale 2026-05-21)                                   |
| `settings-dialog.png`             | **ORPHAN**    | None found (stale 2026-05-21)                                   |

---

## Summary

| Status      | Folder count | Root PNG count |
|-------------|--------------|----------------|
| ACTIVE      | 5 folders + 1 ⭐ launcher + 1 ⭐ extension | 10 |
| HISTORICAL  | 11 folders   | 0              |
| ORPHAN      | 0 folders    | 7              |

---

## Recommendations (NOT actioned in 8A)

**Delete candidates** — 7 root-level orphan PNGs with no
consumer + a stale modification timestamp (>3 days old as
of audit):

```
assets/screenshots/control-room.png
assets/screenshots/doctor-output.png
assets/screenshots/installer-flow.png
assets/screenshots/settings-dialog.png
assets/screenshots/launcher-first-week.png
assets/screenshots/launcher-loading.png
assets/screenshots/launcher-offline.png
```

**Keep but flag** — 11 historical launcher folders are
each ~1-3 MB on disk; total ~25 MB. They serve as the
audit-trail for the launcher's 6I → 7E journey. They
*could* be archived into a single `assets/screenshots/_history.zip`
if disk pressure ever becomes a concern. Today: keep
unchanged.

**Phase 8A does NOT delete anything.** This document
classifies; a future 8B may execute the deletes after
re-verifying each row's "no consumer" claim with fresh
grep evidence.
