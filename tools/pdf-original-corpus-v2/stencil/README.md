# Original image-stencil checkerboard controls

Three original MIT PDFs use six authored bytes for a9-by-3 one-bit stencil. Default versus inverted Decode and one XObject reused under red/green current nonstroking colour are independently checked against parsed rawbits, drawstate and analytic interior regions.

All three full cases remain held: MuPDF differs by one RGB byte on painted foreground over black at72/144DPI. White-backed marks and unmarked backgrounds match; PDFium/PDF.js match the declared ideal. There are18 renders:12 full passes,6 disagreements,0 skipped. No selected expected image or product grade is produced, and the original expectations are unchanged.

Reference-only classification passes648 mask-selection decisions. Its42 differing marked-black centres establish the background correlation, not a normative rounding rule or renderer ownership. Independent white-backed controls are a separate subset and close none of these full-case holds.

Run `python generate.py`, `python run-references.py /pinned/pdfjs-dist`, `python verify-regions.py`, `python verify.py`, `python classify.py`. All edges, soft masks, alpha and interpolation variants are outside this focused scope. Verified clauses and current fine-text limits are in `clause-index.json`.
