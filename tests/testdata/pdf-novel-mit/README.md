# Independently authored MIT PDF behavior corpus

This initial set contains **40 unique PDFs, 40 one-page feature cases, and 120
parameterized test rows**, plus one inventory-integrity test. Assertion methods
are not counted as additional documents or feature cases. It is a small offline
regression suite, not a claim of full PDF.js/PDFium feature parity.

Every PDF was newly authored by `tools/mit-pdf-corpus/generate.py` from behavioral
descriptions. The generator takes no upstream PDF, test source, expected image,
font, artwork, text, or ICC file as input. Raster samples are numeric arrays written
in the generator; both Type3 glyphs are original geometric shapes. There are no
embedded third-party fonts, commercial documents, JavaScript, launch actions,
external links, malformed recovery fixtures, or security/exploit reproductions.
The assets and new accompanying code are MIT; see `LICENSE`. Existing project and
reference-tool licenses are unchanged. Reference runtimes are not vendored.

## Coverage and expectations

`features.json` maps every original input to the behavior it exercises.
`manifest.json` records exact SHA-256, length, license, provenance, page boxes,
rotation, annotations, output size, and expected image/content properties.

- Color: DeviceRGB, Gray, CMYK channel order, Indexed lookup, reversed Decode.
- Images: small original RGB arrays, nearest/smooth interpolation, stencil masks,
  inline RGB/Gray images.
- Geometry: nonzero/even-odd clipping, intersecting transformed clips, round/square
  dash caps, degenerate strokes, translated CropBox and all four rotations,
  translated/reflected/skewed forms with BBox clipping.
- Compositing: constant alpha, empty/painted backdrops, Screen/ColorDodge/Multiply,
  isolated and knockout groups, alpha/luminosity soft masks.
- Painting: axial/radial gradients, colored/uncolored tiling patterns.
- Content: original Type3 d0/d1 glyph procedures, static annotation visibility,
  and explicit button appearance states.

Expected values do **not** come from the OneImage image. The three independent
engines actually render every input. Flat-interior probes were reviewed where all
three outputs have a flat 5×5 neighborhood (spread <=2 per channel), agree within
8 levels, and are away from edges. Those probes permit 12 levels, accommodating
engine/color rounding without turning edge antialiasing into a blanket failure.
Separate RGB/Gray samples come directly from the PDF operands (tolerance 1), an
axial midpoint comes from its analytic interpolation (tolerance 4), and CMYK
channel ranges verify colored quadrants without imposing one engine's CMYK
profile. The on/off dash controls have explicit nonblank/blank expectations.

Ink counts and bounds provide additional conservative content/geometry guards:
RGB below 235 in any channel counts as ink; the initial broad nonblank count
range spans one-third of the reference minimum through three times its maximum,
with 25 pixels of slack and a page-area cap. Reference ink bounds allow 4 pixels
of edge slack. These are coarse guards, not a whole-image equality or complete
correctness proof. Exact page geometry, semantic probes, text presence, and
blank controls add independent checks. Region and serial/parallel equality test
determinism separately; determinism is never used as a correctness oracle.

## Offline tests

The normal .NET tests do not download inputs or require reference tools:

```sh
dotnet run --project tests/OneImage.Pdf.Tests -c Release -- -class OneImage.Pdf.Tests.NovelPdfCorpusTests
python tools/mit-pdf-corpus/generate.py
```

The generator verifies exact committed bytes by default; `--write` is an explicit
maintainer operation, not part of testing. PDF inputs are each under 1 MiB.
Rendering is at 72 DPI (320×240 pixels normally; cropped rotations have smaller
sizes) on opaque white, with limits of 1 MiB input, 1 Mi-pixel images/cache,
16 nesting levels and 512-pixel pattern tile sides. Render operations get a
15-second cancellation token. No PDF action/event is executed.

Two visual assertions expose known baseline defects, instead of blessing current
output. Their structural and region/parallel tests still run:

- `zero-length-dash-gap`: an off dash phase must be blank, but baseline paints a disc.
- `blend-empty-backdrop`: Screen/ColorDodge over unpainted PDF content must paint
  the source, but baseline incorrectly blends against the white display surface.

Set `ONEIMAGE_PDF_NOVEL_KNOWN_FAILURES=1` to execute those visual assertions; keep
this opt-in run in defect verification until the separate production fixes land.
A skip is not a pass. This infrastructure change does not claim to fix either bug.

## Pinned independent reference audit

Install tools into an external environment, outside the checkout. These are
reference tools, **not new project/runtime dependencies**. Their licenses remain
separate from the original MIT test assets.

- PDF.js 6.5.438, build `0a4153349`, official `pdfjs-dist` npm distribution.
  Package integrity: `sha512-vg8Pw1x+AFKy4AMDvhuWl5cOYV8d698UoEANoFFhc79hqXDnZQqnOXoxw3HG907WHOg1JYOvLhP756boddFxpA==`.
  Node 24.22.1 and `@napi-rs/canvas` 1.1.1. `useWorkerFetch=false` disables
  ICC WASM in this backend, and DeviceCMYK uses polynomial fallback. This set
  contains no ICCBased input; its CMYK check is a broad channel/geometry check,
  not color-managed equivalence. This is a **Node Canvas diagnostic
  backend, not native browser Canvas parity**. Sandboxed Chromium could not launch
  in the validation environment; no security/sandbox workaround was used.
- pypdfium2 5.13.0, PDFium 153.0.7999.0, white background, scale 1,
  `draw_annots=True`. Initialize a form environment with XFA disabled for static
  widget appearances. Do not dispatch document/page actions or supply a JS platform.
- PyMuPDF 1.26.6 wrapping **MuPDF 1.26.11** (wrapper and engine versions differ),
  identity matrix, `alpha=False`, `annots=True`.

Primary distribution/documentation sources:
[Mozilla PDF.js](https://github.com/mozilla/pdf.js),
[official npm package](https://www.npmjs.com/package/pdfjs-dist/v/6.5.438),
[pypdfium2](https://github.com/pypdfium2-team/pypdfium2),
[MuPDF](https://mupdf.com/).

For example, create an external venv with `PyMuPDF==1.26.6`,
`pypdfium2==5.13.0`, and `Pillow==13.0.0`. In a separate external npm directory,
install `pdfjs-dist@6.5.438` and `@napi-rs/canvas@1.1.1` with `--ignore-scripts
--save-exact`. The audit requires these pinned engines and never rewrites the
manifest's expectations:

```sh
python tools/mit-pdf-corpus/audit_references.py \
  --pdfjs-runtime /external/node_modules/pdfjs-dist \
  --output /external/new-reference-run
```

Each engine is run in a fresh process with a 20-second timeout. Output must be
outside the checkout. The result contains untouched full-page PNGs and per-input,
per-engine execution status, assertion failures, settings and hashes. Individual
PDF.js reproduction, at the same settings:

```sh
node tools/mit-pdf-corpus/render-pdfjs.mjs \
  /external/node_modules/pdfjs-dist input.pdf output.png 72
```

PDF.js uses white background, static annotations `ENABLE`, no eval, XFA or system
fonts, and only local CMap/font/Wasm paths in the external package. There is one
known reference disagreement: on `zero-length-dash-on`, PDF.js/Node Canvas omits
an on-phase zero-length round cap that MuPDF, PDFium and OneImage paint. The positive
control remains nonblank; that reference execution is reported as a disagreement,
not a pass and not evidence of native-browser behavior. DeviceCMYK differences
are documented policy differences, not automatically bugs. Fresh image hashes
in the manifest identify the evidence; they are not portable pixel or PNG hashes
that every engine must reproduce.

## Future work boundaries

The next separately staged milestone is about 200 additional original MIT
behavior cases, excluding these 40. Priorities include nested groups, default
color spaces, sample/filter combinations, nontrivial pattern matrices, text
positioning/encodings and independently constructed embedded fonts. Behavioral
mapping to external Mozilla/PDFium inventories must not copy or adapt their
fixture/source/asset content. Upstream tests remain external where permitted.
Actual upstream executions, new-original feature coverage, unsupported features,
unsafe/license exclusions, and pending items must be reported separately.
Browser/API/editor tests and PDFium C++ unit/embedder registrations are not
silently included in counts of rendering PDFs. No whole-suite parity is claimed.
