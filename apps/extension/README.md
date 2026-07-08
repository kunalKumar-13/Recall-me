# Recall — Continuity Companion (browser extension)

The browser side of Recall. It does two things, kept deliberately
separate:

1. **Capture** (`background.js` + `capture/`) — quietly records page
   visits, search queries, and chat-platform sessions and delivers
   them to the local Recall daemon at `127.0.0.1:4545` through a
   **durable outbox**: events are queued in `chrome.storage.local`
   and flushed in batches to `/v1/events/batch` with retry, so nothing
   is lost when the daemon is briefly down.
2. **The popup** (`popup/`, built from `ui/`) — a small memory
   *surface*. Open it and it answers one question: *what was I
   doing?* It is not a telemetry dashboard, not browser analytics,
   not an assistant.

Nothing leaves the machine. No remote network. No DOM scraping. No
telemetry. The only HTTP destination this extension can reach is the
loopback Recall daemon.

## Layout

```
apps/extension/
├── manifest.json     MV3 manifest (hand-written)
├── background.js     capture service-worker entry (ES module, hand-written)
├── capture/          capture core (hand-written ES modules)
│   ├── normalize.js     pure URL → event classifier (node-tested)
│   ├── outbox.js        durable, batched, retrying sender
│   ├── sources.js       tab + SPA listeners with title-settle
│   ├── dwell.js         attention tracker → browser_focus dwell events
│   └── *.test.js        node tests (normalize, dwell)
├── popup/            ← BUILT popup — what Chrome loads (generated)
│   ├── index.html
│   └── assets/
└── ui/               ← popup SOURCE (React + Vite + Framer Motion)
    ├── index.html
    ├── src/
    │   ├── App.tsx               two-view shell + connection state machine
    │   ├── components/           SettingsPanel, icons + v2/: Header, Hero,
    │   │                         Investigations, Timeline, Activity,
    │   │                         SearchOverlay, TrustStrip, States
    │   └── lib/                  api, types, motion
    └── package.json
```

Chrome loads `apps/extension/` as the unpacked extension.
`manifest.json`, `background.js`, and the `capture/` modules are
hand-written; `popup/` is a build artifact produced from `ui/`. The
capture core has node tests: `node capture/normalize.test.js` and
`node capture/dwell.test.js`.

Every control in the popup is real: the three capture toggles map to
per-kind gates the worker checks before enqueuing (`KIND_GATE` in
`background.js`), Pause is the shared `pauseUntil` epoch, and the
Private-sites editor writes the `excludedDomains` list the worker
filters on live. The Activity cards and the "N events today" pill
read `/v1/events/today` — engine-side ground truth, never a
client-side guess.

## Build the popup

```bash
cd apps/extension/ui
npm install
npm run build      # type-checks, then writes apps/extension/popup/
```

`npm run dev` serves the popup in a normal browser tab for fast
iteration (the daemon calls fall back gracefully when `chrome.*`
APIs are absent).

## The popup

A 440 px-wide companion. One fresh read of the daemon per open —
never a stale cached dashboard. Sections, top to bottom:

| Section | Answers |
|---|---|
| **Continue** | the single strongest interrupted investigation, with a **Resume** button |
| **Active investigations** | up to four ongoing topics |
| **Browser memory** | recent searches / tabs / chats, grouped |
| **Trust** | local-only, daemon status, events captured today |
| **Settings** | capture toggles + links (reached via the header gear) |

### Popup states

The popup is a small state machine. Every non-normal state is a
calm, full-body screen — no red, no error iconography. For
storybook-style isolated preview, append a `state` query param when
running `npm run dev`:

| `?state=` | Screen |
|---|---|
| `loading` | first daemon read in flight |
| `connected` | the normal surface |
| `disconnected` | daemon not running — capture continues, Resume offline |
| `reconnecting` | a retry in flight |
| `offline` | the browser itself has no network (Recall never needed it) |

The empty state (connected, but nothing captured yet) appears on
its own when there is genuinely nothing to show.

### Design language

Calm, quiet, spatial, trustworthy, minimal — Raycast × Arc ×
Granola. Light surfaces over warm off-white, soft hairline borders,
14 px radius, a 24 px section rhythm. One accent (lavender), used
once per zone. No glass, no neon, no charts, no gradient "AI"
energy. Motion is continuity motion only — fade, expand, slide —
on a single calm easing curve, never a bounce or a float.

See [`architecture.md`](architecture.md) for the component model
and data flow.

## What the popup can do

- **Resume** runs the engine's real restoration plan — tabs, chats and
  searches reopen in the choreographed order (files are counted and
  left to the desktop app).
- **Search (Cmd/Ctrl+K)** blends instant in-memory matches with the
  daemon's episodic search.
- **Pause** (header) stops capture for one hour — the worker honours
  `pauseUntil` from storage; click again to resume early.
- **Options page** — chrome://extensions → Details → Extension
  options opens the same Settings surface in a full tab.

## What it captures

| Page | Becomes |
|---|---|
| Any normal page (`https://…`) | `browser_visit` |
| Google / DuckDuckGo / Bing / Kagi search | `browser_search` |
| chatgpt.com / claude.ai / gemini / copilot / deepseek / grok / poe / … | `chat_session` |
| SPA route changes (pushState) on the above | captured via `webNavigation` |

## What it never captures

- `chrome://`, `edge://`, `about:`, `file://`, `view-source:` — dropped
  before they leave the worker.
- Incognito / Private windows.
- Page contents — only the URL and title. The DOM is never read.
- Anything in your domain exclude list (Recall → Settings → Browser
  Memory).

## Privacy contract

- `host_permissions` is exactly one URL — `http://127.0.0.1:4545/*`.
  Chrome refuses any other network request from this extension.
- No `<all_urls>` permission; only the `tabs` API (URL + title
  metadata, never page contents).
- All captured data lives in plain JSONL under `~/.recall/events/`.

## Install (developer mode)

1. Build the popup (above).
2. Make sure the Recall desktop app is running.
3. Open `chrome://extensions` (or `edge://extensions`).
4. Toggle **Developer mode**.
5. **Load unpacked** → pick this `apps/extension/` folder.

## Icons

`icons/{16,32,48,128}.png` — the thread-and-node mark (ink square,
white thread, red node) wired into both `icons` and
`action.default_icon` in the manifest.
