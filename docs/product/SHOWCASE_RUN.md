# Showcase Run — Phase 6P

A scripted end-to-end Resume verification against the canonical
WebSocket recovery story. Anyone evaluating Recall should be able
to run this from a clean repo and watch the launcher actually
re-open the work.

> **Success criterion:** click Resume → 5 OS opens happen in
> the right order → toast names 3 of them → launcher hides.
> No tracebacks. No silent close. No surprises.

---

## Scenario: WebSocket retry debugging

The recovery card surfaces:

| Field        | Value                                              |
|--------------|----------------------------------------------------|
| Title        | WebSocket retry debugging                          |
| Meta         | 2 tabs · 2 files · reopened after a 2-day gap      |
| Confidence   | high (4+ targets)                                  |
| Targets      | `backoff.py`, `client.py`, MDN, StackOverflow, Google search |

This is the demo payload (`app/core/demo_mode.py:_RECOVERY`), so
the scenario is reproducible without any captured events.

---

## Steps

1. **Boot the daemon.**

   ```powershell
   python recall.py
   ```

   Confirm the api logs `recall.api.app api.service.start`.

2. **Open the launcher.**

   ```powershell
   # Global hotkey, or:
   python recall.py launcher
   ```

   Click *Show example* on the empty surface. The launcher
   should swap to the demo digest:

   ```
   CONTINUE
     WebSocket retry debugging          [ Resume ]
     2 tabs · 2 files · reopened after a 2-day gap

   OTHER WORK
     WebSocket | Healthcare proposal | RLHF
   ```

3. **Close every related app** (browser tabs, editor files) so
   the restore has a clean room to re-fill.

4. **Click Resume.** The preview overlay should appear inside
   the launcher window:

   ```
   CONTINUE
     WebSocket retry debugging

   Will reopen
     · 2 files
     · 2 tabs
     · 1 search

       [ Cancel ]      [ Resume now ]
   ```

5. **Click Resume now.** Five OS opens should fire in this order:

   | # | Kind  | Target                                              |
   |---|-------|-----------------------------------------------------|
   | 1 | file  | `~/code/ws-retry/backoff.py`                        |
   | 2 | file  | `~/code/ws-retry/client.py`                         |
   | 3 | tab   | MDN — WebSocket                                     |
   | 4 | tab   | StackOverflow — retry on disconnect                 |
   | 5 | search| google.com/search?q=websocket+backoff+jitter        |

   Order rule (from `RecoveryEngine.plan_for`): files → chats →
   tabs → searches.

6. **Toast appears at the bottom of the launcher** for 3 s:

   ```
   Restored · backoff.py · client.py · developer.mozilla.org
   ```

   (The toast caps at 3 names. The remaining 2 opens still
   happened — the toast is a sample, not a transcript.)

7. **Launcher hides** ~400 ms after the toast. The user is now
   in the editor (or the browser) — the launcher should not
   be on top.

---

## Verification matrix

| What                                         | Expected                  | Where                          |
|----------------------------------------------|---------------------------|--------------------------------|
| Preview appears on Resume click              | yes                       | overlay paints on top of card  |
| Preview lists files/tabs/searches            | yes                       | classified by `_classify_counts` |
| Cancel closes preview, fires no opens        | yes                       | `_on_preview_cancel`           |
| Resume now opens files first                 | `backoff.py` before MDN   | `RecoveryEngine.plan_for`      |
| Missing file is skipped, not fatal           | other targets still open  | `_on_preview_accept` skip path |
| Daemon down → toast "Could not reach"        | calm copy, no traceback   | `api_client.recovery_restore` returns `None` |
| Toast shows 3 target names                   | yes                       | `RestoreToast.flash_success`   |
| Launcher hides after ~400 ms                 | yes                       | `QTimer.singleShot(400, ...)`  |

---

## Failure injection

Simulate the failure modes deliberately to confirm none of them
crash the launcher.

### Daemon down

```powershell
# kill the api process, then click Resume
```

Expected: preview opens (it doesn't need the API to render —
targets are already in hand). Click Resume now → toast reads
*Could not reach the engine · try again*. Launcher stays open.

### Missing files

Delete `~/code/ws-retry/backoff.py` before clicking Resume now.

Expected: skip count is 1, tabs + the other file still open,
toast reads *Restored 4 of 5 · client.py · developer.mozilla.org
· stackoverflow.com · 1 missing*.

### All targets missing

Delete the whole `~/code/ws-retry/` folder + disconnect from
the network so URL opens fail. (In practice URLs always "open"
because the OS hands them to the browser; this is a manual
contrived case.)

Expected: toast reads *Could not reopen 5 items · Continue
anyway*. Launcher stays open.

---

## What this proves

- Click Resume → real OS opens, not a network call into the void.
- The order is the document's order, not a roulette.
- A missing file is a one-line toast, not a modal.
- The user is never blocked.

Run this every release. Anywhere it diverges from the matrix
above is a regression.
