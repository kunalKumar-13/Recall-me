# OPEN_PROBLEMS.md — what is still actually wrong

The honest list. Every entry here is either a real friction the
project knows about but has not closed, or a directive item that
was named in a phase but cleanly deferred with a written reason.

Companion to [`FRICTION_FIXED.md`](FRICTION_FIXED.md): if a
friction is not in *that* file and not on a roadmap row, it
should be here.

Open problems get one line each: **what is wrong / why it is hard
/ what closes it**. No prose; this is a punch list, not a roadmap.

---

## External dependencies (nothing the maintainer can fix alone)

| # | Problem | Why hard | What closes it |
|---|---|---|---|
| 1 | No EV code-signing certificate | costs ~$300/yr + identity check | maintainer procures cert; signs `Recall-Setup.exe`; SmartScreen warning stops |
| 2 | No Apple Developer ID + notarisation | $99/yr + Mac access | maintainer enrols; macOS Gatekeeper warning stops |
| 3 | macOS verification all `unknown` | no Mac hardware | a maintainer with a Mac runs the script in [`MAC_OWNER_NEEDED.md`](../release/MAC_OWNER_NEEDED.md) |
| 4 | Zero alpha-001 testers enrolled | no distribution channel opened | maintainer hand-shares the [`alpha/`](../../alpha/) packet to five real humans |
| 5 | Three fresh-VM clean-machine walks pending | no VM hosts on this build machine | three runs of [`CLEAN_MACHINE_RUN.md`](../trust/CLEAN_MACHINE_RUN.md) on three different fresh Win10/11 VMs |
| 6 | `install.gif` + `control-room.gif` need live recording | static PNGs can't show motion | follow [`RECORDING_PROTOCOL.md`](../release/RECORDING_PROTOCOL.md) on a recording-quality screen |
| 7 | `LICENSE` file missing at root | maintainer must pick a license | choose MIT / Apache-2 / source-available; add the file |

## Performance (Phase 5J update — Tier A shipped)

| # | Problem | State | Closure path |
|---|---|---|---|
| 8 | Tier A — PyInstaller excludes only | **✅ shipped Phase 5J** (partial; pandas kept). Installer: 260 → **216 MB** (−45 MB); bundle 970 → 783 MB. The V2 audit predicted ≤ 180 MB; the gap (~36 MB) is the pandas exclude in row 9. |
| 9 | Pandas + tzdata exclude (Tier A2) | open | add `pandas` + `tzdata` to `TIER_A_EXCLUDES` in `recall.spec`; rebuild; verify `chromadb.utils.results` is not on Recall's runtime path. Expected: installer ~195 MB. |
| 10 | Tier B — `torch+cpu` pin | open | one `requirements.txt` change to the PyTorch CPU index; rebuild. Expected: installer ~150 MB; install time ~30 s. |
| 11 | Tier C — ONNX route | open | ~80 LOC swap in `app/core/embeddings.py`; drops torch + transformers + sentence_transformers; ships ~80 MB ONNX model. Expected: installer ~50 MB; install time ~15-20 s. Detailed in [`MODEL_STRATEGY.md`](MODEL_STRATEGY.md). |
| 12 | Tier D — Split Distribution (Core 30 MB + optional Retrieval Pack) | open | re-tier `recall.iss` to Inno Setup `[Components]`; default minimal install. Detailed in [`SPLIT_DISTRIBUTION.md`](SPLIT_DISTRIBUTION.md). |
| 13 | Resident memory 623 MB after warm-up | open | partial overlap with row 11 — Tier C + lazy-load on first search drops resident to ~150 MB. |
| 14 | Cold launch time on a clean VM unmeasured | open | needs a fresh VM walk; row in [`CLEAN_MACHINE_RUN.md`](../trust/CLEAN_MACHINE_RUN.md). |
| 15 | Lite-installer install wall time unmeasured | open | wipe-and-reinstall on user's `~/.recall` was permission-denied this phase; clean-VM run measures it. Projection: 66 s → ~50-55 s on a similar machine. |

## Extension popup

| # | Problem | Why hard | What closes it |
|---|---|---|---|
| 12 | No timeline chips on the recovery card | minor design + react work | a new `<TimelineChips>` component reading `recovery.lastActiveAt` + the prior-N-day evidence; one chip per active day |
| 13 | No mini investigation graph | needs a small SVG / canvas + a data shape that doesn't yet exist on `/v1/threads/recent` | either expose a node/edge count per thread, or skip the graph and use chips |
| 14 | No first-run onboarding overlay | the popup currently lands in EMPTY / DisconnectedState without explainer chrome | a one-time overlay reading `chrome.storage.local["recall.onboardingSeen"]`; deferred to keep the popup minimal |
| 15 | `recall://` Open Recall button dispatch can't tell success from failure | OS does not signal handler-missing back to the page | inevitable; the `OpenRecallButton` already cycles `trying → hint` as a workaround |
| 16 | Extension popup width is fixed at 440 px | MV3 popup cannot resize at runtime | accept; the 440 px sits inside the spec's 420-480 range |

## Doctor / install_repair

| # | Problem | Why hard | What closes it |
|---|---|---|---|
| 17 | `recall://` registered by `repair` does not propagate to currently-open browsers | OS protocol routing is cached per session | user reopens the browser; deferred to a small footer note in the future popup help |
| 18 | `recall reset --full` is destructive but does not currently back up | accept; the directive's `reinstall-check` already names the optional backup command | the verb is documented as destructive; users who want a backup run `cp -r ~/.recall ~/.recall.bak` first |
| 19 | `repair` cannot fix a missing PyInstaller bundle | the bundle is the install itself | reinstall via `Recall-Setup.exe`; the message in `repair`'s RED summary already says so |

## Launcher

| # | Problem | Why hard | What closes it |
|---|---|---|---|
| 20 | Stagger reveal plays only on the first digest open per session | by design (Phase 4I motion rule) | accept; the *every-reopen* alternative violates the calm-software rule |
| 21 | Recovery card click is immediately destructive (opens tabs) | by design — one-click resume is the product moment | accept; the *confirmation modal* alternative violates the alpha UX brief |
| 22 | Onboarding overlay in launcher (folders picker on first run) | already exists at `app/ui/onboarding.py`; not currently flagged | leave; the issue would be if it stopped firing, not its presence |
| 23 | No live "events captured today" counter on the launcher footer | `/v1/health` does not return per-day yet; we have lifetime `ingested_total` only | accept for alpha; add `events_today` to `/v1/health` is engine work and explicitly out-of-scope for friction phases |

## Docs / repo

| # | Problem | Why hard | What closes it |
|---|---|---|---|
| 24 | `docs/phases/` subdir named in the brief, never created | no clear content for it | accept; per-phase records live in `CHANGELOG.md` already |
| 25 | `docs/alpha/` subdir named in the brief, never created | `alpha/` at the repo root is the cohort packet, not docs | accept; documented in [`REPO_CLEANUP_REPORT.md`](REPO_CLEANUP_REPORT.md) |
| 26 | `CLAUDE.md` lives at root but the brief listed only six root files | agent-tool auto-load convention | intentional exception; documented in `REPO_CLEANUP_REPORT.md` |

---

## Counts

- External-dependent: **7 items** (need maintainer action: signing, macOS hardware, cohort, VMs, screen recording, license)
- Performance: **4 items**
- Extension popup: **5 items** (3 deferred designs + 2 accepted constraints)
- Doctor / install_repair: **3 items** (all *accept-and-document*)
- Launcher: **4 items** (mostly *accept by design*)
- Docs / repo: **3 items** (all documented as intentional)

**Total open: 26 items.** Of those, 16 are *accept by design* or
*accept with documentation*. The remaining 10 are real work
items, distributed:

- **7** need maintainer action outside the build (signing,
  hardware, distribution, recording).
- **3** are real engineering with a known path (extension
  timeline chips / investigation graph / onboarding overlay).

The 3 engineering items are not blocking the alpha hand-off —
they're polish that fires after the cohort starts returning
feedback in [`alpha_report.md`](../../alpha/alpha_report.md).

> Cross-referenced by [`FRICTION_FIXED.md`](FRICTION_FIXED.md)
> (the fixed-side ledger),
> [`PHASE_TRACKER.md`](../founder/PHASE_TRACKER.md) (blocked-items
> table), and
> [`ROADMAP_LIVE.md`](../founder/ROADMAP_LIVE.md) (the *Next* +
> *Later* columns).
