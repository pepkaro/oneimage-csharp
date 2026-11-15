# SPDX-License-Identifier: MIT
# Copyright (c) 2026 OneImage contributors
"""Original numerical image/mask probes. No imported artwork, PDF bytes, fonts, or ICC profiles."""
from pathlib import Path
import json, hashlib, argparse
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--out',type=Path,required=True,help='Directory for generated fixture PDFs and manifest')
ROOT=parser.parse_args().out
ROOT.mkdir(parents=True,exist_ok=True)
OUT=ROOT/'fixtures'; OUT.mkdir(exist_ok=True)
def stream(d,data):
    data=data.encode() if isinstance(data,str) else data
    return f'<< {d} /Length {len(data)} >>\nstream\n'.encode()+data+b'\nendstream'
def pdf(name,cw,ch,mw,mh,kind='partial',ci=False,mi=False,matte=False,placement='210 0 0 198 15 12',stencil=False,decode=False):
    colors=bytes(v for y in range(ch) for x in range(cw) for v in (37+(x*59+y*17)%197,29+(x*31+y*67)%211,19+(x*83+y*43)%223))
    a=bytes((255 if kind=='opaque' else [0,91,173,255][(x+3*y)%4]) for y in range(mh) for x in range(mw))
    if kind=='hidden': colors=bytes([250,5,20,15,230,60]);a=bytes([0,255])
    if matte: colors=bytes([128,128,128,128,255,128]); a=bytes([128,128])
    if stencil:
        a=bytes((0 if (x+2*y)%3==0 else 255) for y in range(mh) for x in range(mw))
        packed=bytearray(((mw+7)//8)*mh)
        for y in range(mh):
            for x in range(mw):
                if (a[y*mw+x]>0 if decode else a[y*mw+x]==0): packed[y*((mw+7)//8)+x//8]|=128>>(x%8)
        a=bytes(packed)
    elif decode: a=bytes(255-v for v in a)
    content=f'q {placement} cm /Im Do Q'
    objects=[b'<< /Type /Catalog /Pages 2 0 R >>',b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>',b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 240 222] /Contents 4 0 R /Resources << /XObject << /Im 5 0 R >> >> >>',stream('',content),stream(f'/Type /XObject /Subtype /Image /Width {cw} /Height {ch} /ColorSpace /DeviceRGB /BitsPerComponent 8 /Interpolate {str(ci).lower()} '+(('/Mask 6 0 R ' if stencil else '/SMask 6 0 R ') if mw else '')+'/Filter /ASCIIHexDecode',colors.hex()+'>')]
    if mw: objects.append(stream(f'/Type /XObject /Subtype /Image /Width {mw} /Height {mh} {('/ImageMask true /BitsPerComponent 1' if stencil else '/ColorSpace /DeviceGray /BitsPerComponent 8')} /Decode [{('1 0' if decode else '0 1')}] /Interpolate {str(mi).lower()} '+('/Matte [1 1 1] ' if matte else '')+'/Filter /ASCIIHexDecode',a.hex()+'>'))
    b=b'%PDF-1.7\n% Original MIT numerical fixture\n'; offsets=[]
    for i,o in enumerate(objects,1): offsets.append(len(b));b+=f'{i} 0 obj\n'.encode()+o+b'\nendobj\n'
    xref=len(b);b+=f'xref\n0 {len(objects)+1}\n0000000000 65535 f \n'.encode()
    b+=b''.join(f'{n:010d} 00000 n \n'.encode() for n in offsets)
    b+=f'trailer\n<< /Size {len(objects)+1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n'.encode()
    (OUT/(name+'.pdf')).write_bytes(b)
    return {'name':name,'color':[cw,ch],'mask':[mw,mh],'kind':kind,'colorInterpolate':ci,'maskInterpolate':mi,'matte':matte,'placement':placement,'stencil':stencil,'decode':decode,'sha256':hashlib.sha256(b).hexdigest()}
items=[]
for cw,ch,mw,mh in [(3,5,7,11),(11,7,3,5),(3,11,7,5),(11,3,5,7)]:
    for kind in ['none','opaque','partial']:
        items.append(pdf(f'{cw}x{ch}-{mw}x{mh}-{kind}',cw,ch,0 if kind=='none' else mw,mh,kind))
for ci in [False,True]:
    for mi in [False,True]:
        items.append(pdf(f'flags-{int(ci)}-{int(mi)}',3,5,7,11,ci=ci,mi=mi))
        items.append(pdf(f'equal-flags-{int(ci)}-{int(mi)}',3,5,3,5,ci=ci,mi=mi))
        items.append(pdf(f'hidden-flags-{int(ci)}-{int(mi)}',2,1,2,1,kind='hidden',ci=ci,mi=mi))
items.append(pdf('matte-matched',2,1,2,1,ci=True,mi=True,matte=True))
for name,placement in [('skew','183 23 -19 169 36 16'),('reflect','-210 0 0 198 225 12'),('rotate','0 198 -210 0 225 12')]:
    items.append(pdf('transform-'+name,3,11,7,5,placement=placement))
for stencil in [False,True]:
    for decode in [False,True]:
        items.append(pdf(f'mask-kind-{int(stencil)}-decode-{int(decode)}',3,5,7,11,stencil=stencil,decode=decode))
items.append(pdf('crossed-axis-reduction',401,1,1,409))
(ROOT/'fixtures.json').write_text(json.dumps(items,indent=2)+'\n')
