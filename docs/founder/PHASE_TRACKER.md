# PHASE_TRACKER.md — where the build is

The 30-second answer to *"what state is Recall in?"* Updated at the
close of every phase. Pairs with [`ROADMAP_LIVE.md`](ROADMAP_LIVE.md)
(what's next) and [`CHANGELOG.md`](../release/CHANGELOG.md) (what changed).

---

## Current phase

**Phase 6H — Control Room OS.** The founder dashboard at
`apps/admin/web/` is rebuilt as the founder's *operating
system*. **No fake data. No hardcoded cards. Everything
derived.** Eight new live loader modules under
`apps/admin/web/lib/loaders/` (`paths.ts` · `fsx.ts` ·
`health.ts` · `trust.ts` · `daily.ts` · `alpha.ts` · `release.ts`
· `system.ts` + a barrel) read from `apps/admin/data/*`,
`alpha/users/`, `alpha/recovery_journal.json`,
`apps/admin/release_state.json`, and `~/.recall/`. The
`daily.ts` loader mirrors `app/core/daily_loop.summary()`
exactly in TypeScript so the dashboard never asks the daemon
for the aggregation. New three-column shell: sticky left rail
(10 sections in 3 groups, accesskey hotkeys 1-9 + 0; active
route highlighted via `usePathname()`; CSS-only collapse on
small viewports) + main route content + sticky right actions
sidebar (7 buttons — *Refresh data* triggers
`router.refresh()`; *Bake* / *Doctor* / *Alpha report* /
*Open screenshots* / *Open logs* / *Export health* copy the
canonical CLI commands to the clipboard — strict *no server*
stance). Six live panel components: `HealthPanel` /
`AlphaPanel` (6 directive signal cards with GYR pills) /
`DailyLoopPanel` (3 signal cards + 6-row counter table +
7-day heatmap of 5 bins × 7 days, pure styled-div) /
`TrustPanel` (6 outcome stats + derived-signals row including
trust % + return correlation + median time-to-resume) /
`ReleasePanel` (per-gate progress bars with GYR + GO/PARTIAL/
NO-GO + blockers list) / `SystemPanel` (5 live filesystem
checks: `~/.recall` / config / events / launcher lock /
demo overlay). Plus a shared `Verdict.tsx` pill (3 colours +
`mute`, used everywhere). Ten routes: `/` overview (every
panel compact), `/users` (per-cohort table → click to
replay), `/alpha` (deep-dive), `/trust` (deep-dive),
`/daily-loop` (deep-dive + heatmap), `/recovery` (6-stat
header + time-to-resume sparkline + ledger rows clicking to
replay), `/replays?tester=<handle>` (per-tester event
timeline with coverage line: install / activity / recovery /
resume / return / wow / failure), `/release`, `/system`,
`/docs` (static map of the canonical docs). Inline SVG and
styled-div for charts — *no charts library, no chart
explosion*. Every route is a React Server Component with
`force-dynamic`; the loaders re-read the disk on every
request; no cache / no revalidate. Next.js build clean (10
routes, all `ƒ` dynamic, 87.4 KB first-load shared). **No
Python, no engine, no recovery, no `apps/web/` marketing-site
touches.** Receipt:
[`PHASE_6H_STATUS.md`](../engineering/PHASE_6H_STATUS.md).

### Previous phase

**Phase 6G — Public Alpha Surface.** Build the public alpha
front door. **No engine work**, **no recovery work** —
marketing-site + operator-doc only. The Next.js app at
`apps/web/` gains four new section components: `Problem` (the
context-loss tax) + `Story` (three real-shape investigations
matching the demo overlay's WebSocket / Healthcare-pitch
proposal / RLHF reward shaping, each with a real demo
thumbnail) + `Screens` (4-tile gallery of launcher-v2 +
extension-v2 + demo captures) + `Download` (four artifacts in
a calm grid: Windows lite recommended / Windows full / macOS
preview / browser extension; trust strip at the bottom
restating the boundary at the moment of install). Hero copy
rewritten to the directive's exact text (*Recall notices
unfinished work. / Return later. Continue instantly.*) with
*Download alpha* + *Watch demo* CTAs (the primary now anchors
to the in-page `#download`, not a GitHub jump). Privacy
section's eyebrow flipped to *Trust* and its five points
rewritten to the directive's vocabulary — *local only / no
cloud / no telemetry / counts only / export only* — each body
mirroring the on-disk contract in `docs/product/TRUST.md`. Nav
links rebuilt to the new narrative order
(`Problem · How · Stories · Screens · Trust · Download ·
GitHub`); the Nav's CTA renamed to *Download alpha* and
anchored to `#download`. 19 screenshots copied into
`apps/web/public/screens/` (7 launcher-v2 + 5 extension-v2 + 4
demo + 3 alpha). Three new docs: `docs/product/TRUST.md` (the
public trust statement, five rules + on-disk contract per rule
+ *what Recall will / won't ask for* + the
enforcement-in-code map),
`docs/release/DOWNLOAD_GUIDE.md` (every install path in detail
+ 5-step first-run validation + uninstall paths), and
`docs/release/DEMO_VIDEO_SCRIPT.md` (60-second placeholder
storyboard — 6 beats, captions only, no voice-over,
pre-flight checklist, the cuts to never make). PUBLIC_ALPHA.md
gains a Phase 6G addendum naming the new front-door surfaces.
Next.js build clean (`/` at 55 KB / first-load 142 KB).
Receipt:
[`PHASE_6G_STATUS.md`](../engineering/PHASE_6G_STATUS.md).

### Previous phase

**Phase 6F — Daily Loop Validation.** Recall proves repeat use.
**No visual redesign**, **no installer work** — only the data
layer that names whether a real human came back. New
`app/core/daily_loop.py` — six per-day counters (`day_started`
/ `investigations_opened` / `recoveries_shown` /
`recoveries_used` / `returns` / `resume_success`) at
`~/.recall/daily_loop.jsonl` (one JSON line per local day; <
50 KB / year). Three derived signals computed at read time —
`continuity_restored` / `return_rate` / `resume_quality` — with
GREEN/YELLOW/RED verdicts (thresholds pinned in-source; mirrored
in DAILY_LOOP.md). New return detector: every successful ingest
calls `mark_event(ts)` which bumps `returns` when the gap
crosses 30 min (matches session reconstructor's idle break);
state in `~/.recall/daily_loop_state.json`. Disable via
`RECALL_DAILY_LOOP=off`. Three thin API routes —
`POST /v1/loop/bump` (closed pydantic Literal of 6 bins; 422
on bad input) and `GET /v1/loop/summary?days=7`. Two recovery-
surface hooks in `api/main.py` (`recoveries_shown` bumped only
on non-empty `/v1/recovery/recent`, `recoveries_used` bumped in
`/v1/recovery/{id}/restore`); the ingest hook from 6D was
extended (`demo_mode.mark_real_activity` + `daily_loop.mark_event`
in the same one-call hook). New `recall founder daily-loop`
operator panel + new `recall alpha replay <handle>` (per-tester
event-only timeline; no content; coverage line shows which of
the seven first-time moments have landed). Recovery journal v2
schema gains `return_after_gap` + `time_to_resume`. Doc trio:
`DAILY_LOOP.md` (product story — six bins, three signals,
thresholds, the *not telemetry* contract) +
`RETURN_BEHAVIOR.md` (return detector semantics — what counts,
what doesn't, why 30 min, manual verification recipe) +
`MOMENTS.md` (seven first-time moments per tester:
install / capture / investigation / recovery / resume / wow /
trust break). Receipt:
[`PHASE_6F_STATUS.md`](../engineering/PHASE_6F_STATUS.md).

### Previous phase

**Phase 6E — Alpha Reality.** Recall leaves founder-only mode.
**Operations-only phase** — no engine touches, no UI redesign.
`alpha/users/_TEMPLATE/status.json` gained four directive fields
(`installer_version` · `extension` · `wow_moment` · `confusion`),
all metadata, all optional, existing records keep working. Alpha
CLI grew two subcommands: `update <handle> --<field> <value> ...`
(closed allowlist of fields; cross-cohort lookup by handle) and
`export [--cohort <name>]` (JSON dump with the directive's five
top-level keys: `installs` / `returning` / `recoveries` /
`issues` / `trust`). Recovery ledger schema rewritten — the new
`_kind_vocabulary` block names the six Phase 6E outcomes
(`shown` / `accepted` / `ignored` / `correct_silence` /
`bad_recovery` / `resume_ok`); the export aggregator computes
`trust % = (resume_ok + correct_silence) / shown` and maps
legacy `accepted` / `wrong` entries onto the new vocabulary so
pre-6E rows still count. New `recall founder alpha-health`
operator panel — reads `alpha/users/` + `alpha/recovery_journal.json`
directly (bypasses the `bake` round-trip so the panel is always
current), prints the five signals with `[GREEN]` / `[YELLOW]` /
`[RED]` brackets + the directive success-line (5 humans / 3
recoveries / 1 wow / 1 failure story). New doc trio in
`docs/alpha/` — `PLAYBOOK.md` (six-moment lifecycle + daily
morning loop + field list + the no-content-no-telemetry contract
restated), `STATUS.md` (the live cohort board, hand-edited
weekly), `KNOWN_FAILURES.md` (the failure catalogue, quote-don't-
paraphrase rule). `ALPHA_MATRIX.md` extended with a daily-use
section — 5 new rows for Windows × Chrome / Edge / Arc + macOS
Intel / Apple Silicon daily use. 3 new captures in
`assets/screenshots/alpha/` (control room / populated status /
honest empty). Receipt:
[`PHASE_6E_STATUS.md`](../engineering/PHASE_6E_STATUS.md). Pairs
with [`docs/alpha/PLAYBOOK.md`](../alpha/PLAYBOOK.md).

### Previous phase

**Phase 6D — Demo Mode.** A fresh install must feel alive. New
`app/core/demo_mode.py` state machine (five states — `disabled`
/ `available` / `active` / `dismissed` / `completed`) persisted
at `~/.recall/demo.json`. Three thin `/v1/demo/{state,
activate, dismiss}` endpoints plus a one-line
`_post_ingest_hook(ok)` call in every ingest route that
auto-dismisses the overlay the moment a real event arrives
(*real events override demo*, enforced). Canonical fixture
payload — one recovery (*WebSocket retry debugging*, 2 tabs /
2 files / 2-day gap, confidence=high), three investigations
(*WebSocket* / *Healthcare pitch — proposal draft* / *RLHF
reward shaping*), eight-event Today rail with HH:MM
timestamps — **hand-written, fully deterministic, no AI, no
generated text**. Launcher's empty surface now wired live to
`EmptyCard.empty()` with a *Show example* + *Start normally*
button pair (closing the Phase 6B *Live launcher's empty
surface wired to use `EmptyCard.empty()`* deferral); a new
`demo_panel` widget renders the trust banner + recovery card
+ three investigation rows when state is `active`. Extension
popup mirrors the flow — same two buttons, a new `DemoBanner`
component, a `"demo"` branch in the `PopupState` machine, and
a payload-aware `Body` render that reuses the existing
`ConnectedBody` so the demo and the real surface render via
the same code path. Four captures in
`assets/screenshots/demo/`. **No engine layer touched** — the
events / sessions / contexts / resurfacing / threads /
evolution / recovery modules are not consulted, even
indirectly. Story doc:
[`FIRST_MAGIC.md`](../product/FIRST_MAGIC.md).

### Previous phase

**Phase 6C — Extension Premium.** Carries the 6B launcher identity
(warm white + lavender + chip vocabulary) across into the browser
extension popup so the two surfaces read as one product. Header
gained a quiet mono `"N today"` event-count caption next to the
breathing daemon dot, plus a repair-wrench icon button beside the
gear. `ContinueCard` gained a `ConfidencePill` (high / med / low)
that mirrors the launcher's `derive_recovery_confidence(n_targets)`
exactly — same colour vocabulary as the launcher's
`_ConfidenceBadge`, pure UI-side derivation, no engine field.
`MemoryList` was rewritten as a single vertical *Today* rail —
`HH:MM` mono stamps + small kind glyphs along a hairline — in
place of the prior grouped Searches/Tabs/Chats card; rows
without a real `ts` are dropped silently. `InvestigationCard`
became a horizontal pill (28 px, radius 14, soft surface,
12 px thread glyph + title) and the host site renders the
list as a `slice(0,4)` flex-wrap strip with a left-to-right
slide-fade entry. `EmptyState` adopted the launcher's exact
copy — *"Recall notices unfinished work. / Work normally.
Return later. / Recall fills itself."* + a soft *Show example*
pill that dispatches `openRecall()` (handoff to the launcher;
the popup never reaches into the engine itself). Five new
captures in `assets/screenshots/extension-v2/`
(extension-home / -empty / -recovery / -repair / -offline).
**NO engine touches**, **NO founder touches** — the directive's
*Only extension surface* rule held.

## Completed phases

| Phase | Theme | Outcome |
|---|---|---|
| 1A–3C | Engine | events → sessions → contexts → resurfacing → threads → evolution → recovery; `/v1/*` API; launcher; extension; docs |
| 4A | Productization | release lifecycle docs, empty states, error discipline |
| 4B | Public readiness | pseudo-monorepo restructure |
| 4C | Stability + sharpness | `STABILITY.md`, recovery sharpening, JSONL hardening |
| 4D | First public users | first-use audit, uninstall doc, issue triage |
| 4E | Behavioral indispensability | recovery quality gate, specific captions, demo realism |
| 4F | Trust + responsiveness | parse-cache fix (the section-11 perf bug), `PERF.md` |
| 4G | Trust calibration | evidence-specific captions, `TRUST_FIXTURES.md` |
| 4H | Continuity experience | session-anchored thread grouping (the `backoff.py` fix) |
| 4I | Launcher experience | calmness pass (focused, safe) |
| 4J | Surface coherence | `CONTINUITY_LANGUAGE.md`, `SURFACE_MAP.md`, `MOTION.md` |
| 4K | Launcher redesign | `app/ui/cards.py` — six launcher cards, verified by render |
| 4L | Screenshot pipeline | `infra/scripts/capture/` — deterministic doc screenshots |
| 5A | Zero friction | Windows + macOS packaging, extension pairing, install docs |
| 5E | Control Room | `apps/admin/` no-telemetry operator dashboard |
| 5A.1 | Install Validation | PyInstaller bundle built + verified; extension screenshots; `GO_NO_GO.md` |
| 5E.1 | Local Observability | `recall stats` + export + admin import pipeline + `TRUST_LEDGER.md` |
| 5B | Daily Indispensability | time-of-day digest headers, local-only daily score, `CONTINUITY_HEALTH.md`, founder additions |
| 5C | Public Alpha Readiness | `recall doctor`, first-recovery ceremony, extension onboarding, FIRST_WEEK/TRUST_MOMENTS/KNOWN_LIMITATIONS/PUBLIC_ALPHA_CHECKLIST |
| 5D | Codebase Hygiene | 5 web orphans archived, audit docs (DEAD_CODE/COMPLEXITY/REPO_HEALTH/DEPENDENCIES), CI workflow |
| 5D.1 | Documentation Consolidation | 40 root `.md` → `docs/{product,founder,engineering,release,trust}/`; 5 root files only; zero broken links; `DOC_INDEX` + `DOC_HEALTH` |
| 5E.2 | Founder Control Room (UI) | `apps/admin/web/` Next.js dashboard (7 sections, hand-rolled SVG, no server / auth / telemetry) + sample data + `CONTROL_ROOM.md` |
| 5E.3 | Founder Automation Layer | `bake_data.py` pipeline · `recall founder` CLI (7 subcommands) · `release_readiness.py` (0-100 score, six-dim breakdown) · `FOUNDER_OPERATIONS.md` + `READINESS_SCORE.md` |
| 5F | Release Reality | Inno Setup installed → real `Recall-Setup.exe` built · 5 new doctor checks (installer / autostart / protocol / extension / versions) · `alpha/` packet (5 user-facing docs) · `MAC_VERIFICATION.md` · `INSTALL_PROOF_WINDOWS.md` · Settings dialog captured · gate 7 NO-GO → PARTIAL |
| 5G | Reality Validation | Silent install + launch + doctor + uninstall verified on the build machine (66.0 s install / 6.1 s uninstall / 623 MB WS / zero residue) · `CLEAN_MACHINE_RUN.md` · `RECOVERY_STRESS.md` (3 live + 3 design scenarios) · `INSTALL_METRICS.md` · `MAC_OWNER_NEEDED.md` · `alpha_report.md` framework · control-room + doctor + installer-flow screenshots → gate 6 GO · gate 1 has first ▲ run |
| 5H | Alpha Cohorts + Friction Removal | 11 friction items closed (4 doctor + 1 installer registry + 6 extension) · `FRICTION_FIXES.md` · extension state machine (`PopupState`, `derivePopupState`, CapturingState, DebugStrip, `openRecall` no-dead-click) · build green (tsc + vite) · `alpha/launcher/` 5-file pack · `ALPHA_001_RUNBOOK.md` (5 personas) · `LANDING_GO_LIVE.md` · `INSTALL_SIZE_AUDIT.md` (260 MB → ~170 MB path mapped) · `recovery_journal.json` · 3 deterministic GIFs + `RECORDING_PROTOCOL.md` |
| 5I | Surface Quality + Live Feel | Visual tokens (`SURFACE_0/1/2`, `BORDER_SOFT/STRONG`, `SHADOW_SOFT/ELEVATED`, `MOTION_FAST/NORMAL/SLOW_MS`) added to `app/ui/styles.py` + mirrored as CSS vars in `apps/extension/ui/src/styles.css` · launcher cards 54 → 58px + 2 px hover lift + lavender focus ring · `RecoveryCard` 64px + `_ResumePill` + 220 ms slide-fade entrance · extension `AnimatePresence` over Body for smooth state crossfades · `DebugStrip` hidden by default, Alt+D toggle persists in `chrome.storage` · 15 captures + 3 GIFs regenerated |
| Repo Stabilization Pass | (interstitial) | 28 unused Python imports removed across 14 files · 3 empty f-strings flattened · duplicate `_transition_colour` collapsed · `time_label` dead local dropped · extension `calmFlash`/`calmSlow`/`MOTION_*_S` un-exported (zero consumers) · root `CHANGELOG.md` redirect added · `.gitignore` hardened · `REPO_CLEANUP_REPORT.md` published · all 5 build surfaces verified |
| 5H² | Friction Kill | `app/core/install_repair.py` (`recall repair` / `reset` / `reinstall-check`) · extension `DaemonPulse` (breathes when connected) · launcher `_play_digest_stagger_reveal` (180 ms × 60 ms one-shot fade-in cascade) · `PHASE_5H_STATUS.md` + `FRICTION_FIXED.md` (40 fixes) + `OPEN_PROBLEMS.md` (26 named, 16 accept-by-design) |
| 5I | Install Speed + Real World Loop | `audit_install_size_v2.py` + `INSTALL_SIZE_AUDIT_V2.md` (real bytes) · `MODEL_STRATEGY.md` (ONNX path to <150 MB) · `SPLIT_DISTRIBUTION.md` (4 packs / 2 install paths) · `FIRST_72_HOURS.md` (Day 0-3 curve) · launcher split begun: `launcher_anims.py` (one slice) · extension: `1` quick-resume hotkey + investigation surface chips |
| 5J | Installer Shrink Execution | Tier A excludes applied (24 Python excludes + 19 binary patterns) · `Recall-Setup-lite.exe` rebuilt at **216.2 MB** (−45 MB / −17%) · bundle 970 → **783 MB** (−187 MB / −19%) · `PyQt6` 217 → 50 MB (-167 MB win) · launcher split phase 2: `launcher_digest.py` sibling · extension `ResumePreview` (real-data domain list under Resume) · `INSTALL_REDUCTION_REPORT.md` + `PHASE_5J_STATUS.md` · clean-VM install time deferred |
| 5K | Alpha Reality | `alpha/users/` tree (5 cohort folders + TEMPLATE + JSON schema, zero fake testers) · `recall alpha` CLI (`create` / `status` / `report`, ~280 LOC, PII-rejecting handle validation) · `ALPHA_FEEDBACK_V2.md` (6-row form, each maps to a concrete artifact) · `ALPHA_MATRIX.md` (5 install slots × 7 columns, all unknown) · extension *Connection* drawer in Settings (real-data, breathing dot, conditional Open-Recall) |
| 6A | First Magic | RecoveryCard *confidence badge* (high/medium/low, UI-derived) · `RECOVERY_HEIGHT` 64→76 · EmptyCard.empty copy refreshed (*Recall fills itself*) · extension Connection drawer **collapsible** (header click, AnimatePresence body) · MemoryList rows grew mono-font timeline labels from real `ts` field · 14 surfaces re-captured · launcher theme swap deferred (regression risk) |
| 6B | Launcher Identity | Palette inverted to **warm white + lavender** (matches extension popup) · `LAUNCHER_QSS` rewritten with floating glass card (rgba(255,255,255,184), radius 22) + generous spacing · hover-fill swapped from warm beige to low-alpha lavender · `_EvidenceChip` + `_parse_evidence_chips` split the dim evidence line into `[2 tabs] [3 files] [2d gap]` chip row · `EmptyCard.empty` redesigned at 210 px with *"Recall notices unfinished work."* + a soft *Show example* pill (signal stub) · 7 captures regenerated into `assets/screenshots/launcher-v2/` (capture pipeline gained optional `subdir`) |
| 6C | Extension Premium | Launcher palette + chip vocabulary carried across into the popup · Header gained `"N today"` mono caption + repair-wrench icon · `ContinueCard` gained a `ConfidencePill` mirroring `derive_recovery_confidence(n_targets)` exactly · `MemoryList` rewritten as a vertical *Today* rail (HH:MM mono + kind glyphs along a hairline; rows w/o `ts` dropped) · `InvestigationCard` → horizontal pill, `slice(0,4)` strip with left-to-right slide-fade entry · `EmptyState` adopted the launcher's exact copy + soft *Show example* pill (dispatches `openRecall()`; no engine work) · 5 captures in `assets/screenshots/extension-v2/` · `capture_extension.mjs` gained optional `dir` arg + the v2 fixtures · NO engine touches, NO founder touches |
| 6D | Demo Mode | New `app/core/demo_mode.py` state machine (`disabled`/`available`/`active`/`dismissed`/`completed`) at `~/.recall/demo.json` · 3 thin `/v1/demo/{state,activate,dismiss}` routes + one-line auto-dismiss hook on every successful ingest (real events override demo, enforced) · canonical fixture: 1 recovery (*WebSocket retry debugging*, 2 tabs/2 files/2d gap, high) + 3 investigations (*WebSocket* / *Healthcare pitch — proposal draft* / *RLHF reward shaping*) + 8-event Today rail · launcher empty surface wired live to `EmptyCard.empty()` (closing 6B deferral); new `demo_panel` widget renders trust banner + RecoveryCard + InvestigationCard rows · extension popup: 2-button EmptyState, new `DemoBanner` component, `"demo"` branch in `derivePopupState`, `Body` reuses `ConnectedBody` so demo and real share render path · 4 captures in `assets/screenshots/demo/` · `FIRST_MAGIC.md` story doc · **zero engine layer touches** |
| 6E | Alpha Reality | **Operations-only** — no engine work, no UI redesign · `alpha/users/_TEMPLATE/status.json` gained 4 directive fields (`installer_version` · `extension` · `wow_moment` · `confusion`) · alpha CLI gained `update <handle> --<field> <value> ...` (closed allowlist) + `export [--cohort]` (JSON with 5 directive keys: `installs` / `returning` / `recoveries` / `issues` / `trust`) · `recovery_journal.json` schema rewritten around 6-kind vocabulary (`shown` / `accepted` / `ignored` / `correct_silence` / `bad_recovery` / `resume_ok`); legacy entries auto-mapped · new `recall founder alpha-health` operator panel reads `alpha/users/` + `recovery_journal.json` directly (bypasses bake), prints 5 signals with GREEN/YELLOW/RED + directive success-line · doc trio in `docs/alpha/`: `PLAYBOOK.md` (6-moment lifecycle, daily loop, field list, trust contract) · `STATUS.md` (live cohort board, hand-edited weekly) · `KNOWN_FAILURES.md` (failure catalogue, quote-don't-paraphrase rule) · `ALPHA_MATRIX.md` extended with 5 daily-use rows (Win × Chrome/Edge/Arc + macOS Intel/Silicon) · 3 captures in `assets/screenshots/alpha/` (control room / populated status / honest empty) |
| 6F | Daily Loop Validation | **No visual redesign**, **no installer work** · new `app/core/daily_loop.py` — 6 per-day counters at `~/.recall/daily_loop.jsonl` (one JSON line / day, < 50 KB / year) + 3 derived signals (`continuity_restored` / `return_rate` / `resume_quality`) with GREEN/YELLOW/RED · new return detector: every successful ingest calls `mark_event(ts)` which bumps `returns` when the gap crosses 30 min · 3 thin routes (`POST /v1/loop/bump` w/ closed Literal of 6 bins; `GET /v1/loop/summary?days=7`) + 5 DTOs · 2 recovery hooks in `api/main.py` (`shown` only on non-empty surfaces, `used` in restore) · ingest hook extended (`demo_mode.mark_real_activity` + `daily_loop.mark_event` same hook) · disable via `RECALL_DAILY_LOOP=off` · new `recall founder daily-loop` operator panel + `recall alpha replay <handle>` (per-tester timeline, no content, coverage line) · recovery journal v2 schema gains `return_after_gap` + `time_to_resume` · doc trio: `DAILY_LOOP.md` (product story) + `RETURN_BEHAVIOR.md` (detector semantics) + `MOMENTS.md` (7 first-time moments) |
| 6G | Public Alpha Surface | **No engine work**, **no recovery work** — marketing-site + operator-doc only · `apps/web/` gains 4 new section components: `Problem` / `Story` (the 3 canonical demo threads with real thumbnails) / `Screens` (4-tile gallery) / `Download` (4 artifacts: Win lite recommended / Win full / macOS preview / browser extension + trust strip) · Hero copy rewritten to directive: *Recall notices unfinished work. / Return later. Continue instantly.* + *Download alpha* + *Watch demo* CTAs · Privacy → Trust rewrite with 5-rule vocabulary (local only / no cloud / no telemetry / counts only / export only) · Nav links rebuilt to narrative order · 19 screenshots copied into `apps/web/public/screens/` (7 launcher-v2 + 5 extension-v2 + 4 demo + 3 alpha) · 3 new docs: `TRUST.md` (public trust statement + on-disk contract per rule) + `DOWNLOAD_GUIDE.md` (4 install paths + validation + uninstall) + `DEMO_VIDEO_SCRIPT.md` (60-second storyboard, 6 beats, captions only) · PUBLIC_ALPHA.md gains Phase 6G addendum · Next.js build clean (55 KB static, 142 KB first-load) |
| 6H | Control Room OS | **No fake data, no hardcoded cards, everything derived** · 8 new loader modules under `apps/admin/web/lib/loaders/` reading live from `apps/admin/data/*`, `alpha/users/`, `alpha/recovery_journal.json`, `release_state.json`, `~/.recall/` · `daily.ts` mirrors `app/core/daily_loop.summary()` in TS so the dashboard never asks the daemon · 3-column shell: sticky left rail (10 routes, accesskey hotkeys 1-9 + 0, 3 groups) + main + sticky actions sidebar (7 buttons; *Refresh* runs `router.refresh()`, the other 6 copy canonical CLI commands — **no server endpoint**) · 6 live panels (`HealthPanel` / `AlphaPanel` w/ 6 GYR signal cards / `DailyLoopPanel` w/ 3 signals + counter table + 7-day heatmap / `TrustPanel` w/ 6 outcome stats + derived signals / `ReleasePanel` w/ per-gate progress bars + GO/PARTIAL/NO-GO / `SystemPanel` w/ 5 live filesystem checks) + shared `Verdict.tsx` pill · 10 routes (`/`, `/users`, `/alpha`, `/trust`, `/daily-loop`, `/recovery`, `/replays?tester=<handle>` w/ coverage line, `/release`, `/system`, `/docs`), all `force-dynamic`, no cache · Inline SVG + styled-div for charts (no charts library) · Next.js build clean (10 routes, 87.4 KB first-load shared) · No Python, no engine, no marketing-site touches |

## Active work

- **Phase 5H closed the friction backlog from 5G** (11 items).
  Active backlog for what comes next: (1) three clean-Windows-VM
  walks per [`CLEAN_MACHINE_RUN.md`](../trust/CLEAN_MACHINE_RUN.md),
  (2) alpha-001 cohort distribution + first returns into
  [`alpha_report.md`](../../alpha/alpha_report.md) + per-Resume
  rows into [`recovery_journal.json`](../../alpha/recovery_journal.json),
  (3) rebuild the installer to bake in the new `[Registry]`
  section and re-verify `recall://` end-to-end, (4) the two
  deferred GIFs (`install.gif`, `control-room.gif`) per
  [`RECORDING_PROTOCOL.md`](../release/RECORDING_PROTOCOL.md),
  (5) the website diff in
  [`LANDING_GO_LIVE.md`](../release/LANDING_GO_LIVE.md). Code
  signing still outside maintainer's control until an EV cert
  is procured.

## Blocked items

| Item | Blocked on |
|---|---|
| Clean-machine install walk | a fresh Windows VM + the 13-row checklist in [`INSTALL_PROOF_WINDOWS.md`](../trust/INSTALL_PROOF_WINDOWS.md) |
| Code signing | EV certificate (Windows) + Apple Developer ID (macOS) — SmartScreen warns until signed |
| macOS verification | a maintainer with Mac hardware to fill [`MAC_VERIFICATION.md`](../release/MAC_VERIFICATION.md) |
| Public alpha | the seven gates in [`GO_NO_GO.md`](../release/GO_NO_GO.md) — currently NO-GO on gate 1 |
| Control-room screenshot | Playwright capture of `apps/admin/web/` (Next.js, not Qt) |
| Live usage metrics in the dashboard | by design — no telemetry; fed by voluntary cohort check-ins |

## Next milestone

**Phase 5I — Live Cohort.** Two external-dependent deliverables:
(1) three clean-Windows-VM installs in
[`CLEAN_MACHINE_RUN.md`](../trust/CLEAN_MACHINE_RUN.md);
(2) alpha-001 cohort distribution + first returns. Once both
land, the verdict on the directive's success criterion (*5
humans run Recall, 3 get recovery, 2 return voluntarily, 1 says
"wait... it remembered that?"*) becomes writeable in
[`alpha_report.md`](../../alpha/alpha_report.md). Optional in
parallel: macOS verification by an external maintainer using
[`MAC_OWNER_NEEDED.md`](../release/MAC_OWNER_NEEDED.md), and
the website diff per
[`LANDING_GO_LIVE.md`](../release/LANDING_GO_LIVE.md).

## Public release target

`0.2.0` public alpha — gated by
[`GO_NO_GO.md`](../release/GO_NO_GO.md) (all seven gates GO).
Phase 5F closed gate 7's first half; Phase 5G closed gate 6 and
moved gate 1 from NO-GO to PARTIAL (build-machine ▲). Gate 1's
clean-VM half + gate 7's signing half + gates 3/4's cohort
evidence are the remaining three.
[`ROADMAP_LIVE.md`](ROADMAP_LIVE.md) tracks it under **Next**.
