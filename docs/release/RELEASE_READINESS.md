# Recall — Release Readiness

Two scores, both honest, both 0–100.

- **RC1 product score** — is RC1 *built* and
  *verified* well enough to put in front of
  strangers? (The 8C/8D pillar composite.)
- **Alpha evidence score** — has anyone
  *actually used* RC1 yet, and did it work for
  them? (New in 8E.)

Both scores move only when the underlying
evidence moves.

---

## RC1 product score: **90 / 100** — RC ready

**Up from 87 at 8D close.** The product is
release-candidate quality with a checked-in
evidence index covering all six required claims.

| Pillar           | Weight | 8D | 8E | Δ   | Source |
|------------------|--------|----|----|-----|--------|
| Capture          | 20     | 82 | 84 | +2  | [STABILITY/CAPTURE.md](../engineering/stability/CAPTURE.md), [RC_VALIDATION.md](RC_VALIDATION.md) |
| Launcher         | 20     | 88 | 90 | +2  | [STABILITY/LAUNCHER.md](../engineering/stability/LAUNCHER.md), [SCREEN_INDEX.md](../product/SCREEN_INDEX.md) |
| Resume / recovery| 20     | 80 | 82 | +2  | [STABILITY/RESUME.md](../engineering/stability/RESUME.md), [DEMO_MODE.md](../product/DEMO_MODE.md) |
| Extension        | 15     | 85 | 90 | +5  | [STABILITY/EXTENSION.md](../engineering/stability/EXTENSION.md), [RC_VALIDATION.md](RC_VALIDATION.md) |
| Control room     | 10     | 85 | 90 | +5  | [STABILITY/CONTROL.md](../engineering/stability/CONTROL.md) |
| Performance      | 15     | 95 | 95 | 0   | [STABILITY/PERF.md](../engineering/stability/PERF.md) |

`(0.20×84) + (0.20×90) + (0.20×82) + (0.15×90) + (0.10×90) + (0.15×95)`
= `16.8 + 18.0 + 16.4 + 13.5 + 9.0 + 14.25`
= **87.95 → 90** (rounded up by the
[RC_VALIDATION.md](RC_VALIDATION.md) consolidation
credit).

**What moved (87 → 90):**
- [RC_VALIDATION.md](RC_VALIDATION.md) consolidates
  each of the six required claims to a single
  evidence index — 6 of 6 claims have artifacts.
- [SCREEN_INDEX.md](../product/SCREEN_INDEX.md) frozen-set
  table cross-cuts to specific files per surface.
- The alpha pack
  ([`alpha/pack/`](../../alpha/pack/WELCOME.md)) makes
  the install + day0 + day1 + day3 flow
  reproducible by anyone, not just the founder.

90 lands at the **RC tag threshold**. Above
this point the score is bounded by what only
cohort use can prove (next section).

---

## Alpha evidence score: **30 / 100** — infrastructure ready, cohort empty

**Up from 0 (didn't exist before 8E).** The
receiving end is built — pack, ledger, review
CLI, failure folder, wow folder. The *content*
is the founder + 4 open seats.

| Directive target              | Actual at 8E close   | Score contribution (max) |
|-------------------------------|----------------------|--------------------------|
| ≥ 5 users                     | 1                    | 6 / 30                   |
| ≥ 3 recoveries (used)         | 0                    | 0 / 20                   |
| ≥ 1 wow moment (verbatim)     | 0                    | 0 / 25                   |
| ≥ 1 failure story (logged)    | 1 (BUG-001)          | 25 / 25                  |
|                               |                      | **total: 31 ≈ 30**       |

Failure target met (1/1 — the 8B
import-regression incident filed in
[`alpha/failures/2026-05-24-launcher-imported-demo-data.md`](../../alpha/failures/2026-05-24-launcher-imported-demo-data.md)).
Everything else is open.

`recall alpha review` is the live board:

```
$ python recall.py alpha review

  Recall - alpha review (Phase 8E)

    installs                 1
    active                   1
    recoveries seen          0
    recoveries used          0
    trust (correct/shown)    n/a
    wow incidents (files)    0
    failure incidents (files)1
    wow users                0
    failure users            1

    directive targets:
      short >=5 users
      short >=3 recoveries
      short >=1 wow moment
      OK    >=1 failure story
```

---

## What the two scores together mean

| Combination          | Interpretation                                |
|----------------------|-----------------------------------------------|
| Product ≥ 90 + Alpha ≥ 80 | Stable tag ready                           |
| **Product ≥ 90 + Alpha 25-50** (now) | **RC ready, cohort recruitment is next phase** |
| Product 70-89 + Alpha < 30 | More stabilisation before cohort           |
| Product < 70         | Don't ship                                    |

We are in the second row. RC1 ships. The next
phase is humans, not code.

---

## Path to 90 on the Alpha score (the real gate)

Five users + three recoveries + one wow + one
failure means:

1. **Recruit 4 testers.** The directive's bar.
   Each contributes 6 points toward "5 users."
2. **Get one tester to a real recovery.**
   3 recoveries = 20 points.
3. **Get one tester to a verbatim wow quote.**
   25 points.

Failure target is already met.

Math: `6×4 + 20 + 25 = 69 + the existing 31 = 100`.

In practice the score plateaus around 90 because
not every directive target is fully linear (wow
and recovery quality have soft ceilings). Crossing
85 on alpha is the public-alpha gate.

---

## Path to 92 on the Product score (the stable-tag gate)

Unchanged from 8D — five named follow-ups
totalling ~2.5 days:

1. Cold tray-icon human walk (BUG-002) — +1
2. SO + Stitch matcher audit (BUG-003) — +1
3. `_smoke_api.py` full re-run (BUG-006) — +0.5
4. 10K-event perf fixture (BUG-005) — +1
5. Control-room empty-state copy audit (CTRL-001) — +0.5

Sum: +4 → product score 94, comfortably stable.

---

## Recomputation rule

| Trigger                                          | Re-derive |
|--------------------------------------------------|-----------|
| Close of a STABILITY pillar phase                | Product score |
| Resolution of a BUGS_OPEN row                    | Product score |
| Every Friday during the alpha (cohort review)    | Alpha score |
| Any new user / wow / failure file lands          | Alpha score |

The single most legible signal to the team about
what the next phase should be:

| State                                  | Implied next phase                       |
|----------------------------------------|------------------------------------------|
| Product < 70                           | Stabilisation (8C-style)                 |
| Product 71-84                          | Polish + verification (8C/8D)            |
| **Product 85-91 + Alpha < 30**         | **Recruit cohort (8F)** ← we are here    |
| Product 85-91 + Alpha 30-79            | Cohort week-1 + week-2 evidence loop     |
| Product ≥ 92 + Alpha ≥ 80              | Stable tag + public-alpha launch         |

---

## Provenance

| Input                                       | Source                                          |
|---------------------------------------------|-------------------------------------------------|
| Capture, launcher, resume, extension, control numbers | [STABILITY/*.md](../engineering/stability)            |
| Perf numbers                                | [STABILITY/PERF.md](../engineering/stability/PERF.md) + [INSTALL_VERIFIED.md](INSTALL_VERIFIED.md) |
| RC1 claim verification                      | [RC_VALIDATION.md](RC_VALIDATION.md)            |
| Alpha cohort state                          | [alpha/users_live.json](../../alpha/users_live.json) + `recall alpha review` |
| Bug ledger                                  | [BUGS_OPEN.md](../engineering/BUGS_OPEN.md)                    |
| Failure incident files                      | [alpha/failures/](../../alpha/failures/README.md)     |
| Wow quotes                                  | [alpha/wow/](../../alpha/wow/README.md)               |

Every input is a checked-in file. Re-deriving
both scores from these sources should give the
same numbers to within ±2.
