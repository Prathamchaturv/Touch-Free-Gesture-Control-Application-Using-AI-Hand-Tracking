"""
ui/sidebar.py — Collapsible Navigation Sidebar

Vertical panel with icon + label nav buttons.
Collapses to icon-only strip (60 px) via animated QPropertyAnimation.
"""

from __future__ import annotations

from PyQt6.QtCore  import (Qt, QPropertyAnimation, QEasingCurve,
                            QSize, pyqtSlot)
from PyQt6.QtGui   import QIcon, QFont
from PyQt6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout,
                              QPushButton, QLabel, QSizePolicy,
                              QSpacerItem, QWidget)


# ── Nav item definitions ──────────────────────────────────────────────────────

NAV_ITEMS = [
    ("Vision",    "󰓾",  True),   # default selected
    ("Modes",     "󰆈",  False),
    ("Analytics", "󰄒",  False),
    ("Logs",      "󱂅",  False),
    ("Security",  "󰒿",  False),
]

# Unicode fallback symbols (used if emoji font unavailable)
NAV_ICONS = {
    "Vision":    "⊙",
    "Modes":     "⊞",
    "Analytics": "≋",
    "Logs":      "☰",
    "Security":  "⊛",
}

EXPANDED_WIDTH  = 200
COLLAPSED_WIDTH = 60
ANIM_DURATION   = 220   # ms


class NavButton(QPushButton):
    """Single sidebar nav entry with icon + optional text."""

    def __init__(self, label: str, icon_char: str, parent=None):
        super().__init__(parent)
        self._label     = label
        self._icon_char = icon_char
        self._expanded  = True

        self.setObjectName("navButton")
        self.setCheckable(True)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMinimumHeight(44)
        self._refresh_text()

    def set_expanded(self, expanded: bool) -> None:
        self._expanded = expanded
        self._refresh_text()

    def _refresh_text(self) -> None:
        if self._expanded:
            self.setText(f"  {self._icon_char}   {self._label}")
        else:
            self.setText(self._icon_char)
            self.setToolTip(self._label)


class Sidebar(QFrame):
    """Animated collapsible sidebar."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebarFrame")
        self._expanded = True
        self._buttons: list[NavButton] = []

        self._build_ui()
        self._setup_animation()

    # ── Construction ──────────────────────────────────────────────────
    def _build_ui(self) -> None:
        self.setFixedWidth(EXPANDED_WIDTH)

        root = QVBoxLayout(self)
        root.setContentsMargins(10, 12, 10, 12)
        root.setSpacing(4)

        # ── Top: logo area + collapse button ──────────────────────────
        top_row = QHBoxLayout()
        top_row.setContentsMargins(0, 0, 0, 0)

        self._logo_label = QLabel("MMGI")
        self._logo_label.setObjectName("appTitle")
        font = QFont("Segoe UI", 11, QFont.Weight.Bold)
        self._logo_label.setFont(font)
        top_row.addWidget(self._logo_label)
        top_row.addStretch()

        self._collapse_btn = QPushButton("◀")
        self._collapse_btn.setObjectName("collapseBtn")
        self._collapse_btn.setFixedSize(28, 28)
        self._collapse_btn.clicked.connect(self.toggle)
        top_row.addWidget(self._collapse_btn)

        root.addLayout(top_row)

        # ── Divider ────────────────────────────────────────────────────
        div = QFrame()
        div.setObjectName("divider")
        div.setFixedHeight(1)
        root.addWidget(div)
        root.addSpacing(6)

        # ── Nav buttons ────────────────────────────────────────────────
        for label, _, selected in NAV_ITEMS:
            icon = NAV_ICONS.get(label, "•")
            btn  = NavButton(label, icon)
            btn.setChecked(selected)
            btn.clicked.connect(lambda checked, b=btn: self._on_nav_clicked(b))
            self._buttons.append(btn)
            root.addWidget(btn)

        root.addStretch()

        # ── Bottom: version ────────────────────────────────────────────
        self._version_label = QLabel("v7.0  ·  PyQt6")
        self._version_label.setObjectName("metricLabel")
        self._version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(self._version_label)

    def _setup_animation(self) -> None:
        self._anim = QPropertyAnimation(self, b"maximumWidth")
        self._anim.setDuration(ANIM_DURATION)
        self._anim.setEasingCurve(QEasingCurve.Type.InOutQuart)

    # ── Public API ────────────────────────────────────────────────────

    @pyqtSlot()
    def toggle(self) -> None:
        if self._expanded:
            self._collapse()
        else:
            self._expand()

    def _expand(self) -> None:
        self._expanded = True
        self._collapse_btn.setText("◀")
        self._logo_label.setVisible(True)
        self._version_label.setVisible(True)
        for btn in self._buttons:
            btn.set_expanded(True)

        self._anim.stop()
        self._anim.setStartValue(self.width())
        self._anim.setEndValue(EXPANDED_WIDTH)
        self._anim.start()

    def _collapse(self) -> None:
        self._expanded = False
        self._collapse_btn.setText("▶")
        self._logo_label.setVisible(False)
        self._version_label.setVisible(False)
        for btn in self._buttons:
            btn.set_expanded(False)

        self._anim.stop()
        self._anim.setStartValue(self.width())
        self._anim.setEndValue(COLLAPSED_WIDTH)
        self._anim.start()

    def _on_nav_clicked(self, clicked: NavButton) -> None:
        for btn in self._buttons:
            btn.setChecked(btn is clicked)
