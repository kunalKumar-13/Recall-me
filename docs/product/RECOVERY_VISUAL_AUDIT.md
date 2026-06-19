# RECOVERY_VISUAL_AUDIT.md — what each recovery state looks like

Phase 6N's directive-required audit. Five sections — *high
trust · medium trust · weak trust · silence · bad recovery* —
documenting the visual contract for every state the launcher
ships against.

Pairs with [`PHASE_6N_STATUS.md`](../../archive/phase-status/PHASE_6N_STATUS.md)
(the engineering receipt) and
[`docs/product/DAILY_LOOP.md`](DAILY_LOOP.md) (the
`continuity_restored` / `resume_quality` thresholds the
trust-band statistics derive from).

---

## High trust

> *the engine thinks the user is mid-flow on a multi-surface
> investigation; the launcher offers a strong call to action.*

| Surface | Treatment |
|---|---|
| Hero fill | accent-soft (`T.ACCENT_SOFT = #EDE9FB`) — strongest invitation |
| Hero border | accent line at α = 80 |
| CTA pill | accent-filled (`T.ACCENT = #8B7FE3`), white text, `Resume` verb, `1` shortcut chip |
| Confidence badge | accent on accent-soft — `HIGH` |
| Confidence sentence | *"Recall thinks this was interrupted work"* |
| Chip strip | up to **3 real evidence items** (e.g. *2 tabs · 3 files · 2d gap*); never fabricated |
| Investigation strip | sorted with HIGH-signal threads first |

Reference: [`launcher-recovery/high.png`](../../assets/screenshots/launcher-recovery/high.png).

## Medium trust

> *the engine sees a partial investigation — a return that's
> not strong enough to be a hero, but real enough to invite
> action.*

| Surface | Treatment |
|---|---|
| Hero fill | warm cream (`QColor(245, 242, 252)`) — halfway between accent-soft and white |
| Hero border | accent line at α = 48 (quieter than HIGH) |
| CTA pill | accent-soft fill + 1-px accent border, accent ink text, `Continue` verb |
| Confidence badge | warm amber on warn-soft — `MED` |
| Confidence sentence | *"Seen again after return"* |
| Chip strip | same 3-item cap; evidence is whatever the parser produced |
| Investigation strip | medium-strength threads slot into rank 1 (*returned*) when the last-touch carries a `return` marker |

Reference: [`launcher-recovery/medium.png`](../../assets/screenshots/launcher-recovery/medium.png).

## Weak trust

> *the engine isn't sure — it found a thread but the signal
> count is below the medium floor. The launcher offers
> "Review" rather than "Resume" so the user reads first.*

| Surface | Treatment |
|---|---|
| Hero fill | plain raised white (`T.BG_RAISED = #FFFFFF`) — no tint |
| Hero border | hairline at α = 24 — the same border the investigation pills wear |
| CTA pill | **ghost** — transparent fill, hairline border, ink-2 text, `Review` verb |
| Confidence badge | ink-3 on warm grey — `LOW` |
| Confidence sentence | *"Weak signal — review first"* |
| Chip strip | often a single chip (e.g. *1 tab*) — same parser; no fabrication |
| Investigation strip | LOW-signal threads land in rank 2 (*recent*) when their last-touch is fresh, otherwise rank 3 (*passive*) |

Reference: [`launcher-recovery/low.png`](../../assets/screenshots/launcher-recovery/low.png).

## Silence

> *the engine has nothing to surface — no recoveries, no
> investigations, no real activity. The launcher must read as
> calm, not as broken.*

| Surface | Treatment |
|---|---|
| Surface choice | `MinimalEmpty` (vertically centred icon + headline + sub + preview + buttons + trust line) |
| Headline | *Recall notices unfinished work.* (FS_HERO = 20) |
| Sub | *Work normally. Return later. Recall fills itself.* (FS_BODY = 13) |
| **Preview card** | a LOW-state `RecoveryCardV3` with the canonical fixture (WebSocket retry debugging · 2 tabs · 2 files · 2d gap), captioned **PREVIEW** above and *A real recovery will replace this* in the sentence row |
| CTAs | *Show example* (accent-soft pill) + *Start normally* (ghost pill) |
| Trust line | `local only · 127.0.0.1:4545 · no cloud` |
| Auto-dismiss | the preview disappears the moment the launcher swaps from `MinimalEmpty` to `MinimalDigest` — i.e. the instant a real recovery exists |

Reference: [`launcher-recovery/empty.png`](../../assets/screenshots/launcher-recovery/empty.png).

The directive's *"dismiss immediately when real events arrive"*
rule is enforced by the launcher's state machine, not by the
preview widget itself: `MinimalEmpty` is only rendered when
the engine has zero recoveries. The first real ingest flips
the state to populated; the preview is gone before the next
paint frame.

## Bad recovery

> *the user clicked Resume but the reopened work was wrong.
> The launcher itself doesn't render a "bad" state in-line —
> it lives in the cohort ledger.*

| Surface | Treatment |
|---|---|
| Launcher | unchanged on the moment of mis-recovery — the user just hits Esc and continues. **No alarm, no animation, no warning.** A "wrong" recovery never becomes a louder UI surface than a right one. |
| Recovery journal | the founder records the event in `alpha/recovery_journal.json` with `kind = "bad_recovery"`; the per-row notes capture what the launcher offered vs what the user wanted. |
| Control room | `/recovery` route counts `bad_recovery` rows in the trust panel; the trust-quality % drops accordingly. |
| Engine impact | the engine's recovery scoring uses the recovery journal as a feedback signal in a future phase. For now, the journal is the *ground truth* the founder reviews weekly. |

The directive's underlying contract: **a recovery that turns
out to be bad must never be reframed by the launcher as a
success**. The launcher shows what it offered honestly; the
ledger captures the verdict.

---

## Cross-cutting rules

| Rule | Enforced where |
|---|---|
| **Max 3 evidence chips** | `RecoveryCardV3.__init__` truncates `parse_evidence_chips(evidence)[:3]`. |
| **Never fabricate a chip** | the parser only splits the engine's deterministic `·`-separated caption; an empty input yields zero chips. |
| **Confidence sentence is optional** | `RecoveryCardV3(sentence=...)` accepts an engine-provided sentence; falls back to `DEFAULT_SENTENCES[signal]`. |
| **Sort order** | `sort_for_digest()` orders investigations: unfinished (rank 0) · returned (1) · recent (2) · passive (3). Within a rank, high-strength threads come first. |
| **Investigation strip cap** | `MinimalInvestigations.MAX_VISIBLE = 3`; surplus collapses into a single dashed `+N more` chip — never wraps, never scrolls. |
| **No engine touch** | every signal-mapping helper (`_recovery_to_v3`, `_thread_to_v3`, `sort_for_digest`) lives in the launcher layer; the engine ships unchanged. |

---

## Related

- [`PHASE_6N_STATUS.md`](../../archive/phase-status/PHASE_6N_STATUS.md) — engineering receipt + verification matrix.
- [`assets/screenshots/launcher-recovery/`](../../assets/screenshots/launcher-recovery) — 5 captures referenced above.
- [`DAILY_LOOP.md`](DAILY_LOOP.md) — `recoveries_shown` / `recoveries_used` / `resume_success` counters that feed the *resume quality* signal.
- [`MOMENTS.md`](../alpha/MOMENTS.md) — the seven first-time moments per tester; the *bad recovery* row of the moments log links straight to a journal entry.
