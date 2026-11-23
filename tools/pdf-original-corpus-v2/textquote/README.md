# ISO-TEXT-QUOTE-01

Four original MIT PDF 1.7 files exercise single-quote and double-quote text operators, explicit equivalent controls, persistent spacing and line-origin behavior. Every file embeds the complete owned original Type 3 numeric font: vector rectangle glyphs, blank space procedure, widths, encoding and ToUnicode. No external/system font bytes, existing typeface outlines, upstream/private PDFs, borrowed fixtures or goldens are used. One design is reused; no new font design is counted.

The preserved remote baseline is draft #94 prefix `1cd8573`, as supplied by root. The read-only materialized prior repo has HEAD `9b4b91126e54a9c9ba0ae79e57fe007e36274ee9` and tree `22257be8ecf9bc14a30db43c721db374e0da7fd0`; the worker rechecked both, plus prior instructions/backlog. A full remote author SHA was not independently resolved by this worker and is not invented. Only the new work/textquote directory is written; old repos, global ledgers and verifiers are untouched.

## Exact checkpoint counts

- 4 unique original PDFs and 4 one-page cases; 8 distinct case/DPI views.
- 24 fresh reference captures: 4 cases × 2 DPIs × 3 engines; 24 passed, 0 failed, 0 skipped. All 8 views are three-reference qualified; 0 held views/cases.
- 924 of 924 declared sample-center checks pass at tolerance 0.
- 60,470 scored interior pixels per engine; 181,410 analytic reference-pixel checks pass. All three pairwise comparisons are exact within the same declared interiors.
- Independent PDF-operator interpretation checks text, line and effective glyph matrices plus Tc/Tw/leading state at all 30 visible glyphs. Authored programs contain 2 single-quote and 3 double-quote operations, with explicit controls in the first two cases.
- Deterministic regeneration preserves every PDF and manifest byte; font procedure fingerprints match the prior original font.
- 0 upstream inputs fetched/executed, 0 upstream-entry passes, 0 product tests and 0 remote writes. Net-new global semantic coverage is not inferred from file counts.

## Named contracts and math

- Single quote matches explicit T* + Tj: translated columns start at x25/125, with baselines 130 then85 and BA second origins x45/145. Prior AB advancement does not shift the new line origin.
- Double quote aw7/ac3 matches explicit Tw7/Tc3/T*/Tj. The new row uses A-space-B, so B starts47 points after A: 24+3+10+3+7. Operands have distinct values to detect swapped spacing roles.
- After double quote, Tc3/Tw7 persist into Tj and single quote. At y95, A-space-B occupies origins x30,77 and leaves current x100; following AB begins at x100,127 while line x remains30. Single quote returns to x30,53 at y50.
- A shifted Td line origin(50,100) feeds double quote, yielding BA at(50,55),(72,55). Tc2/Tw5 survive ET/BT while matrices reset; the next object at(115,80) has Bx158 for A-space-B.

All pages are 240 by 180 points. Font size 40 and original widths A600/B500/space250 in a .001 matrix give nominal advances24/20/10 points. The manifest separately declares text_matrix, line_matrix, glyph_matrix, character_spacing, word_spacing and leading for every visible glyph.

Ink and counter rectangles are computed from numeric glyph shapes and explicit effective matrices, then inset 1 PDF point before generating references. Paper control is [4,4,16,16]. These regions are the full visual assertion set. Every glyph boundary and undeclared page pixel is unscored; exact renderer edge positions and strict full-page equality are not asserted. Structural matrix checks verify authored operator intent, not native raster edges. Native font weight, hinting, shaping, extraction correctness, vertical/rotated writing and external CTM interactions remain untested.

## Reproduce

```sh
python generate.py
python run-references.py /path/to/node_modules/pdfjs-dist
python verify-regions.py
python verify.py
```

Pinned external runtime: `/workspace/scratch/ee1a2fb9052d/pdf-checkpoint-20261123/references/node_modules/pdfjs-dist`. References are PDFium 153.0.7999.0 / pypdfium2 5.13.0; MuPDF 1.26.11 / PyMuPDF 1.26.6; PDF.js 6.5.438 build 0a4153349 / Node 24.22.3 / @napi-rs/canvas 1.1.1. Settings: page 0, rotation 0, white RGB, 72/144 DPI, annotations disabled. PDF.js uses Node canvas, not a browser. Native versions and actual saved PDF.js versions/empty diagnostics are verified. Runtime packages are outside this corpus.

Owned MIT font source and adapters retain earlier headers. The region verifier saves disagreement evidence before returning a nonzero status for held cases. Eight MuPDF expected-image candidates are listed in checkpoint.json after the three-reference gate; none were committed or product-graded by this worker. Streams are small, complete and valid, with no images, annotations, scripts, external resources or recursive glyphs. No malformed/crash/security/stress cases are included.

## Standards and mapping boundary

ISO 32000-1:2008 9.4.3/Table 109's full quote rows were inspected directly; supporting 9.4.2 and 9.3.1 cover line movement and retained text state. Official 2020 PDF Association errata verifies the 9.4.3 Text-showing operators heading and directly exposes the 9.4.2/Table 106 T* correction. It does not expose the full quote rows; fine 2020 quote-operator wording remains pending, not assumed. Type 3 edition numbering is 2008 9.6.5 versus verified 2020 9.6.4. No standards bytes are redistributed or forms submitted.

All upstream associations remain null. Prior metadata review established no exact relevant scene scope; filenames or broad font-family labels do not earn mapping credit. backlog.json proposes an unclaimed invisible-text advance control, not started.
