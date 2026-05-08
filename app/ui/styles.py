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
    background: rgba(15, 17, 21, 240);
    border: 1px solid rgba(75, 80, 95, 90);
    border-radius: 16px;
}}
QLineEdit#search {{
    background: transparent;
    border: none;
    color: {TEXT};
    font-size: 17px;
    padding: 0 24px;
    selection-background-color: {ACCENT_DIM};
}}
QLineEdit#search:focus {{ outline: none; }}
QListWidget#results {{
    background: transparent;
    border: none;
    border-top: 1px solid rgba(50, 55, 70, 70);
    color: {TEXT};
    outline: 0;
    padding: 8px 8px;
}}
QListWidget#results::item {{
    background: transparent;
    border-radius: 10px;
    padding: 0;
    margin: 2px 4px;
}}
QListWidget#results::item:selected {{
    background: rgba(50, 56, 78, 150);
    color: {TEXT};
}}
QListWidget#results::item:hover {{
    background: rgba(36, 42, 56, 100);
}}
QLabel#hint {{
    color: {TEXT_DIM};
    font-size: 13px;
    padding: 0 24px;
}}
QLabel#empty_title {{
    color: {TEXT};
    font-size: 16px;
    font-weight: 600;
    padding: 0 24px 6px 24px;
}}
QLabel#empty_body {{
    color: {TEXT_DIM};
    font-size: 12px;
    padding: 0 24px;
}}
QLabel#footer {{
    color: {TEXT_DIMMER};
    font-size: 11px;
    padding: 0 24px;
    border-top: 1px solid rgba(50, 55, 70, 70);
    background: rgba(22, 25, 34, 110);
}}
QWidget#preview_pane {{
    background: rgba(22, 25, 34, 90);
    border-left: 1px solid rgba(50, 55, 70, 70);
}}
QLabel#preview_filename {{
    color: {TEXT};
    font-size: 16px;
    font-weight: 600;
    letter-spacing: -0.1px;
}}
QLabel#preview_path {{
    color: {TEXT_DIMMER};
    font-size: 11px;
}}
QFrame#preview_divider {{
    background: rgba(50, 55, 70, 70);
    border: none;
    max-height: 1px;
    min-height: 1px;
}}
QLabel#preview_why {{
    color: {TEXT};
    font-size: 12px;
    font-weight: 500;
}}
QLabel#preview_excerpt {{
    color: {TEXT_DIM};
    font-size: 12px;
    line-height: 1.65;
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
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.7px;
}}
QLabel#preview_last_seen {{
    color: {TEXT_DIMMER};
    font-size: 11px;
    font-style: italic;
}}
QLabel#preview_cross_source {{
    color: {ACCENT};
    font-size: 11px;
    font-weight: 500;
    letter-spacing: 0.2px;
}}
QListWidget#digest {{
    background: transparent;
    border: none;
    color: {TEXT};
    outline: 0;
    padding: 6px 6px;
}}
QListWidget#digest::item {{
    background: transparent;
    border-radius: 8px;
    padding: 0;
    margin: 1px 6px;
}}
QListWidget#digest::item:selected {{
    background: rgba(50, 56, 78, 160);
}}
QListWidget#digest::item:hover {{
    background: rgba(36, 42, 56, 130);
}}
QLabel#digest_section {{
    color: {TEXT_DIM};
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.2px;
    padding: 10px 22px 6px 22px;
}}
QLabel#preview_related_header {{
    color: {TEXT};
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.4px;
    text-transform: uppercase;
}}
QLabel#preview_related_row {{
    color: {TEXT_DIM};
    font-size: 12px;
    padding: 1px 0;
}}
QLabel#preview_related_empty {{
    color: {TEXT_DIMMER};
    font-size: 11px;
    font-style: italic;
}}
QScrollBar:vertical {{
    background: transparent; width: 8px; margin: 4px;
}}
QScrollBar::handle:vertical {{
    background: rgba(80, 85, 100, 90); border-radius: 4px; min-height: 24px;
}}
QScrollBar::handle:vertical:hover {{
    background: rgba(110, 115, 130, 130);
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
