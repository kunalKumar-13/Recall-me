# MAC_VERIFICATION.md — the honest macOS matrix

Phase 5F's directive was *no assumptions*. This file is the macOS
equivalent of [`../trust/INSTALL_PROOF_WINDOWS.md`](../trust/INSTALL_PROOF_WINDOWS.md):
a hardware-by-hardware matrix of what has actually been run on a
Mac, and what is still **unknown**.

Recall is developed on Windows. Until a maintainer with macOS
hardware fills this matrix with `working`, macOS remains a **Preview**
tier — see [`SUPPORTED_PLATFORMS.md`](SUPPORTED_PLATFORMS.md).

Pairs with [`MAC_BUILD_STATUS.md`](MAC_BUILD_STATUS.md) (the
build-side mirror).

---

## The honesty rule

A cell flips off `unknown` only when a real Mac executed the step.
*"It should work"* is **`unknown`**. *"It's the same code as
Windows"* is **`unknown`**. Only *"a maintainer ran it on this
chip + OS and saw X"* counts.

## The matrix

Three columns, one row per verification step.

| Step | Apple Silicon (arm64) | Intel (x86_64) | Notes |
|---|---|---|---|
| 1. `bash infra/packaging/macos/build.sh` exits 0 | unknown | unknown | script written 5A; never executed |
| 2. `Recall.app` bundle produced | unknown | unknown | PyInstaller step inside `build.sh` |
| 3. `Recall.dmg` produced | unknown | unknown | hdiutil step; needs a Mac |
| 4. DMG mounts, drag-to-Applications works | unknown | unknown | the grandmother UX |
| 5. App launches from `/Applications/Recall.app` | unknown | unknown | first run, no crash |
| 6. Menu-bar icon appears (no Dock entry) | unknown | unknown | Phase 4I parity with Windows tray |
| 7. Launcher opens via global shortcut | unknown | unknown | Cmd+Space conflicts with Spotlight; check binding |
| 8. Browser extension connects to `127.0.0.1:4545` | unknown | unknown | same loopback contract as Windows |
| 9. `computer.recall.agent.plist` loads on login | unknown | unknown | `launchctl load` step |
| 10. Autostart survives logout/login cycle | unknown | unknown | the actual login-item test |
| 11. Resume reopens files + tabs | unknown | unknown | end-to-end behavioural test |
| 12. Uninstall removes app, leaves `~/.recall/` | unknown | unknown | the *your memory is yours* rule |
| 13. Gatekeeper warning + *Right-click → Open* path | unknown | unknown | until notarised |

Legend (use exactly these tokens):

- **working** — executed; the documented outcome occurred.
- **blocked** — executed; failed on a named, reproducible issue.
- **unknown** — not executed. Default state.

## Build-host requirements

For a future maintainer who fills this matrix:

- **macOS 12 (Monterey) or later** — PyQt6 wheels target that.
- **Python 3.11+**. Use the official python.org build (not the
  system Python) so PyInstaller can find a clean interpreter.
- **Xcode Command Line Tools** for the linker.
- **For universal2:** a universal Python build + `target_arch="universal2"`
  in `recall.spec`.

Notarisation requires an **Apple Developer ID** (~$99/year). The
build can ship un-notarised for the alpha cycle; Gatekeeper warns
on first run and the user does the *Right-click → Open* dance.

## Procedure for the first Mac maintainer

1. Clone the repo on a Mac.
2. `pip install -r requirements.txt pyinstaller`
3. `bash infra/packaging/macos/build.sh` → check stage 1, 2, 3 each.
4. Open the produced `.dmg`, drag, launch, work for 10 minutes.
5. **Edit this file.** For each row, change `unknown` to `working`
   or `blocked`. For `blocked`, add a one-line reason in the
   *Notes* column. Record the macOS version and chip in the row
   below.
6. Commit. The PR diff is the verification record.

## The reality entry (when filled in)

The maintainer who completes the run replaces this paragraph with:

> Verified on **macOS \_\_** (chip: **Apple Silicon | Intel**) on
> **YYYY-MM-DD** by **\<handle\>**. \[Row N is blocked because
> X.\] All other rows: `working`.

Until then, the macOS install path is **Preview**, and
[`docs/release/INSTALL.md`](INSTALL.md) points Mac users at
*run from source*, not at a `.dmg` that has never been built.

## Why this file exists

The Phase 5F directive: *no assumptions, no pretending*. A README
that lists macOS next to Windows implies parity that has not been
earned. This matrix is the counterweight — every row is a real
question whose only honest current answer is `unknown`. The first
maintainer with a Mac turns it into a release artifact, and the
[`GO_NO_GO.md`](GO_NO_GO.md) macOS gate stays NO-GO until they do.
