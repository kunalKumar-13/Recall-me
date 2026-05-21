# Sample workflow — your first week with Recall

Recall is invisible until it has something to show you. This page
sets the expectation for **what each day actually looks like**.

The long version is
[`docs/founder/FIRST_WEEK.md`](../docs/founder/FIRST_WEEK.md).

---

## Day 0 — install

- Run [`INSTALL.md`](INSTALL.md).
- Press **Ctrl + Space**. The launcher opens — empty, with one
  line: *"Recall is listening. Come back in a day or two."*
- **That is the right state.** Recall has nothing to surface yet.

Close the launcher. Go back to work.

## Day 1 — work normally

- Edit files in the folders you picked.
- Open browser tabs.
- Search the web.
- Open AI chats (Claude, ChatGPT, …).
- Press **Ctrl + Space** at the end of the day. The launcher may
  still be empty. **That is also normal.**

What you should *not* do:

- ❌ Click around looking for a settings menu — it is in the tray.
- ❌ Wait for a popup — there is no popup.
- ❌ Open a "memory" or "history" view — Recall has none.
- ❌ Tag, label, or organise anything — Recall has no tags.

You should treat Recall like a smoke alarm: forget it is there.

## Day 2-3 — the first useful launcher

By now Recall has 24-72 hours of events. Press **Ctrl + Space**:

```
┌─ Continue where you left off ──────────────────────┐
│  WebSocket retry debugging                          │
│  2 tabs · 2 files · last touched 2d ago             │
│  [Resume]                                           │
└─────────────────────────────────────────────────────┘
┌─ Active investigations ─────────────────────────────┐
│  Healthcare startup research                        │
│  Started 2d ago · 3 sessions · 12 events            │
└─────────────────────────────────────────────────────┘
┌─ On your radar ─────────────────────────────────────┐
│  Postgres index tuning                              │
│  noticed across 2 days                              │
└─────────────────────────────────────────────────────┘
```

Three sections, each named in plain English. Click **Resume** on
a recovery card — Recall reopens the **files and tabs** you had
open when you left that work.

That moment — *Resume click → my work is back* — is the product.

## Day 4-6 — the test that matters

Mid-week, on a normal work day:

1. Mid-afternoon, switch tasks. **Don't bookmark anything. Don't
   write a note.** Just leave the work and do something else.
2. The next morning, before you reach for your bookmarks or
   browser history, press **Ctrl + Space**.

Two outcomes:

- ✅ Recall shows the work you abandoned, with the right tabs and
  files. You click Resume. *This is the win you should feel.*
- ⚠️ Recall shows something else, or nothing useful. *This is the
  data we need.* Log it in [`FEEDBACK.md`](FEEDBACK.md) under
  *trust* (with a one-line note on what you were doing).

## Day 7 — feedback

End of week one:

1. Run `recall doctor` (Command Prompt → `%LOCALAPPDATA%\Programs\Recall\Recall.exe doctor`).
   Take a screenshot.
2. Run `recall stats --export` to produce a `stats.json` file.
   This is the **only** thing you ever send back — see
   [`TRUST.md`](TRUST.md).
3. Fill out [`FEEDBACK.md`](FEEDBACK.md).
4. Email or share the three things with your alpha contact.

That's the alpha-001 commitment.

---

## What Recall is *not* doing during your week

This is the calm-software list. If you find yourself wondering "is
something wrong?", check this first:

- ❌ Sending data anywhere. Not once.
- ❌ Showing notifications.
- ❌ Asking you to organise, tag, or rate anything.
- ❌ Summarising your work into prose.
- ❌ Recommending things to read.
- ❌ Auto-completing your queries.

If any of these happen, that is a contract violation. File it in
[`FEEDBACK.md`](FEEDBACK.md) under *trust*.

## The honest definition of success

After one week:

| If you... | Then Recall... |
|---|---|
| reach for the launcher reflexively | earned a place on your machine |
| Resume into your morning work once | proved the loop |
| have nothing to report | gave you back the time you would have spent organising memory |
| want to uninstall it | uninstall it. *That is a fine outcome.* |

A continuity tool that does not earn trust on first contact does
not earn it at all. So we'd rather lose you in week one than fake
the win.
