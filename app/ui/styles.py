"""Centralized theme tokens and stylesheets.

Iterating on look-and-feel happens here so widgets stay free of magic
colors. The launcher uses a translucent rgba background so the OS shows
through subtly — combined with a thin border and rounded corners, this
gives the launcher a floating, glass-like appearance without
platform-specific blur APIs.
"""

# Palette — dark, near-neutral with a single accent for selection / score
BG = "#0f1115"
BG_RAISED = "#161922"
BG_HOVER = "#1c202b"
BG_SELECTED = "#252a3a"
BORDER = "#262a36"
TEXT = "#e8eaf0"
TEXT_DIM = "#9097a8"
TEXT_DIMMER = "#5a6072"
HIGHLIGHT = "#cdd2e0"   # bolded query terms inside the snippet
ACCENT = "#8b9bff"
ACCENT_DIM = "#3b4566"


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
BORDER_STRONG = "#3a4055"

# Shadow recipes — used as drawShadow alpha in the painter, since Qt
# doesn't apply CSS box-shadow to QWidget. Tuple shape:
#   (offset_y_px, blur_px, alpha_0_255)
SHADOW_SOFT = (2, 10, 26)
SHADOW_ELEVATED = (4, 18, 48)

# Motion — milliseconds. Mirrors styles.css `--motion-*`.
MOTION_FAST_MS = 120     # hover, fade
MOTION_NORMAL_MS = 180   # expand, slide
MOTION_SLOW_MS = 220     # recovery open


# rgba colors used in the launcher QSS — tuned for translucency.
# A system-font stack means the launcher inherits the host OS's native
# UI font (Segoe UI on Windows, San Francisco on macOS, Inter / Cantarell
# on Linux) — quietly more native than hard-coding one face.
LAUNCHER_QSS = f"""
* {{
    font-family: "Segoe UI", "SF Pro Text", "Inter", "Cantarell", "Helvetica Neue", sans-serif;
}}
QWidget#launcher {{
    background: transparent;
    border: none;
}}
QWidget#launcher_card {{
    background: rgba(15, 17, 21, 232);
    border: 1px solid rgba(75, 80, 95, 55);
    border-radius: 13px;
}}
QLineEdit#search {{
    background: transparent;
    border: none;
    color: {TEXT};
    font-size: 15px;
    padding: 0 18px;
    selection-background-color: {ACCENT_DIM};
}}
QLineEdit#search:focus {{ outline: none; }}
QListWidget#results {{
    background: transparent;
    border: none;
    border-top: 1px solid rgba(50, 55, 70, 45);
    color: {TEXT};
    outline: 0;
    padding: 5px 5px;
}}
QListWidget#results::item {{
    background: transparent;
    border-radius: 8px;
    padding: 0;
    margin: 1px 4px;
}}
QListWidget#results::item:selected {{
    background: rgba(73, 85, 130, 155);
    color: {TEXT};
}}
QListWidget#results::item:hover {{
    background: rgba(36, 42, 56, 75);
}}
QLabel#hint {{
    color: {TEXT_DIM};
    font-size: 12px;
    padding: 0 18px;
}}
QLabel#empty_title {{
    color: {TEXT};
    font-size: 13.5px;
    font-weight: 600;
    padding: 0 18px 4px 18px;
}}
QLabel#empty_body {{
    color: {TEXT_DIM};
    font-size: 11.5px;
    padding: 0 22px;
}}
QLabel#footer {{
    color: {TEXT_DIMMER};
    font-size: 10.5px;
    padding: 0 16px;
    border-top: 1px solid rgba(50, 55, 70, 45);
    background: rgba(20, 23, 30, 70);
}}
QWidget#preview_pane {{
    background: rgba(20, 23, 30, 70);
    border-left: 1px solid rgba(50, 55, 70, 60);
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
    background: rgba(50, 55, 70, 45);
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
    padding: 4px 4px;
}}
QListWidget#digest::item {{
    background: transparent;
    border-radius: 6px;
    padding: 0;
    margin: 1px 4px;
}}
QListWidget#digest::item:selected {{
    background: rgba(50, 56, 78, 120);
}}
QListWidget#digest::item:hover {{
    /* Phase 4I calmness — a hover should whisper, not light up.
       Softened so passing the cursor over the digest does not
       make the surface flicker with energy. */
    background: rgba(36, 42, 56, 55);
}}
QLabel#digest_section {{
    color: {TEXT_DIMMER};
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.9px;
    text-transform: uppercase;
    /* Phase 4I — vertical rhythm. Generous top padding gives each
       digest tier real breathing room so the surface reads as a
       few calm zones rather than one dense list. */
    padding: 18px 20px 6px 20px;
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
    background: transparent; width: 6px; margin: 4px;
}}
QScrollBar::handle:vertical {{
    background: rgba(80, 85, 100, 70); border-radius: 3px; min-height: 24px;
}}
QScrollBar::handle:vertical:hover {{
    background: rgba(110, 115, 130, 110);
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
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
