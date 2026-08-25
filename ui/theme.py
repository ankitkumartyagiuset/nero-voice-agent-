"""
Futuristic Cyberpunk / Sci-Fi HUD Theme tokens and stylesheet for NERO.
Cyan, Neon Blue, Magenta, Glassmorphism, and glowing borders.
"""

# Color Palette
CYAN = "#00f0ff"
CYAN_GLOW = "rgba(0, 240, 255, 0.4)"
CYAN_DARK = "#008a94"

MAGENTA = "#ff007f"
MAGENTA_GLOW = "rgba(255, 0, 127, 0.4)"

PURPLE = "#9d00ff"
PURPLE_GLOW = "rgba(157, 0, 255, 0.35)"

NEON_BLUE = "#0070f3"
ORANGE_ALERT = "#ff9900"
GREEN_SUCCESS = "#00ff88"
RED_ERROR = "#ff3344"

BG_DARK = "#060b18"
BG_CARD = "rgba(10, 18, 38, 0.75)"
BG_CARD_BORDER = "rgba(0, 240, 255, 0.25)"
BG_HOVER = "rgba(0, 240, 255, 0.12)"

TEXT_PRIMARY = "#ffffff"
TEXT_SECONDARY = "#8fa3bf"
TEXT_MUTED = "#4f637e"
TEXT_CYAN = "#00f0ff"
TEXT_MAGENTA = "#ff007f"

# Master Application QSS Stylesheet
MAIN_STYLESHEET = f"""
QMainWindow {{
    background-color: {BG_DARK};
    color: {TEXT_PRIMARY};
}}

QWidget {{
    font-family: 'Segoe UI', 'Roboto', 'Arial', sans-serif;
    color: {TEXT_PRIMARY};
}}

/* Glass Panel Card */
QFrame#GlassPanel {{
    background-color: {BG_CARD};
    border: 1px solid {BG_CARD_BORDER};
    border-radius: 12px;
}}

/* Header labels */
QLabel#PanelTitle {{
    font-size: 13px;
    font-weight: bold;
    letter-spacing: 2px;
    color: {TEXT_CYAN};
    text-transform: uppercase;
}}

/* Normal labels */
QLabel {{
    font-size: 13px;
    color: {TEXT_PRIMARY};
}}

QLabel#SubtleLabel {{
    font-size: 11px;
    color: {TEXT_SECONDARY};
    letter-spacing: 0.5px;
}}

/* Futuristic Buttons */
QPushButton {{
    background-color: rgba(0, 240, 255, 0.08);
    border: 1px solid rgba(0, 240, 255, 0.3);
    border-radius: 8px;
    color: {CYAN};
    font-size: 12px;
    font-weight: 600;
    padding: 8px 14px;
    letter-spacing: 0.5px;
}}

QPushButton:hover {{
    background-color: rgba(0, 240, 255, 0.2);
    border: 1px solid {CYAN};
    color: #ffffff;
}}

QPushButton:pressed {{
    background-color: rgba(0, 240, 255, 0.35);
}}

/* Danger Action Button */
QPushButton#DangerButton {{
    background-color: rgba(255, 51, 68, 0.1);
    border: 1px solid rgba(255, 51, 68, 0.4);
    color: #ff5566;
}}

QPushButton#DangerButton:hover {{
    background-color: rgba(255, 51, 68, 0.25);
    border: 1px solid #ff3344;
    color: #ffffff;
}}

/* Automation Switch Button */
QPushButton#AutomationButtonActive {{
    background-color: rgba(0, 255, 136, 0.15);
    border: 1px solid {GREEN_SUCCESS};
    color: {GREEN_SUCCESS};
}}

/* Sliders */
QSlider::groove:horizontal {{
    height: 6px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 3px;
}}

QSlider::sub-page:horizontal {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {CYAN}, stop:1 {NEON_BLUE});
    border-radius: 3px;
}}

QSlider::handle:horizontal {{
    background: #ffffff;
    border: 2px solid {CYAN};
    width: 14px;
    height: 14px;
    margin-top: -4px;
    margin-bottom: -4px;
    border-radius: 7px;
}}

/* Scrollbars */
QScrollBar:vertical {{
    background: rgba(0, 0, 0, 0.2);
    width: 6px;
    border-radius: 3px;
}}

QScrollBar::handle:vertical {{
    background: rgba(0, 240, 255, 0.25);
    border-radius: 3px;
    min-height: 20px;
}}

QScrollBar::handle:vertical:hover {{
    background: {CYAN};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

/* Text / Input fields */
QLineEdit, QTextEdit, QPlainTextEdit {{
    background-color: rgba(5, 10, 22, 0.7);
    border: 1px solid rgba(0, 240, 255, 0.25);
    border-radius: 8px;
    padding: 8px;
    color: #ffffff;
    font-size: 13px;
    selection-background-color: {CYAN_DARK};
}}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
    border: 1px solid {CYAN};
}}
"""
