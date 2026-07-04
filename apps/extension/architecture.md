# Extension architecture

The extension is two independent halves that share a manifest and
never call each other directly.

```
        ┌──────────────────────────────────────────┐
        │  background.js + capture/ (service worker)│
        │   sources → normalize → durable outbox    │
        │   → POST /v1/events/batch  (retry on fail) │
        └───────────────────┬──────────────────────┘
                            │ 127.0.0.1:4545
        ┌───────────────────┴──────────────────────┐
        │  Recall daemon (desktop app)              │
        │   events → sessions → … → recovery        │
        └───────────────────┬──────────────────────┘
                            │ 127.0.0.1:4545  (GET only)
        ┌───────────────────┴──────────────────────┐
        │  popup/  (React surface, built from ui/)  │
        │   reads recovery / threads / activity     │
        └───────────────────────────────────────────┘
```

Capture *writes*; the popup *reads*. They are decoupled on purpose:
capture must keep working even when the popup has never been opened,
and the popup must render even when capture is paused.

## Capture module model

```
background.js          thin entry: load config, register sources + retry alarm
└── capture/
    ├── sources.js      tab.onUpdated + webNavigation (SPA) + onRemoved,
    │                   with the title-settle timer
    ├── normalize.js    pure (url, title) → {kind, payload} | null  (node-tested)
    └── outbox.js       durable queue in chrome.storage.local →
                        batched POST /v1/events/batch → retry via chrome.alarms
```

The split is deliberate: `normalize.js` is pure and unit-tested
without a browser; `sources.js` owns the stateful listeners; and
`outbox.js` owns delivery. Coalescing (title-settle) is best-effort,
but *delivery* is durable — an event captured while the daemon is down
is queued and flushed when it returns, surviving service-worker
eviction because the queue lives in `chrome.storage.local`, not memory.

## Popup component model

```
App                       two views + the connection state machine
├── Header                brand · connection dot · gear
├── Body (view: main)
│   ├── ContinueCard       the one strongest interrupted investigation
│   ├── InvestigationCard  ×≤4   ongoing topics
│   ├── MemoryList         recent searches / tabs / chats, grouped
│   └── TrustSurface       local-only · daemon status · events today
├── SettingsPanel (view: settings)   capture toggles + links
├── Section                titled zone wrapper, staggered entrance
└── states                 Loading / Reconnecting / Disconnected /
                            Offline / Empty
```

Each component is presentational — it takes typed props and renders.
All daemon I/O and all `chrome.*` access lives in `lib/api.ts`, so
the components are pure and previewable outside an extension host.

## Data flow

One mount = one read. `App` runs `load()` on mount:

1. `isOnline()` false → `offline`.
2. `fetchHealth()` null → `disconnected` (the daemon is not up).
3. otherwise → fetch recovery + threads + recent activity in
   parallel, then `connected`.

There is no polling and no cache. When the popup closes, the tree is
gone; the next open is a fresh, honest read. A memory surface should
never show yesterday's state as if it were now.

## Connection state machine

```
          load()
 loading ───────────────► connected ──► (main surface)
    │                          │
    │ health fails             │ retry
    ▼                          ▼
 disconnected ◄────────────► reconnecting
    │
    │ navigator.offline
    ▼
 offline
```

Every state below the header is exactly one of these. The body is a
pure function of the state — there is never a half-rendered surface.

## Build pipeline

`ui/` is a Vite + React + TypeScript project. `npm run build`
type-checks (`tsc --noEmit`) then emits to `apps/extension/popup/`
with `base: "./"` so asset URLs resolve from the
`chrome-extension://` origin. `manifest.json`'s `default_popup`
points at `popup/index.html`. The manifest, `background.js`, and the
`capture/` modules are never built — they are hand-written ES modules
at the extension root (`background.service_worker` is loaded with
`"type": "module"`).

## Design constraints (enforced by review)

- **No glass, no neon, no charts, no gradient "AI" energy.** Light
  surfaces, soft hairlines, one lavender accent per zone.
- **Continuity motion only** — fade, expand, slide, one easing
  curve. No bounce, no float, no looping animation.
- **24 px section rhythm, 14 px radius.**
- **The popup never throws.** Every daemon call is wrapped; a dead
  daemon is a calm state, not an error.
- **One network origin** — `127.0.0.1:4545`. The manifest's
  `host_permissions` is the hard boundary.
