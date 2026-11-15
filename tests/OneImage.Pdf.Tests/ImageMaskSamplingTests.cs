// SPDX-License-Identifier: MIT
// Copyright (c) 2026 OneImage contributors
using OneImage.Pdf.Render;
using OnePdf;

namespace OneImage.Pdf.Tests;

/// <summary>Original numerical fixtures: color and mask samples independently cover the unit square.</summary>
public class ImageMaskSamplingTests
{
    private static Rgba32 Color(int x, int y) => new((byte)(37 + ((x * 59 + y * 17) % 197)),
        (byte)(29 + ((x * 31 + y * 67) % 211)), (byte)(19 + ((x * 83 + y * 43) % 223)), 255);

    private static byte Alpha(int x, int y, bool opaque, bool stencil) => opaque ? (byte)255 : stencil
        ? (byte)(((x + 2 * y) % 3 == 0) ? 0 : 255) : new byte[] { 0, 91, 173, 255 }[(x + 3 * y) % 4];

    private static byte[] Page(int cw, int ch, int mw, int mh, bool opaque = false, bool stencil = false,
        bool decode = false, string placement = "210 0 0 198 15 12", string interpolate = "false", string maskInterpolate = "false")
    {
        byte[] colors = new byte[cw * ch * 3];
        for (int y = 0; y < ch; y++)
        {
            for (int x = 0; x < cw; x++)
            {
                Rgba32 p = Color(x, y);
                int i = (y * cw + x) * 3;
                colors[i] = p.R; colors[i + 1] = p.G; colors[i + 2] = p.B;
            }
        }

        var objects = new List<string>();
        string mask = mw == 0 ? "" : stencil ? "/Mask 6 0 R" : "/SMask 6 0 R";
        objects.Add(RegionTests.Obj($"/Type /XObject /Subtype /Image /Width {cw} /Height {ch} /ColorSpace /DeviceRGB /BitsPerComponent 8 /Interpolate {interpolate} /Filter /ASCIIHexDecode {mask}", Convert.ToHexString(colors) + ">"));
        if (mw > 0)
        {
            byte[] values = new byte[(stencil ? (mw + 7) / 8 : mw) * mh];
            for (int y = 0; y < mh; y++)
            {
                for (int x = 0; x < mw; x++)
                {
                    byte a = Alpha(x, y, opaque, stencil);
                    if (stencil)
                    {
                        bool bit = decode ? a > 0 : a == 0;
                        if (bit) values[y * ((mw + 7) / 8) + x / 8] |= (byte)(128 >> (x % 8));
                    }
                    else values[y * mw + x] = decode ? (byte)(255 - a) : a;
                }
            }

            string mode = stencil ? "/ImageMask true /BitsPerComponent 1" : "/ColorSpace /DeviceGray /BitsPerComponent 8";
            objects.Add(RegionTests.Obj($"/Type /XObject /Subtype /Image /Width {mw} /Height {mh} {mode} /Interpolate {maskInterpolate} /Decode [{(decode ? "1 0" : "0 1")}] /Filter /ASCIIHexDecode", Convert.ToHexString(values) + ">"));
        }

        return TestPdf.Page($"q {placement} cm /Im Do Q", "/XObject << /Im 5 0 R >>", 240, 222, objects.ToArray());
    }

    private static Image Load(byte[] bytes, bool smooth = false, long cache = 1 << 26, double dpi = 72) => RenderTests.Load(bytes,
        new PdfRenderOptions { Dpi = dpi, SmoothMagnifiedImages = smooth, Limits = new PdfRenderLimits { MaxCachedPixels = cache } });

    private static void Equal(Rgba32[] a, Rgba32[] b) => Assert.True(a.AsSpan().SequenceEqual(b));

    [Theory]
    [InlineData(3, 5, 7, 11)]
    [InlineData(11, 7, 3, 5)]
    [InlineData(3, 11, 7, 5)]
    [InlineData(11, 3, 5, 7)]
    [InlineData(401, 1, 1, 409)]
    public void OpaqueMaskDoesNotChangeColorSamples(int cw, int ch, int mw, int mh)
    {
        foreach (string placement in new[] { "210 0 0 198 15 12", "0 198 -210 0 225 12", "-210 0 0 198 225 12", "183 23 -19 169 36 16" })
        {
            foreach (bool smooth in new[] { false, true })
            foreach (double dpi in new[] { 36.0, 72.0, 144.0 })
            {
                Equal(Load(Page(cw, ch, 0, 0, placement: placement), smooth, dpi: dpi).ToArray<Rgba32>(),
                    Load(Page(cw, ch, mw, mh, opaque: true, placement: placement), smooth, dpi: dpi).ToArray<Rgba32>());
            }
        }
    }

    [Theory]
    [InlineData(3, 5, 7, 11)]
    [InlineData(11, 7, 3, 5)]
    [InlineData(3, 11, 7, 5)]
    [InlineData(11, 3, 5, 7)]
    public void NearestPlanesUseTheirOwnSampleBoundaries(int cw, int ch, int mw, int mh)
    {
        foreach (bool stencil in new[] { false, true })
        {
            foreach (bool decode in new[] { false, true })
            {
                Rgba32[] pixels = Load(Page(cw, ch, mw, mh, stencil: stencil, decode: decode)).ToArray<Rgba32>();
                for (int y = 12; y < 210; y++)
                {
                    for (int x = 15; x < 225; x++)
                    {
                        double u = (x + .5 - 15) / 210, v = (y + .5 - 12) / 198;
                        Rgba32 c = Color((int)(u * cw), (int)(v * ch));
                        byte a = Alpha((int)(u * mw), (int)(v * mh), false, stencil);
                        Rgba32 actual = pixels[y * 240 + x];
                        static int Composite(byte c, byte a) => (int)Math.Round((c * a + 255 * (255 - a)) / 255.0);
                        Assert.InRange((int)actual.R, Composite(c.R, a) - 1, Composite(c.R, a) + 1);
                        Assert.InRange((int)actual.G, Composite(c.G, a) - 1, Composite(c.G, a) + 1);
                        Assert.InRange((int)actual.B, Composite(c.B, a) - 1, Composite(c.B, a) + 1);
                    }
                }
            }
        }
    }

    [Theory]
    [InlineData(false)]
    [InlineData(true)]
    public void IndependentPlanesAreStableAcrossRegionsAndThreadCounts(bool smooth)
    {
        byte[] pdf = Page(3, 11, 7, 5, placement: "183 23 -19 169 36 16");
        Rgba32[] whole = Load(pdf, smooth).ToArray<Rgba32>(maxDegree: 1);
        foreach (int degree in new[] { 1, 4, 16 })
        {
            Equal(whole, Load(pdf, smooth, cache: 0).ToArray<Rgba32>(maxDegree: degree));
            foreach (var r in new[] { new ImageRect(127, 127, 2, 2), new ImageRect(31, 63, 193, 129) })
            {
                var part = new Rgba32[r.Width * r.Height];
                Load(pdf, smooth).CopyPixelsTo<Rgba32>(part, r, degree);
                for (int y = 0; y < r.Height; y++)
                    Assert.True(part.AsSpan(y * r.Width, r.Width).SequenceEqual(whole.AsSpan((r.Y + y) * 240 + r.X, r.Width)));
            }
        }
    }
    [Theory]
    [InlineData(false, true, 3, 5)]
    [InlineData(true, false, 3, 5)]
    [InlineData(false, true, 7, 11)]
    [InlineData(true, false, 7, 11)]
    public void EachPlaneHonorsItsInterpolationFlag(bool colorInterpolate, bool maskInterpolate, int mw, int mh)
    {
        byte[] pdf = Page(3, 5, mw, mh, interpolate: colorInterpolate ? "true" : "false", maskInterpolate: maskInterpolate ? "true" : "false");
        Rgba32[] pixels = Load(pdf).ToArray<Rgba32>();
        static double Sample(double u, double v, int w, int h, bool linear, Func<int, int, double> sample)
        {
            if (!linear) return sample(Math.Clamp((int)(u * w), 0, w - 1), Math.Clamp((int)(v * h), 0, h - 1));
            double x = u * w - .5, y = v * h - .5;
            int ix = (int)Math.Floor(x), iy = (int)Math.Floor(y);
            double fx = x - ix, fy = y - iy;
            double At(int a, int b) => sample(Math.Clamp(a, 0, w - 1), Math.Clamp(b, 0, h - 1));
            return At(ix, iy) * (1 - fx) * (1 - fy) + At(ix + 1, iy) * fx * (1 - fy) +
                At(ix, iy + 1) * (1 - fx) * fy + At(ix + 1, iy + 1) * fx * fy;
        }

        for (int y = 19; y < 204; y += 7)
        {
            for (int x = 19; x < 220; x += 7)
            {
                double u = (x + .5 - 15) / 210, v = (y + .5 - 12) / 198;
                double a = Sample(u, v, mw, mh, maskInterpolate, (i, j) => Alpha(i, j, false, false)) / 255;
                double r = Sample(u, v, 3, 5, colorInterpolate, (i, j) => Color(i, j).R);
                double expected = r * a + 255 * (1 - a);
                Assert.InRange((double)pixels[y * 240 + x].R, expected - 1, expected + 1);
            }
        }

        // The opt-in viewer policy applies to color and decoded opacity, not just the parent color flag.
        Equal(Load(Page(3, 5, mw, mh, interpolate: "true", maskInterpolate: "true")).ToArray<Rgba32>(),
            Load(pdf, smooth: true).ToArray<Rgba32>());
    }

    [Fact]
    public void IndependentRasterStorageIsAdditiveNotTheCrossProductOfDimensions()
    {
        using PdfDocument doc = PdfDocument.Open(Page(401, 1, 1, 409));
        PdfImageData data = PdfImageData.FromXObject(doc, (PdfStream)doc.GetObject(5)!)!;
        Raster raster = Raster.FromData(data, CancellationToken.None)!;
        Assert.Equal(401, raster.Width);
        Assert.Equal(1, raster.Height);
        Assert.Equal(810, raster.PixelCount);
        Raster reduced = raster.Reduce(40, 30, CancellationToken.None);
        Assert.Equal(40, reduced.Width);
        Assert.Equal(30, reduced.Mask!.Height);
        Assert.Equal(70, reduced.PixelCount);
        using var cancel = new CancellationTokenSource();
        cancel.Cancel();
        Assert.Throws<OperationCanceledException>(() => Raster.FromData(data, cancel.Token));
        Assert.Throws<OperationCanceledException>(() => raster.Reduce(40, 30, cancel.Token));
    }

    [Fact]
    public void LargerMaskHonorsTheImagePixelLimit()
    {
        byte[] pdf = Page(3, 5, 7, 11);
        Image image = RenderTests.Load(pdf, new PdfRenderOptions { Dpi = 72, Limits = new PdfRenderLimits { MaxImagePixels = 20 } });
        Assert.All(image.ToArray<Rgba32>(), p => Assert.Equal(new Rgba32(255, 255, 255, 255), p));
    }

    private static byte[] Pair(string samples, string alpha, string colorFlag, string maskFlag, string matte = "") =>
        TestPdf.Page("q 210 0 0 198 15 12 cm /Im Do Q", "/XObject << /Im 5 0 R >>", 240, 222,
        [RegionTests.Obj($"/Type /XObject /Subtype /Image /Width 2 /Height 1 /ColorSpace /DeviceRGB /BitsPerComponent 8 /Interpolate {colorFlag} /SMask 6 0 R /Filter /ASCIIHexDecode", samples + ">"),
         RegionTests.Obj($"/Type /XObject /Subtype /Image /Width 2 /Height 1 /ColorSpace /DeviceGray /BitsPerComponent 8 /Interpolate {maskFlag} {matte} /Filter /ASCIIHexDecode", alpha + ">")]);

    [Fact]
    public void CoincidentInterpolatedSamplesKeepPremultipliedColorAndMatteEquivalence()
    {
        // This is an interpolation-policy control, not a claim that every PDF viewer uses the same filter.
        Rgba32[] hidden = Load(Pair("fa05140fe63c", "00ff", "true", "true")).ToArray<Rgba32>();
        for (int x = 70; x < 170; x++)
        {
            Rgba32 p = hidden[111 * 240 + x];
            double alpha = (x + .5 - 67.5) / 105;
            Assert.InRange((double)p.R, 255 - 240 * alpha - 1, 255 - 240 * alpha + 1);
        }

        foreach (string flag in new[] { "false", "true" })
        foreach (string maskFlag in new[] { "false", "true" })
        {
            // Exact white-matte preblend at alpha 85: black -> 170, green -> (170,255,170).
            Equal(Load(Pair("00000000ff00", "5555", flag, maskFlag)).ToArray<Rgba32>(),
                Load(Pair("aaaaaaaaffaa", "5555", flag, maskFlag, "/Matte [1 1 1]")).ToArray<Rgba32>());
        }
    }

    [Theory]
    [InlineData("false", "true")]
    [InlineData("true", "false")]
    public void DifferentFlagsKeepHiddenColorAndOpacitySamplingIndependent(string colorFlag, string maskFlag)
    {
        Rgba32[] pixels = Load(Pair("fa05140fe63c", "00ff", colorFlag, maskFlag)).ToArray<Rgba32>();
        for (int x = 70; x < 170; x++)
        {
            double t = (x + .5 - 67.5) / 105;
            double alpha = maskFlag == "true" ? t : x < 120 ? 0 : 1;
            double color = colorFlag == "true" ? 250 - 235 * t : x < 120 ? 250 : 15;
            double expected = color * alpha + 255 * (1 - alpha);
            Assert.InRange((double)pixels[111 * 240 + x].R, expected - 1, expected + 1);
        }
    }

    [Fact]
    public void MaskReductionParticipatesInTheCacheKeyAndConcurrentReads()
    {
        byte[] pdf = Page(3, 1, 317, 1);
        using PdfDocument doc = PdfDocument.Open(pdf);
        PdfImageData data = PdfImageData.FromXObject(doc, (PdfStream)doc.GetObject(5)!)!;
        var page = new PageRender(doc.Pages[0], new PdfRenderOptions());
        Raster first = page.GetRaster(data, 200, 1, CancellationToken.None)!;
        Raster second = page.GetRaster(data, 210, 1, CancellationToken.None)!;
        Assert.Equal(first.Width, second.Width);
        Assert.Equal(200, first.Mask!.Width);
        Assert.Equal(210, second.Mask!.Width);
        Assert.Same(first, page.GetRaster(data, 200, 1, CancellationToken.None));
        Image shared = Load(pdf);
        Rgba32[] expected = Load(pdf).ToArray<Rgba32>(maxDegree: 1);
        Parallel.For(0, 12, new ParallelOptions { MaxDegreeOfParallelism = 4 }, i =>
        {
            var region = new ImageRect(5 + i * 3, 7 + i * 2, 129, 129);
            var part = new Rgba32[region.Width * region.Height];
            shared.CopyPixelsTo<Rgba32>(part, region);
            for (int y = 0; y < region.Height; y++)
                Assert.True(part.AsSpan(y * region.Width, region.Width).SequenceEqual(expected.AsSpan((region.Y + y) * 240 + region.X, region.Width)));
        });
    }

}
