"""
ui/activity_timeline.py — Bottom Activity Log (Scrollable Horizontal Timeline)

Log entries arrive via StateManager.log_appended signal and are rendered as
rounded pill-style widgets that fade in from opacity 0 → 1.
"""

from __future__ import annotations

from PyQt6.QtCore    import Qt, QPropertyAnimation, QEasingCurve, pyqtSlot
from PyQt6.QtGui     import QColor, QFont
from PyQt6.QtWidgets import (QFrame, QHBoxLayout, QVBoxLayout, QLabel,
                              QScrollArea, QSizePolicy, QWidget,
                              QGraphicsOpacityEffect)

from .state_manager  import StateManager, LogEvent
from .styles         import ACCENT, TEXT_SECONDARY, BG_HOVER, BORDER


# ──────────────────────────────────────────────────────────────────────────────
# Single log pill widget
# ──────────────────────────────────────────────────────────────────────────────

class LogPill(QFrame):
    """One rounded pill entry: '[HH:MM:SS] GESTURE → ACTION'."""

    def __init__(self, event: LogEvent, parent=None):
        super().__init__(parent)
        self.setObjectName("logPill")
        self.setFixedHeight(42)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 6, 14, 6)
        layout.setSpacing(6)

        # Timestamp
        ts = QLabel(f"[{event.timestamp}]")
        ts.setObjectName("logText")
        layout.addWidget(ts)

        # Gesture (accent colour)
        g = QLabel(event.gesture)
        g.setObjectName("logAccent")
        layout.addWidget(g)

        # Arrow
        arrow = QLabel("→")
        arrow.setObjectName("logText")
        layout.addWidget(arrow)

        # Action
        a = QLabel(event.action)
        a.setObjectName("logText")
        layout.addWidget(a)

        self.adjustSize()

        # Fade-in animation
        self._opacity_effect = QGraphicsOpacityEffect(self)
        self._opacity_effect.setOpacity(0.0)
        self.setGraphicsEffect(self._opacity_effect)

        self._anim = QPropertyAnimation(self._opacity_effect, b"opacity")
        self._anim.setDuration(350)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(1.0)
        self._anim.start()

    def enterEvent(self, event) -> None:
        self.setStyleSheet(
            f"QFrame#logPill {{ background-color: #2A2A3A; "
            f"border: 1px solid {ACCENT}; border-radius: 20px; }}"
        )

    def leaveEvent(self, event) -> None:
        self.setStyleSheet("")


# ──────────────────────────────────────────────────────────────────────────────
# Timeline container
# ──────────────────────────────────────────────────────────────────────────────

class ActivityTimeline(QFrame):
    """
    Horizontally scrollable timeline panel at the bottom of the window.
    Newest entries are appended to the right; the view auto-scrolls.
    """

    MAX_PILLS = 60   # keep at most N pills in the DOM

    def __init__(self, state: StateManager, parent=None):
        super().__init__(parent)
        self._state = state
        self.setObjectName("timelineFrame")
        self.setFixedHeight(70)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self._build_ui()
        self._state.log_appended.connect(self._on_log)

        # Seed with existing events (if re-attaching to a running state)
        for event in self._state.log_events[-10:]:
            self._add_pill(event, animate=False)
            self._scroll_to_end()

    # ── Build ──────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        root = QHBoxLayout(self)
        root.setContentsMargins(14, 6, 14, 6)
        root.setSpacing(8)

        # "Activity" label on the left
        lbl = QLabel("ACTIVITY")
        lbl.setObjectName("cardTitle")
        lbl.setFixedWidth(68)
        root.addWidget(lbl, 0, Qt.AlignmentFlag.AlignVCenter)

        # Scroll area
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)

        # Inner widget
        self._inner = QWidget()
        self._inner_layout = QHBoxLayout(self._inner)
        self._inner_layout.setContentsMargins(4, 0, 4, 0)
        self._inner_layout.setSpacing(8)
        self._inner_layout.addStretch()

        self._scroll.setWidget(self._inner)
        root.addWidget(self._scroll)

        self._pills: list[LogPill] = []

    # ── Slots ──────────────────────────────────────────────────────────

    @pyqtSlot(object)
    def _on_log(self, event: LogEvent) -> None:
        self._add_pill(event, animate=True)
        self._scroll_to_end()

    # ── Helpers ────────────────────────────────────────────────────────

    def _add_pill(self, event: LogEvent, animate: bool = True) -> None:
        pill = LogPill(event)
        # Insert before the trailing stretch
        count = self._inner_layout.count()
        self._inner_layout.insertWidget(count - 1, pill)
        self._pills.append(pill)

        # Prune old pills
        while len(self._pills) > self.MAX_PILLS:
            old = self._pills.pop(0)
            self._inner_layout.removeWidget(old)
            old.deleteLater()

    def _scroll_to_end(self) -> None:
        sb = self._scroll.horizontalScrollBar()
        sb.setValue(sb.maximum())
