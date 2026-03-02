# MMGI Project Overview
## What Each Component Does

This document provides a high-level explanation of every component in the MMGI (Multi-Modal Gesture Intelligence) project, describing **what** each part does without diving into code implementation details.

---

## 🎯 Project Purpose

MMGI is a **hand gesture recognition system** that allows you to control your Windows computer using hand gestures captured through your webcam. The system can:
- Detect and track your hands in real-time
- Recognize specific hand gestures
- Map gestures to computer actions (launching apps, controlling media, adjusting volume)
- Execute those actions safely with an activation system

---

## 📁 Project Structure Overview

### **main.py** - The Orchestra Conductor
This is the central control file that brings everything together. It:
- Initializes all the system components
- Runs the main loop that captures camera frames continuously
- Coordinates between all modules (camera → hand detection → gesture recognition → action execution)
- Handles user input (keyboard shortcuts like 'q' to quit, 'f' for fullscreen)
- Manages the lifecycle (startup, running, cleanup)

**Why it matters**: This is where everything connects. Without this orchestrator, all the individual components would work in isolation.

---

## 🔧 Core Modules (`core/` folder)

These modules handle the fundamental detection and recognition capabilities.

### **camera.py** - The Eyes
**What it does**:
- Opens and manages your laptop's webcam
- Captures video frames continuously (30 times per second)
- Provides frame data to other components
- Handles camera cleanup when closing the program

**Think of it as**: A dedicated camera operator that never stops recording.

---

### **hand_tracking.py** - The Hand Detective
**What it does**:
- Uses MediaPipe AI technology to find hands in camera frames
- Identifies 21 specific points (landmarks) on each hand (fingertips, knuckles, wrist, etc.)
- Draws the hand skeleton visualization on screen (those colorful dots and lines)
- Determines which fingers are up or down
- Distinguishes between left and right hands
- Supports tracking up to 2 hands simultaneously

**Key capabilities**:
- **Hand Detection**: "Is there a hand in this image?"
- **Landmark Tracking**: "Where exactly are the fingertips, knuckles, and wrist?"
- **Finger State Analysis**: "Which fingers are pointing up vs curled down?"
- **Handedness**: "Is this the left hand or right hand?"

**Think of it as**: A specialized detective that can spot hands and analyze their exact position and configuration.

---

### **gesture_classifier.py** - The Pattern Recognizer
**What it does**:
- Takes the finger state information (which fingers are up/down)
- Matches patterns to identify specific gestures
- Displays the recognized gesture name on screen

**Gestures it recognizes**:
1. **Open Palm** - All 5 fingers extended (used for activation)
2. **Fist** - All fingers closed (used for deactivation)
3. **Thumbs Up** - Only thumb extended
4. **One Finger** - Only index finger up (pointing)
5. **Two Fingers** - Index and middle fingers up (peace sign)
6. **Three Fingers** - Index, middle, and ring fingers up
7. **Ring and Pinky** - Only ring and pinky fingers up
8. **Pinky** - Only pinky finger up

**Think of it as**: A translator that converts hand positions into meaningful gesture names.

---

## ⚙️ Engine Modules (`engine/` folder)

These modules handle the "business logic" - the decision-making and action execution.

### **activation_manager.py** - The Safety Gatekeeper
**What it does**:
- Manages the system's ON/OFF state
- Requires you to hold "Open Palm" for 2 seconds to turn ON (prevents accidental activations)
- Allows instant OFF with a "Fist" gesture
- Ensures gestures are stable (not flickering) for 10 frames before accepting them
- Implements a 1-second cooldown between actions (prevents accidental repeated actions)
- Shows visual feedback with a status panel and progress bar

**Safety features**:
- **Activation Delay**: Must hold Open Palm for 2 full seconds
- **Stability Check**: Gesture must be consistent for at least 10 frames
- **Cooldown Period**: 1-second wait after each action
- **Visual Status**: Always shows whether system is INACTIVE, ACTIVATING, or ACTIVE

**Think of it as**: A security guard that ensures you really mean to trigger an action before allowing it.

---

### **decision_engine.py** - The Strategy Planner
**What it does**:
- Loads the gesture-to-action mapping from the configuration file
- Determines which computer action should be executed for a given gesture
- Implements hand-specific logic (different actions for left vs right hand)
- Provides fallback behavior when only one hand is detected

**Mapping strategy**:
- **Right Hand**: Controls applications and media navigation
  - One Finger → Open Brave Browser
  - Two Fingers → Open Apple Music/Spotify
  - Ring + Pinky → Next Song
  - Pinky → Previous Song

- **Left Hand**: Controls audio and playback
  - One Finger → Volume Up
  - Two Fingers → Volume Down
  - Three Fingers → Mute
  - Pinky → Play/Pause

**Think of it as**: A dispatcher that decides which action should happen based on which gesture you showed and which hand made it.

---

### **action_executor.py** - The Action Performer
**What it does**:
- Actually executes the computer actions (launches apps, presses media keys, adjusts volume)
- Uses PyAutoGUI to simulate keyboard presses and system commands
- Handles Windows-specific paths and commands
- Shows visual feedback on screen when an action is executed
- Implements error handling for failed actions

**Actions it can perform**:
- **Launch Applications**: Open Brave browser, Spotify, Apple Music
- **Media Control**: Next track, previous track, play/pause
- **Volume Control**: Increase, decrease, mute/unmute
- **System Commands**: Various keyboard shortcuts and system controls

**Think of it as**: The hands (literally!) that press the buttons and execute commands on your behalf.

---

## 🛠️ Utility Modules (`utils/` folder)

These modules provide supporting functionality.

### **fps_counter.py** - The Performance Monitor
**What it does**:
- Tracks how many frames per second the system is processing
- Calculates and displays FPS on screen
- Provides performance feedback to ensure smooth operation

**Why it matters**: 
- Helps you verify the system is running smoothly (target: ~30 FPS)
- Indicates if your computer is struggling (low FPS might mean performance issues)

**Think of it as**: A speedometer for your gesture recognition system.

---

### **config.py** - The Settings Manager
**What it does**:
- Loads configuration settings from JSON files
- Provides default values if configuration files are missing
- Centralizes all configurable parameters
- Allows easy adjustment of system behavior without changing code

**Settings it manages**:
- Camera resolution and frame rate
- Hand detection confidence thresholds
- Activation timing parameters
- Display preferences (what to show/hide)
- Application paths

**Think of it as**: A control panel where all adjustable settings live.

---

## 📋 Configuration Files (`config/` folder)

### **gesture_map.json** - The Action Dictionary
**What it contains**:
- JSON mapping of gestures to actions
- Separate mappings for left and right hands
- Easy to edit without touching code

**Purpose**: Allows you to customize which gestures trigger which actions by simply editing a text file.

---

## 📖 Documentation Files

### **README.md** - User Guide
**What it contains**:
- Complete setup instructions
- How to install dependencies
- How to run the project
- Available features and controls
- Troubleshooting tips

**Audience**: Users who want to set up and use the system.

---

### **ARCHITECTURE.md** - Technical Architecture
**What it contains**:
- Detailed module breakdown
- Class descriptions and key methods
- Design decisions and patterns
- Code organization explanations

**Audience**: Developers who want to understand or modify the codebase.

---

### **TWO_HAND_MODE.md** - Dual Hand Control Guide
**What it contains**:
- How two-hand mode works
- Conflict resolution strategies
- Priority system explanation
- Hand-specific gesture mappings

**Audience**: Users and developers wanting to understand the two-hand control system.

---

### **Phase Documentation Files**
- **PHASE2_FINGER_DETECTION.md**: How individual finger detection works
- **PHASE3_GESTURE_RECOGNITION.md**: Gesture pattern recognition details
- **PHASE4_ACTIVATION_SYSTEM.md**: Activation and safety system details
- **PHASE6_WINDOWS_CONTROL.md**: Windows integration and action execution

**Purpose**: Historical documentation of development phases and technical deep-dives.

---

### **MEDIAPIPE_EXPLANATION.md** - MediaPipe Technology Guide
**What it contains**:
- How MediaPipe hand tracking works
- Technical details about the AI model
- Understanding landmarks and coordinates

**Audience**: Those curious about the underlying hand detection technology.

---

## 🔄 System Workflow

Here's how everything works together when you run the program:

### 1. **Initialization Phase**
- **Config** loads all settings
- **Camera** opens the webcam
- **HandTracker** initializes MediaPipe AI model
- **GestureClassifier** prepares gesture patterns
- **ActivationManager** starts in INACTIVE state
- **DecisionEngine** loads gesture-to-action mappings
- **ActionExecutor** prepares for system control
- **FPSCounter** starts tracking performance

### 2. **Main Loop (runs 30 times per second)**
   1. **Camera** captures a new frame
   2. **HandTracker** analyzes frame for hands
   3. If hand(s) found:
      - **HandTracker** draws landmarks on frame
      - **HandTracker** determines finger states
      - **HandTracker** identifies handedness (left/right)
      - **GestureClassifier** recognizes gesture from finger states
      - **ActivationManager** checks if gesture should activate/deactivate system
      - If system is ACTIVE and not in cooldown:
        - **DecisionEngine** determines which action to execute
        - **ActionExecutor** performs the action
        - **ActivationManager** starts cooldown timer
   4. **FPSCounter** updates performance metrics
   5. All visual feedback is drawn on frame
   6. Frame is displayed in window
   7. Check for user input (q/ESC to quit, f for fullscreen)

### 3. **Cleanup Phase**
- **Camera** releases webcam
- **HandTracker** closes MediaPipe resources
- Windows are destroyed
- Program exits gracefully

---

## 🎮 How To Use The System

### **Basic Operation**
1. Run `python main.py`
2. A window opens showing your webcam feed
3. Show **Open Palm** gesture with your right hand
4. Hold steady for 2 seconds (watch the progress bar)
5. System becomes **ACTIVE** (green status)
6. Perform gestures to control your computer
7. Show **Fist** to instantly deactivate
8. Press 'q' or ESC to quit

### **Two-Hand Control**
- **Right hand**: Controls apps and media navigation
- **Left hand**: Controls volume and playback
- Both hands can trigger actions simultaneously
- Single hand? It controls everything for that hand's gesture map

### **Safety Features**
- Won't accidentally trigger - requires 2-second activation
- Gestures must be stable - no flickering allowed
- 1-second cooldown prevents rapid repeated actions
- Visual feedback shows exactly what's happening

---

## 🔧 Dependencies (What External Tools Are Used)

### **OpenCV (opencv-python)**
**Purpose**: Camera capture and image processing
**What it does**: Opens webcam, reads frames, displays windows, draws graphics

### **MediaPipe**
**Purpose**: AI-powered hand detection and tracking
**What it does**: Uses machine learning to find hands and identify 21 landmark points

### **NumPy**
**Purpose**: Fast numerical operations
**What it does**: Handles arrays and mathematical calculations efficiently

### **PyAutoGUI**
**Purpose**: System control and automation
**What it does**: Simulates keyboard presses, launches applications, controls media

---

## 🎯 Key Design Principles

### **1. Modularity**
Each component has one clear responsibility and can be modified independently.

### **2. Safety First**
Multiple layers of safety prevent accidental actions (activation delay, stability check, cooldown).

### **3. Visual Feedback**
Everything has visual confirmation - you always know what the system sees and what state it's in.

### **4. Configurability**
Settings are in JSON files - easy to customize without touching code.

### **5. Performance**
Optimized to run at ~30 FPS on typical laptops while doing complex AI processing.

---

## 📊 System States

The system operates in three main states:

### **INACTIVE** (Red)
- Default state on startup
- System is watching but not responding to gestures
- Waiting for Open Palm activation gesture

### **ACTIVATING** (Yellow)
- Open Palm detected
- Timer counting up to 2 seconds
- Progress bar shows how long to hold
- Release too early = returns to INACTIVE

### **ACTIVE** (Green)
- System is live and responding to gestures
- Can trigger actions (with cooldown)
- Instant deactivation by showing Fist

---

## 🎓 What Makes This Project Special

### **1. Production Quality**
Clean modular architecture with proper separation of concerns - not a single messy script.

### **2. Safety Mechanisms**
Multiple layers prevent accidental triggers - better than most gesture control systems.

### **3. Two-Hand Support**
Simultaneous control with both hands, with intelligent conflict resolution.

### **4. Visual Feedback**
Rich on-screen information - always know what's happening.

### **5. Easy Configuration**
JSON-based settings allow customization without programming knowledge.

### **6. Performance Optimized**
Runs smoothly at 30 FPS while doing complex AI hand tracking.

### **7. Comprehensive Documentation**
Extensive docs for users, developers, and each development phase.

---

## 🚀 Future Possibilities

While not currently implemented, the modular architecture makes these additions straightforward:

- **Dynamic Gestures**: Swipes, circles, movement-based gestures
- **Custom Actions**: User-defined gesture mappings
- **Multi-Computer Control**: Network-based control
- **Gesture Recording**: Save and replay gesture sequences
- **Machine Learning**: Train custom gesture recognition
- **Voice Integration**: Combine gestures with voice commands
- **3D Tracking**: Depth-based gesture recognition

---

## 📝 Quick Reference

| Component | Location | Role |
|-----------|----------|------|
| **main.py** | Root | Orchestrates everything |
| **Camera** | core/camera.py | Webcam management |
| **HandTracker** | core/hand_tracking.py | Hand detection |
| **GestureClassifier** | core/gesture_classifier.py | Pattern recognition |
| **ActivationManager** | engine/activation_manager.py | Safety gatekeeper |
| **DecisionEngine** | engine/decision_engine.py | Action mapping |
| **ActionExecutor** | engine/action_executor.py | System control |
| **FPSCounter** | utils/fps_counter.py | Performance monitoring |
| **Config** | utils/config.py | Settings management |
| **gesture_map.json** | config/ | Gesture-to-action mappings |
| ★ **MainWindow** | ui/main_window.py | Dashboard shell |
| ★ **Sidebar** | ui/sidebar.py | Collapsible navigation |
| ★ **VisionPanel** | ui/vision_panel.py | Live camera card |
| ★ **StatusPanel** | ui/status_panel.py | System/Mode/Perf cards |
| ★ **ActivityTimeline** | ui/activity_timeline.py | Scrollable log bar |
| ★ **StateManager** | ui/state_manager.py | Observable shared state |
| ★ **MMGIWorkerThread** | ui/mmgi_thread.py | Core ↔ UI bridge |
| ★ **SimulatorThread** | ui/simulator.py | Fake-data demo thread |
| ★ **styles.py** | ui/styles.py | Full QSS dark theme |
| ★ **run_ui.py** | Root | Dashboard entry point |

---

## 🎯 Summary

MMGI is a **complete gesture recognition system** that transforms hand movements into computer actions. It combines:
- **AI-powered hand tracking** (MediaPipe)
- **Safety mechanisms** (activation, stability, cooldown)
- **Modular architecture** (easy to maintain and extend)
- **Rich visual feedback** (always know what's happening)
- **Two-hand support** (independent left/right control)
- **Production quality** (proper error handling, cleanup, configuration)
- **Premium AI Dashboard** (Phase 7 — professional PyQt6 interface)

---

## 🖥️ Phase 7 — Premium PyQt6 Dashboard Architecture

### Overview

Phase 7 adds a full professional desktop interface built with PyQt6.  
The UI lives entirely in the `ui/` package and **never touches gesture-detection logic directly**.

```
Data flow:
  Camera → HandTracker → GestureClassifier → ActivationManager
                ↓
          MMGIWorkerThread   ←── background QThread
                ↓  (Qt signals — thread-safe)
          StateManager       ←── central observable state
                ↓  (state_updated signal)
   VisionPanel │ StatusPanel │ ActivityTimeline │ HeaderBar
```

### ui/state_manager.py — The Shared Brain

A `QObject` that holds **all live runtime data**:

| Field | Type | Description |
|-------|------|-------------|
| `current_gesture` | str | Name of the detected gesture |
| `confidence` | float 0–1 | Stability fraction |
| `system_status` | str | INACTIVE / ACTIVATING / ACTIVE |
| `mode` | str | Current operating mode label |
| `latency_ms` | float | Per-frame processing time |
| `fps` | float | Rolling average frames-per-second |
| `accuracy_pct` | float | Detection accuracy percentage |
| `stability_pct` | float | Gesture stability 0–100 |
| `log_events` | list[LogEvent] | History of executed actions |

All UI panels connect to `state_updated` signal — one signal drives the entire dashboard refresh.

### ui/main_window.py — Dashboard Shell

`MainWindow` is the top-level `QMainWindow`.  It:
- Creates and owns the `StateManager`
- Starts either `MMGIWorkerThread` (real camera) or `SimulatorThread` (demo)
- Wires all signals to their respective panels
- Handles clean shutdown via `closeEvent`

### ui/sidebar.py — Animated Navigation

Collapsible left panel with 5 nav sections.
- Expands to 200 px / collapses to 60 px via `QPropertyAnimation`
- Each `NavButton` highlights on hover and shows a left-border accent when selected
- Tooltip shown for each button when collapsed

### ui/vision_panel.py — Live Camera Card

Centre panel showing the real-time annotated camera feed:
- `StatusDot` — pulsing `QPainter`-drawn dot driven by a 25 fps `QTimer`
- `OverlayBar` — semi-transparent bar pinned to the bottom of the feed showing: Gesture / Confidence / Mode / Status
- `QProgressBar` (stabilityBar) at the bottom of the card
- Glowing neon border (`QGraphicsDropShadowEffect`) when system is `ACTIVE`
- `update_frame(QImage)` slot receives camera frames from the worker thread

### ui/status_panel.py — Right Status Cards

Three stacked `QFrame` cards (260 px fixed width):
- **SystemCard** — status badge (colour-coded), latency metric, cooldown progress bar
- **ModeCard** — current mode with gesture→action mini-map preview
- **PerformanceCard** — FPS / Accuracy / Execution Rate each with a mini progress bar

### ui/activity_timeline.py — Log Feed

Fixed-height (70 px) horizontal scroll area at the bottom:
- Each `LogPill` widget fades in via `QGraphicsOpacityEffect` + `QPropertyAnimation`
- Pills glow with neon border on hover
- Auto-scrolls to the latest entry
- Capped at 60 pills to avoid memory growth

### ui/mmgi_thread.py — Real Pipeline Bridge

`QThread` subclass that runs the full MMGI pipeline (Camera → HandTracker → GestureClassifier → ActivationManager → DecisionEngine → ActionExecutor) without blocking the UI.  
Emits `frame_ready`, `state_changed`, `log_event` signals.

### ui/simulator.py — Demo Mode

`SimulatorThread` generates synthetic camera frames and state data at ~30 fps using `QPainter` — no hardware needed.  
Start the dashboard with `python run_ui.py --simulate`.

### ui/styles.py — QSS Stylesheet

Single source of truth for all colours and widget styles:
- Background deep: `#0F0F14`
- Card surface: `#1A1A22`
- Neon accent: `#00E5FF`
- Active green: `#00FF88`
- Inactive red: `#FF4466`
- 15 px rounded corners, Segoe UI font, smooth scrollbars

The result is a **safe, reliable, and performant** system that gives you touchless control over your Windows computer using nothing but hand gestures captured through your webcam.

---

*This document explains WHAT each component does without showing code implementation. For technical details and code, refer to the source files and ARCHITECTURE.md.*
