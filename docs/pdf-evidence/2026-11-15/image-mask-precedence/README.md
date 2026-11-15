# Image-owned soft mask correction

The original opaque-SMask example was invisible before the fix. It now paints at
constant alpha 0.5 over its authored blue backdrop, matching the numerical oracle
and PDFium control. The second example covers partial image alpha under the same
zero graphics-state mask. PNGs are unmodified full-page renders.

These two selected examples illustrate SMask precedence only. The source patch
also implements the explicit/color-key Mask precedence required by ISO 32000-1
11.6.4.3 and independently implemented by PDF.js. PDFium/MuPDF disagree on some
of those cases. The complete 51-render control audit has 37 passes and 14 retained
failures, not an all-engine parity result. Embedded JPX precedence is unchanged
and its separately preserved diagnostic has no passing credit.

Verification: 17 original regression tests (7 fail on baseline, 17 pass fixed),
652 full PDF tests passing with no skips/failures, and a Release solution/analyzer
build with zero warnings/errors. The original minimal repro, its two controls,
and the frozen fourth case pass their unchanged exact checker after the fix.
PDFium's pre-existing two-level precision difference on the fourth is retained.

No native Odin/WebView or native browser check and no performance measurement
are claimed. PDF.js comparison uses Node Canvas, not a native browser. No private
input, third-party fixture source, font or artwork is included.

Files and exact source/assembly identities are in verification.json. Both PDFs
and all generated evidence are original MIT material.
