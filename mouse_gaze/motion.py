"""Turns a raw gaze target into a smooth eye and head pose."""

from __future__ import annotations

import math
from dataclasses import dataclass

from mouse_gaze.smoothing import Smooth2D, clamp

# Eyes lead. The head uses a softer spring so it arrives a little later.
EYE_STIFFNESS = 420.0
EYE_DAMPING = 32.0
HEAD_STIFFNESS = 78.0
HEAD_DAMPING = 14.5

DEFAULT_MAX_HEAD_DEG = 10.0
DEFAULT_HEAD_SHIFT = (13.0, 8.0)
# Spring output may pass the target briefly. Pixel offsets are scaled so that
# this much overshoot still lands inside the eye.
OVERSHOOT = 1.08


@dataclass(frozen=True)
class GazePose:
    """Smoothed look direction and the head motion derived from it.

    `eye_x` / `eye_y` and `head_x` / `head_y` are about -1..1.
    +x is toward the right of the screen, +y is toward the bottom.
    """

    eye_x: float
    eye_y: float
    head_x: float
    head_y: float
    angle_deg: float
    shift_x: float
    shift_y: float


class GazeMotion:
    """Shared eye/head motor so a replacement character can keep the same feel."""

    def __init__(
        self,
        max_head_degrees: float = DEFAULT_MAX_HEAD_DEG,
        head_shift: tuple[float, float] = DEFAULT_HEAD_SHIFT,
    ) -> None:
        self.eyes = Smooth2D(EYE_STIFFNESS, EYE_DAMPING)
        self.head = Smooth2D(HEAD_STIFFNESS, HEAD_DAMPING)
        self.max_head_degrees = max_head_degrees
        self.head_shift = head_shift

    def update(self, gaze_x: float, gaze_y: float, dt: float) -> GazePose:
        gx = clamp(gaze_x, -1.0, 1.0)
        gy = clamp(gaze_y, -1.0, 1.0)
        eye_x, eye_y = self.eyes.toward(gx, gy, dt)
        head_x, head_y = self.head.toward(gx, gy, dt)
        eye_x = clamp(eye_x, -OVERSHOOT, OVERSHOOT)
        eye_y = clamp(eye_y, -OVERSHOOT, OVERSHOOT)
        head_x = clamp(head_x, -OVERSHOOT, OVERSHOOT)
        head_y = clamp(head_y, -OVERSHOOT, OVERSHOOT)
        # Positive x looks right. Pygame angles are counterclockwise, so the
        # head turns the other way to lean toward that side.
        angle = -head_x * self.max_head_degrees
        shift_x = head_x * self.head_shift[0]
        shift_y = head_y * self.head_shift[1]
        return GazePose(eye_x, eye_y, head_x, head_y, angle, shift_x, shift_y)


def breathe_offset(time: float, amplitude: float = 2.2, speed: float = 1.7) -> float:
    return math.sin(time * speed) * amplitude
