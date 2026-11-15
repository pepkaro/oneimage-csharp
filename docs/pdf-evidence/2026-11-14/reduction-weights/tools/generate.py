# SPDX-License-Identifier: MIT
# Copyright (c) 2026 OneImage contributors
# Original numerical test artwork. No external PDF, font, image or test stream is input.
from pathlib import Path
import json, hashlib
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'fixtures'; OUT.mkdir(exist_ok=True)
NOTICE=b'% Original OneImage numeric visual controls. Copyright (c) 2026 OneImage contributors. SPDX-License-Identifier: MIT\n'
class PDF:
 def __init__(self,w=192,h=128):self.objects=[None,None,None];self.w=w;self.h=h
 def obj(self,s):self.objects.append(s.encode('ascii') if isinstance(s,str) else s);return f'{len(self.objects)} 0 R'
 def stream(self,attrs,data):
  if isinstance(data,str):data=data.encode('ascii')
  return self.obj(f'<< {attrs} /Length {len(data)} >>\nstream\n'.encode()+data+b'\nendstream')
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

# Original large numeric raster: ramps, checkered tiles and three flat calibration squares.
import zlib
w,h=1009,751
samples=bytearray()
for y in range(h):
 for x in range(w):
  c=(24+(x*180)//(w-1)+20*((x+y)%2),34+(y*170)//(h-1),52+148*((x//37+y//41)%2))
  if x<96 and y<96:c=(25,83,141)
  elif x>=w-96 and y<96:c=(187,49,101)
  elif 440<=x<568 and y>=h-96:c=(43,179,89)
  samples.extend(c)
packed=zlib.compress(bytes(samples),9)
(OUT/'numeric-raster.rgb.zlib').write_bytes(packed)
p=PDF()
im=p.stream('/Type /XObject /Subtype /Image /Width 1009 /Height 751 /ColorSpace /DeviceRGB /BitsPerComponent 8 /Interpolate false /Filter /FlateDecode',packed)
p.save('reduction-weights','q 160 0 0 96 16 16 cm /Im Do Q',f'/XObject << /Im {im} >>')
(OUT/'source.json').write_text(json.dumps({'license':'MIT','width':w,'height':h,'targetWidth':320,'targetHeight':192,'components':3,'rawRgbSha256':hashlib.sha256(samples).hexdigest(),'compressedRgbSha256':hashlib.sha256(packed).hexdigest(),'sourcePixels':w*h,'weightsBeforePerResize':w*h,'weightsAfterPerResize':w,'logicalWeightBytes':w*16,'cacheBranch':'sh > 1 && sw <= 16384'},indent=2)+'\n')
