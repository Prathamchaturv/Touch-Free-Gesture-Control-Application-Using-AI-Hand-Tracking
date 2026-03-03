"""
MMGI - Multi-Modal Gesture Intelligence
Production-Level Modular Architecture

Entry-point dispatcher
──────────────────────
Default (no flags)  → PyQt6 AI Dashboard  (live camera + Smart Mode UI)
--headless          → OpenCV terminal-only pipeline (original behaviour)

Usage
-----
  python main.py                  # launch dashboard
  python main.py --headless       # headless OpenCV loop
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


# ---------------------------------------------------------------------------
# Headless (OpenCV) pipeline  –  preserved from original main.py
# ---------------------------------------------------------------------------

def run_headless() -> None:
    """Original OpenCV gesture pipeline (no GUI)."""
    import cv2
    from core.camera              import Camera
    from core.hand_tracking       import HandTracker
    from core.gesture_classifier  import GestureClassifier
    from engine.activation_manager import ActivationManager
    from engine.decision_engine    import DecisionEngine
    from engine.action_executor    import ActionExecutor
    from utils.fps_counter         import FPSCounter
    from utils.config              import Config

    print('=' * 60)
    print('MMGI  —  Headless OpenCV Mode')
    print('=' * 60)

    config = Config()
    camera = camera_obj = None
    hand_tracker = None

    try:
        camera_obj = Camera(
            width  = config.get('camera.width'),
            height = config.get('camera.height'),
            fps    = config.get('camera.fps'),
        )
        if not camera_obj.open():
            print('  ✗ Failed to open camera'); return

        hand_tracker       = HandTracker(
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
        decision_engine    = DecisionEngine()
        action_executor    = ActionExecutor(config={
            'brave_path':        config.get('apps.brave_path'),
            'apple_music_aumid': config.get('apps.apple_music_aumid'),
        })
        fps_counter        = FPSCounter()

        print('[Ready] Show Open Palm 2 s to activate. Press q/ESC to quit.\n')

        win = 'MMGI Headless'
        cv2.namedWindow(win, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(win, 1280, 720)

        while True:
            ok, frame = camera_obj.read_frame()
            if not ok or frame is None:
                break
            frame = cv2.flip(frame, 1)
            fps_counter.update()

            results    = hand_tracker.detect_hands(frame)
            hands_info = hand_tracker.get_hands_info(results)

            if results.hand_landmarks:
                hand_tracker.draw_landmarks(frame, results)

            hand_data = hands_info.get('right') or hands_info.get('left')
            gesture   = None
            if hand_data:
                gesture = gesture_classifier.classify(hand_data['finger_states'])
                if gesture == 'Unknown':
                    gesture = None

            action, mode_changed = decision_engine.process(gesture)
            if mode_changed:
                print(f'  Mode → {decision_engine.current_mode}')

            should_exec = activation_manager.update(gesture)
            if should_exec and action:
                action_executor.execute(action)
                print(f'  Action: {action}')

            fps_counter.display_fps(frame)
            activation_manager.display_status(frame)
            cv2.imshow(win, frame)

            key = cv2.waitKey(1) & 0xFF
            if key in (ord('q'), 27):
                break

    except KeyboardInterrupt:
        pass
    finally:
        if camera_obj:
            camera_obj.release()
        if hand_tracker:
            hand_tracker.close()
        cv2.destroyAllWindows()
        print('\nMMGI Headless session ended.')


# ---------------------------------------------------------------------------
# Dashboard (PyQt6) launch
# ---------------------------------------------------------------------------

def run_dashboard() -> None:
    """Launch the PyQt6 Smart Mode AI dashboard."""
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore    import Qt
    from ui.ui           import MainWindow

    app = QApplication(sys.argv)
    app.setApplicationName('MMGI')
    app.setApplicationDisplayName('MMGI — Smart Mode AI Controller')

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    if '--headless' in sys.argv:
        run_headless()
    else:
        run_dashboard()
