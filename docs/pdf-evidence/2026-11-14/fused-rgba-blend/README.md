# Fuse normal RGBA brush blending

This change fuses the ordinary non-solid RGBA Normal/SrcOver path into a single pass rather than repeatedly converting/copying channels. Opacity, coverage and the generic fallback remain unchanged. It is a performance-path change, not an appearance fix.

Exact review base d173137e576bc3f2cfad6aae409c3552a19e4a54, head feaac99059a7373bc33e629224323b8f36932d77. The production change is original173; the one-line SpanStart initialization from the later hairline commit belongs with this blend regression harness and is moved here. Original published history is untouched.

<table><tr><th>Before</th><th>After, identical pixels</th></tr><tr><td><img src="renders/group-performance-40-before.png" width="360" alt="Original MIT groups before fused blending"></td><td><img src="renders/group-performance-40-after.png" width="360" alt="Original MIT groups after fused blending with identical pixels"></td></tr></table>

Both original MIT 40-group and 400-group PDFs have zero differing pixels across full 833×1111 RGBA arrays at 100 DPI, degree 1. Raw PNGs are unedited. Exact engine/input/output hashes are in render metadata. Reuse the original generator/harness and rerun commands in ../group-bounds/. Fresh independent references are in ../group-bounds/references/; their native 834×1112 grid differs from OneImage 833×1111, so no exact cross-engine grid parity is claimed. PDF.js is custom Node Canvas, not a native browser.

## Tests

The exact review source passes 365 PDF cases with 1 known soft-mask-transfer skip, 3 targeted exhaustive blend cases and 335/335 Drawing cases. Release builds have 0 warnings/errors. The SpanStart repair is included in these checks; they are not silently substituted for the original173 test harness. OnePDF/Fonts 1.18.0 remains unchanged.

## Performance remains pending

No speedup or universal no-regression claim is made. The exact new head has not been timed in a controlled window. Its production DLL hashes differ from the original173 snapshot build, so earlier results are not relabelled as exact-head measurements.

The retained historical check used the same original MIT 40-group input, runtime 10.0.15, SDK 10.0.404, process CPU count 2, degree 1, 20 warmups and 30 samples. Other coordinated compute was paused 20:23:49.510Z–20:24:05.512Z. It ran bounds-A, original950-A, original173-A, original173-B, original950-B, bounds-B. Full raw samples and hashes are retained in historical-timing/.

Original950 fresh load/render medians 13.389/12.037ms versus original173 13.984/13.308ms do not demonstrate a fresh-load improvement. Retained medians 8.583/7.563ms versus 7.452/7.426ms suggest less work, but original950 same-binary repeat variation is substantial and these short runs are insufficient for a stable general conclusion. Every output hash agrees. This is an explicitly limited historical observation, not a pass for reconstructed-head performance.

All new assets here are original MIT material or raw output from that material. No private/upstream PDFs/fonts/art/expected-image input is used; existing dependency licenses are unchanged. Full solution/cross-platform CI, AOT/WASM and Odin WebView2 validation remain pending.
