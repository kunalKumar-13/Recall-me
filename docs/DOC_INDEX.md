# DOC_INDEX.md — every doc, with its job

The single index of Recall's documentation system after the Phase
5D.1 consolidation. Every row: where it lives, what it answers, who
owns it, the phase it landed, the status today.

Pairs with [`engineering/DOC_HEALTH.md`](engineering/DOC_HEALTH.md)
(the live metrics).

---

## `/AUDIT/` — Phase 8A repo-wide audit (newest)

| Doc | Purpose | Phase | Status |
|---|---|---|---|
| [`AUDIT/SURFACES.md`](../archive/AUDIT/SURFACES.md) | every runtime surface w/ entry point + owner + status (LIVE / LEGACY / ARCHIVE / REMOVE) | 8A | live |
| [`AUDIT/DEAD_CODE.md`](../archive/AUDIT/DEAD_CODE.md) | dead/duplicate/orphan code catalogue — evidence-based, no deletions | 8A | live |
| [`AUDIT/LAUNCHER_MAP.md`](../archive/AUDIT/LAUNCHER_MAP.md) | every signal, slot, public method + frozen anti-rules; freeze map | 8A | live |
| [`AUDIT/CAPTURE_MAP.md`](../archive/AUDIT/CAPTURE_MAP.md) | seven-hop capture pipeline with file + function per hop + diagnostic CLI table | 8A | live |
| [`AUDIT/ASSETS.md`](../archive/AUDIT/ASSETS.md) | screenshot / image inventory w/ unused + orphan flags | 8A | live |
| [`AUDIT/DEPENDENCIES.md`](../archive/AUDIT/DEPENDENCIES.md) | Python + 3 JS package.json files w/ runtime / dev / unused classification | 8A | live |
| [`AUDIT/STATE.md`](../archive/AUDIT/STATE.md) | the state-of-the-repo summary — what Recall is, what ships, what dies next | 8A | live |
| [`AUDIT/DELETE_PLAN.md`](../archive/AUDIT/DELETE_PLAN.md) | tier-1 cleanup execution log — what moved, what deleted, with verification per row | 8B | live |
| [`AUDIT/LAUNCHER_FREEZE.md`](../archive/AUDIT/LAUNCHER_FREEZE.md) | the official launcher path + public API + allowed/forbidden changes | 8B | live |
| [`AUDIT/DEPENDENCY_DIFF.md`](../archive/AUDIT/DEPENDENCY_DIFF.md) | before/after manifests + build impact for the dep cleanup | 8B | live |
| [`AUDIT/ASSET_FREEZE.md`](../archive/AUDIT/ASSET_FREEZE.md) | the frozen active asset surface + what moved to history + freeze rule | 8B | live |
| [`engineering/PHASE_8B_STATUS.md`](../archive/phase-status/PHASE_8B_STATUS.md) | tier-1 cleanup close-out — before/after metrics, all 8 verifications green, deferred items for 8C | 8B | live |

## `/STABILITY/` — Phase 8C reality pass (newest)

| Doc | Purpose | Phase | Status |
|---|---|---|---|
| [`STABILITY/PERF.md`](engineering/stability/PERF.md) | real wall-clock timings for launcher + CLI + daemon endpoints; reproducible recipe | 8C | live |
| [`STABILITY/CAPTURE.md`](engineering/stability/CAPTURE.md) | 30d event-store coverage by site; ChatGPT/GitHub/Google verified, StackOverflow+Stitch flagged | 8C | live |
| [`STABILITY/LAUNCHER.md`](engineering/stability/LAUNCHER.md) | frozen 7E.1 widget tree walked offscreen + cold-construct timing + state coverage | 8C | live |
| [`STABILITY/RESUME.md`](engineering/stability/RESUME.md) | recovery pipeline reality + bad-recovery ledger state + restore plan invariant | 8C | live |
| [`STABILITY/EXTENSION.md`](engineering/stability/EXTENSION.md) | 9-state machine + 7 captures + bundle health + keyboard shortcuts | 8C | live |
| [`STABILITY/CONTROL.md`](engineering/stability/CONTROL.md) | 13 admin routes + 10 loaders + paths centralisation + tsc clean | 8C | live |
| [`/BUGS_OPEN.md`](engineering/BUGS_OPEN.md) | honest open-bug ledger (1 P0 fixed + 1 P0 open + 5 P1 + 4 P2) | 8C | live |
| [`/RELEASE_READINESS.md`](release/RELEASE_READINESS.md) | composite 0–100 readiness score (currently 87) + path to stable | 8C → 8D | live |

## `/release/` + RC1 top-level — Phase 8D release candidate (newest)

| Doc | Purpose | Phase | Status |
|---|---|---|---|
| [`/VERSION.md`](release/VERSION.md) | v0.1.0-rc1 spec — 8 frozen surfaces + build artifacts + ship/known/blocked bugs | 8D | live |
| [`/SCREEN_INDEX.md`](product/SCREEN_INDEX.md) | frozen capture surface — 4 canonical directories + coverage map for required RC1 screens | 8D | live |
| [`/DEMO_MODE.md`](product/DEMO_MODE.md) | `recall demo run / reset / status` CLI reference + boundary guarantees | 8D | live |
| [`/INSTALL_VERIFIED.md`](release/INSTALL_VERIFIED.md) | honest install walk on the dev box — doctor / capture / daemon / demo all green | 8D | live |
| [`release/README.md`](release/rc1/README.md) | single front door for anyone holding an RC1 build | 8D | live |
| [`release/CHANGELOG_RC1.md`](release/rc1/CHANGELOG_RC1.md) | release notes for v0.1.0-rc1 | 8D | live |
| [`release/INSTALL.md`](release/rc1/INSTALL.md) | Windows + macOS + from-source install paths | 8D | live |
| [`release/QUICKSTART.md`](release/rc1/QUICKSTART.md) | 5-minute install → resume walkthrough | 8D | live |
| [`release/DEMO_FLOW.md`](release/rc1/DEMO_FLOW.md) | 3-minute screen-share demo script + anti-patterns | 8D | live |
| [`release/KNOWN_ISSUES.md`](release/rc1/KNOWN_ISSUES.md) | user-facing bug summary (P0 = 0) | 8D | live |
| [`release/LANDING_CHECK.md`](release/rc1/LANDING_CHECK.md) | marketing-site link + asset audit (zero dead links) | 8D | live |
| [`engineering/PHASE_8D_STATUS.md`](../archive/phase-status/PHASE_8D_STATUS.md) | RC1 capstone — before/after metrics + 12-line verification table | 8D | live |

## `/alpha/` evidence loop + RC validation — Phase 8E alpha users (newest)

| Doc | Purpose | Phase | Status |
|---|---|---|---|
| [`/RC_VALIDATION.md`](release/RC_VALIDATION.md) | cross-link evidence index — all 6 RC1 claims backed by checked-in artifacts | 8E | live |
| [`alpha/users_live.json`](../alpha/users_live.json) | 9-field PII-free cohort ledger; founder = alpha-001 baseline + 4 open seats | 8E | live |
| [`alpha/pack/WELCOME.md`](../alpha/pack/WELCOME.md) | cohort front door — what we ask, what we promise | 8E | live |
| [`alpha/pack/INSTALL.md`](../alpha/pack/INSTALL.md) | 10-minute install path for testers | 8E | live |
| [`alpha/pack/DAY0.md`](../alpha/pack/DAY0.md) | first hour — browse normally | 8E | live |
| [`alpha/pack/DAY1.md`](../alpha/pack/DAY1.md) | the real test — first unprompted launcher open | 8E | live |
| [`alpha/pack/DAY3.md`](../alpha/pack/DAY3.md) | does it stick? self-survey + wow/failure checklists | 8E | live |
| [`alpha/pack/FEEDBACK.md`](../alpha/pack/FEEDBACK.md) | open intake — three channels, no form | 8E | live |
| [`alpha/pack/UNINSTALL.md`](../alpha/pack/UNINSTALL.md) | clean exit + the one sentence we want | 8E | live |
| [`alpha/failures/README.md`](../alpha/failures/README.md) | failure-incident folder — one file per report, 5-field template | 8E | live |
| [`alpha/wow/README.md`](../alpha/wow/README.md) | verbatim-only quote folder — anonymisation guide | 8E | live |
| [`engineering/PHASE_8E_STATUS.md`](../archive/phase-status/PHASE_8E_STATUS.md) | 8E capstone — alpha-evidence infrastructure built; cohort recruitment is 8F | 8E | live |

## Root — what stays at the front door

| Doc | Purpose | Owner | Phase | Status |
|---|---|---|---|---|
| [`/README.md`](../README.md) | first read; what Recall is | founder | 1A → 5D.1 | live |
| [`/CLAUDE.md`](../CLAUDE.md) | engineering charter — the working contract | founder | 4A | live |
| [`/CONTRIBUTING.md`](../CONTRIBUTING.md) | what to send a PR for, what won't be accepted | maintainer | 4A | live |
| [`/SECURITY.md`](../SECURITY.md) | vulnerability reporting | maintainer | 4A | live |
| [`/CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md) | community standard | maintainer | 4A | live |
| [`/CHANGELOG.md`](../CHANGELOG.md) | thin root redirect → `docs/release/CHANGELOG.md` | maintainer | Repo Stabilization Pass | live |

## `docs/product/` — what Recall *is*, in user words

| Doc | Purpose | Phase | Status |
|---|---|---|---|
| [`CONTINUITY_LANGUAGE.md`](product/CONTINUITY_LANGUAGE.md) | the single canonical user vocabulary | 4J | live |
| [`SURFACE_MAP.md`](product/SURFACE_MAP.md) | one job per surface (launcher / extension / website / …) | 4J | live |
| [`MOTION.md`](product/MOTION.md) | the cross-surface motion contract | 4J | live |
| [`CONTINUITY_HEALTH.md`](product/CONTINUITY_HEALTH.md) | the four day-shapes (local-only) | 5B | live |
| [`KNOWN_LIMITATIONS.md`](product/KNOWN_LIMITATIONS.md) | brutally honest limits, by design vs gap | 5C | live |
| [`TRUST_MOMENTS.md`](product/TRUST_MOMENTS.md) | the seven firsts that earn a user's trust | 5C | live |

## `docs/founder/` — running the project

| Doc | Purpose | Phase | Status |
|---|---|---|---|
| [`PHASE_TRACKER.md`](founder/PHASE_TRACKER.md) | current / completed / active / blocked / next | 5E → live | live |
| [`ROADMAP_LIVE.md`](founder/ROADMAP_LIVE.md) | Now / Next / Later / **Never** | 5E | live |
| [`FOUNDER_DASHBOARD.md`](founder/FOUNDER_DASHBOARD.md) | the five founder questions + their honest answer | 5E | live |
| [`FOUNDER_METRICS.md`](founder/FOUNDER_METRICS.md) | which metric answers which question | 5E.1 / 5B | live |
| [`ALPHA_USERS.md`](founder/ALPHA_USERS.md) | the manual public-alpha board | 5E.1 | empty (waiting for cohort) |
| [`FIRST_WEEK.md`](founder/FIRST_WEEK.md) | Day 0 → 4+ user journey | 5C | live |
| [`PUBLIC_ALPHA.md`](founder/PUBLIC_ALPHA.md) | end-to-end alpha-readiness path | 4D | live |
| [`FIRST_USE_AUDIT.md`](founder/FIRST_USE_AUDIT.md) | five-persona post-install audit | 4D | historical reference |
| [`FIRST_IMPRESSION_AUDIT.md`](founder/FIRST_IMPRESSION_AUDIT.md) | five-persona web-first-impressions audit | 4B | historical reference |
| [`CONTROL_ROOM.md`](founder/CONTROL_ROOM.md) | what the operator UI is, what data it accepts, what never enters | 5E.2 | live |
| [`FOUNDER_OPERATIONS.md`](founder/FOUNDER_OPERATIONS.md) | the daily runbook — five-minute morning loop, cohort imports, weekly sweep | 5E.3 | live |
| [`READINESS_SCORE.md`](founder/READINESS_SCORE.md) | the 0-100 readiness verdict — six weighted inputs, three bands, audit trail | 5E.3 | live |

## `docs/engineering/` — how it works, technically

| Doc | Purpose | Phase | Status |
|---|---|---|---|
| [`AUDIT_REPORT.md`](engineering/AUDIT_REPORT.md) | standing engineering debt ledger | 4C → live | live |
| [`DEAD_CODE_AUDIT.md`](engineering/DEAD_CODE_AUDIT.md) | what was removed, what was flagged | 5D | live |
| [`REPO_HEALTH.md`](engineering/REPO_HEALTH.md) | LOC + size metrics, the safe-delete policy | 5D | live |
| [`COMPLEXITY.md`](engineering/COMPLEXITY.md) | largest files + recommended carve | 5D | live |
| [`DEPENDENCIES.md`](engineering/DEPENDENCIES.md) | every dep classified (runtime / build / dev) | 5D | live |
| [`STABILITY.md`](engineering/STABILITY.md) | guarantees + the failure philosophy | 4C | live |
| [`PERF.md`](engineering/PERF.md) | benchmark methodology + budgets + hot paths | 4F | live |
| [`TRUST_LEDGER.md`](engineering/TRUST_LEDGER.md) | what Recall sees / never sees / can export | 5E.1 | live |
| [`ROOT_ARCHITECTURE.md`](engineering/ROOT_ARCHITECTURE.md) | system topology + dependency graph | 4B | live |
| [`REPO_STRUCTURE.md`](engineering/REPO_STRUCTURE.md) | pseudo-monorepo rationale + split criteria | 4B | live |
| [`DOC_HEALTH.md`](engineering/DOC_HEALTH.md) | doc-system metrics | 5D.1 | live |
| [`FRICTION_FIXES.md`](engineering/FRICTION_FIXES.md) | 11 Phase-5G findings × (issue/root-cause/fix/verification) | 5H | live |
| [`INSTALL_SIZE_AUDIT.md`](engineering/INSTALL_SIZE_AUDIT.md) | the 260 MB installer mapped to file counts + wheel sizes + reduction paths | 5H | live |
| [`REPO_CLEANUP_REPORT.md`](engineering/REPO_CLEANUP_REPORT.md) | the Repo Stabilization Pass receipt (28 imports + duplicate fn + motion exports + .gitignore + 5-surface verification) | Repo Stabilization Pass | live |
| [`PHASE_5H_STATUS.md`](../archive/phase-status/PHASE_5H_STATUS.md) | Friction Kill receipt (install_repair CLI + DaemonPulse + stagger reveal + verification matrix) | 5H² | live |
| [`FRICTION_FIXED.md`](engineering/FRICTION_FIXED.md) | the cumulative fixed-frictions ledger (40 items across 5F → 5H²) | 5H² | live |
| [`OPEN_PROBLEMS.md`](engineering/OPEN_PROBLEMS.md) | the still-named open list (26 items, 16 accept-by-design + 10 with named paths) | 5H² | live |
| [`INSTALL_SIZE_AUDIT_V2.md`](engineering/INSTALL_SIZE_AUDIT_V2.md) | real-byte breakdown of the 970 MB bundle; 3 reduction tiers | 5I | live |
| [`MODEL_STRATEGY.md`](engineering/MODEL_STRATEGY.md) | path to a <150 MB embedding stack (ONNX recommended) | 5I | live |
| [`SPLIT_DISTRIBUTION.md`](engineering/SPLIT_DISTRIBUTION.md) | four packs (Core / Retrieval / Dev Tools / Demo Seed); two install paths | 5I | live |
| [`PHASE_5I_STATUS.md`](../archive/phase-status/PHASE_5I_STATUS.md) | Phase 5I receipt | 5I | live |
| [`alpha/FIRST_72_HOURS.md`](../alpha/FIRST_72_HOURS.md) | hour-by-hour trust / confusion / drop-risk / aha curve | 5I | live |
| [`INSTALL_REDUCTION_REPORT.md`](engineering/INSTALL_REDUCTION_REPORT.md) | Tier A execution receipt — excludes table + before/after measurements + smoke matrix | 5J | live |
| [`PHASE_5J_STATUS.md`](../archive/phase-status/PHASE_5J_STATUS.md) | Phase 5J Installer Shrink Execution close-out | 5J | live |
| [`PHASE_5K_STATUS.md`](../archive/phase-status/PHASE_5K_STATUS.md) | Phase 5K Alpha Reality close-out — the cohort infrastructure receipt | 5K | live |
| [`PHASE_6A_STATUS.md`](../archive/phase-status/PHASE_6A_STATUS.md) | Phase 6A First Magic close-out — UX polish toward the 30-second magic test | 6A | live |
| [`PHASE_6B_STATUS.md`](../archive/phase-status/PHASE_6B_STATUS.md) | Phase 6B Launcher Identity close-out — warm white + lavender theme swap, chip-row split, EmptyCard redesign | 6B | live |
| [`PHASE_6C_STATUS.md`](../archive/phase-status/PHASE_6C_STATUS.md) | Phase 6C Extension Premium close-out — popup gains confidence pill, today rail, investigation pill strip, launcher-parity empty state | 6C | live |
| [`PHASE_6D_STATUS.md`](../archive/phase-status/PHASE_6D_STATUS.md) | Phase 6D Demo Mode close-out — first-run overlay, 5-state machine, 3 demo API routes, auto-dismiss on real ingest, no engine touch | 6D | live |
| [`FIRST_MAGIC.md`](product/FIRST_MAGIC.md) | the demo overlay product story — what it is, what it isn't, how it disappears, trust rules | 6D | live |
| [`PHASE_6E_STATUS.md`](../archive/phase-status/PHASE_6E_STATUS.md) | Phase 6E Alpha Reality close-out — operations only: CLI `update`/`export`, recovery ledger 6-kind vocabulary, `founder alpha-health` panel | 6E | live |
| [`alpha/PLAYBOOK.md`](alpha/PLAYBOOK.md) | the alpha cohort operations book — six-moment tester lifecycle + daily morning loop + field list | 6E | live |
| [`alpha/STATUS.md`](alpha/STATUS.md) | live cohort board, hand-edited weekly | 6E | live, empty (waiting for cohort) |
| [`alpha/KNOWN_FAILURES.md`](alpha/KNOWN_FAILURES.md) | failure catalogue, quote-don't-paraphrase / never-inflate contract | 6E | live, empty (waiting for first failure) |
| [`PHASE_6F_STATUS.md`](../archive/phase-status/PHASE_6F_STATUS.md) | Phase 6F Daily Loop Validation close-out — 6 counters at `~/.recall/daily_loop.jsonl`, return detector, 3 signals with RYG, `recall founder daily-loop` + `recall alpha replay` | 6F | live |
| [`DAILY_LOOP.md`](product/DAILY_LOOP.md) | the daily-loop product story — six bins, three signals, the *not telemetry* contract | 6F | live |
| [`RETURN_BEHAVIOR.md`](product/RETURN_BEHAVIOR.md) | the return detector's exact semantics (what counts / why 30 min / state file / manual verify recipe) | 6F | live |
| [`alpha/MOMENTS.md`](alpha/MOMENTS.md) | the seven first-time moments per tester — install / capture / investigation / recovery / resume / wow / trust break | 6F | live, empty (waiting for cohort) |
| [`PHASE_6G_STATUS.md`](../archive/phase-status/PHASE_6G_STATUS.md) | Phase 6G Public Alpha Surface close-out — marketing-site narrative + download grid + trust five-rule rewrite + screenshot pipeline | 6G | live |
| [`TRUST.md`](product/TRUST.md) | the public trust statement — five rules + on-disk contract per rule + what Recall will / won't ask for | 6G | live |
| [`DOWNLOAD_GUIDE.md`](release/DOWNLOAD_GUIDE.md) | the four alpha download paths in detail (Win lite / Win full / macOS preview / extension) | 6G | live |
| [`DEMO_VIDEO_SCRIPT.md`](release/DEMO_VIDEO_SCRIPT.md) | the 60-second placeholder demo storyboard — 6 beats, captions only | 6G | live, placeholder (recording pending) |
| [`PHASE_6H_STATUS.md`](../archive/phase-status/PHASE_6H_STATUS.md) | Phase 6H Control Room OS close-out — 8 live loaders, 3-column shell, 6 panels, 10 dynamic routes, no fake data | 6H | live |
| [`PHASE_6I_STATUS.md`](../archive/phase-status/PHASE_6I_STATUS.md) | Phase 6I Launcher Rebuild close-out — 12-module v3 package, 7 surface primitives, 3-column shell, 5 captures, live untouched | 6I | live |
| [`PHASE_6J_STATUS.md`](../archive/phase-status/PHASE_6J_STATUS.md) | Phase 6J Control Room V2 close-out — top/bottom bars, Ctrl+K palette, 5 new routes, 2 new loaders, no mock values | 6J | live |
| [`CONTROL_ROOM_V2.md`](founder/CONTROL_ROOM_V2.md) | the founder's operating system — 14 routes, shell, palette, trust contract | 6J | live |
| [`PHASE_6K_STATUS.md`](../archive/phase-status/PHASE_6K_STATUS.md) | Phase 6K Launcher Promotion close-out — v3 LiveLauncher becomes default, legacy archived in place, `RECALL_LAUNCHER=legacy` escape hatch | 6K | live |
| [`PHASE_6L_STATUS.md`](../archive/phase-status/PHASE_6L_STATUS.md) | Phase 6L Launcher Simplification close-out — single floating surface, 3-column shell archived, 8 new minimal classes, 4 captures | 6L | live |
| [`PHASE_6M_STATUS.md`](../archive/phase-status/PHASE_6M_STATUS.md) | Phase 6M Desktop Memory Layer close-out — new `app/core/desktop/` capture package, `POST /v1/events/desktop`, `/desktop` control-room route, extension `⊞-N` badge | 6M | live |
| [`DESKTOP_LAYER.md`](product/DESKTOP_LAYER.md) | what the desktop watcher captures (and what it doesn't); metadata-only contract + aggregator rules + engine join | 6M | live |
| [`PHASE_6M.1_STATUS.md`](../archive/phase-status/PHASE_6M.1_STATUS.md) | Phase 6M.1 Launcher Refinement close-out — paper-white solid cards, 28/20/12 spacing, 22/14/12 typography, equal-width pills + overflow chip, vertically-centred empty | 6M.1 | live |
| [`LAUNCHER_REVIEW.md`](product/LAUNCHER_REVIEW.md) | per-refinement audit — what the 6M.1 refit removed / kept / why / future | 6M.1 | live |
| [`PHASE_6M.2_STATUS.md`](../archive/phase-status/PHASE_6M.2_STATUS.md) | Phase 6M.2 Launcher Geometry Recovery close-out — 720×520 window, 2×2 hero grid at 92 px, search capped 640, returns quieter, theme retuned 20/13/11/10 | 6M.2 | live |
| [`LAUNCHER_REGRESSION.md`](product/LAUNCHER_REGRESSION.md) | regression audit — why old looked better / what 6M.1 changed / what 6M.2 fixed (13-token table + Raycast↔Notion axis narrative) | 6M.2 | live |
| [`PHASE_6N_STATUS.md`](../archive/phase-status/PHASE_6N_STATUS.md) | Phase 6N Recovery Precision close-out — 3 signal states (HIGH/MED/LOW), confidence sentence row, preview card on empty, investigation sort | 6N | live |
| [`RECOVERY_VISUAL_AUDIT.md`](product/RECOVERY_VISUAL_AUDIT.md) | per-state visual contract — high / medium / low trust + silence + bad recovery + cross-cutting rules | 6N | live |
| [`PHASE_6O_STATUS.md`](../archive/phase-status/PHASE_6O_STATUS.md) | Phase 6O Launcher Reset close-out — 680×460 window, fixed 100-px hero, HIGH-only gate, 6 files archived to launcher-overbuild/ | 6O | live |
| [`LAUNCHER_RESET.md`](product/LAUNCHER_RESET.md) | the product reset audit — what removed / why launcher failed / new philosophy (3 failure modes + 3 design rules) | 6O | live |
| [`PHASE_6P_STATUS.md`](../archive/phase-status/PHASE_6P_STATUS.md) | Phase 6P Resume Reality close-out — preview overlay + restore toast + real OS opens, missing files skipped not fatal | 6P | live |
| [`RESUME_FLOW.md`](product/RESUME_FLOW.md) | end-to-end resume pipeline audit — source → decision → restore order → failure path | 6P | live |
| [`SHOWCASE_RUN.md`](product/SHOWCASE_RUN.md) | scripted WebSocket demo run + failure-injection matrix for verifying Resume reality | 6P | live |
| [`LAUNCHER_VISIBILITY.md`](product/LAUNCHER_VISIBILITY.md) | Phase 6P.1 launcher visibility recovery — warm page + layered cards + accent strip + window frame (problem · fix · before/after, 9-row table) | 6P.1 | live |
| [`PHASE_6Q_STATUS.md`](../archive/phase-status/PHASE_6Q_STATUS.md) | Phase 6Q Continuity Truth close-out — ledger + Why this? sheet + inspector CLI + trust CLI + showcase | 6Q | live |
| [`INVESTIGATION_PRINCIPLES.md`](product/INVESTIGATION_PRINCIPLES.md) | the 7 rules behind a recovery candidate + the 9 anti-noise trust gates | 6Q | live |
| [`PROMOTION_THRESHOLDS.md`](product/PROMOTION_THRESHOLDS.md) | LOW/MED/HIGH band rules + 5 overrides (unfinished/returned/duplicate/noise/ledger) + 4 worked examples | 6Q | live |
| [`SHOWCASE_TRUTH.md`](product/SHOWCASE_TRUTH.md) | three-investigation scripted walk verifying *only one hero* + the *Why this?* contract + the ledger-demotion path | 6Q | live |
| [`PHASE_6R_STATUS.md`](../archive/phase-status/PHASE_6R_STATUS.md) | Phase 6R Launcher Finalization close-out — 680×440 hard clamp, 88-px hero with chips + HIGH + Resume 112, vertical OTHER WORK, footer, launcher frozen | 6R | live |
| [`LAUNCHER_FINAL_AUDIT.md`](product/LAUNCHER_FINAL_AUDIT.md) | the frozen-product checklist — geometry · paint · hero/OTHER WORK/empty/footer contracts · 7-check visibility audit · the freeze rule | 6R | live |
| [`PHASE_7A_STATUS.md`](../archive/phase-status/PHASE_7A_STATUS.md) | Phase 7A Extension Product Surface close-out — 440×640 frozen popup, 6 fixed regions, search overlay, 7 captures | 7A | live |
| [`EXTENSION_PRODUCT_AUDIT.md`](product/EXTENSION_PRODUCT_AUDIT.md) | the extension's frozen-product checklist — paint · motion · per-region contracts · 7-row state catalogue + capture-architecture table | 7A | live |
| [`PHASE_7B_STATUS.md`](../archive/phase-status/PHASE_7B_STATUS.md) | Phase 7B Launcher Production Freeze close-out — single root card, no per-section chrome, Ctrl+K, timing log, launcher frozen forever | 7B | live |
| [`LAUNCHER_SHIP_AUDIT.md`](product/LAUNCHER_SHIP_AUDIT.md) | **superseded** by `LAUNCHER_VISUAL_MERGE.md` (7B.1) — 6R → 7B delta, paint/geometry/motion/per-region tables, visibility-pass, performance budgets | 7B | superseded |
| [`PHASE_7B.1_STATUS.md`](../archive/phase-status/PHASE_7B.1_STATUS.md) | Phase 7B.1 Launcher Visual Merge close-out — 740×500 single workspace, Continue document, infinity glyph empty, bottom strip, OTHER WORK removed | 7B.1 | live |
| [`LAUNCHER_VISUAL_MERGE.md`](product/LAUNCHER_VISUAL_MERGE.md) | **superseded** by `LAUNCHER_FINAL.md` (7E) — 7B → 7B.1 delta + Stitch-document workspace contract | 7B.1 | superseded |
| [`PHASE_7E_STATUS.md`](../archive/phase-status/PHASE_7E_STATUS.md) | Phase 7E Launcher Final Product Pass close-out — 700×500 single surface w/ Continue + RECENT MEMORY + OTHER WORK + live trust row | 7E | live |
| [`LAUNCHER_FINAL.md`](product/LAUNCHER_FINAL.md) | **supersedes** `LAUNCHER_VISUAL_MERGE.md` as the launcher's live contract — 7B.1 → 7E delta + frozen paint/geometry/typography/per-region tables + 5-row state catalogue + the removed-list | 7E | live |
| [`PHASE_7E.1_STATUS.md`](../archive/phase-status/PHASE_7E.1_STATUS.md) | Phase 7E.1 Launcher Stability close-out — restored `request_settings` + `request_close` signals dropped during 7E rewrite + froze the public interface | 7E.1 | live |
| [`LAUNCHER_CONTRACTS.md`](product/LAUNCHER_CONTRACTS.md) | frozen Python interface for the launcher (`MinimalSearchBar` + `LiveLauncher` signals/methods + wiring map + freeze rule); no future phase may remove or rename these symbols | 7E.1 | live |
| [`PHASE_7D_STATUS.md`](../archive/phase-status/PHASE_7D_STATUS.md) | Phase 7D Capture Truth Audit close-out — `recall capture status` + `recall capture tail` CLIs + seven-hop flow doc | 7D | live |
| [`CAPTURE_FLOW.md`](product/CAPTURE_FLOW.md) | seven-hop end-to-end capture pipeline (browser → extension → daemon → store → investigation → recovery → launcher) with per-hop file/function + verification CLIs + scripted 7-step verification walk | 7D | live |
| [`ALPHA_MATRIX.md`](trust/ALPHA_MATRIX.md) | 5 install-validation slots × 7 columns (Windows ×3 / Mac Intel / Mac Silicon) | 5K | live, all `unknown` |
| [`alpha/ALPHA_FEEDBACK_V2.md`](../alpha/ALPHA_FEEDBACK_V2.md) | tightened 6-row intake form (delight / confusion / wrong / missed / install pain / keep-remove) | 5K | live |
| [`alpha/users/`](../alpha/users) | per-tester records: 5 cohort folders + TEMPLATE + JSON schema (zero fake testers) | 5K | live |

## `docs/release/` — what ships when

| Doc | Purpose | Phase | Status |
|---|---|---|---|
| [`CHANGELOG.md`](release/CHANGELOG.md) | the phase-by-phase record | 4A → live | live |
| [`VERSIONING.md`](release/VERSIONING.md) | SemVer rules | 4A | live |
| [`RELEASE.md`](release/RELEASE.md) | release ladder + pipeline | 4A | live |
| [`INSTALL.md`](release/INSTALL.md) | the grandmother install path | 5A | live |
| [`DOWNLOADS.md`](release/DOWNLOADS.md) | artifact table + SHA-256 | 5A | live |
| [`SUPPORTED_PLATFORMS.md`](release/SUPPORTED_PLATFORMS.md) | tier matrix + release gates | 5A | live |
| [`MAC_BUILD_STATUS.md`](release/MAC_BUILD_STATUS.md) | honest not-pretending macOS tracker | 5A.1 | preview |
| [`MAC_VERIFICATION.md`](release/MAC_VERIFICATION.md) | the 13-row × 2-chip macOS verification matrix | 5F | unknown (all rows) |
| [`MAC_OWNER_NEEDED.md`](release/MAC_OWNER_NEEDED.md) | dispatch ticket for any maintainer with a Mac — script, time, blocking rows | 5G | live |
| [`INSTALL_METRICS.md`](release/INSTALL_METRICS.md) | the five install numbers (size, install/launch time, memory, disk) | 5G | live |
| [`LANDING_GO_LIVE.md`](release/LANDING_GO_LIVE.md) | the seven-section website checklist before the landing goes live | 5H | live (all rows ⬜) |
| [`RECORDING_PROTOCOL.md`](release/RECORDING_PROTOCOL.md) | beat-by-beat recipe for `install.gif` + `control-room.gif` | 5H | live |
| [`GO_NO_GO.md`](release/GO_NO_GO.md) | the public-alpha gate | 5A.1 | NO-GO (gates 1 + 7) |
| [`PUBLIC_ALPHA_CHECKLIST.md`](release/PUBLIC_ALPHA_CHECKLIST.md) | 18-row pre-flight checklist | 5C | live |

## `docs/trust/` — keeping the surfaces honest

| Doc | Purpose | Phase | Status |
|---|---|---|---|
| [`TRUST_FIXTURES.md`](trust/TRUST_FIXTURES.md) | continuity-trust fixtures (excellent / silence / suppressed) | 4G | live |
| [`TRUST_FIXTURES_CONTINUITY.md`](trust/TRUST_FIXTURES_CONTINUITY.md) | investigation-grouping fixtures (correct/bad merge/split) | 4H | live |
| [`TRUST_FIXTURES_DAILY.md`](trust/TRUST_FIXTURES_DAILY.md) | daily-loop fixtures (morning recovery / evening resume) | 5B | live |
| [`INSTALL_VALIDATION_WINDOWS.md`](trust/INSTALL_VALIDATION_WINDOWS.md) | Windows install proof + 13-row checklist (5A.1 cycle) | 5A.1 | superseded by `INSTALL_PROOF_WINDOWS.md` + `CLEAN_MACHINE_RUN.md` |
| [`INSTALL_PROOF_WINDOWS.md`](trust/INSTALL_PROOF_WINDOWS.md) | Phase 5F build proof of `Recall-Setup.exe` artifact | 5F | live |
| [`CLEAN_MACHINE_RUN.md`](trust/CLEAN_MACHINE_RUN.md) | the gate-1 walk record (13-row checklist × N-runs) | 5G | 1 row filled (build machine ▲); 3 clean-VM rows ⬜ |
| [`RECOVERY_STRESS.md`](trust/RECOVERY_STRESS.md) | trust-stress coverage matrix (3 live + 3 design scenarios) | 5G | live |
| [`EXTENSION_VALIDATION.md`](trust/EXTENSION_VALIDATION.md) | extension pairing state matrix | 5A.1 | partial |

## `alpha/` — the public alpha packet (top-level, ship-ready)

| Doc | Purpose | Phase | Status |
|---|---|---|---|
| [`alpha/README.md`](../alpha/README.md) | door — five files, total cold-start under 15 minutes | 5F | live |
| [`alpha/INSTALL.md`](../alpha/INSTALL.md) | the alpha install walkthrough — Windows-first, honest | 5F | live |
| [`alpha/SAMPLE_WORKFLOW.md`](../alpha/SAMPLE_WORKFLOW.md) | day 0 → day 7 — what to expect, what success looks like | 5F | live |
| [`alpha/TRUST.md`](../alpha/TRUST.md) | the contract before granting folder access | 5F | live |
| [`alpha/LIMITATIONS.md`](../alpha/LIMITATIONS.md) | what does not work yet, design vs gap | 5F | live |
| [`alpha/FEEDBACK.md`](../alpha/FEEDBACK.md) | the end-of-week-one return form | 5F | live |
| [`alpha/alpha_report.md`](../alpha/alpha_report.md) | the founder-side evidence ledger (5 questions + sources of truth) | 5G | awaiting cohort data |
| [`alpha/ALPHA_001_RUNBOOK.md`](../alpha/ALPHA_001_RUNBOOK.md) | five-persona runbook × four-day journey × four expected first-of dates | 5H | live |
| [`alpha/launcher/`](../alpha/launcher) | five-file no-terminal install pack for cohort testers | 5H | live |
| [`alpha/recovery_journal.json`](../alpha/recovery_journal.json) | per-Resume ledger (hand-edited, never imported from telemetry) | 5H | awaiting cohort data |

## `docs/archive/old-docs/` — preserved, not live

| Doc | Why archived |
|---|---|
| [`PHASE_4A_STATUS.md`](archive/old-docs/PHASE_4A_STATUS.md) | superseded by `PHASE_TRACKER.md` |

## How to read this index

- A row is **live** if it is referenced from `README.md` /
  `CLAUDE.md` / another live doc, or it is the canonical source
  on a topic the project still does.
- A row is **partial** if it documents a process whose evidence
  rows are themselves still ⛔/⏳ (most often the install-validation
  walks, gated on a clean-machine run).
- A row is **historical reference** if it is read for context but
  no longer the canonical source (e.g. an early audit that has
  been folded into a later, more current one).
- A row in `archive/` is **kept-but-frozen** — `git mv` brought it
  here so the history is preserved without it cluttering the live
  set.

If you are looking for *what Recall is*, start at
[`/README.md`](../README.md) and [`product/`](product). If you are
joining as an engineer, [`engineering/REPO_HEALTH.md`](engineering/REPO_HEALTH.md)
§ *What a new engineer should know* + [`/CLAUDE.md`](../CLAUDE.md)
are the one-hour onboarding.
