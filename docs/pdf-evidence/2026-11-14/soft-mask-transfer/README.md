# Apply soft-mask transfer after mask extraction

## Problem and cause

An inverting soft mask looked like an identity mask: low-valued bands remained faint and unpainted alpha-mask space remained white. The renderer extracted group alpha or luminosity but did not apply OnePDF's evaluated transfer table.

## Fix

Look up each extracted byte in `PdfSoftMaskInfo.TransferTable`; retain the existing value when the table is null. Apply it to the entire mask canvas, including unpainted pixels and space outside the form's bounding box. This is the immediate `04-fused-rgba-blend` → `05-soft-mask-transfer` change, not a comparison against an unrelated earlier baseline.

## Read the visual

The left panel is an Alpha mask; the right panel is Luminosity. Both use the original numerical bands 0.15, 0.35, 0.70 and `TR(x)=1-x`, with the same blue paint. From bottom to top the intended opacities are therefore 0.85, 0.65, 0.30. The alpha panel's unpainted space has opacity 1, including the strip outside its smaller mask form. The luminosity panel uses backdrop gray 0.45 and so its unpainted space has opacity 0.55. Edges, page size and all image pixels below are unmodified.

### Before
![Before: identity-like alpha and luminosity bands](renders/soft-mask-transfer-before.png)

### After
![After: inverse bands and correctly transferred unpainted backdrop](renders/soft-mask-transfer-after.png)

### References, shown without choosing an oracle

![PDFium raw page](references/soft-mask-transfer-pdfium.png)
![MuPDF raw page](references/soft-mask-transfer-mupdf.png)
![PDF.js Node Canvas raw page](references/soft-mask-transfer-pdfjs.png)

PDFium and PDF.js Node Canvas match the inversion and outside-mask behavior. MuPDF also inverts the interior bands, but leaves the area outside the Alpha form's BBox white; this explains the remaining material disagreement. The analytic expectation comes from the PDF rule for applying the transfer function to zero outside an alpha mask, not a vote among engines. See [ISO 32000-1:2008, 11.6.5.2](https://opensource.adobe.com/dc-acrobat-sdk-docs/standards/pdfstandards/pdf/PDF32000_2008.pdf). This small control does not establish a general MuPDF defect diagnosis.

At page coordinate (20,10), outside the alpha form but within the blue painted rectangle, before is RGB (255,255,255), after is (26,77,191), PDFium (26,77,191), MuPDF (255,255,255), PDF.js (26,76,191). The expected fully opaque blue is approximately (26,77,191), subject to byte rounding.

## Measurements and checks

- 71,680 of 98,304 pixels change. RGB mean absolute difference between before and after: 58.2571 on the 0–255 scale.
- Whole-page RGB MAE against PDFium: 58.4157 → 0.4469; against MuPDF: 48.4396 → 11.2243; against PDF.js Node Canvas: 58.2365 → 0.2636. Differences are descriptive, not pass/fail or correctness scores.
- Input, PNG, raw RGBA and engine DLL hashes are verified. All PNGs decode byte-for-byte to their stored RGBA samples. The standalone generator recreates the input byte-for-byte; no source tree is changed by this review.
- Exact review-head full PDF suite: 374 passed, 0 skipped, as recorded by source review. Cross-platform CI, AOT/WASM and native browser/WebView rendering are not covered here. No timing claim is made.

See `PROVENANCE.md`, `REPRODUCTION.md`, `manifest.json`, `metrics.json`, and `SHA256SUMS` for settings, sources and exact bytes.
