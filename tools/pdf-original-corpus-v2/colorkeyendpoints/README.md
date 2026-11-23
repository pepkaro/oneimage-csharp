# Endpoint-only color-key / Decode controls

Logical sub-slice: ISO-IMAGE-COLORKEY-DECODE-03-ENDPOINT-CONTROLS. Exactly three original MIT PDF 1.7 files use one independently authored 3-by-3 RGB8 grid containing only red, cyan, magenta, green, blue and yellow components of 0/255. No source image cell is black or white. An opaque black/white checkerboard is ordinary page graphics behind the image. All variants use reversed Decode [1 0 1 0 1 0]: an unmasked control, stored-red key [255 255 0 0 0 0], and stored-red/magenta range [255 255 0 0 0 255].

Scope is deliberately endpoint-only. These three new cases do not replace, modify, rerun, close or weaken root's four held non-endpoint RGB8 cases. Their one-byte opaque-color disagreement remains separate. No expectation in those cases is changed, and their partial mask results are not promoted. scope.json records this boundary explicitly.

## Measured results

- Exactly 3 byte-unique PDFs; 6 case/DPI views; 18 freshly captured reference PNGs.
- 18 reference runs passed, 0 failed, 0 skipped. The worker invoked the reference runner once (6 calls per engine); no renderer rerun occurred after namespace/alias normalization. All 6 views and all 3 narrowly scoped cases qualify by three-reference agreement; 0 endpoint cases held.
- 666 of 666 named center checks pass at tolerance 0.
- 38,400 scored interior pixels per engine; 115,200 analytic reference-pixel checks pass. All three pairwise comparisons are exact in the declared interiors.
- Structural validation checks all 27 stored-cell mask decisions, exact raw bytes, endpoint complements, Decode/key arrays and the opaque checkerboard drawing program. The exact key masks 2 cells; the range masks 4 cells.
- Decoded-only matches stay opaque: stored cyan decodes to red in both keyed cases, and stored green decodes to magenta in the range case. There are 5 such case/cell controls, scored in all four quadrants at both DPIs across all references.
- Generator rerun preserves the PDF and manifest bytes. No upstream/private assets, external font bytes, borrowed fixtures/goldens, product runs or remote writes occur.

No expected/golden directory is created by this worker. Six MuPDF candidate paths are listed only after genuine independent reference agreement. Full RGB8 quantization remains unresolved by this endpoint sub-slice; no general renderer-conformance or upstream-parity claim is made.

## Geometry and oracle

The grid's stored colors are:

| Row | Left | Middle | Right |
|---|---|---|---|
| 0 (top) | red | cyan | magenta |
| 1 | green | blue | yellow |
| 2 | cyan | red | magenta |

The image occupies [32,40,72,72] on a 240-by-180 point page. Source cells are 24 points square. Each source cell overlays four 12-point checker squares. Every checker quadrant is inset 2 PDF points, yielding an 8-by-8 point scored region; named centers are fixed from that geometry. White paper has a separate [4,4,16,16] region. The NW/SE quadrants are black and NE/SW are white before image painting. Masked cells reveal both colors, preventing white-paint substitution from satisfying the full declared interior oracle.

Expected opaque colors use exact endpoint complement arithmetic; mask selection uses stored components. verify.py independently reconstructs complements using XOR255, rejects keys on out-of-range stored components, and checks separately enumerated masked and decoded-only cell IDs. It does not import the generator or use renderer output as its oracle. Raw decoded stream bytes are exactly 27 authored RGB bytes. There are no fonts, annotations, scripts, soft masks, matte entries, alpha channels, external resources, recursive content or malformed/stress/security cases.

All image, source-cell and checker boundaries and all undeclared page regions are unscored. Native visual/font-weight parity, WebView speed, non-endpoint interpolation/rounding and different color spaces are not tested.

## Reproduce

```sh
python generate.py
python run-references.py /path/to/node_modules/pdfjs-dist
python verify-regions.py
python verify.py
```

Pinned runtime: `/workspace/scratch/ee1a2fb9052d/pdf-checkpoint-20261123/references/node_modules/pdfjs-dist`. References are PDFium 153.0.7999.0 / pypdfium2 5.13.0, MuPDF 1.26.11 / PyMuPDF 1.26.6, PDF.js 6.5.438 build 0a4153349 / Node 24.22.3 / @napi-rs/canvas 1.1.1. Settings match: page 0, one page, rotation 0, 72/144 DPI, white RGB background, annotations disabled, image interpolation false. PDF.js is Node canvas, not a native browser. Actual versions and empty PDF.js diagnostics are verified.

The case IDs use the unique img-colorkey-endpoint-* namespace and the common manifest aliases id/fixture_id, sha/sha256, page=0/page_count=1, width/height, dpis, expected_samples and expected_regions. The initial capture filenames were normalized to that namespace without changing PDF or PNG bytes; reference rows record the exact input PDF SHA. The region verifier saves disagreement evidence before returning a nonzero status for held cases. Earlier helper/fixture files are untouched.

## Standards and mapping

The directly inspected governing clauses are ISO 32000-1:2008 8.9.6.4 (stored-component color-key selection before Decode) and 8.9.5.2 (linear Decode mapping). Official 2020 errata's 8.9.5.1/Table 87 Mask entry explicitly references 8.9.6.4, verifying that location and broad meaning. The full 2020 color-key algorithm/Decode text remains pending; no cart/form submission or standard redistribution occurs.

All upstream IDs/mappings remain empty. These are independently authored endpoint controls, not replacements for unseen upstream inputs or proof that the complete parent family is closed.

invocation-accounting.json separately records observed worker invocation totals for quote and endpoint cohorts; root clean replays are excluded and are not inferred from retained paths.
