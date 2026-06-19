# PHASE_TRACKER.md — where the build is

The 30-second answer to *"what state is Recall in?"* Updated at the
close of every phase. Pairs with [`ROADMAP_LIVE.md`](ROADMAP_LIVE.md)
(what's next) and [`CHANGELOG.md`](../release/CHANGELOG.md) (what changed).

---

## Current phase

**Phase 8E — Alpha Users + Evidence Loop.** *Put
Recall in front of humans. No product work · no
launcher work · no extension redesign · no new
features.* The receiving end of the cohort
evidence loop is built; the cohort itself is 1
(founder) + 4 open seats — recruitment is Phase
8F. **Two scores now**, both honest: **RC1
product score 87 → 90** (RC-tag threshold;
+evidence-index consolidation gives extension +5
/ control-room +5 / launcher +2 / capture +2 /
resume +2) + **Alpha evidence score 30** (new;
failure target 1/1 met via [BUG-001 incident
file](../../alpha/failures/2026-05-24-launcher-imported-demo-data.md);
4 users short / 3 recoveries short / 1 wow
short). **(1) Alpha pack:** 7 docs under
[`alpha/pack/`](../../alpha/pack/WELCOME.md)
matching directive flow (install → browse →
leave → return → resume → report) — `WELCOME` ·
`INSTALL` · `DAY0` · `DAY1` · `DAY3` · `FEEDBACK`
· `UNINSTALL`; privacy boundary repeated
verbatim. **(2) User ledger:**
[`alpha/users_live.json`](../../alpha/users_live.json)
schema `alpha-users-live-v1` with 9 PII-free
fields (handle / install_date / platform /
browser / used_days / recoveries_seen /
recoveries_used / wow / failure / status);
founder = `alpha-001` baseline; explicit gap
table vs directive target. **(3) Daily review:**
new **`recall alpha review`** subcommand
(~110-line `cmd_review` in
[`app/core/alpha_cli.py`](../../app/core/alpha_cli.py))
reads 3 sources (users_live.json + recovery
journal + wow/failures dirs); ASCII-only output;
6 directive-named lines (installs / active /
recoveries / trust / wow / failures) + 4 target
lines (OK / short). **(4) Failure loop:**
[`alpha/failures/`](../../alpha/failures/README.md)
with README + 5-field TEMPLATE + 1 real incident
(BUG-001 8B archive over-reach, with
"module-level imports are alive whenever the
module loads" lesson appended); files counted
automatically by `review` CLI. **(5) Wow
collection:** [`alpha/wow/`](../../alpha/wow/README.md)
README + TEMPLATE — **verbatim-only rule**
(no paraphrase, ever); anonymisation guide;
0 quotes filed (cohort pending). **(6) RC
validation:** new
[`RC_VALIDATION.md`](../release/RC_VALIDATION.md)
cross-link evidence index — all 6 RC1 claims
(install / capture / resume / launcher /
extension / control-room) backed by checked-in
artifacts; 4 carry honest follow-up flags
(BUG-002 / BUG-003 / CTRL-001), 0 unsubstantiated.
**(7) Release-readiness:** RC1 score 87 → 90 +
Alpha score 30 (new dimension);
combination-table interpretation pins the next
phase: *"Product ≥ 90 + Alpha 25-50 ⇒ RC ready,
cohort recruitment is next phase"*. **(8)
Capstone:**
[`PHASE_8E_STATUS.md`](../../archive/phase-status/PHASE_8E_STATUS.md)
with 9-line verification table. 9 verifications
all green: `recall alpha review` renders · alpha
help shows review · pyflakes clean · demo CLI
still seeds · doctor still 5 GREEN · capture
status still live · users_live.json parses · all
3 new alpha dirs populated. Success bar: **Recall
leaves repo. Humans touch it.** Verdict:
infrastructure ready, cohort empty — Phase 8F
fills it.

### Previous phase

**Phase 8D — Release Candidate (RC1).** *Freeze
product. No new features · no redesign · no
cleanup · no archives. Only ship preparation.*
Recall becomes **v0.1.0-rc1**. 8 frozen surfaces:
launcher · extension · capture · resume · control
room · doctor · demo · installer. 4 new top-level
RC docs ([`VERSION.md`](../release/VERSION.md),
[`SCREEN_INDEX.md`](../product/SCREEN_INDEX.md),
[`DEMO_MODE.md`](../product/DEMO_MODE.md),
[`INSTALL_VERIFIED.md`](../release/INSTALL_VERIFIED.md))
+ 7 new release-kit docs under
[`release/`](../release/rc1) (README,
CHANGELOG_RC1, INSTALL, QUICKSTART, DEMO_FLOW,
KNOWN_ISSUES, LANDING_CHECK) + 1 new capstone
([`PHASE_8D_STATUS.md`](../../archive/phase-status/PHASE_8D_STATUS.md)).
**(1) Version lock:** v0.1.0-rc1 spec with
per-surface freeze-source table + build artifacts
(lite 216 MB / full 261 MB / extension 296 KB) +
known/blocked/ship/fixed bug summary. **(2) Release
kit:** quickstart matches directive verbatim
(install → open extension → browse → leave →
resume); demo flow is a 3-minute screen-share
script with anti-patterns; known-issues covers
the 5 ship bugs in plain language. **(3) Screen
freeze:** `assets/screenshots/` reduced from 7
dirs + 11 root PNGs to **4 canonical directories**
(`launcher-7e/` · `extension-7a/` · `alpha/` ·
`demo/`); 3 pre-7E/7A dirs + 11 root PNGs moved
to `archive/screenshots-history-rc/`; coverage
table maps all 6 required surfaces (hero / empty
/ resume / capture / extension / control room)
to specific files. **(4) Demo package:** new
**`recall demo run / reset / status`** CLI
(98-line [`app/core/demo_cli.py`](../../app/core/demo_cli.py)
dispatched in [`recall.py`](../../recall.py))
seeds 30 deterministic events / 12 sessions to
`~/.recall/events-demo/` (never the real log);
end-to-end smoke verified. **(5) Install test:**
honest walk on dev box — `recall doctor` 5
GREEN / 4 YELLOW (opt-in) / 0 RED; capture
status 36 events today / 13 investigations;
daemon endpoints all 200 (`/v1/health` 103 ms,
`/v1/recovery/recent` 122 ms, `/v1/threads/recent`
60 ms); demo CLI round-trip clean; both frontend
`tsc` exit 0; honest gap noted (clean Windows VM
walk = BUG-002, downgraded P0→P1). **(6) Landing
check:** zero dead links, 6/6 asset paths resolve,
6/6 GitHub URLs correct, 6/6 anchors map to
sections, 3 cosmetic-drift content-fill items
flagged. **(7) RC bug pass:** ledger re-classified
to RC1 gate — **P0 = 0** (BUG-001 verified fixed,
BUG-004 not-a-bug, EXT-001/002 + CTRL-002 +
BUG-008 reclassified post-beta/quarantined);
3 P1 must-fix-before-alpha (BUG-002 cold-boot
walk, BUG-003 SO+Stitch matcher audit, CTRL-001
empty-state copy); 2 P2 can-wait; 3 blocked
(macOS signing, cross-browser, smoke re-run).
**(8) Release-readiness score: 76 → 87 (+11)**
— composite of capture 82 / launcher 88 / resume
80 / extension 85 / control-room 85 / perf 95;
target was 85+; achieved. Path to 92 (stable
tag) is 5 follow-ups totalling ~2.5 days. **(9)
Capstone:** [`PHASE_8D_STATUS.md`](../../archive/phase-status/PHASE_8D_STATUS.md)
with 12-line verification table. Success bar:
**Recall becomes a release candidate. P0 = 0.
Score 87. v0.1.0-rc1.**

### Previous phase

**Phase 8C — Product Stabilization + Reality Pass.**
*No new features. No redesign. No cleanup. No
archives.* Make Recall reliable through measurement
+ honest documentation. 9 deliverables ship:
[`STABILITY/PERF.md`](../engineering/stability/PERF.md) —
real wall-clock timings (launcher construct 84.5 ms
warm / ~460 ms cold; CLI commands 230–365 ms; resume
preview 3.1 ms); [`STABILITY/CAPTURE.md`](../engineering/stability/CAPTURE.md)
— 30d event-store reality (166 browser events, 5
day-files, ChatGPT 20 / GitHub 16 / Google 55
working, StackOverflow 0 / Stitch 0 flagged as
matcher-audit-needed); [`STABILITY/LAUNCHER.md`](../engineering/stability/LAUNCHER.md)
— frozen 7E.1 widget tree walked offscreen, public
import contract holds, max 8 user-readable rows
regardless of event count; [`STABILITY/RESUME.md`](../engineering/stability/RESUME.md)
— pipeline alive (6 threads / 5 contexts / 4
resurfacing contexts), 0 recovery candidates is
*correctly conservative* not a bug; [`STABILITY/EXTENSION.md`](../engineering/stability/EXTENSION.md)
— 9-state machine, 7 captures, bundle byte-identical
(293 KB JS) across 8B; [`STABILITY/CONTROL.md`](../engineering/stability/CONTROL.md)
— 13 routes, 10 loaders, TypeScript clean exit 0;
[`BUGS_OPEN.md`](../engineering/BUGS_OPEN.md) — honest
ledger (1 P0 fixed + 1 P0 open + 5 P1 + 4 P2);
[`RELEASE_READINESS.md`](../release/RELEASE_READINESS.md)
— **composite score 76/100** (preview-grade, not
stable). **(0) Real regression caught and fixed:**
8B's archive over-reached — `app/main.py` imports
`demo_data`, `app/ui/onboarding.py` + `settings.py`
import `styles`. 8C restored `demo_data.py` +
`styles.py` + `widgets.py` + `cards.py` from
`archive/launcher-old/` and made the demo_data
import lazy in `main.py:392`. Launcher import path
now clean. **(1) Capture validation:** 166 browser
events / 30d on this box; pipeline writes real data
on real sites; 25-of-30 day-files absent is
expected ("daemon was off") not a reliability
defect. **(2) Launcher reality:** widget tree
matches 7E.1 freeze exactly — `LiveLauncher` →
`MinimalShell` → search + tagline + stacked
digest/empty + `TrustRow` + `ResumePreview` +
`RestoreToast` + 4 shortcuts. Construct stays
constant regardless of event count (event load is
lazy). **(3) Resume reality:** recovery engine
correctly returns 0 candidates because no thread on
this box passes `_MIN_EVENTS=4` + trust gate;
`ResumePreview` constructs in 3.1 ms whether
populated or not. **(4) Extension reality:** 9
states modeled, 7 captured (loading +
reconnecting transient by design), 1,973 LOC across
9 components, bundle 296 KB total (byte-identical
to pre-8B). **(5) Control room reality:** 13
routes / 10 loaders / 1 paths module —
`tsc --noEmit` exits 0; `RECALL_HOME` override
works. **(6) Performance:** measured 4 CLIs + 5
launcher subsystems + 4 daemon endpoints — all
within budget; 10K-event fixture is the single
remaining perf gap. **(7) Bug ledger:** 11 rows
total — `BUG-001` (8B import regression) fixed
in-flight; `BUG-002` (cold tray-icon boot human
walk) + `BUG-003` (SO+Stitch matcher audit) +
`BUG-004` (raw traceback on import fail) +
`EXT-001/002` + `CTRL-001/002` open. **(8)
Release-readiness composite 76/100** — capture 80,
launcher 85, resume 65, extension 80, control 80,
perf 70 — preview-shippable; stable tag needs the
5 highest-value follow-ups (cold-boot walk, matcher
audit, `_smoke_api.py` re-run, 10K perf fixture,
empty-state copy audit) for ~92 score. Verification:
`python -c "from app.main import main"` clean
post-fix · daemon endpoints respond 200 · daemon
returns 6 threads / 5 contexts / 4 resurfacing on
208-event store · offscreen `LiveLauncher`
constructs at `(700, 500)` in 84.5 ms warm · 9
extension state captures index correctly · control
room TypeScript exits 0. Success bar: **Recall
works in reality. Bugs are written down. Score
quantifies the gap to stable.**

### Previous phase

**Phase 8B — Tier 1 Cleanup + Repo Collapse.** Execute
the 8A audit's tier-1 recommendations. **No feature work,
no launcher rewrites, no UI changes, no new docs except
the 5 cleanup audit docs.** Result: **Python LOC −24 %
(29,544 → 22,435 = −7,109 lines moved to archive), asset
PNGs −54 % (102 → 47), asset folders −58 % (19 → 8),
extension components −73 % (11 → 3), `app/ui` live files
−55 % (11 → 5)**. **No code deleted** outside dep entries
+ 7 stale root PNGs; everything else is move-to-archive
(recoverable). **(1) Launcher collapse** — 8 legacy
modules (`launcher_legacy.py` 2675 LOC + `cards.py` 970
LOC + `widgets.py` 2471 LOC + `styles.py` 359 LOC +
`launcher_anims.py` 84 LOC + `launcher_digest.py` 89 LOC
+ `demo_data.py` + `ceremonies.py`) + 3 historical
capture scripts → [`archive/launcher-old/`](../../archive/launcher-old);
`app/ui/launcher.py` collapsed from 60→18 lines (no more
`RECALL_LAUNCHER=legacy` branch + no more back-compat
constant re-exports `LAUNCHER_WIDTH`/`SHADOW_MARGIN`/
`FOOTER_H`); the import contract `from app.ui.launcher
import Launcher` still resolves to `LiveLauncher`. **(2)
Asset cleanup** — 11 historical capture folders
(`launcher-live/` 6K · `launcher-minimal/` 6L ·
`launcher-refined/` 6M.1 · `launcher-compact/` 6M.2 ·
`launcher-recovery/` 6N · `launcher-reset/` 6O ·
`launcher-visible/` 6P.1 · `launcher-truth/` 6Q ·
`launcher-ship/` 6R · `launcher-final/` 7B ·
`launcher-merge/` 7B.1) → `archive/screenshots-history/`;
7 stale orphan PNGs in `assets/screenshots/` deleted
outright (`control-room.png` · `doctor-output.png` ·
`installer-flow.png` · `settings-dialog.png` ·
`launcher-first-week.png` · `launcher-loading.png` ·
`launcher-offline.png`). **(3) Extension pre-7A
components** — 8 dead files (`ContinueCard`, `DebugStrip`,
`DemoBanner`, `InvestigationCard`, `MemoryList`,
`Section`, `TrustSurface`, `states`) →
[`archive/extension-pre-7a/`](../../archive/extension-pre-7a);
vite build proves they were already tree-shaken (293 KB
JS bundle unchanged). **(4) Dependency cleanup** — 3
unused deps removed from `apps/web/package.json` (`clsx`,
`lucide-react`, `tailwind-merge`); `playwright` moved
from `dependencies` → `devDependencies` in
`apps/extension/ui/package.json`. **Deferred** to 8C: 5
orphan API routes (`thread_forget`, `contexts/recent`,
`sessions/recent`, `threads_clear_evolution_cache`,
`replay_day`) — kept until associated pydantic schemas
can be walked cleanly. 5 new audit docs land under
[`AUDIT/`](../../archive/AUDIT): `DELETE_PLAN.md` (per-row
delete log w/ verification per row), `LAUNCHER_FREEZE.md`
(official launcher path + public API + allowed/forbidden
changes — *no more launcher generations*),
`DEPENDENCY_DIFF.md` (before/after manifests + build
impact), `ASSET_FREEZE.md` (frozen active asset surface
+ what moved to history + freeze rule),
`PHASE_8B_STATUS.md` (capstone with before/after metrics
table). `DOC_INDEX.md` updated. Verification: `pyflakes
app/ui app/core api` clean · `recall doctor` GREEN on
config/events/daemon/extension/installer · `recall
capture status` clean (11 events today, 12
investigations) · offscreen `Launcher(FakeEngine())`
constructs at `(700, 500)` (Launcher import resolves to
`LiveLauncher`) · TypeScript clean across all 3 frontend
apps · `vite build` of extension produces 293 KB JS
bundle (identical to 8A — proves dead components were
already tree-shaken so no runtime change). Success bar:
**repo smaller. Same product. No regressions.**

### Previous phase

**Phase 8A — Full Product Audit.** *Stop building features.
Understand what Recall actually is today.* No launcher
redesign · no extension redesign · no control-room
redesign · no new memory systems · no new phases — audit
only. 7 evidence-based audit docs land under a new
top-level [`AUDIT/`](../../archive/AUDIT) folder:
[`SURFACES.md`](../../archive/AUDIT/SURFACES.md) catalogues every
runtime surface (36 LIVE / 2 LEGACY / 11 ARCHIVE / 1
REMOVE) with entry point + owner file + status;
[`DEAD_CODE.md`](../../archive/AUDIT/DEAD_CODE.md) lists parallel
trees + duplicate widgets + orphan API routes + dead
helpers w/ file:line citations + grep evidence (8 truly
DEAD pre-7A extension components, 7 LEGACY `app/ui/*.py`
behind `RECALL_LAUNCHER=legacy`, 3 duplicate widget pairs
+ 1 duplicate confidence-logic pair, 5 orphan API routes);
[`LAUNCHER_MAP.md`](../../archive/AUDIT/LAUNCHER_MAP.md) traces
every signal/slot/public method through the launcher (class
graph + state-flow per refresh + frozen anti-rules
mirroring 7E.1 `LAUNCHER_CONTRACTS.md` + the *one launcher*
collapse path);
[`CAPTURE_MAP.md`](../../archive/AUDIT/CAPTURE_MAP.md) cross-checks
the 7D `CAPTURE_FLOW.md` against current code, lists the
diagnostic CLI per failure mode, captures live measurement
(8 events today, 11 investigations, last event 38m ago);
[`ASSETS.md`](../../archive/AUDIT/ASSETS.md) inventories every
PNG under `assets/screenshots/` (5 ACTIVE folders + 2
`⭐` LIVE-launcher/extension capture folders + 11
HISTORICAL phase folders + 7 root-level ORPHAN PNGs
flagged for tier-1 delete);
[`DEPENDENCIES.md`](../../archive/AUDIT/DEPENDENCIES.md)
classifies all 43 packages across `requirements.txt` + 3
`package.json` files (20 runtime / 19 dev / 3 unused
`clsx`+`lucide-react`+`tailwind-merge` in marketing web /
1 misplaced `playwright` in extension's `dependencies`);
[`STATE.md`](../../archive/AUDIT/STATE.md) is the capstone (*what
Recall is · what ships · what's dead · what survives ·
tier-graded delete recommendations · live verify*). Three
parallel `Explore` subagents gathered evidence for the
dead-code/asset/dependency audits; launcher/capture/state
docs authored against the raw findings. `DOC_INDEX.md`
updated with a new `/AUDIT/` section at the top so the
audit docs are reachable from the standard doc index.
Live verification: `recall doctor` GREEN on
config/events/event-flow/daemon/extension/installer (5
YELLOWs all *user hasn't done yet* — autostart, recall://,
version drift); `recall capture status` clean (8 events
today, 11 investigations); `recall founder status` shows
[GREEN] Continuity restored 78%, Resume sessions 41,
Investigations 134, Extension connected 75%; TypeScript
clean across all 3 frontend apps (`extension/ui`,
`admin/web`, `web`); offscreen `LiveLauncher(FakeEngine())`
boots cleanly at `(700, 500)`. **No deletions performed.
No code changed.** This is the audit phase, not a feature
phase. Success bar: *understand entire repo. No more
accidental building. No more launcher rewrites. No more
code slop.*

### Previous phase

**Phase 7E.1 — Launcher Stability.** *Launcher boots every
time.* No visual work, no redesign — audit + freeze the
launcher's public Python interface. The 7E paint rewrite of
`MinimalSearchBar` silently dropped the `request_settings`
+ `request_close` signals while `LiveLauncher.__init__`
still wired both via `self._search.request_settings.connect(
self.request_settings.emit)` + `self._search.request_close.
connect(self.hide)` — every `python recall.py` crashed
during launcher construction with `AttributeError:
'MinimalSearchBar' object has no attribute
'request_settings'`. Reproduction (offscreen, no Qt GUI
needed): `LiveLauncher(FakeEngine())` raised
`AttributeError` at the connect line. **Fix**: restore both
dropped signals on `MinimalSearchBar` + add the rest of the
documented contract — `searchChanged(str)` as an alias of
`query_changed(str)` (both wired to
`QLineEdit.textChanged` via two parallel `connect` calls so
either spelling fires on every keystroke), `submit(str)`
already present, plus `clear()` + `selectAll()` methods.
The two *may-not-exist* signals (`request_settings`,
`request_close`) are declared even though no widget in 7E
fires them — consumers `connect(...)` safely; later paints
can wire an on-screen affordance without touching host
wiring. The `MinimalSearchBar` docstring grows a "Public
contract (Phase 7E.1 — frozen)" block listing the 5
signals + 3 methods. New
[`LAUNCHER_CONTRACTS.md`](../product/LAUNCHER_CONTRACTS.md)
documents the frozen interface: per-class signals + methods
+ stable attributes table; constructor signature for
`LiveLauncher(search_engine, event_logger=None,
parent=None)`; keyboard-shortcut table (`Esc` / `Ctrl+K` /
`Meta+K` / `1`); the wiring map from `app/main.py` →
`LiveLauncher` → `MinimalSearchBar`; and the freeze rule:
*future launcher phases may **add** to the surface; they
**must not remove or rename** the symbols below* — with the
slow-path procedure (update host first → wait one release →
remove from widget → update doc) for the rare case a major
break needs to happen. Verification: offscreen
`LiveLauncher(FakeEngine())` constructs cleanly
(`CONSTRUCT OK · DEFAULT_SIZE: (700, 500)`); all 5 signals
present, all 3 methods callable; both `query_changed` +
`searchChanged` fire on text type (`{'query_changed': 1,
'searchChanged': 1}`); `request_settings.emit()` propagates
to `LiveLauncher.request_settings` (hits=1); `python
recall.py doctor` green on config / events / extension /
installer (daemon RED is the expected not-running state).
No widget paint changed, no layout changed, no new
features. Receipt:
[`PHASE_7E.1_STATUS.md`](../../archive/phase-status/PHASE_7E.1_STATUS.md).
Success bar: *launcher boots every time.*

### Previous phase

**Phase 7E — Launcher Final Product Pass.** *Freeze engine,
recovery, extension, control room — launcher only. Make
memory visible, hierarchy clear, single surface at 700×500.*
7B.1's Stitch-aligned single-document workspace was
beautiful but solved *floating overlays* by **removing
memory from the surface**; the launcher looked calm but
felt prototype-y. 7E restores memory while honouring the
calm-product feel. Canvas **700 × 500** hard clamp (was
740 × 500), warm `#F5F2ED` page outside; one white inner
card with radius **24** + padding 20/16/20/14 (L/T/R/B);
**no nested cards, no glass, no transparency** —
`MinimalWindow.paintEvent` paints the full warm page, then
a manual two-offset rounded shadow + the white inner card
body, all via `QPainter` (no `QGraphicsDropShadowEffect`).
Five sections stack inside the card with **no per-section
chrome**: (1) **52-px search bar** (warm-paper fill,
hand-drawn glyph, lavender focus ring, inline `Ctrl K`
hint chip auto-hidden on focus, placeholder *Search
investigations…*); (2) **13-px / 9-pt muted-lavender
tagline** *Recall noticed unfinished work* directly under
the search bar — the launcher's posture line; (3)
**Continue hero** rewritten with **HIGH/MED/LOW signal
variants** driving the 6-px left accent rail (HIGH=filled
lavender · MED=soft lavender via `ACCENT_SOFT` · LOW=
outline-only stroked rail) + matching confidence pill
(HIGH=accent filled · MED=accent-soft · LOW=ghost
outline); 110-px tall, title (elided) + Resume button
(fixed 116-px w/ `1` chip) on the title row + inline
evidence (`2 files - 2 tabs - returned 2d` via
`_evidence_from_targets`) on the bottom row; (4) **NEW
RECENT MEMORY section** —
[`recent_memory.py`](../../app/ui/launcher_v3/recent_memory.py)
ships `MemoryRow` dataclass + `RecentMemoryList` widget
(up to 5 rows, 18 px each); `LiveLauncher._load_recent_memory`
pulls events from `EventStore.iter_events(days=2)` and
maps `Event.payload → MemoryRow(time, source, label)` via
`_short_source` (ChatGPT / Claude / Gemini / Google /
DuckDuckGo / Bing / domain title-case) + `_short_label`
(title / query / file basename / chat title). **This fixes
the *memory invisible* problem the prior launcher shapes
had** — user can glance at the launcher and confirm Recall
actually saw what they did; (5) **OTHER WORK rebuilt**
from 7B.1's zero-cost stub into real 36-px rows w/
strength dot (lavender if `surfaces ≥ 3`, ink-4 otherwise)
+ title (elided) + last-seen mono caption right-aligned
(`3d`/`5d`/`1w`, via `events.humanize_age` in
`_thread_to_v3`), max 3 rows, 1-px hairline dividers
between consecutive rows; (6) **TrustRow** pinned at the
bottom — 22-px row w/ 4 tiny pills `LOCAL · NO CLOUD · N
EVENTS TODAY · M INVESTIGATIONS`; counts derived live by
`_load_trust_counts` from the same disk reads
(`EventStore.iter_events_for_date(today)` +
`~/.recall/threads.json` length) the Phase 7D `recall
capture status` CLI uses, so pill values match the CLI
report. **Removed from the surface**: Show example + Start
working giant buttons · centered empty states · large
vertical spacing · floating pills · dark overlays ·
prototype illustrations · the empty-state swap (the
launcher now always shows *something memory-shaped* — even
with no HIGH recovery, Recent Memory + OTHER WORK carry
the surface). Hotkeys preserved: `Esc` / `Ctrl+K` /
`Meta+K` / `1`. Demo path updated for the new digest
signature: synthesises a `MemoryRow` list from the demo
payload's `timeline` so the demo reads identically to a
live populated state. 3 files snapshotted into
[`archive/launcher-7b1/`](../../archive/launcher-7b1)
with per-file README: `minimal_7b1.py` ·
`recovery_panel_7b1.py` · `investigation_panel_7b1.py`. 5
captures (`home · high · med · low · no_hero`) in
`assets/screenshots/launcher-7e/`. New
[`LAUNCHER_FINAL.md`](../product/LAUNCHER_FINAL.md)
**supersedes** `LAUNCHER_VISUAL_MERGE.md` (7B.1) as the
launcher's live contract — 7B.1 → 7E delta table + frozen
paint/geometry/typography/per-region tables + 5-row state
catalogue + the removed-list. Engine + recovery + resume
pipeline (6P) + trust/inspector CLIs (6Q) + capture CLIs
(7D) all **untouched** — 7E is paint + composition only.
pyflakes clean. Receipt:
[`PHASE_7E_STATUS.md`](../../archive/phase-status/PHASE_7E_STATUS.md).
Success bar: *open Recall → see unfinished work + recent
memory + resume path + trust within 3 seconds.* **Launcher
frozen.**

### Previous phase

**Phase 7D — Capture Truth Audit.** *Verify Recall actually
remembers.* **No UI work, no redesign** — engine + CLI +
docs only. New
[`recall capture status`](../../app/core/capture_cli.py) CLI
prints a read-only ASCII summary of today's pipeline state
(`events today` + per-kind tally for the 7 known kinds —
`browser_visit · browser_search · chat_session · open ·
reveal · desktop_window · query` — + `returns (>= 30 min
gap)` + `investigations` + `last event` timestamp/kind/age).
Daemon **not required**: reads
`~/.recall/events/YYYY-MM-DD.jsonl` + `~/.recall/threads.json`
directly off disk; degrades gracefully when the threads
cache is missing (returns `0`). When `events today == 0`
prints three remediation hints (run the daemon, check the
extension is paired, run the demo). New
[`recall capture tail`](../../app/core/capture_cli.py) is a
`tail -f`-style live inspector: prints every existing
event in today's file first (so the user sees context),
then polls the daily JSONL file at 500-ms intervals and
prints new lines as one compact `HH:MM:SS  kind  detail
title` row each. Survives the midnight day-rollover by
reopening the file on every tick (`_today_filename()` re-
derived per loop iteration); survives truncate/rotate by
falling back to `pos = 0`. `--once` mode prints existing
events then exits (script-friendly). Both commands dispatch
from `recall.py`'s fast path before the `app.main` import
so they stay cheap — no Qt boot, no engine import. New
[`CAPTURE_FLOW.md`](../product/CAPTURE_FLOW.md) documents
the **seven hops** end-to-end (browser observers → loopback
POST → daemon ingest routes → EventLogger.log → ThreadBuilder
→ RecoveryEngine.recover_recent → LiveLauncher), names the
file + function that implements each hop, lists the CLI that
confirms the data made it through (the new capture CLIs +
the existing `recall inspect` + `recall trust review`), and
closes with a scripted 7-step verification walk (ChatGPT /
GitHub / StackOverflow / Google → leave ≥ 30 min → return →
confirm Continue document → `recall inspect` confirms
`Strength: HIGH`). Live measurement on this machine: 71
events today (64 tabs + 7 chats), 11 investigations, last
event 1h ago — ChatGPT / Google / Stitch / Kotak visits
all present in the tail output. pyflakes clean. Receipt:
[`PHASE_7D_STATUS.md`](../../archive/phase-status/PHASE_7D_STATUS.md).
Success bar: *Recall truly remembers — and now you can prove
it.*

### Previous phase

**Phase 7B.1 — Launcher Visual Merge.** *Rebuild launcher
toward the Stitch reference. Current launcher discarded
visually; keep logic, replace surface.* 7B locked the
launcher into one root card with three regions inside —
search row + dense hero + vertical OTHER WORK list — and at
product distance the Raycast-shaped density still read as
*utility*. The Stitch reference proves a calmer **document
workspace** shape works better. Canvas grows to **740 ×
500** (hard clamp via `setFixedSize`, single white workspace
inside a 16-px gutter, radius 22) on the warm `#F4F1EC`
page — no transparency, no glass. **Search bar rewritten**
to 52-px row with warm-paper fill (`#FAF7F1`), hand-drawn
glyph, and a right cluster: **settings cog + close × +
`Ctrl K` hint chip** (cog forwards to the existing
`request_settings` signal so `app/main.py`'s settings flow
lights up; × hides the launcher). Placeholder reads **`Start
typing to recover…`**. **Continue document** replaces the
dense hero row: 220-px calm card with a soft warm-paper
tint (`#FBF8F2`), 6-px lavender left accent rail clipped to
the rounded corners, `CONTINUE` eyebrow inside the card,
14.5-pt bold title (elided), bulleted body (file/tab/chat/
search counts derived locally via the same `_body_from_targets`
buckets the resume preview uses + the engine's *returned
after Nd* clause when `preview_caption` carries one — pulled
via a new `_extract_gap_clause` helper in `live.py`), and a
right-aligned fixed-width 116-px Resume button with the `1`
shortcut chip. Reads as a *document with an action*, not a
command-palette row. **Empty workspace rebuilt**: new
`_InfinityGlyph` paints a lavender lemniscate (two
overlapping ellipses + a soft `ACCENT_SOFT` halo) via
`QPainter` — no Unicode glyph dependency; 20-pt bold
headline *Everything you've seen, searchable.* (≈ 26 logical
at Windows DPI per directive's *Title 26*); 14-px sub *Your
digital continuity layer.*; two stacked 200-px buttons
*Show example* (accent-filled) + *Start working* (outline).
**Bottom strip** replaces the centred footer: 22-px row
with trust line *End-to-end encrypted. Local storage only.*
on the left + tiny `Privacy · Demo · Docs · Browser` text
links on the right (links inert in 7B.1; placeholders for
future deep links — the *Design UI now. Engine later.*
pattern). **OTHER WORK list removed from the visible
surface** — single-focus tool. `InvestigationCardV3` +
`InvestigationList` reduced to zero-cost stubs (`HEIGHT =
0`, hidden, `populate()` discards inputs) so the engine
path keeps constructing them while the launcher never
renders. Hotkeys: kept `Esc` / `Ctrl+K` / `Meta+K` / `1`;
removed `2-9` (nothing to navigate to). 3 files snapshotted
into [`archive/launcher-raycast/`](../../archive/launcher-raycast)
with per-file README: `minimal_7b.py` ·
`recovery_panel_7b.py` · `investigation_panel_7b.py`. 5
captures (`empty · active · resume · demo · overflow`) in
`assets/screenshots/launcher-merge/`. New
[`LAUNCHER_VISUAL_MERGE.md`](../product/LAUNCHER_VISUAL_MERGE.md)
**supersedes** `LAUNCHER_SHIP_AUDIT.md` (7B) as the live
contract — carries 7B → 7B.1 delta table + frozen paint/
geometry/typography/per-region tables + 5-row state
catalogue. Engine + recovery layer + resume pipeline (6P)
+ trust/inspector CLIs (6Q) all **untouched** — 7B.1 is
paint + composition only. pyflakes clean. Receipt:
[`PHASE_7B.1_STATUS.md`](../../archive/phase-status/PHASE_7B.1_STATUS.md).
Success bar: *Looks like product. Not utility.*

### Previous phase

**Phase 7B — Launcher Production Freeze.** *Turn the launcher
into shipping product.* No new features, no control room, no
extension, no alpha, no docs except the audit. 6R froze the
layout cleanly but kept the per-section-card pattern; at
arm's length that read as *three floating overlays* rather
than *one product object*. 7B collapses everything into a
**single white root card** on the warm-paper page. Window
unchanged (680 × 440 hard clamp, `setFixedSize`); paint
pattern inverts. The `MinimalWindow.paintEvent` now: (1)
fills the full window with `BG = #F4F1EC`, (2) draws a manual
two-offset-rounded-fill shadow (3-px offset, 18 α — replaces
the prior `QGraphicsDropShadowEffect` so the hot path stays
off the software rasterise route), (3) draws the white root
card body at radius 22 inside the 14-px outer margin with a
1-px `BORDER_RAISED` outline. `MinimalShell` provides 20-px
internal padding (top/sides) + 18 (bottom). **Search bar**
rewritten as a 52-px row with a warm-paper fill (`#F4F1EC`)
inside the root + 2-px `BORDER_RAISED_STRONG` border +
lavender focus ring + hand-drawn `_SearchIcon` + inline
`Ctrl K` hint chip (auto-hidden on focus). **Hero rewritten
— no card chrome**: fixed 88-px height, **only the 6-px
lavender left accent rail** (rounded ends; brighter rail +
1-px lavender outline when keyboard-focused). Title row
(title elided + `HIGH` confidence pill + **fixed-width
112-px Resume button**) on top + chips row beneath (max 3,
derived from `suggested_targets`). **OTHER WORK list — no
wrapping card**: rows paint directly on the root with 1-px
`BORDER_RAISED` hairline dividers between, max 3 visible.
Footer (*local only · no cloud*) pinned at the bottom of
the root card. New **`Ctrl+K`** + **`Meta+K`** QShortcuts
in `LiveLauncher.__init__` focus + select-all the search
input from anywhere inside the launcher. New
**`RECALL_DEBUG=1` timing log** writes one line per
`show_centered` to stderr — `[recall.launcher.timing]
show_centered  N ms  (budget 400)` — so the directive's
*<400 ms launcher open* budget can be confirmed on a real
machine. Search emits on every keystroke (no debounce
client-side) so the *<100 ms search* budget lands by
construction. New
[`capture_launcher_ship.py`](../../infra/scripts/capture/capture_launcher_ship.py)
produces 5 PNGs (`hero · empty · focus · demo · overflow`)
in `assets/screenshots/launcher-ship/`. New
[`LAUNCHER_SHIP_AUDIT.md`](../product/LAUNCHER_SHIP_AUDIT.md)
**supersedes** `LAUNCHER_FINAL_AUDIT.md` (6R) as the live
contract — carries the 6R → 7B delta table + frozen paint/
geometry/motion/per-region tables + 9-row visibility-pass
table (covering 100%/125%/150% scaling + arm-length + dark/
bright room + title overflow + empty + demo) + 2-row
performance-budget table + the explicit *Launcher frozen
forever* freeze rule. 3 files snapshotted into
[`archive/launcher-final/`](../../archive/launcher-final)
with per-file README documenting the per-section-card era:
`minimal_6r.py` · `recovery_panel_6r.py` ·
`investigation_panel_6r.py`. Engine + recovery layer +
resume pipeline (6P) + trust/inspector CLIs (6Q) all
**untouched** — 7B is paint + ergonomics only. pyflakes
clean. Receipt:
[`PHASE_7B_STATUS.md`](../../archive/phase-status/PHASE_7B_STATUS.md).
Success bar: *open Recall · see remembered work · press
Resume · leave*.

### Previous phase

**Phase 7A — Extension Product Surface.** *Stop launcher,
control room, founder tooling, docs, alpha dashboards. Only
extension.* Reference Arc / Raycast / Linear / Readwise Reader
/ Perplexity sidebar. Popup frozen at **440 × 640** (`body
{ width / height; overflow: hidden }`). Six fixed-position
regions in a single column. **(1) Header**: 26-px lavender
mark + breathing daemon dot (1.6 s easeInOut when connected)
+ subtitle (*Connected locally · Reconnecting… · Daemon not
running · Browser is offline · Connecting…*) + Search +
Settings icon-buttons. Removed: event-count badge, desktop
badge, wrench icon. **(2) Continue hero**: full-width white
card, **6-px lavender accent rail**, `CONTINUE` eyebrow
(9-px tracked), tiny `HIGH` confidence pill, title (14 px
600, one line, elided), max **3** chips derived from the
candidate's caption, **fixed-width 112-px Resume button**
with the `1` shortcut chip, capped at **110 px** tall.
Single hero, ever. **(3) Active investigations**: vertical
stack of 48-px rows inside one white card — strength dot
(accent or ink-4 based on surface count) + title (12.5 px
600, elided) + last-seen caption (10.5 px ink-3) + quiet
right chevron. Max 4 visible without scroll. **(4) Today
timeline**: 3-column grid (mono time / bold source 88-px /
label flex) with `staggered` enter motion; empty rail
surfaces a 36-px painted illustration in place of the prior
*"No browser memory captured yet"* prose. **(5) Activity**:
two side-by-side cards — Browser (lists *tabs · navigation
· returns · searches* with `capturing/idle/offline` pill
driven by connection × events_today) + Desktop (lists
*files · editors · integrations* with `capturing/soon/
offline` pill driven by `desktop_apps_today`). The Desktop
card's `SOON` pill surfaces the *Design UI now. Engine
later.* seam honestly. **(6) Trust strip**: 4 tiny pinned
pills `LOCAL ONLY · NO CLOUD · 0 UPLOADS · DAEMON OK`,
replaces the ~140-px `TrustSurface` section with ~40 px
of pinned footer. Plus a **SearchOverlay** that slides down
on **Ctrl/Cmd+K** with an inline search input + groupings
for *Investigations · Files · Returns · Events* (in-memory
filter on the popup's existing state — the directive's
*Design UI now. Engine later.* applies; swap `useResults`
when a unified endpoint lands). New design tokens: **page
`#F5F2ED`**, card `#FFFFFF`, sunken `#F0ECE5`, hairline
`#E6DED4`, accent `#8B7FE3`, shadow `0 12 32 rgba(0,0,0,.06)`
(card) + `0 20 56 rgba(0,0,0,.12)` (search overlay) — *no
glass, no neon, no blur*. Motion scale tightened to the
directive's exact **120 / 180 / 240** via `--motion-fast/
normal/slow`. Eight new components under
`apps/extension/ui/src/components/v2/` (`Header`, `Hero`,
`Investigations`, `Timeline`, `Activity`, `TrustStrip`,
`SearchOverlay`, `States`); `App.tsx` rewritten to compose
them. State machine + API client + demo overlay flow
preserved untouched. `capture_extension.mjs` gains
`OUT_7A` + 7 fixtures (the directive's *empty · capturing
· active · resume · offline · search · demo* audit row);
the `search` capture fires Ctrl+K via Playwright keyboard
so the overlay paints in the screenshot. New
[`EXTENSION_PRODUCT_AUDIT.md`](../product/EXTENSION_PRODUCT_AUDIT.md)
is the frozen-product checklist: paint table · motion table
· per-region contracts · 7-row state catalogue with one
capture per row · the *Design UI now. Engine later.*
capture-architecture table. Receipt:
[`PHASE_7A_STATUS.md`](../../archive/phase-status/PHASE_7A_STATUS.md).
`tsc --noEmit` + `vite build` clean (~293 KB JS). 21
captures total (7 new in `extension-7a/`). Success bar:
*open extension → immediately understand: Recall remembered
work · Recall can continue it · Recall is running*.

### Previous phase

**Phase 6R — Launcher Finalization.** *Stop feature work. Only
launcher. Make it feel like shipped software.* **No docs**
(besides the audit + status). **No trust system, no recovery
ranking, no control room, no extension.** The launcher is now
a **frozen product surface**; no more launcher phases after
this. Window **680 × 440** hard clamp (`setFixedSize`,
min = max, no resize), `WA_TranslucentBackground = False` —
*no glass, no blur, no floating opacity tricks*. Paint:
`BG = #F4F1EC` (was `#F3F1ED`), new `BORDER_RAISED_STRONG =
#E7DED3` for the 2-px search-bar border, new `SHADOW_SEARCH_*
= 0 8 24 rgba(0,0,0,.06)` scales under `SHADOW_CARD_* = 0 12
32 rgba(0,0,0,.08)` so the search bar reads beneath the hero
in z-order despite painting at the column top. **Search bar
rewritten**: 52 px tall, radius 14, lavender focus ring,
hand-drawn `_SearchIcon` (no Unicode glyph dependency),
placeholder *Search work…*. **Hero card rewritten**: fixed
88 px height, **6-px lavender left accent strip** clipped to
the rounded border, title (one line, elided with `...`) +
tiny **HIGH** confidence pill + **fixed-width 112-px
Resume button** + max-3 chip row beneath the title derived
from `suggested_targets` via `_chips_from_targets`. **Removed
from hero**: subtitle · meta caption · prose · *Why this?*
link · `signals` parameter · `request_why` signal. **OTHER
WORK rewritten**: vertical list (was horizontal in 6O), 44
px rows (lavender 6-px dot + title + quiet painted chevron),
max 3 rows, white card wrapper with 1-px inter-row dividers
— *horizontal row read as adrift text at arm's length; the
vertical list reads as a list of things you can click*.
**Empty surface restacked**: lavender square · headline ·
*Show example* (primary accent-filled) · *Start working*
(secondary layered card — renamed from *Start normally* per
directive) — both buttons 200-px fixed width, **inside the
centred stack**, no longer floating page furniture. New
single-line **footer** *local only · no cloud* at the bottom
of every surface (populated + empty), ~10 px ink-3, centred.
Live launcher's `WhyThisSheet` wiring removed: `_recovery_to_v3`
no longer passes `signals`, demo path no longer synthesises
demo signals, the escape cascade collapsed back to *preview >
hide* (the *why sheet > preview > hide* cascade went with
the sheet). New
[`capture_launcher_final.py`](../../infra/scripts/capture/capture_launcher_final.py)
produces 4 PNGs (`hero` · `empty` · `focus` · `overflow`) in
`assets/screenshots/launcher-final/`. New
[`LAUNCHER_FINAL_AUDIT.md`](../product/LAUNCHER_FINAL_AUDIT.md)
is the frozen-product checklist (geometry table · paint table
· hero / OTHER WORK / empty / footer contracts · 7-check
visibility audit: arm-length · dark-room · 50 % / 125 %
scaling · title overflow · empty · demo · resume · the
freeze rule). Four files snapshotted into
[`archive/launcher-debt/`](../../archive/launcher-debt) with
per-file README: `minimal_6p1.py` (6P.1 visibility surface) ·
`recovery_panel_6q.py` (6Q hero with the *Why this?* link) ·
`investigation_panel_6o.py` (6O horizontal row) ·
`why_sheet_6q.py` (6Q signal overlay). The engine-side
signals layer (`recovery.explain_signals` + `recall inspect`
+ `bad_recoveries`) **stays in active code** — only the
launcher's surface changed. Receipt:
[`PHASE_6R_STATUS.md`](../../archive/phase-status/PHASE_6R_STATUS.md).
Success bar: **open Recall · understand instantly · click
Resume · done**.

### Previous phase

**Phase 6Q — Continuity Truth.** *Make Recall feel correct.
Not pretty. Not bigger. Correct.* **No launcher redesign, no
extension redesign, no control-room work — investigation
quality only.** Three layers shipped together. (1) The
**canonical contract**: new
[`INVESTIGATION_PRINCIPLES.md`](../product/INVESTIGATION_PRINCIPLES.md)
codifies the 7 rules (*same topic returns → merge · one-off
visit → suppress · passive browsing → suppress · deep work →
promote · unfinished work → strongest signal · multi-day
return → boost · casual reopen loops → decay*) + a 9-row
table of the trust-floor gates in `recovery.py` (`_MIN_EVENTS`,
`_RECOVERY_WINDOW_DAYS`, `_LAST_PHASE_RECENCY_DAYS`,
`_DEPTH_KINDS`, `_MIN_DISTINCT_TARGETS`, `_MIN_CONFIDENCE`,
`_MIN_RESUME_INTENT`, …); new
[`PROMOTION_THRESHOLDS.md`](../product/PROMOTION_THRESHOLDS.md)
documents the **LOW (0-1) / MED (2-3) / HIGH (4+)** bands +
**5 overrides**: *unfinished overrides all* · *returned_after_gap
boosts +1 band* · *duplicate penalty* (engine-side de-dup) ·
*noise penalty* (`_MIN_RESUME_INTENT` floor) · *ledger
penalty* (-1 band if `bad_recoveries.jsonl` flagged the
thread within 14 days). (2) The **user-feedback loop**: new
[`app/core/bad_recoveries.py`](../../app/core/bad_recoveries.py)
appends to `~/.recall/bad_recoveries.jsonl` (closed 4-reason
enum: `wrong_topic` · `already_done` · `noise` · `duplicate`;
trust contract: **no content**, only `thread_id` + `reason`
+ `ts`; **local-only**, **inspectable plain JSONL**); the
engine writes `signals.ledger_flagged = 1.0` on flagged
threads (`_LEDGER_WINDOW_DAYS = 14`); the launcher's
`_populate_digest` reads the flag and **skips HIGH
promotion** for flagged candidates — the only user-feedback
input into ranking; everything else is derived. (3) The
**introspection surface**: new
[`recall inspect <id>`](../../app/core/inspect_cli.py) CLI
prints a deterministic ASCII card (Title · Strength · Signals
· Evidence · Decision — `SHOW HERO` / `SHOW IN OTHER WORK` /
`SUPPRESS`); accepts candidate id, thread id, or title
substring; ASCII-only (no Unicode rules so it survives
`cp1252`). New
[`recall trust review`](../../app/core/trust_cli.py) prints
the 14-day ledger table + **bad % / silence % / resume %**
rates computed from `bad_recoveries.jsonl` + `counters.json`.
New [`WhyThisSheet`](../../app/ui/launcher_v3/why_sheet.py)
overlay opens from a small lavender *Why this?* link on the
hero's meta row (`_WhyLink` widget on
`RecoveryCardV3`); lists `recovery.explain_signals(candidate)`
verbatim — **no AI text, no prose, no scoring numbers**, just
short observational lines like *"unfinished work · returned
after a 2-day gap · 5 targets involved · multiple surfaces
engaged"*. The launcher's escape cascade goes *why sheet >
preview > hide* so the topmost overlay closes first. New
[`capture_launcher_truth.py`](../../infra/scripts/capture/capture_launcher_truth.py)
produces 4 PNGs in `assets/screenshots/launcher-truth/`
(`hero_with_why` · `why_sheet` · `showcase` ·
`ledger_demoted`). New
[`SHOWCASE_TRUTH.md`](../product/SHOWCASE_TRUTH.md) is the
directive's *Showcase Reality* — a three-investigation
scripted walk (proposal draft · RLHF notes · WebSocket
issue) verifying **only one hero ever surfaces** + the *Why
this?* contract + the ledger-demotion path; carries a
6-row failure-mode table the showcase exists to catch.
[`archive/recovery-ranking/`](../../archive/recovery-ranking)
documents *what 6Q kept untouched* (every gate, every
weight, `_behavior_clause`, `_classify_targets`), *what 6Q
added* (the ledger flag + `explain_signals` + 2 CLIs + the
Why sheet), and *what 6Q considered and rejected* (a learned
ranker — violates CLAUDE.md determinism rule; a second
freshness half-life — double-counts the existing 14-day +
7-day + 3.5-day decay; a chat-heavy promotion bump —
duplicates `_W_SURFACE_BREADTH`; an engine-side duplicate
de-dup pass — deferred until the launcher's 1-hero cap stops
being enough). Receipt:
[`PHASE_6Q_STATUS.md`](../../archive/phase-status/PHASE_6Q_STATUS.md).
Success bar: user says *"Yes. That is exactly what I wanted
back."*

### Previous phase

**Phase 6P.1 — Launcher Visibility Recovery.** *Make the
launcher immediately visible and usable.* **No new features.
No recovery logic work. No resume work.** Visual correction
only. The 6O reset went too far on paint: the near-white page
(`#F7F5F2`) and the white cards differed by ~10 % luminance,
so the layered surfaces blended into each other; the search
input had no chrome of its own; the OTHER WORK row was bare
text adrift on the page; the empty-state buttons floated below
the headline with no fixed widths; and the launcher window
painted flush to its window edge with no visible frame. The
launcher read like a CSS reset that had forgotten to set
borders. This phase keeps the 6O structure (680 × 460 window,
HIGH-only gate, max-3 investigations, fixed 100-px hero) and
restores the *layering*. Concrete changes: `theme.BG` warms
to **`#F3F1ED`** (6 % darker than the white cards — enough
contrast for layering to read at arm's length); new
`BORDER_RAISED = #E4DED6` solid hairline replaces the rgba
hairlines that read as muddy ink on white; new
`SHADOW_CARD_* = 0 12 32 rgba(0,0,0,.08)` (vs the previous
`0 8 24 rgba(0,0,0,.07)`); new `_LayeredCard` base class —
white fill + 1-px warm-grey border + soft drop shadow —
inherited by the search bar (radius 14), the recovery hero
(radius 22), and the new `_InvestigationsCard` wrapper
(radius 18) around the OTHER WORK row. The search bar now
has a hand-drawn `_SearchIcon` (`QPainter` circle + handle —
no Unicode glyph dependency, so it renders identically across
hosts) + a lavender focus ring (2-px `T.ACCENT` border on
`FocusIn`, dropped back to the warm hairline on `FocusOut`);
inactive cards paint at ~0.96 alpha so the focused card is
always the foreground element. The hero gains a **soft 4-px
lavender left accent strip** painted inside the rounded border
(clipped so the corners follow the card curve) and a
**fixed-width 110-px Resume button** (`_ResumeButton.WIDTH`)
so the right edge of the card is stable across recoveries
with different title lengths. The empty surface stacks **logo
dot → headline → sub → buttons** with a fixed 16-px gap and
two **140-px fixed-width buttons** (primary accent-filled,
secondary layered card). `MinimalWindow` reserves a **12-px
outer margin** and paints a 1-px warm-grey border around the
page at radius 24 so the launcher reads as a discrete object,
not as a patch of paint covering the desktop. New
[`capture_launcher_visible.py`](../../infra/scripts/capture/capture_launcher_visible.py)
produces 4 PNGs in
`assets/screenshots/launcher-visible/` (`hero` · `empty` ·
`focus` · `investigations`). New
[`LAUNCHER_VISIBILITY.md`](../product/LAUNCHER_VISIBILITY.md)
carries the directive's *problem · fix · before / after*
audit with a 9-row comparison table. Success bar: *Launcher
readable from 2 meters away.*

### Previous phase

**Phase 6P — Resume Reality.** *Click Resume. Actually
continue work.* The pre-6P v3 launcher had a one-line
`_on_restore` stub that called the API to resolve a
`RestorationPlan` and immediately dropped the plan on the
floor — the user clicked Resume, the launcher closed, and
nothing reopened. This phase wires the click to real OS opens
without touching geometry, theme, or the engine. Two new
widgets: a light
[`ResumePreview`](../../app/ui/launcher_v3/resume_preview.py)
overlay (Continue + a derived count breakdown like *2 files ·
2 tabs · 1 search* + Cancel / Resume now buttons, Esc cancels,
no modal darkening, painted on top of the digest inside the
launcher window), and a 3-second
[`RestoreToast`](../../app/ui/launcher_v3/restore_toast.py)
that pins to the bottom with up to three restored target
names (*Restored · backoff.py · client.py · MDN*) or a calm
failure line (*Could not reopen 1 item · Continue anyway* /
*Could not reach the engine · try again*). `_on_preview_accept`
calls `APIClient.recovery_restore`, walks `plan.steps` in the
engine's prescribed order (files → chats → tabs → searches),
and dispatches each via `_open_target` — `os.startfile` on
Windows, `open` on macOS, `xdg-open` on Linux. File paths are
existence-checked before logging an `open` event so a phantom
file doesn't pollute the log; failures are counted as `skipped`
and the chain continues (no hard stop). The demo path runs
through the same preview → toast cycle so the WebSocket
recovery example reads identically to a live restore. New doc
trio: [`RESUME_FLOW.md`](../product/RESUME_FLOW.md) (the
end-to-end pipeline audit with the *why files first* rationale
+ the failure-mode table) + the
[`SHOWCASE_RUN.md`](../product/SHOWCASE_RUN.md) scripted
verification (the step-by-step demo run + failure-injection
matrix) + the receipt
[`PHASE_6P_STATUS.md`](../../archive/phase-status/PHASE_6P_STATUS.md).
The pre-6P stubs (`_on_restore`, `_on_demo_resume`) were
removed and documented in
[`archive/resume-old/README.md`](../../archive/resume-old/README.md).

### Previous phase

**Phase 6O — Launcher Reset.** The launcher overbuilt across
6I → 6N — multi-state heroes, confidence sentences, preview
cards, returns rows, sort priorities. The reset directive
deletes everything that doesn't support one of two actions:
**resume the recovery** or **dismiss and start fresh**. Window
**680 × 460**, paper white, radius 24, soft shadow only.
Single column: search at top (capped 620 px, centred) →
CONTINUE section + 100-px **fixed** hero (`setFixedHeight` —
no dynamic growth) → OTHER WORK section + up to **3 bare-text
investigation titles** (max 3, equal width, no overflow chip,
no animations). Or — when no HIGH recovery — centred headline
*Recall notices unfinished work* + body *Work normally. /
Return later.* + *Show example* / *Start normally* buttons.
**Deleted from the runtime surface**: returns row · trust
line · MED/LOW signal variants · confidence sentences ·
preview card on empty · status dot on pills · evidence chip
parser · `+N more` overflow chip · `sort_for_digest` priority
sorter · per-card footers · daemon/doctor/version info.
`RecoveryCardV3` rewritten from scratch — single fixed 100-px
hero, title + ambient meta + Resume right (no signal/
confidence/sentence params); new `_EliderLabel` paints `…`
when the title can't fit the constrained column.
`InvestigationCardV3` is now a bare `QLabel`; `InvestigationRow`
caps at 3 equal-width titles. `LiveLauncher._populate_digest`
gates the hero on `n_targets ≥ 4` (HIGH only) and falls
through to the empty surface otherwise; `DEFAULT_SIZE` =
**680 × 460** (was 720 × 520 in 6M.2). Six files moved to
`archive/launcher-overbuild/` with a per-file README: the
prior `minimal.py` · `recovery_panel.py` ·
`investigation_panel.py` · `digest.py` · `capture_launcher_compact.py`
· `capture_launcher_recovery.py`. New
[`capture_launcher_reset.py`](../../infra/scripts/capture/capture_launcher_reset.py)
produces 2 PNGs (populated · empty) in
`assets/screenshots/launcher-reset/`. New
[`LAUNCHER_RESET.md`](../product/LAUNCHER_RESET.md) carries
the directive's *what removed · why launcher failed · new
philosophy* audit (3 failure modes: *every directive added,
no directive removed* · *became a memory center, not a tool*
· *visual hierarchy inverted*; 3 design rules: *one surface ·
HIGH or nothing · add nothing the user doesn't act on*).
Receipt:
[`PHASE_6O_STATUS.md`](../../archive/phase-status/PHASE_6O_STATUS.md).

### Previous phase

**Phase 6N — Recovery Precision.** The launcher *feels
intelligent*. **No redesign. No geometry changes. No
control-room work.** `RecoveryCardV3` gains a `signal`
parameter driving three distinct states — **HIGH** (Resume,
accent fill, *Recall thinks this was interrupted work*),
**MED** (Continue, halfway tint, *Seen again after return*),
**LOW** (Review ghost button, plain white fill, *Weak signal —
review first*). `_ResumePill` rewritten as a three-variant
widget (`kind="resume"|"continue"|"review"`); paint per
variant: accent-filled / accent-soft + border / ghost outline.
Card outer paint also varies by signal (fill + border
strength scale with confidence). New optional `sentence` arg
on the constructor; `DEFAULT_SENTENCES` map carries the
directive's exact strings; LiveLauncher passes
`getattr(c, "why_summary", None)` so a future engine field
overrides without further widget changes. Evidence chips
capped at **3** (directive's exact rule); parser refuses to
fabricate. New
[`sort_for_digest()`](../../app/ui/launcher_v3/investigation_panel.py)
pure helper orders investigations by the directive's rank:
`0 unfinished` (strength ≥ 3) · `1 returned` (last_touch
contains return / revisit / back) · `2 recent` (today / now /
active / Nh / ≤3d) · `3 passive` (everything else); within a
rank, high-strength threads win. `LiveLauncher._populate_digest`
sorts before handing the list to `MinimalInvestigations`,
which still caps at 6M.2's `MAX_VISIBLE = 3` + drops surplus
into the `+N more` overflow chip. `MinimalEmpty._build_preview_card`
adds a *PREVIEW* caption + a non-interactive LOW-state
`RecoveryCardV3` (canonical WebSocket fixture, sentence
*A real recovery will replace this*); the card is rendered
through the same widget the live launcher uses, so the empty
state's preview is a *literal* preview, not an illustration.
Auto-dismiss is upstream — `MinimalEmpty` only renders when
the engine is empty. 5 new captures in
`assets/screenshots/launcher-recovery/`
(high · medium · low · empty · resume). New
[`RECOVERY_VISUAL_AUDIT.md`](../product/RECOVERY_VISUAL_AUDIT.md)
carries the directive's *high / medium / low / silence /
bad recovery* audit + a cross-cutting rules table. Receipt:
[`PHASE_6N_STATUS.md`](../../archive/phase-status/PHASE_6N_STATUS.md).

### Previous phase

**Phase 6M.2 — Launcher Geometry Recovery.** The Phase 6M.1
refinement drifted the launcher away from a Raycast / Arc
utility shape toward a dashboard shape; this phase recovers
the proportions. **No new features. No theme rewrite. No
engine work.** Layout-only retune. Geometry: window
**720 × 520** (was 820 × 640) / max **760 × 560** / column
max **640** (was 760) / `MIN_WIDTH = 520` (was 600) / outer
window radius **24** (was 28). `MinimalSearchBar` capped at
640 px wide and centred (was full-width); height 48,
placeholder *Search investigations…*; min-width 360 to keep
the placeholder readable. `RecoveryCardV3.HEIGHT = 92` (was
124) with a `MAX_HEIGHT = 116` cap to prevent dashboard
sprawl; layout reshaped from vertical-stack-with-stretch into
a **2×2 grid** — title TL · confidence TR · chips BL · Resume
BR. Eyebrow row (accent dot + *CONTINUE*) removed (duplicate
of chip strip + badge). `_ResumePill` 34→**36** (directive's
exact value). `MinimalInvestigations.MAX_VISIBLE = 3` (was 4);
pill height 40→**44**; pill paint radius 20→**14**.
`MinimalReturns.MAX_ROWS = 2` (was 3); section eyebrow
removed, replaced with a 1-px `T.HAIRLINE` `QFrame` above
the rows; row height 28→22; when-label 10.5 pt bold
INK_2 → 9.5 pt INK_3; body 14→**11**; no leading dot. Digest
vertical rhythm changed from one global `setSpacing(20)` to
**explicit per-gap `addSpacing()`** so the directive's
non-uniform `16/12/8` spec lands (hero ↦ investigations 16,
investigations ↦ returns 12, returns ↦ trust 8). Theme:
`GUTTER = 20` (was 28), `SECTION_GAP = 16` (was 20), new
`RETURNS_GAP = 8`, `FS_HERO = 20` (was 22), `FS_TITLE = 14`
(was 16), `FS_BODY = 13` (was 14), `FS_LABEL = 10` (was 11),
`FS_META = 11` (was 12), `FS_SECTION = 13` (was 14), new
`FS_CONFIDENCE = 10`. New
[`capture_launcher_compact.py`](../../infra/scripts/capture/capture_launcher_compact.py)
produces 4 PNGs in `assets/screenshots/launcher-compact/`:
compact · hero · investigations (4 threads → 3 pills +
`+1 more`) · empty. The 6M.1 captures stay on disk as the
*before* set the regression doc references. New
[`LAUNCHER_REGRESSION.md`](../product/LAUNCHER_REGRESSION.md)
audit carries the directive's *why old looked better /
what changed / what fixed* table — 13-token comparison +
narrative on the *Raycast ↔ Notion* axis. Numbering: this
directive's *Phase 6M.1* label conflicts with the prior
Launcher Refinement that already shipped; filed as **6M.2**
so both audit trails survive. Receipt:
[`PHASE_6M.2_STATUS.md`](../../archive/phase-status/PHASE_6M.2_STATUS.md).

### Previous phase

**Phase 6M.1 — Launcher Refinement.** Refinement-only pass to
make the launcher *feel shipped*. **No new features. No engine
work. No control-room work.** Theme tokens refit to the
directive's exact values: paper-white `#F7F5F2`, **solid**
white cards (every `alpha` → 255; the `glass` feel is gone),
shadow `0 8 24` (`SHADOW_SOFT_OFFSET = 8`), card radius 20,
spacing rhythm **28 / 20 / 12**, typography **22 / 14 / 12**
(`FS_HERO` / `FS_SECTION` / `FS_META`). `surfaces.GlassCard.paintEvent`
flipped to a solid white fill; the `alpha` constructor arg is
silently clamped to 255 so downstream callers don't need
edits. `RecoveryCardV3` hero now bottom-aligns its action row
(stretch added above the chip strip + Resume pill) and drops
the *Surfaced because you left this mid-flow.* footer line —
the chip strip + confidence badge already say it. Investigation
strip rewired to **equal-width pills** via `addWidget(pill, 1)`;
new `_OverflowChip` widget paints a dashed-border `+N more`
chip when there are more than 4 threads (the directive's *no
scrolling, no walls* rule). `MinimalEmpty` rewritten without
the wrapping `GlassCard` — vertically centred icon (lavender
tinted square + painted lavender dot, no Unicode glyph so
every system font renders identically) + headline (22 px) +
sub (14 px) + 2 buttons (38 px tall, radius 12) + trust line.
`MinimalShell.MAX_WIDTH = 760` (was 860); `MIN_WIDTH = 600`
(was 760). `MinimalWindow.DEFAULT_SIZE` + `LiveLauncher.DEFAULT_SIZE`
= **820 × 640** (was 920 × 720). Three pre-refinement capture
scripts (`capture_launcher_v3.py` / `capture_launcher_live.py`
/ `capture_launcher_minimal.py`) moved to
`archive/launcher-refine/` with a README documenting why each
was archived (their fixtures reference layout values that no
longer match). New
[`capture_launcher_refined.py`](../../infra/scripts/capture/capture_launcher_refined.py)
produces 5 PNGs in `assets/screenshots/launcher-refined/`:
hero · empty · investigations (4 pills + `+2 more` overflow) ·
resume (focused hero) · focused (focused hero + populated
pill row). New
[`LAUNCHER_REVIEW.md`](../product/LAUNCHER_REVIEW.md) carries
the directive's audit table (*removed · kept · why · future*).
Numbering: previous Phase 6M (Desktop Memory Layer) shipped
this session with its own
[`PHASE_6M_STATUS.md`](../../archive/phase-status/PHASE_6M_STATUS.md); this
phase files as **6M.1** to preserve that history. Receipt:
[`PHASE_6M.1_STATUS.md`](../../archive/phase-status/PHASE_6M.1_STATUS.md).

### Previous phase

**Phase 6M — Desktop Memory Layer.** Recall now sees work
outside the browser. **Metadata only — no screenshots, no OCR,
no audio, no pixel data.** New `app/core/desktop/` package with
six modules: `events.py` (the `desktop_window` kind +
`DesktopWindowEvent` payload), `processes.py` (PID → exe-name
via `QueryFullProcessImageNameW`; pure ctypes, no `psutil`),
`windows.py` (foreground-window probe via `GetForegroundWindow`
+ `GetWindowTextW`; non-Windows hosts → `None` gracefully),
`sessions.py` (`FocusAggregator` — pure, no-I/O block aggregator
with 30 s minimum focus + 60 s re-focus consolidation + EXE
blocklist), `watcher.py` (daemon-thread polling loop with
`RECALL_DESKTOP=off` kill switch). API gains
`POST /v1/events/desktop` (mirrors the other ingest hooks +
auto-dismiss / daily-loop) and `DesktopWindowIn` schema; the
schema's whitelist enforces the *metadata only* contract at the
request boundary. `ALLOWED_KINDS` gains `desktop_window` so the
ingestion service accepts it. New `/desktop` route in the
control room reads `~/.recall/events/*.jsonl` directly,
filters for `kind === "desktop_window"`, aggregates per app
(focus time + blocks + switches + longest session + sampled
titles) and renders the directive's four signals — *apps,
focus, top tools, session time*. Extension popup gains a small
accent `⊞-N` badge next to the *N today* caption (renders
when `health.desktop_apps_today > 0`; pre-6M daemons silently
report 0). Nav row + Ctrl+K palette entry added. The watcher
is opt-in (`desktop_capture_enabled` in `~/.recall/config.json`);
the engine accepts events from any source. Aggregator
unit-tested without Qt — two probes emit two events with
correct durations. **Purely additive layer** — deleting
`app/core/desktop/` removes the watcher without breaking any
downstream artifact (CLAUDE.md rule for new layers honoured).
Receipt:
[`PHASE_6M_STATUS.md`](../../archive/phase-status/PHASE_6M_STATUS.md).
Product story:
[`DESKTOP_LAYER.md`](../product/DESKTOP_LAYER.md).

### Previous phase

**Phase 6L — Launcher Simplification.** The v3 launcher
(promoted in 6K) is stripped to a **single floating surface** —
no admin panel, no control room, no analytics view. System info
lives **only** in the founder control room
(`apps/admin/web/`); the launcher itself surfaces *one thing to
do* + a small ambient strip + a quiet returns row. New
`app/ui/launcher_v3/minimal.py` ships 8 classes:
`MinimalSearchBar` (one rounded input, no nav) ·
`MinimalInvestigations` (horizontal pill flow, max 4 visible,
never scrolls) · `MinimalReturns` (thin 3-row list, hidden on
empty) · `MinimalTrust` (one quiet local-only line) ·
`MinimalEmpty` (single floating card with the directive's
exact *Recall notices unfinished work.* + *Work normally.
Return later. Recall fills itself.* + Show example / Start
normally + trust line) · `MinimalDigest` (composes hero +
investigations + returns + trust) · `MinimalShell` (single
column, width clamped **760-860 px**, outer gutter 32, section
gap 24) · `MinimalWindow` (top-level QWidget, 920 × 720
default). LiveLauncher rewired: composes `MinimalShell`
instead of the 3-column shell from Phase 6I; reads **one**
recovery (was 3) for the hero — *only ONE primary card*;
investigations stay capped at 4 but render as horizontal pills,
not vertical cards; new `_build_returns()` reads
`daily_loop.summary(days=3)` best-effort and surfaces the
today / yesterday return rows (counts only — per Phase 6F
trust contract); `_refresh_context()` deleted (no context
column to refresh). Three widgets archived to
`archive/launcher-v2/` — `shell.py` (Shell + ContextColumn) ·
`sidebar.py` (rich left rail with nav + search + accent-dot
markers) · `window.py` (LauncherWindow that hosted the Shell)
— with a README documenting *why removed* per class. Capture
pipeline:
[`capture_launcher_minimal.py`](../../infra/scripts/capture/capture_launcher_minimal.py)
produces 4 PNGs in `assets/screenshots/launcher-minimal/`
(hero · empty · investigations · resume — focus state).
Default import unchanged
(`from app.ui.launcher import Launcher` still returns
LiveLauncher); `RECALL_LAUNCHER=legacy` escape hatch from
Phase 6K still works. **No engine touches, no recovery-logic
change.** Receipt:
[`PHASE_6L_STATUS.md`](../../archive/phase-status/PHASE_6L_STATUS.md).
Archive doc:
[`archive/launcher-v2/README.md`](../../archive/launcher-v2/README.md).

### Previous phase

**Phase 6K — Launcher Promotion.** The v3 widget tree built in
Phase 6I becomes the actual launcher. **No parallel surface, no
dead launcher path — promote safely.** New
`app/ui/launcher_v3/live.py` ships `LiveLauncher(QWidget)` with
the legacy constructor signature
(`search_engine, event_logger=None`), legacy signals
(`request_settings`, `_request_search`), and legacy public API
(`show_centered()`, `invalidate_digest()`,
`_refresh_idle_state()`) so `app/main.py` constructs it
unchanged. Composes the v3 Shell (Sidebar + ContextColumn)
with a `QStackedLayout` centre that swaps between `EmptyDigest`
and `DigestColumn` based on engine state; reads live data via
the existing `app.core.api_client.APIClient`
(`recovery_recent(n=3)` + `threads_recent(n=6)` + `health()`);
honours the demo overlay from Phase 6D
(`demo_mode.is_active()` short-circuits to the canonical
WebSocket / Healthcare pitch / RLHF investigations);
auto-dismisses on real ingest. Confidence derivation mirrors
v2 + extension (`n_targets ≥ 4 → high · 2-3 → medium · 0-1 →
low`). Keyboard layer: `Esc` hides, `1-9` focuses the n-th card
across the recovery + investigation panels combined. The
previous 1130-line `app/ui/launcher.py` moved to
`app/ui/launcher_legacy.py` (archived in place — not on the
default import path, not dead). New `app/ui/launcher.py` is a
**38-line adapter**: default returns `LiveLauncher as Launcher`;
`RECALL_LAUNCHER=legacy` returns the legacy class — the
directive's *promote safely* escape hatch. Backwards-compat
constants (`LAUNCHER_WIDTH` / `SHADOW_MARGIN` / `FOOTER_H`)
re-exported from the legacy module so `launcher_anims.py` and
`launcher_digest.py` keep working unchanged. No `setFixedHeight`
anywhere in the v3 widget tree; centre column clamped 420-720
px. New
[`capture_launcher_live.py`](../../infra/scripts/capture/capture_launcher_live.py)
produces 6 PNGs in `assets/screenshots/launcher-live/`
(overview · continue · empty · trust · focus · recovery)
constructed from the same v3 widgets LiveLauncher composes at
runtime. **No engine touches**, **no recovery-logic changes**.
Receipt:
[`PHASE_6K_STATUS.md`](../../archive/phase-status/PHASE_6K_STATUS.md).

### Previous phase

**Phase 6J — Control Room V2.** The founder dashboard at
`apps/admin/web/` becomes the founder's actual operating system.
**No mock values. No placeholder buttons. Everything
actionable.** Global chrome: sticky top bar (Recall wordmark +
three live pills daemon/readiness/installs + `⌘K` palette
trigger) + sticky bottom bar (version + doctor verdict +
build label). Command palette (Ctrl+K) fuzzy-searches across
14 routes + 9 directive-named actions; selecting a route
navigates; selecting an action copies the canonical CLI
command — *no server endpoint executes anything*. Two new
loaders: `logs.ts` (reads 5 sources — doctor / recovery /
daily / alpha / release with per-source verdicts) and
`screenshots.ts` (scans 6 buckets — launcher-v2 / launcher-v3
/ extension-v2 / demo / alpha / legacy flat — with
*missing-marker* detection of every directive-named PNG).
Left nav rebuilt to the directive's 12-section order (4
groups: overview · cohort · engine · ship · lab) with
hotkeys 1-9 + 0 on the first ten rows. Five new routes:
`/extension` (popup pairing health + ext/engine version drift
+ capture rate + repair commands), `/launcher` (v3 gallery +
v3↔v2 side-by-side diff strip + promotion checklist surfacing
Phase 6I's deferred wire-in), `/experiments` (8 feature flags
read live from `~/.recall/config.json` + `~/.recall/demo.json`
+ env, each with live value + flip command + verdict; 4
alpha-gate cards; 3 GREEN-floor threshold cards), `/logs`
(5-source picker + filtered substring viewer + clipboard
download), `/screenshots` (per-bucket galleries + missing-
marker strips). Recovery Lab extended with kind filter strip
(all + 6 kinds) + confidence distribution + 7-day
return-after-gap heatmap. System Console gains *Copy
diagnostics* — pre-built markdown blob (handles + mtimes +
verdicts; no URLs, no filenames, no PII) to clipboard via a
client helper. Admin web `public/screens/` populated with 5
mirrored bucket directories so every gallery renders real
thumbnails. Next.js build clean (14 routes, all
`ƒ` server-rendered, 87.4 KB first-load shared). **No engine,
no Python, no marketing-site, no extension touches.** Receipt:
[`PHASE_6J_STATUS.md`](../../archive/phase-status/PHASE_6J_STATUS.md). User
manual: [`CONTROL_ROOM_V2.md`](CONTROL_ROOM_V2.md).

### Previous phase

**Phase 6I — Launcher Rebuild.** The launcher becomes a premium
surface — Linear × Arc × Raycast feel — without touching the
engine or the recovery logic. **UI only.** New parallel package
`app/ui/launcher_v3/` ships the directive's twelve modules:
`theme.py` (warm white `#F7F5F2`, lavender accent, radii
20-28, soft shadow only) · `motion.py` (timings 120/180/260,
OutCubic, fade/slide/expand factories, no bounce/spring) ·
`surfaces.py` (the seven directive primitives: `GlassCard` /
`FloatingPanel` / `SoftDivider` / `Pill` / `ConfidenceBadge` /
`TimelineChip` / `StatusDot`) · `recovery_panel.py`
(`RecoveryCardV3` 124-px hero with chip row + ConfidenceBadge +
accent Resume pill carrying the `1` shortcut + hover lift +
focus ring + Enter/Space/`1` keyboard activation) ·
`investigation_panel.py` (`InvestigationCardV3` with timeline
strip + target chips + last-touch + 4-segment resume-strength
bar) · `trust_panel.py` (three-row footer: Daemon · Local only
· Captured today) · `search_panel.py` (QStackedLayout of empty
↔ results) · `digest.py` (`DigestColumn` composes recovery +
investigations + trust; `EmptyDigest` carries the directive's
first-run surface — *"Recall notices unfinished work."*
headline + Show example / Start normally button pair + trust
line) · `sidebar.py` (220 px left rail; Recall wordmark +
search QLineEdit + 4-row section nav with accent-dot active
marker) · `shell.py` (3-column composition + `ContextColumn`
right rail with Today / Doctor / version blocks) ·
`window.py` (`LauncherWindow` top-level `QWidget`, default
1100 × 720, warm-white page bg) · `__init__.py` (barrel of 22
public symbols). All cards use *minimum* heights, not fixed —
the directive's *remove hardcoded heights* rule honoured.
Centre column clamped 420-720 px so the floating feel survives
wide screens without cramping small ones. 5 new captures in
`assets/screenshots/launcher-v3/` (digest / continue / empty /
trust / focused — the focus shot shows the recovery card's
accent ring). Live `app/ui/launcher.py` is **untouched** — the
v3 package sits alongside, ready for promotion on a follow-up
with its own QA matrix; the directive's anti-rule
(*no engine, no recovery*) held strictly. Receipt:
[`PHASE_6I_STATUS.md`](../../archive/phase-status/PHASE_6I_STATUS.md).

### Previous phase

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
[`PHASE_6H_STATUS.md`](../../archive/phase-status/PHASE_6H_STATUS.md).

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
[`PHASE_6G_STATUS.md`](../../archive/phase-status/PHASE_6G_STATUS.md).

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
[`PHASE_6F_STATUS.md`](../../archive/phase-status/PHASE_6F_STATUS.md).

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
[`PHASE_6E_STATUS.md`](../../archive/phase-status/PHASE_6E_STATUS.md). Pairs
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
| 6I | Launcher Rebuild | **No engine work, no recovery-logic changes — UI only** · new parallel package `app/ui/launcher_v3/` with the directive's 12 named modules: `theme.py` (warm white `#F7F5F2`, lavender accent, radii 20-28) · `motion.py` (120/180/260, OutCubic, fade/slide/expand, no bounce) · `surfaces.py` (7 primitives: `GlassCard` / `FloatingPanel` / `SoftDivider` / `Pill` / `ConfidenceBadge` / `TimelineChip` / `StatusDot`) · `recovery_panel.py` (`RecoveryCardV3` 124 px hero with chip row + ConfidenceBadge + accent Resume pill + `1` shortcut chip + focus ring + Enter/Space/`1` keyboard activation) · `investigation_panel.py` (`InvestigationCardV3` w/ timeline strip + target chips + 4-segment resume-strength bar) · `trust_panel.py` (three-row footer) · `search_panel.py` · `digest.py` (`DigestColumn` + `EmptyDigest` w/ Show example + Start normally) · `sidebar.py` (220 px left rail w/ search + 4-row section nav) · `shell.py` (3-column composition + `ContextColumn` right rail w/ Today + Doctor + version) · `window.py` (`LauncherWindow` top-level, 1100×720 default) · `__init__.py` (22-symbol barrel) · cards use minimum heights (no `setFixedHeight`); centre column clamped 420-720 px · 5 captures in `assets/screenshots/launcher-v3/` (digest / continue / empty / trust / focused) · live `app/ui/launcher.py` **untouched** — v3 package parallel-shipped, ready for promotion on a future phase |
| 6J | Control Room V2 | **No mock values, no placeholder buttons, everything actionable** · global chrome (sticky top bar w/ Recall wordmark + 3 live pills daemon/readiness/installs + `⌘K` search; sticky bottom bar w/ version + doctor verdict + build label) · Ctrl+K command palette fuzzy-searching 14 routes + 9 actions (Run doctor / Bake / Alpha report / Export trust / Open screenshots / Open alpha / Open journal / Open daily / Open logs) · 2 new loaders (`logs.ts` reads 5 sources w/ verdicts; `screenshots.ts` scans 6 buckets w/ missing-marker detection) · left nav rebuilt to directive's 12-section order (4 groups, hotkeys 1-9+0) · 5 new routes: `/extension` (pairing health + drift + capture rate + repair commands), `/launcher` (v3 gallery + v3↔v2 side-by-side diff strip + promotion checklist), `/experiments` (8 feature flags from `~/.recall/config.json` w/ flip commands + 4 alpha gates + 3 threshold cards), `/logs` (5-source picker + filtered viewer + download cmd), `/screenshots` (per-bucket gallery + missing markers) · Recovery Lab extended w/ kind filter strip + confidence distribution + 7-day return-after-gap heatmap · System Console gains *Copy diagnostics* button (redacted markdown blob to clipboard; no PII, no URLs, no filenames) · `apps/admin/web/public/screens/` populated w/ 5 mirrored buckets · Next.js build clean (14 routes, all `ƒ` dynamic, 87.4 KB first-load shared) · **No engine, no Python, no marketing-site, no extension touches** |
| 6K | Launcher Promotion | **No parallel surface, no dead launcher path — promote safely** · new `app/ui/launcher_v3/live.py` ships `LiveLauncher` w/ legacy constructor + signals + public API (`show_centered` / `invalidate_digest` / `_refresh_idle_state`) · composes v3 Shell + Sidebar + ContextColumn + `QStackedLayout` empty↔digest swap · reads live API (`recovery_recent` + `threads_recent` + `health`) · honours demo overlay (auto-dismiss preserved) · confidence derivation matches v2 + extension · keyboard: Esc hides / `1-9` focuses n-th card · previous 1130-line `app/ui/launcher.py` archived in place as `launcher_legacy.py` · new `app/ui/launcher.py` is a **38-line adapter** (default v3, `RECALL_LAUNCHER=legacy` for fallback) · `LAUNCHER_WIDTH` / `SHADOW_MARGIN` / `FOOTER_H` re-exported · 6 captures in `assets/screenshots/launcher-live/` (overview / continue / empty / trust / focus / recovery) · no engine touches, no recovery-logic change · pyflakes clean · doctor unchanged · `from app.ui.launcher import Launcher` now returns `LiveLauncher` |
| 6L | Launcher Simplification | **Single floating surface — no admin panel, no control room, no analytics view** · new `app/ui/launcher_v3/minimal.py` ships 8 classes: `MinimalSearchBar` · `MinimalInvestigations` (horizontal pills, max 4, never scrolls) · `MinimalReturns` (3-row strip, hidden on empty) · `MinimalTrust` · `MinimalEmpty` · `MinimalDigest` · `MinimalShell` (width 760-860 px, outer gutter 32) · `MinimalWindow` (920×720 default) · LiveLauncher rewired to compose `MinimalShell` (was 3-column Shell + Sidebar + ContextColumn); reads **one** recovery for the hero (was 3); investigations stay capped at 4 but render horizontal pills; new `_build_returns()` reads `daily_loop.summary(days=3)` for the recent-returns strip · 3 widgets archived to `archive/launcher-v2/` (shell.py + sidebar.py + window.py) w/ README documenting *why removed* per class · 4 captures in `assets/screenshots/launcher-minimal/` (hero / empty / investigations / resume) · pyflakes clean · default import unchanged · `RECALL_LAUNCHER=legacy` escape hatch preserved · no engine, no recovery-logic touches |
| 6M | Desktop Memory Layer | **Metadata only — no screenshots, no OCR, no audio, no pixel data** · new `app/core/desktop/` package: `events.py` (`desktop_window` kind + `DesktopWindowEvent`) · `processes.py` (PID→exe via `QueryFullProcessImageNameW`, pure ctypes) · `windows.py` (foreground probe; non-Windows → graceful `None`) · `sessions.py` (`FocusAggregator` w/ 30 s floor + 60 s re-focus consolidation + EXE blocklist) · `watcher.py` (daemon thread, `RECALL_DESKTOP=off` kill switch) · `POST /v1/events/desktop` + `DesktopWindowIn` schema (rejects fields outside whitelist at boundary) · `ALLOWED_KINDS += desktop_window` · `/desktop` control-room route reads `~/.recall/events/*.jsonl` directly, surfaces apps / focus / top tools / session log · extension popup: small accent `⊞-N` badge next to today caption · nav + palette entries added · watcher opt-in via `desktop_capture_enabled` in `~/.recall/config.json` · aggregator unit-tested without Qt · admin build clean (15 routes) · extension build clean (293.75 KB JS, +0.7 KB for the badge) · purely additive layer — deleting `app/core/desktop/` removes the watcher without breaking anything downstream |
| 6M.1 | Launcher Refinement | **No new features, no engine work, no control-room work — refinement only** · `theme.py` refit: paper-white `#F7F5F2`, **solid** white cards (every `alpha` → 255), shadow `0 8 24` (`SHADOW_SOFT_OFFSET = 8`), card radius **20**, spacing **28/20/12** (`GUTTER`/`SECTION_GAP`/`CARD_GAP`), typography **22/14/12** (`FS_HERO`/`FS_SECTION`/`FS_META`) · `surfaces.GlassCard.paintEvent` → solid white fill (alpha clamped); `_ResumePill` + every card paints opaque · `RecoveryCardV3` hero bottom-aligns action row, drops *Surfaced because…* footer line, solid accent fill · investigation strip rewired to **equal-width pills** (`addWidget(pill, 1)`) + new `_OverflowChip` widget (dashed `+N more`) when threads > 4 · `MinimalEmpty` rewritten without the wrapping `GlassCard`: vertically centred icon (lavender tinted square + painted dot, no Unicode glyph) + headline + sub + 2 buttons + trust line · `MinimalShell.MAX_WIDTH = 760` (was 860) / `MIN_WIDTH = 600` (was 760) · `MinimalWindow.DEFAULT_SIZE` + `LiveLauncher.DEFAULT_SIZE` = **820 × 640** (was 920×720) · 3 legacy capture scripts (v3 / live / minimal) moved to `archive/launcher-refine/` w/ README · new `capture_launcher_refined.py` produces 5 PNGs in `assets/screenshots/launcher-refined/` (hero / empty / investigations / resume / focused) · `LAUNCHER_REVIEW.md` audit (removed/kept/why/future) · numbering: 6M (Desktop Memory) docs preserved; this phase files as 6M.1 |
| 6M.2 | Launcher Geometry Recovery | **No new features, no theme rewrite, no engine work — layout recovery only** · 6M.1's loose geometry had drifted the launcher away from Raycast/Arc shape toward dashboard shape; this phase retunes tokens + widgets to the directive's compact reset · geometry: window **720 × 520** (was 820×640) / max 760×560 / column max **640** (was 760) / outer window radius **24** (was 28) · `MinimalSearchBar` capped 640 px + centred (was full-width), height 48, placeholder *Search investigations…*, min-width 360 so the placeholder stays readable · `RecoveryCardV3.HEIGHT = 92` (was 124) + `MAX_HEIGHT = 116` cap · hero layout reshaped to **2×2 grid** (title TL · confidence TR · chips BL · Resume BR); eyebrow row removed (duplicate of chip strip+badge) · `_ResumePill` 34→**36** · `MinimalInvestigations.MAX_VISIBLE = 3` (was 4); pill height 40→44; radius 20→**14** · `MinimalReturns.MAX_ROWS = 2` (was 3); section eyebrow removed, replaced w/ a 1-px hairline `QFrame`; row 28→22, when-label 10.5pt→9.5pt INK_3, body 14→11, no leading dot · digest spacing changed from one `setSpacing(20)` to explicit per-gap `addSpacing()` so the **16/12/8** rhythm lands · theme retuned: `GUTTER 28→20` · `SECTION_GAP 20→16` · new `RETURNS_GAP=8` · `FS_HERO 22→20` · `FS_TITLE 16→14` · `FS_BODY 14→13` · `FS_LABEL 11→10` · `FS_META 12→11` · `FS_SECTION 14→13` · new `FS_CONFIDENCE=10` · new `capture_launcher_compact.py` produces 4 PNGs in `assets/screenshots/launcher-compact/` (compact · hero · investigations w/ `+1` overflow · empty) · new `LAUNCHER_REGRESSION.md` audit (why old looked better / what changed / what fixed — 13-token table + Raycast↔Notion axis narrative) · numbering: directive labelled *6M.1* (third 6M-prefix directive this session); filed as **6M.2** so both 6M.1 (Refinement) and 6M.2 (Recovery) audit trails survive |
| 6N | Recovery Precision | **No redesign, no geometry changes, no control-room work — recovery experience only** · `RecoveryCardV3` gains `signal` param (HIGH/MED/LOW) driving CTA verb (Resume/Continue/Review), pill paint variant, card fill + border strength, and confidence sentence · `_ResumePill` rewritten as 3-variant widget (`kind="resume"\|"continue"\|"review"`); per-kind paint (accent-filled / accent-soft+border / ghost outline) · card paint per signal: HIGH=accent-soft fill + accent line α=80; MED=halfway tint + accent line α=48; LOW=plain white + hairline α=24 · new `DEFAULT_SENTENCES` map carries directive's exact strings; optional `sentence` constructor arg overrides; LiveLauncher passes `getattr(c, "why_summary", None)` so engine-side sentences land without further widget changes · evidence chips capped at **3** (directive); parser unchanged — never fabricates · new `sort_for_digest()` pure helper orders investigations: `0 unfinished` (strength≥3) · `1 returned` (last_touch contains return/revisit/back) · `2 recent` (today/now/active/Nh/≤3d) · `3 passive`; within rank, high-strength wins · `LiveLauncher._populate_digest` sorts before passing to strip (still caps at 6M.2's `MAX_VISIBLE=3` + `+N more`) · `MinimalEmpty._build_preview_card` adds PREVIEW caption + non-interactive LOW-state `RecoveryCardV3` (canonical WebSocket fixture, sentence *A real recovery will replace this*); auto-dismiss is upstream (state machine swaps to `MinimalDigest` on first real ingest) · 5 captures in `assets/screenshots/launcher-recovery/` (high/medium/low/empty/resume) · new `RECOVERY_VISUAL_AUDIT.md` (5 sections — high/medium/low trust + silence + bad recovery + cross-cutting rules table) |
| 6O | Launcher Reset | **We overbuilt — stop adding, delete complexity, build ONE surface** · window **680 × 460** paper white, radius 24, soft shadow only · single column: search (capped 620, centred) + CONTINUE section + **fixed 100 px hero** (HIGH only, `n_targets ≥ 4`) + OTHER WORK section + **3 bare-text titles** equal width · or empty (centered headline + body + 2 buttons) · `RecoveryCardV3` rewritten — `setFixedHeight(100)`, single `_ResumeButton`, ambient meta text (no chips, no badges, no sentences, no signal variants); new `_EliderLabel` paints `…` on long titles · `InvestigationCardV3` is now a bare `QLabel`; `InvestigationRow` caps at 3 equal-width, no `+N` overflow, no animations · `minimal.py` slimmed to 5 classes (`MinimalSearchBar`, `MinimalDigest`, `MinimalEmpty`, `MinimalShell`, `MinimalWindow`) · `LiveLauncher.DEFAULT_SIZE = (680, 460)` (was 720×520); `_populate_digest` gates on HIGH and falls through to empty otherwise · **deleted from the runtime surface**: returns row · trust line · MED/LOW signal variants · confidence sentences · preview card · status dots · evidence chip parser · `+N` overflow · `sort_for_digest` · footers · daemon/doctor/version blocks · 6 files moved to `archive/launcher-overbuild/` (prior `minimal.py` · `recovery_panel.py` · `investigation_panel.py` · `digest.py` · 6M.2/6N capture scripts) w/ per-file README · new `capture_launcher_reset.py` produces 2 PNGs (populated · empty) in `assets/screenshots/launcher-reset/` · new `LAUNCHER_RESET.md` (directive's *what removed · why launcher failed · new philosophy* audit: 3 failure modes + 3 design rules) |
| 6P | Resume Reality | **Click Resume — actually continue work. No UI redesign, no launcher changes, no control-room work, restore flow only** · pre-6P `_on_restore` was a one-line stub that resolved the `RestorationPlan` from the API and immediately dropped it — user clicked Resume, launcher silently closed, nothing reopened · new [`ResumePreview`](../../app/ui/launcher_v3/resume_preview.py) overlay floats on top of the digest inside the launcher window: *Continue* eyebrow + title + *Will reopen* count breakdown (e.g. `2 files · 2 tabs · 1 search`, derived from `_classify_counts` locally — same buckets `RecoveryEngine.plan_for` uses) + Cancel / Resume now buttons, Esc cancels, no modal darkening · new [`RestoreToast`](../../app/ui/launcher_v3/restore_toast.py) pins to the bottom of the launcher for **3 s** with up to **3** restored target names (*Restored · backoff.py · client.py · MDN*) or a calm failure line (*Could not reopen 1 item · Continue anyway* / *Could not reach the engine · try again*); `_name_for` shortens paths to basename + URLs to host · `_on_preview_accept` calls `APIClient.recovery_restore`, walks `plan.steps` in the engine's prescribed order (**files → chats → tabs → searches**), opens each via `_open_target` (`os.startfile` on Windows, `open` on macOS, `xdg-open` on Linux); files are existence-checked before logging the `open` event so a phantom file doesn't pollute the log · failure handling is best-effort: missing files + `os.startfile` exceptions are counted as `skipped` and the chain continues — no hard stop, no modal, no traceback ever surfaced to the user · `RECALL_EXPLAIN_RECOVERY=1` writes per-step skip reasons to stdout (developer-only path) · demo path runs through the same preview → toast cycle (synthesises `demo_targets` from the demo recovery's `urls` + `files`) so the WebSocket example reads identically to a live restore · stub helpers (`_on_restore`, `_on_demo_resume`) deleted and documented in `archive/resume-old/README.md` · launcher hides ~400 ms after a successful toast so the user lands in the editor / browser uncovered · 3 new docs: `RESUME_FLOW.md` (end-to-end pipeline + the *why files first* / *why chats second* rationale + 5-row failure table) + `SHOWCASE_RUN.md` (scripted WebSocket demo run + failure-injection matrix) + `PHASE_6P_STATUS.md` · pyflakes clean across the new files; legacy launcher's own `_on_recovery_restore` left intact (still reachable via `RECALL_LAUNCHER=legacy`) |
| 6Q | Continuity Truth | **Make Recall feel correct - not pretty, not bigger - investigation quality only. No launcher redesign, no extension redesign, no control-room work** · 3 layers shipped together: (1) **the canonical contract** — new `INVESTIGATION_PRINCIPLES.md` codifies the 7 rules (*same topic returns → merge · one-off visit → suppress · passive browsing → suppress · deep work → promote · unfinished work → strongest signal · multi-day return → boost · casual reopen loops → decay*) + 9-row trust-floor gate table; new `PROMOTION_THRESHOLDS.md` documents **LOW (0-1) / MED (2-3) / HIGH (4+)** bands + 5 overrides (*unfinished overrides all · returned_after_gap boosts +1 · duplicate penalty · noise penalty · ledger penalty*) (2) **the feedback loop** — new [`bad_recoveries.py`](../../app/core/bad_recoveries.py) appends to `~/.recall/bad_recoveries.jsonl` (closed 4-reason enum: `wrong_topic` · `already_done` · `noise` · `duplicate`; trust contract: no content, only `thread_id`+`reason`+`ts`, local-only, inspectable JSONL), engine writes `signals.ledger_flagged = 1.0` on flagged threads (`_LEDGER_WINDOW_DAYS = 14`), launcher's `_populate_digest` reads the flag and skips HIGH promotion — the only user-feedback input into ranking; everything else stays derived (3) **the introspection surface** — new [`recall inspect <id>`](../../app/core/inspect_cli.py) CLI prints deterministic ASCII card (Title · Strength · Signals · Evidence · Decision); new [`recall trust review`](../../app/core/trust_cli.py) prints 14-day ledger + bad %/silence %/resume % rates; new [`WhyThisSheet`](../../app/ui/launcher_v3/why_sheet.py) overlay opens from a small lavender *Why this?* link on hero meta row (`_WhyLink` widget), lists [`recovery.explain_signals(candidate)`](../../app/core/recovery.py) verbatim — **no AI text, no prose, no scoring numbers**, just observational lines (*"unfinished work · returned after a 2-day gap · 5 targets involved · multiple surfaces engaged"*) · launcher escape cascade: *why sheet > preview > hide* · 4 captures in `assets/screenshots/launcher-truth/` (`hero_with_why` · `why_sheet` · `showcase` · `ledger_demoted`) · new `SHOWCASE_TRUTH.md` is the *Showcase Reality* scripted walk (proposal · RLHF · WebSocket) verifying *only one hero ever surfaces* + the *Why this?* contract + the ledger-demotion path + a 6-row failure-mode table · [`archive/recovery-ranking/`](../../archive/recovery-ranking) documents what 6Q **kept untouched** (every gate + every weight), what 6Q **added** (ledger flag + `explain_signals` + 2 CLIs + Why sheet), and what 6Q **considered and rejected** (learned ranker — CLAUDE.md determinism rule; second freshness half-life — double counts; chat-heavy bump — duplicates surface-breadth weight; engine-side de-dup pass — deferred) · pyflakes clean across new files · ASCII-only output across both CLIs (`cp1252` safe) · success bar: *"Yes. That is exactly what I wanted back."* |
| 6P.1 | Launcher Visibility Recovery | **No new features, no recovery logic work, no resume work — visual correction only** · the 6O reset went too far on paint: `#F7F5F2` page vs `#FFFFFF` cards differed by ~10 % luminance so layered surfaces blended together, search had no chrome of its own, OTHER WORK was bare text adrift, empty-state buttons had no fixed widths, and the launcher window painted flush to its edge with no visible frame · `theme.BG` warms to **`#F3F1ED`** (6 % darker than the cards) · new `BORDER_RAISED = #E4DED6` solid hairline replaces rgba hairlines that read as muddy ink · new `SHADOW_CARD_* = 0 12 32 rgba(0,0,0,.08)` (vs 6O's `0 8 24 .07`) · new `_LayeredCard` base class (white fill + 1-px warm-grey border + soft drop shadow) inherited by the search bar (radius 14), the recovery hero (radius 22), and the new `_InvestigationsCard` wrapper (radius 18) around the OTHER WORK row · search bar gains hand-drawn `_SearchIcon` (`QPainter` circle + handle, no Unicode glyph dependency) + lavender focus ring (2-px `T.ACCENT` border on `FocusIn`, drops back to the warm hairline on `FocusOut`); inactive cards paint at ~0.96 alpha so the focused card is always the foreground · hero gains **soft 4-px lavender left accent strip** painted inside the rounded border (clipped to follow the card curve) + **fixed-width 110-px Resume button** (`_ResumeButton.WIDTH`) so the right edge of the card is stable across recoveries with different title lengths · empty state stacks **logo dot → headline → sub → buttons** with a 16-px gap and two **140-px fixed-width buttons** (primary accent-filled, secondary layered card) · `MinimalWindow` reserves a **12-px outer margin** and paints a 1-px warm-grey border around the page at radius 24 so the launcher reads as a discrete object · new [`capture_launcher_visible.py`](../../infra/scripts/capture/capture_launcher_visible.py) produces 4 PNGs (`hero` · `empty` · `focus` · `investigations`) in `assets/screenshots/launcher-visible/` · new [`LAUNCHER_VISIBILITY.md`](../product/LAUNCHER_VISIBILITY.md) carries the directive's *problem · fix · before / after* audit (9-row comparison table) · structural geometry unchanged (680 × 460, HIGH-only gate, max-3 investigations) · pyflakes clean |
| 6R | Launcher Finalization | **Stop feature work - only launcher - make it feel like shipped software. No docs, no trust system, no recovery ranking, no control room, no extension. The launcher becomes a frozen product surface; no more launcher phases after this** · window **680 × 440** hard clamp (`setFixedSize` min=max, no resize), `WA_TranslucentBackground=False` — *no glass, no blur, no floating opacity tricks* · `BG=#F4F1EC` (was `#F3F1ED`), new `BORDER_RAISED_STRONG=#E7DED3` (2-px search border), new `SHADOW_SEARCH_*=0 8 24 rgba(0,0,0,.06)` under `SHADOW_CARD_*=0 12 32 rgba(0,0,0,.08)` · **search bar rewritten**: 52 px tall, radius 14, lavender focus ring, hand-drawn `_SearchIcon` (no Unicode glyph dependency), placeholder *Search work…* · **hero card rewritten**: fixed 88-px height, **6-px lavender left accent strip** clipped to rounded border, title (one line, elided with `...`) + tiny **HIGH** confidence pill + **fixed-width 112-px Resume button** + max-3 chip row beneath title derived from `suggested_targets` via `_chips_from_targets` (same buckets as resume preview); **removed from hero**: subtitle · meta caption · prose · *Why this?* link · `signals` param · `request_why` signal · **OTHER WORK rewritten**: vertical list (was horizontal in 6O), 44-px rows (lavender 6-px dot + title + quiet painted chevron), max 3 rows, white card wrapper with 1-px inter-row dividers · **empty surface restacked**: lavender square · headline · *Show example* (primary accent-filled) · *Start working* (secondary layered card — renamed from *Start normally* per directive), both buttons 200-px fixed width, **inside the centred stack** (no longer floating page furniture) · new single-line **footer** *local only · no cloud* at the bottom of every surface (populated + empty), ~10 px ink-3, centred · live launcher's `WhyThisSheet` wiring removed: `_recovery_to_v3` no longer passes `signals`, demo path no longer synthesises demo signals, escape cascade collapses back to *preview > hide* · new `capture_launcher_final.py` produces 4 PNGs (`hero` · `empty` · `focus` · `overflow`) in `assets/screenshots/launcher-final/` · new `LAUNCHER_FINAL_AUDIT.md` is the frozen-product checklist (geometry table · paint table · hero / OTHER WORK / empty / footer contracts · 7-check visibility audit covering *arm-length / dark-room / 50% / 125% scaling / title overflow / empty / demo / resume* + the freeze rule) · 4 files snapshotted into [`archive/launcher-debt/`](../../archive/launcher-debt) with per-file README: `minimal_6p1.py` · `recovery_panel_6q.py` · `investigation_panel_6o.py` · `why_sheet_6q.py` · engine-side signals layer (`recovery.explain_signals` + `recall inspect` + `bad_recoveries`) **stays in active code** — only the launcher's surface changed · pyflakes clean · success bar: *open Recall · understand instantly · click Resume · done* |
| 7A | Extension Product Surface | **Stop launcher, control room, founder tooling, docs, alpha dashboards. Only extension. Make Recall extension feel premium** · Popup frozen at **440 × 640** (body width+height pinned, overflow hidden) · 6 fixed regions in a single column: **Header** (lavender mark + breathing daemon dot + subtitle *Connected locally* + Search/Settings icons; removed event-count + desktop badges + wrench) · **Continue hero** (full-width white card, **6-px lavender accent rail**, tiny HIGH pill, title 1 line elided, max 3 derived chips, **fixed-width 112-px Resume** with `1` shortcut chip, capped at 110-px) · **Active investigations** (vertical stack of 48-px rows inside one white card; strength dot + title + last-seen + chevron; max 4 visible without scroll) · **Today timeline** (3-column grid mono-time/bold-source/label, empty rail surfaces 36-px painted illustration in place of the old *"No browser memory captured yet"* prose) · **Activity** (two side-by-side cards — Browser w/ `capturing/idle/offline` pill listing *tabs · navigation · returns · searches*; Desktop w/ `capturing/soon/offline` pill listing *files · editors · integrations* — the Desktop `SOON` pill surfaces the directive's *Design UI now. Engine later.* seam honestly) · **Trust strip** (4 tiny pinned pills `LOCAL ONLY · NO CLOUD · 0 UPLOADS · DAEMON OK` replaces the ~140-px `TrustSurface` section) · **SearchOverlay** on Ctrl/Cmd+K slides down with input + groupings for *Investigations · Files · Returns · Events* (in-memory filter for now; `useResults` swappable when a unified endpoint lands) · new design tokens: **page `#F5F2ED`** warm paper · card `#FFFFFF` · hairline `#E6DED4` · accent `#8B7FE3` · shadow `0 12 32 rgba(0,0,0,.06)` (card) + `0 20 56 rgba(0,0,0,.12)` (search overlay) — *no glass, no neon, no blur* · motion scale tightened to directive's exact **120 / 180 / 240** via `--motion-fast/normal/slow` tokens · 8 new components under `apps/extension/ui/src/components/v2/` (`Header`, `Hero`, `Investigations`, `Timeline`, `Activity`, `TrustStrip`, `SearchOverlay`, `States`) · `App.tsx` rewritten to compose them; state machine + API client + demo overlay flow preserved untouched · `capture_extension.mjs` gains `OUT_7A` + 7 fixtures (`empty · capturing · active · resume · offline · search · demo`); `search` fires Ctrl+K via Playwright keyboard · new `EXTENSION_PRODUCT_AUDIT.md` is the frozen-product checklist (paint table · motion table · per-region contracts · 7-row state catalogue + capture-architecture table) · `tsc --noEmit` + `vite build` clean (~293 KB JS) · 21 captures total (7 new in `extension-7a/`) · success bar: *open extension → immediately understand: Recall remembered work · Recall can continue it · Recall is running* |
| 7B | Launcher Production Freeze | **Turn launcher into shipping product. No new features, no control room, no extension, no alpha, no docs except audit** · 6R froze the layout cleanly but kept the per-section-card pattern (search/hero/OTHER WORK each painted their own bordered shadowed white card on the warm page) → read as *three floating overlays* not *one product object* · 7B collapses into **a single white root card** on the warm page · `MinimalWindow.paintEvent` now: (1) fills full window with `BG=#F4F1EC`, (2) draws manual two-offset-rounded-fill shadow (3-px offset, 18 α — replaces `QGraphicsDropShadowEffect` so hot path skips software rasterise), (3) draws white root card body at radius **22** inside the 14-px outer margin with 1-px `BORDER_RAISED` outline · `MinimalShell` provides 20-px internal padding (top/sides) + 18 (bottom) · **search bar rewritten**: 52-px row with **warm-paper fill** (`#F4F1EC`) inside the root + 2-px `BORDER_RAISED_STRONG` border + lavender focus ring + hand-drawn `_SearchIcon` + inline `Ctrl K` hint chip (auto-hidden on focus) · **hero rewritten — no card chrome**: fixed 88-px height, **only the 6-px lavender left accent rail** (rounded ends; brighter rail + 1-px lavender outline when keyboard-focused); title row (title elided + `HIGH` confidence pill + **fixed-width 112-px Resume button**) + chips row beneath (max 3, derived from `suggested_targets`) · **OTHER WORK list — no wrapping card**: rows paint directly on the root with 1-px `BORDER_RAISED` hairline dividers between, max 3 visible · footer (*local only · no cloud*) pinned at bottom of root card · new **`Ctrl+K` + `Meta+K`** QShortcuts in `LiveLauncher.__init__` focus + select-all the search input from anywhere inside the launcher · new **`RECALL_DEBUG=1` timing log** writes one line per `show_centered` to stderr (`[recall.launcher.timing] show_centered  N ms  (budget 400)`) so the *<400 ms launcher open* budget is verifiable on a real machine · search emits on every keystroke (no client-side debounce) so *<100 ms search* budget lands by construction · new `capture_launcher_ship.py` produces 5 PNGs (`hero · empty · focus · demo · overflow`) in `assets/screenshots/launcher-ship/` · new `LAUNCHER_SHIP_AUDIT.md` **supersedes** `LAUNCHER_FINAL_AUDIT.md` (6R) as the live contract — carries 6R → 7B delta table + frozen paint/geometry/motion/per-region tables + 9-row visibility-pass table (100% / 125% / 150% scaling, arm-length, dark/bright room, title overflow, empty, demo) + 2-row performance-budget table + the explicit *Launcher frozen forever* freeze rule · 3 files snapshotted into [`archive/launcher-final/`](../../archive/launcher-final) with per-file README: `minimal_6r.py` · `recovery_panel_6r.py` · `investigation_panel_6r.py` · engine + recovery layer + resume pipeline (6P) + trust/inspector CLIs (6Q) all **untouched** — 7B is paint + ergonomics only · pyflakes clean · success bar: *open Recall · see remembered work · press Resume · leave* |
| 7B.1 | Launcher Visual Merge | **Rebuild launcher toward Stitch reference. Current launcher discarded visually. Keep logic, replace surface** · 7B locked the launcher into one root card with three regions inside (search/hero/OTHER WORK) but the Raycast-shaped density still read as *utility* · 7B.1 follows the Stitch document-workspace shape · **canvas 740 × 500** hard clamp (`setFixedSize`), single white workspace inside 16-px gutter, radius 22, warm `#F4F1EC` page outside · **search bar rewritten**: 52-px row, warm-paper fill (`#FAF7F1`), hand-drawn glyph, right cluster of **settings cog + close × + `Ctrl K` hint chip** (cog forwards to `request_settings`; × hides launcher), placeholder *Start typing to recover…* · **Continue document** replaces the dense hero row: 220-px calm card w/ soft warm-paper tint (`#FBF8F2`), 6-px lavender accent rail clipped to rounded corners, `CONTINUE` eyebrow inside the card, 14.5-pt bold title (elided), bulleted body (file/tab/chat/search counts + *returned after Nd* clause pulled from `preview_caption` via new `_extract_gap_clause` helper in `live.py`), right-aligned fixed-width 116-px Resume button w/ `1` shortcut chip — reads as *document with an action*, not command-palette row · **empty workspace rebuilt**: new `_InfinityGlyph` paints lavender lemniscate (two overlapping ellipses + `ACCENT_SOFT` halo) via QPainter (no Unicode glyph dependency); 20-pt bold headline *Everything you've seen, searchable.* (≈26 logical at Windows DPI); 14-px sub *Your digital continuity layer.*; two stacked 200-px buttons *Show example* (accent-filled) + *Start working* (outline) · **bottom strip** replaces the centred footer: 22-px row w/ trust line *End-to-end encrypted. Local storage only.* on left + tiny `Privacy · Demo · Docs · Browser` text links on right (links inert in 7B.1, placeholders for future deep links — *Design UI now, engine later* pattern) · **OTHER WORK list removed from visible surface** — single-focus tool; `InvestigationCardV3` + `InvestigationList` reduced to zero-cost stubs (`HEIGHT = 0`, hidden, `populate()` discards) so engine path stays live · hotkeys: kept `Esc` / `Ctrl+K` / `Meta+K` / `1`; removed `2-9` (nothing to navigate to) · 3 files snapshotted into [`archive/launcher-raycast/`](../../archive/launcher-raycast) w/ per-file README: `minimal_7b.py` · `recovery_panel_7b.py` · `investigation_panel_7b.py` · 5 captures (`empty · active · resume · demo · overflow`) in `assets/screenshots/launcher-merge/` · new `LAUNCHER_VISUAL_MERGE.md` **supersedes** `LAUNCHER_SHIP_AUDIT.md` (7B) as the live contract — 7B → 7B.1 delta table + frozen paint/geometry/typography/per-region tables + 5-row state catalogue · engine + recovery + resume + trust/inspector layers all **untouched** — 7B.1 is paint + composition only · pyflakes clean · success bar: *Looks like product. Not utility.* |
| 7D | Capture Truth Audit | **Verify Recall actually remembers. No UI, no redesign — engine + CLI + docs only** · new [`recall capture status`](../../app/core/capture_cli.py) prints read-only ASCII summary (events today + per-kind tally for the 7 known kinds + returns ≥ 30-min gap + investigation count + last-event ts/kind/age); daemon **not required**, reads `~/.recall/events/YYYY-MM-DD.jsonl` + `~/.recall/threads.json` directly; degrades gracefully on missing threads cache (returns `0`); prints 3 remediation hints when `events today == 0` (run daemon · check extension · run demo) · new [`recall capture tail`](../../app/core/capture_cli.py) is a `tail -f`-style live inspector: prints every existing event in today's file first then polls daily JSONL at 500-ms intervals, surfaces each new line as compact `HH:MM:SS  kind  detail  title` row; survives midnight day-rollover (re-derives `_today_filename()` per tick); survives truncate/rotate (falls back to `pos = 0`); `--once` mode prints existing events then exits (script-friendly) · both dispatch from `recall.py` fast path before `app.main` import — no Qt boot cost · new [`CAPTURE_FLOW.md`](../product/CAPTURE_FLOW.md) documents the **seven hops** end-to-end (browser observers → loopback POST → daemon ingest routes → EventLogger.log → ThreadBuilder → RecoveryEngine.recover_recent → LiveLauncher), names file + function per hop, lists confirmation CLI per hop, closes with scripted 7-step verification walk (ChatGPT / GitHub / StackOverflow / Google → leave ≥ 30 min → return → confirm Continue document + `recall inspect` confirms `Strength: HIGH`) · live measurement: 71 events today / 64 tabs + 7 chats / 11 investigations / last event 1h ago — ChatGPT / Google / Stitch all present in tail output · pyflakes clean · success bar: *Recall truly remembers — and now you can prove it* |
| 7E | Launcher Final Product Pass | **Freeze engine, recovery, extension, control room — launcher only. Make memory visible, hierarchy clear, single surface at 700×500** · 7B.1 shipped beautiful Stitch-aligned single-document workspace but solved *floating overlays* by **removing memory from surface** → looked calm but felt prototype-y · 7E restores memory while honouring calm-product feel · canvas **700 × 500** hard clamp (was 740×500), warm `#F5F2ED` page outside, one white inner card radius **24** + padding 20/16/20/14, **no nested cards / no glass / no transparency** · 5 sections stack inside w/ **no per-section chrome**: (1) **52-px search bar** (warm-paper fill, lavender focus ring, inline Ctrl K hint, placeholder *Search investigations…*); (2) **13-px / 9-pt muted-lavender tagline** *Recall noticed unfinished work* directly under search; (3) **Continue hero** w/ **HIGH/MED/LOW signal variants** driving 6-px left accent rail (filled/soft/outline) + matching confidence pill — 110-px row, title + Resume on top, evidence + pill on bottom; (4) **NEW RECENT MEMORY section** — new [`recent_memory.py`](../../app/ui/launcher_v3/recent_memory.py) ships `MemoryRow` + `RecentMemoryList` (max 5 rows, 18 px each); `LiveLauncher._load_recent_memory` pulls from `EventStore.iter_events(days=2)` and maps `Event.payload → MemoryRow(time, source, label)` via `_short_source` (ChatGPT/Claude/Gemini/Google/DuckDuckGo/Bing/domain title-case) + `_short_label` — **fixes the *memory invisible* problem**; (5) **OTHER WORK rebuilt** from 7B.1's zero-cost stub into 36-px rows w/ strength dot (lavender if surfaces≥3 else ink-4) + title elided + last-seen mono caption right-aligned via `events.humanize_age`, max 3 rows, 1-px hairline dividers; (6) **TrustRow** pinned at bottom — 22-px row w/ 4 tiny pills `LOCAL · NO CLOUD · N EVENTS TODAY · M INVESTIGATIONS`, counts derived live by `_load_trust_counts` from same disk reads Phase 7D `recall capture status` uses · **removed from surface**: Show example/Start working giant buttons · centered empty states · large vertical spacing · floating pills · dark overlays · prototype illustrations · empty-state swap (launcher now always shows *something memory-shaped*) · hotkeys preserved: `Esc` / `Ctrl+K` / `Meta+K` / `1` · demo path updated to synthesise `MemoryRow` list from demo payload's timeline · 3 files snapshotted into [`archive/launcher-7b1/`](../../archive/launcher-7b1) w/ per-file README: `minimal_7b1.py` · `recovery_panel_7b1.py` · `investigation_panel_7b1.py` · 5 captures (`home · high · med · low · no_hero`) in `assets/screenshots/launcher-7e/` · new [`LAUNCHER_FINAL.md`](../product/LAUNCHER_FINAL.md) **supersedes** `LAUNCHER_VISUAL_MERGE.md` (7B.1) as live contract — 7B.1→7E delta table + frozen paint/geometry/typography/per-region tables + 5-row state catalogue + removed-list · engine + recovery + resume (6P) + trust/inspector CLIs (6Q) + capture CLIs (7D) all **untouched** — 7E is paint + composition only · pyflakes clean · success bar: *open Recall → see unfinished work + recent memory + resume path + trust within 3 seconds* · **launcher frozen** |
| 7E.1 | Launcher Stability | **Launcher boots every time. No visual work, no redesign — audit + freeze public interface** · 7E paint rewrite of `MinimalSearchBar` silently dropped `request_settings` + `request_close` signals while `LiveLauncher.__init__` still wired both → every `python recall.py` crashed `AttributeError: 'MinimalSearchBar' object has no attribute 'request_settings'` at construction · fix: restore both dropped signals on `MinimalSearchBar` + add documented contract (`searchChanged(str)` alias of `query_changed(str)` wired via two parallel `QLineEdit.textChanged` connects; `submit(str)` already present; `clear()` + `selectAll()` methods added) · two *may-not-exist* signals declared even though no widget in 7E fires them — consumers `connect(...)` safely; later paints can wire an on-screen affordance without touching host wiring · `MinimalSearchBar` docstring gains "Public contract (Phase 7E.1 — frozen)" block listing 5 signals + 3 methods · new [`LAUNCHER_CONTRACTS.md`](../product/LAUNCHER_CONTRACTS.md) documents frozen interface (per-class signals + methods + stable attributes; `LiveLauncher` constructor signature; keyboard-shortcut table; `app/main.py → LiveLauncher → MinimalSearchBar` wiring map; freeze rule *future launcher phases may **add** to the surface; they **must not remove or rename** the symbols below* + slow-path procedure for the rare case a major break needs to happen) · verification: offscreen `LiveLauncher(FakeEngine())` constructs cleanly (`CONSTRUCT OK · DEFAULT_SIZE: (700, 500)`); all 5 signals present; all 3 methods callable; both `query_changed` + `searchChanged` fire on text (`{'query_changed':1,'searchChanged':1}`); `request_settings.emit()` propagates to `LiveLauncher.request_settings` (hits=1); `python recall.py doctor` green on config / events / extension / installer · no widget paint changed, no layout changed, no new features · success bar: *launcher boots every time* |
| 8A | Full Product Audit | **STOP BUILDING FEATURES. Understand what Recall actually is today. No launcher/extension/control-room redesign, no new memory systems, no new phases — audit only** · 7 evidence-based audit docs land under new top-level `AUDIT/` folder: `SURFACES.md` catalogues every runtime surface (36 LIVE / 2 LEGACY / 11 ARCHIVE / 1 REMOVE) w/ entry point + owner file + status · `DEAD_CODE.md` lists parallel trees + duplicate widgets + orphan API routes + dead helpers w/ file:line citations + grep evidence (8 truly DEAD pre-7A extension components, 7 LEGACY `app/ui/*.py` behind `RECALL_LAUNCHER=legacy`, 3 duplicate widget pairs + 1 duplicate confidence-logic pair, 5 orphan API routes: `thread_forget`, `contexts/recent`, `sessions/recent`, `threads_clear_evolution_cache`, `replay_day`) · `LAUNCHER_MAP.md` traces every signal/slot/public method through launcher (class graph + state-flow per refresh + frozen anti-rules mirroring 7E.1 contract + the *one launcher* collapse path) · `CAPTURE_MAP.md` cross-checks 7D `CAPTURE_FLOW.md` against current code, lists diagnostic CLI per failure mode, captures live measurement (8 events today, 11 investigations, last event 38m ago) · `ASSETS.md` inventories every PNG under `assets/screenshots/` (5 ACTIVE folders + `⭐` `launcher-7e/` + `⭐` `extension-7a/` + 11 HISTORICAL phase folders + 7 root-level ORPHAN PNGs flagged for tier-1 delete) · `DEPENDENCIES.md` classifies all 43 packages across `requirements.txt` + 3 `package.json` files (20 runtime / 19 dev / 3 unused `clsx`+`lucide-react`+`tailwind-merge` in marketing web / 1 misplaced `playwright` in extension's `dependencies`) · `STATE.md` is capstone (*what Recall is · what ships · what's dead · what survives · tier-graded delete recommendations · live verify*) · 3 parallel `Explore` subagents gathered evidence for dead-code/asset/dependency audits · launcher/capture/state docs authored against raw findings · `DOC_INDEX.md` updated w/ new `/AUDIT/` section at top so audit docs reachable from standard index · live verify: `recall doctor` GREEN on config/events/event-flow/daemon/extension/installer (5 YELLOWs all *user hasn't done yet* — autostart, recall://, version drift); `recall capture status` clean (8 events today, 11 investigations); `recall founder status` shows [GREEN] Continuity restored 78%, Resume sessions 41, Investigations 134, Extension connected 75%; TypeScript clean across all 3 frontend apps; offscreen `LiveLauncher(FakeEngine())` boots cleanly at `(700, 500)` · **no deletions, no code changes** — audit phase, not feature phase · success bar: *understand entire repo. No more accidental building. No more launcher rewrites. No more code slop.* |
| 8B | Tier 1 Cleanup + Repo Collapse | **Execute 8A audit recommendations. No feature work, no UI changes, no new docs except 5 cleanup audit docs** · Python LOC **−24%** (29,544→22,435 = **−7,109 lines moved to archive**), asset PNGs **−54%** (102→47), asset folders **−58%** (19→8), extension components **−73%** (11→3), `app/ui` live files **−55%** (11→5) · **no code deleted** outside dep entries + 7 stale root PNGs · (1) **launcher collapse** — 8 legacy modules (`launcher_legacy.py` 2675 LOC + `cards.py` 970 + `widgets.py` 2471 + `styles.py` 359 + `launcher_anims.py` 84 + `launcher_digest.py` 89 + `demo_data.py` + `ceremonies.py`) + 3 historical capture scripts → `archive/launcher-old/`; `app/ui/launcher.py` collapsed 60→18 lines (no more `RECALL_LAUNCHER=legacy` branch + no back-compat constant re-exports); import contract `from app.ui.launcher import Launcher` still resolves to `LiveLauncher` · (2) **asset cleanup** — 11 historical capture folders (`launcher-live` 6K · `launcher-minimal` 6L · `launcher-refined` 6M.1 · `launcher-compact` 6M.2 · `launcher-recovery` 6N · `launcher-reset` 6O · `launcher-visible` 6P.1 · `launcher-truth` 6Q · `launcher-ship` 6R · `launcher-final` 7B · `launcher-merge` 7B.1) → `archive/screenshots-history/`; 7 stale orphan PNGs deleted outright (`control-room` · `doctor-output` · `installer-flow` · `settings-dialog` · `launcher-first-week` · `launcher-loading` · `launcher-offline`) · (3) **extension pre-7A components** — 8 dead files (`ContinueCard`, `DebugStrip`, `DemoBanner`, `InvestigationCard`, `MemoryList`, `Section`, `TrustSurface`, `states`) → `archive/extension-pre-7a/`; vite build proves they were already tree-shaken (293 KB JS bundle unchanged) · (4) **dependency cleanup** — 3 unused deps removed from `apps/web/package.json` (`clsx`, `lucide-react`, `tailwind-merge`); `playwright` moved `dependencies`→`devDependencies` in extension · **deferred to 8C**: 5 orphan API routes (`thread_forget`, `contexts/recent`, `sessions/recent`, `threads_clear_evolution_cache`, `replay_day`) — kept until pydantic schemas walked cleanly · 5 new audit docs land in `AUDIT/`: `DELETE_PLAN.md` (per-row delete log w/ verification), `LAUNCHER_FREEZE.md` (official launcher path + public API + allowed/forbidden changes — *no more launcher generations*), `DEPENDENCY_DIFF.md` (before/after manifests + build impact), `ASSET_FREEZE.md` (frozen active asset surface), `PHASE_8B_STATUS.md` (capstone w/ before/after metrics table) · `DOC_INDEX.md` updated · verify: `pyflakes app/ui app/core api` clean · `recall doctor` GREEN · `recall capture status` clean (11 events today, 12 investigations) · offscreen `Launcher(FakeEngine())` constructs at `(700, 500)` · TypeScript clean across all 3 frontend apps · `vite build` of extension 293 KB JS unchanged from 8A · success bar: **repo smaller. Same product. No regressions.** |

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
