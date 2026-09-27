"""Image-backed character loaded from assets/character.json."""

from __future__ import annotations

import json
from pathlib import Path

import pygame

from mouse_gaze.character import Character
from mouse_gaze.motion import OVERSHOOT, GazeMotion, breathe_offset
from mouse_gaze.render import blit_rotate
from mouse_gaze.smoothing import clamp

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
CONFIG_NAME = "character.json"


class ImageCharacter(Character):
    """Layered sprite character.

    Drop `character.json` plus the images it names into the assets folder.
    The procedural girl is used when that file is absent. See
    `assets/character.example.json` for the fields.
    """

    def __init__(self, assets: Path, window_size: tuple[int, int]) -> None:
        self._assets = assets
        self._config = _read_config(assets / CONFIG_NAME)
        self._body_source = _load_optional(assets, self._config.get("body"))
        self._head_source = _load_required(assets, str(self._config["head"]))
        pupil_name = self._config.get("pupil")
        self._pupil_source = _load_optional(assets, pupil_name if isinstance(pupil_name, str) else None)
        shift = self._config.get("head_shift", [13, 8])
        self.motion = GazeMotion(
            max_head_degrees=float(self._config.get("max_head_degrees", 10)),
            head_shift=(float(shift[0]), float(shift[1])),
        )
        self.pose = self.motion.update(0.0, 0.0, 0.0)
        self._time = 0.0
        self._body: pygame.Surface | None = None
        self._head: pygame.Surface | None = None
        self._pupil: pygame.Surface | None = None
        self._body_pos = (0, 0)
        self._anchor = (0.0, 0.0)
        self._pivot_screen = (0.0, 0.0)
        self._pivot_local = (0.0, 0.0)
        self._eyes_local: list[tuple[float, float]] = []
        self._pupil_range = (8.0, 6.0)
        self._frame: pygame.Surface | None = None
        self.on_resize(window_size)

    def on_resize(self, size: tuple[int, int]) -> None:
        ref_w, ref_h = _pair(self._config["reference_size"], "reference_size")
        scale = min(size[0] / ref_w, size[1] / ref_h)
        offset_x = (size[0] - ref_w * scale) / 2.0
        offset_y = (size[1] - ref_h * scale) / 2.0

        def place(point: list[float] | tuple[float, float]) -> tuple[float, float]:
            x, y = _pair(point, "point")
            return offset_x + x * scale, offset_y + y * scale

        self._anchor = place(_pair(self._config["anchor"], "anchor"))
        self._pivot_screen = place(_pair(self._config["head_pos"], "head_pos"))
        if self._body_source is not None:
            body_pos = _pair(self._config.get("body_pos", [0, 0]), "body_pos")
            self._body = _scale(self._body_source, scale)
            self._body_pos = (round(offset_x + body_pos[0] * scale), round(offset_y + body_pos[1] * scale))
        else:
            self._body = None
        self._head = _scale(self._head_source, scale)
        pivot = _pair(self._config["head_pivot"], "head_pivot")
        self._pivot_local = (pivot[0] * scale, pivot[1] * scale)
        self._eyes_local = [(_pair(eye, "eyes")[0] * scale, _pair(eye, "eyes")[1] * scale) for eye in self._config["eyes"]]
        travel = _pair(self._config.get("pupil_range", [12, 8]), "pupil_range")
        self._pupil_range = (travel[0] * scale, travel[1] * scale)
        self._pupil = _scale(self._pupil_source, scale) if self._pupil_source is not None else None
        assert self._head is not None
        self._frame = pygame.Surface(self._head.get_size(), pygame.SRCALPHA)

    def rest_anchor(self) -> tuple[float, float]:
        return self._anchor

    def update(self, gaze_x: float, gaze_y: float, dt: float) -> None:
        self._time += dt
        self.pose = self.motion.update(gaze_x, gaze_y, dt)

    def draw(self, surface: pygame.Surface) -> None:
        assert self._head is not None and self._frame is not None
        breathe = breathe_offset(self._time)
        if self._body is not None:
            surface.blit(self._body, (self._body_pos[0], self._body_pos[1] + round(breathe)))
        frame = self._frame
        frame.fill((0, 0, 0, 0))
        frame.blit(self._head, (0, 0))
        ox = clamp(self.pose.eye_x, -OVERSHOOT, OVERSHOOT) * self._pupil_range[0]
        oy = clamp(self.pose.eye_y, -OVERSHOOT, OVERSHOOT) * self._pupil_range[1]
        for eye_x, eye_y in self._eyes_local:
            self._draw_pupil(frame, eye_x + ox, eye_y + oy)
        pivot = (self._pivot_screen[0] + self.pose.shift_x, self._pivot_screen[1] + self.pose.shift_y + breathe)
        blit_rotate(surface, frame, pivot, self._pivot_local, self.pose.angle_deg)

    def _draw_pupil(self, surface: pygame.Surface, x: float, y: float) -> None:
        if self._pupil is not None:
            rect = self._pupil.get_rect(center=(round(x), round(y)))
            surface.blit(self._pupil, rect)
            return
        radius = max(2, round(min(self._pupil_range) * 0.45))
        pygame.draw.circle(surface, (24, 16, 16), (round(x), round(y)), radius)


def _read_config(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path} is not valid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    for key in ("reference_size", "anchor", "head", "head_pivot", "head_pos", "eyes"):
        if key not in data:
            raise ValueError(f"{path} is missing '{key}'")
    if not isinstance(data["eyes"], list) or len(data["eyes"]) < 1:
        raise ValueError(f"{path} needs an 'eyes' list with one [x, y] pair per eye")
    return data


def _pair(value: object, label: str) -> tuple[float, float]:
    if not isinstance(value, (list, tuple)) or len(value) != 2:
        raise ValueError(f"'{label}' must be a pair of numbers")
    return float(value[0]), float(value[1])


def _load_required(assets: Path, name: str) -> pygame.Surface:
    path = assets / name
    if not path.is_file():
        raise ValueError(f"Missing character image: {path}")
    try:
        return pygame.image.load(path).convert_alpha()
    except pygame.error as exc:
        raise ValueError(f"Could not load {path}: {exc}") from exc


def _load_optional(assets: Path, name: object) -> pygame.Surface | None:
    if not isinstance(name, str) or not name:
        return None
    path = assets / name
    if not path.is_file():
        raise ValueError(f"Missing character image: {path}")
    try:
        return pygame.image.load(path).convert_alpha()
    except pygame.error as exc:
        raise ValueError(f"Could not load {path}: {exc}") from exc


def _scale(image: pygame.Surface, scale: float) -> pygame.Surface:
    width = max(1, round(image.get_width() * scale))
    height = max(1, round(image.get_height() * scale))
    if (width, height) == image.get_size():
        return image
    return pygame.transform.smoothscale(image, (width, height))
