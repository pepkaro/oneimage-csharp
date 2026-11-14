# Reproduce the evidence

Use a clone of `https://github.com/pepkaro/oneimage-csharp` containing the two exact commits below, and .NET SDK 10.0.404/runtime 10.0.15. The source's `global.json` remains unchanged. All these implementation commits pin `RecursiveAI.OnePdf` and `RecursiveAI.OnePdf.Fonts` 1.18.0; exact manifests additionally record the loaded assembly hashes. No newer parser is silently substituted.

Choose an empty scratch directory `$WORK`, and copy this evidence directory to `$WORK/evidence`. From the evidence directory:

```sh
python3 generate.py
bash build-snapshot.sh "$REPO" eb47d5a0155bdb38f6fc7b08a5fa7279fd004a12 "$WORK"
bash build-snapshot.sh "$REPO" c705783366878618d17e3d60f7d64c838d20f42f "$WORK"
dotnet build harness/Evidence.csproj -c Release -p:RendererDir="$WORK/artifacts/c705783/bin/OneImage.Pdf.Tests/release"
```

For each source revision, copy the harness output into its own process directory, then overwrite only the four named renderer dependency assemblies from that revision's test output. Do not mix renderer revisions in a process.

```sh
for rev in eb47d5a c705783; do
  mkdir -p "$WORK/engines/$rev"
  cp harness/bin/Release/net10.0/* "$WORK/engines/$rev/"
  for dll in OneImage OneImage.Pdf OnePdf OnePdf.Fonts; do
    cp "$WORK/artifacts/$rev/bin/OneImage.Pdf.Tests/release/$dll.dll" "$WORK/engines/$rev/"
  done
done
dotnet "$WORK/engines/eb47d5a/Evidence.dll" render fixtures/group-performance-40.pdf renders/01/group-performance-40-before 100 1 false
dotnet "$WORK/engines/c705783/Evidence.dll" render fixtures/group-performance-40.pdf renders/01/group-performance-40-after 100 1 false
```

Each render writes an untouched PNG, its raw RGBA bytes, and metadata including input and output SHA-256, dimensions, runtime, options and assembly hashes. Raw `.rgba` files are reproducible scratch outputs and need not be committed. Compare their complete hashes or bytes, not only a screenshot.

Repeat the two render commands with `group-performance-400.pdf` to reproduce the larger invariant-pixel check. It uses the same 100 DPI and degree 1. No smoothing option is enabled.

## Performance boundaries

Do not compare timings while builds, other renders, or competing workloads are active. The evidence harness can measure the same PDF and verify its pixel hash after every timed sample:

```sh
dotnet "$WORK/engines/eb47d5a/Evidence.dll" measure fixtures/group-performance-40.pdf measurements/before-a 100 1 false 20 30
dotnet "$WORK/engines/c705783/Evidence.dll" measure fixtures/group-performance-40.pdf measurements/after-a 100 1 false 20 30
dotnet "$WORK/engines/c705783/Evidence.dll" measure fixtures/group-performance-40.pdf measurements/after-b 100 1 false 20 30
dotnet "$WORK/engines/eb47d5a/Evidence.dll" measure fixtures/group-performance-40.pdf measurements/before-b 100 1 false 20 30
```

This ABBA order includes two same-binary repeat controls. Every process first renders one image, then performs 20 unreported warmups and 30 recorded samples per boundary. `load+render` creates a fresh document from already resident PDF bytes. `retained-uncached-raster` includes `ReleaseDecodedPixels()` and the subsequent raster copy. Hashing, file I/O, PNG encoding and fixture generation are outside the timed interval. The first output allocation and process/JIT startup are not claimed as cold-start results. No result is a full browser or WebView endpoint comparison. Preserve the per-sample arrays and disclose repeat-control instability rather than asserting a broad speedup.
