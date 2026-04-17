from __future__ import annotations

from math import cos, pi, sin
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageOps


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "src" / "assets" / "hero"
UPSCALE = 3


def rgba(value: str, alpha: int = 255) -> tuple[int, int, int, int]:
    value = value.lstrip("#")
    if len(value) == 3:
        value = "".join(ch * 2 for ch in value)
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4)) + (alpha,)


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def blend(a: tuple[int, int, int, int], b: tuple[int, int, int, int], t: float) -> tuple[int, int, int, int]:
    return tuple(int(lerp(a[idx], b[idx], t)) for idx in range(4))


def vertical_gradient(size: tuple[int, int], top: tuple[int, int, int, int], bottom: tuple[int, int, int, int]) -> Image.Image:
    width, height = size
    image = Image.new("RGBA", size)
    pixels = image.load()
    for y in range(height):
        color = blend(top, bottom, y / max(height - 1, 1))
        for x in range(width):
            pixels[x, y] = color
    return image


def horizontal_gradient(size: tuple[int, int], left: tuple[int, int, int, int], right: tuple[int, int, int, int]) -> Image.Image:
    width, height = size
    image = Image.new("RGBA", size)
    pixels = image.load()
    for x in range(width):
        color = blend(left, right, x / max(width - 1, 1))
        for y in range(height):
            pixels[x, y] = color
    return image


def rounded_mask(size: tuple[int, int], radius: int) -> Image.Image:
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, size[0], size[1]), radius=radius, fill=255)
    return mask


def ellipse_mask(size: tuple[int, int]) -> Image.Image:
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size[0], size[1]), fill=255)
    return mask


def paste_gradient_shape(
    base: Image.Image,
    bbox: tuple[int, int, int, int],
    top: tuple[int, int, int, int],
    bottom: tuple[int, int, int, int],
    *,
    radius: int | None = None,
    ellipse: bool = False,
) -> None:
    left, top_pos, right, bottom_pos = bbox
    size = (right - left, bottom_pos - top_pos)
    fill = vertical_gradient(size, top, bottom)
    mask = ellipse_mask(size) if ellipse else rounded_mask(size, radius or 0)
    base.alpha_composite(fill, dest=(left, top_pos), source=(0, 0))
    base.putalpha(Image.new("L", base.size, 255))
    current = base.crop((left, top_pos, right, bottom_pos))
    current.putalpha(mask)
    base.paste(current, (left, top_pos), current)


def add_glow(
    base: Image.Image,
    bbox: tuple[int, int, int, int],
    color: tuple[int, int, int, int],
    blur: int,
) -> None:
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    draw.ellipse(bbox, fill=color)
    base.alpha_composite(layer.filter(ImageFilter.GaussianBlur(blur)))


def add_soft_circle(
    base: Image.Image,
    center: tuple[int, int],
    radius: int,
    color: tuple[int, int, int, int],
    blur: int,
) -> None:
    x, y = center
    add_glow(base, (x - radius, y - radius, x + radius, y + radius), color, blur)


def draw_rounded_gradient_rect(
    size: tuple[int, int],
    radius: int,
    top: tuple[int, int, int, int],
    bottom: tuple[int, int, int, int],
) -> Image.Image:
    fill = vertical_gradient(size, top, bottom)
    fill.putalpha(rounded_mask(size, radius))
    return fill


def draw_ellipse_gradient(
    size: tuple[int, int],
    top: tuple[int, int, int, int],
    bottom: tuple[int, int, int, int],
) -> Image.Image:
    fill = vertical_gradient(size, top, bottom)
    fill.putalpha(ellipse_mask(size))
    return fill


def add_highlight(base: Image.Image, bbox: tuple[int, int, int, int], color: tuple[int, int, int, int], blur: int) -> None:
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    draw.ellipse(bbox, fill=color)
    base.alpha_composite(layer.filter(ImageFilter.GaussianBlur(blur)))


def draw_platform(image: Image.Image, center: tuple[int, int], scale: float = 1.0) -> None:
    cx, cy = center
    ring_w = int(320 * scale)
    ring_h = int(108 * scale)

    add_soft_circle(
        image,
        (cx, cy - int(16 * scale)),
        int(128 * scale),
        rgba("#ffffff", 120),
        int(42 * scale),
    )

    shadow = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(shadow)
    draw.ellipse(
        (
            cx - int(ring_w * 0.42),
            cy + int(ring_h * 0.08),
            cx + int(ring_w * 0.42),
            cy + int(ring_h * 0.28),
        ),
        fill=rgba("#42506e", 90),
    )
    image.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(int(26 * scale))))

    outer = draw_ellipse_gradient(
        (ring_w, ring_h),
        rgba("#fffdfa", 255),
        rgba("#e5d9cb", 250),
    )
    inner = draw_ellipse_gradient(
        (int(ring_w * 0.76), int(ring_h * 0.58)),
        rgba("#fffefc", 250),
        rgba("#efe4d6", 214),
    )
    core = draw_ellipse_gradient(
        (int(ring_w * 0.48), int(ring_h * 0.18)),
        rgba("#ffffff", 220),
        rgba("#fff4e8", 96),
    )

    image.alpha_composite(outer, (cx - ring_w // 2, cy - ring_h // 2))
    image.alpha_composite(inner, (cx - inner.width // 2, cy - inner.height // 2 + int(6 * scale)))
    image.alpha_composite(core, (cx - core.width // 2, cy - core.height // 2 + int(6 * scale)))

    rim = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(rim)
    draw.arc(
        (
            cx - ring_w // 2,
            cy - ring_h // 2,
            cx + ring_w // 2,
            cy + ring_h // 2,
        ),
        start=200,
        end=355,
        fill=rgba("#d1c0ac", 144),
        width=max(2, int(5 * scale)),
    )
    image.alpha_composite(rim)


def place_with_shadow(image: Image.Image, asset: Image.Image, position: tuple[int, int], shadow_color: tuple[int, int, int, int], blur: int, offset: tuple[int, int]) -> None:
    shadow = Image.new("RGBA", image.size, (0, 0, 0, 0))
    alpha = asset.getchannel("A")
    tint = Image.new("RGBA", asset.size, shadow_color)
    tint.putalpha(alpha)
    shadow.alpha_composite(tint, dest=(position[0] + offset[0], position[1] + offset[1]))
    image.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(blur)))
    image.alpha_composite(asset, position)


def draw_arm(
    image: Image.Image,
    shoulder: tuple[int, int],
    arm_size: tuple[int, int],
    angle: float,
    top: tuple[int, int, int, int],
    bottom: tuple[int, int, int, int],
) -> None:
    width, height = arm_size
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    arm = draw_rounded_gradient_rect((width, height), width // 2, top, bottom)
    hand = draw_ellipse_gradient((int(width * 0.82), int(width * 0.82)), rgba("#ffe8d1"), rgba("#efba8d"))
    arm.alpha_composite(hand, (width // 2 - hand.width // 2, height - hand.height + int(width * 0.1)))
    layer.alpha_composite(arm, shoulder)
    rotated = layer.rotate(angle, resample=Image.Resampling.BICUBIC, center=(shoulder[0] + width // 2, shoulder[1] + int(width * 0.56)))
    image.alpha_composite(rotated)


def draw_leg(
    image: Image.Image,
    origin: tuple[int, int],
    size: tuple[int, int],
    top: tuple[int, int, int, int],
    bottom: tuple[int, int, int, int],
) -> None:
    leg = draw_rounded_gradient_rect(size, size[0] // 2, top, bottom)
    highlight = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(highlight)
    draw.rounded_rectangle(
        (int(size[0] * 0.18), int(size[1] * 0.1), int(size[0] * 0.42), int(size[1] * 0.66)),
        radius=int(size[0] * 0.16),
        fill=rgba("#ffffff", 18),
    )
    leg.alpha_composite(highlight)
    image.alpha_composite(leg, origin)


def draw_face(
    image: Image.Image,
    center: tuple[int, int],
    variant: dict[str, object],
    scale: int,
) -> None:
    cx, cy = center
    head = draw_ellipse_gradient((194 * scale, 214 * scale), rgba("#ffdcb9"), rgba("#edb88c"))
    image.alpha_composite(head, (cx - head.width // 2, cy - head.height // 2))

    add_highlight(
        image,
        (cx - 86 * scale, cy - 84 * scale, cx - 8 * scale, cy - 18 * scale),
        rgba("#ffffff", 62),
        18 * scale,
    )

    hair_back = Image.new("RGBA", image.size, (0, 0, 0, 0))
    hair_draw = ImageDraw.Draw(hair_back)
    hair_top = variant["hair_top"]
    hair_bottom = variant["hair_bottom"]
    hair_fill = vertical_gradient((230 * scale, 172 * scale), hair_top, hair_bottom)
    hair_fill.putalpha(ellipse_mask((230 * scale, 172 * scale)))
    hair_back.alpha_composite(hair_fill, (cx - 115 * scale, cy - 116 * scale))

    if variant["hair_style"] == "bob":
        hair_draw.rounded_rectangle(
            (cx - 140 * scale, cy - 72 * scale, cx - 112 * scale, cy + 32 * scale),
            radius=16 * scale,
            fill=hair_bottom,
        )
        hair_draw.rounded_rectangle(
            (cx + 112 * scale, cy - 72 * scale, cx + 140 * scale, cy + 24 * scale),
            radius=16 * scale,
            fill=hair_bottom,
        )
    elif variant["hair_style"] == "short":
        hair_draw.ellipse((cx - 126 * scale, cy - 124 * scale, cx + 126 * scale, cy + 14 * scale), fill=hair_bottom)
    elif variant["hair_style"] == "short_wave":
        hair_draw.ellipse((cx - 122 * scale, cy - 124 * scale, cx + 122 * scale, cy + 10 * scale), fill=hair_bottom)
        hair_draw.rounded_rectangle(
            (cx + 100 * scale, cy - 34 * scale, cx + 132 * scale, cy + 40 * scale),
            radius=18 * scale,
            fill=hair_bottom,
        )
    else:
        hair_draw.ellipse((cx - 128 * scale, cy - 126 * scale, cx + 128 * scale, cy + 12 * scale), fill=hair_bottom)
        hair_draw.rounded_rectangle(
            (cx - 128 * scale, cy - 40 * scale, cx - 96 * scale, cy + 54 * scale),
            radius=18 * scale,
            fill=hair_bottom,
        )

    image.alpha_composite(hair_back.filter(ImageFilter.GaussianBlur(2)))

    fringe = Image.new("RGBA", image.size, (0, 0, 0, 0))
    fringe_draw = ImageDraw.Draw(fringe)
    fringe_draw.rounded_rectangle(
        (cx - 116 * scale, cy - 124 * scale, cx + 116 * scale, cy - 36 * scale),
        radius=44 * scale,
        fill=hair_top,
    )
    fringe_draw.rounded_rectangle(
        (cx - 48 * scale, cy - 70 * scale, cx + 48 * scale, cy - 18 * scale),
        radius=20 * scale,
        fill=hair_top,
    )
    image.alpha_composite(fringe)

    eye_layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    eye_draw = ImageDraw.Draw(eye_layer)
    eye_draw.ellipse((cx - 32 * scale, cy - 6 * scale, cx - 16 * scale, cy + 14 * scale), fill=rgba("#24334d"))
    eye_draw.ellipse((cx + 16 * scale, cy - 6 * scale, cx + 32 * scale, cy + 14 * scale), fill=rgba("#24334d"))
    image.alpha_composite(eye_layer)


def draw_body_and_accessory(image: Image.Image, variant: dict[str, object], scale: int) -> None:
    body_top = variant["body_top"]
    body_bottom = variant["body_bottom"]
    trim = variant["trim"]

    if trim is not None:
        trim_layer = draw_rounded_gradient_rect((272 * scale, 294 * scale), 108 * scale, trim, trim)
        image.alpha_composite(trim_layer, (364 * scale, 430 * scale))
    body = draw_rounded_gradient_rect((244 * scale, 276 * scale), 96 * scale, body_top, body_bottom)
    image.alpha_composite(body, (378 * scale, 440 * scale))

    highlight = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(highlight)
    draw.rounded_rectangle((410 * scale, 462 * scale, 456 * scale, 648 * scale), radius=24 * scale, fill=rgba("#ffffff", 18))
    draw.rounded_rectangle((566 * scale, 462 * scale, 604 * scale, 620 * scale), radius=20 * scale, fill=rgba("#1c2742", 16))
    image.alpha_composite(highlight)

    accessory_kind = variant["accessory"]
    if accessory_kind == "tablet":
        accessory = draw_rounded_gradient_rect((180 * scale, 248 * scale), 44 * scale, rgba("#7b8ea8"), rgba("#4a6288"))
        overlay = Image.new("RGBA", accessory.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        draw.rounded_rectangle((28 * scale, 20 * scale, 146 * scale, 194 * scale), radius=34 * scale, fill=rgba("#5f7699", 188))
        draw.rounded_rectangle((110 * scale, 42 * scale, 136 * scale, 176 * scale), radius=12 * scale, fill=rgba("#d8e6ff", 60))
        accessory.alpha_composite(overlay)
        accessory = accessory.rotate(-12, resample=Image.Resampling.BICUBIC, expand=True)
        image.alpha_composite(accessory, (490 * scale, 506 * scale))
    elif accessory_kind == "paper":
        accessory = draw_rounded_gradient_rect((142 * scale, 184 * scale), 34 * scale, rgba("#fffefb"), rgba("#ebe4d7"))
        lines = Image.new("RGBA", accessory.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(lines)
        for offset in (42, 72, 102):
            draw.rounded_rectangle((36 * scale, offset * scale, 104 * scale, (offset + 10) * scale), radius=6 * scale, fill=rgba("#92a0b7", 118))
        accessory.alpha_composite(lines)
        accessory = accessory.rotate(-9, resample=Image.Resampling.BICUBIC, expand=True)
        image.alpha_composite(accessory, (484 * scale, 510 * scale))
    elif accessory_kind == "clipboard":
        accessory = draw_rounded_gradient_rect((156 * scale, 218 * scale), 36 * scale, rgba("#fffefb"), rgba("#e8e3d8"))
        clip = Image.new("RGBA", accessory.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(clip)
        draw.rounded_rectangle((54 * scale, -4 * scale, 104 * scale, 24 * scale), radius=14 * scale, fill=rgba("#7d96d9"))
        for index, offset in enumerate((52, 90, 128)):
            draw.ellipse((28 * scale, offset * scale, 48 * scale, (offset + 20) * scale), fill=rgba("#67b57e", 255))
            draw.rounded_rectangle(
                (58 * scale, (offset + 4) * scale, 122 * scale, (offset + 14) * scale),
                radius=5 * scale,
                fill=rgba("#96a4b9", 110 + index * 10),
            )
        accessory.alpha_composite(clip)
        accessory = accessory.rotate(6, resample=Image.Resampling.BICUBIC, expand=True)
        image.alpha_composite(accessory, (502 * scale, 492 * scale))
    elif accessory_kind == "phone":
        accessory = draw_rounded_gradient_rect((64 * scale, 144 * scale), 24 * scale, rgba("#f8fbff"), rgba("#dce7f8"))
        details = Image.new("RGBA", accessory.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(details)
        draw.rounded_rectangle((22 * scale, 10 * scale, 42 * scale, 16 * scale), radius=4 * scale, fill=rgba("#8ca0c8", 90))
        draw.rounded_rectangle((20 * scale, 116 * scale, 44 * scale, 124 * scale), radius=4 * scale, fill=rgba("#d3dced", 92))
        accessory.alpha_composite(details)
        image.alpha_composite(accessory, (580 * scale, 610 * scale))


def make_character_asset(name: str, variant: dict[str, object]) -> None:
    size = (980 * UPSCALE, 1180 * UPSCALE)
    image = Image.new("RGBA", size, (0, 0, 0, 0))

    add_soft_circle(image, (size[0] // 2, int(770 * UPSCALE)), int(170 * UPSCALE), rgba("#fff6ed", 118), int(72 * UPSCALE))

    beam = Image.new("RGBA", size, (0, 0, 0, 0))
    beam_draw = ImageDraw.Draw(beam)
    beam_draw.polygon(
        [
            (int(386 * UPSCALE), int(234 * UPSCALE)),
            (int(594 * UPSCALE), int(234 * UPSCALE)),
            (int(710 * UPSCALE), int(866 * UPSCALE)),
            (int(270 * UPSCALE), int(866 * UPSCALE)),
        ],
        fill=rgba("#ffffff", 74),
    )
    image.alpha_composite(beam.filter(ImageFilter.GaussianBlur(int(44 * UPSCALE))))

    draw_platform(image, (size[0] // 2, int(890 * UPSCALE)), 1.0 * UPSCALE)

    body_shadow = Image.new("RGBA", size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(body_shadow)
    shadow_draw.ellipse((int(322 * UPSCALE), int(338 * UPSCALE), int(662 * UPSCALE), int(804 * UPSCALE)), fill=rgba("#21314c", 66))
    image.alpha_composite(body_shadow.filter(ImageFilter.GaussianBlur(int(42 * UPSCALE))))

    draw_leg(image, (int(414 * UPSCALE), int(686 * UPSCALE)), (int(72 * UPSCALE), int(240 * UPSCALE)), rgba("#313b5a"), rgba("#222c42"))
    draw_leg(image, (int(496 * UPSCALE), int(686 * UPSCALE)), (int(72 * UPSCALE), int(240 * UPSCALE)), rgba("#303a58"), rgba("#20283c"))

    draw_arm(
        image,
        (int(294 * UPSCALE), int(470 * UPSCALE)),
        (int(70 * UPSCALE), int(280 * UPSCALE)),
        variant["arm_left_angle"],
        rgba("#ffdcbf"),
        rgba("#ebb285"),
    )
    draw_arm(
        image,
        (int(614 * UPSCALE), int(448 * UPSCALE)),
        (int(70 * UPSCALE), int(280 * UPSCALE)),
        variant["arm_right_angle"],
        rgba("#ffdcbf"),
        rgba("#ebb285"),
    )

    draw_body_and_accessory(image, variant, UPSCALE)
    draw_face(image, (size[0] // 2, int(332 * UPSCALE)), variant, UPSCALE)

    final = image.resize((980, 1180), Image.Resampling.LANCZOS)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    final.save(OUTPUT_DIR / f"{name}.png")


def make_center_node() -> None:
    size = (860 * UPSCALE, 760 * UPSCALE)
    image = Image.new("RGBA", size, (0, 0, 0, 0))

    add_soft_circle(image, (size[0] // 2, int(438 * UPSCALE)), int(180 * UPSCALE), rgba("#fff5e8", 134), int(74 * UPSCALE))
    beam = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(beam)
    draw.polygon(
        [
            (int(322 * UPSCALE), int(120 * UPSCALE)),
            (int(538 * UPSCALE), int(120 * UPSCALE)),
            (int(640 * UPSCALE), int(488 * UPSCALE)),
            (int(220 * UPSCALE), int(488 * UPSCALE)),
        ],
        fill=rgba("#ffffff", 82),
    )
    image.alpha_composite(beam.filter(ImageFilter.GaussianBlur(int(38 * UPSCALE))))

    draw_platform(image, (size[0] // 2, int(500 * UPSCALE)), 1.04 * UPSCALE)

    bars = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(bars)
    for x, height, color in (
        (334, 78, "#7589b5"),
        (398, 132, "#536688"),
        (466, 194, "#273854"),
    ):
        left = int(x * UPSCALE)
        top = int((470 - height) * UPSCALE)
        rect = draw_rounded_gradient_rect(
            (int(42 * UPSCALE), int(height * UPSCALE)),
            int(18 * UPSCALE),
            rgba(color),
            rgba("#1d2941"),
        )
        image.alpha_composite(rect, (left, top))

    draw.line(
        [
            (int(322 * UPSCALE), int(354 * UPSCALE)),
            (int(410 * UPSCALE), int(290 * UPSCALE)),
            (int(476 * UPSCALE), int(316 * UPSCALE)),
            (int(558 * UPSCALE), int(224 * UPSCALE)),
        ],
        fill=rgba("#d9b07d", 255),
        width=int(18 * UPSCALE),
        joint="curve",
    )
    arrow = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(arrow)
    draw.polygon(
        [
            (int(556 * UPSCALE), int(176 * UPSCALE)),
            (int(642 * UPSCALE), int(220 * UPSCALE)),
            (int(572 * UPSCALE), int(268 * UPSCALE)),
        ],
        fill=rgba("#d9b07d"),
    )
    image.alpha_composite(arrow.filter(ImageFilter.GaussianBlur(int(2 * UPSCALE))))

    badge = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(badge)
    draw.ellipse((int(284 * UPSCALE), int(170 * UPSCALE), int(436 * UPSCALE), int(322 * UPSCALE)), fill=rgba("#5d82e2"))
    draw.ellipse((int(300 * UPSCALE), int(186 * UPSCALE), int(420 * UPSCALE), int(306 * UPSCALE)), fill=rgba("#ffffff", 34))
    draw.line(
        [
            (int(334 * UPSCALE), int(248 * UPSCALE)),
            (int(358 * UPSCALE), int(274 * UPSCALE)),
            (int(394 * UPSCALE), int(222 * UPSCALE)),
        ],
        fill=rgba("#ffffff"),
        width=int(16 * UPSCALE),
        joint="curve",
    )
    image.alpha_composite(badge.filter(ImageFilter.GaussianBlur(int(1 * UPSCALE))))

    final = image.resize((860, 760), Image.Resampling.LANCZOS)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    final.save(OUTPUT_DIR / "hero-node-sync.png")


def bezier_points(
    start: tuple[int, int],
    control1: tuple[int, int],
    control2: tuple[int, int],
    end: tuple[int, int],
    steps: int = 180,
) -> list[tuple[int, int]]:
    points: list[tuple[int, int]] = []
    for index in range(steps + 1):
        t = index / steps
        x = (
            (1 - t) ** 3 * start[0]
            + 3 * (1 - t) ** 2 * t * control1[0]
            + 3 * (1 - t) * t**2 * control2[0]
            + t**3 * end[0]
        )
        y = (
            (1 - t) ** 3 * start[1]
            + 3 * (1 - t) ** 2 * t * control1[1]
            + 3 * (1 - t) * t**2 * control2[1]
            + t**3 * end[1]
        )
        points.append((int(x), int(y)))
    return points


def make_flow_scene() -> None:
    size = (2200, 1240)
    image = Image.new("RGBA", size, (0, 0, 0, 0))

    def draw_trail(points: list[tuple[int, int]], color: tuple[int, int, int, int], width: int, blur: int) -> None:
        trail = Image.new("RGBA", size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(trail)
        draw.line(points, fill=color, width=width, joint="curve")
        image.alpha_composite(trail.filter(ImageFilter.GaussianBlur(blur)))

    trails = [
        (
            bezier_points((84, 784), (346, 640), (636, 676), (1120, 810)),
            rgba("#f5ddba", 166),
            18,
            18,
        ),
        (
            bezier_points((1044, 810), (1384, 884), (1700, 756), (2084, 694)),
            rgba("#c8dcff", 150),
            18,
            18,
        ),
        (
            bezier_points((76, 662), (418, 556), (816, 582), (1186, 690)),
            rgba("#ffffff", 188),
            10,
            12,
        ),
        (
            bezier_points((1022, 700), (1396, 780), (1628, 710), (2100, 602)),
            rgba("#ffffff", 170),
            10,
            12,
        ),
        (
            bezier_points((88, 922), (412, 816), (742, 860), (1098, 1004)),
            rgba("#f2e3ce", 120),
            8,
            14,
        ),
        (
            bezier_points((1070, 1002), (1450, 1128), (1742, 1018), (2120, 930)),
            rgba("#d8e6ff", 112),
            8,
            14,
        ),
    ]

    for points, color, width, blur in trails:
        draw_trail(points, color, width, blur)

    grid = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(grid)
    for idx, value in enumerate((120, 180, 260, 220, 300)):
        x = 126 + idx * 82
        draw.rounded_rectangle((x, 1082 - value, x + 42, 1082), radius=12, fill=rgba("#cad6ea", 82))
    draw.line([(112, 1096), (340, 986), (536, 1032), (710, 940)], fill=rgba("#e0b98a", 104), width=6)

    for idx, value in enumerate((86, 142, 204, 246, 168, 284)):
        x = 1600 + idx * 62
        draw.rounded_rectangle((x, 1100 - value, x + 30, 1100), radius=10, fill=rgba("#c6d5ee", 80))
    image.alpha_composite(grid.filter(ImageFilter.GaussianBlur(2)))

    for center, color in (
        ((250, 280), rgba("#f6dfbc", 110)),
        ((1810, 180), rgba("#c9ddff", 122)),
        ((1128, 622), rgba("#ffffff", 140)),
    ):
        add_soft_circle(image, center, 160, color, 72)

    image.save(OUTPUT_DIR / "hero-flow-scene.png")


def make_composition_preview() -> None:
    background = Image.new("RGBA", (2048, 1310), rgba("#f7f4ed"))
    warm = horizontal_gradient(background.size, rgba("#fff4e2"), rgba("#eef4ff"))
    background.alpha_composite(warm)
    add_soft_circle(background, (260, 230), 280, rgba("#f6dfbc", 122), 120)
    add_soft_circle(background, (1760, 220), 300, rgba("#d3e5ff", 124), 120)

    flow = Image.open(OUTPUT_DIR / "hero-flow-scene.png").convert("RGBA")
    flow = flow.resize((2048, 1180), Image.Resampling.LANCZOS)
    background.alpha_composite(flow, (0, 78))

    asset_positions = [
        ("hero-figure-organizer.png", (48, 220), 250),
        ("hero-figure-team.png", (292, 702), 264),
        ("hero-node-sync.png", (824, 592), 344),
        ("hero-figure-review.png", (1472, 720), 262),
        ("hero-figure-feedback.png", (1740, 222), 246),
    ]

    for filename, position, width in asset_positions:
        asset = Image.open(OUTPUT_DIR / filename).convert("RGBA")
        ratio = width / asset.width
        resized = asset.resize((width, int(asset.height * ratio)), Image.Resampling.LANCZOS)
        place_with_shadow(background, resized, position, rgba("#5f6f8a", 72), 18, (0, 18))

    background.save(OUTPUT_DIR / "hero-composition-preview.png")


def main() -> None:
    variants = {
        "hero-figure-organizer": {
            "hair_top": rgba("#2a3248"),
            "hair_bottom": rgba("#1e2535"),
            "hair_style": "bob",
            "body_top": rgba("#31374a"),
            "body_bottom": rgba("#202739"),
            "trim": rgba("#d57a71"),
            "accessory": "tablet",
            "arm_left_angle": 10,
            "arm_right_angle": -14,
        },
        "hero-figure-team": {
            "hair_top": rgba("#db8b4c"),
            "hair_bottom": rgba("#ae6636"),
            "hair_style": "short",
            "body_top": rgba("#3f6bd8"),
            "body_bottom": rgba("#284faa"),
            "trim": None,
            "accessory": "phone",
            "arm_left_angle": 18,
            "arm_right_angle": -6,
        },
        "hero-figure-review": {
            "hair_top": rgba("#d98d52"),
            "hair_bottom": rgba("#b06634"),
            "hair_style": "side_part",
            "body_top": rgba("#416bcf"),
            "body_bottom": rgba("#2d58b3"),
            "trim": None,
            "accessory": "clipboard",
            "arm_left_angle": 16,
            "arm_right_angle": -8,
        },
        "hero-figure-feedback": {
            "hair_top": rgba("#6f5647"),
            "hair_bottom": rgba("#4b372f"),
            "hair_style": "short_wave",
            "body_top": rgba("#908173"),
            "body_bottom": rgba("#6b6058"),
            "trim": None,
            "accessory": "paper",
            "arm_left_angle": 18,
            "arm_right_angle": -12,
        },
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, variant in variants.items():
        make_character_asset(name, variant)
    make_center_node()
    make_flow_scene()
    make_composition_preview()


if __name__ == "__main__":
    main()
