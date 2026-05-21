# MAC_BUILD_STATUS.md — macOS build, honestly tracked

Phase 5A wrote the macOS packaging scripts. They have **not** been
run on macOS — Recall is being developed on Windows. This file is
the honest status, with no rounding up. macOS is **not** a
supported install path until every row below is `verified`.

Pairs with [`SUPPORTED_PLATFORMS.md`](SUPPORTED_PLATFORMS.md), which
tiers macOS as **Preview** for exactly this reason.

---

## Status

| Item | Status | Notes |
|---|---|---|
| Packaging scripts written | ✅ done | `infra/packaging/macos/` — `build.sh`, `Info.plist`, launch agent |
| PyInstaller `.app` build | � build pending | needs a macOS machine; `recall.spec` may need a `BUNDLE()` step |
| Apple Silicon (arm64) | ⛔ not started | no build attempted |
| Intel (x86_64) | ⛔ not started | no build attempted |
| Universal2 binary | ⛔ not started | needs universal Python + `target_arch` in `recall.spec` |
| `Recall.dmg` build | ⛔ not started | `build.sh` stage 3 unrun |
| Launch agent install path | ⛔ unverified | `computer.recall.agent.plist` written, not loaded/tested |
| Gatekeeper / notarisation | ⛔ not started | needs Apple Developer ID |
| End-to-end install on macOS | ⛔ unverified | the grandmother test has not been run on a Mac |

Legend: ✅ done · ⏳ pending · ⛔ not started/unverified.

## What "verified" will require

For a row to become `verified`, a maintainer on macOS must:

1. Run `bash infra/packaging/macos/build.sh` and get a `Recall.dmg`.
2. Open the `.dmg`, drag to Applications, launch.
3. Confirm the menu-bar entry appears and the launcher opens.
4. Confirm the launch agent installs and survives a re-login.
5. Record the result here, with the macOS version and chip.

## Why this file exists

The directive for this phase was explicit: *no pretending support
exists.* A `README` that lists macOS next to Windows implies parity
that has not been earned. This file is the counterweight — until it
is green, macOS users are pointed at *run from source*, not at a
`.dmg` that has never been built.

> First macOS maintainer to complete the steps above: replace the
> ⛔/⏳ rows with ✅, add your macOS version + chip, and delete this
> blockquote.
