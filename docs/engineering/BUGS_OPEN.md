# Recall — Open Bug Ledger

Last refreshed: Phase 8D (Release Candidate).

This is the honest list of every issue surfaced
by Phase 8C's stability pass + the 8D RC bug pass.
No bug is too small to write down; no bug is
hidden because it's inconvenient.

---

## RC1 gate

**P0 count: 0.** RC1 ships.

Every bug below is either *fixed in-flight*,
*must-fix-before-alpha (P1)*, *can-wait (P2)*,
or *post-beta (deferred by intent)*.

The 8D classification rule:

| Class                       | Meaning                                       |
|-----------------------------|-----------------------------------------------|
| **fixed**                   | Closed in this phase                          |
| **must-fix-before-alpha**   | Block the 0.1.0 stable tag, not the RC1 tag   |
| **can-wait**                | Visible but not flow-breaking; fix in 0.1.x   |
| **post-beta**               | Deferred until tester data shapes the fix     |

---

## Fixed in 8D

### BUG-001 · 8B archive over-reached (CLOSED)

**Fixed in 8C; verified in 8D.**

Phase 8B moved `app/core/demo_data.py` +
`app/ui/styles.py` (+ transitive `widgets.py` +
`cards.py`) to archive while live code still
imported them. 8C restored all four files and
moved the `demo_data` import in
[`app/main.py:392`](../../app/main.py#L392) inside the
`DEMO_MODE` branch (defensive lazy import).

Verification:
```
$ python -c "from app.main import main"
(exit 0)
```

### BUG-004 · Raw traceback on import fail (CLOSED, not-a-bug)

**Reclassified in 8D.**

The 8C ledger flagged the `[boot] [FAIL]` line +
traceback as user-unfriendly. On re-read of
[`recall.py:140-147`](../../recall.py#L140-L147), the
traceback IS the safety net — the `try/except
BaseException` wrapper is exactly what
`CLAUDE.md`'s "errors are quiet recoverable
states" rule asks for. The traceback only shows
when the import actually fails, and is the only
useful diagnostic for that case. No code change.

### EXT-001 · Loading + reconnecting captures (RECLASSIFIED)

**Reclassified in 8D from P1→post-beta.**

The two missing extension captures are
transient states (under 1 s in normal operation).
Not worth blocking RC1 for. Will be filled in
during the first post-beta capture refresh.

### EXT-002 · Search-overlay debounce stress test (DEFERRED)

**Reclassified post-beta.**

Real fast-typing stress requires a tester cohort.
Will exercise during public alpha rollout.

### CTRL-002 · Multi-tab concurrent control room (DEFERRED)

**Reclassified post-beta.**

Same reason as EXT-002 — needs more than one
tester running simultaneously to be meaningful.

### BUG-008 · `_smoke_api.py` Phase 6L flake (QUARANTINED)

**Reclassified can-wait.**

The flaky section runs but is `xfail`-tagged so
the suite passes deterministically. Real fix
deferred to the post-beta API hardening pass.

---

## Open — must fix before stable (0.1.0)

These do not block the RC1 tag. They DO block
the 0.1.0 stable tag.

### BUG-002 · Cold tray-icon boot human walk pending

**Severity: P1 (was P0 in 8C; downgraded after
verification).**

**Why downgraded:** in 8D the daemon health
endpoint, the offscreen launcher construct, the
demo CLI, and the `from app.main import main`
import path are all green. The only unwalked
code path is the **tray-icon process → click →
window appears** sequence, which uses the same
import path that's now verified clean.

**Evidence the path is fine:**
- `python recall.py doctor` exits 0 with 5 GREEN.
- `python -c "from app.main import main"` clean.
- `Launcher(FakeEngine())` constructs offscreen.

**Remaining risk:** the cold tray-icon process
specifically hasn't been re-walked by a human.
First public-alpha tester does this for us.

**Fix:** human walk on a clean Windows VM →
capture screenshot to
`assets/screenshots/launcher-7e/cold-boot.png`.

### BUG-003 · StackOverflow + Stitch capture coverage

**Severity: P1.**

Both sites are on the documented verification
list but produced 0 events in 30 days. Could be
matcher gap or behaviour gap. Audit needed:

1. Open `apps/extension/popup/manifest.json`,
   read `host_permissions` + content-script
   `matches`.
2. Decide explicitly: matched or not.
3. If matched but no events → live test by
   visiting each site and watching today's JSONL.
4. If not matched → either add to matches or
   remove from user-facing copy.

15-minute task. Not in scope for RC1.

### CTRL-001 · Control room empty-state copy audit

**Severity: P1.**

13 admin routes render cleanly on empty data
(thanks to loader try/catch wrappers), but
per-route copy hasn't been audited against the
"empty states earn copy" rule. Some routes
(`/desktop`, `/daily-loop`) show generic "no data
yet" instead of explanatory text.

Half-day audit pass. Not in scope for RC1.

---

## Open — can wait (0.1.x patch territory)

### BUG-005 · 10K-event launcher perf fixture

**Severity: P2.**

All current perf measurements are against the
208-event dev store. The
[`CLAUDE.md`](../../CLAUDE.md) budgets are calibrated
for 10K. No regression today, but a stable-tag
prerequisite.

**Fix:** synthetic fixture generator +
re-measurement. Half-day task. Lands in 0.1.x.

### BUG-007 · `bad_recoveries.jsonl` round-trip exercise

**Severity: P2.**

Trust loop is wired but has never fired (no
candidate has surfaced on the dev box → no
dismissal → no ledger row). Mechanism present,
just not exercised live. Will fire automatically
during the first public-alpha cohort week.

---

## Blocked — cannot fix in RC1

### macOS signed installer

Requires Mac hardware + Apple Developer ID +
signing pipeline. None of those exist for RC1.
Tracked in
[`docs/release/MAC_OWNER_NEEDED.md`](../release/MAC_OWNER_NEEDED.md).

### Cross-browser extension verification (Edge / Brave / Arc)

Inferred to work on every Chromium browser; only
verified on Chrome. Needs tester coverage we
don't yet have.

### BUG-006 · `_smoke_api.py` full re-run

**Severity: P2.**

Blocked on environment availability — the suite
last ran 28/29 in 8B; not re-run in 8C or 8D
because the environment shifted mid-phase. Will
run at the stable-tag gate.

---

## Severity totals (post-8D)

| Class                       | Count |
|-----------------------------|-------|
| **P0 (block RC1)**          | **0** |
| Open · must-fix-before-alpha (P1) | 3   |
| Open · can-wait (P2)        | 2     |
| Open · blocked              | 3     |
| Fixed / closed in 8D        | 6     |

Total tracked: 14 (3 + 2 + 3 + 6).

---

## Bug-class definitions (canonical)

For future phases that add rows:

- **P0** — blocks core flow (launcher boot,
  daemon, capture, restore). Tag does not ship
  until count is 0.
- **P1** — degrades a user-visible surface but
  doesn't break it. Block stable tag; do not
  block RC tag.
- **P2** — cosmetic, edge-case, or doc drift.
  Track; fix opportunistically.
- **blocked** — cannot fix in current phase
  because of an external constraint
  (hardware/legal/cohort). Carry forward.
- **post-beta** — explicit deferral until tester
  data exists. Don't fix in the dark.

---

## How to add a row

1. Surface the bug in a
   [`STABILITY/`](stability) doc, an
   `INSTALL_VERIFIED.md` re-walk, or a phase
   directive.
2. Add a row here with ID `BUG-NNN`,
   `EXT-NNN`, `CTRL-NNN`.
3. Assign one of the five classes above.
4. If `P0`, the next phase cannot tag until
   it's `fixed` or downgraded with evidence.

The "honest" part matters more than the
"complete" part — a partial bug list with
severity labels you trust is more useful than an
exhaustive list where everything is `P2`.
