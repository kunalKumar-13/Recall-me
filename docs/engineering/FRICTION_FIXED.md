# FRICTION_FIXED.md — the running ledger of every fixed friction

A single chronological table of every friction the project has
named and shipped a fix for. Pairs with
[`OPEN_PROBLEMS.md`](OPEN_PROBLEMS.md) (still-named, still-open)
and [`FRICTION_FIXES.md`](FRICTION_FIXES.md) (the detailed
per-issue receipts from earlier passes).

The point of this file: when someone asks *"did Recall ever fix
X?"*, the answer is a single grep here. Each row has the issue,
the phase it shipped in, and a one-line description of the fix.

---

## Install / packaging

| # | Issue | Fixed in | Fix |
|---|---|---|---|
| 1 | No `Recall-Setup.exe` artifact | 5F | Inno Setup 6.7.2 installed via winget; `build.ps1` end-to-end exit 0; 260.8 MB installer |
| 2 | `build.ps1` only checked `Program Files (x86)` for ISCC | 5F | hardened to also try `${env:LOCALAPPDATA}\Programs\Inno Setup 6\` (winget per-user) |
| 3 | `recall.iss` referenced non-existent wizard BMPs | 5F | `WizardImageFile` / `WizardSmallImageFile` removed; `SetupIconFile` points at `app/assets/icon.ico` |
| 4 | `recall://` URL scheme never registered | 5H¹ | `[Registry]` section in `recall.iss`; verify-on-rebuild |
| 5 | `recall://` registration also from a running install | 5H² | `recall repair` writes the same four registry values when frozen |
| 6 | Silent install skipped the autostart task | 5G | documented `/TASKS=desktopicon,startuplaunch`; `alpha/launcher/install.ps1` uses it |
| 7 | No install-repair path other than reinstall | 5H² | `recall repair` + `recall reset` + `recall reinstall-check` |
| 8 | No glanceable "what survives a reinstall" answer | 5H² | `recall reinstall-check` prints survives / re-derived / optional-backup |

¹ first 5H iteration ("Alpha Cohorts + Friction Removal")
² this 5H iteration ("Friction Kill")

## Doctor

| # | Issue | Fixed in | Fix |
|---|---|---|---|
| 9 | cp1252 em-dash mangling (`�` chars) | 5H¹ | three user-facing strings flattened to ASCII hyphens |
| 10 | `versions` check false-fail in a frozen bundle | 5H¹ | skips manifest lookup when `sys.frozen`; returns GREEN with truthful note |
| 11 | Stale instance lock reported GREEN | 5H¹ | `_check_launcher` PID-checks the lock (cross-platform `os.kill(pid, 0)` semantics including `winerror=87` / `winerror=5`) |
| 12 | `autostart` blind to Startup-folder shortcut | 5H¹ | checks HKCU Run **OR** `Startup\Recall.lnk` |
| 13 | No installer-state check | 5F | `_check_installer_state` reports frozen-bundle / source-tree / artifact size |
| 14 | No autostart check at all | 5F | `_check_autostart` added |
| 15 | No `recall://` protocol check | 5F | `_check_protocol_registration` added |
| 16 | No extension-pairing check | 5F | `_check_extension_pairing` added |
| 17 | No engine-vs-extension version drift check | 5F | `_check_version_mismatch` added |

## Extension popup

| # | Issue | Fixed in | Fix |
|---|---|---|---|
| 18 | Popup stayed EMPTY despite captured events | 5H¹ | new `PopupState` machine + `derivePopupState`; invariant `ingestedTotal > 0 ⇒ EMPTY forbidden` |
| 19 | Hardcoded "WebSocket retry debugging" demo card | 5H¹ | removed; replaced with live event feed in `CapturingState` |
| 20 | No transition state between EMPTY and populated | 5H¹ | new `CapturingState` ("Recall is watching locally" + recent activity, max 5) |
| 21 | `Open Recall` was a dead click | 5H¹ | `openRecall()` three-rung ladder + `OpenRecallButton` (idle → trying → repair / hint cycle) |
| 22 | No glanceable counters in the popup | 5H¹ | `DebugStrip` (captured / browser / invest / recovery), hidden by default |
| 23 | DebugStrip always visible cluttered the popup | 5I | hidden by default; **Alt+D** toggles; state persists in `chrome.storage` |
| 24 | No daemon liveness signal in the header | 5H² | `DaemonPulse` breathes when connected; still when not |
| 25 | Empty state dominated the popup | 5H¹ | EMPTY surface compacted from ~360 px to ~180 px |
| 26 | No motion between popup states | 5I | `AnimatePresence mode="wait"` over Body; bodyState fade + 4 px slide |
| 27 | No design-token vocabulary | 5I | `--surface-0/1/2`, `--border-soft/strong`, `--shadow-soft/elevated`, `--motion-fast/normal/slow` in `styles.css`; same names mirrored in `app/ui/styles.py` |

## Launcher

| # | Issue | Fixed in | Fix |
|---|---|---|---|
| 28 | Card height was 54 px (below 56-64 brief) | 5I | bumped to 58 (`RecoveryCard` 64) |
| 29 | No hover lift on cards | 5I | 2 px upward translation paced over 120 ms |
| 30 | Focus ring too thin / too dim | 5I | lavender 1.6 px / 0.92 alpha |
| 31 | Recovery card had only a tiny `_StateDot` for Resume | 5I | `_ResumePill` with 220 ms slide-fade entrance |
| 32 | Hand-rolled `_HOVER_MS=120` constant in cards.py | 5I | replaced by `MOTION_FAST_MS` from `styles.py` |
| 33 | Duplicate `_transition_colour` in `widgets.py` | Repo Stabilization | shadowed line-1694 definition removed |
| 34 | Unused `time_label` local in `_fill_recovery_list` | Repo Stabilization | dropped + stale comment removed |
| 35 | First digest render flashed whole | 5H² | one-shot stagger reveal (180 ms fade × 60 ms inter-section) |

## Code hygiene

| # | Issue | Fixed in | Fix |
|---|---|---|---|
| 36 | 28 unused Python imports across 14 files | Repo Stabilization | all removed; pyflakes clean on `app/ui` + `app/core` + `api` |
| 37 | Three empty f-strings | Repo Stabilization | flattened to plain string literals |
| 38 | Two motion exports with zero consumers (`calmFlash`, `calmSlow`) | Repo Stabilization | removed; numeric `MOTION_*_S` un-exported |
| 39 | No root `CHANGELOG.md` | Repo Stabilization | 8-line redirect to `docs/release/CHANGELOG.md` |
| 40 | `.gitignore` missed common patterns | Repo Stabilization | added `*.pyd`, `node_modules/`, `.next/`, `.recall.dev-backup/`, `*.runtime.log` |

---

## Counts

- **Install / packaging:** 8 items fixed
- **Doctor:** 9 items fixed
- **Extension:** 10 items fixed
- **Launcher:** 8 items fixed
- **Code hygiene:** 5 items fixed
- **Total:** **40 named frictions fixed** across Phase 5F → this
  iteration of Phase 5H.

The directive's "fix every remaining friction" goal is honoured
in the literal-grep sense: the items listed in the *Friction Kill*
brief that were *not* in [`OPEN_PROBLEMS.md`](OPEN_PROBLEMS.md)
either pre-shipped (see *What this iteration did not ship* in
[`PHASE_5H_STATUS.md`](PHASE_5H_STATUS.md)) or shipped here.

The directive's *< 60 s install* target is the one
quantitative goal that did **not** shift this iteration —
install_repair touches install correctness, not wall-clock; the
honest path to < 60 s is the bundle-shrinkage work in
[`INSTALL_SIZE_AUDIT.md`](INSTALL_SIZE_AUDIT.md). Tracked in
[`OPEN_PROBLEMS.md`](OPEN_PROBLEMS.md) under *Performance*.

> Cross-referenced by [`OPEN_PROBLEMS.md`](OPEN_PROBLEMS.md),
> [`PHASE_TRACKER.md`](../founder/PHASE_TRACKER.md), and the
> phase-specific receipts in [`FRICTION_FIXES.md`](FRICTION_FIXES.md).
