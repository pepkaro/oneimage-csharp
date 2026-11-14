#!/usr/bin/env python3
"""Original MIT-licensed deterministic PDF fixtures written for this evidence package.

No external documents, installed fonts, or private assets are read.
The numerical case recreates the original benchmark introduced by c705783.
No upstream PDF or upstream fixture bytes are copied. See PROVENANCE.md.
"""
import base64
import hashlib
import json
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "fixtures"
OUT.mkdir(exist_ok=True)


def stream(entries, data):
    if isinstance(data, str):
        data = data.encode("latin1")
    return f"<< {entries} /Length {len(data)} >>\nstream\n".encode() + data + b"\nendstream"


def page(content, resources="", width=20, height=20, extra=()):
    objects = [b"<< /Type /Catalog /Pages 2 0 R >>",
               b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
               f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {width} {height}] /Contents 4 0 R /Resources << {resources} >> >>".encode(),
               stream("", content), *extra]
    result = bytearray(b"%PDF-1.7\n")
    offsets = []
    for i, obj in enumerate(objects, 1):
        offsets.append(len(result))
        result.extend(f"{i} 0 obj\n".encode())
        result.extend(obj.encode("latin1") if isinstance(obj, str) else obj)
        result.extend(b"\nendobj\n")
    xref = len(result)
    result.extend(f"xref\n0 {len(objects)+1}\n0000000000 65535 f \n".encode())
    for offset in offsets:
        result.extend(f"{offset:010d} 00000 n \n".encode())
    result.extend(f"trailer\n<< /Size {len(objects)+1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode())
    return bytes(result)


manifest = []
def save(name, pdf, dpi, source, *, unit, smooth=False):
    path = OUT / f"{name}.pdf"
    path.write_bytes(pdf)
    manifest.append(dict(name=name, file=f"fixtures/{name}.pdf", sha256=hashlib.sha256(pdf).hexdigest(),
                         dpi=dpi, page=0, box="CropBox (falls back to MediaBox)", rotation=0,
                         background=[255,255,255,255], maxDegree=1, smoothMagnifiedImages=smooth,
                         source=source, unit=unit))


# Exact benchmark geometry, independent of external PDFs.
for groups in (40,400):
    content = "0.8 0.4 0.2 rg 0 0 600 800 re f\n" + "".join(
        f"q 1 0 0 1 10 {10+780.0*i/groups:.17g} cm /G gs /F0 Do Q\n" for i in range(groups))
    form = stream("/Type /XObject /Subtype /Form /BBox [0 0 580 0.5] /Group << /S /Transparency /I false /K false >> /Resources << >>",
                  "0.1 0.7 0.4 RG 0.5 w 0 0.25 m 580 0.25 l S")
    save(f"group-performance-{groups}", page(content,"/XObject << /F0 5 0 R >> /ExtGState << /G << /ca 0.75 /CA 0.75 >> >>",600,800,[form]),
         100,"bench/OneImage.Benchmarks/Pdf/PdfNarrowGroupBenchmarks.cs:Document",unit=1)


(ROOT/"fixtures.json").write_text(json.dumps(manifest,indent=2)+"\n")
print(f"Generated {len(manifest)} original fixtures.")
