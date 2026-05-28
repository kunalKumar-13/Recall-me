# Repo Stabilization — Phase 10C

**Status:** report only. No code changes. No
commits.

**Date:** 2026-05-27.
**Scope:** clean project — audit branches,
stale screenshots, archive references, dead
imports, duplicate docs. No features, no UI, no
landing, no extension.

This is a survey + classification doc. Every
recommendation is *do not act yet* — the cleanup
itself will land in a follow-up directive.

---

## 1. Branches

```
git branch -a
  main
* release/v0.1.0-rc1
  remotes/origin/main
  remotes/origin/release/v0.1.0-rc1
```

| Branch                          | Last commit                                                 | Vs `main` (ahead / behind) | Classification |
|---------------------------------|-------------------------------------------------------------|----------------------------|----------------|
| `main`                          | `2093933` · 2026-05-26 · *docs(demo): add showcase flow*    | —                          | **KEEP** (baseline)         |
| `release/v0.1.0-rc1` *(active)* | `ddb5bb4` · 2026-05-27 · *feat(launcher): phase 10b — DarkLauncher live migration* | 4 ahead / 0 behind         | **KEEP** (active development) |
| `origin/main`                   | `2093933` · 2026-05-26                                       | 0 / 0 vs `main`            | **KEEP** (remote of `main`) |
| `origin/release/v0.1.0-rc1`     | `14969d7` · 2026-05-27 · *docs(launcher): phase 10a registration* | local is 1 ahead / 0 behind | **KEEP** (remote of release branch) |

Tags:

| Tag           | Classification |
|---------------|----------------|
| `v0.2-alpha`  | **KEEP** (historical preview release marker; unchanged from Phase 5 stable) |

**No DELETE / ARCHIVE branches identified.** Both
local branches are active. The release branch is
the live development frontier; `main` is the
stable baseline that release will merge back into
when v0.1.0 ships.

---

## 2. Stale screenshots

### Current capture surface (`assets/screenshots/`)

| Directory                  | Files | Status                                         |
|----------------------------|-------|------------------------------------------------|
| `alpha/`                   | 3     | LIVE — referenced by `SCREEN_INDEX.md`, marketing site |
| `demo/`                    | 4     | LIVE — referenced by marketing `Screens.tsx` + `Story.tsx` |
| `extension-7a/`            | 7     | LIVE — Phase 7A frozen set                     |
| `launcher-7e/`             | 5     | **STALE** — pre-Phase 10 launcher (warm paper, 720×460). Not referenced by anything live. |
| `launcher-final/`          | 4     | LIVE — Phase 10A design-conformance captures (bare `DarkLauncher`) |
| `launcher-live-final/`     | 4     | LIVE — Phase 10B production captures (via `Launcher()`) |
| `README.md`                | —     | LIVE                                           |

**27 capture files across 6 directories.**

### Drift in `apps/web/public/screens/` (marketing site)

The Phase 6G landing page references screenshots
that *predate* the Phase 7E launcher and Phase 7A
extension freezes:

| Reference (live in `apps/web/`)                              | Source dir status                                  |
|--------------------------------------------------------------|----------------------------------------------------|
| `Screens.tsx:30` → `/screens/launcher/launcher-digest.png`   | **STALE** — pre-7E launcher visuals                |
| `Screens.tsx:48` → `/screens/launcher/launcher-empty.png`    | **STALE** — pre-7E launcher visuals                |
| `Screens.tsx:36` → `/screens/extension/extension-home.png`   | **STALE** — pre-7A extension visuals               |
| `Story.tsx:44`   → `/screens/extension/extension-recovery.png`| **STALE** — pre-7A extension visuals               |
| `Story.tsx:56`   → `/screens/demo/demo-launcher.png`         | LIVE — current 8D capture                          |
| `Story.tsx:68`   → `/screens/extension/extension-home.png`   | **STALE** — duplicate of Screens.tsx:36            |
| `Screens.tsx:42` → `/screens/demo/demo-extension.png`        | LIVE — current 8D capture                          |

(Already flagged in
[`release/LANDING_CHECK.md`](../release/LANDING_CHECK.md)
as a content-fill follow-up at the 8D close. Nothing
in 10C changes that — surfacing it again here so
the stabilization sweep has the full picture.)

### Drift in `apps/admin/web/public/screens/`

The Phase 6J control room mirrored 25 capture
folders into `apps/admin/web/public/screens/`
during C5.c. Many of those mirrors point at
folders that **no longer exist** in
`assets/screenshots/`:

| Mirror at `apps/admin/web/public/screens/`     | Source folder in `assets/screenshots/`     |
|-----------------------------------------------|--------------------------------------------|
| `launcher-v2/` (7 files)                       | **MOVED** to `archive/screenshots-history-rc/launcher-v2/` |
| `launcher-v3/` (5 files)                       | **MOVED** to `archive/screenshots-history-rc/launcher-v3/` |
| `extension-v2/` (5 files)                      | **MOVED** to `archive/screenshots-history-rc/extension-v2/` |
| `alpha/`, `demo/`                              | LIVE (unchanged)                            |

Admin code that consumes these mirrors:

```
apps/admin/web/lib/loaders/screenshots.ts:34       launcher-v2 bucket
apps/admin/web/lib/loaders/screenshots.ts:40       launcher-v3 bucket
apps/admin/web/lib/loaders/screenshots.ts:44       extension-v2 bucket
apps/admin/web/app/launcher/page.tsx:25            launcher-v3 dir read
apps/admin/web/app/launcher/page.tsx:26            launcher-v2 dir read
apps/admin/web/app/extension/page.tsx:30           extension-v2 dir read
apps/admin/web/app/screenshots/page.tsx:9-14       launcher-v2 / launcher-v3 / extension-v2 docstring
apps/admin/web/components/ActionsBar.tsx:37        /screens/launcher/launcher-digest.png (pre-7E)
```

The admin web renders these surfaces *correctly*
right now because the public-folder copies were
checked in during C5.c. But the assets/
directory + the admin's public/ directory are
now **divergent sources of truth.**

**Total stale captures (unreferenced or pointing
at archived sources):** 5 dirs + 7 root-level web
references = **≈12 distinct stale paths**.

---

## 3. Archive files still referenced

### Python `import archive.*` count

```
grep -rn "from archive\.\|import archive\." --include='*.py' .
→ 0 matches
```

**Zero.** No live Python code imports anything
under `archive/`. The earlier BUG-001 incident
(Phase 8B restoring `demo_data.py` /
`styles.py` / `widgets.py` / `cards.py` from
archive) is fully resolved — the live copies are
in `app/core/` and `app/ui/`, not under
`archive/`.

### Doc references to archive paths

Documentation files mention archive paths for
historical context. These are *intentional* —
they document where things moved. 25 docs match
the regex; all 25 are status / freeze / audit /
delete-plan files, none are runtime artifacts.

Sampling:

```
docs/engineering/LAUNCHER_MIGRATION.md          archive/launcher-pre10a/ (forward-looking)
AUDIT/LAUNCHER_FREEZE.md                        archive/launcher-old/   (8B history)
AUDIT/DELETE_PLAN.md                            various                 (8B per-row delete log)
docs/founder/PHASE_TRACKER.md                   various                 (cumulative tracker)
alpha/failures/2026-05-24-launcher-imported-demo-data.md   archive/launcher-old/ (BUG-001 postmortem)
```

**Verdict:** documentation references to
archive paths are *correct* and should NOT be
cleaned up. They are the historical trail.

### Code comments mentioning archive paths

```
app/ui/launcher_v3/recovery_panel.py  (pre-10B file, now dead)
app/ui/launcher_v3/minimal.py         (pre-10B file, now dead)
app/ui/launcher_v3/investigation_panel.py (pre-10B file, now dead)
app/ui/launcher.py                    (adapter; comment points at archive/launcher-old/)
```

The `app/ui/launcher.py` adapter's comment is
correct; the three `launcher_v3/*.py` files are
themselves dead-after-10B (see Task 4 below).

---

## 4. Dead imports

### Pre-10B paint cluster inside `app/ui/launcher_v3/`

After commit `ddb5bb4` (Phase 10B), the live
launcher entry point (`live.py`) imports from
exactly one module: `darkframe.py`. The pre-10B
paint cluster is unreferenced from any live code:

| File                                            | Imported by live code? | LOC  | Verdict             |
|-------------------------------------------------|------------------------|------|---------------------|
| `minimal.py`                                    | **no** (only `__init__.py`) | 540  | **DEAD** — archive |
| `search_panel.py`                               | **no** (only `__init__.py`) | 134  | **DEAD** — archive |
| `recovery_panel.py`                             | **no** (only `__init__.py`) | 364  | **DEAD** — archive |
| `recent_memory.py`                              | **no** (only `__init__.py`) | 154  | **DEAD** — archive |
| `investigation_panel.py`                        | **no** (only `__init__.py`) | 206  | **DEAD** — archive |
| `resume_preview.py`                             | **no** (only `__init__.py`) | 284  | **DEAD** — archive |
| `restore_toast.py`                              | **no** (only `__init__.py`) | 150  | **DEAD** — archive |
| `surfaces.py`                                   | (imported by the other dead modules) | 309  | **DEAD** — archive |
| `trust_panel.py`                                | **no** (only `__init__.py`) | 99   | **DEAD** — archive |
| `motion.py`                                     | YES — `darkframe.py` (indirect)  | 109  | LIVE                |
| `theme.py`                                      | YES — `darkframe.py`              | 241  | LIVE                |
| `darkframe.py`                                  | YES — `live.py`                    | 1987 | LIVE (Phase 10A/B)  |
| `live.py`                                       | YES — `app/ui/launcher.py`         | 708  | LIVE (Phase 10B)    |
| `__init__.py`                                   | YES (package init)                 | ~110 | LIVE                |

**9 dead files inside the launcher tree
totalling 2,240 LOC.** Already enumerated in
[`docs/engineering/LAUNCHER_MIGRATION.md`](../docs/engineering/LAUNCHER_MIGRATION.md)
as the Phase 10C archive target. They cross-import
each other but nothing outside the cluster
touches them except `__init__.py`.

### Outside the launcher tree

| File                       | Status |
|----------------------------|--------|
| `app/ui/widgets.py`        | **DEAD** — zero importers (was restored during 8C BUG-001 fix as a safety net; never proven necessary)  |
| `app/ui/cards.py`          | **DEAD** — zero importers (same)                                                                          |
| `app/ui/styles.py`         | LIVE — imported by `onboarding.py` + `settings.py`                                                       |
| `app/ui/onboarding.py`     | LIVE — imported by `app/main.py:69`                                                                       |
| `app/ui/settings.py`       | LIVE — imported by `app/main.py:70`                                                                       |
| `app/ui/hotkey.py`         | LIVE — imported by `app/main.py:67`                                                                       |
| `app/ui/launcher.py`       | LIVE — public adapter; imported by `app/main.py`                                                          |

`widgets.py` + `cards.py` were flagged as
restorations during 8C but the BUG-001
postmortem showed they aren't actually imported
by any live code. Confirming here again: zero
importers. Safe to archive.

### Total dead-Python tally

| Category                                              | Files | LOC   |
|-------------------------------------------------------|-------|-------|
| `app/ui/launcher_v3/` pre-10B paint cluster           | 9     | 2,240 |
| `app/ui/widgets.py`                                   | 1     | ~2,470 |
| `app/ui/cards.py`                                     | 1     | ~970  |
| **Total**                                             | **11**| **≈5,680** |

(Per-file LOC for `widgets.py` and `cards.py`
sourced from the 8B `DELETE_PLAN.md` archive
log; they were restored from archive at the same
LOC.)

---

## 5. Duplicate docs

### Direct duplicates / near-duplicates

| Cluster                      | Members                                                            | Verdict                                            |
|------------------------------|--------------------------------------------------------------------|----------------------------------------------------|
| **Root CHANGELOG**           | `/CHANGELOG.md` (3-line stub redirecting to docs/release/CHANGELOG.md) + `docs/release/CHANGELOG.md` (canonical, 1300+ lines) + `release/CHANGELOG_RC1.md` (RC1-specific user-facing notes) | **NOT duplicate** — three distinct roles. Root is intentional thin pointer per "Repo Stabilization Pass." Keep all three. |
| **INSTALL guides**           | `/INSTALL_VERIFIED.md` (8D dev walk record) + `release/INSTALL.md` (RC1 user install) + `docs/release/INSTALL.md` (~76 LOC; older version) + `alpha/INSTALL.md` (cohort install) + `alpha/pack/INSTALL.md` (cohort install v2) | **Partial duplicates.** `docs/release/INSTALL.md` is superseded by `release/INSTALL.md`. `alpha/INSTALL.md` is superseded by `alpha/pack/INSTALL.md`. Recommend deprecation notice on the two older copies. |
| **FEEDBACK**                 | `alpha/FEEDBACK.md` (133 LOC, pre-8E) + `alpha/pack/FEEDBACK.md` (97 LOC, 8E) + `apps/admin/FEEDBACK.md` (admin-team feedback) | **Partial duplicates.** `alpha/FEEDBACK.md` is superseded by `alpha/pack/FEEDBACK.md`. Recommend deprecating the older copy. |
| **LAUNCHER product docs**    | 9 docs under `docs/product/LAUNCHER_*.md`: CONTRACTS, FINAL, FINAL_AUDIT, REGRESSION, RESET, REVIEW, SHIP_AUDIT, VISIBILITY, VISUAL_MERGE | **NOT duplicate.** Each documents a specific Phase 6 / 7 launcher generation; together they form the historical chain. The Phase 10A amendment lives on CONTRACTS.md. Keep all 9. |
| **Install-size audits**      | `docs/engineering/INSTALL_REDUCTION_REPORT.md` + `INSTALL_SIZE_AUDIT.md` + `INSTALL_SIZE_AUDIT_V2.md` + `docs/release/INSTALL_METRICS.md` | **Possible consolidation candidates.** Four files cover overlapping installer-size territory across phases. Not strictly duplicate. Worth a docs-team pass when someone has 30 min. |
| **Install validation**       | `docs/trust/INSTALL_PROOF_WINDOWS.md` + `INSTALL_VALIFICATION_WINDOWS.md` (sic) | **NOT duplicate.** PROOF is the cohort proof artefact; VALIDATION is the engineering validation script output. Different audiences, kept. |
| **Phase status docs**        | 35 files under `docs/engineering/PHASE_*_STATUS.md` (6A through 10B) | **NOT duplicate.** One per phase; this is the historical record. Keep all. |
| **Alpha runbook + journals** | `alpha/ALPHA_001_RUNBOOK.md` + `alpha/ALPHA_FEEDBACK_V2.md` + `alpha/FIRST_72_HOURS.md` + `alpha/SAMPLE_WORKFLOW.md` + `docs/founder/ALPHA_USERS.md` + `docs/trust/ALPHA_MATRIX.md` | **NOT duplicate.** Each addresses a distinct cohort artefact. Keep all. |
| **Demo docs**                | `/DEMO_MODE.md` (CLI reference) + `release/DEMO_FLOW.md` (3-min screen-share script) + `docs/release/DEMO_VIDEO_SCRIPT.md` | **NOT duplicate.** Three different audiences (operator / pitchman / video producer). Keep all. |
| **README**                   | 10 README.md files spread across `alpha/`, `apps/admin/`, `apps/desktop/`, `apps/docs/`, `apps/extension/`, `apps/web/`, `assets/branding/`, `alpha/failures/`, `alpha/users/`, `alpha/wow/` | **NOT duplicate.** Each scopes a subdirectory. Keep all. |

**Direct duplicates flagged: 3 clusters with
older copies that can be deprecated**
(`docs/release/INSTALL.md`, `alpha/INSTALL.md`,
`alpha/FEEDBACK.md`).

---

## 6. Action queue (do NOT act yet)

Ordered by safest-first.

| # | Action                                                                          | Risk    | LOC impact                  | Blocking?         |
|---|---------------------------------------------------------------------------------|---------|------------------------------|--------------------|
| 1 | Archive 9 dead `launcher_v3/*` paint modules to `archive/launcher-pre10a/` + update `app/ui/launcher_v3/__init__.py` to drop the dead re-exports | low     | -2,240 LOC out of live tree | unblocks 10C cleanup commit |
| 2 | Archive `app/ui/widgets.py` + `app/ui/cards.py`                                 | low     | -3,440 LOC                   | follows #1         |
| 3 | Sync `apps/admin/web/public/screens/` mirrors with the live `assets/screenshots/` set | low-med | refresh + remove archived dirs from public/ | needs landing-page update first |
| 4 | Update `apps/admin/web/lib/loaders/screenshots.ts` + `apps/admin/web/app/{launcher,extension}/page.tsx` to point at `launcher-final` / `extension-7a` instead of `launcher-v3` / `extension-v2` | med     | small TS edits               | independent        |
| 5 | Refresh `apps/web/app/components/Screens.tsx` + `Story.tsx` to use Phase 10 captures + 7A extension shots | med     | small TSX edits + asset moves | landing follow-up |
| 6 | Deprecate `docs/release/INSTALL.md` (point at `release/INSTALL.md`) | low | -76 LOC | independent |
| 7 | Deprecate `alpha/INSTALL.md` + `alpha/FEEDBACK.md` (point at `alpha/pack/*`) | low | -250 LOC | independent |
| 8 | Archive `assets/screenshots/launcher-7e/` (Phase 9 historical capture set) once Phase 10 captures fully replace it | low | -5 PNGs | follows #1 |
| 9 | Pass over `INSTALL_REDUCTION_REPORT.md` / `INSTALL_SIZE_AUDIT*.md` cluster to see if they want consolidation | low | docs-only | not blocking |

**Net potential cleanup:** ≈6,000 LOC of dead
Python + ≈350 LOC of stale docs + ≈17 archived-or-
deprecated PNG references.

**Nothing in this list ships in 10C itself.**
This document is the audit; each row needs its
own scoped directive to act.

---

## 7. Verification (audit-only)

| Check                                                              | Source                                                               |
|--------------------------------------------------------------------|----------------------------------------------------------------------|
| `grep "from archive\.\|import archive\." --include='*.py'`         | 0 matches → no live Python imports archive code                       |
| `grep "from app\.ui\.widgets\|from app\.ui\.cards" --include='*.py'`| 0 matches → widgets.py + cards.py are dead                            |
| `grep "from app\.ui\.launcher_v3\." --include='*.py'` outside `launcher_v3/` | only `live.py` ↔ `darkframe.py` chain alive                          |
| `from app.ui.launcher import Launcher` resolves                    | ✅ → `LiveLauncher` 760×520                                           |
| `from app.main import main`                                        | ✅ clean import                                                       |
| `git branch -a` returns expected 2 local + 2 remote                | ✅                                                                    |

---

## What this audit is NOT

- **Not a cleanup commit.** No files are moved,
  no imports are deleted, no docs are merged.
  Every recommendation is a *future* action.
- **Not a freeze update.** The Phase 10A
  `LAUNCHER_FREEZE.md` and the Phase 10B
  `PHASE_10B_STATUS.md` stay authoritative.
- **Not engine work.** `app/core/*` is
  untouched and untested in this audit.
- **Not landing-page work.** The `apps/web/`
  drift is *flagged* (Task 2), not fixed.
- **Not extension work.** The
  `apps/extension/` capture script's references
  to `extension-v2/` are flagged (Task 2), not
  fixed.

---

## Next phase candidate

**Phase 10D — Cleanup execution.** Acts on
rows 1, 2, 6, 7, 8 from the action queue
above. Touches:

- `app/ui/launcher_v3/__init__.py` (drop dead re-exports)
- `archive/launcher-pre10a/` (new dir, receives 9 files)
- `archive/ui-pre10c/` (new dir, receives widgets.py + cards.py)
- `archive/screenshots-history-pre10c/launcher-7e/` (5 PNG move)
- `docs/release/INSTALL.md` (deprecation pointer)
- `alpha/INSTALL.md` + `alpha/FEEDBACK.md` (deprecation pointers)

Estimated: ≤300 LOC of edits + file moves, low
risk, single concern. Does NOT touch
`apps/admin/web/`, `apps/web/`, or
`apps/extension/`; those are Phase 10E
(landing/admin/extension sync).
