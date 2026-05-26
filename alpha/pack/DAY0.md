# Day 0 — the first hour

You're installed. Daemon green. Extension paired.

**Goal for the next hour:** browse normally.
That's the whole task.

---

## What to do

1. **Open your normal work.**
   - Project repos in your browser
   - Whatever doc you're writing
   - Your IDE, your notes, your inbox
   - A search or two
2. **Do not over-think it.** Don't curate your
   browsing for the demo. Recall is meant to
   work on real, messy activity, not on a
   showcase.
3. **Leave the launcher closed.** It needs
   data to be useful. The data is the next
   hour of your normal browsing.

That's it. There is no setup step you missed.

---

## What's happening under the hood

Every browser tab you open generates one
`browser_visit` event in
`~/.recall/events/YYYY-MM-DD.jsonl`. ChatGPT
conversations are tagged `chat_session`. Google
searches are `browser_search`. Local-file work
(if you have folders watched in Settings) is
captured as `open` events.

You can read these JSONL files with `cat`.
They're plain text. The product is built on the
principle that you can inspect everything Recall
knows about you in a text editor.

To watch the file grow:

```powershell
# PowerShell
Get-Content $env:USERPROFILE\.recall\events\$(Get-Date -Format yyyy-MM-dd).jsonl -Wait

# or for the count
python recall.py capture status
```

---

## When to open the launcher

Wait until you've **left and come back**. The
launcher's interesting state is the *return* —
when it has a few hours of activity to compose
into threads.

If you open it now (Alt+Space), you'll see:

- A search bar
- A short "On your radar" digest with a row or
  two of recent activity
- A quiet trust row at the bottom

It will not feel magical yet. That's expected.

---

## Hotkeys to know

| Shortcut       | Action                       |
|----------------|------------------------------|
| `Alt+Space`    | Open launcher (configurable in Settings) |
| `Esc`          | Close launcher               |
| `Ctrl+K`       | Focus the search bar         |
| `Ctrl+,`       | Open Settings                |
| `Enter`        | Open the highlighted result  |

---

## One thing to try before leaving

In your browser, open the Recall extension popup
once. Note:

- The **green daemon dot** (top-left header).
- The **count of events captured today** if
  populated.
- The **Continue card** if it's already inferred
  one.

Even if there's no Continue card, the popup
should feel calm — no banners, no badges, no
red dots.

If you see a **search overlay** by pressing
`Cmd/Ctrl+K`, try typing two letters and see if
anything comes back. (It's reading your own
events — not the web.)

---

## What to write down

If anything in the first hour made you:

- pause to figure out what was happening
- want a button that wasn't there
- worry about privacy
- feel something specific (good or bad)

… open [FEEDBACK.md](FEEDBACK.md) and jot it
down. Five-word notes are fine. We will read
every word.

---

## What you do next

| When                            | Open                          |
|---------------------------------|-------------------------------|
| Hour 1 is over, you're moving on | (nothing — go work)          |
| Tomorrow morning                | [DAY1.md](DAY1.md)            |
| Something broke                 | [UNINSTALL.md](UNINSTALL.md) (or file an issue) |
