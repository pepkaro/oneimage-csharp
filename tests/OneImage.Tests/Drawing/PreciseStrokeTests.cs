// SPDX-License-Identifier: MIT
// Copyright (c) 2026 OneImage contributors
using OneImage.Drawing;
using Path = OneImage.Drawing.Path;

namespace OneImage.Tests.Drawing;

public class PreciseStrokeTests
{
    [Fact]
    public void GenericCoreKeepsItsSmallSegmentDuplicatePolicy()
    {
        Path path = new PathBuilder().MoveTo(0, 0).LineTo(1e-10f, 0).Close().Build();
        Assert.True(StrokeBuilder.Build(path, 18, StrokeJoin.Miter, StrokeCap.Round, 10, [11, 17], 3, .1).IsEmpty);
        var dash = new DashSplitter([11, 17], 3, joinClosed: false);
        Assert.False(StrokeBuilder.BuildPrecise([0, 0, 1e-10, 0], true, 18, StrokeJoin.Miter, StrokeCap.Round, 10, dash, .1, null).IsEmpty);
    }

    [Fact]
    public void MixedRoutesShareTheConstructionBudgetBeforeResolvingOverlaps()
    {
        var budget = new StrokeBuilder.Budget { Verbs = 1, Coords = 2 };
        var dash = new DashSplitter([11, 17], 3, joinClosed: false);
        Assert.Throws<ImageLimitException>(() => StrokeBuilder.BuildPrecise([0, 0, 1e-10, 0], true, 18,
            StrokeJoin.Miter, StrokeCap.Round, 10, dash, .1, null, budget));
        Path path = new PathBuilder().MoveTo(0, 0).LineTo(10, 0).Build();
        Assert.Throws<ImageLimitException>(() => StrokeBuilder.Build(path, 18, StrokeJoin.Miter, StrokeCap.Round,
            10, .1, null, dash, Path.MaxFlattenedPoints, budget));
    }

    [Fact]
    public void OrdinaryFlattenerHonorsTheRemainingPointBudget()
    {
        Path path = new PathBuilder().MoveTo(0, 0).LineTo(10, 0).Build();
        Assert.Throws<ImageLimitException>(() => StrokeBuilder.Build(path, 18, StrokeJoin.Miter, StrokeCap.Round,
            10, .1, null, null, 1));
        Assert.False(StrokeBuilder.Build(path, 18, StrokeJoin.Miter, StrokeCap.Round,
            10, .1, null, null, 2).IsEmpty);
    }
}
