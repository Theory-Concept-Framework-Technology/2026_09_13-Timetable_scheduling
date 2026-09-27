"""Frame-rate independent smoothing used by gaze motion."""

from __future__ import annotations

import math


def clamp(value: float, low: float, high: float) -> float:
    if value < low:
        return low
    if value > high:
        return high
    return value


def exp_smooth(current: float, target: float, dt: float, tau: float) -> float:
    """Move `current` toward `target`. `tau` is the time constant in seconds."""
    if tau <= 0.0 or dt <= 0.0:
        return target
    weight = 1.0 - math.exp(-dt / tau)
    return current + (target - current) * weight


def spring_step(
    value: float,
    velocity: float,
    target: float,
    dt: float,
    stiffness: float,
    damping: float,
) -> tuple[float, float]:
    """One semi-implicit step of a damped spring. Slightly underdamped by design."""
    acceleration = -stiffness * (value - target) - damping * velocity
    velocity = velocity + acceleration * dt
    value = value + velocity * dt
    return value, velocity


class Smooth2D:
    """Two-axis spring. Higher stiffness follows faster; damping below critical adds a little overshoot."""

    def __init__(self, stiffness: float, damping: float) -> None:
        self.x = 0.0
        self.y = 0.0
        self.vx = 0.0
        self.vy = 0.0
        self.stiffness = stiffness
        self.damping = damping

    def toward(self, target_x: float, target_y: float, dt: float) -> tuple[float, float]:
        dt = clamp(dt, 0.0, 0.05)
        if dt == 0.0:
            return self.x, self.y
        step = 1.0 / 120.0
        steps = max(1, math.ceil(dt / step))
        h = dt / steps
        for _ in range(steps):
            self.x, self.vx = spring_step(self.x, self.vx, target_x, h, self.stiffness, self.damping)
            self.y, self.vy = spring_step(self.y, self.vy, target_y, h, self.stiffness, self.damping)
            self.vx = clamp(self.vx, -12.0, 12.0)
            self.vy = clamp(self.vy, -12.0, 12.0)
        return self.x, self.y
