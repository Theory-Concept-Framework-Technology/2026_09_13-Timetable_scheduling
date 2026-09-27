"""Continuous mouse tracking and gaze direction from a face anchor."""

from __future__ import annotations

import ctypes
import math
import sys

import pygame

from mouse_gaze.smoothing import clamp, exp_smooth

# Distance at which a look reaches its full extent. Closer cursors glance part-way.
GAZE_REACH_PX = 340.0
# Extra look added from cursor speed, as a fraction of full gaze, so a fast
# swipe leads the eyes slightly before the head catches up.
LEAD_SPEED = 4500.0
LEAD_LIMIT = 0.12
VELOCITY_TAU = 0.06
NEAR_FACE_PX = 56.0

_SECTORS = (
    "right",
    "down-right",
    "down",
    "down-left",
    "left",
    "up-left",
    "up",
    "up-right",
)


class _POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]


_USER32 = None


def _user32():
    global _USER32
    if _USER32 is None:
        library = ctypes.windll.user32
        library.GetCursorPos.argtypes = [ctypes.POINTER(_POINT)]
        library.GetCursorPos.restype = ctypes.c_int
        library.ClientToScreen.argtypes = [ctypes.c_void_p, ctypes.POINTER(_POINT)]
        library.ClientToScreen.restype = ctypes.c_int
        _USER32 = library
    return _USER32


def read_screen_cursor() -> tuple[int, int] | None:
    """OS cursor position in screen pixels. Windows only; other platforms return None."""
    if sys.platform != "win32":
        return None
    point = _POINT()
    if not _user32().GetCursorPos(ctypes.byref(point)):
        return None
    return int(point.x), int(point.y)


def _client_origin() -> tuple[int, int] | None:
    if sys.platform != "win32":
        return None
    try:
        hwnd = pygame.display.get_wm_info().get("window")
    except pygame.error:
        return None
    if not hwnd:
        return None
    point = _POINT()
    if not _user32().ClientToScreen(hwnd, ctypes.byref(point)):
        return None
    return int(point.x), int(point.y)


class MouseTracker:
    """Tracks the cursor across the screen and converts it to a gaze target.

    On Windows the cursor is read from the OS, so the character keeps following
    when the pointer leaves the window. While the window is focused, pygame's
    position is used and a scale factor is learned so the two coordinate spaces
    still match on scaled displays.
    """

    def __init__(self) -> None:
        self.x = 0.0
        self.y = 0.0
        self.screen_x = 0.0
        self.screen_y = 0.0
        self.has_screen = False
        self.vx = 0.0
        self.vy = 0.0
        self._has_sample = False
        self._sx = 1.0
        self._sy = 1.0

    def update(self, dt: float) -> None:
        screen = read_screen_cursor()
        if screen is not None:
            self.screen_x, self.screen_y = screen
            self.has_screen = True
        x, y = self._window_position(screen)
        if self._has_sample and dt > 0.0:
            instant_vx = (x - self.x) / dt
            instant_vy = (y - self.y) / dt
            self.vx = exp_smooth(self.vx, instant_vx, dt, VELOCITY_TAU)
            self.vy = exp_smooth(self.vy, instant_vy, dt, VELOCITY_TAU)
        else:
            self.vx = 0.0
            self.vy = 0.0
        self.x = x
        self.y = y
        self._has_sample = True

    def direction_from(self, anchor: tuple[float, float]) -> tuple[float, float]:
        """Unit vector from the face anchor toward the cursor. (0, 0) when overlapping."""
        dx = self.x - anchor[0]
        dy = self.y - anchor[1]
        dist = math.hypot(dx, dy)
        if dist < 1.0:
            return 0.0, 0.0
        return dx / dist, dy / dist

    def gaze_toward(self, anchor: tuple[float, float]) -> tuple[float, float]:
        """Look target in about -1..1. Full deflection is reached at `GAZE_REACH_PX`."""
        dx = self.x - anchor[0]
        dy = self.y - anchor[1]
        dist = math.hypot(dx, dy)
        if dist < 1.0:
            gx, gy = 0.0, 0.0
        else:
            strength = min(1.0, dist / GAZE_REACH_PX)
            gx = dx / dist * strength
            gy = dy / dist * strength
        gx = clamp(gx + clamp(self.vx / LEAD_SPEED, -LEAD_LIMIT, LEAD_LIMIT), -1.0, 1.0)
        gy = clamp(gy + clamp(self.vy / LEAD_SPEED, -LEAD_LIMIT, LEAD_LIMIT), -1.0, 1.0)
        return gx, gy

    def pointing_label(self, anchor: tuple[float, float]) -> str:
        dx = self.x - anchor[0]
        dy = self.y - anchor[1]
        if math.hypot(dx, dy) < NEAR_FACE_PX:
            return "toward you"
        sector = int(round(math.degrees(math.atan2(dy, dx)) / 45.0)) % 8
        return _SECTORS[sector]

    def cursor_text(self) -> str:
        if self.has_screen:
            return f"Cursor {int(round(self.screen_x))}, {int(round(self.screen_y))}"
        return f"Cursor {int(round(self.x))}, {int(round(self.y))}"

    def _window_position(self, screen: tuple[int, int] | None) -> tuple[float, float]:
        local = pygame.mouse.get_pos()
        origin = _client_origin()
        if screen is None or origin is None:
            return float(local[0]), float(local[1])
        pred_x = float(screen[0] - origin[0])
        pred_y = float(screen[1] - origin[1])
        if pygame.mouse.get_focused():
            self._calibrate(local, pred_x, pred_y)
            return float(local[0]), float(local[1])
        return pred_x * self._sx, pred_y * self._sy

    def _calibrate(self, local: tuple[int, int], pred_x: float, pred_y: float) -> None:
        if abs(pred_x) > 40.0 and abs(local[0]) > 40:
            ratio = local[0] / pred_x
            if 0.5 <= ratio <= 2.5:
                self._sx += (ratio - self._sx) * 0.15
        if abs(pred_y) > 40.0 and abs(local[1]) > 40:
            ratio = local[1] / pred_y
            if 0.5 <= ratio <= 2.5:
                self._sy += (ratio - self._sy) * 0.15
