"""
ui/state_manager.py — Shared MMGI State Object

Central observable datastore for the UI.  All panels read from here;
only the worker/simulator threads write to it (via thread-safe signals).
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List
from PyQt6.QtCore import QObject, pyqtSignal


# ──────────────────────────────────────────────────────────────────────────────
# Data containers
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class LogEvent:
    timestamp: str
    gesture:   str
    action:    str

    def __str__(self) -> str:
        return f"[{self.timestamp}]  {self.gesture}  →  {self.action}"


# ──────────────────────────────────────────────────────────────────────────────
# State Manager
# ──────────────────────────────────────────────────────────────────────────────

class StateManager(QObject):
    """
    Singleton-style QObject that holds all live MMGI state.

    Any worker thread that wants to update state should emit a signal that
    calls :meth:`update` — this keeps all mutations on the main thread,
    making Qt UI updates safe.
    """

    # Broadcast when any field changes
    state_updated = pyqtSignal()
    # Emitted specifically when a new log entry arrives
    log_appended  = pyqtSignal(object)   # LogEvent

    def __init__(self, parent=None):
        super().__init__(parent)

        # ── Live gesture data ──────────────────────────────────────────
        self.current_gesture:   str   = "None"
        self.confidence:        float = 0.0
        self.handedness:        str   = "–"      # 'Right', 'Left', or '–'

        # ── System state ───────────────────────────────────────────────
        self.system_status:     str   = "INACTIVE"   # INACTIVE | ACTIVATING | ACTIVE
        self.mode:              str   = "STANDBY"
        self.latency_ms:        float = 0.0
        self.cooldown_remaining: float = 0.0          # 0.0 – 1.0 fraction

        # ── Gesture stability ──────────────────────────────────────────
        self.stability_pct:     float = 0.0           # 0 – 100

        # ── Performance ────────────────────────────────────────────────
        self.fps:               float = 0.0
        self.accuracy_pct:      float = 0.0
        self.execution_rate_pct: float = 0.0

        # ── Log history ────────────────────────────────────────────────
        self.log_events: List[LogEvent] = []

    # ──────────────────────────────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────────────────────────────

    def update(self, **kwargs) -> None:
        """
        Set one or more fields and emit :attr:`state_updated`.

        Example::

            state.update(current_gesture="Thumbs Up", confidence=0.94)
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.state_updated.emit()

    def add_log(self, timestamp: str, gesture: str, action: str) -> None:
        """Append a new log entry and emit :attr:`log_appended`."""
        event = LogEvent(timestamp=timestamp, gesture=gesture, action=action)
        self.log_events.append(event)
        # Keep the in-memory history bounded
        if len(self.log_events) > 200:
            self.log_events = self.log_events[-200:]
        self.log_appended.emit(event)

    @property
    def is_active(self) -> bool:
        return self.system_status == "ACTIVE"
