# ROADMAP_LIVE.md — what's being built, and what isn't

A living board. Four columns. **Never** is as load-bearing as the
other three — it is the public record of what Recall refuses to
become, so scope creep has somewhere to die.

Pairs with [`PHASE_TRACKER.md`](PHASE_TRACKER.md) (build state).

---

## Now

*In the current phase.*

- **Phase 6H — Control Room OS** (this phase). The founder
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
  [`PHASE_6H_STATUS.md`](../engineering/PHASE_6H_STATUS.md).

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
  [`PHASE_6G_STATUS.md`](../engineering/PHASE_6G_STATUS.md).

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
  [`PHASE_6F_STATUS.md`](../engineering/PHASE_6F_STATUS.md).

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
  [`PHASE_6E_STATUS.md`](../engineering/PHASE_6E_STATUS.md).

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
  [`PHASE_6D_STATUS.md`](../engineering/PHASE_6D_STATUS.md).
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
  [`PHASE_6C_STATUS.md`](../engineering/PHASE_6C_STATUS.md).

- **Phase 6B — Launcher Identity** (prior phase). The theme swap
  deferred from 6A landed. Palette inverted to warm white +
  lavender (matching the extension popup); `LAUNCHER_QSS`
  rewritten with a floating white card + generous spacing; the
  evidence text line finally split into `[2 tabs] [3 files] [2d
  gap]` chip pills via `_EvidenceChip` + `_parse_evidence_chips`;
  `EmptyCard.empty` redesigned at 210 px with *"Recall notices
  unfinished work."* and a soft Show-example lavender pill. 7
  new captures in `assets/screenshots/launcher-v2/`. Receipt:
  [`PHASE_6B_STATUS.md`](../engineering/PHASE_6B_STATUS.md).

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
