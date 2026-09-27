"""Headless draw check for Docker and Jenkins. Exits 0 when the app can render."""

from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import pygame

from mouse_gaze.factory import create_character
from mouse_gaze.smoothing import Smooth2D
from mouse_gaze.tracker import MouseTracker


def main() -> None:
    pygame.display.init()
    screen = pygame.display.set_mode((960, 720))
    try:
        _check_spring()
        character = create_character(screen.get_size())
        tracker = MouseTracker()
        for _ in range(8):
            tracker.update(1.0 / 60.0)
            gaze_x, gaze_y = tracker.gaze_toward(character.rest_anchor())
            character.update(gaze_x, gaze_y, 1.0 / 60.0)
            character.draw(screen)
        character.on_resize((800, 600))
        character.update(1.0, -0.4, 0.4)
        character.draw(screen)
    finally:
        pygame.quit()
    print("smoke ok")


def _check_spring() -> None:
    spring = Smooth2D(420.0, 32.0)
    x = y = 0.0
    for _ in range(120):
        x, y = spring.toward(1.0, -0.4, 1.0 / 60.0)
    if abs(x - 1.0) > 0.05 or abs(y + 0.4) > 0.05:
        raise SystemExit(f"gaze spring did not settle: {x:.3f}, {y:.3f}")


if __name__ == "__main__":
    main()
