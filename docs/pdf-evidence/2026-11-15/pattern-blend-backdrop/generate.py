#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Original PDF blend/backdrop reductions. Geometry, expected numbers and writer are original."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parent

def stream(entries,content):
 return f'<< {entries} /Length {len(content.encode())} >>\nstream\n{content}\nendstream'

def pdf(content,resources,extra):
 objs=['<< /Type /Catalog /Pages 2 0 R >>','<< /Type /Pages /Kids [3 0 R] /Count 1 >>',
       f'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 96 96] /Contents 4 0 R /Resources << {resources} >> >>',stream('',content),*extra]
 data=b'%PDF-1.7\n'; offsets=[]
 for i,obj in enumerate(objs,1):
  offsets.append(len(data));data+=f'{i} 0 obj\n{obj}\nendobj\n'.encode('ascii')
 xref=len(data);data+=f'xref\n0 {len(objs)+1}\n0000000000 65535 f \n'.encode()
 data+=''.join(f'{o:010} 00000 n \n' for o in offsets).encode()
 data+=f'trailer\n<< /Size {len(objs)+1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n'.encode()
 return data

def pattern(body,res,step=96):
 return stream(f'/Type /Pattern /PatternType 1 /PaintType 1 /TilingType 1 /BBox [0 0 {step} {step}] /XStep {step} /YStep {step} /Resources << {res} >>',body)
def form(body,res,isolated=False):
 return stream(f'/Type /XObject /Subtype /Form /BBox [0 0 96 96] /Group << /S /Transparency /I {str(isolated).lower()} >> /Resources << {res} >>',body)
def region(x,y,w,h,rgb):return dict(rect=[x,y,w,h],rgb=rgb,tolerance=1)
def fixtures():
 bg='.2 .6 .8 rg 0 0 96 96 re f '
 content='/A gs .8 .4 .2 rg 24 24 48 48 re f';res='/ExtGState << /A << /BM /Multiply >> >>'
 for kind in ['pattern','direct','nonisolated','isolated']:
  if kind=='pattern': extra=[pattern(content,res)];resources='/Pattern << /P 5 0 R >>';paint='/Pattern cs /P scn 24 24 48 48 re f'
  elif kind=='direct':extra=[];resources=res;paint=content
  else:extra=[form(content,res,kind=='isolated')];resources='/XObject << /F 5 0 R >>';paint='/F Do'
  color=[204,102,51] if kind=='isolated' else [41,61,41]
  yield 'single-'+kind,pdf(bg+paint,resources,extra),[region(30,30,36,36,color),region(4,4,12,12,[51,153,204])]
 for mode in ['Normal','Multiply','Screen']:
  body=f'/A gs .8 .4 .2 rg 0 0 24 24 re f';res=f'/ExtGState << /A << /BM /{mode} >> >>'
  extra=[pattern(body,res,24)];resources='/Pattern << /P 5 0 R >>'
  background=bg+'.6 .2 .4 rg 48 0 48 96 re f '
  expected=[]
  for x,cb in [(6,[.2,.6,.8]),(54,[.6,.2,.4])]:
   rgb=[]
   for b,s in zip(cb,[.8,.4,.2]):rgb.append(round(255*(s if mode=='Normal' else b*s if mode=='Multiply' else b+s-b*s)))
   expected.append(region(x,6,12,12,rgb))
  yield 'varied-'+mode.lower(),pdf(background+'/Pattern cs /P scn 0 0 96 96 re f',resources,extra),expected
 body='/A gs .8 .4 .2 rg 0 0 24 24 re f /B gs .1 .8 .3 rg 12 0 12 24 re f'
 res='/ExtGState << /A << /BM /Multiply /ca .5 >> /B << /BM /Screen /ca .5 >> >>'
 expected=[]
 for x,overlap in [(4,False),(16,True),(28,False),(40,True)]:
  rgb=[]
  for b,a,s in zip([.2,.6,.8],[.8,.4,.2],[.1,.8,.3]):
   r=.5*b+.5*b*a
   if overlap:r=.5*r+.5*(r+s-r*s)
   rgb.append(round(255*(.5*b+.5*r)))
  expected.append(region(x,6,4,12,rgb))
 for kind in ['pattern','nonisolated']:
  if kind=='pattern':extra=[pattern(body,res,24)];resources='/Pattern << /P 5 0 R >>';paint='/Pattern cs /P scn 0 0 96 96 re f'
  else:
   copies=' '.join(f'q 1 0 0 1 {24*x} {24*y} cm {body} Q' for y in range(4) for x in range(4))
   extra=[form(copies,res)];resources='/XObject << /F 5 0 R >>';paint='/F Do'
  yield 'multi-'+kind,pdf(bg+'/O gs '+paint,resources+' /ExtGState << /O << /ca .5 >> >>',extra),expected

if __name__=='__main__':
 out=ROOT/'pdf';out.mkdir(exist_ok=False);rows=[]
 for name,data,regions in fixtures():
  (out/(name+'.pdf')).write_bytes(data)
  rows.append(dict(id=name,file='pdf/'+name+'.pdf',sha256=hashlib.sha256(data).hexdigest(),expectedRegions=regions))
 (ROOT/'expectations.json').write_text(json.dumps(dict(fixtures=rows),indent=2)+'\n')
