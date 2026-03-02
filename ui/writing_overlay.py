"""
ui/writing_overlay.py - Transparent Full-Screen Air-Writing Canvas

A frameless, always-on-top, click-through overlay window that renders
hand-drawn strokes produced by SystemModeEngine's Writing sub-mode.

Architecture
────────────
• Created once at app startup (hidden by default).
• Shown / hidden by MainWindow when SharedState.sub_mode_changed fires.
• Receives stroke points via the on_stroke_point() slot (called from the
  main thread via Qt signal).
• Cleared via the on_clear_canvas() slot.
• Window is fully transparent to mouse events (WA_TransparentForMouseEvents),
  so the user can interact normally with other windows while drawing.

Coordinate mapping
──────────────────
Stroke points arrive as normalised (x, y) in [0, 1] relative to the camera
frame.  They are multiplied by the widget's pixel dimensions so strokes
scale correctly regardless of monitor resolution.
"""

from __future__ import annotations

from PyQt6.QtCore    import Qt, pyqtSlot, QPoint, QRect
from PyQt6.QtGui     import QPainter, QPen, QColor, QImage
from PyQt6.QtWidgets import QWidget, QApplication


# ---------------------------------------------------------------------------
# Visual constants
# ---------------------------------------------------------------------------

_STROKE_COLOR = QColor(0, 229, 255, 210)   # #00E5FF — matches dashboard accent
_STROKE_WIDTH = 3                            # pixels
_BG_ALPHA     = 0                            # fully transparent background


# ---------------------------------------------------------------------------
# WritingOverlay
# ---------------------------------------------------------------------------

class WritingOverlay(QWidget):
    """
    Transparent full-screen overlay; renders Air-Writing strokes.

    Slots
    -----
    on_stroke_point(norm_x, norm_y, new_stroke)
        Add one point to the current stroke.
        new_stroke=True marks the start of a new disconnected segment.

    on_clear_canvas()
        Erase all strokes.

    on_set_visible(visible)
        Show or hide the overlay.
    """

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        # List of completed strokes; each stroke is a list of QPoints.
        self._strokes  : list[list[QPoint]] = []
        # Points accumulated for the stroke currently being drawn.
        self._current  : list[QPoint]        = []

        self._setup_window()

    # ------------------------------------------------------------------
    # Window configuration
    # ------------------------------------------------------------------

    def _setup_window(self) -> None:
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool                     # no taskbar entry
        )
        # Translucent background so the painted strokes "float" over the desktop
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        # Do NOT intercept mouse / keyboard events — user must interact with other windows
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        # Cover the entire primary screen
        screen = QApplication.primaryScreen()
        if screen:
            self.setGeometry(screen.geometry())
        else:
            self.resize(1920, 1080)   # safe fallback

    # ------------------------------------------------------------------
    # Public slots
    # ------------------------------------------------------------------

    @pyqtSlot(float, float, bool)
    def on_stroke_point(self, norm_x: float, norm_y: float, new_stroke: bool) -> None:
        """
        Add a point to the active stroke.

        Parameters
        ----------
        norm_x, norm_y : float
            Normalised coordinates in [0, 1] (camera frame space).
        new_stroke : bool
            True when starting a fresh, disconnected stroke segment.
        """
        w = self.width()
        h = self.height()
        pt = QPoint(int(norm_x * w), int(norm_y * h))

        if new_stroke or not self._current:
            # Seal the previous stroke
            if self._current:
                self._strokes.append(list(self._current))
            self._current = [pt]
        else:
            self._current.append(pt)

        self.update()   # schedule repaint

    @pyqtSlot()
    def on_clear_canvas(self) -> None:
        """Erase all strokes immediately."""
        self._strokes.clear()
        self._current.clear()
        self.update()

    @pyqtSlot(bool)
    def on_set_visible(self, visible: bool) -> None:
        """Show or hide the overlay from the main thread."""
        if visible:
            # Re-fit to screen in case resolution changed
            screen = QApplication.primaryScreen()
            if screen:
                self.setGeometry(screen.geometry())
            self.show()
            self.raise_()
        else:
            self.hide()
            # When hidden, seal any open stroke so it isn't dangling
            if self._current:
                self._strokes.append(list(self._current))
                self._current = []

    # ------------------------------------------------------------------
    # Paint
    # ------------------------------------------------------------------

    def paintEvent(self, event) -> None:   # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        pen = QPen(
            _STROKE_COLOR,
            _STROKE_WIDTH,
            Qt.PenStyle.SolidLine,
            Qt.PenCapStyle.RoundCap,
            Qt.PenJoinStyle.RoundJoin,
        )
        painter.setPen(pen)

        for stroke in self._strokes:
            _draw_stroke(painter, stroke)
        _draw_stroke(painter, self._current)

        painter.end()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _draw_stroke(painter: QPainter, points: list[QPoint]) -> None:
    """Render a polyline from a list of QPoints."""
    if len(points) < 2:
        return
    for i in range(1, len(points)):
        painter.drawLine(points[i - 1], points[i])
