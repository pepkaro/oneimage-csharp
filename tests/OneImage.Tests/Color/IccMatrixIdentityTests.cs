// SPDX-License-Identifier: MIT

using System.Buffers.Binary;
using System.Text;

namespace OneImage.Tests;

public class IccMatrixIdentityTests
{
    [Fact]
    public void DescriptionCopyrightTagOrderAndHeaderMetadataDoNotChangeIdentity()
    {
        byte[] bytes = Rewrite(ColorProfile.Srgb, tags =>
        {
            var text = new IccWriter(IccData.Sig("mntr"), "RGB ", "XYZ ", 4, 3);
            tags["desc"] = text.Text("An unrelated name", true);
            tags["cprt"] = text.Text("A different copyright", false);
        });
        // Creation date, manufacturer, model, creator and profile ID are not transform data.
        bytes.AsSpan(24, 12).Fill(1);
        bytes.AsSpan(48, 8).Fill(2);
        bytes.AsSpan(80, 20).Fill(3);
        IccData renamed = IccData.Parse(bytes);
        Assert.True(ColorProfile.Srgb.Data.HasSameRgbMatrixShaper(renamed));
        Assert.True(renamed.HasSameRgbMatrixShaper(ColorProfile.Srgb.Data));
        Assert.False(bytes.AsSpan().SequenceEqual(ColorProfile.Srgb.IccBytes.Span));

        byte[] noText = Rewrite(ColorProfile.Srgb, tags => { tags.Remove("desc"); tags.Remove("cprt"); });
        Assert.True(IccData.Parse(noText).HasSameRgbMatrixShaper(ColorProfile.Srgb.Data));
    }

    [Theory]
    [InlineData("rXYZ")]
    [InlineData("gXYZ")]
    [InlineData("bXYZ")]
    [InlineData("rTRC")]
    [InlineData("gTRC")]
    [InlineData("bTRC")]
    [InlineData("wtpt")]
    public void EveryColorantCurveAndWhitePointMustMatchExactly(string tag)
    {
        byte[] bytes = Rewrite(ColorProfile.Srgb, tags => tags[tag][^1] ^= 1);
        Assert.False(IccData.Parse(bytes).HasSameRgbMatrixShaper(ColorProfile.Srgb.Data));
    }

    [Theory]
    [InlineData("A2B0")]
    [InlineData("A2B1")]
    [InlineData("A2B2")]
    [InlineData("B2A0")]
    [InlineData("B2A1")]
    [InlineData("B2A2")]
    [InlineData("D2B0")]
    [InlineData("D2B1")]
    [InlineData("D2B2")]
    [InlineData("D2B3")]
    [InlineData("B2D0")]
    [InlineData("B2D1")]
    [InlineData("B2D2")]
    [InlineData("B2D3")]
    public void TablesForEveryIntentAndDirectionPreventIdentity(string tag)
    {
        // Only the table's presence matters for this guard; it must never interpret or bypass the payload.
        IccData withTable = IccData.Parse(Rewrite(ColorProfile.Srgb, tags => tags[tag] = new byte[8]));
        Assert.False(withTable.HasSameRgbMatrixShaper(ColorProfile.Srgb.Data));
        Assert.False(ColorProfile.Srgb.Data.HasSameRgbMatrixShaper(withTable));
        Assert.False(withTable.HasSameRgbMatrixShaper(withTable));
    }

    [Fact]
    public void ExtraNonCosmeticTagsPreventIdentity()
    {
        foreach (string tag in new[] { "chad", "bkpt", "lumi", "test" })
        {
            IccData extra = IccData.Parse(Rewrite(ColorProfile.Srgb, tags => tags[tag] = new byte[8]));
            Assert.False(extra.HasSameRgbMatrixShaper(ColorProfile.Srgb.Data));
            Assert.False(ColorProfile.Srgb.Data.HasSameRgbMatrixShaper(extra));
        }
    }

    [Fact]
    public void LinearAndWideGamutProfilesAreNotEncodedSrgb()
    {
        Assert.False(ColorProfile.LinearSrgb.Data.HasSameRgbMatrixShaper(ColorProfile.Srgb.Data));
        Assert.False(ColorProfile.WideGamutRgb.Data.HasSameRgbMatrixShaper(ColorProfile.Srgb.Data));
        Assert.False(ColorProfile.DisplayP3.Data.HasSameRgbMatrixShaper(ColorProfile.Srgb.Data));
        Assert.False(ColorProfile.Gray.Data.HasSameRgbMatrixShaper(ColorProfile.Srgb.Data));
    }

    [Theory]
    [InlineData(9)] // Version bug-fix nibble, not just the parsed major/minor.
    [InlineData(44)] // Profile flags.
    [InlineData(56)] // Device attributes.
    [InlineData(68)] // Header PCS illuminant.
    [InlineData(100)] // Reserved header data.
    public void UncertainHeaderVariantsNeedATransform(int offset)
    {
        byte[] bytes = ColorProfile.Srgb.IccBytes.ToArray();
        bytes[offset] ^= 1;
        Assert.False(IccData.Parse(bytes).HasSameRgbMatrixShaper(ColorProfile.Srgb.Data));
    }

    [Theory]
    [InlineData("rXYZ")]
    [InlineData("rTRC")]
    [InlineData("desc")]
    public void DuplicateTagSignaturesNeedATransform(string duplicateTag)
    {
        byte[] bytes = Rewrite(ColorProfile.Srgb, _ => { }, duplicateTag);
        IccData duplicate = IccData.Parse(bytes);
        Assert.False(duplicate.HasSameRgbMatrixShaper(ColorProfile.Srgb.Data));
        Assert.False(ColorProfile.Srgb.Data.HasSameRgbMatrixShaper(duplicate));
    }

    [Theory]
    [InlineData(8, 2)] // ICC major version
    [InlineData(9, 32)] // ICC minor version
    [InlineData(12, 112)] // mntr -> pntr is invalid, replaced with prtr below
    [InlineData(20, 76)] // XYZ -> Lab below
    public void HeaderTransformFieldsMustMatch(int offset, byte value)
    {
        byte[] bytes = ColorProfile.Srgb.IccBytes.ToArray();
        bytes[offset] = value;
        if (offset == 12)
        {
            Encoding.ASCII.GetBytes("prtr").CopyTo(bytes, 12);
        }
        else if (offset == 20)
        {
            Encoding.ASCII.GetBytes("Lab ").CopyTo(bytes, 20);
        }

        Assert.False(IccData.Parse(bytes).HasSameRgbMatrixShaper(ColorProfile.Srgb.Data));
    }

    private static byte[] Rewrite(ColorProfile profile, Action<Dictionary<string, byte[]>> edit, string? duplicateTag = null)
    {
        ReadOnlySpan<byte> bytes = profile.IccBytes.Span;
        var tags = new Dictionary<string, byte[]>();
        int count = (int)BinaryPrimitives.ReadUInt32BigEndian(bytes[128..]);
        for (int i = 0; i < count; i++)
        {
            int e = 132 + (i * 12);
            string name = Encoding.ASCII.GetString(bytes.Slice(e, 4));
            int offset = (int)BinaryPrimitives.ReadUInt32BigEndian(bytes[(e + 4)..]);
            int size = (int)BinaryPrimitives.ReadUInt32BigEndian(bytes[(e + 8)..]);
            tags[name] = bytes.Slice(offset, size).ToArray();
        }

        edit(tags);
        var writer = new IccWriter(IccData.Sig("mntr"), "RGB ", "XYZ ", 4, 3);
        foreach (var tag in tags.Reverse())
        {
            writer.Add(tag.Key, tag.Value);
        }

        if (duplicateTag is not null)
        {
            byte[] conflicting = tags[duplicateTag].ToArray();
            conflicting[^1] ^= 1;
            writer.Add(duplicateTag, conflicting);
        }

        return writer.Build();
    }
}
