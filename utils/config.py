"""
MMGI - Utils Module: Configuration Management
Handles loading and saving configuration settings.

Author: MMGI Project
Date: February 2026
"""

import json
import os


class Config:
    """
    Configuration manager for MMGI system.
    Loads settings from config file and provides defaults.
    """
    
    DEFAULT_CONFIG = {
        "camera": {
            "index": 0,
            "width": 640,
            "height": 480,
            "fps": 30
        },
        "hand_tracking": {
            "max_num_hands": 2,
            "min_detection_confidence": 0.7,
            "min_tracking_confidence": 0.5,
            "two_hand_mode": True
        },
        "activation": {
            "open_palm_duration": 2.0,
            "cooldown_duration": 1.0,
            "stability_threshold": 10
        },
        "apps": {
            "brave_path": r"C:\Users\vivek\AppData\Local\BraveSoftware\Brave-Browser\Application\brave.exe",
            "apple_music_path": r"C:\Program Files\WindowsApps"
        },
        "display": {
            "show_fps": True,
            "show_landmarks": True,
            "show_finger_states": True,
            "show_gesture": True,
            "show_status": True,
            "show_action_feedback": True,
            "show_hand_detection": True
        }
    }
    
    def __init__(self, config_path="config/settings.json"):
        """
        Initialize configuration manager.
        
        Args:
            config_path (str): Path to configuration file
        """
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self):
        """
        Load configuration from file or use defaults.
        
        Returns:
            dict: Configuration dictionary
        """
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    loaded_config = json.load(f)
                # Merge with defaults (use loaded values where available)
                return self._merge_configs(self.DEFAULT_CONFIG.copy(), loaded_config)
            except Exception as e:
                print(f"Warning: Could not load config from {self.config_path}: {e}")
                print("Using default configuration")
                return self.DEFAULT_CONFIG.copy()
        else:
            return self.DEFAULT_CONFIG.copy()
    
    def _merge_configs(self, default, loaded):
        """
        Recursively merge loaded config with defaults.
        
        Args:
            default (dict): Default configuration
            loaded (dict): Loaded configuration
            
        Returns:
            dict: Merged configuration
        """
        for key, value in loaded.items():
            if key in default and isinstance(default[key], dict) and isinstance(value, dict):
                default[key] = self._merge_configs(default[key], value)
            else:
                default[key] = value
        return default
    
    def get(self, key_path, default=None):
        """
        Get configuration value using dot notation.
        
        Args:
            key_path (str): Configuration key path (e.g., "camera.width", "activation.open_palm_duration")
            default: Default value if not found
            
        Returns:
            Value from configuration, or default if not found
        """
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set(self, section, key, value):
        """
        Set configuration value.
        
        Args:
            section (str): Configuration section
            key (str): Configuration key
            value: Value to set
        """
        if section not in self.config:
            self.config[section] = {}
        
        self.config[section][key] = value
    
    def save(self):
        """Save current configuration to file."""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=4)
            print(f"Configuration saved to {self.config_path}")
        except Exception as e:
            print(f"Error saving configuration: {e}")
    
    def get_all(self):
        """
        Get complete configuration.
        
        Returns:
            dict: Complete configuration dictionary
        """
        return self.config.copy()
    
    def reset_to_defaults(self):
        """Reset configuration to default values."""
        self.config = self.DEFAULT_CONFIG.copy()
        print("Configuration reset to defaults")
