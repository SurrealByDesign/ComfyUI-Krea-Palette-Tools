"""ComfyUI-Krea-Palette-Tools node registration."""

try:
    from .nodes.palette_extractor import KreaPaletteExtractor
    from .nodes.palette_style_reference import KreaPaletteStyleReference
except ImportError:
    # Fallback for tooling (e.g. pytest's package collection) that imports this
    # file without ComfyUI's package context, so there's no "." to resolve.
    from nodes.palette_extractor import KreaPaletteExtractor
    from nodes.palette_style_reference import KreaPaletteStyleReference

NODE_CLASS_MAPPINGS = {
    "KreaPaletteExtractor": KreaPaletteExtractor,
    "KreaPaletteStyleReference": KreaPaletteStyleReference,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "KreaPaletteExtractor": "Krea Palette Extractor",
    "KreaPaletteStyleReference": "Krea Palette Style Reference",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
