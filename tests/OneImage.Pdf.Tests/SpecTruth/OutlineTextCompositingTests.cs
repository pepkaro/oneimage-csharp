using static OneImage.Pdf.Tests.SpecTruth.Spec;

namespace OneImage.Pdf.Tests.SpecTruth;

/// <summary>Outlined-text compositing with a generated CFF square, independent of installed or substitute fonts.</summary>
public class OutlineTextCompositingTests
{
    // Generated CFF1: empty .notdef and A, a 1000-unit square with a 1000-unit advance and no hints.
    // Its Type 2 charstring is: 1000 0 hmoveto 1000 1000 -1000 hlineto endchar.
    private static readonly byte[] SquareCff = Convert.FromBase64String(
        "AQAEAQABAQEKQXVkaXRSZWN0AAEBARj4GwL4GwP4GASLi/p8+nwFyQ+L4RLMEQABAQEKQXVkaXRSZWN0AAAAACIAAgEBBBD6fA76fIsW+nz6fP58Bg4=");

    private static byte[] Text(string content, string graphicsState = "/ca 0.5 /CA 0.5", int scaleX = 1) => Page(
        content,
        "/Font << /F1 5 0 R >> /ExtGState << /G << " + graphicsState + " >> /Opaque << /ca 1 >> >>",
        w: 20 * scaleX,
        extra: FontObjects());

    private static string[] FontObjects(byte[]? cff = null) =>
        [
            "<< /Type /Font /Subtype /Type1 /BaseFont /AuditRect /FirstChar 65 /LastChar 65 /Widths [1000] " +
                "/Encoding << /Type /Encoding /Differences [65 /A] >> /FontDescriptor 6 0 R >>",
            "<< /Type /FontDescriptor /FontName /AuditRect /Flags 32 /FontBBox [0 0 1000 1000] /ItalicAngle 0 " +
                "/Ascent 1000 /Descent 0 /CapHeight 1000 /StemV 100 /FontFile3 7 0 R >>",
            Stream("/Subtype /Type1C", cff ?? SquareCff),
        ];

    // 11.7.4.4 includes text modes 2 and 6: the stroke knocks out the fill, independently of /TK (9.3.8).
    [Theory]
    [InlineData(2, 0.5, 0.5, true, 1, false)]
    [InlineData(6, 0.5, 0.5, true, 1, false)]
    [InlineData(2, 0.5, 0.5, false, 1, false)]
    [InlineData(6, 0.5, 0.5, false, 1, false)]
    [InlineData(2, 1.0, 0.5, true, 1, false)]
    [InlineData(2, 0.5, 1.0, true, 1, false)]
    [InlineData(2, 0.5, 0.5, true, 2, false)]
    [InlineData(6, 0.5, 0.5, true, 2, false)]
    [InlineData(2, 0.5, 0.5, true, 1, true)]
    [Trait("Section", "11.7.4.4")]
    public void TranslucentStrokeKnocksOutGlyphFill(int mode, double fillAlpha, double strokeAlpha, bool textKnockout, int scaleX, bool coloredBackdrop)
    {
        string backdrop = coloredBackdrop ? "0 1 0 rg 0 0 20 20 re f " : "";
        string content = $"{scaleX} 0 0 1 0 0 cm {backdrop}/G gs 1 0 0 rg 0 0 1 RG 4 w BT /F1 8 Tf {mode} Tr 6 6 Td (A) Tj ET";
        string state = FormattableString.Invariant($"/ca {fillAlpha} /CA {strokeAlpha} /TK {(textKnockout ? "true" : "false")}");
        var background = coloredBackdrop ? Rgb(0, 1, 0) : Gray(1);
        var expected = new Expected(20 * scaleX, 20)
            .Rect(0, 0, 20 * scaleX, 20, background)
            .Rect(4 * scaleX, 4, 16 * scaleX, 16, Rgb(0, 0, 1), strokeAlpha)
            .Rect(8 * scaleX, 8, 12 * scaleX, 12, background)
            .Rect(8 * scaleX, 8, 12 * scaleX, 12, Rgb(1, 0, 0), fillAlpha);
        Check(Text(content, state, scaleX), expected, Tol.One);
    }

    [Fact]
    [Trait("Section", "9.3.6")]
    public void FillStrokeClipKeepsTheWholeGlyphOutline()
    {
        byte[] pdf = Text("/G gs 1 0 0 rg 0 0 1 RG 4 w BT /F1 8 Tf 6 Tr 6 6 Td (A) Tj ET /Opaque gs 0 1 0 rg 0 0 20 20 re f");
        var expected = new Expected(20, 20)
            .Rect(4, 4, 16, 16, Rgb(0, 0, 1), 0.5)
            .Rect(6, 6, 14, 14, Rgb(0, 1, 0));
        Check(pdf, expected, Tol.One);
    }

    // Separate text objects do not acquire the atomic fill/stroke operator's knockout behavior.
    [Fact]
    [Trait("Section", "11.7.4.4")]
    public void SeparateFillAndStrokeTextObjectsStillAccumulate()
    {
        byte[] pdf = Text("/G gs 1 0 0 rg 0 0 1 RG 4 w BT /F1 8 Tf 0 Tr 6 6 Td (A) Tj ET BT /F1 8 Tf 1 Tr 6 6 Td (A) Tj ET");
        var expected = new Expected(20, 20).Rect(6, 6, 14, 14, Rgb(1, 0, 0), 0.5)
            .Rect(4, 4, 16, 8, Rgb(0, 0, 1), 0.5)
            .Rect(4, 12, 16, 16, Rgb(0, 0, 1), 0.5)
            .Rect(4, 8, 8, 12, Rgb(0, 0, 1), 0.5)
            .Rect(12, 8, 16, 12, Rgb(0, 0, 1), 0.5);
        Check(pdf, expected, Tol.One);
    }

    [Fact]
    [Trait("Section", "11.7.4.4")]
    public void SeparatedGlyphsKnockOutTheirOwnFills()
    {
        byte[] pdf = Text("/G gs 1 0 0 rg 0 0 1 RG 4 w BT /F1 8 Tf 2 Tr 48 Tc 6 6 Td (AA) Tj ET", scaleX: 4);
        var expected = new Expected(80, 20);
        foreach (int x in new[] { 6, 62 })
        {
            expected.Rect(x - 2, 4, x + 10, 16, Rgb(0, 0, 1), 0.5)
                .Rect(x + 2, 8, x + 6, 12, Gray(1))
                .Rect(x + 2, 8, x + 6, 12, Rgb(1, 0, 0), 0.5);
        }

        Check(pdf, expected, Tol.One);
    }

    // A known limitation, not a spec-truth claim: overlapping or raster-adjacent glyphs keep the legacy merged-run path.
    [Theory]
    [InlineData(2, true, -4)]
    [InlineData(2, false, -4)]
    [InlineData(6, true, -4)]
    [InlineData(6, false, -4)]
    [InlineData(2, true, 5)]
    [InlineData(2, false, 5)]
    public void UncertainGlyphSeparationPreservesLegacyPixels(int mode, bool knockout, int spacing)
    {
        string state = $"/ca 0.5 /CA 0.5 /TK {(knockout ? "true" : "false")}";
        string prefix = "/G gs 1 0 0 rg 0 0 1 RG 4 w ";
        string Run(int m) => $"BT /F1 8 Tf {m} Tr {spacing} Tc 6 6 Td (AA) Tj ET ";
        Assert.Equal(Pix(Text(prefix + Run(0) + Run(1), state, 2)), Pix(Text(prefix + Run(mode), state, 2)));
    }

    [Theory]
    [InlineData(1)]
    [InlineData(2)]
    [Trait("Section", "11.7.4.4")]
    public void HairlineTextStrokeKnocksOutItsFill(int scaleX)
    {
        byte[] pdf = Text(FormattableString.Invariant($"{scaleX} 0 0 1 0 0 cm /G gs 1 0 0 rg 0 0 1 RG 0 w BT /F1 8 Tf 2 Tr {6.5 / scaleX} 6.5 Td (A) Tj ET"), scaleX: scaleX);
        var expected = new Expected(20 * scaleX, 20).Rect(6, 6, 7 + (8 * scaleX), 15, Rgb(0, 0, 1), 0.5)
            .Rect(7, 7, 6 + (8 * scaleX), 14, Gray(1)).Rect(7, 7, 6 + (8 * scaleX), 14, Rgb(1, 0, 0), 0.5);
        Check(pdf, expected, Tol.One);
    }

    [Fact]
    [Trait("Section", "11.7.4.4")]
    public void MultiplyStrokeBlendsWithTheBackdropNotTheFill()
    {
        byte[] pdf = Text("0.25 0.5 0.75 rg 0 0 20 20 re f /G gs 1 0 0 rg 0 0 1 RG 4 w BT /F1 8 Tf 2 Tr 6 6 Td (A) Tj ET", "/ca 0.5 /CA 0.5 /BM /Multiply");
        var background = Rgb(0.25, 0.5, 0.75);
        var expected = new Expected(20, 20).Rect(0, 0, 20, 20, background)
            .Rect(4, 4, 16, 16, Rgb(0, 0, 0.75), 0.5)
            .Rect(8, 8, 12, 12, background).Rect(8, 8, 12, 12, Rgb(0.25, 0, 0), 0.5);
        Check(pdf, expected, Tol.One);
    }

    [Fact]
    [Trait("Section", "11.7.4.4")]
    public void SoftMaskDoesNotRestoreTheKnockedOutFill()
    {
        byte[] pdf = Page("/G gs 1 0 0 rg 0 0 1 RG 4 w BT /F1 8 Tf 2 Tr 6 6 Td (A) Tj ET",
            "/Font << /F1 5 0 R >> /ExtGState << /G << /ca 0.5 /CA 0.5 /SMask << /S /Luminosity /G 8 0 R >> >> >>",
            extra: [.. FontObjects(), Stream("/Type /XObject /Subtype /Form /BBox [0 0 20 20] /Resources << >> /Group << /S /Transparency /CS /DeviceGray >>", "0.5 g 0 0 20 20 re f")]);
        var expected = new Expected(20, 20).Rect(4, 4, 16, 16, Rgb(0, 0, 1), 0.25)
            .Rect(8, 8, 12, 12, Gray(1)).Rect(8, 8, 12, 12, Rgb(1, 0, 0), 0.25);
        Check(pdf, expected, Tol.One);
    }

    [Theory]
    [InlineData("/AIS true")]
    [InlineData("/OP true")]
    [InlineData("/op true")]
    public void UnhandledTransparencySemanticsPreserveLegacyPixels(string flags)
    {
        string state = "/ca 0.5 /CA 0.5 " + flags;
        string prefix = "/G gs 1 0 0 rg 0 0 1 RG 4 w ";
        string Run(int mode) => $"BT /F1 8 Tf {mode} Tr 6 6 Td (A) Tj ET ";
        Assert.Equal(Pix(Text(prefix + Run(0) + Run(1), state)), Pix(Text(prefix + Run(2), state)));
    }

    // A run-wide dash-count fallback can differ from each glyph's fallback; do not infer stroke bounds from those glyphs.
    [Theory]
    [InlineData(2, "2 2")]
    [InlineData(6, "2 2")]
    [InlineData(2, "0.001 0.001")]
    [InlineData(6, "0.001 0.001")]
    public void MultiGlyphDashesPreserveLegacyPixels(int mode, string dashes)
    {
        string prefix = $"/G gs 1 0 0 rg 0 0 1 RG 4 w [{dashes}] 0 d ";
        string Run(int m) => $"BT /F1 8 Tf {m} Tr 8 Tc 6 6 Td (AA) Tj ET ";
        Assert.Equal(Pix(Text(prefix + Run(0) + Run(1), scaleX: 2)), Pix(Text(prefix + Run(mode), scaleX: 2)));
    }

    [Fact]
    public void SingleDashedGlyphMatchesTheEquivalentCombinedPath()
    {
        const string prefix = "/G gs 1 0 0 rg 0 0 1 RG 4 w [2 2] 0 d ";
        Assert.Equal(Pix(Text(prefix + "6 6 8 8 re B")), Pix(Text(prefix + "BT /F1 8 Tf 2 Tr 6 6 Td (A) Tj ET")));
    }

    // A known, deliberately preserved edge: zero-alpha text strokes currently do not knock out the fill.
    [Fact]
    public void ZeroAlphaStrokePreservesLegacyPixels()
    {
        const string prefix = "/G gs 1 0 0 rg 0 0 1 RG 4 w ";
        string Run(int mode) => $"BT /F1 8 Tf {mode} Tr 6 6 Td (A) Tj ET ";
        Assert.Equal(Pix(Text(prefix + Run(0) + Run(1), "/ca 0.5 /CA 0")), Pix(Text(prefix + Run(2), "/ca 0.5 /CA 0")));
    }

    [Fact]
    public void GlyphOutsideBooleanCoordinateLimitPreservesLegacyPixels()
    {
        const string prefix = "/G gs 1 0 0 rg 0 0 1 RG 4 w ";
        string Run(int mode) => $"BT /F1 100000000 Tf {mode} Tr 6 6 Td (A) Tj ET ";
        Assert.Equal(Pix(Text(prefix + Run(0) + Run(1))), Pix(Text(prefix + Run(2))));
    }

    [Theory]
    [InlineData(6.1999, 0, "1 0 0 1", false)]
    [InlineData(6.2, 0, "1 0 0 1", false)]
    [InlineData(42.1999, 0, "1 0 0 1", false)]
    [InlineData(42.2, 0, "1 0 0 1", false)]
    [InlineData(42.2001, 0, "1 0 0 1", false)]
    [InlineData(6.2001, 0, "1 0 0 1", false)]
    [InlineData(6.2, 0.25, "1 0 0 1", false)]
    [InlineData(6.2, 0, "1 0 0 1", true)]
    [InlineData(6.2, 0.25, "0.8 0.6 -0.6 0.8", false)]
    [InlineData(6.2, 0.25, "1 0.2 0.1 1", false)]
    public void SeparationDecisionIsIndependentOfTilesRegionsAndTranslation(double spacing, double phase, string linear, bool translateText)
    {
        byte[] Make(int shift)
        {
            string position = translateText
                ? FormattableString.Invariant($"1 0 0 1 0 0 cm BT /F1 8 Tf 2 Tr {spacing} Tc {20 + shift + phase} 120 Td")
                : FormattableString.Invariant($"{linear} {20 + shift + phase} 120 cm BT /F1 8 Tf 2 Tr {spacing} Tc 0 0 Td");
            return Page("/G gs 1 0 0 rg 0 0 1 RG 4 w " + position + " (AA) Tj ET",
                "/Font << /F1 5 0 R >> /ExtGState << /G << /ca 0.5 /CA 0.5 >> >>", w: 400, h: 400, extra: FontObjects());
        }

        Image Load(int shift) => RenderTests.Load(Make(shift), new PdfRenderOptions { Dpi = 72 });
        Rgba32[] reference = Load(0).ToArray<Rgba32>(maxDegree: 1);
        Rgba32[] shifted = Load(100).ToArray<Rgba32>(maxDegree: 1);
        for (int y = 230; y < 310; y++)
        {
            for (int x = 0; x < 100; x++)
            {
                Rgba32 a = reference[(y * 400) + x], b = shifted[(y * 400) + x + 100];
                // The rasterizer rounds float coordinates; one byte level is allowed, but switching compositing policies is not.
                Assert.True(Math.Abs(a.R - b.R) <= 1 && Math.Abs(a.G - b.G) <= 1 && Math.Abs(a.B - b.B) <= 1 && a.A == b.A,
                    $"translated pixel {x},{y} differs: {a} vs {b}");
            }
        }

        var region = new ImageRect(116, 250, 40, 40);
        foreach (int degree in new[] { 1, 4, 16 })
        {
            Assert.Equal(shifted, Load(100).ToArray<Rgba32>(maxDegree: degree));
            var part = new Rgba32[region.Width * region.Height];
            Load(100).CopyPixelsTo<Rgba32>(part, region, maxDegree: degree);
            for (int y = 0; y < region.Height; y++)
            {
                Assert.True(part.AsSpan(y * region.Width, region.Width).SequenceEqual(
                    shifted.AsSpan(((region.Y + y) * 400) + region.X, region.Width)));
            }
        }
    }
    [Theory]
    [InlineData(16777216)]
    [InlineData(100000000)]
    public void LargeTranslatedTextOriginPreservesLegacyPixels(int origin)
    {
        string prefix = $"1 0 0 1 {6 - origin} 0 cm /G gs 1 0 0 rg 0 0 1 RG 4 w ";
        string Run(int mode) => $"BT /F1 8 Tf {mode} Tr 8 Tc {origin} 6 Td (AA) Tj ET ";
        Assert.Equal(Pix(Text(prefix + Run(0) + Run(1), scaleX: 2)), Pix(Text(prefix + Run(2), scaleX: 2)));
    }


    [Fact]
    public void NearMiterLimitGlyphsPreserveLegacyPixels()
    {
        // Generated triangle: (0,0), (1000,500.375), (0,1000). The text matrix swaps axes, giving (4.003,8)
        // at 8pt. At the large original X origin it rounds to 100004, crossing the miter/bevel decision
        // relative to the origin-normalized proof. Maximum join reach, not re-stroking, must bound it.
        byte[] triangle = Convert.FromBase64String("AQAEAQABAQEKQXVkaXRSZWN0AAEBARj4GwL4GwP4GASLi/p8+nwFyQ+L6RLMEQABAQEKQXVkaXRSZWN0AAAAACIAAgEBBBj6fA76fIsW+nz/AfRgAP58/wHzoAAFDg==");
        const string prefix = "/G gs 1 0 0 rg 0 0 1 RG 20 w 2.2360681 M 1 0 0 1 -99970 0 cm ";
        string Run(int mode) => $"BT /F1 8 Tf {mode} Tr 17 Tc 0 1 1 0 100000 20 Tm (AA) Tj ET ";
        byte[] Make(string content) => Page(content, "/Font << /F1 5 0 R >> /ExtGState << /G << /ca 0.5 /CA 0.5 >> >>",
            w: 100, h: 100, extra: FontObjects(triangle));
        Assert.Equal(Pix(Make(prefix + Run(0) + Run(1))), Pix(Make(prefix + Run(2))));
    }
}
