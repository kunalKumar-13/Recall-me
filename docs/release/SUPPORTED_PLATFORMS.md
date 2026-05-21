# Supported platforms

What Recall runs on, how well, and what is still a release gate.
Honesty over optimism: a tier here is the *real* state, not the
aspiration.

---

## Support tiers

| Platform | Tier | Install | Notes |
|---|---|---|---|
| Windows 11 (x64) | **Supported** | `Recall-Setup.exe` | Primary development + test platform |
| Windows 10 (x64) | **Supported** | `Recall-Setup.exe` | Same installer; 1809+ |
| macOS 12–15 (Apple Silicon) | **Preview** | `Recall.dmg` | Built + reviewed; not yet green on a maintainer's machine |
| macOS 11 (Big Sur) | **Preview** | `Recall.dmg` | Minimum target (`LSMinimumSystemVersion`) |
| macOS (Intel x86_64) | **Source only** | run from source | Universal `.dmg` is a release gate (below) |
| Linux (X11/Wayland) | **Source only** | run from source | PyQt6 runs; no packaged artifact |

- **Supported** — built, installed, and used on this platform.
- **Preview** — the packaging is written and reviewed but has not
  yet produced a verified, tested artifact.
- **Source only** — runs via [`install-3min`](../../apps/docs/install-3min.mdx);
  no one-click installer yet.

## Release gates

Honest list of what stands between "Preview" and "Supported":

1. **Windows code-signing.** The installer is unsigned, so
   SmartScreen warns on first run. Closing this needs an EV
   certificate + `signtool` in the release pipeline ([`RELEASE.md`](RELEASE.md)).
2. **macOS notarisation.** The `.dmg` is unsigned and unnotarised,
   so Gatekeeper warns. Closing this needs an Apple Developer ID +
   `notarytool`.
3. **macOS universal2 build.** The current `build.sh` produces a
   single-architecture `.dmg` matching the build machine. A true
   Apple-Silicon-plus-Intel artifact needs a universal Python and
   `target_arch='universal2'` in `recall.spec` — see
   [`infra/packaging/macos/README.md`](../../infra/packaging/macos/README.md).
4. **macOS verified build.** The macOS scripts have not been run on
   macOS in the current cycle (development is on Windows). First
   green `build.sh` promotes macOS from Preview to Supported.

## Runtime requirements

- **RAM:** ~300–500 MB resident (the embedding model dominates).
- **Disk:** ~250 MB installed + the ~80 MB model cache + your
  growing `~/.recall/` event log (plain JSONL — small).
- **Network:** one outbound call ever — the first-run model
  download. After that Recall is fully offline.
- **Permissions:** none beyond a normal user account. No admin, no
  root, no system extensions.

## What "supported" guarantees

On a Supported platform, the [grandmother test](INSTALL.md) holds:
download one file, double-click, and Recall is running — no
terminal, no Python, no docs required. Anything short of that on a
Supported platform is a release-blocking bug.
