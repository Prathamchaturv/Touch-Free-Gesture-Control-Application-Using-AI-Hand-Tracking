"""
core/camera.py - The Eyes

Opens and manages the laptop webcam. Captures video frames continuously
and provides them to the rest of the pipeline.
"""

import cv2


class Camera:
    """Manages webcam capture lifecycle."""

    def __init__(self, width: int = 1280, height: int = 720,
                 fps: int = 30, camera_index: int = 0):
        self._width = width
        self._height = height
        self._fps = fps
        self._index = camera_index
        self._cap: cv2.VideoCapture | None = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def open(self) -> bool:
        """Open the camera. Returns True on success, False otherwise."""
        self._cap = cv2.VideoCapture(self._index)
        if not self._cap.isOpened():
            print(f'[Camera] Could not open camera index {self._index}')
            return False

        # Request resolution and FPS
        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, self._width)
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self._height)
        self._cap.set(cv2.CAP_PROP_FPS, self._fps)

        # Report actual values (hardware may clamp them)
        actual_w = int(self._cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_h = int(self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        actual_fps = int(self._cap.get(cv2.CAP_PROP_FPS))
        print(f'Camera initialized: {actual_w}x{actual_h} @ {actual_fps}fps')
        return True

    def release(self) -> None:
        """Release the camera resource."""
        if self._cap is not None:
            self._cap.release()
            self._cap = None
            print('Camera released')

    # ------------------------------------------------------------------
    # Frame capture
    # ------------------------------------------------------------------

    def read_frame(self) -> tuple[bool, object]:
        """Read one frame. Returns (success, frame)."""
        if self._cap is None or not self._cap.isOpened():
            return False, None
        return self._cap.read()

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    def is_opened(self) -> bool:
        """True if the camera is currently open."""
        return self._cap is not None and self._cap.isOpened()

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height
