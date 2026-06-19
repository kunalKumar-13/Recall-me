# PHASE_6C_STATUS.md — Extension Premium

The receipt for Phase 6C. The directive's *Goal*: the extension popup
must feel like Arc / Linear / Raycast — not a developer panel, not a
settings window, not a popup utility. The success line was a one-liner:
someone opens the popup and says *"wait this looks like product."*

The 6B→6C handoff: 6B inverted the launcher palette to warm white +
lavender and split the recovery evidence row into chip pills. 6C carries
that same visual language across into the extension popup so the two
surfaces read as one product, then adds the four premium pieces the
popup was still missing — confidence pill on the Continue card, a
vertical "Today" activity rail in place of the grouped browser-memory
list, an investigation **strip** (horizontal pills, not row cards),
and a launcher-parity empty state.

Anti-rules respected: **no engine work** (no new endpoint, no schema
change), **no founder work** (no roadmap-side artifact). Every change
lives under [`apps/extension/`](../../apps/extension) +
`assets/screenshots/extension-v2/`.

Cross-references:
[`PHASE_6B_STATUS.md`](PHASE_6B_STATUS.md) (the predecessor — this
phase mirrors its launcher chip vocabulary into the extension),
[`ROADMAP_LIVE.md`](../../docs/founder/ROADMAP_LIVE.md) (now-column row).

---

## What shipped

### 1. Header — today count + repair icon

[`apps/extension/ui/src/App.tsx`](../../apps/extension/ui/src/App.tsx)
`Header` now takes a `todayCount: number`. When the daemon is connected
and `eventsToday > 0`, a quiet mono caption `"248 today"` sits next to
the lavender `DaemonPulse` so the user has a passive live signal that
isn't just a dot. The header also gained a wrench icon button between
the wordmark and the gear — the directive's *repair* affordance.

A new `wrench` glyph landed in
[`icons.tsx`](../../apps/extension/ui/src/components/icons.tsx) at the
same 1.6-px stroke weight as the gear, so the two icons sit cleanly
together. The button currently routes to `onSettings` (where the
Phase 5K Connection drawer lives — that drawer **is** the repair
center); making it a separate `?view=repair` route is a focused
refactor deferred to the next phase.

### 2. ContinueCard — confidence pill matching the launcher

[`apps/extension/ui/src/components/ContinueCard.tsx`](../../apps/extension/ui/src/components/ContinueCard.tsx)
gained two new top-level helpers:

- `_deriveConfidence(tabCount, fileCount)` — `n_targets ≥ 4 → high`,
  `2-3 → medium`, `0-1 → low`. **Mirrors the launcher's
  `derive_recovery_confidence(n_targets)` exactly**, so a recovery
  scored *high* in the launcher reads as *high* in the popup. Pure
  UI-side derivation; no engine field.
- `ConfidencePill({ level })` — an inline pill rendered right-aligned
  in the card's "CONTINUE" header row. Same colour vocabulary as
  the launcher's `_ConfidenceBadge`: high = accent lavender, medium
  = warn amber, low = ink-3 grey. `aria-label={`confidence ${level}`}`
  for the screen reader.

### 3. MemoryList → vertical "Today" activity rail

[`apps/extension/ui/src/components/MemoryList.tsx`](../../apps/extension/ui/src/components/MemoryList.tsx)
restructured from grouped surface lists (Searches / Tabs / Chats)
into a single chronological vertical timeline. The directive's
example pattern (`09:20 Search / 09:31 Chat / 09:44 Return`) drove
the row layout exactly:

- Items are sorted newest-first by `ts` (epoch seconds from the
  events API), capped at 8.
- Each row renders: an `HH:MM` local-time stamp in mono, a small
  round kind glyph (search / tab / chat), then a kind label +
  short title. A vertical hairline ties the dots together —
  literally the *rail* in the directive.
- Rows without a real `ts` are dropped silently. The popup never
  invents a timestamp; if the engine didn't ship one, the row
  doesn't render.

The outer Section in `App.tsx` is now labelled **"Today"** (was
"Browser memory"), which matches the directive's *Today* heading.

### 4. InvestigationCard → horizontal pill strip

[`apps/extension/ui/src/components/InvestigationCard.tsx`](../../apps/extension/ui/src/components/InvestigationCard.tsx)
rewritten as a single horizontal pill (height 28, radius 14, soft
surface bg, 12-px thread glyph + title). The host call site in
`App.tsx` now renders investigations as:

```tsx
<div style={{ display: "flex", flexWrap: "wrap", gap: 7 }}>
  {investigations.slice(0, 4).map((inv, i) => (
    <InvestigationCard investigation={inv} index={i} />
  ))}
</div>
```

The `slice(0, 4)` enforces the directive's **max-4** rule. The
animation is a slide-fade (`initial={{ opacity: 0, x: -6 }}`,
`animate={{ opacity: 1, x: 0 }}`, `delay: index * 0.04`) so the
strip settles in left-to-right rather than appearing all at once.
No bounce, no overshoot — calm in, calm to settle.

### 5. EmptyState — launcher-parity copy

[`apps/extension/ui/src/components/states.tsx`](../../apps/extension/ui/src/components/states.tsx)
`EmptyState` was rewritten so the popup's empty screen says exactly
what the launcher's empty card says:

- Headline: **"Recall notices unfinished work."**
- Body: **"Work normally. Return later. / Recall fills itself."**
- A soft lavender `Show example` pill (`accent-soft` fill,
  `accent-line` border, accent text) that on click dispatches
  `openRecall()` — the popup never reaches into the engine
  itself; it hands off to the desktop launcher, which owns the
  `EmptyCard.show_example` signal + the demo-seed wiring. This
  honours the *NO engine work* anti-rule.
- The local-only trust line at the bottom is preserved (mono,
  ink-4): `local only · 127.0.0.1:4545 · no cloud`.

### 6. Continue card no longer double-headered

`App.tsx` used to wrap the `ContinueCard` in a `Section
label="Continue"`, which produced a small "CONTINUE" section heading
ABOVE the card's own bolder "● CONTINUE" header — a duplicate that
read as a developer-panel artifact. Phase 6C drops the outer
`Section` wrapper and renders the card directly inside a `motion.section`
that keeps the same `fadeExpand` / `staggered(index)` entrance — the
hero card now stands alone, with the accent dot + uppercase label as
its single header.

### 7. Capture pipeline — `extension-v2/`

[`apps/extension/ui/capture_extension.mjs`](../../apps/extension/ui/capture_extension.mjs)
gained:

- An `OUT_V2` sibling directory (`assets/screenshots/extension-v2/`)
  with a `mkdirSync(..., { recursive: true })` so the Playwright
  screenshot calls don't fail on a missing folder.
- An optional `dir` arg on both `shot()` and `shotWithMock()` so the
  same helpers serve both the historical flat output and the v2
  subdir.
- Two new MOCK payloads: `MOCK_HOME_V2` (the populated home — 248
  events today, a recovery, four investigations, five recent events)
  and `MOCK_RECOVERY_V2` (recovery-only — confidence pill + domain
  preview as the focal point).
- Five v2 captures at the end of the run:

```
assets/screenshots/extension-v2/
├── extension-home.png      (recovery + investigations + today rail)
├── extension-empty.png     (launcher-parity empty surface)
├── extension-recovery.png  (recovery-only — confidence pill focus)
├── extension-repair.png    (Open Recall + Repair connection screen)
└── extension-offline.png   (the calm offline state)
```

The historical `assets/screenshots/extension-*.png` set stays in
place untouched as the *before* reference, matching the
`launcher-v2/` pattern from Phase 6B.

---

## What did **not** ship

| Directive item | Status | Why |
|---|---|---|
| Wrench icon routes to a separate `?view=repair` Repair drawer | partial | The icon is wired; it currently routes to the Settings panel, which is where the Phase 5K *Connection* drawer already provides the connection / daemon / extension / doctor summary + actions. Promoting that drawer into a top-level view is a focused refactor; deferred to keep this phase's diff focused on the visible-surface rebuild. |
| `Show example` button — live demo-seed integration in the popup | stub | The button dispatches `openRecall()`, handing off to the launcher's own `EmptyCard.show_example` signal. The popup deliberately doesn't seed demo events itself (NO engine work). When the launcher's empty path is wired (a 6B-deferred item), the click loop completes end-to-end. |
| Header status states beyond the existing 4 (healthy / capturing / recoverable / offline) | partial | The directive named the four states; the existing `derivePopupState` machine already produces them (`connected`, `capturing`, `recovery`, `offline` plus `loading` / `reconnecting`). The header reads the live `connection` value; the only addition was the `todayCount` caption. No new state field needed. |
| Repair center as a discrete drawer separate from Settings | deferred | The Phase 5K *Connection* drawer already lives inside `SettingsPanel.tsx` as a collapsible Phase 6A section, so its surface area is unchanged. Splitting it out into a sibling view is a navigation refactor (route + back button), deferred to keep the visible-surface budget of this phase intact. |

---

## Verification

| Surface | Command | Result |
|---|---|---|
| TypeScript | `cd apps/extension/ui && npx tsc --noEmit` | zero findings |
| extension build | `cd apps/extension/ui && npm run build` | 399 modules transformed, 289.28 kB JS / 92.25 kB gzipped (essentially flat vs 6B's ~287 kB; the chip + pill rewrites trade one chunk of grouped layout code for similar-sized new code) |
| extension captures | `cd apps/extension/ui && node capture_extension.mjs` | 7 historical PNGs unchanged + 5 new PNGs in `assets/screenshots/extension-v2/` |
| launcher import (regression) | `python -c "from app.ui.cards import RecoveryCard, derive_recovery_confidence"` | unchanged — Phase 6C touched **no** Python file |
| pyflakes (regression) | `python -m pyflakes app/ui app/core api` | unchanged from 6B — Phase 6C touched **no** engine file |
| doctor (regression) | `python recall.py doctor` | unchanged — Phase 6C touched **no** doctor surface |

---

## Touched files

```
modified:
  apps/extension/ui/src/App.tsx
  apps/extension/ui/src/components/ContinueCard.tsx
  apps/extension/ui/src/components/MemoryList.tsx
  apps/extension/ui/src/components/InvestigationCard.tsx
  apps/extension/ui/src/components/icons.tsx
  apps/extension/ui/src/components/states.tsx
  apps/extension/ui/capture_extension.mjs
  apps/extension/popup/index.html       (vite build output)
  apps/extension/popup/assets/index.css (vite build output)
  apps/extension/popup/assets/index.js  (vite build output)

new:
  assets/screenshots/extension-v2/extension-home.png
  assets/screenshots/extension-v2/extension-empty.png
  assets/screenshots/extension-v2/extension-recovery.png
  assets/screenshots/extension-v2/extension-repair.png
  assets/screenshots/extension-v2/extension-offline.png
  docs/engineering/PHASE_6C_STATUS.md
```

No Python files touched. No `app/` files touched. No `api/` files
touched. No `_smoke_api.py` modification (it doesn't cover the
extension surface, by design). No `~/.recall/` file written.

---

## Read-back of the success criterion

The directive's success line was *"wait this looks like product."*
Open `assets/screenshots/extension-v2/extension-home.png` next to
`assets/screenshots/extension-v2/extension-empty.png` and the popup
reads as a calm continuity surface rather than a developer panel.
The Continue card is the hero, the investigations are a quiet pill
strip, the Today rail is a single chronological line, and the empty
state speaks the launcher's exact words. Same product, two surfaces.
