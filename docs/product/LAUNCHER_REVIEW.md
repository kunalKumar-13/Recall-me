# LAUNCHER_REVIEW.md — what the refinement deleted, what it kept, why

The audit doc Phase 6M.1 produced. Pairs with
[`PHASE_6M.1_STATUS.md`](../../archive/phase-status/PHASE_6M.1_STATUS.md) (the
engineering receipt) and
[`archive/launcher-refine/README.md`](../../archive/launcher-refine/README.md)
(the rationale per archived capture script).

The directive: the launcher should *feel shipped*. Refinement
only — no new features, no engine work, no control-room work.

This file is the four-section table the directive named —
**removed**, **kept**, **why**, **future**.

---

## Removed

| Surface | What it was | Where it went |
|---|---|---|
| `MinimalEmpty`'s wrapping `GlassCard` | A floating white card around the icon + headline + sub + buttons (Phase 6L). | The card wrapper is gone. The empty surface paints the icon + text + buttons directly on the paper-white page, vertically centred. |
| The hero's *"Surfaced because you left this mid-flow."* footer | A small ink-3 line under the chip row. | Deleted. The chip strip + confidence badge already say the same thing; the directive's *delete duplicate text / secondary metadata* rule applies. |
| Hero's translucent fill | `QColor(T.ACCENT_SOFT)` at alpha=220. | Solid `T.ACCENT_SOFT` (alpha=255). Same hue, no transparency. |
| `GlassCard` translucent paint (all variants) | `QColor(255, 255, 255, T.SURFACE_ALPHA_MID)` (220). | Solid white (alpha=255). The `alpha` constructor argument is silently clamped to 255; downstream callers don't need to change. |
| Investigation-pill flush-left layout | `_strip.addWidget(pill); _strip.addStretch(1)` | Equal-width pills via `_strip.addWidget(pill, 1)`. Pills now share the strip's width; overflow drops a single `+N more` dashed chip rather than wrapping. |
| The `Surfaced because…` widget's `QLabel` | One label, one stylesheet, one `outer.addWidget()`. | Deleted entirely. No replacement. |
| `MinimalShell.MIN_WIDTH = 760` | The column had a hard 760-px floor (Phase 6L). | New `MIN_WIDTH = 600` so the column breathes on smaller windows. `MAX_WIDTH` tightens from 860 → 760 (directive: *max width 760*). |
| Capture scripts that fixture the old shape | `capture_launcher_v3.py` (6I 3-column shell) · `capture_launcher_live.py` (6K live composition) · `capture_launcher_minimal.py` (6L pre-refinement minimal). | Moved to `archive/launcher-refine/` with a README documenting why each was archived. The 6I / 6K / 6L screenshots themselves remain on disk as historical reference. |

## Kept

| Surface | Why kept |
|---|---|
| `MinimalSearchBar` | Search at the top of the column was always the right shape; only the surrounding spacing tightened. |
| `MinimalDigest` composition (hero + investigations + returns + trust) | The four-section vertical stack is the directive's *exact* shape; refinement was about size + paint + spacing, not order. |
| `RecoveryCardV3` core widget | Title + chip row + confidence badge + Resume CTA already match the directive's hero spec; refinement bottom-aligned the action row and dropped the footer line. |
| `_InvestigationPill` widget | The pill shape is right; refinement made it stretch to equal width and added the overflow chip. |
| `MinimalReturns` row layout | Hidden on empty input — already honoured the directive's *5-second understanding* rule; no change. |
| `MinimalTrust` footer | One quiet mono line — already as small as it can be. No change. |
| `surfaces.GlassCard` class name | Kept as a backwards-compat shim. Every importer of `from app.ui.launcher_v3 import GlassCard` keeps working; the paint is now solid. |
| `archive/launcher-v2/` (Phase 6L) | Still present. The 6L archive is a separate decision about the 3-column shell; 6M.1 added a sibling `archive/launcher-refine/` for the **capture scripts** that referenced the previous shape. |

## Why

The launcher was already minimal after Phase 6L. The
refinement *wasn't* about removing functionality — it was
about making the surface read as **finished product** instead
of *in-progress prototype*.

Three specific reads the refinement targeted:

1. **Card paint.** Translucent white over a warm-white page
   reads as *concept art* — the eye notices that the surface
   is *almost* a card. Solid white over the page reads as a
   card. The directive's *cards look physical* rule maps
   directly onto `alpha=255` everywhere.
2. **Geometry slop.** A 760-860 width *range* meant the
   capture pipeline produced slightly different-shape
   screenshots run-over-run; the live launcher's surface
   reflowed when the window was resized. A single 760-px max
   width means the launcher *looks the same* every time it
   opens.
3. **Empty-state framing.** Wrapping the empty surface in a
   `GlassCard` made it read as "the launcher has nothing right
   now" — a *broken* feeling. Painting the icon + text + buttons
   directly on the page reads as "Recall is calmly waiting" —
   a *settled* feeling. Same content; different framing.

The directive's spacing values (28 / 20 / 12) align the
column to a grid that the previous 32 / 24 / 14 didn't. The
typography sizes (22 / 14 / 12) restate the same three reads
the rest of the product uses (Hero headline at 22 in the
marketing site, section labels at 14 in the control room,
mono meta at 12 in the daily-loop summary).

## Future

What refinement *didn't* close, kept here as the next
launcher-touching phase's input:

- **Live ContextColumn flow.** The 6L LiveLauncher reads
  `health.events_today` once via `_refresh_context()` for the
  *Today* count; the count never appears in the minimal
  layout. Surfacing it in the minimal shell would re-introduce
  the *dashboard* feel — keep it out until a user explicitly
  asks.
- **First-recovery banner on the empty card.** Still pending
  (Phase 6L's *what did not ship* table named it). The slot
  is ready; the widget lands when the cohort records its
  first recovery.
- **`MinimalReturns` row icon.** Currently a `StatusDot("mute")`.
  Could become a per-event-kind glyph (browser / file / chat /
  desktop) — but only when the directive *names* it. Today's
  refinement deliberately stops here.
- **`SearchPanel` results column.** The search bar emits
  `query_changed`; LiveLauncher relays the signal but the
  results never render inline. A third `QStackedLayout` index
  (empty / digest / results) is the next focused refactor.
- **Desktop badge in the launcher trust line.** Phase 6M's
  desktop layer surfaces apps in the popup and control room;
  the launcher's trust line could grow a small `N apps today`
  caption to mirror it. Refinement deliberately did *not* add
  that — *delete density* outranked *parity with popup*.

Nothing on this list is a regression; each item is *next*
work that the refinement intentionally did not pull forward.

---

## Related

- [`PHASE_6M.1_STATUS.md`](../../archive/phase-status/PHASE_6M.1_STATUS.md) —
  the engineering receipt.
- [`archive/launcher-refine/README.md`](../../archive/launcher-refine/README.md)
  — per-capture-script rationale for the archived files.
- [`archive/launcher-v2/README.md`](../../archive/launcher-v2/README.md)
  — Phase 6L's earlier archive of the 3-column shell.
- [`assets/screenshots/launcher-refined/`](../../assets/screenshots/launcher-refined)
  — the five refined captures the directive named.
