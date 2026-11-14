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

Input `outline-knockout.pdf`: SHA-256 `9fd24ab5a39aef02dd77ed8a02bf64d71bff7c392bfdf9eddf9e8271ed9f541c`. Before source tree `7ebd2700f295e2fad543a71492640725cb632fed` (11-device-hairlines); after tree `526fd552634589207c235d0f734c39b020dc6686` (12-outline-knockout). All renderer DLL hashes are in `manifest.json`.

## Font and asset provenance

The generator creates the font solely from explicit points (80,100), (690,100), (770,340), (470,760), (150,620), closes the polygon, and uses fontTools FontBuilder and T2CharStringPen. It loads no vendor/system font or upstream test asset. fontTools installed and declared version = **4.61.1**. The standalone CFF is **168 bytes**, SHA-256 **31f319407fee190319ffceeaecabc6f9a12aa2009bede5318505b9da6a95b83d**. Its bytes exactly match the embedded FontFile3 stream. Decompilation finds only `.notdef` and `wedge`; the former is width 900 + endchar. The latter is width 900, moveto, one horizontal line and three relative lines, closed by endchar. Its private dictionary is empty, global-subroutine count zero, and the charstrings contain no hint, hintmask, counter-mask, subroutine-call, or external dependency operations. No borrowed outline is present in the reviewed source or CFF.

These three PDFs derive from numeric shapes, scalar settings, and one constant RGB sample; the font is the original polygon above. The supplied generator and corpus LICENSE declare MIT, and each PDF embeds the original-artwork MIT notice. That supports an independently authored MIT fixture bundle. It is not a claim to relicense renderer/tool binaries or their dependencies, or a legal clearance of the entire historical repository. Publish raw generated PDFs/PNGs, generator, license, provenance, and exact manifest; do not add unrelated vendor fixtures or bundle reference engine installations.
