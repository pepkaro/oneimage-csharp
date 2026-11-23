# Original PDF behavior corpus

The canonical fixture root is `tests/testdata/pdf-original-v2`, ordered by verified ISO 32000-2:2020 clause headings. It contains 56 independently authored MIT PDFs, 102 selected expected PNG paths for 51 reference-agreed cases, and five held cases. The expected PNGs contain 78 byte-unique images; 294 independent capture paths contain 264 byte-unique images. Encoding variants are separate routes, not extra global behaviors.

[Behavior catalog](CATALOG.md), [subsystem view](SUBSYSTEMS.md), [case ledger](cases.json), [clause backlog](backlog.json), [suite gaps](suite-coverage.json), [source inventory](inventory.json), and [artifact audit](reconciliation.json) all refer to the same canonical assets. No fixtures are duplicated between views. Source IDs are metadata only: zero upstream inputs executed and zero upstream IDs credited. No filename-based or speculative mapping earns coverage.

## Reference-first pipeline

Author an original → render PDFium, PDF.js and MuPDF with matched bounds/settings → compare all three with independent samples/interiors and each other → accept the original and selected capture together → commit them → grade the product against that committed expectation. No engine-majority vote or product-derived oracle. A selected capture is accepted on its declared mask; other pixels are unscored.

Every case uses page 0, 72 and 144 DPI, white background, visible CropBox, declared Rotate/UserUnit and no annotations. Scored RGB and dimensions must match exactly. Geometry has predeclared boundary exclusions; other families use independently declared interior rectangles and named samples. Exact 8-bit quantization is a route criterion, not a claim that ISO mandates identical raster bytes.

Five cases remain held without goldens or product grading: the prior RGB8 Decode case and four fractional-alpha controls. The alpha endpoints and q/Q restoration pass independently; these do not establish fractional compositing parity. The prior round-cap strict point probe differs inside a predeclared excluded edge band. Its raw failure, unchanged expectation and independent classification remain in `stroke/boundary-classification.json`. No normative defect or renderer ownership was inferred.

## Current checkpoint

The continuation adds 14 PDFs: three resource-name cases, four original-font positioning cases and seven alpha controls. Ten new cases qualify for 20 goldens. New references: 84 run, 72 passed, 12 disagreed, zero skipped. New product variants: 20 run, 20 passed, zero failed; eight reference-held variants skipped.

Cumulative fresh reference reproduction: 294 run, 280 passed, 14 disagreed, zero skipped. All 294 capture files reproduce byte-identically. Product accepted masks: 88 passed, zero failed. Including strict point probes: 87 passed, one previously documented boundary mismatch; ten reference-held variants skipped. The strict grader intentionally returns nonzero for that preserved probe.

The exact product baseline is OneImage main `eb47d5a0155bdb38f6fc7b08a5fa7279fd004a12` with declared OnePDF/Fonts 1.18.0 packages. Unchanged prior managed assemblies were hash-verified before reuse; their package/assembly digests are recorded. This does not validate the unmerged fork stack. No production fix, workflow, settings, AOT or merge-gate change is included.

PDF 1.7 fixtures retain separately verified ISO 32000-1:2008 governing references. Official PDF Association errata verifies the 2020 storage headings and some rule wording; finer clauses remain explicitly pending where full text is unavailable. The original Type 3 font uses authored numeric outlines, metrics, encoding and ToUnicode, with no external font bytes. It tests specified positioning, not native text weight or TrueType/OpenType parity.

## Reproduce

Use Python 3.12, Node 24.22.3 and .NET SDK 10.0.404. Reference-only dependencies are pinned; native adapters reject version drift. Reference versions: PDFium 153.0.7999.0 / pypdfium2 5.13.0; MuPDF 1.26.11 / PyMuPDF 1.26.6; PDF.js 6.5.438 build 0a4153349 / Canvas 1.1.1. Engine dependencies retain their own licenses and are not redistributed as MIT corpus assets.

```sh
python -m pip install -r tools/pdf-original-corpus-v2/requirements.txt
npm ci --prefix tools/pdf-original-corpus-v2
python tools/pdf-original-corpus-v2/pipeline.py generate
python tools/pdf-original-corpus-v2/pipeline.py verify
python tools/pdf-original-corpus-v2/pipeline.py catalog
python tools/pdf-original-corpus-v2/pipeline.py references --pdfjs tools/pdf-original-corpus-v2/node_modules/pdfjs-dist --output /tmp/new-pdf-reference-output
```

`generate` regenerates all PDF hashes in temporary directories. `verify` checks canonical capture hashes, independent analytic interiors, all three engine pairs, accepted images and registered holds. `family-routes.json` declares generators and reference steps. `references` uses a new directory and never promotes or overwrites goldens automatically.

```sh
dotnet build tools/PdfRender/PdfRender.csproj -c Release -m:1 -p:UseSharedCompilation=false
python tools/pdf-original-corpus-v2/pipeline.py grade --renderer-dll /absolute/artifacts/bin/PdfRender/release/OneImage.PdfRender.dll --acceptance-commit ACCEPTANCE_COMMIT --source-head EXACT_PRODUCT_SOURCE_SHA --output /tmp/new-pdf-product-output
```

The grader verifies that accepted PDFs/goldens match an existing commit before executing the product. It returns nonzero on a strict mismatch, including the documented cap probe. Compare the separately recorded mask and strict results; do not silently waive a failure. Existing platform, NativeAOT and browser-WASM merge gates remain separate and unchanged.

No upstream/private PDF, font, golden, test source, vulnerability, malformed/crash/stress reproducer or private patch is included. The scoped behavior backlog is incomplete; inventory completion is not suite parity. Windows execution, WebView speed, native text weight and speech remain untested here.

Checkpoint attestation: Codex, 2026-11-23 UTC. Independently authored sources and generated assets are MIT. GitHub API commits are unsigned; Signed-off-by is an authorship attestation, not a cryptographic signature.

## Third batch, before product grading

Seven new originals cover resource-category isolation and horizontal scaling/text rise. All42new reference variants pass;14new expected PNGs are accepted. Alpha classification creates noPDFs or goldens: source-backedmodels match24freshheld-PDFrenders and138240interiorpixels;8directCanvascontrols reproducePDF.jsbackendvalues. Thefourfractionalalphacasesstayheld because no normativebyteoracleisestablished. See alpha-classify/README.md and batch3-checkpoint.json. Product grading follows this acceptancecommit.
