# CONTROL_ROOM.md — what the operator UI is, and isn't

Phase 5E.2 built the actual founder dashboard at
[`apps/admin/web/`](../../apps/admin/web/). This file is the
explainer: what exists, what data is allowed in, what is *never*
allowed in.

Pairs with [`FOUNDER_DASHBOARD.md`](FOUNDER_DASHBOARD.md) (the
philosophy: the five founder questions and which have automatic
answers) and [`../engineering/TRUST_LEDGER.md`](../engineering/TRUST_LEDGER.md)
(the boundary contract).

---

## What exists

A **local-first Next.js page** at [`apps/admin/web/`](../../apps/admin/web/).
Run `npm install && npm run dev` and the founder gets one page,
seven sections, calm visual:

| § | Section | What it shows | Source |
|---|---|---|---|
| 1 | **Health Overview** | 6 cards: active installs, returning installs, continuity restored, resume sessions, investigations, extension connected | `data/health.json` |
| 2 | **Traction Room** | 6 sparklines: install growth, return rate, continuity restored, recoveries accepted, daily reopen, alpha growth | `data/traction.json` |
| 3 | **Alpha Cohorts** | per-cohort cards with device count, returning, feedback volume | `data/cohorts.json` |
| 4 | **Release Room** | version + next milestone + GO/NO-GO + installer/mac/signing/screenshots + blocked list | `data/release.json` |
| 5 | **Trust Room** | 6 cards: shown / accepted / correct silence / bad recoveries / extension offline / doctor reds | `data/trust.json` |
| 6 | **Feedback Room** | tagged inbox (pain / confusion / trust / bug / feature), newest first | `data/feedback.json` |
| 7 | **Founder Timeline** | phase track with done % across all phases | `data/timeline.json` |

### What it isn't

- **Not a server.** No API, no auth, no users database. The page
  is a Next.js Server Component reading filesystem JSON at render
  time. Static export works the same way.
- **Not a public site.** `robots: noindex, nofollow`; intended for
  `localhost:3000` on the founder's machine.
- **Not a chart library.** Sparklines are hand-rolled SVG. The
  visual rule the directive set — *Linear × Stripe internal × calm,
  no startup charts explosion* — is enforced by *not having* a
  chart dependency.
- **Not a telemetry endpoint.** The page *reads* JSON; it never
  receives a POST, never opens a WebSocket, never holds an HTTP
  listener of its own.

## What data is allowed in

The control room reads exactly **eight files** from
[`apps/admin/data/`](../../apps/admin/data/):

```
health.json     traction.json   cohorts.json    release.json
trust.json      feedback.json   timeline.json   meta.json
```

Each file is **placed there by hand or by an existing script**:

- `health.json`, `traction.json`, `trust.json` — derived from
  voluntary `recall stats --export` files that cohort members
  *chose* to share, aggregated by `apps/admin/merge_stats.py`.
- `cohorts.json` — the manual cohort roster (Phase 5E).
- `release.json` — the founder's read of `GO_NO_GO.md` /
  `INSTALL_VALIDATION_WINDOWS.md` / `MAC_BUILD_STATUS.md`.
- `feedback.json` — the founder's hand-logged
  [`FEEDBACK.md`](../../apps/admin/FEEDBACK.md) inbox, exported.
- `timeline.json` — derived from
  [`PHASE_TRACKER.md`](PHASE_TRACKER.md).
- `meta.json` — generation timestamp + a freeform note.

A new section needs a new data file; a new field needs a new key.
There is no schema discovery, no auto-fetch, no implicit data path.

Phase 5G captured a real rendering of the page in
[`assets/screenshots/control-room.png`](../../assets/screenshots/control-room.png)
(Edge `--headless=new` against `next dev`). That image is the
visual contract; if a future change to the page makes it
inconsistent with the screenshot, either the screenshot is
re-captured (the page evolved) or the change is rolled back
(the page drifted from its job).

## What never enters

- **Per-user identifiers.** No emails, no device ids, no hashes,
  no usernames. Cohort entries use founder-assigned handles.
- **Content.** No filenames, URLs, page titles, search queries,
  chat titles. The export contract in
  [`../engineering/TRUST_LEDGER.md`](../engineering/TRUST_LEDGER.md)
  is the boundary: counts and rates only.
- **Sub-day timestamps.** The traction series carry only the date,
  per the same contract.
- **A second data source.** If a number is not in one of the eight
  JSON files above, it is not in the dashboard. Period.

## Visual language

- **White page, lavender accents** — exactly one accent moment per
  card.
- **Soft hairlines** for structure; one card shadow.
- **Plain SVG sparklines** — no bars, no axes, no gradient fills
  beyond a single soft underlay.
- **Calm pills** for status (green / yellow / red / mute) — never
  more than one per card.
- **System fonts** end-to-end.

The look is Linear × Stripe internal × calm. There is no toggle
animation, no entry stagger, no loading spinner — the data is
local and arrives in one frame.

## How to use it

```bash
# refresh the auto-able source (GitHub downloads)
python apps/admin/pull_release_stats.py

# fold in voluntary cohort exports
python apps/admin/import_stats.py <stats.json> <cohort> <user>
python apps/admin/merge_stats.py

# regenerate the eight JSON files the control room reads
recall founder bake

# read the 5-second status from the terminal
recall founder status

# run the page
cd apps/admin/web && npm install && npm run dev
# → open http://localhost:3000
```

Phase 5E.3 closed the assembly gap: `apps/admin/scripts/bake_data.py`
produces all eight `data/*.json` files from `aggregate.json` (the
merged cohort exports), `traction_history.json` (manual roster), the
`alpha/*.json` manual files, `release_state.json` (the founder's
hand-edited release facts), and `timeline_input.json` (the phase
roster). The `recall founder` CLI wraps the bake plus six read-only
inspectors (`status` / `release` / `trust` / `health` / `alpha` /
`timeline`). The bake is fast (~11 ms) and pure-stdlib — see
[`FOUNDER_OPERATIONS.md`](FOUNDER_OPERATIONS.md) for the daily loop
and [`READINESS_SCORE.md`](READINESS_SCORE.md) for the 0-100 verdict
the CLI surfaces.

## The contract this file is

If a future version of the control room ever:

- opens an outbound network connection,
- accepts an HTTP POST,
- reads any file outside `apps/admin/data/`,
- displays content (a filename, a URL, a query),

…then that change has violated this file, and the change should be
reverted unless and until this file is also rewritten. The visible
calm is downstream of an invisible boundary; both have to hold.
