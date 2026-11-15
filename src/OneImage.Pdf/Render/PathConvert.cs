using System.Numerics;
using OneImage.Drawing;
using OnePdf;
using DrawingPath = OneImage.Drawing.Path;

namespace OneImage.Pdf.Render;

/// <summary>Turns OnePDF paths (double precision, any coordinates) into engine paths (float, finite, bounded).</summary>
internal static class PathConvert
{
    // The engine's boolean operations accept coordinates within +-2^25; fills far outside the picture are clamped to this so that
    // a hostile coordinate cannot overflow the rasterizer. Anything this far out is invisible, but a very steep edge crossing the
    // picture would bend: PDF writers do not produce those.
    private const double Limit = 1 << 24;

    /// <summary>Appends <paramref name="path"/> mapped through <paramref name="m"/> to <paramref name="b"/>. Returns false (and appends nothing useful) when a coordinate is not finite.</summary>
    public static bool Append(PathBuilder b, in PdfPath path, in PdfMatrix m, bool clamp) =>
        Append(b, path, m, clamp, false, out _);

    private static bool Append(PathBuilder b, in PdfPath path, in PdfMatrix m, bool clamp, bool omitStationaryCloses, out bool truncatedSegment)
    {
        truncatedSegment = false;
        ReadOnlySpan<byte> verbs = path.VerbBytes.Span;
        ReadOnlySpan<double> pts = path.Points.Span;
        int p = 0;
        bool open = false, stationary = false;
        double sx = 0, sy = 0;
        for (int i = 0; i < verbs.Length; i++)
        {
            switch ((PdfPathVerb)verbs[i])
            {
                case PdfPathVerb.Move:
                    {
                        if (p + 2 > pts.Length)
                        {
                            return true;
                        }

                        sx = pts[p]; sy = pts[p + 1];
                        stationary = omitStationaryCloses;
                        (float x, float y) = Map(pts[p], pts[p + 1], m, clamp);
                        p += 2;
                        if (!float.IsFinite(x + y))
                        {
                            return false;
                        }

                        b.MoveTo(x, y);
                        open = true;
                        break;
                    }

                case PdfPathVerb.Line:
                    {
                        if (p + 2 > pts.Length)
                        {
                            truncatedSegment = true;
                            return true;
                        }

                        stationary = stationary && pts[p] == sx && pts[p + 1] == sy;
                        (float x, float y) = Map(pts[p], pts[p + 1], m, clamp);
                        p += 2;
                        if (!float.IsFinite(x + y))
                        {
                            return false;
                        }

                        if (!open)
                        {
                            b.MoveTo(x, y);
                            open = true;
                        }
                        else
                        {
                            b.LineTo(x, y);
                        }

                        break;
                    }

                case PdfPathVerb.Curve:
                    {
                        if (p + 6 > pts.Length)
                        {
                            truncatedSegment = true;
                            return true;
                        }

                        stationary = stationary && pts[p] == sx && pts[p + 1] == sy
                            && pts[p + 2] == sx && pts[p + 3] == sy && pts[p + 4] == sx && pts[p + 5] == sy;
                        (float x1, float y1) = Map(pts[p], pts[p + 1], m, clamp);
                        (float x2, float y2) = Map(pts[p + 2], pts[p + 3], m, clamp);
                        (float x3, float y3) = Map(pts[p + 4], pts[p + 5], m, clamp);
                        p += 6;
                        if (!float.IsFinite(x1 + y1 + x2 + y2 + x3 + y3))
                        {
                            return false;
                        }

                        if (!open)
                        {
                            b.MoveTo(x1, y1);
                            open = true;
                        }

                        b.CubicBezierTo(x1, y1, x2, y2, x3, y3);
                        break;
                    }

                case PdfPathVerb.Close:
                    // The PDF round-cap pass owns exact stationary subpaths. Keeping them open here prevents
                    // the core stroker from constructing a second disc. Compare doubles before float conversion:
                    // a short segment rounded to one point is not an exact PDF degenerate subpath.
                    if (open && !stationary)
                    {
                        b.Close();
                    }

                    break;
                default:
                    break;
            }
        }

        return true;
    }

    /// <summary>Builds the path mapped through <paramref name="m"/>, or null when it is empty or has a coordinate that is not finite.
    /// Omit stationary closes only when the caller supplies their zero-length round caps separately.</summary>
    public static DrawingPath? ToPath(in PdfPath path, in PdfMatrix m, bool clamp = true, bool omitStationaryCloses = false)
    {
        if (path.IsEmpty)
        {
            return null;
        }

        var b = new PathBuilder();
        if (!Append(b, path, m, clamp, omitStationaryCloses, out bool truncatedSegment))
        {
            return null;
        }

        // ZeroLengthDiscs does not flush the current subpath when a line or curve lacks operands. Preserve the
        // original core outline for such malformed input rather than dropping its already completed closed geometry.
        if (omitStationaryCloses && truncatedSegment)
        {
            b = new PathBuilder();
            Append(b, path, m, clamp);
        }

        DrawingPath built = b.Build();
        return built.IsEmpty ? null : built;
    }

    public static Matrix3x2 ToMatrix(in PdfMatrix m) => new((float)m.A, (float)m.B, (float)m.C, (float)m.D, (float)m.E, (float)m.F);

    /// <summary>The scale of a matrix as the square root of its area factor.</summary>
    public static double MeanScale(in PdfMatrix m) => Math.Sqrt(Math.Abs(m.Determinant));

    private static (float, float) Map(double x, double y, in PdfMatrix m, bool clamp)
    {
        double dx = (m.A * x) + (m.C * y) + m.E;
        double dy = (m.B * x) + (m.D * y) + m.F;
        if (clamp)
        {
            dx = Math.Clamp(dx, -Limit, Limit);
            dy = Math.Clamp(dy, -Limit, Limit);
        }

        return ((float)dx, (float)dy);
    }
}
