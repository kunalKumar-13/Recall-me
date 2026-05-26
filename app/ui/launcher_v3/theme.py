"""Phase 6I + 6M.1 — launcher v3 theme tokens.

Single source of truth for the colours, radii, shadow scales, and
typography sizes the v3 surfaces consume.

Phase 6M.1 (Launcher Refinement) re-tunes the values so the surface
feels *shipped* — paper-white background, solid cards (no
transparency, no blur), tighter shadow, the directive's
**title 22 / section 14 / meta 12** typography scale, and the
**28 / 20 / 12** spacing rhythm.

    background:  #F7F5F2   (paper white)
    surface:     #FFFFFF   (solid white card — no glass, no blur)
    accent:      lavender
    radius:      20 (card)
    shadow:      0 8 24 low opacity (single soft drop)

This module has **no Qt imports** so it stays cheap to load and the
constants can be reused by capture scripts that don't construct
QApplication.
"""

from __future__ import annotations

# ── colours ────────────────────────────────────────────────────────

# Phase 6R — *Launcher Finalization*. The directive freezes the
# launcher's paint: a single warm-paper page with no transparency,
# no blur, no glass. `#F4F1EC` is a touch warmer than 6P.1's
# `#F3F1ED` so the launcher reads as paper, not as a near-white
# panel.
BG = "#F4F1EC"
BG_RAISED = "#FFFFFF"

# Phase 6R — solid 2-px-capable border for the search bar's *card*
# treatment. The 6P.1 hairline (`#E4DED6`) is preserved for the
# hero + investigations card edges (1 px); the search bar uses the
# slightly stronger `BORDER_RAISED_STRONG` (`#E7DED3`) at 2 px so
# the search reads as the launcher's primary input.
BORDER_RAISED = "#E4DED6"
BORDER_RAISED_STRONG = "#E7DED3"

# Phase 6M.1 — cards are now *solid* (no transparency, no blur). The
# alpha levels below stay for backwards-compat with the legacy v3
# surface code, but the refined `SolidCard` paint uses fully opaque
# fills.
SURFACE_ALPHA_HIGH = 255   # solid white
SURFACE_ALPHA_MID = 255    # solid white (was 220 in 6I)
SURFACE_ALPHA_LOW = 255    # solid white (was 184 in 6I)

# Lavender — matches `app/ui/styles.py:ACCENT` (Phase 6B).
ACCENT = "#8B7FE3"
ACCENT_SOFT = "#EDE9FB"
ACCENT_LINE = "rgba(139, 127, 227, 60)"

# Ink — three weights of warm-dark text on the warm-white background.
INK = "#16112B"
INK_2 = "#4A4458"
INK_3 = "#847B8E"
INK_4 = "#B8B2C0"

# Hairlines — used by SoftDivider + card borders.
# Phase 6M.1: a slightly stronger card border so solid cards read as
# physical objects rather than washes.
HAIRLINE = "rgba(24, 17, 45, 24)"
HAIRLINE_STRONG = "rgba(24, 17, 45, 36)"

# Status colours — only used by ConfidenceBadge + StatusDot.
OK = "#4FA784"
OK_SOFT = "#E2F3EB"
WARN = "#C98A5E"
WARN_SOFT = "#F8EDE1"
DANGER = "#D05B5B"
DANGER_SOFT = "#F8E2E2"

# ── radii ──────────────────────────────────────────────────────────

RADIUS_PILL = 12
RADIUS_CARD = 20      # default RecoveryCardV3 / InvestigationCardV3 (Phase 6M.1 spec)
RADIUS_PANEL = 20     # 6M.1: collapse panel + card radii so the rhythm is one value
RADIUS_HERO = 20      # 6M.1: hero matches card (was 28); the directive's *radius 20*

# ── shadow ─────────────────────────────────────────────────────────
#
# Phase 6M.1 — the directive's *0 8 24 low opacity* spec. Single
# soft drop, slight downward offset so the card reads as resting
# on the paper-white page rather than floating in space.

SHADOW_SOFT_RADIUS = 24
SHADOW_SOFT_ALPHA = 18
SHADOW_SOFT_OFFSET = 8
SHADOW_LIFT_RADIUS = 30
SHADOW_LIFT_ALPHA = 26
SHADOW_LIFT_OFFSET = 10

# Phase 6P.1 — *Visibility* shadow scale (used by the hero +
# investigations cards). 0 12 32 rgba(0,0,0,.08).
SHADOW_CARD_RADIUS = 32
SHADOW_CARD_OFFSET = 12
SHADOW_CARD_ALPHA = 20    # ≈ 0.08 alpha

# Phase 6R — search-bar shadow. The directive's exact spec:
# 0 8 24 rgba(0,0,0,.06). Slightly lighter than the hero/work card
# shadow so the search bar sits *under* them in z-order despite
# being painted at the top of the column.
SHADOW_SEARCH_RADIUS = 24
SHADOW_SEARCH_OFFSET = 8
SHADOW_SEARCH_ALPHA = 16   # ≈ 0.06 alpha

# ── spacing rhythm ────────────────────────────────────────────────
#
# Phase 6M.2 — the launcher had regressed to dashboard-shaped
# generosity. The directive's recovery spec: tighter 20 / 16 / 12 / 8
# vertical rhythm so the surface compresses to a Raycast-shaped
# utility instead of a Notion-shaped page.

GUTTER = 20          # outer column padding (6M.1=28 → 6M.2=20)
SECTION_GAP = 16     # between sections — search↦hero↦investigations (was 20)
CARD_GAP = 12        # between cards inside a section (unchanged)
RETURNS_GAP = 8      # between the investigation strip and the returns row
CHIP_GAP = 6         # between chips in a chip row (unchanged)

# ── typography sizes (px) ────────────────────────────────────────
#
# Phase 6M.2 — reduce visual weight. The launcher is a utility,
# not a marketing page; the headline doesn't need to be the page
# headline.

FS_HERO = 20         # the Continue card title (6M.1=22 → 6M.2=20)
FS_TITLE = 14        # investigation card title (was 16)
FS_BODY = 13         # body text inside cards (was 14)
FS_LABEL = 10        # section eyebrow / chip / pill (was 11)
FS_META = 11         # time labels, footer counts (was 12)
FS_SECTION = 13      # explicit *section* size — quieter (was 14)
FS_CONFIDENCE = 10   # confidence badge text — quietest pill in the card


__all__ = [
    # colours
    "BG", "BG_RAISED", "BORDER_RAISED", "BORDER_RAISED_STRONG",
    "SURFACE_ALPHA_HIGH", "SURFACE_ALPHA_MID", "SURFACE_ALPHA_LOW",
    "ACCENT", "ACCENT_SOFT", "ACCENT_LINE",
    "INK", "INK_2", "INK_3", "INK_4",
    "HAIRLINE", "HAIRLINE_STRONG",
    "OK", "OK_SOFT", "WARN", "WARN_SOFT", "DANGER", "DANGER_SOFT",
    # radii
    "RADIUS_PILL", "RADIUS_CARD", "RADIUS_PANEL", "RADIUS_HERO",
    # shadow
    "SHADOW_SOFT_RADIUS", "SHADOW_SOFT_ALPHA", "SHADOW_SOFT_OFFSET",
    "SHADOW_LIFT_RADIUS", "SHADOW_LIFT_ALPHA", "SHADOW_LIFT_OFFSET",
    "SHADOW_CARD_RADIUS", "SHADOW_CARD_OFFSET", "SHADOW_CARD_ALPHA",
    "SHADOW_SEARCH_RADIUS", "SHADOW_SEARCH_OFFSET", "SHADOW_SEARCH_ALPHA",
    # spacing
    "GUTTER", "SECTION_GAP", "CARD_GAP", "RETURNS_GAP", "CHIP_GAP",
    # typography
    "FS_HERO", "FS_TITLE", "FS_BODY", "FS_LABEL", "FS_META",
    "FS_SECTION", "FS_CONFIDENCE",
]
