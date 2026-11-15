// SPDX-License-Identifier: MIT
// Copyright (c) 2026 OneImage contributors
using System.Numerics;
using OneImage.Drawing;
using OnePdf;
using DrawingPath = OneImage.Drawing.Path;

namespace OneImage.Pdf.Render;

internal sealed partial class CanvasDevice
{
    // Most PDF paths retain the original float conversion and stroke construction. Only a positive displacement
    // lost by that conversion, or by the stroker's duplicate tolerance, needs the origin-relative double route.
    private static bool NeedsPreciseStroke(in PdfPath path, double tolerance, CancellationToken ct)
    {
        ReadOnlySpan<double> points = path.Points.Span;
        ReadOnlySpan<byte> verbs = path.VerbBytes.Span;
        double x = 0, y = 0, sx = 0, sy = 0;
        bool found = false, open = false;
        int p = 0;
        foreach (byte value in verbs)
        {
            ct.ThrowIfCancellationRequested();
            var verb = (PdfPathVerb)value;
            int count = verb == PdfPathVerb.Curve ? 6 : verb is PdfPathVerb.Move or PdfPathVerb.Line ? 2 : 0;
            if (p + count > points.Length || (!open && verb is PdfPathVerb.Line or PdfPathVerb.Curve)) { return false; }
            if (verb == PdfPathVerb.Line)
            {
                // Most strokes are polylines. Avoid the cubic control-polygon bookkeeping for one endpoint,
                // while retaining the same finite guard, exact movement predicate and duplicate threshold.
                double nx = points[p], ny = points[p + 1];
                if (!float.IsFinite((float)nx + (float)ny)) { return false; }
                if (nx != x || ny != y)
                {
                    found |= ((float)nx == (float)x && (float)ny == (float)y)
                        || (Math.Abs(nx - x) <= 1e-9 && Math.Abs(ny - y) <= 1e-9);
                }

                x = nx; y = ny; p += 2;
                continue;
            }

            bool moved = false, sameFloat = true, belowDuplicateTolerance = true;
            for (int k = 0; k < count; k += 2)
            {
                double nx = points[p + k], ny = points[p + k + 1];
                if (!float.IsFinite((float)nx + (float)ny)) { return false; }
                moved |= nx != x || ny != y;
                sameFloat &= (float)nx == (float)x && (float)ny == (float)y;
                belowDuplicateTolerance &= Math.Abs(nx - x) <= 1e-9 && Math.Abs(ny - y) <= 1e-9;
            }

            // A repeated or almost repeated control point on an otherwise ordinary cubic is not a collapsed
            // curve. Restrict this route to positive line movement or an entire collapsed control polygon.
            if (open && verb != PdfPathVerb.Move) { found |= moved && (sameFloat || belowDuplicateTolerance); }
            if (verb == PdfPathVerb.Curve && moved && (float)points[p + 4] == (float)x && (float)points[p + 5] == (float)y)
            {
                double ax = (float)points[p], ay = (float)points[p + 1];
                double bx = (float)points[p + 2], by = (float)points[p + 3];
                double ex = (float)points[p + 4], ey = (float)points[p + 5];
                double curvature = Math.Max(StrokeBuilder.PreciseLength((float)x - (2 * ax) + bx, (float)y - (2 * ay) + by),
                    StrokeBuilder.PreciseLength(ax - (2 * bx) + ex, ay - (2 * by) + ey));
                found |= .75 * curvature <= tolerance;
            }
            if (count > 0) { x = points[p + count - 2]; y = points[p + count - 1]; }
            if (verb == PdfPathVerb.Move) { sx = x; sy = y; open = true; }
            if (verb == PdfPathVerb.Close) { x = sx; y = sy; }
            p += count;
        }

        return found;
    }

    private static DrawingPath? StrokePrecise(in PdfPath path, in PdfGraphicsState state, in PdfMatrix m, double scale,
        DrawingPath user, CancellationToken ct) => StrokePrecise(path, state, m, scale, user, ct, out _);

    private static DrawingPath? StrokePrecise(in PdfPath path, in PdfGraphicsState state, in PdfMatrix m, double scale,
        DrawingPath user, CancellationToken ct, out float[] dash)
    {
        dash = [];
        bool hairline = state.LineWidth == 0;
        double width = Math.Max(state.LineWidth, 1.0 / scale);
        if (!double.IsFinite(width) || width * scale > 1e7) { return null; }
        dash = Dashes(state, user, scale);
        // This repair is for positive dashed strokes. Preserve solid and normalized-solid construction exactly,
        // including the established collapsed closed round-cap behavior.
        if (dash.Length == 0) { return StrokeUserPath(user, state, m, scale); }
        DashSplitter? splitter = dash.Length == 0 ? null : new(dash, state.DashPhase, joinClosed: false);
        StrokeJoin join = state.LineJoin switch { 1 => StrokeJoin.Round, 2 => StrokeJoin.Bevel, _ => StrokeJoin.Miter };
        StrokeCap cap = state.LineCap switch { 1 => StrokeCap.Round, 2 => StrokeCap.Square, _ => StrokeCap.Butt };
        double miter = double.IsFinite(state.MiterLimit) && state.MiterLimit >= 1 ? state.MiterLimit : 10;
        double tolerance = DrawingPath.DefaultTolerance / scale;
        double flatTolerance = StrokeFlatTolerance(state, m, scale);
        if (!(flatTolerance > 0))
        {
            throw new ImageOperationException("The transform moves a path coordinate out of the finite range.");
        }
        var result = new PathBuilder();
        var ordinary = new PathBuilder();
        int pointCount = 0;
        var budget = new StrokeBuilder.Budget();

        foreach (PdfPath figure in StrokeFigures(path, ct))
        {
            ct.ThrowIfCancellationRequested();
            bool closed = figure.VerbBytes.Span[^1] == (byte)PdfPathVerb.Close;
            // Preserve the established solid closed-path policy, including its collapsed round-cap dot. Only
            // genuinely dashed closed figures have separately capped seams that require retained direction.
            if (!NeedsPreciseStroke(figure, flatTolerance, ct) || (closed && splitter is null))
            {
                if (cap != StrokeCap.Round || !StationaryFigure(figure))
                {
                    PathConvert.Append(ordinary, figure, PdfMatrix.Identity, clamp: false);
                }

                continue;
            }

            double[] xy = FlattenPrecise(figure, flatTolerance, ref pointCount, ct);
            double sx = figure.Points.Span[0], sy = figure.Points.Span[1];
            // Keep translation out of both centerline arithmetic and the dash metric. Hairlines are dashed in
            // user space, outlined in linear device space, then translated only after their caps exist.
            var linear = new Matrix3x2((float)m.A, (float)m.B, (float)m.C, (float)m.D, 0, 0);
            DrawingPath outline = StrokeBuilder.BuildPrecise(xy, closed, hairline ? 1 : width, join, cap,
                miter, splitter, hairline ? DrawingPath.DefaultTolerance : tolerance, hairline ? linear : null, budget);
            double tx = (sx * m.A) + (sy * m.C) + m.E;
            double ty = (sx * m.B) + (sy * m.D) + m.F;
            Matrix3x2 transform = hairline ? Matrix3x2.CreateTranslation((float)tx, (float)ty)
                : new Matrix3x2(linear.M11, linear.M12, linear.M21, linear.M22, (float)tx, (float)ty);
            result.AddPath(outline.Transform(transform));
        }

        DrawingPath normal = ordinary.Build();
        if (!normal.IsEmpty)
        {
            // All ordinary figures remain together, with their original float coordinates, curve tolerance and
            // core duplicate policy. Reuse the splitter so the dash-switch budget covers the entire PDF stroke.
            DrawingPath outline = StrokeBuilder.Build(normal, hairline ? 1 : width, join, cap, miter,
                hairline ? DrawingPath.DefaultTolerance : tolerance, hairline ? PathConvert.ToMatrix(m) : null,
                splitter, DrawingPath.MaxFlattenedPoints - pointCount, budget);
            result.AddPath(hairline ? outline : outline.Transform(PathConvert.ToMatrix(m)));
        }

        DrawingPath built = result.Build();
        return built.IsEmpty ? null : built;
    }

    private static double StrokeFlatTolerance(in PdfGraphicsState state, in PdfMatrix m, double scale)
    {
        if (state.LineWidth != 0) { return DrawingPath.DefaultTolerance / scale; }
        // Match the ordinary core's Frobenius bound: mean scale is not a directional error bound under
        // anisotropy or shear, even when the ordinary curve merely shares a figure with one tiny segment.
        Matrix3x2 map = PathConvert.ToMatrix(m);
        double norm = Math.Sqrt(((double)map.M11 * map.M11) + ((double)map.M12 * map.M12)
            + ((double)map.M21 * map.M21) + ((double)map.M22 * map.M22));
        return double.IsFinite(norm) ? DrawingPath.DefaultTolerance / Math.Max(norm, 1e-9) : 0;
    }

    private static bool StationaryFigure(in PdfPath figure)
    {
        ReadOnlySpan<double> p = figure.Points.Span;
        for (int i = 2; i < p.Length; i += 2)
        {
            if (p[i] != p[0] || p[i + 1] != p[1]) { return false; }
        }

        return true;
    }

    // Canonicalize only the rare mixed path: Close ends a figure, but a following line/curve starts at its first
    // point. Each returned figure has an explicit Move, so both stroke routes restart the PDF dash phase there.
    private static List<PdfPath> StrokeFigures(in PdfPath path, CancellationToken ct)
    {
        var result = new List<PdfPath>();
        var verbs = new List<byte>();
        var coords = new List<double>();
        int p = 0;
        double sx = 0, sy = 0;
        void Flush()
        {
            if (verbs.Count > 1) { result.Add(new PdfPath(verbs.ToArray(), coords.ToArray())); }
            verbs.Clear(); coords.Clear();
        }

        foreach (byte value in path.VerbBytes.Span)
        {
            ct.ThrowIfCancellationRequested();
            var verb = (PdfPathVerb)value;
            if (verb == PdfPathVerb.Move)
            {
                Flush();
                sx = path.Points.Span[p]; sy = path.Points.Span[p + 1];
            }
            else if (verbs.Count == 0 && verb is PdfPathVerb.Line or PdfPathVerb.Curve)
            {
                verbs.Add((byte)PdfPathVerb.Move);
                coords.Add(sx); coords.Add(sy);
            }

            if (verb is PdfPathVerb.Move or PdfPathVerb.Line or PdfPathVerb.Curve or PdfPathVerb.Close)
            {
                verbs.Add(value);
                int count = verb == PdfPathVerb.Curve ? 6 : verb == PdfPathVerb.Close ? 0 : 2;
                for (int i = 0; i < count; i++) { coords.Add(path.Points.Span[p++]); }
                if (verb == PdfPathVerb.Close) { Flush(); }
            }
        }

        Flush();
        return result;
    }

    private static double[] FlattenPrecise(in PdfPath figure, double tolerance, ref int pointCount, CancellationToken ct)
    {
        var xy = new List<double>();
        int count = pointCount;
        void Add(double x, double y)
        {
            if ((count & 1023) == 0) { ct.ThrowIfCancellationRequested(); }
            if (++count > DrawingPath.MaxFlattenedPoints)
            {
                throw new ImageLimitException($"The path flattens to more than {DrawingPath.MaxFlattenedPoints} points.");
            }

            xy.Add(x); xy.Add(y);
        }

        ReadOnlySpan<double> points = figure.Points.Span;
        double sx = points[0], sy = points[1], cx = 0, cy = 0;
        Add(0, 0);
        int p = 2;
        foreach (byte value in figure.VerbBytes.Span[1..])
        {
            switch ((PdfPathVerb)value)
            {
                case PdfPathVerb.Line:
                    cx = points[p++] - sx; cy = points[p++] - sy;
                    Add(cx, cy);
                    break;
                case PdfPathVerb.Curve:
                    double ax = points[p++] - sx, ay = points[p++] - sy;
                    double bx = points[p++] - sx, by = points[p++] - sy;
                    double ex = points[p++] - sx, ey = points[p++] - sy;
                    double curvature = Math.Max(StrokeBuilder.PreciseLength(cx - (2 * ax) + bx, cy - (2 * ay) + by),
                        StrokeBuilder.PreciseLength(ax - (2 * bx) + ex, ay - (2 * by) + ey));
                    double extent = Math.Max(StrokeBuilder.PreciseLength(ax - cx, ay - cy),
                        Math.Max(StrokeBuilder.PreciseLength(bx - cx, by - cy), StrokeBuilder.PreciseLength(ex - cx, ey - cy)));
                    // Extra refinement belongs only to a curve whose control polygon would collapse in the
                    // ordinary float/duplicate pipeline, never to an unrelated ordinary Bezier in this figure.
                    bool collapsed = extent > 0 && (extent <= 1e-9 ||
                        (ex == cx && ey == cy && .75 * curvature <= tolerance) ||
                        ((float)(cx + sx) == (float)(ax + sx) && (float)(cx + sx) == (float)(bx + sx) && (float)(cx + sx) == (float)(ex + sx)
                        && (float)(cy + sy) == (float)(ay + sy) && (float)(cy + sy) == (float)(by + sy) && (float)(cy + sy) == (float)(ey + sy)));
                    double curveTolerance = collapsed ? Math.Min(tolerance, extent * 1e-6) : tolerance;
                    double steps = curveTolerance > 0 ? Math.Sqrt(0.75 * curvature / curveTolerance) : 4096;
                    int n = steps >= 4096 ? 4096 : Math.Max(1, (int)Math.Ceiling(steps));
                    for (int i = 1; i < n; i++)
                    {
                        double t = (double)i / n, u = 1 - t;
                        Add((u * u * u * cx) + (3 * u * u * t * ax) + (3 * u * t * t * bx) + (t * t * t * ex),
                            (u * u * u * cy) + (3 * u * u * t * ay) + (3 * u * t * t * by) + (t * t * t * ey));
                    }

                    Add(ex, ey);
                    cx = ex; cy = ey;
                    break;
                default:
                    break;
            }
        }

        pointCount = count;
        return xy.ToArray();
    }
}
