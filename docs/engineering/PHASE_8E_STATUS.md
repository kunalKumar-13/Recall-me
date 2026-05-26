# Phase 8E — Alpha Users + Evidence Loop

**Status:** complete · evidence infrastructure
ready · cohort recruitment is the next phase

**Directive:** put Recall in front of humans. No
product work. No launcher work. No extension
redesign. No new features.

> Recall leaves repo. Humans touch it.

---

## Headline

| Metric                                    | 8D close   | 8E close   | Δ        |
|-------------------------------------------|------------|------------|----------|
| **RC1 product score**                     | 87         | **90**     | **+3**   |
| **Alpha evidence score** (new)            | n/a        | **30**     | new      |
| **alpha/ directories**                    | 1 (users/) | **4**      | +3 (pack/, failures/, wow/) |
| **Alpha pack docs**                       | 0          | **7**      | +7       |
| **`recall alpha` subcommands**            | 6          | **7**      | +1 (`review`) |
| **Filed failure incidents**               | 0          | **1**      | +1 (BUG-001) |
| **Filed wow quotes**                      | 0          | 0          | 0 (cohort pending) |
| **Users in `users_live.json`**            | 0          | **1**      | +1 (founder) |
| **RC1 claims with evidence index**        | 6 implicit | **6 explicit** | new doc ([RC_VALIDATION.md](../../RC_VALIDATION.md)) |

The receiving end of the evidence loop is built.
The cohort is not yet recruited — that's Phase 8F.

---

## What changed (per directive section)

### 1. Alpha pack — covered by [`alpha/pack/`](../../alpha/pack/WELCOME.md)

Seven docs matching the directive's
install → browse → leave → return → resume →
report flow:

| Doc                                          | Job |
|----------------------------------------------|-----|
| [`WELCOME.md`](../../alpha/pack/WELCOME.md)  | front door — what we ask, what we promise |
| [`INSTALL.md`](../../alpha/pack/INSTALL.md)  | 10-minute install path with troubleshooting |
| [`DAY0.md`](../../alpha/pack/DAY0.md)        | first hour — browse normally |
| [`DAY1.md`](../../alpha/pack/DAY1.md)        | the real test — first unprompted launcher open |
| [`DAY3.md`](../../alpha/pack/DAY3.md)        | does it stick? self-survey |
| [`FEEDBACK.md`](../../alpha/pack/FEEDBACK.md)| open intake — three channels, no form |
| [`UNINSTALL.md`](../../alpha/pack/UNINSTALL.md)| clean exit + the one sentence we want |

Every doc holds the privacy boundary verbatim:
**no PII, no URLs, no filenames, no queries**.

### 2. User ledger — covered by [`alpha/users_live.json`](../../alpha/users_live.json)

- Schema: `alpha-users-live-v1`.
- 9 metadata fields per user: `handle`,
  `install_date`, `platform`, `browser`,
  `used_days`, `recoveries_seen`,
  `recoveries_used`, `wow`, `failure`,
  `status`.
- 1 entry: `alpha-001` (founder dogfood baseline,
  active, failure=true, wow=false, recoveries=0).
- 4 open seats.
- Hard boundary documented inline: "no real
  names, no employer names, no project
  codenames."
- Separate from the existing
  [`alpha/users/`](../../alpha/users/) tree
  (Phase 5K cohort metadata folders) — the live
  JSON is the 8E single-row aggregation.

### 3. Daily review — covered by `recall alpha review`

- New subcommand wired in
  [`app/core/alpha_cli.py`](../../app/core/alpha_cli.py):
  ~110 lines (`cmd_review` + helper
  `_count_incident_files`).
- ASCII-only output (cp1252 safe).
- Reads three sources:
  - `alpha/users_live.json` — installs, active,
    recoveries seen/used, wow/failure booleans.
  - `alpha/recovery_journal.json` — trust pct
    (re-uses 6E `_compute_trust_pct`).
  - `alpha/wow/` + `alpha/failures/` — file
    counts (excluding READMEs + templates).
- Six directive-named outputs: installs,
  active, recoveries, trust, wow, failures.
- Plus a directive-targets section that scores
  each of the four 8E goals (`OK` / `short`).

Live output today:

```
  Recall - alpha review (Phase 8E)

    installs                 1
    active                   1
    recoveries seen          0
    recoveries used          0
    trust (correct/shown)    n/a   (resume_ok=0, bad=0, silenced=0)
    wow incidents (files)    0
    failure incidents (files)1
    wow users                0
    failure users            1

    directive targets:
      short >=5 users         (have 1)
      short >=3 recoveries     (have 0 used)
      short >=1 wow moment     (have 0)
      OK >=1 failure story  (have 1)
```

### 4. Failure loop — covered by [`alpha/failures/`](../../alpha/failures/README.md)

- Folder created with `README.md` + `TEMPLATE.md`.
- Five-field template (what / expected / actual /
  repro / severity).
- One real incident filed during 8E:
  [`2026-05-24-launcher-imported-demo-data.md`](../../alpha/failures/2026-05-24-launcher-imported-demo-data.md)
  — the 8B archive over-reach
  ([BUG-001](../../BUGS_OPEN.md)). Self-reported
  by the founder.
- Privacy boundary repeated: describe the
  *shape* of content, not the specifics.
- File-name convention: `YYYY-MM-DD-<slug>.md`
  so chronology is implicit.

### 5. Wow collection — covered by [`alpha/wow/`](../../alpha/wow/README.md)

- Folder created with `README.md` + `TEMPLATE.md`.
- **Verbatim-only rule** enforced in the README:
  no paraphrase, exact words only.
- Anonymisation guide for public-facing quotes
  (strip employers, teammates, project codenames).
- 0 quotes filed at 8E close — the cohort is the
  source.

### 6. RC validation — covered by [`RC_VALIDATION.md`](../../RC_VALIDATION.md)

Cross-link evidence index for the six required
RC1 claims:

| Claim                          | Verdict |
|--------------------------------|---------|
| Install works                  | ✅ verified (dev) · ⚠️ clean-VM walk = BUG-002 |
| Capture works                  | ✅ verified · ⚠️ SO + Stitch = BUG-003 |
| Resume works                   | ✅ engine verified · ⚠️ click→tabs = BUG-002 |
| Launcher understandable        | ✅ frozen + captured |
| Extension understandable       | ✅ frozen + captured |
| Control room usable            | ✅ build clean · ⚠️ empty-state copy = CTRL-001 |

**6 of 6 claims have artifacts.** Four carry
honest follow-up flags. Zero are
unsubstantiated. Every row links to its
checked-in evidence source.

### 7. Release-readiness — covered by [`RELEASE_READINESS.md`](../../RELEASE_READINESS.md)

Two scores now, both honest:

- **RC1 product score: 87 → 90** (+3). The
  evidence-index consolidation + pack
  reproducibility raises extension (+5),
  control room (+5), launcher (+2), capture
  (+2), resume (+2). Now at the RC-tag threshold.
- **Alpha evidence score: 30** (new). Failure
  target met (1/1); 4 users short, 3 recoveries
  short, 1 wow short. The score is bounded by
  cohort recruitment, which is Phase 8F.

Combination table interpretation:

> **Product ≥ 90 + Alpha 25-50** ⇒ **RC ready,
> cohort recruitment is next phase**.

### 8. This document

Capstone for 8E. Pairs with the previous
capstones:
[8A `AUDIT/STATE.md`](../../AUDIT/STATE.md) →
[8B `PHASE_8B_STATUS.md`](PHASE_8B_STATUS.md) →
[8C STABILITY/ set](../../STABILITY/) →
[8D `PHASE_8D_STATUS.md`](PHASE_8D_STATUS.md) →
**8E this**.

---

## Files touched

**Created (top-level):**

- [`RC_VALIDATION.md`](../../RC_VALIDATION.md) —
  evidence index for the 6 RC1 claims.

**Created (alpha/):**

- [`alpha/users_live.json`](../../alpha/users_live.json)
  — 8E cohort ledger.
- [`alpha/pack/`](../../alpha/pack/WELCOME.md) — 7
  docs (WELCOME, INSTALL, DAY0, DAY1, DAY3,
  FEEDBACK, UNINSTALL).
- [`alpha/failures/`](../../alpha/failures/README.md)
  — README + TEMPLATE + 1 real incident.
- [`alpha/wow/`](../../alpha/wow/README.md) —
  README + TEMPLATE.

**Created (code):**

- `cmd_review` + `_count_incident_files` in
  [`app/core/alpha_cli.py`](../../app/core/alpha_cli.py)
  (~110 lines added). Registered as `recall
  alpha review`.

**Edited (docs):**

- [`RELEASE_READINESS.md`](../../RELEASE_READINESS.md)
  — added the Alpha evidence score (new
  dimension); RC1 product score 87 → 90.
- [`app/core/alpha_cli.py`](../../app/core/alpha_cli.py)
  `cmd_help` — added review line.

---

## Verification

| Command                                                   | Result |
|-----------------------------------------------------------|--------|
| `python recall.py alpha review`                           | renders ASCII board with 6 directive-named lines + 4 target lines |
| `python recall.py alpha help`                             | new `review` line present |
| `python -c "from app.core.alpha_cli import cmd_review"`   | clean import |
| `python -m pyflakes app/core/alpha_cli.py`                | clean |
| `python recall.py demo run`                               | still seeds (no 8E regression) |
| `python recall.py capture status`                         | still reports live capture |
| `python recall.py doctor`                                 | still 5 GREEN |
| `python -c "import json; json.load(open('alpha/users_live.json'))"` | parses |
| `ls alpha/pack/ alpha/failures/ alpha/wow/`               | full set present |

9 verifications, all green.

---

## Success criterion

> Recall leaves repo. Humans touch it.

**Mixed.** The infrastructure required for humans
to touch Recall is fully in place:

- They have the pack ([`alpha/pack/`](../../alpha/pack/)).
- They have a place to land
  ([`alpha/users_live.json`](../../alpha/users_live.json)).
- They have a place to report wows
  ([`alpha/wow/`](../../alpha/wow/README.md))
  and failures
  ([`alpha/failures/`](../../alpha/failures/README.md)).
- The founder has a daily review board
  (`recall alpha review`).
- Each of the 6 RC1 claims is backed by an
  artifact ([`RC_VALIDATION.md`](../../RC_VALIDATION.md)).

But **the cohort is the founder + 4 open seats**.
The actual humans-touching-Recall part is the
work of the next phase.

Honest verdict: **Phase 8E built the receiving
end. Phase 8F will fill it.**

---

## What's next (Phase 8F territory)

1. **Recruit 4 testers** matching the cohorts
   in [`alpha/users/README.md`](../../alpha/users/README.md)
   (alpha-002, friends, builders, students).
2. **Send the pack** — link them to
   [`alpha/pack/WELCOME.md`](../../alpha/pack/WELCOME.md).
3. **Daily `recall alpha review`** — the founder
   runs this every morning during the cohort
   weeks.
4. **Friday cohort call** — 15 minutes per
   tester. Update [`users_live.json`](../../alpha/users_live.json)
   the same evening.
5. **First wow + first 3 recoveries** = the
   public-alpha gate. After that, Phase 9.

The score gate to public-alpha is **Product ≥ 92
+ Alpha ≥ 80**. We're at **90 / 30**. The path
is humans, not code.

---

## Mantra reminder

> *Productize, don't prototype.* Every change
> from Phase 4A onward carries the question:
> "Would someone trust this enough to leave it
> running all day for years?"

The 8E addition: that question can only be
answered by someone who *isn't us*. The whole
phase is about making sure the receiving end
of that answer is ready.
