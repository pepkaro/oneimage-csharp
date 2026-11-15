# Original knockout-group evidence

These four PDFs and their geometric generator are original MIT material. Comparison images show the same input at 72 dpi, enlarged with nearest-neighbor sampling solely for readability. No external document, artwork, font program or private file is included.

- **single-nonisolated-knockout:** sole Multiply source (0.8,0.4,0.2) over authored backdrop (0.2,0.6,0.8). ISO 32000-1 11.4.6 predicts approximately (41,61,41); before (204,102,51), after (41,61,41). All 1,296 declared interior pixels fail before and pass after. MuPDF, PDFium and PDF.js agree on this control.
- **single-isolated-knockout:** isolation control, unchanged source color (204,102,51); all three reference engines agree.
- **overlap-ais-false:** the second object has opacity 0.25 but full shape, so it removes the preceding sibling and blends only with the initial backdrop. After matches the independent equation and MuPDF/PDF.js. PDFium differs; this is not a unanimous-reference claim.
- **translucent-initial-backdrop:** a nonisolated knockout group inside an isolated parent with a half-alpha backdrop. After matches the independent equation and MuPDF/PDFium. PDF.js differs.

The full investigation retains all fourteen original diagnostics and all 42 reference results: 20 pass their predefined numeric regions and 22 differ. AIS, masks, nested groups, zero-opacity shape and patterns have reference disagreements. Those are not omitted, retuned or counted as unanimous conformance. This selection illustrates one compositing fix, not four independently credited corpus behaviors.

To reproduce the original inputs, run `python3 generate.py` in an empty directory. It creates `pdf/` plus `expectations.json`; the four selected root PDFs are byte-identical to their generated counterparts. Render each with the source version and 72 dpi on white. The before version is e43ee264954a177ff01a16584625a3dea79244fa plus the separately reviewed pattern-blend patch; after additionally applies this knockout patch.

Specification: https://opensource.adobe.com/dc-acrobat-sdk-docs/pdfstandards/PDF32000_2008.pdf, sections 11.4.6,11.4.8 and11.6.4.
