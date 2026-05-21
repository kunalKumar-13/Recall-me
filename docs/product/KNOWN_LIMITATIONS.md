# KNOWN_LIMITATIONS.md — what Recall is not, today

A first user deserves the limits stated plainly before they hit
them. Some of these are **design** — deliberate, never going away.
Some are **gaps** — being closed. Both are below, labelled
honestly. No "we'll see," no "coming soon" without a target.

---

## By design — not gaps, choices

These will not change.

- **No cloud.** Nothing syncs across devices. If you reinstall on a
  new laptop, you start with a fresh `~/.recall/`. *Why* — a
  continuity tool is only worth trusting if it never leaves the
  machine. The promise and cloud sync cannot both be true. See
  [`TRUST_LEDGER.md`](../engineering/TRUST_LEDGER.md).
- **Single-user.** Recall is one user, one machine. There is no
  team account, no shared workspace. The bind is the boundary.
- **No telemetry.** Recall does not phone home. The founder
  dashboard is fed by *voluntary* `recall stats --export` files
  the user chooses to send. See
  [`FOUNDER_DASHBOARD.md`](../founder/FOUNDER_DASHBOARD.md).
- **No notifications, streaks, or scores.** No badges, no daily
  goals, no productivity grade. Phase 5B added time-of-day
  framing; that is the entire concession to "daily loop".
- **No LLM in the production path.** Capture, scoring, and
  recovery are all deterministic. The only model is the local
  embedding model used by file search — downloaded once, then
  `local_files_only=True`.
- **Recovery biases toward silence.** *A missed recovery is better
  than a weak one.* If you see no card today, the gate worked,
  not the engine failed.

## Gaps being closed

These are real. The fix is named.

- **macOS is Preview, not Supported.** Packaging is written; no
  `.dmg` has been built or tested on macOS. Recall on Mac means
  *run from source* until that changes. See
  [`MAC_BUILD_STATUS.md`](../release/MAC_BUILD_STATUS.md).
- **Linux: source only.** No packaged artifact yet. PyQt6 runs
  fine; install from source via
  [`apps/docs/install-3min.mdx`](../../apps/docs/install-3min.mdx).
- **The installer is unsigned.** Windows SmartScreen warns on
  first run; macOS Gatekeeper would warn if a `.dmg` existed.
  Closing this needs an EV cert (Windows) + Apple Developer ID
  (macOS). Tracked in [`GO_NO_GO.md`](../release/GO_NO_GO.md) gate 7.
- **Browser support: Chromium-only.** The extension is MV3 — it
  loads in Chrome, Edge, Brave, Arc, Opera. **Firefox is not
  supported yet** (its MV3 story differs); Safari is not on the
  roadmap. Source-port for Firefox is possible; it is not
  scheduled.
- **Manual export.** `recall stats --export` writes a file. There
  is no "send to founder" button — by design (no telemetry path) —
  but also no in-app share helper. The user emails / pastes /
  drops the file themselves.
- **No auto-update.** Updates are install-over-install; the
  installer's `/SILENT` mode supports it. An auto-update channel
  is a [`ROADMAP_LIVE.md`](../founder/ROADMAP_LIVE.md) *Later* item.
- **`capture_settings.py` / `capture_extension.py` partial.** The
  launcher and recovery card have real screenshots
  (Phase 4L + 5A.1); a settings-dialog capture needs a Config
  fixture, and the extension capture is Playwright-based and
  Chromium-only.

## Behaviour you may notice and wonder about

These are working as intended; they look surprising.

- **The first day shows nothing.** Days 0–1 are empty by design.
  Recovery only surfaces real interrupted work — and there is no
  real interrupted work until there is. See
  [`FIRST_WEEK.md`](../founder/FIRST_WEEK.md).
- **Recovery may surface *no* cards** even after a week of heavy
  use. If your week was many short topics with no multi-day arc,
  recovery has nothing high-trust to offer. *Active
  investigations* and *On your radar* will be busier instead.
- **Recall does not "summarise" your work.** It restores artifacts
  — files, tabs, chats — in order. It never writes prose about
  what you did. See [`SURFACE_MAP.md`](SURFACE_MAP.md).
- **Investigation titles can be plain.** They come from your own
  page titles, search queries, and filenames — not from a model
  inventing a name. Plain wins over polished, because plain stays
  honest.

## What you should *not* see

If any of these happens, file an issue:

- A network request to anything other than `127.0.0.1:4545` (after
  first-run model download).
- A captured filename, URL, or query in `stats.json`.
- A recovery card for a topic you never worked on.
- Recall surviving a `rm -rf ~/.recall/` (it should not — that
  *is* a full reset).
- Any string referring to "AI memory", "smart memory", "AI
  assistant", or a productivity score in user copy.

Each of those is a contract violation. The rest of the list above
is the truthful set of limits — owned, not hidden.
