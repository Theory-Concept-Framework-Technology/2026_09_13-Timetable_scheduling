"""Pick the procedural girl, or a custom image character when one is configured."""

from __future__ import annotations

from mouse_gaze.character import Character
from mouse_gaze.image_character import ASSETS_DIR, CONFIG_NAME


def create_character(window_size: tuple[int, int]) -> Character:
    config = ASSETS_DIR / CONFIG_NAME
    if config.is_file():
        from mouse_gaze.image_character import ImageCharacter

        return ImageCharacter(ASSETS_DIR, window_size)
    from mouse_gaze.girl import GirlCharacter

    return GirlCharacter(window_size)
