using OneImage.Drawing;
namespace OneImage.Pdf.Render;
/// <summary>Reads a finished RGBA canvas layer and its alpha masks directly. Canvases must remain unchanged until disposed.</summary>
internal sealed class CanvasLayerBrush : Brush, IDisposable
{
    private readonly ImageRect _region;
    private readonly PixelLock<Rgba32> _source;
    private readonly PixelLock<Rgba32>? _shape;
    private readonly PixelLock<Rgba32>? _mask;
    public CanvasLayerBrush(Canvas source, Canvas? shape, Canvas? mask, ImageRect region)
    {
        _region = region;
        _source = source.Lock<Rgba32>(region, LockAccess.Read);
        try
        {
            _shape = shape?.Lock<Rgba32>(region, LockAccess.Read);
            _mask = mask?.Lock<Rgba32>(region, LockAccess.Read);
        }
        catch
        {
            _shape?.Dispose();
            _source.Dispose();
            throw;
        }
    }
    public override void FillRow(int x, int y, Span<float> rgba)
    {
        int count = rgba.Length / 4;
        long column = (long)x - _region.X, row = (long)y - _region.Y;
        if (count == 0 || row < 0 || row >= _region.Height)
        {
            rgba.Clear();
            return;
        }
        if (column >= 0 && column + count <= _region.Width)
        {
            FillCoveredRow((int)column, (int)row, rgba);
            return;
        }
        // Arbitrary brush coordinates must not wrap or index outside the region.
        rgba.Clear();
        int first = (int)Math.Clamp(-column, 0, count);
        int last = (int)Math.Clamp(_region.Width - column, 0, count);
        if (first < last)
            FillCoveredRow((int)(column + first), (int)row, rgba.Slice(first * 4, (last - first) * 4));
    }
    private void FillCoveredRow(int column, int row, Span<float> rgba)
    {
        int count = rgba.Length / 4;
        ReadOnlySpan<Rgba32> source = _source.ReadRow(row).Slice(column, count);
        ReadOnlySpan<Rgba32> shape = _shape is null ? default : _shape.ReadRow(row).Slice(column, count);
        ReadOnlySpan<Rgba32> mask = _mask is null ? default : _mask.ReadRow(row).Slice(column, count);
        const float scale = 1f / 255f;
        for (int i = 0; i < count; i++)
        {
            Rgba32 p = source[i];
            int alpha = p.A;
            if (_shape is not null) alpha = MultiplyAlpha(alpha, shape[i].A);
            if (_mask is not null) alpha = MultiplyAlpha(alpha, mask[i].A);
            int offset = i * 4;
            // Retain ApplyMask's transparent black and per-mask 8-bit rounding order.
            if (alpha == 0 && (_shape is not null || _mask is not null))
            {
                rgba.Slice(offset, 4).Clear();
                continue;
            }
            rgba[offset] = p.R * scale;
            rgba[offset + 1] = p.G * scale;
            rgba[offset + 2] = p.B * scale;
            rgba[offset + 3] = alpha * scale;
        }
    }
    public void Dispose()
    {
        _mask?.Dispose();
        _shape?.Dispose();
        _source.Dispose();
    }
    private static int MultiplyAlpha(int alpha, int coverage)
    {
        int product = (alpha * coverage) + 128;
        return (product + (product >> 8)) >> 8;
    }
}
