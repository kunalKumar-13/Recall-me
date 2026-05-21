# Trust — the contract before you run Recall

Recall watches files, browser tabs, and searches. That is a lot of
trust to grant. This page is the **short** version of what you are
agreeing to. The long, line-by-line version is
[`docs/engineering/TRUST_LEDGER.md`](../docs/engineering/TRUST_LEDGER.md).

---

## The one-line promise

> Recall sees a lot, on your machine, to be useful. It can export a
> dozen numbers, only when you ask. Everything in between stays
> exactly where it was: yours.

## What Recall sees

Only inside `%USERPROFILE%\.recall\`:

- The **paths and contents** of the folders you picked on day 1.
- The **URLs and titles** of browser tabs (if you enabled the
  extension). Never the page contents.
- The **search queries** you ran in your browser.
- The **AI-chat URLs and titles** you visited (claude.ai,
  chat.openai.com, …). Never the conversation.
- The **files you opened**.
- The **counters** — a recovery shown, a Resume clicked.

All of it is plain JSON. Open it in Notepad. Delete it with the
Recycle Bin. **Deleting `.recall\` is a complete reset.**

## What Recall never sees

- Anything outside the folders you chose.
- Page **contents** of browser tabs (the extension reads URL +
  title; it does not read the DOM).
- Incognito or private windows.
- Keystrokes, screen, clipboard, microphone — Recall hooks none of
  these.

## What can leave the machine

**Exactly one thing**, and only when you run the command and you
send the file:

```
recall stats --export
```

This writes a `stats.json` file containing a dozen counts and
rates — *install date, days active, recoveries shown, recoveries
accepted, …* — plus the Recall version. **No filenames, no URLs,
no queries, no sub-day timestamps, no device identifier.**

You email or paste that file to the alpha contact. Or you don't.

## What can never leave the machine

| Never exported |
|---|
| File paths, names, contents |
| URLs, domains, page titles |
| Search queries, chat titles |
| Per-event timestamps (export finest grain is the day) |
| Device id, hostname, user id, hash |
| The event log itself (`.recall\events\*.jsonl`) |

## How to verify this yourself

If you do not trust the prose, check the code:

1. **The export is one function.** Read `build_export()` in
   `app/core/stats.py`. Its output is the entire exportable
   surface. If a field is not built there, it cannot leave.
2. **There is no network code on the export path.** `recall stats`
   writes a file; it opens no socket.
3. **Recall's only outbound call, anywhere,** is the one-time
   embedding-model download on first run (~80 MB from Hugging
   Face). After that, `local_files_only=True` and Recall never
   touches the network again unless you reinstall.

If you `grep` the repo for `requests.post`, `analytics`, or a
Recall server URL, you will find none — because none exists.

## The reset button

If at any point you want a clean slate:

```
1. Quit Recall (tray icon → Quit).
2. Delete %USERPROFILE%\.recall\
3. (Optional) Uninstall via Settings → Apps.
```

Step 2 is the **full memory wipe**. Step 3 is the program. They
are independent on purpose.

## If anything in this page is false

Any of these would be a **contract violation**, not a feature:

- A network request to anywhere besides `127.0.0.1:4545` (after the
  first-run model download).
- A captured filename, URL, or query landing in `stats.json`.
- A recovery card for a topic you never worked on.
- Any user-facing string containing "AI memory", "smart memory",
  "AI assistant", or a productivity score.

File these in [`FEEDBACK.md`](FEEDBACK.md) under *trust*. They are
the bugs that block public alpha.
