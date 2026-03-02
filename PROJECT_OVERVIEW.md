# MMGI Project Overview — Smart Mode AI Dashboard
## Architecture & Component Guide

This document explains what every file does in the MMGI project.

---

## 🎯 Project Purpose

MMGI converts hand gestures from a webcam into real system actions through a 3-mode Smart Mode system, all visualised in a premium PyQt6 AI dashboard.

---

## 🗂 Component Map

```
main.py ─────────────────────────────────────────── Entry point
  ├── run_dashboard()  →  PyQt6 AI Dashboard (default)
  └── run_headless()   →  OpenCV terminal-only mode (--headless)

shared_state.py ─────── Reactive data store (PyQt6 signals)
worker_thread.py ───────QThread: full pipeline on background thread

ui/
  main_window.py ─────── Top-level QMainWindow, assembles all panels
  sidebar.py ─────────── Collapsible nav sidebar (Vision + Mode)
  vision_panel.py ─────── Live camera feed + gesture overlay + stability bar
  system_panel.py ─────── System card + Mode card + Performance card
  activity_log.py ─────── Horizontal scrollable pill event timeline
  styles.py ──────────── QSS stylesheet tokens (colours, cards, buttons)

core/
  camera.py ──────────── Webcam capture (OpenCV VideoCapture)
  hand_tracking.py ────── MediaPipe HandLandmarker Tasks API
  gesture_classifier.py ─ Rule-based finger-state → gesture name

engine/
  activation_manager.py ─ Safety gate (Open Palm hold to activate)
  decision_engine.py ───── Smart Mode action resolver + mode switching
  action_executor.py ────── pyautogui system action execution

config/
  gesture_map.json ─────── Mode-based gesture → action config

utils/
  config.py ──────────── Dot-key YAML-like config loader
  fps_counter.py ─────── Rolling-window FPS counter
```

---

## 🔁 Data Flow (per frame)

```
Camera.read_frame()
    │
    ▼
HandTracker.detect_hands()   ← MediaPipe AI inference
HandTracker.get_hands_info() ← Struct: {right, left, count}
    │
    ▼
GestureClassifier.classify(finger_states)
    → gesture name string  e.g. "Thumbs Up"
    │
    ▼
DecisionEngine.process(gesture)
    ├── is_mode_switch?  → update mode stability, commit after 1 s
    └── else             → get_action(gesture, mode)  → action string
    │
    ▼
ActivationManager.update(gesture)
    ├── Open Palm 2 s → ACTIVE
    ├── Fist          → INACTIVE
    └── returns should_execute: bool
    │
    ▼ (if should_execute and action)
ActionExecutor.execute(action)
    → pyautogui keyboard, subprocess, etc.
    │
    ▼
SharedState.set_*(...)   ← signals broadcast to all UI panels
WorkerThread.frame_ready.emit(QImage)
    │
    ▼
VisionPanel.update_frame()   ← UI repaints with annotated frame
```

---

## 🧩 Key Components

### `shared_state.py` — Reactive Store
Central `QObject` holding all live data (fps, mode, gesture, etc.).
Every field has a typed `pyqtSignal` that fires on change.
UI panels subscribe independently — zero coupling between pipeline and UI.

### `worker_thread.py` — QThread Pipeline
Runs the full MMGI pipeline on a background thread so the UI never freezes.
Emits `frame_ready(QImage)` and `error(str)`.
Calls `SharedState.set_*()` to push telemetry to connected UI widgets.

### `engine/decision_engine.py` — Smart Mode Engine
- Loads `config/gesture_map.json` — `mode_switch`, `App Mode`, `Media Mode`, `System Mode` sections
- `process(gesture)` → `(action | None, mode_changed_bool)`
- Mode switching: 10-frame stability + 1.0 s hold + 1.5 s cooldown
- Mode-switch gestures (1/2/3 fingers) are never forwarded as actions
- `mode_stability_progress` (0–1) drives the stability bar in VisionPanel

### `config/gesture_map.json` — Mode Mappings
```json
{
  "mode_switch":  {"One Finger":"App Mode", "Two Fingers":"Media Mode", "Three Fingers":"System Mode"},
  "App Mode":     {"Thumbs Up":"open_brave", "Ring and Pinky":"open_apple_music", "Pinky":"volume_up"},
  "Media Mode":   {"Ring and Pinky":"next_track", "Pinky":"prev_track", "Open Palm":"play_pause", "Thumbs Up":"volume_up"},
  "System Mode":  {"Thumbs Up":"volume_up", "Pinky":"volume_down", "Ring and Pinky":"mute"}
}
```

### `ui/main_window.py` — Dashboard Layout
```
Header (52 px)   ◉ MMGI  Smart Mode AI Controller        APP MODE  ⬤ INACTIVE
Body (stretch)   Sidebar (220 px) | Vision (flex) | System Panel (280 px)
Footer (76 px)   Activity Log — scrollable horizontal pill timeline
```

### `ui/vision_panel.py` — Live Feed
- Receives `QImage` from `WorkerThread.frame_ready` signal
- Scales image to fill label with aspect-ratio preserved
- Glow border changes colour with current mode / active state
- Mode-switch stability progress bar at the bottom

### `ui/system_panel.py` — Right Panel (3 cards)
- **SystemCard**: ON/OFF indicator badge + toggle button (visual feedback)
- **ModeCard**: current mode name + per-mode gesture → action instruction table; mode-switch reminder at bottom
- **PerformanceCard**: FPS, latency, volume bar, confidence bar — all live via SharedState signals

### `ui/activity_log.py` — Event Timeline
Horizontal scrollable strip of coloured pills.
Each pill: `● [HH:MM:SS]  CATEGORY  description`
Categories: ACTION (cyan), MODE (green), SYSTEM (grey), ERROR (red).
Auto-scrolls right on new events. Keeps max 200 events.

### `ui/sidebar.py` — Collapsible Navigation
220 px expanded / 56 px collapsed with animated width transition.
Tabs: Vision, Mode.
Collapse button with ◄/► arrow, smooth `QPropertyAnimation`.

### `ui/styles.py` — Qt Stylesheet
Global QSS injected at `QApplication` level.
Colour tokens: `BG_DEEP #0F0F14`, `BG_CARD #1A1A22`, `ACCENT #00E5FF`, `ACTIVE #00FF88`, `INACTIVE #FF4466`.

---

## ⚡ Activation Protocol

| Step | Gesture | Duration | Effect |
|------|---------|----------|--------|
| Activate | Open Palm | 2 seconds | System → ACTIVE (green) |
| Deactivate | Fist | Instant | System → INACTIVE |
| Switch Mode | 1/2/3 fingers | 1 second hold | App / Media / System mode |
| Execute Action | Any mode gesture | Instant (1 per 1 s cooldown) | Runs system action |

---

## 📦 Dependencies

| Package | Purpose |
|---------|---------|
| PyQt6 ≥ 6.7 | UI framework |
| mediapipe ≥ 0.10 | Hand AI model |
| opencv-python ≥ 4.10 | Camera capture + frame processing |
| pyautogui ≥ 0.9 | Keyboard / media key automation |
| numpy ≥ 2.3 | Array operations for MediaPipe |
