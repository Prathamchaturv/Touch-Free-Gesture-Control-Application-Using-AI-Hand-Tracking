"""
ui/main_window.py - Top-level MMGI dashboard window.

Window layout
─────────────
┌────────────────────────────────────────────────────────┐
│  Header  :  ◉ MMGI  Smart Mode AI Controller     ⬜⬛▢  │
├────────────────────────────────────────────────────────┤
│ Sidebar │   Vision Panel (centre)    │  System Panel   │
│  220 px │       (stretches)          │    340 px       │
├─────────┴────────────────────────────┴─────────────────┤
│                   Activity Log (76 px)                  │
└────────────────────────────────────────────────────────┘

The WorkerThread is started immediately on launch.
Stopping is handled by the window close event.
"""

from __future__ import annotations

from PyQt6.QtCore    import Qt, pyqtSlot
from PyQt6.QtGui     import QCloseEvent
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QFrame, QMessageBox,
)

from shared_state  import SharedState
from worker_thread import WorkerThread
from ui.styles     import (
    GLOBAL_QSS, BG_DEEP, BG_CARD, BORDER, ACCENT,
    ACTIVE, INACTIVE, TEXT_PRI, TEXT_SEC, TEXT_HINT,
)
from ui.sidebar      import Sidebar
from ui.vision_panel import VisionPanel
from ui.system_panel import SystemPanel
from ui.activity_log import ActivityLog


class MainWindow(QMainWindow):
    """MMGI AI dashboard main window."""

    WINDOW_TITLE   = 'MMGI  —  Smart Mode AI Gesture Controller'
    MIN_W, MIN_H   = 1100, 650

    def __init__(self) -> None:
        super().__init__()
        self._state  = SharedState(self)
        self._worker: WorkerThread | None = None

        self._setup_window()
        self._build_ui()
        self._start_worker()

    # ------------------------------------------------------------------
    # Window setup
    # ------------------------------------------------------------------

    def _setup_window(self) -> None:
        self.setWindowTitle(self.WINDOW_TITLE)
        self.setMinimumSize(self.MIN_W, self.MIN_H)
        self.resize(1280, 720)
        self.setStyleSheet(GLOBAL_QSS)

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Header ────────────────────────────────────────
        root.addWidget(self._build_header())

        # ── Main body (sidebar + vision + system) ─────────
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

        # ── Activity log ──────────────────────────────────
        self._activity = ActivityLog(self._state)
        root.addWidget(self._activity)

    def _build_header(self) -> QWidget:
        header = QWidget()
        header.setFixedHeight(52)
        header.setStyleSheet(
            f'background-color: {BG_CARD}; border-bottom: 1px solid {BORDER};'
        )

        lay = QHBoxLayout(header)
        lay.setContentsMargins(20, 0, 20, 0)
        lay.setSpacing(12)

        # Logo + title
        dot = QLabel('◉')
        dot.setStyleSheet(f'color: {ACCENT}; font-size: 14px;')
        self._header_dot = dot

        title = QLabel('MMGI')
        title.setStyleSheet(
            f'color: {ACCENT}; font-size: 15px; font-weight: 700; letter-spacing: 3px;'
        )

        subtitle = QLabel('Smart Mode AI Controller')
        subtitle.setStyleSheet(f'color: {TEXT_HINT}; font-size: 12px;')

        # Status badge (right)
        self._header_status = QLabel('⬤  INACTIVE')
        self._header_status.setStyleSheet(
            f'color: {INACTIVE}; font-size: 12px; font-weight: 600;'
        )

        # Mode badge (right)
        self._header_mode = QLabel('APP MODE')
        self._header_mode.setStyleSheet(
            f'color: {ACCENT}; font-size: 11px; font-weight: 700; '
            f'letter-spacing: 1px; background: rgba(0,229,255,0.10); '
            f'border: 1px solid {ACCENT}; border-radius: 10px; padding: 2px 10px;'
        )

        lay.addWidget(dot)
        lay.addWidget(title)
        lay.addWidget(subtitle)
        lay.addStretch()
        lay.addWidget(self._header_mode)
        lay.addWidget(self._header_status)

        # Connect state
        self._state.system_active_changed.connect(self._on_active_header)
        self._state.mode_changed.connect(self._on_mode_header)

        return header

    # ------------------------------------------------------------------
    # Worker thread
    # ------------------------------------------------------------------

    def _start_worker(self) -> None:
        self._worker = WorkerThread(self._state, parent=self)
        self._worker.frame_ready.connect(self._vision.update_frame)
        self._worker.error.connect(self._on_worker_error)
        self._worker.start()

    # ------------------------------------------------------------------
    # State-driven header updates
    # ------------------------------------------------------------------

    @pyqtSlot(bool)
    def _on_active_header(self, active: bool) -> None:
        if active:
            self._header_status.setText('⬤  ACTIVE')
            self._header_status.setStyleSheet(
                f'color: {ACTIVE}; font-size: 12px; font-weight: 600;'
            )
        else:
            self._header_status.setText('⬤  INACTIVE')
            self._header_status.setStyleSheet(
                f'color: {INACTIVE}; font-size: 12px; font-weight: 600;'
            )

    @pyqtSlot(str)
    def _on_mode_header(self, mode: str) -> None:
        from ui.styles import MODE_APP, MODE_MEDIA, MODE_SYSTEM
        colour_map = {
            'App Mode':    MODE_APP,
            'Media Mode':  MODE_MEDIA,
            'System Mode': MODE_SYSTEM,
        }
        colour = colour_map.get(mode, ACCENT)
        short  = mode.replace(' Mode', '').upper() + ' MODE'
        self._header_mode.setText(short)
        self._header_mode.setStyleSheet(
            f'color: {colour}; font-size: 11px; font-weight: 700; '
            f'letter-spacing: 1px; background: rgba(0,229,255,0.10); '
            f'border: 1px solid {colour}; border-radius: 10px; padding: 2px 10px;'
        )

    # ------------------------------------------------------------------
    # Error handling
    # ------------------------------------------------------------------

    @pyqtSlot(str)
    def _on_worker_error(self, msg: str) -> None:
        self._state.emit_log('--:--:--', 'ERROR', msg.split('\n')[0])
        QMessageBox.critical(
            self,
            'Pipeline Error',
            f'The gesture pipeline encountered an error:\n\n{msg[:400]}',
        )

    # ------------------------------------------------------------------
    # Close
    # ------------------------------------------------------------------

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        if self._worker is not None and self._worker.isRunning():
            self._worker.stop()
            self._worker.wait(3000)
        event.accept()
