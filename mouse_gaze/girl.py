"""Procedural portrait used until a custom character folder replaces it."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass

import pygame

from mouse_gaze.character import Character
from mouse_gaze.motion import OVERSHOOT, GazeMotion, breathe_offset
from mouse_gaze.render import Canvas, blit_rotate, downsample
from mouse_gaze.smoothing import clamp

# Proportions are fractions of the shorter window side (or of face_rx).
FACE_RX = 0.155
FACE_ASPECT = 1.16
EYE_SPACING = 0.40
EYE_RX = 0.23
EYE_RY = 0.19
IRIS_R = 0.088
PUPIL_R = 0.046
SUPERSAMPLE = 2

HAIR = (62, 42, 54)
HAIR_DEEP = (46, 30, 40)
HAIR_SHEEN = (124, 84, 98)
SKIN = (255, 220, 202)
SKIN_SHADOW = (232, 180, 160)
SKIN_DEEP = (214, 158, 144)
SKIN_LIGHT = (255, 234, 222)
LIP = (196, 102, 112)
LIP_DEEP = (164, 78, 90)
BLUSH = (228, 124, 122, 78)
SWEATER = (184, 92, 108)
SWEATER_DARK = (150, 68, 84)
COLLAR = (246, 236, 230)
EAR_INNER = (232, 170, 156)
IRIS = (112, 70, 48)
IRIS_DEEP = (68, 40, 30)
IRIS_LIGHT = (170, 114, 78)
PUPIL = (26, 16, 16)
SCLERA = (255, 250, 246)
SCLERA_SHADE = (236, 214, 210)
CATCHLIGHT = (255, 255, 255)
CLIP = (214, 176, 108)
BG_TOP = (246, 234, 226)
BG_BOTTOM = (228, 190, 180)
HALO = (255, 246, 240, 90)
SHADOW = (120, 72, 78, 48)


@dataclass(frozen=True)
class Layout:
    size: tuple[int, int]
    anchor: tuple[float, float]
    pivot: tuple[float, float]
    head_rect: pygame.Rect
    cx: float
    face_y: float
    face_rx: float
    face_ry: float
    eyes: tuple[tuple[float, float], tuple[float, float]]
    eye_rx: float
    eye_ry: float
    iris_r: float
    pupil_r: float


def compute_layout(size: tuple[int, int]) -> Layout:
    width, height = size
    short = max(1.0, float(min(width, height)))
    cx = width / 2.0
    face_rx = max(28.0, short * FACE_RX)
    face_ry = face_rx * FACE_ASPECT
    face_y = height * 0.40
    eye_rx = face_rx * EYE_RX
    eye_ry = face_rx * EYE_RY
    eye_dx = face_rx * EYE_SPACING
    eye_y = face_y - face_ry * 0.02
    eyes = ((cx - eye_dx, eye_y), (cx + eye_dx, eye_y))
    pivot = (cx, face_y + face_ry * 0.98)
    left = cx - face_rx * 1.72
    top = face_y - face_ry * 1.28
    rect_w = face_rx * 3.44
    rect_h = (pivot[1] - top) + face_ry * 0.42
    head_rect = pygame.Rect(round(left), round(top), max(1, round(rect_w)), max(1, round(rect_h)))
    anchor = ((eyes[0][0] + eyes[1][0]) / 2.0, (eyes[0][1] + eyes[1][1]) / 2.0)
    return Layout(
        size=(width, height),
        anchor=anchor,
        pivot=pivot,
        head_rect=head_rect,
        cx=cx,
        face_y=face_y,
        face_rx=face_rx,
        face_ry=face_ry,
        eyes=eyes,
        eye_rx=eye_rx,
        eye_ry=eye_ry,
        iris_r=face_rx * IRIS_R,
        pupil_r=face_rx * PUPIL_R,
    )


def _gradient(size: tuple[int, int], top: tuple[int, int, int], bottom: tuple[int, int, int]) -> pygame.Surface:
    width, height = size
    surface = pygame.Surface(size)
    if height <= 1:
        surface.fill(top)
        return surface
    for y in range(height):
        blend = y / (height - 1)
        color = tuple(int(a + (b - a) * blend) for a, b in zip(top, bottom))
        pygame.draw.line(surface, color, (0, y), (width, y))
    return surface


def _make_background(layout: Layout) -> pygame.Surface:
    surface = _gradient(layout.size, BG_TOP, BG_BOTTOM)
    canvas = Canvas(pygame.Surface(layout.size, pygame.SRCALPHA), 1)
    canvas.ellipse(HALO, layout.cx, layout.face_y - layout.face_ry * 0.1, layout.face_rx * 3.1, layout.face_ry * 2.6)
    canvas.ellipse((255, 236, 228, 50), layout.size[0] * 0.12, layout.size[1] * 0.16, layout.face_rx * 0.7, layout.face_rx * 0.7)
    canvas.ellipse((255, 228, 220, 40), layout.size[0] * 0.86, layout.size[1] * 0.22, layout.face_rx * 0.45, layout.face_rx * 0.45)
    surface.blit(canvas.surface, (0, 0))
    return surface


def _make_body(layout: Layout) -> pygame.Surface:
    width, height = layout.size
    big = pygame.Surface((width * SUPERSAMPLE, height * SUPERSAMPLE), pygame.SRCALPHA)
    canvas = Canvas(big, SUPERSAMPLE)
    cx = layout.cx
    face_rx = layout.face_rx
    face_ry = layout.face_ry
    face_y = layout.face_y
    pivot_y = layout.pivot[1]

    canvas.ellipse(HAIR_DEEP, cx, face_y - face_ry * 0.15, face_rx * 1.72, face_ry * 1.55)
    canvas.ellipse(HAIR, cx - face_rx * 0.95, face_y + face_ry * 0.85, face_rx * 0.62, face_ry * 1.35)
    canvas.ellipse(HAIR, cx + face_rx * 0.95, face_y + face_ry * 0.85, face_rx * 0.62, face_ry * 1.35)
    shoulder_y = pivot_y + face_ry * 0.55
    canvas.ellipse(SWEATER_DARK, cx - face_rx * 1.25, shoulder_y + face_ry * 0.35, face_rx * 0.62, face_ry * 0.95)
    canvas.ellipse(SWEATER_DARK, cx + face_rx * 1.25, shoulder_y + face_ry * 0.35, face_rx * 0.62, face_ry * 0.95)

    bottom = height - 2
    top = pivot_y + face_ry * 0.02
    half_top = face_rx * 0.78
    half_bottom = face_rx * 1.85
    canvas.polygon(
        SWEATER_DARK,
        [
            (cx - half_top - 8, top + 10),
            (cx + half_top + 8, top + 10),
            (cx + half_bottom, bottom),
            (cx - half_bottom, bottom),
        ],
    )
    canvas.polygon(
        SWEATER,
        [
            (cx - half_top, top),
            (cx + half_top, top),
            (cx + half_bottom - 10, bottom),
            (cx - half_bottom + 10, bottom),
        ],
    )
    canvas.ellipse(SKIN_SHADOW, cx, pivot_y + face_ry * 0.28, face_rx * 0.26, face_ry * 0.34)
    canvas.ellipse(SKIN, cx, pivot_y + face_ry * 0.24, face_rx * 0.22, face_ry * 0.30)
    collar_y = top + face_ry * 0.02
    canvas.polygon(
        COLLAR,
        [
            (cx - face_rx * 0.34, collar_y),
            (cx + face_rx * 0.34, collar_y),
            (cx + face_rx * 0.48, collar_y + face_ry * 0.16),
            (cx - face_rx * 0.48, collar_y + face_ry * 0.16),
        ],
    )
    canvas.ellipse(SHADOW, cx, height * 0.97, face_rx * 1.35, face_rx * 0.16)
    return downsample(big, layout.size)


def _draw_bangs(canvas: Canvas, cx: float, face_y: float, face_rx: float, face_ry: float) -> None:
    """Soft blunt fringe, then long side locks that meet it."""
    canvas.ellipse(HAIR_DEEP, cx, face_y - face_ry * 0.60, face_rx * 1.08, face_ry * 0.40)
    canvas.ellipse(HAIR, cx, face_y - face_ry * 0.66, face_rx * 1.02, face_ry * 0.34)
    canvas.ellipse(HAIR, cx, face_y - face_ry * 0.48, face_rx * 0.36, face_ry * 0.18)
    for side in (-1, 1):
        canvas.ellipse(HAIR_DEEP, cx + side * face_rx * 0.98, face_y + face_ry * 0.22, face_rx * 0.30, face_ry * 1.02)
        canvas.ellipse(HAIR, cx + side * face_rx * 0.92, face_y + face_ry * 0.20, face_rx * 0.22, face_ry * 0.94)
    canvas.ellipse(HAIR_SHEEN, cx - face_rx * 0.86, face_y - face_ry * 0.05, face_rx * 0.05, face_ry * 0.32)


def _make_head(layout: Layout) -> pygame.Surface:
    rect = layout.head_rect
    big = pygame.Surface((rect.w * SUPERSAMPLE, rect.h * SUPERSAMPLE), pygame.SRCALPHA)
    canvas = Canvas(big, SUPERSAMPLE, (rect.x, rect.y))
    cx = layout.cx
    face_y = layout.face_y
    face_rx = layout.face_rx
    face_ry = layout.face_ry
    pivot_y = layout.pivot[1]

    for side in (-1, 1):
        ear_x = cx + side * face_rx * 0.90
        ear_y = face_y + face_ry * 0.06
        canvas.ellipse(SKIN_SHADOW, ear_x, ear_y, face_rx * 0.15, face_ry * 0.20)
        canvas.ellipse(SKIN, ear_x, ear_y, face_rx * 0.12, face_ry * 0.16)
        canvas.ellipse(EAR_INNER, ear_x + side * face_rx * 0.02, ear_y, face_rx * 0.055, face_ry * 0.08)
        canvas.circle(CLIP, (ear_x, ear_y + face_ry * 0.20), face_rx * 0.035)

    canvas.ellipse(SKIN_SHADOW, cx, pivot_y - face_ry * 0.08, face_rx * 0.30, face_ry * 0.28)
    canvas.ellipse(SKIN, cx, pivot_y - face_ry * 0.12, face_rx * 0.26, face_ry * 0.24)

    canvas.ellipse(SKIN_SHADOW, cx, face_y + face_ry * 0.04, face_rx * 1.02, face_ry * 1.04)
    canvas.ellipse(SKIN, cx, face_y, face_rx, face_ry)
    canvas.ellipse(SKIN_LIGHT, cx - face_rx * 0.18, face_y - face_ry * 0.28, face_rx * 0.48, face_ry * 0.36)
    canvas.ellipse(BLUSH, cx - face_rx * 0.42, face_y + face_ry * 0.28, face_rx * 0.15, face_ry * 0.07)
    canvas.ellipse(BLUSH, cx + face_rx * 0.42, face_y + face_ry * 0.28, face_rx * 0.15, face_ry * 0.07)

    _draw_bangs(canvas, cx, face_y, face_rx, face_ry)

    canvas.circle(CLIP, (cx + face_rx * 0.62, face_y - face_ry * 0.58), face_rx * 0.05)
    canvas.circle((236, 206, 140), (cx + face_rx * 0.62, face_y - face_ry * 0.58), face_rx * 0.025)

    nose_y = face_y + face_ry * 0.16
    canvas.lines(
        SKIN_DEEP,
        [
            (cx - face_rx * 0.015, nose_y),
            (cx - face_rx * 0.05, nose_y + face_ry * 0.10),
            (cx + face_rx * 0.055, nose_y + face_ry * 0.10),
        ],
        width=max(1.4, face_rx * 0.018),
    )

    mouth_y = face_y + face_ry * 0.46
    mouth: list[tuple[float, float]] = []
    for step in range(18):
        t = step / 17
        ang = math.pi * t
        mouth.append((cx - face_rx * 0.16 + face_rx * 0.32 * t, mouth_y + math.sin(ang) * face_ry * 0.045))
    canvas.lines(LIP_DEEP, mouth, width=max(2.0, face_rx * 0.028))
    upper = [(x, y - face_ry * 0.012) for x, y in mouth]
    canvas.lines(LIP, upper, width=max(1.4, face_rx * 0.016))
    return downsample(big, (rect.w, rect.h))


class GirlCharacter(Character):
    """Drawn portrait. Swap her out by adding assets/character.json (see the example file)."""

    def __init__(self, window_size: tuple[int, int]) -> None:
        self.motion = GazeMotion()
        self.pose = self.motion.update(0.0, 0.0, 0.0)
        self._time = 0.0
        self._blink = 0.0
        self._blink_phase = "wait"
        self._blink_t = 0.0
        self._blink_wait = 1.6
        self._layout = compute_layout(window_size)
        self._background: pygame.Surface | None = None
        self._body: pygame.Surface | None = None
        self._head_base: pygame.Surface | None = None
        self._head_frame: pygame.Surface | None = None
        self._eyes_local: tuple[tuple[float, float], tuple[float, float]] = ((0.0, 0.0), (0.0, 0.0))
        self._pivot_local = (0.0, 0.0)
        self._max_ox = 1.0
        self._max_oy = 1.0
        self._build()

    def on_resize(self, size: tuple[int, int]) -> None:
        self._layout = compute_layout(size)
        self._build()

    def rest_anchor(self) -> tuple[float, float]:
        return self._layout.anchor

    def update(self, gaze_x: float, gaze_y: float, dt: float) -> None:
        self._time += dt
        self.pose = self.motion.update(gaze_x, gaze_y, dt)
        self._advance_blink(dt)

    def draw(self, surface: pygame.Surface) -> None:
        assert self._background is not None and self._body is not None and self._head_frame is not None
        breathe = breathe_offset(self._time)
        surface.blit(self._background, (0, 0))
        surface.blit(self._body, (0, round(breathe)))
        self._compose_head()
        pivot = (self._layout.pivot[0] + self.pose.shift_x, self._layout.pivot[1] + self.pose.shift_y + breathe)
        blit_rotate(surface, self._head_frame, pivot, self._pivot_local, self.pose.angle_deg)

    def _build(self) -> None:
        layout = self._layout
        self._background = _make_background(layout)
        self._body = _make_body(layout)
        self._head_base = _make_head(layout)
        self._head_frame = pygame.Surface(self._head_base.get_size(), pygame.SRCALPHA)
        origin_x, origin_y = layout.head_rect.topleft
        self._eyes_local = tuple((ex - origin_x, ey - origin_y) for ex, ey in layout.eyes)
        self._pivot_local = (layout.pivot[0] - origin_x, layout.pivot[1] - origin_y)
        self._max_ox = max(0.5, (layout.eye_rx - layout.iris_r - 1.0) / OVERSHOOT)
        self._max_oy = max(0.5, (layout.eye_ry - layout.iris_r - 1.0) / OVERSHOOT)

    def _advance_blink(self, dt: float) -> None:
        if self._blink_phase == "wait":
            self._blink_wait -= dt
            self._blink = 0.0
            if self._blink_wait <= 0.0:
                self._blink_phase = "close"
                self._blink_t = 0.0
            return
        if self._blink_phase == "close":
            self._blink_t += dt / 0.07
            self._blink = min(1.0, self._blink_t)
            if self._blink >= 1.0:
                self._blink_phase = "open"
                self._blink_t = 0.0
            return
        self._blink_t += dt / 0.12
        self._blink = max(0.0, 1.0 - self._blink_t)
        if self._blink <= 0.0:
            self._blink_phase = "wait"
            self._blink_wait = 0.14 if random.random() < 0.22 else random.uniform(2.6, 5.4)

    def _compose_head(self) -> None:
        assert self._head_base is not None and self._head_frame is not None
        frame = self._head_frame
        frame.fill((0, 0, 0, 0))
        frame.blit(self._head_base, (0, 0))
        look = (self.pose.eye_x, self.pose.eye_y)
        lift = self.pose.eye_y * self._layout.eye_ry * 0.16
        for index, eye in enumerate(self._eyes_local):
            outer = -1 if index == 0 else 1
            self._draw_brow(frame, eye, outer, lift)
            eye_sprite = self._paint_eye(look, outer)
            frame.blit(eye_sprite, eye_sprite.get_rect(center=(round(eye[0]), round(eye[1]))))

    def _draw_brow(
        self,
        surface: pygame.Surface,
        eye: tuple[float, float],
        outer: int,
        lift: float,
    ) -> None:
        layout = self._layout
        ex, ey = eye
        base_y = ey - layout.eye_ry * 1.18 + lift
        points: list[tuple[float, float]] = []
        for step in range(8):
            t = step / 7
            x = ex + outer * (t - 0.12) * layout.eye_rx * 1.55
            arch = math.sin(t * math.pi) * layout.eye_ry * 0.22
            tail = t * layout.eye_ry * 0.05
            points.append((x, base_y - arch - tail))
        width = max(2, round(layout.face_rx * 0.028))
        pygame.draw.lines(surface, HAIR_DEEP, False, [(round(x), round(y)) for x, y in points], width)

    def _paint_eye(self, look: tuple[float, float], outer: int) -> pygame.Surface:
        layout = self._layout
        rx = layout.eye_rx
        ry = layout.eye_ry
        pad = max(8.0, rx * 0.55)
        width = max(1, round((rx + pad) * 2))
        height = max(1, round((ry + pad) * 2))
        sprite = pygame.Surface((width, height), pygame.SRCALPHA)
        cx = width / 2
        cy = height / 2
        eye_rect = pygame.Rect(round(cx - rx), round(cy - ry), max(1, round(rx * 2)), max(1, round(ry * 2)))
        pygame.draw.ellipse(sprite, SCLERA_SHADE, eye_rect)
        white = eye_rect.inflate(-max(1, round(rx * 0.08)), -max(1, round(ry * 0.12)))
        pygame.draw.ellipse(sprite, SCLERA, white)

        ox = clamp(look[0], -OVERSHOOT, OVERSHOOT) * self._max_ox
        oy = clamp(look[1], -OVERSHOOT, OVERSHOOT) * self._max_oy
        iris = pygame.Surface((width, height), pygame.SRCALPHA)
        center = (round(cx + ox), round(cy + oy))
        iris_r = max(2, round(layout.iris_r))
        pygame.draw.circle(iris, IRIS_DEEP, center, iris_r)
        pygame.draw.circle(iris, IRIS, center, max(1, round(iris_r * 0.78)))
        pygame.draw.circle(
            iris,
            IRIS_LIGHT,
            (center[0] - round(iris_r * 0.28), center[1] - round(iris_r * 0.32)),
            max(1, round(iris_r * 0.32)),
        )
        pygame.draw.circle(iris, PUPIL, center, max(1, round(layout.pupil_r)))
        pygame.draw.circle(
            iris,
            CATCHLIGHT,
            (center[0] - round(layout.pupil_r * 0.35), center[1] - round(layout.pupil_r * 0.45)),
            max(1, round(layout.pupil_r * 0.45)),
        )
        mask = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.ellipse(mask, (255, 255, 255, 255), eye_rect)
        iris.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        sprite.blit(iris, (0, 0))

        lash_line: list[tuple[int, int]] = []
        for step in range(14):
            nx = -1.0 + 2.0 * step / 13.0
            x = cx + nx * rx
            y = cy - ry * math.sqrt(max(0.0, 1.0 - nx * nx))
            lash_line.append((round(x), round(y)))
        pygame.draw.lines(sprite, HAIR_DEEP, False, lash_line, max(2, round(rx * 0.10)))
        self._draw_lashes(sprite, cx, cy, rx, ry, outer)

        if self._blink > 0.02:
            squish = max(0.07, 1.0 - 0.93 * self._blink)
            sprite = pygame.transform.smoothscale(sprite, (width, max(1, round(height * squish))))
        return sprite

    def _draw_lashes(self, sprite: pygame.Surface, cx: float, cy: float, rx: float, ry: float, outer: int) -> None:
        corner_x = cx + outer * rx * 0.72
        corner_y = cy - ry * 0.05
        color = HAIR_DEEP
        thickness = max(1, round(rx * 0.07))
        for degrees in (35, 65, 95):
            rad = math.radians(degrees)
            length = rx * 0.34
            end = (
                round(corner_x + outer * math.cos(rad) * length),
                round(corner_y - math.sin(rad) * length),
            )
            pygame.draw.line(sprite, color, (round(corner_x), round(corner_y)), end, thickness)
