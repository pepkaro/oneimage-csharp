using System.Numerics;
using OneImage.Drawing;
using Path = OneImage.Drawing.Path;

namespace OneImage.Tests.Drawing;

/// <summary>Device-space stroke centerlines retain the path transform's finite-coordinate contract.</summary>
public class StrokeTransformTests
{
    [Fact]
    public void NonfiniteCenterlineMatricesAreRejected()
    {
        Path path = Path.Polyline([new(1, 1), new(2, 2)]);
        Matrix3x2[] matrices =
        [
            new(float.PositiveInfinity, 0, 0, 1, 0, 0),
            new(1, float.NaN, 0, 1, 0, 0),
            new(1, 0, 0, 1, float.PositiveInfinity, 0),
        ];
        foreach (Matrix3x2 map in matrices)
        {
            Assert.Throws<ImageOperationException>(() => StrokeBuilder.Build(path, 1, StrokeJoin.Miter, StrokeCap.Butt,
                10, [], 0, 0.1, map));
        }
    }

    [Fact]
    public void MappedCoordinatesOutsideFloatRangeAreRejected()
    {
        Path path = Path.Polyline([new(2, 2), new(3, 4)]);
        var map = new Matrix3x2(float.MaxValue, 0, 0, 1, 0, 0);
        Assert.Throws<ImageOperationException>(() => StrokeBuilder.Build(path, 1, StrokeJoin.Miter, StrokeCap.Butt,
            10, [], 0, 0.1, map));
    }

    [Theory]
    [InlineData(StrokeCap.Butt, true)]
    [InlineData(StrokeCap.Round, false)]
    [InlineData(StrokeCap.Square, true)]
    public void FullyCollapsedSolidCenterlineHasOnlyARoundCap(StrokeCap cap, bool empty)
    {
        Path path = Path.Polyline([new(4, 6), new(6, 4)]);
        var map = new Matrix3x2(1, 1, 1, 1, 0, 0);
        Path outline = StrokeBuilder.Build(path, 1, StrokeJoin.Miter, cap, 10, [], 0, 0.1, map);
        Assert.Equal(empty, outline.IsEmpty);
        if (!empty)
        {
            Assert.InRange(outline.Bounds.Width, 0.9f, 1.1f);
            Assert.InRange(outline.Bounds.Height, 0.9f, 1.1f);
        }
    }

    [Theory]
    [InlineData(StrokeCap.Butt)]
    [InlineData(StrokeCap.Round)]
    [InlineData(StrokeCap.Square)]
    public void CollapsedClosedAllOnDashMatchesSolidContour(StrokeCap cap)
    {
        Path path = new PathBuilder().MoveTo(4, 6).LineTo(6, 4).Close().Build();
        var map = new Matrix3x2(1, 1, 1, 1, 0, 0);
        Path solid = StrokeBuilder.Build(path, 1, StrokeJoin.Miter, cap, 10, [], 0, 0.1, map);
        Path dashed = StrokeBuilder.Build(path, 1, StrokeJoin.Miter, cap, 10, [100, 1], 0, 0.1, map);
        Assert.Equal(solid.Verbs, dashed.Verbs);
        Assert.Equal(solid.Coords, dashed.Coords);
    }

}
