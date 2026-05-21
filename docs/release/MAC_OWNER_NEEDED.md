# MAC_OWNER_NEEDED.md — the explicit ask

Recall is developed on Windows. Phase 5F + 5G closed the Windows
install-truth loop. The macOS rows in
[`MAC_VERIFICATION.md`](MAC_VERIFICATION.md) are all `unknown`,
and they will stay `unknown` until a maintainer with macOS
hardware runs the verification script below.

This file is the **dispatch ticket**: who, what, how long, what
to commit. Anyone with a Mac can pick it up.

Pairs with [`MAC_VERIFICATION.md`](MAC_VERIFICATION.md) (the 13×2
matrix) and [`MAC_BUILD_STATUS.md`](MAC_BUILD_STATUS.md) (the
historical build-side tracker).

---

## Who can do this

Anyone with:

- A **macOS 12 (Monterey) or later** Mac. Apple Silicon (M-series)
  or Intel (x86_64) is fine — each adds one column to the matrix.
- Python 3.11+ installed (the python.org build, not the system
  Python).
- Xcode Command Line Tools.
- Time: ~90 minutes for the build + walk; another 90 if both
  chips are available.

You do **not** need:

- An Apple Developer ID. The build runs un-notarised; Gatekeeper
  shows a *"unidentified developer"* warning that the user
  dismisses with *Right-click → Open*. Notarisation is a separate,
  later milestone.
- An EV cert (that's the Windows side).
- Permission. The packaging script is in the repo; the matrix is
  written; the ask is the maintainer-with-Mac you're reading.

## What to do — the verification script

```bash
# 1. Clone Recall on the Mac.
git clone <repo> recall && cd recall

# 2. Install deps + PyInstaller.
python3 -m pip install -r requirements.txt pyinstaller

# 3. Run the macOS packaging script.
bash infra/packaging/macos/build.sh
# Expected outputs:
#   dist/Recall.app/
#   dist/Recall.dmg

# 4. Mount + drag + launch (the grandmother test).
open dist/Recall.dmg
# Drag Recall into Applications.
open -a Recall

# 5. Walk the 13-row matrix in MAC_VERIFICATION.md.
#    For each row, edit the cell from `unknown` to `working` or
#    `blocked`. For `blocked`, add a one-line reason in the
#    Notes column.

# 6. Run the doctor against the installed app.
/Applications/Recall.app/Contents/MacOS/Recall doctor > doctor-mac.log

# 7. Commit + open PR with:
#      docs/release/MAC_VERIFICATION.md  (the filled matrix)
#      doctor-mac.log                    (the audit trail)
#      assets/screenshots/launcher-macos.png (a real launcher capture
#                                             from the running app)
```

## How long it actually takes

| Step | Time | Why |
|---|---|---|
| Clone + deps | ~10 min | depends on network + pip cache |
| First PyInstaller run | **20-40 min** | torch + sentence-transformers + chromadb is a heavy tree; first build resolves all hooks |
| `build.sh` finishing the `.dmg` | ~5 min | hdiutil is fast |
| Drag, launch, verify menu-bar entry | ~5 min | the grandmother test |
| Walk rows 7-13 | ~30 min | Cmd+Space conflicts with Spotlight; binding choice + extension pairing each get a real test |
| Doctor + screenshot | ~5 min | one launch, one screenshot |
| Edit `MAC_VERIFICATION.md` + open PR | ~10 min | the diff is the verification record |
| **Total** | **~90 min on Apple Silicon, +60 min if Intel is added** | |

## Blocking rows — what is most likely to break

These are the rows the build-side analysis flags as *most likely
to need attention on first contact*. If you hit one, mark
`blocked` and add a one-line reason; do not pretend it works.

1. **`recall.spec` may need a `BUNDLE()` step.** PyInstaller on
   macOS produces a `.app` only when the spec calls `BUNDLE()`.
   The current spec produces a one-folder layout; `build.sh`
   wraps it manually. If `Recall.app/Contents/MacOS/Recall` is
   missing, the spec needs `BUNDLE()`.
2. **Cmd+Space hotkey conflicts with Spotlight.** The launcher
   needs a different binding on macOS — `Cmd+Shift+Space` or
   `Option+Space` are good candidates. If the global hotkey
   fails to register, `app/ui/launcher.py` needs a
   platform-aware default.
3. **Launch agent path.** The plist at
   `infra/packaging/macos/computer.recall.agent.plist` is
   *written* but never `launchctl load`-tested. On first install
   the script may need to `launchctl bootstrap` rather than
   `launchctl load`.
4. **Code signing on Apple Silicon.** Un-signed builds on M-chips
   sometimes refuse to launch with a *"is damaged"* error
   (Gatekeeper hardening). Workaround: `xattr -dr
   com.apple.quarantine /Applications/Recall.app`. If this is
   needed, mention it in the row note.
5. **PyQt6 wheel architecture.** A universal2 build needs a
   universal Python interpreter; otherwise the bundle is
   single-arch. Mark the *other* chip column `blocked` if so.

## What "done" looks like

The `MAC_VERIFICATION.md` matrix has **at least one column** with
no `unknown` cells, plus the dispatch entry at the bottom:

> Verified on macOS [version] (chip: Apple Silicon | Intel) on
> [date] by [handle]. [Row N blocked because X.] All other rows:
> working.

Then [`GO_NO_GO.md`](GO_NO_GO.md) can stop saying *"macOS is
Preview only"* and [`SUPPORTED_PLATFORMS.md`](SUPPORTED_PLATFORMS.md)
can promote macOS from Preview to Supported. The
[`READINESS_SCORE`](../founder/READINESS_SCORE.md) Installer
dimension picks up the gain automatically once `release.mac`
flips in [`apps/admin/release_state.json`](../../apps/admin/release_state.json).

## What this file is not

- Not a hiring posting. Anyone with a Mac and an hour and a half
  can do this; you don't need to be a maintainer.
- Not a roadmap item. macOS support is in
  [`ROADMAP_LIVE.md`](../founder/ROADMAP_LIVE.md) → *Next*; this
  file is the *task ticket* for that roadmap row.
- Not an apology. Recall is honest about what it does and doesn't
  support; documenting the gap is the *correct* version of
  cross-platform care for a single-maintainer alpha.

If you're going to do this, drop a note in the project's contact
channel first so the matrix doesn't get two PRs at the same time.
