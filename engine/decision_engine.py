"""
MMGI - Engine Module: Decision Engine
Maps gestures to actions and coordinates execution.

Author: MMGI Project
Date: February 2026
"""

import json
import os


class DecisionEngine:
    """
    Decision engine that maps gestures to actions.
    Loads gesture-action mappings from configuration file.
    """
    
    def __init__(self, config_path="config/gesture_map.json"):
        """
        Initialize decision engine.
        
        Args:
            config_path (str): Path to gesture mapping configuration file
        """
        self.config_path = config_path
        self.gesture_map = self._load_gesture_map()
    
    def _load_gesture_map(self):
        """
        Load gesture-to-action mapping from config file.
        
        Returns:
            dict: Gesture mapping dictionary
        """
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load gesture map: {e}")
                return self._get_default_map()
        else:
            return self._get_default_map()
    
    def _get_default_map(self):
        """
        Get default gesture-to-action mapping.
        
        Returns:
            dict: Default gesture mappings with left/right hand support
        """
        return {
            "right": {
                "One Finger": "open_brave",
                "Two Fingers": "open_spotify",
                "Ring and Pinky": "next_song",
                "Pinky": "previous_song"
            },
            "left": {
                "One Finger": "volume_up",
                "Two Fingers": "volume_down",
                "Three Fingers": "mute",
                "Pinky": "play_pause"
            }
        }
    
    def get_action(self, gesture_name, handedness=None):
        """
        Get action mapped to a gesture.
        
        Args:
            gesture_name (str): Name of the gesture
            handedness (str, optional): "left" or "right". If None, uses single-hand mode.
            
        Returns:
            str or None: Action name, or None if no mapping exists
        """
        # Two-hand mode: check if gesture_map has left/right structure
        if handedness and isinstance(self.gesture_map.get('left'), dict):
            hand_map = self.gesture_map.get(handedness, {})
            return hand_map.get(gesture_name)
        
        # Single-hand mode (backward compatibility)
        return self.gesture_map.get(gesture_name)
    
    def has_action(self, gesture_name, handedness=None):
        """
        Check if gesture has an action mapped.
        
        Args:
            gesture_name (str): Name of the gesture
            handedness (str, optional): "left" or "right"
            
        Returns:
            bool: True if gesture has an action, False otherwise
        """
        if handedness and isinstance(self.gesture_map.get('left'), dict):
            hand_map = self.gesture_map.get(handedness, {})
            return gesture_name in hand_map
        
        return gesture_name in self.gesture_map
    
    def get_all_mappings(self):
        """
        Get all gesture-to-action mappings.
        
        Returns:
            dict: Complete gesture mapping dictionary
        """
        return self.gesture_map.copy()
    
    def update_mapping(self, gesture_name, action_name):
        """
        Update or add a gesture-to-action mapping.
        
        Args:
            gesture_name (str): Name of the gesture
            action_name (str): Name of the action
        """
        self.gesture_map[gesture_name] = action_name
    
    def remove_mapping(self, gesture_name):
        """
        Remove a gesture-to-action mapping.
        
        Args:
            gesture_name (str): Name of the gesture to remove
        """
        if gesture_name in self.gesture_map:
            del self.gesture_map[gesture_name]
    
    def save_mappings(self):
        """Save current mappings to configuration file."""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(self.gesture_map, f, indent=4)
            print(f"Gesture mappings saved to {self.config_path}")
        except Exception as e:
            print(f"Error saving gesture mappings: {e}")
