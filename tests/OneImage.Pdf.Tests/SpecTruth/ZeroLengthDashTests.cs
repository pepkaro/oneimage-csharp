// SPDX-License-Identifier: MIT
// Copyright (c) 2026 OneImage contributors
// Independently authored numeric geometry. No external PDF, font, image or reference pixels.
using static OneImage.Pdf.Tests.SpecTruth.Spec;

namespace OneImage.Pdf.Tests.SpecTruth;

/// <summary>ISO 32000-1 8.4.3.6 and 8.5.3.2: degenerate round-capped subpaths still obey the dash pattern.</summary>
public class ZeroLengthDashTests
{
    // The phase selects the interval beginning at that distance, including exact boundaries. An odd pattern's
    // on/off cycle repeats twice; zero-length on entries still contribute a cap at their exact position.
    public static TheoryData<string, bool> Patterns => new()
    {
        { "[] 0 d", true },
        { "[11 17] 0 d", true }, { "[11 17] 3 d", true }, { "[11 17] 10.999 d", true },
        { "[11 17] 11 d", false }, { "[11 17] 11.001 d", false }, { "[11 17] 19 d", false },
        { "[11 17] 27.999 d", false }, { "[11 17] 28 d", true }, { "[11 17] 31 d", true },
        { "[11 17] 39 d", false }, { "[11 17] 56 d", true }, { "[11 17] 59 d", true },
        { "[7 5 9] 6 d", true }, { "[7 5 9] 7 d", false }, { "[7 5 9] 12 d", true },
        { "[7 5 9] 20 d", true }, { "[7 5 9] 21 d", false }, { "[7 5 9] 23 d", false },
        { "[7 5 9] 28 d", true }, { "[7 5 9] 33 d", false }, { "[7 5 9] 41 d", false },
        { "[7 5 9] 42 d", true }, { "[7 5 9] 49 d", false }, { "[7 5 9] 54 d", true },
        { "[0 17] 0 d", true }, { "[0 17] 1 d", false }, { "[0 17] 17 d", true },
        { "[0 17] 28 d", false }, { "[0 17] 34 d", true },
        { "[11 0] 0 d", true }, { "[11 0] 11 d", true }, { "[11 0] 17 d", true },
        { "[0 0 11 17] 0 d", true }, { "[0 0 11 17] 11 d", false },
        { "[11 0 0 17] 11 d", true }, { "[11 0 0 17] 17 d", false },
        { "[0 0 0 17] 0 d", true }, { "[0 0 0 17] 34 d", true },
        { "[0 17 0] 17 d", true }, { "[0 17 0] 28 d", true }, { "[0 17 0] 35 d", false },
    };

    [Theory]
    [MemberData(nameof(Patterns))]
    [Trait("Section", "8.4.3.6")]
    public void DegenerateRoundCapFollowsDashPhase(string dash, bool painted)
    {
        Rgba32[] actual = Pix(Page($"0 G 18 w 1 J {dash} 48 36 m 48 36 l S", w: 96, h: 72));
        Rgba32[] expected = Pix(Page(painted ? "0 G 18 w 1 J 48 36 m 48 36 l S" : "", w: 96, h: 72));
        Assert.Equal(expected, actual);
        double area = BlackArea(actual, 96, 0, 0, 96, 72);
        if (painted)
        {
            // A 0.1-pixel flattening error bounds disc-area loss by perimeter * 0.1, less than 6.
            Assert.InRange(area, (Math.PI * 81) - 6, (Math.PI * 81) + 1);
        }
        else
        {
            Assert.Equal(0, area);
        }
    }

    [Theory]
    [InlineData("48 36 m h")]
    [InlineData("48 36 m 48 36 l h")]
    [InlineData("48 36 m 48 36 48 36 48 36 c")]
    [InlineData("48 36 0 0 re")]
    [InlineData("48 36 m 48 36 l 48 36 l")]
    [Trait("Section", "8.5.3.2")]
    public void AllDegenerateSubpathFormsObeyTheDash(string path)
    {
        Rgba32[] solid = Pix(Page($"0 G 18 w 1 J {path} S", w: 96, h: 72));
        Rgba32[] on = Pix(Page($"0 G 18 w 1 J [11 17] 3 d {path} S", w: 96, h: 72));
        Rgba32[] off = Pix(Page($"0 G 18 w 1 J [11 17] 19 d {path} S", w: 96, h: 72));
        // The solid closed-subpath geometry is an independent control, not the oracle for dash visibility.
        Assert.Contains(solid, p => p.R != 255);
        Assert.InRange(BlackArea(on, 96, 0, 0, 96, 72), (Math.PI * 81) - 6, (Math.PI * 81) + 1);
        Assert.Equal(0, BlackArea(off, 96, 0, 0, 96, 72));
    }

    [Theory]
    [InlineData("", 18)]
    [InlineData("1.5 0.3 0.25 0.8 -33 -7.2 cm", 18)]
    [InlineData("", 0)]
    [InlineData("1.5 0.3 0.25 0.8 -33 -7.2 cm", 0)]
    [InlineData("-1 0 0 1 96 0 cm", 18)]
    public void TransformAndHairlineDoNotChangeDashSelection(string transform, int width)
    {
        string body = $"0 G {transform} {width} w 1 J 48 36 m 48 36 l S";
        Rgba32[] solid = Pix(Page(body, w: 96, h: 72), new PdfRenderOptions { Dpi = 144 });
        Rgba32[] on = Pix(Page("[11 17] 3 d " + body, w: 96, h: 72), new PdfRenderOptions { Dpi = 144 });
        Rgba32[] off = Pix(Page("[11 17] 19 d " + body, w: 96, h: 72), new PdfRenderOptions { Dpi = 144 });
        Assert.Equal(solid, on);
        Assert.Contains(on, p => p.R != 255);
        Assert.All(off, p => Assert.Equal(new Rgba32(255, 255, 255, 255), p));
    }

    [Theory]
    [InlineData(3)]
    [InlineData(19)]
    public void EachSubpathRestartsThePhase(int phase)
    {
        string setup = $"0 G 6 w 1 J [11 17] {phase} d ";
        const string first = "9 12 m 26 12 l";
        const string second = "48 36 m 48 36 l";
        const string third = "75 57 m 75 57 l";
        Rgba32[] combined = Pix(Page(setup + first + " " + second + " " + third + " S", w: 96, h: 72));
        Rgba32[] separate = Pix(Page(setup + first + " S " + second + " S " + third + " S", w: 96, h: 72));
        Assert.Equal(separate, combined);
        Pixel(combined, 96, 48, 35, phase == 3 ? Gray(0) : Gray(1), Tol.Exact);
        Pixel(combined, 96, 75, 14, phase == 3 ? Gray(0) : Gray(1), Tol.Exact);
    }

    [Theory]
    [InlineData(0)]
    [InlineData(2)]
    public void ButtAndSquareCapsStillLeaveDegenerateSubpathsUnpainted(int cap)
    {
        foreach (string dash in new[] { "[] 0 d", "[11 17] 3 d", "[11 17] 19 d" })
        {
            Assert.Equal(0, BlackArea(Pix(Page($"0 G 18 w {cap} J {dash} 48 36 m 48 36 l S", w: 96, h: 72)), 96, 0, 0, 96, 72));
        }
    }

    [Fact]
    public void MoveOnlyIsNotADegenerateStroke()
    {
        foreach (string dash in new[] { "[] 0 d", "[11 17] 3 d", "[0 17] 0 d" })
        {
            Assert.Equal(0, BlackArea(Pix(Page($"0 G 18 w 1 J {dash} 48 36 m S", w: 96, h: 72)), 96, 0, 0, 96, 72));
        }
    }

    [Fact]
    public void PositiveLengthAndZeroLengthDashControlsRemainDistinct()
    {
        const string tiny = "48 36 m 48.125 36 l S";
        Assert.Equal(0, BlackArea(Pix(Page("0 G 18 w 1 J [11 17] 19 d " + tiny, w: 96, h: 72)), 96, 0, 0, 96, 72));
        double on = BlackArea(Pix(Page("0 G 18 w 1 J [11 17] 3 d " + tiny, w: 96, h: 72)), 96, 0, 0, 96, 72);
        Assert.InRange(on, (Math.PI * 81) + (18 * 0.125) - 6, (Math.PI * 81) + (18 * 0.125) + 1);
        Assert.Equal(Pix(Page("0 G 18 w 1 J " + tiny, w: 96, h: 72)),
            Pix(Page("0 G 18 w 1 J [11 17] 3 d " + tiny, w: 96, h: 72)));
        // Zero-length dashes on a nondegenerate path get square caps; zero-length subpaths do not.
        Rgba32[] dots = Pix(Page("0 G 4 w 2 J [0 17] 0 d 13 36 m 65 36 l S", w: 96, h: 72));
        Assert.Equal(64, BlackArea(dots, 96, 0, 0, 96, 72), 6);
    }

    [Theory]
    [InlineData(1)]
    [InlineData(4)]
    [InlineData(16)]
    public void DegenerateCapsAreRegionAndThreadDeterministic(int degree)
    {
        byte[] pdf = Page("0 G 22 w 1 J [11 17] 19 d 127 129 m 127 129 l 257 257 m 257 257 l S " +
            "[0 17] 0 d 129 127 m 129 127 l 255 255 m 255 255 l S", w: 384, h: 384);
        Image img = RenderTests.Load(pdf, new PdfRenderOptions { Dpi = 72 });
        Rgba32[] whole = img.ToArray<Rgba32>(maxDegree: 1);
        Assert.Equal(whole, RenderTests.Load(pdf, new PdfRenderOptions { Dpi = 72 }).ToArray<Rgba32>(maxDegree: degree));
        var region = new ImageRect(111, 111, 162, 162);
        var part = new Rgba32[region.Width * region.Height];
        RenderTests.Load(pdf, new PdfRenderOptions { Dpi = 72 }).CopyPixelsTo<Rgba32>(part, region, degree);
        for (int y = 0; y < region.Height; y++)
        {
            Assert.True(part.AsSpan(y * region.Width, region.Width).SequenceEqual(whole.AsSpan(((y + region.Y) * 384) + region.X, region.Width)));
        }
    }
}
