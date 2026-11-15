using System.Globalization;
using System.Text;
using static OneImage.Pdf.Tests.SpecTruth.Spec;

namespace OneImage.Pdf.Tests.SpecTruth;

/// <summary>Explicit zero-width strokes stay device-thin without moving user-space dash breaks (8.4.3.2).</summary>
public class HairlineTests
{
    [Theory]
    [InlineData("1 0 0 1 0 0", "3 10.5 m 17 10.5 l")]
    [InlineData("8 0 0 .125 0 0", ".375 84 m 2.125 84 l")]
    [InlineData("-8 0 0 .125 20 0", ".375 84 m 2.125 84 l")]
    [InlineData("0 8 -.125 0 20 0", "1.3125 136 m 1.3125 24 l")]
    [InlineData("1 0 4 1 0 0", "-39 10.5 m -25 10.5 l")]
    [Trait("Section", "8.4.3.2")]
    public void HorizontalHairlineHasOneDevicePixelWidth(string matrix, string path)
    {
        Check(Page($"{matrix} cm 0 w {path} S"), new Expected(20, 20).Rect(3, 10, 17, 11, Gray(0)), Tol.One);
    }

    [Theory]
    [InlineData("8 0 0 .125 0 0", "1.3125 24 m 1.3125 136 l")]
    [InlineData(".125 0 0 8 0 0", "84 .375 m 84 2.125 l")]
    [InlineData("1 0 4 1 0 0", "-1.5 3 m -57.5 17 l")]
    [Trait("Section", "8.4.3.2")]
    public void VerticalHairlineHasOneDevicePixelWidth(string matrix, string path)
    {
        Check(Page($"{matrix} cm 0 w {path} S"), new Expected(20, 20).Rect(10, 3, 11, 17, Gray(0)), Tol.One);
    }

    [Theory]
    [InlineData(0)]
    [InlineData(1)]
    [InlineData(2)]
    [Trait("Section", "8.4.3.6")]
    public void DashLengthsAndPhaseRemainInUserSpace(int cap)
    {
        // User-space on-runs [.5,1.25], [2.25,3.25], [4.25,4.5] map to [2,5], [9,13], [17,18].
        byte[] actual = Page($"4 0 0 .25 0 0 cm 0 w {cap} J [1 1] .25 d .5 42 m 4.5 42 l S");
        byte[] expected = Page($"0 w {cap} J 2 10.5 m 5 10.5 l 9 10.5 m 13 10.5 l 17 10.5 m 18 10.5 l S");
        Assert.Equal(Pix(expected), Pix(actual));
    }

    [Theory]
    [InlineData(1)]
    [InlineData(2)]
    [Trait("Section", "8.5.3.2")]
    public void ZeroLengthDashesUseDeviceSpaceCaps(int cap)
    {
        // Nonuniform scaling keeps each zero-length dash a device-size dot, with a transformed cap direction.
        byte[] actual = Page($"4 0 0 .25 0 0 cm 0 w {cap} J [0 1] 0 d .5 42 m 4.5 42 l S");
        byte[] expected = Page($"0 w {cap} J [0 4] 0 d 2 10.5 m 18 10.5 l S");
        Assert.Equal(Pix(expected), Pix(actual));
    }

    [Theory]
    [InlineData(0, 0)]
    [InlineData(0, 1)]
    [InlineData(0, 2)]
    [InlineData(1, 0)]
    [InlineData(1, 1)]
    [InlineData(1, 2)]
    [InlineData(2, 0)]
    [InlineData(2, 1)]
    [InlineData(2, 2)]
    [Trait("Section", "8.4.3.3")]
    public void ReparameterizingTheSamePolylinePreservesCapsAndJoins(int cap, int join)
    {
        string style = $"0 w {cap} J {join} j 4 M ";
        Rgba32[] expected = Pix(Page(style + "4 4 m 4 14 l 15 14 l 17 7 l S"));
        // A nonuniform scale and shear; these points map exactly to the control's device path.
        Rgba32[] actual = Pix(Page("4 0 2 .5 0 0 cm " + style + "-3 8 m -13 28 l -10.25 28 l -2.75 14 l S"));
        Assert.Equal(expected, actual);
    }

    [Theory]
    [InlineData(0)]
    [InlineData(1)]
    [InlineData(2)]
    [Trait("Section", "8.5.3.2")]
    public void ZeroLengthOpenSubpathPreservesDeviceCap(int cap)
    {
        Rgba32[] expected = Pix(Page($"0 w {cap} J 10.5 10.5 m 10.5 10.5 l S"));
        Rgba32[] actual = Pix(Page($"8 0 0 .125 0 0 cm 0 w {cap} J 1.3125 84 m 1.3125 84 l S"));
        Assert.Equal(expected, actual);
    }

    [Theory]
    [InlineData(0.25)]
    [InlineData(0.485)]
    [InlineData(0.75)]
    [Trait("Section", "8.4.3.2")]
    public void PositiveWidthEnhancementRemainsUnchanged(double width)
    {
        // Preserve the established positive-width minimum; changing it would be a separate rendering policy.
        Check(Page(string.Create(CultureInfo.InvariantCulture, $"{width} w 3 10.5 m 17 10.5 l S")),
            new Expected(20, 20).Rect(3, 10, 17, 11, Gray(0)), Tol.One);
    }

    [Fact]
    [Trait("Section", "8.5.4")]
    public void FractionalClipIntersectsTheDeviceHairline()
    {
        byte[] actual = Page("4.25 10.25 10.5 .5 re W n 8 0 0 .125 0 0 cm 0 w .375 84 m 2.125 84 l S");
        Check(actual, new Expected(20, 20).Rect(4.25, 10.25, 14.75, 10.75, Gray(0)), Tol.One);
    }

    [Theory]
    [InlineData(8, 0, 0, 0.125, false)]
    [InlineData(1, 0, 4, 1, false)]
    [InlineData(0, 8, -0.125, 0, false)]
    [InlineData(8, 0, 0, 0.125, true)]
    [InlineData(1, 0, 4, 1, true)]
    [InlineData(0, 8, -0.125, 0, true)]
    [Trait("Section", "8.4.3.2")]
    public void CurvesBoundDeviceSpaceErrorAndPreserveUserSpaceDashes(double a, double b, double c, double d, bool dashed)
    {
        double det = (a * d) - (b * c);
        (double X, double Y) User(double x, double y) => (((d * x) - (c * y)) / det, ((a * y) - (b * x)) / det);
        var p0 = User(4, 4);
        var p1 = User(4, 16);
        var p2 = User(16, 4);
        var p3 = User(16, 16);
        string prefix = string.Create(CultureInfo.InvariantCulture, $"{a} {b} {c} {d} 0 0 cm 0 w 1 J ")
            + (dashed ? "[2 1] .5 d " : string.Empty);
        string move = string.Create(CultureInfo.InvariantCulture, $"{p0.X} {p0.Y} m ");
        string cubic = string.Create(CultureInfo.InvariantCulture, $"{p1.X} {p1.Y} {p2.X} {p2.Y} {p3.X} {p3.Y} c S");
        var dense = new StringBuilder(prefix + move);
        // An independent dense polyline approximates both user-space arc length and the transformed cubic. It does not
        // use the curve flattener; dashes must be cut by user-space length before their centerlines are transformed.
        for (int i = 1; i <= 4096; i++)
        {
            double t = i / 4096.0, u = 1 - t;
            double x = (u * u * u * p0.X) + (3 * u * u * t * p1.X) + (3 * u * t * t * p2.X) + (t * t * t * p3.X);
            double y = (u * u * u * p0.Y) + (3 * u * u * t * p1.Y) + (3 * u * t * t * p2.Y) + (t * t * t * p3.Y);
            dense.Append(CultureInfo.InvariantCulture, $"{x} {y} l ");
        }

        dense.Append('S');
        Rgba32[] actual = Pix(Page(prefix + move + cubic));
        CoverageClose(actual, Pix(Page(dense.ToString())));
        if (!dashed)
        {
            // The same solid cubic transformed first, then stroked with one device pixel.
            CoverageClose(actual, Pix(Page("0 w 1 J 4 4 m 4 16 16 4 16 16 c S")), meanTolerance: 0.5);
        }
    }

    private static void CoverageClose(Rgba32[] actual, Rgba32[] expected, double meanTolerance = 0.3)
    {
        int maximum = 0;
        double sum = 0;
        for (int i = 0; i < actual.Length; i++)
        {
            int delta = Math.Abs(actual[i].R - expected[i].R);
            maximum = Math.Max(maximum, delta);
            sum += delta;
        }

        // Curved stroke tessellation is bounded in device space, not expected to be byte-identical after reparameterization.
        Assert.True(maximum <= 12 && sum / actual.Length <= meanTolerance,
            $"curve coverage differs by maximum {maximum}, mean {sum / actual.Length}");
    }

    [Theory]
    [InlineData(0, false)]
    [InlineData(1, false)]
    [InlineData(2, false)]
    [InlineData(0, true)]
    [InlineData(1, true)]
    [InlineData(2, true)]
    public void RoundedMatrixMayCollapseOnlyPartOfACenterline(int cap, bool closed)
    {
        // The double matrix has determinant 1e-8, but its float representation makes the first segment zero length.
        string end = closed ? "h S" : "S";
        Rgba32[] actual = Pix(Page($"1 1 1 1.00000001 0 0 cm 0 w {cap} J 4 6 m 6 4 l 10 5 l {end}"));
        Rgba32[] expected = Pix(Page($"0 w {cap} J 10 10 m 15 15 l {end}"));
        Assert.Equal(expected, actual);
    }

    private static byte[] BusyHairlines() => TestPdf.Page(
        "q 4 0 2 .25 -100 0 cm 0 w 1 J 1 j [7 3] 2 d 10 20 m 50 500 l 100 200 l 160 1000 l S Q " +
        "q 127.25 0 129.5 400 re W n 8 0 0 .125 0 0 cm 0 w 2 J [4 2] .5 d 0 1028 m 50 1028 l S Q " +
        "q 8 0 0 .125 0 0 cm 0 w 1 J 16 1024 m 16 1024 l S Q", width: 400, height: 400);

    [Fact]
    public void RegionsAndConcurrentReadsMatchTheWholePage()
    {
        byte[] pdf = BusyHairlines();
        Image Load() => RenderTests.Load(pdf, new PdfRenderOptions { Dpi = 96 });
        Image img = Load();
        Rgba32[] whole = Load().ToArray<Rgba32>(1);
        foreach (int degree in new[] { 1, 4, 16 })
        {
            Assert.Equal(whole, Load().ToArray<Rgba32>(degree));
        }

        ImageRect[] regions = [new(127, 127, 130, 130), new(255, 0, 3, img.Height), new(0, 255, img.Width, 3), new(31, 63, 257, 129)];
        Parallel.For(0, 16, i =>
        {
            ImageRect region = regions[i % regions.Length];
            Rgba32[] part = new Rgba32[region.Width * region.Height];
            (i < regions.Length ? Load() : img).CopyPixelsTo<Rgba32>(part, region);
            for (int y = 0; y < region.Height; y++)
            {
                Assert.True(part.AsSpan(y * region.Width, region.Width).SequenceEqual(
                    whole.AsSpan(((y + region.Y) * img.Width) + region.X, region.Width)));
            }
        });
    }
}
