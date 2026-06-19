# Install — for the alpha cohort

The shortest install path. 10 minutes from
download to a green daemon dot in your browser.

If you've installed before, jump to
[DAY0.md](DAY0.md). Otherwise, follow each step.

---

## Step 1 — download (1 min)

Grab `Recall-Setup-lite.exe` from
[the GitHub releases page](https://github.com/kunalKumar-13/Recall-me/releases/latest).

- `Recall-Setup-lite.exe` is recommended (~216 MB).
- `Recall-Setup-full.exe` is identical product,
  just a larger bundle (~261 MB).

If you're on a Mac, you're on the unsigned
preview path — read
[`docs/release/MAC_OWNER_NEEDED.md`](../../docs/release/MAC_OWNER_NEEDED.md)
first.

## Step 2 — run the installer (3 min)

Double-click `Recall-Setup-lite.exe`.

**SmartScreen will warn you.** RC1 is not yet EV-signed.
Click **More info → Run anyway**.

The installer drops Recall into
`C:\Program Files\Recall\`. Within ~30 seconds
of finishing, you'll see a tray icon appear in
the system tray.

That's the desktop side installed.

## Step 3 — install the extension (3 min)

Open Chrome (or Edge / Brave / Arc):

1. `chrome://extensions` (paste this in the URL bar).
2. Top-right: **Developer mode** → ON.
3. Click **Load unpacked**.
4. Navigate to `C:\Program Files\Recall\extension\popup\`.
5. Pick the `popup` folder and confirm.

The Recall icon appears in your toolbar.

## Step 4 — verify (1 min)

Click the Recall icon in your browser toolbar.

You should see:

- A **green dot** in the popup header (daemon
  connected).
- The copy "Recall is watching locally" (or
  similar — empty state).

If the dot is grey, the desktop app isn't
running. Open the Start menu and click
**Recall**.

From any shell:

```
python recall.py doctor
```

Should print **5 GREEN** lines and ≤4 YELLOW.
YELLOWs are usually opt-in features — see
[`release/INSTALL.md`](../../docs/release/rc1/INSTALL.md)
"verify the install" section if curious.

## Step 5 — first capture (2 min)

Open three tabs in your browser:

- Any GitHub repo
- A Google search
- ChatGPT (or any chat tool)

Wait 10 seconds. Then:

```
python recall.py capture status
```

Should show **`events today` > 0**.

If it says zero events, the extension didn't
pair. Reload it from `chrome://extensions`.

---

## Done

You're installed and capturing. The interesting
part starts when you **leave** and come back —
see [DAY0.md](DAY0.md).

## Optional — try the demo right now

If you want to see what the populated state
looks like before earning your own captures:

```
python recall.py demo run
$env:RECALL_DEMO_MODE = "1"   # PowerShell
python recall.py              # restart launcher
```

The launcher will now show a deterministic
30-event story (a WebSocket investigation, a
proposal draft, a research deep-dive) with a
recovery card at the top.

Reset when done:

```
$env:RECALL_DEMO_MODE = $null
python recall.py demo reset
```

Full demo doc:
[`../../DEMO_MODE.md`](../../docs/product/DEMO_MODE.md).

---

## What you do next

| If…                              | Open                                       |
|----------------------------------|--------------------------------------------|
| Install worked, daemon green     | [DAY0.md](DAY0.md)                         |
| Doctor showed RED                | File an issue with the doctor output       |
| Tray icon never appears          | Run `python recall.py --debug` and email stderr |
| Extension says disconnected      | Reload the extension; restart Recall       |

The
[`KNOWN_ISSUES.md`](../../docs/release/rc1/KNOWN_ISSUES.md)
covers the bugs RC1 ships with. None of them
should block install.
