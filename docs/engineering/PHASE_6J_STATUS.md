# PHASE_6J_STATUS.md — Control Room V2

The receipt for Phase 6J. The directive's *Goal*: the control room
becomes the founder's actual operating system. **No mock values.
No placeholder buttons. Everything actionable.**

The 6H→6J handoff: 6H planted the live-loader data plane and the
three-column shell. 6J adds the global chrome (top bar + bottom
bar + command palette), five new routes (extension / launcher /
experiments / logs / screenshots), and the deeper interactions
the directive named (filters · diff view · copy diagnostics).
Zero engine touches.

Cross-references:
[`PHASE_6H_STATUS.md`](PHASE_6H_STATUS.md) (the v1 foundation),
[`CONTROL_ROOM_V2.md`](../founder/CONTROL_ROOM_V2.md) (the user
manual the founder reads),
[`FOUNDER_OPERATIONS.md`](../founder/FOUNDER_OPERATIONS.md) (the
daily cadence the room supports).

---

## What shipped

### 1. Global chrome — top bar + bottom bar

| Component | Reads | What it shows |
|---|---|---|
| [`TopBar.tsx`](../../apps/admin/web/components/TopBar.tsx) | `loadAlpha()` · `loadRelease()` · `loadSystemSnapshot()` | Wordmark + three live pills (daemon · readiness · installs) + `⌘K` search trigger. Sticky 48 px header. |
| [`BottomBar.tsx`](../../apps/admin/web/components/BottomBar.tsx) | layout-loaded `release` + `system` | Version + doctor verdict pill + build label. Sticky 32 px footer. |
| [`ShellClient.tsx`](../../apps/admin/web/components/ShellClient.tsx) | — | Client wrapper that wires `⌘K` / `Ctrl-K` to the palette. |

Both bars derive every value from the same loaders the inner
pages use; the layout reads them once and passes them down.

### 2. Command palette

[`CommandPalette.tsx`](../../apps/admin/web/components/CommandPalette.tsx)
— `⌘K` / `Ctrl-K` opens, Esc closes, ↑↓ navigates, Enter selects.
Fuzzy-search over every route (14) and every directive-named
action (9):

```
Run doctor · Bake data · Generate alpha report · Export trust ·
Open screenshots · Open alpha folder · Open recovery journal ·
Open daily loop · Open logs · Refresh data
```

Selecting a route navigates; selecting an action copies the
canonical CLI command to the clipboard. The palette never makes
a server call — the *no server* contract Phase 6H established
holds end-to-end.

### 3. Two new loaders

| Module | Reads | Returns |
|---|---|---|
| [`logs.ts`](../../apps/admin/web/lib/loaders/logs.ts) | five canonical sources (`~/.recall/doctor.jsonl`, `alpha/recovery_journal.json`, `~/.recall/daily_loop.jsonl`, `alpha/alpha_report.md`, `apps/admin/data/release.json`) | `LogSource[]` — id / label / mtime / kind / entries / verdict. |
| [`screenshots.ts`](../../apps/admin/web/lib/loaders/screenshots.ts) | `assets/screenshots/{launcher-v2,launcher-v3,extension-v2,demo,alpha}/` + the legacy flat bucket | `ScreenshotBucket[]` — id / label / dir / count / files / expected / **missing** / verdict. |

The `screenshots.ts` loader is the source of truth for the
directive's *missing markers* — every expected PNG is named, and
the bucket's verdict turns red the moment one is absent.

### 4. Left nav — 12 sections, 4 groups

Updated [`Nav.tsx`](../../apps/admin/web/components/Nav.tsx) to the
directive's order:

```
overview:   Overview
cohort:     Users
engine:     Recovery · Replay · Daily Loop · Trust
ship:       Release · System · Extension · Launcher
lab:        Experiments · Docs
```

Hotkeys 1-9 + 0 on the first ten rows; Experiments + Docs
reachable via the palette.

### 5. Five new routes

| Route | Reads | What it does |
|---|---|---|
| `/extension` | manifest + `loadDailyLoop()` + `loadSystemSnapshot()` | Pairing health (paired? · ext/engine version drift) · capture rate (events / day · last activity · returns 7d · resume success%) · popup screenshot gallery · clipboard repair commands. |
| `/launcher` | `loadScreenshots()` + filesystem | v3 gallery · **v3 ↔ v2 diff strip** (side-by-side images for digest / empty / continue / focused) · promotion checklist (six items, each with a verdict, surfacing the Phase 6I deferred wire-in). |
| `/experiments` | `loadAlpha()` + `loadDailyLoop()` + `~/.recall/config.json` + `~/.recall/demo.json` | 8 feature flags (demo overlay · episodic capture · browser ingest · resurfacing · threads · daily loop · evolution · recovery) each with live value + flip command + verdict pill; 4 alpha-gate cards; 3 GREEN-floor threshold cards. |
| `/logs` | `loadLogSources()` + `loadOneLog(id)` | Picker (5 sources, per-source verdict + entry count) + filtered viewer (`?q=` substring) + download command. Renders the first 200 entries; refines via the filter. |
| `/screenshots` | `loadScreenshots()` | One section per bucket. Per-bucket verdict + thumbnails + **missing markers** strip (every expected file the bucket doesn't have). |

### 6. Recovery Lab extended

[`/recovery`](../../apps/admin/web/app/recovery/page.tsx) gained:

- a **kind filter strip** (all · shown · accepted · ignored · correct_silence · bad_recovery · resume_ok) that narrows the ledger row list via the `?kind=` query param;
- a **confidence distribution** block (high / medium / low) derived from per-tester `first_resume_ok`;
- a **return-after-gap heatmap** — 7-day strip of `return_after_gap = true` entries from the journal.

The pre-6J 6-stat header + time-to-resume sparkline + ledger
rows are preserved.

### 7. System Console — Copy diagnostics

[`/system`](../../apps/admin/web/app/system/page.tsx) now renders a
pre-built markdown blob (handles + mtimes + verdicts; **no PII**,
**no URLs**, **no filenames**) plus a
[`CopyDiagnostics`](../../apps/admin/web/components/CopyDiagnostics.tsx)
button that puts the blob on the clipboard. A live-refresh
button next to it re-runs the server fetch.

### 8. Public screenshot assets

The admin web's `public/screens/` directory was populated with
the v2 + v3 + demo + alpha bucket PNGs (mirroring
`assets/screenshots/`). This is what powers the `/extension`,
`/launcher`, and `/screenshots` galleries — Next.js's static
asset serving keeps the cost minimal.

### 9. Data cleanup

Every panel + route reads from a typed loader; no component
carries inline fixture values. The pre-6H `HealthOverview`,
`AlphaCohorts`, and `TrustRoom` legacy components are still
present (they back the *baked operator cards* section of the
panels that surface them) but they only render data their parent
loader hands them. The directive's *no mock values, no
hardcoded cards* rule held.

---

## What did **not** ship

| Directive item | Status | Why |
|---|---|---|
| `/launcher` real diff (image-difference, not side-by-side) | not in scope | Side-by-side is the calmer read for *visual* changes the founder is judging by eye. A pixel diff would need an image-processing pass on every request; deferred. |
| Replay Studio scrubbable timeline | partial | Per-tester timeline + coverage line ship; a real scrubber (drag handle to step through state) would require client-side state and an interaction model the directive's *no placeholder buttons* rule would judge harshly without real per-step data. Will follow when ledger entries carry sub-day timestamps. |
| Logs *download* (file dump) | partial | The Logs page emits the `Get-Content -Raw … \| Set-Clipboard` command. A real download would need a browser file-save trigger; deferred so the page stays a pure server component. |
| Experiments *toggle* (actually flip a flag) | partial | The page shows the live flag + the **flip command**. Flipping from the browser would require either a daemon endpoint or a clipboard-pasted PowerShell — the same anti-rule the actions sidebar resolved by handing the command back. |

---

## Verification

| Surface | Command | Result |
|---|---|---|
| Admin TypeScript | `cd apps/admin/web && npm run build` | ✓ compiled / 14 routes + `_not-found` / 87.4 KB first-load shared; per-route deltas of 165 B-704 B |
| Admin TS check | `cd apps/admin/web && npx tsc --noEmit` | zero findings (the build's lint pass surfaced + fixed: `experiments` page's unused `exists` import; `logs.ts`'s unused `listDir` import; layout's `"warn"`-typed comparison) |
| pyflakes (regression) | `python -m pyflakes app/ui app/core api` | zero findings — Phase 6J touched **no** Python file |
| Doctor (regression) | `python recall.py doctor` | unchanged from 6I |
| Marketing site (regression) | `cd apps/web && npx tsc --noEmit` | unchanged from 6I |
| Extension (regression) | `cd apps/extension/ui && npx tsc --noEmit` | unchanged from 6I |

---

## Touched files

```
new code:
  apps/admin/web/components/TopBar.tsx
  apps/admin/web/components/BottomBar.tsx
  apps/admin/web/components/ShellClient.tsx
  apps/admin/web/components/CommandPalette.tsx
  apps/admin/web/components/CopyDiagnostics.tsx
  apps/admin/web/lib/loaders/logs.ts
  apps/admin/web/lib/loaders/screenshots.ts
  apps/admin/web/app/extension/page.tsx
  apps/admin/web/app/launcher/page.tsx
  apps/admin/web/app/experiments/page.tsx
  apps/admin/web/app/logs/page.tsx
  apps/admin/web/app/screenshots/page.tsx

modified code:
  apps/admin/web/app/layout.tsx           (top + bottom bars + ShellClient mount + live stats)
  apps/admin/web/app/globals.css          (topbar / bottombar / palette CSS)
  apps/admin/web/app/recovery/page.tsx    (kind filter + confidence dist + return heatmap)
  apps/admin/web/app/system/page.tsx      (Copy diagnostics + diagnostics preview)
  apps/admin/web/components/Nav.tsx       (12-row directive order, 4 groups)
  apps/admin/web/lib/loaders/paths.ts     (SCREENSHOTS_DIR + EXTENSION_DIR + LAUNCHER_V3_DIR + EXTENSION_MANIFEST)
  apps/admin/web/lib/loaders/index.ts     (export the two new loaders)

new assets:
  apps/admin/web/public/screens/launcher-v2/*.png    (mirrored from assets/)
  apps/admin/web/public/screens/launcher-v3/*.png
  apps/admin/web/public/screens/extension-v2/*.png
  apps/admin/web/public/screens/demo/*.png
  apps/admin/web/public/screens/alpha/*.png

new docs:
  docs/founder/CONTROL_ROOM_V2.md
  docs/engineering/PHASE_6J_STATUS.md
```

No `app/`, `api/`, `apps/extension/`, or `apps/web/` files were
touched. No engine layer touched. The live launcher untouched.
The directive's anti-rules held.

---

## Read-back of the success criterion

The directive's success line:

> founder can run Recall from the control room

The room now carries:

- **the 30-second understanding** at the overview + top-bar
  pills + bottom-bar verdict;
- **the 5-minute management surface** via the 14 deep-dive
  routes;
- **every operator action** the founder runs in a terminal,
  one keystroke away via `⌘K`;
- **the trust contract restated** at every surface (loaders
  render *honest empty* states; the system page emits a
  redacted diagnostics blob);
- **the screenshots, the cohort, the recovery ledger, the
  daily-loop counters, the release gates, the feature flags,
  the log sources, the doctor verdicts** — all live-derived
  from the same files the CLIs read.

The founder can now sit in the control room and run Recall.
That is the bar the phase set out to clear.
