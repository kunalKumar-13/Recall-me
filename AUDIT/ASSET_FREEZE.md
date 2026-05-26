# Asset Freeze — Phase 8B

The frozen asset surface after the 8B cleanup.

> Source: [`ASSETS.md`](ASSETS.md) (Phase 8A
> classification).

---

## What stays under `assets/screenshots/`

19 folders + 11 root PNGs.

### Live launcher / extension folders (the canonical product captures)

| Folder              | Phase | Purpose                                           |
|---------------------|-------|---------------------------------------------------|
| `launcher-7e/`      | 7E    | **Current** launcher captures (5 PNGs)            |
| `extension-7a/`     | 7A    | **Current** extension popup captures (7 PNGs)     |

### Active reference folders (consumed by web/admin/extension)

| Folder              | Phase | Consumer                                                       |
|---------------------|-------|----------------------------------------------------------------|
| `launcher-v2/`      | 6B    | `apps/admin/web/app/launcher/page.tsx` (promotion baseline) + `apps/web/app/components/Screens.tsx` |
| `launcher-v3/`      | 6I    | `apps/admin/web/app/launcher/page.tsx` (v2↔v3 diff strip)     |
| `extension-v2/`     | 6C    | `apps/admin/web/app/extension/page.tsx` (popup gallery)        |
| `demo/`             | 6D    | `apps/web/app/components/Screens.tsx` + `docs/product/FIRST_MAGIC.md` |
| `alpha/`            | —     | `infra/scripts/capture/capture_alpha.py` + `docs/founder/PUBLIC_ALPHA.md` |

### Root-level flat PNGs (kept — referenced by capture harness or web gallery)

| File                              | Consumer                                                                 |
|-----------------------------------|--------------------------------------------------------------------------|
| `extension-connected.png`         | `apps/extension/ui/capture_extension.mjs`                                |
| `extension-empty.png`             | Capture harness + `apps/admin/web/app/screenshots/page.tsx`              |
| `extension-capturing.png`         | Capture harness                                                          |
| `extension-missing.png`           | Capture harness                                                          |
| `extension-disconnected.png`      | Capture harness                                                          |
| `extension-offline.png`           | Capture harness                                                          |
| `extension-loading.png`           | Capture harness                                                          |
| `launcher-digest.png`             | `apps/web/app/components/Screens.tsx` (web gallery hero)                |
| `launcher-empty.png`              | `apps/web/app/components/Screens.tsx`                                   |
| `recovery-card.png`               | Part of `launcher-v2/` bucket                                            |
| `recovery-card-focused.png`       | Part of `launcher-v2/` bucket                                            |

---

## What moved to `archive/screenshots-history/` (11 folders)

| Folder              | Phase  | Why archived                                              |
|---------------------|--------|-----------------------------------------------------------|
| `launcher-live/`    | 6K     | Historical exploratory captures                            |
| `launcher-minimal/` | 6L     | Pre-6O minimal-surface captures                            |
| `launcher-refined/` | 6M.1   | Pre-6O refinement captures                                 |
| `launcher-compact/` | 6M.2   | Geometry-recovery captures                                 |
| `launcher-recovery/`| 6N     | Recovery-precision captures                                |
| `launcher-reset/`   | 6O     | Reset captures (superseded by 7E)                          |
| `launcher-visible/` | 6P.1   | Visibility-recovery captures                               |
| `launcher-truth/`   | 6Q     | Continuity-truth captures                                  |
| `launcher-ship/`    | 6R     | Production-freeze captures (superseded by 7E)              |
| `launcher-final/`   | 7B     | Final-pass captures (superseded by 7E)                     |
| `launcher-merge/`   | 7B.1   | Visual-merge captures (superseded by 7E)                   |

Each folder is fully recoverable from `archive/`; none
are deleted.

---

## What was deleted (7 root PNGs)

| File                                          | Why deleted (no consumer found anywhere) |
|-----------------------------------------------|------------------------------------------|
| `assets/screenshots/control-room.png`         | Pre-6H mockup, stale 2026-05-21          |
| `assets/screenshots/doctor-output.png`        | Pre-6H mockup, stale 2026-05-21          |
| `assets/screenshots/installer-flow.png`       | Pre-6H mockup, stale 2026-05-21          |
| `assets/screenshots/settings-dialog.png`      | Pre-6H mockup, stale 2026-05-21          |
| `assets/screenshots/launcher-first-week.png`  | Pre-6O legacy, stale 2026-05-22          |
| `assets/screenshots/launcher-loading.png`     | Pre-6O legacy, stale 2026-05-22          |
| `assets/screenshots/launcher-offline.png`     | Pre-6O legacy, stale 2026-05-22          |

---

## Counts

| Metric                                  | Before 8B | After 8B | Delta |
|-----------------------------------------|-----------|----------|-------|
| Folders under `assets/screenshots/`     | 19        | 8        | -11   |
| Subfolders that are archived (`archive/screenshots-history/`) | 0 | 11 | +11 |
| Root-level PNGs                         | 18        | 11       | -7    |
| Total live PNGs                         | ~102      | ~47      | -55   |

The 55 PNGs removed from active asset tree are not
deleted — they live under `archive/screenshots-history/`
+ the 7 deleted-outright orphans that had zero consumer.

---

## Freeze rule

The new active asset surface is:

1. **2 ⭐ live capture folders** (`launcher-7e/` +
   `extension-7a/`) — the only ones a phase 9+ might
   regenerate.
2. **5 reference folders** consumed by the web /
   admin / extension surfaces.
3. **11 root PNGs** that are part of the capture
   harness's expected outputs.

Anything else added to `assets/screenshots/` requires:

- a consumer (a `apps/*/page.tsx`, `app/...`, or
  capture script that references the file by path), AND
- a row in `ASSETS.md` or a successor doc.

Phases that regenerate captures should write into the
existing folder (`launcher-7e/` / `extension-7a/`) — not
create a new `launcher-7f/` parallel folder. The launcher
contract is frozen; its captures live in one folder.
