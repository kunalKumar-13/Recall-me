# ALPHA_MATRIX.md — the cohort install-validation matrix

The Phase 5K directive: **5 install-validation slots**, each one
a different machine — three Windows clean VMs + one Mac Intel +
one Mac Silicon. This file is the matrix; one row per validation
slot, one column per gate.

Pairs with [`CLEAN_MACHINE_RUN.md`](CLEAN_MACHINE_RUN.md) (the
Windows row's parent checklist) and
[`MAC_OWNER_NEEDED.md`](../release/MAC_OWNER_NEEDED.md) (the Mac
rows' ticket).

Honesty rule: a cell flips off `unknown` only when **a real
machine** executed the step. *"It should work"* is `unknown`;
*"the same code passes smoke on the build machine"* is `unknown`.

---

## The matrix

| # | Machine | Install time | Doctor | Extension | First capture | First recovery | Resume | Status |
|---|---|---:|---|---|---|---|---|---|
| 1 | **Windows 10 clean VM** | unknown | unknown | unknown | unknown | unknown | unknown | ⬜ awaiting maintainer |
| 2 | **Windows 11 clean VM** | unknown | unknown | unknown | unknown | unknown | unknown | ⬜ awaiting maintainer |
| 3 | **Windows 11 fresh profile** | unknown | unknown | unknown | unknown | unknown | unknown | ⬜ awaiting maintainer |
| 4 | **macOS Intel** | unknown | unknown | unknown | unknown | unknown | unknown | ⬜ awaiting maintainer + Mac |
| 5 | **macOS Apple Silicon** | unknown | unknown | unknown | unknown | unknown | unknown | ⬜ awaiting maintainer + Mac |

### Phase 6E — daily-use + browser matrix

Phase 6E adds the *daily use* dimension on Windows and a per-browser
extension row. The five clean-install slots above measure the *one-shot
first-install* path; the rows below measure the *sustained-use* path
that decides whether Recall survives past day 1. Each row is one
machine + one browser; the same tester may own several rows on the
same machine if they switch browsers across the week.

| Row | Machine | Browser | Recovery appeared? | Resume worked? | Status |
|---|---|---|---|---|---|
| 6 | **Windows 11 daily use** | Chrome | unknown | unknown | ⬜ awaiting cohort |
| 7 | **Windows 11 daily use** | Edge | unknown | unknown | ⬜ awaiting cohort |
| 8 | **Windows 11 daily use** | Arc | unknown | unknown | ⬜ awaiting cohort |
| 9 | **macOS Intel daily use** | Chrome | unknown | unknown | ⬜ awaiting maintainer + Mac |
| 10 | **macOS Apple Silicon daily use** | Chrome | unknown | unknown | ⬜ awaiting maintainer + Mac |

Daily-use cells flip off `unknown` only when a real tester has used
the machine + browser pair *for at least three days*. The bar is
deliberately higher than the clean-install row; this surface is
where a recovery actually has a chance to fire on real work.

Legend (per cell):

- **Install time** — wall-clock seconds from double-click to
  installer-finish. Target: ≤ 45 s (Phase 5J Tier A) or ≤ 30 s
  (post-Tier B). Record the actual number.
- **Doctor** — output of `recall doctor` immediately after the
  first launch. Acceptable: 3 GREEN + first-launch YELLOWs / no
  REDs.
- **Extension** — the popup state after loading the unpacked
  extension into Chrome / Edge. Acceptable: *Connected*, not
  *Recall not found*.
- **First capture** — *yes* if any event lands in the event log
  within 5 minutes of first browsing.
- **First recovery** — date the launcher shows its first
  recovery card. May be Day 2-5+ depending on persona.
- **Resume** — *yes* if clicking the recovery card actually
  reopens the relevant tabs / files.
- **Status** — overall verdict for the row.

A row is **GO** when every column is non-`unknown` and the
*Install time* + *Doctor* + *Resume* columns are passing.

---

## What ships with each validation slot

The same three artifacts in each machine's hand-off:

1. `Recall-Setup-lite.exe` (or the equivalent macOS `.dmg`)
2. The [`alpha/launcher/`](../../alpha/launcher/) pack
3. The [`alpha/users/<cohort>/`](../../alpha/users/) `TEMPLATE.md`
   that gets copied into a per-tester folder during the run

The Windows path is detailed in
[`CLEAN_MACHINE_RUN.md`](CLEAN_MACHINE_RUN.md); the Mac path is
gated by [`MAC_OWNER_NEEDED.md`](../release/MAC_OWNER_NEEDED.md).

---

## How a slot fills in

When a maintainer (Windows or Mac) walks one slot, they:

1. Boot the clean machine.
2. Copy `Recall-Setup-lite.exe` (or the Mac `.dmg`) over.
3. Run `install.ps1` from the alpha launcher pack (Windows) or
   drag `Recall.app` to `/Applications` (macOS).
4. Time the install; fill the row's *Install time* cell.
5. Open a Command Prompt / Terminal, run
   `Recall.exe doctor`; screenshot. Fill *Doctor* cell.
6. Load the browser extension (unpacked, per
   [`alpha/INSTALL.md`](../../alpha/INSTALL.md)). Fill
   *Extension* cell.
7. Browse for 2-5 minutes; check `.recall/events/` has at least
   one .jsonl. Fill *First capture* cell.
8. Use the machine normally for 2-3 days. Fill *First recovery*
   and *Resume* cells as they fire (or do not).
9. Run `recall alpha create <handle> --cohort <cohort>` and
   start a tester record (this same matrix row maps to that
   tester folder).

The matrix is editable in-place — a maintainer pulls, edits
their row, and PRs the change. Each row's history lives in the
PR; the matrix shows only the current state.

---

## What signals the matrix is meant to surface

Three things the directive specifically asked for:

| Signal | Where it shows up |
|---|---|
| Install time variance across machines | column 1; an outlier (e.g. 180 s) names a slow-disk or slow-AV problem |
| Doctor regressions on a specific platform | column 2; e.g. macOS row showing `protocol RED` would be the `recall://` registration story being macOS-specific |
| Recovery + Resume actually working on fresh installs | columns 5-6; the same data the directive's success criterion is checking against (*3 successful recoveries*) |

The matrix is **not** for marketing — every row is a real test
on a real machine. An empty matrix is the honest answer when
nothing's been tested yet, which is what this file's current
state shows.

---

## Verdict (now)

**0 of 5 install slots filled** + **0 of 5 Phase 6E daily-use rows
filled**. Every row is `unknown`. Closure depends on:

1. Slots 1-3 — a Windows VM host willing to walk
   `CLEAN_MACHINE_RUN.md` three times on three different machine
   shapes (Win 10, Win 11, and a fresh profile on a Win 11 box
   that's *had* Recall before). The Phase 5J lite installer is
   ready to be the artifact.
2. Slots 4-5 — a maintainer with macOS hardware running
   [`MAC_OWNER_NEEDED.md`](../release/MAC_OWNER_NEEDED.md)'s
   verification script on each chip class.

Until both happen the matrix stays `unknown` — and that is the
truthful current state of the cohort install path.

> Cross-referenced by
> [`PHASE_TRACKER.md`](../founder/PHASE_TRACKER.md) and
> [`OPEN_PROBLEMS.md`](../engineering/OPEN_PROBLEMS.md)
> § *External dependencies*.
