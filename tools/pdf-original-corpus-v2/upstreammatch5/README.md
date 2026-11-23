# Bounded upstream metadata review

Eight manually selected entries from the pinned official Mozilla manifest were reviewed after an automated description-field search. Three public lookups were used, including a missing README and directory metadata. No upstream fixture, template, font, test source or golden bytes were read.

Result: **0 exact behavioral matches, 0 associations or credited IDs, 0 input executions**. The current originals remain spec-derived.

The closest page entry, `issue7872`, describes indirect MediaBox/CropBox values rather than inheritance. The closest image entry, `issue2770`, describes four-bit image data with an unspecified mask and Decode array; it does not prove a color-key array or pre-Decode masking. No selected description establishes quote/double-quote text operators.

Other reviewed entries describe two-page Type3 image/pattern resource interactions, negative text parameters, or a clipping operation order absent from existing originals. Exact page settings and assertions remain unresolved. A pinned test-directory listing contains no README; test-source files were deliberately not read.

`metadata-review.json` records each exact ID, revision, route metadata, uncredited candidate originals, missing evidence and official URLs. Manifest Git blob: `f78b1186f3da8dcd5bcfba2d00ce341e41084006`; revision: `d4da7f6542bfdf7f256db30f28fa7057c9006ca3`.

`issue7872` is a promising partial-intent candidate for a separate unclaimed behavior for resolving indirect objects used by BOTH page boxes. It does not identify whether the whole arrays, coordinate elements or both are indirect. A new original should test explicit whole-array and coordinate-element variants against a direct control, with independently checked visible dimensions and content placement. Only root can assign a tested behavior association after implementing/running it; inheritance-only results cannot be used. The source scene/page/settings remain unqualified, so no full-case or whole-suite parity is claimed.

Checkpoint attestation: Codex, 2026-11-23 UTC. No remote writes or global ledger edits.

Proposed next unclaimed slice: `ISO-PAGE-BOX-INDIRECT-01` (proposal only; no original authored or executed). The current batch remains limited to its three claimed slices. No further lookups were performed.
