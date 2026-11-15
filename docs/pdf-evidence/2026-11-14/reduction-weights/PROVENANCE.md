# MIT provenance and exact render settings

All newly authored files in this evidence package, including the numerical image, PDF, generators, adapters, analytical checker, harness, rendered evidence, and documentation, are offered under the included MIT License, copyright 2026 OneImage contributors. The work was independently authored for this control. No private PDF, upstream PDF stream, copied test fixture, expected image, third-party artwork, or font was input. The small PDF-writing scaffold and reference adapters come from the same newly authored MIT control work; they are not copied/adapted from reference engines. No original renderer regression-test source was used to generate the image or analytical expectation.

## Source artwork

`tools/generate.py` writes raw RGB samples using integer arithmetic. For source coordinates x=0…1008, y=0…750:

- R = 24 + floor(180x/1008) + 20((x+y) mod 2)
- G = 34 + floor(170y/750)
- B = 52 + 148((floor(x/37)+floor(y/41)) mod 2)
- Override x<96,y<96 with (25,83,141).
- Override x>=913,y<96 with (187,49,101).
- Override 440<=x<568,y>=655 with (43,179,89).

The generated raw image is Flate-compressed using Python zlib level 9. It is embedded byte-for-byte in a single DeviceRGB, 8-bit PDF image, `/Interpolate false`. The PDF content paints that image with `q 160 0 0 96 16 16 cm /Im Do Q`. There is no text, font, metadata artwork, ICC profile, external resource, annotation, form field, JavaScript, or attachment. Source raw RGB SHA-256 is `538944d6ace0a005b215bc6cf92b87487db25bb196e88a309a76297dd8281ffd`; PDF SHA-256 is `68c53202ec204cb1b28b19e39f23f9d168e60a959a6cd12e7ac12c45e6fab6f3`.

Generator: Python 3.12.14, zlib runtime/build 1.3.2. Checker: NumPy 2.3.5, Pillow 13.0.0, pypdf 6.21.4. The checker uses exact integer overlap endpoints, then double-precision weighted means and nearest-byte rounding. It permits one byte for numerical accumulation in reruns but observed error is exactly zero throughout this capture.

## Engines and geometry

Every capture uses page 1, DPI 144, MediaBox=CropBox=[0,0,192,128] points, rotation 0, opaque white background. Every resulting page is natively 384×256. No dimension conversion, post-render rescale, crop, or image editing is applied.

- OneImage: exact before/head assembly hashes in `manifest.json` and each render JSON, .NET 10.0.15, SDK 10.0.404, degree 1, `SmoothMagnifiedImages=false`. Appearance captures used default tiering settings; timing explicitly disabled tiering/PGO. Timing's output hashes match the appearance captures.
- PDFium 153.0.7999.0 through pypdfium2 5.13.0: scale 2, default antialiasing, opaque-white fill, annotations enabled (none exist).
- MuPDF 1.26.11 through PyMuPDF 1.26.6: matrix(2,2), RGB opaque output, graphics/text antialiasing level 8, annotations enabled (none exist).
- PDF.js 6.5.438 build 0a4153349 through Node 24.22.1 and @napi-rs/canvas 1.1.1: scale 2, ceil viewport dimensions, opaque-white background, static annotation appearances enabled (none exist), no system fonts, XFA disabled, eval disabled, worker fetch disabled. This is Node Canvas, NOT a native browser/WebView. That Node configuration disables ICC; this fixture has only DeviceRGB, so it has no ICC path to test. The package makes no browser, ICC, or all-reference-agreement claim.

Raw reference metadata is in `references/reduction-weights-reference-settings.json`. Exact comparison metrics are in `analytic-checks.json`; differences are retained rather than edited to match. Reference-render outputs are of this wholly original artwork. Dependency implementations, SDK, renderer binaries, fonts, WASM, and packages are not redistributed or relicensed as MIT. Install required dependencies separately from their official sources under their own licenses.

## Captured experiment

The generator has no vendor input. The harness invokes the real internal production `Resize.Area` by a delegate created before timing; it does not replace or copy the resampler. The separate PDF boundary loads a fresh document each operation. The source branch selection follows the audited dimensions and predicate, not a fabricated counter or instrumented production build. All three changed source files were checked against their reviewed SHA-256, and the captured DLLs match the exact split-stage build artifacts. The final harness source was forcibly rebuilt on both sides, renderer/dependency DLL hashes remained unchanged, and its render mode reproduced the originally captured PNG/JSON/raw buffers byte-for-byte. See `verification.json` and `validation/harness-build.json`.

All six processes, all warmup/measured records, input/assembly/output hashes and UTC bounds are retained. The quiet window ran 2026-11-14 23:27:18.254546928Z through 23:27:27.595936089Z, exit 0, under a 120-second cap. Only the prepared measurements ran inside it. The data is one bounded controlled experiment, not a population-level confidence interval or general performance guarantee.
