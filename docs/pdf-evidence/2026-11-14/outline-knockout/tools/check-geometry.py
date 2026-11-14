# SPDX-License-Identifier: MIT
# Copyright (c) 2026 OneImage contributors
from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,io,fontTools,sys
from fontTools.cffLib import CFFFontSet
from pypdf import PdfReader
r=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parents[1];o={}
if (r/'fixtures/novel-wedge.cff').exists():
 b=(r/'fixtures/novel-wedge.cff').read_bytes();cff=CFFFontSet();cff.decompile(io.BytesIO(b),None);top=cff.topDictIndex[0]
 programs={}
 for name in top.charset:
  cs=top.CharStrings[name];cs.decompile();programs[name]=cs.program
 embedded=PdfReader(r/'fixtures/outline-knockout.pdf').pages[0]['/Resources']['/Font']['/F']['/FontDescriptor']['/FontFile3'].get_data()
 o['font']={'fontToolsVersion':fontTools.__version__,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'embeddedMatches':b==embedded,'fontNames':cff.fontNames,'charset':top.charset,'programs':programs,'privateDict':top.Private.rawDict,'globalSubrs':len(cff.GlobalSubrs)}
for n in ['device-hairlines','outline-knockout','image-edge-clip']:
 if not (r/'fixtures'/f'{n}.pdf').exists():continue
 o[n]={}
 for s in ['before','after','pdfium','mupdf','pdfjs']:
  p=r/('renders' if s in ['before','after'] else 'references')/f'{n}-{s}.png';a=np.array(Image.open(p).convert('RGB')).astype(int)
  if n=='device-hairlines':
   x=a[:,:128];pairs=[]
   for i in [1,2]:
    d=abs(x-a[:,128*i:128*(i+1)]);pairs.append({'changedPixels':int(np.any(d,axis=2).sum()),'maxChannelDifference':int(d.max())})
   o[n][s]={'columnsVersusFirst':pairs,'horizontalBarPixelRGB':a[215,40].tolist(),'verticalBarPixelRGB':a[200,62].tolist()}
  if n=='image-edge-clip':
   d=abs(a[0:124]-a[124:248]);o[n][s]={'topVsBottomTranslated124px':{'changedPixels':int(np.any(d,axis=2).sum()),'maxChannelDifference':int(d.max())}}
  if n=='outline-knockout':
   # x=60,y=184 lies in lower stroke band inside fill; y=194 outside fill in same band.
   o[n][s]={'innerStroke':a[184,60].tolist(),'outerStroke':a[194,60].tolist(),'fill':a[150,60].tolist(),'modes2vs6ChangedPixels':int(np.any(a[:,:192]!=a[:,192:],axis=2).sum())}
print(json.dumps(o,indent=2))
