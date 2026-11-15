// SPDX-License-Identifier: MIT
// Copyright (c) 2026 OneImage contributors
using System.Security.Cryptography;
using System.Text.Json;

namespace OneImage.Pdf.Tests;

/// <summary>Original numerical mask-selection regressions (ISO 32000-1 11.6.4.2–4 and Table 89).</summary>
public class ImageMaskPrecedenceTests
{
    private static string Root => Path.Combine(TestPaths.RepoRoot, "testdata", "pdf", "image-mask-precedence");

    public static IEnumerable<object[]> Cases()
    {
        using JsonDocument manifest = JsonDocument.Parse(File.ReadAllText(Path.Combine(Root, "manifest.json")));
        foreach (JsonElement fixture in manifest.RootElement.GetProperty("fixtures").EnumerateArray())
        {
            yield return [fixture.GetProperty("id").GetString()!];
        }
    }

    [Theory]
    [MemberData(nameof(Cases))]
    public void ImageMasksOverrideStateOnlyForTheirOwnPaint(string id)
    {
        using JsonDocument manifest = JsonDocument.Parse(File.ReadAllText(Path.Combine(Root, "manifest.json")));
        JsonElement fixture = manifest.RootElement.GetProperty("fixtures").EnumerateArray().Single(f => f.GetProperty("id").GetString() == id);
        byte[] pdf = File.ReadAllBytes(Path.Combine(Root, fixture.GetProperty("file").GetString()!));
        Assert.Equal(fixture.GetProperty("sha256").GetString(), Convert.ToHexStringLower(SHA256.HashData(pdf)));
        Image image = RenderTests.Load(pdf, new PdfRenderOptions { Dpi = 72, Background = new Rgba32(255, 255, 255, 255) });
        Assert.Equal(fixture.GetProperty("width").GetInt32(), image.Width);
        Assert.Equal(fixture.GetProperty("height").GetInt32(), image.Height);
        Rgba32[] pixels = image.ToArray<Rgba32>(maxDegree: 1);
        // A fresh document/render graph avoids satisfying this check from cached serial pixels.
        Image parallelImage = RenderTests.Load(pdf, new PdfRenderOptions { Dpi = 72, Background = new Rgba32(255, 255, 255, 255) });
        Assert.True(pixels.AsSpan().SequenceEqual(parallelImage.ToArray<Rgba32>(maxDegree: 4)), "Independent serial/parallel mismatch");
        foreach (JsonElement region in fixture.GetProperty("expectedRegions").EnumerateArray())
        {
            int[] rect = region.GetProperty("rect").EnumerateArray().Select(v => v.GetInt32()).ToArray();
            double[] expected = region.GetProperty("rgb").EnumerateArray().Select(v => v.GetDouble()).ToArray();
            double tolerance = region.GetProperty("tolerance").GetDouble();
            string? purpose = region.GetProperty("purpose").GetString();
            for (int y = rect[1]; y < rect[1] + rect[3]; y++)
            for (int x = rect[0]; x < rect[0] + rect[2]; x++)
            {
                Rgba32 p = pixels[(y * image.Width) + x];
                Assert.True(Math.Abs(p.R - expected[0]) <= tolerance && Math.Abs(p.G - expected[1]) <= tolerance && Math.Abs(p.B - expected[2]) <= tolerance && p.A == 255,
                    $"{id}: {purpose} ({x},{y}), expected ({expected[0]:F3},{expected[1]:F3},{expected[2]:F3},255) ±{tolerance}, got {p}");
            }
        }
    }
}
