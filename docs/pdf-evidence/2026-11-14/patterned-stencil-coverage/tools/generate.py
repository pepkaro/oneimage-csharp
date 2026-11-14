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
# Group C: distinct 8x5 one-bit staircase stencil, colored tiled paint, under group and object opacity.
p=PDF();pat=p.stream('/Type /Pattern /PatternType 1 /PaintType 1 /TilingType 1 /BBox [0 0 5 7] /XStep 5 /YStep 7 /Resources << >>','0.65 0.12 0.75 rg 0 0 5 7 re f')
# A zero bit paints. These rows form independent authored stepped bands.
im=p.stream('/Type /XObject /Subtype /Image /Width 8 /Height 5 /ImageMask true /BitsPerComponent 1',bytes([0x7e,0x3c,0x18,0x81,0xc3]))
f=p.form('/H gs /Pattern cs /P scn q 72 0 0 90 12 20 cm /Im Do Q',f'/XObject << /Im {im} >> /Pattern << /P {pat} >> /ExtGState << /H << /ca 0.65 >> >>',bbox='4 4 92 124')
content=f'q /G gs /F Do Q q 1 0 0 1 96 0 cm /D gs /Pattern cs /P scn q 72 0 0 90 12 20 cm /Im Do Q Q'
p.save('patterned-stencil-coverage',content,f'/XObject << /F {f} /Im {im} >> /Pattern << /P {pat} >> /ExtGState << /G << /ca 0.6 >> /D << /ca 0.39 >> >>')
