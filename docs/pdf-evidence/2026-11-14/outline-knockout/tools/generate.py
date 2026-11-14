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
# Original outline font, polygon constructed here; no vendor font or upstream test font.
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.t2CharStringPen import T2CharStringPen
fb=FontBuilder(1000,isTTF=False);fb.setupGlyphOrder(['.notdef','wedge']);fb.setupCharacterMap({65:'wedge'})
cs={}
for name in ['.notdef','wedge']:
 pen=T2CharStringPen(900,None)
 if name=='wedge':
  pen.moveTo((80,100));pen.lineTo((690,100));pen.lineTo((770,340));pen.lineTo((470,760));pen.lineTo((150,620));pen.closePath()
 cs[name]=pen.getCharString()
fb.setupCFF('NovelWedgeMIT',{'FullName':'Novel Wedge MIT','FamilyName':'Novel Wedge MIT','Weight':'Regular','Notice':'Copyright 2026 OneImage contributors. MIT license.'},cs,{})
fb.setupHorizontalMetrics({'.notdef':(900,0),'wedge':(900,80)});fb.setupHorizontalHeader(ascent=800,descent=-200);fb.setupNameTable({'familyName':'Novel Wedge MIT','styleName':'Regular','uniqueFontIdentifier':'NovelWedgeMIT20261114','fullName':'Novel Wedge MIT','psName':'NovelWedgeMIT'});fb.setupOS2(sTypoAscender=800,sTypoDescender=-200,usWinAscent=800,usWinDescent=200);fb.setupPost()
cff=fb.font['CFF '].compile(fb.font);(OUT/'novel-wedge.cff').write_bytes(cff)
p=PDF();fontfile=p.stream('/Subtype /Type1C',cff);desc=p.obj(f'<< /Type /FontDescriptor /FontName /NovelWedgeMIT /Flags 4 /FontBBox [80 100 770 760] /ItalicAngle 0 /Ascent 800 /Descent -200 /CapHeight 760 /StemV 70 /FontFile3 {fontfile} >>');font=p.obj(f'<< /Type /Font /Subtype /Type1 /BaseFont /NovelWedgeMIT /FirstChar 65 /LastChar 65 /Widths [900] /Encoding << /Type /Encoding /Differences [65 /wedge] >> /FontDescriptor {desc} >>')
content=''
for i,mode in enumerate([2,6]):
 content+=f'q /A gs 0.9 0.3 0.12 rg 0.1 0.3 0.8 RG 9 w 1 j BT /F 92 Tf {mode} Tr 1 0 0 1 {2+i*96} 24 Tm (A) Tj ET Q\n'
p.save('outline-knockout',content,f'/Font << /F {font} >> /ExtGState << /A << /ca 0.8 /CA 0.45 >> >>')
