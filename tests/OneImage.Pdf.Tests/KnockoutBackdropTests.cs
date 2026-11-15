// SPDX-License-Identifier: MIT
// Original geometric PDF programs, with independent ISO 32000-1 11.4.6/11.4.8 equations.
using System.Globalization;
using static OneImage.Pdf.Tests.SpecTruth.Spec;

namespace OneImage.Pdf.Tests;

public class KnockoutBackdropTests
{
    private const int Size = 32;
    private const string Bounds = "/Type /XObject /Subtype /Form /BBox [0 0 32 32]";
    private const string Paint = ".8 .4 .2 rg 4 4 24 24 re f";
    private static readonly double[] Back = [.2, .6, .8, 1];
    private static readonly double[] Source = [.8, .4, .2, 1];
    private static readonly double[] Second = [.1, .8, .3, 1];

    public static TheoryData<bool, bool, int, double, string> SingleCases
    {
        get
        {
            var cases = new TheoryData<bool, bool, int, double, string>();
            foreach (bool isolated in new[] { false, true })
            foreach (bool knockout in new[] { false, true })
            foreach (int backdropAlpha in new[] { 0, 128, 255 })
            foreach (double alpha in new[] { 0.0, .25, 1.0 })
            foreach (string blend in new[] { "Normal", "Multiply", "Screen" })
                cases.Add(isolated, knockout, backdropAlpha, alpha, blend);
            return cases;
        }
    }

    [Theory]
    [MemberData(nameof(SingleCases))]
    public void SingleElementUsesInitialBackdrop(bool isolated, bool knockout, int backdropAlpha, double alpha, string mode)
    {
        byte[] pdf = GroupPdf(isolated, knockout, "/A gs " + Paint,
            $"/ExtGState << /A << /ca {N(alpha)} /BM /{mode} >> >>", "/O gs /F Do",
            "/ExtGState << /O << /ca .5 >> >>", backdropAlpha);
        double[] background = [.2, .6, .8, backdropAlpha / 255.0];
        double[] initial = isolated ? [0, 0, 0, 0] : background;
        double[] result = Over(initial, Source, alpha, mode);
        double[] group = Recover(result, initial, alpha);
        Near(At(Pixels(pdf), 12, 12), Over(background, group, alpha * .5, "Normal"));
    }

    [Theory]
    [InlineData(false, false)]
    [InlineData(false, true)]
    [InlineData(true, false)]
    [InlineData(true, true)]
    public void KnockoutAndNonKnockoutOverlapsHaveIndependentShapeAndAlpha(bool isolated, bool knockout)
    {
        foreach (bool ais in new[] { false, true })
        foreach (double secondAlpha in new[] { 0.0, .25, 1.0 })
        foreach (int backdropAlpha in new[] { 0, 128, 255 })
        {
            byte[] pdf = GroupPdf(isolated, knockout,
                "/A gs .8 .4 .2 rg 2 2 20 20 re f /B gs .1 .8 .3 rg 10 10 20 20 re f",
                $"/ExtGState << /A << /ca .5 /BM /Multiply >> /B << /ca {N(secondAlpha)} /BM /Screen /AIS {Bool(ais)} >> >>",
                "/O gs /F Do", "/ExtGState << /O << /ca .5 /BM /Screen >> >>", backdropAlpha);
            double[] background = [.2, .6, .8, backdropAlpha / 255.0];
            double[] initial = isolated ? [0, 0, 0, 0] : background;
            double[] first = Over(initial, Source, .5, "Multiply");
            double shape = ais ? secondAlpha : 1;
            double[] result = knockout ? Mix(first, Over(initial, Second, shape > 0 ? secondAlpha / shape : 0, "Screen"), shape) : Over(first, Second, secondAlpha, "Screen");
            double ag = knockout ? secondAlpha + (.5 * (1 - shape)) : secondAlpha + (.5 * (1 - secondAlpha));
            double[] group = Recover(result, initial, ag);
            Near(At(Pixels(pdf), 14, 14), Over(background, group, ag * .5, "Screen"), 4);
        }
    }

    [Theory]
    [InlineData(false, false)]
    [InlineData(false, true)]
    [InlineData(true, false)]
    [InlineData(true, true)]
    public void NestedGroupsUseParentInitialBackdropAndOwnGeometricShape(bool parentIsolated, bool childIsolated)
    {
        string child = Form(childIsolated, false, "/A gs " + Paint, "/ExtGState << /A << /ca .25 /BM /Multiply >> >>");
        string outer = Form(parentIsolated, true, ".1 .8 .3 rg 0 0 32 32 re f /C Do", "/XObject << /C 6 0 R >>");
        byte[] pdf = BackdropPage("/F Do", "/XObject << /F 5 0 R >>", Size, Size, [outer, child]);
        double[] initial = parentIsolated ? [0, 0, 0, 0] : Back;
        double[] childInitial = childIsolated ? [0, 0, 0, 0] : initial;
        double[] childResult = Over(childInitial, Source, .25, "Multiply");
        double[] childColor = Recover(childResult, childInitial, .25);
        double[] result = Over(initial, childColor, .25, "Normal");
        double[] group = Recover(result, initial, .25);
        Rgba32[] actual = Pixels(pdf);
        Near(At(actual, 12, 12), Over(Back, group, .25, "Normal"));
        Near(At(actual, 1, 1), Second);
    }

    [Theory]
    [InlineData(false)]
    [InlineData(true)]
    public void SoftMaskIsOpacityOrShapeAccordingToAis(bool ais)
    {
        string mask = Stream(Bounds + " /Group << /S /Transparency /I true >>", ".25 g 0 0 32 32 re f");
        string form = Form(false, true, ".1 .8 .3 rg 0 0 32 32 re f /A gs " + Paint,
            $"/ExtGState << /A << /BM /Multiply /AIS {Bool(ais)} /SMask << /S /Luminosity /G 6 0 R >> >> >>");
        byte[] pdf = BackdropPage("/F Do", "/XObject << /F 5 0 R >>", Size, Size, [form, mask]);
        double amount = 64 / 255.0;
        double[] expected = ais ? Mix(Second, Over(Back, Source, 1, "Multiply"), amount) : Over(Back, Source, amount, "Multiply");
        Near(At(Pixels(pdf), 12, 12), expected);
    }

    [Theory]
    [InlineData(false)]
    [InlineData(true)]
    public void MaskedNestedGroupKnocksOutByShapeRatherThanOpacity(bool ais)
    {
        string mask = Stream(Bounds + " /Group << /S /Transparency /I true >>", ".5 g 0 0 32 32 re f");
        string child = Form(false, false, "/A gs " + Paint, "/ExtGState << /A << /ca .25 /BM /Multiply /AIS false >> >>");
        string outer = Form(false, true, ".1 .8 .3 rg 0 0 32 32 re f /A gs /C Do",
            $"/XObject << /C 6 0 R >> /ExtGState << /A << /ca .5 /AIS {Bool(ais)} /SMask << /S /Luminosity /G 7 0 R >> >> >>");
        byte[] pdf = BackdropPage("/F Do", "/XObject << /F 5 0 R >>", Size, Size, [outer, child, mask]);
        double m = .5 * 128 / 255.0;
        double[] multiplied = Over(Back, Source, 1, "Multiply");
        double[] expected = ais ? Mix(Second, Mix(Back, multiplied, .25), m) : Mix(Back, multiplied, .25 * m);
        Near(At(Pixels(pdf), 12, 12), expected);
    }

    [Theory]
    [InlineData(0)]
    [InlineData(128)]
    [InlineData(255)]
    public void PartialGeometryAndClipWeightTheCompletedKnockoutResultOnce(int backdropAlpha)
    {
        byte[] pdf = GroupPdf(false, true,
            ".1 .8 .3 rg 0 0 32 32 re f q 0 0 16.5 32 re W n /A gs .8 .4 .2 rg 8.5 4 20 24 re f Q",
            "/ExtGState << /A << /ca .5 /BM /Multiply >> >>", backdropAlpha: backdropAlpha);
        Rgba32[] pixels = Pixels(pdf);
        double[] background = [.2, .6, .8, backdropAlpha / 255.0];
        double[] painted = Over(background, Source, .5, "Multiply");
        Near(At(pixels, 8, 12), Mix(Second, painted, .5));
        Near(At(pixels, 16, 12), Mix(Second, painted, .5));
        Near(At(pixels, 12, 12), painted);
        Near(At(pixels, 20, 12), Second);
    }

    [Theory]
    [InlineData(false, false)]
    [InlineData(false, true)]
    [InlineData(true, false)]
    [InlineData(true, true)]
    public void ImageMasksDistinguishGeometricCoverageAndOpacity(bool softMask, bool ais)
    {
        string mask = softMask ? Stream("/Type /XObject /Subtype /Image /Width 1 /Height 1 /ColorSpace /DeviceGray /BitsPerComponent 8", new byte[] { 64 }) :
            Stream("/Type /XObject /Subtype /Image /Width 2 /Height 1 /ImageMask true /BitsPerComponent 1", new byte[] { 0x40 });
        string image = Stream($"/Type /XObject /Subtype /Image /Width 1 /Height 1 /ColorSpace /DeviceRGB /BitsPerComponent 8 /{(softMask ? "SMask" : "Mask")} 7 0 R", new byte[] { 204, 102, 51 });
        string form = Form(false, true, ".1 .8 .3 rg 0 0 32 32 re f /A gs q 24 0 0 24 4 4 cm /Im Do Q",
            $"/XObject << /Im 6 0 R >> /ExtGState << /A << /BM /Multiply /ca .5 /AIS {Bool(ais)} >> >>");
        byte[] pdf = BackdropPage("/F Do", "/XObject << /F 5 0 R >>", Size, Size, [form, image, mask]);
        Rgba32[] actual = Pixels(pdf);
        if (softMask)
        {
            double alpha = .5 * 64 / 255.0;
            double[] expected = ais ? Mix(Second, Over(Back, Source, 1, "Multiply"), alpha) : Over(Back, Source, alpha, "Multiply");
            Near(At(actual, 12, 12), expected);
        }
        else
        {
            Near(At(actual, 8, 12), ais ? Mix(Second, Over(Back, Source, 1, "Multiply"), .5) : Over(Back, Source, .5, "Multiply"));
            Near(At(actual, 24, 12), Second);
        }
    }

    [Theory]
    [InlineData(false)]
    [InlineData(true)]
    public void PatternContentsBlendWithInitialBackdropBeforeKnockingOutSiblings(bool internalBlend)
    {
        string pattern = Stream("/Type /Pattern /PatternType 1 /PaintType 1 /TilingType 1 /BBox [0 0 16 16] /XStep 16 /YStep 16 /Resources << /ExtGState << /A << /ca .25 /BM /" + (internalBlend ? "Multiply" : "Normal") + " >> >> >>", "/A gs .8 .4 .2 rg 4 4 8 8 re f");
        string form = Form(false, true, ".1 .8 .3 rg 0 0 32 32 re f /Pattern cs /P scn 0 0 32 32 re f", "/Pattern << /P 6 0 R >>");
        byte[] pdf = BackdropPage("/F Do", "/XObject << /F 5 0 R >>", Size, Size, [form, pattern]);
        Rgba32[] actual = Pixels(pdf);
        Near(At(actual, 8, 8), Over(Back, Source, .25, internalBlend ? "Multiply" : "Normal"));
        Near(At(actual, 1, 1), Second);
    }

    [Fact]
    public void Type3TextInNonisolatedKnockoutKeepsItsInitialBackdrop()
    {
        string glyph = Stream("", "1000 0 0 0 1000 1000 d1 0 0 1000 1000 re f");
        string font = "<< /Type /Font /Subtype /Type3 /FontBBox [0 0 1000 1000] /FontMatrix [.001 0 0 .001 0 0] /CharProcs << /A 7 0 R >> /Encoding << /Type /Encoding /Differences [65 /A] >> /FirstChar 65 /LastChar 65 /Widths [1000] /Resources << >> >>";
        string form = Form(false, true, ".1 .8 .3 rg 0 0 32 32 re f /A gs .8 .4 .2 rg BT /F1 16 Tf 4 4 Td (A) Tj ET",
            "/Font << /F1 6 0 R >> /ExtGState << /A << /ca .5 /BM /Multiply >> >>");
        byte[] pdf = BackdropPage("/F Do", "/XObject << /F 5 0 R >>", Size, Size, [form, font, glyph]);
        Near(At(Pixels(pdf), 12, 12), Over(Back, Source, .5, "Multiply"));
    }

    [Theory]
    [InlineData("Normal")]
    [InlineData("Multiply")]
    [InlineData("Screen")]
    [InlineData("Overlay")]
    [InlineData("Darken")]
    [InlineData("Lighten")]
    [InlineData("ColorDodge")]
    [InlineData("ColorBurn")]
    [InlineData("HardLight")]
    [InlineData("SoftLight")]
    [InlineData("Difference")]
    [InlineData("Exclusion")]
    [InlineData("Hue")]
    [InlineData("Saturation")]
    [InlineData("Color")]
    [InlineData("Luminosity")]
    public void EveryBlendModeUsesInitialRatherThanPreviousSibling(string mode)
    {
        string resources = $"/ExtGState << /A << /ca .5 /BM /{mode} >> >>";
        foreach (int backdropAlpha in new[] { 0, 128, 255 })
        {
            byte[] actual = GroupPdf(false, true, ".1 .8 .3 rg 0 0 32 32 re f /A gs " + Paint, resources, backdropAlpha: backdropAlpha);
            byte[] control = BackdropPage("/A gs " + Paint, resources, Size, Size, backdropAlpha: backdropAlpha);
            Rgba32[] a = Pixels(actual), b = Pixels(control);
            for (int y = 6; y < 26; y++)
            for (int x = 6; x < 26; x++)
            {
                Rgba32 expected = At(b, x, y);
                Near(At(a, x, y), new[] { expected.R, expected.G, expected.B, expected.A }.Select(c => c / 255.0).ToArray(), 1);
            }
        }
    }

    [Theory]
    [InlineData(false, 0.0)]
    [InlineData(false, 0.5)]
    [InlineData(true, 0.0)]
    [InlineData(true, 0.5)]
    public void PatternedStencilUsesStencilAsShapeEvenWithOpacityMask(bool shading, double alpha)
    {
        string pattern = shading ?
            "<< /Type /Pattern /PatternType 2 /Shading << /ShadingType 2 /ColorSpace /DeviceRGB /Coords [0 0 32 0] /Extend [true true] /Function << /FunctionType 2 /Domain [0 1] /C0 [.8 .4 .2] /C1 [.8 .4 .2] /N 1 >> >> >>" :
            Stream("/Type /Pattern /PatternType 1 /PaintType 1 /TilingType 1 /BBox [0 0 32 32] /XStep 32 /YStep 32 /Resources << >>", ".8 .4 .2 rg 0 0 32 32 re f");
        string stencil = Stream("/Type /XObject /Subtype /Image /Width 2 /Height 1 /ImageMask true /BitsPerComponent 1", new byte[] { 0x40 });
        string mask = Stream(Bounds + " /Group << /S /Transparency /I true >>", ".5 g 0 0 32 32 re f");
        string form = Form(false, true, ".1 .8 .3 rg 0 0 32 32 re f /A gs /Pattern cs /P scn q 24 0 0 24 4 4 cm /Im Do Q",
            $"/Pattern << /P 6 0 R >> /XObject << /Im 7 0 R >> /ExtGState << /A << /BM /Multiply /ca {N(alpha)} /SMask << /S /Luminosity /G 8 0 R >> >> >>");
        byte[] pdf = BackdropPage("/F Do", "/XObject << /F 5 0 R >>", Size, Size, [form, pattern, stencil, mask]);
        Rgba32[] actual = Pixels(pdf);
        Near(At(actual, 8, 12), Over(Back, Source, alpha * 128 / 255.0, "Multiply"));
        Near(At(actual, 24, 12), Second);
    }

    [Fact]
    public void NestedShapeSurvivesAnIntermediateNonKnockoutGroup()
    {
        string inner = Form(false, false, "/A gs " + Paint, "/ExtGState << /A << /ca 0 /AIS false >> >>");
        string middle = Form(false, false, "/C Do", "/XObject << /C 7 0 R >>");
        string outer = Form(false, true, ".1 .8 .3 rg 0 0 32 32 re f /C Do", "/XObject << /C 6 0 R >>");
        byte[] pdf = BackdropPage("/F Do", "/XObject << /F 5 0 R >>", Size, Size, [outer, middle, inner]);
        Rgba32[] actual = Pixels(pdf);
        Near(At(actual, 12, 12), Back);
        Near(At(actual, 1, 1), Second);
    }

    [Fact]
    public void RegionsAndConcurrentReadsPreserveTheBorrowedInitialBackdrop()
    {
        const string bounds = "/Type /XObject /Subtype /Form /BBox [0 0 400 400]";
        string inner = Stream(bounds + " /Group << /S /Transparency /I false >> /Resources << /ExtGState << /A << /ca .25 /BM /Multiply >> >> >>",
            "/A gs .8 .4 .2 rg 80.5 80.5 240 240 re f");
        string outer = Stream(bounds + " /Group << /S /Transparency /K true /I false >> /Resources << /XObject << /C 6 0 R >> >>",
            ".1 .8 .3 rg 20 20 360 360 re f /C Do");
        byte[] pdf = BackdropPage("/F Do", "/XObject << /F 5 0 R >>", 400, 400, [outer, inner]);
        Rgba32[] whole = RenderTests.Load(pdf, new PdfRenderOptions { Dpi = 72, Background = default }).ToArray<Rgba32>(maxDegree: 1);
        Image image = RenderTests.Load(pdf, new PdfRenderOptions { Dpi = 72, Background = default });
        Assert.Equal(whole, image.ToArray<Rgba32>(maxDegree: 4));
        Parallel.For(0, 16, new ParallelOptions { MaxDegreeOfParallelism = 4 }, i =>
        {
            var region = new ImageRect(70 + i * 13, 70 + i * 7, 99, 123);
            var part = new Rgba32[region.Width * region.Height];
            image.CopyPixelsTo<Rgba32>(part, region);
            for (int y = 0; y < region.Height; y++)
                Assert.True(part.AsSpan(y * region.Width, region.Width).SequenceEqual(whole.AsSpan((region.Y + y) * 400 + region.X, region.Width)));
        });
    }

    [Theory]
    [InlineData("/None")]
    [InlineData("42")]
    [InlineData("<< >>")]
    [InlineData("999 0 R")]
    [InlineData("/None /SMaskInData 1")]
    public void InvalidSoftMaskEntryDoesNotTurnHardMaskHolesIntoOpacity(string softMask)
    {
        string mask = Stream("/Type /XObject /Subtype /Image /Width 2 /Height 1 /ImageMask true /BitsPerComponent 1", new byte[] { 0x40 });
        string image = Stream($"/Type /XObject /Subtype /Image /Width 1 /Height 1 /ColorSpace /DeviceRGB /BitsPerComponent 8 /Mask 7 0 R /SMask {softMask}", new byte[] { 204, 102, 51 });
        string form = Form(false, true, ".1 .8 .3 rg 0 0 32 32 re f /A gs q 24 0 0 24 4 4 cm /Im Do Q",
            "/XObject << /Im 6 0 R >> /ExtGState << /A << /BM /Multiply /ca .5 >> >>");
        byte[] pdf = BackdropPage("/F Do", "/XObject << /F 5 0 R >>", Size, Size, [form, image, mask]);
        Rgba32[] actual = Pixels(pdf);
        Near(At(actual, 8, 12), Over(Back, Source, .5, "Multiply"));
        Near(At(actual, 24, 12), Second);
    }

    private static byte[] GroupPdf(bool isolated, bool knockout, string content, string resources = "", string page = "/F Do", string pageResources = "", int backdropAlpha = 255) =>
        BackdropPage(page, "/XObject << /F 5 0 R >> " + pageResources, Size, Size, [Form(isolated, knockout, content, resources)], backdropAlpha);
    private static byte[] BackdropPage(string content, string resources, int width, int height, string[]? extra = null, int backdropAlpha = 255)
    {
        // The transparency backdrop is authored PDF paint, not the viewer's final Background.
        // Keep its opacity scoped so it cannot leak into the form invocation or its children.
        string backdropState = $"/Backdrop << /ca {N(backdropAlpha / 255.0)} >>";
        resources = resources.Contains("/ExtGState <<", StringComparison.Ordinal)
            ? resources.Replace("/ExtGState <<", "/ExtGState << " + backdropState, StringComparison.Ordinal)
            : resources + " /ExtGState << " + backdropState + " >>";
        return Page($"q /Backdrop gs .2 .6 .8 rg 0 0 {width} {height} re f Q " + content, resources, width, height, extra);
    }
    private static string Form(bool isolated, bool knockout, string content, string resources) =>
        Stream($"{Bounds} /Group << /S /Transparency /I {Bool(isolated)} /K {Bool(knockout)} >> /Resources << {resources} >>", content);
    private static string Bool(bool value) => value ? "true" : "false";
    private static Rgba32[] Pixels(byte[] pdf) => RenderTests.Load(pdf,
        new PdfRenderOptions { Dpi = 72, Background = default }).ToArray<Rgba32>();
    private static Rgba32 At(Rgba32[] pixels, int x, int y) => pixels[((Size - 1 - y) * Size) + x];
    private static double[] Over(double[] b, double[] s, double alpha, string mode)
    {
        double ar = alpha + b[3] * (1 - alpha);
        var r = new double[4]; r[3] = ar;
        for (int c = 0; c < 3; c++)
        {
            double blend = mode switch { "Multiply" => b[c] * s[c], "Screen" => b[c] + s[c] - b[c] * s[c], _ => s[c] };
            r[c] = ar > 0 ? ((1 - alpha) * b[3] * b[c] + alpha * ((1 - b[3]) * s[c] + b[3] * blend)) / ar : 0;
        }
        return r;
    }
    private static double[] Mix(double[] b, double[] s, double f)
    {
        var r = new double[4]; r[3] = b[3] * (1 - f) + s[3] * f;
        for (int c = 0; c < 3; c++) r[c] = r[3] > 0 ? (b[c] * b[3] * (1 - f) + s[c] * s[3] * f) / r[3] : 0;
        return r;
    }
    private static double[] Recover(double[] result, double[] initial, double alpha)
    {
        var r = new double[4]; r[3] = alpha;
        for (int c = 0; c < 3; c++) r[c] = alpha > 0 ? Math.Clamp((result[c] * result[3] - (1 - alpha) * initial[c] * initial[3]) / alpha, 0, 1) : 0;
        return r;
    }
    private static void Near(Rgba32 actual, double[] expected, int tolerance = 3)
    {
        int[] a = [actual.R, actual.G, actual.B, actual.A];
        for (int c = 0; c < 4; c++) Assert.True(Math.Abs(a[c] - expected[c] * 255) <= tolerance,
            string.Create(CultureInfo.InvariantCulture, $"channel {c}: expected {expected[c] * 255:F3}, actual {a[c]}; RGBA {actual}"));
    }
}
