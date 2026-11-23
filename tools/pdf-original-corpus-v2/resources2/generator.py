#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Original PDF Corpus contributors
"""Original resource-name category isolation. Reads no external inputs."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parent
COLORS={'red':[255,0,0],'blue':[0,0,255],'green':[0,255,0],'black':[0,0,0]}
def stream(content,entries=''):
 data=content.encode('ascii');return f'<< {entries} /Length {len(data)} >>\nstream\n'.encode()+data+b'\nendstream'
def form(content,resources='',bbox='0 0 30 25'):
 return stream(content,f'/Type /XObject /Subtype /Form /FormType 1 /BBox [{bbox}] /Resources << {resources} >>')
def leaf(color):return form({'red':'1 0 0','blue':'0 0 1','green':'0 1 0'}[color]+' rg 0 0 30 25 re f')
def call(name,x,y):return f'q 1 0 0 1 {x} {y} cm /{name} Do Q'
def make(case):
 objects=[b'<< /Type /Catalog /Pages 2 0 R >>',b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>',b'',b'']
 if case==0:
  objects += [leaf('red')]
  resources='/XObject << /Shared 5 0 R >> /ColorSpace << /Shared /DeviceRGB >>'
  content='/Shared cs 0 0 1 scn 10 10 30 25 re f '+call('Shared',70,10)+' /Shared cs 0 1 0 scn 10 60 30 25 re f'
 elif case==1:
  objects += [leaf('red'),leaf('blue'),form('/Shared cs 0 0 1 scn 0 0 30 25 re f '+call('Shared',40,0)+' /Shared cs 0 1 0 scn 0 40 30 25 re f','/XObject << /Shared 5 0 R >> /ColorSpace << /Shared /DeviceRGB >>','0 0 80 75')]
  resources='/XObject << /Shared 6 0 R /Outer 7 0 R >> /ColorSpace << /Shared /DeviceGray >>'
  content=call('Outer',10,10)+' '+call('Shared',110,60)+' /Shared cs 0 scn 110 10 30 25 re f'
 else:
  objects += [leaf('blue'),leaf('red'),form('/Shared cs 0 1 0 scn 0 0 30 25 re f '+call('Shared',0,40),'/XObject << /Shared 5 0 R >> /ColorSpace << /Shared /DeviceRGB >>','0 0 40 75'),form('/Shared cs 0 scn 0 0 30 25 re f '+call('Shared',0,40),'/XObject << /Shared 6 0 R >> /ColorSpace << /Shared /DeviceGray >>','0 0 40 75')]
  resources='/XObject << /Left 7 0 R /Right 8 0 R >>'
  content=call('Left',10,10)+' '+call('Right',90,10)
 objects[2]=f'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 160 100] /Resources << {resources} >> /Contents 4 0 R >>'.encode();objects[3]=stream(content)
 out=bytearray(b'%PDF-1.7\n');offsets=[]
 for i,obj in enumerate(objects,1):offsets.append(len(out));out.extend(f'{i} 0 obj\n'.encode()+obj+b'\nendobj\n')
 xref=len(out);out.extend(f'xref\n0 {len(objects)+1}\n0000000000 65535 f \n'.encode())
 for offset in offsets:out.extend(f'{offset:010d} 00000 n \n'.encode())
 out.extend(f'trailer\n<< /Size {len(objects)+1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n'.encode());return bytes(out)
def main():
 (ROOT/'inputs').mkdir(exist_ok=True);cases=[]
 variants=[('resource-category-page','The page resolves /Shared independently in its ColorSpace and XObject categories',[(10,10,'blue'),(70,10,'red'),(10,60,'green')],[(120,20),(70,70),(50,50)]),('resource-category-page-form','A Form binds /Shared to DeviceRGB and its red leaf while the page binds it to DeviceGray and a blue leaf; postForm calls use page bindings',[(10,10,'blue'),(50,10,'red'),(10,50,'green'),(110,10,'black'),(110,60,'blue')],[(90,70)]),('resource-category-sibling-forms','Two sibling Forms each resolve /Shared in separate ColorSpace and XObject categories with RGB versus Gray and different leaf colors',[(10,10,'green'),(10,50,'blue'),(90,10,'black'),(90,50,'red')],[(65,25),(140,70)])]
 for index,(id,contract,rects,whites) in enumerate(variants):
  data=make(index);file='inputs/'+id+'.pdf';(ROOT/file).write_bytes(data)
  shape_rectangles=[[x,y,30,25,COLORS[color]] for x,y,color in rects]
  samples=[dict(id='binding-'+str(i),x=x+15,y=y+12,rgb=COLORS[color],tolerance=0) for i,(x,y,color) in enumerate(rects)]+[dict(id='paper-'+str(i),x=x,y=y,rgb=[255,255,255],tolerance=0) for i,(x,y) in enumerate(whites)]
  regions=[dict(id='binding-'+str(i),rect=[x+2,y+2,26,21],rgb=COLORS[color],tolerance=0) for i,(x,y,color) in enumerate(rects)]+[dict(id='paper-'+str(i),rect=[x-2,y-2,4,4],rgb=[255,255,255],tolerance=0) for i,(x,y) in enumerate(whites)]
  cases.append(dict(id=id,file=file,sha256=hashlib.sha256(data).hexdigest(),license='MIT',fixture_version='1.7',contract=contract,spec='ISO 32000-1:2008',spec_clauses=['7.8.3/Table33 Resource Dictionaries','8.6.8/Table74 Colour Operators','8.10.2/Table95 Resources'],primary_iso_2020='7.8.3/Table34 Resource dictionaries',secondary_iso_2020=['8.10.2/Table93 Resources','8.6.8 Colour operators: heading verified, exact cs/scn rows pending'],citation_status='2020 resource-association, Table34 ColorSpace mapping and Form-independence text verified in official public errata; unreproduced operator/category rows pending full text',route='page/Form /Shared cs ... scn and /Shared Do resolved through explicit ColorSpace and XObject category subdictionaries',width=160,height=100,display_width_points=160,display_height_points=100,user_unit=1,rotation=0,page=0,pages=[0],page_count=1,dpis=[72,144],background=[255,255,255],annotations='none',shape_rectangles=shape_rectangles,samples=samples,expected_samples=[dict(id=s['id'],point=[s['x'],s['y']],rgb=s['rgb'],tolerance=0) for s in samples],expected_regions=regions,sample_coordinates='PDF page points x right/y up; image row=floor((100-y)*dpi/72)',mask='All pixels except predeclared one-device-pixel bands around shape rectangle boundaries; expected_regions are separate inset exact controls',upstream_association=dict(upstream_id=None,scope='standard-contract-only',exact_upstream_scope_established=False,upstream_input_executed=False)))
 (ROOT/'manifest.json').write_text(json.dumps(dict(schema_version=1,batch='ISO-PAGE-RESOURCE-02',owner='mozilla_originals',purpose='Independent lexical resource names across categories and page/Form resource dictionaries',fixture_count=3,case_count=3,independently_authored=True,upstream_fixture_bytes_read=0,cases=cases),indent=2)+'\n');print(json.dumps(dict(unique_pdfs=3,bytes=sum((ROOT/c['file']).stat().st_size for c in cases))))
if __name__=='__main__':main()
