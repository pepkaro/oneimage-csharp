using System.Globalization;
using System.IO;
using System.Text;
using BenchmarkDotNet.Attributes;
using OneImage.Pdf;

namespace OneImage.Benchmarks.Pdf;

/// <summary>Generated clipped images, including redundant clips and geometry that must keep the existing fallback.</summary>
[MemoryDiagnoser]
public class PdfImageClipBenchmarks
{
    private byte[] _bytes = null!;
    private LoadOptions _options = null!;
    private Image _retained = null!;
    private Rgba32[] _pixels = null!;

    [Params("none", "identical", "rotated", "partial", "curve", "convex8", "convex9", "convex64", "complex")]
    public string Clip { get; set; } = "identical";

    [Params(1, 4)]
    public int Degree { get; set; }

    [GlobalSetup]
    public void Setup()
    {
        _bytes = Document(Clip);
        _options = new LoadOptions { Configuration = new ImageConfiguration().Add(new PdfFormat(new PdfRenderOptions { Dpi = 96 })) };
        _retained = Image.Load(_bytes, _options);
        _pixels = new Rgba32[_retained.Width * _retained.Height];
        _retained.CopyPixelsTo<Rgba32>(_pixels, new ImageRect(0, 0, _retained.Width, _retained.Height), maxDegree: Degree);
    }

    [Benchmark(Description = "PDF clipped images: load + render")]
    public Rgba32 Render()
    {
        Image.Load(_bytes, _options).CopyPixelsTo<Rgba32>(_pixels, new ImageRect(0, 0, _retained.Width, _retained.Height), maxDegree: Degree);
        return _pixels[_pixels.Length / 2];
    }

    [Benchmark(Description = "PDF clipped images: retained document, uncached raster")]
    public Rgba32 Rerender()
    {
        _retained.ReleaseDecodedPixels();
        _retained.CopyPixelsTo<Rgba32>(_pixels, new ImageRect(0, 0, _retained.Width, _retained.Height), maxDegree: Degree);
        return _pixels[_pixels.Length / 2];
    }

    private static byte[] Document(string clip)
    {
        string clipping = clip switch
        {
            "none" => "",
            "identical" or "rotated" => "0 0 1 1 re W n",
            "partial" => "0 0 0.75 1 re W n",
            "curve" => "0 0 m 1 0 1 1 0 1 c h W n",
            "convex8" => PolygonClip(8, 0.8),
            "convex9" => PolygonClip(9, 0.8),
            "convex64" => PolygonClip(64, 0.8),
            "complex" => PolygonClip(128, 0.6),
            _ => throw new ArgumentOutOfRangeException(nameof(clip)),
        };
        var content = new StringBuilder();
        for (int row = 0; row < 4; row++)
        {
            for (int col = 0; col < 4; col++)
            {
                content.Append(CultureInfo.InvariantCulture, $"q 1 0 0 1 {5.25 + (col * 96)} {5.25 + (row * 96)} cm ");
                content.Append(clip == "rotated" ? "70 12 -12 70 12 0 cm " : "85.5 0 0 85.5 0 0 cm ");
                content.Append(clipping).Append(" /Im Do Q\n");
            }
        }

        string[] objects =
        [
            "<< /Type /Catalog /Pages 2 0 R >>",
            "<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
            "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 384 384] /Contents 4 0 R /Resources << /XObject << /Im 5 0 R >> >> >>",
            StreamObject("", content.ToString()),
            StreamObject("/Type /XObject /Subtype /Image /Width 2 /Height 2 /ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /ASCIIHexDecode", "1e1923c0804020b0607080a0>"),
        ];
        using var output = new MemoryStream();
        void Write(string value) => output.Write(Encoding.ASCII.GetBytes(value));
        Write("%PDF-1.7\n");
        var offsets = new long[objects.Length];
        for (int i = 0; i < objects.Length; i++)
        {
            offsets[i] = output.Position;
            Write(FormattableString.Invariant($"{i + 1} 0 obj\n{objects[i]}\nendobj\n"));
        }

        long xref = output.Position;
        Write(FormattableString.Invariant($"xref\n0 {objects.Length + 1}\n0000000000 65535 f \n"));
        foreach (long offset in offsets)
        {
            Write(offset.ToString("D10", CultureInfo.InvariantCulture) + " 00000 n \n");
        }

        Write(FormattableString.Invariant($"trailer\n<< /Size {objects.Length + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n"));
        return output.ToArray();
    }

    private static string PolygonClip(int count, double radius)
    {
        var b = new StringBuilder();
        for (int i = 0; i < count; i++)
        {
            double angle = i * 2 * Math.PI / count;
            b.Append(CultureInfo.InvariantCulture, $"{0.5 + (radius * Math.Cos(angle)):R} {0.5 + (radius * Math.Sin(angle)):R} {(i == 0 ? "m" : "l")} ");
        }

        return b.Append("h W n").ToString();
    }

    private static string StreamObject(string dictionary, string content) =>
        FormattableString.Invariant($"<< {dictionary} /Length {content.Length} >>\nstream\n{content}\nendstream");
}
