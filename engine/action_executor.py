"""
MMGI - Engine Module: Action Executor
Executes system actions (launch apps, control media, etc.).

Author: MMGI Project
Date: February 2026
"""

import subprocess
import os
import time
import cv2
import pyautogui


class ActionExecutor:
    """
    Executes system actions based on gestures.
    
    Supported actions:
    - Launch applications (Brave, Spotify, etc.)
    - Control media playback (next, previous, play/pause)
    - System commands
    """
    
    def __init__(self, config=None):
        """
        Initialize action executor.
        
        Args:
            config (dict): Configuration dictionary with app paths, etc.
        """
        self.config = config or {}
        
        # Default application paths
        self.app_paths = {
            "brave": self.config.get("brave_path", 
                r"C:\Users\vivek\AppData\Local\BraveSoftware\Brave-Browser\Application\brave.exe"),
            "apple_music": self.config.get("apple_music_path",
                r"C:\Program Files\WindowsApps\AppleInc.AppleMusic_*\AppleMusic.exe"),
        }
        
        # Visual feedback tracking
        self.last_action = None
        self.last_action_time = 0
        self.action_display_duration = 2.0
    
    def execute(self, action_name):
        """
        Execute an action by name.
        
        Args:
            action_name (str): Name of action to execute
            
        Returns:
            tuple: (success: bool, message: str)
        """
        action_method = getattr(self, action_name, None)
        
        if action_method and callable(action_method):
            try:
                result = action_method()
                self.last_action = result
                self.last_action_time = time.time()
                return True, result
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                self.last_action = error_msg
                self.last_action_time = time.time()
                print(f"  ⚠️ {error_msg}")
                return False, error_msg
        else:
            return False, f"Unknown action: {action_name}"
    
    # ========== Application Launch Actions ==========
    
    def open_brave(self):
        """Launch Brave browser."""
        try:
            subprocess.Popen([self.app_paths["brave"]])
            print("  🌐 Launching Brave Browser...")
            return "Opening Brave"
        except FileNotFoundError:
            print("  ⚠️ Brave not found. Update path in config.")
            return "Brave Not Found"
    
    def open_apple_music(self):
        """Launch Apple Music."""
        try:
            # Launch Apple Music using Windows Store App ID
            subprocess.Popen(["explorer.exe", "shell:AppsFolder\\AppleInc.AppleMusicWin_nzyj5cx40ttqa!App"])
            print("  🎵 Launching Apple Music...")
            return "Opening Apple Music"
        except Exception as e:
            print(f"  ⚠️ Could not launch Apple Music: {e}")
            return "Apple Music Launch Failed"
    
    # ========== Media Control Actions ==========
    
    def next_song(self):
        """Skip to next track."""
        pyautogui.press('nexttrack')
        print("  ⏭️ Next Track")
        return "Next Track"
    
    def previous_song(self):
        """Go to previous track."""
        pyautogui.press('prevtrack')
        print("  ⏮️ Previous Track")
        return "Previous Track"
    
    def play_pause(self):
        """Toggle play/pause."""
        pyautogui.press('playpause')
        print("  ⏯️ Play/Pause")
        return "Play/Pause"
    
    def volume_up(self):
        """Increase volume."""
        pyautogui.press('volumeup')
        print("  🔊 Volume Up")
        return "Volume Up"
    
    def volume_down(self):
        """Decrease volume."""
        pyautogui.press('volumedown')
        print("  🔉 Volume Down")
        return "Volume Down"
    
    def mute(self):
        """Toggle mute."""
        pyautogui.press('volumemute')
        print("  🔇 Mute")
        return "Mute"
    
    # ========== Visual Feedback ==========
    
    def get_display_action(self):
        """
        Get current action for display.
        
        Returns:
            str or None: Action name if within display window
        """
        if self.last_action:
            if time.time() - self.last_action_time < self.action_display_duration:
                return self.last_action
            else:
                self.last_action = None
        return None
    
    def display_action(self, frame):
        """
        Display executed action on frame.
        
        Args:
            frame: Image to draw on
            
        Returns:
            frame: Frame with action display
        """
        action = self.get_display_action()
        if not action:
            return frame
        
        height, width, _ = frame.shape
        
        # Position at top center
        text_x = width // 2 - 150
        text_y = 60
        
        # Semi-transparent background
        overlay = frame.copy()
        cv2.rectangle(overlay, (text_x - 20, text_y - 40),
                     (text_x + 320, text_y + 10), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.8, frame, 0.2, 0, frame)
        
        # Choose color based on action type
        if "Error" in action or "Not Found" in action:
            color = (0, 0, 255)  # Red
        elif "Brave" in action:
            color = (255, 165, 0)  # Orange
        elif "Spotify" in action:
            color = (0, 255, 0)  # Green
        elif "Next" in action or "Previous" in action:
            color = (255, 255, 0)  # Yellow
        elif "Volume" in action or "Mute" in action:
            color = (255, 0, 255)  # Magenta
        else:
            color = (255, 255, 255)  # White
        
        # Draw action text
        action_text = f"ACTION: {action}"
        cv2.putText(frame, action_text, (text_x, text_y),
                   cv2.FONT_HERSHEY_DUPLEX, 1.0, color, 2, cv2.LINE_AA)
        
        return frame
    
    # ========== Configuration ==========
    
    def update_app_path(self, app_name, path):
        """
        Update application path.
        
        Args:
            app_name (str): Application name (e.g., "brave", "spotify")
            path (str): Full path to executable
        """
        if app_name in self.app_paths:
            self.app_paths[app_name] = path
            print(f"Updated {app_name} path: {path}")
    
    def get_app_paths(self):
        """
        Get all configured application paths.
        
        Returns:
            dict: Application paths dictionary
        """
        return self.app_paths.copy()
