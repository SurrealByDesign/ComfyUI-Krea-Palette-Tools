"""KreaPaletteExtractor node.

Extracts a color palette from an image via k-means clustering, deduplicated
using Delta-E distance in LAB space. A `mode` dropdown selects how the
clusters are ordered: raw frequency (most_populous) or vibrancy-scored
(vibrant/muted and their light/dark variants), Android Palette API-style.
"""

import json

import numpy as np
import torch
from PIL import Image

try:
    from ..utils.extract import clusters_from_pixels, RESIZE_DIM
    from ..utils.color_utils import rgb_to_hex, rgb_to_lab, delta_e, rgb_to_hsl
    from ..utils.preview_utils import render_swatch_strip
except ImportError:
    from utils.extract import clusters_from_pixels, RESIZE_DIM
    from utils.color_utils import rgb_to_hex, rgb_to_lab, delta_e, rgb_to_hsl
    from utils.preview_utils import render_swatch_strip

FALLBACK_HEX = "#808080"

# Target (saturation, lightness) per mode — the Android Palette target values.
# most_populous has no target; it orders by cluster population only.
TARGETS = {
    "vibrant": (1.0, 0.5),
    "light_vibrant": (1.0, 0.74),
    "dark_vibrant": (1.0, 0.26),
    "muted": (0.3, 0.5),
    "light_muted": (0.3, 0.74),
    "dark_muted": (0.3, 0.26),
}
MODES = ["most_populous"] + list(TARGETS.keys())

# Scoring weights (Android Palette: saturation 0.24, luma 0.52, population 0.24).
W_SAT, W_LIGHT, W_POP = 0.24, 0.52, 0.24


def _tensor_to_pil(image_tensor: torch.Tensor) -> Image.Image:
    """Convert a ComfyUI IMAGE tensor (B, H, W, C), float 0-1, to a PIL RGB image (first frame)."""
    img = image_tensor[0].cpu().numpy()
    img = np.clip(img, 0.0, 1.0)
    img = (img * 255.0).astype(np.uint8)
    return Image.fromarray(img, mode="RGB")


def _ordered_hex(centroids, counts, mode, min_delta_e):
    """Order clusters per `mode`, then Delta-E dedup. centroids/counts must already
    be sorted most-populous first (as returned by clusters_from_pixels)."""
    if len(centroids) == 0:
        return []

    if mode == "most_populous":
        ordered_rgb = list(centroids)
    else:
        target_s, target_l = TARGETS.get(mode, TARGETS["vibrant"])
        max_count = float(max(counts)) if len(counts) else 1.0
        scored = []
        for rgb, count in zip(centroids, counts):
            _, s, lightness = rgb_to_hsl(rgb)
            score = (
                W_SAT * (1.0 - abs(s - target_s))
                + W_LIGHT * (1.0 - abs(lightness - target_l))
                + W_POP * (count / max_count if max_count else 0.0)
            )
            scored.append((score, rgb))
        scored.sort(key=lambda item: -item[0])
        ordered_rgb = [rgb for _score, rgb in scored]

    survivors_rgb, survivors_lab = [], []
    for rgb in ordered_rgb:
        lab = rgb_to_lab(rgb)
        if any(delta_e(lab, kept) < min_delta_e for kept in survivors_lab):
            continue
        survivors_rgb.append(rgb)
        survivors_lab.append(lab)
    return [rgb_to_hex(rgb) for rgb in survivors_rgb]


class KreaPaletteExtractor:
    """Extracts a color palette from an image, with a mode dropdown to pick the
    ranking strategy: raw frequency, or vibrancy-scored (vibrant/muted/light/dark).

    Inputs:
        image: reference IMAGE to extract colors from.
        num_colors: target palette size (k-means cluster count).
        min_delta_e: minimum perceptual (LAB) distance required between kept colors.
        mode: most_populous / vibrant / light_vibrant / dark_vibrant / muted /
            light_muted / dark_muted.

    Outputs:
        palette_json: JSON array of hex strings, ordered per mode.
        palette_preview: horizontal swatch strip IMAGE of the extracted colors.
        color_count: number of colors actually returned after deduplication.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "num_colors": ("INT", {"default": 8, "min": 2, "max": 16}),
                "min_delta_e": ("FLOAT", {"default": 10.0, "min": 0.0, "max": 100.0, "step": 0.5}),
                "mode": (MODES, {"default": "most_populous"}),
            }
        }

    RETURN_TYPES = ("STRING", "IMAGE", "INT")
    RETURN_NAMES = ("palette_json", "palette_preview", "color_count")
    FUNCTION = "extract"
    CATEGORY = "Krea/Palette"

    def extract(self, image, num_colors, min_delta_e, mode="most_populous"):
        try:
            pil_image = _tensor_to_pil(image).resize((RESIZE_DIM, RESIZE_DIM))
            pixels = np.asarray(pil_image, dtype=np.float64).reshape(-1, 3)
            centroids, counts = clusters_from_pixels(pixels, num_colors)
            hex_colors = _ordered_hex(centroids, counts, mode, min_delta_e)
            if not hex_colors:
                hex_colors = [FALLBACK_HEX]
        except Exception:
            hex_colors = [FALLBACK_HEX]

        palette_json = json.dumps(hex_colors)
        swatch = render_swatch_strip(hex_colors)
        preview_tensor = torch.from_numpy(swatch).unsqueeze(0)

        return (palette_json, preview_tensor, len(hex_colors))
