using System.Drawing;
using OneImage.Drawing;
using OnePdf;
using DrawingPath = OneImage.Drawing.Path;

namespace OneImage.Pdf.Render;

internal sealed partial class CanvasDevice
{
    /// <summary>
    /// Shows a string. Every glyph outline of the run is placed (OnePDF gives outlines in em units, <c>GlyphMatrix</c> maps them to user
    /// space) and the run is filled as one shape, so overlapping glyphs of one run never blend twice. Stroke modes stroke the outlines in
    /// user space, so the line width follows the CTM; clip modes add the glyphs to the text clip taken by the next <c>PushTextClip</c>.
    /// </summary>
    public void ShowGlyphRun(in PdfGlyphRun run, in PdfGraphicsState state)
    {
        // The run of a Type 3 font carries no outlines (its glyph procedures follow); any other run ends an open text knockout layer.
        foreach (PdfGlyph g in run.Glyphs.Span)
        {
            if (!g.Outline.IsEmpty)
            {
                CloseTextKnockout();
                break;
            }
        }

        PdfTextRenderMode mode = run.RenderMode;
        if (mode == PdfTextRenderMode.Invisible)
        {
            return;
        }

        bool fill = mode is PdfTextRenderMode.Fill or PdfTextRenderMode.FillStroke or PdfTextRenderMode.FillClip or PdfTextRenderMode.FillStrokeClip;
        bool stroke = mode is PdfTextRenderMode.Stroke or PdfTextRenderMode.FillStroke or PdfTextRenderMode.StrokeClip or PdfTextRenderMode.FillStrokeClip;
        bool clip = (int)mode >= 4;
        if (Skip && !clip)
        {
            return;
        }

        _ct.ThrowIfCancellationRequested();
        PdfMatrix total = state.Ctm.Then(_view);
        ReadOnlySpan<PdfGlyph> glyphs = run.Glyphs.Span;
        var devicePath = new PathBuilder();
        PathBuilder? userPath = stroke ? new PathBuilder() : null;
        bool any = false;
        for (int i = 0; i < glyphs.Length; i++)
        {
            PdfPath outline = glyphs[i].Outline;
            if (outline.IsEmpty)
            {
                continue;
            }

            PdfMatrix glyphToUser = run.GlyphMatrix(i);
            if (!glyphToUser.IsFinite)
            {
                continue;
            }

            if (PathConvert.Append(devicePath, outline, glyphToUser.Then(total), clamp: true))
            {
                any = true;
            }

            if (userPath is not null)
            {
                PathConvert.Append(userPath, outline, glyphToUser, clamp: false);
            }
        }

        if (!any)
        {
            if (clip)
            {
                _textClip ??= new PathBuilder();
            }

            return;
        }

        DrawingPath dev = devicePath.Build();
        DrawingPath? strokeOutline = null;
        if (stroke && !Skip && userPath is not null)
        {
            DrawingPath user = userPath.Build();
            double scale = PathConvert.MeanScale(total);
            if (!user.IsEmpty && scale > 1e-9 && double.IsFinite(scale))
            {
                strokeOutline = StrokeUserPath(user, state, total, scale);
            }
        }

        if (fill && !Skip && !dev.IsEmpty)
        {
            DrawingPath visible = dev;
            // 11.7.4.4: a combined fill/stroke glyph is one knockout object, irrespective of /TK.
            // Alpha-as-shape and overprint require different knockout semantics; leave their existing handling unchanged.
            // Merged overlapping glyphs need per-glyph ordering; preserve that existing limitation rather than erasing another
            // glyph's fill with a run-wide stroke. The guard includes raster slack and rejects uncertain separation in linear time.
            if (strokeOutline is not null && state.StrokeAlpha is > 0 and < 1 && !state.AlphaIsShape && !state.FillOverprint && !state.StrokeOverprint)
            {
                try
                {
                    if (GlyphsArePixelDisjoint(run, state, total))
                    {
                        visible = dev.Subtract(strokeOutline, IntersectionRule.NonZero, IntersectionRule.NonZero);
                    }
                }
                catch (ImageLimitException)
                {
                    // Boolean operations have tighter coordinate/complexity limits than raster painting. Preserve the legacy
                    // path when this optional correction cannot be computed; no pixels have been painted yet.
                }
            }

            if (!visible.IsEmpty)
            {
                Paint(visible, IntersectionRule.NonZero, state.FillColor, state.FillAlpha, state);
            }
        }

        if (strokeOutline is not null)
        {
            Paint(strokeOutline, IntersectionRule.NonZero, state.StrokeColor, state.StrokeAlpha, state);
        }

        if (clip)
        {
            _textClip ??= new PathBuilder();
            _textClip.AddPath(dev);
        }
    }

    /// <summary>Conservatively proves that no two glyphs can affect the same raster pixel, including their strokes.</summary>
    private static bool GlyphsArePixelDisjoint(in PdfGlyphRun run, in PdfGraphicsState state, in PdfMatrix total)
    {
        ReadOnlySpan<PdfGlyph> glyphs = run.Glyphs.Span;
        int count = 0;
        int first = -1;
        for (int i = 0; i < glyphs.Length; i++)
        {
            if (glyphs[i].Outline.IsEmpty) continue;
            first = first < 0 ? i : first;
            if (++count > 1) break;
        }

        if (first < 0) return false;
        // Keep uncertain multi-glyph dash/fallback interactions on the legacy path.
        if (count > 1 && !state.Dash.IsEmpty) return false;

        // Remove both cell translation and the common text origin before converting to floats. Every cell must choose
        // the same compositing policy, including when the bounds sit exactly at the conservative separation threshold.
        PdfMatrix origin = run.GlyphMatrix(first);
        if (!origin.IsFinite) return false;
        var linear = new PdfMatrix(total.A, total.B, total.C, total.D, 0, 0);
        double scale = PathConvert.MeanScale(linear);
        double linearSize = Math.Max(Math.Abs(linear.A) + Math.Abs(linear.C), Math.Abs(linear.B) + Math.Abs(linear.D));
        double reachX = 0, reachY = 0;
        if (count > 1)
        {
            // A normalized re-stroke is not a safe bound: rounding the original user vertices can change a bevel into a
            // long miter. Instead bound every possible cap/join around the control-point hull. Square caps reach sqrt(2)
            // half-widths; miters reach at most the miter limit. Hairlines construct these in device space.
            double miter = double.IsFinite(state.MiterLimit) && state.MiterLimit >= 1 ? state.MiterLimit : 10;
            double joinReach = state.LineJoin is 1 or 2 ? Math.Sqrt(2) : Math.Max(Math.Sqrt(2), miter);
            double radius = state.LineWidth == 0 ? 0.5 : Math.Max(state.LineWidth, 1 / scale) / 2;
            reachX = radius * joinReach * (state.LineWidth == 0 ? 1 : Math.Sqrt((linear.A * linear.A) + (linear.C * linear.C)));
            reachY = radius * joinReach * (state.LineWidth == 0 ? 1 : Math.Sqrt((linear.B * linear.B) + (linear.D * linear.D)));
            if (!double.IsFinite(reachX + reachY)) return false;
        }

        RectangleF? aggregate = null;
        for (int i = first; i < glyphs.Length; i++)
        {
            if (glyphs[i].Outline.IsEmpty) continue;
            PdfMatrix m = run.GlyphMatrix(i);
            if (!m.IsFinite) return false;
            double left = double.PositiveInfinity, top = double.PositiveInfinity;
            double right = double.NegativeInfinity, bottom = double.NegativeInfinity;
            ReadOnlySpan<double> points = glyphs[i].Outline.Points.Span;
            for (int p = 0; p + 1 < points.Length; p += 2)
            {
                double x = (m.A * points[p]) + (m.C * points[p + 1]);
                double y = (m.B * points[p]) + (m.D * points[p + 1]);
                // Actual stroking first converts unshifted user coordinates to floats. Reject precision-unsafe runs even
                // when a compensating CTM translation brings them on-page. This budget is independent of the render cell.
                if (!(Math.Max(Math.Abs(x + m.E), Math.Abs(y + m.F)) * linearSize < (1 << 20))) return false;
                x += m.E - origin.E;
                y += m.F - origin.F;
                double dx = (linear.A * x) + (linear.C * y), dy = (linear.B * x) + (linear.D * y);
                left = Math.Min(left, dx);
                right = Math.Max(right, dx);
                top = Math.Min(top, dy);
                bottom = Math.Max(bottom, dy);
            }

            if (!(Math.Max(Math.Max(Math.Abs(left), Math.Abs(right)) + reachX,
                Math.Max(Math.Abs(top), Math.Abs(bottom)) + reachY) < (1 << 20))) return false;
            // A single glyph needs no inter-glyph separation proof, only the conservative coordinate/precision checks.
            if (count == 1) return true;
            var bounds = RectangleF.FromLTRB((float)(left - reachX), (float)(top - reachY), (float)(right + reachX), (float)(bottom + reachY));
            // Include curve/float tolerance and a full pixel of antialiased coverage before proving separation.
            bounds.Inflate(1 + DrawingPath.DefaultTolerance, 1 + DrawingPath.DefaultTolerance);
            if (aggregate is { } prior)
            {
                if (prior.IntersectsWith(bounds)) return false;
                aggregate = RectangleF.Union(prior, bounds);
            }
            else
            {
                aggregate = bounds;
            }
        }

        return true;
    }
}
