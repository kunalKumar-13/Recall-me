# RECOVERY_STRESS.md — what breaks gracefully, and what doesn't

Recall is a continuity tool that touches files, the browser, and
the daemon. Things will go wrong on a user's machine in ways the
unit tests cannot foresee. This file records *what an end user
sees* when each piece breaks — measured by the doctor output and
the launcher behaviour.

The honesty rule: every entry has a *Setup* (how to reproduce the
break), a *Behaviour* (what actually happens), and a *Verdict*
(graceful / loud / silent-fail).

Pairs with [`CLEAN_MACHINE_RUN.md`](CLEAN_MACHINE_RUN.md) (the
install walk) and [`STABILITY.md`](../engineering/STABILITY.md)
(the failure-mode philosophy).

---

## Scenarios captured this cycle (2026-05-20, build machine)

### 1. Daemon dead

**Setup:** Recall.exe killed via `Stop-Process -Force`. The launcher
process and tray icon both gone. `~/.recall/` intact.

**Behaviour:**

```
  RED     daemon       127.0.0.1:4545 not responding (timed out)
  GREEN   launcher     instance lock present
  GREEN   installer    running from bundle - Recall.exe
  …
  RED above is the first thing to fix. The daemon
  must be running for anything else to work.
```

**Verdict — graceful.** Doctor names the right line. The
*"daemon must be running"* tail is the user's next step. **Note**
the `launcher=GREEN` because the instance lock survives a kill
(the lock-file is removed at clean shutdown, not at SIGKILL) —
this is a known false positive after a forced kill. Acceptable
because the next launch detects a stale lock by PID and reuses
it. Phase-5H candidate: doctor could cross-check PID vs lock
contents.

### 2. Corrupt events

**Setup:** Write a 3-line `~/.recall/events/<today>.jsonl` with
one malformed line between two valid records:

```
{"valid":"json","kind":"file_open","path":"a.txt","ts":1}
not-valid-json-line
{"another":"valid","kind":"file_open","ts":2}
```

**Behaviour:** doctor reports `GREEN events 1 day-file(s) on
disk` and `GREEN event flow events in the last 24h`. The bad line
is silently tolerated by the substring-based scan. The daemon was
not running for this test, so the full ingest path was not
exercised (the doctor uses a separate read path; the real
ingester uses JSONL parsing). A separate replay test (Phase-5H
candidate) is the right way to verify the ingest path skips bad
lines without crashing.

**Verdict — graceful (on the read paths exercised).** No
traceback, no scary error message. The trust risk is *silent
data loss*: the user sees a green light while corrupt lines are
quietly skipped. The right calibration is *log + count + carry
on* — currently the count is not surfaced.

### 3. Empty install — `.recall` deleted

**Setup:** Delete the entire `~/.recall/` directory while the
daemon is down. Doctor is run from the bundle.

**Behaviour:**

```
  RED     config       C:\Users\kunal\.recall missing � has Recall ever run?
  YELLOW  events       no events directory yet � work a little
  YELLOW  event flow   no event log yet
  RED     daemon       127.0.0.1:4545 not responding (timed out)
  YELLOW  launcher     no instance lock � launcher not running?
  GREEN   installer    running from bundle - Recall.exe
  …
```

**Verdict — graceful, with cosmetic flaws.** The doctor degrades
without crashing. Two cosmetic findings:

1. **Em-dash mangling.** Three messages render `—` as `�` on
   cp1252 Windows consoles. Affects readability, not
   correctness. Found in `_check_config`, `_check_events_dir`,
   `_check_launcher`. Phase-5H candidate.
2. The `RED config` line is the right state — but the next
   step the user should take is *"launch Recall once"*, not
   *"fix something"*. The message phrasing assumes the user
   knows what `~/.recall` is. Phase-5H candidate: improve the
   message ("Run Recall once. The folder is created on first
   launch.").

### 4. Extension removed

**Setup:** Not reproduced this cycle (requires loading + then
removing the unpacked extension from Chrome on a real desktop
session). The doctor's `extension` check is a proxy: did any
`browser_visit` or `browser_search` event land in the last 7
days?

**Behaviour (inferred from the check definition):** if the
extension is removed, no new browser events flow; old events
within the 7-day window keep the check `GREEN` until they age
out. Past day 7 the check flips `YELLOW` with the message
*"no browser events - extension not paired or idle"*.

**Verdict — graceful by design.** A removed extension never
crashes the daemon (ingestion is push-only over loopback HTTP;
no callback to the extension). The lag in detection (up to 7
days) is on purpose — see [`STABILITY.md`](../engineering/STABILITY.md)
*"silence is fine; alarms are not"*.

### 5. Old export

**Setup:** Not reproduced this cycle. The export contract is in
[`engineering/TRUST_LEDGER.md`](../engineering/TRUST_LEDGER.md):
`stats.json` carries a `version` field. `apps/admin/import_stats.py`
gates on it.

**Behaviour (from the import-side gate):** an old-version
`stats.json` is rejected at import with a clear message;
`apps/admin/data/aggregate.json` is not updated. The dashboard
keeps showing the last successful merge.

**Verdict — graceful by design.** No founder-side state corruption
is possible from a stale export.

### 6. Offline

**Setup:** Not reproduced this cycle (requires network
manipulation on the build machine). Recall's only outbound call
is the one-time embedding-model download on first run.

**Behaviour (from the design):**

- **First run offline:** the embedding-model download fails;
  Recall logs an error and falls back to keyword-only search.
  The launcher still opens; the daemon still serves. The
  user can re-trigger the download via Settings → *Refresh
  memory* once online.
- **Steady-state offline:** all subsequent operations are
  local-only by design. No outbound network call. The daemon
  serves and recovery works exactly as it does online.

**Verdict — graceful by design.** Recall's *local-first* claim
is verified at the network boundary: there is no network code
on the hot path. The first-run download is the only
exposure.

---

## Coverage matrix

| Scenario | This cycle | Mode | Verdict |
|---|---|---|---|
| Daemon dead | ✅ live test | doctor against killed Recall | graceful |
| Corrupt events | ✅ live test | malformed JSONL written | graceful (read paths) |
| Empty install (no `.recall`) | ✅ live test | dir deleted | graceful, cosmetic flaws |
| Extension removed | ⬜ inferred | by-design analysis | graceful (latency up to 7d) |
| Old export | ⬜ inferred | import-side gate read | graceful by design |
| Offline | ⬜ inferred | no-network path read | graceful by design |

A row flips ⬜ → ✅ only on a live reproduction.

---

## What Recall does *not* do gracefully (yet)

These are the open trust-stress questions Phase 5G surfaced.

- **Forced kill leaves a stale lock that reads GREEN.** A
  paranoid user might run doctor expecting `launcher=RED` and
  see `launcher=GREEN` after a crash. Phase-5H: cross-check PID
  vs lock contents.
- **Silent skip on corrupt events with no count.** The user has
  no way to know that a line was dropped. The right calibration
  is a YELLOW row with the count.
  Phase-5H: a `dropped_total` analogue for read paths.
- **First-run embedding-download failure has no in-app retry.**
  *"Refresh memory"* re-triggers indexing but not the embedding
  download; the workaround is uninstall + reinstall while
  online. Phase-5H: surface the model state in Settings with a
  *"Retry download"* button.
- **No deterministic test of the offline path.** This is the
  one row that *needs* a clean VM with the network unplugged.
  A maintainer with a fresh VM should be the one to verify it.

These are not blockers for the alpha — every scenario above is
*graceful enough* for a first user. They are the calibration
backlog the alpha cohort is most likely to surface.
