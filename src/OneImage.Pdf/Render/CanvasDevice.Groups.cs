using OneImage.Drawing;
using OnePdf;
using DrawingPath = OneImage.Drawing.Path;

namespace OneImage.Pdf.Render;

internal sealed partial class CanvasDevice
{
    private enum FrameKind
    {
        /// <summary>A group painted straight onto its parent; nothing to composite at the end.</summary>
        Passthrough,
        Group,
        Mask,
    }

    private sealed class Frame(FrameKind kind, Canvas? layer, Canvas parent, double opacity, BlendMode blend, int maskId)
    {
        public FrameKind Kind { get; } = kind;

        public Canvas? Layer { get; set; } = layer;

        public Canvas Parent { get; } = parent;

        public double Opacity { get; } = opacity;

        public BlendMode Blend { get; } = blend;

        public int MaskId { get; } = maskId;

        public PdfSoftMaskInfo Info { get; init; }

        public ClipState SavedClip { get; init; } = ClipState.None;

        public int SavedClipCount { get; init; }

        public bool Knockout { get; init; }

        /// <summary>For a non-isolated group painted on a copy of its backdrop: what the group's own objects cover (their union alpha).</summary>
        public Canvas? Shape { get; set; }
        public ImageRect? CompositeRegion { get; init; }
    }

    private void CheckNesting()
    {
        // Layers, masks and pattern cells being drawn at once, across the whole chain of devices.
        if (_frames.Count + _depth >= Limits.MaxNesting)
        {
            throw new ImageLimitException($"Transparency groups, soft masks and patterns are nested deeper than {Limits.MaxNesting}.");
        }
    }

    public void BeginGroup(in PdfGroupInfo group, in PdfGraphicsState state)
    {
        CloseTextKnockout();
        BlendMode blend = ParseBlend(state.BlendMode);
        bool maskKnown = state.SoftMaskId != 0 && _masks.ContainsKey(state.SoftMaskId);
        if (!group.Isolated && !group.Knockout && state.FillAlpha >= 1 && blend == BlendMode.Normal && !maskKnown)
        {
            _frames.Add(new Frame(FrameKind.Passthrough, null, _target, 1, BlendMode.Normal, 0));
            return;
        }

        CheckNesting();
        var layer = new Canvas(_w, _h, PixelFormat.Rgba8);
        ImageRect region = GroupRegion(group.Bounds, state.Ctm.Then(_view));
        Canvas? shape = null;
        if (!group.Isolated && !group.Knockout)
        {
            // 11.4.5: a non-isolated group starts from its backdrop, so blend modes inside it see the page. The group's own coverage is
            // tracked apart, and at the end only that part of the result is composited, so the backdrop is not counted twice (11.4.8).
            // An opaque backdrop is assumed; a translucent one is approximated.
            CopyBackdrop(layer, _target, region);
            shape = new Canvas(_w, _h, PixelFormat.Rgba8);
        }

        _frames.Add(new Frame(FrameKind.Group, layer, _target, state.FillAlpha, blend, maskKnown ? state.SoftMaskId : 0) { Knockout = group.Knockout, Shape = shape, CompositeRegion = region });
        _target = layer;
    }

    private ImageRect GroupRegion(in PdfBounds bounds, in PdfMatrix matrix)
    {
        PdfBounds device = matrix.TransformBounds(bounds);
        if (!device.IsFinite) return new ImageRect(0, 0, _w, _h);
        // The form clip already applies fractional coverage. Round outward with one pixel of rasterizer slack.
        int x0 = (int)Math.Clamp(Math.Floor(device.Left) - 1, 0, _w);
        int y0 = (int)Math.Clamp(Math.Floor(device.Bottom) - 1, 0, _h);
        int x1 = (int)Math.Clamp(Math.Ceiling(device.Right) + 1, 0, _w);
        int y1 = (int)Math.Clamp(Math.Ceiling(device.Top) + 1, 0, _h);
        return new ImageRect(x0, y0, Math.Max(0, x1 - x0), Math.Max(0, y1 - y0));
    }
    internal static void CopyBackdrop(Canvas layer, Canvas source, ImageRect region)
    {
        if (region.IsEmpty) return;
        using PixelLock<Rgba32> input = source.Lock<Rgba32>(region, LockAccess.Read);
        using PixelLock<Rgba32> output = layer.Lock<Rgba32>(region, LockAccess.Write);
        for (int y = 0; y < region.Height; y++)
        {
            ReadOnlySpan<Rgba32> from = input.ReadRow(y);
            Span<Rgba32> to = output.GetRow(y);
            for (int x = 0; x < from.Length; x++)
            {
                Rgba32 pixel = from[x];
                // Src painting clears hidden RGB at alpha zero through premultiplied conversion.
                to[x] = pixel.A == 0 ? default : pixel;
            }
        }
    }
    /// <summary>The coverage canvas of the non-isolated group being painted directly into the current target, if any.</summary>
    private Canvas? ShapeShadow => _frames.Count > 0 && _frames[^1] is { Kind: FrameKind.Group, Shape: { } s } f && ReferenceEquals(f.Layer, _target) ? s : null;

    /// <summary>Opens a knockout layer composited with the state's blend mode and soft mask (not its opacity: objects carry their own).</summary>
    private void BeginKnockoutLayer(in PdfGraphicsState state)
    {
        BlendMode blend = ParseBlend(state.BlendMode);
        bool maskKnown = state.SoftMaskId != 0 && _masks.ContainsKey(state.SoftMaskId);
        CheckNesting();
        var layer = new Canvas(_w, _h, PixelFormat.Rgba8);
        _frames.Add(new Frame(FrameKind.Group, layer, _target, 1, blend, maskKnown ? state.SoftMaskId : 0) { Knockout = true });
        _target = layer;
    }

    /// <summary>True while painting directly into the layer of a knockout group, where each object replaces what is under it.</summary>
    private bool InKnockoutGroup => _frames.Count > 0 && _frames[^1] is { Kind: FrameKind.Group, Knockout: true } f && ReferenceEquals(f.Layer, _target);

    public void EndGroup()
    {
        CloseTextKnockout();
        int last = _frames.Count - 1;
        if (last < 0 || _frames[last].Kind == FrameKind.Mask)
        {
            return;
        }

        Frame f = _frames[last];
        _frames.RemoveAt(last);
        if (f.Kind == FrameKind.Passthrough)
        {
            return;
        }

        _target = f.Parent;
        Canvas layer = f.Layer!;
        f.Layer = null;
        CompositeLayer(layer, f.Opacity, f.Blend, f.MaskId, f.Shape, f.CompositeRegion);
    }

    /// <summary>Composites a finished layer onto the current target with an opacity, blend mode and (known) soft mask, and releases it.</summary>
    private void CompositeLayer(Canvas layer, double opacity, BlendMode blend, int maskId, Canvas? shape = null, ImageRect? region = null)
    {
        CanvasLayerBrush? brush = null;
        try
        {
            ImageRect rect = region ?? new ImageRect(0, 0, _w, _h);
            if (rect.IsEmpty) return;
            Canvas? mask = null;
            if (maskId != 0) _masks.TryGetValue(maskId, out mask);
            brush = new CanvasLayerBrush(layer, shape, mask, rect);
            DrawingPath area = DrawingPath.Rectangle(rect.X, rect.Y, rect.Width, rect.Height);
            _target.Fill(brush, area, antialias: false, opacity: (float)Math.Clamp(opacity, 0, 1), blend: blend, composition: AlphaComposition.SrcOver);
            ShapeShadow?.Fill(brush, area, antialias: false, opacity: (float)Math.Clamp(opacity, 0, 1), blend: BlendMode.Normal, composition: AlphaComposition.SrcOver);
        }
        finally
        {
            brush?.Dispose();
            shape?.Dispose();
            layer.Dispose();
        }
    }
    // ---- soft masks ----

    public void BeginSoftMask(in PdfSoftMaskInfo mask, in PdfGraphicsState state)
    {
        CloseTextKnockout();
        CheckNesting();
        var layer = new Canvas(_w, _h, PixelFormat.Rgba8);
        if (mask.Luminosity)
        {
            Rgba32 bc = Backdrop(mask.Backdrop);
            layer.Clear(bc);
        }

        // The mask is defined independently of the clip that happens to be in force where the mask is selected.
        _frames.Add(new Frame(FrameKind.Mask, layer, _target, 1, BlendMode.Normal, 0) { Info = mask, SavedClip = _clip, SavedClipCount = _clips.Count });
        _clip = ClipState.None;
        _target = layer;
    }

    public void EndSoftMask()
    {
        CloseTextKnockout();
        int last = _frames.Count - 1;
        if (last < 0 || _frames[last].Kind != FrameKind.Mask)
        {
            return;
        }

        Frame f = _frames[last];
        _frames.RemoveAt(last);
        _target = f.Parent;
        _clip = f.SavedClip;
        while (_clips.Count > f.SavedClipCount)
        {
            _clips.RemoveAt(_clips.Count - 1);
        }

        Canvas layer = f.Layer!;
        f.Layer = null;
        try
        {
            Canvas mask = BuildMask(layer, f.Info);
            if (_masks.Remove(f.Info.Id, out Canvas? old))
            {
                old.Dispose();
            }

            _masks[f.Info.Id] = mask;
        }
        finally
        {
            layer.Dispose();
        }
    }

    private Canvas BuildMask(Canvas layer, in PdfSoftMaskInfo info)
    {
        var pixels = new Rgba32[_w * _h];
        layer.CopyTo<Rgba32>(pixels, new ImageRect(0, 0, _w, _h));
        // OnePDF evaluates /TR into a byte lookup; null means identity.
        byte[]? transfer = info.TransferTable;
        for (int i = 0; i < pixels.Length; i++)
        {
            Rgba32 p = pixels[i];
            int v = info.Luminosity ? PdfColors.Luma(p) : p.A;
            pixels[i] = new Rgba32(255, 255, 255, transfer is null ? (byte)v : transfer[v]);
        }

        var mask = new Canvas(_w, _h, PixelFormat.Rgba8);
        mask.CopyFrom<Rgba32>(pixels, new ImageRect(0, 0, _w, _h));
        return mask;
    }

    private static Rgba32 Backdrop(PdfArray? bc)
    {
        if (bc is null || bc.Count == 0)
        {
            return new Rgba32(0, 0, 0, 255);
        }

        Span<double> c = stackalloc double[4];
        int n = Math.Min(bc.Count, 4);
        for (int i = 0; i < n; i++)
        {
            c[i] = bc.GetDouble(i);
        }

        PdfColorSpace space = n switch { 1 => PdfColorSpace.Gray, 3 => PdfColorSpace.Rgb, 4 => PdfColorSpace.Cmyk, _ => PdfColorSpace.Gray };
        return PdfColors.ToRgba(space, c[..space.ComponentCount]);
    }
}
