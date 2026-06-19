# Phase 8F · Track A — Capture truth

**Commit:** `b059471` · 2026-05-26
**Files:** `apps/extension/background.js` (+103 / -14)
+ `apps/extension/_track_a_verify.js`
+ `apps/extension/_track_a_verify_defer.js`

---

## Problem

Two truth gaps in the browser-side capture path:

### 1. SPA titles were captured before they settled

`chrome.tabs.onUpdated` fires when a tab finishes
loading (`status === "complete"`). At that
instant, `tab.title` is usually the *initial*
title — a generic placeholder like `"ChatGPT"`,
`"GitHub"`, `"Pull Request"`, `"Notion"`. SPAs
rewrite the title to something specific
(`"ChatGPT — explain JWT auth flow"`,
`"Pull Request #42 — fix capture truth"`) within
~1 second.

The old code sent the event immediately at
`complete`. Result: every chat session, every
GitHub PR, every Notion doc landed in
`~/.recall/events/` with the placeholder title.

This wasn't a missing-event problem — the URL
was correct, the kind was correct, the
timestamp was correct. It was a **title** truth
problem. The launcher's "On your radar"
digest displayed "ChatGPT · 14:32" rows
instead of "ChatGPT — JWT auth · 14:32" rows.

Audit of the live event log on this box (30 d):

```
chat_session events    : 22
unique titles          : 17
generic "ChatGPT" only : 11  (50%)
specific title         : 11  (50%)
```

About half the chat sessions had no useful title.

### 2. Modern AI chat surfaces fell back to browser_visit

`CHAT_DOMAINS` listed only `chatgpt.com`,
`chat.openai.com`, `claude.ai`. Visits to
Gemini, Copilot, Mistral chat, DeepSeek, Grok,
Poe, t3.chat were captured as generic
`browser_visit` events with no `platform` field.

Downstream:

- The launcher's chat-session count
  under-reported actual AI usage.
- The recovery engine's "chat-heavy threads
  earn extra trust" signal was blind to these
  platforms.
- The trust copy ("Recall is watching locally")
  in the popup was technically accurate for
  these sites but the per-platform breakdown
  in the daily-loop log wasn't.

On this dev box the gap was latent
(`chat_session.platform = {'chatgpt'}` only),
which is why 8C / 8D / 8E's BUG-003 audit
didn't surface it directly — the user simply
doesn't use Gemini today. But the day a tester
does, their work gets misclassified.

---

## Change

One file edited, two helper files added. Net 103
insertions / 14 deletions in `background.js`.

### 1. Title-settle defer (`_scheduleFire`)

Replaced the immediate-send + 800 ms dedupe with
a per-tab settle state machine:

```
On (load complete OR title update) for a tab:
  if pending entry exists with same URL:
    reset settle timer to SETTLE_MS = 1500 ms
    update title to latest seen
  if pending entry exists with different URL:
    fire prior URL now (with last-known title)
    start fresh settle for new URL
  else:
    schedule first fire at SETTLE_MS

Cap the total wait at MAX_WAIT_MS = 4000 ms so a
hyperactive title-poking tab still emits.

On tab close:
  emit whatever was pending immediately
  (work never silently vanishes if a user
  closes a tab during the settle window).
```

Captures the *settled* title, not the initial
one. The dedupe behaviour that the old 800 ms
debounce provided is now an emergent property
of the settle: rapid duplicate
`status=complete` events on the same URL just
keep resetting one timer, then fire once.

### 2. Extended `CHAT_DOMAINS`

Added 8 modern AI surfaces to the chat
allowlist, each with its own platform tag in
the payload:

| domain                       | platform tag |
|------------------------------|--------------|
| gemini.google.com            | gemini       |
| aistudio.google.com          | gemini       |
| copilot.microsoft.com        | copilot      |
| chat.deepseek.com            | deepseek     |
| chat.mistral.ai              | mistral      |
| grok.com                     | grok         |
| poe.com                      | poe          |
| t3.chat                      | t3           |

Existing `chatgpt` and `claude` tags
unchanged so historical data lines up.

The `gemini.google.com` case is the most
important one — without the explicit allow it
would have been captured as a generic
`browser_visit` (the search-engine matcher only
fires when `?q=` is set, and Gemini's chat URL
doesn't have one). With the change it correctly
becomes `chat_session` with `platform=gemini`.

---

## Verify

Two deterministic harnesses checked in, both
exit 0:

```
$ node apps/extension/_track_a_verify.js
... 16 pass, 0 fail

$ node apps/extension/_track_a_verify_defer.js
... 12 pass, 0 fail
```

### `_track_a_verify.js` — classify() coverage

16 URL fixtures exercised against `classify()`,
asserting `(endpoint, platform-or-engine)` for
each:

- 11 chat URLs across 11 platform tags ✅
- 2 search URLs (google, duckduckgo) ✅
- 3 generic browse URLs (github, stackoverflow,
  stitch — all stay `browser_visit`) ✅

### `_track_a_verify_defer.js` — defer state machine

12 assertions across 5 cases:

| Case | Behaviour verified |
|------|--------------------|
| 1    | Single load-complete fires once after 1500 ms with the initial title |
| 2    | Title update mid-settle resets the timer; final fire carries the newer title |
| 3    | MAX_WAIT_MS = 4000 ceiling fires under repeated title pokes |
| 4    | URL change in the same tab fires the prior URL immediately, starts a fresh settle for the new URL |
| 5    | Tab close fires the pending entry (work never silently vanishes) |

Each harness stubs `chrome.*` + (for defer)
`setTimeout` / `clearTimeout` / `Date.now`, then
node-evals `background.js` against the stubs.
No real browser needed. Both files live in
`apps/extension/` with `_track_a_` prefix so
they're greppable and obviously phase-scoped.

### Sanity

| Check                              | Result |
|------------------------------------|--------|
| `node --check background.js`       | ok     |
| Net LOC                             | 103 / -14 |
| Manifest unchanged                  | yes    |
| API schema unchanged                | yes    |
| Existing event log readable         | yes (no kind/payload change) |
| Backward-compat for old "chat"/"claude"/"chatgpt" tags | yes |

---

## Open issues

### Carried into Track A → not addressed

- **Tab focus / dwell time still not captured.**
  A tab loaded once and viewed for four hours
  still emits one event. The launcher cannot
  distinguish "five-second glance" from "two-hour
  deep work." Out of scope for capture truth;
  it's a different layer (engagement signal).
  Logged as a new open item below.

### Side-effects to watch

- **Settle delay = 1.5 s.** If the daemon is
  *off* during the settle window and comes back
  up at second 1.4, the event fires at second
  1.5 and the daemon receives it normally. No
  behaviour change there.
- **Tab closed during settle.** The
  `chrome.tabs.onRemoved` handler now emits the
  pending entry. Old behaviour: silently lost
  it. This is more truthful but produces
  ≤1 more event per minute under heavy tab
  churn. Daemon ingest rate at the busiest
  measured 5-min window: 8 events/min. New
  ceiling: ~12 events/min. Well within budget.
- **Reload of the same URL.** Old code: dedupe
  by 800 ms window suppresses repeat. New code:
  the second `complete` resets the same tab's
  settle timer to the latest title; if the URL
  is identical it just emits once after the
  next settle. Functionally similar, slightly
  more truthful (latest title wins).

### New open items raised by this track

- **TA-1.** Tab focus / dwell-time capture
  (severity P2). Would require a new event
  kind (`tab_focus` / `tab_blur`) and an
  ingest schema entry. Phase 9 territory.
- **TA-2.** Perplexity is currently mapped as
  a *search engine* (because `?q=` works). It
  is more accurately a chat product. Leaving
  alone for now — flipping it would change
  every historical Perplexity event's kind on
  fresh re-runs, which is a different problem
  than this track.

---

## Next

**Track B — Ingestion reliability** is next per
the directive's track order.

The question for Track B (preview):
*does every event the extension fires actually
land on disk?* The capture pipeline trusts that
`POST /v1/events/*` always succeeds; if the
daemon is briefly down (boot race, port
collision, sleep/wake), events are lost
silently — there is no client-side queue
(comment in background.js line 159: "Silent —
the next visit retries on its own; we never
queue locally.").

Track B's smallest plausible scope: introduce
an in-extension retry buffer with bounded
storage, so a 30-second daemon hiccup doesn't
silently drop the user's recent activity. I
will diagnose the real failure mode before
deciding on the fix, per the same approach
Track A used.

**Pausing here for explicit user approval to
proceed to Track B** — per directive: "one
track at a time."
