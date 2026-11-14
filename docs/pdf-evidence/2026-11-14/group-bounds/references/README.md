# Fresh independent reference renders

These original MIT 40-group / 400-group PDFs were rendered without pixel editing at 100 DPI using PDFium 153.0.7999.0 (pypdfium2 5.13.0), MuPDF 1.26.11 (PyMuPDF 1.26.6), and PDF.js 6.5.438 (build 0a4153349) with @napi-rs/canvas 1.1.1 on Node 24.22.1. The PDF.js adapter is an original MIT read-only local WASM host adapter, not native browser execution; no ICCBased profile occurs in these controls.

All six PNGs are full native 834×1112 output. OneImage rounds the same fractional 100 DPI page dimensions to 833×1111. These references are not resized and do not establish equal pixel grids or native browser parity. The actual performance claim continues to rely on exact parent/head OneImage invariance and separately measured timing.

Install reference runtimes externally, not in the fork. Run `python render_controls.py ../fixtures /external/node_modules/pdfjs-dist`; exact versions/settings/input-output hashes and adapter hash are in provenance.json. New source and render outputs are covered by ../LICENSE. No runtime modules, fonts, CMaps or WASM payload is included.
