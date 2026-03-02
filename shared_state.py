"""
shared_state.py - Central reactive state store for the MMGI PyQt6 dashboard.

All live data produced by the worker thread is stored here and exposed as
PyQt6 signals so UI panels can subscribe independently without tight coupling.

Usage
-----
from shared_state import SharedState

state = SharedState()          # one instance shared app-wide
state.system_active_changed.connect(my_slot)
state.set_system_active(True)
"""

from __future__ import annotations

from PyQt6.QtCore import QObject, pyqtSignal


class SharedState(QObject):
    """
    Central reactive data store.

    Fields
    ------
    system_active : bool          – whether MMGI tracking is running
    current_mode  : str           – 'App Mode' | 'Media Mode' | 'System Mode'
    current_gesture: str          – latest recognised gesture name ('' = none)
    confidence    : float         – 0.0 – 1.0 classifier confidence
    fps           : float         – camera frames per second
    latency_ms    : float         – pipeline latency in milliseconds
    in_cooldown   : bool          – True while action/mode cooldown is active
    volume_level  : int           – 0–100 system volume estimate
    mode_stability: float         – 0.0–1.0 mode-switch hold progress

    # System Mode specific
    sub_mode      : str           – 'IDLE' | 'CURSOR' | 'WRITING' (System Mode only)
    cursor_active : bool          – True while Air Mouse cursor mode is running
    writing_active: bool          – True while Air Writing mode is running
    """

    # ------------------------------------------------------------------ signals
    system_active_changed   = pyqtSignal(bool)
    mode_changed            = pyqtSignal(str)
    gesture_changed         = pyqtSignal(str)
    confidence_changed      = pyqtSignal(float)
    fps_changed             = pyqtSignal(float)
    latency_changed         = pyqtSignal(float)
    cooldown_changed        = pyqtSignal(bool)
    volume_changed          = pyqtSignal(int)
    mode_stability_changed  = pyqtSignal(float)

    # System Mode sub-mode signals
    sub_mode_changed        = pyqtSignal(str)    # 'IDLE' | 'CURSOR' | 'WRITING'
    cursor_active_changed   = pyqtSignal(bool)
    writing_active_changed  = pyqtSignal(bool)

    # Writing overlay signals (main-thread safe, wired directly to WritingOverlay)
    stroke_added            = pyqtSignal(float, float, bool)  # norm_x, norm_y, new_stroke
    canvas_cleared          = pyqtSignal()                    # erase all strokes
    overlay_visible         = pyqtSignal(bool)                # show/hide overlay

    # Batched update – emits a snapshot dict for panels that want everything
    snapshot_ready          = pyqtSignal(dict)

    # Activity log: (timestamp_str, event_category, description)
    log_event               = pyqtSignal(str, str, str)

    # ------------------------------------------------------------------ init
    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._system_active    = False
        self._current_mode     = 'App Mode'
        self._current_gesture  = ''
        self._confidence       = 0.0
        self._fps              = 0.0
        self._latency_ms       = 0.0
        self._in_cooldown      = False
        self._volume_level     = 50
        self._mode_stability   = 0.0
        # System Mode sub-state
        self._sub_mode         = 'IDLE'
        self._cursor_active    = False
        self._writing_active   = False

    # ------------------------------------------------------------------ getters
    @property
    def system_active(self)   -> bool:  return self._system_active
    @property
    def current_mode(self)    -> str:   return self._current_mode
    @property
    def current_gesture(self) -> str:   return self._current_gesture
    @property
    def confidence(self)      -> float: return self._confidence
    @property
    def fps(self)             -> float: return self._fps
    @property
    def latency_ms(self)      -> float: return self._latency_ms
    @property
    def in_cooldown(self)     -> bool:  return self._in_cooldown
    @property
    def volume_level(self)    -> int:   return self._volume_level
    @property
    def mode_stability(self)  -> float: return self._mode_stability
    @property
    def sub_mode(self)        -> str:   return self._sub_mode
    @property
    def cursor_active(self)   -> bool:  return self._cursor_active
    @property
    def writing_active(self)  -> bool:  return self._writing_active

    # ------------------------------------------------------------------ setters
    def set_system_active(self, value: bool) -> None:
        if self._system_active != value:
            self._system_active = value
            self.system_active_changed.emit(value)
            self._emit_snapshot()

    def set_mode(self, value: str) -> None:
        if self._current_mode != value:
            self._current_mode = value
            self.mode_changed.emit(value)
            self._emit_snapshot()

    def set_gesture(self, value: str) -> None:
        if self._current_gesture != value:
            self._current_gesture = value
            self.gesture_changed.emit(value)

    def set_confidence(self, value: float) -> None:
        self._confidence = round(value, 3)
        self.confidence_changed.emit(self._confidence)

    def set_fps(self, value: float) -> None:
        self._fps = round(value, 1)
        self.fps_changed.emit(self._fps)

    def set_latency(self, value: float) -> None:
        self._latency_ms = round(value, 1)
        self.latency_changed.emit(self._latency_ms)

    def set_cooldown(self, value: bool) -> None:
        if self._in_cooldown != value:
            self._in_cooldown = value
            self.cooldown_changed.emit(value)

    def set_volume(self, value: int) -> None:
        clamped = max(0, min(100, value))
        if self._volume_level != clamped:
            self._volume_level = clamped
            self.volume_changed.emit(clamped)

    def set_mode_stability(self, value: float) -> None:
        self._mode_stability = round(max(0.0, min(1.0, value)), 3)
        self.mode_stability_changed.emit(self._mode_stability)

    def set_sub_mode(self, value: str) -> None:
        """Set System Mode sub-mode: 'IDLE' | 'CURSOR' | 'WRITING'."""
        if self._sub_mode != value:
            self._sub_mode = value
            self.sub_mode_changed.emit(value)
            cursor  = (value == 'CURSOR')
            writing = (value == 'WRITING')
            if self._cursor_active != cursor:
                self._cursor_active = cursor
                self.cursor_active_changed.emit(cursor)
            if self._writing_active != writing:
                self._writing_active = writing
                self.writing_active_changed.emit(writing)
            # Show overlay only in Writing mode
            self.overlay_visible.emit(writing)

    def emit_stroke_point(self, norm_x: float, norm_y: float, new_stroke: bool) -> None:
        """Forward a writing stroke point to the overlay."""
        self.stroke_added.emit(norm_x, norm_y, new_stroke)

    def emit_canvas_clear(self) -> None:
        """Tell the overlay to erase all strokes."""
        self.canvas_cleared.emit()

    def emit_log(self, timestamp: str, category: str, description: str) -> None:
        """Convenience wrapper to push an activity log event."""
        self.log_event.emit(timestamp, category, description)

    # ------------------------------------------------------------------ snapshot
    def snapshot(self) -> dict:
        """Return all current values as a plain dict."""
        return {
            'system_active':  self._system_active,
            'current_mode':   self._current_mode,
            'current_gesture':self._current_gesture,
            'confidence':     self._confidence,
            'fps':            self._fps,
            'latency_ms':     self._latency_ms,
            'in_cooldown':    self._in_cooldown,
            'volume_level':   self._volume_level,
            'mode_stability': self._mode_stability,
            'sub_mode':       self._sub_mode,
            'cursor_active':  self._cursor_active,
            'writing_active': self._writing_active,
        }

    def _emit_snapshot(self) -> None:
        self.snapshot_ready.emit(self.snapshot())
