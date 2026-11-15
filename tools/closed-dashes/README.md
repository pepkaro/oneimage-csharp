# Closed-dash construction controls

All new numeric geometry, test code, fixture-generator code and generated PDFs
are original MIT-licensed work. There are no input documents, external images,
fonts, vendor fixtures or copied reference pixels.

Generate the 91 full-page controls with:

```sh
python3 tools/closed-dashes/generate.py /tmp/closed-dashes
python3 tools/closed-dashes/render_references.py /tmp/closed-dashes
```

The reference script needs `pypdfium2`, `PyMuPDF` and `Pillow`. It renders at 72 and
144 DPI with matching MediaBox/CropBox, rotation zero, opaque white and no
annotations. Output PNGs are not cropped, resized, aligned or retouched.
`reference-settings.json` records exact engine versions. Use the project's
`PdfRender batch` command with generated `inputs.txt` for before/head rendering.

The core fix preserves the documented joining of closed dashed figures. A whole
ON interval must pass the original distinct vertices to the stroker, not an
extra copy of the closing point. A figure starting in an OFF interval must not
be marked wholly ON, or the final partial dash acquires a false closing edge.
Direct core tests assert the exact outline and dash-piece coordinates, including
all joins/caps and a true out-of-bounds Boolean limit. The PDF tests add no-crash,
initial-gap, fresh-region and thread-degree coverage.

The exception fix is **not PDF dash-seam parity**. Both PDFium and MuPDF cap the
first/last pieces at a PDF closed dashed subpath's seam, unlike the core's joined
policy. In particular, the tiny and out-and-back cubic examples now render, but
retain a substantial shape difference. That PDF-specific seam behavior is a
separate issue; PDF smoke tests do not encode whole-ON=solid as a PDF pixel
contract. ISO 32000-1:2008 sections 8.4.3.6 and 8.5.3.2 are the relevant primary
specification, available from:
https://opensource.adobe.com/dc-acrobat-sdk-docs/pdfstandards/PDF32000_2008.pdf

Neither exceptions nor missing reference output count as pixel matches.
PDF.js with Node Canvas has a known stationary-cap limitation and is not used as
a native PDF.js/WebView equivalence claim.
