"""Tests for KreaPaletteStyleReference: payload shape and pass-through image."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import torch

from nodes.palette_style_reference import KreaPaletteStyleReference


def test_build_returns_strength_payload_and_passthrough_image():
    image = torch.zeros((1, 4, 4, 3))
    out_image, payload_json = KreaPaletteStyleReference().build(image, 1.5)
    assert out_image is image
    payload = json.loads(payload_json)
    assert payload == {"strength": 1.5}


def test_strength_bounds_pass_through_as_float():
    image = torch.zeros((1, 4, 4, 3))
    _, payload_json = KreaPaletteStyleReference().build(image, -2.0)
    assert json.loads(payload_json)["strength"] == -2.0


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"{name}: OK")
    print("All palette_style_reference tests passed.")
