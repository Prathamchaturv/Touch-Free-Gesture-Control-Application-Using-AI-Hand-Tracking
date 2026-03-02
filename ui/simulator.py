"""
ui/simulator.py — Fake-Data Simulator Thread

Generates realistic-looking MMGI state updates without requiring a camera
or the full MMGI stack.  Ideal for UI development and demonstration.

Usage::

    sim = SimulatorThread(state_manager)
    sim.start()
    ...
    sim.stop(); sim.wait()
"""

from __future__ import annotations

import math
import random
import time
from datetime import datetime
from typing import List

import numpy as np

from PyQt6.QtCore  import QThread, pyqtSignal, QTimer
from PyQt6.QtGui   import QImage, QColor, QPainter, QFont, QLinearGradient

from .state_manager import StateManager


# ── Fake gesture/action sequences ────────────────────────────────────────────

_GESTURES = [
    ("Open Palm",    "ACTIVATE"),
    ("One Finger",   "OPEN_BRAVE"),
    ("Two Fingers",  "OPEN_MUSIC"),
    ("Thumbs Up",    "VOLUME_UP"),
    ("Three Fingers","MUTE"),
    ("Ring and Pinky","NEXT_TRACK"),
    ("Pinky",        "PREV_TRACK"),
    ("Fist",         "DEACTIVATE"),
]

_MODES = ["APP MODE", "MEDIA MODE", "SYSTEM MODE", "STANDBY"]
_STATUSES = ["INACTIVE", "ACTIVATING", "ACTIVE", "ACTIVE", "ACTIVE"]


class SimulatorThread(QThread):
    """
    Generates fake frames and state data on a ~30 fps loop.

    Signals
    -------
    Same interface as :class:`MMGIWorkerThread` so the main window
    can swap between real and simulated data transparently.
    """

    frame_ready   = pyqtSignal(QImage)
    state_changed = pyqtSignal(dict)
    log_event     = pyqtSignal(str, str, str)

    _FPS        = 30
    _TICK_MS    = 1000 // _FPS
    _LOG_EVERY  = 90   # emit a log event every N frames

    def __init__(self, parent=None):
        super().__init__(parent)
        self._running    = False
        self._frame_idx  = 0
        self._gesture_i  = 0
        self._phase      = 0.0
        self._status     = "INACTIVE"
        self._status_timer = 0

    # ── Thread control ────────────────────────────────────────────────

    def run(self) -> None:
        self._running = True
        while self._running:
            t0 = time.perf_counter()
            self._tick()
            elapsed = (time.perf_counter() - t0) * 1000
            sleep_ms = max(0.0, self._TICK_MS - elapsed)
            time.sleep(sleep_ms / 1000)

    def stop(self) -> None:
        self._running = False

    # ── Per-frame logic ───────────────────────────────────────────────

    def _tick(self) -> None:
        self._frame_idx  += 1
        self._phase       = (self._phase + 0.05) % (2 * math.pi)

        # Rotate through statuses slowly
        self._status_timer += 1
        if self._status_timer > 120:
            self._status_timer = 0
            self._status = random.choice(_STATUSES)

        # Rotate gestures
        if self._frame_idx % 45 == 0:
            self._gesture_i = (self._gesture_i + 1) % len(_GESTURES)

        gesture, action = _GESTURES[self._gesture_i]
        confidence       = 0.80 + 0.18 * abs(math.sin(self._phase))
        stability        = min(100.0, (self._frame_idx % 45) / 45 * 100)
        latency          = 12.0 + 6.0 * abs(math.sin(self._phase * 0.7))
        fps_val          = 28.0 + 4.0 * abs(math.sin(self._phase * 0.3))
        cooldown         = max(0.0, math.sin(self._phase * 0.5)) if self._status == "ACTIVE" else 0.0
        mode             = "APP MODE" if self._status == "ACTIVE" else "STANDBY"
        accuracy         = 91.0 + 6.0 * abs(math.sin(self._phase * 0.4))
        exec_rate        = 73.0 + 15.0 * abs(math.sin(self._phase * 0.6))

        self.state_changed.emit({
            'current_gesture':     gesture,
            'confidence':          confidence,
            'handedness':          random.choice(['Right', 'Left']),
            'system_status':       self._status,
            'mode':                mode,
            'latency_ms':          latency,
            'cooldown_remaining':  cooldown,
            'stability_pct':       stability,
            'fps':                 fps_val,
            'accuracy_pct':        accuracy,
            'execution_rate_pct':  exec_rate,
        })

        # Log event
        if self._frame_idx % self._LOG_EVERY == 0 and self._status == "ACTIVE":
            ts = datetime.now().strftime("%H:%M:%S")
            self.log_event.emit(ts, gesture, action)

        # Fake camera frame
        img = self._generate_frame(gesture, confidence)
        self.frame_ready.emit(img)

    # ── Fake frame generator ──────────────────────────────────────────

    def _generate_frame(self, gesture: str, confidence: float) -> QImage:
        W, H = 640, 480
        img  = QImage(W, H, QImage.Format.Format_RGB888)

        painter = QPainter(img)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Background gradient
        grad = QLinearGradient(0, 0, W, H)
        grad.setColorAt(0.0, QColor(8,   8,  18))
        grad.setColorAt(1.0, QColor(14, 14, 30))
        painter.fillRect(0, 0, W, H, grad)

        # Animated grid lines
        grid_col = QColor(30, 30, 50, 120)
        painter.setPen(grid_col)
        step = 40
        for x in range(0, W, step):
            painter.drawLine(x, 0, x, H)
        for y in range(0, H, step):
            painter.drawLine(0, y, W, y)

        # Simulated "hand" — a circle that moves
        cx = int(W * 0.5 + W * 0.15 * math.sin(self._phase))
        cy = int(H * 0.5 + H * 0.10 * math.cos(self._phase * 0.7))
        r  = 60

        # Glow halo
        for i in range(3, 0, -1):
            alpha = int(40 * i * confidence)
            halo_col = QColor(0, 229, 255, alpha)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(halo_col)
            rr = r + i * 12
            painter.drawEllipse(cx - rr, cy - rr, rr * 2, rr * 2)

        # Hand circle
        painter.setPen(QColor(0, 229, 255, 220))
        painter.setBrush(QColor(0, 100, 140, 80))
        painter.drawEllipse(cx - r, cy - r, r * 2, r * 2)

        # Simulated finger lines
        painter.setPen(QColor(0, 229, 255, 180))
        for i in range(5):
            angle = self._phase + i * (2 * math.pi / 5)
            fx = int(cx + r * 1.5 * math.cos(angle))
            fy = int(cy + r * 1.5 * math.sin(angle))
            painter.drawLine(cx, cy, fx, fy)
            painter.drawEllipse(fx - 5, fy - 5, 10, 10)

        # Gesture text overlay
        painter.setPen(QColor(0, 229, 255))
        painter.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        painter.drawText(20, 40, gesture)

        painter.setPen(QColor(150, 150, 180))
        painter.setFont(QFont("Segoe UI", 11))
        painter.drawText(20, 65, f"Confidence: {int(confidence * 100)}%")

        # DEMO watermark
        painter.setPen(QColor(255, 255, 255, 35))
        painter.setFont(QFont("Segoe UI", 48, QFont.Weight.Bold))
        painter.drawText(140, 280, "DEMO")

        painter.end()
        return img
