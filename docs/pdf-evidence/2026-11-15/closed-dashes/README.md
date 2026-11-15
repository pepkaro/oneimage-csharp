# Two separate closed-dash correctness units

These are proposed correctness-review changes, not merge-ready or performance-cleared changes. Source and visual review remain pending. No speed, timing-neutrality, complete viewer-parity or native-browser equivalence claim is made.

## 1. Core construction repair

Apply `short-closed-strokes.patch` to exact commit `e43ee264954a177ff01a16584625a3dea79244fa`. It is independent of the separate PDF stationary-dash/closed-cap changes.

The core splitter was handing the stroker a repeated closing endpoint while also marking the dash closed. The repair passes the original distinct vertices and only treats the whole figure as ON when it started ON. Generic core joining policy, geometry limits and exception behavior are otherwise unchanged.

Correctness: 412/412 scoped core Drawing tests; 648/648 full PDF tests; 732/732 existing dash/cap integration tests with the core replaced. The exact final new regression assemblies fail before the repair: 68 of 69 core rows fail (the real safety-limit control already passes), and all 13 new PDF rows fail. The explicit repeated-return-to-start case is included. Original tiny/cubic PDFs no longer throw, but this unit alone leaves the seam shape mismatch visible.

## 2. PDF-only seam policy

Apply `pdf-dash-seams.patch` after unit 1. Its core and PDF companion changes must ship together. It does not require the stationary-dash/closed-cap source patches, but their combination was tested.

PDF strokes request separately capped dash pieces at a closed subpath's seam. Generic drawing retains its original joined policy by default. The previous internal stroke entry point is preserved. Both positive-width and hairline PDF strokes use the policy after dash normalization; all-zero and tiny-pattern solid fallbacks remain unchanged.

Correctness: 690/690 full standalone PDF tests, 412/412 scoped core Drawing tests, 787/787 combined PDF tests, and 732/732 old-PDF-binary compatibility tests. Of the exact final 42 new seam rows, 31 fail against the preceding core-fixed implementation and 11 are unchanged controls. Tests use original analytic or equivalent-path geometry, not copied reference pixels.

Across 61 original controls at each of 72 and 144 DPI, there are no render errors; 22 successful outputs change and 39 stay byte-identical. Candidate and PDFium each match all 60 equivalent-description groups internally. MuPDF matches 56, with retained differences for a line following Close and malformed all-zero dash fallback. Antialiasing also differs. These are limits on parity, not hidden matches.

Relevant primary specification: ISO 32000-1:2008 sections 8.4.3.6, 8.5.3.2 and Table 59, https://opensource.adobe.com/dc-acrobat-sdk-docs/pdfstandards/PDF32000_2008.pdf . Specification text is not included.

## Small original visual selection

Open `visuals/gallery.html`. It shows two original numeric PDFs, each with native 144-DPI output from the core repair, the additional PDF seam policy, PDFium and MuPDF. The original implementation throws for both cases, so there is no fabricated baseline image. Images have not been cropped, resized, aligned or retouched. Each page is 192 by 144 points, with matching page boxes, zero rotation, white background and no annotations.

References: PDFium 153.0.7999.0 through pypdfium2 5.13.0; MuPDF 1.26.11 through PyMuPDF 1.26.6. PDF.js Node Canvas is not evidence of native-browser equivalence here. All included fixture geometry, tests, generators and rendered selections are original MIT work. No private/vendor input assets or fonts are included.

## Performance and remaining work

Performance readiness remains unresolved. The first core comparison showed adverse solid-rectangle observations. A later same-binary diagnostic and untimed code trace did not establish their cause; they prove neither a repeatable algorithmic slowdown nor timing neutrality. Every adverse observation remains preserved locally. The PDF seam unit has no performance pass. Raw timing samples, native-code output, binary metadata and hash dumps are deliberately excluded from this small selection.

A separate tiny-positive-coordinate float-collapse omission remains open and has an independent original repro/control handoff. It is not bundled as a third fix. No unrelated codec suite, remote publication, merge or package release is represented by this artifact.
