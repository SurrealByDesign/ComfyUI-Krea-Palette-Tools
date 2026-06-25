# ComfyUI Krea Palette Tools

*Pick the palette. Hand Krea a reference, not a hex-code spreadsheet.*

![Same reference image, palette extracted four ways — most_populous, vibrant, muted, and dark_vibrant — shown as four labeled swatch strips side by side](assets/palette_modes_example.png)

![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)
![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![ComfyUI custom nodes](https://img.shields.io/badge/ComfyUI-custom%20nodes-6f42c1.svg)
![Extra dependency: scikit-learn](https://img.shields.io/badge/extra%20dep-scikit--learn-orange.svg)

## Table of Contents

- [The Problem](#the-problem)
- [The Solution](#the-solution)
- [Features](#features)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Workflow Diagram](#workflow-diagram)
- [Nodes](#nodes)
- [Examples](#examples)
- [Showcase](#showcase)
- [Typical Use Cases](#typical-use-cases)
- [Design Notes](#design-notes)
- [Testing](#testing)
- [FAQ](#faq)
- [Related Projects](#related-projects)
- [License](#license)

## The Problem

Krea 2 has no structured color-palette field in its prompt schema — there's
no JSON slot where you drop an ordered hex array the way you can with
Ideogram 4. The documented way to steer a Krea 2 generation toward a
specific palette is `image_style_references`: up to 10 reference images,
each with a tunable strength, that condition the output's look. In other
words, the "palette" Krea actually wants is an *image*, not a hex list —
and picking those colors by hand, then mocking up a swatch image to hand
Krea, is tedious busywork that has nothing to do with the creative
decision you're actually trying to make.

## The Solution

This toolkit extracts a palette from a reference image automatically and
renders it back out as a clean swatch image — ready to feed Krea as a
style reference, or to translate into prompt text for a local generation.
You pick the reference and the ranking mode; the nodes handle the color
math.

## Features

- **Automatic palette extraction** from any reference image (k-means
  clustering, perceptually-aware deduplication).
- **Seven ranking modes** — raw frequency, or vibrancy-scored toward
  vibrant / muted / light / dark targets — so a small accent color isn't
  buried under a dull background when that's not what you want.
- **Krea-native output.** Produces a swatch image shaped for Krea 2's
  `image_style_references`, not a JSON fragment that Krea can't consume.
- **Works free and local**, or paid and cloud-hosted — your choice (see
  [FAQ](#faq)).
- **Composable nodes.** Wires into any ComfyUI graph; no monolithic
  do-everything node.

## Quick Start

1. Install the package (see [Installation](#installation)).
2. Open [`workflows/palette_reference_workflow.json`](workflows/palette_reference_workflow.json)
   via ComfyUI's **Workflow → Open** menu.
3. Point the `LoadImage` node at your own reference image and hit Run.
4. You now have a labeled swatch-strip image — your starting palette.

From here, wire that swatch into `KreaPaletteStyleReference` to package it
for a real Krea 2 generation (see [Nodes](#nodes) and
[Examples](#examples)).

## Installation

Clone (or copy) this repository into your ComfyUI `custom_nodes/` directory
and restart ComfyUI:

```
cd ComfyUI/custom_nodes
git clone https://github.com/SurrealByDesign/ComfyUI-Krea-Palette-Tools
```

The only extra dependency is **scikit-learn** (used for k-means clustering),
which is not part of a base ComfyUI install. ComfyUI-Manager installs it
automatically from [`requirements.txt`](requirements.txt); to install it by
hand into ComfyUI's Python:

```
pip install scikit-learn
```

The package also uses `torch`, `numpy`, and `Pillow`, but those ship with
ComfyUI and are **deliberately not** listed in `requirements.txt` —
reinstalling them (torch especially) can pull a build that doesn't match
your ComfyUI/CUDA setup and break the install. After restarting, the two
nodes appear in the node menu under **`Krea/Palette`**.

`requires-python = ">=3.10"` in [`pyproject.toml`](pyproject.toml) is the
floor, not a guarantee for every ComfyUI version — open an issue if
something doesn't load on yours.

## Workflow Diagram

```
Reference Image
       │
       ▼
Palette Extraction        KreaPaletteExtractor
       │                  (k-means + Delta-E dedup, mode-ranked)
       ▼
Palette Swatch             palette_preview (labeled IMAGE)
       │
       ▼
Krea Style Reference       KreaPaletteStyleReference
       │                  (+ Krea's own Style Reference / Image
       │                   partner nodes for a real generation)
       ▼
Generated Image
```

The first three steps are always free and local. The last step branches —
see [FAQ](#faq) for the free-local vs. paid-cloud paths.

## Nodes

### Krea Palette Extractor (`KreaPaletteExtractor`)

Takes a reference image, runs k-means clustering, removes near-duplicate
colors with Delta-E filtering, and returns colors ordered per the selected
`mode`.

**Inputs**

| Name | Type | Default | Notes |
| --- | --- | --- | --- |
| `image` | IMAGE | — | reference image |
| `num_colors` | INT | 8 | range 2–16 |
| `min_delta_e` | FLOAT | 10.0 | minimum perceptual distance to keep a color distinct |
| `mode` | COMBO | `most_populous` | `most_populous` / `vibrant` / `light_vibrant` / `dark_vibrant` / `muted` / `light_muted` / `dark_muted` |

**Outputs**

| Name | Type | Notes |
| --- | --- | --- |
| `palette_json` | STRING | hex array, ordered per mode |
| `palette_preview` | IMAGE | labeled swatch strip |
| `color_count` | INT | colors remaining after dedup |

### Krea Palette Style Reference (`KreaPaletteStyleReference`)

Wraps a palette swatch image and a strength value into the payload shape
for one Krea 2 `image_style_references` entry. It does not upload the
image or call the Krea API itself — pair it with an HTTP/upload node that
hosts the swatch image and merges in the resulting `imageUrl`.

**Inputs**

| Name | Type | Default | Notes |
| --- | --- | --- | --- |
| `palette_preview` | IMAGE | — | typically from `KreaPaletteExtractor` |
| `strength` | FLOAT | 1.0 | range -2.0–2.0; negative repels from the reference style |

**Outputs**

| Name | Type | Notes |
| --- | --- | --- |
| `style_reference_image` | IMAGE | pass-through, for an upload node |
| `style_reference_json` | STRING | `{"strength": <float>}`, merge with the hosted `imageUrl` |

## Examples

[`workflows/palette_reference_workflow.json`](workflows/palette_reference_workflow.json)
is the minimal pipeline:

```
LoadImage -> KreaPaletteExtractor
```

`palette_preview` is the swatch-strip image; wire it into
`KreaPaletteStyleReference` to package it for Krea 2's
`image_style_references`:

```
LoadImage -> KreaPaletteExtractor (mode=vibrant) -> KreaPaletteStyleReference (strength=1.0)
                                              \-> PreviewImage (swatch strip)
```

`KreaPaletteStyleReference`'s `style_reference_image` output still needs to
reach Krea as a hosted URL — wire it into whatever upload/HTTP node your
Krea integration uses, merge the resulting `imageUrl` into
`style_reference_json`, and add that as one entry of the request's
`image_style_references` array.

A set of further ready-to-load workflows lives under
[`workflows/`](workflows/):

| Workflow | What it shows | Nodes wired together |
| --- | --- | --- |
| [`showcase_01_palette_to_style_reference.json`](workflows/showcase_01_palette_to_style_reference.json) | The flagship chain: a reference image becomes a Krea-ready style-reference payload (swatch image + strength JSON). | Extractor → Style Reference |
| [`showcase_02_mode_comparison.json`](workflows/showcase_02_mode_comparison.json) | Same image, four rankings side by side — `most_populous` / `vibrant` / `muted` / `dark_vibrant` — for picking a mode before committing to one. | 4× Extractor → 4× PreviewImage |
| [`showcase_03_positive_vs_negative_strength.json`](workflows/showcase_03_positive_vs_negative_strength.json) | One extracted palette fed into two Style Reference nodes at `strength=1.5` and `strength=-1.5`, to compare pulling toward vs. repelling from a palette. | Extractor → 2× Style Reference |

Load any of them via ComfyUI's **Workflow → Open** menu and point the
`LoadImage` node(s) at your own reference. Where a workflow displays a raw
JSON string it uses the optional `ShowText|pysssss` node (from
[ComfyUI-Custom-Scripts](https://github.com/pythongosssss/ComfyUI-Custom-Scripts))
— swap it for any STRING-display node, or delete it; the core pipeline
doesn't depend on it. All swatch previews use the stock `PreviewImage`
node.

## Showcase

The shortest way to see the whole idea:

**Reference → Palette → Result**

1. **Reference** — any image with the colors you want (a mood board, a
   product photo, concept art).
2. **Palette** — `KreaPaletteExtractor` reduces it to a labeled swatch
   strip, ranked by the mode you choose:

   ![Same reference image, palette extracted four ways](assets/palette_modes_example.png)

3. **Result** — that palette drives the generation. Below, the *same*
   prompt and seed produced two different rooms purely by changing the
   color clause derived from two different extracted palettes (vibrant vs.
   muted):

   ![Krea 2 Turbo colorway study: same seed and scene prompt, only the color-palette clause changed — vibrant palette (vivid red, coral, sage green) vs. muted palette (sage green, tan, stone gray)](assets/krea_colorway_study.png)

## Typical Use Cases

- **Match an existing brand palette** — extract from a logo or style
  guide image instead of eyeballing hex codes.
- **Generate alternate colorways** — same composition, different palette,
  by swapping only the extracted swatch or its derived prompt clause.
- **Extract palettes from concept art** — pull a scene's mood into a
  reusable swatch for later generations.
- **Maintain visual consistency across generations** — reuse one
  extracted palette as a style reference across an entire shoot or
  series.
- **Build reusable style references** — save a `palette_preview` swatch
  once, reuse it across many Krea 2 generations.

## Design Notes

- **Delta-E, not RGB distance.** Two colors that are mathematically close
  in RGB can look wildly different to the eye (and vice versa). All
  deduplication uses CIE76 Delta-E in LAB space (see
  [`utils/color_utils.py`](utils/color_utils.py)).
- **Fails gracefully.** Extraction falls back to a flat gray (`#808080`)
  swatch on a bad or degenerate image (single color, tiny image, parse
  errors) rather than crashing the workflow.
- **Image, not JSON, is the interchange format.** Krea 2's
  `image_style_references` takes a hosted image URL, not a hex list — so
  unlike the Ideogram-facing tools in the sibling project, there's no
  "palette → JSON schema" node here. The swatch-strip image *is* the
  payload.

## Testing

Run the test suite from the package root:

```
pytest
```

or run either test file directly:

```
python tests/test_palette_extractor.py        # mode dropdown ranking, dedup, fallbacks
python tests/test_palette_style_reference.py  # strength payload shape, pass-through image
python tests/test_workflows.py                 # workflow JSONs match node signatures, no dangling links
```

## FAQ

**Can I use this locally, for free?**
Yes. The extraction nodes (`KreaPaletteExtractor`,
`KreaPaletteStyleReference`) are pure local image processing — no network
calls, no cost, ever. Generating an actual image from the palette can also
stay free and local if you translate the extracted hex colors into a text
clause and feed it to your own local Krea 2 checkpoint (see the
[Showcase](#showcase) image above for exactly this).

**Do I need the Krea API?**
Only if you want the palette to drive a generation via Krea's hosted
`image_style_references` feature. That path calls Krea's cloud API and is
metered per generation. The free local path (translating the palette into
prompt text) doesn't touch the API at all.

**Do I need Comfy Partner Nodes?**
Only for the cloud path — `Krea 2 Style Reference` and `Krea 2 Image` are
Comfy Partner Nodes that call Krea's hosted service. They're unrelated to
this package's own nodes, which work with or without them installed.

**Can I use custom upload nodes?**
Yes. `KreaPaletteStyleReference` deliberately doesn't upload anything
itself — it just produces the swatch image and the strength payload.
Wire its `style_reference_image` output into whatever HTTP/upload node
your own Krea integration already uses.

## Related Projects

This package is one half of a two-repo Surreal By Design palette-tooling
set — same color-math core, two different prompting philosophies:

- **[ComfyUI-Ideogram-Palette-and-Prompt-Tools](https://github.com/SurrealByDesign/ComfyUI-Ideogram-Palette-and-Prompt-Tools)**
  — JSON-first. Extracts palettes and assembles them into Ideogram 4's
  structured `style_description` prompt schema.
- **ComfyUI Krea Palette Tools** (this repo) — image-first. Extracts
  palettes and renders them as swatch images for Krea 2's
  `image_style_references` style-reference workflow.

The k-means/Delta-E/LAB extraction core here was forked from the Ideogram
repo's `utils/` and is currently maintained independently in each.

## License

Released under the [MIT License](LICENSE).
