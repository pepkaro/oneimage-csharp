# PDF dashed seams

These controls are independently authored original MIT numeric geometry. They
use only the original PDF writer from the adjacent `closed-dashes` tools; no
private documents, vendor fixtures, fonts, images or reference pixels are copied.

```sh
python3 tools/pdf-dash-seams/generate.py /tmp/pdf-dash-seams
python3 tools/closed-dashes/render_references.py /tmp/pdf-dash-seams
```

The 61 PDFs cover tiny out-and-back lines, cubic reversals, polygons, every cap,
multiple/odd/zero-length dash patterns, positive and zero widths, skew/reflection,
all-zero/tiny-pattern solid fallbacks, repeated explicit closing vertices and
commands after Close. All pages are 192 by 144 points with matching CropBox,
zero rotation, white background and no annotations. Reference images are direct
72/144 DPI renders with no crop, resizing, alignment or retouching.

The PDF policy caps the first and last dash pieces independently at a closed
subpath's seam. Core drawing retains its existing joined policy by default.
Only nonempty normalized dash arrays reach the new splitter policy; solid
fallbacks keep their closed joins. Both positive-width and hairline PDF paths
use the explicit PDF policy. The previous StrokeBuilder.Build entry point is
retained for already compiled drawing clients.

The analytical tiny-line test expects one half-disc plus the narrow rectangle.
Other tests compare equivalent independently written path descriptions, not
copied renderer pixels. Relevant primary specification: ISO 32000-1:2008
sections 8.4.3.6, 8.5.3.2 and Table 59:
https://opensource.adobe.com/dc-acrobat-sdk-docs/pdfstandards/PDF32000_2008.pdf

The seam policy is supported by the independent PDFium/MuPDF comparisons; exact
antialiasing pixels differ between engines. Reference disagreements remain
explicit: MuPDF handles a line after Close differently from PDFium and the
standard's new-subpath rule, and omits the malformed all-zero dash fixture
instead of this renderer's existing solid fallback. The fallback is not changed.
Those results do not constitute universal or pixel-exact parity.
