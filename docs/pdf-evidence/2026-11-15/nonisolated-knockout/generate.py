#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Original knockout-group geometry and equations; no external document or artwork inputs."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parent
B=[.2,.6,.8,1];S=[.8,.4,.2,1];T=[.1,.8,.3,1];W=[1,1,1,1]
def stream(entries,body):
 return f'<< {entries} /Length {len(body.encode("latin1"))} >>\nstream\n{body}\nendstream'
def pdf(content,resources,extra):
 objects=['<< /Type /Catalog /Pages 2 0 R >>','<< /Type /Pages /Kids [3 0 R] /Count 1 >>',f'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 96 96] /Contents 4 0 R /Resources << {resources} >> >>',stream('',content),*extra]
 out=b'%PDF-1.7\n';offsets=[]
 for i,o in enumerate(objects,1):offsets.append(len(out));out+=f'{i} 0 obj\n{o}\nendobj\n'.encode('latin1')
 xref=len(out);out+=f'xref\n0 {len(objects)+1}\n0000000000 65535 f \n'.encode();out+=''.join(f'{x:010} 00000 n \n' for x in offsets).encode()
 return out+f'trailer\n<< /Size {len(objects)+1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n'.encode()
def form(body,resources='',isolated=False,knockout=True):
 return stream(f'/Type /XObject /Subtype /Form /BBox [0 0 96 96] /Group << /S /Transparency /I {str(isolated).lower()} /K {str(knockout).lower()} >> /Resources << {resources} >>',body)
def over(b,s,a,mode='Normal'):
 ar=a+b[3]*(1-a);r=[]
 for c in range(3):
  blend=b[c]*s[c] if mode=='Multiply' else b[c]+s[c]-b[c]*s[c] if mode=='Screen' else s[c]
  r.append(((1-a)*b[3]*b[c]+a*((1-b[3])*s[c]+b[3]*blend))/ar if ar else 0)
 return r+[ar]
def mix(b,s,f):
 a=b[3]*(1-f)+s[3]*f
 return [(b[c]*b[3]*(1-f)+s[c]*s[3]*f)/a if a else 0 for c in range(3)]+[a]
def region(color,rect=(30,30,36,36),tolerance=2):return dict(rect=list(rect),rgb=[round(c*255) for c in color[:3]],tolerance=tolerance)
def fixtures():
 bg='.2 .6 .8 rg 0 0 96 96 re f ';src='.8 .4 .2 rg 24 24 48 48 re f';prior='.1 .8 .3 rg 0 0 96 96 re f '
 for iso in [False,True]:
  for knock in [False,True]:
   name=f'single-{"isolated" if iso else "nonisolated"}-{"knockout" if knock else "normal"}'
   yield name,pdf(bg+'/F Do','/XObject << /F 5 0 R >>',[form('/A gs '+src,'/ExtGState << /A << /BM /Multiply >> >>',iso,knock)]),[region(S if iso else over(B,S,1,'Multiply')),region(B,(6,6,12,12))]
 for ais in [False,True]:
  body=prior+'/A gs '+src;resources=f'/ExtGState << /A << /ca .25 /BM /Multiply /AIS {str(ais).lower()} >> >>'
  expected=mix(T,over(B,S,1,'Multiply'),.25) if ais else over(B,S,.25,'Multiply')
  yield f'overlap-ais-{str(ais).lower()}',pdf(bg+'/F Do','/XObject << /F 5 0 R >>',[form(body,resources)]),[region(expected),region(T,(6,6,12,12))]
 child=form('/A gs '+src,'/ExtGState << /A << /ca .25 /BM /Multiply >> >>',False,False)
 yield 'nested-nonisolated',pdf(bg+'/F Do','/XObject << /F 5 0 R >>',[form(prior+'/C Do','/XObject << /C 6 0 R >>'),child]),[region(over(B,S,.25,'Multiply')),region(T,(6,6,12,12))]
 for ais in [False,True]:
  mask=form('.25 g 0 0 96 96 re f','',True,False)
  resources=f'/ExtGState << /A << /BM /Multiply /AIS {str(ais).lower()} /SMask << /S /Luminosity /G 6 0 R >> >> >>'
  expected=mix(T,over(B,S,1,'Multiply'),.25) if ais else over(B,S,.25,'Multiply')
  yield f'soft-mask-ais-{str(ais).lower()}',pdf(bg+'/F Do','/XObject << /F 5 0 R >>',[form(prior+'/A gs '+src,resources),mask]),[region(expected),region(T,(6,6,12,12))]
 pat=stream('/Type /Pattern /PatternType 1 /PaintType 1 /TilingType 1 /BBox [0 0 96 96] /XStep 96 /YStep 96 /Resources << /ExtGState << /A << /BM /Multiply /ca .25 >> >> >>','/A gs '+src)
 yield 'pattern-with-holes',pdf(bg+'/F Do','/XObject << /F 5 0 R >>',[form(prior+'/Pattern cs /P scn 0 0 96 96 re f','/Pattern << /P 6 0 R >>'),pat]),[region(over(B,S,.25,'Multiply')),region(T,(6,6,12,12))]
 image=stream('/Type /XObject /Subtype /Image /Width 1 /Height 1 /ColorSpace /DeviceRGB /BitsPerComponent 8 /SMask 7 0 R',bytes([204,102,51]).decode('latin1'))
 mask=stream('/Type /XObject /Subtype /Image /Width 1 /Height 1 /ColorSpace /DeviceGray /BitsPerComponent 8',chr(64))
 yield 'image-soft-mask',pdf(bg+'/F Do','/XObject << /F 5 0 R >>',[form(prior+'/A gs q 48 0 0 48 24 24 cm /Im Do Q','/XObject << /Im 6 0 R >> /ExtGState << /A << /BM /Multiply >> >>'),image,mask]),[region(over(B,S,64/255,'Multiply')),region(T,(6,6,12,12))]
 inner=form('/A gs '+src,'/ExtGState << /A << /ca .5 /BM /Multiply >> >>')
 outer=form('q /H gs '+bg+'Q /C Do','/ExtGState << /H << /ca .5 >> >> /XObject << /C 6 0 R >>',True,False)
 translucent=over(B[:3]+[.5],S,.5,'Multiply')
 yield 'translucent-initial-backdrop',pdf('/F Do','/XObject << /F 5 0 R >>',[outer,inner]),[region(over(W,translucent,translucent[3])),region(over(W,B,.5),(6,6,12,12))]
 yield 'zero-opacity-knocks-out',pdf(bg+'/F Do','/XObject << /F 5 0 R >>',[form(prior+'/A gs '+src,'/ExtGState << /A << /ca 0 /BM /Multiply >> >>')]),[region(B),region(T,(6,6,12,12))]
 glyph=stream('','1000 0 0 0 1000 1000 d1 0 0 1000 1000 re f')
 font='<< /Type /Font /Subtype /Type3 /FontBBox [0 0 1000 1000] /FontMatrix [.001 0 0 .001 0 0] /CharProcs << /A 7 0 R >> /Encoding << /Type /Encoding /Differences [65 /A] >> /FirstChar 65 /LastChar 65 /Widths [1000] /Resources << >> >>'
 yield 'original-type3-glyph',pdf(bg+'/F Do','/XObject << /F 5 0 R >>',[form(prior+'/A gs .8 .4 .2 rg BT /F1 48 Tf 24 24 Td (A) Tj ET','/Font << /F1 6 0 R >> /ExtGState << /A << /ca .5 /BM /Multiply >> >>'),font,glyph]),[region(over(B,S,.5,'Multiply')),region(T,(6,6,12,12))]
if __name__=='__main__':
 (ROOT/'pdf').mkdir(exist_ok=False);rows=[]
 for name,data,regions in fixtures():
  (ROOT/'pdf'/f'{name}.pdf').write_bytes(data)
  rows.append(dict(id=name,file=f'pdf/{name}.pdf',sha256=hashlib.sha256(data).hexdigest(),expectedRegions=regions))
 (ROOT/'expectations.json').write_text(json.dumps(dict(fixtures=rows),indent=2)+'\n')
