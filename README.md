# MMGI - Multi-Modal Gesture Intelligence

## Phase 6: Windows Control Integration

A comprehensive hand gesture recognition system using MediaPipe and OpenCV that maps hand gestures to real-world system actions, enabling touchless control of applications and media playback.

---

## 🎯 Features

### Phase 1-2: Core Detection
- ✋ Real-time hand detection and tracking
- 📍 21 hand landmark points visualization
- 🔗 Hand skeleton connections rendering
- 👆 Individual finger state detection (up/down)
- 📊 Live FPS counter display
- 🎥 Laptop webcam integration

### Phase 3: Static Gesture Recognition
- ✊ Fist detection
- 🖐️ Open Palm recognition
- 👍 Thumbs Up gesture
- ☝️ One Finger (pointing)
- ✌️ Two Fingers (peace sign)
- 🤟 Three Fingers gesture
- 🤟 Ring and Pinky gesture
- 👆 Pinky gesture

### Phase 4: Activation & Stability
- 🔓 Activation system (2-second Open Palm hold)
- 🔒 Instant deactivation (Fist gesture)
- ⏱️ Stability checking (10-frame minimum)
- ⏳ Cooldown system (1-second after action)
- 📊 Visual status panel with progress bar

### Phase 6: Windows Control Integration
- 🌐 Launch applications (Brave, Spotify)
- 🎵 Control media playback (next/previous track)
- 💻 System action execution
- 👁️ Visual action feedback
- ⚡ Gesture-to-action mapping
- 🛡️ Safe execution with activation check
- 📊 Maintains ~30 FPS performance

---

## 📋 Prerequisites

- **Operating System**: Windows
- **Python Version**: 3.10 or higher
- **Hardware**: Laptop with built-in camera
- **Internet**: Required for initial package installation

---

## 🚀 Setup Instructions

### Step 1: Verify Python Installation

Open PowerShell or Command Prompt and check your Python version:

```powershell
python --version
```

You should see Python 3.10 or higher. If not, download from [python.org](https://www.python.org/downloads/).

### Step 2: Create Virtual Environment (Recommended)

Navigate to your project directory and create a virtual environment:

```powershell
cd d:\Projects\MMGI
python -m venv venv
```

### Step 3: Activate Virtual Environment

```powershell
.\venv\Scripts\Activate
```

You should see `(venv)` in your command prompt.

### Step 4: Install Dependencies

Install all required packages:

```powershell
pip install -r requirements.txt
```

This will install:
- `opencv-python` - Camera capture and image processing
- `mediapipe` - Hand detection and landmark tracking
- `numpy` - Numerical operations
- `pyautogui` - System control and automation (Phase 6)

**Note**: Installation may take 2-5 minutes depending on your internet connection.

### Step 5: Configure Application Paths (Phase 6)

**Important**: Update application paths in `main.py` to match your system.

Open `main.py` and find the `ActionExecutor` class (around line 410):

```python
class ActionExecutor:
    def __init__(self):
        # Customize these paths for your system:
        self.brave_path = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
        self.spotify_path = r"C:\Users\%USERNAME%\AppData\Roaming\Spotify\Spotify.exe"
```

**To find application paths**:
1. Right-click application shortcut (Desktop or Start Menu)
2. Select "Properties"
3. Copy path from "Target" field
4. Paste into `main.py`

**Default Paths**:
- **Brave**: `C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe`
- **Spotify**: `C:\Users\%USERNAME%\AppData\Roaming\Spotify\Spotify.exe`

**Alternative Browsers** (if you don't have Brave):
- Chrome: `C:\Program Files\Google\Chrome\Application\chrome.exe`
- Firefox: `C:\Program Files\Mozilla Firefox\firefox.exe`
- Edge: `C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe`

### Step 6: Run the Application

```powershell
python main.py
```

---

## 🎮 Usage

### Basic Workflow
1. **Launch**: Run `python main.py`
2. **Activate**: Hold "Open Palm" for 2 seconds
3. **Perform Gestures**: Use control gestures
4. **Execute Actions**: Watch system actions execute
5. **Observe Feedback**: See action confirmation on screen
6. **Deactivate**: Show "Fist" gesture
7. **Exit**: Press `q` key to quit safely

### Control Gestures (Phase 6)
- **One Finger**: 🌐 Launch Brave Browser
- **Two Fingers**: 🎵 Launch Spotify
- **Ring and Pinky**: ⏭️ Next Song (media control)
- **Pinky**: ⏮️ Previous Song (media control)

### System Gestures
- **Open Palm**: Activate system (hold 2 seconds)
- **Fist**: Deactivate system (instant)
- **Thumbs Up**: No action (available for customization)
- **Three Fingers**: No action (available for customization)

---

## 📊 Expected Performance

- **FPS**: ~30 frames per second on average laptops
- **Latency**: Minimal delay (<50ms)
- **Detection**: Works best with good lighting
- **Distance**: Optimal at 30-80cm from camera

---

## 🛠️ Troubleshooting

### Camera Not Opening

**Problem**: "Error: Could not open webcam" message

**Solutions**:
- Close other applications using the camera (Zoom, Teams, etc.)
- Check Windows camera privacy settings
- Try restarting your computer
- Test camera with Windows Camera app first

### Low FPS

**Problem**: FPS below 20

**Solutions**:
- Close background applications
- Ensure good lighting (reduces processing load)
- Check if other programs are using CPU heavily
- Try lowering camera resolution in code (already set to 640x480)

### Import Errors

**Problem**: `ModuleNotFoundError` when running

**Solutions**:
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`
- Check Python version: `python --version`

### Hand Not Detected

**Problem**: No landmarks showing when hand is visible

**Solutions**:
- Improve lighting conditions
- Move hand closer to camera (30-80cm optimal)
- Ensure palm or back of hand is clearly visible
- Avoid cluttered backgrounds
- Check if hand is within camera frame

### Application Not Launching (Phase 6)

**Problem**: "Application Not Found" error when using gesture

**Solutions**:
- Verify application is installed on your system
- Update path in `main.py` → `ActionExecutor.__init__()`
- Use absolute paths (not relative)
- Right-click shortcut → Properties → Copy "Target" path
- Check for typos in file path

### Media Keys Not Working (Phase 6)

**Problem**: Next/Previous song gesture doesn't work

**Solutions**:
- Ensure media player (Spotify, YouTube, etc.) is running
- Test media keys manually on keyboard
- Some players require window focus - click on player first
- Check if your keyboard/laptop supports media keys
- Try with different media player to test

### PyAutoGUI Not Found (Phase 6)

**Problem**: `ModuleNotFoundError: No module named 'pyautogui'`

**Solutions**:
```powershell
# Activate virtual environment first
.\venv\Scripts\Activate

# Then install pyautogui
pip install pyautogui

# Or reinstall all dependencies
pip install -r requirements.txt
```

---

## 📁 Project Structure

```
MMGI/
│
├── main.py                      # Main application script (Phase 6)
├── requirements.txt             # Python dependencies (includes pyautogui)
├── README.md                    # This file
├── PROJECT_OVERVIEW.md          # Architecture deep-dive
│
├── core/                        # Hand tracking & gesture classification
│   ├── camera.py
│   ├── hand_tracking.py
│   └── gesture_classifier.py
│
├── engine/                      # State machine & action execution
│   ├── activation_manager.py
│   ├── decision_engine.py
│   └── action_executor.py
│
├── utils/                       # Config, FPS counter helpers
│   ├── config.py
│   └── fps_counter.py
│
└── config/
    └── gesture_map.json         # Gesture → action mappings
```

---

## 🔧 Configuration

You can adjust detection parameters in `main.py`:

### Hand Detection Settings
```python
detector = HandDetector(
    max_num_hands=1,              # Number of hands to detect
    min_detection_confidence=0.7, # Detection threshold (0.0-1.0)
    min_tracking_confidence=0.5   # Tracking threshold (0.0-1.0)
)
```

### Gesture Controller Settings
```python
gesture_controller = GestureController(
    activation_time=2.0,    # Seconds to hold Open Palm for activation
    cooldown_time=1.0,      # Seconds between gesture triggers
    stability_frames=10     # Frames gesture must be stable
)
```

### Application Paths (Phase 6)
```python
# In ActionExecutor class:
self.brave_path = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
self.spotify_path = r"C:\Users\%USERNAME%\AppData\Roaming\Spotify\Spotify.exe"
```

**Customization**:
- Update paths if applications installed in different locations
- Right-click app shortcut → Properties → Target to find path
- Use absolute paths for reliability

---

## 🎓 Learning Resources

- **MediaPipe Documentation**: [https://google.github.io/mediapipe/](https://google.github.io/mediapipe/)
- **OpenCV Python Tutorial**: [https://docs.opencv.org/](https://docs.opencv.org/)
- **PyAutoGUI Documentation**: [https://pyautogui.readthedocs.io/](https://pyautogui.readthedocs.io/)
- **Phase 1 Guide**: See `MEDIAPIPE_EXPLANATION.md` - Hand landmark details
- **Phase 2 Guide**: See `PHASE2_FINGER_DETECTION.md` - Finger state logic
- **Phase 3 Guide**: See `PHASE3_GESTURE_RECOGNITION.md` - Gesture patterns
- **Phase 4 Guide**: See `PHASE4_ACTIVATION_SYSTEM.md` - State machine design
- **Phase 6 Guide**: See `PHASE6_WINDOWS_CONTROL.md` - System control integration

---

## 📝 Completed Phases

- ✅ Phase 1: Hand detection and landmark tracking
- ✅ Phase 2: Finger state detection
- ✅ Phase 3: Static gesture recognition (8 gestures)
- ✅ Phase 4: Activation and stability system
- ✅ Phase 6: Windows control integration (app launching + media control)

## 🚀 Future Enhancements

- Phase 7: Premium desktop UI (PyQt6 dashboard)
- Window management (minimize, maximize, close)
- Virtual desktop switching
- Screenshot capture on gesture
- Smart home integration (lights, plugs)
- Volume control gestures
- Custom scripting execution
- Gaming controls
- Streaming integration (OBS scene switching)

---

## ⚖️ License

This project is for educational purposes.

---

## 👨‍💻 Author

MMGI Project Team  
February – March 2026

---

## 📧 Support

For issues or questions, please check the troubleshooting section above.

---

**Happy Coding! 🚀**
