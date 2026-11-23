# Original PDF behavior corpus

One canonical fixture root, `tests/testdata/pdf-original-v2`, follows verified ISO 32000-2:2020 headings. Original PDFs, selected goldens and independent captures live under focused clauses. Catalog and subsystem views point to those same assets. Page-view cases have explicit settings and named assertions; multipage PDFs are stored once.

Current v2 corpus: **80 unique PDFs, 84 page views**. Reference-agreed: **71 PDFs / 75 views**. Nine PDFs/views remain held. There are 150 selected expected PNG paths (130 byte-unique) and 504 independent capture paths (444 byte-unique).

The fifth batch adds 14 original PDFs / 16 views. Page-attribute inheritance and quote operators add 7 PDFs / 9 views. Three endpoint-only colour-key Decode controls also agree. Four non-endpoint reversed-Decode PDFs remain held. New reference results: 96 renders, 88 passes, 8 registered disagreements, 0 skips. New product results: 24 accepted variants pass 590 named assertions and 109,270 scored pixels; 8 held variants are skipped.

Fresh full replay: 504 renders, 482 passes, 22 registered disagreements, 0 skips; every capture is byte-identical to its committed counterpart. All 80 PDFs regenerate byte-identically. Product: 150/150 declared masks pass; strict checks 149 pass/1 preserved round-cap boundary failure; 18 held variants skipped. Ledger stages: 74 strict-pass views, 1 mismatch view, 9 held/generated views. These are original semantic cases, not upstream suite passes.

Agreement requires matched dimensions, exact analytic RGB and pairwise equality among pinned PDFium/PDF.js/MuPDF on predeclared interiors. Other pixels are unscored. Expected images are fresh PDFium captures selected after this agreement; product output and engine majority are never oracles.

All four new non-endpoint RGB8 Decode cases are wholly held: PDFium opaque output differs by one byte from ideal complemented samples and the other engines, including an unmasked control. Reference-only classification passes 288 stored-sample mask decisions and 186 same-engine opaque/control comparisons. These earn no full-case, golden or product pass. Expectations and held originals are unchanged. The separate endpoint-only originals close none of those holds. See `colorkeydecode/classification-results.json`.

The four fractional-alpha cases and prior RGB8 Decode case remain held too. Exact 8-bit output rounding is an observed raster acceptance rule, not a normative ISO byte requirement. The cap probe's unchanged expectation and raw strict failure remain in `stroke/boundary-classification.json`; the grader intentionally returns nonzero. No renderer ownership, production defect or fix is inferred.

## Reproduce

Use Python 3.12, Node 24.22.3 and .NET SDK 10.0.404. References are PDFium 153.0.7999.0/pypdfium2 5.13.0, MuPDF 1.26.11/PyMuPDF 1.26.6, and PDF.js 6.5.438/build0a4153349 with @napi-rs/canvas 1.1.1. Install reference-only dependencies in isolation:

```sh
python -m pip install -r tools/pdf-original-corpus-v2/requirements.txt
npm ci --prefix tools/pdf-original-corpus-v2
python tools/pdf-original-corpus-v2/pipeline.py generate
python tools/pdf-original-corpus-v2/pipeline.py verify
python tools/pdf-original-corpus-v2/pipeline.py catalog
python tools/pdf-original-corpus-v2/pipeline.py references --pdfjs tools/pdf-original-corpus-v2/node_modules/pdfjs-dist --output /tmp/new-pdf-references
```

`family-routes.json` declares generators/reference steps. `routes.json` references canonical family manifests; `routing-manifest-proof.json` proves all 84 resolved cases unchanged. Legacy inline records remain supported. Verification checks capture hashes, analytic masks, engine pairs, page indices and registered holds; duplicate canonical PDF bytes are rejected. Fresh captures use a new output directory and never promote or overwrite goldens automatically.

```sh
dotnet build tools/PdfRender/PdfRender.csproj -c Release -m:1 -p:UseSharedCompilation=false
python tools/pdf-original-corpus-v2/pipeline.py grade --renderer-dll /absolute/artifacts/bin/PdfRender/release/OneImage.PdfRender.dll --acceptance-commit ACCEPTANCE_COMMIT --source-head EXACT_PRODUCT_SOURCE_SHA --output /tmp/new-pdf-product
```

The grader verifies committed original/golden bytes before running the product and selects the actual case page. Remote acceptance `b05c2197fc6a186699fcff3a94842b0b4c22c2cc`, tree `23f443626f7ff7a3ca55b708ed673228ce9f5364`, matches local pre-grading acceptance `e0461e70d5dc52f71f70ee246a7e5bd4043f8397`. Preserve the known strict nonzero result; report mask evidence separately.

Measured evidence: `batch5-checkpoint.json`, `batch5-reproduction.json`, `product-batch5-strict-results.json`, `product-batch5-mask-results.json`, `batch5-product-provenance.json`. Prior checkpoints/canonical assets remain preserved.

Exact product baseline: OneImage main `eb47d5a0155bdb38f6fc7b08a5fa7279fd004a12` with declared OnePDF/Fonts 1.18.0 packages. Five managed assembly hashes match the previous recorded build. No fresh build, unmerged OnePDF fork head or patch-stack validation is claimed; AOT/WASM/platform merge gates remain unchanged.

The bounded metadata review manually inspected 8 entries using 3 public lookups. There are 0 exact current matches/associations and 0 upstream inputs executed or IDs credited. The 2811 rows remain inventory. `upstreammatch5/metadata-review.json` records precise gaps: indirect boxes are described but indirection form/pages/settings and current inheritance-scene correspondence are unqualified. The indirect-box behavior is a separate unclaimed proposal. Full standard-rule enumeration remains incomplete.

Storage uses verified 2020 headings/cross-references with fine-text access limits recorded. PDF 1.7 originals retain verified 2008 governing clauses. Our reused Type 3 font has no external font bytes and tests positioning, not native weight. No borrowed/private fixtures or goldens, known vulnerability/crash reproductions, private patches, production changes, merges, releases, workflow or settings changes. No Windows, WebView-speed, native-font-weight, speech or full-suite parity claim.

Checkpoint attestation: Codex, 2026-11-23 UTC. New original sources/assets MIT. GitHub API commits are unsigned; Signed-off-by is an authorship attestation, not a cryptographic signature.

## Sixth batch before product grading

Adds16 independently authored original MIT PDFs and18 page views across indirect page boxes, inherited Rotate, invisible text and image stencils. Fifteen views agree; three checkerboard stencil views remain held because MuPDF differs one RGB level on marked cells over black. Separate white-backed controls agree and close none of those holds. New108 reference renders:102 passes,6 registered disagreements,0 skips. No new product result is claimed yet.

Current reference verification:96 unique PDFs,102 views,84 agreed PDFs/90 agreed views,12 held views;612 captures,584 passes/28 known disagreements/0 skips. All96 PDFs regenerate byte-identically. issue7872 remains discovery only: exact source observable/settings and scene are unestablished; no association or upstream credit.
