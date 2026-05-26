# INSTALL — Recall v0.1.0-rc1

The shortest path from a fresh machine to the
launcher opening with a real capture.

---

## Windows — recommended path

### 1. Download

Grab `Recall-Setup-lite.exe` from
[the GitHub releases page](https://github.com/kunalKumar-13/Recall-me/releases/latest).

The lite installer is ~216 MB. The full installer
is ~261 MB and identical in behaviour — pick lite
unless your environment forbids the runtime
dependency-pruning step.

### 2. Run the installer

Double-click `Recall-Setup-lite.exe`.

You'll see a single SmartScreen warning the first
time (we're not yet signed with an EV cert). Click
**More info → Run anyway**.

The installer drops Recall into
`C:\Program Files\Recall\` and registers:

- A Start-menu entry: **Recall**
- A tray icon that boots on next sign-in
- A loopback API on `127.0.0.1:4545`

Nothing else. No services, no scheduled tasks, no
auto-update daemon.

### 3. First launch

Start menu → **Recall**. Within ~3 seconds you'll
see the tray icon appear. Click it (or press the
hotkey from settings) to open the launcher window.

The launcher will be **empty** on first run — no
events captured yet. The empty state explains
itself in one line.

### 4. Install the browser extension

Open Chrome (or Edge / Brave / Arc):

1. Visit `chrome://extensions`.
2. Toggle **Developer mode** on (top-right).
3. Click **Load unpacked**.
4. Pick `C:\Program Files\Recall\extension\popup\`.

The Recall icon appears in your toolbar. Click it
once — the popup shows "connecting" then
"connected" within a second.

### 5. Browse normally

Open ChatGPT, GitHub, Google. Browse for 2-3
minutes. Each visit becomes a `browser_visit` (or
`chat_session`) event in `~/.recall/events/`.

### 6. Open the launcher

The tray icon's hotkey (default `Alt+Space`, see
**Settings → Hotkey**) opens the launcher. You'll
now see your recent activity in the digest.

That's the install. You're ready.

---

## macOS — preview only

The macOS build is unsigned and unsupported in
RC1. See
[`docs/release/MAC_OWNER_NEEDED.md`](../docs/release/MAC_OWNER_NEEDED.md).
If you absolutely need the Mac path, follow that
note's manual `.dmg` flow and accept the
Gatekeeper warning.

---

## Linux — not packaged

Linux runs from source. See the "from-source" path
below.

---

## From source — every platform

For contributors and the bleeding-edge cohort.

```bash
git clone https://github.com/kunalKumar-13/Recall-me.git
cd Recall-me

# Python 3.13+
python -m venv .venv
source .venv/bin/activate     # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt

# First boot — the embedding model downloads once (~80 MB).
python recall.py
```

The extension's source is in `apps/extension/ui/`.
Build the popup bundle:

```bash
cd apps/extension/ui
npm install
npx vite build
```

The build emits to `apps/extension/popup/assets/`.
Point Chrome at `apps/extension/popup/` to load it.

---

## Verify the install

After the launcher opens once, from any shell:

```bash
python recall.py doctor
```

You should see a `GREEN` block for every check:
**config**, **events**, **daemon**, **extension**,
**installer**. Yellow warnings are fine; reds
should be reported (see "Where to file bugs" in
[CHANGELOG_RC1.md](CHANGELOG_RC1.md)).

For an immediate populated digest without waiting
for real captures:

```bash
python recall.py demo run
$env:RECALL_DEMO_MODE = "1"     # PowerShell
python recall.py
```

See [`../DEMO_MODE.md`](../DEMO_MODE.md) for the
full demo flow.

---

## Where things live

| Path                              | Contents                                |
|-----------------------------------|-----------------------------------------|
| `C:\Program Files\Recall\`        | The installed app                        |
| `~/.recall/events/`               | Per-day JSONL event logs                 |
| `~/.recall/chroma/`               | Vector index for file search             |
| `~/.recall/config.json`           | Settings (folders, toggles, hotkey)      |
| `~/.recall/instance.lock`         | Single-instance guard                    |
| `~/.recall/events-demo/`          | Demo trace (only if you ran `demo run`)  |

Deleting `~/.recall/` is a full reset and is
always safe.

---

## Uninstall

**Windows:** Settings → Apps → Recall → Uninstall.

This removes the installed app and the registry
entries. It does **not** touch `~/.recall/` — your
event log and indexes survive. Delete that
directory by hand if you want a complete wipe.

**Browser extension:**
`chrome://extensions` → Recall → Remove.

---

## Network traffic

Recall makes exactly **one** outbound network call
in its lifetime: the first-boot download of the
sentence-transformers embedding model (~80 MB,
from Hugging Face). After that, every byte stays
on your machine.

The local API binds to `127.0.0.1:4545` (loopback
only — not reachable from your network). The
extension talks to it from the same machine.

---

## Help

| Symptom                                      | Fix                                            |
|----------------------------------------------|------------------------------------------------|
| Tray icon never appears                      | Run `python recall.py --debug` and read stderr |
| Extension says "disconnected" forever        | Daemon isn't running. Start Recall from the Start menu. |
| `recall doctor` shows a red                  | Check the line's hint; most resolve by re-running the installer |
| Capture appears to do nothing                | `recall capture status` shows the most recent event timestamp |
| Want to start over                           | Uninstall + delete `~/.recall/`; reinstall    |

The [CHANGELOG_RC1.md](CHANGELOG_RC1.md) has the
canonical bug list. The
[KNOWN_ISSUES.md](KNOWN_ISSUES.md) explains the
ones that ship with RC1.
