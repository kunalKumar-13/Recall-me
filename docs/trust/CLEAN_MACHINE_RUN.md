# CLEAN_MACHINE_RUN.md — the gate-1 walk record

The single question this file answers: *did `Recall-Setup.exe` work
on a machine that has never seen Recall?*

Phase 5G's directive was **reality validation**, not engineering.
This file is the running record of every fresh-install run, with
real timings and friction. It supersedes the silent-install-only
proof in [`INSTALL_PROOF_WINDOWS.md`](INSTALL_PROOF_WINDOWS.md): a
build artifact is necessary, not sufficient.

Honesty rule: a row is ✅ only if it was *executed* on a machine
described in *Setup* below. Build-machine runs are recorded with
their own row tag (▲), because they prove a different thing.

---

## How to use this file

1. Spin up the test machine (a fresh Windows 10/11 VM, or a clean
   profile).
2. Copy `Recall-Setup.exe` to it. Nothing else.
3. Walk the checklist below, **with a stopwatch and a screenshot
   tool**. Fill the rows for your run by appending a new *Run N*
   block (don't overwrite earlier runs — the file is a history).
4. Each row gets ✅/❌/⬜ and a one-line note. Confusions and
   warnings observed in passing go in the *Friction log* below.
5. At the end of a run, paste `recall stats --export` and the
   `recall doctor` outputs into [`EXTENSION_VALIDATION.md`](EXTENSION_VALIDATION.md)
   and [`RECOVERY_STRESS.md`](RECOVERY_STRESS.md) respectively.

A run only counts if rows 1-11 are at minimum ✅/❌ — not ⬜.

---

## Setup template

For each run, fill this once:

```
Run N - YYYY-MM-DD
  tester:       <handle - founder-assigned, never PII>
  machine:      <Windows 10/11 build, RAM, CPU>
  cleanliness:  fresh VM / clean profile / build machine (▲)
  installer:    Recall-Setup.exe SHA-256 <hex>
  network:      online / offline / limited
```

## Checklist

| #  | Step | Pass criteria | Build machine (▲) | Run 2 | Run 3 |
|----|------|---------------|-------------------|-------|-------|
| 1  | Clean machine prepared | no Python, no previous `.recall\`, no dev tools | ⬜ (build machine; not clean) | ⬜ | ⬜ |
| 2  | `Recall-Setup.exe` runs | double-click → wizard, **no admin prompt** | ✅ silent install confirmed `PrivilegesRequired=lowest`, exit 0 | ⬜ | ⬜ |
| 3  | Install completes < 3 min | wizard *Finish*, timed | ✅ **66.0 s** (silent), 1.1 min | ⬜ | ⬜ |
| 4  | Launcher opens | Ctrl + Space → launcher visible | ▲ tray icon + first-run onboarding rendered in offscreen test; visual Ctrl+Space test not run | ⬜ | ⬜ |
| 5  | Daemon starts | `127.0.0.1:4545/v1/health` returns ok | ✅ confirmed via Invoke-WebRequest within ~3 s of launch | ⬜ | ⬜ |
| 6  | Onboarding works | folder pick → indexing starts | ▲ first-run onboarding screen rendered; folder-pick interaction not driven | ⬜ | ⬜ |
| 7  | Browser extension pairs | popup shows *Connected* | ⬜ requires loading the extension in Chrome on the test machine | ⬜ | ⬜ |
| 8  | Autostart honored | reboot → tray icon back; doctor `autostart=GREEN` | ⬜ silent install skipped the autostart task (no `Flags: checkedonce` → defaults off in silent mode); a wizard run keeps the user's checked task | ⬜ | ⬜ |
| 9  | Recovery appears | after real use, a recovery card shows | ⬜ requires 2-3 days of real activity | ⬜ | ⬜ |
| 10 | Resume works | clicking Resume reopens the work | ⬜ requires row 9 to pass first | ⬜ | ⬜ |
| 11 | Repair path | `Recall-Setup.exe /SILENT` over a broken install | ⬜ not exercised | ⬜ | ⬜ |
| 12 | Upgrade | newer version keeps `~/.recall\` | ⬜ no newer version yet | ⬜ | ⬜ |
| 13 | Uninstall — no residue | uninstall removes app; `~/.recall\` left | ✅ `unins000.exe /VERYSILENT` exit 0 in **6.1 s**; install dir + 3 shortcuts + uninstall reg key all removed | ⬜ | ⬜ |

Legend: ✅ pass · ❌ fail · ⬜ not yet run · ▲ partial / build-machine only.

---

## Build-machine run — 2026-05-20

```
Run 1 (▲) - 2026-05-20
  tester:       Recall maintainer (build machine)
  machine:      Windows 11 Pro 10.0.26200, x64
  cleanliness:  BUILD MACHINE (not clean) -
                  ~/.recall moved to ~/.recall.dev-backup before install,
                  restored after uninstall
  installer:    Recall-Setup.exe
                  SHA-256 7AFA53497A419444B11696D4E5494D3A1F2EAAAA229671448B9B6B96375FD975
                  260.8 MB / 273,512,213 bytes
  network:      online (no embedding model download triggered;
                  warm-up completed against local HF cache)
```

### What was executed

- **Install**: `Recall-Setup.exe /VERYSILENT /SUPPRESSMSGBOXES
  /NORESTART /LOG=...` → exit 0, **66.0 seconds wall**, install
  dir 976 MB / 6,867 files. Per-user (`HKEY_CURRENT_USER` root
  key), no admin prompt.
- **Launch**: `Start-Process` against the installed `Recall.exe`,
  stderr+stdout redirected to a file. All boot stages OK per
  `RECALL_DEBUG=1` output (config dir created, API up on
  127.0.0.1:4545, tray icon visible, hotkey registered, model
  warm-up completed). First-run onboarding screen rendered.
- **Memory after warm-up**: WS 623 MB, Private 795 MB,
  705 handles, ~10.7 s CPU during boot. One process tree
  (no separate API subprocess).
- **`recall doctor` against the installed bundle**: 3 GREEN
  (daemon, launcher, installer), 7 YELLOW (the expected
  first-run yellows). No reds. Output preserved at
  `infra/packaging/windows/build_logs/doctor-post-install.log`.
- **Uninstall**: `unins000.exe /VERYSILENT /SUPPRESSMSGBOXES` →
  exit 0, 6.1 s wall. Verified absent post-uninstall: install
  dir, desktop shortcut, Startup shortcut, Start Menu entry,
  uninstall registry key.

### What was not executed

- **Ctrl+Space launcher interaction**: requires a real desktop
  session and visual confirmation.
- **Folder-pick onboarding step**: requires a real user click.
- **Browser extension pair**: requires loading the unpacked
  extension into Chrome/Edge and using a page.
- **Multi-day recovery**: the recovery engine needs real
  activity over time to surface a high-trust card.
- **Repair path**: not exercised.
- **Upgrade**: no newer build to upgrade to.
- **Reboot autostart**: would have required a reboot; out of
  scope for this session.

### Friction log

Real surprises observed during this run. Each is a Phase-5H
candidate.

1. **Process exited silently on first launch attempt.** Running
   the installed `Recall.exe` with `Start-Process -PassThru`
   alone (no `-RedirectStandardOutput`) caused the process to
   exit within ~60 seconds with no diagnostic. The same launch
   with stderr+stdout redirected to files completed normally.
   Suspected root cause: PyInstaller's `console=False` mode +
   inherited PowerShell stdio handles. **Impact for a real
   user:** none (they double-click from Explorer, which doesn't
   inherit handles). **Impact for a maintainer:** misleading
   when verifying from a script.
2. **Em-dash mangling in `recall doctor` strings.** Three strings
   in [`app/core/doctor.py`](../../app/core/doctor.py) use an
   em-dash (`—`) that prints as `�` on a cp1252 Windows console.
   These are user-facing first-run messages. The doctor's own
   header comment claims *"ASCII so Windows cp1252 consoles
   never crash printing them"* — the rule is good; three lines
   slipped through. **Phase-5H candidate.**
3. **Doctor `versions` check can't find the extension manifest
   from inside the frozen bundle.** The check resolves
   `Path(__file__).parents[2] / "apps" / "extension" /
   "manifest.json"` — that path exists in the source tree, not
   inside the bundle. On the installed bundle it reports
   `engine 0.1.0; extension manifest not found`. **Phase-5H
   candidate:** ship the manifest with the bundle, or skip the
   check when `sys.frozen`.
4. **Silent install skipped the autostart task.** Inno Setup's
   `/VERYSILENT` mode applies *only* default-checked tasks; the
   `startuplaunch` task has no `Flags`, so behaviour depends on
   the installer's default. A wizard install keeps the
   user's checked task; a silent install does not. **Workaround
   for alpha:** include `/TASKS="desktopicon,startuplaunch"`
   when scripting silent installs (documented in
   [`INSTALL_METRICS.md`](../release/INSTALL_METRICS.md)).
5. **HKCU Run key never written by install.** Confirmed by
   design: the installer creates a Startup-folder shortcut, not
   a Run-key entry; only `recall doctor` + user toggle write the
   Run key (via `app/core/autostart.py`). Both paths achieve
   launch-on-login; the founder dashboard should call out that
   `recall doctor` reads only the Run key, so a Startup-folder
   install renders as `autostart=YELLOW` even when functionally
   autostarted. **Phase-5H candidate:** extend
   `_check_autostart` to also look at the Startup folder.

---

## What turns gate 1 GREEN

Three more runs of this file, each on a different machine that has
never seen Recall, with rows 1-11 at minimum ❌ (a failed row is
still a *real* answer; a ⬜ row means the run did not happen).

The current verdict is **▲ partial GO**: the installer artifact
runs end-to-end on the build machine. The clean-machine question is
still open.

> Cross-referenced by [`GO_NO_GO.md`](../release/GO_NO_GO.md) gate
> 1 and [`PHASE_TRACKER.md`](../founder/PHASE_TRACKER.md) (Phase 5G).
