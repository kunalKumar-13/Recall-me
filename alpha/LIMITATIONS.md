# Limitations — what does not work yet

Honest list. Some of these are **design** (never going to change).
Some are **gaps** (being closed). Both are below, labelled.

The longer engineering version is
[`docs/product/KNOWN_LIMITATIONS.md`](../docs/product/KNOWN_LIMITATIONS.md).

---

## By design — choices, not bugs

These will not change.

- **No cloud sync.** New laptop = fresh `~/.recall/`. A continuity
  tool only earns trust if it never leaves your machine.
- **Single-user.** One user, one machine. No team workspace, no
  shared account.
- **No notifications.** No badges, no streaks, no "you have 12
  unread recoveries!" The launcher waits for you.
- **No LLM in the path.** Capture, scoring, and recovery are
  deterministic heuristics. The only model is a local embedding
  model for file search.
- **Day 1 is quiet.** Recovery only surfaces real interrupted
  work — and there is no real interrupted work on day 1. See
  [`SAMPLE_WORKFLOW.md`](SAMPLE_WORKFLOW.md).
- **A wrong recovery is worse than no recovery.** Recall biases
  toward silence. If you see no card today, the gate worked — it
  did not have a card it trusted.

## Gaps — the named fixes

These are real; the fix is named in
[`docs/founder/ROADMAP_LIVE.md`](../docs/founder/ROADMAP_LIVE.md).

### Platform gaps

- **macOS: Preview only.** No `.dmg` has been verified on macOS
  hardware. Tracked in
  [`docs/release/MAC_VERIFICATION.md`](../docs/release/MAC_VERIFICATION.md).
- **Linux: source only.** PyQt6 runs; no packaged build.
- **Firefox: not supported.** The extension is MV3; Firefox's MV3
  story differs. Chromium-only for now (Chrome, Edge, Brave, Arc,
  Opera).
- **Safari: not on the roadmap.**

### Install / launch gaps

- **SmartScreen warning on first run.** The installer is **unsigned**.
  Closing this needs an EV code-signing certificate — tracked in
  [`docs/release/GO_NO_GO.md`](../docs/release/GO_NO_GO.md) gate 7.
  *Click More info → Run anyway* is the workaround for the alpha
  cycle.
- **`recall://` deep-link not registered.** The extension popup's
  *Open Recall* button does not deep-link into a specific tab; it
  focuses the launcher instead. Doctor reports this as YELLOW.
- **No auto-update.** Updates are install-over-install (the
  installer's `/SILENT` mode supports it). An auto-update channel
  is a *Later* roadmap item.

### Extension pairing gaps

- **Extension is unpacked, not Web-Store-published.** You load it
  via *Developer mode → Load unpacked*. The Chrome Web Store
  listing is a later release step.
- **First connect can take ~5 seconds.** The popup polls the
  daemon at startup; if the daemon was just launched, the first
  poll may say *Disconnected* before the second succeeds.

### Surface gaps

- **Settings dialog screenshot not yet automated** — the launcher
  and recovery card have real captures (Phase 4L); a settings
  capture is pending a Config fixture.
- **Extension popup screenshots are state-fixtures, not
  end-to-end captures** — Playwright wiring is partial.

## Behaviour that looks like a bug but is not

- **Empty launcher.** Days 0-1 are intentionally empty. The
  digest only fills when there is real interrupted work to
  surface.
- **Recovery silence.** Even after a heavy week, Recall may show
  no card. If your week was many short tasks with no multi-day
  arc, *Active investigations* and *On your radar* fill instead.
- **Plain investigation titles.** Titles come from your own page
  titles, search queries, and filenames — not from a model
  inventing a name. Plain stays honest.

## When something is actually broken

| You see | Likely cause |
|---|---|
| Tray icon missing | Recall not running — relaunch from desktop shortcut |
| `recall doctor` RED on `daemon` | Recall not running, or `127.0.0.1:4545` is taken |
| Popup says *Recall not found* | Extension is loaded but daemon is down |
| Launcher opens but is blank for >3 days | extension not paired, or no indexed folders had activity |
| `Recall-Setup.exe` says "Windows protected your PC" | SmartScreen; click *More info → Run anyway* |

Anything else: file in [`FEEDBACK.md`](FEEDBACK.md) under *bug*.
