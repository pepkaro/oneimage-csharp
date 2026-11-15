# Closed stationary round caps

These controls, their numeric geometry, the Type 3 glyph program, generator and new
regression tests are original MIT work. No private PDF, external artwork, vendor
fixture or existing font is an input. Run `python3 tools/solid-closed-caps/generate.py
<output-directory>` to write the 81 small PDFs and their SHA-256 manifest.

ISO 32000-1:2008 8.5.3.2 defines a degenerate round-capped subpath as one filled
circle at its point. Closing a stationary path must not add a second outline to
that circle. Section 8.4.3.6 continues to control whether the initial dash is on.
The tests use numeric geometry, exact equivalence controls and analytical disc
area bounds, not a reference renderer's antialiasing pixels.

The PDF-specific conversion omits stationary closes only when its separate cap
pass owns round caps. It compares original double coordinates before float
conversion. Ordinary paths, other cap styles, fills, core stroke construction and
non-Type3 glyph-outline conversion retain their existing behavior. Truncated raw
line/curve operands retain the original core outline because the cap pass does
not flush their unfinished subpath. No general antialiasing or width policy changes.

This is a separate change on top of the zero-length dash-gap correction. Keep the
two fixes in separate commits/PRs. The dash normalization and phase code is unchanged.

Reference evidence must use matching full-page boxes, DPI, rotation, annotations
and background, and retain raw images without crop, scaling, alignment or retouching.
PDFium and MuPDF disagree on some degenerate shapes and their edge coverage. Their
outputs are comparisons, not analytical oracles. Native PDF.js/WebView was not
available; Node Canvas omits zero-length positive dots and cannot establish parity.

Two additional positive-length ON-dash controls (`tiny-on` and `moving-cubic-on`)
raise the same pre-existing Boolean-coordinate ImageLimitException before and
after this change. Retain these as render errors, not successful pixel matches.
They are a separate follow-up and are not fixed here.
