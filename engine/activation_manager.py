"""
MMGI - Engine Module: Activation Manager
Manages system activation, deactivation, stability, and cooldown.

Author: MMGI Project
Date: February 2026
"""

import time


class ActivationManager:
    """
    Manages gesture system activation state.
    
    Features:
    - Activation: Hold "Open Palm" for specified duration
    - Deactivation: Instant "Fist" gesture
    - Stability: Gestures must be stable for minimum frames
    - Cooldown: Prevent rapid repeated actions
    """
    
    def __init__(self, open_palm_duration=2.0, cooldown_duration=1.0, stability_threshold=10):
        """
        Initialize activation manager.
        
        Args:
            open_palm_duration (float): Seconds to hold Open Palm for activation
            cooldown_duration (float): Seconds between gesture triggers
            stability_threshold (int): Frames gesture must be stable
        """
        # Configuration
        self.activation_time = open_palm_duration
        self.cooldown_time = cooldown_duration
        self.stability_frames = stability_threshold
        
        # Activation state
        self.is_active = False
        self.activation_start_time = 0
        self.activation_progress = 0.0
        
        # Stability tracking
        self.stable_gesture = None
        self.gesture_frame_count = 0
        
        # Cooldown tracking
        self.is_in_cooldown = False
        self.cooldown_end_time = 0
    
    def update(self, gesture_name):
        """
        Update activation state based on current gesture.
        
        Args:
            gesture_name: Currently detected gesture
            
        Returns:
            bool: True if gesture triggered an action, False otherwise
        """
        current_time = time.time()
        
        # Update cooldown status
        if self.is_in_cooldown and current_time >= self.cooldown_end_time:
            self.is_in_cooldown = False
        
        # Handle activation logic (Open Palm)
        if not self.is_active and gesture_name == "Open Palm":
            if self.activation_start_time == 0:
                self.activation_start_time = current_time
            
            elapsed = current_time - self.activation_start_time
            self.activation_progress = min(elapsed / self.activation_time, 1.0)
            
            if elapsed >= self.activation_time:
                self.is_active = True
                self.activation_start_time = 0
                self.activation_progress = 0
                print("✓ System ACTIVATED")
        else:
            self.activation_start_time = 0
            self.activation_progress = 0
        
        # Handle deactivation (Fist)
        if self.is_active and gesture_name == "Fist":
            self.is_active = False
            self.stable_gesture = None
            self.gesture_frame_count = 0
            print("✕ System DEACTIVATED")
            return False
        
        # If system not active, no gesture processing
        if not self.is_active:
            return False
        
        # Stability checking
        if gesture_name == self.stable_gesture:
            self.gesture_frame_count += 1
        else:
            self.stable_gesture = gesture_name
            self.gesture_frame_count = 1
        
        # Check if gesture is stable and cooldown passed
        if (self.gesture_frame_count >= self.stability_frames and 
            not self.is_in_cooldown and
            gesture_name not in ["Open Palm", "Fist", "Unknown"]):
            
            # Gesture triggered
            print(f"→ Stable gesture triggered: {gesture_name}")
            
            # Start cooldown
            self.is_in_cooldown = True
            self.cooldown_end_time = current_time + self.cooldown_time
            
            # Reset stability counter
            self.gesture_frame_count = 0
            
            return True
        
        return False
    
    def get_status_text(self):
        """
        Get current status as text.
        
        Returns:
            str: Status description
        """
        if not self.is_active:
            return "INACTIVE"
        
        if self.is_in_cooldown:
            remaining = self.cooldown_end_time - time.time()
            return f"ACTIVE (Cooldown: {remaining:.1f}s)"
        
        return "ACTIVE"
    
    def display_status(self, frame):
        """
        Display activation status panel on frame.
        
        Args:
            frame: Image to draw on
            
        Returns:
            frame: Frame with status display
        """
        import cv2
        
        height, width, _ = frame.shape
        
        # Status panel in top-right corner
        panel_width = 250
        panel_height = 120
        panel_x = width - panel_width - 10
        panel_y = 10
        
        # Semi-transparent background
        overlay = frame.copy()
        cv2.rectangle(overlay, (panel_x, panel_y), 
                     (panel_x + panel_width, panel_y + panel_height), 
                     (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        
        # Title
        cv2.putText(frame, "System Status:", (panel_x + 10, panel_y + 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Status text
        status_text = "ACTIVE" if self.is_active else "INACTIVE"
        status_color = (0, 255, 0) if self.is_active else (0, 0, 255)
        
        cv2.putText(frame, status_text, (panel_x + 10, panel_y + 65),
                   cv2.FONT_HERSHEY_DUPLEX, 1.0, status_color, 2)
        
        # Activation progress bar
        if not self.is_active and self.activation_progress > 0:
            bar_width = int((panel_width - 20) * self.activation_progress)
            cv2.rectangle(frame, (panel_x + 10, panel_y + 80),
                         (panel_x + 10 + bar_width, panel_y + 95),
                         (0, 255, 255), -1)
            cv2.rectangle(frame, (panel_x + 10, panel_y + 80),
                         (panel_x + panel_width - 10, panel_y + 95),
                         (255, 255, 255), 2)
        
        # Cooldown indicator
        if self.is_active and self.is_in_cooldown:
            remaining = self.cooldown_end_time - time.time()
            cooldown_text = f"Cooldown: {remaining:.1f}s"
            cv2.putText(frame, cooldown_text, (panel_x + 10, panel_y + 100),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 165, 0), 1)
        
        # Ready indicator
        if self.is_active and self.stable_gesture and not self.is_in_cooldown:
            cv2.putText(frame, "Ready", (panel_x + 10, panel_y + 100),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        return frame
    
    def reset(self):
        """Reset activation manager to initial state."""
        self.is_active = False
        self.activation_start_time = 0
        self.activation_progress = 0
        self.stable_gesture = None
        self.gesture_frame_count = 0
        self.is_in_cooldown = False
        self.cooldown_end_time = 0
