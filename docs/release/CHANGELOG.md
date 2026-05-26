# Changelog

All notable changes to Recall are recorded here.

The format is loosely based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the
project follows [Semantic Versioning](VERSIONING.md). Internal
phase identifiers (Phase 2A, 2B, …) are listed alongside the
public version so contributors can trace artefacts back to their
build cycle.

## [Unreleased]

### Added — Phase 8E (Alpha Users + Evidence Loop)
- **[`alpha/pack/`](../../alpha/pack/WELCOME.md)** —
  7-doc cohort welcome pack matching the
  install → browse → leave → return → resume →
  report flow. Privacy boundary repeated verbatim
  in every doc.
- **[`alpha/users_live.json`](../../alpha/users_live.json)**
  — schema `alpha-users-live-v1`; 9 PII-free
  fields per user; founder = `alpha-001`
  baseline; 4 open seats.
- **`recall alpha review` CLI** — new subcommand
  (~110-line `cmd_review` in
  [`app/core/alpha_cli.py`](../../app/core/alpha_cli.py)).
  ASCII-only board over 3 sources
  (`users_live.json` + recovery journal + wow /
  failures dirs); prints 6 directive-named lines
  + 4 target-check lines.
- **[`alpha/failures/`](../../alpha/failures/README.md)**
  — README + 5-field TEMPLATE + 1 real incident
  ([BUG-001 8B archive over-reach
  postmortem](../../alpha/failures/2026-05-24-launcher-imported-demo-data.md)).
- **[`alpha/wow/`](../../alpha/wow/README.md)** —
  README + TEMPLATE; verbatim-only rule
  enforced; anonymisation guide for public-facing
  quotes.
- **[`RC_VALIDATION.md`](../../RC_VALIDATION.md)**
  — cross-link evidence index for the 6 RC1
  claims (install / capture / resume / launcher /
  extension / control-room). All 6 backed by
  checked-in artifacts; 4 carry honest follow-up
  flags.
- **[`docs/engineering/PHASE_8E_STATUS.md`](../engineering/PHASE_8E_STATUS.md)**
  — 8E capstone with 9-line verification table.

### Changed — Phase 8E
- **[`RELEASE_READINESS.md`](../../RELEASE_READINESS.md)**
  is now a **two-score doc**. **RC1 product
  score 87 → 90** (RC-tag threshold; evidence-index
  consolidation lifts extension +5 / control-room
  +5 / launcher +2 / capture +2 / resume +2).
  New **Alpha evidence score: 30/100** (failure
  target met 1/1; 4 users short, 3 recoveries
  short, 1 wow short). Combination-table
  interpretation: *Product ≥ 90 + Alpha 25–50 ⇒
  RC ready, cohort recruitment is next phase*.
- **`recall alpha help`** updated to list the new
  `review` subcommand.

### Added — Phase 8D (Release Candidate · v0.1.0-rc1)
- **[`VERSION.md`](../../VERSION.md)** — v0.1.0-rc1
  spec freezing 8 surfaces (launcher · extension ·
  capture · resume · control room · doctor · demo ·
  installer); known/blocked/ship/fixed bug summary;
  P0 = 0 gate.
- **[`release/`](../../release/) kit** — 7 docs:
  [README](../../release/README.md),
  [CHANGELOG_RC1](../../release/CHANGELOG_RC1.md),
  [INSTALL](../../release/INSTALL.md),
  [QUICKSTART](../../release/QUICKSTART.md),
  [DEMO_FLOW](../../release/DEMO_FLOW.md),
  [KNOWN_ISSUES](../../release/KNOWN_ISSUES.md),
  [LANDING_CHECK](../../release/LANDING_CHECK.md).
- **`recall demo run / reset / status` CLI** —
  98-line [`app/core/demo_cli.py`](../../app/core/demo_cli.py)
  dispatched in [`recall.py`](../../recall.py).
  Seeds 30 deterministic events / 12 sessions to
  `~/.recall/events-demo/`, isolated from the real
  event log. Idempotent; `--force` to reseed.
  Documented in [`DEMO_MODE.md`](../../DEMO_MODE.md).
- **[`SCREEN_INDEX.md`](../../SCREEN_INDEX.md)** —
  frozen capture surface (4 canonical directories);
  coverage map for required RC1 surfaces (hero /
  empty / resume / capture / extension / control
  room).
- **[`INSTALL_VERIFIED.md`](../../INSTALL_VERIFIED.md)**
  — honest install walk on dev box: 5 GREEN
  doctor, 36 events today, daemon endpoints all
  200 (103 / 122 / 60 ms).
- **[`docs/engineering/PHASE_8D_STATUS.md`](../engineering/PHASE_8D_STATUS.md)**
  — capstone with 12-line verification table.

### Changed — Phase 8D
- **[`BUGS_OPEN.md`](../../BUGS_OPEN.md)** re-classified
  to RC1 gate. **P0 = 0** (down from 1 at 8C close).
  BUG-001 verified fixed; BUG-002 downgraded P0→P1
  with evidence; BUG-004 closed (not-a-bug); EXT-001
  / EXT-002 / CTRL-002 / BUG-008 reclassified
  post-beta or quarantined.
- **[`RELEASE_READINESS.md`](../../RELEASE_READINESS.md)**
  recomputed: **76 → 87 (+11)**. Pillar moves:
  perf +25, resume +15, extension +5,
  control-room +5, launcher +3, capture +2.
- **`assets/screenshots/`** frozen to 4 directories
  (`launcher-7e/`, `extension-7a/`, `alpha/`,
  `demo/`). 3 pre-7E/7A dirs + 11 root-orphan
  PNGs moved to `archive/screenshots-history-rc/`.

### Added — Phase 8C (Product Stabilization + Reality Pass)
- **Top-level [`STABILITY/`](../../STABILITY/) folder**
  with 6 reality-pass docs: `PERF.md` (real wall-clock
  timings for launcher + CLI + daemon), `CAPTURE.md`
  (30d event-store coverage by site), `LAUNCHER.md`
  (frozen 7E.1 widget tree walked offscreen),
  `RESUME.md` (recovery pipeline + bad-recovery ledger
  state), `EXTENSION.md` (9-state machine + capture
  set), `CONTROL.md` (13 admin routes + 10 loaders).
- **[`BUGS_OPEN.md`](../../BUGS_OPEN.md)** — honest
  open-bug ledger (1 P0 fixed in-flight + 1 P0 open
  + 5 P1 + 4 P2) with severity, surface, and proposed
  fix for each row.
- **[`RELEASE_READINESS.md`](../../RELEASE_READINESS.md)**
  — composite 0–100 score (currently **76**) derived
  from the six STABILITY pillars; specifies the
  follow-ups needed to reach a 92 (stable-tag) score.

### Fixed — Phase 8C
- **`app/main.py` boot regression from 8B.** The 8B
  archive of `app/core/demo_data.py` and
  `app/ui/styles.py` (+ transitive `widgets.py` +
  `cards.py`) broke `from app.main import main` —
  `demo_data` is imported by `main.py`, `styles` is
  imported by live `onboarding.py` + `settings.py`.
  Restored all four files from `archive/launcher-old/`
  and converted the `demo_data` import in `main.py`
  to a defensive lazy import inside the `DEMO_MODE`
  branch. Launcher boot path verified clean.

### Changed — Phase 8B (Tier 1 Cleanup + Repo Collapse)
- **Launcher collapsed to one tree.** 8 legacy modules
  (`launcher_legacy.py`, `cards.py`, `widgets.py`,
  `styles.py`, `launcher_anims.py`, `launcher_digest.py`,
  `demo_data.py`, `ceremonies.py`) + 3 historical
  capture scripts moved to
  [`archive/launcher-old/`](../../archive/launcher-old/).
  `app/ui/launcher.py` collapsed from 60 → 18 lines — no
  more `RECALL_LAUNCHER=legacy` branch.
- **11 historical screenshot folders archived** to
  `archive/screenshots-history/` (launcher-live,
  launcher-minimal, launcher-refined, launcher-compact,
  launcher-recovery, launcher-reset, launcher-visible,
  launcher-truth, launcher-ship, launcher-final,
  launcher-merge).
- **8 dead pre-7A extension components archived** to
  `archive/extension-pre-7a/` (ContinueCard, DebugStrip,
  DemoBanner, InvestigationCard, MemoryList, Section,
  TrustSurface, states).
- **Web manifest cleanup.** Removed 3 unused deps from
  `apps/web/package.json` (`clsx`, `lucide-react`,
  `tailwind-merge`). Moved `playwright` from
  `dependencies` → `devDependencies` in
  `apps/extension/ui/package.json`.

### Removed — Phase 8B
- 7 orphan root-level PNGs in `assets/screenshots/`
  (control-room, doctor-output, installer-flow,
  settings-dialog, launcher-first-week, launcher-loading,
  launcher-offline).
- 3 unused dep entries from `apps/web/package.json`.

### Documentation — Phase 8B
- 5 new audit docs in [`AUDIT/`](../../AUDIT/):
  [`DELETE_PLAN.md`](../../AUDIT/DELETE_PLAN.md),
  [`LAUNCHER_FREEZE.md`](../../AUDIT/LAUNCHER_FREEZE.md),
  [`DEPENDENCY_DIFF.md`](../../AUDIT/DEPENDENCY_DIFF.md),
  [`ASSET_FREEZE.md`](../../AUDIT/ASSET_FREEZE.md).
- New [`docs/engineering/PHASE_8B_STATUS.md`](../engineering/PHASE_8B_STATUS.md).
- `DOC_INDEX.md` updated with the 5 new audit + status
  doc rows.

### Verified — Phase 8B
- `python -m pyflakes app/ui app/core api` — clean.
- `python recall.py doctor` — GREEN on
  config/events/daemon/extension/installer.
- `python recall.py capture status` — 11 events today,
  12 investigations.
- Offscreen `Launcher(FakeEngine())` constructs at
  `(700, 500)`.
- TypeScript clean across all 3 frontend apps.
- `vite build` of extension — 293 KB JS bundle (identical
  to 8A, confirming dead components were already
  tree-shaken).

**Metrics**: Python LOC −24 % (29,544 → 22,435 = −7,109
lines moved to archive), asset PNGs −54 %, asset folders
−58 %, extension components −73 %, live `app/ui/` files
−55 %. No product behaviour changed.

### Added — Phase 8A (Full Product Audit)
- **New top-level [`AUDIT/`](../../AUDIT/) folder** with
  7 evidence-based audit docs:
  - [`SURFACES.md`](../../AUDIT/SURFACES.md) — every
    runtime surface with entry point + owner + status
    (36 LIVE / 2 LEGACY / 11 ARCHIVE / 1 REMOVE).
  - [`DEAD_CODE.md`](../../AUDIT/DEAD_CODE.md) — dead /
    duplicate / orphan code catalogue with file:line
    citations.
  - [`LAUNCHER_MAP.md`](../../AUDIT/LAUNCHER_MAP.md) —
    every signal, slot, public method through the
    launcher; freeze anti-rules.
  - [`CAPTURE_MAP.md`](../../AUDIT/CAPTURE_MAP.md) —
    seven-hop capture pipeline cross-checked against
    actual code + per-hop diagnostic CLI table.
  - [`ASSETS.md`](../../AUDIT/ASSETS.md) — every PNG
    under `assets/screenshots/` with ACTIVE /
    HISTORICAL / ORPHAN flags.
  - [`DEPENDENCIES.md`](../../AUDIT/DEPENDENCIES.md) —
    all 43 packages across Py + 3 JS manifests, with
    runtime / dev / unused / candidate-remove classification.
  - [`STATE.md`](../../AUDIT/STATE.md) — capstone (what
    Recall is · what ships · what's dead · what survives
    · tier-graded delete recommendations · live verify).
- **`DOC_INDEX.md`** updated with a new `/AUDIT/`
  section at the top so the audit docs are reachable
  from the standard doc index.

### Verified — Phase 8A
- `recall doctor` GREEN on config / events / event-flow /
  daemon / extension / installer (5 YELLOW = *user
  hasn't done this yet*).
- `recall capture status` clean (8 events today, 11
  investigations).
- `recall founder status` shows [GREEN] Continuity
  restored 78% / Resume sessions 41 / Investigations
  134 / Extension connected 75%.
- TypeScript clean across `apps/extension/ui`,
  `apps/admin/web`, `apps/web`.
- Offscreen `LiveLauncher(FakeEngine())` boots cleanly
  at `(700, 500)`.

**No deletions, no code changes.** This is the audit
phase, not a feature phase.

### Fixed — Phase 7E.1 (Launcher Stability)
- **Launcher no longer crashes on boot.** The 7E paint
  rewrite of `MinimalSearchBar` silently dropped two
  signals (`request_settings`, `request_close`) that
  `LiveLauncher.__init__` still wired, producing
  `AttributeError: 'MinimalSearchBar' object has no
  attribute 'request_settings'` on every `python recall.py`.
  7E.1 restores both signals as part of the frozen
  contract.

### Added — Phase 7E.1
- **`searchChanged(str)`** signal on `MinimalSearchBar`
  alongside `query_changed(str)` — both fire on every
  `QLineEdit.textChanged` via two parallel `connect`
  calls.
- **`clear()` + `selectAll()`** methods on
  `MinimalSearchBar` — part of the frozen contract.
- **Frozen `MinimalSearchBar` contract surface**: 5
  signals (`query_changed`, `searchChanged`, `submit`,
  `request_settings`, `request_close`) + 3 methods
  (`focus`, `clear`, `selectAll`). Future launcher
  phases may add to the surface; they may not remove or
  rename these symbols.

### Documentation — Phase 7E.1
- New
  [`docs/product/LAUNCHER_CONTRACTS.md`](../product/LAUNCHER_CONTRACTS.md)
  — frozen interface for `MinimalSearchBar` +
  `LiveLauncher` with wiring map and freeze rule.
- New
  [`docs/engineering/PHASE_7E.1_STATUS.md`](../engineering/PHASE_7E.1_STATUS.md).

### Changed — Phase 7E (Launcher Final Product Pass)
- **Canvas 700 × 500** (was 740 × 500), hard clamp. Warm
  `#F5F2ED` page outside, one white inner card with
  radius 24 + 20/16/20/14 padding inside. No nested
  cards, no glass, no transparency.
- **NEW Recent Memory section.** Up to 5 rows from
  `~/.recall/events/YYYY-MM-DD.jsonl` via
  `EventStore.iter_events(days=2)`. Each row: mono
  `HH:MM` + bold short source + label (elided).
  [`app/ui/launcher_v3/recent_memory.py`](../../app/ui/launcher_v3/recent_memory.py).
- **Continue hero gains HIGH/MED/LOW variants.** Left
  accent rail: filled lavender (HIGH) / soft lavender
  (MED) / outline-only (LOW). Matching confidence pill
  in the variant's tone.
- **OTHER WORK back.** 36-px rows with strength dot +
  title (elided) + last-seen mono caption right-aligned.
  1-px hairline dividers between rows.
- **TrustRow at the bottom.** 4 tiny pills:
  `LOCAL · NO CLOUD · N EVENTS TODAY · M INVESTIGATIONS`.
  Counts derived live from the same disk reads the
  Phase 7D `recall capture status` CLI uses.
- **Tagline under search.** `Recall noticed unfinished
  work` in 13-px muted lavender.

### Removed — Phase 7E
- Empty-state surface (infinity glyph + 26-pt headline +
  Show example/Start working buttons). The launcher now
  always shows *something memory-shaped*.
- Floating pills, dark overlays, prototype illustrations.

### Documentation — Phase 7E
- New
  [`docs/product/LAUNCHER_FINAL.md`](../product/LAUNCHER_FINAL.md)
  **supersedes** `LAUNCHER_VISUAL_MERGE.md` (7B.1) as
  the launcher's live contract.
- New
  [`docs/engineering/PHASE_7E_STATUS.md`](../engineering/PHASE_7E_STATUS.md).
- New
  [`archive/launcher-7b1/README.md`](../../archive/launcher-7b1/README.md)
  — what 7E archived + why.

### Added — Phase 7D (Capture Truth Audit)
- **`recall capture status` CLI** — read-only ASCII summary
  of today's capture pipeline state: events today + per-kind
  tally (7 known kinds) + returns (>= 30-min gap) +
  investigation count + last-event timestamp / kind / age.
  Daemon not required.
  [`app/core/capture_cli.py`](../../app/core/capture_cli.py).
- **`recall capture tail` CLI** — `tail -f`-style live
  inspector for `~/.recall/events/YYYY-MM-DD.jsonl`. Prints
  existing events first, then polls at 500-ms intervals;
  each new line lands as a compact `HH:MM:SS  kind  detail
  title` row. Survives midnight day-rollover + truncate.
  `--once` mode prints existing events then exits.
- **Both commands dispatch from `recall.py`'s fast path**
  before `app.main` imports — no Qt boot cost.

### Documentation — Phase 7D
- New
  [`docs/product/CAPTURE_FLOW.md`](../product/CAPTURE_FLOW.md)
  — the seven hops end-to-end (browser → extension →
  daemon → store → investigation → recovery → launcher)
  with file + function per hop + the scripted 7-step
  verification walk.
- New
  [`docs/engineering/PHASE_7D_STATUS.md`](../engineering/PHASE_7D_STATUS.md).

### Changed — Phase 7B.1 (Launcher Visual Merge)
- **Canvas 740 × 500** (was 680 × 440), hard clamp. Outer
  gutter 16 px (was 14). Single white workspace inside the
  warm `#F4F1EC` page.
- **Continue document** replaces the dense hero row. 220-px
  calm card with a soft warm-paper tint, 6-px lavender
  accent rail clipped to the rounded corners, internal
  `CONTINUE` eyebrow, 14.5-pt bold title (elided), bulleted
  body (file/tab/chat/search counts + the engine's
  *returned after Nd* clause when `preview_caption` carries
  one — pulled via a new `_extract_gap_clause` helper), and
  a right-aligned fixed-width 116-px Resume button. Reads
  as a *document with an action*, not a command-palette
  row.
- **Empty workspace.** New `_InfinityGlyph` paints a
  lavender lemniscate (two overlapping ellipses + a soft
  halo) via `QPainter` — no Unicode glyph dependency.
  20-pt bold headline *Everything you've seen, searchable.*
  + 14-px sub *Your digital continuity layer.* + two
  stacked 200-px buttons *Show example* (accent-filled) +
  *Start working* (warm-paper outline).
- **Search bar.** Warm-paper fill, hand-drawn glyph, and a
  right cluster of settings cog + close × + Ctrl K hint
  chip. Placeholder **`Start typing to recover…`**.
- **Bottom strip.** 22-px row with the trust line *End-to-end
  encrypted. Local storage only.* on the left + tiny text
  links *Privacy · Demo · Docs · Browser* on the right.
  Replaces the prior centred footer.
- **5 captures** in
  [`assets/screenshots/launcher-merge/`](../../assets/screenshots/launcher-merge/):
  `empty.png`, `active.png`, `resume.png`, `demo.png`,
  `overflow.png`.

### Removed — Phase 7B.1
- **OTHER WORK list from the launcher's visible surface.**
  `InvestigationCardV3` + `InvestigationList` reduced to
  zero-cost stubs (`HEIGHT = 0`, hidden, `populate()`
  discards inputs) so the engine path stays live but the
  launcher never renders investigations.
- **Hotkeys 2-9.** Single-focus surface — nothing to
  navigate to. Esc / Ctrl+K / Cmd+K / `1` preserved.

### Documentation — Phase 7B.1
- New
  [`docs/product/LAUNCHER_VISUAL_MERGE.md`](../product/LAUNCHER_VISUAL_MERGE.md)
  **supersedes** `LAUNCHER_SHIP_AUDIT.md` (7B) as the
  launcher's live contract.
- New
  [`docs/engineering/PHASE_7B.1_STATUS.md`](../engineering/PHASE_7B.1_STATUS.md).
- New
  [`archive/launcher-raycast/README.md`](../../archive/launcher-raycast/README.md)
  — what 7B.1 archived + why.

### Changed — Phase 7B (Launcher Production Freeze)
- **Single white root card.** The launcher now paints the
  full-bleed warm page (`#F4F1EC`) then one white root card
  with radius 22 inside a 14-px outer margin. Manual two-offset
  drop shadow replaces the prior `QGraphicsDropShadowEffect`
  so the launcher's hot path skips the software rasterise
  route.
- **Hero — no card chrome.** Only the 6-px lavender left
  accent rail (rounded ends; brighter on focus). No border,
  no shadow, no card-inside-a-card.
- **OTHER WORK — no wrapping card.** Rows paint directly on
  the root with 1-px hairline dividers between consecutive
  rows.
- **Search bar.** 52-px row with a **warm-paper fill** inside
  the root + 2-px warm-grey border + lavender focus ring +
  hand-drawn `_SearchIcon` + inline `Ctrl K` hint chip
  (auto-hidden on focus).
- **Ctrl/Cmd+K** focuses + selects-all the search input from
  anywhere inside the launcher.
- **`RECALL_DEBUG=1` timing log.** One line per
  `show_centered` written to stderr —
  `[recall.launcher.timing] show_centered  N ms  (budget 400)`
  — so the *<400 ms launcher open* budget is verifiable on
  a real machine.
- **5 captures** in
  [`assets/screenshots/launcher-ship/`](../../assets/screenshots/launcher-ship/):
  `hero.png`, `empty.png`, `focus.png`, `demo.png`,
  `overflow.png`.

### Documentation — Phase 7B
- New
  [`docs/product/LAUNCHER_SHIP_AUDIT.md`](../product/LAUNCHER_SHIP_AUDIT.md)
  **supersedes** `LAUNCHER_FINAL_AUDIT.md` (6R) as the live
  contract.
- New
  [`docs/engineering/PHASE_7B_STATUS.md`](../engineering/PHASE_7B_STATUS.md).
- New
  [`archive/launcher-final/README.md`](../../archive/launcher-final/README.md)
  — what 7B archived + why.

### Added — Phase 7A (Extension Product Surface)
- **Popup frozen at 440 × 640.** `body` sized + `overflow:
  hidden`; `#root` matched. No resize.
- **Six fixed-position regions**: Header → Continue hero →
  Active investigations → Today timeline → Activity → Trust
  strip. Header + Trust strip pinned; main column scrolls.
- **Continue hero** — full-width white card with a 6-px
  lavender accent rail, tiny `HIGH` confidence pill, title
  (one line, elided), max 3 derived chips, fixed-width
  112-px Resume button. Capped at 110 px tall.
- **Active investigations** — vertical stack of 48-px rows
  inside one white card. Strength dot + title + last-seen +
  quiet chevron. Max 4 visible without scroll.
- **Today timeline** — 3-column grid (mono time / bold
  source / label). Empty rail surfaces a painted
  illustration in place of the prior *"No browser memory
  captured yet"* prose.
- **Activity cards** — Browser (live engine) + Desktop
  (designed-now, engine-later). Each carries a one-word
  status pill (`capturing` / `idle` / `offline` / `soon`).
- **Trust strip** — single horizontal row pinned to the
  bottom with four tiny pills (`LOCAL ONLY · NO CLOUD ·
  0 UPLOADS · DAEMON OK`). Replaces the prior 140-px
  `TrustSurface` section.
- **Search overlay** on **Ctrl/Cmd+K**. Slides down with
  an inline input + groupings for *Investigations · Files
  · Returns · Events*. In-memory filter for now (UI now,
  engine later).
- **Design tokens refreshed**: page `#F5F2ED`, hairline
  `#E6DED4`, card shadow `0 12 32 rgba(0,0,0,.06)`,
  motion scale 120 / 180 / 240.
- **7 captures** in
  [`assets/screenshots/extension-7a/`](../../assets/screenshots/extension-7a/):
  `empty` · `capturing` · `active` · `resume` · `offline` ·
  `search` · `demo`.

### Documentation — Phase 7A
- New
  [`docs/product/EXTENSION_PRODUCT_AUDIT.md`](../product/EXTENSION_PRODUCT_AUDIT.md)
  — frozen-product checklist (paint table · motion table ·
  per-region contracts · 7-row state catalogue +
  capture-architecture table).
- New
  [`docs/engineering/PHASE_7A_STATUS.md`](../engineering/PHASE_7A_STATUS.md).

### Changed — Phase 6R (Launcher Finalization)
- **Window 680 × 440, hard clamp** (`setFixedSize`, min = max,
  no resize). `WA_TranslucentBackground = False` — no glass,
  no blur, no floating opacity tricks.
- **Page warmed** to `#F4F1EC` (was `#F3F1ED`). New
  `BORDER_RAISED_STRONG = #E7DED3` for the 2-px search-bar
  border. New `SHADOW_SEARCH_* = 0 8 24 rgba(0,0,0,.06)`
  scales beneath the existing `SHADOW_CARD_* = 0 12 32
  rgba(0,0,0,.08)`.
- **Search bar rewritten.** 52 px tall, radius 14, lavender
  focus ring, hand-drawn `_SearchIcon`, placeholder
  *Search work…*.
- **Hero rewritten.** Fixed 88 px height. 6-px lavender left
  accent strip + title (one line, elided) + tiny **HIGH**
  confidence pill + **fixed-width 112-px Resume button** + a
  max-3 chip row beneath the title derived from
  `suggested_targets` (`_chips_from_targets`). Removed:
  subtitle, meta caption, prose, *Why this?* link, the
  `signals` parameter, the `request_why` signal.
- **OTHER WORK rewritten** as a vertical list (was horizontal
  in 6O). 44-px rows: lavender 6-px dot + title (elided) +
  quiet painted chevron. Max 3 rows. 1-px inter-row dividers.
- **Empty surface restacked.** Lavender square · headline ·
  *Show example* · *Start working* (renamed from *Start
  normally*) — both buttons 200-px fixed width, **inside**
  the centred stack.
- **Footer.** Single-line *local only · no cloud*, ~10 px
  ink-3, centred. Present on every surface.
- **4 captures** in
  [`assets/screenshots/launcher-final/`](../../assets/screenshots/launcher-final/):
  `hero.png`, `empty.png`, `focus.png`, `overflow.png`.

### Removed — Phase 6R
- **`app/ui/launcher_v3/why_sheet.py`** (snapshotted in
  [`archive/launcher-debt/why_sheet_6q.py`](../../archive/launcher-debt/why_sheet_6q.py)).
  The engine-side signals layer
  (`recovery.explain_signals` + `recall inspect` +
  `bad_recoveries`) stays in active code; only the launcher's
  surface lost the *Why this?* overlay.
- **Live launcher's `WhyThisSheet` wiring**:
  `_recovery_to_v3` no longer passes `signals` to the hero,
  the demo path no longer synthesises signal lines, and the
  escape cascade collapses back to *preview > hide*.

### Documentation — Phase 6R
- New
  [`docs/product/LAUNCHER_FINAL_AUDIT.md`](../product/LAUNCHER_FINAL_AUDIT.md)
  — frozen-product checklist (geometry · paint · hero / OTHER
  WORK / empty / footer contracts · 7-check visibility audit
  · the freeze rule).
- New
  [`docs/engineering/PHASE_6R_STATUS.md`](../engineering/PHASE_6R_STATUS.md).
- New
  [`archive/launcher-debt/README.md`](../../archive/launcher-debt/README.md)
  — what 6R archived + why.

### Added — Phase 6Q (Continuity Truth)
- **`recall inspect <id>` CLI** — deterministic ASCII card
  (Title · Strength · Signals · Evidence · Decision) for any
  recovery candidate, thread, or title substring. Read-only;
  no daemon required.
  [`app/core/inspect_cli.py`](../../app/core/inspect_cli.py).
- **`recall trust review` CLI** — 14-day ledger summary plus
  `bad % / silence % / resume %` rates computed from
  `~/.recall/bad_recoveries.jsonl` + `~/.recall/counters.json`.
  [`app/core/trust_cli.py`](../../app/core/trust_cli.py).
- **Wrong-recovery ledger** at
  `~/.recall/bad_recoveries.jsonl` — append-only JSONL with
  four allowed reasons (`wrong_topic` · `already_done` ·
  `noise` · `duplicate`). Trust contract: no content; only
  `thread_id` + `reason` + `ts`.
  [`app/core/bad_recoveries.py`](../../app/core/bad_recoveries.py).
- **Ledger demotion** (Override 5). A candidate whose
  `thread_id` carries a recent ledger flag has
  `signals.ledger_flagged = 1.0` written by the engine; the
  launcher reads it and skips HIGH promotion. The only
  user-feedback input into ranking.
- **`recovery.explain_signals(candidate)`** — deterministic
  pure helper that returns short observational lines
  ("unfinished work", "returned after a multi-day gap",
  "N targets involved", …) for the *Why this?* sheet and the
  inspector. No prose, no AI, no scoring numbers.
- **`Why this?` sheet on the hero card.** A small lavender
  link on the right of the meta row opens a centred overlay
  listing the engine's signals verbatim. Esc / Close to
  dismiss.
  [`app/ui/launcher_v3/why_sheet.py`](../../app/ui/launcher_v3/why_sheet.py).
- **4 captures** in
  [`assets/screenshots/launcher-truth/`](../../assets/screenshots/launcher-truth/):
  `hero_with_why.png`, `why_sheet.png`, `showcase.png`,
  `ledger_demoted.png`.

### Documentation — Phase 6Q
- New
  [`INVESTIGATION_PRINCIPLES.md`](../product/INVESTIGATION_PRINCIPLES.md) —
  the 7 rules + the 9 trust-floor gate table.
- New
  [`PROMOTION_THRESHOLDS.md`](../product/PROMOTION_THRESHOLDS.md) —
  the LOW/MED/HIGH bands + 5 overrides + 4 worked examples.
- New
  [`SHOWCASE_TRUTH.md`](../product/SHOWCASE_TRUTH.md) —
  three-investigation scripted walk verifying *only one
  hero* + the *Why this?* contract + the ledger-demotion path
  + a 6-row failure-mode table.
- New
  [`PHASE_6Q_STATUS.md`](../engineering/PHASE_6Q_STATUS.md).
- New
  [`archive/recovery-ranking/README.md`](../../archive/recovery-ranking/README.md) —
  what 6Q kept, what 6Q added, what 6Q considered and
  rejected.

### Changed — Phase 6P.1 (Launcher Visibility Recovery)
- **Warmer page colour.** `theme.BG` drops from `#F7F5F2` →
  `#F3F1ED` (6% darker). White cards on the new page register
  as distinct surfaces at arm's length; previously they
  blended into the page.
- **Layered cards everywhere.** New `_LayeredCard` base class
  (white fill + 1-px warm-grey border + soft drop shadow,
  `0 12 32 rgba(0,0,0,.08)`) inherited by the search bar,
  recovery hero, and a new `_InvestigationsCard` wrapper around
  the OTHER WORK row.
- **Search bar gains chrome.** Hand-drawn `_SearchIcon`
  (`QPainter` circle + handle — no Unicode glyph dependency) +
  lavender focus ring (2-px `T.ACCENT` border on `FocusIn`).
  Inactive cards paint at ~0.96 alpha so the focused card is
  always the foreground.
- **Hero card.** White fill (was accent-tinted) + a soft
  **4-px lavender left accent strip** painted inside the
  rounded border + a **fixed-width 110-px Resume button**
  (`_ResumeButton.WIDTH`) so the right edge is stable across
  recoveries.
- **Empty state.** Stacked layout: lavender logo dot →
  headline → sub → buttons row, 16-px gap, two 140-px
  fixed-width buttons (primary accent-filled, secondary
  layered card).
- **Window frame.** `MinimalWindow` reserves a 12-px outer
  margin and paints a 1-px warm-grey border at radius 24 — the
  launcher reads as a discrete object now, not a patch of
  paint over the desktop.
- **`BORDER_RAISED` token.** Solid `#E4DED6` warm-grey
  replaces rgba hairlines on raised surfaces (the rgba reads
  as muddy ink against white).
- **4 captures** in
  [`assets/screenshots/launcher-visible/`](../../assets/screenshots/launcher-visible/):
  `hero.png`, `empty.png`, `focus.png`, `investigations.png`.

### Documentation — Phase 6P.1
- New
  [`docs/product/LAUNCHER_VISIBILITY.md`](../product/LAUNCHER_VISIBILITY.md)
  — *problem · fix · before / after* audit with a 9-row
  comparison table.

### Added — Phase 6P (Resume Reality)
- **The Resume button actually works.** Click *Resume* on the
  recovery hero → a small preview overlay appears inside the
  launcher window → click *Resume now* → the OS opens 5 targets
  in the documented order → a 3-second toast names 3 of them
  → the launcher hides. The pre-6P stub resolved the API plan
  and threw it away; the new path walks it.
- **New `ResumePreview` overlay** in
  [`app/ui/launcher_v3/resume_preview.py`](../../app/ui/launcher_v3/resume_preview.py).
  Floats on top of the digest; lists *Will reopen · N files ·
  N tabs · N searches* derived locally from the candidate's
  `suggested_targets` (no second source of truth); Cancel +
  Resume now buttons; Esc cancels.
- **New `RestoreToast` widget** in
  [`app/ui/launcher_v3/restore_toast.py`](../../app/ui/launcher_v3/restore_toast.py).
  3-second pill at the bottom of the launcher. Shows up to
  three target names on success
  (*Restored · backoff.py · client.py · MDN*) or a calm
  failure line (*Could not reopen 1 item · Continue anyway*,
  *Could not reach the engine · try again*).
- **`LiveLauncher._on_preview_accept` walks the plan.** Calls
  `APIClient.recovery_restore`, then opens each step via
  `_open_target` in the engine's prescribed order: **files →
  chats → tabs → searches**. Windows uses `os.startfile`,
  macOS uses `open`, Linux uses `xdg-open`.

### Fixed — Phase 6P
- **Missing files no longer hang the chain.** Each file path is
  existence-checked before logging an `open` event; failures
  are counted as `skipped` and the remaining targets still
  open. The toast reports the partial restore (*Restored 3 of
  5 · … · 2 missing*); the launcher never crashes.
- **Daemon-down state has copy.** When the engine is
  unreachable, the toast reads *Could not reach the engine ·
  try again* instead of silently closing the launcher.
- **Demo recovery now reads identically to a live restore.**
  Demo path runs through the same `ResumePreview` → toast
  cycle; previously demo's `Resume` was a no-op dismiss with
  no visible feedback.

### Removed — Phase 6P
- **`LiveLauncher._on_restore` stub.** Replaced by
  `_on_preview_accept` (real OS opens). Documented in
  [`archive/resume-old/README.md`](../../archive/resume-old/README.md).
- **`LiveLauncher._on_demo_resume` no-op.** Folded into the
  unified preview-accept path so the demo runs the same
  pipeline as a live restore.

### Documentation — Phase 6P
- New [`docs/product/RESUME_FLOW.md`](../product/RESUME_FLOW.md) —
  end-to-end pipeline audit + *why files first / why chats
  second* rationale + failure-mode table.
- New [`docs/product/SHOWCASE_RUN.md`](../product/SHOWCASE_RUN.md) —
  scripted WebSocket demo run + failure-injection matrix.
- New [`docs/engineering/PHASE_6P_STATUS.md`](../engineering/PHASE_6P_STATUS.md).

### Changed — Phase 6O (Launcher Reset)
- **Launcher window 680 × 460.** `MinimalWindow.DEFAULT_SIZE` +
  `LiveLauncher.DEFAULT_SIZE` = `(680, 460)` (was 720 × 520
  in 6M.2). Paper-white background, outer radius 24, soft drop
  shadow.
- **Surface stripped to one column.** Search at top (capped
  620 px, centred) + CONTINUE section + 100-px **fixed** hero
  + OTHER WORK section + up to **3** bare-text investigation
  titles. Or, when no HIGH recovery, a centred empty surface
  (*Recall notices unfinished work* + *Work normally. / Return
  later.* + *Show example* / *Start normally* buttons).
- **`RecoveryCardV3` rewritten** in
  [`recovery_panel.py`](../../app/ui/launcher_v3/recovery_panel.py).
  Single fixed-100-px hero. Title left + ambient meta text
  beneath + `_ResumeButton` (accent-filled, `1` shortcut chip)
  right. **No** `signal` param. **No** `confidence` badge. **No**
  `sentence` row. **No** evidence chip parser. New
  `_EliderLabel` helper paints `…` when the title can't fit
  the constrained column (long titles like *"WebSocket retry
  debugging"* now degrade gracefully).
- **`InvestigationCardV3` rewritten** as a bare `QLabel`.
  No border, no background, no status dot, no surface chip,
  no shadow. New `InvestigationRow` caps at 3 equal-width
  titles; no overflow chip, no scroll, no animations.
- **`minimal.py` rewritten.** Five public classes:
  `MinimalSearchBar` (44-tall, radius 14, centred, capped
  620), `MinimalDigest` (search → hero → row), `MinimalEmpty`
  (centred headline + body + two buttons — no icon, no
  preview card), `MinimalShell` (24-px outer padding, 16-px
  gap between search and body), `MinimalWindow` (680 × 460
  fixed default).
- **`LiveLauncher` HIGH-only gate.**
  [`live.py:_populate_digest`](../../app/ui/launcher_v3/live.py)
  reads `recovery_recent(n=1)` + `threads_recent(n=3)`. The
  hero is constructed **only** when `len(suggested_targets) >= 4`
  (the HIGH bar); otherwise no hero. If neither hero nor
  investigations land → `_show_empty()`. `_recovery_to_v3`
  simplified to four lines; `_thread_to_v3` returns a bare
  `InvestigationCardV3(id, topic, title)`.
- **Deleted from the runtime surface.** Returns row · trust
  line · MED/LOW signal variants on the hero · confidence
  sentences · `_ResumePill(kind="continue"|"review")` ·
  preview card on the empty surface · status dots on
  investigation pills · evidence chip parser + `_chip_for`
  helper · `_OverflowChip` (`+N more`) · `sort_for_digest`
  4-tier priority sorter · per-card footers.
- **Six files moved to
  [`archive/launcher-overbuild/`](../../archive/launcher-overbuild/)**
  with a per-file README documenting *what surface it carried*
  + *why the reset removed it*:
  - the prior `minimal.py`
  - the prior `recovery_panel.py`
  - the prior `investigation_panel.py`
  - `digest.py` (legacy 6I composition; no longer importable
    because its dependencies were removed in the same reset)
  - `capture_launcher_compact.py` (6M.2)
  - `capture_launcher_recovery.py` (6N)
- **New capture pipeline** at
  [`infra/scripts/capture/capture_launcher_reset.py`](../../infra/scripts/capture/capture_launcher_reset.py)
  produces 2 PNGs in `assets/screenshots/launcher-reset/`:
  `populated` (search + hero + 3 titles) and `empty` (centred
  empty surface).
- **`docs/product/LAUNCHER_RESET.md`** — the directive's
  audit: *what we removed · why the launcher failed · the
  new philosophy*. Three failure modes + three design rules
  (*one surface · HIGH or nothing · add nothing the user
  doesn't act on*).
- **`docs/engineering/PHASE_6O_STATUS.md`** — receipt.
- **No engine work.** No `app/core/`, `api/`, `apps/extension/`,
  `apps/admin/`, or `apps/web/` files touched. The
  `RECALL_LAUNCHER=legacy` escape hatch (Phase 6K) is
  preserved.

### Added — Phase 6N (Recovery Precision)
- **3-state recovery hero.** `RecoveryCardV3` gains a `signal`
  parameter (HIGH / MED / LOW); card fill, border, CTA pill,
  and confidence sentence all derive from it. HIGH →
  accent-filled *Resume* pill + *"Recall thinks this was
  interrupted work"*. MED → accent-soft *Continue* pill +
  halfway-tinted fill + *"Seen again after return"*. LOW →
  ghost *Review* pill + plain white fill + *"Weak signal —
  review first"*.
- **`_ResumePill` three variants** (`kind="resume"|"continue"|"review"`).
- **Optional engine-provided sentence** via a new `sentence`
  constructor arg; `DEFAULT_SENTENCES[signal]` provides the
  fallback. LiveLauncher passes
  `getattr(c, "why_summary", None)` so a future engine field
  lands without further widget edits.
- **Evidence chips capped at 3** (`parse_evidence_chips(...)[:3]`);
  the parser is unchanged and never fabricates.
- **`sort_for_digest()`** pure helper in
  [`investigation_panel.py`](../../app/ui/launcher_v3/investigation_panel.py)
  — orders investigations by *unfinished → returned → recent →
  passive*, with high-strength threads winning within each
  rank. Wired into `LiveLauncher._populate_digest`.
- **`MinimalEmpty` preview card.** New `_build_preview_card`
  renders a non-interactive LOW-state `RecoveryCardV3` with
  the canonical WebSocket fixture. *PREVIEW* mono caption
  above; sentence row reads *"A real recovery will replace
  this"*. Auto-dismiss is upstream — `MinimalEmpty` only
  renders when the engine has zero recoveries.
- **Five new captures** at
  [`assets/screenshots/launcher-recovery/`](../../assets/screenshots/launcher-recovery/)
  via
  [`capture_launcher_recovery.py`](../../infra/scripts/capture/capture_launcher_recovery.py):
  `high` · `medium` · `low` · `empty` · `resume`.
- **`docs/product/RECOVERY_VISUAL_AUDIT.md`** — directive's
  *high / medium / low trust + silence + bad recovery* audit
  + cross-cutting rules table.
- **`docs/engineering/PHASE_6N_STATUS.md`** — receipt.

### Changed — Phase 6M.2 (Launcher Geometry Recovery)
- **Launcher window shrinks to a Raycast / Arc shape.**
  `LiveLauncher.DEFAULT_SIZE` + `MinimalWindow.DEFAULT_SIZE`
  = **720 × 520** (was 820 × 640). New `MinimalWindow.MAX_SIZE`
  = (760, 560). Inner column `MinimalShell.MAX_WIDTH = 640`
  (was 760); `MIN_WIDTH = 520` (was 600). Outer window radius
  **24** (was 28). The 6M.1 launcher had drifted toward a
  dashboard shape — the 6M.2 recovery restores the utility
  proportions without rewriting the theme.
- **Search bar capped + centred.**
  [`MinimalSearchBar`](../../app/ui/launcher_v3/minimal.py) now
  `setMaximumWidth(640)` inside a centring
  `addStretch / widget / addStretch` row (was full-width).
  Height 48 (was 40); border-radius 16 (was 12); placeholder
  **"Search investigations…"**; `setMinimumWidth(360)` so the
  centering stretches don't squeeze the placeholder.
- **Hero card 92 px, 2×2 grid.**
  [`RecoveryCardV3.HEIGHT = 92`](../../app/ui/launcher_v3/recovery_panel.py)
  (was 124) with a `MAX_HEIGHT = HEIGHT + 24 = 116` cap to
  prevent dashboard sprawl. Layout reshaped from
  `vertical-stack-with-stretch` into a **2×2 grid** —
  title TL · confidence TR · chips BL · Resume BR. Eyebrow row
  (accent dot + *CONTINUE* label) **removed** — duplicate of
  the chip strip + confidence badge. `_ResumePill` height bumped
  from 34 → **36** (the directive's exact value).
- **Investigations capped at 3** (was 4) with the existing
  `+N more` dashed overflow chip. Pill height **44** (was 40);
  pill paint radius **14** (was 20); title font sized to
  `T.FS_TITLE - 1` so it fits the recovered typography scale.
- **Returns strip quieter.** `MinimalReturns.MAX_ROWS = 2`
  (was 3). Section eyebrow (*"RECENT RETURNS"*) **removed**;
  replaced with a 1-px `T.HAIRLINE` `QFrame` above the rows.
  Per-row layout shrinks: 22 px tall (was 28), no leading dot,
  9.5-pt mono when-label, 11-pt INK_3 body. `setVisible(False)`
  by default; `populate()` flips visibility based on `items`
  length.
- **Digest vertical rhythm explicit.**
  [`MinimalDigest`](../../app/ui/launcher_v3/minimal.py)
  layout `setSpacing(0)` + explicit `addSpacing(T.SECTION_GAP)`
  / `addSpacing(T.CARD_GAP)` / `addSpacing(T.RETURNS_GAP)` so
  the directive's non-uniform `16/12/8` rhythm lands precisely
  between hero → investigations → returns → trust.
- **Theme token retune** in
  [`theme.py`](../../app/ui/launcher_v3/theme.py) — no palette
  change, no shadow change, no radius change; only spacing +
  typography. `GUTTER 28→20` · `SECTION_GAP 20→16` · new
  `RETURNS_GAP=8` · `FS_HERO 22→20` · `FS_TITLE 16→14` ·
  `FS_BODY 14→13` · `FS_LABEL 11→10` · `FS_META 12→11` ·
  `FS_SECTION 14→13` · new `FS_CONFIDENCE=10`.
- **Four new captures** in
  [`assets/screenshots/launcher-compact/`](../../assets/screenshots/launcher-compact/)
  via the new
  [`capture_launcher_compact.py`](../../infra/scripts/capture/capture_launcher_compact.py):
  `compact` (everything together), `hero` (focused alone with
  one investigation pill), `investigations` (4 threads → 3
  pills + `+1 more` overflow), `empty`. The Phase 6M.1
  captures at `assets/screenshots/launcher-refined/` stay
  on disk as the *before* set the regression doc references.
- **`docs/product/LAUNCHER_REGRESSION.md`** — the directive's
  audit: *why old looked better*, *what 6M.1 changed*, *what
  6M.2 fixed*. 13-token comparison table + a narrative on the
  *Raycast ↔ Notion* axis.
- **`docs/engineering/PHASE_6M.2_STATUS.md`** — the receipt.
- **Numbering**: this directive arrived labelled *Phase 6M.1*
  (the third 6M-prefix directive this session). The prior
  Phase 6M.1 (Launcher Refinement) already shipped with its
  own
  [`PHASE_6M.1_STATUS.md`](../engineering/PHASE_6M.1_STATUS.md).
  This receipt files as **6M.2** so both the *refinement* and
  the *recovery* audit trails survive on disk.

### Changed — Phase 6M.1 (Launcher Refinement)
- **Theme tokens refit** in
  [`app/ui/launcher_v3/theme.py`](../../app/ui/launcher_v3/theme.py)
  to the directive's exact values: paper-white `#F7F5F2`,
  every surface alpha → **255** (solid), shadow `0 8 24`
  (`SHADOW_SOFT_OFFSET = 8`), card radius **20**, spacing
  **28 / 20 / 12** (`GUTTER` / `SECTION_GAP` / `CARD_GAP`),
  typography **22 / 14 / 12** (`FS_HERO` / `FS_SECTION` /
  `FS_META`). New `FS_SECTION = 14` token.
- **`GlassCard` paint flipped to solid** in
  [`surfaces.py`](../../app/ui/launcher_v3/surfaces.py). The
  `alpha` constructor arg is silently clamped to 255 — the
  directive forbids transparency outright. The class name is
  preserved as a backwards-compat shim; every downstream
  importer keeps working.
- **`RecoveryCardV3` hero refit** in
  [`recovery_panel.py`](../../app/ui/launcher_v3/recovery_panel.py).
  Action row bottom-aligned (stretch added above the chip strip
  + Resume pill). The *Surfaced because you left this mid-flow.*
  footer line was deleted — the chip strip + confidence badge
  already say it. Accent fill is now solid (alpha=255).
- **Investigation strip — equal-width pills + overflow chip**
  in [`minimal.py`](../../app/ui/launcher_v3/minimal.py).
  Pills now stretch (`addWidget(pill, 1)`) to share the
  strip's width equally; a new `_OverflowChip` widget renders
  a dashed-border `+N more` pill when there are more than 4
  threads — the directive's *no scrolling, no walls* rule.
  Pill height bumped to 40 (was 36) so its bottom edge aligns
  with the hero card.
- **`MinimalEmpty` rewritten** without the wrapping
  `GlassCard`. Surface is now: a 48×48 accent-tinted square
  with a small painted lavender dot (no Unicode glyph —
  cross-system font portability), the headline
  *Recall notices unfinished work.* at 22 px, the body
  *Work normally. Return later. Recall fills itself.* at
  14 px, two buttons (Show example / Start normally) at
  38 px tall with radius 12, and the trust line. Vertically
  centred on the paper-white page.
- **Shell geometry tightened.** `MinimalShell.MAX_WIDTH = 760`
  (was 860 — directive: *max width 760*). `MIN_WIDTH = 600`
  (was 760) so the column breathes on smaller windows.
  `MinimalWindow.DEFAULT_SIZE` + `LiveLauncher.DEFAULT_SIZE`
  = **820 × 640** (was 920 × 720). Outer padding =
  `T.GUTTER = 28`.
- **Three legacy capture scripts archived** to
  [`archive/launcher-refine/`](../../archive/launcher-refine/):
  `capture_launcher_v3.py` (6I 3-column gallery),
  `capture_launcher_live.py` (6K live composition),
  `capture_launcher_minimal.py` (6L pre-refinement minimal).
  Their fixture data references layout values the refined
  launcher no longer matches. The screenshots themselves
  stay on disk as historical reference.
- **New capture pipeline** at
  [`infra/scripts/capture/capture_launcher_refined.py`](../../infra/scripts/capture/capture_launcher_refined.py)
  produces 5 PNGs in `assets/screenshots/launcher-refined/`:
  `hero` (single column · hero + 4 equal-width pills + trust
  line), `empty` (centred icon + headline + sub + 2 buttons),
  `investigations` (6 threads → 4 pills + `+2 more` overflow
  chip), `resume` (focused hero with accent ring), `focused`
  (focused hero + populated pill row).
- **New audit doc** at
  [`docs/product/LAUNCHER_REVIEW.md`](../product/LAUNCHER_REVIEW.md)
  carries the directive's *removed · kept · why · future*
  table.
- **Numbering**: this directive arrived labelled *Phase 6M*
  but Phase 6M (Desktop Memory Layer) already shipped this
  session with its own
  [`PHASE_6M_STATUS.md`](../engineering/PHASE_6M_STATUS.md).
  This receipt files as **6M.1** so the Desktop Memory Layer
  history is preserved.

### Added — Phase 6M (Desktop Memory Layer)
- **New `app/core/desktop/` package** — six modules capturing
  foreground-window focus events: `events.py` (the
  `desktop_window` kind + `DesktopWindowEvent` dataclass),
  `processes.py` (PID → exe-name resolver via
  `OpenProcess` + `QueryFullProcessImageNameW`; pure ctypes,
  no `psutil`), `windows.py` (`probe_foreground()` via
  `GetForegroundWindow` + `GetWindowTextW`), `sessions.py`
  (`FocusAggregator` with **30 s** minimum focus + **60 s**
  re-focus consolidation + EXE blocklist), `watcher.py`
  (daemon-thread polling loop + `start_watcher()` /
  `stop_watcher()` helpers).
- **Metadata only.** No screenshots, no OCR, no audio, no
  pixel data. The watcher reads only what the OS already
  exposes via window title + process API; the schema's
  whitelist enforces the contract at the HTTP boundary.
- **`POST /v1/events/desktop`** route in `api/main.py` +
  `DesktopWindowIn` schema in `api/schemas.py`. `ALLOWED_KINDS`
  in `app/core/ingest.py` gains `desktop_window`. The route
  triggers the same `_post_ingest_hook(ok)` other ingest paths
  do.
- **Control room `/desktop` route** —
  [`apps/admin/web/app/desktop/page.tsx`](../../apps/admin/web/app/desktop/page.tsx)
  + new `desktop.ts` loader. Reads
  `~/.recall/events/*.jsonl` directly, filters for
  `kind === "desktop_window"`, aggregates per app. Surfaces
  *apps · focus · top tools · session log* + a *Privacy*
  card. Nav row + Ctrl+K palette entry added.
- **Extension popup desktop badge** — small accent `⊞-N`
  badge next to the *N today* caption. Reads
  `health.desktop_apps_today` from `/v1/health`; pre-6M
  daemons silently report 0 → no badge. `Health.desktopApps?: number`
  on the popup type.
- **Disabled by default.** Watcher refuses to start on
  non-Windows hosts; `RECALL_DESKTOP=off` is the kill switch;
  the `desktop_capture_enabled` field in
  `~/.recall/config.json` is the explicit opt-in.
- **Purely additive layer.** Deleting `app/core/desktop/`
  removes the watcher without breaking any downstream
  artifact — the CLAUDE.md rule for new layers held.
- **`docs/product/DESKTOP_LAYER.md`** — the product story.
- **`docs/engineering/PHASE_6M_STATUS.md`** — the receipt.

### Added — Phase 6L (Launcher Simplification)
- **The launcher is now a single floating surface.** The
  three-column shell (sidebar + centre + context column) the
  v3 launcher inherited from Phase 6I moved to
  [`archive/launcher-v2/`](../../archive/launcher-v2/). The
  directive: no admin panel, no control room, no analytics
  view. System info lives **only** in the founder control
  room (`apps/admin/web/`).
- **New** [`app/ui/launcher_v3/minimal.py`](../../app/ui/launcher_v3/minimal.py)
  — 8 classes: `MinimalSearchBar` (one rounded input, no nav),
  `MinimalInvestigations` (horizontal pill flow, max 4
  visible, never scrolls), `MinimalReturns` (thin 3-row
  strip, hidden on empty), `MinimalTrust` (one quiet
  *local only · 127.0.0.1:4545 · no cloud* line),
  `MinimalEmpty` (single `GlassCard` with the directive's
  exact copy + Show example / Start normally + trust line),
  `MinimalDigest` (composes hero + investigations + returns +
  trust), `MinimalShell` (width clamped **760-860 px**, outer
  gutter 32, section gap 24), `MinimalWindow` (top-level
  `QWidget`, **920 × 720** default).
- **`LiveLauncher` rewired** in
  [`live.py`](../../app/ui/launcher_v3/live.py) to compose
  `MinimalShell` instead of the 3-column Shell. Reads **one**
  recovery card for the hero (was three vertical cards).
  Investigations stay capped at 4 but render as a horizontal
  pill strip, not a vertical list. New `_build_returns()`
  reads `daily_loop.summary(days=3)` best-effort and surfaces
  today / yesterday return rows — counts only, per the Phase
  6F trust contract. `_refresh_context()` deleted (no context
  column to refresh).
- **Archived widgets** moved to
  [`archive/launcher-v2/`](../../archive/launcher-v2/):
  `shell.py` (Shell + ContextColumn), `sidebar.py` (rich left
  rail with nav), `window.py` (LauncherWindow that hosted the
  Shell). A README documents *why removed* per class. Nothing
  in `app/`, `infra/`, or `apps/` imports from the archive —
  reference, not a code path, not a feature-flag fallback.
- **4 new captures** in
  [`assets/screenshots/launcher-minimal/`](../../assets/screenshots/launcher-minimal/):
  `hero.png` (single column · Continue hero + 4 pills + 3
  returns), `empty.png` (first-run empty surface),
  `investigations.png` (populated with a lower-confidence
  hero so the strip carries the read), `resume.png` (focus
  state). Pipeline at
  [`capture_launcher_minimal.py`](../../infra/scripts/capture/capture_launcher_minimal.py).
- **Visual rules respected**: card radius 24, soft shadow
  only, no `setFixedHeight` anywhere. The directive's
  *more air* + *content-driven sizing* rules.
- **Motion vocabulary preserved**: fade / lift / expand;
  `OutCubic` easing; 120 / 180 / 260 ms. No bounce / spring /
  overshoot.
- **Default import unchanged.**
  `from app.ui.launcher import Launcher` still returns
  `LiveLauncher`; the Phase 6K `RECALL_LAUNCHER=legacy`
  escape hatch is preserved.

### Added — Phase 6K (Launcher Promotion)
- **`from app.ui.launcher import Launcher` now returns the v3
  `LiveLauncher`** by default. The previous 1130-line
  `app/ui/launcher.py` (the v2 widget tree) moved to
  [`app/ui/launcher_legacy.py`](../../app/ui/launcher_legacy.py),
  reachable via `RECALL_LAUNCHER=legacy` — the *promote safely*
  escape hatch.
- **New 38-line adapter** at
  [`app/ui/launcher.py`](../../app/ui/launcher.py) that resolves
  the `Launcher` symbol at import time: default → v3
  LiveLauncher, `RECALL_LAUNCHER=legacy` → the legacy class.
  Backwards-compat constants (`LAUNCHER_WIDTH`, `SHADOW_MARGIN`,
  `FOOTER_H`) re-exported from the legacy module so
  `launcher_anims.py` and `launcher_digest.py` keep working
  unchanged.
- **`LiveLauncher` class** at
  [`app/ui/launcher_v3/live.py`](../../app/ui/launcher_v3/live.py)
  — carries the legacy constructor signature
  (`search_engine, event_logger=None`), legacy signals
  (`request_settings`, `_request_search`), and legacy public
  API (`show_centered()`, `invalidate_digest()`,
  `_refresh_idle_state()`) so `app/main.py:416` constructs it
  unchanged. Composes the v3 Shell (Sidebar + ContextColumn)
  with a `QStackedLayout` centre that swaps between
  `EmptyDigest` (first-run surface with Show example / Start
  normally) and `DigestColumn` (RecoveryPanel +
  InvestigationPanel + TrustPanel).
- **Live data hooks.** `_populate_digest()` reads
  `api_client.recovery_recent(n=3)` + `threads_recent(n=6)`;
  `_refresh_context()` reads `api_client.health()` and rebuilds
  the right-column with the live events-today count. The
  `_recovery_to_v3()` / `_thread_to_v3()` translators map DTOs
  onto v3 widget arguments. Confidence derivation mirrors v2 +
  extension popup: `n_targets ≥ 4 → high · 2-3 → medium · 0-1 →
  low`.
- **Demo overlay honoured.** When `demo_mode.is_active()` and
  the engine is otherwise empty, `_populate_demo()` reads
  `demo_mode.demo_payload()` and renders the canonical
  WebSocket / Healthcare-pitch / RLHF investigations. The Phase
  6D auto-dismiss hook still applies — a real ingest flips the
  state file and the next `_refresh_idle_state()` falls
  through to the live engine.
- **Keyboard layer.** `Esc` hides the launcher. `1-9` focuses
  the n-th card across the recovery + investigation panels
  combined. `Enter` / `Space` activation + focus-ring rendering
  shipped with the Phase 6I cards.
- **Capture pipeline** at
  [`infra/scripts/capture/capture_launcher_live.py`](../../infra/scripts/capture/capture_launcher_live.py)
  produces 6 PNGs in `assets/screenshots/launcher-live/`:
  `overview` (full 3-column shell, populated digest),
  `continue` (recovery hero in isolation), `empty` (first-run
  empty), `trust` (footer in isolation), `focus` (recovery
  card with `_focused=True`), `recovery` (one recovery + one
  investigation — the cohort-facing shape).
- **`docs/engineering/PHASE_6K_STATUS.md`** — the engineering
  receipt + verification matrix.
- **No engine, no recovery-logic change.** The legacy widget
  tree is *archived in place*, not deleted; the directive's
  *promote safely* clause remains the binding constraint. A
  clean deletion can land in a follow-up after one cohort
  week confirms zero v3 regressions.

### Added — Phase 6J (Control Room V2)
- **Global chrome.** New sticky top bar
  ([`TopBar.tsx`](../../apps/admin/web/components/TopBar.tsx)) +
  bottom bar
  ([`BottomBar.tsx`](../../apps/admin/web/components/BottomBar.tsx))
  in [`layout.tsx`](../../apps/admin/web/app/layout.tsx). Top
  bar carries Recall wordmark + three live pills
  (daemon · readiness · installs) + the `⌘K` palette trigger;
  bottom bar carries the version + doctor verdict pill +
  build label. Both bars derive every value from the live
  loaders the inner pages already use.
- **Command palette.**
  [`CommandPalette.tsx`](../../apps/admin/web/components/CommandPalette.tsx)
  — `⌘K` / Ctrl-K opens, Esc closes, ↑↓ navigates, Enter
  selects. Fuzzy search over 14 routes + 9 directive-named
  actions (Run doctor / Bake data / Generate alpha report /
  Export trust / Open screenshots / Open alpha folder / Open
  recovery journal / Open daily loop / Open logs). Selecting
  a route navigates; selecting an action copies the canonical
  CLI command to the clipboard. **No server endpoint executes
  anything** — same contract as the actions sidebar.
- **Two new loaders.**
  [`logs.ts`](../../apps/admin/web/lib/loaders/logs.ts) reads
  5 canonical sources (doctor / recovery / daily / alpha /
  release) with per-source verdicts;
  [`screenshots.ts`](../../apps/admin/web/lib/loaders/screenshots.ts)
  scans 6 buckets (launcher-v2 / launcher-v3 / extension-v2 /
  demo / alpha / legacy flat) with per-bucket
  **missing-marker** detection — every directive-named PNG is
  named, and the bucket's verdict turns red the moment one is
  absent.
- **Left nav rebuilt** to the directive's 12-section order
  (4 groups: overview · cohort · engine · ship · lab) with
  hotkeys 1-9 + 0 on the first ten rows. Experiments + Docs
  reachable via the palette.
- **Five new routes.** `/extension` (popup pairing health · ext
  & engine version drift · capture rate · popup screenshots ·
  clipboard repair commands), `/launcher` (v3 gallery + v3↔v2
  side-by-side diff strip + 6-row promotion checklist
  surfacing Phase 6I's deferred wire-in), `/experiments` (8
  feature flags read live from `~/.recall/config.json` +
  `~/.recall/demo.json` + env, each with live value + flip
  command + verdict; 4 alpha-gate cards; 3 GREEN-floor
  threshold cards), `/logs?source=<id>&q=<query>` (5-source
  picker + filtered substring viewer + clipboard download),
  `/screenshots` (per-bucket gallery + per-bucket verdict +
  missing-marker strip).
- **Recovery Lab extended.**
  [`/recovery`](../../apps/admin/web/app/recovery/page.tsx)
  gained a kind filter chip strip (all + 6 directive kinds),
  a confidence distribution block (high / medium / low
  derived from per-tester `first_resume_ok`), and a 7-day
  return-after-gap heatmap counted from
  `recovery_journal.json` entries with
  `return_after_gap = true`.
- **System Console — Copy diagnostics.**
  [`/system`](../../apps/admin/web/app/system/page.tsx) renders
  a pre-built markdown blob (handles + mtimes + verdicts;
  **no PII, no URLs, no filenames** — the trust-ledger
  contract restated) and a
  [`CopyDiagnostics`](../../apps/admin/web/components/CopyDiagnostics.tsx)
  client button that puts the blob on the clipboard. A
  live-refresh button next to it re-runs the server fetch.
- **Public screenshot assets.**
  `apps/admin/web/public/screens/` populated with 5 mirrored
  bucket directories so every gallery on
  `/extension` / `/launcher` / `/screenshots` renders real
  thumbnails through Next's static asset pipeline.
- **`docs/founder/CONTROL_ROOM_V2.md`** — the user manual the
  founder reads. Pairs with the receipt at
  [`docs/engineering/PHASE_6J_STATUS.md`](../engineering/PHASE_6J_STATUS.md).
- **No engine, no Python, no marketing-site, no extension
  touches.** Admin Next.js build clean: 14 routes, all
  `ƒ` server-rendered, 87.4 KB first-load shared.

### Added — Phase 6I (Launcher Rebuild)
- **New parallel package** at
  [`app/ui/launcher_v3/`](../../app/ui/launcher_v3/) — 12 modules
  delivering the directive's premium-surface system. The live
  `app/ui/launcher.py` is **untouched**; the v3 package sits
  alongside, ready for promotion on a follow-up phase with its
  own QA matrix.
- **`theme.py`** — colour tokens (`BG = #F7F5F2` warm white,
  `BG_RAISED = #FFFFFF`, `ACCENT = #8B7FE3` lavender, three
  surface alphas at 184/220/240) + radius scale (pill 12, card
  20, panel 24, hero 28) + soft-only shadow scale + spacing
  rhythm + typography sizes. Pure constants — no Qt import.
- **`motion.py`** — the directive's timings (`FAST_MS = 120`,
  `NORMAL_MS = 180`, `SLOW_MS = 260`) + `OutCubic` easing +
  `fade()` / `slide_y()` / `expand()` helper factories. No
  bounce, no spring, no overshoot.
- **`surfaces.py`** — seven primitives the directive named:
  `GlassCard`, `FloatingPanel`, `SoftDivider`, `Pill` (accent /
  mute / count), `ConfidenceBadge` (high / medium / low), `TimelineChip`
  (mono-font HH:MM or "2d gap"), `StatusDot` (accent / ok /
  warn / danger / mute) + a `section_label()` helper.
- **`recovery_panel.py`** — `RecoveryCardV3` (124-px hero with
  chip row, ConfidenceBadge, accent Resume pill carrying the
  `1` shortcut chip, hover lift, focus ring, Enter/Space/`1`
  keyboard activation) + `RecoveryPanel` column container.
  Plus a `parse_evidence_chips()` mirror of the v2 parser so a
  capture using the v3 card and the live launcher's RecoveryCard
  read the same chip row.
- **`investigation_panel.py`** — `InvestigationCardV3` with the
  directive's timeline strip + target chips + last-touch label
  + 4-segment resume-strength bar.
- **`trust_panel.py`** — the calm three-row footer (Daemon
  connected · Local only · Captured today).
- **`search_panel.py`** — `SearchPanel` + `SearchResult`
  dataclass with `QStackedLayout` of empty / results states.
- **`digest.py`** — `DigestColumn` (RecoveryPanel +
  InvestigationPanel + TrustPanel in the directive's order) +
  `EmptyDigest` (*"Recall notices unfinished work."* + Show
  example / Start normally button pair + local-only trust
  line). Emits `show_example` / `start_normally` signals —
  same contract as `app/ui/cards.py:EmptyCard`.
- **`sidebar.py`** — `Sidebar` (220 px left rail: Recall
  wordmark + search QLineEdit emitting `query_changed` +
  4-row section nav with accent-dot active marker).
- **`shell.py`** — `Shell` 3-column composition (sidebar +
  clamped centre 420-720 px + context column) + `ContextColumn`
  (right rail with Today / Doctor / version blocks).
- **`window.py`** — `LauncherWindow`, the top-level `QWidget`
  that paints the warm-white page background and hosts the
  Shell. Default 1100 × 720.
- **`__init__.py`** — barrel of 22 public symbols.
- **Dynamic sizing.** No `setFixedHeight` on any card body
  anywhere in the v3 package — `RecoveryCardV3.HEIGHT` and
  `InvestigationCardV3.HEIGHT` are *minimums*, not pinned
  values. The directive's *remove hardcoded heights* rule
  honoured.
- **Capture pipeline** at
  [`infra/scripts/capture/capture_launcher_v3.py`](../../infra/scripts/capture/capture_launcher_v3.py)
  — five PNGs into `assets/screenshots/launcher-v3/`:
  `digest.png` (full 3-column shell, populated), `continue.png`
  (recovery hero in isolation), `empty.png` (3-column shell
  with EmptyDigest centred), `trust.png` (footer in isolation),
  `focused.png` (recovery card in `_focused=True` state —
  the directive's *focus ring* spec rendered).
- **`docs/engineering/PHASE_6I_STATUS.md`** — engineering
  receipt + verification matrix + the deferred wire-in note.
- **No engine work, no recovery-logic changes.** The live
  `app/ui/launcher.py` was not touched. No `app/core/`, `api/`,
  `apps/extension/`, `apps/admin/`, or `apps/web/` file was
  touched. The directive's anti-rules held.

### Added — Phase 6H (Control Room OS)
- **Eight new live data loaders** under
  [`apps/admin/web/lib/loaders/`](../../apps/admin/web/lib/loaders/):
  `paths.ts` (canonical filesystem paths) · `fsx.ts` (defensive
  `readJSON` / `readJSONL` / `listDir` / `exists` / `fileMtime`
  / `pct`) · `health.ts` (baked health + live `~/.recall`
  state) · `trust.ts` (baked + the live 6-kind recovery-ledger
  aggregation) · `daily.ts` (mirrors `app/core/daily_loop.summary()`
  in TypeScript) · `alpha.ts` (re-derives `recall alpha export`
  on every request) · `release.ts` (normalised gate state +
  per-gate progress) · `system.ts` (filesystem-derived doctor
  checks). Every loader is idempotent and defensive — missing
  files return typed fallbacks; the page never throws.
- **Three-column operator shell** in
  [`apps/admin/web/app/layout.tsx`](../../apps/admin/web/app/layout.tsx):
  sticky left rail (`Nav.tsx`, 10 sections in 3 groups,
  accesskey hotkeys 1-9 + 0) · main route content · sticky
  right actions sidebar (`ActionsBar.tsx`, 7 buttons; *Refresh*
  triggers `router.refresh()`; the other six copy canonical CLI
  commands to the clipboard — **no server endpoint executes
  anything**).
- **Six live panel components** in
  [`apps/admin/web/components/panels/`](../../apps/admin/web/components/panels/):
  `HealthPanel`, `AlphaPanel` (6 directive signal cards with
  GYR pills), `DailyLoopPanel` (3 signal cards + counter table
  + 7-day heatmap of 5 bins × 7 days), `TrustPanel` (6 outcome
  stats + derived-signals row including trust %, returns
  linked, median time-to-resume), `ReleasePanel` (per-gate
  progress bars with GYR + GO/PARTIAL/NO-GO + blockers),
  `SystemPanel` (5 live filesystem checks). Plus a shared
  `Verdict.tsx` pill (3 colours + `mute`).
- **Ten dashboard routes**: `/` (overview — every panel
  compact), `/users` (per-cohort table → click to replay),
  `/alpha` (deep-dive), `/trust` (deep-dive), `/daily-loop`
  (deep-dive + heatmap), `/recovery` (6-stat header +
  time-to-resume sparkline + ledger rows linking to replays),
  `/replays?tester=<handle>` (per-tester event timeline +
  coverage line: install / activity / recovery / resume /
  return / wow / failure), `/release`, `/system`, `/docs`
  (static map of canonical docs). Every route is a React
  Server Component with `export const dynamic = "force-dynamic"`
  — no cache, no revalidate.
- **Inline SVG + styled-div for charts** — heatmap +
  time-to-resume sparkline are pure CSS / inline elements. No
  `recharts`, no `d3`, no charts library; the directive's *no
  chart explosion* rule held.
- **`PHASE_6H_STATUS.md`** ships the receipt + the green/yellow/red
  thresholds (also documented in
  [`docs/product/DAILY_LOOP.md`](../product/DAILY_LOOP.md)).
- **No Python, no engine, no recovery, no marketing-site touches.**
  Next.js build for the admin app: 10 routes, all `ƒ`
  server-rendered, 87.4 KB first-load shared. The directive's
  *no fake data, no hardcoded cards, everything derived* rule
  held across every panel.

### Added — Phase 6G (Public Alpha Surface)
- **Four new marketing-site section components** in
  [`apps/web/app/components/`](../../apps/web/app/components/):
  `Problem.tsx`, `Story.tsx`, `Screens.tsx`, `Download.tsx`.
  Each follows the existing visual rhythm (warm white +
  lavender + hairline borders, entrance animation only).
- **Hero copy aligned to the directive** in
  [`Hero.tsx`](../../apps/web/app/components/Hero.tsx). Headline
  *Recall notices unfinished work.*; sub *Return later. /
  Continue instantly.*; primary CTA *Download alpha* (now
  anchors to the in-page `#download` section instead of jumping
  to GitHub releases); secondary CTA *Watch demo*.
- **Privacy → Trust five-point rewrite** in
  [`Privacy.tsx`](../../apps/web/app/components/Privacy.tsx).
  Section eyebrow flipped to *Trust*; points rewritten to
  *Local only / No cloud / No telemetry / Counts only / Export
  only*, with each body mirroring the on-disk contract in
  [`docs/product/TRUST.md`](../product/TRUST.md).
- **Nav rebuilt to the new narrative order** in
  [`Nav.tsx`](../../apps/web/app/components/Nav.tsx):
  *The problem · How it works · Stories · Screens · Trust ·
  Download · GitHub*. The desktop + mobile Download button
  renamed to *Download alpha* and anchored to `#download`.
- **`apps/web/public/screens/`** — 19 PNGs in 4 subdirectories,
  copied from `assets/screenshots/{launcher-v2, extension-v2,
  demo, alpha}/`. The `Story` and `Screens` components reference
  these directly.
- **`docs/product/TRUST.md`** — the public trust statement.
  Five rules + on-disk contract per rule + *what Recall will /
  won't ask for* + the enforcement-in-code map.
- **`docs/release/DOWNLOAD_GUIDE.md`** — the four install paths
  (Windows lite / Windows full / macOS preview / browser
  extension) with platform-specific install steps, the 5-step
  first-run validation, and the per-platform uninstall paths.
- **`docs/release/DEMO_VIDEO_SCRIPT.md`** — the 60-second
  placeholder storyboard. Six beats, captions only (no
  voice-over), pre-flight checklist, the cuts to never make.
  The marketing site's *Watch demo* button flips to the hosted
  URL once `demo.mp4` is recorded.
- **`docs/founder/PUBLIC_ALPHA.md`** gains a Phase 6G addendum
  naming the new front-door surfaces and cross-linking the
  doc trio above.
- **`page.tsx` narrative order**:
  `Hero · Problem · HowItWorks · Story · Features ·
  ThreadConstellation · Screens · Privacy(Trust) · Download ·
  FAQ · FinalCTA`. The pre-6G `TrustedBy` strip is no longer
  mounted (no real "trusted by" logos yet).
- **No engine work**, **no recovery work**. The
  `app/core/`, `api/`, `app/ui/` (launcher / widgets), and
  `apps/extension/` trees are untouched. Next.js build:
  `/` at 55 KB, first-load 142 KB.

### Added — Phase 6F (Daily Loop Validation)
- **New `app/core/daily_loop.py` layer** — six counters per local
  day stored at `~/.recall/daily_loop.jsonl`
  (one JSON line per local day, < 50 KB / year):
  `day_started`, `investigations_opened`, `recoveries_shown`,
  `recoveries_used`, `returns`, `resume_success`. Three derived
  signals computed at read time
  (`continuity_restored` / `return_rate` / `resume_quality`)
  with GREEN/YELLOW/RED verdicts pinned in the in-source
  `verdict()`. **Counts only** — no URLs, filenames, queries,
  chat content, titles, or per-event timestamps. Disable via
  `RECALL_DAILY_LOOP=off`.
- **Return detector.** Every successful ingest calls
  `daily_loop.mark_event(time.time())`. The detector keeps
  `last_event_ts` in `~/.recall/daily_loop_state.json` and
  bumps the `returns` bin when the gap crosses 30 minutes
  (`RETURN_GAP_MIN_SECONDS = 1800`, matching the session
  reconstructor's idle break). Local-only, no upload, no event
  data exposed.
- **`POST /v1/loop/bump`** + **`GET /v1/loop/summary?days=7`**
  — two thin routes in [`api/main.py`](../../api/main.py),
  5 new DTOs in [`api/schemas.py`](../../api/schemas.py).
  Closed pydantic `Literal` of six bin names; bad input → 422.
- **Recovery-surface hooks.** `/v1/recovery/recent` bumps
  `recoveries_shown` **only** when the candidate list is
  non-empty (empty response = correct silence, tracked at the
  alpha-ledger level). `/v1/recovery/{id}/restore` bumps
  `recoveries_used`.
- **`recall founder daily-loop`** — new subcommand in
  [`app/core/founder_cli.py`](../../app/core/founder_cli.py).
  Reads `~/.recall/daily_loop.jsonl` directly (no bake), prints
  today / yesterday / 7-day window rows plus the three signals
  with GREEN/YELLOW/RED brackets and the directive's repeat-use
  success-line. ASCII-only, cp1252 safe.
- **`recall alpha replay <handle>`** — new subcommand in
  [`app/core/alpha_cli.py`](../../app/core/alpha_cli.py). Compiles
  a per-tester event-only timeline from `status.json` and the
  matching `recovery_journal.json` entries. **No content** —
  only dates + kinds + handle labels + meta hints. Ends with a
  coverage line (`OK install, OK activity, OK recovery, …`) so
  the founder can scan one tester in 5 seconds.
- **Recovery journal v2.** Schema in
  [`alpha/recovery_journal.json`](../../alpha/recovery_journal.json)
  gains `return_after_gap` (true/false/null) + `time_to_resume`
  (integer seconds). Both optional; legacy entries keep
  working. The two are the strongest correlation we have
  between *return* and *recovery* — the heart of the directive's
  *repeat-use* test.
- **Doc trio.**
  - [`docs/product/DAILY_LOOP.md`](../product/DAILY_LOOP.md) —
    six bins, three signals, thresholds, the *not telemetry*
    contract, performance budget.
  - [`docs/product/RETURN_BEHAVIOR.md`](../product/RETURN_BEHAVIOR.md)
    — the return detector's semantics in detail. What counts,
    what doesn't, why 30 min, the state file, the manual
    verification recipe.
  - [`docs/alpha/MOMENTS.md`](../alpha/MOMENTS.md) — the seven
    first-time moments per tester
    (first install / first capture / first investigation /
    first recovery / first resume / first wow / trust break)
    with a per-cohort log table.
- **No visual redesign**, **no installer work**. The launcher
  widget tree, the extension popup, the InnoSetup spec, and
  every existing UI surface are unchanged. The only runtime
  side effect is two new files under `~/.recall/`, both
  human-readable JSON, both deletable.

### Added — Phase 6E (Alpha Reality)
- **`alpha/users/_TEMPLATE/status.json` extended** with four
  directive-named optional metadata fields:
  `installer_version`, `extension`, `wow_moment`, `confusion`.
  Existing tester records keep working — the loader defaults
  missing keys to `None`. The boundary is unchanged: metadata
  only, never URLs / filenames / queries / chat content.
- **`recall alpha update <handle> --<field> <value> ...`** — new
  subcommand in [`app/core/alpha_cli.py`](../../app/core/alpha_cli.py).
  Cross-cohort lookup by handle (optional `--cohort` filter for
  disambiguation), closed allowlist of accepted fields
  (`_UPDATABLE_FIELDS`), type-coercion (`install_minutes` → float,
  `feedback_returned` → bool), empty-string clears a field.
- **`recall alpha export [--cohort <name>]`** — JSON dump of the
  same aggregation `report` prints in human form. Five top-level
  keys match the directive vocabulary verbatim:
  `installs` / `returning` / `recoveries` / `issues` / `trust`.
  Counts only.
- **`alpha/recovery_journal.json` schema rewritten** around the
  Phase 6E six-outcome vocabulary: `shown` / `accepted` /
  `ignored` / `correct_silence` / `bad_recovery` / `resume_ok`.
  Trust % computed as `(resume_ok + correct_silence) / shown`.
  Legacy entries (pre-6E `accepted` / `wrong` booleans) get
  mapped on read so old rows still count. Local only, export only.
- **`recall founder alpha-health`** — new subcommand in
  [`app/core/founder_cli.py`](../../app/core/founder_cli.py). Reads
  the source-of-truth files directly (bypasses `bake`) and prints
  the five signals with `[GREEN]` / `[YELLOW]` / `[RED]` brackets
  plus the directive's alpha-001 success-line (*5 humans / 3
  recoveries / 1 wow / 1 failure story*). ASCII-only output
  (cp1252 console safe).
- **`docs/alpha/` doc trio** — new operations book:
  - [`PLAYBOOK.md`](../alpha/PLAYBOOK.md) — six-moment tester
    lifecycle (install / use / leave / return / resume / report),
    daily morning loop, per-tester field list, six recovery
    outcomes, the no-content-no-telemetry contract restated.
  - [`STATUS.md`](../alpha/STATUS.md) — the live cohort board,
    hand-edited weekly from `recall alpha export` +
    `recall founder alpha-health`. Mirrors the directive's
    success-line table.
  - [`KNOWN_FAILURES.md`](../alpha/KNOWN_FAILURES.md) — failure
    catalogue with the quote-don't-paraphrase / never-inflate
    trust contract; promotion-to-engineering at ≥ 2 testers.
- **`docs/trust/ALPHA_MATRIX.md` extended** with a *Phase 6E
  daily-use + browser matrix* section: 5 new rows (Windows 11
  daily use × Chrome / Edge / Arc + macOS Intel / Apple Silicon
  daily use), each with *Recovery appeared?* + *Resume worked?*
  columns. `unknown` until a real tester completes ≥ 3 days on
  the machine + browser pair.
- **`assets/screenshots/alpha/`** — 3 new offscreen-Qt captures
  (Consolas mono, warm-white background so the alpha screens sit
  next to the launcher / extension v2 sets visually):
  `alpha-control-room.png` (the `alpha-health` panel populated
  with fixture data — 5 installs / 3 returning / 3 recoveries /
  trust 83 % / 1 yellow drop reason), `alpha-status.png`
  (`recall alpha status` with 5 testers across 4 cohorts),
  `alpha-empty.png` (the honest zero on a fresh repo).
- **`docs/engineering/PHASE_6E_STATUS.md`** — the engineering
  receipt + verification matrix.
- **No engine layer was touched.** The `events` / `sessions` /
  `microcontexts` / `resurfacing` / `threads` / `evolution` /
  `recovery` modules are not consulted, even indirectly. No UI
  surface (launcher widget tree / extension popup) touched —
  the directive's *no engine work, no UI redesign, only alpha
  operations* rule held.

### Added — Phase 6D (Demo Mode)
- **`app/core/demo_mode.py`** — five-state machine (`disabled` /
  `available` / `active` / `dismissed` / `completed`) persisted
  at `~/.recall/demo.json`. Public surface: `state()`,
  `is_active()`, `activate()`, `dismiss()`, `complete()`,
  `disable()`, `mark_real_activity()`, and the canonical
  `demo_payload(now=None)` fixture (1 recovery + 3 investigations
  + 8 timeline events + trust copy). **Hand-written, fully
  deterministic, no AI, no engine read.**
- **`/v1/demo/{state, activate, dismiss}` routes** in
  [`api/main.py`](../../api/main.py). `state` returns
  `{state, payload}`; `payload` is non-null only when
  `state === "active"`, so a naive consumer doesn't accidentally
  render demo content. Plus an internal `_post_ingest_hook(ok)`
  that every ingest route calls after a successful write —
  one line that calls `demo_mode.mark_real_activity()`, which
  auto-flips state to `dismissed` if it was `active`. *Real
  events override demo*, enforced in 1 function.
- **`api/schemas.py`** — 6 new DTOs (`DemoStateResponse`,
  `DemoPayloadOut`, `DemoRecoveryOut`, `DemoInvestigationOut`,
  `DemoTimelineEventOut`, `DemoTrustOut`).
- **Launcher empty surface wired live to `EmptyCard.empty()`**
  — closes the Phase 6B *Live launcher's empty surface wired to
  use `EmptyCard.empty()`* deferral. `EmptyCard` gained a
  `start_normally` signal + a *Start normally* secondary button
  (transparent fill, warm hairline border via new
  `QPushButton#secondary_button` QSS rule), paired with the
  existing *Show example*.
- **`Launcher._build_demo_panel()`** — the demo overlay
  rendered when `demo_mode.is_active()`. Trust banner
  (lavender-tinted, accent dot, *Example data — Nothing here
  came from your device.* + clickable *Dismiss*), a
  *Continue where you left off* section with the canonical
  demo `RecoveryCard` (WebSocket retry debugging, 2 tabs / 2
  files / 2d gap, confidence=high), and an *Active
  investigations* section with three `InvestigationCard` rows
  (WebSocket / Healthcare pitch — proposal draft / RLHF reward
  shaping). `Launcher._refresh_idle_state` dispatches on
  three branches (demo / empty / digest), with a
  belt-and-braces auto-dismiss for any path that bypasses the
  ingest hook.
- **Extension popup demo overlay.** `EmptyState`
  ([`apps/extension/ui/src/components/states.tsx`](../../apps/extension/ui/src/components/states.tsx))
  gained a *Start normally* secondary button next to the
  existing *Show example*; both wire to new
  `activateDemo()` / `dismissDemo()` helpers in
  `lib/api.ts`. `App.tsx` fetches `/v1/demo/state` alongside
  health / recovery / threads / events, and a new `"demo"`
  branch in the `PopupState` machine renders the canonical
  payload through the existing `ConnectedBody` (so the demo
  uses the same code path as a real populated surface). New
  [`DemoBanner` component](../../apps/extension/ui/src/components/DemoBanner.tsx)
  — lavender-tinted strip, accent dot, *Example data —
  Nothing here came from your device.*, right-aligned
  *Dismiss* link with `framer-motion` slide-fade entry.
- **Capture pipeline.** New
  [`infra/scripts/capture/capture_demo.py`](../../infra/scripts/capture/capture_demo.py)
  produces the launcher demo digest + the post-transition
  digest (same widget tree without the trust banner — the diff
  is exactly the banner). `apps/extension/ui/capture_extension.mjs`
  extended with an `OUT_DEMO` sibling directory, a
  `MOCK_DEMO_ACTIVE` fixture that mirrors the daemon's
  `/v1/demo/state` payload, and two new captures
  (`demo-extension.png`, `demo-extension-empty.png`).
- **`docs/product/FIRST_MAGIC.md`** — the product-side story:
  what demo is, what it isn't, how it disappears, the trust
  rules. Pairs with the engineering receipt
  [`PHASE_6D_STATUS.md`](../engineering/PHASE_6D_STATUS.md).
- **No engine layer was touched.** The `events`, `sessions`,
  `microcontexts`, `resurfacing`, `threads`, `evolution`, and
  `recovery` modules are not consulted by the demo path, even
  indirectly. Deleting `app/core/demo_mode.py` would remove
  the demo entirely without breaking any downstream artifact —
  the *purely additive* rule that CLAUDE.md requires of any
  new layer.

### Added — Phase 6C (Extension Premium)
- **Header — today count + repair icon.** `Header` in
  [`apps/extension/ui/src/App.tsx`](../../apps/extension/ui/src/App.tsx)
  now accepts `todayCount: number`. When the daemon is connected
  and `eventsToday > 0`, a quiet mono caption `"248 today"` sits
  next to the lavender `DaemonPulse` so the user has a passive
  live signal that isn't just a dot. A wrench-icon button (new
  glyph in
  [`icons.tsx`](../../apps/extension/ui/src/components/icons.tsx))
  sits between the wordmark and the gear — the directive's
  *repair* affordance.
- **`ContinueCard` confidence pill.** New `_deriveConfidence`
  (`n ≥ 4 → high`, `2-3 → medium`, `0-1 → low`) + `ConfidencePill`
  helpers render an inline pill right-aligned in the *Continue*
  header row. Mirrors the launcher's
  `derive_recovery_confidence(n_targets)` exactly — high =
  accent lavender, medium = warn amber, low = ink-3 grey. Pure
  UI-side derivation; **no engine field**. The outer
  `Section label="Continue"` wrapper was dropped because the
  card already owns that header with its own accent dot — the
  hero card now stands alone.
- **`MemoryList` rewritten as a vertical *Today* rail.** The
  grouped Searches/Tabs/Chats layout becomes a single
  chronological timeline: `HH:MM` local-time mono stamp + small
  round kind glyph + kind label + short title, sorted newest-first
  by `ts`, capped at 8. A 1 px vertical hairline ties the dots
  together — literally the *rail*. Rows without a real `ts` are
  dropped silently; **the popup never invents a timestamp**.
- **`InvestigationCard` → horizontal pill.** The row-card became
  a 28 px / radius-14 pill (`var(--surface-1)` background, soft
  border, 12 px thread glyph + ellipsised title). The host site
  renders investigations as `slice(0, 4).map(...)` inside a
  `flex-wrap` strip with a left-to-right slide-fade entry
  (`x: -6 → 0`, `opacity: 0 → 1`, `delay: i * 0.04`). Calm in,
  calm to settle — no bounce.
- **`EmptyState` — launcher-parity copy.** Headline
  *"Recall notices unfinished work."*, body *"Work normally.
  Return later. / Recall fills itself."*, and a soft *Show
  example* pill (`accent-soft` fill, `accent-line` border,
  accent text) that on click dispatches `openRecall()` — the
  popup hands off to the launcher, which owns the
  `EmptyCard.show_example` signal + the demo-seed wiring. This
  honours the *NO engine work* anti-rule.
- **Capture pipeline — `extension-v2/`.** `capture_extension.mjs`
  gained an `OUT_V2` sibling directory + optional `dir` arg on
  `shot()` / `shotWithMock()`, mkdir-ed via
  `mkdirSync(..., { recursive: true })`. Two new MOCK payloads —
  `MOCK_HOME_V2` (populated home: 248 events today, a recovery,
  4 investigations, 5 recent events) and `MOCK_RECOVERY_V2`
  (recovery-only, confidence pill + domain preview as focal
  point). Five new captures: `extension-home.png`,
  `extension-empty.png`, `extension-recovery.png`,
  `extension-repair.png`, `extension-offline.png`. The
  historical `assets/screenshots/extension-*.png` set stays
  untouched as the *before* reference, matching the
  `launcher-v2/` pattern from Phase 6B.
- **`docs/engineering/PHASE_6C_STATUS.md`** ships the full
  receipt + verification matrix. The directive's success line
  was *"wait this looks like product."*

### Added — Phase 6B (Launcher Identity)
- **Palette inverted to warm white + lavender.** Every
  `app/ui/styles.py` token flipped: `BG` `#0f1115` → `#fbf7f4`;
  `BG_RAISED` `#161922` → `#ffffff`; `TEXT` `#e8eaf0` → `#16112b`;
  `ACCENT` `#8b9bff` (blue) → `#8b7fe3` (lavender, matching the
  extension popup's `--accent`). The launcher and the extension
  popup now share one visual language. Tokens kept their names
  so every widget that read through the indirection picked up
  the new palette without further edits.
- **`LAUNCHER_QSS` rewritten** for the new theme. Floating
  glass card at `rgba(255, 255, 255, 184)` (72 % white over the
  OS), 1 px warm hairline, 22 px radius. Section labels gain
  generous padding (18 px top / 24 px sides) per the directive's
  spacing rhythm. List items get 10 px radius + 2 px margin.
  Scrollbar handles flipped to lavender at low alpha. A new
  `QPushButton#example_button` style ships for the empty-state
  CTA.
- **Card hover-fill swapped** from warm beige (`BG_HOVER`, which
  read as a flash on white) to low-alpha lavender accent
  (`ACCENT` at 0.10 × hover). Hover lift bumped 2 → 3 px;
  rounded-rect radius 9 → 12. `_ACCENT_RAIL`, `_OK`, `_WARN`
  retuned for the new background.
- **Recovery card evidence row as chip pills.** The dim text
  *"2 tabs · 3 files · reopened after a 2-day gap"* now renders
  as three separate widgets: `[2 tabs] [3 files] [2d gap]`. New
  `_EvidenceChip` (height 18, radius 6, count/time variants),
  new `_middle_with_chips(title, chips)` helper, new
  `_parse_evidence_chips(evidence)` parser that splits on `·`
  and normalises *"-day gap"* / *"hours ago"* into compact chip
  labels. Pure parsing — never invents data.
- **EmptyCard.empty redesigned** at 210 px tall with the
  directive's copy: headline *"Recall notices unfinished work."*,
  body *"Work normally. Return later. / Recall fills itself."*,
  and a soft *Show example* lavender pill that emits a new
  `EmptyCard.show_example` Qt signal (stub — no engine wiring).
  `EmptyCard.__init__` gained optional `height` +
  `show_example_button` kwargs so the unchanged `offline()` /
  `first_week()` factories still produce the compact card.
- **Capture pipeline gained optional `subdir`.** `_render.py`'s
  `render(...)` takes a `subdir=None` keyword; passing
  `subdir="launcher-v2"` writes to `assets/screenshots/launcher-v2/`.
  `Panel`'s default background flipped from `#13151b` to
  `#ffffff` so captures render against the new launcher
  backdrop. Capture scripts that need the historical dark
  surface can still pass `bg=...` explicitly.
- **Seven new launcher-v2 PNGs** in
  `assets/screenshots/launcher-v2/`: `launcher-digest.png` (the
  populated digest with chips + confidence badge),
  `launcher-empty.png` (the new first-magic surface),
  `launcher-loading.png`, `launcher-offline.png`,
  `launcher-first-week.png`, `recovery-card.png` (the chip-row
  recovery card), `recovery-card-focused.png` (with the lavender
  focus ring). The historical dark-theme launcher PNGs at the
  top level stay as the *before* set.
- **[`docs/engineering/PHASE_6B_STATUS.md`](../engineering/PHASE_6B_STATUS.md)** —
  receipt.

### Changed — Phase 6B
- `HOVER_LIFT_PX` 2.0 → 3.0 (still inside the directive's
  *"hover lift: 4 px max"* rule).
- `infra/scripts/capture/_render.py:Panel` default `bg` and
  `radius` parameters: `#13151b` → `#ffffff`, 14 → 22.
- `infra/scripts/capture/capture_launcher.py` and
  `capture_recovery.py` updated to call
  `render(..., subdir="launcher-v2")`.

### Discovered — Phase 6B (deferred)
- Wiring the live launcher's empty path to use `EmptyCard.empty()`
  (currently the running launcher uses its own QLabel-based
  empty widget; the redesigned `EmptyCard` lives in `cards.py`
  and renders in screenshots only). Focused launcher refactor;
  deferred to keep this phase's diff readable.
- *Show example* button — live demo-seed integration. The
  button + signal exist; the connection target is the live
  empty path migration above.
- Section rename to *Continue / Investigations / Recent returns
  / Trust* — same as 6A; touches the canonical vocabulary doc.

### Added — Phase 6A (First Magic)
- **RecoveryCard confidence badge.** A small inline pill in the
  meta column above the Resume affordance, in one of three
  bands: *high* (lavender), *medium* (amber), *low* (grey).
  Low-confidence cards keep the calmer `_StateDot` Resume
  affordance instead of the full `_ResumePill` — a Resume CTA
  on a hedged surface would over-promise. `RECOVERY_HEIGHT`
  bumped 64 → 76 to fit the badge.
- **`derive_recovery_confidence(n_targets)`** in
  [`app/ui/cards.py`](../../app/ui/cards.py) — UI-side mapping
  from candidate target count to band (≥ 4 → high, 2-3 →
  medium, ≤ 1 → low). Pure display logic; no engine-side trust
  field added (the directive's *No engine work* rule held).
- **Softer EmptyCard copy.** Refreshed from instructional
  ("Recall is ready. Work a little, then come back later…")
  to trusting ("Recall fills itself. Work a little. Come back
  later. What you can step back into will appear here.").
- **Extension Connection drawer made collapsible.** Header
  click toggles; `AnimatePresence`-wrapped body animates height
  + opacity over `calmFast` (180 ms). Default expanded when
  daemon is off, collapsed when healthy.
- **MemoryList timeline labels.** Each row gained a small
  mono-font age label on the right (*just now / 3m / 2h /
  yesterday / 3d / 2w*). New optional `ts?: number` field on
  `MemoryItem`; `fetchMemory` reads `e.ts` from the API. Events
  without a `ts` render no label - never fabricated.
- **[`docs/engineering/PHASE_6A_STATUS.md`](../engineering/PHASE_6A_STATUS.md)** —
  receipt.

### Changed — Phase 6A
- `RecoveryCard` parameter rename: `high_trust: bool` →
  `confidence: str` (values: high / medium / low). Capture
  scripts `capture_launcher.py` + `capture_recovery.py`
  updated. Back-compat not retained because the only callers
  were inside the repo.
- Capture mocks (`capture_extension.mjs` `MOCK` and
  `MOCK_CAPTURING`) grew `ts` values on each event so the
  deterministic extension screenshots render the new timeline
  labels.

### Discovered — Phase 6A (deferred)
- Full launcher theme swap to warm white + lavender + glass
  (major QSS rewrite; regression risk against the 15 existing
  screenshots).
- First-run *Show example* demo story (new launcher screen +
  demo-mode dispatch path against `app/core/demo_seed.py`).
- Recovery-card chip-row split (replacing evidence text with
  per-count chip widgets).
- Section rename to *Continue / Investigations / Recent returns
  / Trust* (touches `docs/product/CONTINUITY_LANGUAGE.md`).

### Added — Phase 5K (Alpha Reality)
- **`alpha/users/` directory tree.** Five cohort folders
  (`alpha-001` / `alpha-002` / `friends` / `builders` /
  `students`) each with a `TEMPLATE.md`, plus a shared
  `_TEMPLATE/status.json` schema the CLI copies. Per-tester
  fields: handle / cohort / install_date / platform /
  install_ok / install_minutes / day1 / day2 / day3 /
  first_recovery / first_resume_ok / kept_using / drop_reason /
  feedback_returned / notes. **Metadata only — never URLs,
  filenames, queries, chat content.** Zero fake testers seeded.
  Boundary documented in
  [`alpha/users/README.md`](../../alpha/users/README.md).
- **`app/core/alpha_cli.py`** — three-subcommand cohort CLI
  (~280 LOC, stdlib only).
  - `recall alpha create <handle> --cohort <name>` copies the
    JSON template into `alpha/users/<cohort>/<handle>/`, fills
    `handle` + `cohort` + `install_date: <today>`. Refuses to
    overwrite; rejects PII-shaped handles (any with `@`, spaces,
    or > 24 chars); rejects unknown cohorts.
  - `recall alpha status [--cohort <name>]` prints one calm row
    per tester with a compact `YYY|R3`-style day/recovery
    summary plus a totals footer (`returning`, `first-recovery
    seen`, `drops`).
  - `recall alpha report [--cohort <name>]` aggregates: users,
    returning, first-recovery, issues (install fails + wrong
    recoveries + drops), blockers (drop_reason counts),
    platforms, plus a directive-target check (5 users / 3
    recoveries / 2 returning).
- **`recall.py` fast-path dispatch** — `recall alpha …` routes
  through `app.core.alpha_cli` before the launcher import,
  matching the existing `stats` / `doctor` / `founder` /
  `repair` / `reset` / `reinstall-check` pattern.
- **[`alpha/ALPHA_FEEDBACK_V2.md`](../../alpha/ALPHA_FEEDBACK_V2.md)** —
  the tightened intake form. Six rows: moment of delight /
  confusion / wrong recovery / missed recovery / install pain /
  keep-remove. Each row mapped to a concrete artifact the
  founder must update if the row is filled (e.g. *wrong
  recovery* → a row in
  [`recovery_journal.json`](../../alpha/recovery_journal.json)
  with `wrong: true`). Supersedes v1 for cohorts opened
  post-5K; v1 stays live for already-mid-week testers.
- **[`docs/trust/ALPHA_MATRIX.md`](../trust/ALPHA_MATRIX.md)** —
  install-validation matrix. 5 slots × 7 columns (install time
  / doctor / extension / first capture / first recovery /
  resume / status). 3 Windows VM rows + 1 macOS Intel +
  1 macOS Apple Silicon, all `unknown` today. Each row maps to
  one walkthrough of `CLEAN_MACHINE_RUN.md` (Windows) or
  `MAC_OWNER_NEEDED.md` (Mac).
- **Extension Settings → *Connection* drawer.** New top-of-
  Settings card in
  [`SettingsPanel.tsx`](../../apps/extension/ui/src/components/SettingsPanel.tsx).
  Real-data: a breathing status dot (same vocabulary as
  `DaemonPulse`), `health.ingestedTotal` + `health.eventsToday`
  counts in mono font, a *Re-probe* button that re-runs the
  popup's existing `/v1/health` fetch, and a conditional *Open
  Recall* button (visible only when daemon is down) that routes
  through `openRecall()`. Three new props on `SettingsPanel`:
  `connection`, `health`, `onRetry`. Extension build: 286.85 kB
  JS / 91.58 kB gzipped (+1.81 kB).
- **[`docs/engineering/PHASE_5K_STATUS.md`](../engineering/PHASE_5K_STATUS.md)** —
  the phase close-out.

### Discovered — Phase 5K (not closed)
- **Zero alpha-001 testers enrolled.** The infrastructure is now
  ready; the distribution channel has not opened. The directive's
  success line (5 humans, 3 recoveries, real friction, real trust
  signal) is external-dependent.
- **Control room: alpha-growth / drop-reasons / install-success
  cards** named in the directive but not built. The CLI's `recall
  alpha report` already serves the same data in a terminal-
  friendly form; the Next.js dashboard work is deferred until
  cohort data exists to render.
- **Timeline chips + `correct_silence` counter** still deferred
  (same reasons as 5I + 5J — engine surface unchanged).
- **Launcher paper cuts** — none surfaced this phase without
  visual feedback on a running launcher. Documented as
  *nothing to fix* rather than fabricated polish.

### Added — Phase 5J (Installer Shrink Execution)
- **`Recall-Setup-lite.exe`** — new lite installer at
  `dist/installer/Recall-Setup-lite.exe`. **216.2 MB** (down
  44.6 MB from the 5F full's 260.8 MB). SHA-256 `F18D19FE7EB1CCD58C7260550F9DA6ACD1F70BAF3405A3200C0155BBE4513ED1`.
  Bundle expanded on disk: **783.3 MB** (down 187 MB / 19% from
  the 5F full's 970 MB). PyQt6 alone dropped 167 MB (217 → 50 MB)
  via the unused-modules submodule exclude; pyarrow + imageio_ffmpeg
  fully removed.
- **`Recall-Setup-full.exe`** — the 5F historical artifact stays
  side-by-side, renamed from the legacy `Recall-Setup.exe`. SHA
  recorded in [`INSTALL_PROOF_WINDOWS.md`](../trust/INSTALL_PROOF_WINDOWS.md);
  both variants now reported by `recall doctor` in one GREEN row.
- **`recall.spec`** — new `TIER_A_EXCLUDES` list (24 Python
  submodule excludes: `pyarrow`, `imageio_ffmpeg`, the 14 unused
  PyQt6 submodules — `Quick` / `Qml` / `Quick3D` / `Pdf` /
  `Designer` / `Multimedia` / `WebEngine*` / `Charts` /
  `DataVisualization` / `SerialPort` / `Sensors` / `Bluetooth` /
  `Nfc` / `Positioning` / `Location` / `TextToSpeech` — plus the
  existing dev-tool excludes). New `TIER_A_BIN_PATTERNS` list (19
  patterns) drives a post-Analysis binary filter that drops any
  Qt6 DLL / FFmpeg codec the Python excludes would have missed.
  Build log carries a one-line receipt: *"binaries 376 → 374
  (2 dropped); datas 5837 → 5837 (0 dropped)"* — the Python
  excludes did the heavy lifting.
- **`infra/packaging/windows/recall.iss`** — `OutputBaseFilename`
  changed to `Recall-Setup-lite`; the historical full installer's
  SHA + size are noted inline as the comparison baseline.
- **`app/ui/launcher_digest.py`** — second launcher slice. The
  `DIGEST_RECENT_MAX` / `DIGEST_RESURFACED_MAX` /
  `DIGEST_CONTINUE_MAX` / `DIGEST_THREADS_MAX` /
  `DIGEST_RECOVERY_MAX` / `DIGEST_RECENT_QUERIES_MAX` /
  `DIGEST_RECENT_ACTIVITY_MAX` / `RESURFACED_MIN_AGE_DAYS`
  constants + the `digest_labels()` time-of-day helper moved out
  of the 2.5 KLOC `launcher.py` into a stdlib-only sibling. The
  launcher imports them back so every existing
  `from app.ui.launcher import Launcher` keeps working.
- **Extension `ResumePreview`** — a mono-font caption above the
  Resume button on `ContinueCard` showing up to four unique
  hosts the click is about to reopen. Real data from
  `recovery.urls` only; rendered as `<host>  ·  <host>  ·
  <host>  ·  +N more` when the candidate has more URLs than
  fit. No placeholders — dropped silently when the recovery has
  zero URLs (file-only candidate).
- **[`docs/engineering/INSTALL_REDUCTION_REPORT.md`](../engineering/INSTALL_REDUCTION_REPORT.md)** —
  the Tier A execution receipt. Before/after table per subtree
  (with measured bytes), the 9-surface smoke matrix, and the
  honest *not-verified-this-phase* list (install time, daemon
  on a clean port, `_smoke_api.py` against the installed bundle).
- **[`docs/engineering/PHASE_5J_STATUS.md`](../engineering/PHASE_5J_STATUS.md)** —
  the phase close-out.

### Changed — Phase 5J
- **`app/core/doctor.py`** — `_check_installer_state` now
  recognises `Recall-Setup-lite.exe` + `Recall-Setup-full.exe`
  (alongside the historical `Recall-Setup.exe`) and reports
  every present variant in one GREEN row. Doctor's installer
  line reads:
  `Recall-Setup-lite.exe (216.2 MB) / Recall-Setup-full.exe (260.8 MB)`.

### Discovered — Phase 5J (and not closed)
- **Bundle still 783 MB; installer still 216 MB.** Directive
  targets were ≤ 660 / ≤ 180 MB. The gap closes with `pandas`
  exclude (~28 MB total transitive) + `torch+cpu` swap (~140 MB).
  Both deferred to Phase 5K because they need a clean-VM smoke
  to verify chromadb survives without arrow + pandas isn't on
  the runtime path.
- **Install wall time on a clean profile not measured.** The
  ≤ 45 s target requires a wipe-and-reinstall dance that was
  permission-denied this phase. Closed by a maintainer with VM
  access timing `Recall-Setup-lite.exe /VERYSILENT /LOG=...`.

### Added — Phase 5I (Install Speed + Real World Loop)
- **`infra/scripts/audit_install_size_v2.py`** — V2 install-size
  audit. Cross-references `install.log` against site-packages so
  every subtree row carries a real byte count instead of a wheel
  estimate. Produces the top-25 subtree report + top-20 single
  files report. Stdlib only, ~1.5 s runtime.
- **[`docs/engineering/INSTALL_SIZE_AUDIT_V2.md`](../engineering/INSTALL_SIZE_AUDIT_V2.md)** —
  real-byte breakdown of the 970 MB bundle. Names the elephants:
  `torch_cpu.dll` 265.8 MB; `imageio_ffmpeg` 87.7 MB FFmpeg
  (Recall has no media path); `pyarrow` 88.6 MB; ~60 MB of unused
  PyQt6 Quick / Qml / Designer / Pdf / opengl32sw / avcodec.
  Three reduction tiers: A (PyInstaller excludes alone, ~180 MB
  installer) / A+B (`torch+cpu`, ~150 MB) / A+C (ONNX runtime,
  ~50 MB).
- **[`docs/engineering/MODEL_STRATEGY.md`](../engineering/MODEL_STRATEGY.md)** —
  three concrete routes from torch + transformers to a smaller
  embedding stack. Recommends Tier B (ONNX runtime + bundled
  FP32 model; ~80 LOC swap in `app/core/embeddings.py`). Includes
  the int8 quantisation follow-up (~22 MB model vs ~80 MB FP32).
- **[`docs/engineering/SPLIT_DISTRIBUTION.md`](../engineering/SPLIT_DISTRIBUTION.md)** —
  four packs (Core / Retrieval Pack / Dev Tools / Demo Seed) +
  two install paths (Minimal 30 MB / Full ~110 MB). Inno Setup
  `[Components]` mapping; on-disk layout the engine reads to
  detect whether semantic search is available.
- **[`alpha/FIRST_72_HOURS.md`](../../alpha/FIRST_72_HOURS.md)** —
  hour-by-hour cohort journey map. Plots the trust / confusion /
  drop-risk / aha curve from minute-0 install through the Day 3+
  resume click. Pairs with `ALPHA_001_RUNBOOK.md` (founder view)
  and `SAMPLE_WORKFLOW.md` (cohort view).
- **`app/ui/launcher_anims.py`** — first slice extracted from
  `app/ui/launcher.py` (2.5 KLOC). Contains
  `play_digest_stagger_reveal(launcher)`. The launcher method
  becomes a one-line call. Net: launcher.py is ~50 lines shorter;
  the eventual `app/ui/launcher/` package layout has its first
  resident.
- **Extension `1` quick-resume hotkey.** Pressing `1` (no
  modifier) fires `onResume` on the visible recovery card. The
  Resume button shows a small `1` indicator with
  `aria-keyshortcuts="1"`. Handler skips when focus is in an
  input field (defensive).
- **Extension investigation surface chips.** `InvestigationCard`
  shows up to four small tags listing the *surface types* an
  investigation has touched (tabs / searches / chats / files).
  Real data from `investigation.surfaces` only.
- **[`docs/engineering/PHASE_5I_STATUS.md`](../engineering/PHASE_5I_STATUS.md)** —
  the receipt for the phase.

### Changed — Phase 5I
- **`app/ui/launcher.py`** — dropped three Qt6 imports
  (`QEasingCurve`, `QPropertyAnimation`, `QGraphicsOpacityEffect`)
  and the `MOTION_NORMAL_MS` import that moved with the slice.
  `_show_digest` now calls `play_digest_stagger_reveal(self)`
  instead of the 40-line inline method.
- **`docs/engineering/OPEN_PROBLEMS.md`** — Performance section
  rewritten against the V2 audit's three reduction tiers (concrete
  saving / risk / closure-path columns).

### Added — Phase 5H² (Friction Kill)
- **`app/core/install_repair.py`** — three-command install-side
  CLI. `recall repair` probes config dir / instance lock /
  `recall://` protocol / autostart and fixes the non-GREEN ones
  (with `--dry-run` to preview). `recall reset` clears derived
  caches (`resurfacing.json` / `threads.json` / `evolution.json` /
  `instance.lock`); `--full` adds `events/` + `chroma/` +
  `config.json` with a confirm prompt. `recall reinstall-check`
  is a read-only "what survives a reinstall" verdict. All ASCII,
  GREEN / YELLOW / RED, never raises.
- **`recall.py` fast-path dispatch** — added `repair` / `reset` /
  `reinstall-check` next to the existing `stats` / `doctor` /
  `founder` triad so a tester can run any of them from a Command
  Prompt without booting the launcher.
- **Extension `DaemonPulse`** — the 6 px dot in the popup header
  now breathes (opacity 0.5 → 1 → 0.5 over 1.6 s, looping) when
  the daemon is `connected`. Still when not. A single passive
  live-signal, no badges, no notifications.
- **Launcher `_play_digest_stagger_reveal`** — one-shot cascade
  on the first digest render per launcher instance. Each visible
  section (recovery → investigations → resurface → recent
  queries → recent activity → resurfaced) fades from opacity 0
  → 1 over `MOTION_NORMAL_MS` (180 ms) with a 60 ms inter-row
  stagger. `QGraphicsOpacityEffect` + `QPropertyAnimation`; refs
  held on `self` so Qt's GC does not eat them mid-flight.
- **[`docs/engineering/PHASE_5H_STATUS.md`](../engineering/PHASE_5H_STATUS.md)** —
  the receipt for the Friction Kill iteration.
- **[`docs/engineering/FRICTION_FIXED.md`](../engineering/FRICTION_FIXED.md)** —
  the cumulative ledger: 40 named frictions fixed across Phase 5F
  → here, grouped install / doctor / extension / launcher / code
  hygiene.
- **[`docs/engineering/OPEN_PROBLEMS.md`](../engineering/OPEN_PROBLEMS.md)** —
  the still-open list: 26 items, 16 *accept-by-design*, 10 real
  engineering with named closure paths.

### Fixed — Phase 5H²
- **`repair --dry-run` summary line.** The pre-fix codepath
  always reported "All install-side checks GREEN" in dry-run
  mode because the worst-state tracker only updated when fixes
  ran. Replaced with a `_bump` closure that updates on the
  probe verdict when `dry_run or fix is None`.

### Added — Phase 5H (Alpha Cohorts + Friction Removal)
- **Extension popup state machine.** `PopupState` (8 values:
  `loading` / `reconnecting` / `offline` / `disconnected` /
  `empty` / `capturing` / `investigations` / `recovery`) +
  `derivePopupState()` in
  [`apps/extension/ui/src/App.tsx`](../../apps/extension/ui/src/App.tsx).
  Invariant: daemon healthy AND `ingestedTotal > 0` ⇒ EMPTY
  forbidden (enforced by code path).
- **`CapturingState`** — new in
  [`apps/extension/ui/src/components/states.tsx`](../../apps/extension/ui/src/components/states.tsx).
  The middle ground between EMPTY and a populated launcher: a
  reassurance line, the event count, a live *Recent activity*
  feed (`MemoryList`, max 5 rows). No CTA - the user is mid-flow.
- **`openRecall()`** in
  [`apps/extension/ui/src/lib/api.ts`](../../apps/extension/ui/src/lib/api.ts) —
  three-rung ladder (daemon-probe → `recall://` dispatch →
  repair-fallback). Paired with an `OpenRecallButton` whose
  click *always* changes pixels (`idle → trying → repair |
  hint`) - the *never dead click* rule.
- **`DebugStrip`** in
  [`apps/extension/ui/src/components/DebugStrip.tsx`](../../apps/extension/ui/src/components/DebugStrip.tsx) —
  four mono-font counters at the popup bottom in connected
  states: `captured · browser · invest · recovery`. Derived from
  data already on the page; no extra fetch.
- **[`docs/engineering/FRICTION_FIXES.md`](../engineering/FRICTION_FIXES.md)** —
  11 issues × (issue / root cause / fix / verification) from the
  5G evidence walk. Every entry has a code change link + a
  reproduction recipe.
- **[`docs/engineering/INSTALL_SIZE_AUDIT.md`](../engineering/INSTALL_SIZE_AUDIT.md)** —
  the 260.8 MB installer's composition mapped to file counts +
  wheel sizes. `transformers` + `torch` are 66% of files;
  `pyarrow` + `tzdata` are unexpected ~75 MB of transitive
  weight; the path from 260 MB → ~170 MB compressed is named
  without code changes.
- **[`docs/release/LANDING_GO_LIVE.md`](LANDING_GO_LIVE.md)** —
  the 7-section website checklist (hero, three product
  sections, download row, FAQ ×6, limitations row, demo assets,
  privacy footer). Every row ⬜ today; named gates for go-live.
- **[`docs/release/RECORDING_PROTOCOL.md`](RECORDING_PROTOCOL.md)** —
  beat-by-beat recipe for `install.gif` and `control-room.gif`
  with ScreenToGif. ≤ 5 MB, ≤ 12 s, acceptance criteria.
- **[`alpha/launcher/`](../../alpha/launcher/)** — five-file
  no-terminal pack for cohort-001 testers: `install.ps1` (silent
  install with the right `/TASKS=` flags), `start_recall.bat`,
  `doctor_check.bat`, `feedback_link.txt`, `workflow.txt`.
- **[`alpha/ALPHA_001_RUNBOOK.md`](../../alpha/ALPHA_001_RUNBOOK.md)** —
  five-persona runbook (founder / student / researcher /
  builder / non-productivity) × four-day journey (day 0 / 1 /
  2-3 / 7) × four expected first-of dates (first
  investigation / first recovery / first Resume / first trust
  moment).
- **[`alpha/recovery_journal.json`](../../alpha/recovery_journal.json)** —
  hand-edited per-Resume ledger. Empty array; populated as
  testers report. Schema commented inline; never stores URLs,
  filenames, or queries (the launcher *title* is the only
  surface field).
- **`assets/demos/` — three deterministic GIFs.** Generated by
  [`infra/scripts/capture/generate_demo_gifs.py`](../../infra/scripts/capture/generate_demo_gifs.py)
  from existing static captures: `launcher.gif` (4-frame state
  cycle, 67 kB), `recovery.gif` (2-frame focus animation,
  8.8 kB), `extension.gif` (4-frame popup state cycle, 81 kB).
  Two deferred (install + control room) per
  `RECORDING_PROTOCOL.md`.

### Fixed — Phase 5H
- **[`app/core/doctor.py`](../../app/core/doctor.py)** — five
  related fixes:
  - cp1252 em-dash mangling in three user-facing strings
    (`_check_config`, `_check_events_dir`, `_check_launcher`).
  - `_check_version_mismatch` no longer reports a false
    "manifest not found" inside a frozen bundle; returns
    GREEN with "extension installed in browser, not bundled".
  - `_check_launcher` reads the lock's PID and probes its
    liveness (`_pid_alive` helper with cross-platform
    `os.kill(pid, 0)` semantics). Stale locks now report
    YELLOW instead of false GREEN.
  - `_check_autostart` honours both the HKCU Run-key path
    AND a per-user Startup-folder shortcut; silent installs
    correctly read GREEN.
  - `os` import hoisted to module level (was nested inside
    `_pid_alive`).
- **[`infra/packaging/windows/recall.iss`](../../infra/packaging/windows/recall.iss)** —
  new `[Registry]` section registers the `recall://` URL
  scheme on install (HKCU\Software\Classes\recall, with
  `uninsdeletekey` so the entire subtree is removed on
  uninstall). End-to-end verification deferred to the next
  rebuild + install.
- **Extension** — three popup-level fixes:
  - The hardcoded "WebSocket retry debugging" demo card is
    removed from `EmptyState`. The replacement is real
    recent-activity preview in `CapturingState`.
  - `SettingsPanel`'s *Open Recall* link routes through
    `openRecall()` (was a direct `openTab("recall://open")`
    dead-click).
  - The popup's body decision is no longer the inline `nothing
    = !recovery && investigations.length === 0 && memory.length
    === 0` ternary; it's the `derivePopupState()` pure function
    + a `switch` in `Body`. Removed dead branches.

### Changed — Phase 5H
- **[`apps/extension/ui/capture_extension.mjs`](../../apps/extension/ui/capture_extension.mjs)** —
  added `MOCK_CAPTURING` fixture + `extension-capturing.png`
  capture. Total extension screenshots: 7 (was 6 before 5H).
- **[`assets/screenshots/README.md`](../../assets/screenshots/README.md)** —
  added `control-room.png` / `doctor-output.png` /
  `installer-flow.png` (Phase 5G) + the Phase 5H captures
  list.
- **[`docs/founder/PHASE_TRACKER.md`](../founder/PHASE_TRACKER.md)** —
  advanced to Phase 5H; next milestone renamed to *Phase 5I -
  Live Cohort*; active-work table now names the five remaining
  external-dependent items (3 clean-VM runs, alpha-001
  cohort, recall:// rebuild, 2 live GIFs, website diff).
- **[`docs/founder/ROADMAP_LIVE.md`](../founder/ROADMAP_LIVE.md)** —
  *Now* describes Phase 5H; *Next* lists the live-cohort
  dependencies + the optional macOS + signing parallel tracks.

### Added — Phase 5G (Reality Validation)
- **[`docs/trust/CLEAN_MACHINE_RUN.md`](../trust/CLEAN_MACHINE_RUN.md)** —
  the gate-1 walk record. 13-row checklist × N-runs structure;
  Run 1 (▲ build machine, 2026-05-20) filled with real
  timings (66.0 s silent install, 6.1 s silent uninstall, all
  artifacts created + removed cleanly). Three fresh-VM runs
  remain ⬜.
- **[`docs/trust/RECOVERY_STRESS.md`](../trust/RECOVERY_STRESS.md)** —
  trust-stress coverage matrix. Three scenarios reproduced live
  (daemon-dead / corrupt-events / empty-install), three covered
  by design analysis (extension-removed / old-export / offline).
  Each entry has a *Setup*, *Behaviour* (doctor output), and
  *Verdict* (graceful / loud / silent-fail).
- **[`docs/release/INSTALL_METRICS.md`](INSTALL_METRICS.md)** —
  five numbers: installer size 260.8 MB, install time 66.0 s,
  launch to daemon ~3 s, memory 623 MB WS / 795 MB Private after
  warm-up, install dir 976 MB. Plus a *Later* table with
  shrinkage targets and the silent-install `/TASKS=` caveat.
- **[`docs/release/MAC_OWNER_NEEDED.md`](MAC_OWNER_NEEDED.md)** —
  the explicit dispatch ticket for any maintainer with macOS
  hardware. Step-by-step verification script, time estimate
  (~90 min on Apple Silicon), the five rows most likely to
  block, what "done" looks like.
- **[`alpha/alpha_report.md`](../../alpha/alpha_report.md)** —
  the founder-side evidence ledger framework for alpha-001.
  Five questions (did they install / did they return / did
  recovery help / did trust hold / where is the friction), each
  with a source-of-truth field in the manual `apps/admin/alpha/`
  JSON files. Currently *awaiting cohort data*.
- **Three more deterministic screenshots** —
  [`assets/screenshots/control-room.png`](../../assets/screenshots/README.md)
  (Edge headless against `next dev` at localhost:3000),
  `doctor-output.png` (offscreen-Qt render of the doctor's
  formatted text), `installer-flow.png` (the silent-install log
  milestone lines rendered as a terminal panel). 15 of 15
  documented surfaces now have real captures; only the
  *resume-in-progress* moment remains, gated on a real
  end-to-end install.

### Changed — Phase 5G
- **[`docs/release/GO_NO_GO.md`](GO_NO_GO.md)** — gate 6
  PARTIAL → GO (all 15 surfaces captured); gate 1 NO-GO →
  PARTIAL (build-machine ▲ run filled); gate 7 PARTIAL with
  end-to-end run evidence on the build machine. Verdict text
  rewritten to name the three remaining hard blockers
  (clean-VM ×3, code signing, cohort evidence).
- **[`docs/founder/PHASE_TRACKER.md`](../founder/PHASE_TRACKER.md)** —
  advanced to Phase 5G; next milestone renamed to *Phase 5H —
  Cohort + Polish*; blocked-items table reframed around what
  is genuinely external-dependent (clean VMs, 5 humans, an EV
  cert, a Mac maintainer).
- **[`docs/founder/ROADMAP_LIVE.md`](../founder/ROADMAP_LIVE.md)** —
  *Now* describes the work just completed; *Next* names the
  five Phase-5H polish items by their friction-log
  identifiers (cp1252 em-dash; frozen-bundle manifest;
  stale-lock; silent-install `/TASKS=`; `recall://`
  registration).

### Discovered — Phase 5G (the friction log; not yet fixed)
- **`recall doctor` em-dashes mangle to `�` on cp1252 Windows
  consoles.** Three messages in
  [`app/core/doctor.py`](../../app/core/doctor.py) use `—` despite
  the file's own ASCII-only header rule. Phase-5H.
- **Doctor `versions` check can't find the extension manifest
  from inside a frozen bundle.** Path is resolved relative to
  the source tree; PyInstaller-frozen builds always report
  *extension manifest not found*. Phase-5H: ship the manifest
  with the bundle, or skip the check when `sys.frozen`.
- **Stale instance lock reads GREEN after a forced kill.** The
  lock file is removed at clean shutdown, not SIGKILL. Doctor
  could PID-check the lock contents. Phase-5H.
- **`Recall-Setup.exe /VERYSILENT` skips the autostart task.**
  Documented in `INSTALL_METRICS.md`; workaround is
  `/TASKS="desktopicon,startuplaunch"`. A wizard install is
  unaffected.
- **`recall://` URL scheme not registered by the installer.** The
  extension popup's *Open Recall* button does not deep-link;
  it focus-signals the launcher instead. Phase-5H.

### Added — Phase 5F (Release Reality)
- **`Recall-Setup.exe` built for real.** Inno Setup 6.7.2 installed
  via `winget install JRSoftware.InnoSetup`; `infra/packaging/windows/build.ps1`
  hardened to find ISCC in the winget per-user location
  (`%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe`) and ran end-to-end:
  PyInstaller bundle → `dist/Recall/Recall.exe` → Inno Setup →
  `dist/installer/Recall-Setup.exe`. Closes
  [`GO_NO_GO.md`](GO_NO_GO.md) gate 7's first half (the *artifact
  exists* sub-gate). Code signing remains the second half.
- **`recall doctor` extended** — five new checks added on top of
  the original six: `installer` (bundle / `Recall-Setup.exe`
  presence), `autostart` (HKCU Run-key probe), `protocol`
  (`recall://` URL handler), `extension` (live pairing via the
  event log), `versions` (engine vs extension manifest drift).
  Doctor now answers *"is this install healthy?"* in 10 lines.
- **[`alpha/`](../../alpha/)** — the public alpha packet: a
  `README` plus five user-facing docs (`INSTALL`,
  `SAMPLE_WORKFLOW`, `TRUST`, `LIMITATIONS`, `FEEDBACK`). Short,
  scannable, no terminal required to read; designed for cohort
  alpha-001 to receive and return one filled `FEEDBACK.md` after
  a week.
- **[`docs/release/MAC_VERIFICATION.md`](MAC_VERIFICATION.md)** —
  the honest macOS matrix. 13 rows × 2 chip columns, every cell
  currently `unknown`. Replaces aspiration with a structured
  TODO that a Mac maintainer can fill in.
- **[`docs/trust/INSTALL_PROOF_WINDOWS.md`](../trust/INSTALL_PROOF_WINDOWS.md)** —
  Phase 5F's build proof. Real numbers from this cycle's
  PyInstaller + Inno Setup run, plus the 13-row clean-machine
  checklist that still needs a fresh VM. Replaces
  `INSTALL_VALIDATION_WINDOWS.md` (kept as the pre-5F historical
  record).
- **Settings dialog captured** —
  `infra/scripts/capture/capture_settings.py` renders
  `SettingsDialog` offscreen with a default `Config` fixture.
  `settings-dialog.png` joins the 13 existing real captures (14
  of 15 documented surfaces; control-room render remains the
  last gap).
- **`build.ps1` ISCC discovery hardened** — checks `iscc` on
  PATH, then `Program Files (x86)`, then `Program Files`, then
  the winget per-user location at
  `%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe`. Error message
  names the winget install line.

### Changed — Phase 5F
- **[`docs/release/GO_NO_GO.md`](GO_NO_GO.md)** — gate 7 NO-GO →
  PARTIAL (artifact built, signing pending); gate 5 PARTIAL →
  GO (alpha packet + Mac matrix landed); gate 6 stays PARTIAL
  with more honest numbers (14 of 15 captures); gate 1 still
  NO-GO (clean-machine walk pending).
- **`apps/admin/release_state.json`** — `installer: blocked →
  ready`, `blocked` list slimmed to the genuinely outstanding
  items (clean-machine walk, code signing, macOS hardware,
  control-room screenshot).
- **`app/core/doctor.py`** — original `_check_browser_memory`
  was renamed/refocused as `_check_extension_pairing` (same
  signal, sharper label). No behaviour change for the JSON
  output beyond the renamed key.

### Added — Phase 5E.3 (Founder Automation Layer)
- **`recall founder` CLI** — seven subcommands wired through the
  fast-path dispatch in `recall.py` (alongside `stats` / `doctor`).
  `status` is the 5-second view; `bake` regenerates the dashboard
  files; `release` shows the readiness breakdown + blockers;
  `trust` / `health` / `alpha` / `timeline` each render one
  section. All ASCII output (Windows cp1252 safe).
- **`apps/admin/scripts/bake_data.py`** — derives all eight
  control-room data files from a small set of founder-maintained
  sources (`aggregate.json`, `release_state.json`, `timeline_input.json`,
  `traction_history.json`, `cohorts.json`, `alpha/feedback.json`,
  `alpha/notes.json`). Stdlib only; missing sources degrade to
  warnings, never errors. Verified: 8 files written in ~11 ms.
- **`app/core/release_readiness.py`** — the 0-100 readiness engine.
  Six dimensions (installer / trust / alpha / release / docs /
  screenshots), weighted to 100, with a deterministic GREEN /
  YELLOW / RED verdict and a citable per-dimension audit trail.
- **`apps/admin/alpha/`** — `users.json` + `feedback.json` +
  `notes.json`, the manual board the bake reads from.
- **[`docs/founder/FOUNDER_OPERATIONS.md`](../founder/FOUNDER_OPERATIONS.md)** —
  the daily runbook (five-minute morning loop, cohort-import path,
  weekly sweep, when *not* to touch the admin).
- **[`docs/founder/READINESS_SCORE.md`](../founder/READINESS_SCORE.md)** —
  the 0-100 scoring: six weighted inputs, three bands, why it is
  *not* a marketing or productivity number, and how to move it.

### Added — Phase 5E.2 (Founder Control Room — UI)
- **`apps/admin/web/`** — the actual operator UI, built as a
  local-first Next.js 14 app. One page, seven sections, no server,
  no auth, no database, no telemetry. `npm install && npm run dev`
  → `localhost:3000` and the founder has a 30-second read of
  product state. Build verified clean (one static route, ~87 KB
  first-load).
- **Eight sections, file-driven.** Health overview · Traction
  (six hand-rolled SVG sparklines) · Alpha cohorts · Release
  (GO/NO-GO + installer/mac/signing/screenshots + blocked list) ·
  Trust · Feedback inbox · Founder timeline. Every section reads
  one JSON file from `apps/admin/data/`; a missing file degrades
  to a calm empty card, never an error.
- **`apps/admin/data/`** — eight sample data files seeded for
  screenshots: `health.json`, `traction.json` (30-day series),
  `cohorts.json`, `release.json`, `trust.json`, `feedback.json`,
  `timeline.json`, `meta.json`.
- **[`docs/founder/CONTROL_ROOM.md`](../founder/CONTROL_ROOM.md)** —
  explainer: what exists, what data is allowed in (the eight files,
  no other source), what never enters (per-user identifiers, content,
  sub-day timestamps, a second data source). The boundary contract.

### Changed — Phase 5D.1 (Documentation Consolidation)
- **40 root `.md` files consolidated into
  `docs/{product,founder,engineering,release,trust,archive/old-docs}/`.**
  Root now holds only the five front-door files the directive
  whitelisted: `README.md`, `CLAUDE.md`, `CONTRIBUTING.md`,
  `SECURITY.md`, `CODE_OF_CONDUCT.md`. **Behaviour unchanged** —
  pure file moves + cross-reference rewrites.
- **Every cross-reference rewritten.** A consolidation script
  moved files and rewrote moved-doc-to-moved-doc links to their
  new relative paths. A second pass fixed refs in the five
  kept-root files, `.github/*.md`, `releases/*.md`,
  `infra/**/README.md`, `apps/admin/*.md`,
  `assets/screenshots/README.md`, and the capture-pipeline README.
  Final result: **zero broken `.md`/`.mdx` links** across the
  entire repo, verified by filesystem resolution.
- **Pre-existing `docs/architecture/*.mdx` refs corrected.** The
  `README.md` / `CLAUDE.md` links pointed at
  `docs/architecture/...` which never existed at that path; they
  now correctly target the Mintlify site under `apps/docs/`.

### Added — Phase 5D.1
- **[`docs/DOC_INDEX.md`](../DOC_INDEX.md)** — the single index of
  every doc with purpose / owner / phase / status. Five sections
  matching the new folder structure; archive folder kept distinct.
- **[`docs/engineering/DOC_HEALTH.md`](../engineering/DOC_HEALTH.md)** —
  documentation-system metrics (root vs `docs/` counts, archived,
  broken-link total, orphan check, the hygiene rule going forward).
- **The hygiene rule.** A new doc lands in `docs/<area>/`, never at
  root, unless it is one of the five whitelisted root files.
  Adding a doc means adding a row to `DOC_INDEX.md` in the same
  PR — otherwise it is, by definition, an orphan.

### Changed — Phase 5D (Codebase Hygiene)
- **Archived 5 orphan marketing-page components.** `Architecture`,
  `ContinueWorking`, `ContinuityCore`, `EvolutionTimeline`, and
  `LocalFirstTopology` — no longer imported by
  `apps/web/app/page.tsx` after the Phase 4F landing rebuild —
  moved to `archive/web-components/`. `npx next build` verified
  green after. **No behaviour change.**
- **`.github/workflows/ci.yml`** — Phase 5D CI hygiene. Three
  jobs: engine import-check + 35-section smoke, marketing-site
  `next build`, extension popup `tsc + vite build`. No telemetry,
  no secrets.

### Added — Phase 5D (audit docs)
- **`DEAD_CODE_AUDIT.md`** — real grep-grounded audit. Table
  format (path / reason / action / risk). Records the 5 archived
  components this cycle and the flagged-but-not-removed items
  (`widgets.py` legacy row classes, three dead launcher imports)
  with reasons each was deferred.
- **`COMPLEXITY.md`** — measured LOC of the top files (launcher
  2,536 · widgets 2,487 · api/main 1,070 · recovery 1,026) and a
  proposed carve for the three directive-named candidates
  (`launcher.py`, `recovery.py`, `threads.py`). Refactors are
  recommended for dedicated PRs, **not done here** — Phase 5D's
  no-behaviour-change rule forbids it.
- **`REPO_HEALTH.md`** — headline metrics (20,152 Python LOC;
  3,735 archived; 0 TODO/FIXME comments). A tracked-over-time row
  for each future hygiene pass. Names the **safe-delete policy**:
  unused AND verified AND documented, else archive.
- **`DEPENDENCIES.md`** — every dependency classified across
  Python / web / extension popup. One audit finding flagged
  (`playwright` is in `dependencies`; should be `devDependencies`
  — does not affect the shipped popup bundle).

### Added — Phase 5C (Public Alpha Readiness)
- **`recall doctor`** — a local diagnostics CLI
  ([`app/core/doctor.py`](../../app/core/doctor.py)). Runs six checks
  (config, events directory, event flow, daemon, browser memory,
  launcher) and prints a calm GREEN / YELLOW / RED report with an
  overall verdict. Read-only; the only network call is a one-second
  loopback probe of `/v1/health`. Verified against the real
  `~/.recall/`; `--json` mode for tooling.
- **First-recovery ceremony** — a one-shot acknowledgement the
  first time recovery surfaces a candidate
  ([`app/core/ceremonies.py`](../../app/core/ceremonies.py) +
  launcher wire-in). A single calm footer flash: *"Recall noticed
  unfinished work. Pick a card to resume."* Persisted in
  `~/.recall/ceremonies.json`; never repeats; never animates.
- **Extension onboarding pass.** The popup's `EmptyState` now
  answers the four first-user questions in one calm view: *No
  activity yet* + a *How it works* three-rule card + a *You will
  see something like* example preview + an **Open Recall** CTA +
  the local-only trust line. Verified visually by Playwright
  (`extension-empty.png`).
- **`FIRST_WEEK.md`** — the Day 0–4+ user journey, with the
  friction / confusion / trust moment for every step and the code
  or copy that guards each.
- **`TRUST_MOMENTS.md`** — the seven firsts (first launch, first
  event, first investigation, first recovery, first resume, first
  export, first uninstall), each with the guard that keeps it
  honest. Names the asymmetry: a wrong first costs ~5× a right
  first earns.
- **`KNOWN_LIMITATIONS.md`** — the brutally honest list, split by
  *design* (never going away — no cloud, single-user, no
  telemetry, no LLM in production path, recovery biases toward
  silence) vs. *gaps being closed* (macOS Preview, unsigned
  installers, Chromium-only extension, manual export, no
  auto-update).
- **`PUBLIC_ALPHA_CHECKLIST.md`** — the 18-row kit checklist:
  what's green, what's the path to `0.2.0`. Red rows match
  `GO_NO_GO.md` gates 1, 2, 7 (verified installer + clean-machine
  walk + alpha-001 enrolled).

### Changed — Phase 5C
- **Launcher** picks up `Ceremonies` to fire one-shot
  acknowledgements. `_fill_recovery_list` now also drives the
  first-recovery flash.

### Added — Phase 5B (Daily Indispensability)
- **Date-bucketed counters.** `StatsCounters` now stores
  `{date: {key: count}}` instead of a flat dict — `bump()` writes
  today's bucket, `snapshot()` sums across every date (cumulative,
  the export view), and new `today()` returns just today's bucket.
  Pre-5B flat files are read as a single legacy bucket so no count
  is lost.
- **`recall stats --today`** + `compute_today()` — the local-only
  daily continuity score: recoveries shown/accepted today, work
  recovered, continuity-restored %, resume-success rate, resurface
  opens. **Explicitly excluded from `build_export()`** — none of
  these fields can leave the machine. Verified end-to-end.
- **Time-of-day digest headers.** The launcher's `_fill_*` methods
  now swap section labels by hour: morning lands on *"Continue
  today"*; evening on *"You paused here"*; threads section reads
  *"Still active"* mid-day. No notifications, no streaks — the
  surface just answers a slightly different question depending on
  *when* you reopened it.
- **`CONTINUITY_HEALTH.md`** — names the four day-shapes (excellent
  / fragmented / interrupted / recovered). Not a score, not a
  streak, not exported.
- **`TRUST_FIXTURES_DAILY.md`** — four daily-loop fixtures (great
  morning recovery, correct silence, great evening resume, the bad
  reopen that must not happen) with explicit "why correct" notes.
- **Founder metric additions** in `merge_stats.py` /
  `cohort_summary.py`: **returning installs**, **resume sessions**,
  **continuity restored**, **daily reopen %** — aggregate, derived
  from existing cohort exports. Documented in
  `FOUNDER_METRICS.md` § *Founder additions*.

### Added — Phase 5E.1 (Local Observability)
- **`app/core/stats.py` + `recall stats`.** A local, counts-only
  health command. `recall stats` prints a dozen metrics computed
  entirely from `~/.recall/` — install age, events, investigations,
  recoveries shown/accepted, resume success rate, daily/weekly
  active days, and more. Never a filename, URL, query, or title.
  Dispatched on a fast path in `recall.py` so it skips the launcher
  import.
- **`recall stats --export`** — writes an anonymous `stats.json`:
  counts and rates only, no identifier, no device id, no hash, no
  timestamp finer than the day (`build_export()` is the *entire*
  exportable surface). The user runs it; the user decides whether
  to share it. Nothing is uploaded.
- **`StatsCounters`** — a tiny `~/.recall/counters.json` store for
  the UI interactions the event log can't see (a recovery shown, a
  Resume clicked, a resurface opened). Wired into the launcher's
  `_fill_recovery_list`, `_on_recovery_restore`, and
  `_on_resurface_clicked`. Never raises.
- **`apps/admin/` import pipeline** — `import_stats.py` (validates a
  voluntary export is counts-only and *rejects* anything else),
  `merge_stats.py` (aggregates imports → `aggregate.json`),
  `cohort_summary.py` (the founder's terminal rollup + the
  green/yellow/red health signal). All verified end-to-end.
- **`TRUST_LEDGER.md`** — the enumerated boundary: what Recall sees
  on the machine, what it never sees, what can be exported, what can
  never be — with four ways to verify it yourself.
- **`FOUNDER_METRICS.md`** (which metric answers which founder
  question) and **`ALPHA_USERS.md`** (the manual public-alpha board).

### Changed — Phase 5E.1
- **`apps/admin/DASHBOARD.md`** gained a **Health Overview** —
  four green/yellow/red cards (installation, continuity, extension,
  trust). Its vocabulary was corrected: *downloads / users / DAU /
  MAU* → **active installs / returning installs / recovery sessions
  / continuity events**. Recall counts things, not surveilled
  people, and the words now say so.

### Added — Phase 5A.1 (Install Validation)
- **Real builds attempted, not just specified.** The PyInstaller
  app-bundle build (`recall.spec`) was *executed* against the full
  dependency tree; the extension popup was rendered in headless
  Chromium. Phase 5A.1's rule: a validation row is checked only if
  it was run.
- **`capture_extension.mjs`** — a Playwright capture script that
  serves the built popup over HTTP and screenshots every pairing
  state. Produced five real screenshots — `extension-connected`
  (a fully populated surface, via mocked loopback responses),
  `extension-missing`, `extension-disconnected`, `extension-offline`,
  `extension-loading`. The popup gained a `?state=missing` preview
  path so the never-installed screen is capturable.
- **`releases/`** — release-staging scaffold: `windows/` +
  `preview/` channel folders, `make_checksums.py` (SHA-256SUMS +
  `manifest.json`, runnable), and `RELEASE_NOTES_v0.2.0.md` (draft).
- **Validation docs** — `INSTALL_VALIDATION_WINDOWS.md` (build proof
  + 13-row clean-machine checklist), `MAC_BUILD_STATUS.md` (honest
  not-started tracker — no pretending support exists),
  `EXTENSION_VALIDATION.md` (the pairing-state matrix), and
  `GO_NO_GO.md` (the seven-gate public-alpha gate — currently
  **NO-GO**, with the blockers named).
- **Screenshots are real now.** `assets/screenshots/README.md`
  rewritten from a placeholder plan into an inventory of twelve
  deterministic captures.

### Changed — Phase 5A.1
- **`PHASE_TRACKER.md`** advanced to phase 5A.1; blocked items and
  next milestone (Phase 5B) updated.

### Added — Phase 5E (Control Room)
- **`apps/admin/` — a no-telemetry operator dashboard.** Founder
  visibility into installs, retention, breakage, and recovery —
  built *without* a collection mechanism, because the charter
  declines telemetry and the product promises nothing leaves the
  device. It composes three honest sources only: GitHub's public
  release download counts (`pull_release_stats.py`, runnable),
  voluntary cohort check-ins (`cohorts.json`), and hand-logged
  feedback (`FEEDBACK.md`). `DASHBOARD.md` is the founder's
  30-second view across all six sections — Release Monitor, Usage
  Health, Trust, Funnel, Feedback, Cohorts — with every figure
  tagged by source (`[auto]` / `[cohort]` / `[manual]` / `[—]`).
  Metrics that would require device telemetry render honestly as
  `[—]` (not collected), never silently estimated.
- **`PHASE_TRACKER.md`** — current phase, completed phases, active
  work, blocked items, next milestone, public-release target.
- **`ROADMAP_LIVE.md`** — a four-column board: Now / Next / Later /
  **Never**. The Never column is the public twin of CLAUDE.md's
  *things we will not build* — telemetry included.
- **`FOUNDER_DASHBOARD.md`** — the five founder questions (did they
  install / return / recover; what broke; why leave) and an honest
  account of which have automatic answers and which can only be
  answered by talking to a cohort.

### Added — Phase 5A (Zero Friction)
- **Windows packaging — `infra/packaging/windows/`.** An Inno Setup
  script (`recall.iss`) that wraps the PyInstaller bundle into
  **`Recall-Setup.exe`**: per-user install (no admin prompt), Start-
  menu + optional desktop shortcut, an opt-in "Start Recall when I
  sign in" entry, first-run launch, and a `/SILENT` repair path.
  `build.ps1` runs PyInstaller → Inno Setup in one command.
- **macOS packaging — `infra/packaging/macos/`.** A menu-bar `.app`
  (`Info.plist`, `LSUIElement`), a login launch agent
  (`computer.recall.agent.plist`), and `build.sh` (PyInstaller →
  `.app` → `Recall.dmg` via `hdiutil`). Reviewed, not yet built on
  macOS — flagged honestly in the folder README and
  `SUPPORTED_PLATFORMS.md`.
- **Distribution docs.** `INSTALL.md` (the grandmother path —
  download, double-click, works), `DOWNLOADS.md` (artifact table,
  SHA-256 verification, signing status), `SUPPORTED_PLATFORMS.md`
  (support tiers + the four release gates, stated plainly).

### Changed — Phase 5A
- **Extension pairing.** The popup now distinguishes *Recall never
  installed* from *Recall installed but not running* — it remembers,
  via `chrome.storage`, whether the daemon has ever answered. The
  disconnected screen leads with the right call to action: **Install
  Recall** for a first-time user, **Open Recall** + **Repair
  connection** for a returning one. No more dead-end "try again".

### Added — Phase 4K (Launcher Redesign)
- **`app/ui/cards.py`** — one consistent launcher card, six kinds.
  Every digest surface is now the same 54px row with the same three
  zones: a left glyph chip, a middle block (title + behavior
  evidence), and a right meta column (time + state). The set:
  `RecoveryCard` (accent rail, Resume affordance), `InvestigationCard`,
  `ResurfaceCard`, `TrustCard`, plus the non-row `SkeletonCard`
  (loading placeholder) and `EmptyCard` (calm empty / offline /
  first-week states via classmethods).
- **Keyboard + focus.** Cards are `StrongFocus`, draw a painted
  accent focus ring, and activate on Enter / Return / Space — the
  digest is fully keyboard-navigable.
- **Paced hover.** Hover is a 120ms fade (MOTION.md's 100–140ms
  band), animated via `QVariantAnimation` — never an instant flash.

### Changed — Phase 4K
- **Launcher digest wired to the new cards.** `_fill_recovery_list`,
  `_fill_threads_list`, and `_fill_resurface_list` now build
  `RecoveryCard` / `InvestigationCard` / `ResurfaceCard` instead of
  the old `RecoveryRow` / `ThreadRow` / `ResurfacedRow`. Signal
  shapes were kept compatible, so the restore / open-thread /
  open-target handlers are unchanged. All rows now share one 54px
  height.

### Added — Phase 4L (Screenshot Pipeline)
- **`infra/scripts/capture/`** — a deterministic screenshot
  generator. `_render.py` drives Qt's `offscreen` platform (no
  display), loads a host font into the empty offscreen font
  database, and grabs widget trees to 2× PNGs. `capture_launcher.py`
  renders the digest plus every state; `capture_recovery.py` renders
  the recovery card resting and focused. Output: real, regenerable
  screenshots under `assets/screenshots/` — `launcher-digest`,
  `launcher-loading`, `launcher-empty`, `launcher-offline`,
  `launcher-first-week`, `recovery-card`, `recovery-card-focused`.
- Pending captures (settings dialog, extension popup) are documented
  in `infra/scripts/capture/README.md` — each needs its own host.

### Added — Phase 4J (Surface Coherence)
- **`CONTINUITY_LANGUAGE.md`** — the single source of truth for
  every user-facing word. Resolves the live drift (the launcher
  said *"Active memory threads"*, the extension said *"Active
  investigations"*) by picking canonical names: user-facing copy
  says **investigation**, **memory**, **resume**; the engine keeps
  **thread**, **event**, **restore**. Same internal/external split
  the codebase already used for event/memory.
- **`SURFACE_MAP.md`** — one job per surface (website = promise,
  launcher = active continuity, extension = lightweight continuity,
  docs = explanation, settings = control, recovery = return path,
  resurfacing = passive reminder), with boundary tests for what
  does *not* belong on each.
- **`MOTION.md`** — the motion contract across launcher, extension,
  and website: a three-rung duration ladder (100–140 ms hover /
  180–220 ms expand / 250 ms reveal), one easing family, three
  allowed motions (fade / expand / slide), and an explicit
  forbidden list. Motion is continuity, not delight.
- **`PUBLIC_ALPHA.md`** — the end-to-end alpha path: install,
  first-use, extension setup, expected behavior, trust checks,
  uninstall, and an honest known-limitations list.

### Changed — Phase 4J
- **Vocabulary drift fixed in user-facing strings.** The launcher
  digest header *"Active memory threads"* → **"Active
  investigations"**, matching the extension. The marketing site
  (`ThreadConstellation`, `Features`, `HowItWorks`, `Hero`) and the
  README now say **investigation** wherever they meant a Recall
  thread; `thread` survives only as the engine/API term.
- **README opening** gained the explicit build-around flow —
  *interrupt → leave → return → resume* — and a *"why not an AI
  chatbot"* paragraph (a chatbot answers questions; Recall restores
  state).
- No features added. Phase 4J is coherence only — per its own
  first line, *Recall has enough features*.

### Added — Extension Phase A (Continuity Companion)
- **The browser-extension popup is now a productized memory
  surface.** The old 280 px vanilla HTML popup (a status dot + one
  toggle) is replaced by a 440 px React surface that answers *"what
  was I doing?"* the moment it opens. Source lives in
  `apps/extension/ui/` (Vite + React + TypeScript + Framer Motion);
  `npm run build` emits `apps/extension/popup/`, which the MV3
  manifest's `default_popup` points at. Capture (`background.js`)
  and the popup stay fully decoupled.
- **Five sections, top to bottom:** *Continue* (the single
  strongest interrupted investigation, with a Resume button) ·
  *Active investigations* (≤4 ongoing topics) · *Browser memory*
  (recent searches / tabs / chats, grouped) · *Trust* (local-only,
  daemon status, events captured today) · *Settings* (capture
  toggles + links, a slide-in view reached from the header gear).
  Components: `ContinueCard`, `InvestigationCard`, `MemoryList`,
  `TrustSurface`, `SettingsPanel`, plus `Section`, `states`, `icons`.
- **A real connection state machine.** Every non-normal state —
  loading, reconnecting, disconnected, offline, empty — is a calm
  full-body screen (no red, no error iconography). Each is
  previewable in isolation via a `?state=` query param
  (storybook-style). The popup never throws on a dead daemon: every
  call is wrapped, a missing daemon is a state.
- **Design language:** calm, light, minimal — Raycast × Arc ×
  Granola. Warm off-white surfaces, soft hairlines, 14 px radius,
  24 px section rhythm, one lavender accent per zone. Continuity
  motion only — fade / expand / slide on a single calm easing
  curve; no bounce, no float, no glass, no neon, no charts.
- **`apps/extension/architecture.md`** — component model, the
  capture-vs-popup split, data flow, the connection state machine,
  and the build pipeline. Extension `README.md` rewritten for the
  two-half layout and the popup build.

### Changed — Phase 4I (Launcher Experience)
- **Launcher calmness pass.** Digest section headers gained real
  vertical rhythm (generous top padding) so the idle surface reads
  as a few calm zones rather than one dense list; the digest hover
  was softened so passing the cursor no longer makes the surface
  flicker with energy. The empty-launcher copy is now orientation-
  first — *"Work a little, then come back later"* — instead of an
  instruction block. A deeper structural redesign of the digest
  (merging the surfaces into an explicit three-tier hierarchy, new
  recovery-card widgets, entrance motion) is deferred: it needs a
  running PyQt environment to verify, which this pass did not have.

### Fixed — Phase 4H (Continuity Experience)
- **File artifacts no longer split off from their investigation.**
  A file open carries a *filename*, not a topic, so the thread
  builder keyed `backoff.py` to its own bucket — and it surfaced as
  a standalone thread, disconnected from the WebSocket debugging it
  belonged to. The human saw one investigation; Recall saw several
  loose artifacts.
- **Fix — session-anchored bucketing** (`ThreadBuilder._bucket_events`).
  Two passes: pass 1 anchors each session to its dominant topic
  (from browser / search / chat text); pass 2 buckets every event,
  and a file open/reveal **bridges into its session's anchor topic**
  when one exists. `backoff.py` opened inside a WebSocket session
  now joins the WebSocket investigation; a file opened in a pure
  coding session with no anchor keeps its own key. Deterministic,
  local, no embeddings — the bridge signal is same-session
  co-occurrence inside the 30-minute window. The WebSocket demo
  thread goes from 6 events / its files-orphaned to 10 events /
  4 surfaces.

### Changed — Phase 4H
- **Recovery restores the room, not the objects.** Recovery read
  thread membership by re-deriving each event's key with
  `_thread_key`, which undid the session-anchored grouping above.
  It now reads membership from the new
  `ThreadBuilder.events_for_topic()` — the same bucketing
  `rebuild()` uses — so a WebSocket recovery candidate carries
  `backoff.py` and `client.py`, not just the tabs (5 targets, was
  2). A one-entry `now`-keyed memo on the bucketing pass keeps the
  recovery budget intact.

### Added — Phase 4H
- **`TRUST_FIXTURES_CONTINUITY.md`** — investigation-grouping
  calibration. Four named fixtures — correct merge, correct split,
  bad merge, bad split — each with an explicit rationale for why
  Recall's idea of "one investigation" should or should not match
  the artifact boundaries. The pre-4H `backoff.py` bug is recorded
  as the named "bad split" regression.

### Added — Phase 4G (Trust Calibration)
- **`TRUST_FIXTURES.md`** — named, deterministic continuity-trust
  fixtures. Four categories — *excellent recovery*, *acceptable
  silence*, *correct resurfacing*, *suppressed noise* — each mapped
  to a real story in `demo_seed.py`, with an explicit written
  rationale for why that surface (or silence) is correct. Recovery
  and resurfacing are now graded on believability, not volume; a
  change that moves a fixture off its expected surface is a trust
  regression and is reviewed like a moved perf budget.

### Changed — Phase 4G
- **Recovery captions now state specific, checkable evidence.**
  `_behavior_clause` was sharpened from generic phrases ("repeated
  search", "kept reopening one page") to evidence the user can
  verify against memory: `re-ran the same search 3 times`,
  `reopened after a 2-day gap`, `returned to this 3 times`. It now
  tracks per-target time spans, so a deliberate return after a
  multi-day gap — the strongest return-intent signal — is named
  precisely. Trust is built from specificity: a caption the user
  can confirm is one they come to rely on. Deterministic; one
  clause; `int()`-floored so the gap is never overstated.
- **Smoke § 11 measures best-of-5, not a single sample.** A lone
  wall-time sample on a loaded machine carries ±2× variance
  (TestClient thread/portal overhead, GC, scheduling) — enough to
  flip the gate while the code sits well inside budget. Section 28
  already used best-of-N; § 11 now matches it and the `PERF.md`
  methodology. **The 100 ms budget is unchanged** — only the
  measurement was made honest.

### Added — Phase 4F (Trust + Responsiveness)
- **`PERF.md`** — the performance-discipline contract: benchmark
  methodology (warm vs cold path, distributions over single
  samples, cProfile caveats), the budget table, the profiled hot
  paths, parse-cache behavior, scaling characteristics, and the
  regression-detection philosophy.

### Fixed — Phase 4F
- **Parse-cache TTL too short to bridge consecutive requests.**
  Root-caused the `_smoke_api.py` section-11 budget failure
  (10K-event `/v1/search` measured ~170 ms vs the 100 ms budget).
  Verdict from real profiling: *not* a scoring regression — the
  `EventStore` parse cache had a **0.5 s TTL**, tuned to "cover one
  launcher request". Two searches more than half a second apart
  each re-parsed the whole 10K-event log (~80 ms): a search 0.45 s
  after a warm-up measured 224 ms; 1.0 s after, 171 ms — exactly
  the smoke number. A real responsiveness bug under daily use, not
  just a test artefact.
- **Fix — parse cache keyed on `(mtime, size)`.** Cache freshness
  now rides on the file's modification time *and* size. Every
  write the system makes is an append, which always grows the
  file, so the size check detects every real write immediately;
  the TTL is freed to be a 60 s paranoia backstop. Sustained
  interactive search now stays on the warm ~13 ms path instead of
  paying an ~80 ms re-parse per query. Verified: appends still
  invalidate correctly, and `_smoke_api.py` passes all 35 sections
  across 5 consecutive runs.

### Changed — Phase 4E (Behavioral Indispensability)
- **Recovery quality gate tightened.** The Phase 4E directive is
  *fewer, stronger, eerily believable* recoveries — a recovery the
  user bounces off of teaches them the surface is noise.
  `_MIN_CONFIDENCE` (the trust floor on `max(continuity,
  confidence)`) raised 0.50 → **0.55**. New
  `_MIN_RESUME_INTENT = 0.32` is a hard floor on
  `recovery_confidence` *itself* — a candidate can no longer
  surface on an intact-but-finished context alone.
  `_LAST_PHASE_RECENCY_DAYS` tightened 10.0 → **7.0**
  ("interrupted" means still warm in the user's head).
  `_MIN_DISTINCT_TARGETS` raised 2 → **3** (a real multi-source
  context, not a reference plus one stray click). A missed
  recovery is better than a weak one.
- **Recovery previews gained a behavioral clause.** Counts
  ("3 tabs · 2 files") describe a context's *shape*; they don't
  say what the user was *doing*. `_preview_caption` now adds one
  deterministic middle clause — `repeated search` or
  `kept reopening one page` — drawn from the same event data.
  One signal max, search-first, so the row stays a single quiet
  line. No prose, no model.
- **Demo realism.** Story 1 (websocket-retry debugging) now ends
  with a recent reopen of `backoff.py`, so the interrupted-coding
  recovery lands the user *mid-edit* — the exact moment recovery
  is for. `_SEED_VERSION` 4B.1 → 4E.1 forces a clean re-seed.
- **Behavior-first copy pass.** The landing page (`Hero`,
  `HowItWorks`, `Features`), the README opening, and the launcher
  onboarding subtitle now lead with the *interruption* pain —
  rebuilding context, tab archaeology, the climb back into focus —
  rather than architecture vocabulary. The product names the pain
  it removes within the first fifteen seconds.
- **README** — stale "31-section smoke test" corrected to
  "35-section".

### Added — Phase 4D (First Public Users)
- **`FIRST_USE_AUDIT.md`** — five-persona audit of the
  *post-install* journey (systems engineer, privacy-conscious
  developer, researcher, founder, productivity skeptic). One
  trust moment, one doubt moment, and a concrete fix per
  persona. Three recurring patterns identified as the highest-
  leverage Phase 4D items: first-week silence, hidden
  extension install, restoration choreography pacing.
- **`apps/docs/uninstall.mdx`** — explicit clean-removal path.
  Six steps, complete in ~one minute, leaves zero residue.
  Documents which artefacts Recall installed (`~/.recall/`,
  autostart entry, browser extension, HF model cache) and how
  to verify each was removed.
- **`.github/ISSUE_TRIAGE.md`** — maintainer-side triage flow.
  Decision tree, label policy, what gets immediately
  declined (cloud sync, LLM chat, telemetry, dashboards,
  notifications), what gets escalated, what gets locked.
- **Smoke section 32** — upgrade compatibility. A 4-record
  JSONL file mixing pre-1A shape (no payload), pre-2A shape
  (no session_id), modern shape, and forward-compat shape
  (unknown fields) all parse with safe defaults.
- **Smoke section 33** — restoration plan ordering is
  deterministic. Two consecutive `/v1/recovery/{id}/restore`
  calls return byte-identical step lists.
- **Smoke section 34** — recovery determinism. Two
  consecutive `/v1/recovery/recent` calls return identical
  candidate ids + identical scores within the cache window.
- **Smoke section 35** — extension-disconnect scenario. The
  product is operational without the extension installed;
  non-extension clients can still POST to `/v1/events/*`
  and the API health surface stays accurate.

### Changed — Phase 4D
- **README opening.** *"Why does this matter?"* now lands in
  20 seconds. Live launcher example sits immediately after
  the tagline; three honest claims follow; then the layer
  table. The duplicated demo block lower in the file was
  removed.
- **Public-vocabulary final pass.** Remaining "AI memory
  layer" / "AI memory" copy removed from
  `apps/web/app/layout.tsx` (OpenGraph + Twitter meta),
  `apps/web/app/components/Footer.tsx`, `apps/web/README.md`,
  `app/__init__.py` module docstring, and the
  `app/ui/onboarding.py` welcome subtitle. The canonical
  positioning ("a local-first continuity operating system")
  is now the only framing on every user-facing surface.

### Added — Phase 4C (Stability + Sharpness)
- **`STABILITY.md`** — the contract for *"I trust this enough to
  leave running for years."* Documents guarantees (determinism,
  local-first, inspectability, performance budgets, backward
  compatibility), the failure philosophy (the logger must never
  raise, the reader must never raise on malformed input, the API
  must never 500 silently, the launcher must never crash on
  user-visible actions), per-layer degradation paths, deterministic
  principles, and recovery-specific guarantees.
- **Smoke section 30** — demo seeder determinism (byte-identical
  files across re-seeds for a fixed `now`).
- **Smoke section 31** — corrupt-JSONL graceful degradation (a
  7-line file with 4 broken lines and 3 good lines parses to
  exactly the 3 good events).
- **`apps/docs/install-3min.mdx`** — speedrun install path for
  technical users targeting a <3-minute install.

### Changed — Phase 4C
- **Recovery sharpness.** `_MIN_CONFIDENCE` raised from 0.45 →
  **0.50**. New `_LAST_PHASE_RECENCY_DAYS = 10.0` guard
  filters threads whose last *coherent block of work* (the last
  evolution phase) ended more than ten days ago. The smoke
  fixture sits at conf ≈ 0.74, well clear of the new floor.
- **JSONL parse hardening.** `EventStore._cached_or_parse()` now
  catches `(OSError, UnicodeDecodeError)` on file read and adds
  a fallback `except Exception` per line so one bad line never
  aborts the rest of the file. Honors the STABILITY.md guarantee.
- **Demo seeder marker now scoped to `base_dir`.** Fixes a smoke-
  test breakage where seeding into a test temp dir tried to
  write the marker to the user's real `~/.recall/events-demo/`.
- **Dead-code sweep — web.** Ten orphan marketing-page components
  (`BuiltForThinkers`, `Demo`, `HowItWorks`, `LauncherMockup`,
  `MemoryReconstruction`, `MemoryVisualization`, `Privacy`,
  `Problem`, `QRBlock`, `TrustBadges`) moved to
  `archive/web-components/`. Web build size unchanged (tree-
  shaking was already excluding them); source tree shrinks by
  ~1.5 K LOC.
- **AUDIT_REPORT.md** — Phase 4C resolution ledger added at the
  top; new findings 4C.1 / 4C.2 / 4C.3 documented with **[FIXED]**
  status.

### Added — Phase 4B (Public Readiness)
- **Pseudo-monorepo restructure.** `apps/{web,docs,extension,desktop}`,
  `packages/{shared,design-system,contracts}`, `infra/{installers,
  release,scripts}`, `assets/{screenshots,branding,demos}`, and
  `archive/` are now the top-level layout. The non-Python trees
  (web, docs, extension, scripts) migrated immediately; the Python
  desktop tree stays at the repo root until cross-platform
  PyInstaller verification clears — see
  [`apps/desktop/README.md`](../../apps/desktop/README.md).
- **`ROOT_ARCHITECTURE.md`** — runtime topology, dependency graph,
  release ownership, future extraction paths.
- **`REPO_STRUCTURE.md`** — why pseudo-monorepo before split, per-
  directory gate conditions, package boundaries, contributor
  guidance.
- **`apps/core/demo_seed.py`** (currently at `app/core/demo_seed.py`)
  — deterministic event-log seeder for `RECALL_DEMO_MODE=1`. Writes
  ~30 events spanning four overlapping stories (websocket retry
  debugging, RLHF research, healthcare startup, casual browsing) so
  the launcher's idle digest lights up with `Continue where you
  left off` / `Active memory threads` / `On your radar` content on
  a fresh capture. Idempotent within a seed version.
- **`assets/demos/demo-script.md`** — the canonical 90-second
  walkthrough (three acts, one restoration moment, exact click
  sequence + narration).
- **`FIRST_IMPRESSION_AUDIT.md`** — five-persona simulated audit
  (HN reader, YC partner, systems engineer, privacy developer,
  productivity enthusiast). Includes a re-running checklist for
  future copy changes.
- **`.github/ISSUE_LABELS.md`** — canonical 24-label set across
  `kind/*` `area/*` `priority/*` `status/*` plus first-impression
  flags. Bootstrap commands for a public repo.
- **README stubs** in `packages/`, `infra/installers/`,
  `infra/release/`, `assets/screenshots/`, `assets/branding/`,
  `assets/demos/`, `archive/`, and `apps/desktop/`.

### Changed
- All path references across `README.md`, `CLAUDE.md`,
  `CONTRIBUTING.md`, `RELEASE.md`, `SECURITY.md`, and
  `infra/scripts/dev.{ps1,sh}` updated to the new layout.

### Deferred
- Python desktop tree relocation to `apps/desktop/` (gated on
  cross-platform PyInstaller verification).
- Real product screenshots (gated on a maintainer running the
  launcher in demo mode and capturing the list in
  `assets/screenshots/README.md`).
- Demo video production (gated on the demo script being captured
  per `assets/demos/demo-script.md`).
- Public GitHub issue-label bootstrap (gated on the repo going
  public).

### Added — Phase 4A (Productization)
- `CHANGELOG.md`, `VERSIONING.md`, and `RELEASE.md` to anchor the
  release lifecycle.
- `docs/architecture/visual-system.mdx` codifying the project's
  spacing / typography / motion / elevation / colour scales.
- `docs/troubleshooting.mdx`, `docs/faq.mdx`, and
  `docs/install-validation.mdx`.
- Empty-state strings in the launcher digest sections (recovery,
  threads, resurfacing) so the surface never reads as "broken"
  on a fresh install.
- Landing-page `ContinueWorking` surgical refinement (icon-chip
  rows, `Restored` pill, `Ctrl + Space` kbd chip in the launcher
  mockup header, footer `12 active threads` status line).

### Changed
- Repository charter (`CLAUDE.md`) extended with productization
  rules: error-handling discipline, empty-state requirements,
  trust-surface conventions.
- README repositions Recall as a *local-first continuity
  operating system* (was: *cognitive continuity system*).

### Deferred
- Signed Windows installer build (needs code-signing cert +
  pipeline tooling — documented in `RELEASE.md`, not yet
  produced).
- Repository split into `recall-core` / `recall-extension` /
  `recall-web` / `recall-docs` (large operation, documented in
  `RELEASE.md` § "Repo split plan").
- Real product screenshots (need an actual product run — capture
  list in `docs/install-validation.mdx`).
- Auto-update mechanism implementation (architecture documented
  in `RELEASE.md`).

## [0.1.0] — Phase 1A through 3C (initial build, pre-public)

Recall's first complete vertical: events → sessions → contexts →
resurfacing → threads → evolution → recovery, plus a unified
`/v1/*` HTTP API, a PyQt6 launcher, a Chrome MV3 extension, a
Mintlify docs site, and a Next.js marketing site. All locally
sourced; no cloud, no telemetry.

### Engine layers shipped
- **Phase 1A** Event log (`app/core/events.py`) — append-only
  JSONL at `~/.recall/events/YYYY-MM-DD.jsonl`.
- **Phase 1E** Session reconstruction (`app/core/sessions.py`).
- **Phase 1F** Micro-contexts (`app/core/microcontexts.py`).
- **Phase 2A** Unified local memory API (`api/`) at
  `127.0.0.1:4545`. Loopback-only, no auth.
- **Phase 2B** Resurfacing (`app/core/resurfacing.py`) and the
  launcher's "On your radar" digest section.
- **Phase 2C** Memory threads (`app/core/threads.py`) and the
  thread identity cache at `~/.recall/threads.json`.
- **Phase 3A** Thread evolution (`app/core/evolution.py`).
- **Phase 3B** Continuity recovery (`app/core/recovery.py`) and
  the launcher's primary "Continue where you left off" surface.
- **Phase 3C** Recovery polish: deterministic preview captions,
  orchestrated restoration plans (files → chats → tabs →
  searches), tightened false-positive suppression, the
  `RECALL_EXPLAIN_RECOVERY=1` debug mode, and the
  `SessionTimelineCard` widget.

### Other surfaces shipped
- Chrome / Edge MV3 extension (`extension/`) that posts to the
  `/v1/events/*` endpoints.
- Marketing site (`web/`) — Hero / Architecture /
  EvolutionTimeline / ContinueWorking / Features /
  LocalFirstTopology / FAQ / FinalCTA.
- Docs site (`docs/`) with architecture pages for every engine
  layer.
- 29-section smoke test (`_smoke_api.py`) covering ingestion,
  retrieval, reconstruction, replay, resurfacing, threads,
  evolution, recovery, and per-endpoint perf budgets.

---

[Unreleased]: ../../compare/v0.1.0...HEAD
[0.1.0]: ../../releases/tag/v0.1.0
