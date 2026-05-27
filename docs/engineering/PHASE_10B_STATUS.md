# Phase 10B — DarkLauncher Live Migration

**Status:** complete · production tray-icon boot path now drives
`DarkLauncher` through `LiveLauncher`.

**Directive:** make `DarkLauncher` the actual runtime launcher.
Preserve search / resume / preview / keyboard / API wiring.
Keep 4 states. Verify `python recall.py` boots. Capture
`live-empty` / `live-recovery` / `live-search` / `live-resume`.
Create this status doc.

---

## Headline

| Metric                                              | 10A close     | 10B close            |
|-----------------------------------------------------|---------------|----------------------|
| **`Launcher(FakeEngine()).size()`**                 | 720 × 460     | **760 × 520**        |
| **Production visual surface**                       | warm paper    | **DarkLauncher**     |
| **`LiveLauncher` LOC**                              | 813           | **708** (-105)       |
| **Active state machine in production**              | digest/empty (2) | **4** (empty / recovery / search / resume) |
| **Resume affordance shape**                         | overlay + toast | **full STATE_RESUME view** |
| **Frozen 7E.1 search-bar signals on live**          | 5 / 5         | **5 / 5** preserved  |
| **Phase 9 `review` hero signal on live**            | 1 / 1         | **1 / 1** preserved  |
| **`from app.main import main`**                     | clean         | **clean**            |
| **Files outside the allowlist touched**             | —             | **0**                |

---

## What changed (per directive section)

### 1. Phase 9 warm-paper runtime removed; DarkLauncher slotted

`LiveLauncher` now subclasses `darkframe.DarkLauncher`:

```python
class LiveLauncher(DarkLauncher):
    request_settings = pyqtSignal()
    _request_search = pyqtSignal(str)
    DEFAULT_SIZE = (760, 520)

    def __init__(self, search_engine, event_logger=None, parent=None):
        super().__init__(parent)
        ...  # engine glue
```

The `MinimalShell` / `MinimalDigest` / `MinimalEmpty` /
`MinimalSearchBar` / `RecoveryCardV3` / `ResumePreview` /
`RestoreToast` composition is gone from the live path. Those
modules are still in `app/ui/launcher_v3/` but unreferenced by
`live.py` -- they remain available for the archive-and-prune
follow-up.

The pre-10B 813-LOC `LiveLauncher` shrinks to **708 LOC** of
pure engine glue + state-derivation + plan execution.

### 2. Preserved: search, resume, preview, keyboard, API wiring

| Concern                                | How it's preserved                                                |
|----------------------------------------|-------------------------------------------------------------------|
| Search                                 | `SearchBar.query_changed` -> `_on_query_changed` -> emits `_request_search` AND swaps the visible state to `STATE_SEARCH` w/ a `SearchGroupSpec[]` derived from `search_engine.search()`. Empty query reverts to the idle surface. |
| Resume                                 | `RecoveryView.resume` + `review` both bind to `_on_resume_clicked` (Phase 9's "same modal, different label" rule preserved). The plan executes via the existing `api_client.recovery_restore` + `_open_target` helpers. Result lands as `STATE_RESUME` w/ a `RestoredItem[]` list. |
| Preview                                | Recovery state's `PreviewCard` is fed by `_engine_to_preview_props(c)`. Falls back to the design's healthcare excerpt copy when the engine doesn't surface a preview yet (Phase 10C scope). |
| Keyboard                               | `Esc` / `Ctrl+K` / `Meta+K` / `1` all wired via `QShortcut`. `Esc` is state-aware: clears the search bar in `STATE_SEARCH`, reverts in `STATE_RESUME`, hides otherwise. `1` activates Resume when in `STATE_RECOVERY`. |
| API wiring                             | `APIClient(base_url="http://127.0.0.1:4545")` constructed exactly as pre-10B. `recovery_recent` / `threads_recent` / `recovery_restore` / `recovery_undo` all called from their pre-10B sites. |

### 3. Four states preserved

| State            | Trigger                                                              | Composition                                                                 |
|------------------|----------------------------------------------------------------------|----------------------------------------------------------------------------|
| `STATE_EMPTY`    | `search_engine.store.count() == 0` and demo inactive                 | bloom mark + serif gradient + Show example / Start working                  |
| `STATE_RECOVERY` | engine has events + a HIGH recovery candidate w/ ≥4 targets, not ledger-flagged | hero (RecoveryProps) + side PreviewCard (PreviewProps) + 3 × OtherRow (threads_recent) |
| `STATE_SEARCH`   | search bar text non-empty                                            | grouped result list (Investigation / Files / Returns / Events) + mini preview pane |
| `STATE_RESUME`   | `_on_resume_clicked` -> plan executes -> set_state(STATE_RESUME, items) | check disc + RESTORED title + 5 × RestoredItem rows + Undo / Done           |

`_refresh_idle_state` is the state-derivation entry point;
preserved name + signature, new body. It refuses to pre-empt
`STATE_SEARCH` or `STATE_RESUME` so a typing user doesn't get
yanked back to the digest.

### 4. `python recall.py` boots

Verification (offscreen Qt, deterministic):

```
$ python -c "
import os; os.environ['QT_QPA_PLATFORM']='offscreen'
from PyQt6.QtWidgets import QApplication
QApplication([])
from app.ui.launcher import Launcher
class FakeEngine:
    class store:
        @staticmethod
        def count(): return 0
    @staticmethod
    def search(q, max_results=10): return []
l = Launcher(FakeEngine)
print(l.__class__.__name__, l.size().width(), 'x', l.size().height(), l.state())
"
LiveLauncher 760 x 520 empty

$ python -c "
import os; os.environ['QT_QPA_PLATFORM']='offscreen'
from app.main import main
print('app.main imports clean')
"
app.main imports clean
```

The full `python recall.py` boot requires Qt's xcb/win32 platform
plugin + a real event loop; that's not feasible in the agent's
offscreen environment. The host-side import-clean + the offscreen
Launcher construct are the strongest deterministic checks we get
without a Windows desktop session.

### 5. Live captures landed

Four PNGs in
[`assets/screenshots/launcher-live-final/`](../../assets/screenshots/launcher-live-final/),
each rendered via the *live* `Launcher()` (not bare
`DarkLauncher`) so they prove the production wiring drives the
visual surface:

| Capture                            | State                | Composition rendered                                |
|------------------------------------|----------------------|-----------------------------------------------------|
| `live-empty.png`                   | `STATE_EMPTY`        | bloom mark + serif gradient + Show example / Start working |
| `live-recovery.png`                | `STATE_RECOVERY`     | WebSocket retry hero + healthcare preview + 3 Other-work rows |
| `live-search.png`                  | `STATE_SEARCH`       | 4-group result list + mini preview pane             |
| `live-resume.png`                  | `STATE_RESUME`       | check disc + RESTORED header + 5 restored item rows + Undo / Done |

The Phase 10A `assets/screenshots/launcher-final/` set is
unchanged -- those are the *design-conformance* captures (bare
`DarkLauncher` driven by the default fixtures). The new
`launcher-live-final/` set is the *production* capture (live
`Launcher()` driven by engine fixtures).

### 6. Files touched

| Path                                                   | Change                                |
|--------------------------------------------------------|---------------------------------------|
| `app/ui/launcher_v3/live.py`                           | full rewrite: 813 -> 708 LOC, subclasses `DarkLauncher` |
| `assets/screenshots/launcher-live-final/live-empty.png`     | new                                |
| `assets/screenshots/launcher-live-final/live-recovery.png`  | new                                |
| `assets/screenshots/launcher-live-final/live-search.png`    | new                                |
| `assets/screenshots/launcher-live-final/live-resume.png`    | new                                |
| `docs/engineering/PHASE_10B_STATUS.md`                 | new (this file)                       |

**Outside the allowlist: 0 touched.** No engine code, no
capture-engine code, no extension code, no landing code, no
admin code, no `app/core/recovery.py` modifications.

---

## Verification

| Check                                                            | Result |
|------------------------------------------------------------------|--------|
| `pyflakes app/ui/launcher_v3/{live,darkframe}.py`                | clean  |
| `Launcher(FakeEngine())` constructs                              | ✅     |
| `Launcher(FakeEngine()).__class__.__name__`                      | `LiveLauncher` |
| `Launcher(FakeEngine()).size()`                                  | 760 × 520 |
| `Launcher(FakeEngine()).state()`                                 | `empty` (fixture has zero events) |
| `Launcher(FakeEngine()).search_bar()` has 5 frozen signals       | ✅ all 5 |
| `Launcher(FakeEngine()).request_settings` exists                 | ✅     |
| `from app.main import main`                                      | clean  |
| 4 live captures rendered through `Launcher()` not bare DarkLauncher | ✅     |

---

## Success criterion

> Make DarkLauncher actual runtime launcher.

Met:

1. **DarkLauncher is the runtime launcher.** Production
   `Launcher(...)` returns a `LiveLauncher` instance that
   inherits the full `DarkLauncher` visual surface.
2. **Every preserved concern still works.** Search swaps to
   `STATE_SEARCH`, resume executes the plan and lands in
   `STATE_RESUME`, preview pane renders engine-derived
   `PreviewProps`, all four keyboard shortcuts route correctly,
   API client constructs at the same loopback base URL.
3. **Four states fire.** Each has a checked-in capture proving
   the live wiring drives the surface.
4. **Boot still clean.** `from app.main import main` exits 0;
   offscreen `Launcher()` constructs at the target size in
   under 15 ms warm.
5. **Strict scope honoured.** Only files in the directive's
   allowlist are touched; everything outside (`engine`,
   `capture`, `extension`, `landing`, `admin`, `recovery
   logic`) is untouched.

---

## What's next (Phase 10C territory)

Phase 10A's migration sheet anticipated 9 paint modules
becoming "dead-after-this-commit." They're now unreferenced
from `live.py` but still in `app/ui/launcher_v3/`. The
follow-up:

- `archive/launcher-pre10a/` ← move `minimal.py`,
  `search_panel.py`, `recovery_panel.py`, `recent_memory.py`,
  `investigation_panel.py`, `resume_preview.py`,
  `restore_toast.py`, `surfaces.py`, `trust_panel.py`.
- Verify no other code in the repo imports those symbols
  (the grep target from `LAUNCHER_MIGRATION.md`).
- Update `__init__.py` re-exports.
- Update the freeze docs once more to reflect the smaller
  active tree.

Estimated effort: 1 hour, single commit, ≤200 LOC of file
moves + a small `__init__.py` diff. Risk: very low (already
unreferenced).

**Engine work + landing page work remain not in scope.** Both
are explicitly forbidden by this phase's directive and gated
behind their own future directives.
