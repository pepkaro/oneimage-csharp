// SPDX-License-Identifier: MIT
using OneImage.Drawing;
using OneImage.Kernels;

namespace OneImage.Pdf.Render;

internal enum KnockoutChannel { Color, Alpha, Shape }

/// <summary>
/// ISO 11.4.6: blend an element with the initial backdrop, then replace the immediate backdrop by its shape.
/// Geometry coverage is applied once by Fill; intrinsic shape and opacity remain separate here.
/// All brushes are borrowed and immutable for the duration of a fill. Scratch storage is bounded and per call.
/// </summary>
internal sealed class KnockoutBrush(Brush source, Brush intrinsicShape, Brush? initial, Brush? mask, Brush? stencil,
    float opacity, bool alphaIsShape, BlendMode blend, KnockoutChannel channel) : Brush
{
    public override bool ReadsBackdrop => channel != KnockoutChannel.Shape;

    public override void FillRow(int x, int y, Span<float> rgba) => FillRow(x, y, default, rgba);

    public override void FillRow(int x, int y, ReadOnlySpan<float> backdrop, Span<float> rgba)
    {
        const int chunk = 64 * 4;
        Span<float> initialRow = stackalloc float[chunk];
        Span<float> sourceRow = stackalloc float[chunk];
        Span<float> shapeRow = stackalloc float[chunk];
        Span<float> maskRow = stackalloc float[chunk];
        Span<float> stencilRow = stackalloc float[chunk];
        Span<float> composite = stackalloc float[chunk];
        for (int start = 0; start < rgba.Length; start += chunk)
        {
            int length = Math.Min(chunk, rgba.Length - start), column = checked(x + (start / 4));
            Span<float> b = initialRow[..length], s = sourceRow[..length], f = shapeRow[..length];
            Span<float> m = maskRow[..length], st = stencilRow[..length], t = composite[..length];
            if (channel != KnockoutChannel.Shape)
            {
                if (initial is null) b.Clear(); else initial.FillRow(column, y, b);
                source.FillRow(column, y, b, s);
            }
            intrinsicShape.FillRow(column, y, f);
            mask?.FillRow(column, y, m);
            stencil?.FillRow(column, y, st);
            for (int i = 0; i < length; i += 4)
            {
                float amount = opacity * (mask is null ? 1 : m[i + 3]);
                float geometric = Math.Clamp(f[i + 3], 0, 1) * (stencil is null ? 1 : st[i + 3]);
                float sourceAlpha = (channel == KnockoutChannel.Shape ? 0 : Math.Clamp(s[i + 3], 0, 1)) * amount * (stencil is null ? 1 : st[i + 3]);
                if (alphaIsShape) geometric *= amount;
                geometric = Math.Clamp(geometric, 0, 1);
                f[i + 3] = geometric;
                if (channel != KnockoutChannel.Color)
                {
                    int at = start + i;
                    rgba[at] = rgba[at + 1] = rgba[at + 2] = 1;
                    rgba[at + 3] = channel == KnockoutChannel.Shape ? geometric :
                        sourceAlpha + ((1 - geometric) * (backdrop.IsEmpty ? 0 : backdrop[at + 3]));
                    continue;
                }
                // Remove intrinsic shape before blending: it weights the completed result below, not its opacity.
                float q = geometric > 0 ? Math.Clamp(sourceAlpha / geometric, 0, 1) : 0;
                for (int c = 0; c < 3; c++)
                {
                    s[i + c] *= q;
                    b[i + c] *= b[i + 3];
                }
                s[i + 3] = q;
            }
            if (channel != KnockoutChannel.Color) continue;
            BlendKernel.Row(blend, b, s, t, 3, 1, AlphaComposition.SrcOver);
            for (int i = 0; i < length; i += 4)
            {
                int at = start + i;
                float shape = f[i + 3], keep = 1 - shape;
                float priorAlpha = backdrop.IsEmpty ? 0 : backdrop[at + 3];
                float alpha = (shape * t[i + 3]) + (keep * priorAlpha);
                for (int c = 0; c < 3; c++)
                {
                    float prior = backdrop.IsEmpty ? 0 : backdrop[at + c] * priorAlpha;
                    rgba[at + c] = alpha > 0 ? ((shape * t[i + c]) + (keep * prior)) / alpha : 0;
                }
                rgba[at + 3] = alpha;
            }
        }
    }
}
