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
# Transfer: two mask families with distinct, freshly chosen alpha/luma bands.
p=PDF(); resources=[];content=''
for index,(kind,x) in enumerate([('Alpha',10),('Luminosity',102)]):
 bands='';egs=[]
 for j,v in enumerate([0.15,0.35,0.7]):
  if kind=='Alpha':egs.append(f'/A{j} << /ca {v} >>'); bands+=f'/A{j} gs 1 g '
  else:bands+=f'{v} g '
  bands+=f'{x+7} {20+j*29} 66 23 re f\n'
 mask=p.stream(f'/Type /XObject /Subtype /Form /BBox [{x+3} 14 {x+77} 113] /Group << /S /Transparency /CS /DeviceGray /I true >> /Resources << /ExtGState << {" ".join(egs)} >> >>',bands)
 tr='<< /FunctionType 2 /Domain [0 1] /C0 [1] /C1 [0] /N 1 >>'
 resources.append(f'/M{index} << /SMask << /S /{kind} /G {mask} /BC [0.45] /TR {tr} >> >>')
 content+=f'q /M{index} gs '+rect(x,8,80,112,'0.1 0.3 0.75')+'Q\n'
p.save('soft-mask-transfer',content,'/ExtGState << '+' '.join(resources)+' >>')
