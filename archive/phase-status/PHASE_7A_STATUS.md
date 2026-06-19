# Phase 7A — Extension Product Surface

**Status:** complete
**Directive:** stop launcher · control-room · founder tooling ·
docs · alpha dashboards. **Only extension.** Make Recall's
extension feel premium.
**References:** Arc · Raycast · Linear · Readwise Reader ·
Perplexity sidebar.

> open extension → immediately understand: Recall remembered
> work · Recall can continue it · Recall is running.

---

## What shipped

### Global layout

- **Popup frozen at 440 × 640.** `body` sized + `overflow:
  hidden`; `#root` matches.
- Six fixed-position regions in a single column: Header →
  Continue hero → Active investigations → Today timeline →
  Activity → Trust strip. Header + Trust strip pinned; main
  column scrolls.

### Design tokens

- **Warm paper page** `#F5F2ED`, pure-white cards, lavender
  accent, warm-grey hairline `#E6DED4`, single soft shadow
  `0 12 32 rgba(0,0,0,.06)`.
- **No glass, no neon, no blur.** All surfaces paint opaque.
- **Motion 120 / 180 / 240** via new `--motion-fast` /
  `--motion-normal` / `--motion-slow` tokens. One easing
  curve everywhere.

### New components (`apps/extension/ui/src/components/v2/`)

| File                  | Role                                            |
|-----------------------|-------------------------------------------------|
| `Header.tsx`          | mark + daemon dot + subtitle + Search/Settings  |
| `Hero.tsx`            | Continue card (full-width, 6-px accent rail, HIGH badge, 112 Resume) |
| `Investigations.tsx`  | stacked 48-px rows in a white card              |
| `Timeline.tsx`        | Today rail (time / source / label)              |
| `Activity.tsx`        | Browser + Desktop status cards                  |
| `TrustStrip.tsx`      | 4 tiny pills pinned to the bottom               |
| `SearchOverlay.tsx`   | Ctrl/Cmd+K overlay (Investigations / Files / Returns / Events) |
| `States.tsx`          | loading · reconnecting · offline · disconnected · empty plates |

### App shell

[`App.tsx`](../../apps/extension/ui/src/App.tsx) rewritten
to compose the six regions. The state machine + API client +
demo-overlay flow are preserved untouched. A new `searchOpen`
flag governs the SearchOverlay; Ctrl/Cmd+K toggles it.

### Capture harness

[`capture_extension.mjs`](../../apps/extension/ui/capture_extension.mjs)
gains a `OUT_7A` directory + seven new fixtures:

- `empty` · `capturing` · `active` · `resume` · `demo` ·
  `offline` · `search`

The `search` shot triggers Ctrl+K via Playwright keyboard
after the popup loads, so the capture proves the overlay
opens cleanly.

### Documentation

- [`docs/product/EXTENSION_PRODUCT_AUDIT.md`](../../docs/product/EXTENSION_PRODUCT_AUDIT.md)
  — frozen-product checklist: paint, motion, per-region
  contracts, 7-row state catalogue + 1 capture per row.

---

## Files touched

**New:**

- `apps/extension/ui/src/components/v2/Header.tsx`
- `apps/extension/ui/src/components/v2/Hero.tsx`
- `apps/extension/ui/src/components/v2/Investigations.tsx`
- `apps/extension/ui/src/components/v2/Timeline.tsx`
- `apps/extension/ui/src/components/v2/Activity.tsx`
- `apps/extension/ui/src/components/v2/TrustStrip.tsx`
- `apps/extension/ui/src/components/v2/SearchOverlay.tsx`
- `apps/extension/ui/src/components/v2/States.tsx`
- `docs/product/EXTENSION_PRODUCT_AUDIT.md`
- `docs/engineering/PHASE_7A_STATUS.md`
- 7 captures in `assets/screenshots/extension-7a/`

**Edited:**

- `apps/extension/ui/src/styles.css` — new 7A tokens
  (`#F5F2ED`, `#E6DED4`, `0 12 32 .06`, motion scale),
  popup frozen at 440 × 640.
- `apps/extension/ui/src/lib/motion.ts` — `calmFastest`
  + 120 / 180 / 240 scale.
- `apps/extension/ui/src/App.tsx` — composes the six
  regions; keeps the existing state machine + API + demo
  wiring.
- `apps/extension/ui/capture_extension.mjs` — `OUT_7A`
  directory + 7 fixtures, supports custom viewport height
  + post-shot callback for the search capture.

**Preserved (untouched but no longer rendered from App):**

- `apps/extension/ui/src/components/{ContinueCard,
  DebugStrip, DemoBanner, InvestigationCard, MemoryList,
  Section, TrustSurface, states}.tsx`. The Settings
  panel + icons + lib/api.ts + lib/types.ts are still
  the active code path.

---

## Verification matrix

| Check                                                       | Result   |
|-------------------------------------------------------------|----------|
| `npx tsc --noEmit` in `apps/extension/ui`                   | clean    |
| `npx vite build` in `apps/extension/ui`                     | clean (~293 KB JS) |
| `node capture_extension.mjs`                                | clean, 21 PNGs wrote |
| Window pinned to 440 × 640                                  | yes (`body { width / height; overflow: hidden }`) |
| Header carries mark + daemon dot + subtitle + 2 icons       | yes (capture) |
| Hero shows accent rail + HIGH + Resume 112 + max 3 chips    | yes (capture) |
| Investigations stack vertically with strength dots          | yes (capture) |
| Timeline shows mono time + bold source + label              | yes (capture) |
| Activity cards show Browser CAPTURING / Desktop SOON        | yes (capture) |
| Trust strip pinned with 4 tiny pills                        | yes (capture) |
| Search overlay opens on Ctrl+K with 4 groupings             | yes (capture) |
| Demo overlay shares the populated body render path          | yes      |

---

## Success criterion

The directive's three sentences must all land in one glance:

1. **Recall remembered work** — the hero card names *what was
   in flight*; the investigations list names *what else is
   live*.
2. **Recall can continue it** — the Resume button on the hero
   + the `1` shortcut chip make the next action obvious.
3. **Recall is running** — the breathing daemon dot in the
   header + the trust strip's `DAEMON OK` pill at the bottom
   give the same trust signal at both ends of the popup.

The capture matrix proves all three.
