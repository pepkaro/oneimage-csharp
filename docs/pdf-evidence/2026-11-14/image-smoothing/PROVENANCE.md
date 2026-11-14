# Authorship and evidence boundary

Copyright (c) 2026 OneImage contributors. SPDX-License-Identifier: MIT.

The generator, its numeric PDF objects and content, color/raster arrays, geometric artwork, original polygon glyph where present, reference adapters, harness and explanatory documents were authored for these controls. Source inspection finds no external PDF/font/image/test-stream read or inclusion in the generator. The only artwork inputs are explicit numbers in this source. This review reproduced every PDF and the original CFF byte-for-byte with the listed generator/dependency versions. No upstream/private PDF streams, expected images, vendor fonts, or CC/BSD/Apache fixture material are part of this evidence package. Existing production code/tests were reviewed separately and are not reclassified by this asset provenance statement.

The PNGs were rendered from those original PDFs, then copied without pixel changes into this package. Before/after are immediate adjacent source trees for this one review unit. PNG labels are external Markdown, not painted into the render. The stored OneImage PNGs decode to exactly the raw RGBA hashes recorded at capture. All eight raw before/after pairs differ; the smoothing default-only control is deliberately unchanged. No scaling, cropping, sharpening, alignment, background replacement, or composite montage was used to make the references agree. Every page happens to have an integer 384×256 extent at 144 DPI, so the engines' native dimensions coincide in these controls.

## Engines and configuration

- OneImage: separately built exact source trees and assembly SHA-256 hashes in `manifest.json`. .NET 10.0.15, Debian GNU/Linux 13 x64, `DOTNET_PROCESSOR_COUNT=2`, renderer `maxDegree=1`. Render at 144 DPI with default opaque white background, page index 0, CropBox (MediaBox fallback), rotation 0; smoothing false except explicitly enabled in the smoothing policy comparison. Renderer default area-coverage AA; no overridden text hinting.
- PDFium 153.0.7999.0 through pypdfium2 5.13.0: scale 2, opaque white fill, annotations enabled, default smoothing flags.
- MuPDF 1.26.11 through PyMuPDF 1.26.6: matrix (2,2), alpha=false (white), graphics/text AA level 8, annotations enabled.
- PDF.js 6.5.438, build 0a4153349, Node v24.22.1 and @napi-rs/canvas 1.1.1: viewport scale 2, white canvas, static annotation appearances enabled, `useSystemFonts=false`, `isEvalSupported=false`, `enableXfa=false`, `useWorkerFetch=false`. This is Node Canvas, NOT a browser or WebView. The Node adapter disables ICC; these DeviceRGB/DeviceGray-only controls have no ICC profile. None needs standard-font assets or external CMaps. PDF.js dependency paths remain outside this package.
- Authoring/inspection: Python 3; fontTools 4.61.1 for the original CFF only, pypdf 6.21.4, Pillow 13.0.0. Metrics used NumPy 2.3.5 and SciPy 1.17.0.

All PDFs have one page, MediaBox=CropBox=[0,0,192,128], Rotate=0, no annotations. Reference tools have differing AA, rounding, font and compositing implementations. Reference mismatch is explicitly discussed in the unit README, not hidden or declared erroneous solely because a different engine is closer.

## License boundary

`LICENSE` applies to these independently authored evidence assets and helper sources. Third-party renderer runtimes, fontTools, Python packages, SDK, bundled PDF.js standard fonts and their other dependencies retain their own licenses and are NOT redistributed or relicensed in this package. No engine binary, node_modules, SDK, vendor font, third-party reference PDF, downloaded documentation, upstream expected image or private document is allowlisted.

SHA-256 identifies exact published bytes, not authorship by itself. The source-only construction and reproducible generation are the provenance evidence. The original evidence directory and source trees were preserved during review. Source review reports, build/test logs and raw RGBA are retained locally; the per-unit manifest carries the relevant hashes and checks without publishing those dependencies.

## This unit

Input `image-smoothing.pdf`: SHA-256 `a7f05268cf691a2f541dd4db6edfb00a467ef7607d6c0d79ed52810237f0d050`. Before source tree `8380fd86955698953ee4aa7b7f2f0da22dd9a39b` (08-patterned-stencil-coverage); after tree `e26ce6d8dd234a608c4bcf2d1a2f6f46d1f16b45` (09-image-smoothing). All renderer DLL hashes are in `manifest.json`.
