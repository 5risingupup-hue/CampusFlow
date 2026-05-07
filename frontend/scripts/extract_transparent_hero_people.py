from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage


ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = ROOT / "src" / "assets" / "hero"
SOURCE = ASSET_DIR / "reference-people.png"
PADDING = 26


def build_background_palette(crop: np.ndarray) -> np.ndarray:
    border = np.concatenate(
        [
            crop[0, :, :],
            crop[-1, :, :],
            crop[:, 0, :],
            crop[:, -1, :]
        ],
        axis=0
    )
    return np.unique((np.round(border / 8) * 8).astype(np.uint8), axis=0).astype(np.int16)


def compute_distance_mask(crop: np.ndarray, palette: np.ndarray, threshold: float) -> np.ndarray:
    flat = crop.reshape(-1, 3).astype(np.int32)
    min_distance_sq: np.ndarray | None = None

    for color in palette:
        distance_sq = np.sum((flat - color.astype(np.int32)) ** 2, axis=1)
        min_distance_sq = distance_sq if min_distance_sq is None else np.minimum(min_distance_sq, distance_sq)

    return np.sqrt(min_distance_sq.astype(np.float32)).reshape(crop.shape[:2]) > threshold


def isolate_largest_component(mask: np.ndarray) -> np.ndarray:
    labels, count = ndimage.label(mask)
    if count == 0:
        raise RuntimeError("Unable to detect a foreground figure from the crop box.")

    sizes = np.bincount(labels.ravel())
    sizes[0] = 0
    return labels == sizes.argmax()


def extract_foreground(
    source: Image.Image,
    crop_box: tuple[int, int, int, int],
    *,
    threshold: float
) -> Image.Image:
    crop = np.array(source.crop(crop_box).convert("RGB"))
    palette = build_background_palette(crop)
    mask = compute_distance_mask(crop, palette, threshold)

    mask = ndimage.binary_opening(mask, structure=np.ones((3, 3)))
    mask = ndimage.binary_closing(mask, structure=np.ones((5, 5)))
    mask = ndimage.binary_fill_holes(mask)
    mask = isolate_largest_component(mask)

    alpha = Image.fromarray((mask.astype(np.uint8) * 255), "L").filter(ImageFilter.GaussianBlur(1.2))
    result = Image.fromarray(np.dstack([crop, np.array(alpha)]), "RGBA")

    bbox = alpha.getbbox()
    if not bbox:
        raise RuntimeError("Unable to calculate alpha bounds for the extracted figure.")

    result = result.crop(bbox)
    canvas = Image.new(
        "RGBA",
        (result.width + PADDING * 2, result.height + PADDING * 2),
        (0, 0, 0, 0)
    )
    canvas.alpha_composite(result, (PADDING, PADDING))
    return canvas


def main() -> None:
    if not SOURCE.exists():
        raise FileNotFoundError(f"Missing source image: {SOURCE}")

    source = Image.open(SOURCE)

    crops = {
        "hero-figure-organizer.png": {
            "box": (110, 70, 770, 1500),
            "threshold": 18
        },
        "hero-figure-team.png": {
            "box": (720, 260, 1500, 1530),
            "threshold": 18
        },
        "hero-figure-review.png": {
            "box": (1470, 280, 2090, 1530),
            "threshold": 18
        },
        "hero-figure-feedback.png": {
            "box": (2060, 60, 2710, 1500),
            "threshold": 10
        }
    }

    for filename, config in crops.items():
        extract_foreground(source, config["box"], threshold=config["threshold"]).save(ASSET_DIR / filename)


if __name__ == "__main__":
    main()
