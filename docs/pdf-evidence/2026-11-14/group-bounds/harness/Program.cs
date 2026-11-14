using System.Diagnostics;
using System.Reflection;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text.Json;
using OneImage;
using OneImage.Pdf;

if (args.Length < 6) throw new ArgumentException("render|measure input.pdf output-prefix dpi degree smooth [warmups samples]");
string mode=args[0],input=args[1],prefix=args[2];
double dpi=double.Parse(args[3],System.Globalization.CultureInfo.InvariantCulture);
int degree=int.Parse(args[4]);
bool smooth=bool.Parse(args[5]);
var pdfOptions=new PdfRenderOptions { Dpi=dpi };
if(smooth)
{
    var property=typeof(PdfRenderOptions).GetProperty("SmoothMagnifiedImages") ?? throw new InvalidOperationException("This baseline has no smoothing option.");
    property.SetValue(pdfOptions,true);
}
var loadOptions=new LoadOptions { Configuration=new ImageConfiguration().Add(new PdfFormat(pdfOptions)) };
byte[] bytes=File.ReadAllBytes(input);
string Hash(ReadOnlySpan<byte> data)=>Convert.ToHexString(SHA256.HashData(data)).ToLowerInvariant();
string HashFile(string path)=>Hash(File.ReadAllBytes(path));
var assemblies=new[]{typeof(Image).Assembly,typeof(PdfFormat).Assembly,typeof(OnePdf.PdfDocument).Assembly}
    .Select(a=>new { file=Path.GetFileName(a.Location),name=a.GetName().Name,version=a.GetName().Version?.ToString(),sha256=HashFile(a.Location) }).ToArray();
var metadata=new { runtime=RuntimeInformation.FrameworkDescription,os=RuntimeInformation.OSDescription,architecture=RuntimeInformation.ProcessArchitecture.ToString(),processorCount=Environment.ProcessorCount,
    environment=new[]{"DOTNET_PROCESSOR_COUNT","DOTNET_TieredCompilation","DOTNET_TieredPGO","DOTNET_GCHeapHardLimit","COMPlus_TieredCompilation","COMPlus_TieredPGO"}.ToDictionary(k=>k,Environment.GetEnvironmentVariable),
    dpi,degree,smoothMagnifiedImages=smooth,page=0,background="opaque white",box="CropBox (falls back to MediaBox)",rotation=0,inputSha256=Hash(bytes),assemblies };
Image image=Image.Load(bytes,loadOptions);
int width=image.Width,height=image.Height;
Rgba32[] pixels=new Rgba32[width*height];
void Read(Image source)=>source.CopyPixelsTo<Rgba32>(pixels,new ImageRect(0,0,width,height),maxDegree:degree);
Read(image);
string rgbaHash=Hash(MemoryMarshal.AsBytes(pixels.AsSpan()));
Directory.CreateDirectory(Path.GetDirectoryName(Path.GetFullPath(prefix))!);
if(mode=="render")
{
    // Encode the exact copied RGBA array, without pixel modifications or resizing.
    Image.FromPixels<Rgba32>(pixels,width,height).Save(prefix+".png");
    File.WriteAllBytes(prefix+".rgba",MemoryMarshal.AsBytes(pixels.AsSpan()).ToArray());
    File.WriteAllText(prefix+".json",JsonSerializer.Serialize(new { metadata,width,height,rgbaSha256=rgbaHash,pngSha256=HashFile(prefix+".png") },new JsonSerializerOptions{WriteIndented=true}));
}
else if(mode=="measure")
{
    int warmups=int.Parse(args[6]),samples=int.Parse(args[7]);
    var records=new List<object>();
    foreach(string boundary in new[]{"load+render","retained-uncached-raster"})
    {
        var values=new List<double>();
        var sw=new Stopwatch();
        for(int i=-warmups;i<samples;i++)
        {
            sw.Restart();
            if(boundary=="load+render") image=Image.Load(bytes,loadOptions);
            else image.ReleaseDecodedPixels();
            Read(image);
            sw.Stop();
            if(Hash(MemoryMarshal.AsBytes(pixels.AsSpan()))!=rgbaHash) throw new InvalidOperationException("Timed render changed pixels.");
            if(i>=0) values.Add(sw.Elapsed.TotalMilliseconds);
        }
        records.Add(new { boundary,warmups,samples,elapsedMs=values,medianMs=values.Order().ElementAt(values.Count/2),minMs=values.Min(),maxMs=values.Max() });
    }
    File.WriteAllText(prefix+".json",JsonSerializer.Serialize(new { metadata,width,height,rgbaSha256=rgbaHash,records },new JsonSerializerOptions{WriteIndented=true}));
}
else throw new ArgumentException("Unknown operation.");
Console.WriteLine($"{mode}: {Path.GetFileName(input)} {width}x{height} rgba={rgbaHash}");
