# Installing Recall

The grandmother test: **download, double-click, works.** No
terminal, no Python, no setup.

For the exact files and links, see [`DOWNLOADS.md`](DOWNLOADS.md).

---

## Windows

1. Download **`Recall-Setup.exe`**.
2. Double-click it. Click **Next**, then **Install**.
   - It installs per-user — **no admin password**.
   - Leave *"Start Recall when I sign in"* checked.
3. Recall opens straight into the first-launch screen.

That's it. Recall lives in the **system tray**; press **Ctrl + Space**
anywhere to open the launcher.

> Windows SmartScreen may show *"Windows protected your PC"* on the
> first run — Recall's installer is not yet code-signed. Click
> **More info → Run anyway**. Why this happens, and the plan to fix
> it, is in [`SUPPORTED_PLATFORMS.md`](SUPPORTED_PLATFORMS.md).

## macOS

1. Download **`Recall.dmg`**.
2. Open it and drag **Recall** onto the **Applications** folder.
3. Launch Recall from Applications.

Recall lives in the **menu bar** (no Dock icon). The first-launch
screen offers *"Start Recall when I sign in."*

> Gatekeeper may say *"Recall can't be opened because it is from an
> unidentified developer"* — the build is not yet notarised.
> **Right-click the app → Open**, then **Open** in the dialog. See
> [`SUPPORTED_PLATFORMS.md`](SUPPORTED_PLATFORMS.md).

## The browser extension (optional, recommended)

The extension feeds browser tabs, searches, and chats into Recall.
The popup detects whether Recall is installed and running, and
guides you — *Install Recall* / *Open Recall* / *Repair connection* —
so you never have to think about pairing.

Build and load it per
[`apps/extension/README.md`](../../apps/extension/README.md). A packaged
extension (Chrome Web Store) is a later release step.

---

## First launch — one screen

No wizard, no account, no login, no email. The first-launch screen
is four steps on one surface:

1. **Welcome.**
2. **Enable browser memory** (optional — you can do it later).
3. **Choose folders** to remember (Documents and Desktop are
   pre-checked).
4. **Done.**

Then work normally. Recall captures quietly; come back in a day or
two and the launcher shows what you can step back into. The full
expectation-setting walkthrough is [`PUBLIC_ALPHA.md`](../founder/PUBLIC_ALPHA.md).

## Run from source (developers)

Not the grandmother path — but if you want the source tree, the
five-command setup is [`apps/docs/install-3min.mdx`](../../apps/docs/install-3min.mdx).

## Uninstall

One minute, zero residue — [`apps/docs/uninstall.mdx`](../../apps/docs/uninstall.mdx).
Recall is safe to try because it is trivial to remove.
