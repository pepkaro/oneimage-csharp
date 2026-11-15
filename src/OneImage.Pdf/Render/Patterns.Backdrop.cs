// SPDX-License-Identifier: MIT
using OneImage.Drawing;
using OnePdf;
using DrawingPath = OneImage.Drawing.Path;

namespace OneImage.Pdf.Render;

internal sealed partial class CanvasDevice
{
    /// <summary>Evaluates all copies as one non-isolated group before applying the painted object's state (11.6.7).</summary>
    private void PaintBackdropPattern(PdfTilingPattern pattern, in PdfColor color, DrawingPath area, IntersectionRule rule,
        double alpha, in PdfGraphicsState state, DrawingPath? clip, Canvas? stencil = null)
    {
        if ((!(alpha > 0) && !InKnockoutGroup && GeometryShadow is null) || pattern.Cell is null) return;
        PdfMatrix view = pattern.Matrix.Then(_view);
        double xs = Math.Abs(pattern.XStep), ys = Math.Abs(pattern.YStep);
        if (!view.IsFinite || !Invert(view, out PdfMatrix inverse) || !(xs > 1e-9 && ys > 1e-9) || !double.IsFinite(xs + ys)) return;
        CheckNesting();

        // Never cache backdrop-dependent pixels. Rendering uses the same fixed device cell as the page,
        // so regions and concurrent requests see the same tile order and pixel geometry.
        var rect = new ImageRect(0, 0, _w, _h);
        PdfBounds shown = inverse.TransformBounds(new PdfBounds(-1.5, -1.5, _w + 1.5, _h + 1.5));
        PdfBounds bb = pattern.BBox;
        double firstX = Math.Ceiling((shown.Left - bb.Right) / xs), lastX = Math.Floor((shown.Right - bb.Left) / xs);
        double firstY = Math.Ceiling((shown.Bottom - bb.Top) / ys), lastY = Math.Floor((shown.Top - bb.Bottom) / ys);
        if (!(lastX >= firstX && lastY >= firstY)) return;
        // Subpixel periods and pathological overlaps must not turn a bounded render cell into an unbounded replay loop.
        double copies = (lastX - firstX + 1) * (lastY - firstY + 1);
        if (!(copies <= (long)(_w + 3) * (_h + 3) * Limits.MaxPatternCopies) ||
            Math.Max(Math.Max(Math.Abs(firstX), Math.Abs(lastX)), Math.Max(Math.Abs(firstY), Math.Abs(lastY))) > (1L << 52))
            throw new ImageLimitException("Too many backdrop-dependent pattern copies in one render cell.");

        Rgba32? tint = null;
        if (!pattern.IsColored)
        {
            PdfColorSpace? under = color.Space.PatternBase;
            tint = under is null ? new Rgba32(0, 0, 0, 255) : PdfColors.ToRgba(under, color.C0, color.C1, color.C2, color.C3);
        }
        using var layer = new Canvas(_w, _h, PixelFormat.Rgba8);
        using var coverage = new Canvas(_w, _h, PixelFormat.Rgba8);
        bool knockout = InKnockoutGroup;
        Canvas? backdrop = GroupBackdrop;
        using var geometry = knockout || GeometryShadow is not null ? new Canvas(_w, _h, PixelFormat.Rgba8) : null;
        if (backdrop is not null) CopyBackdrop(layer, backdrop, rect);
        for (double j = firstY; j <= lastY; j++)
        for (double i = firstX; i <= lastX; i++)
        {
            _ct.ThrowIfCancellationRequested();
            PdfMatrix copyView = PdfMatrix.Translation(i * xs, j * ys).Then(view);
            if (!Invert(copyView, out PdfMatrix inv)) continue;
            PdfBounds cull = inv.TransformBounds(new PdfBounds(-1.5, -1.5, _w + 1.5, _h + 1.5));
            using var device = new CanvasDevice(_page, copyView, layer, _depth + _frames.Count + 1, tint, _ct, coverage, geometry);
            pattern.Cell.Replay(device, cull);
        }

        Canvas? mask = null;
        if (state.SoftMaskId != 0) _masks.TryGetValue(state.SoftMaskId, out mask);
        float amount = (float)Math.Clamp(alpha, 0, 1);
        BlendMode blend = ParseBlend(state.BlendMode);
        if (knockout)
        {
            using var geometric = new CanvasLayerBrush(geometry!, null, null, rect);
            if (backdrop is not null)
            {
                using var source = new NonIsolatedGroupBrush(layer, coverage, null, rect, 1, interpolate: false);
                PaintKnockout(source, geometric, area, rule, amount, blend, mask, state.AlphaIsShape, clip, true, stencil);
            }
            else
            {
                using var source = new CanvasLayerBrush(layer, null, null, rect);
                PaintKnockout(source, geometric, area, rule, amount, blend, mask, state.AlphaIsShape, clip, true, stencil);
            }
            return;
        }
        if (geometry is not null)
        {
            using var geometric = new CanvasLayerBrush(geometry, null, null, rect);
            TrackGeometry(geometric, geometric, area, rule, amount, mask, state.AlphaIsShape, clip, true, stencil);
        }
        using Canvas? combinedMask = stencil is not null && mask is not null ? new Canvas(_w, _h, PixelFormat.Rgba8) : null;
        if (combinedMask is not null)
        {
            using var maskBrush = new CanvasLayerBrush(stencil!, null, mask, rect);
            combinedMask.Fill(maskBrush, DrawingPath.Rectangle(0, 0, _w, _h), antialias: false);
        }
        mask = combinedMask ?? stencil ?? mask;
        bool interpolate = blend == BlendMode.Normal;
        using (var brush = new NonIsolatedGroupBrush(layer, coverage, mask, rect, amount, interpolate))
        {
            _target.Fill(brush, area, true, rule, 1, blend,
                interpolate ? AlphaComposition.Src : AlphaComposition.SrcOver, false, null, clip, _clip.Rule);
        }
        if (ShapeShadow is { } shadow)
        {
            using var brush = new CanvasLayerBrush(coverage, null, mask, rect);
            shadow.Fill(brush, area, true, rule, amount, BlendMode.Normal, AlphaComposition.SrcOver, false, null, clip, _clip.Rule);
        }
    }
}
