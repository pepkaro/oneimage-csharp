# Pattern-internal blend backdrop

All PDF bytes and geometric content in this selection are independently authored and MIT licensed. No external PDF, font, image, artwork, or upstream test fixture is embedded.

The 96 × 96 point input paints an opaque RGB (.2,.6,.8) backdrop. A single tiling-pattern cell then paints RGB (.8,.4,.2) with internal Multiply inside the square [24,24,72,72]. Render page zero at 72 dpi on opaque white, with no rotation or crop change. The PDF paints its own background.

ISO 32000-1:2008 §11.6.7 treats the tiling pattern as an implicit non-isolated group. Its Normal-only cached-cell optimization does not apply. The opaque interior must be the component product (.16,.24,.16), about RGB (41,61,41). Primary source: https://opensource.adobe.com/dc-acrobat-sdk-docs/pdfstandards/PDF32000_2008.pdf

Interior checks cover the complete 36 × 36 pixel square inset six points from the painted edges, with one RGB level of tolerance:

- OneImage before: (204,102,51), 1,296 mismatched pixels.
- OneImage fixed: (41,61,41), zero mismatches.
- MuPDF: (41,61,41), zero mismatches.
- PDFium: (40,61,40), zero mismatches.
- PDF.js Node Canvas: (204,102,51), 1,296 mismatches. It is not a supporting reference for this pattern.

The included direct and non-isolated-form controls meet the product expectation in all three references and OneImage. The isolated-form control meets its separate source-color expectation (204,102,51). Those three controls and a Normal-pattern control remain pixel-identical in OneImage before and after the fix.

`generate.py` recreates these four PDFs plus five additional original numerical controls when copied into an empty directory and run with Python 3. It writes the fixed expectations before rendering. The broader nine-case reference experiment has 15 passes and 12 failures across three engines; repeated-cell and multi-object disagreements are preserved, not treated as reference conformance. These selected images show only the independently supported minimal case.

The new renderer path evaluates backdrop-dependent cell copies together, then applies the object's outer opacity, mask and blend once. Normal-only cached rendering remains unchanged. Between-cell paint order is unspecified by §8.7.3.1; the overlapping-copy regression uses identical commuting operations rather than assuming a universally correct instance order.

A separate existing limitation remains: non-isolated knockout groups are treated as isolated. An original direct-Multiply diagnostic still fails in both baseline and fixed OneImage and passes all three references. The knockout equivalence tests preserve existing behavior; they do not establish full knockout conformance.
