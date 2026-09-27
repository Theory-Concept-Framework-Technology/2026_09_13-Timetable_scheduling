"""Turn the illustrated master into transparent body, head, and pupil sprites.

Run from the project root:
  .venv\\Scripts\\python.exe scripts\\build_v2_assets.py
"""

from __future__ import annotations

import json
import statistics
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
SOURCE = Path(
    r"C:\Users\shukl\.cursor\projects\c-Users-shukl-mouse-gaze\assets\mouse-gaze-v2-master.png"
)
OUT = ROOT / "assets" / "v2"
REFERENCE = (1280, 720)
BG = (197, 197, 197)


def color_distance(color: tuple[int, int, int]) -> float:
    return ((color[0] - BG[0]) ** 2 + (color[1] - BG[1]) ** 2 + (color[2] - BG[2]) ** 2) ** 0.5


def luminance(color: tuple[int, int, int]) -> float:
    return (color[0] + color[1] + color[2]) / 3


def is_skin(color: tuple[int, int, int], alpha: int) -> bool:
    red, green, blue = color
    if alpha < 140:
        return False
    # Include lip color and the darker skin under the chin. The maroon shirt
    # stays out: it is darker, and its blue is higher than its green.
    return red > 150 and green > 70 and blue > 55 and red > blue + 18 and green + 8 > blue


def is_shirt(color: tuple[int, int, int], alpha: int) -> bool:
    red, green, blue = color
    if alpha < 140 or is_skin(color, alpha):
        return False
    return red > 85 and red > green + 22 and red > blue + 18 and green < 145 and blue < 140


def is_hair(color: tuple[int, int, int], alpha: int) -> bool:
    if alpha < 100 or is_shirt(color, alpha) or is_skin(color, alpha):
        return False
    red, green, blue = color
    return luminance(color) < 100 and max(red, green, blue) - min(red, green, blue) < 48


def is_sclera(color: tuple[int, int, int], alpha: int) -> bool:
    if alpha < 200:
        return False
    red, green, blue = color
    return luminance(color) > 205 and max(red, green, blue) - min(red, green, blue) < 40


def remove_background(image: Image.Image) -> Image.Image:
    rgb = image.convert("RGB")
    width, height = rgb.size
    source = rgb.load()
    cutout = Image.new("RGBA", (width, height))
    output = cutout.load()
    for y in range(height):
        for x in range(width):
            color = source[x, y]
            distance = color_distance(color)
            chroma = max(color) - min(color)
            red, green, blue = color
            warm = red > 175 and green > 130 and blue > 90 and red > blue + 18 and green > blue + 6
            if warm or chroma > 16 or distance >= 34:
                alpha = 255
            elif distance <= 14:
                alpha = 0
            else:
                alpha = int((distance - 14) / 20 * 255)
            output[x, y] = (red, green, blue, alpha)
    for _ in range(3):
        _strip_gray_fringe(cutout)
    _defringe(cutout)
    return cutout


def _strip_gray_fringe(image: Image.Image) -> None:
    """Drop the gray halo left where dark hair met the flat background."""
    pixels = image.load()
    width, height = image.size
    clear: list[tuple[int, int]] = []
    for y in range(height):
        for x in range(width):
            red, green, blue, alpha = pixels[x, y]
            if alpha < 200:
                continue
            if max(red, green, blue) - min(red, green, blue) > 16:
                continue
            if luminance((red, green, blue)) < 70:
                continue
            touches_empty = False
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                xx, yy = x + dx, y + dy
                if xx < 0 or yy < 0 or xx >= width or yy >= height or pixels[xx, yy][3] < 40:
                    touches_empty = True
                    break
            if touches_empty:
                clear.append((x, y))
    for x, y in clear:
        pixels[x, y] = (0, 0, 0, 0)


def _defringe(image: Image.Image) -> None:
    """Replace gray background mixed into soft edges with a nearby solid color."""
    pixels = image.load()
    width, height = image.size
    radius = 4
    pending: list[tuple[int, int, tuple[int, int, int], int]] = []
    for y in range(height):
        for x in range(width):
            red, green, blue, alpha = pixels[x, y]
            if alpha == 0 or alpha == 255:
                continue
            nearest: tuple[int, tuple[int, int, int]] | None = None
            for dy in range(-radius, radius + 1):
                yy = y + dy
                if yy < 0 or yy >= height:
                    continue
                for dx in range(-radius, radius + 1):
                    xx = x + dx
                    if xx < 0 or xx >= width or pixels[xx, yy][3] != 255:
                        continue
                    score = dx * dx + dy * dy
                    if nearest is None or score < nearest[0]:
                        nearest = (score, pixels[xx, yy][:3])
            color = nearest[1] if nearest is not None else (red, green, blue)
            pending.append((x, y, color, alpha))
    for x, y, color, alpha in pending:
        pixels[x, y] = (*color, alpha)


def bounds(image: Image.Image, threshold: int = 16) -> tuple[int, int, int, int]:
    alpha = image.getchannel("A")
    mask = alpha.point(lambda value: 255 if value > threshold else 0)
    box = mask.getbbox()
    if box is None:
        raise SystemExit("The cutout has no visible pixels.")
    return box


def clusters(points: list[tuple[int, int]]) -> tuple[list[tuple[int, int]], list[tuple[int, int]]]:
    if not points:
        raise SystemExit("Could not find the eyes.")
    middle = statistics.median(x for x, _ in points)
    left = [point for point in points if point[0] < middle]
    right = [point for point in points if point[0] >= middle]
    if not left or not right:
        raise SystemExit("The eyes did not separate into a left and right eye.")
    return left, right


def box_of(points: list[tuple[int, int]], pad: int, limit: tuple[int, int]) -> tuple[int, int, int, int]:
    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    width, height = limit
    return (
        max(0, min(xs) - pad),
        max(0, min(ys) - pad),
        min(width - 1, max(xs) + pad),
        min(height - 1, max(ys) + pad),
    )


def find_eyes(image: Image.Image, box: tuple[int, int, int, int]) -> list[dict]:
    pixels = image.load()
    left, top, right, bottom = box
    band_top = top + int((bottom - top) * 0.18)
    band_bottom = top + int((bottom - top) * 0.46)
    sclera_points: list[tuple[int, int]] = []
    for y in range(band_top, band_bottom):
        for x in range(left + int((right - left) * 0.18), right - int((right - left) * 0.18)):
            red, green, blue, alpha = pixels[x, y]
            if is_sclera((red, green, blue), alpha):
                sclera_points.append((x, y))
    if len(sclera_points) < 20:
        raise SystemExit("Could not find the whites of the eyes.")
    eye_band = statistics.median(point[1] for point in sclera_points)
    sclera_points = [point for point in sclera_points if abs(point[1] - eye_band) <= 28]
    found = []
    for group in clusters(sclera_points):
        center_x = int(round(statistics.mean(point[0] for point in group)))
        center_y = int(round(statistics.mean(point[1] for point in group)))
        dark: list[tuple[int, int]] = []
        for y in range(center_y - 16, center_y + 17):
            for x in range(center_x - 16, center_x + 17):
                if (x - center_x) ** 2 + (y - center_y) ** 2 > 16 * 16:
                    continue
                red, green, blue, alpha = pixels[x, y]
                if alpha > 180 and luminance((red, green, blue)) < 90:
                    dark.append((x, y))
        if len(dark) < 6:
            raise SystemExit("An eye is missing a pupil to remove.")
        darkest = sorted(dark, key=lambda point: luminance(pixels[point][:3]))[: max(6, len(dark) // 2)]
        pupil_x = int(round(statistics.mean(point[0] for point in darkest)))
        pupil_y = int(round(statistics.mean(point[1] for point in darkest)))
        radius = max(5, int(round(statistics.median(
            ((point[0] - pupil_x) ** 2 + (point[1] - pupil_y) ** 2) ** 0.5 for point in darkest
        ))) + 1)
        radius = min(radius, 14)
        found.append(
            {
                "center": (pupil_x, pupil_y),
                "radius": radius,
                "box": box_of(group, 14, image.size),
                "dark": darkest,
            }
        )
    found.sort(key=lambda eye: eye["center"][0])
    return found


def iris_color(image: Image.Image, eye: dict) -> tuple[int, int, int]:
    pixels = image.load()
    center_x, center_y = eye["center"]
    inner = eye["radius"] + 2
    outer = eye["radius"] + 10
    samples: list[tuple[int, int, int]] = []
    x0, y0, x1, y1 = eye["box"]
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            distance = ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5
            if not inner <= distance <= outer:
                continue
            red, green, blue, alpha = pixels[x, y]
            if alpha < 180:
                continue
            if red > blue + 12 and 50 < luminance((red, green, blue)) < 170:
                samples.append((red, green, blue))
    if not samples:
        return (92, 58, 40)
    return (
        int(statistics.median(color[0] for color in samples)),
        int(statistics.median(color[1] for color in samples)),
        int(statistics.median(color[2] for color in samples)),
    )


def iris_radius(image: Image.Image, eye: dict) -> int:
    pixels = image.load()
    center_x, center_y = eye["center"]
    radii: list[int] = []
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1)):
        length = (dx * dx + dy * dy) ** 0.5
        step_x, step_y = dx / length, dy / length
        last = eye["radius"]
        width, height = image.size
        for distance in range(eye["radius"], eye["radius"] + 28):
            x = int(center_x + step_x * distance)
            y = int(center_y + step_y * distance)
            if x < 0 or y < 0 or x >= width or y >= height:
                break
            red, green, blue, alpha = pixels[x, y]
            if alpha < 160 or is_sclera((red, green, blue), alpha) or is_skin((red, green, blue), alpha):
                break
            last = distance
        radii.append(last)
    return int(statistics.median(radii))


def clear_pupils(image: Image.Image, eyes: list[dict]) -> None:
    pixels = image.load()
    for eye in eyes:
        color = iris_color(image, eye)
        center_x, center_y = eye["center"]
        reach = eye["radius"] + 3
        width, height = image.size
        for y in range(max(0, center_y - reach), min(height, center_y + reach + 1)):
            for x in range(max(0, center_x - reach), min(width, center_x + reach + 1)):
                if (x - center_x) ** 2 + (y - center_y) ** 2 > reach * reach:
                    continue
                red, green, blue, alpha = pixels[x, y]
                hole = alpha < 160
                bright_speck = alpha > 160 and luminance((red, green, blue)) > 210
                dark = alpha > 160 and luminance((red, green, blue)) < 80
                if hole or bright_speck or dark:
                    pixels[x, y] = (*color, 255)


def neck_line(image: Image.Image, eyes: list[dict], box: tuple[int, int, int, int]) -> tuple[int, int]:
    """Place the pivot where the wide face narrows into the neck."""
    pixels = image.load()
    width, height = image.size
    center_x = int(round(statistics.mean(eye["center"][0] for eye in eyes)))
    eye_y = int(round(statistics.mean(eye["center"][1] for eye in eyes)))
    rows: list[tuple[int, int]] = []
    for y in range(eye_y + 8, min(height, eye_y + 420)):
        count = 0
        for x in range(max(0, center_x - 220), min(width, center_x + 221)):
            red, green, blue, alpha = pixels[x, y]
            if is_skin((red, green, blue), alpha):
                count += 1
        rows.append((y, count))
    if not rows:
        return center_x, eye_y + 90
    peak = max(count for _, count in rows)
    chin = rows[0][0]
    seen_peak = False
    for y, count in rows:
        if count >= peak * 0.85:
            seen_peak = True
            chin = y
            continue
        if seen_peak and count < peak * 0.55:
            chin = y
            break
    return center_x, min(height - 1, chin + 28)


def split_layers(image: Image.Image, neck_y: int) -> tuple[Image.Image, Image.Image]:
    width, height = image.size
    pixels = image.load()
    head = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    body = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    head_px = head.load()
    body_px = body.load()
    shirt_points: list[tuple[int, int]] = []
    for y in range(height):
        for x in range(width):
            red, green, blue, alpha = pixels[x, y]
            if alpha < 16:
                continue
            color = (red, green, blue)
            shirt = is_shirt(color, alpha)
            skin = is_skin(color, alpha)
            hair = is_hair(color, alpha)
            if shirt:
                body_px[x, y] = (red, green, blue, alpha)
                shirt_points.append((x, y))
            if hair or skin or (not shirt and y <= neck_y + 48):
                head_px[x, y] = (red, green, blue, alpha)
            if skin and y >= neck_y + 8:
                body_px[x, y] = (red, green, blue, alpha)
    if shirt_points:
        sample = pixels[shirt_points[len(shirt_points) // 2]]
        fill = (sample[0], sample[1], sample[2], 255)
        min_x = min(point[0] for point in shirt_points)
        max_x = max(point[0] for point in shirt_points)
        max_y = max(point[1] for point in shirt_points)
        for _ in range(10):
            grown: list[tuple[int, int]] = []
            for y in range(max(1, neck_y), min(height - 1, max_y + 1)):
                for x in range(max(1, min_x), min(width - 1, max_x + 1)):
                    if body_px[x, y][3] > 0 or head_px[x, y][3] == 0:
                        continue
                    neighbors = (
                        body_px[x - 1, y][3],
                        body_px[x + 1, y][3],
                        body_px[x, y - 1][3],
                        body_px[x, y + 1][3],
                    )
                    if any(value > 180 for value in neighbors):
                        grown.append((x, y))
            for x, y in grown:
                body_px[x, y] = fill
            if not grown:
                break
    return head, body


def fill_neck(image: Image.Image, center_x: int, neck_y: int) -> int:
    """Close holes under the chin with the skin color on either side."""
    pixels = image.load()
    width, height = image.size
    fills: dict[tuple[int, int], tuple[int, int, int, int]] = {}
    for y in range(max(0, neck_y - 28), min(height, neck_y + 48)):
        for x in range(max(0, center_x - 80), min(width, center_x + 81)):
            if pixels[x, y][3] >= 180:
                continue
            left = _nearest_skin(pixels, x, y, -1, width)
            right = _nearest_skin(pixels, x, y, 1, width)
            if left is None or right is None:
                continue
            color = tuple((left[channel] + right[channel]) // 2 for channel in range(3))
            fills[(x, y)] = (*color, 255)
    for (x, y), color in fills.items():
        pixels[x, y] = color
    return len(fills)


def _nearest_skin(pixels, x: int, y: int, step: int, width: int) -> tuple[int, int, int, int] | None:
    for offset in range(1, 32):
        xx = x + step * offset
        if xx < 0 or xx >= width:
            return None
        pixel = pixels[xx, y]
        if is_skin(pixel[:3], pixel[3]):
            return pixel
    return None


def crop_with_margin(image: Image.Image, margin: int) -> tuple[Image.Image, tuple[int, int]]:
    left, top, right, bottom = bounds(image)
    left = max(0, left - margin)
    top = max(0, top - margin)
    right = min(image.width, right + margin)
    bottom = min(image.height, bottom + margin)
    return image.crop((left, top, right, bottom)), (left, top)


def scale_to(image: Image.Image, origin: tuple[int, int], factor: float) -> tuple[Image.Image, tuple[float, float]]:
    if abs(factor - 1) < 0.01:
        return image, (float(origin[0]), float(origin[1]))
    size = (max(1, round(image.width * factor)), max(1, round(image.height * factor)))
    return _resize_rgba(image, size), (origin[0] * factor, origin[1] * factor)


def _resize_rgba(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    """Resize in premultiplied alpha so transparent pixels do not tint the edge."""
    red, green, blue, alpha = image.convert("RGBA").split()
    premul = Image.merge(
        "RGBA",
        (ImageChops.multiply(red, alpha), ImageChops.multiply(green, alpha), ImageChops.multiply(blue, alpha), alpha),
    ).resize(size, Image.Resampling.LANCZOS)
    source = premul.load()
    resized = Image.new("RGBA", size)
    output = resized.load()
    width, height = size
    for y in range(height):
        for x in range(width):
            red, green, blue, alpha = source[x, y]
            if alpha == 0:
                output[x, y] = (0, 0, 0, 0)
                continue
            scale = 255 / alpha
            output[x, y] = (
                min(255, round(red * scale)),
                min(255, round(green * scale)),
                min(255, round(blue * scale)),
                alpha,
            )
    return resized


def seal_irises(image: Image.Image, eyes: list[tuple[int, int]], radii: list[int]) -> None:
    """Fill pupil holes with nearby iris color so the backdrop cannot show through."""
    pixels = image.load()
    width, height = image.size
    for (center_x, center_y), radius in zip(eyes, radii):
        reach = max(4, radius)
        samples: list[tuple[int, int, int]] = []
        for y in range(max(0, center_y - reach - 8), min(height, center_y + reach + 9)):
            for x in range(max(0, center_x - reach - 8), min(width, center_x + reach + 9)):
                distance = ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5
                if not reach <= distance <= reach + 7:
                    continue
                red, green, blue, alpha = pixels[x, y]
                if alpha > 200 and red > blue + 8 and 40 < luminance((red, green, blue)) < 175:
                    samples.append((red, green, blue))
        if samples:
            color = tuple(int(statistics.median(sample[channel] for sample in samples)) for channel in range(3))
        else:
            color = (92, 58, 40)
        for y in range(max(0, center_y - reach), min(height, center_y + reach + 1)):
            for x in range(max(0, center_x - reach), min(width, center_x + reach + 1)):
                if (x - center_x) ** 2 + (y - center_y) ** 2 > reach * reach:
                    continue
                red, green, blue, alpha = pixels[x, y]
                tone = luminance((red, green, blue))
                if alpha < 200 or tone < 70 or tone > 220:
                    pixels[x, y] = (*color, 255)


def draw_pupil(radius: int) -> Image.Image:
    radius = max(5, min(radius, 9))
    pad = 4
    size = radius * 2 + pad * 2
    sprite = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(sprite)
    draw.ellipse((pad, pad, pad + radius * 2 - 1, pad + radius * 2 - 1), fill=(22, 14, 12, 255))
    highlight = max(2, radius // 4)
    draw.ellipse((pad + 2, pad + 1, pad + 2 + highlight, pad + 1 + highlight), fill=(255, 255, 255, 220))
    return sprite


def save_png(image: Image.Image, path: Path) -> None:
    image.save(path, "PNG", optimize=True)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    cutout = remove_background(Image.open(SOURCE))
    box = bounds(cutout)
    eyes = find_eyes(cutout, box)
    for eye in eyes:
        eye["iris_radius"] = iris_radius(cutout, eye)
    clear_pupils(cutout, eyes)
    center_x, neck_y = neck_line(cutout, eyes, box)
    head, body = split_layers(cutout, neck_y)
    print("neck fill", fill_neck(head, center_x, neck_y), fill_neck(body, center_x, neck_y))
    head, head_origin = crop_with_margin(head, 28)
    body, body_origin = crop_with_margin(body, 8)

    composed_height = max(head_origin[1] + head.height, body_origin[1] + body.height) - min(head_origin[1], body_origin[1])
    target_height = 660
    factor = min(1.0, target_height / composed_height)
    head, head_origin_f = scale_to(head, head_origin, factor)
    body, body_origin_f = scale_to(body, body_origin, factor)
    head_origin = (int(round(head_origin_f[0])), int(round(head_origin_f[1])))
    body_origin = (int(round(body_origin_f[0])), int(round(body_origin_f[1])))

    eye_centers = []
    iris_limits = []
    iris_radii = []
    for eye in eyes:
        scaled_center = (eye["center"][0] * factor, eye["center"][1] * factor)
        local = (scaled_center[0] - head_origin[0], scaled_center[1] - head_origin[1])
        eye_centers.append((int(round(local[0])), int(round(local[1]))))
        iris_px = int(round(eye["iris_radius"] * factor))
        pupil_px = int(round((eye["radius"] + 2) * factor))
        iris_radii.append(max(4, iris_px - 2))
        iris_limits.append(max(4, iris_px - pupil_px))
    seal_irises(head, eye_centers, iris_radii)

    pupil_radius = max(5, int(round(statistics.mean(eye["radius"] for eye in eyes) * factor * 0.7)))
    pupil = draw_pupil(pupil_radius)
    save_png(head, OUT / "head.png")
    save_png(body, OUT / "body.png")
    save_png(pupil, OUT / "pupil.png")

    stage_width, stage_height = REFERENCE
    content_left = min(head_origin[0], body_origin[0])
    content_right = max(head_origin[0] + head.width, body_origin[0] + body.width)
    content_top = min(head_origin[1], body_origin[1])
    content_height = max(head_origin[1] + head.height, body_origin[1] + body.height) - content_top
    offset_x = int(round((stage_width - (content_right - content_left)) / 2 - content_left))
    offset_y = int(round((stage_height - content_height) / 2 - content_top + 8))

    anchor = (
        int(round(offset_x + statistics.mean(center[0] + head_origin[0] for center in eye_centers))),
        int(round(offset_y + statistics.mean(center[1] + head_origin[1] for center in eye_centers))),
    )
    config = {
        "reference_size": [stage_width, stage_height],
        "anchor": [anchor[0], anchor[1]],
        "body": "body.png",
        "body_pos": [body_origin[0] + offset_x, body_origin[1] + offset_y],
        "head": "head.png",
        "head_pivot": [int(round(center_x * factor - head_origin[0])), int(round(neck_y * factor - head_origin[1]))],
        "head_pos": [int(round(center_x * factor + offset_x)), int(round(neck_y * factor + offset_y))],
        "eyes": [list(center) for center in eye_centers],
        "pupil": "pupil.png",
        "pupil_range": [max(6, min(iris_limits)), max(4, int(round(max(6, min(iris_limits)) * 0.7)))],
        "max_head_degrees": 8,
        "head_shift": [12, 8],
    }
    (OUT / "character.json").write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(config, indent=2))
    for name in ("head.png", "body.png", "pupil.png"):
        path = OUT / name
        with Image.open(path) as saved:
            print(name, saved.size, saved.mode, path.stat().st_size)


if __name__ == "__main__":
    main()
