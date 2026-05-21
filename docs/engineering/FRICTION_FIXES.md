# FRICTION_FIXES.md — what Phase 5G found, what Phase 5H closed

Phase 5G's clean-machine run surfaced **eleven** real friction
points. Six were code; five were UX. Phase 5H closed all eleven
without expanding the engine or adding new memory systems — every
fix is local, reversible, and ships in the next build.

Each entry below has the same four lines:

- **Issue** — what a user actually sees go wrong.
- **Root cause** — why it happens, in one sentence.
- **Fix** — the change that closes it, with the file + handle.
- **Verification** — how a later reader can re-prove the fix.

---

## Doctor — cp1252 em-dash mangling

**Issue.** Three doctor status lines render `—` (em-dash) as `�`
on a default Windows Command Prompt (cp1252).

**Root cause.** [`app/core/doctor.py`](../../app/core/doctor.py)'s
own header sets the rule *"ASCII so Windows cp1252 consoles never
crash printing them"*, but three user-facing strings inside the
checks slipped past the rule.

**Fix.** Replace the three em-dashes with plain hyphens. Comments
and the module docstring keep the em-dash (they are never printed
to a console).

```diff
- f"{CONFIG_DIR} missing — has Recall ever run?"
+ f"{CONFIG_DIR} missing - has Recall ever run?"
- "no events directory yet — work a little"
+ "no events directory yet - work a little"
- "no instance lock — launcher not running?"
+ "no instance lock - launcher not running?"
```

**Verification.** `python recall.py doctor` from `cmd.exe` (not
PowerShell) — no `�` characters in any output line. Grep
`app/core/doctor.py` for em-dash characters inside `Check("...",
..., "...")` literals: zero matches.

---

## Doctor — `versions` check fails inside a frozen bundle

**Issue.** A user running the installed `Recall.exe doctor` sees:

```
YELLOW  versions     engine 0.1.0; extension manifest not found
```

…even though nothing is wrong; the extension is installed in the
browser, not bundled with the desktop.

**Root cause.** `_check_version_mismatch` resolves the manifest at
`Path(__file__).parents[2] / "apps" / "extension" / "manifest.json"`.
That path exists in the source tree but not inside the PyInstaller
bundle, so the check always reports "not found" when frozen.

**Fix.** When `sys.frozen` is true, return a GREEN row that names
the situation truthfully:

```
GREEN   versions     engine 0.1.0 (extension installed in browser, not bundled)
```

Source-tree runs continue to compare the two versions and surface
drift as YELLOW.

**Verification.** Install Recall via `Recall-Setup.exe /VERYSILENT`,
run `%LOCALAPPDATA%\Programs\Recall\Recall.exe doctor`. The
`versions` row reads GREEN with the new copy. Running from source
(`python recall.py doctor`) keeps the old YELLOW drift behaviour.

---

## Doctor — stale instance lock reads GREEN

**Issue.** After a forced kill of Recall (Task Manager, SIGKILL,
crash), the next `recall doctor` reports:

```
GREEN   launcher     instance lock present
```

…even though no Recall process exists. The `~/.recall/instance.lock`
is the launcher's own write-then-delete-on-clean-shutdown file; a
forced kill leaves it on disk with a dead PID inside.

**Root cause.** The pre-fix `_check_launcher` only tested for the
lock's existence, not for the liveness of the PID it holds.

**Fix.** Read the lock contents as an integer PID, then `os.kill(pid,
0)` to probe liveness. Cross-platform PID liveness lives in a new
small helper `_pid_alive`:

```python
def _pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0); return True
    except ProcessLookupError:        # Unix: dead
        return False
    except PermissionError:           # Unix/Windows: alive but not signal-able
        return True
    except OSError as e:
        wer = getattr(e, "winerror", None)
        if wer == 87:  return False   # Windows ERROR_INVALID_PARAMETER -> no such PID
        if wer == 5:   return True    # Windows ERROR_ACCESS_DENIED -> PID exists
        return True                   # any other OSError: prefer alive over false-stale
```

The check now distinguishes four states (no lock / unreadable / no
PID / live / stale) and labels each.

**Verification.** Phase 5H ran the script:

1. With Recall running → GREEN: `instance lock held by PID <N>`.
2. After `Stop-Process -Force` → YELLOW: `stale instance lock (PID
   <N> not alive)`.
3. With a deleted lock → YELLOW: `no instance lock - launcher not
   running?`.

All three branches verified live on the build machine.

---

## Doctor — `autostart` false-negative on silent install

**Issue.** A silent installer install (`Recall-Setup.exe /VERYSILENT`)
correctly creates a per-user Startup-folder shortcut. The doctor
reports `YELLOW autostart off`, suggesting the user reach for
Settings — but autostart is already on, via a different surface.

**Root cause.** `_check_autostart` only inspects
`HKCU\Software\Microsoft\Windows\CurrentVersion\Run`, which is what
[`app/core/autostart.py`](../../app/core/autostart.py) (the in-app
Settings toggle) writes. The installer's `[Icons]` section writes a
`{userstartup}\Recall.lnk` shortcut instead. Two valid autostart
surfaces; doctor was only watching one.

**Fix.** Extend the check to OR the two surfaces:

| Run key | Startup shortcut | Verdict |
|---|---|---|
| ✅ | ✅ | GREEN — "Run key + Startup shortcut (belt and suspenders)" |
| ✅ | ✗ | GREEN — "HKCU Run key set (Settings toggle)" |
| ✗ | ✅ | GREEN — "Startup-folder shortcut present (from installer)" |
| ✗ | ✗ | YELLOW — "autostart off (no Run key, no Startup shortcut)" |

**Verification.** On the build machine, immediately after a silent
install, doctor reads GREEN: *"Startup-folder shortcut present
(from installer)"*. After uninstall, doctor reads YELLOW. After
toggling Settings → *Start Recall when I log in*, doctor reads
GREEN: *"HKCU Run key set (Settings toggle)"*.

---

## Installer — `recall://` URL scheme not registered

**Issue.** The browser extension's *Open Recall* button does
`chrome.tabs.create({ url: "recall://open" })`. If no app on the
machine registered the `recall://` protocol, the OS silently
discards the click — a dead click that looks identical to a
working one.

**Root cause.** The pre-fix [`recall.iss`](../../infra/packaging/windows/recall.iss)
had no `[Registry]` section, so an install did not associate
`recall://` with the installed `Recall.exe`.

**Fix.** Add a `[Registry]` section that writes the four standard
entries for a per-user URL handler:

```
HKCU\Software\Classes\recall                    "URL:Recall protocol"
HKCU\Software\Classes\recall                    "URL Protocol" = ""
HKCU\Software\Classes\recall\DefaultIcon        "{app}\Recall.exe,0"
HKCU\Software\Classes\recall\shell\open\command "\"{app}\Recall.exe\" \"%1\""
```

All four use the `uninsdeletekey` flag (set once on the
parent key) so the entire `recall` subtree is removed on
uninstall — no orphan registry rot.

**Verification.** After the next build + install of
`Recall-Setup.exe`, `recall doctor` reports:

```
GREEN  protocol   recall:// handler registered
```

`reg query HKCU\Software\Classes\recall /s` returns the four
values. After `unins000.exe /VERYSILENT`, the same query returns
*"unable to find the specified registry key"*. End-to-end
re-verification requires a rebuild; the `.iss` change is
syntactically validated by Inno Setup's own pre-flight (the build
fails fast if a `[Registry]` entry is malformed).

---

## Extension — popup stays in EMPTY despite real browsing

**Issue.** After installing the extension and browsing for an
hour, the popup keeps showing the empty state ("No activity yet")
even though `/v1/health` reports a non-zero `ingested_total` and
`/v1/events/recent` returns rows.

**Root cause.** The pre-fix `App.tsx` decided the body via inline
conditionals:

```ts
const nothing = !recovery && investigations.length === 0
                            && memory.length === 0;
if (nothing) return <EmptyState />;
```

There was no consideration of `health.ingestedTotal`. If
`/v1/events/recent` momentarily returned an empty array (cache
miss, ordering, throttling), the popup snapped back to EMPTY even
when the daemon counted events.

**Fix.** Replace the inline conditional with a pure
`derivePopupState(connection, health, recovery, investigations,
memory)` that returns one of eight `PopupState` values. The
EMPTY → CAPTURING transition is driven by `health.ingestedTotal
> 0 || memory.length > 0` — either surface flips it. The
**invariant** is enforced by code path: the only way to reach
the EMPTY branch is `recovery === null && investigations.length
=== 0 && health.ingestedTotal === 0 && memory.length === 0`.

**Verification.** `npm run build` in `apps/extension/ui/` passes
`tsc --noEmit && vite build` (399 modules, 282 KB, 90 KB gzipped).
Re-running the storybook capture
([`apps/extension/ui/capture_extension.mjs`](../../apps/extension/ui/capture_extension.mjs))
with the new `MOCK_CAPTURING` fixture produces
`assets/screenshots/extension-capturing.png` — a live recent-activity
list, never the empty surface.

---

## Extension — hardcoded "WebSocket retry debugging" fixture

**Issue.** The empty state shipped a hardcoded card titled
*"WebSocket retry debugging - 2 tabs · 2 files · reopened after a
2-day gap"* labelled *"You will see something like"*. Real users
hit the same demo string regardless of their actual work; trust
read as "Recall is showing me a canned example".

**Root cause.** Phase 5C's empty-state pass shipped the demo card
as a *what-it-could-look-like* preview. It was never gated on
having no real data, so it always rendered.

**Fix.** Delete the demo card from
[`states.tsx`](../../apps/extension/ui/src/components/states.tsx)'s
`EmptyState`. The replacement is the new `CapturingState`, which
shows a real *Recent activity* list from `/v1/events/recent` (max
5 rows) once any event has been captured. When activity is truly
zero, the fallback line is:

> *Keep browsing. Recall builds investigations from repeated work.*

No fake card, no canned title. The Phase 4G "*correct silence is
better than wrong recovery*" rule, applied to the popup.

**Verification.** Grep `apps/extension/ui/src` for `WebSocket
retry` — zero matches in code (one occurrence remains in a
historical JSDoc inside `states.tsx`, intentionally left as a
removal marker for archaeological context). The
`extension-empty.png` and `extension-capturing.png` captures show
the new surfaces.

---

## Extension — Open Recall is a dead click

**Issue.** The disconnected screen's primary CTA was
`onClick={() => openTab("recall://open")}`. If the OS had no
handler for `recall://`, nothing happened. The user clicked,
nothing changed, no diagnostic — the worst possible UX for a
trust surface.

**Root cause.** No fallback ladder, no visible feedback. The
browser silently dropped the protocol click.

**Fix.** A new `openRecall(): Promise<OpenRecallOutcome>` helper
in [`lib/api.ts`](../../apps/extension/ui/src/lib/api.ts) replaces
the direct `openTab` call:

1. Probe the daemon's `/v1/health`. If it answers, Recall is
   already running — return `launched`.
2. Otherwise dispatch `recall://open` via
   `chrome.tabs.create` (or `location.href` in dev). Return
   `launched`; the caller re-probes the daemon after a short
   delay.
3. If the dispatch itself cannot happen (no `chrome.tabs`, no
   `window`), return `repair` so the caller surfaces a reinstall
   prompt.

The CTA is wrapped in a new `OpenRecallButton` component that
**always** changes pixels on click:

- `idle`    → label *"Open Recall"*.
- `trying`  → label *"Opening Recall…"*, disabled, two-second
  re-probe scheduled.
- `repair`  → primary becomes *"Open the downloads page"* + a
  one-line explanation of the missing protocol handler.
- `hint`    → if the daemon is still down after the re-probe,
  primary becomes *"Try again"* + an inline link to the install
  page.

The settings panel's *Open Recall* row also routes through
`openRecall()` instead of the bare protocol click.

**Verification.** Phase 5H ran the popup against a stopped daemon
(emulating the dead-click case): every click on *Open Recall*
visibly changed the surface — label, then re-probe, then `hint`
state with the install link. Zero null transitions.

---

## Extension — no transition state when first events land

**Issue.** A user installed the extension, browsed for a minute,
and the popup still said *"No activity yet"*. Then suddenly the
popup populated with a full investigation. The intermediate state
(*"Recall is watching, here is what just got captured"*) did not
exist.

**Root cause.** The popup had only two body shapes: *empty* or
*fully populated*. There was no in-between.

**Fix.** A new `CapturingState` in
[`states.tsx`](../../apps/extension/ui/src/components/states.tsx)
fills that gap. It renders when `health.ingestedTotal > 0 ||
memory.length > 0` AND `recovery === null && investigations.length
=== 0`. The surface is:

- A green dot + *"Recall is watching locally"* + an event count
  ("23 events captured").
- A *Recent activity* list (`MemoryList`) with up to 5 rows from
  `/v1/events/recent`.
- The new DebugStrip at the bottom (see next item).
- No CTA. The user is mid-flow; the popup does not interrupt.

**Verification.** `extension-capturing.png` captures the surface
deterministically against `MOCK_CAPTURING`. The
`derivePopupState` function unit-trivially covers the transition
(invariant tested: events>0 ⇒ EMPTY forbidden).

---

## Extension — user cannot verify capture is working

**Issue.** A skeptical user asks *"are you sure anything is being
captured?"*. The popup answered with prose, never with numbers.

**Root cause.** No glanceable counter surface.

**Fix.** A new tiny `DebugStrip` component at the bottom of the
popup, shown only in the connected states (`capturing` /
`investigations` / `recovery`). Four mono-font counters separated
by middle dots:

```
23 captured · 5 browser · 2 invest · 1 recovery
```

Values are derived from data already on the page —
`health.ingestedTotal`, `memory.length`, `investigations.length`,
`recovery ? 1 : 0` — so no extra fetch, no engine work. The strip
is muted (var(--ink-4)) and intentionally below the body's
foreground.

**Verification.** `extension-connected.png` and
`extension-capturing.png` both show the strip; `extension-empty.png`
and `extension-disconnected.png` do not. The
`showsDebugStrip(state: PopupState): boolean` predicate is the
single source of truth.

---

## Extension — empty state dominates the popup

**Issue.** The empty state took the full popup body (~360 px tall)
with three nested sections (a header, a "How it works" list, the
demo card, the CTA, the footer). On a small popup, this read as
"the popup is mostly empty space".

**Root cause.** Over-eager onboarding. The popup is not the
onboarding surface; the desktop launcher is.

**Fix.** The new EMPTY state is *small*: a badge, a 14 px title, a
12 px body line, a 10.5 px mono footer. That's it. Total height
~ 180 px. The popup breathes.

**Verification.** `extension-empty.png` shows the new compact
surface. Diff against the pre-5H capture: ~ 50% fewer pixels of
content, calmer header, no CTA, no fixture row.

---

## Summary table

| # | Layer | Issue | Status |
|---|---|---|---|
| 1 | engine | cp1252 em-dash mangling | **fixed** |
| 2 | engine | frozen-bundle manifest path | **fixed** |
| 3 | engine | stale instance lock false GREEN | **fixed** |
| 4 | engine | autostart blind to Startup folder | **fixed** |
| 5 | installer | `recall://` not registered | **fixed** (verify-on-rebuild) |
| 6 | extension | EMPTY despite captured events | **fixed** |
| 7 | extension | hardcoded WebSocket demo card | **fixed** |
| 8 | extension | Open Recall dead click | **fixed** |
| 9 | extension | no transition state | **fixed** (new CapturingState) |
| 10 | extension | no glanceable counters | **fixed** (DebugStrip) |
| 11 | extension | empty state too dominant | **fixed** |

All eleven were Phase-5G findings; all eleven close in Phase 5H.
None expanded the seven-layer engine; none added new memory
systems. The directive's *only friction, only humans, only
distribution* held — everything above is friction.

## Deferred

Two side-effects of the `recall://` fix that are tracked but **not**
in Phase 5H:

- **End-to-end protocol verification.** Closing item #5 requires a
  rebuild of `Recall-Setup.exe` (Inno Setup re-compiles the new
  `[Registry]` directives into the installer). The syntactic
  correctness is verified at compile time; the installed-state
  behavioural verification ("the `recall://` click in the browser
  routes to the installed Recall.exe") needs the rebuild +
  reinstall and is listed in the next clean-machine run.
- **Deep-link payload routing.** Registering `recall://` so the OS
  knows where to send the click is half the fix. Routing
  `recall://open?investigation=t1` to the *right view* in the
  launcher is a second half that touches `app/main.py` argv
  parsing + the launcher's single-instance IPC. Not engine
  expansion (no new memory layer), but not Phase 5H either.

> Cross-referenced by
> [`CLEAN_MACHINE_RUN.md`](../trust/CLEAN_MACHINE_RUN.md) §
> *Friction log* (each row points back here), and by
> [`PHASE_TRACKER.md`](../founder/PHASE_TRACKER.md) Phase 5H.
