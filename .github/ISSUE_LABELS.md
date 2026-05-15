# Issue labels

The canonical label set for Recall's GitHub issues + pull
requests. The set is intentionally narrow — labels are
expensive when there are too many, and the audit at the
bottom of this file shows why.

Apply labels at the time of triage. A maintainer reviewing
a fresh issue should assign at least one **kind**, one
**area**, and (if known) one **priority** label.

## kind:* — what the issue *is*

| Label | Use |
|---|---|
| `kind/bug` | Something is broken — incorrect output, crash, regression. |
| `kind/feature` | A new capability inside the brief. (Capabilities outside the brief get `kind/wontfix-out-of-scope`.) |
| `kind/perf` | Slower than the documented budget in `CLAUDE.md`. Include the measured numbers. |
| `kind/docs` | A docs change. Includes README, CHANGELOG, and architecture pages. |
| `kind/refactor` | Internal cleanup with no user-visible change. |
| `kind/discussion` | A design question that needs to be answered before any code lands. |
| `kind/wontfix-out-of-scope` | Explicitly closed under one of the *"Things we will not build"* rules in `CLAUDE.md`. The closing comment cites the relevant rule. |

## area:* — which subsystem it lives in

Pick one. If the issue spans multiple, pick the dominant
one; comment names the others.

| Label | Use |
|---|---|
| `area/events` | Event log, JSONL schema, EventLogger / EventStore. |
| `area/sessions` | Session reconstruction. |
| `area/contexts` | Micro-context reconstruction. |
| `area/resurfacing` | Phase 2B engine + the *On your radar* surface. |
| `area/threads` | Memory threads + identity cache. |
| `area/evolution` | Phase chronology + the SessionTimelineCard. |
| `area/recovery` | Continuity recovery + the one-click restore. |
| `area/launcher` | PyQt6 launcher (widgets, hotkey, settings dialog). |
| `area/api` | FastAPI service + the `/v1/*` surface. |
| `area/extension` | Chrome / Edge browser extension. |
| `area/web` | Marketing site (`apps/web/`). |
| `area/docs` | Documentation site (`apps/docs/`). |
| `area/build` | PyInstaller spec, installer pipeline, signing. |
| `area/dev-experience` | Dev scripts, smoke test, CI (when it lands). |

## priority:* — how urgent

Optional, applied during triage.

| Label | Use |
|---|---|
| `priority/critical` | A data-loss or security issue. Drop everything. |
| `priority/high` | Affects daily use; fix in the next release. |
| `priority/medium` | Affects some users; fix in a near release. |
| `priority/low` | Polish / nice-to-have; pick up when the area is open. |

## first-impression flags

These are intentionally not "priority" — they describe
**who's asking** rather than how loud:

| Label | Use |
|---|---|
| `good first issue` | A maintainer has confirmed the scope is small enough for someone's first PR. Comment includes the entry-point file. |
| `help wanted` | The maintainer doesn't have bandwidth; happy to review a PR. |
| `from-audit` | Traced to a specific item in `AUDIT_REPORT.md` or `PHASE_4A_STATUS.md`. Comment links the line. |

## status:* — pipeline state

A small set, applied by the maintainer after a triage.

| Label | Use |
|---|---|
| `status/needs-info` | Waiting on the reporter for a reproduction. Closes if no response in 14 days. |
| `status/blocked` | Waiting on an external dependency (a cert, an upstream fix). Comment names the dependency. |
| `status/in-progress` | A PR is open or imminent. Linked from the PR. |
| `status/ready-for-review` | Code is ready; needs a reviewer. |

## Audit — why this many, and not more

A standard GitHub repo accumulates 30+ labels in the first
year. Recall's standing rule is *every label has to earn
its weight* (same rule as the engineering charter applies
to code). The set above is 24 labels in five families. Adding
a label requires:

1. A row in this file describing the label's exact use.
2. At least three open issues that would have taken the
   new label *today*.
3. A maintainer who'll keep the label clean (re-apply,
   re-explain in code review).

Removing a label requires a sweep through open issues
re-labelling them to a remaining one.

## Bootstrapping on a new repo

If you're standing up a fresh GitHub repo (e.g. after the
[`REPO_STRUCTURE.md`](../REPO_STRUCTURE.md) split), use the
GitHub CLI to apply this set:

```bash
# (illustrative — not a runnable script today)
gh label create kind/bug             --color "d73a4a"
gh label create kind/feature         --color "a2eeef"
gh label create kind/perf            --color "e99695"
gh label create kind/docs            --color "0075ca"
gh label create kind/refactor        --color "cfd3d7"
gh label create kind/discussion      --color "d4c5f9"
gh label create kind/wontfix-out-of-scope --color "ffffff"

gh label create area/events          --color "1d76db"
# … one per area
# … one per priority + first-impression + status
```

A real runnable script will land at
`infra/scripts/setup-labels.sh` once the repo is public.
