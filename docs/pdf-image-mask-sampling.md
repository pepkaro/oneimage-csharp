# PDF image and mask sampling

## Dependency and build status

This renderer change depends on the additive `PdfImageAlpha.Interpolate` property in OnePDF. Neither OneImage's current declared OnePDF **1.18.0** packages nor the unmodified OnePDF **1.22.0** source contain it. The dependency versions are intentionally not changed to an invented package version.

Land and release the OnePDF semantic-data change first, then update both `RecursiveAI.OnePdf` and `RecursiveAI.OnePdf.Fonts` to the actual release and rerun integration tests before merging this renderer change. An isolated source-reference build is suitable for review, not evidence that the current package dependency builds. The renderer must remain blocked until that dependency is available. No reflection compatibility fallback is used.

## Corrected behavior

The color image and a separately sized soft or explicit mask each cover the unit square. Neither grid is resized to the larger dimensions merely to combine them. This prevents an opaque mask from altering color samples, avoids shifting boundaries when dimensions are coprime, and avoids allocating the cross-product of crossed image dimensions.

`PdfImageAlpha.Interpolate` is used independently from the parent image flag. Equal grids with differing flags remain separate. Each independent plane is area-reduced using the existing reduction threshold and filter, then sampled through the same placement. Cache keys include both reduced dimensions, and cache costs include both stored planes. Image limits and cancellation checks apply to both.

## Filtering policy

The default magnification policy is nearest sampling unless the relevant image requests interpolation. Coincident grids with matching sampling policies retain alpha-weighted bilinear filtering and reduction. This keeps transparent sample colors from tinting neighboring visible samples. Different grids or interpolation flags are filtered independently and multiplied at the final device sample. Filtering is not promised to match all viewers.

`SmoothMagnifiedImages` opts into smoothing both color and decoded opacity when each plane is magnified. It does not change standalone stencil behavior. When coincident grids are magnified under this override, they use the existing combined alpha-weighted filter regardless of their original flags. Valid same-size `/Matte` image data are unblended by OnePDF before color conversion, as before; tests compare them with the equivalent unblended input.

## Normative basis and independent checks

[ISO 32000-1:2008](https://opensource.adobe.com/dc-acrobat-sdk-docs/standards/pdfstandards/pdf/PDF32000_2008.pdf), 11.6.5.3 and Table 145, specifies independent mask dimensions without Matte, common unit-square mapping, and ordinary image meaning for the mask's Interpolate entry. Section 8.9.5.3 leaves the interpolation algorithm implementation-dependent. Matte dimensions must match, and recovered colors are used for compositing.

The nearest-sampling tests use an analytical coordinate model and opaque-mask metamorphic controls. Independent PDFium and MuPDF renders corroborate the corrected interior colors and boundaries. MuPDF has small boundary-rounding differences. PDF.js 6.5.438 with Node Canvas is an additional comparison, not the oracle: it constructs combined RGBA, loses independent mask interpolation, and shifts some coprime boundaries. Hidden-color interpolation also differs between viewers. Browser PDF.js output was not verified in the review environment.

## Original fixtures

`ImageMaskSamplingTests` constructs new PDFs from numerical formulas in memory. The companion generator writes independent one-page probes:

```sh
python tools/pdf-gate/generate_image_mask_sampling.py --out /tmp/image-mask-probes
```

The added tests and generator are original MIT work. They contain no imported PDFs, images, fonts, profiles, or copied audit assets. Tests cover larger/smaller masks on both axes, coprime dimensions, opaque/partial/zero alpha, soft and explicit masks, Decode, independent flags, hidden colors, Matte, transforms, reduction, limits, cache keys, cancellation, regions, and concurrent reads.

Performance has not been measured for this change. No universal viewer-parity or performance claim is made.
