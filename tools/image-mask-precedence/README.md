# Image mask precedence regressions

These are original MIT-licensed numerical PDFs, not copies or reductions of an
external document. They contain no fonts, artwork or third-party fixtures.
`generate.py` creates the committed inputs and their analytic expectations in
[`testdata/pdf/image-mask-precedence`](../../testdata/pdf/image-mask-precedence/).
Python 3 and Pillow/OpenJPEG are needed only to regenerate the two JPEG 2000
controls, not to run the C# tests.

## The correction

`CanvasDevice.DrawImage` previously passed the original graphics-state mask to
`PaintBrush` after the image's own mask had already become image alpha. A black
state mask therefore hid even an image with an opaque SMask.

The correction selects a local paint state with no graphics-state soft mask when
a non-stencil image has decoded alpha and an SMask stream or a Mask stream/array.
Only `SoftMaskId` changes. Constant alpha, blend mode, geometry and clipping remain
in effect; the persistent graphics state is not modified. No public API, parser,
sampling or dependency change is involved. Failed mask decoding does not trigger
the override. Standalone stencil coverage and embedded JPX alpha alone do not
trigger this patch.

## Basis and limits

[ISO 32000-1:2008](https://opensource.adobe.com/dc-acrobat-sdk-docs/pdfstandards/PDF32000_2008.pdf),
Table 89 and 11.6.4.3, distinguish image-owned masks from the current soft mask.
The latter section expressly gives both image SMask and image Mask precedence.
Section 11.6.4.2 describes stencil coverage separately as object shape; 11.6.4.4
retains the alpha constant. [PDF.js PR 19269](https://github.com/mozilla/pdf.js/pull/19269)
independently implements that same SMask/Mask rule. No specification or external
implementation text/code has been copied into the inputs or correction.

The explicit/color-key cases are normative regressions, not all-engine consensus
claims. PDF.js passes those cases; the tested PDFium version retains the state
mask for both, while MuPDF retains it for the color key. Broader reference renders
also disagree on some blend, stencil and JPEG 2000 controls. Their failures must
not be converted into passing evidence or used to rewrite the analytic oracle.

Embedded JPEG 2000 mask precedence is deliberately unchanged. The
[PDF Association's ISO-approved issue 215](https://github.com/pdf-association/pdf-issues/issues/215)
clarifies its precedence in PDF 2.0, but the separately preserved active-JPX plus
zero-state-mask diagnostic is unresolved and receives no passing credit. The two
JPX tests here check only active alpha without a state mask and ignored encoded
alpha under a zero state mask. They do not assert correct active-JPX precedence.

## Coverage and oracle

The 17 cases check opaque and partial image SMask, image SMask over color key,
explicit/color-key masks, constant alpha 0 and 0.5, Normal/Multiply/Screen,
clipping, following ordinary-image and path paints, ordinary images, solid
stencils, and the two bounded JPX controls described above. Image and mask sample
grids are equal-sized, so these tests do not depend on the separate independent
mask-grid sampling fix. Each PDF is one 320 by 160 point page.

Expected interior color is computed from the authored source, painted backdrop,
mask and constant alpha: `B + ca * mask * (blend(B, C) - B)`. An image-owned mask
replaces the state mask; ordinary images and stencils retain it. Assertions avoid
antialiasing edges and allow two byte levels for compositing quantization, while
untouched backdrop and clipped-out areas require exact values. This tolerance was
set before any baseline or fixed rendering. Every test verifies its PDF hash and
serial/parallel pixel equality.

Run the built test executable with
`-class OneImage.Pdf.Tests.ImageMaskPrecedenceTests`. All 17 cases are ordinary
assertions, with no expected-failure or skip annotations. Reference engines and
platform-dependent visual checks are evidence, not test dependencies.
