# EXTENSION_VALIDATION.md — extension pairing states

The extension popup is a small state machine (Phase 5A added
pairing detection). This file is the proof that each state renders
the right surface — the right copy, the right call to action.

Each state is reachable for review via the popup's storybook param:
`popup/index.html?state=<name>`. Screenshots live in
`assets/screenshots/`.

---

## State matrix

| State | Trigger | Title | Primary CTA | Screenshot |
|---|---|---|---|---|
| **never installed** | daemon never answered on this profile | "Recall isn't installed yet" | **Install Recall** → releases page | `extension-missing.png` |
| **installed, not running** | daemon answered before, now unreachable | "Recall isn't running" | **Open Recall** + Repair connection | `extension-disconnected.png` |
| **running** | daemon healthy | the memory surface (Continue / Investigations / …) | — | `extension-connected.png` |
| **offline** | the browser itself reports no network | "You're offline" | Try again | `extension-offline.png` |
| **loading** | first health probe in flight | "Picking up where you were" | — | `extension-loading.png` |

The **never-installed vs not-running** distinction is the pairing
logic's whole job: the popup remembers (via `chrome.storage`)
whether the daemon has *ever* answered, so a first-time user is
guided to *install* and a returning user is guided to *open* — never
a dead-end "try again".

## How to verify

1. Build the popup: `cd apps/extension/ui && npm run build`.
2. Open `apps/extension/popup/index.html?state=<name>` in a browser
   (the `chrome.*` APIs are absent, so the `?state=` override drives
   the screen).
3. Confirm each row of the matrix: copy, CTA, calm tone (no red, no
   error iconography).

## Validation run

| Check | Result |
|---|---|
| `npm run build` — type-check + bundle | ✅ pass (`tsc` clean, vite OK) |
| Each `?state=` renders its screen | ✅ captured + visually verified (5 PNGs) |
| `connected` populated surface renders | ✅ verified — Continue card + investigations + memory |
| Pairing: missing ≠ disconnected copy | ✅ verified — *"Recall isn't installed yet"* + Install CTA vs *"Recall isn't running"* + Open/Repair |
| CTAs point at the right destinations | ✅ Install → releases; Open → `recall://`; Repair → retry |

Screenshots are captured by `apps/extension/ui/capture_extension.mjs`
(Phase 5A.1) — Playwright serves the built popup over HTTP and
screenshots each `?state=`; the populated `connected` surface uses
mocked loopback responses, no daemon required. Output:
`assets/screenshots/extension-*.png`.

## Real-extension caveat

The above verifies the popup *renders* each state. Verifying the
*transitions* (daemon actually goes down → popup actually flips to
disconnected) requires loading the unpacked extension in Chrome with
the real daemon — a clean-machine step, tracked in
[`GO_NO_GO.md`](../release/GO_NO_GO.md).
