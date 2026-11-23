# Original PDF behavior corpus

One canonical fixture root, `tests/testdata/pdf-original-v2`, follows verified ISO 32000-2:2020 headings/subclauses. Original PDFs, selected goldens and independent captures are stored under focused clauses. Catalog and subsystem views reference the same assets. Cases have named assertions and explicit settings; multipage originals are stored once.

Current v2 corpus: **96 unique PDFs, 102 page views**. Reference-agreed: **84 PDFs / 90 views**. Twelve PDFs/views remain held. There are **180 expected PNG paths (152 byte-unique)** and **612 independent capture paths (528 byte-unique)**.

The sixth batch adds **16 original PDFs / 18 views**: indirect boxes, inherited Rotate, invisible text and image stencils. Thirteen PDFs / 15 views agree; three checkerboard stencils remain held. New references: **108 executed, 102 passed, 6 registered disagreements, 0 skipped**. New product: **30 accepted variants passed 526 named checks and 232,920 scored pixels; 6 held variants skipped**.

A fresh full replay produced **612 renders, 584 passes, 28 registered disagreements and 0 skips**; every capture matches its committed counterpart byte-for-byte. All 96 PDFs regenerate byte-identically. Product: **180/180 masks passed; strict checks 179 passed / 1 preserved cap-boundary failure; 24 held variants skipped**. Ledger: 89 strict-pass views, 1 mismatch view and 12 held/generated views. These are original semantic cases, not upstream suite passes.

Agreement requires matched dimensions, exact analytic RGB and pairwise equality among pinned PDFium/PDF.js/MuPDF on predeclared interiors. Other pixels are unscored. Goldens are fresh PDFium captures selected after agreement; product output and engine majority are never oracles.

Three new checkerboard stencils are wholly held: MuPDF foreground over black is one RGB level below the declared ideal at both DPIs. Reference-only classification passes 648 mask-selection checks and records 42 differing marked-black centres. These earn no full-case, golden or product credit. Separate WHITE-backed originals validate only their narrower scope and close none of those holds. Original expectations remain unchanged. See `stencil/classification-results.json`.

All nine earlier reference holds remain, including fractional alpha and non-endpoint Decode. Exact 8-bit rounding is an observed raster acceptance rule, not a normative ISO byte requirement. The old cap probe, unchanged white expectation and raw strict failure remain in `stroke/boundary-classification.json`; the grader intentionally returns nonzero. No new product defect, renderer owner or fix is inferred.

## Reproduce

Use Python 3.12, Node 24.22.3 and .NET SDK 10.0.404. References: PDFium 153.0.7999.0/pypdfium2 5.13.0, MuPDF 1.26.11/PyMuPDF 1.26.6, and PDF.js 6.5.438/build0a4153349 with @napi-rs/canvas 1.1.1. Install isolated reference dependencies:

```sh
python -m pip install -r tools/pdf-original-corpus-v2/requirements.txt
npm ci --prefix tools/pdf-original-corpus-v2
python tools/pdf-original-corpus-v2/pipeline.py generate
python tools/pdf-original-corpus-v2/pipeline.py verify
python tools/pdf-original-corpus-v2/pipeline.py catalog
python tools/pdf-original-corpus-v2/pipeline.py references --pdfjs tools/pdf-original-corpus-v2/node_modules/pdfjs-dist --output /tmp/new-pdf-references
```

`family-routes.json` declares generators/reference steps; `routes.json` references canonical family manifests. `routing-batch6-proof.json` verifies all 102 resolved entries. Capture-index compaction changes whitespace only. Verification checks source/capture hashes, analytic masks, engine pairs, actual page indices and registered holds; duplicate canonical PDF bytes are rejected. Fresh captures use a new output directory and never overwrite or promote goldens automatically.

```sh
dotnet build tools/PdfRender/PdfRender.csproj -c Release -m:1 -p:UseSharedCompilation=false
python tools/pdf-original-corpus-v2/pipeline.py grade --renderer-dll /absolute/artifacts/bin/PdfRender/release/OneImage.PdfRender.dll --acceptance-commit ACCEPTANCE_COMMIT --source-head EXACT_PRODUCT_SOURCE_SHA --output /tmp/new-pdf-product
```

The grader checks committed original/golden bytes before product execution and selects the actual page. Remote acceptance `f2cce2ff49883aca9a9c1152af6a1a195a50113f`, tree `be06cd2735e34afac59e74df455cb1057ea5423e`, matches local pre-grading acceptance `be90ac06f2bf3879cd5866514444079514a35fbc`. Preserve the known strict nonzero result and report mask evidence separately.

Measured evidence: `batch6-checkpoint.json`, `batch6-reproduction.json`, `product-batch6-strict-results.json`, `product-batch6-mask-results.json`, `batch6-product-provenance.json`. Prior canonical assets and checkpoints remain preserved.

Product baseline remains OneImage main `eb47d5a0155bdb38f6fc7b08a5fa7279fd004a12` with declared OnePDF/Fonts 1.18.0 packages. Five recorded managed assembly hashes match; no fresh build, OnePDF fork-head, private patch-stack or AOT/WASM/platform validation is claimed. Existing merge gates remain unchanged.

`issue7872` is discovery only: permitted metadata does not establish the exact source indirection form, actual page/observable settings or unseen full scene. Our original direct, whole-array and coordinate-element variants have explicit local settings, but no association or upstream credit is promoted. The 2,811 rows remain inventory: zero upstream inputs executed or IDs credited. See `batch6-mapping-review.json`; full standard-rule enumeration and exact suite qualification remain incomplete.

Storage follows verified 2020 headings/cross-references; PDF 1.7 originals retain inspected 2008 governing rules and explicit fine-2020 access limits. Tr3 Type3 invisibility and advancement are distinguished from Tr7, which is out of scope. Own font design contains no external font bytes and does not establish native font weight or extraction parity.

No borrowed/private fixtures or goldens, known vulnerability/crash reproductions, private patches, production changes, merges, releases, workflows or settings changes. No Windows, WebView-speed, speech or full-suite parity claim.

Checkpoint attestation: Codex, 2026-11-23 UTC. New original sources/assets MIT. GitHub API commits are unsigned; Signed-off-by is an authorship attestation, not a cryptographic signature.
