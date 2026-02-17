"""
MMGI - Core Module: Gesture Classifier
Pattern-based gesture recognition from finger states.

Author: MMGI Project
Date: February 2026
"""

import cv2


class GestureClassifier:
    """
    Classifies hand gestures based on finger states.
    Supports 8 predefined gestures using pattern matching.
    """
    
    # Gesture pattern definitions
    GESTURE_PATTERNS = {
        (1, 1, 1, 1, 1): "Open Palm",
        (0, 0, 0, 0, 0): "Fist",
        (1, 0, 0, 0, 0): "Thumbs Up",
        (0, 1, 0, 0, 0): "One Finger",
        (0, 1, 1, 0, 0): "Two Fingers",
        (0, 1, 1, 1, 0): "Three Fingers",
        (0, 0, 0, 1, 1): "Ring and Pinky",
        (0, 0, 0, 0, 1): "Pinky",
    }
    
    def __init__(self):
        """Initialize gesture classifier."""
        pass
    
    def classify(self, finger_states):
        """
        Classify gesture from finger states.
        
        Args:
            finger_states: List of 5 integers [thumb, index, middle, ring, pinky]
                          Where 1 = finger up, 0 = finger down
        
        Returns:
            str: Name of detected gesture, or "Unknown" if no match
            
        Examples:
            [1,1,1,1,1] → "Open Palm"
            [0,0,0,0,0] → "Fist"
            [0,1,0,0,0] → "One Finger"
            [0,0,0,1,1] → "Ring and Pinky"
        """
        if not finger_states or len(finger_states) != 5:
            return "Unknown"
        
        pattern = tuple(finger_states)
        return self.GESTURE_PATTERNS.get(pattern, "Unknown")
    
    def display_gesture(self, frame, gesture_name, position='center'):
        """
        Display recognized gesture name on frame.
        
        Args:
            frame: Image to draw on
            gesture_name: String name of the gesture
            position: 'center', 'left', or 'right' for hand-specific display
            
        Returns:
            frame: Frame with gesture name displayed
        """
        if not gesture_name or gesture_name == "Unknown":
            return frame
        
        height, width, _ = frame.shape
        
        # Gesture text with hand label
        if position == 'left':
            text = f"LEFT: {gesture_name}"
            color = (255, 100, 0)  # Blue
            text_x = 20
            text_y = height - 80
        elif position == 'right':
            text = f"RIGHT: {gesture_name}"
            color = (0, 100, 255)  # Orange
            text_x = width - 400
            text_y = height - 80
        else:
            text = f"Gesture: {gesture_name}"
            color = (0, 255, 255)  # Yellow
            font = cv2.FONT_HERSHEY_DUPLEX
            font_scale = 1.2
            font_thickness = 3
            
            # Get text size for background
            text_size = cv2.getTextSize(text, font, font_scale, font_thickness)[0]
            text_x = (width - text_size[0]) // 2
            text_y = height - 30
        
        font = cv2.FONT_HERSHEY_DUPLEX
        font_scale = 1.0 if position != 'center' else 1.2
        font_thickness = 2 if position != 'center' else 3
        
        # Get text size for background
        text_size = cv2.getTextSize(text, font, font_scale, font_thickness)[0]
        
        # Adjust text_x for left/right if needed
        if position == 'center':
            text_x = (width - text_size[0]) // 2
        
        # Semi-transparent background
        overlay = frame.copy()
        padding = 10
        cv2.rectangle(overlay,
                     (text_x - padding, text_y - text_size[1] - padding),
                     (text_x + text_size[0] + padding, text_y + padding),
                     (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        
        # Draw text
        cv2.putText(frame, text, (text_x, text_y),
                   font, font_scale, color, font_thickness, cv2.LINE_AA)
        
        return frame
    
    def get_gesture_list(self):
        """
        Get list of all supported gestures.
        
        Returns:
            list: List of gesture names
        """
        return list(self.GESTURE_PATTERNS.values())
