# Zero-length dashed round caps

## Scope and original authorship

The candidate is based on OneImage e43ee264954a177ff01a16584625a3dea79244fa.
The new test source, numeric geometry, PDF generator, generated PDFs and rendered
images are independently authored MIT material. No external fixtures, fonts,
images, vendor test content, private documents or derivatives are used. The
existing project and dependency licences remain unchanged. An earlier MIT corpus
fixture is used separately to verify removal of its known-failure annotation.

## Specification reasoning

ISO 32000-1:2008, 8.4.3.6 defines alternating on/off lengths, cyclic phase and an
independent phase restart for each subpath. Section 8.5.3.2 applies the stroke
graphics state and says degenerate subpaths paint only for round caps; trailing
move-only subpaths do not paint. The special treatment of zero-length dash entries
does not give a cap an independent painting operation inside a positive gap.

Primary sources:

- https://opensource.adobe.com/dc-acrobat-sdk-docs/pdfstandards/PDF32000_2008.pdf
- https://raw.githubusercontent.com/adobe/dc-acrobat-sdk-docs/master/docs/standards/pdfstandards/pdf/PDF32000_2008.pdf
- https://opensource.adobe.com/dc-acrobat-sdk-docs/pdfstandards/pdfreference1.5_v6.pdf

The test expectations are an analytical interpretation of these rules, not a
vote across renderers. For [11 17], phases 0 through less than 11 are on, phases
11 through less than 28 are off, and 28 restarts. A positive on entry that ended
at the starting phase has already been consumed. A zero-length on entry at the
starting phase is still a dash and paints its cap. For example, [11 0 0 17] at
phase 11 includes a zero-length on dash after a zero-length gap, whereas
[0 0 11 17] at phase 11 begins its positive gap. An odd array must be doubled to
restore on/off parity before repeating the cycle. These examples are explicit
test expectations, independent of the implementation.

## Implementation boundary

CanvasDevice.ZeroLengthDiscs formerly synthesized each degenerate round cap
without considering dashes. The candidate computes the existing normalized dash
array once and uses it for both the ordinary stroke and the degenerate-cap phase
check. This preserves the renderer's existing normalization, float precision and
safety fallback. It does not change the general stroker, flattening, path geometry,
minimum positive-width policy, hairline sizing or rasterizer. One bounded phase
scan is shared by every degenerate subpath because each subpath restarts its phase.

## Reference limitations observed before implementation

PDFium and MuPDF both leave the central [11 17], phase 19 zero-length line blank;
both paint its phase 3 and solid controls. Their antialiasing and degenerate-path
handling are not identical. Reference outputs must not be copied into analytical
expectations.

- MuPDF differs on odd arrays after the first traversal. Explicitly doubled-array
  controls are included to isolate this issue.
- PDFium paints at phase 27.999 immediately before the next on interval, while
  MuPDF is blank. A zero-length path cannot consume the remaining positive gap.
- PDFium paints some butt/square degenerate lines but omits the degenerate cubic
  and zero-size rectangle. These are not grounds for changing OneImage's existing
  spec-aligned cap policy.
- Exact zero-entry boundaries have additional reference disagreements, including
  [11 0 0 17] at phase 11. Equivalent initial-zero and positive-length controls are
  included. See the full metrics, not just selected images.
- Native-browser PDF.js was not run. A separate direct Node Canvas reduction found
  the canvas backend omits all exact zero-length round caps, even solid/on controls;
  that result is not independent evidence of correct dash semantics.

All reference comparisons use full pages, 144 DPI, CropBox equal to MediaBox,
rotation 0, opaque white background and annotations disabled. There is no image
scaling, alignment, cropping, retouching or on-image annotation. HTML captions are
outside the raw PNGs. Different AA pixels on visible caps are reported rather than
hidden.
