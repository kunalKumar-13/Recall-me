# Downloads

Every release ships from the GitHub Releases page:

> **https://github.com/kunalKumar-13/Recall-me/releases/latest**

Pick your platform, download the one file, and follow
[`INSTALL.md`](INSTALL.md).

---

## Release artifacts

| Platform | File | What it is |
|---|---|---|
| **Windows 10 / 11 (x64)** | `Recall-Setup.exe` | Double-click installer — shortcuts, start menu, optional launch-on-login |
| **macOS 11+ (Apple Silicon)** | `Recall.dmg` | Drag-to-Applications disk image |
| **macOS 11+ (Intel)** | *run from source* | A universal `.dmg` is a release gate — see below |
| **Linux** | *run from source* | [`apps/docs/install-3min.mdx`](../../apps/docs/install-3min.mdx) |

The embedding model (~80 MB) is **not** in the download — Recall
fetches it once, on first run, into a local cache. After that it
never touches the network.

## Verifying a download

Each release lists a **SHA-256** for every artifact. On Windows:

```powershell
Get-FileHash .\Recall-Setup.exe -Algorithm SHA256
```

on macOS / Linux:

```bash
shasum -a 256 Recall.dmg
```

Compare against the value on the release page.

## Signing status (read this)

Current builds are **not yet code-signed**:

- **Windows** — SmartScreen will warn on first run.
- **macOS** — Gatekeeper will warn (unidentified developer).

This is a known gap, not a risk you are meant to ignore — verify the
SHA-256, and read the *why* and the fix plan in
[`SUPPORTED_PLATFORMS.md`](SUPPORTED_PLATFORMS.md) and
[`RELEASE.md`](RELEASE.md).

## Building it yourself

You never have to trust a binary. The installers are reproducible
from source:

- Windows — [`infra/packaging/windows/`](../../infra/packaging/windows/)
- macOS — [`infra/packaging/macos/`](../../infra/packaging/macos/)
