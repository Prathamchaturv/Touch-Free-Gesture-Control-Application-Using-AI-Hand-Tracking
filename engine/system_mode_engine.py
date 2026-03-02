"""
engine/system_mode_engine.py - System Mode State Machine

Handles two sub-modes within MMGI System Mode:

  Cursor Mode  (CURSOR)  – Thumb tip + Index tip pinch → moves the OS cursor
  Writing Mode (WRITING) – Thumb tip + Middle tip pinch → draws on overlay canvas

State Machine
─────────────
         pinch (thumb+middle, 8 frames)
  IDLE ──────────────────────────────────► WRITING
       ──────────────────────────────────►
         pinch (thumb+index, 8 frames)     CURSOR

  CURSOR  ─── pinch released ──────────► IDLE
  CURSOR  ─── writing pinch  ──────────► WRITING  (override)
  WRITING ─── pinch released ──────────► IDLE

  WRITING + Open Palm held 1.5 s → clear canvas

Priority: WRITING > CURSOR when both pinches detected.

Design principles
─────────────────
• Hand-size-normalised pinch threshold  → scale-invariant (works at any range)
• Moving-average cursor smoothing        → eliminates jitter
• Dead-zone filter                       → prevents micro-drift
• Center-60 % frame region mapped        → consistent cursor range
• No Qt imports – pure logic             → testable outside UI
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass

import pyautogui


# ---------------------------------------------------------------------------
# MediaPipe landmark indices
# ---------------------------------------------------------------------------

WRIST         = 0
THUMB_TIP     = 4
INDEX_TIP     = 8
MIDDLE_TIP    = 12
MIDDLE_MCP    = 9   # used for hand-size normalisation


# ---------------------------------------------------------------------------
# Tuning constants
# ---------------------------------------------------------------------------

# Pinch threshold as a fraction of the wrist→middle-MCP distance.
# Smaller  = tighter pinch required.
# 0.38 is reliable across distances 40–100 cm from camera.
PINCH_RATIO         = 0.38

# Hysteresis: release only when distance grows beyond this ratio.
RELEASE_RATIO       = PINCH_RATIO * 1.45

# Frames the pinch gesture must remain stable before activating.
STABILITY_FRAMES    = 8

# Seconds to wait after any pinch activation before allowing another.
PINCH_COOLDOWN_SECS = 0.5

# Cursor smoothing factor (exponential moving average).
# Higher → smoother but more lag |  1 → raw (no smoothing).
CURSOR_SMOOTHING    = 7

# Pixels of cursor movement below which we skip pyautogui.moveTo().
DEAD_ZONE_PX        = 5

# Fraction of the frame that maps to the full screen on each axis.
# Using the centre 60% (0.20 → 0.80) provides comfortable range of motion.
FRAME_X_MIN, FRAME_X_MAX = 0.20, 0.80
FRAME_Y_MIN, FRAME_Y_MAX = 0.20, 0.80

# Seconds Open Palm must be held inside Writing Mode to clear the canvas.
PALM_CLEAR_SECS     = 1.5
PALM_CLEAR_FRAMES   = 8    # must be stable for at least this many frames too


# ---------------------------------------------------------------------------
# Result dataclass  (worker → shared state / UI)
# ---------------------------------------------------------------------------

@dataclass
class SystemModeResult:
    """
    Produced each frame by SystemModeEngine.update().

    Attributes
    ----------
    state_changed : bool
        True if the sub-mode changed this frame.
    new_state : str
        Current sub-mode after this update: 'IDLE' | 'CURSOR' | 'WRITING'.
    cursor_pos : tuple[int, int] | None
        Screen pixel coordinates to move the cursor to, or None.
    stroke_point : tuple[float, float, bool] | None
        (norm_x, norm_y, is_new_stroke) for the writing overlay, or None.
    clear_canvas : bool
        True when the overlay canvas should be cleared.
    log_message : str | None
        Human-readable event description, or None.
    """
    state_changed : bool                           = False
    new_state     : str                            = 'IDLE'
    cursor_pos    : tuple[int, int] | None         = None
    stroke_point  : tuple[float, float, bool] | None = None
    clear_canvas  : bool                           = False
    log_message   : str | None                     = None


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------

class SystemModeEngine:
    """
    Pure-logic state machine for System Mode gesture sub-modes.

    Usage
    -----
    engine = SystemModeEngine()

    # Every frame when System Mode is active:
    result = engine.update(landmarks, gesture)

    # When leaving System Mode:
    engine.reset()
    """

    STATES = ('IDLE', 'CURSOR', 'WRITING')

    def __init__(self) -> None:
        self._state            = 'IDLE'

        # Pinch stability counters
        self._cursor_stable    = 0
        self._writing_stable   = 0
        self._last_pinch_time  = 0.0

        # Cursor smoothed position (screen pixels)
        self._sm_x: float | None = None
        self._sm_y: float | None = None

        # Canvas-clear tracking (Open Palm in Writing Mode)
        self._palm_clear_count = 0
        self._palm_clear_start = 0.0

        # Disable pyautogui safety features for smooth cursor control
        pyautogui.FAILSAFE = False
        pyautogui.PAUSE    = 0.0

        self._screen_w, self._screen_h = pyautogui.size()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def state(self) -> str:
        """Current sub-mode: 'IDLE' | 'CURSOR' | 'WRITING'."""
        return self._state

    def reset(self) -> None:
        """
        Reset to IDLE immediately.
        Call this when exiting System Mode so state is clean on re-entry.
        """
        self._state            = 'IDLE'
        self._cursor_stable    = 0
        self._writing_stable   = 0
        self._sm_x             = None
        self._sm_y             = None
        self._palm_clear_count = 0

    def update(
        self,
        landmarks: list[tuple[float, float, float]],
        gesture  : str | None,
    ) -> SystemModeResult:
        """
        Process one camera frame.

        Parameters
        ----------
        landmarks :
            21 MediaPipe hand landmarks as (x, y, z) in normalised coords [0, 1].
        gesture :
            Current gesture name from GestureClassifier, or None.

        Returns
        -------
        SystemModeResult
        """
        result = SystemModeResult(new_state=self._state)

        # Guard: need all 21 landmarks
        if not landmarks or len(landmarks) < 21:
            self._cursor_stable  = 0
            self._writing_stable = 0
            return result

        # Compute hand size for normalised thresholds
        hand_size = self._dist(landmarks, WRIST, MIDDLE_MCP)
        if hand_size < 1e-6:
            return result   # degenerate / occluded hand

        pinch_thr   = PINCH_RATIO   * hand_size
        release_thr = RELEASE_RATIO * hand_size

        # Pinch distances
        writing_dist = self._dist(landmarks, THUMB_TIP, MIDDLE_TIP)
        cursor_dist  = self._dist(landmarks, THUMB_TIP, INDEX_TIP)

        # Canvas clear via Open Palm in Writing Mode
        if self._state == 'WRITING' and gesture == 'Open Palm':
            if self._palm_clear_count == 0:
                self._palm_clear_start = time.time()
            self._palm_clear_count += 1
            if (self._palm_clear_count >= PALM_CLEAR_FRAMES
                    and time.time() - self._palm_clear_start >= PALM_CLEAR_SECS):
                result.clear_canvas  = True
                result.log_message   = 'Canvas cleared via Open Palm'
                self._palm_clear_count = 0
        else:
            self._palm_clear_count = 0

        # Route to state handler
        if   self._state == 'IDLE':
            result = self._idle(result, cursor_dist, writing_dist, pinch_thr, landmarks)
        elif self._state == 'CURSOR':
            result = self._cursor(result, cursor_dist, writing_dist, pinch_thr, release_thr, landmarks)
        elif self._state == 'WRITING':
            result = self._writing(result, writing_dist, release_thr, landmarks)

        return result

    # ------------------------------------------------------------------
    # State handlers
    # ------------------------------------------------------------------

    def _idle(
        self,
        result       : SystemModeResult,
        cursor_dist  : float,
        writing_dist : float,
        pinch_thr    : float,
        landmarks    : list,
    ) -> SystemModeResult:
        """IDLE handler — watch for pinch activation."""
        now         = time.time()
        cooldown_ok = (now - self._last_pinch_time) >= PINCH_COOLDOWN_SECS

        # Writing takes priority (Thumb + Middle)
        if writing_dist < pinch_thr:
            self._writing_stable += 1
            self._cursor_stable   = 0

            if self._writing_stable >= STABILITY_FRAMES and cooldown_ok:
                self._state           = 'WRITING'
                self._last_pinch_time = now
                result.state_changed  = True
                result.new_state      = 'WRITING'
                result.log_message    = 'System Mode → Writing Activated'
                # Start a fresh stroke at the current index-tip position
                ix, iy = landmarks[INDEX_TIP][0], landmarks[INDEX_TIP][1]
                result.stroke_point   = (ix, iy, True)

        # Cursor (Thumb + Index)
        elif cursor_dist < pinch_thr:
            self._cursor_stable  += 1
            self._writing_stable  = 0

            if self._cursor_stable >= STABILITY_FRAMES and cooldown_ok:
                self._state           = 'CURSOR'
                self._last_pinch_time = now
                self._sm_x            = None
                self._sm_y            = None
                result.state_changed  = True
                result.new_state      = 'CURSOR'
                result.log_message    = 'System Mode → Cursor Activated'

        else:
            self._cursor_stable  = 0
            self._writing_stable = 0

        return result

    def _cursor(
        self,
        result       : SystemModeResult,
        cursor_dist  : float,
        writing_dist : float,
        pinch_thr    : float,
        release_thr  : float,
        landmarks    : list,
    ) -> SystemModeResult:
        """CURSOR handler — move OS mouse pointer."""
        # Writing override (higher priority)
        if writing_dist < pinch_thr:
            self._writing_stable += 1
            if self._writing_stable >= STABILITY_FRAMES:
                self._state           = 'WRITING'
                self._writing_stable  = 0
                self._sm_x            = None
                self._sm_y            = None
                result.state_changed  = True
                result.new_state      = 'WRITING'
                result.log_message    = 'System Mode → Writing Activated (cursor override)'
                ix, iy = landmarks[INDEX_TIP][0], landmarks[INDEX_TIP][1]
                result.stroke_point   = (ix, iy, True)
                return result
        else:
            self._writing_stable = 0

        # Release check — exit cursor mode
        if cursor_dist > release_thr:
            self._state          = 'IDLE'
            self._sm_x           = None
            self._sm_y           = None
            result.state_changed = True
            result.new_state     = 'IDLE'
            result.log_message   = 'System Mode → Cursor Deactivated'
            return result

        # Map index fingertip to screen coordinates
        raw_x = landmarks[INDEX_TIP][0]
        raw_y = landmarks[INDEX_TIP][1]
        tx, ty = self._to_screen(raw_x, raw_y)

        # Exponential moving average smoothing
        if self._sm_x is None:
            self._sm_x = float(tx)
            self._sm_y = float(ty)
        else:
            self._sm_x += (tx - self._sm_x) / CURSOR_SMOOTHING
            self._sm_y += (ty - self._sm_y) / CURSOR_SMOOTHING

        cx, cy = int(self._sm_x), int(self._sm_y)

        # Dead-zone filter  — only call pyautogui if movement is significant
        try:
            cur_x, cur_y = pyautogui.position()
            dx = abs(cx - cur_x)
            dy = abs(cy - cur_y)
            if dx > DEAD_ZONE_PX or dy > DEAD_ZONE_PX:
                pyautogui.moveTo(cx, cy)
                result.cursor_pos = (cx, cy)
        except Exception:   # pyautogui not available / screen lock
            pass

        return result

    def _writing(
        self,
        result       : SystemModeResult,
        writing_dist : float,
        release_thr  : float,
        landmarks    : list,
    ) -> SystemModeResult:
        """WRITING handler — emit stroke points for the overlay canvas."""
        # Release check — exit writing mode
        if writing_dist > release_thr:
            self._state           = 'IDLE'
            self._cursor_stable   = 0
            result.state_changed  = True
            result.new_state      = 'IDLE'
            result.log_message    = 'System Mode → Writing Deactivated'
            return result

        # Emit current index-fingertip as a stroke continuation
        ix = landmarks[INDEX_TIP][0]
        iy = landmarks[INDEX_TIP][1]
        result.stroke_point = (ix, iy, False)

        return result

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _dist(
        landmarks: list[tuple[float, float, float]],
        a        : int,
        b        : int,
    ) -> float:
        """Euclidean distance between two normalised landmarks (x, y only)."""
        ax, ay = landmarks[a][0], landmarks[a][1]
        bx, by = landmarks[b][0], landmarks[b][1]
        return math.hypot(ax - bx, ay - by)

    def _to_screen(self, norm_x: float, norm_y: float) -> tuple[int, int]:
        """
        Map normalised frame coordinates → screen pixel coordinates.

        Uses the centre 60 % of the frame for comfortable range of motion.
        Clamps to screen bounds.
        """
        sx = (norm_x - FRAME_X_MIN) / (FRAME_X_MAX - FRAME_X_MIN)
        sy = (norm_y - FRAME_Y_MIN) / (FRAME_Y_MAX - FRAME_Y_MIN)

        px = int(sx * self._screen_w)
        py = int(sy * self._screen_h)

        px = max(0, min(self._screen_w - 1, px))
        py = max(0, min(self._screen_h - 1, py))

        return px, py
