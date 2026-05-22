"""Centralized theme tokens and stylesheets.

Iterating on look-and-feel happens here so widgets stay free of magic
colors. The launcher uses a translucent rgba background so the OS shows
through subtly — combined with a thin border and rounded corners, this
gives the launcher a floating, glass-like appearance without
platform-specific blur APIs.
"""

# Phase 6B — Launcher Identity. The palette inverts from dark to
# warm white + lavender. Same names; new values. Every widget that
# reads from these tokens shifts to the light theme automatically;
# any widget with hardcoded hex colors needs a follow-up sweep
# (tracked in PHASE_6B_STATUS.md).
#
# The values mirror the extension popup's `styles.css` design tokens
# so the desktop launcher and the browser popup now share one visual
# language. The accent (lavender) is used **once per visible
# surface** — on resume / focus / selected only.
BG = "#fbf7f4"           # warm off-white (cream, not gray)
BG_RAISED = "#ffffff"    # card surface
BG_HOVER = "#f4efea"     # hover / elevated row
BG_SELECTED = "#ede9fb"  # accent-soft for selected list item
BORDER = "#e8e2dc"       # soft hairline on warm-white
TEXT = "#16112b"         # warm dark ink
TEXT_DIM = "#4a4458"
TEXT_DIMMER = "#847b8e"
HIGHLIGHT = "#16112b"    # bolded query terms inside the snippet
ACCENT = "#8b7fe3"       # lavender (matches extension --accent)
ACCENT_DIM = "#ede9fb"   # soft accent fill (matches --accent-soft)


# ── Phase 5I visual tokens ──────────────────────────────────────────
# Single source for the launcher's surface / border / shadow / motion
# vocabulary. Components reach for these names instead of magic
# numbers. The extension popup mirrors them in `styles.css` so the
# two surfaces share the same elevation + timing grammar.

# Surface elevations (three tiers).
SURFACE_0 = BG          # the launcher backdrop
SURFACE_1 = BG_RAISED   # cards
SURFACE_2 = BG_HOVER    # hover / elevated state

# Border weights (two).
BORDER_SOFT = BORDER
BORDER_STRONG = "#d4ccc4"

# Shadow recipes — used as drawShadow alpha in the painter, since Qt
# doesn't apply CSS box-shadow to QWidget. Tuple shape:
#   (offset_y_px, blur_px, alpha_0_255)
SHADOW_SOFT = (2, 10, 26)
SHADOW_ELEVATED = (4, 18, 48)

# Motion — milliseconds. Mirrors styles.css `--motion-*`.
MOTION_FAST_MS = 120     # hover, fade
MOTION_NORMAL_MS = 180   # expand, slide
MOTION_SLOW_MS = 220     # recovery open


# Phase 6B — Launcher Identity. Warm white surface, soft glass card,
# lavender accent used once per surface (resume / focus / selected).
# Spacing rhythm follows the directive: 24 outer, 18 between sections,
# 12 inner. Border radius 18-24 px on the floating card; 10-12 px on
# row hover.
LAUNCHER_QSS = f"""
* {{
    font-family: "Segoe UI", "SF Pro Text", "Inter", "Cantarell", "Helvetica Neue", sans-serif;
}}
QWidget#launcher {{
    background: transparent;
    border: none;
}}
QWidget#launcher_card {{
    /* Floating glass surface. rgba 255 white at 72 % alpha so the
       OS desktop bleeds through softly; combined with a 1 px warm
       hairline and a 22 px radius, the card reads as a memory
       surface, not a desktop utility. The drop shadow is applied
       in code (QGraphicsDropShadowEffect) - QSS would clip it. */
    background: rgba(255, 255, 255, 184);
    border: 1px solid rgba(24, 17, 45, 30);
    border-radius: 22px;
}}
QLineEdit#search {{
    background: transparent;
    border: none;
    color: {TEXT};
    font-size: 15px;
    padding: 0 24px;
    selection-background-color: {ACCENT_DIM};
}}
QLineEdit#search:focus {{ outline: none; }}
QListWidget#results {{
    background: transparent;
    border: none;
    border-top: 1px solid rgba(24, 17, 45, 18);
    color: {TEXT};
    outline: 0;
    padding: 6px 6px;
}}
QListWidget#results::item {{
    background: transparent;
    border-radius: 10px;
    padding: 0;
    margin: 2px 6px;
}}
QListWidget#results::item:selected {{
    background: {BG_SELECTED};
    color: {TEXT};
}}
QListWidget#results::item:hover {{
    background: {BG_HOVER};
}}
QLabel#hint {{
    color: {TEXT_DIM};
    font-size: 12px;
    padding: 0 24px;
}}
QLabel#empty_title {{
    color: {TEXT};
    font-size: 14.5px;
    font-weight: 600;
    letter-spacing: -0.1px;
    padding: 0 24px 4px 24px;
}}
QLabel#empty_body {{
    color: {TEXT_DIM};
    font-size: 12px;
    line-height: 1.55;
    padding: 0 28px;
}}
QLabel#footer {{
    color: {TEXT_DIMMER};
    font-size: 10.5px;
    padding: 0 24px;
    border-top: 1px solid rgba(24, 17, 45, 18);
    background: rgba(244, 239, 234, 140);
}}
QWidget#preview_pane {{
    background: rgba(244, 239, 234, 140);
    border-left: 1px solid rgba(24, 17, 45, 22);
}}
QLabel#preview_filename {{
    color: {TEXT};
    font-size: 13.5px;
    font-weight: 600;
    letter-spacing: -0.1px;
}}
QLabel#preview_path {{
    color: {TEXT_DIMMER};
    font-size: 10.5px;
}}
QFrame#preview_divider {{
    background: rgba(24, 17, 45, 18);
    border: none;
    max-height: 1px;
    min-height: 1px;
}}
QLabel#preview_why {{
    color: {TEXT};
    font-size: 11.5px;
    font-weight: 500;
}}
QLabel#preview_excerpt {{
    color: {TEXT_DIM};
    font-size: 11.5px;
    line-height: 1.55;
    font-style: italic;
}}
QScrollArea#preview_scroll {{
    background: transparent;
    border: none;
}}
QScrollArea#preview_scroll > QWidget > QWidget {{
    background: transparent;
}}
QLabel#preview_section_label {{
    color: {TEXT_DIMMER};
    font-size: 9.5px;
    font-weight: 600;
    letter-spacing: 0.6px;
    text-transform: uppercase;
}}
QLabel#preview_last_seen {{
    color: {TEXT_DIMMER};
    font-size: 10.5px;
    font-style: italic;
}}
QLabel#preview_cross_source {{
    color: {ACCENT};
    font-size: 10.5px;
    font-weight: 500;
    letter-spacing: 0.2px;
}}
QListWidget#digest {{
    background: transparent;
    border: none;
    color: {TEXT};
    outline: 0;
    padding: 6px 8px;
}}
QListWidget#digest::item {{
    background: transparent;
    border-radius: 10px;
    padding: 0;
    margin: 2px 6px;
}}
QListWidget#digest::item:selected {{
    background: {BG_SELECTED};
}}
QListWidget#digest::item:hover {{
    /* Calmness rule: a hover should whisper, not light up. On
       warm-white the hover is a faint accent-tinted fill - softer
       than BG_HOVER alone, which would read as a beige flash. */
    background: rgba(139, 127, 227, 18);
}}
QLabel#digest_section {{
    color: {TEXT_DIMMER};
    font-size: 10.5px;
    font-weight: 600;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    /* Spacing rhythm (directive): 18 px between sections, so the
       section label sits 18 px below the previous card row and
       6 px above its own list. */
    padding: 18px 24px 6px 24px;
}}
QLabel#preview_related_row {{
    color: {TEXT_DIM};
    font-size: 11px;
    padding: 1px 0;
}}
QLabel#preview_related_empty {{
    color: {TEXT_DIMMER};
    font-size: 10.5px;
    font-style: italic;
}}
QLabel#preview_empty {{
    color: {TEXT_DIMMER};
    font-size: 12px;
    font-style: italic;
    padding: 56px 20px;
    qproperty-alignment: AlignCenter;
}}
QScrollBar:vertical {{
    background: transparent; width: 7px; margin: 6px;
}}
QScrollBar::handle:vertical {{
    background: rgba(139, 127, 227, 56); border-radius: 4px; min-height: 24px;
}}
QScrollBar::handle:vertical:hover {{
    background: rgba(139, 127, 227, 92);
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}

/* Phase 6B — the soft "Show example" pill button on the redesigned
   empty state. Lavender accent fill at low alpha; on hover the fill
   strengthens; never a solid lavender block. */
QPushButton#example_button {{
    background: {ACCENT_DIM};
    color: {ACCENT};
    border: 1px solid rgba(139, 127, 227, 70);
    border-radius: 9px;
    padding: 9px 18px;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.2px;
}}
QPushButton#example_button:hover {{
    background: rgba(139, 127, 227, 60);
}}
/* Phase 6D - the quiet "Start normally" decline that sits next to
   Show example. Transparent fill + the same warm hairline as a card
   border so it reads as a refusal, never as a peer CTA. */
QPushButton#secondary_button {{
    background: transparent;
    color: {TEXT_DIM};
    border: 1px solid {BORDER};
    border-radius: 9px;
    padding: 9px 16px;
    font-size: 12px;
    font-weight: 500;
}}
QPushButton#secondary_button:hover {{
    background: {BG_HOVER};
    color: {TEXT};
}}
"""


SETTINGS_QSS = f"""
* {{
    font-family: "Segoe UI", "SF Pro Text", "Inter", "Cantarell", "Helvetica Neue", sans-serif;
}}
QDialog {{ background: {BG}; color: {TEXT}; }}
QLabel {{ color: {TEXT}; font-size: 13px; }}
QLabel#settings_title {{
    font-size: 18px;
    font-weight: 600;
    letter-spacing: -0.1px;
}}
QLabel#settings_subtitle {{
    color: {TEXT_DIM};
    font-size: 12px;
}}
QLabel#section {{
    color: {TEXT_DIMMER};
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.7px;
    padding-top: 6px;
}}
QListWidget {{
    background: {BG_RAISED};
    border: 1px solid {BORDER};
    border-radius: 10px;
    color: {TEXT};
    padding: 6px;
}}
QListWidget::item {{ padding: 8px; border-radius: 5px; }}
QListWidget::item:selected {{ background: {BG_SELECTED}; }}
QPushButton {{
    background: {BG_RAISED};
    color: {TEXT};
    border: 1px solid {BORDER};
    border-radius: 7px;
    padding: 8px 16px;
    font-size: 12px;
}}
QPushButton:hover {{ background: {BG_HOVER}; border-color: {ACCENT_DIM}; }}
QPushButton:disabled {{ color: {TEXT_DIMMER}; }}
QPushButton#primary {{
    background: {ACCENT_DIM};
    border-color: {ACCENT};
    color: {TEXT};
    font-weight: 600;
}}
QPushButton#primary:hover {{ background: {ACCENT}; }}
QProgressBar {{
    background: {BG_RAISED};
    border: 1px solid {BORDER};
    border-radius: 6px;
    text-align: center;
    color: {TEXT};
    height: 14px;
}}
QProgressBar::chunk {{ background: {ACCENT}; border-radius: 5px; }}
QCheckBox {{ color: {TEXT}; font-size: 12px; spacing: 10px; }}
QCheckBox::indicator {{
    width: 16px; height: 16px;
    border: 1px solid {BORDER};
    border-radius: 4px;
    background: {BG_RAISED};
}}
QCheckBox::indicator:checked {{
    background: {ACCENT};
    border-color: {ACCENT};
}}
QCheckBox:disabled {{ color: {TEXT_DIMMER}; }}
"""
