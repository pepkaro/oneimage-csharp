namespace OneImage.Pdf.Tests;

/// <summary>The optional viewer-style smoothing policy never changes document defaults or image reduction.</summary>
public class ImageSmoothingTests
{
    private const string ImageResources = "/XObject << /Im0 5 0 R >>";
    private const string Placement = "36 0 0 36 2 2";

    private static string Picture(string interpolate, string extra = "", string samples = "00ffff00", int size = 2) =>
        RegionTests.Obj($"/Type /XObject /Subtype /Image /Width {size} /Height {size} /ColorSpace /DeviceGray /BitsPerComponent 8 /Filter /ASCIIHexDecode {interpolate} {extra}", samples + ">");

    private static byte[] Page(string interpolate, string placement = Placement, string samples = "00ffff00") =>
        TestPdf.Page($"q {placement} cm /Im0 Do Q", ImageResources, 40, 40, [Picture(interpolate, samples: samples)]);

    private static Image Load(byte[] pdf, bool smooth = false, long cachePixels = 1 << 26) =>
        RenderTests.Load(pdf, new PdfRenderOptions
        {
            Dpi = 72,
            SmoothMagnifiedImages = smooth,
            Limits = new PdfRenderLimits { MaxCachedPixels = cachePixels },
        });

    private static Rgba32[] Render(byte[] pdf, bool smooth = false) => Load(pdf, smooth).ToArray<Rgba32>(maxDegree: 1);

    private static void Equal(Rgba32[] expected, Rgba32[] actual) => Assert.True(expected.AsSpan().SequenceEqual(actual));

    [Theory]
    [InlineData("")]
    [InlineData("/Interpolate false")]
    public void DefaultAndExplicitFalseKeepExactSampleBlocks(string interpolate)
    {
        Assert.False(new PdfRenderOptions().SmoothMagnifiedImages);
        byte[] pdf = Page(interpolate);
        Rgba32[] pixels = RenderTests.Load(pdf, new PdfRenderOptions { Dpi = 72 }).ToArray<Rgba32>();
        Equal(pixels, Render(pdf, false));
        Equal(pixels, Render(Page("/Interpolate false")));
        for (int y = 0; y < 40; y++)
        {
            for (int x = 0; x < 40; x++)
            {
                byte g = x >= 2 && x < 38 && y >= 2 && y < 38 && ((x < 20) == (y < 20)) ? (byte)0 : (byte)255;
                Assert.Equal(new Rgba32(g, g, g, 255), pixels[(y * 40) + x]);
            }
        }
    }

    [Theory]
    [InlineData(Placement)]
    [InlineData("36 0 0 2 2 19")]
    [InlineData("2 0 0 36 19 2")]
    [InlineData("36 0 0 1 2 19")]
    [InlineData("1 0 0 36 19 2")]
    [InlineData("0 36 -36 0 38 2")]
    [InlineData("-36 0 0 36 38 2")]
    [InlineData("24 8 -8 24 12 4")]
    public void MagnifiedImagesMatchTheExistingInterpolateTruePath(string placement)
    {
        Rgba32[] expected = Render(Page("/Interpolate true", placement, samples: "002080ff"));
        Equal(expected, Render(Page("", placement, samples: "002080ff"), true));
        Equal(expected, Render(Page("/Interpolate false", placement, samples: "002080ff"), true));
        Equal(expected, Render(Page("/Interpolate true", placement, samples: "002080ff"), true));
        Assert.False(expected.AsSpan().SequenceEqual(Render(Page("/Interpolate false", placement, samples: "002080ff"))));
        Assert.Contains(expected, p => p.R > 0 && p.R < 255);
    }

    [Theory]
    [InlineData(2)]
    [InlineData(5)]
    [InlineData(7)]
    [InlineData(8)]
    public void ReducedAndOneToOneImagesAreUnchanged(int side)
    {
        // Exercise both the area-reduction threshold and bilinear-only reduction without area averaging.
        const string samples = "00ff00ff00ff00ffff00ff00ff00ff00";
        foreach (string interpolate in new[] { "", "/Interpolate false", "/Interpolate true" })
        {
            byte[] pdf = TestPdf.Page($"q {side} 0 0 {side} 2 2 cm /Im0 Do Q", ImageResources, 40, 40,
                [Picture(interpolate, samples: string.Concat(Enumerable.Repeat(samples, 4)), size: 8)]);
            Equal(Render(pdf), Render(pdf, true));
        }
    }

    private static byte[] NestedPage(string kind, string interpolate)
    {
        string picture = Picture(interpolate);
        string form = RegionTests.Obj("/Type /XObject /Subtype /Form /BBox [0 0 40 40] /Resources << " + ImageResources + " >>",
            $"q {Placement} cm /Im0 Do Q");
        return kind switch
        {
            "form" => TestPdf.Page("/Outer Do", "/XObject << /Outer 7 0 R >>", 40, 40,
                [picture, form, RegionTests.Obj("/Type /XObject /Subtype /Form /BBox [0 0 40 40] /Resources << /XObject << /Inner 6 0 R >> >>", "/Inner Do")]),
            "pattern" => TestPdf.Page("/Pattern cs /P1 scn 0 0 320 320 re f", "/Pattern << /P1 6 0 R >>", 320, 320,
                [picture, RegionTests.Obj("/Type /Pattern /PatternType 1 /PaintType 1 /TilingType 1 /BBox [0 0 40 40] /XStep 40 /YStep 40 /Resources << " + ImageResources + " >>",
                    $"q {Placement} cm /Im0 Do Q")]),
            "type3" => TestPdf.Page("BT /F1 36 Tf 2 2 Td (a) Tj ET", "/Font << /F1 7 0 R >>", 40, 40,
                [picture, RegionTests.Obj("", "1 0 d0 /Im0 Do"),
                    "<< /Type /Font /Subtype /Type3 /FontBBox [0 0 1 1] /FontMatrix [1 0 0 1 0 0] /CharProcs << /a 6 0 R >> /Encoding << /Type /Encoding /Differences [97 /a] >> /FirstChar 97 /LastChar 97 /Widths [1] /Resources << " + ImageResources + " >> >>"]),
            "soft-mask" => TestPdf.Page("/GS0 gs 1 0 0 rg 0 0 40 40 re f", "/ExtGState << /GS0 << /SMask << /S /Luminosity /G 6 0 R >> >> >>", 40, 40,
                [picture, RegionTests.Obj("/Type /XObject /Subtype /Form /BBox [0 0 40 40] /Group << /S /Transparency /CS /DeviceGray /I true >> /Resources << " + ImageResources + " >>",
                    $"q {Placement} cm /Im0 Do Q")]),
            _ => throw new ArgumentException("Unknown fixture.", nameof(kind)),
        };
    }

    [Theory]
    [InlineData("form")]
    [InlineData("pattern")]
    [InlineData("type3")]
    [InlineData("soft-mask")]
    public void NestedImagesUseThePageOption(string kind)
    {
        byte[] pdf = NestedPage(kind, "/Interpolate false");
        Rgba32[] crisp = Render(pdf);
        Rgba32[] expected = Render(NestedPage(kind, "/Interpolate true"));
        Equal(expected, Render(pdf, true));
        Assert.False(expected.AsSpan().SequenceEqual(crisp));
        // Pattern caches belong to the PageRender/options instance; no global cache can leak the policy across loads.
        Equal(crisp, Render(pdf));
        Equal(expected, Load(pdf, true, cachePixels: 0).ToArray<Rgba32>());
    }

    [Theory]
    [InlineData("")]
    [InlineData("/Interpolate false")]
    [InlineData("/Interpolate true")]
    public void StencilMasksKeepTheirDocumentInterpolation(string interpolate)
    {
        string stencil = RegionTests.Obj($"/Type /XObject /Subtype /Image /Width 2 /Height 2 /ImageMask true /BitsPerComponent 1 /Filter /ASCIIHexDecode {interpolate}", "4080>");
        foreach (bool pattern in new[] { false, true })
        {
            string paint = pattern ? "/Pattern cs /P1 scn" : "1 0 0 rg";
            byte[] pdf = TestPdf.Page($"{paint} q {Placement} cm /Im0 Do Q", ImageResources + " /Pattern << /P1 6 0 R >>", 40, 40,
                [stencil, RegionTests.Obj("/Type /Pattern /PatternType 1 /PaintType 1 /TilingType 1 /BBox [0 0 4 4] /XStep 4 /YStep 4 /Resources << >>", "1 0 0 rg 0 0 4 4 re f")]);
            Equal(Render(pdf), Render(pdf, true));
        }
    }

    [Theory]
    [InlineData("/SMask 6 0 R")]
    [InlineData("/Mask [255 255]")]
    [InlineData("/Mask 6 0 R")]
    public void DecodedImageAlphaUsesTheExistingSmoothPath(string mask)
    {
        byte[] Make(string interpolate) => TestPdf.Page($"0 0 1 rg 0 0 40 40 re f q {Placement} cm /Im0 Do Q", ImageResources, 40, 40,
            [Picture(interpolate, mask), mask == "/Mask 6 0 R"
                ? RegionTests.Obj("/Type /XObject /Subtype /Image /Width 2 /Height 2 /ImageMask true /BitsPerComponent 1 /Filter /ASCIIHexDecode", "4080>")
                : Picture("", samples: "0055aaff")]);
        Rgba32[] expected = Render(Make("/Interpolate true"));
        Equal(expected, Render(Make("/Interpolate false"), true));
        Equal(expected, Render(Make("/Interpolate true"), true));
        Assert.False(expected.AsSpan().SequenceEqual(Render(Make("/Interpolate false"))));
    }

    [Theory]
    [InlineData("pattern", 1)]
    [InlineData("pattern", 4)]
    [InlineData("pattern", 16)]
    [InlineData("image", 1)]
    [InlineData("image", 4)]
    [InlineData("image", 16)]
    public void SmoothImageRegionsAndThreadCountsMatchTheWholePage(string kind, int degree)
    {
        byte[] pdf = kind == "pattern" ? NestedPage("pattern", "") :
            TestPdf.Page("q 260 39 -31 250 42 12 cm /Im0 Do Q", ImageResources, 320, 320, [Picture("")]);
        Rgba32[] whole = Load(pdf, true).ToArray<Rgba32>(maxDegree: 1);
        Equal(whole, Load(pdf, true).ToArray<Rgba32>(maxDegree: degree));
        foreach (var r in new[] { new ImageRect(127, 127, 2, 2), new ImageRect(31, 63, 257, 129), new ImageRect(256, 256, 64, 64) })
        {
            var part = new Rgba32[r.Width * r.Height];
            Load(pdf, true).CopyPixelsTo<Rgba32>(part, r, degree);
            for (int y = 0; y < r.Height; y++)
            {
                Assert.True(part.AsSpan(y * r.Width, r.Width).SequenceEqual(whole.AsSpan(((r.Y + y) * 320) + r.X, r.Width)));
            }
        }
    }

    [Fact]
    public void ConcurrentSmoothRegionReadsShareCachesSafely()
    {
        byte[] pdf = NestedPage("pattern", "");
        Image image = Load(pdf, true);
        Rgba32[] whole = Load(pdf, true).ToArray<Rgba32>(maxDegree: 1);
        Parallel.For(0, 16, new ParallelOptions { MaxDegreeOfParallelism = 4 }, i =>
        {
            var r = new ImageRect((i * 37) % 192, (i * 53) % 192, 129, 129);
            var part = new Rgba32[r.Width * r.Height];
            image.CopyPixelsTo<Rgba32>(part, r);
            for (int y = 0; y < r.Height; y++)
            {
                Assert.True(part.AsSpan(y * r.Width, r.Width).SequenceEqual(whole.AsSpan(((r.Y + y) * 320) + r.X, r.Width)));
            }
        });
    }

    [Fact]
    public void ResizingStillRendersAtTheRequestedSize()
    {
        byte[] pdf = Page("");
        Rgba32[] expected = Load(Page("/Interpolate true")).Resize(width: 61).ToArray<Rgba32>();
        Equal(expected, Load(pdf, true).Resize(width: 61).ToArray<Rgba32>());
    }

    [Fact]
    public void ViewerStyleConfigurationExample()
    {
        // Compiled example from docs/pdf.md.
        var config = new ImageConfiguration().Add(new PdfFormat(new PdfRenderOptions
        {
            Dpi = 144,
            SmoothMagnifiedImages = true,
        }));
        Image image = Image.Load(Page(""), new LoadOptions { Configuration = config });
        Assert.Equal(80, image.Width);
        Assert.Contains(image.ToArray<Rgba32>(), p => p.R > 0 && p.R < 255);
    }

    [Fact]
    public void VectorAndOutlineTextRenderingIsUnchanged()
    {
        byte[] pdf = TestPdf.Page("0 0 1 rg 2 3 18 20 re f BT /F1 12 Tf 1 20 Td (Abc) Tj ET",
            "/Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >>", 40, 40);
        Equal(Render(pdf), Render(pdf, true));
    }
}
