# WHITE-backed stencil controls

Three original MIT PDF 1.7 files under logical ISO-IMAGE-STENCIL-01 isolate ordinary stencil behavior on opaque WHITE backdrops. They use an independently authored 9-by-3, 1-bit grid stored in six raw bytes: 65 00 3A 80 97 00. There are no external assets, fonts, upstream/private inputs, borrowed fixtures/goldens, soft masks or alpha channels.

The cases are stencil-white-default-red, stencil-white-inverse-red and stencil-white-reuse-red-green. Default Decode is omitted (effective [0 1]); inverse Decode is [1 0]. The reuse case draws the same mask XObject twice in separate q/Q blocks, setting red and then green current nonstroking color. Each draw paints its own opaque white backdrop first. This explicitly tests per-draw tint rather than a cached colored image.

## Measured checkpoint

- Exactly 3 byte-unique PDFs, 3 one-page cases and 6 case/DPI views.
- First and only capture run: 18 references, 18 passed, 0 failed, 0 skipped; 0 WHITE-backed cases/views held.
- Actual event log: 6 PDFium, 6 MuPDF and 6 PDF.js invocations; 18 completed with exit 0, no reruns. Retained capture paths are not used to infer invocation counts.
- 762 of 762 named center checks pass at tolerance 0.
- 113,600 declared interior pixels per engine; 340,800 analytic reference-pixel checks pass. All three pairwise comparisons agree exactly on the same interiors.
- Independent parsing verifies 108 draw/cell bit decisions, Decode polarity, no ColorSpace, BPC1, white fills, q/Q state, image placement and per-draw tint. There are 13 marked cells in default red, 14 in inverse red and 13+13 in the reused red/green case.
- Generator rerun preserves all PDF and manifest bytes.
- 0 product runs, 0 upstream-entry passes, 0 global/remote writes and 0 expected/golden promotions.

WHITE-backed scope is strict. Root's three checkerboard stencil originals remain HELD, with their expectations unchanged. This worker did not read, rerun or modify those fixtures. Agreement here closes none of those cases and does not resolve the reported painted foreground channel difference over black. scope.json makes the distinction explicit; no full stencil-family parity is asserted.

## Independent geometry and semantics

Rows are independently encoded MSB-first, with two bytes per nine-sample row and seven padding bits. Both Decode variants use the same six-byte grid. Default0 marks; inverse1 marks. Unmarked cells leave the opaque white backdrop unchanged. Each marked cell takes the current draw's endpoint RGB color.

Each source cell covers 16 by 16 points; a 2-point inset yields a 12-by-12 scored cell. Single placements start at (32,80); reuse placements start at (32,104) and (32,24). Every image is 144 by 48 points. An 8-point opaque white border surrounds each image; each frame strip is independently inset 2 points. The separate paper control is [4,4,16,16], inset from its declared clear page area. All cell/frame/paper regions and named centers are frozen before capture.

Only declared interiors are scored. Image/cell/frame boundaries and all undeclared pixels are unscored. Black or colored backdrops, general compositing quantization, interpolation, other bit depths and full-page equality are not validated. No current-product output is used as the oracle.

## Reproduce

```sh
python generate.py
python run-references.py /path/to/node_modules/pdfjs-dist
python verify-regions.py
python verify.py
```

PDFJS_ROOT: `/workspace/scratch/ee1a2fb9052d/pdf-checkpoint-20261123/references/node_modules/pdfjs-dist`. References: PDFium 153.0.7999.0 / pypdfium2 5.13.0; MuPDF 1.26.11 / PyMuPDF 1.26.6; PDF.js 6.5.438 build 0a4153349 / @napi-rs/canvas 1.1.1 / Node 24.22.3. Matched settings are page 0, one page, rotation 0, white RGB, 72/144 DPI, annotations disabled and image interpolation false. PDF.js runs in Node canvas, not a browser. Actual versions and empty diagnostics are verified.

The runner appends actual capture start/finish events with source hashes. The region verifier saves disagreements before returning nonzero for held cases. Replays append new events and require updated accounting before reporting. No expected/golden files or candidate promotions are made by this worker; outputs are reference evidence only. Previous files, root ledgers and repositories are untouched.

## Standards and next scope

The directly inspected 2008 8.9.6.2 Stencil Masking text (printed pages 213–214, PDF pages 221–222) specifies no ColorSpace, BPC1 and Decode polarity/current-color semantics. The official 2020 errata verifies the 8.9.6.2 heading; full algorithm text remains pending. No full-standard download, form/cart submission or redistribution occurred.

For a possible next unclaimed slice, 2008 8.9.6.3 Explicit Masking was inspected directly: an ordinary base image may reference an external 1-bit image mask through Mask. The proposal in backlog.json uses matched small dimensions and white-backed endpoint colors, avoiding soft alpha and preserving existing checkerboard holds. It is not started. No upstream mapping is asserted from filenames or metadata alone.
