"""KreaPaletteStyleReference node.

Packages an extracted palette swatch-strip IMAGE as one entry of Krea 2's
`image_style_references` request field: {"imageUrl": ..., "strength": ...}.
Krea has no structured color-palette JSON schema (unlike Ideogram 4's
style_description); the documented way to bias generation toward a palette
is via a style-reference image, so this node hands off the swatch image
itself rather than re-encoding the colors as text.

This node does not upload the image or call the Krea API — it returns the
strength-tagged payload dict for an upstream HTTP/upload node to consume,
since image_style_references expects a hosted imageUrl, not raw pixels.
"""

import json


class KreaPaletteStyleReference:
    """Wraps a palette swatch IMAGE + strength into a Krea image_style_references entry.

    Inputs:
        palette_preview: swatch strip IMAGE, typically from KreaPaletteExtractor.
        strength: reference strength per Krea's schema, -2.0 to 2.0 (negative
            repels from the reference style, default 1.0).

    Outputs:
        style_reference_image: pass-through IMAGE for an upload/HTTP node to host.
        style_reference_json: JSON string {"strength": <float>} to merge with the
            hosted imageUrl before sending as one entry of image_style_references.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "palette_preview": ("IMAGE",),
                "strength": ("FLOAT", {"default": 1.0, "min": -2.0, "max": 2.0, "step": 0.1}),
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("style_reference_image", "style_reference_json")
    FUNCTION = "build"
    CATEGORY = "Krea/Palette"

    def build(self, palette_preview, strength):
        payload = json.dumps({"strength": float(strength)})
        return (palette_preview, payload)
