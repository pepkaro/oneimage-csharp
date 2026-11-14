# Reproduce this control

These commands operate on separately built external trees, never change production source, and write new outputs. Use the exact dependency versions in `PROVENANCE.md` for the captured comparison. Install dependencies from their official registries under their original licenses. Check out/build the before source tree `c0a5566f3aeaa219615bf8f7df149a051623d51a` and head `fc149eb1be9923afcc557575f93df5a576998eef`; the publisher's corresponding PR commits must contain those source contents before adding evidence. The build artifact directory must hold OneImage.dll, OneImage.Pdf.dll, OnePdf.dll and OnePdf.Fonts.dll. Exact captured assembly hashes are in the manifest. Rebuilt binaries may have different hashes due to build paths or metadata, so record the actual ones, do not relabel them as captured binaries.

From this unit's directory:

```sh
# Generates the original numeric PDF; for outline-knockout also the original CFF.
python tools/generate.py
sha256sum -c SHA256SUMS

# Build the same small harness independently against each external renderer build.
dotnet build tools/Evidence.csproj -c Release -p:RendererDir=/absolute/before/bin -o /absolute/evidence-before
dotnet build tools/Evidence.csproj -c Release -p:RendererDir=/absolute/after/bin -o /absolute/evidence-after
DOTNET_PROCESSOR_COUNT=2 dotnet /absolute/evidence-before/Evidence.dll render fixtures/passthrough-coverage.pdf rerun/passthrough-coverage-before 144 1 false
DOTNET_PROCESSOR_COUNT=2 dotnet /absolute/evidence-after/Evidence.dll render fixtures/passthrough-coverage.pdf rerun/passthrough-coverage-after 144 1 false

# Official PDF.js and @napi-rs/canvas are installed outside the evidence directory.
python tools/render-references.py fixtures/passthrough-coverage.pdf rerun/references /absolute/external/node_modules/pdfjs-dist
```

For image-smoothing also run the after engine with `false`, saving `rerun/image-smoothing-after-default`; it must retain the baseline pixels. This option is unavailable on the before renderer, so before uses its default only. For other controls leave smoothing false.

The harness's `render` command writes PNG, exact raw RGBA bytes and a metadata JSON including input/assembly/output hashes. PNGs are encoded directly from those raw pixels. The reference adapter records actual versions, settings, dimensions and SHA-256. Every comparison here is a full-page RGB comparison with equal native dimensions, no resizing/alignment. Mean absolute RGB error is the mean of absolute differences across all three 8-bit channels and all pixels. `pixelsAbove8` counts pixels whose largest channel difference exceeds 8. `changedPixels` counts any changed RGB channel. Bounds are inclusive zero-origin raster coordinates, not PDF coordinates.

The optional `flatInterior` metric excludes a pixel unless all three reference images have per-channel range ≤2 in its 5×5 neighborhood (SciPy min/max filter default reflect boundary). It is a descriptive subset, NOT independent ground truth and NOT proof about edges. Hairline interior scores are mostly blank paper and must not be used to claim stroke correctness. The supplied whole-page metrics are for the captured files, not any future rerun. No performance benchmark was run for these correctness controls.
