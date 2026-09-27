"""Small pygame drawing helpers shared by character implementations."""

from __future__ import annotations

import pygame


def blit_rotate(
    destination: pygame.Surface,
    image: pygame.Surface,
    pivot_on_destination: tuple[float, float],
    pivot_on_image: tuple[float, float],
    angle_deg: float,
) -> None:
    """Rotate `image` around a pivot and put that pivot at a destination point.

    `angle_deg` is counterclockwise, matching `pygame.transform.rotate`.
    """
    pos = pygame.math.Vector2(pivot_on_destination)
    origin = pygame.math.Vector2(pivot_on_image)
    resting = image.get_rect(topleft=(pos.x - origin.x, pos.y - origin.y))
    offset_center_to_pivot = pos - pygame.math.Vector2(resting.center)
    rotated_offset = offset_center_to_pivot.rotate(-angle_deg)
    rotated_center = pos - rotated_offset
    rotated = pygame.transform.rotozoom(image, angle_deg, 1.0)
    rect = rotated.get_rect(center=(round(rotated_center.x), round(rotated_center.y)))
    destination.blit(rotated, rect)


class Canvas:
    """Draw in window coordinates onto a supersampled surface, then scale it down."""

    def __init__(self, surface: pygame.Surface, scale: int, origin: tuple[float, float] = (0.0, 0.0)) -> None:
        self.surface = surface
        self.scale = scale
        self.origin = origin

    def _box(self, cx: float, cy: float, rx: float, ry: float) -> pygame.Rect:
        ox, oy = self.origin
        scale = self.scale
        left = round((cx - rx - ox) * scale)
        top = round((cy - ry - oy) * scale)
        right = round((cx + rx - ox) * scale)
        bottom = round((cy + ry - oy) * scale)
        return pygame.Rect(left, top, max(1, right - left), max(1, bottom - top))

    def ellipse(self, color: tuple[int, ...], cx: float, cy: float, rx: float, ry: float, width: int = 0) -> None:
        if rx <= 0.4 or ry <= 0.4:
            return
        rect = self._box(cx, cy, rx, ry)
        if len(color) == 4 and color[3] < 255:
            self._stamp(color, rect)
            return
        pygame.draw.ellipse(self.surface, color, rect, width)

    def circle(self, color: tuple[int, ...], center: tuple[float, float], radius: float, width: int = 0) -> None:
        self.ellipse(color, center[0], center[1], radius, radius, width)

    def polygon(self, color: tuple[int, ...], points: list[tuple[float, float]]) -> None:
        if len(points) < 3:
            return
        ox, oy = self.origin
        scale = self.scale
        mapped = [(round((x - ox) * scale), round((y - oy) * scale)) for x, y in points]
        pygame.draw.polygon(self.surface, color, mapped)

    def lines(self, color: tuple[int, ...], points: list[tuple[float, float]], width: int = 1) -> None:
        if len(points) < 2:
            return
        ox, oy = self.origin
        scale = self.scale
        mapped = [(round((x - ox) * scale), round((y - oy) * scale)) for x, y in points]
        pygame.draw.lines(self.surface, color, False, mapped, max(1, round(width * scale)))

    def _stamp(self, color: tuple[int, ...], rect: pygame.Rect) -> None:
        # Drawing RGBA directly onto an SRCALPHA surface punches a hole.
        # A temporary surface blits with normal alpha blending instead.
        layer = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.ellipse(layer, color, layer.get_rect())
        self.surface.blit(layer, rect.topleft)


def downsample(surface: pygame.Surface, size: tuple[int, int]) -> pygame.Surface:
    if surface.get_size() == size:
        return surface
    return pygame.transform.smoothscale(surface, size)
