"""Pick the drawn character, or the layered version 2 sprites."""

from __future__ import annotations

import os

from mouse_gaze.character import Character
from mouse_gaze.image_character import ASSETS_DIR, CONFIG_NAME

V2_DIR = ASSETS_DIR / "v2"


def create_character(window_size: tuple[int, int]) -> Character:
    version = os.environ.get("MOUSE_GAZE_VERSION", "v2").strip().lower()
    config = V2_DIR / CONFIG_NAME
    if version != "v1" and config.is_file():
        from mouse_gaze.image_character import ImageCharacter

        return ImageCharacter(V2_DIR, window_size)
    from mouse_gaze.girl import GirlCharacter

    return GirlCharacter(window_size)
