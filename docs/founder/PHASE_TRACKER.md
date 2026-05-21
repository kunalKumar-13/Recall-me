# PHASE_TRACKER.md — where the build is

The 30-second answer to *"what state is Recall in?"* Updated at the
close of every phase. Pairs with [`ROADMAP_LIVE.md`](ROADMAP_LIVE.md)
(what's next) and [`CHANGELOG.md`](../release/CHANGELOG.md) (what changed).

---

## Current phase

**Repo Stabilization Pass.** Pure cleanup. 28 unused Python
imports removed across 14 files (pyflakes-zero on the engine);
3 empty f-strings → plain strings; the duplicate
`_transition_colour` definition in `widgets.py` collapsed; the
unused `time_label` local in `launcher.py` dropped; the
extension's 5I-leftover `calmFlash` / `calmSlow` motion exports
and the un-consumed `MOTION_*_S` numeric constants un-exported
(zero consumers). Root gained a small `CHANGELOG.md` redirect
(canonical lives at `docs/release/CHANGELOG.md`). `.gitignore`
hardened against build artifacts and transient logs. All five
build surfaces verified clean: doctor 5G/4Y/0R, launcher import
OK, `npm run build` on extension + control room both pass,
`recall founder status` 61/100 unchanged.

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
