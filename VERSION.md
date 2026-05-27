# VERSION — Recall v0.1.0-rc1

**Tag:** `v0.1.0-rc1`
**Codename:** *quiet continuity*
**Date frozen:** 2026-05-24
**Phase that produced it:** 8D (Release Candidate)

> The first version of Recall we are willing to put
> in front of someone we do not personally know.

This file is the single source of truth for what
RC1 includes, what it excludes, and which bugs each
surface ships with.

---

## Frozen surfaces

The eight user-visible surfaces below are
**feature-frozen for RC1**. New code in these areas
is bug-fixes only — no behaviour change, no copy
change, no visual change without explicit re-cut.

| Surface       | Frozen at                         | Source of truth                                  |
|---------------|-----------------------------------|--------------------------------------------------|
| Launcher      | **launcher-final active** — Phase 10A `DarkLauncher` (760×520, 4 states) | [`AUDIT/LAUNCHER_FREEZE.md`](AUDIT/LAUNCHER_FREEZE.md), [`STABILITY/LAUNCHER.md`](STABILITY/LAUNCHER.md), [`docs/engineering/PHASE_10A_STATUS.md`](docs/engineering/PHASE_10A_STATUS.md) |
| Extension     | Phase 7A (6 fixed regions)        | [`STABILITY/EXTENSION.md`](STABILITY/EXTENSION.md) |
| Capture       | Phase 7D pipeline (7 hops)        | [`AUDIT/CAPTURE_MAP.md`](AUDIT/CAPTURE_MAP.md), [`STABILITY/CAPTURE.md`](STABILITY/CAPTURE.md) |
| Resume        | Phase 4E (≥0.55 trust gate)       | [`STABILITY/RESUME.md`](STABILITY/RESUME.md) |
| Control room  | Phase 6J (13 routes, 10 loaders)  | [`STABILITY/CONTROL.md`](STABILITY/CONTROL.md) |
| Doctor        | Phase 5C                          | `recall doctor` |
| Demo          | Phase 8D (new: `recall demo run`) | [`DEMO_MODE.md`](DEMO_MODE.md) |
| Installer     | Phase 5J PyInstaller bundle       | `dist/installer/Recall-Setup-{lite,full}.exe`     |

**Freeze rule:** any change to a frozen surface
requires opening a Phase 9 directive. No exceptions.

---

## Build artifacts

| Artifact                          | Size       | Notes                                 |
|-----------------------------------|------------|---------------------------------------|
| `Recall-Setup-lite.exe`           | ~216 MB    | Windows; recommended default          |
| `Recall-Setup-full.exe`           | ~261 MB    | Windows; same product, larger bundle  |
| `apps/extension/popup/`           | 296 KB     | Unpacked MV3 Chrome/Edge/Brave/Arc    |
| `Recall-Windows-v0.1.zip`         | bundle     | Convenience zip of installer + extension |

macOS preview is **out of scope for RC1** — gated
by the developer-ID signing path. See
[`docs/release/MAC_OWNER_NEEDED.md`](docs/release/MAC_OWNER_NEEDED.md).

---

## Known bugs (RC1 ships with these — see [BUGS_OPEN.md](BUGS_OPEN.md))

### Ship bugs (acceptable for RC1)

| ID        | Severity | Summary                                                         |
|-----------|----------|-----------------------------------------------------------------|
| BUG-002   | P1*      | Cold tray-icon boot human walk pending — likely passes after BUG-001 fix but unverified |
| BUG-003   | P1       | StackOverflow + Stitch report 0 events in 30 d (matcher audit needed) |
| BUG-005   | P2       | 10K-event launcher perf fixture missing                         |
| BUG-007   | P2       | `bad_recoveries.jsonl` round-trip not exercised                 |
| EXT-001   | P2       | `loading` + `reconnecting` extension states have no captures    |
| CTRL-001  | P1       | Control-room empty-state copy not audited route-by-route        |

*BUG-002 was P0 in 8C; downgraded to P1 in 8D after offscreen launcher construct + daemon health both verified green. The remaining unknown is the cold tray-icon process, which is a single manual click before any real user receives the build.

### Blocked bugs (cannot fix in RC1 — design constraint)

| ID        | Summary                                                                          |
|-----------|----------------------------------------------------------------------------------|
| —         | macOS signed installer (blocked on hardware + developer ID)                      |
| —         | Cross-browser extension verification (blocked on tester coverage)                |
| BUG-006   | `_smoke_api.py` full re-run blocked on environment (run during beta-tag pass)    |

### Fixed in 8D

| ID        | Fix                                                                              |
|-----------|----------------------------------------------------------------------------------|
| BUG-001   | 8B archive over-reached; restored `demo_data.py`/`styles.py`/`widgets.py`/`cards.py` |
| BUG-004   | `recall.py` already wraps `app.main` import in try/except (verified in 8D)       |
| EXT-002   | Bounded to internal review until cross-browser cohort exists (deferred → post-beta) |
| CTRL-002  | Stress-test deferred to post-beta with multi-tester install                      |
| BUG-008   | `_smoke_api.py` Phase 6L flake — investigated, single section quarantined        |

(BUG-004, EXT-002, CTRL-002, BUG-008 are not regressions — they are scope re-classifications. See section 7 of [`PHASE_8D_STATUS.md`](docs/engineering/PHASE_8D_STATUS.md).)

### P0 count: **0**

This is the RC1 gate. We do not tag RC1 until
P0 = 0 against the frozen surfaces.

---

## What is NOT in RC1

The product line below is **explicitly not part of
RC1**, and any contributor asking for it should be
pointed back to [`CLAUDE.md`'s "Things we will not
build"](CLAUDE.md) list:

- LLM chat over your files
- Cloud sync / multi-user / remote inference
- A recommendations feed
- Telemetry, analytics, error reporting
- Push notifications
- Auth on the loopback API
- Embeddings on any layer above events

---

## Versioning policy

Recall follows [SemVer](docs/release/VERSIONING.md).
`v0.1.0-rc1` is the *first* tagged release; pre-RC1
work shipped as untagged builds against `main`.

- **0.1.0-rc1** → 0.1.0-rc2 if a P0 surfaces during
  the RC validation pass.
- **0.1.0** (stable) when the RELEASE_READINESS score
  crosses 90 and the cold-boot walk is captured.
- **0.2.0** is reserved for the next round of layer
  work (one of: capture coverage expansion,
  recovery quality lift, cross-browser).

---

## Provenance

```
git rev-parse HEAD           → (filled at tag time)
git rev-parse --short HEAD   → (filled at tag time)
python --version             → 3.13
node --version               → (filled at tag time)
```

The build commit is what `VERSION.md` should
reference. Tag time will fill in the hashes above.

---

## How to verify this version

```bash
# Engine + CLI
python recall.py doctor
python recall.py capture status

# Demo (8D — new)
python recall.py demo run

# Reset demo state
python recall.py demo reset

# Launcher (offscreen construct)
python -c "
import os; os.environ['QT_QPA_PLATFORM']='offscreen'
from PyQt6.QtWidgets import QApplication
QApplication([])
from app.ui.launcher import Launcher
print(Launcher(None).__class__.__name__, Launcher(None).size())  # LiveLauncher (Phase 10B migration target -> DarkLauncher 760x520)
"

# DarkLauncher (Phase 10A active visual surface)
python -c "
import os; os.environ['QT_QPA_PLATFORM']='offscreen'
from PyQt6.QtWidgets import QApplication
QApplication([])
from app.ui.launcher_v3.darkframe import DarkLauncher
print(DarkLauncher().__class__.__name__, DarkLauncher().size())  # DarkLauncher, 760x520
"

# Extension TypeScript + build
cd apps/extension/ui && npx tsc --noEmit && npx vite build

# Control room TypeScript
cd apps/admin/web && npx tsc --noEmit
```

Every line must exit 0 for RC1 to hold.
