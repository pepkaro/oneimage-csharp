using OneImage.Pdf.Render;

namespace OneImage.Pdf.Tests;

/// <summary>The cached axis mapping preserves the scalar resampler's rounding and alpha behavior.</summary>
public class AreaResizeTests
{
    [Theory]
    [InlineData(false)]
    [InlineData(true)]
    public void SmallSizesAndRatiosMatchScalarReference(bool stencil)
    {
        var random = new Random(58131);
        for (int sw = 1; sw <= 19; sw++)
        {
            for (int sh = 1; sh <= 9; sh++)
            {
                Rgba32[] pixels = Pixels(sw * sh, random);
                for (int dw = 1; dw <= sw; dw++)
                {
                    for (int dh = 1; dh <= sh; dh++)
                    {
                        Equal(AreaResizeReference.Area(pixels, sw, sh, dw, dh, stencil, default), Resize.Area(pixels, sw, sh, dw, dh, stencil, default));
                    }
                }
            }
        }
    }

    [Theory]
    [InlineData(1, 257, 1, 31)]
    [InlineData(16383, 3, 391, 2)]
    [InlineData(16384, 3, 391, 2)]
    [InlineData(16385, 3, 391, 2)]
    [InlineData(16384, 1, 31, 1)]
    [InlineData(301, 217, 97, 53)]
    [InlineData(997, 31, 2, 2)]
    public void LargerImagesAndScratchBoundaryMatchScalarReference(int sw, int sh, int dw, int dh)
    {
        Rgba32[] pixels = Pixels(sw * sh, new Random(9147));
        foreach (bool stencil in new[] { false, true })
        {
            Equal(AreaResizeReference.Area(pixels, sw, sh, dw, dh, stencil, default), Resize.Area(pixels, sw, sh, dw, dh, stencil, default));
        }
    }

    [Fact]
    public void PooledWeightsArePrivateToEachConcurrentResize()
    {
        Parallel.For(0, 32, new ParallelOptions { MaxDegreeOfParallelism = 4 }, i =>
        {
            int sw = 191 + i, sh = 37 + (i % 11), dw = 23 + (i % 17), dh = 7 + (i % 5);
            Rgba32[] pixels = Pixels(sw * sh, new Random(i));
            Equal(AreaResizeReference.Area(pixels, sw, sh, dw, dh, false, default), Resize.Area(pixels, sw, sh, dw, dh, false, default));
        });
    }

    [Fact]
    public void CanceledAndFailedResizesDoNotContaminateLaterResults()
    {
        Rgba32[] pixels = Pixels(997 * 7, new Random(13));
        using var cts = new CancellationTokenSource();
        cts.Cancel();
        Assert.Throws<OperationCanceledException>(() => Resize.Area(pixels, 997, 7, 127, 3, false, cts.Token));
        Assert.Throws<ArgumentOutOfRangeException>(() => Resize.Area([], 997, 7, 127, 3, false, default));
        Equal(AreaResizeReference.Area(pixels, 997, 7, 127, 3, false, default), Resize.Area(pixels, 997, 7, 127, 3, false, default));
    }

    private static Rgba32[] Pixels(int length, Random random)
    {
        byte[] alpha = [0, 1, 63, 127, 128, 191, 254, 255];
        var pixels = new Rgba32[length];
        for (int i = 0; i < length; i++)
        {
            pixels[i] = new Rgba32((byte)random.Next(256), (byte)random.Next(256), (byte)random.Next(256), alpha[i % alpha.Length]);
        }

        return pixels;
    }

    private static void Equal(Rgba32[] expected, Rgba32[] actual) => Assert.True(expected.AsSpan().SequenceEqual(actual));
}

// Keep the original streaming scalar order as a differential oracle. It deliberately recalculates horizontal weights per row.
internal static class AreaResizeReference
{
    /// <summary>Area average to a smaller (or equal) size, streaming over the source rows in memory proportional to the destination row.</summary>
    public static Rgba32[] Area(Rgba32[] src, int sw, int sh, int dw, int dh, bool stencil, CancellationToken ct)
    {
        var dst = new Rgba32[(long)dw * dh];
        float[] rowAcc = new float[dw * 4];
        float[] acc0 = new float[dw * 4];
        float[] acc1 = new float[dw * 4];
        Array.Clear(acc0, 0, dw * 4);
        Array.Clear(acc1, 0, dw * 4);
        double yScale = (double)dh / sh;
        double xScale = (double)dw / sw;
        int curDst = 0;
        for (int y = 0; y < sh; y++)
        {
            if ((y & 63) == 0)
            {
                ct.ThrowIfCancellationRequested();
            }

            HorizontalRow(src.AsSpan(y * sw, sw), rowAcc, dw, xScale);
            double top = y * yScale, bottom = (y + 1) * yScale;
            int d0 = Math.Min((int)top, dh - 1);
            int d1 = Math.Min((int)(bottom - 1e-9), dh - 1);
            if (d0 != curDst)
            {
                // Rows above d0 are finished: only the last accumulator can still be open.
                Flush(acc0, dst, curDst, dw, stencil);
                (acc0, acc1) = (acc1, acc0);
                Array.Clear(acc1, 0, dw * 4);
                curDst = d0;
            }

            double wA = d0 == d1 ? bottom - top : (d0 + 1) - top;
            Accumulate(acc0, rowAcc, dw, (float)wA);
            if (d1 != d0)
            {
                double wB = bottom - d1;
                Accumulate(acc1, rowAcc, dw, (float)wB);
            }
        }

        Flush(acc0, dst, curDst, dw, stencil);
        if (curDst + 1 < dh)
        {
            Flush(acc1, dst, curDst + 1, dw, stencil);
        }

        return dst;
    }

    private static void HorizontalRow(ReadOnlySpan<Rgba32> row, float[] acc, int dw, double xScale)
    {
        Array.Clear(acc, 0, dw * 4);
        for (int x = 0; x < row.Length; x++)
        {
            double left = x * xScale, right = (x + 1) * xScale;
            int d0 = Math.Min((int)left, dw - 1);
            int d1 = Math.Min((int)(right - 1e-9), dw - 1);
            Rgba32 p = row[x];
            float a = p.A * (1f / 255f);
            float pr = p.R * a, pg = p.G * a, pb = p.B * a;
            double wA = d0 == d1 ? right - left : (d0 + 1) - left;
            float fa = (float)wA;
            int o = d0 * 4;
            acc[o] += pr * fa;
            acc[o + 1] += pg * fa;
            acc[o + 2] += pb * fa;
            acc[o + 3] += a * fa;
            if (d1 != d0)
            {
                float fb = (float)(right - d1);
                o = d1 * 4;
                acc[o] += pr * fb;
                acc[o + 1] += pg * fb;
                acc[o + 2] += pb * fb;
                acc[o + 3] += a * fb;
            }
        }
    }

    private static void Accumulate(float[] acc, float[] row, int dw, float weight)
    {
        for (int i = 0; i < dw * 4; i++)
        {
            acc[i] += row[i] * weight;
        }
    }

    private static void Flush(float[] acc, Rgba32[] dst, int row, int dw, bool stencil)
    {
        int o = row * dw;
        for (int x = 0; x < dw; x++)
        {
            float a = acc[(x * 4) + 3];
            if (a <= 1e-6f)
            {
                dst[o + x] = default;
                continue;
            }

            // The sums hold color in 0..255 times alpha in 0..1, so dividing by alpha and by 255 gives the 0..1 range ToByte expects.
            float inv = 1f / (a * 255f);
            dst[o + x] = stencil
                ? new Rgba32(0, 0, 0, ToByte(a))
                : new Rgba32(ToByte(acc[x * 4] * inv), ToByte(acc[(x * 4) + 1] * inv), ToByte(acc[(x * 4) + 2] * inv), ToByte(a));
        }
    }

    private static byte ToByte(float v) => v <= 0 ? (byte)0 : v >= 1 ? (byte)255 : (byte)((v * 255f) + 0.5f);

}
