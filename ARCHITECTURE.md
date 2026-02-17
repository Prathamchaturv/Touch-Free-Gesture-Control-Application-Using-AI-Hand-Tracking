# MMGI - Production-Level Modular Architecture

## Overview
The MMGI project has been successfully refactored from a monolithic 949-line `main.py` into a clean, modular production-level architecture with proper separation of concerns.

## Project Structure

```
D:\Projects\MMGI\
├── main.py                      # Clean orchestration layer (209 lines)
├── main_old.py                  # Backup of original monolithic code
├── hand_landmarker.task        # MediaPipe model
│
├── core/                        # Core detection and classification modules
│   ├── __init__.py
│   ├── camera.py               # Camera management (~80 lines)
│   ├── hand_tracking.py        # Hand detection with MediaPipe (~230 lines)
│   └── gesture_classifier.py  # Gesture pattern recognition (~110 lines)
│
├── engine/                      # Business logic modules
│   ├── __init__.py
│   ├── activation_manager.py  # System state management (~220 lines)
│   ├── decision_engine.py     # Gesture-to-action mapping (~120 lines)
│   └── action_executor.py     # System action execution (~230 lines)
│
├── utils/                       # Utility modules
│   ├── __init__.py
│   ├── fps_counter.py         # Performance tracking (~70 lines)
│   └── config.py              # Configuration management (~170 lines)
│
└── config/                      # Configuration files
    └── gesture_map.json       # Gesture action mappings (JSON)
```

## Module Descriptions

### Core Modules

#### `core/camera.py` - Camera Class
**Purpose**: Manages webcam initialization and frame capture  
**Key Methods**:
- `__init__(index, width, height, fps)` - Initialize camera with parameters
- `read_frame()` - Capture and return current frame
- `is_opened()` - Check if camera is available
- `release()` - Clean up camera resources

#### `core/hand_tracking.py` - HandTracker Class
**Purpose**: MediaPipe hand detection and landmark visualization  
**Key Methods**:
- `detect_hands(frame)` - Detect hands in frame and return landmarks
- `draw_landmarks(frame, hands_data)` - Visualize hand skeleton
- `get_finger_states(hands_data)` - Calculate which fingers are up/down
- `display_finger_states(frame, finger_states)` - Show finger states on screen
- `close()` - Clean up MediaPipe resources

**Features**:
- Downloads MediaPipe model automatically if missing
- Uses Tasks API for Python 3.14+ compatibility
- 21-landmark hand skeleton tracking
- Real-time finger state detection (Thumb, Index, Middle, Ring, Pinky)

#### `core/gesture_classifier.py` - GestureClassifier Class
**Purpose**: Recognize gestures from finger states  
**Key Methods**:
- `classify(finger_states)` - Identify gesture from finger pattern
- `display_gesture(frame, gesture_name)` - Show current gesture on screen

**Supported Gestures**:
1. **Open Palm** - All fingers up
2. **Fist** - All fingers down
3. **Thumbs Up** - Only thumb up
4. **One Finger** - Only index up
5. **Two Fingers** - Index + Middle up
6. **Three Fingers** - Index + Middle + Ring up
7. **Ring and Pinky** - Only Ring + Pinky up
8. **Pinky** - Only pinky up

### Engine Modules

#### `engine/activation_manager.py` - ActivationManager Class
**Purpose**: Manage system activation state with stability and cooldown  
**Key Methods**:
- `update(gesture_name, finger_states)` - Update activation state
- `is_activated()` - Check if system is active
- `can_execute_action()` - Check if action can be executed (cooldown cleared)
- `action_executed()` - Mark action as executed (start cooldown)
- `display_status(frame)` - Show activation status on screen

**Features**:
- **Activation**: Hold Open Palm for 2 seconds (configurable)
- **Deactivation**: Instant Fist gesture
- **Stability**: Gestures must be stable for 10 frames
- **Cooldown**: 1-second delay between actions
- Visual progress bar during activation

#### `engine/decision_engine.py` - DecisionEngine Class
**Purpose**: Map gestures to actions  
**Key Methods**:
- `get_action(gesture_name)` - Get action for given gesture
- `has_action(gesture_name)` - Check if gesture has mapped action
- `update_mapping(gesture, action)` - Change gesture-to-action mapping
- `save_mappings()` - Save mappings to JSON file

**Default Mappings** (from `config/gesture_map.json`):
- **One Finger** → `open_brave` (Launch Brave Browser)
- **Two Fingers** → `open_spotify` (Launch Spotify)
- **Ring and Pinky** → `next_song` (Media Next)
- **Pinky** → `previous_song` (Media Previous)

#### `engine/action_executor.py` - ActionExecutor Class
**Purpose**: Execute system actions  
**Key Methods**:
- `execute(action_name)` - Execute action by name
- `open_brave()` - Launch Brave Browser
- `open_spotify()` - Launch Spotify
- `next_song()` - Send media next key
- `previous_song()` - Send media previous key
- `display_action(frame)` - Show action feedback on screen

**Features**:
- Non-blocking app launches using `subprocess.Popen()`
- Media key simulation via PyAutoGUI
- 2-second visual feedback after action execution
- Process checking to avoid duplicate launches

**Application Paths**:
- Brave: `C:\Users\vivek\AppData\Local\BraveSoftware\Brave-Browser\Application\brave.exe`
- Spotify: `C:\Users\%USERNAME%\AppData\Roaming\Spotify\Spotify.exe`

### Utility Modules

#### `utils/fps_counter.py` - FPSCounter Class
**Purpose**: Track and display frame rate  
**Key Methods**:
- `update()` - Update FPS calculation
- `get_fps()` - Get current FPS value
- `display_fps(frame)` - Show FPS on screen

#### `utils/config.py` - Config Class
**Purpose**: Centralized configuration management  
**Key Methods**:
- `get(key_path)` - Get config value using dot notation (e.g., "camera.width")
- `set(section, key, value)` - Set configuration value
- `save()` - Save current config to file
- `reset_to_defaults()` - Reset to default configuration

**Default Configuration**:
```python
{
    "camera": {
        "index": 0,
        "width": 640,
        "height": 480,
        "fps": 30
    },
    "hand_tracking": {
        "max_num_hands": 1,
        "min_detection_confidence": 0.7,
        "min_tracking_confidence": 0.5
    },
    "activation": {
        "open_palm_duration": 2.0,
        "cooldown_duration": 1.0,
        "stability_threshold": 10
    },
    "apps": {
        "brave_path": "C:\\Users\\vivek\\AppData\\Local\\BraveSoftware\\Brave-Browser\\Application\\brave.exe",
        "spotify_path": "C:\\Users\\%USERNAME%\\AppData\\Roaming\\Spotify\\Spotify.exe"
    },
    "display": {
        "show_fps": true,
        "show_landmarks": true,
        "show_finger_states": true,
        "show_gesture": true,
        "show_status": true,
        "show_action_feedback": true
    }
}
```

### Configuration Files

#### `config/gesture_map.json`
Defines gesture-to-action mappings in JSON format:
```json
{
    "One Finger": "open_brave",
    "Two Fingers": "open_spotify",
    "Ring and Pinky": "next_song",
    "Pinky": "previous_song"
}
```

### Main Orchestration

#### `main.py` - Main Function
**Purpose**: Coordinate all modules in a clean main loop  
**Flow**:
1. Load configuration
2. Initialize all modules
3. Main loop:
   - Read camera frame
   - Detect hands
   - Classify gesture
   - Update activation state
   - Execute action if activated
   - Display all visualizations
   - Check for quit command
4. Clean up resources

**User Controls**:
- Show **Open Palm** for 2 seconds to activate
- Show **Fist** to deactivate instantly
- Press **'q'** or **ESC** to quit

## Key Improvements

### 1. Separation of Concerns
- **Detection** (core) separated from **logic** (engine) and **utilities**
- Each module has a single responsibility (SRP)
- Clear interfaces between components

### 2. Configurability
- JSON-based configuration for easy customization
- Dot notation for nested config access
- Runtime config updates without code changes

### 3. Maintainability
- Reduced main.py from 949 lines to 209 lines
- Each module is independently testable
- Easy to add new gestures or actions

### 4. Extensibility
- Add new gestures by updating `gesture_classifier.py`
- Add new actions by updating `action_executor.py`
- Map gestures to actions via `gesture_map.json`

### 5. Clean Code
- Consistent naming conventions
- Comprehensive docstrings
- Type hints where appropriate
- Error handling and resource cleanup

## Testing Results

✅ All modules initialized successfully  
✅ Camera acquisition working  
✅ Hand detection functional  
✅ Gesture classification accurate  
✅ Activation/deactivation system working  
✅ Brave browser launches correctly  
✅ Spotify launches correctly  
✅ Media keys (Next/Previous) functional  
✅ FPS counter displaying correctly  
✅ All visualizations working  

## How to Run

```powershell
cd D:\Projects\MMGI
.\venv\Scripts\Activate.ps1
python main.py
```

## Dependencies

- Python 3.14.0
- MediaPipe 0.10.32 (Tasks API)
- OpenCV 4.13.0.92
- NumPy 2.4.2
- PyAutoGUI 0.9.54

## Future Enhancements

### Potential Improvements:
1. **Add more gestures**: Peace sign, OK sign, etc.
2. **Add more actions**: Volume control, window management
3. **Plugin system**: Dynamically load action modules
4. **Web interface**: Control and configure via browser
5. **Gesture recording**: Record gesture sequences
6. **Multi-hand support**: Different actions for left/right hands
7. **Context awareness**: Different mappings for different apps
8. **Voice feedback**: Audio confirmation of actions
9. **Logging system**: Track usage statistics
10. **Unit tests**: Comprehensive test coverage

## Conclusion

The MMGI project has been successfully transformed from a monolithic script into a professional, production-ready modular architecture. The code is now:
- **Maintainable**: Easy to understand and modify
- **Extensible**: Simple to add new features
- **Configurable**: Customizable without code changes
- **Testable**: Each module can be tested independently
- **Professional**: Follows software engineering best practices

All original functionality has been preserved, and the system is fully operational!
