# archive/launcher-overbuild/

Six files removed from `app/ui/launcher_v3/` (and
`infra/scripts/capture/`) during the **Launcher Reset — Product
Pass** (filed as Phase 6O). They are kept here as historical
reference: a record of the surfaces the launcher *grew* over
phases 6I–6N that the reset directive judged as overbuild.

The reset rule the directive repeated three times: **stop
adding, delete complexity, build ONE surface**. The launcher
became a memory center / analytics view / dashboard hybrid;
the reset returned it to a single floating tool — search,
CONTINUE, OTHER WORK — and nothing else.

| File | What it carried | Why archived |
|---|---|---|
| `minimal.py` | `MinimalReturns` (returns row), `MinimalTrust` (footer), `_OverflowChip` (`+N more` overflow chip), `_build_preview_card` (preview recovery on empty), Recent returns strip wiring. | The directive named all of them in the *delete* list: *returns strip · trust rows · preview cards · footers*. The reset surface stops at search + CONTINUE + OTHER WORK. |
| `recovery_panel.py` | `RecoveryCardV3` with 3-state signal variants (HIGH / MED / LOW), `_ResumePill(kind=…)` (Resume/Continue/Review), confidence sentence row, evidence-chip parser with 3-chip cap, top-right `ConfidenceBadge`. | Directive: *Only HIGH recovery exists*. The reset hero is one fixed 100 px card with title + meta + Resume. MED and LOW states gone. Sentences gone. Confidence badge gone. |
| `investigation_panel.py` | `InvestigationCardV3` with status dots, soft-rounded pill shells, surface-type chips. `_OverflowChip`. `sort_for_digest()` priority sorter (unfinished / returned / recent / passive). `InvestigationRow` with overflow. | Directive: *Investigations: max 3 · single row · equal width · no overflow animations*. The reset row is bare text titles — no dot, no chrome, no priority sort, no overflow chip. |
| `digest.py` | `DigestColumn` + `EmptyDigest` from Phase 6I — the prior premium-surface composition. | Not part of the reset surface and no longer importable (its `InvestigationPanel` dependency was removed in the same reset). Kept here so a maintainer can recover the 6I composition for comparison. |
| `capture_launcher_compact.py` | The 6M.2 capture script — produced `assets/screenshots/launcher-compact/`. | The widget arguments + sizes it fixtures (920×720 windows, signal=high/medium/low cards, returns row, overflow chip) no longer exist; the script would error if re-run. The compact PNGs themselves stay on disk as historical reference. |
| `capture_launcher_recovery.py` | The 6N capture script — produced `assets/screenshots/launcher-recovery/`. | Same reason: the 3-state hero + preview card + investigation pills it fixtures are gone. The recovery PNGs themselves stay on disk as the *before* reference the reset doc compares against. |

## What stays in `app/ui/launcher_v3/` after the reset

| File | Purpose |
|---|---|
| `theme.py` | tokens — kept |
| `motion.py` | timing constants — kept (the reset doesn't use them, but downstream callers might) |
| `surfaces.py` | primitives — kept; the reset only imports a few but the rest are available for capture scripts |
| `recovery_panel.py` | **rewritten**: one `RecoveryCardV3` (100 px fixed, title + meta + Resume) + `_ResumeButton` + `_EliderLabel` |
| `investigation_panel.py` | **rewritten**: `InvestigationCardV3` (bare title) + `InvestigationRow` (max-3 equal-width row) |
| `minimal.py` | **rewritten**: `MinimalSearchBar` · `MinimalDigest` · `MinimalEmpty` · `MinimalShell` · `MinimalWindow`. 680 × 460. Paper white. |
| `live.py` | `LiveLauncher` — gates the hero on `n_targets ≥ 4` (HIGH only); otherwise shows the empty surface |
| `search_panel.py` | unchanged (inline search results — still optional) |
| `trust_panel.py` | unchanged (legacy escape-hatch surface only) |

## Why this directory exists at all

The launcher's overbuild happened over six phases (6I → 6N). The
features that landed in each phase were individually reasonable
at the time of their directive — multi-column shells, signal-
tinted hero variants, sort priorities, preview cards, returns
strips. The directives kept adding; nobody asked the question
*"does this still look like a tool?"* until the reset directive
did.

This archive is the answer to *"what did we build that we
shouldn't have?"* for the next surface-design conversation. The
files don't run. They aren't a fallback. They are a record of
features the launcher carried that the reset took back.

Nothing in `app/`, `infra/`, or `apps/` imports from this
directory.
