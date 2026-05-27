# Launcher Freeze — Phase 10A (active, 2026-05-27)

> **Phase 10A amendment — supersedes Phase 9 + 8B.**
>
> The active launcher surface is `DarkLauncher`
> (`app/ui/launcher_v3/darkframe.py`) at
> `(760, 520)`. Dark cinematic palette per the
> design pack at
> `api.anthropic.com/v1/design/h/owqos4Wz0Vg_6mMaKfPcmw`.
> Four canonical states, each with its own
> deterministic capture in
> [`assets/screenshots/launcher-final/`](../assets/screenshots/launcher-final/):
>
> | State            | Capture                  | Renders                              |
> |------------------|--------------------------|--------------------------------------|
> | Empty            | `empty.png`              | bloom mark + serif-italic gradient + Show example / Start working |
> | Recovery         | `recovery.png`           | Continue hero + side preview card + 3 Other-work rows |
> | Search           | `search.png`             | grouped result list (Investigation / Files / Returns / Events) + mini preview pane |
> | Resume preview   | `resume-preview.png`     | check disc + RESTORED header + restored item list + Undo / Done |
>
> The Phase 9 `(760, 520)` warm-paper canvas + the
> 7E.1 / 8B `(700, 500)` canvas are now historical
> visual records. The Phase 9 capture set under
> `assets/screenshots/launcher-7e/` stays in tree
> as the historical record; the Phase 10A active
> surface lives under
> `assets/screenshots/launcher-final/`.
>
> **Public contract preserved.**
> `from app.ui.launcher import Launcher` still
> resolves; `LiveLauncher`'s engine wiring is
> untouched in this phase (see
> [`LAUNCHER_MIGRATION.md`](../docs/engineering/LAUNCHER_MIGRATION.md)
> for the slot-in plan). The 5 frozen 7E.1 search
> signals (`query_changed`, `searchChanged`,
> `submit`, `request_settings`, `request_close`)
> are preserved on `DarkLauncher.SearchBar`. The
> Phase 9 `review` signal is preserved on the
> recovery hero (now `darkframe.HeroRecovery`).
> Additive-only rule intact: Phase 10A *adds*
> 4 explicit named states + a public footer
> surface; it does not remove or rename any prior
> signal.
>
> *Every other freeze rule below still holds.*
> No second launcher tree (DarkLauncher *replaces*
> the prior visual surface; both live inside
> `app/ui/launcher_v3/`). No `RECALL_LAUNCHER`
> env-var. No file renames of `app/ui/launcher.py`
> or `app/ui/launcher_v3/`. No
> `QGraphicsDropShadowEffect`.
>
> Migration of the production tray-icon boot path
> from `LiveLauncher`'s Phase 9 composition to
> `DarkLauncher` is sheet-only in 10A and lives at
> [`LAUNCHER_MIGRATION.md`](../docs/engineering/LAUNCHER_MIGRATION.md).
> No runtime wiring is changed here.

---

## Active launcher path (Phase 10A)

```
app/main.py
    │
    └─►  from app.ui.launcher import Launcher
              │
              └─►  LiveLauncher         (app/ui/launcher_v3/live.py)
                       │
                       └─►  DarkLauncher         (darkframe.py)        ← Phase 10A slot
                                │
                                ├─►  Frame              760 × 520 root
                                ├─►  SearchBar          60 px top row
                                ├─►  Footer             30 px bottom row
                                │
                                └─►  one of:
                                       EmptyView
                                       RecoveryView   (HeroRecovery + PreviewCard + OtherRow×N)
                                       SearchView     (SearchGroup×N + _MiniPreviewPane)
                                       ResumeView     (_CheckDisc + _RestoredListContainer + Undo/Done)
```

Token surface: `theme.py` — dark cinematic
palette (`BG #08070C`, `SURFACE #0F0D16`,
`CARD #15131F` → `CARD_HI #1B1827`,
`ACCENT #A78BFA`, six-step ink ladder).

Animation timings unchanged from Phase 9:
fast 120 ms · normal 180 ms · slow 240 ms.

---

# Launcher Freeze — Phase 8B (original)

The launcher is now **one tree, one path, one contract**.
This document is the final word — supersedes
[`LAUNCHER_FINAL.md`](../docs/product/LAUNCHER_FINAL.md)
on *which files exist* (the paint contract still lives
there) and supersedes
[`LAUNCHER_CONTRACTS.md`](../docs/product/LAUNCHER_CONTRACTS.md)'s
*"slow-path"* removal procedure (now there's no legacy
launcher to migrate away from).

> No more launcher generations. There is one launcher.

---

## Official launcher path

```
app/main.py
    │
    └─►  from app.ui.launcher import Launcher
              │
              └─►  LiveLauncher   (app/ui/launcher_v3/live.py)
                       │
                       ├─►  MinimalWindow         (minimal.py)
                       ├─►  MinimalSearchBar      (minimal.py)
                       ├─►  MinimalDigest         (minimal.py)
                       │       ├─►  RecoveryCardV3       (recovery_panel.py)
                       │       ├─►  RecentMemoryList     (recent_memory.py)
                       │       └─►  InvestigationList    (investigation_panel.py)
                       ├─►  TrustRow              (minimal.py)
                       ├─►  ResumePreview         (resume_preview.py)
                       └─►  RestoreToast          (restore_toast.py)
```

The 11 files above + `theme.py` + `live.py` +
`__init__.py` = **the entire launcher**. No legacy
path. No env-var fork. No `RECALL_LAUNCHER` variable.

---

## What's archived (Phase 8B move)

Under [`archive/launcher-old/`](../archive/launcher-old/):

| Archived path                            | Was                                        |
|------------------------------------------|--------------------------------------------|
| `launcher_legacy.py`                     | the v2 launcher (2675 LOC)                  |
| `cards.py`                               | legacy `RecoveryCard` + `InvestigationCard` |
| `widgets.py`                             | legacy `PreviewPane`, `DigestRow`, etc.     |
| `styles.py`                              | legacy `LAUNCHER_QSS`                       |
| `launcher_anims.py`                      | digest stagger animation                    |
| `launcher_digest.py`                     | digest labels + caps                        |
| `demo_data.py`                           | `DemoSearchEngine` for legacy demo path     |
| `ceremonies.py`                          | one-shot recovery toast helper              |
| `captures/capture_launcher.py`           | historical capture script                  |
| `captures/capture_recovery.py`           | historical capture script                  |
| `captures/capture_demo.py`               | historical capture script                  |

Nothing in active code paths imports from
`archive/launcher-old/`.

---

## Public API (frozen — 7E.1 + 8B)

### `Launcher` (alias for `LiveLauncher`)

```python
from app.ui.launcher import Launcher
launcher = Launcher(search_engine, event_logger=None, parent=None)
```

### Methods

| Method                  | Purpose                                          |
|-------------------------|--------------------------------------------------|
| `show_centered()`       | Show launcher centred on the active screen       |
| `invalidate_digest()`   | Drop cached digest; next refresh re-fetches      |
| `_refresh_idle_state()` | Recompute idle surface                           |
| `hide()`                | Standard Qt; also fired by `request_close`       |

### Signals

| Signal              | Args  | Notes                                                  |
|---------------------|-------|--------------------------------------------------------|
| `request_settings`  | —     | Forwarded from `self._search.request_settings`         |
| `_request_search`   | `str` | Emitted on `MinimalSearchBar.query_changed`            |

### `MinimalSearchBar` contract (frozen 7E.1)

5 signals + 3 methods. See
[`docs/product/LAUNCHER_CONTRACTS.md`](../docs/product/LAUNCHER_CONTRACTS.md).
Unchanged in 8B.

### Window size

`MinimalWindow.DEFAULT_SIZE = (760, 520)` — hard clamp,
no resize. Frozen 7E.

### Keyboard shortcuts

| Key              | Effect                                                       |
|------------------|--------------------------------------------------------------|
| `Esc`            | Closes the resume preview if open; otherwise hides           |
| `Ctrl+K` / `⌘K`  | Focuses + selects-all the search input                        |
| `1`              | Resumes the visible Continue document (if any)               |

---

## Allowed changes

Any change that satisfies **all** of these:

- Adds a method or signal to one of the public classes —
  doesn't remove or rename one.
- Keeps `DEFAULT_SIZE = (760, 520)`.
- Keeps the `from app.ui.launcher import Launcher` import
  contract.
- Touches **only files inside `app/ui/launcher_v3/`** (or
  documents a precise reason for touching `app/ui/launcher.py`).
- Passes `pyflakes app/ui` clean.
- Passes offscreen `Launcher(FakeEngine())` boot check
  (the 7E.1 reproduction).
- Updates `LAUNCHER_CONTRACTS.md` + the relevant audit
  doc in the same change.

---

## Forbidden changes

- **Removing any public signal or method on the classes
  listed above.** Breaks the host (`app/main.py`,
  `apps/admin/web/`, any future consumer). The 7E.1
  regression that this rule exists to prevent.
- **Renaming any file under `app/ui/launcher_v3/`.**
  Consumers reference symbols by their import path.
- **Adding a second launcher tree.** Any "new launcher
  experiment" must replace the existing one, not parallel
  it.
- **Reintroducing `RECALL_LAUNCHER=legacy`.** The
  collapsed adapter is final.
- **Reverting the canvas to anything other than
  `(760, 520)`.** Captures + visual contract assume this
  exact pinpoint.
- **Adding `QGraphicsDropShadowEffect`** to any launcher
  surface. 7B replaced it with manual painted shadows for
  the hot-path performance budget; reintroducing it
  reintroduces the jank.

---

## No more launcher generations

The launcher's audit chain (one phase per visible
generation): 6I → 6K → 6L → 6M.1 → 6M.2 → 6N → 6O → 6P.1
→ 6Q → 6R → 7B → 7B.1 → 7E → 7E.1.

**14 phases over the launcher.**

Phase 8B is the freeze. Any phase that proposes a 15th
launcher generation must justify why this audit + this
freeze rule + the 7E.1 contract are insufficient — and
must supersede this document explicitly, in the same
change, with its own freeze rule replacing this one.

Default-no on launcher work going forward.
