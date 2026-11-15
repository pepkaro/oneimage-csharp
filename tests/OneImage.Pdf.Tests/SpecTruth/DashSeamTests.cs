// SPDX-License-Identifier: MIT
// Copyright (c) 2026 OneImage contributors
// Independently authored numeric geometry; no reference pixels or external assets.
using static OneImage.Pdf.Tests.SpecTruth.Spec;

namespace OneImage.Pdf.Tests.SpecTruth;

public class DashSeamTests
{
    [Theory]
    [InlineData(72)]
    [InlineData(144)]
    public void TinyOutAndBackDashHasOneHalfDiscAtTheSeam(int dpi)
    {
        // Both round caps face left at the same origin. Their union is one half-disc, plus the narrow rectangle.
        int scale = dpi / 72;
        Rgba32[] pixels = Pix(Page("0 G 18 w 1 J [11 17] 3 d 48 36 m 48.125 36 l h S", w: 96, h: 72), new PdfRenderOptions { Dpi = dpi });
        double area = BlackArea(pixels, 96 * scale, 0, 0, 96 * scale, 72 * scale) / (scale * scale);
        double exact = (Math.PI * 81 / 2) + (18 * 0.125);
        // A 0.1-pixel flattening error along the semicircle permits less than 3 square points of loss;
        // the slightly wider bound also covers coordinate snapping and byte coverage rounding.
        Assert.InRange(area, exact - 3.5, exact + 0.5);
        Pixel(pixels, 96 * scale, 44 * scale, 35 * scale, Gray(0), Tol.Exact);
        Pixel(pixels, 96 * scale, 52 * scale, 35 * scale, Gray(1), Tol.Exact);
    }

    public static TheoryData<string, string, int, int> SeamCases
    {
        get
        {
            var data = new TheoryData<string, string, int, int>();
            var shapes = new (string Closed, string Open)[]
            {
                ("48 36 m 48.125 36 l h", "48 36 m 48.125 36 l 48 36 l"),
                ("48 36 m 49 36 47 36 48 36 c h", "48 36 m 49 36 47 36 48 36 c"),
                ("24 24 8 6 re", "24 24 m 32 24 l 32 30 l 24 30 l 24 24 l"),
                ("22 24 m 35 25 l 29 37 l h", "22 24 m 35 25 l 29 37 l 22 24 l"),
            };
            foreach (var shape in shapes)
            foreach (int cap in new[] { 0, 1, 2 })
            foreach (int dpi in new[] { 72, 144 })
            {
                data.Add(shape.Closed, shape.Open, cap, dpi);
            }

            return data;
        }
    }

    [Theory]
    [MemberData(nameof(SeamCases))]
    public void WholeOnDashCapsTheSeamLikeTheExplicitOpenPath(string closed, string open, int cap, int dpi)
    {
        var options = new PdfRenderOptions { Dpi = dpi };
        string setup = $"0 G 18 w {cap} J ";
        Assert.Equal(Pix(Page(setup + open + " S", w: 96, h: 72), options),
            Pix(Page(setup + "[200 17] 3 d " + closed + " S", w: 96, h: 72), options));
    }

    [Theory]
    [InlineData("[12 7] 3 d")]
    [InlineData("[7 5 9] 12 d")]
    [InlineData("[0 7] 0 d")]
    [InlineData("[12 0] 0 d")]
    [InlineData("[60 20] 65 d")]
    public void SeveralDashesDoNotJoinAcrossTheSeam(string dash)
    {
        const string closed = "24 24 8 6 re";
        const string open = "24 24 m 32 24 l 32 30 l 24 30 l 24 24 l";
        string setup = "0 G 4 w 1 J " + dash + " ";
        Assert.Equal(Pix(Page(setup + open + " S", w: 64, h: 64)),
            Pix(Page(setup + closed + " S", w: 64, h: 64)));
    }

    [Theory]
    [InlineData("[0 0] 0 d")]
    [InlineData("[.00001 .00001] 0 d")]
    public void NormalizedSolidFallbackKeepsTheClosedJoin(string dash)
    {
        const string body = "0 G 4 w 1 J 24 24 8 6 re S";
        Assert.Equal(Pix(Page(body, w: 64, h: 64)), Pix(Page(dash + " " + body, w: 64, h: 64)));
    }

    [Theory]
    [InlineData("", 18)]
    [InlineData("1.5 .3 .25 .8 -33 -7.2 cm", 18)]
    [InlineData("-1 0 0 1 96 0 cm", 18)]
    [InlineData("", 0)]
    [InlineData("1.5 .3 .25 .8 -33 -7.2 cm", 0)]
    [InlineData("", 0.01)]
    public void TransformAndWidthPoliciesPreserveCappedSeams(string transform, double width)
    {
        string setup = $"0 G {transform} {N(width)} w 1 J ";
        var options = new PdfRenderOptions { Dpi = 144 };
        Assert.Equal(Pix(Page(setup + "24 24 m 32 24 l 32 30 l 24 30 l 24 24 l S", w: 96, h: 72), options),
            Pix(Page(setup + "[200 17] 3 d 24 24 8 6 re S", w: 96, h: 72), options));
    }

    [Theory]
    [InlineData("24 24 8 6 re 50 20 l", "24 24 m 32 24 l 32 30 l 24 30 l 24 24 l 24 24 m 50 20 l")]
    [InlineData("24 24 8 6 re 60 30 m 80 40 l", "24 24 m 32 24 l 32 30 l 24 30 l 24 24 l 60 30 m 80 40 l")]
    [InlineData("24 24 8 6 re 40 40 8 6 re", "24 24 m 32 24 l 32 30 l 24 30 l 24 24 l 40 40 m 48 40 l 48 46 l 40 46 l 40 40 l")]
    public void LaterPathCommandsKeepTheirCurrentPointAndRestartDashPhase(string closed, string open)
    {
        const string setup = "0 G 4 w 1 J [12 7] 3 d ";
        Assert.Equal(Pix(Page(setup + open + " S", w: 96, h: 72)),
            Pix(Page(setup + closed + " S", w: 96, h: 72)));
    }
}
