using OneImage.Pdf.Render;
namespace OneImage.Pdf.Tests;
public class CanvasLayerBrushTests
{
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
