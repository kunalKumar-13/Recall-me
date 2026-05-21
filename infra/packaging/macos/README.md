# macOS packaging

Produces **`Recall.dmg`** — the drag-to-Applications disk image.

## What the user gets

Open `Recall.dmg` → drag **Recall** to **Applications** → launch it.
Recall lives in the **menu bar** (`LSUIElement` — no Dock icon), the
same calm posture as the Windows tray build. The launcher is
summoned with the global hotkey.

The first-launch flow offers "Start Recall when I sign in", which
installs the launch agent (`computer.recall.agent.plist`) into
`~/Library/LaunchAgents/` — per-user, no root.

## Build

```bash
bash infra/packaging/macos/build.sh   # must run on macOS
```

Three stages: PyInstaller bundles the `.app`, `Info.plist` + icon are
copied in, `hdiutil` builds the `.dmg`.

### Prerequisites

- `pip install -r requirements.txt pyinstaller`
- Xcode command-line tools (`hdiutil`, `codesign`).

## Files

| File | Role |
|---|---|
| `Info.plist` | `.app` bundle metadata — menu-bar app, min macOS 11 |
| `computer.recall.agent.plist` | login launch agent (autostart) |
| `build.sh` | PyInstaller → `.app` → `.dmg`, one command |

## Apple Silicon & Intel

Recall targets **macOS 11+ (Big Sur)**. A true universal binary
(Apple Silicon + Intel in one `.dmg`) requires a universal Python and
`target_arch='universal2'` added to the macOS branch of `recall.spec`.
Until that is wired, `build.sh` produces a **single-architecture**
build matching the build machine:

- Build on Apple Silicon → an arm64 `.dmg` (Intel users fall back to
  running from source, or to a separately-built x86_64 `.dmg`).
- The intent is a universal2 artifact; that is tracked as the macOS
  release gate in [`SUPPORTED_PLATFORMS.md`](../../../docs/release/SUPPORTED_PLATFORMS.md).

## Signing & notarisation

`build.sh` produces an **unsigned, unnotarised** `.dmg`. Gatekeeper
will block first launch ("unidentified developer"). Signing with an
Apple Developer ID and notarising with `notarytool` is a separate,
credentialed release step — see [`RELEASE.md`](../../../docs/release/RELEASE.md).

> **Honest status:** these scripts are written and reviewed but have
> not been executed on macOS in this development cycle — Recall is
> being built on Windows. The macOS path is verified by review, not
> by a green build. First macOS maintainer to run `build.sh`: please
> report back so this note can be removed.
