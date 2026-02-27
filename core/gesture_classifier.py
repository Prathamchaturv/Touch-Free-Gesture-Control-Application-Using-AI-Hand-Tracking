"""
core/gesture_classifier.py - The Pattern Recognizer

Takes finger-state information (which fingers are up/down) from the hand
tracker and matches it against known gesture patterns to return a
human-readable gesture name.

Recognised gestures:
    Open Palm    – all 5 fingers extended        (activation trigger)
    Fist         – all fingers curled            (deactivation trigger)
    Thumbs Up    – only thumb extended
    One Finger   – only index finger up          (pointing)
    Two Fingers  – index + middle up             (peace sign)
    Three Fingers– index + middle + ring up
    Ring and Pinky – ring + pinky only up
    Pinky        – only pinky up
"""

import cv2


class GestureClassifier:
    """
    Classifies a set of finger states into a named gesture.

    Gesture patterns are ordered from most-specific to least-specific
    to avoid false positives.
    """

    # Each entry: gesture_name → {finger: expected_state}
    # Fingers not listed are treated as "don't care" (ignored).
    # For full-hand gestures (Open Palm / Fist) all five are checked.
    _PATTERNS: list[tuple[str, dict]] = [
        ('Open Palm',     {'thumb': True,  'index': True,  'middle': True,  'ring': True,  'pinky': True}),
        ('Fist',          {'thumb': False, 'index': False, 'middle': False, 'ring': False, 'pinky': False}),
        ('Thumbs Up',     {'thumb': True,  'index': False, 'middle': False, 'ring': False, 'pinky': False}),
        ('Three Fingers', {'index': True,  'middle': True,  'ring': True,  'pinky': False}),
        ('Two Fingers',   {'index': True,  'middle': True,  'ring': False, 'pinky': False}),
        ('Ring and Pinky',{'index': False, 'middle': False, 'ring': True,  'pinky': True}),
        ('One Finger',    {'index': True,  'middle': False, 'ring': False, 'pinky': False}),
        ('Pinky',         {'index': False, 'middle': False, 'ring': False, 'pinky': True}),
    ]

    # Gestures that require ALL five fingers to be checked
    _FULL_CHECK = {'Open Palm', 'Fist', 'Thumbs Up'}

    # ------------------------------------------------------------------
    # Classification
    # ------------------------------------------------------------------

    def classify(self, finger_states: dict) -> str:
        """
        Return the gesture name that best matches the given finger states.
        Falls back to 'Unknown' if no pattern matches.

        Args:
            finger_states: dict with keys 'thumb','index','middle','ring','pinky'
                           and bool values (True = extended).
        """
        if not finger_states:
            return 'Unknown'

        for gesture_name, pattern in self._PATTERNS:
            if gesture_name in self._FULL_CHECK:
                # Every finger must match exactly
                if all(finger_states.get(f) == v for f, v in pattern.items()):
                    return gesture_name
            else:
                # Only the fingers listed in the pattern are checked
                if all(finger_states.get(f) == v for f, v in pattern.items()):
                    return gesture_name

        return 'Unknown'

    # ------------------------------------------------------------------
    # Visualisation
    # ------------------------------------------------------------------

    def display_gesture(self, frame, gesture: str, position: str = 'center'):
        """
        Render the gesture label on the frame.

        Args:
            position: 'right' | 'left' | 'center'
        """
        h, w = frame.shape[:2]

        if position == 'right':
            x = w - 310
        elif position == 'left':
            x = 10
        else:
            x = w // 2 - 150

        y = 68

        # Background pill
        text = f'Gesture: {gesture}'
        (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
        cv2.rectangle(frame, (x - 6, y - th - 6), (x + tw + 6, y + 6),
                      (30, 30, 30), -1)
        cv2.rectangle(frame, (x - 6, y - th - 6), (x + tw + 6, y + 6),
                      (0, 200, 200), 1)

        cv2.putText(
            frame, text, (x, y),
            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2, cv2.LINE_AA,
        )
        return frame
