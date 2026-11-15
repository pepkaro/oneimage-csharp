# Zero-length dashed stroke controls

These 97 PDFs and the related `SpecTruth/ZeroLengthDashTests.cs` regressions are
independently authored MIT material. All geometry is original numeric geometry.
There are no external test PDFs, fonts, images, source fixtures or expected images.
The generator takes no source document as input. The existing project and
reference-runtime licences are unchanged; runtimes are not vendored.

The regression fixes zero-length round-capped subpaths painting during a dash
gap. ISO 32000-1:2008 8.4.3.6 requires the dash phase to restart independently for
each subpath; 8.5.3.2 supplies the special round-cap shape for degenerate subpaths.
A zero-length dash entry at the current phase still paints its cap. A positive
gap does not. Odd arrays must be repeated twice for the complete on/off cycle.

The unit-test expectations are explicit analytical on/off classifications, with
solid/no-dash, zero-entry and small positive-length controls. Visible-disc area
checks allow the existing 0.1-pixel flattening error; gap checks require exactly
white pixels. These are not reference-image snapshots. They cover boundaries,
wrapped phase, odd arrays, zero entries, resets, line/curve/closed/rectangle
degeneracy, move-only, butt/square, affine transforms, hairlines and region/thread
determinism. The production change does not modify the general stroker or glyph
outline geometry.

Generate an external evidence directory:

```sh
python tools/zero-length-dash/generate.py /tmp/zero-dash-inputs
dotnet build tools/PdfRender -c Release
dotnet "$ONEIMAGE_ARTIFACTS/bin/PdfRender/release/OneImage.PdfRender.dll" \
  batch /tmp/zero-dash-inputs/batch.txt /tmp/zero-dash-oneimage 144 20
```

The generator writes exact PDF SHA-256 hashes, construction operands and batch
inputs. It writes new original files only; it does not rewrite test expectations.
The PDF pages are 192×144 points at rotation 0 with an explicit matching CropBox.

For the optional independent reference run, install these tools outside the
checkout: `pypdfium2==5.13.0` (PDFium 153.0.7999.0), `PyMuPDF==1.26.6`
(MuPDF 1.26.11), and `Pillow==13.0.0`. They are not package/runtime dependencies.

```sh
python tools/zero-length-dash/render_references.py \
  /tmp/zero-dash-inputs /tmp/zero-dash-references
```

The script verifies these versions and the input hashes, renders full pages at
144 DPI on opaque white with annotations disabled, and records raw PNG hashes
and ink/area counts. It performs no cropping, scaling, alignment or retouching.
There are no annotation objects or executable actions in the generated files.

## Reference disagreements are not an oracle

PDFium and MuPDF agree on the central solid/on/off controls. They disagree on
some legitimate degenerate-path boundaries and shapes. The explicit doubled
odd-array controls isolate MuPDF's changed second-traversal parity. PDFium paints
the exact zero-length line just before the next on interval (`even-27.999`) but
leaves a shorter-than-the-gap positive segment blank (`gap-near-end-tiny`). Some
PDFium butt/square degenerates paint, and some degenerate curves/rectangles do
not. Zero-entry boundaries also differ. Preserve these findings when reviewing
full metrics; do not replace analytical assertions with a renderer vote.

The Node PDF.js canvas backend is not a valid independent check for exact
zero-length round caps: it has omitted both solid and on-phase positive controls
in a separate direct-canvas reduction. Native-browser PDF.js remains unverified.
This suite does not claim whole-PDF or cross-engine pixel parity.

Primary specification:
https://opensource.adobe.com/dc-acrobat-sdk-docs/pdfstandards/PDF32000_2008.pdf
(sections 8.4.3.6 and 8.5.3.2).
