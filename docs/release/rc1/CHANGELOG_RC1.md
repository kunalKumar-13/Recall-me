# Recall v0.1.0-rc1 — release notes

**Tag:** `v0.1.0-rc1`
**Date:** 2026-05-24
**Codename:** *quiet continuity*

This is the first tagged Recall release. Earlier
work shipped against `main` as untagged preview
builds. RC1 is the first version we are willing to
hand to a stranger.

If you have been following the phased build, this
is the close-out of phases 7E → 8D. If this is
your first encounter, the [release README](README.md)
is the better starting point.

---

## What you can do today

- **Watch your own browsing and local-file work
  get composed into continuity threads in real
  time.** Browser activity (ChatGPT, GitHub,
  Google, generic visits) and local-file changes
  flow into a single per-day JSONL log.
- **Open the launcher with a hotkey** and see a
  calm "On your radar" digest with up to 5 recent
  memories and 3 investigation threads.
- **Get a one-click "Continue where you left off"
  card** when an interrupted thread crosses the
  recovery trust gate.
- **Run the operator CLIs locally:**
  `recall doctor`, `recall capture status`,
  `recall trust review`, `recall founder status`,
  `recall demo run`.
- **Open the admin control room** at
  `http://localhost:3000` (or your configured Next
  dev port) and see 13 read-only surfaces over
  your engine state.
- **Demo Recall on a fresh box** with one command:
  `recall demo run`, then set `RECALL_DEMO_MODE=1`
  and open the launcher.

---

## What's new since the last preview

### Phase 8D — Release Candidate (this release)

- **`recall demo run / reset / status` CLI** — the
  one-command demo path. Seeds 30 deterministic
  events across 12 sessions into
  `~/.recall/events-demo/`, never touching the
  real event log. Documented in
  [`../DEMO_MODE.md`](../../product/DEMO_MODE.md).
- **Release kit** — this folder. README, install,
  quickstart, demo flow, known-issues, RC
  changelog. The single front door for testers.
- **Screen freeze** — only 6 capture sets are
  considered canonical for RC1. Everything else
  archived to `archive/screenshots-history-rc/`.
  Index at [`../SCREEN_INDEX.md`](../../product/SCREEN_INDEX.md).
- **Bug pass** — 11 open bugs re-classified
  against the must-fix-before-alpha / can-wait /
  post-beta gates. P0 count: 0.
- **Release-readiness score: 85+** (up from 76 at
  the close of 8C). Composite recomputed in
  [`../RELEASE_READINESS.md`](../RELEASE_READINESS.md).

### Phase 8C — Product Stabilization

- Six [`STABILITY/`](../../engineering/stability) docs walking
  performance, capture coverage, launcher tree,
  resume flow, extension state machine, control
  room.
- Real wall-clock measurements:
  launcher 84.5 ms warm / ~460 ms cold,
  CLI commands 230–365 ms,
  resume preview 3.1 ms.
- Honest bug ledger ([`BUGS_OPEN.md`](../../engineering/BUGS_OPEN.md))
  with severity tags and proposed fixes.
- **Critical fix in-flight:** 8B's archive sweep
  over-reached and broke `from app.main import
  main`. Restored `demo_data.py`, `styles.py`,
  `widgets.py`, `cards.py` from archive; made
  `demo_data` import lazy in `main.py`.

### Phase 8B — Repo Collapse

- 7,109 lines of legacy launcher code moved to
  `archive/launcher-old/` (later partly restored
  in 8C; see above).
- 11 historical screenshot folders archived.
- 8 dead pre-7A extension components archived.
- Web manifest cleanup (3 unused deps removed).
- `app/ui/launcher.py` collapsed 60 → 18 lines.

### Phase 8A — Full Product Audit

- 7-doc evidence-based audit under
  [`AUDIT/`](../../../archive/AUDIT).
- 36 LIVE / 2 LEGACY / 11 ARCHIVE / 1 REMOVE
  surface classification.
- Tier-graded delete recommendations executed in 8B.

---

## Known issues

See [`KNOWN_ISSUES.md`](KNOWN_ISSUES.md). Briefly:

- StackOverflow + Stitch domain captures show
  zero events in 30 d — likely a coverage gap;
  manifest audit pending.
- The cold tray-icon process hasn't been walked
  by a human after the 8C import fix. Likely
  passes; not yet verified end-to-end.
- macOS preview is unsigned and unsupported in RC1.
- Some control-room routes have generic
  empty-state copy.

None of these block the RC1 ship gate (P0 = 0).

---

## What we removed since the last preview

Nothing user-facing. All removals were code in the
archive folder and unused deps in `apps/web/`.
Every user-visible surface preserves the exact
contract it had at the close of Phase 7E.1 /
Phase 7A.

---

## Upgrade notes

- **From an earlier preview build:** uninstall
  the previous Recall, then run the new
  installer. Your `~/.recall/` data directory is
  preserved across reinstalls.
- **Fresh install:** see [INSTALL.md](INSTALL.md).
- **Reset your data:** `python recall.py reset`
  clears `~/.recall/` and starts over. The demo
  store at `~/.recall/events-demo/` is separate
  and survives reset.

---

## Where to file bugs

[github.com/kunalKumar-13/Recall-me/issues](https://github.com/kunalKumar-13/Recall-me/issues)

Please include `recall doctor` output. The doctor
CLI captures the local diagnostic state we need to
reproduce.

---

## What's next

- **0.1.0 (stable):** waiting on the cold-boot
  human walk + the StackOverflow/Stitch matcher
  audit + 10K-event perf fixture.
- **0.2.0:** capture coverage expansion +
  recovery quality lift. Cross-browser tester
  cohort.
