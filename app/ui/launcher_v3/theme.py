"""Phase 10 — Recall · Launcher (dark, focused).

Token surface ported verbatim from the Phase 10 design pack
(`Recall Launcher.html` + `launcher.jsx`). The launcher canvas is
dark cinematic with a soft violet bloom; the warm-paper palette of
Phase 6R / Phase 9 is gone.

No Qt imports here so the file stays cheap to load + the constants
can be reused by capture scripts without constructing a QApplication.

Frame contract:
  760 x 520 root window
  20 px radius
  outer page #08070C
  surface #0F0D16 with radial-gradient atmosphere bloom
  layered cards on top: cardHi -> card linear-gradient (#1B1827 -> #15131F)
"""

from __future__ import annotations

# ── canvas ────────────────────────────────────────────────────────

# Outside-the-window page colour. Effectively the desktop the
# launcher floats on.
BG = "#08070C"

# Base window surface (inside the rounded frame).
SURFACE = "#0F0D16"

# Raised card surface (used by HeroRecovery + PreviewCard +
# investigation rows + restored-list container).
CARD = "#15131F"
CARD_HI = "#1B1827"        # top stop of card gradient
CARD_HOVER = "#1F1B2D"

# ── accents ───────────────────────────────────────────────────────

# Primary lavender used for: accent rails, glow, primary button
# fill, the hero serif-italic word, focus rings, "RESTORED" /
# "INVESTIGATION" eyebrows.
ACCENT = "#A78BFA"
ACCENT_DEEP = "#8B7FE3"
ACCENT_SOFT = "rgba(167, 139, 250, 0.16)"
ACCENT_GLOW = "rgba(167, 139, 250, 0.32)"

# ── text ──────────────────────────────────────────────────────────
#
# Six-step text ladder. INK is the bright headline; INK_FAINT is the
# quietest mono microtext (footer status hints).

INK = "#FAFAFA"
INK_2 = "#D4D4D8"
INK_MUTED = "#9A98A6"
INK_FAINT = "#6E6C7A"
INK_DIM = "#4C4A59"

# ── hairlines ─────────────────────────────────────────────────────

# Two-step hairline ladder. LINE is the quiet card edge; LINE_HI is
# the slightly stronger border for inputs + buttons.
LINE = "rgba(255, 255, 255, 0.07)"
LINE_HI = "rgba(255, 255, 255, 0.12)"

# ── status (rarely used on the dark launcher; kept for parity) ───

OK = "#5DBE89"            # daemon-alive footer dot
OK_GLOW = "rgba(93, 190, 137, 0.55)"
DANGER = "#E15050"
DANGER_SOFT = "rgba(229, 80, 80, 0.10)"

# ── radii ─────────────────────────────────────────────────────────

RADIUS_FRAME = 20         # root window
RADIUS_CARD = 14          # hero + preview card
RADIUS_CARD_SM = 12       # mini preview pane in Search state
RADIUS_PILL = 9           # buttons + Kbd containers
RADIUS_CHIP = 7           # chips inside the hero

# ── shadows ───────────────────────────────────────────────────────
#
# The frame's shadow is composite (inset highlight + drop + ring + outer
# glow). PyQt6 can't easily stack four shadows on one widget, so the
# capture paths approximate with one solid drop + a manually-painted
# violet glow ring drawn in the parent.

FRAME_SHADOW_BLUR = 80
FRAME_SHADOW_OFFSET_Y = 30
FRAME_SHADOW_ALPHA = 180          # 0..255

# Hero card lift (used by HeroRecovery / PreviewCard).
CARD_SHADOW_BLUR = 50
CARD_SHADOW_OFFSET_Y = 20
CARD_SHADOW_ALPHA = 178

# Accent disc / pill glow.
ACCENT_HALO_BLUR = 28

# ── spacing rhythm ────────────────────────────────────────────────
#
# Vertical/horizontal rhythm in pixels. Sourced from the JSX layout
# inspection: search bar 60, footer 30, content padding 18/22, cards
# at 14 radius.

H_SEARCH = 60
H_FOOTER = 30
PAD_CONTENT = 18          # vertical padding around the content area
PAD_CONTENT_X = 22        # horizontal padding (Recovery/Resume states)
PAD_CONTENT_X_SEARCH = 12 # tighter horizontal padding (Search state list)
GAP_SECTION = 14          # between content rows
GAP_CARD = 8              # between cards
GAP_CHIP = 6              # between chips inside the hero
GAP_BTN = 8               # between buttons in a button row

# ── typography sizes (px) ─────────────────────────────────────────

FS_HERO_TITLE = 23        # Recovery hero title; Empty tagline (Phase 10D: 22 -> 23 — modest bump that doesn't clip the 1fr/220px hero+preview grid)
FS_RESUME_TITLE = 17      # Resume state title
FS_SEARCH_INPUT = 17      # SearchBar value/placeholder
FS_ROW_TITLE = 13         # OtherRow + SearchRow title
FS_CHIP = 11              # chip text
FS_BUTTON = 13            # primary/ghost button label
FS_BUTTON_SM = 12         # button size=sm
FS_MONO = 10              # footer + meta mono
FS_MONO_SM = 9            # eyebrow mono
FS_EYEBROW = 10           # uppercase eyebrow (lavender)


# ── typography families ───────────────────────────────────────────
#
# Designed against Geist + Geist Mono + Instrument Serif. On a fresh
# Windows box without those installed, Qt falls back to the OS UI
# font + system mono + Georgia. The launcher's structure + colour +
# layout remain correct; only the glyph shapes change.

FAMILY_SANS = "Geist"
FAMILY_MONO = "Geist Mono"
FAMILY_SERIF = "Instrument Serif"

FAMILY_SANS_FALLBACK = "Segoe UI, -apple-system, BlinkMacSystemFont, system-ui, sans-serif"
FAMILY_MONO_FALLBACK = "Consolas, ui-monospace, Menlo, monospace"
FAMILY_SERIF_FALLBACK = "Georgia, 'Times New Roman', serif"


# ── back-compat aliases ───────────────────────────────────────────
#
# A handful of older modules import these names from a previous theme
# generation. Keep the aliases pointing at the closest semantic match
# in the new palette so an import doesn't crash before its caller has
# been refreshed against the new tokens.

BG_RAISED = CARD
BORDER_RAISED = LINE
BORDER_RAISED_STRONG = LINE_HI
SURFACE_ALPHA_HIGH = 255
SURFACE_ALPHA_MID = 255
SURFACE_ALPHA_LOW = 255
INK_3 = INK_MUTED         # legacy 3rd ladder step
INK_4 = INK_FAINT         # legacy 4th ladder step
INK_2 = INK_2             # unchanged
HAIRLINE = LINE
HAIRLINE_STRONG = LINE_HI
ACCENT_LINE = ACCENT_SOFT
OK_SOFT = "rgba(93, 190, 137, 0.18)"
WARN = "#C98A5E"
WARN_SOFT = "rgba(201, 138, 94, 0.14)"

# Spacing aliases from prior generation.
GUTTER = PAD_CONTENT_X
SECTION_GAP = GAP_SECTION
CARD_GAP = GAP_CARD
RETURNS_GAP = GAP_CARD
CHIP_GAP = GAP_CHIP

# Radius aliases.
RADIUS_HERO = RADIUS_CARD
RADIUS_PANEL = RADIUS_CARD

# Typography aliases.
FS_HERO = FS_HERO_TITLE
FS_TITLE = FS_ROW_TITLE + 1
FS_BODY = FS_ROW_TITLE
FS_LABEL = FS_EYEBROW
FS_META = FS_MONO + 1
FS_SECTION = FS_ROW_TITLE
FS_CONFIDENCE = FS_EYEBROW

# Shadow aliases (used by historical capture scripts).
SHADOW_SOFT_RADIUS = CARD_SHADOW_BLUR
SHADOW_SOFT_ALPHA = 80
SHADOW_SOFT_OFFSET = CARD_SHADOW_OFFSET_Y
SHADOW_LIFT_RADIUS = FRAME_SHADOW_BLUR
SHADOW_LIFT_ALPHA = 110
SHADOW_LIFT_OFFSET = FRAME_SHADOW_OFFSET_Y
SHADOW_CARD_RADIUS = CARD_SHADOW_BLUR
SHADOW_CARD_OFFSET = CARD_SHADOW_OFFSET_Y
SHADOW_CARD_ALPHA = 100
SHADOW_SEARCH_RADIUS = 24
SHADOW_SEARCH_OFFSET = 8
SHADOW_SEARCH_ALPHA = 80


__all__ = [
    # canvas
    "BG", "SURFACE", "CARD", "CARD_HI", "CARD_HOVER",
    # accents
    "ACCENT", "ACCENT_DEEP", "ACCENT_SOFT", "ACCENT_GLOW",
    # text
    "INK", "INK_2", "INK_MUTED", "INK_FAINT", "INK_DIM",
    # hairlines
    "LINE", "LINE_HI",
    # status
    "OK", "OK_GLOW", "DANGER", "DANGER_SOFT",
    # radii
    "RADIUS_FRAME", "RADIUS_CARD", "RADIUS_CARD_SM", "RADIUS_PILL", "RADIUS_CHIP",
    # shadow
    "FRAME_SHADOW_BLUR", "FRAME_SHADOW_OFFSET_Y", "FRAME_SHADOW_ALPHA",
    "CARD_SHADOW_BLUR", "CARD_SHADOW_OFFSET_Y", "CARD_SHADOW_ALPHA",
    "ACCENT_HALO_BLUR",
    # spacing
    "H_SEARCH", "H_FOOTER", "PAD_CONTENT", "PAD_CONTENT_X",
    "PAD_CONTENT_X_SEARCH", "GAP_SECTION", "GAP_CARD", "GAP_CHIP", "GAP_BTN",
    # typography
    "FS_HERO_TITLE", "FS_RESUME_TITLE", "FS_SEARCH_INPUT", "FS_ROW_TITLE",
    "FS_CHIP", "FS_BUTTON", "FS_BUTTON_SM", "FS_MONO", "FS_MONO_SM",
    "FS_EYEBROW",
    "FAMILY_SANS", "FAMILY_MONO", "FAMILY_SERIF",
    "FAMILY_SANS_FALLBACK", "FAMILY_MONO_FALLBACK", "FAMILY_SERIF_FALLBACK",
    # legacy aliases
    "BG_RAISED", "BORDER_RAISED", "BORDER_RAISED_STRONG",
    "SURFACE_ALPHA_HIGH", "SURFACE_ALPHA_MID", "SURFACE_ALPHA_LOW",
    "INK_3", "INK_4", "HAIRLINE", "HAIRLINE_STRONG", "ACCENT_LINE",
    "OK_SOFT", "WARN", "WARN_SOFT",
    "GUTTER", "SECTION_GAP", "CARD_GAP", "RETURNS_GAP", "CHIP_GAP",
    "RADIUS_HERO", "RADIUS_PANEL",
    "FS_HERO", "FS_TITLE", "FS_BODY", "FS_LABEL", "FS_META",
    "FS_SECTION", "FS_CONFIDENCE",
    "SHADOW_SOFT_RADIUS", "SHADOW_SOFT_ALPHA", "SHADOW_SOFT_OFFSET",
    "SHADOW_LIFT_RADIUS", "SHADOW_LIFT_ALPHA", "SHADOW_LIFT_OFFSET",
    "SHADOW_CARD_RADIUS", "SHADOW_CARD_OFFSET", "SHADOW_CARD_ALPHA",
    "SHADOW_SEARCH_RADIUS", "SHADOW_SEARCH_OFFSET", "SHADOW_SEARCH_ALPHA",
]
