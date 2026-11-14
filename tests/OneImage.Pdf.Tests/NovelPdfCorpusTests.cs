// SPDX-License-Identifier: MIT
// Copyright (c) 2026 OneImage contributors
using System.Security.Cryptography;
using System.Text.Json;
using OnePdf;
using OnePdf.Text;

namespace OneImage.Pdf.Tests;

/// <summary>Independently authored MIT PDFs, checked against fresh reference renders and document semantics.</summary>
public class NovelPdfCorpusTests
{
    private static readonly string Root = Path.Combine(TestPaths.RepoRoot, "tests", "testdata", "pdf-novel-mit");
    private static readonly JsonElement Manifest = JsonSerializer.Deserialize<JsonElement>(File.ReadAllText(Path.Combine(Root, "manifest.json")));

    public static IEnumerable<object[]> Cases => Manifest.GetProperty("fixtures").EnumerateArray().Select(f => new object[] { f.GetProperty("id").GetString()! });

    private static JsonElement Fixture(string id) => Manifest.GetProperty("fixtures").EnumerateArray().Single(f => f.GetProperty("id").GetString() == id);

    private static byte[] Read(JsonElement fixture)
    {
        byte[] bytes = File.ReadAllBytes(Path.Combine(Root, fixture.GetProperty("file").GetString()!));
        Assert.Equal(fixture.GetProperty("bytes").GetInt32(), bytes.Length);
        Assert.Equal(fixture.GetProperty("sha256").GetString(), Convert.ToHexStringLower(SHA256.HashData(bytes)));
        return bytes;
    }

    [Fact]
    public void InventoryContainsOnlyReproducibleMitCases()
    {
        Assert.Equal("MIT", Manifest.GetProperty("license").GetString());
        Assert.Equal(72, Manifest.GetProperty("dpi").GetInt32());
        JsonElement[] fixtures = Manifest.GetProperty("fixtures").EnumerateArray().ToArray();
        Assert.Equal(40, fixtures.Length);
        Assert.Equal(fixtures.Length, fixtures.Select(f => f.GetProperty("sha256").GetString()).Distinct().Count());
        string[] listed = fixtures.Select(f => Path.GetFileName(f.GetProperty("file").GetString()!)).Order().ToArray();
        Assert.Equal(listed, Directory.GetFiles(Path.Combine(Root, "pdf"), "*.pdf").Select(Path.GetFileName).Order().ToArray());
        foreach (JsonElement fixture in fixtures)
        {
            Assert.Equal("MIT", fixture.GetProperty("license").GetString());
            Assert.InRange(fixture.GetProperty("bytes").GetInt32(), 1, 1 << 20);
            Assert.Single(fixture.GetProperty("pages").EnumerateArray());
        }

        byte[] generator = File.ReadAllBytes(Path.Combine(TestPaths.RepoRoot, Manifest.GetProperty("generator").GetString()!));
        Assert.Equal(Manifest.GetProperty("generatorSha256").GetString(), Convert.ToHexStringLower(SHA256.HashData(generator)));
    }

    [Theory]
    [MemberData(nameof(Cases))]
    public void OriginalBytesAndPageGeometryMatchTheManifest(string id)
    {
        JsonElement fixture = Fixture(id);
        using PdfDocument doc = PdfDocument.Open(Read(fixture));
        JsonElement pages = fixture.GetProperty("pages");
        Assert.Equal(pages.GetArrayLength(), doc.Pages.Count);
        for (int i = 0; i < doc.Pages.Count; i++)
        {
            PdfPage page = doc.Pages[i];
            AssertBox(pages[i].GetProperty("mediaBox"), page.MediaBox);
            AssertBox(pages[i].GetProperty("cropBox"), page.CropBox);
            Assert.Equal(pages[i].GetProperty("rotation").GetInt32(), page.Rotate);
            Assert.Equal(pages[i].GetProperty("annotations").GetInt32(), page.Annotations.Count);
            if (pages[i].TryGetProperty("textContains", out JsonElement text))
            {
                string actual = PdfTextExtractor.Create(doc).ExtractPage(i).Text;
                Assert.Contains(text.GetString()!, actual, StringComparison.Ordinal);
            }
        }
    }

    private static void AssertBox(JsonElement expected, PdfRectangle actual)
    {
        double[] values = [actual.Left, actual.Bottom, actual.Right, actual.Top];
        for (int i = 0; i < values.Length; i++)
        {
            Assert.Equal(expected[i].GetDouble(), values[i], 4);
        }
    }

    private static Image Load(byte[] bytes, int page) => RenderTests.Load(bytes, new PdfRenderOptions
    {
        Dpi = 72,
        FirstPage = page,
        PageCount = 1,
        Limits = new PdfRenderLimits { MaxFileBytes = 1 << 20, MaxImagePixels = 1 << 20, MaxCachedPixels = 1 << 20, MaxNesting = 16, MaxPatternTileSide = 512 },
    });

    [Theory]
    [MemberData(nameof(Cases))]
    public void RenderMatchesIndependentInteriorAndContentExpectations(string id)
    {
        JsonElement fixture = Fixture(id);
        if (fixture.TryGetProperty("knownFailure", out JsonElement failure))
        {
            Assert.SkipUnless(Environment.GetEnvironmentVariable("ONEIMAGE_PDF_NOVEL_KNOWN_FAILURES") == "1", failure.GetString()!);
        }

        using var timeout = new CancellationTokenSource(TimeSpan.FromSeconds(15));
        byte[] bytes = Read(fixture);
        JsonElement pages = fixture.GetProperty("pages");
        for (int page = 0; page < pages.GetArrayLength(); page++)
        {
            JsonElement expected = pages[page];
            Image image = Load(bytes, page);
            int width = expected.GetProperty("renderWidth").GetInt32();
            int height = expected.GetProperty("renderHeight").GetInt32();
            Assert.Equal(width, image.Width);
            Assert.Equal(height, image.Height);
            Rgba32[] pixels = image.ToArray<Rgba32>(maxDegree: 1, cancellationToken: timeout.Token);
            foreach (JsonElement probe in expected.GetProperty("probes").EnumerateArray())
            {
                int x = probe.GetProperty("x").GetInt32(), y = probe.GetProperty("y").GetInt32();
                Rgba32 actual = pixels[(y * width) + x];
                JsonElement rgb = probe.GetProperty("rgb");
                int tolerance = probe.GetProperty("tolerance").GetInt32();
                Assert.True(Math.Abs(actual.R - rgb[0].GetInt32()) <= tolerance && Math.Abs(actual.G - rgb[1].GetInt32()) <= tolerance && Math.Abs(actual.B - rgb[2].GetInt32()) <= tolerance,
                    $"{id}, page {page}, ({x},{y}): expected {rgb} +/- {tolerance}, got {actual}");
                Assert.Equal(255, actual.A);
            }

            if (expected.TryGetProperty("channelChecks", out JsonElement checks))
            {
                foreach (JsonElement check in checks.EnumerateArray())
                {
                    int x = check.GetProperty("x").GetInt32(), y = check.GetProperty("y").GetInt32();
                    Rgba32 actual = pixels[(y * width) + x];
                    byte[] channels = [actual.R, actual.G, actual.B];
                    JsonElement ranges = check.GetProperty("ranges");
                    for (int c = 0; c < 3; c++)
                    {
                        Assert.InRange((int)channels[c], ranges[c][0].GetInt32(), ranges[c][1].GetInt32());
                    }
                }
            }

            int ink = 0;
            JsonElement bounds = expected.GetProperty("inkBounds");
            for (int y = 0; y < height; y++)
            {
                for (int x = 0; x < width; x++)
                {
                    Rgba32 p = pixels[(y * width) + x];
                    if (p.R < 235 || p.G < 235 || p.B < 235)
                    {
                        ink++;
                        Assert.True(x >= bounds[0].GetInt32() && y >= bounds[1].GetInt32() && x <= bounds[2].GetInt32() && y <= bounds[3].GetInt32(), $"{id}, page {page}: unexpected ink at {x},{y}");
                    }
                }
            }

            Assert.InRange(ink, expected.GetProperty("inkMin").GetInt32(), expected.GetProperty("inkMax").GetInt32());
        }
    }

    [Theory]
    [MemberData(nameof(Cases))]
    public void FreshRegionsAndParallelRenderingMatchSerialRendering(string id)
    {
        JsonElement fixture = Fixture(id);
        byte[] bytes = Read(fixture);
        using var timeout = new CancellationTokenSource(TimeSpan.FromSeconds(15));
        for (int page = 0; page < fixture.GetProperty("pages").GetArrayLength(); page++)
        {
            Image image = Load(bytes, page);
            int width = image.Width, height = image.Height;
            Rgba32[] serial = image.ToArray<Rgba32>(maxDegree: 1, cancellationToken: timeout.Token);
            Assert.Equal(serial, Load(bytes, page).ToArray<Rgba32>(maxDegree: 4, cancellationToken: timeout.Token));
            ImageRect[] regions =
            [
                new(0, 0, 1, 1),
                new(width / 3, height / 3, Math.Min(67, width - (width / 3)), Math.Min(47, height - (height / 3))),
                new(width - Math.Min(19, width), height - Math.Min(23, height), Math.Min(19, width), Math.Min(23, height)),
            ];
            foreach (ImageRect region in regions)
            {
                var pixels = new Rgba32[region.Width * region.Height];
                Load(bytes, page).CopyPixelsTo<Rgba32>(pixels, region, maxDegree: 4, cancellationToken: timeout.Token);
                for (int y = 0; y < region.Height; y++)
                {
                    Assert.True(pixels.AsSpan(y * region.Width, region.Width).SequenceEqual(serial.AsSpan(((region.Y + y) * width) + region.X, region.Width)), $"{id}, page {page}, region {region}, row {y}");
                }
            }
        }
    }
}
