// SPDX-License-Identifier: MIT

using OneImage.Pdf.Render;

namespace OneImage.Pdf.Tests;

/// <summary>Original numeric controls distinguish PDF-painted content from the viewer's display background.</summary>
public class PageBackgroundTests
{
    public static IEnumerable<object[]> Modes()
    {
        foreach (string mode in new[] { "Normal", "Multiply", "Screen", "Overlay", "Darken", "Lighten", "ColorDodge", "ColorBurn", "HardLight", "SoftLight", "Difference", "Exclusion", "Hue", "Saturation", "Color", "Luminosity" })
        {
            yield return [mode];
        }
    }

    [Theory]
    [MemberData(nameof(Modes))]
    public void EmptyPageBackdropDoesNotBlendWithViewerWhite(string mode)
    {
        byte[] pdf = TestPdf.Page("/B gs .2 .4 .6 rg 20 20 80 60 re f", $"/ExtGState << /B << /BM /{mode} >> >>", 160, 120);
        Rgba32[] result = Pixels(pdf, new Rgba32(255, 255, 255, 255));
        Assert.Equal(new Rgba32(51, 102, 153, 255), result[(60 * 160) + 60]);
        Assert.Equal(new Rgba32(255, 255, 255, 255), result[0]);
    }

    [Theory]
    [InlineData("Screen", 255)]
    [InlineData("ColorDodge", 255)]
    [InlineData("Multiply", 0)]
    [InlineData("Normal", 0)]
    public void ExplicitPdfWhiteStillParticipatesInBlend(string mode, byte expected)
    {
        byte[] pdf = TestPdf.Page("1 g 0 0 160 120 re f /B gs 0 g 20 20 80 60 re f", $"/ExtGState << /B << /BM /{mode} >> >>", 160, 120);
        Rgba32[] result = Pixels(pdf, new Rgba32(255, 255, 255, 255));
        Assert.Equal(new Rgba32(expected, expected, expected, 255), result[(60 * 160) + 60]);
    }

    [Theory]
    [InlineData(0)]
    [InlineData(128)]
    [InlineData(255)]
    public void ViewerBackgroundCompositesBehindCompletedPage(int backdropAlpha)
    {
        byte[] pdf = TestPdf.Page("/B gs .2 .4 .6 rg 20 20 80 60 re f", "/ExtGState << /B << /BM /Screen /ca .5 >> >>", 160, 120);
        var background = new Rgba32(204, 102, 51, (byte)backdropAlpha);
        Rgba32[] transparent = Pixels(pdf, default), displayed = Pixels(pdf, background);
        // Independently compute normal source-over of the quantized page pixels onto the display background.
        Rgba32 source = transparent[(60 * 160) + 60];
        Assert.Equal(new Rgba32(51, 102, 153, 128), source);
        double sa = source.A / 255.0, ba = background.A / 255.0, a = sa + ba * (1 - sa);
        double[] expected = [
            (source.R * sa + background.R * ba * (1 - sa)) / a,
            (source.G * sa + background.G * ba * (1 - sa)) / a,
            (source.B * sa + background.B * ba * (1 - sa)) / a,
            a * 255,
        ];
        Rgba32 actual = displayed[(60 * 160) + 60];
        byte[] channels = [actual.R, actual.G, actual.B, actual.A];
        for (int c = 0; c < 4; c++) Assert.InRange(Math.Abs(channels[c] - expected[c]), 0, 1);
        Assert.Equal(background.A == 0 ? default : background, displayed[0]);
    }

    public static IEnumerable<object[]> GroupCases()
    {
        foreach (bool isolated in new[] { false, true })
        foreach (string mask in new[] { "None", "Alpha", "Luminosity" })
        foreach (int alpha in new[] { 0, 128, 255 })
            yield return [isolated, mask, alpha];
    }

    [Theory]
    [MemberData(nameof(GroupCases))]
    public void GroupAndMaskFinishBeforeDisplayBackground(bool isolated, string mask, int backgroundAlpha)
    {
        string group = RegionTests.Obj($"/Type /XObject /Subtype /Form /BBox [0 0 160 120] /Group << /S /Transparency /I {isolated.ToString().ToLowerInvariant()} >> /Resources << /ExtGState << /C << /ca .5 /BM /ColorDodge >> >> >>",
            "/C gs .2 .4 .6 rg 20 20 80 60 re f");
        string maskForm = RegionTests.Obj("/Type /XObject /Subtype /Form /BBox [0 0 160 120] /Group << /S /Transparency /I true /CS /DeviceGray >> /Resources << /ExtGState << /H << /ca .5 >> >> >>",
            mask == "Alpha" ? "/H gs 1 g 0 0 80 120 re f" : ".5 g 0 0 80 120 re f");
        string maskEntry = mask == "None" ? "" : $"/SMask << /S /{mask} /G 6 0 R >>";
        byte[] pdf = TestPdf.Page("/G gs /F Do", $"/XObject << /F 5 0 R >> /ExtGState << /G << /ca .5 /BM /Screen {maskEntry} >> >>", 160, 120, [group, maskForm]);
        var background = new Rgba32(204, 102, 51, (byte)backgroundAlpha);
        Rgba32[] pixels = Pixels(pdf, background);
        // On an empty page both blend modes leave the source color alone. The group contributes
        // child alpha times outer alpha, times the half-strength mask when one is present.
        double alpha = mask == "None" ? .25 : .125;
        AssertOver(pixels[(60 * 160) + 60], [.2, .4, .6], alpha, background);
        Assert.Equal(backgroundAlpha == 0 ? default : background, pixels[0]);
        if (mask != "None") Assert.Equal(backgroundAlpha == 0 ? default : background, pixels[(60 * 160) + 90]);
    }

    public static IEnumerable<object[]> PaintedBackdropCases()
    {
        foreach (string mode in new[] { "Normal", "Multiply", "Screen" })
        foreach (int alpha in new[] { 0, 128, 255 })
            yield return [mode, alpha];
    }

    [Theory]
    [MemberData(nameof(PaintedBackdropCases))]
    public void TranslucentPdfBackdropBlendsBeforeDisplayBackground(string mode, int backgroundAlpha)
    {
        byte[] pdf = TestPdf.Page("q /H gs .6 .2 .8 rg 0 0 160 120 re f Q /B gs .2 .4 .6 rg 20 20 80 60 re f",
            $"/ExtGState << /H << /ca .5 >> /B << /ca .5 /BM /{mode} >> >>", 160, 120);
        var background = new Rgba32(153, 204, 51, (byte)backgroundAlpha);
        double[] backdrop = [.6, .2, .8], source = [.2, .4, .6], color = new double[3];
        for (int c = 0; c < color.Length; c++)
        {
            double blend = mode switch
            {
                "Multiply" => backdrop[c] * source[c],
                "Screen" => backdrop[c] + source[c] - backdrop[c] * source[c],
                _ => source[c],
            };
            // PDF source-over blending on a half-alpha PDF backdrop, before any display color.
            color[c] = (.25 * backdrop[c] + .25 * source[c] + .25 * blend) / .75;
        }

        Rgba32[] pixels = Pixels(pdf, background);
        AssertOver(pixels[(60 * 160) + 60], color, .75, background);
        AssertOver(pixels[0], backdrop, .5, background);
    }

    [Theory]
    [InlineData(0)]
    [InlineData(128)]
    [InlineData(255)]
    public void EmptyPageAndFinalPdfClipDoNotClipDisplayBackground(int alpha)
    {
        var background = new Rgba32(137, 83, 211, (byte)alpha);
        Rgba32 expected = alpha == 0 ? default : background;
        foreach (string content in new[] { "", "40 40 10 10 re W n" })
            Assert.All(Pixels(TestPdf.Page(content, width: 160, height: 120), background), p => Assert.Equal(expected, p));
    }

    [Fact]
    public void FractionalEdgeUsesQuantizedPageAlpha()
    {
        byte[] pdf = TestPdf.Page("0 g 20.5 20 80 60 re f", width: 160, height: 120);
        Assert.Equal(new Rgba32(0, 0, 0, 128), Pixels(pdf, default)[(60 * 160) + 20]);
        Assert.Equal(new Rgba32(127, 127, 127, 255), Pixels(pdf, new Rgba32(255, 255, 255, 255))[(60 * 160) + 20]);
    }

    [Theory]
    [InlineData(0)]
    [InlineData(1)]
    [InlineData(127)]
    [InlineData(128)]
    [InlineData(254)]
    [InlineData(255)]
    public void OutputCompositionMatchesCanvasForEveryPageAlphaAndChannel(int backgroundAlpha)
    {
        var input = new Rgba32[256 * 256];
        for (int alpha = 0; alpha < 256; alpha++)
        for (int value = 0; value < 256; value++)
            input[(alpha * 256) + value] = new Rgba32((byte)value, (byte)(255 - value), (byte)((value * 73) % 256), (byte)alpha);
        foreach (Rgba32 color in new Rgba32[]
        {
            new(0, 0, 0, (byte)backgroundAlpha), new(255, 255, 255, (byte)backgroundAlpha),
            new(204, 102, 51, (byte)backgroundAlpha), new(137, 83, 211, (byte)backgroundAlpha),
            new(1, 127, 254, (byte)backgroundAlpha), new(254, 128, 1, (byte)backgroundAlpha),
        })
        {
            using var reference = new Canvas(256, 256, PixelFormat.Rgba8);
            var bounds = new ImageRect(0, 0, 256, 256);
            reference.CopyFrom<Rgba32>(input, bounds);
            // A transparent display background deliberately skips composition, including hidden RGB.
            if (color.A != 0) reference.Fill(color, composition: AlphaComposition.DestOver);
            var expected = new Rgba32[input.Length];
            reference.CopyTo<Rgba32>(expected, bounds);
            Rgba32[] actual = (Rgba32[])input.Clone();
            CellRenderer.CompositeDisplayBackground(actual, color);
            Assert.Equal(expected, actual);
        }
    }

    [Fact]
    public void OutputCompositionMatchesCanvasForRandomTranslucentColors()
    {
        const int width = 73, height = 61;
        var random = new Random(0x5A17C03);
        var bytes = new byte[width * height * 4];
        var backgroundBytes = new byte[4];
        var bounds = new ImageRect(0, 0, width, height);
        for (int trial = 0; trial < 64; trial++)
        {
            random.NextBytes(bytes);
            random.NextBytes(backgroundBytes);
            Rgba32[] input = System.Runtime.InteropServices.MemoryMarshal.Cast<byte, Rgba32>(bytes).ToArray();
            var background = new Rgba32(backgroundBytes[0], backgroundBytes[1], backgroundBytes[2], backgroundBytes[3]);
            using var reference = new Canvas(width, height, PixelFormat.Rgba8);
            reference.CopyFrom<Rgba32>(input, bounds);
            if (background.A != 0) reference.Fill(background, composition: AlphaComposition.DestOver);
            var expected = new Rgba32[input.Length];
            reference.CopyTo<Rgba32>(expected, bounds);
            CellRenderer.CompositeDisplayBackground(input, background);
            Assert.Equal(expected, input);
        }
    }

    [Fact]
    public void OpaqueDisplayBackgroundAlwaysProducesUnitAlpha()
    {
        for (int value = 1; value < 255; value++)
        {
            float pageAlpha = value / 255f;
            Assert.Equal(1f, (1f * (1f + (-1f * pageAlpha))) + pageAlpha);
        }
    }

    [Theory]
    [InlineData(0)]
    [InlineData(1)]
    [InlineData(128)]
    [InlineData(255)]
    public void EmptyAndOpaqueLaneCombinationsMatchCanvas(int backgroundAlpha)
    {
        var background = new Rgba32(151, 33, 219, (byte)backgroundAlpha);
        var bounds = new ImageRect(0, 0, 33, 1);
        var input = new Rgba32[33];
        for (int bits = 0; bits < 256; bits++)
        {
            for (int i = 0; i < input.Length; i++)
                input[i] = new Rgba32((byte)(i * 7), (byte)bits, (byte)(255 - i), (bits & (1 << (i % 8))) == 0 ? (byte)0 : (byte)255);
            using var reference = new Canvas(33, 1, PixelFormat.Rgba8);
            reference.CopyFrom<Rgba32>(input, bounds);
            if (background.A != 0) reference.Fill(background, composition: AlphaComposition.DestOver);
            var expected = new Rgba32[input.Length];
            reference.CopyTo<Rgba32>(expected, bounds);
            CellRenderer.CompositeDisplayBackground(input, background);
            Assert.Equal(expected, input);
        }

        CellRenderer.CompositeDisplayBackground(Span<Rgba32>.Empty, background);
    }

    [Fact]
    public void ViewerBackgroundDoesNotAffectRegionOrThreadDeterminism()
    {
        byte[] pdf = TestPdf.Page("/B gs .2 .4 .6 rg 17.5 9.25 245.75 260.5 re f", "/ExtGState << /B << /BM /Screen /ca .5 >> >>", 290, 280);
        var background = new Rgba32(173, 91, 37, 128);
        Image page = RenderTests.Load(pdf, new PdfRenderOptions { Dpi = 72, Background = background });
        Rgba32[] serial = page.ToArray<Rgba32>(maxDegree: 1);
        Assert.Equal(serial, Pixels(pdf, background, 4));
        var region = new ImageRect(119, 121, 140, 140);
        var part = new Rgba32[region.Width * region.Height];
        Image fresh = RenderTests.Load(pdf, new PdfRenderOptions { Dpi = 72, Background = background });
        fresh.CopyPixelsTo<Rgba32>(part, region, maxDegree: 4);
        for (int y = 0; y < region.Height; y++)
        for (int x = 0; x < region.Width; x++)
            Assert.Equal(serial[((y + region.Y) * 290) + x + region.X], part[(y * region.Width) + x]);
    }

    private static Rgba32[] Pixels(byte[] pdf, Rgba32 background, int degree = 1) =>
        RenderTests.Load(pdf, new PdfRenderOptions { Dpi = 72, Background = background }).ToArray<Rgba32>(maxDegree: degree);

    private static void AssertOver(Rgba32 actual, double[] color, double sourceAlpha, Rgba32 background)
    {
        double ba = background.A / 255.0, alpha = sourceAlpha + ba * (1 - sourceAlpha);
        double[] back = [background.R / 255.0, background.G / 255.0, background.B / 255.0];
        byte[] channels = [actual.R, actual.G, actual.B];
        for (int c = 0; c < channels.Length; c++)
        {
            double expected = 255 * (color[c] * sourceAlpha + back[c] * ba * (1 - sourceAlpha)) / alpha;
            Assert.InRange(Math.Abs(channels[c] - expected), 0, 2);
        }

        Assert.InRange(Math.Abs(actual.A - 255 * alpha), 0, 2);
    }
}
