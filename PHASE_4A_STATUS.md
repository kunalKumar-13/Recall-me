# Phase 4A — Productization status

This file is the honest accounting of what shipped in Phase 4A
and what was deliberately deferred. It's referenced by
`CHANGELOG.md` and lives at the repo root so a future maintainer
doesn't have to dig.

## Shipped

| # | Brief objective | What landed | Where |
|---|---|---|---|
| 1 | First-run experience | Empty-state copy retoned ("Recall is ready.") + quiet first-week hint when all synthesis surfaces return empty | `app/ui/launcher.py` |
| 2 | Installer + packaging architecture | Release-channel architecture, installer pipeline doc, signing notes, deferral rationale | `RELEASE.md` |
| 3 | Release channel system | `stable / preview / nightly` design + `~/.recall/version.json` format | `RELEASE.md` |
| 4 | Error-handling discipline | Charter rule 15 (productize, don't prototype) | `CLAUDE.md` |
| 5 | Empty-state UX | First-week hint + retoned first-run copy | `app/ui/launcher.py` |
| 6 | Trust surfaces | Troubleshooting page + FAQ + install validation | `docs/troubleshooting.mdx`, `docs/faq.mdx`, `docs/install-validation.mdx` |
| 7 | Launcher refinement | Empty-state strings; rest of polish is incremental | `app/ui/launcher.py` |
| 8 | Visual system | Full design-system codification | `docs/architecture/visual-system.mdx` |
| 9 | Landing-page sync | Path-A surgical pass on `ContinueWorking` | `web/app/components/ContinueWorking.tsx` |
| 11 | Docs hardening | Troubleshooting + FAQ + install validation + updated nav | `docs/`, `docs/mint.json` |
| 13 | OSS readiness | `CHANGELOG.md`, `VERSIONING.md`, `RELEASE.md` | repo root |
| 14 | Product narrative | "Local-first continuity operating system" framing | `README.md`, `CLAUDE.md` |
| 15 | Performance | 29-section smoke suite green at 5/5 stability | `_smoke_api.py` |

## Deferred (with rationale)

Each item below is intentionally not shipped this cycle. The
gate condition for shipping it later is named.

### 2. Signed Windows installer build

**Why deferred:** A signed installer requires a real Windows
code-signing certificate (DigiCert / Sectigo / Comodo,
≈ $300–500/yr; EV certs more). That is a project-funding
question, not an engineering one.

**What did ship:** The release pipeline is fully documented in
[`RELEASE.md`](RELEASE.md), including the exact `signtool`
command, the recommended Inno Setup wrapper, and where the
`.iss` script would live. The unsigned `pyinstaller` build path
remains the pre-1.0.0 distribution mechanism.

**Gate to ship:** A code-signing certificate is procured.

### 10. Real screenshots

**Why deferred:** Screenshots have to be captured from an
actual running launcher. That requires Windows + PyQt6 + the
full installed pipeline. Cannot be produced from text-only
tooling.

**What did ship:** The list of needed captures is in
[`docs/install-validation.mdx`](docs/install-validation.mdx)
§ *"What healthy looks like over time"* — six target screens
identified, each tied to a section in the launcher's idle
digest.

**Gate to ship:** A maintainer running the launcher captures
the six screens at 1×, drops them in
`docs/images/launcher-*.png`, and replaces the placeholder
captions in `docs/introduction.mdx`,
`docs/features/browser-memory.mdx`,
`docs/architecture/sessions.mdx`,
`docs/architecture/micro-contexts.mdx`, and
`docs/architecture/retrieval-pipeline.mdx`. The same five
placeholders identified in
[`AUDIT_REPORT.md`](AUDIT_REPORT.md) § 3.4.

### 12. Repo split into `recall-core` / `recall-extension` / `recall-web` / `recall-docs`

**Why deferred:** Multi-repo split is a major operation that
needs maintainer + community buy-in. The monorepo today earns
its keep — most engine changes touch the core + API + extension
+ docs in one PR, which is much harder across four repos.
Premature splitting introduces release-coordination overhead
the project doesn't yet need.

**What did ship:** A documented repo-split plan, with named
boundaries and a gate condition, in
[`RELEASE.md`](RELEASE.md) § *Repo split plan*.

**Gate to ship:** At least one of:
- the launcher and the extension start being released on
  independent cycles, **or**
- the web team is genuinely separate from the engine team,
  **or**
- the contribution map shows persistent confusion over which
  subdirectory owns what.

### Auto-update implementation

**Why deferred:** Implementing in-process update fetching is a
1.0.0 milestone — it needs a stable release host, a signing
infrastructure, and a code-signing identity that can verify
downloaded artefacts. None of those exist yet.

**What did ship:** The full architecture in
[`RELEASE.md`](RELEASE.md) § *Auto-update architecture
(planned)* — manifest format, channel discipline, signing
verification flow, and the explicit guarantee that no install
ever phones home.

**Gate to ship:** A signed release infrastructure (see
"Signed Windows installer build" above).

### Onboarding wizard (multi-step first-run flow)

**Why deferred:** The brief lists "permissions explanation,
browser-extension setup flow, indexed-folders setup, keyboard
shortcut education, privacy explanation" as a first-run
sequence. The product today handles these through a single
calm Settings dialog plus boot diagnostics — and the audit
showed that adding ceremony there can actually *reduce* trust
("why is this AI tool asking me so many questions?").

**What did ship:** The single-screen first-run state
(`empty_widget`) was retoned to set the right trust tone
upfront: *"Recall is ready. Press Ctrl + , to open Settings…"*
plus the first-week hint that explains why the digest is
quiet on a fresh install.

**Gate to ship:** User testing (n ≥ 5 real users on a fresh
install) showing that the single-screen first-run is
insufficient. Until then, the brief's anti-ceremony rule
applies.

### 11/13. "Performance expectations" doc, "good first issues",
"roadmap board", "contribution map"

**Why partially deferred:** The bones are in place
([`CONTRIBUTING.md`](CONTRIBUTING.md),
[`AUDIT_REPORT.md`](AUDIT_REPORT.md),
[`docs/roadmap.mdx`](docs/roadmap.mdx)) but assembling a polished
"good first issues" board requires the GitHub side of the
project to actually exist as a public repo with issues open.

**What did ship:** The four standing trackers
(`CHANGELOG.md`, `VERSIONING.md`, `RELEASE.md`, this file)
plus the audit-report items marked **[FIXED]** vs open.

**Gate to ship:** Public-launch readiness (sometime around
0.2.x).

---

## Smoke + perf status at Phase 4A close

- 29 sections, 5/5 stability run after the Phase-4A edits.
- The two pre-existing wall-time flakes (section 11 search,
  section 20 threads) remained in place; both were re-tuned
  earlier this cycle to best-of-3 with realistic envelopes.
- No new perf assertions added — the productization work
  doesn't touch the engine's hot paths.

## Next milestone recommendation

**Recall 0.2.0 — public 0.x release.** Spend one cycle on:

1. Closing the open items in [`AUDIT_REPORT.md`](AUDIT_REPORT.md).
2. Capturing the six real screenshots (gate condition for
   removing the placeholder captions).
3. Filling in any troubleshooting / FAQ entries that come
   up during the first wave of public install attempts.
4. Procuring a code-signing certificate (one-time gate for
   shipping signed Windows installers and the auto-update
   pipeline).

After 0.2.0 ships and stays stable for a cycle, 1.0.0 becomes
the next named milestone.
