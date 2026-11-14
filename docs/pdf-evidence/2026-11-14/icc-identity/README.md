# Fix: ICC profile descriptions must not change colors

The two input PDFs have identical RGB samples and ICC color-transform data. Only 32 bytes inside the profile's human-readable description differ. The second description contains “sRGB”; its actual profile remains wide-gamut RGB.

Before this fix, `PdfColors.Icc` treated any three-channel profile whose description contained “sRGB” as an identity transform. That skipped the real color conversion. The fix recognizes identity only from conservative, exact transform data. Linear, wide-gamut and table-based profiles retain their conversions regardless of their names.

## Actual renderer output

All images below are **unaltered full-page renderer PNGs**, 480 × 120 pixels at 96 DPI. No crops, retouching, smoothing or generated substitute images. The upper half contains vector fills; the lower half contains the same samples in an image XObject.

<table>
<tr><th>Input profile</th><th>Before: e43ee264</th><th>After: ICC identity correction</th></tr>
<tr><td>Original wide-gamut description</td><td><img src="renders/wide-original-baseline.png" width="480" height="120" alt="Original profile rendered before the fix"></td><td><img src="renders/wide-original-candidate.png" width="480" height="120" alt="Original profile rendered after the fix, unchanged"></td></tr>
<tr><td>Same profile, description contains “sRGB”</td><td><img src="renders/wide-renamed-baseline.png" width="480" height="120" alt="Renaming the profile incorrectly changes colors before the fix"></td><td><img src="renders/wide-renamed-candidate.png" width="480" height="120" alt="Renaming the profile leaves colors identical after the fix"></td></tr>
</table>

Before: renaming changes **39,600 of 57,600 pixels**, by as much as **80 channel levels**. After: **zero pixels change**. The original-name output is also unchanged by the patch.

Independent PDFium 153.0.7999.0 (pypdfium2 wrapper 5.13.0) and MuPDF 1.26.11 (PyMuPDF wrapper 1.26.6) controls likewise produce zero changed pixels when the description is renamed. Their full raw outputs are included in `renders/`. This confirms the metadata-invariance property; it does not claim every OneImage color matches every other renderer.

## Reproduction and provenance

- `generate.py` creates all shapes/sample bytes and changes only description-tag bytes. The profiles are independently generated from standard RGB primaries, gamma and Bradford/D50 math, including newly authored MIT copyright/description tags. No library ICC byte export is used. No user document pixels or other private source data is included.
- PDFs declare version 2.0 because the generated profiles are ICC 4.3.
- `manifest.json` records source, profile, PDF and output SHA256 values, exact dimensions/options, engine versions, binary hashes, the baseline commit and both historical/final patch hashes.
- `render.py` runs the two OneImage builds in separate processes and the independent native controls, preserving raw PNGs and measuring differences. Labels appear only in this document and the HTML report.
- OneImage baseline: `pepkaro/oneimage-csharp` commit `e43ee264954a177ff01a16584625a3dea79244fa`; OnePDF dependency remains pinned at 1.18.0. Candidate: commit `454e154d7cc0a2f2dd99a0f40f3ec52294bab681`, that source plus the final five-file MIT-noticed patch whose SHA256 is `999b75c5a5c9aa32c0b382ad6ff47c2f171ab2cae7b122ae822ea649dcbac39d`. Its implementation logic is identical to the recovered historical patch `25dd4ec1985b239462128d854c0f9ab616765ab16d178308097057ba1dede996`; only SPDX MIT notices were added to the two newly authored test files.
- Both OneImage builds use SDK 10.0.404/runtime 10.0.15. The repository SDK pin was not changed.

The small renderer harness's `render INPUT.pdf OUTPUT.png` mode renders one full page at 96 DPI. Build it against the intended baseline or candidate OneImage assemblies, run `python generate.py` to create the original MIT profiles/PDFs, then render `fixtures/wide-original.pdf` and `fixtures/wide-renamed.pdf` using each build. The `render.py` script records the exact commands used for this reproduction.

## Reference limitations

Fresh Mozilla PDF.js 6.5.438 (build 0a4153349) references are now included under `pdfjs-node-icc/`, using Node 24.22.1, @napi-rs/canvas 1.1.1 and an original MIT read-only local WASM host adapter. This is **custom Node Canvas diagnostic execution, not native browser Canvas**. The adapter leaves PDF.js engine source unchanged and only supplies bytes from the pinned qcms WASM file. Both runs loaded its 96,589 bytes without diagnostics. The reference images remain raw full-page outputs at 96 DPI.

The description-only pair is byte-identical. Actual conversion is separately checked: the ICC-enabled output changes 39,600 pixels, by up to 80 levels, relative to the earlier ICC-disabled DeviceRGB fallback. The earlier adapter had set `useWorkerFetch=false`, disabling ICC/WASM; its fallback outputs remain excluded from this evidence. PDF.js versus fixed OneImage differs in 16,200 pixels by at most 2 RGB levels (full-image mean absolute channel difference 0.21875), so this is not exact cross-engine pixel parity. Native browser and Odin WebView2 validation remain pending.

<table><tr><th>PDF.js ICC-enabled Node diagnostic: original description</th><th>Same profile renamed: identical</th></tr><tr><td><img src="pdfjs-node-icc/wide-original.png" width="480" height="120" alt="ICC-enabled PDF.js Node output with original description"></td><td><img src="pdfjs-node-icc/wide-renamed.png" width="480" height="120" alt="ICC-enabled PDF.js Node output with renamed description, identical"></td></tr></table>

The adapter, exact options, runtime/package/WASM hashes and reproduction commands are included in that subdirectory. Runtime modules, fonts, CMaps and WASM payloads remain external under their own licenses.

## Checks and limits

- Full PDF suite: 644/644 passed; targeted color suite: 268/268 passed.
- The nine new PDF regression cases pass with the fix and fail six cases against the baseline.
- Only the ICC identity shortcut is changed. DefaultCMYK handling and rendering-intent selection are separate issues.
- This visual demonstrates a verified correctness defect and its fix. It makes no performance-parity claim.

### Minimal independent rerun

The included `Repro/` project is a small render executable. Use two source checkouts: the baseline commit above, and that commit plus the identity patch. With .NET 10 installed, set `BASELINE_SOURCE`, `CANDIDATE_SOURCE` and an empty scratch `WORK` directory, then run:

```sh
dotnet build "$BASELINE_SOURCE/tools/PdfRender/PdfRender.csproj" -c Release -p:ArtifactsPath="$WORK/baseline"
dotnet build "$CANDIDATE_SOURCE/tools/PdfRender/PdfRender.csproj" -c Release -p:ArtifactsPath="$WORK/candidate"
dotnet build Repro/Repro.csproj -c Release -o "$WORK/repro-baseline" -p:OneImageDllDir="$WORK/baseline/bin/PdfRender/release"
dotnet build Repro/Repro.csproj -c Release -o "$WORK/repro-candidate" -p:OneImageDllDir="$WORK/candidate/bin/PdfRender/release"
python generate.py
for profile in wide-original wide-renamed; do
  dotnet "$WORK/repro-baseline/Repro.dll" render "fixtures/$profile.pdf" "renders/$profile-baseline.png"
  dotnet "$WORK/repro-candidate/Repro.dll" render "fixtures/$profile.pdf" "renders/$profile-candidate.png"
done
```

Keep both executables' output directories separate: each process must load only one engine version. `generate.py` requires only the Python standard library. The optional native-control/measurement script `render.py` additionally uses Pillow, NumPy, PyMuPDF and pypdfium2, and expects the local `engines/baseline` and `engines/candidate` layout documented by its source.

## Asset license and audit

All new fixture/profile inputs, generator/reproduction source and images in this evidence bundle are MIT licensed; see `LICENSE` and `asset-license-manifest.json`. The input chain is independently authored mathematical RGB data and PDF shapes. No upstream fixture, copied/adapted upstream test source, font, art, text, content stream or expected-image input is used. Reference PNGs were rendered only from these original MIT inputs. Existing renderer libraries and dependencies retain their own licenses.
