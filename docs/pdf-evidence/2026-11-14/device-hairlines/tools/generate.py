# SPDX-License-Identifier: MIT
# Copyright (c) 2026 OneImage contributors
# Original numerical test artwork. No external PDF, font, image or test stream is input.
from pathlib import Path
import json, hashlib, io
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'fixtures'; OUT.mkdir(exist_ok=True)
NOTICE=b'% Original OneImage numeric visual controls. Copyright (c) 2026 OneImage contributors. SPDX-License-Identifier: MIT\n'
class PDF:
 def __init__(self,w=192,h=128):self.objects=[None,None,None];self.w=w;self.h=h
 def obj(self,s):self.objects.append(s.encode('ascii') if isinstance(s,str) else s);return f'{len(self.objects)} 0 R'
 def stream(self,attrs,data):
  if isinstance(data,str):data=data.encode('ascii')
  return self.obj(f'<< {attrs} /Length {len(data)} >>\nstream\n'.encode()+data+b'\nendstream')
 def form(self,data,resources='',group='/I false',bbox='0 0 192 128'):
  return self.stream(f'/Type /XObject /Subtype /Form /BBox [{bbox}] /Group << /S /Transparency /CS /DeviceRGB {group} >> /Resources << {resources} >>',data)
 def save(self,name,data,resources=''):
  content=self.stream('',data)
  self.objects[0]=b'<< /Type /Catalog /Pages 2 0 R >>'
  self.objects[1]=b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>'
  self.objects[2]=f'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {self.w} {self.h}] /CropBox [0 0 {self.w} {self.h}] /Rotate 0 /Resources << {resources} >> /Contents {content} >>'.encode()
  b=bytearray(b'%PDF-1.7\n'+NOTICE); offsets=[0]
  for i,v in enumerate(self.objects,1):offsets.append(len(b));b.extend(f'{i} 0 obj\n'.encode()+v+b'\nendobj\n')
  xref=len(b);b.extend(f'xref\n0 {len(offsets)}\n0000000000 65535 f \n'.encode())
  for n in offsets[1:]:b.extend(f'{n:010} 00000 n \n'.encode())
  b.extend(f'trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n'.encode());(OUT/(name+'.pdf')).write_bytes(b)

def rect(x,y,w,h,c):return f'{c} rg {x} {y} {w} {h} re f\n'
# Device hairlines: same authored shape repeated using equivalent CTM parameterizations.
p=PDF();paths=[]
points=[(13.25,18.25),(13.25,48.25),(39.25,57.25),(49.25,30.25)]
for i,(a,b,c,d) in enumerate([(1,0,0,1),(6,0,0,0.2),(1,0,3,1)]):
 det=a*d-b*c
 pts=[((d*x-c*y)/det,(-b*x+a*y)/det) for x,y in points]
 s=f'q 1 0 0 1 {i*64} 54 cm {a} {b} {c} {d} 0 0 cm 0 w 1 J 1 j 0.05 0.2 0.45 RG '
 s+=' '.join(f'{x:.10g} {y:.10g} '+('m' if j==0 else 'l') for j,(x,y) in enumerate(pts))+' S Q\n';paths.append(s)
 # vertical/horizontal bars below, no zero-length subpaths in this control.
 s=f'q 1 0 0 1 {i*64} 0 cm {a} {b} {c} {d} 0 0 cm 0 w 0 J 0.05 0.2 0.45 RG '
 for xy in [[(13.25,20.25),(49.25,20.25)],[(31.25,9.25),(31.25,39.25)]]:
  for j,(x,y) in enumerate(xy):s+=f'{(d*x-c*y)/det:.10g} {(-b*x+a*y)/det:.10g} '+('m ' if j==0 else 'l S ')
 paths.append(s+'Q\n')
p.save('device-hairlines',''.join(paths))
