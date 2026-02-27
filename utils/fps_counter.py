"""
utils/fps_counter.py - Performance Monitor

Tracks frames-per-second using a rolling window and renders
the FPS value onto the video frame.
"""

import time
import cv2


class FPSCounter:
    """Rolling-average FPS counter."""

    def __init__(self, avg_frames: int = 30):
        self._avg_frames = avg_frames
        self._timestamps: list[float] = []
        self._fps: float = 0.0

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def update(self) -> None:
        """Record the current timestamp and recalculate FPS."""
        now = time.time()
        self._timestamps.append(now)

        # Keep only the last N timestamps
        if len(self._timestamps) > self._avg_frames:
            self._timestamps.pop(0)

        # Calculate FPS from the window
        if len(self._timestamps) >= 2:
            elapsed = self._timestamps[-1] - self._timestamps[0]
            self._fps = (len(self._timestamps) - 1) / elapsed if elapsed > 0 else 0.0

    @property
    def fps(self) -> float:
        """Current FPS value."""
        return self._fps

    def display_fps(self, frame):
        """Render FPS counter onto the top-left corner of a frame."""
        cv2.putText(
            frame,
            f'FPS: {int(self._fps)}',
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2,
            cv2.LINE_AA,
        )
        return frame
