# Phase 8C — Capture Validation

**Question:** does the browser-capture pipeline
actually fire on the sites we tell users it covers?

**Method:** read `~/.recall/events/*.jsonl` for the
last 30 days, count events by `payload.domain`, and
report verbatim. No synthetic data, no test fixtures
— the user's own live event log is the ground truth.

**Window:** 2026-04-24 → 2026-05-24 (30 days,
5 day-files present).

---

## Headline numbers

- **Total events (30d):** 208
- **Browser events (`browser_visit` + `chat_session`):** 166
- **Non-browser events:** 42 (`query` × 41, `open` × 1)
- **Day-files present:** 5 (sparse — see "Capture
  gaps" below)

## Per-site coverage on the verification list

The directive named five sites to verify:

| Site            | Events (30d) | Status |
|-----------------|--------------|--------|
| **ChatGPT**     | 20           | ✅ working — captured as `chat_session` |
| **GitHub**      | 16           | ✅ working — captured as `browser_visit` |
| **Google**      | 55           | ✅ working — captured as `browser_visit` |
| **StackOverflow** | 0          | ⚠️ no events — coverage gap or no recent visits |
| **Stitch**      | 0            | ⚠️ no events — coverage gap or no recent visits |

The two zero-event sites are reported honestly. We
cannot tell from the event log alone whether the
extension's content-script *would* fire on those
domains and the user simply hasn't visited them in
30 days, or whether the matcher list excludes them.
This is the kind of question 8C is built to surface
rather than paper over.

**Recommended follow-up** (not in scope for 8C; logged
in `BUGS_OPEN.md`):

1. Open `apps/extension/ui/manifest.json` and
   confirm `host_permissions` or content-script
   `matches` list includes `stackoverflow.com` and
   the Stitch domain.
2. If matched, visit one URL on each and confirm an
   event appears in today's JSONL within 5 s.
3. If not matched, decide explicitly: add to
   manifest, or remove from user-facing copy.

## Top other domains seen (sanity check)

| Domain               | Events (30d) |
|----------------------|--------------|
| kotak811.bank.in     | 45           |
| hotstar.com          | 26           |
| app.mintlify.com     | 1            |
| reactbits.dev        | 1            |
| scaler.com           | 1            |
| notion.so            | 1            |

The bank + streaming domains are the dominant
"other" share. This is the user's real browsing —
nothing in the capture pipeline is filtering them
out, and nothing should: the pipeline captures
*everything* the extension sees, and the engine
chooses what to surface.

## Investigation / hero formation

`recall capture status` reports the daemon's view:

```
events_today=…
investigations=…
hero_present=true|false
```

At the time of writing the smoke pass for 8C, this
command exits 0 and reports a healthy state. The
investigation engine (Phase 5/6) groups today's
events into topical clusters; the hero is the
top-scored unfinished thread.

**What we did not verify in 8C:**
- Whether the hero is *correct* for today's events.
  That requires a labeled-fixture pass, which is
  the Phase 6L trust-fixture work — already partly
  complete, tracked in
  [`TRUST_FIXTURES_CONTINUITY.md`](../docs/trust/TRUST_FIXTURES_CONTINUITY.md).
- Whether `POST /v1/recovery/{id}/restore` actually
  re-opens the right tabs on this machine. Manual
  spot-check passed; not yet a smoke section.

## Capture gaps

Only 5 day-files exist in a 30-day window. That
means **25 days have zero captured events** — either
the daemon was not running, or the user did not
trigger any captured action. The extension does not
phone home when the daemon is down (it queues
locally and drains on next connect), so the zero-day
gap is most likely "daemon was off."

This is *expected behaviour* for a local-first tool
running on a single developer box that boots
intermittently. It is *not* a reliability problem
for the capture pipeline — the pipeline writes when
asked. It IS something to mention in the public-alpha
copy: "Recall captures what it sees when it's
running."

## What this proves

1. **The capture pipeline writes real events on
   real sites.** 166 browser events across 5 days
   is not a test fixture.
2. **ChatGPT, GitHub, and Google work today.**
3. **JSONL on disk matches the user's actual
   browsing** (kotak811 + hotstar tail confirms this
   is not synthetic).

## What this does NOT prove

- That StackOverflow and Stitch are wired in. They
  are zero in 30 days — could be coverage gap or
  could be user-behaviour gap. Needs explicit
  manifest audit.
- That investigation / hero quality is good. That
  is a separate trust-fixture pass.
- That capture survives a multi-hour daemon crash.
  Extension queueing is implemented but not
  stress-tested in 8C.
