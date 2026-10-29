# Rally identity evolution

The selected identity refines Rally's existing staggered double-slash mark. It keeps the name, forest/lime palette and directional energy, while giving the two traces consistent weight, an exact 60-degree slope and a balanced square footprint. It is an evolution of the supplied identity.

## Existing equity preserved

The exact original files are retained, byte for byte:

| Asset | Preserved copy | Original viewBox |
|---|---|---|
| Supplied application favicon: forest rounded tile, open apex and dot | `assets/brand/original/app-favicon.svg` | 32 × 32 |
| Existing standalone marketing mark: forest square and two lime slashes | `assets/brand/original/marketing-double-slash.svg` | 64 × 64 |

These are two existing Rally assets. Their difference does not establish which mark every older product or marketing surface displayed. The application source and existing `assets/rally-mark.svg` were left intact.

## Internal exploration and selection

Three grayscale concepts were built and inspected at large size and at 16, 24, 32 and 64 pixels. The user requested internal exploration and a selected identity in the completed site, so the strongest direction was selected within that scope.

| Concept file, in `assets/brand/concepts/` | Approach | Decision |
|---|---|---|
| `a-parallel-traces.svg` | Refine the existing staggered forward traces | Selected. Strongest continuity, simplest silhouette, two clear strokes at favicon size. |
| `b-open-return.svg` | An R with a deliberately open counter and a returning diagonal | Readable, but closer to a generic lettermark and a larger departure from the current silhouette. |
| `c-apex-trajectory.svg` | Evolve the application's apex and dot into a trajectory | Preserves that asset's motif, but the isolated dot is more fragile and the silhouette loses the familiar slash rhythm. |

The dedicated [Logo Design skill](https://github.com/kaankiziltug/logo-design-skill) informed exploration, SVG construction and inspection. Its fictional sports-app example “Ralli” was not used as a template. No reference logo was traced.

## Selected asset family

All files below are editable SVGs with explicit fills, meaningful groups and titles. The backgrounds are transparent unless a tile is specified.

| File, in `assets/brand/` | Dimensions / viewBox | Use |
|---|---|---|
| `rally-symbol.svg` | 256 × 256 | Forest master; identical to the explicit forest variant |
| `rally-symbol-forest.svg` | 256 × 256 | Symbol on light backgrounds |
| `rally-symbol-black.svg` | 256 × 256 | Black one-color reproduction |
| `rally-symbol-white.svg` | 256 × 256 | White one-color reproduction on dark backgrounds |
| `rally-symbol-lime.svg` | 256 × 256 | Accent symbol on forest backgrounds |
| `rally-lockup-on-light.svg` | 660 × 256 | Forest symbol and outlined Rally wordmark on a light header |
| `rally-lockup-on-dark.svg` | 660 × 256 | Lime symbol and paper wordmark on a dark header |
| `rally-wordmark-forest.svg` | 476 × 256 | Standalone outlined wordmark on light backgrounds |
| `rally-wordmark-paper.svg` | 476 × 256 | Standalone outlined wordmark on dark backgrounds |
| `rally-favicon.svg` | 256 × 256 | Lime small-size cut on a forest rounded tile |

The wordmark uses the supplied `assets/fonts/archivo-latin-variable.woff2`, instantiated at weight 650. Each Archivo glyph is an outlined path; no installed font, font fetch, text renderer or JavaScript is needed to display the lockups. Optical pair adjustments for R–a, a–l, l–l and l–y are respectively −28, −12, −12 and −8 font units. Glyphs retain their original proportions. Archivo's existing SIL Open Font License remains in `assets/fonts/LICENSE.txt`.

## Color and use

- Forest: `#182C25`.
- Lime: `#DBF268`.
- Paper: `#F3F3EC`.
- Black and white masters: `#000000` and `#FFFFFF`.

Use the light lockup on paper/white and the dark lockup on forest. Keep the two traces together and preserve the lockup's spacing and aspect ratio. Do not stretch, outline, rotate independently, add effects or place lime directly on a light background. A single trace width is the clear-space reference, measured from the artwork; built-in SVG padding counts toward that space.

Use the favicon cut at 16–32 pixels. Prefer the full symbol from 24 pixels upward. Header lockups work around 112–132 pixels wide; check their actual rendered context. Set image alternative text to “Rally” where the identity is meaningful, and avoid repeating it for decorative duplicates.

## Geometry and verification

The selected symbol contains two closed paths and no strokes. Its content bounds are x=30–226 and y=39.58–216 on the 256-unit canvas. Both forward edges follow a 60-degree slope, with 36-unit horizontal stroke width and a 72-unit horizontal / 24-unit vertical stagger. Normal stroke thickness is about 31.18 units; the perpendicular separation is about 43.18 units. At a 16-pixel canvas these correspond to approximately 1.95-pixel strokes and a 2.70-pixel gap.

The favicon widens each horizontal stroke to 40 units while retaining the same visual rhythm. At 16 pixels its normal stroke thickness is about 2.17 pixels, with about 2.27 pixels of separation. It uses a 56-unit corner radius on the forest tile.

Verification performed:

- Parsed every new production and concept SVG as XML; checked viewBoxes, titles, paths and closed shapes.
- Ran the upstream dependency-free SVG audit against the concepts and production family, with two inspection passes.
- Rendered a comparison sheet with installed headless Chrome and visually inspected all three concepts, true-size samples, the outlined lockups and the favicon.
- Confirmed final assets contain no live text, raster images, filters, masks, external references, scripts or runtime font dependencies.
- Confirmed both preserved originals match their source SHA256 hashes.

The audit found no issues in the selected symbol or favicon. Lockups retain two deliberate diagonal angles from Archivo's original glyph outlines; the audit reports those as near-miss angles. They are typography, not misaligned symbol edges, and were retained. Reference-library complexity statistics were unavailable in the source-only audit snapshot, so no library-relative complexity claim is made.

CairoSVG and an FFmpeg SVG decoder were unavailable. Existing Chrome provided successful PNG inspection renders instead. The system Python lacked its optional Brotli extension; a temporary, read-only bridge used Node's built-in Brotli decoder so fontTools could outline the existing WOFF2. No packages or global configuration were installed or changed. Inspection tooling and PNG sheets remain outside the public website asset folder.

Integration and final visual QA in the complete page are handled by the parent website task. No product functionality was changed by this identity work.
