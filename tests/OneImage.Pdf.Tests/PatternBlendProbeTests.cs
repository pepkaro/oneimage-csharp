// SPDX-License-Identifier: MIT
using OneImage.Pdf.Render;
using OnePdf;

namespace OneImage.Pdf.Tests;

public class PatternBlendProbeTests
{
    [Theory]
    [InlineData("Normal", false)]
    [InlineData("Multiply", true)]
    [InlineData("Screen", true)]
    public void ChoosesTheBackdropRouteOnlyWhenRequired(string blend, bool expected)
    {
        string pattern = RegionTests.Obj($"/Type /Pattern /PatternType 1 /PaintType 1 /TilingType 1 /BBox [0 0 24 24] /XStep 24 /YStep 24 /Resources << /ExtGState << /A << /BM /{blend} >> >> >>", "/A gs .8 .4 .2 rg 0 0 24 24 re f");
        AssertRoute(TestPdf.Page("/Pattern cs /P scn 0 0 96 96 re f", "/Pattern << /P 5 0 R >>", 96, 96, [pattern]), expected);
    }

    [Fact]
    public void NestedGroupBlendIsDetectedWhenCellPaintIsNormal()
    {
        string pattern = RegionTests.Obj("/Type /Pattern /PatternType 1 /PaintType 1 /TilingType 1 /BBox [0 0 24 24] /XStep 24 /YStep 24 /Resources << /XObject << /F 6 0 R >> /ExtGState << /A << /BM /Multiply >> >> >>", "/A gs /F Do");
        string form = RegionTests.Obj("/Type /XObject /Subtype /Form /BBox [0 0 24 24] /Group << /S /Transparency /I false >> /Resources << >>", ".8 .4 .2 rg 0 0 24 24 re f");
        AssertRoute(TestPdf.Page("/Pattern cs /P scn 0 0 96 96 re f", "/Pattern << /P 5 0 R >>", 96, 96, [pattern, form]), true);
    }

    [Fact]
    public void CancellationIsObservedBetweenAnalysisCallbacks()
    {
        using var cancellation = new CancellationTokenSource();
        var probe = new PatternBlendProbe(cancellation.Token);
        probe.PushClip(default, false, default);
        cancellation.Cancel();
        Assert.Throws<OperationCanceledException>(() => probe.PopClip());
        Assert.Throws<OperationCanceledException>(() => probe.FillPath(default, false, default));
        Assert.Throws<OperationCanceledException>(() => probe.BeginGroup(default, default));
    }

    private static void AssertRoute(byte[] pdf, bool expected)
    {
        using PdfDocument document = PdfDocument.Open(pdf);
        var probe = new Capture();
        document.Pages[0].Interpret(probe);
        Assert.NotNull(probe.Pattern);
        Assert.Equal(expected, PatternBlendProbe.NeedsBackdrop(probe.Pattern));
    }

    private sealed class Capture : PdfDevice
    {
        public PdfTilingPattern? Pattern { get; private set; }
        public override void FillPath(in PdfPath path, bool evenOdd, in PdfGraphicsState state) => Pattern ??= state.FillColor.Pattern as PdfTilingPattern;
    }
}
