#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 OneImage contributors
"""Render two explicitly supplied original MIT foundation controls; no PDF actions."""
import argparse,hashlib,json,subprocess
from pathlib import Path
import fitz
import pypdfium2 as p
from PIL import Image

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
parser=argparse.ArgumentParser();parser.add_argument('fixtures',type=Path);parser.add_argument('pdfjs_runtime',type=Path);args=parser.parse_args();out=Path(__file__).resolve().parent
report=[]
for name in ['group-performance-40','group-performance-400']:
    source=args.fixtures/(name+'.pdf');initial=sha(source)
    assert source.stat().st_size < 1<<20
    with fitz.open(source) as doc:
        assert len(doc)==1
        pix=doc[0].get_pixmap(matrix=fitz.Matrix(100/72,100/72),alpha=False,annots=True)
        assert pix.width*pix.height <= 1<<20
        pix.save(out/(name+'-mupdf.png'))
    doc=p.PdfDocument(source);doc.init_forms(config=p.raw.FPDF_FORMFILLINFO(version=2,xfa_disabled=True));page=doc[0];bitmap=page.render(scale=100/72,draw_annots=True);bitmap.to_pil().convert('RGB').save(out/(name+'-pdfium.png'));bitmap.close();page.close();doc.close()
    run=subprocess.run(['node',str(out/'render-pdfjs-foundation.mjs'),str(args.pdfjs_runtime.resolve()),str(source.resolve()),str(out/(name+'-pdfjs.png')),'100'],capture_output=True,text=True,timeout=30)
    assert run.returncode==0,run.stderr
    settings=json.loads(run.stdout.strip().splitlines()[-1]);assert initial==sha(source)
    row=dict(input=source.name,inputSha256=initial,dpi=100,settings=dict(mupdf=dict(engine=fitz.VersionFitz,wrapper=fitz.VersionBind,alpha=False,annotations=True),pdfium=dict(engine=str(p.PDFIUM_INFO),wrapper=str(p.PYPDFIUM_INFO),annotations=True,xfa=False),pdfjs=settings),outputs={})
    for engine in ['mupdf','pdfium','pdfjs']:
        path=out/(name+'-'+engine+'.png');row['outputs'][engine]=dict(file=path.name,sha256=sha(path),dimensions=Image.open(path).size)
    report.append(row)
(out/'provenance.json').write_text(json.dumps(dict(schemaVersion=1,license='MIT original inputs and fresh raw outputs; reference runtimes remain external under their own licenses',imageProcessing='None. Full-page native renderer PNGs, no crop, resampling or retouch.',dimensionPolicy='Native100DPI extents ceil to834x1112 for600x800pt pages. OneImage rounds to833x1111; do not claim pixel-grid equality without documenting a matched viewport.',pdfjsBackend='Custom read-only local WASM host adapter with Node Canvas. Not native-browser Canvas; engine internals unchanged. These controls contain no ICCBased input.',adapterSha256=sha(out/'render-pdfjs-foundation.mjs'),rows=report),indent=2)+'\n')
print(json.dumps(report,indent=2))
