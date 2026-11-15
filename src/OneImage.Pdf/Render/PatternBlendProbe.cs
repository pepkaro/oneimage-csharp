// SPDX-License-Identifier: MIT
using OnePdf;

namespace OneImage.Pdf.Render;

/// <summary>Conservatively identifies cells for which the Normal-only isolated-tile optimization is not valid.</summary>
internal sealed class PatternBlendProbe(CancellationToken ct) : PdfDevice
{
    private readonly HashSet<PdfTilingPattern> _seen = [];
    private readonly Queue<PdfTilingPattern> _pending = [];
    private bool _needsBackdrop;

    public static bool NeedsBackdrop(PdfTilingPattern pattern, CancellationToken ct = default)
    {
        ct.ThrowIfCancellationRequested();
        var probe = new PatternBlendProbe(ct);
        probe.Add(pattern);
        while (!probe._needsBackdrop && probe._pending.TryDequeue(out PdfTilingPattern? next))
        {
            ct.ThrowIfCancellationRequested();
            // An unavailable cell is not proof of Normal-only painting. A conservative true result
            // remains safe even if an incomplete/recursive cell is populated before a later use.
            if (next.Cell is null) probe._needsBackdrop = true;
            else next.Cell.Replay(probe);
        }
        return probe._needsBackdrop;
    }

    private void Add(PdfTilingPattern pattern)
    {
        if (_seen.Add(pattern)) _pending.Enqueue(pattern);
    }

    private void Check(in PdfGraphicsState state, bool fill = false, bool stroke = false)
    {
        ct.ThrowIfCancellationRequested();
        _needsBackdrop |= CanvasDevice.ParseBlend(state.BlendMode) != BlendMode.Normal;
        if (fill && state.FillColor.Pattern is PdfTilingPattern f) Add(f);
        if (stroke && state.StrokeColor.Pattern is PdfTilingPattern s) Add(s);
    }

    public override void BeginPage(in PdfPageInfo page) => ct.ThrowIfCancellationRequested();
    public override void EndPage() => ct.ThrowIfCancellationRequested();
    public override void PushClip(in PdfPath path, bool evenOdd, in PdfGraphicsState state) => ct.ThrowIfCancellationRequested();
    public override void PushTextClip(in PdfGraphicsState state) => ct.ThrowIfCancellationRequested();
    public override void PopClip() => ct.ThrowIfCancellationRequested();
    public override void EndType3Glyph() => ct.ThrowIfCancellationRequested();
    public override void EndGroup() => ct.ThrowIfCancellationRequested();
    public override void BeginSoftMask(in PdfSoftMaskInfo mask, in PdfGraphicsState state) => ct.ThrowIfCancellationRequested();
    public override void EndSoftMask() => ct.ThrowIfCancellationRequested();
    public override void BeginMarkedContent(string tag, PdfDictionary? properties) => ct.ThrowIfCancellationRequested();
    public override void EndMarkedContent() => ct.ThrowIfCancellationRequested();
    public override void BeginAnnotation(in PdfAnnotationInfo annotation) => ct.ThrowIfCancellationRequested();
    public override void EndAnnotation() => ct.ThrowIfCancellationRequested();

    public override void FillPath(in PdfPath path, bool evenOdd, in PdfGraphicsState state) => Check(state, fill: true);
    public override void StrokePath(in PdfPath path, in PdfGraphicsState state) => Check(state, stroke: true);
    public override void FillStrokePath(in PdfPath path, bool evenOdd, in PdfGraphicsState state) => Check(state, fill: true, stroke: true);
    public override void ShowGlyphRun(in PdfGlyphRun run, in PdfGraphicsState state) => Check(state, fill: true, stroke: true);
    public override void DrawImage(in PdfImage image, in PdfGraphicsState state) => Check(state, fill: true);
    public override void PaintShading(PdfShading shading, in PdfGraphicsState state) => Check(state);
    public override void BeginGroup(in PdfGroupInfo group, in PdfGraphicsState state) => Check(state);
    public override void BeginType3Glyph(in PdfType3GlyphInfo glyph, in PdfGraphicsState state) => Check(state, fill: true, stroke: true);
}
