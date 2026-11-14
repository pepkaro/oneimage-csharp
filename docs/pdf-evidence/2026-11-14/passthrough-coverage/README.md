# Preserve owning-group coverage through passthrough forms

## Problem, cause and fix

The top row of shapes disappears even though equivalent directly painted shapes in the bottom row remain. A non-isolated passthrough form shares its parent's drawing target but sits at the top of the frame stack. The old coverage lookup examined only that top frame and missed the owning group's alpha canvas. The fix skips passthrough frames while looking for that owner, stopping at another layer or a soft-mask boundary. This is the adjacent `06-group-backdrop-alpha` → `07-passthrough-coverage` change, after the backdrop-removal repair.

## Read the visual

Each top-row polygon is painted through nested non-isolated forms. The bottom row paints the same original polygon directly, translated down exactly 62 points (124 pixels at 144 DPI). Left to right alpha is 0.25, 0.60 and 0.85. An inner change to stroke alpha `/CA 0.83` cannot change these filled polygons. Their intended colors are white×(1−a)+(0.05,0.55,0.75)×a. This numeric/control equivalence determines the expectation; references are secondary observations.

### Before
![Before: nested passthrough shapes vanish while direct controls remain](renders/passthrough-coverage-before.png)
### After
![After: nested shapes match direct controls within byte rounding](renders/passthrough-coverage-after.png)
### References
![PDFium raw page](references/passthrough-coverage-pdfium.png)
![MuPDF raw page](references/passthrough-coverage-mupdf.png)
![PDF.js Node Canvas raw page](references/passthrough-coverage-pdfjs.png)

## Checks and reference differences

Comparing the translated rows gives 13,335 differing pixels before (maximum channel difference 206), versus 349 pixels after, all differing by only 1. At one interior point per column, the after top and bottom colors are exactly equal: (195,226,239), (110,186,217), (49,157,201). The bottom row stays unchanged across the production fix. Do not claim the entire two rows are byte-identical.

PDFium's rows are identical. MuPDF and PDF.js Node Canvas preserve both rows too, but differ by up to 3 and 2 channels respectively between grouped and direct rendering. Whole-page reference MAE changes 10.5198→0.1195, 10.6802→0.2947 and 10.5786→0.1515 for PDFium/MuPDF/PDF.js. This reflects missing-paint repair plus remaining rounding/edge differences, not proof of universal reference equivalence. Before/after changed pixels: 13,339/98,304.

The invariant is consistent with the non-isolated group composition model in [ISO 32000-1:2008, 11.4](https://opensource.adobe.com/dc-acrobat-sdk-docs/standards/pdfstandards/pdf/PDF32000_2008.pdf). This PDF does not exercise crossing soft-mask or isolated-layer boundaries; separate source tests do.

Exact review-head full PDF suite: 450 passed, 0 skipped. The deliberate production-revert control failed the non-isolated passthrough case while the isolated-child and mask-boundary controls passed. See `analytic-checks.json`, reproduction, provenance and manifest for precise settings and byte hashes. No performance or native browser/WebView claim is made.
