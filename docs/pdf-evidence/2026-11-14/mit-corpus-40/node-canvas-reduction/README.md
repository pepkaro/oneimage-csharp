# Direct Node Canvas degenerate-stroke reduction

This is new original MIT adapter/test code. It contains no PDF interpreter and no
upstream test content. `reduce.mjs` draws the exact zero-length segment with
round cap24 and dash[13,14], phases0,3,19,-3, plus solid, through both Path2D and
the immediate context API. A one-pixel-long segment is the positive control.

Actual @napi-rs/canvas1.1.1 on Node24.22.1 result: all ten zero-length combinations
paint0 ink pixels. Both APIs paint506 pixels for a one-pixel-long segment in
solid/on phase, and0 in off phase. Thus the zero-length omission observed in the
PDF.js Node reference can be reproduced at the Node Canvas layer without PDF.js.
It is not evidence of a PDF.js parser/engine defect. Native browser behavior is
not established. Results and exact settings are in report.json; PNGs are raw.

    node reduce.mjs /external/node_modules/pdfjs-dist

The npm directory supplies the external pinned @napi-rs/canvas dependency; no
third-party runtime is included. This bounded investigation does not change the
frozen initial40-case patch or its independent positive-control expectation.
