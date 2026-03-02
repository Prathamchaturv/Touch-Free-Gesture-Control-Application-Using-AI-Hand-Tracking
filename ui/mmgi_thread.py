"""
ui/mmgi_thread.py — QThread bridge between the MMGI core and the UI

Runs the full MMGI pipeline (Camera → HandTracker → GestureClassifier
→ ActivationManager → DecisionEngine → ActionExecutor) in a background
thread.  Frame data and state dicts are emitted via Qt signals so the
UI can update safely on the main thread.
"""

from __future__ import annotations

import time
import sys
from pathlib import Path
from typing import Optional

import numpy as np

from PyQt6.QtCore  import QThread, pyqtSignal
from PyQt6.QtGui   import QImage

# ── Ensure parent package is importable ───────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


class MMGIWorkerThread(QThread):
    """
    Background thread that drives the full MMGI pipeline.

    Signals
    -------
    frame_ready(QImage)
        Emitted every frame with the annotated camera image.
    state_changed(dict)
        Emitted with a dict of state fields for StateManager.update(**d).
    log_event(str, str, str)
        Emitted when an action executes: (timestamp, gesture, action).
    error(str)
        Emitted on a fatal error so the UI can show a message.
    """

    frame_ready   = pyqtSignal(QImage)
    state_changed = pyqtSignal(dict)
    log_event     = pyqtSignal(str, str, str)
    error         = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._running = False

    # ── Thread entry ──────────────────────────────────────────────────

    def run(self) -> None:
        self._running = True
        try:
            self._pipeline()
        except Exception as exc:
            self.error.emit(str(exc))

    def stop(self) -> None:
        self._running = False

    # ── Pipeline ──────────────────────────────────────────────────────

    def _pipeline(self) -> None:
        # Lazy imports so the main process doesn't load cv2 until the thread starts
        import cv2
        from core.camera              import Camera
        from core.hand_tracking       import HandTracker
        from core.gesture_classifier  import GestureClassifier
        from engine.activation_manager import ActivationManager
        from engine.decision_engine    import DecisionEngine
        from engine.action_executor    import ActionExecutor
        from utils.fps_counter         import FPSCounter
        from utils.config              import Config

        config = Config()

        camera = Camera(
            width  = config.get('camera.width'),
            height = config.get('camera.height'),
            fps    = config.get('camera.fps'),
        )
        if not camera.open():
            self.error.emit("Failed to open camera. Is a webcam connected?")
            return

        hand_tracker    = HandTracker(
            max_num_hands            = config.get('hand_tracking.max_num_hands'),
            min_detection_confidence = config.get('hand_tracking.min_detection_confidence'),
            min_tracking_confidence  = config.get('hand_tracking.min_tracking_confidence'),
        )
        gesture_clf     = GestureClassifier()
        activation_mgr  = ActivationManager(
            open_palm_duration  = config.get('activation.open_palm_duration'),
            cooldown_duration   = config.get('activation.cooldown_duration'),
            stability_threshold = config.get('activation.stability_threshold'),
        )
        decision_eng    = DecisionEngine()
        action_exec     = ActionExecutor(config={
            'brave_path':        config.get('apps.brave_path'),
            'apple_music_aumid': config.get('apps.apple_music_aumid'),
        })
        fps_counter     = FPSCounter()

        exec_count = 0
        total_frames = 0
        accurate_frames = 0

        while self._running and camera.is_opened():
            t0 = time.perf_counter()

            success, frame = camera.read_frame()
            if not success or frame is None:
                continue

            fps_counter.update()
            total_frames += 1

            results    = hand_tracker.detect_hands(frame)
            hands_info = hand_tracker.get_hands_info(results)

            if results.hand_landmarks:
                frame = hand_tracker.draw_landmarks(frame, results)
                accurate_frames += 1

            gesture      = "None"
            stability    = 0.0
            should_exec  = False
            action_str   = ""
            handedness   = "–"

            if hands_info['count'] > 0:
                hand = hands_info['right'] or hands_info['left']
                if hand:
                    handedness = 'Right' if hands_info['right'] else 'Left'
                    gesture    = gesture_clf.classify(hand['finger_states'])
                    should_exec = activation_mgr.update(gesture)
                    stability   = min(activation_mgr._stable_count /
                                      max(activation_mgr._stability_threshold, 1), 1.0)

                    if should_exec:
                        side   = 'right' if hands_info['right'] else 'left'
                        action_str = decision_eng.get_action(gesture, handedness=side) or ""
                        if action_str:
                            action_exec.execute(action_str)
                            exec_count += 1
                            ts = time.strftime("%H:%M:%S")
                            self.log_event.emit(ts, gesture, action_str)

            latency_ms   = (time.perf_counter() - t0) * 1000
            cooldown_rem = max(
                0.0,
                config.get('activation.cooldown_duration') -
                (time.time() - activation_mgr._last_action_time)
            ) / max(config.get('activation.cooldown_duration'), 0.001)
            cooldown_rem = min(cooldown_rem, 1.0)

            acc_pct  = (accurate_frames / max(total_frames, 1)) * 100
            exec_pct = min((exec_count / max(total_frames, 1)) * 1000, 100.0)

            mode_map = {
                'INACTIVE':   'STANDBY',
                'ACTIVATING': 'APP MODE',
                'ACTIVE':     'APP MODE',
            }

            self.state_changed.emit({
                'current_gesture':     gesture,
                'confidence':          stability,
                'handedness':          handedness,
                'system_status':       activation_mgr.state,
                'mode':                mode_map.get(activation_mgr.state, 'STANDBY'),
                'latency_ms':          latency_ms,
                'cooldown_remaining':  cooldown_rem,
                'stability_pct':       stability * 100,
                'fps':                 fps_counter.fps,
                'accuracy_pct':        acc_pct,
                'execution_rate_pct':  exec_pct,
            })

            # Emit frame
            rgb   = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb.shape
            img   = QImage(rgb.data.tobytes(), w, h, ch * w,
                           QImage.Format.Format_RGB888)
            self.frame_ready.emit(img.copy())

        camera.release() if hasattr(camera, 'release') else None
