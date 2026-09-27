"""Interface every swappable character implements."""

from __future__ import annotations

from abc import ABC, abstractmethod

import pygame


class Character(ABC):
    """A figure drawn in the window whose eyes and head can follow a gaze target.

    Gaze is measured from `rest_anchor` (usually the midpoint of the eyes).
    `update` receives a direction in about -1..1 on each axis: +x is screen-right,
    +y is screen-down. Implementations should ease toward that target themselves
    so a new character can keep, or replace, the default spring in `GazeMotion`.
    """

    def on_resize(self, size: tuple[int, int]) -> None:
        """Rebuild artwork after the window size changes."""

    @abstractmethod
    def rest_anchor(self) -> tuple[float, float]:
        """Face/eye reference point in window pixels, before head lean."""

    @abstractmethod
    def update(self, gaze_x: float, gaze_y: float, dt: float) -> None:
        """Store a new gaze target and advance smoothing by `dt` seconds."""

    @abstractmethod
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the character into the window surface."""
