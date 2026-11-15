# SPDX-License-Identifier: MIT
# Copyright (c) 2026 OneImage contributors
# Independent box-area expectation from integer interval intersections; not renderer/test source.
from pathlib import Path
import zlib,hashlib,json,sys
import numpy as np
from PIL import Image
from pypdf import PdfReader
R=Path(__file__).resolve().parents[1]
s=json.loads((R/'fixtures/source.json').read_text());sw,sh,dw,dh=[s[k] for k in ['width','height','targetWidth','targetHeight']]
rgb=zlib.decompress((R/'fixtures/numeric-raster.rgb.zlib').read_bytes());src=np.frombuffer(rgb,dtype=np.uint8).reshape(sh,sw,3)
# All overlaps use integer endpoints in the product coordinate system.
def weights(source,dest):
 left=np.maximum(np.arange(dest)[:,None]*source,np.arange(source)[None,:]*dest)
 right=np.minimum((np.arange(dest)[:,None]+1)*source,(np.arange(source)[None,:]+1)*dest)
 return np.maximum(0,right-left).astype(np.float64)/source
wx,wy=weights(sw,dw),weights(sh,dh)
expected=np.stack([wy@src[:,:,k].astype(np.float64)@wx.T for k in range(3)],axis=2)
ideal=np.floor(expected+.5).astype(np.uint8)
area={side:np.frombuffer((R/'renders'/f'reduction-weights-{side}-area.rgba').read_bytes(),dtype=np.uint8).reshape(dh,dw,4) for side in ['before','after']}
page={side:np.asarray(Image.open(R/'renders'/f'reduction-weights-{side}.png').convert('RGBA')) for side in ['before','after']}
out={'formula':'Each destination pixel is the weighted mean of source samples, using exact integer interval-overlap lengths on both axes and double precision for this independent expectation. Compare nearest rounded bytes; allow float accumulation difference of 1 byte.','sourceRawRgbSha256':hashlib.sha256(rgb).hexdigest(),'sourceInsidePdfMatches':PdfReader(R/'fixtures/reduction-weights.pdf').pages[0]['/Resources']['/XObject']['/Im'].get_data()==rgb,'cacheActivatedByParameters':sh>1 and sw<=16384,'weightCalculationCountBefore':sw*sh,'weightCalculationCountAfter':sw,'fullAreaChangedPixels':int(np.any(area['before']!=area['after'],axis=2).sum()),'fullPageChangedPixels':int(np.any(page['before']!=page['after'],axis=2).sum()),'samples':{},'references':{}}
for side in ['before','after']:
 a=area[side][:,:,:3];delta=np.abs(a.astype(int)-ideal.astype(int));out[side]={'areaVsIndependentRoundedMaxChannelError':int(delta.max()),'areaVsIndependentRoundedMeanAbsoluteError':float(delta.mean()),'areaPixelsAbove1Byte':int(np.any(delta>1,axis=2).sum()),'pdfInteriorExactlyMatchesAreaOutput':bool(np.array_equal(page[side][32:224,32:352],area[side])),'pngDecodesToStoredRgba':Image.open(R/'renders'/f'reduction-weights-{side}.png').convert('RGBA').tobytes()==(R/'renders'/f'reduction-weights-{side}.rgba').read_bytes()}
 assert delta.max()<=1
 assert out[side]['pdfInteriorExactlyMatchesAreaOutput']
 assert out[side]['pngDecodesToStoredRgba']
 assert bool(np.all(area[side][:,:,3]==255))
for x,y,c in [(46,44,[25,83,141]),(337,44,[187,49,101]),(192,212,[43,179,89])]:
 out['samples'][str((x,y))]={'expected':c,**{side:page[side][y,x,:3].tolist() for side in page}}
 for side in page:assert page[side][y,x,:3].tolist()==c
for engine in ['pdfium','mupdf','pdfjs']:
 a=np.asarray(Image.open(R/'references'/f'reduction-weights-{engine}.png').convert('RGB'));delta=np.abs(a.astype(int)-page['after'][:,:,:3].astype(int));out['references'][engine]={'nativeDimensions':[a.shape[1],a.shape[0]],'meanAbsoluteRGBDifferenceFromBoth':float(delta.mean()),'pixelsAbove8':int(np.any(delta>8,axis=2).sum()),'maxChannelDifference':int(delta.max())}
assert out['sourceInsidePdfMatches'] and out['fullAreaChangedPixels']==0 and out['fullPageChangedPixels']==0
(R/'analytic-checks.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
