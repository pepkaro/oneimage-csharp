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
        public bool AlphaIsShape { get; init; }
        /// <summary>Borrowed initial backdrop, unchanged while this frame is active; null means transparent.</summary>
        public Canvas? Backdrop { get; init; }
        /// <summary>Union of geometric shapes, independent of opacity, when an ancestor needs knockout shape.</summary>
        public Canvas? Geometry { get; set; }

        /// <summary>For a non-isolated group: its own alpha, excluding the copied backdrop; knockout replaces alpha by shape.</summary>
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
        if (!group.Isolated && !group.Knockout && !InKnockoutGroup && state.FillAlpha >= 1 && blend == BlendMode.Normal && !maskKnown)
        {
            _frames.Add(new Frame(FrameKind.Passthrough, null, _target, 1, BlendMode.Normal, 0));
            return;
        }

        CheckNesting();
        var layer = new Canvas(_w, _h, PixelFormat.Rgba8);
        ImageRect region = GroupRegion(group.Bounds, state.Ctm.Then(_view));
        Canvas? shape = null;
        Canvas? backdrop = group.Isolated ? null : GroupBackdrop;
        Canvas? geometry = null;
        try
        {
            geometry = InKnockoutGroup || GeometryShadow is not null ? new Canvas(_w, _h, PixelFormat.Rgba8) : null;
            if (backdrop is not null)
            {
                // 11.4.5/11.4.6: copy the initial backdrop, which may differ from the immediate parent in a knockout.
                CopyBackdrop(layer, backdrop, region);
                shape = new Canvas(_w, _h, PixelFormat.Rgba8);
            }
            _frames.Add(new Frame(FrameKind.Group, layer, _target, state.FillAlpha, blend, maskKnown ? state.SoftMaskId : 0)
                { Knockout = group.Knockout, Shape = shape, Geometry = geometry, Backdrop = backdrop,
                  AlphaIsShape = state.AlphaIsShape, CompositeRegion = region });
            _target = layer;
        }
        catch
        {
            geometry?.Dispose();
            shape?.Dispose();
            layer.Dispose();
            throw;
        }
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
    private Canvas? ShapeShadow
    {
        get
        {
            for (int i = _frames.Count - 1; i >= 0; i--)
            {
                Frame frame = _frames[i];
                if (frame.Kind == FrameKind.Passthrough) continue;
                // A passthrough form shares its owner's target. Never cross a mask or another layer.
                return frame.Kind == FrameKind.Group && ReferenceEquals(frame.Layer, _target) ? frame.Shape : null;
            }
            return _rootShape;
        }
    }

    /// <summary>Opens the implicit non-isolated text knockout group; each glyph carries its own blend, opacity and mask.</summary>
    private void BeginKnockoutLayer()
    {
        CheckNesting();
        var layer = new Canvas(_w, _h, PixelFormat.Rgba8);
        var region = new ImageRect(0, 0, _w, _h);
        Canvas? backdrop = GroupBackdrop;
        Canvas? alpha = null, geometry = null;
        try
        {
            alpha = backdrop is null ? null : new Canvas(_w, _h, PixelFormat.Rgba8);
            geometry = InKnockoutGroup || GeometryShadow is not null ? new Canvas(_w, _h, PixelFormat.Rgba8) : null;
            if (backdrop is not null) CopyBackdrop(layer, backdrop, region);
            _frames.Add(new Frame(FrameKind.Group, layer, _target, 1, BlendMode.Normal, 0)
                { Knockout = true, Backdrop = backdrop, Shape = alpha, Geometry = geometry, CompositeRegion = region });
            _target = layer;
        }
        catch
        {
            geometry?.Dispose();
            alpha?.Dispose();
            layer.Dispose();
            throw;
        }
    }

    /// <summary>The group that owns this target, ignoring passthrough forms but never crossing masks.</summary>
    private Frame? TargetGroup
    {
        get
        {
            for (int i = _frames.Count - 1; i >= 0; i--)
            {
                Frame frame = _frames[i];
                if (frame.Kind == FrameKind.Passthrough) continue;
                return frame.Kind == FrameKind.Group && ReferenceEquals(frame.Layer, _target) ? frame : null;
            }
            return null;
        }
    }

    private bool InKnockoutGroup => TargetGroup is { Knockout: true };
    private Canvas? GroupBackdrop => TargetGroup is { Knockout: true } group ? group.Backdrop : _target;
    private Canvas? GeometryShadow
    {
        get
        {
            for (int i = _frames.Count - 1; i >= 0; i--)
            {
                Frame frame = _frames[i];
                if (frame.Kind == FrameKind.Passthrough) continue;
                return frame.Kind == FrameKind.Group && ReferenceEquals(frame.Layer, _target) ? frame.Geometry : null;
            }
            return ReferenceEquals(_target, _root) ? _rootGeometry : null;
        }
    }

    private void PaintKnockout(Brush source, Brush intrinsicShape, DrawingPath area, IntersectionRule rule, float opacity,
        BlendMode blend, Canvas? mask, bool alphaIsShape, DrawingPath? clip, bool antialias, Canvas? stencil = null)
    {
        var rect = new ImageRect(0, 0, _w, _h);
        using var initial = GroupBackdrop is { } backdrop ? new CanvasLayerBrush(backdrop, null, null, rect) : null;
        using var maskBrush = mask is null ? null : new CanvasLayerBrush(mask, null, null, rect);
        using var stencilBrush = stencil is null ? null : new CanvasLayerBrush(stencil, null, null, rect);
        var color = new KnockoutBrush(source, intrinsicShape, initial, maskBrush, stencilBrush, opacity, alphaIsShape, blend, KnockoutChannel.Color);
        _target.Fill(color, area, antialias, rule, 1, BlendMode.Normal, AlphaComposition.Src, false, null, clip, _clip.Rule);
        if (ShapeShadow is { } alpha)
        {
            var coverage = new KnockoutBrush(source, intrinsicShape, initial, maskBrush, stencilBrush, opacity, alphaIsShape, blend, KnockoutChannel.Alpha);
            alpha.Fill(coverage, area, antialias, rule, 1, BlendMode.Normal, AlphaComposition.Src, false, null, clip, _clip.Rule);
        }
        TrackGeometry(source, intrinsicShape, area, rule, opacity, mask, alphaIsShape, clip, antialias, stencil);
    }

    private void TrackGeometry(Brush source, Brush intrinsicShape, DrawingPath area, IntersectionRule rule, float opacity,
        Canvas? mask, bool alphaIsShape, DrawingPath? clip, bool antialias, Canvas? stencil = null)
    {
        if (GeometryShadow is not { } geometry) return;
        var rect = new ImageRect(0, 0, _w, _h);
        using var maskBrush = mask is null ? null : new CanvasLayerBrush(mask, null, null, rect);
        using var stencilBrush = stencil is null ? null : new CanvasLayerBrush(stencil, null, null, rect);
        var brush = new KnockoutBrush(source, intrinsicShape, null, maskBrush, stencilBrush, opacity, alphaIsShape, BlendMode.Normal, KnockoutChannel.Shape);
        geometry.Fill(brush, area, antialias, rule, 1, BlendMode.Normal, AlphaComposition.SrcOver, false, null, clip, _clip.Rule);
    }

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
        CompositeLayer(layer, f.Opacity, f.Blend, f.MaskId, f.Shape, f.CompositeRegion, f.Geometry, f.AlphaIsShape);
    }

    /// <summary>Composites a finished layer onto the current target with an opacity, blend mode and (known) soft mask, and releases it.</summary>
    private void CompositeLayer(Canvas layer, double opacity, BlendMode blend, int maskId, Canvas? shape = null, ImageRect? region = null, Canvas? geometry = null, bool alphaIsShape = false)
    {
        try
        {
            ImageRect rect = region ?? new ImageRect(0, 0, _w, _h);
            if (rect.IsEmpty) return;
            Canvas? mask = null;
            if (maskId != 0) _masks.TryGetValue(maskId, out mask);
            DrawingPath area = DrawingPath.Rectangle(rect.X, rect.Y, rect.Width, rect.Height);
            float amount = (float)Math.Clamp(opacity, 0, 1);
            if (InKnockoutGroup)
            {
                using var geometric = new CanvasLayerBrush(geometry!, null, null, rect);
                if (shape is not null)
                {
                    using var source = new NonIsolatedGroupBrush(layer, shape, null, rect, 1, interpolate: false);
                    PaintKnockout(source, geometric, area, IntersectionRule.NonZero, amount, blend, mask, alphaIsShape, null, false);
                }
                else
                {
                    using var source = new CanvasLayerBrush(layer, null, null, rect);
                    PaintKnockout(source, geometric, area, IntersectionRule.NonZero, amount, blend, mask, alphaIsShape, null, false);
                }
                return;
            }
            if (geometry is not null)
            {
                using var geometric = new CanvasLayerBrush(geometry, null, null, rect);
                TrackGeometry(geometric, geometric, area, IntersectionRule.NonZero, amount, mask, alphaIsShape, null, false);
            }
            if (shape is not null)
            {
                bool interpolate = blend == BlendMode.Normal;
                using (var groupBrush = new NonIsolatedGroupBrush(layer, shape, mask, rect, amount, interpolate))
                {
                    _target.Fill(groupBrush, area, antialias: false, blend: blend,
                        composition: interpolate ? AlphaComposition.Src : AlphaComposition.SrcOver);
                }
                // Group alpha excludes the copied backdrop, even when it was translucent.
                if (ShapeShadow is { } parentShape)
                {
                    using var coverage = new CanvasLayerBrush(shape, null, mask, rect);
                    parentShape.Fill(coverage, area, antialias: false, opacity: amount);
                }
            }
            else
            {
                using var layerBrush = new CanvasLayerBrush(layer, null, mask, rect);
                _target.Fill(layerBrush, area, antialias: false, opacity: amount, blend: blend, composition: AlphaComposition.SrcOver);
                ShapeShadow?.Fill(layerBrush, area, antialias: false, opacity: amount, blend: BlendMode.Normal, composition: AlphaComposition.SrcOver);
            }
        }
        finally
        {
            geometry?.Dispose();
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
