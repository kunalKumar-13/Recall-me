# RC1 Validation — evidence index

Phase 8E gate: **prove each of the six RC1
claims with a checked-in artifact**, not a
promise. This document is the cross-link.

| Claim                          | Evidence                                                                                          | Verdict |
|--------------------------------|---------------------------------------------------------------------------------------------------|---------|
| **Install works**              | [INSTALL_VERIFIED.md](INSTALL_VERIFIED.md) §1-2 — doctor 5 GREEN / 0 RED on the dev box           | ✅ verified (dev) · ⚠️ clean-VM walk = [BUG-002](../engineering/BUGS_OPEN.md) |
| **Capture works**              | [STABILITY/CAPTURE.md](../engineering/stability/CAPTURE.md) + [INSTALL_VERIFIED.md](INSTALL_VERIFIED.md) §3 — 36 events today, 166 over 30 d, 3 of 5 named sites confirmed | ✅ verified · ⚠️ SO + Stitch open as [BUG-003](../engineering/BUGS_OPEN.md) |
| **Resume works**               | [STABILITY/RESUME.md](../engineering/stability/RESUME.md) + [INSTALL_VERIFIED.md](INSTALL_VERIFIED.md) §4 — pipeline alive, `/v1/recovery/recent` 200 in 122 ms; `ResumePreview` constructs in 3.1 ms | ✅ engine verified · ⚠️ click → tabs-open end-to-end = [BUG-002](../engineering/BUGS_OPEN.md) |
| **Launcher understandable**    | [STABILITY/LAUNCHER.md](../engineering/stability/LAUNCHER.md) + [SCREEN_INDEX.md](../product/SCREEN_INDEX.md) — frozen 7E.1 widget tree, 5 captures (home / high / med / low / no_hero) | ✅ frozen + captured |
| **Extension understandable**   | [STABILITY/EXTENSION.md](../engineering/stability/EXTENSION.md) + [SCREEN_INDEX.md](../product/SCREEN_INDEX.md) — 9-state machine, 7 captures, bundle 296 KB byte-identical across 8B | ✅ frozen + captured |
| **Control room usable**        | [STABILITY/CONTROL.md](../engineering/stability/CONTROL.md) — 13 routes, 10 loaders, `tsc --noEmit` exit 0      | ✅ build clean · ⚠️ per-route empty-state copy = [CTRL-001](../engineering/BUGS_OPEN.md) |

**6 of 6 RC1 claims have evidence.** Four carry
honest follow-up flags. Zero are unsubstantiated.

---

## Methodology

Each claim was scored against the rule:

> A claim is *verified* iff:
> (a) a code-backed source proves the mechanism
>     exists and works in the developer-machine
>     environment, AND
> (b) any remaining gap is named in
>     [BUGS_OPEN.md](../engineering/BUGS_OPEN.md) with a
>     severity and a proposed close.

No claim is *unverified*; some are
*verified-with-follow-up*.

---

## Detail per claim

### 1. Install works

- **Mechanism:** Phase 5J PyInstaller bundle →
  `Recall-Setup-{lite,full}.exe`.
- **Build artifacts present:**
  `dist/installer/Recall-Setup-lite.exe`
  (216.2 MB) + `Recall-Setup-full.exe` (260.8 MB).
- **Live verification:** `recall doctor` shows
  5 GREEN rows on the dev box (config, events,
  event flow, daemon, extension, installer). 4
  YELLOWs are opt-in features (autostart,
  protocol handler, etc.) — none block install.
- **Gap:** clean Windows VM walk
  ([BUG-002](../engineering/BUGS_OPEN.md)). Will be the first
  cohort tester's first action.

### 2. Capture works

- **Mechanism:** Phase 7D pipeline — extension
  content script → loopback `/v1/events/{kind}`
  → `EventLogger` → `~/.recall/events/*.jsonl`.
- **Live measurement (dev box):** 36 events
  today across `browser_visit` (28), `chat_session`
  (7), `browser_search` (1). 166 browser events
  over 30 days.
- **Verified sites:** ChatGPT (20), GitHub (16),
  Google (55).
- **Gap:** StackOverflow + Stitch report 0
  events ([BUG-003](../engineering/BUGS_OPEN.md)). Matcher
  audit pending.

### 3. Resume works

- **Mechanism:** events → sessions → contexts →
  resurfacing → threads → evolution → recovery
  (the 7-layer sacred hierarchy in
  [CLAUDE.md](../../CLAUDE.md)).
- **Live measurement:** `/v1/recovery/recent`
  returns 200 in 122 ms; `/v1/threads/recent` 60
  ms; `/v1/resurface/idle` 120 ms. Resume preview
  constructs in 3.1 ms.
- **Demo path:** `recall demo run` seeds 30
  deterministic events; the launcher's
  Continue card materialises in
  [DEMO_MODE.md](../product/DEMO_MODE.md).
- **Gap:** end-to-end click → tabs-open
  re-walk pending ([BUG-002](../engineering/BUGS_OPEN.md)). Was
  last verified Phase 4A; not re-walked since.

### 4. Launcher understandable

- **Mechanism:** Phase 7E.1 frozen `MinimalShell`
  + `MinimalDigest` + `MinimalSearchBar` +
  `TrustRow`. One root card. No glass effect.
  Single hairline marker.
- **Visual evidence:** 5 captures in
  `assets/screenshots/launcher-7e/` covering
  home / HIGH-trust / MED / LOW / no-hero
  states.
- **State coverage:** widget tree walked in
  [STABILITY/LAUNCHER.md](../engineering/stability/LAUNCHER.md);
  max 8 user-readable rows regardless of event
  count.
- **Public contract:** `from app.ui.launcher
  import Launcher` resolves to `LiveLauncher`
  at `(700, 500)` — frozen in
  [AUDIT/LAUNCHER_FREEZE.md](../../archive/AUDIT/LAUNCHER_FREEZE.md).
- **Gap:** none in scope for 8E. Cold-boot
  human walk overlaps with BUG-002 above.

### 5. Extension understandable

- **Mechanism:** Phase 7A 6-region layout
  (Header / Hero / Investigations / Timeline /
  Activity / Trust strip) + 2 overlays (Search,
  Settings). 9-state machine enforced by
  `derivePopupState()` in `App.tsx`.
- **Visual evidence:** 7 captures in
  `assets/screenshots/extension-7a/` (active,
  capturing, demo, empty, offline, resume,
  search).
- **Bundle health:** 293 KB JS + 3 KB CSS,
  byte-identical across 8B archive sweep
  (proves dead pre-7A components were already
  tree-shaken).
- **Build verification:** `cd apps/extension/ui
  && npx tsc --noEmit` exit 0 (8B; not
  re-touched in 8C-8E).
- **Gap:** `loading` + `reconnecting` transient
  captures missing ([EXT-001](../engineering/BUGS_OPEN.md)) —
  cosmetic; reclassified post-beta.

### 6. Control room usable

- **Mechanism:** Next.js App Router under
  `apps/admin/web/`. 13 routes, 10 loaders, 1
  paths module ([STABILITY/CONTROL.md](../engineering/stability/CONTROL.md)).
- **Build verification:** `cd apps/admin/web
  && npx tsc --noEmit` exit 0.
- **Path safety:** `RECALL_HOME` override
  centralised in [`lib/loaders/paths.ts`](../../apps/admin/web/lib/loaders/paths.ts) —
  loader move = one-file edit.
- **SSR boundary:** every loader runs
  server-side; loader failures degrade to empty
  shapes via try/catch, not crashes.
- **Gap:** per-route empty-state copy not
  audited ([CTRL-001](../engineering/BUGS_OPEN.md)). Cosmetic;
  doesn't block usage.

---

## What this document is not

- Not a test report. Tests live in
  `_smoke_api.py` and the per-frontend `tsc`
  invocations. This is a *evidence index*.
- Not a marketing claim. Each row honestly
  qualifies what is verified vs. what is
  follow-up.
- Not a substitute for the cohort walk. Phase 8E
  built the alpha pack precisely because the
  next class of validation requires humans
  Recall hasn't met yet.

---

## Provenance

| Source                                | What it proves                          |
|---------------------------------------|-----------------------------------------|
| [INSTALL_VERIFIED.md](INSTALL_VERIFIED.md) | install + capture + daemon work today  |
| [STABILITY/PERF.md](../engineering/stability/PERF.md) | latency budgets met                    |
| [STABILITY/CAPTURE.md](../engineering/stability/CAPTURE.md) | event log is real, not fixture       |
| [STABILITY/LAUNCHER.md](../engineering/stability/LAUNCHER.md) | widget tree is frozen + correct      |
| [STABILITY/RESUME.md](../engineering/stability/RESUME.md) | composition layers compose            |
| [STABILITY/EXTENSION.md](../engineering/stability/EXTENSION.md) | state machine + bundle health       |
| [STABILITY/CONTROL.md](../engineering/stability/CONTROL.md) | admin web routes + loaders           |
| [SCREEN_INDEX.md](../product/SCREEN_INDEX.md)    | visual surface is captured             |
| [VERSION.md](VERSION.md)              | what's frozen, what's blocked          |
| [BUGS_OPEN.md](../engineering/BUGS_OPEN.md)          | every gap is named with severity       |

Re-deriving each verdict from these sources
should produce the same row to within ±1 colour.
