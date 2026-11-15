// SPDX-License-Identifier: MIT
// Copyright (c) 2026 OneImage contributors
// Original numeric geometry and analytical controls; no external assets or expected pixels.
using OneImage.Drawing;
using Path = OneImage.Drawing.Path;
using PathBuilder = OneImage.Drawing.PathBuilder;

namespace OneImage.Tests.Drawing;

public class ClosedDashTests
{
    [Theory]
    [InlineData(3)]
    [InlineData(10.75)] // The dash ends exactly where this figure closes.
    [InlineData(31)]
    [InlineData(-25)]
    public void WholeOnFigureHasOnlyItsOriginalVertices(double phase)
    {
        double[] points = [48, 36, 48.125, 36];
        var sink = new Capture();
        new DashSplitter([11, 17], phase).Split(points, 2, true, sink);
        var piece = Assert.Single(sink.Pieces);
        Assert.True(piece.Closed);
        Assert.Equal(points, piece.Points);
    }

    [Fact]
    public void InitialOffIntervalLeavesTheFinalDashOpen()
    {
        // Perimeter 40; phase 65 skips the first 15 units, then paints the remaining 25.
        var sink = new Capture();
        new DashSplitter([60, 20], 65).Split([20, 20, 30, 20, 30, 30, 20, 30], 4, true, sink);
        var piece = Assert.Single(sink.Pieces);
        Assert.False(piece.Closed);
        Assert.Equal(new double[] { 30, 25, 30, 30, 20, 30, 20, 20 }, piece.Points);
    }

    public static TheoryData<int, StrokeJoin, StrokeCap> WholeFigures
    {
        get
        {
            var data = new TheoryData<int, StrokeJoin, StrokeCap>();
            foreach (int shape in new[] { 0, 1, 2, 3, 4 })
            foreach (StrokeJoin join in Enum.GetValues<StrokeJoin>())
            foreach (StrokeCap cap in Enum.GetValues<StrokeCap>())
            {
                data.Add(shape, join, cap);
            }

            return data;
        }
    }

    [Theory]
    [MemberData(nameof(WholeFigures))]
    public void WholeOnOutlineIsExactlyTheSolidOutline(int shape, StrokeJoin join, StrokeCap cap)
    {
        Path path = shape switch
        {
            0 => new PathBuilder().MoveTo(48, 36).LineTo(48.125f, 36).Close().Build(),
            1 => new PathBuilder().MoveTo(48, 36).CubicBezierTo(49, 36, 47, 36, 48, 36).Close().Build(),
            2 => Path.Rectangle(24, 24, 8, 6),
            3 => Path.Polygon([new(22, 24), new(35, 25), new(29, 37)]),
            // Figure.Dedupe must remove both the consecutive repeat and explicit closing vertex before Split.
            _ => new PathBuilder().MoveTo(48, 36).LineTo(48.125f, 36).LineTo(48, 36).LineTo(48, 36).Close().Build(),
        };
        Path solid = path.GenerateOutline(18, join, cap);
        Path dashed = path.GenerateOutline(18, join, cap, dashPattern: [200, 17], dashOffset: 3);
        Assert.Equal(solid.Verbs.ToArray(), dashed.Verbs.ToArray());
        Assert.Equal(solid.Coords.ToArray(), dashed.Coords.ToArray());
        Assert.All(dashed.Coords.ToArray(), c => Assert.True(float.IsFinite(c)));
        Assert.False(dashed.IsEmpty);
    }

    [Theory]
    [InlineData(StrokeCap.Butt)]
    [InlineData(StrokeCap.Round)]
    [InlineData(StrokeCap.Square)]
    public void InitialGapMatchesAnExplicitOpenDash(StrokeCap cap)
    {
        Path closed = Path.Rectangle(20, 20, 10, 10);
        Path painted = new PathBuilder().MoveTo(30, 25).LineTo(30, 30).LineTo(20, 30).LineTo(20, 20).Build();
        Path expected = painted.GenerateOutline(4, cap: cap);
        Path actual = closed.GenerateOutline(4, cap: cap, dashPattern: [60, 20], dashOffset: 65);
        Assert.Equal(expected.Verbs.ToArray(), actual.Verbs.ToArray());
        Assert.Equal(expected.Coords.ToArray(), actual.Coords.ToArray());
    }

    [Fact]
    public void RealBooleanCoordinateLimitIsStillEnforced()
    {
        Path path = new PathBuilder().MoveTo(40_000_000, 36).LineTo(40_000_032, 36).Close().Build();
        Assert.Throws<ImageLimitException>(() => path.GenerateOutline(18, dashPattern: [200, 17]));
    }

    private sealed class Capture : IDashSink
    {
        public List<(double[] Points, bool Closed)> Pieces { get; } = [];

        public void Dash(double[] xy, int count, bool closed, double dirX, double dirY) =>
            Pieces.Add((xy.AsSpan(0, 2 * count).ToArray(), closed));
    }
}
