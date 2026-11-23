# Original PDF visual corpus, batch 2

This corpus adds35 independently authored MIT PDFs and68 selected expected PNG paths for34 reference-agreed cases. One RGB8 Decode case is held, with no golden and no product grading. No upstream or private fixture, font, expected image or test source was read or copied. References are newly rendered from these originals, not upstream goldens.

The physical canonical root is `tests/testdata/pdf-original-v2`, ordered by verified ISO32000-2:2020 clause headings. Each case directory holds one focused original, named DPI variants, and six independent reference captures. Encoding variants are separately scored routes, not separate global behaviors. Fine-grained2020 clauses whose full text could not be checked are explicitly pending in the clause records; broader verified headings are used for storage. Image fixtures declare PDF1.7 and have independently checked ISO32000-1:2008 governing references. Geometry fixtures declare PDF2.0. No standard text is redistributed.

[Behavior catalog](CATALOG.md), [subsystem view](SUBSYSTEMS.md), [machine-readable cases](cases.json), [suite coverage](suite-coverage.json), [raw source metadata](inventory.json), and [reconciliation](reconciliation.json) are versioned together. `routes.json` records individually named sample/region assertions and settings. The views link to the same cases and fixtures; they do not duplicate coverage.

## Gate and limitations

Generate original → render PDFium, PDF.js and MuPDF with visible CropBox, declared Rotate/UserUnit, page0,72/144DPI, white background and no annotations → compare each with independent analytic samples/interiors and all three pairs with each other → accept original+selected capture together → commit them → only then grade the product against that committed expectation. No engine-majority vote or product-derived oracle. A selected capture is accepted only over the declared mask, not every image pixel.

Geometry excludes a one-device-pixel band around analytically declared region boundaries. Image samples score each24-point cell inset by2points plus a separate paper region. Exact RGB and dimensions are required; tolerance0. Boundary pixels and untested regions remain unscored. RGB channel Decode has a genuine one-value PDFium disagreement at both DPIs; its six captures remain evidence, with no accepted expected image. The geometry UserUnit adapter had two earlier incorrectly scaled captures; correction metadata is preserved and those calls are not engine defects or selected references.

ISO specifies object/coordinate/decoding semantics; identical8-bit renderer quantization is our measured comparison rule, not a claim that ISO mandates these raster bytes. All upstream IDs are metadata only. No upstream bytes were fetched/executed, no scene route is fully qualified, and no upstream ID earns parity credit. A future many-to-many association must name the exact pinned ID, page/settings, asserted contract and evidence. A filename or shared feature name is insufficient. The current2811 rows remain unmapped; safety/eligibility is unknown without further vetted metadata. Security/malformed/crash/stress reproductions are outside scope.

## Reproduce

Use Python3.12, Node24.22.3 and .NET SDK10.0.404. Install reference-only dependencies in an isolated environment:

```sh
python -m pip install -r tools/pdf-original-corpus-v2/requirements.txt
npm ci --prefix tools/pdf-original-corpus-v2
python tools/pdf-original-corpus-v2/pipeline.py generate
python tools/pdf-original-corpus-v2/pipeline.py verify
python tools/pdf-original-corpus-v2/pipeline.py catalog
python tools/pdf-original-corpus-v2/pipeline.py references --pdfjs tools/pdf-original-corpus-v2/node_modules/pdfjs-dist --output /tmp/original-pdf-fresh-references
```

`generate` reconstructs all PDFs in a temporary directory and checks the canonical byte hashes. `verify` independently checks committed captures, masks, analytic expectations, all pairs and held status. `references` uses a new output directory and never promotes or overwrites goldens automatically. Clean reference reproduction makes210calls; historical exploratory calls add2. Runtime versions: PDFium153.0.7999.0/pypdfium2 5.13.0, MuPDF1.26.11/PyMuPDF1.26.6, PDF.js6.5.438 build0a4153349, canvas1.1.1. Node and binding licenses remain their respective upstream licenses, not this corpus MIT license.

Build the existing renderer using ordinary managed compilation and its declared OnePDF/Fonts1.18.0 packages:

```sh
dotnet build tools/PdfRender/PdfRender.csproj -c Release -m:1 -p:UseSharedCompilation=false
python tools/pdf-original-corpus-v2/pipeline.py grade --renderer-dll /absolute/artifacts/bin/PdfRender/release/OneImage.PdfRender.dll --acceptance-commit COMMITTED_REFERENCE_SHA --source-head EXACT_PRODUCT_SOURCE_SHA --output /tmp/original-pdf-product
```

`grade` first verifies that every accepted PDF/golden is byte-identical to the named existing commit, then scores68 product variants. It returns failure on any scored mismatch. The held case's two variants are explicitly skipped. Latest strict result:67pass/1boundary-probe mismatch; accepted-mask classification:68pass/0fail. The unmodified point expectation and raw strict failure are preserved in product-final-strict-results.json and stroke/boundary-classification.json. No normative defect or fix is inferred from this out-of-mask probe. CI can call these commands; no hosted workflow/settings or AOT gate was changed. Existing AOT/WASM/full platform merge gates remain separate. These measurements do not establish native text weight, WebView performance, speech, Windows execution or full-suite parity.

Checkpoint attestation: Codex,2026-11-23 UTC. Independently authored sources and generated assets are MIT. This named attestation is not a cryptographic Git signature. Remote commit verification status must be reported as returned by GitHub.
