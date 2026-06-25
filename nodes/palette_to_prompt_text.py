"""KreaPaletteToPromptText node.

Translates an extracted hex palette into a natural-language color clause,
so a free, local Krea 2 generation can be driven purely through prompt
text -- no Krea API, no Comfy Partner Nodes, no manual color-naming.
"""

import json

try:
    from ..utils.color_names import nearest_color_name
except ImportError:
    from utils.color_names import nearest_color_name

FALLBACK_TEXT = "neutral gray"


def _join_names(names):
    if not names:
        return FALLBACK_TEXT
    if len(names) == 1:
        return names[0]
    if len(names) == 2:
        return f"{names[0]} and {names[1]}"
    return ", ".join(names[:-1]) + f", and {names[-1]}"


class KreaPaletteToPromptText:
    """Converts a palette_json hex array into a comma-joined color-name
    phrase, deduplicating repeated names and capping at max_colors.

    Inputs:
        palette_json: hex array string, typically from KreaPaletteExtractor.
        max_colors: maximum number of color names to include (1-8, default 4).
        template: output template; the literal "{colors}" is replaced with
            the joined color-name phrase.

    Outputs:
        text: the formatted clause, e.g. "vivid red, sage green, and warm
            tan" (or the full templated string if `template` was customized).
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "palette_json": ("STRING", {"forceInput": True}),
                "max_colors": ("INT", {"default": 4, "min": 1, "max": 8}),
                "template": ("STRING", {"default": "{colors}"}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "build"
    CATEGORY = "Krea/Palette"

    def build(self, palette_json, max_colors, template):
        try:
            hex_colors = json.loads(palette_json)
            if not isinstance(hex_colors, list):
                hex_colors = []
        except (json.JSONDecodeError, TypeError):
            hex_colors = []

        names = []
        for hex_color in hex_colors[:max_colors]:
            try:
                name = nearest_color_name(hex_color)
            except (ValueError, TypeError):
                continue
            if name not in names:
                names.append(name)

        text = template.replace("{colors}", _join_names(names))
        return (text,)
