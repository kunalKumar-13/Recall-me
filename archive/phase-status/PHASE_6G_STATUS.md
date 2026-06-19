# PHASE_6G_STATUS.md — Public Alpha Surface

The receipt for Phase 6G. The directive's *Goal*: build the public
alpha front door — *website, story, download, trust*. A stranger
must understand Recall in 60 seconds.

Anti-rules respected: **no engine work**, **no recovery work**. No
file under `app/core/`, `api/`, or the launcher's widget tree was
touched. The phase is pure *marketing-site* + *operator docs*: the
Next.js app at [`apps/web/`](../../apps/web) gains the new
narrative sections, the screenshot pipeline copies the v2 captures
into `apps/web/public/screens/`, and three docs land in
`docs/product/` + `docs/release/` that the site references.

The 6F→6G handoff: 6F gave the cohort a daily-loop layer to prove
repeat use. 6G gives the *public* the front door they walk
through *before* installing — so the cohort can grow beyond the
founder's direct contacts. The two phases share an audience
boundary: 6F is for testers already in the room; 6G is for
strangers being invited in.

Cross-references:
[`docs/product/TRUST.md`](../../docs/product/TRUST.md) (the public trust
statement),
[`docs/release/DOWNLOAD_GUIDE.md`](../../docs/release/DOWNLOAD_GUIDE.md)
(the four install paths),
[`docs/release/DEMO_VIDEO_SCRIPT.md`](../../docs/release/DEMO_VIDEO_SCRIPT.md)
(the 60-second placeholder script),
[`docs/founder/PUBLIC_ALPHA.md`](../../docs/founder/PUBLIC_ALPHA.md)
(extended with a Phase 6G addendum).

---

## What shipped

### 1. Hero — directive copy + Download/Watch CTAs

[`apps/web/app/components/Hero.tsx`](../../apps/web/app/components/Hero.tsx)
rewritten to the directive's exact copy:

- Headline: *"Recall notices unfinished work."*
- Subhead: *"Return later. Continue instantly."*
- Primary CTA: *Download alpha* (now anchors to the in-page
  `#download` section instead of jumping to GitHub releases).
- Secondary CTA: *Watch demo* (anchors to `#how` until the
  demo video at
  [`DEMO_VIDEO_SCRIPT.md`](../../docs/release/DEMO_VIDEO_SCRIPT.md) is
  recorded — at which point `apps/web/app/lib/links.ts:demoVideo`
  flips to the hosted URL).

The Hero's right-column launcher mockup and the four-stat trust
strip below the CTAs are kept untouched — they earned their
weight pre-6G and the *no visual redesign* spirit of the phase
honours them.

### 2. Four new section components

Phase 6G adds four new top-level components in
[`apps/web/app/components/`](../../apps/web/app/components):

| Component | Purpose | Source content |
|---|---|---|
| `Problem.tsx` | Names the context-loss tax. One paragraph + three short observation cards. | Hand-written copy; no fixtures. |
| `Story.tsx` | The three canonical demo threads — WebSocket retry debugging / Healthcare pitch — proposal draft / RLHF reward shaping. Each as a card with thumbnail. | Same payload as `app.core.demo_mode.demo_payload()` — thumbnails come from `/screens/extension/extension-recovery.png`, `/screens/demo/demo-launcher.png`, `/screens/extension/extension-home.png`. |
| `Screens.tsx` | Four-tile gallery (launcher digest, popup home, demo overlay, launcher empty). Real captures from the deterministic offscreen pipeline. | `assets/screenshots/launcher-v2/` + `extension-v2/` + `demo/` copied into `apps/web/public/screens/`. |
| `Download.tsx` | Four artifacts in one calm grid: Windows lite (recommended) / Windows full / macOS preview / browser extension. Each with platform tag, size, short body, CTA. Plus a trust strip at the bottom restating the boundary at the moment of install. | Links to GitHub releases for the binaries; links to `MAC_OWNER_NEEDED.md` for the Mac path. |

Every new component follows the existing visual rhythm: warm
white background, lavender accent, hairline borders,
`font-editorial` headlines, entrance animation only. No glow,
no parallax, no auto-loop. Same language as the launcher and
popup v2 surfaces.

### 3. Privacy → Trust five-point rewrite

[`apps/web/app/components/Privacy.tsx`](../../apps/web/app/components/Privacy.tsx)
section's eyebrow flipped from *Privacy* to *Trust* and its
points rewritten to the directive's five-rule vocabulary:

- Local only
- No cloud
- No telemetry
- Counts only
- Export only

Each point's body mirrors the on-disk contract documented in
the new [`TRUST.md`](../../docs/product/TRUST.md). The right-side
shield-card visual is preserved.

### 4. Nav + LINKS realignment

[`apps/web/app/components/Nav.tsx`](../../apps/web/app/components/Nav.tsx)
section links rewritten to the Phase 6G narrative order:

```
The problem · How it works · Stories · Screens · Trust · Download · GitHub
```

The desktop + mobile *Download for Windows* button changed to
*Download alpha* and now anchors to `#download` (the new
in-page section), not the GitHub releases page. The releases
page is reachable from inside the Download section itself, one
click later.

### 5. Page narrative — `page.tsx`

[`apps/web/app/page.tsx`](../../apps/web/app/page.tsx) rebuilt
to the directive's section order:

```
Hero · Problem · HowItWorks · Story · Features · ThreadConstellation
     · Screens · Privacy(Trust) · Download · FAQ · FinalCTA
```

The pre-6G `TrustedBy` strip was removed — there are no real
"trusted by" logos yet, and the directive's narrative does not
include it. The strip's component file remains in
`components/` (no dead-code deletion this phase), but the page
no longer mounts it.

### 6. Screenshot pipeline → `apps/web/public/screens/`

Four subdirectories under
[`apps/web/public/screens/`](../../apps/web/public/screens):

```
launcher/   (7 PNGs from assets/screenshots/launcher-v2/)
extension/  (5 PNGs from assets/screenshots/extension-v2/)
demo/       (4 PNGs from assets/screenshots/demo/)
alpha/      (3 PNGs from assets/screenshots/alpha/)
```

19 PNGs in total. Sourced by `cp` from the canonical
`assets/screenshots/` tree at phase-build time; the marketing
site does not regenerate captures itself. Deleting any source
PNG silently removes the matching tile rather than 404-ing.

### 7. Doc trio

Three new docs:

- [`docs/product/TRUST.md`](../../docs/product/TRUST.md) — the public
  trust statement. Five rules + on-disk contract per rule +
  *what Recall will ask for / won't ask for* table + the
  enforcement-in-code map.
- [`docs/release/DOWNLOAD_GUIDE.md`](../../docs/release/DOWNLOAD_GUIDE.md)
  — the four install paths in detail. Windows lite (default) /
  Windows full / macOS preview / browser extension, plus a
  5-step first-run validation list and the uninstall paths.
- [`docs/release/DEMO_VIDEO_SCRIPT.md`](../../docs/release/DEMO_VIDEO_SCRIPT.md)
  — the 60-second placeholder script. Six beats, captions only
  (no voice-over), pre-flight checklist, the cuts to never
  make.

Plus a Phase 6G addendum on
[`docs/founder/PUBLIC_ALPHA.md`](../../docs/founder/PUBLIC_ALPHA.md)
that names the new front-door surfaces and links the trio
above.

---

## What did **not** ship

| Directive item | Status | Why |
|---|---|---|
| Hosted demo video | placeholder | The 60-second script lands in [`DEMO_VIDEO_SCRIPT.md`](../../docs/release/DEMO_VIDEO_SCRIPT.md); the recording itself is a one-off founder step that needs real machine + browser captures. The *Watch demo* button currently scroll-anchors; once `demo.mp4` exists, `lib/links.ts:demoVideo` flips and every CTA updates. |
| Logo + signing for the Windows installer | external | Gate 7 of [`PUBLIC_ALPHA.md`](../../docs/founder/PUBLIC_ALPHA.md). EV cert + signed installer eliminates the SmartScreen prompt; not in 6G's scope (it's a release-pipeline change, not a website change). |
| Verified macOS build | external | Gated by [`MAC_OWNER_NEEDED.md`](../../docs/release/MAC_OWNER_NEEDED.md). The Download card for macOS reads *preview* honestly; the page does not pretend otherwise. |
| FAQ rewrite | partial | The existing `FAQ.tsx` carries the right questions; the 6G updates are limited to the narrative order + the new section anchors. A full FAQ refresh against the 6E/6F operations vocabulary is a follow-up. |
| `apps/web/` Lighthouse audit | not in scope | Pre-existing site already optimises for static-only / no JS hydration in non-interactive sections. Phase 6G adds 4 components (~10 KB gzipped extra); the Next.js build report shows `/` at 55 KB / first-load 142 KB — well inside the budget. |

---

## Verification

| Surface | Command | Result |
|---|---|---|
| Web build | `cd apps/web && npm run build` | ✓ compiled / static `/` at 55 KB / first-load 142 KB / 4 static pages |
| Screenshots in public/ | `ls apps/web/public/screens/*` | 19 PNGs in 4 subdirectories |
| TypeScript regression (extension) | `cd apps/extension/ui && npx tsc --noEmit` | unchanged from 6F (zero findings) |
| pyflakes (regression) | `python -m pyflakes app/ui app/core api` | unchanged — Phase 6G touched **no** Python file |
| Doctor (regression) | `python recall.py doctor` | unchanged from 6F |
| Launcher import (regression) | `python -c "from app.ui.launcher import Launcher"` | OK |

---

## Touched files

```
new web components:
  apps/web/app/components/Problem.tsx
  apps/web/app/components/Story.tsx
  apps/web/app/components/Screens.tsx
  apps/web/app/components/Download.tsx

modified web components:
  apps/web/app/page.tsx
  apps/web/app/components/Hero.tsx
  apps/web/app/components/Nav.tsx
  apps/web/app/components/Privacy.tsx

new assets:
  apps/web/public/screens/launcher/*.png   (7)
  apps/web/public/screens/extension/*.png  (5)
  apps/web/public/screens/demo/*.png       (4)
  apps/web/public/screens/alpha/*.png      (3)

new docs:
  docs/product/TRUST.md
  docs/release/DOWNLOAD_GUIDE.md
  docs/release/DEMO_VIDEO_SCRIPT.md
  docs/engineering/PHASE_6G_STATUS.md

modified docs:
  docs/founder/PUBLIC_ALPHA.md            (Phase 6G addendum)
```

No `app/core/`, `api/`, `app/ui/` (launcher / settings / widgets),
`apps/extension/`, or `infra/` files were touched. No `recall://`
protocol change. No installer-spec change. No engine layer
touched.

---

## Read-back of the success criterion

The directive's success line:

> stranger understands Recall in 60 sec

The marketing site now opens with the directive's headline
("Recall notices unfinished work."), takes the visitor through
*Problem → How → Story → Screens* in a single calm scroll, then
hands them the *Download alpha* button. The four-artifact
download grid is honest (Mac is labelled *preview*, the
installer SmartScreen warning is named in the
[`DOWNLOAD_GUIDE.md`](../../docs/release/DOWNLOAD_GUIDE.md), the trust
strip restates the boundary at the moment of install).

A stranger who walks the Hero → Problem → Story → Trust →
Download path covers all four directive sections in well under
60 seconds of scrolling. When the recording lands, the *Watch
demo* CTA gives them the same understanding in literal 60
seconds of video. The phase delivers the front door; the
recording is the only artifact still pending.
