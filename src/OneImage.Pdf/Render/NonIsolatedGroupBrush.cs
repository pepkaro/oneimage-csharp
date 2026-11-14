using OneImage.Drawing;

namespace OneImage.Pdf.Render;

/// <summary>Removes the initial backdrop from a non-isolated group's result (ISO 32000-2 11.4.8).</summary>
internal sealed class NonIsolatedGroupBrush : Brush, IDisposable
{
    private readonly ImageRect _region;
    private readonly PixelLock<Rgba32> _source;
    private readonly PixelLock<Rgba32> _shape;
    private readonly PixelLock<Rgba32>? _mask;
    private readonly float _opacity;
    private readonly bool _interpolate;

    public NonIsolatedGroupBrush(Canvas source, Canvas shape, Canvas? mask, ImageRect region, float opacity, bool interpolate)
    {
        _region = region;
        _opacity = opacity;
        _interpolate = interpolate;
        _source = source.Lock<Rgba32>(region, LockAccess.Read);
        try
        {
            _shape = shape.Lock<Rgba32>(region, LockAccess.Read);
            _mask = mask?.Lock<Rgba32>(region, LockAccess.Read);
        }
        catch
        {
            _shape?.Dispose();
            _source.Dispose();
            throw;
        }
    }

    // The parent does not change while the group paints. Fill supplies its original pixels per run,
    // avoiding a read lock on the same canvas that Fill writes (single-tile locks are live views).
    public override bool ReadsBackdrop => true;

    public override void FillRow(int x, int y, Span<float> rgba) => rgba.Clear();

    public override void FillRow(int x, int y, ReadOnlySpan<float> backdrop, Span<float> rgba)
    {
        if (_interpolate) backdrop.CopyTo(rgba);
        else rgba.Clear();
        long column = (long)x - _region.X, row = (long)y - _region.Y;
        int count = rgba.Length / 4;
        if (row < 0 || row >= _region.Height) return;
        int first = (int)Math.Clamp(-column, 0, count);
        int last = (int)Math.Clamp(_region.Width - column, 0, count);
        if (first >= last) return;
        ReadOnlySpan<Rgba32> source = _source.ReadRow((int)row);
        ReadOnlySpan<Rgba32> shape = _shape.ReadRow((int)row);
        ReadOnlySpan<Rgba32> mask = _mask is null ? default : _mask.ReadRow((int)row);
        const float scale = 1f / 255f;
        for (int i = first; i < last; i++)
        {
            int at = (int)(column + i), offset = i * 4;
            float groupAlpha = shape[at].A * scale;
            float amount = _opacity * (_mask is null ? 1 : mask[at].A * scale);
            if (groupAlpha == 0 || amount == 0) continue;
            Rgba32 result = source[at];
            float resultAlpha = result.A * scale, backdropAlpha = backdrop[offset + 3];
            if (_interpolate)
            {
                // For Normal, Pb + m * (Pr - Pb) is equivalent to recovering the group then
                // painting it, without division by tiny group alpha and its rounding amplification.
                float alpha = backdropAlpha + (amount * (resultAlpha - backdropAlpha));
                float from = (1 - amount) * backdropAlpha, to = amount * resultAlpha * scale;
                rgba[offset] = alpha > 0 ? ((backdrop[offset] * from) + (result.R * to)) / alpha : 0;
                rgba[offset + 1] = alpha > 0 ? ((backdrop[offset + 1] * from) + (result.G * to)) / alpha : 0;
                rgba[offset + 2] = alpha > 0 ? ((backdrop[offset + 2] * from) + (result.B * to)) / alpha : 0;
                rgba[offset + 3] = alpha;
            }
            else
            {
                // Pg = Pr - (1 - ag) * Pb. External blending needs the unassociated group color,
                // not the result color containing the backdrop, and alpha ag rather than ar * ag.
                float retained = (1 - groupAlpha) * backdropAlpha;
                rgba[offset] = Math.Clamp(((result.R * scale * resultAlpha) - (backdrop[offset] * retained)) / groupAlpha, 0, 1);
                rgba[offset + 1] = Math.Clamp(((result.G * scale * resultAlpha) - (backdrop[offset + 1] * retained)) / groupAlpha, 0, 1);
                rgba[offset + 2] = Math.Clamp(((result.B * scale * resultAlpha) - (backdrop[offset + 2] * retained)) / groupAlpha, 0, 1);
                rgba[offset + 3] = groupAlpha * amount;
            }
        }
    }

    public void Dispose()
    {
        _mask?.Dispose();
        _shape.Dispose();
        _source.Dispose();
    }
}
