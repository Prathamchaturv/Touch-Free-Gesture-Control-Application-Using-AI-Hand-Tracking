"""
ui/styles.py — MMGI Premium QSS Dark Theme
AI Dashboard aesthetic: deep dark backgrounds, neon‑blue accents, glass cards.
"""

# ──────────────────────────────────────────────────────────────────────────────
# Colour palette
# ──────────────────────────────────────────────────────────────────────────────
BG_DEEP      = "#0F0F14"
BG_CARD      = "#1A1A22"
BG_CARD_ALT  = "#14141C"
BG_HOVER     = "#22222E"
ACCENT       = "#00E5FF"
ACCENT_DIM   = "#0099BB"
ACCENT_GLOW  = "rgba(0, 229, 255, 60)"
GREEN_ACTIVE = "#00FF88"
RED_INACTIVE = "#FF4466"
TEXT_PRIMARY  = "#E8E8F0"
TEXT_SECONDARY = "#8888AA"
TEXT_MUTED    = "#505060"
BORDER        = "#2A2A38"
BORDER_ACCENT = "#00E5FF"

# ──────────────────────────────────────────────────────────────────────────────
# Main QSS stylesheet
# ──────────────────────────────────────────────────────────────────────────────
DARK_QSS = f"""

/* ── Global ────────────────────────────────────────────────────────────────── */

* {{
    font-family: 'Segoe UI', 'Inter', 'Arial', sans-serif;
    color: {TEXT_PRIMARY};
    outline: none;
}}

QMainWindow {{
    background-color: {BG_DEEP};
}}

QWidget {{
    background-color: transparent;
}}

QScrollArea {{
    background-color: transparent;
    border: none;
}}

QScrollBar:horizontal {{
    background: {BG_CARD};
    height: 6px;
    border-radius: 3px;
}}
QScrollBar::handle:horizontal {{
    background: {ACCENT_DIM};
    border-radius: 3px;
    min-width: 30px;
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0px;
}}

QScrollBar:vertical {{
    background: {BG_CARD};
    width: 6px;
    border-radius: 3px;
}}
QScrollBar::handle:vertical {{
    background: {ACCENT_DIM};
    border-radius: 3px;
    min-height: 30px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

/* ── Header ─────────────────────────────────────────────────────────────────── */

QFrame#headerFrame {{
    background-color: {BG_CARD};
    border-bottom: 1px solid {BORDER};
    min-height: 56px;
    max-height: 56px;
}}

QLabel#appTitle {{
    font-size: 18px;
    font-weight: 700;
    letter-spacing: 2px;
    color: {ACCENT};
}}

QLabel#appSubtitle {{
    font-size: 11px;
    color: {TEXT_SECONDARY};
    letter-spacing: 1px;
}}

/* ── Sidebar ─────────────────────────────────────────────────────────────────── */

QFrame#sidebarFrame {{
    background-color: {BG_CARD_ALT};
    border-right: 1px solid {BORDER};
}}

QPushButton#navButton {{
    background-color: transparent;
    border: none;
    border-radius: 10px;
    text-align: left;
    padding: 10px 14px;
    font-size: 13px;
    color: {TEXT_SECONDARY};
    min-height: 40px;
}}

QPushButton#navButton:hover {{
    background-color: {BG_HOVER};
    color: {ACCENT};
}}

QPushButton#navButton:checked {{
    background-color: rgba(0, 229, 255, 18);
    color: {ACCENT};
    border-left: 3px solid {ACCENT};
}}

QPushButton#collapseBtn {{
    background-color: transparent;
    border: 1px solid {BORDER};
    border-radius: 8px;
    color: {TEXT_SECONDARY};
    font-size: 14px;
    min-width: 32px;
    max-width: 32px;
    min-height: 32px;
    max-height: 32px;
}}
QPushButton#collapseBtn:hover {{
    background-color: {BG_HOVER};
    color: {ACCENT};
    border-color: {ACCENT_DIM};
}}

/* ── Cards ───────────────────────────────────────────────────────────────────── */

QFrame#card {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 14px;
}}

QFrame#cardActive {{
    background-color: {BG_CARD};
    border: 1px solid {ACCENT};
    border-radius: 14px;
}}

QLabel#cardTitle {{
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 2px;
    color: {TEXT_MUTED};
    text-transform: uppercase;
}}

QLabel#cardValue {{
    font-size: 22px;
    font-weight: 700;
    color: {TEXT_PRIMARY};
}}

QLabel#cardValueAccent {{
    font-size: 22px;
    font-weight: 700;
    color: {ACCENT};
}}

QLabel#cardValueGreen {{
    font-size: 14px;
    font-weight: 600;
    color: {GREEN_ACTIVE};
}}

QLabel#cardValueRed {{
    font-size: 14px;
    font-weight: 600;
    color: {RED_INACTIVE};
}}

QLabel#metricLabel {{
    font-size: 11px;
    color: {TEXT_SECONDARY};
}}

QLabel#metricValue {{
    font-size: 13px;
    font-weight: 600;
    color: {TEXT_PRIMARY};
}}

/* ── Vision Panel ────────────────────────────────────────────────────────────── */

QFrame#visionCard {{
    background-color: {BG_CARD_ALT};
    border: 2px solid {BORDER};
    border-radius: 16px;
}}

QFrame#visionCardActive {{
    background-color: {BG_CARD_ALT};
    border: 2px solid {ACCENT};
    border-radius: 16px;
}}

QLabel#cameraFeed {{
    background-color: #080810;
    border-radius: 12px;
    color: {TEXT_MUTED};
    font-size: 14px;
}}

QFrame#overlayBar {{
    background-color: rgba(15, 15, 20, 210);
    border-radius: 10px;
}}

QLabel#overlayLabel {{
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 1px;
    color: {TEXT_SECONDARY};
}}

QLabel#overlayValue {{
    font-size: 14px;
    font-weight: 700;
    color: {ACCENT};
}}

QLabel#overlayValueGreen {{
    font-size: 14px;
    font-weight: 700;
    color: {GREEN_ACTIVE};
}}

QLabel#overlayValueRed {{
    font-size: 14px;
    font-weight: 700;
    color: {RED_INACTIVE};
}}

/* ── Progress Bars ────────────────────────────────────────────────────────────── */

QProgressBar {{
    background-color: {BG_DEEP};
    border: none;
    border-radius: 4px;
    height: 6px;
    text-align: center;
    font-size: 0px;
}}

QProgressBar::chunk {{
    background-color: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 {ACCENT_DIM},
        stop:1 {ACCENT}
    );
    border-radius: 4px;
}}

QProgressBar#stabilityBar::chunk {{
    background-color: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 #00AA66,
        stop:1 {GREEN_ACTIVE}
    );
    border-radius: 4px;
}}

QProgressBar#cooldownBar::chunk {{
    background-color: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 #AA4400,
        stop:1 #FF8800
    );
    border-radius: 4px;
}}

/* ── Timeline / Log ──────────────────────────────────────────────────────────── */

QFrame#timelineFrame {{
    background-color: {BG_CARD};
    border-top: 1px solid {BORDER};
    min-height: 70px;
    max-height: 70px;
}}

QFrame#logPill {{
    background-color: {BG_HOVER};
    border: 1px solid {BORDER};
    border-radius: 20px;
    padding: 4px 10px;
}}

QLabel#logText {{
    font-size: 12px;
    color: {TEXT_SECONDARY};
    white-space: nowrap;
}}

QLabel#logAccent {{
    font-size: 12px;
    font-weight: 600;
    color: {ACCENT};
    white-space: nowrap;
}}

/* ── Divider ──────────────────────────────────────────────────────────────────── */

QFrame#divider {{
    background-color: {BORDER};
    max-height: 1px;
    min-height: 1px;
}}

"""
