# Launcher Migration Sheet — Phase 10A → 10B

**Scope:** planning only. **No implementation in
10A.** This sheet enumerates what moves from
`LiveLauncher` into the `DarkLauncher` slot, what
stays in `LiveLauncher` as engine glue, and what
gets deleted outright.

The target end-state: `LiveLauncher` is a thin
adapter that constructs a `DarkLauncher`,
populates it with engine fixtures
(`RecoveryProps` / `PreviewProps` /
`OtherWorkRow[]` / etc.) on refresh, and forwards
the host signals (`request_settings`, hotkeys,
restore plan execution) to the wrapped surface.

---

## Files in scope

```
app/ui/launcher.py                      — adapter (untouched)
app/ui/launcher_v3/
  __init__.py                           — public re-exports
  live.py             [ACTIVE, MIGRATE] — engine glue + composition
  darkframe.py        [ACTIVE]          — Phase 10A visual surface
  theme.py            [ACTIVE]          — Phase 10A tokens
  motion.py           [ACTIVE]          — 120 / 180 / 240 ms
  search_panel.py     [DEAD AFTER]      — superseded by darkframe.SearchBar
  minimal.py          [DEAD AFTER]      — superseded by darkframe.Frame + state widgets
  recovery_panel.py   [DEAD AFTER]      — superseded by darkframe.HeroRecovery
  recent_memory.py    [DEAD AFTER]      — superseded by darkframe.OtherRow
  investigation_panel.py [DEAD AFTER]   — superseded by darkframe.OtherRow + SearchResultRow
  resume_preview.py   [DEAD AFTER]      — superseded by darkframe.ResumeView (no longer an overlay)
  restore_toast.py    [DEAD AFTER]      — subsumed by darkframe.ResumeView (no separate toast)
  surfaces.py         [DEAD AFTER]      — old composition helpers
  trust_panel.py      [DEAD AFTER]      — superseded by darkframe.Footer
```

`[DEAD AFTER]` means: still imported by the
current `live.py`, will be unreferenced after the
migration. Move to `archive/launcher-pre10a/` in
the same commit as the migration.

---

## What moves from `LiveLauncher` into `DarkLauncher` wiring

### 1. State derivation

Current `LiveLauncher._refresh_idle_state` returns
one of two states (`digest` / `empty`). After
migration, the same method derives one of four:

| Engine condition                                              | New state slug    |
|---------------------------------------------------------------|-------------------|
| no events captured yet                                        | `empty`           |
| events present, no recovery candidate                         | `recovery` *(without HIGH band)* — falls through to a populated digest with strength-dot OtherRow stack |
| events present, recovery candidate above trust gate           | `recovery`        |
| `SearchBar.text()` non-empty                                  | `search`          |
| post-restore confirmation (live for ~3s after `restore`)      | `resume`          |

The derivation logic itself is engine-side and
already exists. The migration is mechanical: stop
constructing `MinimalShell` / `MinimalDigest` /
`MinimalEmpty`; start calling
`DarkLauncher.set_state(slug, **kw)` with the
appropriate fixtures.

### 2. Fixture marshalling

Three fixtures need engine → `DarkLauncher`
adapters:

| Engine input                                                  | DarkLauncher fixture           |
|---------------------------------------------------------------|--------------------------------|
| `recovery_candidate` (`id`, `title`, `targets`, `signal`, `gap`) | `RecoveryProps(...)`           |
| `recent_memory` rows + thread strengths                       | `OtherWorkRow[]`               |
| `preview` payload (file label, excerpt, highlight, meta)      | `PreviewProps(...)`            |
| search `SearchEngine.search()` result                         | `SearchGroupSpec[]`            |
| restore plan (`targets` + per-target status)                  | `RestoredItem[]`               |

These adapters land in a new `live.py` helper
module (e.g. `_fixtures.py` inside
`launcher_v3/`) so the marshalling stays out of
`live.py`'s control flow.

### 3. Signal wiring

| `LiveLauncher` host signal             | Where it lands on `DarkLauncher`              |
|----------------------------------------|-----------------------------------------------|
| `request_settings = pyqtSignal()`      | forward from `DarkLauncher.search_bar().request_settings` |
| `_request_search = pyqtSignal(str)`    | forward from `DarkLauncher.search_bar().query_changed` |
| (hide)                                 | forward from `DarkLauncher.search_bar().request_close` |
| `Esc` shortcut                         | unchanged — installed on the LiveLauncher root |
| `Ctrl+K` / `Cmd+K` shortcut            | call `DarkLauncher.search_bar().focus()`      |
| `1` shortcut (resume)                  | call `RecoveryView.resume.emit()` if in state `recovery` |

### 4. Restore-plan execution

`LiveLauncher._open_preview` currently constructs
a `ResumePreview` overlay + opens it. After the
migration:

- `RecoveryView.resume` → call
  `DarkLauncher.set_state(STATE_RESUME,
  restored_items=plan)` instead of opening the
  overlay.
- The plan execution (file/URL open) stays where
  it is — same `_open_target` helper, same API
  client call.
- `ResumeView.done_clicked` → revert to the prior
  state (`recovery` or `empty` depending on what
  came before).
- `ResumeView.undo_clicked` → call into the
  api_client undo endpoint (already exists).

The `RestoreToast` overlay goes away entirely —
the `ResumeView` *is* the confirmation surface.

---

## What stays in `LiveLauncher` (engine glue)

| Concern                                          | Why it stays                                          |
|--------------------------------------------------|-------------------------------------------------------|
| `APIClient(base_url="http://127.0.0.1:4545")`    | Loopback API session. `DarkLauncher` is engine-free. |
| `_load_recent_memory` / `_load_trust_counts`     | Reads `~/.recall/events/*.jsonl` directly + the bad-recovery ledger. Belongs with engine glue. |
| `_refresh_idle_state`                            | Engine-state poll loop + state-slug derivation.       |
| `_open_target` helper                            | OS-level file/URL open. Platform-specific.            |
| `QShortcut` registrations                        | Host-level keyboard wiring.                           |
| Single-instance lock + tray-icon wiring          | Lives in `app/main.py`; unchanged.                    |

Net effect: `LiveLauncher` shrinks from
~800 LOC of paint + composition + glue down to
~200 LOC of pure glue. The visual surface lives
exclusively in `darkframe.py`.

---

## What gets deleted

Pure-paint modules superseded by `darkframe.py`:

```
archive/launcher-pre10a/   (new)
  ├── minimal.py             (was MinimalShell + MinimalSearchBar + MinimalDigest + MinimalEmpty)
  ├── search_panel.py        (was the standalone 5-signal MinimalSearchBar)
  ├── recovery_panel.py      (was RecoveryCardV3 + _PillButton + _ResumeButton + _ReviewButton)
  ├── recent_memory.py       (was MemoryRow + RecentMemoryList)
  ├── investigation_panel.py (was InvestigationCardV3 + InvestigationList)
  ├── resume_preview.py      (was ResumePreview overlay + RestorationPlan)
  ├── restore_toast.py       (was the RestoreToast bottom-right confirmation)
  ├── surfaces.py            (was composition helpers)
  └── trust_panel.py         (was TrustRow)
```

Captures:

```
assets/screenshots/launcher-7e/  -> archive/screenshots-history-pre10a/
  (5 files: home, high, med, low, no_hero — the Phase 9 capture set)
```

The Phase 10A capture set under
`assets/screenshots/launcher-final/` *replaces*
this; the historical archive preserves the visual
record.

---

## Public API delta

```diff
# app/ui/launcher_v3/__init__.py

  from .live import LiveLauncher
+ from .darkframe import (
+     DarkLauncher, FRAME_W, FRAME_H,
+     STATE_EMPTY, STATE_RECOVERY, STATE_SEARCH, STATE_RESUME,
+     SearchBar, Footer, Frame,
+     EmptyView, RecoveryView, SearchView, ResumeView,
+     HeroRecovery, PreviewCard, OtherRow,
+     RecoveryProps, PreviewProps, OtherWorkRow,
+     SearchGroupSpec, SearchResultRow, RestoredItem,
+ )

# Pre-10A symbols re-exported as thin wrappers so any
# rogue importer outside launcher_v3/ keeps resolving:

- from .minimal import MinimalShell, MinimalSearchBar, MinimalDigest, MinimalEmpty
+ # NOTE: MinimalShell / MinimalSearchBar / MinimalDigest / MinimalEmpty
+ # removed in 10B. Importers should switch to DarkLauncher + SearchBar.
+ # Grep `from app.ui.launcher_v3.minimal` before deleting.
```

Grep targets to run before the migration commit:

```bash
grep -rn "MinimalShell\|MinimalSearchBar\|MinimalDigest\|MinimalEmpty\
\|RecoveryCardV3\|MemoryRow\|RecentMemoryList\
\|InvestigationCardV3\|InvestigationList\
\|ResumePreview\|RestoreToast" --include='*.py' .
```

If anything outside `app/ui/launcher_v3/` matches,
the importer needs updating in the same commit as
the migration.

---

## Risk register

| Risk                                                                | Mitigation                                                                                                  |
|---------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------|
| `app/main.py` boot path breaks                                       | `LiveLauncher` keeps its constructor signature `(search_engine, event_logger=None)`. Test with `from app.main import main`. |
| Keyboard shortcuts stop firing                                       | Hook all `QShortcut` registrations to `LiveLauncher` (not `DarkLauncher`). Verify with the offscreen smoke. |
| `request_settings` no longer reaches `app/main.py`                    | Forward signal explicitly in `LiveLauncher.__init__`: `self._dark.search_bar().request_settings.connect(self.request_settings.emit)`. |
| Restore plan races with state swap                                    | Snapshot `targets` + `title` at `resume_clicked` time; pass into `set_state(STATE_RESUME, ...)` before plan execution starts. |
| Cold-construct latency regresses past the 500 ms "feels instant" bar | Already measured: cold 110.9 ms, warm 1.4 ms. No regression risk. |
| State swap drops focus or causes flicker                              | `Frame._swap` uses `setParent(None)` so old widget stops painting same frame. Verified in Phase 10A captures. |

---

## What 10B does NOT do

- Visual changes. The Phase 10A `darkframe.py`
  paint is the contract.
- New states. Four states only. Any additional
  affordance (e.g. settings overlay) ships as a
  separate modal, not a fifth state.
- Engine work. `app/core/*` is untouched.
- `app/main.py` rewrites beyond the import line.
- Capture regeneration. The Phase 10A captures
  are the live record.

---

## Exit criteria for 10B

1. `Launcher(FakeEngine()).size() == QSize(760, 520)` — production size matches design.
2. Offscreen render of `LiveLauncher` in each
   of the four states produces a pixmap visually
   equivalent to its matching
   `launcher-final/*.png` (modulo engine fixture
   data).
3. All 5 Phase 7E.1 search-bar signals still
   fire from `LiveLauncher.search_bar()`.
4. `Phase 9 review` signal still fires from
   the recovery hero.
5. `python recall.py doctor` exits 0.
6. `_smoke_api.py` passes whatever subset it
   ran in Phase 10A.
7. Pre-10A modules archived to
   `archive/launcher-pre10a/`.
8. `app/ui/launcher_v3/__init__.py` re-exports
   the new public surface.
9. This sheet is updated with the final
   commit SHA + a 1-line "done" note.

Estimated effort: half-day, single commit, ≤300
LOC (mostly `live.py` slimming + one new fixture
adapter module). Risk: low (no engine work, no
visual work, no host-API changes).
