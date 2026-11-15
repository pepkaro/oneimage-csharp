// SPDX-License-Identifier: MIT
// Copyright (c) 2026 OneImage contributors
// Original numeric geometry; no reference-engine output, third-party documents, or assets.
using OneImage.Pdf.Render;
using OnePdf;
using static OneImage.Pdf.Tests.SpecTruth.Spec;

namespace OneImage.Pdf.Tests.SpecTruth;

public class TinyPositiveStrokeTests
{
    [Theory]
    [InlineData("48.00000001", 72)]
    [InlineData("48.00000001", 144)]
    [InlineData("48.0000000001", 72)]
    [InlineData("48.0000000001", 144)]
    [InlineData("48.000001", 144)]
    [InlineData("48.000002", 144)]
    [InlineData("48.000004", 144)]
    public void PositiveClosedDashRetainsItsDirectionalHalfCaps(string end, int dpi)
    {
        int s = dpi / 72;
        Rgba32[] pixels = Pix(Page($"0 G 18 w 1 J [11 17] 3 d 48 36 m {end} 36 l h S", w: 96, h: 72), new PdfRenderOptions { Dpi = dpi });
        double area = BlackArea(pixels, 96 * s, 0, 0, 96 * s, 72 * s) / (s * s);
        Assert.InRange(area, (Math.PI * 81 / 2) - 3.5, (Math.PI * 81 / 2) + 0.5);
        Pixel(pixels, 96 * s, 44 * s, 35 * s, Gray(0), Tol.Exact);
        Pixel(pixels, 96 * s, 52 * s, 35 * s, Gray(1), Tol.Exact);
    }

    [Theory]
    [InlineData("", 1, 250, 256)]
    [InlineData("h", 1, 124, 130)]
    [InlineData("", 2, 320, 328)]
    [InlineData("h", 2, 158, 166)]
    [InlineData("", 0, 0, 0.1)]
    [InlineData("h", 0, 0, 0.1)]
    public void CapsAreNotUniversallyReplacedByACircle(string close, int cap, double lo, double hi)
    {
        var options = new PdfRenderOptions { Dpi = 144 };
        Rgba32[] pixels = Pix(Page($"0 G 18 w {cap} J [11 17] 3 d 48 36 m 48.00000001 36 l {close} S", w: 96, h: 72), options);
        Assert.InRange(BlackArea(pixels, 192, 0, 0, 192, 144) / 4, lo, hi);
    }

    [Theory]
    [InlineData("[11 17] 19 d")]
    [InlineData("[11 17] 11 d")]
    [InlineData("[0 7] 1 d")]
    public void PositiveMovementInsideAGapRemainsBlank(string dash)
    {
        Rgba32[] pixels = Pix(Page($"0 G 18 w 1 J {dash} 48 36 m 48.00000001 36 l h S", w: 96, h: 72));
        Assert.Equal(0, BlackArea(pixels, 96, 0, 0, 96, 72));
    }

    [Theory]
    [InlineData("0 0 m .00000001 0 l h", "1 0 0 1 48 36 cm")]
    [InlineData("1000000 1000000 m 1000000.00000001 1000000 l h", "1 0 0 1 -999952 -999964 cm")]
    [InlineData("-48 -36 m -47.99999999 -36 l h", "1 0 0 1 96 72 cm")]
    public void TranslationAndSmallPositiveLengthDoNotChangeTheLimitShape(string path, string transform)
    {
        const string style = "0 G 18 w 1 J [11 17] 3 d ";
        Assert.Equal(Pix(Page(style + "48 36 m 48.00000001 36 l h S", w: 96, h: 72)),
            Pix(Page(style + transform + " " + path + " S", w: 96, h: 72)));
    }

    [Theory]
    [InlineData("48 36 m 48.00000001 36 l h", "48 36 m 48.00000001 36 l 48 36 l")]
    [InlineData("48 36 m 48.00000001 36 l h 48 44 l", "48 36 m 48.00000001 36 l 48 36 l 48 36 m 48 44 l")]
    [InlineData("48 36 m 48.00000001 36 l h 60 36 m 60.00000001 36 l h", "48 36 m 48.00000001 36 l 48 36 l 60 36 m 60.00000001 36 l 60 36 l")]
    public void CloseAndFollowingCommandsMatchExplicitOpenSeams(string closed, string open)
    {
        const string style = "0 G 18 w 1 J [11 17] 3 d ";
        Assert.Equal(Pix(Page(style + open + " S", w: 96, h: 72)), Pix(Page(style + closed + " S", w: 96, h: 72)));
    }

    [Theory]
    [InlineData("", 18)]
    [InlineData("-1 0 0 1 96 0 cm", 18)]
    [InlineData("1.5 .3 .25 .8 -33 -7.2 cm", 18)]
    [InlineData("1.5 .3 .25 .8 -33 -7.2 cm", 0)]
    [InlineData("", 0.01)]
    public void TransformAndHairlinePoliciesMatchOpenSeams(string transform, double width)
    {
        string style = $"0 G {transform} {N(width)} w 1 J [11 17] 3 d ";
        var options = new PdfRenderOptions { Dpi = 144 };
        Assert.Equal(Pix(Page(style + "48 36 m 48.00000001 36 l 48 36 l S", w: 96, h: 72), options),
            Pix(Page(style + "48 36 m 48.00000001 36 l h S", w: 96, h: 72), options));
    }

    [Fact]
    public void TinyCubicOutAndBackRetainsItsTangents()
    {
        const string style = "0 G 18 w 1 J [11 17] 3 d ";
        Rgba32[] pixels = Pix(Page(style + "48 36 m 48.00000001 36 48.00000001 36 48 36 c h S", w: 96, h: 72));
        Assert.InRange(BlackArea(pixels, 96, 0, 0, 96, 72), 124, 130);
        Pixel(pixels, 96, 44, 35, Gray(0), Tol.Exact);
        Pixel(pixels, 96, 52, 35, Gray(1), Tol.Exact);
    }
    [Theory]
    [InlineData(1e-10)]
    [InlineData(1e-30)]
    [InlineData(1e-100)]
    [InlineData(1e-300)]
    public void RendererPreservesPositiveDoublesIndependentlyOfDecimalParsing(double displacement)
    {
        // Raw device input deliberately bypasses the separate PDF lexer decimal-precision boundary.
        Rgba32[] pixels = Raw([0, 0, displacement, 0], new PdfMatrix(1, 0, 0, 1, 48, 36));
        Assert.InRange(BlackArea(pixels, 96, 0, 0, 96, 72), 124, 130);
        Pixel(pixels, 96, 44, 35, Gray(0), Tol.Exact);
        Pixel(pixels, 96, 52, 35, Gray(1), Tol.Exact);
    }

    [Theory]
    [InlineData(double.NaN)]
    [InlineData(double.PositiveInfinity)]
    [InlineData(double.MaxValue)]
    public void NonfiniteAndUnrepresentableSourceCoordinatesStillDrawNothing(double invalid)
    {
        Rgba32[] pixels = Raw([48, 36, 48.00000001, 36, invalid, 36], PdfMatrix.Identity);
        Assert.Equal(0, BlackArea(pixels, 96, 0, 0, 96, 72));
    }

    [Theory]
    [InlineData(0, 1, 48, 40, 48, 32)]
    [InlineData(0, -1, 48, 32, 48, 40)]
    [InlineData(-1, 0, 52, 35, 44, 35)]
    [InlineData(1, 1, 44, 40, 52, 32)]
    public void PositiveDirectionsDetermineWhichHalfOfTheCapIsPainted(double dx, double dy, int blackX, int blackY, int whiteX, int whiteY)
    {
        Rgba32[] pixels = Raw([0, 0, dx * 1e-10, dy * 1e-10], new PdfMatrix(1, 0, 0, -1, 48, 36));
        Assert.InRange(BlackArea(pixels, 96, 0, 0, 96, 72), 123, 131);
        Pixel(pixels, 96, blackX, blackY, Gray(0), Tol.Exact);
        Pixel(pixels, 96, whiteX, whiteY, Gray(1), Tol.Exact);
    }

    [Theory]
    [InlineData("[0 7] 0 d")]
    [InlineData("[11 17] 10.999999995 d")]
    public void AZeroDashOrDashBoundaryInsideTheSegmentStillGetsBothCaps(string dash)
    {
        Rgba32[] pixels = Pix(Page($"0 G 18 w 1 J {dash} 48 36 m 48.00000001 36 l h S", w: 96, h: 72));
        Assert.InRange(BlackArea(pixels, 96, 0, 0, 96, 72), 248, 257);
    }

    [Fact]
    public void PrecisionRouteHonorsCancellationBeforeRendering()
    {
        using var cancellation = new CancellationTokenSource();
        cancellation.Cancel();
        Assert.Throws<OperationCanceledException>(() => Raw([48, 36, 48.00000001, 36], PdfMatrix.Identity, ct: cancellation.Token));
    }

    [Theory]
    [InlineData("[] 0 d")]
    [InlineData("[0 0] 0 d")]
    [InlineData("[.00001 .00001] 0 d")]
    public void SolidAndNormalizedSolidKeepTheExistingCollapsedClosedCap(string dash)
    {
        Rgba32[] pixels = Pix(Page($"0 G 18 w 1 J {dash} 48 36 m 48.00000001 36 l h S", w: 96, h: 72));
        Assert.InRange(BlackArea(pixels, 96, 0, 0, 96, 72), 248, 257);
    }

    [Theory]
    [InlineData("[11 17 23] 3 d", 124, 130)]
    [InlineData("[11 17 23] 19 d", 0, 0)]
    [InlineData("[11 0] 0 d", 124, 130)]
    public void OddAndZeroGapPatternsUseTheExistingNormalization(string dash, double lo, double hi)
    {
        Rgba32[] pixels = Pix(Page($"0 G 18 w 1 J {dash} 48 36 m 48.00000001 36 l h S", w: 96, h: 72));
        Assert.InRange(BlackArea(pixels, 96, 0, 0, 96, 72), lo, hi);
    }

    [Theory]
    [InlineData("12 20 m 12 60 80 60 80 20 c")]
    [InlineData("12 20 m 12.00000001 20 80 60 80 20 c")]
    public void UnrelatedTinyFigureDoesNotChangeOrdinaryBezierPixels(string curve)
    {
        const string style = "0 G 6 w 1 J [11 17] 3 d ";
        Rgba32[] ordinary = Pix(Page(style + curve + " S", w: 192, h: 144));
        Rgba32[] mixed = Pix(Page(style + curve + " 150 100 m 150.00000001 100 l h S", w: 192, h: 144));
        for (int y = 70; y < 144; y++)
        {
            Assert.True(ordinary.AsSpan(y * 192, 100).SequenceEqual(mixed.AsSpan(y * 192, 100)));
        }

        Assert.InRange(BlackArea(mixed, 192, 140, 30, 160, 55), 12, 15);
    }

    [Fact]
    public void TranslucentFillStrokeAndOverlappingFiguresPaintOneStrokeObject()
    {
        const string resources = "/ExtGState << /G << /ca .5 /CA .5 >> >>";
        const string content = "/G gs 0 g 0 G 18 w 1 J [11 17] 3 d 48 36 m 48.00000001 36 l h 48 36 m 48.00000001 36 l h ";
        Rgba32[] filled = Pix(Page(content + "B", resources, w: 96, h: 72));
        Rgba32[] stroked = Pix(Page(content + "S", resources, w: 96, h: 72));
        Assert.Equal(stroked, filled);
        Pixel(filled, 96, 44, 35, Gray(.5), Tol.One);
        Pixel(filled, 96, 52, 35, Gray(1), Tol.Exact);
    }

    [Fact]
    public void TinyCubicAtZeroOriginKeepsTheSameDirectionalCaps()
    {
        byte[] verbs = [(byte)PdfPathVerb.Move, (byte)PdfPathVerb.Curve, (byte)PdfPathVerb.Close];
        Rgba32[] actual = Raw([0, 0, 1e-8, 0, 1e-8, 0, 0, 0], new PdfMatrix(1, 0, 0, 1, 48, 36), commands: verbs);
        Assert.InRange(BlackArea(actual, 96, 0, 0, 96, 72), 124, 130);
        Pixel(actual, 96, 44, 35, Gray(0), Tol.Exact);
        Pixel(actual, 96, 52, 35, Gray(1), Tol.Exact);
    }

    [Fact]
    public void HairlineCurveInAffectedFigureUsesTheDirectionalTransformBound()
    {
        // x(t) = .15*t*(1-t)*(1-2*t) reaches +/-sqrt(3)/120. The 1000x horizontal
        // scale makes the excursion almost 29 pixels long even though det(CTM)=1. A mean-scale
        // flattening tolerance reduces this curve to its stationary midpoint/chord instead.
        byte[] verbs = [(byte)PdfPathVerb.Move, (byte)PdfPathVerb.Line, (byte)PdfPathVerb.Curve, (byte)PdfPathVerb.Close];
        Rgba32[] actual = Raw([0, 0, 1e-10, 0, .05, .01, -.05, .01, 0, 0],
            new PdfMatrix(1000, 0, 0, .001, 48, 36), commands: verbs, width: 0);
        Assert.InRange(BlackArea(actual, 96, 0, 0, 96, 72), 28, 30);
        Assert.True(actual[(36 * 96) + 36].R < 240);
        Assert.True(actual[(36 * 96) + 59].R < 240);
    }

    [Theory]
    [InlineData(.4)]
    [InlineData(-.4)]
    public void ShearedHairlineKeepsTheOrdinaryCurveResult(double skew)
    {
        // This is an equivalence/non-regression control, not a reference-image or area assertion. The core's
        // near-overlapping sheared hairline outline has a separately retained area-loss reproduction.
        byte[] verbs = [(byte)PdfPathVerb.Move, (byte)PdfPathVerb.Line, (byte)PdfPathVerb.Curve, (byte)PdfPathVerb.Close];
        var matrix = new PdfMatrix(1000, skew, 0, .001, 48, 36);
        Rgba32[] precise = Raw([0, 0, 1e-10, 0, .05, .01, -.05, .01, 0, 0], matrix, commands: verbs, width: 0);
        Rgba32[] ordinary = Raw([0, 0, .05, .01, -.05, .01, 0, 0], matrix,
            commands: [(byte)PdfPathVerb.Move, (byte)PdfPathVerb.Curve, (byte)PdfPathVerb.Close], width: 0);
        Assert.Equal(ordinary, precise);
    }

    private static Rgba32[] Raw(double[] points, PdfMatrix matrix, byte[]? commands = null, double width = 18, CancellationToken ct = default)
    {
        byte[] verbs = new byte[(points.Length / 2) + 1];
        Array.Fill(verbs, (byte)PdfPathVerb.Line);
        verbs[0] = (byte)PdfPathVerb.Move;
        verbs[^1] = (byte)PdfPathVerb.Close;
        verbs = commands ?? verbs;
        using PdfDocument document = PdfDocument.Open(Page("", w: 96, h: 72));
        var page = new PageRender(document.Pages[0], new PdfRenderOptions { Dpi = 72 });
        using var canvas = new Canvas(96, 72, PixelFormat.Rgba8);
        canvas.Clear(new Rgba32(255, 255, 255, 255));
        using var device = new CanvasDevice(page, PdfMatrix.Identity, canvas, 0, null, ct);
        var black = new PdfColor(PdfColorSpace.Gray, 0, 0, 0, 0, null);
        var state = new PdfGraphicsState(matrix, black, black, width, 1, 0, 10,
            new double[] { 11, 17 }, 3, 1, "RelativeColorimetric", 1, 1, "Normal", 0, false, false, false, 0);
        device.StrokePath(new PdfPath(verbs, points), state);
        return canvas.Snapshot().ToArray<Rgba32>(cancellationToken: ct);
    }

}
