> Lossless transport packaging (2026-11-15): the four raw RGBA buffers are stored as deterministic `.rgba.gz` files. The readable PNGs, PDF, numerical source, timing results, and original `manifest.json` are unchanged. See [PACKAGING.md](PACKAGING.md) to reconstruct and hash-check the complete original package before running its checks. The frozen manifest and original `SHA256SUMS` describe that reconstructed package, not the transport-facing README/reproduction additions.

# Reproduce the numeric reduction control

Preserve this captured package. Work in a new copy so generation, rendering, and timing do not overwrite the original evidence. Build the exact before source contents (tree `e26ce6d8dd234a608c4bcf2d1a2f6f46d1f16b45`) and head contents (tree `a3895db911a64996ce997e6274703a4b6a15d737`) separately. These are source tree identifiers, not claims that a later evidence-bearing PR commit has the same entire tree. The publication commits must retain these source contents. Build with the repository's instructions and dependencies; do not patch production code for this harness.

The external build directories must contain OneImage.dll, OneImage.Pdf.dll, OnePdf.dll and OnePdf.Fonts.dll. Captured assembly hashes are in the manifest. Rebuilt binaries can differ due to paths/build metadata; record the actual hashes rather than relabeling them as the captured ones. Install dependency versions listed in PROVENANCE.md from official sources, separately and under their own licenses.

From the new package copy:

```sh
python tools/generate.py
sha256sum -c SHA256SUMS

# Use distinct intermediate/output paths to prevent stale-reference reuse.
dotnet build tools/Evidence.csproj -c Release -t:Rebuild -p:RendererDir=/absolute/before/bin -p:BaseIntermediateOutputPath=/absolute/work/obj-before/ -o /absolute/work/evidence-before
dotnet build tools/Evidence.csproj -c Release -t:Rebuild -p:RendererDir=/absolute/after/bin -p:BaseIntermediateOutputPath=/absolute/work/obj-after/ -o /absolute/work/evidence-after

DOTNET_PROCESSOR_COUNT=2 dotnet /absolute/work/evidence-before/Evidence.dll render fixtures renders/reduction-weights-before 144
DOTNET_PROCESSOR_COUNT=2 dotnet /absolute/work/evidence-after/Evidence.dll render fixtures renders/reduction-weights-after 144
python tools/render-references.py fixtures/reduction-weights.pdf references /absolute/external/node_modules/pdfjs-dist
OPENBLAS_NUM_THREADS=1 python tools/check.py
```

`render` writes a full-page PNG and raw RGBA, a separate 320×192 raw RGBA result from the production Area method, and metadata. Page raw buffers are 384×256×4 bytes, row-major RGBA, top-left origin. The full page image rectangle is x=[32,352), y=[32,224). The raw numerical source contains RGB only, also row-major/top-left. The PNGs are encoded directly from raw pixels. References are native-size full pages, with labels external. All analytical/reference comparisons here use those same dimensions; never silently rescale a different-sized future render.

## Optional controlled timing

Only measure on an otherwise quiet machine. The capture intentionally used `DOTNET_PROCESSOR_COUNT=2`, `DOTNET_TieredCompilation=0`, `DOTNET_TieredPGO=0`, degree 1, and .NET 10.0.15. These are experimental settings, not user defaults. The whole six-process run was capped at 120 seconds. For each process call:

```sh
export DOTNET_PROCESSOR_COUNT=2 DOTNET_TieredCompilation=0 DOTNET_TieredPGO=0
# Repeat in order before,after,after,before,before,after, n=1…6.
dotnet /absolute/work/evidence-SIDE/Evidence.dll measure fixtures measurements/run-N-SIDE 144 10 25 1
python tools/summarize-timing.py
```

Record UTC start/end timestamps for each process in `measurements/run-N-SIDE.start-utc.txt` and `.end-utc.txt`, and overall `window-start-utc.txt`, `window-end-utc.txt`, and `window-exit-status.txt`. Redirect each invocation's stdout/stderr to its own log. The captured files illustrate the exact naming. The summary requires exactly six JSON files and verifies all 420 recorded output hashes and settings. Do not retain old run JSONs alongside new ones or combine samples from different conditions.

The two boundaries are production Area-only and fresh PDF load/render. Each starts with ten retained warmups then 25 measured operations, no trimming. Every operation is hash checked outside its stopwatch. One initial verification call per boundary, source/delegate setup, file IO and hash work are outside timing. Current-thread allocation is recorded per operation and includes harness overhead; it is not total allocation or peak memory. The extra weight pool's cold allocation is not a steady-state measurement. Do not use retained-page renders as a substitute: their cached decoded/reduced image skips the targeted work. Always report the overlapping fresh-PDF medians and avoid claiming that an Area-only result proves an end-to-end gain.
