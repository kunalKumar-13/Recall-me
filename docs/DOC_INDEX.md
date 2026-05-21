# DOC_INDEX.md — every doc, with its job

The single index of Recall's documentation system after the Phase
5D.1 consolidation. Every row: where it lives, what it answers, who
owns it, the phase it landed, the status today.

Pairs with [`engineering/DOC_HEALTH.md`](engineering/DOC_HEALTH.md)
(the live metrics).

---

## Root — what stays at the front door

| Doc | Purpose | Owner | Phase | Status |
|---|---|---|---|---|
| [`/README.md`](../README.md) | first read; what Recall is | founder | 1A → 5D.1 | live |
| [`/CLAUDE.md`](../CLAUDE.md) | engineering charter — the working contract | founder | 4A | live |
| [`/CONTRIBUTING.md`](../CONTRIBUTING.md) | what to send a PR for, what won't be accepted | maintainer | 4A | live |
| [`/SECURITY.md`](../SECURITY.md) | vulnerability reporting | maintainer | 4A | live |
| [`/CODE_OF_CONDUCT.md`](../CODE_OF_CONDUCT.md) | community standard | maintainer | 4A | live |
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
| [`alpha/launcher/`](../alpha/launcher/) | five-file no-terminal install pack for cohort testers | 5H | live |
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
[`/README.md`](../README.md) and [`product/`](product/). If you are
joining as an engineer, [`engineering/REPO_HEALTH.md`](engineering/REPO_HEALTH.md)
§ *What a new engineer should know* + [`/CLAUDE.md`](../CLAUDE.md)
are the one-hour onboarding.
