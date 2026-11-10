namespace OneImage.Pdf.Tests;
public class GroupBoundsTests
{
    [Theory]
    [InlineData("/I false /K false", "1 0 0 1 0 0 cm")]
    [InlineData("/I true /K false", "1 0 0 1 0 0 cm")]
    [InlineData("/I true /K true", "1 0 0 1 0 0 cm")]
    [InlineData("/I false /K false", "0 1 -1 0 256 0 cm")]
    [InlineData("/I false /K false", "0.8 0 0 1.2 16 -20 cm")]
    public void TightGroupBoundsMatchAnExplicitClip(string flags, string transform)
    {
        byte[] tight = Page(flags, transform, true);
        byte[] wide = Page(flags, transform, false);
        Rgba32[] expected = Pixels(wide, 1);
        Assert.True(expected.AsSpan().SequenceEqual(Pixels(tight, 1)));
        Assert.True(expected.AsSpan().SequenceEqual(Pixels(tight, 4)));
    }
    [Theory]
    [InlineData("1 0.2 0.1 1 -12 -24")]
    [InlineData("0.8660254 0.5 -0.5 0.8660254 80 -20")]
    public void TightGroupBoundsRespectTheFormMatrix(string matrix)
    {
        byte[] tight = Page("/I false /K false", "1 0 0 1 0 0 cm", true, matrix);
        byte[] wide = Page("/I false /K false", "1 0 0 1 0 0 cm", false, matrix);
        Rgba32[] expected = Pixels(wide, 1);
        Assert.True(expected.AsSpan().SequenceEqual(Pixels(tight, 1)));
        Assert.True(expected.AsSpan().SequenceEqual(Pixels(tight, 4)));
    }
    [Fact]
    public void TightGroupRegionMatchesTheWholePageAcrossACellBoundary()
    {
        byte[] pdf = Page("/I false /K false", "1 0 0 1 0 0 cm", true);
        Rgba32[] whole = Pixels(pdf, 1);
        var region = new ImageRect(120, 120, 20, 20);
        var part = new Rgba32[region.Width * region.Height];
        RenderTests.Load(pdf, new PdfRenderOptions { Dpi = 72 }).CopyPixelsTo<Rgba32>(part, region, maxDegree: 4);
        for (int y = 0; y < region.Height; y++)
            Assert.True(part.AsSpan(y * region.Width, region.Width).SequenceEqual(whole.AsSpan(((region.Y + y) * 256) + region.X, region.Width)));
    }
    private static byte[] Page(string flags, string transform, bool tight, string formMatrix = "1 0 0 1 0 0")
    {
        string bbox = tight ? "15.25 127.25 242.75 128.75" : "-100 -100 400 400";
        const string formContent = "q 15.25 127.25 227.5 1.5 re W n /M gs 0.1 0.7 0.4 rg 0 0 256 256 re f Q";
        string form = RegionTests.Obj($"/Type /XObject /Subtype /Form /BBox [{bbox}] /Matrix [{formMatrix}] /Group << /S /Transparency {flags} >> /Resources << /ExtGState << /M << /BM /Multiply >> >> >>", formContent);
        return TestPdf.Page("0.8 0.4 0.2 rg 0 0 256 256 re f q " + transform + " /G gs /F0 Do Q", "/XObject << /F0 5 0 R >> /ExtGState << /G << /ca 0.75 >> >>", width: 256, height: 256, extra: [form]);
    }
    [Fact]
    public void TightGroupCropsTheSoftMaskAtTheSameCoordinates()
    {
        Rgba32[] expected = Pixels(MaskedPage(false), 1);
        Assert.True(expected.AsSpan().SequenceEqual(Pixels(MaskedPage(true), 1)));
        Assert.True(expected.AsSpan().SequenceEqual(Pixels(MaskedPage(true), 4)));
    }
    private static byte[] MaskedPage(bool tight)
    {
        string bbox = tight ? "15.25 127.25 242.75 128.75" : "-100 -100 400 400";
        string inner = RegionTests.Obj($"/Type /XObject /Subtype /Form /BBox [{bbox}] /Group << /S /Transparency /I false >> /Resources << >>", "q 15.25 127.25 227.5 1.5 re W n 0.1 0.7 0.4 rg 0 0 256 256 re f Q");
        string mask = RegionTests.Obj("/Type /XObject /Subtype /Form /BBox [0 0 256 256] /Group << /S /Transparency /CS /DeviceGray >> /Resources << /ExtGState << /H << /ca 0.25 >> >> >>", "1 g 0 0 128 256 re f /H gs 128 0 128 256 re f");
        string outer = RegionTests.Obj("/Type /XObject /Subtype /Form /BBox [0 0 256 256] /Group << /S /Transparency /I false >> /Resources << /XObject << /F0 5 0 R >> /ExtGState << /G << /ca 0.6 /SMask << /S /Alpha /G 6 0 R >> >> >> >>", "/G gs /F0 Do");
        return TestPdf.Page("0.8 0.4 0.2 rg 0 0 256 256 re f /G gs /F0 Do", "/XObject << /F0 7 0 R >> /ExtGState << /G << /ca 0.75 >> >>", width: 256, height: 256, extra: [inner, mask, outer]);
    }
    private static Rgba32[] Pixels(byte[] pdf, int degree) => RenderTests.Load(pdf, new PdfRenderOptions { Dpi = 72 }).ToArray<Rgba32>(maxDegree: degree);
}
