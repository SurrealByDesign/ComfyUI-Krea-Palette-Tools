"""Tests for KreaPaletteExtractor: mode dropdown (most_populous vs vibrancy-scored
modes), dedup, and graceful fallback."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import torch

from nodes.palette_extractor import KreaPaletteExtractor, MODES
from utils.color_utils import hex_to_rgb

H = W = 64


def _node():
    return KreaPaletteExtractor()


def _light_gray_bg_with_red_patch():
    """Mostly light gray (dominant by frequency) with a small vivid red patch."""
    img = np.full((H, W, 3), 200 / 255.0, dtype=np.float32)
    img[24:40, 24:40, :] = 0.0
    img[24:40, 24:40, 0] = 1.0
    return torch.from_numpy(img)[None, ...]


def test_most_populous_ranks_background_first():
    image = _light_gray_bg_with_red_patch()
    colors = json.loads(_node().extract(image, 8, 10.0, "most_populous")[0])
    r, g, b = hex_to_rgb(colors[0])
    assert abs(r - g) < 40 and abs(g - b) < 40  # grayish


def test_vibrant_mode_surfaces_accent_over_frequent_background():
    image = _light_gray_bg_with_red_patch()
    colors = json.loads(_node().extract(image, 8, 10.0, "vibrant")[0])
    r, g, b = hex_to_rgb(colors[0])
    assert r > 180 and g < 70 and b < 70


def test_muted_mode_deprioritizes_vivid():
    image = _light_gray_bg_with_red_patch()
    colors = json.loads(_node().extract(image, 8, 10.0, "muted")[0])
    r, g, b = hex_to_rgb(colors[0])
    assert not (r > 180 and g < 70 and b < 70)


def test_all_modes_run_without_error():
    image = _light_gray_bg_with_red_patch()
    for mode in MODES:
        palette_json, preview, count = _node().extract(image, 8, 10.0, mode)
        colors = json.loads(palette_json)
        assert len(colors) == count >= 1
        assert preview.shape[0] == 1


def test_output_format():
    image = _light_gray_bg_with_red_patch()
    palette_json, preview, count = _node().extract(image, 8, 10.0, "most_populous")
    for c in json.loads(palette_json):
        hex_to_rgb(c)
    assert isinstance(preview, torch.Tensor) and preview.shape[3] == 3


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"{name}: OK")
    print("All palette_extractor tests passed.")
