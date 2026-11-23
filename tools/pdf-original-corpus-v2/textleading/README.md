# ISO-TEXT-LEADING-01

Four original MIT PDFs reuse our independently authored numeric Type 3 font for leading and text-line controls: TL/T* after Tj advancement; TD updating leading; Td preserving leading; and BT resetting matrices while leading persists. No external/system font bytes, existing typeface outlines, upstream fixtures or private documents are used. Font procedures, widths, encoding and ToUnicode are self-contained numeric authoring. This is one reused design, not a new font.

Baseline: verified remote draft #94 head `f56204210b1443f42971dbb32d0c693744b57c76`. Root confirmed matching materialized local head `72886e91de55565fa3fc56608ae0a33c6a442bcd`, tree `c20beb32ff7a278d9e2feecbe5dfd241fc6c84c9`; the worker rechecked local HEAD/tree, instructions and backlog. Only the new work/textleading directory is written. Prior repos, ledgers and checkpoints are preserved.

## Verified results

- 4 byte-unique PDFs, 4 named leading contracts, 1 reused original font and 0 new font designs.
- 24 fresh reference renders: 4 cases × 2 DPIs × 3 engines; 24 passed, 0 failed, 0 skipped.
- 744 of 744 analytic centers pass exactly.
- 49,400 declared interior pixels per engine; 148,200 analytic reference-pixel checks pass. All three pairwise comparisons agree exactly in those regions at both DPIs.
- Independent PDF-operator parsing verifies 24 raw/effective glyph matrices and the leading value at each visible glyph.
- Generator rerun preserves all PDF and manifest bytes. Reused glyph fingerprints match the previous original font.
- 0 upstream inputs fetched/executed, 0 upstream-entry passes, 0 product tests and 0 remote writes. No net-new global behavior count is claimed.

The cases are small complete PDF 1.7 pages (240 by 180 points), with black vector glyphs, no images, annotations, scripts, external resources or recursive glyph calls. Font size40 and widths A600/B500 with .001 font matrix give advances24/20 points. No malformed, stress, crash or security cases are authored.

## Independent layout expectations

- TL40 and successive T* after AB/BA give line origins (30,135),(30,95),(30,55), regardless of current text-matrix advancement.
- Initial TL20 followed by TD(10,-45) changes line origin (30,135) to (40,90) and leading to45; T* reaches (40,45).
- Initial TL40 followed by Td(15,-35) changes origin (30,140) to (45,105), preserving leading40; T* reaches (45,65), not (45,70).
- After a first text object at (30,130) with TL45, a new BT followed by Td(70,90) starts at (70,90); T* uses retained TL45 and reaches (70,45).

Every original glyph ink/counter rectangle is transformed from its declared effective matrix, then inset1 PDF point before reference rendering. Paper control is [4,4,16,16]. These regions are the entire visual assertion set. Glyph boundaries, all undeclared pixels, exact raster edge coordinates and strict full-page equality remain unscored. Exact independently parsed matrices validate authored intent, not rendered edge measurements. Native font weight, hinting, shaping, extraction, rotated leading and external CTM interactions are not validated.

Pinned references: PDFium153.0.7999.0 / pypdfium2 5.13.0; MuPDF1.26.11 / PyMuPDF1.26.6; PDF.js6.5.438 build0a4153349 / Node24.22.3 / @napi-rs/canvas1.1.1. Settings: page0, rotation0, white RGB,72/144 DPI, annotations disabled. PDF.js runs in Node canvas, not a native browser. Versions and empty PDF.js diagnostics are checked in saved logs.

## Reproduce

```sh
python generate.py
python run-references.py /path/to/node_modules/pdfjs-dist
python verify-regions.py
python verify.py
```

Pinned external runtime: `/workspace/scratch/ee1a2fb9052d/pdf-checkpoint-20261123/references/node_modules/pdfjs-dist`; runtime packages are not redistributed. Owned MIT helpers and font numeric source retain earlier headers. Eight MuPDF expected-image candidates are listed in checkpoint.json only after independent three-reference qualification. This worker has not committed goldens or graded products.

clause-index.json separates directly inspected governing ISO32000-1:2008 text from official2020 errata. The latter directly verifies9.4.2/Table106's T* correction, plus9.4.1 and9.3 coarse headings. Full2020 TL/TD/Td and retained-state entries remain pending; their numbers are not inferred. The2008 text directly supports retained text state, BT identity reset and line-position/leading rules. No standard bytes are redistributed or forms submitted.

upstream-metadata-review.json reviews the pinned150-row metadata snapshot without reading upstream inputs/goldens. Relevant font_size/type3/type3_xobject metadata does not establish any complete leading-scene assertion; all upstream associations stay null. This snapshot review is not a full review of the2,811-row inventory.

backlog.json proposes an unclaimed quote-operator slice; it is not started.
