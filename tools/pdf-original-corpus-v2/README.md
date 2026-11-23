# Original PDF behavior corpus

One canonical fixture root, `tests/testdata/pdf-original-v2`, follows verified ISO 32000-2:2020 clause headings. The current review checkpoint contains 56 independently authored MIT PDFs, 51 reference-agreed cases and five held cases. Accepted cases have 102 selected expected PNG paths. The machine counts distinguish byte-unique images, capture paths, PDF variants and tested behaviors.

[Catalog](CATALOG.md), [subsystems](SUBSYSTEMS.md), [case ledger](cases.json), [backlog](backlog.json), [suite gaps](suite-coverage.json) and [artifact audit](reconciliation.json) reference the same canonical assets. The 2,811 pinned source IDs remain metadata: zero upstream inputs executed and zero IDs credited. Exact scene scope must be proven before any mapping earns credit. The bounded [mapping review](batch3-mapping-review.json) records known metadata and the specific missing contracts.

## Reference-first gate

Author an original; render PDFium, PDF.js and MuPDF with matched settings; compare all three with independent analytic interiors and each other; accept original plus selected capture; commit them; only then grade the product against that commit. No engine-majority vote or product-derived oracle. Exact RGB and dimensions are required on predeclared masks. Other pixels remain unscored. Geometry boundary bands were defined before rendering.

Settings are page 0, visible CropBox, declared Rotate/UserUnit, 72 and 144 DPI, white background, annotations off. References are PDFium 153.0.7999.0 / pypdfium2 5.13.0; MuPDF 1.26.11 / PyMuPDF 1.26.6; PDF.js 6.5.438 build 0a4153349 / Canvas 1.1.1 / Node 24.22.3. Runtime guards reject drift. Dependency licenses are their own; no engine source or runtime is redistributed as MIT fixture content.

## Third batch

Seven new PDFs cover resource-category isolation and text scaling/rise. Their 42 reference variants all pass. Fourteen goldens were committed before product grading. All 14 new product variants pass their accepted masks and 240 named assertions.

Fresh cumulative reproduction: 336 renders, 322 passes, 14 registered disagreements, zero skipped. Every capture reproduces byte-identically. All 56 PDFs regenerate byte-identically. Product masks: 102 passed, zero failed; strict probes: 101 passed, one prior cap-boundary mismatch. Ten reference-held variants are skipped.

The five held cases are the prior RGB8 Decode case and four fractional-alpha controls. Alpha classification adds no PDFs or goldens: source-backed arithmetic matches 24 fresh held-case captures on 138,240 declared interior pixels, and eight direct Canvas controls isolate the Node backend. This explains implementation quantization, not a normative ISO pixel oracle. All four fractional cases remain held and ungraded. Source/binary correspondence limits and the absence of in-process tracing are explicit. See [classification](alpha-classify/README.md).

The previous cap probe remains inside its predeclared excluded boundary band. Its unchanged expectation, raw strict failure and [classification](stroke/boundary-classification.json) remain. The strict grader intentionally returns nonzero; mask evidence is reported separately. No conformance defect, renderer ownership or production fix is inferred from these findings.

The exact product baseline is OneImage main `eb47d5a0155bdb38f6fc7b08a5fa7279fd004a12` with declared OnePDF/Fonts 1.18.0 packages. Unchanged managed assembly hashes match the prior recorded build. No new product build or unmerged fork stack is claimed. Existing AOT, WASM and platform merge gates remain unchanged.

## Reproduce

Use Python 3.12, Node 24.22.3 and .NET SDK 10.0.404. Install reference-only dependencies in isolation:

```sh
python -m pip install -r tools/pdf-original-corpus-v2/requirements.txt
npm ci --prefix tools/pdf-original-corpus-v2
python tools/pdf-original-corpus-v2/pipeline.py generate
python tools/pdf-original-corpus-v2/pipeline.py verify
python tools/pdf-original-corpus-v2/pipeline.py catalog
python tools/pdf-original-corpus-v2/pipeline.py references --pdfjs tools/pdf-original-corpus-v2/node_modules/pdfjs-dist --output /tmp/new-pdf-references
python tools/pdf-original-corpus-v2/alpha-classify/verify.py --repo .
```

`family-routes.json` declares generators and reference steps. Generation uses temporary directories and checks canonical PDF hashes. Verification checks capture hashes, analytic regions, engine pairs and registered holds. Fresh references use a new output directory and never promote or overwrite goldens automatically.

```sh
dotnet build tools/PdfRender/PdfRender.csproj -c Release -m:1 -p:UseSharedCompilation=false
python tools/pdf-original-corpus-v2/pipeline.py grade --renderer-dll /absolute/artifacts/bin/PdfRender/release/OneImage.PdfRender.dll --acceptance-commit ACCEPTANCE_COMMIT --source-head EXACT_PRODUCT_SOURCE_SHA --output /tmp/new-pdf-product
```

The grader verifies committed input/golden bytes before product execution and returns nonzero for any strict mismatch. The documented prior cap probe is preserved; do not silently waive it. Current evidence is in `batch3-checkpoint.json`, `batch3-reproduction.json`, and the two `product-batch3-*` result files.

PDF 1.7 originals retain separately verified 2008 governing clauses. Official PDF Association errata verifies storage headings and selected rule text; unavailable finer 2020 wording stays pending. Text scale/rise uses our own Type 3 font, not external font bytes, and tests positioning rather than native weight or TrueType/OpenType parity. Full standard-rule enumeration remains incomplete.

No borrowed/private fixtures, fonts, goldens, test sources, known vulnerability/crash reproductions, private patches, releases, merges, workflow or settings changes are included. Windows, WebView speed, native text weight, speech and full-suite parity remain untested here.

Checkpoint attestation: Codex, 2026-11-23 UTC. New original sources and assets are MIT. GitHub API commits are unsigned; Signed-off-by is an authorship attestation, not a cryptographic signature.

The third-batch acceptance is published at `30c3fce95e2a6c62b9b39fef8914423c5cb9e849`, with tree `2b66282c0eb3fcc6efcb62713ea23c77786099fe`, identical to local acceptance `8d2ebc949af9e86ff7a3ac46aff604643ff02f8b` committed before product grading.
