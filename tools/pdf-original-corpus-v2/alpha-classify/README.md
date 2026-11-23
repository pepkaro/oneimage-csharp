# Fractional alpha quantization classification

This slice creates no PDFs or accepted goldens. It reuses four original MIT controls already held in the canonical corpus, without changing their bytes, expectations or status.

| Alpha | PDFium backdrop channel | MuPDF backdrop channel | PDF.js / pinned Node Canvas |
|---|---:|---:|---:|
| 0.25 | 192 | 192 | 191 |
| 0.6 | 102 | 101 | 102 |

These are the channels whose opaque source value is zero over white. Source channels equal to 255 remain 255. Fill and stroke agree within each engine at both DPIs.

Pinned renderer implementation evidence explains the measurements: PDFium truncates the alpha byte and blends over 255; MuPDF expands that byte to a 256-step weight and uses integer channel arithmetic; PDF.js passes alpha to Canvas. Original arithmetic models match all 24 fresh PDF captures and 138,240 independently declared interior pixels. Eight direct Canvas controls reproduce the PDF.js values without a PDF parser. All 24 PDF capture files remain byte-identical to the existing references.

This is a source-backed compatibility explanation, not a normative pixel oracle or a demonstrated conformance defect. No engine majority selects a golden. All four cases remain held and ungraded against the product. Edge coverage, groups, color management, other alpha values and browser Canvas remain outside this classification.

`source-evidence.json` records immutable implementation source URLs, file hashes, reported runtime versions and binary hashes. Third-party implementation files are not redistributed. The models are original arithmetic controls. The PDFium installed metadata does not carry a source hash; its official release names chromium/7999, whose source snapshot was resolved independently. No complete binary rebuild or in-process branch trace was performed, so source-to-binary correspondence has that explicit limit.

Offline verification:

```sh
python tools/pdf-original-corpus-v2/alpha-classify/verify.py --repo .
```

Fresh direct controls and PDF rerendering use the same pinned external runtime:

```sh
node tools/pdf-original-corpus-v2/alpha-classify/canvas-control.mjs /absolute/pdfjs-dist /absolute/controls
python tools/pdf-original-corpus-v2/alpha-classify/classify.py --repo . --pdfjs /absolute/pdfjs-dist --output /new/pdf-diagnostics
```

The classifier uses the committed direct-control evidence; the first command can independently reproduce it in a separate directory. `source-evidence.py` optionally refetches only the seven pinned implementation files and records hashes; it never retrieves test or PDF assets. The common corpus reference command separately rerenders every original.

Checkpoint attestation: Codex, 2026-11-23 UTC. Original models and controls are MIT; referenced engines retain their own licenses. Zero upstream IDs credited and zero product runs in this slice.
