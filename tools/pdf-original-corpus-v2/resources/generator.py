#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Original PDF Corpus contributors
"""Original page/Form resource-name isolation. Reads no external inputs."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parent
COLORS={'red':[255,0,0],'blue':[0,0,255],'green':[0,255,0]}
def stream(content,entries=''):
 data=content.encode('ascii');return f'<< {entries} /Length {len(data)} >>\nstream\n'.encode()+data+b'\nendstream'
def form(content,resources='',bbox='0 0 30 25'):
 return stream(content,f'/Type /XObject /Subtype /Form /FormType 1 /BBox [{bbox}] /Resources << {resources} >>')
def leaf(color):return form({'red':'1 0 0','blue':'0 0 1','green':'0 1 0'}[color]+' rg 0 0 30 25 re f')
def call(name,x,y):return f'q 1 0 0 1 {x} {y} cm /{name} Do Q'
def make(case):
 objects=[b'<< /Type /Catalog /Pages 2 0 R >>',b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>',b'',b'']
 if case==0:
  objects += [leaf('red'),leaf('blue'),form('/Mark Do','/XObject << /Mark 6 0 R >>','0 0 40 35')]
  resources='/XObject << /Mark 5 0 R /Outer 7 0 R >>';content=' '.join([call('Mark',10,10),call('Outer',70,10),call('Mark',10,60)])
 elif case==1:
  objects += [leaf('red'),leaf('green'),leaf('blue'),form('/Mark Do','/XObject << /Mark 5 0 R >>'),form('/Mark Do','/XObject << /Mark 6 0 R >>')]
  resources='/XObject << /Left 8 0 R /Right 9 0 R /Mark 7 0 R >>';content=' '.join([call('Left',10,10),call('Right',70,10),call('Left',10,60),call('Mark',70,60)])
 else:
  objects += [leaf('red'),leaf('blue'),leaf('green'),form('/Mark Do','/XObject << /Mark 7 0 R >>','0 0 35 30'),form('/Mark Do '+call('Inner',40,0)+' '+call('Mark',0,40),'/XObject << /Mark 6 0 R /Inner 8 0 R >>','0 0 90 80')]
  resources='/XObject << /Mark 5 0 R /Outer 9 0 R >>';content=' '.join([call('Outer',10,10),call('Mark',110,10)])
 objects[2]=f'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 160 100] /Resources << {resources} >> /Contents 4 0 R >>'.encode();objects[3]=stream(content)
 out=bytearray(b'%PDF-1.7\n');offsets=[]
 for i,obj in enumerate(objects,1):offsets.append(len(out));out.extend(f'{i} 0 obj\n'.encode()+obj+b'\nendobj\n')
 xref=len(out);out.extend(f'xref\n0 {len(objects)+1}\n0000000000 65535 f \n'.encode())
 for offset in offsets:out.extend(f'{offset:010d} 00000 n \n'.encode())
 out.extend(f'trailer\n<< /Size {len(objects)+1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n'.encode());return bytes(out)
def main():
 (ROOT/'inputs').mkdir(exist_ok=True);cases=[]
 variants=[('resource-page-form-isolation','Page and Form bind /Mark independently; page binding survives the Form call',[(10,10,'red'),(70,10,'blue'),(10,60,'red')],[(120,20),(70,70),(50,50)]),('resource-sibling-form-isolation','Sibling Forms reuse /Mark for different leaf Forms without cross-contamination; page binding remains independent',[(10,10,'red'),(70,10,'green'),(10,60,'red'),(70,60,'blue')],[(120,20),(50,50)]),('resource-nested-form-restoration','Nested Form resolves its own /Mark, then restores outer and page name bindings',[(10,10,'blue'),(50,10,'green'),(10,50,'blue'),(110,10,'red')],[(95,25),(70,70)])]
 for index,(id,contract,rects,whites) in enumerate(variants):
  data=make(index);file='inputs/'+id+'.pdf';(ROOT/file).write_bytes(data)
  shape_rectangles=[[x,y,30,25,COLORS[color]] for x,y,color in rects]
  samples=[dict(id='binding-'+str(i),x=x+15,y=y+12,rgb=COLORS[color],tolerance=0) for i,(x,y,color) in enumerate(rects)]+[dict(id='paper-'+str(i),x=x,y=y,rgb=[255,255,255],tolerance=0) for i,(x,y) in enumerate(whites)]
  regions=[dict(id='binding-'+str(i),rect=[x+2,y+2,26,21],rgb=COLORS[color],tolerance=0) for i,(x,y,color) in enumerate(rects)]+[dict(id='paper-'+str(i),rect=[x-2,y-2,4,4],rgb=[255,255,255],tolerance=0) for i,(x,y) in enumerate(whites)]
  cases.append(dict(id=id,file=file,sha256=hashlib.sha256(data).hexdigest(),license='MIT',fixture_version='1.7',contract=contract,spec='ISO 32000-1:2008',spec_clauses=['7.8.3 Resource Dictionaries','8.10.2/Table95 Resources'],primary_iso_2020='7.8.3 Resource dictionaries',secondary_iso_2020='8.10.2/Table93 Resources',citation_status='Relevant2020 amended resource-association and Form-independence text verified in official public errata; complete standard not inspected',route='page content /Do invoking independent Form XObjects with explicit local /Resources /XObject dictionaries',width=160,height=100,display_width_points=160,display_height_points=100,user_unit=1,rotation=0,page=0,pages=[0],page_count=1,dpis=[72,144],background=[255,255,255],annotations='none',shape_rectangles=shape_rectangles,samples=samples,expected_samples=[dict(id=s['id'],point=[s['x'],s['y']],rgb=s['rgb'],tolerance=0) for s in samples],expected_regions=regions,sample_coordinates='PDF page points x right/y up; image row=floor((100-y)*dpi/72)',mask='All pixels except predeclared one-device-pixel bands around shape rectangle boundaries; expected_regions are separate inset exact controls',upstream_association=dict(upstream_id=None,scope='standard-contract-only',exact_upstream_scope_established=False,upstream_input_executed=False)))
 (ROOT/'manifest.json').write_text(json.dumps(dict(schema_version=1,batch='ISO-PAGE-RESOURCE-01',owner='mozilla_originals',purpose='Independent local resource-name bindings in page, sibling and nested Form content streams',fixture_count=3,case_count=3,independently_authored=True,upstream_fixture_bytes_read=0,cases=cases),indent=2)+'\n');print(json.dumps(dict(unique_pdfs=3,bytes=sum((ROOT/c['file']).stat().st_size for c in cases))))
if __name__=='__main__':main()
