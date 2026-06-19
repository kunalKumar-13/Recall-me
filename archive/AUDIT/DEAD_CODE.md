# Dead Code Audit — Phase 8A

Evidence-based catalogue of dead, duplicate, and orphan
code. **No deletions performed.** This is the
*classification* document; deletion happens (if at all) in
a later phase after each row's verification step is run.

> Status legend: **DEAD** = no live import path · **DUPLICATE**
> = two implementations of the same concept · **ORPHAN** =
> referenced from no consumer · **LEGACY** = behind an
> explicit escape hatch (kept on purpose) · **VERIFIED LIVE**
> = grep found a real consumer.

Pyflakes baseline: `python -m pyflakes app/ api/` runs
clean (zero output). The catalogue below is about
*semantic* dead code, not syntactic warnings.

---

## 1. Parallel launcher trees

| File                                              | Status        | Verification (`grep`)                                            |
|---------------------------------------------------|---------------|------------------------------------------------------------------|
| [`app/ui/launcher.py`](../../app/ui/launcher.py)     | **LIVE**      | Adapter; imported by `app/main.py:from app.ui.launcher import Launcher` |
| [`app/ui/launcher_legacy.py`](../../app/ui/launcher_legacy.py) | **LEGACY** | Imported only by the adapter when `RECALL_LAUNCHER=legacy` |
| [`app/ui/launcher_v3/live.py`](../../app/ui/launcher_v3/live.py) | **LIVE** | Default; `Launcher = LiveLauncher` in the adapter |
| `app/ui/launcher_anims.py`                        | **LIVE**      | Imported by launcher_legacy.py (digest stagger reveal) |
| `app/ui/launcher_digest.py`                       | **LIVE**      | Imported by launcher_legacy.py (`digest_labels` + caps) |
| `app/ui/cards.py`                                 | **LEGACY**    | Imported only by `launcher_legacy.py` — contains `RecoveryCard`, `InvestigationCard`, `derive_recovery_confidence` |
| `app/ui/widgets.py`                               | **LEGACY**    | Imported only by `launcher_legacy.py` — `PreviewPane`, `DigestRow`, `EpisodicCard`, `ResultItemWidget`, etc. |
| `app/ui/styles.py`                                | **LEGACY**    | Imported only by `launcher_legacy.py` for `LAUNCHER_QSS` |

**Finding.** The legacy launcher tree is a real code path
(via `RECALL_LAUNCHER=legacy`) — it isn't dead. But ~7 of
the 11 `app/ui/*.py` files are reachable *only* through
that env-var escape hatch.

---

## 2. Duplicate widgets

| Pair                                              | Locations                                                       | Use case                              |
|---------------------------------------------------|-----------------------------------------------------------------|---------------------------------------|
| `RecoveryCard` vs `RecoveryCardV3`                | `app/ui/cards.py:640` vs `app/ui/launcher_v3/recovery_panel.py` | Legacy vs v3. Mutually exclusive.    |
| `InvestigationCard` vs `InvestigationCardV3`      | `app/ui/cards.py:755` vs `app/ui/launcher_v3/investigation_panel.py` | Legacy vs v3.                  |
| `DigestRow` vs `MinimalDigest`                    | `app/ui/widgets.py` vs `app/ui/launcher_v3/minimal.py`          | Legacy row vs v3 digest.             |
| `TrustSurface` (ext v1) vs `TrustRow` (launcher v3) | `apps/extension/ui/src/components/TrustSurface.tsx` vs `app/ui/launcher_v3/minimal.py:TrustRow` | Different platforms — both LIVE on their own surface; not actually duplicates |

**Finding.** True duplicates exist inside `app/ui/`
(legacy vs v3 cards). They are not *dead* — both are
reachable — but they're concept-duplicates: same widget
shape rendered twice for two launcher variants.

---

## 3. Confidence-derivation logic

| Location                                          | Pattern                                                          | Used where                             |
|---------------------------------------------------|------------------------------------------------------------------|----------------------------------------|
| `app/ui/cards.py:566` (`derive_recovery_confidence`) | `n_targets ≥ 4 → high · 2-3 → medium · 0-1 → low`              | Legacy launcher (cards.py:1656)        |
| `app/ui/launcher_v3/recovery_panel.py:154` (`_confidence_pill`) | accepts `signal: Signal` literal — caller computes the band  | v3 launcher                            |
| `apps/extension/ui/src/lib/api.ts` (commented)    | reference comment only — no implementation                       | extension popup (relies on engine value) |

**Finding.** Two implementations of the same band rule,
in two surfaces. The 6Q `PROMOTION_THRESHOLDS.md` doc
codifies the rule in prose; neither implementation
imports the other. **DUPLICATE** — same logic in two
places, with the v3 path doing nothing inside the widget
(the caller in `live.py` computes the band).

---

## 4. Resume / restore flows

| Implementation                                    | File / line                                                      | Status        |
|---------------------------------------------------|------------------------------------------------------------------|---------------|
| `_on_recovery_restore`                            | `app/ui/launcher_legacy.py:1704`                                 | **LEGACY**    |
| `_on_preview_accept`                              | `app/ui/launcher_v3/live.py:_on_preview_accept`                  | **LIVE**      |
| Stub `_on_restore` (one-line API call, dropped target list) | archived in `archive/resume-old/README.md`              | **ARCHIVE**   |

Both live implementations call
`api_client.recovery_restore(candidate_id)`. They walk the
same `RestorationPlan`. Different signal names, identical
behaviour.

**Finding.** Two implementations of *walk the plan, open
each target*. Both real. Both correct.

---

## 5. Search dispatch

| Component                                         | File                                                              | Status        |
|---------------------------------------------------|-------------------------------------------------------------------|---------------|
| `_SearchWorker` (Qt thread)                       | `app/ui/launcher_legacy.py:240–316`                              | **LEGACY**    |
| `_request_search` signal                          | both `launcher_legacy.py` + `launcher_v3/live.py`                | **LIVE**      |
| `query_changed` / `searchChanged`                 | `app/ui/launcher_v3/minimal.py` (Phase 7E.1 frozen contract)     | **LIVE**      |
| Inline-search results in v3                       | **MISSING** — no consumer renders results when `_request_search` fires | **TODO**  |

**Finding.** The v3 launcher emits `_request_search(query)`
but no v3 component listens. The legacy launcher consumes
the same signal via `_SearchWorker`. Today the v3
launcher's search field is decorative — typing fires
signals into the void. Documented in
[`SURFACES.md`](SURFACES.md) as *LIVE-but-incomplete*.

---

## 6. Orphan API routes

Routes in [`api/main.py`](../../api/main.py) with no live
consumer found via repo-wide grep:

| Route                                            | Handler                       | Status   |
|--------------------------------------------------|-------------------------------|----------|
| `POST /v1/threads/{id}/forget`                    | `thread_forget`               | **ORPHAN** |
| `GET /v1/contexts/recent`                        | `recent_contexts`             | **ORPHAN** |
| `GET /v1/sessions/recent`                        | `recent_sessions`             | **ORPHAN** |
| `POST /v1/threads/cache/clear` (evolution)       | `threads_clear_evolution_cache` | **ORPHAN** (settings.py docstring mentions but doesn't call) |
| `POST /v1/replay/day`                             | `replay_day`                  | **ORPHAN** |
| `POST /v1/loop/bump`                              | `loop_bump`                   | **LIVE** (called inside `api/main.py:_post_ingest_hook` via `daily_loop.mark_event`) |
| `GET /v1/loop/summary`                            | `loop_summary`                | **LIVE** (consumed by `apps/admin/web/lib/loaders/daily.ts`) |
| `POST /v1/demo/{state,activate,dismiss}`          | demo_state / activate / dismiss | **LIVE** (extension popup polls demo state) |

**Finding.** 5 routes have zero callers anywhere in the
repo. They are safe to keep (the cost is small) but they
add API surface area that could be trimmed.

Note: `GET /v1/events/recent` is **LIVE** — both the
extension's `fetchMemory` and the legacy launcher's
digest call it. The agent's earlier classification of
this as orphan was wrong (the extension call is in
`apps/extension/ui/src/lib/api.ts`).

---

## 7. Unused imports

`python -m pyflakes app/ api/` runs **clean** on the current
tree. No syntactic dead code.

The TypeScript builds for the three apps (`apps/extension/ui`,
`apps/admin/web`, `apps/web`) all run `tsc --noEmit` cleanly.

---

## 8. Dead helpers in `app/core/`

| Module                                            | Status        | Consumer                              |
|---------------------------------------------------|---------------|---------------------------------------|
| `demo_data.py`                                    | **LEGACY**    | Imported by `launcher_legacy.py` + `app/main.py` (for `RECALL_DEMO=1`) |
| `demo_seed.py`                                    | **LIVE**      | `_smoke_api.py` + `app/main.py`       |
| `ceremonies.py`                                   | **LEGACY**    | Imported only by `launcher_legacy.py` |
| `demo_mode.py`                                    | **LIVE**      | API routes + both launchers           |

**Finding.** `ceremonies.py` and `demo_data.py` are
legacy-only — they live behind the same env-var escape
hatch as the legacy launcher. Not dead, but coupled to
the legacy path.

---

## 9. Pre-7A extension components

The extension popup at [`apps/extension/ui/src/App.tsx`](../../apps/extension/ui/src/App.tsx)
composes the new `v2/` component tree. Files outside
`v2/` are no longer rendered:

| File                                              | Status        | Notes                                  |
|---------------------------------------------------|---------------|----------------------------------------|
| `apps/extension/ui/src/components/ContinueCard.tsx` | **DEAD**    | Not imported by current App.tsx        |
| `apps/extension/ui/src/components/InvestigationCard.tsx` | **DEAD** | Not imported                          |
| `apps/extension/ui/src/components/MemoryList.tsx` | **DEAD**      | Not imported                           |
| `apps/extension/ui/src/components/Section.tsx`    | **DEAD**      | Not imported                           |
| `apps/extension/ui/src/components/TrustSurface.tsx` | **DEAD**    | Not imported                           |
| `apps/extension/ui/src/components/DebugStrip.tsx` | **DEAD**      | Not imported                           |
| `apps/extension/ui/src/components/DemoBanner.tsx` | **DEAD**      | Not imported (App.tsx has its own inline banner) |
| `apps/extension/ui/src/components/states.tsx`     | **DEAD**      | Replaced by `v2/States.tsx`            |
| `apps/extension/ui/src/components/icons.tsx`      | **LIVE**      | Imported by `v2/Header.tsx` + `v2/SearchOverlay.tsx` + `SettingsPanel.tsx` |
| `apps/extension/ui/src/components/SettingsPanel.tsx` | **LIVE**   | Imported by `App.tsx` for the settings view |

**Finding.** 8 of 10 components in
`apps/extension/ui/src/components/` are unreferenced
after 7A. They are still TypeScript-clean and shipped in
the bundle (tsc compiles them, vite tree-shakes them out
of the final JS — confirmed via the 293 KB bundle size
holding flat from 6D through 7A).

---

## 10. Capture scripts under `infra/scripts/capture/`

| Script                                            | Phase         | Status        |
|---------------------------------------------------|---------------|---------------|
| `capture_launcher_7e.py`                          | 7E            | **LIVE**      |
| `capture_launcher_merge.py`                       | 7B.1          | **HISTORICAL** — last run produced canonical phase captures, not re-run on changes |
| `capture_launcher_ship.py`                        | 7B            | **HISTORICAL** |
| `capture_launcher_final.py`                       | 7B            | **HISTORICAL** (note name collision with `LAUNCHER_FINAL.md` from 7E — `_final.py` is *7B*, `_7e.py` is *7E*) |
| `capture_launcher_truth.py`                       | 6Q            | **HISTORICAL** |
| `capture_launcher_visible.py`                     | 6P.1          | **HISTORICAL** |
| `capture_launcher_reset.py`                       | 6O            | **HISTORICAL** |
| `capture_launcher_recovery.py`                    | 6N            | **HISTORICAL** (also duplicated in `archive/launcher-overbuild/`) |
| `capture_launcher_compact.py`                     | 6M.2          | **HISTORICAL** (also duplicated in `archive/launcher-overbuild/`) |
| `capture_launcher_refined.py`                     | 6M.1          | **HISTORICAL** |
| `capture_alpha.py`                                | —             | **LIVE**      |
| `capture_extension.mjs` (in `apps/extension/ui/`) | grows per phase | **LIVE**    |

**Finding.** 9 historical capture scripts live in
`infra/scripts/capture/`. Each produced its phase's
PNGs in `assets/screenshots/launcher-*/`. None of them
ship; they exist for re-generation on demand. Two
duplicates exist between `infra/scripts/capture/` and
`archive/launcher-overbuild/` (the 6M.2 / 6N scripts).

---

## 11. Stale TODOs / hints

| Path                                            | Line                                          | Notes                              |
|-------------------------------------------------|-----------------------------------------------|------------------------------------|
| `apps/extension/ui/src/App.tsx`                 | comment refs to legacy `_search_panel` patterns | superseded by `SearchOverlay`     |
| `app/ui/launcher_v3/live.py`                    | `Phase 6K wires the typing path…`             | Comment notes v3 search-panel is built but not wired |

No code changes needed; just notes that the audit
surfaced.

---

## Summary

| Category                            | Count |
|-------------------------------------|-------|
| Truly DEAD (no consumer)            | 8 (pre-7A extension components) |
| LEGACY (behind escape hatch)        | 7 (legacy `app/ui/*.py` files) |
| DUPLICATE (same concept twice)      | 3 widget pairs, 1 confidence-logic pair |
| ORPHAN routes (no caller)           | 5                                |
| HISTORICAL scripts (kept for re-run) | 9 + 2 duplicates                |

**Recommended grace period:** All the above stays until
8B. Phase 8 is *audit*, not *deletion*. Each row above
should be re-verified by the next contributor with a
fresh grep before any rm.
