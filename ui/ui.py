"""
ui/ui.py - MMGI PyQt6 Dashboard (consolidated UI module)

Contains all UI components:
  - Colour tokens & global QSS  (formerly styles.py)
  - ActivityLog widget           (formerly activity_log.py)
  - Sidebar widget               (formerly sidebar.py)
  - VisionPanel widget           (formerly vision_panel.py)
  - SystemCard / ModeCard / PerformanceCard / SystemPanel  (formerly system_panel.py)
  - MainWindow                   (formerly main_window.py)

Entry point:
    from ui.ui import MainWindow
"""

from __future__ import annotations

# ===========================================================================
# Colour tokens & global QSS  (was ui/styles.py)
# ===========================================================================

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

MODE_APP    = '#00E5FF'
MODE_MEDIA  = '#00BFFF'
MODE_SYSTEM = '#8A7CFF'

GLOBAL_QSS = f"""
QMainWindow, QWidget {{
    background-color: {BG_DEEP};
    color: {TEXT_PRI};
    font-family: "Segoe UI", "Inter", sans-serif;
    font-size: 13px;
}}
QScrollBar:vertical {{
    background: {BG_CARD}; width: 6px; margin: 0; border-radius: 3px;
}}
QScrollBar::handle:vertical {{
    background: {BORDER}; border-radius: 3px; min-height: 24px;
}}
QScrollBar::handle:vertical:hover {{ background: {ACCENT}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QScrollBar:horizontal {{
    background: {BG_CARD}; height: 6px; border-radius: 3px;
}}
QScrollBar::handle:horizontal {{
    background: {BORDER}; border-radius: 3px; min-width: 24px;
}}
QScrollBar::handle:horizontal:hover {{ background: {ACCENT}; }}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}
QFrame#card {{
    background-color: {BG_CARD}; border: 1px solid {BORDER}; border-radius: 15px;
}}
QLabel#section_title {{ color: {ACCENT}; font-size: 11px; font-weight: 600; letter-spacing: 2px; }}
QLabel#value_large   {{ color: {TEXT_PRI}; font-size: 28px; font-weight: 700; }}
QLabel#value_small   {{ color: {TEXT_SEC}; font-size: 12px; }}
QPushButton#toggle_btn {{
    background-color: {INACTIVE}; color: {BG_DEEP}; border: none; border-radius: 20px;
    padding: 8px 24px; font-size: 13px; font-weight: 700; letter-spacing: 1px;
}}
QPushButton#toggle_btn:hover {{ background-color: #ff6680; }}
QPushButton#toggle_btn[active="true"] {{ background-color: {ACTIVE}; }}
QPushButton#toggle_btn[active="true"]:hover {{ background-color: #33ffaa; }}
QPushButton#nav_btn {{
    background: transparent; color: {TEXT_SEC}; border: none; border-radius: 10px;
    padding: 10px 16px; text-align: left; font-size: 13px;
}}
QPushButton#nav_btn:hover {{ background-color: {BG_HOVER}; color: {TEXT_PRI}; }}
QPushButton#nav_btn[selected="true"] {{ background-color: rgba(0,229,255,0.12); color: {ACCENT}; font-weight: 600; }}
QProgressBar {{
    background-color: {BORDER}; border-radius: 4px; border: none; height: 6px; text-align: center; color: transparent;
}}
QProgressBar::chunk {{ background-color: {ACCENT}; border-radius: 4px; }}
QProgressBar#stability_bar::chunk {{
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {ACTIVE}, stop:1 {ACCENT});
}}
QToolTip {{
    background-color: {BG_CARD}; color: {TEXT_PRI}; border: 1px solid {BORDER};
    border-radius: 6px; padding: 4px 8px;
}}
"""


# ===========================================================================
# Imports for widgets
# ===========================================================================

from PyQt6.QtCore    import Qt, QPropertyAnimation, QEasingCurve, pyqtSignal, QSize, pyqtSlot, QTimer
from PyQt6.QtGui     import QIcon, QFont, QImage, QPixmap, QCloseEvent
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QPushButton, QFrame, QProgressBar, QScrollArea,
    QSizePolicy, QSpacerItem, QMainWindow, QMessageBox,
)

from ui.shared_state  import SharedState
from ui.worker_thread import WorkerThread


# ===========================================================================
# ActivityLog  (was ui/activity_log.py)
# ===========================================================================

MAX_EVENTS = 200

_CATEGORY_STYLE = {
    'ACTION': (ACCENT,    'rgba(0,229,255,0.12)'),
    'MODE':   (ACTIVE,    'rgba(0,255,136,0.12)'),
    'SYSTEM': (TEXT_SEC,  'rgba(138,138,160,0.12)'),
    'ERROR':  (INACTIVE,  'rgba(255,68,102,0.12)'),
}
_DEFAULT_STYLE = (TEXT_SEC, 'rgba(138,138,160,0.12)')


def _pill_colour(category: str) -> tuple[str, str]:
    return _CATEGORY_STYLE.get(category.upper(), _DEFAULT_STYLE)


class EventPill(QFrame):
    def __init__(self, timestamp: str, category: str, description: str) -> None:
        super().__init__()
        colour, bg = _pill_colour(category)
        self.setFixedHeight(42)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setStyleSheet(
            f'QFrame {{ background-color: {bg}; border: 1px solid {colour}33; border-radius: 21px; }}'
        )
        lay = QHBoxLayout(self)
        lay.setContentsMargins(14, 0, 14, 0)
        lay.setSpacing(8)

        dot = QLabel('●')
        dot.setStyleSheet(f'color: {colour}; font-size: 10px; background: transparent; border: none;')
        ts_lbl = QLabel(timestamp)
        ts_lbl.setStyleSheet(f'color: {TEXT_HINT}; font-size: 11px; background: transparent; border: none;')
        cat_lbl = QLabel(category.upper())
        cat_lbl.setStyleSheet(
            f'color: {colour}; font-size: 10px; font-weight: 700; letter-spacing: 1px; background: transparent; border: none;'
        )
        desc_lbl = QLabel(description)
        desc_lbl.setStyleSheet(f'color: {TEXT_PRI}; font-size: 12px; background: transparent; border: none;')

        lay.addWidget(dot)
        lay.addWidget(ts_lbl)
        lay.addWidget(cat_lbl)
        lay.addWidget(desc_lbl)
        self.adjustSize()


class ActivityLog(QWidget):
    def __init__(self, state: SharedState, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._state  = state
        self._count  = 0
        self._pills: list[EventPill] = []
        self._build()
        state.log_event.connect(self._on_log_event)

    def _build(self) -> None:
        self.setFixedHeight(76)
        self.setStyleSheet(f'background-color: {BG_CARD}; border-top: 1px solid {BORDER};')

        outer = QVBoxLayout(self)
        outer.setContentsMargins(20, 6, 20, 6)
        outer.setSpacing(4)

        title_row = QHBoxLayout()
        title = QLabel('ACTIVITY LOG')
        title.setStyleSheet(
            f'color: {ACCENT}; font-size: 10px; font-weight: 600; letter-spacing: 2px; background: transparent; border: none;'
        )
        self._count_lbl = QLabel('0 events')
        self._count_lbl.setStyleSheet(f'color: {TEXT_HINT}; font-size: 10px; background: transparent; border: none;')
        title_row.addWidget(title)
        title_row.addStretch()
        title_row.addWidget(self._count_lbl)
        outer.addLayout(title_row)

        self._scroll = QScrollArea()
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setWidgetResizable(True)
        self._scroll.setStyleSheet('QScrollArea { background: transparent; border: none; }')

        self._inner = QWidget()
        self._inner.setStyleSheet('background: transparent;')
        self._pills_lay = QHBoxLayout(self._inner)
        self._pills_lay.setContentsMargins(0, 0, 0, 0)
        self._pills_lay.setSpacing(8)
        self._pills_lay.addStretch()

        self._scroll.setWidget(self._inner)
        outer.addWidget(self._scroll)

    @pyqtSlot(str, str, str)
    def _on_log_event(self, timestamp: str, category: str, description: str) -> None:
        if len(self._pills) >= MAX_EVENTS:
            old = self._pills.pop(0)
            self._pills_lay.removeWidget(old)
            old.deleteLater()

        pill = EventPill(timestamp, category, description)
        insert_idx = self._pills_lay.count() - 1
        self._pills_lay.insertWidget(insert_idx, pill)
        self._pills.append(pill)

        self._count += 1
        self._count_lbl.setText(f'{self._count} event{"s" if self._count != 1 else ""}')
        QTimer.singleShot(30, self._scroll_right)

    def _scroll_right(self) -> None:
        sb = self._scroll.horizontalScrollBar()
        sb.setValue(sb.maximum())


# ===========================================================================
# Sidebar  (was ui/sidebar.py)
# ===========================================================================

EXPANDED_W  = 220
COLLAPSED_W = 56
ANIM_MS     = 200

_TABS = [
    ('vision', '◉', 'Vision'),
    ('mode',   '⊞', 'Mode'),
]


class Sidebar(QWidget):
    tab_selected = pyqtSignal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._collapsed  = False
        self._active_tab = 'vision'
        self._nav_btns: dict[str, QPushButton] = {}
        self.setFixedWidth(EXPANDED_W)
        self._build_ui()
        self._select_tab('vision')

    def _build_ui(self) -> None:
        self.setStyleSheet(f'QWidget {{ background-color: {BG_CARD}; border-right: 1px solid {BORDER}; }}')
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Header
        header = QWidget()
        header.setFixedHeight(60)
        header.setStyleSheet(f'background: transparent; border-bottom: 1px solid {BORDER};')
        h_lay = QHBoxLayout(header)
        h_lay.setContentsMargins(12, 0, 8, 0)
        self._logo_label = QLabel('MMGI')
        self._logo_label.setStyleSheet(
            f'color: {ACCENT}; font-size: 16px; font-weight: 700; letter-spacing: 3px; border: none;'
        )
        self._collapse_btn = QPushButton('◄')
        self._collapse_btn.setFixedSize(30, 30)
        self._collapse_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._collapse_btn.setToolTip('Collapse sidebar')
        self._collapse_btn.setStyleSheet(f"""
            QPushButton {{ background: transparent; color: {TEXT_SEC}; border: none; font-size: 12px; border-radius: 6px; }}
            QPushButton:hover {{ background: {BG_HOVER}; color: {ACCENT}; }}
        """)
        self._collapse_btn.clicked.connect(self.toggle_collapse)
        h_lay.addWidget(self._logo_label)
        h_lay.addStretch()
        h_lay.addWidget(self._collapse_btn)
        root.addWidget(header)

        # Nav buttons
        nav_container = QWidget()
        nav_container.setStyleSheet('background: transparent; border: none;')
        nav_lay = QVBoxLayout(nav_container)
        nav_lay.setContentsMargins(8, 12, 8, 0)
        nav_lay.setSpacing(4)
        for tab_id, icon, label in _TABS:
            btn = QPushButton(f'{icon}  {label}')
            btn.setObjectName('nav_btn')
            btn.setFixedHeight(42)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setProperty('selected', False)
            btn.setStyleSheet(self._nav_btn_style())
            btn.clicked.connect(lambda checked, tid=tab_id: self._select_tab(tid))
            nav_lay.addWidget(btn)
            self._nav_btns[tab_id] = btn
        nav_lay.addStretch()
        root.addWidget(nav_container, stretch=1)

        # Footer
        footer = QLabel('v0.3  Smart Mode')
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setFixedHeight(36)
        footer.setStyleSheet(
            f'color: {TEXT_HINT}; font-size: 11px; border-top: 1px solid {BORDER}; background: transparent;'
        )
        self._footer = footer
        root.addWidget(footer)

    def _select_tab(self, tab_id: str) -> None:
        self._active_tab = tab_id
        for tid, btn in self._nav_btns.items():
            selected = (tid == tab_id)
            btn.setStyleSheet(self._nav_btn_style(selected=selected))
        self.tab_selected.emit(tab_id)

    def toggle_collapse(self) -> None:
        self._collapsed = not self._collapsed
        target_w = COLLAPSED_W if self._collapsed else EXPANDED_W
        arrow    = '►' if self._collapsed else '◄'

        anim = QPropertyAnimation(self, b'minimumWidth', self)
        anim.setDuration(ANIM_MS)
        anim.setEasingCurve(QEasingCurve.Type.InOutQuart)
        anim.setStartValue(self.width())
        anim.setEndValue(target_w)
        anim.start()
        self._anim = anim

        anim2 = QPropertyAnimation(self, b'maximumWidth', self)
        anim2.setDuration(ANIM_MS)
        anim2.setEasingCurve(QEasingCurve.Type.InOutQuart)
        anim2.setStartValue(self.width())
        anim2.setEndValue(target_w)
        anim2.start()
        self._anim2 = anim2

        self._collapse_btn.setText(arrow)
        self._logo_label.setVisible(not self._collapsed)
        self._footer.setVisible(not self._collapsed)
        for tab_id, icon, label in _TABS:
            btn = self._nav_btns[tab_id]
            btn.setText(icon if self._collapsed else f'{icon}  {label}')

    @staticmethod
    def _nav_btn_style(selected: bool = False) -> str:
        if selected:
            return (
                f'QPushButton {{ background-color: rgba(0,229,255,0.12); color: {ACCENT}; font-weight: 600; '
                f'border: none; border-radius: 10px; padding: 10px 16px; text-align: left; font-size: 13px; }}'
            )
        return (
            f'QPushButton {{ background: transparent; color: {TEXT_SEC}; border: none; border-radius: 10px; '
            f'padding: 10px 16px; text-align: left; font-size: 13px; }}'
            f'QPushButton:hover {{ background-color: {BG_HOVER}; color: {TEXT_PRI}; }}'
        )


# ===========================================================================
# VisionPanel  (was ui/vision_panel.py)
# ===========================================================================

_MODE_ACCENT = {
    'App Mode':    MODE_APP,
    'Media Mode':  MODE_MEDIA,
    'System Mode': MODE_SYSTEM,
}


class VisionPanel(QWidget):
    def __init__(self, state: SharedState, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._state = state
        self._build_ui()
        self._connect_state()

    def _build_ui(self) -> None:
        self.setStyleSheet(f'background-color: {BG_DEEP};')
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(12)

        self._cam_frame = QFrame()
        self._cam_frame.setObjectName('cam_frame')
        self._cam_frame.setStyleSheet(
            f'QFrame#cam_frame {{ background-color: #000000; border: 2px solid {BORDER}; border-radius: 16px; }}'
        )
        cam_lay = QVBoxLayout(self._cam_frame)
        cam_lay.setContentsMargins(0, 0, 0, 0)

        self._video_label = QLabel()
        self._video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._video_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._video_label.setMinimumSize(480, 270)
        self._video_label.setText('⬤  Waiting for camera…')
        self._video_label.setStyleSheet(f'color: {TEXT_HINT}; font-size: 16px; background: transparent; border: none;')

        cam_lay.addWidget(self._video_label)
        root.addWidget(self._cam_frame, stretch=1)

        info_row = QHBoxLayout()
        info_row.setSpacing(20)

        self._mode_pill = QLabel('APP MODE')
        self._mode_pill.setFixedHeight(26)
        self._mode_pill.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._mode_pill.setStyleSheet(
            f'background-color: rgba(0,229,255,0.15); color: {ACCENT}; '
            f'border: 1px solid {ACCENT}; border-radius: 13px; '
            f'padding: 0 12px; font-size: 11px; font-weight: 700; letter-spacing: 1px;'
        )

        gesture_lbl = QLabel('GESTURE')
        gesture_lbl.setStyleSheet(f'color: {TEXT_HINT}; font-size: 11px; letter-spacing: 1px;')

        self._gesture_val = QLabel('—')
        self._gesture_val.setStyleSheet(f'color: {TEXT_PRI}; font-size: 13px; font-weight: 600;')

        info_row.addWidget(self._mode_pill)
        info_row.addStretch()
        info_row.addWidget(gesture_lbl)
        info_row.addWidget(self._gesture_val)
        root.addLayout(info_row)

        stab_lbl = QLabel('MODE SWITCH HOLD')
        stab_lbl.setStyleSheet(f'color: {TEXT_HINT}; font-size: 10px; letter-spacing: 1px;')

        self._stability_bar = QProgressBar()
        self._stability_bar.setObjectName('stability_bar')
        self._stability_bar.setRange(0, 100)
        self._stability_bar.setValue(0)
        self._stability_bar.setFixedHeight(8)
        self._stability_bar.setTextVisible(False)
        self._stability_bar.setStyleSheet(f"""
            QProgressBar {{ background-color: {BORDER}; border-radius: 4px; border: none; }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {ACTIVE}, stop:1 {ACCENT});
                border-radius: 4px;
            }}
        """)

        root.addWidget(stab_lbl)
        root.addWidget(self._stability_bar)

    def _connect_state(self) -> None:
        s = self._state
        s.mode_changed.connect(self._on_mode_changed)
        s.gesture_changed.connect(self._on_gesture_changed)
        s.mode_stability_changed.connect(self._on_stability_changed)
        s.system_active_changed.connect(self._on_active_changed)

    @pyqtSlot(QImage)
    def update_frame(self, image: QImage) -> None:
        lbl_w = self._video_label.width()
        lbl_h = self._video_label.height()
        if lbl_w < 4 or lbl_h < 4:
            return
        pix = QPixmap.fromImage(image).scaled(
            lbl_w, lbl_h,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self._video_label.setPixmap(pix)
        self._video_label.setStyleSheet('background: transparent; border: none;')

    @pyqtSlot(str)
    def _on_mode_changed(self, mode: str) -> None:
        colour = _MODE_ACCENT.get(mode, ACCENT)
        short  = mode.replace(' Mode', '').upper() + ' MODE'
        self._mode_pill.setText(short)
        self._mode_pill.setStyleSheet(
            f'background-color: rgba(0,229,255,0.12); color: {colour}; '
            f'border: 1px solid {colour}; border-radius: 13px; '
            f'padding: 0 12px; font-size: 11px; font-weight: 700; letter-spacing: 1px;'
        )
        self._cam_frame.setStyleSheet(
            f'QFrame#cam_frame {{ background-color: #000000; border: 2px solid {colour}; border-radius: 16px; }}'
        )

    @pyqtSlot(str)
    def _on_gesture_changed(self, gesture: str) -> None:
        self._gesture_val.setText(gesture if gesture else '—')

    @pyqtSlot(float)
    def _on_stability_changed(self, progress: float) -> None:
        self._stability_bar.setValue(int(progress * 100))

    @pyqtSlot(bool)
    def _on_active_changed(self, active: bool) -> None:
        border_colour = ACTIVE if active else BORDER
        self._cam_frame.setStyleSheet(
            f'QFrame#cam_frame {{ background-color: #000000; border: 2px solid {border_colour}; border-radius: 16px; }}'
        )


# ===========================================================================
# SystemPanel cards  (was ui/system_panel.py)
# ===========================================================================

_MODE_COLOUR = {
    'App Mode':    MODE_APP,
    'Media Mode':  MODE_MEDIA,
    'System Mode': MODE_SYSTEM,
}

_GESTURE_INSTRUCTIONS: dict[str, list[tuple[str, str]]] = {
    'App Mode': [
        ('One Finger',  'Open Browser'),
        ('Two Fingers', 'Open Music'),
    ],
    'Media Mode': [
        ('One Finger',  'Volume Up'),
        ('Two Fingers', 'Volume Down'),
        ('4 Fingers',   'Play / Pause'),
        ('Thumbs Up',   'Mute / Unmute'),
    ],
    'System Mode': [],
}

_SWITCH_INSTRUCTIONS = [
    ('3 Fingers  → 1 s', 'Cycle Mode'),
]


def _divider() -> QFrame:
    line = QFrame()
    line.setFrameShape(QFrame.Shape.HLine)
    line.setStyleSheet(f'color: {BORDER}; background: {BORDER}; border: none; max-height: 1px;')
    return line


def _card(title: str) -> tuple[QFrame, QLabel, QVBoxLayout]:
    frame = QFrame()
    frame.setObjectName('card')
    frame.setStyleSheet(
        f'QFrame#card {{ background-color: {BG_CARD}; border: 1px solid {BORDER}; border-radius: 15px; }}'
    )
    lay = QVBoxLayout(frame)
    lay.setContentsMargins(16, 14, 16, 16)
    lay.setSpacing(10)
    title_lbl = QLabel(title)
    title_lbl.setStyleSheet(
        f'color: {ACCENT}; font-size: 10px; font-weight: 600; letter-spacing: 2px; background: transparent; border: none;'
    )
    lay.addWidget(title_lbl)
    return frame, title_lbl, lay


def _instr_row(left: str, right: str, left_colour: str, right_colour: str) -> QWidget:
    w = QWidget()
    w.setStyleSheet('background: transparent;')
    lay = QHBoxLayout(w)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setSpacing(8)
    lbl_l = QLabel(left)
    lbl_l.setStyleSheet(f'color: {left_colour}; font-size: 12px; background: transparent; border: none;')
    lbl_r = QLabel(right)
    lbl_r.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
    lbl_r.setStyleSheet(f'color: {right_colour}; font-size: 12px; font-weight: 600; background: transparent; border: none;')
    lay.addWidget(lbl_l)
    lay.addStretch()
    lay.addWidget(lbl_r)
    return w


class SystemCard(QFrame):
    def __init__(self, state: SharedState, parent=None) -> None:
        super().__init__(parent)
        self._state = state
        self._build()
        state.system_active_changed.connect(self._on_active)

    def _build(self) -> None:
        self.setObjectName('card')
        self.setStyleSheet(
            f'QFrame#card {{ background-color: {BG_CARD}; border: 1px solid {BORDER}; border-radius: 15px; }}'
        )
        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 14, 16, 16)
        lay.setSpacing(10)

        title = QLabel('SYSTEM')
        title.setStyleSheet(
            f'color: {ACCENT}; font-size: 10px; font-weight: 600; letter-spacing: 2px; background: transparent; border: none;'
        )
        lay.addWidget(title)

        badge_row = QHBoxLayout()
        self._dot = QLabel('●')
        self._dot.setStyleSheet(f'color: {INACTIVE}; font-size: 16px; background: transparent; border: none;')
        self._status_lbl = QLabel('INACTIVE')
        self._status_lbl.setStyleSheet(
            f'color: {INACTIVE}; font-size: 13px; font-weight: 600; background: transparent; border: none;'
        )
        badge_row.addWidget(self._dot)
        badge_row.addWidget(self._status_lbl)
        badge_row.addStretch()
        lay.addLayout(badge_row)

        self._toggle_btn = QPushButton('SYSTEM  OFF')
        self._toggle_btn.setObjectName('toggle_btn')
        self._toggle_btn.setFixedHeight(40)
        self._toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._toggle_btn.setProperty('active', False)
        self._toggle_btn.setStyleSheet(self._btn_style(False))
        self._toggle_btn.clicked.connect(self._on_toggle_clicked)
        lay.addWidget(self._toggle_btn)

        hint = QLabel('Show Open Palm 2 s to activate')
        hint.setStyleSheet(f'color: {TEXT_HINT}; font-size: 11px; background: transparent; border: none;')
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(hint)

    @pyqtSlot(bool)
    def _on_active(self, active: bool) -> None:
        if active:
            self._dot.setStyleSheet(f'color: {ACTIVE}; font-size: 16px; background: transparent; border: none;')
            self._status_lbl.setText('ACTIVE')
            self._status_lbl.setStyleSheet(f'color: {ACTIVE}; font-size: 13px; font-weight: 600; background: transparent; border: none;')
            self._toggle_btn.setText('SYSTEM  ON')
            self._toggle_btn.setStyleSheet(self._btn_style(True))
        else:
            self._dot.setStyleSheet(f'color: {INACTIVE}; font-size: 16px; background: transparent; border: none;')
            self._status_lbl.setText('INACTIVE')
            self._status_lbl.setStyleSheet(f'color: {INACTIVE}; font-size: 13px; font-weight: 600; background: transparent; border: none;')
            self._toggle_btn.setText('SYSTEM  OFF')
            self._toggle_btn.setStyleSheet(self._btn_style(False))

    def _on_toggle_clicked(self) -> None:
        pass  # Visual feedback only

    @staticmethod
    def _btn_style(active: bool) -> str:
        bg  = ACTIVE   if active else INACTIVE
        hov = '#33ffaa' if active else '#ff6680'
        return (
            f'QPushButton {{ background-color: {bg}; color: #0F0F14; border: none; border-radius: 20px; '
            f'padding: 8px 24px; font-size: 13px; font-weight: 700; letter-spacing: 1px; }}'
            f'QPushButton:hover {{ background-color: {hov}; }}'
        )


class ModeCard(QFrame):
    def __init__(self, state: SharedState, parent=None) -> None:
        super().__init__(parent)
        self._state = state
        self._build()
        state.mode_changed.connect(self._on_mode_changed)

    def _build(self) -> None:
        self.setObjectName('card')
        self.setStyleSheet(
            f'QFrame#card {{ background-color: {BG_CARD}; border: 1px solid {BORDER}; border-radius: 15px; }}'
        )
        self._lay = QVBoxLayout(self)
        self._lay.setContentsMargins(16, 14, 16, 16)
        self._lay.setSpacing(8)

        title_row = QHBoxLayout()
        title_lbl = QLabel('MODE')
        title_lbl.setStyleSheet(
            f'color: {ACCENT}; font-size: 10px; font-weight: 600; letter-spacing: 2px; background: transparent; border: none;'
        )
        self._mode_name = QLabel('APP MODE')
        self._mode_name.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self._mode_name.setStyleSheet(
            f'color: {MODE_APP}; font-size: 13px; font-weight: 700; background: transparent; border: none;'
        )
        title_row.addWidget(title_lbl)
        title_row.addStretch()
        title_row.addWidget(self._mode_name)
        self._lay.addLayout(title_row)

        self._instr_container = QWidget()
        self._instr_container.setStyleSheet('background: transparent;')
        self._instr_lay = QGridLayout(self._instr_container)
        self._instr_lay.setContentsMargins(0, 0, 0, 0)
        self._instr_lay.setSpacing(5)
        self._instr_lay.setColumnStretch(0, 1)
        self._instr_lay.setColumnStretch(1, 1)
        self._lay.addWidget(self._instr_container)

        self._lay.addWidget(_divider())

        switch_title = QLabel('SWITCH MODE')
        switch_title.setStyleSheet(
            f'color: {TEXT_HINT}; font-size: 10px; letter-spacing: 1px; background: transparent; border: none;'
        )
        self._lay.addWidget(switch_title)
        for hold, target in _SWITCH_INSTRUCTIONS:
            row = _instr_row(hold, target, TEXT_HINT, TEXT_SEC)
            self._lay.addWidget(row)

        self._build_instructions('App Mode')

    def _build_instructions(self, mode: str) -> None:
        while self._instr_lay.count():
            item = self._instr_lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        instructions = _GESTURE_INSTRUCTIONS.get(mode, [])
        for r, (gesture, action) in enumerate(instructions):
            lbl_l = QLabel(gesture)
            lbl_l.setStyleSheet(f'color: {TEXT_SEC}; font-size: 11px; background: transparent; border: none;')
            lbl_l.setWordWrap(True)
            lbl_r = QLabel(action)
            lbl_r.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            lbl_r.setStyleSheet(f'color: {ACCENT}; font-size: 11px; font-weight: 600; background: transparent; border: none;')
            lbl_r.setWordWrap(True)
            self._instr_lay.addWidget(lbl_l, r, 0)
            self._instr_lay.addWidget(lbl_r, r, 1)
        if not instructions:
            ph = QLabel('No gestures configured')
            ph.setStyleSheet(f'color: {TEXT_HINT}; font-size: 11px; font-style: italic; background: transparent; border: none;')
            self._instr_lay.addWidget(ph, 0, 0, 1, 2)

    @pyqtSlot(str)
    def _on_mode_changed(self, mode: str) -> None:
        colour = _MODE_COLOUR.get(mode, ACCENT)
        short  = mode.replace(' Mode', '').upper() + ' MODE'
        self._mode_name.setText(short)
        self._mode_name.setStyleSheet(
            f'color: {colour}; font-size: 13px; font-weight: 700; background: transparent; border: none;'
        )
        self._build_instructions(mode)


class PerformanceCard(QFrame):
    def __init__(self, state: SharedState, parent=None) -> None:
        super().__init__(parent)
        self._state = state
        self._build()
        state.fps_changed.connect(self._on_fps)
        state.latency_changed.connect(self._on_latency)
        state.volume_changed.connect(self._on_volume)
        state.confidence_changed.connect(self._on_confidence)

    def _build(self) -> None:
        self.setObjectName('card')
        self.setStyleSheet(
            f'QFrame#card {{ background-color: {BG_CARD}; border: 1px solid {BORDER}; border-radius: 15px; }}'
        )
        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 14, 16, 16)
        lay.setSpacing(10)

        title = QLabel('PERFORMANCE')
        title.setStyleSheet(
            f'color: {ACCENT}; font-size: 10px; font-weight: 600; letter-spacing: 2px; background: transparent; border: none;'
        )
        lay.addWidget(title)

        metrics_w = QWidget()
        metrics_w.setStyleSheet('background: transparent;')
        metrics_grid = QGridLayout(metrics_w)
        metrics_grid.setContentsMargins(0, 0, 0, 0)
        metrics_grid.setHorizontalSpacing(16)
        metrics_grid.setVerticalSpacing(2)

        fps_title = QLabel('FPS')
        fps_title.setStyleSheet(f'color: {TEXT_HINT}; font-size: 10px; letter-spacing: 1px; background: transparent; border: none;')
        self._fps_val = QLabel('—')
        self._fps_val.setStyleSheet(f'color: {TEXT_PRI}; font-size: 15px; font-weight: 700; background: transparent; border: none;')

        lat_title = QLabel('LATENCY')
        lat_title.setStyleSheet(f'color: {TEXT_HINT}; font-size: 10px; letter-spacing: 1px; background: transparent; border: none;')
        self._latency_val = QLabel('—')
        self._latency_val.setStyleSheet(f'color: {TEXT_PRI}; font-size: 15px; font-weight: 700; background: transparent; border: none;')

        metrics_grid.addWidget(fps_title,         0, 0)
        metrics_grid.addWidget(self._fps_val,     1, 0)
        metrics_grid.addWidget(lat_title,         0, 1)
        metrics_grid.addWidget(self._latency_val, 1, 1)
        metrics_grid.setColumnStretch(0, 1)
        metrics_grid.setColumnStretch(1, 1)
        lay.addWidget(metrics_w)

        lay.addWidget(_divider())

        vol_row = QHBoxLayout()
        vol_title = QLabel('VOLUME')
        vol_title.setStyleSheet(f'color: {TEXT_HINT}; font-size: 10px; letter-spacing: 1px; background: transparent; border: none;')
        self._vol_pct = QLabel('50 %')
        self._vol_pct.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self._vol_pct.setStyleSheet(f'color: {TEXT_SEC}; font-size: 11px; background: transparent; border: none;')
        vol_row.addWidget(vol_title)
        vol_row.addStretch()
        vol_row.addWidget(self._vol_pct)
        lay.addLayout(vol_row)

        self._vol_bar = QProgressBar()
        self._vol_bar.setRange(0, 100)
        self._vol_bar.setValue(50)
        self._vol_bar.setFixedHeight(6)
        self._vol_bar.setTextVisible(False)
        self._vol_bar.setStyleSheet(f"""
            QProgressBar {{ background: {BORDER}; border-radius: 3px; border: none; }}
            QProgressBar::chunk {{ background: {ACCENT}; border-radius: 3px; }}
        """)
        lay.addWidget(self._vol_bar)

        lay.addWidget(_divider())

        conf_row = QHBoxLayout()
        conf_title = QLabel('CONFIDENCE')
        conf_title.setStyleSheet(f'color: {TEXT_HINT}; font-size: 10px; letter-spacing: 1px; background: transparent; border: none;')
        self._conf_pct = QLabel('— %')
        self._conf_pct.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self._conf_pct.setStyleSheet(f'color: {TEXT_SEC}; font-size: 11px; background: transparent; border: none;')
        conf_row.addWidget(conf_title)
        conf_row.addStretch()
        conf_row.addWidget(self._conf_pct)
        lay.addLayout(conf_row)

        self._conf_bar = QProgressBar()
        self._conf_bar.setRange(0, 100)
        self._conf_bar.setValue(0)
        self._conf_bar.setFixedHeight(6)
        self._conf_bar.setTextVisible(False)
        self._conf_bar.setStyleSheet(f"""
            QProgressBar {{ background: {BORDER}; border-radius: 3px; border: none; }}
            QProgressBar::chunk {{ background: {ACTIVE}; border-radius: 3px; }}
        """)
        lay.addWidget(self._conf_bar)

    @pyqtSlot(float)
    def _on_fps(self, fps: float) -> None:
        self._fps_val.setText(f'{fps:.0f}')

    @pyqtSlot(float)
    def _on_latency(self, ms: float) -> None:
        self._latency_val.setText(f'{ms:.0f} ms')

    @pyqtSlot(int)
    def _on_volume(self, pct: int) -> None:
        self._vol_pct.setText(f'{pct} %')
        self._vol_bar.setValue(pct)

    @pyqtSlot(float)
    def _on_confidence(self, conf: float) -> None:
        pct = int(conf * 100)
        self._conf_pct.setText(f'{pct} %')
        self._conf_bar.setValue(pct)


class SystemPanel(QWidget):
    def __init__(self, state: SharedState, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._build(state)

    def _build(self, state: SharedState) -> None:
        self.setFixedWidth(340)
        self.setStyleSheet(f'background-color: {BG_DEEP};')
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 16, 16, 16)
        root.setSpacing(10)
        root.addWidget(SystemCard(state))
        root.addWidget(ModeCard(state))
        root.addWidget(PerformanceCard(state))
        root.addStretch()


# ===========================================================================
# MainWindow  (was ui/main_window.py)
# ===========================================================================

class MainWindow(QMainWindow):
    WINDOW_TITLE   = 'MMGI  —  Smart Mode AI Gesture Controller'
    MIN_W, MIN_H   = 1100, 650

    def __init__(self) -> None:
        super().__init__()
        self._state  = SharedState(self)
        self._worker: WorkerThread | None = None
        self._setup_window()
        self._build_ui()
        self._start_worker()

    def _setup_window(self) -> None:
        self.setWindowTitle(self.WINDOW_TITLE)
        self.setMinimumSize(self.MIN_W, self.MIN_H)
        self.resize(1280, 720)
        self.setStyleSheet(GLOBAL_QSS)

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(self._build_header())

        body = QHBoxLayout()
        body.setSpacing(0)
        body.setContentsMargins(0, 0, 0, 0)
        self._sidebar     = Sidebar()
        self._vision      = VisionPanel(self._state)
        self._sys_panel   = SystemPanel(self._state)
        body.addWidget(self._sidebar)
        body.addWidget(self._vision, stretch=1)
        body.addWidget(self._sys_panel)
        root.addLayout(body, stretch=1)

        self._activity = ActivityLog(self._state)
        root.addWidget(self._activity)

    def _build_header(self) -> QWidget:
        header = QWidget()
        header.setFixedHeight(52)
        header.setStyleSheet(f'background-color: {BG_CARD}; border-bottom: 1px solid {BORDER};')
        lay = QHBoxLayout(header)
        lay.setContentsMargins(20, 0, 20, 0)
        lay.setSpacing(12)

        dot = QLabel('◉')
        dot.setStyleSheet(f'color: {ACCENT}; font-size: 14px;')
        self._header_dot = dot

        title = QLabel('MMGI')
        title.setStyleSheet(f'color: {ACCENT}; font-size: 15px; font-weight: 700; letter-spacing: 3px;')

        subtitle = QLabel('Smart Mode AI Controller')
        subtitle.setStyleSheet(f'color: {TEXT_HINT}; font-size: 12px;')

        self._header_status = QLabel('⬤  INACTIVE')
        self._header_status.setStyleSheet(f'color: {INACTIVE}; font-size: 12px; font-weight: 600;')

        self._header_mode = QLabel('APP MODE')
        self._header_mode.setStyleSheet(
            f'color: {ACCENT}; font-size: 11px; font-weight: 700; letter-spacing: 1px; '
            f'background: rgba(0,229,255,0.10); border: 1px solid {ACCENT}; border-radius: 10px; padding: 2px 10px;'
        )

        lay.addWidget(dot)
        lay.addWidget(title)
        lay.addWidget(subtitle)
        lay.addStretch()
        lay.addWidget(self._header_mode)
        lay.addWidget(self._header_status)

        self._state.system_active_changed.connect(self._on_active_header)
        self._state.mode_changed.connect(self._on_mode_header)
        return header

    def _start_worker(self) -> None:
        self._worker = WorkerThread(self._state, parent=self)
        self._worker.frame_ready.connect(self._vision.update_frame)
        self._worker.error.connect(self._on_worker_error)
        self._worker.start()

    @pyqtSlot(bool)
    def _on_active_header(self, active: bool) -> None:
        if active:
            self._header_status.setText('⬤  ACTIVE')
            self._header_status.setStyleSheet(f'color: {ACTIVE}; font-size: 12px; font-weight: 600;')
        else:
            self._header_status.setText('⬤  INACTIVE')
            self._header_status.setStyleSheet(f'color: {INACTIVE}; font-size: 12px; font-weight: 600;')

    @pyqtSlot(str)
    def _on_mode_header(self, mode: str) -> None:
        colour_map = {'App Mode': MODE_APP, 'Media Mode': MODE_MEDIA, 'System Mode': MODE_SYSTEM}
        colour = colour_map.get(mode, ACCENT)
        short  = mode.replace(' Mode', '').upper() + ' MODE'
        self._header_mode.setText(short)
        self._header_mode.setStyleSheet(
            f'color: {colour}; font-size: 11px; font-weight: 700; letter-spacing: 1px; '
            f'background: rgba(0,229,255,0.10); border: 1px solid {colour}; border-radius: 10px; padding: 2px 10px;'
        )

    @pyqtSlot(str)
    def _on_worker_error(self, msg: str) -> None:
        self._state.emit_log('--:--:--', 'ERROR', msg.split('\n')[0])
        QMessageBox.critical(self, 'Pipeline Error',
                             f'The gesture pipeline encountered an error:\n\n{msg[:400]}')

    def closeEvent(self, event: QCloseEvent) -> None:
        if self._worker is not None and self._worker.isRunning():
            self._worker.stop()
            self._worker.wait(3000)
        event.accept()
