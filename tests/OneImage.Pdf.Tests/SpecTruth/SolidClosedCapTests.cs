// SPDX-License-Identifier: MIT
// Copyright (c) 2026 OneImage contributors
// Independently authored numeric geometry and Type 3 program; no external assets or reference pixels.
using OneImage.Pdf.Render;
using OnePdf;
using static OneImage.Pdf.Tests.SpecTruth.Spec;

namespace OneImage.Pdf.Tests.SpecTruth;

public class SolidClosedCapTests
{
    public static TheoryData<string> StationaryPaths => new()
    {
        "48 36 m h", "48 36 m 48 36 l h", "48 36 0 0 re",
        "48 36 m 48 36 l 48 36 l h", "48 36 m 48 36 48 36 48 36 c h",
        "48 36 m h h", "48 36 m 48 36 l h h", "48 36 m 48 36 l h 48 36 l h",
        "48 36 m 48 36 48 36 48 36 c h 48 36 48 36 48 36 c h",
    };

    [Theory]
    [MemberData(nameof(StationaryPaths))]
    [Trait("Section", "8.5.3.2")]
    public void StationaryRoundCapsHaveOneOutline(string path)
    {
        Rgba32[] control = Pix(Page("0 G 18 w 1 J 48 36 m 48 36 l S", w: 192, h: 144));
        double area = BlackArea(control, 192, 0, 0, 192, 144);
        Assert.InRange(area, (Math.PI * 81) - 6, (Math.PI * 81) + 1);
        foreach (string dash in new[] { "[] 0 d", "[11 17] 3 d", "[0 17] 0 d" })
        {
            Assert.Equal(control, Pix(Page($"0 G 18 w 1 J {dash} {path} S", w: 192, h: 144)));
        }
        Assert.Equal(0, BlackArea(Pix(Page($"0 G 18 w 1 J [11 17] 19 d {path} S", w: 192, h: 144)), 192, 0, 0, 192, 144));
    }

    [Theory]
    [InlineData("", 18, 72)]
    [InlineData("", 18, 144)]
    [InlineData("1.5 0.3 0.25 0.8 -33 -7.2 cm", 18, 144)]
    [InlineData("-1 0 0 1 96 0 cm", 18, 144)]
    [InlineData("", 0, 72)]
    [InlineData("", 0, 144)]
    [InlineData("1.5 0.3 0.25 0.8 -33 -7.2 cm", 0, 144)]
    [InlineData("-1 0 0 1 96 0 cm", 0, 144)]
    [InlineData("", 0.01, 144)]
    public void ClosingDoesNotChangeTransformOrWidth(string transform, double width, int dpi)
    {
        string setup = $"0 G {transform} {N(width)} w 1 J ";
        var options = new PdfRenderOptions { Dpi = dpi };
        Rgba32[] control = Pix(Page(setup + "48 36 m 48 36 l S", w: 192, h: 144), options);
        Assert.Contains(control, p => p.R != 255);
        foreach (string path in new[] { "48 36 m 48 36 l h", "48 36 0 0 re", "48 36 m h" })
        {
            Assert.Equal(control, Pix(Page(setup + path + " S", w: 192, h: 144), options));
        }
    }

    [Fact]
    public void MixedSubpathsAndTrailingMoveAreUnaffected()
    {
        const string setup = "0 G 6 w 1 J ";
        const string ordinary = "9 12 m 29 12 l 29 22 l h";
        const string tail = " 130 95 m";
        Rgba32[] control = Pix(Page(setup + ordinary + " 48 36 m 48 36 l" + tail + " S", w: 192, h: 144));
        Assert.Equal(control, Pix(Page(setup + ordinary + " 48 36 0 0 re" + tail + " S", w: 192, h: 144)));
        Assert.Equal(control, Pix(Page(setup + ordinary + " S 48 36 0 0 re S" + tail + " S", w: 192, h: 144)));
        // A stationary close followed by real geometry must not turn the real segment into a closed path.
        Assert.Equal(Pix(Page(setup + "48 36 m 68 36 l S", w: 192, h: 144)),
            Pix(Page(setup + "48 36 m 48 36 l h 68 36 l S", w: 192, h: 144)));
    }

    [Theory]
    [InlineData(0)]
    [InlineData(2)]
    public void OtherCapStylesKeepTheirOpenControls(int cap)
    {
        foreach (string dash in new[] { "[] 0 d", "[11 17] 3 d", "[11 17] 19 d" })
        {
            Assert.Equal(0, BlackArea(Pix(Page($"0 G 18 w {cap} J {dash} 48 36 m 48 36 l S", w: 192, h: 144)), 192, 0, 0, 192, 144));
        }
    }

    [Theory]
    [InlineData("[] 0 d")]
    [InlineData("[11 17] 3 d")]
    [InlineData("[11 17] 19 d")]
    public void Type3StrokeUsesTheSameCapOwnership(string dash)
    {
        byte[] Glyph(string path) => Page("BT /F 1 Tf 1 0 0 1 0 0 Tm (a) Tj ET", "/Font << /F 5 0 R >>", 192, 144,
            ["<< /Type /Font /Subtype /Type3 /FontBBox [0 0 100 80] /FontMatrix [1 0 0 1 0 0] /CharProcs << /a 6 0 R >> /Encoding << /Type /Encoding /Differences [97 /a] >> /FirstChar 97 /LastChar 97 /Widths [100] /Resources << >> >>",
             Stream("", "100 0 d0 0 G 18 w 1 J " + dash + " " + path + " S")]);
        Rgba32[] control = Pix(Glyph("48 36 m 48 36 l"));
        Assert.Equal(control, Pix(Glyph("48 36 m 48 36 l h")));
        Assert.Equal(Pix(Page("0 G 18 w 1 J " + dash + " 48 36 m 48 36 l S", w: 192, h: 144)), control);
    }
    [Fact]
    public void PositiveGeometryThatRoundsToOneFloatPointIsStillStroked()
    {
        Rgba32[] actual = Pix(Page("0 G 18 w 1 J 48 36 m 48.00000001 36 l h S", w: 192, h: 144));
        Assert.InRange(BlackArea(actual, 192, 0, 0, 192, 144), (Math.PI * 81) - 6, (Math.PI * 81) + 1);
    }

    [Theory]
    [InlineData("48 36 m", "")]
    [InlineData("h h", "")]
    [InlineData("48 36 l", "")]
    [InlineData("48 36 m 48 36 l h 2 l", "48 36 m 48 36 l")]
    [InlineData("48 36 m 48 36 l h 48 36 48 c", "48 36 m 48 36 l")]
    public void IncompleteAndMoveOnlyContentKeepsCompletedGeometry(string path, string expected)
    {
        const string setup = "0 G 18 w 1 J ";
        Assert.Equal(Pix(Page(setup + expected + " S", w: 192, h: 144)),
            Pix(Page(setup + path + " S", w: 192, h: 144)));
    }

    [Theory]
    [InlineData(1)]
    [InlineData(4)]
    [InlineData(16)]
    public void ClosedCapsAreRegionAndThreadDeterministic(int degree)
    {
        byte[] pdf = Page("0 G 22 w 1 J 127 129 m 127 129 l h 257 257 0 0 re S", w: 384, h: 384);
        Rgba32[] whole = RenderTests.Load(pdf, new PdfRenderOptions { Dpi = 72 }).ToArray<Rgba32>(maxDegree: 1);
        Assert.Equal(whole, RenderTests.Load(pdf, new PdfRenderOptions { Dpi = 72 }).ToArray<Rgba32>(maxDegree: degree));
        var region = new ImageRect(111, 111, 162, 162);
        var part = new Rgba32[region.Width * region.Height];
        RenderTests.Load(pdf, new PdfRenderOptions { Dpi = 72 }).CopyPixelsTo<Rgba32>(part, region, degree);
        for (int y = 0; y < region.Height; y++)
        {
            Assert.True(part.AsSpan(y * region.Width, region.Width).SequenceEqual(whole.AsSpan(((y + region.Y) * 384) + region.X, region.Width)));
        }
    }

    [Theory]
    [InlineData((byte)PdfPathVerb.Move)]
    [InlineData((byte)PdfPathVerb.Line)]
    [InlineData((byte)PdfPathVerb.Curve)]
    public void TruncatedRawPathsKeepAlreadyCompletedCoreGeometry(byte truncatedVerb)
    {
        byte[] verbs = [(byte)PdfPathVerb.Move, (byte)PdfPathVerb.Line, (byte)PdfPathVerb.Close, truncatedVerb];
        double[] points = [48, 36, 48, 36];
        using PdfDocument document = PdfDocument.Open(Page("", w: 192, h: 144));
        var page = new PageRender(document.Pages[0], new PdfRenderOptions { Dpi = 72 });
        using var canvas = new Canvas(192, 144, PixelFormat.Rgba8);
        canvas.Clear(new Rgba32(255, 255, 255, 255));
        using var device = new CanvasDevice(page, PdfMatrix.Identity, canvas, 0, null, CancellationToken.None);
        var black = new PdfColor(PdfColorSpace.Gray, 0, 0, 0, 0, null);
        var state = new PdfGraphicsState(PdfMatrix.Identity, black, black, 18, 1, 0, 10,
            ReadOnlyMemory<double>.Empty, 0, 1, "RelativeColorimetric", 1, 1, "Normal", 0, false, false, false, 0);
        device.StrokePath(new PdfPath(verbs, points), state);
        Rgba32[] actual = canvas.Snapshot().ToArray<Rgba32>();
        Assert.InRange(BlackArea(actual, 192, 0, 0, 192, 144), (Math.PI * 81) - 6, (Math.PI * 81) + 1);
    }

}
