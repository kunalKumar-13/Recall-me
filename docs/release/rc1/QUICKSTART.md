# QUICKSTART — Recall in 5 minutes

> Install. Open extension. Browse. Leave. Resume.
> That's the entire loop.

This file walks you through the five steps that
define what Recall is. If you're holding RC1 and
want to know whether the product works for you —
this is the page.

Time budget: 5 minutes of attention + a coffee
break.

---

## 0. Prerequisites

- Windows 10 or 11
- Chrome / Edge / Brave / Arc
- ~250 MB free disk

If you don't have RC1 yet:
[INSTALL.md](INSTALL.md).

---

## 1. Install

```
Run Recall-Setup-lite.exe → finish wizard → see tray icon
```

90 seconds. Full path in [INSTALL.md](INSTALL.md).

---

## 2. Open the extension

1. `chrome://extensions` → **Developer mode** on
   → **Load unpacked** → pick
   `C:\Program Files\Recall\extension\popup\`.
2. Click the Recall icon in your toolbar.

You'll see one of:

- **Loading** (first health check in flight) →
  resolves in <1 s.
- **Connected** (header dot turns from grey to
  green) → ready.
- **Empty** ("Recall is watching locally") → your
  first events haven't landed yet; this is fine.

If you ever see "Disconnected," the desktop app
isn't running. Start it from the Start menu.

---

## 3. Browse

Spend two minutes doing what you'd normally do:

- Open a couple of GitHub repos
- Search Google for something
- Drop into ChatGPT and ask one question
- Switch to a code editor and open a file or two

Each action becomes one row in your
`~/.recall/events/YYYY-MM-DD.jsonl` — captured
locally, hand-readable, no cloud round-trip.

Check what got captured (any shell):

```bash
python recall.py capture status
```

You should see today's event count and the most
recent event timestamp.

---

## 4. Leave

Close the launcher. Close the popup. Go to a
meeting, lunch, or sleep. The point of Recall is
that **it works while you're not looking** — the
capture pipeline keeps writing events as long as
the daemon is up.

The next time you open the launcher (tray icon
or hotkey, default `Alt+Space`):

- The digest now shows what you were just doing.
- Up to 5 recent memories with one-line context.
- Up to 3 investigation threads (topical groupings
  the engine inferred from your events).
- A trust row at the bottom telling you how much
  of your day Recall saw.

---

## 5. Resume

This is the moment that justifies the whole
product.

If your activity formed a coherent unfinished
thread (≥4 events on a topic, recent enough,
above the trust gate), you'll see a **Continue**
card at the top of the launcher.

Click it. The launcher hands the recovery's
URL + file list to your OS:

- Browser URLs reopen in tabs.
- Local files open in your default editor.
- You're back in the context, in one click.

If you don't see a Continue card on your first
session, that's normal — recovery is
deliberately conservative. It waits for evidence
that a thread is *interrupted work*, not casual
browsing. Either keep working for another session
or run the demo (next section).

---

## Try it without waiting — `recall demo run`

If you want to see the full populated experience
right now without building up history:

```bash
python recall.py demo run
$env:RECALL_DEMO_MODE = "1"    # PowerShell
python recall.py               # restart launcher
```

The launcher now shows 30 demo events across 12
sessions: a WebSocket investigation, a proposal
draft, a research deep-dive. A recovery card sits
at the top.

Reset when done:

```bash
$env:RECALL_DEMO_MODE = $null
python recall.py demo reset
```

Full demo doc: [`../DEMO_MODE.md`](../../product/DEMO_MODE.md).

---

## What you should now believe

- Recall captures your real activity, locally,
  without configuration.
- It composes that activity into threads without
  asking you to tag anything.
- When it has a confident "continue this" call,
  it offers one — and one click restores the
  context.
- When it doesn't have one, it stays quiet.

That's the entire promise. If you got here and
something feels off, see
[KNOWN_ISSUES.md](KNOWN_ISSUES.md) —
there's a real chance it's a documented gap, not
a bug in your install.

---

## Next steps

- [DEMO_FLOW.md](DEMO_FLOW.md) — the exact path for
  showing Recall to someone else.
- [KNOWN_ISSUES.md](KNOWN_ISSUES.md) — what RC1
  ships broken.
- [../docs/architecture/](../../architecture)
  — how the seven layers compose.
- [../CLAUDE.md](../../../CLAUDE.md) — what Recall will
  never be.
