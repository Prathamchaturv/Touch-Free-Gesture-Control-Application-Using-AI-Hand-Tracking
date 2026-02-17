"""
MMGI - Utils Module: FPS Counter
Tracks and displays frames per second.

Author: MMGI Project
Date: February 2026
"""

import time
import cv2


class FPSCounter:
    """
    Simple FPS counter to measure and display frame rate.
    """
    
    def __init__(self):
        """Initialize FPS counter."""
        self.prev_time = time.time()
        self.fps = 0
    
    def update(self):
        """
        Update FPS calculation.
        
        Returns:
            float: Current FPS value
        """
        current_time = time.time()
        time_diff = current_time - self.prev_time
        
        if time_diff > 0:
            self.fps = 1.0 / time_diff
        
        self.prev_time = current_time
        return self.fps
    
    def get_fps(self):
        """
        Get current FPS value.
        
        Returns:
            float: Current FPS
        """
        return self.fps
    
    def display_fps(self, frame):
        """
        Draw FPS text on frame.
        
        Args:
            frame: Image to draw on
            
        Returns:
            frame: Frame with FPS display
        """
        height, width, _ = frame.shape
        
        # FPS text
        fps_text = f"FPS: {self.fps:.1f}"
        
        # Position in top-left corner
        text_x = 10
        text_y = 30
        
        # Semi-transparent background
        overlay = frame.copy()
        cv2.rectangle(overlay, (text_x - 5, text_y - 25),
                     (text_x + 90, text_y + 5), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
        
        # Draw FPS text
        cv2.putText(frame, fps_text, (text_x, text_y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        return frame
    
    def reset(self):
        """Reset FPS counter."""
        self.prev_time = time.time()
        self.fps = 0
