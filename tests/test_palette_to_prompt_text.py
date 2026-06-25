"""Tests for KreaPaletteToPromptText: nearest-name lookup, grammar joining,
dedup, max_colors capping, template substitution, and fallback on bad input."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from nodes.palette_to_prompt_text import KreaPaletteToPromptText
from utils.color_names import nearest_color_name


def _node():
    return KreaPaletteToPromptText()


def test_single_color():
    palette = json.dumps(["#E53935"])
    text, = _node().build(palette, 4, "{colors}")
    assert text == "vivid red"


def test_two_colors_joined_with_and():
    palette = json.dumps(["#E53935", "#8FA37E"])
    text, = _node().build(palette, 4, "{colors}")
    assert text == "vivid red and sage green"


def test_three_or_more_colors_use_oxford_comma():
    palette = json.dumps(["#E53935", "#8FA37E", "#C8A878"])
    text, = _node().build(palette, 4, "{colors}")
    assert text == "vivid red, sage green, and warm tan"


def test_dedup_repeated_nearest_names():
    # Two near-identical reds should collapse to a single name.
    palette = json.dumps(["#E53935", "#E43834", "#8FA37E"])
    text, = _node().build(palette, 4, "{colors}")
    assert text == "vivid red and sage green"


def test_max_colors_caps_input():
    palette = json.dumps(["#E53935", "#8FA37E", "#C8A878", "#1B2A4A"])
    text, = _node().build(palette, 2, "{colors}")
    assert text == "vivid red and sage green"


def test_template_substitution():
    palette = json.dumps(["#E53935"])
    text, = _node().build(palette, 4, "color palette of {colors}, soft lighting")
    assert text == "color palette of vivid red, soft lighting"


def test_invalid_json_falls_back():
    text, = _node().build("not json", 4, "{colors}")
    assert text == "neutral gray"


def test_empty_array_falls_back():
    text, = _node().build("[]", 4, "{colors}")
    assert text == "neutral gray"


def test_nearest_color_name_is_deterministic():
    assert nearest_color_name("#E53935") == "vivid red"
    assert nearest_color_name("#101010") == "black"


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"{name}: OK")
    print("All palette_to_prompt_text tests passed.")
