using System.Buffers;
using System.Numerics;
using System.Runtime.InteropServices;
using OneImage.Kernels;
using OnePdf;

namespace OneImage.Pdf.Render;

/// <summary>
/// Draws a rectangle of a page by drawing fixed 128 x 128 cells on the cell grid and cutting the rectangle out of them. Because a cell is
/// always drawn the same way (same origin, same display list items, same arithmetic), a pixel does not depend on which rectangle was
/// asked for, or on how many threads were asking: a region is byte for byte the same as that part of a whole render.
/// </summary>
internal static class CellRenderer
{
    public const int Cell = 128;

    public static void Render(PageRender page, int targetWidth, int targetHeight, ImageRect region, IRowSink sink, CancellationToken ct)
    {
        page.Prepare(ct);
        PdfPageInfo info = page.Info;
        double sx = targetWidth / info.Width, sy = targetHeight / info.Height;
        int firstCol = region.X / Cell, lastCol = (region.Right - 1) / Cell;
        int rowBytes = region.Width * 4;
        byte[] cell = Pools<byte>.Pool.Rent(Cell * Cell * 4);
        byte[] band = Pools<byte>.Pool.Rent(Math.Min(Cell, region.Height) * rowBytes);
        try
        {
            for (int cy = (region.Y / Cell) * Cell; cy < region.Bottom; cy += Cell)
            {
                ct.ThrowIfCancellationRequested();
                int y0 = Math.Max(cy, region.Y), y1 = Math.Min(cy + Cell, region.Bottom);
                int rows = y1 - y0;
                for (int col = firstCol; col <= lastCol; col++)
                {
                    int cx = col * Cell;
                    DrawCell(page, sx, sy, cx, cy, cell, ct);
                    int x0 = Math.Max(cx, region.X), x1 = Math.Min(cx + Cell, region.Right);
                    int bytes = (x1 - x0) * 4;
                    for (int r = 0; r < rows; r++)
                    {
                        cell.AsSpan((((y0 - cy) + r) * Cell + (x0 - cx)) * 4, bytes).CopyTo(band.AsSpan((r * rowBytes) + ((x0 - region.X) * 4)));
                    }
                }

                sink.WriteRows(y0 - region.Y, band.AsSpan(0, rows * rowBytes), rows);
            }
        }
        finally
        {
            Pools<byte>.Pool.Return(cell);
            Pools<byte>.Pool.Return(band);
        }
    }

    /// <summary>Draws the cell whose top-left pixel is (<paramref name="cx"/>, <paramref name="cy"/>) into <paramref name="output"/> (128 x 128 straight RGBA).</summary>
    internal static void DrawCell(PageRender page, double sx, double sy, int cx, int cy, byte[] output, CancellationToken ct)
    {
        // A pixel of slack on every side keeps anti-aliased edges of items just outside the cell.
        var cull = new PdfBounds((cx - 1.5) / sx, (cy - 1.5) / sy, (cx + Cell + 1.5) / sx, (cy + Cell + 1.5) / sy);
        var view = new PdfMatrix(sx, 0, 0, sy, -cx, -cy);
        using var canvas = new Canvas(Cell, Cell, PixelFormat.Rgba8);
        var device = new CanvasDevice(page, view, canvas, depth: 0, tint: null, ct);
        try
        {
            page.List.Replay(device, cull);
        }
        finally
        {
            device.Dispose();
        }

        // The page begins with a transparent backdrop. A viewer background is not PDF content and must
        // not participate in its blend modes; composite it behind the completed page instead.
        Span<byte> bytes = output.AsSpan(0, Cell * Cell * 4);
        canvas.CopyToBytes(bytes, new ImageRect(0, 0, Cell, Cell));
        CompositeDisplayBackground(MemoryMarshal.Cast<byte, Rgba32>(bytes), page.Options.Background);
    }

    /// <summary>Normal destination-over on straight RGBA8 page pixels, after every PDF operation is finished.</summary>
    internal static void CompositeDisplayBackground(Span<Rgba32> pixels, Rgba32 background)
    {
        if (background.A == 0) return;
        ReadOnlySpan<float> table = ConvertFast.ByteToUnit;
        float ba = table[background.A];
        bool opaqueBackground = background.A == 255;
        float br = table[background.R] * ba, bg = table[background.G] * ba, bb = table[background.B] * ba;
        Span<uint> packed = MemoryMarshal.Cast<Rgba32, uint>(pixels);
        var alphaMask = new Vector<uint>(0xff000000u);
        var display = new Vector<uint>((uint)background.R | ((uint)background.G << 8) | ((uint)background.B << 16) | ((uint)background.A << 24));
        int i = 0;
        while (i < pixels.Length)
        {
            int end = pixels.Length;
            if (Vector.IsHardwareAccelerated && BitConverter.IsLittleEndian && i <= pixels.Length - Vector<uint>.Count)
            {
                end = i + Vector<uint>.Count;
                var values = new Vector<uint>(packed.Slice(i, Vector<uint>.Count));
                Vector<uint> alphaBytes = values & alphaMask;
                if (Vector.EqualsAll(alphaBytes, alphaMask))
                {
                    i = end;
                    continue;
                }

                Vector<uint> empty = Vector.Equals(alphaBytes, Vector<uint>.Zero);
                Vector<uint> opaque = Vector.Equals(alphaBytes, alphaMask);
                // Most page pixels are empty or fully opaque. Resolve those lanes together without
                // changing any color/alpha arithmetic for partially covered pixels.
                if (Vector.EqualsAll(empty | opaque, new Vector<uint>(uint.MaxValue)))
                {
                    Vector.ConditionalSelect(empty, display, values).CopyTo(packed.Slice(i, Vector<uint>.Count));
                    i = end;
                    continue;
                }
            }

            for (; i < end; i++)
            {
                Rgba32 p = pixels[i];
                if (p.A == 255) continue;
                if (p.A == 0)
                {
                    pixels[i] = background;
                    continue;
                }

                // Match Canvas.Fill's straight-byte -> premultiplied-float -> DestOver -> straight-byte
                // operation order. Doing this in the output buffer avoids a second full-cell raster fill.
                float pa = table[p.A], factor = 1f + (-1f * pa);
                float r = (br * factor) + (table[p.R] * pa);
                float g = (bg * factor) + (table[p.G] * pa);
                float b = (bb * factor) + (table[p.B] * pa);
                // For an opaque background the generic float alpha is exactly 1 for every byte alpha.
                // Keep its RGB operation order, but avoid three divisions by one and alpha conversion.
                if (opaqueBackground)
                {
                    pixels[i] = new Rgba32(ConvertFast.ToByte(r), ConvertFast.ToByte(g), ConvertFast.ToByte(b), 255);
                    continue;
                }

                float alpha = (ba * factor) + pa;
                pixels[i] = new Rgba32(ConvertFast.ToByte(r / alpha), ConvertFast.ToByte(g / alpha),
                    ConvertFast.ToByte(b / alpha), ConvertFast.ToByte(alpha));
            }
        }
    }
}
