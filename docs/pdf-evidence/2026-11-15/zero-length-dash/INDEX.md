# Zero-length dash phase: selected correctness evidence

This is a correctness-only draft with all 97 original numeric-control PDFs and
complete raw before/head/PDFium/MuPDF visual pages, source/test provenance and
selected correctness logs. CORRECTNESS-ALLOWLIST.json identifies every included
original file and omitted original-publication path. Included bytes are unchanged.

The raw timing dataset and all performance reports/conclusions are NOT included.
Specifically, timing-focus-runs/1-head-ordinary-3.json remains unpublished, with no
transformed copy or substitute summary. Performance review is incomplete. No
speedup, performance-pass or no-regression claim is made. runtime-versions.txt and
all other absolute-workspace-path records are deferred too.

The long pixel-assertion failure log, its transport parts and the separate solid
closed-cap reproduction are also outside this concise selection. The complete
frozen package remains preserved separately. No original full-package manifest is
presented as describing this selected tree. No denied content is rerouted.

Correctness ties to base e43ee264954a177ff01a16584625a3dea79244fa and source tree
7dc1abbaf27a58d68245f4cfc11f6b41a6d5a6a6. The seven-file patch SHA-256 is
0d82699b4331625694abb1086a733086995d9eaacd8c3bf36554acffc587dd01; source hashes,
full patch, original test/generator code and selected correctness logs are included.

The exact-head PDF suite is 696/696; all 61 new rows pass. The same final test
assembly fails 27 and passes 34 on untouched baseline production DLLs. Core stroke
passes 23/23. Full core remains 3,191 passed, one contextual cache failure and eight
skips; this is not a core-wide pass or proven baseline failure. Isolated cache-class
runs pass 3/3 on each side. Independent original40 integration is 816 passed and
one separate background skip, not a combined-stack result. Its metadata patch is
preserved but not applied to this source PR or the frozen foundation.

The phase-19 OFF control changes from 1,076 ink pixels to blank, matching PDFium
and MuPDF exactly. The phase-3 ON control remains visible and byte-identical.
Across all 97 controls, 34 OFF outputs change and 63 remain identical. Raw pages are
384x288 at 144 DPI with matching page boxes, zero rotation and white background.
Reference edge/parity disagreements remain visible. These are controls, not 97
independent feature classes or native-browser parity. Node Canvas cannot serve as
an independent oracle for the degenerate positive controls.

New PDFs, generators, regressions and evidence are independently authored MIT.
Existing project/dependency licenses and package versions are unchanged.
