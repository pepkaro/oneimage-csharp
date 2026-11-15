// SPDX-License-Identifier: MIT
// Copyright (c) 2026 OneImage contributors
// Original evidence harness. Invokes existing production methods without altering source.
using System.Diagnostics;
using System.IO.Compression;
using System.Reflection;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text.Json;
using OneImage;
using OneImage.Pdf;
if(args.Length<4) throw new ArgumentException("render|measure fixture-directory output-prefix dpi [warmups samples batch]");
string mode=args[0],dir=args[1],prefix=args[2];double dpi=double.Parse(args[3]);
if(dpi!=144)throw new ArgumentException("This workload fixes DPI=144 for a 320x192 target.");
byte[] pdf=File.ReadAllBytes(Path.Combine(dir,"reduction-weights.pdf"));
byte[] rgb;using(var z=new ZLibStream(File.OpenRead(Path.Combine(dir,"numeric-raster.rgb.zlib")),CompressionMode.Decompress)){using var ms=new MemoryStream();z.CopyTo(ms);rgb=ms.ToArray();}
const int sw=1009,sh=751,dw=320,dh=192;
if(rgb.Length!=sw*sh*3)throw new InvalidDataException();
var src=new Rgba32[sw*sh];for(int i=0;i<src.Length;i++)src[i]=new Rgba32(rgb[3*i],rgb[3*i+1],rgb[3*i+2],255);
var type=typeof(PdfFormat).Assembly.GetType("OneImage.Pdf.Render.Resize")!;
var method=type.GetMethod("Area",BindingFlags.Static|BindingFlags.Public)!;
var resize=method.CreateDelegate<Func<Rgba32[],int,int,int,int,bool,CancellationToken,Rgba32[]>>();
Rgba32[] Area()=>resize(src,sw,sh,dw,dh,false,default);
string Hash(byte[] a)=>Convert.ToHexString(SHA256.HashData(a)).ToLowerInvariant();
byte[] Raw(Rgba32[] a)=>MemoryMarshal.AsBytes(a.AsSpan()).ToArray();
var opts=new LoadOptions {Configuration=new ImageConfiguration().Add(new PdfFormat(new PdfRenderOptions{Dpi=dpi,SmoothMagnifiedImages=false}))};
Rgba32[] Page(){Image im=Image.Load(pdf,opts);var p=new Rgba32[im.Width*im.Height];im.CopyPixelsTo<Rgba32>(p,new ImageRect(0,0,im.Width,im.Height),maxDegree:1);return p;}
Directory.CreateDirectory(Path.GetDirectoryName(Path.GetFullPath(prefix))!);
var assemblies=new[]{typeof(Image).Assembly,typeof(PdfFormat).Assembly,typeof(OnePdf.PdfDocument).Assembly}.Select(a=>new{file=Path.GetFileName(a.Location),version=a.GetName().Version!.ToString(),sha256=Hash(File.ReadAllBytes(a.Location))}).ToArray();
var metadata=new{runtime=RuntimeInformation.FrameworkDescription,os=RuntimeInformation.OSDescription,architecture=RuntimeInformation.ProcessArchitecture.ToString(),processorCount=Environment.ProcessorCount,dpi,degree=1,background="opaque white",rotation=0,box="CropBox=MediaBox=[0,0,192,128]",smooth=false,sourceWidth=sw,sourceHeight=sh,targetWidth=dw,targetHeight=dh,rgbSha256=Hash(rgb),inputSha256=Hash(pdf),assemblies,environment=new[]{"DOTNET_PROCESSOR_COUNT","DOTNET_TieredCompilation","DOTNET_TieredPGO","COMPlus_TieredCompilation","COMPlus_TieredPGO","DOTNET_GCHeapHardLimit"}.ToDictionary(x=>x,Environment.GetEnvironmentVariable)};
var area=Area();var page=Page();string areaHash=Hash(Raw(area)),pageHash=Hash(Raw(page));
if(mode=="render"){
 File.WriteAllBytes(prefix+"-area.rgba",Raw(area));File.WriteAllBytes(prefix+".rgba",Raw(page));
 Image.FromPixels<Rgba32>(page,384,256).Save(prefix+".png");
 File.WriteAllText(prefix+".json",JsonSerializer.Serialize(new{metadata,width=384,height=256,areaSha256=areaHash,rgbaSha256=pageHash,pngSha256=Hash(File.ReadAllBytes(prefix+".png"))},new JsonSerializerOptions{WriteIndented=true}));
}else if(mode=="measure"){
 int warmups=int.Parse(args[4]),samples=int.Parse(args[5]),batch=int.Parse(args[6]);var records=new List<object>();
 foreach(string boundary in new[]{"production-area-only","fresh-pdf-load-and-render"}){
  var values=new List<double>();var allocated=new List<long>();var allIterations=new List<object>();Func<Rgba32[]> action=boundary=="production-area-only"?Area:Page;string expected=boundary=="production-area-only"?areaHash:pageHash;
  for(int i=-warmups;i<samples;i++){
   Rgba32[]? output=null;long alloc=GC.GetAllocatedBytesForCurrentThread();var watch=Stopwatch.StartNew();for(int j=0;j<batch;j++)output=action();watch.Stop();long used=GC.GetAllocatedBytesForCurrentThread()-alloc;
   string outputHash=Hash(Raw(output!));if(outputHash!=expected)throw new InvalidOperationException("Changed output during timing");
   allIterations.Add(new{phase=i<0?"warmup":"measured",index=i<0?i+warmups:i,elapsedMsPerOperation=watch.Elapsed.TotalMilliseconds/batch,currentThreadAllocatedBytesPerOperation=used/batch,rgbaSha256=outputHash});
   if(i>=0){values.Add(watch.Elapsed.TotalMilliseconds/batch);allocated.Add(used/batch);}
  }
  var sorted=values.Order().ToArray();records.Add(new{boundary,warmups,samples,batch,elapsedMsPerOperation=values,medianMs=sorted[sorted.Length/2],minMs=sorted[0],maxMs=sorted[^1],currentThreadAllocatedBytesPerOperation=allocated,allIterations});
 }
 File.WriteAllText(prefix+".json",JsonSerializer.Serialize(new{metadata,areaSha256=areaHash,rgbaSha256=pageHash,records},new JsonSerializerOptions{WriteIndented=true}));
}else throw new ArgumentException(mode);
Console.WriteLine($"{mode} area={areaHash} page={pageHash}");
