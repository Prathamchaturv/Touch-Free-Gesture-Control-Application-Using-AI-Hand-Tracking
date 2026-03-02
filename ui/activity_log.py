"""
ui/activity_log.py - Scrollable horizontal activity timeline at the bottom.

Each event is displayed as a coloured pill:
  ● [12:34:05]  ACTION   Open Browser  [App Mode]
  ◆ [12:34:10]  MODE     Switched to Media Mode
  ◉ [12:34:00]  SYSTEM   Pipeline started

Pills are added left-to-right; the area auto-scrolls right on new entries.
Maximum of 200 entries kept in memory (oldest are dropped).
"""

from __future__ import annotations

from PyQt6.QtCore    import Qt, pyqtSlot, QTimer
from PyQt6.QtGui     import QColor
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QScrollArea, QFrame, QSizePolicy,
)

from shared_state import SharedState
from ui.styles    import (
    BG_CARD, BG_DEEP, BORDER, ACCENT, ACTIVE, INACTIVE,
    TEXT_PRI, TEXT_SEC, TEXT_HINT,
)

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
    """A single timeline pill."""

    def __init__(self, timestamp: str, category: str, description: str) -> None:
        super().__init__()
        colour, bg = _pill_colour(category)
        self.setFixedHeight(42)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setStyleSheet(
            f'QFrame {{ background-color: {bg}; border: 1px solid {colour}33; '
            f'border-radius: 21px; }}'
        )

        lay = QHBoxLayout(self)
        lay.setContentsMargins(14, 0, 14, 0)
        lay.setSpacing(8)

        dot = QLabel('●')
        dot.setStyleSheet(
            f'color: {colour}; font-size: 10px; background: transparent; border: none;'
        )

        ts_lbl = QLabel(timestamp)
        ts_lbl.setStyleSheet(
            f'color: {TEXT_HINT}; font-size: 11px; background: transparent; border: none;'
        )

        cat_lbl = QLabel(category.upper())
        cat_lbl.setStyleSheet(
            f'color: {colour}; font-size: 10px; font-weight: 700; '
            f'letter-spacing: 1px; background: transparent; border: none;'
        )

        desc_lbl = QLabel(description)
        desc_lbl.setStyleSheet(
            f'color: {TEXT_PRI}; font-size: 12px; background: transparent; border: none;'
        )

        lay.addWidget(dot)
        lay.addWidget(ts_lbl)
        lay.addWidget(cat_lbl)
        lay.addWidget(desc_lbl)

        # Resize to content
        self.adjustSize()


class ActivityLog(QWidget):
    """
    Bottom horizontal scrollable activity timeline.
    New events are appended to the right and the view auto-scrolls.
    """

    def __init__(self, state: SharedState, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._state  = state
        self._count  = 0
        self._pills: list[EventPill] = []
        self._build()
        state.log_event.connect(self._on_log_event)

    # ------------------------------------------------------------------
    def _build(self) -> None:
        self.setFixedHeight(76)
        self.setStyleSheet(
            f'background-color: {BG_CARD}; '
            f'border-top: 1px solid {BORDER};'
        )

        outer = QVBoxLayout(self)
        outer.setContentsMargins(20, 6, 20, 6)
        outer.setSpacing(4)

        # Title
        title_row = QHBoxLayout()
        title = QLabel('ACTIVITY LOG')
        title.setStyleSheet(
            f'color: {ACCENT}; font-size: 10px; font-weight: 600; '
            f'letter-spacing: 2px; background: transparent; border: none;'
        )
        self._count_lbl = QLabel('0 events')
        self._count_lbl.setStyleSheet(
            f'color: {TEXT_HINT}; font-size: 10px; background: transparent; border: none;'
        )
        title_row.addWidget(title)
        title_row.addStretch()
        title_row.addWidget(self._count_lbl)
        outer.addLayout(title_row)

        # Scroll area
        self._scroll = QScrollArea()
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setWidgetResizable(True)
        self._scroll.setStyleSheet(
            'QScrollArea { background: transparent; border: none; }'
        )

        # Inner widget holding all pills
        self._inner = QWidget()
        self._inner.setStyleSheet('background: transparent;')
        self._pills_lay = QHBoxLayout(self._inner)
        self._pills_lay.setContentsMargins(0, 0, 0, 0)
        self._pills_lay.setSpacing(8)
        self._pills_lay.addStretch()          # right-side spacer

        self._scroll.setWidget(self._inner)
        outer.addWidget(self._scroll)

    # ------------------------------------------------------------------
    @pyqtSlot(str, str, str)
    def _on_log_event(self, timestamp: str, category: str, description: str) -> None:
        # Evict oldest if over limit
        if len(self._pills) >= MAX_EVENTS:
            old = self._pills.pop(0)
            self._pills_lay.removeWidget(old)
            old.deleteLater()

        pill = EventPill(timestamp, category, description)
        # Insert before the stretch at the end
        insert_idx = self._pills_lay.count() - 1
        self._pills_lay.insertWidget(insert_idx, pill)
        self._pills.append(pill)

        self._count += 1
        self._count_lbl.setText(f'{self._count} event{"s" if self._count != 1 else ""}')

        # Auto-scroll to the right after layout
        QTimer.singleShot(30, self._scroll_right)

    def _scroll_right(self) -> None:
        sb = self._scroll.horizontalScrollBar()
        sb.setValue(sb.maximum())
