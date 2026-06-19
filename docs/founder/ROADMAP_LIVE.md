# ROADMAP_LIVE.md — what's being built, and what isn't

A living board. Four columns. **Never** is as load-bearing as the
other three — it is the public record of what Recall refuses to
become, so scope creep has somewhere to die.

Pairs with [`PHASE_TRACKER.md`](PHASE_TRACKER.md) (build state).

---

## Now

*In the current phase.*

- **Phase 8E — Alpha Users + Evidence Loop**
  (this phase). *Put Recall in front of humans ·
  no product work · no launcher work · no
  extension redesign · no new features.* The
  receiving end of the cohort evidence loop
  ships: alpha pack
  ([`alpha/pack/`](../../alpha/pack/WELCOME.md)
  — 7 docs covering install → browse → leave →
  return → resume → report), user ledger
  ([`alpha/users_live.json`](../../alpha/users_live.json)
  — 9 PII-free fields), daily review CLI
  (**`recall alpha review`** — ASCII-only board
  reading 3 sources), failure loop
  ([`alpha/failures/`](../../alpha/failures/README.md)
  with 1 real incident filed), wow collection
  ([`alpha/wow/`](../../alpha/wow/README.md) —
  verbatim-only), and an explicit RC evidence
  index
  ([`RC_VALIDATION.md`](../release/RC_VALIDATION.md)
  — all 6 RC1 claims backed by checked-in
  artifacts). **Two scores now:** **RC1 product
  87 → 90** (RC-tag threshold), **Alpha
  evidence 30** (new dimension; failure 1/1 met,
  users 1/5, recoveries 0/3, wow 0/1).
  Combination interpretation: *RC ready · cohort
  recruitment is next phase*. Capstone:
  [`PHASE_8E_STATUS.md`](../../archive/phase-status/PHASE_8E_STATUS.md).
  Verdict: **infrastructure ready, cohort empty
  — Phase 8F fills it.**

- **Phase 8D — Release Candidate (RC1)**
  (previous). *Freeze product · no new features · no
  redesign · no cleanup · only ship preparation.*
  Recall becomes **v0.1.0-rc1**. 8 surfaces frozen
  (launcher · extension · capture · resume ·
  control room · doctor · demo · installer) per
  [`VERSION.md`](../release/VERSION.md). Release kit
  ships under [`release/`](../release/rc1): README,
  CHANGELOG_RC1, INSTALL, QUICKSTART, DEMO_FLOW,
  KNOWN_ISSUES, LANDING_CHECK. Screen freeze
  reduces `assets/screenshots/` to 4 canonical
  dirs ([`SCREEN_INDEX.md`](../product/SCREEN_INDEX.md));
  3 dirs + 11 root PNGs archived to
  `archive/screenshots-history-rc/`. New CLI
  **`recall demo run / reset / status`** + 98-line
  [`app/core/demo_cli.py`](../../app/core/demo_cli.py)
  dispatcher; seeds deterministic 30-event trace
  to `~/.recall/events-demo/` (isolated from real
  log); documented in [`DEMO_MODE.md`](../product/DEMO_MODE.md).
  Install walk verified ([`INSTALL_VERIFIED.md`](../release/INSTALL_VERIFIED.md)):
  doctor 5 GREEN / 0 RED, capture status 36
  events today, daemon endpoints all 200 (103 /
  122 / 60 ms). Landing page: zero dead links
  ([`release/LANDING_CHECK.md`](../release/rc1/LANDING_CHECK.md)).
  Bug ledger re-classified to RC1 gate: **P0 = 0**
  (down from 1 at 8C close); 3 P1 must-fix-before
  -alpha + 2 P2 can-wait + 3 blocked. **Release-
  readiness composite: 87/100** (up from 76; target
  was 85+; achieved). Path to 92 (stable tag) is
  5 named follow-ups totalling ~2.5 days. Capstone:
  [`PHASE_8D_STATUS.md`](../../archive/phase-status/PHASE_8D_STATUS.md).

- **Phase 8C — Product Stabilization + Reality Pass**
  (previous). *No new features · no redesign · no
  cleanup · no archives.* Goal: make Recall reliable
  through measurement + honest documentation. 9
  deliverables: [`STABILITY/PERF.md`](../engineering/stability/PERF.md),
  [`STABILITY/CAPTURE.md`](../engineering/stability/CAPTURE.md),
  [`STABILITY/LAUNCHER.md`](../engineering/stability/LAUNCHER.md),
  [`STABILITY/RESUME.md`](../engineering/stability/RESUME.md),
  [`STABILITY/EXTENSION.md`](../engineering/stability/EXTENSION.md),
  [`STABILITY/CONTROL.md`](../engineering/stability/CONTROL.md),
  [`BUGS_OPEN.md`](../engineering/BUGS_OPEN.md),
  [`RELEASE_READINESS.md`](../release/RELEASE_READINESS.md) +
  one P0 regression fix. Caught and fixed in-flight:
  8B's archive sweep over-reached — `app/main.py`
  imports `demo_data`, `app/ui/onboarding.py` +
  `settings.py` import `styles`. Restored
  `demo_data.py` + `styles.py` + `widgets.py` +
  `cards.py` and made the demo_data import lazy
  (`main.py:392`). Measurements: launcher construct
  84.5 ms warm / ~460 ms cold, CLI commands
  230–365 ms, resume preview 3.1 ms, daemon endpoints
  all 200, 6 threads / 5 contexts / 4 resurfacing on
  208-event store; capture pipeline writes real
  events (166 browser events / 30d — ChatGPT 20,
  GitHub 16, Google 55) with StackOverflow + Stitch
  showing 0 (matcher audit needed); extension bundle
  byte-identical at 296 KB; control room TypeScript
  exits 0 across 13 routes + 10 loaders. **Release-
  readiness composite: 76/100** (preview-shippable;
  stable tag needs the 5 highest-value follow-ups
  for ~92).

- **Phase 8B — Tier 1 Cleanup + Repo Collapse**
  (previous). Execute the 8A audit's tier-1 recommendations.
  No feature work · no launcher rewrites · no UI changes
  · no new docs except the 5 cleanup audit docs. **Result:
  Python LOC −24 % (29,544 → 22,435 = −7,109 lines moved
  to archive), asset PNGs −54 % (102 → 47), asset folders
  −58 % (19 → 8), extension components −73 % (11 → 3),
  `app/ui` live files −55 % (11 → 5)**. **No code
  deleted** outside dep entries + 7 stale root PNGs;
  everything else is move-to-archive (recoverable).
  Concrete moves: (1) **Launcher collapse** — 8 legacy
  modules (`launcher_legacy.py`, `cards.py`, `widgets.py`,
  `styles.py`, `launcher_anims.py`, `launcher_digest.py`,
  `demo_data.py`, `ceremonies.py`) + 3 historical capture
  scripts → [`archive/launcher-old/`](../../archive/launcher-old);
  `app/ui/launcher.py` collapsed from 60→18 lines (no
  more `RECALL_LAUNCHER=legacy` branch); the import
  contract `from app.ui.launcher import Launcher` still
  resolves to `LiveLauncher`. (2) **Asset cleanup** — 11
  historical capture folders (`launcher-live/` ·
  `launcher-minimal/` · `launcher-refined/` ·
  `launcher-compact/` · `launcher-recovery/` ·
  `launcher-reset/` · `launcher-visible/` ·
  `launcher-truth/` · `launcher-ship/` · `launcher-final/`
  · `launcher-merge/`) → `archive/screenshots-history/`;
  7 stale orphan PNGs in `assets/screenshots/` deleted
  outright (`control-room.png` · `doctor-output.png` ·
  `installer-flow.png` · `settings-dialog.png` ·
  `launcher-first-week.png` · `launcher-loading.png` ·
  `launcher-offline.png`). (3) **Extension pre-7A
  components** — 8 dead files (`ContinueCard`,
  `DebugStrip`, `DemoBanner`, `InvestigationCard`,
  `MemoryList`, `Section`, `TrustSurface`, `states`) →
  [`archive/extension-pre-7a/`](../../archive/extension-pre-7a);
  vite build proves they were already tree-shaken (293 KB
  JS bundle unchanged). (4) **Dependency cleanup** — 3
  unused deps removed from `apps/web/package.json`
  (`clsx`, `lucide-react`, `tailwind-merge`); `playwright`
  moved from `dependencies` → `devDependencies` in
  `apps/extension/ui/package.json`. **Deferred** to 8C:
  5 orphan API routes (`thread_forget`, `contexts/recent`,
  `sessions/recent`, `threads_clear_evolution_cache`,
  `replay_day`) — kept until associated pydantic schemas
  can be walked cleanly. 5 new audit docs land under
  [`AUDIT/`](../../archive/AUDIT): `DELETE_PLAN.md` (per-row
  delete log w/ verification), `LAUNCHER_FREEZE.md`
  (official launcher path + public API + allowed /
  forbidden changes — *no more launcher generations*),
  `DEPENDENCY_DIFF.md` (before/after manifests + build
  impact), `ASSET_FREEZE.md` (frozen active asset
  surface), `PHASE_8B_STATUS.md` (capstone). `DOC_INDEX.md`
  updated. Verification: `pyflakes app/ui app/core api`
  clean · `recall doctor` GREEN on config/events/daemon/
  extension/installer · `recall capture status` clean
  (11 events today, 12 investigations) · offscreen
  `Launcher(FakeEngine())` constructs at `(700, 500)` ·
  TypeScript clean across all 3 frontend apps ·
  `vite build` of extension produces 293 KB JS bundle
  (identical to 8A — proves dead components were already
  tree-shaken). Success bar: **repo smaller. Same
  product. No regressions.**

- **Phase 8A — Full Product Audit** (prior phase, this session).
  *Stop building features.* Understand what Recall
  actually is today. No launcher redesign, no extension
  redesign, no control-room redesign, no new memory
  systems, no new phases. 7 audit docs land under a new
  top-level [`AUDIT/`](../../archive/AUDIT) folder, each
  evidence-based (file path + line number + grep
  result), each cross-linked to the others, each citing
  consumers + status: (1)
  [`SURFACES.md`](../../archive/AUDIT/SURFACES.md) inventories
  every runtime surface — 36 LIVE, 2 LEGACY (legacy
  launcher tree + pre-7A extension components), 11
  ARCHIVE, 1 REMOVE (auto-update, n/a); (2)
  [`DEAD_CODE.md`](../../archive/AUDIT/DEAD_CODE.md) catalogues
  parallel trees + duplicates + orphans — 8 truly DEAD
  (pre-7A extension components), 7 LEGACY (behind
  `RECALL_LAUNCHER=legacy` escape hatch), 3 duplicate
  widget pairs + 1 duplicate confidence-logic pair, 5
  orphan API routes (`thread_forget`, `contexts/recent`,
  `sessions/recent`, `threads_clear_evolution_cache`,
  `replay_day`); (3)
  [`LAUNCHER_MAP.md`](../../archive/AUDIT/LAUNCHER_MAP.md)
  traces every signal + slot + public method through
  the launcher; documents the class graph + frozen
  anti-rules (mirrors `LAUNCHER_CONTRACTS.md` from
  7E.1) + the state-flow per refresh + the "one
  launcher" collapse path; (4)
  [`CAPTURE_MAP.md`](../../archive/AUDIT/CAPTURE_MAP.md) cross-
  checks the 7D `CAPTURE_FLOW.md` against actual code,
  lists the diagnostic CLI per failure mode, captures
  live measurement (8 events today, 11 investigations,
  last event 38m ago — ChatGPT/Google/Stitch all
  present); (5)
  [`ASSETS.md`](../../archive/AUDIT/ASSETS.md) inventories
  every PNG under `assets/screenshots/` — 5 ACTIVE
  folders + the live `launcher-7e/` ⭐ + the live
  `extension-7a/` ⭐ + 11 HISTORICAL folders + 7
  root-level ORPHAN PNGs flagged for tier-1 delete;
  (6) [`DEPENDENCIES.md`](../../archive/AUDIT/DEPENDENCIES.md)
  classifies all 43 packages across `requirements.txt`
  + 3 `package.json` files — 20 runtime, 19 dev, 3
  unused (`clsx`, `lucide-react`, `tailwind-merge` in
  marketing web), 1 misplaced (`playwright` in
  extension's `dependencies` instead of
  `devDependencies`); (7)
  [`STATE.md`](../../archive/AUDIT/STATE.md) is the capstone —
  what Recall *is* + what ships + what's dead + what
  survives + tier-graded delete recommendations + live
  verification (`doctor` GREEN on daemon/events/extension,
  `capture status` clean, `founder status` 78%
  continuity restored / 134 investigations,
  TypeScript clean across all 3 apps, offscreen
  launcher boots cleanly at 700×500). `DOC_INDEX.md`
  updated with a new `/AUDIT/` section at the top so
  the audit docs are reachable from the standard doc
  index. Three parallel `Explore` subagents gathered
  the underlying evidence (dead-code audit · asset
  audit · dependency audit); the launcher/capture/state
  docs were authored against the agents' raw findings.
  **No deletions performed.** **No code changed.** This
  is the audit phase, not a feature phase. Success bar:
  *understand entire repo. No more accidental building.
  No more launcher rewrites. No more code slop.*

- **Phase 7E.1 — Launcher Stability** (prior phase, this session).
  *Launcher boots every time.* No visual work, no redesign
  — audit the public Python interface, restore the pieces
  the 7E paint rewrite silently dropped, freeze the
  contract. The 7E rewrite of `MinimalSearchBar` removed
  the `request_settings` + `request_close` signals while
  `LiveLauncher.__init__` still called
  `self._search.request_settings.connect(...)` — every
  `python recall.py` crashed with `AttributeError:
  'MinimalSearchBar' object has no attribute
  'request_settings'`. Fix:
  [`minimal.py`](../../app/ui/launcher_v3/minimal.py)
  restores both signals + adds the rest of the documented
  contract (`searchChanged` alias of `query_changed` —
  both fire on text change via two parallel connects on
  `QLineEdit.textChanged`; `submit(str)` already present;
  `clear()` + `selectAll()` methods added). The two
  *may-not-exist* signals (`request_settings`,
  `request_close`) are declared even though no widget in
  7E fires them — consumers `connect(...)` safely; later
  paints can wire an on-screen affordance without touching
  the host. New
  [`LAUNCHER_CONTRACTS.md`](../product/LAUNCHER_CONTRACTS.md)
  documents the frozen interface (per-symbol table +
  wiring map between `app/main.py` → `LiveLauncher` →
  `MinimalSearchBar`) with the freeze rule: *future
  launcher phases may **add** to the surface; they **must
  not remove or rename** the symbols below*. Receipt:
  [`PHASE_7E.1_STATUS.md`](../../archive/phase-status/PHASE_7E.1_STATUS.md).
  Verified: offscreen `LiveLauncher(FakeEngine())`
  constructs cleanly (`CONSTRUCT OK · DEFAULT_SIZE: (700,
  500)`); both signal spellings fire correctly; the
  `request_settings` chain propagates up to
  `LiveLauncher.request_settings.emit`; `python recall.py
  doctor` green on config / events / extension / installer.
  Success bar: *launcher boots every time.*

- **Phase 7E — Launcher Final Product Pass** (prior phase, this session).
  Engine, recovery, extension, control room frozen —
  launcher only. 7B.1 shipped a beautiful single-document
  workspace but solved *floating overlays* by **removing
  memory from the surface**; 7E restores memory while
  honouring the calm-product feel. Canvas **700 × 500**
  (was 740 × 500), warm `#F5F2ED` page outside, one white
  inner card with radius 24 + 20/16/20/14 padding inside.
  **No nested cards, no floating islands, no glass, no
  transparency, no dark backdrop.** Five sections stack
  inside the card with **no per-section chrome**: (1)
  52-px **search bar** with the `Ctrl K` hint chip; (2)
  13-px (9-pt) muted-lavender **tagline** *Recall noticed
  unfinished work* directly under the search; (3)
  **Continue hero** with HIGH/MED/LOW signal variants
  driving the 6-px left accent rail (filled / soft / outline)
  + matching confidence pill, title (elided) + Resume
  button (fixed 116-px, `1` chip) + inline evidence row
  (`2 files - 2 tabs - returned 2d`); (4) **NEW Recent
  Memory section** —
  [`recent_memory.py`](../../app/ui/launcher_v3/recent_memory.py)
  surfaces up to 5 rows from
  `~/.recall/events/YYYY-MM-DD.jsonl` via
  `EventStore.iter_events(days=2)`, mapped to
  `MemoryRow(time, source, label)` records by
  `_short_source` / `_short_label` (ChatGPT / Claude /
  Gemini / Google / DuckDuckGo / Bing / domain title-case)
  — fixes the *memory invisible* problem; (5) **OTHER
  WORK rebuilt** from 7B.1's zero-cost stub into 36-px
  rows with strength dot (lavender if surfaces ≥ 3, ink-4
  otherwise) + title (elided) + last-seen mono caption
  (`3d`/`5d`/`1w`, via `events.humanize_age`), max 3
  rows, 1-px hairline dividers between; (6) **TrustRow**
  pinned at the bottom with 4 tiny pills `LOCAL · NO CLOUD
  · N EVENTS TODAY · M INVESTIGATIONS` — counts derived
  live from the same disk reads the Phase 7D `recall
  capture status` CLI uses, so pill values match the CLI
  report. **Removed**: Show example + Start working giant
  buttons, centered empty states, large vertical spacing,
  floating pills, dark overlays, prototype illustrations.
  3 files snapshotted into
  [`archive/launcher-7b1/`](../../archive/launcher-7b1)
  with per-file README documenting the Stitch-workspace
  era: `minimal_7b1.py` · `recovery_panel_7b1.py` ·
  `investigation_panel_7b1.py`. 5 captures (`home · high
  · med · low · no_hero`) in
  `assets/screenshots/launcher-7e/`. New
  [`LAUNCHER_FINAL.md`](../product/LAUNCHER_FINAL.md)
  **supersedes** `LAUNCHER_VISUAL_MERGE.md` (7B.1) as the
  launcher's live contract — 7B.1 → 7E delta table +
  frozen paint/geometry/typography/per-region tables +
  5-row state catalogue + the removed-list. Receipt:
  [`PHASE_7E_STATUS.md`](../../archive/phase-status/PHASE_7E_STATUS.md).
  Success bar: *open Recall → see unfinished work + recent
  memory + resume path + trust within 3 seconds.* Launcher
  frozen.

- **Phase 7D — Capture Truth Audit** (prior phase, this session). *Verify
  Recall actually remembers.* **No UI, no redesign** —
  engine + CLI + docs only. New
  [`recall capture status`](../../app/core/capture_cli.py)
  CLI prints a read-only ASCII summary of today's pipeline
  state (events today + per-kind breakdown + returns
  ≥ 30-min gap + investigation count + last-event
  timestamp/kind/age). Daemon not required — reads
  `~/.recall/events/YYYY-MM-DD.jsonl` + `~/.recall/threads.json`
  directly off disk; degrades gracefully (`0` instead of
  raising) on a missing threads cache. New
  [`recall capture tail`](../../app/core/capture_cli.py)
  is a `tail -f`-style live inspector that prints existing
  events on start then polls the daily JSONL file at 500-ms
  intervals; each new line lands as one compact `HH:MM:SS
  kind  detail  title` row. Survives the midnight day-roll
  by reopening the file on every tick; `--once` mode prints
  existing events then exits (script-friendly). Both
  commands dispatch from `recall.py`'s fast path before
  `app.main` imports — no Qt boot cost. New
  [`CAPTURE_FLOW.md`](../product/CAPTURE_FLOW.md) documents
  the **seven hops** end-to-end (browser → extension →
  daemon → event store → investigation → recovery →
  launcher), names the file + function that implements
  each hop, lists the CLI that confirms data made it
  through, and closes with a scripted 7-step verification
  walk (ChatGPT / GitHub / StackOverflow / Google → leave
  ≥ 30 min → return → confirm Continue document) plus the
  `recall inspect` follow-up. Live measurement: this
  machine reports 71 events today / 11 investigations /
  ChatGPT + Google + Stitch tabs streaming through the
  tail — pipeline warm end-to-end. Receipt:
  [`PHASE_7D_STATUS.md`](../../archive/phase-status/PHASE_7D_STATUS.md).
  Success bar: *Recall truly remembers — and now you can
  prove it.*

- **Phase 7B.1 — Launcher Visual Merge** (prior phase, this session).
  *Rebuild launcher toward the Stitch reference. Current
  launcher discarded visually. Keep logic, replace surface.*
  7B locked the launcher to *one root card* with three
  regions inside but at product distance the Raycast-shaped
  density still read as *utility*. The Stitch reference
  proves a calmer **document workspace** shape works
  better — and the new launcher follows it. Canvas grows
  to **740 × 500** (hard clamp, single white workspace,
  16-px gutter, radius 22) on the warm `#F4F1EC` page —
  no transparency, no glass. New **search bar** at the top
  (52 px, warm-paper fill, hand-drawn glyph, **settings
  cog + close × + Ctrl K hint** on the right, placeholder
  **`Start typing to recover…`**). **Continue document**
  replaces the dense hero row: 220-px calm card with a
  6-px lavender accent rail, `CONTINUE` eyebrow, 14.5-pt
  bold title (elided), bulleted body (file/tab/chat/search
  counts + the engine's *returned after Nd* clause when
  `preview_caption` carries one — pulled via a new
  `_extract_gap_clause` helper in `live.py`), and a
  right-aligned fixed-width 116-px Resume button with the
  `1` shortcut chip — reads as a *document with an action*,
  not a command-palette row. **Empty workspace** rebuilt:
  infinity lemniscate glyph (two overlapping ellipses + a
  warm halo, painted via `QPainter`) + 20-pt bold headline
  *Everything you've seen, searchable.* + 14-px sub *Your
  digital continuity layer.* + two stacked 200-px buttons
  (*Show example* accent-filled + *Start working* outline).
  **Bottom strip** replaces the centred footer: 22-px row
  with the trust line *End-to-end encrypted. Local storage
  only.* on the left + tiny `Privacy · Demo · Docs ·
  Browser` text links on the right. **OTHER WORK list
  removed** from the visible surface — single-focus tool;
  `InvestigationCardV3` + `InvestigationList` reduced to
  zero-cost stubs so the engine path stays live while the
  launcher never renders. Hotkeys: kept Esc / Ctrl+K /
  Cmd+K / `1`; removed 2-9 (nothing to navigate to). 3
  files snapshotted into
  [`archive/launcher-raycast/`](../../archive/launcher-raycast)
  with per-file README documenting the per-section/raycast
  command-palette era: `minimal_7b.py` ·
  `recovery_panel_7b.py` · `investigation_panel_7b.py`. 5
  new captures (`empty · active · resume · demo ·
  overflow`) in `assets/screenshots/launcher-merge/`. New
  [`LAUNCHER_VISUAL_MERGE.md`](../product/LAUNCHER_VISUAL_MERGE.md)
  **supersedes** `LAUNCHER_SHIP_AUDIT.md` (7B) as the
  launcher's live contract — carries 7B → 7B.1 delta
  table + frozen paint/geometry/typography/per-region
  tables + 5-row state catalogue. Receipt:
  [`PHASE_7B.1_STATUS.md`](../../archive/phase-status/PHASE_7B.1_STATUS.md).
  Success bar: *Looks like product. Not utility.*

- **Phase 7B — Launcher Production Freeze** (prior phase, this session).
  *Turn the launcher into shipping product.* No new
  features, no control room, no extension, no alpha, no
  docs except the audit. The launcher is now a **shipping
  product**. 6R froze the layout cleanly but kept the
  per-section card pattern — search bar, hero, and OTHER
  WORK each painted their own bordered, shadowed white card
  on the warm-paper page — and at arm's length that read
  as *three floating overlays*, not as *one product
  object*. The 7B directive lists *visibility · weak
  hierarchy · prototype feel · floating overlays · poor
  empty state* as the problems and asks for a single
  cohesive root surface. **Surface architecture**: the
  680 × 440 hard-clamp window now paints the full-bleed
  warm page (`#F4F1EC`) then a **single white root card**
  with radius 22 inside a 14-px outer margin (with a
  manual two-offset-rounded-fill shadow that replaces the
  prior `QGraphicsDropShadowEffect` so the launcher's hot
  path stays off the software rasterise route). The root
  card carries 20-px internal padding. **Search bar**
  rewritten to a 52-px row with a **warm-paper fill**
  (`#F4F1EC`) inside the white root + 2-px warm-grey
  border + lavender focus ring + hand-drawn `_SearchIcon`
  + inline `Ctrl K` hint chip (hidden on focus). **Hero
  rewritten — no card chrome**: fixed 88-px height, only
  the 6-px lavender left accent rail (rounded ends),
  brighter rail + 1-px lavender focus ring when keyboard-
  focused; title row (title elided + tiny `HIGH` pill +
  **fixed-width 112-px Resume button**) + chips row
  beneath (max 3, derived from `suggested_targets`).
  **OTHER WORK list — no wrapping card**: rows paint
  directly on the root with 1-px hairline dividers
  between, max 3 visible. Footer (*local only · no cloud*)
  pinned at the bottom of the root card. New
  **Ctrl/Cmd+K** focuses + selects-all the search input
  from anywhere inside the launcher via two QShortcuts.
  New **`RECALL_DEBUG=1` timing log** writes one line per
  `show_centered` to stderr (*"[recall.launcher.timing]
  show_centered  N ms  (budget 400)"*) so the directive's
  *<400 ms launcher open* budget can be confirmed on a
  real machine. New
  [`capture_launcher_ship.py`](../../infra/scripts/capture/capture_launcher_ship.py)
  produces 5 PNGs (`hero · empty · focus · demo ·
  overflow`) in `assets/screenshots/launcher-ship/`. New
  [`LAUNCHER_SHIP_AUDIT.md`](../product/LAUNCHER_SHIP_AUDIT.md)
  **supersedes** `LAUNCHER_FINAL_AUDIT.md` (6R) as the
  live contract — carries the 6R → 7B delta table +
  frozen paint/geometry/motion/per-region tables + 9-row
  visibility-pass table + 2-row performance-budget table +
  the explicit *Launcher frozen forever* freeze rule. 3
  files snapshotted into
  [`archive/launcher-final/`](../../archive/launcher-final)
  with per-file README documenting the per-section-card
  era: `minimal_6r.py` · `recovery_panel_6r.py` ·
  `investigation_panel_6r.py`. Receipt:
  [`PHASE_7B_STATUS.md`](../../archive/phase-status/PHASE_7B_STATUS.md).
  Success bar: *open Recall · see remembered work · press
  Resume · leave*.

- **Phase 7A — Extension Product Surface** (prior phase, this session).
  *Stop launcher · control room · founder tooling · docs ·
  alpha dashboards.* **Only extension.** Make Recall's
  extension feel premium — reference Arc / Raycast / Linear
  / Readwise Reader / Perplexity sidebar. Popup frozen at
  **440 × 640** (`body { width / height; overflow: hidden }`,
  `#root` matched). Six fixed-position regions in a single
  column: Header (mark + breathing daemon dot + *Connected
  locally* subtitle + Search/Settings buttons) → Continue
  hero (full-width white card, 6-px lavender accent rail,
  `HIGH` confidence pill, 112-px Resume with the `1`
  shortcut chip, max 3 derived chips, capped at 110 px tall)
  → Active investigations (vertical stack of 48-px rows
  inside one white card with strength dot + title + last-seen
  + chevron, max 4 visible) → Today timeline (3-column grid:
  mono time / bold source / label · empty rail surfaces a
  dashed-border illustration in place of the *"No browser
  memory captured yet"* prose) → Activity status (Browser
  card with `capturing / idle / offline` pill listing *tabs ·
  navigation · returns · searches*; Desktop card with
  `capturing / soon / offline` pill listing *files · editors
  · integrations* — the *Design UI now. Engine later.* seam
  surfaced honestly) → Trust strip (4 tiny pinned pills
  `LOCAL ONLY · NO CLOUD · 0 UPLOADS · DAEMON OK`, replaces
  the prior ~140-px `TrustSurface` section). Plus a
  **SearchOverlay** that slides down on **Ctrl/Cmd+K**
  listing matches across *Investigations · Files · Returns
  · Events* (in-memory filter for now; the directive's
  *Design UI now. Engine later.* applies — swap
  `useResults` when a unified endpoint lands). New design
  tokens: **page `#F5F2ED`** (warm paper), card `#FFFFFF`,
  hairline `#E6DED4`, shadow `0 12 32 rgba(0,0,0,.06)` —
  *no glass, no neon, no blur*. Motion scale tightened to
  the directive's exact **120 / 180 / 240** via
  `--motion-fast/normal/slow`. Eight new components under
  `apps/extension/ui/src/components/v2/` (`Header`,
  `Hero`, `Investigations`, `Timeline`, `Activity`,
  `TrustStrip`, `SearchOverlay`, `States`); `App.tsx`
  rewritten to compose them while preserving the existing
  state machine + API client + demo overlay flow untouched.
  `capture_extension.mjs` gains an `OUT_7A` directory + 7
  fixtures (the directive's `empty · capturing · active ·
  resume · offline · search · demo` audit row) — the
  `search` capture fires Ctrl+K via Playwright keyboard so
  the overlay paints in the screenshot. New
  [`EXTENSION_PRODUCT_AUDIT.md`](../product/EXTENSION_PRODUCT_AUDIT.md)
  is the frozen-product checklist (paint table · motion
  table · per-region contracts · 7-row state catalogue
  with one capture per row). Receipt:
  [`PHASE_7A_STATUS.md`](../../archive/phase-status/PHASE_7A_STATUS.md).
  Success bar: *open extension → immediately understand
  Recall remembered work · Recall can continue it · Recall
  is running*.

- **Phase 6R — Launcher Finalization** (prior phase, this session).
  *Stop feature work. Only launcher. Make it feel like
  shipped software.* No docs (besides the audit + status). No
  trust system. No recovery ranking. No control room. No
  extension. The launcher is now a **frozen product surface**;
  no more launcher phases after this. Window **680 × 440**,
  hard clamp (`setFixedSize`, min = max, no resize),
  `WA_TranslucentBackground = False` — *no glass, no blur, no
  floating opacity tricks*. Page warms to **`#F4F1EC`**; new
  `BORDER_RAISED_STRONG = #E7DED3` carries the 2-px search-bar
  border; new `SHADOW_SEARCH_* = 0 8 24 rgba(0,0,0,.06)`
  scales the search shadow under the existing
  `SHADOW_CARD_* = 0 12 32 rgba(0,0,0,.08)` so the search bar
  reads beneath the hero in z-order despite painting at the
  top of the column. **Search bar** rewritten: 52 px tall,
  radius 14, lavender focus ring, hand-drawn
  magnifying-glass icon (`_SearchIcon` — no Unicode glyph
  dependency), placeholder *Search work…*. **Hero card**
  rewritten: fixed 88 px height, **6-px lavender left accent
  strip** clipped to the rounded border, title (one line,
  elided with `...`) + tiny **HIGH** confidence pill +
  **fixed-width 112-px Resume button** (`_ResumeButton.WIDTH`)
  + a max-3 chip row beneath the title derived from
  `suggested_targets` via `_chips_from_targets` (same buckets
  the resume preview uses). **Removed from the hero**:
  subtitle, meta caption, prose, *Why this?* link, the
  `signals` parameter, the `request_why` signal. **OTHER
  WORK** rewritten: vertical list (was horizontal in 6O), 44
  px tall rows with lavender 6-px dot + title + quiet
  right-pointing chevron (painted, not glyph), max 3 rows,
  white card wrapper with 1-px inter-row dividers — *the
  horizontal row read as adrift text at arm's length; the
  vertical list reads as a list of things you can click*.
  **Empty surface** restacked: lavender square · headline
  *Recall notices unfinished work* · **Show example**
  (primary, accent-filled) · **Start working** (secondary,
  layered card; renamed from *Start normally* per directive)
  — both buttons 200-px fixed width, **inside the centred
  stack**, not floating page furniture. New single-line
  **footer** *local only · no cloud* at the bottom of every
  surface (populated + empty), ~10 px ink-3, centred. New
  [`capture_launcher_final.py`](../../infra/scripts/capture/capture_launcher_final.py)
  produces 4 PNGs in `assets/screenshots/launcher-final/`
  (`hero` · `empty` · `focus` · `overflow`). New
  [`LAUNCHER_FINAL_AUDIT.md`](../product/LAUNCHER_FINAL_AUDIT.md)
  carries the frozen-product checklist (geometry table · paint
  table · hero / OTHER WORK / empty / footer contracts · the
  7-check visibility audit covering arm-length / dark-room /
  50 % / 125 % scaling / title overflow / empty / demo /
  resume / the freeze rule). Four files snapshotted into
  [`archive/launcher-debt/`](../../archive/launcher-debt) with
  a per-file README: `minimal_6p1.py` (6P.1 visibility surface)
  · `recovery_panel_6q.py` (6Q hero with the *Why this?* link)
  · `investigation_panel_6o.py` (6O horizontal row) ·
  `why_sheet_6q.py` (6Q signal overlay). The engine-side
  signals layer (`recovery.explain_signals` + `recall inspect`
  + `bad_recoveries`) **stays in active code** — only the
  launcher's surface changed. Receipt:
  [`PHASE_6R_STATUS.md`](../../archive/phase-status/PHASE_6R_STATUS.md).
  Success bar: **open Recall · understand instantly · click
  Resume · done**.

- **Phase 6Q — Continuity Truth** (prior phase, this session). *Make Recall
  feel correct. Not pretty. Not bigger. **Correct.*** No
  launcher redesign, no extension redesign, no control-room
  work — investigation quality only. Three layers shipped:
  (1) the canonical contract — new
  [`INVESTIGATION_PRINCIPLES.md`](../product/INVESTIGATION_PRINCIPLES.md)
  codifies the 7 rules (*same topic returns → merge · one-off
  visit → suppress · passive browsing → suppress · deep work
  → promote · unfinished work → strongest signal · multi-day
  return → boost · casual reopen loops → decay*) and the 9
  trust-floor gates in `recovery.py`; new
  [`PROMOTION_THRESHOLDS.md`](../product/PROMOTION_THRESHOLDS.md)
  documents the LOW/MED/HIGH bands (0-1 / 2-3 / 4+ targets)
  plus 5 overrides — *unfinished overrides all · returned_after_gap
  boosts +1 · duplicate penalty · noise penalty · ledger
  penalty*. (2) The user-feedback loop — new
  [`bad_recoveries.py`](../../app/core/bad_recoveries.py)
  ledger writes to `~/.recall/bad_recoveries.jsonl` (closed
  4-reason enum: `wrong_topic` · `already_done` · `noise` ·
  `duplicate`; trust contract: no content, only `thread_id` +
  `reason` + `ts`), engine surfaces `signals.ledger_flagged`
  on flagged threads, launcher honours by skipping HIGH
  promotion within the 14-day window. (3) The introspection
  surface — new `recall inspect <id>` CLI prints a
  deterministic ASCII card (Title · Strength · Signals ·
  Evidence · Decision); new `recall trust review` CLI prints
  the ledger + bad % / silence % / resume % rates; new
  [`WhyThisSheet`](../../app/ui/launcher_v3/why_sheet.py)
  overlay opens from a small lavender *Why this?* link on the
  hero's meta row and lists `recovery.explain_signals(candidate)`
  verbatim — **no AI text, no prose, no scoring numbers**.
  4 new captures in `assets/screenshots/launcher-truth/`
  (`hero_with_why` · `why_sheet` · `showcase` ·
  `ledger_demoted`). New
  [`SHOWCASE_TRUTH.md`](../product/SHOWCASE_TRUTH.md) carries
  the directive's three-investigation scripted walk (proposal
  · RLHF · WebSocket) verifying *only one hero* + the *Why
  this?* sheet contract + the ledger-demotion path.
  [`archive/recovery-ranking/`](../../archive/recovery-ranking)
  documents what 6Q kept untouched (every gate, every weight),
  what 6Q added (the ledger flag + explain_signals + 2 CLIs +
  the Why sheet), and what 6Q considered and rejected (a
  learned ranker, a second freshness half-life, a chat-heavy
  promotion bump, engine-side duplicate de-dup). Receipt:
  [`PHASE_6Q_STATUS.md`](../../archive/phase-status/PHASE_6Q_STATUS.md).
  Success bar: user says *"Yes. That is exactly what I
  wanted back."*

- **Phase 6P.1 — Launcher Visibility Recovery** (prior phase, this session).
  *Make the launcher immediately visible and usable.* **No new
  features. No recovery logic work. No resume work.** Visual
  correction only. The 6O reset went too far on paint — the
  near-white page (`#F7F5F2`) and white cards differed by ~10 %
  luminance so the surfaces blended into each other, the search
  was a bare input with no chrome, the investigation row was
  bare text adrift, and the empty-state buttons floated below
  the headline with no fixed widths. The launcher read as a
  CSS reset. This phase keeps the 6O structure (680 × 460,
  HIGH-only gate, max-3 investigations) and restores the
  *layering*. Concrete changes: `theme.BG` warms to **`#F3F1ED`**
  (6 % darker than the white cards — enough for layering to
  read at arm's length); new `BORDER_RAISED = #E4DED6` solid
  hairline; new `SHADOW_CARD_* = 0 12 32 rgba(0,0,0,.08)`;
  new `_LayeredCard` base class — white fill + 1-px warm-grey
  border + soft drop shadow — inherited by the search bar
  (radius 14), the recovery hero (radius 22), and the new
  `_InvestigationsCard` wrapper (radius 18) around the OTHER
  WORK row. Search bar now has a hand-drawn
  `_SearchIcon` (`QPainter` circle + handle, no Unicode glyph
  dependency) + lavender focus ring (2-px `T.ACCENT` border on
  `FocusIn`). Hero gains a **soft 4-px lavender left accent
  strip** painted inside the rounded border and a **fixed-width
  110-px Resume button** so the right edge is stable across
  recoveries with different title lengths. Empty state stacks
  **logo dot → headline → sub → buttons** with a 16-px gap and
  two 140-px fixed-width buttons. `MinimalWindow` reserves a
  **12-px outer margin** and paints a 1-px warm-grey border
  around the page at radius 24 so the launcher reads as a
  discrete object. New
  [`capture_launcher_visible.py`](../../infra/scripts/capture/capture_launcher_visible.py)
  produces 4 PNGs in `assets/screenshots/launcher-visible/`
  (hero · empty · focus · investigations). New
  [`LAUNCHER_VISIBILITY.md`](../product/LAUNCHER_VISIBILITY.md)
  carries the directive's *problem · fix · before / after*
  audit (9-row table). Success bar: *Launcher readable from 2
  meters away.*

- **Phase 6P — Resume Reality** (prior phase, this session). *Click Resume.
  Actually continue work.* The pre-6P v3 launcher had a
  one-line `_on_restore` stub that called the API to resolve a
  `RestorationPlan` and then dropped the plan on the floor —
  the user clicked Resume, the launcher silently closed, and
  nothing reopened. This phase wires the click to real OS
  opens. Two new widgets: a light
  [`ResumePreview`](../../app/ui/launcher_v3/resume_preview.py)
  overlay that floats inside the launcher window (Continue + a
  count breakdown *2 files · 2 tabs · 1 search* + Cancel /
  Resume now buttons; Esc cancels) and a
  [`RestoreToast`](../../app/ui/launcher_v3/restore_toast.py)
  that pins to the bottom for 3 s with up to three restored
  target names (*Restored · backoff.py · client.py · MDN*) or
  a calm failure line (*Could not reopen 1 item · Continue
  anyway* / *Could not reach the engine · try again*). The new
  `_on_preview_accept` walks `plan.steps` in the engine's
  prescribed order (files → chats → tabs → searches) and
  dispatches each via `_open_target` (`os.startfile` on
  Windows, `open`/`xdg-open` elsewhere). Missing files are
  skipped + counted, never block the chain. The demo path runs
  through the same preview → toast cycle so the WebSocket
  recovery example reads identically to a live restore. New
  doc trio:
  [`RESUME_FLOW.md`](../product/RESUME_FLOW.md) (end-to-end
  pipeline audit + the *why files first* rationale), the
  [`SHOWCASE_RUN.md`](../product/SHOWCASE_RUN.md) scripted
  verification (step-by-step demo run + failure-injection
  matrix), and the engineering receipt
  [`PHASE_6P_STATUS.md`](../../archive/phase-status/PHASE_6P_STATUS.md).
  The stub `_on_restore` + `_on_demo_resume` were removed and
  documented in [`archive/resume-old/`](../../archive/resume-old).

- **Phase 6O — Launcher Reset** (prior phase). The launcher
  overbuilt across 6I → 6N — multi-state heroes, confidence
  sentences, preview cards, returns rows, sort priorities.
  The reset directive deletes everything that doesn't support
  one of two actions: **resume the recovery** or **dismiss and
  start fresh**. Window **680 × 460**, paper white, radius 24,
  soft shadow only. Single column: search at top (capped
  620 px, centred) → CONTINUE section + 100-px fixed hero
  (when HIGH only) → OTHER WORK section + up to 3 bare-text
  investigation titles. Or — when no HIGH recovery — centred
  headline *Recall notices unfinished work* + body *Work
  normally. / Return later.* + *Show example* / *Start
  normally* buttons. **No returns row, no trust line, no
  confidence sentence, no MED/LOW signal variants, no preview
  card, no status indicators, no overflow chip, no chip
  parser, no sort priority, no footers.** Six files moved to
  `archive/launcher-overbuild/` (the prior `minimal.py`,
  `recovery_panel.py`, `investigation_panel.py`, `digest.py`,
  + the 6M.2 & 6N capture scripts). The remaining three v3
  modules rewritten from scratch around the directive's spec.
  `LiveLauncher` gates the hero on `n_targets ≥ 4` and falls
  through to the empty surface otherwise. New
  [`capture_launcher_reset.py`](../../infra/scripts/capture/capture_launcher_reset.py)
  produces 2 PNGs (populated · empty) in
  `assets/screenshots/launcher-reset/`. Two new docs:
  [`LAUNCHER_RESET.md`](../product/LAUNCHER_RESET.md)
  (the directive's *what removed · why launcher failed · new
  philosophy* audit — 3 failure modes, 3 design rules) +
  [`PHASE_6O_STATUS.md`](../../archive/phase-status/PHASE_6O_STATUS.md).

- **Phase 6N — Recovery Precision** (prior phase). The launcher
  *feels intelligent*. **No redesign. No geometry changes. No
  control-room work.** Recovery experience only. `RecoveryCardV3`
  gains a `signal` parameter with three states: **HIGH** →
  *Resume* (accent-filled pill, accent-soft fill, sentence
  *"Recall thinks this was interrupted work"*); **MED** →
  *Continue* (accent-soft pill + accent border, halfway-tinted
  fill, sentence *"Seen again after return"*); **LOW** →
  *Review* (ghost outline pill, plain white fill, sentence
  *"Weak signal — review first"*). `_ResumePill` rewritten as
  a three-variant widget (`kind="resume"|"continue"|"review"`).
  Card paint varies by signal: fill + border strength scale
  with the recovery's confidence band. Confidence sentence
  row at the foot of the card (`T.FS_META` ink-3); optional
  engine-provided override via the new `sentence` param.
  Evidence chips capped at **3** (directive's exact rule);
  parser refuses to fabricate. New
  [`sort_for_digest()`](../../app/ui/launcher_v3/investigation_panel.py)
  helper orders investigations by the directive's rank —
  *unfinished* → *returned* → *recent* → *passive* — with
  high-strength threads winning within each rank.
  `MinimalEmpty` gains a *PREVIEW* card: a LOW-state
  `RecoveryCardV3` with the canonical WebSocket fixture
  rendered through the same widget the live launcher uses,
  with a *PREVIEW* caption above and *"A real recovery will
  replace this"* in the sentence row; auto-dismisses because
  `MinimalEmpty` only renders when the engine is empty (state
  machine handles the contract). 5 captures in
  `assets/screenshots/launcher-recovery/`
  (high · medium · low · empty · resume). New
  [`RECOVERY_VISUAL_AUDIT.md`](../product/RECOVERY_VISUAL_AUDIT.md)
  carries the directive's *high / medium / low / silence /
  bad recovery* audit. Receipt:
  [`PHASE_6N_STATUS.md`](../../archive/phase-status/PHASE_6N_STATUS.md).

- **Phase 6M.2 — Launcher Geometry Recovery** (prior phase).
  The 6M.1 refinement drifted the launcher away from a
  *Raycast / Arc utility* shape toward a *dashboard* shape;
  this phase recovers the proportions. **No new features. No
  theme rewrite. No engine work.** Layout-only retune of the
  v3 tokens + widgets: window **720 × 520** (was 820 × 640) /
  max **760 × 560** / column max **640 px** (was 760). Search
  bar capped 640 px wide + centred (was full-width), height
  48 px, placeholder *"Search investigations…"*. Hero card
  **92 px** (was 124) with a **2×2 grid** layout — title TL ·
  confidence TR · chips BL · Resume BR — and a 36-px Resume
  pill (was 34). Investigation strip **max 3** pills (was 4)
  with the existing `+N more` overflow chip; pill height 44,
  radius 14. Returns strip **max 2 rows**, eyebrow removed,
  replaced with a single hairline above the rows; 11-px body,
  9.5-pt mono when-label. Theme spacing rhythm:
  `GUTTER=20 / SECTION_GAP=16 / CARD_GAP=12 / RETURNS_GAP=8`
  (the directive's exact `28/20/12/8` reset). Typography
  scale: `FS_HERO=20 / FS_SECTION=13 / FS_META=11 /
  FS_CONFIDENCE=10` (was 22/14/12). Outer window radius **24**
  (was 28). New `capture_launcher_compact.py` produces 4
  PNGs in `assets/screenshots/launcher-compact/`:
  compact (everything together) · hero (focused alone) ·
  investigations (4 threads → 3 pills + `+1 more`) · empty.
  Phase 6M.1's `launcher-refined/` captures stay on disk as
  the *before* set the regression doc references. Two new
  docs:
  [`LAUNCHER_REGRESSION.md`](../product/LAUNCHER_REGRESSION.md)
  (the directive's *why old looked better / what changed /
  what fixed* audit — 13-token comparison table + the
  *Raycast ↔ Notion* axis narrative) +
  [`PHASE_6M.2_STATUS.md`](../../archive/phase-status/PHASE_6M.2_STATUS.md).
  Numbering: this directive's *Phase 6M.1* label conflicts
  with the prior Launcher Refinement that already shipped;
  filed as **6M.2** so both audit trails survive.

- **Phase 6M.1 — Launcher Refinement** (prior phase, this
  session). The
  launcher should *feel shipped*. **No new features. No
  engine work. No control-room work. Refinement only.** Theme
  tokens refit to the directive's exact values
  ([`theme.py`](../../app/ui/launcher_v3/theme.py)):
  paper-white `#F7F5F2`, solid white cards (all alpha → 255),
  shadow `0 8 24` (offset 8, radius 24, alpha 18), card radius
  20, spacing **28 / 20 / 12**, typography **22 / 14 / 12**.
  `GlassCard` paint flipped to solid (alpha clamped); hero
  card bottom-aligns its action row and drops the *Surfaced
  because you left this mid-flow.* footer. Investigation strip
  rewired to **equal-width pills** with a `+N more` dashed
  overflow chip when there are more than 4 threads. `MinimalEmpty`
  rewritten without a wrapping card — vertically centred
  icon + headline + sub + 2 buttons + trust line. Shell `MAX_WIDTH`
  tightened to 760 (was 760-860 range); `MinimalWindow.DEFAULT_SIZE`
  set to **820 × 640** (was 920 × 720). Three legacy capture
  scripts (`capture_launcher_v3.py` / `capture_launcher_live.py`
  / `capture_launcher_minimal.py`) moved to
  `archive/launcher-refine/` with a README; new
  `capture_launcher_refined.py` produces 5 PNGs in
  `assets/screenshots/launcher-refined/` (hero / empty /
  investigations / resume / focused). New
  [`LAUNCHER_REVIEW.md`](../product/LAUNCHER_REVIEW.md) audit
  (removed · kept · why · future). The previous Phase 6M
  (Desktop Memory Layer) docs + tracker entries are untouched.
  Receipt:
  [`PHASE_6M.1_STATUS.md`](../../archive/phase-status/PHASE_6M.1_STATUS.md).

- **Phase 6M — Desktop Memory Layer** (prior phase, this
  session). Recall now
  sees work outside the browser. **Metadata only**: app name,
  window title, focus duration, switch count, optional path
  (from the title only). **No screenshots, no OCR, no audio,
  no pixels.** New `app/core/desktop/` package (six modules:
  `events` · `processes` · `windows` · `sessions` · `watcher`
  + `__init__`). `FocusAggregator` enforces a 30-second floor
  + 60-second re-focus consolidation + an EXE blocklist
  (Recall's own windows never observe themselves). New
  `POST /v1/events/desktop` route + `DesktopWindowIn` schema
  reject any field outside the directive's whitelist;
  `ALLOWED_KINDS` gains `desktop_window`. New `/desktop` route
  in the control room reads `~/.recall/events/*.jsonl` and
  aggregates per-app focus time + top tools + session log.
  Extension popup gains a small `⊞-N` badge next to the today
  caption (renders when `health.desktop_apps_today > 0`).
  Watcher disabled by default — opt-in via
  `desktop_capture_enabled` in `~/.recall/config.json` and
  `RECALL_DESKTOP=off` is the kill switch. Windows is the
  only platform with a probe today; `darwin.py` / `linux.py`
  siblings drop in next to `windows.py` when a maintainer
  with the hardware adds them. Receipt:
  [`PHASE_6M_STATUS.md`](../../archive/phase-status/PHASE_6M_STATUS.md).
  Product story:
  [`DESKTOP_LAYER.md`](../product/DESKTOP_LAYER.md).

- **Phase 6L — Launcher Simplification** (prior phase). The v3
  launcher (promoted in 6K) is stripped to a **single floating
  surface** — no admin panel, no control room, no analytics view.
  System info (doctor / daemon / version / extension / daily
  loop) lives **only** in the founder control room
  (`apps/admin/web/`). New `app/ui/launcher_v3/minimal.py`
  ships 8 classes — `MinimalSearchBar` + `MinimalDigest`
  (hero + horizontal investigations strip + recent returns +
  trust line) + `MinimalEmpty` + `MinimalShell` (width clamped
  760-860 px, outer gutter 32, section gap 24) + `MinimalWindow`
  (920 × 720 default). LiveLauncher rewired: composes
  `MinimalShell` instead of the 3-column shell; reads **one**
  recovery (was 3) for the hero; investigations stay capped at
  4 but render as horizontal pills (not vertical cards);
  recent-returns row reads from `daily_loop.summary(days=3)`.
  Three widgets archived to `archive/launcher-v2/` —
  `shell.py` (Shell + ContextColumn), `sidebar.py` (rich left
  rail), `window.py` (3-column LauncherWindow) — with a README
  documenting *why removed*. 4 captures in
  `assets/screenshots/launcher-minimal/` (hero · empty ·
  investigations · resume). Default import unchanged
  (`from app.ui.launcher import Launcher` still returns the
  v3 LiveLauncher). Receipt:
  [`PHASE_6L_STATUS.md`](../../archive/phase-status/PHASE_6L_STATUS.md).

- **Phase 6K — Launcher Promotion** (prior phase). The v3 widget
  tree built in Phase 6I becomes the actual launcher. **No
  parallel surface. No dead launcher path. Promote safely.**
  New `app/ui/launcher_v3/live.py` ships `LiveLauncher` — same
  constructor signature as the legacy class
  (`search_engine, event_logger`), same signals
  (`request_settings`, `_request_search`), same public API
  (`show_centered()`, `invalidate_digest()`,
  `_refresh_idle_state()`); composes the v3 Shell with a
  `QStackedLayout` centre that swaps between `EmptyDigest` and
  `DigestColumn`; reads live data via the existing
  `api_client.recovery_recent()` / `threads_recent()` /
  `health()`; honours the demo overlay (Phase 6D); fires the
  keyboard layer (`Esc` hides, `1-9` focuses the n-th card).
  The 1130-line `app/ui/launcher.py` moved to
  `app/ui/launcher_legacy.py`; new `app/ui/launcher.py` is a
  38-line adapter that defaults to LiveLauncher and falls back
  to legacy via `RECALL_LAUNCHER=legacy` — the *promote safely*
  escape hatch. Backwards-compat constants
  (`LAUNCHER_WIDTH` / `SHADOW_MARGIN` / `FOOTER_H`) re-exported.
  6 new captures in `assets/screenshots/launcher-live/`
  (overview / continue / empty / trust / focus / recovery).
  Receipt:
  [`PHASE_6K_STATUS.md`](../../archive/phase-status/PHASE_6K_STATUS.md).

- **Phase 6J — Control Room V2** (prior phase). The founder
  dashboard at `apps/admin/web/` becomes the founder's *actual
  operating system*. **No mock values. No placeholder buttons.
  Everything actionable.** Global chrome ships: top bar
  (Recall wordmark + 3 live pills daemon/readiness/installs +
  `⌘K` search) + bottom bar (version + doctor verdict + build
  label). Command palette (Ctrl+K) — fuzzy search over 14
  routes + 9 directive-named actions (Run doctor / Bake data /
  Generate alpha report / Export trust / Open screenshots /
  Open alpha folder / Open recovery journal / Open daily loop /
  Open logs); selecting a route navigates; selecting an action
  copies the canonical CLI command. Two new loaders
  (`logs.ts` reads 5 sources; `screenshots.ts` scans 6 buckets
  with missing-marker detection). Five new routes — `/extension`
  (popup pairing + version drift + capture rate + repair
  commands), `/launcher` (v3 gallery + v3↔v2 diff strip +
  promotion checklist), `/experiments` (8 feature flags + 4
  alpha gates + 3 GREEN-floor threshold cards), `/logs` (5-source
  picker + filtered viewer + download command), `/screenshots`
  (per-bucket gallery + missing-marker strip). Recovery Lab
  extended with kind filter + confidence distribution + 7-day
  return-after-gap heatmap. System Console gains **Copy
  diagnostics** (redacted markdown blob to clipboard; no PII,
  no URLs, no filenames). Admin Next.js build clean (14 routes,
  87.4 KB first-load shared). **No engine touches, no Python
  touches, no marketing-site touches, no extension touches.**
  Receipt:
  [`PHASE_6J_STATUS.md`](../../archive/phase-status/PHASE_6J_STATUS.md).
  User manual:
  [`CONTROL_ROOM_V2.md`](CONTROL_ROOM_V2.md).

- **Phase 6I — Launcher Rebuild** (prior phase). The launcher gets
  its premium surface. **No engine work, no recovery-logic
  changes — UI only.** New parallel package
  `app/ui/launcher_v3/` ships the directive's twelve named
  modules: `theme.py` (warm white #F7F5F2, lavender accent,
  radius 20-28, shadow soft-only) + `motion.py` (120/180/260,
  OutCubic, fade/slide/expand only) + `surfaces.py` (the seven
  primitives: `GlassCard` / `FloatingPanel` / `SoftDivider` /
  `Pill` / `ConfidenceBadge` / `TimelineChip` / `StatusDot`) +
  `recovery_panel.py` (`RecoveryCardV3` 124-px hero with chip
  row + ConfidenceBadge + accent Resume pill + `1` shortcut +
  hover lift + focus ring + keyboard nav) +
  `investigation_panel.py` (`InvestigationCardV3` with timeline
  strip + target chips + 4-segment resume-strength bar) +
  `trust_panel.py` (three-row footer) + `search_panel.py` +
  `digest.py` (`DigestColumn` + `EmptyDigest`) + `sidebar.py` +
  `shell.py` (3-column composition) + `window.py`. 5 new
  captures in `assets/screenshots/launcher-v3/` (digest /
  continue / empty / trust / focused). The live
  `app/ui/launcher.py` is **untouched** — the v3 package sits
  alongside, ready to be wired in on a follow-up with its own
  QA matrix. Receipt:
  [`PHASE_6I_STATUS.md`](../../archive/phase-status/PHASE_6I_STATUS.md).

- **Phase 6H — Control Room OS** (prior phase). The founder
  dashboard at `apps/admin/web/` becomes a real operating system
  for Recall — **no fake data, no hardcoded cards, everything
  derived**. New `apps/admin/web/lib/loaders/` (8 modules:
  paths / fsx / health / trust / daily / alpha / release /
  system) reads live from `apps/admin/data/*`, `alpha/users/`,
  `alpha/recovery_journal.json`, `apps/admin/release_state.json`,
  and `~/.recall/`. New three-column shell: sticky left rail
  (10 sections, accesskey hotkeys 1-9 + 0, three groups) + main
  + sticky right actions sidebar (7 buttons; *Refresh* re-runs
  data fetch; the other six copy canonical CLI commands — *no
  server endpoint*). Six live panels:
  `HealthPanel` / `AlphaPanel` / `DailyLoopPanel` / `TrustPanel`
  / `ReleasePanel` / `SystemPanel`, each taking typed loader
  output. Ten routes: `/` (overview, every panel in compact
  mode), `/users` (per-cohort table → replays), `/alpha`,
  `/trust`, `/daily-loop` (full heatmap), `/recovery` (6-stat
  + time-to-resume bar chart + ledger rows linking to replays),
  `/replays?tester=<handle>` (per-tester event timeline,
  coverage line), `/release`, `/system`, `/docs`. Inline SVG /
  styled-div for charts (heatmap + sparkline); no charts
  library. Next.js build clean — 10 routes, all
  server-rendered on demand, 87.4 KB first-load shared. **No
  Python, no engine, no recovery work, no `apps/web/`
  touched.** Receipt:
  [`PHASE_6H_STATUS.md`](../../archive/phase-status/PHASE_6H_STATUS.md).

- **Phase 6G — Public Alpha Surface** (prior phase). Build the
  public alpha front door. Pure marketing-site + operator-doc
  work — **no engine work**, **no recovery work**.
  `apps/web/` gets four new section components — `Problem`,
  `Story` (the three canonical demo threads with real
  thumbnails), `Screens` (4-tile gallery of launcher-v2 +
  extension-v2 + demo captures), and `Download` (four
  artifacts: Win lite recommended / Win full / macOS preview /
  browser extension). Hero copy flipped to the directive's
  exact text — *Recall notices unfinished work. / Return later.
  Continue instantly.* — with *Download alpha* + *Watch demo*
  CTAs. The Trust section (was Privacy) rewritten around the
  five-rule vocabulary: local only / no cloud / no telemetry /
  counts only / export only. Nav links rebuilt to the new
  narrative order. 19 screenshots copied into
  `apps/web/public/screens/` (launcher / extension / demo /
  alpha). Three new docs: `docs/product/TRUST.md` (public
  trust statement + on-disk contract per rule),
  `docs/release/DOWNLOAD_GUIDE.md` (four install paths,
  validation, uninstall),
  `docs/release/DEMO_VIDEO_SCRIPT.md` (60-second placeholder
  storyboard, 6 beats, captions only). PUBLIC_ALPHA.md gains a
  Phase 6G addendum. Next.js build clean (55 KB static, 142 KB
  first-load). Receipt:
  [`PHASE_6G_STATUS.md`](../../archive/phase-status/PHASE_6G_STATUS.md).

- **Phase 6F — Daily Loop Validation** (prior phase). Recall
  earns the right to keep running only if a real human installs
  it, uses it, leaves, and comes back. New
  `app/core/daily_loop.py` layer — six counters per local day
  (`day_started` / `investigations_opened` / `recoveries_shown`
  / `recoveries_used` / `returns` / `resume_success`), three
  derived signals (`continuity_restored` / `return_rate` /
  `resume_quality`) with GREEN/YELLOW/RED verdicts, stored at
  `~/.recall/daily_loop.jsonl` (one JSON line per day). New
  return detector: every successful ingest passes through
  `mark_event(ts)` which bumps `returns` when the gap crossed
  30 min (matching the session reconstructor's idle break).
  Three thin `/v1/loop/{bump, summary}` routes + 5 DTOs. Two
  recovery-surface hooks (`recoveries_shown` only on non-empty
  surfaces, `recoveries_used` in restore). New
  `recall founder daily-loop` operator panel + new
  `recall alpha replay <handle>` (per-tester event timeline,
  no content). Recovery journal v2 schema gains
  `return_after_gap` + `time_to_resume`. Doc trio:
  `DAILY_LOOP.md` (product story) +
  `RETURN_BEHAVIOR.md` (return semantics in detail) +
  `MOMENTS.md` (seven first-time moments per tester).
  **No visual redesign**, **no installer work**. Receipt:
  [`PHASE_6F_STATUS.md`](../../archive/phase-status/PHASE_6F_STATUS.md).

- **Phase 6E — Alpha Reality** (prior phase). Recall leaves
  founder-only mode: the operational scaffolding for real
  cohort installs lands without touching the engine or
  redesigning any UI surface. `alpha/users/_TEMPLATE/status.json`
  gains four directive fields (`installer_version`, `extension`,
  `wow_moment`, `confusion`); the alpha CLI gains
  `update` + `export` subcommands; the recovery ledger schema
  is rewritten around the six-outcome vocabulary (`shown` /
  `accepted` / `ignored` / `correct_silence` / `bad_recovery` /
  `resume_ok`). New `recall founder alpha-health` operator
  panel reads the source-of-truth files directly and emits the
  five signals (installs / returning / first recoveries / trust % /
  drop reasons) with green/yellow/red verdicts. New doc trio in
  `docs/alpha/` (PLAYBOOK / STATUS / KNOWN_FAILURES); the install
  matrix gains a *Phase 6E daily-use* section with Windows ×
  Chrome / Edge / Arc + macOS daily-use rows. 3 captures in
  `assets/screenshots/alpha/` (control room / populated status /
  honest empty). **No engine work**, **no UI redesign** — pure
  operations. Receipt:
  [`PHASE_6E_STATUS.md`](../../archive/phase-status/PHASE_6E_STATUS.md).

- **Phase 6D — Demo Mode** (prior phase). A fresh install must
  feel alive. New `app/core/demo_mode.py` state machine
  (`disabled` / `available` / `active` / `dismissed` /
  `completed`) persisted at `~/.recall/demo.json`. Three thin
  `/v1/demo/{state,activate,dismiss}` endpoints + a one-line
  auto-dismiss hook in every ingest route. Launcher's
  `EmptyCard.empty()` now wired live with a *Show example* +
  *Start normally* button pair; clicking the primary flips
  state and routes the launcher into a new `demo_panel` that
  shows a trust banner + the canonical *WebSocket retry
  debugging* `RecoveryCard` + three `InvestigationCard` rows
  (WebSocket / Healthcare pitch — proposal draft / RLHF reward
  shaping). Extension popup mirrors the flow — same two
  buttons, a new `DemoBanner` component, a `"demo"` branch in
  `derivePopupState`, and a payload-aware `Body` render that
  reuses the existing `ConnectedBody` so the demo looks
  identical to a real populated surface. 4 captures in
  `assets/screenshots/demo/` (launcher / extension / transition
  / empty). **No engine layer touched.** Receipt:
  [`PHASE_6D_STATUS.md`](../../archive/phase-status/PHASE_6D_STATUS.md).
  Story doc: [`FIRST_MAGIC.md`](../product/FIRST_MAGIC.md).

- **Phase 6C — Extension Premium** (prior phase). The popup gets
  the same warm-white + lavender + chip vocabulary the launcher
  earned in 6B. Header gains a today-count caption + repair
  wrench icon. `ContinueCard` gains a `ConfidencePill` that
  mirrors the launcher's `derive_recovery_confidence(n_targets)`
  exactly. `MemoryList` is rebuilt as a single vertical *Today*
  rail (`HH:MM` mono stamps + kind glyphs along a hairline) in
  place of the grouped Searches/Tabs/Chats card. The
  investigations card becomes a horizontal pill strip, max 4,
  with a left-to-right slide-fade entry. `EmptyState` adopts the
  launcher's exact copy (*"Recall notices unfinished work. /
  Work normally. Return later. / Recall fills itself."*) + a
  soft *Show example* pill that hands off to the launcher via
  `recall://`. 5 new captures in
  `assets/screenshots/extension-v2/`. **NO engine work**, **NO
  founder work** — extension surface only. Receipt:
  [`PHASE_6C_STATUS.md`](../../archive/phase-status/PHASE_6C_STATUS.md).

- **Phase 6B — Launcher Identity** (prior phase). The theme swap
  deferred from 6A landed. Palette inverted to warm white +
  lavender (matching the extension popup); `LAUNCHER_QSS`
  rewritten with a floating white card + generous spacing; the
  evidence text line finally split into `[2 tabs] [3 files] [2d
  gap]` chip pills via `_EvidenceChip` + `_parse_evidence_chips`;
  `EmptyCard.empty` redesigned at 210 px with *"Recall notices
  unfinished work."* and a soft Show-example lavender pill. 7
  new captures in `assets/screenshots/launcher-v2/`. Receipt:
  [`PHASE_6B_STATUS.md`](../../archive/phase-status/PHASE_6B_STATUS.md).

## Next

*Committed; starts when **Now** clears.*

- **Three clean-Windows-VM installs** in
  `CLEAN_MACHINE_RUN.md`. Each on a different fresh VM. Closes
  gate 1.
- **Alpha-001 distribution** → first three cohort returns land
  in `alpha_report.md` + per-Resume rows in
  `recovery_journal.json`. Closes gates 3 + 4.
- **Rebuild + re-verify `recall://`.** Phase 5H added the
  `[Registry]` section to `recall.iss`; the next signed
  `Recall-Setup.exe` bakes it in. After install, `recall
  doctor` should report `GREEN protocol`.
- **Live install + control-room GIFs** per
  `RECORDING_PROTOCOL.md`. Closes the last two demo assets.
- **Sign the installer** — EV cert (Windows) — closes gate 7's
  remaining half. SmartScreen warning goes away.
- **Verified macOS build** — a maintainer with Mac hardware runs
  the script in `MAC_OWNER_NEEDED.md`, fills `MAC_VERIFICATION.md`.
  Promotes macOS from Preview to Supported.

## Later

*Real, not scheduled.*

- Signed auto-update channel (stable / preview).
- Linux packaged artifact (currently source-only).
- Chrome Web Store listing for the extension.
- Universal2 macOS build.
- Apple Developer ID + notarisation (macOS Gatekeeper warning).
- `recall://` protocol handler registration on install — closes
  the YELLOW row in `recall doctor`.

## Never

*Declined. PRs adding these are closed with a link to this line.*

- **Telemetry, analytics, error reporting, usage pings** — including
  "anonymous" or "aggregate" ones. The founder dashboard is fed by
  GitHub's public counts and *voluntary* cohort check-ins, never by
  a collection mechanism.
- **Cloud sync. Multi-user. Remote inference.** The bind is the
  boundary.
- **LLM chat over your files. A copilot. An assistant.**
- **A recommendation feed. Notifications. A productivity score.**
- **Auth on the loopback API.**
- **Embeddings on any layer above file search.**

These mirror [`CLAUDE.md`](../../CLAUDE.md) § *Things we will not build* —
this column is its public-facing twin.
