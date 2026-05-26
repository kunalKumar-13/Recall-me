# archive/launcher-v2/

Three widgets removed from `app/ui/launcher_v3/` in **Phase 6L —
Launcher Simplification**. Kept in this directory as a historical
reference: the *three-column dashboard* shape the launcher used to
take, and the rationale for stripping it back.

The directive: the launcher is a **single floating surface**, not an
admin panel, not a control room, not an analytics view. System info
lives only in the founder control room (`apps/admin/web/`).

| File | Class | Why archived |
|---|---|---|
| `shell.py` | `Shell`, `ContextColumn` | The 3-column composition (sidebar + centre + context column with Today / Doctor / version / extension / protocol blocks) leaked a *dashboard* feeling into the launcher. Phase 6L replaces the Shell with a single-column floating layout; the ContextColumn is gone entirely. |
| `sidebar.py` | `Sidebar` | The rich left rail (Recall mark + search input + 4-row section nav + accent-dot active markers + keyboard-hint footer) added density a user opening Recall for 5 seconds did not need. The replacement minimal search bar lives directly inline in the new shell. |
| `window.py` | `LauncherWindow` | The old window composed a `Shell`; the new minimal window composes the single-column layout directly. The class name moves into the new minimal module. |

## What this directory is not

- **Not** a parallel surface. The launcher only ever renders the
  Phase 6L minimal layout. The archive is reference, not a code
  path.
- **Not** a feature-flag fallback. Phase 6K kept the legacy v2
  launcher as `RECALL_LAUNCHER=legacy`; Phase 6L's archive is
  permanent. If a 6L regression surfaces, the fix is in
  `launcher_v3/`, not a re-import of these files.
- **Not** part of any build / capture pipeline. Nothing under
  `app/`, `infra/`, or `apps/` imports from this directory.

## Why we kept the files at all

The launcher's visual language has *layers*: the v3 surface
primitives (`GlassCard`, `Pill`, `ConfidenceBadge`, …) are still
used by the minimal layout. The three archived widgets show one
plausible *composition* of those primitives — useful when a future
phase needs to decide whether a dashboard-shaped surface still
belongs anywhere in the product. Spoiler: it doesn't belong in the
launcher.

If a maintainer ever wants to render the 6I three-column shell for
a marketing image or a comparison capture, the widgets are right
here.

## What lives in `app/ui/launcher_v3/` now

| File | Purpose |
|---|---|
| `theme.py` | colour / radius / shadow tokens (unchanged) |
| `motion.py` | timings (unchanged) |
| `surfaces.py` | primitives (unchanged) |
| `recovery_panel.py` | `RecoveryCardV3` (unchanged) |
| `investigation_panel.py` | `InvestigationCardV3` + horizontal strip variant (new in 6L) |
| `trust_panel.py` | minimal trust line (slimmed in 6L) |
| `search_panel.py` | optional results column (used inline, not in a sidebar) |
| `digest.py` | `DigestColumn` + `EmptyDigest` (slimmed for the minimal layout) |
| `minimal.py` | the **new** single-column shell + search bar + investigations strip + recent returns (new in 6L) |
| `live.py` | `LiveLauncher` — now composes `minimal.MinimalShell` instead of `shell.Shell` |
| `__init__.py` | barrel — drops `ContextColumn` / `Shell` / `Sidebar` / `LauncherWindow` from `__all__` |

The package is still named `launcher_v3` for import stability
(`from app.ui.launcher import Launcher` resolves to
`launcher_v3.LiveLauncher` as Phase 6K wired it).
