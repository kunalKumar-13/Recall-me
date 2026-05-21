# DEAD_CODE_AUDIT.md — what is no longer earning its weight

A real audit, grounded in `grep` and the import graph — not a guess.
Every row has a path, a reason it was flagged, an action, and a
risk note. Pairs with the safe-delete rule in
[`REPO_HEALTH.md`](REPO_HEALTH.md).

> **Rule (Phase 5D safe-delete policy).** Delete only if **unused
> AND verified AND documented**. Otherwise **archive**. Never strip
> commented blocks from hot paths in the same change as a behaviour
> edit.

---

## This cycle's actions

| Path | Reason | Action | Risk |
|---|---|---|---|
| `apps/web/app/components/Architecture.tsx` | not imported by `page.tsx` after the Phase 4F landing rebuild | **archived** → `archive/web-components/` | none — verified `next build` passes after |
| `apps/web/app/components/ContinueWorking.tsx` | orphan, same reason | **archived** | none |
| `apps/web/app/components/ContinuityCore.tsx` | orphan, same reason | **archived** | none |
| `apps/web/app/components/EvolutionTimeline.tsx` | orphan, same reason | **archived** | none |
| `apps/web/app/components/LocalFirstTopology.tsx` | orphan, same reason | **archived** | none |

Web build after: ✅ `Compiled successfully` (verified in-cycle).

## Flagged for follow-up — left in place

These were *identified* as dead this cycle but **not removed**:
each touches a hot path or a stable file, and Phase 5D's no-behaviour-change
rule says wait for a dedicated cleanup PR with smoke verification.

| Path | Reason | Recommended | Risk |
|---|---|---|---|
| `app/ui/widgets.py` — classes `RecoveryRow`, `ThreadRow`, `ResurfacedRow` | replaced by `app/ui/cards.py` in Phase 4K; no usages remain | archive (move to `archive/legacy-widgets.py`) | low — `launcher.py` no longer references them; need to confirm no external test imports |
| `app/ui/launcher.py` imports lines 125, 127, 130 (`RecoveryRow`, `ResurfacedRow`, `ThreadRow`) | dead imports after Phase 4K; harmless but noisy | delete the three lines | low — verify with `python -c "import app.ui.launcher"` |
| `app/ui/widgets.py` size — 2487 LOC | the launcher's widget-zoo lives here; see [`COMPLEXITY.md`](COMPLEXITY.md) | targeted split (e.g. `widgets/preview.py`, `widgets/results.py`) | high — a behaviour-preserving refactor needs the launcher smoke before it can ship |
| `apps/web/app/components/Logo.tsx`, `WindowsGlyph.tsx` | not in `page.tsx` directly but **used** by `Footer.tsx` / `Hero.tsx` / `FinalCTA.tsx` (verified by grep) | **keep** | — |

## Commented code / TODO density

```
$ grep -rE "# (TODO|FIXME|XXX|HACK)" app api --include="*.py" | wc -l
0
```

Zero TODO/FIXME/XXX/HACK comments across `app/` and `api/`. The
code carries intent comments (the *why*), not punch-list comments
(the *not yet*). Nothing to strip — this row is **clean**.

## Stale assets

| Path | Status |
|---|---|
| `assets/screenshots/*.png` | Phase 4L + 5A.1 + 5C real captures; not stale (see `assets/screenshots/README.md`) |
| `assets/screenshots/extension-popup-*.png` (old slugs) | the original Phase 4B *plan* slugs (`launcher-search`, `launcher-recovery-row`, `extension-popup`) never produced files — no stale PNGs on disk |
| `archive/web-components/` | 16 historical components (10 from Phase 4C + 5 this cycle); deliberately preserved, not stale |

## Top-level dirs

| Dir | Tracked? | Role |
|---|---|---|
| `app/`, `api/`, `apps/`, `infra/`, `assets/`, `archive/`, `releases/`, `packages/` | ✅ tracked | source / docs / staging |
| `build/`, `dist/`, `venv/`, `.venv/`, `demo/` (if present) | gitignored | build outputs / virtualenvs |

The `.gitignore` is consistent with the directive's
*"apps/ core/ infra/ docs/ assets/ archive/ releases/ tests/"*
target. The Python tree lives at the **repo root** under `app/` +
`api/` (the documented pseudo-monorepo state, per
[`apps/desktop/README.md`](../../apps/desktop/README.md)).

## What was *not* attempted

- **Aggressive star-import / circular-import removal.** Not run
  this cycle — needs a clean test run after each change. Tracked as
  a CI step in [`REPO_HEALTH.md`](REPO_HEALTH.md).
- **Auto-formatter sweep** (`ruff`, `black`, `isort`, `autoflake`).
  Not run this cycle — these have not been on the developer toolchain
  before, and a first-time reformat across ~30K LOC would be a huge
  no-behaviour-change diff. Add `ruff` to the CI workflow first,
  then a separate "format pass" commit.
- **Splitting `launcher.py` / `widgets.py`.** Behaviour-preserving
  but high-risk — see [`COMPLEXITY.md`](COMPLEXITY.md) for the
  recommended carve.

## Verification

After this cycle's archives:

```
cd apps/web && npx next build      # ✅ Compiled successfully
```

Engine smoke (the 35-section `_smoke_api.py`) was **not re-run**
this cycle — it exercises `app/core/*` and `api/*`, neither of
which was touched. The web move is independent.

---

*Updated each time real dead code is removed. Rows here cite the
phase and the verification — never a guess.*
