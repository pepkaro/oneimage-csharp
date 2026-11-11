using OneImage.Pdf.Render;

namespace OneImage.Pdf.Tests;

public class NonIsolatedGroupBrushTests
{
    [Theory]
    [InlineData(false)]
    [InlineData(true)]
    public void RowCoordinatesAreClippedAndConcurrentReadsAreDeterministic(bool interpolate)
    {
        var region = new ImageRect(11, 17, 20, 10);
        using var source = new Canvas(64, 64, PixelFormat.Rgba8);
        using var shape = new Canvas(64, 64, PixelFormat.Rgba8);
        using var mask = new Canvas(64, 64, PixelFormat.Rgba8);
        source.Clear(new Rgba32(170, 85, 43, 192));
        shape.Clear(new Rgba32(255, 255, 255, 128));
        mask.Clear(new Rgba32(255, 255, 255, 128));
        using var brush = new NonIsolatedGroupBrush(source, shape, mask, region, 0.5f, interpolate);
        float[] backdrop = [0.4f, 0.2f, 0.1f, 0.5f];
        var inside = new float[4];
        brush.FillRow(11, 17, backdrop, inside);
        Assert.All(inside, value => Assert.True(float.IsFinite(value)));
        (int X, int Y)[] coordinates = [(0, 20), (25, 20), (11, 16), (11, 27), (int.MinValue, 20), (int.MaxValue, 20), (12, int.MinValue), (12, int.MaxValue), (11, 17)];
        Parallel.For(0, 64, pass =>
        {
            (int x, int y) = coordinates[pass % coordinates.Length];
            var backgrounds = new float[16 * 4];
            for (int i = 0; i < 16; i++) backdrop.CopyTo(backgrounds, i * 4);
            var actual = new float[backgrounds.Length];
            Array.Fill(actual, float.NaN);
            brush.FillRow(x, y, backgrounds, actual);
            for (int i = 0; i < 16; i++)
            {
                long column = (long)x + i;
                bool covered = column >= region.X && column < region.Right && y >= region.Y && y < region.Bottom;
                for (int c = 0; c < 4; c++)
                    Assert.Equal(covered ? inside[c] : interpolate ? backdrop[c] : 0, actual[(i * 4) + c]);
            }
        });
    }
}
