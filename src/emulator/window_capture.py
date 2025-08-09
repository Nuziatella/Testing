import time
from typing import Optional, Tuple
import numpy as np
import cv2
import win32gui
import win32api
import win32con

try:
    import dxcam
    HAS_DXCAM = True
except Exception:
    HAS_DXCAM = False

try:
    import mss
    HAS_MSS = True
except Exception:
    HAS_MSS = False

def get_window_rect(hwnd: int) -> Tuple[int, int, int, int]:
    """Get the client area rectangle of a window in screen coordinates."""
    rect = win32gui.GetClientRect(hwnd)
    left, top = win32gui.ClientToScreen(hwnd, (rect[0], rect[1]))
    right, bottom = win32gui.ClientToScreen(hwnd, (rect[2], rect[3]))
    return left, top, right, bottom

def get_top_screen_rect(hwnd: int) -> Tuple[int, int, int, int]:
    """Get the region of the top screen (assumes two 256x192 screens stacked vertically)."""
    l, t, r, b = get_window_rect(hwnd)
    width = r - l
    height = b - t
    target_w, target_h = 256, 192
    # If client height roughly 2*192, split
    if height >= 2 * target_h - 10:
        return l, t, r, t + height // 2
    # Otherwise, try extract 256x192 centered at top area
    x = l + max(0, (width - target_w) // 2)
    y = t + 0
    return x, y, x + target_w, y + target_h

class WindowCapturer:
    """Captures the top screen of the emulator window."""
    def __init__(self, hwnd: int, use_dxcam: bool = True, target_size: Tuple[int, int] = (84, 84)):
        self.hwnd = hwnd
        self.target_size = target_size
        self.use_dxcam = use_dxcam and HAS_DXCAM
        self.dx = None
        self.mss_inst = None
        self.region = self._calc_region()
        if self.use_dxcam:
            self.dx = dxcam.create()
        elif HAS_MSS:
            self.mss_inst = mss.mss()
        else:
            raise RuntimeError("Neither dxcam nor mss is available for capture")

    def _calc_region(self):
        l, t, r, b = get_top_screen_rect(self.hwnd)
        return (l, t, r, b)

    def update_region(self):
        self.region = self._calc_region()

    def capture(self) -> np.ndarray:
        """Capture and preprocess the top screen region."""
        l, t, r, b = self.region
        frame = None
        if self.use_dxcam:
            frame = self.dx.grab(region=(l, t, r, b))
        else:
            frame = np.array(self.mss_inst.grab({"left": l, "top": t, "width": r - l, "height": b - t}))
            frame = frame[:, :, :3]  # drop alpha
        if frame is None:
            # Retry once after short delay
            time.sleep(0.01)
            l, t, r, b = self._calc_region()
            if self.use_dxcam:
                frame = self.dx.grab(region=(l, t, r, b))
            else:
                frame = np.array(self.mss_inst.grab({"left": l, "top": t, "width": r - l, "height": b - t}))
                frame = frame[:, :, :3]
            if frame is None:
                raise RuntimeError("Failed to capture frame from window")
        # Convert BGRA/BGR to grayscale, resize to target
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        resized = cv2.resize(gray, self.target_size, interpolation=cv2.INTER_AREA)
        # Normalize to [0,1]
        norm = resized.astype(np.float32) / 255.0
        return norm