# READINESS_SCORE.md — the 0-100 verdict

A single number the founder can glance at, computed deterministically
from the same data the dashboard reads. Internal only. **Not a
marketing metric.** A higher score does not mean the product is
better; it means the *release* of it is more ready.

The engine lives at
[`app/core/release_readiness.py`](../../app/core/release_readiness.py).
The CLI surface is `recall founder release`.

---

## The six inputs, weighted

Total = 100 by construction.

| Input | Weight | What scores it | 0 score | Full score |
|---|---|---|---|---|
| **Installer** | 25 | `release.installer` + `release.signing` | blocked + unsigned | ready + signed |
| **Trust** | 20 | proportion of green / yellow / red trust cards | all red | all green, zero bad-recovery flags |
| **Alpha** | 20 | active-cohort device count + return % | no devices | ≥ 20 devices and ≥ 50% returning |
| **Release** | 15 | `release.go_no_go` minus a 5 % penalty per blocker (cap 30 %) | NO-GO with many blockers | GO with zero blockers |
| **Docs** | 10 | baked surfaces filled, minus 5 % per confusion-tagged feedback | empty surfaces | populated + no confusion entries |
| **Screenshots** | 10 | `release.screenshots` | missing | complete |

Each dimension returns a 0..1 score. The total is the weighted sum,
rounded to an integer, in `[0, 100]`.

## The three bands

| Band | Score | Meaning |
|---|---|---|
| **GREEN** | ≥ 80 | Ready to tag the next milestone. |
| **YELLOW** | 50–79 | Path is clear; named blockers remain. |
| **RED** | < 50 | Not yet shippable. Start with the named blockers. |

The headline string in `recall founder status` / `recall founder release`
is one of those three lines, verbatim.

## What the score is *not*

- **Not a probability of success.** It is a sum over six readiness
  dimensions, not a prediction.
- **Not a public metric.** It never enters
  `recall stats --export`. The
  [`../engineering/TRUST_LEDGER.md`](../engineering/TRUST_LEDGER.md)
  boundary holds — the score lives on the founder's machine.
- **Not a productivity score.** No user is graded by it; it grades
  the *release*.
- **Not a substitute for [`GO_NO_GO.md`](../release/GO_NO_GO.md).**
  Gate-7's authority is `GO_NO_GO.md`; the readiness score is its
  decimal-resolution companion, helpful between gate flips.

## How to move the score

The honest answer to *"the score is RED, how do I make it GREEN"*
is the directive of [`GO_NO_GO.md`](../release/GO_NO_GO.md):

1. ~~Build a real `Recall-Setup.exe`~~ — **done Phase 5F.**
   `release.installer` flipped from `blocked` to `ready`.
   *Installer* dimension to 100% (~25 points; the EV-cert bonus
   never materialises in this engine — it's a documentation
   gain, not a score gain).
2. ~~Capture the remaining screenshots~~ — **done Phase 5G.**
   Control-room + doctor + installer-flow captures landed.
   `release.screenshots` flipped from `partial` to `complete`.
   *Screenshots* dimension to 100% (~10 points).
3. **Three fresh-VM walks in
   [`../trust/CLEAN_MACHINE_RUN.md`](../trust/CLEAN_MACHINE_RUN.md).**
   The directive's floor for gate 1 is *3 successful installs*.
   Each successful walk removes a row from `release.blocked`,
   recovering ~3-5 *Release* points; the gate-1 flip itself is
   the gate to flipping `release.go_no_go: NO-GO → GO`, which
   recovers ~15 points.
4. **Enrol cohort `alpha-001`** (lifts *Alpha* once devices show
   up + return data lands). The [`alpha/`](../../alpha) packet
   is what they receive. Returns also feed
   [`alpha_report.md`](../../alpha/alpha_report.md)'s Q1-5.
5. **Code-sign the installer.** Closes SmartScreen-warning
   friction; not a score lever but a trust lever.
6. **Run a real macOS build** per
   [`MAC_OWNER_NEEDED.md`](../release/MAC_OWNER_NEEDED.md).
   `release.mac` flips from `preview` to `working`; bonus
   logical-correctness for the *Installer* dimension's narrative.

Phase 5G moved the score from **56/100 YELLOW → 61/100 YELLOW**
(Screenshots dimension closed). 80+ is achievable when steps 3 +
4 complete — no engine changes required.

## How it is computed (the audit trail)

Inputs:
- `apps/admin/data/release.json` — installer, signing, mac,
  screenshots, go_no_go, blocked.
- `apps/admin/data/trust.json` — six trust cards with state.
- `apps/admin/data/cohorts.json` — devices + returning per cohort.
- `apps/admin/data/health.json` — surface fill.
- `apps/admin/data/feedback.json` — feedback rows tagged by
  category.

Each dimension's function reads exactly one or two of these files
and returns a `(score, detail)` tuple. The detail strings are what
`recall founder release` prints under each row — they are the
audit trail.

A failing dimension is therefore *citable*. *"Installer was 0%
because `installer=blocked, signing=unsigned`"* is a more useful
status line than *"the score went down"* — and that is the
distinction this file is for.
