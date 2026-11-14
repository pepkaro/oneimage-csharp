// SPDX-License-Identifier: MIT

using System.Buffers.Binary;
using System.Globalization;
using System.Text;

namespace OneImage.Pdf.Tests;

/// <summary>Generated ICC and PDF controls: profile names must not choose the color conversion.</summary>
public class IccIdentityTests
{
    private static readonly Rgb24[] Samples =
    [
        new(0, 0, 0), new(255, 255, 255), new(128, 128, 128), new(32, 32, 32),
        new(255, 0, 0), new(0, 255, 0), new(0, 0, 255), new(200, 100, 50),
        new(64, 128, 192), new(192, 128, 64), new(128, 200, 128), new(220, 180, 200),
    ];

    [Theory]
    [InlineData(false)]
    [InlineData(true)]
    public void WideGamutDescriptionDoesNotChangeVectorOrImageColors(bool renamedFirst)
    {
        byte[] original = ColorProfile.WideGamutRgb.IccBytes.ToArray();
        byte[] renamed = Rewrite(original, "sRGB diagnostic only");
        Rgba32[] expected = Converted(ColorProfile.WideGamutRgb);
        Assert.NotEqual(AsRgba(Samples), expected);
        CheckBothOrders(original, renamed, expected, renamedFirst);
    }

    [Theory]
    [InlineData(false)]
    [InlineData(true)]
    public void LinearSrgbNeedsItsTransferCurveInBothPaths(bool renamedFirst)
    {
        byte[] original = ColorProfile.LinearSrgb.IccBytes.ToArray();
        byte[] renamed = Rewrite(original, "Linear working profile");
        Rgba32[] expected = Converted(ColorProfile.LinearSrgb);
        Assert.InRange(expected[2].R, (byte)187, (byte)189);
        CheckBothOrders(original, renamed, expected, renamedFirst);
    }

    [Theory]
    [InlineData(false)]
    [InlineData(true)]
    public void TrueSrgbStaysExactWhenRenamedAndRepacked(bool renamedFirst)
    {
        byte[] original = ColorProfile.Srgb.IccBytes.ToArray();
        byte[] renamed = Rewrite(original, "Unrelated working profile");
        CheckBothOrders(original, renamed, AsRgba(Samples), renamedFirst);
    }

    [Theory]
    [InlineData("A2B0")]
    [InlineData("A2B1")]
    public void LutOverridesSrgbMatrixEvenWithSrgbDescription(string tag)
    {
        byte[] profile = Rewrite(ColorProfile.Srgb.IccBytes.ToArray(), "sRGB with table", tag);
        byte[] renamed = Rewrite(profile, "A table profile");
        Rgba32[] expected = Converted(ColorProfile.FromIcc(profile));
        Assert.All(expected, p => Assert.Equal(new Rgba32(0, 0, 0, 255), p));
        CheckBothOrders(profile, renamed, expected, false);
    }

    [Fact]
    public void MalformedProfileStillFallsBackToDeviceRgb()
    {
        CheckSamples(Render([0, 1, 2, 3]), AsRgba(Samples));
    }

    private static void CheckBothOrders(byte[] original, byte[] renamed, Rgba32[] expected, bool renamedFirst)
    {
        // Distinct color spaces, reused samples and alternating renders exercise both cache insertion orders.
        byte[][] profiles = renamedFirst ? [renamed, original, renamed, original] : [original, renamed, original, renamed];
        Rgba32[]? first = null;
        foreach (byte[] profile in profiles)
        {
            Rgba32[] pixels = Render(profile);
            CheckSamples(pixels, expected);
            if (first is not null)
            {
                Assert.Equal(first, pixels);
            }

            first = pixels;
        }
    }

    private static Rgba32[] Converted(ColorProfile profile) =>
        Image.FromPixels<Rgb24>(Samples, Samples.Length, 1).AssignProfile(profile)
            .ConvertColor(ColorProfile.Srgb, RenderingIntent.RelativeColorimetric, true)
            .ConvertTo(PixelFormat.Rgba8).ToArray<Rgba32>();

    private static Rgba32[] AsRgba(Rgb24[] samples) => samples.Select(p => new Rgba32(p.R, p.G, p.B, 255)).ToArray();

    private static void CheckSamples(Rgba32[] pixels, Rgba32[] expected)
    {
        const int scale = 8;
        int width = Samples.Length * scale;
        for (int i = 0; i < Samples.Length; i++)
        {
            // Solid interiors, away from antialiasing boundaries; top = vector, bottom = image.
            Assert.Equal(expected[i], pixels[(4 * width) + (i * scale) + 4]);
            Assert.Equal(expected[i], pixels[(12 * width) + (i * scale) + 4]);
        }
    }

    private static Rgba32[] Render(byte[] profile)
    {
        int width = Samples.Length * 8;
        var content = new StringBuilder("/RelativeColorimetric ri /CS cs\n");
        for (int i = 0; i < Samples.Length; i++)
        {
            Rgb24 p = Samples[i];
            content.Append(CultureInfo.InvariantCulture, $"{p.R / 255.0:R} {p.G / 255.0:R} {p.B / 255.0:R} scn {i * 8} 8 8 8 re f\n");
        }

        // Same ICC stream shared by vector colors and both invocations of the image resource.
        content.Append(CultureInfo.InvariantCulture, $"q {width} 0 0 8 0 0 cm /Im Do /Im Do Q\n");
        byte[] pdf = TestPdf.Build(
        [
            TestPdf.Ascii("<< /Type /Catalog /Pages 2 0 R >>"),
            TestPdf.Ascii("<< /Type /Pages /Kids [3 0 R] /Count 1 >>"),
            TestPdf.Ascii($"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {width} 16] /Contents 4 0 R /Resources << /ColorSpace << /CS [/ICCBased 5 0 R] >> /XObject << /Im 6 0 R >> >> >>"),
            TestPdf.Stream("", TestPdf.Ascii(content.ToString())),
            TestPdf.Stream("/N 3 /Alternate /DeviceRGB", profile),
            TestPdf.Stream($"/Type /XObject /Subtype /Image /Width {Samples.Length} /Height 1 /BitsPerComponent 8 /ColorSpace [/ICCBased 5 0 R]", Samples.SelectMany(p => new[] { p.R, p.G, p.B }).ToArray()),
        ]);
        // Built-in profiles are ICC v4.3, supported by PDF 2.0. The header has the same length, preserving xref offsets.
        "%PDF-2.0\n"u8.CopyTo(pdf);
        return RenderTests.Load(pdf, new PdfRenderOptions { Dpi = 72 }).ToArray<Rgba32>();
    }

    private static byte[] Rewrite(byte[] profile, string description, string? addTable = null)
    {
        var tags = new Dictionary<string, byte[]>();
        int count = Read(profile, 128);
        for (int i = 0; i < count; i++)
        {
            int e = 132 + (i * 12);
            tags[Encoding.ASCII.GetString(profile, e, 4)] = profile.AsSpan(Read(profile, e + 4), Read(profile, e + 8)).ToArray();
        }

        byte[] text = Encoding.BigEndianUnicode.GetBytes(description);
        byte[] desc = new byte[28 + text.Length];
        Encoding.ASCII.GetBytes("mluc").CopyTo(desc, 0);
        Write(desc, 8, 1);
        Write(desc, 12, 12);
        Encoding.ASCII.GetBytes("enUS").CopyTo(desc, 16);
        Write(desc, 20, text.Length);
        Write(desc, 24, 28);
        text.CopyTo(desc, 28);
        tags["desc"] = desc;
        if (addTable is not null)
        {
            tags[addTable] = BlackLut();
        }

        int size = 132 + (tags.Count * 12) + tags.Sum(t => (t.Value.Length + 3) & ~3);
        byte[] result = new byte[size];
        profile.AsSpan(0, 128).CopyTo(result);
        Write(result, 0, size);
        Write(result, 128, tags.Count);
        int at = 132 + (tags.Count * 12), entry = 132;
        // Reverse order and do not share TRC storage, so equality must not depend on byte offsets.
        foreach (var tag in tags.Reverse())
        {
            Encoding.ASCII.GetBytes(tag.Key).CopyTo(result, entry);
            Write(result, entry + 4, at);
            Write(result, entry + 8, tag.Value.Length);
            tag.Value.CopyTo(result, at);
            at += (tag.Value.Length + 3) & ~3;
            entry += 12;
        }

        return result;
    }

    private static byte[] BlackLut()
    {
        // Valid mft2, 3 in/out, 2^3 grid, identity tables/matrix, and an all-black XYZ CLUT.
        byte[] lut = new byte[52 + 12 + 48 + 12];
        Encoding.ASCII.GetBytes("mft2").CopyTo(lut, 0);
        lut[8] = lut[9] = 3;
        lut[10] = 2;
        Write(lut, 12, 65536);
        Write(lut, 28, 65536);
        Write(lut, 44, 65536);
        lut[49] = lut[51] = 2;
        foreach (int start in new[] { 52, 112 })
        {
            for (int i = 0; i < 3; i++)
            {
                lut[start + (i * 4) + 2] = lut[start + (i * 4) + 3] = 255;
            }
        }

        return lut;
    }

    private static int Read(byte[] bytes, int offset) => (int)BinaryPrimitives.ReadUInt32BigEndian(bytes.AsSpan(offset));

    private static void Write(byte[] bytes, int offset, int value) => BinaryPrimitives.WriteUInt32BigEndian(bytes.AsSpan(offset), (uint)value);
}
