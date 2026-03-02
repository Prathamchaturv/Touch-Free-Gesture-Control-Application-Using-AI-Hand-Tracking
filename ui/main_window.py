"""
ui/main_window.py — MMGI Premium Dashboard Window

Assembles header + sidebar + vision panel + status panel + activity timeline
into a single QMainWindow.  Wires state signals from the worker/simulator
thread to the StateManager, which propagates changes to all panels.
"""

from __future__ import annotations

from PyQt6.QtCore    import Qt, QSize, pyqtSlot
from PyQt6.QtGui     import QColor, QFont, QIcon
from PyQt6.QtWidgets import (QMainWindow, QWidget, QFrame,
                              QVBoxLayout, QHBoxLayout, QLabel,
                              QSizePolicy, QApplication,
                              QGraphicsDropShadowEffect)

from .state_manager      import StateManager
from .sidebar            import Sidebar
from .vision_panel       import VisionPanel, StatusDot
from .status_panel       import StatusPanel
from .activity_timeline  import ActivityTimeline
from .styles             import DARK_QSS, ACCENT, BG_CARD, BORDER


# ──────────────────────────────────────────────────────────────────────────────
# Header bar
# ──────────────────────────────────────────────────────────────────────────────

class HeaderBar(QFrame):
    """Top bar with title, sub-title and live status dot."""

    def __init__(self, state: StateManager, parent=None):
        super().__init__(parent)
        self._state = state
        self.setObjectName("headerFrame")
        self.setFixedHeight(56)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setSpacing(12)

        # Title block
        title_block = QVBoxLayout()
        title_block.setSpacing(0)

        title = QLabel("MMGI")
        title.setObjectName("appTitle")

        subtitle = QLabel("Multi-Modal Gesture Intelligence  ·  v7.0")
        subtitle.setObjectName("appSubtitle")

        title_block.addWidget(title)
        title_block.addWidget(subtitle)
        layout.addLayout(title_block)
        layout.addStretch()

        # Live status dot + label
        self._dot = StatusDot()
        layout.addWidget(self._dot, 0, Qt.AlignmentFlag.AlignVCenter)

        self._status_lbl = QLabel("INACTIVE")
        self._status_lbl.setObjectName("cardValueRed")
        layout.addWidget(self._status_lbl, 0, Qt.AlignmentFlag.AlignVCenter)

        self._state.state_updated.connect(self._refresh)

    @pyqtSlot()
    def _refresh(self) -> None:
        status = self._state.system_status
        self._dot.set_active(status == "ACTIVE")
        self._status_lbl.setText(status)
        if status == "ACTIVE":
            self._status_lbl.setObjectName("cardValueGreen")
        elif status == "ACTIVATING":
            self._status_lbl.setObjectName("cardValueAccent")
        else:
            self._status_lbl.setObjectName("cardValueRed")
        self._status_lbl.style().unpolish(self._status_lbl)
        self._status_lbl.style().polish(self._status_lbl)


# ──────────────────────────────────────────────────────────────────────────────
# Main Window
# ──────────────────────────────────────────────────────────────────────────────

class MainWindow(QMainWindow):
    """
    MMGI Premium Dashboard.

    Parameters
    ----------
    state:
        Shared :class:`StateManager`.  Pass ``None`` to create a fresh one.
    simulate:
        If True, starts the built-in fake-data simulator instead of the
        real MMGI pipeline.
    """

    def __init__(self, state: StateManager | None = None,
                 simulate: bool = True):
        super().__init__()

        self._state    = state or StateManager()
        self._simulate = simulate
        self._worker   = None

        self._setup_window()
        self._apply_stylesheet()
        self._build_ui()
        self._start_data_source()

    # ── Window chrome ─────────────────────────────────────────────────

    def _setup_window(self) -> None:
        self.setWindowTitle("MMGI — AI Gesture Dashboard")
        self.setMinimumSize(1280, 720)
        self.resize(1440, 860)

    def _apply_stylesheet(self) -> None:
        QApplication.instance().setStyleSheet(DARK_QSS)

    # ── Build UI ──────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        root = QWidget()
        root.setObjectName("centralWidget")
        self.setCentralWidget(root)

        outer = QVBoxLayout(root)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # ── Header ─────────────────────────────────────────────────────
        self._header = HeaderBar(self._state)
        outer.addWidget(self._header)

        # ── Mid section (sidebar + vision + status) ────────────────────
        mid = QHBoxLayout()
        mid.setContentsMargins(12, 12, 12, 0)
        mid.setSpacing(12)

        self._sidebar      = Sidebar()
        self._vision_panel = VisionPanel(self._state)
        self._status_panel = StatusPanel(self._state)

        mid.addWidget(self._sidebar)
        mid.addWidget(self._vision_panel, stretch=3)
        mid.addWidget(self._status_panel)

        outer.addLayout(mid, stretch=1)

        # ── Bottom Activity Timeline ────────────────────────────────────
        self._timeline = ActivityTimeline(self._state)
        outer.addWidget(self._timeline)

    # ── Data source ────────────────────────────────────────────────────

    def _start_data_source(self) -> None:
        if self._simulate:
            from .simulator import SimulatorThread
            self._worker = SimulatorThread(self)
        else:
            from .mmgi_thread import MMGIWorkerThread
            self._worker = MMGIWorkerThread(self)
            self._worker.error.connect(self._on_worker_error)

        # Wire signals
        self._worker.frame_ready.connect(self._vision_panel.update_frame)
        self._worker.state_changed.connect(self._on_state_changed)
        self._worker.log_event.connect(self._state.add_log)

        self._worker.start()

    # ── Slots ──────────────────────────────────────────────────────────

    @pyqtSlot(dict)
    def _on_state_changed(self, data: dict) -> None:
        """Receive state dict from worker and forward to StateManager."""
        self._state.update(**data)

    @pyqtSlot(str)
    def _on_worker_error(self, msg: str) -> None:
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.critical(self, "MMGI Error", msg)

    # ── Cleanup ────────────────────────────────────────────────────────

    def closeEvent(self, event) -> None:
        if self._worker and self._worker.isRunning():
            self._worker.stop()
            self._worker.wait(3000)
        super().closeEvent(event)
