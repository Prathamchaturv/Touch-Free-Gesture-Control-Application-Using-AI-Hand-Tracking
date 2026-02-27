"""
MMGI - Multi-Modal Gesture Intelligence
Production-Level Modular Architecture

Main orchestration layer that coordinates all modules:
    core/   : Camera, HandTracker, GestureClassifier
    engine/ : ActivationManager, DecisionEngine, ActionExecutor
    utils/  : FPSCounter, Config

Author : MMGI Project
Date   : February 2026
Python : 3.10+
"""

import cv2
import sys
from pathlib import Path

# Ensure project root is on the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# ---- Module imports ----
from core.camera             import Camera
from core.hand_tracking      import HandTracker
from core.gesture_classifier import GestureClassifier
from engine.activation_manager import ActivationManager
from engine.decision_engine    import DecisionEngine
from engine.action_executor    import ActionExecutor
from utils.fps_counter         import FPSCounter
from utils.config              import Config


def main() -> None:
    """Main orchestration function."""
    print('=' * 60)
    print('MMGI - Multi-Modal Gesture Intelligence')
    print('Production-Level Modular Architecture')
    print('=' * 60)

    # ------------------------------------------------------------------ #
    # 1. Configuration                                                     #
    # ------------------------------------------------------------------ #
    config = Config()
    print('\n[Config] Loading configuration...')
    print(f"  Camera       : {config.get('camera.width')}x{config.get('camera.height')}"
          f" @ {config.get('camera.fps')} fps")
    print(f"  Hand Tracking: {config.get('hand_tracking.max_num_hands')} hand(s), "
          f"detect={config.get('hand_tracking.min_detection_confidence')}, "
          f"track={config.get('hand_tracking.min_tracking_confidence')}")
    print(f"  Activation   : hold {config.get('activation.open_palm_duration')}s Open Palm, "
          f"{config.get('activation.cooldown_duration')}s cooldown, "
          f"{config.get('activation.stability_threshold')} stable frames")

    # ------------------------------------------------------------------ #
    # 2. Module initialisation                                             #
    # ------------------------------------------------------------------ #
    camera             = None
    hand_tracker       = None
    gesture_classifier = None
    activation_manager = None
    decision_engine    = None
    action_executor    = None
    fps_counter        = None

    try:
        print('\n[Initialization] Setting up modules...')

        # Camera
        camera = Camera(
            width  = config.get('camera.width'),
            height = config.get('camera.height'),
            fps    = config.get('camera.fps'),
        )
        if not camera.open():
            print('  ✗ Failed to open camera')
            return
        print('  ✓ Camera initialized')

        # Hand Tracker
        hand_tracker = HandTracker(
            max_num_hands            = config.get('hand_tracking.max_num_hands'),
            min_detection_confidence = config.get('hand_tracking.min_detection_confidence'),
            min_tracking_confidence  = config.get('hand_tracking.min_tracking_confidence'),
        )
        print('  ✓ Hand Tracker initialized')

        # Gesture Classifier
        gesture_classifier = GestureClassifier()
        print('  ✓ Gesture Classifier initialized')

        # Activation Manager
        activation_manager = ActivationManager(
            open_palm_duration  = config.get('activation.open_palm_duration'),
            cooldown_duration   = config.get('activation.cooldown_duration'),
            stability_threshold = config.get('activation.stability_threshold'),
        )
        print('  ✓ Activation Manager initialized')

        # Decision Engine
        decision_engine = DecisionEngine()
        print('  ✓ Decision Engine initialized')

        # Action Executor
        action_executor = ActionExecutor(config={
            'brave_path':   config.get('apps.brave_path'),
            'spotify_path': config.get('apps.spotify_path'),
        })
        print('  ✓ Action Executor initialized')

        # FPS Counter
        fps_counter = FPSCounter()
        print('  ✓ FPS Counter initialized')

        # ------------------------------------------------------------------ #
        # 3. Ready banner                                                      #
        # ------------------------------------------------------------------ #
        print('\n[Ready] All modules initialized. Starting main loop...')
        print('\nControls:')
        print('  - Show OPEN PALM for 2 seconds to activate')
        print('  - Show FIST to deactivate instantly')
        print('  - Press \'q\' or ESC to quit   |   \'f\' to toggle fullscreen')
        print('\nTwo-Hand Gesture Mapping:')
        print('  RIGHT HAND  (App & Media Control):')
        print('    · ONE FINGER    → Launch Brave Browser')
        print('    · TWO FINGERS   → Launch Spotify')
        print('    · RING + PINKY  → Next Song')
        print('    · PINKY         → Previous Song')
        print('  LEFT HAND   (Volume Control):')
        print('    · ONE FINGER    → Volume Up')
        print('    · TWO FINGERS   → Volume Down')
        print('    · THREE FINGERS → Mute')
        print('    · PINKY         → Play / Pause')
        print('\n  * Single-hand fallback: one hand controls everything')
        print('\n' + '=' * 60 + '\n')

        # ------------------------------------------------------------------ #
        # 4. Window setup                                                      #
        # ------------------------------------------------------------------ #
        window_name = 'MMGI - Two-Hand Gesture Control'
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, 1280, 720)
        is_fullscreen = False
        print('[Window] Created resizable window (1280×720)')
        print("  Tip: Press 'f' to toggle fullscreen\n")

        # ------------------------------------------------------------------ #
        # 5. Main loop                                                         #
        # ------------------------------------------------------------------ #
        while camera.is_opened():

            # --- Frame capture ---
            success, frame = camera.read_frame()
            if not success or frame is None:
                print('\n[Warning] Failed to read frame from camera')
                break

            # --- Performance ---
            fps_counter.update()

            # --- Hand detection ---
            results    = hand_tracker.detect_hands(frame)
            hands_info = hand_tracker.get_hands_info(results)

            # --- Draw landmarks ---
            if config.get('display.show_landmarks') and results.multi_hand_landmarks:
                frame = hand_tracker.draw_landmarks(frame, results)

            # --- Hand count badge ---
            if config.get('display.show_hand_detection'):
                frame = hand_tracker.display_hand_detection(frame, hands_info)

            # ---- Per-hand processing ----
            if hands_info['count'] > 0:
                left_hand  = hands_info['left']
                right_hand = hands_info['right']

                # ---- RIGHT HAND ----
                if right_hand:
                    right_gesture = gesture_classifier.classify(right_hand['finger_states'])

                    if config.get('display.show_gesture'):
                        frame = gesture_classifier.display_gesture(
                            frame, right_gesture, position='right'
                        )

                    # Right hand drives the activation state machine
                    should_exec = activation_manager.update(right_gesture)

                    if should_exec:
                        action = decision_engine.get_action(right_gesture, handedness='right')
                        if action:
                            action_executor.execute(action)
                            print(f'  [RIGHT HAND] Executing: {action}')

                    # Show finger states for right hand (primary)
                    if config.get('display.show_finger_states'):
                        frame = hand_tracker.display_finger_states(
                            frame, right_hand['finger_states']
                        )

                # ---- LEFT HAND ----
                if left_hand:
                    left_gesture = gesture_classifier.classify(left_hand['finger_states'])

                    if config.get('display.show_gesture'):
                        position = 'left' if right_hand else 'center'
                        frame = gesture_classifier.display_gesture(
                            frame, left_gesture, position=position
                        )

                    if not right_hand:
                        # Only left hand present — it drives activation
                        should_exec = activation_manager.update(left_gesture)
                        if should_exec:
                            action = decision_engine.get_action(left_gesture, handedness='left')
                            if action:
                                action_executor.execute(action)
                                print(f'  [LEFT HAND] Executing: {action}')

                        if config.get('display.show_finger_states'):
                            frame = hand_tracker.display_finger_states(
                                frame, left_hand['finger_states']
                            )
                    else:
                        # Both hands present — left hand acts independently
                        # when system is active, not in cooldown, and gesture differs
                        if (
                            activation_manager.is_active
                            and not activation_manager.is_in_cooldown
                            and left_gesture != right_gesture
                            and left_gesture not in ('Open Palm', 'Fist', 'Unknown', 'Thumbs Up')
                        ):
                            action = decision_engine.get_action(left_gesture, handedness='left')
                            if action:
                                action_executor.execute(action)
                                print(f'  [LEFT HAND] Executing: {action}')

                # Status panel
                if config.get('display.show_status'):
                    frame = activation_manager.display_status(frame)

            else:
                # No hand detected — keep state machine ticking
                activation_manager.update(None)
                if config.get('display.show_status'):
                    frame = activation_manager.display_status(frame)

            # --- Action feedback banner ---
            if config.get('display.show_action_feedback'):
                frame = action_executor.display_action(frame)

            # --- FPS overlay ---
            if config.get('display.show_fps'):
                frame = fps_counter.display_fps(frame)

            # --- Display ---
            cv2.imshow(window_name, frame)

            # --- Key handling ---
            key = cv2.waitKey(1) & 0xFF
            if key in (ord('q'), 27):           # 'q' or ESC → quit
                print('\n[Exit] User requested quit. Shutting down...')
                break
            elif key == ord('f'):               # 'f' → toggle fullscreen
                is_fullscreen = not is_fullscreen
                prop = cv2.WINDOW_FULLSCREEN if is_fullscreen else cv2.WINDOW_NORMAL
                cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, prop)
                mode = 'FULLSCREEN' if is_fullscreen else 'WINDOWED'
                print(f'[Window] Switched to {mode} mode')

        print('\n[Complete] Main loop ended.')

    except KeyboardInterrupt:
        print('\n\n[Interrupt] Keyboard interrupt. Shutting down...')

    except Exception as exc:
        print(f'\n[Error] Unexpected error: {exc}')
        import traceback
        traceback.print_exc()

    finally:
        # ------------------------------------------------------------------ #
        # 6. Cleanup                                                           #
        # ------------------------------------------------------------------ #
        print('\n[Cleanup] Releasing resources...')

        if camera:
            camera.release()
            print('  ✓ Camera released')

        if hand_tracker:
            hand_tracker.close()
            print('  ✓ Hand Tracker closed')

        cv2.destroyAllWindows()
        print('  ✓ Windows closed')

        print('\n' + '=' * 60)
        print('MMGI Session Ended')
        print('=' * 60)


if __name__ == '__main__':
    main()
