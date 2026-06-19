# PHASE_6A_STATUS.md — First Magic

The receipt for Phase 6A. The directive's *Goal*: a stranger
installs Recall, and inside 30 seconds, says *"oh wait — it
remembers unfinished work."* The success line is a tester's
quote (*"wait it remembered that?"*); this phase is the
infrastructure that *invites* the quote.

The directive listed seven surfaces (Launcher / Recovery card /
Extension polish / First run / Empty state / Verify / Status).
Several of them — particularly the full **launcher theme swap**
to warm white + lavender + glass — are a major QSS rewrite with
high regression risk against the existing dark-theme screenshots.
This phase scoped down to the **high-impact, low-risk** subset
and named the heavier work in the *Deferred* list.

Cross-references: [`PHASE_5K_STATUS.md`](PHASE_5K_STATUS.md)
(the cohort infrastructure this phase polishes for),
[`OPEN_PROBLEMS.md`](../../docs/engineering/OPEN_PROBLEMS.md) (the still-open list,
extended with this phase's deferreds).

---

## What shipped

### Recovery card — confidence pill

`RecoveryCard` ([`app/ui/cards.py`](../../app/ui/cards.py)) grew
an inline **confidence badge** in the meta column above the
Resume affordance. Three bands:

| Level | Color | Reads as |
|---|---|---|
| **high** | ACCENT lavender (`#8b9bff`) | *act on this* |
| **medium** | _WARN amber (`#d6a06a`) | *plausible — your call* |
| **low** | TEXT_DIMMER grey (`#5a6072`) | *hint, not a recommendation* |

A *low* card keeps the calmer `_StateDot` ("Resume" label) instead
of the full `_ResumePill`. A *low* CTA on a hedged surface would
over-promise; the directive's *No bounce* / *Only experience*
discipline names this trade-off.

`RECOVERY_HEIGHT` bumped 64 → **76** to fit the new badge between
the time label and the Resume row. Still inside the launcher's
calm row band; the digest does not need to scroll.

`derive_recovery_confidence(n_targets)` is the UI-side mapping
the launcher uses (≥ 4 targets → high, 2-3 → medium, ≤ 1 → low).
**Pure display logic — no engine-side trust field.** Per the
directive's *No engine work* rule.

### Launcher — softer empty state

`EmptyCard.empty()` copy refreshed:

```
before:                                  after:
"Recall is ready."                       "Recall fills itself."
"Work a little, then come back later — "Work a little.  Come back later.
the investigations you can step back     What you can step back into will
into will appear here."                  appear here."
```

The previous copy read as *instructions*; the new copy reads as
*trust* — three short clauses, no semicolon parade, the user
isn't being told what to do. Three-line target met
(directive's "Work a little / Come back later / Recall fills
itself"), reordered slightly so the first line is the promise.

### Extension — collapsible Connection drawer

The Phase 5K *Connection* drawer in
[`SettingsPanel.tsx`](../../apps/extension/ui/src/components/SettingsPanel.tsx)
is now **collapsible**:

- **Header row** stays always-visible: breathing dot + status
  line + ingested/today counts + a `›` chevron that rotates
  90° when expanded.
- **Body** (the *Re-probe* / *Open Recall* buttons) is
  `<AnimatePresence>`-wrapped — height + opacity animate from
  0 → auto on expand, and back on collapse. Same `calmFast`
  transition (180 ms) as the rest of the popup's state motion.
- **Default state**: expanded when the daemon is *off*
  (the drawer is informational then), collapsed when the daemon
  is healthy (one calm row by default, click to expand).
- A11y: `aria-expanded` + `aria-label` on the header button.

### Extension — timeline labels on MemoryList

Each row of the *Searches / Tabs / Chats* groups in
[`MemoryList.tsx`](../../apps/extension/ui/src/components/MemoryList.tsx)
now carries a small mono-font age label on the right:
*"just now"* / *"3m"* / *"2h"* / *"yesterday"* / *"3d"* / *"2w"*.

The label is computed in `_timeAgo(ts)` from the event's own
`ts` (epoch seconds) — **real API data**, not invented. The
field was added to `MemoryItem` in `lib/types.ts` and read in
`lib/api.ts`'s `fetchMemory()`; events without a `ts` (a
defensive default) render no label rather than a fake one.

Capture mocks updated with synthetic `ts` values so the
deterministic extension screenshots render the labels.

---

## What did **not** ship (and why)

| Directive item | Status | Why |
|---|---|---|
| Full launcher theme swap (warm white + lavender + glass + blur + depth) | deferred | A 200+ LOC QSS rewrite against the existing dark theme. High regression risk against the 15 deterministic screenshots; needs a dedicated visual-QA pass. Best done as its own phase with a real desktop session, not interleaved with smoke-only verification. |
| Section rename to *Continue / Investigations / Recent returns / Trust* | partial | The launcher's section labels are driven by `digest_labels()` in [`launcher_digest.py`](../../app/ui/launcher_digest.py) which currently reads (*Continue where you left off* / *Continue today* / *You paused here*) + (*Active investigations* / *Still active*). The *Recent returns* and *Trust* section labels are not yet wired; renaming them touches `docs/product/CONTINUITY_LANGUAGE.md` which is the canonical vocabulary doc. Deferred to a focused continuity-language pass. |
| First-run demo story (*"Show example"* CTA with WebSocket / proposal / research stories) | deferred | A new launcher screen + a *demo-mode* dispatch path. The directive said *No fake memory; demo only*. The existing `app/core/demo_seed.py` produces a deterministic event log; wiring it into a first-run *Show example* button is a real new UI surface (~120 LOC). |
| Recovery card *resume strength* / *time gap* / *work count* / *preview chips* split | partial | The *confidence pill* shipped; the *preview chips* (small badges like `[2 tabs] [3 files]`) still come through as evidence-line text. Splitting evidence into separate chip widgets needs the launcher's `_middle` helper to accept a `chips: list[str]` parameter — possible but not in scope this phase. |
| Extension *activity strip* (separate from MemoryList; *Today / search / chat / tab / resume* with timeline chips like `09:20 Search · 09:31 Chat · 09:42 Return`) | deferred | The MemoryList timeline labels delivered the *real-data ts* half. A separate top-of-popup strip with kind-grouped chips would duplicate; the existing MemoryList groups are *Searches / Tabs / Chats* + the new timeline labels. |
| Repair drawer's *doctor summary* | deferred | The drawer shows daemon-side health + Re-probe + Open Recall. A full doctor summary (the 10-row doctor output rendered inline) would either fork the doctor module or call out to it; both bigger than the directive's *only experience* discipline. |
| Launcher *soft glass / floating surface / blur / depth* | deferred | Same dependency as the theme swap; Qt's `QGraphicsBlurEffect` is OS-dependent and would push the regression risk into platform-specific territory. |

The directive named *Only experience* + *NO engine work* + *NO new docs* + *NO founder systems* — every deferred item respects those constraints (each is real UX work; they were deferred for **scope risk**, not for charter rule).

---

## Verification

| Surface | Command | Result |
|---|---|---|
| pyflakes | `python -m pyflakes app/ui app/core api` | zero findings |
| launcher import | `python -c "from app.ui.launcher import Launcher; from app.ui.cards import RecoveryCard, derive_recovery_confidence"` | OK; `RECOVERY_HEIGHT=76`; `conf(4)=high / conf(2)=medium / conf(0)=low` |
| launcher screenshots | `python infra/scripts/capture/capture_launcher.py` + `capture_recovery.py` | 7 PNGs regenerated cleanly (5 launcher + 2 recovery) |
| extension build | `cd apps/extension/ui && npm run build` | **287.94 kB JS / 91.88 kB gzipped** (+1.1 kB from the drawer collapse + timeline labels) |
| TS scan | `npx tsc --noEmit` | zero findings |
| extension screenshots | `node apps/extension/ui/capture_extension.mjs` | 7 PNGs regenerated (`-empty` / `-capturing` / `-connected` / `-missing` / `-disconnected` / `-offline` / `-loading`) |
| doctor | `python recall.py doctor` | 5 GREEN / 4 YELLOW / 0 RED |
| founder status | `python recall.py founder status` | Readiness 61/100 YELLOW (unchanged) |
| alpha CLI | `python recall.py alpha report` | "No testers recorded yet" (0 entries — correct) |
| control room build | `cd apps/admin/web && npm run build` | 4 static pages, 87.4 kB first-load |

---

## Touched files

```
modified code:
  app/ui/cards.py                                      (_ConfidenceBadge + _meta_with_confidence + RecoveryCard `confidence` param + RECOVERY_HEIGHT 64→76 + EmptyCard.empty copy)
  app/ui/launcher.py                                   (import derive_recovery_confidence + pass confidence at the RecoveryCard call site)
  apps/extension/ui/src/components/SettingsPanel.tsx   (Connection drawer made collapsible)
  apps/extension/ui/src/components/MemoryList.tsx      (_timeAgo helper + per-row mono "ago" label)
  apps/extension/ui/src/lib/api.ts                     (fetchMemory reads `ts` field)
  apps/extension/ui/src/lib/types.ts                   (MemoryItem.ts? added)
  apps/extension/ui/capture_extension.mjs              (MOCK + MOCK_CAPTURING events grew `ts`)
  infra/scripts/capture/capture_launcher.py            (RecoveryCard arg high_trust→confidence)
  infra/scripts/capture/capture_recovery.py            (RecoveryCard arg high_trust→confidence)

new docs:
  docs/engineering/PHASE_6A_STATUS.md                  (this file)

modified docs:
  docs/founder/PHASE_TRACKER.md
  docs/founder/ROADMAP_LIVE.md
  docs/release/CHANGELOG.md
  docs/DOC_INDEX.md
```

No new engine modules. No new memory layers. No new founder
systems. The directive's three anti-rules held.

---

## The 30-second test

The directive's question: *Within 30 seconds of install, the
stranger understands "oh wait — it remembers unfinished work."*

Of the *first-30-seconds* surfaces — install → first-launch
screen → folder picker → empty digest — this phase improved
**one** (the empty digest's copy now reads as *trust*, not
*instructions*). The bigger 30-second wins (the *Show example*
demo story; the warm-white launcher) are deferred.

The 30-second test stays *not yet measured* — same as the *5
humans, 3 recoveries* line from Phase 5K. Closed by the same
external dependency: a real stranger receiving the alpha
packet, double-clicking, and reporting whether the 30 seconds
landed.
