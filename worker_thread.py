"""
worker_thread.py - MMGI Pipeline Worker (QThread)

Runs the full gesture recognition pipeline in a background thread and
pushes state updates into SharedState so the UI never blocks.

Pipeline per frame
------------------
1. Camera.read_frame()
2. HandTracker.process_frame()
3. GestureClassifier.classify()
4. DecisionEngine.process()  ← Smart Mode (mode-switch OR action)
5. ActivationManager.update()
6. ActionExecutor.execute()   (only when active + action resolved)
7. Update SharedState + emit frame as QImage

Signals emitted to the outside
-------------------------------
frame_ready(QImage)  – annotated video frame for the Vision Panel
error(str)           – fatal pipeline error message
"""

from __future__ import annotations

import time
from datetime import datetime

import cv2
from PyQt6.QtCore  import QThread, pyqtSignal
from PyQt6.QtGui   import QImage

from core.camera              import Camera
from core.hand_tracking       import HandTracker
from core.gesture_classifier  import GestureClassifier
from engine.activation_manager import ActivationManager
from engine.decision_engine    import DecisionEngine
from engine.action_executor    import ActionExecutor
from engine.system_mode_engine import SystemModeEngine
from utils.fps_counter         import FPSCounter
from utils.config              import Config
from shared_state              import SharedState


# ---------------------------------------------------------------------------
# Overlay helpers
# ---------------------------------------------------------------------------

_ACCENT   = (0, 229, 255)   # #00E5FF  (BGR)
_GREEN    = (0, 255, 136)   # #00FF88
_RED      = (70, 68, 255)   # #FF4466
_WHITE    = (255, 255, 255)
_DARK     = (20, 20, 30)

_MODE_COLOURS = {
    'App Mode':    (0, 229, 255),    # cyan
    'Media Mode':  (0, 200, 255),    # sky
    'System Mode': (120, 100, 255),  # violet
}

def _ts() -> str:
    return datetime.now().strftime('%H:%M:%S')


def _draw_overlay(frame, gesture: str | None, mode: str,
                  is_active: bool, fps: float,
                  sub_mode: str = 'IDLE') -> None:
    """Annotate frame in-place with gesture/mode/state HUD."""
    h, w = frame.shape[:2]

    # Semi-transparent top bar
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, 60), _DARK, -1)
    cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)

    # State indicator
    state_color = _GREEN if is_active else _RED
    state_text  = 'ACTIVE' if is_active else 'INACTIVE'
    cv2.circle(frame, (24, 30), 8, state_color, -1)
    cv2.putText(frame, state_text, (38, 36),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, state_color, 2)

    # Mode — include sub-mode when in System Mode
    mc        = _MODE_COLOURS.get(mode, _ACCENT)
    mode_text = mode.upper()
    if mode == 'System Mode' and sub_mode != 'IDLE':
        mode_text = f'SYSTEM – {sub_mode}'
    cv2.putText(frame, mode_text, (w // 2 - 80, 36),
                cv2.FONT_HERSHEY_SIMPLEX, 0.65, mc, 2)

    # FPS
    cv2.putText(frame, f'FPS {fps:.0f}', (w - 90, 36),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, _WHITE, 1)

    # Gesture label (bottom-left)
    if gesture:
        cv2.putText(frame, gesture, (16, h - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, _ACCENT, 2)

    # Sub-mode badge for System Mode (bottom bar)
    if mode == 'System Mode' and sub_mode != 'IDLE':
        badge_color = (120, 100, 255) if sub_mode == 'CURSOR' else (0, 200, 100)
        cv2.rectangle(frame, (0, h - 44), (w, h), (20, 20, 30, 180), -1)
        cv2.putText(frame, f'MODE SWITCH HOLD', (16, h - 26),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (120, 120, 120), 1)
        cv2.putText(frame, f'{sub_mode} ACTIVE', (w - 150, h - 26),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, badge_color, 2)


def _frame_to_qimage(frame) -> QImage:
    """Convert a BGR numpy frame to QImage (RGB888)."""
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    h, w, ch = rgb.shape
    return QImage(rgb.data, w, h, ch * w, QImage.Format.Format_RGB888).copy()


# ---------------------------------------------------------------------------
# Worker Thread
# ---------------------------------------------------------------------------

class WorkerThread(QThread):
    """Background pipeline thread."""

    frame_ready = pyqtSignal(QImage)
    error       = pyqtSignal(str)

    def __init__(self, state: SharedState, parent=None) -> None:
        super().__init__(parent)
        self._state   = state
        self._running = False

        # Pipeline components (created in run() so they start on the right thread)
        self._config:    Config | None = None
        self._camera:    Camera | None = None

    # ------------------------------------------------------------------
    # Public control
    # ------------------------------------------------------------------

    def stop(self) -> None:
        """Request the pipeline to stop."""
        self._running = False

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------

    def run(self) -> None:  # noqa: C901  (unavoidably long entry point)
        self._running = True
        state = self._state
        camera: Camera | None = None

        try:
            config = Config()

            camera = Camera(
                width  = config.get('camera.width'),
                height = config.get('camera.height'),
                fps    = config.get('camera.fps'),
            )
            if not camera.open():
                self.error.emit('Could not open camera.')
                return

            hand_tracker = HandTracker(
                max_num_hands            = config.get('hand_tracking.max_num_hands'),
                min_detection_confidence = config.get('hand_tracking.min_detection_confidence'),
                min_tracking_confidence  = config.get('hand_tracking.min_tracking_confidence'),
            )

            gesture_classifier = GestureClassifier()

            activation_manager = ActivationManager(
                open_palm_duration   = config.get('activation.open_palm_duration'),
                cooldown_duration    = config.get('activation.cooldown_duration'),
                stability_threshold  = config.get('activation.stability_threshold'),
            )

            decision_engine = DecisionEngine()

            system_engine = SystemModeEngine()

            action_executor = ActionExecutor(config={
                'brave_path':        config.get('apps.brave_path'),
                'apple_music_aumid': config.get('apps.apple_music_aumid'),
            })

            fps_counter = FPSCounter()

            state.emit_log(_ts(), 'SYSTEM', 'Pipeline started — show Open Palm to activate')

            # ----------------------------------------------------------------
            # Frame loop
            # ----------------------------------------------------------------
            while self._running:
                t_start = time.perf_counter()

                ok, frame = camera.read_frame()
                if not ok or frame is None:
                    continue

                # Mirror for natural interaction
                frame = cv2.flip(frame, 1)

                # ----------------------------------------------------------
                # Hand detection + gesture classification
                # ----------------------------------------------------------
                detection_result = hand_tracker.detect_hands(frame)
                hands_info       = hand_tracker.get_hands_info(detection_result)

                gesture: str | None = None
                confidence          = 0.0

                # Prefer right hand; fall back to left
                hand_data = hands_info.get('right') or hands_info.get('left')
                if hand_data:
                    finger_states = hand_data['finger_states']
                    gesture       = gesture_classifier.classify(finger_states)
                    confidence    = 1.0   # classifier is rule-based, always 1.0 on match
                    if gesture == 'Unknown':
                        gesture    = None
                        confidence = 0.0

                    # Draw hand skeleton
                    hand_tracker.draw_landmarks(frame, detection_result)

                # ----------------------------------------------------------
                # Smart Mode decision
                # ----------------------------------------------------------
                action, mode_changed = decision_engine.process(gesture)

                if mode_changed:
                    new_mode = decision_engine.current_mode
                    state.set_mode(new_mode)
                    state.emit_log(_ts(), 'MODE', f'Switched to {new_mode}')

                # Mode-switch stability bar
                state.set_mode_stability(decision_engine.mode_stability_progress)

                # ----------------------------------------------------------
                # Activation manager
                # ----------------------------------------------------------
                should_execute = activation_manager.update(gesture)
                state.set_system_active(activation_manager.is_active)
                state.set_cooldown(activation_manager.is_in_cooldown)

                # ----------------------------------------------------------
                # System Mode engine  (Air Mouse + Air Writing)
                # ----------------------------------------------------------
                if (activation_manager.is_active
                        and decision_engine.current_mode == 'System Mode'):
                    landmarks = hand_data['landmarks'] if hand_data else []
                    sys_result = system_engine.update(landmarks, gesture)

                    if sys_result.state_changed:
                        state.set_sub_mode(sys_result.new_state)
                        if sys_result.log_message:
                            state.emit_log(_ts(), 'SYSTEM MODE', sys_result.log_message)

                    if sys_result.stroke_point is not None:
                        nx, ny, ns = sys_result.stroke_point
                        state.emit_stroke_point(nx, ny, ns)

                    if sys_result.clear_canvas:
                        state.emit_canvas_clear()
                        if sys_result.log_message:
                            state.emit_log(_ts(), 'SYSTEM MODE', sys_result.log_message)
                else:
                    # Reset engine + clear sub-mode when outside System Mode
                    if system_engine.state != 'IDLE':
                        system_engine.reset()
                        state.set_sub_mode('IDLE')

                # ----------------------------------------------------------
                # Execute action
                # ----------------------------------------------------------
                if should_execute and action:
                    ok_exec = action_executor.execute(action)
                    label   = action_executor._LABELS.get(action, action)
                    if ok_exec:
                        state.emit_log(_ts(), 'ACTION', f'{label}  [{decision_engine.current_mode}]')

                # ----------------------------------------------------------
                # Update telemetry
                # ----------------------------------------------------------
                fps_counter.update()
                latency_ms = (time.perf_counter() - t_start) * 1000

                state.set_gesture(gesture or '')
                state.set_confidence(confidence)
                state.set_fps(fps_counter.fps)
                state.set_latency(latency_ms)

                # ----------------------------------------------------------
                # Annotate and emit frame
                # ----------------------------------------------------------
                _draw_overlay(
                    frame,
                    gesture,
                    decision_engine.current_mode,
                    activation_manager.is_active,
                    fps_counter.fps,
                    sub_mode=system_engine.state,
                )

                self.frame_ready.emit(_frame_to_qimage(frame))

            # ---- Loop exited cleanly ---
            camera.release()
            hand_tracker.close()
            state.set_system_active(False)
            state.emit_log(_ts(), 'SYSTEM', 'Pipeline stopped')

        except Exception as exc:  # noqa: BLE001
            import traceback
            msg = f'Pipeline error: {exc}\n{traceback.format_exc()}'
            self.error.emit(msg)
            try:
                if camera is not None:
                    camera.release()
            except Exception:
                pass
