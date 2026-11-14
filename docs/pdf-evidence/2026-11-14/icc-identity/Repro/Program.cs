// SPDX-License-Identifier: MIT

using OneImage;
using OneImage.Pdf;

if (args.Length != 3 || args[0] != "render")
{
    throw new ArgumentException("Use: render INPUT.pdf OUTPUT.png");
}

var config = new ImageConfiguration().Add(new PdfFormat(new PdfRenderOptions { Dpi = 96 }));
Image.Load(args[1], new LoadOptions { Configuration = config }).Save(args[2]);
