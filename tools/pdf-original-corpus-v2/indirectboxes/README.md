# Indirect page-box objects

Three original MIT PDF 1.7 files isolate how BOTH MediaBox and CropBox values resolve: direct numeric arrays, whole-array indirect references, and indirect numeric coordinate elements. No inherited page attributes, fonts, images or annotations are used. The direct control and two reference placements share the same new vector content.

MediaBox is [0,0,220,180]. CropBox is [24,18,184,138], giving a 160x120pt visible viewport with lower-left origin(24,18). Red[32,28,28,20] appears at display[8,10,28,20]. A blue rectangle crosses the lower crop boundary; yellow crosses the right crop boundary; green and white controls distinguish origin/placement. Black content lies outside CropBox. Eight predeclared inset regions and center assertions avoid all paint and viewport edges.

## Reproduce

```sh
bash reproduce.sh /absolute/path/to/pinned/pdfjs-dist
```

The generator is deterministic. Structural validation uses pypdf 6.21.4 and checks raw whole-array versus element reference forms, each resolved numeric box, visible dimensions/origin, one page, explicit resources and absent annotations/rotation/UserUnit. Fresh reference subprocesses are pinned to PDFium 153.0.7999.0/pypdfium2 5.13.0, MuPDF 1.26.11/PyMuPDF 1.26.6, and PDF.js 6.5.438/build0a4153349 with Canvas 1.1.1/Node 24.22.3. Settings: page 0, 72/144 DPI, visible CropBox, white, annotations off, no resampling.

Only exact analytic RGB plus three-engine pairwise agreement on the predeclared regions qualifies a case. Missing outputs, dimensions or disagreements are held; no majority or product oracle is used. Worker output contains reference captures only; root owns golden promotion, acceptance commit and product grading.

## Standards and limits

Official 2020 errata verifies 7.3.10 Indirect objects and explicitly permits references as array elements/dictionary values. It also verifies 7.7.3.3 Page objects and the 7.9.5 rectangle cross-reference. The PDF 1.7 governing clauses 7.3.6, 7.3.10, 7.7.3.3/Table30 and 7.9.5 were inspected in the official 2008 specification. These page boxes impose no direct-only exception. Complete 2020 page-box wording remains pending; exact antialiasing pixels are not normative requirements. See clause-index.json for verified titles, source URLs and limits.

This slice covers one positive normalized box pair with no inheritance, rotation, UserUnit changes, nested reference chains, negative origins or malformed/missing/cyclic references. Combined whole-array-plus-coordinate indirection is a separate unclaimed proposal. It does not prove all rectangle consumers or full renderer parity.

issue7872 remains DISCOVERY ONLY. Its metadata does not establish source indirection form, pages, settings or exact assertion. No source PDF/template/font/test-source/golden bytes were read, and no ID is mapped or credited. No product run, remote write, fix, gate change, merge or release is performed here.

Checkpoint attestation: Codex, 2026-11-23 UTC. New source PDFs and reference output MIT. The primary clause proposed for canonical storage is 7.3.10 Indirect objects, cross-tagged with page objects and rectangles.
