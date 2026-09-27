"""Render settled gazes for version 2 and one frame of version 1."""

from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import pygame

from mouse_gaze.factory import create_character


def render(version: str, gazes: list[tuple[str, float, float]], folder: Path) -> None:
    os.environ["MOUSE_GAZE_VERSION"] = version
    pygame.display.init()
    screen = pygame.display.set_mode((1280, 720))
    character = create_character(screen.get_size())
    try:
        for name, gaze_x, gaze_y in gazes:
            for _ in range(90):
                character.update(gaze_x, gaze_y, 1 / 60)
            character.draw(screen)
            pygame.image.save(screen, folder / f"{version}-{name}.png")
            print(version, name, "anchor", tuple(round(v) for v in character.rest_anchor()))
    finally:
        pygame.quit()


def main() -> None:
    folder = Path(os.environ["TEMP"])
    render("v2", [("center", 0, 0), ("right", 1, 0), ("left", -1, 0), ("up", 0, -1), ("down", 0, 1)], folder)
    render("v1", [("center", 0, 0)], folder)
    print("wrote", folder)


if __name__ == "__main__":
    main()
