# Changelog

All notable changes to Recall are recorded here.

The format is loosely based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the
project follows [Semantic Versioning](VERSIONING.md). Internal
phase identifiers (Phase 2A, 2B, …) are listed alongside the
public version so contributors can trace artefacts back to their
build cycle.

## [Unreleased]

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
  [`apps/desktop/README.md`](apps/desktop/README.md).
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
