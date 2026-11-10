using OneImage.Pdf.Render;
namespace OneImage.Pdf.Tests;
public class CanvasLayerBrushTests
{
    [Theory]
    [InlineData(false, false)]
    [InlineData(true, false)]
    [InlineData(false, true)]
    [InlineData(true, true)]
    public void MatchesImageMasksForEveryAlphaPair(bool useShape, bool useMask)
    {
        const int width = 280, height = 280;
        var region = new ImageRect(11, 17, 256, 256);
        using var source = new Canvas(width, height, PixelFormat.Rgba8);
        using var shape = new Canvas(width, height, PixelFormat.Rgba8);
        using var mask = new Canvas(width, height, PixelFormat.Rgba8);
        var pixels = new Rgba32[256 * 256];
        var shapePixels = new Rgba32[pixels.Length];
        var maskPixels = new Rgba32[pixels.Length];
        for (int y = 0; y < 256; y++)
            for (int x = 0; x < 256; x++)
            {
                int index = (y * 256) + x;
                pixels[index] = new Rgba32((byte)(x ^ y), (byte)y, (byte)(255 - x), (byte)x);
                shapePixels[index] = new Rgba32(255, 255, 255, (byte)y);
                maskPixels[index] = new Rgba32(255, 255, 255, (byte)((37 * x) + (19 * y)));
            }
        source.CopyFrom<Rgba32>(pixels, region);
        shape.CopyFrom<Rgba32>(shapePixels, region);
        mask.CopyFrom<Rgba32>(maskPixels, region);
        Image reference = source.Snapshot();
        if (useShape) reference = reference.ApplyMask(shape.Snapshot(), MaskChannel.Alpha);
        if (useMask) reference = reference.ApplyMask(mask.Snapshot(), MaskChannel.Alpha);
        var expected = new Rgba32[pixels.Length];
        reference.CopyPixelsTo<Rgba32>(expected, region, maxDegree: 1);
        using var brush = new CanvasLayerBrush(source, useShape ? shape : null, useMask ? mask : null, region);
        var row = new float[256 * 4];
        var expectedRow = new float[row.Length];
        const float scale = 1f / 255f;
        for (int y = 0; y < 256; y++)
        {
            brush.FillRow(region.X, region.Y + y, row);
            for (int x = 0; x < 256; x++)
            {
                Rgba32 p = expected[(y * 256) + x];
                expectedRow[x * 4] = p.R * scale;
                expectedRow[(x * 4) + 1] = p.G * scale;
                expectedRow[(x * 4) + 2] = p.B * scale;
                expectedRow[(x * 4) + 3] = p.A * scale;
            }
            Assert.True(expectedRow.AsSpan().SequenceEqual(row), $"Mask output differs on row {y}.");
        }
    }
    [Theory]
    [InlineData(0, 20, 16)]
    [InlineData(25, 20, 16)]
    [InlineData(11, 16, 4)]
    [InlineData(11, 27, 4)]
    [InlineData(int.MinValue, 20, 16)]
    [InlineData(int.MaxValue, 20, 16)]
    [InlineData(12, int.MinValue, 16)]
    public void OutsideCoordinatesAreTransparent(int x, int y, int count)
    {
        using var source = new Canvas(64, 64, PixelFormat.Rgba8);
        var color = new Rgba32(20, 40, 60, 80);
        source.Clear(color);
        var region = new ImageRect(11, 17, 20, 10);
        using var brush = new CanvasLayerBrush(source, null, null, region);
        var actual = new float[count * 4];
        Array.Fill(actual, 123f);
        brush.FillRow(x, y, actual);
        const float scale = 1f / 255f;
        for (int i = 0; i < count; i++)
        {
            long px = (long)x + i;
            bool inside = px >= region.X && px < region.Right && y >= region.Y && y < region.Bottom;
            Rgba32 expected = inside ? color : default;
            Assert.Equal(expected.R * scale, actual[i * 4]);
            Assert.Equal(expected.G * scale, actual[(i * 4) + 1]);
            Assert.Equal(expected.B * scale, actual[(i * 4) + 2]);
            Assert.Equal(expected.A * scale, actual[(i * 4) + 3]);
        }
    }
    [Fact]
    public void BackdropCopyMatchesSrcPaintingForEveryColorAndAlpha()
    {
        var region = new ImageRect(11, 17, 256, 256);
        using var source = new Canvas(280, 280, PixelFormat.Rgba8);
        using var expected = new Canvas(280, 280, PixelFormat.Rgba8);
        using var actual = new Canvas(280, 280, PixelFormat.Rgba8);
        var pixels = new Rgba32[256 * 256];
        for (int alpha = 0; alpha < 256; alpha++)
            for (int color = 0; color < 256; color++)
                pixels[alpha * 256 + color] = new Rgba32((byte)color, (byte)(255 - color), (byte)(color ^ alpha), (byte)alpha);
        source.CopyFrom<Rgba32>(pixels, region);
        expected.Fill(OneImage.Drawing.Brush.FromImage(source.Snapshot(), tile: false), OneImage.Drawing.Path.Rectangle(region.X, region.Y, region.Width, region.Height), antialias: false, composition: AlphaComposition.Src);
        CanvasDevice.CopyBackdrop(actual, source, region);
        var expectedPixels = new Rgba32[pixels.Length];
        var actualPixels = new Rgba32[pixels.Length];
        expected.CopyTo<Rgba32>(expectedPixels, region);
        actual.CopyTo<Rgba32>(actualPixels, region);
        Assert.True(expectedPixels.AsSpan().SequenceEqual(actualPixels));
    }
    [Fact]
    public void BackdropCopyOnlyChangesTheRequestedRegionWithinOneTile()
    {
        var region = new ImageRect(11, 17, 20, 10);
        using var source = new Canvas(64, 64, PixelFormat.Rgba8);
        using var expected = new Canvas(64, 64, PixelFormat.Rgba8);
        using var actual = new Canvas(64, 64, PixelFormat.Rgba8);
        source.Clear(new Rgba32(23, 87, 190, 57));
        expected.Clear(new Rgba32(129, 64, 19, 147));
        actual.Clear(new Rgba32(129, 64, 19, 147));
        expected.Fill(OneImage.Drawing.Brush.FromImage(source.Snapshot(), tile: false), OneImage.Drawing.Path.Rectangle(region.X, region.Y, region.Width, region.Height), antialias: false, composition: AlphaComposition.Src);
        CanvasDevice.CopyBackdrop(actual, source, region);
        var expectedPixels = new Rgba32[64 * 64];
        var actualPixels = new Rgba32[expectedPixels.Length];
        var whole = new ImageRect(0, 0, 64, 64);
        expected.CopyTo<Rgba32>(expectedPixels, whole);
        actual.CopyTo<Rgba32>(actualPixels, whole);
        Assert.True(expectedPixels.AsSpan().SequenceEqual(actualPixels));
    }
}
