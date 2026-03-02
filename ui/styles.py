"""
ui/styles.py - Global QSS stylesheet and colour tokens for the MMGI dashboard.

Colour system
-------------
BG_DEEP    #0F0F14   – window background
BG_CARD    #1A1A22   – card / panel background
BG_HOVER   #22222E   – hovered card
BORDER     #2A2A3A   – subtle separator
ACCENT     #00E5FF   – neon cyan (primary interactive)
ACTIVE     #00FF88   – neon green (system active)
INACTIVE   #FF4466   – neon red  (system inactive / error)
TEXT_PRI   #E8E8F0   – primary text
TEXT_SEC   #8A8AA0   – secondary / muted text
TEXT_HINT  #505068   – ghost / placeholder
"""

# ---------------------------------------------------------------------------
# Colour tokens
# ---------------------------------------------------------------------------

BG_DEEP   = '#0F0F14'
BG_CARD   = '#1A1A22'
BG_HOVER  = '#22222E'
BORDER    = '#2A2A3A'
ACCENT    = '#00E5FF'
ACTIVE    = '#00FF88'
INACTIVE  = '#FF4466'
TEXT_PRI  = '#E8E8F0'
TEXT_SEC  = '#8A8AA0'
TEXT_HINT = '#505068'

MODE_APP    = '#00E5FF'   # cyan
MODE_MEDIA  = '#00BFFF'   # deep sky blue
MODE_SYSTEM = '#8A7CFF'   # violet

# ---------------------------------------------------------------------------
# Global QSS
# ---------------------------------------------------------------------------

GLOBAL_QSS = f"""
/* ─── Window ─────────────────────────────────────────── */
QMainWindow, QWidget {{
    background-color: {BG_DEEP};
    color: {TEXT_PRI};
    font-family: "Segoe UI", "Inter", sans-serif;
    font-size: 13px;
}}

/* ─── Scrollbars ─────────────────────────────────────── */
QScrollBar:vertical {{
    background: {BG_CARD};
    width: 6px;
    margin: 0;
    border-radius: 3px;
}}
QScrollBar::handle:vertical {{
    background: {BORDER};
    border-radius: 3px;
    min-height: 24px;
}}
QScrollBar::handle:vertical:hover {{
    background: {ACCENT};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}

QScrollBar:horizontal {{
    background: {BG_CARD};
    height: 6px;
    border-radius: 3px;
}}
QScrollBar::handle:horizontal {{
    background: {BORDER};
    border-radius: 3px;
    min-width: 24px;
}}
QScrollBar::handle:horizontal:hover {{
    background: {ACCENT};
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0;
}}

/* ─── Generic card frame ─────────────────────────────── */
QFrame#card {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 15px;
}}

/* ─── Labels ─────────────────────────────────────────── */
QLabel#section_title {{
    color: {ACCENT};
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 2px;
}}
QLabel#value_large {{
    color: {TEXT_PRI};
    font-size: 28px;
    font-weight: 700;
}}
QLabel#value_small {{
    color: {TEXT_SEC};
    font-size: 12px;
}}

/* ─── Toggle button ──────────────────────────────────── */
QPushButton#toggle_btn {{
    background-color: {INACTIVE};
    color: {BG_DEEP};
    border: none;
    border-radius: 20px;
    padding: 8px 24px;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 1px;
}}
QPushButton#toggle_btn:hover {{
    background-color: #ff6680;
}}
QPushButton#toggle_btn[active="true"] {{
    background-color: {ACTIVE};
}}
QPushButton#toggle_btn[active="true"]:hover {{
    background-color: #33ffaa;
}}

/* ─── Sidebar nav buttons ────────────────────────────── */
QPushButton#nav_btn {{
    background: transparent;
    color: {TEXT_SEC};
    border: none;
    border-radius: 10px;
    padding: 10px 16px;
    text-align: left;
    font-size: 13px;
}}
QPushButton#nav_btn:hover {{
    background-color: {BG_HOVER};
    color: {TEXT_PRI};
}}
QPushButton#nav_btn[selected="true"] {{
    background-color: rgba(0,229,255,0.12);
    color: {ACCENT};
    font-weight: 600;
}}

/* ─── Progress bars ──────────────────────────────────── */
QProgressBar {{
    background-color: {BORDER};
    border-radius: 4px;
    border: none;
    height: 6px;
    text-align: center;
    color: transparent;
}}
QProgressBar::chunk {{
    background-color: {ACCENT};
    border-radius: 4px;
}}
QProgressBar#stability_bar::chunk {{
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {ACTIVE}, stop:1 {ACCENT});
}}

/* ─── Tooltip ────────────────────────────────────────── */
QToolTip {{
    background-color: {BG_CARD};
    color: {TEXT_PRI};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 4px 8px;
}}
"""
