# TRUST_LEDGER.md — what Recall sees, and what it can never export

Recall is a continuity tool that reads your files, tabs, searches,
and chats. That is a lot of trust to ask for. This ledger is the
exact, enumerated answer to *"what does it do with all that?"* —
written so a sceptical user can check every claim against the
source.

Two columns matter most: what Recall **sees** (on your machine) and
what Recall **can export** (what is ever allowed to leave it). They
are deliberately, hugely different.

---

## What Recall sees — on your machine, in `~/.recall/`

| It sees | Where it lives | Why |
|---|---|---|
| File paths + contents of indexed folders | `chroma/` (local vector index) | so search can find a file by meaning |
| Browser tab URLs + titles | `events/*.jsonl` | so a tab is part of an investigation |
| Search queries you ran | `events/*.jsonl` | so "I was researching X" is recoverable |
| AI-chat session URLs + titles | `events/*.jsonl` | so a chat is part of an investigation |
| Files you opened | `events/*.jsonl` | so recovery can reopen them |
| Launcher queries you typed | `events/*.jsonl` | episodic recall of past searches |
| Interaction counts | `counters.json` | a recovery shown, a Resume clicked |

All of it is plain JSON / JSONL — open it in any editor, delete it
with `rm`. Deleting `~/.recall/` is a complete reset.

## What Recall never sees

| It never sees | Because |
|---|---|
| Anything outside the folders you chose | the indexer only walks your selected folders |
| Page *contents* of browser tabs | the extension reads URL + title only, never the DOM |
| Incognito / private windows | the browser hides them; the extension also checks |
| Keystrokes, screen, clipboard, microphone | Recall hooks none of these |
| Other users on the machine | state is per-user under your home directory |

## What can leave the machine

Exactly **one** thing, and only when *you* run the command and
*you* send the file:

- **`recall stats --export`** → a `stats.json` of the form in
  `app/core/stats.py`'s `build_export()`: a dozen **counts and
  rates**, a Recall version, and a date. That is the whole payload.

It is generated on demand, written to a local file, and goes
nowhere unless you choose to share it. `apps/admin/import_stats.py`
*re-validates* it on the founder's side and rejects anything that
is not counts-only.

## What can never leave the machine

| Never exported | Even though Recall sees it locally |
|---|---|
| File paths, names, or contents | yes — but they never enter `stats.json` |
| URLs, domains, page titles | yes — never exported |
| Search queries, chat titles | yes — never exported |
| Per-event timestamps | the export's finest time grain is the **day** |
| Any identifier — device id, hostname, user id, hash | none is collected, so none can be exported |
| The event log itself (`events/*.jsonl`) | never read by the export path |

## How to verify this ledger yourself

1. **The export path is one function.** Read `build_export()` in
   `app/core/stats.py` — its output is the entire exportable
   surface. If a field is not constructed there, it cannot leave.
2. **The import is a gate.** `apps/admin/import_stats.py` rejects
   any file with a non-numeric value or an unexpected key.
3. **There is no network code on the export path.** `recall stats`
   writes a file; it opens no socket. Recall's *only* outbound call
   anywhere is the one-time embedding-model download on first run.
4. **`grep` the repo.** There is no analytics SDK, no telemetry
   endpoint, no `requests.post` to a Recall server — because there
   is no Recall server.

## The promise, in one line

> Recall sees a lot, on your machine, to be useful. It can export
> a dozen numbers, only when you ask. Everything in between stays
> exactly where it was: yours.

Cross-referenced by [`FOUNDER_DASHBOARD.md`](../founder/FOUNDER_DASHBOARD.md),
[`FOUNDER_METRICS.md`](../founder/FOUNDER_METRICS.md), and the charter
([`CLAUDE.md`](../../CLAUDE.md) § *Things we will not build*).
