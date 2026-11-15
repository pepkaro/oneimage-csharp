# Tiny positive dashed strokes

These original MIT controls use only numeric geometry. They contain no private documents, third-party artwork, fonts, images, or reference-engine pixels.

Generate the 13 small PDFs and their content/hash manifest:

```sh
python3 tools/tiny-dashed-strokes/generate.py --output /tmp/tiny-dashed-strokes
```

Render one input with the repository's PDF renderer (72 or 144 DPI):

```sh
dotnet build tools/PdfRender -c Release
dotnet "$ONEIMAGE_ARTIFACTS/bin/PdfRender/release/OneImage.PdfRender.dll" render /tmp/tiny-dashed-strokes/closed-on.pdf /tmp/closed-on.png 144
```

The 128×96-point pages have equal MediaBox/CropBox, no rotation and no annotations. Use an opaque white background when comparing renderers.

## Expectations

The positive horizontal displacement is 0.00000002 points at (64,48), with width 16 and dash pattern [9 13], phase 2. The ordinary float path loses that displacement. A positive closed out-and-back dash has two coincident caps facing left at its seam; their union approaches a half-disc of area π×8²/2 = 100.531 square points. The open dash approaches a full disc of area 201.062. A square-capped closed dash approaches a half-square of area 128. A butt-capped tiny line has negligible area. Reversing the positive direction reverses the half-cap.

OFF, exactly stationary, solid/normalized-solid and ordinary-length cases are separate controls. The existing solid and exact-stationary policies are intentionally unchanged. A zero-length ON dash is also distinct from a positive closed out-and-back dash.

Reference engines disagree on some extremely small closed paths, stationary paths and cap styles. Their rasters are useful diagnostic comparisons, not one universal circle oracle. The tests use analytical area/direction and equivalent paths, and label non-regression controls separately from correctness assertions.

## Scope and implementation

This repair applies to positive **dashed** stroke geometry lost by float conversion, duplicate-point tolerance, or a tiny looping cubic flattened to a stationary chord. Ordinary figures retain their float coordinates, flattener and core duplicate policy. Affected figures use origin-relative doubles until the outline exists; dash phase stays in user space, including hairlines. Hairline flattening uses the ordinary core's Frobenius transform bound. The original per-path point, dash-switch and pre-resolution outline budgets are shared across both routes.

Solid/normalized-solid paths retain the existing policy. This does not change the PDF number parser or claim exact parity with every native PDF renderer. Decimal values lost before a PdfPath reaches the renderer cannot be recovered here.

Tests are in TinyPositiveStrokeTests and PreciseStrokeTests. The test comments distinguish the separately observed sheared-hairline equivalence control from the analytical no-shear correctness test. No performance claim is made.
