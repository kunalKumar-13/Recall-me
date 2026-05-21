# Windows packaging

Produces **`Recall-Setup.exe`** — the single-double-click installer.

## What the user gets

Double-click `Recall-Setup.exe` → Next → Next → done. After that:

- Recall installed under `%LOCALAPPDATA%\Programs\Recall\` (per-user,
  **no admin prompt** — `PrivilegesRequired=lowest`).
- A Start-menu entry and an optional desktop shortcut.
- An optional **"Start Recall when I sign in"** entry (checked by
  default — a continuity tool that isn't running captures nothing).
- Recall launched straight into onboarding.

No terminal, no Python, no docs. First-run state (`~/.recall/`) is
created by the app itself on first launch.

## Build

```powershell
pwsh infra\packaging\windows\build.ps1
```

Two stages: PyInstaller bundles the app (`recall.spec` → `dist\Recall\`),
then Inno Setup wraps it (`recall.iss` → `dist\installer\Recall-Setup.exe`).

### Prerequisites (build machine, one-time)

- `pip install -r requirements.txt pyinstaller`
- [Inno Setup 6](https://jrsoftware.org/isdl.php) — provides `iscc`.

## Files

| File | Role |
|---|---|
| `recall.iss` | Inno Setup script — shortcuts, start menu, launch-on-login, first-run launch, silent-repair support |
| `build.ps1` | PyInstaller → Inno Setup, one command |
| `../../../recall.spec` | the PyInstaller spec (repo root) |
| `../assets/recall.ico` | installer + app icon — see `infra/packaging/assets/` |

## Silent repair

`Recall-Setup.exe /SILENT` reinstalls in place over a broken install
without prompting — the recovery path when a user's binary is
damaged. The extension's "Repair connection" CTA points users here.

## Code signing

`build.ps1` produces an **unsigned** installer; Windows SmartScreen
will warn on first run. Signing (an EV certificate + `signtool`) is a
separate, credentialed release step — see [`RELEASE.md`](../../../docs/release/RELEASE.md).
That gap is documented honestly in
[`SUPPORTED_PLATFORMS.md`](../../../docs/release/SUPPORTED_PLATFORMS.md).
