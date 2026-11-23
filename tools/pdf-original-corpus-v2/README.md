# Original PDF behavior corpus

One canonical fixture root, `tests/testdata/pdf-original-v2`, follows verified ISO 32000-2:2020 headings. PDFs and selected goldens live under their focused clauses. The generated catalog and subsystem view point to those same assets. Each page-view case has named assertions and explicit settings; a multipage PDF is stored once.

Current v2 corpus: **66 unique PDFs, 68 page views**. Independently agreed: **61 PDFs / 63 views**. Five PDFs/views remain held. There are 126 selected expected PNG paths (110 byte-unique) and 408 independent capture paths (360 byte-unique). The fourth batch adds 10 unique originals, 12 views, 72 agreed references and 24 expected-image paths.

A fresh full replay produced 394 reference passes and 14 registered disagreements, with 0 skips and 408 byte-identical captures. All66 originals regenerate byte-identically. Product comparison passed 126/126 declared masks; strict results are 125 passes and 1 preserved round-cap boundary mismatch;10 held variants were skipped. All 24 new variants passed 392 named assertions and 152,520 scored pixels. A second product run after lossless routing JSON compaction reproduced all 126 images byte-for-byte.

Agreement requires matched dimensions, exact analytic RGB and pairwise equality among the three pinned engines on predeclared interiors. Selected expected images are fresh PDFium captures only after agreement. Other pixels are unscored; product output and engine majority are never oracles. The strict point probe remains unchanged and intentionally makes the grader return nonzero. See `stroke/boundary-classification.json`.

All four fractional alpha cases remain held: source-backed implementation models explain rounding differences without establishing a normative ISO byte oracle. The prior RGB8 Decode case remains held too. See `alpha-classify/README.md`. No production fix or renderer ownership is inferred.

## Reproduce

Use Python 3.12, Node 24.22.3 and .NET SDK 10.0.404. Reference versions are PDFium 153.0.7999.0/pypdfium2 5.13.0, PDF.js 6.5.438/build0a4153349 with @napi-rs/canvas 1.1.1, and MuPDF 1.26.11/PyMuPDF 1.26.6. Install isolated reference dependencies:

```sh
python -m pip install -r tools/pdf-original-corpus-v2/requirements.txt
npm ci --prefix tools/pdf-original-corpus-v2
python tools/pdf-original-corpus-v2/pipeline.py generate
python tools/pdf-original-corpus-v2/pipeline.py verify
python tools/pdf-original-corpus-v2/pipeline.py catalog
python tools/pdf-original-corpus-v2/pipeline.py references --pdfjs tools/pdf-original-corpus-v2/node_modules/pdfjs-dist --output /tmp/new-pdf-references
```

`family-routes.json` declares generators and reference steps. Generation uses temporary directories and checks canonical PDF hashes. Verification checks capture hashes, analytic masks, pairwise agreement, actual page indices and registered holds; duplicated canonical PDF bytes are rejected. Fresh captures use a new output directory and never promote or overwrite goldens automatically.

```sh
dotnet build tools/PdfRender/PdfRender.csproj -c Release -m:1 -p:UseSharedCompilation=false
python tools/pdf-original-corpus-v2/pipeline.py grade --renderer-dll /absolute/artifacts/bin/PdfRender/release/OneImage.PdfRender.dll --acceptance-commit ACCEPTANCE_COMMIT --source-head EXACT_PRODUCT_SOURCE_SHA --output /tmp/new-pdf-product
```

The grader verifies committed original/golden bytes before product execution and selects the case's actual page. Use remote acceptance `6a5d56793da8d7c3375ceb1f8554f2054f4a5ad0`, tree `6e44219885322baa1f75d462e44ba16c60a775fe`, identical to local pre-grading acceptance `0a56d97e3721cf28295d4a81d330bfe3a2d1e123`. The earlier local acceptance is preserved. The strict grader returns nonzero for the documented cap probe; report accepted-mask evidence separately and preserve the raw strict failure.

Measured evidence: `batch4-checkpoint.json`, `batch4-reproduction.json`, `product-batch4-strict-results.json`, `product-batch4-mask-results.json`, `batch4-product-provenance.json`. Prior batch checkpoints remain preserved. Routing/report JSON compaction changes whitespace only; `routing-format-proof.json` records parsed equivalence.

The exact product baseline is OneImage main `eb47d5a0155bdb38f6fc7b08a5fa7279fd004a12` with declared OnePDF/Fonts 1.18.0 packages. All five managed assembly hashes match the prior recorded build. No fresh build, unmerged OnePDF fork head, AOT/WASM/Windows gate or patch-stack validation is claimed. Existing merge gates remain.

The 2811 upstream rows are inventory: 0 upstream inputs executed and 0 IDs mapped/credited. `batch4-mapping-review.json` records missing exact scene/route evidence. New cases are independently authored standard-derived semantics; they do not approximate arbitrary upstream files. Full standard-rule enumeration remains incomplete. Verified 2020 headings/cross-references and unavailable fine-text limits are explicit; PDF 1.7 originals use separately verified 2008 governing clauses. The font is our own MIT Type 3 design, with no external font bytes; positioning evidence does not establish native text weight.

No borrowed/private fixtures, goldens or fonts, known vulnerability/crash reproductions, private patches, production changes, merges, releases, workflow or settings changes. WebView speed, Windows, speech and full-suite parity remain untested here.

Checkpoint attestation: Codex, 2026-11-23 UTC. New original sources and assets MIT. GitHub API commits are unsigned; Signed-off-by is an authorship attestation, not a cryptographic signature.
