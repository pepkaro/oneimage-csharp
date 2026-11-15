// SPDX-License-Identifier: MIT
// Original geometric PDF reductions; no external documents, fonts, images or artwork.
using System.Globalization;

namespace OneImage.Pdf.Tests;

public class PatternBackdropTests
{
    private const string Paint = "/Pattern cs /P scn 0 0 96 96 re f";
    private const string Source = ".8 .4 .2 rg 0 0 24 24 re f";
    private static readonly Rgba32 Backdrop = new(51, 153, 204, 255);

    [Theory]
    [InlineData("Normal")]
    [InlineData("Multiply")]
    [InlineData("Screen")]
    public void InternalBlendUsesTheBackdropAtEveryCopy(string mode)
    {
        string cell = $"/A gs {Source}";
        byte[] pdf = Pdf(cell, $"/ExtGState << /A << /BM /{mode} >> >>",
            ".2 .6 .8 rg 0 0 48 96 re f .6 .2 .4 rg 48 0 48 96 re f " + Paint);
        Rgba32[] pixels = Pixels(pdf);
        double[] source = [.8, .4, .2];
        foreach (int x in new[] { 12, 36, 60, 84 })
        {
            double[] background = x < 48 ? [.2, .6, .8] : [.6, .2, .4];
            Near(At(pixels, x, 12), Enumerable.Range(0, 3).Select(c => 255 * Blend(mode, background[c], source[c])).Append(255).ToArray());
        }
    }

    [Theory]
    [InlineData(0)]
    [InlineData(128)]
    [InlineData(255)]
    public void InternalAndOuterAlphaUseNonIsolatedEquations(int backgroundAlpha)
    {
        double ab = backgroundAlpha / 255.0;
        double[] cb = [.2, .6, .8], cs = [.8, .4, .2];
        foreach (string outside in new[] { "Normal", "Multiply", "Screen" })
        {
            byte[] pdf = Pdf("/A gs " + Source, "/ExtGState << /A << /ca .5 /BM /Multiply >> >>", "/O gs " + Paint,
                $"/ExtGState << /O << /ca .5 /BM /{outside} >> >>");
            Rgba32 actual = At(Pixels(pdf, new Rgba32(51, 153, 204, (byte)backgroundAlpha)), 12, 12);
            const double a = .25;
            double ar = a + (ab * (1 - a));
            var expected = new double[4];
            expected[3] = ar * 255;
            for (int c = 0; c < 3; c++)
            {
                double group = ((1 - ab) * cs[c]) + (ab * cb[c] * cs[c]);
                double blended = ((1 - ab) * group) + (ab * Blend(outside, cb[c], group));
                expected[c] = 255 * (((1 - a) * ab * cb[c]) + (a * blended)) / ar;
            }
            Near(actual, expected);
        }
    }

    [Fact]
    public void MultipleCellObjectsBlendInOrderBeforeOuterOpacity()
    {
        // The overlapping right half is not equivalent to moving either internal blend to the outer paint.
        string cell = "/A gs .8 .4 .2 rg 0 0 24 24 re f /B gs .1 .8 .3 rg 12 0 12 24 re f";
        string resources = "/ExtGState << /A << /BM /Multiply /ca .5 >> /B << /BM /Screen /ca .5 >> >>";
        byte[] pdf = Pdf(cell, resources, "/O gs " + Paint, "/ExtGState << /O << /ca .5 >> >>");
        Rgba32[] pixels = Pixels(pdf, Backdrop);
        double[] cb = [.2, .6, .8], a = [.8, .4, .2], b = [.1, .8, .3];
        foreach (int x in new[] { 6, 18, 30, 42 })
        {
            bool overlap = x % 24 >= 12;
            var expected = new double[4];
            expected[3] = 255;
            for (int c = 0; c < 3; c++)
            {
                double result = .5 * cb[c] + .5 * cb[c] * a[c];
                if (overlap) result = .5 * result + .5 * Blend("Screen", result, b[c]);
                expected[c] = 255 * (.5 * cb[c] + .5 * result);
            }
            Near(At(pixels, x, 12), expected);
        }
    }

    [Fact]
    public void OverlappingCopiesShareOneGroupAndApplyOuterOpacityOnce()
    {
        // ISO 8.7.3.1 leaves tile-instance order unspecified. These two identical Multiply
        // operations commute, so the oracle does not depend on a particular tile order.
        string cell = "/A gs " + Source;
        byte[] pdf = Pdf(cell, "/ExtGState << /A << /BM /Multiply /ca .5 >> >>", "/O gs " + Paint,
            "/ExtGState << /O << /ca .5 >> >>", xStep: 12);
        Rgba32[] pixels = Pixels(pdf, Backdrop);
        double[] cb = [.2, .6, .8], cs = [.8, .4, .2];
        double[] expected = Enumerable.Range(0, 3).Select(c => 255 * cb[c] * (.5 + .5 * Math.Pow(.5 + .5 * cs[c], 2))).Append(255).ToArray();
        Near(At(pixels, 18, 12), expected);
    }

    [Theory]
    [InlineData(false)]
    [InlineData(true)]
    public void OuterMaskStencilAndClipAreAppliedAfterCellBlending(bool stencil)
    {
        const string mask = "/Type /XObject /Subtype /Form /BBox [0 0 96 96] /Group << /S /Transparency /I true >> /Resources << /ExtGState << /H << /ca .5 >> >> >>";
        string paint = stencil ? "/Pattern cs /P scn q 96 0 0 96 0 0 cm BI /W 2 /H 1 /IM true /BPC 1 /F /AHx ID 40> EI Q" : Paint;
        byte[] pdf = Pdf("/A gs " + Source, "/ExtGState << /A << /BM /Multiply >> >>",
            "8 8 80 80 re W n /O gs " + paint,
            "/ExtGState << /O << /ca .5 /SMask << /S /Alpha /G 6 0 R >> >> >>",
            extra: [RegionTests.Obj(mask, "/H gs 1 g 0 0 96 48 re f")]);
        Rgba32[] pixels = Pixels(pdf, Backdrop);
        Near(At(pixels, 12, 12), [48.45, 130.05, 163.2, 255]);
        Assert.Equal(Backdrop, At(pixels, 4, 12));
        Assert.Equal(Backdrop, At(pixels, 12, 72));
        if (stencil) Assert.Equal(Backdrop, At(pixels, 72, 12));
    }

    [Theory]
    [InlineData("1 0 0 1 0 0")]
    [InlineData("0 1 -1 0 96 0")]
    [InlineData("-1 0 0 1 96 0")]
    [InlineData("1 .25 .5 1 -24 -12")]
    public void MatrixCopiesMatchExplicitNonIsolatedGroup(string matrix)
    {
        const string cell = "/A gs .8 .4 .2 rg 4 4 12 12 re f /B gs .2 .8 .3 rg 10 8 10 12 re f";
        const string resources = "/ExtGState << /A << /BM /Multiply /ca .5 >> /B << /BM /Screen /ca .5 >> >>";
        byte[] pattern = Pdf(cell, resources, "/O gs " + Paint, "/ExtGState << /O << /ca .5 >> >>", matrix: matrix);
        var copies = new System.Text.StringBuilder();
        for (int y = -10; y <= 10; y++)
        for (int x = -10; x <= 10; x++)
            copies.Append(CultureInfo.InvariantCulture, $"q 1 0 0 1 {24 * x} {24 * y} cm {cell} Q ");
        string form = RegionTests.Obj($"/Type /XObject /Subtype /Form /BBox [-1000 -1000 1000 1000] /Group << /S /Transparency /I false >> /Resources << {resources} >>", copies.ToString());
        byte[] direct = TestPdf.Page($"0 0 96 96 re W n /O gs {matrix} cm /F Do", "/XObject << /F 5 0 R >> /ExtGState << /O << /ca .5 >> >>", 96, 96, [form]);
        Rgba32[] actual = Pixels(pattern, Backdrop), expected = Pixels(direct, Backdrop);
        Assert.Equal(expected, actual);
    }

    [Fact]
    public void NestedPatternsAndGroupsRetainCoverage()
    {
        string child = RegionTests.Obj("/Type /Pattern /PatternType 1 /PaintType 1 /TilingType 1 /BBox [0 0 24 24] /XStep 24 /YStep 24 /Resources << /ExtGState << /A << /BM /Multiply >> >> >>", "/A gs " + Source);
        byte[] pdf = Pdf("/Pattern cs /C scn 0 0 24 24 re f", "/Pattern << /C 6 0 R >>", "/G gs /F Do", "/XObject << /F 7 0 R >> /ExtGState << /G << /ca .5 >> >>",
            extra: [child, RegionTests.Obj("/Type /XObject /Subtype /Form /BBox [0 0 96 96] /Group << /S /Transparency /I false >> /Resources << /Pattern << /P 5 0 R >> >>", Paint)]);
        Near(At(Pixels(pdf, Backdrop), 12, 12), [45.9, 107.1, 122.4, 255]);
    }

    [Fact]
    public void UncoloredPatternUsesTheCurrentTintWithItsInternalBlend()
    {
        string pattern = RegionTests.Obj("/Type /Pattern /PatternType 1 /PaintType 2 /TilingType 1 /BBox [0 0 24 24] /XStep 24 /YStep 24 /Resources << /ExtGState << /A << /BM /Multiply >> >> >>", "/A gs 0 0 24 24 re f");
        byte[] pdf = TestPdf.Page("/Tint cs .8 .4 .2 /P scn 0 0 48 96 re f .4 .8 .6 /P scn 48 0 48 96 re f",
            "/ColorSpace << /Tint [/Pattern /DeviceRGB] >> /Pattern << /P 5 0 R >>", 96, 96, [pattern]);
        Rgba32[] pixels = Pixels(pdf, Backdrop);
        Near(At(pixels, 12, 12), [40.8, 61.2, 40.8, 255]);
        Near(At(pixels, 60, 12), [20.4, 122.4, 122.4, 255]);
    }

    [Fact]
    public void RepeatedPaintingDoesNotReuseAStaleBackdrop()
    {
        byte[] pdf = Pdf("/A gs " + Source, "/ExtGState << /A << /BM /Multiply >> >>", Paint + " " + Paint);
        Near(At(Pixels(pdf, Backdrop), 12, 12), [32.64, 24.48, 8.16, 255]);
    }

    [Fact]
    public void RegionsAndConcurrentReadsMatchAcrossRenderCells()
    {
        byte[] pdf = Pdf("/A gs .8 .4 .2 rg 4 4 12 12 re f", "/ExtGState << /A << /BM /Multiply /ca .5 >> >>", matrix: "1 .25 .5 1 0 0");
        var options = new PdfRenderOptions { Dpi = 216, Background = Backdrop };
        Image image = RenderTests.Load(pdf, options);
        Rgba32[] whole = image.ToArray<Rgba32>(maxDegree: 1);
        Assert.Equal(whole, RenderTests.Load(pdf, options).ToArray<Rgba32>(maxDegree: 4));
        Parallel.For(0, 8, i =>
        {
            var region = new ImageRect(117 + i, 118 - i, 40, 45);
            var part = new Rgba32[region.Width * region.Height];
            RenderTests.Load(pdf, options).CopyPixelsTo<Rgba32>(part, region);
            for (int y = 0; y < region.Height; y++)
                Assert.True(part.AsSpan(y * region.Width, region.Width).SequenceEqual(whole.AsSpan(((region.Y + y) * image.Width) + region.X, region.Width)));
        });
    }

    [Fact]
    public void ExcessiveBackdropDependentCopiesFailBeforeReplay()
    {
        byte[] pdf = Pdf("/A gs " + Source, "/ExtGState << /A << /BM /Multiply >> >>", xStep: .000001);
        Assert.Throws<ImageLimitException>(() => Pixels(pdf));
    }

    [Fact]
    public void NegativeStepsProduceTheSameGrid()
    {
        const string resources = "/ExtGState << /A << /BM /Multiply >> >>";
        byte[] positive = Pdf("/A gs " + Source, resources);
        string pattern = RegionTests.Obj("/Type /Pattern /PatternType 1 /PaintType 1 /TilingType 1 /BBox [0 0 24 24] /XStep -24 /YStep -24 /Resources << " + resources + " >>", "/A gs " + Source);
        byte[] negative = TestPdf.Page(Paint, "/Pattern << /P 5 0 R >>", 96, 96, [pattern]);
        Assert.Equal(Pixels(positive, Backdrop), Pixels(negative, Backdrop));
    }

    [Fact]
    public void ArbitraryClipGeometryRestrictsTheFinalPatternObject()
    {
        byte[] pdf = Pdf("/A gs " + Source, "/ExtGState << /A << /BM /Multiply >> >>",
            "8 8 m 88 8 l 8 88 l h W n " + Paint);
        Rgba32[] pixels = Pixels(pdf, Backdrop);
        Near(At(pixels, 12, 12), [40.8, 61.2, 40.8, 255]);
        Assert.Equal(Backdrop, At(pixels, 72, 72));
        Assert.Equal(Backdrop, At(pixels, 4, 12));
    }

    [Theory]
    [InlineData(false, 128)]
    [InlineData(false, 255)]
    [InlineData(true, 128)]
    [InlineData(true, 255)]
    public void KnockoutParentMatchesAnEquivalentNormalOnlyCell(bool isolated, int backgroundAlpha)
    {
        const string resources = "/ExtGState << /A << /BM /Multiply /ca .5 >> /B << /BM /Screen /ca .5 >> >>";
        const string body = "/A gs .8 .4 .2 rg 0 0 24 24 re f /B gs .1 .8 .3 rg 12 0 12 24 re f";
        // The renderer currently treats all knockout groups as isolated. Preserve that existing limitation:
        // derive the cell on transparent black, then replace it with disjoint Normal objects of equal RGBA.
        double[] first = [.8, .4, .2], second = [.1, .8, .3];
        string[] components = Enumerable.Range(0, 3).Select(c =>
            ((.25 * first[c] + .25 * second[c] + .25 * Blend("Screen", first[c], second[c])) / .75)
            .ToString("0.#################", CultureInfo.InvariantCulture)).ToArray();
        string equivalent = "/A gs .8 .4 .2 rg 0 0 12 24 re f /B gs " + string.Join(" ", components) + " rg 12 0 12 24 re f";
        const string normalResources = "/ExtGState << /A << /ca .5 >> /B << /ca .75 >> >>";
        string parent = RegionTests.Obj($"/Type /XObject /Subtype /Form /BBox [0 0 96 96] /Group << /S /Transparency /K true /I {isolated.ToString().ToLowerInvariant()} >> /Resources << /Pattern << /P 5 0 R >> /ExtGState << /H << /ca .5 >> >> >>", "0 1 0 rg 0 0 96 96 re f /H gs " + Paint);
        const string pageResources = "/XObject << /F 6 0 R >> /ExtGState << /G << /ca .5 >> >>";
        byte[] actualPdf = Pdf(body, resources, "/G gs /F Do", pageResources, extra: [parent]);
        byte[] normalPdf = Pdf(equivalent, normalResources, "/G gs /F Do", pageResources, extra: [parent]);
        var backdrop = new Rgba32(51, 153, 204, (byte)backgroundAlpha);
        Rgba32[] actual = Pixels(actualPdf, backdrop), expected = Pixels(normalPdf, backdrop);
        for (int y = 0; y < 96; y++)
        for (int x = 0; x < 96; x++)
        {
            Rgba32 e = At(expected, x, y);
            Near(At(actual, x, y), [e.R, e.G, e.B, e.A]);
        }
    }

    [Fact]
    public void ConservativeIsolatedGroupDetectionDoesNotIntroduceBackdropDependence()
    {
        string form = RegionTests.Obj("/Type /XObject /Subtype /Form /BBox [0 0 24 24] /Group << /S /Transparency /I true >> /Resources << /ExtGState << /A << /BM /Multiply >> >> >>", "/A gs " + Source);
        byte[] actual = Pdf("/F Do", "/XObject << /F 6 0 R >>", extra: [form]);
        byte[] normal = Pdf(Source, "");
        Assert.Equal(Pixels(normal, Backdrop), Pixels(actual, Backdrop));
    }

    private static byte[] Pdf(string cell, string cellResources, string content = Paint, string pageResources = "", string matrix = "1 0 0 1 0 0", double xStep = 24, string[]? extra = null)
    {
        string pattern = RegionTests.Obj($"/Type /Pattern /PatternType 1 /PaintType 1 /TilingType 1 /BBox [0 0 24 24] /XStep {xStep.ToString("0.#################", CultureInfo.InvariantCulture)} /YStep 24 /Matrix [{matrix}] /Resources << {cellResources} >>", cell);
        return TestPdf.Page(content, "/Pattern << /P 5 0 R >> " + pageResources, 96, 96, [pattern, ..extra ?? []]);
    }
    private static Rgba32[] Pixels(byte[] pdf, Rgba32 background = default) => RenderTests.Load(pdf, new PdfRenderOptions { Dpi = 72, Background = background }).ToArray<Rgba32>(maxDegree: 1);
    private static Rgba32 At(Rgba32[] pixels, int x, int y) => pixels[((95 - y) * 96) + x];
    private static double Blend(string mode, double cb, double cs) => mode switch { "Multiply" => cb * cs, "Screen" => cb + cs - cb * cs, _ => cs };
    private static void Near(Rgba32 pixel, double[] expected)
    {
        byte[] actual = [pixel.R, pixel.G, pixel.B, pixel.A];
        for (int i = 0; i < 4; i++) Assert.True(Math.Abs(actual[i] - expected[i]) <= 2, $"channel {i}: {actual[i]}, expected {expected[i]:F3}");
    }
}
