using System.Runtime.InteropServices;
using OneImage.Drawing;
using OneImage.Kernels;

namespace OneImage.Tests.Drawing;

public class NonSolidRgbaBlendTests
{
    [Fact]
    public void EveryByteAlphaPairMatchesGenericPipeline()
    {
        var random = new Random(18571);
        float[] opacities = [0f, 1f / 255f, 0.37f, 0.999f, 1f];
        float[] coverages = [1f / 1024f, 0.25f, 0.5f, 0.999f, 1f];
        const int width = 128;
        var back = new byte[width * 4];
        var source = new float[width * 4];
        var coverage = new float[width];
        foreach (float opacity in opacities)
        {
            foreach (float c in coverages)
            {
                Array.Fill(coverage, c);
                for (int start = 0; start < 65536; start += width)
                {
                    random.NextBytes(back);
                    for (int x = 0; x < width; x++)
                    {
                        int pair = start + x;
                        back[(x * 4) + 3] = (byte)pair;
                        source[(x * 4) + 3] = (pair / 256) / 255f;
                        for (int k = 0; k < 3; k++)
                        {
                            source[(x * 4) + k] = random.Next(256) / 255f;
                        }
                    }

                    Check(back, source, coverage, opacity, false);
                }
            }
        }
    }

    [Fact]
    public void MixedRunsAndFloatBrushesMatchGenericPipeline()
    {
        var random = new Random(73195);
        float[] unusual = [float.NaN, float.PositiveInfinity, float.NegativeInfinity, -1f, -0f, 0f,
            float.Epsilon, 0.5f, 1f, 1.5f, float.MaxValue];
        int[] widths = [1, 2, 7, 31, 64, 127, 128];
        foreach (int width in widths)
        {
            for (int trial = 0; trial < 120; trial++)
            {
                var back = new byte[width * 4];
                random.NextBytes(back);
                var source = new float[width * 4];
                var coverage = new float[width];
                for (int x = 0; x < width; x++)
                {
                    coverage[x] = trial % 4 == 0 ? 1f : x % 5 == 0 ? 0f : random.NextSingle();
                    for (int k = 0; k < 4; k++)
                    {
                        source[(x * 4) + k] = trial % 3 == 0 ? unusual[random.Next(unusual.Length)] : random.NextSingle();
                    }
                }

                Check(back, source, coverage, trial % 4 == 0 ? 1f : random.NextSingle(), false);
                Check(back, source, coverage, trial % 4 == 0 ? 1f : random.NextSingle(), true);
            }
        }
    }

    [Fact]
    public void OpaqueReplacementAndTransparentHiddenColorsMatchGenericPipeline()
    {
        byte[] back = [12, 34, 56, 0, 255, 0, 127, 255, 0, 32, 255, 81];
        float[] source = [0.25f, 0.75f, 0.5f, 1f, 1f, 0f, 0.3f, 1f, 0f, 1f, 0.5f, 1f];
        Check(back, source, [1f, 1f, 1f], 1f, false);
        source[3] = 0f;
        source[7] = 0f;
        source[11] = 0f;
        Check(back, source, [1f, 0.5f, 1f], 1f, false);
    }

    private static void Check(byte[] back, float[] source, float[] coverage, float opacity, bool readsBackdrop)
    {
        int width = coverage.Length;
        var brush = new RowBrush(source, readsBackdrop);
        byte[] actual = (byte[])back.Clone();
        byte[] expected = Reference(back, brush, coverage, opacity);
        RasterScratch scratch = RasterScratch.Rent();
        coverage.CopyTo(scratch.Coverage, 0);
        scratch.SpanEnd[0] = width;
        FillSettings settings = FillSettings.Check(true, IntersectionRule.NonZero, opacity,
            BlendMode.Normal, AlphaComposition.SrcOver, false, null, PixelFormat.Rgba8);
        FillPlan.Create(PixelFormat.Rgba8, brush, settings).Paint(actual, width, 1, 0, 0, scratch);
        RasterScratch.Return(scratch);
        Assert.Equal(expected, actual);
    }

    // Independently retain the old generic conversion/blend/coverage pipeline, including run-level opaque replacement.
    private static byte[] Reference(byte[] back, RowBrush brush, float[] coverage, float opacity)
    {
        byte[] expected = (byte[])back.Clone();
        var work = new PixelFormat(ColorModel.Rgb, SampleType.F32, AlphaMode.Premultiplied);
        int x = 0;
        while (x < coverage.Length)
        {
            if (coverage[x] <= 0f)
            {
                x++;
                continue;
            }

            int end = x + 1;
            while (end < coverage.Length && coverage[end] > 0f)
            {
                end++;
            }

            int n = end - x;
            Span<byte> stored = expected.AsSpan(x * 4, n * 4);
            var rgba = new float[n * 4];
            if (brush.ReadsBackdrop)
            {
                var straight = new float[n * 4];
                ConvertKernel.ConvertRow(stored, PixelFormat.Rgba8, MemoryMarshal.AsBytes(straight.AsSpan()), PixelFormat.RgbaF32, n);
                brush.FillRow(x, 0, straight, rgba);
            }
            else
            {
                brush.FillRow(x, 0, rgba);
            }

            bool opaque = opacity >= 1f;
            for (int i = 0; i < n; i++)
            {
                if (coverage[x + i] < 1f || rgba[(i * 4) + 3] < 1f)
                {
                    opaque = false;
                }
            }

            if (opaque)
            {
                BrushKernel.RgbaF32ToRgba8(rgba, stored);
            }
            else
            {
                var backdrop = new float[n * 4];
                var overlay = new float[n * 4];
                var result = new float[n * 4];
                ConvertKernel.ConvertRow(stored, PixelFormat.Rgba8, MemoryMarshal.AsBytes(backdrop.AsSpan()), work, n);
                ConvertKernel.ConvertRow(MemoryMarshal.AsBytes(rgba.AsSpan()), PixelFormat.RgbaF32,
                    MemoryMarshal.AsBytes(overlay.AsSpan()), work, n);
                BlendKernel.Row(BlendMode.Normal, backdrop, overlay, result, 3, opacity, AlphaComposition.SrcOver);
                for (int i = 0; i < n; i++)
                {
                    float c = coverage[x + i];
                    if (c < 1f)
                    {
                        for (int k = 0; k < 4; k++)
                        {
                            int j = (i * 4) + k;
                            result[j] = backdrop[j] + ((result[j] - backdrop[j]) * c);
                        }
                    }
                }

                ConvertKernel.ConvertRow(MemoryMarshal.AsBytes(result.AsSpan()), work, stored, PixelFormat.Rgba8, n);
            }

            x = end;
        }

        return expected;
    }

    private sealed class RowBrush(float[] values, bool readsBackdrop) : Brush
    {
        public override bool ReadsBackdrop => readsBackdrop;

        public override void FillRow(int x, int y, Span<float> rgba) => values.AsSpan(x * 4, rgba.Length).CopyTo(rgba);

        public override void FillRow(int x, int y, ReadOnlySpan<float> backdrop, Span<float> rgba)
        {
            FillRow(x, y, rgba);
            for (int i = 0; i < rgba.Length; i += 4)
            {
                rgba[i] = (rgba[i] + backdrop[i + 1]) * 0.5f;
                rgba[i + 1] = backdrop[i];
                rgba[i + 2] *= backdrop[i + 2];
            }
        }
    }
}
