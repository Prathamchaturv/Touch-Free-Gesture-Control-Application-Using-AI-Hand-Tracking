"""
MMGI - Multi-Modal Gesture Intelligence
Production-Level Modular Architecture

Main orchestration layer that coordinates all modules:
- core: Camera, HandTracker, GestureClassifier
- engine: ActivationManager, DecisionEngine, ActionExecutor
- utils: FPSCounter, Config

Author: MMGI Project
Date: February 2026
Python Version: 3.10+
"""

import cv2
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import all modules
from core.camera import Camera
from core.hand_tracking import HandTracker
from core.gesture_classifier import GestureClassifier
from engine.activation_manager import ActivationManager
from engine.decision_engine import DecisionEngine
from engine.action_executor import ActionExecutor
from utils.fps_counter import FPSCounter
from utils.config import Config


def main():
    """Main orchestration function."""
    print("=" * 60)
    print("MMGI - Multi-Modal Gesture Intelligence")
    print("Production-Level Modular Architecture")
    print("=" * 60)
    
    # Initialize configuration
    config = Config()
    print("\n[Config] Loading configuration...")
    print(f"  Camera: {config.get('camera.width')}x{config.get('camera.height')} @ {config.get('camera.fps')} fps")
    print(f"  Hand Tracking: {config.get('hand_tracking.max_num_hands')} hand(s), {config.get('hand_tracking.min_detection_confidence')} confidence")
    print(f"  Activation: {config.get('activation.open_palm_duration')}s Open Palm, {config.get('activation.cooldown_duration')}s cooldown")
    print(f"  Display: Landmarks={config.get('display.show_landmarks')}, Gesture={config.get('display.show_gesture')}, Status={config.get('display.show_status')}")
    
    # Initialize all components
    camera = None
    hand_tracker = None
    gesture_classifier = None
    activation_manager = None
    decision_engine = None
    action_executor = None
    fps_counter = None
    
    try:
        print("\n[Initialization] Setting up modules...")
        
        # Camera
        camera = Camera(
            width=config.get('camera.width'),
            height=config.get('camera.height'),
            fps=config.get('camera.fps')
        )
        if not camera.open():
            print("  ✗ Failed to open camera")
            return
        print("  ✓ Camera initialized")
        
        # Hand Tracker
        hand_tracker = HandTracker(
            max_num_hands=config.get('hand_tracking.max_num_hands'),
            min_detection_confidence=config.get('hand_tracking.min_detection_confidence'),
            min_tracking_confidence=config.get('hand_tracking.min_tracking_confidence')
        )
        print("  ✓ Hand Tracker initialized")
        
        # Gesture Classifier
        gesture_classifier = GestureClassifier()
        print("  ✓ Gesture Classifier initialized")
        
        # Activation Manager
        activation_manager = ActivationManager(
            open_palm_duration=config.get('activation.open_palm_duration'),
            cooldown_duration=config.get('activation.cooldown_duration'),
            stability_threshold=config.get('activation.stability_threshold')
        )
        print("  ✓ Activation Manager initialized")
        
        # Decision Engine
        decision_engine = DecisionEngine()
        print("  ✓ Decision Engine initialized")
        
        # Action Executor
        action_executor = ActionExecutor(
            config={
                'brave_path': config.get('apps.brave_path'),
                'spotify_path': config.get('apps.spotify_path')
            }
        )
        print("  ✓ Action Executor initialized")
        
        # FPS Counter
        fps_counter = FPSCounter()
        print("  ✓ FPS Counter initialized")
        
        print("\n[Ready] All modules initialized. Starting main loop...")
        print("\nControls:")
        print("  - Show OPEN PALM for 2 seconds to activate")
        print("  - Show FIST to deactivate instantly")
        print("  - Press 'q' or ESC to quit")
        print("\nTwo-Hand Gesture Control:")
        print("  RIGHT HAND (App & Media Control):")
        print("    - ONE FINGER → Launch Brave Browser")
        print("    - TWO FINGERS → Launch Apple Music")
        print("    - RING + PINKY → Next Song")
        print("    - PINKY → Previous Song")
        print("  LEFT HAND (Volume Control):")
        print("    - ONE FINGER → Volume Up")
        print("    - TWO FINGERS → Volume Down")
        print("    - THREE FINGERS → Mute")
        print("    - PINKY → Play/Pause")
        print("\n  * Single-hand fallback: One hand controls everything")
        print("\n" + "=" * 60 + "\n")
        
        # Main loop
        while camera.is_opened():
            # Read frame
            success, frame = camera.read_frame()
            if not success or frame is None:
                print("\n[Warning] Failed to read frame from camera")
                break
            
            # Update FPS
            fps_counter.update()
            
            # Detect hands
            results = hand_tracker.detect_hands(frame)
            hands_info = hand_tracker.get_hands_info(results)
            
            # Draw landmarks
            if config.get('display.show_landmarks') and results.hand_landmarks:
                frame = hand_tracker.draw_landmarks(frame, results)
            
            # Display hand detection status
            if config.get('display.show_hand_detection'):
                frame = hand_tracker.display_hand_detection(frame, hands_info)
            
            # Process hands based on detection mode
            if hands_info['count'] > 0:
                # Determine which hand(s) to process
                left_hand = hands_info['left']
                right_hand = hands_info['right']
                
                # Conflict resolution: Process both hands separately
                # Right hand has priority for activation
                primary_gesture = None
                primary_finger_states = None
                
                # Process right hand (if present)
                if right_hand:
                    right_gesture = gesture_classifier.classify(right_hand['finger_states'])
                    
                    # Display right hand gesture
                    if config.get('display.show_gesture'):
                        frame = gesture_classifier.display_gesture(frame, right_gesture, position='right')
                    
                    # Use right hand for activation
                    primary_gesture = right_gesture
                    primary_finger_states = right_hand['finger_states']
                    
                    # Update activation and check if action should be executed
                    # update() returns True when gesture is stable and ready to trigger
                    should_execute_right = activation_manager.update(right_gesture)
                    
                    # Execute right hand action if triggered
                    if should_execute_right:
                        action = decision_engine.get_action(right_gesture, handedness='right')
                        if action:
                            action_executor.execute(action)
                            print(f"  [RIGHT HAND] Executing: {action}")
                
                # Process left hand
                if left_hand:
                    left_gesture = gesture_classifier.classify(left_hand['finger_states'])
                    
                    # Display left hand gesture
                    if config.get('display.show_gesture'):
                        position = 'left' if right_hand else 'center'
                        frame = gesture_classifier.display_gesture(frame, left_gesture, position=position)
                    
                    # If only left hand present, use it for activation
                    if not right_hand:
                        primary_gesture = left_gesture
                        primary_finger_states = left_hand['finger_states']
                        
                        # Update activation and check if action should be executed
                        should_execute_left = activation_manager.update(left_gesture)
                        
                        # Execute left hand action if triggered
                        if should_execute_left:
                            action = decision_engine.get_action(left_gesture, handedness='left')
                            if action:
                                action_executor.execute(action)
                                print(f"  [LEFT HAND] Executing: {action}")
                    else:
                        # Both hands present: left hand can trigger independently
                        # Only trigger if system is active and not same gesture as right
                        if activation_manager.is_active and left_gesture != right_gesture:
                            # Check if enough time passed and gesture is actionable
                            if not activation_manager.is_in_cooldown and left_gesture not in ["Open Palm", "Fist", "Unknown"]:
                                action = decision_engine.get_action(left_gesture, handedness='left')
                                if action:
                                    action_executor.execute(action)
                                    print(f"  [LEFT HAND] Executing: {action}")
                
                # Display finger states for primary hand
                if config.get('display.show_finger_states') and primary_finger_states:
                    frame = hand_tracker.display_finger_states(frame, primary_finger_states)
                
                # Display status
                if config.get('display.show_status'):
                    frame = activation_manager.display_status(frame)
            
            else:
                # No hand detected - update activation with None
                activation_manager.update(None)
                
                # Display status even when no hand
                if config.get('display.show_status'):
                    frame = activation_manager.display_status(frame)
            
            # Display action feedback
            if config.get('display.show_action_feedback'):
                frame = action_executor.display_action(frame)
            
            # Display FPS
            if config.get('display.show_fps'):
                frame = fps_counter.display_fps(frame)
            
            # Show frame
            cv2.imshow('MMGI - Two-Hand Mode', frame)
            
            # Check for quit
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:  # 'q' or ESC
                print("\n[Exit] User requested quit. Shutting down...")
                break
        
        print("\n[Complete] Main loop ended.")
        
    except KeyboardInterrupt:
        print("\n\n[Interrupt] Keyboard interrupt detected. Shutting down...")
    
    except Exception as e:
        print(f"\n[Error] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        print("\n[Cleanup] Releasing resources...")
        
        if camera:
            camera.release()
            print("  ✓ Camera released")
        
        if hand_tracker:
            hand_tracker.close()
            print("  ✓ Hand Tracker closed")
        
        cv2.destroyAllWindows()
        print("  ✓ Windows closed")
        
        print("\n" + "=" * 60)
        print("MMGI Session Ended")
        print("=" * 60)


if __name__ == "__main__":
    main()
