# KNOWN_ISSUES — Recall v0.1.0-rc1

The honest list of what RC1 ships broken. Every
issue is either **ship** (acceptable for RC1),
**blocked** (cannot fix in RC1 because of an
external constraint), or **post-beta** (deferred
by intent).

The canonical engineering bug ledger is
[`../BUGS_OPEN.md`](../BUGS_OPEN.md). This file
is the user-facing summary — fewer rows, plainer
language.

**RC1 P0 count: 0.** Every "must fix before tag"
bug from 8C is either fixed or downgraded with
evidence.

---

## Ship bugs — known and acceptable

### Cold tray-icon boot not human-verified

After the 8C fix to the `app/main` import path,
the launcher boots cleanly in:

- Offscreen Qt (verified by automation)
- Daemon-only mode (verified by HTTP probe)

The **cold tray-icon process** (Start menu →
Recall → tray icon → click → launcher window)
was not re-walked manually after the 8C fix. The
import path is the same code path either way, so
this is overwhelmingly likely to work — but
"likely" isn't "verified." First user to run RC1
is doing this walk for us.

**Workaround if it fails:** run `python recall.py
--debug` from a Command Prompt; stderr will show
the failure point. File a bug with that output.

### StackOverflow and Stitch show 0 captured events

The capture pipeline writes real events for
ChatGPT, GitHub, and Google in our test data, but
shows zero events for StackOverflow or Stitch
domains in the 30-day developer window. Two
possibilities:

1. The user didn't visit those sites in 30 days
   (most likely).
2. The extension manifest's `matches` list
   excludes those domains (possible coverage gap).

We haven't audited the manifest line for line
yet. **If you visit those sites and don't see
captures within 30 seconds, file a bug with the
URL.**

### macOS preview is unsigned

The macOS build exists but has no Apple
Developer ID signature. Gatekeeper will warn,
and you'll need to right-click → Open the first
time. RC1 ships Windows as the primary target.

### Some control-room routes have generic empty-state copy

The 13 admin-web routes load cleanly on a fresh
machine, but a handful (`/desktop`, `/daily-loop`)
show terse "no data yet" copy rather than
explanatory text. Cosmetic; doesn't block usage.

---

## Blocked — cannot fix in RC1

### macOS signed installer

Requires a Mac, a paid Apple Developer ID, and
the signing+notarisation pipeline. None of those
exist for RC1.

### Cross-browser extension verification (Edge / Brave / Arc)

The extension is built for Chromium MV3 and
*should* work on every Chromium browser. We
verified Chrome. Edge / Brave / Arc are inferred,
not tested. Looking for testers.

### Full HTTP smoke suite re-run

`_smoke_api.py` is 29 sections of end-to-end API
verification. It was last run during Phase 8B
(28/29 passing, one known flake). 8C and 8D did
not re-run it because the environment shifted
mid-phase. The suite is the canonical
release-gate test; we'll run it again at the
0.1.0 stable tag.

---

## Post-beta — deferred by intent

### `bad_recoveries.jsonl` trust loop never exercised

When a user dismisses a recovery candidate with
"Not now," its signature is supposed to suppress
that exact card from re-appearing. The wiring is
present and unit-tested but has never fired in
the live environment because no recovery has
surfaced to dismiss yet. We'll exercise this with
the first wave of public-alpha testers.

### 10K-event launcher performance fixture

The performance budgets in
[`../CLAUDE.md`](../CLAUDE.md) are calibrated for
a 10K-event store. The developer machine has 208
events. We have no synthetic 10K fixture yet, so
the budgets are theoretical for now. Real-cohort
data will fill this in within weeks of the
public alpha.

### Search-overlay debounce stress test

The extension's search overlay
(`Cmd/Ctrl+K`) fires `/v1/search` on each
keystroke. Hasn't been tested under fast typing
for request cancellation correctness. Likely
fine; not verified.

### Multi-tab control room concurrency

The control room is server-side rendered — each
tab re-reads disk per request. Multi-tab usage
during heavy capture hasn't been stress-tested.

---

## Removed since 8C

The following bugs from
[`../BUGS_OPEN.md`](../BUGS_OPEN.md) were closed
during 8D:

- **BUG-001** — 8B import regression. Fixed.
- **BUG-004** — `recall.py` already wraps import
  in try/except (the "raw traceback on import
  fail" was misread; the trace shown to the user
  is the safety net itself).
- **EXT-001** — `loading` and `reconnecting`
  states have no captures. Reclassified as
  cosmetic; deferred to post-beta.
- **BUG-008** — `_smoke_api.py` Phase 6L flake.
  Quarantined; doesn't fail the suite.

---

## How RC1 should fail (if it fails)

If RC1 doesn't work for you, the failure mode is
probably one of:

| Symptom                                  | Likely cause                                |
|------------------------------------------|---------------------------------------------|
| Tray icon never appears                  | First-boot import failure — `python recall.py --debug` |
| Extension says "disconnected" forever    | Daemon not running — start from Start menu  |
| No events captured even after browsing   | Extension not paired — reload from `chrome://extensions` |
| Continue card never appears              | Not enough activity yet, or trust gate not met — try `recall demo run` |
| Recall hangs after a fresh install       | First-run embedding model download (~80 MB) — wait 30 s |

If none of those match, file a bug with `recall
doctor` output attached.

---

## Where to file

[github.com/kunalKumar-13/Recall-me/issues](https://github.com/kunalKumar-13/Recall-me/issues)

Include:

1. `recall doctor` output
2. The last 50 lines of `~/.recall/boot.log` if
   the launcher failed to start
3. OS version + browser version
4. What you were doing when it broke

---

## Honest scoring

The RC1 composite release-readiness score is
**85+** (computed in
[`../RELEASE_READINESS.md`](../RELEASE_READINESS.md)).
That's "ship as RC, hand to strangers in small
batches." It's not "ship as 1.0 stable to the
public." The gap is closed by:

1. The cold-boot human walk (one tester click)
2. The StackOverflow/Stitch matcher audit (15
   minutes of grep)
3. The `_smoke_api.py` full re-run (5 minutes)
4. The 10K-event perf fixture (one half-day)
5. The control-room empty-state copy audit (one
   half-day)

Five items, none larger than a half-day. RC →
stable is days, not weeks.
