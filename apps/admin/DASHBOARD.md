# Recall — operator dashboard

The founder's 30-second read. **Operational as of Phase 5E.1:** the
usage numbers are now real — fed by counts-only `recall stats`
exports that cohort members *choose* to send.

**Refresh:**

```bash
python apps/admin/pull_release_stats.py   # GitHub downloads  [auto]
python apps/admin/merge_stats.py          # cohort exports    [cohort]
python apps/admin/cohort_summary.py       # the rollup + health signal
```

Source tags: `[auto]` GitHub, no telemetry · `[cohort]` voluntary
`stats.json` import · `[manual]` founder-logged · `[—]` not
collected, by design.

---

## Health Overview

One glance: is the product alive? Each card is **green / yellow /
red**, computed from the merged cohort aggregate by
`cohort_summary.py`.

| Card | Green | Yellow | Red |
|---|---|---|---|
| **Installation health** | installs accumulate events | installs but `events_total` tiny | `install_age_days` flat — install dead |
| **Continuity health** | recoveries shown *and* accepted | shown, rarely accepted | `recoveries_shown` 0 — recovery never surfaced |
| **Extension health** | `extension_connected_days` climbing | sporadic browser events | `extension_connected_days` 0 — never paired |
| **Trust health** | accept rate healthy, feedback calm | open `trust`-tagged feedback | recoveries shown, accepted ≈ 0 — cards not believed |

Overall signal (from `cohort_summary.py`):

- **RED** — installs run, but no recovery ever surfaced.
- **YELLOW** — recoveries flow, but the extension is absent.
- **GREEN** — installs work, recoveries flow.

> Current: **no data** — alpha-001 has not opened. The pipeline is
> built and verified; it is waiting for its first real export.

## 1. Release Monitor

| Metric | Value | Source |
|---|---|---|
| Current version | `v0.1.0` (pre-alpha) | manual |
| **Active installs** | downloads of `Recall-Setup.exe` (proxy) | `[auto]` |
| **Returning installs** | devices with `weekly_active_days` > 1 | `[cohort]` |
| Windows / macOS split | per-asset download counts | `[auto]` |
| Installer failures · update success | not collected | `[—]` |

## 2. Usage Health — counts only, no content

| Metric | Source |
|---|---|
| Active installs · returning installs | `[auto]` · `[cohort]` |
| Investigations created | `[cohort]` `investigations_total` |
| **Recovery sessions** (shown · accepted) | `[cohort]` `recoveries_shown` · `recoveries_accepted` |
| Resume success rate | `[cohort]` `resume_success_rate` |
| **Continuity events** (events captured/day) | `[cohort]` `events_total` ÷ active days |
| Extension-connected days | `[cohort]` `extension_connected_days` |

### Founder additions (Phase 5B)

Computed by `merge_stats.py` and printed by `cohort_summary.py`.
Aggregate only — never per-user, never finer than counts.

| Metric | Aggregate definition | Reads from |
|---|---|---|
| **Returning installs** | devices with `weekly_active_days >= 2` | per-device export |
| **Resume sessions** | sum of `recoveries_accepted` | per-device export |
| **Continuity restored** | avg `resume_success_rate` across devices | per-device export |
| **Daily reopen %** | avg `daily_active_days ÷ install_age_days` | per-device export |

These four are the founder's *behavioural* answers — did the
installs stick (returning), did the product run (resume sessions),
did it actually help (continuity restored), did people come back
(daily reopen %). None of them is a *user score*; the per-device
counterpart on the user's machine (`recall stats --today`,
`CONTINUITY_HEALTH.md`) stays local and never feeds this view.

> **Vocabulary note (Phase 5E.1).** This dashboard does not say
> *downloads*, *users*, *DAU*, or *MAU* — those are the words of an
> analytics product that watches people. Recall counts **active
> installs**, **returning installs**, **recovery sessions**, and
> **continuity events**: things, not surveilled humans.

## 3. Funnel

```
Active installs       [auto]    ← release downloads
  → Returning install [cohort]  ← weekly_active_days > 1
  → First investigation [cohort]
  → Recovery session  [cohort]  ← recoveries_shown
  → Recovery accepted [cohort]  ← the milestone
```

## 4. Feedback Inbox

Live file: [`FEEDBACK.md`](FEEDBACK.md) — tags: `pain`, `bug`,
`confusing`, `feature`, `trust`.

## 5. Public Alpha Cohorts

Registry: [`cohorts.json`](cohorts.json) · board:
[`../../ALPHA_USERS.md`](../../docs/founder/ALPHA_USERS.md).

---

## The 30-second read

1. **Health Overview** — four cards green?
2. **Release Monitor** — active installs moved?
3. **Feedback Inbox** — anything new?

If sections 2–4 are sparse, that is a local-first product being
honest about what it cannot see — fed only by what users *chose* to
share. The fix is a cohort conversation, never a ping.
