"""
ui/vision_panel.py — Live Vision Section (Centre Panel)

Large card-style camera feed with overlay labels, stability bar, and
a glowing border when the system is ACTIVE.

Camera frames are fed in as QImage via :meth:`update_frame`.
"""

from __future__ import annotations

import math

from PyQt6.QtCore    import Qt, QTimer, pyqtSlot
from PyQt6.QtGui     import (QImage, QPixmap, QPainter, QColor,
                              QRadialGradient, QPen, QFont)
from PyQt6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout,
                              QLabel, QProgressBar, QSizePolicy,
                              QWidget, QGraphicsDropShadowEffect)

from .state_manager  import StateManager
from .styles         import (ACCENT, GREEN_ACTIVE, RED_INACTIVE,
                              TEXT_SECONDARY, BG_DEEP, BG_CARD_ALT)


# ──────────────────────────────────────────────────────────────────────────────
# Animated status dot (pulsing glow)
# ──────────────────────────────────────────────────────────────────────────────

class StatusDot(QWidget):
    """Small pulsing dot — green (ACTIVE) or red (INACTIVE)."""

    _DOT_RADIUS = 6

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(28, 28)
        self._active = False
        self._phase  = 0.0

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(40)   # ~25 fps pulse

    def set_active(self, active: bool) -> None:
        self._active = active

    def _tick(self) -> None:
        self._phase = (self._phase + 0.12) % (2 * math.pi)
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        cx, cy = self.width() // 2, self.height() // 2
        r = self._DOT_RADIUS

        if self._active:
            core_color = QColor(GREEN_ACTIVE)
            pulse_r    = int(r * 1.8 + r * 0.6 * math.sin(self._phase))

            # Glow halo
            grad = QRadialGradient(cx, cy, pulse_r)
            grad.setColorAt(0.0, QColor(0, 255, 136, 140))
            grad.setColorAt(1.0, QColor(0, 255, 136, 0))
            painter.setBrush(grad)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(cx - pulse_r, cy - pulse_r,
                                pulse_r * 2, pulse_r * 2)
        else:
            core_color = QColor(RED_INACTIVE)

        painter.setBrush(core_color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(cx - r, cy - r, r * 2, r * 2)


# ──────────────────────────────────────────────────────────────────────────────
# Overlay info bar (gesture / confidence / mode / status)
# ──────────────────────────────────────────────────────────────────────────────

def _label_pair(title: str, value_name: str) -> tuple[QLabel, QLabel]:
    """Create a title + value label pair and return them."""
    t = QLabel(title)
    t.setObjectName("overlayLabel")

    v = QLabel("—")
    v.setObjectName(value_name)
    return t, v


class OverlayBar(QFrame):
    """Semi-transparent bar drawn over the camera view."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("overlayBar")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(32)

        for title, attr in [
            ("GESTURE",    "gesture"),
            ("CONFIDENCE", "confidence"),
            ("MODE",       "mode"),
            ("STATUS",     "status"),
        ]:
            col = QVBoxLayout()
            col.setSpacing(2)
            t_lbl = QLabel(title)
            t_lbl.setObjectName("overlayLabel")
            v_lbl = QLabel("—")
            v_lbl.setObjectName("overlayValue")
            col.addWidget(t_lbl)
            col.addWidget(v_lbl)
            layout.addLayout(col)
            setattr(self, f"_{attr}_lbl", v_lbl)

        layout.addStretch()

    def refresh(self, state: StateManager) -> None:
        self._gesture_lbl.setText(state.current_gesture)

        conf_pct = int(state.confidence * 100)
        self._confidence_lbl.setText(f"{conf_pct}%")

        self._mode_lbl.setText(state.mode)

        status = state.system_status
        self._status_lbl.setText(status)
        if status == "ACTIVE":
            self._status_lbl.setObjectName("overlayValueGreen")
        elif status == "INACTIVE":
            self._status_lbl.setObjectName("overlayValueRed")
        else:
            self._status_lbl.setObjectName("overlayValue")
        # Force style refresh after objectName change
        self._status_lbl.style().unpolish(self._status_lbl)
        self._status_lbl.style().polish(self._status_lbl)


# ──────────────────────────────────────────────────────────────────────────────
# Vision Panel
# ──────────────────────────────────────────────────────────────────────────────

class VisionPanel(QFrame):
    """
    Central camera feed card.

    Call :meth:`update_frame` to push a new QImage.
    Connect the panel to a StateManager to auto-refresh overlays.
    """

    def __init__(self, state: StateManager, parent=None):
        super().__init__(parent)
        self._state  = state
        self._active = False

        self.setObjectName("visionCard")
        self.setSizePolicy(QSizePolicy.Policy.Expanding,
                           QSizePolicy.Policy.Expanding)

        self._build_ui()
        self._connect_state()

    # ── Construction ──────────────────────────────────────────────────

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(10)

        # Section title row
        title_row = QHBoxLayout()
        cam_title = QLabel("LIVE VISION")
        cam_title.setObjectName("cardTitle")
        title_row.addWidget(cam_title)
        title_row.addStretch()
        self._dot = StatusDot()
        title_row.addWidget(self._dot, 0, Qt.AlignmentFlag.AlignVCenter)
        root.addLayout(title_row)

        # Camera feed label
        self._feed_label = QLabel()
        self._feed_label.setObjectName("cameraFeed")
        self._feed_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._feed_label.setText("⊙  Camera feed not started\n\nRun with  --simulate  for demo mode")
        self._feed_label.setSizePolicy(QSizePolicy.Policy.Expanding,
                                       QSizePolicy.Policy.Expanding)

        # Overlay sits on top — put both in a container
        feed_container = QWidget()
        feed_container.setSizePolicy(QSizePolicy.Policy.Expanding,
                                      QSizePolicy.Policy.Expanding)
        feed_layout = QVBoxLayout(feed_container)
        feed_layout.setContentsMargins(0, 0, 0, 0)
        feed_layout.setSpacing(0)
        feed_layout.addWidget(self._feed_label)

        root.addWidget(feed_container)

        # Overlay bar (anchored to bottom of feed)
        self._overlay = OverlayBar(feed_container)
        # Positioned via resizeEvent

        # Stability bar row
        stab_row = QHBoxLayout()
        stab_lbl = QLabel("STABILITY")
        stab_lbl.setObjectName("cardTitle")
        stab_row.addWidget(stab_lbl)
        stab_row.addSpacing(10)
        self._stability_bar = QProgressBar()
        self._stability_bar.setObjectName("stabilityBar")
        self._stability_bar.setRange(0, 100)
        self._stability_bar.setValue(0)
        self._stability_bar.setFixedHeight(6)
        self._stability_bar.setTextVisible(False)
        stab_row.addWidget(self._stability_bar)
        root.addLayout(stab_row)

    def _connect_state(self) -> None:
        self._state.state_updated.connect(self._on_state_updated)

    # ── Resize: reposition overlay over feed ─────────────────────────
    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._position_overlay()

    def _position_overlay(self) -> None:
        # Feed container is the second item in root layout
        # We walk children to find the right parent
        feed_label = self._feed_label
        parent_w   = feed_label.parent()
        if parent_w is None:
            return
        pw = parent_w.width()
        ph = parent_w.height()
        ow = pw
        oh = 68
        self._overlay.setGeometry(0, ph - oh, ow, oh)

    # ── Public API ────────────────────────────────────────────────────

    @pyqtSlot(QImage)
    def update_frame(self, image: QImage) -> None:
        """Push a new camera frame (called from worker thread via signal)."""
        pix = QPixmap.fromImage(image)
        self._feed_label.setPixmap(
            pix.scaled(self._feed_label.width(),
                       self._feed_label.height(),
                       Qt.AspectRatioMode.KeepAspectRatio,
                       Qt.TransformationMode.SmoothTransformation)
        )

    # ── State refresh ─────────────────────────────────────────────────

    @pyqtSlot()
    def _on_state_updated(self) -> None:
        active = self._state.system_status == "ACTIVE"

        # Glowing border toggle
        if active != self._active:
            self._active = active
            self.setObjectName("visionCardActive" if active else "visionCard")
            self.style().unpolish(self)
            self.style().polish(self)

            # Drop shadow glow when active
            if active:
                shadow = QGraphicsDropShadowEffect(self)
                shadow.setBlurRadius(28)
                shadow.setColor(QColor(0, 229, 255, 120))
                shadow.setOffset(0, 0)
                self.setGraphicsEffect(shadow)
            else:
                self.setGraphicsEffect(None)

        self._dot.set_active(active)
        self._overlay.refresh(self._state)
        self._stability_bar.setValue(int(self._state.stability_pct))
        self._position_overlay()
