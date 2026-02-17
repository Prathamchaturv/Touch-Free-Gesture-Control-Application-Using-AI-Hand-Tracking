"""
MMGI - Core Module: Hand Tracking
MediaPipe-based hand landmark detection and visualization.

Author: MMGI Project
Date: February 2026
"""

import cv2
import numpy as np
import urllib.request
import os
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


# Model configuration
MODEL_PATH = "hand_landmarker.task"
MODEL_URL = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"


def download_model():
    """Download the hand landmarker model if not already present."""
    if not os.path.exists(MODEL_PATH):
        print("Downloading hand landmarker model...")
        print("This is a one-time download (~10 MB)")
        try:
            urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
            print("Model downloaded successfully!")
        except Exception as e:
            print(f"Error downloading model: {e}")
            print("Please download manually from:")
            print(MODEL_URL)
            return False
    return True


class HandTracker:
    """
    Hand tracking using MediaPipe HandLandmarker.
    Detects hand landmarks and provides finger state information.
    
    Landmark indices:
    - Wrist: 0
    - Thumb: 1-4 (CMC, MCP, IP, tip)
    - Index: 5-8 (MCP, PIP, DIP, tip)
    - Middle: 9-12
    - Ring: 13-16
    - Pinky: 17-20
    """
    
    # Hand connections for visualization
    HAND_CONNECTIONS = [
        (0, 1), (1, 2), (2, 3), (3, 4),  # Thumb
        (0, 5), (5, 6), (6, 7), (7, 8),  # Index
        (0, 9), (9, 10), (10, 11), (11, 12),  # Middle
        (0, 13), (13, 14), (14, 15), (15, 16),  # Ring
        (0, 17), (17, 18), (18, 19), (19, 20),  # Pinky
        (5, 9), (9, 13), (13, 17), (0, 5), (0, 17)  # Palm
    ]
    
    def __init__(self, max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.5):
        """
        Initialize hand tracker.
        
        Args:
            max_num_hands (int): Maximum number of hands to detect
            min_detection_confidence (float): Detection threshold (0.0-1.0)
            min_tracking_confidence (float): Tracking threshold (0.0-1.0)
        """
        # Ensure model is downloaded
        if not download_model():
            raise RuntimeError("Failed to download hand landmarker model")
        
        # Create HandLandmarker options
        base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.VIDEO,
            num_hands=max_num_hands,
            min_hand_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        
        # Create HandLandmarker
        self.detector = vision.HandLandmarker.create_from_options(options)
        self.timestamp_ms = 0
    
    def detect_hands(self, frame):
        """
        Detect hands in the frame.
        
        Args:
            frame: BGR image from camera
            
        Returns:
            HandLandmarkerResult: Detection results with hand landmarks and handedness
        """
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Create MediaPipe Image
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        
        # Detect hand landmarks
        self.timestamp_ms += 1
        results = self.detector.detect_for_video(mp_image, self.timestamp_ms)
        
        return results
    
    def get_hands_info(self, results):
        """
        Extract hand information with handedness labels.
        
        Args:
            results: HandLandmarkerResult from detection
            
        Returns:
            dict: {
                'left': {'landmarks': [...], 'finger_states': [...]},
                'right': {'landmarks': [...], 'finger_states': [...]},
                'count': int (number of hands detected)
            }
        """
        hands_info = {
            'left': None,
            'right': None,
            'count': 0
        }
        
        if not results.hand_landmarks or not results.handedness:
            return hands_info
        
        hands_info['count'] = len(results.hand_landmarks)
        
        # Process each detected hand
        for hand_landmarks, handedness in zip(results.hand_landmarks, results.handedness):
            # Get handedness label (MediaPipe returns "Left" or "Right")
            hand_label = handedness[0].category_name.lower()
            
            # Get finger states for this hand (pass handedness for correct thumb detection)
            finger_states = self.get_finger_states(hand_landmarks, hand_label)
            
            hands_info[hand_label] = {
                'landmarks': hand_landmarks,
                'finger_states': finger_states
            }
        
        return hands_info
    
    def draw_landmarks(self, frame, results):
        """
        Draw hand landmarks and connections on frame.
        
        Args:
            frame: Image to draw on
            results: HandLandmarkerResult from detection
            
        Returns:
            frame: Frame with landmarks drawn
        """
        if not results.hand_landmarks:
            return frame
        
        height, width, _ = frame.shape
        
        # Draw each detected hand
        for hand_landmarks in results.hand_landmarks:
            # Draw connections
            for connection in self.HAND_CONNECTIONS:
                start_idx, end_idx = connection
                start_point = hand_landmarks[start_idx]
                end_point = hand_landmarks[end_idx]
                
                start_x = int(start_point.x * width)
                start_y = int(start_point.y * height)
                end_x = int(end_point.x * width)
                end_y = int(end_point.y * height)
                
                cv2.line(frame, (start_x, start_y), (end_x, end_y), (0, 255, 0), 2)
            
            # Draw landmarks
            for landmark in hand_landmarks:
                x = int(landmark.x * width)
                y = int(landmark.y * height)
                cv2.circle(frame, (x, y), 5, (0, 0, 255), -1)
        
        return frame
    
    def get_finger_states(self, hand_landmarks, handedness='right'):
        """
        Determine which fingers are up or down.
        
        Args:
            hand_landmarks: List of 21 hand landmarks
            handedness: 'left' or 'right' hand (needed for thumb detection)
            
        Returns:
            list: [thumb, index, middle, ring, pinky] where 1=up, 0=down
        """
        fingers = []
        
        # Thumb: Check x-position relative to MCP joint
        # For right hand: thumb up means tip is to the right of MCP
        # For left hand: thumb up means tip is to the left of MCP
        thumb_tip = hand_landmarks[4]
        thumb_mcp = hand_landmarks[2]
        
        if handedness == 'left':
            # Left hand: thumb up = tip.x < mcp.x (tip is to the left)
            thumb_up = 1 if thumb_tip.x < thumb_mcp.x else 0
        else:
            # Right hand: thumb up = tip.x > mcp.x (tip is to the right)
            thumb_up = 1 if thumb_tip.x > thumb_mcp.x else 0
        
        fingers.append(thumb_up)
        
        # Other fingers: Compare tip y-coordinate with PIP joint
        finger_tips = [8, 12, 16, 20]  # Index, Middle, Ring, Pinky
        finger_pips = [6, 10, 14, 18]
        
        for tip_idx, pip_idx in zip(finger_tips, finger_pips):
            finger_up = 1 if hand_landmarks[tip_idx].y < hand_landmarks[pip_idx].y else 0
            fingers.append(finger_up)
        
        return fingers
    
    def display_finger_states(self, frame, finger_states):
        """
        Display finger states panel on frame.
        
        Args:
            frame: Image to draw on
            finger_states: List of 5 integers [thumb, index, middle, ring, pinky]
            
        Returns:
            frame: Frame with finger states panel
        """
        if not finger_states or len(finger_states) != 5:
            return frame
        
        finger_names = ["Thumb", "Index", "Middle", "Ring", "Pinky"]
        
        # Semi-transparent panel
        overlay = frame.copy()
        cv2.rectangle(overlay, (10, 80), (240, 270), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
        
        # Title
        cv2.putText(frame, "Finger States:", (20, 95),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Draw each finger state
        for i, (name, state) in enumerate(zip(finger_names, finger_states)):
            y_pos = 130 + (i * 28)
            
            # Finger name
            cv2.putText(frame, name, (20, y_pos),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
            
            # State indicator
            color = (0, 255, 0) if state == 1 else (0, 0, 255)
            status_text = "UP" if state == 1 else "DOWN"
            
            cv2.circle(frame, (160, y_pos - 5), 8, color, -1)
            cv2.circle(frame, (160, y_pos - 5), 9, (255, 255, 255), 1)
            cv2.putText(frame, status_text, (180, y_pos),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        # Finger count
        fingers_up = sum(finger_states)
        cv2.putText(frame, f"Count: {fingers_up}", (20, 260),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        
        return frame
    
    def display_hand_detection(self, frame, hands_info):
        """
        Display hand detection status (LEFT/RIGHT/BOTH).
        
        Args:
            frame: Image to draw on
            hands_info: Dictionary with left/right hand info
            
        Returns:
            frame: Frame with hand detection panel
        """
        if hands_info['count'] == 0:
            return frame
        
        # Determine status text
        if hands_info['left'] and hands_info['right']:
            status_text = "BOTH HANDS DETECTED"
            status_color = (0, 255, 255)  # Yellow
        elif hands_info['left']:
            status_text = "LEFT HAND DETECTED"
            status_color = (255, 100, 0)  # Blue
        elif hands_info['right']:
            status_text = "RIGHT HAND DETECTED"
            status_color = (0, 100, 255)  # Orange
        else:
            return frame
        
        # Get frame dimensions
        height, width = frame.shape[:2]
        
        # Calculate text size and position (top center)
        font = cv2.FONT_HERSHEY_DUPLEX
        font_scale = 0.8
        thickness = 2
        (text_width, text_height), baseline = cv2.getTextSize(status_text, font, font_scale, thickness)
        
        # Position at top center
        x = (width - text_width) // 2
        y = 40
        
        # Draw semi-transparent background
        padding = 10
        overlay = frame.copy()
        cv2.rectangle(overlay, 
                     (x - padding, y - text_height - padding),
                     (x + text_width + padding, y + baseline + padding),
                     (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
        
        # Draw text
        cv2.putText(frame, status_text, (x, y),
                   font, font_scale, status_color, thickness)
        
        return frame
    
    def close(self):
        """Release MediaPipe resources."""
        if self.detector:
            self.detector.close()
