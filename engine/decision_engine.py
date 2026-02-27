"""
engine/decision_engine.py - The Strategy Planner

Loads gesture-to-action mappings from config/gesture_map.json and
resolves which computer action should be executed for a given gesture
and handedness.

Default mapping
---------------
Right hand  (app & media navigation):
    One Finger    → open_brave
    Two Fingers   → open_spotify
    Ring and Pinky→ next_track
    Pinky         → prev_track

Left hand  (audio & playback):
    One Finger    → volume_up
    Two Fingers   → volume_down
    Three Fingers → mute
    Pinky         → play_pause

Single-hand fallback: the detected hand uses its own map.
"""

import json
from pathlib import Path


class DecisionEngine:
    """Maps gestures + handedness to action strings."""

    # Built-in defaults (used if gesture_map.json is missing or incomplete)
    _DEFAULT_RIGHT: dict[str, str] = {
        'One Finger':     'open_brave',
        'Two Fingers':    'open_apple_music',
        'Ring and Pinky': 'next_track',
        'Pinky':          'prev_track',
    }

    _DEFAULT_LEFT: dict[str, str] = {
        'One Finger':     'volume_up',
        'Two Fingers':    'volume_down',
        'Three Fingers':  'mute',
        'Pinky':          'play_pause',
    }

    def __init__(self, config_path: str | Path | None = None):
        self._right_map: dict[str, str] = dict(self._DEFAULT_RIGHT)
        self._left_map:  dict[str, str] = dict(self._DEFAULT_LEFT)

        # Resolve config path relative to project root
        if config_path is None:
            config_path = Path(__file__).parent.parent / 'config' / 'gesture_map.json'

        self._load_map(Path(config_path))

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_action(self, gesture: str, handedness: str = 'right') -> str | None:
        """
        Return the action string for the given gesture and hand.

        Args:
            gesture:    Recognised gesture name (e.g. 'One Finger')
            handedness: 'right' or 'left'

        Returns:
            Action string (e.g. 'volume_up') or None if no mapping exists.
        """
        if handedness == 'right':
            return self._right_map.get(gesture)
        else:
            return self._left_map.get(gesture)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load_map(self, path: Path) -> None:
        """Merge mappings from gesture_map.json, overriding defaults."""
        try:
            with open(path, 'r', encoding='utf-8') as fh:
                data: dict = json.load(fh)

            if 'right' in data:
                self._right_map.update(data['right'])
            if 'left' in data:
                self._left_map.update(data['left'])

            print(f'[DecisionEngine] Loaded gesture map from {path}')
        except FileNotFoundError:
            print(f'[DecisionEngine] gesture_map.json not found at {path} — using defaults')
        except (json.JSONDecodeError, KeyError) as exc:
            print(f'[DecisionEngine] Warning: could not parse gesture map: {exc} — using defaults')
        except Exception as exc:
            print(f'[DecisionEngine] Warning: {exc} — using defaults')
