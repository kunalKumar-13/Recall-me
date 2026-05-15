# Recall.me — Memory Sync (browser extension)

The smallest possible bridge between Chrome / Edge and the local
Recall daemon. Captures page visits, search-engine queries, and
chat-platform sessions, and POSTs them to `127.0.0.1:4545`.

Nothing leaves the machine. No remote network. No DOM scraping. No
telemetry. The only HTTP destination this extension is permitted to
reach is the loopback Recall daemon.

## Install (developer mode)

1. Make sure the Recall desktop app is running. Confirm in Settings →
   Browser Memory that the listener is "Listening on 127.0.0.1:4545".
2. Open `chrome://extensions` (or `edge://extensions`).
3. Toggle **Developer mode** in the top-right corner.
4. Click **Load unpacked** and pick this `extension/` folder.
5. The extension's puzzle-piece icon appears in the toolbar; click it
   to confirm "Connected · N captured".

That's the whole setup.

## What it captures

| Page                                  | Becomes        |
|---------------------------------------|----------------|
| Any normal page (`https://…`)         | `browser_visit`|
| Google / DuckDuckGo / Bing / Kagi search | `browser_search` |
| chatgpt.com / chat.openai.com / claude.ai | `chat_session` |

Every event carries: `url`, `title`, `domain`, plus the kind-specific
payload. The full schema is documented in `app/core/ingest.py`.

## What it never captures

- `chrome://`, `edge://`, `about:`, `file://`, `view-source:`, and
  similar internal pages — dropped before they leave the worker.
- Incognito / Private windows — Chrome's runtime hides these from
  the extension; we additionally check `tab.incognito` as a belt.
- Page contents — only the URL and the title. The DOM is never read.
- Anything in your domain exclude list (configured in Recall →
  Settings → Browser Memory). The list is matched as a suffix, so
  adding `google.com` silently filters `mail.google.com`,
  `docs.google.com`, etc.

## Privacy contract

- The extension's `host_permissions` is exactly one URL —
  `http://127.0.0.1:4545/*`. Chrome will refuse any other network
  request from the worker.
- The extension does not request `<all_urls>` permissions; it only
  uses the `tabs` API, which exposes URL + title metadata for the
  active tab and never the page contents.
- All captured data lives in the per-day JSONL files under
  `~/.recall/events/`. Plain text. Open them in any editor. Delete
  them whenever.

## Build

There is no build step. The extension is vanilla JavaScript +
HTML + JSON; what you see in this folder is what runs in the
browser.

## Icons

Icons are intentionally not bundled — Chrome falls back to a
default puzzle-piece glyph. Add `icons/icon-{16,48,128}.png` and
the corresponding `"icons"` block in `manifest.json` if you want a
custom toolbar icon.
