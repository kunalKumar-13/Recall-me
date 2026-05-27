# Phase 10A — Launcher Registration

**Status:** complete · launcher frozen at
`DarkLauncher (760, 520)` with 4 canonical states.

**Directive:** freeze launcher officially. NO UI
work, NO redesign, NO landing. Only docs + a
runtime-wiring migration sheet.

> The Phase 10 visual rebuild (commit `3ae52e2`)
> ships. The freeze paperwork catches up.

---

## Headline

| Metric                                           | Phase 9 close | Phase 10A close   |
|--------------------------------------------------|---------------|-------------------|
| **Active launcher canvas**                       | 720 × 460     | **760 × 520**     |
| **Active visual surface module**                 | `live.py` + `minimal.py` family | **`darkframe.py`** |
| **Named canonical states**                       | 2 (digest / empty) | **4** (empty / recovery / search / resume) |
| **Capture set authority**                        | `launcher-7e/` | **`launcher-final/`** |
| **Freeze docs aligned with active surface**      | drifted        | **registered**    |
| **Production tray-icon boot path migrated**      | no             | **no** (planned for 10B; sheet attached) |

---

## What changed (per directive section)

### 1. `AUDIT/LAUNCHER_FREEZE.md` — updated

Phase 10A amendment at the top of the file
supersedes both the Phase 9 (720×460) and 8B
(700×500) amendments. The amendment:

- Pins the active launcher at `DarkLauncher
  (760, 520)`.
- Names the four canonical states (empty,
  recovery, search, resume preview) and their
  captures.
- Preserves every prior freeze rule that still
  applies (no second tree, no
  `RECALL_LAUNCHER`, no file renames, no
  `QGraphicsDropShadowEffect`).
- Cross-links the migration sheet at
  [`docs/engineering/LAUNCHER_MIGRATION.md`](LAUNCHER_MIGRATION.md).

Three in-place `(720, 460)` literals replaced
with `(760, 520)`.

### 2. `docs/product/LAUNCHER_CONTRACTS.md` — updated

Phase 10A amendment at the top adds the new
public surface from
`app/ui/launcher_v3/darkframe.py`:

- `DarkLauncher` ctor + `state_changed` signal +
  `set_state(...)` keyword surface +
  `state()` + `search_bar()` accessors.
- `SearchBar` — preserves the 5 frozen 7E.1
  signals (`query_changed`, `searchChanged`,
  `submit`, `request_settings`, `request_close`)
  + 3 frozen methods (`focus`, `clear`,
  `selectAll`) verbatim.
- `HeroRecovery` — preserves the Phase 9
  `review_clicked` alongside the existing
  `resume_clicked`. Consumes a `RecoveryProps`
  dataclass.
- `RecoveryView` / `SearchView` / `ResumeView` —
  each documented with their public signal
  surface + state-derivation rules.
- `PreviewCard` — documented with its
  `PreviewProps` dataclass + `open_clicked`
  signal.
- Boot-path diagram + search-flow walk +
  resume-flow walk + preview-pane section all
  added.

The Phase 7E.1 original section stays as
historical record below.

### 3. `STABILITY/LAUNCHER.md` — updated

Phase 10A amendment at the top adds:

- **Render timings** for `DarkLauncher` across
  5 runs each, offscreen Qt with the system-font
  bootstrap: cold construct 110.9 ms; warm
  construct 1.4 ms; per-state swap 2.9–8.2 ms
  median; `render()` to 760×520 pixmap 19.3 ms.
- **State coverage table** — all four named
  states mapped to their composition + capture
  file.
- **Widget tree** — the new `DarkLauncher → Frame
  → {SearchBar, state widget, Footer}` shape.
- **Frozen contract check** — `from
  app.ui.launcher import Launcher` still
  resolves; `DarkLauncher().size() == (760,
  520)`. The `LiveLauncher` size still reads
  720×460 because the boot-path migration is
  Phase 10B (sheet attached).

### 4. `VERSION.md` — updated

The launcher frozen-surface row now reads
**"launcher-final active — Phase 10A
`DarkLauncher` (760×520, 4 states)"** and
cross-links the new `PHASE_10A_STATUS.md`. The
inline verify recipe now exercises both
`LiveLauncher` (pre-migration host wrapper) and
`DarkLauncher` (active visual surface).

### 5. `docs/engineering/LAUNCHER_MIGRATION.md` — new

Planning sheet only. **No implementation.**
Enumerates:

- **Files in scope** — what's `[ACTIVE]`, what's
  `[ACTIVE, MIGRATE]`, what's `[DEAD AFTER]`.
- **What moves** from `LiveLauncher` into the
  `DarkLauncher` slot — state derivation,
  fixture marshalling, signal wiring, restore-
  plan execution.
- **What stays** in `LiveLauncher` — the API
  client, the disk readers
  (`_load_recent_memory` / `_load_trust_counts`),
  the `QShortcut` registrations, the OS-level
  `_open_target` helper, the single-instance
  lock.
- **What gets deleted** — 9 pure-paint modules
  superseded by `darkframe.py`; the Phase 9
  capture set archived.
- **Public API delta** — concrete `__init__.py`
  diff.
- **Risk register** — 6 named risks + their
  mitigations.
- **Exit criteria** — 9 numbered conditions for
  Phase 10B to ship cleanly.
- **Estimate** — half-day, single commit,
  ≤300 LOC, low risk.

### 6. `docs/engineering/PHASE_10A_STATUS.md` — this file

Capstone for 10A. Pairs with the existing
phase-status chain:
[8A](../../AUDIT/STATE.md) →
[8B](PHASE_8B_STATUS.md) →
[8C](../../STABILITY/) →
[8D](PHASE_8D_STATUS.md) →
[8E](PHASE_8E_STATUS.md) →
8F Track A (`3ae52e2` commit body) →
**10A (this file)**.

---

## Files touched (strict)

| Path                                                   | Change                                |
|--------------------------------------------------------|---------------------------------------|
| `AUDIT/LAUNCHER_FREEZE.md`                             | Phase 10A amendment + 3 size literals |
| `docs/product/LAUNCHER_CONTRACTS.md`                   | Phase 10A amendment (DarkLauncher API)|
| `STABILITY/LAUNCHER.md`                                | Phase 10A amendment (timings + states)|
| `VERSION.md`                                           | launcher row + verify recipe          |
| `docs/engineering/LAUNCHER_MIGRATION.md`               | new                                   |
| `docs/engineering/PHASE_10A_STATUS.md`                 | new (this file)                       |

**Files NOT touched** (per directive):

- Any `.py` file. **No UI work. No engine
  work.** The Phase 10A commit `3ae52e2`
  already landed the visual surface; this phase
  is paperwork.
- Anything outside `AUDIT/`, `STABILITY/`,
  `docs/`, and `VERSION.md`.
- Captures (`assets/screenshots/launcher-final/`
  / `assets/screenshots/launcher-7e/`).
- Landing site (`apps/web/`). **No landing.**
- Extension (`apps/extension/`). **No
  extension.**
- Engine (`app/core/`). **No engine.**

---

## Verification

| Check                                                  | Result |
|--------------------------------------------------------|--------|
| `AUDIT/LAUNCHER_FREEZE.md` open + reads coherent       | ✅     |
| `docs/product/LAUNCHER_CONTRACTS.md` ditto             | ✅     |
| `STABILITY/LAUNCHER.md` ditto                          | ✅     |
| `VERSION.md` launcher row reads "launcher-final active"| ✅     |
| `docs/engineering/LAUNCHER_MIGRATION.md` exists        | ✅     |
| `docs/engineering/PHASE_10A_STATUS.md` exists          | ✅     |
| No `.py` files modified                                | ✅     |
| No engine / extension / landing touched                | ✅     |

The 10A commit is docs-only.

---

## Success criterion

> Freeze launcher officially.

Met:

1. **Active surface registered.** Every prior
   "720×460 / Phase 9" reference in the four
   freeze docs now reads "760×520 / Phase 10A
   `DarkLauncher`".
2. **Public API documented.** `LAUNCHER_CONTRACTS.md`
   carries the full `DarkLauncher` surface --
   ctor, signals, `set_state` keyword args, the
   five preserved 7E.1 search-bar signals, the
   preserved Phase 9 `review` signal.
3. **Render timings real.** `STABILITY/LAUNCHER.md`
   carries the offscreen-measured per-state
   timings + the four captures' paths.
4. **Version row pinned.** `VERSION.md` reads
   "launcher-final active".
5. **Migration sheet in place.** `LAUNCHER_MIGRATION.md`
   enumerates the slot-in plan with exit
   criteria + risk register -- ready for Phase
   10B to execute.

---

## What's next

**Phase 10B — Launcher migration**

Execute the migration sheet. ~half-day, single
commit, ≤300 LOC. Exit criteria already named in
[`LAUNCHER_MIGRATION.md`](LAUNCHER_MIGRATION.md).

After 10B lands:

- `LiveLauncher` is a thin wrapper around
  `DarkLauncher`.
- `LiveLauncher(FakeEngine()).size()` returns
  `QSize(760, 520)`.
- Production tray-icon boot path shows the
  Phase 10A dark surface in each of the four
  states.
- 9 pre-10A paint modules archived to
  `archive/launcher-pre10a/`.

**Then** the landing site (`apps/web/`)
rebuild becomes the next phase candidate. Not
before.
