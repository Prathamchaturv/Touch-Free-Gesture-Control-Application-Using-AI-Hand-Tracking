"""
ui/sidebar.py - Collapsible sidebar with Vision + Mode tabs only.

Layout (expanded, 220 px wide)
-------------------------------
┌──────────────────────────────┐
│  ≡  MMGI              ◄      │  ← collapse button
├──────────────────────────────┤
│  ◉  Vision                   │  ← nav tab
│  ⊞  Mode                     │  ← nav tab
├──────────────────────────────┤
│  v0.3  Smart Mode            │  ← footer version badge
└──────────────────────────────┘

Collapsed: 56 px wide, icons only, no labels.
"""

from __future__ import annotations

from PyQt6.QtCore    import Qt, QPropertyAnimation, QEasingCurve, pyqtSignal, QSize
from PyQt6.QtGui     import QIcon, QFont
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QSizePolicy, QFrame, QSpacerItem,
)

from ui.styles import (
    BG_CARD, BORDER, ACCENT, TEXT_PRI, TEXT_SEC, TEXT_HINT, BG_HOVER,
)

EXPANDED_W  = 220
COLLAPSED_W = 56
ANIM_MS     = 200

_TABS = [
    ('vision', '◉', 'Vision'),
    ('mode',   '⊞', 'Mode'),
]


class Sidebar(QWidget):
    """Animated collapsible sidebar."""

    tab_selected = pyqtSignal(str)   # emits tab id on click

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._collapsed  = False
        self._active_tab = 'vision'
        self._nav_btns: dict[str, QPushButton] = {}

        self.setFixedWidth(EXPANDED_W)
        self._build_ui()
        self._select_tab('vision')

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {BG_CARD};
                border-right: 1px solid {BORDER};
            }}
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Header ──────────────────────────────
        header = QWidget()
        header.setFixedHeight(60)
        header.setStyleSheet(f'background: transparent; border-bottom: 1px solid {BORDER};')
        h_lay = QHBoxLayout(header)
        h_lay.setContentsMargins(12, 0, 8, 0)

        self._logo_label = QLabel('MMGI')
        self._logo_label.setStyleSheet(
            f'color: {ACCENT}; font-size: 16px; font-weight: 700; '
            f'letter-spacing: 3px; border: none;'
        )

        self._collapse_btn = QPushButton('◄')
        self._collapse_btn.setFixedSize(30, 30)
        self._collapse_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._collapse_btn.setToolTip('Collapse sidebar')
        self._collapse_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {TEXT_SEC};
                border: none;
                font-size: 12px;
                border-radius: 6px;
            }}
            QPushButton:hover {{
                background: {BG_HOVER};
                color: {ACCENT};
            }}
        """)
        self._collapse_btn.clicked.connect(self.toggle_collapse)

        h_lay.addWidget(self._logo_label)
        h_lay.addStretch()
        h_lay.addWidget(self._collapse_btn)
        root.addWidget(header)

        # ── Nav buttons ─────────────────────────
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

        # ── Footer ──────────────────────────────
        footer = QLabel('v0.3  Smart Mode')
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setFixedHeight(36)
        footer.setStyleSheet(
            f'color: {TEXT_HINT}; font-size: 11px; '
            f'border-top: 1px solid {BORDER}; background: transparent;'
        )
        self._footer = footer
        root.addWidget(footer)

    # ------------------------------------------------------------------
    # Tab selection
    # ------------------------------------------------------------------

    def _select_tab(self, tab_id: str) -> None:
        self._active_tab = tab_id
        for tid, btn in self._nav_btns.items():
            selected = (tid == tab_id)
            btn.setProperty('selected', selected)
            btn.style().unpolish(btn)
            btn.style().polish(btn)
            # Manual colour override (dynamic property styling is unreliable)
            if selected:
                btn.setStyleSheet(self._nav_btn_style(selected=True))
            else:
                btn.setStyleSheet(self._nav_btn_style(selected=False))
        self.tab_selected.emit(tab_id)

    # ------------------------------------------------------------------
    # Collapse / expand
    # ------------------------------------------------------------------

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
        # Keep reference alive
        self._anim = anim

        # Fix maximum width too so layout snaps
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

        # Switch button text
        for tab_id, icon, label in _TABS:
            btn = self._nav_btns[tab_id]
            btn.setText(icon if self._collapsed else f'{icon}  {label}')

    # ------------------------------------------------------------------
    # Style helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _nav_btn_style(selected: bool = False) -> str:
        if selected:
            return (
                f'QPushButton {{ background-color: rgba(0,229,255,0.12); '
                f'color: {ACCENT}; font-weight: 600; '
                f'border: none; border-radius: 10px; '
                f'padding: 10px 16px; text-align: left; font-size: 13px; }}'
            )
        return (
            f'QPushButton {{ background: transparent; color: {TEXT_SEC}; '
            f'border: none; border-radius: 10px; '
            f'padding: 10px 16px; text-align: left; font-size: 13px; }}'
            f'QPushButton:hover {{ background-color: {BG_HOVER}; color: {TEXT_PRI}; }}'
        )
