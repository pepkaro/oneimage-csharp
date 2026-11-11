using System.Globalization;

namespace OneImage.Pdf.Tests;

public class GroupAlphaTests
{
    public static IEnumerable<object[]> AlphaCases()
    {
        foreach (bool isolated in new[] { false, true })
        foreach (double outer in new[] { 0.0, 0.5, 1.0 })
        foreach (double child in new[] { 0.0, 0.5, 1.0 })
        foreach (byte backdrop in new byte[] { 0, 128, 255 })
            yield return [isolated, outer, child, backdrop];
    }

    [Theory]
    [MemberData(nameof(AlphaCases))]
    public void GroupAlphaAndBlendModesMatchPremultipliedEquations(bool isolated, double outer, double child, byte backdropAlpha)
    {
        var backdrop = new Rgba32(204, 102, 51, backdropAlpha);
        double[] cb = [0.8, 0.4, 0.2], cs = [0.2, 0.6, 0.8];
        double ab = backdropAlpha / 255.0;
        foreach (string inside in new[] { "Normal", "Multiply", "Screen" })
        foreach (string outside in new[] { "Normal", "Multiply", "Screen" })
        {
            string form = Form(isolated, $"/H gs 0.2 0.6 0.8 rg 8 8 16 16 re f",
                $"/ExtGState << /H << /ca {N(child)} /BM /{inside} >> >>");
            byte[] pdf = TestPdf.Page("/G gs /F Do", $"/XObject << /F 5 0 R >> /ExtGState << /G << /ca {N(outer)} /BM /{outside} >> >>", 32, 32, [form]);
            Rgba32[] pixels = Pixels(pdf, backdrop);
            double a = outer * child, resultAlpha = a + (ab * (1 - a));
            var expected = new double[4];
            expected[3] = resultAlpha * 255;
            for (int channel = 0; channel < 3; channel++)
            {
                double groupColor = isolated ? cs[channel] : ((1 - ab) * cs[channel]) + (ab * Blend(inside, cb[channel], cs[channel]));
                double blended = ((1 - ab) * groupColor) + (ab * Blend(outside, cb[channel], groupColor));
                expected[channel] = resultAlpha == 0 ? 0 : (((1 - a) * ab * cb[channel]) + (a * blended)) / resultAlpha * 255;
            }
            Near(pixels[(16 * 32) + 16], expected, $"I={isolated}, outer={outer}, child={child}, backdrop={backdropAlpha}, {inside}/{outside}");
            // No group contribution outside the painted object, including a translucent initial backdrop.
            Near(pixels[0], [backdropAlpha == 0 ? 0 : 204, backdropAlpha == 0 ? 0 : 102, backdropAlpha == 0 ? 0 : 51, backdropAlpha], "untouched");
        }
    }

    [Theory]
    [InlineData(false)]
    [InlineData(true)]
    public void OverlappingChildrenUseUnionAlphaOnce(bool isolated)
    {
        string form = Form(isolated, "/H gs 1 0 0 rg 4 4 20 20 re f 0 0 1 rg 12 12 16 16 re f", "/ExtGState << /H << /ca .5 >> >>");
        byte[] pdf = TestPdf.Page("1 g 0 0 32 32 re f /G gs /F Do", "/XObject << /F 5 0 R >> /ExtGState << /G << /ca .5 >> >>", 32, 32, [form]);
        Rgba32[] pixels = Pixels(pdf, new Rgba32(255, 255, 255, 255));
        Near(pixels[(16 * 32) + 16], [191.25, 159.375, 223.125, 255], "overlap");
        Near(pixels[(24 * 32) + 8], [255, 191.25, 191.25, 255], "red only");
    }

    [Theory]
    [InlineData("Normal", false)]
    [InlineData("Multiply", false)]
    [InlineData("Screen", false)]
    [InlineData("Normal", true)]
    [InlineData("Multiply", true)]
    [InlineData("Screen", true)]
    public void NestedGroupsPropagateTheirOwnAlpha(string outside, bool isolateMiddle)
    {
        string leaf = Form(false, "/H gs 1 0 0 rg 8 8 16 16 re f", "/ExtGState << /H << /ca .5 >> >>");
        string middle = Form(isolateMiddle, "/H gs /F Do", "/XObject << /F 5 0 R >> /ExtGState << /H << /ca .5 >> >>");
        byte[] pdf = TestPdf.Page("/G gs /F Do", $"/XObject << /F 6 0 R >> /ExtGState << /G << /ca .5 /BM /{outside} >> >>", 32, 32, [leaf, middle]);
        var backdrop = new Rgba32(102, 153, 204, 128);
        Rgba32[] pixels = Pixels(pdf, backdrop);
        double ab = 128 / 255.0, a = 0.125, alpha = a + ab * (1 - a);
        double[] cb = [0.4, 0.6, 0.8], cs = [1, 0, 0], expected = [0, 0, 0, alpha * 255];
        for (int c = 0; c < 3; c++)
            expected[c] = (((1 - a) * ab * cb[c]) + (a * (((1 - ab) * cs[c]) + (ab * Blend(outside, cb[c], cs[c]))))) / alpha * 255;
        Near(pixels[(16 * 32) + 16], expected, "nested");
    }

    [Theory]
    [InlineData(false)]
    [InlineData(true)]
    public void PassthroughFormDoesNotHideAncestorCoverage(bool isolateChild)
    {
        string leaf = Form(isolateChild, "1 0 0 rg 8 8 16 16 re f");
        string parent = Form(false, "/H gs /F Do", "/XObject << /F 5 0 R >> /ExtGState << /H << /CA .5 >> >>");
        byte[] pdf = TestPdf.Page("1 g 0 0 32 32 re f /G gs /F Do", "/XObject << /F 6 0 R >> /ExtGState << /G << /ca .5 >> >>", 32, 32, [leaf, parent]);
        Near(Pixels(pdf, default)[(16 * 32) + 16], [255, 127.5, 127.5, 255], "passthrough");
    }

    [Theory]
    [InlineData("Normal")]
    [InlineData("Multiply")]
    [InlineData("Screen")]
    public void SoftMaskAndOuterOpacityAreAppliedOnce(string outside)
    {
        string leaf = Form(false, "/H gs 1 0 0 rg 0 0 32 32 re f", "/ExtGState << /H << /ca .5 >> >>");
        string mask = Form(true, "/H gs 1 g 0 0 16 32 re f", "/ExtGState << /H << /ca .5 >> >>");
        byte[] pdf = TestPdf.Page("/G gs /F Do", $"/XObject << /F 5 0 R >> /ExtGState << /G << /ca .5 /BM /{outside} /SMask << /S /Alpha /G 6 0 R >> >> >>", 32, 32, [leaf, mask]);
        var bg = new Rgba32(102, 153, 204, 255);
        Rgba32[] pixels = Pixels(pdf, bg);
        double[] cb = [0.4, 0.6, 0.8], cs = [1, 0, 0], expected = [0, 0, 0, 255];
        for (int c = 0; c < 3; c++) expected[c] = 255 * ((0.875 * cb[c]) + (0.125 * Blend(outside, cb[c], cs[c])));
        Near(pixels[(16 * 32) + 8], expected, "masked");
        Assert.Equal(bg, pixels[(16 * 32) + 24]);
    }

    [Theory]
    [InlineData(0)]
    [InlineData(128)]
    [InlineData(255)]
    public void FractionalThinRulesMatchDirectPaintingAcrossTiles(int alpha)
    {
        const string paint = "1 0 0 rg 5.25 127.25 259.5 1.5 re f 0 0 1 RG .5 w 127.25 5 m 129.75 265 l S";
        string form = RegionTests.Obj("/Type /XObject /Subtype /Form /BBox [0 0 270 270] /Group << /S /Transparency /I false >> /Resources << /ExtGState << /H << /ca .5 /CA .5 >> >> >>", "/H gs " + paint);
        byte[] grouped = TestPdf.Page("/G gs /F Do", "/XObject << /F 5 0 R >> /ExtGState << /G << /ca .5 >> >>", 270, 270, [form]);
        // Non-overlapping pixels match painting each primitive at the combined alpha.
        byte[] direct = TestPdf.Page("/G gs " + paint, "/ExtGState << /G << /ca .25 /CA .25 >> >>", 270, 270);
        var bg = new Rgba32(102, 153, 204, (byte)alpha);
        Rgba32[] actual = Pixels(grouped, bg), expected = Pixels(direct, bg);
        Assert.True(actual.AsSpan().SequenceEqual(Pixels(grouped, bg, 4)));
        for (int y = 0; y < 270; y++)
        for (int x = 0; x < 270; x++)
        {
            if (x > 124 && x < 133 && y > 139 && y < 145) continue; // The two primitives overlap here.
            Rgba32 e = expected[(y * 270) + x];
            Rgba32 a = actual[(y * 270) + x];
            // At sub-byte edge alpha, straight RGB is ill-conditioned (and irrelevant at zero).
            // Compare associated color and alpha, the actual contribution to any backdrop.
            double[] expectedPremultiplied = [e.R * e.A / 255.0, e.G * e.A / 255.0, e.B * e.A / 255.0, e.A];
            double[] actualPremultiplied = [a.R * a.A / 255.0, a.G * a.A / 255.0, a.B * a.A / 255.0, a.A];
            for (int c = 0; c < 4; c++)
                Assert.True(Math.Abs(expectedPremultiplied[c] - actualPremultiplied[c]) <= 2, $"thin rule ({x},{y}), channel {c}");
        }
    }

    [Theory]
    [InlineData(0)]
    [InlineData(128)]
    [InlineData(255)]
    public void TinyGroupAlphaHasBoundedAssociatedColorError(int backdropAlpha)
    {
        double[] cb = [0.8, 0.4, 0.2], cs = [0.2, 0.6, 0.8];
        double ab = backdropAlpha / 255.0;
        foreach (double child in new[] { 0.000001, 1.0 / 255, 2.0 / 255 })
        foreach (string outside in new[] { "Normal", "Multiply", "Screen" })
        {
            string form = Form(false, "/H gs 0.2 0.6 0.8 rg 8 8 16 16 re f", $"/ExtGState << /H << /ca {N(child)} >> >>");
            byte[] pdf = TestPdf.Page("/G gs /F Do", $"/XObject << /F 5 0 R >> /ExtGState << /G << /ca .5 /BM /{outside} >> >>", 32, 32, [form]);
            Rgba32 pixel = Pixels(pdf, new Rgba32(204, 102, 51, (byte)backdropAlpha))[(16 * 32) + 16];
            double a = child * 0.5, expectedAlpha = a + (ab * (1 - a));
            Assert.InRange(Math.Abs(pixel.A - (expectedAlpha * 255)), 0, 2);
            byte[] channels = [pixel.R, pixel.G, pixel.B];
            for (int c = 0; c < 3; c++)
            {
                double expected = 255 * (((1 - a) * ab * cb[c]) + (a * (((1 - ab) * cs[c]) + (ab * Blend(outside, cb[c], cs[c])))));
                Assert.InRange(Math.Abs((channels[c] * pixel.A / 255.0) - expected), 0, 2);
            }
        }
    }
    [Theory]
    [InlineData(1.0, false)]
    [InlineData(0.5, false)]
    [InlineData(1.0, true)]
    [InlineData(0.5, true)]
    public void PatternedStencilContributesItsAlphaToTheGroup(double patternAlpha, bool masked)
    {
        string maskEntry = masked ? "/SMask << /S /Alpha /G 7 0 R >>" : "";
        string form = Form(false, "/H gs /Pattern cs /P scn q 16 0 0 16 8 8 cm BI /W 1 /H 1 /IM true /BPC 1 /F /AHx ID 00> EI Q",
            $"/Pattern << /P 6 0 R >> /ExtGState << /H << /ca .5 {maskEntry} >> >>");
        string pattern = RegionTests.Obj($"/Type /Pattern /PatternType 1 /PaintType 1 /TilingType 1 /BBox [0 0 2 2] /XStep 2 /YStep 2 /Resources << /ExtGState << /A << /ca {N(patternAlpha)} >> >> >>", "/A gs 1 0 0 rg 0 0 2 2 re f");
        string mask = Form(true, "/H gs 1 g 0 0 32 32 re f", "/ExtGState << /H << /ca .5 >> >>");
        byte[] pdf = TestPdf.Page("/G gs /F Do", "/XObject << /F 5 0 R >> /ExtGState << /G << /ca .5 >> >>", 32, 32, [form, pattern, mask]);
        Rgba32[] pixels = Pixels(pdf, new Rgba32(255, 255, 255, 255));
        double alpha = 0.25 * patternAlpha * (masked ? 0.5 : 1);
        Near(pixels[(16 * 32) + 16], [255, 255 * (1 - alpha), 255 * (1 - alpha), 255], "patterned stencil");
        Assert.Equal(new Rgba32(255, 255, 255, 255), pixels[0]);
    }
    [Fact]
    public void MaskDefinitionDoesNotContributeToAncestorGroupAlpha()
    {
        string form = Form(false, "/M gs /N gs 1 0 0 rg 4 4 4 4 re f",
            "/ExtGState << /M << /SMask << /S /Alpha /G 6 0 R >> >> /N << /SMask /None >> >>");
        string mask = Form(false, "1 g 0 0 32 32 re f");
        byte[] pdf = TestPdf.Page("/G gs /F Do", "/XObject << /F 5 0 R >> /ExtGState << /G << /ca .5 /BM /Multiply >> >>", 32, 32, [form, mask]);
        var backdrop = new Rgba32(204, 102, 51, 128);
        Rgba32[] pixels = Pixels(pdf, backdrop);
        Assert.Equal(backdrop, pixels[(16 * 32) + 16]);
        Assert.Equal(backdrop, pixels[0]);
    }
    private static string Form(bool isolated, string content, string resources = "") => RegionTests.Obj($"/Type /XObject /Subtype /Form /BBox [0 0 32 32] /Group << /S /Transparency /I {isolated.ToString().ToLowerInvariant()} >> /Resources << {resources} >>", content);
    private static Rgba32[] Pixels(byte[] pdf, Rgba32 background, int degree = 1) => RenderTests.Load(pdf, new PdfRenderOptions { Dpi = 72, Background = background }).ToArray<Rgba32>(maxDegree: degree);
    private static string N(double value) => value.ToString("0.#################", CultureInfo.InvariantCulture);
    private static double Blend(string mode, double backdrop, double source) => mode switch { "Multiply" => backdrop * source, "Screen" => backdrop + source - backdrop * source, _ => source };
    private static void Near(Rgba32 actual, double[] expected, string context, double tolerance = 2)
    {
        byte[] channels = [actual.R, actual.G, actual.B, actual.A];
        for (int c = 0; c < 4; c++) Assert.True(Math.Abs(channels[c] - expected[c]) <= tolerance, $"{context}: channel {c}, expected {expected[c]:F3}, got {channels[c]}");
    }
}
