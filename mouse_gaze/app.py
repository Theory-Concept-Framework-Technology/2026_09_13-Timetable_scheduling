"""Pygame window loop."""

from __future__ import annotations

import pygame

from mouse_gaze.factory import create_character
from mouse_gaze.tracker import MouseTracker

WINDOW_SIZE = (1280, 720)
MIN_SIZE = 240
HUD_COLOR = (78, 52, 58)
HUD_PANEL = (255, 248, 244, 188)


def run() -> None:
    pygame.display.init()
    pygame.font.init()
    pygame.display.set_caption("Mouse Gaze")
    screen = _open_window(WINDOW_SIZE)
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("segoeui,calibri,arial", 18)
    character = create_character(screen.get_size())
    tracker = MouseTracker()
    hud_key = ""
    hud_surface: pygame.Surface | None = None

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        if dt <= 0.0:
            dt = 1.0 / 60.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            elif event.type == pygame.VIDEORESIZE and event.w >= MIN_SIZE and event.h >= MIN_SIZE:
                screen = pygame.display.get_surface()
                character.on_resize(screen.get_size())
                hud_key = ""

        tracker.update(dt)
        anchor = character.rest_anchor()
        gaze_x, gaze_y = tracker.gaze_toward(anchor)
        character.update(gaze_x, gaze_y, dt)
        character.draw(screen)
        hud_key, hud_surface = _draw_hud(
            screen,
            font,
            tracker.cursor_text(),
            f"Looking {tracker.pointing_label(anchor)}",
            hud_key,
            hud_surface,
        )
        pygame.display.flip()

    pygame.quit()


def _open_window(size: tuple[int, int]) -> pygame.Surface:
    flags = pygame.RESIZABLE
    try:
        return pygame.display.set_mode(size, flags, vsync=1)
    except (TypeError, pygame.error):
        return pygame.display.set_mode(size, flags)


def _draw_hud(
    screen: pygame.Surface,
    font: pygame.font.Font,
    line_one: str,
    line_two: str,
    cache_key: str,
    cached: pygame.Surface | None,
) -> tuple[str, pygame.Surface]:
    key = f"{line_one}|{line_two}|{screen.get_width()}"
    if key != cache_key or cached is None:
        first = font.render(line_one, True, HUD_COLOR)
        second = font.render(line_two, True, HUD_COLOR)
        width = max(first.get_width(), second.get_width()) + 28
        height = first.get_height() + second.get_height() + 22
        panel = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(panel, HUD_PANEL, panel.get_rect(), border_radius=12)
        panel.blit(first, (14, 8))
        panel.blit(second, (14, 10 + first.get_height()))
        cached = panel
        cache_key = key
    screen.blit(cached, (16, screen.get_height() - cached.get_height() - 16))
    return cache_key, cached
