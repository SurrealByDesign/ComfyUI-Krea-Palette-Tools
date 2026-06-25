"""ComfyUI-Krea-Palette-Tools node registration."""

try:
    from .nodes.palette_extractor import KreaPaletteExtractor
    from .nodes.palette_style_reference import KreaPaletteStyleReference
    from .nodes.palette_to_prompt_text import KreaPaletteToPromptText
except ImportError:
    # Fallback for tooling (e.g. pytest's package collection) that imports this
    # file without ComfyUI's package context, so there's no "." to resolve.
    from nodes.palette_extractor import KreaPaletteExtractor
    from nodes.palette_style_reference import KreaPaletteStyleReference
    from nodes.palette_to_prompt_text import KreaPaletteToPromptText

NODE_CLASS_MAPPINGS = {
    "KreaPaletteExtractor": KreaPaletteExtractor,
    "KreaPaletteStyleReference": KreaPaletteStyleReference,
    "KreaPaletteToPromptText": KreaPaletteToPromptText,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "KreaPaletteExtractor": "Krea Palette Extractor",
    "KreaPaletteStyleReference": "Krea Palette Style Reference",
    "KreaPaletteToPromptText": "Krea Palette To Prompt Text",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
