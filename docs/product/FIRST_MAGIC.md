# FIRST_MAGIC.md — what a fresh install must feel like

A continuity layer only earns trust if the first thirty seconds tell
the user what it is *without forcing them to wait*. On a fresh
install Recall has no events, no threads, no recovery candidates;
the engine is correctly empty. The question this doc answers:
**how do we let the user *see* what continuity will feel like
without inventing data they didn't produce?**

The answer is the Phase 6D **demo overlay**.

---

## What demo mode is

A one-click first-run surface that overlays canonical fixture data
on top of the empty engine state. Three named stories — the same
three the launcher's `app.core.demo_seed` already scripts:

1. **WebSocket retry debugging** — the hero recovery candidate
   (2 tabs, 2 files, reopened after a 2-day gap, high confidence).
2. **Healthcare pitch — proposal draft** — an active investigation
   spanning notes / browser tabs / chat sessions.
3. **RLHF reward shaping** — an active investigation across
   searches + arxiv / hf blog visits.

Plus a deterministic eight-event *Today* rail with `HH:MM` mono
timestamps. The data is hand-written, fully deterministic, and
identical between the launcher and the extension popup. No AI
generation, no random selection, no engine touch.

## What demo mode is *not*

- **It is not a model.** No text is generated. Every label, URL,
  filename, and timestamp is hand-written in
  [`app/core/demo_mode.py`](../../app/core/demo_mode.py).
- **It is not a fake event.** No event is written to the user's
  event log. The engine layers (`events`, `sessions`,
  `microcontexts`, `resurfacing`, `threads`, `evolution`,
  `recovery`) never see demo content.
- **It is not opt-in capture.** Demo mode adds zero data points
  to disk apart from `~/.recall/demo.json` (the state machine's
  own one-key file).
- **It is not a tutorial.** No coach marks, no walkthrough, no
  "next" buttons. It is one calm screen that shows *what the
  product will look like* when the engine fills up.

## Why demo exists

Empty is honest, but empty is also indistinguishable from broken.
A user opening the popup for the first time and seeing "Recall
notices unfinished work." is hearing a *promise* — and the
promise needs a way to be inspected before they have any work
captured. The demo overlay is the inspection surface. The
user reads three real-looking topics laid out the same way
their own thinking will be laid out, decides whether the
product matches their needs, and either accepts the demo
("oh I get it") or declines it ("start normally") and waits
for their own data to surface.

## How it disappears

Demo mode disappears the moment real data exists. Two paths:

1. **Auto-dismiss on ingest.** Every successful ingest route
   (`POST /v1/events/{browser, search, chat, open}`) calls
   `demo_mode.mark_real_activity()`. If state was `active`, it
   flips to `dismissed`. The next time the popup opens, the
   demo overlay is gone and the user's real engine surface
   takes over. No flash, no flicker — the popup's existing
   `AnimatePresence` over the body component crossfades
   between states.
2. **Manual dismiss.** The trust banner across both surfaces
   carries a *Dismiss* link that POSTs `/v1/demo/dismiss`.
   The user gets to refuse the demo at any point.

The Phase 6D rule: **real events override demo, always.** The
demo never competes with the user's own data; it yields the
moment data exists.

## The state machine

Five states, persisted at `~/.recall/demo.json`:

| State | Meaning | Next |
|---|---|---|
| `disabled` | Demo affordance hidden. Reserved for a future setting; not currently surfaced as a toggle. | terminal |
| `available` | Default on fresh install. Empty surfaces show the *Show example* + *Start normally* buttons. | → `active` (Show example) / `dismissed` (Start normally) |
| `active` | The overlay is visible. Trust banner is up. | → `dismissed` (manual or auto) / `completed` (future) |
| `dismissed` | User declined or real activity arrived. Empty surfaces show without buttons. | terminal until file deleted |
| `completed` | Reserved: future "user clicked Resume on a demo card" state, currently treated like `dismissed`. | terminal |

Deleting `~/.recall/demo.json` returns the state machine to
`available` — useful for QA. The file is human-readable JSON;
inspecting it is the same as inspecting any other file under
`~/.recall/`.

## Trust rules

Demo data is presented inside a calm trust banner that says
exactly two things:

```
Example data — Nothing here came from your device.
```

Plus a Dismiss action.

The banner is:

- **always visible while state === "active"** — on both the
  launcher demo digest and the extension popup demo overlay.
  No surface shows demo data without it.
- **lavender-tinted, not warning-coloured** — demo is a trust
  *statement*, not a warning. Never red.
- **the only on-brand surface that doesn't read from the
  engine** — a user who walks away after seeing it knows
  Recall didn't see anything they did.

## Surfaces

| Surface | Demo signal | Trust banner | Dismiss |
|---|---|---|---|
| Launcher empty card | *Show example* (primary) + *Start normally* (secondary) buttons | yes — first row of the demo digest | banner *Dismiss* link |
| Extension popup empty | same two-button pair | yes — first row of the demo overlay | banner *Dismiss* link |
| Either surface, after demo | falls back to the normal empty card | n/a | n/a |

The launcher and the popup share **one** state file, so the
user's choice on one surface is honoured on the other on the
next open.

## Engine impact

Zero. The demo overlay lives in:

- [`app/core/demo_mode.py`](../../app/core/demo_mode.py) — state
  machine + fixture payload (`demo_payload()`).
- [`api/main.py`](../../api/main.py) — three thin routes
  (`/v1/demo/state`, `/v1/demo/activate`, `/v1/demo/dismiss`)
  plus a one-line `_post_ingest_hook(ok)` call after each
  successful ingest that flips state on real activity.
- [`app/ui/launcher.py`](../../app/ui/launcher.py) — a new
  `demo_panel` widget + the `_on_show_example_clicked` /
  `_on_start_normally_clicked` handlers.
- [`apps/extension/ui/src/components/DemoBanner.tsx`](../../apps/extension/ui/src/components/DemoBanner.tsx)
  + a `"demo"` branch in the popup state machine.

Every existing engine layer is untouched. Deleting
`app/core/demo_mode.py` would remove the demo entirely without
breaking any downstream artifact — the *purely additive* rule
that any new layer must satisfy.

## Captures

| File | What it shows |
|---|---|
| `assets/screenshots/demo/demo-launcher.png` | Launcher demo digest — trust banner + recovery card + three investigation cards. |
| `assets/screenshots/demo/demo-extension.png` | Extension popup demo overlay — trust banner + ContinueCard + investigation pill strip + Today rail. |
| `assets/screenshots/demo/demo-transition.png` | Launcher digest *without* the banner — the post-dismiss / post-real-ingest surface, so the diff with `demo-launcher.png` is exactly the banner. |
| `assets/screenshots/demo/demo-extension-empty.png` | Extension popup right after the user clicked *Start normally* — the empty card with both buttons present. |

## Related

- [`PHASE_6D_STATUS.md`](../engineering/PHASE_6D_STATUS.md) —
  the engineering receipt for this phase.
- [`CLAUDE.md`](../../CLAUDE.md) — the engineering charter, in
  particular the *Things we will not build* section. The demo
  overlay sits inside the charter because it is *additive,
  inspectable, deterministic, and never writes engine state*.
- [`app/core/demo_seed.py`](../../app/core/demo_seed.py) — the
  earlier scripted seeder that writes events to
  `~/.recall/events-demo/`. Same three stories; different
  delivery (the seeder writes JSONL; demo mode hands back a
  fixture payload). The two are complementary — a future phase
  could let the demo overlay's *Resume* button actually point
  the engine at the seeded directory.
