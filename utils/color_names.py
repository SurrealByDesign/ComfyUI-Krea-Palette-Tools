"""Curated descriptive color names for translating extracted hex colors into
natural-language prompt clauses.

Pure nearest-match lookup (Delta-E in LAB space) against a fixed table --
no model calls, no network, no API. This is what lets the palette-to-text
path stay completely free and local: turning "#E53935" into "vivid red" is
just color math, not a generation request.
"""

try:
    from .color_utils import hex_to_rgb, rgb_to_lab, delta_e
except ImportError:
    from color_utils import hex_to_rgb, rgb_to_lab, delta_e

# (name, hex) pairs chosen for natural-sounding prompt phrases rather than
# exhaustive CSS coverage -- skews toward descriptive two-word names that
# read well inside a generation prompt.
NAMED_COLORS = [
    ("vivid red", "#E53935"),
    ("coral", "#FF7F66"),
    ("rust orange", "#B5482B"),
    ("warm tan", "#C8A878"),
    ("golden yellow", "#E8B923"),
    ("mustard", "#C9A227"),
    ("olive", "#7D7A3A"),
    ("sage green", "#8FA37E"),
    ("forest green", "#2E5339"),
    ("teal", "#2E7378"),
    ("sky blue", "#7EC8E3"),
    ("slate blue", "#5D5882"),
    ("navy", "#1B2A4A"),
    ("lavender", "#B6A6CA"),
    ("plum", "#6E3B5C"),
    ("magenta", "#9B2D6B"),
    ("blush pink", "#E8A6A0"),
    ("burgundy", "#5C1A1A"),
    ("charcoal", "#2E2B28"),
    ("stone gray", "#9F9A8E"),
    ("warm gray", "#7A766E"),
    ("cream", "#F1E9D8"),
    ("ivory", "#F8F4E8"),
    ("taupe", "#9C8770"),
    ("chocolate brown", "#4A2E1E"),
    ("black", "#101010"),
    ("white", "#F7F7F5"),
]

_NAMED_LAB = [(name, rgb_to_lab(hex_to_rgb(h))) for name, h in NAMED_COLORS]


def nearest_color_name(hex_color: str) -> str:
    """Return the closest descriptive name (CIE76 Delta-E in LAB) for a hex color."""
    target_lab = rgb_to_lab(hex_to_rgb(hex_color))
    best_name, best_dist = _NAMED_LAB[0][0], float("inf")
    for name, lab in _NAMED_LAB:
        dist = delta_e(target_lab, lab)
        if dist < best_dist:
            best_name, best_dist = name, dist
    return best_name
