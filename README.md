# MMGI — Multi-Modal Gesture Intelligence

> **Smart Mode AI Dashboard** — touch-free gesture control with a production-grade PyQt6 interface.

A real-time hand-gesture recognition system powered by MediaPipe AI that maps hand gestures
to system actions through an intelligent 3-mode switching architecture — all visualised in a
premium dark-theme PyQt6 dashboard.

---

## ✨ Highlights

| Feature | Details |
|---|---|
| **Smart Mode System** | 3 context modes: App / Media / System, switched by 1-second finger holds |
| **Live AI Dashboard** | Dark-theme PyQt6 UI with live camera feed, stability bar, activity log |
| **Zero Latency** | QThread pipeline — UI never blocks camera processing |
| **Reactive State** | `SharedState` (PyQt6 signals) decouples UI from pipeline completely |
| **Headless fallback** | `--headless` flag preserves original OpenCV window mode |

---

## 🎛️ Smart Mode System

Mode switching is triggered by holding **Three Fingers** for **1 second** (10-frame stability + 1.5 s cooldown). Each hold cycles to the next mode:  **App → Media → System → App**

| Gesture | Hold | Effect |
|---|---|---|
| 🤟 Three Fingers | 1 s | Cycle to next mode |

### App Mode Actions
| Gesture | Action |
|---|---|
| ☝️ One Finger | Open Browser (Brave) |
| ✌️ Two Fingers | Open Music (Apple Music) |
| 💍 Ring + Pinky | Next Track |
| 🤙 Pinky | Previous Track |

### Media Mode Actions
| Gesture | Action |
|---|---|
| 💍 Ring + Pinky | Next Track |
| 🤙 Pinky | Previous Track |
| 👍 Thumbs Up | Play / Pause |
| ✌️ Two Fingers | Volume Up |

### System Mode Actions
| Gesture | Action |
|---|---|
| 👍 Thumbs Up | Volume Up |
| 🤙 Pinky | Volume Down |
| 💍 Ring + Pinky | Mute |

---

## 🖥️ UI Layout

```
┌────────────────────────────────────────────────────────────┐
│  ◉ MMGI    Smart Mode AI Controller       APP MODE  ⬤ ACTIVE│
├──────────┬─────────────────────────────┬────────────────────┤
│ Sidebar  │   Live Vision Feed          │  System Panel      │
│  Vision  │   Hand skeleton overlay     │  ─ System ON/OFF   │
│  Mode    │   Gesture label             │  ─ Mode + gestures │
│ (220 px) │   Mode-switch progress bar  │  ─ FPS / Latency   │
├──────────┴─────────────────────────────┴────────────────────┤
│  Activity Log – scrollable horizontal pill timeline         │
└────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Obtain the MediaPipe model
Download `hand_landmarker.task` and place it in the project root:
```
https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task
```

### 3. Run

**Dashboard (default):**
```bash
python main.py
```

**Headless OpenCV mode:**
```bash
python main.py --headless
```

---

## 📁 Project Structure

```
MMGI/
├── main.py                   # Entry point — dashboard or headless
├── shared_state.py           # Reactive state store (PyQt6 signals)
├── worker_thread.py          # QThread gesture pipeline
├── requirements.txt
│
├── config/
│   └── gesture_map.json      # Smart Mode gesture→action mappings
│
├── core/
│   ├── camera.py             # Webcam capture
│   ├── hand_tracking.py      # MediaPipe HandLandmarker
│   └── gesture_classifier.py # Rule-based gesture classifier
│
├── engine/
│   ├── activation_manager.py # Safety gate (Open Palm hold to activate)
│   ├── decision_engine.py    # Smart Mode action resolver
│   └── action_executor.py    # pyautogui system action execution
│
├── ui/
│   ├── main_window.py        # Top-level QMainWindow
│   ├── sidebar.py            # Collapsible Vision + Mode sidebar
│   ├── vision_panel.py       # Live feed + overlay + stability bar
│   ├── system_panel.py       # System / Mode / Performance cards
│   ├── activity_log.py       # Horizontal scrollable event timeline
│   └── styles.py             # QSS stylesheet + colour tokens
│
└── utils/
    ├── config.py             # Dot-key config loader
    └── fps_counter.py        # Rolling FPS counter
```

---

## ⚙️ Requirements

- Python 3.10+
- PyQt6 ≥ 6.7
- mediapipe ≥ 0.10.30
- opencv-python ≥ 4.10
- pyautogui ≥ 0.9.54
- numpy ≥ 2.3

---

## 🎮 Activation Protocol

1. Show **Open Palm** and hold for **2 seconds** → system activates (border turns green)
2. Show **Fist** → instant deactivation
3. Hold **Three Fingers** for 1 second → cycle to next mode (App→Media→System→App)
4. Use mode-specific gestures to trigger actions (1 s cooldown between actions)

---

## ⚖️ License

This project is for educational purposes.
