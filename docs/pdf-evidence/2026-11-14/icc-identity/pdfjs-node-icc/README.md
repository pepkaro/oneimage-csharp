# Fresh PDF.js ICC diagnostic

These untouched full-page PNGs were rendered from the unchanged independently authored MIT ICC fixtures. Both are 480×120 at 96 DPI on white. The custom Node Canvas host adapter is included; the PDF.js runtime stays external. See provenance.json for exact versions, integrity, WASM hash, input/output hashes, options and transform controls.

This is **Node Canvas with a custom read-only local WASM host adapter**, not browser execution. The adapter changes no PDF.js engine source. It implements only the synchronous local runtime-byte read needed by the pinned ICC loader. It cannot fetch arbitrary paths or network URLs.

Unlike the excluded earlier fallback output, these images actually apply the ICC transform: qcms loads without warnings and 39,600 pixels change relative to ICC-disabled output (maximum channel delta 80). Changing only the embedded profile description leaves the two corrected PNGs byte-identical. Description invariance alone was not considered proof of ICC conversion.

Install official pdfjs-dist@6.5.438 and @napi-rs/canvas@1.1.1 in an external directory using npm --ignore-scripts --save-exact. Run under Node24.22.1:

    node render-pdfjs-local-icc.mjs /external/node_modules/pdfjs-dist wide-original.pdf wide-original.png 96

Repeat for wide-renamed.pdf. No AI-generated, retouched or cropped evidence is included. Runtime licenses remain separate from the new MIT assets and adapter.
