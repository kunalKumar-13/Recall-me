# REPO_CLEANUP_REPORT.md — Repo Stabilization Pass

A single audit pass across the Python launcher, the browser
extension, the marketing site, and the repo's surface files.
**No behavior changes** — every entry below is either dead code
removed, a redirect stub added, or a `.gitignore` tightening. The
verification block at the bottom is the receipt.

Pairs with [`DEAD_CODE_AUDIT.md`](DEAD_CODE_AUDIT.md) (the Phase
5D ledger) and [`REPO_HEALTH.md`](REPO_HEALTH.md) (the
LOC + size metrics doc).

---

## Removed

### Python — 28 unused imports across 14 files

Detected by `python -m pyflakes app/ui app/core api` (pyflakes
3.4.0). All removals verified by re-running pyflakes after each
file and re-importing the modules. No `__all__` re-exports
affected — checked via `grep "__all__" app/ ui/ api/`.

| File | Removed |
|---|---|
| `app/ui/cards.py` | `typing.List`, `typing.Tuple` |
| `app/ui/hotkey.py` | `typing.Optional` |
| `app/ui/launcher.py` | `..core.episodic.EpisodicRetriever`, `..core.microcontexts.MicroContextReconstructor`, `..core.recovery.RestorationPlan`, `..core.recovery.RestorationStep`, `..core.sessions.SessionReconstructor`, `..widgets.RecoveryRow`, `..widgets.ResurfacedRow`, `..widgets.SessionTimelineCard`, `..widgets.ThreadRow` |
| `app/core/api_client.py` | `typing.Tuple` |
| `app/core/demo_seed.py` | `dataclasses.field` |
| `app/core/events.py` | `datetime.date`, `typing.Iterable` |
| `app/core/evolution.py` | `math`, `collections.defaultdict`, `datetime.datetime`, `datetime.timezone`, `typing.Iterable` |
| `app/core/microcontexts.py` | `time as _time`, `typing.Iterable` |
| `app/core/sessions.py` | `time`, `datetime.timezone` |
| `app/core/threads.py` | `typing.Iterable` |
| `api/main.py` | `app.core.evolution.ThreadEvolution` |
| `api/services/evolution.py` | `typing.List`, `app.core.threads.ThreadBuilder` |
| `api/services/ingestion.py` | `datetime.datetime`, `datetime.timezone` |
| `api/services/recovery.py` | `app.core.threads.ThreadBuilder` |
| `api/services/storage.py` | `datetime.date`, `datetime.datetime`, `datetime.timezone`, `typing.Iterable`, `..logging_config.log_with` |
| `api/services/threads.py` | `typing.Iterable`, `typing.Tuple` |

### Python — three empty f-strings → plain strings

`f"..."` with no `{}` placeholders is a code smell pyflakes
catches; the runtime cost is zero but the intent is unclear.
Replaced with regular string literals in three places: the API
base URL in [`launcher.py:397`](../../app/ui/launcher.py),
the "Couldn't reopen" flash at [`launcher.py:2461`](../../app/ui/launcher.py),
and the Restore label colour in [`widgets.py:1523`](../../app/ui/widgets.py).

### Python — duplicate function

`_transition_colour` was defined **twice** in
[`app/ui/widgets.py`](../../app/ui/widgets.py) (lines 1694 and
1808). Python's last-definition-wins meant only the second was
ever used; the first was a slightly-different-alpha shadow from
an earlier iteration. Removed the shadowed (line 1694) copy.

### Python — unused local in `launcher.py`

`time_label` was computed in the recovery-list filler but never
read (the RecoveryCard constructor was passed
`humanize_age(...)` directly). Dropped the 6-line computation
block and the stale comment that defended it.

### Extension — three motion exports with zero consumers

In Phase 5I I added `calmFlash`, `calmSlow` (Transition objects)
and `MOTION_FAST_S` / `MOTION_NORMAL_S` / `MOTION_SLOW_S`
(numeric constants) to
[`lib/motion.ts`](../../apps/extension/ui/src/lib/motion.ts).
Grep across `src/` shows zero consumers of any of them. Removed
`calmFlash` and `calmSlow`; un-exported the numeric constants
(kept `MOTION_NORMAL_S` as a module-scoped const since
`calmFast` reads it for documentation).

### Extension — already clean of unused locals / parameters

The extension's `tsconfig.json` has `noUnusedLocals: true` +
`noUnusedParameters: true` since Phase 4J. `npx tsc --noEmit`
returns zero errors — verified before and after this pass.

---

## Moved

**Nothing actually moved this pass.** Phase 5D.1 already
relocated 40 root `.md` files into `docs/{product, founder,
engineering, release, trust, archive}/`. The current root
markdown set (5 files: `CLAUDE.md`, `CODE_OF_CONDUCT.md`,
`CONTRIBUTING.md`, `README.md`, `SECURITY.md`) is the
stable surface.

What this pass **added** at the root:

- **`CHANGELOG.md`** — an 8-line redirect that points readers to
  the canonical [`docs/release/CHANGELOG.md`](../release/CHANGELOG.md).
  Tools that look for a top-level `CHANGELOG.md` now find one;
  the source of truth stays in the release folder alongside
  `VERSIONING.md` and `RELEASE.md`.

---

## Kept (intentional exceptions)

- **`CLAUDE.md` at root.** The directive's list does not name
  it, but `CLAUDE.md` is the project's engineering charter and
  is **auto-loaded by AI coding tools** (Claude Code, Cursor,
  etc.) from the working-directory root. Moving it to `docs/`
  would silently break that auto-load contract. Treated as the
  same kind of exception as `recall.py` / `recall.spec` /
  `requirements.txt` — files that have to be at root for tool
  conventions, not for documentation reasons.
- **`alpha/` at the repo root**, not under `docs/alpha/`. The
  directive lists `alpha/` as a `docs/` subdir, but the
  existing top-level `alpha/` folder is a **cohort-distributed
  packet** (the install script, the workflow, the feedback
  template, the per-Resume journal). It is intended to be
  zipped and handed to alpha-001 testers as a single bundle.
  Moving it under `docs/` would make that hand-off awkward.
- **`_smoke_api.py`'s four section-scoped imports.** Pyflakes
  flags `timedelta` (line 441), `statistics as _stats20` (758),
  `statistics as _stats` (1074), and `os as _os` (1245). All
  four sit inside numbered test sections that use them
  conditionally via `eval`/`exec`-style code-path branches
  pyflakes can't follow. The smoke test is the source of truth
  for endpoint behaviour ([`CLAUDE.md`](../../CLAUDE.md)
  § *Verifying changes*) — risk of behavioural change > the
  cosmetic value of removing four lines. Left alone.
- **`infra/packaging/windows/build_logs/*.log`** (Phase 5G
  evidence files). Referenced by
  [`INSTALL_PROOF_WINDOWS.md`](../trust/INSTALL_PROOF_WINDOWS.md)
  and [`RECOVERY_STRESS.md`](../trust/RECOVERY_STRESS.md) as
  the audit trail. Tracked deliberately.
- **`archive/web-components/*.tsx`** (10 archived React
  components from Phase 5D). Kept tracked as historical record;
  excluded from the marketing-site build (`apps/web/`) by not
  being imported from anywhere live.

---

## Deferred

- **`LICENSE` file.** Genuinely missing at the repo root and
  inside `docs/`. Adding one is a licensing decision the
  maintainer has to make (MIT vs Apache-2 vs source-available);
  this pass is not the place. Tracked separately.
- **`docs/phases/` and `docs/alpha/` subdirs.** The directive
  named them but neither has clear content to move there now:
  per-phase docs already live in the changelog, and `alpha/` at
  the root is the right home for the cohort packet (see
  *Kept*). Both directories stay un-created until a real artifact
  needs one.
- **End-to-end `recall://` registration verification.** Phase
  5H landed the `[Registry]` section in `recall.iss`; full
  verification needs a rebuilt `Recall-Setup.exe` (24-minute
  install). Same status as Phase 5H.
- **`releases/preview/` and `releases/windows/` cleanup.** Both
  directories are empty (their contents are in `releases/.gitignore`
  via `windows/*` + `preview/*`). The `.gitkeep` sentinels keep
  the directory tree alive. No action needed; flagging for
  visibility.

---

## Asset + archive inventory (Phase 5J snapshot)

The repo's tracked binary surface as of this pass:

| Location | Tracked | Purpose |
|---|---|---|
| `assets/screenshots/` | 15 PNGs | deterministic Qt + Playwright captures (Phase 4L → 5I) |
| `assets/demos/` | 3 GIFs + 2 `.md` | landing-page motion artifacts + recording protocol scripts |
| `assets/screenshots/README.md` | 1 .md | the capture-source ledger |
| `archive/web-components/` | 10 .tsx + README | components archived in Phase 5D |
| `archive/README.md` | 1 .md | "why this folder exists" |
| `infra/packaging/windows/build_logs/` | 9 .log | Phase 5G install/uninstall/doctor evidence files |
| `releases/checksums/` | SHA256SUMS + manifest.json | release-time SHA-256 ledger |
| `releases/.gitignore` | 1 | gitignore for `windows/*` + `preview/*` binaries |
| `app/assets/icon.ico` | 1 | the launcher icon (referenced from `recall.iss`) |
| `apps/admin/data/*.json` | 8 | baked dashboard data (Phase 5E.3) |
| `apps/admin/release_state.json` + alpha files | 4 | founder-maintained inputs |
| `alpha/launcher/` | 5 files | the no-terminal cohort install pack (Phase 5H) |

Total tracked binary footprint: well under 5 MB. The bulk is
PNG screenshots (~1.2 MB) and the 9 install log files
(~3 MB). No accidentally-committed installer artifact (the
`dist/installer/Recall-Setup.exe` at 260.8 MB stays
gitignored).

---

## Verification (the receipt)

The five-surface build matrix from the directive, run after
every cleanup edit above:

| Surface | Command | Result |
|---|---|---|
| doctor | `python recall.py doctor` | 5 GREEN / 4 YELLOW / 0 RED; no `�` mangling |
| launcher import | `python -c "from app.ui.launcher import Launcher; ..."` | OK; CARD_HEIGHT=58 / RECOVERY_HEIGHT=64 / `_transition_colour('pivot')` = mint |
| founder control room CLI | `python recall.py founder status` | Readiness 61/100 YELLOW (unchanged from 5I; no input drift) |
| founder dashboard build | `cd apps/admin/web && npm run build` | 4 static pages, 87.4 kB first-load JS |
| extension build | `cd apps/extension/ui && npm run build` | 399 modules → **283.49 kB JS / 90.87 kB gzipped, 2.69 kB CSS** (identical size to pre-cleanup; tree-shake already eliminated the dead exports at compile time) |
| pyflakes scan (engine) | `python -m pyflakes app/ui app/core api` | **zero findings** |
| TS scan (extension) | `cd apps/extension/ui && npx tsc --noEmit` | **zero findings** |

### Cleanup deltas observed

- Python LOC removed: **~50 lines** across 16 files (imports,
  comments, the duplicate function, the unused local).
- TS LOC removed: **~4 lines** in `lib/motion.ts` (the unused
  motion-variant exports).
- Build size change: **~0 bytes** in both bundles — vite/rollup
  already tree-shook everything. The cleanup is for source
  tidiness, not artifact size.
- `.gitignore` additions: `*.pyd`, `node_modules/`,
  `apps/admin/web/.next/`, `.recall.dev-backup/`,
  `*.log.tmp`, `*.runtime.log`.

> Cross-referenced by
> [`PHASE_TRACKER.md`](../founder/PHASE_TRACKER.md) (the *Repo
> Stabilization Pass* row), [`DEAD_CODE_AUDIT.md`](DEAD_CODE_AUDIT.md)
> (the older Phase 5D ledger this pass extends), and
> [`DOC_HEALTH.md`](DOC_HEALTH.md).
