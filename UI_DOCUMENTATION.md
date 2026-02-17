# MMGI Professional Dashboard

## Overview

Professional desktop UI for MMGI gesture control system built with Tkinter. Provides real-time monitoring, control, and activity logging while the gesture detection runs in a background thread.

---

## Architecture

### Threading Model

```
┌─────────────────┐         ┌──────────────────┐
│   Main Thread   │◄───────►│ Background Thread│
│  (Tkinter UI)   │  Queues │   (MMGI Core)    │
└─────────────────┘         └──────────────────┘
        │                            │
        │                            ├─ Camera
        │                            ├─ Hand Tracking
        │                            ├─ Gesture Recognition
        │                            └─ Action Execution
        │
        ├─ Dashboard Display
        ├─ Control Panel
        └─ Activity Log
```

### Communication

**Command Queue** (UI → Core):
- `('start', None)` - Start gesture detection
- `('stop', None)` - Stop gesture detection  
- `('mode', 'app')` - Change control mode

**Status Queue** (Core → UI):
- `('gesture', "One Finger")` - Current gesture update
- `('hands', {...})` - Hand detection info
- `('fps', 30.5)` - FPS update
- `('action', ('volume_up', 'left'))` - Action executed
- `('log', "message")` - Log entry

---

## Components

### 1. **ui/dashboard.py** - MMGIDashboard Class

Professional Tkinter interface with:

#### Features:
- **System Controls**: ON/OFF toggle, mode selection
- **Status Display**: Active/Inactive, hand detection, current gesture
- **Activity Log**: Scrolling log of all gesture events
- **Volume Indicator**: Visual volume level display
- **FPS Counter**: Real-time performance monitoring

#### Key Methods:
- `__init__(master=None)` - Initialize dashboard
- `update_gesture(gesture_name)` - Update gesture display
- `update_hands(hands_info)` - Update hand detection
- `log_action(action_name, hand)` - Log executed action
- `run()` - Start UI main loop (blocking)

#### Styling:
- Modern dark theme (#1e1e1e background)
- Custom ttk styles for consistent look
- Color-coded status indicators
- Responsive layout (900x700 default)

### 2. **ui/core_wrapper.py** - MMGICore Class

Threading wrapper that runs MMGI in background:

#### Responsibilities:
- Initialize all MMGI components (camera, tracking, etc.)
- Run gesture detection loop in separate thread
- Process UI commands from queue
- Send status updates to UI
- Handle resource cleanup

#### Key Methods:
- `__init__(command_queue, status_queue)` - Setup with queues
- `run()` - Main thread loop (overrides Thread.run())
- `stop()` - Graceful shutdown
- `_process_commands()` - Handle UI commands
- `_initialize_components()` - Setup MMGI modules

#### Thread Safety:
- Daemon thread (auto-closes with main thread)
- Queue-based communication (thread-safe)
- No shared mutable state
- Proper resource cleanup on exit

### 3. **main_ui.py** - Entry Point

Launches MMGI with UI:

```python
# Create UI
dashboard = MMGIDashboard()

# Create core thread
core = MMGICore(
    command_queue=dashboard.get_command_queue(),
    status_queue=dashboard.get_status_queue()
)

# Start background processing
core.start()

# Run UI (blocks until window closes)
dashboard.run()

# Cleanup
core.stop()
core.join()
```

---

## Running the UI

### Launch Dashboard:
```bash
cd D:\Projects\MMGI
python main_ui.py
```

### Launch Classic Mode (no UI):
```bash
python main.py
```

---

## UI Usage

### 1. **Start System**
1. Click **⚡ START SYSTEM** button
2. Status changes to **ACTIVE** (green)
3. Camera feed starts processing

### 2. **Select Mode**
Choose control mode:
- 🚀 **App Control** - Launch applications
- 🎵 **Media Control** - Playback control
- ⚙️ **System Control** - System operations

### 3. **Use Gestures**
- Show **OPEN PALM** for 2 seconds to activate
- Use hand gestures to trigger actions
- Actions appear in activity log
- **4 Fingers** = Cycle through modes

### 4. **Monitor Activity**
- **Current Gesture**: Large display shows active gesture
- **Hands Detected**: Shows LEFT/RIGHT/BOTH
- **FPS**: Frame rate indicator
- **Activity Log**: Scrolling event history

### 5. **Stop System**
1. Click **⚡ STOP SYSTEM** button
2. Gesture detection stops
3. Camera continues running (for instant restart)

---

## Mode System

### Gesture Mode Switching

**4 Fingers Gesture** → Cycles through modes:
- App → Media → System → App

Each mode has different gesture-to-action mappings:

**App Mode (🚀)**:
- One Finger → Brave Browser
- Two Fingers → Spotify
- Ring + Pinky → Next Track
- Pinky → Previous Track

**Media Mode (🎵)**:
- One Finger → Play/Pause
- Two Fingers → Next Track
- Three Fingers → Previous Track
- Open Palm → Volume Up
- Fist → Volume Down

**System Mode (⚙️)**:
- One Finger → Screenshot
- Two Fingers → Lock Screen
- Three Fingers → Task View
- Open Palm → Maximize Window

*(Note: Media and System modes are placeholders - you can customize)*

---

## Configuration

### Customizing the UI

Edit `ui/dashboard.py`:

```python
# Window size
self.root.geometry("900x700")  # Change dimensions

# Colors
bg_dark = '#1e1e1e'     # Main background
bg_medium = '#2d2d2d'   # Panel background
accent_green = '#4CAF50' # Active color
accent_red = '#f44336'   # Inactive color

# Update rate
self.root.after(50, self._update_ui)  # 50ms = 20 updates/sec
```

### Adding Custom Modes

Edit `ui/dashboard.py` MODES dict:

```python
MODES = {
    'app': {'name': 'App Control', 'color': '#4CAF50', 'icon': '🚀'},
    'media': {'name': 'Media Control', 'color': '#2196F3', 'icon': '🎵'},
    'system': {'name': 'System Control', 'color': '#FF9800', 'icon': '⚙️'},
    'custom': {'name': 'Custom Mode', 'color': '#9C27B0', 'icon': '⭐'}  # Add this
}
```

---

## Threading Implementation Details

### Why Threading?

**Problem**: Tkinter UI runs in main thread and blocks. Camera processing would freeze the UI.

**Solution**: Run MMGI core in daemon background thread, communicate via queues.

### Queue Communication Pattern

```python
# UI sends command to core
command_queue.put(('start', None))

# Core sends update to UI  
status_queue.put(('gesture', "One Finger"))

# UI processes updates (called every 50ms)
while not status_queue.empty():
    msg_type, data = status_queue.get_nowait()
    # Update UI based on message
```

### Synchronization

- **Queues are thread-safe** (Python queue.Queue)
- **No locks needed** for communication
- **UI updates only in main thread** (Tkinter requirement)
- **Core never touches UI directly**

### Graceful Shutdown

```python
# 1. User closes window
dashboard.run()  # Returns when window closes

# 2. Signal core to stop
core.stop()  # Sets running=False flag

# 3. Wait for thread to finish
core.join(timeout=2)  # Max 2 seconds

# 4. Cleanup happens in core thread
camera.release()
hand_tracker.close()
cv2.destroyAllWindows()
```

---

## Troubleshooting

### UI doesn't open
- Check Python has tkinter: `python -m tkinter`
- Install if missing: `pip install tk`

### Gestures not working
1. Click **START SYSTEM** button
2. Check Status shows **ACTIVE**
3. Verify camera access in Activity Log

### UI freezing
- Should NOT happen with threading
- If it does, check for exceptions in core thread
- Check Activity Log for error messages

### High CPU usage
- Normal: ~10-20% CPU (camera processing)
- High: Check FPS - should be ~25-30
- Reduce by lowering camera resolution in config

---

## Performance

### Typical Resource Usage:
- **CPU**: 10-20% (single core)
- **RAM**: ~150-200 MB
- **FPS**: 25-30 (depends on camera)
- **UI Updates**: 20 Hz (every 50ms)

### Optimization Tips:
1. Lower camera resolution (640x480 → 320x240)
2. Reduce hand tracking confidence threshold
3. Increase UI update interval (50ms → 100ms)
4. Disable camera feed display

---

## Future Enhancements

### Possible Additions:
1. **Camera Feed Display** - Show video in UI window
2. **Gesture Customization** - GUI for mapping gestures
3. **Profile System** - Save/load different configurations
4. **Statistics Panel** - Gesture usage analytics
5. **Hotkey System** - Keyboard shortcuts for modes
6. **System Tray Icon** - Minimize to tray
7. **Multi-language** - Internationalization support
8. **Voice Feedback** - TTS for action confirmations
9. **Recording Mode** - Record gesture sequences
10. **Remote Control** - Network API for remote access

---

## API Reference

### MMGIDashboard

```python
class MMGIDashboard:
    def __init__(self, master=None)
    def update_gesture(self, gesture_name: str)
    def update_hands(self, hands_info: dict)
    def update_fps(self, fps: float)
    def log_action(self, action_name: str, hand: str = '')
    def run(self)
    def get_command_queue(self) -> queue.Queue
    def get_status_queue(self) -> queue.Queue
```

### MMGICore

```python
class MMGICore(threading.Thread):
    def __init__(self, command_queue: queue.Queue, status_queue: queue.Queue)
    def run(self)  # Override Thread.run()
    def stop(self)
    def _initialize_components(self) -> bool
    def _cleanup(self)
    def _process_commands(self)
```

---

## License & Credits

Part of MMGI - Multi-Modal Gesture Intelligence Project  
Built with Python, Tkinter, MediaPipe, OpenCV  
Threading model inspired by MVC architecture

---

**Happy Gesture Controlling! 🖐️**
