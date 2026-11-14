using System.Globalization;
using System.IO;
using System.Text;
using BenchmarkDotNet.Attributes;
using OneImage.Pdf;
namespace OneImage.Benchmarks.Pdf;
/// <summary>Generated narrow non-isolated transparency groups. No external PDF is needed to reproduce the workload.</summary>
[MemoryDiagnoser]
public class PdfNarrowGroupBenchmarks
{
    private byte[] _bytes = null!;
    private LoadOptions _options = null!;
    private Rgba32[] _pixels = null!;
    private int _width, _height;
    [Params(40, 400)] public int Groups { get; set; }
    [Params(1, 4)] public int Degree { get; set; }
    [GlobalSetup]
    public void Setup()
    {
        _bytes = Document(Groups);
        _options = new LoadOptions { Configuration = new ImageConfiguration().Add(new PdfFormat(new PdfRenderOptions { Dpi = 100 })) };
        Image image = Image.Load(_bytes, _options);
        _width = image.Width;
        _height = image.Height;
        _pixels = new Rgba32[_width * _height];
    }
    [Benchmark(Description = "PDF narrow translucent groups: load + render")]
    public Rgba32 Render()
    {
        Image.Load(_bytes, _options).CopyPixelsTo<Rgba32>(_pixels, new ImageRect(0, 0, _width, _height), maxDegree: Degree);
        return _pixels[_pixels.Length / 2];
    }
    private static byte[] Document(int groups)
    {
        var content = new StringBuilder("0.8 0.4 0.2 rg 0 0 600 800 re f\n");
        for (int i = 0; i < groups; i++)
        {
            double y = 10 + (780.0 * i / groups);
            content.Append(CultureInfo.InvariantCulture, $"q 1 0 0 1 10 {y:R} cm /G gs /F0 Do Q\n");
        }
        const string form = "0.1 0.7 0.4 RG 0.5 w 0 0.25 m 580 0.25 l S";
        string[] objects =
        [
            "<< /Type /Catalog /Pages 2 0 R >>",
            "<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
            "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 600 800] /Contents 4 0 R /Resources << /XObject << /F0 5 0 R >> /ExtGState << /G << /ca 0.75 /CA 0.75 >> >> >> >>",
            StreamObject("", content.ToString()),
            StreamObject("/Type /XObject /Subtype /Form /BBox [0 0 580 0.5] /Group << /S /Transparency /I false /K false >> /Resources << >>", form),
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
            Write(offset.ToString("D10", CultureInfo.InvariantCulture) + " 00000 n \n");
        Write(FormattableString.Invariant($"trailer\n<< /Size {objects.Length + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n"));
        return output.ToArray();
    }
    private static string StreamObject(string dictionary, string content) =>
        FormattableString.Invariant($"<< {dictionary} /Length {content.Length} >>\nstream\n{content}\nendstream");
}
