// SPDX-License-Identifier: MIT
// Copyright (c) 2026 OneImage contributors
// Original numeric geometry. Expected images come from equivalent geometry, not reference pixels.
using static OneImage.Pdf.Tests.SpecTruth.Spec;

namespace OneImage.Pdf.Tests.SpecTruth;

/// <summary>PDF integration for closed-dash geometry safety and initial-gap handling (ISO 32000-1 8.4.3.6).</summary>
public class ClosedDashTests
{
    [Theory]
    [InlineData("48 36 m 48.125 36 l h", 72)]
    [InlineData("48 36 m 48.125 36 l h", 144)]
    [InlineData("48 36 m 49 36 47 36 48 36 c h", 72)]
    [InlineData("48 36 m 49 36 47 36 48 36 c h", 144)]
    public void PositiveClosedDashesRenderWithoutNonFiniteCoordinates(string path, int dpi)
    {
        // A PDF integration smoke test for the core coordinate failure, not a dash-seam pixel oracle.
        // The direct core tests verify exact outline geometry. PDF dash-seam semantics are a separate issue.
        Rgba32[] pixels = Pix(Page($"0 G 18 w 1 J [11 17] 3 d {path} S", w: 96, h: 72), new PdfRenderOptions { Dpi = dpi });
        Assert.Contains(pixels, p => p.R != 255);
        Assert.All(pixels, p => Assert.Equal((byte)255, p.A));
    }

    [Theory]
    [InlineData(0, 72)]
    [InlineData(1, 72)]
    [InlineData(2, 72)]
    [InlineData(0, 144)]
    [InlineData(1, 144)]
    [InlineData(2, 144)]
    public void InitialOffIntervalDoesNotCloseTheRemainingDash(int cap, int dpi)
    {
        var options = new PdfRenderOptions { Dpi = dpi };
        string setup = $"0 G 4 w {cap} J ";
        Rgba32[] expected = Pix(Page(setup + "30 25 m 30 30 l 20 30 l 20 20 l S", w: 64, h: 64), options);
        Rgba32[] actual = Pix(Page(setup + "[60 20] 65 d 20 20 10 10 re S", w: 64, h: 64), options);
        Assert.Equal(expected, actual);
    }

    [Theory]
    [InlineData(1)]
    [InlineData(4)]
    [InlineData(16)]
    public void ClosedDashesAreRegionAndThreadDeterministic(int degree)
    {
        byte[] pdf = Page("0 G 18 w 1 J [200 17] 3 d 127 129 m 127.125 129 l h " +
            "257 257 m 258 257 256 257 257 257 c h 121 121 8 6 re S " +
            "4 w [60 20] 65 d 250 250 10 10 re S", w: 384, h: 384);
        var options = new PdfRenderOptions { Dpi = 72 };
        Rgba32[] whole = RenderTests.Load(pdf, options).ToArray<Rgba32>(maxDegree: 1);
        Assert.Equal(whole, RenderTests.Load(pdf, options).ToArray<Rgba32>(maxDegree: degree));
        var region = new ImageRect(111, 111, 162, 162);
        var part = new Rgba32[region.Width * region.Height];
        RenderTests.Load(pdf, options).CopyPixelsTo<Rgba32>(part, region, degree);
        for (int y = 0; y < region.Height; y++)
        {
            Assert.True(part.AsSpan(y * region.Width, region.Width).SequenceEqual(whole.AsSpan(((y + region.Y) * 384) + region.X, region.Width)));
        }
    }
}
