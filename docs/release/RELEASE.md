# Release pipeline

This file documents how Recall builds, tags, and ships. It is the
single source of truth the release engineer reads before cutting a
build. Versioning policy lives in [`VERSIONING.md`](VERSIONING.md);
the user-facing changelog is [`CHANGELOG.md`](CHANGELOG.md).

## Release channels

Three channels, conceptually three pipelines pointing at the same
codebase from different cuts.

| Channel | Source | Cadence | Audience | Auto-update |
|---|---|---|---|---|
| **stable** | A signed tag on `main` (`vMAJOR.MINOR.PATCH`) | When the maintainer says so. Tested. Documented. | Daily users. Default download. | On (architecture documented below; implementation deferred). |
| **preview** | The latest commit on `main` that passes the smoke test on all three OSs | At most weekly | Contributors + curious users | On (separate update channel). |
| **nightly** | The latest commit on `main` regardless of smoke status | Every push | Engine developers | Off — install + uninstall manually. |

No telemetry on any channel. Channels do not phone home; they are
distinguished by where the binary was downloaded from, not by any
runtime check. A user can sit on stable for years and never see a
nightly artefact.

### Channel naming on disk

The launcher's `~/.recall/version.json` records:

```json
{
  "version": "0.2.0",
  "channel": "stable",
  "build_id": "0.2.0-stable-2026-05-22",
  "smoke_test_passed_at": "2026-05-21T18:32:00Z"
}
```

This file is *the only* place the channel is recorded. Settings
displays it; the launcher boot log prints it. No remote endpoint
ever sees it.

## Auto-update architecture (planned)

The pipeline below is the design, not the running implementation.
What lands in 0.x is the *file format* and a single function that
*reads* an update manifest — actual update fetching is gated on a
1.0.0 milestone.

```
┌─────────────────────────────────────────────────────────┐
│  Recall (local process)                                 │
│                                                         │
│  At startup:                                            │
│   1. Read ~/.recall/version.json                        │
│   2. (Future) Fetch updates/{channel}.json from         │
│      a single hardcoded HTTPS host                      │
│   3. If newer signed manifest available, present a      │
│      Settings prompt: "Update to v0.2.1 available"      │
│   4. User accepts → download + verify signature →       │
│      replace executable on next launch                  │
│                                                         │
│  At no point:                                           │
│   • is user data uploaded                               │
│   • is install ID generated                             │
│   • is "phone home" telemetry sent                      │
└─────────────────────────────────────────────────────────┘
```

The update manifest is a signed JSON file:

```json
{
  "channel": "stable",
  "latest_version": "0.2.1",
  "released_at": "2026-05-22T00:00:00Z",
  "release_notes_url": "https://docs.recall.computer/releases/0.2.1",
  "binaries": [
    {
      "platform": "windows-x64",
      "url": "https://releases.recall.computer/0.2.1/Recall-0.2.1-stable.exe",
      "sha256": "…",
      "signature": "…"
    }
  ]
}
```

A user with auto-update disabled in Settings stays on their
current version forever. The product never updates without
explicit consent.

## Installer pipeline (macOS launcher)

The v2 Tauri launcher ships as a `.dmg`:

1. `cd apps/launcher && pnpm tauri build` — compiles the release
   binary (fat-LTO, `opt-level = "s"`) and bundles both artifacts:

   ```
   src-tauri/target/release/bundle/macos/Recall.app
   src-tauri/target/release/bundle/dmg/Recall_<version>_aarch64.dmg
   ```

   The whole app is ~2.4 MB — the launcher is a thin shell; the
   engine ships separately with the Python daemon.

2. **Today's signing state: ad-hoc** (linker-signed). Gatekeeper
   will warn on first open; right-click → Open works for the
   pre-1.0.0 audience. Same funding-not-engineering posture as the
   Windows section below.

3. **Real signing + notarization** (deferred, needs a $99/yr Apple
   Developer ID). When the certificate exists, no code changes are
   required — export before the same build command:

   ```bash
   export APPLE_SIGNING_IDENTITY="Developer ID Application: <name> (<team>)"
   export APPLE_ID=… APPLE_PASSWORD=… APPLE_TEAM_ID=…   # notarytool
   pnpm tauri build
   ```

   Tauri signs the bundle, submits it to notarytool, and staples
   the ticket into the `.dmg`.

Known build constraint: `window-vibrancy` must stay on the same
minor version tauri's `macos-private-api` feature pulls — two
versions of the crate define the same Objective-C class and the
duplicate symbol fails the fat-LTO release link (dev builds don't
catch it).

## Installer pipeline (Windows)

The packaging path today:

1. `python infra/scripts/build_icon.py` (optional — generates
   `app/assets/icon.ico` from the SVG source if you haven't
   already).
2. `pyinstaller recall.spec` (uses the existing spec in repo
   root). Produces `dist/Recall/Recall.exe` plus the bundled
   PyQt6 + ChromaDB + sentence-transformers runtime.
3. **Code signing** (deferred). The producer needs a Windows
   code-signing certificate (DigiCert, Sectigo, …). The signing
   step belongs between PyInstaller and the MSI step:

   ```bash
   signtool sign /tr http://timestamp.digicert.com /td sha256 \
                 /fd sha256 /a dist/Recall/Recall.exe
   ```

4. **MSI / setup wrapper** (deferred). The recommended tool is
   `Inno Setup`. A draft `.iss` script will land at
   [`infra/installers/windows/recall.iss`](../../infra/installers/README.md)
   once an installer is needed; today the spec produces a folder
   install rather than a true Windows installer.

### Why this is deferred

- A signed installer requires a real certificate (≈ $300/yr, EV
  certs more), which is a project-funding question, not an
  engineering one.
- The unsigned `pyinstaller` build is sufficient for the
  pre-1.0.0 audience (developers, early adopters who can
  whitelist the binary in SmartScreen).
- The release-channel architecture above does not depend on a
  signed installer; it can ship on top of the existing
  PyInstaller artefact.

## Release checklist

Before tagging `v0.X.Y`:

- [ ] `python _smoke_api.py` passes all 29 sections.
- [ ] Manual launcher run: open Ctrl+Space; type a query; verify
      results render in under 100 ms.
- [ ] Manual recovery: open the launcher idle, click a "Continue
      where you left off" card, verify all targets open.
- [ ] [`CHANGELOG.md`](CHANGELOG.md) updated with the version's
      entries.
- [ ] [`AUDIT_REPORT.md`](../engineering/AUDIT_REPORT.md) — any items closed in
      the release are marked **[FIXED]**.
- [ ] Docs site rebuilds (`docs/` mintlify preview).
- [ ] Marketing site rebuilds (`cd web && npx next build` — must
      complete with no errors).
- [ ] `recall.py --debug` boots cleanly on Windows + macOS +
      Linux (or whichever subset the release covers).
- [ ] Git tag created: `git tag -a v0.X.Y -m "Recall v0.X.Y"`.

## Repo split plan (deferred)

The brief asks for repository organisation into
`recall-core` / `recall-extension` / `recall-web` / `recall-docs`.
This is a major operation that needs maintainer + community
buy-in; the monorepo today carries enough coherence benefits that
the split should be **deferred until at least one of**:

- the launcher and the extension start being released on
  independent cycles, **or**
- the web team is genuinely separate from the engine team, **or**
- the contribution map shows persistent confusion over which
  subdirectory owns what.

Until then, the monorepo earns its keep: a single PR can touch
the engine + API + docs + marketing surface together, which is
what most engine changes need.

When the split happens, the recommended boundaries are:

| Repo | Owns | Releases on |
|---|---|---|
| `recall-core` | `apps/desktop/` + `apps/extension/` + `_smoke_api.py` | Independent version `MAJOR.MINOR.PATCH` |
| `recall-web` | `apps/web/` | Continuous deploy from `main` |
| `recall-docs` | `apps/docs/` | Continuous deploy from `main` |

The `apps/extension/` is bundled in `recall-core` because its
`host_permissions` is locked to the same port the API service
hosts; shipping them out of sync would break the loopback
contract. See [`REPO_STRUCTURE.md`](../engineering/REPO_STRUCTURE.md) for the
per-directory gate conditions for actually performing the
split.

## Release notes template

Markdown body for a GitHub release:

```markdown
## Recall v0.X.Y

**Channel:** stable | preview | nightly
**Released:** YYYY-MM-DD

### What's new

- One-line, user-facing summary of each notable change.
- Reference `CHANGELOG.md` for the full list.

### Bug fixes

- Same shape.

### Performance

- Numbers from `_smoke_api.py`'s perf sections, if changed.

### Upgrading

- Anything a user has to do manually (rare; default is "replace
  the binary and relaunch").

### Known issues

- Documented limitations the smoke test doesn't catch.
```
