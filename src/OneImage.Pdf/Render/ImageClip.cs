using OneImage.Drawing;
using DrawingPath = OneImage.Drawing.Path;

namespace OneImage.Pdf.Render;

/// <summary>A bounded proof that a polygonal clip cannot remove any of an image's device-space quad.</summary>
internal static class ImageClip
{
    // This is an optional fast path, not a new limit on accepted PDF geometry. More complicated clips use the existing painter.
    // Eight vertices cover intersections of two image quads while keeping the all-pairs proof cheap.
    private const int MaxVertices = 8;

    public static bool Contains(DrawingPath clip, DrawingPath quad)
    {
        if (!TryPolygon(clip, out int count) || !TryPolygon(quad, out int corners) || corners != 4)
        {
            return false;
        }

        ReadOnlySpan<float> p = clip.Coords, q = quad.Coords;
        int direction = 0;
        for (int i = 0; i < count && direction == 0; i++)
        {
            int j = (i + 1) % count, k = (i + 2) % count;
            direction = Side(p[2 * i], p[(2 * i) + 1], p[2 * j], p[(2 * j) + 1], p[2 * k], p[(2 * k) + 1]);
        }

        if (direction == 0)
        {
            return false;
        }

        for (int i = 0; i < count; i++)
        {
            int j = (i + 1) % count;
            float ax = p[2 * i], ay = p[(2 * i) + 1], bx = p[2 * j], by = p[(2 * j) + 1];
            if (ax == bx && ay == by)
            {
                continue;
            }

            // Requiring every vertex inside every edge proves convexity, including for self-intersecting input. Testing only
            // consecutive turns would admit stars. Multiple contours, holes and curves were rejected without flattening.
            for (int k = 0; k < count + corners; k++)
            {
                float x = k < count ? p[2 * k] : q[2 * (k - count)];
                float y = k < count ? p[(2 * k) + 1] : q[(2 * (k - count)) + 1];
                if ((x == ax && y == ay) || (x == bx && y == by) || (ax == bx && x == ax) || (ay == by && y == ay))
                {
                    continue;
                }

                if (Side(ax, ay, bx, by, x, y) != direction)
                {
                    return false;
                }
            }
        }

        return true;
    }

    private static bool TryPolygon(DrawingPath path, out int count)
    {
        count = 0;
        ReadOnlySpan<byte> verbs = path.Verbs;
        if (verbs.Length < 4 || verbs.Length > MaxVertices + 2 || verbs[0] != (byte)Verb.Move)
        {
            return false;
        }

        int end = verbs[^1] == (byte)Verb.Close ? verbs.Length - 1 : verbs.Length;
        for (int i = 1; i < end; i++)
        {
            if (verbs[i] != (byte)Verb.Line)
            {
                return false;
            }
        }

        count = end;
        ReadOnlySpan<float> p = path.Coords;
        if (count > MaxVertices || p.Length != count * 2)
        {
            return false;
        }

        foreach (float v in p)
        {
            if (!float.IsFinite(v))
            {
                return false;
            }
        }

        if (p[0] == p[^2] && p[1] == p[^1])
        {
            count--;
        }

        // A contour that traverses a convex boundary more than once has a different even-odd interior. Reject repeated
        // vertices (apart from the explicit closing point removed above) rather than assuming its winding is one.
        for (int i = 0; i < count; i++)
        {
            for (int j = i + 1; j < count; j++)
            {
                if (p[2 * i] == p[2 * j] && p[(2 * i) + 1] == p[(2 * j) + 1])
                {
                    return false;
                }
            }
        }

        return count >= 3;
    }

    private static int Side(float ax, float ay, float bx, float by, float x, float y)
    {
        double left = ((double)bx - ax) * ((double)y - ay), right = ((double)by - ay) * ((double)x - ax);
        double cross = left - right;
        // A rounding-error guard only REJECTS uncertain containment. It never expands a clip or treats near points as equal.
        // Exact shared vertices and horizontal/vertical collinearity are handled above; other near-collinear cases fall back.
        double error = (Math.Abs(left) + Math.Abs(right)) * (8 * 2.2204460492503131e-16);
        return cross > error ? 1 : cross < -error ? -1 : 0;
    }
}
