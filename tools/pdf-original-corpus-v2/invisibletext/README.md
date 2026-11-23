# ISO-TEXT-INVISIBLE-01

Four small original MIT PDF 1.7 files use our owned original numeric Type 3 font to test Tr3 ink suppression, retained text advancement, spacing/TJ interaction, text-object state persistence and subsequent nontext painting. The complete procedures, metrics, encoding and ToUnicode are embedded. No external/system font bytes, existing typeface outlines, upstream/private inputs or borrowed fixtures/goldens are used. One font design is reused, not counted as new.

The verified baseline is remote draft #94 head `688d99e57791656b25b4d5a69f431f9adc60af22`, matching the parent-verified materialized local head `f4a7fe39f28e232654c8ca81c20dd47e9fdd34e5`, tree `a3b4932d73af4e3eee35b7d2cea1be11db5585a9`. The worker rechecked local HEAD/tree, instructions and backlog. Only the new work/invisibletext path is written. No existing repository, global ledger, old helper or checkpoint is changed.

## Exact checkpoint

- 4 byte-unique original PDFs; 4 one-page cases; 8 qualified case/DPI views.
- 24 fresh reference captures: 24 passed, 0 failed, 0 skipped; 0 cases/views held.
- 492 of 492 named sample centers pass at tolerance 0.
- 60,500 scored interior pixels per engine; 181,500 analytic reference-pixel checks pass. Every three-engine pairwise comparison is exact on declared interiors.
- Independent content interpretation verifies 17 glyph records: 11 Tr3/invisible and 6 Tr0/visible, including raw text, line and effective glyph matrices plus rendering mode and spacing/leading state.
- Exactly 1 reference-runner invocation launched 24 engine subprocesses (8 PDFium, 8 MuPDF, 8 PDF.js); all 24 completed with exit 0. Actual starts/finishes/source hashes are recorded in reference-invocations.jsonl. There were no reruns; retained paths are not used to infer counts. Root replays are excluded.
- Numeric regeneration preserves all PDFs, manifest and font design bytes. Font procedure fingerprints match the prior owned design.
- 0 upstream inputs fetched/executed, 0 upstream-entry passes, 0 product tests and 0 remote/global writes. No net-new global semantic coverage count is asserted.

## Contracts and independent math

- Invisible advance: AB under Tr3 has no ink and advances 24+20 points; visible BA after Tr0 begins at x74,94 from initial x30. The line origin stays (30,90).
- Spacing/TJ: with Tc3/Tw7, invisible A plus space advances 27+20; TJ100 subtracts 4, placing B at x73. B advances 23 and TJ-250 adds 10, placing A at106. Its27-point advance leaves visible B at133. A separate ordinary visible B control is anchored at x133,y60.
- Object state: Tr3 persists through ET/BT while matrices reset. Invisible BA in the second object begins at (90,80),(110,80); switching to Tr0 paints AB at (134,80),(158,80).
- Nonclipping: after Tr3 text, ordinary blue page graphics remain visible across the rectangle [20,70,100,60], including areas outside all glyphs. This case scores later paint only; it does not count invisibility beneath the overpaint. No Tr7 operation is present or asserted.

The governing Type 3 exception is important: the directly inspected 2008 9.3.6 text says that mode3 is the only rendering mode that affects Type 3 fonts. Table106 identifies Tr3 as invisible, while clipping rows are separate. Our scope is exclusively Tr3/Tr0; nothing here tests or equates Tr7 clipping behavior. The official 2020 errata directly verifies the 9.3.6 heading and its matrix-update correction for mode3; full 2020 mode-table/Type3-exception rows remain pending.

Font size40, widths A600/B500/space250 and the .001 font matrix give nominal advances24/20/10 points. For the first three cases, original glyph ink/counter rectangles are inset1 PDF point; would-be ink under Tr3 is declared white. The later-paint case instead scores a blue rectangle inset2 points, a separate white outside control and white paper. These are the full visual assertion set. All glyph/paint boundaries, undeclared pixels, exact raster edge coordinates and strict full-page equality are unscored. No extraction, native typeface/font-weight, hinting, shaping, Tr7, rotated writing or external CTM claim is made.

## Reproduce

```sh
python generate.py
python run-references.py /path/to/node_modules/pdfjs-dist
python verify-regions.py
python verify.py
```

PDFJS_ROOT remains `/workspace/scratch/ee1a2fb9052d/pdf-checkpoint-20261123/references/node_modules/pdfjs-dist`. Pinned references: PDFium 153.0.7999.0 / pypdfium2 5.13.0; MuPDF 1.26.11 / PyMuPDF 1.26.6; PDF.js 6.5.438 build 0a4153349 / @napi-rs/canvas 1.1.1 / Node 24.22.3. Settings: page0, one page, rotation0, white RGB, 72/144 DPI, annotations disabled. PDF.js is Node canvas, not a browser. Actual versions and empty diagnostics are verified. Runtime packages are not redistributed.

The runner now records actual invocation events in this new directory. verify.py validates every recorded complete run without inferring counts from files; a deliberate replay appends another 24-call run and must receive revised checkpoint/accounting before being reported as a new result. No historical events are fabricated. The region verifier saves disagreements before returning a failure for held cases. Eight MuPDF expected-image candidates are listed only after genuine three-reference agreement; no expected/golden directory is created and no product grading occurs here.

All streams are complete ordinary inputs, with no images, annotations, scripts, external resources, recursive glyph calls or malformed/crash/security/stress examples. All upstream mappings are empty. clause-index.json records exact evidence limits; no standard bytes are redistributed or forms submitted. backlog.json proposes an unclaimed focused text/CTM slice, not started.
