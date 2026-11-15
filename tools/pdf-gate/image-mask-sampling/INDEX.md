# Independent image/mask correctness selection

This narrow selection contains one original correctness report, three unchanged raw PNGs, their original numeric PDF, MIT license and image provenance. The OnePDF additive API and dependent OneImage renderer are separate source review units. Source patches, tests and generator are in their respective source branches, not substituted by this evidence.

Before: OneImage e43 plus unmodified OnePDF d813 source. After: the independent-grid correction and once-per-row dispatch with the separate alpha-interpolation API. Both source units retain their exact reviewed source trees. A fully opaque 7x11 mask must not alter a 3x5 color grid. The after image matches the supplied PDFium output exactly in RGB for this one fixture. The raw full 240x222 PNGs at 72 DPI are unedited. PROVENANCE.md gives the complete original numeric construction, image hashes and limitations.

CORRECTNESS.md is the original readable correctness record and explicitly states its broader raw observations remain local. Only this single fixture's selected images are public here, not the entire 33-fixture / multi-DPI reference collection. The original report includes historical prepublication/first-candidate status language; it is not a claim of current merge readiness or publicly completed performance review.

## Incomplete public performance review

PERFORMANCE-FASTPATH.md is not included. Neither are PERFORMANCE-HELD.md, raw timing records, frozen-input/binary provenance dumps, full image collections or the broader timing harness bundle. No held performance payload is transformed or summarized as a substitute here. No numerical performance conclusion, performance-pass, speedup or no-regression claim is made. Public performance evidence and review remain incomplete. Complete frozen originals and contrary results remain preserved separately.

## Actual dependency gate

The OneImage renderer calls the new PdfImageAlpha.Interpolate property. Current declared OnePDF 1.18.0 and unmodified source 1.22 do not provide it. A normal package build has three expected CS1061 errors. The reported passing renderer tests use explicit patched-source integration, not a released dependency. The API must be independently reviewed and released, both actual OneImage package declarations and dependency prose updated, then ordinary rebased builds/tests rerun. No release number is invented, no package pin is changed, and neither draft is presented as merge-ready.

The renderer is based on historical e43. The reconstructed split chain ending at OneImage PR21 has the same source tree but different ancestry; an explicit later rebase/reconciliation with exact source/diff checks and actual integration tests remains required. No ref is retargeted by this publication.

PUBLICATION-ALLOWLIST.json is authoritative for this selected evidence tree. All original files are unchanged. The original broader source/evidence allowlists are retained locally and are not represented as checksums for this subset. Existing project/dependency licenses remain unchanged. No private/upstream PDF, font, artwork, copied test or expected image is included.
