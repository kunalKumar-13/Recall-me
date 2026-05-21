# LANDING_GO_LIVE.md — what has to be true before the website goes live

The website at [`apps/web/`](../../apps/web/) is the *front door*
for a person who has never heard of Recall. Once it goes live,
the install path is no longer a hand-share — strangers will hit
it, click *Download*, and either succeed or bounce. This file is
the punch list that turns it on.

Pairs with [`GO_NO_GO.md`](GO_NO_GO.md) (the public-alpha
gates) and [`INSTALL.md`](INSTALL.md) (the user-facing
walkthrough).

---

## The bar

Go-live = a person who:

- arrives at the landing page with no context,
- watches less than 90 seconds of motion / reads less than three
  paragraphs,
- clicks one button labelled *Download*,
- ends up with `Recall-Setup.exe` on their machine,
- runs it and lands in the first-launch onboarding,
- understands enough about *what Recall does* and *what it
  doesn't* to choose folders honestly,
- closes their laptop trusting that nothing is leaving.

Everything below is a row that has to be true for that sentence
to be honest. The website *does not go live* until every row is
✅. Today most rows are still ⬜.

---

## Page checklist

### 1. Hero — the one paragraph

| Item | Status | What "done" looks like |
|---|---|---|
| The one-sentence promise is the visible headline | ⬜ | *"A continuity layer for your own thinking — only on your machine."* (or its winner) — verbatim from [`docs/product/CONTINUITY_LANGUAGE.md`](../product/CONTINUITY_LANGUAGE.md) |
| The subheadline names *what it is not* in the same breath | ⬜ | *"Not an AI memory assistant. Not a cloud service. Not a productivity dashboard."* |
| Hero CTA reads *Download for Windows* (not *Sign up*, not *Start free*) | ⬜ | direct link to `Recall-Setup.exe` |
| macOS button reads *Coming soon* + a one-line link to [`MAC_BUILD_STATUS.md`](MAC_BUILD_STATUS.md) | ⬜ | honest about the Preview status |
| Hero motion is the launcher's idle digest, not a marketing animation | ⬜ | uses `assets/screenshots/launcher-digest.png` or its GIF |

### 2. Three sections, not seven

| Item | Status | Source |
|---|---|---|
| *Continue where you left off* — recovery card screenshot + 30 words | ⬜ | `assets/screenshots/recovery-card.png` |
| *Active investigations* — the investigations panel + 30 words | ⬜ | `assets/screenshots/launcher-digest.png` (already in hero; reuse a crop) |
| *Trust* — the boundary statement + a link to [`TRUST_LEDGER.md`](../engineering/TRUST_LEDGER.md) | ⬜ | one paragraph, links to the long version |

The current page (Phase 5B redesign) has more sections than
this. The directive's *Three sections, not seven* trims the
landing to the three that move a stranger from arrival to
download.

### 3. Download row

| Item | Status | Detail |
|---|---|---|
| Windows download is the **real** `Recall-Setup.exe` | ⬜ | currently 260.8 MB, SHA-256 `7AFA5349…75FD975` |
| SHA-256 is rendered next to the download button | ⬜ | copy-on-click |
| File size is in the button copy ("Download · 261 MB") | ⬜ | strangers deserve the number |
| macOS link points to [`MAC_VERIFICATION.md`](MAC_VERIFICATION.md) | ⬜ | until a maintainer fills the matrix |
| *Run from source* link is one paragraph below for developers | ⬜ | small, not hidden |

### 4. FAQ — six questions, no more

The directive caps the FAQ at six. They are the six a stranger
will ask in their first three minutes:

| # | Question | Source of truth |
|---|---|---|
| 1 | *"What does Recall actually do?"* | [`README.md`](../../README.md) + [`SAMPLE_WORKFLOW.md`](../../alpha/SAMPLE_WORKFLOW.md) |
| 2 | *"Where does my data go?"* | [`TRUST_LEDGER.md`](../engineering/TRUST_LEDGER.md) |
| 3 | *"Is this an AI thing?"* | [`CLAUDE.md`](../../CLAUDE.md) § *Things we will not build* |
| 4 | *"What if I want to remove it?"* | [`alpha/INSTALL.md`](../../alpha/INSTALL.md) § *Uninstall* |
| 5 | *"Does it work on Mac / Linux?"* | [`SUPPORTED_PLATFORMS.md`](SUPPORTED_PLATFORMS.md) |
| 6 | *"What's the catch?"* | [`KNOWN_LIMITATIONS.md`](../product/KNOWN_LIMITATIONS.md) |

Each FAQ answer is **two sentences**, with a link to the long
form. The landing FAQ is not a documentation portal.

### 5. Limitations — visible, not hidden

| Item | Status | What "done" looks like |
|---|---|---|
| A single line near the download: *"Unsigned installer — SmartScreen may warn on first run."* + link to the workaround | ⬜ | this is the #1 friction for a stranger; calling it out is trust |
| macOS row says *Preview only — see verification matrix* | ⬜ | covered by FAQ #5 + the download row |
| Day-1 expectation: *"The first day, the launcher is empty by design. Recall starts useful at Day 2-3."* | ⬜ | short, near the download |

### 6. Demo / proof assets

| Item | Status | Source |
|---|---|---|
| One landing-hero motion (launcher state cycle, 4 frames, looped) | ⬜ | `assets/demos/launcher.gif` (Phase 5H) |
| Recovery-card focus moment, 2-frame loop | ⬜ | `assets/demos/recovery.gif` (Phase 5H) |
| Extension popup state cycle | ⬜ | `assets/demos/extension.gif` (Phase 5H) |
| Live install screen capture | ⬜ | `assets/demos/install.gif` — pending live recording on a fresh VM |
| Control-room glance | ⬜ | `assets/demos/control-room.gif` — pending live recording |

The Phase 5H deterministic GIFs (launcher / recovery / extension)
are produced from existing real captures; the live ones
(install / control-room) need a screen recorder. The recording
protocol is in [`docs/release/RECORDING_PROTOCOL.md`](RECORDING_PROTOCOL.md).

### 7. Privacy + footer

| Item | Status |
|---|---|
| No analytics script on the page (Plausible / GA / Posthog: none) | ⬜ |
| No third-party CDN for marketing JS | ⬜ |
| Footer link to [`TRUST_LEDGER.md`](../engineering/TRUST_LEDGER.md) | ⬜ |
| Footer link to the GitHub repo + the issues page | ⬜ |
| Footer says *"Built by one person. Honest about limits."* — or its winner | ⬜ |

---

## What `apps/web` already has

This is *not* a from-scratch page. Phase 5B's redesign landed a
calm cinematic Hero, a Features section, and a final CTA. The
go-live checklist above is the diff between *that* page and the
*shippable* page.

The known gaps from the Phase 5G screenshots README:

- The site uses static screenshots, not the new
  [`launcher-digest.png`](../../assets/screenshots/launcher-digest.png) /
  [`recovery-card.png`](../../assets/screenshots/recovery-card.png)
  versions from Phase 4L / 5F / 5G.
- The download CTA is a placeholder; no real `Recall-Setup.exe`
  link.
- The FAQ has eight questions, two of them aspirational. Trim
  to six.

---

## The go-live gate

The landing goes live only when:

1. Every row above is ✅.
2. [`GO_NO_GO.md`](GO_NO_GO.md) gate 1 is GO (three
   clean-machine runs of `Recall-Setup.exe` complete).
3. [`alpha_report.md`](../../alpha/alpha_report.md) has at
   least one *correct first recovery* recorded from the
   cohort.
4. The installer is code-signed (or the SmartScreen warning is
   honestly named on the download row — both are acceptable for
   alpha; only one is acceptable post-alpha).

Until all four are true, the website stays in its private state.

---

## Once live — the *first 48 hours* runbook

Not part of go-live itself, but written here so the founder is
not improvising at 2 AM. In the first 48 hours after the page
goes live:

| Hour | Watch |
|---|---|
| 0-6 | the GitHub issues stream; the `Recall-Setup.exe` download count (GitHub releases); the `?utm_source=…` URLs people share |
| 6-24 | the first 5-10 testers' `recall doctor` outputs (if they share); any *"the installer SmartScreen-blocked me"* report (expected — the row above named it) |
| 24-48 | the first uninstall reports; the first *"this is exactly what I needed"* report; the first *"this is not what I thought it was"* report |

The pre-rendered response for each of those three classes of
report lives in [`docs/founder/FOUNDER_OPERATIONS.md`](../founder/FOUNDER_OPERATIONS.md).

No social-media monitoring. No notification-bell dashboard. The
loop is intentionally human.

> Cross-referenced by [`GO_NO_GO.md`](GO_NO_GO.md) (the gate
> this file unblocks) and
> [`PHASE_TRACKER.md`](../founder/PHASE_TRACKER.md) Phase 5H.
