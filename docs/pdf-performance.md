# PDF performance measurement

The goal is page-rendering performance comparable to an interactive browser or WebView without changing rendered pixels. A fast screenshot of an already cached page does not establish rasterizer parity, and a first call that includes .NET JIT work does not measure steady-state rendering.

## Reproducible transparency workload

`PdfNarrowGroupBenchmarks` generates a PDF containing 40 or 400 narrow, non-isolated transparency groups over an opaque background. It uses no external PDF, runs at 100 DPI, and tests degrees 1 and 4.

```sh
dotnet run -c Release --project bench/OneImage.Benchmarks -- --filter '*PdfNarrowGroupBenchmarks*'
```

The two methods measure different boundaries:

- `Render`: load a new document from bytes and render it into a reusable RGBA output array.
- `Rerender`: retain the loaded document, call `ReleaseDecodedPixels`, and render again. Output tiles are discarded; the PDF decoder retains its document, display list, and budgeted image resources. This rerasterizes the page instead of copying a cached output bitmap. The release call is included in the measurement.

BenchmarkDotNet warms the runtime, so neither method measures process-cold startup. A `--job Dry` run is a build/execution smoke check, not evidence for a performance comparison.

The renderer bounds transparency-group copying and compositing to outward-rounded form bounds with one pixel of rasterizer slack. It copies straight RGBA backdrops directly, normalizing zero-alpha pixels as the former Src paint did. Finished layers are sampled directly, applying shape and soft-mask alpha in the same sequential 8-bit rounding order as the general image-mask pipeline. General blend and coverage behavior remains in `Canvas.Fill`.

## Real-document measurement

Use a local PDF that you have permission to test. Keep the PDF and rendered images out of the repository. Record the commit, build configuration, runtime, CPU, thread limit, page, page box, rotation, DPI, and actual output width and height.

Measure these cases separately:

1. **Process-cold first document:** new process, first load and render. Report file reading separately and identify whether process creation is included. This includes JIT and lazy initialization, but does not imply a cold filesystem cache.
2. **Warm runtime, new document:** warm up the same operation, then create a new `Image.Load` for every sample. Time loading and rendering separately, and report their sum too.
3. **Retained document, uncached output:** reuse one loaded document but release decoded output before each render. Verify that the renderer replays cells, rather than relying only on elapsed time to infer cache behavior.
4. **First render at a new scale:** open a new document, render one smaller size, then time the first render at the target size. Do not visit the target size beforehand. This models an interactive scale change with document resources retained.
5. **Cached output copy/display:** retain output pixels and read or display them again. Label this separately from rerasterization.

A natural smaller-size prime in a fresh host is not equivalent to several full runtime warmups. Report the first target-scale render after that prime separately from a fully warmed runtime.

Use multiple warmups and measured samples, retain every sample, and report a median and range. Do not run builds or competing benchmarks simultaneously. Rebuild after source changes and verify the source and assembly used, especially when transferring files with preserved timestamps. Hash the complete RGBA output outside the timed interval and compare with the original implementation. Regression tests should also cover masks, transforms, fractional bounds, partial alpha, cell boundaries, and parallel rendering.

Evaluate ReadyToRun and tiering choices in both process-cold and post-prime or warm scenarios before changing a host default. A startup improvement can reverse after the initial page has been shown; retain the same output checks and measurement boundaries for every configuration.

## Browser and WebView comparisons

Use an actual browser PDF viewer or WebView host, not a standalone PDFium call labeled as WebView. Record browser/runtime versions, viewport, device scale factor, viewer zoom, and the page-content rectangle. Match the PDF, page, box, rotation, and pixel dimensions. A browser's 100% viewer zoom commonly maps PDF points at 96 DPI; it is not automatically a 100-DPI render.

Time from a documented action to a verified, settled page image. Navigation-completed alone is not proof that the target page is painted. Verify the page identity and geometry and compare the completed image with an independently captured reference from that renderer. Different renderers need not have byte-identical antialiasing; unchanged OneImage pixels are a separate correctness check.

Report browser/WebView initialization, navigation, polling, screenshot/capture, image encoding, and physical presentation boundaries explicitly. A captured UI frame includes work not present in an in-memory RGBA renderer, while the viewer may retain caches not exposed to the benchmark. Do not subtract guessed overhead and call the remainder pure rendering time.

For a matched viewer endpoint, present the OneImage result through the same WebView host and include output conversion, PNG encoding, bridge or IPC transfer, image decoding, presentation, and capture. Report raw RGBA rendering separately. A minimal image presentation surface still differs from a full PDF viewer, so matching the host and capture endpoint does not make their UI work identical.

For a stronger first-scale comparison, start each browser trial in a new process/profile, open directly at a smaller zoom, wait for that page to settle, then time the first transition to a never-before-visited target scale. Returning to a previously visited scale can reuse a final raster and must be labeled as potentially cached. Even the first-scale protocol retains document resources and remains a broader UI/capture measurement, not an isolated rasterizer benchmark.

Any parity conclusion must name the tested scenario and its timing boundaries. One document, one device, or a cached return to a page is not proof of general renderer parity.
