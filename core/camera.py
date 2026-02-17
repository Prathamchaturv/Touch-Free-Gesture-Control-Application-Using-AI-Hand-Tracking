"""
MMGI - Core Module: Camera
Handles webcam capture and frame management.

Author: MMGI Project
Date: February 2026
"""

import cv2


class Camera:
    """
    Camera manager for webcam capture.
    Handles initialization, frame capture, and resource cleanup.
    """
    
    def __init__(self, camera_index=0, width=640, height=480, fps=30):
        """
        Initialize camera with specified parameters.
        
        Args:
            camera_index (int): Camera device index (default: 0 for built-in webcam)
            width (int): Frame width in pixels
            height (int): Frame height in pixels
            fps (int): Target frames per second
        """
        self.camera_index = camera_index
        self.width = width
        self.height = height
        self.fps = fps
        self.cap = None
        
    def open(self):
        """
        Open camera connection and configure settings.
        
        Returns:
            bool: True if camera opened successfully, False otherwise
        """
        self.cap = cv2.VideoCapture(self.camera_index)
        
        if not self.cap.isOpened():
            print("Error: Could not open webcam.")
            print("Please check:")
            print("  1. Camera is connected properly")
            print("  2. No other application is using the camera")
            print("  3. Camera permissions are enabled")
            return False
        
        # Set camera properties
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.cap.set(cv2.CAP_PROP_FPS, self.fps)
        
        print(f"Camera initialized: {self.width}x{self.height} @ {self.fps}fps")
        return True
    
    def read_frame(self):
        """
        Read a single frame from the camera.
        
        Returns:
            tuple: (success, frame) where success is bool and frame is numpy array
        """
        if self.cap is None or not self.cap.isOpened():
            return False, None
        
        success, frame = self.cap.read()
        return success, frame
    
    def release(self):
        """Release camera resources."""
        if self.cap is not None:
            self.cap.release()
            print("Camera released")
    
    def is_opened(self):
        """
        Check if camera is currently opened.
        
        Returns:
            bool: True if camera is opened, False otherwise
        """
        return self.cap is not None and self.cap.isOpened()
