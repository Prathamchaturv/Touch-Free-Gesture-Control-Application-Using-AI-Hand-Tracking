"""
ui/system_panel.py - Right panel with three cards:

1. SystemCard  – ON/OFF toggle + status indicator
2. ModeCard    – current mode name + gesture→action instruction table
3. PerformanceCard – FPS / Latency / Volume readouts

Layout
──────
┌──────────────────────┐
│  SYSTEM              │  ← section title
│  ●  ACTIVE           │  ← status badge
│  [  SYSTEM  ON  ]    │  ← toggle button
└──────────────────────┘
┌──────────────────────┐
│  MODE                │  ← current mode (colour-coded)
│  Thumbs Up → Browser │  ← instruction rows
│  Ring+Pinky → Music  │
│  Pinky → Volume Up   │
└──────────────────────┘
┌──────────────────────┐
│  PERFORMANCE         │
│  FPS     Latency     │
│  30.0    12.3 ms     │
│  ░░░░░░░░░ Volume 65%│
└──────────────────────┘
"""

from __future__ import annotations

from PyQt6.QtCore    import Qt, pyqtSlot
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QPushButton, QFrame, QProgressBar, QScrollArea,
    QSizePolicy, QSpacerItem,
)

from shared_state import SharedState
from ui.styles    import (
    BG_CARD, BG_DEEP, BORDER, ACCENT, ACTIVE, INACTIVE,
    TEXT_PRI, TEXT_SEC, TEXT_HINT, MODE_APP, MODE_MEDIA, MODE_SYSTEM,
)

_MODE_COLOUR = {
    'App Mode':    MODE_APP,
    'Media Mode':  MODE_MEDIA,
    'System Mode': MODE_SYSTEM,
}

# Gesture → human label mapping (per mode)
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

# Mode-switch instructions (always shown at bottom)
_SWITCH_INSTRUCTIONS = [
    ('3 Fingers  → 1 s', 'Cycle Mode'),
]


def _divider() -> QFrame:
    line = QFrame()
    line.setFrameShape(QFrame.Shape.HLine)
    line.setStyleSheet(f'color: {BORDER}; background: {BORDER}; border: none; max-height: 1px;')
    return line


def _card(title: str) -> tuple[QFrame, QLabel, QVBoxLayout]:
    """Create a styled card frame. Returns (frame, title_label, body_layout)."""
    frame = QFrame()
    frame.setObjectName('card')
    frame.setStyleSheet(
        f'QFrame#card {{'
        f'  background-color: {BG_CARD};'
        f'  border: 1px solid {BORDER};'
        f'  border-radius: 15px;'
        f'}}'
    )
    lay = QVBoxLayout(frame)
    lay.setContentsMargins(16, 14, 16, 16)
    lay.setSpacing(10)

    title_lbl = QLabel(title)
    title_lbl.setStyleSheet(
        f'color: {ACCENT}; font-size: 10px; font-weight: 600; '
        f'letter-spacing: 2px; background: transparent; border: none;'
    )
    lay.addWidget(title_lbl)

    return frame, title_lbl, lay


# ---------------------------------------------------------------------------
# System Card
# ---------------------------------------------------------------------------

class SystemCard(QFrame):
    def __init__(self, state: SharedState, parent=None) -> None:
        super().__init__(parent)
        self._state = state
        self._build()
        state.system_active_changed.connect(self._on_active)

    def _build(self) -> None:
        self.setObjectName('card')
        self.setStyleSheet(
            f'QFrame#card {{ background-color: {BG_CARD}; '
            f'border: 1px solid {BORDER}; border-radius: 15px; }}'
        )
        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 14, 16, 16)
        lay.setSpacing(10)

        # Title
        QLabel('SYSTEM', self)
        title = QLabel('SYSTEM')
        title.setStyleSheet(
            f'color: {ACCENT}; font-size: 10px; font-weight: 600; '
            f'letter-spacing: 2px; background: transparent; border: none;'
        )
        lay.addWidget(title)

        # Status badge
        badge_row = QHBoxLayout()
        self._dot = QLabel('●')
        self._dot.setStyleSheet(f'color: {INACTIVE}; font-size: 16px; background: transparent; border: none;')
        self._status_lbl = QLabel('INACTIVE')
        self._status_lbl.setStyleSheet(
            f'color: {INACTIVE}; font-size: 13px; font-weight: 600; '
            f'background: transparent; border: none;'
        )
        badge_row.addWidget(self._dot)
        badge_row.addWidget(self._status_lbl)
        badge_row.addStretch()
        lay.addLayout(badge_row)

        # Toggle button
        self._toggle_btn = QPushButton('SYSTEM  OFF')
        self._toggle_btn.setObjectName('toggle_btn')
        self._toggle_btn.setFixedHeight(40)
        self._toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._toggle_btn.setProperty('active', False)
        self._toggle_btn.setStyleSheet(self._btn_style(False))
        self._toggle_btn.clicked.connect(self._on_toggle_clicked)
        lay.addWidget(self._toggle_btn)

        # Instruction
        hint = QLabel('Show Open Palm 2 s to activate')
        hint.setStyleSheet(
            f'color: {TEXT_HINT}; font-size: 11px; background: transparent; border: none;'
        )
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(hint)

    @pyqtSlot(bool)
    def _on_active(self, active: bool) -> None:
        if active:
            self._dot.setStyleSheet(f'color: {ACTIVE}; font-size: 16px; background: transparent; border: none;')
            self._status_lbl.setText('ACTIVE')
            self._status_lbl.setStyleSheet(
                f'color: {ACTIVE}; font-size: 13px; font-weight: 600; '
                f'background: transparent; border: none;'
            )
            self._toggle_btn.setText('SYSTEM  ON')
            self._toggle_btn.setStyleSheet(self._btn_style(True))
        else:
            self._dot.setStyleSheet(f'color: {INACTIVE}; font-size: 16px; background: transparent; border: none;')
            self._status_lbl.setText('INACTIVE')
            self._status_lbl.setStyleSheet(
                f'color: {INACTIVE}; font-size: 13px; font-weight: 600; '
                f'background: transparent; border: none;'
            )
            self._toggle_btn.setText('SYSTEM  OFF')
            self._toggle_btn.setStyleSheet(self._btn_style(False))

    def _on_toggle_clicked(self) -> None:
        # Visual feedback only — real state is driven by gesture / worker
        pass

    @staticmethod
    def _btn_style(active: bool) -> str:
        bg  = ACTIVE   if active else INACTIVE
        hov = '#33ffaa' if active else '#ff6680'
        return (
            f'QPushButton {{ background-color: {bg}; color: #0F0F14; '
            f'border: none; border-radius: 20px; padding: 8px 24px; '
            f'font-size: 13px; font-weight: 700; letter-spacing: 1px; }}'
            f'QPushButton:hover {{ background-color: {hov}; }}'
        )


# ---------------------------------------------------------------------------
# Mode Card
# ---------------------------------------------------------------------------

class ModeCard(QFrame):
    def __init__(self, state: SharedState, parent=None) -> None:
        super().__init__(parent)
        self._state = state
        self._build()
        state.mode_changed.connect(self._on_mode_changed)

    def _build(self) -> None:
        self.setObjectName('card')
        self.setStyleSheet(
            f'QFrame#card {{ background-color: {BG_CARD}; '
            f'border: 1px solid {BORDER}; border-radius: 15px; }}'
        )
        self._lay = QVBoxLayout(self)
        self._lay.setContentsMargins(16, 14, 16, 16)
        self._lay.setSpacing(8)

        # Title row
        title_row = QHBoxLayout()
        title_lbl = QLabel('MODE')
        title_lbl.setStyleSheet(
            f'color: {ACCENT}; font-size: 10px; font-weight: 600; '
            f'letter-spacing: 2px; background: transparent; border: none;'
        )
        self._mode_name = QLabel('APP MODE')
        self._mode_name.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self._mode_name.setStyleSheet(
            f'color: {MODE_APP}; font-size: 13px; font-weight: 700; '
            f'background: transparent; border: none;'
        )
        title_row.addWidget(title_lbl)
        title_row.addStretch()
        title_row.addWidget(self._mode_name)
        self._lay.addLayout(title_row)

        # Instruction rows container — uses QGridLayout so columns stay aligned
        self._instr_container = QWidget()
        self._instr_container.setStyleSheet('background: transparent;')
        self._instr_lay = QGridLayout(self._instr_container)
        self._instr_lay.setContentsMargins(0, 0, 0, 0)
        self._instr_lay.setSpacing(5)
        self._instr_lay.setColumnStretch(0, 1)
        self._instr_lay.setColumnStretch(1, 1)
        self._lay.addWidget(self._instr_container)

        self._lay.addWidget(_divider())

        # Mode-switch reminder
        switch_title = QLabel('SWITCH MODE')
        switch_title.setStyleSheet(
            f'color: {TEXT_HINT}; font-size: 10px; letter-spacing: 1px; '
            f'background: transparent; border: none;'
        )
        self._lay.addWidget(switch_title)
        for hold, target in _SWITCH_INSTRUCTIONS:
            row = _instr_row(hold, target, TEXT_HINT, TEXT_SEC)
            self._lay.addWidget(row)

        # Build default (App Mode)
        self._build_instructions('App Mode')

    def _build_instructions(self, mode: str) -> None:
        """Rebuild the gesture instruction rows for the given mode."""
        # Clear old cells
        while self._instr_lay.count():
            item = self._instr_lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        instructions = _GESTURE_INSTRUCTIONS.get(mode, [])
        for r, (gesture, action) in enumerate(instructions):
            lbl_l = QLabel(gesture)
            lbl_l.setStyleSheet(
                f'color: {TEXT_SEC}; font-size: 11px; '
                f'background: transparent; border: none;'
            )
            lbl_l.setWordWrap(True)
            lbl_r = QLabel(action)
            lbl_r.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            lbl_r.setStyleSheet(
                f'color: {ACCENT}; font-size: 11px; font-weight: 600; '
                f'background: transparent; border: none;'
            )
            lbl_r.setWordWrap(True)
            self._instr_lay.addWidget(lbl_l, r, 0)
            self._instr_lay.addWidget(lbl_r, r, 1)

        # If no gestures, show a placeholder
        if not instructions:
            ph = QLabel('No gestures configured')
            ph.setStyleSheet(
                f'color: {TEXT_HINT}; font-size: 11px; font-style: italic; '
                f'background: transparent; border: none;'
            )
            self._instr_lay.addWidget(ph, 0, 0, 1, 2)

    @pyqtSlot(str)
    def _on_mode_changed(self, mode: str) -> None:
        colour = _MODE_COLOUR.get(mode, ACCENT)
        short  = mode.replace(' Mode', '').upper() + ' MODE'
        self._mode_name.setText(short)
        self._mode_name.setStyleSheet(
            f'color: {colour}; font-size: 13px; font-weight: 700; '
            f'background: transparent; border: none;'
        )
        self._build_instructions(mode)



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


# ---------------------------------------------------------------------------
# Performance Card
# ---------------------------------------------------------------------------

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
            f'QFrame#card {{ background-color: {BG_CARD}; '
            f'border: 1px solid {BORDER}; border-radius: 15px; }}'
        )
        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 14, 16, 16)
        lay.setSpacing(10)

        title = QLabel('PERFORMANCE')
        title.setStyleSheet(
            f'color: {ACCENT}; font-size: 10px; font-weight: 600; '
            f'letter-spacing: 2px; background: transparent; border: none;'
        )
        lay.addWidget(title)

        # Metrics grid: FPS | Latency  — use QGridLayout for clean two-column layout
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

        # Volume bar
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

        # Confidence bar
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


# ---------------------------------------------------------------------------
# System Panel (assembles all three cards)
# ---------------------------------------------------------------------------

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
