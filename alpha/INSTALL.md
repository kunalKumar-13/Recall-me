# Install Recall — alpha walkthrough

Goal: **download → working app in under 3 minutes**, no terminal.

## Windows 10 / 11

### 1. Download

You should have been handed a copy of **`Recall-Setup.exe`** (the
installer) or a link to the alpha download.

> If you do not have `Recall-Setup.exe`, ask your alpha contact —
> the public download page is not live yet.

### 2. Run it

Double-click `Recall-Setup.exe`.

- **SmartScreen warning?** Click *More info* → *Run anyway*. The
  installer is not yet code-signed; *why* is in
  [`LIMITATIONS.md`](LIMITATIONS.md).
- **No admin password.** Recall installs *per-user*, into
  `%LOCALAPPDATA%\Programs\Recall\`. It cannot, and does not, touch
  the rest of your system.
- **Two checkboxes.** Leave both checked:
  - *Create a desktop shortcut*
  - *Start Recall when I sign in*

Click **Install**. The installer runs for ~20 seconds.

### 3. First launch

Recall opens automatically. You see one screen — the first-launch
panel — with three steps:

1. **Welcome.** Read the one-line promise.
2. **Browser memory** (optional). Skip for now if you'd like; you
   can turn it on later in Settings.
3. **Choose folders.** Documents and Desktop are pre-checked. Add
   or remove as you like. *These are the only folders Recall will
   ever read.*

Click **Done**.

### 4. Where Recall lives

- **System tray.** Recall is the small icon in the bottom-right
  corner of your screen. Right-click for Settings or Quit.
- **Ctrl + Space.** From anywhere, this opens the launcher. Today
  it is empty by design — Recall has nothing to surface yet.

That is the install. **Now go work normally for a day.** Come back
to the launcher in 24-48 hours.

---

## Browser extension (recommended, optional)

The extension adds your browser to what Recall sees. Without it,
Recall watches files; with it, Recall watches files + tabs +
searches. Most of the interesting recovery happens once both are on.

For the alpha cycle, the extension is loaded as an *unpacked*
extension (the Chrome Web Store listing is a later step):

1. Unzip `recall-extension.zip` (or use the `apps/extension/`
   folder from this packet).
2. Open `chrome://extensions` (or `edge://extensions`).
3. Toggle **Developer mode** on.
4. Click **Load unpacked** → select the unzipped folder.
5. The popup should show **Connected** when Recall is running.

If the popup says *Recall not found* or *Disconnected*, see
[`LIMITATIONS.md`](LIMITATIONS.md) → *Extension pairing* — and
include the popup state in `FEEDBACK.md`.

## macOS

The macOS build is **not** ready for alpha — `Recall.dmg` has not
been produced or verified. macOS testers, please wait. See
[`docs/release/MAC_VERIFICATION.md`](../docs/release/MAC_VERIFICATION.md)
for the honest matrix.

## Linux

Source-only. Five commands at
[`apps/docs/install-3min.mdx`](../apps/docs/install-3min.mdx).

---

## Did it work?

`recall doctor` (open a Command Prompt, run
`%LOCALAPPDATA%\Programs\Recall\Recall.exe doctor`) should return
mostly **GREEN**.

- **Daemon RED** → Recall is not running. Start it from the
  desktop shortcut.
- **Extension YELLOW** → expected for the first 24 hours; comes
  back GREEN after some browsing.
- **Protocol YELLOW** → the `recall://` deep-link is not registered
  yet (known gap; the *Open Recall* button in the extension popup
  falls back to a focus signal).

Anything red after a full day is a bug — file it in
[`FEEDBACK.md`](FEEDBACK.md).

## Uninstall

If you decide to remove Recall:

1. Settings → Apps → search "Recall" → Uninstall.
2. (Optional) Delete `%USERPROFILE%\.recall\` to remove your local
   memory data. The installer **never** deletes this folder — your
   data is yours.

Recall is safe to try because it is trivial to remove.
