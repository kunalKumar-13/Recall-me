# ROADMAP_LIVE.md — what's being built, and what isn't

A living board. Four columns. **Never** is as load-bearing as the
other three — it is the public record of what Recall refuses to
become, so scope creep has somewhere to die.

Pairs with [`PHASE_TRACKER.md`](PHASE_TRACKER.md) (build state).

---

## Now

*In the current phase.*

- **Repo Stabilization Pass** (this pass). Pure cleanup, no
  behaviour change. Dead-code audit + import sweep + duplicate-
  function collapse + un-export of zero-consumer motion exports
  + a root `CHANGELOG.md` redirect + `.gitignore` hardening.
  Full receipt: [`REPO_CLEANUP_REPORT.md`](../engineering/REPO_CLEANUP_REPORT.md).
  All five build surfaces re-verified (doctor / launcher import /
  extension `npm run build` / control-room `next build` /
  `recall founder status`).

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
