"""
ui/vision_panel.py - Live camera feed panel with overlay and stability bar.

Layout (centre panel)
─────────────────────
┌─────────────────────────────────────┐
│  ┌───────────────────────────────┐  │  ← glow border (neon when active)
│  │                               │  │
│  │     Live Camera Feed          │  │
│  │     + hand skeleton overlay   │  │
│  │                               │  │
│  └───────────────────────────────┘  │
│  MODE: APP MODE   Gesture: Fist     │  ← info strip
│  [========= Mode Switch Progress ]  │  ← stability bar
└─────────────────────────────────────┘
"""

from __future__ import annotations

from PyQt6.QtCore    import Qt, pyqtSlot
from PyQt6.QtGui     import QImage, QPixmap, QColor
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QProgressBar, QFrame, QSizePolicy,
)

from shared_state import SharedState
from ui.styles    import (
    BG_CARD, BG_DEEP, BORDER, ACCENT, ACTIVE, INACTIVE,
    TEXT_PRI, TEXT_SEC, TEXT_HINT, MODE_APP, MODE_MEDIA, MODE_SYSTEM,
)

_MODE_ACCENT = {
    'App Mode':    MODE_APP,
    'Media Mode':  MODE_MEDIA,
    'System Mode': MODE_SYSTEM,
}


class VisionPanel(QWidget):
    """
    Displays the annotated live camera frame with mode/gesture labels
    and a mode-switch stability progress bar.
    """

    def __init__(self, state: SharedState, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._state = state
        self._build_ui()
        self._connect_state()

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        self.setStyleSheet(f'background-color: {BG_DEEP};')

        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(12)

        # ── Camera frame container ────────────────────────
        self._cam_frame = QFrame()
        self._cam_frame.setObjectName('cam_frame')
        self._cam_frame.setStyleSheet(
            f'QFrame#cam_frame {{'
            f'  background-color: #000000;'
            f'  border: 2px solid {BORDER};'
            f'  border-radius: 16px;'
            f'}}'
        )
        cam_lay = QVBoxLayout(self._cam_frame)
        cam_lay.setContentsMargins(0, 0, 0, 0)

        self._video_label = QLabel()
        self._video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._video_label.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self._video_label.setStyleSheet('background: transparent; border: none;')
        self._video_label.setMinimumSize(480, 270)

        # Placeholder
        self._video_label.setText('⬤  Waiting for camera…')
        self._video_label.setStyleSheet(
            f'color: {TEXT_HINT}; font-size: 16px; background: transparent; border: none;'
        )
        cam_lay.addWidget(self._video_label)
        root.addWidget(self._cam_frame, stretch=1)

        # ── Info strip ───────────────────────────────────
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
        self._gesture_val.setStyleSheet(
            f'color: {TEXT_PRI}; font-size: 13px; font-weight: 600;'
        )

        info_row.addWidget(self._mode_pill)
        info_row.addStretch()
        info_row.addWidget(gesture_lbl)
        info_row.addWidget(self._gesture_val)
        root.addLayout(info_row)

        # ── Stability bar ────────────────────────────────
        stab_lbl = QLabel('MODE SWITCH HOLD')
        stab_lbl.setStyleSheet(
            f'color: {TEXT_HINT}; font-size: 10px; letter-spacing: 1px;'
        )

        self._stability_bar = QProgressBar()
        self._stability_bar.setObjectName('stability_bar')
        self._stability_bar.setRange(0, 100)
        self._stability_bar.setValue(0)
        self._stability_bar.setFixedHeight(8)
        self._stability_bar.setTextVisible(False)
        self._stability_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {BORDER};
                border-radius: 4px;
                border: none;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {ACTIVE}, stop:1 {ACCENT});
                border-radius: 4px;
            }}
        """)

        root.addWidget(stab_lbl)
        root.addWidget(self._stability_bar)

    # ------------------------------------------------------------------
    # State connections
    # ------------------------------------------------------------------

    def _connect_state(self) -> None:
        s = self._state
        s.mode_changed.connect(self._on_mode_changed)
        s.gesture_changed.connect(self._on_gesture_changed)
        s.mode_stability_changed.connect(self._on_stability_changed)
        s.system_active_changed.connect(self._on_active_changed)

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------

    @pyqtSlot(QImage)
    def update_frame(self, image: QImage) -> None:
        """Called from WorkerThread.frame_ready — display annotated frame."""
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
        # Remove placeholder text style once real frame arrives
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
        # Glow border on camera frame
        self._cam_frame.setStyleSheet(
            f'QFrame#cam_frame {{'
            f'  background-color: #000000;'
            f'  border: 2px solid {colour};'
            f'  border-radius: 16px;'
            f'}}'
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
            f'QFrame#cam_frame {{'
            f'  background-color: #000000;'
            f'  border: 2px solid {border_colour};'
            f'  border-radius: 16px;'
            f'}}'
        )
