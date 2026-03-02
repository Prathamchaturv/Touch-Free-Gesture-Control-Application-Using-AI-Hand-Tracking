"""
ui/status_panel.py — Right Status Panel (3 stacked cards)

Cards:
  A) System  — status, latency, cooldown timer
  B) Mode    — current mode, gesture→action preview
  C) Performance — FPS, accuracy %, execution rate %
"""

from __future__ import annotations

from PyQt6.QtCore    import Qt, pyqtSlot
from PyQt6.QtGui     import QFont, QColor
from PyQt6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout,
                              QLabel, QProgressBar, QSizePolicy,
                              QGraphicsDropShadowEffect, QScrollArea,
                              QWidget)

from .state_manager  import StateManager
from .styles         import ACCENT, GREEN_ACTIVE, RED_INACTIVE, TEXT_SECONDARY


# ──────────────────────────────────────────────────────────────────────────────
# Helper widgets
# ──────────────────────────────────────────────────────────────────────────────

def _card_shadow() -> QGraphicsDropShadowEffect:
    s = QGraphicsDropShadowEffect()
    s.setBlurRadius(20)
    s.setColor(QColor(0, 0, 0, 120))
    s.setOffset(0, 4)
    return s


def _title_label(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setObjectName("cardTitle")
    return lbl


def _value_label(text: str = "—", accent=False) -> QLabel:
    lbl = QLabel(text)
    lbl.setObjectName("cardValueAccent" if accent else "cardValue")
    return lbl


def _metric_row(label: str, value: str = "—") -> tuple[QHBoxLayout, QLabel]:
    """Returns (layout, value_label) for a metric row."""
    row = QHBoxLayout()
    row.setContentsMargins(0, 0, 0, 0)
    l = QLabel(label)
    l.setObjectName("metricLabel")
    v = QLabel(value)
    v.setObjectName("metricValue")
    v.setAlignment(Qt.AlignmentFlag.AlignRight)
    row.addWidget(l)
    row.addStretch()
    row.addWidget(v)
    return row, v


# ──────────────────────────────────────────────────────────────────────────────
# Individual cards
# ──────────────────────────────────────────────────────────────────────────────

class SystemCard(QFrame):
    """Card A — ACTIVE/INACTIVE status, latency, cooldown bar."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setGraphicsEffect(_card_shadow())

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 14, 16, 14)
        root.setSpacing(10)

        root.addWidget(_title_label("SYSTEM"))

        # Large status value
        self._status_lbl = QLabel("INACTIVE")
        self._status_lbl.setObjectName("cardValueRed")
        font = QFont("Segoe UI", 20, QFont.Weight.Bold)
        self._status_lbl.setFont(font)
        root.addWidget(self._status_lbl)

        # Metric rows
        row_lat, self._latency_val   = _metric_row("Latency")
        row_cd,  self._cooldown_val  = _metric_row("Cooldown")
        root.addLayout(row_lat)
        root.addLayout(row_cd)

        # Cooldown progress bar
        self._cooldown_bar = QProgressBar()
        self._cooldown_bar.setObjectName("cooldownBar")
        self._cooldown_bar.setRange(0, 100)
        self._cooldown_bar.setValue(0)
        self._cooldown_bar.setFixedHeight(5)
        self._cooldown_bar.setTextVisible(False)
        root.addWidget(self._cooldown_bar)

    @pyqtSlot()
    def refresh(self, state: StateManager) -> None:
        status = state.system_status
        self._status_lbl.setText(status)
        if status == "ACTIVE":
            self._status_lbl.setObjectName("cardValueGreen")
        elif status == "ACTIVATING":
            self._status_lbl.setObjectName("cardValueAccent")
        else:
            self._status_lbl.setObjectName("cardValueRed")
        self._status_lbl.style().unpolish(self._status_lbl)
        self._status_lbl.style().polish(self._status_lbl)

        self._latency_val.setText(f"{state.latency_ms:.1f} ms")
        cooldown_pct = int(state.cooldown_remaining * 100)
        self._cooldown_val.setText(f"{state.cooldown_remaining:.2f}s")
        self._cooldown_bar.setValue(cooldown_pct)


class ModeCard(QFrame):
    """Card B — Current mode and gesture→action preview."""

    # Preview map shown in the card
    _PREVIEW: list[tuple[str, str]] = [
        ("☝  One Finger",    "Launch Browser"),
        ("✌  Two Fingers",   "Launch Music"),
        ("🤟 Ring + Pinky",  "Next Track"),
        ("👆 Pinky",         "Prev Track"),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setGraphicsEffect(_card_shadow())

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 14, 16, 14)
        root.setSpacing(8)

        root.addWidget(_title_label("MODE"))

        self._mode_lbl = _value_label("STANDBY", accent=True)
        self._mode_lbl.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        root.addWidget(self._mode_lbl)

        # Divider
        div = QFrame()
        div.setObjectName("divider")
        root.addWidget(div)

        # Gesture→action mini-map
        for gesture, action in self._PREVIEW:
            row = QHBoxLayout()
            row.setContentsMargins(0, 0, 0, 0)
            g_lbl = QLabel(gesture)
            g_lbl.setObjectName("metricLabel")
            a_lbl = QLabel(action)
            a_lbl.setObjectName("metricValue")
            a_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
            row.addWidget(g_lbl)
            row.addStretch()
            row.addWidget(a_lbl)
            root.addLayout(row)

    @pyqtSlot()
    def refresh(self, state: StateManager) -> None:
        self._mode_lbl.setText(state.mode)


class PerformanceCard(QFrame):
    """Card C — FPS, accuracy, execution rate with mini progress bars."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setGraphicsEffect(_card_shadow())

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 14, 16, 14)
        root.setSpacing(10)

        root.addWidget(_title_label("PERFORMANCE"))

        self._metrics: dict[str, tuple[QLabel, QProgressBar]] = {}

        for key, label in [("fps", "FPS"), ("accuracy", "Accuracy"),
                            ("exec_rate", "Exec Rate")]:
            row, bar = self._add_metric_bar(root, label)
            self._metrics[key] = (row, bar)

    def _add_metric_bar(
        self, parent_layout: QVBoxLayout, label: str
    ) -> tuple[QLabel, QProgressBar]:
        h = QHBoxLayout()
        h.setContentsMargins(0, 0, 0, 0)
        l = QLabel(label)
        l.setObjectName("metricLabel")
        v = QLabel("0")
        v.setObjectName("metricValue")
        v.setFixedWidth(48)
        v.setAlignment(Qt.AlignmentFlag.AlignRight)
        h.addWidget(l)
        h.addStretch()
        h.addWidget(v)
        parent_layout.addLayout(h)

        bar = QProgressBar()
        bar.setRange(0, 100)
        bar.setValue(0)
        bar.setFixedHeight(5)
        bar.setTextVisible(False)
        parent_layout.addWidget(bar)

        return v, bar

    @pyqtSlot()
    def refresh(self, state: StateManager) -> None:
        fps_val, fps_bar         = self._metrics["fps"]
        acc_val, acc_bar         = self._metrics["accuracy"]
        exec_val, exec_bar       = self._metrics["exec_rate"]

        fps_capped = min(int(state.fps), 60)
        fps_val.setText(f"{state.fps:.0f}")
        fps_bar.setValue(int(fps_capped / 60 * 100))

        acc_val.setText(f"{state.accuracy_pct:.0f}%")
        acc_bar.setValue(int(state.accuracy_pct))

        exec_val.setText(f"{state.execution_rate_pct:.0f}%")
        exec_bar.setValue(int(state.execution_rate_pct))


# ──────────────────────────────────────────────────────────────────────────────
# Status Panel — container for all three cards
# ──────────────────────────────────────────────────────────────────────────────

class StatusPanel(QFrame):
    """Right-side panel stacking System, Mode, and Performance cards."""

    def __init__(self, state: StateManager, parent=None):
        super().__init__(parent)
        self._state = state
        self.setFixedWidth(260)
        self.setSizePolicy(QSizePolicy.Policy.Fixed,
                           QSizePolicy.Policy.Expanding)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(10)

        self._system_card = SystemCard()
        self._mode_card   = ModeCard()
        self._perf_card   = PerformanceCard()

        root.addWidget(self._system_card)
        root.addWidget(self._mode_card)
        root.addWidget(self._perf_card)
        root.addStretch()

        # Connect to state updates
        self._state.state_updated.connect(self._on_state_updated)

    @pyqtSlot()
    def _on_state_updated(self) -> None:
        self._system_card.refresh(self._state)
        self._mode_card.refresh(self._state)
        self._perf_card.refresh(self._state)
