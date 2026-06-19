# PHASE_6D_STATUS.md — Demo Mode

The receipt for Phase 6D. The directive's *Goal*: a fresh install
must feel alive. A user opens Recall, sees no history (correctly,
because they have not produced any), but can still inspect three
named investigations — *WebSocket debugging*, *Proposal draft*,
*Research investigation* — laid out the same way their own
thinking will be laid out. The success line: a new user says
*"ohhh I get it."*

The 6C→6D handoff: 6C made the extension popup feel like product;
6D answers the *but I just installed it* problem by adding a calm
first-run overlay that *demonstrates continuity without inventing
any data the user produced*.

Anti-rules respected: **no engine rewrite**. The demo overlay is
purely additive — a state file, three thin API routes, two UI
panels (one Qt, one React), and zero touches to the engine layers
(events / sessions / contexts / resurfacing / threads / evolution
/ recovery). Deleting `app/core/demo_mode.py` would remove the
demo entirely without breaking any downstream artifact.

Cross-references:
[`FIRST_MAGIC.md`](../../docs/product/FIRST_MAGIC.md) (the product-side
story — what demo is, what it isn't, how it disappears),
[`PHASE_6C_STATUS.md`](PHASE_6C_STATUS.md) (the predecessor —
this phase builds on the popup's existing rendering of recovery
+ investigations + today rail).

---

## What shipped

### 1. `app/core/demo_mode.py` — state machine + fixture payload

A new module that owns the user's *choice* about whether the demo
overlay should currently be visible. Five-state machine —
`disabled` / `available` / `active` / `dismissed` / `completed` —
persisted at `~/.recall/demo.json`. The state file is plain JSON,
human-readable, deletable for QA. The default `available` is what
a fresh install reads when no file exists.

Public surface:

- `state() -> str` — current state, defaults to `available`.
- `is_active() -> bool` — convenience for the launcher.
- `activate() / dismiss() / complete() / disable()` — explicit
  state transitions, each writing a `{state}_at` timestamp.
- `mark_real_activity()` — called by the ingest path after every
  successful event. If state was `active`, flips to `dismissed`.
  This is the *real events override demo* rule, enforced in
  one tiny function.
- `demo_payload(now=None) -> Dict` — the canonical fixture data.
  One recovery candidate (WebSocket retry debugging, 2 tabs / 2
  files / 2-day gap, confidence=high), three investigations
  (WebSocket / Healthcare pitch — proposal draft / RLHF reward
  shaping), an eight-event timeline with `HH:MM`-rendered
  timestamps anchored to `now`, and the trust banner copy.
  Hand-written, fully deterministic, no AI, no engine read.

No engine dependency: the module imports `config.CONFIG_DIR` for
the file path and nothing else. The events / sessions / threads
/ recovery engines are not consulted, even indirectly.

### 2. `/v1/demo/state | activate | dismiss` + auto-dismiss hook

Three thin routes added to [`api/main.py`](../../api/main.py):

- `GET /v1/demo/state` — returns `{state, payload}`. The
  `payload` field is `null` unless `state === "active"`, so a
  consumer that naively renders the payload doesn't show demo
  content by accident.
- `POST /v1/demo/activate` — flips state to `active` and
  returns the same shape. Lets the popup paint the overlay
  immediately without a follow-up GET.
- `POST /v1/demo/dismiss` — flips state to `dismissed`.

Plus a single internal helper `_post_ingest_hook(ok)` that every
ingest route (`/v1/events/browser`, `/v1/events/search`,
`/v1/events/chat`, `/v1/events/open`, and the legacy `/events`
shim) calls after a successful write. The hook is one line:
`if ok: demo_mode.mark_real_activity()`. This is what
auto-transitions the overlay off the moment a real event lands.

Schema additions in [`api/schemas.py`](../../api/schemas.py):
`DemoStateResponse`, `DemoPayloadOut`, `DemoRecoveryOut`,
`DemoInvestigationOut`, `DemoTimelineEventOut`, `DemoTrustOut`.

### 3. Launcher — `EmptyCard` 2 buttons + demo digest

`EmptyCard.empty()` already had a *Show example* button from
Phase 6B; Phase 6D pairs it with a quieter *Start normally*
secondary action. Both buttons emit dedicated Qt signals
(`show_example` / `start_normally`); the widget itself remains
engine-free.

A new launcher panel —
[`Launcher._build_demo_panel()`](../../app/ui/launcher.py) —
renders the demo overlay:

1. **Trust banner** — lavender-tinted, with a small accent dot,
   the *Example data* + *Nothing here came from your device.*
   copy, and a clickable *Dismiss* label that calls
   `demo_mode.dismiss()` + refreshes.
2. **Continue where you left off** — section header.
3. **Demo `RecoveryCard`** — built from `demo_payload()`,
   confidence pinned to *high*, with the same chip-row +
   Resume pill the live recovery card uses.
4. **Active investigations** — section header.
5. **Three `InvestigationCard` rows** — WebSocket / Proposal /
   RLHF, exactly the directive's named threads.

The empty surface was also wired to use `EmptyCard.empty()`
directly (closing the Phase 6B *Live launcher's empty surface
wired to use EmptyCard.empty()* deferral). The pre-6B
`empty_title` / `empty_body` QLabels stay in the QSS as unused
selectors; cleanup deferred to keep the diff focused.

`Launcher._refresh_idle_state` now dispatches on three branches:
demo-active overlay, normal empty card, or the live digest. A
belt-and-braces check flips state from `active` to `dismissed`
if it's reached the idle-state code path with a non-empty store
— covers any path that bypasses the ingest hook.

QSS addition in [`app/ui/styles.py`](../../app/ui/styles.py): a
new `QPushButton#secondary_button` rule for the *Start normally*
action. Transparent fill, warm hairline border, dim text — the
button reads as a quiet refusal, never a peer CTA.

### 4. Extension — EmptyState 2 buttons + demo body + banner

`EmptyState` in
[`apps/extension/ui/src/components/states.tsx`](../../apps/extension/ui/src/components/states.tsx)
gained a *Start normally* secondary button next to the existing
*Show example*. Click handlers call `activateDemo()` /
`dismissDemo()` (new helpers in
[`apps/extension/ui/src/lib/api.ts`](../../apps/extension/ui/src/lib/api.ts))
and invoke an optional parent callback so `App.tsx` can
refresh the demo slice.

`App.tsx` now:

- fetches `/v1/demo/state` in parallel with health / recovery /
  threads / events on every `load()`;
- adds a `"demo"` branch to the `PopupState` type;
- in `derivePopupState`, when the engine is otherwise empty and
  `demo?.state === "active"`, returns `"demo"`;
- in `Body`, the `"demo"` case renders the existing
  `ConnectedBody` with the demo payload's recovery /
  investigations / timeline AND a new optional `banner` slot
  filled with a `DemoBanner` component.

`DemoBanner` is a new component
([`apps/extension/ui/src/components/DemoBanner.tsx`](../../apps/extension/ui/src/components/DemoBanner.tsx))
— lavender-tinted strip, accent dot, two-line *Example data —
Nothing here came from your device.* copy, right-aligned
*Dismiss* link. Slide-fade entry via `framer-motion`'s `calmFast`
transition; no bounce.

The popup never invents demo timestamps client-side — every `ts`
on the demo timeline comes from the daemon's `demo_payload()`
output. The HH:MM labels read in the user's local hour.

### 5. Capture pipeline + screens

Two capture additions:

- [`infra/scripts/capture/capture_demo.py`](../../infra/scripts/capture/capture_demo.py)
  — new Python capture that builds the launcher demo digest
  (with banner) and the post-transition digest (without
  banner). Pure offscreen-Qt, deterministic.
- [`apps/extension/ui/capture_extension.mjs`](../../apps/extension/ui/capture_extension.mjs)
  — extended to write to a new `assets/screenshots/demo/`
  output (`mkdirSync(..., {recursive:true})`) and emit
  `demo-extension.png` (overlay live) + `demo-extension-empty.png`
  (post-dismiss empty card with both buttons). A new
  `MOCK_DEMO_ACTIVE` fixture mirrors the daemon's
  `/v1/demo/state` payload, so the Playwright shot is
  deterministic across machines.

Four PNGs land in
[`assets/screenshots/demo/`](../../assets/screenshots/demo):

```
demo-launcher.png            (launcher demo digest)
demo-extension.png           (popup demo overlay)
demo-transition.png          (launcher digest, post-banner)
demo-extension-empty.png     (popup empty card + 2 buttons)
```

---

## What did **not** ship

| Directive item | Status | Why |
|---|---|---|
| Animated demo→real transition (fade demo out, fade real in) | partial | The popup's existing `AnimatePresence` over the body crossfades between `PopupState` values on every state change, which includes the `demo → empty/capturing/recovery` transition naturally. A bespoke synchronised fade between the demo banner and the real surface would require a shared layout animation; deferred to keep the diff focused. The launcher demo→digest transition is currently a hide/show swap; a `QPropertyAnimation` cascade on the demo panel is a follow-up. |
| `recall://demo/start` deep link from the extension popup | not in scope | The popup activates the demo via `POST /v1/demo/activate` directly to the daemon, no protocol handler required. A future surface (e.g., a marketing-page link) might benefit from the protocol form. |
| `completed` state distinguished from `dismissed` (user clicked a demo card's Resume) | reserved | The state value is in the enum + persisted; no consumer differentiates yet. Will matter when the demo's Resume button is wired to actually open the seed events. |
| Smoke-test coverage for `/v1/demo/*` in `_smoke_api.py` | not in scope this phase | Tested via TestClient one-offs during this phase. A dedicated smoke section is a 5-line follow-up; this phase prioritised the user-visible surface. |

---

## Verification

| Surface | Command | Result |
|---|---|---|
| demo_mode module | `python -c "from app.core import demo_mode; demo_mode.activate(); print(demo_mode.state())"` | `active`; payload keys = `['recovery', 'investigations', 'timeline', 'trust', 'generated_at']` |
| demo API + auto-dismiss | TestClient: `POST /v1/demo/activate` → state `active`; `POST /v1/events/browser` (success) → state `dismissed` | verified, transition lands in one call |
| pyflakes | `python -m pyflakes app/ui app/core api` | zero findings |
| launcher import (offscreen) | construct `Launcher`, call `_refresh_idle_state` with demo active / dismissed | `_state` transitions `demo → empty` cleanly |
| TypeScript | `cd apps/extension/ui && npx tsc --noEmit` | zero findings |
| extension build | `cd apps/extension/ui && npm run build` | 400 modules / 293.07 kB JS / 93.19 kB gzipped (+3.8 kB vs 6C for the demo wiring + banner component) |
| launcher captures | `python infra/scripts/capture/capture_demo.py` | 2 PNGs into `assets/screenshots/demo/` |
| extension captures | `cd apps/extension/ui && node capture_extension.mjs` | 14 PNGs total; 2 in `assets/screenshots/demo/` |
| doctor (regression) | `python recall.py doctor` | unchanged from 6C |

---

## Touched files

```
new code:
  app/core/demo_mode.py
  apps/extension/ui/src/components/DemoBanner.tsx
  infra/scripts/capture/capture_demo.py

modified code:
  api/main.py                       (imports, helpers, 4 routes, ingest hook)
  api/schemas.py                    (6 demo DTOs)
  app/ui/cards.py                   (EmptyCard 2-button layout)
  app/ui/launcher.py                (empty wired to EmptyCard; demo_panel)
  app/ui/styles.py                  (secondary_button QSS rule)
  apps/extension/ui/src/App.tsx     (demo state + body branch + plumbing)
  apps/extension/ui/src/lib/api.ts  (fetchDemoState / activate / dismiss)
  apps/extension/ui/src/lib/types.ts (DemoState, DemoPayload, "demo" state)
  apps/extension/ui/src/components/states.tsx (EmptyState 2 buttons)
  apps/extension/ui/capture_extension.mjs (OUT_DEMO + MOCK_DEMO_ACTIVE)
  apps/extension/popup/...          (vite build output)

new docs:
  docs/product/FIRST_MAGIC.md
  docs/engineering/PHASE_6D_STATUS.md

new captures:
  assets/screenshots/demo/demo-launcher.png
  assets/screenshots/demo/demo-extension.png
  assets/screenshots/demo/demo-transition.png
  assets/screenshots/demo/demo-extension-empty.png
```

No engine layer (`events.py`, `sessions.py`, `microcontexts.py`,
`resurfacing.py`, `threads.py`, `evolution.py`, `recovery.py`)
was touched. No `~/.recall/events/` file was written by the demo
path; the only file the demo path can produce is
`~/.recall/demo.json` (state machine), and only when the user
explicitly activates or dismisses.

---

## Read-back of the success criterion

The directive's success line: *a new user says "ohhh I get it."*
Open `assets/screenshots/demo/demo-launcher.png` and
`assets/screenshots/demo/demo-extension.png` side-by-side: both
surfaces show the same three named threads (WebSocket /
Proposal / Research) atop the same trust banner, in the same
visual vocabulary as a real populated surface. A user who
clicks *Show example* sees exactly what their own popup will
look like once they've worked a little, and the moment they
do, the demo yields silently to real data via the ingest
auto-dismiss hook. That is the *first magic* the phase set
out to deliver.
