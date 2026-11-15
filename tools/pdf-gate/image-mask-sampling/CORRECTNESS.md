# Independent image and mask sampling

The full raw records, binary provenance dumps, generated images and freeze manifests referenced below are retained locally for audit. This public report does not include or redistribute those raw collections.

## Scope

Raster.FromData previously resampled a color image to a larger mask's dimensions using bilinear filtering before combining alpha. A fully opaque soft mask could therefore change broad image colors even with Interpolate false. Nearest resampling to a shared maximum-sized grid is not a complete fix: coprime image/mask dimensions can move sample boundaries.

The candidate keeps color and opacity on their own grids when dimensions or effective interpolation flags differ. PixelBrush maps both through their shared unit-square placement and samples each using its own grid and policy. Matching coincident grids retain the existing premultiplied filter. Different flags remain independent even at equal dimensions. The opt-in SmoothMagnifiedImages policy applies to magnified color and decoded opacity; matching coincident effective policies use the combined path. Valid same-size Matte recovery and standalone stencil behavior remain intact.

The follow-up fast path changes only PixelBrush dispatch. A once-per-row decision sends independent masks to the corrected sampling loop. Without an independent mask, the loop matches the original e43 implementation exactly. This includes unmasked images and coincident masks already combined into the raster. It does not change mask semantics or introduce JIT/runtime configuration changes.

## Review units and build dependency

OnePDF base: d813ec6ba9dd138f7d2a6f3b8f5a51dc9c5f4bc8, source version 1.22. OneImage base: e43ee264954a177ff01a16584625a3dea79244fa. The two repositories remain separate review units.

The additive OnePDF property PdfImageAlpha.Interpolate retains the flag of the effective opacity supplier. It covers soft masks, explicit/standalone stencils and embedded or color-key alpha without reconstructing loader decisions from raw dictionaries.

The OneImage renderer depends on that property. Its currently declared OnePDF 1.18.0 package and unmodified source 1.22 do not contain it. A normal 1.18 package build has three expected CS1061 errors. Tests use an explicit source-reference integration with patched d813, not a claim of 1.18 compatibility. Merge/release the OnePDF API first, then update both OneImage dependency declarations to the actual containing release, update the dependency prose in src/OneImage.Pdf/README.md and docs/pdf.md, and rerun ordinary builds/tests on the actual rebased stack. No release number has been invented and no package has been published.

## Correctness evidence

- Source-matched e43 plus unmodified d813 fails 15 of 19 applicable behavioral regressions. Two new internal-representation tests cannot compile against the old Raster API. All 21 new cases pass in the corrected renderer.
- The original corrected candidate passes 656/656 OneImage.Pdf tests. The separate PixelBrush fast-path candidate also passes 55/55 focused sampling/smoothing tests and 656/656 full PDF tests, with zero build warnings or errors.
- The unchanged OnePDF patch passes 3,613 core tests with 281 skips and zero failures (3,894 total). Skips reflect missing external test data/tools and one pre-existing reading-order limitation, not successful coverage of those cases. The fast path does not alter OnePDF source.
- All 33 e43/package-1.18 renders are byte-identical to their e43/unmodified-source-1.22 counterparts, isolating the renderer fix from the dependency-version difference.
- All 99 fast-path RGBA and PNG outputs at 36, 72 and 144 DPI exactly match the held corrected candidate. The same three required unchanged 288-DPI performance controls also match baseline byte-for-byte.
- All four coprime nearest partial-mask cases match the analytical sampling/compositing model exactly. PDFium pixels with a channel error greater than two fall from 25,920, 13,566, 22,350 and 22,458 to zero respectively for color/mask dimensions 3×5/7×11, 11×7/3×5, 3×11/7×5 and 11×3/5×7.
- Twelve opaque-mask/unmasked comparisons (four dimension pairs at three DPIs) are byte-identical in the corrected renderer. Reflection, rotation, skew, unequal flags, hidden color, partial/zero/opaque alpha, Decode, soft/explicit masks, smoothing override, Matte, reduction, cancellation, limits, cache accounting, fresh regions and multithread controls are also exercised.
- The skew control matches the analytical nearest result within one channel value at all 29,962 tested interior pixels. Remaining PDFium differences lie within two pixels of a source/mask sample boundary; MuPDF differences lie within one. These are documented residuals, not full transformed-edge parity.

## Independent references and limits

Reference versions: PDFium 153.0.7999.0 through pypdfium2 5.13.0; MuPDF 1.26.11 through PyMuPDF 1.26.6; PDF.js 6.5.438 through @napi-rs/canvas Node Canvas. The evidence contains 99 unretouched 72-DPI PNG references plus 72 at 36/144 DPI. PDF.js results are Node-specific; no browser output was obtained and no browser parity is claimed.

[ISO 32000-1:2008](https://opensource.adobe.com/dc-acrobat-sdk-docs/standards/pdfstandards/pdf/PDF32000_2008.pdf) section 11.6.5.3/Table 145 maps the image and mask independently to the unit square. Section 8.9.5.3 allows implementation-specific interpolation. Equal-grid hidden-color probes expose reference disagreements: PDFium/MuPDF use straight-color interpolation, whereas PDF.js Node and the retained coincident OneImage policy use premultiplied filtering. The candidate deliberately preserves that coincident policy and corrects independent sample geometry/flags; it does not claim universal interpolation parity. Native minification filters also disagree. Existing area-reduction policy is retained per plane.

Both raster planes count toward cache storage, and each plane is checked before its renderer raster allocation. These renderer checks happen after OnePDF decoding; decoder allocations remain governed by DocumentLimits. The crossed 401×1 and 1×409 example stores 810 RGBA pixels, not 810 bytes or a peak-memory bound. Cache budgeting is best-effort and pre-existing cached-result cancellation behavior remains unchanged. Build analyzers pass, but no Native AOT publish was run.

The first performance gate exposed a repeatable unchanged nearest retained-path slowdown, so the original corrected candidate is held for performance review. Its raw records remain intact. The fast-path candidate has separate source, binaries, correctness evidence and performance records. Corrected independent-mask costs must be reported separately from unintended common-path overhead. No universal, parallel or default-runtime performance-neutrality claim is made.

## Original-MIT provenance

The 33 PDFs, numerical formulas, regression tests and generator are original MIT work. No private PDF, third-party audit fixture bytes, artwork, fonts, profiles or non-MIT corpus asset were copied. Reference PNGs are unmodified outputs produced from those original numerical PDFs. External reference renderer programs and binary assemblies are not redistributed by the evidence bundle. Existing source repository licenses remain intact; LICENSE covers the new evidence material.

The committed portable generator is tools/pdf-gate/generate_image_mask_sampling.py. It reproduces the 33 fixture bytes and their manifest. source-manifest.json records every changed source hash and source-only patch hash. Exact file allowlists identify review source and optional evidence; they exclude local source-reference overrides, copied repositories, generated binary assemblies and private reports.
