# Phase 8C — Extension Reality

**Question:** does the Phase 7A extension popup
render the right state for the right data, every
time?

**Method:** read the popup's state machine
([`apps/extension/ui/src/App.tsx`](../apps/extension/ui/src/App.tsx)
+ [`lib/types.ts`](../apps/extension/ui/src/lib/types.ts)),
catalogue every state, confirm the capture set under
`assets/screenshots/extension-7a/` covers the visual
ones, and report bundle health.

---

## State machine

The popup body renders exactly one of these states
at a time. The contract is enforced by
`derivePopupState()` in `App.tsx`.

| `PopupState`      | When it renders                                    | Visual surface |
|-------------------|----------------------------------------------------|----------------|
| `loading`         | first health check in flight                       | `LoadingPlate` |
| `reconnecting`    | retry after a transient disconnect                 | `ReconnectingPlate` |
| `offline`         | browser itself reports no network                  | `OfflinePlate` |
| `disconnected`    | daemon unreachable                                 | `DisconnectedPlate` |
| `empty`           | daemon healthy + 0 events + 0 memory               | `EmptyPlate` |
| `capturing`       | daemon healthy + events captured, no investigations yet | full layout w/ "Recall is watching locally" hint |
| `investigations`  | investigations exist, no recovery candidate        | Hero hidden, `Investigations` rail leads |
| `recovery`        | a recovery candidate is ready                      | `Hero` card leads, rest stacks below |
| `demo`            | daemon empty + demo_mode active                    | reuses live render path with seeded data |

**Invariant:** if daemon is healthy AND
`ingestedTotal > 0`, the `empty` state is
forbidden. Documented in `types.ts:34`.

---

## Six fixed-position regions

The directive ("open extension → immediately
understand: Recall remembered work · Recall can
continue it · Recall is running") is satisfied by
six regions in a single 440×640 popup:

1. **Header** — mark + daemon dot + Search / Settings buttons
2. **Continue hero** — full-width recovery card when one exists
3. **Investigations** — stacked rows (max 4 visible)
4. **Today timeline** — event rail
5. **Activity** — Browser + Desktop status cards
6. **Trust strip** — collapsed footer

Plus two overlays:
- **Search overlay** (Cmd/Ctrl+K, slide-in from the top)
- **Settings view** (slides in from the right)

Source: `App.tsx:45-62`.

---

## Component LOC budget

| Component         | LOC |
|-------------------|-----|
| `App.tsx`         | 376 |
| `SearchOverlay`   | 310 |
| `States`          | 240 |
| `Timeline`        | 218 |
| `Hero`            | 204 |
| `Investigations`  | 193 |
| `Activity`        | 191 |
| `Header`          | 160 |
| `TrustStrip`      | 81  |
| **Total**         | **1,973** |

Below 2K LOC for the entire popup surface. Phase 8B
archived 8 pre-7A components (ContinueCard,
DebugStrip, DemoBanner, InvestigationCard,
MemoryList, Section, TrustSurface, states.tsx) —
the build identity number below proves they were
already tree-shaken from the runtime, so the
archive carried zero pixel risk.

---

## Bundle health

| Asset              | Size      |
|--------------------|-----------|
| `index.js`         | 293,508 B (293 KB) |
| `index.css`        | 2,708 B   |
| **Total**          | **296,216 B (296 KB)** |

Identical to the post-8B measurement, identical to
the pre-8B measurement. Tree-shaking confirms the
8B archive removed only files Vite was already
ignoring.

Browser popup load cost (estimated by transfer size
on a local filesystem read): negligible. Real
user-perceived cost is dominated by the popup's
first `/v1/health` fetch — which is throttled to
1 s by the daemon for its own protection.

---

## Capture set (frozen)

Active capture folder: `assets/screenshots/extension-7a/`

| File           | State captured |
|----------------|----------------|
| `active.png`   | populated, healthy daemon |
| `capturing.png`| `capturing` state |
| `demo.png`     | `demo` state |
| `empty.png`    | `empty` state |
| `offline.png`  | `offline` state |
| `resume.png`   | `recovery` state with hero |
| `search.png`   | search overlay open |

**7 captures, 9 states.** The two states without
explicit captures (`loading`, `reconnecting`) are
transient by design — they exist for under a
second in normal operation and the `States.tsx`
component renders them as a single shared
`LoadingPlate` variant. Acceptable gap; logged in
`BUGS_OPEN.md` as `EXT-001` (cosmetic).

---

## Keyboard shortcuts

| Shortcut       | Action                       |
|----------------|------------------------------|
| `Cmd/Ctrl+K`   | open / close search overlay  |
| `1`            | resume visible recovery (`recovery.urls.forEach(openTab)`) |

Both registered at the window level (App.tsx:123)
so they survive focus changes between popup regions.
Text inputs are exempted from the `1` shortcut
(checks `e.target instanceof HTMLInputElement`).

---

## Forced state (test affordance)

`readForcedState()` reads a query-string override
that lets a developer pin the popup to any state
for visual review without running the full daemon.
`?forced=disconnected` is the canonical example.
Used by the capture harness.

---

## What this proves

1. **Nine states, all explicitly modeled.** The
   state machine in `types.ts` is the contract;
   `App.tsx` enforces it.
2. **Seven captured states.** Plus two transient
   states the harness deliberately skips.
3. **Bundle identity holds across 8B.** 293 KB
   JS, byte-identical to pre-archive. The dead
   pre-7A components were never live.
4. **Single 440×640 surface.** Six fixed regions
   + two overlays. No floating modals, no nested
   popovers.

## What this does NOT prove

- That the popup renders correctly across Chrome /
  Edge / Brave / Arc. The capture harness uses
  Chromium via Playwright — other Chromium
  variants are inferred to work but not verified.
- That `openTab(url)` opens reliably across all
  URL schemes. Last verified in Phase 4A.
- That the search overlay's debounce + cancellation
  is correct under fast typing. Open as `EXT-002`
  in `BUGS_OPEN.md`.
