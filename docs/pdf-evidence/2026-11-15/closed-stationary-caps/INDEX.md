# Closed stationary round-cap correctness evidence

This distinct seven-file correction depends on the published dash-phase source at 570389fe5d554b1bbc367c1a813c91b61c246fe7. It gives exactly stationary closed PDF round strokes one cap owner instead of synthesizing the same circle in both core stroke conversion and the PDF cap pass. Original double coordinates, dash phase, transforms, width/hairline policy and malformed-path fallback are preserved. Core drawing and ordinary positive-length geometry are not changed.

## Before, after and controls

Five original MIT numeric PDFs are selected: closed-solid, open-solid, rectangle-solid and two retained failing positive-path controls, tiny-on and moving-cubic-on. The three successful controls each include full unmodified before/head/PDFium/MuPDF images at 72 and 144 DPI. Page boxes match [0,0,192,144], rotation is zero, and background is white. These generated PDFs contain no annotations. The OneImage runner uses its default View/appearance settings; the independent references explicitly disable annotations. PNGs have no crop, alignment, recoloring or in-pixel labels. Reference pins and render options are in reference-settings.json.

The radius-9 solid closed disc changes from 263.0902 to 251.6706 square points at 72 DPI and equals the unchanged open control. At 144 DPI it changes from 259.2588 to 252.9137 and again equals the open control. The analytic circle area is 254.4690 square points; existing flattening loss remains within the independent perimeter bound. Reference pixels are not copied as expected test values. PDFium omits the zero-size rectangle, and other degenerate boundary disagreements are retained. No native PDF.js, browser or WebView parity is claimed.

Full metrics cover 81 original cases at both DPIs: 18 intended changes, 61 unchanged RGB outputs and two matching errors per DPI. The selected public raw images/PDFs are only the five named cases; complete unchanged source-generation code is in the source PR. Full original raw collections remain preserved separately. The two errors are not image matches: baseline and head both throw the same ImageLimitException for positive closed-path ON-dash cases. Their reference images, input PDFs, error identity and complete render logs are included. This patch does not fix them.

## Tests

Final PDF suite: 732/732 pass, including 36 new rows plus 696 prior rows. The exact same final 36-test assembly against accepted prior production binaries fails 21 and passes 15; original failure logs remain included. Focused existing core stroke suite: 23/23. The failed malformed-path prototype log remains included; final malformed controls pass without weakening assertions. No full codec, whole-repository, AOT or cross-platform rerun is claimed.

Apply solid-closed-cap-fix.patch only after the dash-phase source. Verify the seven source SHA-256 values in source-files.json, then build and run the repository's Release PDF test suite. Published source tree is 3117d5903d73c7878793bd59110b6dab2db30047. The source PR contains the independent generator, tests, MIT license and original numeric controls; no external fonts, fixtures, artwork or private pages are required.

## Selected scope and limitations

This is a correctness-only public selection. No raw performance records or numerical performance conclusions are included; no speedup, performance-pass or no-regression claim is made. Full original timing, adverse samples, binary provenance and all unselected original evidence remain preserved locally. No specifically denied payload from another unit is included, transformed or summarized here. PUBLICATION-ALLOWLIST.json lists the exact selected files and every omitted original path. The original full-package manifest is not represented as describing this selected tree. Existing project and dependency licenses remain unchanged.
