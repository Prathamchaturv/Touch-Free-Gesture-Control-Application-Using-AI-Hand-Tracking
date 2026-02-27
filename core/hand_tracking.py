"""
core/hand_tracking.py - The Hand Detective

Uses MediaPipe AI technology to:
- Find hands in camera frames
- Identify 21 landmark points (fingertips, knuckles, wrist, etc.)
- Draw the hand skeleton visualisation
- Determine which fingers are up or down
- Distinguish between left and right hands
- Support up to 2 hands simultaneously
"""

import cv2
import mediapipe as mp


class HandTracker:
    """
    Wraps MediaPipe Hands to provide hand detection, landmark extraction,
    finger-state analysis, and on-screen drawing.
    """

    # MediaPipe solutions shortcuts
    _MP_HANDS = mp.solutions.hands
    _MP_DRAWING = mp.solutions.drawing_utils
    _MP_DRAWING_STYLES = mp.solutions.drawing_styles

    # Landmark indices used for finger state detection
    #                 thumb  index middle ring  pinky
    _TIP_IDS  = [4,    8,    12,   16,   20]
    _PIP_IDS  = [3,    6,    10,   14,   18]  # IP for thumb, PIP for others
    _MCP_IDS  = [2,    5,     9,   13,   17]

    def __init__(
        self,
        max_num_hands: int = 2,
        min_detection_confidence: float = 0.7,
        min_tracking_confidence: float = 0.5,
    ):
        self._hands = self._MP_HANDS.Hands(
            static_image_mode=False,
            max_num_hands=max_num_hands,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )

    # ------------------------------------------------------------------
    # Detection
    # ------------------------------------------------------------------

    def detect_hands(self, frame):
        """
        Run MediaPipe inference on a BGR frame.
        Returns the raw MediaPipe results object.
        """
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False
        results = self._hands.process(rgb)
        rgb.flags.writeable = True
        return results

    def get_hands_info(self, results) -> dict:
        """
        Parse MediaPipe results into a structured dict:
        {
            'count': int,
            'left':  hand_data | None,
            'right': hand_data | None,
        }

        Each hand_data dict has:
            'landmarks'    : list of (x, y, z) normalised coords
            'finger_states': dict of finger→bool (True = extended)
            'handedness'   : 'Left' | 'Right'
        """
        info: dict = {'count': 0, 'left': None, 'right': None}

        if not results.multi_hand_landmarks:
            return info

        for hand_landmarks, handedness in zip(
            results.multi_hand_landmarks, results.multi_handedness
        ):
            label: str = handedness.classification[0].label  # 'Left' or 'Right'
            finger_states = self._get_finger_states(hand_landmarks)
            landmarks_list = [
                (lm.x, lm.y, lm.z) for lm in hand_landmarks.landmark
            ]

            hand_data = {
                'landmarks': landmarks_list,
                'finger_states': finger_states,
                'handedness': label,
            }

            info['count'] += 1
            # MediaPipe labels are from the subject's perspective (mirrored)
            if label == 'Right':
                info['right'] = hand_data
            else:
                info['left'] = hand_data

        return info

    # ------------------------------------------------------------------
    # Finger state detection
    # ------------------------------------------------------------------

    def _get_finger_states(self, hand_landmarks) -> dict:
        """
        Determine which fingers are extended (True) or curled (False).

        Thumb  : extended when tip.x is far from wrist (horizontal spread)
        Others : extended when tip.y < pip.y (tip higher than middle joint)
        """
        lm = hand_landmarks.landmark
        states: dict = {}

        # --- Thumb ---
        # Compare x-distance: tip vs IP joint relative to MCP
        thumb_tip = lm[4]
        thumb_ip  = lm[3]
        thumb_mcp = lm[2]
        wrist     = lm[0]

        tip_dist = abs(thumb_tip.x - wrist.x)
        ip_dist  = abs(thumb_ip.x  - wrist.x)
        states['thumb'] = tip_dist > ip_dist

        # --- Index, Middle, Ring, Pinky ---
        finger_data = [
            ('index',  8,  6),
            ('middle', 12, 10),
            ('ring',   16, 14),
            ('pinky',  20, 18),
        ]
        for name, tip_id, pip_id in finger_data:
            states[name] = lm[tip_id].y < lm[pip_id].y

        return states

    # ------------------------------------------------------------------
    # Visualisation
    # ------------------------------------------------------------------

    def draw_landmarks(self, frame, results):
        """Draw hand skeleton connections and landmark dots onto the frame."""
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self._MP_DRAWING.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self._MP_HANDS.HAND_CONNECTIONS,
                    self._MP_DRAWING_STYLES.get_default_hand_landmarks_style(),
                    self._MP_DRAWING_STYLES.get_default_hand_connections_style(),
                )
        return frame

    def display_hand_detection(self, frame, hands_info: dict):
        """Render hand count badge in the top-right corner."""
        h, w = frame.shape[:2]
        text = f"Hands: {hands_info['count']}"
        cv2.putText(
            frame, text, (w - 150, 30),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2, cv2.LINE_AA,
        )
        # Label each hand
        for key, colour in [('right', (0, 255, 100)), ('left', (100, 200, 255))]:
            if hands_info.get(key):
                lms = hands_info[key]['landmarks']
                # Use wrist landmark (index 0) to anchor the label
                wx = int(lms[0][0] * w)
                wy = int(lms[0][1] * h) + 20
                cv2.putText(
                    frame, key.upper(), (wx - 20, wy),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, colour, 2, cv2.LINE_AA,
                )
        return frame

    def display_finger_states(self, frame, finger_states: dict):
        """Render finger up/down states in the bottom-left corner."""
        h = frame.shape[0]
        y = h - 150
        for name, up in finger_states.items():
            colour = (0, 255, 0) if up else (0, 0, 220)
            label  = f'{name}: {"UP" if up else "DOWN"}'
            cv2.putText(
                frame, label, (10, y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.48, colour, 1, cv2.LINE_AA,
            )
            y += 26
        return frame

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------

    def close(self) -> None:
        """Release MediaPipe resources."""
        self._hands.close()
