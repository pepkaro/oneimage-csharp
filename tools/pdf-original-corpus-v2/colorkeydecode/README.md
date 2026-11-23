# Colour-key masking before reversed Decode

Four original MIT RGB8 PDFs share36 newly authored sample bytes, reversed Decode and an opaque checkerboard. An unmasked control, two exact-key controls and an inclusive-range control distinguish stored-sample masking from ideal complemented-value matching. Predeclared2-point-inset cell interiors, frame and paper are scored at72/144DPI.

All four full cases are **held**: PDFium differs by one RGB byte on opaque reversed-Decode colors, including the unmasked control. MuPDF/PDF.js match the ideal complement criterion. There are16 full-render passes and8 disagreements among24 renders. No selected expected image or product grade is produced; no expectation is changed to match any engine.

Reference-only component classification passes288 mask-selection checks and186 same-engine opaque/unmasked-control comparisons. These do not validate a held full case or establish a normative8bit rounding oracle. No renderer ownership or source/binary root cause is proven. Endpoint controls are a separate, explicitly narrower sub-slice; these original held files remain unchanged.

Run `python generate.py`, `python run-references.py /pinned/pdfjs-dist`, `python verify-regions.py`, `python verify.py`, `python classify.py`. Boundaries and soft masks are untested. Verified2008 governing rules and2020 citation limits are in `clause-index.json`.
