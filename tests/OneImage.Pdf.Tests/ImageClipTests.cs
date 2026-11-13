using System.Numerics;
using OneImage.Drawing;
using OneImage.Pdf.Render;
using DrawingPath = OneImage.Drawing.Path;

namespace OneImage.Pdf.Tests;

/// <summary>Generated image/clip invariants; no reference pixels or external PDF assets.</summary>
public class ImageClipTests
{
    private const string Resources = "/XObject << /Im0 5 0 R >>";
    private const string Placement = "159.5 0 0 159.5 10.25 10.25";
    private const string Picture = "/Type /XObject /Subtype /Image /Width 2 /Height 2 /ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /ASCIIHexDecode";

    private static byte[] Page(string clip, string placement = Placement, string kind = "opaque", bool transparent = false)
    {
        string image = RegionTests.Obj(Picture + (kind == "image-alpha" ? " /SMask 6 0 R" : ""), "1e19231e19231e19231e1923>");
        string mask = RegionTests.Obj("/Type /XObject /Subtype /Image /Width 2 /Height 2 /ColorSpace /DeviceGray /BitsPerComponent 8 /Filter /ASCIIHexDecode", "4080c0ff>");
        string resources = Resources + " /ExtGState << /GS << /ca 0.5 /BM /Multiply >> /SM << /SMask << /S /Luminosity /G 7 0 R >> >> >>";
        string softMask = RegionTests.Obj("/Type /XObject /Subtype /Form /BBox [0 0 180 180] /Group << /S /Transparency /CS /DeviceGray /I true >> /Resources << >>", "0.5 g 0 0 180 180 re f");
        string state = kind == "alpha-blend" ? "/GS gs " : kind == "soft-mask" ? "/SM gs " : "";
        string draw = $"q {state}{placement} cm {clip} /Im0 Do Q";
        if (kind is "isolated" or "nonisolated" or "knockout")
        {
            string group = RegionTests.Obj($"/Type /XObject /Subtype /Form /BBox [0 0 180 180] /Group << /S /Transparency /I {(kind == "nonisolated" ? "false" : "true")} /K {(kind == "knockout" ? "true" : "false")} >> /Resources << {resources} >>", "0 0.5 0 rg 0 0 180 180 re f " + draw);
            return TestPdf.Page((transparent ? "" : "0.2 0.4 0.6 rg 0 0 180 180 re f ") + "/GS gs /Fm Do", resources + " /XObject << /Fm 8 0 R >>", 180, 180, [image, mask, softMask, group]);
        }

        return TestPdf.Page(draw, resources, 180, 180, [image, mask, softMask]);
    }

    private static Rgba32[] Render(byte[] pdf, double dpi = 96, int degree = 1) =>
        RenderTests.Load(pdf, new PdfRenderOptions { Dpi = dpi }).ToArray<Rgba32>(maxDegree: degree);

    private static void Equal(Rgba32[] expected, Rgba32[] actual) => Assert.True(expected.AsSpan().SequenceEqual(actual));

    [Theory]
    [InlineData(72)]
    [InlineData(96)]
    [InlineData(144)]
    [InlineData(288)]
    public void IdenticalRectangleClipDoesNotSquareImageEdgeCoverage(double dpi) =>
        Equal(Render(Page(""), dpi), Render(Page("0 0 1 1 re W n"), dpi));

    [Theory]
    [InlineData(Placement)]
    [InlineData("81.25 25.5 -30.75 90.125 60.25 20.125")]
    [InlineData("0 159.5 -159.5 0 169.75 10.25")]
    [InlineData("-159.5 0 0 159.5 169.75 10.25")]
    [InlineData("0.375 0 0 0.625 10.25 10.25")]
    public void IdenticalClipIsInvariantUnderPlacement(string placement)
    {
        foreach (double dpi in new[] { 72.0, 96, 144 })
        {
            Equal(Render(Page("", placement), dpi), Render(Page("0 0 1 1 re W n", placement), dpi));
        }
    }

    [Theory]
    [InlineData("0 0 1 1 re W* n")]
    [InlineData("0 0 m 0 1 l 1 1 l 1 0 l h W n")]
    [InlineData("-0.01 -0.01 1.02 1.02 re W n")]
    [InlineData("-1 -1 3 3 re W n 0 0 1 1 re W n")]
    [InlineData("0 0 1 1 re W n -1 -1 3 3 re W n")]
    public void ContainingAndNestedClipsAreRedundant(string clip) => Equal(Render(Page("")), Render(Page(clip)));

    [Theory]
    [InlineData("opaque")]
    [InlineData("image-alpha")]
    [InlineData("alpha-blend")]
    [InlineData("soft-mask")]
    [InlineData("isolated")]
    [InlineData("nonisolated")]
    [InlineData("knockout")]
    public void RedundantClipPreservesTransparencySemantics(string kind) =>
        Equal(Render(Page("", kind: kind)), Render(Page("0 0 1 1 re W n", kind: kind)));

    [Theory]
    [InlineData(1)]
    [InlineData(4)]
    [InlineData(16)]
    public void RegionsAndThreadCountsMatch(int degree)
    {
        byte[] pdf = Page("0 0 1 1 re W n");
        Rgba32[] whole = Render(Page(""));
        Equal(whole, Render(pdf, degree: degree));
        foreach (var r in new[] { new ImageRect(127, 127, 2, 2), new ImageRect(7, 11, 201, 179), new ImageRect(0, 0, 240, 240) })
        {
            var part = new Rgba32[r.Width * r.Height];
            RenderTests.Load(pdf, new PdfRenderOptions { Dpi = 96 }).CopyPixelsTo<Rgba32>(part, r, degree);
            for (int y = 0; y < r.Height; y++)
            {
                Assert.True(part.AsSpan(y * r.Width, r.Width).SequenceEqual(whole.AsSpan(((r.Y + y) * 240) + r.X, r.Width)));
            }
        }
    }

    [Theory]
    [InlineData("0.25 0.25 0.5 0.5 re W n")]
    [InlineData("0 0 0.75 1 re W n")]
    [InlineData("0 0 1 1 re 0.25 0.25 0.5 0.5 re W* n")]
    [InlineData("0 0 m 1 0 l 1 1 l 0.5 0.5 l 0 1 l h W n")]
    public void NonredundantClipsStillRemovePixels(string clip)
    {
        Rgba32[] expected = Render(Page(""));
        Rgba32[] clipped = Render(Page(clip));
        Assert.False(expected.AsSpan().SequenceEqual(clipped));
        Assert.True(clipped.Count(p => p.R == 255) > expected.Count(p => p.R == 255));
    }

    [Theory]
    [InlineData(false)]
    [InlineData(true)]
    public void StencilImagesKeepExistingPatternAndAlphaSemantics(bool pattern)
    {
        string stencil = RegionTests.Obj("/Type /XObject /Subtype /Image /Width 2 /Height 2 /ImageMask true /BitsPerComponent 1 /Filter /ASCIIHexDecode", "4080>");
        string paint = pattern ? "/Pattern cs /P scn" : "0.2 0.4 0.6 rg";
        byte[] Make(string clip) => TestPdf.Page($"{paint} q {Placement} cm {clip} /Im0 Do Q", Resources + " /Pattern << /P 6 0 R >>", 180, 180,
            [stencil, RegionTests.Obj("/Type /Pattern /PatternType 1 /PaintType 1 /TilingType 1 /BBox [0 0 8 8] /XStep 8 /YStep 8 /Resources << >>", "0.2 0.4 0.6 rg 0 0 8 8 re f")]);
        Equal(Render(Make("")), Render(Make("0 0 1 1 re W n")));
    }

    [Fact]
    public void ContainmentRejectsCurvesHolesConcavityAndRepeatedWindings()
    {
        DrawingPath quad = DrawingPath.Rectangle(0, 0, 1, 1);
        Assert.False(ImageClip.Contains(DrawingPath.Ellipse(-2, -2, 5, 5), quad));
        Assert.False(ImageClip.Contains(new PathBuilder().AddPath(DrawingPath.Rectangle(-1, -1, 3, 3)).AddPath(quad).Build(), quad));
        Assert.False(ImageClip.Contains(DrawingPath.Polygon([new(-1, -1), new(2, -1), new(2, 2), new(0.5f, 0.5f), new(-1, 2)]), quad));
        Assert.False(ImageClip.Contains(DrawingPath.Polygon([new(0, 0), new(1, 0), new(1, 1), new(0, 1), new(0, 0), new(1, 0), new(1, 1), new(0, 1)]), quad));
        Assert.False(ImageClip.Contains(DrawingPath.Polygon([new(0, -2), new(1, 2), new(-2, -1), new(2, -1), new(-1, 2)]), quad));
    }

    [Theory]
    [InlineData("0.25 0.25 0.5 0.5 re W n")]
    [InlineData("0 0 0.75 1 re W n")]
    [InlineData("2 2 1 1 re W n")]
    [InlineData("1.0001 0 1 1 re W n")]
    [InlineData("0.9999 0 1 1 re W n")]
    [InlineData("0 0 1 1 re 0.25 0.25 0.5 0.5 re W* n")]
    [InlineData("0 0 m 1 0 l 1 1 l 0.5 0.5 l 0 1 l h W n")]
    [InlineData("0 0 m 1 0 1 1 0 1 c h W n")]
    [InlineData("0 0 m 1 0 l 1 1 l 0 1 l 0 0 l 1 0 l 1 1 l 0 1 l h W* n")]
    public void FallbackClipsMatchExistingPathClipping(string clip)
    {
        byte[] path = TestPdf.Page($"q {Placement} cm {clip} 0.11764705882352941 0.09803921568627451 0.13725490196078433 rg 0 0 1 1 re f Q", width: 180, height: 180);
        Equal(Render(path), Render(Page(clip)));
    }

    [Fact]
    public void ContainmentHasNoExpansionAndAcceptsReversedOrClosedPolygons()
    {
        DrawingPath quad = DrawingPath.Rectangle(0, 0, 1, 1);
        Assert.True(ImageClip.Contains(quad, quad));
        Assert.True(ImageClip.Contains(quad.Reverse(), quad));
        Assert.True(ImageClip.Contains(new PathBuilder().MoveTo(0, 0).LineTo(1, 0).LineTo(1, 1).LineTo(0, 1).LineTo(0, 0).Close().Build(), quad));
        Assert.False(ImageClip.Contains(DrawingPath.Rectangle(0, 0, MathF.BitDecrement(1), 1), quad));
        Assert.False(ImageClip.Contains(DrawingPath.Rectangle(float.Epsilon, 0, 1, 1), quad));
        Assert.False(ImageClip.Contains(DrawingPath.Rectangle(0, 0, 0, 1), quad));
    }

    [Fact]
    public void ComplexityAndCoordinateBoundsUseAConservativeFallback()
    {
        Vector2[] Polygon(int count) => Enumerable.Range(0, count).Select(i =>
            new Vector2((float)(100 * Math.Cos(2 * Math.PI * i / count)), (float)(100 * Math.Sin(2 * Math.PI * i / count)))).ToArray();
        DrawingPath quad = DrawingPath.Rectangle(-1, -1, 2, 2);
        Assert.True(ImageClip.Contains(DrawingPath.Polygon(Polygon(8)), quad));
        Assert.False(ImageClip.Contains(DrawingPath.Polygon(Polygon(9)), quad));
        Assert.False(ImageClip.Contains(DrawingPath.Polygon(Polygon(64)), quad));
        Assert.False(ImageClip.Contains(DrawingPath.Polygon(Polygon(65)), quad));
        Assert.False(ImageClip.Contains(DrawingPath.Polygon(Polygon(1024)), quad));
        const float bound = 1 << 24;
        DrawingPath large = DrawingPath.Rectangle(-bound, -bound, 2 * bound, 2 * bound);
        Assert.True(ImageClip.Contains(large, quad));
        Assert.True(ImageClip.Contains(large, large));
    }


    [Theory]
    [InlineData("opaque")]
    [InlineData("image-alpha")]
    [InlineData("alpha-blend")]
    [InlineData("soft-mask")]
    [InlineData("isolated")]
    [InlineData("nonisolated")]
    [InlineData("knockout")]
    public void TransparentBackgroundKeepsColorAndAlpha(string kind)
    {
        Rgba32[] Make(string clip) => RenderTests.Load(Page(clip, kind: kind, transparent: true), new PdfRenderOptions
        {
            Dpi = 96,
            Background = new Rgba32(0, 0, 0, 0),
        }).ToArray<Rgba32>(maxDegree: 1);
        Rgba32[] expected = Make("");
        Assert.Contains(expected, p => p.A > 0 && p.A < 255);
        Equal(expected, Make("0 0 1 1 re W n"));
    }

}
